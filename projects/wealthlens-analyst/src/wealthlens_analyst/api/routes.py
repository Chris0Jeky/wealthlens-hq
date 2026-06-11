"""API routes.

- POST /ask           — the analyst. Body: {"question": ...}. Optional
                        ?debug=retrieval returns the fused candidate list
                        (with per-chunk provenance and component ranks)
                        WITHOUT generation — the M2 milestone surface.
- GET  /healthz       — liveness: app up, DB reachable.
- GET  /metrics/data  — JSON for the public metrics page: p50/p95 latency and
                        cost per query, computed from query_log (ADR 0002).
                        Cache hit rate is added only when caching lands.

Response schemas (answer | refusal | over-budget) are fixed in H1-20 and
validated by a deterministic eval check.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class AskRequest(BaseModel):
    """A question for the analyst."""

    question: str = Field(min_length=1, max_length=2000)


@router.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness probe. DB reachability check is added with H1-13."""
    return {"status": "ok"}


@router.post("/ask")
def ask(request: AskRequest, debug: str | None = None) -> dict[str, object]:
    """Answer a question with chunk-level citations, refuse honestly, or 429.

    Pipeline (pending tasks H1-13..H1-22): budget guard -> hybrid retrieval
    (FTS + dense, RRF-fused) -> optional rerank (flag) -> abstention gate ->
    cited composition -> citation resolution -> query_log row.
    """
    raise NotImplementedError("H1-13: /ask not yet implemented")


@router.get("/metrics/data")
def metrics_data() -> dict[str, object]:
    """Serve p50/p95 latency and cost-per-query aggregates from query_log."""
    raise NotImplementedError("H1-29: metrics endpoint not yet implemented")
