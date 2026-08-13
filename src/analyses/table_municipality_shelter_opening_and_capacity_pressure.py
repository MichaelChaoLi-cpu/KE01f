#!/usr/bin/env python3
"""Municipality Shelter Opening and Capacity Pressure.

Plan: Provide a paper-ready summary of prefecture-wide shelter-opening needs and
the ten municipalities facing the greatest capacity pressure.
Framework: Sections 5-7 apply municipality-contained reverse requirements before
network assignment; scenario rows are modeled and not observed municipality use.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.page import PageMargins
from openpyxl.worksheet.table import Table, TableStyleInfo


ROOT = Path(__file__).resolve().parents[2]
MUNICIPALITY_PATH = (
    ROOT / "data/exp/capacity-threshold-estimate/municipality_capacity_thresholds.csv"
)
PRESSURE_PATH = (
    ROOT
    / "data/exp/capacity-threshold-estimate/municipality_required_capacity_pressure_ranking.csv"
)
DEMAND_PATH = ROOT / "data/processed/kumamoto_prefecture_shelter_demand_preprocessed.parquet"
OUTPUT_PATH = (
    ROOT
    / "data/results/tables/Table_municipality_shelter_opening_and_capacity_pressure.xlsx"
)
SHEET_NAME = "Paper Summary"
TABLE_TITLE = "Municipality Shelter Opening and Capacity Pressure"

SCENARIO_LABELS = {
    "Observed-use stress, population weighted": "Observed-use stress - population weighted",
    "Observed-use stress, central housing-loss weighted": "Observed-use stress - central-loss weighted",
    "Observed-use stress, high housing-loss weighted": "Observed-use stress - high-loss weighted",
    "Modeled high housing-loss demand": "Modeled high housing-loss demand",
}

ENGLISH_MUNICIPALITY_NAMES = {
    "43100": "Kumamoto City",
    "43202": "Yatsushiro",
    "43204": "Arao",
    "43208": "Yamaga",
    "43211": "Uto",
    "43213": "Uki",
    "43216": "Koshi",
    "43367": "Nankan",
    "43404": "Kikuyo",
    "43468": "Hikawa",
}

COLUMNS = [
    "Scope",
    "Area",
    "Demand Scenario",
    "Residential Population",
    "Minimum Epicentral Distance (km)",
    "General Shelters",
    "Scenario Demand",
    "Required Capacity if All General Shelters Open",
    "Minimum Open Shelters Required at 25 Persons",
    "25-Person Local Pressure",
    "Minimum Open Shelters Required at 50 Persons",
    "Pressure Rank",
]


def build_full_results() -> pd.DataFrame:
    municipality = pd.read_csv(MUNICIPALITY_PATH, dtype={"Municipality Code": str})
    pressure = pd.read_csv(PRESSURE_PATH, dtype={"Municipality Code": str})[
        ["Demand Scenario", "Municipality Code", "Pressure Rank"]
    ]
    demand = pd.read_parquet(
        DEMAND_PATH,
        columns=["Municipality Code", "Municipality", "Epicentral Distance (km)"],
    )
    demand["Municipality Code"] = demand["Municipality Code"].astype(str)
    distance = (
        demand.groupby(["Municipality Code", "Municipality"], as_index=False)[
            "Epicentral Distance (km)"
        ]
        .min()
        .rename(columns={"Epicentral Distance (km)": "Minimum Epicentral Distance (km)"})
    )
    full = municipality.merge(
        pressure,
        on=["Demand Scenario", "Municipality Code"],
        how="left",
        validate="1:1",
    ).merge(
        distance[["Municipality Code", "Minimum Epicentral Distance (km)"]],
        on="Municipality Code",
        how="left",
        validate="many_to_one",
    )
    full = full.rename(columns={"Residential_Population": "Residential Population"})
    if full.shape[0] != 180 or full["Municipality Code"].nunique() != 45:
        raise RuntimeError("Expected 180 rows covering all 45 municipalities.")
    if full[["Minimum Epicentral Distance (km)", "Pressure Rank"]].isna().any().any():
        raise RuntimeError("Source distance or pressure rank is missing.")
    return full


def build_paper_table(full: pd.DataFrame) -> pd.DataFrame:
    municipality_base = full.drop_duplicates("Municipality Code")
    prefecture_population = int(municipality_base["Residential Population"].sum())
    prefecture_shelters = int(municipality_base["General Shelters"].sum())

    summary_rows: list[dict[str, object]] = []
    scenario_order = [
        "Modeled high housing-loss demand",
        "Observed-use stress, population weighted",
        "Observed-use stress, central housing-loss weighted",
        "Observed-use stress, high housing-loss weighted",
    ]
    for scenario in scenario_order:
        group = full.loc[full["Demand Scenario"] == scenario]
        scenario_demand = float(group["Scenario Demand"].sum())
        infeasible_count = int((~group["Locally Feasible at 25 Persons"]).sum())
        municipality_contained_openings_25 = int(
            group["Minimum Open Shelters Required at 25 Persons"].sum()
        )
        municipality_contained_openings_50 = int(
            group["Minimum Open Shelters Required at 50 Persons"].sum()
        )
        summary_rows.append(
            {
                "Scope": "Prefecture summary",
                "Area": "Kumamoto Prefecture",
                "Demand Scenario": SCENARIO_LABELS[scenario],
                "Residential Population": prefecture_population,
                "Minimum Epicentral Distance (km)": None,
                "General Shelters": prefecture_shelters,
                "Scenario Demand": scenario_demand,
                "Required Capacity if All General Shelters Open": (
                    scenario_demand / prefecture_shelters
                ),
                "Minimum Open Shelters Required at 25 Persons": (
                    municipality_contained_openings_25
                ),
                "25-Person Local Pressure": f"{infeasible_count} municipalities infeasible",
                "Minimum Open Shelters Required at 50 Persons": (
                    municipality_contained_openings_50
                ),
                "Pressure Rank": None,
            }
        )

    worst_index = full.groupby("Municipality Code")[
        "Required Capacity if All General Shelters Open"
    ].idxmax()
    worst = (
        full.loc[worst_index]
        .sort_values(
            ["Required Capacity if All General Shelters Open", "Municipality Code"],
            ascending=[False, True],
        )
        .head(10)
        .reset_index(drop=True)
    )
    municipality_rows: list[dict[str, object]] = []
    for rank, row in worst.iterrows():
        municipality_name = ENGLISH_MUNICIPALITY_NAMES.get(str(row["Municipality Code"]))
        if municipality_name is None:
            raise RuntimeError(
                f"Missing English municipality name for code {row['Municipality Code']}."
            )
        shortfall = max(
            0,
            int(row["Minimum Open Shelters Required at 25 Persons"])
            - int(row["General Shelters"]),
        )
        municipality_rows.append(
            {
                "Scope": "High-pressure municipality",
                "Area": municipality_name,
                "Demand Scenario": SCENARIO_LABELS[row["Demand Scenario"]],
                "Residential Population": row["Residential Population"],
                "Minimum Epicentral Distance (km)": row[
                    "Minimum Epicentral Distance (km)"
                ],
                "General Shelters": row["General Shelters"],
                "Scenario Demand": row["Scenario Demand"],
                "Required Capacity if All General Shelters Open": row[
                    "Required Capacity if All General Shelters Open"
                ],
                "Minimum Open Shelters Required at 25 Persons": row[
                    "Minimum Open Shelters Required at 25 Persons"
                ],
                "25-Person Local Pressure": (
                    f"Short by {shortfall} shelters" if shortfall else "Feasible"
                ),
                "Minimum Open Shelters Required at 50 Persons": row[
                    "Minimum Open Shelters Required at 50 Persons"
                ],
                "Pressure Rank": rank + 1,
            }
        )

    table = pd.DataFrame([*summary_rows, *municipality_rows], columns=COLUMNS)
    if table.shape != (14, 12):
        raise RuntimeError(f"Expected a 14 × 12 paper table, found {table.shape}.")
    expected_prefecture_openings = {
        "Modeled high housing-loss demand": (122, 78),
        "Observed-use stress - population weighted": (441, 233),
        "Observed-use stress - central-loss weighted": (446, 235),
        "Observed-use stress - high-loss weighted": (441, 235),
    }
    prefecture_rows = table.loc[table["Scope"] == "Prefecture summary"]
    actual_prefecture_openings = {
        str(row["Demand Scenario"]): (
            int(row["Minimum Open Shelters Required at 25 Persons"]),
            int(row["Minimum Open Shelters Required at 50 Persons"]),
        )
        for _, row in prefecture_rows.iterrows()
    }
    if actual_prefecture_openings != expected_prefecture_openings:
        raise RuntimeError(
            "Municipality-contained prefecture totals do not match the validated "
            f"scenario sums: {actual_prefecture_openings}"
        )
    return table


def style_workbook(path: Path) -> None:
    workbook = load_workbook(path)
    worksheet = workbook[SHEET_NAME]
    worksheet.sheet_view.showGridLines = False
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = f"A1:L{worksheet.max_row}"
    worksheet.sheet_view.zoomScale = 80
    worksheet.print_area = f"A1:L{worksheet.max_row}"
    worksheet.print_title_rows = "1:1"
    worksheet.page_setup.orientation = "landscape"
    worksheet.page_setup.paperSize = worksheet.PAPERSIZE_A3
    worksheet.page_setup.fitToWidth = 1
    worksheet.page_setup.fitToHeight = 1
    worksheet.sheet_properties.pageSetUpPr.fitToPage = True
    worksheet.page_margins = PageMargins(
        left=0.20, right=0.20, top=0.28, bottom=0.28, header=0.12, footer=0.12
    )

    header_fill = PatternFill("solid", fgColor="17365D")
    header_font = Font(name="Aptos", size=9, bold=True, color="FFFFFF")
    body_font = Font(name="Aptos", size=8.5, color="172033")
    thin_border = Border(bottom=Side(style="thin", color="D0D5DD"))
    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    worksheet.row_dimensions[1].height = 58

    for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
        scope = str(row[0].value)
        for cell in row:
            cell.font = body_font
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = thin_border
        row[0].fill = PatternFill(
            "solid", fgColor="EAF2F8" if scope == "Prefecture summary" else "FFF1D6"
        )
        row[0].font = Font(name="Aptos", size=8.5, bold=True, color="17365D")
        for position in (3, 4, 5, 6, 7, 8, 10, 11):
            row[position].alignment = Alignment(horizontal="right", vertical="top")
        row[3].number_format = "#,##0"
        row[4].number_format = "0.0"
        row[5].number_format = "#,##0"
        row[6].number_format = "#,##0.0"
        row[7].number_format = "#,##0.0"
        row[8].number_format = "#,##0"
        row[10].number_format = "#,##0"
        row[11].number_format = "#,##0"
        if str(row[9].value).startswith("Short by"):
            row[9].fill = PatternFill("solid", fgColor="FDE7E3")
            row[9].font = Font(name="Aptos", size=8.5, bold=True, color="B42318")
        worksheet.row_dimensions[row[0].row].height = 37

    widths = {
        "A": 27,
        "B": 20,
        "C": 39,
        "D": 18,
        "E": 20,
        "F": 15,
        "G": 17,
        "H": 25,
        "I": 23,
        "J": 25,
        "K": 23,
        "L": 13,
    }
    for column, width in widths.items():
        worksheet.column_dimensions[column].width = width

    table = Table(displayName="MunicipalityOpeningPressure", ref=f"A1:L{worksheet.max_row}")
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
    if worksheet.max_row != 15 or worksheet.max_column != 12:
        raise RuntimeError(
            f"Unexpected workbook dimensions: {worksheet.max_row} rows × {worksheet.max_column} columns."
        )
    if worksheet.freeze_panes != "A2":
        raise RuntimeError("Expected the header row to be frozen at A2.")
    if worksheet.merged_cells.ranges:
        raise RuntimeError("Merged cells are not permitted in article-facing tables.")
    formula_errors = {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A"}
    for row in worksheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and any(
                error in cell.value for error in formula_errors
            ):
                raise RuntimeError(f"Formula error text found in {cell.coordinate}: {cell.value}")


def main() -> None:
    full = build_full_results()
    table = build_paper_table(full)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        table.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    style_workbook(OUTPUT_PATH)
    verify_workbook(OUTPUT_PATH)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
