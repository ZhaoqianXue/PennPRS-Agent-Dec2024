from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from experiments.contribution3.cross_optimized.data_contract import (
    SCHEMA_VERSION,
    CompactBundleRecord,
    CompactPgsRecord,
    clean_text,
    compact_text,
    split_multi_value,
    unique_preserve_order,
)
from experiments.contribution3.cross_optimized.paths import (
    DEFAULT_COMPACT_CATALOG_JSON,
    PGS_EFO_TRAITS_CSV,
    PGS_EVALUATION_SAMPLE_SETS_CSV,
    PGS_PERFORMANCE_METRICS_CSV,
    PGS_SCORES_CSV,
)


CONTINUOUS_HINTS = {
    "measurement",
    "count",
    "level",
    "ratio",
    "index",
    "height",
    "amount",
    "quantity",
    "mass",
    "density",
    "status",
    "consumption",
    "pressure",
    "rate",
    "volume",
    "concentration",
    "percentage",
    "body mass",
    "weight",
    "hemoglobin",
    "cholesterol",
    "protein",
    "cell",
    "bmi",
}


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return slug or "unknown"


def infer_bundle_type(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9\s]", " ", (label or "").lower())
    return "continuous" if any(hint in normalized for hint in CONTINUOUS_HINTS) else "binary"


def _safe_int(raw: Any) -> int | None:
    try:
        if raw is None or pd.isna(raw):
            return None
        return int(float(raw))
    except Exception:
        return None


def _safe_float(raw: Any) -> float | None:
    text = clean_text(raw)
    if not text:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?", text, re.IGNORECASE)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _max_metric(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return max(present) if present else None


def _max_abs_metric(values: list[float | None]) -> float | None:
    present = [abs(value) for value in values if value is not None]
    return max(present) if present else None


def _r2_from_other_metric(raw: Any) -> float | None:
    text = clean_text(raw)
    if not text:
        return None
    normalized = text.lower().replace("r²", "r2").replace("r-squared", "r2")
    if "r2" not in normalized:
        return None
    values: list[float] = []
    for match in re.finditer(r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?", normalized, re.IGNORECASE):
        try:
            value = float(match.group(0))
        except ValueError:
            continue
        if 0 <= value <= 1:
            values.append(value)
    return max(values) if values else None


def _load_sample_set_summaries(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    summaries: dict[tuple[str, str], dict[str, Any]] = {}
    for _, row in df.iterrows():
        pgs_id = clean_text(row.get("Polygenic Score (PGS) ID"))
        sample_set_id = clean_text(row.get("PGS Sample Set (PSS)"))
        if not pgs_id or not sample_set_id:
            continue
        summaries[(pgs_id, sample_set_id)] = {
            "n": _safe_int(row.get("Number of Individuals")) or 0,
            "cases": _safe_int(row.get("Number of Cases")) or 0,
            "controls": _safe_int(row.get("Number of Controls")) or 0,
            "ancestry": clean_text(row.get("Broad Ancestry Category")),
        }
    return summaries


def _load_performance_summaries(
    *,
    performance_metrics_csv: Path,
    evaluation_sample_sets_csv: Path,
) -> dict[str, dict[str, Any]]:
    if not performance_metrics_csv.exists():
        return {}
    metrics = pd.read_csv(performance_metrics_csv)
    sample_sets = _load_sample_set_summaries(evaluation_sample_sets_csv)
    by_pgs: dict[str, dict[str, Any]] = {}
    sample_keys_by_pgs: dict[str, set[tuple[str, str]]] = {}
    ancestry_by_pgs: dict[str, set[str]] = {}

    for _, row in metrics.iterrows():
        pgs_id = clean_text(row.get("Evaluated Score"))
        if not pgs_id:
            continue
        summary = by_pgs.setdefault(
            pgs_id,
            {
                "performance_record_count": 0,
                "sample_set_count": 0,
                "evaluation_sample_total": 0,
                "evaluation_sample_max": 0,
                "best_auc": None,
                "best_r2": None,
                "best_hr": None,
                "best_or": None,
                "best_abs_beta": None,
                "evaluation_ancestry": [],
            },
        )
        summary["performance_record_count"] += 1
        summary["best_auc"] = _max_metric(
            [
                summary.get("best_auc"),
                _safe_float(row.get("Area Under the Receiver-Operating Characteristic Curve (AUROC)")),
                _safe_float(row.get("Concordance Statistic (C-index)")),
            ]
        )
        summary["best_r2"] = _max_metric([summary.get("best_r2"), _r2_from_other_metric(row.get("Other Metric(s)"))])
        summary["best_hr"] = _max_metric([summary.get("best_hr"), _safe_float(row.get("Hazard Ratio (HR)"))])
        summary["best_or"] = _max_metric([summary.get("best_or"), _safe_float(row.get("Odds Ratio (OR)"))])
        summary["best_abs_beta"] = _max_abs_metric([summary.get("best_abs_beta"), _safe_float(row.get("Beta"))])

        sample_set_id = clean_text(row.get("PGS Sample Set (PSS)"))
        sample_key = (pgs_id, sample_set_id)
        if sample_set_id and sample_key in sample_sets:
            sample_keys_by_pgs.setdefault(pgs_id, set()).add(sample_key)
            ancestry = clean_text(sample_sets[sample_key].get("ancestry"))
            if ancestry:
                ancestry_by_pgs.setdefault(pgs_id, set()).add(ancestry)

    for pgs_id, sample_keys in sample_keys_by_pgs.items():
        summary = by_pgs[pgs_id]
        sample_rows = [sample_sets[key] for key in sample_keys]
        sample_counts = [int(row.get("n") or 0) for row in sample_rows]
        summary["sample_set_count"] = len(sample_rows)
        summary["evaluation_sample_total"] = sum(sample_counts)
        summary["evaluation_sample_max"] = max(sample_counts) if sample_counts else 0
        summary["evaluation_ancestry"] = sorted(ancestry_by_pgs.get(pgs_id, set()))

    return by_pgs


def _load_efo_label_lookup(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    lookup: dict[str, str] = {}
    for _, row in df.iterrows():
        trait_id = clean_text(row.get("Ontology Trait ID"))
        label = clean_text(row.get("Ontology Trait Label"))
        if trait_id and label:
            lookup[trait_id] = label
    return lookup


def _publication(row: pd.Series) -> dict[str, str]:
    return {
        "pgp_id": clean_text(row.get("PGS Publication (PGP) ID")),
        "pmid": clean_text(row.get("Publication (PMID")),
        "doi": clean_text(row.get("Publication (doi)")),
    }


def _pgs_record_from_row(row: pd.Series, performance_by_pgs: dict[str, dict[str, Any]]) -> CompactPgsRecord:
    pgs_id = clean_text(row.get("Polygenic Score (PGS) ID"))
    return CompactPgsRecord(
        pgs_id=pgs_id,
        pgs_name=compact_text(row.get("PGS Name"), 120),
        reported_trait=compact_text(row.get("Reported Trait"), 180),
        mapped_trait_labels=split_multi_value(row.get("Mapped Trait(s) (EFO label)")),
        mapped_trait_ids=split_multi_value(row.get("Mapped Trait(s) (EFO ID)")),
        method=compact_text(row.get("PGS Development Method"), 160),
        method_details=compact_text(row.get("PGS Development Details/Relevant Parameters"), 220),
        variant_count=_safe_int(row.get("Number of Variants")),
        ancestry_gwas=compact_text(row.get("Ancestry Distribution (%) - Source of Variant Associations (GWAS)"), 180),
        ancestry_training=compact_text(row.get("Ancestry Distribution (%) - Score Development/Training"), 180),
        ancestry_evaluation=compact_text(row.get("Ancestry Distribution (%) - PGS Evaluation"), 180),
        publication=_publication(row),
        release_date=clean_text(row.get("Release Date")),
        performance=performance_by_pgs.get(pgs_id, {}),
    )


def build_compact_catalog(
    *,
    scores_csv: Path = PGS_SCORES_CSV,
    efo_traits_csv: Path = PGS_EFO_TRAITS_CSV,
    performance_metrics_csv: Path = PGS_PERFORMANCE_METRICS_CSV,
    evaluation_sample_sets_csv: Path = PGS_EVALUATION_SAMPLE_SETS_CSV,
) -> dict[str, Any]:
    scores = pd.read_csv(scores_csv)
    efo_label_lookup = _load_efo_label_lookup(efo_traits_csv)
    performance_by_pgs = _load_performance_summaries(
        performance_metrics_csv=performance_metrics_csv,
        evaluation_sample_sets_csv=evaluation_sample_sets_csv,
    )

    pgs_records: list[CompactPgsRecord] = []
    bundles: dict[str, dict[str, Any]] = {}

    for _, row in scores.iterrows():
        pgs = _pgs_record_from_row(row, performance_by_pgs)
        if not pgs.pgs_id:
            continue
        pgs_records.append(pgs)

        reported_trait = pgs.reported_trait
        mapped_labels = list(pgs.mapped_trait_labels)
        mapped_ids = list(pgs.mapped_trait_ids)
        pair_count = max(len(mapped_labels), len(mapped_ids), 1)
        for idx in range(pair_count):
            mapped_id = mapped_ids[idx] if idx < len(mapped_ids) else ""
            mapped_label = mapped_labels[idx] if idx < len(mapped_labels) else ""
            canonical_label = (
                efo_label_lookup.get(mapped_id)
                or mapped_label
                or reported_trait
                or f"unmapped {pgs.pgs_id}"
            )
            bundle_key = mapped_id or f"LABEL::{canonical_label.lower()}"
            bundle = bundles.setdefault(
                bundle_key,
                {
                    "bundle_id": slugify(bundle_key.replace("::", "_")),
                    "canonical_label": canonical_label,
                    "bundle_type": infer_bundle_type(canonical_label),
                    "aliases": [],
                    "candidate_pgs_ids": [],
                    "source_efo_ids": [],
                    "source_mondo_ids": [],
                },
            )
            bundle["aliases"].extend([canonical_label, mapped_label, reported_trait])
            bundle["candidate_pgs_ids"].append(pgs.pgs_id)
            if mapped_id.startswith("EFO_"):
                bundle["source_efo_ids"].append(mapped_id)
            elif mapped_id.startswith("MONDO_"):
                bundle["source_mondo_ids"].append(mapped_id)

    bundle_records: list[CompactBundleRecord] = []
    for bundle in bundles.values():
        candidate_pgs_ids = sorted(set(bundle["candidate_pgs_ids"]))
        bundle_records.append(
            CompactBundleRecord(
                bundle_id=bundle["bundle_id"],
                canonical_label=bundle["canonical_label"],
                bundle_type=bundle["bundle_type"],
                aliases=unique_preserve_order([clean_text(v) for v in bundle["aliases"]]),
                candidate_pgs_ids=candidate_pgs_ids,
                n_models=len(candidate_pgs_ids),
                source_efo_ids=sorted(set(bundle["source_efo_ids"])),
                source_mondo_ids=sorted(set(bundle["source_mondo_ids"])),
            )
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "asset_type": "compact_catalog",
        "source_files": {
            "scores_csv": str(scores_csv),
            "efo_traits_csv": str(efo_traits_csv),
            "performance_metrics_csv": str(performance_metrics_csv),
            "evaluation_sample_sets_csv": str(evaluation_sample_sets_csv),
        },
        "pgs_records": [record.to_prompt_dict() for record in sorted(pgs_records, key=lambda item: item.pgs_id)],
        "bundles": [
            record.to_prompt_dict()
            for record in sorted(bundle_records, key=lambda item: item.bundle_id)
        ],
    }


def write_compact_catalog(catalog: dict[str, Any], outpath: Path = DEFAULT_COMPACT_CATALOG_JSON) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build leak-free compact PGS Catalog asset.")
    parser.add_argument("--scores-csv", type=Path, default=PGS_SCORES_CSV)
    parser.add_argument("--efo-traits-csv", type=Path, default=PGS_EFO_TRAITS_CSV)
    parser.add_argument("--out", type=Path, default=DEFAULT_COMPACT_CATALOG_JSON)
    args = parser.parse_args()

    catalog = build_compact_catalog(scores_csv=args.scores_csv, efo_traits_csv=args.efo_traits_csv)
    write_compact_catalog(catalog, args.out)
    print(
        f"Wrote {len(catalog['pgs_records'])} PGS records and "
        f"{len(catalog['bundles'])} bundles -> {args.out}"
    )


if __name__ == "__main__":
    main()
