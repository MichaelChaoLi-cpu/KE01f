"""Estimate walking, motorized, and mixed-mode shelter-accessibility bounds.

Motorized times use the existing road-class baseline edge travel times. Scenario
speed factors scale those edge times, while off-network demand and shelter
connectors are traversed at 4 km/h. The mixed-mode calculation varies the share
of demand that can use the union of walking and motorized catchments; it does
not estimate observed evacuation-mode choice.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
EDGES_PATH = (
    ROOT
    / "data/raw/prior_projects/KE01d/kumamoto_routable_road_edges_preprocessed.parquet"
)
DEMAND_PATH = (
    ROOT
    / "data/processed/kumamoto_prefecture_demand_mesh_walking_network_access_preprocessed.parquet"
)
SHELTER_PATH = (
    ROOT
    / "data/processed/kumamoto_prefecture_shelter_walking_network_access_preprocessed.parquet"
)
WALKING_ACCESS_PATH = (
    ROOT
    / "data/processed/kumamoto_prefecture_nearest_shelter_walking_access_preprocessed.parquet"
)
PROCESSED_OUTPUT = (
    ROOT
    / "data/processed/kumamoto_prefecture_nearest_shelter_motorized_access_preprocessed.parquet"
)
OUT = ROOT / "data/exp/prefecture-shelter-multimodal-access"

SPEED_FACTORS = (0.25, 0.50, 1.00)
TIME_THRESHOLDS_MIN = (10, 15, 30)
VEHICLE_ENABLED_SHARES = (0.00, 0.25, 0.50, 0.75, 1.00)
CENTRAL_SPEED_FACTOR = 0.50
CENTRAL_THRESHOLD_MIN = 15
CONNECTOR_SPEED_KMH = 4.0
SUPER_SOURCE = "__TEMPORARY_MOTORIZED_SHELTER_SOURCE__"

DEMAND_COLUMNS = (
    "Residential Population",
    "Housing-Loss Shelter Demand High",
    "Observed-Use Stress Demand Population Weighted",
    "Observed-Use Stress Demand Central Housing-Loss Weighted",
    "Observed-Use Stress Demand High Housing-Loss Weighted",
)
PRIMARY_DEMAND_COLUMN = (
    "Observed-Use Stress Demand High Housing-Loss Weighted"
)


def load_edges() -> tuple[pd.DataFrame, nx.Graph]:
    columns = [
        "Road Edge ID",
        "From Node ID",
        "To Node ID",
        "Baseline Edge Travel Time (min)",
        "Road Available",
        "Network Analysis Eligible",
    ]
    edges = pd.read_parquet(EDGES_PATH, columns=columns)
    keep = (
        edges["Road Available"].fillna(False)
        & edges["Network Analysis Eligible"].fillna(False)
    )
    edges = edges.loc[keep].copy()
    edges["Node A"] = np.minimum(
        edges["From Node ID"].astype(str), edges["To Node ID"].astype(str)
    )
    edges["Node B"] = np.maximum(
        edges["From Node ID"].astype(str), edges["To Node ID"].astype(str)
    )
    graph_edges = (
        edges.sort_values("Baseline Edge Travel Time (min)")
        .drop_duplicates(["Node A", "Node B"])
    )
    graph = nx.Graph()
    graph.add_weighted_edges_from(
        graph_edges[
            ["From Node ID", "To Node ID", "Baseline Edge Travel Time (min)"]
        ].itertuples(index=False, name=None)
    )
    return edges.drop_duplicates("Road Edge ID"), graph


def connector_minutes(distance_m: np.ndarray | pd.Series) -> np.ndarray:
    return 60.0 * np.asarray(distance_m, dtype=float) / (1000.0 * CONNECTOR_SPEED_KMH)


def shelter_source_costs(
    edge_reference: pd.DataFrame,
    shelters: pd.DataFrame,
    speed_factor: float,
) -> tuple[dict[str, float], dict[str, tuple[np.ndarray, np.ndarray]]]:
    joined = shelters.merge(
        edge_reference[
            [
                "Road Edge ID",
                "From Node ID",
                "To Node ID",
                "Baseline Edge Travel Time (min)",
            ]
        ],
        left_on="Walking Access Road Edge ID",
        right_on="Road Edge ID",
        how="left",
        validate="many_to_one",
    )
    if joined["Road Edge ID"].isna().any():
        raise RuntimeError("Every shelter access edge must exist in the motorized graph")

    source_cost: dict[str, float] = {}
    same_edge: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    connector = connector_minutes(joined["Walking Network Snap Distance (m)"])
    edge_time = joined["Baseline Edge Travel Time (min)"].to_numpy(float) / speed_factor
    fraction = joined["Walking Access Edge Fraction"].to_numpy(float)

    from_nodes = joined["From Node ID"].astype(str).to_numpy()
    to_nodes = joined["To Node ID"].astype(str).to_numpy()
    for position, (from_node, to_node) in enumerate(zip(from_nodes, to_nodes)):
        from_cost = connector[position] + fraction[position] * edge_time[position]
        to_cost = connector[position] + (1.0 - fraction[position]) * edge_time[position]
        source_cost[from_node] = min(source_cost.get(from_node, np.inf), from_cost)
        source_cost[to_node] = min(source_cost.get(to_node, np.inf), to_cost)

    for edge_id, frame in joined.groupby("Walking Access Road Edge ID"):
        same_edge[str(edge_id)] = (
            frame["Walking Access Edge Fraction"].to_numpy(float),
            connector_minutes(frame["Walking Network Snap Distance (m)"]),
        )
    return source_cost, same_edge


def nearest_motorized_time(
    edges: pd.DataFrame,
    graph: nx.Graph,
    demand: pd.DataFrame,
    shelters: pd.DataFrame,
    speed_factor: float,
) -> np.ndarray:
    edge_reference = edges.set_index("Road Edge ID", drop=False)
    source_cost, same_edge_shelters = shelter_source_costs(
        edges, shelters, speed_factor
    )
    for node, cost in source_cost.items():
        graph.add_edge(SUPER_SOURCE, node, weight=float(cost))
    distances = nx.single_source_dijkstra_path_length(
        graph, SUPER_SOURCE, weight="weight"
    )
    graph.remove_node(SUPER_SOURCE)

    output = np.full(len(demand), np.inf, dtype=float)
    connector = connector_minutes(demand["Walking Network Snap Distance (m)"])
    accepted = demand["Walking Network Snap Accepted"].fillna(False).to_numpy(bool)
    edge_ids = demand["Walking Access Road Edge ID"].astype(str).to_numpy()
    fractions = demand["Walking Access Edge Fraction"].to_numpy(float)
    for position, (is_accepted, edge_id, fraction) in enumerate(
        zip(accepted, edge_ids, fractions)
    ):
        if not is_accepted:
            continue
        edge = edge_reference.loc[edge_id]
        edge_time = float(edge["Baseline Edge Travel Time (min)"]) / speed_factor
        endpoint = connector[position] + min(
            distances.get(str(edge["From Node ID"]), np.inf) + fraction * edge_time,
            distances.get(str(edge["To Node ID"]), np.inf)
            + (1.0 - fraction) * edge_time,
        )
        best = endpoint
        same_edge = same_edge_shelters.get(edge_id)
        if same_edge is not None:
            shelter_fraction, shelter_connector = same_edge
            direct = connector[position] + np.min(
                shelter_connector + np.abs(fraction - shelter_fraction) * edge_time
            )
            best = min(best, float(direct))
        output[position] = best
    return output


def weighted_percent(values: pd.Series, reachable: np.ndarray) -> float:
    weights = values.to_numpy(float)
    return 100.0 * float(weights[reachable].sum()) / float(weights.sum())


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    PROCESSED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    edges, graph = load_edges()
    demand = pd.read_parquet(DEMAND_PATH).reset_index(drop=True)
    shelters = pd.read_parquet(SHELTER_PATH)
    shelters = shelters.loc[
        shelters["Shelter Service Class"].eq("general")
        & shelters["Walking Network Snap Accepted"].fillna(False)
    ].reset_index(drop=True)
    walking = pd.read_parquet(WALKING_ACCESS_PATH)
    if not demand["Mesh Code"].astype(str).equals(walking["Mesh Code"].astype(str)):
        raise RuntimeError("Walking and motorized demand rows are not aligned")

    result = demand[
        [
            "Mesh Code",
            "Municipality Code",
            "Municipality",
            *DEMAND_COLUMNS,
            "Mesh Geometry",
        ]
    ].copy()
    summary_rows: list[dict[str, object]] = []

    walking_reachable = (
        walking["Reachable within 15 min at 4 km/h"].fillna(False).to_numpy(bool)
    )
    for demand_column in DEMAND_COLUMNS:
        summary_rows.append(
            {
                "Mode": "Walking",
                "Road Speed Factor": np.nan,
                "Time Threshold (min)": CENTRAL_THRESHOLD_MIN,
                "Demand Measure": demand_column,
                "Accessible Demand": float(
                    demand.loc[walking_reachable, demand_column].sum()
                ),
                "Total Demand": float(demand[demand_column].sum()),
                "Accessible Percent": weighted_percent(
                    demand[demand_column], walking_reachable
                ),
            }
        )

    for speed_factor in SPEED_FACTORS:
        times = nearest_motorized_time(
            edges, graph, demand, shelters, speed_factor
        )
        time_column = f"Nearest General Shelter Motorized Time at {speed_factor:.2f}x (min)"
        result[time_column] = np.where(np.isfinite(times), times, np.nan)
        for threshold in TIME_THRESHOLDS_MIN:
            reachable = times <= threshold
            result[
                f"Reachable within {threshold} min at {speed_factor:.2f}x Motorized Speed"
            ] = reachable
            for demand_column in DEMAND_COLUMNS:
                summary_rows.append(
                    {
                        "Mode": "Motorized",
                        "Road Speed Factor": speed_factor,
                        "Time Threshold (min)": threshold,
                        "Demand Measure": demand_column,
                        "Accessible Demand": float(
                            demand.loc[reachable, demand_column].sum()
                        ),
                        "Total Demand": float(demand[demand_column].sum()),
                        "Accessible Percent": weighted_percent(
                            demand[demand_column], reachable
                        ),
                    }
                )

    central_motor = result[
        "Reachable within 15 min at 0.50x Motorized Speed"
    ].to_numpy(bool)
    mode_flexible = walking_reachable | central_motor
    result["Walking Reachable in Central Comparison"] = walking_reachable
    result["Motorized Reachable in Central Comparison"] = central_motor
    result["Mode-Flexible Reachable in Central Comparison"] = mode_flexible
    result.to_parquet(PROCESSED_OUTPUT, index=False)

    pd.DataFrame(summary_rows).to_csv(
        OUT / "walking_and_motorized_accessibility_summary.csv", index=False
    )

    mixed_rows: list[dict[str, object]] = []
    primary = demand[PRIMARY_DEMAND_COLUMN].to_numpy(float)
    for share in VEHICLE_ENABLED_SHARES:
        accessible = primary * (
            (1.0 - share) * walking_reachable.astype(float)
            + share * mode_flexible.astype(float)
        )
        mixed_rows.append(
            {
                "Vehicle-Enabled Demand Share": share,
                "Walking Speed (km/h)": CONNECTOR_SPEED_KMH,
                "Motorized Road Speed Factor": CENTRAL_SPEED_FACTOR,
                "Time Threshold (min)": CENTRAL_THRESHOLD_MIN,
                "Accessible Demand": float(accessible.sum()),
                "Total Stress Load": float(primary.sum()),
                "Accessible Percent": 100.0 * float(accessible.sum()) / float(primary.sum()),
                "Explanation Gap": float(primary.sum() - accessible.sum()),
                "Explanation Gap Percent": 100.0
                * float(primary.sum() - accessible.sum())
                / float(primary.sum()),
            }
        )
    mixed = pd.DataFrame(mixed_rows)
    mixed.to_csv(OUT / "mixed_mode_accessibility_summary.csv", index=False)

    municipality_rows: list[pd.DataFrame] = []
    for share in VEHICLE_ENABLED_SHARES:
        frame = demand[["Municipality Code", "Municipality"]].copy()
        frame["Stress Load"] = primary
        frame["Accessible Demand"] = primary * (
            (1.0 - share) * walking_reachable.astype(float)
            + share * mode_flexible.astype(float)
        )
        grouped = frame.groupby(
            ["Municipality Code", "Municipality"], as_index=False
        ).sum(numeric_only=True)
        grouped["Vehicle-Enabled Demand Share"] = share
        grouped["Accessible Percent"] = (
            100.0 * grouped["Accessible Demand"] / grouped["Stress Load"]
        )
        municipality_rows.append(grouped)
    municipality = pd.concat(municipality_rows, ignore_index=True)
    municipality.to_csv(OUT / "municipality_mixed_mode_accessibility.csv", index=False)

    readme = OUT / "README.md"
    readme.write_text(
        "# Multimodal shelter-accessibility sensitivity\n\n"
        "Motorized road times use the existing road-class baseline edge travel times "
        "multiplied by 0.25, 0.50, or 1.00 speed factors. Off-network connectors are "
        "walked at 4 km/h. The central comparison uses 0.50 of baseline road speed and "
        "a 15-minute threshold. Vehicle-enabled demand shares from 0 to 1 are scenario "
        "bounds, not observed travel-mode estimates. Vehicle-enabled demand may use the "
        "union of walking and motorized catchments.\n",
        encoding="utf-8",
    )
    print(mixed.to_string(index=False))
    central_summary = pd.DataFrame(summary_rows)
    print(
        "\nCentral walking and motorized accessibility\n",
        central_summary.loc[
            central_summary["Demand Measure"].eq(PRIMARY_DEMAND_COLUMN)
            & central_summary["Time Threshold (min)"].eq(CENTRAL_THRESHOLD_MIN)
            & (
                central_summary["Mode"].eq("Walking")
                | central_summary["Road Speed Factor"].eq(CENTRAL_SPEED_FACTOR)
            )
        ].to_string(index=False),
    )


if __name__ == "__main__":
    main()
