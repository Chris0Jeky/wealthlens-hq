# Orchestration Control — WealthLens HQ Autonomous Workflow v2

> **PURPOSE**: Master control document for end-to-end autonomous development.
> Survives context compaction. Any future Claude instance picks up from here.
>
> **CRITICAL**: Update this file BEFORE every compaction risk (long tool calls, large diffs).

Last updated: 2026-05-23T14:00Z

## 2026-05-23 Status — WealthLens-Sim Microsimulator Build

Phase has shifted from dashboard frontend (Waves 1-8, PRs #232-#272, all merged) to the WealthLens-Sim microsimulation engine. Blueprint v5 drives all design. Stacked branch strategy on main.

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

**Phase: SIMULATOR BUILD — Gate 1 (Blueprint v5)**

Branch stack: `main` → `feat/sim-skeleton` → `feat/sim-schema` → `feat/assumption-loader` → `feat/top-tail`

### Simulator PRs (stacked)

| # | Stream | Branch | Base | PR | Status | R1 | R2 |
|---|--------|--------|------|----|--------|----|----|
| 43 | Assumptions YAML registry (18 entries) | `feat/assumptions-registry` | main | #289 | R2 APPROVED ✓ | Clean | Clean |
| 44 | Baselines YAML registry (13 entries) | `feat/baselines-registry` | main | #290 | R2 APPROVED ✓ | Clean | Clean |
| 45 | Dependabot batch (Node 22, deps) | `chore/dependabot-batch-2026-05-23` | main | #291 | R2 APPROVED ✓ | Clean | Clean |
| 46 | Pydantic schema module (households, policies, results) | `feat/sim-schema` | feat/sim-skeleton | #292 | R2 APPROVED ✓ | Fixed: ConfigDict, Nation validator, VersionTag fields | Clean |
| 47 | Assumption + baselines loaders | `feat/assumption-loader` | feat/sim-schema | #293 | R2 FIXES PUSHED | Fixed: monotonic range, StrEnum, duplicate IDs, empty-file safety, ScheduleValue validator | R2 fixes applied |
| 48 | Top-tail Pareto reconstruction | `feat/top-tail` | feat/assumption-loader | #295 | R1 IN PROGRESS | 2 reviewers launched | — |

### Closed/Absorbed
| PR | Reason |
|----|--------|
| #294 | Baselines loader absorbed into PR #293 |

### Dashboard PRs (Waves 1-8, all merged: PRs #232-#272)

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-23 | Stacked branch strategy for sim | Each module depends on previous; stacking avoids merge conflicts |
| 2026-05-23 | StrEnum migration across all schema enums | Ruff UP042 compliance; Python 3.11+ target |
| 2026-05-23 | Empty baselines file raises ValueError not fabricates date | Data integrity: "do not fabricate statistics" |
| 2026-05-23 | ScheduleValue requires at least one rate/band field | Prevents silent acceptance of content-free schedules |
| 2026-05-23 | Pareto v0.1 uses bootstrap CI, v0.2+ will use Bayesian | Per Blueprint v5 section 7.3 phasing |
| 2026-05-23 | All five baseline variants ship co-equally | Blueprint section 2.3: no silent favouring |

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
