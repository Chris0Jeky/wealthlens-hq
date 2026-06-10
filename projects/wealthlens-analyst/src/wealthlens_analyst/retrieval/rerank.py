"""Optional reranking of the fused candidate list (ADR 0001 §3).

Sits behind the RERANK_ENABLED feature flag, default OFF: with the flag off,
the fused RRF order passes through untouched (byte-identical behaviour, locked
by a test in H1-16). Which reranker (Cohere Rerank API vs self-hosted BGE) is
an ADR 0003 open decision — this module must keep the choice behind one
function so the decision is a config/implementation swap, not a refactor.

If the reranker is API-based, its calls are metered through the budget
middleware like every other model call (ADR 0002).

Pending: task H1-16 in tasks/hero1-backlog.md.
"""

from __future__ import annotations

from wealthlens_analyst.retrieval.fts import ChunkHit


def rerank(query: str, candidates: list[ChunkHit], *, top_k: int = 8) -> list[ChunkHit]:
    """Rerank fused candidates; return the top_k in reranked order.

    Callers must check Settings.rerank_enabled BEFORE calling — flag-off
    means this function is never invoked.
    """
    raise NotImplementedError("H1-16: reranker pending ADR 0003 decision")
