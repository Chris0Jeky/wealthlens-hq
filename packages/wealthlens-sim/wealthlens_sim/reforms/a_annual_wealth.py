"""Family A: Annual net wealth taxes.

Blueprint v5 §9 Family A: threshold, rate, tax unit, base (comprehensive or
excluding pensions / main residence / business assets), debt deductibility.

Caution (Blueprint v5): high-threshold annual wealth taxes are extremely
sensitive to top-tail measurement and behavioural assumptions.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.reforms._banding import RateBand, compute_banded_liability
from wealthlens_sim.schema.household import Asset, AssetType, Household


class TaxUnit(StrEnum):
    INDIVIDUAL = "individual"
    HOUSEHOLD = "household"


class WealthTaxConfig(BaseModel):
    """Configuration for an annual net wealth tax.

    Use `rate` for a flat tax above `threshold`, or `rate_bands` for
    progressive schedules. Wealth below the first band's threshold is
    untaxed (implicit 0% band).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    threshold: float = Field(ge=0, default=0, description="Minimum taxable wealth (GBP)")
    rate: float = Field(gt=0, le=1, default=0.01, description="Annual tax rate (e.g. 0.01 = 1%)")
    rate_bands: tuple[RateBand, ...] | None = Field(
        default=None,
        min_length=1,
        description="Progressive rate bands (overrides rate/threshold when set)",
    )
    tax_unit: TaxUnit = TaxUnit.INDIVIDUAL
    exempt_asset_types: frozenset[AssetType] = Field(
        default=frozenset(),
        description="Asset types excluded from the tax base",
    )

    @model_validator(mode="after")
    def _validate_rate_bands(self) -> WealthTaxConfig:
        if self.rate_bands is not None:
            thresholds = [b.threshold for b in self.rate_bands]
            if len(thresholds) != len(set(thresholds)):
                msg = "rate_bands must have unique thresholds"
                raise ValueError(msg)
            if self.threshold != 0 or self.rate != 0.01:
                msg = (
                    "When rate_bands is set, threshold and rate are ignored; "
                    "leave them at defaults or omit them"
                )
                raise ValueError(msg)
        return self


class WealthTaxResult(BaseModel):
    """Per-household wealth tax computation result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    household_id: str
    taxable_wealth: float = Field(ge=0, description="Non-negative net wealth in the tax base (GBP)")
    tax_liability: float = Field(ge=0, description="Annual tax due (GBP)")
    effective_rate: float = Field(ge=0, description="Tax / total net wealth (0 if total net wealth <= 0)")
    is_liable: bool


class AggregateRevenue(BaseModel):
    """Population-level revenue estimate from a wealth tax."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total_revenue_bn: float = Field(description="Total revenue (GBP billions)")
    taxpayer_count: float = Field(ge=0, description="Weighted count of liable households")
    population_count: float = Field(ge=0, description="Weighted count of all households")
    liable_sample_count: int = Field(ge=0, description="Unweighted count of liable survey households")
    mean_liability: float = Field(ge=0, description="Population-weighted mean tax among liable households (GBP)")
    revenue_by_nation: dict[str, float] = Field(
        default_factory=dict,
        description="Revenue in GBP billions, keyed by Nation value",
    )


def _compute_liability(wealth: float, config: WealthTaxConfig) -> float:
    """Compute tax liability for a given wealth amount using flat or progressive rates."""
    if wealth <= 0:
        return 0.0
    if config.rate_bands is not None:
        return compute_banded_liability(wealth, config.rate_bands)
    return max(0.0, wealth - config.threshold) * config.rate


def taxable_wealth_for_person(
    assets: list[Asset],
    exempt_types: frozenset[AssetType],
) -> float:
    """Compute non-negative net wealth in the tax base for a single person."""
    return max(0.0, sum(
        a.net_value
        for a in assets
        if a.asset_type not in exempt_types
    ))


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
            total_liability += _compute_liability(person_wealth, config)
    else:
        total_taxable = sum(
            taxable_wealth_for_person(p.assets, config.exempt_asset_types)
            for p in household.persons
        )
        total_liability = _compute_liability(total_taxable, config)

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
        liable_sample_count=liable_count_unweighted,
        mean_liability=mean_liability,
        revenue_by_nation=nation_bn,
    )
