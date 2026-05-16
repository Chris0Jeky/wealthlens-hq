# WealthLens HQ — Active Status Board

> Single source of truth for current focus areas. Read this first after `AGENTS.md`.
>
> **POST-MERGE CLEANUP COMPLETE** (2026-05-16): All 192 PRs handled, 874 tests passing, CI green, 496 stale branches deleted.
> Merge history: [MERGE_ORCHESTRATION.md](.codex/memories/session_notes/MERGE_ORCHESTRATION.md) | PR creation history: [ORCHESTRATION.md](.codex/memories/session_notes/ORCHESTRATION.md) (archived)

Last updated: 2026-05-16

## Current phase: Ready to Ship — Feature Complete v0.1

All code is on main. Site live. No open PRs. No stale branches. Codebase includes:
- 10 data pipelines (WID, ONS housing, CGT, wealth-by-decile, productivity-pay, GDHI, tax composition, BoE rates, child poverty, generational wealth)
- Vue 3 frontend: 40+ components/composables, dark mode, broadsheet chart redesign, WCAG AA, analytics
- FastAPI backend: health, data, metadata, columns, summary stats, CSV download, security headers, GZip, rate limiting
- 874 tests passing (156 root + 135 backend + 583 frontend)
- CI/CD: ruff, mypy, bandit, pytest, ESLint, vue-tsc, vitest, vite build — all green
- Deployment: GitHub Pages auto-deploy on push to main

### Active focus areas

| Area | Status | Next step |
| --- | --- | --- |
| Data pipelines | 8+ pipelines on main | Maintain; add new pipelines as needed |
| Charts (v0.1) | Live (4 charts + broadsheet redesign) | Build more chart components in Vue |
| Backend API | Full-featured (health, data, metadata, columns, CSV, summary stats) | Deploy to staging |
| Frontend | Vue 3 + TS + Pinia + TailwindCSS with dark mode, a11y, analytics | Wire up remaining chart components |
| Deployment | Live at chris0jeky.github.io/wealthlens-hq/ | Automatic on push to main |
| Testing | 874 tests passing (156 root + 135 backend + 583 frontend) | Maintain coverage |
| CI/CD | All green — Backend + Frontend + CodeQL + Deploy + weekly-update | Monitor for failures |
| Social assets | chart_to_social.py generates 4 platform sizes | Generate assets for first LinkedIn post |
| Social accounts | Twitter/X + Bluesky created | Update LinkedIn profile, write first post |
| Outreach | Emails sent to mySociety + Democracy Club | Follow up |
| GitHub Issues | Previously created (good first issue + help wanted) | Share in first LinkedIn post |
| Reading | *The Trading Game* started | Continue; start Piketty when it arrives |
| Newsletters | 5 subscribed | Ongoing — read and note insights |

### Recent activity

- 2026-05-16: **REPO CLEANUP** — deleted 496 stale branches (292 local + 204 remote), updated all docs
- 2026-05-16: Post-merge health check — all CI green, 874 tests passing
- 2026-05-16: Merge session complete — 192 PRs handled (155 merged, 21 closed, 10 Dependabot, 6 deferred)
- 2026-05-16: Deployed Vue frontend to GitHub Pages as master site
- 2026-05-15: Scaffolded FastAPI backend + Vue 3 frontend; deployed v0.1 with 4 charts

### Guardrails snapshot

- No production deployment yet — all changes are local/greenfield.
- Data integrity: every dataset cites source, URL, and access date.
- Open source: all code will be public. Never commit secrets.
- Volunteers will read this code — clarity over cleverness.

### Best next actions

1. Update LinkedIn profile (headline, about, featured) — link to live site
2. Write and publish first LinkedIn post — "Why I'm building WealthLens UK"
3. Wire up first Vue chart component using the data store + API
4. Make first open-source PR to mySociety, Democracy Club, or TJN repos
5. Send outreach emails now unblocked by v0.1 deployment (TJN, Equality Trust, Gary Stevenson)
6. Handle deferred major dependency upgrades (pandas 3, TypeScript 6, Vite 8) when ready
7. Deploy backend to staging environment
