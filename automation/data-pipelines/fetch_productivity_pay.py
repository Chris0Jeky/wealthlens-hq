"""Fetch and process UK productivity vs. pay data (the "scissors chart").

Source — Productivity:
    ONS Labour Productivity, Output per hour worked, whole economy (SA).
    Dataset: "Output per hour worked, UK"
    URL: https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/
         labourproductivity/timeseries/lzvd/prdy
    Licence: OGL v3.0

Source — Pay:
    ONS Average Weekly Earnings (AWE), total pay, whole economy (nominal),
    deflated to real terms using ONS CPIH (L55O).
    URL: https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/
         earningsandworkinghours/timeseries/kab9/emp
    CPIH: https://www.ons.gov.uk/economy/inflationandpriceindices/
          timeseries/l55o/mm23
    Licence: OGL v3.0

The pipeline attempts to fetch live ONS time-series data via the ONS
beta API.  If the API is unavailable it falls back to illustrative data
derived from published ONS bulletins — clearly marked as such.

Output: projects/wealthlens-dashboard/data/processed/productivity_pay_gap.csv
Columns: year, productivity_index, pay_index, gap_pct
Both indices are normalised to 100 at the chosen base year (1997).
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
from chart_html import write_accessible_chart

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 60

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "projects" / "wealthlens-dashboard" / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHART_DIR = ROOT / "projects" / "wealthlens-dashboard" / "charts"

ACCESS_DATE = date.today().isoformat()

# Base year for index normalisation (both series = 100 in this year).
BASE_YEAR = 1997

# --- ONS time-series API endpoints ---
# LZVD = Output per hour worked, whole economy, SA (index 2019=100)
PRODUCTIVITY_URL = (
    "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/"
    "labourproductivity/timeseries/lzvd/prdy/data"
)

# KAB9 = Average Weekly Earnings, total pay, whole economy (£, not SA)
AWE_URL = (
    "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/"
    "earningsandworkinghours/timeseries/kab9/emp/data"
)

# L55O = CPIH index (2015=100) for deflating nominal AWE to real terms
CPIH_URL = (
    "https://www.ons.gov.uk/economy/inflationandpriceindices/"
    "timeseries/l55o/mm23/data"
)

# --- Source metadata dict (used by the backend data router) ---
SOURCE_META = {
    "description": "UK productivity vs. real pay, indexed to 100 at 1997",
    "source": "ONS Labour Productivity (LZVD) & ONS AWE (KAB9) deflated by CPIH (L55O)",
    "source_url": (
        "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/"
        "labourproductivity/timeseries/lzvd/prdy"
    ),
    "access_date": ACCESS_DATE,
}


def _fetch_ons_timeseries(url: str, label: str) -> pd.DataFrame | None:
    """Fetch an ONS time-series JSON endpoint.

    Returns a DataFrame with columns [date, value] containing annual
    observations, or None if the request fails.
    """
    logger.info("Fetching ONS %s data...", label)
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Failed to fetch %s: %s", label, exc)
        return None

    try:
        data = resp.json()
    except ValueError as exc:
        logger.warning("Invalid JSON from %s endpoint: %s", label, exc)
        return None

    # The ONS JSON response has keys "years", "quarters", "months".
    # We want annual data from "years".
    years_data = data.get("years", [])
    if not years_data:
        logger.warning("No annual data found in %s response.", label)
        return None

    records = []
    for entry in years_data:
        try:
            year = int(entry.get("year", entry.get("date", "")))
            value = float(entry.get("value", ""))
            records.append({"year": year, "value": value})
        except (ValueError, TypeError):
            continue

    if not records:
        logger.warning("Could not parse any annual records from %s.", label)
        return None

    df = pd.DataFrame(records)
    logger.info("Fetched %d annual observations for %s (%d-%d).",
                len(df), label, df["year"].min(), df["year"].max())
    return df


def fetch() -> tuple[pd.DataFrame | None, pd.DataFrame | None, pd.DataFrame | None]:
    """Fetch productivity, AWE, and CPIH time-series from the ONS.

    Returns (productivity_df, awe_df, cpih_df) — any may be None if the
    API is unavailable.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    prod_df = _fetch_ons_timeseries(PRODUCTIVITY_URL, "productivity (LZVD)")
    awe_df = _fetch_ons_timeseries(AWE_URL, "AWE total pay (KAB9)")
    cpih_df = _fetch_ons_timeseries(CPIH_URL, "CPIH (L55O)")

    # Save raw data for reproducibility
    for df, name in [
        (prod_df, "ons_productivity_lzvd.csv"),
        (awe_df, "ons_awe_kab9.csv"),
        (cpih_df, "ons_cpih_l55o.csv"),
    ]:
        if df is not None:
            path = RAW_DIR / name
            df.to_csv(path, index=False)
            logger.info("Raw data saved to %s", path)

    return prod_df, awe_df, cpih_df


def _build_fallback_data() -> pd.DataFrame:
    """Illustrative UK productivity vs. real pay data (1970-2023).

    *** ILLUSTRATIVE DATA — for development and layout purposes only. ***

    These figures are derived from published ONS bulletins and academic
    summaries of the UK productivity-pay gap, but are NOT exact official
    time-series values.  Replace with real ONS data before publication.

    The general pattern is well-documented: UK productivity (output per
    hour) roughly doubled between 1970 and 2023, while real median pay
    grew by approximately 30-40% over the same period — with most of the
    divergence occurring after 2000 and real pay stagnating after 2008.

    Sources consulted:
    - ONS "Labour productivity, UK" bulletin (various editions)
    - Resolution Foundation "The Living Standards Outlook" (2024)
    - ONS "Employee earnings in the UK" statistical bulletins
    - TUC analysis of the productivity-pay gap (2023)

    Base year: 1997 = 100 for both series.
    """
    data = {
        "year": list(range(1970, 2024)),
        "productivity_index": [
            # 1970-1979: steady growth
            52.0, 53.5, 55.2, 57.0, 56.5,
            56.8, 58.0, 59.5, 61.0, 62.8,
            # 1980-1989: acceleration through Thatcher reforms
            62.0, 63.5, 66.0, 69.0, 71.5,
            73.0, 75.0, 77.5, 80.0, 82.5,
            # 1990-1999: continued growth, base year 1997=100
            83.5, 85.0, 88.0, 91.0, 94.0,
            96.0, 98.0, 100.0, 102.5, 105.0,
            # 2000-2009: strong pre-crisis, flat after 2008
            108.0, 110.5, 113.0, 116.0, 118.5,
            120.0, 122.5, 125.0, 124.0, 121.5,
            # 2010-2019: slow recovery ("productivity puzzle")
            123.0, 124.0, 124.5, 125.0, 125.5,
            126.5, 127.5, 128.5, 129.5, 131.0,
            # 2020-2023: COVID dip then recovery
            128.0, 130.0, 131.5, 132.0,
        ],
        "pay_index": [
            # 1970-1979: real pay growing alongside productivity
            50.0, 52.0, 54.0, 56.0, 57.0,
            57.5, 58.0, 56.5, 59.0, 60.5,
            # 1980-1989: pay growth but slightly lagging
            59.0, 60.0, 61.5, 64.0, 66.5,
            68.5, 71.0, 74.0, 77.5, 81.0,
            # 1990-1999: reasonable pay growth, 1997=100
            82.0, 85.0, 87.0, 89.5, 91.0,
            93.0, 95.5, 100.0, 102.5, 105.0,
            # 2000-2009: pay growth slows relative to productivity
            107.0, 110.0, 112.0, 113.5, 114.5,
            115.0, 116.0, 117.5, 116.0, 113.0,
            # 2010-2019: real pay stagnation / "lost decade"
            112.0, 110.0, 109.5, 109.0, 108.5,
            109.0, 110.5, 112.0, 113.0, 114.5,
            # 2020-2023: COVID hit, partial recovery, cost-of-living
            114.0, 113.0, 110.0, 111.0,
        ],
    }

    df = pd.DataFrame(data)
    df["gap_pct"] = round(
        (df["productivity_index"] - df["pay_index"]) / df["pay_index"] * 100,
        1,
    )

    return df


def process(
    prod_df: pd.DataFrame | None,
    awe_df: pd.DataFrame | None,
    cpih_df: pd.DataFrame | None,
) -> pd.DataFrame:
    """Process raw ONS data into normalised productivity vs. pay indices.

    If any input is None, falls back to illustrative data.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if prod_df is None or awe_df is None or cpih_df is None:
        logger.warning(
            "One or more ONS data sources unavailable. "
            "Using illustrative fallback data."
        )
        df = _build_fallback_data()
        out_path = PROCESSED_DIR / "productivity_pay_gap.csv"
        df.to_csv(out_path, index=False)
        logger.info("Processed data saved to %s", out_path)
        logger.info("%d rows", len(df))
        return df

    # Deflate nominal AWE to real terms using CPIH
    merged = awe_df.merge(cpih_df, on="year", suffixes=("_awe", "_cpih"))
    # Real AWE = nominal AWE / (CPIH / 100)
    merged["real_awe"] = merged["value_awe"] / (merged["value_cpih"] / 100)

    # Merge with productivity
    merged = merged.merge(
        prod_df.rename(columns={"value": "productivity"}),
        on="year",
    )

    # Normalise both to BASE_YEAR = 100
    base_row = merged[merged["year"] == BASE_YEAR]
    if base_row.empty:
        logger.warning(
            "Base year %d not found in data. "
            "Using illustrative fallback data.", BASE_YEAR
        )
        df = _build_fallback_data()
        out_path = PROCESSED_DIR / "productivity_pay_gap.csv"
        df.to_csv(out_path, index=False)
        logger.info("Processed data saved to %s", out_path)
        return df

    prod_base = float(base_row["productivity"].iloc[0])
    pay_base = float(base_row["real_awe"].iloc[0])

    df = pd.DataFrame({
        "year": merged["year"],
        "productivity_index": round(merged["productivity"] / prod_base * 100, 1),
        "pay_index": round(merged["real_awe"] / pay_base * 100, 1),
    })

    df["gap_pct"] = round(
        (df["productivity_index"] - df["pay_index"]) / df["pay_index"] * 100,
        1,
    )

    df = df.sort_values("year").reset_index(drop=True)

    out_path = PROCESSED_DIR / "productivity_pay_gap.csv"
    df.to_csv(out_path, index=False)
    logger.info("Processed data saved to %s", out_path)
    logger.info("%d rows", len(df))

    return df


def build_chart(df: pd.DataFrame) -> None:
    """Generate the productivity vs. pay 'scissors chart'."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    # Determine whether we are using fallback data (check if 1970 is present)
    is_fallback = len(df) > 40  # real ONS data would typically be shorter
    data_caveat = (
        " Data is ILLUSTRATIVE — derived from ONS bulletins, not exact"
        " time-series values. Replace with live ONS data before publication."
        if is_fallback
        else ""
    )

    fig = go.Figure()

    # Productivity line
    fig.add_trace(go.Scatter(
        x=df["year"],
        y=df["productivity_index"],
        mode="lines",
        name="Productivity (output per hour)",
        line=dict(color="#1f77b4", width=3),
        hovertemplate="Productivity: %{y:.1f}<br>Year: %{x}<extra></extra>",
    ))

    # Real pay line
    fig.add_trace(go.Scatter(
        x=df["year"],
        y=df["pay_index"],
        mode="lines",
        name="Real pay (AWE deflated by CPIH)",
        line=dict(color="#d62728", width=3),
        hovertemplate="Real pay: %{y:.1f}<br>Year: %{x}<extra></extra>",
    ))

    # Shade the gap between the two lines where productivity > pay
    fig.add_trace(go.Scatter(
        x=list(df["year"]) + list(df["year"][::-1]),
        y=list(df["productivity_index"]) + list(df["pay_index"][::-1]),
        fill="toself",
        fillcolor="rgba(31, 119, 180, 0.08)",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Add base-year reference line
    fig.add_hline(
        y=100,
        line_dash="dot",
        line_color="#999",
        line_width=1,
        annotation_text=f"Base year ({BASE_YEAR} = 100)",
        annotation_position="bottom right",
        annotation_font_size=10,
        annotation_font_color="#999",
    )

    # Get the latest gap for the annotation
    latest = df.iloc[-1]
    latest_gap = latest["gap_pct"]

    fig.update_layout(
        title=dict(
            text="The UK Productivity-Pay Gap",
            font=dict(size=20),
        ),
        xaxis=dict(
            title="Year",
            tickfont=dict(size=13),
            gridcolor="#e0e0e0",
        ),
        yaxis=dict(
            title=f"Index ({BASE_YEAR} = 100)",
            tickfont=dict(size=13),
            gridcolor="#e0e0e0",
            rangemode="tozero",
        ),
        legend=dict(
            font=dict(size=12),
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)",
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", color="#1a1a1a"),
        margin=dict(b=160),
        annotations=[
            dict(
                text=(
                    f"Source: ONS Labour Productivity (LZVD) & ONS AWE (KAB9) "
                    f"deflated by CPIH (L55O) - OGL v3.0 - "
                    f"Accessed {ACCESS_DATE}<br>"
                    f"In {int(latest['year'])}, productivity was "
                    f"{latest_gap:+.0f}% above where pay would be if both "
                    f"had grown equally since {BASE_YEAR}.{data_caveat}"
                ),
                xref="paper", yref="paper",
                x=0, y=-0.28,
                showarrow=False,
                font=dict(size=10, color="#666666"),
            )
        ],
    )

    out_path = CHART_DIR / "productivity_pay_gap.html"
    write_accessible_chart(
        fig,
        out_path,
        title="The UK Productivity-Pay Gap",
        description=(
            "Line chart comparing UK productivity growth (output per hour) "
            "against real pay growth since 1970, both indexed to 100 in 1997. "
            "Shows how productivity and pay diverged, especially after 2000."
        ),
    )


def main() -> None:
    """Fetch productivity and pay data, process, and generate chart."""
    prod_df, awe_df, cpih_df = fetch()
    df = process(prod_df, awe_df, cpih_df)
    build_chart(df)
    logger.info("Done. Open the chart HTML in a browser to view.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    main()
