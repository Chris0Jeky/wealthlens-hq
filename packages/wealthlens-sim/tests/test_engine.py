"""Tests for the engine/ orchestrator (Wave 12 PR3a).

Covers the synth -> rules -> provenance wiring, the decile-attribution invariant
(decile sum == aggregate total), the PopulationSource protocol seam, the
provenance manifest, and edge cases (empty population, registry vs no-registry).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wealthlens_sim.assumptions import load_assumptions
from wealthlens_sim.engine import (
    N_DECILES,
    EngineResult,
    PopulationSource,
    Registries,
    revenue_by_wealth_decile,
    run_scenario,
)
from wealthlens_sim.engine.result import Interval
from wealthlens_sim.provenance.manifest import PipelineLayer, ProvenanceManifest
from wealthlens_sim.reforms.a_annual_wealth import WealthTaxConfig
from wealthlens_sim.reforms.d_iht_reform import IHTConfig
from wealthlens_sim.reforms.e_property_tax import HVCTSConfig
from wealthlens_sim.rules import FamilySelection, PolicyFamily, Scenario
from wealthlens_sim.rules import run_scenario as run_families
from wealthlens_sim.schema.base import VersionTag
from wealthlens_sim.synth import SynthConfig, SyntheticPopulation, generate_population


def _version() -> VersionTag:
    return VersionTag(
        macro_baseline_version="NBS-2025",
        policy_version="2026-05-21",
        population_version="synth-v0.1",
        wealthlens_sim_version="0.1.0",
    )


def _population(n: int = 1_500, seed: int = 11) -> SyntheticPopulation:
    return generate_population(SynthConfig(n_households=n, seed=seed))


def _wealth_tax(threshold: float = 1_000_000, rate: float = 0.01) -> FamilySelection:
    return FamilySelection(
        family=PolicyFamily.ANNUAL_WEALTH_TAX,
        config=WealthTaxConfig(threshold=threshold, rate=rate),
    )


def _scenario(*families: FamilySelection, name: str = "s") -> Scenario:
    return Scenario(name=name, version_tag=_version(), families=list(families))


class TestPopulationSourceSeam:
    def test_synthetic_population_satisfies_protocol(self):
        pop = _population(n=50)
        assert isinstance(pop, PopulationSource)

    def test_protocol_needs_households_and_provenance_ids(self):
        class Missing:
            def __init__(self) -> None:
                self.households: list[object] = []  # no provenance_ids attribute

        assert not isinstance(Missing(), PopulationSource)


class TestRunScenario:
    def test_returns_engine_result(self):
        result = run_scenario(_population(), _scenario(_wealth_tax()))
        assert isinstance(result, EngineResult)
        assert isinstance(result.total_revenue_gbp_bn, Interval)
        assert isinstance(result.provenance, ProvenanceManifest)

    def test_total_matches_rules_aggregate(self):
        pop = _population()
        scenario = _scenario(_wealth_tax())
        result = run_scenario(pop, scenario)
        aggregate = run_families(pop.households, scenario)
        assert result.total_revenue_gbp_bn.central == pytest.approx(aggregate.total_revenue_bn)

    def test_households_scored_counts_population(self):
        pop = _population(n=500)
        result = run_scenario(pop, _scenario(_wealth_tax()))
        assert result.households_scored == 500

    def test_intervals_are_degenerate_in_pr3a(self):
        # PR3a placeholder: low == central == high until PR3c propagates ranges.
        result = run_scenario(_population(), _scenario(_wealth_tax()))
        iv = result.total_revenue_gbp_bn
        assert iv.low == iv.central == iv.high

    def test_deterministic(self):
        pop = _population()
        scenario = _scenario(_wealth_tax())
        r1 = run_scenario(pop, scenario)
        r2 = run_scenario(pop, scenario)
        assert r1.total_revenue_gbp_bn == r2.total_revenue_gbp_bn
        assert r1.revenue_by_decile == r2.revenue_by_decile

    def test_revenue_by_nation_matches_aggregate(self):
        pop = _population()
        scenario = _scenario(
            _wealth_tax(),
            FamilySelection(family=PolicyFamily.HVCTS, config=HVCTSConfig()),
        )
        result = run_scenario(pop, scenario)
        aggregate = run_families(pop.households, scenario)
        for nation, interval in result.revenue_by_nation.items():
            assert interval.central == pytest.approx(aggregate.revenue_by_nation[nation])


class TestDecileAttribution:
    def test_decile_count_is_ten(self):
        result = run_scenario(_population(), _scenario(_wealth_tax()))
        assert len(result.revenue_by_decile) == N_DECILES

    def test_decile_sum_equals_total(self):
        # The core invariant: per-household decile attribution and the aggregate
        # total are computed by the same calculators, so they must agree.
        pop = _population()
        scenario = _scenario(
            _wealth_tax(),
            FamilySelection(family=PolicyFamily.IHT, config=IHTConfig()),
        )
        result = run_scenario(pop, scenario)
        decile_sum = sum(iv.central for iv in result.revenue_by_decile)
        assert decile_sum == pytest.approx(result.total_revenue_gbp_bn.central)

    def test_wealth_tax_revenue_concentrated_in_top_decile(self):
        # A £1m-threshold wealth tax falls on the wealthiest households, so the
        # top decile (index 9) must out-raise the bottom decile (index 0).
        pop = _population()
        result = run_scenario(pop, _scenario(_wealth_tax()))
        assert result.revenue_by_decile[-1].central > result.revenue_by_decile[0].central

    def test_empty_population_has_no_deciles(self):
        empty = SyntheticPopulation(households=[], seed=0)
        result = run_scenario(empty, _scenario(_wealth_tax()))
        assert result.revenue_by_decile == []
        assert result.households_scored == 0
        assert result.total_revenue_gbp_bn.central == 0.0

    def test_helper_zero_weight_returns_empty(self):
        # Defensive: a non-positive total weight yields no deciles, not a crash.
        pop = _population(n=20)
        for hh in pop.households:
            object.__setattr__(hh, "weight", 0.0)  # bypass frozen for the test
        deciles = revenue_by_wealth_decile(pop.households, [_wealth_tax()])
        assert deciles == []


class TestProvenance:
    def test_manifest_records_revenue_outputs(self):
        result = run_scenario(_population(n=100), _scenario(_wealth_tax()))
        labels = {e.output_label for e in result.provenance.entries}
        assert "total_revenue_gbp_bn" in labels
        assert all(e.layer == PipelineLayer.REVENUE for e in result.provenance.entries)

    def test_manifest_uses_scenario_version_tag(self):
        scenario = _scenario(_wealth_tax())
        result = run_scenario(_population(n=100), scenario)
        assert result.provenance.version_tag == scenario.version_tag

    def test_registry_path_builds_equivalent_manifest(self):
        # Supplying an assumption registry routes provenance through the
        # collector; in PR3a it yields the same entries as the registry-free path.
        pop = _population(n=100)
        scenario = _scenario(_wealth_tax())
        without = run_scenario(pop, scenario)
        with_reg = run_scenario(pop, scenario, registries=Registries(assumptions=load_assumptions()))
        assert {e.output_label for e in with_reg.provenance.entries} == {
            e.output_label for e in without.provenance.entries
        }


class TestEngineResultModel:
    def test_rejects_bad_decile_count(self):
        with pytest.raises(ValidationError, match="revenue_by_decile must have"):
            EngineResult(
                scenario=_scenario(_wealth_tax()),
                total_revenue_gbp_bn=Interval(low=0, central=0, high=0),
                revenue_by_nation={},
                revenue_by_decile=[Interval(low=0, central=0, high=0)] * 3,
                households_scored=0,
                provenance=ProvenanceManifest(version_tag=_version(), assumptions_consumed={}, entries=[]),
            )
