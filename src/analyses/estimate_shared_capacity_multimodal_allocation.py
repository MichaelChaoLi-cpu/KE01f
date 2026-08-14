#!/usr/bin/env python3
"""Estimate shared-capacity walking and motorized shelter allocation.

Framework: Section 6 splits each demand unit into walking-only and vehicle-enabled
components. Both components compete for the same standardized shelter capacity and
the same 415-opening budget. Motorized time scales every traversed road edge.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, linprog, milp
from scipy.sparse import coo_array


ROOT = Path(__file__).resolve().parents[2]
EDGES_PATH = ROOT / "data/raw/prior_projects/KE01d/kumamoto_routable_road_edges_preprocessed.parquet"
DEMAND_PATH = ROOT / "data/processed/kumamoto_prefecture_demand_mesh_walking_network_access_preprocessed.parquet"
SHELTER_PATH = ROOT / "data/processed/kumamoto_prefecture_shelter_walking_network_access_preprocessed.parquet"
WALKING_PAIR_PATH = ROOT / "data/exp/primary-capacity-constrained-allocation/primary_reachable_demand_shelter_pairs.parquet"
OUT = ROOT / "data/exp/shared-capacity-multimodal-allocation"

DEMAND_COLUMN = "Observed-Use Stress Demand High Housing-Loss Weighted"
SPEED_FACTOR = 0.50
TIME_THRESHOLD_MIN = 15.0
CONNECTOR_SPEED_KMH = 4.0
OPENING_LIMIT = 415
VEHICLE_SHARES = (0.00, 0.25, 0.50, 0.75, 1.00)
CAPACITIES = (50.0, 100.0)
UNAVAILABILITY_SHARES = (0.10, 0.20, 0.30)
RANDOM_DRAWS = 30
RANDOM_SEED = 20260813
SUPER_SOURCE = "__TEMPORARY_MULTIMODAL_SOURCE__"


def connector_minutes(distance_m: float | pd.Series) -> np.ndarray:
    return 60.0 * np.asarray(distance_m, dtype=float) / (1000.0 * CONNECTOR_SPEED_KMH)


def load_network() -> tuple[pd.DataFrame, nx.Graph]:
    columns = [
        "Road Edge ID",
        "From Node ID",
        "To Node ID",
        "Baseline Edge Travel Time (min)",
        "Road Available",
        "Network Analysis Eligible",
    ]
    edges = pd.read_parquet(EDGES_PATH, columns=columns)
    edges = edges.loc[
        edges["Road Available"].fillna(False)
        & edges["Network Analysis Eligible"].fillna(False)
    ].copy()
    edge_reference = edges.drop_duplicates("Road Edge ID").copy()
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
        (
            str(node_a),
            str(node_b),
            float(edge_time) / SPEED_FACTOR,
        )
        for node_a, node_b, edge_time in graph_edges[
            ["From Node ID", "To Node ID", "Baseline Edge Travel Time (min)"]
        ].itertuples(index=False, name=None)
    )
    return edge_reference, graph


def build_motorized_pairs(
    edge_reference: pd.DataFrame,
    graph: nx.Graph,
    demand: pd.DataFrame,
    shelters: pd.DataFrame,
) -> pd.DataFrame:
    """Enumerate every demand-shelter pair reachable within 15 minutes."""
    lookup = edge_reference.set_index("Road Edge ID")
    demand_by_node: dict[str, list[tuple[int, float]]] = defaultdict(list)
    demand_by_edge: dict[str, list[int]] = defaultdict(list)
    demand_fraction = demand["Walking Access Edge Fraction"].to_numpy(float)
    demand_connector = connector_minutes(demand["Walking Network Snap Distance (m)"])

    for position, row in demand.iterrows():
        if not bool(row["Walking Network Snap Accepted"]):
            continue
        edge_id = str(row["Walking Access Road Edge ID"])
        edge = lookup.loc[edge_id]
        fraction = float(row["Walking Access Edge Fraction"])
        edge_time = float(edge["Baseline Edge Travel Time (min)"]) / SPEED_FACTOR
        demand_by_node[str(edge["From Node ID"])].append(
            (position, demand_connector[position] + fraction * edge_time)
        )
        demand_by_node[str(edge["To Node ID"])].append(
            (position, demand_connector[position] + (1.0 - fraction) * edge_time)
        )
        demand_by_edge[edge_id].append(position)

    rows: list[tuple[int, int, float]] = []
    for shelter_position, row in shelters.iterrows():
        edge_id = str(row["Walking Access Road Edge ID"])
        edge = lookup.loc[edge_id]
        fraction = float(row["Walking Access Edge Fraction"])
        shelter_connector = float(
            connector_minutes(float(row["Walking Network Snap Distance (m)"]))
        )
        edge_time = float(edge["Baseline Edge Travel Time (min)"]) / SPEED_FACTOR
        from_node = str(edge["From Node ID"])
        to_node = str(edge["To Node ID"])
        graph.add_edge(
            SUPER_SOURCE,
            from_node,
            weight=shelter_connector + fraction * edge_time,
        )
        if to_node == from_node:
            graph[SUPER_SOURCE][from_node]["weight"] = min(
                graph[SUPER_SOURCE][from_node]["weight"],
                shelter_connector + (1.0 - fraction) * edge_time,
            )
        else:
            graph.add_edge(
                SUPER_SOURCE,
                to_node,
                weight=shelter_connector + (1.0 - fraction) * edge_time,
            )
        distances = nx.single_source_dijkstra_path_length(
            graph,
            SUPER_SOURCE,
            cutoff=TIME_THRESHOLD_MIN,
            weight="weight",
        )
        graph.remove_node(SUPER_SOURCE)

        best: dict[int, float] = {}
        for node, node_time in distances.items():
            if node == SUPER_SOURCE:
                continue
            for demand_position, endpoint_time in demand_by_node.get(str(node), []):
                total = float(node_time) + endpoint_time
                if total <= TIME_THRESHOLD_MIN + 1e-9 and total < best.get(
                    demand_position, np.inf
                ):
                    best[demand_position] = total

        for demand_position in demand_by_edge.get(edge_id, []):
            direct = (
                shelter_connector
                + demand_connector[demand_position]
                + abs(fraction - demand_fraction[demand_position]) * edge_time
            )
            if direct <= TIME_THRESHOLD_MIN + 1e-9 and direct < best.get(
                demand_position, np.inf
            ):
                best[demand_position] = float(direct)

        rows.extend(
            (demand_position, shelter_position, travel_time)
            for demand_position, travel_time in best.items()
        )
        if (shelter_position + 1) % 100 == 0:
            print(
                f"Motorized pairs: {shelter_position + 1:,}/{len(shelters):,} "
                f"shelters; {len(rows):,} pairs",
                flush=True,
            )

    pairs = pd.DataFrame(
        rows,
        columns=["Demand Position", "Shelter Position", "Motorized Time (min)"],
    )
    pairs = (
        pairs.sort_values("Motorized Time (min)")
        .drop_duplicates(["Demand Position", "Shelter Position"])
        .reset_index(drop=True)
    )
    return pairs


def vehicle_union_pairs(
    walking_pairs: pd.DataFrame, motorized_pairs: pd.DataFrame
) -> pd.DataFrame:
    walking = walking_pairs[
        ["Demand Position", "Shelter Position", "Walking Distance (m)"]
    ].copy()
    walking["Eligible Time (min)"] = walking["Walking Distance (m)"] / (
        1000.0 * CONNECTOR_SPEED_KMH / 60.0
    )
    motorized = motorized_pairs[
        ["Demand Position", "Shelter Position", "Motorized Time (min)"]
    ].copy()
    motorized = motorized.rename(columns={"Motorized Time (min)": "Eligible Time (min)"})
    union = pd.concat(
        [
            walking[["Demand Position", "Shelter Position", "Eligible Time (min)"]],
            motorized,
        ],
        ignore_index=True,
    )
    return (
        union.sort_values("Eligible Time (min)")
        .drop_duplicates(["Demand Position", "Shelter Position"])
        .reset_index(drop=True)
    )


def solve_service(
    walking_pairs: pd.DataFrame,
    vehicle_pairs: pd.DataFrame,
    demand_values: np.ndarray,
    shelter_count: int,
    vehicle_share: float,
    capacity: float,
    available: np.ndarray | None = None,
    opening_limit: int = OPENING_LIMIT,
    time_limit: float = 180.0,
) -> dict[str, object]:
    """Solve a coverage upper bound and a fixed-facility capacitated-flow lower bound.

    Equality of the two bounds proves global optimality for maximum assigned demand.
    This decomposition is equivalent to the first lexicographic stage when the bounds
    close and is substantially more stable than the unaggregated mixed-integer flow.
    """
    if available is None:
        available = np.ones(shelter_count, dtype=bool)
    n_demand = len(demand_values)
    components: list[tuple[pd.DataFrame, np.ndarray]] = []
    if vehicle_share < 1.0:
        components.append((walking_pairs, (1.0 - vehicle_share) * demand_values))
    if vehicle_share > 0.0:
        components.append((vehicle_pairs, vehicle_share * demand_values))

    component_specs: list[tuple[pd.DataFrame, np.ndarray, np.ndarray]] = []
    component_count = 0
    for pairs, component_demand in components:
        active = np.unique(pairs["Demand Position"].to_numpy(np.int64))
        position_map = np.full(n_demand, -1, dtype=np.int64)
        position_map[active] = np.arange(len(active), dtype=np.int64)
        component_specs.append((pairs, active, component_demand[active]))
        component_count += len(active)

    # Coverage-selection relaxation: a component may be served when at least one
    # selected shelter is reachable. Aggregate capacity is retained, while the
    # facility-level capacity distribution is relaxed, so this is a strict upper bound.
    coverage_rows: list[np.ndarray] = []
    coverage_columns: list[np.ndarray] = []
    coverage_values: list[np.ndarray] = []
    component_weights: list[np.ndarray] = []
    offset = 0
    for pairs, active, weights in component_specs:
        position_map = np.full(n_demand, -1, dtype=np.int64)
        position_map[active] = np.arange(len(active), dtype=np.int64)
        pair_demand = pairs["Demand Position"].to_numpy(np.int64)
        pair_shelter = pairs["Shelter Position"].to_numpy(np.int64)
        component_rows = offset + position_map[pair_demand]
        component_columns = np.arange(offset, offset + len(active), dtype=np.int64)
        coverage_rows.extend([component_columns, component_rows])
        coverage_columns.extend(
            [component_columns, component_count + pair_shelter]
        )
        coverage_values.extend(
            [np.ones(len(active)), -np.ones(len(pairs))]
        )
        component_weights.append(weights)
        offset += len(active)

    weights_all = np.concatenate(component_weights)
    capacity_row = component_count
    opening_row = component_count + 1
    coverage_rows.extend(
        [
            np.full(component_count, capacity_row, dtype=np.int64),
            np.full(shelter_count, capacity_row, dtype=np.int64),
            np.full(shelter_count, opening_row, dtype=np.int64),
        ]
    )
    coverage_columns.extend(
        [
            np.arange(component_count, dtype=np.int64),
            component_count + np.arange(shelter_count, dtype=np.int64),
            component_count + np.arange(shelter_count, dtype=np.int64),
        ]
    )
    coverage_values.extend(
        [weights_all, np.full(shelter_count, -capacity), np.ones(shelter_count)]
    )
    coverage_matrix = coo_array(
        (
            np.concatenate(coverage_values),
            (np.concatenate(coverage_rows), np.concatenate(coverage_columns)),
        ),
        shape=(component_count + 2, component_count + shelter_count),
    ).tocsc()
    coverage_upper = np.concatenate(
        [
            np.zeros(component_count + 1),
            np.array([min(opening_limit, int(available.sum()))], dtype=float),
        ]
    )
    coverage = milp(
        np.concatenate([-weights_all, np.zeros(shelter_count)]),
        integrality=np.concatenate(
            [
                np.zeros(component_count, dtype=np.int8),
                np.ones(shelter_count, dtype=np.int8),
            ]
        ),
        bounds=Bounds(
            np.zeros(component_count + shelter_count),
            np.concatenate([np.ones(component_count), available.astype(float)]),
        ),
        constraints=LinearConstraint(
            coverage_matrix,
            np.full(coverage_matrix.shape[0], -np.inf),
            coverage_upper,
        ),
        options={"time_limit": time_limit, "mip_rel_gap": 1e-5, "presolve": True},
    )
    if coverage.x is None:
        raise RuntimeError(f"Coverage-selection model failed: {coverage.message}")
    selected = np.flatnonzero(coverage.x[component_count:] >= 0.5)
    selected_mask = np.zeros(shelter_count, dtype=bool)
    selected_mask[selected] = True
    coverage_upper_bound = float(-coverage.fun)
    coverage_dual = getattr(coverage, "mip_dual_bound", None)
    if coverage.status != 0 and coverage_dual is not None:
        coverage_upper_bound = max(coverage_upper_bound, -float(coverage_dual))

    # Exact continuous maximum flow for the selected facilities.
    filtered_components: list[tuple[pd.DataFrame, np.ndarray]] = []
    for pairs, component_demand in components:
        filtered_components.append(
            (pairs.loc[pairs["Shelter Position"].isin(selected)].copy(), component_demand)
        )
    flow_count = sum(len(pairs) for pairs, _ in filtered_components)
    flow_rows: list[np.ndarray] = []
    flow_columns: list[np.ndarray] = []
    flow_values: list[np.ndarray] = []
    flow_upper: list[np.ndarray] = []
    flow_offset = 0
    demand_offset = 0
    for pairs, component_demand in filtered_components:
        pair_count = len(pairs)
        columns = flow_offset + np.arange(pair_count, dtype=np.int64)
        flow_rows.extend(
            [
                demand_offset + pairs["Demand Position"].to_numpy(np.int64),
                len(components) * n_demand
                + pairs["Shelter Position"].to_numpy(np.int64),
            ]
        )
        flow_columns.extend([columns, columns])
        flow_values.extend([np.ones(pair_count), np.ones(pair_count)])
        flow_upper.append(component_demand)
        flow_offset += pair_count
        demand_offset += n_demand
    flow_matrix = coo_array(
        (
            np.concatenate(flow_values),
            (np.concatenate(flow_rows), np.concatenate(flow_columns)),
        ),
        shape=(len(components) * n_demand + shelter_count, flow_count),
    ).tocsc()
    flow_result = linprog(
        -np.ones(flow_count),
        A_ub=flow_matrix,
        b_ub=np.concatenate(
            [*flow_upper, np.where(selected_mask, capacity, 0.0)]
        ),
        bounds=(0, None),
        method="highs",
        options={"time_limit": time_limit},
    )
    if flow_result.x is None:
        raise RuntimeError(f"Fixed-facility maximum flow failed: {flow_result.message}")
    served = float(-flow_result.fun)
    absolute_gap = max(0.0, coverage_upper_bound - served)
    relative_gap = absolute_gap / coverage_upper_bound if coverage_upper_bound else 0.0
    proven_optimal = bool(absolute_gap <= 1e-5)
    return {
        "Vehicle-Enabled Demand Share": vehicle_share,
        "Capacity per Open Shelter": capacity,
        "Opening Limit": opening_limit,
        "Available Shelters": int(available.sum()),
        "Maximum Served Demand": served,
        "Served Percent": 100.0 * served / float(demand_values.sum()),
        "Model Explanation Gap": float(demand_values.sum() - served),
        "Modeled Open Shelters": int(len(selected)),
        "Status": 0 if proven_optimal else 1,
        "Message": "Coverage upper bound equals fixed-facility maximum flow" if proven_optimal else "Reported service is a lower bound below the coverage relaxation",
        "Proven Optimal": proven_optimal,
        "MIP Gap": relative_gap,
        "MIP Dual Bound Served Demand": coverage_upper_bound,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    edge_reference, graph = load_network()
    demand = pd.read_parquet(DEMAND_PATH).reset_index(drop=True)
    shelters = pd.read_parquet(SHELTER_PATH)
    shelters = shelters.loc[
        shelters["Shelter Service Class"].eq("general")
        & shelters["Walking Network Snap Accepted"].fillna(False)
    ].reset_index(drop=True)
    walking_pairs = pd.read_parquet(WALKING_PAIR_PATH).reset_index(drop=True)
    motor_path = OUT / "motorized_pairs_15min_0_50x.parquet"
    if motor_path.exists():
        motorized_pairs = pd.read_parquet(motor_path)
    else:
        motorized_pairs = build_motorized_pairs(
            edge_reference, graph, demand, shelters
        )
        motorized_pairs.to_parquet(motor_path, index=False)
    vehicle_pairs = vehicle_union_pairs(walking_pairs, motorized_pairs)
    vehicle_path = OUT / "vehicle_flexible_pairs_15min_0_50x.parquet"
    vehicle_pairs.to_parquet(vehicle_path, index=False)
    print(
        f"Pair sets: walking={len(walking_pairs):,}; motorized={len(motorized_pairs):,}; "
        f"vehicle-flexible={len(vehicle_pairs):,}",
        flush=True,
    )

    demand_values = demand[DEMAND_COLUMN].to_numpy(float)
    scenario_rows: list[dict[str, object]] = []
    for capacity in CAPACITIES:
        for share in VEHICLE_SHARES:
            row = solve_service(
                walking_pairs,
                vehicle_pairs,
                demand_values,
                len(shelters),
                share,
                capacity,
            )
            scenario_rows.append(row)
            pd.DataFrame(scenario_rows).to_csv(
                OUT / "shared_capacity_mode_and_capacity_sensitivity.csv", index=False
            )
            print(
                f"capacity={capacity:.0f}; vehicle share={share:.0%}; "
                f"served={row['Served Percent']:.3f}%; status={row['Status']}; "
                f"gap={row['MIP Gap']}",
                flush=True,
            )

    central_share = 0.50
    central_capacity = 100.0
    vehicle_pressure = (
        vehicle_pairs.assign(
            Reachable_Demand=demand_values[
                vehicle_pairs["Demand Position"].to_numpy(np.int64)
            ]
        )
        .groupby("Shelter Position")["Reachable_Demand"]
        .sum()
        .reindex(np.arange(len(shelters)), fill_value=0.0)
        .to_numpy(float)
    )
    walking_pressure = (
        walking_pairs.assign(
            Reachable_Demand=demand_values[
                walking_pairs["Demand Position"].to_numpy(np.int64)
            ]
        )
        .groupby("Shelter Position")["Reachable_Demand"]
        .sum()
        .reindex(np.arange(len(shelters)), fill_value=0.0)
        .to_numpy(float)
    )
    mixed_pressure = (
        (1.0 - central_share) * walking_pressure
        + central_share * vehicle_pressure
    )
    targeted_order = np.argsort(-mixed_pressure, kind="stable")
    rng = np.random.default_rng(RANDOM_SEED)
    failure_rows: list[dict[str, object]] = []
    baseline = next(
        row
        for row in scenario_rows
        if row["Capacity per Open Shelter"] == central_capacity
        and row["Vehicle-Enabled Demand Share"] == central_share
    )
    failure_rows.append(
        {**baseline, "Failure Mode": "baseline", "Unavailability Share": 0.0, "Draw": 0}
    )
    for removal_share in UNAVAILABILITY_SHARES:
        removal_count = int(np.rint(removal_share * len(shelters)))
        specifications = [
            ("targeted_mixed_reachable_pressure", 0, targeted_order[:removal_count])
        ]
        specifications.extend(
            (
                "random",
                draw,
                np.sort(
                    rng.choice(len(shelters), size=removal_count, replace=False)
                ),
            )
            for draw in range(1, RANDOM_DRAWS + 1)
        )
        for failure_mode, draw, removed in specifications:
            available = np.ones(len(shelters), dtype=bool)
            available[removed] = False
            row = solve_service(
                walking_pairs,
                vehicle_pairs,
                demand_values,
                len(shelters),
                central_share,
                central_capacity,
                available=available,
                time_limit=180.0,
            )
            row.update(
                {
                    "Failure Mode": failure_mode,
                    "Unavailability Share": removal_share,
                    "Draw": draw,
                    "Service Loss from Baseline": baseline["Maximum Served Demand"]
                    - row["Maximum Served Demand"],
                }
            )
            failure_rows.append(row)
            pd.DataFrame(failure_rows).to_csv(
                OUT / "matched_multimodal_facility_unavailability.csv", index=False
            )
            print(
                f"{failure_mode}; removed={removal_share:.0%}; draw={draw}; "
                f"served={row['Served Percent']:.3f}%",
                flush=True,
            )

    random_summary = (
        pd.DataFrame(failure_rows)
        .loc[lambda frame: frame["Failure Mode"].eq("random")]
        .groupby("Unavailability Share", as_index=False)
        .agg(
            Draws=("Draw", "count"),
            Mean_Served_Percent=("Served Percent", "mean"),
            Minimum_Served_Percent=("Served Percent", "min"),
            Maximum_Served_Percent=("Served Percent", "max"),
            Maximum_MIP_Gap=("MIP Gap", "max"),
        )
    )
    random_summary.to_csv(
        OUT / "matched_multimodal_facility_unavailability_random_summary.csv",
        index=False,
    )
    all_open = solve_service(
        walking_pairs,
        vehicle_pairs,
        demand_values,
        len(shelters),
        central_share,
        central_capacity,
        opening_limit=len(shelters),
        time_limit=300.0,
    )
    pd.DataFrame(
        [
            {**baseline, "Opening Scenario": "At most 415 openings"},
            {**all_open, "Opening Scenario": "All 1,156 shelters selectable"},
        ]
    ).to_csv(
        OUT / "matched_multimodal_opening_scale_sensitivity.csv",
        index=False,
    )
    print("Saved shared-capacity multimodal results.")


if __name__ == "__main__":
    main()
