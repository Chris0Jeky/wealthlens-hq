# Wave 12 Design — Static Microsimulation Engine + Synthetic Population

Last updated: 2026-05-29
Status: IN PROGRESS. Author: autonomous dev cycle.

## Build progress

- ✅ **PR1 `synth/`** (#327) — deterministic synthetic-population generator
  (`generate_population(SynthConfig) -> SyntheticPopulation`; lognormal body +
  Pareto tail; weights on `Household.weight`; `provenance_ids` seam).
- ✅ **PR2 `rules/`** (#328) — `Scenario` / `FamilySelection` / `PolicyFamily` +
  `run_scenario(households, scenario) -> ScenarioResult` dispatching revenue
  families A–E (`match` + `assert_never` exhaustive) → total + `revenue_by_nation`.
- ⏭️ **PR3 `engine/` + `outputs/` (next, task #17)** — `engine.run_scenario(
  population, scenario, registries) -> EngineResult` wiring synth→rules→provenance;
  interval propagation (top-tail α + assumption ranges); per-decile attribution
  (needs per-household revenue, not the aggregate API); population-source
  `Protocol` seam; families F (enforcement uplift) + G (devolution scope)
  composition; `outputs.to_dashboard_json` with a golden-file test. Likely 2–3 PRs.
- Backlog: calibrate `synth/` to cited public WAS/ONS marginals (grossed total
  currently overshoots ~£26tn vs ~£15–16tn real — illustrative only until cited);
  Monte-Carlo/Sobol uncertainty (`uncertainty/`, Wave 13).

## 1. Why this wave

Gate 1 is complete: `packages/wealthlens-sim` ships the schema layer, registry
loaders, top-tail Pareto reconstruction, provenance, and **all seven policy
families (A–G)** as standalone calculators — but *nothing drives them end to
end yet*. Each family can score a household; no component (a) supplies a
population of households, (b) runs a chosen reform scenario across that
population, or (c) emits a dashboard-ready result. Wave 12 closes that loop and
produces the first **headline number**: "Reform X raises £Y bn (£low–£high)."

## 2. Current building blocks (on `main`)

| Module | Status | Provides |
|--------|--------|----------|
| `schema/` | done | `Household`, `Person`, `Asset`, `Nation`, `VersionTag`, result models |
| `reforms/` | done | Families A–G: `compute_*` (per-household) + `compute_aggregate_*_revenue` |
| `top_tail/` | done | Pareto reconstruction, 5 baseline variants → wealth-share / total intervals |
| `assumptions/`, `schema/baselines_loader` | done | validated registry loaders |
| `provenance/` | done | `ProvenanceCollector` → `ProvenanceManifest` |
| `synth/` | **stub** | (target) synthetic FRS+WAS population generation |
| `rules/` | **stub** | (target) shared execution framework over the families (Blueprint §9) |
| `engine/` | **stub** | (target) orchestration / PolicyEngine-UK bridge |
| `reconstruction/`, `reconcile/`, `uncertainty/`, `outputs/` | **stub** | deeper layers (later sub-waves) |

## 3. Wave 12 scope (minimal end-to-end path)

Implement the **shortest path to a working simulation**, deferring the heavier
statistical layers to Wave 13+:

1. **`synth/`** — a deterministic, seeded synthetic-population generator. v0.1
   produces a weighted list of `Household` objects whose wealth/asset marginals
   are calibrated to public WAS summary statistics, with the top tail shaped by
   the existing `top_tail/` Pareto parameters. No real microdata (licensing
   deferred — see §7). Output: `SyntheticPopulation(households, weights, seed,
   provenance_ids)`.
2. **`rules/`** — a `ScenarioRunner` that takes a `Scenario` (which families are
   enabled + each family's config) and a population, dispatches to the existing
   `reforms/` calculators, and returns per-household + aggregate results. This is
   the "execution framework" the `rules/` docstring already promises.
3. **`engine/`** — a thin `run_scenario(population, scenario, registries)`
   orchestrator that wires synth → rules → aggregation → provenance and returns
   an `EngineResult`.
4. **`outputs/`** — `to_dashboard_json(EngineResult)` producing the JSON contract
   the Vue dashboard consumes (totals, by-nation, by-decile, intervals, sources).

Deferred to Wave 13+: `reconstruction/` orchestration, `reconcile/` (NBS macro
reconciliation, Gate 2), full `uncertainty/` Monte-Carlo/Sobol (layer 7), and a
real PolicyEngine-UK rules bridge.

## 4. Data flow

```
registries/*.yml ──► loaders ──► assumptions + baselines
                                      │
synth.generate(seed) ──► SyntheticPopulation(households, weights)
                                      │
        (optional) top_tail augmentation of the top of the distribution
                                      │
engine.run_scenario(population, scenario, registries)
        │   for each enabled family in scenario:
        │       rules.ScenarioRunner → reforms.compute_<family>(household, cfg)
        │   aggregate: total, revenue_by_nation, by wealth decile
        │   intervals: from top_tail alpha interval + assumption RangeValues
        │   provenance: ProvenanceCollector.consume(...) + record(...)
        ▼
EngineResult ──► outputs.to_dashboard_json() ──► dashboard/*.json
```

## 5. Key interfaces (proposed)

```python
# rules/scenario.py
class FamilySelection(BaseModel):          # one enabled family + its config
    family: PolicyFamily                   # enum A..G
    config: <family-specific config model>

class Scenario(BaseModel):
    name: str
    version_tag: VersionTag
    families: list[FamilySelection]

# engine/result.py
class EngineResult(BaseModel):
    scenario: Scenario
    total_revenue_gbp_bn: Interval          # reuse top_tail.Interval
    revenue_by_nation: dict[str, Interval]
    revenue_by_decile: list[Interval]
    households_scored: int
    provenance: ProvenanceManifest

# engine/__init__.py
def run_scenario(population, scenario, *, registries=None) -> EngineResult: ...

# synth/population.py  (as implemented in PR1)
class SyntheticPopulation(BaseModel):
    households: list[Household]   # grossing weight lives on each Household.weight
    seed: int
    is_synthetic: bool = True
    provenance_ids: list[str] = []   # seam for the engine's provenance manifest
    # .weights property returns [h.weight for h in households]
```

**Weights** live on `Household.weight` (a first-class schema field), not a parallel
list — more flexible and co-located with the data the engine consumes; a
`weights` convenience property is provided. The **population-source `Protocol`**
(so a future real-microdata provider can drop in) is introduced in the engine PR
that consumes it, not in `synth/`.

## 6. Build sequence (stacked PRs, each with 2 adversarial reviews + ci-sim)

1. `synth/` skeleton + deterministic generator + marginal calibration tests.
2. `rules/ScenarioRunner` — single family over a population + aggregate revenue.
3. Multi-family scenarios + `revenue_by_nation` + by-decile aggregation.
4. Interval propagation (top-tail alpha interval + assumption `RangeValue`s).
5. Provenance wiring into the engine (every published number carries a manifest).
6. `outputs.to_dashboard_json` + a golden-file test of the JSON contract.

Each builds on the prior (true stack); ci-sim (added Wave-12-prep) runs ruff +
mypy + pytest on every PR.

## 7. Open decisions (need a steer before/while building)

1. **Microdata vs synthetic-only for v0.1.** Real WAS/FRS microdata needs a UKDS
   licence and cannot ship publicly. Recommendation: **synthetic-only** for v0.1
   (calibrated to public marginals), with the `Protocol` seam for real data later.
2. **Uncertainty method.** Full Monte-Carlo/Sobol (`uncertainty/`, SALib/NumPyro)
   is heavy. Recommendation: **interval arithmetic + scenario sweep** for Wave 12;
   Monte-Carlo in Wave 13.
3. **Calibration targets.** Which public WAS/ONS tables anchor the synthetic
   marginals — must be cited per the data-integrity guardrail (URL + access date
   in `registries/sources.yml`).

## 8. Guardrails (carried from CLAUDE.md / Model Charter)

- Every published number carries a provenance manifest (Blueprint §13.4).
- No fabricated statistics; synthetic data is clearly labelled synthetic and its
  calibration sources are cited.
- New behaviour ships behind explicit scenario selection; existing family
  calculators are unchanged (additive only).
- WCAG AA / mobile-responsive applies once outputs reach the dashboard.
