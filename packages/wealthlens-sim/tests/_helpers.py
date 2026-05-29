"""Shared test fixtures and helpers for wealthlens-sim tests."""

from __future__ import annotations

from wealthlens_sim.schema.base import Nation
from wealthlens_sim.schema.household import Asset, AssetType, Household, Person


def make_person(
    person_id: str = "p1",
    assets: list[tuple[AssetType, float, float]] | None = None,
    annual_income: float = 0,
    capital_gains_realised: float = 0,
) -> Person:
    """Create a person with specified assets as (type, gross, debt)."""
    if assets is None:
        assets = []
    return Person(
        person_id=person_id,
        age=45,
        annual_income=annual_income,
        capital_gains_realised=capital_gains_realised,
        assets=[
            Asset(asset_type=t, gross_value=g, debt=d)
            for t, g, d in assets
        ],
    )


def make_household(
    persons: list[Person],
    nation: Nation = Nation.ENGLAND,
    weight: float = 1.0,
    household_id: str = "hh1",
) -> Household:
    return Household(
        household_id=household_id,
        nation=nation,
        weight=weight,
        persons=persons,
    )
