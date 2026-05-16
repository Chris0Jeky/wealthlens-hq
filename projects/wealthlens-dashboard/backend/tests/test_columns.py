"""Tests for the dataset columns endpoint."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_csv():
    """Provide a small DataFrame for column metadata tests."""
    df = pd.DataFrame(
        {
            "year": [2020, 2021, 2022],
            "value": [1.5, None, 3.0],
            "region": ["London", "London", "Wales"],
        }
    )
    with patch("app.routers.data._read_csv", return_value=df):
        yield df


def test_columns_returns_200(mock_csv):
    response = client.get("/api/data/wealth-shares/columns")
    assert response.status_code == 200


def test_columns_returns_dataset_name(mock_csv):
    data = client.get("/api/data/wealth-shares/columns").json()
    assert data["dataset"] == "wealth-shares"


def test_columns_returns_row_count(mock_csv):
    data = client.get("/api/data/wealth-shares/columns").json()
    assert data["row_count"] == 3


def test_columns_returns_all_columns(mock_csv):
    data = client.get("/api/data/wealth-shares/columns").json()
    names = [c["name"] for c in data["columns"]]
    assert names == ["year", "value", "region"]


def test_columns_dtype_info(mock_csv):
    data = client.get("/api/data/wealth-shares/columns").json()
    cols = {c["name"]: c for c in data["columns"]}
    assert "int" in cols["year"]["dtype"]
    assert "float" in cols["value"]["dtype"]
    assert cols["region"]["dtype"] in ("object", "str", "string")


def test_columns_null_count(mock_csv):
    data = client.get("/api/data/wealth-shares/columns").json()
    cols = {c["name"]: c for c in data["columns"]}
    assert cols["value"]["null_count"] == 1
    assert cols["year"]["null_count"] == 0


def test_columns_unique_count(mock_csv):
    data = client.get("/api/data/wealth-shares/columns").json()
    cols = {c["name"]: c for c in data["columns"]}
    assert cols["region"]["unique_count"] == 2
    assert cols["year"]["unique_count"] == 3


def test_columns_404_unknown_dataset():
    response = client.get("/api/data/nonexistent/columns")
    assert response.status_code == 404
