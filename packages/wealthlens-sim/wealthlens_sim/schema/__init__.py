"""Pydantic schemas for policy parameters, household records, and simulation outputs.

Reference: Blueprint v5 §8.2, §13.6: schema layer.
Nation is a first-class field on every household and policy record.
"""

from wealthlens_sim.schema.base import Nation, VersionTag
from wealthlens_sim.schema.household import Asset, AssetType, Household, Person
from wealthlens_sim.schema.policy import LegalStatus, PolicyLever, PolicyScenario
from wealthlens_sim.schema.results import HouseholdResult, SimulationResult

__all__ = [
    "Asset",
    "AssetType",
    "Household",
    "HouseholdResult",
    "LegalStatus",
    "Nation",
    "Person",
    "PolicyLever",
    "PolicyScenario",
    "SimulationResult",
    "VersionTag",
]
