"""Estimate nearest general-shelter walking access on the screened road graph.

This first network result measures whether each populated 125 m mesh can reach at
least one general shelter within 10, 15, or 30 minutes. It does not yet impose the
50-person capacity or 415-opening constraints.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "data" / "raw" / "prior_projects"
EDGES_PATH = PRIOR / "KE01d" / "kumamoto_routable_road_edges_preprocessed.parquet"
DEMAND_PATH = (
    ROOT
    / "data"
    / "processed"
    / "kumamoto_prefecture_demand_mesh_walking_network_access_preprocessed.parquet"
)
SHELTER_PATH = (
    ROOT
    / "data"
    / "processed"
    / "kumamoto_prefecture_shelter_walking_network_access_preprocessed.parquet"
)
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "data" / "exp" / "prefecture-shelter-walking-access"

EXPRESSWAY_CATEGORY = "National Expressway or Equivalent"
FREE_TOLL_CATEGORY = "Free"
SUPER_SOURCE = "__ALL_GENERAL_SHELTERS__"
MAXIMUM_DISTANCE_M = 2000.0
SPEEDS_KMH = (3, 4)
THRESHOLDS_MIN = (10, 15, 30)

DEMAND_SCENARIOS = [
    "Housing-Loss Shelter Demand Low",
    "Housing-Loss Shelter Demand Central",
    "Housing-Loss Shelter Demand High",
    "Observed-Use Stress Demand Population Weighted",
    "Observed-Use Stress Demand Central Housing-Loss Weighted",
    "Observed-Use Stress Demand High Housing-Loss Weighted",
]


def walking_edges() -> pd.DataFrame:
    edges = pd.read_parquet(
        EDGES_PATH,
        columns=[
            "Road Edge ID",
            "From Node ID",
            "To Node ID",
            "Road Length (m)",
            "Road Available",
            "Network Analysis Eligible",
            "Road Category",
            "Toll Category",
        ],
    )
    keep = (
        edges["Network Analysis Eligible"].fillna(False)
        & edges["Road Available"].fillna(False)
        & edges["Road Category"].ne(EXPRESSWAY_CATEGORY)
        & edges["Toll Category"].eq(FREE_TOLL_CATEGORY)
    )
    edges = edges.loc[keep].copy()
    edges["Node A"] = np.minimum(
        edges["From Node ID"].astype(str), edges["To Node ID"].astype(str)
    )
    edges["Node B"] = np.maximum(
        edges["From Node ID"].astype(str), edges["To Node ID"].astype(str)
    )
    return edges


def graph_with_shelter_sources(
    edges: pd.DataFrame, shelters: pd.DataFrame
) -> tuple[nx.Graph, pd.DataFrame]:
    graph = nx.Graph()
    graph_edges = edges.sort_values("Road Length (m)").drop_duplicates(["Node A", "Node B"])
    graph.add_weighted_edges_from(
        graph_edges[["From Node ID", "To Node ID", "Road Length (m)"]].itertuples(
            index=False, name=None
        )
    )

    edge_lookup = edges[
        ["Road Edge ID", "From Node ID", "To Node ID", "Road Length (m)"]
    ].drop_duplicates("Road Edge ID")
    sources = shelters.loc[
        shelters["Shelter Service Class"].eq("general")
        & shelters["Walking Network Snap Accepted"]
    ].merge(
        edge_lookup,
        left_on="Walking Access Road Edge ID",
        right_on="Road Edge ID",
        how="inner",
        validate="many_to_one",
    )
    fraction = sources["Walking Access Edge Fraction"].astype(float).clip(0, 1)
    source_to_from = (
        sources["Walking Network Snap Distance (m)"].astype(float)
        + fraction * sources["Road Length (m)"].astype(float)
    )
    source_to_to = (
        sources["Walking Network Snap Distance (m)"].astype(float)
        + (1 - fraction) * sources["Road Length (m)"].astype(float)
    )
    endpoint_costs = pd.concat(
        [
            pd.DataFrame(
                {"Node": sources["From Node ID"].astype(str), "Cost": source_to_from}
            ),
            pd.DataFrame(
                {"Node": sources["To Node ID"].astype(str), "Cost": source_to_to}
            ),
        ],
        ignore_index=True,
    ).groupby("Node", as_index=False)["Cost"].min()
    graph.add_weighted_edges_from(
        (SUPER_SOURCE, row.Node, float(row.Cost))
        for row in endpoint_costs.itertuples(index=False)
    )
    return graph, sources


def same_edge_direct_distance(
    demand: pd.DataFrame, shelter_sources: pd.DataFrame, edge_lengths: pd.Series
) -> np.ndarray:
    """Calculate direct along-edge access when demand and shelter share an edge."""
    shelter_by_edge: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for edge_id, frame in shelter_sources.groupby("Walking Access Road Edge ID"):
        shelter_by_edge[str(edge_id)] = (
            frame["Walking Access Edge Fraction"].to_numpy(float),
            frame["Walking Network Snap Distance (m)"].to_numpy(float),
        )
    result = np.full(len(demand), np.inf, dtype=float)
    edge_ids = demand["Walking Access Road Edge ID"].astype("string").to_numpy()
    demand_fraction = demand["Walking Access Edge Fraction"].astype(float).to_numpy()
    demand_snap = demand["Walking Network Snap Distance (m)"].to_numpy(float)
    for position, edge_id in enumerate(edge_ids):
        if pd.isna(edge_id):
            continue
        candidates = shelter_by_edge.get(str(edge_id))
        if candidates is None:
            continue
        shelter_fraction, shelter_snap = candidates
        length = float(edge_lengths.loc[str(edge_id)])
        result[position] = demand_snap[position] + np.min(
            shelter_snap + np.abs(demand_fraction[position] - shelter_fraction) * length
        )
    return result


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    edges = walking_edges()
    demand = pd.read_parquet(DEMAND_PATH)
    shelters = pd.read_parquet(SHELTER_PATH)
    graph, shelter_sources = graph_with_shelter_sources(edges, shelters)
    node_distance = nx.single_source_dijkstra_path_length(
        graph, SUPER_SOURCE, cutoff=MAXIMUM_DISTANCE_M, weight="weight"
    )

    edge_lookup = edges[
        ["Road Edge ID", "From Node ID", "To Node ID", "Road Length (m)"]
    ].drop_duplicates("Road Edge ID")
    analysis = demand.merge(
        edge_lookup,
        left_on="Walking Access Road Edge ID",
        right_on="Road Edge ID",
        how="left",
        validate="many_to_one",
    )
    fraction = analysis["Walking Access Edge Fraction"].astype(float)
    from_distance = analysis["From Node ID"].astype("string").map(node_distance)
    to_distance = analysis["To Node ID"].astype("string").map(node_distance)
    # `np.minimum` propagates NaN when one endpoint lies beyond the Dijkstra
    # cutoff even if the other endpoint provides a valid route. `np.fmin`
    # retains the finite endpoint and therefore implements the intended minimum.
    via_endpoints = analysis["Walking Network Snap Distance (m)"].astype(float) + np.fmin(
        fraction * analysis["Road Length (m)"].astype(float) + from_distance,
        (1 - fraction) * analysis["Road Length (m)"].astype(float) + to_distance,
    )
    direct = same_edge_direct_distance(
        analysis,
        shelter_sources,
        edge_lookup.set_index("Road Edge ID")["Road Length (m)"],
    )
    nearest = np.minimum(via_endpoints.fillna(np.inf).to_numpy(float), direct)
    nearest[~analysis["Walking Network Snap Accepted"].fillna(False).to_numpy()] = np.inf
    analysis["Nearest General Shelter Walking Distance (m), Capped at 2 km"] = np.where(
        np.isfinite(nearest) & (nearest <= MAXIMUM_DISTANCE_M), nearest, np.nan
    )
    analysis["Beyond 30-Minute Maximum Walking Screen"] = ~np.isfinite(nearest) | (
        nearest > MAXIMUM_DISTANCE_M
    )

    for speed in SPEEDS_KMH:
        time_column = f"Nearest General Shelter Walking Time at {speed} km/h (min)"
        analysis[time_column] = np.where(
            np.isfinite(nearest) & (nearest <= MAXIMUM_DISTANCE_M),
            60 * nearest / (1000 * speed),
            np.nan,
        )
        for threshold in THRESHOLDS_MIN:
            analysis[f"Reachable within {threshold} min at {speed} km/h"] = (
                analysis[time_column].le(threshold).fillna(False)
            )

    output_columns_to_drop = ["Road Edge ID", "From Node ID", "To Node ID", "Road Length (m)"]
    analysis = analysis.drop(columns=output_columns_to_drop)
    processed_path = (
        PROCESSED / "kumamoto_prefecture_nearest_shelter_walking_access_preprocessed.parquet"
    )
    analysis.to_parquet(processed_path, index=False)

    summary_rows: list[dict[str, object]] = []
    for speed in SPEEDS_KMH:
        for threshold in THRESHOLDS_MIN:
            reach = analysis[f"Reachable within {threshold} min at {speed} km/h"]
            for scenario in ["Total Population", *DEMAND_SCENARIOS]:
                total = float(analysis[scenario].sum())
                covered = float(analysis.loc[reach, scenario].sum())
                summary_rows.append(
                    {
                        "Walking Speed (km/h)": speed,
                        "Time Threshold (min)": threshold,
                        "Coverage Measure": scenario,
                        "Covered": covered,
                        "Total": total,
                        "Coverage Percent": 100 * covered / total if total else np.nan,
                    }
                )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT / "prefecture_walking_access_coverage_summary.csv", index=False)

    municipality_rows: list[pd.DataFrame] = []
    for speed in SPEEDS_KMH:
        for threshold in THRESHOLDS_MIN:
            reach_column = f"Reachable within {threshold} min at {speed} km/h"
            frame = (
                analysis.groupby(["Municipality Code", "Municipality"], as_index=False)
                .agg(
                    Residential_Population=("Total Population", "sum"),
                    High_Observed_Use_Stress_Demand=(
                        "Observed-Use Stress Demand High Housing-Loss Weighted",
                        "sum",
                    ),
                )
            )
            reachable = (
                analysis.loc[analysis[reach_column]]
                .groupby(["Municipality Code", "Municipality"], as_index=False)
                .agg(
                    Reachable_Residential_Population=("Total Population", "sum"),
                    Reachable_High_Observed_Use_Stress_Demand=(
                        "Observed-Use Stress Demand High Housing-Loss Weighted",
                        "sum",
                    ),
                )
            )
            frame = frame.merge(
                reachable,
                on=["Municipality Code", "Municipality"],
                how="left",
                validate="1:1",
            ).fillna(
                {
                    "Reachable_Residential_Population": 0,
                    "Reachable_High_Observed_Use_Stress_Demand": 0,
                }
            )
            frame["Walking Speed (km/h)"] = speed
            frame["Time Threshold (min)"] = threshold
            frame["Population Coverage Percent"] = (
                100
                * frame["Reachable_Residential_Population"]
                / frame["Residential_Population"]
            )
            frame["High Stress Demand Coverage Percent"] = (
                100
                * frame["Reachable_High_Observed_Use_Stress_Demand"]
                / frame["High_Observed_Use_Stress_Demand"]
            )
            municipality_rows.append(frame)
    municipality = pd.concat(municipality_rows, ignore_index=True)
    municipality.sort_values(
        ["Walking Speed (km/h)", "Time Threshold (min)", "High Stress Demand Coverage Percent"]
    ).to_csv(OUT / "municipality_walking_access_coverage.csv", index=False)

    primary = summary.loc[
        summary["Walking Speed (km/h)"].eq(4)
        & summary["Time Threshold (min)"].eq(15)
    ]
    (OUT / "README.md").write_text(
        """# Nearest general-shelter walking access

This analysis computes the nearest general shelter on the pedestrian-screened
road graph. National expressways and toll edges are excluded. Door-to-door
distance includes demand-centroid and shelter connectors plus walking along the
network. Results report 10-, 15-, and 30-minute coverage at 3 and 4 km/h.

The output is unconstrained nearest-shelter access. It does not yet impose the
50-person capacity, the 415-opening limit, or facility-unavailability scenarios.
""",
        encoding="utf-8",
    )

    print("Primary 15-minute access at 4 km/h:")
    print(
        primary[["Coverage Measure", "Covered", "Total", "Coverage Percent"]].to_string(
            index=False
        )
    )
    print("\nAll headline walking coverage:")
    print(
        summary.loc[
            summary["Coverage Measure"].isin(
                ["Total Population", "Observed-Use Stress Demand High Housing-Loss Weighted"]
            )
        ].to_string(index=False)
    )
    print(f"\nWrote {processed_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
