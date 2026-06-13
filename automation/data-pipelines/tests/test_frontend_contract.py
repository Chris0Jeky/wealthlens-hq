"""Contract test (WL-007): every registered chart ships cited data + metadata.

WHY THIS EXISTS
---------------
The dashboard registers its chart pages in ONE canonical place — the frontend
``VALID_CHART_NAMES`` set (``frontend/src/constants/charts.ts``). Each chart is
backed by a static JSON payload in ``frontend/public/data/`` plus a
``{slug}-metadata.json`` sibling carrying its source citation. Before WL-003,
``inheritance-tax`` shipped its data file but NO metadata sibling, so its source
provenance lived only inside the bespoke data file and was not guarded anywhere.
This test locks the invariant: for every committed chart, the data file and the
metadata sibling both exist, parse as JSON, and the metadata cites a non-empty
source + source_url + date. It would have FAILED before WL-003 (missing
inheritance-tax-metadata.json) and PASSES after.

SCOPE — committed vs deploy-only (be precise, do not overclaim)
---------------------------------------------------------------
A fresh checkout (and CI) only contains the files git tracks. The other ~8
charts' data/metadata are build artifacts produced by
``frontend/scripts/generate_static_api.py`` from gitignored
``data/processed/*.csv``; they are ABSENT in CI and cannot be regenerated there.
So the existence + content assertions are scoped to the chart slugs whose data
file is whitelisted in the root ``.gitignore``. Both the chart list and the
whitelist are READ from their canonical source files at test time (never
duplicated here), so this test cannot drift from them: add a chart to
``VALID_CHART_NAMES`` and whitelist its data, and this test immediately demands
a cited metadata sibling for it.

BESPOKE vs PAGINATED shapes
---------------------------
Two committed data shapes exist and both are accepted:
  * paginated  — ``{ data, page, limit, total, total_pages }`` (wealth-shares)
  * bespoke    — a per-chart payload (wage-stagnation: ``{ data, ... }``;
                 inheritance-tax: ``{ meta, summary, by_year, by_estate_size }``)
The data assertion only requires the file to exist and parse as a JSON object;
the per-shape structural contract is owned by the frontend
``static-data-validation.test.ts``. The metadata-citation assertion is the
focus here.

The metadata files themselves also have two committed shapes — the canonical
``DatasetMetadataResponse`` form (wealth-shares, inheritance-tax:
``name/description/source/source_url/access_date/...``) and the older
wage-stagnation form (``slug/title/.../last_updated`` with NO ``access_date``).
The date field is therefore accepted as either ``access_date`` or
``last_updated`` so the existing wage-stagnation outlier is honoured without a
rewrite; both are ISO ``YYYY-MM-DD`` provenance dates.
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

import pytest

# Repo root: tests/ -> data-pipelines -> automation -> ROOT.
ROOT = Path(__file__).resolve().parents[3]
PUBLIC_DATA = ROOT / "projects" / "wealthlens-dashboard" / "frontend" / "public" / "data"
CHARTS_TS = ROOT / "projects" / "wealthlens-dashboard" / "frontend" / "src" / "constants" / "charts.ts"
GITIGNORE = ROOT / ".gitignore"

# A metadata file must carry a non-empty value for each of these citation fields.
REQUIRED_CITATION_FIELDS = ("source", "source_url")
# Plus one date field, accepted under either committed key (see module docstring).
DATE_FIELD_KEYS = ("access_date", "last_updated")
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _read_valid_chart_names() -> list[str]:
    """Parse ``VALID_CHART_NAMES`` slugs from the canonical charts.ts.

    Sourced from the frontend constant rather than re-listing slugs here, so the
    test cannot drift from the single registry of chart pages. Extracts the
    quoted string literals inside the ``new Set([ ... ])`` block.
    """
    text = CHARTS_TS.read_text(encoding="utf-8")
    match = re.search(r"VALID_CHART_NAMES\s*=\s*new Set\(\[(.*?)\]\)", text, re.DOTALL)
    if match is None:  # pragma: no cover - guards a charts.ts refactor
        raise AssertionError(f"Could not locate VALID_CHART_NAMES Set literal in {CHARTS_TS}")
    slugs = re.findall(r'"([a-z0-9-]+)"', match.group(1))
    assert slugs, f"VALID_CHART_NAMES parsed empty from {CHARTS_TS}"
    return slugs


def _read_whitelisted_data_slugs() -> set[str]:
    """Return chart slugs whose ``{slug}.json`` data file is whitelisted to ship.

    Parsed from the root .gitignore negation lines so the committed/deploy-only
    split is read from its single source of truth. A line like
    ``!.../public/data/wealth-shares.json`` whitelists the ``wealth-shares`` data
    file; ``-metadata.json`` and non-public-data negations are ignored here.
    """
    prefix = "!projects/wealthlens-dashboard/frontend/public/data/"
    slugs: set[str] = set()
    for raw in GITIGNORE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith(prefix):
            continue
        filename = line[len(prefix) :]
        if filename.endswith("-metadata.json"):
            continue
        if filename.endswith(".json") and filename != "freshness.json":
            slugs.add(filename[: -len(".json")])
    return slugs


# Charts whose data file ships in the repo (intersection of the registry and the
# .gitignore whitelist). Deploy-only charts are out of scope — see module docstring.
VALID_CHART_NAMES = _read_valid_chart_names()
WHITELISTED_DATA_SLUGS = _read_whitelisted_data_slugs()
COMMITTED_CHARTS = sorted(set(VALID_CHART_NAMES) & WHITELISTED_DATA_SLUGS)


def test_public_data_dir_exists() -> None:
    """The committed static-data dir must exist (it ships verbatim)."""
    assert PUBLIC_DATA.is_dir(), f"expected committed static data at {PUBLIC_DATA}"


def test_committed_charts_resolved() -> None:
    """Guard against an empty scope silently passing every parametrised test.

    If charts.ts or the .gitignore whitelist were mis-parsed, COMMITTED_CHARTS
    would be empty and the per-chart tests below would vanish into 0 cases — a
    silent no-op. Assert we actually resolved at least the known committed charts.
    """
    assert COMMITTED_CHARTS, (
        "No committed charts resolved — charts.ts or .gitignore parsing drifted. "
        f"VALID_CHART_NAMES={VALID_CHART_NAMES}, whitelist={sorted(WHITELISTED_DATA_SLUGS)}"
    )
    # inheritance-tax must be in scope after WL-003; this is the regression we lock.
    assert "inheritance-tax" in COMMITTED_CHARTS


@pytest.mark.parametrize("slug", COMMITTED_CHARTS)
def test_committed_chart_has_data_file(slug: str) -> None:
    """Every committed chart ships a ``{slug}.json`` data file that parses."""
    data_path = PUBLIC_DATA / f"{slug}.json"
    assert data_path.is_file(), f"missing committed data file: {data_path.name}"
    parsed = json.loads(data_path.read_text(encoding="utf-8"))
    # Accept both paginated and bespoke shapes — only require a JSON object.
    assert isinstance(parsed, dict), f"{data_path.name} must be a JSON object"


@pytest.mark.parametrize("slug", COMMITTED_CHARTS)
def test_committed_chart_has_cited_metadata(slug: str) -> None:
    """Every committed chart ships a metadata sibling citing source + url + date.

    This is the WL-007 invariant. Before WL-003, inheritance-tax had no metadata
    sibling, so this assertion would have failed for it; it now passes.
    """
    meta_path = PUBLIC_DATA / f"{slug}-metadata.json"
    assert meta_path.is_file(), (
        f"missing metadata sibling: {meta_path.name} (every committed chart must ship cited metadata — WL-007)"
    )
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert isinstance(meta, dict), f"{meta_path.name} must be a JSON object"

    for field in REQUIRED_CITATION_FIELDS:
        value = meta.get(field)
        assert isinstance(value, str) and value.strip(), f"{meta_path.name}: '{field}' must be a non-empty string"

    # source_url must be an http(s) URL, not a placeholder like "tbd"/"see notes" —
    # matches the frontend static-data-validation.test.ts `new URL(...)` check on
    # the same files (a citation URL is the load-bearing part of provenance).
    source_url = meta["source_url"]
    assert re.match(r"^https?://", source_url), (
        f"{meta_path.name}: 'source_url' must be an http(s) URL, got {source_url!r}"
    )

    # A provenance date under either committed key (access_date | last_updated).
    date_value = next(
        (meta[k] for k in DATE_FIELD_KEYS if isinstance(meta.get(k), str) and meta[k].strip()),
        None,
    )
    assert date_value is not None, (
        f"{meta_path.name}: a non-empty date field ({' or '.join(DATE_FIELD_KEYS)}) is required"
    )
    assert _ISO_DATE.match(date_value), f"{meta_path.name}: date '{date_value}' must be ISO YYYY-MM-DD"
    # Reject regex-valid but impossible dates (e.g. 2026-99-99) — mirrors the
    # frontend isRealCalendarDate() round-trip guard.
    try:
        datetime.date.fromisoformat(date_value)
    except ValueError as err:
        raise AssertionError(f"{meta_path.name}: date '{date_value}' is not a real calendar date") from err
