"""Tests for the schema module."""

from __future__ import annotations

from datetime import date

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
    PolicyFamily,
    PolicyLever,
    PolicyScenario,
    SimulationResult,
    VersionTag,
)


class TestNation:
    def test_all_nations(self):
        assert len(Nation) == 5
        assert Nation.UK in Nation

    def test_constituent_nations(self):
        constituents = {Nation.ENGLAND, Nation.SCOTLAND, Nation.WALES, Nation.NORTHERN_IRELAND}
        assert len(constituents) == 4

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

    def test_gross_value_must_be_non_negative(self):
        with pytest.raises(ValidationError):
            Asset(asset_type=AssetType.FINANCIAL, gross_value=-1)

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            Asset(asset_type=AssetType.FINANCIAL, gross_value=10_000, surprise=42)


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

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            Person(person_id="p1", age=30, unknown_field="x")


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

    def test_uk_nation_rejected(self):
        with pytest.raises(ValidationError, match="constituent nation"):
            Household(
                household_id="h1",
                nation=Nation.UK,
                weight=1.0,
                persons=[Person(person_id="p1", age=30)],
            )


class TestPolicyLever:
    def test_default_nations_is_uk(self):
        lever = PolicyLever(
            lever_id="test",
            family=PolicyFamily.A_ANNUAL_WEALTH,
            legal_status=LegalStatus.CURRENT_LAW,
        )
        assert lever.nations == [Nation.UK]

    def test_invalid_family_rejected(self):
        with pytest.raises(ValidationError):
            PolicyLever(
                lever_id="test",
                family="Z",
                legal_status=LegalStatus.CURRENT_LAW,
            )

    def test_custom_nations(self):
        lever = PolicyLever(
            lever_id="hvcts",
            family=PolicyFamily.E_PROPERTY_TAX,
            legal_status=LegalStatus.CONSULTATION_STAGE,
            nations=[Nation.ENGLAND],
        )
        assert lever.nations == [Nation.ENGLAND]

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            PolicyLever(
                lever_id="test",
                family=PolicyFamily.A_ANNUAL_WEALTH,
                legal_status=LegalStatus.CURRENT_LAW,
                typo_field=True,
            )


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
        assert s.baseline_date == date(2026, 5, 21)

    def test_empty_levers_valid(self):
        s = PolicyScenario(
            scenario_id="baseline",
            label="No policy changes",
            baseline_date="2026-05-21",
        )
        assert len(s.levers) == 0

    def test_invalid_date_rejected(self):
        with pytest.raises(ValidationError):
            PolicyScenario(
                scenario_id="test",
                label="Test",
                baseline_date="last tuesday",
            )


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
                    nation=Nation.ENGLAND,
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
        assert r2.household_results[0].nation == Nation.ENGLAND

    def test_version_tag_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            VersionTag(
                macro_baseline_version="NBS-2025",
                policy_version="2026-05-21",
                population_version="FRS-2024-25",
                wealthlens_sim_version="0.1.0.dev0",
                unknown="bad",
            )

    def test_version_tag_new_fields(self):
        v = VersionTag(
            macro_baseline_version="NBS-2025",
            policy_version="2026-05-21",
            population_version="FRS-2024-25",
            wealthlens_sim_version="0.1.0.dev0",
            consultation_state="hvcts_consultation_open",
            fiscal_event_anchor="autumn_statement_2025",
        )
        assert v.consultation_state == "hvcts_consultation_open"
        assert v.fiscal_event_anchor == "autumn_statement_2025"

    def test_household_result_defaults(self):
        hr = HouseholdResult(
            household_id="h1",
            nation=Nation.SCOTLAND,
            weight=100.0,
            net_wealth_pre=1_000_000,
            net_wealth_post=990_000,
        )
        assert hr.tax_liability == 0
        assert hr.can_pay_from_income is True
        assert hr.liquidity_constrained is False
