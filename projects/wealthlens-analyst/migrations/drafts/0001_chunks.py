"""DRAFT migration 0001 — chunks table (promoted to a real revision in H1-05).

Provenance is captured AT INGESTION TIME (ADR 0001 §4): citations resolve
from these columns and are never reconstructed later. NOT NULL is the
enforcement: a chunk that cannot say where it came from cannot be stored.
`page`/`section`/`span` are nullable because tabular sources have no pages —
but ingestion requires section+span for tabular and page+span for documents
(checked in code, task H1-09).

DDL sketch::

    CREATE TABLE chunks (
        chunk_id     BIGSERIAL PRIMARY KEY,
        source_id    TEXT NOT NULL,          -- registries/sources.yml id
        document_id  TEXT NOT NULL,          -- file/publication identifier
        section      TEXT,                   -- heading / table section
        page         INTEGER,                -- PDF page (null for tabular)
        span         TEXT,                   -- char/cell range within section
        text         TEXT NOT NULL,
        token_count  INTEGER NOT NULL,
        access_date  DATE NOT NULL,          -- when the source was fetched
        created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
        ts           TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', text)) STORED
    );
    CREATE INDEX chunks_ts_gin ON chunks USING GIN (ts);
    CREATE INDEX chunks_source ON chunks (source_id, document_id);
"""
