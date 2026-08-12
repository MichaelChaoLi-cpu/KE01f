"""Estimate shelter-capacity thresholds without complete facility-area data.

This exploratory analysis does not impute a factual capacity for every shelter.
Instead it asks how much standardized capacity and how many general shelters would
be required to serve observed aggregate use and modeled spatial demand scenarios.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEMAND_PATH = ROOT / "data" / "processed" / "kumamoto_prefecture_shelter_demand_preprocessed.parquet"
SHELTER_AUDIT_PATH = (
    ROOT
    / "data"
    / "exp"
    / "prefecture-shelter-capacity-audit"
    / "prefecture_shelter_capacity_evidence_audit.csv"
)
SNAPSHOT_PATH = (
    ROOT
    / "data"
    / "processed"
    / "kumamoto_2026_official_shelter_use_snapshots_preprocessed.parquet"
)
OUT = ROOT / "data" / "exp" / "capacity-threshold-estimate"

CAPACITY_THRESHOLDS = (25, 50, 100, 200)


def ceil_people(value: float, capacity: int) -> int:
    """Return the number of shelters needed for fractional scenario demand."""
    return int(np.ceil(max(float(value), 0.0) / capacity - 1e-12))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    demand = pd.read_parquet(DEMAND_PATH)
    shelters = pd.read_csv(SHELTER_AUDIT_PATH, dtype={"Municipality Code": "string"})
    snapshots = pd.read_parquet(SNAPSHOT_PATH).sort_values("Observation Timestamp")

    general = shelters.loc[shelters["Shelter Service Class"].eq("general")].copy()
    welfare = shelters.loc[shelters["Shelter Service Class"].eq("welfare_specific")].copy()
    if len(general) + len(welfare) != len(shelters):
        raise ValueError("Every shelter must be classified as general or welfare-specific")

    general_count = len(general)
    if general["Municipality"].nunique() != 45:
        raise ValueError("General-shelter inventory must cover all 45 municipalities")

    # Official numeric-capacity records calibrate plausibility but are not extrapolated
    # deterministically to unsupported facilities.
    documented = general.loc[general["Official Numeric Capacity"].notna()].copy()
    documented = documented.sort_values(
        "Official Source Match Name Similarity", ascending=False
    ).drop_duplicates("Official Capacity Source Record ID")
    calibration_rows: list[dict[str, object]] = []
    for threshold in CAPACITY_THRESHOLDS:
        calibration_rows.append(
            {
                "Standardized Capacity per Shelter": threshold,
                "Official General Shelters in Calibration Sample": len(documented),
                "Calibration Municipalities": documented["Municipality"].nunique(),
                "Official Capacity Median": documented["Official Numeric Capacity"].median(),
                "Official Capacity First Quartile": documented["Official Numeric Capacity"].quantile(0.25),
                "Official Capacity Tenth Percentile": documented["Official Numeric Capacity"].quantile(0.10),
                "Official Shelters at or above Threshold": int(
                    documented["Official Numeric Capacity"].ge(threshold).sum()
                ),
                "Official Sample Share at or above Threshold (%)": 100
                * documented["Official Numeric Capacity"].ge(threshold).mean(),
                "Interpretation": "Plausibility calibration only; three-municipality sample",
            }
        )
    calibration = pd.DataFrame(calibration_rows)
    calibration.to_csv(OUT / "official_capacity_threshold_calibration.csv", index=False)

    # Evaluate each actual prefecture-wide snapshot against its reported open count.
    snapshot_rows: list[dict[str, object]] = []
    for _, snapshot in snapshots.iterrows():
        evacuees = float(snapshot["Reported Evacuees"])
        open_shelters = int(snapshot["Open Shelters"])
        for threshold in CAPACITY_THRESHOLDS:
            scenario_capacity = open_shelters * threshold
            snapshot_rows.append(
                {
                    "Observation Timestamp": snapshot["Observation Timestamp"],
                    "Hours Since Earthquake": snapshot["Hours Since Earthquake"],
                    "Reported Evacuees": evacuees,
                    "Reported Open Shelters": open_shelters,
                    "Observed Average Evacuees per Open Shelter": evacuees / open_shelters,
                    "Standardized Capacity per Open Shelter": threshold,
                    "Implied Aggregate Capacity": scenario_capacity,
                    "Aggregate Surplus or Shortfall": scenario_capacity - evacuees,
                    "Minimum Open Shelters Required": ceil_people(evacuees, threshold),
                    "Sufficient at Reported Open Count": scenario_capacity >= evacuees,
                }
            )
    snapshot_thresholds = pd.DataFrame(snapshot_rows)
    snapshot_thresholds.to_csv(OUT / "event_snapshot_capacity_thresholds.csv", index=False)

    # Build municipality totals and transparent spatializations of the largest
    # available observed-use benchmark. These are modeled distributions, never
    # municipality-level observed evacuee counts.
    municipal_demand = (
        demand.groupby(["Municipality Code", "Municipality"], as_index=False)
        .agg(
            Residential_Population=("Residential Population", "sum"),
            Housing_Loss_Central=("Housing-Loss Shelter Demand Central", "sum"),
            Housing_Loss_High=("Housing-Loss Shelter Demand High", "sum"),
        )
    )
    municipal_shelters = (
        general.groupby(["Municipality Code", "Municipality"], as_index=False)
        .size()
        .rename(columns={"size": "General Shelters"})
    )
    municipal = municipal_demand.merge(
        municipal_shelters,
        on=["Municipality Code", "Municipality"],
        how="left",
        validate="1:1",
    )
    if municipal["General Shelters"].isna().any() or municipal["General Shelters"].le(0).any():
        raise ValueError("Every municipality must have at least one general shelter")

    observed_max = float(snapshots["Reported Evacuees"].max())
    spatial_scenarios = {
        "Observed-use stress, population weighted": (
            observed_max
            * municipal["Residential_Population"]
            / municipal["Residential_Population"].sum()
        ),
        "Observed-use stress, central housing-loss weighted": (
            observed_max
            * municipal["Housing_Loss_Central"]
            / municipal["Housing_Loss_Central"].sum()
        ),
        "Observed-use stress, high housing-loss weighted": (
            observed_max
            * municipal["Housing_Loss_High"]
            / municipal["Housing_Loss_High"].sum()
        ),
        "Modeled high housing-loss demand": municipal["Housing_Loss_High"],
    }

    municipal_rows: list[pd.DataFrame] = []
    summary_rows: list[dict[str, object]] = []
    for scenario_name, scenario_demand in spatial_scenarios.items():
        frame = municipal[
            ["Municipality Code", "Municipality", "Residential_Population", "General Shelters"]
        ].copy()
        frame["Demand Scenario"] = scenario_name
        frame["Scenario Demand"] = np.asarray(scenario_demand, dtype=float)
        frame["Observed Municipality Demand"] = False
        frame["Required Capacity if All General Shelters Open"] = (
            frame["Scenario Demand"] / frame["General Shelters"]
        )
        for threshold in CAPACITY_THRESHOLDS:
            required_col = f"Minimum Open Shelters Required at {threshold} Persons"
            feasible_col = f"Locally Feasible at {threshold} Persons"
            frame[required_col] = frame["Scenario Demand"].map(
                lambda value: ceil_people(value, threshold)
            )
            frame[feasible_col] = frame[required_col].le(frame["General Shelters"])

            infeasible = ~frame[feasible_col]
            summary_rows.append(
                {
                    "Demand Scenario": scenario_name,
                    "Scenario Demand": frame["Scenario Demand"].sum(),
                    "Standardized Capacity per Shelter": threshold,
                    "Minimum Open Shelters Required with Municipality Containment": int(
                        frame[required_col].sum()
                    ),
                    "Share of General Inventory Required (%)": 100
                    * frame[required_col].sum()
                    / general_count,
                    "Municipalities Infeasible without Cross-Border Assignment": int(infeasible.sum()),
                    "Demand in Infeasible Municipalities": frame.loc[infeasible, "Scenario Demand"].sum(),
                    "Maximum Municipality Required Capacity per Shelter": frame[
                        "Required Capacity if All General Shelters Open"
                    ].max(),
                }
            )
        municipal_rows.append(frame)

    municipality_thresholds = pd.concat(municipal_rows, ignore_index=True)
    municipality_thresholds.to_csv(OUT / "municipality_capacity_thresholds.csv", index=False)
    municipality_thresholds.to_parquet(
        OUT / "municipality_capacity_thresholds.parquet", index=False
    )
    scenario_summary = pd.DataFrame(summary_rows)
    scenario_summary.to_csv(OUT / "spatial_scenario_threshold_summary.csv", index=False)

    # Reverse solve the smallest integer capacity that can serve each spatial
    # scenario using no more than the 415 shelters reported open at the largest
    # available observed-use snapshot, while retaining residents within their
    # municipality for this conservative first screen.
    observed_scale_open_count = int(
        snapshots.loc[snapshots["Reported Evacuees"].idxmax(), "Open Shelters"]
    )
    critical_rows: list[dict[str, object]] = []
    for scenario_name in spatial_scenarios:
        frame = municipality_thresholds.loc[
            municipality_thresholds["Demand Scenario"].eq(scenario_name)
        ].copy()
        solution: dict[str, object] | None = None
        for capacity in range(1, 5001):
            needed = np.ceil(frame["Scenario Demand"] / capacity - 1e-12).astype(int)
            locally_feasible = needed.le(frame["General Shelters"])
            if locally_feasible.all() and int(needed.sum()) <= observed_scale_open_count:
                pressure_index = frame[
                    "Required Capacity if All General Shelters Open"
                ].idxmax()
                solution = {
                    "Demand Scenario": scenario_name,
                    "Scenario Demand": frame["Scenario Demand"].sum(),
                    "Observed-Scale Open Shelter Limit": observed_scale_open_count,
                    "Critical Integer Capacity per Open Shelter": capacity,
                    "Minimum Open Shelters at Critical Capacity": int(needed.sum()),
                    "Unused Opening Slots at Critical Capacity": observed_scale_open_count
                    - int(needed.sum()),
                    "Maximum Municipality Required Capacity if All Local Shelters Open": frame[
                        "Required Capacity if All General Shelters Open"
                    ].max(),
                    "Binding or Highest-Pressure Municipality": frame.loc[
                        pressure_index, "Municipality"
                    ],
                    "Interpretation": (
                        "Modeled reverse requirement with municipality containment; "
                        "not observed facility capacity"
                    ),
                }
                break
        if solution is None:
            raise ValueError(f"No critical capacity solution found for {scenario_name}")
        critical_rows.append(solution)
    critical = pd.DataFrame(critical_rows)
    critical.to_csv(OUT / "critical_capacity_at_observed_open_scale.csv", index=False)

    # A compact pressure ranking is easier to inspect than the full wide table.
    pressure = municipality_thresholds[
        [
            "Demand Scenario",
            "Municipality Code",
            "Municipality",
            "General Shelters",
            "Scenario Demand",
            "Required Capacity if All General Shelters Open",
        ]
    ].copy()
    pressure["Pressure Rank"] = pressure.groupby("Demand Scenario")[
        "Required Capacity if All General Shelters Open"
    ].rank(method="min", ascending=False).astype(int)
    pressure.sort_values(["Demand Scenario", "Pressure Rank"]).to_csv(
        OUT / "municipality_required_capacity_pressure_ranking.csv", index=False
    )

    readme = OUT / "README.md"
    readme.write_text(
        f"""# Prefecture shelter-capacity threshold estimate

This exploratory estimate avoids unsupported facility-area imputation. It evaluates
standardized capacities of {', '.join(map(str, CAPACITY_THRESHOLDS))} persons per general
shelter and calculates the reverse requirement: the minimum capacity and minimum number
of open shelters needed to serve each demand scenario.

- General designated shelters: {general_count:,}
- Welfare-specific shelters kept outside general supply: {len(welfare):,}
- General shelters with deduplicated official numeric capacity: {len(documented):,}
- Sum of documented general capacity in the three source municipalities: {documented['Official Numeric Capacity'].sum():,.0f}
- Median documented capacity: {documented['Official Numeric Capacity'].median():,.0f}
- Highest observed prefecture-wide use in the available 0-72 h reports: {observed_max:,.0f}

The three 10,467-person municipality distributions are sensitivity scenarios weighted
by population, central housing-loss demand, and high housing-loss demand. They are not
observed municipal evacuee counts. Municipality-contained results are a conservative
screen before cross-boundary network assignment. Official capacity values calibrate the
plausibility of thresholds but are not deterministically imputed to other shelters.
""",
        encoding="utf-8",
    )

    highest = snapshots.loc[snapshots["Reported Evacuees"].idxmax()]
    print(
        "Highest observed snapshot: "
        f"{highest['Reported Evacuees']:,.0f} evacuees / {highest['Open Shelters']:.0f} open "
        f"= {highest['Reported Evacuees'] / highest['Open Shelters']:.2f} people per open shelter"
    )
    print("\nSnapshot threshold result at highest observed use:")
    print(
        snapshot_thresholds.loc[
            snapshot_thresholds["Reported Evacuees"].eq(observed_max),
            [
                "Standardized Capacity per Open Shelter",
                "Implied Aggregate Capacity",
                "Aggregate Surplus or Shortfall",
                "Minimum Open Shelters Required",
                "Sufficient at Reported Open Count",
            ],
        ].to_string(index=False)
    )
    print("\nSpatial scenario summary:")
    print(scenario_summary.to_string(index=False))
    print("\nCritical reverse capacity at the 415-open-shelter scale:")
    print(
        critical[
            [
                "Demand Scenario",
                "Critical Integer Capacity per Open Shelter",
                "Minimum Open Shelters at Critical Capacity",
                "Binding or Highest-Pressure Municipality",
            ]
        ].to_string(index=False)
    )
    print(f"\nWrote threshold estimates to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
