"""Top-tail reconstruction of UK wealth distributions.

Methods: Vermeulen (2018) Pareto, Kennickell (2025) GPD-POT,
Wildauer-Kapeller (2022) rank correction, rich-list anchoring,
hidden-wealth sensitivity.

Reference: Blueprint v5 sections 2.3, 7.3.
"""

from wealthlens_sim.top_tail.pareto import (
    bootstrap_alpha,
    compute_wealth_shares,
    fit_pareto,
    fit_pareto_mle,
    ks_test_pareto,
    pareto_wealth_share,
)
from wealthlens_sim.top_tail.types import (
    BaselineVariant,
    Interval,
    ParetoFit,
    TailEstimate,
    WealthShares,
)

__all__ = [
    "BaselineVariant",
    "Interval",
    "ParetoFit",
    "TailEstimate",
    "WealthShares",
    "bootstrap_alpha",
    "compute_wealth_shares",
    "fit_pareto",
    "fit_pareto_mle",
    "ks_test_pareto",
    "pareto_wealth_share",
]
