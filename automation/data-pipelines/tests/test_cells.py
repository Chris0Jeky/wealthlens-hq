"""Unit tests for the shared spreadsheet-cell parser ``_cells.to_finite_float``.

This helper was previously copied byte-for-byte into four pipelines; these tests
are the single home for its behaviour now that it lives in one shared module.
"""

from __future__ import annotations

# Add the pipeline dir (this file's grandparent) to sys.path so the hyphenated
# ``automation/data-pipelines`` package's sibling modules import by bare name,
# matching the sibling test files (e.g. test_validate.py).
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _cells import to_finite_float


def test_plain_number() -> None:
    """A float passes through unchanged."""
    assert to_finite_float(14200.0) == 14200.0


def test_plain_int_and_numeric_string() -> None:
    """Ints and plain numeric strings coerce to float."""
    assert to_finite_float(42) == 42.0
    assert to_finite_float("8") == 8.0


def test_comma_grouped_text() -> None:
    """Thousands-separated text parses (the data-integrity reason the helper exists)."""
    assert to_finite_float("14,200") == 14200.0


def test_comma_grouped_text_with_surrounding_whitespace() -> None:
    """Leading/trailing whitespace is stripped before parsing."""
    assert to_finite_float(" 1,234.5 ") == 1234.5


def test_nan_float_returns_none() -> None:
    """A blank cell pandas reads as NaN must be rejected (the #361 bug class):
    ``str(nan) == "nan"`` would otherwise float() back into a NaN."""
    assert to_finite_float(float("nan")) is None


def test_nan_text_returns_none() -> None:
    """The literal text 'nan' must also be rejected, not parsed to a float NaN."""
    assert to_finite_float("nan") is None


def test_positive_infinity_returns_none() -> None:
    assert to_finite_float(float("inf")) is None


def test_negative_infinity_returns_none() -> None:
    assert to_finite_float(float("-inf")) is None


def test_empty_string_returns_none() -> None:
    assert to_finite_float("") is None


def test_none_returns_none() -> None:
    assert to_finite_float(None) is None


def test_non_numeric_string_returns_none() -> None:
    assert to_finite_float("abc") is None
    assert to_finite_float("Source: ONS") is None


def test_negative_number_is_preserved() -> None:
    """A genuine finite negative value is not rejected (callers apply their own
    ``<= 0`` guards downstream); the helper only filters non-finite/non-numeric."""
    assert to_finite_float("-3.5") == pytest.approx(-3.5)


def test_numpy_float_fast_path() -> None:
    """numpy float64 (a float subclass, the usual pandas numeric cell) takes the
    fast path and is behaviour-identical: finite passes through, NaN/inf rejected."""
    np = pytest.importorskip("numpy")
    assert to_finite_float(np.float64(14200.0)) == 14200.0
    assert to_finite_float(np.float64("nan")) is None
    assert to_finite_float(np.float64("inf")) is None


def test_bool_still_rejected() -> None:
    """bool is an int subclass (not float) — it must NOT take the float fast path;
    True/False are not numeric cells and must return None (unchanged behaviour)."""
    assert to_finite_float(True) is None
    assert to_finite_float(False) is None
