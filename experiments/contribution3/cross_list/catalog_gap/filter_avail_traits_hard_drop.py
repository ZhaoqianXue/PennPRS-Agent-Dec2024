#!/usr/bin/env python3
"""
Filter obviously low-value traits from catalog-gap avail_traits.csv.

Current PennPRS catalog-gap triage is focused on stable disease endpoints that
are worth carrying forward into PRS benchmark / transfer analysis. This script
removes "hard drop" ICD roots that are clearly out of scope, including:

- injury / poisoning / external-cause event traits
- symptom / abnormal finding traits
- status / aftercare / susceptibility / encounter traits
- pregnancy / perinatal-specific traits
- postprocedural complication traits
- broad / unspecified umbrella disorders
- acute / exposure-dominant infectious traits
- secondary manifestation / complication traits
- non-specific benign / uncertain neoplasm traits
- residual broad / unspecified disease groups
- organism / etiology auxiliary codes (B95–B97 family)
- selected trivial cosmetic / low-priority misc endpoints

Inputs:
- avail_traits.csv
- NLM Clinical Tables ICD-10-CM API

Outputs:
- avail_traits_hard_drop.csv
- avail_traits_keep.csv
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


CATALOG_GAP_DIR = Path(__file__).resolve().parent

AVAIL_TRAITS_CSV = CATALOG_GAP_DIR / "avail_traits.csv"

HARD_DROP_CSV = CATALOG_GAP_DIR / "avail_traits_hard_drop.csv"
KEEP_CSV = CATALOG_GAP_DIR / "avail_traits_keep.csv"

ICD10CM_API_URL = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
API_PAGE_SIZE = 500
API_TIMEOUT_SECONDS = 20
API_MAX_RETRIES = 3
API_RETRY_BACKOFF_SECONDS = 1.5
API_WORKERS = 4
DISPLAY_STEM_LIMIT = 6


@dataclass(frozen=True)
class DropRule:
    category: str
    reason: str


DROP_RULES: dict[str, DropRule] = {
    "injury_toxic_external": DropRule(
        category="injury_toxic_external",
        reason=(
            "Acute injury, poisoning, external-cause, or procedure-linked event trait. "
            "These are not stable disease endpoints for PRS benchmark or cross-disease transfer."
        ),
    ),
    "symptom_abnormal_finding": DropRule(
        category="symptom_abnormal_finding",
        reason=(
            "Symptom, complaint, or abnormal finding rather than a disease entity. "
            "Phenotype is too nonspecific for disease-level PRS benchmarking."
        ),
    ),
    "status_aftercare_allergy": DropRule(
        category="status_aftercare_allergy",
        reason=(
            "Status / aftercare / susceptibility / encounter code rather than active disease. "
            "These reflect healthcare process or background state, not a stable disease endpoint."
        ),
    ),
    "pregnancy_perinatal": DropRule(
        category="pregnancy_perinatal",
        reason=(
            "Pregnancy- or perinatal-specific trait. This is out of scope for the current general "
            "disease-focused catalog-gap workflow."
        ),
    ),
    "postproc_complication_status": DropRule(
        category="postproc_complication_status",
        reason=(
            "Postprocedural complication / postsurgical state. Signal is dominated by care pathway "
            "and treatment history rather than primary disease risk."
        ),
    ),
    "broad_unspecified_umbrella": DropRule(
        category="broad_unspecified_umbrella",
        reason=(
            "Broad or unspecified umbrella disorder code. Phenotype is too heterogeneous to be a "
            "clean target for catalog-gap PRS triage."
        ),
    ),
    "acute_or_exposure_dominant_infectious": DropRule(
        category="acute_or_exposure_dominant_infectious",
        reason=(
            "Acute or exposure-dominant infectious trait. These are short-horizon event phenotypes "
            "rather than stable disease-risk endpoints for catalog-gap PRS work."
        ),
    ),
    "secondary_manifestation_or_complication": DropRule(
        category="secondary_manifestation_or_complication",
        reason=(
            "Secondary manifestation, physiologic consequence, or complication state rather than a "
            "primary disease endpoint."
        ),
    ),
    "non_specific_benign_or_uncertain_neoplasm": DropRule(
        category="non_specific_benign_or_uncertain_neoplasm",
        reason=(
            "Benign, uncertain-behavior, or otherwise non-specific neoplasm trait. This is not a "
            "clean malignant disease target for the current catalog-gap workflow."
        ),
    ),
    "escaped_broad_unspecified_group": DropRule(
        category="escaped_broad_unspecified_group",
        reason=(
            "Residual broad or unspecified disease group that is still too heterogeneous to act as a "
            "clean catalog-gap PRS target."
        ),
    ),
    "etiology_auxiliary_code": DropRule(
        category="etiology_auxiliary_code",
        reason=(
            "Auxiliary ICD block used to record an infectious agent or organism as the cause of "
            "disease classified elsewhere. This is not a stand-alone disease phenotype for "
            "catalog-gap PRS alignment."
        ),
    ),
    "low_priority_misc_endpoint": DropRule(
        category="low_priority_misc_endpoint",
        reason=(
            "Clinically minor or non-disease cosmetic endpoints with weak interpretability for "
            "disease-level PRS benchmark or cross-trait transfer in this workflow."
        ),
    ),
}

EXTRA_SYMPTOM_CODES = {
    "G89",
    "M25",
    "M54",
    "N23",
}

POSTPROC_COMPLICATION_CODES = {
    "E89",
    "G97",
    "I97",
    "J95",
    "K66",
    "K91",
    "L76",
    "M96",
    "N99",
}

BROAD_UNSPECIFIED_UMBRELLA_CODES = {
    "B99",
    "E07",
    "F09",
    "F99",
    "G95",
    "H57",
    "H69",
    "I99",
    "J34",
    "J38",
    "J39",
    "K08",
    "K14",
    "K31",
    "L98",
    "M85",
    "M89",
    "M94",
    "N50",
    "N64",
    "N72",
}

ACUTE_INFECTIOUS_CODES = {
    "A09",
    "A63",
    "B00",
    "B30",
    "B34",
    "B36",
    "J00",
    "J02",
    "J03",
    "J06",
    "J10",
    "J11",
    "J12",
    "J20",
    "J21",
    "J22",
    "L01",
}

SECONDARY_MANIFESTATION_CODES = {
    "D63",
    "F02",
    "F54",
    "G63",
    "I31",
    "I46",
    "I51",
    "J69",
    "J81",
    "J90",
    "J91",
}

NON_SPECIFIC_NEOPLASM_CODES = {
    "C80",
    "D12",
    "D21",
    "D23",
    "D31",
    "D32",
    "D35",
    "D36",
    "D48",
    "D49",
}

ESCAPED_BROAD_GROUP_CODES = {
    "D89",
    "F98",
    "M12",
    "M13",
    "M71",
    "M79",
    "N88",
    "N90",
}

ETIOLOGY_AUXILIARY_CODES = {
    "B95",
    "B96",
    "B97",
}

LOW_PRIORITY_MISC_CODES = {
    "E65",
    "L84",
}


@dataclass(frozen=True)
class DescriptionRecord:
    display_text: str


def _normalize_icd(code: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", code.upper())


def _request_json(url: str) -> list[object]:
    last_error: Exception | None = None
    for attempt in range(API_MAX_RETRIES):
        try:
            with urllib.request.urlopen(url, timeout=API_TIMEOUT_SECONDS) as response:
                return json.load(response)
        except (TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < API_MAX_RETRIES - 1:
                time.sleep(API_RETRY_BACKOFF_SECONDS * (2**attempt))
    raise RuntimeError(f"Failed to fetch ICD-10-CM data from API: {url}") from last_error


def _fetch_icd10cm_names(icd: str) -> list[str]:
    normalized_icd = _normalize_icd(icd)
    if not normalized_icd:
        return []

    seen_names: set[str] = set()
    names: list[str] = []
    offset = 0

    while True:
        params = {
            "terms": normalized_icd,
            "sf": "code",
            "df": "code,name",
            "count": str(API_PAGE_SIZE),
            "offset": str(offset),
        }
        url = f"{ICD10CM_API_URL}?{urllib.parse.urlencode(params)}"
        payload = _request_json(url)
        rows = payload[3] if len(payload) > 3 and payload[3] else []

        if not rows:
            break

        for row in rows:
            if len(row) < 2:
                continue
            api_code = _normalize_icd(str(row[0]))
            api_name = str(row[1]).strip()
            if not api_name or not api_code.startswith(normalized_icd):
                continue
            if api_name not in seen_names:
                seen_names.add(api_name)
                names.append(api_name)

        if len(rows) < API_PAGE_SIZE:
            break
        offset += API_PAGE_SIZE

    return names


def _stem_description(name: str) -> str:
    stem = name.split(",", 1)[0].strip()
    return re.sub(r"\s+", " ", stem)


def _build_display_description(names: list[str]) -> str:
    stems: list[str] = []
    seen_stems: set[str] = set()

    for name in names:
        stem = _stem_description(name) or name.strip()
        if not stem:
            continue
        key = stem.lower()
        if key in seen_stems:
            continue
        seen_stems.add(key)
        stems.append(stem)

    if not stems:
        return ""
    if len(stems) <= DISPLAY_STEM_LIMIT:
        return " | ".join(stems)
    visible = stems[:DISPLAY_STEM_LIMIT]
    return " | ".join(visible) + f" (+{len(stems) - DISPLAY_STEM_LIMIT} more API-matched stems)"


def _fetch_description_record(icd: str) -> DescriptionRecord:
    names = _fetch_icd10cm_names(icd)
    return DescriptionRecord(display_text=_build_display_description(names))


def load_descriptions(icds: list[str]) -> dict[str, DescriptionRecord]:
    descriptions: dict[str, DescriptionRecord] = {}
    total = len(icds)

    with ThreadPoolExecutor(max_workers=API_WORKERS) as executor:
        futures = {executor.submit(_fetch_description_record, icd): icd for icd in icds}
        completed = 0
        for future in as_completed(futures):
            icd = futures[future]
            descriptions[icd] = future.result()
            completed += 1
            if completed % 50 == 0 or completed == total:
                print(f"Fetched ICD-10-CM API descriptions: {completed}/{total}", flush=True)

    return descriptions


def classify_hard_drop(icd: str) -> str | None:
    if re.match(r"^[STVWXY]", icd):
        return "injury_toxic_external"
    if icd.startswith("R"):
        return "symptom_abnormal_finding"
    if icd.startswith("Z"):
        return "status_aftercare_allergy"
    if icd.startswith("O"):
        return "pregnancy_perinatal"
    if icd in EXTRA_SYMPTOM_CODES:
        return "symptom_abnormal_finding"
    if icd in POSTPROC_COMPLICATION_CODES:
        return "postproc_complication_status"
    if icd in ETIOLOGY_AUXILIARY_CODES:
        return "etiology_auxiliary_code"
    if icd in LOW_PRIORITY_MISC_CODES:
        return "low_priority_misc_endpoint"
    if icd in BROAD_UNSPECIFIED_UMBRELLA_CODES:
        return "broad_unspecified_umbrella"
    if icd in ACUTE_INFECTIOUS_CODES:
        return "acute_or_exposure_dominant_infectious"
    if icd in SECONDARY_MANIFESTATION_CODES:
        return "secondary_manifestation_or_complication"
    if icd in NON_SPECIFIC_NEOPLASM_CODES:
        return "non_specific_benign_or_uncertain_neoplasm"
    if icd in ESCAPED_BROAD_GROUP_CODES:
        return "escaped_broad_unspecified_group"

    return None


def load_avail_icds(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [(row.get("icd") or "").strip() for row in reader if (row.get("icd") or "").strip()]


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    avail_icds = load_avail_icds(AVAIL_TRAITS_CSV)
    descriptions = load_descriptions(avail_icds)

    hard_drop_rows: list[dict[str, str]] = []
    keep_rows: list[dict[str, str]] = []

    for icd in avail_icds:
        description_record = descriptions.get(icd, DescriptionRecord(display_text=""))
        drop_category = classify_hard_drop(icd)

        if drop_category is None:
            keep_rows.append(
                {
                    "icd": icd,
                    "description": description_record.display_text,
                }
            )
            continue

        rule = DROP_RULES[drop_category]
        hard_drop_rows.append(
            {
                "icd": icd,
                "description": description_record.display_text,
                "drop_category": rule.category,
                "drop_reason": rule.reason,
            }
        )

    write_rows(
        HARD_DROP_CSV,
        ["icd", "description", "drop_category", "drop_reason"],
        hard_drop_rows,
    )
    write_rows(
        KEEP_CSV,
        ["icd", "description"],
        keep_rows,
    )

    print(f"Input traits: {len(avail_icds)}")
    print(f"Hard-drop traits: {len(hard_drop_rows)}")
    print(f"Kept traits: {len(keep_rows)}")

    counts: dict[str, int] = {}
    for row in hard_drop_rows:
        category = row["drop_category"]
        counts[category] = counts.get(category, 0) + 1

    print("Drop counts by category:")
    for category in sorted(counts):
        print(f"  {category}: {counts[category]}")


if __name__ == "__main__":
    main()
