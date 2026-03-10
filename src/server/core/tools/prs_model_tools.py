# src/server/core/tools/prs_model_tools.py
"""
PRS Model Tools for Module 3.
Implements sop.md L356-462 tool specifications.
"""
import os
import time
import json
import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Iterable, Tuple, Set
from statistics import median, quantiles
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.server.core.tool_schemas import (
    PublicationMetadata, PGSModelSummary, PGSSearchResult,
    PerformanceLandscape, MetricDistribution,
    ToolError
)
from src.server.core.agent_artifacts import get_artifacts_dir, stable_json_dumps

logger = logging.getLogger(__name__)

DOMAIN_QUERY_EXPANSION: Dict[str, List[str]] = {
    "clinical": ["clinical", "guideline", "consensus", "threshold", "benchmark"],
    "auc": ["auc", "auroc", "roc", "c-index"],
    "r2": ["r2", "r²", "variance"],
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
    
    # 2. Fetch details/performance for ALL candidate IDs (up to client-side cap) CONCURRENTLY,
    #    then rank and slice. This makes "topN" deterministic and meaningful.
    #    Optimized for speed: use concurrent fetching like pgs_search_service.py
    candidates: List[PGSModelSummary] = []
    pgs_ids = [res["id"] for res in search_results]
    
    # Update progress: model hydration progress (separate from step progress).
    # IMPORTANT: Do not overload `total/fetched` (used for step progress) with model counts.
    if request_id and request_id in search_progress:
        search_progress[request_id].update({
            "status": "running",
            "current_action": "Fetching metadata...",
            "current_step": "step-1",
            # Model-level progress for step-1 UI.
            "models_total": len(pgs_ids),
            # `models_fetched` counts attempted hydrations (monotonic to total).
            "models_fetched": 0,
            # `models_successful` counts non-empty detail payloads (best-effort).
            "models_successful": 0,
        })
    
    # Fetch details and performance concurrently (like pgs_search_service.py)
    # Further increased default workers for faster fetching (was 10, now 20)
    max_workers = int(os.getenv("PGS_FETCH_MAX_WORKERS", "20"))
    details_map: Dict[str, Dict[str, Any]] = {}
    performance_map: Dict[str, List[Dict[str, Any]]] = {}
    attempted_details_count = 0
    successful_details_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_pid: Dict[Any, Tuple[str, str]] = {}
        for pgs_id in pgs_ids:
            future_to_pid[executor.submit(client.get_score_details, pgs_id)] = (pgs_id, "details")
            future_to_pid[executor.submit(client.get_score_performance, pgs_id)] = (pgs_id, "performance")
        
        for future in as_completed(future_to_pid):
            pgs_id, req_type = future_to_pid[future]
            try:
                data = future.result()
                if req_type == "details":
                    # Count attempted detail hydrations (monotonic progress).
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
                else:  # performance
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
    
    # Process fetched data - include ALL models; never skip due to missing details.
    # (Details are assumed fetchable; if empty, use minimal/fallback metadata.)
    for pgs_id in pgs_ids:
        details = details_map.get(pgs_id)
        performance = performance_map.get(pgs_id, [])

        # Extract fields from details when available; otherwise use fallbacks.
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

        auc, r2 = _extract_auc_r2_from_performance_records(performance)

        phenotyping_reported = "Unknown"
        covariates = "Unknown"
        validation_sample_size: Optional[str] = None
        if performance:
            first = performance[0] if isinstance(performance[0], dict) else {}
            phenotyping_reported = first.get("phenotyping_reported") or "Unknown"
            covariates = first.get("covariates") or "Unknown"
            validation_sample_size = _extract_validation_sample_size(performance)

        summary = PGSModelSummary(
            id=pgs_id,
            trait_reported=trait_reported,
            trait_efo=trait_efo,
            method_name=method_name,
            variants_number=variants_number,
            ancestry_distribution=ancestry_distribution,
            publication=publication,
            date_release=date_release,
            samples_training=samples_training,
            performance_metrics={"auc": auc, "r2": r2},
            phenotyping_reported=phenotyping_reported,
            covariates=covariates,
            training_development_cohorts=cohorts,
            validation_sample_size=validation_sample_size,
        )
        candidates.append(summary)

    # Ranking logic DISABLED: return models in API raw order (pgs_ids from search_scores).
    # No Z-score sorting; preserves PGS Catalog / trait-search response order.
    models = candidates

    # Optional: restrict to evaluated models only (Contribution2 alignment with N Models).
    if evaluated_pgs_whitelist:
        whitelist_set = set(evaluated_pgs_whitelist)
        models = [m for m in models if m.id in whitelist_set]

    # Finalize model hydration progress (attempted == total).
    if request_id and request_id in search_progress:
        search_progress[request_id].update({
            "models_total": len(pgs_ids),
            "models_fetched": len(pgs_ids),
            "models_successful": successful_details_count,
            "current_action": f"Completed fetching {len(pgs_ids)} models",
            "current_step": "step-1",
        })
        
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


def _extract_validation_sample_size(performance_records: List[Dict[str, Any]]) -> Optional[str]:
    """
    Extract validation cohort sample size from performance records.
    Returns the largest sampleset sample count across all performance entries (n=...).
    """
    if not performance_records:
        return None
    best_n = 0
    for p in performance_records:
        if not isinstance(p, dict):
            continue
        ss = p.get("sampleset") or {}
        if not isinstance(ss, dict):
            continue
        samples = ss.get("samples") or []
        total = sum((s.get("sample_number") or 0) for s in samples if isinstance(s, dict))
        if total > best_n:
            best_n = total
    if best_n <= 0:
        return None
    return f"n={best_n:,}"


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


def _extract_auc_r2_from_performance_records(performance_records: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract (best) AUC and R2 from a list of performance/search records.

    A score can have multiple performance entries; we take the maximum AUC and maximum R²
    across entries to avoid missing strong validations.
    """
    best_auc: Optional[float] = None
    best_r2: Optional[float] = None

    # Some endpoints return "performance records" shaped like:
    # - /performance/search: [{..., "performance_metrics": {"effect_sizes": [...], "class_acc": [...], ...}}, ...]
    # - /performance/all:    [{..., "performance_metrics": {"effect_sizes": [...], ...}}, ...]
    # While other call sites may pass the inner dict directly: {"effect_sizes": [...], ...}
    #
    # Normalize both shapes by treating `pm` as either p["performance_metrics"] (dict) or `p` itself.
    best_c_index: Optional[float] = None

    def _as_unit_interval(x: float) -> Optional[float]:
        """
        Normalize common metric encodings:
        - Some sources encode AUC/R²/C-index as percentages (e.g., 28.5 meaning 28.5%).
        - Convert 0-100 values to 0-1 when applicable.
        """
        if x is None:
            return None
        try:
            v = float(x)
        except Exception:
            return None
        if v > 1.0 and v <= 100.0:
            v = v / 100.0
        if 0.0 <= v <= 1.0:
            return v
        return None

    def _iter_metric_entries(pm: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        for key in ("effect_sizes", "class_acc", "othermetrics"):
            for entry in (pm.get(key) or []):
                if isinstance(entry, dict):
                    yield entry

    for p in performance_records or []:
        if not isinstance(p, dict):
            continue
        pm = p.get("performance_metrics")
        if isinstance(pm, dict):
            metrics_dict = pm
        else:
            metrics_dict = p

        for m in _iter_metric_entries(metrics_dict):
            name = str(m.get("name_short", "")).strip().upper()
            estimate = m.get("estimate")
            if estimate is None:
                continue
            try:
                val = float(estimate)
            except Exception:
                continue

            # AUC-like metrics (accept common aliases used by PGS Catalog).
            if name in {"AUC", "AUROC", "ROC AUC", "AUCROC"}:
                v = _as_unit_interval(val)
                if v is not None:
                    best_auc = v if best_auc is None else max(best_auc, v)
                continue

            # Concordance statistic (often used in cancer risk models); keep as AUC fallback.
            if name in {"C-INDEX", "C INDEX", "CINDEX"}:
                v = _as_unit_interval(val)
                if v is not None:
                    best_c_index = v if best_c_index is None else max(best_c_index, v)
                continue

            # R²-like metrics.
            if name in {"R²", "R2", "R^2"}:
                v = _as_unit_interval(val)
                if v is not None:
                    best_r2 = v if best_r2 is None else max(best_r2, v)

    # If AUC is not available but C-index exists, treat C-index as the best available AUC-like score.
    # This preserves ranking behavior and avoids dropping cancer scores that report concordance.
    if best_auc is None and best_c_index is not None:
        best_auc = best_c_index

    return best_auc, best_r2


def _parse_sample_size(samples_training: str) -> Optional[int]:
    """Parse 'n=12,345' style strings into integers."""
    if not samples_training:
        return None
    text = str(samples_training).strip()
    if text.upper() == "N/A":
        return None
    if not text.lower().startswith("n="):
        return None
    try:
        return int(text[2:].replace(",", "").strip())
    except Exception:
        return None


def _count_ancestry_codes(ancestry_distribution: str) -> Dict[str, int]:
    """
    Best-effort parse ancestry codes from formatted ancestry strings.

    Example inputs:
    - "GWAS: EUR (100%) | DEV: AFR (50%), EUR (50%)"
    Returns counts by code.
    """
    if not ancestry_distribution:
        return {}
    codes = ["EUR", "AFR", "EAS", "SAS", "AMR", "MAE", "GME", "ASN"]
    upper = ancestry_distribution.upper()
    counts: Dict[str, int] = {}
    for code in codes:
        # Count occurrences of standalone codes (very lightweight heuristic).
        # This keeps the logic deterministic and token-efficient.
        n = upper.count(code)
        if n:
            counts[code] = counts.get(code, 0) + n
    return counts


def prs_model_performance_landscape(
    client,  # PGSCatalogClient
    candidate_models: List[PGSModelSummary],
    max_scores: Optional[int] = None,
    max_performance_records: Optional[int] = None
) -> PerformanceLandscape:
    """
    Calculate GLOBAL performance landscape across the entire PGS Catalog.
    
    This is a global reference frame used to compare the candidate top-N models
    against the broader ecosystem, enabling meaningful "market baseline" reasoning.

    Implements sop.md L430-462 specification (updated: global reference).
    Token Budget: ~200 tokens.
    
    Args:
        client: PGSCatalogClient instance (used for `/rest/score/all` and `/rest/performance/all`)
        candidate_models: Candidate models from prs_model_pgscatalog_search (unused for distribution
            computation, but kept for tool-call ergonomics in the agent workflow)
        max_scores: Optional cap for score/all iteration (safety/testing)
        max_performance_records: Optional cap for performance/all iteration (safety/testing)
        
    Returns:
        PerformanceLandscape with global distributions (7 required categories)
    """
    # Default safety caps: computing a true "global" landscape can be very expensive
    # and can trigger API limits. Set env vars to 0 to disable the caps.
    if max_scores is None:
        default_max_scores = int(os.getenv("PGS_LANDSCAPE_MAX_SCORES", "2000"))
        max_scores = None if default_max_scores <= 0 else default_max_scores
    if max_performance_records is None:
        default_max_perf = int(os.getenv("PGS_LANDSCAPE_MAX_PERFORMANCE_RECORDS", "5000"))
        max_performance_records = None if default_max_perf <= 0 else default_max_perf

    # Optional file cache for real PGS Catalog client usage only.
    # Tests typically use a fake client (no BASE_URL attribute), so caching stays off.
    cache_ttl_s = int(os.getenv("PGS_LANDSCAPE_CACHE_TTL_S", "86400"))
    enable_cache = bool(os.getenv("PGS_LANDSCAPE_ENABLE_CACHE", "1") == "1")
    is_real_client = bool(getattr(client, "BASE_URL", "").startswith("https://www.pgscatalog.org/"))
    cache_path: Optional[Path] = None
    if enable_cache and cache_ttl_s > 0 and is_real_client:
        cache_path = get_artifacts_dir() / "pgs_performance_landscape_cache.json"
        try:
            if cache_path.exists():
                raw = json.loads(cache_path.read_text(encoding="utf-8"))
                ts = float(raw.get("created_at_epoch_s") or 0.0)
                age = time.time() - ts
                if age >= 0 and age <= cache_ttl_s:
                    payload = raw.get("landscape")
                    if isinstance(payload, dict):
                        return PerformanceLandscape(**payload)
        except Exception:
            # Cache is best-effort only.
            pass

    # Build performance index: PGS id -> best (auc, r2) across ALL performance records
    perf_best: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
    for rec in client.iter_all_performances(batch_size=100, max_records=max_performance_records):
        pgs_id = rec.get("associated_pgs_id")
        if not pgs_id:
            continue
        pm = (rec.get("performance_metrics") or {})
        # Normalize to a "performance/search-like" record list so we can reuse parsing
        auc, r2 = _extract_auc_r2_from_performance_records([pm])
        prev = perf_best.get(pgs_id, (None, None))
        best_auc = auc if prev[0] is None else (max(prev[0], auc) if auc is not None else prev[0])
        best_r2 = r2 if prev[1] is None else (max(prev[1], r2) if r2 is not None else prev[1])
        perf_best[pgs_id] = (best_auc, best_r2)

    auc_vals: List[float] = []
    r2_vals: List[float] = []
    sample_size_vals: List[float] = []
    variants_vals: List[float] = []

    auc_missing = 0
    r2_missing = 0
    sample_size_missing = 0

    ancestry_counts: Dict[str, int] = {}
    cohort_counts: Dict[str, int] = {}
    method_counts: Dict[str, int] = {}

    total_scores = 0
    for score in client.iter_all_scores(batch_size=100, max_scores=max_scores):
        total_scores += 1

        pgs_id = score.get("id")
        if not pgs_id:
            continue

        # PRS method
        method = (score.get("method_name") or "Unknown").strip() or "Unknown"
        method_counts[method] = method_counts.get(method, 0) + 1

        # Variants
        try:
            variants_vals.append(float(score.get("variants_number") or 0))
        except Exception:
            variants_vals.append(0.0)

        # Sample size (training)
        train_samples = score.get("samples_training", []) or []
        train_n = sum(int((s.get("sample_number") or 0)) for s in train_samples)
        if train_n > 0:
            sample_size_vals.append(float(train_n))
        else:
            sample_size_missing += 1

        # Ancestry: parse structured ancestry_distribution when available
        ancestry_dist = score.get("ancestry_distribution") or {}
        # Count major ancestry category in GWAS dist (best-effort)
        try:
            gwas = ancestry_dist.get("gwas", {}) or {}
            dist = gwas.get("dist", {}) or {}
            if dist:
                major = max(dist.items(), key=lambda x: x[1])[0]
                ancestry_counts[str(major).upper()] = ancestry_counts.get(str(major).upper(), 0) + 1
        except Exception:
            pass

        # Cohorts: from samples_training + samples_variants
        cohorts = _extract_cohorts(score)
        for c in cohorts:
            cohort_counts[c] = cohort_counts.get(c, 0) + 1

        # AUC / R2 (best per score)
        best_auc, best_r2 = perf_best.get(pgs_id, (None, None))
        if best_auc is not None:
            auc_vals.append(float(best_auc))
        else:
            auc_missing += 1
        if best_r2 is not None:
            r2_vals.append(float(best_r2))
        else:
            r2_missing += 1

    zero = MetricDistribution(min=0, max=0, median=0, p25=0, p75=0, missing_count=0)
    if total_scores == 0:
        return PerformanceLandscape(
            total_models=0,
            ancestry={},
            sample_size=zero,
            auc=zero,
            r2=zero,
            variants=zero,
            training_development_cohorts={},
            prs_methods={}
        )

    landscape = PerformanceLandscape(
        total_models=total_scores,
        ancestry=dict(sorted(ancestry_counts.items(), key=lambda x: x[1], reverse=True)),
        sample_size=_calculate_distribution(sample_size_vals, sample_size_missing),
        auc=_calculate_distribution(auc_vals, auc_missing),
        r2=_calculate_distribution(r2_vals, r2_missing),
        variants=_calculate_distribution(variants_vals, 0),
        training_development_cohorts=dict(sorted(cohort_counts.items(), key=lambda x: x[1], reverse=True)),
        prs_methods=dict(sorted(method_counts.items(), key=lambda x: x[1], reverse=True))
    )

    # Persist cache (best-effort) for real client usage.
    if cache_path:
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            blob = {
                "created_at_epoch_s": time.time(),
                "caps": {
                    "max_scores": max_scores,
                    "max_performance_records": max_performance_records,
                },
                "landscape": landscape.model_dump(),
            }
            cache_path.write_text(stable_json_dumps(blob), encoding="utf-8")
        except Exception:
            pass

    return landscape
    
    auc_vals: List[float] = []
    r2_vals: List[float] = []
    sample_size_vals: List[float] = []
    variants_vals: List[float] = []

    auc_missing = 0
    r2_missing = 0
    sample_size_missing = 0

    ancestry_counts: Dict[str, int] = {}
    cohort_counts: Dict[str, int] = {}
    method_counts: Dict[str, int] = {}

    for m in models:
        # AUC / R2
        auc = m.performance_metrics.get("auc")
        r2 = m.performance_metrics.get("r2")
        if auc is not None:
            auc_vals.append(float(auc))
        else:
            auc_missing += 1
        if r2 is not None:
            r2_vals.append(float(r2))
        else:
            r2_missing += 1

        # Sample size (training)
        n = _parse_sample_size(m.samples_training)
        if n is not None:
            sample_size_vals.append(float(n))
        else:
            sample_size_missing += 1

        # Variants
        variants_vals.append(float(m.variants_number))

        # Ancestry (best-effort parse)
        for code, count in _count_ancestry_codes(m.ancestry_distribution).items():
            ancestry_counts[code] = ancestry_counts.get(code, 0) + int(count)

        # Cohorts
        for c in (m.training_development_cohorts or []):
            cohort_counts[c] = cohort_counts.get(c, 0) + 1

        # PRS methods
        method = (m.method_name or "Unknown").strip() or "Unknown"
        method_counts[method] = method_counts.get(method, 0) + 1

    return PerformanceLandscape(
        total_models=len(models),
        ancestry=ancestry_counts,
        sample_size=_calculate_distribution(sample_size_vals, sample_size_missing),
        auc=_calculate_distribution(auc_vals, auc_missing),
        r2=_calculate_distribution(r2_vals, r2_missing),
        variants=_calculate_distribution(variants_vals, 0),
        training_development_cohorts=dict(sorted(cohort_counts.items(), key=lambda x: x[1], reverse=True)),
        prs_methods=dict(sorted(method_counts.items(), key=lambda x: x[1], reverse=True))
    )


def _calculate_distribution(values: List[float], missing_count: int) -> MetricDistribution:
    """Calculate statistical distribution for a list of values."""
    if not values:
        return MetricDistribution(
            min=0, max=0, median=0, p25=0, p75=0, missing_count=missing_count
        )
    
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    
    if n >= 4:
        # Use quantiles for 4+ values
        q = quantiles(sorted_vals, n=4)
        p25, med, p75 = q[0], q[1], q[2]
    elif n >= 2:
        med = median(sorted_vals)
        p25 = sorted_vals[0]
        p75 = sorted_vals[-1]
    else:
        # Single value
        med = sorted_vals[0]
        p25 = p75 = med
    
    return MetricDistribution(
        min=min(sorted_vals),
        max=max(sorted_vals),
        median=med,
        p25=p25,
        p75=p75,
        missing_count=missing_count
    )


# --- Domain Knowledge Tool ---

# Default path to knowledge base
import os
KNOWLEDGE_BASE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "knowledge", "prs_model_domain_knowledge.md"
)


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
            source="prs_model_domain_knowledge.md",
            section=title,
            content=truncated,
            relevance_score=min(score / 10.0, 1.0)  # Normalize to 0-1
        )
        snippets.append(snippet)
    
    return DomainKnowledgeResult(
        query=query,
        full_document=content.strip(),
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
