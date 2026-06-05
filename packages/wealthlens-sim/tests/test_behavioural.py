"""Tests for the reduced-form behavioural-response layer (Wave 13+)."""

from __future__ import annotations

import math

import pytest

from wealthlens_sim.assumptions.schema import RangeValue
from wealthlens_sim.behavioural import (
    BehaviouralChannel,
    BehaviouralResponse,
    revenue_response_factor,
)


class TestRevenueResponseFactor:
    def test_no_channels_is_identity(self) -> None:
        result = revenue_response_factor([], rate_change_pp=2.0)
        assert result.factor == 1.0
        assert result.channel_factors == ()

    def test_zero_rate_change_is_identity(self) -> None:
        ch = BehaviouralChannel(name="migration", semi_elasticity=-0.04)
        result = revenue_response_factor([ch], rate_change_pp=0.0)
        assert result.factor == 1.0

    def test_single_negative_elasticity_erodes_revenue(self) -> None:
        # ε=-0.04 per pp, +1pp wealth tax -> base/revenue * (1 - 0.04) = 0.96.
        ch = BehaviouralChannel(name="non_dom", semi_elasticity=-0.04)
        result = revenue_response_factor([ch], rate_change_pp=1.0)
        assert result.factor == pytest.approx(0.96)
        assert result.channel_factors == (("non_dom", pytest.approx(0.96)),)
        assert result.clamped is False

    def test_channels_compose_multiplicatively(self) -> None:
        chans = [
            BehaviouralChannel(name="non_dom", semi_elasticity=-0.04),
            BehaviouralChannel(name="dom_emig", semi_elasticity=-0.02),
        ]
        result = revenue_response_factor(chans, rate_change_pp=1.0)
        assert result.factor == pytest.approx(0.96 * 0.98)

    def test_positive_elasticity_allowed(self) -> None:
        ch = BehaviouralChannel(name="broaden", semi_elasticity=0.03)
        result = revenue_response_factor([ch], rate_change_pp=2.0)
        assert result.factor == pytest.approx(1.06)

    def test_factor_clamped_at_zero(self) -> None:
        # An extreme elasticity*rate would drive the factor negative; clamp to 0.
        ch = BehaviouralChannel(name="extreme", semi_elasticity=-0.8)
        result = revenue_response_factor([ch], rate_change_pp=2.0)  # 1 + (-1.6) = -0.6
        assert result.factor == 0.0
        assert result.clamped is True
        assert result.channel_factors == (("extreme", 0.0),)

    def test_even_over_eroding_channels_do_not_mask(self) -> None:
        # Two channels each over-eroding (raw factor -0.6). WITHOUT per-channel clamping
        # the product would be a spurious POSITIVE (-0.6 * -0.6 = 0.36), masking the
        # over-response. Per-channel clamping makes each 0 -> product 0, clamped True.
        chans = [
            BehaviouralChannel(name="a", semi_elasticity=-0.8),
            BehaviouralChannel(name="b", semi_elasticity=-0.8),
        ]
        result = revenue_response_factor(chans, rate_change_pp=2.0)  # each raw = -0.6
        assert result.factor == 0.0
        assert result.clamped is True
        assert result.channel_factors == (("a", 0.0), ("b", 0.0))

    def test_mixed_one_clamped_one_normal(self) -> None:
        # One over-eroding channel (clamped to 0) makes the whole product 0, regardless
        # of a healthy channel — a fully-eroded base stays fully eroded.
        chans = [
            BehaviouralChannel(name="ok", semi_elasticity=-0.04),  # raw 0.96
            BehaviouralChannel(name="extreme", semi_elasticity=-0.8),  # raw -0.6 -> 0
        ]
        result = revenue_response_factor(chans, rate_change_pp=2.0)
        assert result.factor == 0.0
        assert result.clamped is True

    def test_deterministic(self) -> None:
        chans = [BehaviouralChannel(name="a", semi_elasticity=-0.04, source_id="s")]
        r1 = revenue_response_factor(chans, rate_change_pp=1.5)
        r2 = revenue_response_factor(chans, rate_change_pp=1.5)
        assert r1 == r2

    def test_non_finite_rate_change_rejected(self) -> None:
        ch = BehaviouralChannel(name="a", semi_elasticity=-0.04)
        with pytest.raises(ValueError, match="rate_change_pp must be finite"):
            revenue_response_factor([ch], rate_change_pp=math.inf)


class TestBehaviouralChannel:
    def test_non_finite_elasticity_rejected(self) -> None:
        with pytest.raises(ValueError, match="must be finite"):
            BehaviouralChannel(name="a", semi_elasticity=math.nan)

    def test_from_range_value_central_default(self) -> None:
        rv = RangeValue(type="range", low=-0.01, central=-0.04, high=-0.10)
        ch = BehaviouralChannel.from_range_value("non_dom", rv, source_id="advani2020")
        assert ch.semi_elasticity == pytest.approx(-0.04)
        assert ch.source_id == "advani2020"

    def test_from_range_value_low_and_high(self) -> None:
        rv = RangeValue(type="range", low=-0.01, central=-0.04, high=-0.10)
        assert BehaviouralChannel.from_range_value("x", rv, point="low").semi_elasticity == pytest.approx(-0.01)
        assert BehaviouralChannel.from_range_value("x", rv, point="high").semi_elasticity == pytest.approx(-0.10)

    def test_from_range_value_bad_point(self) -> None:
        rv = RangeValue(type="range", low=-0.01, central=-0.04, high=-0.10)
        with pytest.raises(ValueError, match="point must be"):
            BehaviouralChannel.from_range_value("x", rv, point="median")

    @pytest.mark.parametrize("bad_name", ["a;b", "mig@x", "a=b", "a b", "a,b", "a(b)"])
    def test_name_with_provenance_delimiter_rejected(self, bad_name: str) -> None:
        # The channel tag is name=<eps>@source joined with ';' — delimiters in name/
        # source_id would make the provenance grammar non-injective (mirrors ParameterSpec).
        with pytest.raises(ValueError, match="provenance delimiters"):
            BehaviouralChannel(name=bad_name, semi_elasticity=-0.04)

    def test_source_id_with_delimiter_rejected(self) -> None:
        with pytest.raises(ValueError, match="provenance delimiters"):
            BehaviouralChannel(name="ok", semi_elasticity=-0.04, source_id="x@y")

    def test_source_id_dash_sentinel_rejected(self) -> None:
        # '-' is the absent-source sentinel rendered as '@-'; an explicit '-' would be
        # indistinguishable from None.
        with pytest.raises(ValueError, match="absent-source sentinel"):
            BehaviouralChannel(name="ok", semi_elasticity=-0.04, source_id="-")


class TestProvenance:
    def test_provenance_ids_capture_run(self) -> None:
        chans = [BehaviouralChannel(name="non_dom", semi_elasticity=-0.04, source_id="advani2020")]
        result = revenue_response_factor(chans, rate_change_pp=1.0)
        ids = result.provenance_ids
        assert "behavioural.method:first_order_reduced_form" in ids
        assert any(s.startswith("behavioural.rate_change_pp:") for s in ids)
        assert any(s.startswith("behavioural.factor:") for s in ids)
        assert "behavioural.channel:non_dom=-0.04@advani2020" in ids

    def test_provenance_absent_source_renders_dash(self) -> None:
        chans = [BehaviouralChannel(name="x", semi_elasticity=-0.02)]
        result = revenue_response_factor(chans, rate_change_pp=1.0)
        assert "behavioural.channel:x=-0.02@-" in result.provenance_ids

    def test_result_is_immutable(self) -> None:
        result = revenue_response_factor([], rate_change_pp=1.0)
        assert isinstance(result, BehaviouralResponse)
        with pytest.raises(Exception):  # noqa: B017 - frozen dataclass raises FrozenInstanceError
            result.factor = 0.5  # type: ignore[misc]
