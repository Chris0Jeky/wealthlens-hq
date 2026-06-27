"""Database access for the analyst: engine factory + Core table handles.

The DDL is owned by the hand-written Alembic migrations under
``migrations/versions/`` — they stay the single source of truth (env.py diffs
against no metadata: ``target_metadata = None``). The lightweight SQLAlchemy
Core table defined here mirrors migration ``0001_chunks`` for ONE purpose:
issuing typed INSERT/DELETE statements on the ingestion write path (H1-09). It
is never used to emit DDL.

Server-managed columns are deliberately omitted, because the write path must
never supply them:

- ``chunk_id`` — an always-``Identity`` primary key (Postgres assigns it);
- ``ts`` — a STORED generated ``tsvector`` (Postgres maintains the FTS index);
- ``created_at`` — a ``now()`` server default.
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Engine

from wealthlens_analyst.config import Settings

# Mirrors the INSERTABLE columns of migration 0001_chunks. A standalone
# MetaData (never reflected, never create_all'd) so this can be imported with no
# database connection — CI has no Postgres service.
chunks_metadata = sa.MetaData()
chunks_table = sa.Table(
    "chunks",
    chunks_metadata,
    sa.Column("source_id", sa.Text, nullable=False),
    sa.Column("document_id", sa.Text, nullable=False),
    sa.Column("section", sa.Text),
    sa.Column("page", sa.Integer),
    sa.Column("span", sa.Text),
    sa.Column("text", sa.Text, nullable=False),
    sa.Column("token_count", sa.Integer, nullable=False),
    sa.Column("access_date", sa.Date, nullable=False),
)


def engine_from_settings(settings: Settings) -> Engine:
    """Build a SQLAlchemy engine from the configured ``DATABASE_URL``.

    Fails loudly when the URL is unset: an ingest or retrieval call with no
    database configured is a setup error, not something to paper over with a
    silent default (which would surface later as a confusing connection error).
    """
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not configured (see .env.example); cannot reach the analyst database")
    return sa.create_engine(settings.database_url)
