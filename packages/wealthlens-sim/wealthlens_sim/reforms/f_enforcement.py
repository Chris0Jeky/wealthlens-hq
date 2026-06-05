"""Family F: Enforcement and information reform — compliance gap model.

Blueprint v5 §9 Family F and §3.5: enforcement as a policy family,
not a caveat. Beneficial-ownership reporting, trust/offshore reporting,
wealthy-taxpayer segmentation, valuation-audit resources, compliance
intensity, penalties/interest, data-sharing and anomaly detection.

This is a v0.1 compliance-multiplier model. It models the tax gap as
the difference between theoretical tax liabilities and collected
revenue, parameterised by a compliance rate per tax family.

The core insight: "what if HMRC had better wealth visibility?" may
raise revenue by increasing observability rather than rates.

Key statistics (sources below):
- UK tax gap: £46.8bn (5.3% of theoretical liabilities)
- Wealthy individuals (>£200k income or >£2m assets): ~850,000 in 2023-24
- Wealthy compliance yield: ~£5.2bn in 2023-24
- Wealthy tax gap: ~£1.9bn in 2022-23, the latest year available in the NAO report

Sources:
    HMRC, Measuring tax gaps 2025 edition: tax gaps summary,
    https://www.gov.uk/government/statistics/measuring-tax-gaps/1-tax-gaps-summary,
    accessed 2026-05-30.

    NAO, Collecting the right tax from wealthy individuals,
    https://www.nao.org.uk/reports/collecting-the-right-tax-from-wealthy-individuals/,
    accessed 2026-05-30.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

HMRC_OVERALL_TAX_GAP_RATE_2023_24 = 0.053
HMRC_OVERALL_BASELINE_COMPLIANCE_RATE_2023_24 = 1.0 - HMRC_OVERALL_TAX_GAP_RATE_2023_24
HMRC_OVERALL_TAX_GAP_GBP_BN_2023_24 = 46.8
HMRC_WEALTHY_TAX_GAP_GBP_BN_2022_23 = 1.9
HMRC_WEALTHY_COMPLIANCE_YIELD_GBP_BN_2023_24 = 5.2
HMRC_OVERALL_TAX_GAP_SOURCE = (
    "HMRC, Measuring tax gaps 2025 edition: tax gaps summary, "
    "https://www.gov.uk/government/statistics/measuring-tax-gaps/1-tax-gaps-summary, accessed 2026-05-30"
)
NAO_WEALTHY_TAX_SOURCE = (
    "NAO, Collecting the right tax from wealthy individuals, "
    "https://www.nao.org.uk/reports/collecting-the-right-tax-from-wealthy-individuals/, accessed 2026-05-30"
)
ENFORCEMENT_COMPLIANCE_ASSUMPTION_ID = "model.enforcement.compliance_rates.v0_1"
ENFORCEMENT_COMPLIANCE_SOURCE = f"{HMRC_OVERALL_TAX_GAP_SOURCE}; {NAO_WEALTHY_TAX_SOURCE}"
#: Machine-readable URLs for ENFORCEMENT_COMPLIANCE_SOURCE. The enforcement assumption
#: is injected into provenance by the engine (not loaded via the registry), so it must
#: carry its own source_urls to match the data-integrity guarantee for every other
#: consumed assumption.
ENFORCEMENT_COMPLIANCE_SOURCE_URLS = (
    "https://www.gov.uk/government/statistics/measuring-tax-gaps/1-tax-gaps-summary",
    "https://www.nao.org.uk/reports/collecting-the-right-tax-from-wealthy-individuals/",
)


class TaxFamily(StrEnum):
    """Tax families for which compliance rates can be set."""

    INCOME_TAX = "income_tax"
    CGT = "cgt"
    IHT = "iht"
    VAT = "vat"
    CORPORATION_TAX = "corporation_tax"
    OTHER = "other"


class ComplianceRate(BaseModel):
    """Compliance rate for a single tax family."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tax_family: TaxFamily
    baseline_rate: float = Field(
        default=HMRC_OVERALL_BASELINE_COMPLIANCE_RATE_2023_24,
        ge=0,
        le=1,
        description=(
            "Current-law compliance rate (fraction of theoretical revenue collected); "
            "default is HMRC's 2023-24 all-tax baseline implied by a 5.3% tax gap"
        ),
    )
    scenario_rate: float = Field(
        default=1.0,
        ge=0,
        le=1,
        description="Reform-scenario compliance rate after enforcement changes",
    )

    @model_validator(mode="after")
    def _scenario_not_below_baseline(self) -> ComplianceRate:
        if self.scenario_rate < self.baseline_rate:
            msg = (
                f"scenario_rate ({self.scenario_rate}) must not be below "
                f"baseline_rate ({self.baseline_rate})"
            )
            raise ValueError(msg)
        return self


class EnforcementConfig(BaseModel):
    """Configuration for enforcement/compliance gap modelling.

    Each ComplianceRate entry defines a baseline and scenario compliance
    rate for one tax family. The enforcement model computes the revenue
    uplift from moving from baseline to scenario compliance.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    compliance_rates: tuple[ComplianceRate, ...] = Field(
        min_length=1,
        description="Compliance rates per tax family",
    )
    enforcement_cost_bn: float = Field(
        default=0.0, ge=0,
        description="Estimated additional HMRC enforcement cost (GBP billions)",
    )

    @model_validator(mode="after")
    def _unique_families(self) -> EnforcementConfig:
        families = [cr.tax_family for cr in self.compliance_rates]
        if len(families) != len(set(families)):
            msg = "compliance_rates must have unique tax_family values"
            raise ValueError(msg)
        return self


class EnforcementResult(BaseModel):
    """Per-tax-family enforcement revenue uplift."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tax_family: TaxFamily
    theoretical_revenue_bn: float = Field(
        ge=0, description="Theoretical full-compliance revenue (GBP billions)",
    )
    baseline_revenue_bn: float = Field(
        ge=0, description="Revenue at baseline compliance (GBP billions)",
    )
    scenario_revenue_bn: float = Field(
        ge=0, description="Revenue at scenario compliance (GBP billions)",
    )
    revenue_uplift_bn: float = Field(
        ge=0, description="Additional revenue from improved compliance (GBP billions)",
    )
    baseline_gap_bn: float = Field(
        ge=0, description="Tax gap at baseline compliance (GBP billions)",
    )
    gap_closed_fraction: float = Field(
        ge=0, le=1,
        description="Fraction of baseline gap closed by the scenario",
    )


class AggregateEnforcementRevenue(BaseModel):
    """Aggregate enforcement revenue uplift across all tax families."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    family_results: tuple[EnforcementResult, ...]
    total_uplift_bn: float = Field(
        ge=0, description="Total revenue uplift across all families (GBP billions)",
    )
    total_theoretical_bn: float = Field(
        ge=0, description="Total theoretical revenue (GBP billions)",
    )
    total_baseline_revenue_bn: float = Field(
        ge=0, description="Total revenue at baseline compliance (GBP billions)",
    )
    total_scenario_revenue_bn: float = Field(
        ge=0, description="Total revenue at scenario compliance before enforcement cost (GBP billions)",
    )
    total_baseline_gap_bn: float = Field(
        ge=0, description="Total tax gap at baseline (GBP billions)",
    )
    enforcement_cost_bn: float = Field(
        ge=0, description="Estimated additional HMRC enforcement cost (GBP billions)",
    )
    net_uplift_bn: float = Field(
        description="Revenue uplift minus enforcement cost (GBP billions)",
    )


def compute_enforcement_uplift(
    theoretical_revenues: dict[TaxFamily, float],
    config: EnforcementConfig,
) -> AggregateEnforcementRevenue:
    """Compute enforcement revenue uplift from compliance improvements.

    theoretical_revenues: mapping from TaxFamily to theoretical
    full-compliance revenue in GBP billions.
    """
    family_results: list[EnforcementResult] = []

    for cr in config.compliance_rates:
        theoretical = theoretical_revenues.get(cr.tax_family, 0.0)
        if theoretical < 0:
            theoretical = 0.0

        baseline_rev = theoretical * cr.baseline_rate
        scenario_rev = theoretical * cr.scenario_rate
        uplift = scenario_rev - baseline_rev
        baseline_gap = theoretical - baseline_rev
        gap_closed = uplift / baseline_gap if baseline_gap > 0 else 0.0

        family_results.append(EnforcementResult(
            tax_family=cr.tax_family,
            theoretical_revenue_bn=theoretical,
            baseline_revenue_bn=baseline_rev,
            scenario_revenue_bn=scenario_rev,
            revenue_uplift_bn=uplift,
            baseline_gap_bn=baseline_gap,
            gap_closed_fraction=gap_closed,
        ))

    total_uplift = sum(r.revenue_uplift_bn for r in family_results)
    total_theoretical = sum(r.theoretical_revenue_bn for r in family_results)
    total_baseline_revenue = sum(r.baseline_revenue_bn for r in family_results)
    total_scenario_revenue = sum(r.scenario_revenue_bn for r in family_results)
    total_gap = sum(r.baseline_gap_bn for r in family_results)

    return AggregateEnforcementRevenue(
        family_results=tuple(family_results),
        total_uplift_bn=total_uplift,
        total_theoretical_bn=total_theoretical,
        total_baseline_revenue_bn=total_baseline_revenue,
        total_scenario_revenue_bn=total_scenario_revenue,
        total_baseline_gap_bn=total_gap,
        enforcement_cost_bn=config.enforcement_cost_bn,
        net_uplift_bn=total_uplift - config.enforcement_cost_bn,
    )
