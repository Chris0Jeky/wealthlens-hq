"""Child-poverty figures must come from the recorded official AHC tables."""
from __future__ import annotations

import io
import json
import xml.etree.ElementTree as ET
import zipfile
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

import fetch_child_poverty as cp
import pandas as pd
import pytest
import requests

FIXTURE = Path(__file__).parent / "fixtures" / "hbai-regional-ahc-recorded.ods"


def workbook_with(old: bytes, new: bytes) -> bytes:
    """Mutate recorded source text without making up alternative observations."""
    with zipfile.ZipFile(FIXTURE) as source:
        content = source.read("content.xml")
    assert old in content
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as target:
        target.writestr("content.xml", content.replace(old, new))
    return out.getvalue()


def test_reads_ahc_rates_and_counts_at_published_precision():
    frame = cp.parse_workbook(FIXTURE.read_bytes())
    assert set(frame.region) == set(cp.REGIONS.values())
    assert len(frame) == len(cp.REGIONS)
    # Independent check against the recorded DISPLAY text, not hidden decimals.
    with zipfile.ZipFile(FIXTURE) as z:
        root = ET.fromstring(z.read("content.xml"))
    tables = root.findall(".//table:table", cp.NS)
    expected = {}
    for table in tables:
        ahc = False
        values = {}
        for row in table.findall("table:table-row", cp.NS):
            cells = ["".join(c.itertext()).strip() for c in list(row)]
            if cells[0] == "After Housing Costs":
                ahc = True
            if ahc and cells[0] in cp.REGIONS:
                values[cp.REGIONS[cells[0]]] = Decimal(cells[1])
            if ahc and cells[0].startswith("All children ("):
                values["UK"] = Decimal(cells[1])
        expected[table.get(cp.TABLE_NAME)] = values
    by_region = frame.set_index("region")
    for region in cp.REGIONS.values():
        assert by_region.loc[region, "child_poverty_pct"] == expected["4_16ts"][region]
        assert by_region.loc[region, "children_in_poverty"] == expected["4_17ts"][region] * 1_000_000
    assert frame.national_avg_pct.nunique() == 1
    assert frame.national_avg_pct.iloc[0] == expected["4_16ts"]["UK"]
    assert (frame.above_national_avg == (frame.child_poverty_pct > frame.national_avg_pct)).all()


@pytest.mark.parametrize(("old", "new"), [
    (b"After Housing Costs", b"Before Housing Costs"),
    (b"21/22-23/24", b"period unavailable"),
    (b"North East", b"Unrecognised region"),
    (b"Percentage of children", b"Composition of children"),
    (b"Number of children (millions)", b"Different units"),
    (b"Region/Country (3-year average)", b"Different statistic"),
])
def test_refuses_wrong_measure_period_geography_or_statistic(old, new):
    with pytest.raises(ValueError):
        cp.parse_workbook(workbook_with(old, new))


def test_refuses_unavailable_rate():
    with zipfile.ZipFile(FIXTURE) as z:
        content = z.read("content.xml")
    root = ET.fromstring(content)
    table = root.findall(".//table:table", cp.NS)[0]
    ahc = False
    for row in table.findall("table:table-row", cp.NS):
        cells = list(row)
        label = "".join(cells[0].itertext()).strip()
        ahc = ahc or label == "After Housing Costs"
        if ahc and label in cp.REGIONS:
            for node in cells[1].iter():
                if node.tag == cp.TEXT_P:
                    node.text = "[u]"
            break
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("content.xml", ET.tostring(root))
    with pytest.raises(ValueError):
        cp.parse_workbook(out.getvalue())


def test_failed_fetch_does_not_publish_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(cp, "RAW_DIR", tmp_path)
    monkeypatch.setattr(cp.requests, "get", Mock(side_effect=requests.RequestException("offline")))
    with pytest.raises(requests.RequestException):
        cp.fetch()
    assert not list(tmp_path.iterdir())


def test_official_writer_records_table_url_date_and_measure(tmp_path, monkeypatch):
    monkeypatch.setattr(cp, "PROCESSED_DIR", tmp_path)
    frame = cp.parse_workbook(FIXTURE.read_bytes())
    cp.process(frame, is_fallback=False)
    meta = json.loads((tmp_path / "child_poverty_by_region.meta.json").read_text())
    assert meta["data_type"] == "live_ons"
    assert meta["source_url"] == cp.SOURCE_URL
    assert meta["download_url"] == cp.DOWNLOAD_URL
    assert meta["tables"] == ["4.16ts", "4.17ts"]
    assert meta["period"] == cp.PERIOD
    assert meta["access_date"] == cp.ACCESS_DATE
    assert "after housing costs" in meta["measure"]
    pd.testing.assert_frame_equal(frame, pd.read_csv(tmp_path / "child_poverty_by_region.csv"))


def test_static_api_preserves_fetched_citation_and_observations(tmp_path, monkeypatch):
    """The public export must use the fetched sidecar, including its access date."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "child_static_api", Path(__file__).resolve().parents[3] / "scripts/generate_static_api.py"
    )
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    processed = tmp_path / "processed"
    out = tmp_path / "public"
    monkeypatch.setattr(cp, "PROCESSED_DIR", processed)
    frame = cp.parse_workbook(FIXTURE.read_bytes())
    cp.process(frame, is_fallback=False)
    monkeypatch.setattr(api, "DATA_DIR", processed)
    monkeypatch.setattr(api, "OUT_DIR", out)
    monkeypatch.setattr(api, "DATASETS", {"child-poverty": "child_poverty_by_region.csv"})
    monkeypatch.setattr(api, "generate_simulator_static", lambda: None)
    api.main()
    metadata = json.loads((out / "child-poverty-metadata.json").read_text())
    assert metadata["source_url"] == cp.SOURCE_URL
    assert metadata["access_date"] == cp.ACCESS_DATE
    assert metadata["tables"] == ["4.16ts", "4.17ts"]
    assert metadata["data_type"] == "live_ons"
    assert metadata["period"] == cp.PERIOD
    exported = json.loads((out / "child-poverty.json").read_text())["data"]
    assert exported == frame.to_dict(orient="records")
    assert json.loads((out / "all-metadata.json").read_text())["datasets"] == [metadata]
    assert set(pd.read_csv(out / "child-poverty.csv").data_type) == {"live_ons"}


def test_chart_artifact_cites_ahc_source_and_period(tmp_path, monkeypatch):
    monkeypatch.setattr(cp, "CHART_DIR", tmp_path)
    cp.build_chart(cp.parse_workbook(FIXTURE.read_bytes()))
    html = (tmp_path / "child_poverty_by_region.html").read_text(encoding="utf-8")
    assert "DWP/HMRC Children in Low Income Families" not in html
    assert "UK (2022/23)" not in html
    assert cp.PERIOD in html
    assert cp.SOURCE_URL in html
    assert cp.ACCESS_DATE in html
    assert "after housing costs" in html


def test_live_and_static_catalogues_cite_the_same_official_tables():
    """Both serving modes must agree with the pipeline's actual source."""
    import ast
    from datetime import date

    root = Path(__file__).resolve().parents[3]
    paths = [
        root / "projects/wealthlens-dashboard/backend/app/routers/data.py",
        root / "scripts/generate_static_api.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        node = next(n for n in tree.body if isinstance(n, ast.AnnAssign) and n.target.id == "DATASET_META")
        meta = ast.literal_eval(node.value)["child-poverty"]
        assert meta["source_url"] == cp.SOURCE_URL
        assert meta["source"] == cp.SOURCE
        assert "three-year average" in meta["description"]
        # Catalogue dates identify this checked-in snapshot, not a new live fetch.
        date.fromisoformat(meta["access_date"])
