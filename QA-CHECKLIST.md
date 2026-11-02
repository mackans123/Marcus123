# Frontend QA – preview.albakaos.com

Test target: **https://preview.albakaos.com**, workspace **"Albacros Nordic AB"**
(switch via profile menu → Switch workspace). Login credentials: ask Marcus (kept out of git; `.env.qa` locally).

Scope: the whole frontend (almost everything changed under the hood). **Outreach section is out of scope.**
Mode: **read-only** – do not create, edit or delete segments, connectors, users, campaigns etc. unless told otherwise.

For every page/flow check: page renders, no "Something went wrong" screen, no JS errors in the console,
no 4xx/5xx calls to `api.albakaos.com`, numbers look sane, desktop (1440px) and mobile (390px) layout.

## Findings so far (2026-11-02, headless Chromium)

| # | Severity | Where | Finding | Status |
|---|---|---|---|---|
| 1 | Medium | Every page after workspace load | `GET api.albakaos.com/customers/6/subscription_expiry_date` returns **404** | Confirmed |
| 2 | Low (data) | Workspace switcher / profile | Workspace named "Albacro**s** Nordic AB" (missing s) | Confirmed |
| 3 | Low | Direct URL `/settings`, `/notifications` | Unknown route shows generic "Something went wrong" crash screen instead of a 404 page | Confirmed (real settings route is `/account/company`) |
| 4 | Medium? | Profile menu → **Notifications** | Clicking it does nothing; menu stays open, no page/panel | **Verify manually** |
| 5 | Info | `/companies`, `/companies/all` | ~16 s until network idle; most other pages 7–10 s | Check if preview-env only |

## Coverage checklist

### Done – page loads cleanly (no errors except #1)
- [x] Login page (desktop + mobile)
- [x] Login with email/password → lands on `/companies`
- [x] Switch workspace modal + switching
- [x] Home (`/home`)
- [x] Website Visitors – segments overview (`/companies`), all visitors list (`/companies/all`)
- [x] Pages & Intent Levels (`/website_pages`)
- [x] External Buying Signals (`/signals`)
- [x] Buyer Personas (`/buyer_personas`)
- [x] Connectors overview + all 13 type tabs (`/connector/overview/*`)
- [x] ABM: Campaigns / Overview / Publishers / Companies / Ads (`/campaign/*`)
- [x] Advertise (`/advertise`)
- [x] Settings landing (`/account/company`)

### To do – interactive
- [ ] Notifications (finding #4)
- [ ] Settings sub-pages: Billing & Plans, Security, Users & Permissions, Agency Settings, Personal Info, Personal Security, Integrations, Website Tracking, API Keys, Tag…
- [ ] Website Visitors list: search, every filter type, "Last seen" ranges, sorting each column, pagination/infinite scroll
- [ ] Company detail (click a company): visits, pages, sessions, sources, contacts, intent
- [ ] Segment detail (click a segment card) + grid/list toggle + segment search
- [ ] Export (CSV) from visitors list – file downloads and contents match the table
- [ ] Pages & Intent Levels: list, search, sort (view only)
- [ ] External Buying Signals: open a report, topics, filters
- [ ] Buyer Personas: open a persona, AI generator opens (don't save)
- [ ] Connectors: open a connector detail, Activity Log
- [ ] ABM: date range picker, campaign status filter, export
- [ ] Home: numbers vs. Website Visitors counts consistent
- [ ] Forgot password page, Sign up page (render only)
- [ ] Logout + protected route redirects to login
- [ ] Mobile (390px) pass over all pages above
- [ ] Browser back/forward and page reload on deep links keep state
