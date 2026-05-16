"""Tests for the CSV download endpoint."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_DF = pd.DataFrame({"year": [2020, 2021], "value": [1.0, 2.0]})


class TestDownloadEndpoint:
    """GET /api/data/{name}/download should return CSV file."""

    def test_unknown_dataset_returns_404(self) -> None:
        response = client.get("/api/data/nonexistent/download")
        assert response.status_code == 404

    @patch("app.routers.data._read_csv", return_value=SAMPLE_DF)
    def test_returns_csv_content_type(self, mock_read) -> None:  # noqa: ANN001
        response = client.get("/api/data/wealth-shares/download")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    @patch("app.routers.data._read_csv", return_value=SAMPLE_DF)
    def test_returns_attachment_header(self, mock_read) -> None:  # noqa: ANN001
        response = client.get("/api/data/wealth-shares/download")
        assert "attachment" in response.headers["content-disposition"]
        assert "wealth-shares.csv" in response.headers["content-disposition"]

    @patch("app.routers.data._read_csv", return_value=SAMPLE_DF)
    def test_csv_content_is_valid(self, mock_read) -> None:  # noqa: ANN001
        response = client.get("/api/data/wealth-shares/download")
        lines = response.text.strip().splitlines()
        assert lines[0] == "year,value"
        assert lines[1] == "2020,1.0"
        assert lines[2] == "2021,2.0"
