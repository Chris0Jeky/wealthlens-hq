"""Compose a cited answer from retrieved evidence.

Generation goes through the LLM client seam (llm/client.py, ADR 0002) — never
a provider SDK directly. The prompt constrains the model to claims supported
by the supplied chunks and to cite chunk ids inline; citations are then
resolved and verified by citations.py before anything reaches the user.

Pending: task H1-18 in tasks/hero1-backlog.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from wealthlens_analyst.retrieval.fts import ChunkHit


@dataclass(frozen=True)
class ComposedAnswer:
    """A generated answer with the chunk ids it claims as evidence."""

    text: str
    cited_chunk_ids: list[int] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0


def compose_answer(question: str, evidence: list[ChunkHit]) -> ComposedAnswer:
    """Generate an answer grounded in `evidence`, citing chunk ids inline.

    Only called AFTER the abstention gate (abstain.py) has decided the
    evidence is strong enough — weak evidence never reaches generation,
    which also keeps refusals free.
    """
    raise NotImplementedError("H1-18: answer composition not yet implemented")
