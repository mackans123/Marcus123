---
domain: aisdr.com
action: correct (+ link request)
priority: P0
page: https://aisdr.com/blog/website-visitor-tracking/   # Albacross #5/9
ranks: US #6 "website visitor identification software", #7 "identify website visitors", #8 "website visitor tracking software", #10 "website visitor identification"; AI Overview source for all four
contact: Joshua Schiefelbein (author). Page last reviewed 2026-10-14, so they do update it.
checked: 2026-11-02
---
# aiSDR: fix price and contract claim

**Why it matters:** this is the third-party page Google's AI Overview cites most for our P1 category keywords. It already lists Albacross, but with two wrong facts.

## Corrections (exact text)
<!-- src: https://www.albacross.com/pricing, checked 2026-11-02 (facts.yaml v0.1) -->
| Currently says | Replace with |
|---|---|
| "Starts at €79 per month." | "Starts at €59 per month (Starter, billed yearly); 14-day free trial, no credit card required." |
| Limitations: "Company-level identification only, and annual contracts required." | "Company-level identification only. Monthly and annual billing are available (annual saves 30%)." |

Optional add (from facts.yaml): "Includes AI-powered email and LinkedIn sequences to decision-makers at identified companies, and a Bombora-powered off-site intent layer." Also ask them to link the Albacross heading to https://www.albacross.com/.

## LinkedIn connection note (≤300 chars)
> Hi Joshua, I liked your visitor-tracking guide on aiSDR, and the G2 quote you used about Albacross is spot on. Two details are outdated: we start at €59/mo, and monthly billing is available. Could I send the exact wording?

## Follow-up message
> Thanks, Joshua. Here are the two lines:
> • "Starts at €79 per month" → "Starts at €59 per month (Starter, billed yearly); 14-day free trial, no credit card."
> • "annual contracts required" → "Monthly and annual billing available (annual saves 30%)."
> Source: albacross.com/pricing (screenshot attached). If you're open to it, linking the heading to albacross.com would help readers check the details. I can also share a short quote on how teams combine company-level identification with AI SDR outreach, which fits your audience.

## Loom script (≈60 s)
1. "Hi Joshua, [name] from Albacross. Thanks for including us in your visitor-tracking guide."
2. Screen: their Albacross section. "Two things changed: our entry price is €59 a month billed yearly, not €79, and we don't require annual contracts. Monthly billing is available."
3. Screen: albacross.com/pricing toggle (monthly/yearly). "Here's the pricing page that shows both."
4. "I've put the replacement lines in my message. I can also give you a quote on pairing visitor ID with AI SDR workflows if that's useful for the next refresh."

## Value offer
- Corrected lines plus a screenshot.
- An expert quote for their AI-SDR audience. [[VERIFY: spokesperson name/title]]
- Customer proof from public case studies (PayFit, CloudTalk, Spendesk). [[VERIFY: approved metrics]]

## Pre-send checklist (human)
- [ ] PMM has approved the `pricing` block in `facts.yaml` (status is still DRAFT v0.1).
- [ ] **Fix `albacross.com/llms.txt` first.** It still says Professional "up to 1,000" and Organisation "from €375/user/month". Many of these third-party errors come from that file. If it isn't fixed, the editor can point to our own file.
- [ ] Re-open the page on the day you send. The checks below were made 2026-11-02.
- [ ] Send from a named person's own LinkedIn. One message, one follow-up, then stop.
- [ ] Log the outcome in `placements.csv` (add a `status` note).
