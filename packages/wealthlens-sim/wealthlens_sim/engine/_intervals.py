"""Interval propagation for engine revenue (Wave 12 PR3d).

v0.1 propagates a single dominant uncertainty — the top-tail Pareto exponent
``alpha`` — multiplicatively across every published revenue figure. Wealth-tax
revenue scales with the Pareto tail mean ``alpha / (alpha - 1)``, which is
*decreasing* in alpha: a heavier tail (lower alpha) concentrates more wealth at
the very top and raises more revenue. The alpha credible interval lives in the
assumption registry (``toptail.pareto_alpha.overall.v1``, sourced from Vermeulen
2018 calibrated to UK WAS + the Sunday Times Rich List), so the resulting revenue
intervals are cited and recorded in the provenance manifest.

Richer per-parameter propagation (each assumption ``RangeValue`` swept
independently, Monte-Carlo / Sobol) is deferred to Wave 13 (``uncertainty/``).
"""

from __future__ import annotations

from wealthlens_sim.assumptions.schema import AssumptionRegistry, RangeValue
from wealthlens_sim.top_tail.types import Interval

#: Registry assumption whose range drives v0.1 revenue uncertainty.
PARETO_ALPHA_ASSUMPTION_ID = "toptail.pareto_alpha.overall.v1"


def _tail_mean_factor(alpha: float) -> float:
    """Pareto tail-mean shape factor ``alpha / (alpha - 1)``.

    The threshold cancels when taking ratios, so only the alpha-dependent shape
    factor matters for relative scaling. Requires ``alpha > 1`` for a finite mean.
    """
    if alpha <= 1.0:
        msg = f"Pareto alpha must exceed 1 for a finite tail mean, got {alpha}"
        raise ValueError(msg)
    return alpha / (alpha - 1.0)


def revenue_scale_from_alpha(alpha: Interval) -> tuple[float, float]:
    """Return multiplicative ``(low, high)`` revenue factors from the alpha interval.

    Factors are relative to the central alpha (so the central factor is 1.0). Because
    the tail mean is monotonic in alpha and the central alpha lies between the bounds,
    ``low <= 1.0 <= high`` — i.e. scaling a positive central revenue yields a valid
    ``low <= central <= high`` interval. ``min``/``max`` make the result robust to a
    descending alpha range.
    """
    central = _tail_mean_factor(alpha.central)
    at_low = _tail_mean_factor(alpha.low)
    at_high = _tail_mean_factor(alpha.high)
    factor_low = min(at_low, at_high) / central
    factor_high = max(at_low, at_high) / central
    return factor_low, factor_high


def scaled_interval(central: float, scale_low: float, scale_high: float) -> Interval:
    """Build a revenue interval by scaling ``central`` by the ``(low, high)`` factors.

    ``min``/``max`` preserve the ``low <= central <= high`` ordering even when
    ``central`` is negative (e.g. an enforcement cost exceeding the uplift), where
    multiplying by the factors flips their order.
    """
    bound_a = central * scale_low
    bound_b = central * scale_high
    return Interval(low=min(bound_a, bound_b), central=central, high=max(bound_a, bound_b))


def alpha_interval_from_registry(registry: AssumptionRegistry) -> Interval | None:
    """Read the top-tail alpha credible interval from the assumption registry.

    Returns ``None`` only when the assumption is *absent* — the engine then falls
    back to degenerate intervals (uncertainty unquantified). A present-but-wrong-
    type assumption (e.g. someone changed the canonical alpha to a ``PointValue``)
    is a registry *defect*, so it is raised rather than silently downgraded — the
    caller asked for sourced intervals by naming the registry.
    """
    assumption = registry.get(PARETO_ALPHA_ASSUMPTION_ID)
    if assumption is None:
        return None
    distribution = assumption.value_or_distribution
    if not isinstance(distribution, RangeValue):
        msg = (
            f"{PARETO_ALPHA_ASSUMPTION_ID} must be a range to drive revenue intervals, "
            f"got {type(distribution).__name__}"
        )
        raise TypeError(msg)
    return Interval(low=distribution.low, central=distribution.central, high=distribution.high)
