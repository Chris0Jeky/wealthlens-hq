"""Unit tests for citation resolution (H1-19).

DB-free by design (CI has no Postgres): these cover the pure resolution logic
(fabricated / missing / unknown-source stripping, order preservation, and full
provenance + registry name/URL on resolved citations), the row->provenance
mapper, the registry loader's fail-loud guards, and that resolve_citations
short-circuits without opening a connection when no lookup is needed. The SQL
itself and the end-to-end retrieve->compose->resolve chain are verified live
against the analyst-db container (evals/checks/check_citations_live.py), not
here.
"""

from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from wealthlens_analyst.answer.citations import (
    ChunkProvenance,
    Citation,
    ResolvedCitations,
    SourceMeta,
    _provenance_from_rows,
    _resolve_citations,
    load_source_registry,
    resolve_citations,
)
from wealthlens_analyst.answer.compose import ComposedAnswer

_REGISTRY = {
    "ons-was-wealth": SourceMeta(name="ONS Wealth and Assets Survey (WAS)", url="https://ons.example/was"),
    "hmrc-cgt-statistics": SourceMeta(name="HMRC Capital Gains Tax Statistics", url="https://hmrc.example/cgt"),
}


class _ExplodingEngine:
    """Fails if a connection is opened — proves a lookup was short-circuited."""

    def connect(self) -> object:
        raise AssertionError("database connection opened despite no lookup being needed")


def _prov(chunk_id: int, source_id: str = "ons-was-wealth", section: str | None = "sec") -> ChunkProvenance:
    return ChunkProvenance(
        chunk_id=chunk_id, source_id=source_id, document_id=f"doc-{chunk_id}", section=section, page=None
    )


def _answer(cited: list[int], fabricated: list[int] | None = None) -> ComposedAnswer:
    return ComposedAnswer(text="...", cited_chunk_ids=cited, fabricated_chunk_ids=fabricated or [])


# ── pure resolution (_resolve_citations) ──────────────────────────────────────


def test_resolves_cited_id_to_full_citation() -> None:
    """A cited, evidence-grounded id becomes a Citation with DB provenance + registry name/URL."""
    answer = _answer([9118])
    provenance = {9118: ChunkProvenance(9118, "ons-was-wealth", "was-decile", "Decile 10", None)}
    result = _resolve_citations(answer, provenance, _REGISTRY)

    assert result.unresolved_chunk_ids == []
    (citation,) = result.citations
    assert citation == Citation(
        chunk_id=9118,
        source_id="ons-was-wealth",
        source_name="ONS Wealth and Assets Survey (WAS)",
        document_id="was-decile",
        section="Decile 10",
        page=None,
        url="https://ons.example/was",
    )


def test_fabricated_id_is_stripped_and_flagged() -> None:
    """The done-when: a fabricated cited id is caught; only resolved citations remain.

    777 is in fabricated_chunk_ids (compose saw it was not in the evidence), so
    it is dropped WITHOUT a provenance lookup, even though it has no row here.
    """
    answer = _answer(cited=[9118, 777], fabricated=[777])
    provenance = {9118: _prov(9118)}
    result = _resolve_citations(answer, provenance, _REGISTRY)

    assert [c.chunk_id for c in result.citations] == [9118]
    assert result.unresolved_chunk_ids == [777]


def test_missing_from_corpus_is_stripped() -> None:
    """An evidence-grounded id with no chunk row (data anomaly) is stripped, not served."""
    answer = _answer(cited=[9118, 9999])  # 9999 not fabricated, but absent from the corpus
    provenance = {9118: _prov(9118)}
    result = _resolve_citations(answer, provenance, _REGISTRY)

    assert [c.chunk_id for c in result.citations] == [9118]
    assert result.unresolved_chunk_ids == [9999]


def test_unknown_source_is_stripped() -> None:
    """A real chunk whose source is not in the registry cannot be cited (no name/URL)."""
    answer = _answer(cited=[9118])
    provenance = {9118: _prov(9118, source_id="mystery-source")}
    result = _resolve_citations(answer, provenance, _REGISTRY)

    assert result.citations == []
    assert result.unresolved_chunk_ids == [9118]


def test_order_is_first_appearance_for_resolved_and_unresolved() -> None:
    """Both lists follow the answer's cited order, interleaving stripped ids out."""
    answer = _answer(cited=[9140, 777, 9118], fabricated=[777])
    provenance = {9118: _prov(9118), 9140: _prov(9140, source_id="hmrc-cgt-statistics")}
    result = _resolve_citations(answer, provenance, _REGISTRY)

    assert [c.chunk_id for c in result.citations] == [9140, 9118]
    assert [c.source_name for c in result.citations] == [
        "HMRC Capital Gains Tax Statistics",
        "ONS Wealth and Assets Survey (WAS)",
    ]
    assert result.unresolved_chunk_ids == [777]


def test_no_citations_resolves_to_empty() -> None:
    """A refusal (no cited ids) resolves to an empty result."""
    assert _resolve_citations(_answer([]), {}, _REGISTRY) == ResolvedCitations()


def test_fabricated_id_is_logged_loudly(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="wealthlens_analyst.answer.citations"):
        _resolve_citations(_answer(cited=[777], fabricated=[777]), {}, _REGISTRY)
    assert any("777" in record.getMessage() and "fabricated" in record.getMessage() for record in caplog.records)


# ── row -> provenance mapper (_provenance_from_rows) ───────────────────────────


def test_provenance_from_rows_maps_and_coerces_chunk_id() -> None:
    rows = [
        SimpleNamespace(chunk_id=7, source_id="ons-was-wealth", document_id="d", section="s", page=3),
        SimpleNamespace(chunk_id=True, source_id="hmrc-cgt-statistics", document_id="d2", section=None, page=None),
    ]
    provenance = _provenance_from_rows(rows)

    assert set(provenance) == {7, 1}  # True coerces to int 1
    assert isinstance(provenance[1].chunk_id, int)
    assert provenance[7] == ChunkProvenance(7, "ons-was-wealth", "d", "s", 3)
    assert provenance[1].section is None


def test_provenance_from_rows_empty() -> None:
    assert _provenance_from_rows([]) == {}


# ── registry loader (load_source_registry) ────────────────────────────────────


def test_load_source_registry_maps_id_to_name_and_url(tmp_path: Path) -> None:
    registry_file = tmp_path / "sources.yml"
    registry_file.write_text(
        "sources:\n  - id: a\n    name: A source\n    url: https://a\n  - id: b\n    name: B source\n    url: https://b\n",
        encoding="utf-8",
    )
    assert load_source_registry(registry_file) == {
        "a": SourceMeta("A source", "https://a"),
        "b": SourceMeta("B source", "https://b"),
    }


def test_load_source_registry_fails_on_entry_missing_url(tmp_path: Path) -> None:
    registry_file = tmp_path / "sources.yml"
    registry_file.write_text("sources:\n  - id: a\n    name: A source\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing id/name/url"):
        load_source_registry(registry_file)


def test_load_source_registry_fails_without_sources_list(tmp_path: Path) -> None:
    registry_file = tmp_path / "sources.yml"
    registry_file.write_text("not_sources: true\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no top-level 'sources' list"):
        load_source_registry(registry_file)


def test_default_registry_resolves_the_corpus_sources() -> None:
    """The real registries/sources.yml still carries the two frozen-corpus sources.

    Reads the committed file (DB-free): a future rename of these ids would break
    live citation resolution, so couple H1-19 to the registry that ships.
    """
    registry = load_source_registry()
    for source_id in ("ons-was-wealth", "hmrc-cgt-statistics"):
        assert source_id in registry
        assert registry[source_id].name
        assert registry[source_id].url.startswith("http")


# ── resolve_citations short-circuits (no DB when no lookup is needed) ──────────


def test_resolve_citations_uncited_answer_opens_no_connection() -> None:
    result = resolve_citations(_answer([]), engine=_ExplodingEngine(), registry=_REGISTRY)  # type: ignore[arg-type]
    assert result == ResolvedCitations()


def test_resolve_citations_all_fabricated_opens_no_connection() -> None:
    answer = _answer(cited=[777, 888], fabricated=[777, 888])
    result = resolve_citations(answer, engine=_ExplodingEngine(), registry=_REGISTRY)  # type: ignore[arg-type]
    assert result.citations == []
    assert result.unresolved_chunk_ids == [777, 888]


def test_resolve_citations_defaults_registry_from_disk_without_db() -> None:
    """registry=None loads the real file; an all-fabricated answer still needs no DB."""
    answer = _answer(cited=[777], fabricated=[777])
    result = resolve_citations(answer, engine=_ExplodingEngine())  # type: ignore[arg-type]
    assert result.unresolved_chunk_ids == [777]
