"""Tests for ONS wealth by decile processed data and parsing logic."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# Make the pipeline importable without installing it as a package.
PIPELINE_DIR = Path(__file__).resolve().parents[1] / "automation" / "data-pipelines"
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

import fetch_ons_wealth  # noqa: E402

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "projects"
    / "wealthlens-dashboard"
    / "data"
    / "processed"
    / "ons_wealth_by_decile.csv"
)


# ---------------------------------------------------------------------------
# Tests against the processed CSV (integration-level)
# ---------------------------------------------------------------------------


@pytest.fixture()
def processed_df() -> pd.DataFrame:
    """Load the processed CSV, or generate it from fallback data."""
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    # No CSV on disk yet — use the fallback data directly.
    return fetch_ons_wealth._build_fallback_data()


def test_output_has_expected_columns(processed_df: pd.DataFrame) -> None:
    assert set(processed_df.columns) == {"decile", "total_wealth_bn"}


def test_has_ten_deciles(processed_df: pd.DataFrame) -> None:
    assert len(processed_df) == 10, f"Expected 10 deciles, got {len(processed_df)}"


def test_top_decile_is_largest(processed_df: pd.DataFrame) -> None:
    max_idx = processed_df["total_wealth_bn"].idxmax()
    # .loc returns a dynamically-typed pandas Scalar; the decile label is a string,
    # so str()-coerce it to make the membership test valid (no-op at runtime).
    assert "10th" in str(processed_df.loc[max_idx, "decile"]), (
        "Top decile should hold the most wealth"
    )


def test_total_wealth_is_plausible(processed_df: pd.DataFrame) -> None:
    """Total UK household wealth should be in a plausible range (trillions)."""
    total = processed_df["total_wealth_bn"].sum()
    assert 5000 < total < 20000, f"Total wealth £{total}bn seems implausible"


def test_bottom_decile_exists(processed_df: pd.DataFrame) -> None:
    """The poorest decile row should exist."""
    bottom = processed_df[processed_df["decile"].str.contains("1st")]
    assert len(bottom) == 1, "Should have exactly one bottom decile row"


# ---------------------------------------------------------------------------
# Unit tests for fallback data
# ---------------------------------------------------------------------------


def test_fallback_data_structure() -> None:
    df = fetch_ons_wealth._build_fallback_data()
    assert set(df.columns) == {"decile", "total_wealth_bn"}
    assert len(df) == 10


def test_fallback_data_values_match_ons() -> None:
    """Fallback values should match the April 2020-March 2022 ONS figures."""
    df = fetch_ons_wealth._build_fallback_data()
    # Top decile from Table 2.2: 5,523,204 millions = 5523.2 bn
    assert df.iloc[-1]["total_wealth_bn"] == pytest.approx(5523.2, abs=0.1)
    # Bottom decile: 13,897 millions = 13.9 bn
    assert df.iloc[0]["total_wealth_bn"] == pytest.approx(13.9, abs=0.1)


# ---------------------------------------------------------------------------
# Unit tests for _to_finite_float (NaN/inf rejection — same bug class as #361)
# ---------------------------------------------------------------------------


def test_to_finite_float_plain_number() -> None:
    assert fetch_ons_wealth._to_finite_float(42) == 42.0
    assert fetch_ons_wealth._to_finite_float(13.9) == pytest.approx(13.9)
    assert fetch_ons_wealth._to_finite_float("100") == 100.0


def test_to_finite_float_comma_grouped_text() -> None:
    """Comma-grouped spreadsheet text should parse to the grouped value."""
    assert fetch_ons_wealth._to_finite_float("14,200") == 14200.0


def test_to_finite_float_nan_returns_none() -> None:
    """A blank cell pandas reads as NaN must be rejected (the #361 bug)."""
    assert fetch_ons_wealth._to_finite_float(float("nan")) is None
    assert fetch_ons_wealth._to_finite_float("nan") is None


def test_to_finite_float_inf_returns_none() -> None:
    assert fetch_ons_wealth._to_finite_float(float("inf")) is None
    assert fetch_ons_wealth._to_finite_float(float("-inf")) is None


def test_to_finite_float_empty_string_returns_none() -> None:
    assert fetch_ons_wealth._to_finite_float("") is None


def test_to_finite_float_none_returns_none() -> None:
    assert fetch_ons_wealth._to_finite_float(None) is None


def test_to_finite_float_non_numeric_returns_none() -> None:
    assert fetch_ons_wealth._to_finite_float("not a number") is None


# ---------------------------------------------------------------------------
# Unit tests for _shorten_decile_label
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "label, expected",
    [
        ("Total Wealth Decile 1 (lowest)", "1st (poorest)"),
        ("Total Wealth Decile 2", "2nd"),
        ("Total Wealth Decile 3", "3rd"),
        ("Total Wealth Decile 4", "4th"),
        ("Total Wealth Decile 10 (highest)", "10th (richest)"),
    ],
)
def test_shorten_decile_label(label: str, expected: str) -> None:
    assert fetch_ons_wealth._shorten_decile_label(label) == expected


# ---------------------------------------------------------------------------
# Unit tests for _parse_table_2_2
# ---------------------------------------------------------------------------


def _build_mock_table_2_2() -> pd.DataFrame:
    """Build a minimal DataFrame mimicking Table 2.2 structure."""
    # Row 0: title
    # Row 1: units
    # Row 2: period headers
    # Rows 3-12: aggregate total wealth decile data
    rows = [
        ["Table 2.2: ...", None, None, None],
        ["Great Britain...", "millions", None, None],
        [None, None, "Apr 2018\nto\nMar 2020", "Apr 2020\nto\nMar 2022"],
        ["Aggregate total wealth\n(millions)", "Total Wealth Decile 1 (lowest)", -1372, 13897],
        [None, "Total Wealth Decile 2", 74789, 78424],
        [None, "Total Wealth Decile 3", 193645, 195622],
        [None, "Total Wealth Decile 4", 391138, 392482],
        [None, "Total Wealth Decile 5", 652523, 651950],
        [None, "Total Wealth Decile 6", 969217, 955204],
        [None, "Total Wealth Decile 7", 1380227, 1322966],
        [None, "Total Wealth Decile 8", 1961727, 1805596],
        [None, "Total Wealth Decile 9", 2965899, 2628545],
        [None, "Total Wealth Decile 10 (highest)", 6619170, 5523204],
    ]
    return pd.DataFrame(rows)


def test_parse_table_2_2_extracts_10_deciles() -> None:
    df_raw = _build_mock_table_2_2()
    result = fetch_ons_wealth._parse_table_2_2(df_raw)
    assert result is not None
    assert len(result) == 10


def test_parse_table_2_2_drops_nan_value_cell() -> None:
    """End-to-end: a blank (NaN) decile cell must not leak into the output.

    Locks the call site (not just _to_finite_float): with one decile's latest-column
    value blank, the parser yields 9 valid rows, trips the 'expected 10 deciles'
    guard, and returns None (→ caller falls back to the next parser / vetted
    fallback) rather than emitting a 10-row frame containing a NaN total_wealth_bn.
    """
    df_raw = _build_mock_table_2_2()
    df_raw.iloc[7, 3] = float("nan")  # blank Decile 5's latest-column value
    result = fetch_ons_wealth._parse_table_2_2(df_raw)
    assert result is None, "a NaN decile cell must not produce a NaN-containing result"


def test_parse_table_2_2_uses_latest_column() -> None:
    """Parser should pick values from the last (most recent) column."""
    df_raw = _build_mock_table_2_2()
    result = fetch_ons_wealth._parse_table_2_2(df_raw)
    assert result is not None
    # The last column value for Decile 10 is 5523204 millions = 5523.2 bn
    assert result.iloc[-1]["total_wealth_bn"] == pytest.approx(5523.2, abs=0.1)


def test_parse_table_2_2_converts_millions_to_billions() -> None:
    df_raw = _build_mock_table_2_2()
    result = fetch_ons_wealth._parse_table_2_2(df_raw)
    assert result is not None
    # Decile 1: 13897 millions = 13.9 bn
    assert result.iloc[0]["total_wealth_bn"] == pytest.approx(13.9, abs=0.1)


def test_parse_table_2_2_returns_none_for_unrecognised_layout() -> None:
    df_raw = pd.DataFrame([["Something else", 1, 2], ["No deciles here", 3, 4]])
    result = fetch_ons_wealth._parse_table_2_2(df_raw)
    assert result is None


def test_parse_table_2_2_friendly_labels() -> None:
    df_raw = _build_mock_table_2_2()
    result = fetch_ons_wealth._parse_table_2_2(df_raw)
    assert result is not None
    assert result.iloc[0]["decile"] == "1st (poorest)"
    assert result.iloc[-1]["decile"] == "10th (richest)"
    assert result.iloc[1]["decile"] == "2nd"


def test_parse_table_2_2_skips_trailing_nan_columns() -> None:
    """Parser should skip trailing NaN columns (common openpyxl artefact)."""
    import numpy as np

    df_raw = _build_mock_table_2_2()

    # Append two trailing columns filled with NaN, simulating openpyxl
    # reading empty columns from the XLSX file.
    df_raw[4] = np.nan
    df_raw[5] = np.nan

    result = fetch_ons_wealth._parse_table_2_2(df_raw)
    assert result is not None
    assert len(result) == 10
    # Values should come from column 3 (the last real data column),
    # not from the trailing NaN columns 4 or 5.
    assert result.iloc[-1]["total_wealth_bn"] == pytest.approx(5523.2, abs=0.1)
    assert result.iloc[0]["total_wealth_bn"] == pytest.approx(13.9, abs=0.1)


# ---------------------------------------------------------------------------
# Unit tests for fetch() fallback mechanism
# ---------------------------------------------------------------------------


def test_fetch_tries_fallback_on_primary_failure() -> None:
    """If the primary URL fails, fetch() should try the fallback URL."""
    call_log: list[str] = []

    def mock_get(url: str, **kwargs) -> MagicMock:
        call_log.append(url)
        if url == fetch_ons_wealth.XLSX_URL:
            raise fetch_ons_wealth.requests.RequestException("404 Not Found")
        resp = MagicMock()
        resp.status_code = 200
        resp.content = b"fake xlsx content"
        return resp

    with (
        patch.object(fetch_ons_wealth.requests, "get", side_effect=mock_get),
        patch.object(Path, "write_bytes"),
        patch.object(Path, "mkdir"),
    ):
        result = fetch_ons_wealth.fetch()

    assert result is not None
    assert len(call_log) == 2
    assert call_log[0] == fetch_ons_wealth.XLSX_URL
    assert call_log[1] == fetch_ons_wealth.XLSX_FALLBACK_URL


def test_fetch_returns_none_when_both_urls_fail() -> None:
    """If both URLs fail, fetch() should return None."""

    def mock_get(url: str, **kwargs) -> MagicMock:
        raise fetch_ons_wealth.requests.RequestException("Network error")

    with (
        patch.object(fetch_ons_wealth.requests, "get", side_effect=mock_get),
        patch.object(Path, "mkdir"),
    ):
        result = fetch_ons_wealth.fetch()

    assert result is None


# ---------------------------------------------------------------------------
# Hardening: partial decile data rejection
# ---------------------------------------------------------------------------


def _build_partial_table_2_2(n_deciles: int = 5) -> pd.DataFrame:
    """Build a Table 2.2-like DataFrame with fewer than 10 decile rows."""
    rows: list[list[object]] = [
        ["Table 2.2: ...", None, None, None],
        ["Great Britain...", "millions", None, None],
        [None, None, "Apr 2018\nto\nMar 2020", "Apr 2020\nto\nMar 2022"],
        ["Aggregate total wealth\n(millions)", "Total Wealth Decile 1 (lowest)", -1372, 13897],
    ]
    for i in range(2, n_deciles + 1):
        rows.append([None, f"Total Wealth Decile {i}", 100000 * i, 100000 * i])
    return pd.DataFrame(rows)


def test_parse_table_2_2_rejects_partial_deciles() -> None:
    """Partial decile data (fewer than 10 rows) must return None."""
    df_raw = _build_partial_table_2_2(n_deciles=5)
    result = fetch_ons_wealth._parse_table_2_2(df_raw)
    assert result is None, "Should reject partial decile data (5 rows)"


def test_parse_table_2_2_rejects_nine_deciles() -> None:
    """Edge case: 9 deciles should also be rejected."""
    df_raw = _build_partial_table_2_2(n_deciles=9)
    result = fetch_ons_wealth._parse_table_2_2(df_raw)
    assert result is None, "Should reject partial decile data (9 rows)"


# ---------------------------------------------------------------------------
# Hardening: corrupt XLSX handling in process()
# ---------------------------------------------------------------------------


def test_process_falls_back_on_corrupt_xlsx(tmp_path: Path) -> None:
    """process() should return fallback data when the XLSX is corrupt."""
    corrupt_file = tmp_path / "corrupt.xlsx"
    corrupt_file.write_bytes(b"this is not a valid xlsx file")

    df = fetch_ons_wealth.process(corrupt_file)

    # Should fall back gracefully to the hard-coded data.
    assert len(df) == 10
    assert set(df.columns) == {"decile", "total_wealth_bn"}
    assert "1st (poorest)" in df["decile"].values


def test_process_falls_back_on_truncated_xlsx(tmp_path: Path) -> None:
    """process() should handle a truncated (zero-byte) XLSX gracefully."""
    empty_file = tmp_path / "empty.xlsx"
    empty_file.write_bytes(b"")

    df = fetch_ons_wealth.process(empty_file)

    assert len(df) == 10
    assert set(df.columns) == {"decile", "total_wealth_bn"}
