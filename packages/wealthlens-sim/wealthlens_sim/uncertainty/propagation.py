"""Monte-Carlo propagation of a sampled parameter block (Wave 13 groundwork).

Blueprint v5 §8.1 (layer 7) and §10.1: published figures are intervals. Today the
engine derives its revenue band from a *single* multiplicative sweep of the
top-tail Pareto alpha (``engine/_intervals.py``). The next step is to draw many
uncertain parameters jointly (:mod:`~wealthlens_sim.uncertainty.sampling`) and
propagate them through the model, summarising the output distribution as a cited
interval.

This module is that **propagation layer** and nothing more. It consumes a
:class:`~wealthlens_sim.uncertainty.sampling.ParameterSamples` block and a
caller-supplied ``evaluate(params) -> float``, runs it once per joint draw, and
returns a :class:`PropagationResult` (a central + quantile-band :class:`Interval`,
where the centre defaults to the draw median but can be overridden with a point
estimate, the per-draw outputs for downstream sensitivity analysis, and
reproducible provenance ids).

It is pure, deterministic (the draws are seeded and ``evaluate`` is the caller's),
and **engine-free** — a later PR supplies the engine ``evaluate`` (run the scenario
at each draw) to replace the single alpha band with full Monte-Carlo propagation,
default OFF. Keeping the propagation generic here lets it be reviewed in isolation
and preserves the "uncertainty package does not import the engine" invariant.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from wealthlens_sim.top_tail.types import Interval
from wealthlens_sim.uncertainty.sampling import ParameterSamples, _format_float

__all__ = [
    "PropagationResult",
    "propagate",
]


@dataclass(frozen=True, kw_only=True)
class PropagationResult:
    """Summary of an output distribution from Monte-Carlo propagation.

    ``interval`` is the cited output band: ``central`` defaults to the *median* of
    the propagated outputs (``np.quantile(., 0.5)``) but can be overridden by the
    caller with a point estimate; ``low``/``high`` are the ``lower_quantile`` /
    ``upper_quantile`` percentiles, so ``low <= central <= high`` always holds.
    ``mean`` and ``std`` describe the same draws; ``std`` is the *population*
    standard deviation (``np.std`` default ``ddof=0``). ``outputs`` is the read-only
    per-draw output vector (row-aligned with the sample matrix) retained for later
    Sobol / sensitivity analysis. ``provenance_ids`` extends the sample block's ids
    with the centre/quantile choices so the band is auditable and reproducible.

    Construction is keyword-only and the output vector is copied and locked
    read-only in ``__post_init__`` so the summarised draw cannot be mutated after the
    fact — the same immutability contract :class:`ParameterSamples` enforces on its
    matrix.
    """

    interval: Interval
    mean: float
    std: float
    n_samples: int
    outputs: NDArray[np.float64]
    provenance_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        owned = self.outputs.copy()
        owned.flags.writeable = False
        object.__setattr__(self, "outputs", owned)


def propagate(
    samples: ParameterSamples,
    evaluate: Callable[[Mapping[str, float]], float],
    *,
    lower_quantile: float = 0.05,
    upper_quantile: float = 0.95,
    central: float | None = None,
) -> PropagationResult:
    """Propagate ``samples`` through ``evaluate`` and summarise the output band.

    ``evaluate`` is called once per joint draw with a ``{parameter_name: value}``
    mapping (exactly what :meth:`ParameterSamples.as_dicts` yields) and must return
    a finite scalar. The result's ``interval`` band is the ``lower_quantile`` /
    ``upper_quantile`` percentiles (NumPy's linear interpolation).

    By default ``interval.central`` is the *median of the draws*
    (``np.quantile(outputs, 0.5)`` — derived from the same primitive as the band so
    ``low <= central <= high`` holds exactly for any
    ``0 <= lower_quantile <= 0.5 <= upper_quantile <= 1``). Pass ``central`` to
    override it with a *point estimate* — e.g. the engine evaluates the scenario at
    the central parameter values and wants the headline figure to be that, not the
    draw median (the existing ``engine/_intervals.py`` centre semantics). An explicit
    ``central`` must be finite and lie within the ``[low, high]`` band.

    Determinism: the draws are deterministic (seeded) and ``evaluate`` is the
    caller's, so the same ``samples`` + ``evaluate`` always yield the same result;
    no randomness is introduced here.

    Raises ``ValueError`` if the sample block is empty, the quantiles are out of the
    required order/range, ``evaluate`` returns a non-finite value for any draw, the
    summary statistics overflow to non-finite, or an explicit ``central`` is
    non-finite or outside the band.
    """
    if not (0.0 <= lower_quantile <= 0.5 <= upper_quantile <= 1.0):
        msg = (
            "require 0 <= lower_quantile <= 0.5 <= upper_quantile <= 1, got "
            f"({lower_quantile}, {upper_quantile})"
        )
        raise ValueError(msg)
    if samples.n_samples == 0:
        msg = "cannot propagate an empty sample block"
        raise ValueError(msg)

    outputs = np.fromiter(
        (evaluate(row) for row in samples.as_dicts()),
        dtype=np.float64,
        count=samples.n_samples,
    )
    if not bool(np.all(np.isfinite(outputs))):
        msg = "evaluate returned a non-finite value for at least one draw"
        raise ValueError(msg)

    # One np.quantile call (a single partition/sort) for all three bounds. Because
    # they come from the same sorted data and lower_quantile <= 0.5 <= upper_quantile,
    # low <= band_central <= high holds exactly — the band can never trip Interval.
    low, band_central, high = (
        float(v) for v in np.quantile(outputs, [lower_quantile, 0.5, upper_quantile])
    )

    if central is None:
        centre = band_central
        central_tag = "uncertainty.central:median"
    else:
        centre = float(central)
        if not math.isfinite(centre):
            msg = f"explicit central must be finite, got {central}"
            raise ValueError(msg)
        if not (low <= centre <= high):
            msg = f"explicit central {centre} must lie within the [{low}, {high}] quantile band"
            raise ValueError(msg)
        central_tag = f"uncertainty.central:explicit:{_format_float(centre)}"

    # Every individual output is finite, but huge-but-finite values can overflow the
    # squared-deviation sum. Suppress the numpy warning (we detect and fail loud on
    # the non-finite result below) rather than publish a non-finite std.
    with np.errstate(over="ignore", invalid="ignore"):
        mean = float(np.mean(outputs))
        std = float(np.std(outputs))
    if not (math.isfinite(mean) and math.isfinite(std)):
        msg = "propagated outputs overflow the summary statistics (mean/std non-finite); evaluate outputs are out of a usable numeric range"
        raise ValueError(msg)

    provenance_ids = (
        *samples.provenance_ids(),
        central_tag,
        f"uncertainty.quantiles:{_format_float(lower_quantile)};{_format_float(upper_quantile)}",
    )
    return PropagationResult(
        interval=Interval(low=low, central=centre, high=high),
        mean=mean,
        std=std,
        n_samples=samples.n_samples,
        outputs=outputs,
        provenance_ids=provenance_ids,
    )
