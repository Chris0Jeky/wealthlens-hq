"""Unit tests for cited answer composition (H1-18).

Model-free: the client seam is monkeypatched with canned CompletionResults, so
the prompt construction, citation parsing, accounting passthrough and fail-loud
guards are pinned without a network call. The generation itself is verified
LIVE against the local corpus (the backlog's done-when: a live query's
citations are all in the retrieved set).
"""

from __future__ import annotations

import logging

import pytest

import wealthlens_analyst.answer.compose as compose
from wealthlens_analyst.answer.compose import ComposedAnswer, compose_answer
from wealthlens_analyst.llm.client import CompletionResult
from wealthlens_analyst.retrieval.fts import ChunkHit


def _hit(chunk_id: int) -> ChunkHit:
    return ChunkHit(
        chunk_id=chunk_id,
        source_id=f"source-{chunk_id}",
        document_id=f"doc-{chunk_id}",
        section=f"section-{chunk_id}",
        page=None,
        span=f"span-{chunk_id}",
        text=f"evidence text {chunk_id}",
        rank=1,
        score=1.0,
    )


_EVIDENCE = [_hit(9118), _hit(9140)]


class _FakeClient:
    def __init__(self, text: str, calls: dict[str, object]) -> None:
        self._text = text
        self._calls = calls

    def complete(self, *, system: str, prompt: str, max_tokens: int) -> CompletionResult:
        self._calls.update({"system": system, "prompt": prompt, "max_tokens": max_tokens})
        return CompletionResult(
            text=self._text,
            model="fake-model",
            tokens_in=1500,
            tokens_out=200,
            cost_gbp=1.6e-3,
        )


def _compose_with(monkeypatch: pytest.MonkeyPatch, text: str) -> tuple[ComposedAnswer, dict[str, object]]:
    calls: dict[str, object] = {}
    monkeypatch.setattr(compose, "get_client", lambda: _FakeClient(text, calls))
    answer = compose_answer("who holds the most wealth?", _EVIDENCE)
    return answer, calls


def test_prompt_carries_question_and_every_evidence_chunk(monkeypatch: pytest.MonkeyPatch) -> None:
    _, calls = _compose_with(monkeypatch, "answer [chunk:9118]")
    prompt = str(calls["prompt"])
    assert "who holds the most wealth?" in prompt
    # Each chunk appears as the exact marker the model must reuse, with its
    # provenance and verbatim text.
    assert "[chunk:9118] source=source-9118 document=doc-9118 section=section-9118" in prompt
    assert "[chunk:9140] source=source-9140 document=doc-9140 section=section-9140" in prompt
    assert "evidence text 9118" in prompt
    assert "evidence text 9140" in prompt
    # The hard constraints ride in the system message, not the user prompt.
    system = str(calls["system"])
    assert "[chunk:<id>]" in system
    assert calls["max_tokens"] == compose._MAX_ANSWER_TOKENS


def test_citations_parsed_in_first_appearance_order_deduplicated(monkeypatch: pytest.MonkeyPatch) -> None:
    answer, _ = _compose_with(
        monkeypatch,
        "Top decile holds most [chunk:9140]. The distribution is skewed [chunk:9118], "
        "and the top band dominates [chunk:9140].",
    )
    assert answer.cited_chunk_ids == [9140, 9118]


def test_accounting_passes_through_from_the_client(monkeypatch: pytest.MonkeyPatch) -> None:
    answer, _ = _compose_with(monkeypatch, "cited [chunk:9118]")
    assert answer.tokens_in == 1500
    assert answer.tokens_out == 200
    assert answer.cost_gbp == pytest.approx(1.6e-3)
    assert answer.model == "fake-model"


def test_fabricated_citation_is_returned_but_logged_loudly(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # Compose records what the answer CLAIMS (resolution is H1-19), but a
    # citation outside the evidence set is the product's core failure mode
    # and must be visible.
    with caplog.at_level(logging.WARNING, logger="wealthlens_analyst.answer.compose"):
        answer, _ = _compose_with(monkeypatch, "made up [chunk:777] but also real [chunk:9118]")
    assert answer.cited_chunk_ids == [777, 9118]
    assert any("777" in record.getMessage() for record in caplog.records)


def test_empty_evidence_fails_loud(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(compose, "get_client", lambda: _FakeClient("x", {}))
    with pytest.raises(ValueError, match="abstention gate"):
        compose_answer("a question", [])


def test_blank_question_fails_loud(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(compose, "get_client", lambda: _FakeClient("x", {}))
    with pytest.raises(ValueError, match="non-blank"):
        compose_answer("   ", _EVIDENCE)


def test_empty_generation_fails_loud(monkeypatch: pytest.MonkeyPatch) -> None:
    # A reasoning model can burn the whole output budget thinking; an empty
    # "answer" must be an error, not a silently served blank.
    with pytest.raises(RuntimeError, match="empty text"):
        _compose_with(monkeypatch, "   ")
