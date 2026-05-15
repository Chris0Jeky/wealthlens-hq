"""Generate social media images from processed chart data.

Reads processed CSV datasets and exports Plotly charts as static PNG images
at platform-specific dimensions.

Requires: plotly, pandas, kaleido
Usage: python automation/social-media/chart_to_social.py [--chart NAME]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "projects" / "wealthlens-dashboard" / "data" / "processed"
OUT_DIR = ROOT / "projects" / "wealthlens-dashboard" / "social-assets"

SIZES = {
    "og": (1200, 630),
    "twitter": (1600, 900),
    "instagram": (1080, 1080),
    "linkedin": (1200, 627),
}


def _wealth_shares_fig() -> tuple[go.Figure, str]:
    df = pd.read_csv(DATA_DIR / "wid_wealth_shares_gb.csv")
    fig = go.Figure()
    colours = {"p99p100": "#d62728", "p90p100": "#1f77b4"}
    labels = {"p99p100": "Top 1%", "p90p100": "Top 10%"}
    for var in df["variable"].unique():
        subset = df[df["variable"] == var].sort_values("year")
        perc = "p99p100" if "p99p100" in var else "p90p100"
        fig.add_trace(go.Scatter(
            x=subset["year"], y=subset["value"] * 100,
            mode="lines", name=labels.get(perc, var),
            line=dict(color=colours.get(perc, "#333"), width=3),
        ))
    fig.update_layout(
        title=dict(text="Share of Net Personal Wealth — UK", font=dict(size=28)),
        xaxis=dict(title="Year", tickfont=dict(size=16)),
        yaxis=dict(title="Share (%)", ticksuffix="%", tickfont=dict(size=16)),
        legend=dict(font=dict(size=18), x=0.02, y=0.98),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="system-ui, sans-serif", color="#1a1a1a"),
        margin=dict(l=80, r=40, t=80, b=60),
    )
    return fig, "wealth-shares"


def _housing_fig() -> tuple[go.Figure, str]:
    df = pd.read_csv(DATA_DIR / "ons_housing_affordability_by_region.csv")
    fig = go.Figure()
    highlight = {"London": "#d62728", "South East": "#1f77b4", "North East": "#17becf", "England": "#1a1a1a"}
    for region in highlight:
        subset = df[df["region"] == region].sort_values("year")
        if subset.empty:
            continue
        fig.add_trace(go.Scatter(
            x=subset["year"], y=subset["ratio"],
            mode="lines", name=region,
            line=dict(color=highlight[region], width=3),
        ))
    fig.update_layout(
        title=dict(text="Housing Affordability: Price-to-Earnings Ratio", font=dict(size=26)),
        xaxis=dict(title="Year", tickfont=dict(size=16)),
        yaxis=dict(title="House price ÷ earnings", ticksuffix="x", tickfont=dict(size=16)),
        legend=dict(font=dict(size=16)),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="system-ui, sans-serif", color="#1a1a1a"),
        margin=dict(l=80, r=40, t=80, b=60),
    )
    return fig, "housing-affordability"


def _wealth_decile_fig() -> tuple[go.Figure, str]:
    df = pd.read_csv(DATA_DIR / "ons_wealth_by_decile.csv")
    colours = ["#1f77b4"] * 7 + ["#ff7f0e"] * 2 + ["#d62728"]
    fig = go.Figure(go.Bar(
        x=df["decile"], y=df["total_wealth_bn"],
        marker_color=colours[:len(df)],
        text=[f"£{v:,.0f}bn" if v >= 0 else f"-£{abs(v):,.0f}bn" for v in df["total_wealth_bn"]],
        textposition="outside", textfont=dict(size=14),
    ))
    fig.update_layout(
        title=dict(text="Total Net Wealth by Decile — Great Britain", font=dict(size=24)),
        xaxis=dict(tickfont=dict(size=12), tickangle=-30),
        yaxis=dict(title="£ billions", tickfont=dict(size=14)),
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
        font=dict(family="system-ui, sans-serif", color="#1a1a1a"),
        margin=dict(l=80, r=40, t=80, b=100),
    )
    return fig, "wealth-by-decile"


def _cgt_fig() -> tuple[go.Figure, str]:
    df = pd.read_csv(DATA_DIR / "hmrc_cgt_concentration.csv")
    fig = go.Figure(go.Bar(
        x=df["gain_band"], y=df["share_of_gains_pct"],
        marker_color=["#d62728" if p > 20 else "#ff7f0e" if p > 10 else "#1f77b4" for p in df["share_of_gains_pct"]],
        text=[f"{p:.0f}%" if pd.notna(p) else "n/a" for p in df["share_of_gains_pct"]],
        textposition="outside", textfont=dict(size=14),
    ))
    fig.update_layout(
        title=dict(text="Capital Gains Concentration — UK", font=dict(size=26)),
        xaxis=dict(title="Size of gain", tickfont=dict(size=12), tickangle=-30),
        yaxis=dict(title="Share of total gains (%)", ticksuffix="%", tickfont=dict(size=14)),
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
        font=dict(family="system-ui, sans-serif", color="#1a1a1a"),
        margin=dict(l=80, r=40, t=80, b=100),
    )
    return fig, "cgt-concentration"


CHARTS = {
    "wealth-shares": _wealth_shares_fig,
    "housing-affordability": _housing_fig,
    "wealth-by-decile": _wealth_decile_fig,
    "cgt-concentration": _cgt_fig,
}


def export(chart_name: str, sizes: dict[str, tuple[int, int]] | None = None) -> list[Path]:
    """Export a chart at all social media sizes. Returns paths of generated files."""
    if sizes is None:
        sizes = SIZES

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if chart_name not in CHARTS:
        print(f"Unknown chart: {chart_name}. Available: {', '.join(CHARTS)}")
        return []

    fig, name = CHARTS[chart_name]()
    exported: list[Path] = []

    for size_name, (w, h) in sizes.items():
        out_path = OUT_DIR / f"{name}_{size_name}.png"
        fig.write_image(str(out_path), width=w, height=h, scale=2)
        print(f"  {out_path.name} ({w}x{h} @2x)")
        exported.append(out_path)

    return exported


def main() -> None:
    """Generate social media images for all or a specific chart."""
    parser = argparse.ArgumentParser(description="Generate social media images from chart data")
    parser.add_argument("--chart", choices=list(CHARTS), help="Export a specific chart only")
    args = parser.parse_args()

    charts = [args.chart] if args.chart else list(CHARTS)

    total = 0
    for chart_name in charts:
        print(f"\n=== {chart_name} ===")
        exported = export(chart_name)
        total += len(exported)

    print(f"\nGenerated {total} images in {OUT_DIR}")


if __name__ == "__main__":
    main()
