# Shared conventions for all Albacross AI SEO agents

Every agent in `.claude/agents/ai-seo-*.md` reads this file first.

## Paths (relative to repo root)
| What | Where |
|---|---|
| Plan & tasks | `ai-seo-agent/README.md`, `ai-seo-agent/TASKS.md` |
| Approved product facts (single source of truth) | `ai-seo-agent/facts.yaml` |
| Positioning block | `ai-seo-agent/positioning.md` |
| Voice of customer | `ai-seo-agent/research/voc.md` |
| Competitor sheet | `ai-seo-agent/research/competitors.md` |
| Keyword universe | `ai-seo-agent/money-keywords.csv` |
| Prompt universe | `ai-seo-agent/money-prompts.csv` |
| Weekly snapshots | `ai-seo-agent/state/visibility-YYYY-WW.json` |
| Opportunity queue | `ai-seo-agent/state/opportunities.json` |
| Content log | `ai-seo-agent/state/content-log.json` |
| Briefs / drafts | `ai-seo-agent/content/briefs/<slug>.md`, `ai-seo-agent/content/drafts/<slug>.md` |
| Placement list / outreach drafts | `ai-seo-agent/outreach/placements.csv`, `ai-seo-agent/outreach/drafts/*.md` |
| Technical audit | `ai-seo-agent/research/tech-audit.md` |

## Connected tools (MCP)
- **Peec AI**: the official AI-visibility tracker (ChatGPT, Google AI Overview, Gemini). It has no API here, so exports are saved in `ai-seo-agent/state/peec/`. Compare month-on-month on the same 30-day basis and the same prompt set. Next re-run: 2026-12-02.
- **Ahrefs**: rankings, keywords, SERPs, backlinks, site audit. Always call `mcp__Ahrefs__doc` for a tool before its first use, and use `mode=subdomains` for domains. Brand Radar is NOT in the plan, so don't call `brand-radar-*`.
- **PostHog**: web analytics and AI referral sessions (`sessions.$entry_referring_domain`, `$entry_utm_source`).
- **Attio**: CRM, call recordings, notes, emails (for voice-of-customer research).
- **Intercom**: support conversations.
- **Webflow**: CMS and pages. Only the publisher agent writes, and only DRAFTS.
- **Trello**: task board.
- **WebSearch / WebFetch**: SERP and AI-citation checks, third-party pages.

## Hard rules
1. **Never publish, send or post anything externally.** Agents write files and drafts. A human approves and sends. Webflow writes are CMS *drafts* only, and only after a human approves the draft in chat.
2. **Facts come from `facts.yaml`.** If a fact isn't there, mark it `[[VERIFY: …]]`. Never invent pricing, customer counts, accuracy rates, or integrations.
3. **Competitor claims need a source URL and a date checked**, kept in an HTML comment `<!-- src: url, checked YYYY-MM-DD -->`. Be fair: say where a competitor is the better fit.
4. **Privacy**: VOC output contains no personal names, emails or company names of prospects or customers unless that customer is already a public case study. Quote anonymously ("Head of Marketing, SaaS, DACH").
5. **No spam tactics**: no fake reviews, no astroturfed Reddit/forum posts, no mass-generated thin pages.
6. **Positioning**: use the block in `positioning.md` word for word, so the site and third-party mentions describe Albacross the same way.
7. Write dates as absolute dates (today's date), never "recently".
8. Finish every run with a short summary: what you produced (file paths), what needs human action, open questions.

## URL safety (SEO work is in progress, rule set by Marcus on 2026-11-02)
- **Never change, move, rename, merge or redirect an existing URL or slug.** Never delete or unpublish an existing page or CMS item.
- New pages go on **new** slugs only, and only after the URL is agreed with the SEO team.
- Any task that needs a redirect, slug change or consolidation is **ON HOLD (needs SEO team)** in TASKS.md.
- Never run a full Webflow site publish. It would push other people's pending changes. Publish only individual CMS items that have no pending edits (lastUpdated ≤ lastPublished before our change). Page-level changes stay staged for the web team's next publish.

## Page blueprints

### Listicle / alternatives (`best-*`, `*-alternatives`)
1. Money keyword in the slug and in a single H1 (e.g. "12 Best Leadfeeder Alternatives in 2026 (Tested & Compared)")
2. Author byline (real person, bio line) + "Last updated: <date>"
3. **TL;DR** (40–70 words) that answers the query directly and names Albacross plus 2–3 others
4. **Quick shortlist table**: Tool | Best for | Identification level | Starting price | GDPR stance. Albacross is #1 with an honest "best for"
5. "Why teams look for an alternative to X" (from VOC: real switch reasons)
6. "How we evaluated" (criteria + method; credibility)
7. Full list: for each tool give a 1-paragraph overview, best for, key features, pros, cons, pricing (sourced) and a "choose it if…" line. Albacross gets the most depth plus a customer quote
8. Full comparison table
9. Page-specific FAQ (5–8 Qs from VOC/Intercom, phrased the way buyers ask). Each answer starts with a self-contained 1–2 sentence answer
10. CTA block (free trial, no credit card, 14 days) + 5+ internal links (other alternatives pages, comparison pages, integrations, GDPR hub)
11. GEO enrichments: at least 3 statistics (Albacross data or sourced), at least 2 quotes (customer/expert), and outbound citations to credible sources

### Comparison (`albacross-vs-x`)
TL;DR verdict → side-by-side table (identification level, data coverage EU/US, intent data, outreach automation, ABM ads, integrations, GDPR/DPA, pricing, free trial) → "choose X if / choose Albacross if" → migration steps → customer quote → FAQ → CTA.

### How-to / jobs-to-be-done
Answer first (steps) → the manual way (and where it breaks) → the Albacross way → GDPR notes → FAQ → CTA.

## Draft file format
Markdown with YAML front matter:
```yaml
---
slug: best-website-visitor-identification-software
target_keyword: website visitor identification software
secondary_keywords: [...]
target_prompts: [P01, P02, P26]
page_type: listicle
meta_title: "... (≤60 chars)"
meta_description: "... (≤155 chars)"
author: "[[VERIFY: author name]]"
status: draft | qc-passed | approved | published
---
```
