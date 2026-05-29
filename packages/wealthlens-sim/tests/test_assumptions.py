"""Tests for the assumption registry loader and schema."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from wealthlens_sim.assumptions import (
    Assumption,
    AssumptionRegistry,
    FlagValue,
    PointValue,
    RangeValue,
    ScheduleValue,
    TransferabilityScore,
    load_assumptions,
)
from wealthlens_sim.schema import LegalStatus

POINT_ENTRY = {
    "assumption_id": "toptail.data_quality.was_response_rate.v1",
    "domain": "top-tail",
    "value_or_distribution": {"type": "point", "value": 0.41},
    "source": "ONS WAS quality report",
    "transferability_score": "high",
    "valid_range": "rate in [0.30, 0.60]",
    "applies_to": "all families",
    "last_reviewed": "2026-05-23",
}

RANGE_ENTRY = {
    "assumption_id": "toptail.pareto_alpha.overall.v1",
    "domain": "top-tail",
    "value_or_distribution": {"type": "range", "low": 1.3, "central": 1.5, "high": 1.8},
    "source": "Vermeulen (2018)",
    "transferability_score": "medium",
    "valid_range": "alpha in [1.1, 2.5]",
    "applies_to": "all families",
    "last_reviewed": "2026-05-23",
}

NEGATIVE_RANGE_ENTRY = {
    "assumption_id": "behaviour.migration.non_dom_stock_elasticity.v1",
    "domain": "migration",
    "value_or_distribution": {"type": "range", "low": -0.01, "central": -0.04, "high": -0.10},
    "source": "Advani & Summers (2020)",
    "transferability_score": "low",
    "valid_range": "elasticity in [-0.20, 0.0]",
    "applies_to": "Family A, Family B",
    "last_reviewed": "2026-05-23",
}

SCHEDULE_ENTRY = {
    "assumption_id": "policy.cgt.rates_2026.v1",
    "domain": "capital-gains",
    "legal_status": "current_law",
    "value_or_distribution": {
        "type": "schedule",
        "rates": {"basic_rate": 18, "higher_rate": 24},
    },
    "source": "GOV.UK CGT rates page",
    "transferability_score": "high",
    "valid_range": "n/a",
    "applies_to": "Family C baseline",
    "last_reviewed": "2026-05-23",
}

FLAG_ENTRY = {
    "assumption_id": "policy.iht.pension_inclusion_2027.v1",
    "domain": "transfer-tax",
    "legal_status": "enacted_future",
    "value_or_distribution": {"type": "flag", "value": 1},
    "source": "Finance Act 2026",
    "transferability_score": "high",
    "valid_range": "n/a",
    "applies_to": "Family D baseline",
    "last_reviewed": "2026-05-23",
}


class TestValueDistribution:
    def test_point_value(self):
        a = Assumption.model_validate(POINT_ENTRY)
        assert isinstance(a.value_or_distribution, PointValue)
        assert a.value_or_distribution.value == 0.41

    def test_range_value(self):
        a = Assumption.model_validate(RANGE_ENTRY)
        assert isinstance(a.value_or_distribution, RangeValue)
        assert a.value_or_distribution.central == 1.5

    def test_range_non_monotonic_rejected(self):
        bad = {**RANGE_ENTRY, "value_or_distribution": {"type": "range", "low": 2.0, "central": 1.5, "high": 1.8}}
        with pytest.raises(ValidationError, match="monotonically ordered"):
            Assumption.model_validate(bad)

    def test_negative_range_accepted(self):
        a = Assumption.model_validate(NEGATIVE_RANGE_ENTRY)
        assert isinstance(a.value_or_distribution, RangeValue)
        assert a.value_or_distribution.low == -0.01
        assert a.value_or_distribution.high == -0.10

    def test_schedule_value(self):
        a = Assumption.model_validate(SCHEDULE_ENTRY)
        assert isinstance(a.value_or_distribution, ScheduleValue)

    def test_empty_schedule_rejected(self):
        bad = {**SCHEDULE_ENTRY, "value_or_distribution": {"type": "schedule"}}
        with pytest.raises(ValidationError, match="rate/band field"):
            Assumption.model_validate(bad)

    def test_flag_value(self):
        a = Assumption.model_validate(FLAG_ENTRY)
        assert isinstance(a.value_or_distribution, FlagValue)
        assert a.value_or_distribution.value == 1

    def test_flag_rejects_out_of_range(self):
        bad = {**FLAG_ENTRY, "value_or_distribution": {"type": "flag", "value": 2}}
        with pytest.raises(ValidationError):
            Assumption.model_validate(bad)


class TestAssumption:
    def test_id_pattern_enforced(self):
        bad = {**POINT_ENTRY, "assumption_id": "BAD ID!"}
        with pytest.raises(ValidationError, match="assumption_id"):
            Assumption.model_validate(bad)

    def test_id_rejects_double_dots(self):
        bad = {**POINT_ENTRY, "assumption_id": "abc..def.v1"}
        with pytest.raises(ValidationError, match="assumption_id"):
            Assumption.model_validate(bad)

    def test_id_rejects_leading_zero_version(self):
        bad = {**POINT_ENTRY, "assumption_id": "abc.def.v01"}
        with pytest.raises(ValidationError, match="assumption_id"):
            Assumption.model_validate(bad)

    def test_transferability_enum(self):
        a = Assumption.model_validate(POINT_ENTRY)
        assert a.transferability_score == TransferabilityScore.HIGH

    def test_invalid_transferability_rejected(self):
        bad = {**POINT_ENTRY, "transferability_score": "unknown"}
        with pytest.raises(ValidationError):
            Assumption.model_validate(bad)

    def test_extra_fields_rejected(self):
        bad = {**POINT_ENTRY, "surprise_field": 42}
        with pytest.raises(ValidationError, match="Extra inputs"):
            Assumption.model_validate(bad)

    def test_legal_status_uses_enum(self):
        a = Assumption.model_validate(POINT_ENTRY)
        assert a.legal_status is None
        a2 = Assumption.model_validate(SCHEDULE_ENTRY)
        assert a2.legal_status == LegalStatus.CURRENT_LAW

    def test_invalid_legal_status_rejected(self):
        bad = {**SCHEDULE_ENTRY, "legal_status": "curent_law"}
        with pytest.raises(ValidationError):
            Assumption.model_validate(bad)

    def test_last_reviewed_parsed_as_date(self):
        a = Assumption.model_validate(POINT_ENTRY)
        assert a.last_reviewed.year == 2026
        assert a.last_reviewed.month == 5

    def test_notes_default_empty(self):
        a = Assumption.model_validate(POINT_ENTRY)
        assert a.notes == ""


class TestAssumptionRegistry:
    def test_empty_registry(self):
        reg = AssumptionRegistry(assumptions=[])
        assert len(reg.assumptions) == 0

    def test_get_by_id(self):
        reg = AssumptionRegistry.model_validate({"assumptions": [POINT_ENTRY, RANGE_ENTRY]})
        found = reg.get("toptail.pareto_alpha.overall.v1")
        assert found is not None
        assert found.domain == "top-tail"

    def test_get_missing_returns_none(self):
        reg = AssumptionRegistry.model_validate({"assumptions": [POINT_ENTRY]})
        assert reg.get("nonexistent.v1") is None

    def test_by_domain(self):
        reg = AssumptionRegistry.model_validate(
            {"assumptions": [POINT_ENTRY, RANGE_ENTRY, SCHEDULE_ENTRY]}
        )
        top_tail = reg.by_domain("top-tail")
        assert len(top_tail) == 2

    def test_by_transferability(self):
        reg = AssumptionRegistry.model_validate(
            {"assumptions": [POINT_ENTRY, RANGE_ENTRY, SCHEDULE_ENTRY]}
        )
        high = reg.by_transferability(TransferabilityScore.HIGH)
        assert len(high) == 2
        medium = reg.by_transferability(TransferabilityScore.MEDIUM)
        assert len(medium) == 1

    def test_duplicate_ids_rejected(self):
        with pytest.raises(ValidationError, match="Duplicate assumption_id"):
            AssumptionRegistry.model_validate({"assumptions": [POINT_ENTRY, POINT_ENTRY]})

    def test_round_trip(self):
        reg = AssumptionRegistry.model_validate(
            {"assumptions": [POINT_ENTRY, RANGE_ENTRY, FLAG_ENTRY]}
        )
        data = reg.model_dump()
        reg2 = AssumptionRegistry.model_validate(data)
        assert len(reg2.assumptions) == 3
        assert reg2.get("policy.iht.pension_inclusion_2027.v1") is not None


class TestLoader:
    def test_load_empty_registry(self, tmp_path: Path):
        data = {"assumptions": []}
        p = tmp_path / "empty.yml"
        p.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
        reg = load_assumptions(p)
        assert isinstance(reg, AssumptionRegistry)
        assert len(reg.assumptions) == 0

    def test_load_from_path(self, tmp_path: Path):
        data = {"assumptions": [POINT_ENTRY, RANGE_ENTRY]}
        p = tmp_path / "test_assumptions.yml"
        p.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
        reg = load_assumptions(p)
        assert len(reg.assumptions) == 2

    def test_load_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_assumptions(tmp_path / "nonexistent.yml")

    def test_load_empty_file_raises(self, tmp_path: Path):
        p = tmp_path / "empty.yml"
        p.write_text("", encoding="utf-8")
        with pytest.raises(ValueError, match="empty or contains only comments"):
            load_assumptions(p)

    def test_load_invalid_schema_raises(self, tmp_path: Path):
        data = {"assumptions": [{"assumption_id": "bad", "domain": "test"}]}
        p = tmp_path / "bad.yml"
        p.write_text(yaml.dump(data), encoding="utf-8")
        with pytest.raises(ValidationError):
            load_assumptions(p)

    def test_load_comment_only_file_raises(self, tmp_path: Path):
        p = tmp_path / "comments.yml"
        p.write_text("# just a comment\n", encoding="utf-8")
        with pytest.raises(ValueError, match="empty or contains only comments"):
            load_assumptions(p)

    def test_load_with_explicit_path(self, tmp_path: Path):
        """Explicit path bypasses registry discovery -- no parents[4] dependency."""
        data = {"assumptions": [POINT_ENTRY]}
        p = tmp_path / "custom" / "assumptions.yml"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
        reg = load_assumptions(p)
        assert len(reg.assumptions) == 1
        assert reg.assumptions[0].assumption_id == POINT_ENTRY["assumption_id"]


class TestScheduleValueValidation:
    """Tests for ScheduleValue extra-field type validation."""

    def test_schedule_accepts_numeric_extra(self):
        entry = {**SCHEDULE_ENTRY, "value_or_distribution": {"type": "schedule", "rate": 0.18}}
        a = Assumption.model_validate(entry)
        assert isinstance(a.value_or_distribution, ScheduleValue)

    def test_schedule_accepts_string_extra(self):
        entry = {
            **SCHEDULE_ENTRY,
            "value_or_distribution": {"type": "schedule", "boundary_convention": "lower", "rate": 0.18},
        }
        a = Assumption.model_validate(entry)
        assert isinstance(a.value_or_distribution, ScheduleValue)

    def test_schedule_accepts_dict_extra(self):
        entry = {
            **SCHEDULE_ENTRY,
            "value_or_distribution": {"type": "schedule", "rates": {"basic_rate": 18, "higher_rate": 24}},
        }
        a = Assumption.model_validate(entry)
        assert isinstance(a.value_or_distribution, ScheduleValue)

    def test_schedule_accepts_band_list(self):
        entry = {
            **SCHEDULE_ENTRY,
            "value_or_distribution": {
                "type": "schedule",
                "bands": [
                    {"threshold": 0, "rate": 0.0},
                    {"threshold": 12570, "rate": 0.20},
                    {"threshold": 50270, "rate": 0.40},
                ],
            },
        }
        a = Assumption.model_validate(entry)
        assert isinstance(a.value_or_distribution, ScheduleValue)

    def test_schedule_rejects_non_dict_band_list(self):
        entry = {
            **SCHEDULE_ENTRY,
            "value_or_distribution": {
                "type": "schedule",
                "bands": [42, 99],
            },
        }
        with pytest.raises(ValidationError, match="band entries must be dicts"):
            Assumption.model_validate(entry)

    def test_schedule_rejects_unsupported_type(self):
        entry = {
            **SCHEDULE_ENTRY,
            "value_or_distribution": {
                "type": "schedule",
                "bad_field": (1, 2, 3),
            },
        }
        with pytest.raises(ValidationError, match="unsupported type"):
            Assumption.model_validate(entry)
