"""Lexical retrieval over Postgres full-text search.

Queries the `chunks` table's tsvector column (GIN-indexed; see
migrations/versions/0001_chunks.py) and returns ranked chunk hits. Official
statistics are full of exact terms ("decile", "nil-rate band", years, table
numbers), which is why the lexical leg of the hybrid is load-bearing.

Pending: task H1-10 in tasks/hero1-backlog.md.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkHit:
    """One retrieved chunk with its provenance, as stored at ingestion time.

    Provenance fields mirror the chunks table columns (ADR 0001 §4):
    citations resolve from these, never reconstructed later.
    """

    chunk_id: int
    source_id: str  # registry id in registries/sources.yml
    document_id: str
    section: str | None
    page: int | None
    span: str | None
    text: str
    rank: int  # 1-based rank within this retriever's result list
    score: float  # retriever-native score (ts_rank / cosine similarity)


def search_fts(query: str, *, limit: int = 50) -> list[ChunkHit]:
    """Return the top `limit` chunks by Postgres full-text rank.

    Implemented in H1-10: plainto_tsquery/websearch_to_tsquery over the
    GIN-indexed tsvector column, ordered by ts_rank.
    """
    raise NotImplementedError("H1-10: FTS query path not yet implemented")
