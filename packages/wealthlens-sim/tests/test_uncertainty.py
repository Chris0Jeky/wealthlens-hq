"""Tests for the Monte-Carlo parameter-sampling groundwork (Wave 13)."""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError

from wealthlens_sim.assumptions.schema import RangeValue
from wealthlens_sim.top_tail.types import Interval
from wealthlens_sim.uncertainty import (
    Distribution,
    ParameterSpec,
    SamplingConfig,
    SamplingMethod,
    sample_parameters,
)


def _specs() -> list[ParameterSpec]:
    return [
        ParameterSpec(name="alpha", low=2.0, central=2.5, high=3.0),
        ParameterSpec(name="threshold", low=1.0, central=1.0, high=2.0, distribution=Distribution.UNIFORM),
    ]


class TestParameterSpec:
    def test_rejects_non_ascending(self):
        with pytest.raises(ValidationError):
            ParameterSpec(name="x", low=3.0, central=2.0, high=1.0)

    def test_rejects_central_outside_bounds(self):
        with pytest.raises(ValidationError):
            ParameterSpec(name="x", low=1.0, central=5.0, high=2.0)

    def test_rejects_empty_name(self):
        with pytest.raises(ValidationError):
            ParameterSpec(name="", low=1.0, central=2.0, high=3.0)

    def test_degenerate_spec_allowed(self):
        spec = ParameterSpec(name="fixed", low=4.0, central=4.0, high=4.0)
        assert spec.low == spec.central == spec.high == 4.0

    def test_is_frozen(self):
        spec = ParameterSpec(name="x", low=1.0, central=2.0, high=3.0)
        with pytest.raises(ValidationError):
            spec.low = 0.0  # type: ignore[misc]

    def test_from_interval(self):
        spec = ParameterSpec.from_interval("a", Interval(low=1.0, central=2.0, high=4.0))
        assert (spec.low, spec.central, spec.high) == (1.0, 2.0, 4.0)
        assert spec.distribution is Distribution.TRIANGULAR

    def test_from_range_value_preserves_ascending(self):
        spec = ParameterSpec.from_range_value("a", RangeValue(type="range", low=1.0, central=2.0, high=4.0))
        assert (spec.low, spec.central, spec.high) == (1.0, 2.0, 4.0)

    def test_from_range_value_normalises_descending(self):
        # Negative-elasticity style range (low >= central >= high) is normalised
        # to an ascending density with central preserved.
        spec = ParameterSpec.from_range_value("e", RangeValue(type="range", low=-0.1, central=-0.3, high=-0.5))
        assert spec.low == -0.5
        assert spec.high == -0.1
        assert spec.central == -0.3


class TestSamplingConfig:
    def test_defaults(self):
        cfg = SamplingConfig()
        assert cfg.n_samples == 1024
        assert cfg.seed == 0
        assert cfg.method is SamplingMethod.LATIN_HYPERCUBE

    def test_rejects_non_positive_samples(self):
        with pytest.raises(ValidationError):
            SamplingConfig(n_samples=0)

    def test_rejects_negative_seed(self):
        with pytest.raises(ValidationError):
            SamplingConfig(seed=-1)


class TestSampling:
    def test_empty_specs_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            sample_parameters([])

    def test_duplicate_names_raise(self):
        specs = [
            ParameterSpec(name="dup", low=1.0, central=2.0, high=3.0),
            ParameterSpec(name="dup", low=1.0, central=2.0, high=3.0),
        ]
        with pytest.raises(ValueError, match="duplicate"):
            sample_parameters(specs)

    def test_shape_and_names_sorted(self):
        samples = sample_parameters(_specs(), SamplingConfig(n_samples=64))
        assert samples.names == ("alpha", "threshold")  # sorted
        assert samples.matrix.shape == (64, 2)
        assert samples.n_samples == 64

    def test_determinism_same_seed(self):
        cfg = SamplingConfig(n_samples=128, seed=11)
        a = sample_parameters(_specs(), cfg)
        b = sample_parameters(_specs(), cfg)
        assert np.array_equal(a.matrix, b.matrix)

    def test_different_seed_changes_samples(self):
        a = sample_parameters(_specs(), SamplingConfig(n_samples=128, seed=1))
        b = sample_parameters(_specs(), SamplingConfig(n_samples=128, seed=2))
        assert not np.array_equal(a.matrix, b.matrix)

    def test_spec_order_independence(self):
        forward = _specs()
        reversed_specs = list(reversed(_specs()))
        cfg = SamplingConfig(n_samples=64, seed=5)
        a = sample_parameters(forward, cfg)
        b = sample_parameters(reversed_specs, cfg)
        assert a.names == b.names
        assert np.array_equal(a.matrix, b.matrix)

    @pytest.mark.parametrize("method", list(SamplingMethod))
    def test_samples_within_bounds(self, method: SamplingMethod):
        specs = _specs()
        samples = sample_parameters(specs, SamplingConfig(n_samples=2000, seed=3, method=method))
        for spec in specs:
            col = samples.column(spec.name)
            assert col.min() >= spec.low - 1e-9
            assert col.max() <= spec.high + 1e-9

    def test_degenerate_parameter_is_constant(self):
        specs = [
            ParameterSpec(name="fixed", low=4.0, central=4.0, high=4.0),
            ParameterSpec(name="varies", low=0.0, central=1.0, high=2.0),
        ]
        samples = sample_parameters(specs, SamplingConfig(n_samples=100, seed=0))
        assert np.allclose(samples.column("fixed"), 4.0)
        assert samples.column("varies").std() > 0

    def test_uniform_degenerate_is_constant(self):
        spec = ParameterSpec(name="u", low=2.0, central=2.0, high=2.0, distribution=Distribution.UNIFORM)
        samples = sample_parameters([spec], SamplingConfig(n_samples=50, seed=0))
        assert np.allclose(samples.column("u"), 2.0)

    def test_triangular_mean_approximates_third_of_sum(self):
        # E[Triangular(a, c, b)] = (a + c + b) / 3.
        spec = ParameterSpec(name="t", low=0.0, central=1.0, high=3.0)
        samples = sample_parameters([spec], SamplingConfig(n_samples=20000, seed=9))
        assert samples.column("t").mean() == pytest.approx((0.0 + 1.0 + 3.0) / 3.0, abs=0.05)

    def test_uniform_mean_approximates_midpoint(self):
        spec = ParameterSpec(name="u", low=0.0, central=1.0, high=2.0, distribution=Distribution.UNIFORM)
        samples = sample_parameters([spec], SamplingConfig(n_samples=20000, seed=9))
        assert samples.column("u").mean() == pytest.approx(1.0, abs=0.05)

    def test_lhs_stratifies_each_bin_once(self):
        # With n samples and LHS, each of the n equal-probability strata holds
        # exactly one sample (verified on a uniform marginal for clarity).
        spec = ParameterSpec(name="u", low=0.0, central=1.0, high=2.0, distribution=Distribution.UNIFORM)
        n = 200
        samples = sample_parameters([spec], SamplingConfig(n_samples=n, seed=4, method=SamplingMethod.LATIN_HYPERCUBE))
        col = samples.column("u")
        bins = np.floor((col - spec.low) / (spec.high - spec.low) * n).astype(int)
        bins = np.clip(bins, 0, n - 1)
        assert sorted(bins.tolist()) == list(range(n))

    def test_lhs_more_uniform_than_independent(self):
        # LHS marginal coverage should be at least as even as independent MC:
        # the max gap between sorted draws is smaller.
        spec = ParameterSpec(name="u", low=0.0, central=1.0, high=2.0, distribution=Distribution.UNIFORM)
        cfg_kwargs = dict(n_samples=500, seed=7)
        lhs = np.sort(sample_parameters([spec], SamplingConfig(method=SamplingMethod.LATIN_HYPERCUBE, **cfg_kwargs)).column("u"))
        mc = np.sort(sample_parameters([spec], SamplingConfig(method=SamplingMethod.INDEPENDENT, **cfg_kwargs)).column("u"))
        assert np.diff(lhs).max() < np.diff(mc).max()


class TestParameterSamples:
    def test_column_unknown_name_raises(self):
        samples = sample_parameters(_specs(), SamplingConfig(n_samples=8))
        with pytest.raises(KeyError, match="unknown parameter"):
            samples.column("missing")

    def test_as_dicts_yields_all_rows(self):
        samples = sample_parameters(_specs(), SamplingConfig(n_samples=10))
        rows = list(samples.as_dicts())
        assert len(rows) == 10
        assert all(set(row) == {"alpha", "threshold"} for row in rows)
        # Row values match the matrix.
        assert rows[0]["alpha"] == pytest.approx(samples.matrix[0, 0])

    def test_provenance_ids(self):
        samples = sample_parameters(_specs(), SamplingConfig(n_samples=32))
        ids = samples.provenance_ids()
        assert "uncertainty.n_samples:32" in ids
        assert "uncertainty.parameters:alpha;threshold" in ids

    def test_is_frozen(self):
        samples = sample_parameters(_specs(), SamplingConfig(n_samples=8))
        with pytest.raises(Exception):  # noqa: B017 - dataclass FrozenInstanceError
            samples.names = ()  # type: ignore[misc]

    def test_matrix_is_read_only(self):
        samples = sample_parameters(_specs(), SamplingConfig(n_samples=8))
        with pytest.raises(ValueError, match="read-only"):
            samples.matrix[0, 0] = 0.0
        with pytest.raises(ValueError, match="read-only"):
            samples.column("alpha")[0] = 0.0


def _imports_engine(tree: ast.AST) -> bool:
    """True if any import node in ``tree`` references ``wealthlens_sim.engine``."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name == "wealthlens_sim.engine" or a.name.startswith("wealthlens_sim.engine.") for a in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "wealthlens_sim.engine" or module.startswith("wealthlens_sim.engine."):
                return True
            # Catch the aliased ``from wealthlens_sim import engine`` form too.
            if module == "wealthlens_sim" and any(a.name == "engine" for a in node.names):
                return True
    return False


def test_uncertainty_package_does_not_import_engine() -> None:
    """Groundwork guard: nothing in the uncertainty package imports the engine.

    Wiring is a later, separately reviewed PR; keeping the feature OFF by
    construction means default engine behaviour is unchanged. AST-parse *every*
    module in the package (not just ``sampling.py``, and not a naive substring
    scan) so ``__init__``-level imports and the dotted / ``from wealthlens_sim
    import engine`` forms are all caught.
    """
    import wealthlens_sim.uncertainty as pkg

    pkg_dir = Path(pkg.__file__).parent
    offenders = [
        path.name
        for path in sorted(pkg_dir.glob("*.py"))
        if _imports_engine(ast.parse(path.read_text(encoding="utf-8")))
    ]
    assert not offenders, f"uncertainty package must not import the engine yet: {offenders}"
