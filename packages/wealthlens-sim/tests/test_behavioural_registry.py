"""Tests for loading behavioural channels from the cited assumption registry."""

from __future__ import annotations

from datetime import date

import pytest

from wealthlens_sim.assumptions import load_assumptions
from wealthlens_sim.assumptions.schema import (
    Assumption,
    AssumptionRegistry,
    PointValue,
    RangeValue,
    ValueDistribution,
)
from wealthlens_sim.behavioural import load_behavioural_channels
from wealthlens_sim.behavioural.registry import RATE_RESPONSIVE_DOMAINS


def _mk(assumption_id: str, domain: str, vd: ValueDistribution) -> Assumption:
    """Build a minimal-but-valid Assumption (fills the registry's required fields)."""
    return Assumption(
        assumption_id=assumption_id,
        domain=domain,
        value_or_distribution=vd,
        source="test",
        transferability_score="low",
        valid_range="n/a",
        applies_to="Family A",
        last_reviewed=date(2026, 5, 23),
    )


def _registry() -> AssumptionRegistry:
    """A small registry mixing rate-elasticity ranges, a point value, and a level fraction."""
    return AssumptionRegistry(
        assumptions=[
            _mk("behaviour.migration.non_dom.v1", "migration", RangeValue(type="range", low=-0.01, central=-0.04, high=-0.10)),
            _mk("behaviour.avoidance.cgt_lock_in.v1", "avoidance", RangeValue(type="range", low=-0.3, central=-0.5, high=-0.8)),
            # A migration-domain POINT value: skipped (a rate-response channel needs a range).
            _mk("behaviour.migration.fixed.v1", "migration", PointValue(type="point", value=-0.03)),
            # A compliance-domain fraction: NOT a rate-elasticity, excluded by default domain.
            _mk("behaviour.compliance.concealment.v1", "compliance", RangeValue(type="range", low=0.02, central=0.05, high=0.15)),
        ]
    )


class TestLoadBehaviouralChannels:
    def test_loads_rate_elasticity_ranges_only(self) -> None:
        channels = load_behavioural_channels(_registry())
        names = [c.name for c in channels]
        # Both range-valued migration/avoidance channels; the point value + compliance excluded.
        assert names == ["behaviour.migration.non_dom.v1", "behaviour.avoidance.cgt_lock_in.v1"]

    def test_channels_are_sourced_from_assumption_id(self) -> None:
        channels = load_behavioural_channels(_registry())
        for c in channels:
            assert c.source_id == c.name  # provenance ties back to the cited assumption

    def test_central_point_default(self) -> None:
        channels = load_behavioural_channels(_registry())
        by_name = {c.name: c for c in channels}
        assert by_name["behaviour.migration.non_dom.v1"].semi_elasticity == pytest.approx(-0.04)

    def test_low_and_high_points(self) -> None:
        low = {c.name: c for c in load_behavioural_channels(_registry(), point="low")}
        high = {c.name: c for c in load_behavioural_channels(_registry(), point="high")}
        assert low["behaviour.migration.non_dom.v1"].semi_elasticity == pytest.approx(-0.01)
        # For a negative elasticity the registry "high" is the MORE-eroding end.
        assert high["behaviour.migration.non_dom.v1"].semi_elasticity == pytest.approx(-0.10)

    def test_compliance_excluded_by_default_but_loadable_if_requested(self) -> None:
        default = load_behavioural_channels(_registry())
        assert not any(c.name.startswith("behaviour.compliance") for c in default)
        # Explicitly requesting the domain loads it (caller's choice — but see the module
        # docstring on why concealment is a level fraction, not a rate-elasticity).
        explicit = load_behavioural_channels(_registry(), domains=("compliance",))
        assert [c.name for c in explicit] == ["behaviour.compliance.concealment.v1"]

    def test_unknown_domain_yields_empty(self) -> None:
        assert load_behavioural_channels(_registry(), domains=("does_not_exist",)) == []

    def test_invalid_point_raises_even_with_no_matching_assumptions(self) -> None:
        # Validated up-front, so an invalid point fails loudly even when nothing matches.
        with pytest.raises(ValueError, match="point must be 'low', 'central' or 'high'"):
            load_behavioural_channels(_registry(), point="invalid", domains=("does_not_exist",))  # type: ignore[arg-type]

    def test_domains_as_string_raises_type_error(self) -> None:
        # 'migration' as a bare string would iterate characters ('m','i',...) -> silently
        # empty; guard against the gotcha.
        with pytest.raises(TypeError, match="domains must be a sequence of strings"):
            load_behavioural_channels(_registry(), domains="migration")  # type: ignore[arg-type]

    def test_duplicate_domains_do_not_duplicate_channels(self) -> None:
        # A repeated/overlapping domain must NOT emit the same channel twice (that would
        # double-count its erosion via revenue_response_factor's multiplicative compose).
        once = load_behavioural_channels(_registry(), domains=("migration",))
        twice = load_behavioural_channels(_registry(), domains=("migration", "migration"))
        assert [c.name for c in once] == [c.name for c in twice]


class TestRealRegistry:
    """Integration: the committed registry's cited elasticities load into channels."""

    def test_real_registry_loads_known_channels(self) -> None:
        channels = load_behavioural_channels(load_assumptions())
        names = {c.name for c in channels}
        # The three rate-responsive elasticities cited in registries/assumptions.yml.
        assert "behaviour.migration.non_dom_stock_elasticity.v1" in names
        assert "behaviour.migration.dom_emigration_elasticity.v1" in names
        assert "behaviour.avoidance.cgt_lock_in.v1" in names
        # All are negative (base-eroding) and carry a registry source id.
        for c in channels:
            assert c.semi_elasticity <= 0.0
            assert c.source_id == c.name

    def test_real_registry_excludes_level_fractions(self) -> None:
        names = {c.name for c in load_behavioural_channels(load_assumptions())}
        # concealment + valuation discount are LEVEL fractions, not rate-elasticities.
        assert not any("concealment" in n or "valuation" in n for n in names)
        assert RATE_RESPONSIVE_DOMAINS == ("migration", "avoidance")
