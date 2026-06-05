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
    ENFORCEMENT_COMPLIANCE_ASSUMPTION_ID,
    ENFORCEMENT_COMPLIANCE_SOURCE,
    ENFORCEMENT_COMPLIANCE_SOURCE_URLS,
    HMRC_OVERALL_BASELINE_COMPLIANCE_RATE_2023_24,
    HMRC_OVERALL_TAX_GAP_GBP_BN_2023_24,
    HMRC_OVERALL_TAX_GAP_RATE_2023_24,
    HMRC_WEALTHY_COMPLIANCE_YIELD_GBP_BN_2023_24,
    HMRC_WEALTHY_TAX_GAP_GBP_BN_2022_23,
    AggregateEnforcementRevenue,
    ComplianceRate,
    EnforcementConfig,
    EnforcementResult,
    TaxFamily,
    compute_enforcement_uplift,
)
from wealthlens_sim.reforms.g_devolution import (
    DevolutionConfig,
    DevolutionSplit,
    NationScope,
    split_households_by_scope,
)

__all__ = [
    "ENFORCEMENT_COMPLIANCE_ASSUMPTION_ID",
    "ENFORCEMENT_COMPLIANCE_SOURCE",
    "ENFORCEMENT_COMPLIANCE_SOURCE_URLS",
    "HMRC_OVERALL_BASELINE_COMPLIANCE_RATE_2023_24",
    "HMRC_OVERALL_TAX_GAP_GBP_BN_2023_24",
    "HMRC_OVERALL_TAX_GAP_RATE_2023_24",
    "HMRC_WEALTHY_COMPLIANCE_YIELD_GBP_BN_2023_24",
    "HMRC_WEALTHY_TAX_GAP_GBP_BN_2022_23",
    "AggregateCGTRevenue",
    "AggregateEnforcementRevenue",
    "AggregateHVCTSRevenue",
    "AggregateIHTRevenue",
    "AggregateOneOffRevenue",
    "AggregateRevenue",
    "CGTConfig",
    "CGTResult",
    "ComplianceRate",
    "DevolutionConfig",
    "DevolutionSplit",
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
    "NationScope",
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
    "split_households_by_scope",
    "taxable_wealth_for_person",
]
