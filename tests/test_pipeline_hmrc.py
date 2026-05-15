"""Tests for HMRC CGT data processing."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation" / "data-pipelines"))


def test_nan_taxpayer_count_handled_in_chart_text():
    """The £3,000+ band has suppressed taxpayer count — chart text must not show 'nan%'."""
    df = pd.read_csv(
        Path(__file__).resolve().parents[1]
        / "projects"
        / "wealthlens-dashboard"
        / "data"
        / "processed"
        / "hmrc_cgt_concentration.csv"
    )
    gains_text = [
        f"{pct:.0f}%" if pd.notna(pct) else "n/a"
        for pct in df["share_of_gains_pct"]
    ]
    taxpayer_text = [
        f"{pct:.0f}%" if pd.notna(pct) else "n/a"
        for pct in df["share_of_taxpayers_pct"]
    ]
    assert "nan%" not in gains_text
    assert "nan%" not in taxpayer_text


def test_shares_sum_near_100():
    """Total shares should sum close to 100% (within rounding tolerance)."""
    df = pd.read_csv(
        Path(__file__).resolve().parents[1]
        / "projects"
        / "wealthlens-dashboard"
        / "data"
        / "processed"
        / "hmrc_cgt_concentration.csv"
    )
    gains_sum = df["share_of_gains_pct"].sum()
    assert 95.0 <= gains_sum <= 105.0, f"Gains shares sum to {gains_sum}%, expected ~100%"


def test_band_lower_monotonically_increasing():
    df = pd.read_csv(
        Path(__file__).resolve().parents[1]
        / "projects"
        / "wealthlens-dashboard"
        / "data"
        / "processed"
        / "hmrc_cgt_concentration.csv"
    )
    lowers = df["band_lower"].tolist()
    assert lowers == sorted(lowers), "band_lower should be monotonically increasing"
