# WealthLens HQ — Active Status Board

> Single source of truth for current focus areas. Read this first after `AGENTS.md`.
>
> **ACTIVE ORCHESTRATION SESSION**: An end-to-end autonomous workflow is in progress.
> Read [`.codex/memories/session_notes/ORCHESTRATION.md`](.codex/memories/session_notes/ORCHESTRATION.md) for branch status, PR tracking, review rounds, and recovery instructions.
> That file is the master control document — update it as work progresses.

Last updated: 2026-05-15

## Current phase: v0.1 Live → Dashboard Build-out & Visibility

The project is live at https://chris0jeky.github.io/wealthlens-hq/ with 4 interactive charts, automated deploy, and weekly data update workflows. Backend API and Vue 3 frontend are now scaffolded. Next steps: LinkedIn presence, first open-source PR, chart components in Vue, and frontend redesign.

### Active focus areas

| Area | Status | Next step |
| --- | --- | --- |
| Data pipelines | Done (4 scripts + validator + runner) | Maintain; find correct ONS WAS XLSX URL; add new pipelines |
| Charts (v0.1) | Live (4 charts + index, accessible HTML) | Add charts as frontend redesign progresses |
| Backend API | FastAPI scaffold live (health + 4 data endpoints) | Add metadata endpoint, pagination |
| Frontend | Vue 3 + TS + Pinia + TailwindCSS scaffold (builds clean) | Wire up chart components, connect to API |
| Deployment | Live at chris0jeky.github.io/wealthlens-hq/ | Automatic on push to main |
| Testing | 32 tests passing (pipelines, API, chart_html, validation) | Add frontend tests (vitest) |
| CI/CD | Deploy + weekly-update workflows created | Verify workflows after first push |
| Social assets | chart_to_social.py generates 4 platform sizes | Generate assets for first LinkedIn post |
| Social accounts | Twitter/X + Bluesky created | Update LinkedIn profile, write first post |
| Outreach | Emails sent to mySociety + Democracy Club | Wait for replies, follow up 2026-05-21 |
| GitHub Issues | 10 issues created (good first issue + help wanted) | Share in first LinkedIn post |
| Frontend redesign | `docs/redesign/` ready for briefs | Awaiting design instructions |
| Reading | *The Trading Game* started | Continue; start Piketty when it arrives |
| Newsletters | 5 subscribed | Ongoing — read and note insights |

### Recent activity

- 2026-05-15: Scaffolded Vue 3 + TypeScript + Pinia + TailwindCSS frontend (builds clean)
- 2026-05-15: Scaffolded FastAPI backend with /health and /api/data/{name} endpoints (8 API tests)
- 2026-05-15: Added tests for all 4 pipelines + chart_html + validation (32 tests total, up from 7)
- 2026-05-15: Implemented chart_to_social.py — generates PNG images at 4 social media sizes
- 2026-05-15: Added CSV data validation module with make validate target
- 2026-05-15: Added cross-platform pipeline runner (run_all.py)
- 2026-05-15: Fixed all ruff lint issues, added types-requests to dev deps
- 2026-05-15: Updated CONTRIBUTING.md with real dev setup instructions
- 2026-05-15: Created 10 GitHub Issues with good-first-issue labels
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
2. Write and publish first LinkedIn post — "Why I'm building WealthLens UK" (include GitHub Issues link)
3. Wire up first Vue chart component using the data store + API
4. Find good-first-issue in mySociety or Democracy Club repos for first PR
5. Find correct ONS Wealth and Assets Survey XLSX URL (current one 404s)
6. Add vitest frontend test scaffold
7. Begin frontend redesign when instructions arrive
