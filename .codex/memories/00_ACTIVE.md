# WealthLens HQ — Active Status Board

> Single source of truth for current focus areas. Read this first after `AGENTS.md`.

Last updated: 2026-05-14

## Current phase: Foundation → First Deploy

The project has moved from pure scaffolding to having real data pipelines and charts. Three interactive Plotly visualisations exist locally. Next milestone: live URL.

### Active focus areas

| Area | Status | Next step |
| --- | --- | --- |
| Data pipelines | Done (3 scripts) | Maintain; add more datasets after deploy |
| Charts (v0.1) | Done (3 charts, local) | Fix CGT nan% bug, add index.html, deploy |
| Deployment | Not started | Deploy to GitHub Pages or Cloudflare Pages |
| Social accounts | Twitter/X + Bluesky created | Update LinkedIn profile, write first post |
| Outreach | Emails sent to mySociety + Democracy Club | Wait for replies, follow up 2026-05-21 |
| Reading | *The Trading Game* started | Continue; start Piketty when it arrives |
| Newsletters | 5 subscribed | Ongoing — read and note insights |
| Research consolidation | Done | Maintained in `research/synthesised/` |
| Contributing guide | Not started | Draft after v0.1 deploy |

### Recent activity

- 2026-05-14: Built 3 data pipelines (WID, ONS housing, HMRC CGT) with reproducible fetch/process/chart workflow
- 2026-05-14: Generated 3 interactive Plotly charts in `projects/wealthlens-dashboard/charts/`
- 2026-05-14: Created Twitter/X and Bluesky accounts
- 2026-05-14: Sent volunteer emails to Democracy Club and mySociety
- 2026-05-14: Subscribed to 5 key newsletters
- 2026-05-14: Ordered books (*The Trading Game*, *A Brief History of Equality*)
- 2026-05-14: Added combined UK wealth inequality research
- 2026-05-14: Added operating scaffold (strategy, vision, identity, tasks)
- 2026-05-14: Configured agent guidance and settings

### Guardrails snapshot

- No production deployment yet — all changes are local/greenfield.
- Data integrity: every dataset cites source, URL, and access date. All 3 charts have source annotations.
- Open source: all code will be public. Never commit secrets.
- Volunteers will read this code — clarity over cleverness.

### Best next actions

1. Fix CGT chart nan% display bug and create index.html for charts directory
2. Deploy v0.1 to GitHub Pages or Cloudflare Pages — get a live URL
3. Update LinkedIn profile (headline, about, featured)
4. Write and publish first LinkedIn post
5. Find good-first-issue in mySociety or Democracy Club repos for first PR
