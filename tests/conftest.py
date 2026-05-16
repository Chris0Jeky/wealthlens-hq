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
            f"shweal_p99p100,GB,{y},0.{20 + y - 2016}\n"
            f"shweal_p90p100,GB,{y},0.{50 + y - 2016}\n"
            for y in range(2016, 2023)
        )
    ),
    "ons_housing_affordability_by_region.csv": (
        "region,year,ratio\n"
        "London,2022,12.5\n"
        "South East,2022,9.8\n"
        "North East,2022,5.4\n"
    ),
    "ons_wealth_by_decile.csv": "".join(
        ["decile,total_wealth_bn\n"]
        + [f"{d},{d * 150}\n" for d in range(1, 11)]
    ),
    "hmrc_cgt_concentration.csv": (
        "gain_band,band_lower,num_taxpayers_thousands,total_gains_millions,"
        "share_of_gains_pct,share_of_taxpayers_pct,"
        "cumul_gains_from_top_pct,cumul_taxpayers_from_top_pct\n"
        "1m+,1000000,5,30000,55.0,1.5,55.0,1.5\n"
        "500k-1m,500000,10,8000,15.0,3.0,70.0,4.5\n"
        "100k-500k,100000,30,10000,18.0,9.0,88.0,13.5\n"
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
