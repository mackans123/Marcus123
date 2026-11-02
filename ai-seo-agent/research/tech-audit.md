# Albacross technical SEO / AEO audit

- **Date:** 2026-11-02
- **Agent:** ai-seo-tech-auditor (run 1)
- **Scope:** www.albacross.com (Webflow, served through Cloudflare) plus subdomains app., management., help., test., docs., integrations., career.
- **Raw data:** `ai-seo-agent/research/tech-crawl.csv` has one row per sitemap URL (158 rows). Columns: status, title/meta lengths, canonical, meta robots, H1/H2 counts, word count, JSON-LD types, visible date, internal links, images missing alt, og:image.
- **Method:** sequential curl crawl with a 0.5 s delay. I fetched with 8 bot user agents, queried Ahrefs Site Explorer (top pages, `mode=subdomains`, 2026-11-01) and pulled PostHog `$web_vitals` for the last 30 days, p75, host = www.albacross.com. Nothing was changed in Webflow.

---

## 1. Executive summary

AI crawlers can reach the site. Every AI and search user agent got a 200, and the main content (hero copy, the pricing table and comparison pages) is in the server-rendered HTML. The problems are about **which URLs get indexed and how clearly each page describes itself**:

1. **No page on www has a canonical tag (158 of 158 sitemap URLs).** Body links that carry UTM parameters create duplicate URLs, and Ahrefs shows one of them ranking: `albacross.com/newsroom/what-is-lead-generation/?utm_source=Blog&utm_medium=FurtherReading` (est. 15 visits/mo, top keyword "lead generation"). In Webflow this is a single setting.
2. **App, staging and admin hosts are indexed and rank #1 for the brand name.** `app.albacross.com/account/integration` gets an estimated 126 organic visits/mo for "albacross". That is more than the brand traffic Ahrefs assigns to any app page. `management.`, `app./login`, `app./register`, `app./home` and `test.albacross.com` (a staging copy of the app) are indexed too. None of these hosts serves a real robots.txt: the SPA returns `index.html` with a 200.
3. **The money pages have no `<h1>`.** This covers the homepage, /pricing, /gain-insight, /generate-leads, /auto-engage, /account-based-marketing, /success-stories, /book-a-demo and all 12 customer stories (22 URLs in total). The homepage headline "Your website visitors aren't anonymous. Not to us." is a styled `div`.
4. **The homepage and pricing page have no structured data.** Of 158 URLs, 76 have no JSON-LD. Only the 79 newsroom posts (Article) and 3 of the 6 alternative pages (FAQPage) have any. Nothing on the site declares Organization or SoftwareApplication/Offer, so LLMs have no machine-readable price.
5. **llms.txt contradicts the pricing page.** It gives per-user pricing, "up to 1,000" companies and "from €375/user/month". It also links 4 times to `integrations.albacross.com`, which returns **HTTP 451 (Vercel `DEPLOYMENT_DISABLED`)**, so the whole integrations marketplace is down.

---

## 2. Verified baseline (things already known, re-checked 2026-11-02)

| Check | Result | Evidence |
|---|---|---|
| `www/robots.txt` | 200, text/plain, 46 bytes. The only line is `Sitemap: https://www.albacross.com/sitemap.xml`, so all crawlers are allowed by default. It is served with `x-robots-tag: noindex`, which is Webflow's default and harmless. | `curl` |
| `www/sitemap.xml` | 200, **158 URLs**: 79 /newsroom, 38 root pages, 24 /ebook-chapters, 12 /customer-stories, 5 /ebooks. Content-Type is `application/rss+xml` (should be `application/xml`; minor). | `curl` |
| `www/llms.txt` | 200, 9.4 KB, "Last updated: 2026-09-29" | `curl` |
| Canonical tag | **Missing on 158/158** URLs (homepage, pricing, newsroom and alternative pages included) | crawl CSV `canonical_ok=missing` |
| Meta robots | None on any page, so everything is indexable | crawl CSV |
| JSON-LD on homepage / pricing | **None** | crawl CSV |
| JSON-LD on newsroom posts | `Article` (+ Person author, Organization publisher, ImageObject) on all 79 | crawl CSV |
| JSON-LD on alternative pages | `FAQPage` on /leadfeeder-, /leadinfo-, /snitcher-alternative. **Missing on the newer /6sense-, /clearbit- and /lead-forensics-alternative** (published 2026-10-19) | crawl CSV |
| `app.albacross.com/robots.txt` | 200 **text/html**: the SPA shell (`<title>Albacross</title>`, legacy meta description "Advertise to companies on the web…"). Served from S3/CloudFront. | `curl` |
| `management.albacross.com/robots.txt` | 200 **text/html** (SPA shell "Albacross - Management") | `curl` |
| `help.albacross.com/robots.txt` | 200 text/plain (Intercom). Declares `Sitemap: http://help.albacross.com/sitemap.xml` (**http**) | `curl` |
| App/management indexed | Yes, confirmed in Ahrefs (table in §5) | Ahrefs top-pages |
| UTM URL indexed | Yes: `…/what-is-lead-generation/?utm_source=Blog&utm_medium=FurtherReading`. Also `…/newsroom/b2b-sales?msID=…` | Ahrefs top-pages |
| `/blog` | 404 (and `/blog/` 301 → `/blog` → 404) | `curl` |
| Status codes | All 158 sitemap URLs return 200 with no redirects. Unknown URLs return a real 404 (no soft-404s). Apex and http both 301 to `https://www.` | crawl CSV |

---

## 3. Prioritized issue list

Impact: **H** = affects indexation or how AI and search engines understand the brand or pricing; **M** = ranking, CTR or extraction quality; **L** = hygiene.
Owner: **Web** = Webflow editor or designer; **Eng** = product engineering (AWS/Vercel/Intercom); **PMM** = product marketing; **Content** = content team.

| # | Issue | Affected (count + examples) | Impact | Exact fix steps | Owner | TASKS ID |
|---|---|---|---|---|---|---|
| 1 | **No canonical tags anywhere**, so parameter URLs (UTM, `msID`, Webflow pagination `?bc5c4af0_page=2`) get indexed as duplicates | 158/158 sitemap URLs. Indexed: `/newsroom/what-is-lead-generation/?utm_source=Blog&utm_medium=FurtherReading`, `/newsroom/b2b-sales?msID=9b95…` | **H** | Webflow → **Site settings → SEO → Global canonical tag URL** → enter `https://www.albacross.com` (no trailing slash) → Save → **Publish** to all domains. Webflow then outputs a self-referencing `<link rel="canonical">` on every static and CMS page, with query strings dropped. Check: `curl -s https://www.albacross.com/pricing \| grep canonical`. After that, override the canonical only on deliberate duplicates (Page settings → SEO → Canonical URL). | Web | **2.1** |
| 2 | **App, admin and staging hosts indexed, and they rank for the brand.** No robots.txt (SPA returns HTML), no `noindex` | `app.albacross.com/account/integration` (#1 "albacross", ~126 visits/mo), `app./`, `app./login`, `app./register`, `app./home`, `management.albacross.com/` (#1 "albacross"), **`test.albacross.com/`** (staging, not previously known) | **H** | Not Webflow. For each host (CloudFront distribution in front of the S3 SPA bucket): **(a)** add a CloudFront *Response headers policy* with the custom header `X-Robots-Tag: noindex, nofollow` on all paths (for `app.`, `/login` and `/register` can stay `noindex`). **(b)** Leave robots.txt *allowing* crawl until the URLs drop out (Google can't see `noindex` on a URL that robots.txt blocks). **(c)** Upload a real `robots.txt` object (text/plain) to the bucket root anyway, so `/robots.txt` stops returning HTML. Contents in §7.2, and switch it to `Disallow: /` once the URLs are gone. **(d)** Put `test.albacross.com` behind basic auth / CloudFront signed access, or take it down. **(e)** In GSC (domain property) → Removals → temporarily remove `app.`, `management.` and `test.` URL prefixes. Same in Bing Webmaster Tools → Block URLs. | Eng | **2.2** (+ `test.` is new) |
| 3 | **Body links in newsroom posts hard-code UTM parameters and the non-www host**, which keeps creating the duplicates in #1 and costs 2 redirect hops per click | 6 posts contain **37** links with `?utm_source=Blog&utm_medium=FurtherReading` (worst: `/newsroom/how-a-website-lurker-went-from-…` 9, `/convert-prospects-into-customers` 7, `/b2b-sales` 6, `/b2b-sales-techniques` 6, `/how-to-close-a-sale` 5, `/lead-generation-funnel-infographic` 4). **48 posts** contain **193** links to `https://albacross.com/…/` (chain `albacross.com/x/` → `albacross.com/x` → `www.albacross.com/x`). 2 links use `http://`. | **H** (with #1) | Webflow → **CMS → Newsroom collection** → open each post → in the Rich Text field select each link → link settings → replace it with the clean relative path (e.g. `/newsroom/b2b-sales-techniques`, no trailing slash, no UTM). Save, then publish. The publisher agent can prepare this as CMS **drafts** via API (find `https?://albacross\.com` and `utm_` in the rich text, replace with `/path`), but a human must approve first. Track internal clicks with PostHog autocapture, not with UTMs on internal links. | Content (+ publisher agent drafts) | **2.1**, **2.11** |
| 4 | **Missing `<h1>` on the homepage, pricing, product and customer-story pages**. Headlines are styled `div`s, so search engines and LLM extractors get no primary topic signal | **22 URLs**: `/`, `/pricing`, `/gain-insight`, `/generate-leads`, `/auto-engage`, `/account-based-marketing`, `/success-stories`, `/book-a-demo`, `/zaplify`, `/lead-estimator`, 12 × `/customer-stories/*`. Multiple H1s on 6 URLs (`/offers-linkedin` 3, `/linkedin` 2, 4 newsroom posts 2). Pricing has 0 `<h2>`, and the homepage has only 2. | **H** | Webflow **Designer** → open the page → select the hero headline (homepage: "Your website visitors aren't anonymous. Not to us.") → in the **Element settings** panel (gear icon) set the tag to **H1** (if it is a Text Block/Div, drag in a *Heading* element, set it to H1, give it the same class and move the text). Keep exactly one H1 per page. Pricing: add an H1 such as "Albacross pricing: plans from €59/month", and make the plan names (Starter/Professional/Organisation) H2. Customer-story template (CMS): set the story-title element to H1 once in the template. Newsroom posts with 2 H1s: change the H1 inside the rich text to H2. | Web | **NEW → propose 2.12** |
| 5 | **No Organization / SoftwareApplication schema; homepage and pricing have no JSON-LD** | 76/158 URLs have no JSON-LD (35 root pages, 24 ebook chapters, 12 customer stories, 5 ebooks). Homepage, pricing and product pages have none. | **H** | Webflow → **Pages → Home → Page settings (gear) → Custom code → "Inside `<head>` tag"** → paste the Organization + WebSite block (§8.1). Pricing → Page settings → Custom code → paste the SoftwareApplication block (§8.2). Save → Publish → test at https://search.google.com/test/rich-results and https://validator.schema.org. Keep the prices in sync with `facts.yaml` (the tech auditor checks this weekly, task 7.7). | Web (+ PMM sign-off on prices) | **2.3** |
| 6 | **llms.txt contradicts the pricing page and links to a dead subdomain** | llms.txt: "€59/user/month, up to 100", "€149/user/month, up to 1,000", "Organisation from €375/user/month". Pricing page (2026-11-02): Starter €59/mo (billed yearly, 0–50 and 50–100 companies), Professional €149/mo (0–250 and 251–500), Organisation "Talk to Us" (501–1,000 up to 5,000+, annual only). Monthly billing €84 / €213. **No "per user" anywhere on the pricing page** (that phrase appears only in the competitor-cost comparison block). The 3 new alternative pages are missing from llms.txt. Uses the legacy names Gain Insight / Generate Leads / Auto-Engage. | **H** | Webflow can't serve `llms.txt` from the Designer. Find where it is hosted now (Webflow → Site settings → **Hosting → Upload a file** or a Cloudflare/Worker route [[VERIFY: how llms.txt is deployed]]). Replace the `## Pricing` section with §9, add the 3 alternative pages under `## Comparisons`, fix the integrations links (#7) and bump "Last updated". | PMM + Web | **2.9**, **6.12** |
| 7 | **integrations.albacross.com is down: HTTP 451, `x-vercel-error: DEPLOYMENT_DISABLED`** | `/`, `/listings/salesforce`, `/listings/hubspot-crm`, `/listings/linkedin-matched-audiences`. All 4 are linked from llms.txt, and the integration claims ("30+ native integrations") now point to error pages. | **H** | Vercel → project for integrations.albacross.com → re-enable the deployment / resolve the billing or plan issue. If the marketplace is retired, 301 it to a new `www.albacross.com/integrations` page (Webflow → Site settings → Publishing → 301 redirects can't cover another host, so do the redirect in Vercel/DNS) and update llms.txt. | Eng + PMM | **NEW → propose 2.13** |
| 8 | **Sitemap is stale**: newest posts missing and `lastmod` unreliable | Missing: `/newsroom/automate-sales-plays-albacross-attio-slack` (datePublished 2026-10-30) and `/newsroom/account-based-marketing-examples` (2026-11-02), even though the sitemap was regenerated at 2026-11-02 12:06 GMT. 63 URLs share `lastmod` 2025-02-18 (a migration date, not a real edit date). | M | Webflow → **CMS → Newsroom collection settings → SEO** → confirm "Exclude from sitemap" is **off**. Open each missing item and check that it is *published* (not "staged") → **Publish** the site. Site settings → SEO → **Auto-generate sitemap = On**. After publish, check that both URLs are in `/sitemap.xml`. Then submit the sitemap in GSC and Bing WMT. | Web | **2.6** |
| 9 | **Core Web Vitals**: slow LCP on product pages, CLS on the newsroom index | PostHog p75, 30 days, only pages with ≥100 samples: `/generate-leads` LCP **3.59 s** (235 samples), `/auto-engage` **3.74 s** (178), `/gain-insight` **3.27 s** (112) (all "needs improvement"). `/newsroom` CLS **0.264** (157 samples, "poor"). `/register` CLS 0.132, INP 280 ms. The homepage (LCP 1.62 s, 2,285 samples) and pricing (0.66 s) pass. Low-sample "poor" pages (<10 samples, e.g. `/newsroom/b2b-sales-techniques` 23.9 s, `/engage` INP 1.9 s) are noise until confirmed. | M | `/generate-leads`: hero `product-gl-hero.png` is a 298 KB PNG, and other assets are a 1.42 MB `Image.svg` (raster embedded in SVG), a 739 KB SVG and three 320–430 KB PNGs. In Webflow → **Assets panel** → select each PNG → **Convert to WebP / AVIF** (Webflow "Compress" button), replace the SVG-wrapped rasters with WebP. Set the hero image **Load = Eager** and all below-fold images **Load = Lazy** (Image settings). Do the same for /auto-engage and /gain-insight, which use the same template. `/newsroom` CLS: give the post-card image wrappers a fixed aspect ratio (Designer → class → Size → aspect-ratio or set height) and reserve space for the pagination block. | Web | **2.7** |
| 10 | **No og:image on 79 URLs, homepage included**, so link previews in Slack/LinkedIn and some AI UIs show no image | All 38 root pages, 24 ebook chapters, 12 customer stories, 5 ebooks | M | Page settings → **Open Graph settings → Open Graph image URL / Upload** for each static page (start with Home, Pricing, the 6 alternative pages, the product pages). CMS templates (customer stories, ebooks, ebook chapters): Collection page settings → Open Graph image → bind to the main image field. | Web | **NEW → propose 2.14** |
| 11 | **FAQPage schema missing on the 3 newest alternative pages**, and no "Last updated" date on any alternative page | `/6sense-alternative`, `/clearbit-alternative`, `/lead-forensics-alternative` (no JSON-LD). A visible "Last updated" date appears on 0 of 6 alternative pages, which the blueprint requires. | M | Copy the FAQPage `<script type="application/ld+json">` pattern from `/leadfeeder-alternative` → Page settings → Custom code → paste into each page, rewriting the Q&As to match that page's visible FAQ. Add a "Last updated: 2 November 2026" text element under the H1 (template or symbol). | Web + Content | **2.3**, WS4 blueprint |
| 12 | **Legacy and duplicate product pages compete with each other**, which confuses entity understanding | `/gain-insight` vs `/identify`, `/generate-leads` vs `/signal`, `/auto-engage` vs `/engage` are all live and all in the sitemap. The legacy ones get **more** traffic (PostHog LCP samples 235 vs 17 for generate-leads vs signal) and are the ones llms.txt links to. Thin/orphan pages in the sitemap: `/get-started` (42 words), `/lead-estimator` (10 words), `/offers-linkedin` (3 H1s, campaign page), `/zaplify` (5 internal links). | M | PMM decision (one URL per module). Then Webflow → **Site settings → Publishing → 301 redirects**: `/gain-insight` → `/identify`, `/generate-leads` → `/signal`, `/auto-engage` → `/engage` (or the reverse). Update the nav, llms.txt and internal links. For campaign/utility pages (`/get-started`, `/lead-estimator`, `/offers-linkedin`, `/register`, `/book-a-demo`): Page settings → SEO → **Sitemap indexing off** and add `<meta name="robots" content="noindex">` under Custom code (keep `/book-a-demo` indexable if it gets brand searches). | PMM → Web | **6.12**, **5.1** |
| 13 | **`/blog` returns 404** | `/blog`, `/blog/` (301 → 404). Buyers and LLMs guess `/blog`. | M | Webflow → Site settings → **Publishing → 301 redirects**: add `/blog` → `/newsroom` and `/blog/(.*)` → `/newsroom/%1` [[VERIFY: legacy /blog slugs match current /newsroom slugs before adding the wildcard; otherwise send everything to /newsroom]]. Superseded if 2.10 moves the hub to /blog. | Web | **2.10** |
| 14 | **No explicit AI-crawler policy in robots.txt.** Access works today, but by default only | All bots got 200 + full content (table §6). Cloudflare sits in front (Webflow-managed), and the test came from non-verified IPs, so Cloudflare "verified bot" rules (AI Crawl Control) couldn't be exercised | M | Webflow → **Site settings → SEO → Robots.txt** → paste §7.1 → Save → Publish. Confirm with Bing WMT URL Inspection ("Live test") and GSC URL Inspection. Webflow manages the Cloudflare zone, so ask Webflow support whether any bot-blocking is applied to `www.albacross.com` [[VERIFY]]. | Web | **2.4** |
| 15 | **Help centre: first redirect hop goes to `http://`**, and the help sitemap declares http | `https://help.albacross.com/` → 302 `http://help.albacross.com/en/` → https. Ahrefs indexes `http://help.albacross.com/en/...` URLs (e.g. NACE codes article, pos. 5). | L–M | Intercom → Settings → Help Center → **Custom domain** → enable/repair SSL ("Use HTTPS"), then check that the redirect and sitemap use https. | Eng/Support | NEW → propose 2.15 |
| 16 | **Article schema is double-escaped**: `&amp;` appears literally in the JSON-LD `headline` | e.g. `/newsroom/albacross-gdpr` headline "Albacross &amp; GDPR: Everything you need to know". Affects every post with "&" in the title. | L | Webflow CMS template custom code inserts HTML-escaped field values. Either replace "&" with "and" in those post names, or add a plain-text "Schema headline" CMS field without special characters and bind it in the template's JSON-LD. | Web | **2.3** |
| 17 | **Key trust page is stale**: GDPR article `dateModified` 2024-12-30 | `/newsroom/albacross-gdpr` (linked from llms.txt and facts.yaml as *the* GDPR page) | M (for AEO on GDPR prompts) | Content refresh with legal (EU data hosting, DPA, legitimate interest wording per facts.yaml [[VERIFY with legal]]). Then update the CMS "Updated" date so `dateModified` and the visible date change. | Content + Legal | **5.1** |
| 18 | **Title / meta length hygiene** | 92 titles > 60 chars (52 of them newsroom); 9 titles < 30 chars (`/pricing` = "Pricing — Albacross", 19 chars); 53 meta descriptions > 160; 4 missing (`/privacy-policy`, `/terms-of-service`, `/cookie-policy`, `/newsroom/lead-generation-to-revenue-acceleration`); duplicate title "What is Albacross? \| Albacross Ebooks" on 2 ebook chapters | L–M | Page settings → SEO settings → Title tag / Meta description. Priority: `/pricing` title → "Albacross Pricing: Plans from €59/month, 14-Day Free Trial" (56). CMS templates: change the title formula so it doesn't add " \| Albacross" when the name is already long. | Web + Content | **5.1** |
| 19 | **Image alt text** | 4,930 of 5,555 `<img>` lack alt (many are decorative icons/logos repeated in the nav/footer symbols) | L | Designer → select each meaningful image (product screenshots, customer logos) → Image settings → Alt text. Decorative icons: tick "Decorative" so Webflow outputs `alt=""` intentionally. Fix the nav/footer **symbols** first, since that cleans up every page at once. | Web | **2.7** |
| 20 | **No IndexNow** | Site-wide | M | Webflow doesn't ping IndexNow natively. Use a Webflow site-publish webhook → small function (or Make/Zapier) that POSTs changed URLs to `https://api.indexnow.org/indexnow` with a key file. Hosting the key file needs Webflow Hosting → *upload file* or a Cloudflare Worker [[VERIFY: what's available on this Webflow plan]]. | Eng | **2.5** |

### Things that are fine (no action)
- **Server-rendered content (2.8).** The homepage hero, the full pricing table (€59, €149, "Talk to Us", the credit price tables) and the alternative-page FAQs are all in the raw HTML. Pricing is not hidden in JS tabs.
- **No accidental noindex** on www. No soft-404s. All sitemap URLs return 200 with no redirect chains. `lang="en"` is set everywhere.
- **Response times:** every sitemap URL responded in under 1.5 s total (from a US East test box).
- **`docs.albacross.com`** (API docs) has a permissive robots.txt and `index, follow`, which is reasonable for a public API reference.
- **`career.albacross.com`** (Teamtailor) has `Content-Signal: search=yes, ai-train=no, ai-input=yes`. That is the vendor default, fine for a careers site.

---

## 4. Crawl statistics (from `tech-crawl.csv`)

| Metric | Value |
|---|---|
| URLs crawled | 158 (all 200) |
| Canonical present | 0 |
| H1 = 1 / 0 / >1 | 130 / 22 / 6 |
| JSON-LD: Article / FAQPage / none | 79 / 3 / 76 |
| og:image present | 79 (newsroom only) |
| Visible publish date | 85 pages (mostly newsroom, 78/79 posts) |
| Visible "Updated/Last updated" label | 1 page |
| Median newsroom word count | ~1,800 |
| Thin (<300 words) | `/get-started` 42, `/lead-estimator` 10, `/book-a-demo` 101, `/register` 148 |
| Sitemap `lastmod` = 2025-02-18 | 63 URLs |

---

## 5. Indexation risk (Ahrefs Site Explorer, top pages, 2026-11-01, mode=subdomains)

Estimated monthly organic traffic. These are pages outside www, or parameter URLs, that rank.

| URL | Est. traffic | Top keyword (pos.) | Should be indexed? |
|---|---|---|---|
| https://app.albacross.com/account/integration | 126 | albacross (1) | **No** |
| https://career.albacross.com/ | 27 | albacross (1) | Yes |
| https://management.albacross.com/ | 26 | albacross (1) | **No** |
| https://app.albacross.com/ | 25 | albacross (1) | **No** (`/login` is acceptable as a sitelink, but it should be a noindexed SPA) |
| https://albacross.com/newsroom/what-is-lead-generation/?utm_source=Blog&utm_medium=FurtherReading | 15 | lead generation (1) | **No**, should consolidate into the clean URL |
| http://help.albacross.com/en/articles/1279784-nace-codes-full-list | 2 | what is nace (5) | Yes, but via https |
| http://help.albacross.com/en/ | 2 | albacross pricing (7) | Yes, via https |
| https://app.albacross.com/login, /register, /home | 1 / 1 / 0 | albacross / albacross pricing | **No** |
| https://test.albacross.com/ | 0 | albacross (3) | **No (staging)** |
| https://albacross.com/newsroom/b2b-sales?msID=9b956bee-… | 0 | albacross (3) | **No** |
| https://docs.albacross.com/ | 0 | albacross (10) | Yes |

Takeaway: about 180 estimated brand visits/mo go to app/admin/staging hosts that show a login wall and the legacy description "Advertise to companies on the web and track their behaviour…". LLMs that retrieve brand SERPs see that old positioning.

---

## 6. AI-crawler fetch test (2026-11-02)

Each page was fetched with each UA string from a non-verified IP. "Content" means a page-specific marker was found in the raw HTML (homepage hero "Not to us", pricing "€149", "Leadfeeder", "GDPR").

| User agent | `/` | `/pricing` | `/leadfeeder-alternative` | `/newsroom/albacross-gdpr` |
|---|---|---|---|---|
| GPTBot | 200 ✓ content | 200 ✓ | 200 ✓ | 200 ✓ |
| OAI-SearchBot | 200 ✓ | 200 ✓ | 200 ✓ | 200 ✓ |
| ChatGPT-User | 200 ✓ | 200 ✓ | 200 ✓ | 200 ✓ |
| ClaudeBot | 200 ✓ | 200 ✓ | 200 ✓ | 200 ✓ |
| Claude-SearchBot | 200 ✓ | 200 ✓ | 200 ✓ | 200 ✓ |
| PerplexityBot | 200 ✓ | 200 ✓ | 200 ✓ | 200 ✓ |
| Bingbot | 200 ✓ | 200 ✓ | 200 ✓ | 200 ✓ |
| Googlebot | 200 ✓ | 200 ✓ | 200 ✓ | 200 ✓ |

No `cf-mitigated` challenge header appeared. Identical byte sizes across UAs mean there is no UA-based cloaking. Caveat: Cloudflare can treat *verified* bot IPs differently, so the definitive check is Bing WMT / GSC live URL inspection plus Cloudflare/Webflow bot settings (#14).

---

## 7. Ready-to-paste robots.txt

### 7.1 www.albacross.com (Webflow → Site settings → SEO → Robots.txt)

```txt
# robots.txt for www.albacross.com (proposal 2026-11-02, TASKS 2.4)
# NOTE: a crawler that matches a named group ignores the "*" group.
# If you ever add a Disallow, repeat it in every group.

# Search engines and AI answer/search agents: allowed
User-agent: Googlebot
User-agent: Bingbot
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Applebot
User-agent: DuckAssistBot
Allow: /

# AI model-training crawlers: allowed (recommendation; needs an owner decision)
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: CCBot
User-agent: meta-externalagent
Allow: /

# Everyone else
User-agent: *
Allow: /

Sitemap: https://www.albacross.com/sitemap.xml
```

Parameter URLs are deliberately **not** blocked in robots.txt. Crawlers have to be able to fetch them to see the canonical tag added in #1.

### 7.2 app. / management. / test.albacross.com (Eng: upload a text/plain `robots.txt` object to each bucket root)

Phase 1 (now, together with the `X-Robots-Tag: noindex, nofollow` response header), so crawlers can still see the noindex:
```txt
User-agent: *
Allow: /
```
Phase 2 (after GSC shows the URLs removed, about 4–8 weeks):
```txt
User-agent: *
Disallow: /
```

---

## 8. JSON-LD snippets (prices from `facts.yaml`, checked against /pricing 2026-11-02)

### 8.1 Organization + WebSite: Homepage → Page settings → Custom code → Inside `<head>` tag

The `description` is the positioning one-liner, word for word (`positioning.md`). In `sameAs`, LinkedIn, X/Twitter, Facebook and G2 are taken from the live homepage footer. Add Capterra, YouTube, Crunchbase and Wikidata once you have the URLs [[VERIFY: profile URLs]]. Replace the logo with a ≥512 px raster PNG/WebP logo (the current schema logo is an SVG, which Google doesn't accept for logos) [[VERIFY: logo asset URL]].

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://www.albacross.com/#organization",
      "name": "Albacross",
      "legalName": "Albacross Nordic AB",
      "url": "https://www.albacross.com",
      "logo": "https://cdn.prod.website-files.com/67336b6d03d7829a16579243/677e35932a231ffa0db0ee35_ms-icon-310x310.png",
      "description": "Albacross is a European B2B website visitor identification and intent platform that shows which companies visit your site and helps you engage them, GDPR-first.",
      "foundingDate": "2014",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Stockholm",
        "addressCountry": "SE"
      },
      "sameAs": [
        "https://www.linkedin.com/company/albacross/",
        "https://twitter.com/albacrossnordic",
        "https://www.facebook.com/albacrossnordic/",
        "https://www.g2.com/products/albacross/reviews"
      ]
    },
    {
      "@type": "WebSite",
      "@id": "https://www.albacross.com/#website",
      "url": "https://www.albacross.com",
      "name": "Albacross",
      "publisher": { "@id": "https://www.albacross.com/#organization" },
      "inLanguage": "en"
    }
  ]
}
</script>
```

### 8.2 SoftwareApplication with offers: Pricing → Page settings → Custom code → Inside `<head>` tag

Organisation ("Talk to us") is left out of `offers` because an Offer without a price fails rich-result validation. The prices are the lowest tier of each plan, billed yearly.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "@id": "https://www.albacross.com/#software",
  "name": "Albacross",
  "url": "https://www.albacross.com",
  "applicationCategory": "BusinessApplication",
  "applicationSubCategory": "B2B website visitor identification and intent data platform",
  "operatingSystem": "Web",
  "description": "Albacross identifies the companies visiting your website, without forms or cookies on individual people. It scores them by fit and buying intent (on-site behaviour plus Bombora research signals) and pushes hot accounts to your CRM, Slack or Teams. It can also start AI-personalised email and LinkedIn outreach to the right decision-makers. Built in Stockholm for GDPR, with published pricing from €59/month.",
  "publisher": { "@id": "https://www.albacross.com/#organization" },
  "offers": [
    {
      "@type": "Offer",
      "name": "Starter",
      "url": "https://www.albacross.com/pricing",
      "price": "59",
      "priceCurrency": "EUR",
      "priceSpecification": {
        "@type": "UnitPriceSpecification",
        "price": "59",
        "priceCurrency": "EUR",
        "unitText": "month",
        "billingDuration": "P1Y",
        "description": "From €59/month billed yearly (€84/month billed monthly). 0–100 identified companies per month; 10 verified email + 5 verified phone credits included."
      },
      "eligibleDuration": { "@type": "QuantitativeValue", "value": 14, "unitCode": "DAY" },
      "availability": "https://schema.org/InStock"
    },
    {
      "@type": "Offer",
      "name": "Professional",
      "url": "https://www.albacross.com/pricing",
      "price": "149",
      "priceCurrency": "EUR",
      "priceSpecification": {
        "@type": "UnitPriceSpecification",
        "price": "149",
        "priceCurrency": "EUR",
        "unitText": "month",
        "billingDuration": "P1Y",
        "description": "From €149/month billed yearly (€213/month billed monthly). 0–500 identified companies per month; 25 verified email + 10 verified phone credits included; HubSpot and LinkedIn Ads integrations."
      },
      "availability": "https://schema.org/InStock"
    }
  ]
}
</script>
```
Notes: the `eligibleDuration` on Starter stands for the 14-day free trial, but schema.org has no clean "free trial" property, so drop it if the validator warns. Don't add `aggregateRating` unless the rating is shown on the page and sourced (CONVENTIONS rule 2).

---

## 9. Proposed llms.txt `## Pricing` section (replaces the current one)

This corrects the `site_inconsistencies` in `facts.yaml`. The current section says "€59/user/month, up to 100", "€149/user/month, up to 1,000" and "Organisation from €375/user/month". The live pricing page shows no per-user wording, Professional tops out at 500 identified companies, and Organisation is "Talk to us".

```markdown
## Pricing

Current prices are always listed at https://www.albacross.com/pricing (last checked: 2026-11-02).
Prices below are per month, billed yearly. Annual billing saves 30% compared with monthly billing.

- **Starter**: from €59/month billed yearly (€84/month billed monthly). 0–100 identified companies per month. Includes 10 verified email and 5 verified phone credits, AI email and LinkedIn sequences, Slack, Microsoft Teams and Pipedrive integrations.
- **Professional**: from €149/month billed yearly (€213/month billed monthly). 0–500 identified companies per month. Includes 25 verified email and 10 verified phone credits, unlimited sequences, HubSpot, LinkedIn Ads and Google Sheets integrations, CSV export and priority support.
- **Organisation**: custom pricing (talk to sales), annual billing only. 500 to 5,000+ identified companies per month.
- **Extra credits**: verified email and phone credits can be added monthly or as annual bundles.
- **Free trial**: 14 days, no credit card required.
```

Also in llms.txt:
- Add under `## Comparisons`: `/6sense-alternative`, `/clearbit-alternative`, `/lead-forensics-alternative`.
- Rename the product sections to the site navigation, keeping the legacy names in brackets: "Identify (formerly Gain Insight)", "Signal (formerly Generate Leads)", "Automate", "Engage (formerly Auto-Engage™)". Point the links at whichever URLs survive issue #12.
- Fix or remove the 4 `integrations.albacross.com` links (issue #7).
- Replace the intro with the positioning short description, word for word.
- Bump `Last updated:`.

**Discrepancies to resolve in other agent files:**
- `research/llms-txt-pricing-fix.md` says "monthly billing costs 30% more". The page says annual **saves 30%**, which means monthly costs about 43% more (€84 vs €59, €213 vs €149). Use the wording above.
- `facts.yaml → pricing.plans[Organisation].identified_companies` says "501–1,000 / 1,000–2,000+". The page now lists tiers up to **5,000+**, and the monthly prices (€84 / €213) aren't in facts.yaml yet. PMM should update facts.yaml.
- `facts.yaml → pricing.per_user` [[VERIFY]] is still open. The pricing page doesn't say per user. Until PMM confirms, llms.txt should not say "per user".

---

## 10. Needs human action / open questions

1. **Web (Webflow, ~1 hour):** #1 global canonical, #14 robots.txt, #5 JSON-LD, #13 /blog redirect, #8 sitemap check, then publish. These are the highest-ROI changes and need no engineering.
2. **Eng:** #2 noindex headers and robots.txt on app./management./test. (plus GSC Removals). #7 the integrations site is down (Vercel `DEPLOYMENT_DISABLED`). #15 help-centre https.
3. **PMM:** approve the §9 llms.txt pricing text and the §8 offer prices. Decide on legacy vs new product URLs (#12). Update facts.yaml (Organisation tiers, monthly prices, per-user).
4. **Content:** clean up the 37 UTM links and 193 non-www links in newsroom rich text (#3). The publisher agent can prepare drafts after approval. Also the GDPR page refresh (#17).
5. **Open:** How is `llms.txt` deployed on Webflow (hosted file vs Worker)? Who owns the Cloudflare/bot settings for the Webflow-hosted zone? Is `test.albacross.com` still needed?

Re-check cadence: the weekly tech-auditor run (TASKS 7.7) should re-run `crawl.py` and confirm that canonical is present on 158/158, the app hosts send `X-Robots-Tag`, integrations returns 200, the sitemap contains every newsroom post, and the JSON-LD prices match facts.yaml.
