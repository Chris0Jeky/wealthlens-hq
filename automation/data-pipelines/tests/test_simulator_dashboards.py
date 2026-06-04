"""Tests for the simulator dashboard generator.

The generator is deterministic (seeded synth population + fixed registries), so the
committed fixtures under ``projects/wealthlens-dashboard/data/simulator/`` must
equal a fresh run. This turns "forgot to regenerate after a simulator change" from
a silent data-staleness bug into a test failure.

Requires the in-repo ``wealthlens_sim`` package, which the generator puts on the
path via its own ``sys.path`` shim when imported.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add the pipeline dir to the path so we can import the generator by module name
# (matches the convention in test_validate.py).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generate_simulator_dashboards import (
    OUT_DIR,
    SCENARIOS,
    build_payloads,
)


def test_committed_fixtures_match_a_fresh_generation() -> None:
    """Every committed fixture equals a fresh deterministic build (no staleness)."""
    fresh = build_payloads()
    for scenario_id, payload in fresh.items():
        path = OUT_DIR / f"{scenario_id}.json"
        assert path.exists(), f"missing fixture for {scenario_id}"
        committed = json.loads(path.read_text(encoding="utf-8"))
        assert committed == payload, (
            f"projects/wealthlens-dashboard/data/simulator/{scenario_id}.json is stale — "
            "re-run automation/data-pipelines/generate_simulator_dashboards.py and commit"
        )


def test_no_orphan_fixtures() -> None:
    """No fixture on disk lacks a scenario in the generator (and vice versa)."""
    on_disk = {p.stem for p in OUT_DIR.glob("*.json")}
    assert on_disk == set(SCENARIOS)


def test_headline_revenue_is_plausibly_scaled() -> None:
    """A coarse data-plausibility floor: no scenario should publish an absurd

    headline (the synth IHT ~100x overshoot is excluded for exactly this reason).
    A 1-2% wealth tax over GB should be tens of £bn, not hundreds or thousands.
    """
    for scenario_id, payload in build_payloads().items():
        central = payload["total_revenue_gbp_bn"]["central"]
        assert 0 <= central < 200, f"{scenario_id} headline {central} £bn looks implausible"
