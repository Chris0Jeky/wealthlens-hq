"""Tests for outputs.to_dashboard_json (Wave 12 PR3e).

Includes a golden-file test pinning the dashboard JSON contract and structural
tests for serialisability, intervals, devolution scope, and provenance.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from wealthlens_sim.assumptions import load_assumptions
from wealthlens_sim.engine import DevolutionConfig, Registries, simulate
from wealthlens_sim.outputs import DASHBOARD_SCHEMA_VERSION, to_dashboard_json
from wealthlens_sim.reforms.a_annual_wealth import WealthTaxConfig
from wealthlens_sim.reforms.f_enforcement import ComplianceRate, EnforcementConfig, TaxFamily
from wealthlens_sim.reforms.g_devolution import NationScope
from wealthlens_sim.rules import FamilySelection, PolicyFamily, Scenario
from wealthlens_sim.schema.base import VersionTag
from wealthlens_sim.synth import SynthConfig, generate_population
from wealthlens_sim.uncertainty import SamplingConfig

_GOLDEN_DIR = Path(__file__).parent / "golden"
_GOLDEN = _GOLDEN_DIR / "dashboard_wealth_tax.json"
_GOLDEN_DEVO_ENF = _GOLDEN_DIR / "dashboard_devolution_enforcement.json"


def _version() -> VersionTag:
    return VersionTag(
        macro_baseline_version="NBS-2025",
        policy_version="2026-05-21",
        population_version="synth-v0.1",
        wealthlens_sim_version="0.1.0",
    )


def _golden_scenario() -> Scenario:
    return Scenario(
        name="annual-wealth-1pct",
        version_tag=_version(),
        families=[
            FamilySelection(
                family=PolicyFamily.ANNUAL_WEALTH_TAX,
                config=WealthTaxConfig(threshold=1_000_000, rate=0.01),
            )
        ],
    )


def _golden_result():
    # Must match exactly how tests/golden/dashboard_wealth_tax.json was generated.
    pop = generate_population(SynthConfig(n_households=500, seed=7))
    return simulate(pop, _golden_scenario(), registries=Registries(assumptions=load_assumptions()))


def _devolution_enforcement_result():
    # England-only scope + an OTHER enforcement uplift: exercises the devolution
    # scope serialisation and enforcement-uplift fields end-to-end.
    pop = generate_population(SynthConfig(n_households=500, seed=7))
    enforcement = EnforcementConfig(
        compliance_rates=(ComplianceRate(tax_family=TaxFamily.OTHER, baseline_rate=0.8, scenario_rate=0.9),),
    )
    return simulate(
        pop,
        _golden_scenario(),
        registries=Registries(assumptions=load_assumptions()),
        devolution=DevolutionConfig(scope=NationScope.ENGLAND_ONLY),
        enforcement=enforcement,
    )


def _check_golden(path: Path, produced: dict[str, Any]) -> None:
    """Compare ``produced`` to the golden at ``path``, or regenerate it.

    Set ``REGEN_GOLDEN=1`` to rewrite the golden after an intentional engine
    change (keeps generation identical to the test's own builders).
    """
    if os.environ.get("REGEN_GOLDEN"):
        path.write_text(json.dumps(produced, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    golden = json.loads(path.read_text(encoding="utf-8"))
    _assert_json_approx(produced, golden)


def _assert_json_approx(actual: Any, expected: Any, path: str = "") -> None:
    """Recursively compare two JSON structures, floats with tolerance.

    Robust to last-bit float differences across platforms (numpy-driven synth +
    Pareto math) while still pinning structure, keys, strings, ints, and bools.
    """
    assert type(actual) is type(expected), f"type mismatch at {path}: {type(actual)} != {type(expected)}"
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), f"key mismatch at {path}: {actual.keys()} != {expected.keys()}"
        for key in expected:
            _assert_json_approx(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        assert len(actual) == len(expected), f"length mismatch at {path}: {len(actual)} != {len(expected)}"
        for i, (a, e) in enumerate(zip(actual, expected, strict=True)):
            _assert_json_approx(a, e, f"{path}[{i}]")
    elif isinstance(expected, float):
        assert actual == pytest.approx(expected, rel=1e-9, abs=1e-12), (
            f"float mismatch at {path}: {actual} != {expected}"
        )
    else:
        assert actual == expected, f"value mismatch at {path}: {actual!r} != {expected!r}"


class TestGoldenFile:
    def test_matches_golden(self):
        _check_golden(_GOLDEN, to_dashboard_json(_golden_result()))

    def test_matches_golden_devolution_enforcement(self):
        _check_golden(_GOLDEN_DEVO_ENF, to_dashboard_json(_devolution_enforcement_result()))

    def test_output_is_json_serialisable(self):
        # The whole point of the contract: it must round-trip through json.
        produced = to_dashboard_json(_golden_result())
        reparsed = json.loads(json.dumps(produced))
        assert reparsed["scenario_name"] == "annual-wealth-1pct"

    def test_different_scenario_produces_different_json(self):
        # Guard against a constant/stub to_dashboard_json: a higher rate must
        # change the headline central total.
        pop = generate_population(SynthConfig(n_households=500, seed=7))
        registries = Registries(assumptions=load_assumptions())
        one_pct = _golden_scenario()
        two_pct = Scenario(
            name="annual-wealth-2pct",
            version_tag=_version(),
            families=[
                FamilySelection(
                    family=PolicyFamily.ANNUAL_WEALTH_TAX,
                    config=WealthTaxConfig(threshold=1_000_000, rate=0.02),
                )
            ],
        )
        a = to_dashboard_json(simulate(pop, one_pct, registries=registries))
        b = to_dashboard_json(simulate(pop, two_pct, registries=registries))
        assert b["total_revenue_gbp_bn"]["central"] != a["total_revenue_gbp_bn"]["central"]


class TestStructure:
    def test_schema_version_present(self):
        result = to_dashboard_json(_golden_result())
        assert result["schema_version"] == DASHBOARD_SCHEMA_VERSION

    def test_interval_method_alpha_sweep_by_default(self):
        result = to_dashboard_json(_golden_result())
        assert result["interval_method"] == "alpha_sweep"
        assert result["uncertainty_provenance_ids"] == []

    def test_interval_method_monte_carlo_when_sampled(self):
        # An MC run must label its band as monte_carlo and carry the sampling trail,
        # so a consumer is never told an MC credible interval is the alpha sweep.
        pop = generate_population(SynthConfig(n_households=500, seed=7))
        registries = Registries(assumptions=load_assumptions())
        result = to_dashboard_json(
            simulate(pop, _golden_scenario(), registries=registries,
                     uncertainty=SamplingConfig(n_samples=256, seed=0))
        )
        assert result["interval_method"] == "monte_carlo"
        assert any(s.startswith("uncertainty.n_samples:") for s in result["uncertainty_provenance_ids"])

    def test_intervals_have_low_central_high(self):
        result = to_dashboard_json(_golden_result())
        total = result["total_revenue_gbp_bn"]
        assert set(total) == {"low", "central", "high"}
        assert total["low"] <= total["central"] <= total["high"]
        assert set(result["enforcement_cost_gbp_bn"]) == {"low", "central", "high"}
        assert set(result["enforcement_net_fiscal_impact_gbp_bn"]) == {"low", "central", "high"}
        assert len(result["revenue_by_decile"]) == 10

    def test_provenance_block_lists_consumed_assumptions(self):
        result = to_dashboard_json(_golden_result())
        prov = result["provenance"]
        assert prov["complete"] is True
        ids = {a["assumption_id"] for a in prov["assumptions_consumed"]}
        assert "toptail.pareto_alpha.overall.v1" in ids
        # Every consumed assumption carries a human-readable source.
        assert all(a["source"] for a in prov["assumptions_consumed"])

    def test_devolution_scope_included_when_scoped(self):
        pop = generate_population(SynthConfig(n_households=500, seed=7))
        result = simulate(
            pop,
            _golden_scenario(),
            registries=Registries(assumptions=load_assumptions()),
            devolution=DevolutionConfig(scope=NationScope.ENGLAND_ONLY),
        )
        dash = to_dashboard_json(result)
        assert dash["devolution_scope"] is not None
        assert dash["devolution_scope"]["included_nations"] == ["england"]

    def test_devolution_scope_null_when_uk_wide(self):
        dash = to_dashboard_json(_golden_result())
        assert dash["devolution_scope"] is None

    def test_no_volatile_timestamp_in_output(self):
        # run_timestamp is excluded so the contract is deterministic (golden-able).
        dash = to_dashboard_json(_golden_result())
        assert "run_timestamp" not in json.dumps(dash)


class TestDataIntegritySurfacing:
    def test_complete_sourced_synth_run_carries_population_caveat(self):
        # A fully-sourced run over the SYNTHETIC population carries exactly the
        # synthetic-population caveat (emitted by the contract itself now) and NOT
        # the incomplete-provenance caveat.
        dash = to_dashboard_json(_golden_result())
        assert dash["provenance_complete"] is True
        assert any("synthetic v0.1 population" in c for c in dash["caveats"])
        assert not any("Provenance incomplete" in c for c in dash["caveats"])

    def test_real_population_omits_synthetic_caveat(self):
        # GROUND TRUTH: a population whose is_synthetic flag is False must NOT carry
        # the synthetic-population caveat. (No real-microdata provider exists yet, so
        # flip the flag on a generated population via model_copy to exercise the
        # is_synthetic gate directly — independent of the version_tag string.)
        pop = generate_population(SynthConfig(n_households=500, seed=7)).model_copy(
            update={"is_synthetic": False}
        )
        dash = to_dashboard_json(
            simulate(pop, _golden_scenario(), registries=Registries(assumptions=load_assumptions()))
        )
        assert not any("synthetic v0.1 population" in c for c in dash["caveats"])
        assert dash["caveats"] == []

    def test_unsourced_run_flags_incomplete_provenance(self):
        # No registry => degenerate intervals + incomplete provenance. The contract
        # must make this LOUD: a root flag + a caveat, not just a nested bool.
        pop = generate_population(SynthConfig(n_households=500, seed=7))
        dash = to_dashboard_json(simulate(pop, _golden_scenario()))
        assert dash["provenance_complete"] is False
        assert any("Provenance incomplete" in c for c in dash["caveats"])
        # Degenerate intervals are still emitted, but the caveat is the guardrail.
        total = dash["total_revenue_gbp_bn"]
        assert total["low"] == total["central"] == total["high"]

    def test_unsourced_synth_run_orders_synthetic_then_incomplete(self):
        # An unsourced SYNTH run carries BOTH caveats; pin the order
        # (synthetic-population first, incomplete-provenance second) so a future
        # reorder can't silently change what the chart's banner leads with.
        pop = generate_population(SynthConfig(n_households=500, seed=7))
        dash = to_dashboard_json(simulate(pop, _golden_scenario()))
        assert len(dash["caveats"]) == 2
        assert "synthetic v0.1 population" in dash["caveats"][0]
        assert "Provenance incomplete" in dash["caveats"][1]

    def test_enforcement_headline_has_no_overstatement_caveat(self):
        dash = to_dashboard_json(_devolution_enforcement_result())
        assert dash["enforcement_uplift_gbp_bn"]["central"] > 0.0
        assert dash["enforcement_cost_gbp_bn"]["central"] == 0.0
        assert dash["enforcement_net_fiscal_impact_gbp_bn"]["central"] == dash["enforcement_uplift_gbp_bn"]["central"]
        assert not any("overstates collectible revenue" in c for c in dash["caveats"])

    def test_negative_net_fiscal_impact_has_no_overstatement_caveat(self):
        pop = generate_population(SynthConfig(n_households=500, seed=7))
        enforcement = EnforcementConfig(
            compliance_rates=(ComplianceRate(tax_family=TaxFamily.OTHER, baseline_rate=0.8, scenario_rate=0.9),),
            enforcement_cost_bn=10.0,
        )
        dash = to_dashboard_json(
            simulate(
                pop,
                _golden_scenario(),
                registries=Registries(assumptions=load_assumptions()),
                enforcement=enforcement,
            )
        )
        assert dash["enforcement_uplift_gbp_bn"]["central"] > 0.0
        assert dash["enforcement_cost_gbp_bn"]["central"] == 10.0
        assert dash["enforcement_net_fiscal_impact_gbp_bn"]["central"] < 0.0
        assert dash["total_revenue_gbp_bn"]["central"] > 0.0
        assert not any("overstates collectible revenue" in c for c in dash["caveats"])

    def test_root_flag_mirrors_nested_provenance_complete(self):
        dash = to_dashboard_json(_golden_result())
        assert dash["provenance_complete"] == dash["provenance"]["complete"]


class TestPopulationProvenance:
    """population_provenance resolves registered data sources to URL + access date."""

    def test_registered_source_resolved_with_url_and_access_date(self):
        dash = to_dashboard_json(_golden_result())
        by_id = {e["id"]: e for e in dash["population_provenance"]}
        was = by_id["ons-was-wealth"]
        assert was["url"].startswith("https://")
        assert was["access_date"]  # non-empty (the data-integrity rule)
        assert was["name"]
        assert was["licence"]

    def test_synth_params_are_id_only(self):
        dash = to_dashboard_json(_golden_result())
        synth = [e for e in dash["population_provenance"] if e["id"].startswith("synth.")]
        assert synth, "expected synth.* generation-parameter ids"
        # Generation parameters are config inputs, not external sources: id only.
        assert all(set(e) == {"id"} for e in synth)

    def test_order_matches_ids_and_covers_all(self):
        # Order-preserving and 1:1 with the flat id list kept for back-compat.
        dash = to_dashboard_json(_golden_result())
        assert [e["id"] for e in dash["population_provenance"]] == dash["population_provenance_ids"]

    def test_missing_registry_degrades_to_id_only(self, monkeypatch: pytest.MonkeyPatch):
        # If the source index can't load, resolution degrades to id-only (no crash,
        # no regression vs. the bare id list) rather than breaking the contract.
        # Replacing the whole function sidesteps the lru_cache; monkeypatch restores it.
        from wealthlens_sim import outputs

        monkeypatch.setattr(outputs, "_source_index", lambda: {})
        dash = to_dashboard_json(_golden_result())
        assert all(set(e) == {"id"} for e in dash["population_provenance"])
        assert [e["id"] for e in dash["population_provenance"]] == dash["population_provenance_ids"]
