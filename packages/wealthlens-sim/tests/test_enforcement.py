"""Tests for Family F enforcement/compliance gap module."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wealthlens_sim.reforms.f_enforcement import (
    AggregateEnforcementRevenue,
    ComplianceRate,
    EnforcementConfig,
    EnforcementResult,
    TaxFamily,
    compute_enforcement_uplift,
)


class TestTaxFamily:
    def test_all_values(self):
        assert TaxFamily.INCOME_TAX == "income_tax"
        assert TaxFamily.CGT == "cgt"
        assert TaxFamily.IHT == "iht"
        assert TaxFamily.VAT == "vat"
        assert TaxFamily.CORPORATION_TAX == "corporation_tax"
        assert TaxFamily.OTHER == "other"

    def test_is_str(self):
        assert isinstance(TaxFamily.INCOME_TAX, str)


class TestComplianceRate:
    def test_valid(self):
        cr = ComplianceRate(
            tax_family=TaxFamily.INCOME_TAX,
            baseline_rate=0.90,
            scenario_rate=0.95,
        )
        assert cr.tax_family == TaxFamily.INCOME_TAX
        assert cr.baseline_rate == 0.90
        assert cr.scenario_rate == 0.95

    def test_frozen(self):
        cr = ComplianceRate(
            tax_family=TaxFamily.CGT,
            baseline_rate=0.80,
            scenario_rate=0.90,
        )
        with pytest.raises(ValidationError, match="frozen"):
            cr.baseline_rate = 0.85

    def test_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            ComplianceRate(
                tax_family=TaxFamily.CGT,
                baseline_rate=0.80,
                scenario_rate=0.90,
                surprise="bad",
            )

    def test_scenario_below_baseline_rejected(self):
        with pytest.raises(ValidationError, match="must not be below"):
            ComplianceRate(
                tax_family=TaxFamily.INCOME_TAX,
                baseline_rate=0.95,
                scenario_rate=0.90,
            )

    def test_equal_rates_accepted(self):
        cr = ComplianceRate(
            tax_family=TaxFamily.INCOME_TAX,
            baseline_rate=0.95,
            scenario_rate=0.95,
        )
        assert cr.baseline_rate == cr.scenario_rate

    def test_zero_baseline_accepted(self):
        cr = ComplianceRate(
            tax_family=TaxFamily.OTHER,
            baseline_rate=0.0,
            scenario_rate=0.50,
        )
        assert cr.baseline_rate == 0.0

    def test_full_compliance_accepted(self):
        cr = ComplianceRate(
            tax_family=TaxFamily.VAT,
            baseline_rate=0.90,
            scenario_rate=1.0,
        )
        assert cr.scenario_rate == 1.0

    def test_rate_above_one_rejected(self):
        with pytest.raises(ValidationError):
            ComplianceRate(
                tax_family=TaxFamily.INCOME_TAX,
                baseline_rate=0.90,
                scenario_rate=1.01,
            )

    def test_negative_rate_rejected(self):
        with pytest.raises(ValidationError):
            ComplianceRate(
                tax_family=TaxFamily.INCOME_TAX,
                baseline_rate=-0.10,
                scenario_rate=0.90,
            )


class TestEnforcementConfig:
    def test_valid(self):
        config = EnforcementConfig(
            compliance_rates=(
                ComplianceRate(
                    tax_family=TaxFamily.INCOME_TAX,
                    baseline_rate=0.90,
                    scenario_rate=0.95,
                ),
            ),
        )
        assert len(config.compliance_rates) == 1
        assert config.enforcement_cost_bn == 0.0

    def test_frozen(self):
        config = EnforcementConfig(
            compliance_rates=(
                ComplianceRate(
                    tax_family=TaxFamily.INCOME_TAX,
                    baseline_rate=0.90,
                    scenario_rate=0.95,
                ),
            ),
        )
        with pytest.raises(ValidationError, match="frozen"):
            config.enforcement_cost_bn = 1.0

    def test_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            EnforcementConfig(
                compliance_rates=(
                    ComplianceRate(
                        tax_family=TaxFamily.INCOME_TAX,
                        baseline_rate=0.90,
                        scenario_rate=0.95,
                    ),
                ),
                surprise="bad",
            )

    def test_empty_compliance_rates_rejected(self):
        with pytest.raises(ValidationError):
            EnforcementConfig(compliance_rates=())

    def test_duplicate_families_rejected(self):
        with pytest.raises(ValidationError, match="unique"):
            EnforcementConfig(
                compliance_rates=(
                    ComplianceRate(
                        tax_family=TaxFamily.INCOME_TAX,
                        baseline_rate=0.90,
                        scenario_rate=0.95,
                    ),
                    ComplianceRate(
                        tax_family=TaxFamily.INCOME_TAX,
                        baseline_rate=0.85,
                        scenario_rate=0.92,
                    ),
                ),
            )

    def test_multiple_families(self):
        config = EnforcementConfig(
            compliance_rates=(
                ComplianceRate(
                    tax_family=TaxFamily.INCOME_TAX,
                    baseline_rate=0.90,
                    scenario_rate=0.95,
                ),
                ComplianceRate(
                    tax_family=TaxFamily.CGT,
                    baseline_rate=0.80,
                    scenario_rate=0.90,
                ),
            ),
            enforcement_cost_bn=0.5,
        )
        assert len(config.compliance_rates) == 2
        assert config.enforcement_cost_bn == 0.5

    def test_negative_cost_rejected(self):
        with pytest.raises(ValidationError):
            EnforcementConfig(
                compliance_rates=(
                    ComplianceRate(
                        tax_family=TaxFamily.INCOME_TAX,
                        baseline_rate=0.90,
                        scenario_rate=0.95,
                    ),
                ),
                enforcement_cost_bn=-1.0,
            )


class TestComputeEnforcementUplift:
    def _make_simple_config(self) -> EnforcementConfig:
        return EnforcementConfig(
            compliance_rates=(
                ComplianceRate(
                    tax_family=TaxFamily.INCOME_TAX,
                    baseline_rate=0.90,
                    scenario_rate=0.95,
                ),
            ),
        )

    def _make_multi_config(self) -> EnforcementConfig:
        return EnforcementConfig(
            compliance_rates=(
                ComplianceRate(
                    tax_family=TaxFamily.INCOME_TAX,
                    baseline_rate=0.90,
                    scenario_rate=0.95,
                ),
                ComplianceRate(
                    tax_family=TaxFamily.CGT,
                    baseline_rate=0.80,
                    scenario_rate=0.90,
                ),
                ComplianceRate(
                    tax_family=TaxFamily.IHT,
                    baseline_rate=0.85,
                    scenario_rate=0.92,
                ),
            ),
            enforcement_cost_bn=0.5,
        )

    def test_single_family_uplift(self):
        config = self._make_simple_config()
        theoretical = {TaxFamily.INCOME_TAX: 200.0}
        result = compute_enforcement_uplift(theoretical, config)

        assert result.total_uplift_bn == pytest.approx(200.0 * 0.05)
        assert result.net_uplift_bn == pytest.approx(10.0)
        assert result.enforcement_cost_bn == 0.0

    def test_multi_family_uplift(self):
        config = self._make_multi_config()
        theoretical = {
            TaxFamily.INCOME_TAX: 200.0,
            TaxFamily.CGT: 15.0,
            TaxFamily.IHT: 7.0,
        }
        result = compute_enforcement_uplift(theoretical, config)

        it_uplift = 200.0 * 0.05
        cgt_uplift = 15.0 * 0.10
        iht_uplift = 7.0 * 0.07
        expected_total = it_uplift + cgt_uplift + iht_uplift
        assert result.total_uplift_bn == pytest.approx(expected_total)
        assert result.net_uplift_bn == pytest.approx(expected_total - 0.5)

    def test_missing_theoretical_treated_as_zero(self):
        config = self._make_simple_config()
        result = compute_enforcement_uplift({}, config)

        assert result.total_uplift_bn == 0.0
        assert result.total_theoretical_bn == 0.0

    def test_negative_theoretical_floored(self):
        config = self._make_simple_config()
        theoretical = {TaxFamily.INCOME_TAX: -50.0}
        result = compute_enforcement_uplift(theoretical, config)

        assert result.total_uplift_bn == 0.0
        fr = result.family_results[0]
        assert fr.theoretical_revenue_bn == 0.0

    def test_zero_theoretical(self):
        config = self._make_simple_config()
        theoretical = {TaxFamily.INCOME_TAX: 0.0}
        result = compute_enforcement_uplift(theoretical, config)

        assert result.total_uplift_bn == 0.0

    def test_baseline_gap(self):
        config = self._make_simple_config()
        theoretical = {TaxFamily.INCOME_TAX: 100.0}
        result = compute_enforcement_uplift(theoretical, config)

        fr = result.family_results[0]
        assert fr.baseline_gap_bn == pytest.approx(100.0 * 0.10)

    def test_gap_closed_fraction(self):
        config = self._make_simple_config()
        theoretical = {TaxFamily.INCOME_TAX: 100.0}
        result = compute_enforcement_uplift(theoretical, config)

        fr = result.family_results[0]
        expected = (100 * 0.05) / (100 * 0.10)
        assert fr.gap_closed_fraction == pytest.approx(expected)

    def test_gap_closed_zero_gap(self):
        config = EnforcementConfig(
            compliance_rates=(
                ComplianceRate(
                    tax_family=TaxFamily.INCOME_TAX,
                    baseline_rate=1.0,
                    scenario_rate=1.0,
                ),
            ),
        )
        theoretical = {TaxFamily.INCOME_TAX: 100.0}
        result = compute_enforcement_uplift(theoretical, config)

        fr = result.family_results[0]
        assert fr.gap_closed_fraction == 0.0
        assert fr.baseline_gap_bn == 0.0

    def test_total_theoretical(self):
        config = self._make_multi_config()
        theoretical = {
            TaxFamily.INCOME_TAX: 200.0,
            TaxFamily.CGT: 15.0,
            TaxFamily.IHT: 7.0,
        }
        result = compute_enforcement_uplift(theoretical, config)
        assert result.total_theoretical_bn == pytest.approx(222.0)

    def test_total_baseline_gap(self):
        config = self._make_multi_config()
        theoretical = {
            TaxFamily.INCOME_TAX: 200.0,
            TaxFamily.CGT: 15.0,
            TaxFamily.IHT: 7.0,
        }
        result = compute_enforcement_uplift(theoretical, config)
        expected_gap = (200 * 0.10) + (15 * 0.20) + (7 * 0.15)
        assert result.total_baseline_gap_bn == pytest.approx(expected_gap)

    def test_enforcement_cost_subtracted(self):
        config = self._make_multi_config()
        theoretical = {
            TaxFamily.INCOME_TAX: 200.0,
            TaxFamily.CGT: 15.0,
            TaxFamily.IHT: 7.0,
        }
        result = compute_enforcement_uplift(theoretical, config)
        assert result.net_uplift_bn == pytest.approx(
            result.total_uplift_bn - 0.5,
        )

    def test_net_uplift_can_be_negative(self):
        config = EnforcementConfig(
            compliance_rates=(
                ComplianceRate(
                    tax_family=TaxFamily.INCOME_TAX,
                    baseline_rate=0.90,
                    scenario_rate=0.91,
                ),
            ),
            enforcement_cost_bn=5.0,
        )
        theoretical = {TaxFamily.INCOME_TAX: 100.0}
        result = compute_enforcement_uplift(theoretical, config)
        assert result.net_uplift_bn < 0

    def test_family_result_fields(self):
        config = self._make_simple_config()
        theoretical = {TaxFamily.INCOME_TAX: 100.0}
        result = compute_enforcement_uplift(theoretical, config)

        fr = result.family_results[0]
        assert fr.tax_family == TaxFamily.INCOME_TAX
        assert fr.theoretical_revenue_bn == 100.0
        assert fr.baseline_revenue_bn == pytest.approx(90.0)
        assert fr.scenario_revenue_bn == pytest.approx(95.0)
        assert fr.revenue_uplift_bn == pytest.approx(5.0)

    def test_family_results_count_matches_config(self):
        config = self._make_multi_config()
        theoretical = {
            TaxFamily.INCOME_TAX: 200.0,
            TaxFamily.CGT: 15.0,
            TaxFamily.IHT: 7.0,
        }
        result = compute_enforcement_uplift(theoretical, config)
        assert len(result.family_results) == 3

    def test_extra_theoretical_ignored(self):
        config = self._make_simple_config()
        theoretical = {
            TaxFamily.INCOME_TAX: 100.0,
            TaxFamily.VAT: 200.0,
        }
        result = compute_enforcement_uplift(theoretical, config)
        assert len(result.family_results) == 1
        assert result.total_theoretical_bn == 100.0

    def test_all_six_families(self):
        rates = {
            TaxFamily.INCOME_TAX: (0.90, 0.95),
            TaxFamily.CGT: (0.80, 0.88),
            TaxFamily.IHT: (0.85, 0.92),
            TaxFamily.VAT: (0.88, 0.93),
            TaxFamily.CORPORATION_TAX: (0.92, 0.96),
            TaxFamily.OTHER: (0.75, 0.85),
        }
        config = EnforcementConfig(
            compliance_rates=tuple(
                ComplianceRate(
                    tax_family=tf, baseline_rate=b, scenario_rate=s,
                )
                for tf, (b, s) in rates.items()
            ),
            enforcement_cost_bn=1.0,
        )
        theoretical = {tf: 50.0 for tf in TaxFamily}
        result = compute_enforcement_uplift(theoretical, config)

        assert len(result.family_results) == 6
        expected_uplift = sum(
            50.0 * (s - b) for b, s in rates.values()
        )
        assert result.total_uplift_bn == pytest.approx(expected_uplift)
        assert result.net_uplift_bn == pytest.approx(expected_uplift - 1.0)
        families_in_result = {fr.tax_family for fr in result.family_results}
        assert families_in_result == set(TaxFamily)


class TestEnforcementResult:
    def test_round_trip(self):
        result = EnforcementResult(
            tax_family=TaxFamily.INCOME_TAX,
            theoretical_revenue_bn=100.0,
            baseline_revenue_bn=90.0,
            scenario_revenue_bn=95.0,
            revenue_uplift_bn=5.0,
            baseline_gap_bn=10.0,
            gap_closed_fraction=0.5,
        )
        data = result.model_dump()
        r2 = EnforcementResult.model_validate(data)
        assert r2.tax_family == TaxFamily.INCOME_TAX
        assert r2.revenue_uplift_bn == 5.0

    def test_frozen(self):
        result = EnforcementResult(
            tax_family=TaxFamily.INCOME_TAX,
            theoretical_revenue_bn=100.0,
            baseline_revenue_bn=90.0,
            scenario_revenue_bn=95.0,
            revenue_uplift_bn=5.0,
            baseline_gap_bn=10.0,
            gap_closed_fraction=0.5,
        )
        with pytest.raises(ValidationError, match="frozen"):
            result.revenue_uplift_bn = 0.0


class TestAggregateEnforcementRevenue:
    def test_round_trip(self):
        result = AggregateEnforcementRevenue(
            family_results=(
                EnforcementResult(
                    tax_family=TaxFamily.INCOME_TAX,
                    theoretical_revenue_bn=100.0,
                    baseline_revenue_bn=90.0,
                    scenario_revenue_bn=95.0,
                    revenue_uplift_bn=5.0,
                    baseline_gap_bn=10.0,
                    gap_closed_fraction=0.5,
                ),
            ),
            total_uplift_bn=5.0,
            total_theoretical_bn=100.0,
            total_baseline_gap_bn=10.0,
            enforcement_cost_bn=0.5,
            net_uplift_bn=4.5,
        )
        data = result.model_dump()
        r2 = AggregateEnforcementRevenue.model_validate(data)
        assert r2.net_uplift_bn == 4.5
        assert len(r2.family_results) == 1

    def test_frozen(self):
        result = AggregateEnforcementRevenue(
            family_results=(),
            total_uplift_bn=0.0,
            total_theoretical_bn=0.0,
            total_baseline_gap_bn=0.0,
            enforcement_cost_bn=0.0,
            net_uplift_bn=0.0,
        )
        with pytest.raises(ValidationError, match="frozen"):
            result.net_uplift_bn = 1.0
