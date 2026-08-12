"""Extract discrete official shelter-use snapshots for the 2026 Kumamoto earthquake.

The four prefectural disaster-headquarters reports are used as event benchmarks,
not as a continuous time series.  Counts are extracted from the report text and
checked against the figures printed on the visually reviewed summary pages.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pdfplumber


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "kumamoto_2026_event_reports"
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "data" / "exp" / "prefecture-shelter-capacity-audit"

EARTHQUAKE_TIMESTAMP = pd.Timestamp("2026-07-28 16:27:00", tz="Asia/Tokyo")

REPORTS = [
    {
        "filename": "2026-07-28_2200_hq_materials.pdf",
        "meeting_timestamp": "2026-07-28 22:00:00",
        "observation_timestamp": "2026-07-28 22:00:00",
        "summary_page": 2,
        "expected_open_shelters": 466,
        "expected_households": 2180,
        "expected_evacuees": 4744,
        "source_url": "https://www.pref.kumamoto.jp/uploaded/attachment/315400.pdf",
    },
    {
        "filename": "2026-07-29_0930_hq_materials.pdf",
        "meeting_timestamp": "2026-07-29 09:30:00",
        "observation_timestamp": "2026-07-29 09:30:00",
        "summary_page": 1,
        "expected_open_shelters": 465,
        "expected_households": None,
        "expected_evacuees": 9872,
        "source_url": "https://www.pref.kumamoto.jp/uploaded/attachment/315465.pdf",
    },
    {
        "filename": "2026-07-29_1600_hq_materials.pdf",
        "meeting_timestamp": "2026-07-29 16:00:00",
        "observation_timestamp": "2026-07-29 14:00:00",
        "summary_page": 3,
        "expected_open_shelters": 432,
        "expected_households": None,
        "expected_evacuees": 8886,
        "source_url": "https://www.pref.kumamoto.jp/uploaded/attachment/315507.pdf",
    },
    {
        "filename": "2026-07-30_0930_hq_materials.pdf",
        "meeting_timestamp": "2026-07-30 09:30:00",
        "observation_timestamp": "2026-07-30 07:30:00",
        "summary_page": 3,
        "expected_open_shelters": 415,
        "expected_households": None,
        "expected_evacuees": 10467,
        "source_url": "https://www.pref.kumamoto.jp/uploaded/attachment/315599.pdf",
    },
]


def normalize_text(value: str) -> str:
    """Normalize full-width digits and spacing while preserving Japanese labels."""
    translation = str.maketrans("０１２３４５６７８９，：", "0123456789,:")
    return re.sub(r"[ \u3000]+", "", value.translate(translation))


def first_integer(patterns: list[str], text: str) -> int | None:
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1).replace(",", ""))
    return None


def extract_summary(path: Path, page_number: int) -> dict[str, int | None]:
    with pdfplumber.open(path) as pdf:
        text = normalize_text(pdf.pages[page_number - 1].extract_text() or "")

    return {
        "open_shelters": first_integer(
            [r"避難所開設数[:：]?([0-9,]+)カ所", r"避難所は[0-9,]+市町村で([0-9,]+)カ所開設"],
            text,
        ),
        "households": first_integer([r"([0-9,]+)世帯、?[0-9,]+人が避難"], text),
        "evacuees": first_integer(
            [r"避難者数[:：]?([0-9,]+)名", r"[0-9,]+世帯、?([0-9,]+)人が避難"],
            text,
        ),
    }


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    for report in REPORTS:
        path = RAW / report["filename"]
        extracted = extract_summary(path, int(report["summary_page"]))
        for key in ("open_shelters", "households", "evacuees"):
            expected = report[f"expected_{key}"]
            if extracted[key] != expected:
                raise ValueError(
                    f"{path.name}: extracted {key}={extracted[key]!r}, expected {expected!r}"
                )

        meeting = pd.Timestamp(str(report["meeting_timestamp"]), tz="Asia/Tokyo")
        observed = pd.Timestamp(str(report["observation_timestamp"]), tz="Asia/Tokyo")
        rows.append(
            {
                "Observation Timestamp": observed,
                "Meeting Timestamp": meeting,
                "Hours Since Earthquake": (observed - EARTHQUAKE_TIMESTAMP).total_seconds() / 3600,
                "Open Shelters": extracted["open_shelters"],
                "Reported Households": extracted["households"],
                "Reported Evacuees": extracted["evacuees"],
                "Geographic Coverage": "Kumamoto Prefecture aggregate",
                "Municipality Detail Available": False,
                "Interpretation": "Discrete observed-use benchmark; not a continuous time series",
                "Source Agency": "Kumamoto Prefectural Government",
                "Source Report": path.name,
                "Source Summary Page": report["summary_page"],
                "Source URL": report["source_url"],
            }
        )

    snapshots = pd.DataFrame(rows).sort_values("Observation Timestamp")
    snapshots["Highest Observed within Available 0-72h Snapshots"] = (
        snapshots["Reported Evacuees"] == snapshots["Reported Evacuees"].max()
    )

    parquet = PROCESSED / "kumamoto_2026_official_shelter_use_snapshots_preprocessed.parquet"
    csv = OUT / "official_event_shelter_use_snapshots.csv"
    snapshots.to_parquet(parquet, index=False)
    snapshots.to_csv(csv, index=False)

    readme = OUT / "official_event_shelter_use_snapshots_README.md"
    readme.write_text(
        """# Official event shelter-use snapshots\n\n"
        "Four Kumamoto Prefectural Government disaster-headquarters reports provide "
        "discrete prefecture-wide shelter-use observations in the first 0-72 hours. "
        "They are retained as validation and observed-use benchmarks, not modeled as "
        "a continuous time series. The highest value in the available reports is "
        "10,467 evacuees at 07:30 JST on 30 July 2026, 39.05 hours after the earthquake. "
        "Because the reports provide no municipality-level evacuee table, the aggregate "
        "counts must not be spatially allocated and presented as observed municipal use.\n"
        """,
        encoding="utf-8",
    )

    print(snapshots[["Observation Timestamp", "Open Shelters", "Reported Evacuees"]].to_string(index=False))
    print(f"\nWrote {parquet.relative_to(ROOT)}")
    print(f"Wrote {csv.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
