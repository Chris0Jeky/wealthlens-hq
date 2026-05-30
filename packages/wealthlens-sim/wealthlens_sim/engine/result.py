"""Engine result types and the population-source seam (Wave 12 PR3a).

The :class:`EngineResult` is the engine's public contract: every published number
is an :class:`~wealthlens_sim.top_tail.types.Interval` (never a naked point
estimate — Blueprint v5 §10.1) and carries a
:class:`~wealthlens_sim.provenance.manifest.ProvenanceManifest`.

:class:`PopulationSource` is a structural seam: the engine scores *anything* with
``households`` and ``provenance_ids`` attributes. ``SyntheticPopulation`` satisfies
it today; a future real-microdata provider (behind a UKDS licence) can drop in
without the engine changing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.assumptions.schema import AssumptionRegistry
from wealthlens_sim.provenance.manifest import ProvenanceManifest
from wealthlens_sim.reforms.g_devolution import DevolutionSplit
from wealthlens_sim.rules.scenario import Scenario
from wealthlens_sim.schema.household import Household
from wealthlens_sim.top_tail.types import Interval

__all__ = [
    "N_DECILES",
    "EngineResult",
    "Interval",
    "PopulationSource",
    "Registries",
]

#: Number of wealth deciles the engine attributes revenue across.
N_DECILES = 10


@runtime_checkable
class PopulationSource(Protocol):
    """Structural type for any population the engine can score.

    The engine only needs a list of households (each carrying its own grossing
    ``weight``) and the provenance ids that describe how the population was
    produced. ``SyntheticPopulation`` satisfies this protocol; a licensed
    real-microdata provider can satisfy it without engine changes.
    """

    households: list[Household]
    provenance_ids: list[str]


@dataclass(frozen=True)
class Registries:
    """Optional registry bundle the engine reads for provenance + policy status.

    A frozen dataclass (not a Pydantic model) so it can hold the registry objects
    without arbitrary-type juggling. Both members are optional: when
    ``assumptions`` is present the engine routes provenance through a
    :class:`~wealthlens_sim.provenance.collector.ProvenanceCollector`; PR3c
    consumes the top-tail alpha + assumption ranges through the same seam.
    """

    assumptions: AssumptionRegistry | None = None


class EngineResult(BaseModel):
    """End-to-end result of scoring a scenario over a population.

    All revenue figures are GBP billions as intervals. ``revenue_by_decile`` is
    ordered from the lowest wealth decile (index 0) to the highest (index 9); it
    is either empty (no households scored) or exactly :data:`N_DECILES` long.
    """

    model_config = ConfigDict(extra="forbid")

    scenario: Scenario
    total_revenue_gbp_bn: Interval
    revenue_by_nation: dict[str, Interval]
    revenue_by_decile: list[Interval] = Field(default_factory=list)
    #: Net Family-F enforcement uplift (revenue from closing the compliance gap,
    #: minus enforcement cost) in GBP bn. It is **included in
    #: ``total_revenue_gbp_bn``** (do not add it again) but is an aggregate
    #: compliance-gap figure NOT attributed to nation or decile, so
    #: ``sum(revenue_by_decile) ~= total_revenue_gbp_bn - enforcement_uplift_bn``.
    #: Zero when no enforcement config is supplied. May be negative if enforcement
    #: cost exceeds the uplift. **v0.1 caveat:** because the A-E base is full
    #: statutory liability, this uplift sits on top of the 100%-compliance ceiling
    #: and overstates collectible revenue — see ``engine._enforcement``.
    enforcement_uplift_bn: Interval = Field(default_factory=lambda: Interval(low=0.0, central=0.0, high=0.0))
    #: Count of households actually scored. When a devolution scope is applied
    #: this is the *included* subset (see ``devolution_split``), not the whole
    #: population.
    households_scored: int = Field(ge=0)
    provenance: ProvenanceManifest
    #: The nation-scope split when a Family G devolution scope was applied
    #: (which nations were included/excluded and their weights); ``None`` when
    #: the scenario ran UK-wide over the whole population.
    devolution_split: DevolutionSplit | None = None
    #: Provenance ids carried by the scored population (e.g. synth calibration
    #: sources). Surfaced verbatim so the population's own provenance is never
    #: silently dropped; empty for the v0.1 synthetic generator.
    population_provenance_ids: list[str] = Field(default_factory=list)
    #: ``True`` once every registry assumption the published intervals depend on
    #: (the top-tail Pareto alpha driving the revenue bounds) has been consumed
    #: and recorded in the manifest. ``False`` when no assumption registry was
    #: supplied — then the intervals are degenerate (uncertainty unquantified) and
    #: a consumer must NOT treat the figures as fully sourced. The scenario policy
    #: parameters are always carried verbatim on ``scenario``, not the manifest.
    provenance_complete: bool = False

    @model_validator(mode="after")
    def _check_decile_count(self) -> EngineResult:
        n = len(self.revenue_by_decile)
        if n not in (0, N_DECILES):
            msg = f"revenue_by_decile must have 0 or {N_DECILES} entries, got {n}"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check_devolution_consistency(self) -> EngineResult:
        # When a devolution scope was applied, households_scored is the included
        # subset, so it must equal the split's included_count — guards against an
        # inconsistent result (e.g. hand-constructed) carrying mismatched counts.
        if (
            self.devolution_split is not None
            and self.households_scored != self.devolution_split.included_count
        ):
            msg = (
                f"households_scored ({self.households_scored}) must match "
                f"devolution_split.included_count ({self.devolution_split.included_count})"
            )
            raise ValueError(msg)
        return self
