"""Static microsimulation engine — wires synth -> rules -> provenance (Wave 12 PR3a).

:func:`simulate` is the engine's single entry point: it scores a
:class:`~wealthlens_sim.engine.result.PopulationSource` against a
:class:`~wealthlens_sim.rules.scenario.Scenario` (revenue families A-E) and
returns an :class:`~wealthlens_sim.engine.result.EngineResult` carrying interval
revenue totals, a per-nation and per-wealth-decile breakdown, and a provenance
manifest. It is named ``simulate`` (not ``run_scenario``) to avoid colliding with
``rules.run_scenario``, which has a different signature and return type.

Given a ``registries`` bundle carrying the top-tail Pareto alpha range, the engine
propagates genuine ``low``/``central``/``high`` revenue intervals (see
``_intervals``) and emits a **complete** provenance manifest that consumes the
alpha and records it against each published output
(``EngineResult.provenance_complete is True``). Without a registry it falls back to
**degenerate intervals** (``low == central == high``) and an incomplete manifest
(``provenance_complete is False``) — the uncertainty is unquantified. Family G
(devolution) composes here as of PR3b and Family F (enforcement) as of PR3c (via
the ``_enforcement`` helper). Richer per-parameter / Monte-Carlo uncertainty is the
genuinely-deferred Wave 13 (``uncertainty/``) work.

Reference: docs/WAVE12_SIMULATION_ENGINE_DESIGN.md §5.
"""

from __future__ import annotations

from wealthlens_sim.engine._attribution import household_liability, revenue_by_wealth_decile
from wealthlens_sim.engine._enforcement import compute_engine_enforcement, tax_family_for
from wealthlens_sim.engine._intervals import (
    PARETO_ALPHA_ASSUMPTION_ID,
    alpha_interval_from_registry,
    revenue_scale_from_alpha,
    scaled_interval,
)
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
from wealthlens_sim.reforms.f_enforcement import EnforcementConfig
from wealthlens_sim.reforms.g_devolution import (
    DevolutionConfig,
    DevolutionSplit,
    split_households_by_scope,
)
from wealthlens_sim.rules.scenario import Scenario
from wealthlens_sim.rules.scenario import run_scenario as _run_families
from wealthlens_sim.schema.household import Household
from wealthlens_sim.top_tail.types import Interval

__all__ = [
    "N_DECILES",
    "DevolutionConfig",
    "DevolutionSplit",
    "EnforcementConfig",
    "EngineResult",
    "PopulationSource",
    "Registries",
    "household_liability",
    "revenue_by_wealth_decile",
    "simulate",
    "tax_family_for",
]

#: Labels recorded in the provenance manifest, one per published output.
_OUTPUT_LABELS = ("total_revenue_gbp_bn", "revenue_by_nation", "revenue_by_decile")


def _build_complete_provenance(
    scenario: Scenario,
    registries: Registries,
    *,
    devolution: DevolutionConfig | None,
) -> ProvenanceManifest:
    """Build a complete provenance manifest through the collector.

    Consumes the top-tail alpha assumption (which drives the revenue intervals)
    and records it against every published revenue output. When a devolution
    scope was applied, a POLICY_RULES entry records the territorial scope so the
    manifest reflects the geography the numbers were computed under.
    """
    assert registries.assumptions is not None
    collector = ProvenanceCollector(scenario.version_tag, registries.assumptions)
    collector.consume(PARETO_ALPHA_ASSUMPTION_ID)
    for label in _OUTPUT_LABELS:
        collector.record(label, PipelineLayer.REVENUE, [PARETO_ALPHA_ASSUMPTION_ID])
    if devolution is not None:
        collector.record(f"devolution_scope:{devolution.scope.value}", PipelineLayer.POLICY_RULES, [])
    return collector.build()


def _build_incomplete_provenance(scenario: Scenario) -> ProvenanceManifest:
    """Build a known-incomplete manifest when no assumption registry is supplied.

    Records the published-output labels with no consumed assumptions; the caller
    stamps ``provenance_complete = False`` and the revenue intervals are degenerate
    (uncertainty unquantified without the registry).
    """
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
    enforcement: EnforcementConfig | None = None,
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

    When ``enforcement`` (Family F) is supplied, the compliance-gap model is
    applied to the scenario's family revenues and its net uplift (revenue gained
    minus enforcement cost) is **added to** ``total_revenue_gbp_bn`` and reported
    separately on ``enforcement_uplift_bn``. The uplift is an aggregate figure and
    is NOT attributed to nation or decile, so the decile invariant becomes
    ``sum(revenue_by_decile) ~= total_revenue_gbp_bn - enforcement_uplift_bn``.
    Family F is a revenue-uplift modifier, so — like G — it is an engine argument
    rather than an A-E ``Scenario`` member. Only the net uplift is surfaced; the
    full per-family/gross/gap breakdown is intentionally not on ``EngineResult``
    in v0.1 and is recomputable via ``compute_engine_enforcement``. **Caveat:** the
    A-E calculators report full statutory liability, so adding the uplift on top
    can push the headline above the 100%-compliance ceiling — see
    ``_enforcement.compute_engine_enforcement`` for the v0.1 simplification.

    **Revenue intervals.** When ``registries`` supplies the top-tail Pareto alpha
    range, every revenue figure carries a genuine ``low``/``central``/``high``
    interval propagated multiplicatively from that range (see ``_intervals``), and
    the provenance manifest consumes the alpha so ``provenance_complete is True``.
    Without a registry the intervals are degenerate (``low == central == high``)
    and ``provenance_complete is False`` — the uncertainty is unquantified.

    The ``PopulationSource`` protocol is structural and presence-only
    (``runtime_checkable`` checks attribute presence, not element types);
    ``list(population.households)`` therefore fails loudly here if a malformed
    population is passed.
    """
    households = list(population.households)

    scored: list[Household] = households
    split: DevolutionSplit | None = None
    if devolution is not None:
        # The excluded households are intentionally dropped: the DevolutionSplit
        # summary (counts/weights/nations) is the contract, and only the included
        # subset is scored. Do not "restore" the excluded list without a consumer.
        scored, _excluded, split = split_households_by_scope(households, devolution)

    aggregate = _run_families(scored, scenario)
    decile_central = revenue_by_wealth_decile(scored, scenario.families, n_deciles=N_DECILES)

    enforcement_uplift = 0.0
    if enforcement is not None:
        enforcement_uplift = compute_engine_enforcement(aggregate.family_revenues, enforcement).net_uplift_bn

    # Interval propagation: derive low/high revenue factors from the top-tail alpha
    # range if the registry provides it; otherwise fall back to degenerate (1.0,
    # 1.0) factors. The same factors scale every published figure uniformly (a
    # documented v0.1 single-uncertainty-source simplification).
    alpha = None
    if registries is not None and registries.assumptions is not None:
        alpha = alpha_interval_from_registry(registries.assumptions)
    scale_low, scale_high = revenue_scale_from_alpha(alpha) if alpha is not None else (1.0, 1.0)

    def interval(value: float) -> Interval:
        return scaled_interval(value, scale_low, scale_high)

    if alpha is not None and registries is not None:
        provenance = _build_complete_provenance(scenario, registries, devolution=devolution)
    else:
        provenance = _build_incomplete_provenance(scenario)

    return EngineResult(
        scenario=scenario,
        total_revenue_gbp_bn=interval(aggregate.total_revenue_bn + enforcement_uplift),
        revenue_by_nation={nation: interval(value) for nation, value in aggregate.revenue_by_nation.items()},
        revenue_by_decile=[interval(value) for value in decile_central],
        enforcement_uplift_bn=interval(enforcement_uplift),
        households_scored=len(scored),
        provenance=provenance,
        population_provenance_ids=list(population.provenance_ids),
        provenance_complete=alpha is not None,
        devolution_split=split,
    )
