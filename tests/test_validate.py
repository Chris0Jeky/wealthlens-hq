"""Tests for the data validation pipeline.

Unit tests for ``validate_all()`` in ``automation/data-pipelines/validate.py``.
Every test mocks the filesystem and ``pd.read_csv`` so no real CSV files are
needed.  The module-level ``CHECKS`` list is overridden per test to isolate
each scenario.

Note: ``validate_all()`` returns ``list[str]`` — a single flat list of error
strings prefixed with MISSING:, EMPTY:, COLUMNS:, ROWS:, or NULLS:.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pandas as pd

# conftest.py adds automation/data-pipelines to sys.path.
import validate
from validate import validate_all

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# A single-check config used by most tests to keep assertions focused.
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
    return pd.DataFrame({c: range(rows) for c in cols})


# ---------------------------------------------------------------------------
# 1. test_missing_file — Path.exists returns False → MISSING error
# ---------------------------------------------------------------------------


@patch.object(validate, "CHECKS", SINGLE_CHECK)
def test_missing_file() -> None:
    """A file that does not exist on disk produces a MISSING error."""
    with patch.object(Path, "exists", return_value=False):
        errors = validate_all()

    assert len(errors) == 1
    assert errors[0].startswith("MISSING:")
    assert "test_data.csv" in errors[0]


# ---------------------------------------------------------------------------
# 2. test_empty_dataframe — pd.read_csv returns empty DataFrame → EMPTY error
# ---------------------------------------------------------------------------


@patch.object(validate, "CHECKS", SINGLE_CHECK)
def test_empty_dataframe() -> None:
    """A zero-row DataFrame produces an EMPTY error."""
    empty_df = pd.DataFrame(columns=["col_a", "col_b", "col_c"])

    with (
        patch.object(Path, "exists", return_value=True),
        patch("validate.pd.read_csv", return_value=empty_df),
    ):
        errors = validate_all()

    assert len(errors) == 1
    assert errors[0].startswith("EMPTY:")
    assert "test_data.csv" in errors[0]


# ---------------------------------------------------------------------------
# 3. test_missing_columns — DataFrame missing required columns → COLUMNS error
# ---------------------------------------------------------------------------


@patch.object(validate, "CHECKS", SINGLE_CHECK)
def test_missing_columns() -> None:
    """A DataFrame that lacks required columns produces a COLUMNS error."""
    # Has col_a only; col_b and col_c are missing.
    bad_df = pd.DataFrame({"col_a": range(6)})

    with (
        patch.object(Path, "exists", return_value=True),
        patch("validate.pd.read_csv", return_value=bad_df),
    ):
        errors = validate_all()

    col_errors = [e for e in errors if e.startswith("COLUMNS:")]
    assert len(col_errors) == 1
    assert "col_b" in col_errors[0] or "col_c" in col_errors[0]


# ---------------------------------------------------------------------------
# 4. test_row_count_below_minimum — fewer rows than min_rows → ROWS error
# ---------------------------------------------------------------------------


@patch.object(validate, "CHECKS", SINGLE_CHECK)
def test_row_count_below_minimum() -> None:
    """A DataFrame with fewer rows than min_rows produces a ROWS error."""
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


# ---------------------------------------------------------------------------
# 5. test_row_count_at_minimum — exactly min_rows → no ROWS error
# ---------------------------------------------------------------------------


@patch.object(validate, "CHECKS", SINGLE_CHECK)
def test_row_count_at_minimum() -> None:
    """Exactly min_rows should NOT trigger a ROWS error."""
    df = _make_df(rows=5)

    with (
        patch.object(Path, "exists", return_value=True),
        patch("validate.pd.read_csv", return_value=df),
    ):
        errors = validate_all()

    row_errors = [e for e in errors if e.startswith("ROWS:")]
    assert row_errors == []


# ---------------------------------------------------------------------------
# 6. test_null_rows_detected — fully-null rows → NULLS error
# ---------------------------------------------------------------------------


@patch.object(validate, "CHECKS", SINGLE_CHECK)
def test_null_rows_detected() -> None:
    """Fully-null rows produce a NULLS error."""
    df = _make_df(rows=6)
    # Append two fully-null rows.
    null_rows = pd.DataFrame({c: [None, None] for c in df.columns})
    df = pd.concat([df, null_rows], ignore_index=True)

    with (
        patch.object(Path, "exists", return_value=True),
        patch("validate.pd.read_csv", return_value=df),
    ):
        errors = validate_all()

    null_errors = [e for e in errors if e.startswith("NULLS:")]
    assert len(null_errors) == 1
    assert "2 fully-null rows" in null_errors[0]


# ---------------------------------------------------------------------------
# 7. test_no_null_rows — no null rows → no NULLS error
# ---------------------------------------------------------------------------


@patch.object(validate, "CHECKS", SINGLE_CHECK)
def test_no_null_rows() -> None:
    """A DataFrame without any null rows produces no NULLS error."""
    df = _make_df(rows=10)

    with (
        patch.object(Path, "exists", return_value=True),
        patch("validate.pd.read_csv", return_value=df),
    ):
        errors = validate_all()

    null_errors = [e for e in errors if e.startswith("NULLS:")]
    assert null_errors == []


# ---------------------------------------------------------------------------
# 8. test_clean_data_passes — well-formed DataFrame → zero errors
# ---------------------------------------------------------------------------


@patch.object(validate, "CHECKS", SINGLE_CHECK)
def test_clean_data_passes() -> None:
    """A well-formed DataFrame produces zero errors."""
    df = _make_df(rows=10)

    with (
        patch.object(Path, "exists", return_value=True),
        patch("validate.pd.read_csv", return_value=df),
    ):
        errors = validate_all()

    assert errors == []


# ---------------------------------------------------------------------------
# 9. test_missing_file_skips_downstream — only MISSING error, nothing else
# ---------------------------------------------------------------------------


@patch.object(validate, "CHECKS", SINGLE_CHECK)
def test_missing_file_skips_downstream() -> None:
    """When a file is missing, only a MISSING error appears (no COLUMNS,
    ROWS, or NULLS errors)."""
    with patch.object(Path, "exists", return_value=False):
        errors = validate_all()

    tags = {e.split(":")[0] for e in errors}
    assert tags == {"MISSING"}


# ---------------------------------------------------------------------------
# 10. test_multiple_checks_independent — each CHECKS entry validated alone
# ---------------------------------------------------------------------------


def test_multiple_checks_independent() -> None:
    """Multiple CHECKS entries are validated independently; a failure in
    one does not affect the other."""
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

    def fake_exists(self_path: Path) -> bool:
        return "good.csv" in str(self_path)

    with (
        patch.object(validate, "CHECKS", two_checks),
        patch.object(Path, "exists", fake_exists),
        patch("validate.pd.read_csv", return_value=good_df),
    ):
        errors = validate_all()

    # Only the missing file should produce an error; the good file passes.
    assert len(errors) == 1
    assert errors[0].startswith("MISSING:")
    assert "missing.csv" in errors[0]
