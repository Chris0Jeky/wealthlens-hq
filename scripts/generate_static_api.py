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
import re
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
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

DATASET_META: dict[str, dict[str, Any]] = {
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
        "description": "HBAI regional relative low income after housing costs, 2021/22 to 2023/24 (three-year average)",
        "source": "DWP Households Below Average Income (HBAI), tables 4.16ts and 4.17ts",
        "source_url": "https://www.gov.uk/government/statistics/households-below-average-income-for-financial-years-ending-1995-to-2024",
        "access_date": "2026-10-22",
        "download_url": "https://assets.publishing.service.gov.uk/media/6836dae29411f0341f323689/HBAI_2324_ods_table_pack.zip",
        "tables": ["4.16ts", "4.17ts"],
        "period": "2021/22 to 2023/24 (three-year average)",
        "measure": "Children below 60% of contemporary median equivalised disposable household income after housing costs",
        "rounding": "Published whole percentages; counts converted from published 0.1 million",
    },
    "generational-wealth": {
        "description": "Median household wealth by generation at equivalent ages",
        "source": "Resolution Foundation / ONS Wealth and Assets Survey",
        "source_url": "https://www.resolutionfoundation.org/publications/",
        "access_date": "2026-05-16",
    },
}


def _child_poverty_source_matches(sidecar: dict[str, Any]) -> bool:
    """Require the pinned HBAI source, tables, AHC measure and averaging period."""
    expected = DATASET_META["child-poverty"]
    try:
        # The access date is the fetch's own record; the download URL pins the table pack.
        date.fromisoformat(sidecar["access_date"])
    except (KeyError, TypeError, ValueError):
        return False
    return all(
        sidecar.get(key) == expected[key]
        for key in ("source", "source_url", "download_url", "tables", "period", "measure")
    )


def _metadata_citation(dataset_name: str, data_type: str | None) -> dict[str, Any]:
    """Never certify retained legacy child-poverty files with the HBAI citation."""
    if dataset_name == "child-poverty" and data_type not in ("live_ons", "static_published"):
        return {
            "description": "Child poverty figures with unverified source, measure and period",
            "source": "Unverified child-poverty data",
            "source_url": "",
            "access_date": "",
        }
    return DATASET_META.get(dataset_name, {}).copy()


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
    records = df.to_dict(orient="records")

    def _is_missing(v: object) -> bool:
        # Convert any pandas/numpy missing sentinel -> None. Doing it on the
        # DataFrame (df.where(pd.notna(df), other=None)) is INEFFECTIVE for float
        # columns: pandas re-coerces the None back to NaN, which then serialises
        # to the invalid-JSON literal `NaN` (json.dumps allows NaN by default),
        # so the browser's fetch().json() cannot parse it. Sanitising the
        # plain-Python records avoids that trap. pd.isna covers every NA flavour
        # (float NaN, None, pd.NA from nullable dtypes, pd.NaT) — broader than an
        # isinstance(float)+isnan check. Values come from to_dict(orient="records")
        # so they are always scalars (never array-like), which makes pd.isna safe;
        # the try/except is belt-and-braces for a future non-scalar. Note inf is
        # NOT missing (pd.isna(inf) is False), so a stray Infinity still trips the
        # allow_nan=False writes below and fails the build loudly rather than
        # shipping unparseable JSON.
        try:
            return bool(pd.isna(v))
        except (TypeError, ValueError):
            return False

    records = [
        {k: (None if _is_missing(v) else v) for k, v in row.items()} for row in records
    ]

    if slug in _POSTPROCESSORS:
        records = _POSTPROCESSORS[slug](records)

    return records


def _read_data_type(csv_path: Path, records: list[dict]) -> str | None:
    """Validate sidecar provenance against any marker carried in the CSV rows.

    Match the API: missing provenance for productivity-pay, boe-rates or child-poverty, invalid sidecars or
    contradictory CSV markers are unverified. Real static_published data remains
    genuine only when its source matches the catalogue; other legacy datasets without a sidecar retain None.
    """
    meta_path = csv_path.with_suffix(".meta.json")
    try:
        sidecar = json.loads(meta_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return "unverified" if csv_path.name in (
            DATASETS.get("productivity-pay"), DATASETS.get("boe-rates"), DATASETS.get("child-poverty"),
        ) else None
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return "unverified"
    value = sidecar.get("data_type") if isinstance(sidecar, dict) else None
    if not isinstance(value, str) or value not in ("live_ons", "illustrative_fallback", "static_published"):
        return "unverified"
    if csv_path.name == DATASETS.get("child-poverty") and not _child_poverty_source_matches(sidecar):
        return "unverified"
    if any("data_type" in row and row["data_type"] != value for row in records):
        return "unverified"
    return value


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


def generate_simulator_static(out_dir: Path | None = None) -> int:
    """Mirror the registered simulator scenarios into the static build.

    Writes ``{id}.json`` (the same dashboard contract the API serves) plus a
    ``scenarios.json`` index matching ``GET /api/simulator/`` so the frontend's
    static path is byte-for-byte equivalent to the API path. Returns the count
    of scenarios published.
    """
    if out_dir is None:
        out_dir = SIM_OUT_DIR
    scenarios = _load_simulator_scenarios()
    out_dir.mkdir(parents=True, exist_ok=True)
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
        (out_dir / f"{scenario_id}.json").write_text(
            json.dumps(payload, allow_nan=False), encoding="utf-8"
        )
        index.append({"id": scenario_id, "name": meta["name"], "description": meta["description"]})
        print(f"  OK simulator {scenario_id}")
    (out_dir / "scenarios.json").write_text(
        json.dumps({"scenarios": index}, allow_nan=False), encoding="utf-8"
    )
    print(f"Generated {len(index)}/{len(scenarios)} simulator scenarios in {out_dir}")
    return len(index)


# No CSV mirror until the output-licence decision lands (ACTION-REQUIRED #10):
# the upstream Resolution Foundation series is CC BY-NC-ND 4.0, and a download
# affordance invites exactly the redistribution ND forbids. The frontend hides
# the CSV link for these slugs (src/constants/downloads.ts mirrors this set).
CSV_MIRROR_EXCLUDED = frozenset({"generational-wealth"})


def _write_csv_mirror(out_dir: Path, slug: str, records: list[dict], data_type: str | None) -> None:
    """Write ``{slug}.csv`` next to the JSON — the downloadable data mirror.

    RFC-001a: chart pages and home cards link these directly, so the reuse
    layer needs no backend. Data-honesty rule (RFC-001 risk section): when the
    dataset's provenance ``data_type`` is known it travels IN the artifact as
    a trailing ``data_type`` column — an ``illustrative_fallback`` composite
    must never circulate as a bare, uncaveated CSV. ``None`` cells serialise
    as empty strings.
    """
    import csv

    if slug in CSV_MIRROR_EXCLUDED or not records:
        return
    columns = list(records[0].keys())
    fieldnames = columns + (["data_type"] if data_type and "data_type" not in columns else [])
    csv_out = out_dir / f"{slug}.csv"
    with csv_out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in records:
            out_row = {k: ("" if v is None else v) for k, v in row.items()}
            if data_type:
                out_row["data_type"] = data_type
            writer.writerow(out_row)


def main() -> None:
    """Stage the entire export before replacing any last-good public files."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Sibling staging keeps replacements on the same filesystem. Only generated
    # files are promoted; curated files and missing-CSV fallbacks stay untouched.
    with TemporaryDirectory(prefix=".static-api-", dir=OUT_DIR.parent) as tmp:
        staged = Path(tmp)
        _generate_static_api(staged)
        for source in staged.rglob("*"):
            if source.is_file():
                destination = OUT_DIR / source.relative_to(staged)
                destination.parent.mkdir(parents=True, exist_ok=True)
                source.replace(destination)


def _generate_static_api(out_dir: Path) -> None:
    """Generate into staging, reading committed fallbacks from OUT_DIR."""

    available: list[str] = []
    errors: list[str] = []
    regenerated = 0
    # Normalised metadata for static (committed-JSON) datasets, keyed by slug.
    STATIC_META: dict[str, dict[str, Any]] = {}

    for slug, filename in DATASETS.items():
        csv_path = DATA_DIR / filename
        if not csv_path.exists():
            # A fail-closed pipeline leaves no CSV on a fresh checkout. Keep serving the
            # committed last-good files untouched (decision D-D) rather than dropping
            # the dataset from the listing and the provenance catalogue.
            if (OUT_DIR / f"{slug}.json").exists() and (OUT_DIR / f"{slug}-metadata.json").exists():
                available.append(slug)
                errors.append(f"  KEEP {slug}: {csv_path} not found; serving committed last-good data")
            else:
                errors.append(f"  SKIP {slug}: {csv_path} not found")
            continue

        records = _read_csv_as_records(csv_path, slug=slug)
        # Reject empty pipeline output before it can erase a last-good chart.
        if not records:
            raise ValueError(f"Dataset '{slug}' has no rows; refusing to replace public data")
        available.append(slug)
        regenerated += 1

        # Paginated data response (all rows in one page)
        data_response = {
            "data": records,
            "page": 1,
            "limit": len(records),
            "total": len(records),
            "total_pages": 1,
        }
        data_path = out_dir / f"{slug}.json"
        # allow_nan=False: NaN/Infinity are not valid JSON; fail the build loudly
        # rather than ship an unparseable file (records are sanitised above, so
        # this only fires on a genuinely new non-finite leak).
        data_path.write_text(
            json.dumps(data_response, allow_nan=False), encoding="utf-8"
        )

        # CSV mirror for the download links (RFC-001a)
        data_type = _read_data_type(csv_path, records)
        _write_csv_mirror(out_dir, slug, records, data_type)

        # Metadata response
        meta = _metadata_citation(slug, data_type)
        if slug == "child-poverty" and data_type in ("live_ons", "static_published"):
            # Verified sidecar: publish the fetch's own access date.
            sidecar = json.loads(csv_path.with_suffix(".meta.json").read_text(encoding="utf-8"))
            meta["access_date"] = sidecar["access_date"]
        if slug == "boe-rates" and data_type == "live_ons":
            # The pipeline sidecar records the actual two-source fetch and date.
            sidecar = json.loads(csv_path.with_suffix(".meta.json").read_text(encoding="utf-8"))
            sources = sidecar["sources"]
            meta = {
                **meta,
                "description": sidecar["description"],
                "source": " / ".join(source["name"] for source in sources),
                "source_url": sidecar["source_url"],
                "access_date": sidecar["access_date"],
            }
        columns = list(records[0].keys()) if records else []
        meta_response = {
            "name": slug,
            "description": meta.get("description", ""),
            "source": meta.get("source", ""),
            "source_url": meta.get("source_url", ""),
            "access_date": meta.get("access_date", ""),
            "row_count": len(records),
            "columns": columns,
            "data_type": data_type,
        }
        if slug == "child-poverty" and data_type in ("live_ons", "static_published"):
            for key in ("download_url", "tables", "period", "measure", "rounding"):
                meta_response[key] = meta[key]
        if slug == "boe-rates" and data_type == "live_ons":
            meta_response["sources"] = sources
        meta_path = out_dir / f"{slug}-metadata.json"
        meta_path.write_text(
            json.dumps(meta_response, allow_nan=False), encoding="utf-8"
        )

        print(f"  OK {slug}: {len(records)} rows")

    # Datasets served from committed static JSON (no pipeline CSV): normalise their
    # committed metadata sidecars to the API DatasetMetadata shape so the public
    # provenance page (all-metadata) cites every routed chart — not just the CSV-pipeline
    # ones. They are deliberately NOT added to datasets.json (the fetchable-data listing):
    # their data JSON is hand-curated and not in the API {data,total,...} shape, so the
    # data-contract validation only covers the CSV-pipeline datasets.
    STATIC_DATASETS = ("inheritance-tax", "wage-stagnation")
    for slug in STATIC_DATASETS:
        if slug in available:
            continue
        sidecar = OUT_DIR / f"{slug}-metadata.json"
        if not sidecar.exists():
            # Fail loud rather than silently dropping a routed chart from provenance.
            errors.append(f"  SKIP static {slug}: {sidecar} not found")
            continue
        m = json.loads(sidecar.read_text(encoding="utf-8"))
        # row_count/columns: use the sidecar's if present (e.g. inheritance-tax), else
        # derive them from the committed data JSON's row array so the catalog is
        # accurate rather than publishing 0 / [] for a real chart (e.g. wage-stagnation).
        row_count = m.get("row_count")
        columns = m.get("columns")
        data_file = OUT_DIR / f"{slug}.json"
        if data_file.exists():
            dj = json.loads(data_file.read_text(encoding="utf-8"))
            # Hand-curated JSONs are either {data: rows} shaped, bare rows, or a
            # keyed document whose primary table is `by_year` (inheritance-tax).
            rows = dj.get("data", dj.get("by_year")) if isinstance(dj, dict) else dj
            if isinstance(rows, list) and rows and isinstance(rows[0], dict):
                if row_count is None:
                    row_count = len(rows)
                if columns is None:
                    columns = list(rows[0].keys())
                # CSV mirror so the download links cover ALL routed charts,
                # not just the CSV-pipeline datasets (RFC-001a).
                _write_csv_mirror(out_dir, slug, rows, m.get("data_type"))
        STATIC_META[slug] = {
            "name": m.get("name", m.get("slug", slug)),
            "description": m.get("description", ""),
            "source": m.get("source", ""),
            "source_url": m.get("source_url", ""),
            # chart-meta sidecars use "last_updated"; API metadata uses "access_date".
            "access_date": m.get("access_date", m.get("last_updated", "")),
            "row_count": row_count if row_count is not None else 0,
            "columns": columns if columns is not None else [],
            # Schema parity with the CSV-pipeline metadata (which carries data_type).
            "data_type": m.get("data_type"),
        }

    # Dataset listing (CSV-pipeline datasets only — what the data API can serve)
    listing = {"datasets": available}
    listing_path = out_dir / "datasets.json"
    listing_path.write_text(json.dumps(listing, allow_nan=False), encoding="utf-8")

    # All metadata combined: CSV-pipeline datasets + the static-JSON datasets, so the
    # provenance page lists every routed chart.
    all_meta: dict[str, list[dict[str, Any]]] = {"datasets": []}
    for slug in available:
        meta_path = out_dir / f"{slug}-metadata.json"
        if not meta_path.exists():
            meta_path = OUT_DIR / meta_path.name
        all_meta["datasets"].append(json.loads(meta_path.read_text(encoding="utf-8")))
    for static_entry in STATIC_META.values():
        all_meta["datasets"].append(static_entry)
    all_meta_path = out_dir / "all-metadata.json"
    all_meta_path.write_text(json.dumps(all_meta, allow_nan=False), encoding="utf-8")

    # NOTE: this generator deliberately does NOT write freshness.json. The committed
    # frontend/public/data/freshness.json is HAND-MAINTAINED with the schema the
    # DataFreshnessBadge actually consumes — a flat map of
    # {slug: {last_updated: "YYYY-MM-DD", source: "..."}} (curated source dates).
    # An earlier version emitted an mtime-derived {datasets, thresholds} blob here
    # (the LIVE /api/data/freshness schema), which both mismatched the badge's flat
    # date-only/source schema AND overwrote the curated file on every deploy, silently
    # breaking the static-mode freshness badges. The live age/status view is served by
    # the /api/data/freshness endpoint; the static badge uses the curated file as-is.

    # Simulator scenarios (independent of the CSV datasets above).
    generate_simulator_static(out_dir / "simulator")

    print(f"\nGenerated static API for {regenerated}/{len(DATASETS)} datasets ({len(available)} listed) in {OUT_DIR}")
    if errors:
        print("\n".join(errors))
        if not regenerated:
            sys.exit(1)


if __name__ == "__main__":
    main()
