"""Dense retrieval over pgvector.

Embeds the query through the LLM client seam (llm/client.py — the ONLY module
allowed to touch provider SDKs, ADR 0002) and runs cosine-similarity search
against the `embeddings` table (HNSW index; see
migrations/drafts/0002_embeddings.py).

Embedding model choice is an ADR 0003 open decision; this module reads it
from configuration and must not hard-code a provider.

Pending: task H1-11 in tasks/hero1-backlog.md.
"""

from __future__ import annotations

from wealthlens_analyst.retrieval.fts import ChunkHit


def search_dense(query: str, *, limit: int = 50) -> list[ChunkHit]:
    """Return the top `limit` chunks by cosine similarity.

    Implemented in H1-11: embed the query via the client seam, then
    `ORDER BY embedding <=> :query_vec LIMIT :limit` with provenance joined
    from the chunks table.
    """
    raise NotImplementedError("H1-11: dense query path not yet implemented")


def embed_corpus(*, batch_size: int = 64) -> int:
    """Embed every chunk lacking an embedding row; returns the count embedded.

    Implemented in H1-11 as the batch ingestion step behind `make ingest-slice`.
    """
    raise NotImplementedError("H1-11: corpus embedding not yet implemented")
