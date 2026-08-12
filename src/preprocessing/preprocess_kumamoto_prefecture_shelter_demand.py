"""Assign prefecture-wide earthquake-related shelter demand to municipalities.

The upstream housing-loss estimates remain unchanged.  This script adds official
administrative reporting strata and creates a capacity-evidence acquisition priority
that combines central demand with the share of general shelters lacking numeric or
area evidence.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from shapely import wkb
from shapely.strtree import STRtree


ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "data" / "raw" / "prior_projects"
INPUT = PRIOR / "KE01" / "kumamoto_grid_exposure_estimates_preprocessed.parquet"
ADMIN = PRIOR / "KE01b" / "kumamoto_administrative_areas_preprocessed.parquet"
EVIDENCE = (
    ROOT
    / "data"
    / "exp"
    / "prefecture-shelter-capacity-audit"
    / "municipality_capacity_evidence_summary.csv"
)
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "data" / "exp" / "prefecture-shelter-capacity-audit"


def decode_geometry(value: object):
    if isinstance(value, (bytes, bytearray, memoryview)):
        return wkb.loads(bytes(value))
    return value


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    source = pd.read_parquet(INPUT)
    admin = pd.read_parquet(ADMIN).copy()
    admin_geometries = admin["Geometry"].map(decode_geometry).tolist()
    tree = STRtree(admin_geometries)

    assignments: list[dict[str, object]] = []
    decoded_demand_geometry = source["geometry"].map(decode_geometry)
    for geometry in decoded_demand_geometry:
        point = geometry.representative_point()
        candidates = tree.query(point, predicate="intersects")
        if len(candidates) == 0:
            nearest_index = int(tree.query_nearest(point)[0])
            selected = admin.iloc[nearest_index]
            method = "nearest_admin_polygon"
        else:
            selected = admin.iloc[int(candidates[0])]
            method = "representative_point_intersection"
        assignments.append(
            {
                "Municipality Code": (
                    "43100"
                    if str(selected["Municipality Name"]) == "熊本市"
                    else str(selected["Municipality Code"])
                ),
                "Administrative Polygon Code": str(selected["Municipality Code"]),
                "Municipality": selected["Municipality Name"],
                "Ward": selected["Ward Name"],
                "Municipality Label": selected["Municipality Label"],
                "Administrative Assignment Method": method,
            }
        )
    assigned = pd.DataFrame(assignments)

    demand = pd.DataFrame(
        {
            "Residential Demand Unit ID": source["Disclosure Group Code"],
            "Constituent 125 m Mesh Count": source["Disclosure Group Size"],
            "Municipality Code": assigned["Municipality Code"],
            "Administrative Polygon Code": assigned["Administrative Polygon Code"],
            "Municipality": assigned["Municipality"],
            "Ward": assigned["Ward"],
            "Municipality Label": assigned["Municipality Label"],
            "Administrative Assignment Method": assigned["Administrative Assignment Method"],
            "Residential Population": source["Total Population"],
            "Population Age 65+": source["Population Age 65+"],
            "Epicentral Distance (km)": source["Epicentral Distance km"],
            "Housing-Loss Shelter Demand Low": source[
                "Estimated Affected Population Lower Bound"
            ],
            "Housing-Loss Shelter Demand Central": source["Estimated Affected Population"],
            "Housing-Loss Shelter Demand High": source[
                "Estimated Affected Population Upper Bound"
            ],
            "Housing-Loss Shelter Demand Age 65+ Central": source[
                "Estimated Affected Population Age 65+"
            ],
            "Geometry": source["geometry"],
        }
    )

    if demand["Municipality"].isna().any():
        raise ValueError("All demand units must receive a municipality")
    if demand["Municipality"].nunique() != 45:
        raise ValueError(f"Expected 45 municipalities, found {demand['Municipality'].nunique()}")
    for new, old in [
        ("Housing-Loss Shelter Demand Low", "Estimated Affected Population Lower Bound"),
        ("Housing-Loss Shelter Demand Central", "Estimated Affected Population"),
        ("Housing-Loss Shelter Demand High", "Estimated Affected Population Upper Bound"),
    ]:
        if abs(float(demand[new].sum()) - float(source[old].sum())) > 1e-8:
            raise ValueError(f"Prefecture total changed for {new}")

    target = PROCESSED / "kumamoto_prefecture_shelter_demand_preprocessed.parquet"
    demand.to_parquet(target, index=False)

    municipal = (
        demand.groupby(["Municipality Code", "Municipality"], as_index=False)
        .agg(
            Residential_Demand_Units=("Residential Demand Unit ID", "size"),
            Residential_Population=("Residential Population", "sum"),
            Minimum_Epicentral_Distance_km=("Epicentral Distance (km)", "min"),
            Demand_Low=("Housing-Loss Shelter Demand Low", "sum"),
            Demand_Central=("Housing-Loss Shelter Demand Central", "sum"),
            Demand_High=("Housing-Loss Shelter Demand High", "sum"),
            Demand_Age_65_Plus_Central=("Housing-Loss Shelter Demand Age 65+ Central", "sum"),
        )
    )
    evidence = pd.read_csv(EVIDENCE, dtype={"Municipality Code": "string"})
    priority = municipal.merge(
        evidence,
        on=["Municipality Code", "Municipality"],
        how="left",
        validate="1:1",
    )
    coverage = priority["General_Capacity_Evidence_Coverage_Percent"].fillna(0) / 100
    priority["Capacity_Evidence_Gap_Weighted_Central_Demand"] = (
        priority["Demand_Central"] * (1 - coverage)
    )
    priority["Source_Acquisition_Priority_Rank"] = priority[
        "Capacity_Evidence_Gap_Weighted_Central_Demand"
    ].rank(method="min", ascending=False).astype(int)
    priority = priority.sort_values(
        ["Source_Acquisition_Priority_Rank", "Minimum_Epicentral_Distance_km"]
    )
    priority.to_csv(OUT / "municipality_demand_and_capacity_evidence_priority.csv", index=False)

    print(
        priority[
            [
                "Source_Acquisition_Priority_Rank",
                "Municipality",
                "Demand_Central",
                "Demand_High",
                "General_Shelters",
                "General_Capacity_Evidence_Coverage_Percent",
                "Capacity_Evidence_Gap_Weighted_Central_Demand",
            ]
        ]
        .head(15)
        .to_string(index=False)
    )
    print(f"\nWrote {len(demand):,} demand units to {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
