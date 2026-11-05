#!/usr/bin/env python3
"""Bygger viruspodden.se som en statisk sajt utifrån Podbeans RSS-flöde.

    python3 build.py              # hämtar flödet från feed_url i site.json
    python3 build.py --sample     # förhandsvisning med exempeldata (sample/feed.xml)
    python3 build.py --feed FIL   # valfritt flöde (URL eller lokal fil)

Resultatet hamnar i _site/ och kan läggas upp på valfri statisk webbhotell.
Endast Pythons standardbibliotek används.
"""

from __future__ import annotations

import argparse
import email.utils
import hashlib
import html
import json
import re
import shutil
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
SAMPLE_DIR = ROOT / "sample"

NS = {
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "atom": "http://www.w3.org/2005/Atom",
}

MONTHS_SV = [
    "januari", "februari", "mars", "april", "maj", "juni",
    "juli", "augusti", "september", "oktober", "november", "december",
]

e = html.escape


# --------------------------------------------------------------------------
# Hämta och tolka flödet
# --------------------------------------------------------------------------

def read_feed(source: str) -> bytes:
    if re.match(r"^https?://", source):
        req = urllib.request.Request(
            source,
            headers={"User-Agent": "viruspodden.se site builder (+https://viruspodden.se)"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    return Path(source).read_bytes()


def text(el: ET.Element | None, path: str, default: str = "") -> str:
    if el is None:
        return default
    found = el.find(path, NS)
    if found is None or found.text is None:
        return default
    return found.text.strip()


def attr(el: ET.Element | None, path: str, name: str, default: str = "") -> str:
    if el is None:
        return default
    found = el.find(path, NS)
    if found is None:
        return default
    return (found.get(name) or default).strip()


def parse_duration(raw: str) -> int:
    raw = (raw or "").strip()
    if not raw:
        return 0
    if raw.isdigit():
        return int(raw)
    parts = raw.split(":")
    try:
        nums = [int(float(p)) for p in parts]
    except ValueError:
        return 0
    seconds = 0
    for n in nums:
        seconds = seconds * 60 + n
    return seconds


def fmt_duration(seconds: int) -> str:
    if seconds <= 0:
        return ""
    minutes = round(seconds / 60)
    if minutes < 60:
        return f"{max(minutes, 1)} min"
    h, m = divmod(minutes, 60)
    return f"{h} h {m} min" if m else f"{h} h"


def fmt_date(d: datetime) -> str:
    return f"{d.day} {MONTHS_SV[d.month - 1]} {d.year}"


def slugify(value: str) -> str:
    value = value.lower().replace("å", "a").replace("ä", "a").replace("ö", "o")
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:80].strip("-") or "avsnitt"


def slug_from_link(link: str) -> str:
    """Podbean-länkar ser ut som https://xxx.podbean.com/e/avsnittets-namn/."""
    path = unquote(urlparse(link).path).strip("/")
    if path.startswith("e/"):
        return slugify(path[2:])
    return ""


class Sanitizer(HTMLParser):
    """Släpper bara igenom enkel, säker formatering i avsnittsbeskrivningar."""

    ALLOWED = {"p", "br", "a", "strong", "b", "em", "i", "ul", "ol", "li", "blockquote", "h3", "h4"}
    DROP_CONTENT = {"script", "style", "iframe", "object", "embed", "noscript"}
    VOID = {"br"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.stack: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.DROP_CONTENT:
            self.skip += 1
            return
        if self.skip:
            return
        if tag == "div":
            tag = "p"
        if tag in ("h1", "h2"):
            tag = "h3"
        if tag not in self.ALLOWED:
            return
        if tag == "a":
            href = dict(attrs).get("href", "") or ""
            if not re.match(r"^(https?:|mailto:)", href.strip(), re.I):
                self.stack.append("")  # behåll texten men inte länken
                return
            self.out.append(f'<a href="{e(href.strip())}" rel="noopener" target="_blank">')
            self.stack.append("a")
            return
        if tag in self.VOID:
            self.out.append("<br>")
            return
        self.out.append(f"<{tag}>")
        self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        if tag == "br" and not self.skip:
            self.out.append("<br>")

    def handle_endtag(self, tag):
        if tag in self.DROP_CONTENT:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag == "div":
            tag = "p"
        if tag in ("h1", "h2"):
            tag = "h3"
        if tag == "a":
            if self.stack and self.stack[-1] in ("a", ""):
                opened = self.stack.pop()
                if opened == "a":
                    self.out.append("</a>")
            return
        if tag not in self.ALLOWED or tag in self.VOID:
            return
        if tag in self.stack:
            while self.stack:
                t = self.stack.pop()
                if t:
                    self.out.append(f"</{t}>")
                if t == tag:
                    break

    def handle_data(self, data):
        if not self.skip:
            self.out.append(e(data, quote=False))

    def result(self) -> str:
        while self.stack:
            t = self.stack.pop()
            if t:
                self.out.append(f"</{t}>")
        out = "".join(self.out)
        out = re.sub(r"<p>\s*(<br>\s*)*</p>", "", out)
        return out.strip()


def sanitize(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return ""
    if not re.search(r"<[a-zA-Z/][^>]*>", raw):
        paras = [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip()]
        return "".join(f"<p>{e(p).replace(chr(10), '<br>')}</p>" for p in paras)
    s = Sanitizer()
    s.feed(raw)
    s.close()
    return s.result()


def plain(raw: str) -> str:
    raw = re.sub(r"<br\s*/?>|</p>|</li>", " ", raw or "", flags=re.I)
    raw = re.sub(r"<[^>]+>", "", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def excerpt(raw: str, limit: int = 200) -> str:
    t = plain(raw)
    if len(t) <= limit:
        return t
    cut = t[:limit].rsplit(" ", 1)[0].rstrip(",.;:–- ")
    return cut + "…"


def clean_title(title: str) -> str:
    """Podbean-titlar börjar ofta med avsnittsnumret ("34. Historien om HIV") –
    numret visas redan separat, så det tas bort ur rubriken."""
    cleaned = re.sub(r"^\s*(avsnitt\s*)?\d+\s*[.:]\s*[–-]?\s*", "", title, flags=re.I)
    return cleaned or title


def parse_date(raw: str) -> datetime:
    try:
        d = email.utils.parsedate_to_datetime(raw)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d
    except (TypeError, ValueError):
        return datetime(1970, 1, 1, tzinfo=timezone.utc)


def parse_feed(data: bytes) -> tuple[dict, list[dict]]:
    root = ET.fromstring(data)
    ch = root.find("channel")
    if ch is None:
        raise ValueError("Ogiltigt RSS-flöde: <channel> saknas")

    cover = attr(ch, "itunes:image", "href") or text(ch, "image/url")
    podcast = {
        "title": text(ch, "title"),
        "description": plain(text(ch, "itunes:summary") or text(ch, "description")),
        "link": text(ch, "link"),
        "image": cover,
        "author": text(ch, "itunes:author"),
        "language": text(ch, "language", "sv"),
        "email": text(ch, "itunes:owner/itunes:email"),
    }

    episodes: list[dict] = []
    for item in ch.findall("item"):
        audio = attr(item, "enclosure", "url")
        if not audio:
            continue
        title = text(item, "title") or "Avsnitt"
        link = text(item, "link")
        desc_raw = text(item, "content:encoded") or text(item, "description") or text(item, "itunes:summary")
        date = parse_date(text(item, "pubDate"))
        dur = parse_duration(text(item, "itunes:duration"))
        num = text(item, "itunes:episode")
        image = attr(item, "itunes:image", "href")
        episodes.append({
            "title": clean_title(title),
            "link": link,
            "guid": text(item, "guid") or audio,
            "date": date,
            "date_iso": date.date().isoformat(),
            "date_display": fmt_date(date),
            "duration": dur,
            "duration_display": fmt_duration(dur),
            "audio": audio,
            "audio_type": attr(item, "enclosure", "type") or "audio/mpeg",
            "number": int(num) if num.isdigit() else None,
            "season": text(item, "itunes:season"),
            "type": (text(item, "itunes:episodeType") or "full").lower(),
            "image": image if image and image != cover else "",
            "html": sanitize(desc_raw),
            "excerpt": excerpt(desc_raw),
            "summary": excerpt(desc_raw, 155),
        })

    episodes.sort(key=lambda ep: ep["date"], reverse=True)

    # Numrera i tidsordning om flödet saknar avsnittsnummer
    if not any(ep["number"] for ep in episodes):
        n = 0
        for ep in reversed(episodes):
            if ep["type"] == "full":
                n += 1
                ep["number"] = n

    # Stabila, unika adresser
    used: set[str] = set()
    for ep in reversed(episodes):
        base = slug_from_link(ep["link"]) or slugify(ep["title"])
        slug, i = base, 2
        while slug in used:
            slug, i = f"{base}-{i}", i + 1
        used.add(slug)
        ep["slug"] = slug

    return podcast, episodes


# --------------------------------------------------------------------------
# Ikoner (inline SVG)
# --------------------------------------------------------------------------

ICONS = {
    "play": '<path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.6-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z" fill="currentColor"/>',
    "pause": '<rect x="6.5" y="5" width="4" height="14" rx="1.2" fill="currentColor"/><rect x="13.5" y="5" width="4" height="14" rx="1.2" fill="currentColor"/>',
    "back": '<path d="M12 5V2L7 6l5 4V7a6 6 0 1 1-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><text x="12" y="16.5" font-size="7" font-weight="700" text-anchor="middle" fill="currentColor" font-family="Open Sans,system-ui,sans-serif">15</text>',
    "fwd": '<path d="M12 5V2l5 4-5 4V7a6 6 0 1 0 6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><text x="12" y="16.5" font-size="7" font-weight="700" text-anchor="middle" fill="currentColor" font-family="Open Sans,system-ui,sans-serif">30</text>',
    "close": '<path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "spotify": '<circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M7 9.6c3.4-1 7.3-.7 10.2 1M7.6 12.7c2.8-.8 5.9-.5 8.3.9M8.2 15.6c2.2-.6 4.5-.4 6.4.7" stroke="var(--icon-cut, #fff)" stroke-width="1.6" stroke-linecap="round" fill="none"/>',
    "apple": '<circle cx="12" cy="10" r="2.6" fill="currentColor"/><path d="M10.6 14h2.8l-.6 7h-1.6z" fill="currentColor"/><path d="M7.4 15.6a7 7 0 1 1 9.2 0M5 18.3a10 10 0 1 1 14 0" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round"/>',
    "podbean": '<path d="M4 14v-2a8 8 0 0 1 16 0v2" stroke="currentColor" stroke-width="2" fill="none"/><rect x="3" y="13" width="5" height="7" rx="2" fill="currentColor"/><rect x="16" y="13" width="5" height="7" rx="2" fill="currentColor"/>',
    "youtube": '<rect x="2" y="5" width="20" height="14" rx="4" fill="currentColor"/><path d="M10 9l5 3-5 3z" fill="var(--icon-cut, #fff)"/>',
    "amazon": '<path d="M4 15c4.5 3 11.5 3 16 0" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M17 13.5l3 1.5-1 3" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 5h8v6H8z" fill="currentColor"/>',
    "rss": '<circle cx="6" cy="18" r="2.2" fill="currentColor"/><path d="M4 10.5a9.5 9.5 0 0 1 9.5 9.5M4 4.5A15.5 15.5 0 0 1 19.5 20" stroke="currentColor" stroke-width="2.4" fill="none" stroke-linecap="round"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5" stroke="currentColor" stroke-width="2" fill="none"/><path d="M4 7l8 6 8-6" stroke="currentColor" stroke-width="2" fill="none" stroke-linejoin="round"/>',
    "share": '<path d="M12 3v12M7.5 7.5L12 3l4.5 4.5M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    "download": '<path d="M12 3v12M7.5 10.5L12 15l4.5-4.5M5 19h14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    "arrow-left": '<path d="M19 12H5M11 6l-6 6 6 6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    "arrow-right": '<path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    "search": '<circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="2" fill="none"/><path d="M16 16l4.5 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
}


def icon(name: str, cls: str = "icon") -> str:
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


def logo_svg(cls: str = "logo-mark") -> str:
    import math
    spikes = []
    for i in range(10):
        a = math.tau * i / 10 - math.pi / 2
        x1, y1 = 20 + 11.5 * math.cos(a), 20 + 11.5 * math.sin(a)
        x2, y2 = 20 + 16 * math.cos(a), 20 + 16 * math.sin(a)
        spikes.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>'
            f'<circle cx="{20 + 17.2 * math.cos(a):.2f}" cy="{20 + 17.2 * math.sin(a):.2f}" r="2.3" class="knob"/>'
        )
    return (
        f'<svg class="{cls}" viewBox="0 0 40 40" aria-hidden="true" focusable="false">'
        f'<g stroke="currentColor" stroke-width="2.2" stroke-linecap="round">{"".join(spikes)}</g>'
        '<circle cx="20" cy="20" r="11" fill="currentColor"/>'
        '<circle cx="16.2" cy="17" r="2.4" class="dot"/><circle cx="23.4" cy="16.2" r="1.6" class="dot"/>'
        '<circle cx="22" cy="23.6" r="2.8" class="dot"/><circle cx="15.6" cy="23.4" r="1.3" class="dot"/>'
        "</svg>"
    )


# --------------------------------------------------------------------------
# Sidmallar
# --------------------------------------------------------------------------

PLATFORM_LABELS = [
    ("spotify", "Spotify"),
    ("apple", "Apple Podcasts"),
    ("youtube", "YouTube"),
    ("amazon", "Amazon Music"),
    ("podbean", "Podbean"),
]


class Site:
    def __init__(self, cfg: dict, podcast: dict, episodes: list[dict], out: Path, preview: bool):
        self.cfg = cfg
        self.podcast = podcast
        self.episodes = episodes
        self.out = out
        self.preview = preview
        self.url = cfg["site_url"].rstrip("/")
        self.title = cfg.get("title") or podcast["title"] or "Viruspodden"
        platforms = dict(cfg.get("platforms") or {})
        if not platforms.get("podbean") and podcast.get("link"):
            platforms["podbean"] = podcast["link"]
        self.platforms = [(k, label, platforms[k]) for k, label in PLATFORM_LABELS if platforms.get(k)]
        self.feed_url = cfg.get("feed_url", "")
        self.cover = podcast.get("image") or ""
        self.versions: dict[str, str] = {}

    # --- hjälpare -------------------------------------------------------

    @staticmethod
    def prefix(depth: int) -> str:
        return "../" * depth if depth else "./"

    def asset(self, name: str, depth: int) -> str:
        v = self.versions.get(name, "")
        return f"{self.prefix(depth)}assets/{name}" + (f"?v={v}" if v else "")

    def cover_src(self, depth: int) -> str:
        if self.cover:
            return self.cover
        if (STATIC / "img" / "cover.jpg").exists():
            return self.asset("img/cover.jpg", depth)
        return self.asset("img/cover.svg", depth)

    def cover_abs(self) -> str:
        if self.cover:
            return self.cover
        if (STATIC / "img" / "cover.jpg").exists():
            return f"{self.url}/assets/img/cover.jpg"
        return f"{self.url}/assets/img/cover.svg"

    def ep_url(self, ep: dict, depth: int) -> str:
        return f"{self.prefix(depth)}avsnitt/{ep['slug']}/"

    def ep_label(self, ep: dict) -> str:
        if ep["type"] == "trailer":
            return "Trailer"
        if ep["type"] == "bonus":
            return "Bonusavsnitt"
        return f"Avsnitt {ep['number']}" if ep.get("number") else "Avsnitt"

    def play_attrs(self, ep: dict, depth: int) -> str:
        return (
            f'data-play data-id="{e(ep["slug"])}" data-src="{e(ep["audio"])}" '
            f'data-title="{e(ep["title"])}" data-url="{e(self.ep_url(ep, depth))}" '
            f'data-image="{e(ep["image"] or self.cover_src(depth))}"'
        )

    def platform_links(self, cls: str = "platforms", include_rss: bool = True) -> str:
        items = [
            f'<a class="platform" href="{e(url)}" target="_blank" rel="noopener">{icon(key)}<span>{e(label)}</span></a>'
            for key, label, url in self.platforms
        ]
        if include_rss and self.feed_url:
            items.append(
                f'<a class="platform" href="{e(self.feed_url)}" target="_blank" rel="noopener" '
                f'title="Kopiera RSS-adressen till valfri poddapp">{icon("rss")}<span>RSS</span></a>'
            )
        return f'<div class="{cls}">{"".join(items)}</div>' if items else ""

    # --- ramverk ----------------------------------------------------------

    def page(self, *, depth: int, title: str, description: str, path: str, body: str,
             og_type: str = "website", image: str = "", jsonld: dict | None = None,
             active: str = "") -> str:
        p = self.prefix(depth)
        canonical = f"{self.url}/{path}"
        full_title = title if title == self.title else f"{title} – {self.title}"
        og_image = image or self.cover_abs()
        nav = [
            ("Avsnitt", f"{p}avsnitt/", "avsnitt"),
            ("Om podden", f"{p}#om", "om"),
            ("Programledare", f"{p}#programledare", "programledare"),
            ("Kontakt", f"{p}#kontakt", "kontakt"),
        ]
        current = ' aria-current="page"'
        nav_html = "".join(
            f'<a href="{href}"{current if key == active else ""}>{label}</a>'
            for label, href, key in nav
        )
        preview = (
            '<div class="preview-banner" role="status">Förhandsvisning med exempeldata – '
            "riktiga avsnitt hämtas automatiskt från Podbean när sidan publiceras.</div>"
            if self.preview else ""
        )
        ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
        rss = (f'<link rel="alternate" type="application/rss+xml" title="{e(self.title)}" href="{e(self.feed_url)}">'
               if self.feed_url else "")
        year = datetime.now().year
        footer_contact = ""
        if self.cfg.get("contact", {}).get("email"):
            em = self.cfg["contact"]["email"]
            footer_contact = f'<a href="mailto:{e(em)}">{icon("mail")}<span>{e(em)}</span></a>'

        return f"""<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:site_name" content="{e(self.title)}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(og_image)}">
<meta property="og:locale" content="sv_SE">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0c4469">
<link rel="icon" href="{self.asset('img/favicon.svg', depth)}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{e(self.cover_src(depth))}">
{rss}
<link rel="preload" href="{p}assets/fonts/bebas-neue-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{p}assets/fonts/open-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{self.asset('style.css', depth)}">
{ld}
</head>
<body>
<a class="skip" href="#main">Hoppa till innehållet</a>
{preview}
<header class="site-header">
  <div class="wrap site-header__inner">
    <a class="brand" href="{p}" aria-label="{e(self.title)} – startsida">{logo_svg()}<span>{e(self.title.upper())}</span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Meny">{icon("menu")}</button>
    <nav id="site-nav" class="site-nav" aria-label="Huvudmeny">{nav_html}</nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap site-footer__inner">
    <div class="site-footer__brand">
      <a class="brand brand--footer" href="{p}">{logo_svg()}<span>{e(self.title.upper())}</span></a>
      <p>{e(self.cfg.get("tagline", ""))}</p>
    </div>
    <div class="site-footer__links">
      <h2 class="site-footer__heading">Lyssna</h2>
      {self.platform_links("platforms platforms--footer")}
    </div>
    <div class="site-footer__links">
      <h2 class="site-footer__heading">Sidor</h2>
      <nav class="footer-nav" aria-label="Sidfot">{nav_html}{footer_contact}</nav>
    </div>
  </div>
  <div class="wrap site-footer__legal">© {year} {e(self.title)} · Lennart Svensson &amp; Åke Lundkvist</div>
</footer>
{self.player_html()}
<script src="{self.asset('app.js', depth)}" defer></script>
</body>
</html>
"""

    def player_html(self) -> str:
        return f"""<div class="player" id="player" hidden aria-label="Ljudspelare" role="region">
  <div class="player__inner wrap">
    <img class="player__img" alt="" width="56" height="56">
    <div class="player__info">
      <a class="player__title" href="#"></a>
      <div class="player__time"><span data-cur>0:00</span><span aria-hidden="true"> / </span><span data-dur>–:–</span></div>
    </div>
    <div class="player__controls">
      <button class="icon-btn" data-skip="-15" aria-label="Spola tillbaka 15 sekunder">{icon("back")}</button>
      <button class="play-btn play-btn--lg" data-toggle aria-label="Spela">{icon("play", "icon icon-play")}{icon("pause", "icon icon-pause")}</button>
      <button class="icon-btn" data-skip="30" aria-label="Spola fram 30 sekunder">{icon("fwd")}</button>
    </div>
    <input class="player__seek" type="range" min="0" max="0" step="1" value="0" aria-label="Position i avsnittet">
    <button class="speed-btn" data-speed aria-label="Uppspelningshastighet">1×</button>
    <button class="icon-btn player__close" data-close aria-label="Stäng spelaren">{icon("close")}</button>
  </div>
  <audio preload="none"></audio>
</div>"""

    # --- komponenter ------------------------------------------------------

    def episode_row(self, ep: dict, depth: int, heading: str = "h3") -> str:
        meta = [f'<span class="ep-num">{self.ep_label(ep)}</span>', f'<time datetime="{ep["date_iso"]}">{ep["date_display"]}</time>']
        if ep["duration_display"]:
            meta.append(ep["duration_display"])
        search = e(f'{ep["title"]} {ep["excerpt"]} {self.ep_label(ep)}'.lower())
        img = (f'<img class="ep-row__img" src="{e(ep["image"])}" alt="" loading="lazy" width="88" height="88">'
               if ep["image"] else "")
        return f"""<article class="ep-row" data-search="{search}">
  <button class="play-btn" {self.play_attrs(ep, depth)} aria-label="Spela {e(ep['title'])}">{icon("play", "icon icon-play")}{icon("pause", "icon icon-pause")}</button>
  <div class="ep-row__body">
    <p class="meta">{' <span aria-hidden="true">·</span> '.join(meta)}</p>
    <{heading} class="ep-row__title"><a href="{self.ep_url(ep, depth)}">{e(ep["title"])}</a></{heading}>
    <p class="ep-row__excerpt">{e(ep["excerpt"])}</p>
  </div>
  {img}
</article>"""

    def featured(self, ep: dict) -> str:
        meta = [f'<span class="ep-num">{self.ep_label(ep)}</span>', f'<time datetime="{ep["date_iso"]}">{ep["date_display"]}</time>']
        if ep["duration_display"]:
            meta.append(ep["duration_display"])
        return f"""<section class="section section--featured" aria-labelledby="latest-h">
  <div class="wrap">
    <article class="featured">
      <img class="featured__img" src="{e(ep['image'] or self.cover_src(0))}" alt="" width="220" height="220">
      <div class="featured__body">
        <p class="eyebrow" id="latest-h">Senaste avsnittet</p>
        <h2 class="featured__title"><a href="{self.ep_url(ep, 0)}">{e(ep["title"])}</a></h2>
        <p class="meta">{' <span aria-hidden="true">·</span> '.join(meta)}</p>
        <p class="featured__excerpt">{e(ep["excerpt"])}</p>
        <div class="actions">
          <button class="btn btn--primary" {self.play_attrs(ep, 0)}>{icon("play", "icon icon-play")}{icon("pause", "icon icon-pause")}<span>Spela avsnittet</span></button>
          <a class="btn btn--ghost" href="{self.ep_url(ep, 0)}">Läs mer om avsnittet</a>
        </div>
      </div>
    </article>
  </div>
</section>"""

    def host_card(self, host: dict, depth: int, show_initials: bool = True) -> str:
        photo = host.get("photo", "")
        if photo and (STATIC / photo).exists():
            media = f'<img class="host__photo" src="{self.asset(photo, depth)}" alt="Porträtt av {e(host["name"])}" loading="lazy" width="160" height="160">'
        elif not show_initials:
            media = ""
        else:
            initials = "".join(w[0] for w in host["name"].split()[:2])
            media = f'<div class="host__photo host__photo--initials" aria-hidden="true">{e(initials)}</div>'
        bio = "".join(f"<p>{e(par)}</p>" for par in host.get("bio", []))
        aff = f'<p class="host__aff">{e(host["affiliation"])}</p>' if host.get("affiliation") else ""
        return f"""<article class="host">
  {media}
  <div class="host__body">
    <h3 class="host__name">{e(host["name"])}</h3>
    <p class="host__role">{e(host.get("role", ""))}</p>
    {aff}
    <div class="host__bio">{bio}</div>
  </div>
</article>"""

    def contact_section(self) -> str:
        c = self.cfg.get("contact", {}) or {}
        email_addr = c.get("email", "")
        endpoint = c.get("form_endpoint", "")
        key = c.get("form_access_key", "")
        mail_line = (f'<p class="contact__direct">Eller mejla direkt till '
                     f'<a href="mailto:{e(email_addr)}">{e(email_addr)}</a>.</p>' if email_addr else "")
        key_field = f'<input type="hidden" name="access_key" value="{e(key)}">' if key else ""
        return f"""<section class="section section--contact" id="kontakt" aria-labelledby="kontakt-h">
  <div class="wrap contact">
    <div class="contact__intro">
      <p class="eyebrow">Kontakt</p>
      <h2 id="kontakt-h">Hör av dig till oss</h2>
      <p>Har du en fråga om virus, ett förslag på ämne eller gäst – eller vill du nå oss som journalist eller arrangör? Skriv till oss så återkommer vi.</p>
      {mail_line}
    </div>
    <form class="contact__form" id="contact-form" data-endpoint="{e(endpoint)}" data-email="{e(email_addr)}" novalidate>
      {key_field}
      <input type="hidden" name="subject" value="Nytt meddelande via viruspodden.se">
      <div class="field field--hp" aria-hidden="true"><label>Lämna tomt <input type="text" name="botcheck" tabindex="-1" autocomplete="off"></label></div>
      <div class="field-row">
        <div class="field">
          <label for="cf-name">Namn</label>
          <input id="cf-name" name="name" type="text" autocomplete="name" required>
        </div>
        <div class="field">
          <label for="cf-email">E-post</label>
          <input id="cf-email" name="email" type="email" autocomplete="email" required>
        </div>
      </div>
      <div class="field">
        <label for="cf-topic">Ärende</label>
        <select id="cf-topic" name="topic">
          <option>Fråga till podden</option>
          <option>Förslag på ämne</option>
          <option>Förslag på gäst</option>
          <option>Press och media</option>
          <option>Föreläsning eller samarbete</option>
          <option>Övrigt</option>
        </select>
      </div>
      <div class="field">
        <label for="cf-message">Meddelande</label>
        <textarea id="cf-message" name="message" rows="6" required></textarea>
      </div>
      <p class="contact__privacy">Vi använder dina uppgifter enbart för att kunna svara dig.</p>
      <button class="btn btn--primary" type="submit">{icon("mail")}<span>Skicka meddelande</span></button>
      <p class="form-status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>"""

    # --- sidor ------------------------------------------------------------

    def build_index(self) -> None:
        eps = self.episodes
        latest = eps[0]
        more = eps[1:7]
        cfg = self.cfg
        first_year = min(ep["date"].year for ep in eps)
        full_count = sum(1 for ep in eps if ep["type"] == "full")
        stats = [
            (str(full_count), "avsnitt"),
            (f"{cfg.get('stats', {}).get('experience_years', 80)}+", "års samlad erfarenhet av virusforskning"),
            (str(first_year), "sändes första avsnittet"),
        ]
        stats_html = "".join(f'<div class="stat"><span class="stat__num">{e(n)}</span><span class="stat__label">{e(l)}</span></div>' for n, l in stats)
        about = "".join(f"<p>{e(p)}</p>" for p in cfg.get("about", []))
        duo_photo = cfg.get("hosts_photo", "")
        has_duo = bool(duo_photo) and (STATIC / duo_photo).exists()
        hosts = "".join(self.host_card(h, 0, show_initials=not has_duo) for h in cfg.get("hosts", []))
        duo = (f'<figure class="duo"><img src="{self.asset(duo_photo, 0)}" alt="Lennart Svensson och Åke Lundkvist" loading="lazy" width="960" height="624">'
               f'<figcaption>{e(cfg.get("byline", "").removeprefix("med ").strip())}</figcaption></figure>' if has_duo else "")
        rows = "".join(self.episode_row(ep, 0) for ep in more)

        body = f"""<section class="hero velvet">
  <div class="wrap hero__inner">
    <div class="hero__text">
      <h1 class="hero__title">{e(self.title.upper())}</h1>
      <p class="hero__byline">{e(cfg.get("byline", ""))}</p>
      <p class="hero__tagline">{e(cfg.get("tagline", ""))}</p>
      <p class="hero__intro">{e(cfg.get("intro", ""))}</p>
      <div class="actions">
        <button class="btn btn--primary" {self.play_attrs(latest, 0)}>{icon("play", "icon icon-play")}{icon("pause", "icon icon-pause")}<span>Lyssna på senaste avsnittet</span></button>
        <a class="btn btn--light" href="./avsnitt/">Alla avsnitt</a>
      </div>
      <div class="hero__platforms">
        <p class="hero__platforms-label">Lyssna där du lyssnar på poddar</p>
        {self.platform_links("platforms platforms--light")}
      </div>
    </div>
    <div class="hero__art">
      <img src="{e(self.cover_src(0))}" alt="Omslagsbild för {e(self.title)}" width="480" height="480">
    </div>
  </div>
</section>
{self.featured(latest)}
<section class="section" aria-labelledby="more-h">
  <div class="wrap">
    <div class="section__head">
      <h2 id="more-h">Fler avsnitt</h2>
      <a class="link-arrow" href="./avsnitt/">Alla {len(eps)} avsnitt {icon("arrow-right")}</a>
    </div>
    <div class="ep-list">{rows}</div>
    <div class="center"><a class="btn btn--ghost" href="./avsnitt/">Visa alla avsnitt</a></div>
  </div>
</section>
<section class="section section--alt" id="om" aria-labelledby="om-h">
  <div class="wrap about">
    <div class="about__text">
      <p class="eyebrow">Om podden</p>
      <h2 id="om-h">Välkomna till {e(self.title)}!</h2>
      {about}
    </div>
    <div class="stats">{stats_html}</div>
  </div>
</section>
<section class="section" id="programledare" aria-labelledby="pl-h">
  <div class="wrap">
    <p class="eyebrow">Programledare</p>
    <h2 id="pl-h">Två professorer i virologi</h2>
    {duo}
    <div class="hosts">{hosts}</div>
  </div>
</section>
{self.contact_section()}"""

        jsonld = {
            "@context": "https://schema.org",
            "@type": "PodcastSeries",
            "name": self.title,
            "description": " ".join(cfg.get("about", [])) or self.podcast["description"],
            "url": self.url + "/",
            "image": self.cover_abs(),
            "inLanguage": "sv",
            "webFeed": self.feed_url,
            "author": [{"@type": "Person", "name": h["name"]} for h in cfg.get("hosts", [])],
        }
        desc = f"{cfg.get('tagline', '')}. {cfg.get('intro', '')}".strip(". ")
        self.write("index.html", self.page(depth=0, title=self.title, description=desc, path="",
                                           body=body, jsonld=jsonld))

    def build_archive(self) -> None:
        groups: dict[int, list[dict]] = {}
        for ep in self.episodes:
            groups.setdefault(ep["date"].year, []).append(ep)
        blocks = []
        for year, eps in groups.items():
            rows = "".join(self.episode_row(ep, 1) for ep in eps)
            blocks.append(f'<section class="year-group" aria-labelledby="y{year}"><h2 class="year-group__h" id="y{year}">{year}</h2><div class="ep-list">{rows}</div></section>')
        body = f"""<section class="page-head velvet">
  <div class="wrap">
    <p class="eyebrow eyebrow--light">Arkiv</p>
    <h1>Alla avsnitt</h1>
    <p class="page-head__lead">{len(self.episodes)} avsnitt om virus och virussjukdomar – från rotavirus och hantavirus till pandemier och vacciner.</p>
    <div class="search">
      {icon("search")}
      <input id="ep-search" type="search" placeholder="Sök bland avsnitten, t.ex. ”influensa”" aria-label="Sök bland avsnitten" autocomplete="off">
    </div>
  </div>
</section>
<section class="section section--tight">
  <div class="wrap">
    <p class="search-count" id="search-count" aria-live="polite"></p>
    {''.join(blocks)}
    <p class="search-empty" id="search-empty" hidden>Inga avsnitt matchade sökningen.</p>
  </div>
</section>"""
        self.write("avsnitt/index.html", self.page(
            depth=1, title="Alla avsnitt", path="avsnitt/", body=body, active="avsnitt",
            description=f"Lyssna på alla {len(self.episodes)} avsnitt av {self.title} – {self.cfg.get('tagline', '')}."))

    def build_episode(self, i: int, ep: dict) -> None:
        newer = self.episodes[i - 1] if i > 0 else None
        older = self.episodes[i + 1] if i + 1 < len(self.episodes) else None
        meta = [f'<span class="ep-num">{self.ep_label(ep)}</span>', f'<time datetime="{ep["date_iso"]}">{ep["date_display"]}</time>']
        if ep["duration_display"]:
            meta.append(ep["duration_display"])
        nav = []
        if older:
            nav.append(f'<a class="ep-nav__link" href="../{older["slug"]}/" rel="prev"><span class="ep-nav__dir">{icon("arrow-left")} Föregående</span><span class="ep-nav__title">{e(older["title"])}</span></a>')
        else:
            nav.append("<span></span>")
        if newer:
            nav.append(f'<a class="ep-nav__link ep-nav__link--next" href="../{newer["slug"]}/" rel="next"><span class="ep-nav__dir">Nästa {icon("arrow-right")}</span><span class="ep-nav__title">{e(newer["title"])}</span></a>')
        podbean_link = (f'<a class="btn btn--ghost btn--sm" href="{e(ep["link"])}" target="_blank" rel="noopener">{icon("podbean")}<span>Öppna på Podbean</span></a>'
                        if ep["link"] else "")
        notes = ep["html"] or f'<p>{e(ep["excerpt"])}</p>'
        body = f"""<article class="episode">
  <header class="page-head page-head--episode velvet">
    <div class="wrap episode__head">
      <img class="episode__img" src="{e(ep['image'] or self.cover_src(2))}" alt="" width="240" height="240">
      <div>
        <a class="back-link" href="../">{icon("arrow-left")} Alla avsnitt</a>
        <p class="meta meta--light">{' <span aria-hidden="true">·</span> '.join(meta)}</p>
        <h1 class="episode__title">{e(ep["title"])}</h1>
        <div class="actions">
          <button class="btn btn--primary" {self.play_attrs(ep, 2)}>{icon("play", "icon icon-play")}{icon("pause", "icon icon-pause")}<span>Spela avsnittet</span></button>
          <button class="btn btn--light" data-share data-title="{e(ep['title'])}">{icon("share")}<span>Dela</span></button>
        </div>
      </div>
    </div>
  </header>
  <div class="wrap episode__layout">
    <div class="episode__notes prose">
      <h2 class="visually-hidden">Om avsnittet</h2>
      {notes}
    </div>
    <aside class="episode__aside">
      <h2 class="aside-h">Lyssna i din poddapp</h2>
      {self.platform_links("platforms platforms--stack")}
      <div class="episode__extra">
        {podbean_link}
        <a class="btn btn--ghost btn--sm" href="{e(ep['audio'])}" download>{icon("download")}<span>Ladda ner (mp3)</span></a>
      </div>
    </aside>
  </div>
  <nav class="wrap ep-nav" aria-label="Fler avsnitt">{''.join(nav)}</nav>
</article>"""
        jsonld = {
            "@context": "https://schema.org",
            "@type": "PodcastEpisode",
            "name": ep["title"],
            "url": f"{self.url}/avsnitt/{ep['slug']}/",
            "datePublished": ep["date_iso"],
            "description": ep["summary"],
            "associatedMedia": {"@type": "MediaObject", "contentUrl": ep["audio"]},
            "partOfSeries": {"@type": "PodcastSeries", "name": self.title, "url": self.url + "/"},
        }
        if ep.get("number"):
            jsonld["episodeNumber"] = ep["number"]
        if ep["duration"]:
            jsonld["timeRequired"] = f"PT{ep['duration'] // 60}M"
        self.write(f"avsnitt/{ep['slug']}/index.html", self.page(
            depth=2, title=ep["title"], path=f"avsnitt/{ep['slug']}/", body=body, og_type="article",
            description=ep["summary"] or self.cfg.get("tagline", ""), image=ep["image"], jsonld=jsonld,
            active="avsnitt"))

    def build_404(self) -> None:
        body = f"""<section class="page-head page-head--center velvet">
  <div class="wrap">
    <p class="eyebrow eyebrow--light">404</p>
    <h1>Sidan kunde inte hittas</h1>
    <p class="page-head__lead">Sidan du letar efter finns inte längre, eller så har adressen ändrats.</p>
    <div class="actions actions--center">
      <a class="btn btn--primary" href="{self.url}/">Till startsidan</a>
      <a class="btn btn--light" href="{self.url}/avsnitt/">Alla avsnitt</a>
    </div>
  </div>
</section>"""
        html_out = self.page(depth=0, title="Sidan kunde inte hittas", path="404.html", body=body,
                             description="Sidan kunde inte hittas.")
        # 404-sidan visas på godtycklig adress, så tillgångar måste ha absoluta sökvägar.
        html_out = html_out.replace('href="./assets/', f'href="{self.url}/assets/').replace('src="./assets/', f'src="{self.url}/assets/')
        html_out = html_out.replace('href="./"', f'href="{self.url}/"').replace('href="./#', f'href="{self.url}/#').replace('href="./avsnitt/', f'href="{self.url}/avsnitt/')
        self.write("404.html", html_out)

    def build_meta_files(self) -> None:
        now = datetime.now(timezone.utc).date().isoformat()
        urls = [(f"{self.url}/", self.episodes[0]["date_iso"]), (f"{self.url}/avsnitt/", self.episodes[0]["date_iso"])]
        urls += [(f"{self.url}/avsnitt/{ep['slug']}/", ep["date_iso"]) for ep in self.episodes]
        sm = "".join(f"<url><loc>{e(u)}</loc><lastmod>{d or now}</lastmod></url>" for u, d in urls)
        self.write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
        robots = "User-agent: *\nDisallow: /\n" if self.preview else f"User-agent: *\nAllow: /\n\nSitemap: {self.url}/sitemap.xml\n"
        self.write("robots.txt", robots)
        self.write(".nojekyll", "")

    # --- skrivning --------------------------------------------------------

    def write(self, rel: str, content: str) -> None:
        path = self.out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def copy_static(self) -> None:
        dest = self.out / "assets"
        shutil.copytree(STATIC, dest)
        for f in ("style.css", "app.js"):
            self.versions[f] = hashlib.sha1((STATIC / f).read_bytes()).hexdigest()[:8]
        (dest / "img").mkdir(exist_ok=True)
        (dest / "img" / "favicon.svg").write_text(
            logo_svg("").replace('<svg class=""', '<svg xmlns="http://www.w3.org/2000/svg" color="#2bbbb4"')
            .replace('class="knob"', 'fill="#2bbbb4"').replace('class="dot"', 'fill="#06191f"'),
            encoding="utf-8")
        if not (dest / "img" / "cover.svg").exists():
            (dest / "img" / "cover.svg").write_text(placeholder_cover(self.title), encoding="utf-8")

    def build(self) -> None:
        if self.out.exists():
            shutil.rmtree(self.out)
        self.out.mkdir(parents=True)
        self.copy_static()
        self.build_index()
        self.build_archive()
        for i, ep in enumerate(self.episodes):
            self.build_episode(i, ep)
        self.build_404()
        self.build_meta_files()


def placeholder_cover(title: str) -> str:
    mark = (logo_svg("").replace('<svg class=""', '<svg x="140" y="110" width="200" height="200" color="#2bbbb4"')
            .replace('class="knob"', 'fill="#2bbbb4"').replace('class="dot"', 'fill="#06191f"'))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 480">
<defs><radialGradient id="g" cx="50%" cy="40%" r="70%"><stop offset="0" stop-color="#1d5f8e"/><stop offset="1" stop-color="#0c4469"/></radialGradient></defs>
<rect width="480" height="480" fill="url(#g)"/>
{mark}
<text x="240" y="390" text-anchor="middle" font-family="Bebas Neue, Arial Narrow, sans-serif" font-size="72" letter-spacing="8" fill="#ffffff">{e(title.upper())}</text>
</svg>
"""


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--feed", help="RSS-flöde (URL eller fil). Standard: feed_url i site.json")
    ap.add_argument("--sample", action="store_true", help="Bygg med exempeldata från sample/feed.xml")
    ap.add_argument("--out", default=str(ROOT / "_site"), help="Utkatalog (standard: _site)")
    args = ap.parse_args()

    cfg = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    source = str(SAMPLE_DIR / "feed.xml") if args.sample else (args.feed or cfg.get("feed_url", ""))
    if not source:
        print("Fel: ange feed_url i site.json eller --feed", file=sys.stderr)
        return 2

    print(f"Hämtar flöde: {source}")
    try:
        podcast, episodes = parse_feed(read_feed(source))
    except Exception as exc:  # noqa: BLE001 – tydligt felmeddelande i CI-loggen
        print(f"Fel: kunde inte läsa flödet ({exc})", file=sys.stderr)
        return 1
    if not episodes:
        print("Fel: flödet innehåller inga avsnitt med ljudfil", file=sys.stderr)
        return 1

    out = Path(args.out)
    Site(cfg, podcast, episodes, out, preview=args.sample).build()
    if args.sample:
        shutil.copy(SAMPLE_DIR / "sample.wav", out / "assets" / "sample.wav")
    print(f"Klart: {len(episodes)} avsnitt → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
