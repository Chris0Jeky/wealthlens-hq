"""Uncertainty propagation for wealth-policy scenarios.

Methods: Monte Carlo, Sobol sensitivity analysis (SALib), Bayesian posterior
sampling (NumPyro, Phase 3+), surrogate models for interactive dashboard.

Reference: Blueprint v5 sections 8.1 (layer 7), 13.5.

Wave 13 groundwork: :mod:`~wealthlens_sim.uncertainty.sampling` provides the
deterministic parameter-sampling layer (independent + Latin-hypercube draws over
uniform/triangular marginals) and :mod:`~wealthlens_sim.uncertainty.propagation`
propagates a sampled block through a scalar ``evaluate`` into a cited interval.
Both are standalone and not yet wired into the engine; a later PR will supply the
engine ``evaluate`` to replace the single multiplicative top-tail-alpha band with
full Monte-Carlo propagation (default OFF).
"""

from wealthlens_sim.uncertainty.propagation import (
    PropagationResult,
    propagate,
)
from wealthlens_sim.uncertainty.sampling import (
    Distribution,
    ParameterSamples,
    ParameterSpec,
    SamplingConfig,
    SamplingMethod,
    sample_parameters,
)

__all__ = [
    "Distribution",
    "ParameterSamples",
    "ParameterSpec",
    "PropagationResult",
    "SamplingConfig",
    "SamplingMethod",
    "propagate",
    "sample_parameters",
]
