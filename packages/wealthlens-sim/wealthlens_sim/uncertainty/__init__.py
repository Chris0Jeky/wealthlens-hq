"""Uncertainty propagation for wealth-policy scenarios.

Methods: Monte Carlo, Sobol sensitivity analysis (SALib), Bayesian posterior
sampling (NumPyro, Phase 3+), surrogate models for interactive dashboard.

Reference: Blueprint v5 sections 8.1 (layer 7), 13.5.

Wave 13 groundwork: :mod:`~wealthlens_sim.uncertainty.sampling` provides the
deterministic parameter-sampling layer (independent + Latin-hypercube draws over
uniform/triangular marginals). It is standalone and not yet wired into the engine;
a later PR will run the scenario over the sampled matrix to replace the single
multiplicative top-tail-alpha band with full Monte-Carlo propagation.
"""

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
    "SamplingConfig",
    "SamplingMethod",
    "sample_parameters",
]
