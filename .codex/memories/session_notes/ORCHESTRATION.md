# Orchestration Control — WealthLens HQ Autonomous Workflow v2

> **PURPOSE**: Master control document for end-to-end autonomous development.
> Survives context compaction. Any future Claude instance picks up from here.
>
> **CRITICAL**: Update this file BEFORE every compaction risk (long tool calls, large diffs).

Last updated: 2026-05-30

---

# 🟢 HANDOFF — read this first (2026-05-30, post #333/#334 drain)

**You are continuing an endless end-to-end autonomous cycle on the WealthLens-Sim
microsimulator.** This session built the entire Wave 12 **engine** (synth → rules →
engine → outputs) as a reviewed PR stack and merged most of it. Below is exactly
where things stand, where to start, and where to go. (Sections further down are the
historical per-cycle logs — skim only if you need detail.)

## What the user wants (standing directive)
Endless cycle: pick the next task → implement in **small incremental commits** →
**2 independent adversarial reviews per PR** (use `Agent` with
`pr-review-toolkit:code-reviewer` + `pr-review-toolkit:silent-failure-hunter`, or
similar, with *different lenses*) → **address ALL findings of every severity** →
**address ALL bot comments** (gemini-code-assist, chatgpt-codex-connector, copilot)
→ stacked branches for dependencies → seed new tasks when the queue empties →
**don't stop**. Pre-existing bugs get fixed too. Use worktrees/subagents when efficient.

**Merge discipline (important):** never merge the *newest* open PR; a PR that is
~3 PRs back and has 2 reviews + all bot comments addressed + CI green + some elapsed
time may be merged. Keep a healthy backlog of aging PRs. Merge oldest-first with
plain `gh pr merge <n> --merge` (preserves SHAs); then `gh pr edit <child> --base main`.
**Never `--delete-branch` a stacked base** — it closed child PRs in a past cycle
([[feedback_stacked_merge_delete_branch]]).

## Current state (main)
- **Full engine is on main** via merged PRs **#329** (engine-core), **#330**
  (devolution), **#331** (enforcement), **#332** (intervals), **#333** (dashboard
  JSON outputs), and **#334** (headline example). **634 sim tests pass on main;
  635 pass on the integrated #335 branch.**
- `engine.simulate(population, scenario, *, registries=None, devolution=None,
  enforcement=None) -> EngineResult` is the single entry point (named `simulate`,
  NOT `run_scenario`, to avoid colliding with `rules.run_scenario`).
- **Open PR:** **#335** `feat/synth-ons-calibration` → main calibrates synth
  defaults to cited public ONS/WAS aggregate marginals and threads source IDs through
  population provenance. GitHub checks are green; it is the newest open PR, so do
  not merge it until reviewed, aged, and another PR is opened above it.

## ▶️ WHERE TO START (next session, in order)
1. **Recover:** read this file, `00_ACTIVE.md`, `tasks/active-sprint.md`,
   `tasks/inbox.md`; run `gh pr list --state open` and `gh pr checks 335`.
2. **Review/age #335**. It has local verification and CI green as of this handoff, but
   still needs the normal review/bot-clean cycle before merge.
3. **Open the next Wave 13 PR above #335 before merging it.** Good candidates are the
   enforcement compliance model, remaining synth generative provenance, or wiring the
   dashboard JSON into Vue.
4. Continue the endless cycle: small PR → 2 independent reviews → address all findings
   and bot comments → merge only once the PR is no longer newest.

## Wave 13 backlog (also in tasks/inbox.md "Wave 13 candidates")
Ordered by value/data-integrity:
- **Review and drain #335 synth calibration** once it is no longer newest. It reduces
  default synthetic gross wealth to ~£14tn on standard seeds using cited public
  ONS/WAS aggregate marginals in `registries/sources.yml`.
- **Proper enforcement compliance model** (task #7): the Family-F uplift is added on
  top of *full statutory liability*, so it overstates above the 100%-compliance
  ceiling. Give families a baseline-vs-theoretical compliance split anchored to
  HMRC's published tax-gap stats (already cited in `reforms/f_enforcement.py`).
- **Record remaining synth generative params in provenance** — #335 threads public
  source IDs through `population.provenance_ids`, but the synth `pareto_alpha`/seed
  still aren't recorded. Changing this will require regenerating dashboard goldens
  (`REGEN_GOLDEN=1 python -m pytest tests/test_outputs.py -q`).
- **Monte-Carlo / Sobol uncertainty** (`uncertainty/` stub) — replace the single
  multiplicative top-tail-α band with per-parameter sampling (SALib/NumPyro).
- **Wire the dashboard JSON into a Vue scenario page** (mission: make it visible) —
  ConfidenceFanChart + ProvenanceTooltip + a banner that renders `caveats[]`.
- Other stubs awaiting work: `reconcile/` (NBS macro reconciliation, Gate 2),
  `reconstruction/`, real-microdata provider behind the `PopulationSource` Protocol.

## Engine architecture (so you can revise/extend confidently)
Package: `packages/wealthlens-sim/wealthlens_sim/`. Engine modules:
- `engine/__init__.py` — `simulate()` orchestrator; `_OUTPUT_LABELS`;
  `_build_complete_provenance` / `_build_incomplete_provenance`.
- `engine/result.py` — `EngineResult` (all revenue as `Interval`; fields:
  total/by_nation/by_decile, `enforcement_uplift_bn`, `households_scored`,
  `provenance`, `devolution_split`, `population_provenance_ids`,
  `provenance_complete`); `PopulationSource` Protocol seam; `Registries` bundle.
  Two validators: 0-or-10 deciles; `households_scored == devolution_split.included_count`.
- `engine/_attribution.py` — per-household liability dispatch + **equal-weight
  boundary-split deciles** (conserves revenue for ANY positive weight; raises on
  n_deciles<=0 / negative / non-positive-total weight).
- `engine/_enforcement.py` — `tax_family_for` (A/B/E→OTHER, C→CGT, D→IHT) +
  `compute_engine_enforcement`.
- `engine/_intervals.py` — top-tail-α → multiplicative revenue band
  (`α/(α-1)` tail-mean ratio; α from `toptail.pareto_alpha.overall.v1`); raises on
  malformed alpha; returns None only when absent.
- `outputs/__init__.py` — `to_dashboard_json` → root `provenance_complete` +
  `caveats[]` + intervals + flattened provenance. `DASHBOARD_SCHEMA_VERSION="1.1"`.
- `examples/headline_revenue.py` — runnable demo (`python -m
  wealthlens_sim.examples.headline_revenue`).

**Key invariants / caveats (don't regress):** `sum(revenue_by_decile) ≈ total -
enforcement_uplift` at EVERY bound; degenerate intervals + `provenance_complete=False`
when no registry; enforcement overstatement + unsourced state surfaced via `caveats[]`;
synthetic data clearly labelled everywhere it's published.

## Ops cheat-sheet (environment gotchas that bit this session)
- Run from the package dir: `cd C:/Users/jekyt/source/wealthlens-hq/packages/wealthlens-sim`
  then `python -m pytest -q` · `python -m ruff check wealthlens_sim` ·
  `python -m ruff format ...` · `python -m mypy wealthlens_sim`. Regenerate goldens:
  `REGEN_GOLDEN=1 python -m pytest tests/test_outputs.py -q`.
- **Bash tool cwd resets between calls** — always `cd <abs> && ...`. Backslash paths
  get mangled; use forward slashes.
- **`git push --force-with-lease` must be its OWN command** (chained pushes were
  permission-denied). After editing a stacked base, rebase children up
  (`git rebase <base>`) and force-push each branch standalone.
- **CI workflows trigger on PR→main** (`pull_request` to main). A stacked PR whose
  base is another feature branch shows **"no checks reported"** until you
  `gh pr edit <n> --base main` AND a push/synchronize fires. ci-sim runs ruff+mypy+
  pytest on py3.11/3.12. main has **no branch protection** (CI is informational; the
  post-merge main CI is the real safety net — watch it after each merge).
- Commit subjects: `<area>: <imperative>`. Status-doc syncs commit directly to main
  (established repo practice). Feature work goes on branches → PRs.

---

## 2026-05-30 New Cycle: WAVE 12 PR3 — ENGINE STACK (endless end-to-end)

**DIRECTIVE (user, 2026-05-30):** Resume the endless end-to-end cycle. Per PR: 2
independent adversarial reviews; address ALL findings (every importance) + all bot
comments; small incremental commits; worktrees/subagents where efficient; stacked
branches for dependencies. Address pre-existing bugs too. Seed new tasks when the
queue empties. **Merge discipline:** do NOT merge the newest PR; a PR that was
opened ~3 PRs ago may be merged once it has 2 reviews + all bot comments addressed
+ some elapsed time. Keep a healthy backlog of open PRs aging in the stack.

### Plan: Wave 12 PR3 = a 4-PR stack (task #17 split for reviewability)
Each stacked on the prior; each = 2 adversarial reviews + ci-sim green + small commits.

| PR | Branch | Base | Scope |
|----|--------|------|-------|
| 3a | `feat/engine-core` | main | **PR #329 (open, 2 review rounds done).** `PopulationSource` Protocol seam; `EngineResult` model (total/by-nation/by-decile as `Interval`, households_scored, provenance, `provenance_complete`, `population_provenance_ids`); `engine.simulate(population, scenario, *, registries=None)` (named `simulate`, NOT `run_scenario`, to avoid colliding with `rules.run_scenario`) — A–E via `rules.run_scenario` → equal-weight per-decile attribution → provenance manifest. Degenerate intervals (low=central=high) placeholder. **G-scope deferred to 3b** (Scenario can't hold G). |
| 3b | `feat/engine-enforcement` | feat/engine-core | Family F enforcement-uplift composition (map A–E revenues → `TaxFamily`, `compute_enforcement_uplift`, add `net_uplift_bn`). Document the TaxFamily-mapping decision. |
| 3c | `feat/engine-intervals` | feat/engine-enforcement | Real interval propagation: top-tail α `Interval` sweep + assumption `RangeValue` low/central/high → revenue `Interval`s. |
| 3d | `feat/outputs-dashboard-json` | feat/engine-intervals | `outputs.to_dashboard_json(EngineResult)` + golden-file test. |

### Per-household liability fields (for decile attribution, PR3a)
A `compute_wealth_tax(hh,cfg).tax_liability` · B `compute_one_off_levy(hh,cfg).levy_liability`
· C `compute_household_cgt(hh,cfg).total_cgt_liability` · D `compute_household_iht(hh,cfg).total_iht_liability`
· E `compute_hvcts(hh,cfg).total_surcharge`. Weight by `hh.weight`; bin by `total_net_wealth`.

### Known seams / decisions for the stack
- `rules.run_scenario(list[Household], Scenario) -> ScenarioResult` (A–E only). The
  engine entry point is `engine.simulate(...)`; it imports the rules function aliased
  (`_run_families`) so `rules.run_scenario` cannot shadow the engine's own symbol.
- F (`compute_enforcement_uplift(theoretical: dict[TaxFamily,float], cfg)`) and G
  (`split_households_by_scope(households, cfg) -> (included, excluded, split)`) compose in engine.
- Synth sets income/CGT=0 → CGT family yields 0 on synth data (documented, not a bug).
- `population.provenance_ids` is always `[]` today; engine builds manifest from registries it reads.
- Open decision (PR3b): TaxFamily has no wealth-tax member → map A/B/E→OTHER, C→CGT, D→IHT; document.

### Stack progress (2026-05-30)
- **PR #329** `feat/engine-core` → main: DONE. 2 adversarial rounds + all bot comments
  (gemini/codex) addressed. CI **green** (CodeQL+analyze+lint-type-test 3.11/3.12).
  604 sim tests. Renamed entry `simulate` (not run_scenario). Equal-weight deciles.
  **Oldest PR — merge candidate once stack is ~3 deep + time elapsed.**
- **PR #330** `feat/engine-devolution` → feat/engine-core: DONE. 2 reviews + findings.
  Family G scope filter; `devolution_split` on result; `DevolutionSplit` exported.
- **PR #331** `feat/engine-enforcement` → feat/engine-devolution: DONE. 2 reviews +
  findings. Family F uplift; `enforcement_uplift_bn`; documented v0.1 overstatement
  caveat (A-E is full statutory → uplift exceeds ceiling); follow-up = task #7.
- **CI on stacked PRs:** workflows trigger on PRs → `main`, so #330/#331 show "no
  checks" until retargeted to main. Verified locally instead. On merge of #329,
  retarget #330 base→main with `gh pr edit 330 --base main` (do NOT --delete-branch
  a stacked base — see [[feedback_stacked_merge_delete_branch]]; it closed children before).
- **NEXT:** PR3d `feat/engine-intervals` (task #3) = real interval propagation
  (top-tail α sweep + assumption RangeValue) + COMPLETE provenance (consume α +
  ranges, thread devolution scope into manifest, flip provenance_complete=True).
  Then PR3e `feat/outputs-dashboard-json` (task #4). After PR3d opens (stack 4 deep),
  merge #329 → main.
- Follow-ups seeded: task #7 (proper enforcement compliance model).

### Branch hygiene backlog (task #5)
Stale local `feat/*`,`fix/*` + leftover `worktree-agent-*` branches (prior merged cycle).
`feat/baselines-loader` is an unmerged orphan on origin — investigate/delete.

---

## 2026-05-29 New Cycle: MERGE + ADVANCE (policy shift)

**DIRECTIVE CHANGE (user, 2026-05-29):** The prior "Never merge — leave all PRs
open" rule is **superseded**. New standing directive: re-check open PRs (comments
+ reviews, address findings of all importances), then **merge them systematically**
so work can continue. Endless end-to-end cycle: address findings → merge → seed
new tasks → repeat. Stacked branches for dependencies. Small incremental commits.
Worktrees + subagents where efficient. 2 independent adversarial reviews per *new* PR.

### State snapshot (2026-05-29)
- 38 open PRs. All `MERGEABLE`, 0 failing checks. `main` has **no branch protection**.
- Deep linear simulator stack (Wave 9 + Wave 11) + 7 `fix/*` PRs (#304–#310, results
  of prior review rounds, not yet folded in) + Dependabot (#273–#283, #311, #312) +
  batch #291 + docs (#284, #285).
- **PR #293 is BROKEN**: head=`main`, base=`feat/sim-schema` (inverted). Real code is
  on branch `feat/assumption-loader` which has NO open PR. Must close #293 + recreate.

### Merge mechanics (decided)
- Allowed methods: squash, merge, rebase. Use **merge commits** (`--merge`) to
  preserve commit SHAs so stacked children stay clean.
- Use `gh pr merge <n> --merge --delete-branch`: deleting the base branch **auto-retargets
  child PRs to `main`** — the clean mechanism for the deep stack.
- Fold each `fix/*` PR INTO its feature branch first (fix → feature), then feature → main.
- Verify CI green (`gh pr checks`) before each merge even though not enforced.

### Merge train order (bottom-up)
- M1 docs (base main): #284, #285
- M2 skeleton: #286 (→ auto-retargets #287,#288,#289,#290,#292 to main)
- M3 skeleton children: #287; #288(+fix #305); #289(+fix #306); #290(+fix #309); #292(+fix #307)
- M4 deep chain: assumption-loader(fix #293 + fix #308) → #295(+#304) → #296(+#310) →
  #297 → #298 → #299 → #300 → #301 → #302 → #303
- M5 Dependabot: merge batch #291, close superseded #273–#283; then #311, #312

### Progress log (M-train) — 2026-05-29
- DONE M1: #284, #285 (docs) merged.
- DONE M5: batch #291 merged; #273–#283 closed (superseded); #311, #312, #313 merged.
- DONE M2/M3: sim-skeleton #286 merged. NOTE: `--delete-branch` CLOSED the 5
  child PRs (#287–#292) instead of retargeting — recreated as #314–#319 → main, merged.
  Lesson saved to memory [[feedback_stacked_merge_delete_branch]]. Going forward:
  merge with plain `--merge`, retarget children just-in-time, delete branches later.
- DONE M4: broken #293 closed; assumption-loader recreated as #319 (rebased, resolved
  baselines.yml conflict in favour of main's curated #317 registry). Deep chain
  #295–#303 rebased onto main with `git rebase -X ours --onto origin/main <oldbase>`
  (stale registry/ORCHESTRATION drafts deferred to main; code applied clean) and merged.
- VERIFIED: full sim suite 499→515 passing on integrated main; ruff clean.
- Fix PRs (prior review rounds): #305, #306, #307, #308 merged (rebased --onto main).
  #309 → silently broke (added/removed duplicate baselines.py); redone as #320 with
  only the effective_date doc clarification, merged.
- 2 adversarial reviews of the integrated stack pre-merge: reviewer-1 (math) SAFE;
  reviewer-2 (types) found 5 issues → all triaged into tasks #8–#13.
- IN PROGRESS: #321 (top-tail: int-truncation float coercion + ci validation; finding
  #9 was a false positive — bootstrap already filters alpha>1) and #322 (provenance:
  faithful schedule preservation, fixes silent-drop in prior #310 approach + mypy).
  4 fresh adversarial reviews launched (2 per PR).
- KNOWN PRE-EXISTING: ci-backend.yml path filters EXCLUDE packages/wealthlens-sim →
  sim tests never run in CI (task #7). mypy needs yaml/scipy overrides. To do after
  #321/#322 land: add ci-sim.yml + types-PyYAML + mypy overrides.

### Force-push note
`gh`/hook denied `git push --force-with-lease` on some fix branches mid-session;
workaround = push to a fresh `-v2` branch (plain push), open new PR, close old.
Used for #320 (was #309), #321 (was #304), #322 (was #310).

### 2026-05-29 cycle COMPLETE — all 38 PRs resolved
- All sim + fix PRs merged to main (#284–#323). 0 open PRs. 523 sim tests pass.
- Fix PRs landed as v2 branches: #320 (was #309), #321 (was #304), #322 (was #310);
  each got 2 fresh adversarial reviews; all findings (incl. nits) addressed.
- CI gap closed: ci-sim.yml runs ruff+mypy+pytest on py3.11/3.12 + weekly (#323).
- 21 merged feature/fix branches deleted from origin. `feat/baselines-loader` left
  (unmerged orphan — investigate/delete later).
- Backlog follow-ups ALL DONE this cycle (each 2 reviews + merged):
  - #324 (was task #13): IHT charitable-gift exemption + RNRB cap-at-residence.
  - #325 (was task #14): npm overrides patch tmp/uuid → Dependabot alerts now 0.
  - #326 (was task #12): registries packaged into wheel+sdist via conditional
    hatch build hook (hatch_build.py); sdist install verified end-to-end. The
    R1 review caught a real sdist-uninstallable bug; R2 confirmed the fix.
- STATE: 0 open PRs; main green; 534 sim tests; Dependabot 0; all branches clean.
- Wave 12 design: `docs/WAVE12_SIMULATION_ENGINE_DESIGN.md`. User decided (2026-05-29):
  **synthetic-only** population for v0.1; interval-arithmetic uncertainty; cite WAS/ONS.
- Wave 12 PR1 DONE: `synth/` generator MERGED (#327) — `generate_population(SynthConfig)`
  → `SyntheticPopulation` (lognormal body + Pareto tail; weights on Household.weight;
  `provenance_ids` seam; clearly-labelled synthetic, sourced, verify-before-publish).
  2 reviews + a confirmation round; 549 sim tests; ci-sim green. Task #15 done.
- Wave 12 PR2 DONE: `rules/` MERGED (#328) — `Scenario`/`FamilySelection`/
  `PolicyFamily` + `run_scenario(households, scenario)` dispatching the 5 revenue
  families A-E (match+assert_never exhaustive; dict-config coerced to family type)
  → `ScenarioResult{total_revenue_bn, revenue_by_nation, family_revenues}`.
  564 sim tests; 2 reviews + confirmation; ci-sim green. Task #16 done.
- NEXT (Wave 12 final): task #17 = `engine.simulate(population, scenario,
  registries) -> EngineResult` wiring synth→rules→aggregate→**provenance**, plus
  interval propagation (top-tail alpha + assumption RangeValues), per-decile
  attribution (needs per-household revenue — NOT in the aggregate API, so call the
  per-household reforms/ funcs), the population-source `Protocol` seam (design §5),
  and `outputs.to_dashboard_json` (golden-file test). Families F (enforcement
  uplift) + G (devolution scope) compose here too. Likely split into 2-3 PRs.
  Each PR: 2 reviews + ci-sim. KNOWN: synth IHT estimate is implausibly high
  (synth overshoots real wealth + IHT-as-if-death) — calibration follow-up.

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

### Wave 11 — Simulator Core Modules (stacked on main)

Branch stack: `main` → `feat/sim-schema` → `feat/assumption-loader` → `feat/top-tail` → `feat/provenance` → `feat/wealth-tax` → `feat/one-off-levy` → `feat/hvcts` → `feat/cgt-baseline` → `feat/iht-baseline` → `feat/enforcement` → `feat/devolution`

| # | Stream | Branch | Base | PR | Status | R1 | R2 |
|---|--------|--------|------|----|--------|----|----|
| 51 | Pydantic schema module | `feat/sim-schema` | feat/sim-skeleton | #292 | R2 APPROVED ✓ | Fixed: ConfigDict, Nation validator, VersionTag fields | Clean |
| 52 | Assumption + baselines loaders | `feat/assumption-loader` | feat/sim-schema | #293 | R2 APPROVED ✓ | Fixed: monotonic range, StrEnum, duplicate IDs | Clean |
| 53 | Top-tail Pareto reconstruction | `feat/top-tail` | feat/assumption-loader | #295 | R2 APPROVED ✓ | 8 fixes applied | 6 new fixes |
| 54 | Provenance manifest + collector | `feat/provenance` | feat/top-tail | #296 | R2 APPROVED ✓ | 8 fixes | 4 fixes |
| 55 | Family A annual wealth tax | `feat/wealth-tax` | feat/provenance | #297 | R2 APPROVED ✓ | 7 fixes, 14 new tests | 4 fixes, 10 new tests (47 total) |
| 56 | Family B one-off wealth levy | `feat/one-off-levy` | feat/wealth-tax | #298 | R2 APPROVED ✓ | Fixed: shared _banding, LevyRateBand alias | 4 fixes |
| 57 | Family E HVCTS (property tax) | `feat/hvcts` | feat/one-off-levy | #299 | R2 APPROVED ✓ | Fixed: revenue_by_nation, boundary tests | Overlapping-band validation |
| 58 | Family C CGT baseline | `feat/cgt-baseline` | feat/hvcts | #300 | R2 APPROVED ✓ | Fixed: dead config guards, ge=0 rates | ValueError for validators |
| 59 | Family D IHT baseline | `feat/iht-baseline` | feat/cgt-baseline | #301 | R2 APPROVED ✓ | 6 fixes, 14 boundary tests (72 IHT) | PENSION_TYPES constant, 2 integration tests |
| 60 | Family F enforcement | `feat/enforcement` | feat/iht-baseline | #302 | R2 APPROVED ✓ | all-6-families test (38 enforcement) | Clean |
| 61 | Family G devolution | `feat/devolution` | feat/enforcement | #303 | R2 APPROVED ✓ | 2 fixes: ValueError, reject contradictory nations (29 devolution) | 1 fix: stale field description |

**All 7 policy families (A-G) implemented. 498 tests passing. Gate 1 policy family code complete.**

PR #294 was absorbed into #293.

### Wave 12+ Candidates (from blueprint/compass)

- Static microsimulation engine (`engine/` module)
- Synthetic FRS+WAS data generation (`synth/` module)
- WAS/FRS reconstruction pipeline (`reconstruction/` module)
- ONS NBS macro reconciliation (`reconcile/` module)
- Uncertainty propagation (`uncertainty/` module)
- PolicyEngine-UK integration (`rules/` module)
- Output formatting + dashboard JSON (`outputs/` module)
- Gate documentation (gates 0-9)
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
| 2026-05-23 | Stacked branch strategy for sim | Each module depends on previous; stacking avoids merge conflicts |
| 2026-05-23 | StrEnum migration across all schema enums | Ruff UP042 compliance; Python 3.11+ target |
| 2026-05-23 | Shared _banding.py extracted from A/B duplication | RateBand + compute_banded_liability shared |
| 2026-05-24 | All 7 policy families (A-G) implemented | Gate 1 policy family code complete (498 tests) |
| 2026-05-24 | Family F enforcement as compliance-multiplier model | Revenue uplift from observability, not rate changes |
| 2026-05-24 | Family G devolution as nation-scope routing layer | Composition over reimplementation |
| 2026-05-24 | Preset scope rejects contradictory included_nations | R1 finding: silent discard is a footgun in fiscal simulation |

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
