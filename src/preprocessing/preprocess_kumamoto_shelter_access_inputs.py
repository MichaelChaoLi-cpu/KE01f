"""Prepare 125 m demand nodes and shelter network attachments for access analysis."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import shapely
from shapely import from_wkb


ROOT = Path(__file__).resolve().parents[2]
GROUP_DEMAND_INPUT = (
    ROOT / "data/processed/kumamoto_shelter_demand_scenarios_preprocessed.parquet"
)
MESH_ACCESS_INPUT = (
    ROOT
    / "data/raw/prior_projects/KE01b/kumamoto_population_mesh_network_access_preprocessed.parquet"
)
ROAD_EDGE_INPUT = (
    ROOT
    / "data/raw/prior_projects/KE01d/kumamoto_routable_road_edges_preprocessed.parquet"
)
ROAD_NODE_INPUT = (
    ROOT
    / "data/raw/prior_projects/KE01d/kumamoto_routable_road_nodes_preprocessed.parquet"
)
SHELTER_INPUT = (
    ROOT / "data/processed/kumamoto_shelter_capacity_scenarios_preprocessed.parquet"
)
DEMAND_OUTPUT = (
    ROOT / "data/processed/kumamoto_shelter_demand_125m_network_preprocessed.parquet"
)
SHELTER_OUTPUT = (
    ROOT / "data/processed/kumamoto_shelter_network_access_preprocessed.parquet"
)
AUDIT_OUTPUT = ROOT / "data/exp/shelter-access-preparation/network_attachment_audit.csv"


def approximate_distance_m(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    """Approximate short point-to-point distances in metres in Kumamoto."""
    first_x = shapely.get_x(first)
    first_y = shapely.get_y(first)
    second_x = shapely.get_x(second)
    second_y = shapely.get_y(second)
    mean_latitude = (first_y + second_y) / 2
    x_m = (first_x - second_x) * 111_320 * np.cos(np.deg2rad(mean_latitude))
    y_m = (first_y - second_y) * 110_574
    return np.sqrt(x_m**2 + y_m**2)


def prepare_demand_nodes() -> pd.DataFrame:
    group_demand = pd.read_parquet(GROUP_DEMAND_INPUT)
    mesh_access = pd.read_parquet(MESH_ACCESS_INPUT)
    road_edges = pd.read_parquet(ROAD_EDGE_INPUT)[
        [
            "Road Edge ID",
            "From Node ID",
            "To Node ID",
            "Network Component ID",
            "Road Length (m)",
            "Road Available",
            "Network Analysis Eligible",
        ]
    ]

    demand = mesh_access.loc[
        mesh_access["Disclosure Group Code"].isin(group_demand["Residential Demand Unit ID"])
    ].copy()
    group_fields = group_demand[
        [
            "Residential Demand Unit ID",
            "Ward Code",
            "Ward",
            "Residential Population",
            "Housing-Loss Shelter Demand Low",
            "Housing-Loss Shelter Demand Central",
            "Housing-Loss Shelter Demand High",
            "Housing-Loss Shelter Demand Age 65+ Low",
            "Housing-Loss Shelter Demand Age 65+ Central",
            "Housing-Loss Shelter Demand Age 65+ High",
        ]
    ].rename(
        columns={
            "Residential Demand Unit ID": "Disclosure Group Code",
            "Residential Population": "Group Residential Population",
        }
    )
    demand = demand.merge(
        group_fields,
        on="Disclosure Group Code",
        how="left",
        validate="many_to_one",
    )

    reconstructed_group_population = demand.groupby("Disclosure Group Code")[
        "Total Population"
    ].transform("sum")
    if not np.array_equal(
        reconstructed_group_population.to_numpy(),
        demand["Group Residential Population"].to_numpy(),
    ):
        raise ValueError("125 m mesh population does not reconstruct disclosure-group population")
    demand["Within-Group Population Share"] = (
        demand["Total Population"] / demand["Group Residential Population"]
    )

    allocation_columns = [
        "Housing-Loss Shelter Demand Low",
        "Housing-Loss Shelter Demand Central",
        "Housing-Loss Shelter Demand High",
        "Housing-Loss Shelter Demand Age 65+ Low",
        "Housing-Loss Shelter Demand Age 65+ Central",
        "Housing-Loss Shelter Demand Age 65+ High",
    ]
    for column in allocation_columns:
        demand[f"125 m {column}"] = demand[column] * demand["Within-Group Population Share"]

    demand = demand.merge(
        road_edges,
        left_on="Access Road Edge ID",
        right_on="Road Edge ID",
        how="left",
        validate="many_to_one",
    )
    rename = {
        "Mesh Code": "Mesh Code",
        "Geometry": "Mesh Centroid Geometry WKB",
        "Disclosure Group Code": "Residential Demand Unit ID",
        "Total Population": "125 m Residential Population",
        "Demand Node ID": "Demand Node ID",
        "Network Snap Distance (m)": "Demand Network Snap Distance (m)",
        "Network Snap Accepted": "Demand Network Snap Accepted",
        "Access Road Edge ID": "Demand Access Road Edge ID",
        "Access Edge Fraction": "Demand Access Edge Fraction",
        "From Node ID": "Access Edge From Node ID",
        "To Node ID": "Access Edge To Node ID",
        "Network Component ID": "Demand Network Component ID",
        "Road Length (m)": "Access Edge Length (m)",
    }
    demand = demand.rename(columns=rename)
    demand = demand.rename(
        columns={
            f"125 m {column}": f"{column} at 125 m"
            for column in allocation_columns
        }
    )
    columns = [
        "Mesh Code",
        "Mesh Centroid Geometry WKB",
        "Residential Demand Unit ID",
        "Ward Code",
        "Ward",
        "125 m Residential Population",
        "Within-Group Population Share",
        "Housing-Loss Shelter Demand Low at 125 m",
        "Housing-Loss Shelter Demand Central at 125 m",
        "Housing-Loss Shelter Demand High at 125 m",
        "Housing-Loss Shelter Demand Age 65+ Low at 125 m",
        "Housing-Loss Shelter Demand Age 65+ Central at 125 m",
        "Housing-Loss Shelter Demand Age 65+ High at 125 m",
        "Demand Node ID",
        "Demand Network Snap Distance (m)",
        "Demand Network Snap Accepted",
        "Demand Access Road Edge ID",
        "Demand Access Edge Fraction",
        "Access Edge From Node ID",
        "Access Edge To Node ID",
        "Demand Network Component ID",
        "Access Edge Length (m)",
        "Road Available",
        "Network Analysis Eligible",
    ]
    demand = demand[columns].sort_values("Mesh Code").reset_index(drop=True)

    if len(demand) != 11_146 or demand["Mesh Code"].duplicated().any():
        raise ValueError("Expected 11,146 unique Kumamoto City 125 m demand meshes")
    if not demand["Demand Network Snap Accepted"].all():
        raise ValueError("All selected demand meshes should have accepted network snaps")
    for group_column, mesh_column in [
        (column, f"{column} at 125 m") for column in allocation_columns
    ]:
        original_total = float(group_demand[group_column].sum())
        allocated_total = float(demand[mesh_column].sum())
        if not np.isclose(original_total, allocated_total, rtol=0, atol=1e-8):
            raise ValueError(f"Demand allocation does not preserve {group_column}")
    return demand


def prepare_shelter_nodes() -> pd.DataFrame:
    shelters = pd.read_parquet(SHELTER_INPUT)
    road_nodes = pd.read_parquet(ROAD_NODE_INPUT)
    eligible_nodes = road_nodes.loc[road_nodes["Network Analysis Eligible"]].copy()
    node_geometries = from_wkb(eligible_nodes["Geometry"].to_numpy())
    shelter_geometries = from_wkb(shelters["Shelter Geometry WKB"].to_numpy())
    tree = shapely.STRtree(node_geometries)
    nearest_indices = tree.nearest(shelter_geometries)
    nearest = eligible_nodes.iloc[nearest_indices].reset_index(drop=True)
    nearest_geometries = node_geometries[nearest_indices]

    output = shelters.copy().reset_index(drop=True)
    output["Shelter Network Node ID"] = nearest["Network Node ID"]
    output["Shelter Network Component ID"] = nearest["Network Component ID"]
    output["Shelter Network Snap Distance (m)"] = approximate_distance_m(
        shelter_geometries, nearest_geometries
    )
    output["Shelter Network Snap Accepted"] = output[
        "Shelter Network Snap Distance (m)"
    ].le(200)

    if not output["Shelter Network Snap Accepted"].all():
        raise ValueError("Every shelter must be within 200 m of an eligible road node")
    if output["Shelter ID"].duplicated().any() or len(output) != 182:
        raise ValueError("Expected 182 unique shelter network attachments")
    return output


def main() -> None:
    demand = prepare_demand_nodes()
    shelters = prepare_shelter_nodes()
    DEMAND_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    demand.to_parquet(DEMAND_OUTPUT, index=False)
    shelters.to_parquet(SHELTER_OUTPUT, index=False)

    main_component = shelters["Shelter Network Component ID"].mode().iloc[0]
    audit = pd.DataFrame(
        [
            {"Metric": "125 m demand meshes", "Value": len(demand), "Unit": "meshes"},
            {
                "Metric": "Demand population with accepted network snap",
                "Value": int(
                    demand.loc[
                        demand["Demand Network Snap Accepted"],
                        "125 m Residential Population",
                    ].sum()
                ),
                "Unit": "persons",
            },
            {
                "Metric": "Demand population in main shelter component",
                "Value": int(
                    demand.loc[
                        demand["Demand Network Component ID"].eq(main_component),
                        "125 m Residential Population",
                    ].sum()
                ),
                "Unit": "persons",
            },
            {"Metric": "Shelters attached", "Value": len(shelters), "Unit": "shelters"},
            {
                "Metric": "Shelters in main component",
                "Value": int(shelters["Shelter Network Component ID"].eq(main_component).sum()),
                "Unit": "shelters",
            },
            {
                "Metric": "Median shelter network snap distance",
                "Value": float(shelters["Shelter Network Snap Distance (m)"].median()),
                "Unit": "m",
            },
            {
                "Metric": "Maximum shelter network snap distance",
                "Value": float(shelters["Shelter Network Snap Distance (m)"].max()),
                "Unit": "m",
            },
        ]
    )
    audit.to_csv(AUDIT_OUTPUT, index=False)
    print(f"Wrote {len(demand):,} demand meshes to {DEMAND_OUTPUT.relative_to(ROOT)}")
    print(f"Wrote {len(shelters)} shelter attachments to {SHELTER_OUTPUT.relative_to(ROOT)}")
    print(audit.to_string(index=False))


if __name__ == "__main__":
    main()
