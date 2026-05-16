"""Shared test fixtures for the WealthLens backend test suite."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture()
def pipeline_module(tmp_path: Path) -> ModuleType:
    """Import the fetch_productivity_pay pipeline module.

    Adds the automation/data-pipelines directory to sys.path temporarily
    so the module can be imported even though it lives outside the
    backend package.  Also patches PROCESSED_DIR to use a temp directory
    so tests don't write to the real data folder.
    """
    repo_root = Path(__file__).resolve().parents[4]
    pipeline_dir = repo_root / "automation" / "data-pipelines"

    # Temporarily add pipeline dir to sys.path
    sys_path_entry = str(pipeline_dir)
    if sys_path_entry not in sys.path:
        sys.path.insert(0, sys_path_entry)

    # Import (or reload) the module
    if "fetch_productivity_pay" in sys.modules:
        mod = importlib.reload(sys.modules["fetch_productivity_pay"])
    else:
        mod = importlib.import_module("fetch_productivity_pay")

    # Patch PROCESSED_DIR to a temp directory so tests don't touch real data
    mod.PROCESSED_DIR = tmp_path  # type: ignore[attr-defined]

    return mod
