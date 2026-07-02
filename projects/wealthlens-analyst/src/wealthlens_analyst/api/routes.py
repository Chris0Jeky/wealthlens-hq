"""API routes.

- POST /ask           — the analyst. Body: {"question": ...}. With
                        ?debug=retrieval (H1-13, the M2 milestone surface) it
                        returns the RRF-fused candidate list with per-chunk
                        provenance and both component ranks, WITHOUT
                        generation. Plain mode (cited answer | refusal) lands
                        in H1-18/H1-21 and until then returns 501.
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
from typing import Annotated, Literal

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError

from wealthlens_analyst.retrieval.dense import search_dense
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
        """Reject whitespace-only questions before they reach retrieval.

        min_length=1 alone would admit " ", which FTS-matches nothing but
        would still trigger a paid embedding call in the dense leg.
        """
        if not value.strip():
            raise ValueError("question must not be blank")
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

    Any database failure maps to 503 (the probe's honest signal), never a 500:
    a health endpoint that crashes on the condition it exists to detect would
    be reporting its own bug, not the service's state.
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

    Pipeline (pending tasks H1-15..H1-22): budget guard -> hybrid retrieval
    (FTS + dense, RRF-fused) -> optional rerank (flag) -> abstention gate ->
    cited composition -> citation resolution -> query_log row.

    H1-13 ships the retrieval half behind ?debug=retrieval: both retriever
    legs run against the shared engine, RRF fuses them (k=60, ADR 0001), and
    the response carries full provenance plus each chunk's component ranks.
    Plain mode is 501 until composition (H1-18) lands — an explicit contract,
    not a stub crash.
    """
    if debug != "retrieval":
        raise HTTPException(
            status_code=501,
            detail="answer composition is not implemented yet (H1-18); use POST /ask?debug=retrieval",
        )
    lexical = search_fts(request.question, limit=_PER_RETRIEVER_LIMIT, engine=engine)
    dense = search_dense(request.question, limit=_PER_RETRIEVER_LIMIT, engine=engine)
    fused = fuse_rrf(lexical, dense, limit=_FUSED_LIMIT)
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
