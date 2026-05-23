"""Provenance manifests for audit-trail and reproducibility.

Every WealthLens output carries a provenance envelope listing all assumption IDs,
data versions, code versions, and source references it depends on.

Reference: Blueprint v5 sections 8.2, 13.4, compass deliverable 31.
"""

from wealthlens_sim.provenance.collector import ProvenanceCollector
from wealthlens_sim.provenance.manifest import (
    PipelineLayer,
    ProvenanceEntry,
    ProvenanceManifest,
    ResolvedAssumption,
)

__all__ = [
    "PipelineLayer",
    "ProvenanceCollector",
    "ProvenanceEntry",
    "ProvenanceManifest",
    "ResolvedAssumption",
]
