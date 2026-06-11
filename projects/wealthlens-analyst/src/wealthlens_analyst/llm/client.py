"""The thin LLM client seam — the ONLY module that touches provider SDKs.

ADR 0002: one Protocol, concrete implementations behind it, token/cost
accounting included in every result so the budget middleware and the public
metrics page never depend on a provider's shape. When Hero #2 lands, a
gateway-backed implementation replaces AnthropicClient without touching any
call site.

Provider SDK imports happen INSIDE methods (lazy), so importing this module —
and everything above it — never requires provider credentials.

Pending: concrete implementations land with H1-11 (embed) and H1-18 (complete).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CompletionResult:
    """A model completion plus the accounting the budget layer requires."""

    text: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_gbp: float


@dataclass(frozen=True)
class EmbeddingResult:
    """Embeddings plus accounting. Vectors are row-aligned with the input texts."""

    vectors: list[list[float]]
    model: str
    tokens_in: int
    cost_gbp: float


class LLMClient(Protocol):
    """What the rest of the service is allowed to know about model providers.

    Implementations MUST fill in real token counts and cost — the hard spend
    cap (budget/middleware.py) and the metrics page are computed from these.
    """

    def complete(self, *, system: str, prompt: str, max_tokens: int) -> CompletionResult:
        """Run one generation call."""
        ...

    def embed(self, texts: list[str]) -> EmbeddingResult:
        """Embed a batch of texts with the configured embedding model."""
        ...


class AnthropicClient:
    """Concrete provider implementation: Anthropic for generation.

    Embeddings (ADR 0003 D2) come from OpenAI (text-embedding-3-small), a
    different vendor — it gets its own class here and the composition stays
    behind get_client(). Model ids come from configuration (ANALYST_MODEL /
    EMBEDDING_MODEL), never hard-coded.
    """

    def __init__(self, *, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def complete(self, *, system: str, prompt: str, max_tokens: int) -> CompletionResult:
        """Implemented in H1-18 (lazy `import anthropic` lives here)."""
        raise NotImplementedError("H1-18: Anthropic completion not yet implemented")

    def embed(self, texts: list[str]) -> EmbeddingResult:
        """Implemented in H1-11 once ADR 0003 fixes the embedding provider."""
        raise NotImplementedError("H1-11: embeddings not yet implemented (ADR 0003 D2: text-embedding-3-small)")


def get_client() -> LLMClient:
    """Return the configured client. The single composition point for the seam."""
    raise NotImplementedError("H1-11/H1-18: client wiring not yet implemented")
