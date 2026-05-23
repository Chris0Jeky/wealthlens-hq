"""Pydantic schema for the baselines registry (registries/baselines.yml).

Reference: Blueprint v5 section 3.1.
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class BaselineStatus(str, Enum):
    """Legal status of a baseline policy lever."""

    current_law = "current_law"
    enacted_future = "enacted_future"
    announced = "announced"
    consultation_stage = "consultation_stage"
    hypothetical = "hypothetical"


class BaselineEntry(BaseModel):
    """A single policy-lever entry in the baselines registry."""

    id: str = Field(description="Unique kebab-case identifier for the baseline entry")
    area: str = Field(description="Policy area (e.g. Capital Gains Tax, Inheritance Tax)")
    status: BaselineStatus = Field(description="Legal status of the policy lever")
    effective_date: date | None = Field(
        default=None,
        description=(
            "Date policy takes effect, or snapshot date for ongoing-practice"
            " entries; null for hypothetical"
        ),
    )
    description: str = Field(description="Human-readable description of the policy lever")
    wealthlens_treatment: str = Field(
        description="How WealthLens models this lever (e.g. current-law baseline)"
    )
    source_url: str | None = Field(
        default=None,
        description="Authoritative source URL; null for hypothetical entries",
    )
    notes: str | None = Field(default=None, description="Additional notes or caveats")


class BaselinesRegistry(BaseModel):
    """Top-level schema for registries/baselines.yml."""

    modelling_date: date = Field(
        description="Snapshot date for all status assessments in this file"
    )
    baselines: list[BaselineEntry] = Field(
        description="List of baseline policy-lever entries"
    )
