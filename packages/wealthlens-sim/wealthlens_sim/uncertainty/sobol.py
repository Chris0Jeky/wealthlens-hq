"""Variance-based global sensitivity analysis — Sobol indices (Wave 13 groundwork).

Blueprint v5 §8.1 (layer 7) calls for *Sobol sensitivity analysis* alongside the
Monte-Carlo band: once a published figure carries uncertainty from several inputs,
the honest follow-up question is *which* inputs drive it. Sobol indices answer that
by decomposing the output variance into the contribution of each input.

This module is the **sensitivity layer** and nothing more. It is pure,
deterministic (seeded), dependency-free beyond NumPy, and — like
:mod:`~wealthlens_sim.uncertainty.sampling` and
:mod:`~wealthlens_sim.uncertainty.propagation` — **standalone**: it consumes the
same :class:`~wealthlens_sim.uncertainty.sampling.ParameterSpec` marginals and a
caller-supplied ``evaluate(params) -> float``, and is not wired into the engine. A
later PR can run Sobol over the engine ``evaluate`` to report which assumptions
dominate a revenue band.

What it computes
----------------
For ``d`` inputs it returns two indices per input:

* **First-order** ``S_i`` — the fraction of output variance explained by input *i*
  *on its own* (its main effect, averaging over all other inputs).
* **Total-order** ``S_Ti`` — the fraction explained by input *i* *including every
  interaction* it participates in. ``S_Ti >= S_i`` always; ``S_Ti - S_i`` measures
  how much of *i*'s influence is through interactions.

Method (no SALib dependency)
----------------------------
Standard **Saltelli sampling**: draw two independent base sample matrices ``A`` and
``B`` (``n_base`` rows each), then for every input *i* form ``AB_i`` = ``A`` with
its *i*-th column replaced by ``B``'s. Evaluating the model on ``A``, ``B`` and the
``d`` cross matrices costs ``n_base * (d + 2)`` runs. The indices use the
recommended estimators:

* First-order (Saltelli et al. 2010, Table 2):
  ``V_i = mean( f(B) * (f(AB_i) - f(A)) )`` and ``S_i = V_i / Var(Y)``.
* Total-order (Jansen 1999):
  ``E_i = mean( (f(A) - f(AB_i))^2 ) / 2`` and ``S_Ti = E_i / Var(Y)``.

``Var(Y)`` is the population variance of the pooled base outputs ``[f(A), f(B)]``.
The base matrices are independent halves of one ``n_base x 2d`` draw, so ``A`` and
``B`` are genuinely independent (required by the estimators). Estimates carry
Monte-Carlo noise, so a small negative ``S_i`` or an ``S_Ti`` slightly above 1 at
low ``n_base`` is expected and reported as-is (not clamped) — clamping would hide a
too-small sample.

Reference: Saltelli et al. (2010) *Comput. Phys. Commun.* 181:259-270; Jansen (1999).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from wealthlens_sim.uncertainty.sampling import (
    ParameterSpec,
    _format_float,
    _map_unit_column,
)

__all__ = [
    "SobolResult",
    "sobol_indices",
]

#: Default base sample size. Total model evaluations are ``n_base * (d + 2)``.
#: A power of two is conventional for Saltelli sampling; 1024 is a reasonable
#: default for smooth models (raise it for noisy estimates).
DEFAULT_N_BASE = 1024

#: Hard floor on ``n_base``. Saltelli indices are an average over ``n_base`` rows;
#: below this the estimate is noise, not signal — and at ``n_base == 1`` it is
#: structurally meaningless (a single pair) yet the zero-variance guard cannot fire
#: (a 2-point pool has non-zero variance). Reject the degenerate regime loudly
#: rather than return confident-looking garbage. This is a sanity floor, NOT a
#: sufficiency guarantee: a usable estimate typically needs hundreds-plus.
MIN_N_BASE = 8


@dataclass(frozen=True, kw_only=True)
class SobolResult:
    """First- and total-order Sobol indices for each input.

    ``names`` is the sorted input order; ``first_order`` and ``total_order`` align
    column-for-column with it. ``total_variance`` is the pooled-base output variance
    the indices are normalised by (indices are undefined if it is zero, which
    :func:`sobol_indices` rejects). ``n_base`` is the base sample size and
    ``n_evaluations == n_base * (len(names) + 2)`` is the total model-run count.
    ``provenance_ids`` records the method, estimators, sample size, seed and the
    full marginal of every input, so the analysis is reproducible from the trail.

    Construction is keyword-only and the index tuples are plain Python floats, so
    the result is an immutable, JSON-friendly summary.
    """

    names: tuple[str, ...]
    first_order: tuple[float, ...]
    total_order: tuple[float, ...]
    total_variance: float
    n_base: int
    n_evaluations: int
    seed: int
    provenance_ids: tuple[str, ...]

    def first_order_by_name(self) -> dict[str, float]:
        """``{input_name: S_i}`` first-order indices."""
        return dict(zip(self.names, self.first_order, strict=True))

    def total_order_by_name(self) -> dict[str, float]:
        """``{input_name: S_Ti}`` total-order indices."""
        return dict(zip(self.names, self.total_order, strict=True))


def _evaluate_matrix(
    matrix: NDArray[np.float64],
    names: tuple[str, ...],
    evaluate: Callable[[Mapping[str, float]], float],
) -> NDArray[np.float64]:
    """Evaluate ``evaluate`` over each row of ``matrix`` (a ``{name: value}`` map).

    Returns a 1-D float array row-aligned with ``matrix``. Raises ``ValueError`` if
    ``evaluate`` returns a non-finite value for any row (a silent NaN would corrupt
    every downstream index).

    ``matrix.tolist()`` is materialised once so each row is a list of native Python
    floats — iterating the 2-D array directly would build a fresh 1-D view per row
    and hand ``evaluate`` ``np.float64`` scalars, both slower over the ``n_base*(d+2)``
    rows this is called for.
    """
    outputs = np.fromiter(
        (evaluate(dict(zip(names, row, strict=True))) for row in matrix.tolist()),
        dtype=np.float64,
        count=matrix.shape[0],
    )
    if not bool(np.all(np.isfinite(outputs))):
        msg = "evaluate returned a non-finite value for at least one sample"
        raise ValueError(msg)
    return outputs


def sobol_indices(
    specs: Sequence[ParameterSpec],
    evaluate: Callable[[Mapping[str, float]], float],
    *,
    n_base: int = DEFAULT_N_BASE,
    seed: int = 0,
) -> SobolResult:
    """Estimate first- and total-order Sobol indices for ``evaluate`` over ``specs``.

    ``evaluate`` is called once per Saltelli sample with a ``{parameter_name: value}``
    mapping (exactly what the propagation layer expects) and must return a finite
    scalar. Inputs are processed in sorted ``name`` order, so the result is
    independent of the order ``specs`` are supplied in, and the same ``specs`` +
    ``n_base`` + ``seed`` always yield identical indices (seeded RNG).

    Total model evaluations: ``n_base * (len(specs) + 2)``.

    Raises ``ValueError`` if ``specs`` is empty or has duplicate names, ``n_base`` is
    below :data:`MIN_N_BASE` (a single base row makes the estimate meaningless yet
    cannot trip the zero-variance guard), ``evaluate`` returns a non-finite value, or
    the output has zero (or non-finite) variance — in which case the indices are
    mathematically undefined rather than silently returned as NaN/inf.
    """
    if n_base < MIN_N_BASE:
        msg = f"n_base must be >= {MIN_N_BASE} for a usable Saltelli estimate, got {n_base}"
        raise ValueError(msg)
    if not specs:
        msg = "sobol_indices requires at least one ParameterSpec"
        raise ValueError(msg)

    ordered = sorted(specs, key=lambda s: s.name)
    names = tuple(s.name for s in ordered)
    if len(set(names)) != len(names):
        msg = f"duplicate parameter names in specs: {names}"
        raise ValueError(msg)
    d = len(ordered)

    # One n_base x 2d unit draw, split into independent halves A and B — the
    # independence the Saltelli estimators require comes for free from disjoint
    # columns of a single draw.
    rng = np.random.default_rng(seed)
    unit = rng.random(size=(n_base, 2 * d))
    a_unit = unit[:, :d]
    b_unit = unit[:, d:]

    # Map each input column to its marginal once, then assemble A, B, and the d
    # cross matrices AB_i (A with column i taken from B).
    a_mat = np.empty((n_base, d), dtype=np.float64)
    b_mat = np.empty((n_base, d), dtype=np.float64)
    for j, spec in enumerate(ordered):
        a_mat[:, j] = _map_unit_column(a_unit[:, j], spec)
        b_mat[:, j] = _map_unit_column(b_unit[:, j], spec)

    f_a = _evaluate_matrix(a_mat, names, evaluate)
    f_b = _evaluate_matrix(b_mat, names, evaluate)

    # Total variance from the pooled base outputs (2 * n_base independent samples).
    # Suppress the overflow warning and fail loud on a non-finite result instead of
    # publishing nonsense indices (mirrors the propagation layer).
    with np.errstate(over="ignore", invalid="ignore"):
        total_variance = float(np.var(np.concatenate([f_a, f_b])))
    if not math.isfinite(total_variance):
        msg = "pooled output variance is non-finite; evaluate outputs are out of a usable numeric range"
        raise ValueError(msg)
    if total_variance <= 0.0:
        msg = "output has zero variance across the sample; Sobol indices are undefined (the model is constant over these inputs)"
        raise ValueError(msg)

    first_order: list[float] = []
    total_order: list[float] = []
    for i in range(d):
        # AB_i = A with column i taken from B. Swap that one column in place and
        # restore it afterwards rather than copying the whole (n_base x d) matrix
        # d times — only the n_base-length column is duplicated per input.
        original_col = a_mat[:, i].copy()
        a_mat[:, i] = b_mat[:, i]
        f_ab_i = _evaluate_matrix(a_mat, names, evaluate)
        a_mat[:, i] = original_col
        with np.errstate(over="ignore", invalid="ignore"):
            # Saltelli et al. (2010): V_i = mean(f_B * (f_AB_i - f_A)).
            v_i = float(np.mean(f_b * (f_ab_i - f_a)))
            # Jansen (1999): E_i = mean((f_A - f_AB_i)^2) / 2.
            e_i = float(np.mean((f_a - f_ab_i) ** 2) / 2.0)
        if not (math.isfinite(v_i) and math.isfinite(e_i)):
            msg = f"sensitivity numerator for input {names[i]!r} is non-finite; evaluate outputs overflow"
            raise ValueError(msg)
        first_order.append(v_i / total_variance)
        total_order.append(e_i / total_variance)

    n_evaluations = n_base * (d + 2)
    provenance_ids = (
        "uncertainty.sobol.method:saltelli",
        "uncertainty.sobol.estimators:saltelli2010_first;jansen1999_total",
        f"uncertainty.sobol.n_base:{n_base}",
        f"uncertainty.sobol.n_evaluations:{n_evaluations}",
        f"uncertainty.sobol.seed:{seed}",
        f"uncertainty.sobol.parameters:{';'.join(names)}",
        f"uncertainty.sobol.total_variance:{_format_float(total_variance)}",
        f"uncertainty.sobol.specs:{';'.join(spec.provenance_tag() for spec in ordered)}",
    )
    return SobolResult(
        names=names,
        first_order=tuple(first_order),
        total_order=tuple(total_order),
        total_variance=total_variance,
        n_base=n_base,
        n_evaluations=n_evaluations,
        seed=seed,
        provenance_ids=provenance_ids,
    )
