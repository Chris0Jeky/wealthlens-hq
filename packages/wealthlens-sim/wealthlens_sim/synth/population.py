"""Deterministic synthetic household-population generator (v0.1).

Wave 12 PR1 (see docs/WAVE12_SIMULATION_ENGINE_DESIGN.md). Produces a weighted
population of :class:`~wealthlens_sim.schema.household.Household` objects so the
microsimulation engine has inputs, *without* shipping any licensed microdata.

**This data is SYNTHETIC.** It is generated from a parametric model, not drawn
from real respondents, and must never be presented as observed statistics. Its
distributional shape is a lognormal body with a Pareto upper tail — the standard
empirical description of wealth (Vermeulen 2018; already encoded as the top-tail
Pareto alpha in ``registries/assumptions.yml``).

Calibration parameters in :class:`SynthConfig` are **illustrative v0.1 defaults**.
They are coarsely consistent with public ONS sources (Wealth and Assets Survey
for the wealth shape/asset mix; mid-year population estimates for the nation
split) but are **not verified against a specific release**. Verify and cite the
exact source release (URL + access date in ``registries/sources.yml``) before
any generated figure informs a published number. See Blueprint v5 §7.1-7.4.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlens_sim.schema.base import Nation
from wealthlens_sim.schema.household import Asset, AssetType, Household, Person

# Constituent nations only (Household rejects the UK aggregate).
_NATIONS: tuple[Nation, ...] = (
    Nation.ENGLAND,
    Nation.SCOTLAND,
    Nation.WALES,
    Nation.NORTHERN_IRELAND,
)


class SynthConfig(BaseModel):
    """Parameters for the v0.1 synthetic-population generator.

    All numeric defaults are illustrative and tunable; they are not asserted as
    published statistics. Calibrate against cited ONS releases before publishing.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    # Assignment-style Field defaults (not Annotated) so default construction
    # `SynthConfig()` type-checks cleanly under the project's strict mypy.
    n_households: int = Field(gt=0, default=10_000, description="Number of synthetic households to draw")
    seed: int = Field(ge=0, default=42, description="RNG seed for reproducibility")
    population_households: float = Field(
        gt=0, default=28_000_000, description="Total UK households the sample grosses up to (ONS, illustrative)"
    )

    # Wealth shape: lognormal body, Pareto tail above the threshold.
    median_net_wealth: float = Field(
        gt=0, default=300_000, description="Median household net wealth, GBP (ONS WAS, illustrative)"
    )
    lognormal_sigma: float = Field(gt=0, default=1.4, description="Lognormal dispersion of the wealth body")
    pareto_threshold: float = Field(
        gt=0, default=2_000_000, description="Net-wealth level above which the Pareto tail applies, GBP"
    )
    pareto_alpha: float = Field(
        gt=1, default=1.5, description="Pareto tail exponent (matches top-tail assumptions registry)"
    )

    # Couple share (else single-person household).
    couple_share: float = Field(ge=0, le=1, default=0.55, description="Fraction of households that are couples")

    # Constituent-nation population shares (ONS mid-year estimates, illustrative).
    nation_shares: dict[str, float] = Field(
        default_factory=lambda: {
            Nation.ENGLAND.value: 0.84,
            Nation.SCOTLAND.value: 0.08,
            Nation.WALES.value: 0.05,
            Nation.NORTHERN_IRELAND.value: 0.03,
        },
        description="Share of households by constituent nation; must sum to ~1",
    )

    # Net-wealth split across asset types (ONS WAS aggregate composition, illustrative).
    asset_shares: dict[str, float] = Field(
        default_factory=lambda: {
            AssetType.DC_PENSION.value: 0.42,
            AssetType.MAIN_RESIDENCE.value: 0.36,
            AssetType.FINANCIAL.value: 0.13,
            AssetType.PHYSICAL.value: 0.09,
        },
        description="Fraction of household net wealth held in each asset type; must sum to ~1",
    )

    @model_validator(mode="after")
    def _shares_sum_to_one(self) -> SynthConfig:
        for name, shares in (("nation_shares", self.nation_shares), ("asset_shares", self.asset_shares)):
            total = sum(shares.values())
            if not 0.99 <= total <= 1.01:
                msg = f"{name} must sum to ~1.0, got {total}"
                raise ValueError(msg)
        return self


class SyntheticPopulation(BaseModel):
    """A generated synthetic population: households plus generation metadata."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    households: list[Household]
    seed: int
    is_synthetic: bool = Field(default=True, description="Always True — never real microdata")
    provenance_ids: list[str] = Field(
        default_factory=list,
        description="Assumption/source IDs consumed to build this population; the engine "
        "feeds these into its provenance manifest (empty until calibration is wired).",
    )

    @property
    def weights(self) -> list[float]:
        """Per-household grossing weights (weights live on each Household.weight)."""
        return [h.weight for h in self.households]

    @property
    def total_net_wealth(self) -> float:
        """Grossed-up total net wealth across the population (GBP)."""
        return sum(h.total_net_wealth * h.weight for h in self.households)


def _draw_net_wealth(rng: np.random.Generator, config: SynthConfig) -> NDArray[np.float64]:
    """Draw household net wealth: lognormal body, Pareto Type-I tail above threshold."""
    mu = float(np.log(config.median_net_wealth))  # median of lognormal is exp(mu)
    wealth = rng.lognormal(mean=mu, sigma=config.lognormal_sigma, size=config.n_households)
    # Reshape the upper tail to follow Pareto(alpha) so it matches the top-tail model
    # rather than the (too-thin) lognormal tail.
    # Only the draws that already landed above the threshold are reshaped, so the
    # tail *count* (mass) is the lognormal-implied P(X>=threshold) — it is NOT an
    # independent mixing weight. Tuning the tail share to a target (e.g. top-1%)
    # means jointly solving median/sigma/threshold. Documented for calibrators.
    tail_mask = wealth >= config.pareto_threshold
    n_tail = int(tail_mask.sum())
    if n_tail:
        u = rng.uniform(size=n_tail)
        # Pareto Type I inverse-CDF: x = threshold * (1 - u)^(-1/alpha)
        wealth[tail_mask] = config.pareto_threshold * (1.0 - u) ** (-1.0 / config.pareto_alpha)
    return wealth


def _assign_by_share(rng: np.random.Generator, shares: dict[str, float], size: int) -> NDArray[np.str_]:
    """Vectorised categorical draw over the keys of ``shares`` (normalised)."""
    keys = list(shares.keys())
    probs = np.array([shares[k] for k in keys], dtype=np.float64)
    probs = probs / probs.sum()
    return rng.choice(keys, size=size, p=probs)


def _make_assets(person_wealth: float, asset_shares: dict[str, float]) -> list[Asset]:
    """Split a person's net wealth across asset types (gross=net, no debt in v0.1).

    Shares are normalised so the assets sum to exactly ``person_wealth`` even if
    the configured shares sum to slightly off 1.0 (within the validator tolerance).
    """
    total_share = sum(asset_shares.values()) or 1.0
    assets: list[Asset] = []
    for asset_type, share in asset_shares.items():
        value = person_wealth * (share / total_share)
        if value <= 0:
            continue
        assets.append(
            Asset(
                asset_type=AssetType(asset_type),
                gross_value=value,
                debt=0.0,
                is_liquid=asset_type == AssetType.FINANCIAL.value,
            )
        )
    return assets


def _make_person(person_id: str, age: int, wealth: float, asset_shares: dict[str, float]) -> Person:
    """Construct a synthetic person (all schema fields explicit for strict typing)."""
    return Person(
        person_id=person_id,
        age=age,
        is_uk_resident=True,
        fig_regime_years_remaining=0,
        annual_income=0.0,
        capital_gains_realised=0.0,
        assets=_make_assets(wealth, asset_shares),
    )


def generate_population(config: SynthConfig | None = None) -> SyntheticPopulation:
    """Generate a deterministic synthetic household population.

    The same ``config`` (same seed) always yields an identical population.
    """
    if config is None:
        config = SynthConfig()

    rng = np.random.default_rng(config.seed)
    n = config.n_households
    wealth = _draw_net_wealth(rng, config)
    nations = _assign_by_share(rng, config.nation_shares, n)
    is_couple = rng.random(n) < config.couple_share
    # Couples split wealth 60/40 (fixed); ages drawn from a plausible adult range.
    ages = rng.integers(18, 90, size=n)
    partner_ages = rng.integers(18, 90, size=n)
    grossing_weight = config.population_households / n

    households: list[Household] = []
    for i in range(n):
        hh_wealth = float(wealth[i])
        persons: list[Person] = []
        if is_couple[i]:
            persons.append(_make_person(f"h{i}p1", int(ages[i]), hh_wealth * 0.6, config.asset_shares))
            persons.append(_make_person(f"h{i}p2", int(partner_ages[i]), hh_wealth * 0.4, config.asset_shares))
        else:
            persons.append(_make_person(f"h{i}p1", int(ages[i]), hh_wealth, config.asset_shares))

        households.append(
            Household(
                household_id=f"synthhh{i}",
                nation=Nation(nations[i]),
                region="",
                weight=grossing_weight,
                persons=persons,
            )
        )

    return SyntheticPopulation(households=households, seed=config.seed)
