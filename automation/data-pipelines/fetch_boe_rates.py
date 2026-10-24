"""Fetch monthly Bank Rate (BoE IUMABEDR) and annual CPI inflation (ONS D7G7).

Join official observations by calendar month from 2000 onwards, labelling each
month YYYY-MM-01. IADB dates are month-end labels for monthly averages, not
end-month policy readings. Only months covered by both sources are published.
Download or parse failures abort; illustrative fallback is an explicit offline opt-in.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
from datetime import date
from io import StringIO
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
from _cells import to_finite_float
from chart_html import write_accessible_chart
from http_retry import fetch_with_retry

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
BANK_RATE_SERIES = "IUMABEDR"
CPI_SERIES = "D7G7"
ONS_CPI_URL = (
    "https://www.ons.gov.uk/generator?format=csv&uri="
    "/economy/inflationandpriceindices/timeseries/d7g7/mm23"
)

USER_AGENT = (
    "Mozilla/5.0 (compatible; WealthLensDataPipeline/1.0; "
    "+https://github.com/Chris0Jeky/wealthlens-hq)"
)

ACCESS_DATE = date.today().isoformat()

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 60


def _write_metadata(
    csv_path: Path, *, data_type: str, access_date: str | None = None,
    source_url: str = BOE_IADB_URL, sources: list[dict] | None = None,
) -> None:
    """Persist provenance beside raw and processed CSVs for all consumers."""
    metadata = json.loads(
        (Path(__file__).parent / "metadata/boe_rates.meta.json").read_text(encoding="utf-8")
    )
    metadata["sources"] = sources if sources is not None else [
        {**source, "access_date": access_date} for source in metadata["sources"]
    ]
    metadata.update(
        data_type=data_type,
        source_url=source_url,
        access_date=access_date,
        generated=ACCESS_DATE,
        provenance_note=(
            "Downloaded from the official source."
            if data_type == "live_ons" else
            "Illustrative worked examples, not published statistics."
            if data_type == "illustrative_fallback" else
            "Unverified provenance; these figures have not been verified as official statistics."
        ),
    )
    csv_path.with_suffix(".meta.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )


def _build_iadb_params(series_codes: str) -> dict[str, str]:
    """Build query parameters for the BoE IADB CSV download.

    The IADB requires a date range and output format. We fetch monthly
    data from 2000 onwards to capture the full modern monetary policy era.
    """
    return {
        "csv.x": "yes",
        "SeriesCodes": series_codes,
        "CSVF": "TN",  # CSV with field names
        "UsingCodes": "Y",
        "VFD": "N",
        "Datefrom": "01/Jan/2000",
        "Dateto": "01/Dec/2099",  # Far future to always get latest
        "VPD": "Y",  # Values per date
    }


def _download_iadb(
    series_codes: str, *, params: dict[str, str] | None = None,
) -> requests.Response:
    """Request official CSV bytes, also usable to capture an unedited test fixture."""
    return _download_csv(
        BOE_IADB_URL,
        params=params if params is not None else _build_iadb_params(series_codes),
    )


def _download_csv(url: str, *, params: dict[str, str] | None = None) -> requests.Response:
    """Use the same User-Agent, timeout and transient retry policy for both sources."""
    response = fetch_with_retry(
        url, params=params, timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response


def _download_ons() -> requests.Response:
    """Download the official MM23 D7G7 CSV, including its metadata header."""
    return _download_csv(ONS_CPI_URL)


def _parse_ons_csv(raw_text: str) -> pd.DataFrame:
    """Read only YYYY MON observations; skip metadata, annual and quarterly rows."""
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    rows = list(csv.reader(StringIO(raw_text.lstrip("\ufeff"))))
    headers = {row[0]: row[1] for row in rows if len(row) == 2}
    if headers.get("CDID") != CPI_SERIES or headers.get("Source dataset ID") != "MM23":
        raise ValueError("ONS response is not D7G7 from MM23")
    records = []
    for row in rows:
        if not row or not re.fullmatch(r"\d{4} [A-Z]{3}", row[0].strip()):
            continue
        year, month = row[0].strip().split()
        if month not in months or len(row) != 2:
            raise ValueError("Invalid ONS monthly observation")
        value = to_finite_float(row[1])
        if value is None:
            raise ValueError("ONS monthly CPI must be finite")
        records.append({"DATE": f"{year}-{months.index(month) + 1:02d}-01", CPI_SERIES: value})
    if not records:
        raise ValueError("ONS response has no monthly observations")
    frame = pd.DataFrame(records)
    if frame["DATE"].duplicated().any():
        raise ValueError("Duplicate ONS month")
    return frame.sort_values("DATE").reset_index(drop=True)


def _join_monthly(bank: pd.DataFrame, cpi: pd.DataFrame) -> pd.DataFrame:
    """Inner join calendar months, without filling or interpolating either series."""
    bank = bank.rename(columns={"DATES": "DATE"})[["DATE", BANK_RATE_SERIES]].copy()
    bank["DATE"] = pd.to_datetime(bank["DATE"], format="mixed").dt.to_period("M").dt.to_timestamp()
    bank["DATE"] = bank["DATE"].dt.strftime("%Y-%m-%d")
    if bank["DATE"].duplicated().any():
        raise ValueError("Duplicate IADB month")
    joined = bank.merge(cpi, on="DATE", how="inner", validate="one_to_one")
    joined = joined.loc[joined["DATE"] >= "2000-01-01"].sort_values("DATE").reset_index(drop=True)
    if joined.empty:
        raise ValueError("Official sources have no common months from 2000 onwards")
    for column in (BANK_RATE_SERIES, CPI_SERIES):
        if any(to_finite_float(value) is None for value in joined[column]):
            raise ValueError("Official monthly observations must be finite")
    expected = pd.period_range(joined["DATE"].iloc[0], joined["DATE"].iloc[-1], freq="M")
    if len(joined) != len(expected):
        raise ValueError("Official sources have missing months within their common range")
    return joined


def _parse_iadb_csv(
    raw_text: str, *, required_series: tuple[str, ...] = (),
) -> pd.DataFrame:
    """Parse IADB comma/tab exports; HTTP success alone does not prove CSV data."""
    raw_text = raw_text.lstrip("\ufeff\r\n")
    first_line = raw_text.splitlines()[0] if raw_text else ""
    delimiter = "\t" if "\t" in first_line else ","
    header = [value.strip().strip('"').upper() for value in first_line.split(delimiter)]
    if not {"DATE", "DATES"}.intersection(header):
        raise ValueError("IADB response is not a dated CSV export (possibly an HTML error page)")
    frame = pd.read_csv(StringIO(raw_text), delimiter=delimiter, skipinitialspace=True)
    frame.columns = pd.Index([str(column).strip().upper() for column in frame.columns])
    missing = set(required_series).difference(frame.columns)
    if missing:
        raise ValueError(f"IADB response lacks required series: {', '.join(sorted(missing))}")
    if frame.empty:
        raise ValueError("IADB response has no observations")
    return frame


def fetch(*, allow_fallback: bool = False) -> Path:
    """Download Bank Rate from BoE IADB and CPI annual inflation from ONS.

    Abort before writing if either source cannot be downloaded or parsed.
    Set allow_fallback=True only for illustrative offline development data.
    """
    out_path = RAW_DIR / "boe_iadb_rates.csv"

    try:
        logger.info("Fetching BoE %s and ONS %s...", BANK_RATE_SERIES, CPI_SERIES)
        bank_response = _download_iadb(BANK_RATE_SERIES)
        bank = _parse_iadb_csv(
            bank_response.content.decode("utf-8-sig"), required_series=(BANK_RATE_SERIES,),
        )
        cpi_response = _download_ons()
        cpi = _parse_ons_csv(cpi_response.content.decode("utf-8-sig"))
        joined = _join_monthly(bank, cpi)
        template = json.loads(
            (Path(__file__).parent / "metadata/boe_rates.meta.json").read_text(encoding="utf-8")
        )
        sources = [
            {**source, "url": response.url, "access_date": ACCESS_DATE}
            for source, response in zip(template["sources"], (bank_response, cpi_response), strict=True)
        ]
    except (requests.RequestException, OSError, ValueError) as exc:
        if not allow_fallback:
            message = "BoE IUMABEDR / ONS D7G7 fetch failed; preserving last-good outputs"
            logger.error("%s: %s", message, exc)
            raise RuntimeError(message) from exc
        logger.warning("Official Bank Rate/CPI fetch failed (%s), using fallback data", exc)
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        return _write_fallback(out_path)

    # Keep both unedited responses for audit; publish only the validated join.
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "boe_iumabedr.csv").write_bytes(bank_response.content)
    (RAW_DIR / "ons_d7g7.csv").write_bytes(cpi_response.content)
    joined.to_csv(out_path, index=False)
    _write_metadata(
        out_path, data_type="live_ons", access_date=ACCESS_DATE,
        source_url=bank_response.url, sources=sources,
    )
    logger.info("Saved joined official monthly data to %s (%d rows)", out_path, len(joined))
    return out_path


def _write_fallback(out_path: Path) -> Path:
    """Write explicitly requested illustrative offline development data.

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

    # Write as CSV (same format the process step expects after parsing)
    out_path.write_text(
        "DATE,IUDBEDR,D7BT,data_type\n"
        + "\n".join(
            f"{r[0]},{r[1]},{r[2]},illustrative_fallback" for r in fallback_rows
        )
        + "\n",
        encoding="utf-8",
    )
    _write_metadata(out_path, data_type="illustrative_fallback")
    logger.info("Wrote fallback data to %s (%d rows)", out_path, len(fallback_rows))
    return out_path


def process(raw_path: Path) -> pd.DataFrame:
    """Parse raw BoE IADB CSV into a clean DataFrame.

    The IADB CSV format has a header row with "DATE", then series code
    columns. Dates may be in DD/MMM/YYYY or YYYY-MM-DD format depending
    on the download mode.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
    df_raw = _parse_iadb_csv(raw_text)

    # Transport provenance, never row count, determines whether figures are official.
    # Unknown or conflicting evidence must not silently become official data.
    try:
        metadata = json.loads(raw_path.with_suffix(".meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        metadata = {}
    if not isinstance(metadata, dict):
        metadata = {}
    data_type = metadata.get("data_type", "unverified")
    if data_type not in ("live_ons", "illustrative_fallback"):
        data_type = "unverified"
    if "DATA_TYPE" in df_raw.columns and not df_raw["DATA_TYPE"].eq(data_type).all():
        data_type = "unverified"
    access_date = metadata.get("access_date") if data_type == "live_ons" else None
    if data_type == "live_ons":
        # Official exports need BOTH exact series, never a partially official chart.
        _parse_iadb_csv(raw_text, required_series=(BANK_RATE_SERIES, CPI_SERIES))

    # Find the date column
    date_col = None
    for candidate in ("DATE", "DATES"):
        if candidate in df_raw.columns:
            date_col = candidate
            break

    if date_col is None:
        logger.error("No DATE column found in BoE data. Columns: %s", list(df_raw.columns))
        raise ValueError(f"No DATE column in BoE raw data: {list(df_raw.columns)}")

    # Parse dates: BoE live uses day/month-name/year; fallback uses ISO dates.
    # format="mixed" handles both; dayfirst omitted to avoid swapping
    # month/day on ISO dates.
    df_raw[date_col] = pd.to_datetime(df_raw[date_col], format="mixed")
    if data_type == "live_ons":
        # IADB labels monthly observations at month-end. The chart uses month-start
        # labels for that SAME calendar month, not an end-month policy-rate reading.
        df_raw[date_col] = df_raw[date_col].dt.to_period("M").dt.to_timestamp()

    # Extract Bank Rate and CPI columns
    bank_rate_col = None
    cpi_col = None
    for col in df_raw.columns:
        if col == BANK_RATE_SERIES or (data_type != "live_ons" and col == "IUDBEDR"):
            bank_rate_col = col
        if col == CPI_SERIES or (data_type != "live_ons" and col == "D7BT"):
            cpi_col = col

    if bank_rate_col is None and cpi_col is None:
        logger.error(
            "Neither Bank Rate (%s) nor CPI (%s) column found. Columns: %s",
            BANK_RATE_SERIES, CPI_SERIES, list(df_raw.columns),
        )
        raise ValueError(
            f"No Bank Rate or CPI columns in BoE data: {list(df_raw.columns)}"
        )

    skipped = 0
    records = []
    for _, row in df_raw.iterrows():
        record: dict[str, object] = {"date": row[date_col].strftime("%Y-%m-%d")}

        if bank_rate_col and pd.notna(row.get(bank_rate_col)):
            # to_finite_float returns None for a non-numeric or NaN/inf cell so a
            # bad value is counted as skipped rather than written into the CSV.
            bank_rate = to_finite_float(row[bank_rate_col])
            if bank_rate is None:
                skipped += 1
            record["bank_rate"] = bank_rate
        else:
            record["bank_rate"] = None

        if cpi_col and pd.notna(row.get(cpi_col)):
            cpi_annual = to_finite_float(row[cpi_col])
            if cpi_annual is None:
                skipped += 1
            record["cpi_annual"] = cpi_annual
        else:
            record["cpi_annual"] = None

        if data_type == "live_ons" and (
            record["bank_rate"] is None or record["cpi_annual"] is None
        ):
            raise ValueError("Official BoE data requires finite Bank Rate and CPI for every month")
        if record.get("bank_rate") is not None or record.get("cpi_annual") is not None:
            records.append(record)

    if skipped > 0:
        logger.warning("Skipped %d unparseable numeric values", skipped)

    if not records:
        raise ValueError("No valid data rows after parsing BoE CSV")

    df = pd.DataFrame(records)
    df = df.sort_values("date").reset_index(drop=True)

    # Legacy illustrative examples retain their existing fill behaviour. A monthly
    # official average must never be inferred from a previous month's observation.
    if data_type != "live_ons" and "bank_rate" in df.columns:
        df["bank_rate"] = df["bank_rate"].ffill()

    out_path = PROCESSED_DIR / "boe_rates.csv"
    df["data_type"] = data_type
    df.attrs["access_date"] = access_date
    df.to_csv(out_path, index=False)
    _write_metadata(
        out_path, data_type=data_type, access_date=access_date,
        source_url=metadata.get("source_url", BOE_IADB_URL), sources=metadata.get("sources"),
    )
    logger.info("Processed BoE data saved to %s", out_path)
    logger.info(
        "%d rows, date range %s to %s",
        len(df),
        df["date"].iloc[0],
        df["date"].iloc[-1],
    )

    if data_type != "live_ons":
        logger.warning(
            "BoE data provenance is %s. Re-run when BoE IADB is accessible for official data.",
            data_type,
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

    data_type = df["data_type"].iloc[0] if "data_type" in df.columns else "unverified"
    fallback_note = (
        " (ILLUSTRATIVE FALLBACK DATA)" if data_type == "illustrative_fallback"
        else " (UNVERIFIED PROVENANCE)" if data_type != "live_ons"
        else ""
    )

    fig.update_layout(
        title=dict(
            text=f"Bank Rate and CPI Inflation - United Kingdom{fallback_note}",
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
    )

    fig.add_annotation(
        text=(
            ("Illustrative worked examples, not published statistics.<br>"
             if data_type == "illustrative_fallback" else
             "Unverified provenance, not verified as official statistics.<br>"
             if data_type != "live_ons" else
             f"Accessed {df.attrs.get('access_date') or 'unknown'}<br>")
            + f'Reference: <a href="{BOE_IADB_URL}">Bank of England Interactive Analytical Database</a><br>'
            + 'Bank Rate: Bank of England terms.<br>'
            + f'CPI: <a href="{ONS_CPI_URL}">ONS D7G7 (MM23)</a>, OGL v3.0.<br>'
            + (f"Bank Rate ({BANK_RATE_SERIES}, monthly average) and CPI annual rate ({CPI_SERIES}). "
             if data_type == "live_ons" else
             "Illustrative Bank Rate and CPI annual rate; reference links do not verify these values. ")
            + "2% dashed line = BoE inflation target."
        ),
        xref="paper", yref="paper",
        x=0, y=-0.18,
        showarrow=False,
        font=dict(size=11, color="#666666"),
    )

    out_path = CHART_DIR / "boe_rates.html"
    write_accessible_chart(
        fig,
        out_path,
        title=f"Bank Rate and CPI Inflation - United Kingdom{fallback_note}",
        description=(
            "Dual-axis line chart showing the Bank of England Bank Rate and "
            f"CPI annual inflation rate.{fallback_note}"
        ),
    )


def main() -> None:
    """Fetch BoE interest rate and CPI data, then generate chart."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-illustrative-fallback", action="store_true",
        help="Allow illustrative fallback data for offline development (default: off).",
    )
    args = parser.parse_args()
    raw_path = fetch(allow_fallback=args.allow_illustrative_fallback)
    df = process(raw_path)
    build_chart(df)
    logger.info("Done. Open the chart HTML in a browser to view.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    main()
