"""Construct facility-level shelter capacity scenarios for Kumamoto City.

The five facilities without official area evidence are retained and assigned zero
*known-source* capacity. This is not an assertion that their actual capacity is zero.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data/exp/shelter-capacity-audit/shelter_capacity_source_audit.parquet"
LOCATION_INPUT = (
    ROOT
    / "data/raw/prior_projects/KE01/kumamoto_designated_shelters_geospatial_preprocessed.parquet"
)
OUTPUT = ROOT / "data/processed/kumamoto_shelter_capacity_scenarios_preprocessed.parquet"

GRADE_B = "B - gymnasium-specific area"
GRADE_C = "C - whole-facility gross floor area"
GRADE_D = "D - missing area"

SCENARIOS = {
    "Safe Spacious": {
        "gym_share": 0.80,
        "school_building_share": 0.00,
        "non_school_share": 0.30,
        "area_per_person": 4.0,
    },
    "Central": {
        "gym_share": 0.85,
        "school_building_share": 0.10,
        "non_school_share": 0.40,
        "area_per_person": 3.0,
    },
    "Emergency Compact": {
        "gym_share": 0.90,
        "school_building_share": 0.20,
        "non_school_share": 0.50,
        "area_per_person": 2.0,
    },
}


def effective_area(df: pd.DataFrame, parameters: dict[str, float]) -> pd.Series:
    """Return scenario-specific effective floor area in square metres."""
    area = pd.Series(0.0, index=df.index, dtype="float64")
    school = df["Area Evidence Grade"].eq(GRADE_B)
    non_school = df["Area Evidence Grade"].eq(GRADE_C)
    area.loc[school] = (
        parameters["gym_share"] * df.loc[school, "Gymnasium Area (m2)"].fillna(0)
        + parameters["school_building_share"]
        * df.loc[school, "School Building Gross Area (m2)"].fillna(0)
    )
    area.loc[non_school] = (
        parameters["non_school_share"]
        * df.loc[non_school, "Non-School Gross Area (m2)"].fillna(0)
    )
    return area


def main() -> None:
    source = pd.read_parquet(INPUT)
    locations = pd.read_parquet(LOCATION_INPUT)[
        ["Common ID", "Latitude", "Longitude", "geometry"]
    ].rename(
        columns={
            "Common ID": "Shelter ID",
            "Latitude": "Shelter Latitude",
            "Longitude": "Shelter Longitude",
            "geometry": "Shelter Geometry WKB",
        }
    )
    if len(source) != 182 or source["Shelter ID"].duplicated().any():
        raise ValueError("Expected 182 unique official designated shelters")
    expected_grades = {GRADE_B, GRADE_C, GRADE_D}
    observed_grades = set(source["Area Evidence Grade"].dropna())
    if observed_grades != expected_grades:
        raise ValueError(f"Unexpected evidence grades: {sorted(observed_grades)}")

    df = source[
        [
            "Shelter ID",
            "Shelter Name",
            "Ward",
            "Address",
            "Official 2026 Designated Shelter",
            "Area Evidence Grade",
            "Source Area (m2)",
            "Additional School Building Gross Area (m2)",
            "Area Basis",
            "Source Title",
            "Source Page",
            "Capacity Construction Status",
        ]
    ].copy()
    df["Gymnasium Area (m2)"] = df["Source Area (m2)"].where(
        df["Area Evidence Grade"].eq(GRADE_B)
    )
    df["School Building Gross Area (m2)"] = df[
        "Additional School Building Gross Area (m2)"
    ].where(df["Area Evidence Grade"].eq(GRADE_B))
    df["Non-School Gross Area (m2)"] = df["Source Area (m2)"].where(
        df["Area Evidence Grade"].eq(GRADE_C)
    )
    df["Capacity Area Missing"] = df["Area Evidence Grade"].eq(GRADE_D)
    df = df.merge(locations, on="Shelter ID", how="left", validate="one_to_one")
    if df[["Shelter Latitude", "Shelter Longitude", "Shelter Geometry WKB"]].isna().any().any():
        raise ValueError("Every official shelter must have a matched location")

    for scenario, parameters in SCENARIOS.items():
        area_column = f"{scenario} Effective Area (m2)"
        capacity_column = f"{scenario} Capacity (persons)"
        df[area_column] = effective_area(df, parameters)
        df[capacity_column] = np.floor(
            df[area_column] / parameters["area_per_person"]
        ).astype("int64")

    ordered = [
        "Shelter ID",
        "Shelter Name",
        "Ward",
        "Address",
        "Shelter Latitude",
        "Shelter Longitude",
        "Shelter Geometry WKB",
        "Official 2026 Designated Shelter",
        "Area Evidence Grade",
        "Capacity Area Missing",
        "Gymnasium Area (m2)",
        "School Building Gross Area (m2)",
        "Non-School Gross Area (m2)",
        "Safe Spacious Effective Area (m2)",
        "Safe Spacious Capacity (persons)",
        "Central Effective Area (m2)",
        "Central Capacity (persons)",
        "Emergency Compact Effective Area (m2)",
        "Emergency Compact Capacity (persons)",
        "Area Basis",
        "Source Title",
        "Source Page",
        "Capacity Construction Status",
    ]
    df = df[ordered].sort_values(["Ward", "Shelter Name"]).reset_index(drop=True)

    if not (
        (df["Safe Spacious Capacity (persons)"] <= df["Central Capacity (persons)"])
        & (df["Central Capacity (persons)"] <= df["Emergency Compact Capacity (persons)"])
    ).all():
        raise ValueError("Facility capacity scenarios are not monotonic")
    if int(df["Capacity Area Missing"].sum()) != 5:
        raise ValueError("Expected five facilities without area evidence")
    missing_capacity = df.loc[
        df["Capacity Area Missing"],
        [column for column in df.columns if column.endswith("Capacity (persons)")],
    ]
    if missing_capacity.to_numpy().sum() != 0:
        raise ValueError("Missing-area facilities must have zero known-source capacity")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT, index=False)
    totals = df[[c for c in df.columns if c.endswith("Capacity (persons)")]].sum()
    print(f"Wrote {len(df)} shelters to {OUTPUT.relative_to(ROOT)}")
    print(totals.to_string())


if __name__ == "__main__":
    main()
