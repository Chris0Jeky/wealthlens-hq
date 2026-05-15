# WealthLens HQ — Active Status Board

> Single source of truth for current focus areas. Read this first after `AGENTS.md`.

Last updated: 2026-05-15

## Current phase: v0.1 Live → Visibility & Outreach

The project is live at https://chris0jeky.github.io/wealthlens-hq/ with 4 interactive charts, automated deploy, and weekly data update workflows. Next steps: LinkedIn presence, first open-source PR, and frontend redesign.

### Active focus areas

| Area | Status | Next step |
| --- | --- | --- |
| Data pipelines | Done (4 scripts) | Maintain; find correct ONS WAS XLSX URL |
| Charts (v0.1) | Live (4 charts + index, accessible HTML) | Add charts as frontend redesign progresses |
| Deployment | Live at chris0jeky.github.io/wealthlens-hq/ | Automatic on push to main |
| Testing | 7 tests passing | Add tests for ONS housing and ONS wealth output |
| CI/CD | Deploy + weekly-update workflows created | Verify workflows after first push |
| Social accounts | Twitter/X + Bluesky created | Update LinkedIn profile, write first post |
| Outreach | Emails sent to mySociety + Democracy Club | Wait for replies, follow up 2026-05-21 |
| Frontend redesign | `docs/redesign/` ready for briefs | Awaiting design instructions |
| Reading | *The Trading Game* started | Continue; start Piketty when it arrives |
| Newsletters | 5 subscribed | Ongoing — read and note insights |

### Recent activity

- 2026-05-15: Deployed v0.1 to GitHub Pages — site live with 4 charts
- 2026-05-15: Fixed CGT chart nan% display bug for suppressed taxpayer bands
- 2026-05-15: Created charts/index.html landing page with mobile-responsive grid
- 2026-05-15: Added shared chart_html.py accessibility wrapper (lang, viewport, aria, skip link)
- 2026-05-15: Implemented 4th pipeline: ONS wealth-by-decile with graceful fallback
- 2026-05-15: Created GitHub Pages deploy workflow and weekly data update cron
- 2026-05-15: Added pyproject.toml, updated Makefile, created update_all.ps1
- 2026-05-15: Added pytest scaffold with 7 passing tests
- 2026-05-15: Rewrote README.md for public repo, added LICENSE (MIT), data-licences.md
- 2026-05-15: Added incremental commit discipline and stricter DoD to CLAUDE.md/AGENTS.md
- 2026-05-15: Created docs/redesign/ receiving directory for frontend redesign briefs
- 2026-05-14: Built 3 data pipelines (WID, ONS housing, HMRC CGT)
- 2026-05-14: Generated 3 interactive Plotly charts
- 2026-05-14: Created Twitter/X and Bluesky accounts
- 2026-05-14: Sent volunteer emails to Democracy Club and mySociety
- 2026-05-14: Added operating scaffold (strategy, vision, identity, tasks)

### Guardrails snapshot

- No production deployment yet — all changes are local/greenfield.
- Data integrity: every dataset cites source, URL, and access date. All 3 charts have source annotations.
- Open source: all code will be public. Never commit secrets.
- Volunteers will read this code — clarity over cleverness.

### Best next actions

1. Update LinkedIn profile (headline, about, featured) — link to live site
2. Write and publish first LinkedIn post — "Why I'm building WealthLens UK"
3. Find good-first-issue in mySociety or Democracy Club repos for first PR
4. Find correct ONS Wealth and Assets Survey XLSX URL (current one 404s)
5. Begin frontend redesign when instructions arrive
