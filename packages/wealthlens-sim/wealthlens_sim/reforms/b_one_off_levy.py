"""Family B: One-off wealth levy.

Blueprint v5 §9 Family B: assessment date, rate and payment period, threshold,
included assets, debt and liquidity treatment, anti-forestalling assumptions,
recent-arrival and emigrant rules, estate interaction.

Caution (Blueprint v5): one-off levies and annual wealth taxes are not
interchangeable. A one-off levy is efficient only if it is credibly unexpected
and credibly one-off.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from wealthlens_sim.reforms.a_annual_wealth import (
    TaxUnit,
    taxable_wealth_for_person,
)
from wealthlens_sim.schema.household import AssetType, Household


class LevyRateBand(BaseModel):
    """A single band in a progressive one-off levy schedule."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    threshold: float = Field(ge=0, description="Band starts at this wealth level (GBP)")
    rate: float = Field(gt=0, le=1, description="Marginal rate for this band")


class OneOffLevyConfig(BaseModel):
    """Configuration for a one-off wealth levy.

    Use ``rate`` for a flat levy above ``threshold``, or ``rate_bands`` for
    progressive schedules.  If ``rate_bands`` is set, ``rate`` and
    ``threshold`` are ignored.

    ``instalment_years`` controls how many years the levy payment is
    spread over.  When > 1 the total liability is unchanged but the
    annual instalment is ``liability / instalment_years``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    threshold: float = Field(ge=0, default=0, description="Minimum taxable wealth (GBP)")
    rate: float = Field(gt=0, le=1, default=0.05, description="One-off levy rate (e.g. 0.05 = 5%)")
    rate_bands: tuple[LevyRateBand, ...] | None = Field(
        default=None,
        description="Progressive rate bands (overrides rate/threshold when set)",
    )
    tax_unit: TaxUnit = TaxUnit.INDIVIDUAL
    exempt_asset_types: frozenset[AssetType] = Field(
        default=frozenset(),
        description="Asset types excluded from the levy base",
    )
    instalment_years: int = Field(
        ge=1, default=1, description="Number of years over which to spread levy payments"
    )


class OneOffLevyResult(BaseModel):
    """Per-household one-off levy computation result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    household_id: str
    taxable_wealth: float = Field(ge=0, description="Non-negative net wealth in the levy base (GBP)")
    levy_liability: float = Field(ge=0, description="Total one-off levy due (GBP)")
    annual_instalment: float = Field(ge=0, description="Annual instalment (levy / instalment_years)")
    effective_rate: float = Field(ge=0, description="Levy / total net wealth (0 if total net wealth <= 0)")
    is_liable: bool


class AggregateOneOffRevenue(BaseModel):
    """Population-level revenue estimate from a one-off wealth levy."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total_revenue_bn: float = Field(description="Total levy revenue (GBP billions)")
    taxpayer_count: float = Field(ge=0, description="Weighted count of liable households")
    population_count: float = Field(ge=0, description="Weighted count of all households")
    liable_sample_count: int = Field(ge=0, description="Unweighted count of liable survey households")
    mean_liability: float = Field(ge=0, description="Population-weighted mean levy among liable households (GBP)")
    annual_instalment_revenue_bn: float = Field(
        description="Annual instalment revenue (total_revenue_bn / instalment_years)"
    )
    revenue_by_nation: dict[str, float] = Field(
        default_factory=dict,
        description="Revenue in GBP billions, keyed by Nation value",
    )


def _compute_liability(wealth: float, config: OneOffLevyConfig) -> float:
    """Compute levy liability for a given wealth amount using flat or progressive rates."""
    if config.rate_bands is not None:
        bands = sorted(config.rate_bands, key=lambda b: b.threshold)
        liability = 0.0
        for i, band in enumerate(bands):
            if wealth <= band.threshold:
                break
            ceiling = bands[i + 1].threshold if i + 1 < len(bands) else wealth
            taxable_in_band = min(wealth, ceiling) - band.threshold
            liability += max(0.0, taxable_in_band) * band.rate
        return liability
    return max(0.0, wealth - config.threshold) * config.rate


def compute_one_off_levy(
    household: Household,
    config: OneOffLevyConfig,
) -> OneOffLevyResult:
    """Compute one-off wealth levy for a single household."""
    if config.tax_unit == TaxUnit.INDIVIDUAL:
        total_liability = 0.0
        total_taxable = 0.0
        for person in household.persons:
            person_wealth = max(0.0, taxable_wealth_for_person(
                person.assets, config.exempt_asset_types
            ))
            total_taxable += person_wealth
            total_liability += _compute_liability(person_wealth, config)
    else:
        total_taxable = max(0.0, sum(
            taxable_wealth_for_person(p.assets, config.exempt_asset_types)
            for p in household.persons
        ))
        total_liability = _compute_liability(total_taxable, config)

    total_net = household.total_net_wealth
    effective = total_liability / total_net if total_net > 0 else 0.0
    annual_instalment = total_liability / config.instalment_years

    return OneOffLevyResult(
        household_id=household.household_id,
        taxable_wealth=total_taxable,
        levy_liability=total_liability,
        annual_instalment=annual_instalment,
        effective_rate=effective,
        is_liable=total_liability > 0,
    )


def compute_aggregate_one_off_revenue(
    households: list[Household],
    config: OneOffLevyConfig,
) -> AggregateOneOffRevenue:
    """Compute population-level revenue from a one-off levy across all households."""
    total_revenue = 0.0
    taxpayer_weight = 0.0
    population_weight = 0.0
    liable_count_unweighted = 0
    revenue_by_nation: dict[str, float] = {}

    for hh in households:
        result = compute_one_off_levy(hh, config)
        weighted_liability = result.levy_liability * hh.weight
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
    total_revenue_bn = total_revenue / 1e9

    return AggregateOneOffRevenue(
        total_revenue_bn=total_revenue_bn,
        taxpayer_count=taxpayer_weight,
        population_count=population_weight,
        liable_sample_count=liable_count_unweighted,
        mean_liability=mean_liability,
        annual_instalment_revenue_bn=total_revenue_bn / config.instalment_years,
        revenue_by_nation=nation_bn,
    )
