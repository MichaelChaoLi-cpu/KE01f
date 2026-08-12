"""Build prefecture-wide shelter and demand connections to the road network.

Shelters are snapped directly to eligible road edges in EPSG:6670. This avoids
the earlier staging-site proxy that first required a shelter to be within 250 m
of a populated mesh. Group-level demand is allocated back to its constituent
125 m population meshes while exactly preserving every scenario total.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import shapely
from pyproj import Transformer
from shapely import STRtree, from_wkb, to_wkb, transform


ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "data" / "raw" / "prior_projects"
EDGES_PATH = PRIOR / "KE01d" / "kumamoto_routable_road_edges_preprocessed.parquet"
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
OUT = ROOT / "data" / "exp" / "prefecture-network-access-audit"

SOURCE_CRS = 6668
CALCULATION_CRS = 6670
MAXIMUM_SNAP_DISTANCE_M = 250.0

HOUSING_SCENARIOS = [
    "Housing-Loss Shelter Demand Low",
    "Housing-Loss Shelter Demand Central",
    "Housing-Loss Shelter Demand High",
]
OBSERVED_STRESS_SCENARIOS = [
    "Observed-Use Stress Demand Population Weighted",
    "Observed-Use Stress Demand Central Housing-Loss Weighted",
    "Observed-Use Stress Demand High Housing-Loss Weighted",
]


def geometry_array(series: pd.Series) -> np.ndarray:
    """Decode a WKB-backed parquet geometry column."""
    values = np.asarray(series, dtype=object)
    if len(values) == 0:
        return values
    if isinstance(values[0], (bytes, bytearray, memoryview)):
        return from_wkb(values)
    return values


def allocate_group_demand_to_meshes(
    mesh_access: pd.DataFrame, group_demand: pd.DataFrame, observed_total: float
) -> pd.DataFrame:
    """Allocate disclosure-group demand using constituent mesh population shares."""
    groups = group_demand[
        [
            "Residential Demand Unit ID",
            "Municipality Code",
            "Administrative Polygon Code",
            "Municipality",
            "Ward",
            "Residential Population",
            *HOUSING_SCENARIOS,
        ]
    ].copy()
    groups["Residential Demand Unit ID"] = groups["Residential Demand Unit ID"].astype("string")

    meshes = mesh_access.copy()
    meshes["Disclosure Group Code"] = meshes["Disclosure Group Code"].astype("string")
    meshes = meshes.merge(
        groups,
        left_on="Disclosure Group Code",
        right_on="Residential Demand Unit ID",
        how="left",
        validate="many_to_one",
    )
    if meshes["Residential Demand Unit ID"].isna().any():
        raise ValueError("Every population mesh must match one residential demand unit")

    group_population_from_meshes = meshes.groupby("Residential Demand Unit ID")[
        "Total Population"
    ].transform("sum")
    population_difference = (
        group_population_from_meshes.astype(float) - meshes["Residential Population"].astype(float)
    ).abs()
    if population_difference.max() > 1e-8:
        raise ValueError("Constituent mesh population does not preserve group population")
    meshes["Within-Group Population Share"] = (
        meshes["Total Population"].astype(float) / group_population_from_meshes.astype(float)
    )

    for scenario in HOUSING_SCENARIOS:
        group_values = meshes[scenario].astype(float)
        meshes[scenario] = group_values * meshes["Within-Group Population Share"]
        expected = float(group_demand[scenario].sum())
        if abs(float(meshes[scenario].sum()) - expected) > 1e-8:
            raise ValueError(f"Mesh allocation changed total for {scenario}")

    meshes[OBSERVED_STRESS_SCENARIOS[0]] = (
        observed_total * meshes["Total Population"].astype(float) / meshes["Total Population"].sum()
    )
    meshes[OBSERVED_STRESS_SCENARIOS[1]] = (
        observed_total
        * meshes[HOUSING_SCENARIOS[1]]
        / meshes[HOUSING_SCENARIOS[1]].sum()
    )
    meshes[OBSERVED_STRESS_SCENARIOS[2]] = (
        observed_total
        * meshes[HOUSING_SCENARIOS[2]]
        / meshes[HOUSING_SCENARIOS[2]].sum()
    )
    for scenario in OBSERVED_STRESS_SCENARIOS:
        if abs(float(meshes[scenario].sum()) - observed_total) > 1e-8:
            raise ValueError(f"Observed-use stress total changed for {scenario}")
    return meshes


def direct_shelter_snaps(edges: pd.DataFrame, shelters: pd.DataFrame) -> pd.DataFrame:
    """Snap every shelter point directly to its nearest eligible road edge."""
    eligible = edges.loc[
        edges["Network Analysis Eligible"].fillna(False)
        & edges["Road Available"].fillna(False)
    ].reset_index(drop=True)
    edge_geographic = geometry_array(eligible["Geometry"])
    point_geographic = shapely.points(
        shelters["Longitude"].to_numpy(float), shelters["Latitude"].to_numpy(float)
    )
    transformer = Transformer.from_crs(SOURCE_CRS, CALCULATION_CRS, always_xy=True)
    edge_projected = transform(edge_geographic, transformer.transform, interleaved=False)
    point_projected = transform(point_geographic, transformer.transform, interleaved=False)

    tree = STRtree(edge_projected)
    pairs, distances = tree.query_nearest(
        point_projected, all_matches=False, return_distance=True
    )
    if not np.array_equal(pairs[0], np.arange(len(shelters))):
        raise RuntimeError("Nearest-edge query did not return one result per shelter")
    edge_positions = pairs[1]
    nearest_edges = edge_projected[edge_positions]
    fractions = shapely.line_locate_point(nearest_edges, point_projected, normalized=True)
    snapped_projected = shapely.line_interpolate_point(
        nearest_edges, fractions, normalized=True
    )
    reverse_transformer = Transformer.from_crs(
        CALCULATION_CRS, SOURCE_CRS, always_xy=True
    )
    snapped_geographic = transform(
        snapped_projected, reverse_transformer.transform, interleaved=False
    )
    accepted = distances <= MAXIMUM_SNAP_DISTANCE_M

    selected_edges = eligible.iloc[edge_positions].reset_index(drop=True)
    result = shelters.copy().reset_index(drop=True)
    result["Shelter Network Node ID"] = pd.Series(
        [f"SHELTER-NETWORK-{position + 1:07d}" for position in range(len(result))],
        dtype="string",
    ).where(accepted)
    result["Shelter Network Snap Distance (m)"] = distances
    result["Shelter Network Snap Accepted"] = accepted
    result["Shelter Access Road Edge ID"] = pd.Series(
        selected_edges["Road Edge ID"].to_numpy(), dtype="string"
    ).where(accepted)
    result["Shelter Access Edge Fraction"] = pd.Series(
        fractions, dtype="Float64"
    ).where(accepted)
    result["Shelter Network Component ID"] = pd.Series(
        selected_edges["Network Component ID"].to_numpy(), dtype="string"
    ).where(accepted)
    result["Shelter Point Geometry"] = to_wkb(point_geographic)
    result["Shelter Snapped Network Geometry"] = pd.Series(
        to_wkb(snapped_geographic), dtype=object
    ).where(accepted)
    return result


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    edges = pd.read_parquet(EDGES_PATH)
    edge_reference = edges[
        ["Road Edge ID", "Network Component ID", "Road Available", "Network Analysis Eligible"]
    ].copy()
    if edge_reference["Road Edge ID"].duplicated().any():
        raise ValueError("Road Edge ID must be unique")

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
    shelter_audit = pd.read_csv(
        SHELTER_AUDIT_PATH, dtype={"Municipality Code": "string"}
    )[shelter_columns]
    shelter_access = direct_shelter_snaps(edges, shelter_audit)
    shelter_access.to_parquet(
        PROCESSED / "kumamoto_prefecture_shelter_network_access_preprocessed.parquet",
        index=False,
    )

    group_demand = pd.read_parquet(GROUP_DEMAND_PATH)
    snapshots = pd.read_parquet(SNAPSHOT_PATH)
    observed_total = float(snapshots["Reported Evacuees"].max())
    mesh_access = pd.read_parquet(MESH_ACCESS_PATH)
    demand_mesh = allocate_group_demand_to_meshes(
        mesh_access, group_demand, observed_total
    )
    demand_mesh = demand_mesh.merge(
        edge_reference[["Road Edge ID", "Network Component ID"]],
        left_on="Access Road Edge ID",
        right_on="Road Edge ID",
        how="left",
        validate="many_to_one",
    ).drop(columns="Road Edge ID")
    demand_mesh = demand_mesh.rename(
        columns={"Network Component ID": "Demand Network Component ID"}
    )

    general_components = set(
        shelter_access.loc[
            shelter_access["Shelter Service Class"].eq("general")
            & shelter_access["Shelter Network Snap Accepted"],
            "Shelter Network Component ID",
        ].dropna()
    )
    demand_mesh["Network Component Has General Shelter"] = demand_mesh[
        "Demand Network Component ID"
    ].isin(general_components)
    demand_mesh.to_parquet(
        PROCESSED / "kumamoto_prefecture_demand_mesh_network_access_preprocessed.parquet",
        index=False,
    )

    general = shelter_access.loc[
        shelter_access["Shelter Service Class"].eq("general")
    ].copy()
    coverage_rows: list[dict[str, object]] = [
        {
            "Metric": "General shelter direct road snaps accepted",
            "Numerator": int(general["Shelter Network Snap Accepted"].sum()),
            "Denominator": len(general),
            "Percent": 100 * general["Shelter Network Snap Accepted"].mean(),
        },
        {
            "Metric": "Population mesh road snaps accepted",
            "Numerator": int(demand_mesh["Network Snap Accepted"].sum()),
            "Denominator": len(demand_mesh),
            "Percent": 100 * demand_mesh["Network Snap Accepted"].mean(),
        },
        {
            "Metric": "Residential population with accepted road snap",
            "Numerator": float(
                demand_mesh.loc[demand_mesh["Network Snap Accepted"], "Total Population"].sum()
            ),
            "Denominator": float(demand_mesh["Total Population"].sum()),
            "Percent": 100
            * demand_mesh.loc[demand_mesh["Network Snap Accepted"], "Total Population"].sum()
            / demand_mesh["Total Population"].sum(),
        },
        {
            "Metric": "Residential population in component with general shelter",
            "Numerator": float(
                demand_mesh.loc[
                    demand_mesh["Network Component Has General Shelter"], "Total Population"
                ].sum()
            ),
            "Denominator": float(demand_mesh["Total Population"].sum()),
            "Percent": 100
            * demand_mesh.loc[
                demand_mesh["Network Component Has General Shelter"], "Total Population"
            ].sum()
            / demand_mesh["Total Population"].sum(),
        },
    ]
    for scenario in [*HOUSING_SCENARIOS, *OBSERVED_STRESS_SCENARIOS]:
        covered = demand_mesh.loc[
            demand_mesh["Network Component Has General Shelter"], scenario
        ].sum()
        total = demand_mesh[scenario].sum()
        coverage_rows.append(
            {
                "Metric": f"{scenario} in component with general shelter",
                "Numerator": float(covered),
                "Denominator": float(total),
                "Percent": 100 * covered / total if total else np.nan,
            }
        )
    coverage = pd.DataFrame(coverage_rows)
    coverage.to_csv(OUT / "network_access_coverage_summary.csv", index=False)

    shelter_component = (
        general.loc[general["Shelter Network Snap Accepted"]]
        .groupby("Shelter Network Component ID", as_index=False)
        .agg(General_Shelters=("Shelter ID", "size"))
        .rename(columns={"Shelter Network Component ID": "Network Component ID"})
    )
    demand_component = (
        demand_mesh.groupby("Demand Network Component ID", dropna=False, as_index=False)
        .agg(
            Population_Meshes=("Mesh Code", "size"),
            Residential_Population=("Total Population", "sum"),
            Housing_Loss_Demand_High=(HOUSING_SCENARIOS[2], "sum"),
            Observed_Use_Stress_High_Weighted=(OBSERVED_STRESS_SCENARIOS[2], "sum"),
        )
        .rename(columns={"Demand Network Component ID": "Network Component ID"})
    )
    component = demand_component.merge(
        shelter_component, on="Network Component ID", how="outer"
    )
    component["General_Shelters"] = component["General_Shelters"].fillna(0).astype(int)
    component["Component_Has_General_Shelter"] = component["General_Shelters"].gt(0)
    component.sort_values(
        ["Component_Has_General_Shelter", "Residential_Population"],
        ascending=[True, False],
    ).to_csv(OUT / "network_component_shelter_coverage.csv", index=False)

    municipality = (
        demand_mesh.groupby(["Municipality Code", "Municipality"], as_index=False)
        .agg(
            Population_Meshes=("Mesh Code", "size"),
            Residential_Population=("Total Population", "sum"),
            Population_in_Component_with_General_Shelter=(
                "Network Component Has General Shelter",
                lambda value: float(
                    demand_mesh.loc[value.index[value], "Total Population"].sum()
                ),
            ),
            High_Observed_Use_Stress_Demand=(OBSERVED_STRESS_SCENARIOS[2], "sum"),
            High_Observed_Use_Stress_Demand_in_Component_with_General_Shelter=(
                "Network Component Has General Shelter",
                lambda value: float(
                    demand_mesh.loc[value.index[value], OBSERVED_STRESS_SCENARIOS[2]].sum()
                ),
            ),
        )
    )
    municipal_general = (
        general.groupby(["Municipality Code", "Municipality"], as_index=False)
        .agg(
            General_Shelters=("Shelter ID", "size"),
            General_Shelters_with_Accepted_Direct_Road_Snap=(
                "Shelter Network Snap Accepted",
                "sum",
            ),
        )
    )
    municipality = municipality.merge(
        municipal_general,
        on=["Municipality Code", "Municipality"],
        how="left",
        validate="1:1",
    )
    municipality["Population_Component_Coverage_Percent"] = (
        100
        * municipality["Population_in_Component_with_General_Shelter"]
        / municipality["Residential_Population"]
    )
    municipality["High_Stress_Component_Coverage_Percent"] = (
        100
        * municipality[
            "High_Observed_Use_Stress_Demand_in_Component_with_General_Shelter"
        ]
        / municipality["High_Observed_Use_Stress_Demand"]
    )
    municipality.sort_values(
        ["High_Stress_Component_Coverage_Percent", "Residential_Population"]
    ).to_csv(OUT / "municipality_network_attachment_summary.csv", index=False)

    rejected = shelter_access.loc[~shelter_access["Shelter Network Snap Accepted"]].copy()
    rejected.to_csv(OUT / "rejected_shelter_direct_road_snaps.csv", index=False)

    readme = OUT / "README.md"
    readme.write_text(
        f"""# Prefecture network-access preprocessing audit

Shelters are snapped directly to eligible road edges in EPSG:6670 with a
{MAXIMUM_SNAP_DISTANCE_M:.0f} m acceptance threshold. This replaces the prior
staging-site proxy that required proximity to a populated mesh. Group demand is
allocated to 62,945 constituent 125 m population meshes using exact within-group
population shares.

- General shelters with accepted direct road snaps: {int(general['Shelter Network Snap Accepted'].sum()):,}/{len(general):,}
- Population meshes with accepted road snaps: {int(demand_mesh['Network Snap Accepted'].sum()):,}/{len(demand_mesh):,}
- Residential population with accepted road snaps: {coverage.loc[coverage['Metric'].eq('Residential population with accepted road snap'), 'Percent'].iloc[0]:.4f}%
- Residential population in a network component containing a general shelter: {coverage.loc[coverage['Metric'].eq('Residential population in component with general shelter'), 'Percent'].iloc[0]:.4f}%

Component coverage establishes topological possibility only. It does not establish
10-, 15-, or 30-minute walking access; shortest-path computation is the next step.
""",
        encoding="utf-8",
    )

    print(coverage.to_string(index=False))
    print(f"\nRejected direct shelter snaps: {len(rejected):,}")
    if len(rejected):
        print(
            rejected[
                [
                    "Shelter ID",
                    "Shelter Name",
                    "Municipality",
                    "Shelter Service Class",
                    "Shelter Network Snap Distance (m)",
                ]
            ].to_string(index=False)
        )
    print(f"\nWrote network-access audit to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
