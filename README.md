# OPPT Locations Contact Scraper

Scrapes [theoppt.com/locations](https://www.theoppt.com/locations/) and pulls,
for every clinic location, the named contacts — **Client Manager (PT Owner)**
and **Business Manager** — with their **name, role, and email**.

## Output

- `contacts.csv` / `contacts.json` — one row per contact:
  `location, location_url, role, name, email, phone, address`
- `snapshots/<slug>.html` — the raw rendered HTML of each location page, saved so
  the extraction selectors can be refined if any name/email comes back blank.

## Why a headless browser?

`theoppt.com` sits behind bot protection that returns `403` to plain HTTP
clients (`requests`, `curl`). The scraper therefore drives a real Chromium
browser via [Playwright], which renders the JS and passes the challenge.

## Run it

```bash
pip install -r requirements.txt
playwright install chromium      # one-time: downloads the browser binary
python scraper.py
```

Useful flags:

```bash
python scraper.py --headed       # show the browser window (helps if challenged)
python scraper.py --limit 3      # only scrape the first 3 locations (a quick test)
python scraper.py --out output   # write CSV/JSON/snapshots into ./output
```

## Important: run this on your own machine

This repo was opened in a Claude Code **web** session whose network policy is an
allowlist (it permits PyPI/npm/GitHub but **blocks `theoppt.com`**), so the
scraper cannot reach the site from inside that environment. Run it locally —
where there is no allowlist — or recreate the web environment with an
unrestricted network policy. See the
[network policy docs](https://code.claude.com/docs/en/claude-code-on-the-web).

## Tuning the extractor

The site's per-location markup isn't publicly inspectable from the sandbox, so
the name/role/email extraction in `scraper.py` is heuristic:

- **Roles** are matched from the label text (`Client Manager`, `PT Owner`,
  `Business Manager`) — see `ROLE_PATTERNS`.
- **Emails** come from `mailto:` links inside the contact card.
- **Names** are the most name-like line in the card.

If a field is blank after the first run, open the matching file in `snapshots/`,
find the real element/class names, and tighten the selectors in
`extract_contacts_from_page()`.

[Playwright]: https://playwright.dev/python/
