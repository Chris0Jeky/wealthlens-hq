"""Call-site regression tests for the shared ``_cells.to_finite_float`` NaN guard.

#365 follow-up. ``fetch_hmrc_stats`` already has a focused test
(``test_hmrc_finite_cells``). These lock in the OTHER three fetchers that route
raw source cells through ``_cells.to_finite_float`` — ``fetch_boe_rates``,
``fetch_productivity_pay`` and ``fetch_wid_data`` — so a future refactor that
reintroduces a raw ``float()`` (which would let a blank / NaN / inf source cell
leak into a published CSV) is caught here rather than in production data.

Each test feeds a payload containing a value that bare ``float()`` WOULD accept
but ``to_finite_float`` rejects (``"inf"`` / ``"nan"`` / blank / overflow), and
asserts the published output never carries a non-finite number.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fetch_boe_rates
import fetch_productivity_pay
import fetch_wid_data


def _has_nonfinite(series: pd.Series) -> bool:
    """True if any non-None entry of ``series`` is NaN/inf."""
    return bool(series.map(lambda x: x is not None and not math.isfinite(x)).any())


# --- fetch_wid_data.process -------------------------------------------------


def test_wid_drops_nonfinite_value_and_noninteger_year(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A blank/inf value or a non-integer year is dropped, never published as NaN."""
    monkeypatch.setattr(fetch_wid_data, "PROCESSED_DIR", tmp_path)
    raw: dict[str, Any] = {
        "shweal_p99p100_992_j": [
            {
                "GB": {
                    "values": [
                        {"y": 2000, "v": 0.20},  # valid
                        {"y": 2001, "v": ""},  # blank value -> drop
                        {"y": 2002, "v": "inf"},  # non-finite -> drop
                        {"y": "2003.5", "v": 0.22},  # non-integer year -> drop
                        {"y": 2004, "v": 0.23},  # valid
                    ]
                }
            },
        ],
    }
    df = fetch_wid_data.process(raw)
    assert df["year"].tolist() == [2000, 2004]
    assert not _has_nonfinite(df["value"])


# --- fetch_productivity_pay._fetch_ons_timeseries ---------------------------


class _FakeResp:
    """Minimal stand-in for a ``requests`` response exposing the used surface."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


def test_productivity_timeseries_drops_nonfinite_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A blank/NaN observation is dropped from the parsed ONS time-series."""
    payload = {
        "years": [
            {"year": "2000", "value": "100.0"},  # valid
            {"year": "2001", "value": ""},  # blank -> drop
            {"year": "2002", "value": "nan"},  # non-finite -> drop
            {"year": "2003", "value": "110.0"},  # valid
        ]
    }
    monkeypatch.setattr(
        fetch_productivity_pay.requests, "get", lambda *_a, **_k: _FakeResp(payload)
    )
    df = fetch_productivity_pay._fetch_ons_timeseries("http://example.org/x", "prod")
    assert df is not None
    assert df["year"].tolist() == [2000, 2003]
    assert not _has_nonfinite(df["value"])


# --- fetch_boe_rates.process ------------------------------------------------


def test_boe_rejects_nonfinite_rate_cells(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A non-finite Bank Rate / CPI cell never reaches the published CSV.

    ``inf`` would survive a bare ``float()`` — ``to_finite_float`` turns it into
    ``None`` (skipped). A row whose values are all non-finite is dropped entirely.
    """
    monkeypatch.setattr(fetch_boe_rates, "PROCESSED_DIR", tmp_path)
    raw = tmp_path / "boe_raw.csv"
    raw.write_text(
        "DATE,IUDBEDR,D7BT\n"
        "01 Jan 2000,5.5,2.1\n"  # valid
        "02 Jan 2000,inf,3.0\n"  # bank_rate non-finite -> None (row kept via CPI)
        "03 Jan 2000,nan,nan\n"  # all non-finite -> row dropped
        "04 Jan 2000,4.0,1.5\n",  # valid
        encoding="utf-8",
    )
    df = fetch_boe_rates.process(raw)
    assert not _has_nonfinite(df["bank_rate"])
    assert not _has_nonfinite(df["cpi_annual"])
    # The all-non-finite row carried no publishable value, so it is dropped.
    assert "2000-01-03" not in df["date"].tolist()
    # The valid dates survive.
    assert {"2000-01-01", "2000-01-04"} <= set(df["date"].tolist())
