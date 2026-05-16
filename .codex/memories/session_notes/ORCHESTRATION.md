# Orchestration Control — WealthLens HQ Multi-Session Workflow

> **PURPOSE**: This file is the master control document for an end-to-end autonomous workflow.
> It survives context compaction and tells any future Claude instance exactly where things stand.
>
> **INSTRUCTIONS FOR FUTURE CONTEXT**: If you are reading this after a compaction or session restart:
> 1. Read THIS file first.
> 2. Read `.codex/memories/00_ACTIVE.md` for project status.
> 3. Run `git branch -a` and `gh pr list --state open` to see branch/PR state.
> 4. Run `TaskList` to see in-conversation task progress.
> 5. Pick up from the **Current Phase** section below.
> 6. After completing work, UPDATE this file before the next compaction risk.

Last updated: 2026-05-15 (wave 6 complete — 28 PRs total, 6 waves, all reviewed x2)

## Workflow Design

### Branch Strategy (Stacked PRs)
```
main
 ├── chore/gitignore-cleanup          PR #? (independent)
 ├── fix/ons-was-pipeline-url         PR #? (independent)
 ├── feat/backend-api-enhancements    PR #? (independent)
 │    └── feat/frontend-wealth-chart  PR #? (stacked on backend-api-enhancements)
 └── feat/frontend-vitest-scaffold    PR #? (independent)
```

### Review Protocol (per PR)
1. Create PR with descriptive body
2. **Review Round 1**: Run 4 adversarial agents (code-reviewer, silent-failure-hunter, type-design-analyzer, pr-test-analyzer). Post comments on PR.
3. Fix all findings. Push fix commits.
4. **Review Round 2**: Re-run all agents. Confirm fixes. Post final comments.
5. Leave PR open (do NOT merge).

### Commit Convention
- `<area>: <imperative summary>`
- Small, logical commits grouped by domain
- Each commit independently reviewable

## Current Phase

**Phase: WAVE 6 COMPLETE** — 28 PRs total (waves 1-6), all reviewed x2 with fixes applied.

### Work Stream Status

| # | Stream | Branch | PR | Status | Review R1 | Fix R1 | Review R2 |
|---|--------|--------|----|--------|-----------|--------|-----------|
| 1 | Gitignore cleanup | `chore/gitignore-cleanup` | #11 | REVIEWED x2 | LGTM R2 | Fixed | LGTM |
| 2 | Backend API enhancements | `feat/backend-api-enhancements` | #13 | REVIEWED x2 | 19 tests pass | Fixed (cache, parity, NaN) | Clean, non-blocking notes |
| 3 | Frontend vitest scaffold | `feat/frontend-vitest-scaffold` | #12 | REVIEWED x2 | 14 tests pass | Fixed (res.ok, tsconfig) | Approved |
| 4 | Vue chart component | `feat/frontend-wealth-chart` | #15 | REVIEWED x2 | Build passes | Fixed (XSS, empty data, lazy, conditional) | Approved |
| 5 | ONS WAS pipeline fix | `fix/ons-was-pipeline-url` | #14 | REVIEWED x2 | 20 tests pass | Fixed (NaN cols, import) | Clean, non-blocking notes |

### Phase Sequence
1. [DONE] Create orchestration file
2. [DONE] Build streams 1, 2, 3, 5 in parallel (independent branches) — PRs #11, #12, #13, #14
3. [DONE] Build stream 4 (stacked on #13) — PR #15
4. [DONE] Run review round 1 on all PRs — findings posted as comments
5. [DONE] Fix all review findings — all fixes pushed
6. [DONE] Run review round 2 on all PRs — all approved or clean
7. [DONE] Audit repo, seed wave 2 tasks
8. [DONE] Build wave 2 PRs (7 PRs: #16-#22)
9. [DONE] Wave 2 review round 1 + fixes
10. [DONE] Wave 2 review round 2 — all PRs verified clean
11. [DONE] Audit for wave 3, seed tasks
12. [DONE] Build wave 3 PRs (6 PRs: #23-#28)
13. [DONE] Wave 3 review round 1 + fixes
14. [DONE] Wave 3 review round 2 — all 6 PRs verified LGTM
15. [DONE] Audit for wave 4, seed tasks
16. [DONE] Build wave 4 PRs (4 PRs: a11y, 404/error, tests, timeout config)
17. [DONE] Wave 4 review round 1 + fixes
18. [DONE] Wave 4 review round 2 — all 4 PRs verified LGTM
19. [DONE] Audit for wave 5, seed tasks
20. [DONE] Build wave 5 PRs (4 PRs: #33, #34, #35, #36)
21. [DONE] Wave 5 review round 1 + fixes
22. [DONE] Wave 5 review round 2 — all 4 PRs verified LGTM
23. [DONE] Audit for wave 6, seed tasks
24. [DONE] Build wave 6 PRs (2 PRs: #37, #38)
25. [DONE] Wave 6 review round 1 + fixes
26. [DONE] Wave 6 review round 2 — both PRs verified LGTM

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-15 | Use worktree isolation for parallel branch work | Keeps main clean, allows concurrent subagent work |
| 2026-05-15 | Stack frontend-wealth-chart on backend-api-enhancements | Chart component needs metadata endpoint for source citations |
| 2026-05-15 | Leave all PRs open, do not merge | Per user request — build on them for dependency resolution |

## Files Modified Tracker

Track which files each branch touches to detect conflicts early:

| Branch | Files touched |
|--------|--------------|
| chore/gitignore-cleanup | `.gitignore`, removal of `__pycache__/` tracked files |
| feat/backend-api-enhancements | `backend/app/routers/data.py`, `backend/app/main.py`, `tests/test_api.py` |
| feat/frontend-vitest-scaffold | `frontend/package.json`, `frontend/vitest.config.ts`, `frontend/src/**/*.test.ts` |
| feat/frontend-wealth-chart | `frontend/src/components/WealthSharesChart.vue`, `frontend/src/views/HomeView.vue`, `frontend/package.json` |
| fix/ons-was-pipeline-url | `automation/data-pipelines/fetch_ons_wealth.py`, possibly `data/processed/*.csv` |
| feat/frontend-additional-charts | `frontend/src/components/HousingAffordabilityChart.vue`, `CgtConcentrationChart.vue`, `ChartView.vue`, `DatasetCard.vue` |
| refactor/pipeline-logging | All files in `automation/data-pipelines/`, `automation/social-media/chart_to_social.py` |
| feat/health-data-endpoint | `backend/app/routers/data.py`, `tests/test_api.py` |
| feat/vite-manual-chunks | `frontend/vite.config.ts` |
| chore/prettierignore | `frontend/.prettierignore` |
| fix/extract-action-items | `automation/analysis/extract_action_items.py` |

## Recovery Checklist (After Compaction)

If context was compacted and you lost track:
1. `git branch -a` — see all branches
2. `gh pr list --state open` — see all open PRs
3. `git log --oneline -5` on each branch — see latest commits
4. Read this file for the status table
5. Read `TaskList` output for in-conversation progress
6. Continue from the first NOT STARTED or IN PROGRESS stream
7. After finishing a stream, update the status table in this file

## Subagent Dispatch Plan

For parallel work, dispatch these subagent types:
- **code-reviewer** (pr-review-toolkit:code-reviewer) — style, bugs, logic
- **silent-failure-hunter** (pr-review-toolkit:silent-failure-hunter) — error handling
- **type-design-analyzer** (pr-review-toolkit:type-design-analyzer) — type quality
- **pr-test-analyzer** (pr-review-toolkit:pr-test-analyzer) — test coverage gaps
- **Explore** — codebase research before implementation
- **general-purpose** — implementation in worktrees

## Wave 2 — Seeded from audit + R2 findings

| # | Stream | Branch | Base | PR | Status |
|---|--------|--------|------|----|--------|
| 6 | ESLint + Prettier | `feat/frontend-linting` | main | #22 | REVIEWED x2 — LGTM |
| 7 | Backend error handling | `fix/backend-error-handling` | feat/backend-api-enhancements | #20 | REVIEWED x2 — LGTM |
| 8 | ONS pipeline hardening | `fix/ons-pipeline-hardening` | fix/ons-was-pipeline-url | #19 | REVIEWED x2 — LGTM |
| 9 | WID API key to env var | `fix/wid-api-key-env` | main | #17 | REVIEWED x2 — LGTM |
| 10 | Extract Vue router | `refactor/extract-vue-router` | feat/frontend-wealth-chart | #18 | REVIEWED x2 — LGTM |
| 11 | CI use run_all.py | `fix/ci-use-pipeline-runner` | main | #16 | REVIEWED x2 — LGTM |
| 12 | CORS env-aware | `fix/cors-env-aware` | feat/backend-api-enhancements | #21 | REVIEWED x2 — LGTM (10 tests) |

## Audit Findings (2026-05-15)

Severity counts: 1 CRITICAL, 3 HIGH, 5 MEDIUM, 7 LOW (16 total)

### Must-fix (next wave PRs)
1. **CRITICAL** — WID API key hardcoded in `automation/data-pipelines/fetch_wid_data.py:28` — move to env var
2. **HIGH** — Missing ESLint + Prettier config in frontend (Makefile references them but no config exists)
3. **HIGH** — `automation/analysis/extract_action_items.py` is a stub with NotImplementedError
4. **MEDIUM** — GitHub Actions `weekly-data-update.yml` calls individual scripts instead of `run_all.py`
5. **MEDIUM** — CORS origins hardcoded for localhost only — need env-aware config
6. **MEDIUM** — Tests depend on actual data files, will fail without pipeline run

### Should-fix (quality improvements)
7. **LOW** — No `.env.example` file
8. **LOW** — Frontend missing eslint/prettier npm dependencies
9. **LOW** — Router setup embedded in `main.ts` instead of `src/router/index.ts`
10. **LOW** — Missing type definitions for WID API response
11. **LOW** — Hardcoded timeouts in pipeline fetch scripts
12. **LOW** — No `/health/data` endpoint checking CSV availability

### Already clear
- No TODO/FIXME/HACK comments found
- No secrets beyond the public WID key
- Vite proxy correctly configured
- All 4 pipelines have error handling

## Wave 3 — Seeded from inbox + audit + review findings

| # | Stream | Branch | Base | PR | Status |
|---|--------|--------|------|----|--------|
| 13 | Housing + CGT charts | `feat/frontend-additional-charts` | refactor/extract-vue-router | #25 | REVIEWED x2 — LGTM |
| 14 | Pipeline logging migration | `refactor/pipeline-logging` | fix/ons-pipeline-hardening | #28 | REVIEWED x2 — LGTM |
| 15 | Health/data endpoint | `feat/health-data-endpoint` | fix/backend-error-handling | #27 | REVIEWED x2 — LGTM |
| 16 | Vite manual chunks | `feat/vite-manual-chunks` | refactor/extract-vue-router | #24 | REVIEWED x2 — LGTM |
| 17 | .prettierignore | `chore/prettierignore` | feat/frontend-linting | #23 | REVIEWED x2 — LGTM |
| 18 | Extract action items | `fix/extract-action-items` | main | #26 | REVIEWED x2 — LGTM |

### Wave 3 stacking

```
main
 ├── fix/ons-was-pipeline-url (#14)
 │    └── fix/ons-pipeline-hardening (#19)
 │         └── refactor/pipeline-logging (NEW)
 ├── feat/backend-api-enhancements (#13)
 │    ├── fix/backend-error-handling (#20)
 │    │    └── feat/health-data-endpoint (NEW)
 │    └── feat/frontend-wealth-chart (#15)
 │         └── refactor/extract-vue-router (#18)
 │              ├── feat/frontend-additional-charts (NEW)
 │              └── feat/vite-manual-chunks (NEW)
 ├── feat/frontend-linting (#22)
 │    └── chore/prettierignore (NEW)
 └── fix/extract-action-items (NEW, independent)
```

## Wave 4 — Seeded from wave 3 audit (accessibility, testing, config)

| # | Stream | Branch | Base | PR | Status |
|---|--------|--------|------|----|--------|
| 19 | Frontend a11y | `feat/frontend-a11y` | feat/frontend-additional-charts | #29 | REVIEWED x2 — LGTM |
| 20 | 404 + error boundary | `feat/frontend-error-handling` | feat/frontend-a11y | #32 | REVIEWED x2 — LGTM |
| 21 | Action items tests | `tests/action-items-tests` | fix/extract-action-items | #31 | REVIEWED x2 — LGTM |
| 22 | Pipeline timeout config | `fix/pipeline-timeout-config` | refactor/pipeline-logging | #30 | REVIEWED x2 — LGTM |

### Wave 4 stacking
```
feat/frontend-additional-charts (#25)
 └── feat/frontend-a11y (NEW)
      └── feat/frontend-error-handling (NEW, blocked)

fix/extract-action-items (#26)
 └── tests/action-items-tests (NEW)

refactor/pipeline-logging (#28)
 └── fix/pipeline-timeout-config (NEW)
```

## Wave 5 — Seeded from wave 4 audit (error handling, API quality, DX)

| # | Stream | Branch | Base | PR | Status |
|---|--------|--------|------|----|--------|
| 23 | Store error handling | `fix/store-error-handling` | feat/frontend-error-handling | #33 | REVIEWED x2 — LGTM |
| 24 | Backend response models | `feat/backend-response-models` | feat/health-data-endpoint | #36 | REVIEWED x2 — LGTM |
| 25 | .env.example files | `chore/env-example` | main | #35 | REVIEWED x2 — LGTM |
| 26 | CI frontend workflow | `feat/ci-frontend` | main | #34 | REVIEWED x2 — LGTM |

### Wave 5 stacking
```
feat/frontend-error-handling (#32)
 └── fix/store-error-handling (NEW)

feat/health-data-endpoint (#27)
 └── feat/backend-response-models (NEW)

main
 ├── chore/env-example (NEW, independent)
 └── feat/ci-frontend (NEW, independent)
```

## Wave 6 — Seeded from wave 5 audit (chart completion, backend CI)

| # | Stream | Branch | Base | PR | Status |
|---|--------|--------|------|----|--------|
| 27 | Wealth by decile chart | `feat/wealth-by-decile-chart` | fix/store-error-handling | #38 | REVIEWED x2 — LGTM |
| 28 | CI backend workflow | `feat/ci-backend` | main | #37 | REVIEWED x2 — LGTM |

### Wave 6 stacking
```
fix/store-error-handling (#33)
 └── feat/wealth-by-decile-chart (NEW)

main
 └── feat/ci-backend (NEW, independent)
```

## Notes

- Windows 10 Pro environment — Bash tool uses Git Bash, not PowerShell
- Python 3.11+, Node via npm
- Tests: pytest (backend), vitest (frontend — being added)
- Linting: ruff (Python), vue-tsc (TypeScript)
- Solo dev repo — amend/rebase/reset allowed per user preference
