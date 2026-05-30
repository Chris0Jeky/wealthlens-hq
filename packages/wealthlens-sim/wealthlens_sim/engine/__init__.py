"""Static microsimulation engine — wires synth -> rules -> provenance (Wave 12 PR3a).

:func:`simulate` is the engine's single entry point: it scores a
:class:`~wealthlens_sim.engine.result.PopulationSource` against a
:class:`~wealthlens_sim.rules.scenario.Scenario` (revenue families A-E) and
returns an :class:`~wealthlens_sim.engine.result.EngineResult` carrying interval
revenue totals, a per-nation and per-wealth-decile breakdown, and a provenance
manifest. It is named ``simulate`` (not ``run_scenario``) to avoid colliding with
``rules.run_scenario``, which has a different signature and return type.

PR3a ships the A-E end-to-end path with **degenerate intervals**
(``low == central == high``) and a **known-incomplete** provenance manifest
(``EngineResult.provenance_complete is False``): the published numbers depend on
the policy configs and the top-tail Pareto alpha, but PR3a does not yet
``consume`` those assumptions. Real interval propagation + full provenance land
in PR3c; Family F (enforcement) + Family G (devolution) composition lands in PR3b.
The ``registries`` seam is threaded now so those PRs need no signature change.

Reference: docs/WAVE12_SIMULATION_ENGINE_DESIGN.md §5.
"""

from __future__ import annotations

from wealthlens_sim.engine._attribution import household_liability, revenue_by_wealth_decile
from wealthlens_sim.engine.result import (
    N_DECILES,
    EngineResult,
    PopulationSource,
    Registries,
)
from wealthlens_sim.provenance.collector import ProvenanceCollector
from wealthlens_sim.provenance.manifest import (
    PipelineLayer,
    ProvenanceEntry,
    ProvenanceManifest,
)
from wealthlens_sim.reforms.g_devolution import DevolutionConfig, split_households_by_scope
from wealthlens_sim.rules.scenario import Scenario
from wealthlens_sim.rules.scenario import run_scenario as _run_families
from wealthlens_sim.schema.household import Household
from wealthlens_sim.top_tail.types import Interval

__all__ = [
    "N_DECILES",
    "DevolutionConfig",
    "EngineResult",
    "PopulationSource",
    "Registries",
    "household_liability",
    "revenue_by_wealth_decile",
    "simulate",
]

#: Labels recorded in the provenance manifest, one per published output.
_OUTPUT_LABELS = ("total_revenue_gbp_bn", "revenue_by_nation", "revenue_by_decile")


def _point_interval(value: float) -> Interval:
    """Wrap a point estimate as a degenerate interval (PR3a placeholder).

    PR3c replaces these with genuine low/central/high bounds propagated from the
    top-tail alpha interval and assumption ranges.
    """
    return Interval(low=value, central=value, high=value)


def _build_provenance(scenario: Scenario, registries: Registries | None) -> ProvenanceManifest:
    """Build the run's provenance manifest (known-incomplete in PR3a).

    Records one REVENUE-layer entry per published output. When an assumption
    registry is supplied the manifest is built through a
    :class:`ProvenanceCollector` (the seam PR3c uses to ``consume`` the top-tail
    alpha + assumption ranges); otherwise it is constructed directly. Both paths
    produce the same *entries* (labels, layer, assumption ids) in PR3a — they do
    not yet differ because no assumptions are consumed — though each manifest's
    ``run_timestamp`` is necessarily distinct. The caller stamps
    ``EngineResult.provenance_complete = False`` so these partial manifests are
    not mistaken for fully-sourced ones.
    """
    if registries is not None and registries.assumptions is not None:
        collector = ProvenanceCollector(scenario.version_tag, registries.assumptions)
        for label in _OUTPUT_LABELS:
            collector.record(label, PipelineLayer.REVENUE, [])
        return collector.build()

    entries = [
        ProvenanceEntry(output_label=label, layer=PipelineLayer.REVENUE, assumption_ids=[]) for label in _OUTPUT_LABELS
    ]
    return ProvenanceManifest(
        version_tag=scenario.version_tag,
        assumptions_consumed={},
        entries=entries,
    )


def simulate(
    population: PopulationSource,
    scenario: Scenario,
    *,
    registries: Registries | None = None,
    devolution: DevolutionConfig | None = None,
) -> EngineResult:
    """Score ``scenario`` over ``population`` and return an :class:`EngineResult`.

    Wires the building blocks: ``rules.run_scenario`` supplies the canonical
    aggregate total + per-nation revenue (families A-E), and a per-household pass
    attributes that revenue across equal-weight wealth deciles. The decile
    breakdown and the aggregate total are computed by the *same* underlying
    calculators, so ``sum(revenue_by_decile) ~= total_revenue_gbp_bn`` (equal up
    to floating-point summation order — a tested invariant).

    When ``devolution`` (Family G) is supplied, the population is first split by
    nation scope and **only the included subset is scored** — every downstream
    number (total, per-nation, per-decile, household count) reflects the included
    households, and the :class:`DevolutionSplit` summary is attached to the
    result so the excluded nations and their weights stay visible. Family G is a
    territorial-scope layer, so it is an engine argument rather than a member of
    the A-E ``Scenario``.

    The ``PopulationSource`` protocol is structural and presence-only
    (``runtime_checkable`` checks attribute presence, not element types);
    ``list(population.households)`` therefore fails loudly here if a malformed
    population is passed.
    """
    households = list(population.households)

    scored: list[Household] = households
    split = None
    if devolution is not None:
        scored, _excluded, split = split_households_by_scope(households, devolution)

    aggregate = _run_families(scored, scenario)
    decile_central = revenue_by_wealth_decile(scored, scenario.families, n_deciles=N_DECILES)

    return EngineResult(
        scenario=scenario,
        total_revenue_gbp_bn=_point_interval(aggregate.total_revenue_bn),
        revenue_by_nation={nation: _point_interval(value) for nation, value in aggregate.revenue_by_nation.items()},
        revenue_by_decile=[_point_interval(value) for value in decile_central],
        households_scored=len(scored),
        provenance=_build_provenance(scenario, registries),
        population_provenance_ids=list(population.provenance_ids),
        provenance_complete=False,
        devolution_split=split,
    )
