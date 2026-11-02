# Albacross AI SEO Agent: architecture

The goal is a system that runs the SEO and AI-visibility (AEO/GEO) loop each week, with a human approving anything that gets published. It is not a one-off content generator.

```
            ┌──────────────────────────────────────────────────────────────┐
            │                  ORCHESTRATOR (weekly cron)                  │
            │    reads state → picks next jobs → routes to sub-agents      │
            └──────────────┬───────────────────────────────┬───────────────┘
                           │                               │
     ┌─────────────────────▼─────┐               ┌─────────▼───────────────────┐
     │ 1. MONITOR                 │               │ 2. RESEARCH (VOC)           │
     │ - prompt tracking (40+     │               │ - Attio call notes/emails   │
     │   money prompts × 5 LLMs)  │               │ - Intercom conversations    │
     │ - Ahrefs rankings / GSC    │               │ → pains, objections, switch │
     │ - PostHog AI referrals     │               │   reasons, verbatim language│
     │ - "how did you hear" field │               └─────────┬───────────────────┘
     └─────────────┬──────────────┘                         │
                   │        ┌───────────────────────────────▼──┐
                   └───────►│ 3. GAP ANALYST                   │
                            │ prompt/keyword × (our page?,     │
                            │ cited?, rank?, competitor cited?)│
                            │ → prioritized opportunity queue  │
                            └──────┬──────────────────┬────────┘
                                   │                  │
                 ┌─────────────────▼───┐      ┌───────▼─────────────────────┐
                 │ 4. CONTENT ENGINE   │      │ 5. OFF-PAGE SCOUT           │
                 │ brief → draft →     │      │ cited domains/listicles we  │
                 │ fact-check → schema │      │ are missing from → outreach │
                 │ → Webflow CMS DRAFT │      │ list + personalised drafts  │
                 └─────────┬───────────┘      └───────┬─────────────────────┘
                           │                          │
                 ┌─────────▼───────────┐      ┌───────▼──────────────┐
                 │ 6. TECH AUDITOR     │      │ HUMAN REVIEW (Trello)│
                 │ crawlability, schema│─────►│ approve / edit / send│
                 │ canonicals, CWV,    │      └───────┬──────────────┘
                 │ llms.txt freshness  │              │ publish
                 └─────────────────────┘              ▼
                                         7. REFRESH LOOP (every 90 days per money page)
```

## Modules

| # | Module | Inputs (tools already connected) | Output | Cadence | Human in loop? |
|---|--------|----------------------------------|--------|---------|----------------|
| 1 | **Monitor** | Prompt tracker (Ahrefs Brand Radar add-on, or Peec/Profound/Otterly), Ahrefs Site Explorer + Rank Tracker, GSC, PostHog `sessions` (AI referrers + `utm_source=chatgpt.com`), CRM "how did you hear about us" | Weekly AI share-of-voice, citations, rankings, AI sessions, self-reported AI attribution | Weekly | No |
| 2 | **VOC Research** | Attio (call recordings, notes, emails), Intercom conversations | Living `voc.md`: pains, objections, switch-away reasons per competitor, buyer phrasing, follow-up question trees | Monthly | Review |
| 3 | **Gap Analyst** | 1 + 2 + `money-keywords.csv` + `money-prompts.csv` + sitemap | Scored opportunity queue: (intent × volume × winnability × revenue fit) minus existing coverage | Weekly | Approve priorities |
| 4 | **Content Engine** | Opportunity + SERP and AI-citation benchmark pages + VOC + product facts file | Brief → draft that follows the Listicle / Landing / Comparison blueprint → fact check against `facts.yaml` → JSON-LD → **Webflow CMS draft** (never auto-publish) | 2–3 pages/week | **Required** |
| 5 | **Off-page Scout** | Cited domains/pages from the prompt tracker, Ahrefs SERP and backlinks, Listen Notes | Target list (listicles, G2/Capterra, Reddit threads, podcasts) with personalised outreach drafts | Weekly | **Required** (humans send) |
| 6 | **Tech Auditor** | Ahrefs Site Audit, fetches with AI user agents, Webflow pages API | Issues list: blocked bots, missing schema/canonicals, indexed app pages, stale `dateModified`, broken llms.txt | Weekly | Fixes reviewed |
| 7 | **Refresh Loop** | Page age, rank/citation decay | Refresh brief for any money page older than 90 days or losing rank/citations | Weekly check | **Required** |

## Guardrails (non-negotiable)
1. **Single source of truth for facts**: a `facts.yaml` (pricing, customers, integrations, data coverage, GDPR position, company-level vs person-level). Every draft is checked against it. LLMs repeat what the web says about you, so a wrong price published once ends up copied into AI answers.
2. **Never auto-publish.** The agent writes Webflow CMS *drafts* and Trello cards. A named human approves.
3. **Fair competitor coverage**: describe competitors accurately and give a date. AI engines and readers both reward balanced comparisons, and inaccurate claims about competitors carry legal risk.
4. **No spam**: no mass AI-generated pages, no fake reviews, no astroturfed Reddit posts. Reddit and review work goes through real customers and employees who say who they work for.
5. **Every claim gets a source**: stats in drafts carry a citation or come from Albacross's own data.

## Build path (suggested)
- **Phase A (weeks 1–4): runs from Claude Code.** Each module is a Claude skill or prompt that calls the MCP connectors already in this workspace: Ahrefs, PostHog, Webflow, Attio, Intercom, Trello. A person triggers it weekly. Gets value quickly without building infrastructure.
- **Phase B (month 2–3): scheduled.** Move to a scheduled job (Claude Agent SDK or a scheduled Claude Code task) that writes a weekly report and Trello cards, and keeps state in the repo (`/state/*.json`).
- **Phase C (month 3+): closed loop.** Measure each content intervention against citation and pipeline lift, then re-weight the gap scoring by what actually moved revenue.

## State files the agent maintains
- `money-keywords.csv`: keyword universe with volume, KD and our rank (refreshed monthly)
- `money-prompts.csv`: tracked prompts (refreshed quarterly)
- `facts.yaml`: approved product facts (owned by PMM)
- `voc.md`: voice-of-customer synthesis
- `state/visibility-YYYY-WW.json`: weekly snapshot (SoV per prompt per engine, cited URLs)
- `state/opportunities.json`: scored queue
- `state/content-log.json`: what was published or refreshed and when, so lift can be measured
