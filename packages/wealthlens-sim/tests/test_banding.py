"""Tests for shared progressive-rate banding infrastructure."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wealthlens_sim.reforms._banding import RateBand, compute_banded_liability


class TestRateBand:
    def test_basic(self):
        band = RateBand(threshold=1_000_000, rate=0.01)
        assert band.threshold == 1_000_000
        assert band.rate == 0.01

    def test_frozen(self):
        band = RateBand(threshold=1_000_000, rate=0.01)
        with pytest.raises(ValidationError, match="frozen"):
            band.rate = 0.02

    def test_extra_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            RateBand(threshold=0, rate=0.01, surprise="bad")

    def test_rate_bounds(self):
        with pytest.raises(ValidationError):
            RateBand(threshold=0, rate=0)
        with pytest.raises(ValidationError):
            RateBand(threshold=0, rate=1.5)

    def test_negative_threshold_rejected(self):
        with pytest.raises(ValidationError):
            RateBand(threshold=-1, rate=0.01)


class TestComputeBandedLiability:
    def test_single_band(self):
        bands = (RateBand(threshold=10_000_000, rate=0.05),)
        assert compute_banded_liability(15_000_000, bands) == pytest.approx(250_000)

    def test_two_bands(self):
        bands = (
            RateBand(threshold=5_000_000, rate=0.03),
            RateBand(threshold=10_000_000, rate=0.05),
        )
        expected = (10_000_000 - 5_000_000) * 0.03 + (15_000_000 - 10_000_000) * 0.05
        assert compute_banded_liability(15_000_000, bands) == pytest.approx(expected)

    def test_below_first_band(self):
        bands = (RateBand(threshold=10_000_000, rate=0.05),)
        assert compute_banded_liability(5_000_000, bands) == 0.0

    def test_exactly_at_threshold(self):
        bands = (RateBand(threshold=10_000_000, rate=0.05),)
        assert compute_banded_liability(10_000_000, bands) == 0.0

    def test_zero_wealth(self):
        bands = (RateBand(threshold=0, rate=0.05),)
        assert compute_banded_liability(0, bands) == 0.0

    def test_negative_wealth(self):
        bands = (RateBand(threshold=0, rate=0.05),)
        assert compute_banded_liability(-1_000_000, bands) == 0.0

    def test_unsorted_bands(self):
        bands = (
            RateBand(threshold=10_000_000, rate=0.05),
            RateBand(threshold=5_000_000, rate=0.03),
        )
        expected = (10_000_000 - 5_000_000) * 0.03 + (15_000_000 - 10_000_000) * 0.05
        assert compute_banded_liability(15_000_000, bands) == pytest.approx(expected)

    def test_three_bands(self):
        bands = (
            RateBand(threshold=1_000_000, rate=0.01),
            RateBand(threshold=5_000_000, rate=0.03),
            RateBand(threshold=20_000_000, rate=0.05),
        )
        expected = (
            (5_000_000 - 1_000_000) * 0.01
            + (20_000_000 - 5_000_000) * 0.03
            + (30_000_000 - 20_000_000) * 0.05
        )
        assert compute_banded_liability(30_000_000, bands) == pytest.approx(expected)
