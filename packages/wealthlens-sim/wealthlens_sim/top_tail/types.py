"""Result types for top-tail reconstruction.

Blueprint v5 §2.3: five co-equal baseline variants.
Blueprint v5 §10.1: intervals by default, never naked point estimates.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class BaselineVariant(StrEnum):
    SURVEY_ONLY = "survey_only"
    PARETO_CORRECTED = "pareto_corrected"
    RICH_LIST_AUGMENTED = "rich_list_augmented"
    MACRO_RECONCILED = "macro_reconciled"
    HIDDEN_WEALTH_SENSITIVITY = "hidden_wealth_sensitivity"


class Interval(BaseModel):
    """A credible interval with low, central, and high bounds."""

    model_config = ConfigDict(extra="forbid")

    low: float
    central: float
    high: float


class ParetoFit(BaseModel):
    """Result of fitting a Pareto Type I distribution to tail data."""

    model_config = ConfigDict(extra="forbid")

    alpha: Interval = Field(description="Pareto tail exponent with bootstrap CI")
    threshold: float = Field(ge=0, description="Wealth threshold used for fitting (£)")
    n_tail: int = Field(ge=0, description="Number of observations above threshold")
    ks_statistic: float | None = Field(
        default=None, description="Kolmogorov-Smirnov goodness-of-fit statistic"
    )


class WealthShares(BaseModel):
    """Top wealth share estimates with intervals."""

    model_config = ConfigDict(extra="forbid")

    top_10_pct: Interval = Field(description="Share of total wealth held by top 10%")
    top_1_pct: Interval = Field(description="Share of total wealth held by top 1%")
    top_01_pct: Interval = Field(description="Share of total wealth held by top 0.1%")


class TailEstimate(BaseModel):
    """Complete output for one baseline variant's top-tail estimate."""

    model_config = ConfigDict(extra="forbid")

    variant: BaselineVariant
    pareto_fit: ParetoFit
    wealth_shares: WealthShares
    total_wealth_imputed: Interval = Field(
        description="Total wealth after top-tail adjustment (£bn)"
    )
