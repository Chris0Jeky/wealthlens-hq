"""Fetch official HBAI regional child low-income estimates after housing costs.

The former CiLIF attribution was unsupported: that release was BHC and the
legacy constants had no verified table. Never use them as a fetch fallback.
"""
from __future__ import annotations

import io
import json
import logging
import xml.etree.ElementTree as ET
import zipfile
from datetime import date
from decimal import Decimal, InvalidOperation
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
    "households-below-average-income-for-financial-years-ending-1995-to-2024"
)
DOWNLOAD_URL = (
    "https://assets.publishing.service.gov.uk/media/6836dae29411f0341f323689/"
    "HBAI_2324_ods_table_pack.zip"
)
WORKBOOK = "children-hbai-timeseries-1994-95-2023-24-tables.ods"
PERIOD = "2021/22 to 2023/24 (three-year average)"
PERIOD_COLUMN = "21/22-23/241"  # Final 1 is DWP's note marker, not part of the year.
ACCESS_DATE = date.today().isoformat()
SOURCE = "DWP Households Below Average Income (HBAI), tables 4.16ts and 4.17ts"
MEASURE = "Children below 60% of contemporary median equivalised disposable household income after housing costs"
NS = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}
TABLE_NAME = "{" + NS["table"] + "}name"
TEXT_P = "{" + NS["text"] + "}p"
REGIONS = {
    "North East": "North East",
    "North West": "North West",
    "Yorkshire and the Humber": "Yorkshire and The Humber",
    "East Midlands": "East Midlands",
    "West Midlands": "West Midlands",
    "East": "East of England",
    "London": "London",
    "South East": "South East",
    "South West": "South West",
    "Wales": "Wales",
    "Scotland": "Scotland",
    "Northern Ireland": "Northern Ireland",
}
logger = logging.getLogger(__name__)


def _read_ahc_table(root: ET.Element, sheet: str, title: str, unit: str) -> dict[str, Decimal]:
    """Read displayed cells, avoiding the extra precision hidden in ODS values."""
    matches = [t for t in root.findall(".//table:table", NS) if t.get(TABLE_NAME) == sheet]
    if len(matches) != 1:
        raise ValueError(f"Missing or duplicate HBAI table: {sheet}")
    rows = []
    for element_row in matches[0].findall("table:table-row", NS):
        cells: list[str] = []
        for cell in element_row:
            text = " ".join("".join(p.itertext()) for p in cell.findall("text:p", NS)).strip()
            repeat = int(cell.get("{" + NS["table"] + "}number-columns-repeated", "1"))
            cells.extend([text] * min(repeat, 64))
        rows.append(cells)
    if not rows or not rows[0][0].startswith(title):
        raise ValueError(f"Unexpected HBAI statistic: {sheet}")
    headers = [(i, r.index(PERIOD_COLUMN)) for i, r in enumerate(rows) if PERIOD_COLUMN in r]
    if len(headers) != 1 or not any(unit in r for r in rows):
        raise ValueError(f"Missing HBAI period or units: {sheet}")
    header_row, column = headers[0]
    sections = [i for i, r in enumerate(rows) if r and r[0] == "After Housing Costs"]
    if len(sections) != 1 or sections[0] <= header_row:
        raise ValueError(f"Missing or duplicate AHC section: {sheet}")
    section = rows[sections[0] + 1:]
    if not section or section[0][0] != "Region/Country (3-year average)":
        raise ValueError(f"Unexpected HBAI averaging basis: {sheet}")
    values = {}
    for row in section[1:]:
        label = row[0]
        if label not in REGIONS and not label.startswith("All children ("):
            continue  # England is an aggregate overlapping the English regions.
        key = REGIONS.get(label, "UK")
        if key in values or column >= len(row):
            raise ValueError(f"Duplicate or incomplete HBAI observation: {label}")
        try:
            value = Decimal(row[column])
        except InvalidOperation as exc:
            raise ValueError(f"Unavailable HBAI observation: {label}") from exc
        if not value.is_finite() or value < 0:
            raise ValueError(f"Invalid HBAI observation: {label}")
        values[key] = value
    if set(values) != {*REGIONS.values(), "UK"}:
        raise ValueError(f"Incomplete HBAI geography: {sheet}")
    return values


def parse_workbook(content: bytes) -> pd.DataFrame:
    """Extract rates and counts for the same AHC measure, geography and period."""
    with zipfile.ZipFile(io.BytesIO(content)) as workbook:
        root = ET.fromstring(workbook.read("content.xml"))
    rates = _read_ahc_table(root, "4_16ts", "Table 4.16ts: Percentage of children", "Percentage of children")
    counts = _read_ahc_table(root, "4_17ts", "Table 4.17ts: Number of children", "Number of children (millions)")
    if any(value > 100 for value in rates.values()):
        raise ValueError("HBAI rates outside percentage range")
    # These are the official DISPLAYED values: whole percentages and 0.1 million.
    # Unit conversion only, never infer counts from rounded rates or vice versa.
    return pd.DataFrame([
        {
            "region": region,
            "child_poverty_pct": float(rates[region]),
            "children_in_poverty": int(counts[region] * 1_000_000),
            "national_avg_pct": float(rates["UK"]),
            "above_national_avg": rates[region] > rates["UK"],
        }
        for region in REGIONS.values()
    ]).sort_values("child_poverty_pct", ascending=False).reset_index(drop=True)


def fetch() -> tuple[pd.DataFrame, bool]:
    """Download the pinned official table pack; any failure aborts publication."""
    response = requests.get(DOWNLOAD_URL, timeout=60, allow_redirects=False)
    response.raise_for_status()
    if response.status_code != 200:
        raise ValueError("Unexpected HBAI download response")
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        content = archive.read(WORKBOOK)
    frame = parse_workbook(content)  # Validate before writing any output.
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / WORKBOOK).write_bytes(content)
    return frame, False


def process(df_raw: pd.DataFrame, *, is_fallback: bool) -> pd.DataFrame:
    """Write official observations and their reproducible provenance sidecar."""
    if is_fallback:
        raise ValueError("Unverified legacy child-poverty fallback must not be published")
    df = df_raw.copy()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DIR / "child_poverty_by_region.csv", index=False)
    meta = {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "download_url": DOWNLOAD_URL,
        "archive_member": WORKBOOK,
        "tables": ["4.16ts", "4.17ts"],
        "access_date": ACCESS_DATE,
        "is_fallback": False,
        "data_type": "live_ons",
        "row_count": len(df),
        "period": PERIOD,
        "measure": MEASURE,
        "geography": "Nine English regions, Wales, Scotland and Northern Ireland",
        "rounding": "Published whole percentages; counts converted from published 0.1 million",
        "licence": "Open Government Licence v3.0",
        "update_pattern": "Annual; pinned release, not automatically the latest",
    }
    (PROCESSED_DIR / "child_poverty_by_region.meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
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
            text=f"Child Poverty by Region (AHC): {PERIOD}",
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
                    f'Source: <a href="{SOURCE_URL}">DWP HBAI, tables 4.16ts and 4.17ts</a>.<br>'
                    f"OGL v3.0 · Accessed {ACCESS_DATE}<br>"
                    f"Red bars indicate regions above the national average. "
                    f"{PERIOD}. Relative low income after housing costs."
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
        title="Child Poverty Rates by Region: UK (AHC)",
        description=(
            f"Horizontal bar chart of relative low income after housing costs across UK regions. "
            f"{PERIOD}. Published whole percentages and counts rounded to the nearest "
            "hundred thousand. The UK reference is published for the same period. "
            f"Source: {SOURCE}. {SOURCE_URL}. Accessed {ACCESS_DATE}."
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
