"""Data endpoints — serves processed CSV datasets as JSON."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "processed"

DATASETS: dict[str, str] = {
    "wealth-shares": "wid_wealth_shares_gb.csv",
    "housing-affordability": "ons_housing_affordability_by_region.csv",
    "wealth-by-decile": "ons_wealth_by_decile.csv",
    "cgt-concentration": "hmrc_cgt_concentration.csv",
}


@router.get("/")
def list_datasets() -> dict[str, list[str]]:
    """Return available dataset names."""
    return {"datasets": list(DATASETS.keys())}


@router.get("/{dataset_name}")
def get_dataset(dataset_name: str) -> dict[str, list[dict]]:
    """Return a processed dataset as a list of row objects."""
    if dataset_name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {dataset_name}")

    csv_path = DATA_DIR / DATASETS[dataset_name]
    if not csv_path.exists():
        raise HTTPException(status_code=503, detail=f"Dataset file not found — run the pipeline first")

    df = pd.read_csv(csv_path)
    return {"data": df.to_dict(orient="records")}
