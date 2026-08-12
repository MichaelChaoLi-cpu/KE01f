#!/usr/bin/env python3
"""Capacity Evidence and Threshold Calibration.

Plan: Document shelter service class, numeric-capacity evidence, source coverage,
and the share of documented general shelters meeting each standardized threshold.
Framework: Sections 5-7 separate general from welfare-specific supply and use the
118 documented general shelters only to calibrate the plausibility of 25, 50,
100, and 200 persons per shelter; they are not universal observed capacities.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.page import PageMargins
from openpyxl.worksheet.table import Table, TableStyleInfo


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = (
    ROOT
    / "data/exp/prefecture-shelter-capacity-audit/prefecture_shelter_capacity_evidence_audit.parquet"
)
TIER_PATH = (
    ROOT / "data/exp/prefecture-shelter-capacity-audit/capacity_evidence_tier_summary.csv"
)
THRESHOLD_PATH = (
    ROOT / "data/exp/capacity-threshold-estimate/official_capacity_threshold_calibration.csv"
)
OUTPUT_PATH = (
    ROOT / "data/results/tables/Table_capacity_evidence_and_threshold_calibration.xlsx"
)
SHEET_NAME = "Capacity Calibration"
TABLE_TITLE = "Capacity Evidence and Threshold Calibration"

COLUMNS = [
    "Row Group",
    "Evidence Tier / Calibration Group",
    "Shelter Service Class",
    "Shelters",
    "Share of Relevant Inventory (%)",
    "Shelters with Official Numeric Capacity",
    "Official Capacity Median (persons)",
    "Standardized Threshold (persons)",
    "Documented General Shelters at or above Threshold (%)",
    "Interpretation and Limitation",
]

TIER_LABELS = {
    "A_numeric_capacity": "A - Official numeric capacity",
    "B_gymnasium_area": "B - Documented gymnasium area",
    "C_gross_facility_area": "C - Gross facility area",
    "D_school_identity_only": "D - School identity only",
    "E_public_facility_identity_only": "E - Public-facility identity only",
    "F_no_capacity_source_link": "F - No capacity-source link",
}

TIER_LIMITS = {
    "A_numeric_capacity": "Direct official numeric-capacity evidence; duplicate source records are flagged before calibration.",
    "B_gymnasium_area": "Area is documented, but no universal persons-per-square-metre conversion is imposed in this study.",
    "C_gross_facility_area": "Gross facility area is not equivalent to usable shelter floor area.",
    "D_school_identity_only": "Facility identity is linked; no area or numeric capacity is established.",
    "E_public_facility_identity_only": "Public-facility identity is linked; no area or numeric capacity is established.",
    "F_no_capacity_source_link": "No matched capacity-source identity; capacity remains undocumented.",
}


def build_table() -> pd.DataFrame:
    audit = pd.read_parquet(AUDIT_PATH)
    tier_summary = pd.read_csv(TIER_PATH)
    threshold = pd.read_csv(THRESHOLD_PATH)

    tier_crosstab = pd.crosstab(
        audit["Capacity Evidence Tier"], audit["Shelter Service Class"]
    )
    tier_rows: list[dict[str, object]] = []
    for row in tier_summary.itertuples(index=False):
        tier = str(row[0])
        general_count = int(tier_crosstab.loc[tier].get("general", 0))
        welfare_count = int(tier_crosstab.loc[tier].get("welfare_specific", 0))
        tier_rows.append(
            {
                "Row Group": "Evidence tier",
                "Evidence Tier / Calibration Group": TIER_LABELS[tier],
                "Shelter Service Class": f"General {general_count:,}; welfare-specific {welfare_count:,}",
                "Shelters": int(row.Shelters),
                "Share of Relevant Inventory (%)": float(row.Percent),
                "Shelters with Official Numeric Capacity": int(
                    audit.loc[
                        audit["Capacity Evidence Tier"].eq(tier),
                        "Official Numeric Capacity",
                    ].notna().sum()
                ),
                "Official Capacity Median (persons)": audit.loc[
                    audit["Capacity Evidence Tier"].eq(tier),
                    "Official Numeric Capacity",
                ].median(),
                "Standardized Threshold (persons)": pd.NA,
                "Documented General Shelters at or above Threshold (%)": pd.NA,
                "Interpretation and Limitation": TIER_LIMITS[tier],
            }
        )

    service_rows: list[dict[str, object]] = []
    for service_class, label in (
        ("general", "General-shelter inventory"),
        ("welfare_specific", "Welfare-specific inventory"),
    ):
        subset = audit.loc[audit["Shelter Service Class"].eq(service_class)]
        numeric = subset["Official Numeric Capacity"].dropna()
        interpretation = (
            "Unrestricted general-population supply; 118 documented capacities in Uki, Uto, and Yatsushiro form the threshold-calibration sample."
            if service_class == "general"
            else "Reserved as welfare-specific supply and excluded from unrestricted general-population capacity."
        )
        service_rows.append(
            {
                "Row Group": "Service-class calibration",
                "Evidence Tier / Calibration Group": label,
                "Shelter Service Class": (
                    "General" if service_class == "general" else "Welfare-specific"
                ),
                "Shelters": int(len(subset)),
                "Share of Relevant Inventory (%)": 100.0,
                "Shelters with Official Numeric Capacity": int(numeric.notna().sum()),
                "Official Capacity Median (persons)": numeric.median(),
                "Standardized Threshold (persons)": pd.NA,
                "Documented General Shelters at or above Threshold (%)": pd.NA,
                "Interpretation and Limitation": interpretation,
            }
        )

    threshold_rows: list[dict[str, object]] = []
    for row in threshold.itertuples(index=False):
        threshold_value = int(row[0])
        threshold_rows.append(
            {
                "Row Group": "Threshold plausibility",
                "Evidence Tier / Calibration Group": f"{threshold_value}-person standardized threshold",
                "Shelter Service Class": "General",
                "Shelters": int(row[1]),
                "Share of Relevant Inventory (%)": 100.0,
                "Shelters with Official Numeric Capacity": int(row[1]),
                "Official Capacity Median (persons)": float(row[3]),
                "Standardized Threshold (persons)": threshold_value,
                "Documented General Shelters at or above Threshold (%)": float(row[7]),
                "Interpretation and Limitation": (
                    "Plausibility calibration only: documented general shelters come from three municipalities and do not establish universal observed capacity."
                ),
            }
        )

    table = pd.DataFrame([*tier_rows, *service_rows, *threshold_rows], columns=COLUMNS)
    if table.shape != (12, 10):
        raise RuntimeError(f"Expected a 12 × 10 table, found {table.shape}.")
    if int(table.loc[table["Row Group"].eq("Evidence tier"), "Shelters"].sum()) != len(audit):
        raise RuntimeError("Evidence-tier shelter counts do not reconcile to the 1,315-record inventory.")
    general_row = table.loc[
        table["Evidence Tier / Calibration Group"].eq("General-shelter inventory")
    ].iloc[0]
    if int(general_row["Shelters"]) != 1156 or int(
        general_row["Shelters with Official Numeric Capacity"]
    ) != 118:
        raise RuntimeError("General-shelter inventory or calibration sample is inconsistent.")
    return table


def style_workbook(path: Path) -> None:
    workbook = load_workbook(path)
    worksheet = workbook[SHEET_NAME]
    worksheet.sheet_view.showGridLines = False
    worksheet.freeze_panes = "A3"
    worksheet.auto_filter.ref = f"A2:J{worksheet.max_row}"
    worksheet.sheet_view.zoomScale = 85
    worksheet.print_area = f"A1:J{worksheet.max_row}"
    worksheet.print_title_rows = "1:2"
    worksheet.page_setup.orientation = "landscape"
    worksheet.page_setup.paperSize = worksheet.PAPERSIZE_A3
    worksheet.page_setup.fitToWidth = 1
    worksheet.page_setup.fitToHeight = 1
    worksheet.sheet_properties.pageSetUpPr.fitToPage = True
    worksheet.page_margins = PageMargins(
        left=0.25,
        right=0.25,
        top=0.35,
        bottom=0.35,
        header=0.15,
        footer=0.15,
    )

    worksheet.merge_cells("A1:J1")
    title = worksheet["A1"]
    title.value = TABLE_TITLE
    title.fill = PatternFill("solid", fgColor="D9EAF7")
    title.font = Font(name="Aptos Display", size=15, bold=True, color="17365D")
    title.alignment = Alignment(horizontal="left", vertical="center")
    worksheet.row_dimensions[1].height = 28

    header_fill = PatternFill("solid", fgColor="17365D")
    header_font = Font(name="Aptos", size=10, bold=True, color="FFFFFF")
    body_font = Font(name="Aptos", size=9, color="172033")
    thin_border = Border(bottom=Side(style="thin", color="D0D5DD"))
    for cell in worksheet[2]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    worksheet.row_dimensions[2].height = 52

    group_fills = {
        "Evidence tier": "EAF2F8",
        "Service-class calibration": "E8F3EC",
        "Threshold plausibility": "FFF1D6",
    }
    for row in worksheet.iter_rows(min_row=3, max_row=worksheet.max_row):
        group = str(row[0].value)
        for cell in row:
            cell.font = body_font
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = thin_border
        row[0].fill = PatternFill("solid", fgColor=group_fills[group])
        row[0].font = Font(name="Aptos", size=9, bold=True, color="17365D")
        for position in (3, 5, 6, 7):
            row[position].alignment = Alignment(horizontal="right", vertical="top")
        row[3].number_format = "#,##0"
        row[4].number_format = "0.0"
        row[5].number_format = "#,##0"
        row[6].number_format = "#,##0.0"
        row[7].number_format = "#,##0"
        row[8].number_format = "0.0"
        worksheet.row_dimensions[row[0].row].height = 48

    widths = {
        "A": 22,
        "B": 36,
        "C": 31,
        "D": 12,
        "E": 22,
        "F": 23,
        "G": 22,
        "H": 20,
        "I": 29,
        "J": 64,
    }
    for column, width in widths.items():
        worksheet.column_dimensions[column].width = width

    table = Table(displayName="CapacityEvidenceCalibration", ref=f"A2:J{worksheet.max_row}")
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
    if worksheet.max_row != 14 or worksheet.max_column != 10:
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
