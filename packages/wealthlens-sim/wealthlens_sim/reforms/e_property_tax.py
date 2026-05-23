"""Family E: Property-tax reform — HVCTS sub-module.

Blueprint v5 §9 Family E and §3.4: High Value Council Tax Surcharge.
England-only annual surcharge on residential properties valued at £2m+.

GOV.UK consultation published 19 May 2026 (closes 14 July 2026).
Proposed bands: £2-2.5m £2,500; £2.5-3.5m £3,500; £3.5-5m £5,000; £5m+ £7,500.
OBR estimate: ~£0.4bn in 2029-30.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.schema.base import Nation
from wealthlens_sim.schema.household import Asset, AssetType, Household

PROPERTY_TYPES: frozenset[AssetType] = frozenset({
    AssetType.MAIN_RESIDENCE,
    AssetType.OTHER_PROPERTY,
})


class HVCTSBand(BaseModel):
    """A single HVCTS surcharge band."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    lower: float = Field(ge=0, description="Band lower bound (GBP, inclusive)")
    upper: float | None = Field(
        default=None, description="Band upper bound (GBP, exclusive); None = no cap"
    )
    annual_surcharge: float = Field(gt=0, description="Fixed annual surcharge (GBP)")

    @model_validator(mode="after")
    def _upper_exceeds_lower(self) -> HVCTSBand:
        if self.upper is not None and self.upper <= self.lower:
            msg = f"upper ({self.upper}) must exceed lower ({self.lower})"
            raise ValueError(msg)
        return self


ANNOUNCED_BANDS: tuple[HVCTSBand, ...] = (
    HVCTSBand(lower=2_000_000, upper=2_500_000, annual_surcharge=2_500),
    HVCTSBand(lower=2_500_000, upper=3_500_000, annual_surcharge=3_500),
    HVCTSBand(lower=3_500_000, upper=5_000_000, annual_surcharge=5_000),
    HVCTSBand(lower=5_000_000, upper=None, annual_surcharge=7_500),
)


class HVCTSConfig(BaseModel):
    """Configuration for the High Value Council Tax Surcharge.

    Defaults to the announced consultation parameters (England-only,
    April 2028 start, 4 bands from £2m).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    bands: tuple[HVCTSBand, ...] = Field(
        default=ANNOUNCED_BANDS,
        min_length=1,
        description="Surcharge bands by property value",
    )
    nation: Nation = Field(
        default=Nation.ENGLAND,
        description="Nation to which the surcharge applies",
    )
    property_types: frozenset[AssetType] = Field(
        default=PROPERTY_TYPES,
        description="Asset types subject to HVCTS",
    )

    @model_validator(mode="after")
    def _validate_bands(self) -> HVCTSConfig:
        lowers = [b.lower for b in self.bands]
        if len(lowers) != len(set(lowers)):
            msg = "bands must have unique lower bounds"
            raise ValueError(msg)
        if self.nation == Nation.UK:
            msg = "HVCTS must target a constituent nation, not UK aggregate"
            raise ValueError(msg)
        return self


def _surcharge_for_property(value: float, bands: tuple[HVCTSBand, ...]) -> float:
    """Compute the HVCTS surcharge for a single property."""
    if value <= 0:
        return 0.0
    sorted_bands = sorted(bands, key=lambda b: b.lower)
    for band in sorted_bands:
        in_band = value >= band.lower and (band.upper is None or value < band.upper)
        if in_band:
            return band.annual_surcharge
    return 0.0


class HVCTSResult(BaseModel):
    """Per-household HVCTS computation result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    household_id: str
    properties_in_scope: int = Field(ge=0, description="Count of properties subject to HVCTS")
    total_surcharge: float = Field(ge=0, description="Annual HVCTS due (GBP)")
    is_liable: bool


class AggregateHVCTSRevenue(BaseModel):
    """Population-level HVCTS revenue estimate."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total_revenue_bn: float = Field(description="Total HVCTS revenue (GBP billions)")
    liable_household_count: float = Field(ge=0, description="Weighted count of liable households")
    population_count: float = Field(ge=0, description="Weighted count of all in-scope households")
    liable_sample_count: int = Field(ge=0, description="Unweighted count of liable survey households")
    properties_in_scope: float = Field(ge=0, description="Weighted count of properties subject to HVCTS")
    mean_surcharge: float = Field(ge=0, description="Mean surcharge among liable households (GBP)")


def _eligible_properties(household: Household, config: HVCTSConfig) -> list[Asset]:
    """Return residential properties in the target nation eligible for HVCTS."""
    if household.nation != config.nation:
        return []
    return [
        a
        for p in household.persons
        for a in p.assets
        if a.asset_type in config.property_types and a.gross_value >= config.bands[0].lower
    ]


def compute_hvcts(
    household: Household,
    config: HVCTSConfig,
) -> HVCTSResult:
    """Compute HVCTS surcharge for a single household."""
    properties = _eligible_properties(household, config)
    sorted_bands = tuple(sorted(config.bands, key=lambda b: b.lower))
    total = sum(_surcharge_for_property(a.gross_value, sorted_bands) for a in properties)

    return HVCTSResult(
        household_id=household.household_id,
        properties_in_scope=len(properties),
        total_surcharge=total,
        is_liable=total > 0,
    )


def compute_aggregate_hvcts_revenue(
    households: list[Household],
    config: HVCTSConfig,
) -> AggregateHVCTSRevenue:
    """Compute population-level HVCTS revenue across all households."""
    total_revenue = 0.0
    liable_weight = 0.0
    population_weight = 0.0
    liable_count_unweighted = 0
    properties_weighted = 0.0

    for hh in households:
        result = compute_hvcts(hh, config)
        weighted_surcharge = result.total_surcharge * hh.weight
        total_revenue += weighted_surcharge
        population_weight += hh.weight
        properties_weighted += result.properties_in_scope * hh.weight

        if result.is_liable:
            liable_weight += hh.weight
            liable_count_unweighted += 1

    mean_surcharge = total_revenue / liable_weight if liable_weight > 0 else 0.0

    return AggregateHVCTSRevenue(
        total_revenue_bn=total_revenue / 1e9,
        liable_household_count=liable_weight,
        population_count=population_weight,
        liable_sample_count=liable_count_unweighted,
        properties_in_scope=properties_weighted,
        mean_surcharge=mean_surcharge,
    )
