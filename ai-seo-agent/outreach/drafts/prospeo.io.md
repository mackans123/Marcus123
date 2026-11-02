---
domain: prospeo.io
action: add + correct
priority: P1
pages:
  - https://prospeo.io/s/rb2b-alternatives                        # 8 tools, Albacross absent ("rb2b alternatives", P06)
  - https://prospeo.io/s/lead-forensics-alternatives              # 10 tools, Albacross absent (P08)
  - https://prospeo.io/s/albacross-pricing-reviews-pros-and-cons  # Organisation €375; Salesforce tier; "auto-renewal trap"
contact: "Prospeo Team" (no byline). Contact via prospeo.io/contact or a Prospeo marketing lead on LinkedIn [[VERIFY: name]]
checked: 2026-11-02
---
# Prospeo: fill two gaps, fix one pricing page

**Why it matters:** Prospeo (DR 73, ~31k organic visits/mo) publishes "real pricing" programmatic pages that LLMs quote. Its RB2B and Lead Forensics alternatives lists have no EU company-level option, and its Albacross pricing page repeats the outdated €375 Organisation price.

## Corrections (exact text)
<!-- src: https://www.albacross.com/pricing, checked 2026-11-02 (facts.yaml v0.1) -->
| Currently says | Replace with |
|---|---|
| "Organisation: €375/mo (annual), custom monthly; 200 email credits, 60 phone credits" | "Organisation: custom pricing (501+ identified companies/month)" [[VERIFY: Organisation credit allowance]] |
| "Salesforce (Organisation)" | [[VERIFY: Salesforce tier]] |
| "Auto-renewal trap" | Ask them to cite the source or rephrase to "annual plans renew automatically; check notice period" [[VERIFY: terms]] |

## Add requests
- rb2b-alternatives: "Albacross: for teams with mostly European traffic, where person-level ID raises GDPR issues. Company-level, from €59/mo billed yearly, 14-day trial."
- lead-forensics-alternatives: "Albacross: published pricing (from €59/mo) vs Lead Forensics' quote-only model."

## LinkedIn connection note (≤300 chars)
> Hi [name], your "real pricing" pages are useful, and the Albacross pricing page is close. One plan is outdated: Organisation is now custom, not €375. Also, your RB2B and Lead Forensics alternatives lack an EU option. Can I send details?

## Follow-up message
> Thanks! (1) Albacross pricing page: Organisation is custom-priced, and Starter/Professional are unchanged. (2) If useful, here are two short entries for your RB2B and Lead Forensics alternatives pages, both written around published pricing, which fits your "real pricing" angle. Source: albacross.com/pricing (screenshot attached).

## Loom script (≈60 s)
1. "Hi, [name] from Albacross. Your pricing pages are the kind buyers trust, so here's one update."
2. Screen: their page next to /pricing. "Starter and Professional are right. Organisation is custom now."
3. "Two of your alternatives lists have no European option. Our pricing is public, which suits your format. Entries are in my message."

## Value offer
- Sourced pricing, two entries, and screenshots.

## Pre-send checklist (human)
- [ ] PMM has approved the `pricing` block in `facts.yaml` (status is still DRAFT v0.1).
- [ ] **Fix `albacross.com/llms.txt` first.** It still says Professional "up to 1,000" and Organisation "from €375/user/month". Many of these third-party errors come from that file. If it isn't fixed, the editor can point to our own file.
- [ ] Re-open the page on the day you send. The checks below were made 2026-11-02.
- [ ] Send from a named person's own LinkedIn. One message, one follow-up, then stop.
- [ ] Log the outcome in `placements.csv` (add a `status` note).
