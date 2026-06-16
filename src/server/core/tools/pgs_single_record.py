"""Build the unrestricted PGS candidate schema directly from the full
PGS Catalog REST dump.

Every PGS produces the same fixed candidate identifier plus seven evidence
sections as the original single-record schema, but multi-record source sections
now retain every source record instead of selecting, aggregating, or taking the
first row. The source of
truth is
`data/pgs_all_metadata/pgs_full_rest_dump.jsonl` (one full nested REST record
per PGS, 5,332 = PGS Catalog full), the same data that produced the reference
example.

Performance metrics preserve the PGS Catalog REST buckets rather than exposing
interpretive fields such as PRS-only AUROC or full-model AUROC. The serializer
maps REST `effect_sizes`, `class_acc`, and `othermetrics` to compact
`effect_sizes`, `classification_metrics`, and `other_metrics` entries.

This is the canonical candidate serialization shown to the LLM in the
contribution2 within-trait recommendation task, so the candidate's field
vocabulary matches the prs-model-recommendation skill exactly.

Excluded fields (per spec): percent_male, ancestry free/country in the primary
record (only broad kept, key `ancestry`), sample_set_id.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.server.core.tools.prs_model_tools import _normalized_metric_entries

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_REST_DUMP_PATH = PROJECT_ROOT / "data" / "pgs_all_metadata" / "pgs_full_rest_dump.jsonl"

# ---------------------------------------------------------------------------
# Dump loading (cached, thread-safe)
# ---------------------------------------------------------------------------

_DUMP_LOCK = threading.Lock()
_DUMP_INDEX: Optional[Dict[str, dict]] = None
_DUMP_PATH_LOADED: Optional[Path] = None


def load_rest_dump(path: Optional[Path] = None) -> Dict[str, dict]:
    """Load the REST dump into a {pgs_id: record} index (cached process-wide)."""
    global _DUMP_INDEX, _DUMP_PATH_LOADED
    resolved = Path(path) if path else DEFAULT_REST_DUMP_PATH
    with _DUMP_LOCK:
        if _DUMP_INDEX is not None and _DUMP_PATH_LOADED == resolved:
            return _DUMP_INDEX
        index: Dict[str, dict] = {}
        with open(resolved, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                pid = rec.get("pgs_id") or (rec.get("score") or {}).get("id")
                if pid:
                    index[pid] = rec
        _DUMP_INDEX = index
        _DUMP_PATH_LOADED = resolved
        return index


# ---------------------------------------------------------------------------
# Simple field mappings (the non-complex parts of the fixed-section assembly)
# ---------------------------------------------------------------------------

def _sample_numbers(sample: dict) -> dict:
    return {
        "individuals": sample.get("sample_number"),
        "cases": sample.get("sample_cases"),
        "controls": sample.get("sample_controls"),
    }


def _compact_metric_entries(entries: Any) -> List[dict]:
    compact: List[dict] = []
    for entry in _normalized_metric_entries(entries):
        name = entry.get("name_short") or entry.get("name_long")
        item = {}
        if name is not None:
            item["metric_name"] = name
        for key in ("estimate", "ci_lower", "ci_upper"):
            if key in entry:
                item[key] = entry.get(key)
        compact.append(item)
    return compact


def _sample_cohorts(sample: dict) -> List[str]:
    out: List[str] = []
    for cohort in sample.get("cohorts") or []:
        name = cohort.get("name_short") or cohort.get("name_full")
        if name and name not in out:
            out.append(name)
    return out


def _sample_block(sample: dict, include_cohorts: bool = True) -> dict:
    block = {
        "sample_numbers": _sample_numbers(sample),
        "ancestry": sample.get("ancestry_broad"),
    }
    if include_cohorts:
        block["cohorts"] = _sample_cohorts(sample)
    return block


def _performance_metric_record(perf_record: dict) -> dict:
    metrics_dict = perf_record.get("performance_metrics") or {}
    if not isinstance(metrics_dict, dict):
        metrics_dict = {}
    samples = [
        _sample_block(sample)
        for sample in (perf_record.get("sampleset") or {}).get("samples") or []
        if isinstance(sample, dict)
    ]
    return {
        "performance_id": perf_record.get("id"),
        "phenotyping_reported": perf_record.get("phenotyping_reported"),
        "covariates": perf_record.get("covariates"),
        "effect_sizes": _compact_metric_entries(metrics_dict.get("effect_sizes") or []),
        "classification_metrics": _compact_metric_entries(metrics_dict.get("class_acc") or []),
        "other_metrics": _compact_metric_entries(metrics_dict.get("othermetrics") or []),
        "evaluation_samples": samples,
    }


# ---------------------------------------------------------------------------
# Public builder
# ---------------------------------------------------------------------------

def build_single_record(pgs_id: str, dump: Optional[Dict[str, dict]] = None) -> Optional[dict]:
    """Build the unrestricted id-plus-seven-evidence-section schema for one PGS."""
    index = dump if dump is not None else load_rest_dump()
    rec = index.get(pgs_id)
    if not rec:
        return None
    score = rec.get("score") or {}
    perf_records = rec.get("performance") or []

    performance_metrics = [
        _performance_metric_record(perf_record)
        for perf_record in perf_records
        if isinstance(perf_record, dict)
    ]
    gwas = [
        _sample_block(sample)
        for sample in score.get("samples_variants") or []
        if isinstance(sample, dict)
    ]
    score_development_training = [
        _sample_block(sample, include_cohorts=False)
        for sample in score.get("samples_training") or []
        if isinstance(sample, dict)
    ]

    trait_efo = [
        {"label": t.get("label"), "id": t.get("id")}
        for t in (score.get("trait_efo") or [])
        if isinstance(t, dict)
    ]
    publication = score.get("publication") or {}

    return {
        "id": pgs_id,
        "predicted_trait": {
            "trait_reported": score.get("trait_reported"),
            "trait_efo": trait_efo,
        },
        "development_method": {"method_name": score.get("method_name")},
        "variants": {"variants_number": score.get("variants_number")},
        "pgs_source": {
            "publication_title": publication.get("title"),
            "publication_journal": publication.get("journal"),
            "date_release": score.get("date_release"),
        },
        "source_of_variant_associations_gwas": gwas,
        "score_development_training": score_development_training,
        "performance_metrics": performance_metrics,
    }
