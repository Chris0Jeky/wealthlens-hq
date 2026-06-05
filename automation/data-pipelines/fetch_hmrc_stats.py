"""Fetch HMRC Capital Gains Tax statistics.

Source: HMRC Capital Gains Tax Statistics (OGL v3.0)
Shows concentration of capital gains among top taxpayers.
"""

from __future__ import annotations

import logging
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from _cells import to_finite_float
from chart_html import write_accessible_chart
from http_retry import fetch_with_retry

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "projects" / "wealthlens-dashboard" / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHART_DIR = ROOT / "projects" / "wealthlens-dashboard" / "charts"

# Table 2: taxpayer numbers/gains by size of gain
TABLE2_URL = (
    "https://assets.publishing.service.gov.uk/media/"
    "6878ac562bad77c3dae4dcef/Table_2_2025_Size_of_gain.ods"
)

# Table 1: overall trends by year
TABLE1_URL = (
    "https://assets.publishing.service.gov.uk/media/"
    "6878ac497ea209168636386e/Table_1_2025_Taxpayer_numbers_gains_and_tax_liabilities.ods"
)

ACCESS_DATE = date.today().isoformat()

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 60


def fetch() -> dict[str, Path]:
    """Download HMRC CGT ODS files."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}

    for name, url in [("table2", TABLE2_URL), ("table1", TABLE1_URL)]:
        out_path = RAW_DIR / f"hmrc_cgt_{name}.ods"
        logger.info("Downloading HMRC CGT %s...", name)
        resp = fetch_with_retry(url, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        logger.info("Saved to %s (%d KB)", out_path, len(resp.content) // 1024)
        paths[name] = out_path

    return paths


def process(paths: dict[str, Path]) -> pd.DataFrame:
    """Extract capital gains concentration data from Table 2.

    Sheet 2_1a (latest individual data) structure:
      Rows 0-9: metadata/notes
      Row 10: header (Range of gain, Number of individuals, Amounts of gains, Amounts of tax)
      Rows 11-23: gain band data (lower limit, thousands, £millions, £millions)
      Row 24: "All" totals row
    Numbers in thousands (taxpayers) and £millions (gains/tax).
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    table2_path = paths["table2"]
    xl = pd.ExcelFile(table2_path, engine="odf")

    # Pick the most recent individual taxpayer sheet (2_1a pattern)
    target_sheet = None
    for name in xl.sheet_names:
        if "1a" in str(name):
            target_sheet = name
            break
    if target_sheet is None:
        target_sheet = next(s for s in xl.sheet_names if str(s) != "Contents")

    logger.info("Reading sheet: '%s'", target_sheet)
    df_raw = pd.read_excel(table2_path, sheet_name=target_sheet, header=None, engine="odf")

    # Find the header row containing "Range" or "Number"
    header_row = None
    for i in range(len(df_raw)):
        row_str = " ".join(str(v).lower() for v in df_raw.iloc[i].values if pd.notna(v))
        if "range" in row_str and "number" in row_str:
            header_row = i
            break

    if header_row is None:
        logger.error("Could not find header row. Dumping first 15 rows:")
        for i in range(min(15, len(df_raw))):
            logger.debug("%d: %s", i, [str(v)[:40] for v in df_raw.iloc[i].values if pd.notna(v)])
        sys.exit(1)

    # Columns: 0=band lower limit, 1=num individuals (thousands), 2=gains (£m), 3=tax (£m)
    records = []
    for i in range(header_row + 1, len(df_raw)):
        band_raw = str(df_raw.iloc[i, 0]).strip()
        if not band_raw or band_raw == "nan":
            continue

        gains_raw: object = df_raw.iloc[i, 2]
        count_raw: object = df_raw.iloc[i, 1]

        # Parse gains — skip rows with "[Less than 1]" or similar.
        # to_finite_float also rejects a blank (NaN) cell so it can't leak past
        # the share-of-gains division below.
        gains = to_finite_float(gains_raw)
        if gains is None:
            continue

        # Parse the taxpayer count. HMRC suppresses some bands' counts for disclosure
        # control while STILL publishing the band's gains, so a blank/suppressed count
        # must NOT drop the row — that would discard valid gains data (codex review).
        # Keep the row with count=None (None -> NaN in the float column, the honest
        # representation of a suppressed count; share_of_taxpayers is then NaN for that
        # band only). to_finite_float turns a blank/NaN cell into None rather than a
        # fabricated number, so nothing spurious is published.
        count = to_finite_float(count_raw)

        # Build readable band label
        band_lower: float = 0.0
        if band_raw.lower() == "all":
            label = "All"
        else:
            band_lower_parsed = to_finite_float(band_raw)
            if band_lower_parsed is None:
                # Non-numeric band label (e.g. a descriptive range): keep the raw
                # text as the label and leave the lower bound at 0.
                label = band_raw
            else:
                band_lower = band_lower_parsed
                label = f"£{int(band_lower):,}+"

        records.append({
            "gain_band": label,
            "band_lower": band_lower,
            "num_taxpayers_thousands": count,
            "total_gains_millions": gains,
        })

    df = pd.DataFrame(records)

    # Separate totals row from band data
    totals = df[df["gain_band"] == "All"]
    df = df[df["gain_band"] != "All"].copy()

    if df.empty:
        logger.error("No data extracted from HMRC Table 2.")
        sys.exit(1)

    # Use the "All" row total if available, otherwise sum
    total_gains = float(totals["total_gains_millions"].iloc[0]) if not totals.empty else df["total_gains_millions"].sum()
    total_taxpayers = float(totals["num_taxpayers_thousands"].iloc[0]) if not totals.empty else df["num_taxpayers_thousands"].sum()

    df["share_of_gains_pct"] = (df["total_gains_millions"] / total_gains * 100).round(1)
    df["share_of_taxpayers_pct"] = (df["num_taxpayers_thousands"] / total_taxpayers * 100).round(1)

    # Sort by band (ascending) for the chart, cumulative from top for analysis
    df = df.sort_values("band_lower").reset_index(drop=True)

    # Cumulative from top (reverse order)
    df_rev = df.sort_values("band_lower", ascending=False)
    df["cumul_gains_from_top_pct"] = df_rev["share_of_gains_pct"].cumsum().values[::-1]
    df["cumul_taxpayers_from_top_pct"] = df_rev["share_of_taxpayers_pct"].cumsum().values[::-1]

    out_path = PROCESSED_DIR / "hmrc_cgt_concentration.csv"
    df.to_csv(out_path, index=False)
    logger.info("Processed: %d bands, total gains £%s m, %s k taxpayers", len(df), f"{total_gains:,.0f}", f"{total_taxpayers:,.0f}")

    # Log the headline stat
    top_bands = df[df["band_lower"] >= 1_000_000]
    top_gains_share = top_bands["share_of_gains_pct"].sum()
    top_taxpayer_share = top_bands["share_of_taxpayers_pct"].sum()
    logger.info("Taxpayers with gains >= £1m: %.1f%% of taxpayers, %.1f%% of all gains", top_taxpayer_share, top_gains_share)

    return df


def build_chart(df: pd.DataFrame) -> None:
    """Generate capital gains concentration chart."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig = go.Figure()

    # Bar chart: share of gains vs share of taxpayers per band
    fig.add_trace(go.Bar(
        x=df["gain_band"],
        y=df["share_of_gains_pct"],
        name="Share of total gains",
        marker_color=[
            "#d62728" if pct > 20 else "#ff7f0e" if pct > 10 else "#1f77b4"
            for pct in df["share_of_gains_pct"]
        ],
        text=[f"{pct:.0f}%" if pd.notna(pct) else "n/a" for pct in df["share_of_gains_pct"]],
        textposition="outside",
        textfont=dict(size=12),
        hovertemplate=(
            "%{x}<br>"
            "Share of total gains: %{y:.1f}%<br>"
            "Taxpayers: %{customdata[0]}<br>"
            "<extra></extra>"
        ),
        customdata=[
            [f"{pct:.1f}% of total" if pd.notna(pct) else "suppressed"]
            for pct in df["share_of_taxpayers_pct"]
        ],
    ))

    fig.add_trace(go.Bar(
        x=df["gain_band"],
        y=df["share_of_taxpayers_pct"],
        name="Share of taxpayers",
        marker_color="#aec7e8",
        text=[f"{pct:.0f}%" if pd.notna(pct) else "n/a" for pct in df["share_of_taxpayers_pct"]],
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="%{x}<br>Share of taxpayers: %{y:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text="Capital Gains Concentration by Size of Gain — UK",
            font=dict(size=18),
        ),
        xaxis=dict(
            title="Size of gain (lower threshold)",
            tickfont=dict(size=11),
            tickangle=-30,
            gridcolor="#e0e0e0",
            categoryorder="array",
            categoryarray=df["gain_band"].tolist(),
        ),
        yaxis=dict(
            title="Share of total gains (%)",
            ticksuffix="%",
            tickfont=dict(size=14),
            gridcolor="#e0e0e0",
        ),
        barmode="group",
        legend=dict(font=dict(size=12)),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", color="#1a1a1a"),
        margin=dict(b=140),
        annotations=[
            dict(
                text=(
                    f"Source: HMRC Capital Gains Tax Statistics · "
                    f"OGL v3.0 · Accessed {ACCESS_DATE}<br>"
                    f"A small number of taxpayers with very large gains "
                    f"account for the vast majority of total capital gains."
                ),
                xref="paper", yref="paper",
                x=0, y=-0.30,
                showarrow=False,
                font=dict(size=11, color="#666666"),
            )
        ],
    )

    out_path = CHART_DIR / "hmrc_cgt_concentration.html"
    write_accessible_chart(
        fig,
        out_path,
        title="Capital Gains Concentration by Size of Gain",
        description="Bar chart showing how capital gains are concentrated among a small number of high-gain taxpayers in the UK, sourced from HMRC.",
    )


def main() -> None:
    """Fetch HMRC CGT data and generate chart."""
    paths = fetch()
    df = process(paths)
    build_chart(df)
    logger.info("Done. Open the chart HTML in a browser to view.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    main()
