"""Tests for Family C CGT baseline module."""

from __future__ import annotations

import pytest
from _helpers import make_household, make_person
from pydantic import ValidationError

from wealthlens_sim.reforms.c_cgt_reform import (
    CGTConfig,
    CGTResult,
    HouseholdCGTResult,
    TaxpayerType,
    _compute_person_cgt,
    compute_aggregate_cgt_revenue,
    compute_household_cgt,
)
from wealthlens_sim.schema.base import Nation
from wealthlens_sim.schema.household import Household


class TestCGTConfig:
    def test_defaults(self):
        config = CGTConfig()
        assert config.annual_exempt_amount == 3_000
        assert config.basic_rate == 0.18
        assert config.higher_rate == 0.24
        assert config.trustee_rate == 0.24
        assert config.badr_rate == 0.18
        assert config.death_uplift is True
        assert config.main_residence_exempt is True
        assert config.taxpayer_type == TaxpayerType.INDIVIDUAL

    def test_frozen(self):
        config = CGTConfig()
        with pytest.raises(ValidationError, match="frozen"):
            config.basic_rate = 0.20

    def test_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            CGTConfig(surprise="bad")

    def test_basic_rate_must_not_exceed_higher(self):
        with pytest.raises(ValidationError, match="must not exceed"):
            CGTConfig(basic_rate=0.30, higher_rate=0.24)

    def test_equal_rates_accepted(self):
        config = CGTConfig(basic_rate=0.24, higher_rate=0.24)
        assert config.basic_rate == config.higher_rate

    def test_custom_aea(self):
        config = CGTConfig(annual_exempt_amount=6_000)
        assert config.annual_exempt_amount == 6_000

    def test_zero_aea(self):
        config = CGTConfig(annual_exempt_amount=0)
        assert config.annual_exempt_amount == 0

    def test_trustee_type(self):
        config = CGTConfig(taxpayer_type=TaxpayerType.TRUSTEE)
        assert config.taxpayer_type == TaxpayerType.TRUSTEE


class TestComputePersonCGT:
    def test_no_gains(self):
        taxable, liability = _compute_person_cgt(0, 30_000, CGTConfig())
        assert taxable == 0.0
        assert liability == 0.0

    def test_gains_below_aea(self):
        taxable, liability = _compute_person_cgt(2_000, 30_000, CGTConfig())
        assert taxable == 0.0
        assert liability == 0.0

    def test_gains_exactly_at_aea(self):
        taxable, liability = _compute_person_cgt(3_000, 30_000, CGTConfig())
        assert taxable == 0.0
        assert liability == 0.0

    def test_basic_rate_taxpayer(self):
        config = CGTConfig()
        gains = 10_000
        income = 30_000
        taxable, liability = _compute_person_cgt(gains, income, config)
        expected_taxable = gains - config.annual_exempt_amount
        taxable_income = income - config.personal_allowance
        remaining_basic = config.basic_rate_band - taxable_income
        assert remaining_basic > expected_taxable
        assert taxable == expected_taxable
        assert liability == pytest.approx(expected_taxable * 0.18)

    def test_higher_rate_taxpayer(self):
        config = CGTConfig()
        gains = 50_000
        income = 100_000
        _taxable, liability = _compute_person_cgt(gains, income, config)
        expected_taxable = gains - config.annual_exempt_amount
        taxable_income = income - config.personal_allowance
        remaining_basic = max(0, config.basic_rate_band - taxable_income)
        assert remaining_basic == 0
        assert liability == pytest.approx(expected_taxable * 0.24)

    def test_split_across_bands(self):
        config = CGTConfig()
        income = 40_000
        gains = 20_000
        _taxable, liability = _compute_person_cgt(gains, income, config)
        expected_taxable = gains - config.annual_exempt_amount
        taxable_income = income - config.personal_allowance
        remaining_basic = config.basic_rate_band - taxable_income
        basic_portion = remaining_basic
        higher_portion = expected_taxable - remaining_basic
        expected_liability = basic_portion * 0.18 + higher_portion * 0.24
        assert liability == pytest.approx(expected_liability)

    def test_trustee_flat_rate(self):
        config = CGTConfig(taxpayer_type=TaxpayerType.TRUSTEE)
        gains = 50_000
        _taxable, liability = _compute_person_cgt(gains, 0, config)
        expected_taxable = gains - config.annual_exempt_amount
        assert liability == pytest.approx(expected_taxable * 0.24)

    def test_negative_gains(self):
        taxable, liability = _compute_person_cgt(-5_000, 30_000, CGTConfig())
        assert taxable == 0.0
        assert liability == 0.0

    def test_zero_income_basic_rate(self):
        config = CGTConfig()
        gains = 10_000
        _taxable, liability = _compute_person_cgt(gains, 0, config)
        expected_taxable = gains - config.annual_exempt_amount
        assert liability == pytest.approx(expected_taxable * 0.18)

    def test_very_high_gains(self):
        config = CGTConfig()
        gains = 10_000_000
        _taxable, liability = _compute_person_cgt(gains, 200_000, config)
        expected_taxable = gains - config.annual_exempt_amount
        assert liability == pytest.approx(expected_taxable * 0.24)


class TestComputeHouseholdCGT:
    def test_single_person_liable(self):
        person = make_person(capital_gains_realised=50_000, annual_income=60_000)
        hh = make_household([person])
        result = compute_household_cgt(hh, CGTConfig())
        assert result.is_liable
        assert result.total_cgt_liability > 0
        assert len(result.person_results) == 1

    def test_single_person_not_liable(self):
        person = make_person(capital_gains_realised=1_000, annual_income=30_000)
        hh = make_household([person])
        result = compute_household_cgt(hh, CGTConfig())
        assert not result.is_liable
        assert result.total_cgt_liability == 0.0

    def test_multiple_persons(self):
        p1 = make_person("p1", capital_gains_realised=50_000, annual_income=60_000)
        p2 = make_person("p2", capital_gains_realised=10_000, annual_income=30_000)
        hh = make_household([p1, p2])
        result = compute_household_cgt(hh, CGTConfig())
        assert len(result.person_results) == 2
        assert result.total_cgt_liability == sum(r.cgt_liability for r in result.person_results)

    def test_no_gains_household(self):
        person = make_person(capital_gains_realised=0, annual_income=50_000)
        hh = make_household([person])
        result = compute_household_cgt(hh, CGTConfig())
        assert not result.is_liable
        assert result.total_cgt_liability == 0.0

    def test_effective_rate(self):
        person = make_person(capital_gains_realised=50_000, annual_income=100_000)
        hh = make_household([person])
        result = compute_household_cgt(hh, CGTConfig())
        pr = result.person_results[0]
        assert pr.effective_rate == pytest.approx(pr.cgt_liability / 50_000)

    def test_result_frozen(self):
        person = make_person(capital_gains_realised=50_000, annual_income=60_000)
        hh = make_household([person])
        result = compute_household_cgt(hh, CGTConfig())
        with pytest.raises(ValidationError, match="frozen"):
            result.total_cgt_liability = 0.0


class TestAggregateCGTRevenue:
    def _make_population(self) -> list[Household]:
        wealthy = make_household(
            [make_person("p1", capital_gains_realised=500_000, annual_income=200_000)],
            nation=Nation.ENGLAND,
            weight=1_000,
            household_id="hh_wealthy",
        )
        middle = make_household(
            [make_person("p2", capital_gains_realised=10_000, annual_income=40_000)],
            nation=Nation.SCOTLAND,
            weight=5_000,
            household_id="hh_middle",
        )
        no_gains = make_household(
            [make_person("p3", capital_gains_realised=0, annual_income=30_000)],
            nation=Nation.WALES,
            weight=10_000,
            household_id="hh_no_gains",
        )
        return [wealthy, middle, no_gains]

    def test_basic_revenue(self):
        config = CGTConfig()
        result = compute_aggregate_cgt_revenue(self._make_population(), config)
        assert result.total_revenue_bn > 0
        assert result.population_count == 16_000

    def test_liable_counts(self):
        config = CGTConfig()
        result = compute_aggregate_cgt_revenue(self._make_population(), config)
        assert result.taxpayer_count == 1_000 + 5_000
        assert result.liable_sample_count == 2

    def test_revenue_by_nation(self):
        config = CGTConfig()
        result = compute_aggregate_cgt_revenue(self._make_population(), config)
        assert "england" in result.revenue_by_nation
        assert result.revenue_by_nation["england"] > 0

    def test_no_liable_households(self):
        no_gains = make_household(
            [make_person("p1", capital_gains_realised=0, annual_income=30_000)],
            weight=10_000, household_id="hh1",
        )
        config = CGTConfig()
        result = compute_aggregate_cgt_revenue([no_gains], config)
        assert result.total_revenue_bn == 0.0
        assert result.mean_liability == 0.0

    def test_empty_population(self):
        config = CGTConfig()
        result = compute_aggregate_cgt_revenue([], config)
        assert result.total_revenue_bn == 0.0
        assert result.population_count == 0

    def test_result_frozen(self):
        config = CGTConfig()
        result = compute_aggregate_cgt_revenue(self._make_population(), config)
        with pytest.raises(ValidationError, match="frozen"):
            result.total_revenue_bn = 0.0


class TestCGTResult:
    def test_round_trip(self):
        result = CGTResult(
            person_id="p1",
            gains_realised=50_000,
            gains_taxable=47_000,
            cgt_liability=11_280,
            effective_rate=0.2256,
            is_liable=True,
        )
        data = result.model_dump()
        r2 = CGTResult.model_validate(data)
        assert r2.person_id == "p1"
        assert r2.cgt_liability == 11_280

    def test_frozen(self):
        result = CGTResult(
            person_id="p1",
            gains_realised=50_000,
            gains_taxable=47_000,
            cgt_liability=11_280,
            effective_rate=0.2256,
            is_liable=True,
        )
        with pytest.raises(ValidationError, match="frozen"):
            result.cgt_liability = 0.0


class TestHouseholdCGTResultModel:
    def test_round_trip(self):
        result = HouseholdCGTResult(
            household_id="hh1",
            person_results=(
                CGTResult(
                    person_id="p1",
                    gains_realised=50_000,
                    gains_taxable=47_000,
                    cgt_liability=11_280,
                    effective_rate=0.2256,
                    is_liable=True,
                ),
            ),
            total_cgt_liability=11_280,
            is_liable=True,
        )
        data = result.model_dump()
        r2 = HouseholdCGTResult.model_validate(data)
        assert r2.household_id == "hh1"
        assert len(r2.person_results) == 1
