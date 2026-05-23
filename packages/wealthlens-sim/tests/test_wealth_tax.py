"""Tests for Family A annual wealth tax calculator."""

from __future__ import annotations

import pytest
from _helpers import make_household, make_person
from pydantic import ValidationError

from wealthlens_sim.reforms._banding import RateBand
from wealthlens_sim.reforms.a_annual_wealth import (
    TaxUnit,
    WealthTaxConfig,
    WealthTaxResult,
    _compute_liability,
    compute_aggregate_revenue,
    compute_wealth_tax,
    taxable_wealth_for_person,
)
from wealthlens_sim.schema.base import Nation
from wealthlens_sim.schema.household import AssetType, Household


class TestWealthTaxConfig:
    def test_basic_config(self):
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        assert config.threshold == 10_000_000
        assert config.rate == 0.01
        assert config.tax_unit == TaxUnit.INDIVIDUAL
        assert config.exempt_asset_types == frozenset()

    def test_frozen(self):
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        with pytest.raises(ValidationError, match="frozen"):
            config.threshold = 5_000_000

    def test_rate_bounds(self):
        with pytest.raises(ValidationError):
            WealthTaxConfig(threshold=0, rate=0)
        with pytest.raises(ValidationError):
            WealthTaxConfig(threshold=0, rate=1.5)

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            WealthTaxConfig(threshold=0, rate=0.01, surprise="bad")

    def test_exempt_asset_types(self):
        config = WealthTaxConfig(
            threshold=0,
            rate=0.01,
            exempt_asset_types=frozenset({AssetType.MAIN_RESIDENCE, AssetType.DB_PENSION}),
        )
        assert AssetType.MAIN_RESIDENCE in config.exempt_asset_types


class TestTaxableWealth:
    def test_no_exemptions(self):
        p = make_person(assets=[
            (AssetType.FINANCIAL, 5_000_000, 0),
            (AssetType.MAIN_RESIDENCE, 2_000_000, 500_000),
        ])
        result = taxable_wealth_for_person(p.assets, frozenset())
        assert result == 6_500_000

    def test_exempt_main_residence(self):
        p = make_person(assets=[
            (AssetType.FINANCIAL, 5_000_000, 0),
            (AssetType.MAIN_RESIDENCE, 2_000_000, 500_000),
        ])
        result = taxable_wealth_for_person(
            p.assets, frozenset({AssetType.MAIN_RESIDENCE})
        )
        assert result == 5_000_000

    def test_exempt_pensions(self):
        p = make_person(assets=[
            (AssetType.FINANCIAL, 3_000_000, 0),
            (AssetType.DB_PENSION, 1_000_000, 0),
            (AssetType.DC_PENSION, 500_000, 0),
        ])
        result = taxable_wealth_for_person(
            p.assets, frozenset({AssetType.DB_PENSION, AssetType.DC_PENSION})
        )
        assert result == 3_000_000

    def test_no_assets(self):
        p = make_person(assets=[])
        result = taxable_wealth_for_person(p.assets, frozenset())
        assert result == 0.0


class TestComputeWealthTax:
    def test_below_threshold_no_liability(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 1_000_000, 0),
        ])
        hh = make_household([person])
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        result = compute_wealth_tax(hh, config)
        assert result.tax_liability == 0.0
        assert not result.is_liable

    def test_above_threshold_individual(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 15_000_000, 0),
        ])
        hh = make_household([person])
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        result = compute_wealth_tax(hh, config)
        assert result.tax_liability == pytest.approx(50_000)
        assert result.is_liable
        assert result.taxable_wealth == 15_000_000

    def test_household_unit_two_persons(self):
        p1 = make_person("p1", [(AssetType.FINANCIAL, 8_000_000, 0)])
        p2 = make_person("p2", [(AssetType.FINANCIAL, 7_000_000, 0)])
        hh = make_household([p1, p2])
        config = WealthTaxConfig(
            threshold=10_000_000, rate=0.01, tax_unit=TaxUnit.HOUSEHOLD
        )
        result = compute_wealth_tax(hh, config)
        assert result.taxable_wealth == 15_000_000
        assert result.tax_liability == pytest.approx(50_000)

    def test_individual_unit_two_persons_below_each(self):
        p1 = make_person("p1", [(AssetType.FINANCIAL, 8_000_000, 0)])
        p2 = make_person("p2", [(AssetType.FINANCIAL, 7_000_000, 0)])
        hh = make_household([p1, p2])
        config = WealthTaxConfig(
            threshold=10_000_000, rate=0.01, tax_unit=TaxUnit.INDIVIDUAL
        )
        result = compute_wealth_tax(hh, config)
        assert result.tax_liability == 0.0

    def test_exemptions_reduce_base(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 12_000_000, 0),
            (AssetType.MAIN_RESIDENCE, 5_000_000, 0),
        ])
        hh = make_household([person])
        config_comprehensive = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        config_exempt_home = WealthTaxConfig(
            threshold=10_000_000,
            rate=0.01,
            exempt_asset_types=frozenset({AssetType.MAIN_RESIDENCE}),
        )
        result_comp = compute_wealth_tax(hh, config_comprehensive)
        result_exempt = compute_wealth_tax(hh, config_exempt_home)
        assert result_comp.tax_liability > result_exempt.tax_liability
        assert result_exempt.tax_liability == pytest.approx(20_000)

    def test_effective_rate(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 20_000_000, 0),
        ])
        hh = make_household([person])
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        result = compute_wealth_tax(hh, config)
        assert result.effective_rate == pytest.approx(100_000 / 20_000_000)

    def test_effective_rate_zero_wealth(self):
        person = make_person(assets=[])
        hh = make_household([person])
        config = WealthTaxConfig(threshold=0, rate=0.01)
        result = compute_wealth_tax(hh, config)
        assert result.effective_rate == 0.0


class TestAggregateRevenue:
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
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        result = compute_aggregate_revenue(self._make_population(), config)
        expected_per_hh = (50_000_000 - 10_000_000) * 0.01
        expected_total = expected_per_hh * 1000
        assert result.total_revenue_bn == pytest.approx(expected_total / 1e9)
        assert result.taxpayer_count == 1000
        assert result.population_count == 16_000

    def test_revenue_by_nation(self):
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        result = compute_aggregate_revenue(self._make_population(), config)
        assert "england" in result.revenue_by_nation
        assert result.revenue_by_nation["england"] > 0
        assert result.revenue_by_nation.get("scotland", 0) == 0
        assert result.revenue_by_nation.get("wales", 0) == 0

    def test_no_liable_households(self):
        config = WealthTaxConfig(threshold=100_000_000, rate=0.01)
        result = compute_aggregate_revenue(self._make_population(), config)
        assert result.total_revenue_bn == 0.0
        assert result.taxpayer_count == 0
        assert result.mean_liability == 0.0

    def test_empty_population(self):
        config = WealthTaxConfig(threshold=0, rate=0.01)
        result = compute_aggregate_revenue([], config)
        assert result.total_revenue_bn == 0.0
        assert result.population_count == 0

    def test_multiple_thresholds_sensitivity(self):
        pop = self._make_population()
        low = compute_aggregate_revenue(
            pop, WealthTaxConfig(threshold=1_000_000, rate=0.01)
        )
        high = compute_aggregate_revenue(
            pop, WealthTaxConfig(threshold=10_000_000, rate=0.01)
        )
        assert low.total_revenue_bn > high.total_revenue_bn
        assert low.taxpayer_count >= high.taxpayer_count

    def test_result_frozen(self):
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        result = compute_aggregate_revenue(self._make_population(), config)
        with pytest.raises(ValidationError, match="frozen"):
            result.total_revenue_bn = 999.0


class TestProgressiveRateBands:
    def test_single_band_matches_flat(self):
        config = WealthTaxConfig(
            rate_bands=(RateBand(threshold=10_000_000, rate=0.01),),
        )
        liability = _compute_liability(15_000_000, config)
        assert liability == pytest.approx(50_000)

    def test_two_bands(self):
        config = WealthTaxConfig(
            rate_bands=(
                RateBand(threshold=5_000_000, rate=0.005),
                RateBand(threshold=10_000_000, rate=0.01),
            ),
        )
        liability = _compute_liability(15_000_000, config)
        expected = (10_000_000 - 5_000_000) * 0.005 + (15_000_000 - 10_000_000) * 0.01
        assert liability == pytest.approx(expected)

    def test_three_bands(self):
        config = WealthTaxConfig(
            rate_bands=(
                RateBand(threshold=1_000_000, rate=0.005),
                RateBand(threshold=5_000_000, rate=0.01),
                RateBand(threshold=20_000_000, rate=0.02),
            ),
        )
        liability = _compute_liability(30_000_000, config)
        expected = (
            (5_000_000 - 1_000_000) * 0.005
            + (20_000_000 - 5_000_000) * 0.01
            + (30_000_000 - 20_000_000) * 0.02
        )
        assert liability == pytest.approx(expected)

    def test_below_first_band(self):
        config = WealthTaxConfig(
            rate_bands=(
                RateBand(threshold=10_000_000, rate=0.01),
                RateBand(threshold=20_000_000, rate=0.02),
            ),
        )
        liability = _compute_liability(5_000_000, config)
        assert liability == 0.0

    def test_exactly_at_threshold(self):
        config = WealthTaxConfig(
            rate_bands=(RateBand(threshold=10_000_000, rate=0.01),),
        )
        liability = _compute_liability(10_000_000, config)
        assert liability == 0.0

    def test_progressive_via_compute_wealth_tax(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 15_000_000, 0),
        ])
        hh = make_household([person])
        config = WealthTaxConfig(
            rate_bands=(
                RateBand(threshold=5_000_000, rate=0.005),
                RateBand(threshold=10_000_000, rate=0.01),
            ),
        )
        result = compute_wealth_tax(hh, config)
        expected = (10_000_000 - 5_000_000) * 0.005 + (15_000_000 - 10_000_000) * 0.01
        assert result.tax_liability == pytest.approx(expected)
        assert result.is_liable

    def test_rate_band_frozen(self):
        band = RateBand(threshold=10_000_000, rate=0.01)
        with pytest.raises(ValidationError, match="frozen"):
            band.rate = 0.02

    def test_rate_band_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            RateBand(threshold=0, rate=0.01, surprise="bad")


class TestNegativeWealth:
    def test_negative_net_value_floored_at_zero(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 100_000, 500_000),
        ])
        result = taxable_wealth_for_person(person.assets, frozenset())
        assert result == 0.0

    def test_mixed_positive_negative_individual_unit(self):
        p1 = make_person("p1", [(AssetType.FINANCIAL, 15_000_000, 0)])
        p2 = make_person("p2", [(AssetType.FINANCIAL, 100_000, 500_000)])
        hh = make_household([p1, p2])
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        result = compute_wealth_tax(hh, config)
        assert result.tax_liability == pytest.approx(50_000)
        assert result.taxable_wealth == 15_000_000

    def test_all_exempt_assets_zero_liability(self):
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 2_000_000, 0),
            (AssetType.DB_PENSION, 1_000_000, 0),
        ])
        hh = make_household([person])
        config = WealthTaxConfig(
            threshold=0,
            rate=0.01,
            exempt_asset_types=frozenset({AssetType.MAIN_RESIDENCE, AssetType.DB_PENSION}),
        )
        result = compute_wealth_tax(hh, config)
        assert result.tax_liability == 0.0
        assert result.taxable_wealth == 0.0
        assert not result.is_liable


class TestAggregateRevenueExtended:
    def test_liable_sample_count(self):
        wealthy = make_household(
            [make_person("p1", [(AssetType.FINANCIAL, 50_000_000, 0)])],
            weight=1000, household_id="hh1",
        )
        poor = make_household(
            [make_person("p2", [(AssetType.FINANCIAL, 10_000, 0)])],
            weight=5000, household_id="hh2",
        )
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        result = compute_aggregate_revenue([wealthy, poor], config)
        assert result.liable_sample_count == 1

    def test_liable_sample_count_zero(self):
        poor = make_household(
            [make_person("p1", [(AssetType.FINANCIAL, 10_000, 0)])],
            weight=5000, household_id="hh1",
        )
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        result = compute_aggregate_revenue([poor], config)
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
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        result = compute_aggregate_revenue([hh1, hh2], config)
        expected_rev = (10_000_000 * 0.01 * 100) + (20_000_000 * 0.01 * 200)
        expected_mean = expected_rev / (100 + 200)
        assert result.mean_liability == pytest.approx(expected_mean)


class TestConfigValidation:
    def test_empty_rate_bands_rejected(self):
        with pytest.raises(ValidationError):
            WealthTaxConfig(rate_bands=())

    def test_duplicate_thresholds_rejected(self):
        with pytest.raises(ValidationError, match="unique thresholds"):
            WealthTaxConfig(
                rate_bands=(
                    RateBand(threshold=5_000_000, rate=0.005),
                    RateBand(threshold=5_000_000, rate=0.01),
                ),
            )

    def test_conflicting_flat_and_progressive_rejected(self):
        with pytest.raises(ValidationError, match="rate_bands is set"):
            WealthTaxConfig(
                threshold=10_000_000,
                rate=0.05,
                rate_bands=(RateBand(threshold=5_000_000, rate=0.01),),
            )

    def test_rate_bands_with_defaults_accepted(self):
        config = WealthTaxConfig(
            rate_bands=(RateBand(threshold=5_000_000, rate=0.01),),
        )
        assert config.rate_bands is not None

    def test_unsorted_bands_same_result(self):
        bands_sorted = (
            RateBand(threshold=5_000_000, rate=0.005),
            RateBand(threshold=10_000_000, rate=0.01),
        )
        bands_reversed = (bands_sorted[1], bands_sorted[0])
        config_sorted = WealthTaxConfig(rate_bands=bands_sorted)
        config_reversed = WealthTaxConfig(rate_bands=bands_reversed)
        assert _compute_liability(15_000_000, config_sorted) == _compute_liability(
            15_000_000, config_reversed
        )

    def test_zero_wealth_progressive(self):
        config = WealthTaxConfig(
            rate_bands=(RateBand(threshold=0, rate=0.01),),
        )
        assert _compute_liability(0, config) == 0.0

    def test_negative_wealth_returns_zero(self):
        config = WealthTaxConfig(threshold=0, rate=0.01)
        assert _compute_liability(-1_000_000, config) == 0.0

    def test_negative_wealth_progressive_returns_zero(self):
        config = WealthTaxConfig(
            rate_bands=(RateBand(threshold=0, rate=0.01),),
        )
        assert _compute_liability(-500_000, config) == 0.0


class TestEffectiveRateEdgeCases:
    def test_negative_total_wealth_positive_taxable(self):
        p = make_person(assets=[
            (AssetType.FINANCIAL, 15_000_000, 0),
            (AssetType.MAIN_RESIDENCE, 1_000_000, 20_000_000),
        ])
        hh = make_household([p])
        config = WealthTaxConfig(
            threshold=10_000_000,
            rate=0.01,
            exempt_asset_types=frozenset({AssetType.MAIN_RESIDENCE}),
        )
        result = compute_wealth_tax(hh, config)
        assert result.taxable_wealth == 15_000_000
        assert result.tax_liability == pytest.approx(50_000)
        assert result.effective_rate == 0.0

    def test_mean_liability_excludes_non_liable(self):
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
        config = WealthTaxConfig(threshold=10_000_000, rate=0.01)
        result = compute_aggregate_revenue([wealthy, middle], config)
        expected_liability = (50_000_000 - 10_000_000) * 0.01
        expected_mean = (expected_liability * 1000) / 1000
        assert result.mean_liability == pytest.approx(expected_mean)


class TestWealthTaxResult:
    def test_round_trip(self):
        result = WealthTaxResult(
            household_id="hh1",
            taxable_wealth=15_000_000,
            tax_liability=50_000,
            effective_rate=0.0025,
            is_liable=True,
        )
        data = result.model_dump()
        r2 = WealthTaxResult.model_validate(data)
        assert r2.household_id == "hh1"
        assert r2.tax_liability == 50_000
