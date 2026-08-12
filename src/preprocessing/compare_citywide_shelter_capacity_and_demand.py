"""Create a preliminary citywide capacity-demand comparison matrix."""

from __future__ import annotations

from itertools import product
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CAPACITY_INPUT = ROOT / "data/processed/kumamoto_shelter_capacity_scenarios_preprocessed.parquet"
DEMAND_INPUT = ROOT / "data/processed/kumamoto_shelter_demand_scenarios_preprocessed.parquet"
OUTPUT = ROOT / "data/exp/shelter-capacity-audit/citywide_capacity_demand_comparison.csv"
OBSERVED_REPORTED_EVACUEES = 2_344.0


def main() -> None:
    capacity = pd.read_parquet(CAPACITY_INPUT)
    demand = pd.read_parquet(DEMAND_INPUT)
    capacity_columns = {
        "Safe Spacious": "Safe Spacious Capacity (persons)",
        "Central": "Central Capacity (persons)",
        "Emergency Compact": "Emergency Compact Capacity (persons)",
    }
    demand_values = {
        "Housing-Loss Low": float(demand["Housing-Loss Shelter Demand Low"].sum()),
        "Housing-Loss Central": float(demand["Housing-Loss Shelter Demand Central"].sum()),
        "Housing-Loss High": float(demand["Housing-Loss Shelter Demand High"].sum()),
        "Observed Use Benchmark": OBSERVED_REPORTED_EVACUEES,
    }

    rows = []
    for capacity_scenario, demand_scenario in product(capacity_columns, demand_values):
        available = int(capacity[capacity_columns[capacity_scenario]].sum())
        needed = demand_values[demand_scenario]
        rows.append(
            {
                "Capacity Scenario": capacity_scenario,
                "Demand Scenario": demand_scenario,
                "Known-Source Capacity (persons)": available,
                "Shelter Demand or Observed Use (persons)": needed,
                "Capacity Minus Demand (persons)": available - needed,
                "Capacity-Demand Ratio": available / needed if needed > 0 else float("inf"),
                "Unmet Demand (persons)": max(0.0, needed - available),
                "Interpretation Scope": (
                    "observed citywide shelter use; spatial distribution unavailable"
                    if demand_scenario == "Observed Use Benchmark"
                    else "scenario-based housing-loss shelter demand"
                ),
            }
        )

    result = pd.DataFrame(rows)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(result)} comparisons to {OUTPUT.relative_to(ROOT)}")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
