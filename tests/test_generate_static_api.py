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


def test_generator_emits_csv_mirror_with_data_type_column(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RFC-001a: main() writes {slug}.csv next to the JSON, and a known
    provenance data_type travels IN the artifact as a trailing column."""
    data_dir = tmp_path / "processed"
    data_dir.mkdir()
    (data_dir / "t.csv").write_text("band,count\nA,2.0\nB,\n", encoding="utf-8")
    (data_dir / "t.meta.json").write_text(
        json.dumps({"data_type": "illustrative_fallback"}), encoding="utf-8"
    )
    out_dir = tmp_path / "out"
    monkeypatch.setattr(gsa, "DATA_DIR", data_dir)
    monkeypatch.setattr(gsa, "OUT_DIR", out_dir)
    monkeypatch.setattr(gsa, "DATASETS", {"t": "t.csv"})
    monkeypatch.setattr(gsa, "generate_simulator_static", lambda: 0)
    gsa.main()

    lines = (out_dir / "t.csv").read_text(encoding="utf-8").strip().splitlines()
    assert lines[0] == "band,count,data_type"
    assert lines[1] == "A,2.0,illustrative_fallback"
    # None cells serialise as empty strings, never as "None"/NaN
    assert lines[2] == "B,,illustrative_fallback"


@pytest.mark.parametrize(
    ("sidecar", "csv_type", "expected"),
    [
        ('{"data_type":"illustrative_fallback"}', "illustrative_fallback", "illustrative_fallback"),
        (None, "illustrative_fallback", "unverified"),
        ("{ corrupt", "illustrative_fallback", "unverified"),
        ('{"data_type":"live_ons"}', "illustrative_fallback", "unverified"),
        ('{"data_type":"bogus"}', "illustrative_fallback", "unverified"),
        ("[]", "illustrative_fallback", "unverified"),
        ('{"data_type":"live_ons"}', "live_ons", "live_ons"),
        ('{"data_type":"static_published"}', "static_published", "static_published"),
    ],
)
def test_generator_preserves_unverified_provenance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    sidecar: str | None,
    csv_type: str,
    expected: str,
) -> None:
    csv_path = tmp_path / "productivity_pay_gap.csv"
    csv_path.write_text(f"year,data_type\n1997,{csv_type}\n", encoding="utf-8")
    if sidecar is not None:
        csv_path.with_suffix(".meta.json").write_text(sidecar, encoding="utf-8")
    out_dir = tmp_path / "out"
    monkeypatch.setattr(gsa, "DATA_DIR", tmp_path)
    monkeypatch.setattr(gsa, "OUT_DIR", out_dir)
    monkeypatch.setattr(gsa, "DATASETS", {"productivity-pay": csv_path.name})
    monkeypatch.setattr(gsa, "generate_simulator_static", lambda: 0)
    gsa.main()

    metadata = json.loads((out_dir / "productivity-pay-metadata.json").read_text(encoding="utf-8"))
    assert metadata["data_type"] == expected
    catalog = json.loads((out_dir / "all-metadata.json").read_text(encoding="utf-8"))
    assert catalog["datasets"][0]["data_type"] == expected
    assert (out_dir / "productivity-pay.csv").read_text(encoding="utf-8").splitlines()[1] == f"1997,{expected}"


def test_generator_skips_csv_mirror_for_nc_nd_dataset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No generational-wealth CSV until the output-licence decision
    (ACTION-REQUIRED #10) — the source is CC BY-NC-ND 4.0."""
    data_dir = tmp_path / "processed"
    data_dir.mkdir()
    (data_dir / "g.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    monkeypatch.setattr(gsa, "DATA_DIR", data_dir)
    monkeypatch.setattr(gsa, "OUT_DIR", out_dir)
    monkeypatch.setattr(gsa, "DATASETS", {"generational-wealth": "g.csv"})
    monkeypatch.setattr(gsa, "generate_simulator_static", lambda: 0)
    gsa.main()

    assert (out_dir / "generational-wealth.json").exists()
    assert not (out_dir / "generational-wealth.csv").exists()


@pytest.mark.parametrize("case", [
    "current", "static-current", "legacy", "missing", "corrupt", "source", "source_url",
    "download_url", "tables", "period", "measure", "access_date", "later-fetch",
])
def test_child_poverty_static_metadata_requires_hbai_sidecar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    current = json.loads((SCRIPTS_DIR.parent / "projects/wealthlens-dashboard/frontend/public/data"
                          / "child-poverty-metadata.json").read_text(encoding="utf-8"))
    sidecar = current.copy()
    if case == "static-current":
        sidecar["data_type"] = "static_published"
    elif case == "later-fetch":
        # A re-fetch of the pinned table pack on another day stays verified.
        sidecar["access_date"] = "2027-01-15"
    elif case == "legacy":
        sidecar = {
            "data_type": "static_published",
            "source": "DWP/HMRC Children in Low Income Families",
            "source_url": "https://www.gov.uk/government/statistics/children-in-low-income-families-local-area-statistics-2014-to-2023",
            "access_date": "2026-05-16",
        }
    elif case not in ("current", "missing", "corrupt"):
        sidecar[case] = ["4.16ts"] if case == "tables" else "mismatch"
    verified = case in ("current", "static-current", "later-fetch")
    csv = tmp_path / "child_poverty_by_region.csv"
    csv.write_text(
        "region,child_poverty_pct,children_in_poverty,national_avg_pct,above_national_avg\n"
        + ("North East,34,200000,30,True\n" if verified else "North East,38,185000,29.8,True\n"),
        encoding="utf-8",
    )
    if case != "missing":
        csv.with_suffix(".meta.json").write_text(
            "{ corrupt" if case == "corrupt" else json.dumps(sidecar), encoding="utf-8"
        )
    out_dir = tmp_path / "out"
    monkeypatch.setattr(gsa, "DATA_DIR", tmp_path)
    monkeypatch.setattr(gsa, "OUT_DIR", out_dir)
    monkeypatch.setattr(gsa, "DATASETS", {"child-poverty": csv.name})
    monkeypatch.setattr(gsa, "generate_simulator_static", lambda: 0)
    gsa.main()
    metadata = json.loads((out_dir / "child-poverty-metadata.json").read_text(encoding="utf-8"))
    catalogue = json.loads((out_dir / "all-metadata.json").read_text(encoding="utf-8"))["datasets"][0]
    assert metadata == catalogue
    if verified:
        assert metadata["data_type"] == sidecar["data_type"]
        for key in ("source", "source_url", "access_date", "download_url", "tables", "period", "measure"):
            assert metadata[key] == sidecar[key]
    else:
        assert metadata["data_type"] == "unverified"
        assert metadata["source"] == "Unverified child-poverty data"
        assert metadata["source_url"] == ""
        assert "HBAI" not in json.dumps(metadata)
        assert "download_url" not in metadata
        records = json.loads((out_dir / "child-poverty.json").read_text(encoding="utf-8"))["data"]
        assert records[0]["child_poverty_pct"] == 38
        assert records[0]["children_in_poverty"] == 185000
        assert (out_dir / "child-poverty.csv").read_text(encoding="utf-8").splitlines()[1].endswith(",unverified")


def test_missing_csv_keeps_committed_last_good_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A fail-closed pipeline leaves no processed CSV on a fresh checkout (#741).

    The committed public files must stay byte-identical and the dataset must stay
    in datasets.json and all-metadata.json (decision D-D: serve last-good data).
    """
    data_dir = tmp_path / "processed"
    data_dir.mkdir()
    (data_dir / "fresh.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    last_good_data = b'{"data": [{"date": "2026-09-01", "bank_rate": 4.0}]}'
    last_good_meta = b'{"name": "boe-rates", "source": "Bank of England / ONS", "access_date": "2026-10-22"}'
    (out_dir / "boe-rates.json").write_bytes(last_good_data)
    (out_dir / "boe-rates-metadata.json").write_bytes(last_good_meta)
    monkeypatch.setattr(gsa, "DATA_DIR", data_dir)
    monkeypatch.setattr(gsa, "OUT_DIR", out_dir)
    monkeypatch.setattr(gsa, "DATASETS", {"wealth-shares": "fresh.csv", "boe-rates": "absent.csv"})
    monkeypatch.setattr(gsa, "generate_simulator_static", lambda: 0)
    gsa.main()

    assert (out_dir / "boe-rates.json").read_bytes() == last_good_data
    assert (out_dir / "boe-rates-metadata.json").read_bytes() == last_good_meta
    listing = json.loads((out_dir / "datasets.json").read_text(encoding="utf-8"))
    assert listing["datasets"] == ["wealth-shares", "boe-rates"]
    catalogue = json.loads((out_dir / "all-metadata.json").read_text(encoding="utf-8"))["datasets"]
    assert json.loads(last_good_meta) in catalogue


def test_missing_csv_without_last_good_is_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With no committed last-good files the dataset is still skipped, not invented."""
    data_dir = tmp_path / "processed"
    data_dir.mkdir()
    (data_dir / "fresh.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    monkeypatch.setattr(gsa, "DATA_DIR", data_dir)
    monkeypatch.setattr(gsa, "OUT_DIR", out_dir)
    monkeypatch.setattr(gsa, "DATASETS", {"wealth-shares": "fresh.csv", "boe-rates": "absent.csv"})
    monkeypatch.setattr(gsa, "generate_simulator_static", lambda: 0)
    gsa.main()

    listing = json.loads((out_dir / "datasets.json").read_text(encoding="utf-8"))
    assert listing["datasets"] == ["wealth-shares"]
    assert not (out_dir / "boe-rates.json").exists()
