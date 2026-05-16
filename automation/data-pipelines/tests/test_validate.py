"""Tests for the data validation script."""

from __future__ import annotations

# Add parent to path so we can import validate
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validate import CHECKS, validate_all


class TestValidateAll:
    """Test validate_all against synthetic data."""

    def test_missing_file_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        errors = validate_all()
        assert any("MISSING" in e for e in errors)

    def test_empty_file_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        csv_file = tmp_path / CHECKS[0]["file"]
        csv_file.write_text(",".join(CHECKS[0]["columns"]) + "\n")
        errors = validate_all()
        assert any("EMPTY" in e for e in errors)

    def test_missing_columns_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        csv_file = tmp_path / CHECKS[0]["file"]
        csv_file.write_text("wrong_col\n" + "\n".join(["x"] * 100))
        errors = validate_all()
        assert any("COLUMNS" in e for e in errors)

    def test_too_few_rows_reported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        check = CHECKS[0]
        header = ",".join(check["columns"])
        row = ",".join(["x"] * len(check["columns"]))
        csv_file = tmp_path / check["file"]
        csv_file.write_text(header + "\n" + row + "\n")
        errors = validate_all()
        assert any("ROWS" in e for e in errors)

    def test_valid_file_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("validate.DATA_DIR", tmp_path)
        for check in CHECKS:
            header = ",".join(check["columns"])
            row = ",".join(["1"] * len(check["columns"]))
            rows = "\n".join([row] * max(check["min_rows"], 200))
            csv_file = tmp_path / check["file"]
            csv_file.write_text(header + "\n" + rows + "\n")
        errors = validate_all()
        assert errors == []
