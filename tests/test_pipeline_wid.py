"""Tests for WID wealth share processed data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "projects"
    / "wealthlens-dashboard"
    / "data"
    / "processed"
    / "wid_wealth_shares_gb.csv"
)


def test_output_has_expected_columns():
    df = pd.read_csv(DATA_PATH)
    assert set(df.columns) == {"variable", "country", "year", "value"}


def test_values_are_fractions():
    df = pd.read_csv(DATA_PATH)
    assert (df["value"] >= 0).all()
    assert (df["value"] <= 1).all(), "Values should be fractions, not percentages"


def test_contains_both_percentile_groups():
    df = pd.read_csv(DATA_PATH)
    variables = df["variable"].unique()
    assert any("p99p100" in v for v in variables), "Missing top 1% data"
    assert any("p90p100" in v for v in variables), "Missing top 10% data"


def test_year_range_is_plausible():
    df = pd.read_csv(DATA_PATH)
    assert df["year"].min() <= 1920, "Expected historical data going back before 1920"
    assert df["year"].max() >= 2020, "Expected recent data up to at least 2020"
