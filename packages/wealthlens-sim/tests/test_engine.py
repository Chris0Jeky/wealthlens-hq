"""Tests for the engine/ orchestrator (Wave 12 PR3).

Covers the synth -> rules -> provenance wiring; the decile-attribution invariant
(decile sum ~= aggregate total) and equal-weight deciles under heterogeneous
weights; the PopulationSource protocol seam; Family G devolution scoping; Family F
enforcement uplift; interval propagation from the top-tail alpha range and the
complete-vs-incomplete provenance marker; and edge cases (empty population,
non-positive weight).
"""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from wealthlens_sim.assumptions import load_assumptions
from wealthlens_sim.assumptions.schema import (
    Assumption,
    AssumptionRegistry,
    PointValue,
    TransferabilityScore,
)
from wealthlens_sim.engine import (
    N_DECILES,
    DevolutionConfig,
    EngineResult,
    PopulationSource,
    Registries,
    revenue_by_wealth_decile,
    simulate,
    tax_family_for,
)
from wealthlens_sim.engine._intervals import revenue_scale_from_alpha
from wealthlens_sim.provenance.manifest import PipelineLayer, ProvenanceManifest
from wealthlens_sim.reforms.a_annual_wealth import WealthTaxConfig
from wealthlens_sim.reforms.d_iht_reform import IHTConfig
from wealthlens_sim.reforms.e_property_tax import HVCTSConfig
from wealthlens_sim.reforms.f_enforcement import (
    ENFORCEMENT_COMPLIANCE_ASSUMPTION_ID,
    ComplianceRate,
    EnforcementConfig,
    TaxFamily,
)
from wealthlens_sim.reforms.g_devolution import NationScope
from wealthlens_sim.rules import FamilySelection, PolicyFamily, Scenario
from wealthlens_sim.rules import run_scenario as run_families
from wealthlens_sim.schema.base import Nation, VersionTag
from wealthlens_sim.schema.household import Asset, AssetType, Household, Person
from wealthlens_sim.synth import SynthConfig, SyntheticPopulation, generate_population
from wealthlens_sim.top_tail.types import Interval
from wealthlens_sim.uncertainty import SamplingConfig


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

    def test_intervals_degenerate_without_registry(self):
        # No registry => uncertainty unquantified => degenerate intervals.
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

    def test_provenance_incomplete_without_registry(self):
        # Without a registry the engine consumes no assumptions, so it must
        # declare its provenance incomplete.
        result = simulate(_population(n=100), _scenario(_wealth_tax()))
        assert result.provenance_complete is False

    def test_provenance_complete_with_registry(self):
        # With the assumption registry, the engine consumes the top-tail alpha and
        # records it against every revenue output, so provenance is complete.
        pop = _population(n=100)
        scenario = _scenario(_wealth_tax())
        result = simulate(pop, scenario, registries=Registries(assumptions=load_assumptions()))
        assert result.provenance_complete is True
        assert "toptail.pareto_alpha.overall.v1" in result.provenance.assumptions_consumed
        for entry in result.provenance.entries:
            if entry.output_label in {"total_revenue_gbp_bn", "revenue_by_nation", "revenue_by_decile"}:
                assert "toptail.pareto_alpha.overall.v1" in entry.assumption_ids

    def test_enforcement_provenance_records_compliance_model(self):
        pop = _population(n=100)
        scenario = _scenario(_wealth_tax())
        result = simulate(
            pop,
            scenario,
            registries=Registries(assumptions=load_assumptions()),
            enforcement=EnforcementConfig(
                compliance_rates=(
                    ComplianceRate(tax_family=TaxFamily.OTHER, baseline_rate=0.8, scenario_rate=0.9),
                ),
                enforcement_cost_bn=0.25,
            ),
        )
        assert ENFORCEMENT_COMPLIANCE_ASSUMPTION_ID in result.provenance.assumptions_consumed
        resolved = result.provenance.assumptions_consumed[ENFORCEMENT_COMPLIANCE_ASSUMPTION_ID]
        assert "gov.uk/government/statistics/measuring-tax-gaps" in resolved.source
        assert "nao.org.uk/reports/collecting-the-right-tax-from-wealthy-individuals" in resolved.source
        for entry in result.provenance.entries:
            if entry.output_label in {
                "total_revenue_gbp_bn",
                "revenue_by_nation",
                "revenue_by_decile",
                "enforcement_uplift_gbp_bn",
                "enforcement_cost_gbp_bn",
                "enforcement_net_fiscal_impact_gbp_bn",
            }:
                assert ENFORCEMENT_COMPLIANCE_ASSUMPTION_ID in entry.assumption_ids

    def test_manifest_uses_scenario_version_tag(self):
        scenario = _scenario(_wealth_tax())
        result = simulate(_population(n=100), scenario)
        assert result.provenance.version_tag == scenario.version_tag


class TestMonteCarloUncertainty:
    """The optional ``uncertainty`` config replaces the single multiplicative alpha
    band with a Monte-Carlo credible interval — default OFF."""

    @staticmethod
    def _registries() -> Registries:
        return Registries(assumptions=load_assumptions())

    def test_off_by_default(self):
        result = simulate(_population(n=100), _scenario(_wealth_tax()), registries=self._registries())
        assert result.uncertainty_provenance_ids == []

    def test_mc_produces_band_and_provenance(self):
        result = simulate(
            _population(n=100), _scenario(_wealth_tax()), registries=self._registries(),
            uncertainty=SamplingConfig(n_samples=512, seed=0),
        )
        iv = result.total_revenue_gbp_bn
        assert iv.low < iv.high                      # a real sampled band
        assert iv.low <= iv.central <= iv.high
        ids = result.uncertainty_provenance_ids
        assert any(s.startswith("uncertainty.n_samples:") for s in ids)
        assert any(s.startswith("uncertainty.specs:") for s in ids)
        assert "uncertainty.central:explicit:1.0" in ids
        assert any(s.startswith("uncertainty.quantiles:") for s in ids)

    def test_mc_central_matches_single_band(self):
        # Enabling MC must not move the headline: central is the point estimate.
        pop, scenario = _population(n=100), _scenario(_wealth_tax())
        single = simulate(pop, scenario, registries=self._registries())
        mc = simulate(pop, scenario, registries=self._registries(),
                      uncertainty=SamplingConfig(n_samples=512, seed=0))
        assert mc.total_revenue_gbp_bn.central == pytest.approx(single.total_revenue_gbp_bn.central)
        for d_single, d_mc in zip(single.revenue_by_decile, mc.revenue_by_decile, strict=True):
            assert d_mc.central == pytest.approx(d_single.central)

    def test_mc_band_within_single_band(self):
        # The 5-95 quantile band is contained in the full alpha-range band.
        pop, scenario = _population(n=100), _scenario(_wealth_tax())
        single = simulate(pop, scenario, registries=self._registries())
        mc = simulate(pop, scenario, registries=self._registries(),
                      uncertainty=SamplingConfig(n_samples=2000, seed=1))
        s, m = single.total_revenue_gbp_bn, mc.total_revenue_gbp_bn
        assert s.low <= m.low <= m.central <= m.high <= s.high

    def test_mc_deterministic(self):
        pop, scenario = _population(n=100), _scenario(_wealth_tax())
        cfg = SamplingConfig(n_samples=256, seed=7)
        a = simulate(pop, scenario, registries=self._registries(), uncertainty=cfg)
        b = simulate(pop, scenario, registries=self._registries(), uncertainty=cfg)
        assert a.total_revenue_gbp_bn == b.total_revenue_gbp_bn
        assert a.uncertainty_provenance_ids == b.uncertainty_provenance_ids

    def test_mc_without_registry_is_noop(self):
        # No registry alpha → MC cannot run; degenerate band, no MC provenance.
        result = simulate(_population(n=100), _scenario(_wealth_tax()),
                          uncertainty=SamplingConfig(n_samples=256, seed=0))
        iv = result.total_revenue_gbp_bn
        assert iv.low == iv.central == iv.high
        assert result.uncertainty_provenance_ids == []

    def test_devolution_scope_recorded_in_manifest(self):
        # A scoped run with a registry records the territorial scope in the manifest.
        pop = _population(n=200)
        result = simulate(
            pop,
            _scenario(_wealth_tax()),
            registries=Registries(assumptions=load_assumptions()),
            devolution=DevolutionConfig(scope=NationScope.ENGLAND_ONLY),
        )
        labels = {e.output_label for e in result.provenance.entries}
        assert "devolution_scope:england_only" in labels


class TestDevolution:
    def test_no_devolution_scores_whole_population(self):
        result = simulate(_population(), _scenario(_wealth_tax()))
        assert result.devolution_split is None

    def test_england_only_scores_england_subset(self):
        pop = _population()
        cfg = _wealth_tax()
        scenario = _scenario(cfg)
        result = simulate(pop, scenario, devolution=DevolutionConfig(scope=NationScope.ENGLAND_ONLY))
        england = [h for h in pop.households if h.nation == Nation.ENGLAND]
        # Only England is scored; the split summary stays visible.
        assert result.households_scored == len(england)
        assert result.devolution_split is not None
        assert result.devolution_split.included_nations == ("england",)
        assert result.devolution_split.excluded_count == len(pop.households) - len(england)
        # Revenue equals the rules aggregate over the England-only subset.
        aggregate = run_families(england, scenario)
        assert result.total_revenue_gbp_bn.central == pytest.approx(aggregate.total_revenue_bn)
        # Non-England nations contribute nothing.
        assert set(result.revenue_by_nation) <= {"england"}

    def test_custom_scope_scores_only_named_nation(self):
        pop = _population()
        cfg = DevolutionConfig(scope=NationScope.CUSTOM, included_nations=frozenset({Nation.SCOTLAND}))
        result = simulate(pop, _scenario(_wealth_tax()), devolution=cfg)
        scotland = [h for h in pop.households if h.nation == Nation.SCOTLAND]
        assert result.households_scored == len(scotland)
        assert result.devolution_split is not None
        assert result.devolution_split.included_nations == ("scotland",)

    def test_great_britain_scope_excludes_northern_ireland(self):
        pop = _population()
        result = simulate(pop, _scenario(_wealth_tax()), devolution=DevolutionConfig(scope=NationScope.GREAT_BRITAIN))
        assert result.devolution_split is not None
        assert result.devolution_split.included_nations == ("england", "scotland", "wales")
        assert "northern_ireland" in result.devolution_split.excluded_nations
        assert "northern_ireland" not in result.revenue_by_nation

    def test_custom_multi_nation_scope(self):
        pop = _population()
        cfg = DevolutionConfig(scope=NationScope.CUSTOM, included_nations=frozenset({Nation.SCOTLAND, Nation.WALES}))
        result = simulate(pop, _scenario(_wealth_tax()), devolution=cfg)
        included = [h for h in pop.households if h.nation in {Nation.SCOTLAND, Nation.WALES}]
        assert result.households_scored == len(included)
        assert result.devolution_split is not None
        assert result.devolution_split.included_nations == ("scotland", "wales")
        assert set(result.revenue_by_nation) <= {"scotland", "wales"}

    def test_england_only_drops_exactly_the_excluded_nations_revenue(self):
        # The revenue removed by an England-only scope must equal the revenue the
        # excluded nations contributed UK-wide — proving the filter removes their
        # revenue, not merely their household count.
        pop = _population()
        scenario = _scenario(_wealth_tax())
        uk_wide = simulate(pop, scenario)
        england_only = simulate(pop, scenario, devolution=DevolutionConfig(scope=NationScope.ENGLAND_ONLY))
        excluded_revenue = sum(
            value.central for nation, value in uk_wide.revenue_by_nation.items() if nation != "england"
        )
        dropped = uk_wide.total_revenue_gbp_bn.central - england_only.total_revenue_gbp_bn.central
        assert dropped == pytest.approx(excluded_revenue)

    def test_decile_invariant_holds_on_included_subset(self):
        pop = _population()
        scenario = _scenario(_wealth_tax())
        result = simulate(pop, scenario, devolution=DevolutionConfig(scope=NationScope.ENGLAND_ONLY))
        decile_sum = sum(iv.central for iv in result.revenue_by_decile)
        assert decile_sum == pytest.approx(result.total_revenue_gbp_bn.central)

    def test_scope_excluding_all_households_yields_zero(self):
        # An all-England population scoped to Scotland-only scores nobody.
        households = [_household(f"h{i}", net_wealth=3_000_000.0, weight=1.0) for i in range(20)]
        pop = SyntheticPopulation(households=households, seed=0)
        cfg = DevolutionConfig(scope=NationScope.CUSTOM, included_nations=frozenset({Nation.SCOTLAND}))
        result = simulate(pop, _scenario(_wealth_tax()), devolution=cfg)
        assert result.households_scored == 0
        assert result.total_revenue_gbp_bn.central == 0.0
        assert result.revenue_by_decile == []
        assert result.devolution_split is not None
        assert result.devolution_split.included_count == 0


class TestEnforcement:
    def _enforcement(self, family=TaxFamily.OTHER, baseline=0.8, scenario=0.9, cost=0.0):
        return EnforcementConfig(
            compliance_rates=(ComplianceRate(tax_family=family, baseline_rate=baseline, scenario_rate=scenario),),
            enforcement_cost_bn=cost,
        )

    def test_no_enforcement_uplift_is_zero(self):
        result = simulate(_population(), _scenario(_wealth_tax()))
        assert result.enforcement_uplift_bn.central == 0.0

    def test_enforcement_applies_compliance_without_exceeding_theoretical(self):
        # The annual wealth tax maps to TaxFamily.OTHER; an OTHER compliance
        # improvement moves baseline revenue toward the theoretical ceiling.
        pop = _population()
        scenario = _scenario(_wealth_tax())
        base = simulate(pop, scenario)
        with_enf = simulate(pop, scenario, enforcement=self._enforcement(baseline=0.8, scenario=0.9))
        # OTHER theoretical = wealth-tax revenue; uplift = theoretical * (0.9 - 0.8).
        expected_uplift = base.total_revenue_gbp_bn.central * 0.1
        assert with_enf.enforcement_uplift_bn.central == pytest.approx(expected_uplift)
        assert with_enf.total_revenue_gbp_bn.central == pytest.approx(base.total_revenue_gbp_bn.central * 0.9)
        assert with_enf.total_revenue_gbp_bn.central <= base.total_revenue_gbp_bn.central

    def test_decile_invariant_excludes_enforcement(self):
        # Enforcement uplift is aggregate-only: deciles cover baseline-compliance
        # family revenue, so sum(deciles) == total - enforcement_uplift.
        pop = _population()
        result = simulate(pop, _scenario(_wealth_tax()), enforcement=self._enforcement(baseline=0.7, scenario=0.95))
        decile_sum = sum(iv.central for iv in result.revenue_by_decile)
        assert decile_sum == pytest.approx(result.total_revenue_gbp_bn.central - result.enforcement_uplift_bn.central)
        assert result.enforcement_uplift_bn.central > 0

    def test_nation_breakdown_uses_baseline_compliance_with_enforcement(self):
        pop = _population()
        scenario = _scenario(_wealth_tax())
        base = simulate(pop, scenario)
        result = simulate(pop, scenario, enforcement=self._enforcement(baseline=0.8, scenario=0.9))
        assert result.revenue_by_nation["england"].central == pytest.approx(
            base.revenue_by_nation["england"].central * 0.8
        )

    def test_nation_invariant_excludes_enforcement(self):
        # Like deciles, nation revenue covers baseline-compliance family revenue;
        # the aggregate enforcement uplift stays separate.
        pop = _population()
        result = simulate(pop, _scenario(_wealth_tax()), enforcement=self._enforcement(baseline=0.7, scenario=0.95))
        nation_sum = sum(iv.central for iv in result.revenue_by_nation.values())
        assert nation_sum == pytest.approx(result.total_revenue_gbp_bn.central - result.enforcement_uplift_bn.central)

    def test_unconfigured_family_stays_at_full_revenue_with_enforcement(self):
        # An OTHER compliance rate changes wealth-tax revenue only; IHT maps to
        # its own tax family and has no configured rate here, so it remains at
        # its full theoretical revenue.
        pop = _population()
        wealth = _wealth_tax()
        iht = FamilySelection(family=PolicyFamily.IHT, config=IHTConfig())
        wealth_only = simulate(pop, _scenario(wealth))
        iht_only = simulate(pop, _scenario(iht))
        result = simulate(
            pop,
            _scenario(wealth, iht),
            enforcement=self._enforcement(family=TaxFamily.OTHER, baseline=0.8, scenario=0.9),
        )
        assert result.total_revenue_gbp_bn.central == pytest.approx(
            wealth_only.total_revenue_gbp_bn.central * 0.9 + iht_only.total_revenue_gbp_bn.central
        )

    def test_enforcement_cost_is_reported_separately_from_revenue(self):
        pop = _population()
        scenario = _scenario(_wealth_tax())
        no_cost = simulate(pop, scenario, enforcement=self._enforcement(cost=0.0))
        with_cost = simulate(pop, scenario, enforcement=self._enforcement(cost=1.0))
        assert with_cost.enforcement_uplift_bn.central == pytest.approx(no_cost.enforcement_uplift_bn.central)
        assert with_cost.enforcement_cost_bn.central == pytest.approx(1.0)
        assert with_cost.enforcement_net_fiscal_impact_bn.central == pytest.approx(
            no_cost.enforcement_uplift_bn.central - 1.0
        )

    def test_cgt_and_iht_map_to_own_tax_family(self):
        assert tax_family_for(PolicyFamily.CGT) == TaxFamily.CGT
        assert tax_family_for(PolicyFamily.IHT) == TaxFamily.IHT
        assert tax_family_for(PolicyFamily.ANNUAL_WEALTH_TAX) == TaxFamily.OTHER
        assert tax_family_for(PolicyFamily.HVCTS) == TaxFamily.OTHER

    def test_negative_net_fiscal_impact_does_not_reduce_revenue_headline(self):
        # Documented contract: an enforcement cost exceeding the gross uplift
        # yields a negative net fiscal impact but does not reduce revenue.
        pop = _population()
        scenario = _scenario(_wealth_tax())
        base = simulate(pop, scenario)
        gross_uplift = base.total_revenue_gbp_bn.central * 0.1  # OTHER 0.8 -> 0.9
        result = simulate(
            pop,
            scenario,
            enforcement=self._enforcement(baseline=0.8, scenario=0.9, cost=gross_uplift + 5.0),
        )
        assert result.enforcement_uplift_bn.central == pytest.approx(gross_uplift)
        assert result.enforcement_net_fiscal_impact_bn.central == pytest.approx(-5.0)
        assert result.total_revenue_gbp_bn.central == pytest.approx(base.total_revenue_gbp_bn.central * 0.9)

    def test_other_bucket_sums_multiple_families(self):
        # Wealth tax AND HVCTS both map to OTHER, so a single OTHER compliance rate
        # applies to their COMBINED revenue base.
        pop = _population()
        scenario = _scenario(
            _wealth_tax(),
            FamilySelection(family=PolicyFamily.HVCTS, config=HVCTSConfig()),
        )
        base = simulate(pop, scenario)
        with_enf = simulate(pop, scenario, enforcement=self._enforcement(baseline=0.8, scenario=0.9))
        # Uplift = (wealth + hvcts) revenue * (0.9 - 0.8) = base family total * 0.1.
        expected = base.total_revenue_gbp_bn.central * 0.1
        assert with_enf.enforcement_uplift_bn.central == pytest.approx(expected)

    def test_enforcement_on_unmatched_family_yields_zero_uplift(self):
        # A CGT compliance rate over a wealth-tax-only scenario has no CGT
        # theoretical revenue, so the uplift is zero (not an error).
        pop = _population()
        result = simulate(
            pop,
            _scenario(_wealth_tax()),
            enforcement=self._enforcement(family=TaxFamily.CGT, baseline=0.5, scenario=0.9),
        )
        assert result.enforcement_uplift_bn.central == pytest.approx(0.0)


def _registry_with_alpha(distribution) -> AssumptionRegistry:
    """Build a single-assumption registry whose alpha is the given distribution."""
    return AssumptionRegistry(
        assumptions=[
            Assumption(
                assumption_id="toptail.pareto_alpha.overall.v1",
                domain="top-tail",
                value_or_distribution=distribution,
                source="test",
                transferability_score=TransferabilityScore.MEDIUM,
                valid_range="alpha in [1.1, 2.5]",
                applies_to="test",
                last_reviewed=date(2026, 5, 30),
            )
        ]
    )


class TestIntervals:
    def _registries(self):
        return Registries(assumptions=load_assumptions())

    def test_registry_yields_non_degenerate_intervals(self):
        result = simulate(_population(), _scenario(_wealth_tax()), registries=self._registries())
        iv = result.total_revenue_gbp_bn
        assert iv.low < iv.central < iv.high

    def test_interval_scale_matches_tail_mean_ratio(self):
        # The low/high factors come from the Pareto tail-mean ratio at the alpha
        # bounds. These mirror registries/assumptions.yml (toptail.pareto_alpha
        # .overall.v1 = 1.3/1.5/1.8) and must be updated together if it changes.
        result = simulate(_population(), _scenario(_wealth_tax()), registries=self._registries())
        iv = result.total_revenue_gbp_bn
        central_factor = 1.5 / 0.5
        expected_low = iv.central * ((1.8 / 0.8) / central_factor)  # higher alpha -> less revenue
        expected_high = iv.central * ((1.3 / 0.3) / central_factor)  # lower alpha -> more revenue
        assert iv.low == pytest.approx(expected_low)
        assert iv.high == pytest.approx(expected_high)

    def test_missing_alpha_falls_back_to_degenerate(self):
        # A registry WITHOUT the alpha assumption is a legitimate fallback:
        # degenerate intervals + incomplete provenance, no error.
        registries = Registries(assumptions=AssumptionRegistry(assumptions=[]))
        result = simulate(_population(), _scenario(_wealth_tax()), registries=registries)
        iv = result.total_revenue_gbp_bn
        assert iv.low == iv.central == iv.high
        assert result.provenance_complete is False

    def test_malformed_alpha_raises(self):
        # A present-but-wrong-type alpha (PointValue, not a range) is a registry
        # defect and must fail loudly, not silently downgrade to degenerate.
        registries = Registries(assumptions=_registry_with_alpha(PointValue(type="point", value=1.5)))
        with pytest.raises(TypeError, match="must be a range"):
            simulate(_population(), _scenario(_wealth_tax()), registries=registries)

    def test_negative_net_fiscal_interval_ordering_with_registry(self):
        # With a non-degenerate revenue scale AND a negative net fiscal impact,
        # the derived net-impact interval must still satisfy low <= central <= high.
        pop = _population()
        scenario = _scenario(_wealth_tax())
        base = simulate(pop, scenario)
        gross = base.total_revenue_gbp_bn.central * 0.1
        enforcement = EnforcementConfig(
            compliance_rates=(ComplianceRate(tax_family=TaxFamily.OTHER, baseline_rate=0.8, scenario_rate=0.9),),
            enforcement_cost_bn=gross + 5.0,
        )
        result = simulate(pop, scenario, registries=self._registries(), enforcement=enforcement)
        iv = result.enforcement_net_fiscal_impact_bn
        assert iv.central < 0
        assert iv.low <= iv.central <= iv.high

    def test_negative_net_fiscal_impact_preserves_bound_invariants(self):
        # Regression: enforcement cost is not revenue, so even a negative net
        # fiscal impact cannot flip interval-bound conservation.
        pop = _population()
        scenario = _scenario(_wealth_tax())
        base = simulate(pop, scenario)
        gross = base.total_revenue_gbp_bn.central * 0.1
        enforcement = EnforcementConfig(
            compliance_rates=(ComplianceRate(tax_family=TaxFamily.OTHER, baseline_rate=0.8, scenario_rate=0.9),),
            enforcement_cost_bn=gross * 3,
        )
        result = simulate(pop, scenario, registries=self._registries(), enforcement=enforcement)
        assert result.enforcement_net_fiscal_impact_bn.central < 0
        for bound in ("low", "central", "high"):
            decile_sum = sum(getattr(iv, bound) for iv in result.revenue_by_decile)
            nation_sum = sum(getattr(iv, bound) for iv in result.revenue_by_nation.values())
            total = getattr(result.total_revenue_gbp_bn, bound)
            uplift = getattr(result.enforcement_uplift_bn, bound)
            assert decile_sum == pytest.approx(total - uplift)
            assert nation_sum == pytest.approx(total - uplift)

    def test_decile_invariant_at_every_bound_with_enforcement(self):
        # The subtraction path: deciles cover family revenue only, so at EVERY
        # bound sum(decile.bound) == total.bound - enforcement.bound.
        pop = _population()
        enforcement = EnforcementConfig(
            compliance_rates=(ComplianceRate(tax_family=TaxFamily.OTHER, baseline_rate=0.7, scenario_rate=0.95),),
        )
        result = simulate(pop, _scenario(_wealth_tax()), registries=self._registries(), enforcement=enforcement)
        for bound in ("low", "central", "high"):
            decile_sum = sum(getattr(iv, bound) for iv in result.revenue_by_decile)
            total = getattr(result.total_revenue_gbp_bn, bound)
            uplift = getattr(result.enforcement_uplift_bn, bound)
            assert decile_sum == pytest.approx(total - uplift)

    def test_nation_invariant_at_every_bound_with_enforcement(self):
        # Nation splits follow the same contract as deciles under enforcement:
        # they carry baseline-compliance family revenue, not the aggregate uplift.
        pop = _population()
        enforcement = EnforcementConfig(
            compliance_rates=(ComplianceRate(tax_family=TaxFamily.OTHER, baseline_rate=0.7, scenario_rate=0.95),),
        )
        result = simulate(pop, _scenario(_wealth_tax()), registries=self._registries(), enforcement=enforcement)
        for bound in ("low", "central", "high"):
            nation_sum = sum(getattr(iv, bound) for iv in result.revenue_by_nation.values())
            total = getattr(result.total_revenue_gbp_bn, bound)
            uplift = getattr(result.enforcement_uplift_bn, bound)
            assert nation_sum == pytest.approx(total - uplift)

    def test_tail_mean_factor_requires_alpha_above_one(self):
        # alpha <= 1 has an infinite tail mean; revenue_scale_from_alpha must raise
        # rather than fabricate a factor.
        with pytest.raises(ValueError, match="must exceed 1"):
            revenue_scale_from_alpha(Interval(low=0.5, central=0.8, high=0.95))

    def test_decile_invariant_holds_at_every_bound(self):
        # The same factor scales every figure, so the decile sum equals the total
        # (net of enforcement) at low, central, AND high.
        result = simulate(
            _population(),
            _scenario(_wealth_tax()),
            registries=self._registries(),
        )
        for bound in ("low", "central", "high"):
            decile_sum = sum(getattr(iv, bound) for iv in result.revenue_by_decile)
            total = getattr(result.total_revenue_gbp_bn, bound)
            assert decile_sum == pytest.approx(total)

    def test_intervals_deterministic(self):
        pop = _population()
        scenario = _scenario(_wealth_tax())
        r1 = simulate(pop, scenario, registries=self._registries())
        r2 = simulate(pop, scenario, registries=self._registries())
        assert r1.total_revenue_gbp_bn == r2.total_revenue_gbp_bn


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
