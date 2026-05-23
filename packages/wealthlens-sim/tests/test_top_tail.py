"""Tests for the top-tail Pareto reconstruction module."""

from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from wealthlens_sim.top_tail import (
    BaselineVariant,
    Interval,
    ParetoFit,
    TailEstimate,
    VariantConfig,
    WealthShares,
    bootstrap_alpha,
    compute_wealth_shares,
    fit_pareto,
    fit_pareto_mle,
    ks_test_pareto,
    pareto_wealth_share,
    run_all_variants,
    run_variant,
)


def _make_pareto_sample(
    alpha: float = 1.5,
    threshold: float = 1_000_000,
    n: int = 500,
    seed: int = 42,
) -> np.ndarray:
    """Generate synthetic Pareto-distributed wealth data for testing."""
    rng = np.random.default_rng(seed)
    uniform = rng.uniform(0, 1, n)
    return threshold / uniform ** (1 / alpha)


class TestParetoMLE:
    def test_recovers_known_alpha(self):
        data = _make_pareto_sample(alpha=1.5, n=5000)
        alpha_hat = fit_pareto_mle(data, threshold=1_000_000)
        assert 1.4 < alpha_hat < 1.6

    def test_different_alpha(self):
        data = _make_pareto_sample(alpha=2.0, n=5000)
        alpha_hat = fit_pareto_mle(data, threshold=1_000_000)
        assert 1.9 < alpha_hat < 2.1

    def test_too_few_observations_raises(self):
        data = np.array([500_000.0])
        with pytest.raises(ValueError, match="at least 2"):
            fit_pareto_mle(data, threshold=1_000_000)

    def test_no_observations_above_threshold(self):
        data = np.array([100.0, 200.0, 300.0])
        with pytest.raises(ValueError, match="at least 2"):
            fit_pareto_mle(data, threshold=1_000_000)

    def test_exact_threshold_included(self):
        data = np.array([1_000_000.0, 2_000_000.0, 3_000_000.0])
        alpha = fit_pareto_mle(data, threshold=1_000_000)
        assert alpha > 0


class TestBootstrapAlpha:
    def test_interval_contains_true_alpha(self):
        data = _make_pareto_sample(alpha=1.5, n=2000)
        interval = bootstrap_alpha(
            data, threshold=1_000_000, n_bootstrap=500, ci=0.90, rng=np.random.default_rng(0)
        )
        assert interval.low <= 1.5 <= interval.high

    def test_central_near_mle(self):
        data = _make_pareto_sample(alpha=1.5, n=2000)
        rng = np.random.default_rng(0)
        interval = bootstrap_alpha(data, threshold=1_000_000, n_bootstrap=500, rng=rng)
        mle = fit_pareto_mle(data, threshold=1_000_000)
        assert abs(interval.central - mle) < 0.15

    def test_wider_ci_is_wider(self):
        data = _make_pareto_sample(alpha=1.5, n=500)
        rng1 = np.random.default_rng(0)
        narrow = bootstrap_alpha(data, threshold=1_000_000, ci=0.50, rng=rng1)
        rng2 = np.random.default_rng(0)
        wide = bootstrap_alpha(data, threshold=1_000_000, ci=0.95, rng=rng2)
        assert (wide.high - wide.low) >= (narrow.high - narrow.low)

    def test_too_few_raises(self):
        data = np.array([500_000.0])
        with pytest.raises(ValueError, match="at least 2"):
            bootstrap_alpha(data, threshold=1_000_000)


class TestKSTest:
    def test_good_fit_low_statistic(self):
        data = _make_pareto_sample(alpha=1.5, n=1000)
        ks = ks_test_pareto(data, threshold=1_000_000, alpha=1.5)
        assert ks < 0.1

    def test_bad_fit_high_statistic(self):
        rng = np.random.default_rng(42)
        data = rng.normal(5_000_000, 100_000, 1000)
        data = data[data >= 1_000_000]
        if len(data) >= 2:
            ks = ks_test_pareto(data, threshold=1_000_000, alpha=1.5)
            assert ks > 0.1

    def test_insufficient_data_returns_nan(self):
        data = np.array([500_000.0])
        ks = ks_test_pareto(data, threshold=1_000_000, alpha=1.5)
        assert np.isnan(ks)


class TestFitPareto:
    def test_returns_pareto_fit(self):
        data = _make_pareto_sample(alpha=1.5, n=1000)
        result = fit_pareto(data, threshold=1_000_000, n_bootstrap=200, rng=np.random.default_rng(0))
        assert isinstance(result, ParetoFit)
        assert result.threshold == 1_000_000
        assert result.n_tail == 1000
        assert result.ks_statistic is not None

    def test_alpha_interval_reasonable(self):
        data = _make_pareto_sample(alpha=1.5, n=2000)
        result = fit_pareto(data, threshold=1_000_000, n_bootstrap=500, rng=np.random.default_rng(0))
        assert result.alpha.low > 1.0
        assert result.alpha.high < 3.0
        assert result.alpha.low < result.alpha.central < result.alpha.high


class TestParetoWealthShare:
    def test_top_10_pct_alpha_1_5(self):
        share = pareto_wealth_share(1.5, 0.10)
        expected = 0.10 ** (1 - 1 / 1.5)
        assert abs(share - expected) < 1e-10

    def test_top_1_pct_alpha_2(self):
        share = pareto_wealth_share(2.0, 0.01)
        expected = 0.01 ** 0.5
        assert abs(share - expected) < 1e-10

    def test_higher_alpha_less_concentrated(self):
        share_low_alpha = pareto_wealth_share(1.3, 0.01)
        share_high_alpha = pareto_wealth_share(2.0, 0.01)
        assert share_low_alpha > share_high_alpha

    def test_alpha_le_1_raises(self):
        with pytest.raises(ValueError, match="must be > 1"):
            pareto_wealth_share(1.0, 0.01)

    def test_invalid_p_raises(self):
        with pytest.raises(ValueError, match="must be in"):
            pareto_wealth_share(1.5, 0.0)
        with pytest.raises(ValueError, match="must be in"):
            pareto_wealth_share(1.5, 1.0)


class TestComputeWealthShares:
    def test_returns_three_intervals(self):
        alpha = Interval(low=1.3, central=1.5, high=1.8)
        shares = compute_wealth_shares(alpha)
        assert "top_10_pct" in shares
        assert "top_1_pct" in shares
        assert "top_01_pct" in shares

    def test_intervals_monotonic(self):
        alpha = Interval(low=1.3, central=1.5, high=1.8)
        shares = compute_wealth_shares(alpha)
        for interval in shares.values():
            assert interval.low <= interval.central <= interval.high

    def test_top_10_gt_top_1_gt_top_01(self):
        alpha = Interval(low=1.3, central=1.5, high=1.8)
        shares = compute_wealth_shares(alpha)
        assert shares["top_10_pct"].central > shares["top_1_pct"].central
        assert shares["top_1_pct"].central > shares["top_01_pct"].central

    def test_lower_alpha_wider_interval(self):
        narrow = Interval(low=1.8, central=1.9, high=2.0)
        wide = Interval(low=1.2, central=1.5, high=1.8)
        shares_narrow = compute_wealth_shares(narrow)
        shares_wide = compute_wealth_shares(wide)
        width_narrow = shares_narrow["top_1_pct"].high - shares_narrow["top_1_pct"].low
        width_wide = shares_wide["top_1_pct"].high - shares_wide["top_1_pct"].low
        assert width_wide > width_narrow


class TestTypes:
    def test_baseline_variant_all_five(self):
        assert len(BaselineVariant) == 5

    def test_interval_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            Interval.model_validate({"low": 0, "central": 0.5, "high": 1, "extra": True})

    def test_pareto_fit_threshold_non_negative(self):
        with pytest.raises(ValidationError):
            ParetoFit.model_validate({
                "alpha": {"low": 1.3, "central": 1.5, "high": 1.8},
                "threshold": -100,
                "n_tail": 50,
            })

    def test_tail_estimate_round_trip(self):
        est = TailEstimate(
            variant=BaselineVariant.PARETO_CORRECTED,
            pareto_fit=ParetoFit(
                alpha=Interval(low=1.3, central=1.5, high=1.8),
                threshold=2_000_000,
                n_tail=150,
                ks_statistic=0.03,
            ),
            wealth_shares=WealthShares(
                top_10_pct=Interval(low=0.40, central=0.46, high=0.52),
                top_1_pct=Interval(low=0.18, central=0.22, high=0.26),
                top_01_pct=Interval(low=0.08, central=0.10, high=0.13),
            ),
            total_wealth_imputed=Interval(low=15_000, central=16_500, high=18_200),
        )
        data = est.model_dump()
        est2 = TailEstimate.model_validate(data)
        assert est2.variant == BaselineVariant.PARETO_CORRECTED
        assert est2.pareto_fit.n_tail == 150

    def test_wealth_shares_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            WealthShares.model_validate({
                "top_10_pct": {"low": 0, "central": 0.5, "high": 1},
                "top_1_pct": {"low": 0, "central": 0.2, "high": 0.4},
                "top_01_pct": {"low": 0, "central": 0.1, "high": 0.2},
                "top_50_pct": {"low": 0, "central": 0.9, "high": 1},
            })


class TestRunVariant:
    def test_pareto_corrected_variant(self):
        data = _make_pareto_sample(alpha=1.5, n=2000)
        config = VariantConfig(
            variant=BaselineVariant.PARETO_CORRECTED,
            threshold=1_000_000,
            n_bootstrap=200,
        )
        result = run_variant(data, config, rng=np.random.default_rng(0))
        assert result.variant == BaselineVariant.PARETO_CORRECTED
        assert result.wealth_shares.top_1_pct.central > 0
        assert result.total_wealth_imputed.central > 0

    def test_survey_only_variant(self):
        data = _make_pareto_sample(alpha=1.5, n=2000)
        config = VariantConfig(
            variant=BaselineVariant.SURVEY_ONLY,
            threshold=1_000_000,
            n_bootstrap=200,
        )
        result = run_variant(data, config, rng=np.random.default_rng(0))
        assert result.variant == BaselineVariant.SURVEY_ONLY

    def test_hidden_wealth_increases_total(self):
        data = _make_pareto_sample(alpha=1.5, n=2000)
        base_config = VariantConfig(
            variant=BaselineVariant.PARETO_CORRECTED,
            threshold=1_000_000,
            n_bootstrap=100,
        )
        hidden_config = VariantConfig(
            variant=BaselineVariant.HIDDEN_WEALTH_SENSITIVITY,
            threshold=1_000_000,
            n_bootstrap=100,
            offshore_ratio=0.15,
            trust_adjustment=0.10,
        )
        base = run_variant(data, base_config, rng=np.random.default_rng(0))
        hidden = run_variant(data, hidden_config, rng=np.random.default_rng(0))
        assert hidden.total_wealth_imputed.central > base.total_wealth_imputed.central

    def test_richlist_augmented_changes_alpha(self):
        data = _make_pareto_sample(alpha=1.5, n=2000)
        base_config = VariantConfig(
            variant=BaselineVariant.PARETO_CORRECTED,
            threshold=1_000_000,
            n_bootstrap=100,
        )
        rl_config = VariantConfig(
            variant=BaselineVariant.RICH_LIST_AUGMENTED,
            threshold=1_000_000,
            n_bootstrap=100,
            richlist_visibility=0.85,
        )
        base = run_variant(data, base_config, rng=np.random.default_rng(0))
        rl = run_variant(data, rl_config, rng=np.random.default_rng(0))
        assert base.pareto_fit.alpha.central != rl.pareto_fit.alpha.central


class TestRunAllVariants:
    def test_returns_all_five(self):
        data = _make_pareto_sample(alpha=1.5, n=2000, threshold=1_000_000)
        configs = {
            v: VariantConfig(variant=v, threshold=1_000_000, n_bootstrap=100)
            for v in BaselineVariant
        }
        configs[BaselineVariant.HIDDEN_WEALTH_SENSITIVITY] = VariantConfig(
            variant=BaselineVariant.HIDDEN_WEALTH_SENSITIVITY,
            threshold=1_000_000,
            n_bootstrap=100,
            offshore_ratio=0.15,
            trust_adjustment=0.10,
        )
        configs[BaselineVariant.RICH_LIST_AUGMENTED] = VariantConfig(
            variant=BaselineVariant.RICH_LIST_AUGMENTED,
            threshold=1_000_000,
            n_bootstrap=100,
            richlist_visibility=0.85,
        )
        results = run_all_variants(data, configs, seed=42)
        assert len(results) == 5
        for variant in BaselineVariant:
            assert variant in results
            assert isinstance(results[variant], TailEstimate)

    def test_reproducible_with_seed(self):
        data = _make_pareto_sample(alpha=1.5, n=1000, threshold=1_000_000)
        configs = {
            v: VariantConfig(variant=v, threshold=1_000_000, n_bootstrap=100)
            for v in BaselineVariant
        }
        r1 = run_all_variants(data, configs, seed=99)
        r2 = run_all_variants(data, configs, seed=99)
        for v in BaselineVariant:
            assert r1[v].pareto_fit.alpha.central == r2[v].pareto_fit.alpha.central
