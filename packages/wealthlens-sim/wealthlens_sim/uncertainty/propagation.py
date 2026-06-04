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
returns a :class:`PropagationResult` (a median + quantile-band :class:`Interval`,
the per-draw outputs for downstream sensitivity analysis, and reproducible
provenance ids).

It is pure, deterministic (the draws are seeded and ``evaluate`` is the caller's),
and **engine-free** — a later PR supplies the engine ``evaluate`` (run the scenario
at each draw) to replace the single alpha band with full Monte-Carlo propagation,
default OFF. Keeping the propagation generic here lets it be reviewed in isolation
and preserves the "uncertainty package does not import the engine" invariant.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from wealthlens_sim.top_tail.types import Interval
from wealthlens_sim.uncertainty.sampling import ParameterSamples

__all__ = [
    "PropagationResult",
    "propagate",
]


@dataclass(frozen=True)
class PropagationResult:
    """Summary of an output distribution from Monte-Carlo propagation.

    ``interval`` is the cited output band: ``central`` is the *median* of the
    propagated outputs and ``low``/``high`` are the ``lower_quantile`` /
    ``upper_quantile`` percentiles, so ``low <= central <= high`` always holds.
    ``mean`` and ``std`` describe the same draws. ``outputs`` is the read-only
    per-draw output vector (row-aligned with the sample matrix) retained for later
    Sobol / sensitivity analysis. ``provenance_ids`` extends the sample block's ids
    with the centre/quantile choices so the band is auditable and reproducible.

    The output vector is copied and locked read-only in ``__post_init__`` so the
    summarised draw cannot be mutated after the fact — the same immutability
    contract :class:`ParameterSamples` enforces on its matrix.
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
) -> PropagationResult:
    """Propagate ``samples`` through ``evaluate`` and summarise the output band.

    ``evaluate`` is called once per joint draw with a ``{parameter_name: value}``
    mapping (exactly what :meth:`ParameterSamples.as_dicts` yields) and must return
    a finite scalar. The result's ``interval`` uses the sample median as the central
    estimate and the ``lower_quantile`` / ``upper_quantile`` percentiles (NumPy's
    linear interpolation) as the band; requiring
    ``0 <= lower_quantile <= 0.5 <= upper_quantile <= 1`` guarantees the median lies
    within the band so ``Interval``'s ``low <= central <= high`` invariant holds.

    Determinism: the draws are deterministic (seeded) and ``evaluate`` is the
    caller's, so the same ``samples`` + ``evaluate`` always yield the same result;
    no randomness is introduced here.

    Raises ``ValueError`` if the sample block is empty, the quantiles are out of the
    required order/range, or ``evaluate`` returns a non-finite value for any draw.
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

    low = float(np.quantile(outputs, lower_quantile))
    central = float(np.median(outputs))
    high = float(np.quantile(outputs, upper_quantile))

    provenance_ids = (
        *samples.provenance_ids(),
        "uncertainty.central:median",
        f"uncertainty.quantiles:{lower_quantile!r};{upper_quantile!r}",
    )
    return PropagationResult(
        interval=Interval(low=low, central=central, high=high),
        mean=float(np.mean(outputs)),
        std=float(np.std(outputs)),
        n_samples=samples.n_samples,
        outputs=outputs,
        provenance_ids=provenance_ids,
    )
