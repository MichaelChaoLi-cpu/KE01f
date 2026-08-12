"""Extract official facility-level shelter capacities near the 2026 hypocenter.

The output preserves municipality-specific definitions.  In particular, Uki City
reports designated-shelter capacity at 3 square metres per person, whereas
Yatsushiro City reports maximum and infection-control capacities and separately
identifies facilities planned to open for stronger earthquakes.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd
import pdfplumber


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "kumamoto_prefecture_capacity_sources"
PROCESSED = ROOT / "data" / "processed"
EXP = ROOT / "data" / "exp" / "prefecture-shelter-capacity-audit"

UKI_SOURCE = RAW / "uki_designated_shelters_2022.pdf"
YATSUSHIRO_SOURCE = RAW / "yatsushiro_shelter_list_2026.pdf"

UTO_MATERIALS_URL = "https://www.city.uto.lg.jp/d?q=2d4941a3d9559dc2e1bcdaba35bac6eb.pdf"
UTO_FLOOD_PLAN_URL = "https://www.city.uto.lg.jp/d?q=d7d48a854644e3c4a953932ae9878a7a.pdf"


def clean_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return unicodedata.normalize("NFKC", str(value)).replace("\n", "").strip()


def numeric(value: object) -> float | None:
    text = clean_text(value).replace(",", "")
    text = re.sub(r"(?:㎡|m2|名|人)$", "", text, flags=re.IGNORECASE).strip()
    if text in {"", "-", "―", "−", "ー"}:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def extract_uki() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with pdfplumber.open(UKI_SOURCE) as pdf:
        # Printed page 55 / PDF page 59 contains the complete municipal table.
        table = pdf.pages[58].extract_tables()[0]
    for row in table[3:]:
        name = clean_text(row[2])
        if not name or "小計" in name or "TOTAL" in name:
            continue
        rows.append(
            {
                "Source Municipality Code": "43213",
                "Source Municipality": "宇城市",
                "Source Facility Name": name,
                "Source Address": clean_text(row[3]),
                "Official Capacity Primary (persons)": numeric(row[13]),
                "Official Capacity Primary Definition": "designated_shelter_capacity_at_3m2_per_person",
                "Official Capacity Secondary (persons)": numeric(row[11]),
                "Official Capacity Secondary Definition": "emergency_evacuation_place_capacity_at_2m2_per_person",
                "Official Building Area (m2)": numeric(row[4]),
                "Earthquake Opening or Suitability Flag": clean_text(row[7]) == "○",
                "Earthquake Flag Definition": "designated_emergency_evacuation_place_earthquake_suitability",
                "Official Source Title": "宇城市 指定避難所一覧（令和4年6月現在）",
                "Official Source Date": "2022-06",
                "Official Source URL": "https://www.city.uki.kumamoto.jp/kurashi/bosaiinfo/2160153",
                "Official Source File": str(UKI_SOURCE.relative_to(ROOT)),
                "Official Source Page": 59,
            }
        )
    return rows


def extract_yatsushiro() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with pdfplumber.open(YATSUSHIRO_SOURCE) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            table = page.extract_tables()[0]
            for row in table[2:]:
                name = clean_text(row[1])
                if not name:
                    continue
                rows.append(
                    {
                        "Source Municipality Code": "43202",
                        "Source Municipality": "八代市",
                        "Source Facility Name": name,
                        "Source Address": clean_text(row[2]),
                        "Official Capacity Primary (persons)": numeric(row[3]),
                        "Official Capacity Primary Definition": "maximum_capacity",
                        "Official Capacity Secondary (persons)": numeric(row[4]),
                        "Official Capacity Secondary Definition": "infection_control_capacity",
                        "Official Building Area (m2)": pd.NA,
                        "Earthquake Opening or Suitability Flag": clean_text(row[12]) == "〇",
                        "Earthquake Flag Definition": "planned_opening_for_seismic_intensity_6_upper_or_greater",
                        "Official Source Title": "令和8年度八代市避難所一覧表",
                        "Official Source Date": "2026-06-01",
                        "Official Source URL": "https://www.city.yatsushiro.lg.jp/kiji00322241/index.html",
                        "Official Source File": str(YATSUSHIRO_SOURCE.relative_to(ROOT)),
                        "Official Source Page": page_number,
                    }
                )
    return rows


def extract_uto() -> list[dict[str, object]]:
    """Structure the two official Uto tables exposed by the city web index.

    Direct command-line retrieval of the official PDFs currently returns the city's
    HTML error page.  Values below are transcribed from the indexed official tables
    and are guarded by a complete 41-general-shelter coverage assertion downstream.
    The current materials table is preferred; three non-city facilities use the
    official flood-plan table, which includes them explicitly.
    """
    # facility, address without prefecture/city prefix, capacity, source variant
    values = [
        ("市武道館", "旭町500", 223, "materials"),
        ("ecowin宇土アリーナ（宇土市民体育館）", "旭町504", 1441, "materials"),
        ("宇土市立図書館", "浦田町131-1", 210, "materials"),
        ("市福祉センター", "浦田町44", 30, "materials"),
        ("市役所別館", "浦田町51", 195, "materials"),
        ("網田中学校体育館", "下網田町1120", 308, "materials"),
        ("網田小学校体育館", "下網田町1842", 274, "materials"),
        ("網田地区農業者トレーニングセンター", "下網田町1903", 176, "materials"),
        ("西部老人福祉センター", "下網田町1942-1", 119, "materials"),
        ("宇土マリーナ会議室", "下網田町3084-1", 22, "materials"),
        ("網田公民館", "下網田町566-1", 18, "materials"),
        ("宇土市スポーツセンター", "花園町523-2", 198, "materials"),
        ("宇土高校体育館", "古城町63", 300, "materials"),
        ("花園小学校体育館", "古保里町695", 217, "materials"),
        ("花園コミュニティセンター", "古保里町977", 70, "materials"),
        ("花っ子学童クラブ", "古保里町977", 30, "materials"),
        ("宇土小学校体育館", "高柳町104-1", 378, "materials"),
        ("住吉中学校体育館", "笹原町1700", 403, "materials"),
        ("JR住吉駅前駐輪場", "住吉町836-4", 15, "materials"),
        ("住吉漁協会議室", "住吉町875", 30, "flood_plan"),
        ("市民会館", "新小路町123", 963, "materials"),
        ("老人福祉センター", "新小路町138-2", 127, "materials"),
        ("鶴城中学校体育館", "新小路町151", 306, "materials"),
        ("中央公民館", "新小路町96-1", 31, "materials"),
        ("轟地区農業者トレーニングセンター", "石橋町1", 167, "materials"),
        ("轟公民館", "石橋町10-2", 34, "materials"),
        ("走潟地区体育館", "走潟町619-5", 299, "materials"),
        ("走潟小学校体育館", "走潟町743", 321, "materials"),
        ("走潟公民館", "走潟町822", 12, "materials"),
        ("宇土東小学校体育館", "築籠町46", 291, "materials"),
        ("長浜福祉館", "長浜町411-2", 117, "materials"),
        ("網田漁業協同組合", "長浜町508-5", 50, "flood_plan"),
        ("創価学会宇土文化会館", "南段原町130-1", 100, "flood_plan"),
        ("網津公民館網引分館", "網引町790-1", 15, "materials"),
        ("網津防災センター", "網津町1991-1", 69, "materials"),
        ("網津地区多目的研修会施設", "網津町2026-2", 221, "materials"),
        ("網津小学校体育館", "網津町2082-3", 275, "materials"),
        ("あじさいの湯", "網津町2283", 20, "materials"),
        ("緑川地区農業者トレーニングセンター", "野鶴町207-3", 223, "materials"),
        ("緑川小学校体育館", "野鶴町246", 279, "materials"),
        ("緑川公民館", "野鶴町294-1", 13, "materials"),
    ]
    if len(values) != 41:
        raise ValueError("Expected 41 general-shelter capacity rows for Uto City")

    rows: list[dict[str, object]] = []
    for name, address, capacity, variant in values:
        source_url = UTO_MATERIALS_URL if variant == "materials" else UTO_FLOOD_PLAN_URL
        source_title = (
            "宇土市地域防災計画書 第6部 資料編"
            if variant == "materials"
            else "宇土市地域防災計画書 第2部 風水害対策編"
        )
        rows.append(
            {
                "Source Municipality Code": "43211",
                "Source Municipality": "宇土市",
                "Source Facility Name": name,
                "Source Address": f"宇土市{address}",
                "Official Capacity Primary (persons)": float(capacity),
                "Official Capacity Primary Definition": "usable_area_divided_by_3m2_per_person",
                "Official Capacity Secondary (persons)": pd.NA,
                "Official Capacity Secondary Definition": pd.NA,
                "Official Building Area (m2)": pd.NA,
                "Earthquake Opening or Suitability Flag": pd.NA,
                "Earthquake Flag Definition": "not_recovered_in_structured_transcription",
                "Official Source Title": source_title,
                "Official Source Date": "2025",
                "Official Source URL": source_url,
                "Official Source File": pd.NA,
                "Official Source Page": 7 if variant == "materials" else 228,
                "Extraction Note": "manual_structuring_from_official_pdf_web_index",
            }
        )
    return rows


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    EXP.mkdir(parents=True, exist_ok=True)
    data = pd.DataFrame(extract_uki() + extract_yatsushiro() + extract_uto())
    data.insert(0, "Official Source Record ID", [f"CAP-{i:04d}" for i in range(1, len(data) + 1)])

    if data["Official Source Record ID"].duplicated().any():
        raise ValueError("Official source record IDs must be unique")
    if data["Official Capacity Primary (persons)"].isna().all():
        raise ValueError("No official numeric capacities were extracted")

    target = PROCESSED / "kumamoto_prefecture_official_shelter_capacity_sources_preprocessed.parquet"
    data.to_parquet(target, index=False)
    data.to_csv(EXP / "official_capacity_source_records.csv", index=False)

    summary = (
        data.groupby(["Source Municipality Code", "Source Municipality"], as_index=False)
        .agg(
            Official_Source_Facilities=("Official Source Record ID", "size"),
            Facilities_With_Primary_Capacity=("Official Capacity Primary (persons)", "count"),
            Sum_Primary_Capacity=("Official Capacity Primary (persons)", "sum"),
            Facilities_With_Building_Area=("Official Building Area (m2)", "count"),
            Earthquake_Flagged_Facilities=("Earthquake Opening or Suitability Flag", "sum"),
        )
    )
    summary.to_csv(EXP / "official_capacity_source_municipality_summary.csv", index=False)
    print(summary.to_string(index=False))
    print(f"\nWrote {len(data):,} official source records to {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
