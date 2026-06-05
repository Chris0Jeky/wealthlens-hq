"""Focused regression test for the HMRC CGT NaN-leak fix.

`fetch_hmrc_stats.process` previously parsed the taxpayer-count cell with raw
``float()`` and, on a blank cell that pandas reads as NaN, appended
``num_taxpayers_thousands = NaN`` *without skipping the row* — so a NaN leaked
into the published CSV. Routing the parse through ``_cells.to_finite_float`` (which
rejects NaN) plus skipping the row when the count is ``None`` closes that leak.

The parse is inline inside ``process()``, so we exercise it by monkeypatching the
two pandas Excel readers it calls (``pd.ExcelFile`` for sheet names and
``pd.read_excel`` for the raw frame) and pointing ``PROCESSED_DIR`` at a tmp dir.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fetch_hmrc_stats


class _FakeExcelFile:
    """Stand-in for ``pd.ExcelFile`` exposing only the ``sheet_names`` used."""

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self.sheet_names = ["Contents", "2_1a"]


def _raw_frame_with_blank_count() -> pd.DataFrame:
    """Build a raw HMRC-style sheet where one band has a blank (NaN) count cell.

    Layout mirrors what ``process()`` expects:
      col 0 = band lower limit, col 1 = num individuals (thousands),
      col 2 = gains (£m), col 3 = tax (£m).
    The header row must contain both "range" and "number" for detection.
    """
    rows = [
        ["Notes", None, None, None],
        ["Range of gain", "Number of individuals", "Amounts of gains", "Amounts of tax"],
        # Valid band — finite count.
        ["10000", "30", "10000", "1000"],
        # Band with a SUPPRESSED/blank taxpayer count (pandas NaN). This is the
        # row that used to leak a NaN num_taxpayers into the CSV; it must now be
        # dropped instead of appended.
        ["500000", float("nan"), "12000", "2400"],
        # Another valid band so the frame is non-empty after the drop.
        ["1000000", "5", "25000", "5000"],
        # Totals row.
        ["All", "35", "47000", "8400"],
    ]
    return pd.DataFrame(rows)


def test_blank_taxpayer_count_row_is_dropped_not_nan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A band with a blank (NaN) count must be dropped, never written as NaN."""
    monkeypatch.setattr(fetch_hmrc_stats.pd, "ExcelFile", _FakeExcelFile)
    monkeypatch.setattr(
        fetch_hmrc_stats.pd,
        "read_excel",
        lambda *_a, **_k: _raw_frame_with_blank_count(),
    )
    monkeypatch.setattr(fetch_hmrc_stats, "PROCESSED_DIR", tmp_path)

    df = fetch_hmrc_stats.process({"table2": tmp_path / "fake.ods"})

    # The £500,000 band had a blank count — it must not appear in the output.
    assert 500000 not in df["band_lower"].tolist(), (
        "Row with a blank (NaN) taxpayer count should be dropped, not kept"
    )
    # And no NaN must survive in the published taxpayer-count column.
    assert not df["num_taxpayers_thousands"].isna().any(), (
        "num_taxpayers_thousands must contain no NaN after the leak fix"
    )
    # The two valid bands (10k, 1m) remain.
    assert set(df["band_lower"].tolist()) == {10000.0, 1000000.0}
