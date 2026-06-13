"""Scaffolding smoke tests: every stub module imports cleanly.

This is the M0 guarantee — the package skeleton is importable (so the CI job,
mypy, and future tasks build on a sound base) while pending logic raises
NotImplementedError rather than silently doing nothing.
"""

from __future__ import annotations

import pytest


def test_package_imports() -> None:
    """All modules import without side effects or missing dependencies."""
    import wealthlens_analyst
    import wealthlens_analyst.answer.abstain
    import wealthlens_analyst.answer.citations
    import wealthlens_analyst.answer.compose
    import wealthlens_analyst.api.app
    import wealthlens_analyst.api.routes
    import wealthlens_analyst.budget.middleware
    import wealthlens_analyst.budget.models
    import wealthlens_analyst.config
    import wealthlens_analyst.ingest.fetch_documents
    import wealthlens_analyst.ingest.slice_corpus
    import wealthlens_analyst.llm.client
    import wealthlens_analyst.retrieval.dense
    import wealthlens_analyst.retrieval.fts
    import wealthlens_analyst.retrieval.fuse_rrf
    import wealthlens_analyst.retrieval.rerank

    assert wealthlens_analyst.__version__


def test_app_factory_and_healthz() -> None:
    """The FastAPI app builds and the liveness route answers."""
    from fastapi.testclient import TestClient

    from wealthlens_analyst.api.app import create_app

    client = TestClient(create_app())
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_pending_stubs_raise_not_implemented() -> None:
    """Pending seams fail loudly, not silently (repo rule: no silent failures).

    fuse_rrf (H1-12) is now implemented, so it is no longer asserted here — its
    behaviour is pinned by tests/test_fuse_rrf.py.
    """
    from wealthlens_analyst.llm.client import get_client

    with pytest.raises(NotImplementedError):
        get_client()


def test_budget_config_fail_closed_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """No BUDGET_MONTHLY_CAP_GBP in the environment -> cap is None (blocked)."""
    from wealthlens_analyst.config import load_settings

    monkeypatch.delenv("BUDGET_MONTHLY_CAP_GBP", raising=False)
    assert load_settings().budget_monthly_cap_gbp is None

    monkeypatch.setenv("BUDGET_MONTHLY_CAP_GBP", "10.00")
    assert load_settings().budget_monthly_cap_gbp == 10.0

    # A malformed cap fails LOUDLY at startup — never silently unguarded.
    monkeypatch.setenv("BUDGET_MONTHLY_CAP_GBP", "ten pounds")
    with pytest.raises(ValueError, match="BUDGET_MONTHLY_CAP_GBP"):
        load_settings()
