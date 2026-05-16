# WealthLens HQ — Active Status Board

> Single source of truth for current focus areas. Read this first after `AGENTS.md`.
>
> **MERGE SESSION COMPLETE**: All ~192 PRs have been handled (merged or closed). Zero open PRs remain.
> See [`.codex/memories/session_notes/MERGE_ORCHESTRATION.md`](.codex/memories/session_notes/MERGE_ORCHESTRATION.md) for full merge history.
> See [`.codex/memories/session_notes/ORCHESTRATION.md`](.codex/memories/session_notes/ORCHESTRATION.md) for original PR creation/review history.

Last updated: 2026-05-16

## Current phase: Post-Merge Consolidation — CI Green

All feature PRs have been merged into main. Post-merge health check complete. The codebase now includes:
- 10 data pipelines (WID, ONS housing, CGT, wealth-by-decile, productivity-pay, GDHI, tax composition, BoE rates, child poverty, generational wealth)
- Vue 3 frontend with AppHeader/AppFooter, dark mode, broadsheet chart redesign, WCAG audit fixes
- FastAPI backend with security headers, GZip, rate limiting, error envelope, CSV download, summary stats, columns endpoint
- 874 tests passing (156 root + 135 backend + 583 frontend)
- CI/CD all green: ruff, mypy, bandit, pytest, ESLint, vue-tsc, vitest, vite build

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

- 2026-05-16: **POST-MERGE HEALTH CHECK COMPLETE** — all CI green, docs updated, 874 tests passing
- 2026-05-16: Fixed mypy errors (Starlette type suppression, generator fixture), added httpx to dev deps
- 2026-05-16: Fixed seed CSVs for CI (year ranges, region counts, decile labels, sort order, row counts)
- 2026-05-16: Fixed ruff lint in automation/ and tests/ (noqa for unicode ×, import sorting, unused vars)
- 2026-05-16: Updated dashboard README from stub to reflect actual state (10 datasets, API, 4 charts)
- 2026-05-16: **MERGE SESSION COMPLETE** — all ~192 PRs merged or closed, zero open PRs
- 2026-05-16: Fixed 15 test files to align with post-merge component structure (718 tests passing)
- 2026-05-16: Merged 10 Dependabot dependency bumps; closed 6 risky major version bumps
- 2026-05-16: Merged 13 remaining feature PRs (pipelines, analytics, WCAG audit, chart redesign)
- 2026-05-16: Merged 16 frontend feature PRs (API types, dark mode, About page, PWA manifest, etc.)
- 2026-05-16: Merged 10 backend feature PRs (security headers, GZip, error envelope, CSV download, etc.)
- 2026-05-16: Merged 10 test/docs/CI PRs
- 2026-05-16: Closed ~21 duplicate PRs (superseded by already-merged features)
- 2026-05-15: Scaffolded Vue 3 + TypeScript + Pinia + TailwindCSS frontend (builds clean)
- 2026-05-15: Scaffolded FastAPI backend with /health and /api/data/{name} endpoints
- 2026-05-15: Deployed v0.1 to GitHub Pages — site live with 4 charts

### Guardrails snapshot

- No production deployment yet — all changes are local/greenfield.
- Data integrity: every dataset cites source, URL, and access date.
- Open source: all code will be public. Never commit secrets.
- Volunteers will read this code — clarity over cleverness.

### Best next actions

1. Update LinkedIn profile (headline, about, featured) — link to live site
2. Write and publish first LinkedIn post — "Why I'm building WealthLens UK"
3. Wire up first Vue chart component using the data store + API
4. Find good-first-issue in mySociety or Democracy Club repos for first PR
5. Deploy backend to staging environment
6. Handle major dependency upgrades (pandas 3, TypeScript 6, Vite 8) when ready
7. Begin frontend redesign when instructions arrive
