"""Pareto Type I fitting and wealth-share estimation.

Blueprint v5 section 7.3: fit upper-tail Pareto above configurable thresholds.
MLE: alpha_hat = n / sum(ln(w_i / w_min)) for observations w_i >= w_min.
Wealth share of top p fraction: S(p) = p^(1 - 1/alpha) for alpha > 1.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy import stats

from wealthlens_sim.top_tail.types import Interval, ParetoFit


def fit_pareto_mle(
    wealth: NDArray[np.floating],
    threshold: float,
) -> float:
    """Compute Pareto alpha via maximum likelihood on tail observations.

    Returns the MLE estimate of the Pareto tail exponent.
    Raises ValueError if fewer than 2 observations exceed the threshold,
    or if all tail values equal the threshold exactly.
    """
    tail = wealth[wealth >= threshold]
    n = len(tail)
    if n < 2:
        msg = f"Need at least 2 observations above threshold {threshold}, got {n}"
        raise ValueError(msg)
    log_sum = float(np.sum(np.log(tail / threshold)))
    if log_sum <= 0:
        msg = f"Log-ratio sum is {log_sum}; all tail values may equal the threshold"
        raise ValueError(msg)
    return float(n / log_sum)


def bootstrap_alpha(
    wealth: NDArray[np.floating],
    threshold: float,
    *,
    n_bootstrap: int = 1000,
    ci: float = 0.90,
    rng: np.random.Generator | None = None,
) -> Interval:
    """Bootstrap confidence interval for Pareto alpha.

    Resamples tail observations with replacement, refits alpha each time,
    and returns the median with ci-level credible interval.
    Degenerate samples (all values at threshold) are excluded from the CI.
    """
    if rng is None:
        rng = np.random.default_rng()

    tail = wealth[wealth >= threshold]
    n = len(tail)
    if n < 2:
        msg = f"Need at least 2 observations above threshold {threshold}, got {n}"
        raise ValueError(msg)

    alphas = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        sample = rng.choice(tail, size=n, replace=True)
        log_ratio_sum = float(np.sum(np.log(sample / threshold)))
        if log_ratio_sum > 0:
            alphas[i] = n / log_ratio_sum
        else:
            alphas[i] = np.inf

    valid_mask = np.isfinite(alphas) & (alphas > 1)
    alphas = alphas[valid_mask]
    if len(alphas) == 0:
        msg = "All bootstrap replicates produced degenerate alpha estimates"
        raise ValueError(msg)

    lo = (1 - ci) / 2
    hi = 1 - lo
    low_q, median, high_q = np.quantile(alphas, [lo, 0.5, hi])
    return Interval(low=float(low_q), central=float(median), high=float(high_q))


def ks_test_pareto(
    wealth: NDArray[np.floating],
    threshold: float,
    alpha: float,
) -> float:
    """Kolmogorov-Smirnov goodness-of-fit test for Pareto(threshold, alpha)."""
    tail = wealth[wealth >= threshold]
    if len(tail) < 2:
        return float("nan")
    normalised = tail / threshold
    result = stats.kstest(normalised, "pareto", args=(alpha,))
    return float(result.statistic)


def fit_pareto(
    wealth: NDArray[np.floating],
    threshold: float,
    *,
    n_bootstrap: int = 1000,
    ci: float = 0.90,
    rng: np.random.Generator | None = None,
) -> ParetoFit:
    """Full Pareto fit: MLE + bootstrap CI + KS test."""
    alpha_mle = fit_pareto_mle(wealth, threshold)
    alpha_interval = bootstrap_alpha(
        wealth, threshold, n_bootstrap=n_bootstrap, ci=ci, rng=rng
    )
    ks = ks_test_pareto(wealth, threshold, alpha_mle)
    tail_count = int(np.sum(wealth >= threshold))
    return ParetoFit(
        alpha=alpha_interval,
        threshold=threshold,
        n_tail=tail_count,
        ks_statistic=ks if not np.isnan(ks) else None,
    )


def pareto_wealth_share(alpha: float, p: float) -> float:
    """Wealth share held by top p fraction under Pareto(alpha).

    S(p) = p^(1 - 1/alpha) for alpha > 1.
    """
    if alpha <= 1:
        msg = f"Pareto alpha must be > 1 for finite wealth shares, got {alpha}"
        raise ValueError(msg)
    if not 0 < p < 1:
        msg = f"Population fraction p must be in (0, 1), got {p}"
        raise ValueError(msg)
    return float(p ** (1 - 1 / alpha))


def pareto_tail_mean(alpha: float, threshold: float) -> float:
    """Expected wealth per tail observation under Pareto(alpha, threshold).

    E[W | W >= threshold] = threshold * alpha / (alpha - 1) for alpha > 1.
    """
    if alpha <= 1:
        msg = f"Pareto alpha must be > 1 for finite mean, got {alpha}"
        raise ValueError(msg)
    return threshold * alpha / (alpha - 1)


def empirical_wealth_shares(
    wealth: NDArray[np.floating],
) -> dict[str, float]:
    """Compute top-10%, top-1%, top-0.1% shares from empirical data."""
    total = float(np.sum(wealth))
    if total <= 0:
        return {"top_10_pct": 0.0, "top_1_pct": 0.0, "top_01_pct": 0.0}
    sorted_w = np.sort(wealth)[::-1]
    n = len(sorted_w)
    result: dict[str, float] = {}
    for label, frac in [("top_10_pct", 0.10), ("top_1_pct", 0.01), ("top_01_pct", 0.001)]:
        k = max(1, int(np.ceil(n * frac)))
        result[label] = float(np.sum(sorted_w[:k]) / total)
    return result


def compute_wealth_shares(alpha: Interval) -> dict[str, Interval]:
    """Compute top-10%, top-1%, top-0.1% shares from alpha interval.

    Propagates uncertainty: low alpha -> higher concentration -> higher shares.
    """
    fractions = {"top_10_pct": 0.10, "top_1_pct": 0.01, "top_01_pct": 0.001}
    result: dict[str, Interval] = {}
    for label, p in fractions.items():
        shares = [pareto_wealth_share(a, p) for a in (alpha.low, alpha.central, alpha.high)]
        shares.sort()
        result[label] = Interval(
            low=shares[0],
            central=shares[1],
            high=shares[2],
        )
    return result
