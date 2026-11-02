# Money Keyword Matrix (from VOC)

**Run date:** 2026-11-02 · **Source:** `research/voc.md` (Attio notes and emails, Intercom; 2026-05-01 to 2026-11-02) · **Status:** draft. Volumes and difficulty are NOT checked yet; the gap analyst should run them through Ahrefs before prioritising.

Legend: **NEW** = not in `money-keywords.csv` or `money-prompts.csv`. **EXT** = a sharper variant of an existing row (the existing ID is given). **EXISTS** = already covered. `[[VERIFY]]` = depends on a product fact that is not in `facts.yaml`. Do not publish those claims until confirmed.

## 1. The matrix (5 columns)

| 1. Solution terms (buyer words) | 2. Industries / segments / regions | 3. Competitor + switch reason (VOC) | 4. Jobs to be done | 5. Integrations |
|---|---|---|---|---|
| website visitor identification | B2B SaaS (HR, fintech, language tech) | **Leadfeeder**: new minimum plan/billing for new customers; price (~€156/mo seen); Albacross better value incl. marketing suite | see which companies visit without forms | HubSpot |
| company-level visitor identification | Manufacturing / industrial tech | **Lead Forensics**: manual page tagging; per-site pricing; cookie-gated; CSV workflows; Nordic coverage | separate noise (ISP/VPN/bots) from real leads | Salesforce |
| B2B website visitor tracking | Logistics & commercial property (corporate / IR sites) | **Leadinfo**: too many unused features; coarse industry data; lower identification in a trial | prioritise accounts that hit high-intent pages | Pipedrive |
| IP-to-company API / Reveal API | Marketing & sales agencies (multi-client) | **HubSpot / Clearbit Reveal**: "already in our CRM"; Albacross answer = EU identification + intent + activation | push identified accounts to CRM automatically | SuperOffice `[[VERIFY: not native yet]]` |
| identification rate / match rate | Professional services / consulting | **ZoomInfo**: GDPR risk (US vendor); aggressive discounting | real-time Slack / Teams alerts to sales | Slack |
| buying intent / signals | Telecom / IT services | **Dreamdata**: over-engineered for small teams | build LinkedIn audiences from visiting companies | Microsoft Teams |
| GDPR-compliant / cookieless visitor identification | **Regions:** Sweden, Denmark, Norway, Finland (Nordics), UK, Germany/DACH, Benelux, Poland | Apollo Signals / Clay (evaluated alongside for "signals") | weekly leadership report of visiting companies (no manual CSV) | LinkedIn Matched Audiences / LinkedIn Ads |
| ABM / warm outbound | SMB teams with low traffic | — | enrich server-log IPs with company data (API) | Google Sheets |
| visitor intelligence | Enterprise multi-site estates (14–40+ sites) | — | run identification across many client sites | Google Tag Manager |
| | | | route leads to reps by region | Webhooks / n8n `[[VERIFY]]` |
| | | | query visitor data from Claude / Copilot | Zapier `[[VERIFY]]` |
| | | | run a fair side-by-side tool test | Claude MCP `[[VERIFY: launch ~2026-11-17]]` |
| | | | decide if it is worth it at low traffic | Clay, Attio `[[VERIFY]]` |

## 2. Long-tail money keywords / prompts (column combinations)

| # | Keyword / prompt | Columns combined | Type | Status | Notes |
|---|---|---|---|---|---|
| 1 | lead forensics alternative for Nordic companies | Competitor + Region | Alternatives | **NEW** (EXT of `lead forensics alternatives`, P08) | VOC: Nordic coverage gap vs LF |
| 2 | lead forensics alternative without manual page tagging | Competitor + JTBD | Alternatives | **NEW** | VOC: "240+ pages" manual tagging |
| 3 | lead forensics pricing | Competitor | Pricing page | **NEW** | VOC: per-site pricing frustration |
| 4 | albacross vs lead forensics | Competitor (brand) | Comparison | **NEW** | 4 accounts in the sample; there is no LF comparison prompt yet |
| 5 | leadfeeder alternative with a lower minimum plan | Competitor + Solution | Alternatives | **NEW** (EXT of P04) | VOC: Leadfeeder minimum-plan change |
| 6 | leadfeeder vs albacross: which identifies more companies in Europe | Competitor + Region + Solution | Comparison | EXT of P05 | Lead with the trial-count method |
| 7 | leadinfo alternative Germany / DACH | Competitor + Region | Alternatives | **NEW** (EXT of `leadinfo alternatives`) | VOC: DACH agency leaving Leadinfo |
| 8 | leadinfo pricing | Competitor | Pricing page | **NEW** | |
| 9 | do I need a visitor identification tool if I have HubSpot | Competitor + JTBD | How-to / objection | **NEW** | Top objection plus churn reason |
| 10 | HubSpot visitor identification vs dedicated tool (Europe) | Competitor + Region + Integration | Comparison | **NEW** | Use the CSM framing; no unsourced claims |
| 11 | ZoomInfo alternative for GDPR-compliant website visitor identification | Competitor + Solution + Region | Alternatives | **NEW** | |
| 12 | website visitor identification for property and real estate companies | Solution + Industry | Listicle / landing | **NEW** | Two property deals incl. a €22k multi-site deal |
| 13 | which companies visit our investor relations page | JTBD + Industry | How-to | **NEW** | Corporate-comms use case (not lead gen) |
| 14 | automated weekly report of companies visiting our website | JTBD | How-to | **NEW** | Replaces the manual CSV pain |
| 15 | website visitor identification for manufacturing companies | Solution + Industry | Listicle | EXISTS (P28) | VOC confirms: industrial buyers ask for industry references |
| 16 | IP to company API pricing (per lookup / small volume) | Solution | Landing (API) | **NEW** (EXT of `ip to company api`) | `[[VERIFY: API tiers]]` |
| 17 | enrich server log IP addresses with company data | Solution + JTBD | How-to (API) | **NEW** | Buyer said "nginx server logs" word for word |
| 18 | website visitor identification for agencies with multiple client sites | Solution + Industry + JTBD | Landing | EXT of P27 | `[[VERIFY: agency pricing/discount]]` |
| 19 | white-label / reseller IP-to-company data for agencies | Solution + Industry | Landing | **NEW** | Three agency inbound threads asked for this |
| 20 | website visitor identification webhooks to n8n | Integration + JTBD | Integration how-to | **NEW** | `[[VERIFY]]` |
| 21 | SuperOffice website visitor tracking integration | Integration | Integration page | **NEW** | ⚠️ Only if/when the integration ships; currently a gap |
| 22 | Microsoft Teams alerts when a target account visits our website | Integration + JTBD | Integration how-to | **NEW** (sibling of P22 Slack) | Teams is confirmed in facts |
| 23 | retarget companies that visited our website on LinkedIn | Integration + JTBD | How-to | **NEW** | LinkedIn Matched Audiences is confirmed |
| 24 | Pipedrive website visitor tracking integration | Integration | Integration page | EXISTS (P23) | |
| 25 | send website visitor company data to HubSpot | Integration | Integration page | EXISTS (P20) | |
| 26 | how to filter ISP and VPN traffic out of website visitor identification | Solution + JTBD | How-to | **NEW** | High pain. Be honest about limits |
| 27 | does website visitor identification work without cookies | Solution + Region | FAQ / how-to | **NEW** (related P18/P19) | Legal-approved wording needed |
| 28 | cookieless website visitor identification GDPR | Solution + Region | Landing / hub | **NEW** | `[[VERIFY with legal]]` |
| 29 | is website visitor identification worth it for low traffic B2B websites | Solution + Segment + JTBD | How-to / calculator | **NEW** | Top "Lost" reason. Rule of thumb ~20% `[[VERIFY]]` |
| 30 | website visitor identification match rate UK vs Nordics vs US | Solution + Region | Data study | **NEW** | Needs published Albacross data `[[VERIFY]]` |
| 31 | how to compare website visitor identification tools side by side (trial method) | Solution + Competitor | How-to | **NEW** | Wins came from head-to-head trials |
| 32 | best website visitor identification tool in Denmark / Finland / Norway | Solution + Region | Listicle | EXT of P30 | DK/NO/FI active in pipeline |
| 33 | website visitor identification for Swedish SMBs | Solution + Region + Segment | Listicle | EXT of P30 | Buyer asked word for word about "coverage of Swedish SMBs" |
| 34 | intent data for fintech and payments companies | Solution + Industry | Listicle | **NEW** | |
| 35 | auto-assign website visitor leads to sales reps by region | JTBD + Integration | How-to | **NEW** | |
| 36 | query website visitor data in Claude (MCP) | Integration + JTBD | How-to | **NEW** | `[[VERIFY: launch date]]`. Customers already do this by hand |
| 37 | warm outbound to companies that visited your website | Solution + JTBD | How-to | **NEW** | Rep framing that buyers repeated |
| 38 | website visitor tracking tool for B2B companies in Germany / DACH | Solution + Region | Listicle | EXISTS (P29) | |
| 39 | best IP to company API | Solution | Listicle | EXISTS (P24) | ChatGPT already sends traffic to `/ip-to-company-api` |
| 40 | website visitor identification for HR software / SaaS | Solution + Industry | Listicle | EXISTS (P26) | |

**Totals:** 40 rows: **27 NEW**, 6 EXT, 7 EXISTS.

## 3. Suggested additions to `money-prompts.csv` (draft IDs; human to approve before merging)

| draft_id | prompt | cluster | matrix_column | funnel_stage |
|---|---|---|---|---|
| P41 | Lead Forensics vs Albacross: which identifies more companies in the Nordics? | Comparison | Competitor | BOFU |
| P42 | Best Lead Forensics alternatives without manual page tagging | Alternatives | Competitor | BOFU |
| P43 | Do I need a website visitor identification tool if I already have HubSpot? | JTBD / objection | Competitor+Integration | MOFU |
| P44 | Is website visitor identification worth it for a low-traffic B2B website? | JTBD | Job to be done | MOFU |
| P45 | How do I filter ISPs, VPNs and bots out of website visitor identification? | JTBD | Job to be done | MOFU |
| P46 | Does website visitor identification work without cookies? | JTBD / objection | Job to be done | MOFU |
| P47 | How can I see which companies visit our investor relations page? | JTBD + Industry | Solution+Industry | MOFU |
| P48 | Website visitor identification for agencies managing many client websites | Category + Industry | Solution+Industry | BOFU |
| P49 | How to enrich server-log IP addresses with company data via API | Category (API) | Solution | BOFU |
| P50 | Leadinfo alternatives in Germany | Alternatives | Competitor | BOFU |

## 4. Notes for the gap analyst / strategist
- **Do not build RB2B, Snitcher, 6sense or Warmly switch-reason content from this VOC.** There were zero mentions in the sample. Use competitor research instead (`research/competitors.md`).
- **Lead Forensics is under-represented** in the current keyword and prompt universe compared with how often it appears in VOC (4 accounts, with a clear switch story). It is the highest-value addition.
- Several rows depend on facts that are **not yet in `facts.yaml`** (API tiers, agency pricing, webhooks/n8n/Zapier, MCP, SuperOffice, match rates). Get confirmation before drafting.
