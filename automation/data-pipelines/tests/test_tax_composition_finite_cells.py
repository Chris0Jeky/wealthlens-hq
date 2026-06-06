"""Call-site regression test for the ``fetch_tax_composition`` NaN guard.

#365 follow-up. ``test_pipeline_finite_cells`` and ``test_hmrc_finite_cells`` already
lock in four of the ``to_finite_float`` call sites; this file adds the
``fetch_tax_composition`` one named (but not yet tested) in that follow-up list, so a
future refactor that reintroduces a bare ``float()`` — which would let a blank / NaN /
inf source cell leak into the published ``tax_composition.csv`` — is caught here rather
than in production data.

``fetch_tax_composition._try_parse_live`` reads an HMRC annual-receipts sheet:

* it locates the header row + year columns (cells like ``"2023-24"``),
* finds the five tax rows by keyword in column 0 (income tax / national insurance /
  capital gains / inheritance / stamp duty land),
* and for each ``(year, tax)`` cell calls ``to_finite_float(df_raw.iloc[r, c])``.

A blank/NaN/inf cell makes ``to_finite_float`` return ``None``, which sets
``all_valid = False`` and DROPS that whole YEAR. So this is a drop call site: the test
feeds one bad cell (a value bare ``float()`` would happily accept — ``"inf"`` / ``"nan"``
/ a pandas-blank ``NaN``) and asserts the offending year never reaches the published
frame and that no published number is non-finite. The fake supplies four year columns so
exactly one drop still leaves the three valid years ``_try_parse_live`` needs to stay on
the live path (asserted via ``data_source == "live"``, which also stops the test passing
vacuously through the illustrative fallback).

The parse is inline inside ``_try_parse_live``, so we exercise it by monkeypatching the
two pandas Excel readers it calls and pointing ``PROCESSED_DIR`` at a tmp dir, mirroring
``test_hmrc_finite_cells``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fetch_tax_composition

# Published numeric columns ``process()`` writes to ``tax_composition.csv``. None of
# these may carry a non-finite value: a finite raw cell stays finite, and a bad cell
# drops its year, so any NaN/inf here can only be a leaked bare ``float()``.
_PUBLISHED_NUMERIC_COLS = [
    "income_tax_bn",
    "nics_bn",
    "cgt_bn",
    "iht_bn",
    "sdlt_bn",
    "work_taxes_bn",
    "wealth_taxes_bn",
    "total_selected_bn",
    "work_pct",
    "wealth_pct",
]


def _has_nonfinite(series: pd.Series) -> bool:
    """True if any entry is NaN/None or +/-inf.

    A working ``to_finite_float`` drops the whole year on a bad cell, so the surviving
    rows carry no legitimate missing value — any NaN/inf in a published column is a leak.
    ``isin`` matches both ``np.inf`` and ``float('inf')``; ``isna`` covers None and NaN.
    """
    has_inf = bool(series.isin([float("inf"), float("-inf")]).any())
    return bool(series.isna().any()) or has_inf


class _FakeExcelFile:
    """Stand-in for ``pd.ExcelFile`` exposing only the ``sheet_names`` used.

    ``_try_parse_live`` picks the first sheet whose name contains ``"annual"`` or
    ``"a1"``; ``"Annual receipts"`` matches so the parse proceeds.
    """

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self.sheet_names = ["Contents", "Annual receipts"]


def _raw_frame(bad_value: object, bad_row: int, bad_col: int) -> pd.DataFrame:
    """Build a header=None HMRC-style annual sheet with one poisoned cell.

    Layout mirrors what ``_try_parse_live`` expects:
      * row 0 = header: col 0 is a label, cols 1-4 are year strings (``"2021-22"`` ...),
      * rows 1-5 = the five tax rows keyed off column 0,
      * cols 1-4 = the per-year £m values for each tax.

    ``rows[bad_row][bad_col]`` is overwritten with ``bad_value`` (an ``"inf"`` / ``"nan"``
    text cell, or a pandas-blank ``float('nan')``) to drop exactly the year in
    ``bad_col``. Four year columns mean one drop still leaves three valid years.
    """
    rows: list[list[object]] = [
        ["Tax (£m)", "2021-22", "2022-23", "2023-24", "2024-25"],
        ["Income Tax", "270000", "275000", "280000", "285000"],
        ["National Insurance contributions", "172000", "175000", "178000", "180000"],
        ["Capital Gains Tax", "14500", "15000", "15500", "16000"],
        ["Inheritance Tax", "7100", "7300", "7400", "7500"],
        ["Stamp Duty Land Tax", "12000", "12500", "13000", "13500"],
    ]
    rows[bad_row][bad_col] = bad_value
    return pd.DataFrame(rows)


def _run_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raw: pd.DataFrame
) -> pd.DataFrame:
    """Drive ``process()`` through the live-parse path against a crafted raw frame."""
    monkeypatch.setattr(fetch_tax_composition.pd, "ExcelFile", _FakeExcelFile)
    monkeypatch.setattr(fetch_tax_composition.pd, "read_excel", lambda *_a, **_k: raw)
    monkeypatch.setattr(fetch_tax_composition, "PROCESSED_DIR", tmp_path)
    return fetch_tax_composition.process(tmp_path / "fake.xlsx")


def _assert_clean_live(df: pd.DataFrame, dropped_year: str, tmp_path: Path) -> None:
    """Shared assertions: stayed on the live path, dropped the bad year, all finite —
    on BOTH the returned frame and the published CSV on disk (the real artifact)."""
    # Prove we exercised the live parse, not the illustrative fallback (which would
    # always be finite and make the test pass vacuously).
    assert df["data_source"].iloc[0] == "live"
    # The poisoned year is gone; the other three survived.
    assert dropped_year not in df["year"].tolist()
    assert set(df["year"].tolist()) == {"2021-22", "2022-23", "2023-24", "2024-25"} - {
        dropped_year
    }
    # No published number is non-finite — the discriminating signal vs a bare float() —
    # verified on the returned frame AND the CSV that actually ships.
    published = pd.read_csv(tmp_path / "tax_composition.csv")
    assert dropped_year not in published["year"].astype(str).tolist()
    for col in _PUBLISHED_NUMERIC_COLS:
        assert not _has_nonfinite(df[col]), f"{col} carries a non-finite value"
        assert not _has_nonfinite(published[col]), f"published {col} carries a non-finite value"


def test_inf_cell_drops_its_year(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An ``"inf"`` income-tax cell (bare ``float()`` would accept it) drops that year."""
    raw = _raw_frame("inf", bad_row=1, bad_col=4)  # Income Tax, 2024-25
    df = _run_process(tmp_path, monkeypatch, raw)
    _assert_clean_live(df, dropped_year="2024-25", tmp_path=tmp_path)


def test_nan_text_cell_drops_its_year(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A ``"nan"`` NICs cell (bare ``float()`` would accept it) drops that year."""
    raw = _raw_frame("nan", bad_row=2, bad_col=1)  # National Insurance, 2021-22
    df = _run_process(tmp_path, monkeypatch, raw)
    _assert_clean_live(df, dropped_year="2021-22", tmp_path=tmp_path)


def test_blank_nan_cell_drops_its_year(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pandas-blank ``float('nan')`` CGT cell drops that year.

    ``str(nan)`` is ``"nan"``, which bare ``float()`` turns back into a NaN — exactly the
    blank-cell leak ``to_finite_float`` exists to stop.
    """
    raw = _raw_frame(float("nan"), bad_row=3, bad_col=2)  # Capital Gains, 2022-23
    df = _run_process(tmp_path, monkeypatch, raw)
    _assert_clean_live(df, dropped_year="2022-23", tmp_path=tmp_path)
