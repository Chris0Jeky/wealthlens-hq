"""Tests for Family E HVCTS sub-module."""

from __future__ import annotations

import pytest
from _helpers import make_household, make_person
from pydantic import ValidationError

from wealthlens_sim.reforms.e_property_tax import (
    ANNOUNCED_BANDS,
    HVCTSBand,
    HVCTSConfig,
    HVCTSResult,
    _surcharge_for_property,
    compute_aggregate_hvcts_revenue,
    compute_hvcts,
)
from wealthlens_sim.schema.base import Nation
from wealthlens_sim.schema.household import AssetType, Household


class TestHVCTSBand:
    def test_basic_band(self):
        band = HVCTSBand(lower=2_000_000, upper=2_500_000, annual_surcharge=2_500)
        assert band.lower == 2_000_000
        assert band.upper == 2_500_000
        assert band.annual_surcharge == 2_500

    def test_open_ended_band(self):
        band = HVCTSBand(lower=5_000_000, upper=None, annual_surcharge=7_500)
        assert band.upper is None

    def test_upper_must_exceed_lower(self):
        with pytest.raises(ValidationError, match="must exceed"):
            HVCTSBand(lower=5_000_000, upper=5_000_000, annual_surcharge=2_500)

    def test_upper_below_lower_rejected(self):
        with pytest.raises(ValidationError, match="must exceed"):
            HVCTSBand(lower=5_000_000, upper=3_000_000, annual_surcharge=2_500)

    def test_frozen(self):
        band = HVCTSBand(lower=2_000_000, upper=2_500_000, annual_surcharge=2_500)
        with pytest.raises(ValidationError, match="frozen"):
            band.annual_surcharge = 5_000

    def test_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            HVCTSBand(lower=0, upper=100, annual_surcharge=50, surprise="bad")


class TestAnnouncedBands:
    def test_four_bands(self):
        assert len(ANNOUNCED_BANDS) == 4

    def test_band_values(self):
        assert ANNOUNCED_BANDS[0].annual_surcharge == 2_500
        assert ANNOUNCED_BANDS[1].annual_surcharge == 3_500
        assert ANNOUNCED_BANDS[2].annual_surcharge == 5_000
        assert ANNOUNCED_BANDS[3].annual_surcharge == 7_500

    def test_last_band_open_ended(self):
        assert ANNOUNCED_BANDS[3].upper is None


class TestHVCTSConfig:
    def test_default_config(self):
        config = HVCTSConfig()
        assert config.nation == Nation.ENGLAND
        assert len(config.bands) == 4

    def test_custom_bands(self):
        bands = (HVCTSBand(lower=1_000_000, upper=None, annual_surcharge=1_000),)
        config = HVCTSConfig(bands=bands)
        assert len(config.bands) == 1

    def test_empty_bands_rejected(self):
        with pytest.raises(ValidationError):
            HVCTSConfig(bands=())

    def test_duplicate_lower_bounds_rejected(self):
        with pytest.raises(ValidationError, match="unique lower"):
            HVCTSConfig(bands=(
                HVCTSBand(lower=2_000_000, upper=3_000_000, annual_surcharge=2_500),
                HVCTSBand(lower=2_000_000, upper=None, annual_surcharge=5_000),
            ))

    def test_uk_aggregate_rejected(self):
        with pytest.raises(ValidationError, match="constituent nation"):
            HVCTSConfig(nation=Nation.UK)

    def test_scotland_allowed(self):
        config = HVCTSConfig(nation=Nation.SCOTLAND)
        assert config.nation == Nation.SCOTLAND

    def test_frozen(self):
        config = HVCTSConfig()
        with pytest.raises(ValidationError, match="frozen"):
            config.nation = Nation.WALES

    def test_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            HVCTSConfig(surprise="bad")


class TestSurchargeForProperty:
    def test_below_threshold(self):
        assert _surcharge_for_property(1_500_000, ANNOUNCED_BANDS) == 0.0

    def test_exactly_at_lower_bound(self):
        assert _surcharge_for_property(2_000_000, ANNOUNCED_BANDS) == 2_500

    def test_band_1(self):
        assert _surcharge_for_property(2_200_000, ANNOUNCED_BANDS) == 2_500

    def test_at_band_boundary(self):
        assert _surcharge_for_property(2_500_000, ANNOUNCED_BANDS) == 3_500

    def test_band_2(self):
        assert _surcharge_for_property(3_000_000, ANNOUNCED_BANDS) == 3_500

    def test_at_band_boundary_3_5m(self):
        assert _surcharge_for_property(3_500_000, ANNOUNCED_BANDS) == 5_000

    def test_band_3(self):
        assert _surcharge_for_property(4_000_000, ANNOUNCED_BANDS) == 5_000

    def test_at_band_boundary_5m(self):
        assert _surcharge_for_property(5_000_000, ANNOUNCED_BANDS) == 7_500

    def test_band_4_open(self):
        assert _surcharge_for_property(10_000_000, ANNOUNCED_BANDS) == 7_500

    def test_very_high_value(self):
        assert _surcharge_for_property(100_000_000, ANNOUNCED_BANDS) == 7_500

    def test_zero_value(self):
        assert _surcharge_for_property(0, ANNOUNCED_BANDS) == 0.0

    def test_negative_value(self):
        assert _surcharge_for_property(-1_000_000, ANNOUNCED_BANDS) == 0.0


class TestComputeHVCTS:
    def test_england_liable_property(self):
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 3_000_000, 500_000),
        ])
        hh = make_household([person], nation=Nation.ENGLAND)
        result = compute_hvcts(hh, HVCTSConfig())
        assert result.properties_in_scope == 1
        assert result.total_surcharge == 3_500
        assert result.is_liable

    def test_scotland_excluded(self):
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 5_000_000, 0),
        ])
        hh = make_household([person], nation=Nation.SCOTLAND)
        result = compute_hvcts(hh, HVCTSConfig())
        assert result.properties_in_scope == 0
        assert result.total_surcharge == 0.0
        assert not result.is_liable

    def test_below_threshold_not_liable(self):
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 1_500_000, 0),
        ])
        hh = make_household([person], nation=Nation.ENGLAND)
        result = compute_hvcts(hh, HVCTSConfig())
        assert result.properties_in_scope == 0
        assert result.total_surcharge == 0.0
        assert not result.is_liable

    def test_multiple_properties(self):
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 3_000_000, 0),
            (AssetType.OTHER_PROPERTY, 6_000_000, 0),
        ])
        hh = make_household([person], nation=Nation.ENGLAND)
        result = compute_hvcts(hh, HVCTSConfig())
        assert result.properties_in_scope == 2
        assert result.total_surcharge == 3_500 + 7_500

    def test_non_property_assets_excluded(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 10_000_000, 0),
            (AssetType.MAIN_RESIDENCE, 3_000_000, 0),
        ])
        hh = make_household([person], nation=Nation.ENGLAND)
        result = compute_hvcts(hh, HVCTSConfig())
        assert result.properties_in_scope == 1
        assert result.total_surcharge == 3_500

    def test_uses_gross_value_not_net(self):
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 3_000_000, 2_500_000),
        ])
        hh = make_household([person], nation=Nation.ENGLAND)
        result = compute_hvcts(hh, HVCTSConfig())
        assert result.total_surcharge == 3_500

    def test_multiple_persons_properties(self):
        p1 = make_person("p1", [(AssetType.MAIN_RESIDENCE, 2_200_000, 0)])
        p2 = make_person("p2", [(AssetType.OTHER_PROPERTY, 4_000_000, 0)])
        hh = make_household([p1, p2], nation=Nation.ENGLAND)
        result = compute_hvcts(hh, HVCTSConfig())
        assert result.properties_in_scope == 2
        assert result.total_surcharge == 2_500 + 5_000

    def test_custom_bands(self):
        bands = (HVCTSBand(lower=1_000_000, upper=None, annual_surcharge=1_000),)
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 1_500_000, 0),
        ])
        hh = make_household([person], nation=Nation.ENGLAND)
        config = HVCTSConfig(bands=bands)
        result = compute_hvcts(hh, config)
        assert result.total_surcharge == 1_000

    def test_scotland_config_scotland_household(self):
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 3_000_000, 0),
        ])
        hh = make_household([person], nation=Nation.SCOTLAND)
        config = HVCTSConfig(nation=Nation.SCOTLAND)
        result = compute_hvcts(hh, config)
        assert result.is_liable


class TestAggregateHVCTSRevenue:
    def _make_population(self) -> list[Household]:
        wealthy = make_household(
            [make_person("p1", [
                (AssetType.MAIN_RESIDENCE, 6_000_000, 0),
                (AssetType.OTHER_PROPERTY, 3_000_000, 0),
            ])],
            nation=Nation.ENGLAND,
            weight=500,
            household_id="hh_wealthy",
        )
        mid = make_household(
            [make_person("p2", [(AssetType.MAIN_RESIDENCE, 2_200_000, 0)])],
            nation=Nation.ENGLAND,
            weight=2_000,
            household_id="hh_mid",
        )
        below = make_household(
            [make_person("p3", [(AssetType.MAIN_RESIDENCE, 800_000, 0)])],
            nation=Nation.ENGLAND,
            weight=10_000,
            household_id="hh_below",
        )
        scotland = make_household(
            [make_person("p4", [(AssetType.MAIN_RESIDENCE, 5_000_000, 0)])],
            nation=Nation.SCOTLAND,
            weight=1_000,
            household_id="hh_scot",
        )
        return [wealthy, mid, below, scotland]

    def test_basic_revenue(self):
        config = HVCTSConfig()
        result = compute_aggregate_hvcts_revenue(self._make_population(), config)
        wealthy_surcharge = 7_500 + 3_500
        mid_surcharge = 2_500
        expected = (wealthy_surcharge * 500 + mid_surcharge * 2_000) / 1e9
        assert result.total_revenue_bn == pytest.approx(expected)

    def test_liable_counts(self):
        config = HVCTSConfig()
        result = compute_aggregate_hvcts_revenue(self._make_population(), config)
        assert result.liable_household_count == 500 + 2_000
        assert result.liable_sample_count == 2

    def test_population_count(self):
        config = HVCTSConfig()
        result = compute_aggregate_hvcts_revenue(self._make_population(), config)
        assert result.population_count == 500 + 2_000 + 10_000 + 1_000

    def test_properties_in_scope(self):
        config = HVCTSConfig()
        result = compute_aggregate_hvcts_revenue(self._make_population(), config)
        assert result.properties_in_scope == (2 * 500) + (1 * 2_000)

    def test_no_liable(self):
        below = make_household(
            [make_person("p1", [(AssetType.MAIN_RESIDENCE, 500_000, 0)])],
            nation=Nation.ENGLAND,
            weight=10_000,
            household_id="hh1",
        )
        config = HVCTSConfig()
        result = compute_aggregate_hvcts_revenue([below], config)
        assert result.total_revenue_bn == 0.0
        assert result.mean_surcharge == 0.0

    def test_empty_population(self):
        config = HVCTSConfig()
        result = compute_aggregate_hvcts_revenue([], config)
        assert result.total_revenue_bn == 0.0
        assert result.population_count == 0

    def test_result_frozen(self):
        config = HVCTSConfig()
        result = compute_aggregate_hvcts_revenue(self._make_population(), config)
        with pytest.raises(ValidationError, match="frozen"):
            result.total_revenue_bn = 999.0

    def test_mean_surcharge(self):
        config = HVCTSConfig()
        result = compute_aggregate_hvcts_revenue(self._make_population(), config)
        wealthy_surcharge = 7_500 + 3_500
        mid_surcharge = 2_500
        total_rev = wealthy_surcharge * 500 + mid_surcharge * 2_000
        expected_mean = total_rev / (500 + 2_000)
        assert result.mean_surcharge == pytest.approx(expected_mean)

    def test_revenue_by_nation(self):
        config = HVCTSConfig()
        result = compute_aggregate_hvcts_revenue(self._make_population(), config)
        assert "england" in result.revenue_by_nation
        assert result.revenue_by_nation["england"] > 0
        assert result.revenue_by_nation.get("scotland", 0) == 0


class TestUnsortedBands:
    def test_unsorted_bands_eligible_properties(self):
        bands = (
            HVCTSBand(lower=5_000_000, upper=None, annual_surcharge=7_500),
            HVCTSBand(lower=2_000_000, upper=5_000_000, annual_surcharge=2_500),
        )
        config = HVCTSConfig(bands=bands)
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 3_000_000, 0),
        ])
        hh = make_household([person], nation=Nation.ENGLAND)
        result = compute_hvcts(hh, config)
        assert result.properties_in_scope == 1
        assert result.total_surcharge == 2_500

    def test_unsorted_bands_surcharge(self):
        bands = (
            HVCTSBand(lower=5_000_000, upper=None, annual_surcharge=7_500),
            HVCTSBand(lower=2_000_000, upper=5_000_000, annual_surcharge=2_500),
        )
        assert _surcharge_for_property(3_000_000, bands) == 2_500
        assert _surcharge_for_property(6_000_000, bands) == 7_500


class TestHVCTSResult:
    def test_round_trip(self):
        result = HVCTSResult(
            household_id="hh1",
            properties_in_scope=2,
            total_surcharge=11_000,
            is_liable=True,
        )
        data = result.model_dump()
        r2 = HVCTSResult.model_validate(data)
        assert r2.household_id == "hh1"
        assert r2.total_surcharge == 11_000

    def test_frozen(self):
        result = HVCTSResult(
            household_id="hh1",
            properties_in_scope=1,
            total_surcharge=2_500,
            is_liable=True,
        )
        with pytest.raises(ValidationError, match="frozen"):
            result.total_surcharge = 0
