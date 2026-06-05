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
    :class:`~wealthlens_sim.provenance.collector.ProvenanceCollector` and consumes
    the top-tail alpha that drives the revenue intervals through that seam.
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
    #: Gross Family-F enforcement revenue uplift from closing the compliance gap
    #: in GBP bn. It is **included in ``total_revenue_gbp_bn``** (do not add it
    #: again) but is an aggregate compliance-gap figure NOT attributed to nation
    #: or decile, so
    #: ``sum(revenue_by_decile) ~= total_revenue_gbp_bn - enforcement_uplift_bn``.
    #: Zero when no enforcement config is supplied. When Family F is supplied,
    #: the decile and nation breakdowns represent baseline-compliance revenue;
    #: the uplift moves that baseline toward scenario compliance without
    #: exceeding the theoretical full-compliance ceiling. Enforcement cost is
    #: expenditure, not revenue, and is surfaced separately below.
    enforcement_uplift_bn: Interval = Field(default_factory=lambda: Interval(low=0.0, central=0.0, high=0.0))
    #: Additional HMRC enforcement cost in GBP bn. This is not included in
    #: ``total_revenue_gbp_bn`` because the headline is a revenue figure.
    enforcement_cost_bn: Interval = Field(default_factory=lambda: Interval(low=0.0, central=0.0, high=0.0))
    #: Net fiscal impact in GBP bn: gross enforcement revenue uplift minus
    #: enforcement cost. This may be negative; it is reported separately so the
    #: revenue headline and attribution invariants cannot go below zero because
    #: of a spending assumption.
    enforcement_net_fiscal_impact_bn: Interval = Field(
        default_factory=lambda: Interval(low=0.0, central=0.0, high=0.0)
    )
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
    #: silently dropped; empty when a generator cannot assert source-backed
    #: population provenance.
    population_provenance_ids: list[str] = Field(default_factory=list)
    #: Whether the scored population is synthetic (generated microdata) rather than
    #: real respondent microdata. Carried from the population source so the dashboard
    #: contract can surface the synthetic-population caveat from GROUND TRUTH rather
    #: than inferring it from a version-tag string. Defaults ``True`` (fail-closed:
    #: if a source does not assert it is real, treat it as synthetic and warn).
    population_is_synthetic: bool = Field(default=True)
    #: Provenance ids for the Monte-Carlo uncertainty propagation, when an
    #: ``uncertainty`` sampling config was supplied to :func:`simulate` (the seed,
    #: method, sample count, the sampled marginals, and the centre/quantile choices
    #: — see :meth:`ParameterSamples.provenance_ids` / :class:`PropagationResult`).
    #: Empty when the feature is OFF (the default), in which case the revenue band
    #: is the single multiplicative top-tail-alpha sweep recorded in the manifest.
    uncertainty_provenance_ids: list[str] = Field(default_factory=list)
    #: ``True`` once every **registry assumption** the published intervals depend
    #: on (the top-tail Pareto alpha driving the revenue bounds) has been consumed
    #: and recorded in the manifest. ``False`` when no assumption registry was
    #: supplied — then the intervals are degenerate (uncertainty unquantified) and
    #: a consumer must NOT treat the figures as fully sourced.
    #:
    #: Scope of the claim (what ``True`` does NOT cover, by design in v0.1): the
    #: scenario *policy parameters* are carried verbatim on ``scenario`` (not the
    #: manifest), and population-source metadata is surfaced separately in
    #: ``population_provenance_ids``. For the synthetic provider this includes the
    #: calibration source ids plus stable ``synth.*`` tags for *every* generation
    #: parameter that affects the drawn population (seed, household count, grossing
    #: total, the lognormal/Pareto wealth-shape parameters, couple share, and the
    #: nation/asset share mappings) — so two materially different synthetic
    #: populations cannot publish identical provenance. A future real-microdata
    #: provider can expose its own ids through the same seam.
    #: ``provenance_complete`` therefore means
    #: "registry-assumption trail for the intervals is complete", not "every input
    #: is traceable from the manifest alone".
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
