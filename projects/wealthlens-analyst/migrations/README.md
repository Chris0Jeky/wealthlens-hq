# Migrations (Alembic)

Schema drafts live in `drafts/` until task **H1-05** wires Alembic properly
(`alembic.ini` + `env.py` against the package's SQLAlchemy metadata) and
promotes them to `versions/` as real revisions.

The repo had **no database and no migration tool** before this product
(the dashboard backend serves static CSVs), so Alembic was adopted here —
decision recorded in ADR 0001 §5. Scope is this subtree only.

Draft order (each file documents its DDL and rationale):

1. `drafts/0001_chunks.py` — corpus chunks with ingestion-time provenance
   columns (source_id, document_id, section, page, span) + tsvector/GIN.
2. `drafts/0002_embeddings.py` — pgvector column + HNSW index
   (dimension fixed by the ADR 0003 embedding decision).
3. `drafts/0003_budgets.py` — the hard spend cap (ADR 0002).
4. `drafts/0004_query_log.py` — per-query tokens/cost/latency/decision;
   feeds the public metrics page.
