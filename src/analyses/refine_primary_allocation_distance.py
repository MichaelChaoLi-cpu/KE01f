"""Minimize walking distance for the stage-2 optimal shelter opening set.

This is the documented fallback when the global third-stage mixed-integer model
does not return a feasible incumbent within its time limit. It preserves the
proven-optimal served-demand target and the selected 415-shelter set, then solves
the remaining continuous transportation problem exactly.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.sparse import coo_array


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "exp" / "primary-capacity-constrained-allocation"
PROCESSED = ROOT / "data" / "processed"
DEMAND_PATH = (
    PROCESSED
    / "kumamoto_prefecture_demand_mesh_walking_network_access_preprocessed.parquet"
)
SHELTER_PATH = (
    PROCESSED
    / "kumamoto_prefecture_shelter_walking_network_access_preprocessed.parquet"
)
PAIR_PATH = OUT / "primary_reachable_demand_shelter_pairs.parquet"
OPENING_PATH = OUT / "primary_modeled_shelter_openings.csv"
SUMMARY_PATH = OUT / "primary_model_summary.csv"
DEMAND_COLUMN = "Observed-Use Stress Demand High Housing-Loss Weighted"
CAPACITY_PER_SHELTER = 50.0


def main() -> None:
    demand = pd.read_parquet(DEMAND_PATH).reset_index(drop=True)
    shelters = pd.read_parquet(SHELTER_PATH)
    shelters = shelters.loc[
        shelters["Shelter Service Class"].eq("general")
        & shelters["Walking Network Snap Accepted"]
    ].reset_index(drop=True)
    pairs = pd.read_parquet(PAIR_PATH).reset_index(drop=True)
    prior_openings = pd.read_csv(
        OPENING_PATH,
        usecols=["Shelter ID", "Modeled Open Shelter"],
        dtype={"Shelter ID": str},
    )
    summary = pd.read_csv(SUMMARY_PATH)

    open_lookup = prior_openings.set_index("Shelter ID")["Modeled Open Shelter"]
    open_values = (
        shelters["Shelter ID"].astype(str).map(open_lookup).fillna(False).astype(bool)
    )
    if int(open_values.sum()) != 415:
        raise RuntimeError(f"Expected 415 modeled openings, found {open_values.sum()}")

    target = float(summary.loc[0, "Stage 1 Served Target"])
    demand_index = pairs["Demand Position"].to_numpy(np.int64)
    shelter_index = pairs["Shelter Position"].to_numpy(np.int64)
    variable_index = np.arange(len(pairs), dtype=np.int64)

    rows = np.concatenate([demand_index, len(demand) + shelter_index])
    cols = np.concatenate([variable_index, variable_index])
    values = np.ones(2 * len(pairs), dtype=float)
    matrix = coo_array(
        (values, (rows, cols)),
        shape=(len(demand) + len(shelters), len(pairs)),
    ).tocsc()
    upper = np.concatenate(
        [
            demand[DEMAND_COLUMN].to_numpy(float),
            CAPACITY_PER_SHELTER * open_values.to_numpy(float),
        ]
    )
    equality = coo_array(
        (
            np.ones(len(pairs), dtype=float),
            (
                np.zeros(len(pairs), dtype=np.int64),
                variable_index,
            ),
        ),
        shape=(1, len(pairs)),
    ).tocsc()
    result = linprog(
        pairs["Walking Distance (m)"].to_numpy(float),
        A_ub=matrix,
        b_ub=upper,
        A_eq=equality,
        b_eq=np.array([target]),
        bounds=(0, None),
        method="highs",
        options={"time_limit": 180.0, "presolve": True},
    )
    if result.x is None:
        raise RuntimeError(f"Conditional distance refinement failed: {result.message}")

    flow = result.x
    demand_values = demand[DEMAND_COLUMN].to_numpy(float)
    demand_served = np.bincount(
        demand_index, weights=flow, minlength=len(demand)
    )
    shelter_assigned = np.bincount(
        shelter_index, weights=flow, minlength=len(shelters)
    )
    demand_violation = float(np.maximum(0, demand_served - demand_values).max())
    capacity_violation = float(
        np.maximum(
            0,
            shelter_assigned - CAPACITY_PER_SHELTER * open_values.to_numpy(float),
        ).max()
    )
    service_error = abs(float(flow.sum()) - target)
    if max(demand_violation, capacity_violation, service_error) > 1e-5:
        raise RuntimeError(
            "Conditional solution failed validation: "
            f"demand={demand_violation}, capacity={capacity_violation}, "
            f"service={service_error}"
        )

    positive = pairs.loc[flow > 1e-9].copy()
    positive["Assigned Demand"] = flow[flow > 1e-9]
    positive.to_parquet(
        OUT / "primary_positive_demand_shelter_allocation.parquet", index=False
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

    shelter_result = shelters[
        [
            "Shelter ID",
            "Shelter Name",
            "Municipality Code",
            "Municipality",
            "Shelter Point Geometry",
        ]
    ].copy()
    shelter_result["Modeled Open Shelter"] = open_values.to_numpy()
    shelter_result["Assigned Demand"] = shelter_assigned
    shelter_result["Modeled Utilization Percent"] = (
        100 * shelter_assigned / CAPACITY_PER_SHELTER
    )
    shelter_result.to_csv(OPENING_PATH, index=False)

    municipality = (
        demand_result.groupby(["Municipality Code", "Municipality"], as_index=False)
        .agg(
            Scenario_Demand=(DEMAND_COLUMN, "sum"),
            Served_Demand=("Capacity-Constrained Served Demand", "sum"),
            Unmet_Demand=("Local Unmet Shelter Demand", "sum"),
        )
    )
    openings = (
        shelter_result.groupby(
            ["Municipality Code", "Municipality"], as_index=False
        ).agg(
            Modeled_Open_Shelters=("Modeled Open Shelter", "sum"),
            Demand_Assigned_to_Local_Shelters=("Assigned Demand", "sum"),
        )
    )
    municipality = municipality.merge(
        openings,
        on=["Municipality Code", "Municipality"],
        how="left",
        validate="1:1",
    )
    municipality["Served Percent"] = (
        100 * municipality["Served_Demand"] / municipality["Scenario_Demand"]
    )
    municipality = municipality.sort_values("Served Percent")
    municipality.to_csv(
        OUT / "primary_municipality_capacity_constrained_results.csv", index=False
    )

    weighted_mean_distance = float(
        np.average(pairs["Walking Distance (m)"].to_numpy(float), weights=flow)
    )
    summary.loc[0, "Conditional Distance Status"] = int(result.status)
    summary.loc[0, "Conditional Distance Message"] = result.message
    summary.loc[0, "Conditional Distance Proven Optimal"] = bool(result.status == 0)
    summary.loc[0, "Final Solution Source"] = (
        "conditional_distance_solution_for_stage_2_open_set"
    )
    summary.loc[0, "Served Demand in Final Solution"] = float(demand_served.sum())
    summary.loc[0, "Unmet Demand in Final Solution"] = float(
        (demand_values - demand_served).sum()
    )
    summary.loc[0, "Demand-Weighted Mean Walking Distance (m)"] = weighted_mean_distance
    summary.loc[0, "Positive Allocation Pairs"] = int((flow > 1e-9).sum())
    summary.loc[0, "Maximum Demand Constraint Violation"] = demand_violation
    summary.loc[0, "Maximum Capacity Constraint Violation"] = capacity_violation
    summary.to_csv(SUMMARY_PATH, index=False)

    print(summary.to_string(index=False))
    print("\nLowest municipality service")
    print(municipality.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
