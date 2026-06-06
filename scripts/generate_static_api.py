"""Generate static JSON files that mimic the backend API responses.

Reads processed CSVs and writes JSON files to the frontend public
directory so the Vue app can work without a live backend (GitHub Pages).

Output structure:
  frontend/public/data/datasets.json        — list of dataset names
  frontend/public/data/{slug}.json          — paginated rows
  frontend/public/data/{slug}-metadata.json — source citation + columns

Usage: python scripts/generate_static_api.py
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "projects" / "wealthlens-dashboard" / "data" / "processed"
OUT_DIR = ROOT / "projects" / "wealthlens-dashboard" / "frontend" / "public" / "data"

# Simulator scenario fixtures (the same files the backend /api/simulator serves)
# are mirrored into the static build so /simulator works without a backend.
SIM_SRC_DIR = ROOT / "projects" / "wealthlens-dashboard" / "data" / "simulator"
SIM_OUT_DIR = OUT_DIR / "simulator"
BACKEND_SIMULATOR = (
    ROOT / "projects" / "wealthlens-dashboard" / "backend" / "app" / "routers" / "simulator.py"
)
# Mirrors backend app/routers/simulator.py _REQUIRED_KEYS: a fixture must carry
# these or the build fails, rather than publishing a broken contract statically.
# `provenance` is included so the statically-served payload carries the
# assumptions_consumed citations the scenario page renders (kept in sync with the
# backend guard, which also requires it).
_SIM_REQUIRED_KEYS = frozenset(
    {"schema_version", "total_revenue_gbp_bn", "caveats", "interval_method", "provenance"}
)

DATASETS: dict[str, str] = {
    "wealth-shares": "wid_wealth_shares_gb.csv",
    "housing-affordability": "ons_housing_affordability_by_region.csv",
    "wealth-by-decile": "ons_wealth_by_decile.csv",
    "cgt-concentration": "hmrc_cgt_concentration.csv",
    "productivity-pay": "productivity_pay_gap.csv",
    "gdhi-by-region": "ons_gdhi_by_region.csv",
    "tax-composition": "tax_composition.csv",
    "boe-rates": "boe_rates.csv",
    "child-poverty": "child_poverty_by_region.csv",
    "generational-wealth": "generational_wealth_gap.csv",
}

DATASET_META: dict[str, dict[str, str]] = {
    "wealth-shares": {
        "description": "Top 1%/10% wealth shares in GB",
        "source": "World Inequality Database",
        "source_url": "https://wid.world/",
        "access_date": "2026-05-14",
    },
    "housing-affordability": {
        "description": "House price to earnings ratio by region",
        "source": "ONS",
        "source_url": "https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/ratioofhousepricetoworkplacebasedearningslowerquartileandmedian",
        "access_date": "2026-05-14",
    },
    "wealth-by-decile": {
        "description": "Total net wealth by decile",
        "source": "ONS Wealth and Assets Survey",
        "source_url": "https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/datasets/totalwealthwealthingreatbritain",
        "access_date": "2026-05-14",
    },
    "cgt-concentration": {
        "description": "Capital gains by size of gain",
        "source": "HMRC",
        "source_url": "https://www.gov.uk/government/statistics/capital-gains-tax-statistics",
        "access_date": "2026-05-14",
    },
    "productivity-pay": {
        "description": "UK productivity vs. real pay, indexed to 100 at 1997",
        "source": "ONS Labour Productivity & AWE",
        "source_url": "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/labourproductivity/timeseries/lzvd/prdy",
        "access_date": "2026-05-16",
    },
    "gdhi-by-region": {
        "description": "Gross disposable household income per head by region",
        "source": "ONS Regional GDHI",
        "source_url": "https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome/datasets/regionalgrossdisposablehouseholdincomegdhi",
        "access_date": "2026-05-16",
    },
    "tax-composition": {
        "description": "UK tax revenue composition: work taxes vs wealth taxes",
        "source": "HMRC Tax and NIC Receipts",
        "source_url": "https://www.gov.uk/government/statistics/hmrc-tax-and-nics-receipts-for-the-uk",
        "access_date": "2026-05-16",
    },
    "boe-rates": {
        "description": "Bank Rate and CPI annual inflation",
        "source": "Bank of England Interactive Analytical Database",
        "source_url": "https://www.bankofengland.co.uk/boeapps/database/",
        "access_date": "2026-05-16",
    },
    "child-poverty": {
        "description": "Child poverty rates by UK region (after housing costs)",
        "source": "DWP/HMRC Children in Low Income Families",
        "source_url": "https://www.gov.uk/government/statistics/children-in-low-income-families-local-area-statistics-2014-to-2023",
        "access_date": "2026-05-16",
    },
    "generational-wealth": {
        "description": "Median household wealth by generation at equivalent ages",
        "source": "Resolution Foundation / ONS Wealth and Assets Survey",
        "source_url": "https://www.resolutionfoundation.org/publications/",
        "access_date": "2026-05-16",
    },
}


def _extract_percentile(variable: str) -> str:
    """Extract percentile key from WID variable name.

    e.g. 'shweal_p99p100_992_j' -> 'p99p100'
         'shweal_p90p100_992_j' -> 'p90p100'
    """
    match = re.search(r"(p\d+p\d+)", variable)
    return match.group(1) if match else variable


# Dataset-specific post-processing hooks.
# Each function receives a list of row dicts and returns a modified list.
def _postprocess_wealth_shares(records: list[dict]) -> list[dict]:
    """Add a 'percentile' field derived from the WID 'variable' column.

    The WealthSharesChart.vue component filters rows by r.percentile,
    but the source CSV only has the full WID variable name.  This derives
    the short percentile key (e.g. 'p99p100') so the frontend works
    without needing to parse variable names at runtime.
    """
    for row in records:
        if row.get("variable"):
            row["percentile"] = _extract_percentile(row["variable"])
    return records


_POSTPROCESSORS: dict[str, Callable[[list[dict[str, Any]]], list[dict[str, Any]]]] = {
    "wealth-shares": _postprocess_wealth_shares,
}


def _read_csv_as_records(path: Path, slug: str = "") -> list[dict]:
    """Read a CSV and return list of row dicts, converting NaN to None.

    If a post-processor is registered for the given slug, it is applied
    after CSV parsing to add derived fields needed by the frontend.
    """
    import pandas as pd

    df = pd.read_csv(path)
    df = df.where(pd.notna(df), other=None)
    records = df.to_dict(orient="records")

    if slug in _POSTPROCESSORS:
        records = _POSTPROCESSORS[slug](records)

    return records


def _load_simulator_scenarios() -> dict[str, dict[str, str]]:
    """Read the backend's SIMULATOR_SCENARIOS registry without importing it.

    The registry (id -> {name, description}) is the single source of truth for
    which scenarios the API exposes. We parse the module with ``ast`` and
    ``literal_eval`` the dict literal so the static index cannot drift from the
    API and so this script needs no FastAPI/backend dependency at build time.
    """
    tree = ast.parse(BACKEND_SIMULATOR.read_text(encoding="utf-8"))
    # Module-level statements only (not ast.walk): the registry is a top-level
    # binding, and scanning only tree.body avoids matching a same-named symbol in
    # an inner scope (function/TYPE_CHECKING block) after a future refactor.
    for node in tree.body:
        target = None
        value = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target, value = node.target.id, node.value
        elif (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            target, value = node.targets[0].id, node.value
        if target == "SIMULATOR_SCENARIOS" and value is not None:
            try:
                return ast.literal_eval(value)
            except ValueError as e:
                raise RuntimeError(
                    f"SIMULATOR_SCENARIOS in {BACKEND_SIMULATOR} is not a static literal: {e}"
                ) from e
    raise RuntimeError(f"SIMULATOR_SCENARIOS not found in {BACKEND_SIMULATOR}")


def generate_simulator_static() -> int:
    """Mirror the registered simulator scenarios into the static build.

    Writes ``{id}.json`` (the same dashboard contract the API serves) plus a
    ``scenarios.json`` index matching ``GET /api/simulator/`` so the frontend's
    static path is byte-for-byte equivalent to the API path. Returns the count
    of scenarios published.
    """
    scenarios = _load_simulator_scenarios()
    SIM_OUT_DIR.mkdir(parents=True, exist_ok=True)
    index: list[dict[str, str]] = []
    for scenario_id, meta in scenarios.items():
        src = SIM_SRC_DIR / f"{scenario_id}.json"
        if not src.exists():
            # Fail loud: a registered scenario with no fixture would silently drop
            # from scenarios.json, diverging from the API (list_scenarios lists every
            # registered scenario; get_scenario 503s on a missing fixture). Failing
            # the export beats a partial publish that hides a policy scenario.
            raise FileNotFoundError(
                f"Simulator fixture for registered scenario '{scenario_id}' not found at {src}. "
                "Run automation/data-pipelines/generate_simulator_dashboards.py first."
            )
        # Validate before publishing: a well-formed JSON object carrying the same
        # required contract keys the backend enforces, so a malformed or incomplete
        # fixture fails the build instead of being served statically as a broken
        # contract.
        try:
            payload = json.loads(src.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Malformed JSON in simulator fixture '{scenario_id}': {e}") from e
        if not isinstance(payload, dict) or not _SIM_REQUIRED_KEYS.issubset(payload):
            present = set(payload) if isinstance(payload, dict) else set()
            raise ValueError(
                f"Simulator fixture '{scenario_id}' is missing required contract keys: "
                f"{sorted(_SIM_REQUIRED_KEYS - present)}"
            )
        (SIM_OUT_DIR / f"{scenario_id}.json").write_text(json.dumps(payload), encoding="utf-8")
        index.append({"id": scenario_id, "name": meta["name"], "description": meta["description"]})
        print(f"  OK simulator {scenario_id}")
    (SIM_OUT_DIR / "scenarios.json").write_text(
        json.dumps({"scenarios": index}), encoding="utf-8"
    )
    print(f"Generated {len(index)}/{len(scenarios)} simulator scenarios in {SIM_OUT_DIR}")
    return len(index)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    available: list[str] = []
    errors: list[str] = []

    for slug, filename in DATASETS.items():
        csv_path = DATA_DIR / filename
        if not csv_path.exists():
            errors.append(f"  SKIP {slug}: {csv_path} not found")
            continue

        records = _read_csv_as_records(csv_path, slug=slug)
        available.append(slug)

        # Paginated data response (all rows in one page)
        data_response = {
            "data": records,
            "page": 1,
            "limit": len(records),
            "total": len(records),
            "total_pages": 1,
        }
        data_path = OUT_DIR / f"{slug}.json"
        data_path.write_text(json.dumps(data_response), encoding="utf-8")

        # Metadata response
        meta = DATASET_META.get(slug, {})
        columns = list(records[0].keys()) if records else []
        meta_response = {
            "name": slug,
            "description": meta.get("description", ""),
            "source": meta.get("source", ""),
            "source_url": meta.get("source_url", ""),
            "access_date": meta.get("access_date", ""),
            "row_count": len(records),
            "columns": columns,
        }
        meta_path = OUT_DIR / f"{slug}-metadata.json"
        meta_path.write_text(json.dumps(meta_response), encoding="utf-8")

        print(f"  OK {slug}: {len(records)} rows")

    # Dataset listing
    listing = {"datasets": available}
    listing_path = OUT_DIR / "datasets.json"
    listing_path.write_text(json.dumps(listing), encoding="utf-8")

    # All metadata combined
    all_meta = {"datasets": []}
    for slug in available:
        meta_path = OUT_DIR / f"{slug}-metadata.json"
        all_meta["datasets"].append(json.loads(meta_path.read_text(encoding="utf-8")))
    all_meta_path = OUT_DIR / "all-metadata.json"
    all_meta_path.write_text(json.dumps(all_meta), encoding="utf-8")

    # Freshness data — uses CSV file modification times
    freshness_threshold_fresh = 168  # 7 days in hours
    freshness_threshold_stale = 720  # 30 days in hours
    now = datetime.now(tz=UTC)
    datasets_freshness: dict[str, dict] = {}
    for slug in available:
        csv_path = DATA_DIR / DATASETS[slug]
        mtime = os.path.getmtime(csv_path)
        last_updated = datetime.fromtimestamp(mtime, tz=UTC)
        # Clamp at 0 (same as the live /api/data/freshness endpoint): a future file
        # mtime would otherwise emit a negative age into the static freshness.json.
        age_hours = max(0.0, (now - last_updated).total_seconds() / 3600)
        if age_hours <= freshness_threshold_fresh:
            status = "fresh"
        elif age_hours <= freshness_threshold_stale:
            status = "stale"
        else:
            status = "expired"
        datasets_freshness[slug] = {
            "last_updated": last_updated.isoformat(),
            "age_hours": round(age_hours, 1),
            "status": status,
        }
    freshness_response = {
        "datasets": datasets_freshness,
        "thresholds": {
            "fresh_hours": freshness_threshold_fresh,
            "stale_hours": freshness_threshold_stale,
        },
    }
    freshness_path = OUT_DIR / "freshness.json"
    freshness_path.write_text(json.dumps(freshness_response), encoding="utf-8")

    # Simulator scenarios (independent of the CSV datasets above).
    generate_simulator_static()

    print(f"\nGenerated static API for {len(available)}/{len(DATASETS)} datasets in {OUT_DIR}")
    if errors:
        print("\n".join(errors))
        if not available:
            sys.exit(1)


if __name__ == "__main__":
    main()
