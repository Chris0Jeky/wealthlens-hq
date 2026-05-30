"""Per-household revenue attribution for decile breakdowns (Wave 12 PR3a).

The ``rules.run_scenario`` aggregate API discards per-household detail, so the
engine recomputes liabilities household-by-household here to attribute revenue to
wealth deciles. The per-household calculators used are the *same* functions the
aggregate calculators call internally, so the weighted sum across deciles equals
the aggregate ``total_revenue_bn`` (an invariant the tests assert).
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
    """Attribute total scenario revenue (GBP bn) across weighted wealth deciles.

    Households are ranked by ``total_net_wealth`` ascending and split into
    ``n_deciles`` equal-grossing-weight bins (each decile holds ~1/n of the
    grossed-up population, not 1/n of the survey rows). Each household is assigned
    by the cumulative weight at its *centre* (``cum_before + weight/2``), which
    avoids the off-by-one bias of using a leading or trailing edge.

    Returns a list of length ``n_deciles`` (lowest wealth first), or an empty
    list when there are no households or total weight is non-positive.
    """
    if not households:
        return []

    total_weight = sum(h.weight for h in households)
    if total_weight <= 0:
        return []

    ranked = sorted(households, key=lambda h: h.total_net_wealth)
    decile_gbp = [0.0] * n_deciles
    cumulative = 0.0
    for household in ranked:
        liability = sum(household_liability(household, sel) for sel in selections)
        centre_fraction = (cumulative + household.weight / 2) / total_weight
        index = min(n_deciles - 1, int(centre_fraction * n_deciles))
        decile_gbp[index] += liability * household.weight
        cumulative += household.weight

    return [gbp / _GBP_PER_BN for gbp in decile_gbp]
