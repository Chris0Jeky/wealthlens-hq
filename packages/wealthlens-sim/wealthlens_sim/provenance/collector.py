"""Runtime provenance collector for tracking consumed assumptions.

Blueprint v5 section 13.4: provenance_manifest() call is explicit
and central to the public API.
"""

from __future__ import annotations

from wealthlens_sim.assumptions import AssumptionRegistry
from wealthlens_sim.assumptions.schema import FlagValue, PointValue, RangeValue, ScheduleValue
from wealthlens_sim.provenance.manifest import (
    PipelineLayer,
    ProvenanceEntry,
    ProvenanceManifest,
    ResolvedAssumption,
)
from wealthlens_sim.schema.base import VersionTag


class ProvenanceCollector:
    """Collects provenance data during a simulation run.

    Usage:
        collector = ProvenanceCollector(version_tag, registry)
        value = collector.consume("toptail.pareto_alpha.overall.v1")
        collector.record("Top-1% wealth share", PipelineLayer.TOP_TAIL,
                         ["toptail.pareto_alpha.overall.v1"])
        manifest = collector.build()
    """

    def __init__(
        self,
        version_tag: VersionTag,
        registry: AssumptionRegistry,
    ) -> None:
        self._version_tag = version_tag
        self._registry = registry
        self._consumed: dict[str, ResolvedAssumption] = {}
        self._entries: list[ProvenanceEntry] = []
        self._built = False

    def consume(self, assumption_id: str) -> ResolvedAssumption:
        """Look up and record an assumption as consumed.

        Raises KeyError if the assumption_id is not in the registry.
        """
        if assumption_id in self._consumed:
            return self._consumed[assumption_id]

        assumption = self._registry.get(assumption_id)
        if assumption is None:
            msg = f"Assumption not found in registry: {assumption_id}"
            raise KeyError(msg)

        vd = assumption.value_or_distribution
        resolved: float | int | bool | dict[str, float | int]
        if isinstance(vd, PointValue):
            resolved = vd.value
        elif isinstance(vd, RangeValue):
            resolved = vd.central
        elif isinstance(vd, ScheduleValue):
            resolved = dict(vd.model_extra) if vd.model_extra else {}
        elif isinstance(vd, FlagValue):
            resolved = bool(vd.value)
        else:
            msg = f"Unknown value_or_distribution type: {type(vd)}"
            raise TypeError(msg)

        entry = ResolvedAssumption(
            assumption_id=assumption_id,
            domain=assumption.domain,
            resolved_value=resolved,
            source=assumption.source,
        )
        self._consumed[assumption_id] = entry
        return entry

    def record(
        self,
        output_label: str,
        layer: PipelineLayer,
        assumption_ids: list[str] | None = None,
    ) -> None:
        """Record a provenance entry for a published output."""
        ids = assumption_ids or []
        missing = [aid for aid in ids if aid not in self._consumed]
        if missing:
            msg = f"assumption_ids not yet consumed: {missing}"
            raise ValueError(msg)
        self._entries.append(
            ProvenanceEntry(
                output_label=output_label,
                layer=layer,
                assumption_ids=ids,
            )
        )

    def build(self) -> ProvenanceManifest:
        """Build the final provenance manifest. May only be called once."""
        if self._built:
            msg = "build() already called; create a new ProvenanceCollector"
            raise RuntimeError(msg)
        self._built = True
        return ProvenanceManifest(
            version_tag=self._version_tag,
            assumptions_consumed=dict(self._consumed),
            entries=list(self._entries),
        )
