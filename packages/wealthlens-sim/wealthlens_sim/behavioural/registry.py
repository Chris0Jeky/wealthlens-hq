"""Build behavioural-response channels from the cited assumption registry.

Keeps the behavioural layer **sourced from the registry**, not hand-constructed: each
:class:`~wealthlens_sim.behavioural.response.BehaviouralChannel` is built from a cited
``RangeValue`` elasticity (``name = source_id = the assumption_id``), so a behavioural
estimate traces back to its evidence (Advani & Summers 2020, Brülhart 2022, Agersnap &
Zidar 2021, ...).

Only **rate-responsive semi-elasticities** belong in the multiplicative rate-response
factor — the ``migration`` (base migrates with the rate) and ``avoidance`` (realisation
timing) domains. The other behavioural-ish registry domains are deliberately EXCLUDED
here because they are **level adjustments to the base, not rate-elasticities**, and
folding them into ``(1 + e*dtau)`` would be a category error:

* ``compliance`` (``wealth_concealment``): a *fraction* of the base concealed — a base
  haircut applied before the tax, independent of the rate change.
* ``valuation`` (``private_business.discount``): a *fraction* discount on an asset
  class — also a base adjustment, not a response to the rate.

Wire those two as base adjustments elsewhere (synth/reconstruction), not through this
module.
"""

from __future__ import annotations

from collections.abc import Sequence

from wealthlens_sim.assumptions.schema import AssumptionRegistry, RangeValue
from wealthlens_sim.behavioural.response import BehaviouralChannel

__all__ = [
    "RATE_RESPONSIVE_DOMAINS",
    "load_behavioural_channels",
]

#: Registry domains whose ``RangeValue`` entries are rate-responsive semi-elasticities
#: suitable for the multiplicative behavioural response factor. (See the module
#: docstring for why ``compliance``/``valuation`` are excluded.)
RATE_RESPONSIVE_DOMAINS = ("migration", "avoidance")


def load_behavioural_channels(
    registry: AssumptionRegistry,
    *,
    point: str = "central",
    domains: Sequence[str] = RATE_RESPONSIVE_DOMAINS,
) -> list[BehaviouralChannel]:
    """Build behavioural channels from the registry's cited rate-elasticity assumptions.

    Reads every ``RangeValue`` assumption in ``domains`` and builds a channel sourced
    from it (``name = source_id = assumption_id``). Non-range assumptions in those
    domains are skipped (a rate-response channel needs a low/central/high elasticity).
    Channels are returned in ``domains``-then-registry order. ``point`` selects which of
    the registry triple to use (``"central"`` default, or ``"low"``/``"high"`` for a
    future uncertainty band — note ``"high"`` is the MORE-eroding end for a negative
    elasticity).

    This loads channels only; it does **not** apply them to any revenue. Applying them
    correctly (per the affected base slice, with the right rate-change units) is the
    caller's responsibility — see the "When wiring this in" checklist in
    :mod:`~wealthlens_sim.behavioural.response`.
    """
    channels: list[BehaviouralChannel] = []
    for domain in domains:
        for assumption in registry.by_domain(domain):
            value = assumption.value_or_distribution
            if isinstance(value, RangeValue):
                channels.append(
                    BehaviouralChannel.from_range_value(
                        assumption.assumption_id,
                        value,
                        point=point,
                        source_id=assumption.assumption_id,
                    )
                )
    return channels
