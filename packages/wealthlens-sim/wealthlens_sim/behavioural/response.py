"""Reduced-form behavioural-response factors for revenue estimation (Wave 13+).

Static (mechanical) revenue assumes taxpayers do not change behaviour when a reform
changes a tax rate. In reality the taxable base responds — non-dom/domestic migration,
avoidance, realisation timing. This module turns **cited** semi-elasticities (the
registry ``migration``/``avoidance`` domains: Advani & Summers 2020, Brülhart et al.
2022, Agersnap & Zidar 2021, etc.) into a first-order revenue-response **multiplier**,
so a caller can scale a mechanical revenue figure to an *illustrative* behavioural one.

This is a deliberately SIMPLE, transparent reduced form — **NOT** a structural
behavioural model, and not a costing. For a base with constant semi-elasticity ``ε``
with respect to the tax rate, a rate change of ``Δτ`` **percentage points** moves the
base by a factor ``(1 + e*dtau)`` to first order, and revenue (rate * base) scales by the
same factor. Independent channels compose multiplicatively. The combined factor is
clamped to ``≥ 0`` (this reduced form cannot represent a response that destroys more
than 100% of revenue).

Design (mirrors the other Wave-13 layers):
* Pure, deterministic, dependency-free beyond Pydantic/NumPy (already deps).
* **Engine-free and not wired in.** A later PR supplies the rate change from a
  scenario and applies the factor to the relevant family's revenue — default OFF and
  surfaced behind a ``caveats[]`` entry, because behavioural responses are uncertain
  and the elasticities have ``transferability_score: low`` for UK migration.
* The unit contract is explicit: ``rate_change_pp`` is in **percentage points** (a 1%→2%
  wealth tax is ``rate_change_pp = 1.0``), matching how the registry semi-elasticities
  are defined ("per percentage-point of the tax rate"). The caller owns supplying the
  correct rate change; this module only implements the cited reduced form.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.assumptions.schema import RangeValue

__all__ = [
    "BehaviouralChannel",
    "BehaviouralResponse",
    "revenue_response_factor",
]


class BehaviouralChannel(BaseModel):
    """One behavioural channel: a cited semi-elasticity of the base to the tax rate.

    ``semi_elasticity`` is the proportional change in the taxable base per percentage
    point of the tax rate (registry ``migration``/``avoidance`` domains). It is
    typically **negative** for base-eroding responses (migration, lock-in), but any
    finite value is accepted (a positive elasticity — base-broadening — is unusual but
    not forbidden). ``source_id`` keeps the channel traceable to its registry evidence.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1, description="Stable channel identifier (e.g. a registry assumption id)")
    semi_elasticity: float = Field(description="Proportional base change per percentage-point of the tax rate")
    source_id: str | None = Field(default=None, description="Optional registry assumption/source id for provenance")

    @model_validator(mode="after")
    def _finite(self) -> BehaviouralChannel:
        if not math.isfinite(self.semi_elasticity):
            msg = f"BehaviouralChannel {self.name!r} semi_elasticity must be finite, got {self.semi_elasticity}"
            raise ValueError(msg)
        return self

    @classmethod
    def from_range_value(
        cls,
        name: str,
        value: RangeValue,
        *,
        point: str = "central",
        source_id: str | None = None,
    ) -> BehaviouralChannel:
        """Build a channel from a registry :class:`RangeValue` elasticity.

        ``point`` selects which of the registry triple to use: ``"central"`` (default),
        ``"low"``, or ``"high"`` — so a point estimate uses the central elasticity while
        a future Monte-Carlo pass can build low/high channels for an uncertainty band.
        """
        if point not in ("low", "central", "high"):
            msg = f"point must be 'low', 'central' or 'high', got {point!r}"
            raise ValueError(msg)
        return cls(name=name, semi_elasticity=float(getattr(value, point)), source_id=source_id)


@dataclass(frozen=True, kw_only=True)
class BehaviouralResponse:
    """Result of composing behavioural channels into a revenue-response multiplier.

    ``factor`` multiplies a mechanical revenue figure to give the illustrative
    behavioural one (``factor < 1`` ⇒ revenue eroded). ``channel_factors`` is the
    per-channel ``(name, 1 + ε·Δτ)`` breakdown, aligned with the input order.
    ``clamped`` is ``True`` when the raw product fell below 0 and was clamped to 0 (the
    reduced form cannot erode more than 100%). ``provenance_ids`` records the method,
    the rate change, and each channel's marginal so the estimate is auditable.
    """

    factor: float
    channel_factors: tuple[tuple[str, float], ...]
    rate_change_pp: float
    clamped: bool
    provenance_ids: tuple[str, ...]


def revenue_response_factor(
    channels: Sequence[BehaviouralChannel],
    rate_change_pp: float,
) -> BehaviouralResponse:
    """Compose ``channels`` into a first-order revenue-response multiplier.

    Each channel contributes a factor ``(1 + semi_elasticity · rate_change_pp)``;
    independent channels compose **multiplicatively**. ``rate_change_pp`` is the tax-rate
    change in **percentage points** (see the module docstring's unit contract). With no
    channels the factor is ``1.0`` (no response). The combined factor is clamped to
    ``≥ 0``.

    Raises ``ValueError`` if ``rate_change_pp`` is non-finite or a composed factor is
    non-finite (it never should be for finite inputs, but guard against overflow).
    """
    if not math.isfinite(rate_change_pp):
        msg = f"rate_change_pp must be finite, got {rate_change_pp}"
        raise ValueError(msg)

    channel_factors: list[tuple[str, float]] = []
    combined = 1.0
    for channel in channels:
        f_i = 1.0 + channel.semi_elasticity * rate_change_pp
        channel_factors.append((channel.name, f_i))
        combined *= f_i

    if not math.isfinite(combined):
        msg = "composed behavioural factor is non-finite (inputs overflow a usable range)"
        raise ValueError(msg)

    clamped = combined < 0.0
    factor = 0.0 if clamped else combined

    provenance_ids = (
        "behavioural.method:first_order_reduced_form",
        f"behavioural.rate_change_pp:{_fmt(rate_change_pp)}",
        f"behavioural.factor:{_fmt(factor)}",
        *(
            f"behavioural.channel:{ch.name}={_fmt(ch.semi_elasticity)}@{ch.source_id if ch.source_id else '-'}"
            for ch in channels
        ),
    )
    return BehaviouralResponse(
        factor=factor,
        channel_factors=tuple(channel_factors),
        rate_change_pp=rate_change_pp,
        clamped=clamped,
        provenance_ids=provenance_ids,
    )


def _fmt(value: float) -> str:
    """Exact round-tripping float repr for provenance tags (``-0.0`` folded to ``0.0``)."""
    return repr(value + 0.0)
