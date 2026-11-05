# Joint Academy outbound tools

Scripts that support the Joint Academy outbound reset plan (Smartlead):

| Script | What it does | Touches Smartlead? |
| --- | --- | --- |
| `smartlead_audit.py` | Lists every JA inbox with a verdict (READY / REST / FIX / RETIRE) and every JA campaign with bounce rate, reply rate, leads left and flags. Exports campaign leads with an `is_bounced` column. | Read-only (GET requests only) |
| `lead_filter.py` | Turns lead exports into clean lists: physical therapists only (never physicians), no one who replied, bounced, unsubscribed or is Do Not Contact, de-duplicated across campaigns, split into re-engage vs never contacted, and optionally into Microsoft vs Google/other mail hosts. | No (local CSV files) |
| `spintax_check.py` | Checks Smartlead spintax copy for broken braces, single-brace variables, empty options and spam words, counts versions and prints sample renders. | No |

Python 3.9+ and the standard library only: nothing to install.

Everything else in this repository (the OPPT scraper) is unrelated and untouched.

## Run them on your own machine

Smartlead takes the API key only as a URL parameter, so run these locally, not
in a shared or cloud environment. The scripts redact the key from every message.

```bash
cd jointacademy
export SMARTLEAD_API_KEY=your-key      # Smartlead > Settings > API key
```

On Windows (PowerShell): `$env:SMARTLEAD_API_KEY = "your-key"`.

## Week 1: audit

```bash
python smartlead_audit.py all
```

Writes `audit/<today>/`:

- `accounts.csv`: one row per JA inbox, worst first. Verdict rules: **READY** = connected, warmup on, reputation 97%+, warmed 14+ days. **REST** = 85–96%, warmup off, or warmed under 14 days. **FIX** = SMTP/IMAP disconnected or warmup blocked. **RETIRE** = under 85% or suspended. It also prints every non-Ready inbox still sitting in a campaign.
- `domains.csv`: verdicts rolled up per sending domain. Several weak inboxes on one domain point at the domain.
- `campaigns.csv`: JA campaigns, highest bounce rate first, with flags (`PAUSE: bounce over 3%`, `UNFINISHED`, `DRAFT`, `LOW REPLIES`, `N inbox(es) not Ready`).

Which campaigns count as Joint Academy: names matching `--match` (default: contains "Joint Academy" or starts with "JA"). If Joint Academy is its own Smartlead client, use `--client-id <id>` instead. Inboxes are included when they sit in a JA campaign, belong to that client, carry a tag starting with `JA`, or use a domain passed with `--domain`. Thresholds can be changed with `--ready`, `--retire` and `--min-warmup-days`.

## Week 1–2: leads

```bash
# 1. Export every JA campaign's leads (adds is_bounced, which Smartlead's export lacks)
python smartlead_audit.py export-leads --out exports

# 2. Non-repliers from old campaigns, physical therapists only, split by mail host
python lead_filter.py exports/*.csv --history sources/*.csv --exclude customers.csv --out out/reengage --mx

# 3. Fresh leads, checked against everything already contacted
python lead_filter.py fresh/apollo.csv --history exports/*.csv sources/*.csv --exclude customers.csv --out out/fresh --mx
```

- `--history`: files used only for checking, never output. A person who replied, bounced or unsubscribed in any of them is excluded. If your Smartlead exports have no job titles, put the original lead source files (e.g. Apollo exports) here: titles are filled in from them by email.
- `--exclude`: emails or domains never to contact (customers, other clients' leads). A CSV with an email/domain column, or one per line.
- `--mx`: looks up each recipient domain's mail host (DNS over HTTPS, cached in `.mx_cache.json`).

Output in `--out`:

| File | Goes to |
| --- | --- |
| `reengage_microsoft.csv` | JA / PT re-engage / MS campaign |
| `reengage_google_and_other.csv` | JA / PT re-engage / Google campaign |
| `never_contacted_microsoft.csv` | JA / PT fresh / MS campaign |
| `never_contacted_google_and_other.csv` | JA / PT fresh / Google campaign |
| `review.csv` | A human: titles that are neither clearly PT nor clearly physician |
| `excluded.csv` | Nobody; each row says why it was dropped |
| `summary.txt` | Counts |

Verify every list with an email verifier before uploading.

How roles are decided: physical therapist titles (Physical Therapist, Physiotherapist, PT, DPT, MPT, PTA, fysioterapeut, sjukgymnast) are kept. Physician titles (Physician, MD, DO, Surgeon, Physiatrist, PM&R, läkare, ortoped) are excluded, as are other professions (chiropractor, physician assistant, OT, naprapat, nurse). Owners, directors and managers are kept only when the company name is clearly a PT practice. Support roles at PT clinics (aide, receptionist, billing, student) and anything unclear go to review.

## Before approving copy

```bash
python spintax_check.py copy/step1.txt
```

Exit code 1 means errors; fix them before the copy goes into Smartlead.

## Keep lead data out of git

`audit/`, `exports/`, `out/`, `sources/`, `fresh/` and `.mx_cache.json` are git-ignored here because they hold personal data. Do not commit lead files.

## Tests

```bash
python -m unittest discover -s tests
```

The Smartlead tests use a fake API built from the documented response shapes. The scripts have not yet been run against a live Smartlead account, so check the first `accounts.csv` against what the Smartlead UI shows.
