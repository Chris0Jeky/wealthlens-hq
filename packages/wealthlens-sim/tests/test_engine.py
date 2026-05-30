"""Tests for the engine/ orchestrator (Wave 12 PR3a).

Covers the synth -> rules -> provenance wiring, the decile-attribution invariant
(decile sum ~= aggregate total), equal-weight deciles under heterogeneous survey
weights, the PopulationSource protocol seam, the provenance manifest + the
known-incomplete marker, and edge cases (empty population, non-positive weight).
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
    simulate,
)
from wealthlens_sim.provenance.manifest import PipelineLayer, ProvenanceManifest
from wealthlens_sim.reforms.a_annual_wealth import WealthTaxConfig
from wealthlens_sim.reforms.d_iht_reform import IHTConfig
from wealthlens_sim.reforms.e_property_tax import HVCTSConfig
from wealthlens_sim.rules import FamilySelection, PolicyFamily, Scenario
from wealthlens_sim.rules import run_scenario as run_families
from wealthlens_sim.schema.base import Nation, VersionTag
from wealthlens_sim.schema.household import Asset, AssetType, Household, Person
from wealthlens_sim.synth import SynthConfig, SyntheticPopulation, generate_population
from wealthlens_sim.top_tail.types import Interval


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


def _household(hid: str, net_wealth: float, weight: float) -> Household:
    return Household(
        household_id=hid,
        nation=Nation.ENGLAND,
        weight=weight,
        persons=[
            Person(
                person_id=f"{hid}-p1",
                age=50,
                assets=[Asset(asset_type=AssetType.FINANCIAL, gross_value=net_wealth)],
            )
        ],
    )


class TestPopulationSourceSeam:
    def test_synthetic_population_satisfies_protocol(self):
        pop = _population(n=50)
        assert isinstance(pop, PopulationSource)

    def test_protocol_needs_households_and_provenance_ids(self):
        class Missing:
            def __init__(self) -> None:
                self.households: list[object] = []  # no provenance_ids attribute

        assert not isinstance(Missing(), PopulationSource)


class TestSimulate:
    def test_returns_engine_result(self):
        result = simulate(_population(), _scenario(_wealth_tax()))
        assert isinstance(result, EngineResult)
        assert isinstance(result.total_revenue_gbp_bn, Interval)
        assert isinstance(result.provenance, ProvenanceManifest)

    def test_total_matches_rules_aggregate(self):
        pop = _population()
        scenario = _scenario(_wealth_tax())
        result = simulate(pop, scenario)
        aggregate = run_families(pop.households, scenario)
        assert result.total_revenue_gbp_bn.central == pytest.approx(aggregate.total_revenue_bn)

    def test_households_scored_counts_population(self):
        pop = _population(n=500)
        result = simulate(pop, _scenario(_wealth_tax()))
        assert result.households_scored == 500

    def test_intervals_are_degenerate_in_pr3a(self):
        # PR3a placeholder: low == central == high until PR3c propagates ranges.
        result = simulate(_population(), _scenario(_wealth_tax()))
        iv = result.total_revenue_gbp_bn
        assert iv.low == iv.central == iv.high

    def test_deterministic(self):
        pop = _population()
        scenario = _scenario(_wealth_tax())
        r1 = simulate(pop, scenario)
        r2 = simulate(pop, scenario)
        assert r1.total_revenue_gbp_bn == r2.total_revenue_gbp_bn
        assert r1.revenue_by_decile == r2.revenue_by_decile

    def test_revenue_by_nation_matches_aggregate(self):
        pop = _population()
        scenario = _scenario(
            _wealth_tax(),
            FamilySelection(family=PolicyFamily.HVCTS, config=HVCTSConfig()),
        )
        result = simulate(pop, scenario)
        aggregate = run_families(pop.households, scenario)
        for nation, interval in result.revenue_by_nation.items():
            assert interval.central == pytest.approx(aggregate.revenue_by_nation[nation])

    def test_surfaces_population_provenance_ids(self):
        # The population's own provenance ids must not be silently dropped.
        pop = SyntheticPopulation(households=[], seed=0, provenance_ids=["was-2022", "frs-2023"])
        result = simulate(pop, _scenario(_wealth_tax()))
        assert result.population_provenance_ids == ["was-2022", "frs-2023"]


class TestDecileAttribution:
    def test_decile_count_is_ten(self):
        result = simulate(_population(), _scenario(_wealth_tax()))
        assert len(result.revenue_by_decile) == N_DECILES

    def test_decile_sum_equals_total(self):
        # The core invariant: per-household decile attribution and the aggregate
        # total are computed by the same calculators, so they agree to float order.
        pop = _population()
        scenario = _scenario(
            _wealth_tax(),
            FamilySelection(family=PolicyFamily.IHT, config=IHTConfig()),
        )
        result = simulate(pop, scenario)
        decile_sum = sum(iv.central for iv in result.revenue_by_decile)
        assert decile_sum == pytest.approx(result.total_revenue_gbp_bn.central)

    def test_wealth_tax_revenue_concentrated_in_top_decile(self):
        # A £1m-threshold wealth tax falls on the wealthiest households, so the
        # top decile (index 9) must out-raise the bottom decile (index 0).
        pop = _population()
        result = simulate(pop, _scenario(_wealth_tax()))
        assert result.revenue_by_decile[-1].central > result.revenue_by_decile[0].central

    def test_heterogeneous_weights_place_rich_household_in_top_decile(self):
        # A highest-wealth household that is heavily weighted — but whose weight
        # is still within one decile band — must land its revenue in the TOP
        # decile, where its WEALTH places it. Naive centre-of-mass binning would
        # misplace it toward the middle; equal-weight boundary-splitting does not.
        # The 99 sub-threshold households pay nothing, so all revenue is the rich
        # household's, and the decile sum still equals the aggregate total.
        households = [_household(f"h{i}", net_wealth=10_000.0 * (i + 1), weight=1.0) for i in range(99)]
        # weight 10 < one band (total 109 / 10 = 10.9), so it sits wholly in decile 9.
        households.append(_household("rich", net_wealth=5_000_000.0, weight=10.0))
        cfg = _wealth_tax(threshold=1_000_000, rate=0.01)
        deciles = revenue_by_wealth_decile(households, [cfg], n_deciles=N_DECILES)
        assert deciles[-1] > 0
        assert sum(deciles[:-1]) == pytest.approx(0.0)
        aggregate = run_families(households, _scenario(cfg))
        assert sum(deciles) == pytest.approx(aggregate.total_revenue_bn)

    def test_dominant_weight_household_loads_top_decile_most(self):
        # Equal-weight deciles are slices of the *weighted* population. A single
        # household carrying most of the grossing weight legitimately occupies
        # almost every decile (it IS most of the population), but its revenue is
        # still loaded toward the top (most in the top decile, least in the
        # bottom) and the sum is conserved — no revenue is lost or invented.
        households = [_household(f"h{i}", net_wealth=10_000.0 * (i + 1), weight=1.0) for i in range(99)]
        households.append(_household("rich", net_wealth=5_000_000.0, weight=1000.0))
        cfg = _wealth_tax(threshold=1_000_000, rate=0.01)
        deciles = revenue_by_wealth_decile(households, [cfg], n_deciles=N_DECILES)
        assert deciles[-1] == pytest.approx(max(deciles))  # top decile holds the most
        assert deciles[0] == pytest.approx(min(deciles))  # bottom decile holds the least
        aggregate = run_families(households, _scenario(cfg))
        assert sum(deciles) == pytest.approx(aggregate.total_revenue_bn)

    def test_tiny_weight_household_conserves_revenue(self):
        # Regression (review R2): a sub-1e-9 grossing weight straddling a band
        # boundary must not drop revenue. The decile sum must still equal the
        # aggregate total — conservation holds for any positive weight.
        households = [
            _household("a", net_wealth=3_000_000.0, weight=3.0),
            _household("tiny", net_wealth=4_000_000.0, weight=1e-12),
            _household("b", net_wealth=5_000_000.0, weight=6.999_999_999),
        ]
        cfg = _wealth_tax(threshold=1_000_000, rate=0.01)
        deciles = revenue_by_wealth_decile(households, [cfg], n_deciles=N_DECILES)
        aggregate = run_families(households, _scenario(cfg))
        assert sum(deciles) == pytest.approx(aggregate.total_revenue_bn)

    def test_empty_population_has_no_deciles(self):
        empty = SyntheticPopulation(households=[], seed=0)
        result = simulate(empty, _scenario(_wealth_tax()))
        assert result.revenue_by_decile == []
        assert result.households_scored == 0
        assert result.total_revenue_gbp_bn.central == 0.0

    def test_non_positive_total_weight_raises(self):
        # A non-empty population with non-positive weight is a data defect and is
        # surfaced loudly, not collapsed into an empty (publishable-looking) result.
        households = [_household("h1", net_wealth=2_000_000.0, weight=1.0)]
        object.__setattr__(households[0], "weight", 0.0)  # bypass frozen for the test
        with pytest.raises(ValueError, match="total household weight must be positive"):
            revenue_by_wealth_decile(households, [_wealth_tax()])

    def test_negative_weight_raises(self):
        # A negative weight would wrap to a negative decile index; reject it.
        households = [_household("h1", net_wealth=2_000_000.0, weight=1.0)]
        object.__setattr__(households[0], "weight", -1.0)
        with pytest.raises(ValueError, match="household weights must be non-negative"):
            revenue_by_wealth_decile(households, [_wealth_tax()])

    def test_invalid_n_deciles_raises(self):
        households = [_household("h1", net_wealth=2_000_000.0, weight=1.0)]
        with pytest.raises(ValueError, match="n_deciles must be strictly positive"):
            revenue_by_wealth_decile(households, [_wealth_tax()], n_deciles=0)


class TestProvenance:
    def test_manifest_records_revenue_outputs(self):
        result = simulate(_population(n=100), _scenario(_wealth_tax()))
        labels = {e.output_label for e in result.provenance.entries}
        assert "total_revenue_gbp_bn" in labels
        assert all(e.layer == PipelineLayer.REVENUE for e in result.provenance.entries)

    def test_provenance_marked_incomplete_in_pr3a(self):
        # PR3a does not consume the assumptions the numbers depend on, so the
        # result must declare its provenance incomplete.
        result = simulate(_population(n=100), _scenario(_wealth_tax()))
        assert result.provenance_complete is False

    def test_manifest_uses_scenario_version_tag(self):
        scenario = _scenario(_wealth_tax())
        result = simulate(_population(n=100), scenario)
        assert result.provenance.version_tag == scenario.version_tag

    def test_registry_path_builds_equivalent_entries(self):
        # Supplying an assumption registry routes provenance through the
        # collector; in PR3a it yields the same entries as the registry-free path
        # (run_timestamp aside, which is necessarily per-run).
        pop = _population(n=100)
        scenario = _scenario(_wealth_tax())
        without = simulate(pop, scenario)
        with_reg = simulate(pop, scenario, registries=Registries(assumptions=load_assumptions()))
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
