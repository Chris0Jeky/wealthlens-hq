"""Call-site regression test for the ONS GDHI ``to_finite_float`` NaN guard.

#365 follow-up. ``fetch_ons_gdhi`` was one of the call sites named as guarded-but-not
yet call-site-tested in ``test_pipeline_finite_cells``. ``process`` extracts the most
recent year's GDHI-per-head value per region with::

    gdhi = to_finite_float(df_raw.iloc[i, latest_col])
    if gdhi is None or gdhi <= 0:
        continue

A blank/NaN/``inf`` cell is a value that a bare ``float()`` would happily accept
(``float("inf")`` and ``float(float("nan"))`` both succeed, and neither is ``<= 0``),
so it would leak a non-finite ``gdhi_per_head`` into the published CSV. ``to_finite_float``
instead returns ``None`` for those cells, so the row is dropped. This is a DROP call
site: there is no legitimate missing value among surviving rows, so the published
``gdhi_per_head`` column must carry no non-finite number at all.

The parse is reached through ``process()``, so we drive it by monkeypatching the two
pandas Excel readers (``pd.ExcelFile`` for sheet discovery, ``pd.read_excel`` for the
sheet body) and pointing ``PROCESSED_DIR`` at a tmp dir. The fake sheet is crafted to
pass year-header detection (a row with >=5 cells in 1990-2030) and name-column
detection (region names in column 1; numeric values elsewhere). Asserting
``is_fallback is False`` proves the live parse ran — a fake that broke detection would
route to the illustrative fallback (which has no non-finite values) and pass vacuously.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fetch_ons_gdhi


def _has_nonfinite(series: pd.Series) -> bool:
    """True if any entry is NaN/None or +/-inf.

    Valid only where surviving rows carry no legitimate missing value (a DROP call
    site) — there a NaN or inf can only be a leak from a bypassed ``to_finite_float``.
    """
    if bool(series.isna().any()):
        return True
    return bool(series.isin([float("inf"), float("-inf")]).any())


class _FakeExcelFile:
    """Stand-in for ``pd.ExcelFile`` exposing only the ``sheet_names`` used.

    ``"Table 3"`` is a direct-name match in ``_find_per_head_sheet``, so sheet
    discovery short-circuits without any further ``read_excel`` peek calls.
    """

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self.sheet_names = ["Table 3"]


def _raw_frame() -> pd.DataFrame:
    """Build a raw ONS-GDHI-style sheet exercising the non-finite-cell scenarios.

    Layout mirrors what ``_parse_gdhi_per_head`` expects:
      * row 0  = a title row (no year cells),
      * row 1  = the year-header row (cells 2018-2023 in cols 2-7),
      * rows 2+ = data rows: col 0 ITL code (left blank so the leaf-ITL filter is
        skipped), col 1 region name, cols 2-7 yearly values.

    The latest year is 2023 (column 7). The bad cells live in that latest column so
    they hit ``to_finite_float`` at value extraction; keeping them out of columns 0-2
    means they cannot disturb name-column detection (``"inf"``/``"nan"`` count as text).
    Region values are >2030 so they are never mistaken for year headers.
    """
    rows: list[list[object]] = [
        ["GDHI per head at current prices (GBP)", None, None, None, None, None, None, None],
        ["ITL code", "Region name", 2018, 2019, 2020, 2021, 2022, 2023],
        # Valid regions: finite latest-year values -> kept.
        [None, "Westminster", 58000, 59000, 60000, 61000, 63000, 64000],
        [None, "Blackpool", 13000, 13200, 13500, 13800, 14000, 14200],
        # inf latest cell: float("inf") passes a bare float() and is not <= 0 -> would
        # leak; to_finite_float returns None -> row dropped.
        [None, "Region with inf cell", 15000, 15500, 16000, 16500, 17000, "inf"],
        # "nan" text latest cell: float("nan") passes a bare float() -> would leak.
        [None, "Region with nan text", 18000, 18500, 19000, 19500, 20000, "nan"],
        # Blank latest cell (pandas NaN): float(nan) passes a bare float() -> would leak.
        [None, "Region with blank cell", 21000, 21500, 22000, 22500, 23000, float("nan")],
    ]
    return pd.DataFrame(rows)


def _run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[pd.DataFrame, bool]:
    """Drive ``process()`` through the fake readers and a tmp ``PROCESSED_DIR``."""
    monkeypatch.setattr(fetch_ons_gdhi.pd, "ExcelFile", _FakeExcelFile)
    monkeypatch.setattr(fetch_ons_gdhi.pd, "read_excel", lambda *_a, **_k: _raw_frame())
    monkeypatch.setattr(fetch_ons_gdhi, "PROCESSED_DIR", tmp_path)
    return fetch_ons_gdhi.process(tmp_path / "fake.xlsx")


def test_nonfinite_gdhi_cells_are_dropped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """inf / "nan" / blank latest-year cells are dropped, never published as non-finite."""
    df, is_fallback = _run(tmp_path, monkeypatch)
    assert is_fallback is False, "must exercise the live parse, not the illustrative fallback"

    regions = df["region"].tolist()
    for bad in ("Region with inf cell", "Region with nan text", "Region with blank cell"):
        assert bad not in regions, f"non-finite row {bad!r} must be dropped"

    # The returned frame is exactly what _save_and_return writes to CSV.
    assert not _has_nonfinite(df["gdhi_per_head"])

    # And the published CSV on disk carries no non-finite number either.
    published = pd.read_csv(tmp_path / "ons_gdhi_by_region.csv")
    assert not _has_nonfinite(published["gdhi_per_head"])


def test_valid_regions_survive_with_correct_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The finite-valued regions survive with their latest-year (2023) value."""
    df, is_fallback = _run(tmp_path, monkeypatch)
    assert is_fallback is False
    assert len(df) == 2
    by_region = df.set_index("region")["gdhi_per_head"].to_dict()
    assert by_region == {"Westminster": 64000.0, "Blackpool": 14200.0}
