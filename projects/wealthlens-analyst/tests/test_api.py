"""Unit tests for the /ask?debug=retrieval surface and /healthz (H1-13).

The retrieval SQL needs Postgres + pgvector, so the two retriever legs are
monkeypatched here with fixture ChunkHits and verified live against analyst-db
separately (the backlog's done-when). These tests pin what must hold WITHOUT a
database or a model call: the fusion wiring, the component-rank attribution,
the provenance passthrough, the response schema, and the failure contracts
(501 plain mode, 422 bad input, 503 unreachable DB).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError

import wealthlens_analyst.api.routes as routes
from wealthlens_analyst.api.app import create_app
from wealthlens_analyst.api.routes import get_engine
from wealthlens_analyst.budget.models import QueryDecision
from wealthlens_analyst.llm.client import EmbeddingResult
from wealthlens_analyst.retrieval.fts import ChunkHit
from wealthlens_analyst.retrieval.fuse_rrf import RRF_K


def _hit(chunk_id: int, rank: int, score: float) -> ChunkHit:
    """A ChunkHit with distinguishable provenance derived from chunk_id."""
    return ChunkHit(
        chunk_id=chunk_id,
        source_id=f"source-{chunk_id}",
        document_id=f"doc-{chunk_id}",
        section=f"section-{chunk_id}",
        page=None,
        span=f"span-{chunk_id}",
        text=f"text of chunk {chunk_id}",
        rank=rank,
        score=score,
    )


# Overlap fixture: chunk 2 appears in BOTH lists (top of dense, second in
# lexical) so fusion must rank it first and report both component ranks.
_LEXICAL = [_hit(1, rank=1, score=0.9), _hit(2, rank=2, score=0.5), _hit(3, rank=3, score=0.1)]
_DENSE = [_hit(2, rank=1, score=0.8), _hit(4, rank=2, score=0.7)]

_ENGINE_SENTINEL = object()

# What the fake client's embed() reports — the accounting the query_log row
# must carry (H1-15).
_EMBED_TOKENS = 7
_EMBED_COST_GBP = 2.5e-7


class _FakeClient:
    """Stands in for the llm/client seam: one canned embedding, no network."""

    def __init__(self, calls: dict[str, dict[str, Any]]) -> None:
        self._calls = calls

    def embed(self, texts: list[str]) -> EmbeddingResult:
        self._calls["embed"] = {"texts": list(texts)}
        return EmbeddingResult(
            vectors=[[0.1, 0.2, 0.3]],
            model="fake-embedding-model",
            tokens_in=_EMBED_TOKENS,
            cost_gbp=_EMBED_COST_GBP,
        )


@dataclass
class _Harness:
    """A DB-free app: fixture retriever legs, sentinel engine, recorded calls."""

    client: TestClient
    app: FastAPI
    calls: dict[str, dict[str, Any]] = field(default_factory=dict)
    recorded: list[dict[str, Any]] = field(default_factory=list)


@pytest.fixture()
def harness(monkeypatch: pytest.MonkeyPatch) -> _Harness:
    """Build the app with monkeypatched retrievers and an overridden engine.

    The TestClient is used WITHOUT entering its context manager, so the
    lifespan (real engine creation) never runs — these tests are DB-free.
    record_query is captured (not written): its row shape is pinned in
    test_budget_models.py and the real insert is verified live.
    """
    calls: dict[str, dict[str, Any]] = {}
    recorded: list[dict[str, Any]] = []

    def fake_fts(query: str, *, limit: int, engine: Any) -> list[ChunkHit]:
        calls["fts"] = {"query": query, "limit": limit, "engine": engine}
        return list(_LEXICAL)

    def fake_dense_by_vector(query_vec: list[float], *, limit: int, engine: Any) -> list[ChunkHit]:
        calls["dense"] = {"query_vec": query_vec, "limit": limit, "engine": engine}
        return list(_DENSE)

    def fake_record_query(engine: Any, **kwargs: Any) -> None:
        recorded.append({"engine": engine, **kwargs})

    monkeypatch.setattr(routes, "search_fts", fake_fts)
    monkeypatch.setattr(routes, "search_dense_by_vector", fake_dense_by_vector)
    monkeypatch.setattr(routes, "get_client", lambda: _FakeClient(calls))
    monkeypatch.setattr(routes, "record_query", fake_record_query)
    app = create_app()
    app.dependency_overrides[get_engine] = lambda: _ENGINE_SENTINEL
    return _Harness(client=TestClient(app), app=app, calls=calls, recorded=recorded)


def test_ask_debug_retrieval_fuses_and_attributes_component_ranks(harness: _Harness) -> None:
    response = harness.client.post("/ask?debug=retrieval", json={"question": "top decile wealth"})
    assert response.status_code == 200
    body = response.json()

    assert body["question"] == "top decile wealth"
    assert body["mode"] == "retrieval"
    assert body["fts_candidates"] == 3
    assert body["dense_candidates"] == 2

    # RRF (k=60): chunk 2 is in both lists so it must fuse first; the rest
    # follow by their single-list contribution 1/(k + position).
    assert [c["chunk_id"] for c in body["candidates"]] == [2, 1, 4, 3]
    assert [c["fused_rank"] for c in body["candidates"]] == [1, 2, 3, 4]

    by_id = {c["chunk_id"]: c for c in body["candidates"]}
    assert by_id[2]["rrf_score"] == pytest.approx(1 / (RRF_K + 2) + 1 / (RRF_K + 1))
    assert by_id[1]["rrf_score"] == pytest.approx(1 / (RRF_K + 1))
    assert by_id[4]["rrf_score"] == pytest.approx(1 / (RRF_K + 2))
    assert by_id[3]["rrf_score"] == pytest.approx(1 / (RRF_K + 3))

    # Component-rank attribution: both ranks when in both lists, None otherwise.
    assert (by_id[2]["fts_rank"], by_id[2]["dense_rank"]) == (2, 1)
    assert (by_id[1]["fts_rank"], by_id[1]["dense_rank"]) == (1, None)
    assert (by_id[4]["fts_rank"], by_id[4]["dense_rank"]) == (None, 2)
    assert (by_id[3]["fts_rank"], by_id[3]["dense_rank"]) == (3, None)


def test_ask_debug_retrieval_passes_provenance_through_unchanged(harness: _Harness) -> None:
    response = harness.client.post("/ask?debug=retrieval", json={"question": "median wealth"})
    top = response.json()["candidates"][0]  # chunk 2
    assert top["source_id"] == "source-2"
    assert top["document_id"] == "doc-2"
    assert top["section"] == "section-2"
    assert top["page"] is None
    assert top["span"] == "span-2"
    assert top["text"] == "text of chunk 2"


def test_ask_debug_retrieval_wires_shared_engine_into_both_legs(harness: _Harness) -> None:
    harness.client.post("/ask?debug=retrieval", json={"question": "capital gains"})
    assert harness.calls["fts"]["engine"] is _ENGINE_SENTINEL
    assert harness.calls["dense"]["engine"] is _ENGINE_SENTINEL
    assert harness.calls["fts"]["query"] == "capital gains"
    # The route embeds through the seam and passes the vector to the dense leg.
    assert harness.calls["embed"]["texts"] == ["capital gains"]
    assert harness.calls["dense"]["query_vec"] == [0.1, 0.2, 0.3]
    assert harness.calls["fts"]["limit"] == harness.calls["dense"]["limit"] == routes._PER_RETRIEVER_LIMIT


def test_ask_debug_retrieval_records_an_answered_row_with_real_embed_accounting(harness: _Harness) -> None:
    response = harness.client.post("/ask?debug=retrieval", json={"question": "top decile wealth"})
    assert response.status_code == 200
    assert len(harness.recorded) == 1
    row = harness.recorded[0]
    assert row["engine"] is _ENGINE_SENTINEL
    assert row["question"] == "top decile wealth"
    assert row["decision"] == QueryDecision.ANSWERED
    # The backlog's core requirement: debug rows carry the REAL embed spend,
    # not zeros (ADR 0002: every model call is metered).
    assert row["tokens_in"] == _EMBED_TOKENS
    assert row["tokens_out"] == 0
    assert row["cost_gbp"] == _EMBED_COST_GBP
    assert isinstance(row["latency_ms"], int)
    assert row["latency_ms"] >= 0


def test_ask_fails_the_request_when_success_accounting_cannot_be_written(
    harness: _Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    # ADR 0002 fail-closed: served-but-unrecorded spend would silently
    # understate the summed cap input, so the request must fail instead.
    def broken_record(engine: Any, **kwargs: Any) -> None:
        raise OperationalError("INSERT ...", {}, Exception("db gone"))

    monkeypatch.setattr(routes, "record_query", broken_record)
    response = harness.client.post("/ask?debug=retrieval", json={"question": "anything"})
    assert response.status_code == 500
    assert response.json()["detail"] == "query accounting failed"


def test_ask_without_debug_is_501_until_composition_lands(harness: _Harness) -> None:
    response = harness.client.post("/ask", json={"question": "anything"})
    assert response.status_code == 501
    assert "H1-18" in response.json()["detail"]
    # Neither retriever ran: plain mode must not spend before it can answer.
    assert harness.calls == {}
    # And nothing ran -> nothing to account: no query_log row.
    assert harness.recorded == []


def test_ask_unknown_debug_value_is_422(harness: _Harness) -> None:
    response = harness.client.post("/ask?debug=everything", json={"question": "anything"})
    assert response.status_code == 422


@pytest.mark.parametrize("question", ["", "   ", "\n\t"])
def test_ask_blank_question_is_422_not_a_paid_embedding_call(harness: _Harness, question: str) -> None:
    response = harness.client.post("/ask?debug=retrieval", json={"question": question})
    assert response.status_code == 422
    # Neither retriever ran (the dense leg would have spent on an embedding).
    assert harness.calls == {}


def test_healthz_ok_when_database_answers(harness: _Harness) -> None:
    class _FakeConn:
        def execute(self, *args: Any, **kwargs: Any) -> None:
            return None

        def __enter__(self) -> _FakeConn:
            return self

        def __exit__(self, *exc: Any) -> bool:
            return False

    class _FakeEngine:
        def connect(self) -> _FakeConn:
            return _FakeConn()

    harness.app.dependency_overrides[get_engine] = lambda: _FakeEngine()
    response = harness.client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_healthz_maps_database_failure_to_503(harness: _Harness) -> None:
    class _BrokenEngine:
        def connect(self) -> Any:
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    harness.app.dependency_overrides[get_engine] = lambda: _BrokenEngine()
    response = harness.client.get("/healthz")
    assert response.status_code == 503
    assert response.json()["detail"] == "database unreachable"


def _configure_startup_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """A complete request-path config: DB URL nobody listens on + dummy provider.

    create_engine pools lazily and get_client makes no network call, so the
    lifespan opens no connection and spends nothing — these stay DB-free.
    """
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://x:x@127.0.0.1:9/analyst")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-never-used")
    monkeypatch.setenv("EMBEDDING_MODEL", "text-embedding-3-small")


def test_lifespan_creates_and_disposes_the_shared_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure_startup_env(monkeypatch)
    disposed: list[Engine] = []
    original_dispose = Engine.dispose

    def spy(self: Engine, close: bool = True) -> None:
        disposed.append(self)
        original_dispose(self, close)

    monkeypatch.setattr(Engine, "dispose", spy)
    app = create_app()
    with TestClient(app):
        engine = app.state.engine
        assert isinstance(engine, Engine)
    assert disposed == [engine]


def test_lifespan_fails_loud_without_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"), TestClient(create_app()):
        pass  # pragma: no cover — startup must raise before we get here


def test_lifespan_fails_loud_without_provider_config(monkeypatch: pytest.MonkeyPatch) -> None:
    # A keyless API would pass /healthz but 500 on every /ask?debug=retrieval
    # (the dense leg embeds per request) — so startup must refuse instead.
    _configure_startup_env(monkeypatch)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"), TestClient(create_app()):
        pass  # pragma: no cover — startup must raise before we get here


def test_retrieval_limits_are_the_h1_14_measurement_basis() -> None:
    # H1-14's recall report is defined against these depths; changing either
    # must be a deliberate, review-visible decision, not a drive-by edit.
    assert routes._PER_RETRIEVER_LIMIT == 50
    assert routes._FUSED_LIMIT == 20


def test_ask_debug_retrieval_truncates_to_the_fused_limit(harness: _Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    # 30 disjoint hits per leg -> 60 fused candidates available; the response
    # must carry exactly _FUSED_LIMIT, so the top-N contract is behavioural,
    # not just a constant.
    lexical = [_hit(i, rank=i, score=1.0 / i) for i in range(1, 31)]
    dense = [_hit(100 + i, rank=i, score=1.0 / i) for i in range(1, 31)]
    monkeypatch.setattr(routes, "search_fts", lambda q, *, limit, engine: lexical)
    monkeypatch.setattr(routes, "search_dense_by_vector", lambda v, *, limit, engine: dense)
    response = harness.client.post("/ask?debug=retrieval", json={"question": "deep corpus"})
    assert response.status_code == 200
    assert len(response.json()["candidates"]) == routes._FUSED_LIMIT


def test_ask_question_with_nul_byte_is_422_not_a_db_error(harness: _Harness) -> None:
    response = harness.client.post("/ask?debug=retrieval", json={"question": "wealth\x00share"})
    assert response.status_code == 422
    assert harness.calls == {}


def test_ask_maps_database_failure_to_503_and_records_an_error_row(
    harness: _Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken_fts(query: str, *, limit: int, engine: Any) -> list[ChunkHit]:
        raise OperationalError("SELECT ...", {}, Exception("connection refused"))

    monkeypatch.setattr(routes, "search_fts", broken_fts)
    response = harness.client.post("/ask?debug=retrieval", json={"question": "anything"})
    assert response.status_code == 503
    assert response.json()["detail"] == "retrieval backend unavailable"
    # The free leg failed first, so the paid embedding call never happened...
    assert "embed" not in harness.calls
    # ...and the failure was still accounted: an `error` row with zero spend.
    assert len(harness.recorded) == 1
    row = harness.recorded[0]
    assert row["decision"] == QueryDecision.ERROR
    assert row["tokens_in"] == 0
    assert row["cost_gbp"] == 0.0


def test_ask_error_row_write_failure_does_not_mask_the_503(harness: _Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    # Realistic double failure: the same outage that broke retrieval also
    # breaks the accounting insert. The caller must still see the 503.
    def broken_fts(query: str, *, limit: int, engine: Any) -> list[ChunkHit]:
        raise OperationalError("SELECT ...", {}, Exception("connection refused"))

    def broken_record(engine: Any, **kwargs: Any) -> None:
        raise OperationalError("INSERT ...", {}, Exception("still down"))

    monkeypatch.setattr(routes, "search_fts", broken_fts)
    monkeypatch.setattr(routes, "record_query", broken_record)
    response = harness.client.post("/ask?debug=retrieval", json={"question": "anything"})
    assert response.status_code == 503
    assert response.json()["detail"] == "retrieval backend unavailable"
