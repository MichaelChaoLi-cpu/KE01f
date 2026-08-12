"""Estimate maximum service under standardized shelter-capacity thresholds."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, linprog, milp
from scipy.sparse import coo_array


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "exp" / "primary-capacity-constrained-allocation"
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
PAIR_PATH = OUT / "primary_reachable_demand_shelter_pairs.parquet"
DEMAND_COLUMN = "Observed-Use Stress Demand High Housing-Loss Weighted"
CAPACITY_THRESHOLDS = (25.0, 50.0, 100.0, 200.0)
MAXIMUM_OPEN_SHELTERS = 415


def constraint_matrix(
    pairs: pd.DataFrame,
    demand_values: np.ndarray,
    shelter_count: int,
    capacity: float,
) -> tuple[coo_array, np.ndarray]:
    pair_count = len(pairs)
    demand_count = len(demand_values)
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
            np.full(shelter_count, -capacity),
            np.ones(shelter_count),
        ]
    )
    matrix = coo_array(
        (values, (rows, cols)),
        shape=(demand_count + shelter_count + 1, pair_count + shelter_count),
    ).tocsc()
    upper = np.concatenate(
        [
            demand_values,
            np.zeros(shelter_count),
            np.array([MAXIMUM_OPEN_SHELTERS], dtype=float),
        ]
    )
    return matrix, upper


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all-open-only",
        action="store_true",
        help="Reuse existing 415-opening results and recompute only all-open LP rows.",
    )
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    demand = pd.read_parquet(DEMAND_PATH).reset_index(drop=True)
    shelters = pd.read_parquet(SHELTER_PATH)
    shelters = shelters.loc[
        shelters["Shelter Service Class"].eq("general")
        & shelters["Walking Network Snap Accepted"]
    ].reset_index(drop=True)
    pairs = pd.read_parquet(PAIR_PATH).reset_index(drop=True)
    demand_values = demand[DEMAND_COLUMN].to_numpy(float)
    geographically_reachable = float(
        demand.loc[pairs["Demand Position"].unique(), DEMAND_COLUMN].sum()
    )
    pair_count = len(pairs)
    shelter_count = len(shelters)
    variable_count = pair_count + shelter_count
    bounds = Bounds(
        np.zeros(variable_count),
        np.concatenate([np.full(pair_count, np.inf), np.ones(shelter_count)]),
    )
    integrality = np.concatenate(
        [np.zeros(pair_count, dtype=np.int8), np.ones(shelter_count, dtype=np.int8)]
    )
    objective = np.concatenate([-np.ones(pair_count), np.zeros(shelter_count)])

    result_path = OUT / "capacity_threshold_sensitivity.csv"
    if args.all_open_only:
        if not result_path.exists():
            raise FileNotFoundError(
                "Run the full threshold script before using --all-open-only."
            )
        cached = pd.read_csv(result_path)
        if "Opening Constraint" not in cached.columns:
            cached["Opening Constraint"] = "At most 415 modeled openings"
        cached = cached.loc[
            cached["Opening Constraint"].eq("At most 415 modeled openings")
        ]
        rows: list[dict[str, object]] = cached.to_dict("records")
    else:
        rows = []

    for capacity in (() if args.all_open_only else CAPACITY_THRESHOLDS):
        matrix, upper = constraint_matrix(
            pairs, demand_values, shelter_count, capacity
        )
        result = milp(
            objective,
            integrality=integrality,
            bounds=bounds,
            constraints=LinearConstraint(
                matrix, np.full(matrix.shape[0], -np.inf), upper
            ),
            options={"time_limit": 180.0, "mip_rel_gap": 1e-7, "presolve": True},
        )
        if result.x is None:
            raise RuntimeError(
                f"No feasible solution for capacity {capacity}: {result.message}"
            )
        flow = result.x[:pair_count]
        openings = result.x[pair_count:]
        served = float(flow.sum())
        rows.append(
            {
                "Capacity per Open Shelter": capacity,
                "Opening Constraint": "At most 415 modeled openings",
                "Maximum Open Shelters": MAXIMUM_OPEN_SHELTERS,
                "Scenario Demand": float(demand_values.sum()),
                "Geographically Reachable Demand": geographically_reachable,
                "Maximum Served Demand": served,
                "Unmet Demand": float(demand_values.sum() - served),
                "Served Percent": 100 * served / demand_values.sum(),
                "Geographically Reachable Served Percent": (
                    100 * served / geographically_reachable
                ),
                "Modeled Open Shelters in Returned Solution": int(
                    (openings >= 0.5).sum()
                ),
                "Status": int(result.status),
                "Message": result.message,
                "Proven Optimal": bool(result.status == 0),
                "MIP Gap": getattr(result, "mip_gap", np.nan),
                "MIP Dual Bound Served Demand": (
                    -float(result.mip_dual_bound)
                    if getattr(result, "mip_dual_bound", None) is not None
                    else np.nan
                ),
            }
        )
        print(
            f"capacity={capacity:.0f}: served={served:,.3f}; "
            f"open={(openings >= 0.5).sum():,}; status={result.status}; "
            f"gap={getattr(result, 'mip_gap', None)}"
        )

    # Fixed all-open benchmark: no facility-selection integers are needed, so
    # this transportation problem is solved exactly as a continuous LP.
    demand_index = pairs["Demand Position"].to_numpy(np.int64)
    shelter_index = pairs["Shelter Position"].to_numpy(np.int64)
    pair_index = np.arange(pair_count, dtype=np.int64)
    all_open_matrix = coo_array(
        (
            np.ones(2 * pair_count),
            (
                np.concatenate([demand_index, len(demand) + shelter_index]),
                np.concatenate([pair_index, pair_index]),
            ),
        ),
        shape=(len(demand) + shelter_count, pair_count),
    ).tocsc()
    for capacity in CAPACITY_THRESHOLDS:
        upper = np.concatenate(
            [demand_values, np.full(shelter_count, capacity, dtype=float)]
        )
        result = linprog(
            -np.ones(pair_count),
            A_ub=all_open_matrix,
            b_ub=upper,
            bounds=(0, None),
            method="highs",
            options={"time_limit": 180.0, "presolve": True},
        )
        if result.x is None:
            raise RuntimeError(
                f"All-open benchmark failed for capacity {capacity}: {result.message}"
            )
        served = float(result.x.sum())
        used_shelters = int(
            (
                np.bincount(
                    shelter_index, weights=result.x, minlength=shelter_count
                )
                > 1e-9
            ).sum()
        )
        rows.append(
            {
                "Capacity per Open Shelter": capacity,
                "Opening Constraint": "All 1,156 general shelters available",
                "Maximum Open Shelters": shelter_count,
                "Scenario Demand": float(demand_values.sum()),
                "Geographically Reachable Demand": geographically_reachable,
                "Maximum Served Demand": served,
                "Unmet Demand": float(demand_values.sum() - served),
                "Served Percent": 100 * served / demand_values.sum(),
                "Geographically Reachable Served Percent": (
                    100 * served / geographically_reachable
                ),
                "Modeled Open Shelters in Returned Solution": used_shelters,
                "Status": int(result.status),
                "Message": result.message,
                "Proven Optimal": bool(result.status == 0),
                "MIP Gap": np.nan,
                "MIP Dual Bound Served Demand": np.nan,
            }
        )
        print(
            f"all-open capacity={capacity:.0f}: served={served:,.3f}; "
            f"used={used_shelters:,}; status={result.status}"
        )

    output = pd.DataFrame(rows)
    output.to_csv(result_path, index=False)
    print("\n", output.to_string(index=False))


if __name__ == "__main__":
    main()
