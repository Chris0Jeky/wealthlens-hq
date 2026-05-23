"""Tests for Family D IHT baseline module."""

from __future__ import annotations

import pytest
from _helpers import make_household, make_person
from pydantic import ValidationError

from wealthlens_sim.reforms.d_iht_reform import (
    HouseholdIHTResult,
    IHTConfig,
    IHTResult,
    PersonIHTFlags,
    _compute_apr_bpr_relief,
    _compute_person_iht,
    _compute_rnrb,
    compute_aggregate_iht_revenue,
    compute_household_iht,
)
from wealthlens_sim.schema.base import Nation
from wealthlens_sim.schema.household import AssetType, Household


class TestIHTConfig:
    def test_defaults(self):
        config = IHTConfig()
        assert config.nil_rate_band == 325_000
        assert config.residence_nil_rate_band == 175_000
        assert config.rnrb_taper_threshold == 2_000_000
        assert config.main_rate == 0.40
        assert config.charitable_rate == 0.36
        assert config.charitable_threshold == 0.10
        assert config.apr_bpr_allowance == 2_500_000
        assert config.apr_bpr_relief_above == 0.50
        assert config.include_pensions is False
        assert config.spousal_exempt is True

    def test_frozen(self):
        config = IHTConfig()
        with pytest.raises(ValidationError, match="frozen"):
            config.main_rate = 0.45

    def test_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            IHTConfig(surprise="bad")

    def test_charitable_rate_must_not_exceed_main(self):
        with pytest.raises(ValidationError, match="must not exceed"):
            IHTConfig(charitable_rate=0.45, main_rate=0.40)

    def test_equal_rates_accepted(self):
        config = IHTConfig(charitable_rate=0.40, main_rate=0.40)
        assert config.charitable_rate == config.main_rate

    def test_custom_nrb(self):
        config = IHTConfig(nil_rate_band=500_000)
        assert config.nil_rate_band == 500_000

    def test_zero_nrb(self):
        config = IHTConfig(nil_rate_band=0)
        assert config.nil_rate_band == 0

    def test_pensions_included(self):
        config = IHTConfig(include_pensions=True)
        assert config.include_pensions is True


class TestComputeRNRB:
    def test_no_residence(self):
        config = IHTConfig()
        assert _compute_rnrb(500_000, False, True, config) == 0.0

    def test_no_descendants(self):
        config = IHTConfig()
        assert _compute_rnrb(500_000, True, False, config) == 0.0

    def test_full_rnrb(self):
        config = IHTConfig()
        assert _compute_rnrb(500_000, True, True, config) == 175_000

    def test_at_taper_threshold(self):
        config = IHTConfig()
        assert _compute_rnrb(2_000_000, True, True, config) == 175_000

    def test_taper_partial(self):
        config = IHTConfig()
        rnrb = _compute_rnrb(2_100_000, True, True, config)
        expected = 175_000 - (100_000 / 2)
        assert rnrb == pytest.approx(expected)

    def test_taper_to_zero(self):
        config = IHTConfig()
        rnrb = _compute_rnrb(2_350_000, True, True, config)
        assert rnrb == 0.0

    def test_taper_beyond_zero(self):
        config = IHTConfig()
        rnrb = _compute_rnrb(3_000_000, True, True, config)
        assert rnrb == 0.0


class TestComputeAPRBPRRelief:
    def test_zero_qualifying(self):
        config = IHTConfig()
        assert _compute_apr_bpr_relief(0, config) == 0.0

    def test_negative_qualifying(self):
        config = IHTConfig()
        assert _compute_apr_bpr_relief(-100_000, config) == 0.0

    def test_below_allowance(self):
        config = IHTConfig()
        relief = _compute_apr_bpr_relief(1_000_000, config)
        assert relief == 1_000_000

    def test_at_allowance(self):
        config = IHTConfig()
        relief = _compute_apr_bpr_relief(2_500_000, config)
        assert relief == 2_500_000

    def test_above_allowance(self):
        config = IHTConfig()
        relief = _compute_apr_bpr_relief(4_500_000, config)
        expected = 2_500_000 + (2_000_000 * 0.50)
        assert relief == pytest.approx(expected)

    def test_large_qualifying(self):
        config = IHTConfig()
        relief = _compute_apr_bpr_relief(10_000_000, config)
        expected = 2_500_000 + (7_500_000 * 0.50)
        assert relief == pytest.approx(expected)


class TestComputePersonIHT:
    def test_zero_estate(self):
        result = _compute_person_iht(0, False, False, 0, False, 0.0, IHTConfig())
        assert not result.is_liable
        assert result.iht_liability == 0.0

    def test_negative_estate(self):
        result = _compute_person_iht(-100_000, False, False, 0, False, 0.0, IHTConfig())
        assert not result.is_liable
        assert result.estate_value == 0.0

    def test_spousal_exempt(self):
        config = IHTConfig()
        result = _compute_person_iht(5_000_000, True, True, 0, True, 0.0, config)
        assert not result.is_liable
        assert result.is_spousal_exempt
        assert result.iht_liability == 0.0
        assert result.estate_value == 5_000_000

    def test_below_nrb(self):
        config = IHTConfig()
        result = _compute_person_iht(300_000, False, False, 0, False, 0.0, config)
        assert not result.is_liable
        assert result.taxable_estate == 0.0

    def test_at_nrb(self):
        config = IHTConfig()
        result = _compute_person_iht(325_000, False, False, 0, False, 0.0, config)
        assert not result.is_liable

    def test_above_nrb_no_rnrb(self):
        config = IHTConfig()
        estate = 500_000
        result = _compute_person_iht(estate, False, False, 0, False, 0.0, config)
        expected_taxable = estate - 325_000
        assert result.is_liable
        assert result.taxable_estate == expected_taxable
        assert result.iht_liability == pytest.approx(expected_taxable * 0.40)
        assert result.iht_rate_applied == 0.40

    def test_with_rnrb(self):
        config = IHTConfig()
        estate = 600_000
        result = _compute_person_iht(estate, True, True, 0, False, 0.0, config)
        total_nrb = 325_000 + 175_000
        expected_taxable = estate - total_nrb
        assert result.is_liable
        assert result.taxable_estate == expected_taxable
        assert result.iht_liability == pytest.approx(expected_taxable * 0.40)
        assert result.rnrb_used == 175_000

    def test_rnrb_taper(self):
        config = IHTConfig()
        estate = 2_200_000
        result = _compute_person_iht(estate, True, True, 0, False, 0.0, config)
        expected_rnrb = 175_000 - (200_000 / 2)
        total_nrb = 325_000 + expected_rnrb
        expected_taxable = estate - total_nrb
        assert result.rnrb_used == pytest.approx(expected_rnrb)
        assert result.taxable_estate == pytest.approx(expected_taxable)

    def test_charitable_rate(self):
        config = IHTConfig()
        estate = 1_000_000
        result = _compute_person_iht(estate, False, False, 0, False, 0.15, config)
        expected_taxable = estate - 325_000
        assert result.iht_rate_applied == 0.36
        assert result.iht_liability == pytest.approx(expected_taxable * 0.36)

    def test_charitable_below_threshold(self):
        config = IHTConfig()
        estate = 1_000_000
        result = _compute_person_iht(estate, False, False, 0, False, 0.05, config)
        assert result.iht_rate_applied == 0.40

    def test_apr_bpr_below_allowance(self):
        config = IHTConfig()
        estate = 3_000_000
        result = _compute_person_iht(estate, False, False, 2_000_000, False, 0.0, config)
        estate_after_relief = estate - 2_000_000
        expected_taxable = max(0, estate_after_relief - 325_000)
        assert result.apr_bpr_relief == 2_000_000
        assert result.taxable_estate == pytest.approx(expected_taxable)

    def test_apr_bpr_above_allowance(self):
        config = IHTConfig()
        estate = 5_000_000
        qualifying = 4_000_000
        result = _compute_person_iht(estate, False, False, qualifying, False, 0.0, config)
        expected_relief = 2_500_000 + (1_500_000 * 0.50)
        assert result.apr_bpr_relief == pytest.approx(expected_relief)

    def test_apr_bpr_eliminates_liability(self):
        config = IHTConfig()
        estate = 2_000_000
        result = _compute_person_iht(estate, False, False, 2_000_000, False, 0.0, config)
        assert not result.is_liable
        assert result.taxable_estate == 0.0

    def test_effective_rate(self):
        config = IHTConfig()
        estate = 1_000_000
        result = _compute_person_iht(estate, False, False, 0, False, 0.0, config)
        assert result.effective_rate == pytest.approx(result.iht_liability / estate)

    def test_spousal_exempt_disabled(self):
        config = IHTConfig(spousal_exempt=False)
        result = _compute_person_iht(1_000_000, False, False, 0, True, 0.0, config)
        assert result.is_liable
        assert not result.is_spousal_exempt

    def test_very_large_estate(self):
        config = IHTConfig()
        estate = 100_000_000
        result = _compute_person_iht(estate, True, True, 0, False, 0.0, config)
        assert result.rnrb_used == 0.0
        assert result.iht_liability == pytest.approx((estate - 325_000) * 0.40)


class TestComputeHouseholdIHT:
    def test_single_person_liable(self):
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 800_000, 100_000),
            (AssetType.FINANCIAL, 300_000, 0),
        ])
        hh = make_household([person])
        result = compute_household_iht(hh, IHTConfig())
        assert result.is_liable
        assert result.total_iht_liability > 0
        assert len(result.person_results) == 1

    def test_single_person_below_nrb(self):
        person = make_person(assets=[
            (AssetType.FINANCIAL, 200_000, 0),
        ])
        hh = make_household([person])
        result = compute_household_iht(hh, IHTConfig())
        assert not result.is_liable
        assert result.total_iht_liability == 0.0

    def test_multiple_persons(self):
        p1 = make_person("p1", assets=[
            (AssetType.MAIN_RESIDENCE, 1_000_000, 0),
        ])
        p2 = make_person("p2", assets=[
            (AssetType.FINANCIAL, 200_000, 0),
        ])
        hh = make_household([p1, p2])
        result = compute_household_iht(hh, IHTConfig())
        assert len(result.person_results) == 2
        assert result.total_iht_liability == sum(r.iht_liability for r in result.person_results)

    def test_person_flags_married(self):
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 2_000_000, 0),
        ])
        hh = make_household([person])
        flags = {"p1": {"is_married": True}}
        result = compute_household_iht(hh, IHTConfig(), person_flags=flags)
        assert not result.is_liable
        pr = result.person_results[0]
        assert pr.is_spousal_exempt

    def test_person_flags_descendants(self):
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 700_000, 0),
        ])
        hh = make_household([person])
        no_desc = compute_household_iht(hh, IHTConfig())
        with_desc = compute_household_iht(
            hh, IHTConfig(),
            person_flags={"p1": {"has_direct_descendants": True}},
        )
        assert with_desc.total_iht_liability < no_desc.total_iht_liability

    def test_pension_excluded_by_default(self):
        person = make_person(assets=[
            (AssetType.DC_PENSION, 1_000_000, 0),
            (AssetType.FINANCIAL, 200_000, 0),
        ])
        hh = make_household([person])
        result = compute_household_iht(hh, IHTConfig())
        pr = result.person_results[0]
        assert pr.estate_value == 200_000

    def test_pension_included_when_configured(self):
        person = make_person(assets=[
            (AssetType.DC_PENSION, 1_000_000, 0),
            (AssetType.FINANCIAL, 200_000, 0),
        ])
        hh = make_household([person])
        config = IHTConfig(include_pensions=True)
        result = compute_household_iht(hh, config)
        pr = result.person_results[0]
        assert pr.estate_value == 1_200_000

    def test_business_assets_get_apr_bpr(self):
        person = make_person(assets=[
            (AssetType.PRIVATE_BUSINESS, 3_000_000, 0),
            (AssetType.FINANCIAL, 500_000, 0),
        ])
        hh = make_household([person])
        result = compute_household_iht(hh, IHTConfig())
        pr = result.person_results[0]
        assert pr.apr_bpr_relief > 0

    def test_result_frozen(self):
        person = make_person(assets=[(AssetType.FINANCIAL, 1_000_000, 0)])
        hh = make_household([person])
        result = compute_household_iht(hh, IHTConfig())
        with pytest.raises(ValidationError, match="frozen"):
            result.total_iht_liability = 0.0


class TestAggregateIHTRevenue:
    def _make_population(self) -> list[Household]:
        wealthy = make_household(
            [make_person("p1", assets=[
                (AssetType.MAIN_RESIDENCE, 3_000_000, 0),
                (AssetType.FINANCIAL, 2_000_000, 0),
            ])],
            nation=Nation.ENGLAND,
            weight=500,
            household_id="hh_wealthy",
        )
        middle = make_household(
            [make_person("p2", assets=[
                (AssetType.MAIN_RESIDENCE, 400_000, 100_000),
                (AssetType.FINANCIAL, 100_000, 0),
            ])],
            nation=Nation.SCOTLAND,
            weight=5_000,
            household_id="hh_middle",
        )
        below = make_household(
            [make_person("p3", assets=[
                (AssetType.FINANCIAL, 50_000, 0),
            ])],
            nation=Nation.WALES,
            weight=20_000,
            household_id="hh_below",
        )
        return [wealthy, middle, below]

    def test_basic_revenue(self):
        config = IHTConfig()
        result = compute_aggregate_iht_revenue(self._make_population(), config)
        assert result.total_revenue_bn > 0
        assert result.population_count == 500 + 5_000 + 20_000

    def test_liable_counts(self):
        config = IHTConfig()
        result = compute_aggregate_iht_revenue(self._make_population(), config)
        assert result.taxpayer_count > 0
        assert result.liable_sample_count >= 1

    def test_revenue_by_nation(self):
        config = IHTConfig()
        result = compute_aggregate_iht_revenue(self._make_population(), config)
        assert "england" in result.revenue_by_nation
        assert result.revenue_by_nation["england"] > 0

    def test_no_liable_households(self):
        below = make_household(
            [make_person("p1", assets=[(AssetType.FINANCIAL, 50_000, 0)])],
            weight=10_000, household_id="hh1",
        )
        config = IHTConfig()
        result = compute_aggregate_iht_revenue([below], config)
        assert result.total_revenue_bn == 0.0
        assert result.mean_liability == 0.0

    def test_empty_population(self):
        config = IHTConfig()
        result = compute_aggregate_iht_revenue([], config)
        assert result.total_revenue_bn == 0.0
        assert result.population_count == 0

    def test_result_frozen(self):
        config = IHTConfig()
        result = compute_aggregate_iht_revenue(self._make_population(), config)
        with pytest.raises(ValidationError, match="frozen"):
            result.total_revenue_bn = 0.0

    def test_mean_liability(self):
        config = IHTConfig()
        result = compute_aggregate_iht_revenue(self._make_population(), config)
        if result.taxpayer_count > 0:
            assert result.mean_liability > 0


class TestIHTResultModel:
    def test_round_trip(self):
        result = IHTResult(
            person_id="p1",
            estate_value=1_000_000,
            nil_rate_band_used=325_000,
            rnrb_used=0.0,
            apr_bpr_relief=0.0,
            taxable_estate=675_000,
            iht_rate_applied=0.40,
            iht_liability=270_000,
            effective_rate=0.27,
            is_liable=True,
            is_spousal_exempt=False,
        )
        data = result.model_dump()
        r2 = IHTResult.model_validate(data)
        assert r2.person_id == "p1"
        assert r2.iht_liability == 270_000

    def test_frozen(self):
        result = IHTResult(
            person_id="p1",
            estate_value=1_000_000,
            nil_rate_band_used=325_000,
            rnrb_used=0.0,
            apr_bpr_relief=0.0,
            taxable_estate=675_000,
            iht_rate_applied=0.40,
            iht_liability=270_000,
            effective_rate=0.27,
            is_liable=True,
            is_spousal_exempt=False,
        )
        with pytest.raises(ValidationError, match="frozen"):
            result.iht_liability = 0.0


class TestHouseholdIHTResultModel:
    def test_round_trip(self):
        result = HouseholdIHTResult(
            household_id="hh1",
            person_results=(
                IHTResult(
                    person_id="p1",
                    estate_value=1_000_000,
                    nil_rate_band_used=325_000,
                    rnrb_used=0.0,
                    apr_bpr_relief=0.0,
                    taxable_estate=675_000,
                    iht_rate_applied=0.40,
                    iht_liability=270_000,
                    effective_rate=0.27,
                    is_liable=True,
                    is_spousal_exempt=False,
                ),
            ),
            total_iht_liability=270_000,
            is_liable=True,
        )
        data = result.model_dump()
        r2 = HouseholdIHTResult.model_validate(data)
        assert r2.household_id == "hh1"
        assert len(r2.person_results) == 1


class TestStatePensionExclusion:
    """STATE_PENSION must always be excluded from the estate, even with include_pensions=True."""

    def test_state_pension_excluded_by_default(self):
        person = make_person(assets=[
            (AssetType.STATE_PENSION, 200_000, 0),
            (AssetType.FINANCIAL, 100_000, 0),
        ])
        hh = make_household([person])
        result = compute_household_iht(hh, IHTConfig())
        pr = result.person_results[0]
        assert pr.estate_value == 100_000

    def test_state_pension_excluded_even_with_include_pensions(self):
        person = make_person(assets=[
            (AssetType.STATE_PENSION, 200_000, 0),
            (AssetType.DC_PENSION, 500_000, 0),
            (AssetType.FINANCIAL, 100_000, 0),
        ])
        hh = make_household([person])
        config = IHTConfig(include_pensions=True)
        result = compute_household_iht(hh, config)
        pr = result.person_results[0]
        assert pr.estate_value == 600_000

    def test_state_pension_only_estate_zero(self):
        person = make_person(assets=[
            (AssetType.STATE_PENSION, 300_000, 0),
        ])
        hh = make_household([person])
        result = compute_household_iht(hh, IHTConfig(include_pensions=True))
        pr = result.person_results[0]
        assert pr.estate_value == 0.0
        assert not result.is_liable


class TestNRBRNRBBoundary:
    """Estate exactly at £500k NRB+RNRB combined threshold."""

    def test_estate_exactly_at_combined_nrb_rnrb(self):
        config = IHTConfig()
        estate = 500_000
        result = _compute_person_iht(estate, True, True, 0, False, 0.0, config)
        assert result.nil_rate_band_used == 325_000
        assert result.rnrb_used == 175_000
        assert result.taxable_estate == 0.0
        assert not result.is_liable

    def test_estate_one_pound_above_combined(self):
        config = IHTConfig()
        estate = 500_001
        result = _compute_person_iht(estate, True, True, 0, False, 0.0, config)
        assert result.taxable_estate == 1.0
        assert result.is_liable
        assert result.iht_liability == pytest.approx(0.40)


class TestRNRBFullTaper:
    """£2.35M estate fully tapers RNRB to zero."""

    def test_full_taper_at_2_350_000(self):
        config = IHTConfig()
        estate = 2_350_000
        result = _compute_person_iht(estate, True, True, 0, False, 0.0, config)
        assert result.rnrb_used == 0.0
        expected_taxable = estate - 325_000
        assert result.taxable_estate == pytest.approx(expected_taxable)
        assert result.iht_liability == pytest.approx(expected_taxable * 0.40)

    def test_taper_one_below_full(self):
        config = IHTConfig()
        estate = 2_349_998
        result = _compute_person_iht(estate, True, True, 0, False, 0.0, config)
        assert result.rnrb_used == pytest.approx(1.0)


class TestAPRBPRExceedsEstate:
    """APR/BPR relief that exceeds the estate should floor taxable at zero."""

    def test_apr_bpr_exceeds_estate(self):
        config = IHTConfig()
        estate = 1_000_000
        qualifying = 2_000_000
        result = _compute_person_iht(estate, False, False, qualifying, False, 0.0, config)
        assert not result.is_liable
        assert result.taxable_estate == 0.0

    def test_apr_bpr_gross_value_used(self):
        person = make_person(assets=[
            (AssetType.PRIVATE_BUSINESS, 3_000_000, 500_000),
            (AssetType.FINANCIAL, 1_000_000, 0),
        ])
        hh = make_household([person])
        result = compute_household_iht(hh, IHTConfig())
        pr = result.person_results[0]
        expected_relief = 2_500_000 + (500_000 * 0.50)
        assert pr.apr_bpr_relief == pytest.approx(expected_relief)


class TestPersonIdPassthrough:
    """_compute_person_iht should set person_id from the keyword argument."""

    def test_person_id_default_empty(self):
        result = _compute_person_iht(500_000, False, False, 0, False, 0.0, IHTConfig())
        assert result.person_id == ""

    def test_person_id_set(self):
        result = _compute_person_iht(
            500_000, False, False, 0, False, 0.0, IHTConfig(), person_id="test_person",
        )
        assert result.person_id == "test_person"

    def test_household_sets_person_id(self):
        person = make_person("custom_id", assets=[
            (AssetType.FINANCIAL, 1_000_000, 0),
        ])
        hh = make_household([person])
        result = compute_household_iht(hh, IHTConfig())
        assert result.person_results[0].person_id == "custom_id"


class TestPersonIHTFlagsType:
    """PersonIHTFlags TypedDict provides type-safe person metadata."""

    def test_typed_flags_accepted(self):
        flags: PersonIHTFlags = {
            "is_married": True,
            "has_direct_descendants": True,
            "charitable_fraction": 0.15,
        }
        person = make_person(assets=[(AssetType.FINANCIAL, 1_000_000, 0)])
        hh = make_household([person])
        result = compute_household_iht(hh, IHTConfig(), person_flags={"p1": flags})
        assert not result.is_liable
        assert result.person_results[0].is_spousal_exempt

    def test_partial_flags(self):
        flags: PersonIHTFlags = {"has_direct_descendants": True}
        person = make_person(assets=[
            (AssetType.MAIN_RESIDENCE, 700_000, 0),
        ])
        hh = make_household([person])
        result = compute_household_iht(hh, IHTConfig(), person_flags={"p1": flags})
        pr = result.person_results[0]
        assert pr.rnrb_used == 175_000
