"""Tests for the /api/simulator endpoints.

The simulator scenario JSON is precomputed by
``automation/data-pipelines/generate_simulator_dashboards.py`` and served
statically. These tests assert
the listing, the pass-through of the dashboard contract (intervals + provenance +
caveats + interval_method), and the 404 / 422 error paths.
"""

from __future__ import annotations

from app.main import app
from app.routers.simulator import SIMULATOR_DIR, SIMULATOR_SCENARIOS
from fastapi.testclient import TestClient

client = TestClient(app)

_KNOWN_ID = "one-percent-wealth-tax"


class TestListScenarios:
    def test_returns_200(self) -> None:
        response = client.get("/api/simulator/")
        assert response.status_code == 200

    def test_lists_every_registered_scenario(self) -> None:
        body = client.get("/api/simulator/").json()
        ids = {s["id"] for s in body["scenarios"]}
        assert ids == set(SIMULATOR_SCENARIOS)
        for scenario in body["scenarios"]:
            assert scenario["name"]
            assert scenario["description"]

    def test_sets_cache_header(self) -> None:
        response = client.get("/api/simulator/")
        assert "max-age" in response.headers.get("cache-control", "")


class TestGetScenario:
    def test_returns_200_for_known_scenario(self) -> None:
        response = client.get(f"/api/simulator/scenarios/{_KNOWN_ID}")
        assert response.status_code == 200

    def test_passes_through_the_dashboard_contract(self) -> None:
        body = client.get(f"/api/simulator/scenarios/{_KNOWN_ID}").json()
        # The data-integrity fields a chart must render are present and unmodified.
        assert body["schema_version"] == "1.3"
        assert isinstance(body["provenance_complete"], bool)
        assert isinstance(body["caveats"], list)
        assert body["interval_method"] in {"alpha_sweep", "monte_carlo"}
        # The headline interval is a low <= central <= high band.
        total = body["total_revenue_gbp_bn"]
        assert set(total) == {"low", "central", "high"}
        assert total["low"] <= total["central"] <= total["high"]
        assert body["households_scored"] > 0
        assert len(body["revenue_by_decile"]) == 10

    def test_404_for_unknown_scenario(self) -> None:
        response = client.get("/api/simulator/scenarios/no-such-scenario")
        assert response.status_code == 404

    def test_422_for_malformed_scenario_id(self) -> None:
        # Uppercase violates the lowercase/digit/hyphen path pattern.
        response = client.get("/api/simulator/scenarios/INVALID_ID")
        assert response.status_code == 422

    def test_503_when_registered_scenario_file_is_missing(self, monkeypatch) -> None:
        # A scenario in the registry whose JSON has not been generated -> 503,
        # not a 404 or an opaque 500.
        monkeypatch.setitem(
            SIMULATOR_SCENARIOS, "ungenerated-scenario", {"name": "x", "description": "y"}
        )
        try:
            response = client.get("/api/simulator/scenarios/ungenerated-scenario")
            assert response.status_code == 503
        finally:
            SIMULATOR_SCENARIOS.pop("ungenerated-scenario", None)

    def test_every_registered_scenario_has_a_generated_file(self) -> None:
        # Guard against registry/generator drift: each registered id must have a file.
        for scenario_id in SIMULATOR_SCENARIOS:
            assert (SIMULATOR_DIR / f"{scenario_id}.json").exists(), scenario_id
