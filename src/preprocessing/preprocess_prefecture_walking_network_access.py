"""Create pedestrian-screened network connections for shelters and demand meshes.

The upstream routable graph was built for emergency-vehicle analysis. For walking
access, this script conservatively removes national expressways and toll edges,
recomputes network components, and directly snaps shelter points and population-
mesh centroids to the remaining edges within 250 m.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import shapely
from pyproj import Transformer
from shapely import STRtree, from_wkb, to_wkb, transform

from preprocess_prefecture_shelter_network_access import (
    HOUSING_SCENARIOS,
    OBSERVED_STRESS_SCENARIOS,
    allocate_group_demand_to_meshes,
    geometry_array,
)


ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "data" / "raw" / "prior_projects"
EDGES_PATH = PRIOR / "KE01d" / "kumamoto_routable_road_edges_preprocessed.parquet"
MESH_SOURCE_PATH = PRIOR / "KE01" / "kumamoto_population_mesh_125m_preprocessed.parquet"
MESH_ACCESS_PATH = (
    PRIOR / "KE01b" / "kumamoto_population_mesh_network_access_preprocessed.parquet"
)
SHELTER_AUDIT_PATH = (
    ROOT
    / "data"
    / "exp"
    / "prefecture-shelter-capacity-audit"
    / "prefecture_shelter_capacity_evidence_audit.csv"
)
GROUP_DEMAND_PATH = (
    ROOT / "data" / "processed" / "kumamoto_prefecture_shelter_demand_preprocessed.parquet"
)
SNAPSHOT_PATH = (
    ROOT
    / "data"
    / "processed"
    / "kumamoto_2026_official_shelter_use_snapshots_preprocessed.parquet"
)
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "data" / "exp" / "prefecture-walking-network-audit"

SOURCE_CRS = 6668
CALCULATION_CRS = 6670
MAXIMUM_SNAP_DISTANCE_M = 250.0
EXPRESSWAY_CATEGORY = "National Expressway or Equivalent"
FREE_TOLL_CATEGORY = "Free"


def pedestrian_edges(edges: pd.DataFrame) -> pd.DataFrame:
    """Retain baseline edges that are conservatively eligible for walking."""
    keep = (
        edges["Network Analysis Eligible"].fillna(False)
        & edges["Road Available"].fillna(False)
        & edges["Road Category"].ne(EXPRESSWAY_CATEGORY)
        & edges["Toll Category"].eq(FREE_TOLL_CATEGORY)
    )
    result = edges.loc[keep].reset_index(drop=True).copy()
    if result.empty:
        raise ValueError("Pedestrian-screened road network is empty")
    return result


def walking_components(edges: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """Recompute components after removing expressway and toll edges."""
    graph = nx.Graph()
    graph.add_edges_from(zip(edges["From Node ID"], edges["To Node ID"], strict=True))
    components = sorted(nx.connected_components(graph), key=len, reverse=True)
    node_to_component: dict[str, str] = {}
    component_rows: list[dict[str, object]] = []
    for position, nodes in enumerate(components, start=1):
        component_id = f"WALK-COMP-{position:04d}"
        node_to_component.update({str(node): component_id for node in nodes})
        component_rows.append(
            {"Walking Network Component ID": component_id, "Network Nodes": len(nodes)}
        )
    edge_components = edges["From Node ID"].astype(str).map(node_to_component)
    if edge_components.isna().any():
        raise ValueError("Every walking edge must receive a recomputed component")
    return edge_components.astype("string"), pd.DataFrame(component_rows)


def snap_points(
    points_projected: np.ndarray,
    edge_projected: np.ndarray,
    edge_frame: pd.DataFrame,
) -> dict[str, object]:
    """Return direct nearest-edge attachment fields for projected points."""
    tree = STRtree(edge_projected)
    pairs, distances = tree.query_nearest(
        points_projected, all_matches=False, return_distance=True
    )
    if not np.array_equal(pairs[0], np.arange(len(points_projected))):
        raise RuntimeError("Nearest-edge query did not return one result per point")
    positions = pairs[1]
    nearest_edges = edge_projected[positions]
    fractions = shapely.line_locate_point(
        nearest_edges, points_projected, normalized=True
    )
    snapped = shapely.line_interpolate_point(
        nearest_edges, fractions, normalized=True
    )
    accepted = distances <= MAXIMUM_SNAP_DISTANCE_M
    selected = edge_frame.iloc[positions].reset_index(drop=True)
    return {
        "distance": distances,
        "accepted": accepted,
        "edge_id": selected["Road Edge ID"].to_numpy(),
        "edge_fraction": fractions,
        "from_node": selected["From Node ID"].to_numpy(),
        "to_node": selected["To Node ID"].to_numpy(),
        "component": selected["Walking Network Component ID"].to_numpy(),
        "snapped": snapped,
    }


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    edges_all = pd.read_parquet(EDGES_PATH)
    walking = pedestrian_edges(edges_all)
    walking["Walking Network Component ID"], component_nodes = walking_components(walking)

    forward = Transformer.from_crs(SOURCE_CRS, CALCULATION_CRS, always_xy=True)
    reverse = Transformer.from_crs(CALCULATION_CRS, SOURCE_CRS, always_xy=True)
    edge_geographic = geometry_array(walking["Geometry"])
    edge_projected = transform(edge_geographic, forward.transform, interleaved=False)

    # Shelter direct attachments.
    shelter_columns = [
        "Shelter ID",
        "Shelter Name",
        "Address",
        "Latitude",
        "Longitude",
        "Municipality Code",
        "Municipality",
        "Ward",
        "Facility Type",
        "Shelter Service Class",
        "Capacity Evidence Tier",
        "Official Numeric Capacity",
    ]
    shelters = pd.read_csv(
        SHELTER_AUDIT_PATH, dtype={"Municipality Code": "string"}
    )[shelter_columns]
    shelter_points_geographic = shapely.points(
        shelters["Longitude"].to_numpy(float), shelters["Latitude"].to_numpy(float)
    )
    shelter_points_projected = transform(
        shelter_points_geographic, forward.transform, interleaved=False
    )
    shelter_snap = snap_points(shelter_points_projected, edge_projected, walking)
    shelter_accepted = np.asarray(shelter_snap["accepted"], dtype=bool)
    shelter_snapped_geographic = transform(
        shelter_snap["snapped"], reverse.transform, interleaved=False
    )
    shelter_access = shelters.copy()
    shelter_access["Walking Network Node ID"] = pd.Series(
        [f"SHELTER-WALK-{position + 1:07d}" for position in range(len(shelters))],
        dtype="string",
    ).where(shelter_accepted)
    shelter_access["Walking Network Snap Distance (m)"] = shelter_snap["distance"]
    shelter_access["Walking Network Snap Accepted"] = shelter_accepted
    shelter_access["Walking Access Road Edge ID"] = pd.Series(
        shelter_snap["edge_id"], dtype="string"
    ).where(shelter_accepted)
    shelter_access["Walking Access Edge Fraction"] = pd.Series(
        shelter_snap["edge_fraction"], dtype="Float64"
    ).where(shelter_accepted)
    shelter_access["Walking Access From Node ID"] = pd.Series(
        shelter_snap["from_node"], dtype="string"
    ).where(shelter_accepted)
    shelter_access["Walking Access To Node ID"] = pd.Series(
        shelter_snap["to_node"], dtype="string"
    ).where(shelter_accepted)
    shelter_access["Walking Network Component ID"] = pd.Series(
        shelter_snap["component"], dtype="string"
    ).where(shelter_accepted)
    shelter_access["Shelter Point Geometry"] = to_wkb(shelter_points_geographic)
    shelter_access["Walking Snapped Network Geometry"] = pd.Series(
        to_wkb(shelter_snapped_geographic), dtype=object
    ).where(shelter_accepted)
    shelter_path = (
        PROCESSED / "kumamoto_prefecture_shelter_walking_network_access_preprocessed.parquet"
    )
    shelter_access.to_parquet(shelter_path, index=False)

    # Population-mesh centroid direct attachments and demand construction.
    mesh_source = pd.read_parquet(MESH_SOURCE_PATH)
    mesh_access_upstream = pd.read_parquet(MESH_ACCESS_PATH).drop(columns="Geometry")
    if not mesh_source["Mesh Code"].is_unique or not mesh_access_upstream["Mesh Code"].is_unique:
        raise ValueError("Mesh Code must be unique")
    mesh_polygons_geographic = geometry_array(mesh_source["geometry"])
    mesh_polygons_projected = transform(
        mesh_polygons_geographic, forward.transform, interleaved=False
    )
    mesh_centroids_projected = shapely.centroid(mesh_polygons_projected)
    mesh_centroids_geographic = transform(
        mesh_centroids_projected, reverse.transform, interleaved=False
    )
    mesh_snap = snap_points(mesh_centroids_projected, edge_projected, walking)
    mesh_accepted = np.asarray(mesh_snap["accepted"], dtype=bool)
    mesh_snapped_geographic = transform(
        mesh_snap["snapped"], reverse.transform, interleaved=False
    )

    mesh = mesh_access_upstream.merge(
        mesh_source[["Mesh Code", "geometry"]].rename(columns={"geometry": "Mesh Geometry"}),
        on="Mesh Code",
        how="left",
        validate="1:1",
    )
    mesh["Walking Demand Node ID"] = pd.Series(
        [f"DEMAND-WALK-{position + 1:07d}" for position in range(len(mesh))],
        dtype="string",
    ).where(mesh_accepted)
    mesh["Walking Network Snap Distance (m)"] = mesh_snap["distance"]
    mesh["Walking Network Snap Accepted"] = mesh_accepted
    mesh["Walking Access Road Edge ID"] = pd.Series(
        mesh_snap["edge_id"], dtype="string"
    ).where(mesh_accepted)
    mesh["Walking Access Edge Fraction"] = pd.Series(
        mesh_snap["edge_fraction"], dtype="Float64"
    ).where(mesh_accepted)
    mesh["Walking Access From Node ID"] = pd.Series(
        mesh_snap["from_node"], dtype="string"
    ).where(mesh_accepted)
    mesh["Walking Access To Node ID"] = pd.Series(
        mesh_snap["to_node"], dtype="string"
    ).where(mesh_accepted)
    mesh["Walking Network Component ID"] = pd.Series(
        mesh_snap["component"], dtype="string"
    ).where(mesh_accepted)
    mesh["Mesh Centroid Geometry"] = to_wkb(mesh_centroids_geographic)
    mesh["Walking Snapped Network Geometry"] = pd.Series(
        to_wkb(mesh_snapped_geographic), dtype=object
    ).where(mesh_accepted)

    group_demand = pd.read_parquet(GROUP_DEMAND_PATH)
    observed_total = float(pd.read_parquet(SNAPSHOT_PATH)["Reported Evacuees"].max())
    demand_mesh = allocate_group_demand_to_meshes(mesh, group_demand, observed_total)

    general_components = set(
        shelter_access.loc[
            shelter_access["Shelter Service Class"].eq("general")
            & shelter_access["Walking Network Snap Accepted"],
            "Walking Network Component ID",
        ].dropna()
    )
    demand_mesh["Walking Network Component Has General Shelter"] = demand_mesh[
        "Walking Network Component ID"
    ].isin(general_components)
    demand_path = (
        PROCESSED / "kumamoto_prefecture_demand_mesh_walking_network_access_preprocessed.parquet"
    )
    demand_mesh.to_parquet(demand_path, index=False)

    general = shelter_access.loc[shelter_access["Shelter Service Class"].eq("general")]
    summary_rows: list[dict[str, object]] = [
        {
            "Metric": "Vehicle-network edge length removed from walking graph (m)",
            "Numerator": float(edges_all["Road Length (m)"].sum() - walking["Road Length (m)"].sum()),
            "Denominator": float(edges_all["Road Length (m)"].sum()),
            "Percent": 100
            * (edges_all["Road Length (m)"].sum() - walking["Road Length (m)"].sum())
            / edges_all["Road Length (m)"].sum(),
        },
        {
            "Metric": "General shelter walking-network snaps accepted",
            "Numerator": int(general["Walking Network Snap Accepted"].sum()),
            "Denominator": len(general),
            "Percent": 100 * general["Walking Network Snap Accepted"].mean(),
        },
        {
            "Metric": "Population mesh walking-network snaps accepted",
            "Numerator": int(demand_mesh["Walking Network Snap Accepted"].sum()),
            "Denominator": len(demand_mesh),
            "Percent": 100 * demand_mesh["Walking Network Snap Accepted"].mean(),
        },
        {
            "Metric": "Residential population with walking-network snap",
            "Numerator": float(
                demand_mesh.loc[demand_mesh["Walking Network Snap Accepted"], "Total Population"].sum()
            ),
            "Denominator": float(demand_mesh["Total Population"].sum()),
            "Percent": 100
            * demand_mesh.loc[demand_mesh["Walking Network Snap Accepted"], "Total Population"].sum()
            / demand_mesh["Total Population"].sum(),
        },
        {
            "Metric": "Residential population in walking component with general shelter",
            "Numerator": float(
                demand_mesh.loc[
                    demand_mesh["Walking Network Component Has General Shelter"], "Total Population"
                ].sum()
            ),
            "Denominator": float(demand_mesh["Total Population"].sum()),
            "Percent": 100
            * demand_mesh.loc[
                demand_mesh["Walking Network Component Has General Shelter"], "Total Population"
            ].sum()
            / demand_mesh["Total Population"].sum(),
        },
    ]
    for scenario in [*HOUSING_SCENARIOS, *OBSERVED_STRESS_SCENARIOS]:
        total = float(demand_mesh[scenario].sum())
        covered = float(
            demand_mesh.loc[
                demand_mesh["Walking Network Component Has General Shelter"], scenario
            ].sum()
        )
        summary_rows.append(
            {
                "Metric": f"{scenario} in walking component with general shelter",
                "Numerator": covered,
                "Denominator": total,
                "Percent": 100 * covered / total if total else np.nan,
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT / "walking_network_access_coverage_summary.csv", index=False)

    component_shelters = (
        general.loc[general["Walking Network Snap Accepted"]]
        .groupby("Walking Network Component ID", as_index=False)
        .agg(General_Shelters=("Shelter ID", "size"))
    )
    component_demand = demand_mesh.groupby(
        "Walking Network Component ID", dropna=False, as_index=False
    ).agg(
        Population_Meshes=("Mesh Code", "size"),
        Residential_Population=("Total Population", "sum"),
        High_Housing_Loss_Demand=(HOUSING_SCENARIOS[2], "sum"),
        High_Weighted_Observed_Use_Stress=(OBSERVED_STRESS_SCENARIOS[2], "sum"),
    )
    components = component_nodes.merge(
        component_demand, on="Walking Network Component ID", how="outer"
    ).merge(component_shelters, on="Walking Network Component ID", how="left")
    components["General_Shelters"] = components["General_Shelters"].fillna(0).astype(int)
    components["Component_Has_General_Shelter"] = components["General_Shelters"].gt(0)
    components.sort_values(
        ["Component_Has_General_Shelter", "Residential_Population"],
        ascending=[True, False],
    ).to_csv(OUT / "walking_network_component_shelter_coverage.csv", index=False)

    shelter_access.loc[~shelter_access["Walking Network Snap Accepted"]].to_csv(
        OUT / "rejected_shelter_walking_network_snaps.csv", index=False
    )
    demand_mesh.loc[~demand_mesh["Walking Network Snap Accepted"]].to_csv(
        OUT / "rejected_demand_mesh_walking_network_snaps.csv", index=False
    )

    (OUT / "README.md").write_text(
        f"""# Pedestrian-screened network-access audit

National expressways and toll edges are excluded before calculating walking
access. Network components are recomputed after exclusion. Shelter points and
population-mesh centroids are snapped directly to the remaining road edges in
EPSG:6670 using a {MAXIMUM_SNAP_DISTANCE_M:.0f} m acceptance threshold.

- Walking edges: {len(walking):,} of {len(edges_all):,}
- General shelters with accepted walking snaps: {int(general['Walking Network Snap Accepted'].sum()):,}/{len(general):,}
- Population meshes with accepted walking snaps: {int(demand_mesh['Walking Network Snap Accepted'].sum()):,}/{len(demand_mesh):,}
- Recomputed walking components: {len(component_nodes):,}

This is an access-preprocessing audit, not yet a 10-, 15-, or 30-minute
coverage result. The next analysis runs shortest paths on this screened graph.
""",
        encoding="utf-8",
    )

    print(summary.to_string(index=False))
    print(f"\nWalking edges: {len(walking):,}/{len(edges_all):,}")
    print(
        "Rejected general shelter snaps: "
        f"{int((~general['Walking Network Snap Accepted']).sum()):,}"
    )
    print(
        "Rejected demand mesh snaps: "
        f"{int((~demand_mesh['Walking Network Snap Accepted']).sum()):,}"
    )
    print(f"Wrote {shelter_path.relative_to(ROOT)}")
    print(f"Wrote {demand_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
