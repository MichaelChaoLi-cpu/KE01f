"""Prepare true 125 m mesh polygons and Kumamoto City ward boundaries for maps."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEMAND_INPUT = (
    ROOT / "data/processed/kumamoto_shelter_demand_125m_network_preprocessed.parquet"
)
MESH_GEOMETRY_INPUT = (
    ROOT / "data/raw/prior_projects/KE01/kumamoto_population_mesh_125m_preprocessed.parquet"
)
ADMIN_INPUT = (
    ROOT / "data/raw/prior_projects/KE01b/kumamoto_administrative_areas_preprocessed.parquet"
)
MESH_OUTPUT = ROOT / "data/processed/kumamoto_shelter_demand_125m_map_preprocessed.parquet"
WARD_OUTPUT = ROOT / "data/processed/kumamoto_city_ward_boundaries_preprocessed.parquet"


def main() -> None:
    demand = pd.read_parquet(DEMAND_INPUT)
    mesh_geometry = pd.read_parquet(MESH_GEOMETRY_INPUT, columns=["Mesh Code", "geometry"])
    mesh_geometry = mesh_geometry.rename(columns={"geometry": "125 m Mesh Geometry WKB"})
    mapped = demand.merge(mesh_geometry, on="Mesh Code", how="left", validate="one_to_one")
    if len(mapped) != 11_146 or mapped["125 m Mesh Geometry WKB"].isna().any():
        raise ValueError("Every Kumamoto City demand mesh must match one polygon")

    admin = pd.read_parquet(ADMIN_INPUT)
    wards = admin.loc[
        admin["Municipality Name"].eq("熊本市"),
        ["Municipality Code", "Ward Name", "Municipality Label", "Geometry"],
    ].rename(
        columns={
            "Municipality Code": "Ward Code",
            "Ward Name": "Ward",
            "Municipality Label": "Ward Label (Japanese)",
            "Geometry": "Ward Boundary Geometry WKB",
        }
    )
    ward_english = {
        "中央区": "Chuo Ward",
        "東区": "Higashi Ward",
        "西区": "Nishi Ward",
        "南区": "Minami Ward",
        "北区": "Kita Ward",
    }
    wards["Ward Label"] = wards["Ward"].map(ward_english)
    wards = wards[
        [
            "Ward Code",
            "Ward",
            "Ward Label",
            "Ward Label (Japanese)",
            "Ward Boundary Geometry WKB",
        ]
    ].sort_values("Ward Code").reset_index(drop=True)
    if len(wards) != 5 or wards["Ward Boundary Geometry WKB"].isna().any():
        raise ValueError("Expected five complete Kumamoto City ward polygons")

    MESH_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    mapped.to_parquet(MESH_OUTPUT, index=False)
    wards.to_parquet(WARD_OUTPUT, index=False)
    print(f"Wrote {len(mapped):,} mesh polygons to {MESH_OUTPUT.relative_to(ROOT)}")
    print(f"Wrote {len(wards)} ward boundaries to {WARD_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
