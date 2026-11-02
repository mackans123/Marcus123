# Albacross AI SEO / AI-visibility program: analysis & plan

*Prepared 2026-11-02. Sources: the Breaking B2B "SEO & AEO for Revenue" playbook (shared research doc), live Ahrefs data, PostHog data, a crawl of albacross.com, and external research (sources listed at the bottom).*

**Goal:** get Albacross named and cited when B2B buyers ask ChatGPT, Perplexity, Claude, Gemini, Copilot or Google AI Overviews/AI Mode which tool to use, and turn that visibility into pipeline. The work is run by an AI SEO agent with a human approving output (see [`agent-architecture.md`](agent-architecture.md)). The full task breakdown is in [`TASKS.md`](TASKS.md).

---

## 1. Where Albacross stands today (baseline)

| Metric | Albacross | RB2B | Leadinfo | Leadfeeder | Snitcher |
|---|---|---|---|---|---|
| Domain Rating (Ahrefs) | **75** | 77 | – | 81 | 66 |
| Est. organic traffic / mo | **~2,200** | ~8,000 | ~18,300 | ~35,800 | ~1,150 (+2,800 paid) |
| Organic keywords (top 100) | **49** | 299 | 896 | 3,015 | 41 |

*Ahrefs Site Explorer, 2026-10-31.*

**What the numbers say**

1. **Authority is not the problem; coverage is.** Albacross has a DR of 75, about level with RB2B (77). Yet roughly 60% of its organic traffic is brand searches: "albacross" alone sends ~1,100 visits to the homepage, plus /register, app and login pages. In the US it ranks for only **22 keywords**.
2. **Organic traffic is falling.** It peaked at ~3,000/mo in spring 2025 and dropped to ~1,150 in Sep 2026, about −60%. October and November show some recovery.
3. **There is no blog to rank with.** `/blog` returns 404. The content lives in `/newsroom` (80 posts, mostly older or informational) and ebook chapters. Albacross has **no listicle** ("best website visitor identification tools") and no alternatives roundups, and these are the page types Google and LLMs cite most for this category.
4. **The comparison pages exist but don't rank.** `/leadfeeder-alternative`, `/clearbit-alternative`, `/6sense-alternative` and similar are about 1,000-word 1:1 landing pages. None of them reaches the US top 100 for "leadfeeder alternatives" (600/mo, KD 0), "clearbit alternatives" (250/mo, KD 0) and the rest. Pages that do rank for these queries are listicles: RB2B's "Top 12 Leadfeeder Alternatives" (#2), Gartner, Reddit, getbreakout, Snitcher, Factors.ai and Cognism.
5. **AI traffic is small but growing.** From PostHog (AI referrers plus `utm_source=chatgpt.com`):

   | Month 2026 | Sessions | AI-referred sessions | Share |
   |---|---|---|---|
   | Jul | 3,702 | 25 | 0.7% |
   | Aug | 7,962 | 65 | 0.8% |
   | Sep | 8,089 | 114 | 1.4% |
   | Oct | 10,732 | 106 | 1.0% |

   ChatGPT accounts for most of it. Many AI clicks arrive with no referrer, so treat these numbers as a floor. In Ahrefs' own data, AI was 0.5% of visits but 12.1% of signups, so this channel should be judged on pipeline, not on volume.
6. **How AI and third parties describe Albacross:**
   - Albacross *is* named in the main category listicles, but in the middle of the list and on pages written by competitors. Examples: #6 on Leadfeeder's own "best visitor identification software", #2 on RB2B's Leadfeeder-alternatives page, #2 on 11x's list, #8 of 13 on Factors.ai's.
   - It is **missing** from newer "RB2B alternatives" and AI-SDR-era lists (Prospeo, Bitscale).
   - **Competitors own the "Albacross alternatives" query** (100/mo): Warmly, Knock-AI, Happierleads, ModernInbound and Abmatic all have pages for it.
   - The common framing is "EU / company-level only". RB2B lists Albacross pricing inconsistently (€99 vs €79).
   - Albacross currently has **no control over its own narrative** in the sources LLMs read.
7. **The technical base is mostly fine, with fixable gaps:**
   - ✅ Webflow serves server-rendered HTML, so AI crawlers (which don't run JavaScript) can read it.
   - ✅ robots.txt allows all bots. GPTBot, ClaudeBot, PerplexityBot and OAI-SearchBot all get HTTP 200.
   - ✅ `llms.txt` exists and is good, last updated 2026-09-29. Evidence says it doesn't move citations, but it costs nothing to keep.
   - ⚠️ **No `<link rel="canonical">`** on the homepage, pricing, newsroom or alternative pages, and UTM-tagged URLs are indexed (e.g. `?utm_source=Blog...`).
   - ⚠️ **The homepage and pricing page have no Organization / SoftwareApplication schema.** The homepage has only 2 H2s.
   - ⚠️ **App, login and management subdomains are indexed** (`app.albacross.com/account/integration`, `management.albacross.com`). The app subdomain serves no robots.txt.
   - ⚠️ The sitemap covers only 158 URLs, and no blog or listicle section exists.
8. **AI visibility (Peec AI, 2026-10-04 → 11-02):** Albacross trails Leadfeeder on every engine. ChatGPT 41.6% vs 50.4%, **Google AI Overview 27.3% vs 50.5%** (the widest gap) and Gemini 31.0% vs 51.2%. Albacross does lead on Gemini share of voice (31.8%), with win rate and position close to Leadfeeder's. Intent-data and ABM listicles that name Leadfeeder and Factors but not Albacross are among the most-cited sources. See `state/peec/`.

## 2. What actually drives AI visibility (evidence summary)

| Lever | Evidence | Implication for Albacross |
|---|---|---|
| **Brand mentions across the web** | Ahrefs, 75K brands: mentions correlate 0.664 with AI Overview visibility vs 0.218 for backlinks | Off-page mentions in listicles, Reddit, YouTube, LinkedIn, G2/GetApp and podcasts are the biggest lever. Authority (DR 75) is already there. |
| **Third-party "best X" listicles** | About 44% of ChatGPT-cited page types are "best X" lists. Vendors' own sites are cited only about 12% of the time when ChatGPT recommends software. | Get into the top 3 of the listicles AI cites, *and* publish Albacross's own. |
| **Your own BOFU pages** (listicles, alternatives, comparisons, integrations) | Breaking B2B playbook. RB2B grew non-branded traffic +77% from "leadfeeder alternatives" content. | Build the missing page types. Most target keywords have **KD 0–6**. |
| **Fan-out coverage** | AI Mode and AI Overviews issue sub-queries. Only 12–38% of cited URLs rank top 10 for the main query. | Cover the follow-up questions (pricing, GDPR, accuracy, integrations, vs pages) in depth, but don't mass-produce thin pages (Google scaled content abuse policy). |
| **Freshness** | Seer: ~65% of AI bot hits go to content updated in the last year. Ahrefs: cited URLs are 26% fresher. | Make real updates to money pages every 90 days, with visible "last updated" dates. |
| **Content style** | Princeton GEO paper: adding quotes +43%, statistics +33%, cited sources +28%; keyword stuffing −9% | Use Albacross's own data (3B+ events/mo, identification rates by country), customer quotes, and sourced stats. |
| **Bing index** | 87% of SearchGPT citations matched Bing's top results (Seer). Bing Webmaster Tools now has an AI Performance report. | Set up Bing Webmaster Tools and IndexNow. |
| **YouTube** | The #1 cited domain in AI Overviews (~23–30%) | Make demo and comparison videos and embed them on money pages. |
| **Schema / llms.txt** | Controlled tests show no citation uplift | Do it for hygiene and rich results; don't expect AI wins from it. |

## 3. Strategy in one paragraph

Albacross's own site already has the authority (DR 75) to rank but lacks the pages. In **Month 1**:
- fix the technical gaps;
- turn on measurement (prompt tracking, AI channel, "how did you hear about us");
- run voice-of-customer mining on Attio calls and Intercom;
- rebuild the comparison layer as **best-in-class listicles and alternatives roundups** for the KD 0–6 money keywords.

In **Months 2–3**, the AI SEO agent runs the loop each week:
- monitor prompts;
- find gaps (prompts where competitors are named and Albacross isn't, plus the third-party URLs being cited);
- draft pages and refreshes into Webflow as drafts for human approval;
- run an **off-page program** to get into the listicles, review sites, Reddit threads, YouTube videos and podcasts that LLMs actually cite.

Positioning should be consistent everywhere: *company-level, GDPR-first, EU-strong, intent + auto-engage, transparent pricing from €59/mo.* That turns the "EU / company-level only" framing into the reason buyers choose Albacross.

## 4. Targets (proposed. Agree them in week 1)

| KPI | Baseline (Oct 2026) | 90-day target | 6-month target |
|---|---|---|---|
| AI visibility vs Leadfeeder (Peec, 30-day) | ChatGPT 41.6% vs 50.4% · AI Overview 27.3% vs 50.5% · Gemini 31.0% vs 51.2% | close ChatGPT gap; AIO ≥40% | ≥ Leadfeeder on all 3 engines |
| Non-branded organic clicks / mo | ~800 (est.) | 2× | 4× |
| Money keywords in top 3 (US + UK + DE + SE) | ~2 | 15 | 40 |
| AI-referred sessions / mo | ~106 | 250 | 500 |
| Listicles (3rd-party) with Albacross in top 3 | ~1 | 8 | 20 |
| Demos/signups attributed (self-reported "AI" + AI sessions) | not measured | tracked | +X pipeline (set with RevOps) |

## 5. Files in this folder

- `README.md`: this analysis
- `TASKS.md`: the full task breakdown (workstreams → tasks, owner, agent vs human, priority, effort, timing)
- `agent-architecture.md`: how the AI SEO agent is built (modules, tools, guardrails, build phases)
- `money-keywords.csv`: priority keyword universe with live Ahrefs volume and difficulty
- `money-prompts.csv`: 40 buyer prompts to track AI share of voice against

## Sources

- Breaking B2B, *B2B SaaS SEO & AEO for Revenue* (internal research doc)
- Ahrefs, AI Overview brand correlation (75K brands): https://ahrefs.com/blog/ai-overview-brand-correlation/
- Ahrefs, AI search vs Google top-10 overlap: https://ahrefs.com/blog/ai-search-overlap/
- Ahrefs, freshness of AI citations: https://ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content/
- Ahrefs, AI traffic conversions (0.5% → 12.1% signups): https://ahrefs.com/blog/ai-search-traffic-conversions-ahrefs/
- Seer Interactive, SearchGPT vs Bing: https://www.seerinteractive.com/insights/87-percent-of-searchgpt-citations-match-bings-top-results
- Seer Interactive, content recency: https://www.seerinteractive.com/insights/study-ai-brand-visibility-and-content-recency
- Aggarwal et al., GEO (KDD 2024): https://arxiv.org/abs/2311.09735
- DerivateX, ChatGPT software recommendation sources: https://derivatex.agency/report/chatgpt-software-recommendation-sources/
- Semrush, most-cited domains in AI: https://www.semrush.com/blog/most-cited-domains-ai/
- SE Ranking via SEJ, llms.txt and citations: https://www.searchenginejournal.com/llms-txt-shows-no-clear-effect-on-ai-citations-based-on-300k-domains/561542/
- Vercel, AI crawlers & JavaScript: https://vercel.com/blog/the-rise-of-the-ai-crawler
- OpenAI crawler docs: https://developers.openai.com/docs/bots
- Google, AI features & your website: https://developers.google.com/search/docs/appearance/ai-features
- Category listicles reviewed: Leadfeeder, RB2B, 11x, Factors.ai, Bitscale, Prospeo, Warmly "Albacross alternatives"
