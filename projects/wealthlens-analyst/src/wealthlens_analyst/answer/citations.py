"""Resolve and verify chunk-level citations (ADR 0001 §4).

A citation is only served if its chunk_id exists and its stored provenance
(source_id, document_id, section, page, span — captured at ingestion) matches
what the answer renders. Unresolvable citations are stripped and flagged: a
fabricated citation is worse than no answer.

Citation resolvability is one of the deterministic eval checks
(evals/checks/deterministic.py), so this module stays side-effect free and
easily testable.

Pending: task H1-19 in tasks/hero1-backlog.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from wealthlens_analyst.answer.compose import ComposedAnswer


@dataclass(frozen=True)
class Citation:
    """A resolved, render-ready citation."""

    chunk_id: int
    source_id: str
    source_name: str
    document_id: str
    section: str | None
    page: int | None
    url: str  # the registry source URL (registries/sources.yml)


def resolve_citations(answer: ComposedAnswer) -> list[Citation]:
    """Resolve every cited chunk_id to full provenance from the database.

    Raises / flags (exact contract fixed in H1-19) when a cited chunk_id does
    not exist — that signals the model fabricated a citation.
    """
    raise NotImplementedError("H1-19: citation resolution not yet implemented")
