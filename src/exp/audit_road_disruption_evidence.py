"""Audit whether available road evidence supports pedestrian edge removal."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "data" / "raw" / "prior_projects"
EDGES_PATH = PRIOR / "KE01d" / "kumamoto_routable_road_edges_preprocessed.parquet"
RESTRICTIONS_PATH = PRIOR / "KE01e" / "road_restrictions_preprocessed.parquet"
MATCHES_PATH = PRIOR / "KE01e" / "road_restriction_edge_matches_preprocessed.parquet"
OUT = ROOT / "data" / "exp" / "road-disruption-evidence-audit"

EARTHQUAKE_TIME = pd.Timestamp("2026-07-28 16:27:00", tz="Asia/Tokyo")
END_72H = EARTHQUAKE_TIME + pd.Timedelta(hours=72)
EXPRESSWAY_CATEGORY = "National Expressway or Equivalent"
FREE_TOLL_CATEGORY = "Free"


def active_full_closure(status: pd.Series) -> pd.Series:
    text = status.astype("string")
    return text.str.contains("通行止", na=False) & ~text.str.contains("解除", na=False)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    edges = pd.read_parquet(EDGES_PATH)
    restrictions = pd.read_parquet(RESTRICTIONS_PATH).reset_index(drop=True)
    matches = pd.read_parquet(MATCHES_PATH)
    restrictions["Restriction Observation ID"] = [
        f"RR-{index:06d}" for index in range(1, len(restrictions) + 1)
    ]
    restrictions["Resolved Restriction Status"] = (
        restrictions["Restriction Status"]
        .astype("string")
        .combine_first(restrictions["Restriction Start Status"].astype("string"))
    )

    walking = edges.loc[
        edges["Network Analysis Eligible"].fillna(False)
        & edges["Road Available"].fillna(False)
        & edges["Road Category"].ne(EXPRESSWAY_CATEGORY)
        & edges["Toll Category"].eq(FREE_TOLL_CATEGORY)
    ].copy()
    walking_ids = set(walking["Road Edge ID"].astype(str))
    walking_length = float(walking["Road Length (m)"].sum())

    within_72h = restrictions.loc[
        restrictions["Snapshot Time"].between(EARTHQUAKE_TIME, END_72H)
    ].copy()
    latest_time = within_72h["Snapshot Time"].max()
    latest = within_72h.loc[within_72h["Snapshot Time"].eq(latest_time)].copy()
    latest_kumamoto = latest.loc[latest["Prefecture Name"].eq("熊本県")].copy()
    latest_kumamoto["Active Full Closure"] = active_full_closure(
        latest_kumamoto["Resolved Restriction Status"]
    )
    latest_active = latest_kumamoto.loc[
        latest_kumamoto["Active Full Closure"]
    ].copy()
    latest_active_ids = set(latest_active["Restriction Observation ID"])

    snapshot_frame = restrictions.assign(
        Kumamoto_Prefecture=restrictions["Prefecture Name"].eq("熊本県"),
        Active_Full_Closure=active_full_closure(
            restrictions["Resolved Restriction Status"]
        ),
    )
    snapshot_frame["Kumamoto Active Full Closure"] = (
        snapshot_frame["Kumamoto_Prefecture"]
        & snapshot_frame["Active_Full_Closure"]
    )
    snapshot_summary = (
        snapshot_frame
        .groupby("Snapshot Time", as_index=False)
        .agg(
            All_Observations=("Restriction Observation ID", "count"),
            Named_Kumamoto_Observations=("Kumamoto_Prefecture", "sum"),
            Named_Kumamoto_Active_Full_Closures=(
                "Kumamoto Active Full Closure",
                "sum",
            ),
        )
    )
    snapshot_summary["Within First 72 Hours"] = snapshot_summary[
        "Snapshot Time"
    ].between(EARTHQUAKE_TIME, END_72H)
    snapshot_summary.to_csv(OUT / "restriction_snapshot_summary.csv", index=False)

    reason_summary = (
        latest_active.groupby(
            ["Restriction Reason", "Resolved Restriction Status"],
            dropna=False,
            observed=True,
        )
        .size()
        .rename("Restriction Observations")
        .reset_index()
        .sort_values("Restriction Observations", ascending=False)
    )
    reason_summary.to_csv(OUT / "latest_72h_restriction_reason_summary.csv", index=False)

    latest_matches = matches.loc[
        matches["Restriction Observation ID"].isin(latest_active_ids)
        & matches["Matched Road Edge ID"].astype("string").isin(walking_ids)
        & matches["Road Edge Match Status"].eq("matched_primary")
    ].copy()
    latest_matches["Route Agreement Not False"] = ~latest_matches[
        "Route Name Agreement"
    ].eq(False).fillna(False)

    rules = {
        "Published 50 m candidate buffer": np.ones(len(latest_matches), dtype=bool),
        "Candidate distance <= 10 m": latest_matches[
            "Road Edge Match Distance (m)"
        ].le(10),
        "Candidate distance <= 5 m": latest_matches[
            "Road Edge Match Distance (m)"
        ].le(5),
        "Candidate distance <= 1 m": latest_matches[
            "Road Edge Match Distance (m)"
        ].le(1),
        "<= 5 m and route agreement not false": latest_matches[
            "Road Edge Match Distance (m)"
        ].le(5)
        & latest_matches["Route Agreement Not False"],
    }
    nearest_index = (
        latest_matches.sort_values(
            [
                "Restriction Observation ID",
                "Road Edge Match Distance (m)",
                "Matched Road Edge ID",
            ]
        )
        .drop_duplicates("Restriction Observation ID")
        .index
    )
    nearest_mask = latest_matches.index.isin(nearest_index)
    rules["Single nearest walking edge per restriction"] = nearest_mask

    edge_lookup = walking.set_index("Road Edge ID")["Road Length (m)"]
    match_rows: list[dict[str, object]] = []
    for rule, mask in rules.items():
        selected = latest_matches.loc[np.asarray(mask)]
        selected_edges = selected["Matched Road Edge ID"].dropna().astype(str).unique()
        selected_length = float(edge_lookup.reindex(selected_edges).fillna(0).sum())
        match_rows.append(
            {
                "Rule": rule,
                "Matched Restriction Observations": selected[
                    "Restriction Observation ID"
                ].nunique(),
                "Candidate Rows": len(selected),
                "Unique Walking Edges": len(selected_edges),
                "Selected Walking-Edge Length (m)": selected_length,
                "Share of Walking-Network Length (%)": (
                    100 * selected_length / walking_length
                ),
                "Pedestrian Impassability Identified": False,
                "Interpretation": (
                    "Spatial footprint sensitivity only; the official status is a "
                    "motor-vehicle restriction and does not establish pedestrian closure."
                ),
            }
        )
    match_rule_summary = pd.DataFrame(match_rows)
    match_rule_summary.to_csv(OUT / "edge_match_rule_sensitivity.csv", index=False)

    evidence_inventory = pd.DataFrame(
        [
            {
                "Evidence": "Official event road restrictions",
                "Rows or Features": len(restrictions),
                "Observed or Derived": "Observed administrative traffic restriction",
                "Event Specific": True,
                "Supports Motor-Vehicle Restriction": True,
                "Supports Pedestrian Impassability": False,
                "Use Decision": "Appendix contextual sensitivity only",
                "Reason": (
                    "Status and cause are reported, but no pedestrian prohibition or "
                    "walkability field is present."
                ),
            },
            {
                "Evidence": "Restriction-to-road-edge candidates",
                "Rows or Features": len(matches),
                "Observed or Derived": "Derived many-to-many spatial candidates",
                "Event Specific": True,
                "Supports Motor-Vehicle Restriction": False,
                "Supports Pedestrian Impassability": False,
                "Use Decision": "Matching uncertainty audit only",
                "Reason": (
                    "A 50 m line buffer returns many candidate edges; match status "
                    "explicitly does not imply closure."
                ),
            },
            {
                "Evidence": "Baseline road availability flags",
                "Rows or Features": len(edges),
                "Observed or Derived": "Derived baseline network eligibility",
                "Event Specific": False,
                "Supports Motor-Vehicle Restriction": False,
                "Supports Pedestrian Impassability": False,
                "Use Decision": "Retain for baseline network only",
                "Reason": "Every edge is marked available and eligible; this is not a post-event state.",
            },
            {
                "Evidence": "Landslide warning-zone exposure",
                "Rows or Features": int(edges["Hazard Exposure Class"].notna().sum()),
                "Observed or Derived": "Derived warning-zone intersection",
                "Event Specific": False,
                "Supports Motor-Vehicle Restriction": False,
                "Supports Pedestrian Impassability": False,
                "Use Decision": "Hazard context, not deterministic edge deletion",
                "Reason": "Warning-zone exposure is scenario risk, not observed earthquake failure.",
            },
            {
                "Evidence": "Bridge or elevated road-state class",
                "Rows or Features": int(edges["Road State"].eq("Bridge or Elevated").sum()),
                "Observed or Derived": "Baseline structural class",
                "Event Specific": False,
                "Supports Motor-Vehicle Restriction": False,
                "Supports Pedestrian Impassability": False,
                "Use Decision": "Structural descriptor only",
                "Reason": "Bridge/elevated classification does not report damage or closure.",
            },
        ]
    )
    evidence_inventory.to_csv(OUT / "road_evidence_inventory.csv", index=False)

    candidate_counts = matches.groupby("Restriction Observation ID")[
        "Road Edge Match Candidate Count"
    ].first()
    readme = f"""# Road disruption evidence audit

## Decision

The available evidence does **not** justify deleting road edges in the main
pedestrian-access model. Official records describe motor-vehicle traffic
restrictions and causes, but contain no pedestrian-prohibition, sidewalk,
walkability, or passability field. Road disruption may be shown only as a
clearly labelled appendix sensitivity based on alternative spatial-match rules.

## Evidence scale

- Official restrictions: {len(restrictions):,} snapshot observations across {restrictions['Snapshot Time'].nunique():,} snapshots.
- Named Kumamoto Prefecture observations: {int(restrictions['Prefecture Name'].eq('熊本県').sum()):,}.
- Latest snapshot within 72 hours: {latest_time.isoformat()}.
- Named Kumamoto observations at that snapshot: {len(latest_kumamoto):,}.
- Active full-closure observations at that snapshot: {len(latest_active):,}.
- Restriction-edge candidate table: {len(matches):,} rows; median {candidate_counts.median():.0f} and maximum {candidate_counts.max():.0f} candidate edges per restriction observation.
- Baseline pedestrian-screened network: {len(walking):,} edge records.

Missing-prefecture records in the first 72 hours are expressway observations.
Expressways and toll edges are already excluded from the pedestrian-screened
baseline, so they do not provide an additional walking-network disruption state.

## Interpretation

`Road Available` and `Network Analysis Eligible` are baseline construction
flags; all {len(edges):,} routable edge records are true. `Hazard Exposure Class`
is warning-zone overlap and `Road State` is a structural class. Neither is an
observed failure indicator. Restriction-edge matches are candidate spatial links,
not confirmed closures, and the published 50 m buffer is many-to-many.

The defensible main specification therefore retains the pedestrian-screened
baseline network and reports facility unavailability, walking thresholds, and
capacity sensitivity as the principal robustness analyses. If a road appendix
is retained, it must be titled motor-vehicle-restriction-footprint sensitivity,
show multiple match rules, and must not be described as observed pedestrian
inaccessibility.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    print(readme)
    print("\nEdge-match rule sensitivity")
    print(match_rule_summary.to_string(index=False))
    print("\nLatest restriction reasons")
    print(reason_summary.to_string(index=False))


if __name__ == "__main__":
    main()
