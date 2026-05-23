"""Family A: Annual net wealth taxes.

Blueprint v5 §9 Family A: threshold, rate, tax unit, base (comprehensive or
excluding pensions / main residence / business assets), debt deductibility.

Caution (Blueprint v5): high-threshold annual wealth taxes are extremely
sensitive to top-tail measurement and behavioural assumptions.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from wealthlens_sim.schema.household import AssetType, Household


class TaxUnit(StrEnum):
    INDIVIDUAL = "individual"
    HOUSEHOLD = "household"


class WealthTaxConfig(BaseModel):
    """Configuration for an annual net wealth tax."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    threshold: float = Field(ge=0, description="Minimum taxable wealth (GBP)")
    rate: float = Field(gt=0, le=1, description="Annual tax rate (e.g. 0.01 = 1%)")
    tax_unit: TaxUnit = TaxUnit.INDIVIDUAL
    exempt_asset_types: frozenset[AssetType] = Field(
        default=frozenset(),
        description="Asset types excluded from the tax base",
    )


class WealthTaxResult(BaseModel):
    """Per-household wealth tax computation result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    household_id: str
    taxable_wealth: float = Field(description="Net wealth in the tax base (GBP)")
    tax_liability: float = Field(ge=0, description="Annual tax due (GBP)")
    effective_rate: float = Field(ge=0, description="Tax / total net wealth")
    is_liable: bool


class AggregateRevenue(BaseModel):
    """Population-level revenue estimate from a wealth tax."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total_revenue_bn: float = Field(description="Total revenue (GBP billions)")
    taxpayer_count: float = Field(ge=0, description="Weighted count of liable households")
    population_count: float = Field(ge=0, description="Weighted count of all households")
    mean_liability: float = Field(ge=0, description="Mean tax among liable households (GBP)")
    revenue_by_nation: dict[str, float] = Field(
        default_factory=dict,
        description="Revenue in GBP billions, keyed by Nation value",
    )


def taxable_wealth_for_person(
    assets: list,
    exempt_types: frozenset[AssetType],
) -> float:
    """Compute net wealth in the tax base for a single person."""
    return sum(
        a.net_value
        for a in assets
        if a.asset_type not in exempt_types
    )


def compute_wealth_tax(
    household: Household,
    config: WealthTaxConfig,
) -> WealthTaxResult:
    """Compute annual wealth tax for a single household."""
    if config.tax_unit == TaxUnit.INDIVIDUAL:
        total_liability = 0.0
        total_taxable = 0.0
        for person in household.persons:
            person_wealth = taxable_wealth_for_person(
                person.assets, config.exempt_asset_types
            )
            total_taxable += person_wealth
            excess = max(0.0, person_wealth - config.threshold)
            total_liability += excess * config.rate
    else:
        total_taxable = sum(
            taxable_wealth_for_person(p.assets, config.exempt_asset_types)
            for p in household.persons
        )
        excess = max(0.0, total_taxable - config.threshold)
        total_liability = excess * config.rate

    total_net = household.total_net_wealth
    effective = total_liability / total_net if total_net > 0 else 0.0

    return WealthTaxResult(
        household_id=household.household_id,
        taxable_wealth=total_taxable,
        tax_liability=total_liability,
        effective_rate=effective,
        is_liable=total_liability > 0,
    )


def compute_aggregate_revenue(
    households: list[Household],
    config: WealthTaxConfig,
) -> AggregateRevenue:
    """Compute population-level revenue from a wealth tax across all households."""
    total_revenue = 0.0
    taxpayer_weight = 0.0
    population_weight = 0.0
    liable_count_unweighted = 0
    revenue_by_nation: dict[str, float] = {}

    for hh in households:
        result = compute_wealth_tax(hh, config)
        weighted_liability = result.tax_liability * hh.weight
        total_revenue += weighted_liability
        population_weight += hh.weight

        nation_key = hh.nation.value
        revenue_by_nation[nation_key] = (
            revenue_by_nation.get(nation_key, 0.0) + weighted_liability
        )

        if result.is_liable:
            taxpayer_weight += hh.weight
            liable_count_unweighted += 1

    mean_liability = (
        total_revenue / taxpayer_weight if taxpayer_weight > 0 else 0.0
    )

    nation_bn = {k: v / 1e9 for k, v in revenue_by_nation.items()}

    return AggregateRevenue(
        total_revenue_bn=total_revenue / 1e9,
        taxpayer_count=taxpayer_weight,
        population_count=population_weight,
        mean_liability=mean_liability,
        revenue_by_nation=nation_bn,
    )
