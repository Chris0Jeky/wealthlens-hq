"""Fetch UK wealth share data from the World Inequality Database API.

Source: WID.world (CC-BY licence)
API endpoint discovered from the public WID Stata tool:
  https://github.com/world-inequality-database/wid-stata-tool
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
from chart_html import write_accessible_chart
from http_retry import fetch_with_retry

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "projects" / "wealthlens-dashboard" / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHART_DIR = ROOT / "projects" / "wealthlens-dashboard" / "charts"

WID_API_BASE = "https://rfap9nitz6.execute-api.eu-west-1.amazonaws.com/prod"
# Published public key from https://github.com/world-inequality-database/wid-stata-tool
# Prefer env var override; fall back to the public default so it works without config.
logger = logging.getLogger(__name__)

WID_API_KEY = os.environ.get("WID_API_KEY", "").strip() or "rYFByOB0ioaPATwHtllMI71zLOZSK0Ic5veQonJP"
logger.info("WID API: using %s key", "environment" if os.environ.get("WID_API_KEY", "").strip() else "default public")
HEADERS = {"x-api-key": WID_API_KEY}

AREA = "GB"
ACCESS_DATE = date.today().isoformat()

# Variable format: {indicator}_{percentile}_{age}_{population}
# 992 = equal-split adults, j = all population
REQUEST_TIMEOUT_SECONDS = 60

VARIABLES = [
    "shweal_p99p100_992_j",  # Top 1% share of net personal wealth
    "shweal_p90p100_992_j",  # Top 10% share of net personal wealth
]


def fetch() -> dict[str, Any]:
    """Download top wealth share data from WID API."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Fetching UK wealth share data from WID API...")
    resp = fetch_with_retry(
        f"{WID_API_BASE}/countries-variables",
        params={"countries": AREA, "variables": ",".join(VARIABLES)},
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    raw_data: dict[str, Any] = resp.json()

    # API may return an S3 download URL for large payloads
    if isinstance(raw_data, dict) and "download_url" in raw_data:
        resp2 = fetch_with_retry(raw_data["download_url"], timeout=REQUEST_TIMEOUT_SECONDS)
        resp2.raise_for_status()
        raw_data = resp2.json()

    raw_path = RAW_DIR / "wid_shweal_gb_data.json"
    raw_path.write_text(json.dumps(raw_data, indent=2), encoding="utf-8")
    logger.info("Saved raw data to %s", raw_path)

    return raw_data


def process(raw_data: dict[str, Any]) -> pd.DataFrame:
    """Clean WID API response into a tidy DataFrame.

    API returns: {variable: [{country: {meta: {...}, values: [{y, v}, ...]}}]}
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    for variable, entries in raw_data.items():
        for entry in entries:
            for country, payload in entry.items():
                for point in payload.get("values", []):
                    records.append({
                        "variable": variable,
                        "country": country,
                        "year": int(point["y"]),
                        "value": float(point["v"]),
                    })

    df = pd.DataFrame(records)

    if df.empty:
        logger.error("No data returned from WID API")
        sys.exit(1)

    df = df.sort_values(["variable", "year"])

    out_path = PROCESSED_DIR / "wid_wealth_shares_gb.csv"
    df.to_csv(out_path, index=False)
    logger.info("Processed data saved to %s", out_path)
    logger.info("%d rows, years %d-%d", len(df), int(df["year"].min()), int(df["year"].max()))

    return df


def build_chart(df: pd.DataFrame) -> None:
    """Generate an interactive Plotly chart of UK wealth shares."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig = go.Figure()

    # WCAG AA compliant colours with high contrast
    colours = {"p99p100": "#d62728", "p90p100": "#1f77b4"}
    labels = {"p99p100": "Top 1%", "p90p100": "Top 10%"}

    if "variable" in df.columns:
        for var in df["variable"].unique():
            subset = df[df["variable"] == var].sort_values("year")
            # Extract percentile from variable name
            perc = "p99p100" if "p99p100" in var else "p90p100" if "p90p100" in var else var
            label = labels.get(perc, var)
            colour = colours.get(perc, "#333333")

            fig.add_trace(go.Scatter(
                x=subset["year"],
                y=subset["value"] * 100,
                mode="lines",
                name=label,
                line=dict(color=colour, width=2.5),
                hovertemplate=f"{label}: %{{y:.1f}}%<br>Year: %{{x}}<extra></extra>",
            ))
    else:
        fig.add_trace(go.Scatter(
            x=df["year"],
            y=df["value"] * 100,
            mode="lines",
            name="Top 1% share",
            line=dict(color="#d62728", width=2.5),
        ))

    fig.update_layout(
        title=dict(
            text="Share of Net Personal Wealth — United Kingdom",
            font=dict(size=20),
        ),
        xaxis=dict(title="Year", tickfont=dict(size=14), gridcolor="#e0e0e0"),
        yaxis=dict(
            title="Share of total wealth (%)",
            ticksuffix="%",
            tickfont=dict(size=14),
            gridcolor="#e0e0e0",
        ),
        legend=dict(font=dict(size=14), x=0.02, y=0.98),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", color="#1a1a1a"),
        margin=dict(b=100),
        annotations=[
            dict(
                text=(
                    f"Source: World Inequality Database (wid.world) · CC-BY · "
                    f"Accessed {ACCESS_DATE} · Equal-split adults"
                ),
                xref="paper", yref="paper",
                x=0, y=-0.15,
                showarrow=False,
                font=dict(size=11, color="#666666"),
            )
        ],
    )

    out_path = CHART_DIR / "wid_wealth_shares_gb.html"
    write_accessible_chart(
        fig,
        out_path,
        title="Share of Net Personal Wealth — United Kingdom",
        description="Line chart showing the top 1% and top 10% share of UK net personal wealth from 1820 to 2024, sourced from the World Inequality Database.",
    )


def main() -> None:
    """Fetch WID wealth share data and generate chart."""
    raw_data = fetch()
    df = process(raw_data)
    build_chart(df)
    logger.info("Done. Open the chart HTML in a browser to view.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    main()
