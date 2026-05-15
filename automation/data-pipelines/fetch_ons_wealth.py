"""Fetch ONS Wealth and Assets Survey aggregate data.

Source: ONS Total Wealth in Great Britain (OGL v3.0)
Dataset: Aggregate total wealth by wealth decile and component.
Edition: July 2006 to June 2016 / April 2014 to March 2022.
Published: 24 January 2025.

Note: WAS lost accredited official statistics status in June 2025.
Response rate declined from 66% to 41%, and a December 2024 DB pension
methodology change reduced measured wealth by approximately £2.3tn.
These caveats are noted on the chart output.
"""

from __future__ import annotations

import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
from chart_html import write_accessible_chart

try:
    from openpyxl.utils.exceptions import InvalidFileException
except ImportError:  # pragma: no cover — openpyxl is always installed with pandas[excel]
    InvalidFileException = type('InvalidFileException', (OSError,), {})  # type: ignore[assignment,misc]

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "projects" / "wealthlens-dashboard" / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHART_DIR = ROOT / "projects" / "wealthlens-dashboard" / "charts"

# Primary URL: latest ONS Total Wealth XLSX (Jan 2025 edition, covers up to
# March 2022).  The previous URL (april2018tomarch2020revised/...) 404s as of
# 2026-05-15 because ONS reorganised the download paths when they published
# the combined multi-period edition.
XLSX_URL = (
    "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/"
    "personalandhouseholdfinances/incomeandwealth/datasets/"
    "totalwealthwealthingreatbritain/"
    "july2006tojune2016andapril2014tomarch2022/"
    "totalwealthtables.xlsx"
)

# Fallback URL: the April 2014 to March 2020 edition (still online as of
# 2026-05-15).  Used if the primary URL breaks in the future.
XLSX_FALLBACK_URL = (
    "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/"
    "personalandhouseholdfinances/incomeandwealth/datasets/"
    "totalwealthwealthingreatbritain/"
    "july2006tojune2016andapril2014tomarch2020/"
    "totalwealthtablesfinal1.xlsx"
)

ACCESS_DATE = date.today().isoformat()


def fetch() -> Path | None:
    """Download the ONS Total Wealth XLSX.

    Tries the primary URL first, then the fallback URL.  Returns the path to
    the downloaded file, or None if both URLs fail (in which case the pipeline
    will use hard-coded fallback data).
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / "ons_total_wealth_by_decile.xlsx"

    urls = [
        ("primary", XLSX_URL),
        ("fallback", XLSX_FALLBACK_URL),
    ]

    for label, url in urls:
        print(f"Downloading ONS Total Wealth data ({label} URL)...")
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"  {label.capitalize()} download failed: {exc}")
            continue

        try:
            out_path.write_bytes(resp.content)
        except (OSError, IOError) as exc:
            print(f"  Warning: could not write file ({type(exc).__name__}: {exc})")
            continue
        print(f"  Saved to {out_path} ({len(resp.content) // 1024} KB)")
        return out_path

    print(
        "  ERROR: Both primary and fallback ONS download URLs failed.\n"
        "  The ONS may have reorganised their download paths again.\n"
        "  Check the dataset page for updated links:\n"
        "    https://www.ons.gov.uk/peoplepopulationandcommunity/"
        "personalandhouseholdfinances/incomeandwealth/datasets/"
        "totalwealthwealthingreatbritain\n"
        "  Falling back to hard-coded data from the ONS bulletin."
    )
    return None


def process(xlsx_path: Path | None) -> pd.DataFrame:
    """Extract total net wealth by decile from the XLSX.

    The spreadsheet (Jan 2025 edition) uses "Table 2.2" for aggregate
    household total wealth by decile.  The layout is:

        Col 0: wealth-component label (merged across decile rows)
        Col 1: decile label ("Total Wealth Decile 1 (lowest)" ... "10 (highest)")
        Col 2..10: period columns (the last column is the most recent wave)

    Values are in **millions of pounds**.  We convert to billions for the
    processed CSV to stay consistent with the chart and fallback data.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if xlsx_path is None:
        print("  No XLSX available, using fallback data.")
        df = _build_fallback_data()
        out_path = PROCESSED_DIR / "ons_wealth_by_decile.csv"
        df.to_csv(out_path, index=False)
        print(f"  Processed data saved to {out_path}")
        print(f"  {len(df)} rows")
        return df

    # Guard against corrupt / truncated XLSX files (e.g. partial download,
    # server returning an HTML error page with a .xlsx extension).
    try:
        xl = pd.ExcelFile(xlsx_path, engine="openpyxl")
    except (zipfile.BadZipFile, InvalidFileException, ValueError, OSError) as exc:
        print(f"  Warning: cannot open XLSX ({type(exc).__name__}: {exc})")
        print("  Falling back to hard-coded data.")
        df = _build_fallback_data()
        out_path = PROCESSED_DIR / "ons_wealth_by_decile.csv"
        df.to_csv(out_path, index=False)
        print(f"  Processed data saved to {out_path}")
        print(f"  {len(df)} rows")
        return df

    print(f"  Available sheets: {xl.sheet_names}")

    # Prefer "Table 2.2" (aggregate total wealth by decile).  Fall back to
    # the old heuristic if the sheet name changed in a future edition.
    target_sheet = None
    for name in xl.sheet_names:
        if name.strip() == "Table 2.2":
            target_sheet = name
            break
    if target_sheet is None:
        for name in xl.sheet_names:
            lower = name.lower()
            if "decile" in lower or "total" in lower:
                target_sheet = name
                break
    if target_sheet is None:
        target_sheet = xl.sheet_names[0]

    print(f"  Reading sheet: '{target_sheet}'")
    try:
        df_raw = pd.read_excel(
            xlsx_path, sheet_name=target_sheet, header=None, engine="openpyxl",
        )
    except (zipfile.BadZipFile, InvalidFileException, ValueError, OSError) as exc:
        print(f"  Warning: cannot read sheet ({type(exc).__name__}: {exc})")
        print("  Falling back to hard-coded data.")
        df = _build_fallback_data()
        out_path = PROCESSED_DIR / "ons_wealth_by_decile.csv"
        df.to_csv(out_path, index=False)
        print(f"  Processed data saved to {out_path}")
        print(f"  {len(df)} rows")
        return df

    df = _parse_table_2_2(df_raw)
    if df is None:
        # Fall back to the older generic parser.
        header_row = _find_decile_header_row(df_raw)
        if header_row is not None:
            df = _parse_decile_data(df_raw, header_row)
        else:
            print("  Could not locate decile data.  Dumping first 20 rows:")
            for i in range(min(20, len(df_raw))):
                vals = [str(v)[:50] for v in df_raw.iloc[i].values if pd.notna(v)]
                print(f"    Row {i}: {vals}")
            print("  Falling back to hard-coded data.")
            df = _build_fallback_data()

    out_path = PROCESSED_DIR / "ons_wealth_by_decile.csv"
    df.to_csv(out_path, index=False)
    print(f"  Processed data saved to {out_path}")
    print(f"  {len(df)} rows")

    return df


def _parse_table_2_2(df_raw: pd.DataFrame) -> pd.DataFrame | None:
    """Parse the Jan-2025-edition Table 2.2 layout.

    Expected layout (rows 3-12 are the "Aggregate total wealth" block):
        Col 0: component label (only on the first row of each block)
        Col 1: decile label
        Col 2..N: period columns (last column = most recent wave)

    Values are in millions; we convert to billions (divide by 1000).
    Returns None if the expected structure is not found.
    """
    # Find the row that starts the "Aggregate total wealth" block.
    agg_row = None
    for i in range(min(20, len(df_raw))):
        cell = str(df_raw.iloc[i, 0]).lower()
        if "aggregate total wealth" in cell:
            agg_row = i
            break

    if agg_row is None:
        return None

    # The last data column holds the most recent survey wave.
    last_col = len(df_raw.columns) - 1

    records: list[dict[str, object]] = []
    for i in range(agg_row, min(agg_row + 12, len(df_raw))):
        label = str(df_raw.iloc[i, 1]).strip() if pd.notna(df_raw.iloc[i, 1]) else ""
        if "decile" not in label.lower():
            continue

        try:
            wealth_m = float(df_raw.iloc[i, last_col])
        except (ValueError, TypeError):
            continue

        # Convert the ONS decile label to a shorter, user-friendly form.
        short = _shorten_decile_label(label)
        records.append({
            "decile": short,
            "total_wealth_bn": round(wealth_m / 1000, 1),
        })

    if len(records) != 10:
        print(f"  Warning: expected 10 decile rows, found {len(records)}.")
        # Partial decile data is unreliable — reject so the caller can fall
        # back to the next parser or hard-coded data.
        return None

    return pd.DataFrame(records)


def _shorten_decile_label(label: str) -> str:
    """Turn 'Total Wealth Decile 1 (lowest)' into '1st (poorest)' etc."""
    import re

    m = re.search(r"Decile\s+(\d+)", label, re.IGNORECASE)
    if not m:
        return label

    n = int(m.group(1))
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n, "th")
    short = f"{n}{suffix}"

    if "lowest" in label.lower():
        short += " (poorest)"
    elif "highest" in label.lower():
        short += " (richest)"

    return short


def _find_decile_header_row(df_raw: pd.DataFrame) -> int | None:
    """Scan the first 20 rows for a row containing decile labels."""
    for i in range(min(20, len(df_raw))):
        row_vals = [str(v).lower() for v in df_raw.iloc[i].values if pd.notna(v)]
        row_str = " ".join(row_vals)
        if "decile" in row_str or ("1st" in row_str and "10th" in row_str):
            return i
    return None


def _parse_decile_data(df_raw: pd.DataFrame, header_row: int) -> pd.DataFrame:
    """Parse decile wealth data from the raw XLSX starting at header_row.

    This is the legacy parser for older XLSX layouts where data runs down
    columns 0 (label) and 1 (value).
    """
    records: list[dict[str, object]] = []
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
    """ONS WAS April 2020 to March 2022 — total net wealth by decile (£bn).

    Source: ONS Total Wealth in Great Britain, Table 2.2.
    Edition: July 2006 to June 2016 / April 2014 to March 2022.
    URL: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/datasets/totalwealthwealthingreatbritain
    Accessed: 2026-05-15

    Values are the April 2020-March 2022 column from Table 2.2, converted
    from £ millions to £ billions.
    """
    return pd.DataFrame({
        "decile": [
            "1st (poorest)", "2nd", "3rd", "4th", "5th",
            "6th", "7th", "8th", "9th", "10th (richest)",
        ],
        "total_wealth_bn": [
            13.9, 78.4, 195.6, 392.5, 652.0,
            955.2, 1323.0, 1805.6, 2628.5, 5523.2,
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
                    f"Source: ONS Wealth and Assets Survey, April 2020 to March 2022 · "
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
