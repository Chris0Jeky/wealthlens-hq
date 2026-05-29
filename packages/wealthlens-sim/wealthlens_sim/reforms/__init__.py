"""Policy family reform modules (Families A--G).

Each module implements one policy family from the WealthLens scenario universe
(Blueprint v5 section 9). Reforms follow PolicyEngine-UK conventions.

Blueprint v5 §13.6 uses ``policies/`` for this directory. This repo uses
``reforms/`` to align with PolicyEngine-UK naming and to distinguish reform
code from the broader scenario/package/revenue-equivalent-set layer that
will live in the ``rules/`` module.
"""

from wealthlens_sim.reforms._banding import RateBand
from wealthlens_sim.reforms.a_annual_wealth import (
    AggregateRevenue,
    TaxUnit,
    WealthTaxConfig,
    WealthTaxResult,
    compute_aggregate_revenue,
    compute_wealth_tax,
    taxable_wealth_for_person,
)
from wealthlens_sim.reforms.b_one_off_levy import (
    AggregateOneOffRevenue,
    LevyRateBand,
    OneOffLevyConfig,
    OneOffLevyResult,
    compute_aggregate_one_off_revenue,
    compute_one_off_levy,
)
from wealthlens_sim.reforms.c_cgt_reform import (
    AggregateCGTRevenue,
    CGTConfig,
    CGTResult,
    HouseholdCGTResult,
    TaxpayerType,
    compute_aggregate_cgt_revenue,
    compute_household_cgt,
)
from wealthlens_sim.reforms.d_iht_reform import (
    AggregateIHTRevenue,
    HouseholdIHTResult,
    IHTConfig,
    IHTResult,
    PersonIHTFlags,
    compute_aggregate_iht_revenue,
    compute_household_iht,
)
from wealthlens_sim.reforms.e_property_tax import (
    AggregateHVCTSRevenue,
    HVCTSBand,
    HVCTSConfig,
    HVCTSResult,
    compute_aggregate_hvcts_revenue,
    compute_hvcts,
)
from wealthlens_sim.reforms.f_enforcement import (
    AggregateEnforcementRevenue,
    ComplianceRate,
    EnforcementConfig,
    EnforcementResult,
    TaxFamily,
    compute_enforcement_uplift,
)

__all__ = [
    "AggregateCGTRevenue",
    "AggregateEnforcementRevenue",
    "AggregateHVCTSRevenue",
    "AggregateIHTRevenue",
    "AggregateOneOffRevenue",
    "AggregateRevenue",
    "CGTConfig",
    "CGTResult",
    "ComplianceRate",
    "EnforcementConfig",
    "EnforcementResult",
    "HVCTSBand",
    "HVCTSConfig",
    "HVCTSResult",
    "HouseholdCGTResult",
    "HouseholdIHTResult",
    "IHTConfig",
    "IHTResult",
    "LevyRateBand",
    "OneOffLevyConfig",
    "OneOffLevyResult",
    "PersonIHTFlags",
    "RateBand",
    "TaxFamily",
    "TaxUnit",
    "TaxpayerType",
    "WealthTaxConfig",
    "WealthTaxResult",
    "compute_aggregate_cgt_revenue",
    "compute_aggregate_hvcts_revenue",
    "compute_aggregate_iht_revenue",
    "compute_aggregate_one_off_revenue",
    "compute_aggregate_revenue",
    "compute_enforcement_uplift",
    "compute_household_cgt",
    "compute_household_iht",
    "compute_hvcts",
    "compute_one_off_levy",
    "compute_wealth_tax",
    "taxable_wealth_for_person",
]
