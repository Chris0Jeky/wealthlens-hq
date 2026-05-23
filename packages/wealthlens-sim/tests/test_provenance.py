"""Tests for the provenance manifest and collector."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wealthlens_sim.assumptions import AssumptionRegistry
from wealthlens_sim.provenance import (
    PipelineLayer,
    ProvenanceCollector,
    ProvenanceEntry,
    ProvenanceManifest,
    ResolvedAssumption,
)
from wealthlens_sim.schema.base import VersionTag

POINT_ASSUMPTION = {
    "assumption_id": "toptail.data_quality.was_response_rate.v1",
    "domain": "top-tail",
    "value_or_distribution": {"type": "point", "value": 0.41},
    "source": "ONS WAS quality report",
    "transferability_score": "high",
    "valid_range": "rate in [0.30, 0.60]",
    "applies_to": "all families",
    "last_reviewed": "2026-05-23",
}

RANGE_ASSUMPTION = {
    "assumption_id": "toptail.pareto_alpha.overall.v1",
    "domain": "top-tail",
    "value_or_distribution": {"type": "range", "low": 1.3, "central": 1.5, "high": 1.8},
    "source": "Vermeulen (2018)",
    "transferability_score": "medium",
    "valid_range": "alpha in [1.1, 2.5]",
    "applies_to": "all families",
    "last_reviewed": "2026-05-23",
}

SCHEDULE_ASSUMPTION = {
    "assumption_id": "policy.cgt.rates_2026.v1",
    "domain": "capital-gains",
    "legal_status": "current_law",
    "value_or_distribution": {
        "type": "schedule",
        "basic_rate": 18,
        "higher_rate": 24,
    },
    "source": "GOV.UK CGT rates page",
    "transferability_score": "high",
    "valid_range": "n/a",
    "applies_to": "Family C baseline",
    "last_reviewed": "2026-05-23",
}

FLAG_ASSUMPTION = {
    "assumption_id": "model.behavioural.use_savings_response.v1",
    "domain": "behavioural",
    "value_or_distribution": {"type": "flag", "value": 1},
    "source": "internal default",
    "transferability_score": "high",
    "valid_range": "0 or 1",
    "applies_to": "all families",
    "last_reviewed": "2026-05-23",
}


def _make_version_tag() -> VersionTag:
    return VersionTag(
        macro_baseline_version="NBS-2025",
        policy_version="uk_2026_05_21_v1",
        population_version="frs_was_v0.1",
        wealthlens_sim_version="0.1.0",
    )


def _make_registry() -> AssumptionRegistry:
    return AssumptionRegistry.model_validate({
        "assumptions": [POINT_ASSUMPTION, RANGE_ASSUMPTION, SCHEDULE_ASSUMPTION, FLAG_ASSUMPTION]
    })


class TestResolvedAssumption:
    def test_point_value(self):
        ra = ResolvedAssumption(
            assumption_id="test.v1",
            domain="test",
            resolved_value=0.41,
            source="test source",
        )
        assert ra.resolved_value == 0.41

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            ResolvedAssumption(
                assumption_id="test.v1",
                domain="test",
                resolved_value=0.41,
                source="test",
                extra_field="bad",
            )


class TestProvenanceEntry:
    def test_basic_entry(self):
        entry = ProvenanceEntry(
            output_label="Top-1% wealth share",
            layer=PipelineLayer.TOP_TAIL,
            assumption_ids=["toptail.pareto_alpha.overall.v1"],
        )
        assert entry.layer == PipelineLayer.TOP_TAIL
        assert len(entry.assumption_ids) == 1

    def test_default_empty_assumptions(self):
        entry = ProvenanceEntry(
            output_label="test",
            layer=PipelineLayer.SURVEY_INGEST,
        )
        assert entry.assumption_ids == []


class TestProvenanceManifest:
    def test_empty_manifest(self):
        manifest = ProvenanceManifest(version_tag=_make_version_tag())
        assert len(manifest.assumptions_consumed) == 0
        assert len(manifest.entries) == 0

    def test_assumption_ids_sorted(self):
        manifest = ProvenanceManifest(
            version_tag=_make_version_tag(),
            assumptions_consumed={
                "z.v1": ResolvedAssumption(assumption_id="z.v1", domain="z", resolved_value=1, source="s"),
                "a.v1": ResolvedAssumption(assumption_id="a.v1", domain="a", resolved_value=2, source="s"),
            },
        )
        assert manifest.assumption_ids() == ["a.v1", "z.v1"]

    def test_entries_by_layer(self):
        manifest = ProvenanceManifest(
            version_tag=_make_version_tag(),
            entries=[
                ProvenanceEntry(output_label="a", layer=PipelineLayer.TOP_TAIL),
                ProvenanceEntry(output_label="b", layer=PipelineLayer.POLICY_RULES),
                ProvenanceEntry(output_label="c", layer=PipelineLayer.TOP_TAIL),
            ],
        )
        top_tail = manifest.entries_by_layer(PipelineLayer.TOP_TAIL)
        assert len(top_tail) == 2
        assert manifest.entries_by_layer(PipelineLayer.REVENUE) == []

    def test_round_trip(self):
        manifest = ProvenanceManifest(
            version_tag=_make_version_tag(),
            assumptions_consumed={
                "test.v1": ResolvedAssumption(
                    assumption_id="test.v1", domain="test", resolved_value=42, source="s"
                ),
            },
            entries=[
                ProvenanceEntry(output_label="out", layer=PipelineLayer.PROVENANCE, assumption_ids=["test.v1"]),
            ],
        )
        data = manifest.model_dump()
        m2 = ProvenanceManifest.model_validate(data)
        assert len(m2.assumptions_consumed) == 1
        assert m2.version_tag.policy_version == "uk_2026_05_21_v1"

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="Extra inputs"):
            ProvenanceManifest(
                version_tag=_make_version_tag(),
                surprise="bad",
            )


class TestPipelineLayer:
    def test_all_twelve_layers(self):
        assert len(PipelineLayer) == 12


class TestProvenanceCollector:
    def test_consume_point_value(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        resolved = collector.consume("toptail.data_quality.was_response_rate.v1")
        assert resolved.resolved_value == 0.41
        assert resolved.source == "ONS WAS quality report"

    def test_consume_range_resolves_central(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        resolved = collector.consume("toptail.pareto_alpha.overall.v1")
        assert resolved.resolved_value == 1.5

    def test_consume_missing_raises(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        with pytest.raises(KeyError, match="not found"):
            collector.consume("nonexistent.v1")

    def test_consume_idempotent(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        r1 = collector.consume("toptail.data_quality.was_response_rate.v1")
        r2 = collector.consume("toptail.data_quality.was_response_rate.v1")
        assert r1 is r2

    def test_record_and_build(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        collector.consume("toptail.pareto_alpha.overall.v1")
        collector.record(
            "Top-1% share",
            PipelineLayer.TOP_TAIL,
            ["toptail.pareto_alpha.overall.v1"],
        )
        manifest = collector.build()
        assert len(manifest.assumptions_consumed) == 1
        assert len(manifest.entries) == 1
        assert manifest.entries[0].output_label == "Top-1% share"

    def test_build_includes_version_tag(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        manifest = collector.build()
        assert manifest.version_tag.macro_baseline_version == "NBS-2025"

    def test_multiple_assumptions_and_entries(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        collector.consume("toptail.data_quality.was_response_rate.v1")
        collector.consume("toptail.pareto_alpha.overall.v1")
        collector.record("Output A", PipelineLayer.TOP_TAIL, [
            "toptail.data_quality.was_response_rate.v1",
            "toptail.pareto_alpha.overall.v1",
        ])
        collector.record("Output B", PipelineLayer.POLICY_RULES)
        manifest = collector.build()
        assert len(manifest.assumptions_consumed) == 2
        assert len(manifest.entries) == 2
        assert "toptail.pareto_alpha.overall.v1" in manifest.assumption_ids()

    def test_consume_schedule_resolves_rate_bands(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        resolved = collector.consume("policy.cgt.rates_2026.v1")
        assert isinstance(resolved.resolved_value, dict)
        assert resolved.resolved_value["basic_rate"] == 18
        assert resolved.resolved_value["higher_rate"] == 24
        assert "type" not in resolved.resolved_value

    def test_consume_flag_resolves_bool(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        resolved = collector.consume("model.behavioural.use_savings_response.v1")
        assert resolved.resolved_value is True

    def test_record_unconsumed_raises(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        with pytest.raises(ValueError, match="not yet consumed"):
            collector.record("Bad output", PipelineLayer.TOP_TAIL, ["nonexistent.v1"])

    def test_build_twice_raises(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        collector.build()
        with pytest.raises(RuntimeError, match="already called"):
            collector.build()

    def test_resolved_assumption_frozen(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        resolved = collector.consume("toptail.data_quality.was_response_rate.v1")
        with pytest.raises(ValidationError, match="frozen"):
            resolved.resolved_value = 999.0

    def test_manifest_timestamp_is_utc(self):
        from datetime import UTC

        manifest = ProvenanceManifest(version_tag=_make_version_tag())
        assert manifest.run_timestamp.tzinfo is UTC

    def test_consume_after_build_raises(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        collector.build()
        with pytest.raises(RuntimeError, match="sealed"):
            collector.consume("toptail.data_quality.was_response_rate.v1")

    def test_record_after_build_raises(self):
        collector = ProvenanceCollector(_make_version_tag(), _make_registry())
        collector.build()
        with pytest.raises(RuntimeError, match="sealed"):
            collector.record("test", PipelineLayer.TOP_TAIL)

    def test_provenance_entry_frozen(self):
        entry = ProvenanceEntry(
            output_label="test",
            layer=PipelineLayer.TOP_TAIL,
        )
        with pytest.raises(ValidationError, match="frozen"):
            entry.output_label = "mutated"
