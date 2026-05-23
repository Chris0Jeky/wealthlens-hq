"""Five-variant top-tail estimation orchestrator.

Blueprint v5 section 2.3: all five baseline variants ship co-equally.
No silent favouring of any single variant.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from wealthlens_sim.top_tail.pareto import compute_wealth_shares, fit_pareto
from wealthlens_sim.top_tail.types import (
    BaselineVariant,
    Interval,
    TailEstimate,
    WealthShares,
)


@dataclass(frozen=True)
class VariantConfig:
    """Configuration for a single top-tail baseline variant."""

    variant: BaselineVariant
    threshold: float
    n_bootstrap: int = 1000
    ci: float = 0.90
    offshore_ratio: float = 0.0
    trust_adjustment: float = 0.0
    richlist_visibility: float = 1.0


DEFAULT_CONFIGS = {
    BaselineVariant.SURVEY_ONLY: VariantConfig(
        variant=BaselineVariant.SURVEY_ONLY,
        threshold=2_000_000,
        n_bootstrap=500,
    ),
    BaselineVariant.PARETO_CORRECTED: VariantConfig(
        variant=BaselineVariant.PARETO_CORRECTED,
        threshold=2_000_000,
    ),
    BaselineVariant.RICH_LIST_AUGMENTED: VariantConfig(
        variant=BaselineVariant.RICH_LIST_AUGMENTED,
        threshold=2_000_000,
        richlist_visibility=0.85,
    ),
    BaselineVariant.MACRO_RECONCILED: VariantConfig(
        variant=BaselineVariant.MACRO_RECONCILED,
        threshold=2_000_000,
    ),
    BaselineVariant.HIDDEN_WEALTH_SENSITIVITY: VariantConfig(
        variant=BaselineVariant.HIDDEN_WEALTH_SENSITIVITY,
        threshold=2_000_000,
        offshore_ratio=0.15,
        trust_adjustment=0.10,
    ),
}


def _apply_hidden_wealth(
    wealth: NDArray[np.floating],
    offshore_ratio: float,
    trust_adjustment: float,
) -> NDArray[np.floating]:
    """Add hidden-wealth stress-test adjustments."""
    adjustment = 1.0 + offshore_ratio + trust_adjustment
    return (wealth * adjustment).astype(wealth.dtype)


def _apply_richlist_visibility(
    wealth: NDArray[np.floating],
    threshold: float,
    visibility: float,
) -> NDArray[np.floating]:
    """Scale tail observations for rich-list visibility bias."""
    result = wealth.copy()
    tail_mask = result >= threshold
    result[tail_mask] = result[tail_mask] / visibility
    return result


def run_variant(
    wealth: NDArray[np.floating],
    config: VariantConfig,
    *,
    rng: np.random.Generator | None = None,
) -> TailEstimate:
    """Run a single top-tail variant and return its estimate."""
    adjusted = wealth.copy()

    if config.variant == BaselineVariant.HIDDEN_WEALTH_SENSITIVITY:
        adjusted = _apply_hidden_wealth(
            adjusted, config.offshore_ratio, config.trust_adjustment
        )
    elif config.variant == BaselineVariant.RICH_LIST_AUGMENTED:
        adjusted = _apply_richlist_visibility(
            adjusted, config.threshold, config.richlist_visibility
        )

    pareto_fit = fit_pareto(
        adjusted,
        config.threshold,
        n_bootstrap=config.n_bootstrap,
        ci=config.ci,
        rng=rng,
    )

    share_intervals = compute_wealth_shares(pareto_fit.alpha)
    wealth_shares = WealthShares(
        top_10_pct=share_intervals["top_10_pct"],
        top_1_pct=share_intervals["top_1_pct"],
        top_01_pct=share_intervals["top_01_pct"],
    )

    total = float(np.sum(adjusted))
    total_bn = total / 1e9
    alpha = pareto_fit.alpha
    spread = (alpha.high - alpha.low) / alpha.central if alpha.central > 0 else 0
    total_wealth = Interval(
        low=total_bn * (1 - spread / 2),
        central=total_bn,
        high=total_bn * (1 + spread / 2),
    )

    return TailEstimate(
        variant=config.variant,
        pareto_fit=pareto_fit,
        wealth_shares=wealth_shares,
        total_wealth_imputed=total_wealth,
    )


def run_all_variants(
    wealth: NDArray[np.floating],
    configs: dict[BaselineVariant, VariantConfig] | None = None,
    *,
    seed: int = 42,
) -> dict[BaselineVariant, TailEstimate]:
    """Run all five baseline variants and return results keyed by variant."""
    if configs is None:
        configs = DEFAULT_CONFIGS

    rng = np.random.default_rng(seed)
    results: dict[BaselineVariant, TailEstimate] = {}

    for variant in BaselineVariant:
        config = configs.get(variant)
        if config is None:
            config = DEFAULT_CONFIGS[variant]
        variant_rng = np.random.default_rng(rng.integers(0, 2**31))
        results[variant] = run_variant(wealth, config, rng=variant_rng)

    return results
