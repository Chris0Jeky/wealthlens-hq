"""Generate dashboard-JSON fixtures for the simulator API endpoint.

Runs a small set of predefined WealthLens-Sim scenarios through
``engine.simulate`` + ``outputs.to_dashboard_json`` and writes one JSON file per
scenario into ``projects/wealthlens-dashboard/data/simulator/``. The FastAPI
``/api/simulator`` router then serves those files statically — the backend never
imports the simulator at runtime (the simulator lives in a separate package), so
this is the reproducible "pipeline" step, exactly like the CSV ``fetch_*`` scripts
in this directory feed ``/api/data``.

**These figures are illustrative estimates over a *synthetic* v0.1 population, not
official forecasts.** Only scenarios whose headline is in a defensible range are
included: the synthetic IHT estimate is a known ~100x overshoot (the synth
population over-states top wealth and applies IHT as-if-at-death to everyone), so
IHT scenarios are intentionally excluded until the synth IHT calibration lands
(tracked in tasks/inbox.md). Do not serve a scenario whose number can't be
sanity-checked against published statistics without a caveat.

Run it after any simulator change:

    python automation/data-pipelines/generate_simulator_dashboards.py

The output is deterministic (seeded synthetic population), so re-running with no
simulator change produces an identical diff. Commit the regenerated JSON.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# The simulator is a sibling package, not a pipeline dependency. Prepend its
# source to the path so we import the in-repo version (not a stale editable
# install) without adding it to requirements.
_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "packages" / "wealthlens-sim"))

import wealthlens_sim  # noqa: E402
from wealthlens_sim.assumptions import load_assumptions  # noqa: E402
from wealthlens_sim.engine import Registries, simulate  # noqa: E402
from wealthlens_sim.outputs import to_dashboard_json  # noqa: E402
from wealthlens_sim.reforms.a_annual_wealth import WealthTaxConfig  # noqa: E402
from wealthlens_sim.rules import FamilySelection, PolicyFamily, Scenario  # noqa: E402
from wealthlens_sim.schema.base import VersionTag  # noqa: E402
from wealthlens_sim.synth import SynthConfig, generate_population  # noqa: E402

OUT_DIR = _REPO / "projects" / "wealthlens-dashboard" / "data" / "simulator"

#: Deterministic synthetic population shared by every scenario (seeded).
_POP_HOUSEHOLDS = 2_000
_POP_SEED = 20

#: Surfaced in every served fixture's ``caveats[]`` — the contract field the chart
#: renders — so the synthetic-population framing reaches a consumer that fetches the
#: scenario payload directly, not only the API listing description.
_SYNTHETIC_POPULATION_CAVEAT = (
    "Illustrative estimate over a synthetic v0.1 population (household microdata "
    "statistically generated and calibrated to published aggregates), not an "
    "official forecast. Treat the figures as indicative, not as a costing."
)


def _version() -> VersionTag:
    return VersionTag(
        macro_baseline_version="NBS-2025",
        policy_version="2026-27",  # the modelled current-law parameter year
        population_version="synth-v0.1",
        # Truthful run identifier — read from the package, not hand-written, so
        # provenance never claims a release that did not produce the numbers.
        wealthlens_sim_version=wealthlens_sim.__version__,
    )


def _wealth_tax(threshold: float = 1_000_000, rate: float = 0.01) -> FamilySelection:
    return FamilySelection(
        family=PolicyFamily.ANNUAL_WEALTH_TAX,
        config=WealthTaxConfig(threshold=threshold, rate=rate),
    )


#: scenario_id -> (display name, list of policy families). The display name flows
#: into the fixture's ``scenario_name``; the backend listing's name must match it
#: (asserted by a drift-guard test).
SCENARIOS: dict[str, tuple[str, list[FamilySelection]]] = {
    "one-percent-wealth-tax": (
        "1% annual wealth tax above £1m",
        [_wealth_tax(rate=0.01)],
    ),
    "two-percent-wealth-tax": (
        "2% annual wealth tax above £1m",
        [_wealth_tax(rate=0.02)],
    ),
}


def build_payloads() -> dict[str, dict[str, Any]]:
    """Build every scenario's dashboard JSON payload (deterministic, no file I/O).

    Separated from :func:`generate` so a staleness test can compare the freshly
    built payloads against the committed fixtures without touching the filesystem.
    """
    population = generate_population(SynthConfig(n_households=_POP_HOUSEHOLDS, seed=_POP_SEED))
    registries = Registries(assumptions=load_assumptions())
    payloads: dict[str, dict[str, Any]] = {}
    for scenario_id, (name, families) in SCENARIOS.items():
        scenario = Scenario(name=name, version_tag=_version(), families=families)
        result = simulate(population, scenario, registries=registries)
        payload = to_dashboard_json(result)
        # Prepend the synthetic-population caveat to whatever the contract already
        # carries (e.g. an incomplete-provenance caveat), so the chart's caveat
        # banner always states these are synthetic estimates.
        payload["caveats"] = [_SYNTHETIC_POPULATION_CAVEAT, *payload["caveats"]]
        payloads[scenario_id] = payload
    return payloads


def generate() -> list[Path]:
    """Write every scenario's dashboard JSON to ``OUT_DIR``; return the paths."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for scenario_id, payload in build_payloads().items():
        path = OUT_DIR / f"{scenario_id}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(path)
    return written


if __name__ == "__main__":
    for written_path in generate():
        print(f"wrote {written_path}")
