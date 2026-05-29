"""Tests for the baselines registry loader and schema."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from wealthlens_sim.schema import (
    BaselinesRegistry,
    LegalStatus,
    PolicyBaseline,
    load_baselines,
)

CURRENT_LAW_ENTRY = {
    "id": "cgt-rates-2026",
    "area": "Capital Gains Tax",
    "status": "current_law",
    "effective_date": "2026-04-06",
    "description": "CGT rates of 18% and 24%.",
    "wealthlens_treatment": "Current-law baseline",
    "source_url": "https://www.gov.uk/capital-gains-tax/rates",
    "notes": "Family C baseline parameter.",
}

ENACTED_FUTURE_ENTRY = {
    "id": "pension-iht-2027",
    "area": "Inheritance Tax",
    "status": "enacted_future",
    "effective_date": "2027-04-06",
    "description": "IHT on unused pension funds from 6 April 2027.",
    "wealthlens_treatment": "Future-law baseline scenario",
    "source_url": "https://www.gov.uk/government/publications/inheritance-tax-on-pensions",
}

HYPOTHETICAL_ENTRY = {
    "id": "annual-net-wealth-tax",
    "area": "Annual net wealth tax",
    "status": "hypothetical",
    "effective_date": None,
    "description": "Hypothetical annual net wealth tax.",
    "wealthlens_treatment": "Counterfactual scenario family (Family A)",
    "source_url": None,
}

CONSULTATION_ENTRY = {
    "id": "hvcts-2028",
    "area": "Property taxation",
    "status": "consultation_stage",
    "effective_date": "2028-04-01",
    "description": "HVCTS on properties £2m+ in England.",
    "wealthlens_treatment": "Consultation-sensitive baseline",
    "source_url": "https://www.gov.uk/government/consultations/high-value-council-tax-surcharge",
}


class TestPolicyBaseline:
    def test_current_law(self):
        b = PolicyBaseline.model_validate(CURRENT_LAW_ENTRY)
        assert b.status == LegalStatus.CURRENT_LAW
        assert b.effective_date is not None
        assert b.effective_date.year == 2026

    def test_hypothetical_null_date(self):
        b = PolicyBaseline.model_validate(HYPOTHETICAL_ENTRY)
        assert b.effective_date is None
        assert b.source_url is None

    def test_id_pattern_enforced(self):
        bad = {**CURRENT_LAW_ENTRY, "id": "BAD ID!"}
        with pytest.raises(ValidationError, match="id"):
            PolicyBaseline.model_validate(bad)

    def test_invalid_status_rejected(self):
        bad = {**CURRENT_LAW_ENTRY, "status": "draft"}
        with pytest.raises(ValidationError):
            PolicyBaseline.model_validate(bad)

    def test_extra_fields_rejected(self):
        bad = {**CURRENT_LAW_ENTRY, "family": "C"}
        with pytest.raises(ValidationError, match="Extra inputs"):
            PolicyBaseline.model_validate(bad)

    def test_notes_default_empty(self):
        b = PolicyBaseline.model_validate(ENACTED_FUTURE_ENTRY)
        assert b.notes == ""


class TestBaselinesRegistry:
    def _make_registry(self, entries: list[dict]) -> BaselinesRegistry:
        return BaselinesRegistry.model_validate({
            "modelling_date": "2026-05-21",
            "baselines": entries,
        })

    def test_empty_registry(self):
        reg = self._make_registry([])
        assert len(reg.baselines) == 0
        assert reg.modelling_date.year == 2026

    def test_get_by_id(self):
        reg = self._make_registry([CURRENT_LAW_ENTRY, HYPOTHETICAL_ENTRY])
        found = reg.get("cgt-rates-2026")
        assert found is not None
        assert found.area == "Capital Gains Tax"

    def test_get_missing_returns_none(self):
        reg = self._make_registry([CURRENT_LAW_ENTRY])
        assert reg.get("nonexistent") is None

    def test_by_status(self):
        reg = self._make_registry([
            CURRENT_LAW_ENTRY, ENACTED_FUTURE_ENTRY, HYPOTHETICAL_ENTRY, CONSULTATION_ENTRY
        ])
        current = reg.by_status(LegalStatus.CURRENT_LAW)
        assert len(current) == 1
        hypo = reg.by_status(LegalStatus.HYPOTHETICAL)
        assert len(hypo) == 1

    def test_by_area(self):
        reg = self._make_registry([CURRENT_LAW_ENTRY, ENACTED_FUTURE_ENTRY])
        iht = reg.by_area("Inheritance Tax")
        assert len(iht) == 1
        cgt = reg.by_area("Capital Gains Tax")
        assert len(cgt) == 1

    def test_round_trip(self):
        reg = self._make_registry([CURRENT_LAW_ENTRY, HYPOTHETICAL_ENTRY])
        data = reg.model_dump()
        reg2 = BaselinesRegistry.model_validate(data)
        assert len(reg2.baselines) == 2
        assert reg2.modelling_date.month == 5

    def test_duplicate_ids_rejected(self):
        with pytest.raises(ValidationError, match="Duplicate baseline id"):
            self._make_registry([CURRENT_LAW_ENTRY, CURRENT_LAW_ENTRY])

    def test_modelling_date_required(self):
        with pytest.raises(ValidationError):
            BaselinesRegistry.model_validate({"baselines": []})


class TestLoader:
    def test_load_empty_with_date(self, tmp_path: Path):
        data = {"modelling_date": "2026-05-21", "baselines": []}
        p = tmp_path / "empty_baselines.yml"
        p.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
        reg = load_baselines(p)
        assert isinstance(reg, BaselinesRegistry)
        assert len(reg.baselines) == 0

    def test_load_from_path(self, tmp_path: Path):
        data = {
            "modelling_date": "2026-05-21",
            "baselines": [CURRENT_LAW_ENTRY, CONSULTATION_ENTRY],
        }
        p = tmp_path / "test_baselines.yml"
        p.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
        reg = load_baselines(p)
        assert len(reg.baselines) == 2

    def test_load_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_baselines(tmp_path / "nonexistent.yml")

    def test_load_empty_file(self, tmp_path: Path):
        p = tmp_path / "empty.yml"
        p.write_text("", encoding="utf-8")
        with pytest.raises(ValueError, match="empty"):
            load_baselines(p)

    def test_load_invalid_schema_raises(self, tmp_path: Path):
        data = {"modelling_date": "2026-05-21", "baselines": [{"id": "bad"}]}
        p = tmp_path / "bad.yml"
        p.write_text(yaml.dump(data), encoding="utf-8")
        with pytest.raises(ValidationError):
            load_baselines(p)
