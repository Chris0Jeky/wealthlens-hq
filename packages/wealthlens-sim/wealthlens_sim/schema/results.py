"""Simulation result schemas.

Blueprint v5 §8.2: every output is a distribution.
Blueprint v5 §13.4: provenance manifest emitted with every published number.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

from wealthlens_sim.schema.base import VersionTag


class HouseholdResult(BaseModel):
    """Tax and wealth outcomes for a single household under one scenario."""

    household_id: str
    weight: Annotated[float, Field(gt=0)]
    net_wealth_pre: float = Field(description="Net wealth before policy")
    net_wealth_post: float = Field(description="Net wealth after policy")
    tax_liability: Annotated[float, Field(ge=0, default=0)]
    can_pay_from_income: bool = Field(default=True, description="Tax <= annual income")
    liquidity_constrained: bool = Field(default=False)


class SimulationResult(BaseModel):
    """Aggregate results from a single scenario run."""

    scenario_id: str
    version: VersionTag
    total_revenue_gbp: float = Field(description="Aggregate revenue raised")
    affected_households: int = Field(ge=0)
    household_results: list[HouseholdResult] = Field(default_factory=list)
    assumptions_used: list[str] = Field(default_factory=list, description="assumption_ids from registry")
    warnings: list[str] = Field(default_factory=list)
