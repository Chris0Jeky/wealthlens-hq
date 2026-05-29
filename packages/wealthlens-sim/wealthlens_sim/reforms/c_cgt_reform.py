"""Family C: Capital gains tax — current-law baseline and reform scenarios.

Blueprint v5 §9 Family C and §3.2: rate alignment with income tax, annual
exempt amount, death uplift removal, main-residence relief, business asset
reliefs, carried interest, exit charge, accrual taxation.

Current-law baseline (2026-27):
- Individual rates: 18% (basic rate) / 24% (higher rate)
- Trustees and PRs: 24% flat
- BADR/IR: 18%
- Annual exempt amount: £3,000
- Death uplift: gains wiped on death (no CGT charge)
- Main-residence relief: PPR gains fully exempt

Source: GOV.UK, Capital Gains Tax rates and allowances,
        https://www.gov.uk/guidance/capital-gains-tax-rates-and-allowances,
        accessed 2026-05-23.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.schema.household import Household

BASIC_RATE_BAND_2026: float = 37_700
PERSONAL_ALLOWANCE_2026: float = 12_570


class TaxpayerType(StrEnum):
    INDIVIDUAL = "individual"
    TRUSTEE = "trustee"


class CGTConfig(BaseModel):
    """Configuration for capital gains tax computation.

    Defaults to 2026-27 current-law parameters.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    annual_exempt_amount: float = Field(
        default=3_000, ge=0, description="Annual exempt amount (GBP)"
    )
    basic_rate: float = Field(
        default=0.18, ge=0, le=1, description="CGT rate for basic-rate taxpayers"
    )
    higher_rate: float = Field(
        default=0.24, ge=0, le=1, description="CGT rate for higher-rate taxpayers"
    )
    trustee_rate: float = Field(
        default=0.24, ge=0, le=1, description="CGT rate for trustees/PRs"
    )
    badr_rate: float = Field(
        default=0.18, ge=0, le=1,
        description="Rate for BADR/IR gains (stored for future use; not yet applied in computation)",
    )
    death_uplift: bool = Field(
        default=True,
        description="Whether gains are wiped on death (stored for future reform scenarios; "
        "baseline assumes True, not yet applied in computation)",
    )
    main_residence_exempt: bool = Field(
        default=True,
        description="Whether main-residence gains are fully exempt (stored for future reform "
        "scenarios; baseline assumes True, not yet applied in computation)",
    )
    basic_rate_band: float = Field(
        default=BASIC_RATE_BAND_2026, ge=0,
        description="Basic rate band width (GBP, for income tax band placement)",
    )
    personal_allowance: float = Field(
        default=PERSONAL_ALLOWANCE_2026, ge=0,
        description="Personal allowance (GBP)",
    )
    taxpayer_type: TaxpayerType = Field(
        default=TaxpayerType.INDIVIDUAL,
        description="Tax entity type (individual or trustee)",
    )

    @model_validator(mode="after")
    def _rates_consistent(self) -> CGTConfig:
        if self.basic_rate > self.higher_rate:
            msg = "basic_rate must not exceed higher_rate"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _unimplemented_flags(self) -> CGTConfig:
        if not self.death_uplift:
            msg = "death_uplift=False is not yet implemented in the computation"
            raise ValueError(msg)
        if not self.main_residence_exempt:
            msg = "main_residence_exempt=False is not yet implemented in the computation"
            raise ValueError(msg)
        if "badr_rate" in self.model_fields_set:
            msg = "badr_rate is stored but not yet applied; BADR gains are not split in the data model"
            raise ValueError(msg)
        return self


class CGTResult(BaseModel):
    """Per-person CGT computation result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    person_id: str
    gains_realised: float = Field(ge=0, description="Total realised gains (GBP)")
    gains_taxable: float = Field(ge=0, description="Gains after AEA deduction (GBP)")
    cgt_liability: float = Field(ge=0, description="CGT due (GBP)")
    effective_rate: float = Field(
        ge=0,
        description="CGT / gains_realised, inclusive of AEA benefit "
        "(for rate on taxable gains, use cgt_liability / gains_taxable)",
    )
    is_liable: bool


class HouseholdCGTResult(BaseModel):
    """Household-level CGT summary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    household_id: str
    person_results: tuple[CGTResult, ...]
    total_cgt_liability: float = Field(ge=0, description="Total CGT due across all persons (GBP)")
    is_liable: bool


class AggregateCGTRevenue(BaseModel):
    """Population-level CGT revenue estimate."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total_revenue_bn: float = Field(ge=0, description="Total CGT revenue (GBP billions)")
    taxpayer_count: float = Field(ge=0, description="Weighted count of liable households")
    population_count: float = Field(ge=0, description="Weighted count of all households in the dataset")
    liable_sample_count: int = Field(ge=0, description="Unweighted count of liable survey households")
    mean_liability: float = Field(ge=0, description="Population-weighted mean CGT among liable households (GBP)")
    revenue_by_nation: dict[str, float] = Field(
        default_factory=dict,
        description="Revenue in GBP billions, keyed by Nation value",
    )


def _compute_person_cgt(
    gains_realised: float,
    annual_income: float,
    config: CGTConfig,
) -> tuple[float, float]:
    """Compute CGT liability for a single person.

    Returns (taxable_gains, cgt_liability).
    """
    if gains_realised <= 0:
        return 0.0, 0.0

    taxable = max(0.0, gains_realised - config.annual_exempt_amount)
    if taxable == 0:
        return 0.0, 0.0

    if config.taxpayer_type == TaxpayerType.TRUSTEE:
        return taxable, taxable * config.trustee_rate

    # PA taper (£1 lost per £2 above £100k) is not modelled; has no practical
    # effect on CGT band placement because remaining_basic is already zero
    # for income above the basic rate band ceiling (~£50,270).
    taxable_income = max(0.0, annual_income - config.personal_allowance)
    remaining_basic = max(0.0, config.basic_rate_band - taxable_income)

    if remaining_basic >= taxable:
        liability = taxable * config.basic_rate
    else:
        liability = (
            remaining_basic * config.basic_rate
            + (taxable - remaining_basic) * config.higher_rate
        )

    return taxable, liability


def compute_household_cgt(
    household: Household,
    config: CGTConfig,
) -> HouseholdCGTResult:
    """Compute CGT for all persons in a household."""
    person_results: list[CGTResult] = []

    for person in household.persons:
        taxable, liability = _compute_person_cgt(
            person.capital_gains_realised,
            person.annual_income,
            config,
        )
        effective = liability / person.capital_gains_realised if person.capital_gains_realised > 0 else 0.0
        person_results.append(CGTResult(
            person_id=person.person_id,
            gains_realised=person.capital_gains_realised,
            gains_taxable=taxable,
            cgt_liability=liability,
            effective_rate=effective,
            is_liable=liability > 0,
        ))

    total = sum(r.cgt_liability for r in person_results)
    return HouseholdCGTResult(
        household_id=household.household_id,
        person_results=tuple(person_results),
        total_cgt_liability=total,
        is_liable=total > 0,
    )


def compute_aggregate_cgt_revenue(
    households: list[Household],
    config: CGTConfig,
) -> AggregateCGTRevenue:
    """Compute population-level CGT revenue across all households."""
    total_revenue = 0.0
    taxpayer_weight = 0.0
    population_weight = 0.0
    liable_count_unweighted = 0
    revenue_by_nation: dict[str, float] = {}

    for hh in households:
        result = compute_household_cgt(hh, config)
        weighted_liability = result.total_cgt_liability * hh.weight
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

    return AggregateCGTRevenue(
        total_revenue_bn=total_revenue / 1e9,
        taxpayer_count=taxpayer_weight,
        population_count=population_weight,
        liable_sample_count=liable_count_unweighted,
        mean_liability=mean_liability,
        revenue_by_nation=nation_bn,
    )
