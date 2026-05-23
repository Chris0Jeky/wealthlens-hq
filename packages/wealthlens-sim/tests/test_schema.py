"""Tests for the schema module."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wealthlens_sim.schema import (
    Asset,
    AssetType,
    Household,
    HouseholdResult,
    LegalStatus,
    Nation,
    Person,
    PolicyLever,
    PolicyScenario,
    SimulationResult,
    VersionTag,
)
from wealthlens_sim.schema.policy import PolicyFamily


class TestNation:
    def test_all_four_nations(self):
        assert len(Nation) == 5
        assert Nation.UK in Nation

    def test_string_value(self):
        assert Nation.ENGLAND.value == "england"


class TestAsset:
    def test_net_value(self):
        a = Asset(asset_type=AssetType.MAIN_RESIDENCE, gross_value=500_000, debt=200_000)
        assert a.net_value == 300_000

    def test_liquid_default_false(self):
        a = Asset(asset_type=AssetType.FINANCIAL, gross_value=10_000)
        assert not a.is_liquid

    def test_debt_must_be_non_negative(self):
        with pytest.raises(ValidationError):
            Asset(asset_type=AssetType.FINANCIAL, gross_value=10_000, debt=-1)


class TestPerson:
    def test_total_net_wealth(self):
        p = Person(
            person_id="p1",
            age=45,
            assets=[
                Asset(asset_type=AssetType.MAIN_RESIDENCE, gross_value=500_000, debt=200_000),
                Asset(asset_type=AssetType.FINANCIAL, gross_value=50_000, is_liquid=True),
            ],
        )
        assert p.total_net_wealth == 350_000

    def test_total_liquid_wealth(self):
        p = Person(
            person_id="p1",
            age=45,
            assets=[
                Asset(asset_type=AssetType.MAIN_RESIDENCE, gross_value=500_000),
                Asset(asset_type=AssetType.FINANCIAL, gross_value=50_000, is_liquid=True),
            ],
        )
        assert p.total_liquid_wealth == 50_000

    def test_fig_regime_max_4(self):
        with pytest.raises(ValidationError):
            Person(person_id="p1", age=30, fig_regime_years_remaining=5)


class TestHousehold:
    def test_requires_at_least_one_person(self):
        with pytest.raises(ValidationError):
            Household(household_id="h1", nation=Nation.ENGLAND, weight=1.0, persons=[])

    def test_total_net_wealth(self):
        h = Household(
            household_id="h1",
            nation=Nation.SCOTLAND,
            weight=150.0,
            persons=[
                Person(
                    person_id="p1",
                    age=40,
                    assets=[Asset(asset_type=AssetType.FINANCIAL, gross_value=100_000)],
                ),
                Person(
                    person_id="p2",
                    age=38,
                    assets=[Asset(asset_type=AssetType.FINANCIAL, gross_value=50_000)],
                ),
            ],
        )
        assert h.total_net_wealth == 150_000

    def test_nation_is_first_class(self):
        h = Household(
            household_id="h1",
            nation=Nation.WALES,
            weight=1.0,
            persons=[Person(person_id="p1", age=30)],
        )
        assert h.nation == Nation.WALES


class TestPolicyScenario:
    def test_basic_scenario(self):
        s = PolicyScenario(
            scenario_id="wealth-tax-1pct",
            label="1% wealth tax above £10m",
            baseline_date="2026-05-21",
            levers=[
                PolicyLever(
                    lever_id="wt-threshold",
                    family=PolicyFamily.A_ANNUAL_WEALTH,
                    legal_status=LegalStatus.HYPOTHETICAL,
                    parameters={"threshold": 10_000_000, "rate": 0.01},
                ),
            ],
        )
        assert len(s.levers) == 1
        assert s.levers[0].family == PolicyFamily.A_ANNUAL_WEALTH


class TestSimulationResult:
    def test_round_trip(self):
        v = VersionTag(
            macro_baseline_version="NBS-2025",
            policy_version="2026-05-21",
            population_version="FRS-2024-25",
            wealthlens_sim_version="0.1.0.dev0",
        )
        r = SimulationResult(
            scenario_id="test",
            version=v,
            total_revenue_gbp=5.2e9,
            affected_households=85_000,
            household_results=[
                HouseholdResult(
                    household_id="h1",
                    weight=150.0,
                    net_wealth_pre=12_000_000,
                    net_wealth_post=11_880_000,
                    tax_liability=120_000,
                ),
            ],
            assumptions_used=["toptail.pareto_alpha.overall.v1"],
        )
        data = r.model_dump()
        r2 = SimulationResult.model_validate(data)
        assert r2.total_revenue_gbp == 5.2e9
        assert len(r2.household_results) == 1
