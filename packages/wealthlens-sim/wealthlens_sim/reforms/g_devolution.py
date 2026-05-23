"""Family G: Devolution-asymmetric reform — nation-scope routing.

Blueprint v5 §9 Family G and §4.3-4.4: devolution as a policy family.
England-only HVCTS vs GB/UK equivalents, Scottish council-tax
revaluation, Welsh property-tax reforms, NI domestic-rates adjustment,
nation-specific property-tax offsets.

This module provides the composition layer that allows any reform
family (A-F) to be applied differentially by devolved geography.
The v0.1 model filters households by nation scope so the upstream
reform compute functions can run on the included subset.

The core insight: HVCTS is England-only, but the question "what if
we extended it to Scotland?" is a Family G scenario, not a Family E
parameter — it changes the territorial scope, not the tax structure.

Current-law property-tax baselines by nation:
- England: council tax (1991 bands)
- Scotland: council tax (1991 bands, separate multipliers)
- Wales: council tax (2003 bands, revalued)
- Northern Ireland: domestic rates (capital value, 2005 revaluation)

Sources:
    Blueprint v5 §4.3: recommended devolution treatment.
    Blueprint v5 §9, Family G: devolution-asymmetric reform definition.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.schema.base import Nation
from wealthlens_sim.schema.household import Household

CONSTITUENT_NATIONS: frozenset[Nation] = frozenset({
    Nation.ENGLAND,
    Nation.SCOTLAND,
    Nation.WALES,
    Nation.NORTHERN_IRELAND,
})

GREAT_BRITAIN_NATIONS: frozenset[Nation] = frozenset({
    Nation.ENGLAND,
    Nation.SCOTLAND,
    Nation.WALES,
})


class NationScope(StrEnum):
    """Territorial scope for a devolution-asymmetric reform."""

    ENGLAND_ONLY = "england_only"
    GREAT_BRITAIN = "great_britain"
    UK_WIDE = "uk_wide"
    CUSTOM = "custom"


_SCOPE_TO_NATIONS: dict[NationScope, frozenset[Nation]] = {
    NationScope.ENGLAND_ONLY: frozenset({Nation.ENGLAND}),
    NationScope.GREAT_BRITAIN: GREAT_BRITAIN_NATIONS,
    NationScope.UK_WIDE: CONSTITUENT_NATIONS,
}


class DevolutionConfig(BaseModel):
    """Configuration for devolution-asymmetric reform scoping.

    Defines which nations are included in or excluded from a reform.
    For CUSTOM scope, provide explicit included_nations.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    scope: NationScope = Field(
        description="Territorial scope preset or CUSTOM for explicit nation list",
    )
    included_nations: frozenset[Nation] | None = Field(
        default=None,
        description="Explicit nation set (required for CUSTOM scope, ignored otherwise)",
    )

    @model_validator(mode="after")
    def _validate_scope(self) -> DevolutionConfig:
        if self.scope == NationScope.CUSTOM:
            if self.included_nations is None or len(self.included_nations) == 0:
                msg = "included_nations must be provided and non-empty for CUSTOM scope"
                raise ValueError(msg)
            non_constituent = self.included_nations - CONSTITUENT_NATIONS
            if non_constituent:
                msg = f"included_nations must be constituent nations, got: {non_constituent}"
                raise ValueError(msg)
        return self

    def get_included_nations(self) -> frozenset[Nation]:
        """Return the set of nations included in this scope."""
        if self.scope == NationScope.CUSTOM:
            assert self.included_nations is not None
            return self.included_nations
        return _SCOPE_TO_NATIONS[self.scope]


class DevolutionSplit(BaseModel):
    """Result of splitting a population by nation scope."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scope: NationScope
    included_nations: tuple[str, ...]
    excluded_nations: tuple[str, ...]
    included_count: int = Field(ge=0, description="Unweighted count of included households")
    excluded_count: int = Field(ge=0, description="Unweighted count of excluded households")
    included_weight: float = Field(ge=0, description="Weighted count of included households")
    excluded_weight: float = Field(ge=0, description="Weighted count of excluded households")
    included_weight_fraction: float = Field(
        ge=0, le=1,
        description="Fraction of total population weight in included nations",
    )


def split_households_by_scope(
    households: list[Household],
    config: DevolutionConfig,
) -> tuple[list[Household], list[Household], DevolutionSplit]:
    """Split households into included and excluded based on nation scope.

    Returns (included, excluded, split_summary).
    """
    included_nations = config.get_included_nations()
    excluded_nations = CONSTITUENT_NATIONS - included_nations

    included: list[Household] = []
    excluded: list[Household] = []
    included_weight = 0.0
    excluded_weight = 0.0

    for hh in households:
        if hh.nation in included_nations:
            included.append(hh)
            included_weight += hh.weight
        else:
            excluded.append(hh)
            excluded_weight += hh.weight

    total_weight = included_weight + excluded_weight
    fraction = included_weight / total_weight if total_weight > 0 else 0.0

    split = DevolutionSplit(
        scope=config.scope,
        included_nations=tuple(sorted(n.value for n in included_nations)),
        excluded_nations=tuple(sorted(n.value for n in excluded_nations)),
        included_count=len(included),
        excluded_count=len(excluded),
        included_weight=included_weight,
        excluded_weight=excluded_weight,
        included_weight_fraction=fraction,
    )
    return included, excluded, split
