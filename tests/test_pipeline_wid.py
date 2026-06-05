"""Tests for WID wealth share processed data."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

# Make the pipeline importable for the process() call-site tests.
PIPELINE_DIR = Path(__file__).resolve().parents[1] / "automation" / "data-pipelines"
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

import fetch_wid_data  # noqa: E402

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


# ---------------------------------------------------------------------------
# Call-site tests for process(): a malformed/NaN point must be dropped, never
# leaked as NaN and never crash with a KeyError (locks the to_finite_float +
# .get() handling against a future refactor reintroducing raw point["v"]).
# ---------------------------------------------------------------------------


def _raw(values: list[dict[str, object]]) -> dict[str, object]:
    """Wrap a list of {y, v} points in the WID API response shape."""
    return {"sptincj992_p99p100": [{"GB": {"meta": {}, "values": values}}]}


@pytest.fixture()
def _isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Redirect process()'s CSV write to a tmp dir so tests never touch the real CSV."""
    monkeypatch.setattr(fetch_wid_data, "PROCESSED_DIR", tmp_path)


@pytest.mark.usefixtures("_isolated")
def test_process_keeps_clean_points() -> None:
    df = fetch_wid_data.process(_raw([{"y": 2000, "v": 0.20}, {"y": 2001, "v": 0.21}]))
    assert set(df["year"]) == {2000, 2001}
    assert df["value"].notna().all()


@pytest.mark.usefixtures("_isolated")
def test_process_drops_nan_and_nonfinite_values() -> None:
    df = fetch_wid_data.process(
        _raw([{"y": 2000, "v": 0.20}, {"y": 2001, "v": float("nan")}, {"y": 2002, "v": float("inf")}])
    )
    assert set(df["year"]) == {2000}, "NaN/inf value points must be dropped"
    assert df["value"].notna().all()


@pytest.mark.usefixtures("_isolated")
def test_process_drops_points_missing_keys_without_crashing() -> None:
    # A point missing "v" or "y" must be dropped gracefully (no KeyError).
    df = fetch_wid_data.process(_raw([{"y": 2000, "v": 0.20}, {"y": 2001}, {"v": 0.22}]))
    assert set(df["year"]) == {2000}


@pytest.mark.usefixtures("_isolated")
def test_process_empty_values_raises_loudly() -> None:
    # All points bad -> empty -> the pipeline fails loud (sys.exit), not a silent empty CSV.
    with pytest.raises(SystemExit):
        fetch_wid_data.process(_raw([{"y": 2001, "v": float("nan")}]))
