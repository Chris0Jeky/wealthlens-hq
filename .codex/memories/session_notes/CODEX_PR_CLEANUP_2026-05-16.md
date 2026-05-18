# Codex PR Cleanup Sweep - 2026-05-16

Last updated: 2026-05-17T13:30+01:00

## Scope

User requested a systematic cleanup of open PRs, branch/worktree state, CI/tests, bot comments, review status, docs, and outstanding tasks. Merges are allowed only for PRs with 2 adversarial reviews, bot comments addressed, and green CI/tests.

## Verified Starting State

- Current checkout: `feat/dataset-search`
- Open PRs: 41 (`#232`-`#272`)
- Docs conflict:
  - `.codex/memories/00_ACTIVE.md` and `MERGE_ORCHESTRATION.md` claim zero open PRs.
  - GitHub live state shows 41 open PRs.
  - `.codex/memories/session_notes/ORCHESTRATION.md` is stale after Wave 2 and does not include PRs through `#272`.
- Local dirty state after first fix:
  - Only untracked files remain:
    - malformed temp file `CUsersjekytsourcewealthlens-hq.claudelocalbase_chartview_b64.txt`
    - `projects/wealthlens-dashboard/frontend/src/components/WealthScaleScroller.vue`
    - `projects/wealthlens-dashboard/frontend/src/components/__tests__/WealthScaleScroller.test.ts`
- Active/locked worktrees:
  - `.claude/worktrees/agent-a3d865ff7df10ee30` on `feat/wage-stagnation-chart`
  - `.claude/worktrees/agent-aa8810991d3a0798a` on `worktree-agent-aa8810991d3a0798a`
  - `.claude/worktrees/agent-ab60b9747ad729f35` on `feat/loading-ux-polish`

## CI Red/Needs Attention

- All previously red checks are green as of 2026-05-17T00:20+01:00:
  - `#238` `feat/og-meta-tags`
  - `#244` `chore/test-coverage-reporting`
  - `#247` `feat/chart-export`
  - `#250` `fix/bandit-enforcement`
  - `#256` `chore/lighthouse-ci`
  - `#260` `test/playwright-e2e`
  - `#263` `feat/inheritance-tax-chart`
  - `#267` `feat/faq-glossary`
  - `#268` `feat/wealth-scale-scroller`
  - `#269` `feat/dataset-search`
  - `#270` `feat/og-image-generation`
  - `#272` `feat/loading-ux-polish`
- `#239` `feat/chart-article-pages`: no checks because it is stacked on `feat/new-chart-components`.

## Work Completed

- `#269`: fixed unused `isSearchActive` import causing CI lint failure.
- `#269`: tightened combobox ARIA behavior in `DatasetSearch.vue`:
  - `aria-expanded` reflects active search state.
  - `aria-controls` only points to result list when active.
  - `aria-activedescendant` only set when active.
  - input has `maxlength="200"`.
- `#269`: updated DatasetSearch test expectation.
- Verification for `#269`:
  - `npm run lint -- src/components/DatasetSearch.vue src/views/HomeView.vue src/components/__tests__/DatasetSearch.test.ts` passed with warnings only.
  - `npm run test -- src/components/__tests__/DatasetSearch.test.ts` passed: 20 tests.
- Fixed and pushed CI/security/test repairs for:
  - `#238` commit `5be94ea`: removed `v-html` injection sinks from `ChartView.vue`.
  - `#244` commit `5549425`: synced coverage provider lockfile.
  - `#247` commits `ccf333f`, `7d6b4bd`: typed chart export test mocks and refs.
  - `#250` commit `ccaff3a`: documented trusted subprocess calls for Bandit.
  - `#256` commits `2d5a113`, `423bceb`: run LHCI against Vite preview with Pages base path.
  - `#260` commit `4a281cd`: exact Playwright nav link locator.
  - `#263` commit `700590c`: typed inheritance tax fetch mock.
  - `#267` commit `a2d6824`: route count aligned with FAQ route.
  - `#268` commit `4be81a9`: removed unused ResizeObserver test parameter.
  - `#270` commit `b450455`: type OG image layouts with satori.
  - `#272` commit `9fc369d`: hardened loading UX cleanup and typed mocks.
- Merged reviewed/green PRs:
  - `#233` `feat/wealth-shares-static-data`
  - `#234` `feat/new-chart-components`
  - `#232` `feat/home-dashboard-cards`
  - `#236` `feat/data-sources-page`
  - `#235` `test/e2e-chart-data-flow`
  - `#237` `feat/api-version-health`
  - `#238` `feat/og-meta-tags`
  - `#240` `perf/route-code-splitting`
  - `#241` `worktree-agent-a5176bcc1a1983a86`
  - `#242` `feat/dataset-freshness-tracking`
  - `#239` `feat/chart-article-pages`
- R1 repair commits pushed after crash recovery:
  - `#243` commit `f44deb6`: added root `CODE_OF_CONDUCT.md`; verified `ContributeView.test.ts` (8 tests) and frontend typecheck.
  - `#254` commit `e5a2335`: blank wealth comparison inputs now remain invalid instead of parsing as `0`; verified `WealthCalculatorCompare.test.ts` (26 tests) and frontend typecheck.
  - `#246` commit `dc6a82a`: rate limiting now defaults OFF behind `RATE_LIMIT_ENABLED=true`; worker verified rate-limit/health tests, full backend pytest, ruff, mypy, and diff check.
  - `#247` commit `8a06d90`: chart components now expose their `VChart` instances for PNG/SVG export instead of leaving `chartComponentRef` empty; verified export/chart component tests (53 tests) and frontend typecheck.
  - `#249` commit `c24d8ab`: switched Buttondown embedded-form POST to the official `buttondown.com` endpoint, added `embed=1`, and replaced `AbortSignal.any/timeout` with an `AbortController` timeout fallback; verified newsletter tests (14 tests) and frontend typecheck.
  - `#259` commit `3bf0d12`: updated income-tax band calculation to keep the basic band at £37,700 after personal-allowance taper and updated CGT comparison to current 18%/24% rates; verified tax utility/component tests (39 tests) and frontend typecheck.
  - `#264` commit `c32dc35`: upgraded `vue-i18n` to `^11.4.2`, added guarded browser storage utilities, and hardened i18n/theme storage paths; worker verified targeted tests (33 tests), typecheck, build, and lint with existing warnings.
  - `#266` commits `b52ab98`, `2c57c41`: sourced/corrected wealth-tax simulator estimates, added source URLs/access dates and docs data-licence entries, and merged current main; worker verified targeted simulator/router tests (57 tests), typecheck, lint with existing warnings, diff check, and green GitHub checks.
  - `#269` commit `b548a8b`: expanded dataset search metadata to all 10 public datasets and wired active search filters into the HomeView dataset grid; verified DatasetSearch/HomeView tests (29 tests) and frontend typecheck.
  - `#270` merge from `origin/main` plus commit `ee8f2ee`: added OG metadata and generated PNGs for the six chart slugs added on main so CI no longer expects missing files; verified OG generation, OG image tests (26 tests), and frontend typecheck.
  - `#271` commits `353d66a`, `733b115`: registered the wage-stagnation dataset in the backend, added the processed CSV, and changed the ECharts shading to a silent stacked gap band between actual and counterfactual lines; verified WageStag/ChartComponents tests (38 tests), frontend typecheck, and backend wage-stagnation tests (3 tests).
- Merge-up conflict fixes:
  - `#238`: merged current `main`, preserving meta tags plus async chart load fallbacks.
  - `#240`: merged current `main` twice, preserving route prefetch plus meta tags.
  - `#242`: merged current `main` twice, preserving freshness, route prefetch, and meta tags.
  - `#239`: retargeted from `feat/new-chart-components` to `main`, merged current `main`, fixed `chartArticles.ts` section keys from `headlineEmphasis` to `headingEmphasis`, and verified local `typecheck`, targeted lint/tests, and frontend build.

## Merge Gate Snapshot

- `#232`-`#242`: merged after green checks and owner R1/R2 review comments. `#239` required retarget + CI repair before merge.
- `#243`-`#272`: green before the first merge wave, but no owner R1/R2 review comments found. They require the adversarial review workflow before merge and may now need merge-ups because `main` advanced.
- Bot comments on recent PRs are mostly Gemini quota warnings, Copilot review errors, and Codex review suggestions. Treat quota/error notices as non-actionable bot status; Codex suggestions must be checked against the diff/review findings before a PR is considered clean.

## R1 Adversarial Findings for PRs #243-#272

- PASS R1, no blocking findings: `#248`, `#250`, `#251`, `#253`, `#255`, `#260`, `#261`, `#262`, `#267`.
- BLOCK R1:
  - `#243`: `ContributeView.vue` links to missing `CODE_OF_CONDUCT.md`.
  - `#244`: backend CI has non-gating tests via `|| true`; `pytest-cov>=6.0` shell argument is unquoted.
  - `#245`: methodology/privacy copy says no third-party tracking scripts, conflicting with optional Plausible.
  - `#246`: rate limiting defaults on at 60 RPM, violating default-off new behavior rule.
  - `#247`: merge dirty; chart export refs do not expose chart instances, making export a no-op.
  - `#249`: merge dirty; Buttondown endpoint host appears wrong; `AbortSignal.any/timeout` lacks fallback.
  - `#252`: sitemap generation includes only 4 chart slugs and omits `/data-sources`.
  - `#254`: compare mode treats blank wealth fields as `0`, enabling misleading comparison.
  - `#256`: `npm run lighthouse` depends on a globally-installed LHCI CLI, not project deps.
  - `#257`: service worker network-first API check uses `/wealthlens-hq/api/` while app requests `/api/...`.
  - `#258`: freshness fetch bypasses Vite base path; date parsing can shift local calendar date.
  - `#259`: tax calculator applies income bands to gross thresholds after allowance taper; CGT rates are stale for post-2024-10-30 disposals.
  - `#263`: inheritance tax chart rejects valid `liability_rate_pct: 0`.
  - `#264`: `vue-i18n@^10.0.8` is deprecated/EOL; localStorage access lacks try/catch.
  - `#265`: architecture docs overstate `make ci-quick`; dataset onboarding omits `DATASET_META`.
  - `#266`: wealth-tax simulator low-threshold estimate understates empirical threshold data and lacks URLs/access dates for cited estimates.
  - `#268`: `ResizeObserver` is constructed unguarded.
  - `#269`: dataset search index/grid filtering omits datasets or does not filter main grid.
  - `#270`: OG image script test uses `__dirname` under ESM; partial font cache can crash generation; metadata access dates are inconsistent.
  - `#271`: wage stagnation chart has no backend/static dataset registration and shades to baseline instead of the actual/counterfactual gap.
  - `#272`: `useMinLoadingTime` lacks `immediate`; failed images remain hidden and busy forever.

## Open Classifications

- Blocker: live PR state contradicts status docs.
- Blocker before merge: `#243`-`#272` do not yet have the required two adversarial owner review rounds.
- Non-blocking risk: local untracked `WealthScaleScroller` files appear to be incorrectly copied into the dataset-search checkout; preserve until `#268` is inspected.
- Non-blocking risk: `feat/wage-stagnation-chart` worktree still has a pre-existing uncommitted `package-lock.json` license-only diff from an earlier install; it was not included in the repair commits.
- Non-blocking risk: `npm run test:unit` does not exist; use `npm run test -- <path>` for frontend targeted tests.
- Tool failure: six spawned review agents after crash returned `not_found`; no review results should be inferred from them.
- GitHub API condition: GraphQL bucket was exhausted at 2026-05-17T00:40+01:00 and reset was reported for 2026-05-17T00:54+01:00. REST/core quota remained available and was used for #239 checks and merge.

## Next Steps

1. Finish subagent inventories:
   - PR review/comment/bot status.
   - Worktree/branch cleanup hazards.
   - CI failure root causes.
2. Fix red checks branch-by-branch, avoiding unrelated local untracked files.
3. Verify bot comments are addressed.
4. Run/record adversarial review workflow for `#243`-`#272`.
5. Fix R1 findings and merge-up conflicts caused by the advanced `main`.
6. Post R2 verification comments after fixes.
7. Merge only PRs that meet the stated gate.
8. Update stale status docs.

## Final Resume Status - 2026-05-17

- Open PRs: none (`gh pr list --state open` returned `[]`).
- Merged after resume: `#270`, `#271`, and `#272`.
- Final main merge commit checked: `1f5318e` (`Merge pull request #272 from Chris0Jeky/feat/loading-ux-polish`).
- Latest relevant main workflows: CI Backend on backend-affecting merge `09c4ea5` completed successfully; CI Frontend, CodeQL, E2E Tests, Lighthouse CI, and Deploy to GitHub Pages on latest merge `1f5318e` completed successfully.
- `#270` repairs: completed package/vitest conflict resolution, preserved Playwright/Lighthouse/sitemap dependencies, added missing inheritance-tax OG metadata and image, removed generated JS shadows before committing, and merged after green checks.
- `#271` repairs: committed package-lock license metadata, resolved chart registry conflicts to preserve both `wage-stagnation` and `inheritance-tax`, added missing wage-stagnation OG metadata/image, replaced the backend version endpoint's `git` subprocess fallback with direct `.git` metadata reads, and merged after green checks.
- `#272`: merged cleanly after the final queue check.
- Local verification run during final repairs:
  - `npm --prefix projects/wealthlens-dashboard/frontend run test -- src/components/__tests__/WageStagChart.test.ts src/components/__tests__/ChartComponents.test.ts src/views/__tests__/ViewComponents.test.ts` -> 92 passed.
  - `python -m pytest -q projects/wealthlens-dashboard/backend/tests/test_version.py projects/wealthlens-dashboard/backend/tests/test_wage_stagnation.py` -> 15 passed.
  - `python -m bandit -r projects/wealthlens-dashboard/backend/ -c pyproject.toml` -> no issues.
  - `python -m ruff check projects/wealthlens-dashboard/backend/ automation/ tests/` -> passed.
  - `python -m mypy projects/wealthlens-dashboard/backend/` -> passed.
  - `npm --prefix projects/wealthlens-dashboard/frontend run test -- --coverage` -> 106 files / 1125 tests passed.
  - `npm --prefix projects/wealthlens-dashboard/frontend run build` -> passed.
- Non-blocking follow-ups:
  - GitHub push banner still reports one low-severity Dependabot vulnerability on the default branch.
  - Frontend `npm install` reports four low-severity audit findings; no forced audit fix was applied because that can introduce breaking dependency changes.
  - Several local worktrees and generated/untracked artifacts remain in the workspace; they were preserved rather than destructively cleaned because the main checkout is on `feat/dataset-search` and has unrelated untracked files.
