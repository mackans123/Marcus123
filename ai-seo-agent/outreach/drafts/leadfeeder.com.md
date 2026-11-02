---
domain: leadfeeder.com
action: correct
priority: P1
page: https://www.leadfeeder.com/blog/website-visitor-identification/best-visitor-identification-software/   # Albacross #6/10, unlinked
contact: Sanjana Murali (author)
checked: 2026-11-02
---
# Leadfeeder (Dealfront): a fair entry with one outdated price

**Why it matters:** Leadfeeder's /web-visitors page leads the SERP for our category keywords, and its blog list is published by the category leader, so LLMs treat it as authoritative. The entry is fair ("EU teams", "Strong European data coverage"). Only the Organisation price and the Salesforce tier are questionable. This is a competitor, so send only clear fixes.

## Corrections (exact text)
<!-- src: https://www.albacross.com/pricing, checked 2026-11-02 (facts.yaml v0.1) -->
| Currently says | Replace with |
|---|---|
| "Transparent pricing: Starter at €59 per month (annual), Professional at €149, Organization at €375" | "Transparent pricing: Starter from €59 per month and Professional from €149 per month (billed annually); Organisation is custom-priced" |
| "Salesforce bi-directional integration requires Organization" | [[VERIFY: Salesforce plan tier. Send only if wrong]] |

## LinkedIn connection note (≤300 chars)
> Hi Sanjana, thanks for the fair write-up of Albacross in your visitor-ID software guide. One small update: our Organisation plan no longer has a list price (it's custom). Happy to send the exact sentence if useful.

## Follow-up message
> Thanks, Sanjana. The sentence would read: "Starter from €59/month and Professional from €149/month (billed annually); Organisation is custom-priced." Source: albacross.com/pricing (screenshot attached, 2 Nov 2026). Everything else in the entry is accurate. Thanks for keeping the comparison even-handed.

## Loom script (≈45 s)
1. "Hi Sanjana, [name] from Albacross. Thanks for an even-handed entry."
2. Screen: the pricing line next to /pricing. "The only change: Organisation is now custom, not €375."
3. "The exact sentence is in my message. That's it."

## Value offer
- One-sentence fix plus a screenshot. No other ask.

## Pre-send checklist (human)
- [ ] PMM has approved the `pricing` block in `facts.yaml` (status is still DRAFT v0.1).
- [ ] **Fix `albacross.com/llms.txt` first.** It still says Professional "up to 1,000" and Organisation "from €375/user/month". Many of these third-party errors come from that file. If it isn't fixed, the editor can point to our own file.
- [ ] Re-open the page on the day you send. The checks below were made 2026-11-02.
- [ ] Send from a named person's own LinkedIn. One message, one follow-up, then stop.
- [ ] Log the outcome in `placements.csv` (add a `status` note).
