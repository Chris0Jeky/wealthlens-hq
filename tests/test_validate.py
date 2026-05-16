"""Tests for the data validation pipeline.

Unit tests for ``validate_all()`` in ``automation/data-pipelines/validate.py``.
Every test mocks the filesystem and ``pd.read_csv`` so no real CSV files are
needed.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

# The module lives in a directory with a hyphen, so we manipulate sys.path
# rather than using a normal import.
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "automation" / "data-pipelines"),
)

import validate
from validate import validate_all

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# A single-check config used by most tests.  Keeps assertions focused on one
# file at a time.
SINGLE_CHECK: list[dict] = [
    {
        "file": "test_data.csv",
        "columns": {"col_a", "col_b", "col_c"},
        "min_rows": 5,
    },
]


def _make_df(rows: int = 10, columns: list[str] | None = None) -> pd.DataFrame:
    """Return a well-formed DataFrame that passes every current check."""
    cols = columns or ["col_a", "col_b", "col_c"]
    return pd.DataFrame(
        {c: range(rows) for c in cols},
    )


# ---------------------------------------------------------------------------
# 1. Missing file detection
# ---------------------------------------------------------------------------


class TestMissingFile:
    """MISSING error when a CSV does not exist on disk."""

    @patch.object(validate, "CHECKS", SINGLE_CHECK)
    def test_missing_file_emits_error(self):
        with patch.object(Path, "exists", return_value=False):
            errors = validate_all()

        assert len(errors) == 1
        assert errors[0].startswith("MISSING:")
        assert "test_data.csv" in errors[0]


# ---------------------------------------------------------------------------
# 2. Missing columns
# ---------------------------------------------------------------------------


class TestMissingColumns:
    """COLUMNS error when required columns are absent."""

    @patch.object(validate, "CHECKS", SINGLE_CHECK)
    def test_missing_columns_emits_error(self):
        # DataFrame has col_a only -- col_b and col_c are missing.
        bad_df = pd.DataFrame({"col_a": [1, 2, 3, 4, 5, 6]})

        with (
            patch.object(Path, "exists", return_value=True),
            patch("validate.pd.read_csv", return_value=bad_df),
        ):
            errors = validate_all()

        col_errors = [e for e in errors if e.startswith("COLUMNS:")]
        assert len(col_errors) == 1
        assert "col_b" in col_errors[0] or "col_c" in col_errors[0]

    @patch.object(validate, "CHECKS", SINGLE_CHECK)
    def test_missing_columns_still_checks_row_count(self):
        """Even when columns are wrong, downstream checks still run."""
        # Only 2 rows (below min_rows=5) AND missing columns.
        bad_df = pd.DataFrame({"col_a": [1, 2]})

        with (
            patch.object(Path, "exists", return_value=True),
            patch("validate.pd.read_csv", return_value=bad_df),
        ):
            errors = validate_all()

        tags = {e.split(":")[0] for e in errors}
        assert "COLUMNS" in tags
        assert "ROWS" in tags


# ---------------------------------------------------------------------------
# 3. Row count below minimum
# ---------------------------------------------------------------------------


class TestRowCount:
    """ROWS error when the DataFrame has fewer rows than min_rows."""

    @patch.object(validate, "CHECKS", SINGLE_CHECK)
    def test_too_few_rows_emits_error(self):
        # min_rows=5, we supply 3
        small_df = _make_df(rows=3)

        with (
            patch.object(Path, "exists", return_value=True),
            patch("validate.pd.read_csv", return_value=small_df),
        ):
            errors = validate_all()

        row_errors = [e for e in errors if e.startswith("ROWS:")]
        assert len(row_errors) == 1
        assert "3 rows" in row_errors[0]
        assert ">= 5" in row_errors[0]

    @patch.object(validate, "CHECKS", SINGLE_CHECK)
    def test_exact_min_rows_passes(self):
        """Exactly min_rows should NOT trigger an error."""
        df = _make_df(rows=5)

        with (
            patch.object(Path, "exists", return_value=True),
            patch("validate.pd.read_csv", return_value=df),
        ):
            errors = validate_all()

        row_errors = [e for e in errors if e.startswith("ROWS:")]
        assert row_errors == []


# ---------------------------------------------------------------------------
# 4. Fully-null row detection
# ---------------------------------------------------------------------------


class TestNullDetection:
    """NULLS error when rows are entirely null."""

    @patch.object(validate, "CHECKS", SINGLE_CHECK)
    def test_fully_null_rows_emit_error(self):
        df = _make_df(rows=6)
        # Append two fully-null rows.
        null_rows = pd.DataFrame(
            {c: [None, None] for c in df.columns},
        )
        df = pd.concat([df, null_rows], ignore_index=True)

        with (
            patch.object(Path, "exists", return_value=True),
            patch("validate.pd.read_csv", return_value=df),
        ):
            errors = validate_all()

        null_errors = [e for e in errors if e.startswith("NULLS:")]
        assert len(null_errors) == 1
        assert "2 fully-null rows" in null_errors[0]

    @patch.object(validate, "CHECKS", SINGLE_CHECK)
    def test_partial_null_row_not_flagged(self):
        """A row with some nulls but not all should NOT trigger NULLS."""
        df = _make_df(rows=6)
        # Set only one column to None on a row.
        df.loc[0, "col_a"] = None

        with (
            patch.object(Path, "exists", return_value=True),
            patch("validate.pd.read_csv", return_value=df),
        ):
            errors = validate_all()

        null_errors = [e for e in errors if e.startswith("NULLS:")]
        assert null_errors == []


# ---------------------------------------------------------------------------
# 5. Empty DataFrame
# ---------------------------------------------------------------------------


class TestEmptyDataFrame:
    """EMPTY error for a zero-row DataFrame."""

    @patch.object(validate, "CHECKS", SINGLE_CHECK)
    def test_empty_df_emits_error(self):
        empty_df = pd.DataFrame(columns=["col_a", "col_b", "col_c"])

        with (
            patch.object(Path, "exists", return_value=True),
            patch("validate.pd.read_csv", return_value=empty_df),
        ):
            errors = validate_all()

        assert len(errors) == 1
        assert errors[0].startswith("EMPTY:")
        assert "test_data.csv" in errors[0]

    @patch.object(validate, "CHECKS", SINGLE_CHECK)
    def test_empty_df_skips_downstream_checks(self):
        """After EMPTY, no COLUMNS / ROWS / NULLS errors should appear."""
        empty_df = pd.DataFrame(columns=["col_a", "col_b", "col_c"])

        with (
            patch.object(Path, "exists", return_value=True),
            patch("validate.pd.read_csv", return_value=empty_df),
        ):
            errors = validate_all()

        tags = {e.split(":")[0] for e in errors}
        assert tags == {"EMPTY"}


# ---------------------------------------------------------------------------
# 6. Clean data -- zero errors
# ---------------------------------------------------------------------------


class TestCleanData:
    """A well-formed DataFrame produces zero errors."""

    @patch.object(validate, "CHECKS", SINGLE_CHECK)
    def test_clean_data_passes(self):
        df = _make_df(rows=10)

        with (
            patch.object(Path, "exists", return_value=True),
            patch("validate.pd.read_csv", return_value=df),
        ):
            errors = validate_all()

        assert errors == []


# ---------------------------------------------------------------------------
# 7. Multiple checks run independently
# ---------------------------------------------------------------------------


class TestMultipleChecks:
    """Each entry in CHECKS is validated independently."""

    def test_one_missing_one_valid(self):
        two_checks = [
            {
                "file": "missing.csv",
                "columns": {"x"},
                "min_rows": 1,
            },
            {
                "file": "good.csv",
                "columns": {"x", "y"},
                "min_rows": 1,
            },
        ]
        good_df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})

        def fake_exists(self_path):
            return "good.csv" in str(self_path)

        with (
            patch.object(validate, "CHECKS", two_checks),
            patch.object(Path, "exists", fake_exists),
            patch("validate.pd.read_csv", return_value=good_df),
        ):
            errors = validate_all()

        assert len(errors) == 1
        assert errors[0].startswith("MISSING:")
        assert "missing.csv" in errors[0]


# ---------------------------------------------------------------------------
# 8. Missing file stops further checks for that file
# ---------------------------------------------------------------------------


class TestMissingFileSkipsDownstream:
    """When a file is missing, no COLUMNS / ROWS / NULLS errors appear."""

    @patch.object(validate, "CHECKS", SINGLE_CHECK)
    def test_missing_file_only_emits_missing(self):
        with patch.object(Path, "exists", return_value=False):
            errors = validate_all()

        tags = {e.split(":")[0] for e in errors}
        assert tags == {"MISSING"}


# ---------------------------------------------------------------------------
# 9. All real CHECKS entries are well-formed
# ---------------------------------------------------------------------------


class TestChecksIntegrity:
    """Verify the CHECKS constant itself is structurally valid."""

    def test_checks_is_non_empty_list(self):
        assert isinstance(validate.CHECKS, list)
        assert len(validate.CHECKS) > 0

    @pytest.mark.parametrize("check", validate.CHECKS)
    def test_check_has_required_keys(self, check):
        assert "file" in check
        assert "columns" in check
        assert "min_rows" in check

    @pytest.mark.parametrize("check", validate.CHECKS)
    def test_columns_is_set_of_strings(self, check):
        assert isinstance(check["columns"], set)
        for col in check["columns"]:
            assert isinstance(col, str)

    @pytest.mark.parametrize("check", validate.CHECKS)
    def test_min_rows_is_positive_int(self, check):
        assert isinstance(check["min_rows"], int)
        assert check["min_rows"] > 0
