#!/usr/bin/env python3
"""Network Adequacy and Robustness.

Plan: Summarize the primary network-allocation result and its most informative
demand, walking, capacity, facility-loss, and single-shelter sensitivities in a
paper-ready table.
Framework: Sections 5-7 use network reachability followed by capacity-constrained
allocation and interpret service loss under facility failure as model sensitivity,
not observed denial of shelter access.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.page import PageMargins
from openpyxl.worksheet.table import Table, TableStyleInfo


ROOT = Path(__file__).resolve().parents[2]
DEMAND_ACCESS_PATH = ROOT / "data/exp/shelter-robustness/demand_access_sensitivity.csv"
CAPACITY_PATH = (
    ROOT
    / "data/exp/primary-capacity-constrained-allocation/capacity_threshold_sensitivity.csv"
)
FACILITY_PATH = ROOT / "data/exp/shelter-robustness/facility_unavailability_sensitivity.csv"
RANDOM_PATH = ROOT / "data/exp/shelter-robustness/facility_unavailability_random_summary.csv"
CRITICAL_PATH = ROOT / "data/exp/shelter-robustness/critical_single_shelter_loss.csv"
PRIMARY_SUMMARY_PATH = (
    ROOT
    / "data/exp/primary-capacity-constrained-allocation/primary_model_summary.csv"
)
PRIMARY_MUNICIPALITY_PATH = (
    ROOT
    / "data/exp/primary-capacity-constrained-allocation/primary_municipality_capacity_constrained_results.csv"
)
PRIMARY_OPENINGS_PATH = (
    ROOT
    / "data/exp/primary-capacity-constrained-allocation/primary_modeled_shelter_openings.csv"
)
OUTPUT_PATH = ROOT / "data/results/tables/Table_network_adequacy_and_robustness.xlsx"
SHEET_NAME = "Network Robustness"
TABLE_TITLE = "Network Adequacy and Robustness"

ENGLISH_CRITICAL_SHELTER_NAMES = {
    "E4321300034111": "Toyofuku Elementary School Gymnasium (Uki)",
    "E4321300010111": "Uki City Ogawa Disaster Prevention Base Center (Uki)",
    "E4321300011111": "Ogawa General Cultural Center Rapport (Uki)",
    "E4320200016111": "Kagami Elementary School (Yatsushiro)",
    "E4320200004111": "Matsutaka Elementary School (Yatsushiro)",
}

ENGLISH_MUNICIPALITY_NAMES = {
    "43100": "Kumamoto City",
    "43202": "Yatsushiro",
    "43211": "Uto",
    "43213": "Uki",
    "43468": "Hikawa",
}

COLUMNS = [
    "Evidence Block",
    "Scenario",
    "Demand Geography",
    "Walking Speed (km/h)",
    "Time Threshold (min)",
    "Capacity per Shelter",
    "Maximum Open Shelters",
    "Facility Unavailability",
    "Available / Modeled Open Shelters",
    "Reachable Demand (%)",
    "Served Demand (%)",
    "Unmet Demand",
    "Served-Demand Change from Primary",
    "Interpretation / Solution Status",
]


def row_template() -> dict[str, object]:
    return {column: None for column in COLUMNS}


def solution_note(proven_optimal: object) -> str:
    return "Proven optimal" if bool(proven_optimal) else "Time-limit incumbent; interpret as a lower bound"


def build_table() -> pd.DataFrame:
    access = pd.read_csv(DEMAND_ACCESS_PATH)
    capacity = pd.read_csv(CAPACITY_PATH)
    facility = pd.read_csv(FACILITY_PATH)
    random = pd.read_csv(RANDOM_PATH)
    critical = pd.read_csv(CRITICAL_PATH)
    primary_summary = pd.read_csv(PRIMARY_SUMMARY_PATH)
    municipality = pd.read_csv(
        PRIMARY_MUNICIPALITY_PATH, dtype={"Municipality Code": str}
    )
    primary_openings = pd.read_csv(PRIMARY_OPENINGS_PATH)
    if primary_summary.shape[0] != 1:
        raise RuntimeError("Expected exactly one primary model-summary row.")
    baseline_served = float(primary_summary.loc[0, "Final Served Demand"])
    scenario_demand = float(primary_summary.loc[0, "Scenario Demand"])
    shelter_inventory = int(primary_openings.shape[0])
    if shelter_inventory != 1156:
        raise RuntimeError(
            f"Expected 1,156 general shelters, found {shelter_inventory}."
        )
    rows: list[dict[str, object]] = []

    access_labels = {
        "population_weighted": "Population-weighted demand",
        "central_loss_weighted": "Central-loss-weighted demand",
        "high_loss_weighted": "Primary: high-loss-weighted demand",
        "10min_3kmh": "10 min at 3 km/h",
        "15min_3kmh": "15 min at 3 km/h",
        "30min_3kmh": "30 min at 3 km/h",
        "10min_4kmh": "10 min at 4 km/h",
        "30min_4kmh": "30 min at 4 km/h",
    }
    selected_access_scenarios = {
        "population_weighted",
        "central_loss_weighted",
        "high_loss_weighted",
        "10min_4kmh",
        "15min_3kmh",
        "30min_4kmh",
    }
    selected_access = access.loc[access["Scenario"].isin(selected_access_scenarios)]
    if selected_access.shape[0] != 6:
        raise RuntimeError("Expected six selected demand-geography and walking rows.")
    for _, source in selected_access.iterrows():
        row = row_template()
        scenario = str(source["Scenario"])
        row.update(
            {
                "Evidence Block": (
                    "Primary / demand geography"
                    if source["Sensitivity Dimension"] == "Demand geography"
                    else "Walking-access sensitivity"
                ),
                "Scenario": access_labels[scenario],
                "Demand Geography": (
                    scenario.replace("_weighted", "").replace("_", " ")
                    if source["Sensitivity Dimension"] == "Demand geography"
                    else "high loss weighted"
                ),
                "Walking Speed (km/h)": source["Walking Speed (km/h)"],
                "Time Threshold (min)": source["Time Threshold (min)"],
                "Capacity per Shelter": source["Capacity per Open Shelter"],
                "Maximum Open Shelters": source["Maximum Open Shelters"],
                "Facility Unavailability": "None",
                "Available / Modeled Open Shelters": shelter_inventory,
                "Reachable Demand (%)": source["Reachable Percent"],
                "Served Demand (%)": source["Served Percent"],
                "Unmet Demand": source["Unmet Demand"],
                "Served-Demand Change from Primary": source["Maximum Served Demand"]
                - baseline_served,
                "Interpretation / Solution Status": solution_note(source["Proven Optimal"]),
            }
        )
        rows.append(row)

    selected_capacity = capacity.loc[
        ((capacity["Maximum Open Shelters"] == 415) & (capacity["Capacity per Open Shelter"] != 50))
        | ((capacity["Maximum Open Shelters"] == shelter_inventory) & (capacity["Capacity per Open Shelter"] == 100))
    ]
    if selected_capacity.shape[0] != 4:
        raise RuntimeError("Expected four selected capacity/opening rows.")
    for _, source in selected_capacity.iterrows():
        all_available = int(source["Maximum Open Shelters"]) == shelter_inventory
        row = row_template()
        row.update(
            {
                "Evidence Block": "Capacity / opening sensitivity",
                "Scenario": (
                    f"{int(source['Capacity per Open Shelter'])} persons; "
                    + ("all shelters available" if all_available else "maximum 415 open")
                ),
                "Demand Geography": "high loss weighted",
                "Walking Speed (km/h)": 4.0,
                "Time Threshold (min)": 15.0,
                "Capacity per Shelter": source["Capacity per Open Shelter"],
                "Maximum Open Shelters": source["Maximum Open Shelters"],
                "Facility Unavailability": "None",
                "Available / Modeled Open Shelters": shelter_inventory,
                "Reachable Demand (%)": 100
                * source["Geographically Reachable Demand"]
                / source["Scenario Demand"],
                "Served Demand (%)": source["Served Percent"],
                "Unmet Demand": source["Unmet Demand"],
                "Served-Demand Change from Primary": source["Maximum Served Demand"]
                - baseline_served,
                "Interpretation / Solution Status": solution_note(source["Proven Optimal"]),
            }
        )
        rows.append(row)

    selected_random = random.loc[random["Unavailability Share"].isin([0.1, 0.3])]
    if selected_random.shape[0] != 2:
        raise RuntimeError("Expected random 10% and 30% unavailability summaries.")
    for _, source in selected_random.iterrows():
        share = float(source["Unavailability Share"])
        row = row_template()
        row.update(
            {
                "Evidence Block": "Facility-unavailability sensitivity",
                "Scenario": f"Random {int(share * 100)}% loss; mean of {int(source['Draws'])} draws",
                "Demand Geography": "high loss weighted",
                "Walking Speed (km/h)": 4.0,
                "Time Threshold (min)": 15.0,
                "Capacity per Shelter": 50.0,
                "Maximum Open Shelters": 415,
                "Facility Unavailability": f"Random {int(share * 100)}%",
                "Available / Modeled Open Shelters": round(
                    shelter_inventory * (1 - share)
                ),
                "Reachable Demand (%)": None,
                "Served Demand (%)": source["Mean_Served_Percent"],
                "Unmet Demand": scenario_demand - source["Mean_Served_Demand"],
                "Served-Demand Change from Primary": -source["Mean_Service_Loss"],
                "Interpretation / Solution Status": "Mean across reproducible random draws",
            }
        )
        rows.append(row)

    targeted = facility.loc[facility["Failure Mode"] == "targeted_high_reachable_pressure"]
    for _, source in targeted.iterrows():
        share = float(source["Unavailability Share"])
        row = row_template()
        row.update(
            {
                "Evidence Block": "Facility-unavailability sensitivity",
                "Scenario": f"Targeted removal of highest-pressure {int(share * 100)}%",
                "Demand Geography": "high loss weighted",
                "Walking Speed (km/h)": 4.0,
                "Time Threshold (min)": 15.0,
                "Capacity per Shelter": 50.0,
                "Maximum Open Shelters": 415,
                "Facility Unavailability": f"Targeted {int(share * 100)}%",
                "Available / Modeled Open Shelters": source["Available Shelters"],
                "Reachable Demand (%)": None,
                "Served Demand (%)": source["Served Percent"],
                "Unmet Demand": source["Unmet Demand"],
                "Served-Demand Change from Primary": -source["Service Loss from Baseline"],
                "Interpretation / Solution Status": solution_note(source["Proven Optimal"]),
            }
        )
        rows.append(row)

    municipality = municipality.sort_values(
        ["Unmet_Demand", "Municipality Code"], ascending=[False, True]
    ).head(5)
    if municipality.shape[0] != 5:
        raise RuntimeError("Expected five high-unmet-demand municipalities.")
    for rank, (_, source) in enumerate(municipality.iterrows(), start=1):
        municipality_name = ENGLISH_MUNICIPALITY_NAMES.get(
            str(source["Municipality Code"])
        )
        if municipality_name is None:
            raise RuntimeError(
                f"Missing English municipality name for {source['Municipality Code']}."
            )
        row = row_template()
        row.update(
            {
                "Evidence Block": "Municipality primary gaps",
                "Scenario": f"{rank}. {municipality_name}",
                "Demand Geography": "high loss weighted",
                "Walking Speed (km/h)": 4.0,
                "Time Threshold (min)": 15.0,
                "Capacity per Shelter": 50.0,
                "Maximum Open Shelters": 415,
                "Facility Unavailability": "None",
                "Available / Modeled Open Shelters": source[
                    "Modeled_Open_Shelters"
                ],
                "Reachable Demand (%)": None,
                "Served Demand (%)": source["Served Percent"],
                "Unmet Demand": source["Unmet_Demand"],
                "Served-Demand Change from Primary": None,
                "Interpretation / Solution Status": (
                    f"Primary modeled demand {source['Scenario_Demand']:,.1f}; "
                    "ranked by municipality unmet demand"
                ),
            }
        )
        rows.append(row)

    critical = critical.sort_values(
        "Single-Shelter Service-Loss Lower Bound", ascending=False
    ).head(4)
    for rank, (_, source) in enumerate(critical.iterrows(), start=1):
        shelter_name = ENGLISH_CRITICAL_SHELTER_NAMES.get(str(source["Shelter ID"]))
        if shelter_name is None:
            raise RuntimeError(f"Missing English shelter name for {source['Shelter ID']}.")
        served = float(source["Served Demand after Removal"])
        row = row_template()
        row.update(
            {
                "Evidence Block": "Critical single-shelter loss",
                "Scenario": f"{rank}. {shelter_name}",
                "Demand Geography": "high loss weighted",
                "Walking Speed (km/h)": 4.0,
                "Time Threshold (min)": 15.0,
                "Capacity per Shelter": 50.0,
                "Maximum Open Shelters": 415,
                "Facility Unavailability": "One critical shelter",
                "Available / Modeled Open Shelters": shelter_inventory - 1,
                "Reachable Demand (%)": None,
                "Served Demand (%)": 100 * served / scenario_demand,
                "Unmet Demand": scenario_demand - served,
                "Served-Demand Change from Primary": -source[
                    "Single-Shelter Service-Loss Lower Bound"
                ],
                "Interpretation / Solution Status": (
                    "Screened among 30 highest reachable-pressure shelters; "
                    + solution_note(source["Proven Optimal"])
                ),
            }
        )
        rows.append(row)

    table = pd.DataFrame(rows, columns=COLUMNS)
    if table.shape != (24, 14):
        raise RuntimeError(f"Expected a 24 × 14 table, found {table.shape}.")
    if table["Evidence Block"].nunique() != 6:
        raise RuntimeError("Expected six evidence blocks.")
    return table


def style_workbook(path: Path) -> None:
    workbook = load_workbook(path)
    worksheet = workbook[SHEET_NAME]
    worksheet.sheet_view.showGridLines = False
    worksheet.freeze_panes = "A3"
    worksheet.auto_filter.ref = f"A2:N{worksheet.max_row}"
    worksheet.sheet_view.zoomScale = 75
    worksheet.print_area = f"A1:N{worksheet.max_row}"
    worksheet.print_title_rows = "1:2"
    worksheet.page_setup.orientation = "landscape"
    worksheet.page_setup.paperSize = worksheet.PAPERSIZE_A3
    worksheet.page_setup.fitToWidth = 1
    worksheet.page_setup.fitToHeight = 1
    worksheet.sheet_properties.pageSetUpPr.fitToPage = True
    worksheet.page_margins = PageMargins(
        left=0.20, right=0.20, top=0.28, bottom=0.28, header=0.12, footer=0.12
    )

    worksheet.merge_cells("A1:N1")
    title = worksheet["A1"]
    title.value = TABLE_TITLE
    title.fill = PatternFill("solid", fgColor="D9EAF7")
    title.font = Font(name="Aptos Display", size=15, bold=True, color="17365D")
    title.alignment = Alignment(horizontal="left", vertical="center")
    worksheet.row_dimensions[1].height = 28

    header_fill = PatternFill("solid", fgColor="17365D")
    header_font = Font(name="Aptos", size=9, bold=True, color="FFFFFF")
    body_font = Font(name="Aptos", size=8.5, color="172033")
    thin_border = Border(bottom=Side(style="thin", color="D0D5DD"))
    for cell in worksheet[2]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    worksheet.row_dimensions[2].height = 58

    block_fills = {
        "Primary / demand geography": "DDEBF7",
        "Walking-access sensitivity": "E8F3EC",
        "Capacity / opening sensitivity": "FFF1D6",
        "Facility-unavailability sensitivity": "FDE7E3",
        "Municipality primary gaps": "E8EAF6",
        "Critical single-shelter loss": "F2EBF6",
    }
    for row in worksheet.iter_rows(min_row=3, max_row=worksheet.max_row):
        for cell in row:
            cell.font = body_font
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = thin_border
        block = str(row[0].value)
        row[0].fill = PatternFill("solid", fgColor=block_fills[block])
        row[0].font = Font(name="Aptos", size=8.5, bold=True, color="17365D")
        for position in range(3, 13):
            row[position].alignment = Alignment(horizontal="right", vertical="top")
        for position in (3, 4):
            row[position].number_format = "0.0"
        for position in (5, 6, 8):
            row[position].number_format = "#,##0"
        row[9].number_format = "0.0"
        row[10].number_format = "0.0"
        row[11].number_format = "#,##0.0"
        row[12].number_format = "#,##0.0"
        if "Time-limit" in str(row[13].value):
            row[13].fill = PatternFill("solid", fgColor="FFF1D6")
        worksheet.row_dimensions[row[0].row].height = 38

    widths = {
        "A": 28,
        "B": 43,
        "C": 22,
        "D": 16,
        "E": 17,
        "F": 18,
        "G": 19,
        "H": 23,
        "I": 16,
        "J": 18,
        "K": 17,
        "L": 17,
        "M": 20,
        "N": 47,
    }
    for column, width in widths.items():
        worksheet.column_dimensions[column].width = width

    table = Table(displayName="NetworkAdequacyRobustness", ref=f"A2:N{worksheet.max_row}")
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    worksheet.add_table(table)
    workbook.save(path)


def verify_workbook(path: Path) -> None:
    workbook = load_workbook(path, data_only=False)
    worksheet = workbook[SHEET_NAME]
    if worksheet.max_row != 26 or worksheet.max_column != 14:
        raise RuntimeError(
            f"Unexpected workbook dimensions: {worksheet.max_row} rows × {worksheet.max_column} columns."
        )
    if worksheet.freeze_panes != "A3":
        raise RuntimeError("Expected frozen title/header rows at A3.")
    for row in worksheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and any(
                error in cell.value
                for error in ("#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A")
            ):
                raise RuntimeError(f"Formula error text found in {cell.coordinate}: {cell.value}")


def main() -> None:
    table = build_table()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        table.to_excel(writer, sheet_name=SHEET_NAME, index=False, startrow=1)
    style_workbook(OUTPUT_PATH)
    verify_workbook(OUTPUT_PATH)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
