# Refresh audit: Albacross's two existing GDPR assets

**Run date:** 2026-11-02 · **Author:** ai-seo-content-strategist (agent) · **Status:** draft for Legal + PMM

> ⛔ **LEGAL SIGN-OFF REQUIRED BEFORE ANYONE CITES EITHER PAGE.** That covers sales, CS, the writer of the new GDPR hub, llms.txt and third-party profiles. Both pages contain statements that are outdated or contradict Albacross's current DPA and privacy policy. Until Legal approves replacement text, treat them as **not citable**. The "should say instead" wording below comes only from Albacross's current published material, or is marked `[[VERIFY: legal]]`. It is a proposal, not approved copy.

**Pages audited** (raw text pulled from the live pages on 2026-11-02):
| # | URL | Visible date | Schema dates | Body words | Backlinks (Ahrefs, 2026-11-02) |
|---|---|---|---|---|---|
| A | https://www.albacross.com/newsroom/albacross-gdpr | "March 3, 2020" | datePublished 2020-03-03, dateModified 2024-12-30 (no visible update and no content change) | about 850 | 3 live / 2 referring domains (4 / 3 all-time) |
| B | https://www.albacross.com/ebook-chapters/marketers-guide-albacross-and-gdpr | none | none | about 130 | 0 |

**Current Albacross sources used as the reference:**
- **DPA:** https://www.albacross.com/data-processing-agreement, last revised 2024-10-02.
- **Privacy policy:** https://www.albacross.com/privacy-policy, last revised 2024-10-02. Highlights:
  - IP-based visitor data is processed on legitimate interest.
  - Servers are in Ireland.
  - IP + company "may constitute personal data" (e.g. sole traders).
  - Lead Contact Data is deleted within 30 days if there is no response.
  - Right to object via support@albacross.com.
  - The supervisory authority is IMY.
- **Help GDPR FAQ:** https://help.albacross.com/en/articles/3933505-gdpr-frequently-asked-questions, updated 2026-08-13.
- **Help GDPR checklist:** https://help.albacross.com/en/articles/1933616-gdpr-compliance-checklist, updated 2025-10-01.
- **`facts.yaml`:**
  - Contacts come "via credits (data waterfall across leading providers)".
  - Compliance line: "Built for GDPR and CCPA compliance; Data Processing Agreement available".
- **Pricing page:** https://www.albacross.com/pricing (per `facts.yaml`). It has no GDPR content beyond the badge, so it isn't used as a legal source.

⚠️ **The current sources contradict each other** on two points. Replacement text can't be final until Legal decides:
- **Legal basis.** The help FAQ says the customer "must obtain valid consent" before using the script. The privacy policy relies on legitimate interest for Albacross's own processing.
- **Cookie lifetime.** The checklist says 1 year. The privacy policy says 24 months.

---

## A. /newsroom/albacross-gdpr ("Albacross & GDPR: Everything you need to know")

| # | Statement on page (quoted) | Problem | Type | What it should say instead (source) |
|---|---|---|---|---|
| A1 | "March 3, 2020" · "1 min read" · Contents: "Heading 2" | 6.5 years old with no visible update. The read time is wrong. The table of contents shows a template placeholder. The schema dateModified (2024-12-30) doesn't match any visible change | Outdated / technical | Show "Last updated: <date of Legal approval>" and a "Legally reviewed by" line. Fix the read time. Remove the placeholder TOC. Set dateModified only when the content really changes |
| A2 | "we're dedicated to being 100% transparent with how we comply so you can feel totally at ease." | An unsupported absolute claim. The page omits hosting, sub-processors, retention and transfers, so it isn't transparent | Unsupported | Drop "100%". Instead, link to the DPA (sub-processor list, Schedule 3) and the privacy policy (hosting, retention) |
| A3 | "In the infographic below, we explain our role in processing data…" | The infographic is an image with empty `alt`. LLMs and screen readers can't read it, and its content hasn't been reviewed since 2020 | Unverifiable / accessibility | Replace it with an HTML table (customer = controller; Albacross = processor, and controller for database improvement, per DPA Schedule 1). Or add full alt text after Legal checks the image `[[VERIFY: legal, review infographic contents]]` |
| A4 | "Names, email addresses, location data and IP-addresses (static and dynamic) can be personal data." | Broadly correct, but unsourced | OK, keep | Keep it, and add the primary source (GDPR Art. 4(1), Recital 30; CJEU C-582/14 *Breyer*). Align the wording with the privacy policy: "In some cases, the IP-address and the company it is matched with may constitute personal data" |
| A5 | "'company data' … name and address, website and company telephone number. These data points do not fall under the GDPR as they are not considered personal data." | **Legally sensitive and too broad.** Albacross's own privacy policy says IP + company may be personal data (e.g. sole traders). The DPA lists "employees of companies the customer identifies as leads" as data subjects | Contradicts current docs | "Data about companies as legal entities is generally outside the GDPR. But company data can be personal data when it relates to an identifiable person, for example a sole trader, or a named employee's contact details." (Privacy policy; DPA Schedule 1.) `[[VERIFY: legal]]` |
| A6 | "you must obtain valid cookie and inform your visitors…" (the word "consent" is missing) | A typo in the key compliance sentence | Error | Fix the grammar as part of the A7 rewrite |
| A7 | "obtain the valid consent of your visitors to set cookies in their devices and read them" | **Legally sensitive.** It states consent as the only route. Sales now describes cookieless, hybrid and consent-gated set-ups (VOC), and the privacy policy uses legitimate interest for Albacross's own processing. The ePrivacy Directive (Art. 5(3)) isn't named | Conflicts / incomplete | `[[VERIFY: legal]]` Describe the set-up options Legal approves. Separate the ePrivacy question (cookies/device access) from the GDPR legal basis. Link to the new hub `/gdpr-website-visitor-identification` |
| A8 | "…to improve our Lead Generation Service" | Legacy product name. "Generate Leads" is now Identify, Signal, Automate and Engage (`facts.yaml → legacy_names`). The help FAQ says "Intent Data Service" | Outdated | Use the purpose wording from DPA Schedule 1 ("identifying which companies visit the customer's site…") and the current module names `[[VERIFY: legal, purpose wording]]` |
| A9 | "It's easy to make this change. Just copy and paste the text from our GDPR Compliance Checklist… same section as… Google Analytics script" | It oversimplifies a legal step. The checklist was last updated 2025-10-01 and is itself consent-based (see the contradiction above) | Sensitive | "Use the notice text in our GDPR compliance checklist (updated 2025-10-01) as a starting point, and have your legal team adapt it." Update the checklist first `[[VERIFY: legal]]` |
| A10 | "Albacross is the data processor… once we have processed your data, we store this information in our database… We then become data controllers…" | Consistent with the DPA (rev. 2024-10-02, Schedule 1), but no source is given | OK, keep | Keep it, cite the DPA, and add the purpose ("to improve the database") in the DPA's wording |
| A11 | "Is Albacross data GDPR compliant?" → "Yes!" | A blanket compliance claim with nothing behind it. No sources, no certification, no audit | Unsupported | Answer with facts instead: DPA available and signable; data stored on servers in Ireland (privacy policy); sub-processors listed (DPA Schedule 3); right to object via support@albacross.com; supervisory authority IMY. Wording `[[VERIFY: legal]]` |
| A12 | "IP-addresses may constitute personal data and therefore, Albacross (and our customers) must comply with GDPR." | OK. But chapter B says "constitute", without "may" | Inconsistent across pages | Use one approved phrasing on all pages (suggested: the privacy-policy wording quoted in A4) |
| A13 | "Albacross also enriches company data via a third party with contact data for individuals, upon request from customers." | Outdated mechanism. Contacts are now bought with credits through a data waterfall (`facts.yaml`; pricing page credits) | Outdated | "Verified emails and phone numbers for decision-makers at identified companies are available via credits, sourced through a waterfall of data providers listed as sub-processors in our DPA." (`facts.yaml`; DPA Schedule 3) `[[VERIFY: legal]]` |
| A14 | "All contact information shown in the platform has been provided by our third party data partner, Cognism." | **Factually outdated.** DPA Schedule 3 lists Cognism (UK) and Waterfall Data (US). `facts.yaml` describes a waterfall across leading providers. The link target `https://www.cognism.com.` (stray period) **returns 404** | Outdated + broken link | Remove the sentence (and the link). Point to the DPA sub-processor list. Legal to decide whether to name providers publicly `[[VERIFY: legal]]`. **Highest priority: fix this even before the full refresh** |
| A15 | "If your legal team wants a signed copy, please get in touch." | Vague | Improve | "To get a signed DPA, email legal@albacross.com with the signer's name, company and email." (Help GDPR FAQ, 2026-08-13) |
| A16 | "The GDPR states that personal data for direct marketing purposes may be regarded as carried out for a legitimate interest." | A paraphrase of Recital 47, uncited. Acceptable | OK, source it | Keep it and cite Recital 47 GDPR |
| A17 | "This means the company whose personal data you're processing must have a legitimate interest in what you're offering them." | **Legally wrong framing.** The legitimate interest belongs to the *controller*, and it must pass a necessity and balancing test against the *individual's* rights (Art. 6(1)(f)). Companies don't have "personal data" | Legally sensitive | `[[VERIFY: legal]]` Explain the three-part test (purpose, necessity, balancing), and say each customer runs its own assessment. Link to the hub's LIA section |
| A18 | "…you have legal ground to inform them about your services in order to win the lead as a customer." | **Overclaim.** Legitimate interest isn't automatic. B2B email and calls are also governed by ePrivacy Art. 13 and national e-marketing rules. The help FAQ itself says to check local marketing laws | Legally sensitive | "Outreach to identified contacts may rely on legitimate interest if your assessment supports it. You must state the data source and purpose and offer an opt-out, and local e-marketing rules also apply." (Help GDPR FAQ Q10; privacy policy, 30-day deletion of unanswered Lead Contact Data) `[[VERIFY: legal]]` |
| A19 | "It is not intended to hinder business or industry…" | An opinion, with no compliance value | Remove | Delete it |
| A20 | "Albacross has taken the necessary action to ensure we comply with the GDPR." | An unsupported blanket claim | Unsupported | Keep the not-legal-advice disclaimer. Replace the claim with specific measures from DPA §5 and Schedule 2 (encryption, access controls, backups, staff training) |
| A21 | Sidebar/footer badge "GDPR COMPLIANT" (site-wide) | An absolute claim with no certification or audit behind it | Unsupported | Legal to decide: remove it, or change it to "GDPR-ready · DPA available" `[[VERIFY: legal]]` |
| A22 | Bio: "Victor Ekelund, CEO Albacross" (no byline on the article) | Authorship and title not confirmed for 2026 | Verify | `[[VERIFY: current CEO/author]]`. Add a real author plus a Legal reviewer |
| A23 | *(missing)* | No hosting, transfers, sub-processors, retention, right to object, DPO/contact, IMY, CCPA or ePrivacy | Gap | Add short, sourced answers: hosting in Ireland, transfers "subject to appropriate safeguards" (privacy policy; name the mechanism `[[VERIFY: legal]]`), 30-day Lead Contact Data deletion, support@albacross.com, IMY, and "Built for GDPR and CCPA compliance" (`facts.yaml`) |

## B. /ebook-chapters/marketers-guide-albacross-and-gdpr (chapter 8, "Albacross & GDPR")

| # | Statement on page (quoted) | Problem | Type | What it should say instead (source) |
|---|---|---|---|---|
| B1 | "In this chapter, we share our obligations and highlight the actions you need to take to comply…" | The chapter is about 130 words and lists neither the obligations nor the actions. It only links elsewhere. Thin content | Thin / misleading | Either summarise the 5–6 steps (once Legal has approved the hub checklist) or make it a 2-line pointer to the hub |
| B2 | "Albacross reveals the companies visiting your website by identifying IP-addresses and matching them to company data in our proprietary database." | OK factually. "Proprietary" isn't substantiated, but it's low risk | OK | Keep it. Optionally align with positioning: "identifies the companies visiting your website" (`positioning.md`) |
| B3 | "IP-addresses constitute personal data and therefore, Albacross must comply with the GDPR." | Absolute ("constitute"), while page A says "may" and the privacy policy says "in some cases" | Inconsistent | Use the single approved phrasing (see A4/A12) `[[VERIFY: legal]]` |
| B4 | "…including this post and this checklist…" → links to `https://albacross.com/newsroom/albacross-gdpr/` (non-www, trailing slash) and the help checklist | It sends readers to the outdated 2020 post (page A) through a redirecting URL. The checklist is consent-only and conflicts with the privacy policy | Outdated dependency | Link to `/gdpr-website-visitor-identification` (the hub) and the refreshed trust page, using canonical www URLs. Re-link the checklist only after it's updated |
| B5 | "We are happy to go through this documentation with your legal team." | Fine, but gives no contact | Improve | Add "Email legal@albacross.com" (help GDPR FAQ) |
| B6 | Downloadable PDF ("Download Albacross & GDPR", "Get the full ebook as a PDF") | The PDF probably contains the same or older text, and it is out of reach of web edits | Verify | `[[VERIFY: PMM, audit the PDF chapter 8 text; reissue the PDF with the approved copy]]` |
| B7 | Badge "GDPR COMPLIANT" and footer nav "Gain Insight", "Generate Leads" | Unsupported badge (A21). Legacy product names (`facts.yaml → site_inconsistencies`) | Unsupported / outdated | As A21. Change the footer to the Identify / Signal / Automate / Engage names |
| B8 | No date anywhere on the chapter | Undated legal content | Gap | Add "Last updated" once the copy is approved |

## Recommendation: refresh or redirect?

| Asset | Recommendation | Why |
|---|---|---|
| **A. /newsroom/albacross-gdpr** | **Refresh in place** as the branded "Albacross & GDPR" trust page (target prompt P38 "Is Albacross GDPR compliant?"). **Don't redirect it into the hub** | (1) It holds the only GDPR backlinks: 2 live referring domains, and chapter B links to it. (2) The branded P38 question needs an Albacross-specific answer (roles, hosting, sub-processors, DPA, retention, opt-out). The hub answers the generic P18 question, and merging both would blur each. (3) The URL already matches the query. The hub and trust page should cross-link. **Fallback:** if Legal can only support one page for now, 301 it to `/gdpr-website-visitor-identification#how-albacross-approaches-gdpr` |
| **B. Ebook chapter 8** | **Keep the URL, but cut the chapter to a short, dated summary** that links to the hub and trust page. Or **301 it to the hub** if the ebook is being retired | It has no backlinks and only about 130 words, so it has no SEO value on its own. It exists for ebook continuity (chapter 7 → 8 navigation and the PDF). A redirect would break the chapter sequence, so a thin pointer is the safer choice unless PMM retires the ebook |

**Do now, before the full refresh** (each needs only a quick Legal OK):
1. A14: remove the outdated "All contact information… Cognism" sentence and its 404 link.
2. A6: fix the missing word "consent".
3. A1/B4: fix the placeholder TOC, the read time and the non-canonical link.

**Do after Legal resolves the contradictions** (C1–C7 in `ai-seo-agent/research/gdpr-ip-tracking-gap.md`):
- Rewrite A5, A7, A11, A17, A18 and A23.
- Then update the help checklist and FAQ so the help center, privacy policy, DPA, the trust page and the hub all give the same answer.

**Owners:**
- **Legal:** sign-off, and the contradictions (legal basis, cookie lifetime of 1 year vs 24 months, transfer mechanism, badge).
- **PMM:** module names, ebook PDF.
- **Writer:** rewrite from the hub brief `ai-seo-agent/content/briefs/gdpr-website-visitor-identification.md`.
- **Web:** schema dates, TOC, alt text.
