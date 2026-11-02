# AI SEO weekly report, 2026-W45 (BASELINE)

Generated 2026-11-02. This is the first snapshot, so there are no week-over-week deltas yet. Data: `state/visibility-2026-W45.json`. Real AI visibility is in **Peec** (`state/peec/`): ChatGPT 41.6% vs Leadfeeder 50.4% · AI Overview 27.3% vs 50.5% · Gemini 31.0% vs 51.2%.

## Headline numbers
| Metric | Value |
|---|---|
| albacross.com organic traffic / keywords (Ahrefs, 2026-10-31) | 2,201 / 49 (DR 75) |
| Competitor organic traffic | Leadfeeder 35,761 · Leadinfo 18,290 · RB2B 8,040 · Lead Forensics 7,930 · Warmly 6,116 · Snitcher 1,151 |
| Money keywords ranking (27 tracked, top 100 in US/GB/DE/SE) | 2 of 27, both #5 US: "identify website visitors", "b2b website visitor identification" |
| AI-assistant sessions, last week (2026-10-26 to 11-01) | 30 (1.3% of 2,277 sessions) |
| AI sessions, last 8 weeks | 208: ChatGPT 192 (92%), Gemini 9, Perplexity 7, others 0 |
| AI session conversion, 8 weeks | Signup 6/208 (2.9%) vs 0.8% site-wide · demo form 2/208 (1.0%) vs 0.15% (small sample; directional) |
| Prompt spot-checks (web-search proxy) | Albacross named in 4 of 9 non-branded prompts; albacross.com cited in **0 of 10** |

## 3 things that stand out
1. **Albacross is mentioned in answers, but its own pages are never the source.** Mentions come only from third-party lists. It is absent from GDPR prompts P03 and P18 (Leadinfo owns those), and from intent data (P12), Clearbit (P07) and identifying anonymous companies (P14).
2. **AI traffic grew for 3 months, then stalled.** AI sessions went 25 → 65 → 114 (Jul–Sep) and then 106 in October, while total sessions grew 33%. The share fell from 1.41% to 0.99%. `/data-api` had 35 AI sessions but none in the last 4 weeks, which may be a lost citation.
3. **Index hygiene problems show up in brand search results.** `test.albacross.com` ranks #3 GB for "albacross". `app.albacross.com/account/integration` ranks #1 DE. A `?utm_source=` URL ranks #1 GB for "leads generation". "albacross pricing" lands on `/account-based-marketing`, not `/pricing`.

## 3 recommended actions
1. Ship the GDPR hub and the EU-angled listicles first (TASKS 4.12, 4.1, 4.3).
2. Fix the indexing leaks: noindex `app.` and `test.` (2.2), canonicals for UTM URLs (2.1), point brand-pricing intent to `/pricing` (4.18).
3. Get onto the lists that AI answers draw from (6.3, plus the Peec list of 16 pages) and own the "Albacross alternatives" query (4.5).

## Gaps
- No self-reported attribution: Attio only has "Deal source" (Inbound/Outbound). Add a discovery-source field (1.5, 1.6).
- Conversion events available in PostHog: `NewSignup`, `book_demo_form_submitted`, `MeetingBooked`.
