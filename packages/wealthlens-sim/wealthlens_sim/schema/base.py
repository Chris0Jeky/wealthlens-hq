"""Shared base types used across all schema modules."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Nation(StrEnum):
    ENGLAND = "england"
    SCOTLAND = "scotland"
    WALES = "wales"
    NORTHERN_IRELAND = "northern_ireland"
    UK = "uk"


class VersionTag(BaseModel):
    """Tags every simulation output for reproducibility.

    Blueprint v5 §13.3: five versioning dimensions.
    """

    model_config = ConfigDict(extra="forbid")

    macro_baseline_version: str = Field(description="ONS National Balance Sheet vintage, e.g. 'NBS-2025'")
    policy_version: str = Field(description="Baselines registry snapshot date, e.g. '2026-05-21'")
    population_version: str = Field(description="FRS/WAS survey wave, e.g. 'FRS-2024-25'")
    wealthlens_sim_version: str = Field(description="Package version at run time")
    consultation_state: str = Field(default="", description="e.g. 'hvcts_consultation_open'")
    fiscal_event_anchor: str = Field(default="", description="e.g. 'autumn_statement_2025'")
