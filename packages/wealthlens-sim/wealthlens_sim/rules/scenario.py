"""Scenario definition and execution over a household population (Wave 12 PR2).

A :class:`Scenario` selects one or more revenue-raising policy families (A--E)
with their configs; :func:`run_scenario` dispatches each to the matching
``reforms/`` aggregate calculator across a population and merges the results
into total + per-nation revenue.

Scope (see docs/WAVE12_SIMULATION_ENGINE_DESIGN.md):
- Families **A** (annual wealth tax), **B** (one-off levy), **C** (CGT),
  **D** (IHT), and **E** (HVCTS property tax) raise revenue per household and
  share the ``compute_aggregate_*(households, config)`` signature, so they
  dispatch uniformly here.
- Family **F** (enforcement) is a revenue *uplift modifier* and Family **G**
  (devolution) is a *nation-scope filter*; they compose at a different layer and
  are wired in the engine PR, not here.
- Per-**decile** attribution needs per-household revenue (not exposed by the
  aggregate API) and is also deferred to the engine PR.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, assert_never

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.reforms.a_annual_wealth import WealthTaxConfig, compute_aggregate_revenue
from wealthlens_sim.reforms.b_one_off_levy import OneOffLevyConfig, compute_aggregate_one_off_revenue
from wealthlens_sim.reforms.c_cgt_reform import CGTConfig, compute_aggregate_cgt_revenue
from wealthlens_sim.reforms.d_iht_reform import IHTConfig, compute_aggregate_iht_revenue
from wealthlens_sim.reforms.e_property_tax import HVCTSConfig, compute_aggregate_hvcts_revenue
from wealthlens_sim.schema.base import VersionTag
from wealthlens_sim.schema.household import Household

FamilyConfig = WealthTaxConfig | OneOffLevyConfig | CGTConfig | IHTConfig | HVCTSConfig


class PolicyFamily(StrEnum):
    """Revenue-raising policy families dispatchable by the scenario runner."""

    ANNUAL_WEALTH_TAX = "annual_wealth_tax"  # Family A
    ONE_OFF_LEVY = "one_off_levy"  # Family B
    CGT = "cgt"  # Family C
    IHT = "iht"  # Family D
    HVCTS = "hvcts"  # Family E


# Each family's expected config type — used to validate FamilySelection.
_FAMILY_CONFIG_TYPE: dict[PolicyFamily, type[FamilyConfig]] = {
    PolicyFamily.ANNUAL_WEALTH_TAX: WealthTaxConfig,
    PolicyFamily.ONE_OFF_LEVY: OneOffLevyConfig,
    PolicyFamily.CGT: CGTConfig,
    PolicyFamily.IHT: IHTConfig,
    PolicyFamily.HVCTS: HVCTSConfig,
}


class FamilySelection(BaseModel):
    """One policy family enabled in a scenario, with its config."""

    model_config = ConfigDict(frozen=True)

    family: PolicyFamily
    config: FamilyConfig

    @model_validator(mode="before")
    @classmethod
    def _coerce_dict_config(cls, data: Any) -> Any:
        """Coerce a *dict* config to the family-correct type before union validation.

        The five config models have overlapping fields, so pydantic's smart union
        would otherwise coerce a bare/sparse dict to whichever member appears first
        (WealthTaxConfig) regardless of ``family``. Constructing the expected type
        explicitly fixes that. Config objects are left untouched.
        """
        if isinstance(data, dict):
            family = data.get("family")
            config = data.get("config")
            if isinstance(config, dict) and family is not None:
                config_type = _FAMILY_CONFIG_TYPE[PolicyFamily(family)]
                data = {**data, "config": config_type(**config)}
        return data

    @model_validator(mode="after")
    def _config_matches_family(self) -> FamilySelection:
        expected = _FAMILY_CONFIG_TYPE[self.family]
        if not isinstance(self.config, expected):
            msg = f"family {self.family} requires a {expected.__name__}, got {type(self.config).__name__}"
            raise ValueError(msg)
        return self


class Scenario(BaseModel):
    """A named reform scenario: a set of enabled families with their configs."""

    model_config = ConfigDict(frozen=True)

    name: str
    version_tag: VersionTag
    families: list[FamilySelection] = Field(min_length=1)

    @model_validator(mode="after")
    def _no_duplicate_families(self) -> Scenario:
        seen = [s.family for s in self.families]
        if len(seen) != len(set(seen)):
            msg = "each policy family may appear at most once in a scenario"
            raise ValueError(msg)
        return self


class FamilyRevenue(BaseModel):
    """Revenue from a single family within a scenario (GBP billions)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    family: PolicyFamily
    total_revenue_bn: float
    revenue_by_nation: dict[str, float]


class ScenarioResult(BaseModel):
    """Combined revenue from running all families in a scenario."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_name: str
    family_revenues: list[FamilyRevenue]
    total_revenue_bn: float
    revenue_by_nation: dict[str, float]


def _run_family(households: list[Household], selection: FamilySelection) -> FamilyRevenue:
    """Dispatch one family to its aggregate calculator.

    The config type is guaranteed to match ``family`` by ``FamilySelection``'s
    validators; the ``isinstance`` checks narrow the union for the type-checker.
    The ``match`` with ``assert_never`` makes the dispatch exhaustive — adding a
    ``PolicyFamily`` member without a branch is a compile-time mypy error rather
    than a silent mis-dispatch.
    """
    config = selection.config
    total: float
    by_nation: dict[str, float]
    match selection.family:
        case PolicyFamily.ANNUAL_WEALTH_TAX:
            assert isinstance(config, WealthTaxConfig)
            agg = compute_aggregate_revenue(households, config)
            total, by_nation = agg.total_revenue_bn, agg.revenue_by_nation
        case PolicyFamily.ONE_OFF_LEVY:
            assert isinstance(config, OneOffLevyConfig)
            levy = compute_aggregate_one_off_revenue(households, config)
            total, by_nation = levy.total_revenue_bn, levy.revenue_by_nation
        case PolicyFamily.CGT:
            assert isinstance(config, CGTConfig)
            cgt = compute_aggregate_cgt_revenue(households, config)
            total, by_nation = cgt.total_revenue_bn, cgt.revenue_by_nation
        case PolicyFamily.IHT:
            assert isinstance(config, IHTConfig)
            iht = compute_aggregate_iht_revenue(households, config)
            total, by_nation = iht.total_revenue_bn, iht.revenue_by_nation
        case PolicyFamily.HVCTS:
            assert isinstance(config, HVCTSConfig)
            hvcts = compute_aggregate_hvcts_revenue(households, config)
            total, by_nation = hvcts.total_revenue_bn, hvcts.revenue_by_nation
        case _:  # pragma: no cover - exhaustiveness guard
            assert_never(selection.family)
    return FamilyRevenue(family=selection.family, total_revenue_bn=total, revenue_by_nation=by_nation)


def run_scenario(households: list[Household], scenario: Scenario) -> ScenarioResult:
    """Run every family in ``scenario`` over ``households`` and merge the revenue.

    Returns total revenue (GBP bn) and revenue merged by constituent nation,
    plus the per-family breakdown. Families are independent and additive in v0.1
    (no behavioural interaction between families — a documented simplification).
    """
    family_revenues: list[FamilyRevenue] = []
    merged_by_nation: dict[str, float] = {}
    total = 0.0

    for selection in scenario.families:
        fr = _run_family(households, selection)
        family_revenues.append(fr)
        total += fr.total_revenue_bn
        for nation, revenue in fr.revenue_by_nation.items():
            merged_by_nation[nation] = merged_by_nation.get(nation, 0.0) + revenue

    return ScenarioResult(
        scenario_name=scenario.name,
        family_revenues=family_revenues,
        total_revenue_bn=total,
        revenue_by_nation=merged_by_nation,
    )
