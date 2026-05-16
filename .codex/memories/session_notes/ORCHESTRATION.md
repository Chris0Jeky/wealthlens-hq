# Orchestration Control — WealthLens HQ Autonomous Workflow v2

> **PURPOSE**: Master control document for end-to-end autonomous development.
> Survives context compaction. Any future Claude instance picks up from here.
>
> **CRITICAL**: Update this file BEFORE every compaction risk (long tool calls, large diffs).

Last updated: 2026-05-16T23:50Z

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
2. **Review Round 1**: Run adversarial code-reviewer agent
3. Fix all findings. Push fix commits.
4. **Review Round 2**: Re-run reviewer. Confirm fixes. Post final approval.
5. Check CI status (gh pr checks). Fix any failures.
6. Update this file with final status.

## Current Phase

**Phase: WAVE 8 — FIXING R1 + REVIEWING REMAINING**

### Waves 1-6: ALL R2 APPROVED ✓ (PRs #232-#260)

### Wave 7 Streams — ALL R2 APPROVED ✓

| # | Stream | Branch | Base | PR | Status | R1 | R2 |
|---|--------|--------|------|----|--------|----|----|
| 31 | Component test coverage (top 6 components) | `test/component-coverage` | main | #262 | R2 APPROVED ✓ | Fixed: added keyboard interaction tests | APPROVED |
| 32 | HealthBadge accessibility fix (color-only → icon+text) | `fix/healthbadge-accessibility` | main | #261 | R2 APPROVED ✓ | Fixed: focusable, dead code | APPROVED |
| 33 | Inheritance tax chart page | `feat/inheritance-tax-chart` | main | #263 | R2 APPROVED ✓ | Fixed: data validation, fetchWithRetry, contrast | APPROVED |
| 34 | i18n framework (vue-i18n) | `feat/i18n-setup` | main | #264 | R2 APPROVED ✓ | Fixed: unused t, localStorage persist, label i18n | APPROVED |
| 35 | Architecture docs + CONTRIBUTING | `docs/architecture-and-conduct` | main | #265 | R2 APPROVED ✓ | Fixed: paths, composable refs, e2e ref | APPROVED |
| 36 | Wealth tax revenue simulator with sliders | `feat/wealth-tax-simulator` | main | #266 | R2 APPROVED ✓ | Fixed: findIndex fallback, unused import | APPROVED |

### Wave 8 Streams

| # | Stream | Branch | Base | PR | Status | R1 | R2 |
|---|--------|--------|------|----|--------|----|----|
| 37 | "1 pixel = £1,000" wealth scale scroller | `feat/wealth-scale-scroller` | main | #268 | FIXING R1 | Invalid role, aria-live spam, valuemax, valuetext, tests | — |
| 38 | Global dataset search/filter | `feat/dataset-search` | main | #269 | R1 IN PROGRESS | — | — |
| 39 | OG-image generation (satori + resvg-js) | `feat/og-image-generation` | main | #270 | R1 IN PROGRESS | — | — |
| 40 | Real wage stagnation chart | `feat/wage-stagnation-chart` | main | #271 | FIXING R1 | Data inconsistency (2% vs 1.5%), unused counterfactual, comments | — |
| 41 | FAQ/glossary page | `feat/faq-glossary` | main | #267 | R2 APPROVED ✓ | Fixed: use Accordion, dark mode, headings | APPROVED |
| 42 | Performance: loading UX polish | `feat/loading-ux-polish` | main | #272 | R1 IN PROGRESS | — | — |

### Wave 8+ (future candidates)
- Compare your effective tax rate to a billionaire
- Ownership by age and tenure chart
- Backend structured JSON logging for production
- Data comparison feature (/compare route)
- UK billionaire wealth tracker
- FTSE 100 CEO pay ratio chart
- Postcode-driven house-price-to-earnings lookup

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-16 | Start with static data gap fix | Quick win, unblocks offline dev |
| 2026-05-16 | Build 6 new chart components before article pages | Components are prerequisite for pages |
| 2026-05-16 | Leave all PRs open, stack on them | Per user request |
| 2026-05-16 | Wave 4: fix stub pages + backend hardening first | Stub routes are visible broken links; backend validation is security debt |
| 2026-05-16 | Fixed freshness.json static generation (pushed to PR #242) | Feature invisible on deployed site without static fallback |
| 2026-05-16 | CODE_OF_CONDUCT blocked by content filter; replaced with enhanced CONTRIBUTING.md | Agent couldn't produce CoC template; CONTRIBUTING covers conduct section |
| 2026-05-16 | Wave 8: focus on engagement + viral shareability | Wealth scale scroller, search, OG images — make site compelling to share |
| 2026-05-16 | Wage chart: corrected growth rate from 2% to 1.5% (actual 2000-2008 CAGR) | Data integrity guardrail — do not fabricate statistics |

## Subagent Dispatch Reference

```
# Implementation (in worktree)
Agent(subagent_type="general-purpose", isolation="worktree", prompt="...")

# Review Round 1
Agent(subagent_type="pr-review-toolkit:code-reviewer", prompt="Review PR #N...")
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
