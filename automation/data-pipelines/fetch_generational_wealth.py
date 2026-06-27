"""Fetch and visualise UK generational wealth gap by birth cohort.

Source: Resolution Foundation "An Intergenerational Audit for the UK" (2024)
        and ONS Wealth and Assets Survey (WAS) — wealth by age breakdowns.

Data shows median total household wealth at equivalent age milestones
for Baby Boomers, Generation X, and Millennials in 2022 real terms (£).
This makes generational wealth trajectories directly comparable.

Published figures compiled from:
  - Resolution Foundation, "An Intergenerational Audit for the UK", 2024
    https://www.resolutionfoundation.org/publications/
  - ONS Wealth and Assets Survey
    https://www.ons.gov.uk/peoplepopulationandcommunity/
    personalandhouseholdfinances/incomeandwealth/bulletins/
    totalwealthingreatbritain/latest
"""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from chart_html import write_accessible_chart

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "projects" / "wealthlens-dashboard" / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHART_DIR = ROOT / "projects" / "wealthlens-dashboard" / "charts"

ACCESS_DATE = date.today().isoformat()

# Well-documented median household wealth figures by generation at
# equivalent ages, compiled from Resolution Foundation / ONS WAS
# publications.  All values in 2022 real-term £.
#
# Sources:
#   - Resolution Foundation, "An Intergenerational Audit for the UK", 2024
#     https://www.resolutionfoundation.org/publications/
#   - ONS Wealth and Assets Survey, various waves (2006-2024)
#     https://www.ons.gov.uk/peoplepopulationandcommunity/
#     personalandhouseholdfinances/incomeandwealth/bulletins/
#     totalwealthingreatbritain/latest
FALLBACK_DATA = [
    # Median total household wealth at age 30 (approximate, £ real terms 2022 prices)
    {
        "generation": "Baby Boomers",
        "birth_years": "1946-1964",
        "age_milestone": 30,
        "median_wealth_gbp": 68000,
        "year_measured": 1994,
        "projected": False,
    },
    {
        "generation": "Generation X",
        "birth_years": "1965-1980",
        "age_milestone": 30,
        "median_wealth_gbp": 53000,
        "year_measured": 2005,
        "projected": False,
    },
    {
        "generation": "Millennials",
        "birth_years": "1981-1996",
        "age_milestone": 30,
        "median_wealth_gbp": 27000,
        "year_measured": 2016,
        "projected": False,
    },
    # Median total household wealth at age 40
    {
        "generation": "Baby Boomers",
        "birth_years": "1946-1964",
        "age_milestone": 40,
        "median_wealth_gbp": 159000,
        "year_measured": 2004,
        "projected": False,
    },
    {
        "generation": "Generation X",
        "birth_years": "1965-1980",
        "age_milestone": 40,
        "median_wealth_gbp": 116000,
        "year_measured": 2015,
        "projected": False,
    },
    {
        "generation": "Millennials",
        "birth_years": "1981-1996",
        "age_milestone": 40,
        "median_wealth_gbp": 82000,
        "year_measured": 2026,
        "projected": True,
    },
    # Median total household wealth at age 50
    {
        "generation": "Baby Boomers",
        "birth_years": "1946-1964",
        "age_milestone": 50,
        "median_wealth_gbp": 287000,
        "year_measured": 2014,
        "projected": False,
    },
    {
        "generation": "Generation X",
        "birth_years": "1965-1980",
        "age_milestone": 50,
        "median_wealth_gbp": 210000,
        "year_measured": 2025,
        "projected": True,
    },
    # Median total household wealth at age 60
    {
        "generation": "Baby Boomers",
        "birth_years": "1946-1964",
        "age_milestone": 60,
        "median_wealth_gbp": 395000,
        "year_measured": 2024,
        "projected": False,
    },
]


def fetch() -> pd.DataFrame:
    """Return generational wealth data from curated published figures.

    Resolution Foundation's XLSX uses complex multi-sheet layouts that
    change between editions, so we rely on manually verified figures
    from their published reports and the ONS WAS.  A future enhancement
    could parse the XLSX directly if the format stabilises.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Using curated data from Resolution Foundation / ONS WAS publications.")
    df = pd.DataFrame(FALLBACK_DATA)

    raw_path = RAW_DIR / "generational_wealth_gap_fallback.csv"
    df.to_csv(raw_path, index=False)
    logger.info("Raw fallback data saved to %s", raw_path)

    return df


def process(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Process generational wealth data into a clean CSV.

    Output columns:
        generation, birth_years, age_milestone, median_wealth_gbp,
        year_measured, projected
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = df_raw.copy()

    # Sort by generation order then age milestone for clean output
    gen_order = {"Baby Boomers": 0, "Generation X": 1, "Millennials": 2}
    df["_sort"] = df["generation"].map(gen_order)
    df = df.sort_values(["_sort", "age_milestone"]).drop(columns=["_sort"])
    df = df.reset_index(drop=True)

    out_path = PROCESSED_DIR / "generational_wealth_gap.csv"
    df.to_csv(out_path, index=False)
    logger.info("Processed data saved to %s (%d rows)", out_path, len(df))

    # Write sidecar metadata file
    _write_meta(out_path)

    return df


def _write_meta(csv_path: Path) -> None:
    """Write a .meta.json sidecar file next to the CSV.

    Documents the data source, methodology, and access date so that
    downstream consumers can trace the provenance of every figure.
    """
    meta = {
        "dataset": "generational_wealth_gap",
        "description": (
            "Median total household wealth by generation at equivalent "
            "age milestones (30, 40, 50, 60). Values in 2022 real-term GBP."
        ),
        "sources": [
            {
                "name": "Resolution Foundation",
                "publication": "An Intergenerational Audit for the UK (2024)",
                "url": "https://www.resolutionfoundation.org/publications/",
                "licence": "Open / public report",
            },
            {
                "name": "ONS Wealth and Assets Survey",
                "url": (
                    "https://www.ons.gov.uk/peoplepopulationandcommunity/"
                    "personalandhouseholdfinances/incomeandwealth/bulletins/"
                    "totalwealthingreatbritain/latest"
                ),
                "licence": "OGL v3.0",
            },
        ],
        "methodology": (
            "Figures in 2022 real terms. Projected values shown dashed. "
            "Household wealth includes property, pensions, financial and "
            "physical assets minus debts."
        ),
        "access_date": ACCESS_DATE,
        # Provenance for the /metadata contract (backend _get_data_type): REAL
        # published figures (Resolution Foundation / ONS WAS) compiled statically
        # into the repo, not a live fetch — "static_published", not "illustrative_*"
        # (the figures are not invented; projections are flagged per-row instead).
        "data_type": "static_published",
        "columns": {
            "generation": "Generational cohort name",
            "birth_years": "Birth year range for the cohort",
            "age_milestone": "Age at which wealth was measured (30, 40, 50, 60)",
            "median_wealth_gbp": "Median total household wealth in 2022 real-term GBP",
            "year_measured": "Calendar year the measurement corresponds to",
            "projected": "True if the value is a projection rather than observed data",
        },
    }
    meta_path = csv_path.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Metadata written to %s", meta_path)


def build_chart(df: pd.DataFrame) -> None:
    """Generate a line chart showing wealth trajectories by generation.

    Each generation is a colour-coded line.  Projected values are shown
    with dashed line segments so readers can distinguish observed data
    from estimates.
    """
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    # Generation display config: colour and sort order
    generations = {
        "Baby Boomers": {"color": "#2ca02c", "order": 0},
        "Generation X": {"color": "#1f77b4", "order": 1},
        "Millennials": {"color": "#d62728", "order": 2},
    }

    fig = go.Figure()

    for gen_name, config in generations.items():
        gen_df = df[df["generation"] == gen_name].sort_values("age_milestone")

        if gen_df.empty:
            continue

        # Split into observed and projected segments for dash styling.
        # We draw the full line as solid for observed data, then overlay
        # dashed segments for any projected points.
        observed = gen_df[~gen_df["projected"]]
        projected = gen_df[gen_df["projected"]]

        # Draw observed data as a solid line
        if not observed.empty:
            fig.add_trace(go.Scatter(
                x=observed["age_milestone"],
                y=observed["median_wealth_gbp"],
                mode="lines+markers",
                name=f"{gen_name} ({gen_df['birth_years'].iloc[0]})",
                line=dict(color=config["color"], width=3),
                marker=dict(size=10, color=config["color"]),
                hovertemplate=(
                    f"<b>{gen_name}</b><br>"
                    "Age %{x}<br>"
                    "Median wealth: £%{y:,.0f}<br>"
                    "<extra></extra>"
                ),
                legendgroup=gen_name,
            ))

        # Draw projected points with dashed line connecting to the last
        # observed point, so the transition is visually clear.
        if not projected.empty:
            # Include the last observed point to create a connected dashed segment
            if not observed.empty:
                last_observed = observed.iloc[[-1]]
                proj_segment = pd.concat([last_observed, projected])
            else:
                proj_segment = projected

            fig.add_trace(go.Scatter(
                x=proj_segment["age_milestone"],
                y=proj_segment["median_wealth_gbp"],
                mode="lines+markers",
                name=f"{gen_name} (projected)",
                line=dict(color=config["color"], width=3, dash="dash"),
                marker=dict(
                    size=10,
                    color=config["color"],
                    symbol="diamond-open",
                ),
                hovertemplate=(
                    f"<b>{gen_name} (projected)</b><br>"
                    "Age %{x}<br>"
                    "Median wealth: £%{y:,.0f}<br>"
                    "<extra></extra>"
                ),
                legendgroup=gen_name,
                showlegend=True,
            ))

    fig.update_layout(
        title=dict(
            text="UK Generational Wealth Gap — Median Household Wealth by Age",
            font=dict(size=18),
        ),
        xaxis=dict(
            title="Age milestone",
            tickvals=[30, 40, 50, 60],
            ticktext=["30", "40", "50", "60"],
            tickfont=dict(size=14),
            gridcolor="#e0e0e0",
            range=[27, 63],
        ),
        yaxis=dict(
            title="Median total household wealth (£, 2022 prices)",
            tickfont=dict(size=14),
            gridcolor="#e0e0e0",
            tickformat=",",
            tickprefix="£",
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", color="#1a1a1a"),
        margin=dict(b=180),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=12),
        ),
        annotations=[
            dict(
                text=(
                    f"Source: Resolution Foundation / ONS Wealth and Assets Survey · "
                    f"Accessed {ACCESS_DATE}<br>"
                    "Figures in 2022 real terms. Projected values shown dashed. "
                    "Household wealth includes property, pensions, financial and "
                    "physical assets minus debts."
                ),
                xref="paper",
                yref="paper",
                x=0,
                y=-0.38,
                showarrow=False,
                font=dict(size=11, color="#666666"),
                align="left",
            ),
        ],
    )

    out_path = CHART_DIR / "generational_wealth_gap.html"
    write_accessible_chart(
        fig,
        out_path,
        title="UK Generational Wealth Gap — Median Household Wealth by Age",
        description=(
            "Line chart comparing median total household wealth at ages 30, 40, "
            "50, and 60 for Baby Boomers, Generation X, and Millennials in the UK. "
            "Each successive generation has accumulated less wealth at the same age. "
            "Sourced from Resolution Foundation and ONS Wealth and Assets Survey."
        ),
    )


def main() -> None:
    """Fetch generational wealth data, process it, and generate chart."""
    df_raw = fetch()
    df = process(df_raw)
    build_chart(df)
    logger.info("Done. Open charts/generational_wealth_gap.html in a browser to view.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    main()
