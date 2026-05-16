"""Shared fixtures for WealthLens tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Allow direct imports from automation/analysis/ (e.g. extract_action_items)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation" / "analysis"))

# Allow direct imports from the backend package
sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
        / "projects"
        / "wealthlens-dashboard"
        / "backend"
    ),
)

# Allow direct imports from automation/data-pipelines/ (e.g. validate)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation" / "data-pipelines"))

DATA_DIR = (
    Path(__file__).resolve().parents[1]
    / "projects"
    / "wealthlens-dashboard"
    / "data"
    / "processed"
)

_SEED_CSVS: dict[str, str] = {
    "wid_wealth_shares_gb.csv": (
        "variable,country,year,value\n"
        + "".join(
            f"shweal_p99p100,GB,{y},0.21\n"
            f"shweal_p90p100,GB,{y},0.52\n"
            for y in range(1900, 2023)
        )
    ),
    "ons_housing_affordability_by_region.csv": (
        "region,year,ratio\n"
        + "".join(
            f"{r},{y},{ratio}\n"
            for r in ["London", "South East", "East", "South West", "West Midlands",
                       "East Midlands", "North West", "Yorkshire", "North East"]
            for y, ratio in [(1997, 4.0), (2005, 7.0), (2015, 8.0), (2022, 9.0)]
        )
    ),
    "ons_wealth_by_decile.csv": (
        "decile,total_wealth_bn\n"
        "1st (poorest),13.9\n"
        "2nd,78.4\n"
        "3rd,195.6\n"
        "4th,392.5\n"
        "5th,652.0\n"
        "6th,955.2\n"
        "7th,1323.0\n"
        "8th,1805.6\n"
        "9th,2628.5\n"
        "10th (richest),5523.2\n"
    ),
    "hmrc_cgt_concentration.csv": (
        "gain_band,band_lower,num_taxpayers_thousands,total_gains_millions,"
        "share_of_gains_pct,share_of_taxpayers_pct,"
        "cumul_gains_from_top_pct,cumul_taxpayers_from_top_pct\n"
        "0-50k,0,200,4000,7.0,60.0,100.0,100.0\n"
        "50k-100k,50000,60,4500,8.0,18.0,93.0,40.0\n"
        "100k-500k,100000,30,10000,18.0,9.0,85.0,22.0\n"
        "500k-1m,500000,10,12000,22.0,3.0,67.0,13.0\n"
        "1m+,1000000,5,25000,45.0,1.5,45.0,1.5\n"
    ),
    "productivity_pay_gap.csv": (
        "year,productivity_index,real_pay_index\n"
        "1997,100.0,100.0\n"
        "2005,115.0,108.0\n"
        "2022,125.0,106.0\n"
    ),
    "ons_gdhi_by_region.csv": (
        "region,year,gdhi_per_head\n"
        "London,2021,32000\n"
        "South East,2021,26000\n"
        "North East,2021,18000\n"
    ),
    "tax_composition.csv": (
        "year,income_tax_bn,nics_bn,cgt_bn,iht_bn,sdlt_bn,"
        "work_taxes_bn,wealth_taxes_bn,total_selected_bn,work_pct,wealth_pct,data_source\n"
        "2021-22,225,155,15,6,14,380,35,415,91.6,8.4,illustrative\n"
        "2022-23,250,170,14,7,12,420,33,453,92.7,7.3,illustrative\n"
        "2023-24,270,180,15,7.5,12,450,34.5,484.5,92.9,7.1,illustrative\n"
    ),
    "boe_rates.csv": (
        "date,bank_rate,cpi_annual_rate\n"
        + "".join(
            f"2023-{m:02d},{rate},{cpi}\n"
            for m, rate, cpi in [
                (1, 3.50, 10.1), (2, 4.00, 10.4), (3, 4.25, 10.1),
                (4, 4.25, 8.7), (5, 4.50, 8.7), (6, 5.00, 7.9),
                (7, 5.25, 6.8), (8, 5.25, 6.7), (9, 5.25, 6.7),
                (10, 5.25, 4.6), (11, 5.25, 3.9), (12, 5.25, 4.0),
            ]
        )
    ),
    "child_poverty_by_region.csv": (
        "region,child_poverty_pct,year\n"
        "London,32.0,2022\n"
        "North East,38.0,2022\n"
        "South East,22.0,2022\n"
    ),
    "generational_wealth_gap.csv": (
        "generation,median_wealth,year\n"
        "Baby Boomers,500000,2020\n"
        "Gen X,250000,2020\n"
        "Millennials,50000,2020\n"
    ),
}


def _seed_data_files() -> list[Path]:
    """Write minimal CSV fixtures for any dataset files that are missing."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for filename, content in _SEED_CSVS.items():
        path = DATA_DIR / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(path)
    return created


@pytest.fixture(autouse=True, scope="session")
def _seed_test_data():
    """Seed minimal CSV fixtures before tests, clean up after."""
    created = _seed_data_files()
    yield
    for path in created:
        path.unlink(missing_ok=True)


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Create a temporary directory structure matching the project layout."""
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "charts").mkdir(parents=True)
    return tmp_path
