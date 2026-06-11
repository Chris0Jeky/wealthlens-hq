"""The abstention gate: refuse honestly when the corpus can't answer.

When fused retrieval evidence is weak, /ask returns a structured
"cannot answer from this corpus" refusal instead of a generated guess.
Refusal is a visible product feature with its own response schema and its own
deterministic eval check (the 5+ out-of-corpus golden questions MUST refuse).

Gating mechanism: ADR 0003 D4 = threshold on the fused RRF score plus a
min-hits guard (the cheapest mechanism deterministic checks can test),
calibrated against the reviewed golden set in H1-21. The mechanism stays
behind one function so any future change is a swap, not a refactor.

Pending: task H1-21 in tasks/hero1-backlog.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from wealthlens_analyst.retrieval.fts import ChunkHit

# Stable machine-readable reason served in the refusal body.
REFUSAL_REASON_WEAK_EVIDENCE = "cannot_answer_from_corpus"


@dataclass(frozen=True)
class GateDecision:
    """Outcome of the confidence gate for one question."""

    answerable: bool
    # The signal the gate used (fused score / rerank score / judge verdict),
    # logged to query_log so refusal behaviour is auditable.
    signal: float
    reason: str | None  # set when answerable is False


def evaluate_evidence(question: str, evidence: list[ChunkHit]) -> GateDecision:
    """Decide whether the retrieved evidence supports answering at all."""
    raise NotImplementedError("H1-21: abstention gate not yet implemented (ADR 0003 D4: fused-RRF threshold)")
