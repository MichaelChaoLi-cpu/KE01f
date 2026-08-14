#!/usr/bin/env python3
"""Refine endpoint evidence for the shared-capacity multimodal core scenarios.

The script replaces walking-only rows with the existing proven-optimal walking
allocation and improves the fully vehicle-enabled, 100-person endpoint using the
proven-optimal 75-percent vehicle-enabled facility set followed by exact maximum flow.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, linprog, milp
from scipy.sparse import coo_array


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/exp/shared-capacity-multimodal-allocation"
CORE_PATH = OUT / "shared_capacity_mode_and_capacity_sensitivity.csv"
REFINED_PATH = OUT / "shared_capacity_mode_and_capacity_sensitivity_refined.csv"
WALKING_RESULTS = ROOT / "data/exp/primary-capacity-constrained-allocation/capacity_threshold_sensitivity.csv"
DEMAND_PATH = ROOT / "data/processed/kumamoto_prefecture_demand_mesh_walking_network_access_preprocessed.parquet"
WALKING_PAIRS = ROOT / "data/exp/primary-capacity-constrained-allocation/primary_reachable_demand_shelter_pairs.parquet"
VEHICLE_PAIRS = OUT / "vehicle_flexible_pairs_15min_0_50x.parquet"

DEMAND_COLUMN = "Observed-Use Stress Demand High Housing-Loss Weighted"
SHELTER_COUNT = 1156
OPENING_LIMIT = 415


def select_central_high_vehicle_facilities(
    demand_values: np.ndarray,
    walking: pd.DataFrame,
    vehicle: pd.DataFrame,
) -> np.ndarray:
    vehicle_share = 0.75
    capacity = 100.0
    demand_count = len(demand_values)
    components = [
        (walking, (1.0 - vehicle_share) * demand_values),
        (vehicle, vehicle_share * demand_values),
    ]
    specifications: list[tuple[pd.DataFrame, np.ndarray, np.ndarray]] = []
    component_count = 0
    for pairs, values in components:
        active = np.unique(pairs["Demand Position"].to_numpy(np.int64))
        position_map = np.full(demand_count, -1, dtype=np.int64)
        position_map[active] = np.arange(len(active), dtype=np.int64)
        specifications.append((pairs, position_map, values[active]))
        component_count += len(active)

    rows: list[np.ndarray] = []
    columns: list[np.ndarray] = []
    values: list[np.ndarray] = []
    weights: list[np.ndarray] = []
    offset = 0
    for pairs, position_map, component_weights in specifications:
        pair_demand = pairs["Demand Position"].to_numpy(np.int64)
        pair_shelter = pairs["Shelter Position"].to_numpy(np.int64)
        active_count = len(component_weights)
        component_columns = np.arange(offset, offset + active_count, dtype=np.int64)
        rows.extend([component_columns, offset + position_map[pair_demand]])
        columns.extend([component_columns, component_count + pair_shelter])
        values.extend([np.ones(active_count), -np.ones(len(pairs))])
        weights.append(component_weights)
        offset += active_count

    all_weights = np.concatenate(weights)
    capacity_row = component_count
    opening_row = component_count + 1
    rows.extend(
        [
            np.full(component_count, capacity_row, dtype=np.int64),
            np.full(SHELTER_COUNT, capacity_row, dtype=np.int64),
            np.full(SHELTER_COUNT, opening_row, dtype=np.int64),
        ]
    )
    columns.extend(
        [
            np.arange(component_count, dtype=np.int64),
            component_count + np.arange(SHELTER_COUNT, dtype=np.int64),
            component_count + np.arange(SHELTER_COUNT, dtype=np.int64),
        ]
    )
    values.extend(
        [all_weights, np.full(SHELTER_COUNT, -capacity), np.ones(SHELTER_COUNT)]
    )
    matrix = coo_array(
        (
            np.concatenate(values),
            (np.concatenate(rows), np.concatenate(columns)),
        ),
        shape=(component_count + 2, component_count + SHELTER_COUNT),
    ).tocsc()
    result = milp(
        np.concatenate([-all_weights, np.zeros(SHELTER_COUNT)]),
        integrality=np.concatenate(
            [np.zeros(component_count, dtype=np.int8), np.ones(SHELTER_COUNT, dtype=np.int8)]
        ),
        bounds=Bounds(
            np.zeros(component_count + SHELTER_COUNT),
            np.ones(component_count + SHELTER_COUNT),
        ),
        constraints=LinearConstraint(
            matrix,
            np.full(matrix.shape[0], -np.inf),
            np.concatenate([np.zeros(component_count + 1), [OPENING_LIMIT]]),
        ),
        options={"time_limit": 180.0, "mip_rel_gap": 1e-5, "presolve": True},
    )
    if result.x is None or result.status != 0:
        raise RuntimeError(f"High-vehicle facility selection did not prove optimal: {result.message}")
    selected = np.flatnonzero(result.x[component_count:] >= 0.5)
    if len(selected) > OPENING_LIMIT:
        raise RuntimeError("Selected facility count exceeds the opening limit")
    return selected


def fixed_facility_vehicle_flow(
    demand_values: np.ndarray,
    vehicle: pd.DataFrame,
    selected: np.ndarray,
    capacity: float,
) -> float:
    pairs = vehicle.loc[vehicle["Shelter Position"].isin(selected)].copy()
    pair_count = len(pairs)
    columns = np.arange(pair_count, dtype=np.int64)
    demand_index = pairs["Demand Position"].to_numpy(np.int64)
    shelter_index = pairs["Shelter Position"].to_numpy(np.int64)
    matrix = coo_array(
        (
            np.ones(2 * pair_count),
            (
                np.concatenate([demand_index, len(demand_values) + shelter_index]),
                np.concatenate([columns, columns]),
            ),
        ),
        shape=(len(demand_values) + SHELTER_COUNT, pair_count),
    ).tocsc()
    available = np.isin(np.arange(SHELTER_COUNT), selected)
    result = linprog(
        -np.ones(pair_count),
        A_ub=matrix,
        b_ub=np.concatenate([demand_values, np.where(available, capacity, 0.0)]),
        bounds=(0, None),
        method="highs",
    )
    if result.x is None:
        raise RuntimeError(f"Endpoint maximum flow failed: {result.message}")
    return float(-result.fun)


def main() -> None:
    core = pd.read_csv(CORE_PATH)
    walking_results = pd.read_csv(WALKING_RESULTS)
    walking_results = walking_results.loc[
        walking_results["Opening Constraint"].eq("At most 415 modeled openings")
    ]
    demand = pd.read_parquet(DEMAND_PATH)
    demand_values = demand[DEMAND_COLUMN].to_numpy(float)
    walking = pd.read_parquet(WALKING_PAIRS)
    vehicle = pd.read_parquet(VEHICLE_PAIRS)

    for capacity in (50.0, 100.0):
        source = walking_results.loc[
            walking_results["Capacity per Open Shelter"].eq(capacity)
        ].iloc[0]
        target = (
            core["Capacity per Open Shelter"].eq(capacity)
            & core["Vehicle-Enabled Demand Share"].eq(0.0)
        )
        served = float(source["Maximum Served Demand"])
        core.loc[target, "Maximum Served Demand"] = served
        core.loc[target, "Served Percent"] = 100.0 * served / demand_values.sum()
        core.loc[target, "Model Explanation Gap"] = demand_values.sum() - served
        core.loc[target, "Proven Optimal"] = bool(source["Proven Optimal"])
        core.loc[target, "Status"] = 0 if bool(source["Proven Optimal"]) else 1
        core.loc[target, "MIP Gap"] = float(source["MIP Gap"])
        core.loc[target, "MIP Dual Bound Served Demand"] = float(
            source["MIP Dual Bound Served Demand"]
        )
        core.loc[target, "Message"] = "Reused proven-optimal walking-only allocation"

    selected = select_central_high_vehicle_facilities(
        demand_values, walking, vehicle
    )
    selected_frame = pd.DataFrame({"Shelter Position": selected})
    selected_frame.to_csv(OUT / "central_high_vehicle_selected_shelters.csv", index=False)
    served = fixed_facility_vehicle_flow(demand_values, vehicle, selected, 100.0)
    target = (
        core["Capacity per Open Shelter"].eq(100.0)
        & core["Vehicle-Enabled Demand Share"].eq(1.0)
    )
    upper = float(core.loc[target, "MIP Dual Bound Served Demand"].iloc[0])
    core.loc[target, "Maximum Served Demand"] = served
    core.loc[target, "Served Percent"] = 100.0 * served / demand_values.sum()
    core.loc[target, "Model Explanation Gap"] = demand_values.sum() - served
    core.loc[target, "Modeled Open Shelters"] = len(selected)
    core.loc[target, "Proven Optimal"] = abs(upper - served) <= 1e-5
    core.loc[target, "MIP Gap"] = max(0.0, upper - served) / upper
    core.loc[target, "Message"] = "Improved lower bound from proven-optimal 75-percent vehicle facility set"

    if not core.loc[
        core["Capacity per Open Shelter"].eq(100.0), "Served Percent"
    ].is_monotonic_increasing:
        raise RuntimeError("Central-capacity service must be monotonic in vehicle share")
    core.to_csv(REFINED_PATH, index=False)
    print(f"Saved: {REFINED_PATH.relative_to(ROOT)}")
    print(
        core.loc[core["Capacity per Open Shelter"].eq(100.0), [
            "Vehicle-Enabled Demand Share",
            "Served Percent",
            "Proven Optimal",
            "MIP Gap",
        ]].to_string(index=False)
    )


if __name__ == "__main__":
    main()
