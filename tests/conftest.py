"""Shared fixtures for WealthLens tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Allow direct imports from automation/analysis/ (e.g. extract_action_items)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation" / "analysis"))


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Create a temporary directory structure matching the project layout."""
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "charts").mkdir(parents=True)
    return tmp_path
