"""Household, person, and asset schemas.

Blueprint v5 §8.2: nation is a first-class field on every household.
Blueprint v5 §7.1-7.2: FRS as tax-benefit spine, WAS wealth imputed.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from wealthlens_sim.schema.base import Nation


class AssetType(str, Enum):
    MAIN_RESIDENCE = "main_residence"
    OTHER_PROPERTY = "other_property"
    FINANCIAL = "financial"
    PHYSICAL = "physical"
    PRIVATE_BUSINESS = "private_business"
    DB_PENSION = "db_pension"
    DC_PENSION = "dc_pension"
    STATE_PENSION = "state_pension"


class Asset(BaseModel):
    """A single wealth component held by a person or household."""

    asset_type: AssetType
    gross_value: Annotated[float, Field(description="Gross value in GBP")]
    debt: Annotated[float, Field(ge=0, default=0, description="Debt secured against this asset")]
    is_liquid: bool = Field(default=False, description="Can be realised within 30 days without significant loss")

    @property
    def net_value(self) -> float:
        return self.gross_value - self.debt


class Person(BaseModel):
    """An individual within a household."""

    person_id: str
    age: Annotated[int, Field(ge=0, le=120)]
    is_uk_resident: bool = True
    fig_regime_years_remaining: Annotated[int, Field(ge=0, le=4, default=0)]
    annual_income: Annotated[float, Field(ge=0, default=0)]
    capital_gains_realised: Annotated[float, Field(ge=0, default=0)]
    assets: list[Asset] = Field(default_factory=list)

    @property
    def total_net_wealth(self) -> float:
        return sum(a.net_value for a in self.assets)

    @property
    def total_liquid_wealth(self) -> float:
        return sum(a.net_value for a in self.assets if a.is_liquid)


class Household(BaseModel):
    """A household unit — the primary simulation entity.

    Blueprint v5 §8.2: nation is first-class, not derived.
    """

    household_id: str
    nation: Nation
    region: str = Field(default="", description="Sub-national region, e.g. ITL1 code")
    weight: Annotated[float, Field(gt=0, description="Survey grossing weight")]
    persons: list[Person] = Field(min_length=1)

    @property
    def total_net_wealth(self) -> float:
        return sum(p.total_net_wealth for p in self.persons)

    @property
    def total_income(self) -> float:
        return sum(p.annual_income for p in self.persons)
