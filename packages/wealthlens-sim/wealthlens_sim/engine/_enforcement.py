"""Family F enforcement composition for the engine (Wave 12 PR3c).

Family F (enforcement) is a revenue *uplift modifier*, not a per-household revenue
family, so it composes in the engine rather than in ``rules.run_scenario``. The
compliance-gap model (``reforms.f_enforcement``) is parameterised per HMRC tax
family; this module maps the scenario's revenue families (A-E) onto those tax
families and applies the model to the modeled family revenues.
"""

from __future__ import annotations

from typing import assert_never

from wealthlens_sim.reforms.f_enforcement import (
    AggregateEnforcementRevenue,
    EnforcementConfig,
    TaxFamily,
    compute_enforcement_uplift,
)
from wealthlens_sim.rules.scenario import FamilyRevenue, PolicyFamily


def tax_family_for(policy: PolicyFamily) -> TaxFamily:
    """Map a revenue policy family (A-E) onto an enforcement :class:`TaxFamily`.

    CGT and IHT map directly to their HMRC tax-gap categories. The wealth-tax
    families (annual, one-off) and the HVCTS property surcharge have no dedicated
    HMRC tax-gap category, so they map to ``OTHER`` — meaning a single ``OTHER``
    compliance rate governs their combined uplift (a caller cannot set distinct
    compliance for annual-wealth vs HVCTS in v0.1). This is the documented v0.1
    mapping decision; a finer mapping can replace it once HMRC publishes
    wealth-tax-specific gap estimates. The ``match``/``assert_never`` keeps the
    mapping exhaustive at type-check time.
    """
    match policy:
        case PolicyFamily.CGT:
            return TaxFamily.CGT
        case PolicyFamily.IHT:
            return TaxFamily.IHT
        case PolicyFamily.ANNUAL_WEALTH_TAX | PolicyFamily.ONE_OFF_LEVY | PolicyFamily.HVCTS:
            return TaxFamily.OTHER
        case _:  # pragma: no cover - exhaustiveness guard
            assert_never(policy)


def theoretical_revenues_by_tax_family(
    family_revenues: list[FamilyRevenue],
) -> dict[TaxFamily, float]:
    """Aggregate scenario family revenues (GBP bn) by enforcement tax family."""
    totals: dict[TaxFamily, float] = {}
    for family_revenue in family_revenues:
        tax_family = tax_family_for(family_revenue.family)
        totals[tax_family] = totals.get(tax_family, 0.0) + family_revenue.total_revenue_bn
    return totals


def compute_engine_enforcement(
    family_revenues: list[FamilyRevenue],
    config: EnforcementConfig,
) -> AggregateEnforcementRevenue:
    """Apply the enforcement compliance-gap model to the scenario's family revenues.

    The modeled A-E family revenues are treated as the *theoretical* base for the
    per-tax-family compliance-gap calculation, and the engine then **adds** the
    resulting ``net_uplift_bn`` to the headline total.

    **v0.1 simplification — known to overstate.** The A-E calculators report full
    statutory liability (no compliance/avoidance haircut), i.e. the base already
    *is* the 100%-compliance ceiling. Adding a compliance-gap uplift on top of it
    therefore pushes the headline ABOVE that ceiling, overstating total
    collectible revenue (a coherent model would report ``theoretical *
    scenario_rate`` instead, which is <= theoretical). This additive form is a
    deliberate placeholder until the families gain an explicit baseline-vs-
    theoretical compliance split; enforcement is opt-in (default off) and the
    uplift is reported separately on ``EngineResult.enforcement_uplift_bn`` so it
    can be inspected or removed. See the Wave 12 backlog follow-up.
    """
    theoretical = theoretical_revenues_by_tax_family(family_revenues)
    return compute_enforcement_uplift(theoretical, config)
