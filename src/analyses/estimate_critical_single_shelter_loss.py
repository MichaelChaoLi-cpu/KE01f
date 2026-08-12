"""Screen high-pressure shelters for single-facility service loss."""

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
OPENING_PATH = PRIMARY / "primary_modeled_shelter_openings.csv"
SUMMARY_PATH = PRIMARY / "primary_model_summary.csv"
DEMAND_COLUMN = "Observed-Use Stress Demand High Housing-Loss Weighted"
CAPACITY = 50.0
MAXIMUM_OPEN_SHELTERS = 415
CANDIDATE_COUNT = 30


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
    baseline_served = float(
        pd.read_csv(SUMMARY_PATH).loc[0, "Stage 1 Served Target"]
    )
    prior_open = pd.read_csv(
        OPENING_PATH,
        usecols=["Shelter ID", "Modeled Open Shelter"],
        dtype={"Shelter ID": str},
    ).set_index("Shelter ID")["Modeled Open Shelter"]

    pressure = (
        pairs.assign(
            Reachable_Demand=demand_values[
                pairs["Demand Position"].to_numpy(np.int64)
            ]
        )
        .groupby("Shelter Position")["Reachable_Demand"]
        .sum()
        .reindex(np.arange(len(shelters)), fill_value=0.0)
        .to_numpy(float)
    )
    candidates = np.argsort(-pressure, kind="stable")[:CANDIDATE_COUNT]

    matrix, upper = constraint_matrix(
        pairs, demand_values, len(shelters), CAPACITY
    )
    lower_constraint = np.full(matrix.shape[0], -np.inf)
    lower_constraint[-1] = MAXIMUM_OPEN_SHELTERS
    pair_count = len(pairs)
    variable_count = pair_count + len(shelters)
    integrality = np.concatenate(
        [
            np.zeros(pair_count, dtype=np.int8),
            np.ones(len(shelters), dtype=np.int8),
        ]
    )
    objective = np.concatenate([-np.ones(pair_count), np.zeros(len(shelters))])

    rows: list[dict[str, object]] = []
    output_path = OUT / "critical_single_shelter_loss.csv"
    for rank, position in enumerate(candidates, start=1):
        available = np.ones(len(shelters), dtype=float)
        available[position] = 0.0
        result = milp(
            objective,
            integrality=integrality,
            bounds=Bounds(
                np.zeros(variable_count),
                np.concatenate([np.full(pair_count, np.inf), available]),
            ),
            constraints=LinearConstraint(matrix, lower_constraint, upper),
            options={"time_limit": 60.0, "mip_rel_gap": 1e-4, "presolve": True},
        )
        if result.x is None:
            raise RuntimeError(
                f"No single-loss solution for shelter position {position}: {result.message}"
            )
        served = float(result.x[:pair_count].sum())
        dual = getattr(result, "mip_dual_bound", None)
        served_upper = -float(dual) if dual is not None else np.nan
        loss_lower = max(0.0, baseline_served - served_upper)
        loss_upper = max(0.0, baseline_served - served)
        shelter_id = str(shelters.loc[position, "Shelter ID"])
        rows.append(
            {
                "Pressure Rank": rank,
                "Shelter Position": int(position),
                "Shelter ID": shelter_id,
                "Shelter Name": shelters.loc[position, "Shelter Name"],
                "Municipality Code": shelters.loc[position, "Municipality Code"],
                "Municipality": shelters.loc[position, "Municipality"],
                "Reachable-Pressure Score": pressure[position],
                "Open in Primary Stage-2 Set": bool(
                    prior_open.get(shelter_id, False)
                ),
                "Served Demand after Removal": served,
                "Served-Demand Solver Upper Bound": served_upper,
                "Single-Shelter Service-Loss Lower Bound": loss_lower,
                "Single-Shelter Service-Loss Upper Bound": loss_upper,
                "Status": int(result.status),
                "Message": result.message,
                "Proven Optimal": bool(result.status == 0),
                "MIP Gap": getattr(result, "mip_gap", np.nan),
            }
        )
        pd.DataFrame(rows).to_csv(output_path, index=False)
        print(
            f"{rank:02d}/{CANDIDATE_COUNT} {shelters.loc[position, 'Shelter Name']}: "
            f"loss=[{loss_lower:.3f}, {loss_upper:.3f}], "
            f"gap={getattr(result, 'mip_gap', None)}",
            flush=True,
        )

    results = pd.DataFrame(rows).sort_values(
        [
            "Single-Shelter Service-Loss Lower Bound",
            "Single-Shelter Service-Loss Upper Bound",
        ],
        ascending=False,
    )
    results.to_csv(output_path, index=False)
    print("\nHighest confirmed single-shelter losses")
    print(results.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
