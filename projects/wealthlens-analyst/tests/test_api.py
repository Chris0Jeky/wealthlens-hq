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


@dataclass
class _Harness:
    """A DB-free app: fixture retriever legs, sentinel engine, recorded calls."""

    client: TestClient
    app: FastAPI
    calls: dict[str, dict[str, Any]] = field(default_factory=dict)


@pytest.fixture()
def harness(monkeypatch: pytest.MonkeyPatch) -> _Harness:
    """Build the app with monkeypatched retrievers and an overridden engine.

    The TestClient is used WITHOUT entering its context manager, so the
    lifespan (real engine creation) never runs — these tests are DB-free.
    """
    calls: dict[str, dict[str, Any]] = {}

    def fake_fts(query: str, *, limit: int, engine: Any) -> list[ChunkHit]:
        calls["fts"] = {"query": query, "limit": limit, "engine": engine}
        return list(_LEXICAL)

    def fake_dense(query: str, *, limit: int, engine: Any) -> list[ChunkHit]:
        calls["dense"] = {"query": query, "limit": limit, "engine": engine}
        return list(_DENSE)

    monkeypatch.setattr(routes, "search_fts", fake_fts)
    monkeypatch.setattr(routes, "search_dense", fake_dense)
    app = create_app()
    app.dependency_overrides[get_engine] = lambda: _ENGINE_SENTINEL
    return _Harness(client=TestClient(app), app=app, calls=calls)


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
    assert harness.calls["dense"]["query"] == "capital gains"
    assert harness.calls["fts"]["limit"] == harness.calls["dense"]["limit"] == routes._PER_RETRIEVER_LIMIT


def test_ask_without_debug_is_501_until_composition_lands(harness: _Harness) -> None:
    response = harness.client.post("/ask", json={"question": "anything"})
    assert response.status_code == 501
    assert "H1-18" in response.json()["detail"]
    # Neither retriever ran: plain mode must not spend before it can answer.
    assert harness.calls == {}


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


def test_lifespan_creates_and_disposes_the_shared_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    # A syntactically valid URL nobody listens on: create_engine pools lazily,
    # so the lifespan opens no connection and this stays DB-free.
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://x:x@127.0.0.1:9/analyst")
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
