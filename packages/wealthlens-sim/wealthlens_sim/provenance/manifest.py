"""Provenance manifest models for audit-trail and reproducibility.

Blueprint v5 section 13.4: every published number carries a provenance
envelope listing assumption IDs, data versions, and source references.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt

from wealthlens_sim.schema.base import VersionTag


class PipelineLayer(StrEnum):
    """Blueprint v5 section 8.1: 12-layer architecture labels."""

    SURVEY_INGEST = "survey_ingest"
    HARMONISATION = "harmonisation"
    TOP_TAIL = "top_tail"
    POLICY_RULES = "policy_rules"
    BEHAVIOURAL = "behavioural"
    REVENUE = "revenue"
    UNCERTAINTY = "uncertainty"
    PRESENTATION = "presentation"
    VALIDATION = "validation"
    METADATA = "metadata"
    LOGGING = "logging"
    PROVENANCE = "provenance"


class ResolvedAssumption(BaseModel):
    """An assumption resolved to its concrete value at runtime."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    assumption_id: str
    domain: str
    # Scalars keep strict typing (no bool<->int leakage); schedules are
    # recorded faithfully as their full nested/band/flat payload.
    resolved_value: float | StrictInt | StrictBool | dict[str, Any] | list[Any]
    source: str
    # Canonical URLs (DOI/official) for the works named in `source`. A tuple keeps
    # this frozen model fully immutable. Empty when the registry entry has no URLs.
    # De-duplication + URL well-formedness are guaranteed upstream by the Assumption
    # schema validator (the collector only ever copies from a validated Assumption).
    source_urls: tuple[str, ...] = ()


class ProvenanceEntry(BaseModel):
    """Provenance trace for a single published output value."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    output_label: str = Field(description="Human-readable label for this output")
    layer: PipelineLayer
    assumption_ids: list[str] = Field(
        default_factory=list,
        description="Assumption IDs that influenced this value",
    )


class ProvenanceManifest(BaseModel):
    """Complete audit trail for a simulation run.

    Blueprint v5 section 13.4: every published number traces back through
    provenance_manifest() to source.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    version_tag: VersionTag
    run_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    assumptions_consumed: dict[str, ResolvedAssumption] = Field(
        default_factory=dict,
        description="Map of assumption_id -> resolved value at runtime",
    )
    entries: list[ProvenanceEntry] = Field(
        default_factory=list,
        description="Provenance trace per output value",
    )

    def assumption_ids(self) -> list[str]:
        """All assumption IDs consumed in this run."""
        return sorted(self.assumptions_consumed.keys())

    def entries_by_layer(self, layer: PipelineLayer) -> list[ProvenanceEntry]:
        """Filter entries by pipeline layer."""
        return [e for e in self.entries if e.layer == layer]
