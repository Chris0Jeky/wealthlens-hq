"""DRAFT migration 0002 — embeddings (promoted to a real revision in H1-05).

Requires the pgvector extension. The vector DIMENSION is fixed by the
ADR 0003 embedding-model decision; both candidate models (hosted 1536-dim,
open-weights 1024-dim) sit under pgvector's 2,000-dim limit for standard
HNSW indexes, so no halfvec workaround is needed.

Kept as a separate table (not a column on chunks) so re-embedding with a
different model is an insert+swap, not a chunks rewrite, and so the model
that produced each vector is recorded — an embedding without its model id
is unreproducible.

DDL sketch::

    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE TABLE embeddings (
        chunk_id   BIGINT PRIMARY KEY REFERENCES chunks(chunk_id) ON DELETE CASCADE,
        model      TEXT NOT NULL,            -- e.g. the ADR 0003 choice
        embedding  VECTOR(<DIM>) NOT NULL,   -- <DIM> fixed by ADR 0003
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX embeddings_hnsw ON embeddings
        USING hnsw (embedding vector_cosine_ops);
"""
