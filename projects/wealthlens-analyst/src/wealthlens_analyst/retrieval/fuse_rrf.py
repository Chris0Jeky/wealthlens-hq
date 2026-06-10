"""Reciprocal Rank Fusion of the lexical and dense result lists (ADR 0001).

RRF is rank-based — score(d) = sum over lists of 1 / (k + rank(d)) — so it
needs no calibration between incomparable score distributions (ts_rank vs
cosine similarity). k = 60 is the standard constant from the original paper
(Cormack, Clarke & Buettcher 2009) and is locked by ADR 0001.

This module is pure (no DB, no model calls) so the eval harness's
deterministic checks can exercise it directly.

Pending: task H1-12 in tasks/hero1-backlog.md.
"""

from __future__ import annotations

from wealthlens_analyst.retrieval.fts import ChunkHit

RRF_K = 60


def fuse_rrf(
    lexical: list[ChunkHit],
    dense: list[ChunkHit],
    *,
    k: int = RRF_K,
    limit: int = 20,
) -> list[ChunkHit]:
    """Fuse two ranked lists into one, ordered by descending RRF score.

    Each returned hit keeps its provenance; component ranks are surfaced via
    the /ask?debug=retrieval response so recall analysis can attribute hits
    to a retriever. Ties break deterministically (by chunk_id) so results
    are reproducible.
    """
    raise NotImplementedError("H1-12: RRF fusion not yet implemented")
