"""Policy scenario and lever schemas.

Blueprint v5 §3.1: baseline status matrix.
Blueprint v5 §9: policy families A-G.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from wealthlens_sim.schema.base import Nation


class LegalStatus(str, Enum):
    CURRENT_LAW = "current_law"
    ENACTED_FUTURE = "enacted_future"
    ANNOUNCED = "announced"
    CONSULTATION_STAGE = "consultation_stage"
    HYPOTHETICAL = "hypothetical"


class PolicyFamily(str, Enum):
    A_ANNUAL_WEALTH = "A"
    B_ONE_OFF_LEVY = "B"
    C_CGT_REFORM = "C"
    D_IHT_TRANSFER = "D"
    E_PROPERTY_TAX = "E"
    F_ENFORCEMENT = "F"
    G_DEVOLUTION = "G"


class PolicyLever(BaseModel):
    """A single policy parameter that can be varied in scenarios."""

    model_config = ConfigDict(extra="forbid")

    lever_id: str
    family: PolicyFamily
    legal_status: LegalStatus
    nations: list[Nation] = Field(default_factory=lambda: [Nation.UK])
    parameters: dict[str, Any] = Field(default_factory=dict)


class PolicyScenario(BaseModel):
    """A complete set of policy levers defining one simulation run."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    label: str = Field(description="Human-readable scenario name")
    description: str = ""
    levers: list[PolicyLever] = Field(default_factory=list)
    baseline_date: date = Field(description="Baselines registry snapshot date")
