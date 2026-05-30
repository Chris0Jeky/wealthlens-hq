# Active Sprint

Last updated: 2026-05-29

This week's focus. Keep this list to 5-7 tasks.

## Sprint: 2026-05-29 to 2026-06-05

**Context:** The entire Gate-1 simulator (skeleton, schema, loaders, top-tail
reconstruction, provenance, all 7 policy families A–G) is MERGED to `main` (PRs
#284–#326). Wave 12 (the engine driving them) is underway: `synth/` (#327) and
`rules/run_scenario` (#328) merged. 564 sim tests pass; ci-sim green; 0 open PRs.

1. - [x] CI gap: add `packages/wealthlens-sim` to CI — ci-sim.yml + types-PyYAML + scipy mypy override (PR #323) (@Chris) [completed: 2026-05-29]
2. - [x] IHT v0.1: deduct charitable bequest from estate; cap RNRB at residence value (PR #324) (@Chris) [completed: 2026-05-29]
3. - [x] Security: patch tmp/uuid Dependabot alerts via npm overrides (PR #325) (@Chris) [completed: 2026-05-29]
4. - [x] Package registries into wheel+sdist via hatch build hook + resolver fallback (PR #326) (@Chris) [completed: 2026-05-29]
5. - [x] Wave 12 PR1 `synth/`: deterministic synthetic-population generator (PR #327) (@Chris) [completed: 2026-05-29]
6. - [x] Wave 12 PR2 `rules/`: Scenario + run_scenario over the population (PR #328) (@Chris) [completed: 2026-05-29]
7. - [ ] **Wave 12 PR3 `engine/`** (split into a 4-PR stack): `engine.simulate(population, scenario, registries) -> EngineResult` — wire synth→rules→provenance, interval propagation, per-decile attribution, F/G composition, `outputs.to_dashboard_json` (@Chris) [due: 2026-06-05]
   - 3a `feat/engine-core` (PR #329, in review): Protocol seam + EngineResult + A–E end-to-end + equal-weight deciles + provenance.
   - 3b enforcement+devolution (F/G); 3c real interval propagation; 3d outputs+golden file.

## Why These

- **Merge cycle (1–4):** cleared all 38 open PRs with rigour; closed the CI gap (simulator was untested in CI), the IHT data-integrity simplifications, the security alerts, and the pip-install packaging gap — each its own reviewed PR.
- **Wave 12 (5–7):** the policy families existed but nothing drove them. `synth/` supplies a population, `rules/` runs a scenario over it; the **engine PR (7)** ties synth→rules→provenance into a single `EngineResult` — the first end-to-end headline-revenue number. Then `outputs/` formats it for the dashboard.
- **Follow-ups (backlog, not this sprint):** calibrate the synth generator to cited WAS marginals (currently overshoots); Monte-Carlo uncertainty (Wave 13); real WAS/FRS microdata behind the Protocol seam.

## Completed This Sprint

- [x] Extract all research insights, action items, contacts, and data sources into structured files (@Chris) [completed: 2026-05-14]
- [x] Create initial WealthLens HQ scaffold (@Codex) [completed: 2026-05-14]
- [x] Order *The Trading Game* by Gary Stevenson and *A Brief History of Equality* by Piketty; begin reading (@Chris) [completed: 2026-05-14]
- [x] Create Twitter/X account and Bluesky account (@Chris) [completed: 2026-05-14]
- [x] Build 3 data pipelines + interactive Plotly charts: WID wealth shares, ONS housing affordability, HMRC CGT concentration (@Chris) [completed: 2026-05-14]
- [x] Send volunteer emails to mySociety and Democracy Club (@Chris) [completed: 2026-05-14]
- [x] Subscribe to 5 key newsletters: Resolution Foundation, Tax Policy Associates, Milanovic, Tooze, IFS (@Chris) [completed: 2026-05-14]
- [x] Scaffold FastAPI backend with health, data, metadata endpoints (@Chris) [completed: 2026-05-15]
- [x] Scaffold Vue 3 + TypeScript + Pinia + TailwindCSS frontend (@Chris) [completed: 2026-05-15]
- [x] Deploy Vue frontend to GitHub Pages as master site (@Chris) [completed: 2026-05-16]
- [x] Merge all ~192 PRs (10 waves of reviewed, stacked PRs) — zero open PRs remain (@Chris) [completed: 2026-05-16]
- [x] Resume interrupted PR cleanup and merge remaining reviewed PRs through #272; final main CI green and zero open PRs remain (@Codex) [completed: 2026-05-17]
- [x] Post-merge health check — fix lint, types, tests; 874 tests passing, all CI green (@Chris) [completed: 2026-05-16]
- [x] Clean up 292 local + 204 remote stale branches (@Chris) [completed: 2026-05-16]
