"""Tests for dataset name path parameter validation.

Verifies that:
- Valid dataset names (lowercase, digits, hyphens) pass validation.
- Malformed names (path traversal, spaces, uppercase, special chars) get 422.
- Valid-format but unknown dataset names get 404.
"""

from __future__ import annotations

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


# ---------------------------------------------------------------------------
# Valid names — should reach the handler (200 if CSV exists, 503 if missing)
# ---------------------------------------------------------------------------


class TestValidDatasetNames:
    """Dataset names matching the regex should pass validation."""

    @pytest.mark.parametrize(
        "name",
        [
            "wealth-shares",
            "housing-affordability",
            "wealth-by-decile",
            "cgt-concentration",
        ],
    )
    def test_known_dataset_passes_validation(self, name: str) -> None:
        """Known datasets return 200 (data present) or 503 (CSV missing)."""
        response = client.get(f"/api/data/{name}")
        assert response.status_code in (200, 503)

    @pytest.mark.parametrize(
        "name",
        [
            "wealth-shares",
            "housing-affordability",
        ],
    )
    def test_known_dataset_metadata_passes_validation(self, name: str) -> None:
        """Known dataset metadata returns 200 or 503."""
        response = client.get(f"/api/data/{name}/metadata")
        assert response.status_code in (200, 503)


# ---------------------------------------------------------------------------
# Invalid names — should be rejected with 422 before hitting the handler
# ---------------------------------------------------------------------------


class TestInvalidDatasetNames:
    """Malformed dataset names must be rejected with 422."""

    @pytest.mark.parametrize(
        "name",
        [
            "foo bar",
            "FOO",
            "WEALTH-SHARES",
            "wealth_shares",
            "wealth.shares",
            "a" * 51,  # exceeds 50-char limit
        ],
    )
    def test_invalid_name_returns_422(self, name: str) -> None:
        """Names with invalid characters or length get 422."""
        response = client.get(f"/api/data/{name}")
        assert response.status_code == 422, (
            f"Expected 422 for '{name}', got {response.status_code}"
        )

    @pytest.mark.parametrize(
        "name",
        [
            "../etc/passwd",
            "<script>alert(1)</script>",
        ],
    )
    def test_path_traversal_blocked(self, name: str) -> None:
        """Path traversal and HTML injection never reach the handler (404 or 422)."""
        response = client.get(f"/api/data/{name}")
        assert response.status_code in (404, 422), (
            f"Expected 404 or 422 for '{name}', got {response.status_code}"
        )

    @pytest.mark.parametrize(
        "name",
        [
            "FOO",
            "wealth_shares",
            "<script>",
            "a" * 51,
        ],
    )
    def test_invalid_name_metadata_returns_422(self, name: str) -> None:
        """Metadata endpoint also rejects invalid names with 422."""
        response = client.get(f"/api/data/{name}/metadata")
        assert response.status_code == 422, (
            f"Expected 422 for '{name}', got {response.status_code}"
        )

    def test_path_traversal_metadata_blocked(self) -> None:
        """Path traversal in metadata endpoint is blocked (404 or 422)."""
        response = client.get("/api/data/../etc/passwd/metadata")
        assert response.status_code in (404, 422)


# ---------------------------------------------------------------------------
# Valid format but unknown — should get past validation, return 404
# ---------------------------------------------------------------------------


class TestUnknownDatasetNames:
    """Names that pass regex but are not in DATASETS should return 404."""

    @pytest.mark.parametrize(
        "name",
        [
            "not-a-real-dataset",
            "foo-bar-baz",
            "dataset-999",
        ],
    )
    def test_unknown_dataset_returns_404(self, name: str) -> None:
        """Valid-format but unknown names get 404 from the handler."""
        response = client.get(f"/api/data/{name}")
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "name",
        [
            "not-a-real-dataset",
            "foo-bar-baz",
        ],
    )
    def test_unknown_dataset_metadata_returns_404(self, name: str) -> None:
        """Valid-format but unknown names get 404 from metadata handler."""
        response = client.get(f"/api/data/{name}/metadata")
        assert response.status_code == 404
