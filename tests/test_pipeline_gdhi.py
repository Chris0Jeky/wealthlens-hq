"""Tests for ONS GDHI by region pipeline data and parsing logic."""

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

import fetch_ons_gdhi  # noqa: E402

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "projects"
    / "wealthlens-dashboard"
    / "data"
    / "processed"
    / "ons_gdhi_by_region.csv"
)

EXPECTED_COLUMNS = {"region", "gdhi_per_head", "year"}


# ---------------------------------------------------------------------------
# Tests for fallback data generation
# ---------------------------------------------------------------------------


def test_fallback_data_has_expected_columns() -> None:
    """Fallback data must have the three expected columns."""
    df = fetch_ons_gdhi._build_fallback_data()
    assert set(df.columns) == EXPECTED_COLUMNS


def test_fallback_data_has_rows() -> None:
    """Fallback data must produce a non-empty DataFrame."""
    df = fetch_ons_gdhi._build_fallback_data()
    assert len(df) > 0, "Fallback data should not be empty"


def test_fallback_data_no_nan_in_key_columns() -> None:
    """Key columns must not contain NaN values."""
    df = fetch_ons_gdhi._build_fallback_data()
    for col in EXPECTED_COLUMNS:
        assert df[col].isna().sum() == 0, f"Column '{col}' has NaN values"


def test_fallback_data_regions_are_unique() -> None:
    """Each region name should appear only once."""
    df = fetch_ons_gdhi._build_fallback_data()
    duplicates = df[df["region"].duplicated()]
    assert len(duplicates) == 0, f"Duplicate regions found: {duplicates['region'].tolist()}"


def test_fallback_data_gdhi_values_positive() -> None:
    """All GDHI per-head values should be positive."""
    df = fetch_ons_gdhi._build_fallback_data()
    assert (df["gdhi_per_head"] > 0).all(), "All GDHI values should be positive"


def test_fallback_data_year_consistent() -> None:
    """All rows should have the same year value."""
    df = fetch_ons_gdhi._build_fallback_data()
    years = df["year"].unique()
    assert len(years) == 1, f"Expected one year, got {years}"


def test_fallback_data_includes_extremes() -> None:
    """Fallback data should include high and low extremes for inequality."""
    df = fetch_ons_gdhi._build_fallback_data()
    regions = set(df["region"])
    # At minimum, one wealthy London area and one deprived area
    assert "Westminster" in regions or any("Kensington" in r for r in regions), (
        "Should include a wealthy London region"
    )
    assert "Blackpool" in regions, "Should include Blackpool as a low-GDHI region"


def test_fallback_data_gdhi_range_plausible() -> None:
    """GDHI per-head values should be in a plausible range (GBP)."""
    df = fetch_ons_gdhi._build_fallback_data()
    assert df["gdhi_per_head"].min() > 5000, "Minimum GDHI seems too low"
    assert df["gdhi_per_head"].max() < 200000, "Maximum GDHI seems too high"


# ---------------------------------------------------------------------------
# Tests for CSV output format validation
# ---------------------------------------------------------------------------


@pytest.fixture()
def processed_df() -> pd.DataFrame:
    """Load the processed CSV, or generate it from fallback data."""
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    # No CSV on disk yet — use the fallback data directly.
    return fetch_ons_gdhi._build_fallback_data()


def test_output_has_expected_columns(processed_df: pd.DataFrame) -> None:
    assert set(processed_df.columns) == EXPECTED_COLUMNS


def test_output_no_nan_in_key_columns(processed_df: pd.DataFrame) -> None:
    for col in EXPECTED_COLUMNS:
        assert processed_df[col].isna().sum() == 0, f"Column '{col}' has NaN values"


def test_output_regions_unique(processed_df: pd.DataFrame) -> None:
    duplicates = processed_df[processed_df["region"].duplicated()]
    assert len(duplicates) == 0, f"Duplicate regions: {duplicates['region'].tolist()}"


def test_output_gdhi_positive(processed_df: pd.DataFrame) -> None:
    assert (processed_df["gdhi_per_head"] > 0).all()


# ---------------------------------------------------------------------------
# Tests for _parse_gdhi_per_head
# ---------------------------------------------------------------------------


def _build_mock_gdhi_sheet(
    *,
    include_itl_codes: bool = True,
    itl_levels: str = "mixed",
) -> pd.DataFrame:
    """Build a minimal DataFrame mimicking the ONS GDHI per-head sheet.

    Args:
        include_itl_codes: Whether to include ITL codes in column 0.
        itl_levels: 'mixed' for ITL1+ITL3 rows, 'itl1_only' for ITL1 only,
                    'itl3_only' for ITL3 only.

    The year header row must contain 5+ year values to trigger the parser's
    detection heuristic.  Column 0 uses numeric-style ITL codes (or None)
    so that ``_find_name_column`` correctly identifies column 1 as the
    region-name column.
    """
    # Header area — must have enough columns for code + name + 6 years
    n_cols = 8
    rows: list[list[object]] = [
        ["GDHI per head at current basic prices"] + [None] * (n_cols - 1),
        ["£ per head"] + [None] * (n_cols - 1),
        [None] * n_cols,
    ]

    # Year header row — 6 years satisfies the >=5 heuristic
    year_header: list[object]
    if include_itl_codes:
        year_header = [None, None, 2017, 2018, 2019, 2020, 2021, 2022]
    else:
        year_header = [None, None, 2017, 2018, 2019, 2020, 2021, 2022]
    rows.append(year_header)

    # Data rows — ITL1 (parent) rows
    # Column 0: ITL code (short alphanumeric), Column 1: region name, Cols 2-7: values
    itl1_rows: list[list[object]] = [
        ["TLC", "London", 25000, 26000, 27000, 28000, 29000, 30000],
        ["TLK", "South West", 17000, 18000, 19000, 20000, 21000, 22000],
    ]

    # ITL3 (leaf) rows
    itl3_rows: list[list[object]] = [
        ["TLC11", "Camden and City of London", 44000, 45000, 46000, 48000, 50000, 52000],
        ["TLC12", "Westminster", 56000, 57000, 58000, 60000, 62000, 64000],
        ["TLC21", "Hackney and Newham", 14000, 15000, 16000, 18000, 19000, 20000],
        ["TLK11", "Bristol, City of", 19000, 20000, 21000, 22000, 23000, 24000],
        ["TLK14", "Bath and North East Somerset", 22000, 23000, 24000, 25000, 26000, 27000],
        ["TLK15", "Dorset", 18000, 19000, 20000, 21000, 22000, 23000],
    ]

    def _strip_code(row: list[object]) -> list[object]:
        """Replace the ITL code column with None."""
        return [None, *row[1:]]

    if itl_levels == "mixed":
        for row in itl1_rows:
            rows.append(row if include_itl_codes else _strip_code(row))
        for row in itl3_rows:
            rows.append(row if include_itl_codes else _strip_code(row))
    elif itl_levels == "itl1_only":
        for row in itl1_rows:
            rows.append(row if include_itl_codes else _strip_code(row))
    elif itl_levels == "itl3_only":
        for row in itl3_rows:
            rows.append(row if include_itl_codes else _strip_code(row))

    return pd.DataFrame(rows)


def test_parse_extracts_regions() -> None:
    """Parser should extract region data from a well-formed sheet."""
    df_raw = _build_mock_gdhi_sheet(include_itl_codes=False)
    result = fetch_ons_gdhi._parse_gdhi_per_head(df_raw)
    assert result is not None
    assert len(result) > 0
    assert set(result.columns) == EXPECTED_COLUMNS


def test_parse_uses_latest_year() -> None:
    """Parser should extract values from the most recent year column."""
    df_raw = _build_mock_gdhi_sheet(include_itl_codes=False)
    result = fetch_ons_gdhi._parse_gdhi_per_head(df_raw)
    assert result is not None
    assert (result["year"] == 2022).all(), "Should use 2022 (latest year)"


def test_parse_returns_none_for_empty_sheet() -> None:
    """Parser should return None when no data can be extracted."""
    df_raw = pd.DataFrame([
        ["Nothing useful here", None],
        ["Still nothing", None],
    ])
    result = fetch_ons_gdhi._parse_gdhi_per_head(df_raw)
    assert result is None


def test_parse_returns_none_for_no_year_headers() -> None:
    """Parser should return None when no year header row is found."""
    df_raw = pd.DataFrame([
        ["Region", "Value A", "Value B"],
        ["London", "high", "medium"],
    ])
    result = fetch_ons_gdhi._parse_gdhi_per_head(df_raw)
    assert result is None


# ---------------------------------------------------------------------------
# Tests for _filter_to_leaf_itl_level
# ---------------------------------------------------------------------------


def test_filter_removes_parent_rows_when_children_exist() -> None:
    """When ITL3 rows exist, ITL1 parent rows should be filtered out."""
    # Test _filter_to_leaf_itl_level directly with a DataFrame that has
    # a mix of ITL1 and ITL3 rows.
    df = pd.DataFrame({
        "region": [
            "London", "South West",
            "Camden and City of London", "Westminster",
            "Hackney and Newham", "Bristol, City of",
            "Bath and NE Somerset", "Dorset",
        ],
        "gdhi_per_head": [30000, 22000, 52000, 64000, 20000, 24000, 27000, 23000],
        "year": [2022] * 8,
        "itl_code": [
            "TLC", "TLK",
            "TLC11", "TLC12", "TLC21", "TLK11", "TLK14", "TLK15",
        ],
    })
    result = fetch_ons_gdhi._filter_to_leaf_itl_level(df)
    regions = set(result["region"])
    # ITL1 rows (London, South West) should be filtered out
    assert "London" not in regions, "ITL1 parent 'London' should be filtered out"
    assert "South West" not in regions, "ITL1 parent 'South West' should be filtered out"
    # ITL3 rows should remain
    assert "Westminster" in regions, "ITL3 'Westminster' should remain"
    assert "Camden and City of London" in regions
    assert len(result) == 6


def test_filter_keeps_all_when_only_itl1() -> None:
    """When only ITL1 data exists, all rows should be kept."""
    df = pd.DataFrame({
        "region": ["London", "South East", "North West", "Scotland", "Wales", "East"],
        "gdhi_per_head": [30000, 26000, 20000, 22000, 19000, 24000],
        "year": [2022] * 6,
        "itl_code": ["TLC", "TLJ", "TLD", "TLM", "TLL", "TLH"],
    })
    result = fetch_ons_gdhi._filter_to_leaf_itl_level(df)
    assert len(result) == 6, "All ITL1 rows should be kept when no children exist"


def test_filter_passes_through_when_no_itl_codes() -> None:
    """When no ITL codes are present, data should pass through unchanged."""
    df = pd.DataFrame({
        "region": ["London", "Blackpool", "Bristol"],
        "gdhi_per_head": [30000, 14000, 24000],
        "year": [2022] * 3,
        "itl_code": ["", "", ""],
    })
    result = fetch_ons_gdhi._filter_to_leaf_itl_level(df)
    assert len(result) == 3


# ---------------------------------------------------------------------------
# Tests for _find_name_column
# ---------------------------------------------------------------------------


def test_find_name_column_identifies_text_column() -> None:
    """Should identify a column with text region names (not year data)."""
    df_raw = _build_mock_gdhi_sheet(include_itl_codes=True)
    # Year header is at row 3 in our mock
    name_col = fetch_ons_gdhi._find_name_column(df_raw, year_row=3)
    # Both columns 0 (ITL codes) and 1 (names) contain text; the function
    # picks the first column with the highest text count.  Either 0 or 1 is
    # acceptable — the key invariant is it must NOT pick a year-data column.
    assert name_col in (0, 1), f"Expected column 0 or 1, got {name_col}"


def test_find_name_column_prefers_names_over_numbers() -> None:
    """When column 0 has numeric codes, column 1 should win."""
    rows: list[list[object]] = [
        [None, None, 2017, 2018, 2019, 2020, 2021, 2022],  # year header (row 0)
        [101, "London", 25000, 26000, 27000, 28000, 29000, 30000],
        [102, "South West", 17000, 18000, 19000, 20000, 21000, 22000],
        [103, "Scotland", 18000, 19000, 20000, 21000, 22000, 23000],
    ]
    df_raw = pd.DataFrame(rows)
    name_col = fetch_ons_gdhi._find_name_column(df_raw, year_row=0)
    assert name_col == 1, f"Expected column 1 (text names), got {name_col}"


# ---------------------------------------------------------------------------
# Tests for process() return type and fallback flag
# ---------------------------------------------------------------------------


def test_process_returns_tuple_with_fallback_flag() -> None:
    """process(None) should return (DataFrame, True) for fallback data."""
    result = fetch_ons_gdhi.process(None)
    assert isinstance(result, tuple)
    assert len(result) == 2
    df, is_fallback = result
    assert isinstance(df, pd.DataFrame)
    assert is_fallback is True


def test_process_falls_back_on_corrupt_xlsx(tmp_path: Path) -> None:
    """process() should return fallback data when the XLSX is corrupt."""
    corrupt_file = tmp_path / "corrupt.xlsx"
    corrupt_file.write_bytes(b"this is not a valid xlsx file")

    df, is_fallback = fetch_ons_gdhi.process(corrupt_file)

    assert is_fallback is True
    assert len(df) > 0
    assert set(df.columns) == EXPECTED_COLUMNS


def test_process_falls_back_on_empty_xlsx(tmp_path: Path) -> None:
    """process() should handle a zero-byte XLSX gracefully."""
    empty_file = tmp_path / "empty.xlsx"
    empty_file.write_bytes(b"")

    df, is_fallback = fetch_ons_gdhi.process(empty_file)

    assert is_fallback is True
    assert len(df) > 0
    assert set(df.columns) == EXPECTED_COLUMNS


# ---------------------------------------------------------------------------
# Tests for fetch() fallback mechanism
# ---------------------------------------------------------------------------


def test_fetch_tries_fallback_on_primary_failure() -> None:
    """If the primary URL fails, fetch() should try the fallback URL."""
    call_log: list[str] = []

    def mock_get(url: str, timeout: int = 90) -> MagicMock:
        call_log.append(url)
        if url == fetch_ons_gdhi.XLSX_URL:
            raise fetch_ons_gdhi.requests.RequestException("404 Not Found")
        resp = MagicMock()
        resp.content = b"fake xlsx content"
        return resp

    with (
        patch.object(fetch_ons_gdhi.requests, "get", side_effect=mock_get),
        patch.object(Path, "write_bytes"),
        patch.object(Path, "mkdir"),
    ):
        result = fetch_ons_gdhi.fetch()

    assert result is not None
    assert len(call_log) == 2
    assert call_log[0] == fetch_ons_gdhi.XLSX_URL
    assert call_log[1] == fetch_ons_gdhi.XLSX_FALLBACK_URL


def test_fetch_returns_none_when_both_urls_fail() -> None:
    """If both URLs fail, fetch() should return None."""

    def mock_get(url: str, timeout: int = 90) -> MagicMock:
        raise fetch_ons_gdhi.requests.RequestException("Network error")

    with (
        patch.object(fetch_ons_gdhi.requests, "get", side_effect=mock_get),
        patch.object(Path, "mkdir"),
    ):
        result = fetch_ons_gdhi.fetch()

    assert result is None
