"""Estimate demand-geography and walking-access allocation sensitivity.

All scenarios use a standardized capacity of 50 persons and at most 415 modeled
open general shelters. Demand-geography sensitivity varies the spatialization of
the same 10,467-person observed-use stress total at the primary 15-minute,
4-km/h threshold. Access sensitivity holds the high-housing-loss-weighted demand
constant and varies walking speed and time.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp

from estimate_capacity_threshold_sensitivity import constraint_matrix
from estimate_primary_capacity_constrained_allocation import (
    build_reachable_pairs,
    load_walking_edges,
)


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "exp" / "shelter-robustness"
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
PAIR_PATH = OUT / "demand_shelter_pairs_within_2km.parquet"
CAPACITY = 50.0
MAXIMUM_OPEN_SHELTERS = 415
DEMAND_COLUMNS = {
    "population_weighted": "Observed-Use Stress Demand Population Weighted",
    "central_loss_weighted": (
        "Observed-Use Stress Demand Central Housing-Loss Weighted"
    ),
    "high_loss_weighted": "Observed-Use Stress Demand High Housing-Loss Weighted",
}


def get_pairs(
    demand: pd.DataFrame, shelters: pd.DataFrame, rebuild: bool = False
) -> pd.DataFrame:
    if PAIR_PATH.exists() and not rebuild:
        return pd.read_parquet(PAIR_PATH)
    edges, graph = load_walking_edges()
    edge_lookup = edges[
        ["Road Edge ID", "From Node ID", "To Node ID", "Road Length (m)"]
    ].drop_duplicates("Road Edge ID")
    pairs = build_reachable_pairs(
        graph,
        edge_lookup,
        demand,
        shelters,
        maximum_distance_m=2000.0,
    )
    pairs["Demand Mesh Code"] = demand.loc[
        pairs["Demand Position"], "Mesh Code"
    ].to_numpy()
    pairs["Shelter ID"] = shelters.loc[
        pairs["Shelter Position"], "Shelter ID"
    ].to_numpy()
    pairs.to_parquet(PAIR_PATH, index=False)
    return pairs


def solve_maximum_service(
    pairs: pd.DataFrame,
    demand_values: np.ndarray,
    shelter_count: int,
    time_limit: float,
) -> tuple[object, float, int]:
    matrix, upper = constraint_matrix(
        pairs, demand_values, shelter_count, CAPACITY
    )
    pair_count = len(pairs)
    variable_count = pair_count + shelter_count
    lower = np.full(matrix.shape[0], -np.inf)
    # For a service-maximization objective, any solution using fewer than 415
    # shelters can add unused openings without changing service. Equality is
    # therefore service-equivalent to the stated at-most limit and removes a
    # large family of symmetric binary solutions.
    lower[-1] = MAXIMUM_OPEN_SHELTERS
    result = milp(
        np.concatenate([-np.ones(pair_count), np.zeros(shelter_count)]),
        integrality=np.concatenate(
            [
                np.zeros(pair_count, dtype=np.int8),
                np.ones(shelter_count, dtype=np.int8),
            ]
        ),
        bounds=Bounds(
            np.zeros(variable_count),
            np.concatenate(
                [np.full(pair_count, np.inf), np.ones(shelter_count)]
            ),
        ),
        constraints=LinearConstraint(matrix, lower, upper),
        options={"time_limit": time_limit, "mip_rel_gap": 1e-6, "presolve": True},
    )
    if result.x is None:
        raise RuntimeError(f"Sensitivity model returned no solution: {result.message}")
    served = float(result.x[:pair_count].sum())
    openings = int((result.x[pair_count:] >= 0.5).sum())
    return result, served, openings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        nargs="*",
        help="Recompute only named scenarios and retain other existing rows.",
    )
    parser.add_argument("--time-limit", type=float, default=60.0)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    demand = pd.read_parquet(DEMAND_PATH).reset_index(drop=True)
    shelters = pd.read_parquet(SHELTER_PATH)
    shelters = shelters.loc[
        shelters["Shelter Service Class"].eq("general")
        & shelters["Walking Network Snap Accepted"]
    ].reset_index(drop=True)
    all_pairs = get_pairs(demand, shelters)
    print(f"Pairs within 2 km: {len(all_pairs):,}")

    scenarios: list[dict[str, object]] = []
    for label, column in DEMAND_COLUMNS.items():
        scenarios.append(
            {
                "Sensitivity Dimension": "Demand geography",
                "Scenario": label,
                "Demand Column": column,
                "Walking Speed (km/h)": 4.0,
                "Time Threshold (min)": 15.0,
                "Distance Threshold (m)": 1000.0,
            }
        )
    for speed in (3.0, 4.0):
        for minutes in (10.0, 15.0, 30.0):
            if speed == 4.0 and minutes == 15.0:
                continue
            scenarios.append(
                {
                    "Sensitivity Dimension": "Walking access",
                    "Scenario": f"{minutes:.0f}min_{speed:.0f}kmh",
                    "Demand Column": DEMAND_COLUMNS["high_loss_weighted"],
                    "Walking Speed (km/h)": speed,
                    "Time Threshold (min)": minutes,
                    "Distance Threshold (m)": 1000 * speed * minutes / 60,
                }
            )

    result_path = OUT / "demand_access_sensitivity.csv"
    if args.only and result_path.exists():
        existing = pd.read_csv(result_path)
        existing = existing.loc[~existing["Scenario"].isin(args.only)]
        result_rows: list[dict[str, object]] = existing.to_dict("records")
        scenarios = [s for s in scenarios if str(s["Scenario"]) in args.only]
    else:
        result_rows = []
    for scenario in scenarios:
        threshold = float(scenario["Distance Threshold (m)"])
        pairs = all_pairs.loc[
            all_pairs["Walking Distance (m)"].le(threshold + 1e-9)
        ].reset_index(drop=True)
        demand_column = str(scenario["Demand Column"])
        demand_values = demand[demand_column].to_numpy(float)
        reachable_positions = pairs["Demand Position"].unique()
        reachable = float(demand.loc[reachable_positions, demand_column].sum())
        result, served, openings = solve_maximum_service(
            pairs, demand_values, len(shelters), args.time_limit
        )
        dual = getattr(result, "mip_dual_bound", None)
        result_rows.append(
            {
                **scenario,
                "Capacity per Open Shelter": CAPACITY,
                "Maximum Open Shelters": MAXIMUM_OPEN_SHELTERS,
                "Scenario Demand": float(demand_values.sum()),
                "Reachable Demand before Capacity": reachable,
                "Reachable Percent": 100 * reachable / demand_values.sum(),
                "Maximum Served Demand": served,
                "Served Percent": 100 * served / demand_values.sum(),
                "Unmet Demand": float(demand_values.sum() - served),
                "Additional Capacity-Opening Gap": reachable - served,
                "Modeled Open Shelters": openings,
                "Status": int(result.status),
                "Message": result.message,
                "Proven Optimal": bool(result.status == 0),
                "MIP Gap": getattr(result, "mip_gap", np.nan),
                "MIP Dual Bound Served Demand": (
                    -float(dual) if dual is not None else np.nan
                ),
                "Reachable Pairs": len(pairs),
            }
        )
        print(
            f"{scenario['Sensitivity Dimension']} {scenario['Scenario']}: "
            f"reachable={reachable:,.2f}, served={served:,.2f}, "
            f"status={result.status}, gap={getattr(result, 'mip_gap', None)}",
            flush=True,
        )
        pd.DataFrame(result_rows).to_csv(result_path, index=False)

    results = pd.DataFrame(result_rows)
    results.to_csv(result_path, index=False)
    print("\n", results.to_string(index=False))


if __name__ == "__main__":
    main()
