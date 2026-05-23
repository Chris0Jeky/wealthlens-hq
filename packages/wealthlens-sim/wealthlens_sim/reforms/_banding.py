"""Shared progressive-rate banding infrastructure for wealth-based reforms.

Used by Family A (annual wealth tax) and Family B (one-off levy).
Both share the same marginal-rate band model and liability computation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RateBand(BaseModel):
    """A single band in a progressive wealth tax or levy schedule."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    threshold: float = Field(ge=0, description="Band starts at this wealth level (GBP)")
    rate: float = Field(gt=0, le=1, description="Marginal rate for this band")


def compute_banded_liability(
    wealth: float,
    rate_bands: tuple[RateBand, ...],
) -> float:
    """Compute marginal-rate liability across sorted bands.

    Bands are sorted by threshold internally. Wealth below the first
    band's threshold is untaxed (implicit 0% band).
    """
    if wealth <= 0:
        return 0.0
    bands = sorted(rate_bands, key=lambda b: b.threshold)
    liability = 0.0
    for i, band in enumerate(bands):
        if wealth <= band.threshold:
            break
        ceiling = bands[i + 1].threshold if i + 1 < len(bands) else wealth
        taxable_in_band = min(wealth, ceiling) - band.threshold
        liability += max(0.0, taxable_in_band) * band.rate
    return liability
