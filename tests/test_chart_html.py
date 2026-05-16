"""Tests for the shared accessible chart HTML wrapper."""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation" / "data-pipelines"))

from chart_html import write_accessible_chart


def test_output_contains_lang_attribute(tmp_path: Path):
    fig = go.Figure(go.Bar(x=["A", "B"], y=[1, 2]))
    out = tmp_path / "test.html"
    write_accessible_chart(fig, out, title="Test", description="Test chart")
    html = out.read_text(encoding="utf-8")
    assert 'lang="en"' in html


def test_output_contains_viewport_meta(tmp_path: Path):
    fig = go.Figure(go.Bar(x=["A", "B"], y=[1, 2]))
    out = tmp_path / "test.html"
    write_accessible_chart(fig, out, title="Test", description="Test chart")
    html = out.read_text(encoding="utf-8")
    assert "viewport" in html
    assert "width=device-width" in html


def test_output_contains_skip_link(tmp_path: Path):
    fig = go.Figure(go.Bar(x=["A", "B"], y=[1, 2]))
    out = tmp_path / "test.html"
    write_accessible_chart(fig, out, title="Test", description="Test chart")
    html = out.read_text(encoding="utf-8")
    assert "skip-link" in html
    assert 'href="#chart"' in html


def test_output_contains_aria_label(tmp_path: Path):
    fig = go.Figure(go.Bar(x=["A", "B"], y=[1, 2]))
    out = tmp_path / "test.html"
    write_accessible_chart(fig, out, title="Test", description="My description")
    html = out.read_text(encoding="utf-8")
    assert 'aria-label="My description"' in html


def test_output_contains_noscript_fallback(tmp_path: Path):
    fig = go.Figure(go.Bar(x=["A", "B"], y=[1, 2]))
    out = tmp_path / "test.html"
    write_accessible_chart(fig, out, title="Test", description="Test chart")
    html = out.read_text(encoding="utf-8")
    assert "<noscript>" in html


def test_title_includes_wealthlens_branding(tmp_path: Path):
    fig = go.Figure(go.Bar(x=["A", "B"], y=[1, 2]))
    out = tmp_path / "test.html"
    write_accessible_chart(fig, out, title="My Chart", description="Test chart")
    html = out.read_text(encoding="utf-8")
    assert "<title>My Chart — WealthLens UK</title>" in html


def test_html_escape_prevents_xss_in_title(tmp_path: Path):
    fig = go.Figure(go.Bar(x=["A", "B"], y=[1, 2]))
    out = tmp_path / "test.html"
    write_accessible_chart(
        fig, out, title='<script>alert("xss")</script>', description="Safe"
    )
    html = out.read_text(encoding="utf-8")
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


def test_html_escape_prevents_xss_in_description(tmp_path: Path):
    fig = go.Figure(go.Bar(x=["A", "B"], y=[1, 2]))
    out = tmp_path / "test.html"
    write_accessible_chart(
        fig, out, title="Safe", description='"><script>alert(1)</script>'
    )
    html = out.read_text(encoding="utf-8")
    assert '"><script>' not in html


def test_plausible_tag_present_when_env_set(tmp_path: Path, monkeypatch: object):
    import pytest

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("PLAUSIBLE_DOMAIN", "wealthlens.uk")
    try:
        fig = go.Figure(go.Bar(x=["A", "B"], y=[1, 2]))
        out = tmp_path / "test.html"
        write_accessible_chart(fig, out, title="Test", description="Test chart")
        html = out.read_text(encoding="utf-8")
        assert 'data-domain="wealthlens.uk"' in html
        assert "plausible.io/js/script.js" in html
    finally:
        monkeypatch.undo()


def test_plausible_tag_absent_when_env_unset(tmp_path: Path, monkeypatch: object):
    import os
    os.environ.pop("PLAUSIBLE_DOMAIN", None)
    fig = go.Figure(go.Bar(x=["A", "B"], y=[1, 2]))
    out = tmp_path / "test.html"
    write_accessible_chart(fig, out, title="Test", description="Test chart")
    html = out.read_text(encoding="utf-8")
    assert "plausible.io" not in html


def test_plausible_whitespace_domain_ignored(tmp_path: Path):
    import os
    os.environ["PLAUSIBLE_DOMAIN"] = "   "
    try:
        fig = go.Figure(go.Bar(x=["A", "B"], y=[1, 2]))
        out = tmp_path / "test.html"
        write_accessible_chart(fig, out, title="Test", description="Test chart")
        html = out.read_text(encoding="utf-8")
        assert "plausible.io" not in html
    finally:
        os.environ.pop("PLAUSIBLE_DOMAIN", None)
