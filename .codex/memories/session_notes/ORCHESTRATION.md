# Orchestration Control — WealthLens HQ Autonomous Workflow v2

> **PURPOSE**: Master control document for end-to-end autonomous development.
> Survives context compaction. Any future Claude instance picks up from here.
>
> **CRITICAL**: Update this file BEFORE every compaction risk (long tool calls, large diffs).

Last updated: 2026-05-23T16:00Z

## 2026-05-23 New Cycle: Blueprint Foundation

Starting a new autonomous development cycle. The `resources/` directory contains a comprehensive Blueprint v5 and strategic plan that haven't been actioned. This cycle implements foundational infrastructure for the WealthLens-Sim microsimulation platform.

**Source material**: `resources/1779367399635_WealthLens_UK_Unified_Blueprint_v5.md` (2000-line research blueprint) and `resources/compass_artifact_*.md` (strategic/technical bridge plan).

**Prior state**: Waves 1-8 complete (PRs #232–#272 all merged). 11 Dependabot PRs open (#273–#283). Zero custom open PRs. Main CI green.

## 2026-05-17 Recovery Status (archived)

The autonomous cleanup/merge sweep completed. PRs through `#272` merged to `main`. CI green.

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

**Phase: WAVE 9 — BLUEPRINT FOUNDATION (started 2026-05-23)**

### Waves 1-8: ALL MERGED ✓ (PRs #232–#272)

See archived wave tables below for historical provenance.

### Wave 9 Streams — Blueprint Foundation

| # | Stream | Branch | Base | PR | Status | R1 | R2 |
|---|--------|--------|------|----|--------|----|----|
| 43 | Repository restructure (packages/wealthlens-sim/ + registries/) | `feat/sim-skeleton` | main | #286 | R2 DONE | 2/2 | 2/2 |
| 44 | License split (AGPL-3.0 for simulator) | `chore/license-split` | feat/sim-skeleton | #287 | R2 DONE | 2/2 | 2/2 |
| 45 | Model Charter (docs/MODEL_CHARTER.md) | `docs/model-charter` | main | #284 | R2 DONE | 2/2 | 2/2 |
| 46 | AI/LLM Disclosure (docs/AI_LLM_DISCLOSURE.md) | `docs/ai-disclosure` | main | #285 | R2 DONE | 2/2 | 2/2 |
| 47 | Sources registry (registries/sources.yml) | `feat/sources-registry` | feat/sim-skeleton | #288 | R2 DONE | 2/2 | 2/2 |
| 48 | Assumptions registry (registries/assumptions.yml) | `feat/assumptions-registry` | feat/sim-skeleton | #289 | R2 FIXES PUSHED | 2/2 | 2/2 fixes applied |
| 49 | Baselines registry (registries/baselines.yml) | `feat/baselines-registry` | feat/sim-skeleton | #290 | R2 FIXES PUSHED | 2/2 | 2/2 fixes applied |

### Wave 10 — Dependabot + Housekeeping

| # | Stream | Branch | Base | PR | Status | R1 | R2 |
|---|--------|--------|------|----|--------|----|----|
| 50 | Batch Dependabot updates (11 PRs consolidated) | `chore/dependabot-batch-2026-05-23` | main | #291 | R1 IN PROGRESS | 2/2 pending | — |

### Wave 11+ Candidates (from blueprint/compass)

- PolicyEngine-UK integration skeleton
- Top-tail reconstruction module (Pareto, GPD, rank correction)
- HVCTS reform module (Family E)
- Policy family stubs (Families A–G)
- Provenance manifest system
- Gate documentation (gates 0–9)
- Synthetic FRS+WAS data generation skeleton
- Dashboard components: ScenarioSelector, ProvenanceTooltip, ConfidenceFanChart
- Behavioural priors registry (priors.yml)
- CONTRIBUTING.md expansion with simulator dev workflow

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
| 2026-05-23 | Batch all 11 Dependabot PRs into single PR #291 | Cleaner than merging 11 individual PRs; vue-tsc major bump verified locally |
| 2026-05-23 | R2 found YAML 1.1 scientific notation bug in assumptions.yml | PyYAML requires e+ not bare e for float parsing — silent type error |
| 2026-05-23 | R2 found Family G missing from baselines.yml | Added devolution property-tax baseline to cover all 7 policy families |

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
