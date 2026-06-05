"""Behavioural-response modelling for revenue estimation (Wave 13+).

Turns cited semi-elasticities (registry ``migration``/``avoidance`` domains) into a
first-order revenue-response multiplier so a mechanical revenue figure can be scaled to
an *illustrative* behavioural one. Standalone and **not yet wired into the engine** — a
later PR applies the factor to a scenario's revenue, default OFF and caveated.

See :mod:`~wealthlens_sim.behavioural.response`.
"""

from wealthlens_sim.behavioural.response import (
    BehaviouralChannel,
    BehaviouralResponse,
    revenue_response_factor,
)

__all__ = [
    "BehaviouralChannel",
    "BehaviouralResponse",
    "revenue_response_factor",
]
