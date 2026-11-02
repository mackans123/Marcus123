---
name: ai-seo-weekly
description: Run the Albacross AI SEO program cycle - coordinates the ai-seo-* subagents (monitor, VOC, gap analyst, strategist, writer, QC, off-page scout, tech auditor, publisher). Use when the user says "run the weekly AI SEO cycle", "next AI SEO wave", "produce the next pages", or asks for the AI SEO status.
---

# Albacross AI SEO: orchestration

You are the orchestrator. The subagents do the work; you sequence them, check what they hand back, and keep the human in control. Read `ai-seo-agent/CONVENTIONS.md`, `ai-seo-agent/TASKS.md` and the latest `ai-seo-agent/state/report-*.md` first.

## Weekly cycle

**Step 1. Measure (parallel, background)**
- `ai-seo-monitor`: weekly snapshot + report
- `ai-seo-tech-auditor`: only if no audit exists yet, the last one is older than 30 days, or the site changed

**Step 2. Decide**
- `ai-seo-gap-analyst`: refresh `state/opportunities.json` using the new snapshot
- Show the user the top 5 opportunities and the proposed queue for this week (2–3 pages + 1–2 refreshes). **Wait for the user to confirm or edit the queue.**

**Step 3. Produce (parallel per page)**
- For each queued slug, run in sequence: `ai-seo-content-strategist` (brief) → `ai-seo-content-writer` (draft) → `ai-seo-content-qc` (QC + fixes)
- At the same time: `ai-seo-offpage-scout` updates placements and drafts outreach for the top 15

**Step 4. Human review**
- Summarise each draft for the user: slug, QC verdict, `[[VERIFY]]` items, link to file
- The user approves → set `status: approved` → `ai-seo-publisher` creates the **Webflow CMS draft**. The user publishes in Webflow.
- Outreach drafts are handed over for a human to send. Agents never send.

**Step 5. Log & commit**
- Update `state/content-log.json`, tick finished items in `TASKS.md`, and commit to the working branch

## Monthly extras
- `ai-seo-voc-researcher`: refresh `research/voc.md` + keyword matrix
- Refresh rotation: any money page last updated more than 90 days ago is queued as a refresh

## Rules
- Run independent agents in parallel and in the background, and brief each with exact file paths and slugs.
- Check every agent's output against the rules in CONVENTIONS.md before reporting it as done (spot-check facts and sources).
- Anything external (publish, send, post, change Trello/Webflow) needs explicit user approval in this conversation.
