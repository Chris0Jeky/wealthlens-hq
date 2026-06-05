"""Tests for ONS housing affordability processed data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

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
