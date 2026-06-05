"""Tests for the Sobol sensitivity layer (Wave 13).

Correctness is pinned against functions with *analytically known* Sobol indices:
the Ishigami function (the standard sensitivity-analysis benchmark), a purely
additive linear function (first-order == total-order, no interactions), and a
product (total-order > first-order, pure interaction). Tolerances are loose enough
for Monte-Carlo noise at the chosen sample sizes but tight enough to catch an
estimator that is wrong.
"""

from __future__ import annotations

import math

import pytest

from wealthlens_sim.uncertainty import (
    Distribution,
    ParameterSpec,
    SobolResult,
    sobol_indices,
)
from wealthlens_sim.uncertainty.sobol import DEFAULT_N_BASE


def _uniform(name: str, low: float, high: float) -> ParameterSpec:
    return ParameterSpec(name=name, low=low, central=(low + high) / 2.0, high=high, distribution=Distribution.UNIFORM)


class TestKnownIndices:
    def test_ishigami_matches_analytical(self):
        # Ishigami: f = sin(x1) + a sin^2(x2) + b x3^4 sin(x1), x_i ~ U(-pi, pi),
        # a=7, b=0.1. Textbook analytical indices:
        #   S1 = [0.3139, 0.4424, 0.0]   ST = [0.5576, 0.4424, 0.2436]
        a, b = 7.0, 0.1
        specs = [_uniform(n, -math.pi, math.pi) for n in ("x1", "x2", "x3")]

        def ishigami(p: dict[str, float]) -> float:
            return math.sin(p["x1"]) + a * math.sin(p["x2"]) ** 2 + b * p["x3"] ** 4 * math.sin(p["x1"])

        result = sobol_indices(specs, ishigami, n_base=32768, seed=7)
        s1 = result.first_order_by_name()
        st = result.total_order_by_name()

        assert s1["x1"] == pytest.approx(0.3139, abs=0.04)
        assert s1["x2"] == pytest.approx(0.4424, abs=0.04)
        assert s1["x3"] == pytest.approx(0.0, abs=0.04)
        assert st["x1"] == pytest.approx(0.5576, abs=0.04)
        assert st["x2"] == pytest.approx(0.4424, abs=0.04)
        assert st["x3"] == pytest.approx(0.2436, abs=0.04)

    def test_additive_linear_first_equals_total(self):
        # f = 2 x1 + x2, x_i ~ U(0,1). No interactions => S1 == ST, and
        # S1 = [Var(2 x1), Var(x2)] / Var = [1/3, 1/12] / (5/12) = [0.8, 0.2].
        specs = [_uniform("x1", 0.0, 1.0), _uniform("x2", 0.0, 1.0)]
        result = sobol_indices(specs, lambda p: 2.0 * p["x1"] + p["x2"], n_base=16384, seed=1)
        s1 = result.first_order_by_name()
        st = result.total_order_by_name()

        assert s1["x1"] == pytest.approx(0.8, abs=0.03)
        assert s1["x2"] == pytest.approx(0.2, abs=0.03)
        # No interactions: total-order tracks first-order, and they sum to ~1.
        assert st["x1"] == pytest.approx(s1["x1"], abs=0.03)
        assert st["x2"] == pytest.approx(s1["x2"], abs=0.03)
        assert s1["x1"] + s1["x2"] == pytest.approx(1.0, abs=0.03)

    def test_product_total_exceeds_first(self):
        # f = x1 * x2, x_i ~ U(0,1). Pure interaction:
        #   S1 = 3/7 ≈ 0.4286 each, ST = 4/7 ≈ 0.5714 each, so ST > S1.
        specs = [_uniform("x1", 0.0, 1.0), _uniform("x2", 0.0, 1.0)]
        result = sobol_indices(specs, lambda p: p["x1"] * p["x2"], n_base=16384, seed=2)
        s1 = result.first_order_by_name()
        st = result.total_order_by_name()

        assert s1["x1"] == pytest.approx(3.0 / 7.0, abs=0.04)
        assert st["x1"] == pytest.approx(4.0 / 7.0, abs=0.04)
        assert st["x1"] > s1["x1"]
        assert st["x2"] > s1["x2"]


class TestStructureAndDeterminism:
    def test_deterministic_for_same_seed(self):
        specs = [_uniform("x1", 0.0, 1.0), _uniform("x2", 0.0, 1.0)]

        def f(p: dict[str, float]) -> float:
            return p["x1"] ** 2 + p["x2"]

        r1 = sobol_indices(specs, f, n_base=2048, seed=42)
        r2 = sobol_indices(specs, f, n_base=2048, seed=42)
        assert r1.first_order == r2.first_order
        assert r1.total_order == r2.total_order
        assert r1.total_variance == r2.total_variance

    def test_different_seed_changes_estimate(self):
        specs = [_uniform("x1", 0.0, 1.0), _uniform("x2", 0.0, 1.0)]
        f = lambda p: p["x1"] ** 2 + p["x2"]  # noqa: E731
        r1 = sobol_indices(specs, f, n_base=2048, seed=1)
        r2 = sobol_indices(specs, f, n_base=2048, seed=2)
        assert r1.first_order != r2.first_order

    def test_order_independent(self):
        # Supplying specs in a different order yields the same per-name indices.
        f = lambda p: 2.0 * p["a"] + p["b"]  # noqa: E731
        forward = sobol_indices([_uniform("a", 0.0, 1.0), _uniform("b", 0.0, 1.0)], f, n_base=4096, seed=3)
        reverse = sobol_indices([_uniform("b", 0.0, 1.0), _uniform("a", 0.0, 1.0)], f, n_base=4096, seed=3)
        assert forward.names == reverse.names == ("a", "b")
        assert forward.first_order == reverse.first_order
        assert forward.total_order == reverse.total_order

    def test_evaluation_count_and_fields(self):
        specs = [_uniform("x1", 0.0, 1.0), _uniform("x2", 0.0, 1.0), _uniform("x3", 0.0, 1.0)]
        result = sobol_indices(specs, lambda p: sum(p.values()), n_base=512, seed=0)
        assert isinstance(result, SobolResult)
        assert result.n_base == 512
        # n_base * (d + 2) total model runs.
        assert result.n_evaluations == 512 * (3 + 2)
        assert len(result.first_order) == len(result.total_order) == 3
        assert result.total_variance > 0.0

    def test_default_n_base(self):
        specs = [_uniform("x1", 0.0, 1.0)]
        result = sobol_indices(specs, lambda p: p["x1"], seed=0)
        assert result.n_base == DEFAULT_N_BASE

    def test_provenance_ids_capture_run(self):
        specs = [_uniform("x1", 0.0, 1.0), _uniform("x2", 0.0, 1.0)]
        result = sobol_indices(specs, lambda p: p["x1"] + p["x2"], n_base=256, seed=9)
        ids = result.provenance_ids
        assert "uncertainty.sobol.method:saltelli" in ids
        assert "uncertainty.sobol.n_base:256" in ids
        assert "uncertainty.sobol.n_evaluations:1024" in ids  # 256 * (2 + 2)
        assert "uncertainty.sobol.seed:9" in ids
        assert "uncertainty.sobol.parameters:x1;x2" in ids
        # The specs tag carries each marginal so the run is reproducible.
        assert any(s.startswith("uncertainty.sobol.specs:") for s in ids)
        assert any(s.startswith("uncertainty.sobol.estimators:") for s in ids)


class TestValidation:
    def test_empty_specs_rejected(self):
        with pytest.raises(ValueError, match="at least one ParameterSpec"):
            sobol_indices([], lambda p: 0.0)

    def test_duplicate_names_rejected(self):
        with pytest.raises(ValueError, match="duplicate parameter names"):
            sobol_indices([_uniform("x", 0.0, 1.0), _uniform("x", 0.0, 2.0)], lambda p: p["x"])

    def test_non_positive_n_base_rejected(self):
        with pytest.raises(ValueError, match="n_base must be positive"):
            sobol_indices([_uniform("x", 0.0, 1.0)], lambda p: p["x"], n_base=0)

    def test_constant_output_rejected(self):
        # Zero output variance => indices undefined; must fail loud, not return NaN.
        with pytest.raises(ValueError, match="zero variance"):
            sobol_indices([_uniform("x", 0.0, 1.0)], lambda _p: 5.0, n_base=256)

    def test_non_finite_evaluate_rejected(self):
        with pytest.raises(ValueError, match="non-finite"):
            sobol_indices([_uniform("x", 0.0, 1.0)], lambda p: math.inf, n_base=256)

    def test_single_parameter_is_fully_attributed(self):
        # A function of one input: that input explains all variance (S1 == ST ~ 1).
        result = sobol_indices([_uniform("x", 0.0, 1.0)], lambda p: p["x"], n_base=8192, seed=5)
        assert result.first_order_by_name()["x"] == pytest.approx(1.0, abs=0.03)
        assert result.total_order_by_name()["x"] == pytest.approx(1.0, abs=0.03)
        # Output array is read-only-safe: result indices are plain floats.
        assert all(isinstance(v, float) for v in result.first_order)
