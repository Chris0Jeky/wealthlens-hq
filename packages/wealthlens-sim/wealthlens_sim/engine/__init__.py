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
from wealthlens_sim.engine._enforcement import (
    baseline_compliance_rate_for,
    compute_engine_enforcement,
    tax_family_for,
)
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
    ResolvedAssumption,
)
from wealthlens_sim.reforms.f_enforcement import (
    ENFORCEMENT_COMPLIANCE_ASSUMPTION_ID,
    ENFORCEMENT_COMPLIANCE_SOURCE,
    EnforcementConfig,
)
from wealthlens_sim.reforms.g_devolution import (
    DevolutionConfig,
    DevolutionSplit,
    split_households_by_scope,
)
from wealthlens_sim.rules.scenario import FamilyRevenue, FamilySelection, Scenario
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

#: Labels recorded in the provenance manifest, one per published output — every
#: number the dashboard contract emits must have a corresponding trail, including
#: the enforcement uplift (zero when no enforcement config is supplied).
_OUTPUT_LABELS = (
    "total_revenue_gbp_bn",
    "revenue_by_nation",
    "revenue_by_decile",
    "enforcement_uplift_gbp_bn",
    "enforcement_cost_gbp_bn",
    "enforcement_net_fiscal_impact_gbp_bn",
)
_ALPHA_OUTPUT_LABELS = (
    "total_revenue_gbp_bn",
    "revenue_by_nation",
    "revenue_by_decile",
)
_ENFORCEMENT_REVENUE_OUTPUT_LABELS = (
    "enforcement_uplift_gbp_bn",
    "enforcement_net_fiscal_impact_gbp_bn",
)


def _build_complete_provenance(
    scenario: Scenario,
    registries: Registries,
    *,
    devolution: DevolutionConfig | None,
    enforcement: EnforcementConfig | None,
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
        assumption_ids: list[str] = []
        if label in _ALPHA_OUTPUT_LABELS or (enforcement is not None and label in _ENFORCEMENT_REVENUE_OUTPUT_LABELS):
            assumption_ids.append(PARETO_ALPHA_ASSUMPTION_ID)
        collector.record(label, PipelineLayer.REVENUE, assumption_ids)
    if devolution is not None:
        collector.record(f"devolution_scope:{devolution.scope.value}", PipelineLayer.POLICY_RULES, [])
    manifest = collector.build()
    if enforcement is None:
        return manifest

    enforcement_assumption = ResolvedAssumption(
        assumption_id=ENFORCEMENT_COMPLIANCE_ASSUMPTION_ID,
        domain="tax-compliance",
        resolved_value={
            "compliance_rates": [
                {
                    "tax_family": rate.tax_family.value,
                    "baseline_rate": rate.baseline_rate,
                    "scenario_rate": rate.scenario_rate,
                }
                for rate in enforcement.compliance_rates
            ],
            "enforcement_cost_bn": enforcement.enforcement_cost_bn,
        },
        source=ENFORCEMENT_COMPLIANCE_SOURCE,
    )
    assumptions = {
        **manifest.assumptions_consumed,
        ENFORCEMENT_COMPLIANCE_ASSUMPTION_ID: enforcement_assumption,
    }
    entries = [
        entry.model_copy(
            update={"assumption_ids": [*entry.assumption_ids, ENFORCEMENT_COMPLIANCE_ASSUMPTION_ID]}
        )
        if entry.output_label in _OUTPUT_LABELS
        else entry
        for entry in manifest.entries
    ]
    return manifest.model_copy(update={"assumptions_consumed": assumptions, "entries": entries})


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


def _baseline_revenue_by_nation(
    family_revenues: list[FamilyRevenue],
    enforcement: EnforcementConfig | None,
) -> dict[str, float]:
    """Return nation revenue after baseline compliance rates when F is enabled."""
    merged: dict[str, float] = {}
    for family_revenue in family_revenues:
        rate = 1.0
        if enforcement is not None:
            rate = baseline_compliance_rate_for(family_revenue.family, enforcement)
        for nation, revenue in family_revenue.revenue_by_nation.items():
            merged[nation] = merged.get(nation, 0.0) + revenue * rate
    return merged


def _baseline_revenue_by_decile(
    households: list[Household],
    scenario: Scenario,
    enforcement: EnforcementConfig | None,
) -> list[float]:
    """Return decile revenue after baseline compliance rates when F is enabled."""
    if not households:
        return []
    if enforcement is None:
        return revenue_by_wealth_decile(households, scenario.families, n_deciles=N_DECILES)

    rates_to_selections: dict[float, list[FamilySelection]] = {}
    for selection in scenario.families:
        rate = baseline_compliance_rate_for(selection.family, enforcement)
        rates_to_selections.setdefault(rate, []).append(selection)

    deciles = [0.0] * N_DECILES
    for rate, selections in rates_to_selections.items():
        family_deciles = revenue_by_wealth_decile(households, selections, n_deciles=N_DECILES)
        for i, value in enumerate(family_deciles):
            deciles[i] += value * rate
    return deciles


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

    When ``enforcement`` (Family F) is supplied, the A-E family revenues are
    treated as theoretical full-compliance liability. The compliance-gap model
    first converts them to baseline collected revenue, then adds the gross
    revenue uplift from moving from baseline to scenario compliance. Enforcement
    cost is expenditure, not revenue, and is surfaced separately as net fiscal
    impact. The uplift is an aggregate figure and is NOT attributed to nation or decile,
    so the decile invariant remains
    ``sum(revenue_by_decile) ~= total_revenue_gbp_bn - enforcement_uplift_bn``.
    Family F is a revenue-uplift modifier, so — like G — it is an engine argument
    rather than an A-E ``Scenario`` member. The aggregate gross uplift, cost, and
    net fiscal impact are surfaced; the full per-family/gap breakdown is
    intentionally not on ``EngineResult`` in v0.1 and is recomputable via
    ``compute_engine_enforcement``.

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
    decile_central = _baseline_revenue_by_decile(scored, scenario, enforcement)
    revenue_by_nation = _baseline_revenue_by_nation(aggregate.family_revenues, enforcement)
    baseline_family_revenue = sum(decile_central)

    enforcement_uplift = 0.0
    enforcement_cost = 0.0
    if enforcement is not None:
        enforcement_result = compute_engine_enforcement(aggregate.family_revenues, enforcement)
        enforcement_uplift = enforcement_result.total_uplift_bn
        enforcement_cost = enforcement_result.enforcement_cost_bn
    else:
        baseline_family_revenue = aggregate.total_revenue_bn

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

    def net_fiscal_interval(gross_uplift: float, cost: float) -> Interval:
        gross = interval(gross_uplift)
        return Interval(
            low=gross.low - cost,
            central=gross.central - cost,
            high=gross.high - cost,
        )

    if alpha is not None and registries is not None:
        provenance = _build_complete_provenance(scenario, registries, devolution=devolution, enforcement=enforcement)
    else:
        provenance = _build_incomplete_provenance(scenario)

    return EngineResult(
        scenario=scenario,
        total_revenue_gbp_bn=interval(baseline_family_revenue + enforcement_uplift),
        revenue_by_nation={nation: interval(value) for nation, value in revenue_by_nation.items()},
        revenue_by_decile=[interval(value) for value in decile_central],
        enforcement_uplift_bn=interval(enforcement_uplift),
        enforcement_cost_bn=Interval(low=enforcement_cost, central=enforcement_cost, high=enforcement_cost),
        enforcement_net_fiscal_impact_bn=net_fiscal_interval(enforcement_uplift, enforcement_cost),
        households_scored=len(scored),
        provenance=provenance,
        population_provenance_ids=list(population.provenance_ids),
        provenance_complete=alpha is not None,
        devolution_split=split,
    )
