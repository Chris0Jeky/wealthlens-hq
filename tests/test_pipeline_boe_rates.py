"""Tests for Bank of England rates pipeline processed data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "projects"
    / "wealthlens-dashboard"
    / "data"
    / "processed"
    / "boe_rates.csv"
)


@pytest.fixture()
def df() -> pd.DataFrame:
    """Load the processed BoE rates CSV."""
    if not DATA_PATH.exists():
        pytest.skip("boe_rates.csv not found — run the pipeline first")
    return pd.read_csv(DATA_PATH)


def test_output_has_expected_columns(df: pd.DataFrame) -> None:
    """Processed CSV must have date and bank_rate columns at minimum."""
    assert "date" in df.columns
    assert "bank_rate" in df.columns


def test_bank_rate_in_plausible_range(df: pd.DataFrame) -> None:
    """Bank Rate should be between 0% and 20% (historical UK range)."""
    rates = df["bank_rate"].dropna()
    assert (rates >= 0).all(), "Bank Rate should not be negative"
    assert (rates <= 20).all(), "Bank Rate above 20% is implausible for modern UK"


def test_cpi_in_plausible_range(df: pd.DataFrame) -> None:
    """CPI annual rate should be between -5% and 15% for modern UK data."""
    if "cpi_annual" not in df.columns:
        pytest.skip("cpi_annual column not present")
    cpi = df["cpi_annual"].dropna()
    if cpi.empty:
        pytest.skip("No CPI data present")
    assert (cpi >= -5).all(), "CPI below -5% is implausible"
    assert (cpi <= 15).all(), "CPI above 15% is implausible for 2000+ UK data"


def test_dates_are_parseable(df: pd.DataFrame) -> None:
    """All dates should be parseable as ISO dates."""
    dates = pd.to_datetime(df["date"], format="mixed")
    assert not dates.isna().any(), "Some dates failed to parse"


def test_has_sufficient_rows(df: pd.DataFrame) -> None:
    """Should have at least 10 data points (even fallback has ~33)."""
    assert len(df) >= 10, f"Expected >= 10 rows, got {len(df)}"


def test_dates_are_sorted(df: pd.DataFrame) -> None:
    """Dates should be in ascending order."""
    dates = pd.to_datetime(df["date"], format="mixed")
    assert dates.is_monotonic_increasing, "Dates should be sorted ascending"


def test_no_fully_null_rows(df: pd.DataFrame) -> None:
    """No rows should be completely null."""
    null_rows = df.isnull().all(axis=1).sum()
    assert null_rows == 0, f"Found {null_rows} fully-null rows"
