"""Fetch ONS housing affordability data for England and Wales.

Source: ONS Housing Affordability in England and Wales (OGL v3.0)
Dataset: House price to workplace-based earnings ratio
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
from chart_html import write_accessible_chart

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "projects" / "wealthlens-dashboard" / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHART_DIR = ROOT / "projects" / "wealthlens-dashboard" / "charts"

XLSX_URL = (
    "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/housing/"
    "datasets/ratioofhousepricetoworkplacebasedearningslowerquartileandmedian/"
    "current/aff1ratioofhousepricetoworkplacebasedearnings.xlsx"
)

ACCESS_DATE = date.today().isoformat()

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 60

def fetch() -> Path:
    """Download the ONS housing affordability XLSX."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / "ons_housing_affordability.xlsx"

    logger.info("Downloading ONS housing affordability data...")
    resp = requests.get(XLSX_URL, timeout=REQUEST_TIMEOUT_SECONDS)
    resp.raise_for_status()

    out_path.write_bytes(resp.content)
    logger.info("Saved to %s (%d KB)", out_path, len(resp.content) // 1024)
    return out_path


def process(xlsx_path: Path) -> pd.DataFrame:
    """Extract median affordability ratios by region from sheet 1c.

    Sheet 1c structure:
      Row 0: title
      Row 1: header (Code, Name, 1997, 1998, ...)
      Rows 2+: data (region code, region name, ratio values)
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df_raw = pd.read_excel(
        xlsx_path, sheet_name="1c", header=None, engine="openpyxl",
    )

    # Row 1 has headers: Code, Name, year columns
    years = []
    year_cols = []
    for col_idx in range(2, len(df_raw.columns)):
        val = df_raw.iloc[1, col_idx]
        try:
            year = int(float(str(val)))
            if 1990 <= year <= 2030:
                years.append(year)
                year_cols.append(col_idx)
        except (ValueError, TypeError):
            continue

    logger.info("Found %d years: %d-%d", len(years), min(years), max(years))

    # Rows 2+ have data: code, name, values
    records = []
    for i in range(2, len(df_raw)):
        region = str(df_raw.iloc[i, 1]).strip()
        if not region or region == "nan":
            continue

        for year, col_idx in zip(years, year_cols, strict=True):
            cell: object = df_raw.iloc[i, col_idx]
            try:
                ratio = float(cell)  # type: ignore[arg-type]
                records.append({"region": region, "year": year, "ratio": ratio})
            except (ValueError, TypeError):
                continue

    df = pd.DataFrame(records)
    df = df.sort_values(["region", "year"])

    out_path = PROCESSED_DIR / "ons_housing_affordability_by_region.csv"
    df.to_csv(out_path, index=False)
    logger.info("Processed data saved to %s", out_path)
    logger.info("%d rows across %d regions", len(df), df["region"].nunique())

    return df


def build_chart(df: pd.DataFrame) -> None:
    """Generate interactive affordability chart."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig = go.Figure()

    # Highlight regions and assign colours
    highlight = {
        "London": {"color": "#d62728", "width": 3},
        "England": {"color": "#1a1a1a", "width": 2.5, "dash": "dash"},
        "South East": {"color": "#1f77b4", "width": 2},
        "North East": {"color": "#17becf", "width": 2},
    }
    default_colours = [
        "#ff7f0e", "#2ca02c", "#9467bd", "#8c564b",
        "#e377c2", "#7f7f7f", "#bcbd22", "#aec7e8",
    ]

    regions = sorted(df["region"].unique())
    # Show highlighted regions first, then the rest
    show_first = [r for r in ["London", "South East", "North East", "England"] if r in regions]
    rest = [r for r in regions if r not in show_first and r != "England and Wales"]
    colour_idx = 0

    for region in show_first + rest:
        subset = df[df["region"] == region].sort_values("year")
        if subset.empty:
            continue

        style = highlight.get(region, {})
        if not style:
            style = {"color": default_colours[colour_idx % len(default_colours)], "width": 1.5}
            colour_idx += 1

        fig.add_trace(go.Scatter(
            x=subset["year"],
            y=subset["ratio"],
            mode="lines",
            name=region,
            line=dict(
                color=style["color"],
                width=style.get("width", 1.5),
                dash=style.get("dash", "solid"),
            ),
            hovertemplate=f"{region}: %{{y:.2f}}x<br>Year: %{{x}}<extra></extra>",
            visible=True if region in highlight else "legendonly",
        ))

    fig.update_layout(
        title=dict(
            text="Housing Affordability: House Price to Earnings Ratio by Region",
            font=dict(size=18),
        ),
        xaxis=dict(title="Year", tickfont=dict(size=14), gridcolor="#e0e0e0"),
        yaxis=dict(
            title="Median house price ÷ median earnings",
            ticksuffix="x",
            tickfont=dict(size=14),
            gridcolor="#e0e0e0",
            rangemode="tozero",
        ),
        legend=dict(font=dict(size=12)),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", color="#1a1a1a"),
        margin=dict(b=100),
        annotations=[
            dict(
                text=(
                    f"Source: ONS Housing Affordability in England and Wales · "
                    f"OGL v3.0 · Accessed {ACCESS_DATE}<br>"
                    f"Ratio = median house price ÷ median gross annual workplace-based earnings. "
                    f"Click legend to show/hide regions."
                ),
                xref="paper", yref="paper",
                x=0, y=-0.18,
                showarrow=False,
                font=dict(size=11, color="#666666"),
            )
        ],
    )

    out_path = CHART_DIR / "ons_housing_affordability.html"
    write_accessible_chart(
        fig,
        out_path,
        title="Housing Affordability by Region",
        description="Line chart showing median house price to earnings ratio across English regions from 1997 to 2025, sourced from ONS.",
    )


def main() -> None:
    """Fetch ONS housing data and generate chart."""
    xlsx_path = fetch()
    df = process(xlsx_path)
    build_chart(df)
    logger.info("Done. Open the chart HTML in a browser to view.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    main()
