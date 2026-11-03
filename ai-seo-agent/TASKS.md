# Albacross AI SEO: full task breakdown

**Legend**
- **Who**
  - 🤖 = the agent can do it end to end
  - 🤖➜👤 = the agent drafts and a human approves or publishes
  - 👤 = human only (access, relationships, decisions)
- **Priority:** P0 = blocking or this week · P1 = core 90-day work · P2 = after the core is live · P3 = later or optional
- **Effort:** S < ½ day · M 1–3 days · L 1–2 weeks

The sequence follows the 90-day roadmap: **Weeks 1–2** foundations → **Weeks 3–4** quick wins → **Month 2** new content → **Month 3** authority and compounding.

---

## WS0: Ownership & setup (week 1)

| ID | Task | Who | Pri | Effort | Done when |
|---|---|---|---|---|---|
| 0.1 | Name an owner for the program (marketing) and approvers for content (PMM) and technical changes (web) | 👤 | P0 | S | Owners named in the doc |
| 0.2 | Agree the KPIs and targets in README §4 with RevOps, including how "AI-influenced pipeline" is defined | 👤 | P0 | S | Targets signed off |
| 0.3 | Create `facts.yaml`, the approved single source of truth: pricing tiers, customer count, integrations, data coverage by country, GDPR stance, company-level vs person-level, Bombora partnership, free trial terms | 🤖➜👤 | P0 | S | PMM-approved file in repo |
| 0.4 | Set up a Trello board "AI SEO" with the lists Backlog / This week / Drafted by agent / In review / Published / Measuring | 🤖 | P1 | S | Board exists; tasks below imported |
| 0.5 | Confirm budget for tools: Ahrefs Brand Radar add-on (or Peec AI / Profound / Otterly), Listen Notes, possibly freelance video | 👤 | P0 | S | Tool chosen |

## WS1: Measurement (weeks 1–2)

| ID | Task | Who | Pri | Effort | Done when |
|---|---|---|---|---|---|
| 1.1 | Turn on AI prompt tracking for the 40 prompts in `money-prompts.csv` across ChatGPT, Perplexity, AI Overviews, AI Mode, Gemini, Copilot and Claude. Competitors: Leadfeeder, RB2B, Warmly, Snitcher, Leadinfo, Lead Forensics, 6sense, Clearbit/HubSpot, Factors, Vector | 👤 buy, 🤖 configure | P0 | S | First baseline snapshot saved to `state/` |
| 1.2 | Record the **baseline**: share of voice per prompt per engine, the cited URLs, how Albacross is described (sentiment and accuracy), and where wrong facts appear (e.g. price) | 🤖 | P0 | M | `state/visibility-baseline.json` + summary |
| 1.3 | Add an "AI Assistants" channel in PostHog (and GA4 if used): referrer regex `chatgpt\.com\|chat\.openai\.com\|perplexity\.ai\|claude\.ai\|gemini\.google\.com\|copilot\.microsoft\.com\|edgeservices\|grok\.com\|meta\.ai\|deepseek\.com` **OR** `utm_source` matching the same list | 🤖➜👤 | P0 | S | Saved insight or dashboard |
| 1.4 | Build a PostHog dashboard with four views: AI sessions by engine, AI landing pages, AI session → signup/demo conversion, and branded vs non-branded organic | 🤖 | P1 | S | Dashboard live |
| 1.5 | Add a free-text **"How did you hear about us?"** field to register, book-a-demo and get-started forms (Webflow) and send it to Attio | 👤 (web) | P0 | S | Field live and syncing to CRM |
| 1.6 | Have sales ask about the discovery route on first calls and log it in an Attio attribute ("Discovery source: AI / Search / Peer / …") | 👤 | P1 | S | Attribute exists and is used |
| 1.7 | Connect GSC and **Bing Webmaster Tools**, turn on the BWT **AI Performance** report, and connect GSC to Ahrefs | 👤 | P0 | S | Both verified |
| 1.8 | Set up an Ahrefs Rank Tracker project with all keywords in `money-keywords.csv` for US, UK, DE, SE, NL and FR | 🤖 | P1 | S | Project tracking |
| 1.9 | Send a weekly automated report (agent): SoV change, new or lost citations, rank movers, AI sessions, self-reported AI attributions, what shipped | 🤖 | P1 | M | Report arrives every Monday |

## WS2: Technical foundation (weeks 1–3)

| ID | Task | Who | Pri | Effort | Done when |
|---|---|---|---|---|---|
| 2.1 | Add **self-referencing canonical tags** to every page (Webflow page settings / CMS template); make sure UTM-tagged URLs canonicalise to the clean URL | 🤖➜👤 | P0 | S | No indexed `?utm_` URLs after recrawl |
| 2.2 | **Noindex / robots-block the app subdomains** (`app.`, `management.`): serve a robots.txt there and add `X-Robots-Tag: noindex` on app pages | 👤 (eng) | P0 | S | App URLs drop out of the index |
| 2.3 | Add **Organization** (with `sameAs` for LinkedIn, G2, Capterra, YouTube, Crunchbase, Wikidata) and **SoftwareApplication/Product** schema with `offers` (pricing) on the home and pricing pages; Article + author Person schema on all newsroom posts | 🤖➜👤 | P1 | S | Passes the Rich Results test |
| 2.4 | Set robots.txt rules explicitly: **allow** OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User, Bingbot and Googlebot; make a deliberate decision on GPTBot, ClaudeBot and Google-Extended (recommend allow). Check Cloudflare/CDN bot settings | 🤖➜👤 | P0 | S | Explicit rules live; bot fetch test passes |
| 2.5 | Turn on **IndexNow** (Webflow integration or Cloudflare) so Bing, which feeds ChatGPT and Copilot, picks up updates fast | 👤 | P1 | S | Pings logged |
| 2.6 | Fix the sitemap: include all newsroom posts and new listicle and comparison URLs, with accurate `lastmod` | 🤖➜👤 | P1 | S | Sitemap validated in GSC + BWT |
| 2.7 | Run Core Web Vitals checks on key templates (home, pricing, alternative pages, newsroom) and compress heavy images and video | 🤖 audit, 👤 fix | P1 | M | CWV pass in PostHog web vitals / GSC |
| 2.8 | Make sure critical content (pricing tables, comparison tables, FAQs) sits in the **server-rendered HTML** and not in JS tabs or embeds | 🤖 audit | P1 | S | Text visible in raw HTML fetch |
| 2.9 | Make `llms.txt` a living file: the agent updates it from `facts.yaml` monthly and adds links to new listicle and comparison pages | 🤖 | P3 | S | Auto-updated |
| 2.10 | ⛔ ON HOLD (URL change, needs SEO team sign-off): Decide the content hub URL: either move `/newsroom` to `/blog` (with 301s) or keep it and create `/compare/` and `/best/` sections | 👤 | P1 | S | Decision + URL structure doc |
| 2.11 | Internal linking: ensure each money page has 5+ relevant internal links in and out (home → listicles, alternatives ↔ listicle, integrations ↔ use cases) | 🤖➜👤 | P1 | M | Link map in repo |

## WS3: Customer research & positioning (weeks 1–3)

| ID | Task | Who | Pri | Effort | Done when |
|---|---|---|---|---|---|
| 3.1 | Mine the **last 90 days of Attio call recordings, notes and emails** for pains, the buyer's own words, winning criteria, competitors evaluated and switch-away reasons | 🤖 | P0 | M | `voc.md` v1 |
| 3.2 | Mine **Intercom conversations** for objections, accuracy and coverage questions, integration questions and FAQ follow-up chains | 🤖 | P1 | M | `voc.md` FAQ section |
| 3.3 | Fill in the **Money Keyword Matrix**: (1) solution terms, (2) best-fit industries *from CRM won-deal data*, (3) competitors + switch reason, (4) jobs to be done, (5) integrations | 🤖➜👤 | P0 | M | `keyword-matrix.md` approved |
| 3.4 | Write the **positioning statement for AI**: who Albacross is for (EU/GDPR-sensitive B2B, SMB → mid-market), who it is *not* for (US person-level), and its differentiators (intent + Bombora, Auto-Engage, ABM ads, published pricing). Use it verbatim on site and off site | 🤖➜👤 | P0 | S | Approved 100-word block |
| 3.5 | Build the competitor sheet: for each competitor, pricing, positioning, where they beat Albacross and where Albacross wins, and **accurate** claims with sources | 🤖➜👤 | P1 | M | `competitors.md` |
| 3.6 | Build **original data assets** that AI loves to cite, e.g. "B2B website visitor identification rates by country 2026" or "What % of B2B traffic is identifiable in Europe vs US", from Albacross's 3B+ monthly events | 👤 data + 🤖 write | P1 | L | Published report page + summary stats |
| 3.7 | Collect quotable proof: 10+ customer quotes, 3 video testimonials, and before/after metrics from case studies | 👤 | P1 | M | Asset library |

## WS4: New money pages (weeks 3–8): the main lever

Each page follows the **Listicle Blueprint**:
- money keyword in the URL and H1
- author and date
- sticky CTA and table of contents
- a TL;DR summary
- a mini comparison table with Albacross #1 and a clear "who it's for" (stated honestly)
- why look for alternatives (from VOC)
- social proof
- the full list with pros, cons, pricing and fair competitor writeups
- a full comparison table
- a page-specific FAQ from real calls
- 5+ internal links
- YouTube embed where possible

| ID | Page (target keyword · US vol · KD) | Type | Who | Pri | Effort |
|---|---|---|---|---|---|
| 4.1 | **Best website visitor identification software 2026** (website visitor identification 700 · KD 5; …software 400 · KD 6; …tracking software 500 · KD 5) | Listicle | 🤖➜👤 | P0 | M |
| 4.2 | **Leadfeeder alternatives**: 12 tools compared (700 + 600 · KD 0), also covering "Dealfront alternatives" (90) | Listicle | 🤖➜👤 | P0 | M |
| 4.3 | **RB2B alternatives** (200), with an angle on GDPR and EU-compliant alternatives to person-level ID | Listicle | 🤖➜👤 | P0 | M |
| 4.4 | **Clearbit Reveal alternatives** after the HubSpot acquisition (250 · KD 0) | Listicle | 🤖➜👤 | P1 | M |
| 4.5 | **Albacross alternatives** (100): own the narrative on your own brand query with an honest page ("when Albacross isn't the right fit") | Defensive listicle | 🤖➜👤 | P0 | M |
| 4.6 | Lead Forensics alternatives (90), 6sense alternatives (150), Leadinfo alternatives (150), Warmly alternatives (60), Snitcher alternatives (20) | Listicles | 🤖➜👤 | P1 | M each |
| 4.7 | **Upgrade the six 1:1 "X-alternative" pages** into "Albacross vs X (2026)" comparison pages: feature table, pricing, GDPR, accuracy, migration steps, FAQ, video. Keep URLs (or 301 to `/compare/x-vs-albacross`) | Comparison | 🤖➜👤 | P0 | M each |
| 4.8 | New head-to-heads: Albacross vs RB2B, vs Warmly, vs Dealfront/Leadfeeder (already exists, deepen it), vs Vector | Comparison | 🤖➜👤 | P1 | M each |
| 4.9 | **Best intent data providers / tools** (b2b intent data providers 250 · KD 16 · TP 700; intent data tools 100) | Listicle | 🤖➜👤 | P1 | M |
| 4.10 | **Best account-based marketing tools for SMB** (600 · KD 11 · TP 1,100) | Listicle | 🤖➜👤 | P2 | M |
| 4.11 | **Anonymous visitor identification** landing page (450 · KD 3) + "How to identify companies visiting your website (GDPR-safe)" how-to (identify website visitors 600 · KD 3) | Landing + how-to | 🤖➜👤 | P0 | M |
| 4.12 | **GDPR & visitor identification** hub: "Is website visitor identification legal in the EU?", company-level vs person-level, DPA, legitimate interest. This is the moat topic | Pillar | 🤖➜👤 + legal review | P0 | M |
| 4.13 | Integration pages: HubSpot, Salesforce, Pipedrive, Slack, Teams, LinkedIn Matched Audiences. Each covers "how to see website visitor companies in X", showing the manual way vs the Albacross way | Integration | 🤖➜👤 | P1 | S each |
| 4.14 | Industry/ICP pages for the top 3–5 verticals from 3.3 (e.g. "visitor identification for SaaS / agencies / manufacturing / IT services") | ICP pages | 🤖➜👤 | P2 | S each |
| 4.15 | Regional pages: best visitor identification for **DACH, Nordics, Benelux, UK, France**, localized where the market justifies it (DE/SV/NL/FR) | Listicle / landing | 🤖➜👤 | P2 | M |
| 4.16 | API pages: "Best IP-to-company APIs" listicle (ip to company api 100) + deepen `/ip-to-company-api` (docs, sample response, pricing, rate limits) | Listicle + landing | 🤖➜👤 | P2 | M |
| 4.17 | Competitor pricing explainers: "Leadfeeder pricing 2026" (200 · KD 0), "RB2B pricing" (350 · KD 2), "Lead Forensics pricing". Factual, dated, and Albacross compared alongside | Info/commercial | 🤖➜👤 | P2 | S each |
| 4.18 | **Rework the homepage and pricing page** with the Landing Page Blueprint: clear category H1, positioning block, logos linking to case studies, pricing visible, problem → solution, video, page FAQ (the homepage has only 2 H2s today) | Landing | 🤖 draft, 👤 design | P1 | L |

**Cadence:** 2–3 pages/week. The weeks 3–8 queue is 4.1, 4.2, 4.5, 4.7, 4.11, 4.12, 4.3, then the rest by score.

## WS5: Refresh existing content (weeks 3–6, then every 90 days)

| ID | Task | Who | Pri | Effort |
|---|---|---|---|---|
| 5.1 | Pull every newsroom and ebook URL with Ahrefs/GSC data (impressions, position, clicks, conversions) and classify each as **refresh / merge / redirect / noindex** | 🤖 | P0 | S |
| 5.2 | Refresh the quick-win pages ranking #4–#15 with commercial intent: `/newsroom/website-visitor-tracking` (#5 for "identify website visitors"), `/newsroom/how-to-identify-website-visitors` (#5 for "b2b website visitor identification"), `/newsroom/b2b-buying-signals` (#10), `/newsroom/using-intent-data-for-b2b-marketing`, `/newsroom/reverse-ip-lookup`. For each: add a TL;DR, a mini shortlist with Albacross, a comparison table, VOC FAQs, an updated date and author, and internal links to the new listicles | 🤖➜👤 | P0 | M |
| 5.3 | ⛔ ON HOLD (URL change, needs SEO team sign-off): Consolidate cannibalising posts, e.g. "website-visitor-tracking" and "how-to-identify-website-visitors" compete for the same intent: merge them and 301 | 🤖➜👤 | P1 | S |
| 5.4 | Replace generic copied FAQ blocks with page-specific conversation-tree FAQs (from 3.2 and AlsoAsked) | 🤖➜👤 | P1 | M |
| 5.5 | ⛔ ON HOLD (URL change, needs SEO team sign-off): Prune or redirect thin and obsolete newsroom posts (old company news, non-ICP topics) | 🤖➜👤 | P2 | S |
| 5.6 | Add GEO-style enrichments to all money pages: Albacross statistics, quotable expert/customer quotes, cited external sources (Princeton GEO: +28–43% visibility) | 🤖➜👤 | P1 | M |
| 5.7 | Set up a **90-day refresh rotation**: the agent flags any money page older than 90 days or losing rank or citations, and writes a refresh brief | 🤖 | P1 | S |

## WS6: Off-page, brand mentions & citations (weeks 4–12, ongoing)

| ID | Task | Who | Pri | Effort |
|---|---|---|---|---|
| 6.1 | Build the **target placement list** from AI-cited URLs (from 1.2) and Google top 10 for every money keyword: listicles, roundups, review sites, Reddit threads, YouTube videos. Score each by citation frequency and whether Albacross is present, and at what rank | 🤖 | P0 | M |
| 6.2 | **Fix wrong facts about Albacross** on third-party pages (e.g. RB2B lists €99 vs €79; "company-level only" framing without the Auto-Engage contacts feature). Send polite correction requests with the correct facts from `facts.yaml` | 🤖 draft, 👤 send | P0 | S |
| 6.3 | **Get added to listicles that miss Albacross** (Bitscale, Prospeo "RB2B alternatives", getbreakout, knock-ai, aisdr, syncgtm, Cognism, instantly). Use LinkedIn + Loom outreach and offer a swap, data or a write-up | 🤖 research+draft, 👤 send | P0 | ongoing |
| 6.4 | **Move up in listicles that include Albacross mid-list** (11x, Factors, StackReaction, …). Offer fresh data, screenshots, a customer quote, an updated pricing block | 🤖➜👤 | P1 | ongoing |
| 6.5 | **Review sites**: refresh G2, Capterra, GetApp, Software Advice, TrustRadius and Gartner Peer Insights profiles (same positioning text, category, pricing, screenshots). Run a customer review campaign; GetApp/Capterra are heavily cited in ChatGPT review answers | 👤 (+🤖 copy) | P0 | M |
| 6.6 | **Reddit**: find threads cited for category prompts (r/sales, r/b2bmarketing, r/SaaS, r/marketing, r/Wordpress "Leadfeeder alternatives"). Employees and happy customers take part *transparently*; no astroturfing | 🤖 find, 👤 participate | P1 | ongoing |
| 6.7 | **YouTube**: 6–10 videos, e.g. "Best website visitor identification tools 2026 (tested)", "Leadfeeder vs Albacross", "How to see which companies visit your site in HubSpot", "Is visitor ID GDPR-legal?". Embed each on the matching money page | 👤 record, 🤖 scripts | P1 | L |
| 6.8 | **Podcasts**: use Listen Notes to find top-rated B2B marketing, sales and RevOps shows (EU-focused too) and pitch 3 topics each (GDPR-safe intent, turning anonymous traffic into pipeline) | 🤖 list+pitch drafts, 👤 guest | P2 | ongoing |
| 6.9 | **Unlinked mention reclamation**: find pages mentioning "Albacross" with no link, plus press mentions of founders and execs that link only to LinkedIn. Ask for a link and a positioning line | 🤖 find+draft, 👤 send | P1 | S |
| 6.10 | **LinkedIn** (the #2 cited domain in some studies): exec and founder posts and LinkedIn articles on the core topics, reusing the original data (3.6) | 👤 (+🤖 drafts) | P1 | ongoing |
| 6.11 | **Partner co-marketing**: integration partners (HubSpot, Pipedrive, Bombora, Zapier marketplace listings) with consistent descriptions and links; partner blog swaps with non-competing ICP tools | 👤 | P2 | M |
| 6.12 | **Entity consistency**: make LinkedIn, Crunchbase, Wikidata, G2, the partner directories and llms.txt all say the same thing (category, HQ, founded 2014, positioning) | 🤖 audit, 👤 fix | P1 | S |
| 6.13 | Digital PR around the original data report (3.6): pitch it to EU martech/sales media and newsletters | 👤 | P2 | M |

## WS7: Build the AI SEO agent (in parallel, weeks 1–10)

See `agent-architecture.md` for the design.

| ID | Task | Who | Pri | Effort |
|---|---|---|---|---|
| 7.1 | **Monitor module**: script/skill that pulls prompt-tracker results, Ahrefs rankings, GSC and PostHog AI sessions and writes `state/visibility-YYYY-WW.json` | 🤖 build, 👤 review | P0 | M |
| 7.2 | **VOC module**: an Attio + Intercom mining prompt pack that writes `voc.md` (pains, objections, switch reasons, FAQ trees) | 🤖 | P1 | M |
| 7.3 | **Gap analyst**: scoring = intent × volume/prompt importance × winnability (KD, current rank/citation) × ICP fit − existing coverage. Writes `state/opportunities.json` + Trello cards | 🤖 | P0 | M |
| 7.4 | **Brief generator**: for the top opportunity, analyse the top-10 pages and AI-cited pages and produce a brief (page type, H-structure, must-cover subtopics/fan-out questions, tools to include, VOC quotes, internal links, CTA) | 🤖 | P0 | M |
| 7.5 | **Draft + QC module**: draft to blueprint → fact-check vs `facts.yaml` → competitor-claims check (source required) → style/brand check → JSON-LD → save as **Webflow CMS draft** | 🤖 build, 👤 approves every page | P1 | L |
| 7.6 | **Off-page scout**: from cited-domain data, maintain the placement list and draft personalised outreach (LinkedIn note + Loom script) | 🤖 | P1 | M |
| 7.7 | **Tech auditor**: weekly crawl checks (AI-UA fetch status, canonicals, schema validity, indexability of app subdomains, CWV regressions, sitemap lastmod) | 🤖 | P2 | S |
| 7.8 | **Refresh loop** (5.7) and **impact logging**: every publish or refresh is logged with a date so rank, citation and pipeline lift can be attributed after 30/60/90 days | 🤖 | P1 | S |
| 7.9 | Schedule it: weekly run → Monday report + Trello cards (Claude Code scheduled task or Agent SDK job) | 🤖 | P1 | S |
| 7.10 | Phase C: re-weight gap scoring from what actually produced citations and pipeline (closed loop) | 🤖➜👤 | P3 | M |

## WS8: Governance & review rhythm

| ID | Task | Who | Pri |
|---|---|---|---|
| 8.1 | Weekly 30-min review: agent report, approve drafts, pick next week's queue | 👤 | P0 |
| 8.2 | Monthly: VOC refresh, SoV trend, kill or double-down decisions, update targets | 👤 | P1 |
| 8.3 | Quarterly: re-pull keyword/prompt universe, revisit positioning, legal review of comparison claims | 👤 + 🤖 | P1 |

---

## The first 10 things to do (this week)
1. 0.1 / 0.2 / 0.5: name owners, agree KPIs, buy prompt tracking (Brand Radar add-on or Peec/Profound)
2. 1.5: "How did you hear about us?" field on every form
3. 1.3: AI Assistants channel in PostHog
4. 1.7: Bing Webmaster Tools + AI Performance report
5. 2.1 / 2.2: canonicals + de-index the app subdomains
6. 0.3 / 3.4: `facts.yaml` + positioning block
7. 3.1: mine Attio calls → `voc.md`
8. 6.2: correct the wrong Albacross pricing/framing on RB2B's and others' listicles
9. 4.1: draft "Best website visitor identification software 2026"
10. 4.2: draft "Leadfeeder alternatives"
