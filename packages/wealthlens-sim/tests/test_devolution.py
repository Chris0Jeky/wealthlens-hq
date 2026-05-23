"""Tests for Family G devolution-asymmetric reform module."""

from __future__ import annotations

import pytest
from _helpers import make_household, make_person
from pydantic import ValidationError

from wealthlens_sim.reforms.g_devolution import (
    CONSTITUENT_NATIONS,
    GREAT_BRITAIN_NATIONS,
    DevolutionConfig,
    DevolutionSplit,
    NationScope,
    split_households_by_scope,
)
from wealthlens_sim.schema.base import Nation
from wealthlens_sim.schema.household import AssetType


class TestNationScope:
    def test_all_values(self):
        assert NationScope.ENGLAND_ONLY == "england_only"
        assert NationScope.GREAT_BRITAIN == "great_britain"
        assert NationScope.UK_WIDE == "uk_wide"
        assert NationScope.CUSTOM == "custom"

    def test_is_str(self):
        assert isinstance(NationScope.ENGLAND_ONLY, str)


class TestDevolutionConfig:
    def test_england_only(self):
        config = DevolutionConfig(scope=NationScope.ENGLAND_ONLY)
        assert config.get_included_nations() == frozenset({Nation.ENGLAND})

    def test_great_britain(self):
        config = DevolutionConfig(scope=NationScope.GREAT_BRITAIN)
        assert config.get_included_nations() == GREAT_BRITAIN_NATIONS

    def test_uk_wide(self):
        config = DevolutionConfig(scope=NationScope.UK_WIDE)
        assert config.get_included_nations() == CONSTITUENT_NATIONS

    def test_custom_valid(self):
        config = DevolutionConfig(
            scope=NationScope.CUSTOM,
            included_nations=frozenset({Nation.SCOTLAND, Nation.WALES}),
        )
        assert config.get_included_nations() == frozenset({Nation.SCOTLAND, Nation.WALES})

    def test_custom_requires_nations(self):
        with pytest.raises(ValidationError, match="must be provided"):
            DevolutionConfig(scope=NationScope.CUSTOM)

    def test_custom_empty_rejected(self):
        with pytest.raises(ValidationError, match="must be provided"):
            DevolutionConfig(
                scope=NationScope.CUSTOM,
                included_nations=frozenset(),
            )

    def test_custom_rejects_uk_aggregate(self):
        with pytest.raises(ValidationError, match="constituent nations"):
            DevolutionConfig(
                scope=NationScope.CUSTOM,
                included_nations=frozenset({Nation.UK}),
            )

    def test_frozen(self):
        config = DevolutionConfig(scope=NationScope.ENGLAND_ONLY)
        with pytest.raises(ValidationError, match="frozen"):
            config.scope = NationScope.UK_WIDE

    def test_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            DevolutionConfig(scope=NationScope.ENGLAND_ONLY, surprise="bad")

    def test_preset_ignores_included_nations(self):
        config = DevolutionConfig(
            scope=NationScope.ENGLAND_ONLY,
            included_nations=frozenset({Nation.SCOTLAND}),
        )
        assert config.get_included_nations() == frozenset({Nation.ENGLAND})

    def test_custom_single_nation(self):
        config = DevolutionConfig(
            scope=NationScope.CUSTOM,
            included_nations=frozenset({Nation.NORTHERN_IRELAND}),
        )
        assert config.get_included_nations() == frozenset({Nation.NORTHERN_IRELAND})


class TestSplitHouseholdsByScope:
    def _make_population(self) -> list:
        eng = make_household(
            [make_person("p1", assets=[(AssetType.FINANCIAL, 500_000, 0)])],
            nation=Nation.ENGLAND, weight=10_000, household_id="hh_eng",
        )
        sco = make_household(
            [make_person("p2", assets=[(AssetType.FINANCIAL, 300_000, 0)])],
            nation=Nation.SCOTLAND, weight=5_000, household_id="hh_sco",
        )
        wal = make_household(
            [make_person("p3", assets=[(AssetType.FINANCIAL, 200_000, 0)])],
            nation=Nation.WALES, weight=3_000, household_id="hh_wal",
        )
        ni = make_household(
            [make_person("p4", assets=[(AssetType.FINANCIAL, 100_000, 0)])],
            nation=Nation.NORTHERN_IRELAND, weight=2_000, household_id="hh_ni",
        )
        return [eng, sco, wal, ni]

    def test_england_only(self):
        config = DevolutionConfig(scope=NationScope.ENGLAND_ONLY)
        inc, exc, split = split_households_by_scope(self._make_population(), config)
        assert len(inc) == 1
        assert len(exc) == 3
        assert inc[0].nation == Nation.ENGLAND
        assert split.included_weight == 10_000
        assert split.excluded_weight == 10_000

    def test_great_britain(self):
        config = DevolutionConfig(scope=NationScope.GREAT_BRITAIN)
        inc, exc, split = split_households_by_scope(self._make_population(), config)
        assert len(inc) == 3
        assert len(exc) == 1
        assert exc[0].nation == Nation.NORTHERN_IRELAND
        assert split.included_weight == 18_000
        assert split.excluded_weight == 2_000

    def test_uk_wide(self):
        config = DevolutionConfig(scope=NationScope.UK_WIDE)
        inc, exc, split = split_households_by_scope(self._make_population(), config)
        assert len(inc) == 4
        assert len(exc) == 0
        assert split.included_weight_fraction == pytest.approx(1.0)

    def test_custom_scope(self):
        config = DevolutionConfig(
            scope=NationScope.CUSTOM,
            included_nations=frozenset({Nation.SCOTLAND, Nation.WALES}),
        )
        inc, _exc, split = split_households_by_scope(self._make_population(), config)
        assert len(inc) == 2
        assert {hh.nation for hh in inc} == {Nation.SCOTLAND, Nation.WALES}
        assert split.included_weight == 8_000

    def test_empty_population(self):
        config = DevolutionConfig(scope=NationScope.ENGLAND_ONLY)
        inc, exc, split = split_households_by_scope([], config)
        assert len(inc) == 0
        assert len(exc) == 0
        assert split.included_weight_fraction == 0.0

    def test_no_matching_nation(self):
        sco = make_household(
            [make_person("p1", assets=[(AssetType.FINANCIAL, 100_000, 0)])],
            nation=Nation.SCOTLAND, weight=5_000, household_id="hh_sco",
        )
        config = DevolutionConfig(scope=NationScope.ENGLAND_ONLY)
        inc, exc, split = split_households_by_scope([sco], config)
        assert len(inc) == 0
        assert len(exc) == 1
        assert split.included_weight_fraction == 0.0

    def test_weight_fraction(self):
        config = DevolutionConfig(scope=NationScope.ENGLAND_ONLY)
        _, _, split = split_households_by_scope(self._make_population(), config)
        assert split.included_weight_fraction == pytest.approx(10_000 / 20_000)

    def test_split_nations_sorted(self):
        config = DevolutionConfig(scope=NationScope.GREAT_BRITAIN)
        _, _, split = split_households_by_scope(self._make_population(), config)
        assert split.included_nations == ("england", "scotland", "wales")
        assert split.excluded_nations == ("northern_ireland",)

    def test_split_scope_preserved(self):
        config = DevolutionConfig(scope=NationScope.ENGLAND_ONLY)
        _, _, split = split_households_by_scope(self._make_population(), config)
        assert split.scope == NationScope.ENGLAND_ONLY

    def test_multiple_households_same_nation(self):
        eng1 = make_household(
            [make_person("p1", assets=[(AssetType.FINANCIAL, 500_000, 0)])],
            nation=Nation.ENGLAND, weight=5_000, household_id="hh_eng1",
        )
        eng2 = make_household(
            [make_person("p2", assets=[(AssetType.FINANCIAL, 200_000, 0)])],
            nation=Nation.ENGLAND, weight=3_000, household_id="hh_eng2",
        )
        sco = make_household(
            [make_person("p3", assets=[(AssetType.FINANCIAL, 100_000, 0)])],
            nation=Nation.SCOTLAND, weight=2_000, household_id="hh_sco",
        )
        config = DevolutionConfig(scope=NationScope.ENGLAND_ONLY)
        inc, _exc, split = split_households_by_scope([eng1, eng2, sco], config)
        assert len(inc) == 2
        assert split.included_weight == 8_000
        assert split.included_count == 2


class TestDevolutionSplit:
    def test_round_trip(self):
        split = DevolutionSplit(
            scope=NationScope.ENGLAND_ONLY,
            included_nations=("england",),
            excluded_nations=("northern_ireland", "scotland", "wales"),
            included_count=1,
            excluded_count=3,
            included_weight=10_000,
            excluded_weight=10_000,
            included_weight_fraction=0.5,
        )
        data = split.model_dump()
        r2 = DevolutionSplit.model_validate(data)
        assert r2.scope == NationScope.ENGLAND_ONLY
        assert r2.included_weight_fraction == 0.5

    def test_frozen(self):
        split = DevolutionSplit(
            scope=NationScope.UK_WIDE,
            included_nations=("england", "northern_ireland", "scotland", "wales"),
            excluded_nations=(),
            included_count=4,
            excluded_count=0,
            included_weight=20_000,
            excluded_weight=0,
            included_weight_fraction=1.0,
        )
        with pytest.raises(ValidationError, match="frozen"):
            split.included_weight = 0.0


class TestConstants:
    def test_constituent_nations(self):
        assert len(CONSTITUENT_NATIONS) == 4
        assert Nation.UK not in CONSTITUENT_NATIONS

    def test_great_britain_nations(self):
        assert len(GREAT_BRITAIN_NATIONS) == 3
        assert Nation.NORTHERN_IRELAND not in GREAT_BRITAIN_NATIONS
        assert GREAT_BRITAIN_NATIONS < CONSTITUENT_NATIONS
