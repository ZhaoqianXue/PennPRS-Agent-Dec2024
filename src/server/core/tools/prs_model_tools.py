# src/server/core/tools/prs_model_tools.py
"""
PRS Model Tools for Module 3.
Implements sop.md L356-462 tool specifications.
"""
import os
import re
import logging
import threading
from functools import lru_cache
from typing import List, Optional, Dict, Any, Iterable, Tuple, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.server.core.tool_schemas import (
    PublicationMetadata, PGSModelSummary, PGSSearchResult,
    ToolError
)

logger = logging.getLogger(__name__)

# Process-wide PGS Catalog metadata caches. The transfer pipeline hydrates the
# same bundle (e.g. a large generalist trait retained by many targets) across
# 80 targets in parallel workers — without a cache, each worker re-fetches the
# same PGS details and performance rows hundreds of times. A simple lock-guarded
# read-through cache collapses those to one fetch per distinct PGS ID for the
# lifetime of the process. None is cached as well so we don't hammer the catalog
# on PGS IDs that return 404.
_PGS_DETAILS_CACHE: Dict[str, Any] = {}
_PGS_PERFORMANCE_CACHE: Dict[str, Any] = {}
_PGS_DETAILS_LOCKS: Dict[str, threading.Lock] = {}
_PGS_PERFORMANCE_LOCKS: Dict[str, threading.Lock] = {}
_PGS_CACHE_LOCK = threading.Lock()
_PGS_CACHE_SENTINEL = object()


def _pgs_key_lock(lock_map: Dict[str, threading.Lock], pgs_id: str) -> threading.Lock:
    """Return a per-PGS lock so concurrent workers share one in-flight fetch."""
    with _PGS_CACHE_LOCK:
        lock = lock_map.get(pgs_id)
        if lock is None:
            lock = threading.Lock()
            lock_map[pgs_id] = lock
        return lock


def _cached_get_score_details(client, pgs_id: str) -> Any:
    with _PGS_CACHE_LOCK:
        cached = _PGS_DETAILS_CACHE.get(pgs_id, _PGS_CACHE_SENTINEL)
    if cached is not _PGS_CACHE_SENTINEL:
        return cached
    key_lock = _pgs_key_lock(_PGS_DETAILS_LOCKS, pgs_id)
    with key_lock:
        with _PGS_CACHE_LOCK:
            cached = _PGS_DETAILS_CACHE.get(pgs_id, _PGS_CACHE_SENTINEL)
        if cached is not _PGS_CACHE_SENTINEL:
            return cached
        data = client.get_score_details(pgs_id)
        with _PGS_CACHE_LOCK:
            _PGS_DETAILS_CACHE.setdefault(pgs_id, data)
        return data


def _cached_get_score_performance(client, pgs_id: str) -> Any:
    with _PGS_CACHE_LOCK:
        cached = _PGS_PERFORMANCE_CACHE.get(pgs_id, _PGS_CACHE_SENTINEL)
    if cached is not _PGS_CACHE_SENTINEL:
        return cached
    key_lock = _pgs_key_lock(_PGS_PERFORMANCE_LOCKS, pgs_id)
    with key_lock:
        with _PGS_CACHE_LOCK:
            cached = _PGS_PERFORMANCE_CACHE.get(pgs_id, _PGS_CACHE_SENTINEL)
        if cached is not _PGS_CACHE_SENTINEL:
            return cached
        data = client.get_score_performance(pgs_id)
        with _PGS_CACHE_LOCK:
            _PGS_PERFORMANCE_CACHE.setdefault(pgs_id, data)
        return data


def _load_dev_cache_from_disk() -> None:
    """Development-only optimization: if a pre-fetched PGS Catalog metadata
    pickle exists under `data/pgs_catalog_cache/`, pre-populate the in-memory
    caches at module import time. In production the file will be absent and
    the transfer pipeline falls back to on-demand API hydration. Build the
    cache by running
      ``experiments/contribution3/transfer/scripts/prefetch_pgs_catalog_cache.py``.
    """
    try:
        import pickle
        from pathlib import Path
        # repo_root = .../PennPRS_Agent
        repo_root = Path(__file__).resolve().parents[4]
        cache_file = repo_root / "data" / "pgs_catalog_cache" / "pgs_catalog_cache.pkl"
        if not cache_file.exists():
            return
        with cache_file.open("rb") as f:
            data = pickle.load(f)
        details = data.get("details", {})
        performance = data.get("performance", {})
        with _PGS_CACHE_LOCK:
            _PGS_DETAILS_CACHE.update(details)
            _PGS_PERFORMANCE_CACHE.update(performance)
        logger.info(
            "Loaded PGS Catalog dev cache: %d details + %d performance entries from %s",
            len(details), len(performance), cache_file,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to load PGS Catalog dev cache: %s", exc)


_load_dev_cache_from_disk()

DOMAIN_QUERY_EXPANSION: Dict[str, List[str]] = {
    "clinical": ["clinical", "guideline", "consensus", "threshold", "benchmark"],
    "auc": ["auc", "auroc", "roc", "c-index"],
    "r2": ["r2", "r²", "variance"],
    "heritability": ["heritability", "h2", "h²", "ceiling", "sanity check", "genetic architecture"],
    "ceiling": ["ceiling", "upper bound", "sanity check", "heritability"],
    "gates": ["gate", "must-pass", "must_pass", "eligibility"],
    "ranking": ["ranking", "prioritize", "priority", "rank"],
    "penalties": ["penalty", "penalties", "red flag", "risk"],
    "method": ["method", "ldpred2", "prs-cs", "lassosum", "c+t"],
    "ancestry": ["ancestry", "eur", "afr", "eas", "sas", "multi-ancestry"],
    "phenotype": ["phenotype", "trait", "endpoint", "proxy", "family history"],
    "endpoint": ["endpoint", "specificity", "incident", "prevalent", "time-to-event", "proxy"],
    "specificity": ["specificity", "exact disease", "subtype", "organ-specific"],
    "transfer": ["external", "transfer", "transportability", "deploy", "biobank"],
    "external": ["external", "transportability", "independent validation", "deployment"],
    "snpnet": ["snpnet", "time-to-event", "ukb", "biobank"],
    "ukb": ["ukb", "biobank", "time-to-event", "administrative"],
    "validation": ["validation", "validated", "external validation", "sample size"],
    "sample": ["sample", "sample size", "validation", "powered", "n="],
    "size": ["sample size", "validation", "cohort", "n="],
    "tie-break": ["tie-break", "tiebreak", "validation sample size", "close auc"],
    "incident": ["incident", "time-to-event", "horizon-specific"],
    "case-control": ["case-control", "clinical endpoint", "exact disease"],
    "subtype": ["subtype", "dominant subtype", "organ-specific"],
}

STRUCTURED_SECTION_KEYWORDS: Dict[str, List[str]] = {
    "structured selection rules": ["clinical", "threshold", "ranking", "penalties", "method", "selection"],
    "must-pass gates": ["gate", "phenotype", "ancestry", "proxy", "endpoint"],
    "ranking features": ["ranking", "auc", "r2", "sample", "validation", "method"],
    "heritability sanity check": ["heritability", "h2", "h²", "ceiling", "sanity", "pgs-only", "no covariates"],
    "penalties and red flags": ["penalties", "red", "flag", "proxy", "overlap", "bias"],
    "method priors": ["method", "ldpred2", "prs-cs", "lassosum", "c+t"],
    "endpoint integrity notes (disease-agnostic)": ["proxy", "endpoint", "family history", "disease"],
    "decision order": ["ranking", "selection", "endpoint", "transfer", "auc"],
    "endpoint specificity hierarchy": ["endpoint", "specificity", "incident", "prevalent", "proxy", "time-to-event"],
    "external transfer reliability heuristics": ["external", "transfer", "transportability", "biobank", "validation"],
    "large-biobank snpnet / time-to-event caution": ["snpnet", "time-to-event", "ukb", "biobank"],
    "validation sample-size tie-break": ["validation", "sample", "size", "tie-break", "tiebreak"],
    "disease-family cautions": ["cancer", "carcinoma", "thyroid", "cardiovascular", "vitiligo"],
}

TARGET_DISEASE_SECTION_TITLES = {
    "Abdominal Aortic Aneurysm",
    "Aortic Stenosis",
    "Cervical Carcinoma",
    "Hashimoto's Thyroiditis",
    "Hypothyroidism",
    "Late-Onset Alzheimer's Disease",
    "Obesity",
    "Open-Angle Glaucoma",
    "Prostate Cancer",
    "Thyroid Carcinoma",
    "Uterine Carcinoma",
    "Vitiligo",
}


def _dedupe_preserve_order(values: Iterable[Any]) -> List[str]:
    ordered: List[str] = []
    seen: Set[str] = set()
    for raw in values or []:
        value = str(raw or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def hydrate_pgs_model_summaries(
    client,  # PGSCatalogClient
    pgs_ids: Iterable[str],
    request_id: Optional[str] = None,
) -> List[PGSModelSummary]:
    """
    Hydrate agent-facing PGS model summaries for an explicit ordered list of IDs.

    This is the exact-ID counterpart to ``prs_model_pgscatalog_search`` and is useful
    when the caller already knows the candidate universe and must not rely on trait
    text retrieval recall.
    """
    # Import search_progress here to avoid circular imports
    from src.server.core.state import search_progress

    ordered_ids = _dedupe_preserve_order(pgs_ids)
    if request_id and request_id in search_progress:
        search_progress[request_id].update({
            "status": "running",
            "current_action": "Fetching metadata...",
            "current_step": "step-1",
            "models_total": len(ordered_ids),
            "models_fetched": 0,
            "models_successful": 0,
        })

    max_workers = int(os.getenv("PGS_FETCH_MAX_WORKERS", "20"))
    details_map: Dict[str, Dict[str, Any]] = {}
    performance_map: Dict[str, List[Dict[str, Any]]] = {}
    attempted_details_count = 0
    successful_details_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_pid: Dict[Any, Tuple[str, str]] = {}
        for pgs_id in ordered_ids:
            future_to_pid[executor.submit(_cached_get_score_details, client, pgs_id)] = (pgs_id, "details")
            future_to_pid[executor.submit(_cached_get_score_performance, client, pgs_id)] = (
                pgs_id,
                "performance",
            )

        for future in as_completed(future_to_pid):
            pgs_id, req_type = future_to_pid[future]
            try:
                data = future.result()
                if req_type == "details":
                    attempted_details_count += 1
                    if data:
                        details_map[pgs_id] = data
                        successful_details_count += 1
                    if request_id and request_id in search_progress:
                        search_progress[request_id].update({
                            "models_fetched": attempted_details_count,
                            "models_successful": successful_details_count,
                            "current_action": f"Fetching {pgs_id}...",
                            "current_step": "step-1",
                        })
                else:
                    performance_map[pgs_id] = data or []
            except Exception as e:
                logger.debug(f"Failed to fetch {req_type} for {pgs_id}: {e}")
                if req_type == "details":
                    attempted_details_count += 1
                    if request_id and request_id in search_progress:
                        search_progress[request_id].update({
                            "models_fetched": attempted_details_count,
                            "models_successful": successful_details_count,
                            "current_action": f"Fetching {pgs_id}...",
                            "current_step": "step-1",
                        })
                continue

    candidates: List[PGSModelSummary] = []
    for pgs_id in ordered_ids:
        details = details_map.get(pgs_id)
        performance = performance_map.get(pgs_id, [])

        if details:
            cohorts = _extract_cohorts(details)
            trait_reported = details.get("trait_reported", "Unknown")
            trait_efo = ", ".join([t.get("label", "") for t in details.get("trait_efo", [])])
            method_name = details.get("method_name", "Unknown")
            variants_number = details.get("variants_number", 0)
            ancestry_distribution = _format_ancestry(details.get("ancestry_distribution", {}))
            publication = _extract_publication_metadata(details.get("publication"))
            date_release = details.get("date_release", "Unknown")
            samples_training = _format_samples(details.get("samples_training", []))
        else:
            cohorts = []
            trait_reported = "Unknown"
            trait_efo = ""
            method_name = "Unknown"
            variants_number = 0
            ancestry_distribution = "Unknown"
            publication = PublicationMetadata(title="Unknown", journal="Unknown")
            date_release = "Unknown"
            samples_training = "N/A"

        performance_summary, selected_performance = _build_selected_performance_summary(performance)
        phenotyping_reported = "Unknown"
        covariates = "Unknown"
        validation_sample_size: Optional[str] = None
        if selected_performance:
            phenotyping_reported = selected_performance.get("phenotyping_reported") or "Unknown"
            covariates = selected_performance.get("covariates") or "Unknown"
            validation_sample_size = _format_validation_sample_size(
                _extract_validation_sample_count(selected_performance)
            )

        candidates.append(
            PGSModelSummary(
                id=pgs_id,
                trait_reported=trait_reported,
                trait_efo=trait_efo,
                method_name=method_name,
                variants_number=variants_number,
                ancestry_distribution=ancestry_distribution,
                publication=publication,
                date_release=date_release,
                samples_training=samples_training,
                performance_metrics=performance_summary,
                phenotyping_reported=phenotyping_reported,
                covariates=covariates,
                training_development_cohorts=cohorts,
                validation_sample_size=validation_sample_size,
            )
        )

    if request_id and request_id in search_progress:
        search_progress[request_id].update({
            "models_total": len(ordered_ids),
            "models_fetched": len(ordered_ids),
            "models_successful": len(local_summaries) + successful_details_count,
            "current_action": f"Completed fetching {len(ordered_ids)} models",
            "current_step": "step-1",
        })

    return candidates


def prs_model_pgscatalog_search(
    client,  # PGSCatalogClient
    trait_query: str,
    request_id: Optional[str] = None,
    evaluated_pgs_whitelist: Optional[Set[str]] = None,
) -> PGSSearchResult:
    """
    Search for trait-specific PRS models and retrieve [Agent + UI] metadata.

    Implements sop.md L359-392 specification.
    No AUC/R² filter: includes all models from retrieval (aligned with Contribution1 pgs_id_list).

    **Ranking and Top-N strategy DISABLED** (as of Contribution2 alignment):
    - Returns ALL filtered models in API raw order (no Z-score sorting).
    - No truncation; LLM context accommodates full candidate sets (typically 3-96 per trait).

    **Evaluated models filter** (optional, for Contribution2 evaluation):
    - When evaluated_pgs_whitelist is provided, only models whose PGS ID is in the set are kept.
    - Aligns Agent candidate pool with N Models (All of Us evaluated set) for fair benchmarking.

    Args:
        client: PGSCatalogClient instance
        trait_query: User's target trait (e.g., "Type 2 Diabetes")
        request_id: Optional request ID for progress tracking
        evaluated_pgs_whitelist: Optional set of PGS IDs to keep (only models in this set returned).
            Used for Contribution2 evaluation to restrict to All of Us evaluated models.

    Returns:
        PGSSearchResult with all filtered, ranked models
    """
    # Import search_progress here to avoid circular imports
    from src.server.core.state import search_progress
    
    # 1. Search for scores
    if request_id and request_id in search_progress:
        search_progress[request_id]["current_action"] = "Searching PGS Catalog..."
    
    search_results = client.search_scores(trait_query)
    total_found = len(search_results)
    
    models = []

    # 2. Fetch details/performance for the filtered explicit candidate IDs.
    pgs_ids = [res["id"] for res in search_results]
    if evaluated_pgs_whitelist:
        whitelist_set = set(evaluated_pgs_whitelist)
        pgs_ids = [pgs_id for pgs_id in pgs_ids if pgs_id in whitelist_set]

    # Ranking logic DISABLED: preserve API raw order from search_scores.
    models = hydrate_pgs_model_summaries(client, pgs_ids, request_id=request_id)
        
    return PGSSearchResult(
        query_trait=trait_query,
        total_found=total_found,
        after_filter=len(models),
        models=models
    )


def _format_ancestry(dist: Dict[str, Any]) -> str:
    """Format ancestry distribution for LLM context."""
    if not dist:
        return "Unknown"
    
    parts = []
    for stage in ["gwas", "dev", "eval"]:
        if stage in dist:
            stage_parts = []
            stage_obj = dist.get(stage)
            if isinstance(stage_obj, dict) and "dist" in stage_obj and isinstance(stage_obj.get("dist"), dict):
                stage_dist = stage_obj.get("dist") or {}
            elif isinstance(stage_obj, dict):
                stage_dist = stage_obj
            else:
                stage_dist = {}

            for anc, weight in stage_dist.items():
                try:
                    w = float(weight)
                except Exception:
                    continue
                # Some APIs return percentages (0-100) while others return fractions (0-1).
                pct = w if w > 1.0 else (w * 100.0)
                stage_parts.append(f"{anc} ({pct:.0f}%)")
            parts.append(f"{stage.upper()}: {', '.join(stage_parts)}")
            
    return " | ".join(parts) if parts else "Unknown"


def _format_samples(samples: List[Dict[str, Any]]) -> str:
    """Format training samples for LLM context."""
    if not samples:
        return "N/A"
    # Use (x or 0) to handle None (API may return null for sample_number)
    total_n = sum((s.get("sample_number") or 0) for s in samples)
    return f"n={total_n:,}"


def _extract_publication_metadata(publication: Any) -> PublicationMetadata:
    """Extract agent-facing publication metadata from the raw PGS Catalog object."""
    if isinstance(publication, dict):
        title = str(publication.get("title") or "Unknown")
        journal = str(publication.get("journal") or "Unknown")
        return PublicationMetadata(title=title, journal=journal)
    return PublicationMetadata(title="Unknown", journal="Unknown")

PRIMARY_AUC_NAMES = {"AUC", "AUROC", "ROC AUC", "AUCROC"}
C_INDEX_NAMES = {"C-INDEX", "C INDEX", "CINDEX"}
R2_NAMES = {"R²", "R2", "R^2"}


def _safe_metric_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _as_unit_interval(x: Any) -> Optional[float]:
    """
    Normalize common metric encodings:
    - Some sources encode AUC/R²/C-index as percentages (e.g., 28.5 meaning 28.5%).
    - Convert 0-100 values to 0-1 when applicable.
    """
    v = _safe_metric_float(x)
    if v is None:
        return None
    if v > 1.0 and v <= 100.0:
        v = v / 100.0
    if 0.0 <= v <= 1.0:
        return v
    return None


def _metric_name(entry: Dict[str, Any]) -> str:
    return str(entry.get("name_short") or entry.get("name_long") or "").strip()


def _metric_name_upper(entry: Dict[str, Any]) -> str:
    return _metric_name(entry).upper()


def _metric_name_lower(entry: Dict[str, Any]) -> str:
    return _metric_name(entry).lower()


def _is_delta_metric(entry: Dict[str, Any]) -> bool:
    name = _metric_name(entry)
    lower = name.lower()
    return ("incremental" in lower) or ("delta" in lower) or ("change" in lower) or ("Δ" in name)


def _is_auc_like_name(name_lower: str) -> bool:
    return ("auc" in name_lower) or ("auroc" in name_lower) or ("area under" in name_lower)


def _is_r2_like_name(name_lower: str) -> bool:
    return ("r2" in name_lower) or ("r²" in name_lower) or ("r^2" in name_lower) or ("variance" in name_lower)


def _is_pgs_only_auc_metric(entry: Dict[str, Any]) -> bool:
    lower = _metric_name_lower(entry)
    return "pgs" in lower and _is_auc_like_name(lower)


def _is_pgs_only_r2_metric(entry: Dict[str, Any]) -> bool:
    lower = _metric_name_lower(entry)
    if "pgs" in lower and _is_r2_like_name(lower):
        return True
    return "covariates regressed out" in lower and _is_r2_like_name(lower)


def _is_full_model_r2_metric(entry: Dict[str, Any]) -> bool:
    lower = _metric_name_lower(entry)
    upper = _metric_name_upper(entry)
    if _is_pgs_only_r2_metric(entry):
        return False
    return upper in R2_NAMES or _is_r2_like_name(lower)


def _metric_max(current: Optional[float], candidate: Optional[float]) -> Optional[float]:
    if candidate is None:
        return current
    if current is None:
        return candidate
    return max(current, candidate)


def _normalized_metric_entries(entries: Any) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        item = dict(entry)
        if "estimate" in item:
            item["estimate"] = _safe_metric_float(item.get("estimate"))
        if "ci_lower" in item:
            item["ci_lower"] = _safe_metric_float(item.get("ci_lower"))
        if "ci_upper" in item:
            item["ci_upper"] = _safe_metric_float(item.get("ci_upper"))
        normalized.append(item)
    return normalized


def _iter_metric_entries(pm: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
    for key, out_key in (
        ("effect_sizes", "effect_sizes"),
        ("class_acc", "classification_metrics"),
        ("othermetrics", "other_metrics"),
    ):
        for entry in _normalized_metric_entries(pm.get(key) or []):
            yield out_key, entry


def _extract_auc_r2_from_metrics_dict(metrics_dict: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    """Extract PRS-comparable AUC/R²-like metrics from a single performance_metrics dict."""
    summary = _extract_metric_summary_from_metrics_dict(metrics_dict)
    return summary.get("auc"), summary.get("r2")


def _extract_metric_summary_from_metrics_dict(metrics_dict: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """
    Separate PRS-comparable metrics from full-model metrics within one validation record.

    Top-level `auc` and `r2` are reserved for PRS-comparable metrics aligned to
    Contribution1-style interpretation. Full-model AUROC/R² are kept separately
    for sanity checking and inspection.
    """
    best_pgs_only_auc: Optional[float] = None
    best_pgs_only_r2: Optional[float] = None
    best_full_model_auc: Optional[float] = None
    best_full_model_r2: Optional[float] = None
    best_incremental_auc: Optional[float] = None
    best_c_index: Optional[float] = None

    for section, entry in _iter_metric_entries(metrics_dict):
        name_upper = _metric_name_upper(entry)
        name_lower = _metric_name_lower(entry)
        estimate = entry.get("estimate")
        if estimate is None:
            continue
        value = _as_unit_interval(estimate)

        if _is_pgs_only_auc_metric(entry):
            best_pgs_only_auc = _metric_max(best_pgs_only_auc, value)
            continue

        if _is_delta_metric(entry) and _is_auc_like_name(name_lower):
            best_incremental_auc = _metric_max(best_incremental_auc, value)
            continue

        if name_upper in C_INDEX_NAMES:
            best_c_index = _metric_max(best_c_index, value)
            continue

        if name_upper in PRIMARY_AUC_NAMES:
            best_full_model_auc = _metric_max(best_full_model_auc, value)
            continue

        if section == "other_metrics" and not _is_delta_metric(entry) and _is_auc_like_name(name_lower):
            best_full_model_auc = _metric_max(best_full_model_auc, value)
            continue

        if _is_pgs_only_r2_metric(entry):
            best_pgs_only_r2 = _metric_max(best_pgs_only_r2, value)
            continue

        if _is_full_model_r2_metric(entry):
            best_full_model_r2 = _metric_max(best_full_model_r2, value)

    if best_full_model_auc is None and best_c_index is not None:
        best_full_model_auc = best_c_index

    return {
        "auc": best_pgs_only_auc,
        "r2": best_pgs_only_r2,
        "pgs_only_auc": best_pgs_only_auc,
        "pgs_only_r2": best_pgs_only_r2,
        "full_model_auc": best_full_model_auc,
        "full_model_r2": best_full_model_r2,
        "incremental_auc": best_incremental_auc,
    }


def _extract_validation_ancestries(record: Dict[str, Any]) -> List[str]:
    ancestries: List[str] = []
    sampleset = record.get("sampleset") or {}
    if not isinstance(sampleset, dict):
        return ancestries
    for sample in sampleset.get("samples") or []:
        if not isinstance(sample, dict):
            continue
        ancestry = sample.get("ancestry_broad") or sample.get("ancestry_free")
        if ancestry:
            value = str(ancestry).strip()
            if value and value not in ancestries:
                ancestries.append(value)
    return ancestries


def _is_european_ancestry(label: str) -> bool:
    text = (label or "").strip().lower()
    return ("europe" in text) or bool(re.search(r"\beur\b", text))


def _extract_validation_sample_count(record: Dict[str, Any]) -> int:
    sampleset = record.get("sampleset") or {}
    if not isinstance(sampleset, dict):
        return 0
    total = 0
    for sample in sampleset.get("samples") or []:
        if not isinstance(sample, dict):
            continue
        total += int(sample.get("sample_number") or 0)
    return total


def _format_validation_sample_size(sample_count: int) -> Optional[str]:
    if sample_count <= 0:
        return None
    return f"n={sample_count:,}"


def _select_representative_performance_record(
    performance_records: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Select one representative validation record for agent-facing reasoning.

    Rule:
    1. Prefer records with European validation ancestry.
    2. Within EUR records, choose the highest-result record.
    3. If no EUR record exists, choose the highest-result record overall.

    "Highest-result" is determined by:
    - PRS-comparable AUC first
    - then PRS-comparable R²
    - then full-model AUC
    - then full-model R²
    - then validation sample size
    """
    ranked: List[Tuple[int, int, float, int, int, Dict[str, Any]]] = []
    for idx, record in enumerate(performance_records or []):
        if not isinstance(record, dict):
            continue
        metrics_dict = record.get("performance_metrics") or {}
        if not isinstance(metrics_dict, dict):
            metrics_dict = {}
        metric_summary = _extract_metric_summary_from_metrics_dict(metrics_dict)
        comparable_auc = metric_summary.get("auc")
        comparable_r2 = metric_summary.get("r2")
        full_model_auc = metric_summary.get("full_model_auc")
        full_model_r2 = metric_summary.get("full_model_r2")
        if comparable_auc is not None:
            metric_tier = 4
            metric_value = comparable_auc
        elif comparable_r2 is not None:
            metric_tier = 3
            metric_value = comparable_r2
        elif full_model_auc is not None:
            metric_tier = 2
            metric_value = full_model_auc
        elif full_model_r2 is not None:
            metric_tier = 1
            metric_value = full_model_r2
        else:
            metric_tier = 0
            metric_value = -1.0
        ancestries = _extract_validation_ancestries(record)
        eur_flag = 1 if any(_is_european_ancestry(a) for a in ancestries) else 0
        sample_n = _extract_validation_sample_count(record)
        ranked.append((eur_flag, metric_tier, metric_value, sample_n, -idx, record))

    if not ranked:
        return None

    eur_ranked = [item for item in ranked if item[0] == 1]
    pool = eur_ranked if eur_ranked else ranked
    return max(pool, key=lambda item: (item[1], item[2], item[3], item[4]))[-1]


def _build_selected_performance_summary(
    performance_records: List[Dict[str, Any]]
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    selected = _select_representative_performance_record(performance_records)
    if not selected:
        return {
            "auc": None,
            "r2": None,
            "selected_performance_id": None,
            "selected_validation_ancestry": None,
            "record_count": len(performance_records or []),
            "classification_metrics": [],
            "other_metrics": [],
            "effect_sizes": [],
        }, None

    metrics_dict = selected.get("performance_metrics") or {}
    if not isinstance(metrics_dict, dict):
        metrics_dict = {}
    metric_summary = _extract_metric_summary_from_metrics_dict(metrics_dict)
    ancestries = _extract_validation_ancestries(selected)
    return {
        "auc": metric_summary.get("auc"),
        "r2": metric_summary.get("r2"),
        "pgs_only_auc": metric_summary.get("pgs_only_auc"),
        "pgs_only_r2": metric_summary.get("pgs_only_r2"),
        "full_model_auc": metric_summary.get("full_model_auc"),
        "full_model_r2": metric_summary.get("full_model_r2"),
        "incremental_auc": metric_summary.get("incremental_auc"),
        "selected_performance_id": selected.get("id"),
        "selected_validation_ancestry": ", ".join(ancestries) if ancestries else None,
        "record_count": len(performance_records or []),
        "classification_metrics": _normalized_metric_entries(metrics_dict.get("class_acc") or []),
        "other_metrics": _normalized_metric_entries(metrics_dict.get("othermetrics") or []),
        "effect_sizes": _normalized_metric_entries(metrics_dict.get("effect_sizes") or []),
    }, selected


def _extract_cohorts(details: Dict[str, Any]) -> List[str]:
    """
    Extract cohort short names from training/development-related sample blocks.

    Best-effort:
    - Use `samples_training` and `samples_variants` cohorts from score details.
    - Return a deduplicated, sorted list of cohort short names (fallback to full name if short missing).
    """
    def _cohort_names(sample_block: Dict[str, Any]) -> Iterable[str]:
        for c in sample_block.get("cohorts", []) or []:
            name = c.get("name_short") or c.get("name_full") or c.get("name_others")
            if name:
                yield str(name)

    cohorts: set[str] = set()
    for s in (details.get("samples_training", []) or []):
        cohorts.update(_cohort_names(s))
    for s in (details.get("samples_variants", []) or []):
        cohorts.update(_cohort_names(s))

    return sorted(cohorts)


# --- Domain Knowledge Tool ---

# Default path to knowledge base
KNOWLEDGE_BASE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "knowledge", "prs_model_domain_knowledge.md"
)


@lru_cache(maxsize=1)
def _get_heritability_aggregator():
    from src.server.modules.heritability.aggregator import HeritabilityAggregator
    return HeritabilityAggregator()


def _format_optional_float(value: Optional[float], digits: int = 4) -> str:
    if value is None:
        return "N/A"
    return f"{float(value):.{digits}f}"


def _format_optional_int(value: Optional[int]) -> str:
    if value is None:
        return "N/A"
    try:
        parsed = int(value)
    except Exception:
        return "N/A"
    return f"{parsed:,}" if parsed > 0 else "N/A"


def _collapse_query_to_trait(query: str) -> Optional[str]:
    text = re.sub(r"\s+", " ", (query or "").strip())
    if not text:
        return None
    text = re.sub(r";.*$", "", text)
    return text or None


def _heritability_confidence_rank(est: Any) -> Tuple[int, float, int]:
    source_priority = {
        "gwas_atlas": 3,
        "ukbb_ldsc": 2,
        "pan_ukb": 1,
    }
    n_samples = int(getattr(est, "n_samples", 0) or 0)
    se = getattr(est, "h2_obs_se", None)
    se_inv = 0.0 if not se else 1.0 / (float(se) + 0.001)
    source = getattr(getattr(est, "source", None), "value", getattr(est, "source", ""))
    return (n_samples, se_inv, source_priority.get(str(source), 0))


def _build_trait_specific_heritability_section(query: str) -> Optional[Tuple[str, str]]:
    target_trait = _extract_target_trait_phrase(query) or _collapse_query_to_trait(query)
    if not target_trait:
        return None

    try:
        aggregator = _get_heritability_aggregator()
        eur_best = aggregator.get_best_estimate(target_trait, ancestry="EUR")
        all_results = aggregator.search(target_trait, min_score=70, limit=8)
    except Exception as exc:
        logger.warning("Failed to load trait-specific heritability for '%s': %s", target_trait, exc)
        return (
            "Trait-Specific Heritability",
            (
                f"Target trait: {target_trait}\n"
                "Local heritability lookup failed.\n"
                "- use heritability only as a ceiling/sanity field for PGS-only metrics\n"
                "- do not back-calculate or rank by full-model AUROC"
            ),
        )

    if eur_best is None and all_results:
        eur_best = sorted(all_results, key=_heritability_confidence_rank, reverse=True)[0]

    if eur_best is None:
        return (
            "Trait-Specific Heritability",
            (
                f"Target trait: {target_trait}\n"
                "No matching local heritability estimate was found above the retrieval threshold.\n"
                "- use the generic ceiling rule only\n"
                "- do not infer PRS quality from full-model AUROC alone"
            ),
        )

    top_results = sorted(all_results, key=_heritability_confidence_rank, reverse=True)[:3]
    best_source = getattr(getattr(eur_best, "source", None), "value", getattr(eur_best, "source", "N/A"))
    lines = [
        f"Target trait: {target_trait}",
        (
            "Best matched local heritability estimate: "
            f"h2_obs={_format_optional_float(getattr(eur_best, 'h2_obs', None))}; "
            f"h2_liability={_format_optional_float(getattr(eur_best, 'h2_liability', None))}; "
            f"SE={_format_optional_float(getattr(eur_best, 'h2_obs_se', None))}; "
            f"z={_format_optional_float(getattr(eur_best, 'h2_z', None), digits=2)}; "
            f"population={getattr(eur_best, 'population', 'N/A')}; "
            f"n={_format_optional_int(getattr(eur_best, 'n_samples', None))}; "
            f"source={best_source}."
        ),
        "Sanity-check usage:",
        "- compare PGS-only R2 or covariates-regressed-out R2 against h2; they should remain below the trait heritability ceiling",
        "- if full-model AUROC is very high but incremental AUROC and PGS-only R2 are small relative to h2, treat the AUROC as mostly covariate-driven rather than PRS-driven",
        "- if PGS-only AUROC is absent, do not substitute the full-model AUROC as a comparable PRS metric",
        "- use heritability as a ceiling/sanity field, not as an exact formula to reconstruct AUROC",
    ]
    if top_results:
        lines.append("Top local matches:")
        for est in top_results:
            source = getattr(getattr(est, "source", None), "value", getattr(est, "source", "N/A"))
            lines.append(
                "- "
                f"{getattr(est, 'trait_name', 'Unknown')} | "
                f"h2_obs={_format_optional_float(getattr(est, 'h2_obs', None))} | "
                f"population={getattr(est, 'population', 'N/A')} | "
                f"n={_format_optional_int(getattr(est, 'n_samples', None))} | "
                f"source={source}"
            )
    return ("Trait-Specific Heritability", "\n".join(lines))


def prs_model_domain_knowledge(
    query: str,
    knowledge_file: Optional[str] = None,
    max_snippets: int = 8
):
    """
    Search domain knowledge for PRS model selection guidance.
    
    Implements sop.md L394-428 specification.
    Currently uses local file retrieval; will upgrade to web search.
    Returns the full knowledge document for agent injection plus
    relevance-ranked section snippets for inspection/debugging.
    
    Args:
        query: Search query (e.g., "LDpred2 best for", "ancestry considerations")
        knowledge_file: Optional path to knowledge base file
        max_snippets: Maximum snippets to return (default 5)
        
    Returns:
        DomainKnowledgeResult with relevant snippets
    """
    from src.server.core.tool_schemas import DomainKnowledgeResult, KnowledgeSnippet
    
    kb_path = knowledge_file or KNOWLEDGE_BASE_PATH
    
    # Load knowledge base
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return DomainKnowledgeResult(
            query=query,
            full_document="",
            snippets=[],
            source_type="local"
        )
    
    # Parse into sections
    sections = _parse_markdown_sections(content)
    dynamic_sections: List[Tuple[str, str]] = []
    heritability_section = _build_trait_specific_heritability_section(query)
    if heritability_section:
        dynamic_sections.append(heritability_section)
    sections = dynamic_sections + sections
    
    # Score and rank sections by relevance
    query_terms = _expand_domain_query_terms(query)
    target_trait_phrase = _extract_target_trait_phrase(query)
    scored_sections = []
    
    for section_title, section_content in sections:
        score = _calculate_relevance(
            query_terms,
            section_title,
            section_content,
            target_trait_phrase=target_trait_phrase,
        )
        if score > 0:
            scored_sections.append((section_title, section_content, score))
    
    # Sort by score descending
    scored_sections.sort(key=lambda x: x[2], reverse=True)
    if target_trait_phrase:
        normalized_target = _normalize_phrase(target_trait_phrase)
        target_sections = [
            item for item in scored_sections
            if normalized_target
            and (
                normalized_target in _normalize_phrase(item[0])
                or _normalize_phrase(item[0]) in normalized_target
            )
        ]
        other_sections = [
            item for item in scored_sections
            if item not in target_sections
            and (
                item[0] not in TARGET_DISEASE_SECTION_TITLES
                or (
                    normalized_target
                    and (
                        normalized_target in _normalize_phrase(item[0])
                        or _normalize_phrase(item[0]) in normalized_target
                    )
                )
            )
        ]
        scored_sections = target_sections + other_sections
    
    # Build snippets
    snippets = []
    for title, content_text, score in scored_sections[:max_snippets]:
        # Truncate content to reasonable length
        truncated = content_text[:500] + "..." if len(content_text) > 500 else content_text
        
        snippet = KnowledgeSnippet(
            source="local_heritability_data" if title == "Trait-Specific Heritability" else "prs_model_domain_knowledge.md",
            section=title,
            content=truncated,
            relevance_score=min(score / 10.0, 1.0)  # Normalize to 0-1
        )
        snippets.append(snippet)

    full_document = content.strip()
    if dynamic_sections:
        dynamic_doc = "\n\n".join(
            f"## {title}\n\n{section_content.strip()}"
            for title, section_content in dynamic_sections
        ).strip()
        full_document = f"{dynamic_doc}\n\n{full_document}" if full_document else dynamic_doc

    return DomainKnowledgeResult(
        query=query,
        full_document=full_document,
        snippets=snippets,
        source_type="local"
    )


def _parse_markdown_sections(content: str) -> List[tuple]:
    """
    Parse markdown content into sections.
    
    Returns:
        List of (section_title, section_content) tuples
    """
    import re
    
    sections = []
    current_title = "Introduction"
    current_content = []
    
    for line in content.split('\n'):
        # Check for headers (##, ###)
        header_match = re.match(r'^(#{2,3})\s+(.+)$', line)
        if header_match:
            # Save previous section
            if current_content:
                sections.append((current_title, '\n'.join(current_content).strip()))
            current_title = header_match.group(2)
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections.append((current_title, '\n'.join(current_content).strip()))
    
    return sections


def _extract_target_trait_phrase(query: str) -> Optional[str]:
    match = re.search(r"target_trait\s*:\s*([^;]+)", query or "", flags=re.IGNORECASE)
    if not match:
        return None
    phrase = re.sub(r"\s+", " ", match.group(1)).strip().lower()
    return phrase or None


def _normalize_phrase(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()
    return re.sub(r"\s+", " ", normalized)


def _calculate_relevance(
    query_terms: List[str],
    title: str,
    content: str,
    target_trait_phrase: Optional[str] = None,
) -> float:
    """
    Calculate relevance score between query and section.
    
    Simple keyword matching - can be upgraded to embeddings later.
    """
    combined = (title + " " + content).lower()
    title_l = title.lower()
    query_set = set(query_terms)

    score = 0.0
    for term in query_terms:
        if term in combined:
            # Higher weight for title matches
            if term in title_l:
                score += 3.0
            else:
                score += 1.0
            
            # Bonus for multiple occurrences
            count = combined.count(term)
            if count > 1:
                score += min(count * 0.2, 2.0)

    for section_key, trigger_terms in STRUCTURED_SECTION_KEYWORDS.items():
        if section_key in title_l and any(t in query_set for t in trigger_terms):
            score += 4.0
            break

    if target_trait_phrase:
        if target_trait_phrase in title_l:
            score += 8.0
        elif target_trait_phrase in combined:
            score += 4.0

    if "endpoint" in title_l and any(t in query_set for t in {"endpoint", "specificity", "phenotype", "proxy"}):
        score += 2.0
    if any(t in title_l for t in {"transfer", "transport", "biobank", "snpnet"}):
        if any(t in query_set for t in {"external", "transfer", "transportability", "snpnet", "ukb", "biobank"}):
            score += 2.0
    if any(t in title_l for t in {"validation", "sample-size", "tie-break", "tiebreak"}):
        if any(t in query_set for t in {"validation", "sample", "size", "tie-break", "tiebreak"}):
            score += 2.0

    return score


def _expand_domain_query_terms(query: str) -> List[str]:
    raw_terms = [t.strip().lower() for t in (query or "").split() if t.strip()]
    expanded: List[str] = []
    seen = set()

    for term in raw_terms:
        if term not in seen:
            expanded.append(term)
            seen.add(term)
        for alias in DOMAIN_QUERY_EXPANSION.get(term, []):
            if alias not in seen:
                expanded.append(alias)
                seen.add(alias)

    return expanded
