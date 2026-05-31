"""Deterministic synthetic household-population generator (v0.1).

Wave 12 PR1 (see docs/WAVE12_SIMULATION_ENGINE_DESIGN.md). Produces a weighted
population of :class:`~wealthlens_sim.schema.household.Household` objects so the
microsimulation engine has inputs, *without* shipping any licensed microdata.

**This data is SYNTHETIC.** It is generated from a parametric model, not drawn
from real respondents, and must never be presented as observed statistics. Its
distributional shape is a lognormal body with a Pareto upper tail — a simple
parametric approximation of the observed WAS wealth marginals.

Calibration parameters in :class:`SynthConfig` are anchored to cited public ONS releases.
Defaults use the Wealth and Assets Survey April 2020 to March 2022 Great Britain
wealth marginals plus ONS 2022 Great Britain household-count/nation-share anchors.
This remains synthetic data, not observed microdata; source calibration avoids
the v0.1 gross-wealth overshoot but does not replace licensed WAS/FRS microdata.
See Blueprint v5 section 7.
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

# Public calibration anchors. ONS WAS is Great Britain only, so the v0.1 defaults
# also gross to Great Britain and exclude Northern Ireland from default nation
# shares until NI-specific wealth marginals are wired.
ONS_WAS_TOTAL_WEALTH_GBP = 13_568_000_000_000.0
ONS_WAS_MEDIAN_HOUSEHOLD_WEALTH_GBP = 293_700.0
ONS_WAS_TOP_DECILE_THRESHOLD_GBP = 1_200_500.0
ONS_WAS_TOP_ONE_PERCENT_THRESHOLD_GBP = 3_121_500.0
ONS_GB_HOUSEHOLDS_2022 = 27_500_000.0
ONS_GB_NATION_HOUSEHOLDS_2022 = {
    Nation.ENGLAND.value: 23_626_000.0,
    Nation.SCOTLAND.value: 2_542_000.0,
    Nation.WALES.value: 1_332_000.0,
}
SYNTH_CALIBRATION_SOURCE_IDS = ("ons-was-wealth", "ons-families-households-2022")
_CALIBRATION_SENSITIVE_FIELDS = frozenset(
    {
        "population_households",
        "median_net_wealth",
        "lognormal_sigma",
        "nation_shares",
        "pareto_threshold",
        "pareto_alpha",
        "asset_shares",
    }
)


class SynthConfig(BaseModel):
    """Parameters for the v0.1 synthetic-population generator.

    Numeric defaults are calibrated to cited public ONS marginals. They are still
    tunable because this is synthetic data, not respondent microdata.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    # Assignment-style Field defaults (not Annotated) so default construction
    # `SynthConfig()` type-checks cleanly under the project's strict mypy.
    n_households: int = Field(gt=0, default=10_000, description="Number of synthetic households to draw")
    seed: int = Field(ge=0, default=42, description="RNG seed for reproducibility")
    population_households: float = Field(
        gt=0,
        default=ONS_GB_HOUSEHOLDS_2022,
        description="Total Great Britain households the sample grosses up to (ONS 2022)",
    )

    # Wealth shape: lognormal body, Pareto tail above the threshold.
    median_net_wealth: float = Field(
        gt=0, default=ONS_WAS_MEDIAN_HOUSEHOLD_WEALTH_GBP, description="Median household net wealth, GBP (ONS WAS)"
    )
    lognormal_sigma: float = Field(gt=0, default=1.1, description="Lognormal dispersion calibrated to WAS deciles")
    pareto_threshold: float = Field(
        gt=0,
        default=ONS_WAS_TOP_DECILE_THRESHOLD_GBP,
        description="Net-wealth level above which the synthetic Pareto tail applies, GBP (ONS WAS top-decile threshold)",
    )
    pareto_alpha: float = Field(
        gt=1,
        default=2.5,
        description="Synthetic Pareto tail exponent calibrated to WAS top-decile/top-1% marginals",
    )

    # Couple share (else single-person household).
    couple_share: float = Field(ge=0, le=1, default=0.55, description="Fraction of households that are couples")

    # Great Britain nation household shares (ONS Families and households 2022).
    nation_shares: dict[str, float] = Field(
        default_factory=lambda: {
            nation: households / ONS_GB_HOUSEHOLDS_2022
            for nation, households in ONS_GB_NATION_HOUSEHOLDS_2022.items()
        },
        description="Share of households by Great Britain nation; must sum to ~1",
    )

    # Net-wealth split across asset types (ONS WAS April 2020 to March 2022).
    asset_shares: dict[str, float] = Field(
        default_factory=lambda: {
            AssetType.DC_PENSION.value: 0.3544,
            AssetType.MAIN_RESIDENCE.value: 0.4025,
            AssetType.FINANCIAL.value: 0.1411,
            AssetType.PHYSICAL.value: 0.1021,
        },
        description="Fraction of household net wealth held in each asset type; must sum to ~1",
    )
    calibration_source_ids: tuple[str, ...] = Field(
        default=SYNTH_CALIBRATION_SOURCE_IDS,
        description=(
            "Source-registry IDs for the public marginals used to calibrate this synthetic population; "
            "custom calibration-sensitive parameters must provide their own IDs or leave this empty"
        ),
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
        description=(
            "Source IDs and stable synthetic generation-parameter tags used to build this "
            "population; the engine surfaces them alongside its provenance manifest."
        ),
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
    keys = sorted(shares)
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
    for asset_type in sorted(asset_shares):
        share = asset_shares[asset_type]
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


def _format_float(value: float) -> str:
    """Return a compact stable representation for provenance tags."""
    return f"{value:.12g}"


def _format_mapping(values: dict[str, float]) -> str:
    """Return a stable key-sorted mapping representation for provenance tags."""
    return ";".join(f"{key}={_format_float(values[key])}" for key in sorted(values))


def _generation_provenance_ids(config: SynthConfig) -> list[str]:
    """Return stable tags for generator parameters that affect generated output."""
    return [
        f"synth.n_households:{config.n_households}",
        f"synth.seed:{config.seed}",
        f"synth.population_households:{_format_float(config.population_households)}",
        f"synth.median_net_wealth:{_format_float(config.median_net_wealth)}",
        f"synth.lognormal_sigma:{_format_float(config.lognormal_sigma)}",
        f"synth.pareto_threshold:{_format_float(config.pareto_threshold)}",
        f"synth.pareto_alpha:{_format_float(config.pareto_alpha)}",
        f"synth.couple_share:{_format_float(config.couple_share)}",
        f"synth.nation_shares:{_format_mapping(config.nation_shares)}",
        f"synth.asset_shares:{_format_mapping(config.asset_shares)}",
    ]


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

    if (
        "calibration_source_ids" not in config.model_fields_set
        and _CALIBRATION_SENSITIVE_FIELDS.intersection(config.model_fields_set)
    ):
        source_ids: list[str] = []
    else:
        source_ids = list(config.calibration_source_ids)

    provenance_ids = [*source_ids, *_generation_provenance_ids(config)]
    return SyntheticPopulation(households=households, seed=config.seed, provenance_ids=provenance_ids)
