"""Fetch ONS Gross Disposable Household Income (GDHI) per head by region.

Source: ONS Regional Gross Disposable Household Income (OGL v3.0)
Dataset: GDHI per head at current prices, by ITL1 region.
Edition: 1997 to 2023.
URL: https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome/datasets/regionalgrossdisposablehouseholdincomegdhi
Accessed: 2026-05-16

Note: GDHI is income after taxes and benefits — the amount households
have available for spending or saving.  Per-head figures divide total
GDHI by the resident population of each region.  The ONS publishes at
ITL1 (nations/regions), ITL2 (counties/groups), and ITL3 (local
authority groups).  This pipeline extracts the ITL3 (local-authority
level) per-head data for the most recent year available, to show the
full range of regional inequality from Westminster to Blackpool.
"""

from __future__ import annotations

import logging
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
from chart_html import write_accessible_chart

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 90

try:
    from openpyxl.utils.exceptions import InvalidFileException
except ImportError:  # pragma: no cover
    InvalidFileException = type("InvalidFileException", (OSError,), {})  # type: ignore[assignment,misc]

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "projects" / "wealthlens-dashboard" / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHART_DIR = ROOT / "projects" / "wealthlens-dashboard" / "charts"

# Primary URL: latest ONS Regional GDHI XLSX (1997 to 2023 edition).
XLSX_URL = (
    "https://www.ons.gov.uk/file?uri=/economy/regionalaccounts/"
    "grossdisposablehouseholdincome/datasets/"
    "regionalgrossdisposablehouseholdincomegdhi/"
    "1997to2023/"
    "regionalgrossdisposablehouseholdincomeallitlregions2023.xlsx"
)

# Fallback URL: previous edition (1997 to 2022).
XLSX_FALLBACK_URL = (
    "https://www.ons.gov.uk/file?uri=/economy/regionalaccounts/"
    "grossdisposablehouseholdincome/datasets/"
    "regionalgrossdisposablehouseholdincomegdhi/"
    "1997to2022/"
    "regionalgrossdisposablehouseholdincomeallitlregions.xlsx"
)

ACCESS_DATE = date.today().isoformat()


def fetch() -> Path | None:
    """Download the ONS Regional GDHI XLSX.

    Tries the primary URL first, then the fallback.  Returns the path
    to the downloaded file, or None if both URLs fail (the pipeline
    will then use illustrative fallback data).
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / "ons_gdhi_by_region.xlsx"

    urls = [
        ("primary", XLSX_URL),
        ("fallback", XLSX_FALLBACK_URL),
    ]

    for label, url in urls:
        logger.info("Downloading ONS GDHI data (%s URL)...", label)
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("%s download failed: %s", label.capitalize(), exc)
            continue

        try:
            out_path.write_bytes(resp.content)
        except OSError as exc:
            logger.warning("Could not write file (%s: %s)", type(exc).__name__, exc)
            continue

        logger.info("Saved to %s (%d KB)", out_path, len(resp.content) // 1024)
        return out_path

    logger.error(
        "Both primary and fallback ONS GDHI download URLs failed. "
        "The ONS may have reorganised their download paths. "
        "Check: https://www.ons.gov.uk/economy/regionalaccounts/"
        "grossdisposablehouseholdincome/datasets/"
        "regionalgrossdisposablehouseholdincomegdhi — "
        "Falling back to illustrative data."
    )
    return None


def process(xlsx_path: Path | None) -> pd.DataFrame:
    """Extract GDHI per head by region from the XLSX.

    The ONS GDHI workbook has multiple sheets.  We look for a sheet
    containing "per head" data (typically named something like
    "Table 3" or containing "GDHI per head" in early rows).  The
    layout has region names in column 0-1 and year columns across
    the top.  We extract the most recent year's values.

    If the XLSX cannot be parsed, falls back to illustrative data
    sourced from the ONS 2023 GDHI bulletin.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if xlsx_path is None:
        logger.info("No XLSX available, using illustrative fallback data.")
        df = _build_fallback_data()
        return _save_and_return(df)

    try:
        xl = pd.ExcelFile(xlsx_path, engine="openpyxl")
    except (zipfile.BadZipFile, InvalidFileException, ValueError, OSError) as exc:
        logger.warning("Cannot open XLSX (%s: %s)", type(exc).__name__, exc)
        logger.warning("Falling back to illustrative data.")
        df = _build_fallback_data()
        return _save_and_return(df)

    logger.info("Available sheets: %s", xl.sheet_names)

    # Find the per-head sheet.  ONS naming varies between editions:
    # "Table 3", "GDHI per head", etc.
    target_sheet = _find_per_head_sheet(xl)
    if target_sheet is None:
        logger.warning("Could not find GDHI per-head sheet. Falling back.")
        df = _build_fallback_data()
        return _save_and_return(df)

    logger.info("Reading sheet: '%s'", target_sheet)
    try:
        df_raw = pd.read_excel(
            xlsx_path, sheet_name=target_sheet, header=None, engine="openpyxl",
        )
    except (zipfile.BadZipFile, InvalidFileException, ValueError, OSError) as exc:
        logger.warning("Cannot read sheet (%s: %s)", type(exc).__name__, exc)
        df = _build_fallback_data()
        return _save_and_return(df)

    df = _parse_gdhi_per_head(df_raw)
    if df is None or df.empty:
        logger.warning("Could not parse GDHI per-head data. Falling back.")
        df = _build_fallback_data()

    return _save_and_return(df)


def _save_and_return(df: pd.DataFrame) -> pd.DataFrame:
    """Save the processed DataFrame to CSV and return it."""
    out_path = PROCESSED_DIR / "ons_gdhi_by_region.csv"
    df.to_csv(out_path, index=False)
    logger.info("Processed data saved to %s", out_path)
    logger.info("%d rows across %d regions", len(df), df["region"].nunique())
    return df


def _find_per_head_sheet(xl: pd.ExcelFile) -> str | None:
    """Find the sheet containing GDHI per-head data.

    Strategy:
    1. Look for a sheet named "Table 3" (common in recent editions).
    2. Look for any sheet with "per head" in the name.
    3. Scan the first few rows of each sheet for "per head" text.
    """
    # Direct name match
    for name in xl.sheet_names:
        stripped = name.strip()
        if stripped == "Table 3":
            return name
        if "per head" in stripped.lower():
            return name

    # Content scan — read first 10 rows of each sheet
    for name in xl.sheet_names:
        try:
            df_peek = pd.read_excel(
                xl, sheet_name=name, header=None, nrows=10, engine="openpyxl",
            )
        except Exception:  # noqa: BLE001 — skip unreadable sheets
            continue

        for i in range(len(df_peek)):
            row_text = " ".join(
                str(v).lower() for v in df_peek.iloc[i].values if pd.notna(v)
            )
            if "per head" in row_text and "gdhi" in row_text:
                return name

    return None


def _parse_gdhi_per_head(df_raw: pd.DataFrame) -> pd.DataFrame | None:
    """Parse GDHI per-head values from the raw sheet.

    Expected layout (varies slightly between editions):
        - A title/header area in the first few rows
        - A row containing year columns (1997, 1998, ..., 2023)
        - Data rows with: ITL code, region name, values per year

    We extract the most recent year's values for all regions.
    """
    # Find the row containing year headers
    year_row = None
    years: list[int] = []
    year_cols: list[int] = []

    for i in range(min(20, len(df_raw))):
        row_years: list[int] = []
        row_year_cols: list[int] = []
        for col_idx in range(len(df_raw.columns)):
            val = df_raw.iloc[i, col_idx]
            try:
                year = int(float(str(val)))
                if 1990 <= year <= 2030:
                    row_years.append(year)
                    row_year_cols.append(col_idx)
            except (ValueError, TypeError):
                continue
        # A row with 5+ year values is likely the header
        if len(row_years) >= 5:
            year_row = i
            years = row_years
            year_cols = row_year_cols
            break

    if year_row is None:
        logger.warning("Could not find year header row in GDHI sheet.")
        return None

    logger.info(
        "Found %d years: %d-%d (header at row %d)",
        len(years), min(years), max(years), year_row,
    )

    # Use the most recent year
    latest_year = max(years)
    latest_col = year_cols[years.index(latest_year)]

    # Find the region name column — usually column 1 (after the ITL code)
    # Scan the data area to determine which column has text region names
    name_col = _find_name_column(df_raw, year_row)

    records: list[dict[str, object]] = []
    for i in range(year_row + 1, len(df_raw)):
        region = (
            str(df_raw.iloc[i, name_col]).strip()
            if pd.notna(df_raw.iloc[i, name_col])
            else ""
        )
        if not region or region == "nan" or region.startswith("Source"):
            continue

        val = df_raw.iloc[i, latest_col]
        try:
            gdhi = float(val)
        except (ValueError, TypeError):
            continue

        # Skip rows with non-positive values (section headers or footnotes)
        if gdhi <= 0:
            continue

        records.append({
            "region": region,
            "gdhi_per_head": round(gdhi, 0),
            "year": latest_year,
        })

    if not records:
        logger.warning("No GDHI per-head records extracted.")
        return None

    df = pd.DataFrame(records)
    df = df.sort_values("gdhi_per_head", ascending=False).reset_index(drop=True)

    logger.info(
        "Extracted %d regions. Highest: %s (%s), Lowest: %s (%s)",
        len(df),
        df.iloc[0]["region"],
        f"£{df.iloc[0]['gdhi_per_head']:,.0f}",
        df.iloc[-1]["region"],
        f"£{df.iloc[-1]['gdhi_per_head']:,.0f}",
    )

    return df


def _find_name_column(df_raw: pd.DataFrame, year_row: int) -> int:
    """Determine which column contains region names.

    Typically column 1 (after the ITL code in column 0), but we verify
    by checking which of the first few columns has the most non-numeric
    text values in the data rows.
    """
    best_col = 1
    best_count = 0

    for col in range(min(3, len(df_raw.columns))):
        text_count = 0
        for i in range(year_row + 1, min(year_row + 20, len(df_raw))):
            val = df_raw.iloc[i, col]
            if pd.notna(val):
                s = str(val).strip()
                if s and not s.replace(".", "").replace("-", "").isdigit():
                    text_count += 1
        if text_count > best_count:
            best_count = text_count
            best_col = col

    return best_col


def _build_fallback_data() -> pd.DataFrame:
    """Illustrative GDHI per head data by UK local authority area.

    These figures are illustrative values based on publicly available
    ONS GDHI per-head statistics.  They are rounded and should be
    replaced with live data from the ONS XLSX when possible.

    Source context: ONS Regional GDHI, 1997 to 2023.
    URL: https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome/datasets/regionalgrossdisposablehouseholdincomegdhi
    Accessed: 2026-05-16
    Licence: OGL v3.0

    IMPORTANT: These are illustrative values for development purposes.
    The pipeline will use real ONS data when the download succeeds.
    The actual ONS figures should be verified before publication.
    """
    # Selected regions showing the full range of UK GDHI inequality.
    # Values are approximate GDHI per head (pounds, current prices) for
    # the most recent available year, based on ONS published data.
    regions = [
        ("Kensington and Chelsea, and Hammersmith and Fulham", 79500),
        ("Westminster", 64800),
        ("Camden and City of London", 51200),
        ("Wandsworth", 38700),
        ("Richmond upon Thames", 35400),
        ("Surrey", 32100),
        ("Buckinghamshire", 30800),
        ("Hertfordshire", 29500),
        ("Edinburgh, City of", 27600),
        ("United Kingdom", 24800),
        ("South East", 26400),
        ("East of England", 24200),
        ("South West", 23600),
        ("Scotland", 22800),
        ("North West", 20400),
        ("West Midlands", 19800),
        ("Yorkshire and The Humber", 19600),
        ("Wales", 19200),
        ("North East", 18800),
        ("Northern Ireland", 18600),
        ("Tees Valley and Durham", 17800),
        ("East Wales", 21400),
        ("West Wales and The Valleys", 17400),
        ("Nottingham", 15800),
        ("Leicester", 15400),
        ("Blackpool", 14200),
    ]

    return pd.DataFrame({
        "region": [r[0] for r in regions],
        "gdhi_per_head": [r[1] for r in regions],
        "year": [2023] * len(regions),
    })


def build_chart(df: pd.DataFrame) -> None:
    """Generate a bar chart of GDHI per head by region, sorted high to low.

    Westminster and Blackpool are highlighted to show the extremes
    of regional income inequality.
    """
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    # Sort highest to lowest
    df_sorted = df.sort_values("gdhi_per_head", ascending=True).copy()

    # Limit to top/bottom regions for readability if there are many
    if len(df_sorted) > 40:
        top = df_sorted.tail(15)
        bottom = df_sorted.head(10)
        df_sorted = pd.concat([bottom, top]).drop_duplicates()
        df_sorted = df_sorted.sort_values("gdhi_per_head", ascending=True)

    # Colour logic: highlight specific regions
    highlight_high = {
        "Westminster", "Kensington and Chelsea, and Hammersmith and Fulham",
        "Camden and City of London",
    }
    highlight_low = {"Blackpool", "Nottingham", "Leicester"}
    uk_avg = {"United Kingdom"}

    colours = []
    for region in df_sorted["region"]:
        if region in highlight_high:
            colours.append("#d62728")  # Red — extreme wealth
        elif region in highlight_low:
            colours.append("#1f77b4")  # Blue — deprived areas
        elif region in uk_avg:
            colours.append("#2ca02c")  # Green — UK average
        else:
            colours.append("#aec7e8")  # Light blue — other regions

    year = df_sorted["year"].iloc[0]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_sorted["gdhi_per_head"],
        y=df_sorted["region"],
        orientation="h",
        marker_color=colours,
        text=[f"£{v:,.0f}" for v in df_sorted["gdhi_per_head"]],
        textposition="outside",
        textfont=dict(size=10),
        hovertemplate=(
            "%{y}<br>GDHI per head: £%{x:,.0f}<extra></extra>"
        ),
    ))

    # Find UK average for reference line
    uk_row = df_sorted[df_sorted["region"] == "United Kingdom"]
    uk_avg_val = uk_row["gdhi_per_head"].iloc[0] if not uk_row.empty else None

    shapes = []
    if uk_avg_val is not None:
        shapes.append(dict(
            type="line",
            x0=uk_avg_val, x1=uk_avg_val,
            y0=-0.5, y1=len(df_sorted) - 0.5,
            line=dict(color="#2ca02c", width=2, dash="dash"),
        ))

    # Determine if using real or fallback data
    is_fallback = len(df_sorted) < 30
    data_note = (
        "ILLUSTRATIVE DATA — verify against ONS source before publication. "
        if is_fallback
        else ""
    )

    fig.update_layout(
        title=dict(
            text=(
                "Gross Disposable Household Income per Head "
                f"by Region ({year})"
            ),
            font=dict(size=16),
        ),
        xaxis=dict(
            title="GDHI per head (£, current prices)",
            tickfont=dict(size=12),
            tickprefix="£",
            tickformat=",",
            gridcolor="#e0e0e0",
        ),
        yaxis=dict(
            tickfont=dict(size=10),
            gridcolor="#e0e0e0",
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="system-ui, -apple-system, sans-serif",
            color="#1a1a1a",
        ),
        margin=dict(l=280, b=120, r=80),
        showlegend=False,
        shapes=shapes,
        height=max(500, len(df_sorted) * 28),
        annotations=[
            dict(
                text=(
                    f"{data_note}"
                    "Source: ONS Regional Gross Disposable Household "
                    f"Income · OGL v3.0 · Accessed {ACCESS_DATE}"
                    "<br>"
                    "GDHI = income after taxes and benefits. "
                    "Red = highest areas, blue = most deprived, "
                    "green dashed line = UK average."
                ),
                xref="paper", yref="paper",
                x=0, y=-0.12,
                showarrow=False,
                font=dict(size=10, color="#666666"),
            )
        ],
    )

    out_path = CHART_DIR / "ons_gdhi_by_region.html"
    write_accessible_chart(
        fig,
        out_path,
        title=f"GDHI per Head by Region ({year})",
        description=(
            "Horizontal bar chart showing gross disposable household "
            f"income per head across UK regions in {year}, sorted from "
            "highest to lowest. Westminster and wealthy London boroughs "
            "are highlighted in red; deprived areas like Blackpool in "
            "blue."
        ),
    )


def main() -> None:
    """Fetch ONS GDHI data, process, and generate chart."""
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
