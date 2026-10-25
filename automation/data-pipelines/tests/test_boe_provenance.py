"""BoE fallback provenance must survive processing and publication."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from unittest.mock import Mock

import fetch_boe_rates as boe
import http_retry
import pandas as pd
import pytest
import requests

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "projects/wealthlens-dashboard/backend"))

import generate_static_api as static_api  # noqa: E402
from app.routers import data as api  # noqa: E402


@pytest.fixture()
def pipeline_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(boe, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(boe, "PROCESSED_DIR", tmp_path / "processed")
    monkeypatch.setattr(boe, "CHART_DIR", tmp_path / "charts")
    monkeypatch.setattr(http_retry.time, "sleep", lambda _: None)
    return tmp_path


@pytest.mark.parametrize("entrypoint", ["fetch", "main"])
@pytest.mark.parametrize("source", ["bank", "cpi"])
@pytest.mark.parametrize("failure", ["download", "parse", "oserror"])
@pytest.mark.parametrize("existing_outputs", [False, True])
def test_failed_fetch_preserves_last_good_outputs(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture,
    entrypoint: str, source: str, failure: str, existing_outputs: bool,
) -> None:
    if existing_outputs:
        for relative in (
            "raw/boe_iumabedr.csv", "raw/ons_d7g7.csv", "raw/boe_iadb_rates.csv",
            "raw/boe_iadb_rates.meta.json", "processed/boe_rates.csv",
            "processed/boe_rates.meta.json", "charts/boe_rates.html",
        ):
            path = pipeline_dirs / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"last-good\x00\xff\r\n")
    before = {p.relative_to(pipeline_dirs): p.read_bytes() for p in pipeline_dirs.rglob("*") if p.is_file()}
    paths_before = set(pipeline_dirs.rglob("*"))
    bank_response = Mock(content=BANK_RATE_FIXTURE.read_bytes(), status_code=200)
    if failure == "parse":
        failed_response: object = Mock(content=b"<html>Upstream error</html>", status_code=200)
    elif failure == "oserror":
        failed_response = OSError("offline fixture read failed")
    else:
        failed_response = requests.ConnectionError("offline regression fixture")
    responses = ([] if source == "bank" else [bank_response]) + [failed_response] * 4
    monkeypatch.setattr(boe.requests, "get", Mock(side_effect=responses))
    monkeypatch.setattr(sys, "argv", ["fetch_boe_rates.py"])

    with caplog.at_level(logging.ERROR, logger=boe.__name__), pytest.raises(
        RuntimeError, match="BoE IUMABEDR / ONS D7G7",
    ) as error:
        if entrypoint == "fetch":
            boe.fetch()
        else:
            boe.main()

    expected_error = ValueError if failure == "parse" else OSError if failure == "oserror" else requests.ConnectionError
    assert isinstance(error.value.__cause__, expected_error)
    assert {p.relative_to(pipeline_dirs): p.read_bytes() for p in pipeline_dirs.rglob("*") if p.is_file()} == before
    assert set(pipeline_dirs.rglob("*")) == paths_before
    assert any(record.name == boe.__name__ and record.levelno == logging.ERROR for record in caplog.records)
    assert "using fallback data" not in caplog.text


@pytest.mark.parametrize("entrypoint", ["fetch", "main"])
def test_opt_in_failed_fetch_labels_fallback_through_api_and_static_export(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch, entrypoint: str,
) -> None:
    def unavailable(*args: object, **kwargs: object) -> None:
        raise requests.ConnectionError("offline regression fixture")

    monkeypatch.setattr(boe.requests, "get", unavailable)
    if entrypoint == "fetch":
        frame = boe.process(boe.fetch(allow_fallback=True))
    else:
        monkeypatch.setattr(sys, "argv", ["fetch_boe_rates.py", "--allow-illustrative-fallback"])
        boe.main()
        frame = pd.read_csv(pipeline_dirs / "processed/boe_rates.csv")
    processed = pipeline_dirs / "processed"
    sidecar = json.loads((processed / "boe_rates.meta.json").read_text())
    assert sidecar["data_type"] == "illustrative_fallback"
    assert frame["data_type"].eq("illustrative_fallback").all()

    monkeypatch.setattr(api, "DATA_DIR", processed)
    monkeypatch.setattr(api, "_metadata_cache", {})
    assert api._build_metadata("boe-rates")["data_type"] == "illustrative_fallback"

    output = pipeline_dirs / "public"
    monkeypatch.setattr(static_api, "DATA_DIR", processed)
    monkeypatch.setattr(static_api, "OUT_DIR", output)
    monkeypatch.setattr(static_api, "DATASETS", {"boe-rates": "boe_rates.csv"})
    monkeypatch.setattr(static_api, "generate_simulator_static", lambda *args: 0)
    static_api.main()
    metadata = json.loads((output / "boe-rates-metadata.json").read_text())
    assert metadata["data_type"] == "illustrative_fallback"
    catalog = json.loads((output / "all-metadata.json").read_text())
    assert catalog["datasets"][0]["data_type"] == "illustrative_fallback"
    assert pd.read_csv(output / "boe-rates.csv")["data_type"].eq("illustrative_fallback").all()
    assert all(
        row["data_type"] == "illustrative_fallback"
        for row in json.loads((output / "boe-rates.json").read_text())["data"]
    )
    # More fallback rows must never turn an example into an official chart.
    boe.build_chart(pd.concat([frame, frame]))
    chart = (pipeline_dirs / "charts/boe_rates.html").read_text(encoding="utf-8")
    assert "ILLUSTRATIVE FALLBACK DATA" in chart
    assert "not published statistics" in chart


def test_download_uses_project_user_agent_and_existing_timeout(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = Mock(content=BANK_RATE_FIXTURE.read_bytes(), status_code=200)
    request = Mock(return_value=response)
    monkeypatch.setattr(boe.requests, "get", request)
    assert boe._download_iadb(boe.BANK_RATE_SERIES) is response
    request.assert_called_once_with(
        boe.BOE_IADB_URL,
        params=boe._build_iadb_params(boe.BANK_RATE_SERIES),
        timeout=boe.REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": boe.USER_AGENT},
    )
    assert "Mozilla/5.0" in boe.USER_AGENT
    assert "WealthLensDataPipeline" in boe.USER_AGENT
    response.raise_for_status.assert_called_once()


BANK_RATE_FIXTURE = Path(__file__).parent / "fixtures/boe_iumabedr.csv"
CPI_FIXTURE = Path(__file__).parent / "fixtures/ons_d7g7_mm23.csv"


@pytest.mark.parametrize("delimiter", [",", "\t"])
def test_parser_reads_captured_iadb_monthly_average_export(delimiter: str) -> None:
    # Expected observations come from captured official bytes, never typed figures.
    original = pd.read_csv(BANK_RATE_FIXTURE)
    raw_text = BANK_RATE_FIXTURE.read_text(encoding="utf-8").replace(",", delimiter)
    parsed = boe._parse_iadb_csv(raw_text, required_series=(boe.BANK_RATE_SERIES,))
    pd.testing.assert_frame_equal(parsed, original)
    dates = pd.to_datetime(parsed["DATE"], format="%d %b %Y")
    assert dates.dt.is_month_end.all()
    assert dates.dt.to_period("M").is_unique


@pytest.mark.parametrize("response_body", [
    b"<html><title>Error</title>Invalid series code value supplied.</html>",
    BANK_RATE_FIXTURE.read_bytes(),
])
def test_successful_http_without_both_series_keeps_whole_dataset_illustrative(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch, response_body: bytes,
) -> None:
    response = Mock(content=response_body, status_code=200)
    monkeypatch.setattr(boe.requests, "get", Mock(return_value=response))
    result = boe.process(boe.fetch(allow_fallback=True))
    expected = boe.process(boe._write_fallback(pipeline_dirs / "expected.csv"))
    pd.testing.assert_frame_equal(result, expected)
    assert result["data_type"].eq("illustrative_fallback").all()


def test_processing_incomplete_official_export_fails_before_writing(
    pipeline_dirs: Path,
) -> None:
    raw = pipeline_dirs / "incomplete.csv"
    raw.write_bytes(BANK_RATE_FIXTURE.read_bytes())
    citation = json.loads(BANK_RATE_FIXTURE.with_suffix(".meta.json").read_text())
    boe._write_metadata(
        raw, data_type="live_ons", source_url=citation["source_url"],
        access_date=citation["access_date"],
    )
    with pytest.raises(ValueError, match="lacks required series"):
        boe.process(raw)
    assert not (pipeline_dirs / "processed/boe_rates.csv").exists()


@pytest.mark.parametrize("sidecar_text", [None, "{ corrupt", "[]", '{"data_type":"live_ons"}'])
def test_missing_corrupt_or_conflicting_raw_provenance_never_becomes_official(
    pipeline_dirs: Path, sidecar_text: str | None,
) -> None:
    raw_dir = pipeline_dirs / "raw"
    raw_dir.mkdir()
    raw = boe._write_fallback(raw_dir / "input.csv")
    sidecar = raw.with_suffix(".meta.json")
    if sidecar_text is None:
        sidecar.unlink(missing_ok=True)
    else:
        sidecar.write_text(sidecar_text)
    result = boe.process(raw)
    assert result["data_type"].isin(["illustrative_fallback", "unverified"]).all()
    meta = json.loads((pipeline_dirs / "processed/boe_rates.meta.json").read_text())
    assert meta["data_type"] in {"illustrative_fallback", "unverified"}


def test_committed_boe_values_rebuild_exactly_from_full_official_fixtures(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every public byte must be reproducible offline, including every Bank Rate month."""
    bank_citation = json.loads(BANK_RATE_FIXTURE.with_suffix(".meta.json").read_text())
    cpi_citation = json.loads(CPI_FIXTURE.with_suffix(".meta.json").read_text())
    monkeypatch.setattr(boe, "ACCESS_DATE", bank_citation["access_date"])
    monkeypatch.setattr(boe.requests, "get", Mock(side_effect=[
        Mock(content=BANK_RATE_FIXTURE.read_bytes(), status_code=requests.codes.ok, url=bank_citation["source_url"]),
        Mock(content=CPI_FIXTURE.read_bytes(), status_code=requests.codes.ok, url=cpi_citation["source_url"]),
    ]))
    frame = boe.process(boe.fetch())
    public = ROOT / "projects/wealthlens-dashboard/frontend/public/data"
    output = pipeline_dirs / "public"
    monkeypatch.setattr(static_api, "DATA_DIR", pipeline_dirs / "processed")
    monkeypatch.setattr(static_api, "OUT_DIR", output)
    monkeypatch.setattr(static_api, "DATASETS", {"boe-rates": "boe_rates.csv"})
    monkeypatch.setattr(static_api, "generate_simulator_static", lambda *args: 0)
    static_api.main()
    # Compare text with normalised line endings: git stores these files with LF and
    # checks them out with the platform's endings, while the CSV writer emits CRLF.
    for filename in ("boe-rates.json", "boe-rates.csv", "boe-rates-metadata.json"):
        built = (output / filename).read_bytes().replace(b"\r\n", b"\n")
        committed = (public / filename).read_bytes().replace(b"\r\n", b"\n")
        assert built == committed, filename
    assert frame["data_type"].eq("live_ons").all()
    assert frame["date"].iloc[0] == "2000-01-01"
    bank = boe._parse_iadb_csv(BANK_RATE_FIXTURE.read_text())
    assert len(frame) == len(bank)


def test_missing_boe_sidecar_is_unverified_in_both_publication_paths(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = boe.process(boe._write_fallback(pipeline_dirs / "input.csv"))
    processed = pipeline_dirs / "processed"
    csv_path = processed / "boe_rates.csv"
    csv_path.with_suffix(".meta.json").unlink()
    monkeypatch.setattr(api, "DATA_DIR", processed)
    monkeypatch.setattr(api, "_metadata_cache", {})
    assert api._build_metadata("boe-rates")["data_type"] == "unverified"
    assert static_api._read_data_type(csv_path, frame.to_dict("records")) == "unverified"


def test_parser_reads_captured_ons_months_only() -> None:
    import csv

    original = list(csv.reader(CPI_FIXTURE.read_text(encoding="utf-8-sig").splitlines()))
    monthly = [row for row in original if len(row[0].split()) == 2 and row[0].split()[1] in
               ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]]
    parsed = boe._parse_ons_csv(CPI_FIXTURE.read_text(encoding="utf-8"))
    assert len(parsed) == len(monthly)
    assert parsed[boe.CPI_SERIES].tolist() == [float(row[1]) for row in monthly]
    assert pd.to_datetime(parsed["DATE"]).dt.strftime("%Y %b").str.upper().tolist() == [
        row[0] for row in monthly
    ]


@pytest.mark.parametrize("damage", ["html", "wrong-series", "no-months", "duplicate", "non-finite"])
def test_ons_parser_rejects_invalid_exports(damage: str) -> None:
    text = CPI_FIXTURE.read_text(encoding="utf-8")
    lines = text.splitlines()
    monthly = next(line for line in lines if ' JAN"' in line)
    if damage == "html":
        text = "<html>Temporarily unavailable</html>"
    elif damage == "wrong-series":
        text = text.replace('"D7G7"', '"OTHER"')
    elif damage == "no-months":
        text = "\n".join(lines[:8])
    elif damage == "duplicate":
        text += monthly + "\n"
    else:
        text = text.replace(monthly, monthly.rsplit(",", 1)[0] + ',"NaN"')
    with pytest.raises(ValueError):
        boe._parse_ons_csv(text)


def test_two_official_fetches_join_months_and_publish_sources(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    bank_response = Mock(content=BANK_RATE_FIXTURE.read_bytes(), status_code=200, url=boe.BOE_IADB_URL)
    cpi_response = Mock(content=CPI_FIXTURE.read_bytes(), status_code=200, url=boe.ONS_CPI_URL)
    request = Mock(side_effect=[bank_response, cpi_response])
    monkeypatch.setattr(boe.requests, "get", request)
    raw = boe.fetch()
    result = boe.process(raw)
    bank = boe._parse_iadb_csv(BANK_RATE_FIXTURE.read_text())
    cpi = boe._parse_ons_csv(CPI_FIXTURE.read_text())
    expected = boe._join_monthly(bank, cpi).rename(columns={
        "DATE": "date", boe.BANK_RATE_SERIES: "bank_rate", boe.CPI_SERIES: "cpi_annual",
    })
    pd.testing.assert_frame_equal(result.drop(columns="data_type"), expected)
    assert result["data_type"].eq("live_ons").all()
    assert pd.to_datetime(result["date"]).dt.is_month_start.all()
    assert len(result) == len(bank)
    assert request.call_args_list[0].kwargs["params"]["SeriesCodes"] == boe.BANK_RATE_SERIES
    assert request.call_args_list[1].args == (boe.ONS_CPI_URL,)
    for call in request.call_args_list:
        assert call.kwargs["timeout"] == boe.REQUEST_TIMEOUT_SECONDS
        assert call.kwargs["headers"] == {"User-Agent": boe.USER_AGENT}
    metadata = json.loads(raw.with_suffix(".meta.json").read_text())
    assert [source["url"] for source in metadata["sources"]] == [boe.BOE_IADB_URL, boe.ONS_CPI_URL]
    assert all(source["access_date"] == boe.ACCESS_DATE for source in metadata["sources"])
    processed = pipeline_dirs / "processed"
    assert json.loads((processed / "boe_rates.meta.json").read_text())["sources"] == metadata["sources"]
    monkeypatch.setattr(api, "DATA_DIR", processed)
    monkeypatch.setattr(api, "_metadata_cache", {})
    api_metadata = api._build_metadata("boe-rates")
    assert api_metadata["data_type"] == "live_ons"
    monkeypatch.setattr(static_api, "DATA_DIR", processed)
    monkeypatch.setattr(static_api, "OUT_DIR", pipeline_dirs / "public")
    monkeypatch.setattr(static_api, "DATASETS", {"boe-rates": "boe_rates.csv"})
    monkeypatch.setattr(static_api, "generate_simulator_static", lambda *args: 0)
    static_api.main()
    published = json.loads((pipeline_dirs / "public/boe-rates-metadata.json").read_text())
    assert published["sources"] == metadata["sources"]
    assert published["access_date"] == metadata["access_date"]
    assert published["data_type"] == "live_ons"
    for key in ("description", "source", "source_url", "access_date", "sources", "data_type"):
        assert api_metadata[key] == published[key]
    boe.build_chart(result)
    chart = (pipeline_dirs / "charts/boe_rates.html").read_text(encoding="utf-8")
    assert "ILLUSTRATIVE FALLBACK DATA" not in chart
    assert "UNVERIFIED PROVENANCE" not in chart
    assert "ONS D7G7" in chart


@pytest.mark.parametrize("damage", ["missing-month", "duplicate", "non-finite", "no-overlap"])
def test_join_rejects_incomplete_official_months(damage: str) -> None:
    bank = boe._parse_iadb_csv(BANK_RATE_FIXTURE.read_text())
    cpi = boe._parse_ons_csv(CPI_FIXTURE.read_text())
    if damage == "missing-month":
        bank = bank.drop(bank.index[len(bank) // 2])
    elif damage == "duplicate":
        bank = pd.concat([bank, bank.iloc[:1]])
    elif damage == "non-finite":
        bank.loc[bank.index[0], boe.BANK_RATE_SERIES] = float("inf")
    else:
        cpi = cpi.loc[cpi["DATE"] < "2000-01-01"]
    with pytest.raises(ValueError):
        boe._join_monthly(bank, cpi)


def test_join_limits_to_common_source_coverage() -> None:
    bank = boe._parse_iadb_csv(BANK_RATE_FIXTURE.read_text())
    cpi = boe._parse_ons_csv(CPI_FIXTURE.read_text())
    expected = boe._join_monthly(bank, cpi)
    cpi = cpi.loc[cpi["DATE"] <= expected["DATE"].iloc[-2]]
    actual = boe._join_monthly(bank, cpi)
    pd.testing.assert_frame_equal(actual, expected.iloc[:-1])


@pytest.mark.parametrize("source", ["bank", "cpi"])
def test_both_official_downloads_retry_transient_failures(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch, source: str,
) -> None:
    fixture = BANK_RATE_FIXTURE if source == "bank" else CPI_FIXTURE
    response = Mock(content=fixture.read_bytes(), status_code=requests.codes.ok)
    request = Mock(side_effect=[requests.Timeout("temporary upstream timeout"), response])
    monkeypatch.setattr(boe.requests, "get", request)
    download = (lambda: boe._download_iadb(boe.BANK_RATE_SERIES)) if source == "bank" else boe._download_ons
    assert download() is response
    assert request.call_count == 2
    assert request.call_args_list[0] == request.call_args_list[1]


def test_ons_outage_cannot_publish_partially_official_data(
    pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    bank_response = Mock(content=BANK_RATE_FIXTURE.read_bytes(), status_code=requests.codes.ok)

    def get(url: str, **kwargs: object) -> Mock:
        if url == boe.BOE_IADB_URL:
            return bank_response
        raise requests.ConnectionError("ONS unavailable")

    monkeypatch.setattr(boe.requests, "get", get)
    result = boe.process(boe.fetch(allow_fallback=True))
    assert result["data_type"].eq("illustrative_fallback").all()
    metadata = json.loads((pipeline_dirs / "processed/boe_rates.meta.json").read_text())
    assert metadata["access_date"] is None
    assert all(source["access_date"] is None for source in metadata["sources"])
