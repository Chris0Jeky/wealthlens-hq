"""Tests for the data validation module."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation" / "data-pipelines"))

from validate import validate_all


def test_all_datasets_pass_validation():
    errors = validate_all()
    assert errors == [], f"Validation errors: {errors}"
