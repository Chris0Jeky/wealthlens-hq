"""Compose a cited answer from retrieved evidence.

Generation goes through the LLM client seam (llm/client.py, ADR 0002) — never
a provider SDK directly. The prompt constrains the model to claims supported
by the supplied chunks and to cite chunk ids inline; citations are then
resolved and verified by citations.py (H1-19) before anything reaches the
user — compose PARSES what the model claimed, it does not vouch for it.

Task H1-18 in tasks/hero1-backlog.md.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from wealthlens_analyst.llm.client import get_client
from wealthlens_analyst.retrieval.fts import ChunkHit

logger = logging.getLogger(__name__)

#: Inline citation marker the prompt mandates and the parser extracts. One
#: format, defined once — citations.py (H1-19) resolves the same ids.
_CITATION_RE = re.compile(r"\[chunk:(\d+)\]")

#: Output budget per answer. Caps completion tokens INCLUDING the model's
#: reasoning tokens (see client.complete), so it is deliberately generous for
#: what is a short cited paragraph; at gpt-5.4-mini's verified $4.50/1M output
#: price this bounds a single answer at well under a penny.
_MAX_ANSWER_TOKENS = 900

_SYSTEM_PROMPT = """\
You are the WealthLens Analyst: an evidence-backed research analyst over official UK wealth statistics.

Rules — these are hard constraints, not style guidance:
- Use ONLY the numbered evidence chunks supplied in the user message. No outside knowledge, no estimates of your own.
- EVERY factual claim must carry an inline citation of the form [chunk:<id>], where <id> is an id that appears in the evidence. Cite the chunk(s) that directly support each specific claim.
- Preserve figures, units, periods and geographic coverage exactly as the evidence states them (e.g. do not turn "Great Britain" into "the UK", do not re-round).
- If the evidence does not support an answer to the question, say exactly that in one sentence, with no invented figures.
- Be concise: a short paragraph, or a few bullet points for multi-part answers.
"""


@dataclass(frozen=True)
class ComposedAnswer:
    """A generated answer with the chunk ids it claims as evidence."""

    text: str
    cited_chunk_ids: list[int] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    #: Estimated GBP cost of the generation call (from the client's verified
    #: price table), for the query_log row (H1-15) and the cap (H1-27).
    cost_gbp: float = 0.0
    model: str = ""


def _format_evidence(evidence: list[ChunkHit]) -> str:
    """Render evidence chunks as the numbered blocks the system prompt cites.

    Each block leads with the exact ``[chunk:<id>]`` marker the model must
    reuse, followed by the ingestion-time provenance (so the model can weigh
    sources) and the verbatim chunk text.
    """
    blocks = []
    for hit in evidence:
        provenance = f"source={hit.source_id} document={hit.document_id}"
        if hit.section:
            provenance += f" section={hit.section}"
        blocks.append(f"[chunk:{hit.chunk_id}] {provenance}\n{hit.text}")
    return "\n\n".join(blocks)


def _parse_citations(text: str, evidence_ids: set[int]) -> list[int]:
    """Extract cited chunk ids in first-appearance order, deduplicated.

    Ids the model cites that are NOT in the evidence are still returned (the
    dataclass records what the answer CLAIMS; resolution/stripping is
    citations.py's job, H1-19) — but they are logged loudly here, because a
    fabricated citation is exactly the failure mode this product exists to
    make visible.
    """
    cited: list[int] = []
    for match in _CITATION_RE.finditer(text):
        chunk_id = int(match.group(1))
        if chunk_id not in cited:
            cited.append(chunk_id)
    fabricated = [cid for cid in cited if cid not in evidence_ids]
    if fabricated:
        logger.warning("compose: answer cites chunk ids not in the supplied evidence: %s", fabricated)
    return cited


def compose_answer(question: str, evidence: list[ChunkHit]) -> ComposedAnswer:
    """Generate an answer grounded in `evidence`, citing chunk ids inline.

    Only called AFTER the abstention gate (abstain.py, H1-21) has decided the
    evidence is strong enough — weak evidence never reaches generation, which
    also keeps refusals free. Empty evidence is therefore a caller bug and
    fails loudly rather than generating an answer from nothing.
    """
    if not question.strip():
        raise ValueError("compose_answer requires a non-blank question")
    if not evidence:
        raise ValueError(
            "compose_answer requires evidence; the abstention gate (H1-21) must refuse before generation is reached"
        )
    result = get_client().complete(
        system=_SYSTEM_PROMPT,
        prompt=f"Question: {question}\n\nEvidence:\n\n{_format_evidence(evidence)}",
        max_tokens=_MAX_ANSWER_TOKENS,
    )
    # Every generation is a metered spend — visible cost is a product goal.
    logger.info(
        "compose: %s tokens_in=%d tokens_out=%d est. cost GBP %.8f",
        result.model,
        result.tokens_in,
        result.tokens_out,
        result.cost_gbp,
    )
    if not result.text.strip():
        # A busy reasoning model can burn the whole output budget thinking and
        # return nothing; serving an empty "answer" would look like a silent
        # failure to the caller, so fail loudly (spend is still logged above).
        raise RuntimeError(f"generation returned empty text ({result.model}, tokens_out={result.tokens_out})")
    return ComposedAnswer(
        text=result.text,
        cited_chunk_ids=_parse_citations(result.text, {hit.chunk_id for hit in evidence}),
        tokens_in=result.tokens_in,
        tokens_out=result.tokens_out,
        cost_gbp=result.cost_gbp,
        model=result.model,
    )
