"""Family D: Inheritance tax — current-law baseline (simplified estate model).

Blueprint v5 §9 Family D and §3.3: nil-rate bands, RNRB taper, APR/BPR
allowance, spousal exemption, charitable-giving reduced rate, pensions
inclusion flag.

This is a v0.1 simplified estate-level model. It computes IHT on a
person's total net wealth as if it were a taxable estate at death.

Simplifying assumptions (explicit per Blueprint v5 §3.3):
- No lifetime-gift modelling (7-year rule, PETs, CLTs out of scope)
- No trust taxation
- No transferable NRB from a predeceased spouse
- RNRB eligibility is inferred from main-residence ownership and a
  has_direct_descendants flag, not from detailed estate planning. The
  band is capped at the net value of the residence assets (UK RNRB
  cannot exceed the value of the residence passed to descendants).
- APR/BPR qualifying value is taken from PRIVATE_BUSINESS asset type
  only (agricultural land not separately modelled in v0.1)
- Pension inclusion flag defaults to False (pre-April 2027 baseline)
- Charitable gifts (charitable_fraction x estate) are exempt and
  deducted from the chargeable estate before NRB/RNRB; the 36% reduced
  rate additionally applies when the gift meets the 10% threshold.
- Estate value equals Person.total_net_wealth (no deductions beyond
  charitable gifts, NRB/RNRB, and reliefs modelled here)

Current-law parameters (2026-27):
- Nil-rate band (NRB): £325,000 (frozen since 2009-10)
- Residence nil-rate band (RNRB): £175,000
- RNRB taper: £1 reduction for every £2 above £2,000,000
- Main rate: 40%
- Reduced rate: 36% (if ≥10% of baseline estate left to charity)
- Spousal exemption: transfers to spouse/civil partner fully exempt
- APR/BPR: £2.5m combined allowance at 100% relief, 50% above
  (from 6 April 2026)

Sources:
    GOV.UK, Inheritance Tax thresholds and interest rates,
    https://www.gov.uk/guidance/inheritance-tax-thresholds,
    accessed 2026-05-23.

    GOV.UK, Changes to agricultural property relief and business
    property relief,
    https://www.gov.uk/government/publications/changes-to-agricultural-property-relief-and-business-property-relief,
    accessed 2026-05-23.
"""

from __future__ import annotations

from typing import TypedDict

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.schema.household import AssetType, Household

NRB_2026: float = 325_000
RNRB_2026: float = 175_000
RNRB_TAPER_THRESHOLD: float = 2_000_000
APR_BPR_ALLOWANCE_2026: float = 2_500_000
APR_BPR_RELIEF_ABOVE: float = 0.50
IHT_MAIN_RATE: float = 0.40
IHT_CHARITABLE_RATE: float = 0.36
CHARITABLE_THRESHOLD: float = 0.10

RESIDENCE_TYPES: frozenset[AssetType] = frozenset({
    AssetType.MAIN_RESIDENCE,
})

APR_BPR_TYPES: frozenset[AssetType] = frozenset({
    AssetType.PRIVATE_BUSINESS,
})

ALWAYS_EXCLUDED_TYPES: frozenset[AssetType] = frozenset({
    AssetType.STATE_PENSION,
})

PENSION_TYPES: frozenset[AssetType] = frozenset({
    AssetType.DB_PENSION,
    AssetType.DC_PENSION,
})


class PersonIHTFlags(TypedDict, total=False):
    """Per-person metadata for IHT computation.

    Charitable fraction is the fraction of the *baseline* estate (before
    NRB/RNRB/reliefs) left to charity. The caller must compute this
    externally — the IHT module has no gift/bequest model in v0.1.
    """

    is_married: bool
    has_direct_descendants: bool
    charitable_fraction: float


class IHTConfig(BaseModel):
    """Configuration for inheritance tax computation.

    Defaults to 2026-27 current-law parameters.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    nil_rate_band: float = Field(
        default=NRB_2026, ge=0,
        description="Nil-rate band (GBP)",
    )
    residence_nil_rate_band: float = Field(
        default=RNRB_2026, ge=0,
        description="Residence nil-rate band (GBP)",
    )
    rnrb_taper_threshold: float = Field(
        default=RNRB_TAPER_THRESHOLD, ge=0,
        description="Estate value above which RNRB tapers (GBP)",
    )
    main_rate: float = Field(
        default=IHT_MAIN_RATE, gt=0, le=1,
        description="Standard IHT rate",
    )
    charitable_rate: float = Field(
        default=IHT_CHARITABLE_RATE, gt=0, le=1,
        description="Reduced IHT rate for charitable estates",
    )
    charitable_threshold: float = Field(
        default=CHARITABLE_THRESHOLD, gt=0, le=1,
        description="Fraction of baseline estate that must go to charity for reduced rate",
    )
    apr_bpr_allowance: float = Field(
        default=APR_BPR_ALLOWANCE_2026, ge=0,
        description="Combined APR/BPR 100% relief allowance (GBP)",
    )
    apr_bpr_relief_above: float = Field(
        default=APR_BPR_RELIEF_ABOVE, ge=0, le=1,
        description="Relief rate on APR/BPR value above the allowance",
    )
    include_pensions: bool = Field(
        default=False,
        description="Whether pension assets are included in the estate (pre-April 2027: False)",
    )
    spousal_exempt: bool = Field(
        default=True,
        description="Whether spousal/civil-partner transfers are fully exempt",
    )

    @model_validator(mode="after")
    def _rates_consistent(self) -> IHTConfig:
        if self.charitable_rate > self.main_rate:
            msg = "charitable_rate must not exceed main_rate"
            raise ValueError(msg)
        return self


class IHTResult(BaseModel):
    """Per-person (estate) IHT computation result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    person_id: str
    estate_value: float = Field(ge=0, description="Total estate value (GBP)")
    nil_rate_band_used: float = Field(ge=0, description="NRB applied (GBP)")
    rnrb_used: float = Field(ge=0, description="RNRB applied (GBP)")
    apr_bpr_relief: float = Field(ge=0, description="APR/BPR relief applied (GBP)")
    taxable_estate: float = Field(ge=0, description="Estate value after all deductions (GBP)")
    iht_rate_applied: float = Field(ge=0, le=1, description="Effective IHT rate applied")
    iht_liability: float = Field(ge=0, description="IHT due (GBP)")
    effective_rate: float = Field(ge=0, description="IHT / estate_value (0 if no estate)")
    is_liable: bool
    is_spousal_exempt: bool = Field(description="Whether spousal exemption was applied")


class HouseholdIHTResult(BaseModel):
    """Household-level IHT summary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    household_id: str
    person_results: tuple[IHTResult, ...]
    total_iht_liability: float = Field(ge=0, description="Total IHT due across all persons (GBP)")
    is_liable: bool


class AggregateIHTRevenue(BaseModel):
    """Population-level IHT revenue estimate."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total_revenue_bn: float = Field(description="Total IHT revenue (GBP billions)")
    taxpayer_count: float = Field(ge=0, description="Weighted count of liable households")
    population_count: float = Field(ge=0, description="Weighted count of all households in the dataset")
    liable_sample_count: int = Field(ge=0, description="Unweighted count of liable survey households")
    mean_liability: float = Field(ge=0, description="Population-weighted mean IHT among liable households (GBP)")
    revenue_by_nation: dict[str, float] = Field(
        default_factory=dict,
        description="Revenue in GBP billions, keyed by Nation value",
    )


def _compute_rnrb(
    estate_value: float,
    owns_residence: bool,
    has_direct_descendants: bool,
    config: IHTConfig,
    *,
    residence_value: float | None = None,
) -> float:
    """Compute the available Residence Nil-Rate Band.

    When ``residence_value`` is supplied, the band is capped at that value:
    UK RNRB cannot exceed the net value of the residence passed to descendants.
    When it is ``None`` (e.g. direct unit-test calls), no cap is applied.
    """
    if not owns_residence or not has_direct_descendants:
        return 0.0

    rnrb = config.residence_nil_rate_band
    if estate_value > config.rnrb_taper_threshold:
        taper = (estate_value - config.rnrb_taper_threshold) / 2.0
        rnrb = max(0.0, rnrb - taper)
    if residence_value is not None:
        rnrb = min(rnrb, max(0.0, residence_value))
    return rnrb


def _compute_apr_bpr_relief(
    qualifying_value: float,
    config: IHTConfig,
) -> float:
    """Compute APR/BPR relief for qualifying assets."""
    if qualifying_value <= 0:
        return 0.0

    if qualifying_value <= config.apr_bpr_allowance:
        return qualifying_value

    relief_at_100 = config.apr_bpr_allowance
    excess = qualifying_value - config.apr_bpr_allowance
    relief_above = excess * config.apr_bpr_relief_above
    return relief_at_100 + relief_above


def _compute_person_iht(
    estate_value: float,
    owns_residence: bool,
    has_direct_descendants: bool,
    apr_bpr_qualifying: float,
    is_married: bool,
    charitable_fraction: float,
    config: IHTConfig,
    *,
    person_id: str = "",
    residence_value: float | None = None,
) -> IHTResult:
    """Compute IHT liability for a single person's estate."""

    if estate_value <= 0:
        return IHTResult(
            person_id=person_id,
            estate_value=0.0,
            nil_rate_band_used=0.0,
            rnrb_used=0.0,
            apr_bpr_relief=0.0,
            taxable_estate=0.0,
            iht_rate_applied=0.0,
            iht_liability=0.0,
            effective_rate=0.0,
            is_liable=False,
            is_spousal_exempt=False,
        )

    if config.spousal_exempt and is_married:
        return IHTResult(
            person_id=person_id,
            estate_value=estate_value,
            nil_rate_band_used=0.0,
            rnrb_used=0.0,
            apr_bpr_relief=0.0,
            taxable_estate=0.0,
            iht_rate_applied=0.0,
            iht_liability=0.0,
            effective_rate=0.0,
            is_liable=False,
            is_spousal_exempt=True,
        )

    apr_bpr_relief = _compute_apr_bpr_relief(apr_bpr_qualifying, config)
    # Charitable gifts are IHT-exempt: the donated amount leaves the chargeable
    # estate before nil-rate bands are applied (separate from the 36% reduced
    # rate, which additionally requires the 10% threshold below).
    charitable_donation = max(0.0, charitable_fraction) * estate_value
    estate_after_relief = max(0.0, estate_value - apr_bpr_relief - charitable_donation)

    rnrb = _compute_rnrb(
        estate_value,
        owns_residence,
        has_direct_descendants,
        config,
        residence_value=residence_value,
    )
    total_nil_rate = config.nil_rate_band + rnrb

    taxable = max(0.0, estate_after_relief - total_nil_rate)

    if taxable == 0:
        return IHTResult(
            person_id=person_id,
            estate_value=estate_value,
            nil_rate_band_used=min(config.nil_rate_band, estate_after_relief),
            rnrb_used=min(rnrb, max(0.0, estate_after_relief - config.nil_rate_band)),
            apr_bpr_relief=apr_bpr_relief,
            taxable_estate=0.0,
            iht_rate_applied=0.0,
            iht_liability=0.0,
            effective_rate=0.0,
            is_liable=False,
            is_spousal_exempt=False,
        )

    rate = config.main_rate
    if charitable_fraction >= config.charitable_threshold:
        rate = config.charitable_rate

    liability = taxable * rate

    return IHTResult(
        person_id=person_id,
        estate_value=estate_value,
        nil_rate_band_used=config.nil_rate_band,
        rnrb_used=rnrb,
        apr_bpr_relief=apr_bpr_relief,
        taxable_estate=taxable,
        iht_rate_applied=rate,
        iht_liability=liability,
        effective_rate=liability / estate_value,
        is_liable=True,
        is_spousal_exempt=False,
    )


def compute_household_iht(
    household: Household,
    config: IHTConfig,
    person_flags: dict[str, PersonIHTFlags] | None = None,
) -> HouseholdIHTResult:
    """Compute IHT for all persons in a household.

    person_flags optionally provides per-person metadata keyed by person_id.
    If absent, defaults are: not married, no descendants, no charitable giving.
    """
    if person_flags is None:
        person_flags = {}

    person_results: list[IHTResult] = []

    for person in household.persons:
        flags = person_flags.get(person.person_id, {})
        is_married = flags.get("is_married", False)
        has_direct_descendants = flags.get("has_direct_descendants", False)
        charitable_fraction = flags.get("charitable_fraction", 0.0)

        estate_value = 0.0
        owns_residence = False
        residence_value = 0.0
        apr_bpr_qualifying = 0.0

        for asset in person.assets:
            if asset.asset_type in ALWAYS_EXCLUDED_TYPES:
                continue
            if asset.asset_type in PENSION_TYPES and not config.include_pensions:
                continue
            estate_value += asset.net_value
            if asset.asset_type in RESIDENCE_TYPES:
                owns_residence = True
                residence_value += asset.net_value
            if asset.asset_type in APR_BPR_TYPES:
                apr_bpr_qualifying += asset.gross_value

        estate_value = max(0.0, estate_value)

        person_results.append(_compute_person_iht(
            estate_value=estate_value,
            owns_residence=owns_residence,
            has_direct_descendants=has_direct_descendants,
            apr_bpr_qualifying=max(0.0, apr_bpr_qualifying),
            is_married=is_married,
            charitable_fraction=charitable_fraction,
            config=config,
            person_id=person.person_id,
            residence_value=max(0.0, residence_value),
        ))

    total = sum(r.iht_liability for r in person_results)
    return HouseholdIHTResult(
        household_id=household.household_id,
        person_results=tuple(person_results),
        total_iht_liability=total,
        is_liable=total > 0,
    )


def compute_aggregate_iht_revenue(
    households: list[Household],
    config: IHTConfig,
    population_flags: dict[str, dict[str, PersonIHTFlags]] | None = None,
) -> AggregateIHTRevenue:
    """Compute population-level IHT revenue across all households.

    population_flags: {household_id: {person_id: PersonIHTFlags}}
    """
    if population_flags is None:
        population_flags = {}

    total_revenue = 0.0
    taxpayer_weight = 0.0
    population_weight = 0.0
    liable_count_unweighted = 0
    revenue_by_nation: dict[str, float] = {}

    for hh in households:
        person_flags = population_flags.get(hh.household_id)
        result = compute_household_iht(hh, config, person_flags)
        weighted_liability = result.total_iht_liability * hh.weight
        total_revenue += weighted_liability
        population_weight += hh.weight

        nation_key = hh.nation.value
        revenue_by_nation[nation_key] = (
            revenue_by_nation.get(nation_key, 0.0) + weighted_liability
        )

        if result.is_liable:
            taxpayer_weight += hh.weight
            liable_count_unweighted += 1

    mean_liability = total_revenue / taxpayer_weight if taxpayer_weight > 0 else 0.0
    nation_bn = {k: v / 1e9 for k, v in revenue_by_nation.items()}

    return AggregateIHTRevenue(
        total_revenue_bn=total_revenue / 1e9,
        taxpayer_count=taxpayer_weight,
        population_count=population_weight,
        liable_sample_count=liable_count_unweighted,
        mean_liability=mean_liability,
        revenue_by_nation=nation_bn,
    )
