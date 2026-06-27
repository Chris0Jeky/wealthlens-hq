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


# --- live-parse completeness guard (sweep fix) -------------------------------
# process() derives work/wealth totals from ALL FIVE tax columns, so _try_parse_live
# must reject a partial parse (return None -> complete illustrative fallback) rather
# than hand back a DataFrame missing a column (which would KeyError in process()).

_FIXTURE_LABELS_COMPLETE = {
    "income_tax_bn": "Income Tax",
    "nics_bn": "National Insurance contributions",
    "cgt_bn": "Capital Gains Tax",
    "iht_bn": "Inheritance Tax",
    "sdlt_bn": "Stamp Duty Land Tax",
}
# Values in £m (the parser divides by 1000 -> £bn); chosen to land on the fallback bn figures.
_FIXTURE_VALUES_M = {
    "income_tax_bn": [250000, 260000, 270000],
    "nics_bn": [170000, 175000, 180000],
    "cgt_bn": [14000, 14500, 15000],
    "iht_bn": [7000, 7200, 7500],
    "sdlt_bn": [11000, 11500, 12000],
}
_FIXTURE_YEARS = ["2021-22", "2022-23", "2023-24"]


def _write_annual_xlsx(path: Path, labels: dict[str, str]) -> None:
    """Write a minimal HMRC-style 'Annual' sheet: a year header row + one row per
    tax in ``labels`` (column 0 = label, then one £m value per year)."""
    rows: list[list[object]] = [["Tax", *_FIXTURE_YEARS]]
    for key, label in labels.items():
        rows.append([label, *_FIXTURE_VALUES_M[key]])
    pd.DataFrame(rows).to_excel(path, sheet_name="Annual totals", header=False, index=False)


def test_try_parse_live_accepts_a_complete_five_tax_sheet(tmp_path: Path):
    """A complete sheet parses to a frame carrying all five tax columns."""
    from fetch_tax_composition import _try_parse_live

    xlsx = tmp_path / "complete.xlsx"
    _write_annual_xlsx(xlsx, _FIXTURE_LABELS_COMPLETE)
    df = _try_parse_live(xlsx)

    assert df is not None
    assert set(_FIXTURE_LABELS_COMPLETE).issubset(df.columns)  # all 5 present
    latest = df[df["year"] == "2023-24"].iloc[0]
    assert latest["income_tax_bn"] == 270.0  # 270000 £m / 1000
    assert latest["sdlt_bn"] == 12.0


def test_try_parse_live_rejects_an_incomplete_tax_set(tmp_path: Path):
    """A sheet whose IHT/SDLT labels don't match (3 of 5) returns None, NOT a
    column-short frame — so process() falls back instead of raising KeyError."""
    from fetch_tax_composition import _try_parse_live

    partial = {
        "income_tax_bn": "Income Tax",
        "nics_bn": "National Insurance contributions",
        "cgt_bn": "Capital Gains Tax",
        "iht_bn": "Death duties",  # no "inheritance" keyword -> unmatched
        "sdlt_bn": "Property transfer levy",  # no "stamp duty land" keyword -> unmatched
    }
    xlsx = tmp_path / "partial.xlsx"
    _write_annual_xlsx(xlsx, partial)
    assert _try_parse_live(xlsx) is None
