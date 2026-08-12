"""Audit capacity-evidence readiness for all Kumamoto Prefecture shelters.

This script does not construct or impute capacity.  It separates three different
states that must not be conflated:

1. a shelter has a numeric capacity reported by an official source;
2. a shelter has an official facility-area source; and
3. a shelter can only be linked to an official school/public-facility identity.

The existing Kumamoto City area audit is retained as a validated subset.  School
and public-facility point datasets are used only to identify likely source families;
they contain no floor area and therefore are not capacity evidence by themselves.
"""

from __future__ import annotations

import math
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
from shapely import wkb


ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "data" / "raw" / "prior_projects"
OUT = ROOT / "data" / "exp" / "prefecture-shelter-capacity-audit"

SHELTERS = PRIOR / "KE01" / "kumamoto_designated_shelters_geospatial_preprocessed.parquet"
ADMIN = PRIOR / "KE01b" / "kumamoto_administrative_areas_preprocessed.parquet"
SCHOOLS = PRIOR / "KE01c" / "schools_preprocessed.parquet"
PUBLIC_FACILITIES = PRIOR / "KE01c" / "public_facilities_preprocessed.parquet"
CITY_AUDIT = OUT.parent / "shelter-capacity-audit" / "shelter_capacity_source_audit.parquet"
OFFICIAL_CAPACITY_SOURCES = (
    ROOT
    / "data"
    / "processed"
    / "kumamoto_prefecture_official_shelter_capacity_sources_preprocessed.parquet"
)

# JMA CMT hypocenter for the 28 July 2026 16:27 earthquake.
HYPOCENTER_LAT = 32 + 37.5 / 60
HYPOCENTER_LON = 130 + 40.7 / 60


def clean_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return unicodedata.normalize("NFKC", str(value)).replace("\n", "").strip()


def primary_facility_name(value: object) -> str:
    """Remove annotations that describe backup rooms or operating conditions."""
    text = clean_text(value)
    text = re.split(r"[（(](?:予備|指定|福祉|一時|旧称|旧)[：:]?", text, maxsplit=1)[0]
    return text.strip(" ・")


def normalize_name(value: object, *, school_key: bool = False) -> str:
    text = primary_facility_name(value)
    text = text.replace("壼", "壺").replace("ヶ", "ケ").replace("ヵ", "カ")
    text = text.replace("高等学校", "高校").replace("中等教育学校", "中等教育校")
    text = re.sub(r"[\s・･,，.。/／・（）()\-‐―ー]", "", text)
    if school_key:
        # The school registry commonly includes the operator prefix while shelter
        # inventories usually do not.  Restrict this removal to school-like names.
        if re.search(r"(幼稚園|小学校|中学校|高校|高専|大学|支援学校|養護学校)", text):
            text = re.sub(r"^(?:熊本県|[^立]{1,10}[市町村])立", "", text)
        text = re.sub(
            r"(?:体育館|屋内運動場|運動場|グラウンド|校舎|武道場|講堂|多目的ホール)$",
            "",
            text,
        )
    return text


def facility_type(value: object) -> str:
    name = clean_text(value)
    if re.search(r"(小学校|中学校|義務教育学校|中等教育学校|高校|高等学校|高専|大学|支援学校|養護学校|学校体育館|分校)", name):
        return "school_or_university"
    if re.search(r"(体育館|運動公園|スポーツ|競技場|武道館|武道場|アリーナ|ドーム|プール|グラウンド|運動場|B&G)", name, flags=re.IGNORECASE):
        return "sports_facility"
    if re.search(r"(公民館|コミュニティ|集会所|自治会館|交流館|交流センター|地域センター|研修センター|地区センター)", name):
        return "community_or_assembly"
    if re.search(r"(福祉|保健|老人|高齢者|デイサービス|介護|障害|こども|児童|保育|幼稚園|病院|診療所)", name):
        return "health_welfare_or_childcare"
    if re.search(r"(市役所|町役場|村役場|庁舎|支所|出張所|振興局|消防|警察)", name):
        return "government_or_emergency"
    if re.search(r"(文化|ホール|会館|図書館|博物館|資料館|記念館|センター)", name):
        return "cultural_or_multiuse"
    if re.search(r"(寺|神社|教会)", name):
        return "religious_facility"
    if re.search(r"(ホテル|旅館|店舗|事業所|工場|会社)", name):
        return "private_or_commercial"
    return "other"


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_m = 6_371_008.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius_m * math.asin(math.sqrt(a))


def decode_point(value: object) -> tuple[float, float]:
    geom = wkb.loads(bytes(value)) if isinstance(value, (bytes, bytearray, memoryview)) else value
    return float(geom.y), float(geom.x)


def similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def source_identity_key(value: object, municipality: str) -> str:
    text = primary_facility_name(value)
    text = text.replace(municipality, "")
    text = re.sub(r"^(?:熊本県)?(?:市|町|村)?立", "", text)
    text = text.replace("高等学校", "高校").replace("中等教育学校", "中等教育校")
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"[\s・･,，.。/／（）()\-‐―ー]", "", text)


def address_key(value: object) -> str:
    text = unicodedata.normalize("NFKC", clean_text(value))
    text = text.replace("熊本県", "").replace("番地", "-")
    text = re.sub(r"[\s,，.。‐－−―ー]", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def official_capacity_match(
    shelter_name: str,
    shelter_address: str,
    municipality_code: str,
    municipality: str,
    candidates: pd.DataFrame,
) -> dict[str, object] | None:
    subset = candidates[
        candidates["Source Municipality Code"].astype("string").eq(municipality_code)
    ]
    if subset.empty:
        return None
    name_key = source_identity_key(shelter_name, municipality)
    shelter_address_key = address_key(shelter_address)
    options: list[tuple[tuple[object, ...], pd.Series, float, bool]] = []
    exact_address_count = 0
    for _, candidate in subset.iterrows():
        candidate_address_key = address_key(candidate["Source Address"])
        address_exact = shelter_address_key == candidate_address_key
        if address_exact:
            exact_address_count += 1
        name_score = similarity(
            name_key,
            source_identity_key(candidate["Source Facility Name"], municipality),
        )
        rank = (0 if address_exact else 1, -name_score)
        options.append((rank, candidate, name_score, address_exact))
    options.sort(key=lambda item: item[0])
    _, selected, name_score, address_exact = options[0]
    selected_key = source_identity_key(selected["Source Facility Name"], municipality)
    name_exact = bool(name_key and name_key == selected_key)
    accepted = (
        name_exact
        or (address_exact and exact_address_count == 1)
        or (address_exact and name_score >= 0.35)
    )
    if not accepted:
        return None
    result = selected.to_dict()
    result["Source Match Name Similarity"] = name_score
    result["Source Match Address Exact"] = address_exact
    return result


def nearest_identity_match(
    shelter_name: str,
    shelter_lat: float,
    shelter_lon: float,
    candidates: pd.DataFrame,
    *,
    school: bool,
) -> dict[str, object]:
    target_key = normalize_name(shelter_name, school_key=school)
    best: dict[str, object] | None = None
    for candidate in candidates.itertuples(index=False):
        name = candidate.name
        lat = candidate.latitude
        lon = candidate.longitude
        distance = haversine_m(shelter_lat, shelter_lon, lat, lon)
        if distance > 1_000:
            continue
        key = normalize_name(name, school_key=school)
        score = similarity(target_key, key)
        exact = bool(target_key and target_key == key)
        # A spatially close fuzzy match is useful for audit routing, while an exact
        # normalized name may tolerate a larger coordinate displacement.
        accepted = (exact and distance <= 1_000) or (score >= 0.72 and distance <= 250)
        rank = (0 if accepted else 1, 0 if exact else 1, -score, distance)
        if best is None or rank < best["_rank"]:
            best = {
                "_rank": rank,
                "accepted": accepted,
                "exact": exact,
                "score": score,
                "distance": distance,
                "name": clean_text(name),
                "id": clean_text(candidate.identifier),
            }
    if best is None:
        return {
            "accepted": False,
            "exact": False,
            "score": pd.NA,
            "distance": pd.NA,
            "name": pd.NA,
            "id": pd.NA,
        }
    best.pop("_rank")
    return best


def load_point_candidates(
    path: Path, geometry_column: str, name_column: str, id_column: str
) -> pd.DataFrame:
    frame = pd.read_parquet(path).copy()
    coordinates = frame[geometry_column].map(decode_point)
    return pd.DataFrame(
        {
            "identifier": frame[id_column].map(clean_text),
            "name": frame[name_column].map(clean_text),
            "latitude": coordinates.str[0],
            "longitude": coordinates.str[1],
        }
    )


def municipality_lookup() -> dict[str, str]:
    admin = pd.read_parquet(ADMIN)
    lookup = {
        clean_text(row["Municipality Code"]): clean_text(row["Municipality Name"])
        for _, row in admin.iterrows()
    }
    # Designated-shelter IDs use the citywide code, while the admin polygons use
    # the five ward codes.
    lookup["43100"] = "熊本市"
    return lookup


def city_evidence_lookup() -> dict[str, dict[str, object]]:
    if not CITY_AUDIT.exists():
        return {}
    city = pd.read_parquet(CITY_AUDIT)
    return city.set_index("Shelter ID").to_dict(orient="index")


def evidence_tier(row: pd.Series) -> str:
    if pd.notna(row["Official Numeric Capacity"]):
        return "A_numeric_capacity"
    if pd.notna(row["Documented Area (m2)"]):
        basis = clean_text(row["Documented Area Basis"])
        if basis == "gymnasium_floor_area":
            return "B_gymnasium_area"
        return "C_gross_facility_area"
    if bool(row["School Identity Match"]):
        return "D_school_identity_only"
    if bool(row["Public Facility Identity Match"]):
        return "E_public_facility_identity_only"
    return "F_no_capacity_source_link"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    shelters = pd.read_parquet(SHELTERS).copy()
    schools = load_point_candidates(SCHOOLS, "Geometry", "School Name", "School Facility ID")
    public = load_point_candidates(
        PUBLIC_FACILITIES, "Geometry", "Public Facility Name", "Public Facility ID"
    )
    municipality_names = municipality_lookup()
    city_evidence = city_evidence_lookup()
    official_sources = (
        pd.read_parquet(OFFICIAL_CAPACITY_SOURCES)
        if OFFICIAL_CAPACITY_SOURCES.exists()
        else pd.DataFrame()
    )

    rows: list[dict[str, object]] = []
    for _, shelter in shelters.iterrows():
        shelter_id = clean_text(shelter["Common ID"])
        name = clean_text(shelter["Facility Name"])
        address = clean_text(shelter["Address"])
        accepted_persons = clean_text(shelter["Accepted Persons"])
        lat = float(shelter["Latitude"])
        lon = float(shelter["Longitude"])
        code = shelter_id[1:6]
        municipality = municipality_names.get(code, "Unknown")
        ward_match = re.search(r"熊本市(中央区|東区|西区|南区|北区)", address)
        ward = ward_match.group(1) if ward_match else pd.NA

        official = official_capacity_match(
            name,
            address,
            code,
            municipality,
            official_sources,
        )

        school_match = nearest_identity_match(
            name,
            lat,
            lon,
            schools,
            school=True,
        )
        public_match = nearest_identity_match(
            name,
            lat,
            lon,
            public,
            school=False,
        )

        city = city_evidence.get(shelter_id, {})
        official_capacity = (
            official.get("Official Capacity Primary (persons)", pd.NA)
            if official is not None
            else pd.NA
        )
        official_secondary_capacity = (
            official.get("Official Capacity Secondary (persons)", pd.NA)
            if official is not None
            else pd.NA
        )
        official_area = (
            official.get("Official Building Area (m2)", pd.NA)
            if official is not None
            else pd.NA
        )
        city_area = city.get("Source Area (m2)", pd.NA)
        area = official_area if pd.notna(official_area) else city_area
        if pd.notna(official_area):
            basis = "official_building_area_with_separate_published_capacity"
        else:
            basis = city.get("Area Basis", pd.NA)
        source_title = (
            official.get("Official Source Title", pd.NA)
            if official is not None
            else city.get("Source Title", pd.NA)
        )
        source_file = (
            official.get("Official Source File", pd.NA)
            if official is not None
            else city.get("Source File", pd.NA)
        )
        source_page = (
            official.get("Official Source Page", pd.NA)
            if official is not None
            else city.get("Source Page", pd.NA)
        )

        rows.append(
            {
                "Shelter ID": shelter_id,
                "Shelter Name": name,
                "Address": address,
                "Latitude": lat,
                "Longitude": lon,
                "Municipality Code": code,
                "Municipality": municipality,
                "Ward": ward,
                "Facility Type": facility_type(name),
                "Shelter Service Class": (
                    "welfare_specific" if accepted_persons else "general"
                ),
                "Accepted Persons Description": accepted_persons or pd.NA,
                "Hypocentral Distance (km)": haversine_m(lat, lon, HYPOCENTER_LAT, HYPOCENTER_LON) / 1_000,
                "Official Numeric Capacity": official_capacity,
                "Official Capacity Definition": (
                    official.get("Official Capacity Primary Definition", pd.NA)
                    if official is not None
                    else pd.NA
                ),
                "Official Secondary Capacity": official_secondary_capacity,
                "Official Secondary Capacity Definition": (
                    official.get("Official Capacity Secondary Definition", pd.NA)
                    if official is not None
                    else pd.NA
                ),
                "Official Earthquake Opening or Suitability Flag": (
                    official.get("Earthquake Opening or Suitability Flag", pd.NA)
                    if official is not None
                    else pd.NA
                ),
                "Official Earthquake Flag Definition": (
                    official.get("Earthquake Flag Definition", pd.NA)
                    if official is not None
                    else pd.NA
                ),
                "Official Capacity Source Record ID": (
                    official.get("Official Source Record ID", pd.NA)
                    if official is not None
                    else pd.NA
                ),
                "Official Source Match Name Similarity": (
                    official.get("Source Match Name Similarity", pd.NA)
                    if official is not None
                    else pd.NA
                ),
                "Official Source Match Address Exact": (
                    official.get("Source Match Address Exact", pd.NA)
                    if official is not None
                    else pd.NA
                ),
                "Documented Area (m2)": area,
                "Documented Area Basis": basis,
                "Area Source Title": source_title,
                "Area Source File": source_file,
                "Area Source Page": clean_text(source_page) or pd.NA,
                "School Identity Match": school_match["accepted"],
                "Matched School ID": school_match["id"],
                "Matched School Name": school_match["name"],
                "School Name Similarity": school_match["score"],
                "School Match Distance (m)": school_match["distance"],
                "Public Facility Identity Match": public_match["accepted"],
                "Matched Public Facility ID": public_match["id"],
                "Matched Public Facility Name": public_match["name"],
                "Public Facility Name Similarity": public_match["score"],
                "Public Facility Match Distance (m)": public_match["distance"],
            }
        )

    audit = pd.DataFrame(rows)
    audit["Capacity Evidence Tier"] = audit.apply(evidence_tier, axis=1)
    audit["Has Area or Numeric Capacity Evidence"] = audit["Capacity Evidence Tier"].str.startswith(("A_", "B_", "C_"))
    audit["Has Source Identity Link"] = (
        audit["Has Area or Numeric Capacity Evidence"]
        | audit["School Identity Match"]
        | audit["Public Facility Identity Match"]
    )
    source_multiplicity = audit["Official Capacity Source Record ID"].value_counts(dropna=True)
    audit["Official Capacity Source Match Multiplicity"] = (
        audit["Official Capacity Source Record ID"].map(source_multiplicity).astype("Int64")
    )
    audit["Official Capacity Must Be Deduplicated"] = (
        audit["Official Capacity Source Match Multiplicity"].fillna(0).gt(1)
    )

    if len(audit) != 1_315 or audit["Shelter ID"].nunique() != 1_315:
        raise ValueError("The prefecture shelter master must contain 1,315 unique IDs")
    if audit["Municipality"].eq("Unknown").any():
        missing = audit.loc[audit["Municipality"].eq("Unknown"), "Municipality Code"].unique()
        raise ValueError(f"Missing municipality lookup for {missing.tolist()}")

    audit.to_parquet(OUT / "prefecture_shelter_capacity_evidence_audit.parquet", index=False)
    audit.to_csv(OUT / "prefecture_shelter_capacity_evidence_audit.csv", index=False)

    municipal = (
        audit.groupby(["Municipality Code", "Municipality"], as_index=False)
        .agg(
            Designated_Shelters=("Shelter ID", "size"),
            Minimum_Hypocentral_Distance_km=("Hypocentral Distance (km)", "min"),
            Median_Hypocentral_Distance_km=("Hypocentral Distance (km)", "median"),
            Shelters_With_Area_or_Numeric_Capacity=("Has Area or Numeric Capacity Evidence", "sum"),
            Shelters_With_School_Identity=("School Identity Match", "sum"),
            Shelters_With_Public_Facility_Identity=("Public Facility Identity Match", "sum"),
            Shelters_With_Any_Source_Link=("Has Source Identity Link", "sum"),
        )
        .sort_values(["Minimum_Hypocentral_Distance_km", "Municipality"])
    )
    municipal["Area_or_Numeric_Evidence_Percent"] = (
        100 * municipal["Shelters_With_Area_or_Numeric_Capacity"] / municipal["Designated_Shelters"]
    )
    municipal["Any_Source_Link_Percent"] = (
        100 * municipal["Shelters_With_Any_Source_Link"] / municipal["Designated_Shelters"]
    )
    service_counts = (
        audit.assign(
            General_Shelter=audit["Shelter Service Class"].eq("general"),
            Welfare_Shelter=audit["Shelter Service Class"].eq("welfare_specific"),
            General_With_Numeric_Capacity=(
                audit["Shelter Service Class"].eq("general")
                & audit["Official Numeric Capacity"].notna()
            ),
            General_With_Area_or_Numeric_Evidence=(
                audit["Shelter Service Class"].eq("general")
                & audit["Has Area or Numeric Capacity Evidence"]
            ),
            Welfare_With_Numeric_Capacity=(
                audit["Shelter Service Class"].eq("welfare_specific")
                & audit["Official Numeric Capacity"].notna()
            ),
        )
        .groupby(["Municipality Code", "Municipality"], as_index=False)
        .agg(
            General_Shelters=("General_Shelter", "sum"),
            Welfare_Shelters=("Welfare_Shelter", "sum"),
            General_Shelters_With_Numeric_Capacity=("General_With_Numeric_Capacity", "sum"),
            General_Shelters_With_Area_or_Numeric_Evidence=(
                "General_With_Area_or_Numeric_Evidence",
                "sum",
            ),
            Welfare_Shelters_With_Numeric_Capacity=("Welfare_With_Numeric_Capacity", "sum"),
        )
    )
    municipal = municipal.merge(
        service_counts, on=["Municipality Code", "Municipality"], how="left", validate="1:1"
    )
    municipal["General_Numeric_Capacity_Coverage_Percent"] = (
        100
        * municipal["General_Shelters_With_Numeric_Capacity"]
        / municipal["General_Shelters"].replace(0, pd.NA)
    )
    municipal["General_Capacity_Evidence_Coverage_Percent"] = (
        100
        * municipal["General_Shelters_With_Area_or_Numeric_Evidence"]
        / municipal["General_Shelters"].replace(0, pd.NA)
    )
    municipal.to_csv(OUT / "municipality_capacity_evidence_summary.csv", index=False)

    facility_summary = (
        audit.groupby("Facility Type", as_index=False)
        .agg(
            Designated_Shelters=("Shelter ID", "size"),
            Shelters_With_Area_or_Numeric_Capacity=("Has Area or Numeric Capacity Evidence", "sum"),
            Shelters_With_School_Identity=("School Identity Match", "sum"),
            Shelters_With_Public_Facility_Identity=("Public Facility Identity Match", "sum"),
            Shelters_With_Any_Source_Link=("Has Source Identity Link", "sum"),
        )
        .sort_values("Designated_Shelters", ascending=False)
    )
    facility_summary["Area_or_Numeric_Evidence_Percent"] = (
        100 * facility_summary["Shelters_With_Area_or_Numeric_Capacity"] / facility_summary["Designated_Shelters"]
    )
    facility_summary["Any_Source_Link_Percent"] = (
        100 * facility_summary["Shelters_With_Any_Source_Link"] / facility_summary["Designated_Shelters"]
    )
    facility_summary.to_csv(OUT / "facility_type_capacity_evidence_summary.csv", index=False)

    tier_summary = (
        audit.groupby("Capacity Evidence Tier", as_index=False)
        .agg(Shelters=("Shelter ID", "size"))
        .sort_values("Capacity Evidence Tier")
    )
    tier_summary["Percent"] = 100 * tier_summary["Shelters"] / len(audit)
    tier_summary.to_csv(OUT / "capacity_evidence_tier_summary.csv", index=False)

    numeric_count = int(audit["Official Numeric Capacity"].notna().sum())
    readme = f"""# Kumamoto Prefecture shelter capacity-evidence audit

## Purpose

This is a source-readiness audit for all {len(audit):,} designated shelters in Kumamoto
Prefecture. It does **not** impute capacity and does not treat a school/public-facility point
match as area evidence.

## Current evidence state

{tier_summary.to_markdown(index=False, floatfmt='.1f')}

- Numeric official shelter capacities recovered and matched: {numeric_count:,}.
- Official facility-area evidence currently comes only from the validated Kumamoto City
  subset and the official Uki City source. Those values must not be extrapolated mechanically
  to other municipalities.
- General and welfare-specific shelters are retained as separate service classes. Welfare
  capacity must not be added to general-population capacity without an explicit demand class
  and a documented non-duplication rule.
- School and public-facility identity matches identify the most promising official source
  family for further acquisition; the source point files do not contain floor area.
- `Accepted Persons` in the shelter master describes eligible groups for welfare shelters,
  not a numeric accommodation capacity.

## Municipality priority

Municipalities are sorted by minimum shelter distance to the JMA hypocenter. This supports
targeted source recovery near the earthquake before expanding to the rest of the prefecture.

## Matching rule

Candidate identities are accepted when normalized names are exact within 1 km, or when name
similarity is at least 0.72 within 250 m. These are routing links for manual/source audit, not
proof that the entire building or campus is usable for accommodation.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    print(tier_summary.to_string(index=False))
    print("\nNearest municipalities:")
    print(municipal.head(12).to_string(index=False))
    print("\nFacility types:")
    print(facility_summary.to_string(index=False))


if __name__ == "__main__":
    main()
