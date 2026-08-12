"""Estimate shelter service under random and pressure-targeted unavailability."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp

from estimate_capacity_threshold_sensitivity import constraint_matrix


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "data" / "exp" / "primary-capacity-constrained-allocation"
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
PAIR_PATH = PRIMARY / "primary_reachable_demand_shelter_pairs.parquet"
DEMAND_COLUMN = "Observed-Use Stress Demand High Housing-Loss Weighted"
CAPACITY = 50.0
MAXIMUM_OPEN_SHELTERS = 415
UNAVAILABILITY_SHARES = (0.10, 0.20, 0.30)
RANDOM_DRAWS = 30
RANDOM_SEED = 20260812


def solve_available_pool(
    pairs: pd.DataFrame,
    demand_values: np.ndarray,
    shelter_count: int,
    available: np.ndarray,
) -> tuple[object, float, int]:
    matrix, upper = constraint_matrix(
        pairs, demand_values, shelter_count, CAPACITY
    )
    pair_count = len(pairs)
    variable_count = pair_count + shelter_count
    lower_constraint = np.full(matrix.shape[0], -np.inf)
    lower_constraint[-1] = min(MAXIMUM_OPEN_SHELTERS, int(available.sum()))
    upper_variable = np.concatenate(
        [np.full(pair_count, np.inf), available.astype(float)]
    )
    result = milp(
        np.concatenate([-np.ones(pair_count), np.zeros(shelter_count)]),
        integrality=np.concatenate(
            [
                np.zeros(pair_count, dtype=np.int8),
                np.ones(shelter_count, dtype=np.int8),
            ]
        ),
        bounds=Bounds(np.zeros(variable_count), upper_variable),
        constraints=LinearConstraint(matrix, lower_constraint, upper),
        options={"time_limit": 30.0, "mip_rel_gap": 1e-3, "presolve": True},
    )
    if result.x is None:
        raise RuntimeError(f"No feasible unavailability solution: {result.message}")
    served = float(result.x[:pair_count].sum())
    openings = int((result.x[pair_count:] >= 0.5).sum())
    return result, served, openings


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    demand = pd.read_parquet(DEMAND_PATH).reset_index(drop=True)
    shelters = pd.read_parquet(SHELTER_PATH)
    shelters = shelters.loc[
        shelters["Shelter Service Class"].eq("general")
        & shelters["Walking Network Snap Accepted"]
    ].reset_index(drop=True)
    pairs = pd.read_parquet(PAIR_PATH).reset_index(drop=True)
    demand_values = demand[DEMAND_COLUMN].to_numpy(float)
    primary_summary = pd.read_csv(PRIMARY / "primary_model_summary.csv")
    baseline_served = float(primary_summary.loc[0, "Stage 1 Served Target"])
    shelter_count = len(shelters)
    rng = np.random.default_rng(RANDOM_SEED)

    pressure = (
        pairs.assign(
            Reachable_Demand=demand_values[
                pairs["Demand Position"].to_numpy(np.int64)
            ]
        )
        .groupby("Shelter Position")["Reachable_Demand"]
        .sum()
        .reindex(np.arange(shelter_count), fill_value=0.0)
        .to_numpy(float)
    )
    targeted_order = np.argsort(-pressure, kind="stable")

    scenario_specs: list[dict[str, object]] = [
        {
            "Failure Mode": "baseline",
            "Unavailability Share": 0.0,
            "Draw": 0,
            "Removed Positions": np.array([], dtype=np.int64),
        }
    ]
    for share in UNAVAILABILITY_SHARES:
        remove_count = int(np.rint(share * shelter_count))
        scenario_specs.append(
            {
                "Failure Mode": "targeted_high_reachable_pressure",
                "Unavailability Share": share,
                "Draw": 0,
                "Removed Positions": targeted_order[:remove_count],
            }
        )
        for draw in range(1, RANDOM_DRAWS + 1):
            scenario_specs.append(
                {
                    "Failure Mode": "random",
                    "Unavailability Share": share,
                    "Draw": draw,
                    "Removed Positions": np.sort(
                        rng.choice(shelter_count, size=remove_count, replace=False)
                    ),
                }
            )

    result_path = OUT / "facility_unavailability_sensitivity.csv"
    removal_path = OUT / "facility_unavailability_removed_shelters.csv"
    result_rows: list[dict[str, object]] = []
    removal_rows: list[dict[str, object]] = []
    for spec in scenario_specs:
        removed = np.asarray(spec["Removed Positions"], dtype=np.int64)
        available = np.ones(shelter_count, dtype=bool)
        available[removed] = False
        if spec["Failure Mode"] == "baseline":
            served = baseline_served
            openings = MAXIMUM_OPEN_SHELTERS
            status = 0
            message = "Reused proven-optimal primary baseline"
            proven_optimal = True
            mip_gap = 0.0
            dual_bound = baseline_served
        else:
            result, served, openings = solve_available_pool(
                pairs, demand_values, shelter_count, available
            )
            status = int(result.status)
            message = result.message
            proven_optimal = bool(result.status == 0)
            mip_gap = getattr(result, "mip_gap", np.nan)
            dual = getattr(result, "mip_dual_bound", None)
            dual_bound = -float(dual) if dual is not None else np.nan
        row = {
            "Failure Mode": spec["Failure Mode"],
            "Unavailability Share": spec["Unavailability Share"],
            "Draw": spec["Draw"],
            "Removed Shelters": len(removed),
            "Available Shelters": int(available.sum()),
            "Removed Reachable-Pressure Score": float(pressure[removed].sum()),
            "Scenario Demand": float(demand_values.sum()),
            "Maximum Served Demand": served,
            "Served Percent": 100 * served / demand_values.sum(),
            "Unmet Demand": float(demand_values.sum() - served),
            "Service Loss from Baseline": baseline_served - served,
            "Modeled Open Shelters": openings,
            "Status": status,
            "Message": message,
            "Proven Optimal": proven_optimal,
            "MIP Gap": mip_gap,
            "MIP Dual Bound Served Demand": dual_bound,
        }
        result_rows.append(row)
        for position in removed:
            removal_rows.append(
                {
                    "Failure Mode": spec["Failure Mode"],
                    "Unavailability Share": spec["Unavailability Share"],
                    "Draw": spec["Draw"],
                    "Shelter Position": int(position),
                    "Shelter ID": shelters.loc[position, "Shelter ID"],
                    "Shelter Name": shelters.loc[position, "Shelter Name"],
                    "Municipality": shelters.loc[position, "Municipality"],
                    "Reachable-Pressure Score": pressure[position],
                }
            )
        pd.DataFrame(result_rows).to_csv(result_path, index=False)
        pd.DataFrame(removal_rows).to_csv(removal_path, index=False)
        print(
            f"{spec['Failure Mode']} share={float(spec['Unavailability Share']):.0%} "
            f"draw={spec['Draw']}: served={served:,.2f}; status={status}; "
            f"gap={mip_gap}",
            flush=True,
        )

    results = pd.DataFrame(result_rows)
    random_summary = (
        results.loc[results["Failure Mode"].eq("random")]
        .groupby("Unavailability Share", as_index=False)
        .agg(
            Draws=("Draw", "count"),
            Mean_Served_Demand=("Maximum Served Demand", "mean"),
            Minimum_Served_Demand=("Maximum Served Demand", "min"),
            Maximum_Served_Demand=("Maximum Served Demand", "max"),
            Mean_Served_Percent=("Served Percent", "mean"),
            Minimum_Served_Percent=("Served Percent", "min"),
            Maximum_Served_Percent=("Served Percent", "max"),
            Mean_Service_Loss=("Service Loss from Baseline", "mean"),
            Maximum_Service_Loss=("Service Loss from Baseline", "max"),
            Maximum_MIP_Gap=("MIP Gap", "max"),
        )
    )
    random_summary.to_csv(
        OUT / "facility_unavailability_random_summary.csv", index=False
    )
    print("\nRandom summary")
    print(random_summary.to_string(index=False))


if __name__ == "__main__":
    main()
