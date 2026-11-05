#!/usr/bin/env python3
"""
Read-only Smartlead audit for Joint Academy.

Every call is a GET. Nothing in Smartlead is changed, paused or deleted.

Commands:
  accounts      every inbox with provider, warmup reputation, connection
                state, the JA campaigns it sits in, and a verdict:
                READY / REST / FIX / RETIRE                -> accounts.csv
  campaigns     every JA campaign with sent, replies, bounce rate, leads left
                and flags (bounce too high, unfinished, non-Ready inboxes)
                                                           -> campaigns.csv
  export-leads  each JA campaign's leads as CSV, with an is_bounced column
                added (Smartlead's own export has none)     -> exports/*.csv
  all           accounts + campaigns

Set your API key in the environment (Smartlead > Settings > API key):

    export SMARTLEAD_API_KEY=...            # macOS / Linux
    setx SMARTLEAD_API_KEY ...              # Windows (new terminal after)

Examples:

    python smartlead_audit.py all
    python smartlead_audit.py all --client-id 1234
    python smartlead_audit.py export-leads --out exports
    python smartlead_audit.py campaigns --match "joint|^JA\\b|leif"

Which campaigns count as Joint Academy: those whose name matches --match
(a regex, case-insensitive), or that belong to --client-id when given.
Inboxes are included when they sit in a JA campaign, belong to --client-id,
carry a tag matching --account-tag, or use a domain in --domain.
Use --all-accounts to list every inbox in the workspace.

Standard library only. Runs on your own machine: the API key goes in the URL
(Smartlead supports no header auth), so it is redacted from every message.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

BASE = "https://server.smartlead.ai/api/v1"
DEFAULT_MATCH = r"joint\s*-?\s*academy|^JA\b"
DEFAULT_ACCOUNT_TAG = r"^JA"

# Verdict thresholds (see the plan's inbox lifecycle).
READY_REPUTATION = 97.0
RETIRE_REPUTATION = 85.0
MIN_WARMUP_DAYS = 14


# --------------------------------------------------------------------------
# HTTP client
# --------------------------------------------------------------------------

class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never follow redirects: the API key is in the URL."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "redirect refused", headers, fp)


class Smartlead:
    def __init__(self, api_key: str, min_interval: float = 0.25, max_retries: int = 5):
        self.api_key = api_key
        self.min_interval = min_interval  # 0.25 s = at most 8 requests per 2 s
        self.max_retries = max_retries
        self._last = 0.0
        self._opener = urllib.request.build_opener(NoRedirect)

    def _redact(self, text: str) -> str:
        return text.replace(self.api_key, "***") if self.api_key else text

    def get(self, path: str, raw: bool = False, **params):
        params = {k: v for k, v in params.items() if v is not None}
        query = urllib.parse.urlencode({**params, "api_key": self.api_key})
        url = f"{BASE}{path}?{query}"
        delay = 2.0
        for attempt in range(self.max_retries + 1):
            wait = self.min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            try:
                req = urllib.request.Request(url, headers={"Accept": "application/json, text/csv"})
                with self._opener.open(req, timeout=60) as resp:
                    body = resp.read().decode("utf-8-sig")
                return body if raw else json.loads(body or "null")
            except urllib.error.HTTPError as e:
                retryable = e.code == 429 or e.code >= 500
                if not retryable or attempt == self.max_retries:
                    detail = self._redact(e.read().decode("utf-8", "replace")[:300]) if e.fp else ""
                    raise SystemExit(f"Smartlead {e.code} on GET {path}: {detail}") from None
                retry_after = e.headers.get("Retry-After") if e.headers else None
                sleep_for = float(retry_after) if retry_after and retry_after.isdigit() else delay
                if e.code == 429 and not retry_after:
                    sleep_for = max(sleep_for, 6.0)  # per-endpoint limits are per 60 s
                print(f"  {e.code} on {path}, retrying in {sleep_for:.0f}s", file=sys.stderr)
                time.sleep(sleep_for)
                delay = min(delay * 2, 60)
            except urllib.error.URLError as e:
                if attempt == self.max_retries:
                    raise SystemExit(f"Network error on GET {path}: {self._redact(str(e.reason))}") from None
                time.sleep(delay)
                delay = min(delay * 2, 60)
        raise SystemExit(f"GET {path} failed")

    def paged(self, path: str, limit: int = 100, max_pages: int = 2000, **params) -> list:
        """Offset/limit pagination.

        Reads until an empty page rather than trusting a short page to be the
        last: a server that caps page size below `limit` would otherwise cut
        the list short without saying so. Stops if a page repeats the previous
        one (an endpoint that ignores offset).
        """
        out, offset, previous = [], 0, None
        for _ in range(max_pages):
            page = as_list(self.get(path, offset=offset, limit=limit, **params))
            if not page or page == previous:
                return out
            out.extend(page)
            offset += len(page)
            previous = page
        raise SystemExit(f"GET {path}: stopped after {max_pages} pages")


def as_list(resp) -> list:
    """Accept a bare array or an envelope like {"data": [...]}."""
    if isinstance(resp, list):
        return resp
    if isinstance(resp, dict):
        for key in ("data", "campaigns", "email_accounts", "leads", "results"):
            if isinstance(resp.get(key), list):
                return resp[key]
    return []


# --------------------------------------------------------------------------
# Parsing helpers (the docs disagree on types, so be lenient)
# --------------------------------------------------------------------------

def to_int(v) -> int:
    try:
        return int(float(str(v).strip() or 0))
    except (TypeError, ValueError):
        return 0


def to_pct(v) -> float | None:
    """'98%' or 98 or '98' -> 98.0; None/'' -> None."""
    if v is None:
        return None
    s = str(v).strip().rstrip("%").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_date(v) -> dt.date | None:
    if not v:
        return None
    try:
        return dt.datetime.fromisoformat(str(v).replace("Z", "+00:00")).date()
    except ValueError:
        return None


def provider_of(acc: dict) -> str:
    t = str(acc.get("type") or "").upper()
    if t == "GMAIL":
        return "Google"
    if t == "OUTLOOK":
        return "Microsoft"
    host = str(acc.get("smtp_host") or "").lower()
    if "gmail" in host or "google" in host:
        return "Google"
    if "office365" in host or "outlook" in host:
        return "Microsoft"
    return f"SMTP ({t.lower() or 'unknown'})"


def tag_names(obj: dict) -> list[str]:
    names = []
    for t in obj.get("tags") or []:
        if isinstance(t, dict):
            names.append(str(t.get("tag_name") or t.get("name") or ""))
        else:
            names.append(str(t))
    return [n for n in names if n]


def warmup_info(acc: dict) -> dict:
    w = acc.get("warmup_details") or {}
    return {
        "status": str(w.get("status") or "").upper(),
        "reputation": to_pct(w.get("warmup_reputation")),
        "started": parse_date(w.get("warmup_created_at") or w.get("created_at")),
        "blocked": bool(w.get("is_warmup_blocked")) or bool(w.get("blocked_reason")),
        "blocked_reason": str(w.get("blocked_reason") or ""),
        "sent": to_int(w.get("total_sent_count")),
        "spam": to_int(w.get("total_spam_count")),
    }


def verdict(acc: dict, today: dt.date, ready: float = READY_REPUTATION,
            retire: float = RETIRE_REPUTATION, min_days: int = MIN_WARMUP_DAYS) -> tuple[str, str]:
    """READY / REST / FIX / RETIRE with a one-line reason."""
    if acc.get("is_suspended"):
        return "RETIRE", "account suspended"
    smtp_ok = acc.get("is_smtp_success") is not False
    imap_ok = acc.get("is_imap_success") is not False
    if not (smtp_ok and imap_ok):
        err = acc.get("smtp_failure_error") or acc.get("imap_failure_error") or ""
        which = "SMTP" if not smtp_ok else "IMAP"
        return "FIX", f"{which} disconnected" + (f": {str(err)[:80]}" if err else "")

    w = warmup_info(acc)
    rep = w["reputation"]
    if w["blocked"]:
        return "FIX", "warmup blocked" + (f": {w['blocked_reason'][:80]}" if w["blocked_reason"] else "")
    if rep is not None and rep < retire:
        return "RETIRE", f"reputation {rep:g}% (under {retire:g}%)"
    if w["status"] != "ACTIVE":
        return "REST", f"warmup is {w['status'].lower() or 'off'}: turn it on before sending"
    if rep is None:
        return "REST", "no warmup reputation yet"
    if rep < ready:
        return "REST", f"reputation {rep:g}% (under {ready:g}%)"
    if w["started"] is not None:
        age = (today - w["started"]).days
        if age < min_days:
            return "REST", f"warming only {age} days (needs {min_days})"
    return "READY", f"reputation {rep:g}%"


def campaign_flags(row: dict, not_ready_inboxes: int) -> list[str]:
    flags = []
    if row["bounce_rate_pct"] > 3:
        flags.append("PAUSE: bounce over 3%")
    elif row["bounce_rate_pct"] > 2:
        flags.append("WATCH: bounce over 2%")
    if row["leads_contacted"] >= 500 and row["reply_rate_pct"] < 1:
        flags.append("LOW REPLIES: under 1% after 500 leads")
    if row["status"] == "DRAFTED":
        flags.append("DRAFT: never launched")
    if row["status"] in ("ACTIVE", "PAUSED") and row["leads_left"] > 0:
        flags.append(f"UNFINISHED: {row['leads_left']} leads left")
    if not_ready_inboxes:
        flags.append(f"{not_ready_inboxes} inbox(es) not Ready")
    return flags


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def ja_campaigns(sl: Smartlead, match: str, client_id: str | None) -> list[dict]:
    rx = re.compile(match, re.I)
    campaigns = as_list(sl.get("/campaigns/", client_id=client_id, include_tags="true"))
    if client_id:
        return [c for c in campaigns if str(c.get("client_id")) == str(client_id)]
    return [c for c in campaigns
            if rx.search(str(c.get("name") or "")) or any(rx.search(t) for t in tag_names(c))]


def campaign_inboxes(sl: Smartlead, campaigns: list[dict]) -> dict[int, list[dict]]:
    """campaign id -> inboxes attached to it."""
    out = {}
    for c in campaigns:
        out[c["id"]] = as_list(sl.get(f"/campaigns/{c['id']}/email-accounts"))
    return out


def cmd_accounts(args, accounts: list[dict], verdicts: dict, campaigns: list[dict],
                 inboxes_by_campaign: dict[int, list[dict]]) -> None:
    names = {c["id"]: str(c.get("name") or c["id"]) for c in campaigns}
    in_campaigns: dict[int, list[str]] = {}
    for cid, accs in inboxes_by_campaign.items():
        for a in accs:
            if a.get("id") is not None:
                in_campaigns.setdefault(a["id"], []).append(names[cid])

    tag_rx = re.compile(args.account_tag, re.I) if args.account_tag else None
    domains = {d.lower().lstrip("@") for d in args.domain}

    rows = []
    for a in accounts:
        email = str(a.get("from_email") or a.get("username") or "")
        domain = email.rsplit("@", 1)[-1].lower() if "@" in email else ""
        tags = tag_names(a)
        include = (args.all_accounts
                   or a.get("id") in in_campaigns
                   or (args.client_id and str(a.get("client_id")) == str(args.client_id))
                   or (tag_rx and any(tag_rx.search(t) for t in tags))
                   or domain in domains)
        if not include:
            continue
        v, why = verdicts[a.get("id")]
        w = warmup_info(a)
        rows.append({
            "verdict": v,
            "reason": why,
            "from_email": email,
            "from_name": a.get("from_name") or "",
            "provider": provider_of(a),
            "domain": domain,
            "warmup_status": w["status"],
            "warmup_reputation_pct": "" if w["reputation"] is None else f"{w['reputation']:g}",
            "warmup_started": w["started"].isoformat() if w["started"] else "",
            "warmup_sent": w["sent"],
            "warmup_spam": w["spam"],
            "smtp_ok": a.get("is_smtp_success"),
            "imap_ok": a.get("is_imap_success"),
            "cold_cap_per_day": a.get("message_per_day") or "",
            "sent_today": a.get("daily_sent_count") or "",
            "ja_campaigns": "; ".join(sorted(in_campaigns.get(a.get("id"), []))),
            "tags": "; ".join(tags),
            "client_id": a.get("client_id") or "",
            "account_id": a.get("id"),
        })

    order = {"RETIRE": 0, "FIX": 1, "REST": 2, "READY": 3}
    rows.sort(key=lambda r: (order.get(r["verdict"], 9), r["provider"], r["domain"], r["from_email"]))
    write_csv(args.out / "accounts.csv", rows)

    # Domain roll-up: a domain with several weak inboxes is the problem, not the inbox.
    by_domain: dict[str, dict] = {}
    for r in rows:
        d = by_domain.setdefault(r["domain"], {"domain": r["domain"], "provider": r["provider"],
                                               "inboxes": 0, "READY": 0, "REST": 0, "FIX": 0, "RETIRE": 0})
        d["inboxes"] += 1
        d[r["verdict"]] += 1
    write_csv(args.out / "domains.csv", sorted(by_domain.values(), key=lambda d: -d["RETIRE"]))

    print_counts("Inboxes", rows, ("verdict", "provider"))
    for r in rows:
        if r["verdict"] != "READY" and r["ja_campaigns"]:
            print(f"  ! {r['verdict']:6s} {r['from_email']} is still in: {r['ja_campaigns']}")


def cmd_campaigns(sl, args, verdicts: dict, campaigns: list[dict],
                  inboxes_by_campaign: dict[int, list[dict]]) -> None:
    rows = []
    for c in campaigns:
        a = sl.get(f"/campaigns/{c['id']}/analytics") or {}
        stats = a.get("campaign_lead_stats") or {}
        sent = to_int(a.get("sent_count"))
        contacted = to_int(a.get("unique_sent_count")) or sent
        bounces = to_int(a.get("bounce_count"))
        replies = to_int(a.get("reply_count"))
        total = to_int(stats.get("total")) or to_int(a.get("total_count"))
        left = to_int(stats.get("notStarted")) + to_int(stats.get("inprogress"))
        inboxes = inboxes_by_campaign.get(c["id"], [])
        not_ready = sum(1 for i in inboxes
                        if verdicts.get(i.get("id"), ("UNKNOWN",))[0] != "READY")
        row = {
            "name": c.get("name") or "",
            "status": str(a.get("status") or c.get("status") or "").upper(),
            "created": str(c.get("created_at") or "")[:10],
            "leads_total": total,
            "leads_left": left,
            "leads_completed": to_int(stats.get("completed")),
            "leads_blocked": to_int(stats.get("blocked")),
            "emails_sent": sent,
            "leads_contacted": contacted,
            "replies": replies,
            "reply_rate_pct": round(100 * replies / contacted, 2) if contacted else 0.0,
            "bounces": bounces,
            "bounce_rate_pct": round(100 * bounces / contacted, 2) if contacted else 0.0,
            "unsubscribed": to_int(a.get("unsubscribed_count")),
            "inboxes": len(inboxes),
            "inboxes_microsoft": sum(1 for i in inboxes if provider_of(i) == "Microsoft"),
            "plain_text": c.get("send_as_plain_text", ""),
            "client_id": c.get("client_id") or "",
            "campaign_id": c["id"],
        }
        row["flags"] = "; ".join(campaign_flags(row, not_ready))
        rows.append(row)

    rows.sort(key=lambda r: (-r["bounce_rate_pct"], r["name"]))
    write_csv(args.out / "campaigns.csv", rows)
    print_counts("Campaigns", rows, ("status",))
    for r in rows:
        if r["flags"]:
            print(f"  - {r['name']}: {r['flags']}")


def cmd_export_leads(sl, args, today):
    campaigns = ja_campaigns(sl, args.match, args.client_id)
    args.out.mkdir(parents=True, exist_ok=True)
    for c in campaigns:
        csv_text = sl.get(f"/campaigns/{c['id']}/leads-export", raw=True)
        rows = list(csv.DictReader(io.StringIO(csv_text)))
        bounced = set()
        for s in sl.paged(f"/campaigns/{c['id']}/statistics", email_status="bounced"):
            if s.get("is_bounced") in (True, "true", 1, "1") and s.get("lead_email"):
                bounced.add(str(s["lead_email"]).strip().lower())
        for r in rows:
            r["is_bounced"] = "true" if (r.get("email") or "").strip().lower() in bounced else "false"
            r["campaign_name"] = c.get("name") or ""
        slug = re.sub(r"[^A-Za-z0-9]+", "_", str(c.get("name") or "")).strip("_")[:60]
        path = args.out / f"{c['id']}_{slug}.csv"
        fields = list(rows[0].keys()) if rows else ["email", "is_bounced", "campaign_name"]
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"  {len(rows):6d} leads, {len(bounced):4d} bounced  -> {path}")


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else ["(no rows)"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {path}")


def print_counts(label: str, rows: list[dict], keys: tuple[str, ...]) -> None:
    counts = Counter(tuple(str(r[k]) for k in keys) for r in rows)
    print(f"\n{label}:")
    for combo, n in sorted(counts.items()):
        print(f"  {' / '.join(combo):30s} {n:5d}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["accounts", "campaigns", "export-leads", "all"])
    ap.add_argument("--match", default=DEFAULT_MATCH,
                    help=f"regex for Joint Academy campaign names or tags (default: {DEFAULT_MATCH!r})")
    ap.add_argument("--client-id", help="Smartlead client id for Joint Academy, if it has one")
    ap.add_argument("--account-tag", default=DEFAULT_ACCOUNT_TAG,
                    help="regex: inboxes with a matching tag are included (default: ^JA)")
    ap.add_argument("--domain", nargs="*", default=[], help="sending domains to include")
    ap.add_argument("--all-accounts", action="store_true", help="list every inbox in the workspace")
    ap.add_argument("--ready", type=float, default=READY_REPUTATION, help="reputation %% for READY")
    ap.add_argument("--retire", type=float, default=RETIRE_REPUTATION, help="reputation %% below which to RETIRE")
    ap.add_argument("--min-warmup-days", type=int, default=MIN_WARMUP_DAYS)
    ap.add_argument("--out", type=Path, default=None,
                    help="output folder (default: audit/<today>, or exports/ for export-leads)")
    args = ap.parse_args(argv)

    api_key = os.environ.get("SMARTLEAD_API_KEY", "").strip()
    if not api_key:
        print("Set SMARTLEAD_API_KEY first (Smartlead > Settings > API key).", file=sys.stderr)
        return 2

    today = dt.date.today()
    if args.out is None:
        args.out = Path("exports") if args.command == "export-leads" else Path("audit") / today.isoformat()
    sl = Smartlead(api_key)

    if args.command == "export-leads":
        cmd_export_leads(sl, args, today)
        return 0

    campaigns = ja_campaigns(sl, args.match, args.client_id)
    print(f"Joint Academy campaigns found: {len(campaigns)}")
    inboxes = campaign_inboxes(sl, campaigns)
    # Campaign inbox lists carry no warmup data, so verdicts come from the
    # full account list.
    accounts = sl.paged("/email-accounts/")
    verdicts = {a.get("id"): verdict(a, today, args.ready, args.retire, args.min_warmup_days)
                for a in accounts}
    if args.command in ("accounts", "all"):
        cmd_accounts(args, accounts, verdicts, campaigns, inboxes)
    if args.command in ("campaigns", "all"):
        cmd_campaigns(sl, args, verdicts, campaigns, inboxes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
