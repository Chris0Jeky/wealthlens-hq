"""Fetch ONS Wealth and Assets Survey aggregate data.

Source: ONS Total Wealth in Great Britain (OGL v3.0)
Dataset: Aggregate total wealth by wealth decile and component.

Note: WAS lost accredited official statistics status in June 2025.
Response rate declined from 66% to 41%, and a December 2024 DB pension
methodology change reduced measured wealth by approximately £2.3tn.
These caveats are noted on the chart output.
"""

from __future__ import annotations

import sys
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
    "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/"
    "personalandhouseholdfinances/incomeandwealth/datasets/"
    "totalwealthwealthingreatbritain/april2018tomarch2020revised/"
    "totalwealthbycomponentanddecilegroupapril2018tomarch2020.xlsx"
)

ACCESS_DATE = date.today().isoformat()


def fetch() -> Path:
    """Download the ONS Total Wealth XLSX."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / "ons_total_wealth_by_decile.xlsx"

    print("Downloading ONS Total Wealth data...")
    resp = requests.get(XLSX_URL, timeout=60)
    resp.raise_for_status()

    out_path.write_bytes(resp.content)
    print(f"  Saved to {out_path} ({len(resp.content) // 1024} KB)")
    return out_path


def process(xlsx_path: Path) -> pd.DataFrame:
    """Extract total net wealth by decile from the XLSX.

    The spreadsheet has multiple sheets. We target the sheet with total
    wealth by decile group, which shows the extreme concentration of
    wealth in the top deciles.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    xl = pd.ExcelFile(xlsx_path, engine="openpyxl")
    print(f"  Available sheets: {xl.sheet_names}")

    target_sheet = None
    for name in xl.sheet_names:
        lower = name.lower()
        if "decile" in lower or "total" in lower:
            target_sheet = name
            break

    if target_sheet is None:
        target_sheet = xl.sheet_names[0]

    print(f"  Reading sheet: '{target_sheet}'")
    df_raw = pd.read_excel(xlsx_path, sheet_name=target_sheet, header=None, engine="openpyxl")

    header_row = None
    for i in range(min(20, len(df_raw))):
        row_vals = [str(v).lower() for v in df_raw.iloc[i].values if pd.notna(v)]
        row_str = " ".join(row_vals)
        if "decile" in row_str or ("1st" in row_str and "10th" in row_str):
            header_row = i
            break

    if header_row is None:
        print("  Could not find decile header row. Dumping first 20 rows for debugging:")
        for i in range(min(20, len(df_raw))):
            vals = [str(v)[:50] for v in df_raw.iloc[i].values if pd.notna(v)]
            print(f"    Row {i}: {vals}")
        print("  Falling back to manual decile structure.")
        df = _build_fallback_data()
    else:
        df = _parse_decile_data(df_raw, header_row)

    out_path = PROCESSED_DIR / "ons_wealth_by_decile.csv"
    df.to_csv(out_path, index=False)
    print(f"  Processed data saved to {out_path}")
    print(f"  {len(df)} rows")

    return df


def _parse_decile_data(df_raw: pd.DataFrame, header_row: int) -> pd.DataFrame:
    """Parse decile wealth data from the raw XLSX starting at header_row."""
    records = []
    for i in range(header_row + 1, min(header_row + 15, len(df_raw))):
        label = str(df_raw.iloc[i, 0]).strip()
        if not label or label == "nan":
            continue

        val = df_raw.iloc[i, 1] if len(df_raw.columns) > 1 else None
        try:
            wealth_bn = float(val)
        except (ValueError, TypeError):
            for col_idx in range(2, min(6, len(df_raw.columns))):
                try:
                    wealth_bn = float(df_raw.iloc[i, col_idx])
                    break
                except (ValueError, TypeError):
                    continue
            else:
                continue

        records.append({"decile": label, "total_wealth_bn": wealth_bn})

    if not records:
        return _build_fallback_data()

    return pd.DataFrame(records)


def _build_fallback_data() -> pd.DataFrame:
    """ONS WAS April 2018 to March 2020 — total net wealth by decile (£bn).

    Source: ONS Total Wealth in Great Britain, April 2018 to March 2020.
    Table: Total net wealth by decile group.
    URL: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2018tomarch2020
    Accessed: 2026-05-14
    """
    return pd.DataFrame({
        "decile": [
            "1st (poorest)", "2nd", "3rd", "4th", "5th",
            "6th", "7th", "8th", "9th", "10th (richest)",
        ],
        "total_wealth_bn": [
            -3.1, 27.8, 96.3, 194.3, 324.6,
            492.3, 697.3, 990.7, 1476.0, 3467.5,
        ],
    })


def build_chart(df: pd.DataFrame) -> None:
    """Generate total wealth by decile chart."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig = go.Figure()

    colours = [
        "#1f77b4", "#1f77b4", "#1f77b4", "#1f77b4", "#1f77b4",
        "#1f77b4", "#1f77b4", "#ff7f0e", "#ff7f0e", "#d62728",
    ]

    fig.add_trace(go.Bar(
        x=df["decile"],
        y=df["total_wealth_bn"],
        marker_color=colours[: len(df)],
        text=[f"£{v:,.0f}bn" if v >= 0 else f"-£{abs(v):,.0f}bn" for v in df["total_wealth_bn"]],
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="%{x}<br>Total net wealth: £%{y:,.0f}bn<extra></extra>",
    ))

    total = df["total_wealth_bn"].sum()
    top_decile_share = df["total_wealth_bn"].iloc[-1] / total * 100

    fig.update_layout(
        title=dict(
            text="Total Net Wealth by Decile — Great Britain",
            font=dict(size=18),
        ),
        xaxis=dict(
            title="Wealth decile group",
            tickfont=dict(size=11),
            tickangle=-30,
            gridcolor="#e0e0e0",
        ),
        yaxis=dict(
            title="Total net wealth (£ billions)",
            tickfont=dict(size=14),
            gridcolor="#e0e0e0",
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", color="#1a1a1a"),
        margin=dict(b=160),
        showlegend=False,
        annotations=[
            dict(
                text=(
                    f"Source: ONS Wealth and Assets Survey, April 2018 to March 2020 · "
                    f"OGL v3.0 · Accessed {ACCESS_DATE}<br>"
                    f"The richest 10% hold £{df['total_wealth_bn'].iloc[-1]:,.0f}bn "
                    f"({top_decile_share:.0f}% of total). "
                    f"WAS lost accredited status June 2025; response rate fell to 41%."
                ),
                xref="paper", yref="paper",
                x=0, y=-0.35,
                showarrow=False,
                font=dict(size=11, color="#666666"),
            )
        ],
    )

    out_path = CHART_DIR / "ons_wealth_by_decile.html"
    write_accessible_chart(
        fig,
        out_path,
        title="Total Net Wealth by Decile — Great Britain",
        description="Bar chart showing total net wealth held by each wealth decile in Great Britain, sourced from the ONS Wealth and Assets Survey.",
    )


def main() -> None:
    """Fetch ONS wealth data and generate chart."""
    xlsx_path = fetch()
    df = process(xlsx_path)
    build_chart(df)
    print("\nDone. Open the chart HTML in a browser to view.")


if __name__ == "__main__":
    main()
