"""Tests for the v0.1 synthetic-population generator."""

from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from wealthlens_sim.schema.base import Nation
from wealthlens_sim.synth import SynthConfig, SyntheticPopulation, generate_population


def _small(**kw) -> SynthConfig:
    kw.setdefault("n_households", 2_000)
    kw.setdefault("seed", 7)
    return SynthConfig(**kw)


class TestSynthConfig:
    def test_defaults_valid(self):
        c = SynthConfig()
        assert c.n_households == 10_000
        assert abs(sum(c.nation_shares.values()) - 1.0) < 0.01
        assert abs(sum(c.asset_shares.values()) - 1.0) < 0.01

    def test_rejects_nation_shares_not_summing_to_one(self):
        with pytest.raises(ValidationError, match="nation_shares must sum"):
            SynthConfig(nation_shares={"england": 0.5, "scotland": 0.1})

    def test_rejects_asset_shares_not_summing_to_one(self):
        with pytest.raises(ValidationError, match="asset_shares must sum"):
            SynthConfig(asset_shares={"financial": 0.5})

    def test_frozen(self):
        c = SynthConfig()
        with pytest.raises(ValidationError, match="frozen"):
            c.seed = 9


class TestGeneratePopulation:
    def test_count_and_validity(self):
        pop = generate_population(_small())
        assert isinstance(pop, SyntheticPopulation)
        assert pop.is_synthetic is True
        assert len(pop.households) == 2_000
        for h in pop.households:
            assert h.nation in (Nation.ENGLAND, Nation.SCOTLAND, Nation.WALES, Nation.NORTHERN_IRELAND)
            assert h.nation != Nation.UK
            assert h.weight > 0
            assert len(h.persons) >= 1
            assert h.total_net_wealth > 0

    def test_deterministic_same_seed(self):
        a = generate_population(_small())
        b = generate_population(_small())
        wa = [h.total_net_wealth for h in a.households]
        wb = [h.total_net_wealth for h in b.households]
        assert wa == wb
        assert [h.nation for h in a.households] == [h.nation for h in b.households]

    def test_different_seed_differs(self):
        a = generate_population(_small(seed=1))
        b = generate_population(_small(seed=2))
        wa = [h.total_net_wealth for h in a.households]
        wb = [h.total_net_wealth for h in b.households]
        assert wa != wb

    def test_grossing_weight_sums_to_population(self):
        config = _small()
        pop = generate_population(config)
        total_weight = sum(h.weight for h in pop.households)
        assert total_weight == pytest.approx(config.population_households)

    def test_has_pareto_tail(self):
        config = _small(n_households=5_000)
        pop = generate_population(config)
        wealths = np.array([h.total_net_wealth for h in pop.households])
        # A heavy tail: at least some households well above the Pareto threshold,
        # and the max should dwarf the median (lognormal-only would not).
        assert (wealths >= config.pareto_threshold).sum() > 0
        assert wealths.max() > 20 * np.median(wealths)

    def test_nation_shares_approximated(self):
        config = _small(n_households=8_000)
        pop = generate_population(config)
        england = sum(1 for h in pop.households if h.nation == Nation.ENGLAND) / len(pop.households)
        # Large-sample share should land near the configured 0.84 (loose tolerance).
        assert abs(england - config.nation_shares["england"]) < 0.05

    def test_total_net_wealth_positive(self):
        pop = generate_population(_small())
        assert pop.total_net_wealth > 0

    def test_households_are_valid_engine_inputs(self):
        """Smoke test: synthetic households are consumable by a policy-family calculator."""
        from wealthlens_sim.reforms.d_iht_reform import IHTConfig, compute_household_iht

        pop = generate_population(_small(n_households=200))
        results = [compute_household_iht(h, IHTConfig()) for h in pop.households]
        assert len(results) == 200
        # Some households exceed the NRB and are liable; the call must never raise.
        assert any(r.is_liable for r in results)
