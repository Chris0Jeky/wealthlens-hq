"""Output formatting: dashboard-ready JSON for the Vue frontend (Wave 12 PR3e).

:func:`to_dashboard_json` converts an :class:`~wealthlens_sim.engine.result.EngineResult`
into a plain, JSON-serialisable ``dict`` — the contract the dashboard consumes:
headline total + per-nation + per-decile revenue (each as a low/central/high
interval), the gross enforcement revenue uplift, enforcement cost, net fiscal
impact, the devolution scope (if any), and a
flattened provenance block (the assumptions consumed with their sources, plus the
per-output assumption trail). Every published number therefore reaches the
dashboard alongside its uncertainty band and its provenance (Blueprint v5 §13.6,
§15 Gate-9 dashboard safety).

Data-integrity states a chart must not publish silently are surfaced **loudly at
the contract root**: ``provenance_complete`` (``False`` ⇒ unsourced, degenerate
intervals) and a ``caveats`` list the frontend must render. The nested
``provenance.complete`` mirrors the root flag for the detailed block.

The volatile ``run_timestamp`` is intentionally excluded so the output is
deterministic for a given result (enabling the golden-file test); the stable
``version_tag`` identifies the run instead. To regenerate the golden files after an
intentional engine change, run the outputs tests with ``REGEN_GOLDEN=1`` set.

Reference: docs/WAVE12_SIMULATION_ENGINE_DESIGN.md §6.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import yaml

from wealthlens_sim._registry_path import find_registries_dir
from wealthlens_sim.engine.result import EngineResult
from wealthlens_sim.top_tail.types import Interval

__all__ = ["DASHBOARD_SCHEMA_VERSION", "to_dashboard_json"]

#: Bumped only for BREAKING shape changes (a removed/renamed/retyped key) — the
#: frontend guards on EXACT equality, so bumping rejects older clients. Purely
#: ADDITIVE keys (a new optional field older consumers ignore) do NOT bump; e.g.
#: ``population_provenance`` was added additively at 1.3.
#: 1.3 adds ``interval_method`` + ``uncertainty_provenance_ids`` so a Monte-Carlo
#: band is never published while labelled as the single alpha sweep.
DASHBOARD_SCHEMA_VERSION = "1.3"

_INCOMPLETE_PROVENANCE_CAVEAT = (
    "Provenance incomplete: no assumption registry was supplied, so the intervals "
    "are point estimates and the uncertainty is unquantified — do not present these "
    "figures as fully sourced."
)

#: Emitted at the contract root for any run over a SYNTHETIC population (the v0.1
#: default), so every consumer of the contract — not only callers of the downstream
#: fixture generator — is told the figures are over generated microdata, not a real
#: costing. Conditioned on ``version_tag.population_version`` so a future
#: real-microdata population does not carry it.
_SYNTHETIC_POPULATION_CAVEAT = (
    "Illustrative estimate over a synthetic v0.1 population (household microdata "
    "statistically generated and calibrated to published aggregates), not an "
    "official forecast. Treat the figures as indicative, not as a costing."
)


def _interval(interval: Interval) -> dict[str, float]:
    return {"low": interval.low, "central": interval.central, "high": interval.high}


def _caveats(result: EngineResult) -> list[str]:
    """Machine-readable data-integrity caveats the frontend MUST render.

    Surfaces, loudly and at the contract root, states a chart must not publish
    silently. Enforcement no longer adds revenue above the full-compliance
    ceiling, so it does not need a separate overstatement caveat.
    """
    caveats: list[str] = []
    # Keyed off the population's GROUND-TRUTH is_synthetic flag (threaded through
    # EngineResult from the population source), not a version-tag string — so a
    # synthetic population can never fail open (omit the caveat) by being mistagged,
    # and the default is fail-closed (treat as synthetic and warn) when a source
    # omits the flag.
    if result.population_is_synthetic:
        caveats.append(_SYNTHETIC_POPULATION_CAVEAT)
    if not result.provenance_complete:
        caveats.append(_INCOMPLETE_PROVENANCE_CAVEAT)
    return caveats


@lru_cache(maxsize=1)
def _source_index() -> dict[str, dict[str, str]]:
    """Map a registered source id -> {name, url, access_date, licence} from
    ``registries/sources.yml``.

    Used to resolve ``population_provenance_ids`` into cited sources carrying a URL
    and access date (the repo data-integrity rule). Loaded once and cached. On any
    failure the index is empty, so resolution degrades to id-only entries (no
    regression vs. the bare id list) rather than breaking the contract.
    """
    try:
        raw = yaml.safe_load((find_registries_dir() / "sources.yml").read_text(encoding="utf-8"))
        entries = raw.get("sources", []) if isinstance(raw, dict) else []
    except (FileNotFoundError, OSError, yaml.YAMLError):
        return {}
    index: dict[str, dict[str, str]] = {}
    for entry in entries:
        sid = entry.get("id")
        if not sid:
            continue
        index[sid] = {
            "name": entry.get("name", ""),
            "url": entry.get("url", ""),
            "access_date": str(entry.get("access_date", "")),
            "licence": entry.get("licence", ""),
        }
    return index


def _population_provenance(ids: list[str]) -> list[dict[str, str]]:
    """Resolve population provenance ids to structured source records.

    Order-preserving (deterministic, golden-file friendly). A registered data
    source (in ``sources.yml``) becomes ``{id, name, url, access_date, licence}``;
    an unregistered id — the ``synth.*`` generation parameters, which are config
    inputs, not external sources — stays ``{id}`` only (no URL to cite).
    """
    index = _source_index()
    out: list[dict[str, str]] = []
    for sid in ids:
        meta = index.get(sid)
        out.append({"id": sid, **meta} if meta else {"id": sid})
    return out


def _provenance(result: EngineResult) -> dict[str, Any]:
    manifest = result.provenance
    # Sort assumptions by id for a stable, golden-file-friendly ordering.
    assumptions = [
        {
            "assumption_id": resolved.assumption_id,
            "domain": resolved.domain,
            "source": resolved.source,
            "resolved_value": resolved.resolved_value,
        }
        for _id, resolved in sorted(manifest.assumptions_consumed.items())
    ]
    outputs = [
        {
            "output_label": entry.output_label,
            "layer": entry.layer.value,
            "assumption_ids": list(entry.assumption_ids),
        }
        for entry in manifest.entries
    ]
    return {
        "complete": result.provenance_complete,
        "version_tag": manifest.version_tag.model_dump(mode="json"),
        "assumptions_consumed": assumptions,
        "outputs": outputs,
    }


def to_dashboard_json(result: EngineResult) -> dict[str, Any]:
    """Render an :class:`EngineResult` as the dashboard JSON contract.

    Returns a plain ``dict`` of JSON-native types (str/float/int/bool/list/dict),
    safe to pass to ``json.dumps``. Deterministic for a given result — the
    non-deterministic provenance ``run_timestamp`` is omitted (the stable
    ``version_tag`` identifies the run).
    """
    devolution = result.devolution_split.model_dump(mode="json") if result.devolution_split is not None else None
    return {
        "schema_version": DASHBOARD_SCHEMA_VERSION,
        "scenario_name": result.scenario.name,
        # Hoisted to the root (not just under `provenance`) so a consumer cannot
        # miss the unsourced state, and the data-integrity caveats it must render.
        "provenance_complete": result.provenance_complete,
        "caveats": _caveats(result),
        "households_scored": result.households_scored,
        # How the published low/high band was derived, so a consumer is never told a
        # Monte-Carlo credible interval is the single deterministic alpha sweep.
        # ``monte_carlo`` ⇒ see ``uncertainty_provenance_ids`` for the sampling
        # method/seed/draws/quantiles; ``alpha_sweep`` ⇒ the top-tail-alpha-range
        # multiplicative band recorded in ``provenance``.
        "interval_method": "monte_carlo" if result.uncertainty_provenance_ids else "alpha_sweep",
        "total_revenue_gbp_bn": _interval(result.total_revenue_gbp_bn),
        "enforcement_uplift_gbp_bn": _interval(result.enforcement_uplift_bn),
        "enforcement_cost_gbp_bn": _interval(result.enforcement_cost_bn),
        "enforcement_net_fiscal_impact_gbp_bn": _interval(result.enforcement_net_fiscal_impact_bn),
        "revenue_by_nation": {nation: _interval(interval) for nation, interval in result.revenue_by_nation.items()},
        "revenue_by_decile": [_interval(interval) for interval in result.revenue_by_decile],
        "devolution_scope": devolution,
        "population_provenance_ids": list(result.population_provenance_ids),
        # Structured view of the population provenance: registered data sources
        # resolved to {id,name,url,access_date,licence} from registries/sources.yml
        # (the data-integrity URL+access-date rule); synth.* generation params stay
        # id-only. Additive — the flat id list above is kept for back-compat.
        "population_provenance": _population_provenance(list(result.population_provenance_ids)),
        # Monte-Carlo sampling/propagation trail (seed, method, draws, sampled
        # marginals, quantiles). Empty when ``interval_method == "alpha_sweep"``.
        "uncertainty_provenance_ids": list(result.uncertainty_provenance_ids),
        "provenance": _provenance(result),
    }
