"""Parameter sampling for Monte-Carlo uncertainty propagation (Wave 13 groundwork).

Blueprint v5 §8.1 (layer 7) and §10.1: published figures are intervals, never
naked point estimates. Today the engine derives its revenue band from a *single*
multiplicative sweep of the top-tail Pareto alpha (``engine/_intervals.py``). The
next step is to sample *many* uncertain parameters jointly and propagate them
through the engine — Monte-Carlo, then Sobol sensitivity on top of the same draws.

This module is the **sampling layer** for that work and nothing more. It is pure,
deterministic (seeded), dependency-free beyond NumPy (already a dependency), and
**not yet wired into the engine** — a later PR consumes :class:`ParameterSamples`
to run the scenario ``n_samples`` times. Keeping it standalone makes it reviewable
in isolation and keeps the default engine behaviour unchanged (feature OFF).

Design notes
------------
* Two draw methods: plain ``INDEPENDENT`` Monte-Carlo and ``LATIN_HYPERCUBE``
  (LHS), which stratifies each parameter into ``n`` equal-probability bins so the
  marginal space is covered evenly with far fewer samples — the standard choice
  for expensive simulators.
* Two marginal distributions: ``UNIFORM`` over ``[low, high]`` and ``TRIANGULAR``
  with mode ``central`` (the natural fit for the project's existing low/central/
  high :class:`~wealthlens_sim.top_tail.types.Interval` /
  :class:`~wealthlens_sim.assumptions.schema.RangeValue` triples).
* Parameters are always drawn in **sorted name order**, so the sample matrix is
  independent of the order specs are supplied in — the same canonicalisation
  discipline the synth provenance work adopted. Reordering the specs cannot change
  a single drawn value.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from enum import StrEnum

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.assumptions.schema import RangeValue
from wealthlens_sim.top_tail.types import Interval

__all__ = [
    "Distribution",
    "ParameterSamples",
    "ParameterSpec",
    "SamplingConfig",
    "SamplingMethod",
    "sample_parameters",
]


class SamplingMethod(StrEnum):
    """How the unit hypercube is filled before mapping to each marginal."""

    INDEPENDENT = "independent"
    LATIN_HYPERCUBE = "latin_hypercube"


class Distribution(StrEnum):
    """Marginal distribution for a single uncertain parameter."""

    UNIFORM = "uniform"
    TRIANGULAR = "triangular"


class ParameterSpec(BaseModel):
    """One uncertain parameter and the marginal to draw it from.

    ``low``/``central``/``high`` mirror the project's existing interval triples.
    Only ascending ranges are accepted here (``low <= central <= high``): a
    sampled *input* parameter must have a well-defined density, unlike a
    :class:`RangeValue` elasticity that may run negative. A degenerate spec
    (``low == central == high``) is allowed and yields that constant for every
    sample, which is how a known-exactly parameter participates without widening
    the band.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1, description="Stable parameter identifier (used to address sample columns)")
    low: float
    central: float
    high: float
    distribution: Distribution = Field(
        default=Distribution.TRIANGULAR,
        description="Marginal to draw from; TRIANGULAR uses ``central`` as the mode",
    )
    source_id: str | None = Field(
        default=None,
        description="Optional source/assumption-registry id, so a sampled run stays traceable to its evidence",
    )

    @model_validator(mode="after")
    def _ascending(self) -> ParameterSpec:
        if not (self.low <= self.central <= self.high):
            msg = f"ParameterSpec {self.name!r} must satisfy low <= central <= high, got ({self.low}, {self.central}, {self.high})"
            raise ValueError(msg)
        return self

    @classmethod
    def from_interval(
        cls,
        name: str,
        interval: Interval,
        *,
        distribution: Distribution = Distribution.TRIANGULAR,
        source_id: str | None = None,
    ) -> ParameterSpec:
        """Build a spec from an engine :class:`Interval` (low <= central <= high)."""
        return cls(
            name=name,
            low=interval.low,
            central=interval.central,
            high=interval.high,
            distribution=distribution,
            source_id=source_id,
        )

    @classmethod
    def from_range_value(
        cls,
        name: str,
        value: RangeValue,
        *,
        distribution: Distribution = Distribution.TRIANGULAR,
        source_id: str | None = None,
    ) -> ParameterSpec:
        """Build a spec from an assumption-registry :class:`RangeValue`.

        ``RangeValue`` permits descending (negative-elasticity) ranges; sampling
        needs an ascending density, so the bounds are normalised to
        ``low = min, high = max`` while ``central`` is preserved.
        """
        low, high = sorted((float(value.low), float(value.high)))
        return cls(
            name=name,
            low=low,
            central=float(value.central),
            high=high,
            distribution=distribution,
            source_id=source_id,
        )


class SamplingConfig(BaseModel):
    """Controls the size, reproducibility, and method of a sampling run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    n_samples: int = Field(gt=0, default=1024, description="Number of joint parameter draws to produce")
    seed: int = Field(ge=0, default=0, description="RNG seed; the same config + specs always yields identical samples")
    method: SamplingMethod = Field(
        default=SamplingMethod.LATIN_HYPERCUBE,
        description="INDEPENDENT Monte-Carlo or stratified LATIN_HYPERCUBE",
    )


@dataclass(frozen=True)
class ParameterSamples:
    """An immutable ``n_samples x n_parameters`` block of drawn values.

    ``names`` is sorted and aligns column-for-column with ``matrix``. A NumPy
    array (not a Pydantic field) because this is a numeric workspace handed to the
    engine, not a serialised contract. ``matrix`` is set read-only at construction
    so the deterministic draw cannot be mutated in place; ``column`` returns a
    read-only view of it.
    """

    names: tuple[str, ...]
    matrix: NDArray[np.float64]

    @property
    def n_samples(self) -> int:
        """Number of joint draws (rows)."""
        return int(self.matrix.shape[0])

    def column(self, name: str) -> NDArray[np.float64]:
        """Return the 1-D array of draws for parameter ``name``."""
        try:
            idx = self.names.index(name)
        except ValueError as exc:  # pragma: no cover - guard for caller typos
            msg = f"unknown parameter {name!r}; known parameters: {list(self.names)}"
            raise KeyError(msg) from exc
        return self.matrix[:, idx]

    def as_dicts(self) -> Iterator[dict[str, float]]:
        """Iterate each joint draw as a ``{parameter_name: value}`` mapping."""
        for row in self.matrix:
            yield {name: float(value) for name, value in zip(self.names, row, strict=True)}

    def provenance_ids(self) -> list[str]:
        """Stable tags describing this sampling run, for the provenance trail.

        Tags use a structured ``uncertainty.<key>:<value>`` grammar (the same
        ``namespace.key:value`` shape the synth generation-parameter tags use) so
        a Monte-Carlo run is as auditable as a single-point run. A later
        engine-wiring PR can fold these into the provenance trail alongside the
        population's source ids.
        """
        return [
            f"uncertainty.n_samples:{self.n_samples}",
            f"uncertainty.parameters:{';'.join(self.names)}",
        ]


def _unit_samples(rng: np.random.Generator, n: int, n_params: int, method: SamplingMethod) -> NDArray[np.float64]:
    """Fill an ``n x n_params`` array of independent unit ``[0, 1)`` draws.

    For ``LATIN_HYPERCUBE`` each column is stratified into ``n`` equal bins with
    one sample per bin (a fresh random permutation per parameter), so the marginal
    coverage is even while the columns stay independent.
    """
    if method is SamplingMethod.INDEPENDENT:
        return rng.random(size=(n, n_params))

    # Latin hypercube: stratified per column.
    out = np.empty((n, n_params), dtype=np.float64)
    strata = np.arange(n, dtype=np.float64)
    for j in range(n_params):
        jitter = rng.random(size=n)
        permutation = rng.permutation(n)
        out[:, j] = (strata[permutation] + jitter) / n
    return out


def _to_uniform(u: NDArray[np.float64], low: float, high: float) -> NDArray[np.float64]:
    return low + u * (high - low)


def _to_triangular(u: NDArray[np.float64], low: float, central: float, high: float) -> NDArray[np.float64]:
    """Inverse-CDF transform of unit draws ``u`` to Triangular(low, central, high)."""
    span = high - low
    if span == 0:  # degenerate spec: constant
        return np.full_like(u, low)
    # Cumulative probability at the mode.
    f_mode = (central - low) / span
    out = np.empty_like(u)
    lower = u < f_mode
    upper = ~lower
    # Left branch: x = low + sqrt(u * span * (central - low)).
    out[lower] = low + np.sqrt(u[lower] * span * (central - low))
    # Right branch: x = high - sqrt((1 - u) * span * (high - central)).
    out[upper] = high - np.sqrt((1.0 - u[upper]) * span * (high - central))
    return out


def sample_parameters(specs: Sequence[ParameterSpec], config: SamplingConfig | None = None) -> ParameterSamples:
    """Draw ``config.n_samples`` joint samples of ``specs``.

    Parameters are processed in sorted ``name`` order so the result is independent
    of the order ``specs`` are supplied in. The same ``config`` and ``specs``
    always produce an identical matrix (seeded RNG). Every drawn value lies within
    its spec's ``[low, high]`` bounds by construction.

    Raises ``ValueError`` if ``specs`` is empty or contains duplicate names.
    """
    if config is None:
        config = SamplingConfig()
    if not specs:
        msg = "sample_parameters requires at least one ParameterSpec"
        raise ValueError(msg)

    ordered = sorted(specs, key=lambda s: s.name)
    names = tuple(s.name for s in ordered)
    if len(set(names)) != len(names):
        msg = f"duplicate parameter names in specs: {names}"
        raise ValueError(msg)

    rng = np.random.default_rng(config.seed)
    unit = _unit_samples(rng, config.n_samples, len(ordered), config.method)

    matrix = np.empty_like(unit)
    for j, spec in enumerate(ordered):
        col = unit[:, j]
        if spec.distribution is Distribution.UNIFORM:
            matrix[:, j] = _to_uniform(col, spec.low, spec.high)
        else:
            matrix[:, j] = _to_triangular(col, spec.low, spec.central, spec.high)

    # Lock the draw so the "deterministic, immutable" contract holds literally:
    # neither ``matrix`` nor the views ``column`` returns can be written in place.
    matrix.flags.writeable = False
    return ParameterSamples(names=names, matrix=matrix)
