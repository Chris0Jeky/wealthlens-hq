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
        # The exact schema_version is pinned by the regeneration guard (in the
        # generator's own tests); here we only require it is present + non-empty, so
        # a simulator schema bump doesn't break the bridge test spuriously.
        assert isinstance(body["schema_version"], str) and body["schema_version"]
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

    def test_503_when_payload_is_malformed(self, monkeypatch, tmp_path) -> None:
        # A registered scenario whose file is valid JSON but NOT a dashboard
        # contract (missing required keys) must 503, not be served as if valid.
        monkeypatch.setattr("app.routers.simulator.SIMULATOR_DIR", tmp_path)
        monkeypatch.setitem(SIMULATOR_SCENARIOS, "malformed", {"name": "x", "description": "y"})
        (tmp_path / "malformed.json").write_text('{"not": "a contract"}', encoding="utf-8")
        try:
            response = client.get("/api/simulator/scenarios/malformed")
            assert response.status_code == 503
        finally:
            SIMULATOR_SCENARIOS.pop("malformed", None)

    def test_503_when_provenance_missing(self, monkeypatch, tmp_path) -> None:
        # provenance is a required key (the scenario page renders its citations);
        # a payload that has the other keys but omits provenance must 503 rather
        # than be served and crash the client render.
        monkeypatch.setattr("app.routers.simulator.SIMULATOR_DIR", tmp_path)
        monkeypatch.setitem(SIMULATOR_SCENARIOS, "noprov", {"name": "x", "description": "y"})
        (tmp_path / "noprov.json").write_text(
            '{"schema_version": "1.3", "total_revenue_gbp_bn": {"low": 1, "central": 2, '
            '"high": 3}, "caveats": [], "interval_method": "alpha_sweep"}',
            encoding="utf-8",
        )
        try:
            response = client.get("/api/simulator/scenarios/noprov")
            assert response.status_code == 503
        finally:
            SIMULATOR_SCENARIOS.pop("noprov", None)


class TestRegistryDriftGuards:
    """The backend registry and the generator's fixtures must not diverge."""

    def test_files_and_registry_match_both_ways(self) -> None:
        on_disk = {p.stem for p in SIMULATOR_DIR.glob("*.json")}
        assert on_disk == set(SIMULATOR_SCENARIOS), (
            "data/simulator/*.json must match the SIMULATOR_SCENARIOS registry exactly "
            "(orphan fixtures or un-generated scenarios)"
        )

    def test_listing_name_matches_the_served_scenario_name(self) -> None:
        # The listing name is hardcoded separately from the generator, which sets the
        # fixture's scenario_name. They must agree, or the list advertises a label the
        # served contract contradicts.
        for scenario_id, meta in SIMULATOR_SCENARIOS.items():
            body = client.get(f"/api/simulator/scenarios/{scenario_id}").json()
            assert body["scenario_name"] == meta["name"], scenario_id
