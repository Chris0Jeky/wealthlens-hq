"""Shared pytest fixtures for the wealthlens-sim test suite."""

from __future__ import annotations

import pytest

from wealthlens_sim.outputs import _source_index


@pytest.fixture(autouse=True)
def _clear_source_index_cache() -> None:
    """Clear the ``sources.yml`` lru_cache around every test.

    ``outputs._source_index`` is process-cached; clearing it before and after each
    test stops cached (or monkeypatched-away) registry state from leaking between
    tests — e.g. the missing-registry degradation test must not poison a later test
    that calls the resolver.
    """
    _source_index.cache_clear()
    yield
    _source_index.cache_clear()
