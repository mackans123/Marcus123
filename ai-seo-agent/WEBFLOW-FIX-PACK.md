# Webflow fix pack: albacross.com (2026-11-03)

These fixes are ready to apply. **None of them changes a URL, slug or redirect** (URL safety rule, see CONVENTIONS.md).

Context:
- The site is not on Webflow Enterprise, so page changes only go live through a **full-site publish**.
- Someone already has unpublished changes on the Home page (edited 2026-10-30; last publish 2026-10-29). Check with the team before publishing.
## ✅ Applied and PUBLISHED LIVE by Claude on 2026-11-03 (full-site publish at Marcus's request; verified on the live site)
- A1: Organization + WebSite JSON-LD on Home
- A2: SoftwareApplication + offers JSON-LD on Pricing
- A3: FAQPage JSON-LD on /6sense-alternative, /clearbit-alternative and /lead-forensics-alternative (it mirrors the visible FAQs word for word)
- /leadfeeder-alternative copy: "only reads activity on your website" → "scores activity on your website"; table cell "Your website only" → "Not stated on pricing page"; intent FAQ reworded to say Leadfeeder lists intent signals/topics on Activate+; price FAQ now says "both billed annually; the plans include different company volumes". The page's FAQPage JSON-LD was synced to match.
- Pricing SEO title and meta description. Old: "What does Albacross' Revenue Acceleration platform cost? Get a customized pricing plan…". New: "Published pricing: Starter from €59/month and Professional from €149/month billed yearly, Organisation on request. 14-day free trial, no credit card needed."

No slugs or URLs were changed. Nothing was published. After the next publish, validate at https://search.google.com/test/rich-results.

- G: newsroom link clean-up done. 49 posts and 193 links now point to https://www.albacross.com, and 37 UTM tags were removed. A live scan of all 81 posts afterwards found 0 UTM and 0 non-www internal links. Skipped: b2b-email-marketing (draft).

The full-site publish also pushed whatever else was staged, including the Home-page edits from 2026-10-30.

---

Site ID: `67336b6d03d7829a16579243`

---

## A. Structured data (JSON-LD): ✅ STAGED 2026-11-03 · TASKS 2.3
Apply in **Page settings → Schema markup** (or Custom code → inside `<head>`). Neither page has JSON-LD today.

### A1. Home (page id `67336b6d03d7829a16579251`): Organization + WebSite
```json
{"@context":"https://schema.org","@graph":[
 {"@type":"Organization","@id":"https://www.albacross.com/#organization","name":"Albacross","legalName":"Albacross Nordic AB","url":"https://www.albacross.com",
  "logo":"https://cdn.prod.website-files.com/67336b6d03d7829a16579243/677e35932a231ffa0db0ee35_ms-icon-310x310.png",
  "description":"Albacross is a European B2B website visitor identification and intent platform that shows which companies visit your site and helps you engage them.",
  "foundingDate":"2014","address":{"@type":"PostalAddress","addressLocality":"Stockholm","addressCountry":"SE"},
  "sameAs":["https://www.linkedin.com/company/albacross/","https://twitter.com/albacrossnordic","https://www.facebook.com/albacrossnordic/","https://www.g2.com/products/albacross/reviews"]},
 {"@type":"WebSite","@id":"https://www.albacross.com/#website","url":"https://www.albacross.com","name":"Albacross","publisher":{"@id":"https://www.albacross.com/#organization"},"inLanguage":"en"}]}
```

### A2. Pricing (page id `6745d3fa8d70ad1c8e355069`): SoftwareApplication + offers
```json
{"@context":"https://schema.org","@type":"SoftwareApplication","@id":"https://www.albacross.com/#software","name":"Albacross","url":"https://www.albacross.com",
 "applicationCategory":"BusinessApplication","applicationSubCategory":"B2B website visitor identification and intent data platform","operatingSystem":"Web",
 "description":"Albacross identifies the companies visiting your website, scores them by fit and buying intent, and pushes high-intent accounts to your CRM, Slack or Teams, with AI-personalised email and LinkedIn outreach to decision-makers. Published pricing from €59/month billed yearly, with a 14-day free trial.",
 "publisher":{"@id":"https://www.albacross.com/#organization"},
 "offers":[
  {"@type":"Offer","name":"Starter","url":"https://www.albacross.com/pricing","price":"59","priceCurrency":"EUR","availability":"https://schema.org/InStock",
   "priceSpecification":{"@type":"UnitPriceSpecification","price":"59","priceCurrency":"EUR","unitText":"month","billingDuration":"P1Y","description":"From €59/month billed yearly (€84/month billed monthly). 0–100 identified companies per month; 10 verified email and 5 verified phone credits included."}},
  {"@type":"Offer","name":"Professional","url":"https://www.albacross.com/pricing","price":"149","priceCurrency":"EUR","availability":"https://schema.org/InStock",
   "priceSpecification":{"@type":"UnitPriceSpecification","price":"149","priceCurrency":"EUR","unitText":"month","billingDuration":"P1Y","description":"From €149/month billed yearly (€213/month billed monthly). 0–500 identified companies per month; 25 verified email and 10 verified phone credits included."}}]}
```
After publishing, validate at https://search.google.com/test/rich-results.

### A3. FAQPage schema on /6sense-alternative, /clearbit-alternative, /lead-forensics-alternative
Copy the pattern from /leadfeeder-alternative and rewrite the Q&As to match each page's visible FAQ.

## B. llms.txt: 5 min · TASKS 2.9 · **highest-impact fix**
At least 7 third-party listicles copy the wrong pricing from llms.txt. Replace its `## Pricing` section with the text in `research/llms-txt-pricing-fix.md` (or tech-audit.md §9). Also:
- remove or fix the 4 `integrations.albacross.com` links (that site returns HTTP 451);
- add the 6sense, Clearbit and Lead Forensics pages under Comparisons;
- use the current product names (Identify / Signal / Automate / Engage).

## C. Site settings: 5 min · TASKS 2.1
- **Site settings → SEO → Global canonical tag URL:** `https://www.albacross.com`. This gives every page a self-referencing canonical and removes the indexed `?utm_` duplicates.
- **Site settings → SEO → Sitemap:** keep it auto-generated, and check that the newest posts appear (2026-10-30 and 2026-11-02 are missing).

## D. Fix risky claims on existing comparison pages (same URLs): TASKS 4.7
Leadfeeder's pricing page offers "intent signals" and "intent topics" filters (Activate and above), so these lines are unsafe:
- `/leadfeeder-alternative` hero: "Leadfeeder (formerly Dealfront) only reads activity on your website." → suggest: "Leadfeeder (formerly Dealfront) scores activity on your website. Albacross adds Bombora research data on what each visiting company researches across the web."
- Comparison table row "Off-site research (Bombora)": change "Your website only" → "Not stated on Leadfeeder's pricing page (intent topics on Activate+)".
- FAQ "How is the intent data different?" (visible text **and** JSON-LD): remove "Leadfeeder's intent comes from your own website".
- Price FAQ: add "both billed annually" to "€59/month vs €79 for Leadfeeder Discover". Note: the two plans cover different company volumes.
- Same check on `/leadinfo-alternative` and `/snitcher-alternative` meta descriptions ("Leadinfo scores on-site visits…").
- "100+ intent signals" and "3B+ events" sit in meta descriptions and hero stats. PMM must confirm them; until then they're unapproved claims.

## E. Case-study template: every story's text ships on every case-study page (Designer) · TASKS 3.7
**Root cause (verified 2026-11-03):** the Customer Stories template holds 11 static sections (`section_main-story-content` + combo classes apello, reply, qvantum, spendesk, payfit, omron, alpega, planday, phc, cloudtalk, general). Conditional visibility hides the 10 that don't belong, but Webflow still renders them in the HTML with `w-condition-invisible` (display:none). People see the right story. AI crawlers read the raw HTML, see all 11 customers' quotes and stats on every page, and misattribute them (e.g. Alpega's testimonial on Omron, Appello's "thirty percent more" on Planday).

**Fix:** move each customer's story text into that item's CMS `content` rich-text field (it's empty for 10 of 12 items), bind one rich-text block in the template to it, and delete the 11 static sections. URLs stay unchanged.

## F. Headings and performance (Designer): TASKS 2.12 / 2.7
- 22 pages have no `<h1>`, including Home, /pricing and the product pages. Set the headline element's tag to H1. This is a visual no-op.
- /generate-leads, /auto-engage and /gain-insight have LCP of 3.3–3.7 s from heavy PNG/SVG files: compress them. /newsroom has CLS 0.264.

## G. Newsroom link hygiene (CMS rich text): ✅ DONE 2026-11-03 · TASKS 2.11
- 6 posts contain 37 internal links tagged `?utm_source=Blog…`. Strip the UTM parameters.
- 48 posts contain 193 links to `albacross.com/…` without www, each costing 2 redirect hops. Change them to `https://www.albacross.com/…`.

These change link targets inside posts, not page URLs. Publish item by item, and only for items with no other pending edits.

## H. Not Webflow (engineering): TASKS 2.2 / 2.13
- `app.`, `management.` and `test.albacross.com` are indexed. Add `X-Robots-Tag: noindex`, serve a real robots.txt, use the GSC removal tool, and put test. behind auth.
- integrations.albacross.com returns HTTP 451 (Vercel deployment disabled): restore it or redirect it on that subdomain.

## I. Needs Legal before any edit
- /newsroom/albacross-gdpr (2020): outdated Cognism sentence plus a broken link, and the "company data is not personal data" claim. Full list in `research/gdpr-assets-refresh-audit.md`.

## On hold (URL changes: SEO team decides)
/customer-stories → /success-stories redirect · newsroom → blog move · merging cannibalising posts · /leadfeeder-alternative repurposing.
