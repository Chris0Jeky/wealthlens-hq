"""Pydantic models for the assumption registry YAML schema.

Blueprint v5 §7.6: every modelling assumption carries id, domain,
value_or_distribution, source, transferability_score, valid_range,
applies_to, last_reviewed, notes.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.schema.policy import LegalStatus


class TransferabilityScore(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    STRESS_TEST_ONLY = "stress-test-only"


class PointValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["point"]
    value: float | int


class RangeValue(BaseModel):
    """Supports both positive ranges (low <= high) and negative elasticities (low >= high)."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["range"]
    low: float | int
    central: float | int
    high: float | int

    @model_validator(mode="after")
    def _monotonic_ordering(self) -> RangeValue:
        ascending = self.low <= self.central <= self.high
        descending = self.low >= self.central >= self.high
        if not (ascending or descending):
            msg = f"Must be monotonically ordered, got {self.low}, {self.central}, {self.high}"
            raise ValueError(msg)
        return self


class ScheduleValue(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: Literal["schedule"]

    @model_validator(mode="after")
    def _not_empty(self) -> ScheduleValue:
        if not self.model_extra:
            msg = "Schedule must contain at least one rate/band field"
            raise ValueError(msg)
        return self


class FlagValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["flag"]
    value: int = Field(ge=0, le=1)


ValueDistribution = Annotated[
    PointValue | RangeValue | ScheduleValue | FlagValue,
    Field(discriminator="type"),
]


class Assumption(BaseModel):
    """A single modelling assumption from the registry."""

    model_config = ConfigDict(extra="forbid")

    assumption_id: str = Field(pattern=r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+\.v[1-9]\d*$")
    domain: str
    legal_status: LegalStatus | None = None
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

    @model_validator(mode="after")
    def _unique_ids(self) -> AssumptionRegistry:
        seen: set[str] = set()
        for a in self.assumptions:
            if a.assumption_id in seen:
                msg = f"Duplicate assumption_id: {a.assumption_id}"
                raise ValueError(msg)
            seen.add(a.assumption_id)
        return self

    def get(self, assumption_id: str) -> Assumption | None:
        for a in self.assumptions:
            if a.assumption_id == assumption_id:
                return a
        return None

    def by_domain(self, domain: str) -> list[Assumption]:
        return [a for a in self.assumptions if a.domain == domain]

    def by_transferability(self, score: TransferabilityScore) -> list[Assumption]:
        return [a for a in self.assumptions if a.transferability_score == score]
