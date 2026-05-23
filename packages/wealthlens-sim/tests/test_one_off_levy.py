"""Tests for Family B one-off wealth levy calculator."""

from __future__ import annotations

import pytest
from _helpers import make_household, make_person
from pydantic import ValidationError

from wealthlens_sim.reforms._banding import RateBand
from wealthlens_sim.reforms.a_annual_wealth import TaxUnit
from wealthlens_sim.reforms.b_one_off_levy import (
    LevyRateBand,
    OneOffLevyConfig,
    OneOffLevyResult,
    _compute_liability,
    compute_aggregate_one_off_revenue,
    compute_one_off_levy,
)
from wealthlens_sim.schema.base import Nation
from wealthlens_sim.schema.household import AssetType, Household


class TestOneOffLevyConfig:
    def test_basic_config(self):
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        assert config.threshold == 10_000_000
        assert config.rate == 0.05
        assert config.tax_unit == TaxUnit.INDIVIDUAL
        assert config.exempt_asset_types == frozenset()
        assert config.instalment_years == 1

    def test_frozen(self):
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        with pytest.raises(ValidationError, match="frozen"):
            config.threshold = 5_000_000

    def test_rate_bounds(self):
        with pytest.raises(ValidationError):
            OneOffLevyConfig(threshold=0, rate=0)
        with pytest.raises(ValidationError):
            OneOffLevyConfig(threshold=0, rate=1.5)

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            OneOffLevyConfig(threshold=0, rate=0.05, surprise="bad")

    def test_exempt_asset_types(self):
        config = OneOffLevyConfig(
            threshold=0,
            rate=0.05,
            exempt_asset_types=frozenset({AssetType.MAIN_RESIDENCE, AssetType.DB_PENSION}),
        )
        assert AssetType.MAIN_RESIDENCE in config.exempt_asset_types

    def test_instalment_years_default(self):
        config = OneOffLevyConfig(threshold=0, rate=0.05)
        assert config.instalment_years == 1

    def test_instalment_years_custom(self):
        config = OneOffLevyConfig(threshold=0, rate=0.05, instalment_years=5)
        assert config.instalment_years == 5

    def test_instalment_years_must_be_positive(self):
        with pytest.raises(ValidationError):
            OneOffLevyConfig(threshold=0, rate=0.05, instalment_years=0)

    def test_instalment_years_frozen(self):
        config = OneOffLevyConfig(threshold=0, rate=0.05, instalment_years=3)
        with pytest.raises(ValidationError, match="frozen"):
            config.instalment_years = 5


class TestConfigValidation:
    def test_empty_rate_bands_rejected(self):
        with pytest.raises(ValidationError):
            OneOffLevyConfig(rate_bands=())

    def test_duplicate_thresholds_rejected(self):
        with pytest.raises(ValidationError, match="unique thresholds"):
            OneOffLevyConfig(
                rate_bands=(
                    RateBand(threshold=5_000_000, rate=0.03),
                    RateBand(threshold=5_000_000, rate=0.05),
                ),
            )

    def test_conflicting_flat_and_progressive_rejected(self):
        with pytest.raises(ValidationError, match="rate_bands is set"):
            OneOffLevyConfig(
                threshold=10_000_000,
                rate=0.10,
                rate_bands=(RateBand(threshold=5_000_000, rate=0.05),),
            )

    def test_rate_bands_with_defaults_accepted(self):
        config = OneOffLevyConfig(
            rate_bands=(RateBand(threshold=5_000_000, rate=0.05),),
        )
        assert config.rate_bands is not None

    def test_negative_wealth_returns_zero(self):
        config = OneOffLevyConfig(threshold=0, rate=0.05)
        assert _compute_liability(-1_000_000, config) == 0.0

    def test_negative_wealth_progressive_returns_zero(self):
        config = OneOffLevyConfig(
            rate_bands=(RateBand(threshold=0, rate=0.05),),
        )
        assert _compute_liability(-500_000, config) == 0.0


class TestComputeOneOffLevy:
    def test_below_threshold_no_liability(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 1_000_000, 0),
        ])
        hh = make_household([person])
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        result = compute_one_off_levy(hh, config)
        assert result.levy_liability == 0.0
        assert result.annual_instalment == 0.0
        assert not result.is_liable

    def test_above_threshold_individual(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 15_000_000, 0),
        ])
        hh = make_household([person])
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        result = compute_one_off_levy(hh, config)
        assert result.levy_liability == pytest.approx(250_000)
        assert result.annual_instalment == pytest.approx(250_000)
        assert result.is_liable
        assert result.taxable_wealth == 15_000_000

    def test_household_unit_two_persons(self):
        p1 = make_person("p1", [(AssetType.FINANCIAL, 8_000_000, 0)])
        p2 = make_person("p2", [(AssetType.FINANCIAL, 7_000_000, 0)])
        hh = make_household([p1, p2])
        config = OneOffLevyConfig(
            threshold=10_000_000, rate=0.05, tax_unit=TaxUnit.HOUSEHOLD
        )
        result = compute_one_off_levy(hh, config)
        assert result.taxable_wealth == 15_000_000
        assert result.levy_liability == pytest.approx(250_000)

    def test_individual_unit_two_persons_below_each(self):
        p1 = make_person("p1", [(AssetType.FINANCIAL, 8_000_000, 0)])
        p2 = make_person("p2", [(AssetType.FINANCIAL, 7_000_000, 0)])
        hh = make_household([p1, p2])
        config = OneOffLevyConfig(
            threshold=10_000_000, rate=0.05, tax_unit=TaxUnit.INDIVIDUAL
        )
        result = compute_one_off_levy(hh, config)
        assert result.levy_liability == 0.0

    def test_exemptions_reduce_base(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 12_000_000, 0),
            (AssetType.MAIN_RESIDENCE, 5_000_000, 0),
        ])
        hh = make_household([person])
        config_comprehensive = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        config_exempt_home = OneOffLevyConfig(
            threshold=10_000_000,
            rate=0.05,
            exempt_asset_types=frozenset({AssetType.MAIN_RESIDENCE}),
        )
        result_comp = compute_one_off_levy(hh, config_comprehensive)
        result_exempt = compute_one_off_levy(hh, config_exempt_home)
        assert result_comp.levy_liability > result_exempt.levy_liability
        assert result_exempt.levy_liability == pytest.approx(100_000)

    def test_effective_rate(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 20_000_000, 0),
        ])
        hh = make_household([person])
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        result = compute_one_off_levy(hh, config)
        assert result.effective_rate == pytest.approx(500_000 / 20_000_000)

    def test_effective_rate_zero_wealth(self):
        person = make_person(assets=[])
        hh = make_household([person])
        config = OneOffLevyConfig(threshold=0, rate=0.05)
        result = compute_one_off_levy(hh, config)
        assert result.effective_rate == 0.0

    def test_instalment_splits_liability(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 20_000_000, 0),
        ])
        hh = make_household([person])
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05, instalment_years=5)
        result = compute_one_off_levy(hh, config)
        assert result.levy_liability == pytest.approx(500_000)
        assert result.annual_instalment == pytest.approx(100_000)

    def test_instalment_one_year_matches_total(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 20_000_000, 0),
        ])
        hh = make_household([person])
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05, instalment_years=1)
        result = compute_one_off_levy(hh, config)
        assert result.levy_liability == result.annual_instalment


class TestAggregateOneOffRevenue:
    def _make_population(self) -> list[Household]:
        wealthy = make_household(
            [make_person("p1", [(AssetType.FINANCIAL, 50_000_000, 0)])],
            nation=Nation.ENGLAND,
            weight=1000,
            household_id="hh_wealthy",
        )
        middle = make_household(
            [make_person("p2", [(AssetType.FINANCIAL, 500_000, 0)])],
            nation=Nation.SCOTLAND,
            weight=10_000,
            household_id="hh_middle",
        )
        poor = make_household(
            [make_person("p3", [(AssetType.FINANCIAL, 10_000, 0)])],
            nation=Nation.WALES,
            weight=5_000,
            household_id="hh_poor",
        )
        return [wealthy, middle, poor]

    def test_basic_revenue(self):
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        result = compute_aggregate_one_off_revenue(self._make_population(), config)
        expected_per_hh = (50_000_000 - 10_000_000) * 0.05
        expected_total = expected_per_hh * 1000
        assert result.total_revenue_bn == pytest.approx(expected_total / 1e9)
        assert result.taxpayer_count == 1000
        assert result.population_count == 16_000

    def test_revenue_by_nation(self):
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        result = compute_aggregate_one_off_revenue(self._make_population(), config)
        assert "england" in result.revenue_by_nation
        assert result.revenue_by_nation["england"] > 0
        assert result.revenue_by_nation.get("scotland", 0) == 0
        assert result.revenue_by_nation.get("wales", 0) == 0

    def test_no_liable_households(self):
        config = OneOffLevyConfig(threshold=100_000_000, rate=0.05)
        result = compute_aggregate_one_off_revenue(self._make_population(), config)
        assert result.total_revenue_bn == 0.0
        assert result.taxpayer_count == 0
        assert result.mean_liability == 0.0

    def test_empty_population(self):
        config = OneOffLevyConfig(threshold=0, rate=0.05)
        result = compute_aggregate_one_off_revenue([], config)
        assert result.total_revenue_bn == 0.0
        assert result.population_count == 0
        assert result.annual_instalment_revenue_bn == 0.0

    def test_multiple_thresholds_sensitivity(self):
        pop = self._make_population()
        low = compute_aggregate_one_off_revenue(
            pop, OneOffLevyConfig(threshold=1_000_000, rate=0.05)
        )
        high = compute_aggregate_one_off_revenue(
            pop, OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        )
        assert low.total_revenue_bn > high.total_revenue_bn
        assert low.taxpayer_count >= high.taxpayer_count

    def test_result_frozen(self):
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        result = compute_aggregate_one_off_revenue(self._make_population(), config)
        with pytest.raises(ValidationError, match="frozen"):
            result.total_revenue_bn = 999.0

    def test_instalment_revenue(self):
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05, instalment_years=5)
        result = compute_aggregate_one_off_revenue(self._make_population(), config)
        assert result.annual_instalment_revenue_bn == pytest.approx(
            result.total_revenue_bn / 5
        )

    def test_instalment_one_year_revenue_matches_total(self):
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05, instalment_years=1)
        result = compute_aggregate_one_off_revenue(self._make_population(), config)
        assert result.annual_instalment_revenue_bn == pytest.approx(
            result.total_revenue_bn
        )


class TestProgressiveRateBands:
    def test_single_band_matches_flat(self):
        config = OneOffLevyConfig(
            rate_bands=(RateBand(threshold=10_000_000, rate=0.05),),
        )
        liability = _compute_liability(15_000_000, config)
        assert liability == pytest.approx(250_000)

    def test_two_bands(self):
        config = OneOffLevyConfig(
            rate_bands=(
                RateBand(threshold=5_000_000, rate=0.03),
                RateBand(threshold=10_000_000, rate=0.05),
            ),
        )
        liability = _compute_liability(15_000_000, config)
        expected = (10_000_000 - 5_000_000) * 0.03 + (15_000_000 - 10_000_000) * 0.05
        assert liability == pytest.approx(expected)

    def test_three_bands(self):
        config = OneOffLevyConfig(
            rate_bands=(
                RateBand(threshold=1_000_000, rate=0.01),
                RateBand(threshold=5_000_000, rate=0.03),
                RateBand(threshold=20_000_000, rate=0.05),
            ),
        )
        liability = _compute_liability(30_000_000, config)
        expected = (
            (5_000_000 - 1_000_000) * 0.01
            + (20_000_000 - 5_000_000) * 0.03
            + (30_000_000 - 20_000_000) * 0.05
        )
        assert liability == pytest.approx(expected)

    def test_below_first_band(self):
        config = OneOffLevyConfig(
            rate_bands=(
                RateBand(threshold=10_000_000, rate=0.05),
                RateBand(threshold=20_000_000, rate=0.10),
            ),
        )
        liability = _compute_liability(5_000_000, config)
        assert liability == 0.0

    def test_exactly_at_threshold(self):
        config = OneOffLevyConfig(
            rate_bands=(RateBand(threshold=10_000_000, rate=0.05),),
        )
        liability = _compute_liability(10_000_000, config)
        assert liability == 0.0

    def test_progressive_via_compute_one_off_levy(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 15_000_000, 0),
        ])
        hh = make_household([person])
        config = OneOffLevyConfig(
            rate_bands=(
                RateBand(threshold=5_000_000, rate=0.03),
                RateBand(threshold=10_000_000, rate=0.05),
            ),
        )
        result = compute_one_off_levy(hh, config)
        expected = (10_000_000 - 5_000_000) * 0.03 + (15_000_000 - 10_000_000) * 0.05
        assert result.levy_liability == pytest.approx(expected)
        assert result.is_liable

    def test_progressive_with_instalments(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 15_000_000, 0),
        ])
        hh = make_household([person])
        config = OneOffLevyConfig(
            rate_bands=(
                RateBand(threshold=5_000_000, rate=0.03),
                RateBand(threshold=10_000_000, rate=0.05),
            ),
            instalment_years=5,
        )
        result = compute_one_off_levy(hh, config)
        expected = (10_000_000 - 5_000_000) * 0.03 + (15_000_000 - 10_000_000) * 0.05
        assert result.levy_liability == pytest.approx(expected)
        assert result.annual_instalment == pytest.approx(expected / 5)

    def test_rate_band_frozen(self):
        band = RateBand(threshold=10_000_000, rate=0.05)
        with pytest.raises(ValidationError, match="frozen"):
            band.rate = 0.10

    def test_rate_band_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            RateBand(threshold=0, rate=0.05, surprise="bad")


class TestNegativeWealth:
    def test_negative_net_value_no_liability(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 100_000, 500_000),
        ])
        hh = make_household([person])
        config = OneOffLevyConfig(threshold=0, rate=0.05)
        result = compute_one_off_levy(hh, config)
        assert result.levy_liability == 0.0
        assert result.taxable_wealth == 0.0

    def test_mixed_positive_negative_individual_unit(self):
        p1 = make_person("p1", [(AssetType.FINANCIAL, 15_000_000, 0)])
        p2 = make_person("p2", [(AssetType.FINANCIAL, 100_000, 500_000)])
        hh = make_household([p1, p2])
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        result = compute_one_off_levy(hh, config)
        assert result.levy_liability == pytest.approx(250_000)
        assert result.taxable_wealth == 15_000_000

    def test_all_exempt_assets_zero_liability(self):
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 2_000_000, 0),
            (AssetType.DB_PENSION, 1_000_000, 0),
        ])
        hh = make_household([person])
        config = OneOffLevyConfig(
            threshold=0,
            rate=0.05,
            exempt_asset_types=frozenset({AssetType.MAIN_RESIDENCE, AssetType.DB_PENSION}),
        )
        result = compute_one_off_levy(hh, config)
        assert result.levy_liability == 0.0
        assert result.taxable_wealth == 0.0
        assert not result.is_liable


class TestAggregateOneOffRevenueExtended:
    def test_liable_sample_count(self):
        wealthy = make_household(
            [make_person("p1", [(AssetType.FINANCIAL, 50_000_000, 0)])],
            weight=1000, household_id="hh1",
        )
        poor = make_household(
            [make_person("p2", [(AssetType.FINANCIAL, 10_000, 0)])],
            weight=5000, household_id="hh2",
        )
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        result = compute_aggregate_one_off_revenue([wealthy, poor], config)
        assert result.liable_sample_count == 1

    def test_liable_sample_count_zero(self):
        poor = make_household(
            [make_person("p1", [(AssetType.FINANCIAL, 10_000, 0)])],
            weight=5000, household_id="hh1",
        )
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        result = compute_aggregate_one_off_revenue([poor], config)
        assert result.liable_sample_count == 0

    def test_mean_liability_weighted(self):
        hh1 = make_household(
            [make_person("p1", [(AssetType.FINANCIAL, 20_000_000, 0)])],
            weight=100, household_id="hh1",
        )
        hh2 = make_household(
            [make_person("p2", [(AssetType.FINANCIAL, 30_000_000, 0)])],
            weight=200, household_id="hh2",
        )
        config = OneOffLevyConfig(threshold=10_000_000, rate=0.05)
        result = compute_aggregate_one_off_revenue([hh1, hh2], config)
        expected_rev = (10_000_000 * 0.05 * 100) + (20_000_000 * 0.05 * 200)
        expected_mean = expected_rev / (100 + 200)
        assert result.mean_liability == pytest.approx(expected_mean)


class TestOneOffLevyResult:
    def test_round_trip(self):
        result = OneOffLevyResult(
            household_id="hh1",
            taxable_wealth=15_000_000,
            levy_liability=250_000,
            annual_instalment=50_000,
            effective_rate=0.0125,
            is_liable=True,
        )
        data = result.model_dump()
        r2 = OneOffLevyResult.model_validate(data)
        assert r2.household_id == "hh1"
        assert r2.levy_liability == 250_000
        assert r2.annual_instalment == 50_000

    def test_result_frozen(self):
        result = OneOffLevyResult(
            household_id="hh1",
            taxable_wealth=15_000_000,
            levy_liability=250_000,
            annual_instalment=250_000,
            effective_rate=0.0125,
            is_liable=True,
        )
        with pytest.raises(ValidationError, match="frozen"):
            result.levy_liability = 0.0


class TestLevyRateBandAlias:
    def test_alias_is_rate_band(self):
        assert LevyRateBand is RateBand

    def test_alias_works_in_config(self):
        config = OneOffLevyConfig(
            rate_bands=(LevyRateBand(threshold=5_000_000, rate=0.05),),
        )
        assert config.rate_bands is not None


class TestUnsortedBands:
    def test_unsorted_bands_produce_correct_result(self):
        config = OneOffLevyConfig(
            rate_bands=(
                RateBand(threshold=10_000_000, rate=0.05),
                RateBand(threshold=5_000_000, rate=0.03),
            ),
        )
        liability = _compute_liability(15_000_000, config)
        expected = (10_000_000 - 5_000_000) * 0.03 + (15_000_000 - 10_000_000) * 0.05
        assert liability == pytest.approx(expected)


class TestZeroWealthProgressive:
    def test_zero_wealth_progressive_returns_zero(self):
        config = OneOffLevyConfig(
            rate_bands=(RateBand(threshold=0, rate=0.05),),
        )
        assert _compute_liability(0, config) == 0.0

    def test_zero_wealth_flat_returns_zero(self):
        config = OneOffLevyConfig(threshold=0, rate=0.05)
        assert _compute_liability(0, config) == 0.0


class TestHouseholdUnitNegativeWealth:
    def test_household_unit_negative_member_floored_before_sum(self):
        p1 = make_person("p1", [(AssetType.FINANCIAL, 15_000_000, 0)])
        p2 = make_person("p2", [(AssetType.FINANCIAL, 100_000, 20_000_000)])
        hh = make_household([p1, p2])
        config = OneOffLevyConfig(
            threshold=10_000_000, rate=0.05, tax_unit=TaxUnit.HOUSEHOLD
        )
        result = compute_one_off_levy(hh, config)
        assert result.taxable_wealth == 15_000_000
        assert result.levy_liability == pytest.approx(250_000)
        assert result.is_liable

    def test_household_unit_all_negative(self):
        p1 = make_person("p1", [(AssetType.FINANCIAL, 100_000, 500_000)])
        p2 = make_person("p2", [(AssetType.FINANCIAL, 50_000, 200_000)])
        hh = make_household([p1, p2])
        config = OneOffLevyConfig(
            threshold=0, rate=0.05, tax_unit=TaxUnit.HOUSEHOLD
        )
        result = compute_one_off_levy(hh, config)
        assert result.taxable_wealth == 0.0
        assert result.levy_liability == 0.0
