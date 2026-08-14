#!/usr/bin/env python3
"""Re-estimate the focused shared-capacity robustness scenarios.

Framework: The central comparison uses the high-loss-weighted 10,467-person stress
surface, 15 minutes, 4 km/h walking connectors, a 0.50 motorized road-speed factor,
50% vehicle-enabled demand, and 100 persons per shelter. This script adds the
all-1,156-opening comparison and ranks targeted loss by the matching 50% walking
plus 50% vehicle-enabled reachable-pressure measure.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from estimate_shared_capacity_multimodal_allocation import solve_service


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/exp/shared-capacity-multimodal-allocation"
DEMAND_PATH = ROOT / "data/processed/kumamoto_prefecture_demand_mesh_walking_network_access_preprocessed.parquet"
SHELTER_PATH = ROOT / "data/processed/kumamoto_prefecture_shelter_walking_network_access_preprocessed.parquet"
WALKING_PAIR_PATH = ROOT / "data/exp/primary-capacity-constrained-allocation/primary_reachable_demand_shelter_pairs.parquet"
VEHICLE_PAIR_PATH = OUT / "vehicle_flexible_pairs_15min_0_50x.parquet"
CORE_PATH = OUT / "shared_capacity_mode_and_capacity_sensitivity_refined.csv"
FAILURE_PATH = OUT / "matched_multimodal_facility_unavailability.csv"
OPENING_PATH = OUT / "matched_multimodal_opening_scale_sensitivity.csv"

DEMAND_COLUMN = "Observed-Use Stress Demand High Housing-Loss Weighted"
CENTRAL_VEHICLE_SHARE = 0.50
CENTRAL_CAPACITY = 100.0
CENTRAL_OPENING_LIMIT = 415
TARGETED_SHARES = (0.10, 0.20, 0.30)


def reachable_pressure(
    pairs: pd.DataFrame,
    demand_values: np.ndarray,
    shelter_count: int,
) -> np.ndarray:
    positions = pairs["Demand Position"].to_numpy(np.int64)
    return (
        pairs.assign(Reachable_Demand=demand_values[positions])
        .groupby("Shelter Position")["Reachable_Demand"]
        .sum()
        .reindex(np.arange(shelter_count), fill_value=0.0)
        .to_numpy(float)
    )


def main() -> None:
    demand = pd.read_parquet(DEMAND_PATH).reset_index(drop=True)
    shelters = pd.read_parquet(SHELTER_PATH)
    shelters = shelters.loc[
        shelters["Shelter Service Class"].eq("general")
        & shelters["Walking Network Snap Accepted"].fillna(False)
    ].reset_index(drop=True)
    walking_pairs = pd.read_parquet(WALKING_PAIR_PATH)
    vehicle_pairs = pd.read_parquet(VEHICLE_PAIR_PATH)
    demand_values = demand[DEMAND_COLUMN].to_numpy(float)
    shelter_count = len(shelters)

    core = pd.read_csv(CORE_PATH)
    baseline = core.loc[
        core["Vehicle-Enabled Demand Share"].eq(CENTRAL_VEHICLE_SHARE)
        & core["Capacity per Open Shelter"].eq(CENTRAL_CAPACITY)
    ].iloc[0].to_dict()
    baseline["Opening Limit"] = CENTRAL_OPENING_LIMIT

    all_open = solve_service(
        walking_pairs,
        vehicle_pairs,
        demand_values,
        shelter_count,
        CENTRAL_VEHICLE_SHARE,
        CENTRAL_CAPACITY,
        opening_limit=shelter_count,
        time_limit=300.0,
    )
    opening = pd.DataFrame(
        [
            {**baseline, "Opening Scenario": "At most 415 openings"},
            {**all_open, "Opening Scenario": "All 1,156 shelters selectable"},
        ]
    )
    opening.to_csv(OPENING_PATH, index=False)

    walking_pressure = reachable_pressure(walking_pairs, demand_values, shelter_count)
    vehicle_pressure = reachable_pressure(vehicle_pairs, demand_values, shelter_count)
    mixed_pressure = (
        (1.0 - CENTRAL_VEHICLE_SHARE) * walking_pressure
        + CENTRAL_VEHICLE_SHARE * vehicle_pressure
    )
    targeted_order = np.argsort(-mixed_pressure, kind="stable")

    prior = pd.read_csv(FAILURE_PATH)
    retained = prior.loc[
        ~prior["Failure Mode"].astype(str).str.startswith("targeted_")
    ].copy()
    targeted_rows: list[dict[str, object]] = []
    for removal_share in TARGETED_SHARES:
        removal_count = int(np.rint(removal_share * shelter_count))
        available = np.ones(shelter_count, dtype=bool)
        available[targeted_order[:removal_count]] = False
        row = solve_service(
            walking_pairs,
            vehicle_pairs,
            demand_values,
            shelter_count,
            CENTRAL_VEHICLE_SHARE,
            CENTRAL_CAPACITY,
            available=available,
            opening_limit=CENTRAL_OPENING_LIMIT,
            time_limit=300.0,
        )
        row.update(
            {
                "Failure Mode": "targeted_mixed_reachable_pressure",
                "Unavailability Share": removal_share,
                "Draw": 0,
                "Service Loss from Baseline": float(baseline["Maximum Served Demand"])
                - float(row["Maximum Served Demand"]),
            }
        )
        targeted_rows.append(row)
        print(
            f"Targeted {removal_share:.0%}: {row['Served Percent']:.3f}% "
            f"served; solver gap={100 * float(row['MIP Gap']):.3f}%",
            flush=True,
        )

    revised = pd.concat([retained, pd.DataFrame(targeted_rows)], ignore_index=True)
    revised = revised.sort_values(
        ["Unavailability Share", "Failure Mode", "Draw"], kind="stable"
    ).reset_index(drop=True)
    revised.to_csv(FAILURE_PATH, index=False)
    print(
        f"All-shelter opening case: {all_open['Served Percent']:.3f}% served; "
        f"solver gap={100 * float(all_open['MIP Gap']):.3f}%",
        flush=True,
    )
    print(f"Saved: {OPENING_PATH.relative_to(ROOT)}")
    print(f"Saved: {FAILURE_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
