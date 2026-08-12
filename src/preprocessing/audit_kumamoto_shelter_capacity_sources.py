"""Audit facility-area evidence for Kumamoto City's 2026 designated shelters.

This is a source-coverage audit, not the final capacity construction. It preserves the
distinction between gymnasium-specific floor area and whole-facility gross floor area.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd
import pdfplumber


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "kumamoto_city_official"
OUT = ROOT / "data" / "exp" / "shelter-capacity-audit"
SHELTER_SOURCE = (
    ROOT
    / "data"
    / "raw"
    / "prior_projects"
    / "KE01"
    / "kumamoto_designated_shelters_geospatial_preprocessed.parquet"
)


def clean_text(value: object) -> str:
    return unicodedata.normalize("NFKC", str(value or "")).replace("\n", "").strip()


def normalize_name(value: object) -> str:
    text = clean_text(value)
    text = text.replace("壼", "壺").replace("ヶ", "ケ").replace("市立", "")
    text = text.replace("高等学校", "高校")
    return re.sub(r"[\s・（）()]", "", text)


def numeric(value: object) -> float | None:
    text = clean_text(value).replace(",", "")
    if text in {"", "-", "None"}:
        return None
    return float(text)


def add_area_record(
    records: list[dict[str, object]],
    name: object,
    area: object,
    area_basis: str,
    source_title: str,
    source_path: Path,
    source_page: int | str,
) -> None:
    area_value = numeric(area)
    if not clean_text(name) or area_value is None:
        return
    records.append(
        {
            "source_facility_name": clean_text(name),
            "source_name_key": normalize_name(name),
            "source_area_m2": area_value,
            "area_basis": area_basis,
            "source_title": source_title,
            "source_file": str(source_path.relative_to(ROOT)),
            "source_page": source_page,
        }
    )


def extract_school_areas() -> list[dict[str, object]]:
    path = RAW / "kumamoto_education_guide_2025.pdf"
    records: list[dict[str, object]] = []
    # Each school-name page is followed by its aligned building-area page.
    page_pairs = [
        (116, 0, 117, 0),
        (118, 0, 119, 0),
        (120, 0, 121, 0),
        (122, 0, 123, 0),
        (124, 0, 125, 0),
        (124, 1, 125, 1),
    ]
    with pdfplumber.open(path) as pdf:
        for name_page, name_table, area_page, area_table in page_pairs:
            names = pdf.pages[name_page - 1].extract_tables()[name_table][2:]
            areas = pdf.pages[area_page - 1].extract_tables()[area_table][3:]
            if len(names) != len(areas):
                raise ValueError(
                    f"Unaligned education tables: pages {name_page}/{area_page}"
                )
            for name_row, area_row in zip(names, areas, strict=True):
                if name_row[0] == "合 計":
                    continue
                add_area_record(
                    records,
                    name_row[1],
                    area_row[6],
                    "gymnasium_floor_area",
                    "Kumamoto Education Guide 2025",
                    path,
                    area_page,
                )
                add_area_record(
                    records,
                    name_row[1],
                    area_row[3],
                    "school_building_gross_floor_area",
                    "Kumamoto Education Guide 2025",
                    path,
                    area_page,
                )
    return records


def extract_generic_table_areas(
    path: Path,
    page_tables: list[tuple[int, int]],
    source_title: str,
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with pdfplumber.open(path) as pdf:
        for page_number, table_number in page_tables:
            table = pdf.pages[page_number - 1].extract_tables()[table_number]
            for row in table:
                if len(row) < 6 or not clean_text(row[0]).isdigit():
                    continue
                add_area_record(
                    records,
                    row[1],
                    row[5],
                    "whole_facility_gross_floor_area",
                    source_title,
                    path,
                    page_number,
                )
    return records


def extract_sports_areas() -> list[dict[str, object]]:
    path = RAW / "kumamoto_sports_facility_stock_plan.pdf"
    records: list[dict[str, object]] = []
    with pdfplumber.open(path) as pdf:
        table = pdf.pages[4].extract_tables()[2]
        for row in table[2:]:
            if not clean_text(row[0]).isdigit():
                continue
            add_area_record(
                records,
                row[1],
                row[4],
                "whole_facility_gross_floor_area",
                "Kumamoto Sports Facility Stock Optimization Plan",
                path,
                5,
            )
    return records


def build_area_evidence() -> pd.DataFrame:
    records = extract_school_areas()
    records += extract_generic_table_areas(
        RAW / "kumamoto_public_facility_whitepaper_2024.pdf",
        [(1, 0), (12, 0), (13, 0), (14, 0)],
        "Kumamoto Public Facility White Paper 2024 - civic halls",
    )
    records += extract_sports_areas()
    records += extract_generic_table_areas(
        RAW / "kumamoto_public_facility_whitepaper_culture_2024.pdf",
        [(1, 0), (5, 0)],
        "Kumamoto Public Facility White Paper 2024 - assembly and cultural facilities",
    )
    records += extract_generic_table_areas(
        RAW / "kumamoto_public_facility_whitepaper_welfare_2024.pdf",
        [(1, 0)],
        "Kumamoto Public Facility White Paper 2024 - welfare facilities",
    )
    records += extract_generic_table_areas(
        RAW / "kumamoto_public_facility_whitepaper_administration_2024.pdf",
        [(9, 0), (30, 0)],
        "Kumamoto Public Facility White Paper 2024 - administrative facilities",
    )

    # Official management evaluation gives both gross and room-level areas. Gross area is
    # retained here to keep this audit comparable with the other non-school facilities.
    add_area_record(
        records,
        "熊本市食品交流会館",
        2280.85,
        "whole_facility_gross_floor_area",
        "Kumamoto Food Exchange Hall management evaluation",
        RAW / "kumamoto_food_exchange_hall_management_evaluation.pdf",
        "facility overview",
    )
    return pd.DataFrame(records)


# Official and source documents use several different facility labels.
SOURCE_ALIASES = {
    "熊本市総合体育館・青年会館": "総合体育館・青年会館",
    "水前寺競技場": "水前寺運動公園（競技場）",
    "アクアドームくまもと": "総合屋内プール",
    "浜線健康パーク（田迎公園運動施設）": "田迎公園（運動施設）",
    "雁回館": "富合雁回館",
    "天明体育館": "天明運動施設",
    "アスパル富合（富合公民館）": "アスパル富合（ホール等）",
    "城南総合スポーツセンター（城南B&G海洋センター含む）": "城南総合スポーツセンター",
    "大江交流室・公民館": "大江公民館（大江交流室）",
    "五福交流室・公民館": "五福公民館（五福まちづくり交流センター）",
    "秋津まちづくりセンター・公民館": "秋津公民館（秋津まちづくりセンター）",
    "託麻まちづくりセンター・公民館": "託麻公民館（託麻まちづくりセンター）",
    "花園まちづくりセンター・公民館": "花園公民館（花園まちづくりセンター）",
    "河内交流室・公民館": "河内公民館（河内交流室）",
    "天明まちづくりセンター・公民館": "天明公民館（天明まちづくりセンター）",
    "飽田まちづくりセンター・公民館": "飽田公民館（飽田まちづくりセンター）",
    "幸田まちづくりセンター・公民館": "幸田公民館（幸田まちづくりセンター）",
    "南部まちづくりセンター・公民館": "南部公民館（南部まちづくりセンター）",
    "北部まちづくりセンター・公民館": "北部公民館（北部まちづくりセンター）",
    "清水まちづくりセンター・公民館": "清水公民館（清水まちづくりセンター）",
    "龍田まちづくりセンター・公民館": "龍田公民館（龍田まちづくりセンター）",
    "植木文化センター": "植木文化センター（ホール等）",
    "火の君文化センター": "火の君文化センター（ホール等）",
    "くまもと森都心プラザ": "くまもと森都心プラザ（ホール等）",
    "東部公民館": "東部公民館（東部まちづくりセンター）",
    "西部公民館": "西部公民館（西区役所）",
    "芳野コミュニティセンター": "芳野コミュニティセンター（河内まちづくりセンター芳野分室）",
    "熊本市食品交流会館": "熊本市食品交流会館",
}


def preferred_evidence(options: pd.DataFrame) -> pd.Series | None:
    if options.empty:
        return None
    order = {
        "gymnasium_floor_area": 0,
        "whole_facility_gross_floor_area": 1,
        "school_building_gross_floor_area": 2,
    }
    ranked = options.assign(
        _rank=options["area_basis"].map(order).fillna(9),
        _source_rank=options["source_title"].str.contains("2024").map({True: 0, False: 1}),
    ).sort_values(["_rank", "_source_rank"])
    return ranked.iloc[0]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    shelters = pd.read_parquet(SHELTER_SOURCE)
    shelters = shelters[
        shelters["Common ID"].astype("string").str.startswith("E4310000", na=False)
    ].copy()
    if len(shelters) != 182:
        raise ValueError(f"Expected 182 Kumamoto City shelters, found {len(shelters)}")

    evidence = build_area_evidence()
    rows: list[dict[str, object]] = []
    for shelter in shelters.itertuples(index=False):
        facility_name = shelter[2]
        requested_source_name = SOURCE_ALIASES.get(facility_name, facility_name)
        key = normalize_name(requested_source_name)
        selected = preferred_evidence(evidence[evidence["source_name_key"] == key])
        school_building = evidence[
            (evidence["source_name_key"] == key)
            & (evidence["area_basis"] == "school_building_gross_floor_area")
        ]
        address = clean_text(shelter[3])
        ward_match = re.search(r"熊本市(中央区|東区|西区|南区|北区)", address)
        ward = ward_match.group(1) if ward_match else "Unknown"

        row = {
            "Shelter ID": shelter[1],
            "Shelter Name": facility_name,
            "Ward": ward,
            "Address": address,
            "Official 2026 Designated Shelter": True,
            "Initial Event Opening Evidence": "citywide count only",
            "Observed Facility Capacity": pd.NA,
            "Source Area (m2)": pd.NA,
            "Additional School Building Gross Area (m2)": pd.NA,
            "Area Basis": "missing",
            "Area Evidence Grade": "D - missing area",
            "Source Facility Name": pd.NA,
            "Source Title": pd.NA,
            "Source File": pd.NA,
            "Source Page": pd.NA,
            "Capacity Construction Status": "not ready - area missing",
        }
        if selected is not None:
            row.update(
                {
                    "Source Area (m2)": selected["source_area_m2"],
                    "Area Basis": selected["area_basis"],
                    "Area Evidence Grade": (
                        "B - gymnasium-specific area"
                        if selected["area_basis"] == "gymnasium_floor_area"
                        else "C - whole-facility gross floor area"
                    ),
                    "Source Facility Name": selected["source_facility_name"],
                    "Source Title": selected["source_title"],
                    "Source File": selected["source_file"],
                    "Source Page": selected["source_page"],
                    "Capacity Construction Status": (
                        "requires usable-area factor and space-per-person standard"
                    ),
                }
            )
        if not school_building.empty:
            row["Additional School Building Gross Area (m2)"] = school_building.iloc[0][
                "source_area_m2"
            ]
        rows.append(row)

    audit = pd.DataFrame(rows).sort_values(["Ward", "Shelter Name"]).reset_index(drop=True)
    audit["Source Page"] = audit["Source Page"].astype("string")
    audit.to_csv(OUT / "shelter_capacity_source_audit.csv", index=False)
    audit.to_parquet(OUT / "shelter_capacity_source_audit.parquet", index=False)

    grade_summary = (
        audit.groupby(["Area Evidence Grade"], dropna=False)
        .size()
        .rename("Shelters")
        .reset_index()
    )
    ward_summary = (
        audit.assign(Area_Available=audit["Source Area (m2)"].notna())
        .groupby("Ward")
        .agg(
            Designated_Shelters=("Shelter ID", "size"),
            Shelters_With_Area=("Area_Available", "sum"),
        )
        .reset_index()
    )
    ward_summary["Area_Coverage_Percent"] = (
        100 * ward_summary["Shelters_With_Area"] / ward_summary["Designated_Shelters"]
    ).round(1)
    grade_summary.to_csv(OUT / "area_evidence_grade_summary.csv", index=False)
    ward_summary.to_csv(OUT / "ward_area_coverage_summary.csv", index=False)

    missing = audit[audit["Source Area (m2)"].isna()][
        ["Shelter Name", "Ward", "Address"]
    ]
    coverage = audit["Source Area (m2)"].notna().mean() * 100
    readme = f"""# Shelter Capacity Source Audit

## Scope

- Official Kumamoto City designated shelters: {len(audit)}
- Facilities with an official area source: {audit['Source Area (m2)'].notna().sum()} ({coverage:.1f}%)
- Facilities with no recovered area: {len(missing)}
- Facilities with an observed numeric shelter-capacity field: 0
- Active school shelters with both gymnasium area and separate school-building gross area:
  {audit['Additional School Building Gross Area (m2)'].notna().sum()}

The official 2026 disaster-plan appendix reports 182 designated shelters. The local
prefecture-wide inventory contains exactly 182 records with Kumamoto City code `43100`, so
those records form the facility master. The 29 July 2026 event report also gives 182 opened
shelters after the all-shelter opening order, but it does not publish facility capacity.

## Evidence Grades

{grade_summary.to_markdown(index=False)}

- Grade B is a gymnasium- or indoor-arena-specific floor area. It is the strongest currently
  available facility-level basis, but circulation, storage, toilets, and unusable zones still
  require an effective-area factor.
- For active school shelters, school-building gross area is retained in a separate field. It
  may support a scenario in which a documented share of classrooms is opened, but it is never
  added directly to the gymnasium area as if the entire school building were habitable space.
- Grade C is whole-facility gross floor area. It must not be divided directly by a
  space-per-person standard; a facility-type-specific usable-area factor is required first.
- Grade D has no recovered area and must be completed from a facility ledger or represented
  transparently through bounded imputation.
- No facility currently has Grade A evidence (an official numeric shelter capacity or an
  official designated accommodation-area measurement).

## Coverage by Ward

{ward_summary.to_markdown(index=False)}

## Facilities Still Missing Area

{missing.to_markdown(index=False)}

## Interpretation

This audit establishes that a facility-level capacity scenario is feasible, but it does not
yet establish shelter sufficiency. The next construction decision is the combination of
usable-area factors and space-per-person standards. Proposed sensitivity values should be
confirmed before writing the final capacity variables to `data/processed/`.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    print(f"Wrote {OUT / 'shelter_capacity_source_audit.csv'} ({len(audit)} rows)")
    print(grade_summary.to_string(index=False))
    print(ward_summary.to_string(index=False))
    print("Missing area facilities:", len(missing))


if __name__ == "__main__":
    main()
