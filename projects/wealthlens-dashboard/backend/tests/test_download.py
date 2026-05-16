"""Tests for the CSV download endpoint."""

from __future__ import annotations

from pathlib import Path

import pytest
from app.main import app
from app.routers import data as data_mod
from fastapi.testclient import TestClient

client = TestClient(app)

CSV_CONTENT = "year,value\n2020,1.0\n2021,2.0\n"


@pytest.fixture(autouse=True)
def _fake_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Point DATA_DIR to a temp directory with a sample CSV."""
    csv_file = tmp_path / "wid_wealth_shares_gb.csv"
    csv_file.write_text(CSV_CONTENT, encoding="utf-8")
    monkeypatch.setattr(data_mod, "DATA_DIR", tmp_path)


class TestDownloadEndpoint:
    """GET /api/data/{name}/download should return CSV file."""

    def test_unknown_dataset_returns_404(self) -> None:
        response = client.get("/api/data/nonexistent/download")
        assert response.status_code == 404

    def test_missing_file_returns_503(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.setattr(data_mod, "DATA_DIR", empty_dir)
        response = client.get("/api/data/wealth-shares/download")
        assert response.status_code == 503

    def test_returns_csv_content_type(self) -> None:
        response = client.get("/api/data/wealth-shares/download")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_returns_attachment_header(self) -> None:
        response = client.get("/api/data/wealth-shares/download")
        assert "attachment" in response.headers["content-disposition"]
        assert "wealth-shares.csv" in response.headers["content-disposition"]

    def test_returns_content_length(self) -> None:
        response = client.get("/api/data/wealth-shares/download")
        assert "content-length" in response.headers
        assert int(response.headers["content-length"]) > 0

    def test_csv_content_is_valid(self) -> None:
        response = client.get("/api/data/wealth-shares/download")
        lines = response.text.strip().splitlines()
        assert lines[0] == "year,value"
        assert lines[1].startswith("2020,")
        assert lines[2].startswith("2021,")

    def test_route_not_shadowed_by_get_dataset(self) -> None:
        """Verify /download is reachable and not captured by /{dataset_name}."""
        response = client.get("/api/data/wealth-shares/download")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
