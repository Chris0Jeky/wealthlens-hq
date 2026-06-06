"""Call-site NaN-guard regression test for ``fetch_ons_wealth.process``.

#365 follow-up. ``fetch_ons_wealth`` was named in ``test_pipeline_finite_cells`` as a
``to_finite_float`` call site that was guarded but not yet call-site-tested. This file
closes that gap so a future refactor that reintroduces a bare ``float()`` (which would
let a blank / NaN / inf source cell leak into the published ``ons_wealth_by_decile.csv``)
is caught here rather than in production data.

``process()`` has three ``to_finite_float`` call sites across two parsers:

* ``_parse_decile_data`` value cell (the legacy parser; the col-1 site plus the
  col-2..5 recovery loop). A bad cell with no finite sibling drops the whole decile row.
* ``_parse_table_2_2`` value cell (the primary Jan-2025 parser). A bad cell drops that
  decile, and because the parser demands all 10 deciles it then rejects the partial
  block (returns ``None``) rather than publish a NaN-bearing table.

Discriminating signal (same as ``test_pipeline_finite_cells``): a working
``to_finite_float`` converts a non-finite cell to ``None`` (the row is dropped / the
block rejected), so a published ``inf`` or ``NaN`` can only come from a bare ``float()``
— ``float(float("nan"))`` is ``nan`` and ``float("inf")`` is ``inf``, both of which the
guard rejects.

The legacy parser is exercised end-to-end through ``process()`` (monkeypatching the two
pandas Excel readers and pointing ``PROCESSED_DIR`` at a tmp dir, mirroring
``test_hmrc_finite_cells``); the primary parser is exercised directly on a faithful
Table 2.2 frame because a dropped row there cascades to a ``None`` return that the
``process()`` fallback chain would obscure — with a clean-frame control so the rejection
test cannot pass vacuously.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fetch_ons_wealth


def _has_inf(series: pd.Series) -> bool:
    """True if any entry is +/-infinity — the unmistakable bare-``float()`` signature.

    ``to_finite_float`` converts a non-finite cell to ``None``, so a published ``inf``
    can only come from a bypassed bare ``float()``. ``isin`` matches both ``np.inf`` and
    ``float('inf')`` and is safe on object dtype.
    """
    return bool(series.isin([float("inf"), float("-inf")]).any())


def _has_nonfinite(series: pd.Series) -> bool:
    """True if any entry is NaN/None or +/-inf.

    Safe on the published wealth column, where every surviving row carries a real
    finite value — so any NaN/inf there is a leak, never a legitimate missing value.
    """
    return bool(series.isna().any() or _has_inf(series))


class _FakeExcelFile:
    """Stand-in for ``pd.ExcelFile`` exposing only the ``sheet_names`` ``process`` uses.

    The sheet name is irrelevant here because ``pd.read_excel`` is also stubbed to return
    our raw frame regardless of which sheet ``process`` selects.
    """

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self.sheet_names = ["Sheet1"]


def _drive_legacy_process(
    df_raw: pd.DataFrame, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> pd.DataFrame:
    """Run ``process()`` against ``df_raw`` via the legacy ``_parse_decile_data`` path.

    ``df_raw`` deliberately omits the "aggregate total wealth" marker, so the primary
    ``_parse_table_2_2`` parser returns ``None`` and ``process`` falls through to
    ``_find_decile_header_row`` + ``_parse_decile_data`` — the path under test.
    """
    monkeypatch.setattr(fetch_ons_wealth.pd, "ExcelFile", _FakeExcelFile)
    monkeypatch.setattr(fetch_ons_wealth.pd, "read_excel", lambda *_a, **_k: df_raw)
    monkeypatch.setattr(fetch_ons_wealth, "PROCESSED_DIR", tmp_path)
    return fetch_ons_wealth.process(tmp_path / "fake.xlsx")


# --- legacy parser (_parse_decile_data value cell) --------------------------


def test_legacy_parser_drops_nonfinite_value_cells(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A blank/``inf``/``nan`` decile value is dropped, never published as NaN/inf.

    A blank Excel cell is read by pandas as a float ``NaN``; textual ``"inf"`` / ``"nan"``
    cells satisfy a bare ``float()`` (-> ``inf`` / ``nan``). ``to_finite_float`` rejects
    all three (-> ``None``), and with no finite sibling column each bad row is dropped, so
    the published ``total_wealth_bn`` stays finite. A bare ``float()`` would instead keep
    those rows and leak a NaN/inf into the CSV.
    """
    rows: list[list[object]] = [
        ["Decile", "Total net wealth (£bn)"],  # header detected by _find_decile_header_row
        ["1st (poorest)", 13.9],  # valid
        ["2nd", float("nan")],  # blank cell pandas reads as NaN -> row dropped
        ["3rd", "inf"],  # non-finite text -> row dropped
        ["4th", "nan"],  # non-finite text -> row dropped
        ["5th", 652.0],  # valid
    ]
    df = _drive_legacy_process(pd.DataFrame(rows), tmp_path, monkeypatch)

    assert "2nd" not in df["decile"].tolist(), "blank-value decile must be dropped"
    assert "3rd" not in df["decile"].tolist(), "inf-value decile must be dropped"
    assert "4th" not in df["decile"].tolist(), "nan-value decile must be dropped"
    assert set(df["decile"].tolist()) == {"1st (poorest)", "5th"}
    assert not _has_inf(df["total_wealth_bn"])
    assert not _has_nonfinite(df["total_wealth_bn"]), (
        "total_wealth_bn (the published metric) must carry no NaN/inf"
    )
    # Same guarantee on the published CSV (the real artifact), not just the frame.
    published = pd.read_csv(tmp_path / "ons_wealth_by_decile.csv")
    assert not _has_nonfinite(published["total_wealth_bn"])
    for bad in ("2nd", "3rd", "4th"):
        assert bad not in published["decile"].astype(str).tolist()


def test_legacy_parser_recovery_loop_routes_siblings_through_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The col-2..5 sibling-recovery loop also routes cells through ``to_finite_float``.

    When the col-1 value is non-finite, ``_parse_decile_data`` scans the sibling columns
    for a finite value. A non-finite sibling (``inf``/``nan``) is rejected — with no other
    finite sibling the decile is dropped; a finite sibling is recovered. A bare ``float()``
    in that loop would instead leak the sibling ``inf`` into the published table. (This
    exercises the 3rd ons_wealth call site, ``fetch_ons_wealth.py:313``.)
    """
    rows: list[list[object]] = [
        ["Decile", "Total net wealth (£bn)", "Alt"],  # 3-col header so the loop runs
        ["1st (poorest)", 13.9, None],  # valid via col-1
        ["2nd", float("nan"), "inf"],  # col-1 missing, only sibling is inf -> dropped
        ["3rd", float("nan"), 42.0],  # col-1 missing, finite sibling -> recovered as 42.0
        ["4th", 652.0, None],  # valid via col-1
    ]
    df = _drive_legacy_process(pd.DataFrame(rows), tmp_path, monkeypatch)

    assert "2nd" not in df["decile"].tolist(), "inf-only-sibling decile must be dropped"
    recovered = df[df["decile"] == "3rd"]
    assert len(recovered) == 1, "a finite sibling must recover the decile"
    assert recovered["total_wealth_bn"].iloc[0] == pytest.approx(42.0)
    assert set(df["decile"].tolist()) == {"1st (poorest)", "3rd", "4th"}
    assert not _has_nonfinite(df["total_wealth_bn"]), (
        "no NaN/inf may reach the published metric via the recovery loop"
    )
    published = pd.read_csv(tmp_path / "ons_wealth_by_decile.csv")
    assert not _has_nonfinite(published["total_wealth_bn"])
    assert "2nd" not in published["decile"].astype(str).tolist()


# --- primary parser (_parse_table_2_2 value cell) ---------------------------


def _table_2_2_frame(decile5_value: object) -> pd.DataFrame:
    """A faithful minimal Table 2.2 block (Jan-2025 layout).

    Col 0 = component label (only on the first block row), col 1 = decile label,
    col 2 = the value (£m, the most-recent-wave / ``last_col`` column). Ten decile rows
    so a clean frame parses; ``decile5_value`` is the cell under test.
    """
    rows: list[list[object]] = [
        ["Total wealth, Great Britain", None, None],  # title (no "aggregate total wealth")
        ["Component", "Decile", "April 2020 to March 2022"],  # header
        ["Aggregate total wealth", "Total Wealth Decile 1 (lowest)", 100000],  # agg_row
        [None, "Total Wealth Decile 2", 200000],
        [None, "Total Wealth Decile 3", 300000],
        [None, "Total Wealth Decile 4", 400000],
        [None, "Total Wealth Decile 5", decile5_value],  # cell under test
        [None, "Total Wealth Decile 6", 600000],
        [None, "Total Wealth Decile 7", 700000],
        [None, "Total Wealth Decile 8", 800000],
        [None, "Total Wealth Decile 9", 900000],
        [None, "Total Wealth Decile 10 (highest)", 1000000],
    ]
    return pd.DataFrame(rows)


def test_primary_parser_publishes_ten_finite_deciles() -> None:
    """Control: a clean Table 2.2 block parses to 10 finite decile rows.

    Pairs with the rejection test below — it proves the fake frame is structurally valid,
    so a ``None`` return there can only be the dropped non-finite cell, not a broken fake.
    """
    result = fetch_ons_wealth._parse_table_2_2(_table_2_2_frame(500000))

    assert result is not None
    assert len(result) == 10
    assert not _has_nonfinite(result["total_wealth_bn"])


def test_primary_parser_rejects_block_with_a_nonfinite_cell() -> None:
    """A blank decile cell is dropped, so the partial block is rejected (not published).

    The decile-5 NaN is rejected at the ``last_col`` ``to_finite_float`` guard, leaving
    only 9 finite deciles; the parser requires all 10 and returns ``None`` so the caller
    falls back rather than publish a NaN-bearing table. A bare ``float(nan)`` would keep
    the row, give 10 records and return a NaN-bearing frame instead of ``None``.
    """
    result = fetch_ons_wealth._parse_table_2_2(_table_2_2_frame(float("nan")))

    assert result is None
