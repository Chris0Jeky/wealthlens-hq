"""Tests for the v0.1 synthetic-population generator."""

from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from wealthlens_sim.schema.base import Nation
from wealthlens_sim.synth import SynthConfig, SyntheticPopulation, generate_population
from wealthlens_sim.synth.population import _generation_provenance_ids


def _small(**kw) -> SynthConfig:
    kw.setdefault("n_households", 2_000)
    kw.setdefault("seed", 7)
    return SynthConfig(**kw)


class TestSynthConfig:
    def test_defaults_valid(self):
        c = SynthConfig()
        assert c.n_households == 10_000
        assert c.population_households == 27_500_000
        assert c.median_net_wealth == 293_700
        assert c.pareto_threshold == 1_200_500
        assert Nation.NORTHERN_IRELAND.value not in c.nation_shares
        assert c.nation_shares[Nation.ENGLAND.value] == pytest.approx(23_626_000 / 27_500_000)
        assert abs(sum(c.nation_shares.values()) - 1.0) < 0.01
        assert abs(sum(c.asset_shares.values()) - 1.0) < 0.01
        assert "ons-was-wealth" in c.calibration_source_ids

    def test_defaults_match_public_ons_wealth_marginals(self):
        config = SynthConfig(n_households=10_000, seed=42)
        pop = generate_population(config)
        wealths = np.array([h.total_net_wealth for h in pop.households])
        total_wealth_gbp = pop.total_net_wealth
        top_decile_cutoff = np.quantile(wealths, 0.9)
        top_one_pct_cutoff = np.quantile(wealths, 0.99)
        sorted_wealth = np.sort(wealths)
        n = len(sorted_wealth)
        top_decile_share = sorted_wealth[-max(1, int(n * 0.1)) :].sum() / sorted_wealth.sum()
        top_one_pct_share = sorted_wealth[-max(1, int(n * 0.01)) :].sum() / sorted_wealth.sum()

        # ONS WAS April 2020-March 2022 anchors:
        # total wealth £13.568tn, median £293,700, top-decile threshold
        # £1,200,500, top-1% threshold £3,121,500, top decile holds ~41%,
        # top 1% holds 10%. This parametric synth should be close enough for
        # honest v0.1 examples, not an exact microdata reconstruction.
        assert total_wealth_gbp == pytest.approx(13_568_000_000_000, rel=0.08)
        assert np.median(wealths) == pytest.approx(293_700, rel=0.08)
        assert top_decile_cutoff == pytest.approx(1_200_500, rel=0.12)
        assert top_one_pct_cutoff == pytest.approx(3_121_500, rel=0.20)
        assert top_decile_share == pytest.approx(0.407, abs=0.05)
        assert top_one_pct_share == pytest.approx(0.10, abs=0.04)

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

    def test_weights_property_matches_household_weights(self):
        pop = generate_population(_small())
        assert pop.weights == [h.weight for h in pop.households]
        assert all(w > 0 for w in pop.weights)

    def test_provenance_ids_seam_present(self):
        config = _small()
        pop = generate_population(config)
        assert pop.provenance_ids == [*config.calibration_source_ids, *_generation_provenance_ids(config)]

    def test_provenance_ids_record_generation_parameters(self):
        config = _small(seed=13, pareto_alpha=2.25)
        pop = generate_population(config)
        assert pop.provenance_ids == _generation_provenance_ids(config)

    def test_custom_calibration_clears_default_source_provenance_ids(self):
        config = _small(median_net_wealth=500_000)
        pop = generate_population(config)
        assert pop.provenance_ids == _generation_provenance_ids(config)

    def test_custom_nation_shares_clear_default_source_provenance_ids(self):
        config = _small(nation_shares={"england": 0.5, "scotland": 0.5})
        pop = generate_population(config)
        assert pop.provenance_ids == _generation_provenance_ids(config)

    def test_custom_calibration_preserves_explicit_provenance_ids(self):
        config = _small(median_net_wealth=500_000, calibration_source_ids=("custom-calibration",))
        pop = generate_population(config)
        assert pop.provenance_ids == ["custom-calibration", *_generation_provenance_ids(config)]

    def test_asset_shares_are_normalised(self):
        # Same seed ⇒ identical drawn wealth (asset_shares don't affect the draw).
        # With normalisation, proportional shares that sum to 1.00 vs 0.99 must
        # yield identical household wealth; without it they'd differ by ~1%.
        a = generate_population(_small(asset_shares={"financial": 0.5, "main_residence": 0.5}))
        b = generate_population(_small(asset_shares={"financial": 0.495, "main_residence": 0.495}))
        assert a.households[0].total_net_wealth == pytest.approx(b.households[0].total_net_wealth)

    def test_households_are_valid_engine_inputs(self):
        """Smoke test: synthetic households are consumable by a policy-family calculator."""
        from wealthlens_sim.reforms.d_iht_reform import IHTConfig, compute_household_iht

        pop = generate_population(_small(n_households=200))
        results = [compute_household_iht(h, IHTConfig()) for h in pop.households]
        assert len(results) == 200
        # Some households exceed the NRB and are liable; the call must never raise.
        assert any(r.is_liable for r in results)
