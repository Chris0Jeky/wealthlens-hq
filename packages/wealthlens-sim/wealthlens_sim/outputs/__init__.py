"""Output formatting: dashboard-ready JSON for the Vue frontend (Wave 12 PR3e).

:func:`to_dashboard_json` converts an :class:`~wealthlens_sim.engine.result.EngineResult`
into a plain, JSON-serialisable ``dict`` — the contract the dashboard consumes:
headline total + per-nation + per-decile revenue (each as a low/central/high
interval), the net enforcement uplift, the devolution scope (if any), and a
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

from typing import Any

from wealthlens_sim.engine.result import EngineResult
from wealthlens_sim.top_tail.types import Interval

__all__ = ["DASHBOARD_SCHEMA_VERSION", "to_dashboard_json"]

#: Bumped when the dashboard JSON shape changes so the frontend can guard on it.
DASHBOARD_SCHEMA_VERSION = "1.1"

_INCOMPLETE_PROVENANCE_CAVEAT = (
    "Provenance incomplete: no assumption registry was supplied, so the intervals "
    "are point estimates and the uncertainty is unquantified — do not present these "
    "figures as fully sourced."
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
    if not result.provenance_complete:
        caveats.append(_INCOMPLETE_PROVENANCE_CAVEAT)
    return caveats


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
        "total_revenue_gbp_bn": _interval(result.total_revenue_gbp_bn),
        "enforcement_uplift_gbp_bn": _interval(result.enforcement_uplift_bn),
        "revenue_by_nation": {nation: _interval(interval) for nation, interval in result.revenue_by_nation.items()},
        "revenue_by_decile": [_interval(interval) for interval in result.revenue_by_decile],
        "devolution_scope": devolution,
        "population_provenance_ids": list(result.population_provenance_ids),
        "provenance": _provenance(result),
    }
