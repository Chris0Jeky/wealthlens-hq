"""API routes.

- POST /ask           — the analyst. Body: {"question": ...}. With
                        ?debug=retrieval (H1-13, the M2 milestone surface) it
                        returns the RRF-fused candidate list with per-chunk
                        provenance and both component ranks, WITHOUT
                        generation. Every debug request writes a query_log
                        accounting row (H1-15): hashed question, decision,
                        embed tokens + cost, latency. Plain mode (cited
                        answer | refusal) lands in H1-18/H1-21 and until then
                        returns 501 (and writes no row — nothing runs).
- GET  /healthz       — liveness: app up, DB reachable.
- GET  /metrics/data  — JSON for the public metrics page: p50/p95 latency and
                        cost per query, computed from query_log (ADR 0002).
                        Cache hit rate is added only when caching lands.

Response schemas (answer | refusal | over-budget) are fixed in H1-20 and
validated by a deterministic eval check; the debug=retrieval schema below is
separate (a diagnostic surface, not a product answer).
"""

from __future__ import annotations

import logging
import time
from typing import Annotated, Literal

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError

from wealthlens_analyst.budget.models import QueryDecision, record_query
from wealthlens_analyst.llm.client import EmbeddingResult, get_client
from wealthlens_analyst.retrieval.dense import search_dense_by_vector
from wealthlens_analyst.retrieval.fts import search_fts
from wealthlens_analyst.retrieval.fuse_rrf import fuse_rrf

logger = logging.getLogger(__name__)

router = APIRouter()

#: How many candidates each retriever contributes to fusion. Matches the
#: search_fts/search_dense default: deep enough that RRF sees genuine overlap,
#: cheap enough that a single /ask stays one embedding call + two indexed reads.
_PER_RETRIEVER_LIMIT = 50

#: How many fused candidates the debug surface returns. Matches the fuse_rrf
#: default (ADR 0001); H1-14's recall report is measured against this top-N.
_FUSED_LIMIT = 20


def _elapsed_ms(started: float) -> int:
    """Milliseconds since a time.perf_counter() start, rounded to int."""
    return round((time.perf_counter() - started) * 1000)


def _record_outcome_best_effort(
    engine: Engine,
    question: str,
    decision: QueryDecision,
    embedded: EmbeddingResult | None,
    started: float,
) -> None:
    """Record a query_log row on a FAILURE path without masking the failure.

    The original error is what the caller must see; if the accounting write
    also fails (e.g. the same DB outage that broke retrieval), that is logged
    loudly and swallowed — the opposite policy from the success path, where
    an accounting failure fails the request (see ask()).
    """
    try:
        record_query(
            engine,
            question=question,
            decision=decision,
            tokens_in=embedded.tokens_in if embedded is not None else 0,
            tokens_out=0,
            cost_gbp=embedded.cost_gbp if embedded is not None else 0.0,
            latency_ms=_elapsed_ms(started),
        )
    except Exception:  # deliberately broad: never mask the original error
        logger.exception("ask: could not record %s query_log row", decision.value)


def get_engine(request: Request) -> Engine:
    """Yield the app's shared engine (created in app.py's lifespan).

    A FastAPI dependency so tests can override it (dependency_overrides)
    without a database; the request path never builds an engine per query.
    """
    engine: Engine = request.app.state.engine
    return engine


class AskRequest(BaseModel):
    """A question for the analyst."""

    question: str = Field(min_length=1, max_length=2000)

    @field_validator("question")
    @classmethod
    def _reject_blank(cls, value: str) -> str:
        """Reject blank and NUL-bearing questions before they reach retrieval.

        min_length=1 alone would admit " ", which FTS-matches nothing but
        would still trigger a paid embedding call in the dense leg. A NUL
        byte is valid JSON/Python but not valid Postgres text — it would
        surface as a DB error (500) instead of the honest 422.
        """
        if not value.strip():
            raise ValueError("question must not be blank")
        if "\x00" in value:
            raise ValueError("question must not contain NUL characters")
        return value


class RetrievalCandidate(BaseModel):
    """One fused retrieval candidate with its ingestion-time provenance.

    Provenance fields mirror the chunks table columns (ADR 0001 §4) — carried
    through ChunkHit, never reconstructed. fts_rank/dense_rank are the chunk's
    1-based rank within each retriever's own list (None = that retriever did
    not return it), so H1-14's recall analysis can attribute every hit.
    """

    chunk_id: int
    source_id: str
    document_id: str
    section: str | None
    page: int | None
    span: str | None
    text: str
    fused_rank: int
    rrf_score: float
    fts_rank: int | None
    dense_rank: int | None


class RetrievalDebugResponse(BaseModel):
    """The /ask?debug=retrieval payload: fused candidates, no generation."""

    question: str
    mode: Literal["retrieval"] = "retrieval"
    fts_candidates: int
    dense_candidates: int
    candidates: list[RetrievalCandidate]


@router.get("/healthz")
def healthz(engine: Annotated[Engine, Depends(get_engine)]) -> dict[str, str]:
    """Liveness probe: app up AND the database is reachable.

    Database failures surface as SQLAlchemyError (SQLAlchemy wraps every
    DBAPI/psycopg error, including pool timeouts) and map to 503 — the
    probe's honest signal, not a 500: a health endpoint that crashes on the
    condition it exists to detect would be reporting its own bug, not the
    service's state. Anything outside that hierarchy would be a genuine app
    bug, and a 500 is then the correct signal.
    """
    try:
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.warning("healthz: database unreachable: %s", exc)
        raise HTTPException(status_code=503, detail="database unreachable") from exc
    return {"status": "ok", "database": "ok"}


@router.post("/ask")
def ask(
    request: AskRequest,
    engine: Annotated[Engine, Depends(get_engine)],
    debug: Literal["retrieval"] | None = None,
) -> RetrievalDebugResponse:
    """Answer a question with chunk-level citations, refuse honestly, or 429.

    Pipeline (pending tasks H1-16..H1-22): budget guard -> hybrid retrieval
    (FTS + dense, RRF-fused) -> optional rerank (flag) -> abstention gate ->
    cited composition -> citation resolution -> query_log row.

    H1-13 ships the retrieval half behind ?debug=retrieval: both retriever
    legs run against the shared engine, RRF fuses them (k=60, ADR 0001), and
    the response carries full provenance plus each chunk's component ranks.
    H1-15 adds the query_log row: hashed question, decision, the query
    embedding's real tokens/cost (generation tokens are 0 until H1-18), and
    latency — written for served requests AND failures; a success whose row
    cannot be written is failed (500) rather than served unmetered. Requests
    rejected by validation (422) never reach the handler and log nothing.
    Plain mode is 501 until composition (H1-18) lands — an explicit contract,
    not a stub crash.
    """
    if debug != "retrieval":
        # No query_log row: nothing ran and nothing was spent. Plain-mode
        # logging is defined with composition (H1-18/H1-20).
        raise HTTPException(
            status_code=501,
            detail="answer composition is not implemented yet (H1-18); use POST /ask?debug=retrieval",
        )
    started = time.perf_counter()
    embedded: EmbeddingResult | None = None
    # The legs run sequentially, FREE leg first, on purpose: if the database is
    # down, search_fts fails before the query embedding can spend. (Concurrent
    # legs are a latency optimisation to revisit once the budget guard, H1-27,
    # makes an always-spend race acceptable.) The embed happens HERE, through
    # the client seam, rather than inside search_dense, so its accounting can
    # be persisted to query_log (H1-15). A database failure is the backend's
    # fault, not the caller's -> 503, matching /healthz; provider (embedding)
    # failures stay 500 until H1-20 fixes the error schemas — both record an
    # `error` row first (with whatever WAS spent), best-effort.
    try:
        lexical = search_fts(request.question, limit=_PER_RETRIEVER_LIMIT, engine=engine)
        embedded = get_client().embed([request.question])
        dense = search_dense_by_vector(embedded.vectors[0], limit=_PER_RETRIEVER_LIMIT, engine=engine)
    except SQLAlchemyError as exc:
        logger.warning("ask: retrieval backend unavailable: %s", exc)
        _record_outcome_best_effort(engine, request.question, QueryDecision.ERROR, embedded, started)
        raise HTTPException(status_code=503, detail="retrieval backend unavailable") from exc
    except Exception:
        _record_outcome_best_effort(engine, request.question, QueryDecision.ERROR, embedded, started)
        raise
    fused = fuse_rrf(lexical, dense, limit=_FUSED_LIMIT)
    # Accounting is part of serving the request (ADR 0002): if the row cannot
    # be written, fail the request rather than serve unmetered spend — a
    # silently dropped row would systematically understate the summed cap
    # input the budget guard (H1-27) will enforce against.
    try:
        record_query(
            engine,
            question=request.question,
            decision=QueryDecision.ANSWERED,
            tokens_in=embedded.tokens_in,
            tokens_out=0,  # no generation in debug mode (H1-18)
            cost_gbp=embedded.cost_gbp,
            latency_ms=_elapsed_ms(started),
        )
    except SQLAlchemyError as exc:
        logger.error("ask: query_log write failed after successful retrieval: %s", exc)
        raise HTTPException(status_code=500, detail="query accounting failed") from exc
    # ChunkHit.rank is the 1-based position each retriever assigned (fts.py's
    # _hits_from_rows); fuse_rrf overwrites rank/score on ITS copies but the
    # raw input lists still hold the component ranks the response surfaces.
    fts_ranks = {hit.chunk_id: hit.rank for hit in lexical}
    dense_ranks = {hit.chunk_id: hit.rank for hit in dense}
    return RetrievalDebugResponse(
        question=request.question,
        fts_candidates=len(lexical),
        dense_candidates=len(dense),
        candidates=[
            RetrievalCandidate(
                chunk_id=hit.chunk_id,
                source_id=hit.source_id,
                document_id=hit.document_id,
                section=hit.section,
                page=hit.page,
                span=hit.span,
                text=hit.text,
                fused_rank=hit.rank,
                rrf_score=hit.score,
                fts_rank=fts_ranks.get(hit.chunk_id),
                dense_rank=dense_ranks.get(hit.chunk_id),
            )
            for hit in fused
        ],
    )


@router.get("/metrics/data")
def metrics_data() -> dict[str, object]:
    """Serve p50/p95 latency and cost-per-query aggregates from query_log."""
    raise NotImplementedError("H1-29: metrics endpoint not yet implemented")
