#!/usr/bin/env python3
"""
OPPT locations contact scraper.

Scrapes https://www.theoppt.com/locations/ and, for every clinic location,
extracts the named contacts (Client Manager / PT Owner and Business Manager)
together with their email address and role.

Output: contacts.csv and contacts.json with columns
    location, location_url, role, name, email, phone, address

The live site is fronted by bot protection that 403s plain HTTP clients, so we
drive a real headless browser via Playwright rather than `requests`.

Usage:
    pip install -r requirements.txt
    playwright install chromium
    python scraper.py
    # options:
    python scraper.py --headed        # watch the browser (helps if challenged)
    python scraper.py --out mydir     # write output + page snapshots elsewhere
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

BASE = "https://www.theoppt.com"
INDEX_URL = f"{BASE}/locations/"

# Role labels we care about. Map the various wordings the site might use to a
# normalized role name in the output.
ROLE_PATTERNS = [
    (re.compile(r"client\s+manager", re.I), "Client Manager (PT Owner)"),
    (re.compile(r"pt\s+owner", re.I), "Client Manager (PT Owner)"),
    (re.compile(r"business\s+manager", re.I), "Business Manager"),
]

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}")


@dataclass
class Contact:
    location: str
    location_url: str
    role: str
    name: str
    email: str
    phone: str = ""
    address: str = ""


def normalize_role(text: str) -> str | None:
    for pattern, label in ROLE_PATTERNS:
        if pattern.search(text):
            return label
    return None


def collect_location_links(page) -> list[str]:
    """Return absolute URLs of every individual location page on the index."""
    hrefs = page.eval_on_selector_all(
        "a[href*='/locations/']",
        "els => els.map(e => e.getAttribute('href'))",
    )
    links: list[str] = []
    seen = set()
    for href in hrefs:
        if not href:
            continue
        url = urljoin(BASE, href)
        # Skip the index itself; keep only deeper /locations/<slug> pages.
        path = url.split("?")[0].rstrip("/")
        if path.endswith("/locations"):
            continue
        if "/locations/" not in path:
            continue
        if url not in seen:
            seen.add(url)
            links.append(url)
    return links


def extract_contacts_from_page(page, url: str, snapshot_dir: Path) -> list[Contact]:
    """Heuristically pull (role, name, email) cards from a location page."""
    location_name = (page.title() or "").split("|")[0].strip()

    # Save a snapshot so selectors can be refined against real markup later.
    try:
        slug = url.rstrip("/").split("/")[-1] or "index"
        (snapshot_dir / f"{slug}.html").write_text(page.content(), encoding="utf-8")
    except Exception:
        pass

    page_text = page.inner_text("body")
    phones = PHONE_RE.findall(page_text)
    phone = phones[0] if phones else ""

    # Address: first plausible "street ... city, ST zip" line.
    address = ""
    addr_match = re.search(
        r"\d{1,6}[^\n,]+,[^\n]+,?\s*[A-Z]{2}\s*\d{5}", page_text
    )
    if addr_match:
        address = re.sub(r"\s+", " ", addr_match.group(0)).strip()

    contacts: list[Contact] = []
    seen = set()

    # Strategy: find every element whose own text names a role, climb to a small
    # containing card, then read the name (a heading-ish line) and the email
    # (a mailto link) out of that card.
    role_nodes = page.query_selector_all(
        "xpath=//*[contains(translate(., 'CLIENTBUSNSMGROWP', 'clientbusnsmgrowp'), 'manager')]"
    )
    for node in role_nodes:
        try:
            node_text = node.inner_text()
        except Exception:
            continue
        role = normalize_role(node_text)
        if not role:
            continue

        # Walk up a few ancestors to find a container that also holds an email.
        card = node
        card_html = ""
        for _ in range(5):
            try:
                card_html = card.inner_html()
            except Exception:
                card_html = ""
            if "mailto:" in card_html or EMAIL_RE.search(card_html):
                break
            parent = card.query_selector("xpath=..")
            if not parent:
                break
            card = parent

        try:
            card_text = card.inner_text()
        except Exception:
            card_text = node_text

        # Email: prefer a mailto href, else regex from text.
        email = ""
        mailto = card.query_selector("a[href^='mailto:']")
        if mailto:
            href = mailto.get_attribute("href") or ""
            email = href.replace("mailto:", "").split("?")[0].strip()
        if not email:
            m = EMAIL_RE.search(card_text)
            email = m.group(0) if m else ""

        name = guess_name(card_text, role)

        key = (role, name, email)
        if key in seen:
            continue
        seen.add(key)
        contacts.append(
            Contact(
                location=location_name,
                location_url=url,
                role=role,
                name=name,
                email=email,
                phone=phone,
                address=address,
            )
        )

    return contacts


def guess_name(card_text: str, role: str) -> str:
    """Pick the most name-like line from a contact card."""
    lines = [ln.strip() for ln in card_text.splitlines() if ln.strip()]
    role_words = re.compile(r"manager|owner|email|phone|director|pt\b", re.I)
    candidates = []
    for ln in lines:
        if EMAIL_RE.search(ln) or PHONE_RE.search(ln):
            continue
        if role_words.search(ln):
            continue
        # A person's name: 2-4 capitalized words, no digits.
        if re.fullmatch(r"([A-Z][A-Za-z.'\-]+\s+){1,3}[A-Z][A-Za-z.'\-]+", ln):
            candidates.append(ln)
    return candidates[0] if candidates else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--headed", action="store_true", help="run a visible browser")
    ap.add_argument("--out", default=".", help="output directory")
    ap.add_argument("--limit", type=int, default=0, help="only scrape N locations")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    snapshot_dir = out / "snapshots"
    snapshot_dir.mkdir(exist_ok=True)

    all_contacts: list[Contact] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 900},
            locale="en-US",
        )
        page = context.new_page()

        print(f"Loading index: {INDEX_URL}", file=sys.stderr)
        page.goto(INDEX_URL, wait_until="networkidle", timeout=60000)
        links = collect_location_links(page)
        print(f"Found {len(links)} location pages", file=sys.stderr)

        if args.limit:
            links = links[: args.limit]

        for i, url in enumerate(links, 1):
            print(f"[{i}/{len(links)}] {url}", file=sys.stderr)
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
            except PWTimeout:
                print(f"  timeout, skipping", file=sys.stderr)
                continue
            contacts = extract_contacts_from_page(page, url, snapshot_dir)
            for c in contacts:
                print(f"  -> {c.role}: {c.name or '???'} <{c.email or 'no email'}>",
                      file=sys.stderr)
            all_contacts.extend(contacts)

        browser.close()

    # Write CSV
    csv_path = out / "contacts.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["location", "location_url", "role", "name", "email",
                        "phone", "address"],
        )
        writer.writeheader()
        for c in all_contacts:
            writer.writerow(asdict(c))

    json_path = out / "contacts.json"
    json_path.write_text(
        json.dumps([asdict(c) for c in all_contacts], indent=2),
        encoding="utf-8",
    )

    print(f"\nWrote {len(all_contacts)} contacts to {csv_path} and {json_path}",
          file=sys.stderr)
    print(f"Raw page snapshots saved in {snapshot_dir}/ (use these to refine "
          f"selectors if any names/emails are missing).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
