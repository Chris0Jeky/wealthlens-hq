"""Unit tests for the abstention gate (H1-21, ADR 0003 D4).

Model-free and DB-free: the gate is a pure function over fused RRF scores, so
the threshold + min-hits mechanism is pinned with fixture ChunkHits carrying
explicit scores. Fixtures are built RELATIVE to the module thresholds, so the
tests assert the MECHANISM (weak/thin evidence refuses, strong answers) rather
than a specific calibration — the H1-22 recalibration against the golden set
keeps them green as long as the structural invariants hold.
"""

from __future__ import annotations

import pytest

from wealthlens_analyst.answer import abstain
from wealthlens_analyst.answer.abstain import evaluate_evidence
from wealthlens_analyst.retrieval.fts import ChunkHit

_ABOVE_TOP = abstain._MIN_TOP_SCORE * 1.5  # clears the top-score bar
_BELOW_TOP = abstain._MIN_TOP_SCORE * 0.5  # below the top-score bar
_SUPPORTING = abstain._MIN_HIT_SCORE * 1.01  # clears the supporting-hit bar
_TRIVIAL = abstain._MIN_HIT_SCORE * 0.5  # below the supporting-hit bar


def _hit(score: float, chunk_id: int = 1) -> ChunkHit:
    """A ChunkHit carrying only the fused RRF score the gate reads."""
    return ChunkHit(
        chunk_id=chunk_id,
        source_id="s",
        document_id="d",
        section=None,
        page=None,
        span=None,
        text="t",
        rank=1,
        score=score,
    )


def test_strong_evidence_is_answerable() -> None:
    # A strong top plus enough supporting hits to clear the min-hits guard.
    evidence = [_hit(_ABOVE_TOP, 1)] + [_hit(_SUPPORTING, i) for i in range(2, 2 + abstain._MIN_HITS)]
    decision = evaluate_evidence("q", evidence)
    assert decision.answerable is True
    assert decision.reason is None
    assert decision.signal == _ABOVE_TOP


def test_weak_top_score_refuses() -> None:
    # Many hits, but the strongest is below the top-score bar -> weak evidence.
    evidence = [_hit(_BELOW_TOP, i) for i in range(1, 6)]
    decision = evaluate_evidence("q", evidence)
    assert decision.answerable is False
    assert decision.reason == abstain.REFUSAL_REASON_WEAK_EVIDENCE
    assert decision.signal == _BELOW_TOP


def test_too_few_supporting_hits_refuses() -> None:
    # The top is strong (so this is NOT a top-score refusal) but fewer than
    # _MIN_HITS chunks clear the supporting bar -> thin, uncorroborated evidence.
    clearing = [_hit(_ABOVE_TOP if j == 0 else _SUPPORTING, j + 1) for j in range(abstain._MIN_HITS - 1)]
    filler = [_hit(_TRIVIAL, 90 + j) for j in range(3)]
    decision = evaluate_evidence("q", clearing + filler)
    assert decision.answerable is False
    assert decision.reason == abstain.REFUSAL_REASON_WEAK_EVIDENCE


def test_no_evidence_refuses_with_zero_signal() -> None:
    decision = evaluate_evidence("q", [])
    assert decision.answerable is False
    assert decision.signal == 0.0
    assert decision.reason == abstain.REFUSAL_REASON_WEAK_EVIDENCE


def test_signal_is_the_top_score_regardless_of_list_order() -> None:
    # The gate must not assume the fused list is sorted; the signal is the max.
    evidence = [_hit(_SUPPORTING, 1), _hit(_ABOVE_TOP, 2), _hit(_SUPPORTING, 3)]
    assert evaluate_evidence("q", evidence).signal == _ABOVE_TOP


def test_blank_question_fails_loud() -> None:
    with pytest.raises(ValueError, match="non-blank"):
        evaluate_evidence("   ", [_hit(_ABOVE_TOP)])


def test_threshold_invariants_hold() -> None:
    # Structural invariants the mechanism relies on; the H1-22 recalibration must
    # preserve them (a supporting hit is no stricter than the top bar; >= 1 hit).
    assert 0 < abstain._MIN_HIT_SCORE <= abstain._MIN_TOP_SCORE
    assert abstain._MIN_HITS >= 1
