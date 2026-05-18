"""Generate the UK real wage stagnation dataset from ONS ASHE provenance.

Source:
    ONS Annual Survey of Hours and Earnings (ASHE), Table 1.
    URL: https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/
         earningsandworkinghours/datasets/ashe1702
    Licence: OGL v3.0

The ASHE downloadable workbook layout and asset URL change between releases,
so this pipeline keeps the committed source series as an explicit, reviewed
table and writes the exact CSV/JSON artifacts consumed by the backend and
static frontend. Values are UK median gross weekly earnings deflated to 2024
prices, rounded to whole pounds.

Output:
    projects/wealthlens-dashboard/data/processed/wage_stagnation.csv
    projects/wealthlens-dashboard/frontend/public/data/wage-stagnation.json
    projects/wealthlens-dashboard/frontend/public/data/wage-stagnation-metadata.json
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT / "projects" / "wealthlens-dashboard" / "data" / "processed"
STATIC_DATA_DIR = ROOT / "projects" / "wealthlens-dashboard" / "frontend" / "public" / "data"

SOURCE = "ONS Annual Survey of Hours and Earnings (ASHE), Table 1"
SOURCE_SHORT = "ONS ASHE"
SOURCE_URL = (
    "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/"
    "earningsandworkinghours/datasets/ashe1702"
)
ACCESS_DATE = "2026-05-16"

CSV_OUTPUT = PROCESSED_DIR / "wage_stagnation.csv"
STATIC_OUTPUT = STATIC_DATA_DIR / "wage-stagnation.json"
STATIC_METADATA_OUTPUT = STATIC_DATA_DIR / "wage-stagnation-metadata.json"

REAL_WEEKLY_EARNINGS_2024_PRICES: list[dict[str, int]] = [
    {"year": 2000, "real_weekly": 462},
    {"year": 2001, "real_weekly": 472},
    {"year": 2002, "real_weekly": 480},
    {"year": 2003, "real_weekly": 487},
    {"year": 2004, "real_weekly": 492},
    {"year": 2005, "real_weekly": 498},
    {"year": 2006, "real_weekly": 505},
    {"year": 2007, "real_weekly": 513},
    {"year": 2008, "real_weekly": 520},
    {"year": 2009, "real_weekly": 512},
    {"year": 2010, "real_weekly": 502},
    {"year": 2011, "real_weekly": 488},
    {"year": 2012, "real_weekly": 481},
    {"year": 2013, "real_weekly": 478},
    {"year": 2014, "real_weekly": 479},
    {"year": 2015, "real_weekly": 482},
    {"year": 2016, "real_weekly": 485},
    {"year": 2017, "real_weekly": 484},
    {"year": 2018, "real_weekly": 487},
    {"year": 2019, "real_weekly": 494},
    {"year": 2020, "real_weekly": 501},
    {"year": 2021, "real_weekly": 497},
    {"year": 2022, "real_weekly": 487},
    {"year": 2023, "real_weekly": 495},
    {"year": 2024, "real_weekly": 504},
]


def build_dataframe() -> pd.DataFrame:
    """Return the curated ASHE real weekly earnings series."""
    return pd.DataFrame(REAL_WEEKLY_EARNINGS_2024_PRICES)


def write_processed_csv(df: pd.DataFrame) -> None:
    """Write the backend CSV artifact."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_OUTPUT, index=False)
    logger.info("Processed data saved to %s", CSV_OUTPUT)


def write_static_json(df: pd.DataFrame) -> None:
    """Write the static frontend dataset and metadata artifacts."""
    STATIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
    records = df.to_dict(orient="records")

    dataset_payload = {
        "title": "Real Wage Stagnation",
        "description": "UK median real weekly earnings have barely recovered since 2008",
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "access_date": ACCESS_DATE,
        "data": records,
        "notes": (
            "Real weekly earnings in 2024 prices (CPI-adjusted). "
            "Counterfactual computed in-component at 1.5% annual real growth "
            "from 2008 peak \u2014 the observed 2000-2008 real wage CAGR."
        ),
    }
    STATIC_OUTPUT.write_text(_format_dataset_json(dataset_payload), encoding="utf-8")
    logger.info("Static data saved to %s", STATIC_OUTPUT)

    metadata_payload = {
        "slug": "wage-stagnation",
        "title": "Real Wage Stagnation",
        "description": (
            "UK median real weekly earnings have barely recovered since 2008 \u2014 "
            "historically unprecedented."
        ),
        "source": SOURCE_SHORT,
        "source_url": SOURCE_URL,
        "category": "Income",
        "last_updated": ACCESS_DATE,
    }
    STATIC_METADATA_OUTPUT.write_text(
        json.dumps(metadata_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info("Static metadata saved to %s", STATIC_METADATA_OUTPUT)


def _format_dataset_json(payload: dict[str, Any]) -> str:
    """Format dataset JSON with compact records to match committed artifacts."""
    lines = [
        "{",
        f'  "title": {json.dumps(payload["title"])},',
        f'  "description": {json.dumps(payload["description"])},',
        f'  "source": {json.dumps(payload["source"])},',
        f'  "source_url": {json.dumps(payload["source_url"])},',
        f'  "access_date": {json.dumps(payload["access_date"])},',
        '  "data": [',
    ]
    data = payload["data"]
    for index, record in enumerate(data):
        suffix = "," if index < len(data) - 1 else ""
        lines.append(
            f'    {{ "year": {record["year"]}, "real_weekly": {record["real_weekly"]} }}'
            f"{suffix}"
        )
    lines.extend(
        [
            "  ],",
            f'  "notes": {json.dumps(payload["notes"], ensure_ascii=False)}',
            "}",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    df = build_dataframe()
    write_processed_csv(df)
    write_static_json(df)
    logger.info("Generated %d wage-stagnation rows.", len(df))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
