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


def _assert_json_close(actual: object, expected: object, path: str = "") -> None:
    """Recursively compare two JSON structures; floats with tolerance.

    Mirrors the simulator's own golden-file comparison: structure/keys/strings/ints
    are exact, but floats use a relative+absolute tolerance so last-bit numpy/Pareto
    differences across platforms (fixtures generated on one OS, CI on another) do not
    flag a fresh-but-equivalent build as stale.
    """
    assert type(actual) is type(expected), f"type mismatch at {path}: {type(actual)} != {type(expected)}"
    # The type-identity assert above guarantees actual matches expected at runtime;
    # the per-branch isinstance asserts narrow `actual` (typed `object`) for mypy and
    # are no-ops at runtime.
    if isinstance(expected, dict):
        assert isinstance(actual, dict)
        assert actual.keys() == expected.keys(), f"key mismatch at {path}: {set(actual)} != {set(expected)}"
        for key in expected:
            _assert_json_close(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        assert isinstance(actual, list)
        assert len(actual) == len(expected), f"length mismatch at {path}"
        for i, (a, e) in enumerate(zip(actual, expected, strict=True)):
            _assert_json_close(a, e, f"{path}[{i}]")
    elif isinstance(expected, float):
        assert isinstance(actual, float)
        assert abs(actual - expected) <= 1e-9 * max(1.0, abs(expected)) + 1e-12, (
            f"float mismatch at {path}: {actual} != {expected}"
        )
    else:
        assert actual == expected, f"value mismatch at {path}: {actual!r} != {expected!r}"


def test_committed_fixtures_match_a_fresh_generation() -> None:
    """Every committed fixture equals a fresh deterministic build (no staleness)."""
    fresh = build_payloads()
    for scenario_id, payload in fresh.items():
        path = OUT_DIR / f"{scenario_id}.json"
        assert path.exists(), f"missing fixture for {scenario_id}"
        committed = json.loads(path.read_text(encoding="utf-8"))
        try:
            _assert_json_close(committed, payload)
        except AssertionError as exc:
            raise AssertionError(
                f"projects/wealthlens-dashboard/data/simulator/{scenario_id}.json is stale — "
                "re-run automation/data-pipelines/generate_simulator_dashboards.py and commit"
                f" ({exc})"
            ) from exc


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
