"""Synthetic data generation for public-release wealth datasets.

v0.1 (Wave 12 PR1) ships a deterministic parametric generator
(:func:`generate_population`) — a lognormal body with a Pareto upper tail — so
the microsimulation engine has inputs without any licensed microdata. Richer
methods (statistical matching / StatMatch, CTGAN/TVAE via SDV, gradient-descent
reweighting via ipfn / policyengine-reweight) are deferred to later sub-waves.

Reference: Blueprint v5 section 7.4, compass deliverable 6.
"""

from wealthlens_sim.synth.population import (
    SynthConfig,
    SyntheticPopulation,
    generate_population,
)

__all__ = ["SynthConfig", "SyntheticPopulation", "generate_population"]
