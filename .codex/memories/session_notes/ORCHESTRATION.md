# Orchestration Control — WealthLens HQ Autonomous Workflow v2

> **PURPOSE**: Master control document for end-to-end autonomous development.
> Survives context compaction. Any future Claude instance picks up from here.
>
> **CRITICAL**: Update this file BEFORE every compaction risk (long tool calls, large diffs).

Last updated: 2026-05-16T19:00Z

## Recovery Checklist (READ FIRST after compaction or session restart)

1. Read THIS file completely.
2. Read `.codex/memories/00_ACTIVE.md` for project status.
3. Run `git branch -a` and `gh pr list --state open` to see branch/PR state.
4. Run `TaskList` to see in-conversation task progress.
5. Pick up from the **Current Phase** section below.
6. After completing any stream, UPDATE this file before continuing.
7. Use `/loop` to keep the workflow alive across turns.

## Workflow Design

### Principles
- **Small commits**: One logical change per commit. Each independently reviewable.
- **Worktree isolation**: Each stream gets its own worktree via `Agent(isolation: "worktree")`.
- **Stacked branches**: When stream B depends on stream A, base B on A's branch.
- **2 adversarial review rounds per PR**: Round 1 finds issues → fix → Round 2 confirms.
- **Never merge**: Leave all PRs open. Stack new work on top of them.
- **Continuous seeding**: When task queue empties, audit and seed new tasks.
- **Docs sync**: Update orchestration after every stream completion.

### Branch Naming Convention
```
<type>/<short-description>
```
Types: feat, fix, refactor, test, chore, docs

### Review Protocol (per PR)
1. Create PR with descriptive body (## Summary + ## Test plan)
2. **Review Round 1**: Run 4 adversarial agents in parallel:
   - `pr-review-toolkit:code-reviewer` — bugs, logic, style
   - `pr-review-toolkit:silent-failure-hunter` — error handling, swallowed errors
   - `pr-review-toolkit:type-design-analyzer` — type quality, invariants
   - `pr-review-toolkit:pr-test-analyzer` — test coverage gaps
3. Post findings as PR comments.
4. Fix all findings. Push fix commits.
5. **Review Round 2**: Re-run all 4 agents. Confirm fixes. Post final approval.
6. Check CI status (gh pr checks). Fix any failures.
7. Update this file with final status.

### Stacking Strategy
```
main
 ├── feat/wealth-shares-static-data      PR #? (independent — quick fix)
 ├── feat/new-chart-components           PR #? (independent — 6 new charts)
 │    └── feat/chart-article-pages       PR #? (stacked — broadsheet pages for new charts)
 ├── feat/home-dashboard-cards           PR #? (independent — HomeView shows all datasets)
 ├── feat/data-sources-page              PR #? (independent — public data provenance page)
 └── test/e2e-chart-data-flow            PR #? (independent — integration tests)
```

## Current Phase

**Phase: WAVE 2 R2 IN FLIGHT — WAVE 1 COMPLETE**

### Wave 1 Streams

| # | Stream | Branch | Base | PR | Status | R1 | R2 |
|---|--------|--------|------|----|--------|----|----|
| 1 | Add wealth-shares.json static fallback | `feat/wealth-shares-static-data` | main | #233 | R2 APPROVED ✓ | Reworked: real data from CSV | APPROVED |
| 2 | New chart components (6 datasets) | `feat/new-chart-components` | main | #234 | R2 APPROVED ✓ | Fixed: MarkLine, contrast, async errors, NaN warnings | APPROVED |
| 3 | HomeView dashboard with dataset cards | `feat/home-dashboard-cards` | main | #232 | R2 APPROVED ✓ | Fixed: race condition, decoupled cards, connectivity warning | APPROVED |
| 4 | Data sources public page | `feat/data-sources-page` | main | #236 | R2 APPROVED ✓ | Clean pass | APPROVED |
| 5 | E2E chart data flow tests | `test/e2e-chart-data-flow` | main | #235 | R2 APPROVED ✓ | Lint fix pushed, no blocking issues | APPROVED |

### Wave 2 Streams

| # | Stream | Branch | Base | PR | Status | R1 | R2 |
|---|--------|--------|------|----|--------|----|----|
| 6 | Broadsheet article pages for new charts | `feat/chart-article-pages` | feat/new-chart-components | #239 | FIXED | activeRange bug, [verify] markers, file size → fixed | PENDING |
| 7 | Social OG meta tags for chart pages | `feat/og-meta-tags` | main | #238 | FIXED | Multi-instance conflict, SSR guard, stale tags → fixed | PENDING |
| 8 | API version endpoint + health widget | `feat/api-version-health` | main | #237 | FIXED | Security leak, breaking compat, AbortController → fixed | PENDING |

### Wave 3 Streams (to start after Wave 2 R2)

| # | Stream | Branch | Base | PR | Status | R1 | R2 |
|---|--------|--------|------|----|--------|----|----|
| 9 | Embed/share widget for charts | `feat/chart-embed-share` | main | — | NOT STARTED | — | — |
| 10 | Performance: route-level code splitting | `perf/route-code-splitting` | main | — | NOT STARTED | — | — |
| 11 | Backend: dataset freshness tracking | `feat/dataset-freshness` | main | — | NOT STARTED | — | ��� |

### Wave 4+ (future)
- Major dep upgrades (pandas 3, TypeScript 6, Vite 8)
- Wealth calculator enhancements
- Email subscription widget (Buttondown)
- Accessibility audit automation

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-16 | Start with static data gap fix | Quick win, unblocks offline dev |
| 2026-05-16 | Build 6 new chart components before article pages | Components are prerequisite for pages |
| 2026-05-16 | Leave all PRs open, stack on them | Per user request |

## Context for Each Stream

### Stream 1: wealth-shares static data
The wealth-shares chart has no static JSON fallback in `/public/data/`. All other 9 datasets have one. Generate it from the pipeline CSV or backend and add to `/public/data/wealth-shares.json`.

### Stream 2: New chart components
6 datasets have API endpoints + static data but NO chart component:
- productivity-pay → ProductivityPayChart.vue (scissor/line chart)
- gdhi-by-region → GdhiByRegionChart.vue (bar/map chart)
- tax-composition → TaxCompositionChart.vue (stacked bar/pie)
- boe-rates → BoeRatesChart.vue (line chart, time series)
- child-poverty → ChildPovertyChart.vue (choropleth/bar)
- generational-wealth → GenerationalWealthChart.vue (grouped bar)

Each needs: component file, route entry, ChartView config, test file.

### Stream 3: HomeView dashboard
HomeView should show DatasetCards for all 10 datasets with real metadata from the API. Currently may be using hardcoded data or incomplete list.

### Stream 4: Data sources page
Public page at /data-sources showing all dataset provenance: source name, URL, licence, update frequency, access date. Uses metadata from backend.

### Stream 5: E2E tests
Integration tests that verify the full data flow: API serves data → store fetches → composable provides → chart renders.

## Subagent Dispatch Reference

```
# Implementation (in worktree)
Agent(subagent_type="general-purpose", isolation="worktree", prompt="...")

# Review Round 1 (4 agents in parallel)
Agent(subagent_type="pr-review-toolkit:code-reviewer", prompt="Review PR #N...")
Agent(subagent_type="pr-review-toolkit:silent-failure-hunter", prompt="Review PR #N...")
Agent(subagent_type="pr-review-toolkit:type-design-analyzer", prompt="Review PR #N...")
Agent(subagent_type="pr-review-toolkit:pr-test-analyzer", prompt="Review PR #N...")
```

## How to Update This File

After completing ANY stream:
1. Change its status in the table (NOT STARTED → IN PROGRESS → PR CREATED → R1 DONE → FIXING → R2 DONE)
2. Fill in the PR number once created
3. Note any blockers or surprises in the Decisions Log
4. If all streams in a wave are R2 DONE, seed the next wave
5. Timestamp the `Last updated` line

## End Condition

This workflow runs until:
- All seeded tasks are complete (R2 DONE)
- No more actionable tasks can be inferred from the codebase/inbox
- User explicitly stops it

If the task queue is empty: run an audit (lint, tests, coverage, accessibility, broken links, outdated deps, inbox review) and seed new streams from findings.
