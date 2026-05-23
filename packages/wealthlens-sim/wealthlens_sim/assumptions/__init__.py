"""Assumption registry loader.

Loads and queries the machine-readable assumption registry (registries/assumptions.yml).
Every assumption has: id, domain, value_or_distribution, source, transferability_score,
valid_range, applies_to, last_reviewed, notes.

Reference: Blueprint v5 §7.6.
"""

from wealthlens_sim.assumptions.loader import load_assumptions
from wealthlens_sim.assumptions.schema import (
    Assumption,
    AssumptionRegistry,
    FlagValue,
    PointValue,
    RangeValue,
    ScheduleValue,
    TransferabilityScore,
    ValueDistribution,
)

__all__ = [
    "Assumption",
    "AssumptionRegistry",
    "FlagValue",
    "PointValue",
    "RangeValue",
    "ScheduleValue",
    "TransferabilityScore",
    "ValueDistribution",
    "load_assumptions",
]
