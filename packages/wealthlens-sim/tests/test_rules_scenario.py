"""Tests for the rules/ scenario runner (Wave 12 PR2)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wealthlens_sim.reforms.a_annual_wealth import WealthTaxConfig, compute_aggregate_revenue
from wealthlens_sim.reforms.b_one_off_levy import OneOffLevyConfig, compute_aggregate_one_off_revenue
from wealthlens_sim.reforms.c_cgt_reform import CGTConfig, compute_aggregate_cgt_revenue
from wealthlens_sim.reforms.d_iht_reform import IHTConfig, compute_aggregate_iht_revenue
from wealthlens_sim.reforms.e_property_tax import HVCTSConfig, compute_aggregate_hvcts_revenue
from wealthlens_sim.rules import (
    FamilySelection,
    PolicyFamily,
    Scenario,
    ScenarioResult,
    run_scenario,
)
from wealthlens_sim.schema.base import VersionTag
from wealthlens_sim.synth import SynthConfig, generate_population


def _version() -> VersionTag:
    return VersionTag(
        macro_baseline_version="NBS-2025",
        policy_version="2026-05-21",
        population_version="synth-v0.1",
        wealthlens_sim_version="0.1.0",
    )


def _population():
    return generate_population(SynthConfig(n_households=1_500, seed=11)).households


def _wealth_tax(threshold: float = 1_000_000, rate: float = 0.01) -> FamilySelection:
    return FamilySelection(
        family=PolicyFamily.ANNUAL_WEALTH_TAX,
        config=WealthTaxConfig(threshold=threshold, rate=rate),
    )


class TestFamilySelection:
    def test_valid_selection(self):
        sel = _wealth_tax()
        assert sel.family == PolicyFamily.ANNUAL_WEALTH_TAX

    def test_rejects_mismatched_config(self):
        with pytest.raises(ValidationError, match="requires a WealthTaxConfig"):
            FamilySelection(family=PolicyFamily.ANNUAL_WEALTH_TAX, config=IHTConfig())

    def test_iht_selection_accepts_iht_config(self):
        sel = FamilySelection(family=PolicyFamily.IHT, config=IHTConfig())
        assert sel.family == PolicyFamily.IHT

    def test_dict_config_coerced_to_family_type(self):
        # A sparse/empty dict must coerce to the FAMILY's config type, not the
        # first overlapping union member (WealthTaxConfig).
        iht = FamilySelection(family=PolicyFamily.IHT, config={})
        assert isinstance(iht.config, IHTConfig)
        levy = FamilySelection(
            family=PolicyFamily.ONE_OFF_LEVY, config={"threshold": 1_000_000, "rate": 0.05}
        )
        assert isinstance(levy.config, OneOffLevyConfig)
        cgt = FamilySelection(family=PolicyFamily.CGT, config={})
        assert isinstance(cgt.config, CGTConfig)


class TestScenario:
    def test_rejects_empty_families(self):
        with pytest.raises(ValidationError):
            Scenario(name="empty", version_tag=_version(), families=[])

    def test_rejects_duplicate_families(self):
        with pytest.raises(ValidationError, match="at most once"):
            Scenario(name="dup", version_tag=_version(), families=[_wealth_tax(), _wealth_tax()])


class TestRunScenario:
    def test_single_family_matches_direct_aggregate(self):
        households = _population()
        cfg = WealthTaxConfig(threshold=1_000_000, rate=0.01)
        scenario = Scenario(
            name="wealth-only",
            version_tag=_version(),
            families=[FamilySelection(family=PolicyFamily.ANNUAL_WEALTH_TAX, config=cfg)],
        )
        result = run_scenario(households, scenario)
        direct = compute_aggregate_revenue(households, cfg)
        assert isinstance(result, ScenarioResult)
        assert result.total_revenue_bn == pytest.approx(direct.total_revenue_bn)
        assert result.family_revenues[0].revenue_by_nation == direct.revenue_by_nation

    def test_multi_family_total_is_sum(self):
        households = _population()
        scenario = Scenario(
            name="multi",
            version_tag=_version(),
            families=[
                _wealth_tax(),
                FamilySelection(family=PolicyFamily.IHT, config=IHTConfig()),
                FamilySelection(family=PolicyFamily.HVCTS, config=HVCTSConfig()),
            ],
        )
        result = run_scenario(households, scenario)
        assert len(result.family_revenues) == 3
        assert result.total_revenue_bn == pytest.approx(
            sum(fr.total_revenue_bn for fr in result.family_revenues)
        )
        # A wealth tax at a £1m threshold over a Pareto-tailed population raises > 0.
        assert result.total_revenue_bn > 0

    def test_revenue_by_nation_merges_across_families(self):
        households = _population()
        scenario = Scenario(
            name="merge",
            version_tag=_version(),
            families=[
                _wealth_tax(),
                FamilySelection(family=PolicyFamily.IHT, config=IHTConfig()),
            ],
        )
        result = run_scenario(households, scenario)
        for nation, total in result.revenue_by_nation.items():
            per_family = sum(fr.revenue_by_nation.get(nation, 0.0) for fr in result.family_revenues)
            assert total == pytest.approx(per_family)
        # Merged nations are the union of the families' nations.
        union = set().union(*(fr.revenue_by_nation.keys() for fr in result.family_revenues))
        assert set(result.revenue_by_nation.keys()) == union

    def test_deterministic(self):
        households = _population()
        scenario = Scenario(name="det", version_tag=_version(), families=[_wealth_tax()])
        r1 = run_scenario(households, scenario)
        r2 = run_scenario(households, scenario)
        assert r1.total_revenue_bn == r2.total_revenue_bn
        assert r1.revenue_by_nation == r2.revenue_by_nation

    @pytest.mark.parametrize(
        ("family", "config", "agg_fn"),
        [
            (PolicyFamily.ANNUAL_WEALTH_TAX, WealthTaxConfig(threshold=1_000_000, rate=0.01), compute_aggregate_revenue),
            (PolicyFamily.ONE_OFF_LEVY, OneOffLevyConfig(threshold=1_000_000, rate=0.05), compute_aggregate_one_off_revenue),
            (PolicyFamily.CGT, CGTConfig(), compute_aggregate_cgt_revenue),
            (PolicyFamily.IHT, IHTConfig(), compute_aggregate_iht_revenue),
            (PolicyFamily.HVCTS, HVCTSConfig(), compute_aggregate_hvcts_revenue),
        ],
    )
    def test_each_family_matches_direct_aggregate(self, family, config, agg_fn):
        # Pins dispatch correctness for ALL five families (not just A).
        households = _population()
        scenario = Scenario(
            name="single", version_tag=_version(), families=[FamilySelection(family=family, config=config)]
        )
        result = run_scenario(households, scenario)
        direct = agg_fn(households, config)
        assert result.total_revenue_bn == pytest.approx(direct.total_revenue_bn)
        assert result.family_revenues[0].revenue_by_nation == direct.revenue_by_nation
