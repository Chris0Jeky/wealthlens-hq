"""Fetch Bank of England Bank Rate and CPI inflation data.

Source: Bank of England Interactive Analytical Database (OGL v3.0)
Series codes:
  - IUDBEDR: Official Bank Rate (monthly, not seasonally adjusted)
  - D7BT: CPI annual rate (12-month % change, ONS series via BoE IADB)

URL pattern:
  https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp
  ?csv.x=yes&SeriesCodes=IUDBEDR,D7BT&...

Output: projects/wealthlens-dashboard/data/processed/boe_rates.csv
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

# BoE IADB CSV download endpoint
BOE_IADB_URL = (
    "https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp"
)

# Series codes
BANK_RATE_SERIES = "IUDBEDR"
CPI_SERIES = "D7BT"

ACCESS_DATE = date.today().isoformat()

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 60


def _build_iadb_params(series_codes: str) -> dict[str, str]:
    """Build query parameters for the BoE IADB CSV download.

    The IADB requires a date range and output format. We fetch monthly
    data from 2000 onwards to capture the full modern monetary policy era.
    """
    return {
        "csv.x": "yes",
        "SeriesCodes": series_codes,
        "CSVF": "TN",  # Tab-separated with field names
        "Datefrom": "01/Jan/2000",
        "Dateto": "01/Dec/2099",  # Far future to always get latest
        "VPD": "Y",  # Values per date
    }


def fetch() -> Path:
    """Download Bank Rate and CPI data from BoE IADB.

    Falls back to illustrative data if the API is unreachable.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / "boe_iadb_rates.csv"

    series = f"{BANK_RATE_SERIES},{CPI_SERIES}"
    params = _build_iadb_params(series)

    try:
        logger.info("Fetching BoE IADB data for %s...", series)
        resp = requests.get(
            BOE_IADB_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        logger.info("Saved raw BoE data to %s (%d KB)", out_path, len(resp.content) // 1024)
        return out_path
    except (requests.RequestException, OSError) as exc:
        logger.warning("BoE IADB fetch failed (%s), using fallback data", exc)
        return _write_fallback(out_path)


def _write_fallback(out_path: Path) -> Path:
    """Write illustrative fallback data when the live API is unreachable.

    IMPORTANT: This data is clearly marked as illustrative. Values are
    approximate historical Bank Rate and CPI figures for demonstration.
    Do not present fallback data as authoritative.
    """
    # Approximate historical Bank Rate and CPI annual rate
    # Sources for reference values (not used directly):
    # - Bank Rate: widely reported in BoE press releases
    # - CPI: ONS headline inflation series
    fallback_rows = [
        # date, bank_rate, cpi_annual
        ("2000-01-01", 5.50, 0.8),
        ("2001-01-01", 6.00, 0.9),
        ("2002-01-01", 4.00, 1.6),
        ("2003-01-01", 4.00, 1.4),
        ("2004-01-01", 3.75, 1.3),
        ("2005-01-01", 4.75, 1.9),
        ("2006-01-01", 4.50, 2.1),
        ("2007-01-01", 5.25, 2.3),
        ("2008-01-01", 5.50, 3.6),
        ("2009-01-01", 1.50, 2.2),
        ("2010-01-01", 0.50, 3.3),
        ("2011-01-01", 0.50, 4.5),
        ("2012-01-01", 0.50, 2.8),
        ("2013-01-01", 0.50, 2.6),
        ("2014-01-01", 0.50, 1.5),
        ("2015-01-01", 0.50, 0.0),
        ("2016-01-01", 0.50, 0.7),
        ("2017-01-01", 0.25, 2.7),
        ("2018-01-01", 0.50, 2.5),
        ("2019-01-01", 0.75, 1.8),
        ("2020-01-01", 0.75, 1.3),
        ("2020-04-01", 0.10, 0.8),
        ("2021-01-01", 0.10, 0.7),
        ("2021-07-01", 0.10, 2.5),
        ("2022-01-01", 0.25, 5.5),
        ("2022-07-01", 1.25, 10.1),
        ("2022-10-01", 2.25, 11.1),
        ("2023-01-01", 3.50, 10.1),
        ("2023-07-01", 5.25, 6.8),
        ("2024-01-01", 5.25, 4.0),
        ("2024-07-01", 5.00, 2.2),
        ("2024-12-01", 4.75, 2.5),
        ("2025-01-01", 4.50, 3.0),
    ]
    df = pd.DataFrame(fallback_rows, columns=["date", "bank_rate", "cpi_annual"])

    # Write as CSV (same format the process step expects after parsing)
    out_path.write_text(
        "DATE,IUDBEDR,D7BT\n"
        + "\n".join(
            f"{r[0]},{r[1]},{r[2]}" for r in fallback_rows
        )
        + "\n",
        encoding="utf-8",
    )
    logger.info("Wrote fallback data to %s (%d rows)", out_path, len(fallback_rows))
    return out_path


def process(raw_path: Path) -> pd.DataFrame:
    """Parse raw BoE IADB CSV into a clean DataFrame.

    The IADB CSV format has a header row with "DATE", then series code
    columns. Dates may be in DD/MMM/YYYY or YYYY-MM-DD format depending
    on the download mode.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Try reading with common delimiters (IADB uses comma or tab)
    raw_text = raw_path.read_text(encoding="utf-8", errors="replace")

    # Detect delimiter
    first_line = raw_text.split("\n")[0]
    delimiter = "\t" if "\t" in first_line else ","

    df_raw = pd.read_csv(raw_path, delimiter=delimiter, skipinitialspace=True)

    # Normalise column names to uppercase for matching
    df_raw.columns = [c.strip().upper() for c in df_raw.columns]

    # Find the date column
    date_col = None
    for candidate in ("DATE", "DATES"):
        if candidate in df_raw.columns:
            date_col = candidate
            break

    if date_col is None:
        logger.error("No DATE column found in BoE data. Columns: %s", list(df_raw.columns))
        raise ValueError(f"No DATE column in BoE raw data: {list(df_raw.columns)}")

    # Parse dates — BoE uses DD/Mon/YYYY (e.g. 02 Jan 2000) or ISO format
    df_raw[date_col] = pd.to_datetime(df_raw[date_col], dayfirst=True, format="mixed")

    # Extract Bank Rate and CPI columns
    bank_rate_col = None
    cpi_col = None
    for col in df_raw.columns:
        if BANK_RATE_SERIES in col:
            bank_rate_col = col
        if CPI_SERIES in col:
            cpi_col = col

    records = []
    for _, row in df_raw.iterrows():
        record: dict[str, object] = {"date": row[date_col].strftime("%Y-%m-%d")}

        if bank_rate_col and pd.notna(row.get(bank_rate_col)):
            try:
                record["bank_rate"] = float(row[bank_rate_col])
            except (ValueError, TypeError):
                record["bank_rate"] = None
        else:
            record["bank_rate"] = None

        if cpi_col and pd.notna(row.get(cpi_col)):
            try:
                record["cpi_annual"] = float(row[cpi_col])
            except (ValueError, TypeError):
                record["cpi_annual"] = None
        else:
            record["cpi_annual"] = None

        # Only keep rows that have at least one value
        if record.get("bank_rate") is not None or record.get("cpi_annual") is not None:
            records.append(record)

    df = pd.DataFrame(records)
    df = df.sort_values("date").reset_index(drop=True)

    # Forward-fill Bank Rate (it stays constant between changes)
    if "bank_rate" in df.columns:
        df["bank_rate"] = df["bank_rate"].ffill()

    out_path = PROCESSED_DIR / "boe_rates.csv"
    df.to_csv(out_path, index=False)
    logger.info("Processed BoE data saved to %s", out_path)
    logger.info(
        "%d rows, date range %s to %s",
        len(df),
        df["date"].iloc[0],
        df["date"].iloc[-1],
    )

    # Check if fallback data was used
    if len(df) < 50:
        logger.warning(
            "Only %d rows — this may be fallback/illustrative data. "
            "Re-run when BoE IADB is accessible for full dataset.",
            len(df),
        )

    return df


def build_chart(df: pd.DataFrame) -> None:
    """Generate interactive dual-axis chart: Bank Rate vs CPI inflation."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig = go.Figure()

    # Bank Rate trace (left y-axis)
    if "bank_rate" in df.columns:
        bank_df = df.dropna(subset=["bank_rate"])
        fig.add_trace(go.Scatter(
            x=bank_df["date"],
            y=bank_df["bank_rate"],
            mode="lines",
            name="Bank Rate",
            line=dict(color="#1f77b4", width=2.5),
            hovertemplate="Bank Rate: %{y:.2f}%<br>%{x}<extra></extra>",
            yaxis="y",
        ))

    # CPI inflation trace (right y-axis)
    if "cpi_annual" in df.columns:
        cpi_df = df.dropna(subset=["cpi_annual"])
        fig.add_trace(go.Scatter(
            x=cpi_df["date"],
            y=cpi_df["cpi_annual"],
            mode="lines",
            name="CPI Inflation (annual %)",
            line=dict(color="#d62728", width=2.5),
            hovertemplate="CPI: %{y:.1f}%<br>%{x}<extra></extra>",
            yaxis="y2",
        ))

    # Add 2% inflation target reference line
    fig.add_hline(
        y=2.0,
        line_dash="dot",
        line_color="#888888",
        line_width=1,
        annotation_text="2% target",
        annotation_position="top right",
        annotation_font_color="#888888",
        yref="y2",
    )

    is_fallback = len(df) < 50
    fallback_note = " (ILLUSTRATIVE FALLBACK DATA)" if is_fallback else ""

    fig.update_layout(
        title=dict(
            text=f"Bank Rate and CPI Inflation — United Kingdom{fallback_note}",
            font=dict(size=18),
        ),
        xaxis=dict(
            title="Date",
            tickfont=dict(size=14),
            gridcolor="#e0e0e0",
        ),
        yaxis=dict(
            title="Bank Rate (%)",
            ticksuffix="%",
            tickfont=dict(size=14),
            gridcolor="#e0e0e0",
            side="left",
            rangemode="tozero",
        ),
        yaxis2=dict(
            title="CPI Annual Rate (%)",
            ticksuffix="%",
            tickfont=dict(size=14),
            overlaying="y",
            side="right",
            rangemode="tozero",
        ),
        legend=dict(font=dict(size=14), x=0.02, y=0.98),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="system-ui, -apple-system, sans-serif", color="#1a1a1a"),
        margin=dict(b=120),
        annotations=[
            dict(
                text=(
                    f"Source: Bank of England Interactive Analytical Database · "
                    f"OGL v3.0 · Accessed {ACCESS_DATE}<br>"
                    f"Bank Rate (IUDBEDR) and CPI annual rate (D7BT/ONS). "
                    f"2% dashed line = BoE inflation target."
                ),
                xref="paper", yref="paper",
                x=0, y=-0.18,
                showarrow=False,
                font=dict(size=11, color="#666666"),
            ),
        ],
    )

    out_path = CHART_DIR / "boe_rates.html"
    write_accessible_chart(
        fig,
        out_path,
        title="Bank Rate and CPI Inflation — United Kingdom",
        description=(
            "Dual-axis line chart showing the Bank of England Bank Rate and "
            "CPI annual inflation rate from 2000 to present, sourced from "
            "the Bank of England Interactive Analytical Database."
        ),
    )


def main() -> None:
    """Fetch BoE interest rate and CPI data, then generate chart."""
    raw_path = fetch()
    df = process(raw_path)
    build_chart(df)
    logger.info("Done. Open the chart HTML in a browser to view.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    main()
