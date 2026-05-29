"""Rules-as-code layer: translates policy parameters into household-level tax liabilities.

Each policy family (A-G) provides a reform module in reforms/; this package
provides the shared execution framework and parameter validation. v0.1 (Wave 12
PR2) adds :func:`run_scenario`, which runs a :class:`Scenario` (a set of enabled
revenue-raising families A-E with their configs) over a household population and
returns merged total + per-nation revenue.

Reference: Blueprint v5 section 9.
"""

from wealthlens_sim.rules.scenario import (
    FamilyRevenue,
    FamilySelection,
    PolicyFamily,
    Scenario,
    ScenarioResult,
    run_scenario,
)

__all__ = [
    "FamilyRevenue",
    "FamilySelection",
    "PolicyFamily",
    "Scenario",
    "ScenarioResult",
    "run_scenario",
]
