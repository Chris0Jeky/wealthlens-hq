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

    @model_validator(mode="after")
    def _identifiers_are_provenance_safe(self) -> ParameterSpec:
        """Forbid the provenance-tag structural delimiters in name/source_id.

        The canonical tag is ``name=dist(low,central,high)@source_id`` and tags are
        joined with ``;``. If ``name`` or ``source_id`` could contain any of those
        delimiters (or whitespace), two distinct spec sets could serialise to the
        same ``uncertainty.specs`` string, defeating the reproducibility guarantee.
        Parameter names and registry source ids are simple identifiers, so this
        precondition is cheap to enforce and keeps the readable grammar injective.
        """
        forbidden = set(";=@(),") | set(" \t\n\r\f\v")
        for field, val in (("name", self.name), ("source_id", self.source_id)):
            if val is not None and (set(val) & forbidden):
                msg = (
                    f"ParameterSpec {field}={val!r} must not contain whitespace or "
                    "any of the provenance delimiters ; = @ ( ) ,"
                )
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

    def provenance_tag(self) -> str:
        """Canonical, deterministic one-line encoding of this marginal spec.

        Captures everything that changes the drawn column for a parameter — name,
        distribution kind, bounds/mode, and source id — so two specs that produce
        different draws encode to *different* strings (and identical specs encode
        identically). Floats use an exact round-tripping ``repr`` (see
        :func:`_format_float`) so even sub-12-significant-figure bound differences
        are reflected. ``central`` is always included (it does not affect a UNIFORM
        draw but keeps the encoding total and unambiguous); ``source_id`` renders as
        ``-`` when absent so a change of evidence is always reflected in provenance.
        The structural delimiters (``; = @ ( ) ,`` and whitespace) are rejected from
        ``name``/``source_id`` by a validator, so this readable grammar is injective.
        """
        source = self.source_id if self.source_id is not None else "-"
        return (
            f"{self.name}="
            f"{self.distribution.value}"
            f"({_format_float(self.low)},{_format_float(self.central)},{_format_float(self.high)})"
            f"@{source}"
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
    engine, not a serialised contract. ``matrix`` is set read-only in
    ``__post_init__`` so the deterministic draw cannot be mutated in place via the
    array or the views ``column`` returns — for *any* construction path, not only
    :func:`sample_parameters`. ``seed`` and ``method`` are carried so the draw is
    fully reproducible from the sample block (and its provenance) alone. ``specs``
    retains the ordered marginal definitions (aligned column-for-column with
    ``names``/``matrix``) so the run can be regenerated and so its provenance can
    capture the full marginal of every parameter, not merely its name.
    """

    names: tuple[str, ...]
    specs: tuple[ParameterSpec, ...]
    matrix: NDArray[np.float64]
    seed: int
    method: SamplingMethod

    def __post_init__(self) -> None:
        # Own the draw before locking it, so the "deterministic, immutable" contract
        # holds for ANY construction path. Merely flipping ``writeable`` on the
        # passed array is not enough: a caller can construct ParameterSamples around
        # a *view* (whose writeable base array stays mutable) or around an array it
        # still references and can re-enable writing on — either lets an external
        # mutation silently corrupt the values the engine/provenance later read.
        # Copying to a private array no caller can reach, then marking *that*
        # read-only, closes both holes. ``object.__setattr__`` rebinds the field on
        # the frozen dataclass; the copy is O(n_samples * n_params), negligible
        # beside the draw itself.
        owned = self.matrix.copy()
        owned.flags.writeable = False
        object.__setattr__(self, "matrix", owned)

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
        a Monte-Carlo run is as auditable as a single-point run. ``seed`` and
        ``method`` are included so two runs over the same parameters but a
        different seed or draw method publish *distinct* provenance and the exact
        draw set is reproducible from the trail. The ``uncertainty.specs`` tag
        canonically encodes every parameter's full marginal (distribution, bounds,
        mode, source id), so two runs that share names/seed/method/sample-count but
        differ in bounds, distribution, or source publish *distinct* provenance —
        identical ids therefore imply an identical draw matrix. A later
        engine-wiring PR can fold these into the provenance trail alongside the
        population's source ids.
        """
        return [
            f"uncertainty.n_samples:{self.n_samples}",
            f"uncertainty.method:{self.method.value}",
            f"uncertainty.seed:{self.seed}",
            f"uncertainty.parameters:{';'.join(self.names)}",
            f"uncertainty.specs:{';'.join(spec.provenance_tag() for spec in self.specs)}",
        ]


def _format_float(value: float) -> str:
    """Exact, stable float repr for provenance tags.

    Uses ``repr`` — the shortest string that round-trips to the *same* float64 —
    so two specs differing in any bound (even below 12 significant figures)
    serialise to *different* tags. This makes the provenance guarantee literal:
    identical ``uncertainty.specs`` tags imply identical drawn columns, not merely
    columns equal to ~12 significant figures. ``+ 0.0`` folds ``-0.0`` to ``0.0``
    (numerically identical, identical draws) so a cosmetic sign-of-zero cannot
    perturb the tag.
    """
    return repr(value + 0.0)


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

    # ParameterSamples.__post_init__ locks ``matrix`` read-only. ``ordered`` is the
    # sorted-by-name spec list used to build each column, so it stays aligned with
    # ``names``/``matrix`` and lets provenance capture every parameter's marginal.
    return ParameterSamples(
        names=names,
        specs=tuple(ordered),
        matrix=matrix,
        seed=config.seed,
        method=config.method,
    )
