"""Pydantic models for the baselines registry YAML schema.

Blueprint v5 §3.1: baseline status matrix — every policy lever tagged
by legal status as of the modelling date.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.schema.policy import LegalStatus


class PolicyBaseline(BaseModel):
    """A single policy baseline entry from the status matrix."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9-]+$")
    area: str
    status: LegalStatus
    effective_date: date | None = None
    description: str
    wealthlens_treatment: str
    source_url: str | None = None
    notes: str = ""


class BaselinesRegistry(BaseModel):
    """Top-level container for the baselines YAML file."""

    model_config = ConfigDict(extra="forbid")

    modelling_date: date
    baselines: list[PolicyBaseline] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_ids(self) -> BaselinesRegistry:
        seen: set[str] = set()
        for b in self.baselines:
            if b.id in seen:
                msg = f"Duplicate baseline id: {b.id}"
                raise ValueError(msg)
            seen.add(b.id)
        return self

    def get(self, baseline_id: str) -> PolicyBaseline | None:
        for b in self.baselines:
            if b.id == baseline_id:
                return b
        return None

    def by_status(self, status: LegalStatus) -> list[PolicyBaseline]:
        return [b for b in self.baselines if b.status == status]

    def by_area(self, area: str) -> list[PolicyBaseline]:
        return [b for b in self.baselines if b.area == area]
