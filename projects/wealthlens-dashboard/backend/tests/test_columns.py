"""Tests for the columns endpoint."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

SAMPLE_DF = pd.DataFrame({"year": [2020, 2021], "value": [1.0, 2.0], "region": ["London", "SE"]})


class TestColumnsEndpoint:
    """GET /api/data/{name}/columns should return column info."""

    def test_unknown_dataset_returns_404(self) -> None:
        response = client.get("/api/data/nonexistent/columns")
        assert response.status_code == 404

    @patch("app.routers.data._read_csv", return_value=SAMPLE_DF)
    def test_returns_column_names(self, mock_read) -> None:
        response = client.get("/api/data/wealth-shares/columns")
        assert response.status_code == 200
        body = response.json()
        assert body["dataset"] == "wealth-shares"
        col_names = [c["name"] for c in body["columns"]]
        assert col_names == ["year", "value", "region"]

    @patch("app.routers.data._read_csv", return_value=SAMPLE_DF)
    def test_returns_inferred_dtypes(self, mock_read) -> None:
        response = client.get("/api/data/wealth-shares/columns")
        body = response.json()
        dtypes = {c["name"]: c["dtype"] for c in body["columns"]}
        assert dtypes["year"] == "integer"
        assert dtypes["value"] == "float"
        assert dtypes["region"] == "string"
