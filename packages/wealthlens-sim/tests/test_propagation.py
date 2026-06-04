"""Tests for the Monte-Carlo propagation layer (Wave 13)."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pytest

from wealthlens_sim.top_tail.types import Interval
from wealthlens_sim.uncertainty import (
    Distribution,
    ParameterSamples,
    ParameterSpec,
    PropagationResult,
    SamplingConfig,
    SamplingMethod,
    propagate,
    sample_parameters,
)


def _specs() -> list[ParameterSpec]:
    return [
        ParameterSpec(name="alpha", low=2.0, central=2.5, high=3.0),
        ParameterSpec(name="threshold", low=1.0, central=1.0, high=2.0, distribution=Distribution.UNIFORM),
    ]


def _samples(n: int = 256, seed: int = 0) -> ParameterSamples:
    return sample_parameters(_specs(), SamplingConfig(n_samples=n, seed=seed, method=SamplingMethod.INDEPENDENT))


class TestPropagate:
    def test_linear_evaluate_matches_quantiles(self):
        samples = _samples()
        # evaluate returns one parameter unchanged, so the output distribution is
        # exactly that column and the band must equal NumPy's quantiles of it.
        result = propagate(samples, lambda p: p["alpha"])
        col = samples.column("alpha")
        assert result.interval.low == pytest.approx(float(np.quantile(col, 0.05)))
        assert result.interval.central == pytest.approx(float(np.median(col)))
        assert result.interval.high == pytest.approx(float(np.quantile(col, 0.95)))
        assert result.mean == pytest.approx(float(np.mean(col)))
        assert result.std == pytest.approx(float(np.std(col)))
        assert result.n_samples == 256

    def test_interval_ordering_holds(self):
        result = propagate(_samples(), lambda p: p["alpha"] * 1000.0 - p["threshold"])
        assert result.interval.low <= result.interval.central <= result.interval.high

    def test_constant_evaluate_is_degenerate(self):
        result = propagate(_samples(), lambda _p: 42.0)
        assert result.interval == Interval(low=42.0, central=42.0, high=42.0)
        assert result.std == pytest.approx(0.0)
        assert result.mean == pytest.approx(42.0)

    def test_custom_quantiles(self):
        samples = _samples()
        result = propagate(samples, lambda p: p["alpha"], lower_quantile=0.25, upper_quantile=0.75)
        col = samples.column("alpha")
        assert result.interval.low == pytest.approx(float(np.quantile(col, 0.25)))
        assert result.interval.high == pytest.approx(float(np.quantile(col, 0.75)))

    def test_median_boundary_quantiles(self):
        # lower=upper=0.5 collapses the band onto the median (still a valid Interval).
        result = propagate(_samples(), lambda p: p["alpha"], lower_quantile=0.5, upper_quantile=0.5)
        assert result.interval.low == pytest.approx(result.interval.central)
        assert result.interval.high == pytest.approx(result.interval.central)

    @pytest.mark.parametrize(
        ("lo", "hi"),
        [(0.6, 0.9), (0.1, 0.4), (-0.1, 0.9), (0.1, 1.1), (0.9, 0.1)],
    )
    def test_rejects_bad_quantiles(self, lo: float, hi: float):
        with pytest.raises(ValueError, match="lower_quantile"):
            propagate(_samples(), lambda p: p["alpha"], lower_quantile=lo, upper_quantile=hi)

    def test_rejects_non_finite_output(self):
        def evaluate(p: Mapping[str, float]) -> float:
            return float("inf") if p["alpha"] > 2.5 else p["alpha"]

        with pytest.raises(ValueError, match="non-finite"):
            propagate(_samples(), evaluate)

    def test_determinism(self):
        a = propagate(_samples(seed=7), lambda p: p["alpha"] + p["threshold"])
        b = propagate(_samples(seed=7), lambda p: p["alpha"] + p["threshold"])
        assert a.provenance_ids == b.provenance_ids
        assert np.array_equal(a.outputs, b.outputs)
        assert a.interval == b.interval

    def test_provenance_extends_sample_block(self):
        samples = _samples()
        result = propagate(samples, lambda p: p["alpha"], lower_quantile=0.05, upper_quantile=0.95)
        # Every sample-block id is preserved, plus the centre and quantile tags.
        for sid in samples.provenance_ids():
            assert sid in result.provenance_ids
        assert "uncertainty.central:median" in result.provenance_ids
        assert "uncertainty.quantiles:0.05;0.95" in result.provenance_ids

    def test_outputs_row_aligned_and_read_only(self):
        samples = _samples(n=32)
        result = propagate(samples, lambda p: p["alpha"])
        assert result.outputs.shape == (32,)
        assert np.array_equal(result.outputs, samples.column("alpha"))
        with pytest.raises(ValueError, match="read-only"):
            result.outputs[0] = 0.0

    def test_result_is_frozen(self):
        from dataclasses import FrozenInstanceError

        result = propagate(_samples(n=8), lambda p: p["alpha"])
        with pytest.raises(FrozenInstanceError):
            result.mean = 0.0  # type: ignore[misc]

    def test_returns_propagation_result(self):
        result = propagate(_samples(n=8), lambda p: p["alpha"])
        assert isinstance(result, PropagationResult)
