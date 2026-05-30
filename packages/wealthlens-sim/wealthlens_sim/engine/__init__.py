"""Static microsimulation engine — wires synth -> rules -> provenance (Wave 12 PR3a).

:func:`run_scenario` is the engine's single entry point: it scores a
:class:`~wealthlens_sim.engine.result.PopulationSource` against a
:class:`~wealthlens_sim.rules.scenario.Scenario` (revenue families A-E) and
returns an :class:`~wealthlens_sim.engine.result.EngineResult` carrying interval
revenue totals, a per-nation and per-wealth-decile breakdown, and a provenance
manifest.

PR3a ships the A-E end-to-end path with **degenerate intervals**
(``low == central == high``); real interval propagation (top-tail alpha sweep +
assumption ``RangeValue``s) lands in PR3c, and Family F (enforcement) + Family G
(devolution) composition lands in PR3b. The ``registries`` seam is already
threaded so those PRs need no signature change.

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
from wealthlens_sim.rules.scenario import Scenario
from wealthlens_sim.rules.scenario import run_scenario as _run_families
from wealthlens_sim.top_tail.types import Interval

__all__ = [
    "N_DECILES",
    "EngineResult",
    "PopulationSource",
    "Registries",
    "household_liability",
    "revenue_by_wealth_decile",
    "run_scenario",
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
    """Build the run's provenance manifest.

    When an assumption registry is supplied the manifest is built through a
    :class:`ProvenanceCollector` (the seam PR3c uses to ``consume`` the top-tail
    alpha + assumption ranges); otherwise it is constructed directly with the
    same REVENUE-layer entries. Both paths yield identical manifests in PR3a
    because no registry assumptions are consumed yet.
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


def run_scenario(
    population: PopulationSource,
    scenario: Scenario,
    *,
    registries: Registries | None = None,
) -> EngineResult:
    """Score ``scenario`` over ``population`` and return an :class:`EngineResult`.

    Wires the building blocks: ``rules.run_scenario`` supplies the canonical
    aggregate total + per-nation revenue (families A-E), and a per-household pass
    attributes that revenue across weighted wealth deciles. The decile breakdown
    and the aggregate total are computed by the *same* underlying calculators, so
    ``sum(revenue_by_decile) == total_revenue_gbp_bn`` (a tested invariant).
    """
    households = list(population.households)

    aggregate = _run_families(households, scenario)
    decile_central = revenue_by_wealth_decile(households, scenario.families, n_deciles=N_DECILES)

    return EngineResult(
        scenario=scenario,
        total_revenue_gbp_bn=_point_interval(aggregate.total_revenue_bn),
        revenue_by_nation={nation: _point_interval(value) for nation, value in aggregate.revenue_by_nation.items()},
        revenue_by_decile=[_point_interval(value) for value in decile_central],
        households_scored=len(households),
        provenance=_build_provenance(scenario, registries),
    )
