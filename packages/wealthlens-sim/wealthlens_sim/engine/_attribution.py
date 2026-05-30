"""Per-household revenue attribution by wealth decile (Wave 12 PR3a).

The ``rules.run_scenario`` aggregate API discards per-household detail, so the
engine recomputes liabilities household-by-household here to attribute revenue to
wealth deciles. The per-household calculators used are the *same* functions the
aggregate calculators call internally, so the weighted decile sum equals the
aggregate ``total_revenue_bn`` up to floating-point summation order (a tested
invariant).

Deciles are **equal-grossing-weight** bins (the standard definition: each decile
holds 1/n of the weighted population). A household whose grossing weight straddles
a decile boundary has its revenue split across the bands it overlaps in proportion
to the weight in each band, so the bins stay exactly even even when survey weights
are heterogeneous (as real WAS/FRS microdata will be behind the population seam).
"""

from __future__ import annotations

from typing import assert_never

from wealthlens_sim.reforms.a_annual_wealth import WealthTaxConfig, compute_wealth_tax
from wealthlens_sim.reforms.b_one_off_levy import OneOffLevyConfig, compute_one_off_levy
from wealthlens_sim.reforms.c_cgt_reform import CGTConfig, compute_household_cgt
from wealthlens_sim.reforms.d_iht_reform import IHTConfig, compute_household_iht
from wealthlens_sim.reforms.e_property_tax import HVCTSConfig, compute_hvcts
from wealthlens_sim.rules.scenario import FamilySelection, PolicyFamily
from wealthlens_sim.schema.household import Household

_GBP_PER_BN = 1_000_000_000.0


def household_liability(household: Household, selection: FamilySelection) -> float:
    """Return one household's unweighted GBP liability for one family.

    Mirrors ``rules.scenario._run_family`` but at the household grain. The
    ``match``/``assert_never`` makes the dispatch exhaustive: adding a
    ``PolicyFamily`` member without a branch is a compile-time mypy error.
    """
    config = selection.config
    match selection.family:
        case PolicyFamily.ANNUAL_WEALTH_TAX:
            assert isinstance(config, WealthTaxConfig)
            return compute_wealth_tax(household, config).tax_liability
        case PolicyFamily.ONE_OFF_LEVY:
            assert isinstance(config, OneOffLevyConfig)
            return compute_one_off_levy(household, config).levy_liability
        case PolicyFamily.CGT:
            assert isinstance(config, CGTConfig)
            return compute_household_cgt(household, config).total_cgt_liability
        case PolicyFamily.IHT:
            assert isinstance(config, IHTConfig)
            return compute_household_iht(household, config).total_iht_liability
        case PolicyFamily.HVCTS:
            assert isinstance(config, HVCTSConfig)
            return compute_hvcts(household, config).total_surcharge
        case _:  # pragma: no cover - exhaustiveness guard
            assert_never(selection.family)


def revenue_by_wealth_decile(
    households: list[Household],
    selections: list[FamilySelection],
    *,
    n_deciles: int = 10,
) -> list[float]:
    """Attribute total scenario revenue (GBP bn) across equal-weight wealth deciles.

    Households are ranked by ``total_net_wealth`` ascending and laid out along a
    cumulative-weight axis of length ``total_weight``. The axis is cut into
    ``n_deciles`` equal bands of width ``total_weight / n_deciles``; each
    household's weighted liability is split across the bands its weight interval
    ``[cumulative, cumulative + weight)`` overlaps, proportional to the overlap.
    This keeps the deciles exactly even (each holds 1/n of the weighted
    population) and places the highest-wealth weight in the top decile regardless
    of how heterogeneous the survey weights are.

    Returns a list of length ``n_deciles`` (lowest wealth first), or an empty
    list when ``households`` is empty.

    Raises:
        ValueError: if the population is non-empty but its total weight is not
            positive — a data defect (weights must be > 0), surfaced rather than
            silently collapsed into an empty result.
    """
    if not households:
        return []

    total_weight = sum(h.weight for h in households)
    if total_weight <= 0:
        msg = f"total household weight must be positive to attribute deciles, got {total_weight}"
        raise ValueError(msg)

    ranked = sorted(households, key=lambda h: h.total_net_wealth)
    band_width = total_weight / n_deciles
    decile_gbp = [0.0] * n_deciles
    cumulative = 0.0
    for household in ranked:
        weighted_liability = sum(household_liability(household, sel) for sel in selections) * household.weight
        start = cumulative
        end = cumulative + household.weight
        # Bands this household's weight interval [start, end) overlaps. The tiny
        # epsilon keeps an interval ending exactly on a boundary out of the next
        # (empty-overlap) band; min() guards the final float-rounding edge.
        first = min(n_deciles - 1, int(start / band_width))
        last = min(n_deciles - 1, int((end - 1e-9) / band_width))
        if first == last:
            decile_gbp[first] += weighted_liability
        else:
            for index in range(first, last + 1):
                band_lo = index * band_width
                band_hi = (index + 1) * band_width
                overlap = min(end, band_hi) - max(start, band_lo)
                if overlap > 0:
                    decile_gbp[index] += weighted_liability * (overlap / household.weight)
        cumulative = end

    return [gbp / _GBP_PER_BN for gbp in decile_gbp]
