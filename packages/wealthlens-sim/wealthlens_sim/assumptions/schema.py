"""Pydantic models for the assumption registry YAML schema.

Blueprint v5 §7.6: every modelling assumption carries id, domain,
value_or_distribution, source, transferability_score, valid_range,
applies_to, last_reviewed, notes.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TransferabilityScore(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    STRESS_TEST_ONLY = "stress-test-only"


class PointValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["point"]
    value: float | int


class RangeValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["range"]
    low: float | int
    central: float | int
    high: float | int

    @model_validator(mode="after")
    def _low_le_central_le_high(self) -> RangeValue:
        if not (self.low <= self.central <= self.high):
            msg = f"Must satisfy low <= central <= high, got {self.low}, {self.central}, {self.high}"
            raise ValueError(msg)
        return self


class ScheduleValue(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: Literal["schedule"]


class FlagValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["flag"]
    value: int = Field(ge=0, le=1)


ValueDistribution = Annotated[
    Union[PointValue, RangeValue, ScheduleValue, FlagValue],
    Field(discriminator="type"),
]


class Assumption(BaseModel):
    """A single modelling assumption from the registry."""

    model_config = ConfigDict(extra="forbid")

    assumption_id: str = Field(pattern=r"^[a-z][a-z0-9_.]+\.v\d+$")
    domain: str
    legal_status: str | None = None
    value_or_distribution: ValueDistribution
    source: str
    transferability_score: TransferabilityScore
    valid_range: str
    applies_to: str
    last_reviewed: date
    notes: str = ""


class AssumptionRegistry(BaseModel):
    """Top-level container for the assumptions YAML file."""

    model_config = ConfigDict(extra="forbid")

    assumptions: list[Assumption] = Field(default_factory=list)

    def get(self, assumption_id: str) -> Assumption | None:
        for a in self.assumptions:
            if a.assumption_id == assumption_id:
                return a
        return None

    def by_domain(self, domain: str) -> list[Assumption]:
        return [a for a in self.assumptions if a.domain == domain]

    def by_transferability(self, score: TransferabilityScore) -> list[Assumption]:
        return [a for a in self.assumptions if a.transferability_score == score]
