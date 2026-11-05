#!/usr/bin/env python3
"""
Joint Academy lead filter: turn messy campaign exports into clean,
campaign-ready lead lists of physical therapists (never physicians).

What it does, in order:
  1. Reads one or more CSV exports (Smartlead campaign exports, Apollo exports,
     anything with an email column). Column names are matched loosely.
  2. Groups rows by email across ALL files, so a person who replied or bounced
     in any campaign is excluded everywhere.
  3. Drops anyone who replied, bounced, unsubscribed, is Do Not Contact, or is
     on an exclude list (customers, other clients' leads, ...).
  4. Classifies the role from the job title (and company name for neutral
     titles like "Owner"): physical therapist -> keep, physician -> exclude,
     unclear -> review file for a human.
  5. Splits the keepers into "re-engage" (contacted before, no reply) and
     "never contacted" (fresh).
  6. Optional --mx: looks up each recipient domain's mail host and splits each
     list into Microsoft-hosted vs Google/other, matching the MS and Google
     sender campaigns.

Standard library only. Examples:

    # Non-repliers from old campaigns
    python lead_filter.py exports/*.csv --out out/reengage --mx

    # Fresh leads, checked against everything already contacted
    python lead_filter.py fresh/apollo.csv --history exports/*.csv \
        --exclude customers.csv --out out/fresh --mx
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, OrderedDict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------
# Column matching
# --------------------------------------------------------------------------

# Normalized field -> accepted header spellings (compared after normalizing:
# lowercase, spaces/dashes -> underscores).
COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "email": ("email", "email_address", "work_email", "lead_email", "e_mail"),
    "first_name": ("first_name", "firstname", "first", "fornamn", "förnamn"),
    "last_name": ("last_name", "lastname", "last", "surname", "efternamn"),
    "title": ("title", "job_title", "designation", "position", "role", "titel"),
    "company_name": ("company_name", "company", "organization", "organisation",
                     "account_name", "foretag", "företag"),
    "website": ("website", "company_url", "company_website", "domain"),
    "linkedin": ("linkedin_profile", "linkedin", "linkedin_url",
                 "person_linkedin_url"),
    "phone": ("phone_number", "phone", "work_direct_phone", "mobile_phone"),
    "location": ("location", "city", "state", "country"),
    "status": ("status", "lead_status", "campaign_lead_status"),
    "category": ("category", "lead_category"),
    "reply_count": ("reply_count", "replies", "replied_count"),
    "is_unsubscribed": ("is_unsubscribed", "unsubscribed"),
    "is_bounced": ("is_bounced", "bounced"),
    "email_status": ("email_status", "verification_status", "email_verification"),
    "last_step_sent": ("last_email_sequence_sent", "sequence_number",
                       "emails_sent", "sent_count"),
    "open_count": ("open_count", "opens"),
    "custom_fields": ("custom_fields",),
}

OUTPUT_FIELDS = [
    "email", "first_name", "last_name", "title", "company_name", "website",
    "linkedin", "phone", "location", "mail_host", "role_bucket", "role_reason",
    "previously_contacted", "prior_status", "source_files",
]


def _norm_header(h: str) -> str:
    return re.sub(r"[\s\-]+", "_", (h or "").strip().lower())


def map_columns(headers: list[str]) -> dict[str, str]:
    """Return {normalized_field: original_header} for the headers we know."""
    by_norm = {_norm_header(h): h for h in headers}
    mapping: dict[str, str] = {}
    for fld, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in by_norm:
                mapping[fld] = by_norm[alias]
                break
    return mapping


# --------------------------------------------------------------------------
# Role classification: physical therapist vs physician
# --------------------------------------------------------------------------

# Words, matched case-insensitively.
PT_WORDS = re.compile(
    r"physical\s*therap|physiotherap|physio\b|fysioterap|sjukgymnast|"
    r"doctor\s+of\s+physical\s+therapy",
    re.I,
)
# Credentials, matched case-sensitively so "pt" / "do" inside words don't count.
PT_CREDENTIALS = re.compile(
    r"(?<![A-Za-z])(D\.?P\.?T|M\.?P\.?T|P\.?T\.?A|P\.T\.?|PT)(?![A-Za-z])")

# PT-related but not a therapist or decision maker: a human should look.
SUPPORT_ROLE = re.compile(
    r"receptionist|front\s+desk|billing|biller|scheduler|coordinator|\baide\b|"
    r"technician|\btech\b|marketing|recruit|student|intern\b|assistant\s+to",
    re.I,
)

PHYSICIAN_WORDS = re.compile(
    r"physician|surgeon|physiatr|physical\s+medicine|pm\s*&\s*r|"
    r"doctor\s+of\s+(medicine|osteopath)|osteopathic|orthopa?edist|"
    r"anesthesiolog|radiolog|rheumatolog|neurolog|general\s+practitioner|"
    r"l[äa]kare|ortoped\b|allm[äa]nl[äa]kare|"
    r"\bmedical\s+doctor\b",
    re.I,
)
PHYSICIAN_CREDENTIALS = re.compile(r"(?<![A-Za-z])(M\.D\.?|MD|D\.O\.|DO|MBBS|PA-C)(?![A-Za-z])")

# Other professions that are not physical therapists.
OTHER_PROFESSION = re.compile(
    r"chiropract|kiropraktor|naprapat|occupational\s+therap|arbetsterapeut|"
    r"speech|logoped|\bnurse\b|sjuksk[öo]terska|dentist|tandl[äa]kare|"
    r"veterinar|massage|psycholog|dietitian|pharmac|apotek",
    re.I,
)

# Titles that say "decision maker" but not which profession.
NEUTRAL_LEADER = re.compile(
    r"owner|founder|co-?founder|ceo|president|partner|principal|director|"
    r"manager|head\s+of|clinic\s+lead|verksamhetschef|klinikchef|\bvd\b|"
    r"[äa]gare|grundare|chef",
    re.I,
)

# Company names that indicate a physical therapy practice.
PT_COMPANY = re.compile(
    r"physical\s*therap|physiotherap|physio|(?<![A-Za-z])PT(?![A-Za-z])|"
    r"fysio|sjukgymnast",
    re.I,
)
PHYSICIAN_COMPANY = re.compile(
    r"orthopa?edic\s+(surgery|surgeons|associates|group)|surgical|"
    r"medical\s+group|\bmd\b|hospital|v[åa]rdcentral",
    re.I,
)


def classify_role(title: str, company: str = "") -> tuple[str, str]:
    """Return (bucket, reason). bucket is one of: pt, physician, other, review."""
    t = (title or "").strip()
    c = (company or "").strip()

    pt = bool(PT_WORDS.search(t) or PT_CREDENTIALS.search(t))
    doc_word = PHYSICIAN_WORDS.search(t)
    doc_cred = PHYSICIAN_CREDENTIALS.search(t)
    # "Physician assistant" is not a physician, but it is not a PT either.
    if re.search(r"physician\s+assistant|\bPA-C\b", t, re.I):
        return "other", "physician assistant"
    other = OTHER_PROFESSION.search(t)

    if pt and (doc_word or doc_cred):
        return "review", "title mentions both PT and physician"
    if doc_word or doc_cred:
        hit = (doc_word or doc_cred).group(0)
        return "physician", f"physician title ({hit})"
    if pt and SUPPORT_ROLE.search(t):
        return "review", f"PT-related support role ({SUPPORT_ROLE.search(t).group(0)})"
    if pt:
        return "pt", "physical therapist title"
    if other:
        return "other", f"other profession ({other.group(0)})"
    if not t:
        if c and PT_COMPANY.search(c) and not PHYSICIAN_COMPANY.search(c):
            return "review", "no title, PT company"
        return "review", "no title"
    if NEUTRAL_LEADER.search(t):
        if c and PT_COMPANY.search(c) and not PHYSICIAN_COMPANY.search(c):
            return "pt", "leader at a PT practice"
        return "review", "leader title, company not clearly PT"
    return "review", "title not recognised"


# --------------------------------------------------------------------------
# Lead status: replied / bounced / unsubscribed / contacted
# --------------------------------------------------------------------------

TRUE_WORDS = {"true", "yes", "1", "y", "t"}

# Lead categories that mean a human replied, or must not be contacted.
STOP_CATEGORIES = (
    "interested", "not interested", "do not contact", "wrong person",
    "meeting", "information request", "closed", "unsubscribe", "bounce",
)
NOT_A_REAL_REPLY = ("out of office", "ooo", "auto reply", "auto-reply")

NOT_CONTACTED_STATUSES = ("not_started", "notstarted", "not started", "drafted",
                          "queued", "")


def _truthy(v: str) -> bool:
    return (v or "").strip().lower() in TRUE_WORDS


def _int(v: str) -> int:
    try:
        return int(float((v or "0").strip() or 0))
    except ValueError:
        return 0


EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+'\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


@dataclass
class Lead:
    email: str
    rows: list[dict] = field(default_factory=list)   # normalized rows
    sources: list[str] = field(default_factory=list)
    candidate: bool = False  # appeared in a candidate (non-history) file

    def first(self, fld: str) -> str:
        for r in self.rows:
            v = (r.get(fld) or "").strip()
            if v:
                return v
        return ""


def stop_reason(lead: Lead) -> str | None:
    """Why this person must not be emailed again, or None."""
    for r in lead.rows:
        status = (r.get("status") or "").strip().lower()
        category = (r.get("category") or "").strip().lower()
        email_status = (r.get("email_status") or "").strip().lower()
        if _truthy(r.get("is_unsubscribed", "")) or "unsub" in status:
            return "unsubscribed"
        if _truthy(r.get("is_bounced", "")) or "bounce" in status or "blocked" in status:
            return "bounced"
        if email_status in ("invalid", "bounced", "undeliverable", "do_not_mail"):
            return f"email verification: {email_status}"
        if category and not any(w in category for w in NOT_A_REAL_REPLY):
            if any(w in category for w in STOP_CATEGORIES):
                return f"category: {category}"
        if _int(r.get("reply_count", "")) > 0 or "replied" in status:
            if not any(w in category for w in NOT_A_REAL_REPLY):
                return "replied"
    return None


def was_contacted(lead: Lead) -> bool:
    """True if any campaign export shows an email was already sent to them.

    A sent-step count, when the export has one, decides. Otherwise any lead
    status other than a clear "not started" counts as contacted: it is safer to
    wait 30 days than to email someone twice in a week.
    """
    for r in lead.rows:
        if _int(r.get("open_count", "")) > 0:
            return True
        steps = (r.get("last_step_sent") or "").strip()
        if steps:
            if _int(steps) > 0:
                return True
            continue
        if "status" in r:
            status = (r.get("status") or "").strip().lower()
            if status not in NOT_CONTACTED_STATUSES:
                return True
    return False


# --------------------------------------------------------------------------
# Mail host (MX) lookup via DNS-over-HTTPS
# --------------------------------------------------------------------------

DOH_ENDPOINTS = (
    "https://dns.google/resolve?name={name}&type=MX",
    "https://cloudflare-dns.com/dns-query?name={name}&type=MX",
)


def mx_hosts(domain: str, timeout: float = 8.0) -> list[str] | None:
    """MX hostnames for a domain, [] if it has none, None if lookup failed."""
    for template in DOH_ENDPOINTS:
        url = template.format(name=urllib.parse.quote(domain))
        req = urllib.request.Request(url, headers={"Accept": "application/dns-json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
        except Exception:
            continue
        records = []
        for a in data.get("Answer") or []:
            if a.get("type") == 15:  # MX: "<preference> <host>."
                parts = str(a.get("data", "")).split()
                if len(parts) == 2 and parts[0].isdigit():
                    records.append((int(parts[0]), parts[1].rstrip(".").lower()))
        return [host for _, host in sorted(records)]
    return None


def classify_mail_host(hosts: list[str] | None) -> str:
    """Classify by the preferred (lowest number) MX host."""
    if hosts is None:
        return "unknown"
    if not hosts:
        return "no-mx"
    best = hosts[0]
    if best.endswith(("google.com", "googlemail.com")):
        return "google"
    if best.endswith(("outlook.com", "hotmail.com")):
        return "microsoft"
    return "other"


def lookup_domains(domains: set[str], cache_path: Path | None, workers: int = 16) -> dict[str, str]:
    cache: dict[str, str] = {}
    if cache_path and cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text())
        except json.JSONDecodeError:
            cache = {}
    todo = sorted(d for d in domains if d not in cache or cache[d] == "unknown")
    if todo:
        print(f"Looking up mail hosts for {len(todo)} domains...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for domain, hosts in zip(todo, pool.map(mx_hosts, todo)):
                cache[domain] = classify_mail_host(hosts)
        if cache_path:
            cache_path.write_text(json.dumps(cache, indent=1, sort_keys=True))
    return {d: cache.get(d, "unknown") for d in domains}


# --------------------------------------------------------------------------
# Reading inputs
# --------------------------------------------------------------------------

def _expand_custom_fields(row: dict) -> None:
    """Smartlead exports can hold extra fields as JSON in `custom_fields`."""
    raw = row.get("custom_fields") or ""
    if not raw.strip().startswith("{"):
        return
    try:
        extra = json.loads(raw)
    except json.JSONDecodeError:
        return
    mapping = map_columns(list(extra.keys()))
    for fld, key in mapping.items():
        if not row.get(fld) and extra.get(key) not in (None, ""):
            row[fld] = str(extra[key])


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(f, dialect=dialect)
        mapping = map_columns(reader.fieldnames or [])
        if "email" not in mapping:
            raise SystemExit(f"{path}: no email column found (headers: {reader.fieldnames})")
        rows = []
        for raw in reader:
            row = {fld: (raw.get(src) or "") for fld, src in mapping.items()}
            _expand_custom_fields(row)
            rows.append(row)
        return rows


def read_exclude(paths: list[Path]) -> tuple[set[str], set[str]]:
    """Emails and domains to never contact.

    Accepts a CSV with an email and/or domain/website column, or a plain text
    file with one email or domain per line.
    """
    emails, domains = set(), set()

    def add(token: str) -> None:
        token = token.strip().strip('"').lower()
        token = re.sub(r"^https?://", "", token).removeprefix("www.").split("/")[0]
        if "@" in token:
            emails.add(token)
        elif "." in token and " " not in token:
            domains.add(token)

    for p in paths:
        with p.open(newline="", encoding="utf-8-sig") as f:
            first = f.readline()
            f.seek(0)
            headers = [_norm_header(h) for h in next(csv.reader([first]), [])]
            known = {"email", "email_address", "domain", "website", "company_url"}
            if known & set(headers):
                for row in csv.DictReader(f):
                    for h, v in row.items():
                        if _norm_header(h or "") in known and v:
                            add(v)
            else:
                for line in f:
                    if line.strip():
                        add(line)
    return emails, domains


def load_leads(candidates: list[Path], history: list[Path]) -> "OrderedDict[str, Lead]":
    leads: "OrderedDict[str, Lead]" = OrderedDict()
    for paths, is_candidate in ((candidates, True), (history, False)):
        for p in paths:
            for row in read_csv(p):
                email = (row.get("email") or "").strip().lower()
                if not email:
                    continue
                lead = leads.setdefault(email, Lead(email=email))
                lead.rows.append(row)
                if p.name not in lead.sources:
                    lead.sources.append(p.name)
                lead.candidate = lead.candidate or is_candidate
    return leads


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def process(candidates: list[Path], history: list[Path], exclude: list[Path],
            out_dir: Path, use_mx: bool, mx_cache: Path | None) -> Counter:
    leads = load_leads(candidates, history)
    ex_emails, ex_domains = read_exclude(exclude)

    buckets: dict[str, list[dict]] = {"reengage": [], "never_contacted": [],
                                      "review": [], "excluded": []}
    stats: Counter = Counter()

    for lead in leads.values():
        if not lead.candidate:
            continue  # history-only rows inform exclusions, never get output
        domain = lead.email.rsplit("@", 1)[-1]
        out = {
            "email": lead.email,
            "first_name": lead.first("first_name"),
            "last_name": lead.first("last_name"),
            "title": lead.first("title"),
            "company_name": lead.first("company_name"),
            "website": lead.first("website"),
            "linkedin": lead.first("linkedin"),
            "phone": lead.first("phone"),
            "location": lead.first("location"),
            "mail_host": "",
            "prior_status": "; ".join(sorted({(r.get("status") or "").strip()
                                              for r in lead.rows} - {""})),
            "source_files": "; ".join(lead.sources),
        }
        reason = None
        if not EMAIL_RE.match(lead.email):
            reason = "invalid email"
        elif lead.email in ex_emails or domain in ex_domains:
            reason = "on exclude list"
        else:
            reason = stop_reason(lead)

        bucket, why = classify_role(out["title"], out["company_name"])
        out["role_bucket"], out["role_reason"] = bucket, why
        contacted = was_contacted(lead)
        out["previously_contacted"] = "yes" if contacted else "no"

        if reason:
            out["role_reason"] = f"{reason} | role: {why}"
            buckets["excluded"].append(out)
            stats[f"excluded: {reason.split(':')[0]}"] += 1
        elif bucket in ("physician", "other"):
            buckets["excluded"].append(out)
            stats[f"excluded: {bucket}"] += 1
        elif bucket == "review":
            buckets["review"].append(out)
            stats["review"] += 1
        else:
            key = "reengage" if contacted else "never_contacted"
            buckets[key].append(out)
            stats[key] += 1

    if use_mx:
        keep = buckets["reengage"] + buckets["never_contacted"] + buckets["review"]
        domains = {r["email"].rsplit("@", 1)[-1] for r in keep}
        hosts = lookup_domains(domains, mx_cache)
        for r in keep:
            r["mail_host"] = hosts.get(r["email"].rsplit("@", 1)[-1], "unknown")
            stats[f"mail host: {r['mail_host']}"] += 1

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in buckets.items():
        write_csv(out_dir / f"{name}.csv", rows)
        if use_mx and name in ("reengage", "never_contacted"):
            ms = [r for r in rows if r["mail_host"] == "microsoft"]
            google = [r for r in rows if r["mail_host"] != "microsoft"]
            write_csv(out_dir / f"{name}_microsoft.csv", ms)
            write_csv(out_dir / f"{name}_google_and_other.csv", google)

    summary = "\n".join(f"{k:40s} {v:>7d}" for k, v in sorted(stats.items()))
    (out_dir / "summary.txt").write_text(summary + "\n")
    return stats


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", type=Path,
                    help="CSV files whose leads you want to (re)contact")
    ap.add_argument("--history", nargs="*", type=Path, default=[],
                    help="older campaign exports: used only to exclude people "
                         "who replied/bounced/unsubscribed and to mark who was contacted")
    ap.add_argument("--exclude", nargs="*", type=Path, default=[],
                    help="files with emails or domains never to contact")
    ap.add_argument("--out", type=Path, default=Path("out"), help="output folder")
    ap.add_argument("--mx", action="store_true",
                    help="look up mail hosts and split lists into Microsoft vs Google/other")
    ap.add_argument("--mx-cache", type=Path, default=Path(".mx_cache.json"),
                    help="where to cache mail host lookups between runs")
    args = ap.parse_args(argv)

    stats = process(args.inputs, args.history, args.exclude, args.out,
                    args.mx, args.mx_cache)
    print((args.out / "summary.txt").read_text(), end="")
    print(f"\nWrote lists to {args.out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
