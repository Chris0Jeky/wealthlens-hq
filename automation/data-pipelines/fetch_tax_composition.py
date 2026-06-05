"""Fetch UK tax revenue composition data and generate chart.

Source: HMRC Tax and NIC Receipts (OGL v3.0)
Shows the proportion of tax revenue from work (Income Tax + NICs) vs
wealth (Capital Gains Tax + Inheritance Tax + Stamp Duty Land Tax).

The key insight: approximately 93% of selected UK tax revenue comes
from taxes on work and income, while only ~7% comes from taxes on
wealth (CGT, IHT, SDLT).

HMRC publishes monthly/annual receipts data as XLSX at:
https://www.gov.uk/government/statistics/hmrc-tax-and-nics-receipts-for-the-uk

If the live download is unavailable, this script falls back to
illustrative data based on published 2023-24 outturn figures, clearly
marked as such.
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

# HMRC Tax and NIC Receipts — monthly national statistics
# The XLSX file contains annual outturn by tax type.
HMRC_RECEIPTS_URL = (
    "https://assets.publishing.service.gov.uk/media/"
    "67eaee6093e0a7b9eb1e7ae2/"
    "HMRC_Tax_and_NIC_Receipts_Monthly_and_Annual_Apr25.xlsx"
)

ACCESS_DATE = date.today().isoformat()

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 60


# ---------------------------------------------------------------------------
# Illustrative fallback data
# ---------------------------------------------------------------------------
# Based on HMRC published 2023-24 outturn figures.
# These are used ONLY when the live download fails, and the output CSV
# is clearly marked as illustrative.
_FALLBACK_DATA: list[dict[str, object]] = [
    # Multi-year data based on HMRC annual receipts publications
    {"year": "2018-19", "income_tax_bn": 191.0, "nics_bn": 137.0, "cgt_bn": 9.2, "iht_bn": 5.4, "sdlt_bn": 12.0},
    {"year": "2019-20", "income_tax_bn": 194.0, "nics_bn": 143.0, "cgt_bn": 9.9, "iht_bn": 5.3, "sdlt_bn": 11.6},
    {"year": "2020-21", "income_tax_bn": 194.0, "nics_bn": 141.0, "cgt_bn": 11.1, "iht_bn": 5.4, "sdlt_bn": 10.0},
    {"year": "2021-22", "income_tax_bn": 225.0, "nics_bn": 157.0, "cgt_bn": 14.3, "iht_bn": 6.1, "sdlt_bn": 14.1},
    {"year": "2022-23", "income_tax_bn": 249.0, "nics_bn": 172.0, "cgt_bn": 14.5, "iht_bn": 7.1, "sdlt_bn": 12.0},
    {"year": "2023-24", "income_tax_bn": 270.0, "nics_bn": 180.0, "cgt_bn": 15.0, "iht_bn": 7.5, "sdlt_bn": 12.0},
]


def fetch() -> Path | None:
    """Download HMRC Tax and NIC Receipts XLSX.

    Returns the path to the downloaded file, or None if the download fails
    (in which case the pipeline falls back to illustrative data).
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / "hmrc_tax_receipts.xlsx"

    logger.info("Downloading HMRC Tax and NIC Receipts...")
    try:
        resp = requests.get(HMRC_RECEIPTS_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        logger.info("Saved to %s (%d KB)", out_path, len(resp.content) // 1024)
        return out_path
    except (requests.RequestException, OSError) as exc:
        logger.warning(
            "Could not download HMRC receipts (%s). Using illustrative fallback data.",
            exc,
        )
        return None


def _try_parse_live(xlsx_path: Path) -> pd.DataFrame | None:
    """Attempt to parse annual receipts from the live HMRC XLSX.

    The HMRC workbook structure varies between releases. This function
    tries to locate the annual summary sheet and extract the key tax
    series. Returns None if parsing fails, triggering fallback.
    """
    try:
        xl = pd.ExcelFile(xlsx_path)
    except (ValueError, TypeError, KeyError, PermissionError, OSError) as exc:
        logger.warning("Could not open XLSX: %s", exc)
        return None

    # Look for the annual totals sheet
    annual_sheet = None
    for name in xl.sheet_names:
        lower = str(name).lower()
        if "annual" in lower or "a1" in lower:
            annual_sheet = name
            break

    if annual_sheet is None:
        logger.warning(
            "No annual summary sheet found. Available sheets: %s",
            xl.sheet_names,
        )
        return None

    logger.info("Reading sheet: '%s'", annual_sheet)
    try:
        df_raw = pd.read_excel(xlsx_path, sheet_name=annual_sheet, header=None)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        logger.warning("Could not read sheet '%s': %s", annual_sheet, exc)
        return None

    # The sheet typically has tax names in column 0 and years across the top.
    # We need to find rows for Income Tax, NICs, CGT, IHT, SDLT and extract
    # the most recent complete years.
    tax_keywords = {
        "income_tax_bn": ["income tax"],
        "nics_bn": ["national insurance", "nic"],
        "cgt_bn": ["capital gains"],
        "iht_bn": ["inheritance"],
        "sdlt_bn": ["stamp duty land"],
    }

    # Find the header row with years
    header_row = None
    year_cols: dict[str, int] = {}
    for i in range(min(20, len(df_raw))):
        for j in range(len(df_raw.columns)):
            cell = str(df_raw.iloc[i, j]).strip()
            # Year patterns like "2023-24" or "2023/24"
            if len(cell) >= 7 and cell[4] in "-/" and cell[:4].isdigit():
                if header_row is None:
                    header_row = i
                year_cols[cell.replace("/", "-")] = j

    if header_row is None or len(year_cols) < 3:
        logger.warning("Could not locate year headers in sheet.")
        return None

    # Find rows for each tax type
    tax_rows: dict[str, int] = {}
    for i in range(header_row + 1, len(df_raw)):
        cell = str(df_raw.iloc[i, 0]).strip().lower()
        for key, keywords in tax_keywords.items():
            if key not in tax_rows:
                for kw in keywords:
                    if kw in cell:
                        tax_rows[key] = i
                        break

    if len(tax_rows) < 3:
        logger.warning(
            "Could not find enough tax rows. Found: %s", list(tax_rows.keys())
        )
        return None

    # Extract data
    records = []
    for year_label, col_idx in sorted(year_cols.items()):
        row_data: dict[str, object] = {"year": year_label}
        all_valid = True
        for tax_key, row_idx in tax_rows.items():
            val = df_raw.iloc[row_idx, col_idx]
            try:
                # Values are typically in £millions in the HMRC sheet. Coerce via
                # str() first so comma-grouped text ("1,234") parses, and so the
                # dynamically-typed pandas cell satisfies float()'s signature; the
                # except below still skips any genuinely non-numeric cell.
                val_float = float(str(val).replace(",", "").strip())
                # Convert from £m to £bn
                row_data[tax_key] = round(val_float / 1000, 1)
            except (ValueError, TypeError):
                all_valid = False
                break
        if all_valid:
            records.append(row_data)

    if len(records) < 3:
        logger.warning("Only extracted %d year(s) of data — using fallback.", len(records))
        return None

    df = pd.DataFrame(records)
    logger.info("Parsed %d years from live HMRC data.", len(df))
    return df


def _build_from_fallback() -> pd.DataFrame:
    """Build DataFrame from illustrative fallback data."""
    logger.info("Using illustrative fallback data (based on HMRC published figures).")
    return pd.DataFrame(_FALLBACK_DATA)


def process(xlsx_path: Path | None) -> pd.DataFrame:
    """Parse or generate tax composition data, compute work vs wealth totals."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Try live data first, fall back to illustrative
    df: pd.DataFrame | None = None
    data_source = "live"

    if xlsx_path is not None:
        df = _try_parse_live(xlsx_path)

    if df is None:
        df = _build_from_fallback()
        data_source = "illustrative"

    # Compute derived columns
    df["work_taxes_bn"] = df["income_tax_bn"] + df["nics_bn"]
    df["wealth_taxes_bn"] = df["cgt_bn"] + df["iht_bn"] + df["sdlt_bn"]
    df["total_selected_bn"] = df["work_taxes_bn"] + df["wealth_taxes_bn"]
    safe_total = df["total_selected_bn"].replace(0, pd.NA)
    df["work_pct"] = (df["work_taxes_bn"] / safe_total * 100).round(1)
    df["wealth_pct"] = (df["wealth_taxes_bn"] / safe_total * 100).round(1)
    df["data_source"] = data_source

    out_path = PROCESSED_DIR / "tax_composition.csv"
    df.to_csv(out_path, index=False)
    logger.info(
        "Processed: %d years, latest work taxes %.1f%%, wealth taxes %.1f%%",
        len(df),
        df["work_pct"].iloc[-1],
        df["wealth_pct"].iloc[-1],
    )

    return df


def build_chart(df: pd.DataFrame) -> None:
    """Generate stacked bar chart of work vs wealth tax proportions."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    latest = df.iloc[-1]
    data_source = str(latest.get("data_source", "unknown"))
    source_label = (
        f"Source: HMRC Tax and NIC Receipts · OGL v3.0 · Accessed {ACCESS_DATE}"
    )
    if data_source == "illustrative":
        source_label += "<br>Note: Based on published HMRC outturn figures (illustrative)"

    fig = go.Figure()

    # Stacked bar: work taxes
    fig.add_trace(go.Bar(
        x=df["year"],
        y=df["work_taxes_bn"],
        name="Work taxes (Income Tax + NICs)",
        marker_color="#1f77b4",
        text=[f"£{v:.0f}bn" for v in df["work_taxes_bn"]],
        textposition="inside",
        textfont=dict(size=11, color="white"),
        hovertemplate=(
            "%{x}<br>"
            "Work taxes: £%{y:.0f}bn (%{customdata[0]:.1f}%)<br>"
            "<extra></extra>"
        ),
        customdata=[[pct] for pct in df["work_pct"]],
    ))

    # Stacked bar: wealth taxes
    fig.add_trace(go.Bar(
        x=df["year"],
        y=df["wealth_taxes_bn"],
        name="Wealth taxes (CGT + IHT + SDLT)",
        marker_color="#d62728",
        text=[f"£{v:.0f}bn" for v in df["wealth_taxes_bn"]],
        textposition="inside",
        textfont=dict(size=11, color="white"),
        hovertemplate=(
            "%{x}<br>"
            "Wealth taxes: £%{y:.0f}bn (%{customdata[0]:.1f}%)<br>"
            "<extra></extra>"
        ),
        customdata=[[pct] for pct in df["wealth_pct"]],
    ))

    fig.update_layout(
        title=dict(
            text=(
                "UK Tax Revenue: Work vs Wealth<br>"
                "<sub>Income Tax + NICs vs Capital Gains Tax + Inheritance Tax + Stamp Duty</sub>"
            ),
            font=dict(size=18),
        ),
        xaxis=dict(
            title="Tax year",
            tickfont=dict(size=12),
            gridcolor="#e0e0e0",
        ),
        yaxis=dict(
            title="Revenue (£ billions)",
            tickfont=dict(size=14),
            gridcolor="#e0e0e0",
        ),
        barmode="stack",
        legend=dict(
            font=dict(size=12),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", color="#1a1a1a"),
        margin=dict(b=160),
        annotations=[
            dict(
                text=(
                    f"{source_label}<br>"
                    f"Britain taxes work approximately "
                    f"{latest['work_pct'] / latest['wealth_pct']:.0f}x harder than "
                    f"wealth: {latest['work_pct']:.0f}% of these revenues come from "
                    f"Income Tax and NICs, just {latest['wealth_pct']:.0f}% from CGT, "
                    f"IHT, and Stamp Duty combined."
                ),
                xref="paper", yref="paper",
                x=0, y=-0.32,
                showarrow=False,
                font=dict(size=11, color="#666666"),
            )
        ],
    )

    out_path = CHART_DIR / "tax_composition.html"
    write_accessible_chart(
        fig,
        out_path,
        title="UK Tax Revenue Composition: Work vs Wealth",
        description=(
            "Stacked bar chart comparing UK tax revenue from work "
            "(Income Tax and NICs) versus wealth (Capital Gains Tax, "
            "Inheritance Tax, and Stamp Duty Land Tax). Shows that "
            "approximately 93% of these revenues come from taxing work."
        ),
    )


def main() -> None:
    """Fetch HMRC tax receipts data and generate composition chart."""
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
