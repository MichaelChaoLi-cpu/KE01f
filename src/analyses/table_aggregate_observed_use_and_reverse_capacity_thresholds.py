#!/usr/bin/env python3
"""Aggregate Observed-Use and Reverse Capacity Thresholds.

Plan: Compare four official event-use snapshots with four standardized capacity
thresholds and report reverse critical capacities at the 415-opening scale.
Framework: Sections 5-7 treat the snapshots as discrete aggregate benchmarks and
use municipality-contained reverse requirements rather than observed local demand.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.page import PageMargins
from openpyxl.worksheet.table import Table, TableStyleInfo


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_THRESHOLD_PATH = (
    ROOT / "data/exp/capacity-threshold-estimate/event_snapshot_capacity_thresholds.csv"
)
CRITICAL_PATH = (
    ROOT / "data/exp/capacity-threshold-estimate/critical_capacity_at_observed_open_scale.csv"
)
OUTPUT_PATH = (
    ROOT
    / "data/results/tables/Table_aggregate_observed_use_and_reverse_capacity_thresholds.xlsx"
)
SHEET_NAME = "Aggregate Thresholds"
TABLE_TITLE = "Aggregate Observed-Use and Reverse Capacity Thresholds"

COLUMNS = [
    "Row Group",
    "Observation / Demand Scenario",
    "Hours Since Earthquake",
    "Evacuees / Scenario Demand",
    "Reported / Modeled Opening Limit",
    "Capacity Threshold / Critical Capacity",
    "Implied Capacity at Opening Limit",
    "Surplus or Shortfall at Opening Limit",
    "Minimum Open Shelters Required",
    "Sufficiency / Highest-Pressure Municipality",
    "Interpretation",
]

SCENARIO_LABELS = {
    "Observed-use stress, population weighted": "Observed-use stress - population weighted",
    "Observed-use stress, central housing-loss weighted": "Observed-use stress - central-loss weighted",
    "Observed-use stress, high housing-loss weighted": "Observed-use stress - high-loss weighted",
    "Modeled high housing-loss demand": "Modeled high housing-loss demand",
}

MUNICIPALITY_LABELS = {
    "熊本市": "Kumamoto City",
    "八代市": "Yatsushiro",
}


def build_table() -> pd.DataFrame:
    snapshots = pd.read_csv(SNAPSHOT_THRESHOLD_PATH)
    critical = pd.read_csv(CRITICAL_PATH)

    snapshot_rows: list[dict[str, object]] = []
    for row in snapshots.itertuples(index=False):
        timestamp = pd.Timestamp(row[0]).strftime("%Y-%m-%d %H:%M JST")
        sufficient = bool(row[9])
        snapshot_rows.append(
            {
                "Row Group": "Official aggregate snapshot x threshold",
                "Observation / Demand Scenario": timestamp,
                "Hours Since Earthquake": float(row[1]),
                "Evacuees / Scenario Demand": float(row[2]),
                "Reported / Modeled Opening Limit": int(row[3]),
                "Capacity Threshold / Critical Capacity": int(row[5]),
                "Implied Capacity at Opening Limit": float(row[6]),
                "Surplus or Shortfall at Opening Limit": float(row[7]),
                "Minimum Open Shelters Required": int(row[8]),
                "Sufficiency / Highest-Pressure Municipality": (
                    "Sufficient in aggregate" if sufficient else "Shortfall in aggregate"
                ),
                "Interpretation": (
                    "Discrete official prefecture-wide use benchmark; aggregate arithmetic only, without municipality origins, walking access, or facility-specific capacity."
                ),
            }
        )

    critical_rows: list[dict[str, object]] = []
    for row in critical.itertuples(index=False):
        scenario = str(row[0])
        demand = float(row[1])
        opening_limit = int(row[2])
        capacity = int(row[3])
        critical_rows.append(
            {
                "Row Group": "Reverse critical capacity at 415 openings",
                "Observation / Demand Scenario": SCENARIO_LABELS[scenario],
                "Hours Since Earthquake": pd.NA,
                "Evacuees / Scenario Demand": demand,
                "Reported / Modeled Opening Limit": opening_limit,
                "Capacity Threshold / Critical Capacity": capacity,
                "Implied Capacity at Opening Limit": opening_limit * capacity,
                "Surplus or Shortfall at Opening Limit": opening_limit * capacity - demand,
                "Minimum Open Shelters Required": int(row[4]),
                "Sufficiency / Highest-Pressure Municipality": MUNICIPALITY_LABELS.get(
                    str(row[7]), str(row[7])
                ),
                "Interpretation": (
                    "Modeled reverse requirement with municipality containment; critical capacity is not an observed facility capacity and precedes network constraints."
                ),
            }
        )

    table = pd.DataFrame([*snapshot_rows, *critical_rows], columns=COLUMNS)
    if table.shape != (20, 11):
        raise RuntimeError(f"Expected a 20 × 11 table, found {table.shape}.")
    official = table["Row Group"].eq("Official aggregate snapshot x threshold")
    if official.sum() != 16 or (~official).sum() != 4:
        raise RuntimeError("Expected 16 snapshot-threshold rows and 4 reverse-capacity rows.")
    shortfall = table.loc[
        official
        & table["Evacuees / Scenario Demand"].eq(10467)
        & table["Capacity Threshold / Critical Capacity"].eq(25),
        "Surplus or Shortfall at Opening Limit",
    ]
    if len(shortfall) != 1 or float(shortfall.iloc[0]) != -92.0:
        raise RuntimeError("The official 10,467-person, 25-person-threshold shortfall does not reconcile.")
    return table


def style_workbook(path: Path) -> None:
    workbook = load_workbook(path)
    worksheet = workbook[SHEET_NAME]
    worksheet.sheet_view.showGridLines = False
    worksheet.freeze_panes = "A3"
    worksheet.auto_filter.ref = f"A2:K{worksheet.max_row}"
    worksheet.sheet_view.zoomScale = 82
    worksheet.print_area = f"A1:K{worksheet.max_row}"
    worksheet.print_title_rows = "1:2"
    worksheet.page_setup.orientation = "landscape"
    worksheet.page_setup.paperSize = worksheet.PAPERSIZE_A3
    worksheet.page_setup.fitToWidth = 1
    worksheet.page_setup.fitToHeight = 1
    worksheet.sheet_properties.pageSetUpPr.fitToPage = True
    worksheet.page_margins = PageMargins(
        left=0.22,
        right=0.22,
        top=0.30,
        bottom=0.30,
        header=0.12,
        footer=0.12,
    )

    worksheet.merge_cells("A1:K1")
    title = worksheet["A1"]
    title.value = TABLE_TITLE
    title.fill = PatternFill("solid", fgColor="D9EAF7")
    title.font = Font(name="Aptos Display", size=15, bold=True, color="17365D")
    title.alignment = Alignment(horizontal="left", vertical="center")
    worksheet.row_dimensions[1].height = 28

    header_fill = PatternFill("solid", fgColor="17365D")
    header_font = Font(name="Aptos", size=9.5, bold=True, color="FFFFFF")
    body_font = Font(name="Aptos", size=8.5, color="172033")
    thin_border = Border(bottom=Side(style="thin", color="D0D5DD"))
    for cell in worksheet[2]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    worksheet.row_dimensions[2].height = 54

    group_fills = {
        "Official aggregate snapshot x threshold": "EAF2F8",
        "Reverse critical capacity at 415 openings": "FFF1D6",
    }
    for row in worksheet.iter_rows(min_row=3, max_row=worksheet.max_row):
        group = str(row[0].value)
        for cell in row:
            cell.font = body_font
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = thin_border
        row[0].fill = PatternFill("solid", fgColor=group_fills[group])
        row[0].font = Font(name="Aptos", size=8.5, bold=True, color="17365D")
        for position in range(2, 9):
            row[position].alignment = Alignment(horizontal="right", vertical="top")
        row[2].number_format = "0.00"
        for position in (3, 4, 5, 6, 7, 8):
            row[position].number_format = "#,##0.0" if position in (3, 7) else "#,##0"
        if isinstance(row[7].value, (int, float)) and row[7].value < 0:
            row[7].font = Font(name="Aptos", size=8.5, bold=True, color="B42318")
            row[9].fill = PatternFill("solid", fgColor="FDE7E3")
        worksheet.row_dimensions[row[0].row].height = 43

    widths = {
        "A": 29,
        "B": 38,
        "C": 15,
        "D": 18,
        "E": 19,
        "F": 21,
        "G": 20,
        "H": 22,
        "I": 20,
        "J": 29,
        "K": 65,
    }
    for column, width in widths.items():
        worksheet.column_dimensions[column].width = width

    table = Table(displayName="AggregateObservedUseThresholds", ref=f"A2:K{worksheet.max_row}")
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
    if worksheet.max_row != 22 or worksheet.max_column != 11:
        raise RuntimeError(
            f"Unexpected workbook dimensions: {worksheet.max_row} rows × {worksheet.max_column} columns."
        )
    if worksheet.freeze_panes != "A3":
        raise RuntimeError("Expected frozen title/header rows at A3.")
    formula_errors = {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A"}
    for row in worksheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and any(error in cell.value for error in formula_errors):
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
