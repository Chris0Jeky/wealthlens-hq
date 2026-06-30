"""Unit tests for the LLM client seam (H1-11 embeddings).

DB-free and SDK-free: the OpenAI SDK is faked via sys.modules so the embed
mapping, row-alignment, and cost accounting are pinned without a network call or
the package installed. The live embedding call is verified against the local DB
during ingestion (like the SQL in retrieval/fts.py).
"""

from __future__ import annotations

import sys
import types

import pytest

from wealthlens_analyst.llm.client import (
    EmbeddingResult,
    OpenAIClient,
    embedding_cost_gbp,
    get_client,
)


def test_embedding_cost_known_model() -> None:
    # text-embedding-3-small = $0.02 / 1M tokens, converted at the documented FX.
    assert embedding_cost_gbp("text-embedding-3-small", 1_000_000) == pytest.approx(0.02 * 0.79)
    assert embedding_cost_gbp("text-embedding-3-small", 0) == 0.0


def test_embedding_cost_unknown_model_fails_loud() -> None:
    # An unpriced model must raise, never silently return 0 (the cap depends on cost).
    with pytest.raises(ValueError, match="no price configured"):
        embedding_cost_gbp("text-embedding-9-imaginary", 100)


def _install_fake_openai(monkeypatch: pytest.MonkeyPatch, *, prompt_tokens: int) -> dict[str, object]:
    """Install a fake `openai` module; return a dict capturing the call args."""
    captured: dict[str, object] = {}

    class _Item:
        def __init__(self, embedding: list[float], index: int) -> None:
            self.embedding = embedding
            self.index = index

    class _Usage:
        def __init__(self, tokens: int) -> None:
            self.prompt_tokens = tokens

    class _Response:
        def __init__(self) -> None:
            # Deliberately OUT OF ORDER so the index-sort is exercised.
            self.data = [_Item([0.2] * 1536, 1), _Item([0.1] * 1536, 0)]
            self.usage = _Usage(prompt_tokens)

    class _Embeddings:
        def create(self, *, model: str, input: list[str]) -> _Response:
            captured["model"] = model
            captured["input"] = input
            return _Response()

    class _OpenAI:
        def __init__(self, *, api_key: str) -> None:
            captured["api_key"] = api_key
            self.embeddings = _Embeddings()

    fake = types.ModuleType("openai")
    fake.OpenAI = _OpenAI  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openai", fake)
    return captured


def test_embed_maps_and_aligns_by_index(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = _install_fake_openai(monkeypatch, prompt_tokens=7)
    client = OpenAIClient(api_key="sk-x", embedding_model="text-embedding-3-small", analyst_model="gpt-5.4-mini")

    result = client.embed(["alpha", "beta"])

    assert isinstance(result, EmbeddingResult)
    # Sorted back into input order by item.index: index 0 ([0.1...]) first, index 1 ([0.2...]) second.
    assert result.vectors[0][0] == pytest.approx(0.1)
    assert result.vectors[1][0] == pytest.approx(0.2)
    assert len(result.vectors) == 2
    assert len(result.vectors[0]) == 1536
    assert result.model == "text-embedding-3-small"
    assert result.tokens_in == 7
    assert result.cost_gbp == pytest.approx(7 / 1_000_000 * 0.02 * 0.79)
    # The configured model + key + batched input reached the SDK.
    assert captured["model"] == "text-embedding-3-small"
    assert captured["api_key"] == "sk-x"
    assert captured["input"] == ["alpha", "beta"]


def test_complete_pending_h1_18() -> None:
    client = OpenAIClient(api_key="sk-x", embedding_model="text-embedding-3-small", analyst_model="gpt-5.4-mini")
    with pytest.raises(NotImplementedError, match="H1-18"):
        client.complete(system="s", prompt="p", max_tokens=10)


def test_get_client_builds_openai_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("EMBEDDING_MODEL", "text-embedding-3-small")
    monkeypatch.setenv("ANALYST_MODEL", "gpt-5.4-mini")
    client = get_client()
    assert isinstance(client, OpenAIClient)


def test_get_client_without_key_fails_loud(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("EMBEDDING_MODEL", "text-embedding-3-small")
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        get_client()


def test_get_client_without_embedding_model_fails_loud(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("EMBEDDING_MODEL", raising=False)
    with pytest.raises(RuntimeError, match="EMBEDDING_MODEL"):
        get_client()
