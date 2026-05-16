"""Fetch UK child poverty rates by region.

Source: DWP/HMRC Children in Low Income Families statistics (OGL v3.0)
Shows percentage of children in relative low income after housing costs
by UK region.
"""

from __future__ import annotations

import json
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

SOURCE_URL = (
    "https://www.gov.uk/government/statistics/"
    "children-in-low-income-families-local-area-statistics-2014-to-2023"
)

ACCESS_DATE = date.today().isoformat()

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 60

# Fallback data from DWP/HMRC Children in Low Income Families statistics
# (% of children in relative low income after housing costs, 2022/23).
# Used when the live download is unavailable or the spreadsheet format
# has changed.
FALLBACK_DATA = [
    {"region": "North East", "child_poverty_pct": 38.0, "children_in_poverty": 185000},
    {"region": "North West", "child_poverty_pct": 33.0, "children_in_poverty": 380000},
    {"region": "Yorkshire and The Humber", "child_poverty_pct": 33.0, "children_in_poverty": 290000},
    {"region": "East Midlands", "child_poverty_pct": 28.0, "children_in_poverty": 210000},
    {"region": "West Midlands", "child_poverty_pct": 35.0, "children_in_poverty": 340000},
    {"region": "East of England", "child_poverty_pct": 24.0, "children_in_poverty": 230000},
    {"region": "London", "child_poverty_pct": 36.0, "children_in_poverty": 700000},
    {"region": "South East", "child_poverty_pct": 22.0, "children_in_poverty": 310000},
    {"region": "South West", "child_poverty_pct": 24.0, "children_in_poverty": 190000},
    {"region": "Wales", "child_poverty_pct": 31.0, "children_in_poverty": 150000},
    {"region": "Scotland", "child_poverty_pct": 26.0, "children_in_poverty": 230000},
    {"region": "Northern Ireland", "child_poverty_pct": 24.0, "children_in_poverty": 90000},
]


def fetch() -> tuple[pd.DataFrame, bool]:
    """Try to download child poverty data from gov.uk; fall back to hardcoded data.

    Returns:
        A tuple of (DataFrame with raw data, is_fallback flag).
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    try:
        logger.info("Attempting to fetch child poverty data from gov.uk...")
        resp = requests.get(SOURCE_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()

        # The landing page is HTML, not a direct file download.
        # A real pipeline would parse it for the .ods/.xlsx link, then
        # download and parse the spreadsheet.  For now, we use the
        # fallback data since the download URL changes with each release.
        logger.info(
            "Landing page fetched (%d bytes) — "
            "direct spreadsheet parsing not yet implemented, using fallback data.",
            len(resp.content),
        )
    except requests.ConnectionError:
        logger.warning("Could not connect to gov.uk — using fallback data.")
    except requests.Timeout:
        logger.warning("Request to gov.uk timed out — using fallback data.")
    except requests.HTTPError as exc:
        logger.warning("HTTP error from gov.uk (%s) — using fallback data.", exc)

    logger.info("Using fallback data from DWP/HMRC statistics (2022/23).")
    df = pd.DataFrame(FALLBACK_DATA)

    raw_path = RAW_DIR / "child_poverty_by_region_fallback.csv"
    df.to_csv(raw_path, index=False)
    logger.info("Raw fallback data saved to %s", raw_path)

    return df, True


def process(df_raw: pd.DataFrame, *, is_fallback: bool) -> pd.DataFrame:
    """Clean and enrich child poverty data; write processed CSV and metadata sidecar."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = df_raw.copy()
    df = df.sort_values("child_poverty_pct", ascending=False).reset_index(drop=True)

    # Compute national average (weighted by children_in_poverty / child_poverty_pct
    # gives approximate total children per region, then re-derive the weighted rate).
    total_children_in_poverty = df["children_in_poverty"].sum()
    total_children_approx = (
        df["children_in_poverty"] / (df["child_poverty_pct"] / 100)
    ).sum()
    national_avg = (total_children_in_poverty / total_children_approx) * 100
    df["national_avg_pct"] = round(national_avg, 1)
    df["above_national_avg"] = df["child_poverty_pct"] > national_avg

    out_path = PROCESSED_DIR / "child_poverty_by_region.csv"
    df.to_csv(out_path, index=False)
    logger.info("Processed data saved to %s (%d rows)", out_path, len(df))

    # Write .meta.json sidecar
    meta = {
        "source": "DWP/HMRC Children in Low Income Families",
        "source_url": SOURCE_URL,
        "access_date": ACCESS_DATE,
        "is_fallback": is_fallback,
        "row_count": len(df),
        "period": "2022/23",
        "measure": "Percentage of children in relative low income after housing costs",
    }
    meta_path = PROCESSED_DIR / "child_poverty_by_region.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logger.info("Metadata sidecar saved to %s", meta_path)

    return df


def build_chart(df: pd.DataFrame) -> None:
    """Generate a horizontal bar chart of child poverty rates by region."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    # Sort ascending so highest poverty rate appears at the top of the
    # horizontal bar chart (Plotly draws bars bottom-to-top).
    df_chart = df.sort_values("child_poverty_pct", ascending=True).reset_index(drop=True)

    national_avg = float(df_chart["national_avg_pct"].iloc[0])

    bar_colors = [
        "#C8161D" if above else "#B0B0B0"
        for above in df_chart["above_national_avg"]
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_chart["region"],
        x=df_chart["child_poverty_pct"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"{pct:.0f}%" for pct in df_chart["child_poverty_pct"]],
        textposition="outside",
        textfont=dict(size=12),
        hovertemplate=(
            "%{y}<br>"
            "Child poverty rate: %{x:.1f}%<br>"
            "Children in poverty: %{customdata[0]:,}<br>"
            "<extra></extra>"
        ),
        customdata=[[c] for c in df_chart["children_in_poverty"]],
    ))

    # National average reference line
    fig.add_vline(
        x=national_avg,
        line_dash="dash",
        line_color="#333333",
        annotation_text=f"UK avg: {national_avg:.1f}%",
        annotation_position="top right",
        annotation_font=dict(size=11, color="#333333"),
    )

    fig.update_layout(
        title=dict(
            text="Child Poverty Rates by Region — UK (2022/23)",
            font=dict(size=18),
        ),
        xaxis=dict(
            title="% of children in relative low income (after housing costs)",
            ticksuffix="%",
            tickfont=dict(size=13),
            gridcolor="#e0e0e0",
            range=[0, max(df_chart["child_poverty_pct"]) + 5],
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=13),
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", color="#1a1a1a"),
        margin=dict(l=200, b=120),
        annotations=[
            dict(
                text=(
                    f"Source: DWP/HMRC Children in Low Income Families · "
                    f"OGL v3.0 · Accessed {ACCESS_DATE}<br>"
                    f"Red bars indicate regions above the national average. "
                    f"Measure: relative low income after housing costs."
                ),
                xref="paper", yref="paper",
                x=0, y=-0.18,
                showarrow=False,
                font=dict(size=11, color="#666666"),
            ),
        ],
    )

    out_path = CHART_DIR / "child_poverty_by_region.html"
    write_accessible_chart(
        fig,
        out_path,
        title="Child Poverty Rates by Region — UK",
        description=(
            "Horizontal bar chart showing child poverty rates across UK regions in 2022/23. "
            "The North East has the highest rate at 38%, while the South East has the lowest "
            "at 22%. Regions above the national average are highlighted in red."
        ),
    )


def main() -> None:
    """Fetch child poverty data and generate chart."""
    df_raw, is_fallback = fetch()
    df = process(df_raw, is_fallback=is_fallback)
    build_chart(df)
    logger.info("Done. Open the chart HTML in a browser to view.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    main()
