"""Regression tests for scripts/generate_static_api.py NaN handling.

A blank/suppressed source cell (pandas NaN) must serialise to JSON ``null``, not
the invalid-JSON literal ``NaN``. The generator previously used
``df.where(pd.notna(df), other=None)``, which is ineffective for float columns
(pandas re-coerces None back to NaN), so ``cgt-concentration.json`` shipped a
literal ``NaN`` that no browser ``fetch().json()`` / ``JSON.parse`` can read.

These tests lock the two halves of the fix: record-level NaN->None sanitisation,
and ``allow_nan=False`` strict serialisation as a build-time guard.
"""

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import generate_static_api as gsa  # noqa: E402


def _write_csv(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "dataset.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_blank_cell_becomes_none_not_nan(tmp_path: Path) -> None:
    """A blank numeric cell parses to None (JSON null), not float NaN."""
    csv = _write_csv(
        tmp_path,
        # The second row's suppressed taxpayer count is blank -> pandas NaN.
        "gain_band,band_lower,num_taxpayers_thousands\n"
        "A,0.0,2.0\n"
        "B,3000.0,\n",
    )
    records = gsa._read_csv_as_records(csv)

    assert records[1]["num_taxpayers_thousands"] is None
    # Surrounding values are untouched.
    assert records[0]["num_taxpayers_thousands"] == 2.0
    assert records[1]["gain_band"] == "B"
    assert records[1]["band_lower"] == 3000.0


def test_records_serialise_as_strict_valid_json(tmp_path: Path) -> None:
    """Sanitised records pass json.dumps(allow_nan=False) and round-trip."""
    csv = _write_csv(
        tmp_path,
        "a,b\n1.0,\n,2.0\n",  # one blank per row
    )
    records = gsa._read_csv_as_records(csv)

    # allow_nan=False is the generator's build-time guard: it must not raise,
    # must emit `null` (never the invalid `NaN` token), and must round-trip
    # through a strict JSON parser (what the browser does).
    out = json.dumps({"data": records}, allow_nan=False)
    assert "NaN" not in out
    assert "null" in out
    assert json.loads(out) == {"data": records}


def _run_generator_on(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, csv_text: str
) -> Path:
    """Drive the generator's REAL main() write path over a single tmp dataset.

    Points DATA_DIR (input CSVs) and OUT_DIR (output JSON) at tmp dirs, restricts
    DATASETS to one slug, and no-ops the simulator step (independent of CSV data
    and needs the registry/fixtures). Returns the output dir.
    """
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    out_dir = tmp_path / "out"
    (in_dir / "t.csv").write_text(csv_text, encoding="utf-8")
    monkeypatch.setattr(gsa, "DATA_DIR", in_dir)
    monkeypatch.setattr(gsa, "OUT_DIR", out_dir)
    monkeypatch.setattr(gsa, "DATASETS", {"t": "t.csv"})
    monkeypatch.setattr(gsa, "generate_simulator_static", lambda: 0)
    gsa.main()
    return out_dir


def test_generator_write_path_emits_valid_json_for_blank_cells(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: main()'s real write produces strict-valid JSON (null, not NaN).

    Unlike the unit tests above (which call a local json.dumps), this exercises
    the generator's ACTUAL data_path.write_text(json.dumps(..., allow_nan=False))
    so the record-sanitisation half is locked through the real seam, on the exact
    cgt-concentration failure shape (a blank/suppressed float cell).
    """
    out_dir = _run_generator_on(
        tmp_path, monkeypatch, "band,count\nA,2.0\nB,\n"
    )
    raw = (out_dir / "t.json").read_text(encoding="utf-8")
    assert "NaN" not in raw
    parsed = json.loads(raw)  # strict parse — what the browser's fetch().json() does
    assert parsed["data"][1]["count"] is None
    assert parsed["data"][0]["count"] == 2.0


def test_generator_write_path_fails_loud_on_a_nonfinite_leak(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: the allow_nan=False guard half actually bites.

    An ``inf`` cell survives _read_csv_as_records (it only nulls NaN), so it
    reaches main()'s write and must trip allow_nan=False. If a future edit drops
    allow_nan=False from the generator's writes, this test fails (the file would
    instead be written with the invalid `Infinity` token) — which the earlier
    unit tests, using a local json.dumps, would NOT catch.
    """
    with pytest.raises(ValueError):
        _run_generator_on(tmp_path, monkeypatch, "a,b\n1.0,inf\n")
