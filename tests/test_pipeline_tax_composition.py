"""Tests for the tax composition data pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation" / "data-pipelines"))

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "projects"
    / "wealthlens-dashboard"
    / "data"
    / "processed"
    / "tax_composition.csv"
)


@pytest.fixture()
def df() -> pd.DataFrame:
    """Load the processed tax composition CSV."""
    return pd.read_csv(DATA_PATH)


def test_csv_exists():
    """Processed CSV should exist after pipeline run."""
    assert DATA_PATH.exists(), f"Missing: {DATA_PATH}"


def test_required_columns(df: pd.DataFrame):
    """All expected columns must be present."""
    required = {
        "year", "income_tax_bn", "nics_bn", "cgt_bn", "iht_bn", "sdlt_bn",
        "work_taxes_bn", "wealth_taxes_bn", "total_selected_bn",
        "work_pct", "wealth_pct", "data_source",
    }
    missing = required - set(df.columns)
    assert not missing, f"Missing columns: {missing}"


def test_min_rows(df: pd.DataFrame):
    """At least 3 years of data should be present."""
    assert len(df) >= 3, f"Only {len(df)} rows, expected >= 3"


def test_no_fully_null_rows(df: pd.DataFrame):
    """No row should be entirely null."""
    null_rows = df.isnull().all(axis=1).sum()
    assert null_rows == 0, f"{null_rows} fully-null rows"


def test_work_pct_plus_wealth_pct_near_100(df: pd.DataFrame):
    """Work % and wealth % should sum to ~100% for each year."""
    for _, row in df.iterrows():
        total = row["work_pct"] + row["wealth_pct"]
        assert 99.0 <= total <= 101.0, (
            f"Year {row['year']}: work_pct + wealth_pct = {total}, expected ~100"
        )


def test_work_taxes_dominate(df: pd.DataFrame):
    """Work taxes should be the large majority (>80%) in every year."""
    for _, row in df.iterrows():
        assert row["work_pct"] > 80, (
            f"Year {row['year']}: work_pct = {row['work_pct']}, expected > 80"
        )


def test_wealth_taxes_small_but_nonzero(df: pd.DataFrame):
    """Wealth taxes should be nonzero but small (<20%) in every year."""
    for _, row in df.iterrows():
        assert 0 < row["wealth_pct"] < 20, (
            f"Year {row['year']}: wealth_pct = {row['wealth_pct']}, "
            "expected 0 < x < 20"
        )


def test_individual_tax_amounts_positive(df: pd.DataFrame):
    """All individual tax amounts should be positive."""
    tax_cols = ["income_tax_bn", "nics_bn", "cgt_bn", "iht_bn", "sdlt_bn"]
    for col in tax_cols:
        assert (df[col] > 0).all(), f"{col} has non-positive values"


def test_derived_totals_consistent(df: pd.DataFrame):
    """work_taxes_bn should equal income_tax_bn + nics_bn, etc."""
    for _, row in df.iterrows():
        expected_work = row["income_tax_bn"] + row["nics_bn"]
        assert abs(row["work_taxes_bn"] - expected_work) < 0.1, (
            f"Year {row['year']}: work_taxes_bn mismatch"
        )
        expected_wealth = row["cgt_bn"] + row["iht_bn"] + row["sdlt_bn"]
        assert abs(row["wealth_taxes_bn"] - expected_wealth) < 0.1, (
            f"Year {row['year']}: wealth_taxes_bn mismatch"
        )


def test_data_source_column_valid(df: pd.DataFrame):
    """data_source should be either 'live' or 'illustrative'."""
    valid = {"live", "illustrative"}
    actual = set(df["data_source"].unique())
    assert actual.issubset(valid), f"Invalid data_source values: {actual - valid}"


def test_fallback_data_matches_known_figures():
    """Verify the fallback builder produces expected 2023-24 figures."""
    from fetch_tax_composition import _build_from_fallback

    df = _build_from_fallback()
    latest = df[df["year"] == "2023-24"].iloc[0]
    assert latest["income_tax_bn"] == 270.0
    assert latest["nics_bn"] == 180.0
    assert latest["cgt_bn"] == 15.0
    assert latest["iht_bn"] == 7.5
    assert latest["sdlt_bn"] == 12.0
