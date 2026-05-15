"""Tests for ONS wealth by decile processed data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "projects"
    / "wealthlens-dashboard"
    / "data"
    / "processed"
    / "ons_wealth_by_decile.csv"
)


def test_output_has_expected_columns():
    df = pd.read_csv(DATA_PATH)
    assert set(df.columns) == {"decile", "total_wealth_bn"}


def test_has_ten_deciles():
    df = pd.read_csv(DATA_PATH)
    assert len(df) == 10, f"Expected 10 deciles, got {len(df)}"


def test_top_decile_is_largest():
    df = pd.read_csv(DATA_PATH)
    max_idx = df["total_wealth_bn"].idxmax()
    assert "10th" in df.loc[max_idx, "decile"], "Top decile should hold the most wealth"


def test_total_wealth_is_plausible():
    """Total UK household wealth should be in a plausible range (trillions)."""
    df = pd.read_csv(DATA_PATH)
    total = df["total_wealth_bn"].sum()
    assert 5000 < total < 20000, f"Total wealth £{total}bn seems implausible"


def test_bottom_decile_can_be_negative():
    """The poorest decile may have negative net wealth (debt exceeds assets)."""
    df = pd.read_csv(DATA_PATH)
    bottom = df[df["decile"].str.contains("1st")]
    assert len(bottom) == 1, "Should have exactly one bottom decile row"
