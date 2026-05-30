"""Tests for the runnable engine examples (keeps the living docs honest)."""

from __future__ import annotations

from wealthlens_sim import __version__
from wealthlens_sim.examples.headline_revenue import build_report, example_result


class TestHeadlineRevenue:
    def test_result_is_deterministic(self):
        a = example_result()
        b = example_result()
        assert a.total_revenue_gbp_bn == b.total_revenue_gbp_bn
        assert a.revenue_by_decile == b.revenue_by_decile

    def test_result_has_real_intervals_and_complete_provenance(self):
        result = example_result()
        iv = result.total_revenue_gbp_bn
        assert iv.low < iv.central < iv.high  # registry supplied => real intervals
        assert result.provenance_complete is True
        assert "toptail.pareto_alpha.overall.v1" in result.provenance.assumptions_consumed
        assert result.scenario.version_tag.wealthlens_sim_version == __version__

    def test_revenue_concentrated_in_top_decile(self):
        result = example_result()
        # A £1m-threshold wealth tax falls on the wealthiest households.
        assert result.revenue_by_decile[-1].central > result.revenue_by_decile[0].central

    def test_report_renders_headline_and_provenance(self):
        report = build_report(example_result())
        assert "Headline revenue" in report
        assert "By nation:" in report
        assert "By wealth decile" in report
        assert "Provenance: complete" in report

    def test_report_labels_headline_honestly(self):
        # Data-integrity guardrail: no single line may be quoted as a real estimate.
        report = build_report(example_result())
        lines = report.splitlines()
        # A banner heads the report.
        assert "ILLUSTRATIVE" in lines[0] and "NOT a real revenue estimate" in lines[0]
        # The headline line is itself self-labelled (not just labelled elsewhere).
        headline = next(line for line in lines if "Headline revenue" in line)
        assert "ILLUSTRATIVE" in headline or "synthetic" in headline.lower()
        # The known overshoot (biased high) is disclosed where a CLI user sees it.
        assert "biased HIGH" in report
        assert "15-16tn" in report
