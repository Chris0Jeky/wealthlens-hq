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
from typing import Literal

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
    point: Literal["low", "central", "high"] = "central",
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

    Passing a non-default ``domains`` (e.g. ``("compliance",)``/``("valuation",)``) IS
    permitted but UNGUARDED: those are level fractions, not rate-elasticities (see the
    module docstring), so composing them through ``revenue_response_factor`` is a category
    error the caller owns. ``domains`` is order-preserving-deduplicated so a repeated
    domain cannot emit a channel twice.

    Raises ``ValueError`` for an invalid ``point`` and ``TypeError`` if ``domains`` is a
    single string (a common gotcha — iterating a string yields characters) — validated
    up-front so an invalid call fails loudly even when no assumption matches.
    """
    if point not in ("low", "central", "high"):
        msg = f"point must be 'low', 'central' or 'high', got {point!r}"
        raise ValueError(msg)
    if isinstance(domains, str):
        msg = f"domains must be a sequence of strings, not a single string ({domains!r})"
        raise TypeError(msg)

    channels: list[BehaviouralChannel] = []
    # Deduplicate domains (order-preserving) so a repeated/overlapping domain list cannot
    # emit the same channel twice — composing it via revenue_response_factor would
    # double-count that channel's erosion of the SAME base, violating the independence
    # contract documented in `response.py`. (assumption_ids are globally unique, so once
    # each domain is processed at most once, no channel can recur.)
    for domain in dict.fromkeys(domains):
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
