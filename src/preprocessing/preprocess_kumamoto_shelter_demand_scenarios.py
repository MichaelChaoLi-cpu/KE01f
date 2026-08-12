"""Restrict upstream earthquake-related shelter-demand estimates to Kumamoto City."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import shapely
from shapely import from_wkb


ROOT = Path(__file__).resolve().parents[2]
DEMAND_INPUT = (
    ROOT
    / "data/raw/prior_projects/KE01/kumamoto_grid_exposure_estimates_preprocessed.parquet"
)
BOUNDARY_INPUT = (
    ROOT
    / "data/raw/prior_projects/KE01b/kumamoto_administrative_areas_preprocessed.parquet"
)
OUTPUT = ROOT / "data/processed/kumamoto_shelter_demand_scenarios_preprocessed.parquet"


def assign_kumamoto_ward(demand: pd.DataFrame, boundaries: pd.DataFrame) -> pd.DataFrame:
    """Assign each disclosure-group geometry by an interior representative point."""
    wards = boundaries.loc[boundaries["Municipality Name"].eq("熊本市")].copy()
    if set(wards["Municipality Code"]) != {"43101", "43102", "43103", "43104", "43105"}:
        raise ValueError("Expected the five Kumamoto City ward boundaries")

    demand_geometries = from_wkb(demand["geometry"].to_numpy())
    representative_points = shapely.point_on_surface(demand_geometries)
    ward_name = pd.Series(pd.NA, index=demand.index, dtype="string")
    ward_code = pd.Series(pd.NA, index=demand.index, dtype="string")

    for _, ward in wards.iterrows():
        ward_geometry = from_wkb(ward["Geometry"])
        match = shapely.covers(ward_geometry, representative_points)
        ward_name.loc[match] = ward["Ward Name"]
        ward_code.loc[match] = ward["Municipality Code"]

    selected = demand.loc[ward_name.notna()].copy()
    selected["Ward"] = ward_name.loc[selected.index].to_numpy()
    selected["Ward Code"] = ward_code.loc[selected.index].to_numpy()
    return selected


def main() -> None:
    source = pd.read_parquet(DEMAND_INPUT)
    boundaries = pd.read_parquet(BOUNDARY_INPUT)
    selected = assign_kumamoto_ward(source, boundaries)

    rename = {
        "Disclosure Group Code": "Residential Demand Unit ID",
        "geometry": "Geometry WKB",
        "Disclosure Group Size": "Constituent 125 m Mesh Count",
        "Total Population": "Residential Population",
        "Population Age 65+": "Residential Population Age 65+",
        "Estimated Affected Population Lower Bound": "Housing-Loss Shelter Demand Low",
        "Estimated Affected Population": "Housing-Loss Shelter Demand Central",
        "Estimated Affected Population Upper Bound": "Housing-Loss Shelter Demand High",
        "Estimated Affected Population Age 65+ Lower Bound": "Housing-Loss Shelter Demand Age 65+ Low",
        "Estimated Affected Population Age 65+": "Housing-Loss Shelter Demand Age 65+ Central",
        "Estimated Affected Population Age 65+ Upper Bound": "Housing-Loss Shelter Demand Age 65+ High",
        "Nearest Designated Shelter ID": "Upstream Nearest Shelter ID",
        "Nearest Designated Shelter Distance m": "Upstream Nearest Shelter Distance (m)",
        "Damage Evidence Cutoff": "Damage Evidence Cutoff",
        "Estimation Status": "Demand Estimation Status",
    }
    selected = selected.rename(columns=rename)
    columns = [
        "Residential Demand Unit ID",
        "Geometry WKB",
        "Constituent 125 m Mesh Count",
        "Ward Code",
        "Ward",
        "Residential Population",
        "Residential Population Age 65+",
        "Housing-Loss Shelter Demand Low",
        "Housing-Loss Shelter Demand Central",
        "Housing-Loss Shelter Demand High",
        "Housing-Loss Shelter Demand Age 65+ Low",
        "Housing-Loss Shelter Demand Age 65+ Central",
        "Housing-Loss Shelter Demand Age 65+ High",
        "Upstream Nearest Shelter ID",
        "Upstream Nearest Shelter Distance (m)",
        "Damage Evidence Cutoff",
        "Demand Estimation Status",
    ]
    selected = selected[columns].sort_values("Residential Demand Unit ID").reset_index(drop=True)

    if len(selected) != 8_714:
        raise ValueError(f"Expected 8,714 Kumamoto City demand units, found {len(selected):,}")
    if selected["Residential Demand Unit ID"].duplicated().any():
        raise ValueError("Residential demand unit IDs must be unique")
    total_population = int(selected["Residential Population"].sum())
    if not 700_000 <= total_population <= 800_000:
        raise ValueError(f"Unexpected Kumamoto City population total: {total_population:,}")
    if not (
        (selected["Housing-Loss Shelter Demand Low"] <= selected["Housing-Loss Shelter Demand Central"])
        & (selected["Housing-Loss Shelter Demand Central"] <= selected["Housing-Loss Shelter Demand High"])
    ).all():
        raise ValueError("Demand scenarios are not monotonic")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    selected.to_parquet(OUTPUT, index=False)
    totals = selected[
        [
            "Residential Population",
            "Housing-Loss Shelter Demand Low",
            "Housing-Loss Shelter Demand Central",
            "Housing-Loss Shelter Demand High",
        ]
    ].sum()
    print(f"Wrote {len(selected):,} demand units to {OUTPUT.relative_to(ROOT)}")
    print(totals.to_string())


if __name__ == "__main__":
    main()
