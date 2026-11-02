# QC report: leadfeeder-alternatives

**Draft:** `ai-seo-agent/content/drafts/leadfeeder-alternatives.md` · **Brief:** `ai-seo-agent/content/briefs/leadfeeder-alternatives.md`
**QC date:** 2026-11-02 · **Reviewer:** ai-seo-content-qc (agent) · **Result:** `status: qc-passed`, with pre-publish human gates (see section 4)
**Word count (body, excluding front matter, tables and HTML comments):** 3,770 (was 3,817; target ≤3,800)

## 1. PASS/FAIL table

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Albacross facts match `facts.yaml` | PASS (fixed) | Pricing (€59/€149, Talk to us), tiers, credits, add-on credit prices, 30% annual saving and 14-day/no-card trial all match facts.yaml and the live /pricing page (re-checked 2026-11-02). Positioning block (one-liner, short description, best for, not-a-fit) is used word for word. Added the like-for-like caveat (Starter covers up to 100 companies and 10+5 credits; Activate starts at 1,000 companies and 200 credits) wherever the draft compares €59 with €369. |
| 2 | Case studies are public (Alpega, Appello) | PASS | Both `/customer-stories/alpega` and `/customer-stories/appello` return 200, have no robots noindex, and are linked from the public hub https://www.albacross.com/success-stories (a fake slug returns 404). They are public, so I kept them, but they are **not yet in facts.yaml `proof.customer_stories`**. PMM should add them (plus Reply, PHC, Turn Energy and Contanto Seguro, which are also listed). |
| 3 | Case-study stats and quotes match live pages | PASS (fixed) | All five quotes and stats verified verbatim. Alpega quote: exact. Planday quote: exact. Appello: "more than 8 months", "roughly thirty percent more (!) companies than the competitive product" (competitor not named; the draft now says "not named in the story"). Omron reworded to match the page: the *previous marketing automation tool* identified 4% and Albacross 28%, "7 times that of the previous provider" (the draft had said Omron "went from 4% to 28%"). Spendesk: "approximately 33% higher than cold outbound leads" (contact-to-opportunity). Each has a src comment that holds the verbatim text. |
| 4 | VOC evidence anonymised, anecdotal, not generalised | PASS (fixed) | The minimum-plan claim lost its "agency in Finland" label and moved from the "why teams leave" list into switch step 1 as a buyer tip. It is framed as "one anecdote", the draft notes that Leadfeeder's pricing page states no minimum, and it says "ask". The "value for price" line lost its "cleantech, Denmark" label and is now a paraphrase, because VOC doesn't mark it as the buyer's own words. On 14/18 vs 13/18, I removed "the margin is often small", which generalised from one trial; it now reads "one trial, not a benchmark: the gap was a single account". The UI line is paraphrased. |
| 5 | Leadfeeder minimum-plan claim vs live pricing | PASS (reframed) | The live https://www.leadfeeder.com/pricing/ shows Discover from €79/mo (up to 50 companies) with "Try for free" on every paid tier, and **no stated minimum plan or minimum billing**. Our anecdote is not supported by the public page, so it now appears only as an anonymous, single-buyer experience with that caveat. |
| 6 | Competitor pricing re-verified at source | PASS (fixed) | All six named in the ask, plus Factors, SalesViewer, Happierleads, HubSpot (2 pages), ZoomInfo and 6sense: 100% of pricing sources and 17 of the ~19 cited URLs were re-fetched. See section 2. |
| 7 | Fairness and legal risk (Leadfeeder) | PASS (fixed) | See section 3. |
| 8 | Fairness (other competitors) | PASS (fixed) | Happierleads: the draft implied it had no GDPR stance, but its page says "GDPR & CCPA compliant" with a DPA on paid plans, so I corrected that in three places. ZoomInfo: removed the unsourced "buyers raised GDPR questions about US-based vendors" and replaced it with the factual "no GDPR note on the product page". Lead Forensics: removed the "manual page tagging / per-site pricing" con (based on 1–2 rep notes). Leadinfo: removed the "too coarse to be useful" quote and kept a softer "some buyers found its feature set broader than they needed". |
| 9 | Blueprint: H1, byline/date, TL;DR, shortlist, why switch, how evaluated, 12 entries, full table, FAQ, CTA | PASS | Single H1 with keyword; TL;DR is 58 words and names Albacross + 3 others; shortlist table with Albacross #1 and Leadfeeder as a reference row; FAQ has 8 Qs with self-contained bold first sentences; 4 CTA placements as the brief asks. |
| 10 | Blueprint: author byline (real person + bio) | FAIL (human) | Still `[[VERIFY: author name]]` / `[[VERIFY: author bio line]]`. This must be done before publish. |
| 11 | Blueprint: ≥5 internal links | PASS | 18 internal URLs, 16 of which return 200 today (see section 5). |
| 12 | Blueprint: ≥3 stats, ≥2 quotes, outbound citations | PASS | Stats: Omron 28% vs 4%, Spendesk +33%, Appello ~30% more, Leadfeeder €79→€369 step, Leadinfo ~30% typical ID rate. Quotes: Alpega, Planday. Outbound citations: Leadfeeder pricing, rebrand FAQ and integrations pages, each vendor's pricing page, Cision, Leadinfo release, HubSpot KB, EUR-Lex. |
| 13 | SEO: keyword in slug/H1/title/first 100 words | PASS | "leadfeeder alternatives" is in the slug, H1 and meta title; "Leadfeeder alternative" is in TL;DR sentence 1. |
| 14 | SEO: meta title ≤60, description ≤155 | PASS (tight) | Title 57 chars; description 155 chars (at the limit, so re-count in the CMS; if the CMS counts "€" as 2 bytes, drop "Updated Nov 2026."). |
| 15 | SEO: no keyword stuffing; headings work as Q/A | PASS | Headings are natural questions or answers. |
| 16 | AEO: each H2 answers on its own | PASS (fixed) | Each H2 opens with a bold self-contained answer. Removed the cross-reference "See the step-by-step guide above" from the FAQ. |
| 17 | AEO: no unproven superlatives | PASS (fixed) | "Most teams leave Leadfeeder because…" became "The reasons we hear most…". "That is the price step most switchers mention" was removed (VOC doesn't support it). FAQ #1 "The best alternative … is Albacross" became "we recommend Albacross (our product)" with the reason. |
| 18 | Readability and brand | PASS | Plain and unhyped, with a disclosure line and honest cons for Albacross. |
| 19 | Word count ≤3,800 excl. tables | PASS | 3,770. |
| 20 | Brand history accuracy | PASS (fixed) | "June 2022: announced a merger" isn't supported by the cited Cision release ("following their merger in 2022", no month), so it now reads "2022: merged". Added "no functionality was removed" (verbatim from the Leadfeeder FAQ). |

## 2. Source re-verification log (2026-11-02)

| Claim in draft | Source | Result |
|---|---|---|
| Leadfeeder Lite €0 / Discover €79 (€113 monthly) / Activate €369 (€527) / Scale €599 / Enterprise custom; 14-day trial; save 30%; Lite last 100 companies, 7-day history, unlimited users | leadfeeder.com/pricing | Confirmed |
| Leadfeeder Lite "20 credits" listed as *contacts* | same | **Corrected.** The credits row is "shared monthly allowance for enrichment, exports, and CRM syncs"; verified emails/phones are listed under Activate. Table column renamed "Verified contacts". |
| Leadfeeder Scale "Annual only" | same | **Corrected.** The page says both "billed annually only" and "annual paid upfront or quarterly" (internal inconsistency on their page). |
| Leadfeeder "Outreach automation: not on the pricing page" | same | **Corrected for fairness.** The page lists display-ad Campaigns, LinkedIn Audience Sync, workflows and CRM automations (Activate+). It does not list email/LinkedIn sequences. |
| Leadfeeder intent | same | Lists "Filter by intent signals" and "intent topics"; source not stated. `[[VERIFY]]` kept. |
| Leadfeeder is company-level only | leadfeeder.com/blog/.../company-level-vs-person-level-identification/ | Confirmed: "Leadfeeder does company-level identification. We do not do person-level." Wording tightened to "anonymous visitors", because Leadfeeder does show individuals who self-identify. |
| Rebrand 24 March 2026; module/API renames; no pricing/contract/hosting change; entities keep names | leadfeeder.com/product-updates/dealfront-is-rebranding-as-leadfeeder-faq/ | Confirmed. Also adds "Leadfeeder API → Legacy Leadfeeder API" and "No functionality is being removed". |
| Leadfeeder integrations (Salesforce … Zapier) | leadfeeder.com/integrations/ | Confirmed |
| Dealfront launch 3 April 2023 | news.cision.com release | Confirmed. "June 2022" was not supported and has been removed. |
| RB2B Free / $79 / from $149 / from $199; 7-day trial; "Contact-level (person) ID is US only." | rb2b.com/pricing | Confirmed. The free plan is "150 monthly resolutions" (company-level only), so the draft wording changed from "identifications" to "resolutions a month". The trial needs no card (added). |
| Warmly from $10,000/yr; quarterly; no GDPR note | warmly.ai/pricing | Confirmed ($4,875/quarter; "Save 30%" on annual) |
| Leadinfo €69 / €159 / €359 | leadinfo.com/en/pricing/ | **Partly corrected.** The plan cards show those figures, but the calculator on the same page shows €49 annual / €59 monthly for 0–50. The draft now states both and advises getting a quote. 14-day trial, ~30% ID rate and Art. 6(1)(f) confirmed. |
| Leadinfo acquired Visitor Queue 20 Jan 2026; 9,000+ clients in Europe; team.blue | leadinfo.com/?p=40099 | Confirmed |
| Snitcher $49–$529; ~30% annual discount; 14-day, no card; Art. 6(1)(f) | snitcher.com/pricing | Confirmed |
| Lead Forensics: no published pricing; Essentials/Automate; 1-week trial; quote text | leadforensics.com/pricing/ | Confirmed (verbatim quote matches) |
| Factors Lite $199/mo, Basic $6K, Growth $20K, Enterprise $36K+ | factors.ai/pricing | Confirmed |
| HubSpot buyer intent KB quote; tiers; credits | knowledge.hubspot.com/reports/use-buyer-intent; hubspot.com/.../credits | Confirmed ($10 per 1,000 credits; "Included credits vary by product and tier"). **H3 changed** from "HubSpot buyer intent (formerly Breeze Intelligence)" to "HubSpot buyer intent", because no source supports "formerly". |
| SalesViewer €99/€339/€629; 20% annual; excl. VAT; 14-day; "No contract…" | salesviewer.com/pricing | Confirmed |
| Happierleads $99/mo billed yearly, 300 visitors; 7-day/100 visitors, no card; "174+ countries" | happierleads.com/pricing | Confirmed; GDPR stance corrected (see row 8 above) |
| ZoomInfo WebSights quote; no pricing; free trial no card | zoominfo.com/features/identify-website-visitors | Confirmed |
| 6sense quote-only; Bombora Topic Pack and AI Email add-ons; volume bands | 6sense.com/pricing/ | Confirmed |
| Albacross €59/€149, 30%, 14-day/no card | albacross.com/pricing | Confirmed |

Not re-fetched: the EUR-Lex GDPR link (a stable official source) and the Albacross internal newsroom pages (checked for status 200 only).

## 3. Leadfeeder fairness and legal-risk review (every statement)

Comparative advertising in the EU (Directive 2006/114/EC) must be objective, verifiable and like-for-like, and must not denigrate. Statement-by-statement outcome:

| Statement | Risk before | Action |
|---|---|---|
| "Most teams leave Leadfeeder because of…" | Unverifiable generalisation from 6 accounts | Changed to "The reasons we hear most…", with sample size disclosed |
| "that is the price step most switchers mention" | Unsupported by VOC | Removed |
| "contacts only from Activate" / €59 vs €369 comparisons | Not like-for-like (volumes and credit counts differ ~10×) | Wording is now "listed from Activate", with a volume caveat in the Albacross entry, at-a-glance table and Pros. Leadfeeder is credited with "higher volumes on one plan" in the verdict and FAQ |
| Lite "20 credits" shown as contacts | Factual error | Corrected |
| "Brand and product churn … some teams want a calmer roadmap" | Speculative and mildly denigrating; no VOC support (Dealfront mentions = 0) | Replaced with factual API rename facts plus "teams with custom integrations should check them" |
| "Minimum plans for new customers" (buyer quote, agency, Finland) | Implies Leadfeeder doesn't honour published pricing, based on one anecdote; identifiable label | Anonymised and moved to the switch checklist as a single anecdote. Notes the pricing page states no minimum |
| "Outreach automation: Not on the pricing page" | Misleading omission (Campaigns, LinkedIn sync and CRM automations exist) | Replaced with an accurate "Activation" row |
| "doesn't offer person-level identification" | Partly inaccurate (self-identified individuals are shown) | Qualified as "anonymous" visitors, with a Leadfeeder-authored source |
| "Albacross is better if you want intent data" (FAQ) | Implied Leadfeeder has no intent | Changed to "Bombora intent" |
| UI "slightly more compelling" (in Leadfeeder's favour) | Low | Paraphrased (provenance not labelled in VOC) |
| "What Leadfeeder still does well" section | Positive; sourced | Kept; added a src to the hosting statement |

Residual risk: **low**. Every remaining Leadfeeder statement is either sourced to leadfeeder.com (dated 2026-11-02) or explicitly framed as a single anonymous anecdote. Recommendation: have legal give the Leadfeeder rows a quick read before publish, because this page names a direct competitor in the title.

## 4. Remaining human actions

**Pre-publish gates (must be done before `approved`):**
1. `[[VERIFY: author name]]` and `[[VERIFY: author bio line]]`: add a real person with a bio line (blueprint requirement; needed for Person schema).
2. `[[VERIFY: PMM approval of case-study quotes and stats]]`: PMM approves the Alpega and Planday quotes and the Appello, Omron and Spendesk stats. **Add Alpega and Appello to `facts.yaml → proof.customer_stories`** (both are public; see row 2).
3. `[[VERIFY: Salesforce integration tier, SSO, API access]]` in the Albacross pricing table (Organisation row): PMM. If it can't be confirmed, replace the cell with "Custom".
4. `[[VERIFY: does Leadfeeder use third-party intent in 2026?]]`: its pricing page lists "intent signals" and "intent topics" without a source. Confirm (Leadfeeder docs or a trial account) or leave the "source not stated" wording and remove the VERIFY tag.
5. Legal: quick read of the Leadfeeder statements (section 3).

**Launch dependencies (links kept in the draft):**
6. `/compare/albacross-vs-leadfeeder` returns **404** and is linked 4 times (Albacross entry, at-a-glance, FAQ, related reading). Publish it first, per the URL plan in the brief.
7. `/best-website-visitor-identification-software` returns **404** (linked once, in related reading). Its draft exists in `content/drafts/`; publish it first or remove the link at launch.
8. Decide the URL plan (the brief recommends that the listicle take `/leadfeeder-alternative`, which currently serves the 1:1 page). The front-matter slug is `leadfeeder-alternatives`; align the slug with the final URL.

**Site issues found during QC (fix on albacross.com):**
9. Template bug: the Appello Q&A block ("roughly thirty percent more (!) companies…") also renders on other customer-story pages (seen on /customer-stories/planday). An LLM or a reader could attribute Appello's stat to Planday. Fix in Webflow.
10. `/customer-stories` (the index) returns 404, while `/success-stories` is the hub. Consider a redirect.

**Nice to have:**
11. Meta description is exactly 155 chars; re-count in the CMS.
12. Leadinfo's own pricing page is internally inconsistent (cards vs calculator). Re-check at the 90-day refresh.

## 5. Internal link check (HTTP status, 2026-11-02)

200: /register, /book-a-demo, /pricing, /identify, /signal, /engage, /newsroom/bombora-partnership, /newsroom/albacross-gdpr, /data-processing-agreement, /snitcher-alternative, /leadinfo-alternative, /lead-forensics-alternative, /clearbit-alternative, /6sense-alternative, /customer-stories/appello, /customer-stories/alpega, /success-stories (added).
404 (launch dependencies): /compare/albacross-vs-leadfeeder, /best-website-visitor-identification-software.
The anchors for the five "-alternative" URLs changed from "X alternatives" to "Albacross vs X", because those pages are 1:1 comparisons (their titles are "Albacross vs X …").

## 6. Status decision

`status: qc-passed`. No factual, sourcing, privacy or legal-risk issues remain open in the copy. The open items are human sign-offs (author, PMM approval, one Leadfeeder intent check) and launch dependencies, and all are tracked in section 4. Don't move the draft to `approved` until gates 1–5 are closed.
