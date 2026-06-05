"""Tests for ONS housing affordability processed data."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

# Make the pipeline importable without installing it as a package.
PIPELINE_DIR = Path(__file__).resolve().parents[1] / "automation" / "data-pipelines"
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

import fetch_ons_housing  # noqa: E402

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "projects"
    / "wealthlens-dashboard"
    / "data"
    / "processed"
    / "ons_housing_affordability_by_region.csv"
)


def test_output_has_expected_columns():
    df = pd.read_csv(DATA_PATH)
    assert set(df.columns) == {"region", "year", "ratio"}


def test_ratios_are_positive():
    df = pd.read_csv(DATA_PATH)
    assert (df["ratio"] > 0).all(), "All affordability ratios should be positive"


def test_year_range_covers_1997_to_recent():
    df = pd.read_csv(DATA_PATH)
    assert df["year"].min() <= 1997, "Expected data going back to at least 1997"
    assert df["year"].max() >= 2020, "Expected recent data up to at least 2020"


def test_contains_multiple_regions():
    df = pd.read_csv(DATA_PATH)
    regions = df["region"].unique()
    assert len(regions) >= 5, f"Expected at least 5 regions, got {len(regions)}"


def test_london_has_highest_ratios():
    """London should consistently have among the highest affordability ratios."""
    df = pd.read_csv(DATA_PATH)
    mean_by_region = df.groupby("region")["ratio"].mean()
    assert "London" in mean_by_region.index, "London region missing from data"
    assert mean_by_region["London"] == mean_by_region.max(), (
        "London should have the highest mean affordability ratio"
    )


# ---------------------------------------------------------------------------
# Unit tests for _to_finite_float (NaN/inf rejection — same bug class as #361)
# ---------------------------------------------------------------------------


def test_to_finite_float_plain_number() -> None:
    assert fetch_ons_housing._to_finite_float(42) == 42.0
    assert fetch_ons_housing._to_finite_float(4.5) == pytest.approx(4.5)
    assert fetch_ons_housing._to_finite_float("8") == 8.0


def test_to_finite_float_comma_grouped_text() -> None:
    """Comma-grouped spreadsheet text should parse to the grouped value."""
    assert fetch_ons_housing._to_finite_float("14,200") == 14200.0


def test_to_finite_float_nan_returns_none() -> None:
    """A blank cell pandas reads as NaN must be rejected (the #361 bug)."""
    assert fetch_ons_housing._to_finite_float(float("nan")) is None
    assert fetch_ons_housing._to_finite_float("nan") is None


def test_to_finite_float_inf_returns_none() -> None:
    assert fetch_ons_housing._to_finite_float(float("inf")) is None
    assert fetch_ons_housing._to_finite_float(float("-inf")) is None


def test_to_finite_float_empty_string_returns_none() -> None:
    assert fetch_ons_housing._to_finite_float("") is None


def test_to_finite_float_none_returns_none() -> None:
    assert fetch_ons_housing._to_finite_float(None) is None


def test_to_finite_float_non_numeric_returns_none() -> None:
    assert fetch_ons_housing._to_finite_float("not a number") is None
