"""Solve the primary 50-person, 415-opening shelter allocation scenario.

The primary demand is the 10,467-person high-housing-loss-weighted stress
spatialization. Reachability is limited to 1,000 m door-to-door walking distance,
equivalent to 15 minutes at 4 km/h on the pedestrian-screened graph.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_array, vstack


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
OUT = ROOT / "data" / "exp" / "primary-capacity-constrained-allocation"
PROCESSED = ROOT / "data" / "processed"

DEMAND_COLUMN = "Observed-Use Stress Demand High Housing-Loss Weighted"
CAPACITY_PER_SHELTER = 50.0
MAXIMUM_OPEN_SHELTERS = 415
MAXIMUM_WALKING_DISTANCE_M = 1000.0
EXPRESSWAY_CATEGORY = "National Expressway or Equivalent"
FREE_TOLL_CATEGORY = "Free"
SUPER_SOURCE = "__TEMPORARY_SHELTER_SOURCE__"
SOLVER_TOLERANCE = 1e-6


def load_walking_edges() -> tuple[pd.DataFrame, nx.Graph]:
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
    graph_edges = edges.sort_values("Road Length (m)").drop_duplicates(["Node A", "Node B"])
    graph = nx.Graph()
    graph.add_weighted_edges_from(
        graph_edges[["From Node ID", "To Node ID", "Road Length (m)"]].itertuples(
            index=False, name=None
        )
    )
    return edges, graph


def build_reachable_pairs(
    graph: nx.Graph,
    edge_lookup: pd.DataFrame,
    demand: pd.DataFrame,
    shelters: pd.DataFrame,
    maximum_distance_m: float = MAXIMUM_WALKING_DISTANCE_M,
) -> pd.DataFrame:
    """Enumerate demand-shelter pairs within the primary walking threshold."""
    edge_reference = edge_lookup.set_index("Road Edge ID")
    demand_by_node: dict[str, list[tuple[int, float]]] = defaultdict(list)
    demand_by_edge: dict[str, list[int]] = defaultdict(list)
    for position, (_, values) in enumerate(demand.iterrows()):
        if not bool(values["Walking Network Snap Accepted"]):
            continue
        edge_id = str(values["Walking Access Road Edge ID"])
        edge = edge_reference.loc[edge_id]
        fraction = float(values["Walking Access Edge Fraction"])
        snap = float(values["Walking Network Snap Distance (m)"])
        length = float(edge["Road Length (m)"])
        demand_by_node[str(edge["From Node ID"])].append(
            (position, snap + fraction * length)
        )
        demand_by_node[str(edge["To Node ID"])].append(
            (position, snap + (1 - fraction) * length)
        )
        demand_by_edge[edge_id].append(position)

    demand_fraction = demand["Walking Access Edge Fraction"].astype(float).to_numpy()
    demand_snap = demand["Walking Network Snap Distance (m)"].to_numpy(float)
    pair_rows: list[tuple[int, int, float]] = []

    for shelter_position, (_, values) in enumerate(shelters.iterrows()):
        edge_id = str(values["Walking Access Road Edge ID"])
        edge = edge_reference.loc[edge_id]
        fraction = float(values["Walking Access Edge Fraction"])
        snap = float(values["Walking Network Snap Distance (m)"])
        length = float(edge["Road Length (m)"])
        from_node = str(edge["From Node ID"])
        to_node = str(edge["To Node ID"])
        from_cost = snap + fraction * length
        to_cost = snap + (1 - fraction) * length

        graph.add_edge(SUPER_SOURCE, from_node, weight=from_cost)
        if to_node == from_node:
            graph[SUPER_SOURCE][from_node]["weight"] = min(from_cost, to_cost)
        else:
            graph.add_edge(SUPER_SOURCE, to_node, weight=to_cost)
        distances = nx.single_source_dijkstra_path_length(
            graph,
            SUPER_SOURCE,
            cutoff=maximum_distance_m,
            weight="weight",
        )
        graph.remove_node(SUPER_SOURCE)

        best: dict[int, float] = {}
        for node, node_distance in distances.items():
            if node == SUPER_SOURCE:
                continue
            for demand_position, endpoint_cost in demand_by_node.get(str(node), []):
                total = float(node_distance) + endpoint_cost
                if total <= maximum_distance_m + 1e-9:
                    previous = best.get(demand_position)
                    if previous is None or total < previous:
                        best[demand_position] = total

        # The endpoint formulation can overstate distance when both attachments
        # lie on the same edge, so add the direct along-edge alternative.
        for demand_position in demand_by_edge.get(edge_id, []):
            total = (
                snap
                + demand_snap[demand_position]
                + abs(fraction - demand_fraction[demand_position]) * length
            )
            if total <= maximum_distance_m + 1e-9:
                previous = best.get(demand_position)
                if previous is None or total < previous:
                    best[demand_position] = float(total)

        pair_rows.extend(
            (demand_position, shelter_position, distance)
            for demand_position, distance in best.items()
        )
        if (shelter_position + 1) % 100 == 0:
            print(
                f"Reachability: {shelter_position + 1:,}/{len(shelters):,} shelters; "
                f"{len(pair_rows):,} pairs"
            )

    pairs = pd.DataFrame(
        pair_rows,
        columns=["Demand Position", "Shelter Position", "Walking Distance (m)"],
    )
    if pairs.duplicated(["Demand Position", "Shelter Position"]).any():
        pairs = (
            pairs.sort_values("Walking Distance (m)")
            .drop_duplicates(["Demand Position", "Shelter Position"])
            .reset_index(drop=True)
        )
    return pairs


def base_constraints(
    pairs: pd.DataFrame, demand_values: np.ndarray, shelter_count: int
) -> tuple[coo_array, np.ndarray, np.ndarray]:
    pair_count = len(pairs)
    demand_count = len(demand_values)
    variable_count = pair_count + shelter_count

    pair_index = np.arange(pair_count, dtype=np.int64)
    demand_index = pairs["Demand Position"].to_numpy(np.int64)
    shelter_index = pairs["Shelter Position"].to_numpy(np.int64)

    rows = np.concatenate(
        [
            demand_index,
            demand_count + shelter_index,
            demand_count + np.arange(shelter_count, dtype=np.int64),
            np.full(shelter_count, demand_count + shelter_count, dtype=np.int64),
        ]
    )
    cols = np.concatenate(
        [
            pair_index,
            pair_index,
            pair_count + np.arange(shelter_count, dtype=np.int64),
            pair_count + np.arange(shelter_count, dtype=np.int64),
        ]
    )
    values = np.concatenate(
        [
            np.ones(pair_count),
            np.ones(pair_count),
            np.full(shelter_count, -CAPACITY_PER_SHELTER),
            np.ones(shelter_count),
        ]
    )
    matrix = coo_array(
        (values, (rows, cols)),
        shape=(demand_count + shelter_count + 1, variable_count),
    ).tocsc()
    lower = np.full(matrix.shape[0], -np.inf)
    upper = np.concatenate(
        [
            demand_values,
            np.zeros(shelter_count),
            np.array([MAXIMUM_OPEN_SHELTERS], dtype=float),
        ]
    )
    return matrix, lower, upper


def solve_lexicographic(
    pairs: pd.DataFrame, demand_values: np.ndarray, shelter_count: int
) -> tuple[np.ndarray, dict[str, object]]:
    pair_count = len(pairs)
    variable_count = pair_count + shelter_count
    matrix, lower, upper = base_constraints(pairs, demand_values, shelter_count)
    bounds = Bounds(
        np.zeros(variable_count),
        np.concatenate([np.full(pair_count, np.inf), np.ones(shelter_count)]),
    )
    integrality = np.concatenate(
        [np.zeros(pair_count, dtype=np.int8), np.ones(shelter_count, dtype=np.int8)]
    )
    options = {"time_limit": 180.0, "mip_rel_gap": 1e-7, "presolve": True}

    objective_service = np.concatenate([-np.ones(pair_count), np.zeros(shelter_count)])
    stage1 = milp(
        objective_service,
        integrality=integrality,
        bounds=bounds,
        constraints=LinearConstraint(matrix, lower, upper),
        options=options,
    )
    if stage1.x is None:
        raise RuntimeError(f"Stage 1 failed: {stage1.message}")
    served_target = float(stage1.x[:pair_count].sum())
    print(f"Stage 1 served demand: {served_target:,.6f}; {stage1.message}")

    service_row = coo_array(
        (
            -np.ones(pair_count),
            (np.zeros(pair_count, dtype=np.int64), np.arange(pair_count, dtype=np.int64)),
        ),
        shape=(1, variable_count),
    ).tocsc()
    matrix2 = vstack([matrix, service_row], format="csc")
    lower2 = np.concatenate([lower, [-np.inf]])
    upper2 = np.concatenate([upper, [-(served_target - SOLVER_TOLERANCE)]])
    objective_open = np.concatenate([np.zeros(pair_count), np.ones(shelter_count)])
    stage2 = milp(
        objective_open,
        integrality=integrality,
        bounds=bounds,
        constraints=LinearConstraint(matrix2, lower2, upper2),
        options=options,
    )
    if stage2.x is None:
        raise RuntimeError(f"Stage 2 failed: {stage2.message}")
    open_target = int(np.rint(stage2.x[pair_count:].sum()))
    print(f"Stage 2 open shelters: {open_target:,}; {stage2.message}")

    open_row = coo_array(
        (
            np.ones(shelter_count),
            (
                np.zeros(shelter_count, dtype=np.int64),
                pair_count + np.arange(shelter_count, dtype=np.int64),
            ),
        ),
        shape=(1, variable_count),
    ).tocsc()
    matrix3 = vstack([matrix2, open_row], format="csc")
    lower3 = np.concatenate([lower2, [-np.inf]])
    upper3 = np.concatenate([upper2, [open_target]])
    objective_walk = np.concatenate(
        [pairs["Walking Distance (m)"].to_numpy(float), np.zeros(shelter_count)]
    )
    stage3_options = {"time_limit": 60.0, "mip_rel_gap": 1e-7, "presolve": True}
    stage3 = milp(
        objective_walk,
        integrality=integrality,
        bounds=bounds,
        constraints=LinearConstraint(matrix3, lower3, upper3),
        options=stage3_options,
    )
    conditional = None
    if stage3.x is None:
        fixed_open = np.rint(stage2.x[pair_count:])
        conditional_bounds = Bounds(
            np.concatenate([np.zeros(pair_count), fixed_open]),
            np.concatenate([np.full(pair_count, np.inf), fixed_open]),
        )
        conditional = milp(
            objective_walk,
            integrality=np.zeros(variable_count, dtype=np.int8),
            bounds=conditional_bounds,
            constraints=LinearConstraint(matrix3, lower3, upper3),
            options={"time_limit": 180.0, "presolve": True},
        )

    if stage3.x is not None:
        final = stage3
        final_source = "stage_3_global_distance_solution"
    elif conditional is not None and conditional.x is not None:
        final = conditional
        final_source = "conditional_distance_solution_for_stage_2_open_set"
    else:
        final = stage2
        final_source = "stage_2_service_and_opening_solution"
    final_flow = final.x[:pair_count]
    final_open = final.x[pair_count:]
    final_served = float(final_flow.sum())
    final_open_count = int(np.rint(final_open.sum()))
    demand_flow = np.bincount(
        pairs["Demand Position"].to_numpy(np.int64),
        weights=final_flow,
        minlength=len(demand_values),
    )
    shelter_flow = np.bincount(
        pairs["Shelter Position"].to_numpy(np.int64),
        weights=final_flow,
        minlength=shelter_count,
    )
    maximum_demand_violation = float(np.maximum(0, demand_flow - demand_values).max())
    maximum_capacity_violation = float(
        np.maximum(0, shelter_flow - CAPACITY_PER_SHELTER * final_open).max()
    )
    if max(maximum_demand_violation, maximum_capacity_violation) > 1e-5:
        raise RuntimeError(
            "Final allocation violates demand or shelter capacity constraints: "
            f"demand={maximum_demand_violation}, capacity={maximum_capacity_violation}"
        )

    def result_gap(result: object) -> float | None:
        value = getattr(result, "mip_gap", None)
        return None if value is None else float(value)

    metadata = {
        "Stage 1 Status": int(stage1.status),
        "Stage 1 Message": stage1.message,
        "Stage 1 Proven Optimal": bool(stage1.status == 0),
        "Stage 1 MIP Gap": result_gap(stage1),
        "Stage 1 Served Target": served_target,
        "Stage 2 Status": int(stage2.status),
        "Stage 2 Message": stage2.message,
        "Stage 2 Proven Optimal": bool(stage2.status == 0),
        "Stage 2 MIP Gap": result_gap(stage2),
        "Stage 2 Open-Shelter Target": open_target,
        "Stage 3 Status": int(stage3.status),
        "Stage 3 Message": stage3.message,
        "Stage 3 Proven Optimal": bool(stage3.status == 0),
        "Stage 3 MIP Gap": result_gap(stage3),
        "Stage 3 Solution Used": stage3.x is not None,
        "Conditional Distance Status": (
            None if conditional is None else int(conditional.status)
        ),
        "Conditional Distance Message": (
            None if conditional is None else conditional.message
        ),
        "Conditional Distance Proven Optimal": bool(
            conditional is not None and conditional.status == 0
        ),
        "Final Solution Source": final_source,
        "Final Served Demand": final_served,
        "Final Open-Shelter Count": final_open_count,
        "Maximum Demand Constraint Violation": maximum_demand_violation,
        "Maximum Capacity Constraint Violation": maximum_capacity_violation,
    }
    print(f"Stage 3: {stage3.message}")
    if conditional is not None:
        print(f"Conditional distance refinement: {conditional.message}")
    return final.x, metadata


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    edges, graph = load_walking_edges()
    edge_lookup = edges[
        ["Road Edge ID", "From Node ID", "To Node ID", "Road Length (m)"]
    ].drop_duplicates("Road Edge ID")
    demand = pd.read_parquet(DEMAND_PATH).reset_index(drop=True)
    shelters = pd.read_parquet(SHELTER_PATH)
    shelters = shelters.loc[
        shelters["Shelter Service Class"].eq("general")
        & shelters["Walking Network Snap Accepted"]
    ].reset_index(drop=True)

    pairs = build_reachable_pairs(graph, edge_lookup, demand, shelters)
    pairs["Demand Mesh Code"] = demand.loc[pairs["Demand Position"], "Mesh Code"].to_numpy()
    pairs["Shelter ID"] = shelters.loc[pairs["Shelter Position"], "Shelter ID"].to_numpy()
    pairs.to_parquet(OUT / "primary_reachable_demand_shelter_pairs.parquet", index=False)
    print(f"Reachable pairs complete: {len(pairs):,}")

    demand_values = demand[DEMAND_COLUMN].to_numpy(float)
    solution, metadata = solve_lexicographic(pairs, demand_values, len(shelters))
    pair_count = len(pairs)
    flow = solution[:pair_count]
    open_values = solution[pair_count:]

    demand_served = np.bincount(
        pairs["Demand Position"].to_numpy(np.int64),
        weights=flow,
        minlength=len(demand),
    )
    demand_result = demand[
        [
            "Mesh Code",
            "Municipality Code",
            "Municipality",
            "Total Population",
            DEMAND_COLUMN,
            "Mesh Geometry",
        ]
    ].copy()
    demand_result["Capacity-Constrained Served Demand"] = demand_served
    demand_result["Local Unmet Shelter Demand"] = np.maximum(
        0, demand_values - demand_served
    )
    demand_result.to_parquet(
        PROCESSED / "kumamoto_prefecture_primary_shelter_allocation_preprocessed.parquet",
        index=False,
    )

    shelter_assigned = np.bincount(
        pairs["Shelter Position"].to_numpy(np.int64),
        weights=flow,
        minlength=len(shelters),
    )
    shelter_result = shelters[
        ["Shelter ID", "Shelter Name", "Municipality Code", "Municipality", "Shelter Point Geometry"]
    ].copy()
    shelter_result["Modeled Open Shelter"] = open_values >= 0.5
    shelter_result["Assigned Demand"] = shelter_assigned
    shelter_result["Modeled Utilization Percent"] = 100 * shelter_assigned / CAPACITY_PER_SHELTER
    shelter_result.to_csv(OUT / "primary_modeled_shelter_openings.csv", index=False)

    municipality = (
        demand_result.groupby(["Municipality Code", "Municipality"], as_index=False)
        .agg(
            Scenario_Demand=(DEMAND_COLUMN, "sum"),
            Served_Demand=("Capacity-Constrained Served Demand", "sum"),
            Unmet_Demand=("Local Unmet Shelter Demand", "sum"),
        )
    )
    openings = (
        shelter_result.groupby(["Municipality Code", "Municipality"], as_index=False)
        .agg(
            Modeled_Open_Shelters=("Modeled Open Shelter", "sum"),
            Assigned_Demand=("Assigned Demand", "sum"),
        )
    )
    municipality = municipality.merge(
        openings,
        on=["Municipality Code", "Municipality"],
        how="left",
        validate="1:1",
    )
    municipality["Served Percent"] = 100 * municipality["Served_Demand"] / municipality[
        "Scenario_Demand"
    ]
    municipality.sort_values("Served Percent").to_csv(
        OUT / "primary_municipality_capacity_constrained_results.csv", index=False
    )

    metadata.update(
        {
            "Demand Scenario": DEMAND_COLUMN,
            "Scenario Demand": float(demand_values.sum()),
            "Capacity per Shelter": CAPACITY_PER_SHELTER,
            "Maximum Open Shelters": MAXIMUM_OPEN_SHELTERS,
            "Maximum Walking Distance (m)": MAXIMUM_WALKING_DISTANCE_M,
            "Reachable Pairs": len(pairs),
            "Served Demand in Final Solution": float(demand_served.sum()),
            "Unmet Demand in Final Solution": float((demand_values - demand_served).sum()),
            "Modeled Open Shelters in Final Solution": int((open_values >= 0.5).sum()),
        }
    )
    pd.DataFrame([metadata]).to_csv(OUT / "primary_model_summary.csv", index=False)
    print("\nPrimary model summary")
    print(pd.DataFrame([metadata]).to_string(index=False))
    print("\nLowest municipality service")
    print(municipality.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
