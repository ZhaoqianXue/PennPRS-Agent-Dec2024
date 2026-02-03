# src/server/core/tools/prs_model_tools.py
"""
PRS Model Tools for Module 3.
Implements sop.md L356-462 tool specifications.
"""
import os
import time
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Iterable, Tuple
from statistics import median, quantiles
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.server.core.tool_schemas import (
    PGSModelSummary, PGSSearchResult,
    PerformanceLandscape, MetricDistribution,
    ToolError
)
from src.server.core.agent_artifacts import get_artifacts_dir, stable_json_dumps

logger = logging.getLogger(__name__)


def prs_model_pgscatalog_search(
    client,  # PGSCatalogClient
    trait_query: str,
    limit: int = 25
) -> PGSSearchResult:
    """
    Search for trait-specific PRS models and retrieve [Agent + UI] metadata.
    
    Implements sop.md L359-392 specification.
    Hard-coded Filter: Remove models where AUC and R2 are both null.
    Token Budget: ~500 tokens per model; max 10 models.
    
    Args:
        client: PGSCatalogClient instance
        trait_query: User's target trait (e.g., "Type 2 Diabetes")
        limit: Max models to return (default 25)
        
    Returns:
        PGSSearchResult with filtered models
    """
    # 1. Search for scores
    search_results = client.search_scores(trait_query)
    total_found = len(search_results)

    # Safety cap: avoid hydrating an unbounded number of PGS IDs (429 risk).
    # This cap is independent of the final `limit` returned to the caller.
    max_candidates = int(os.getenv("PGS_SEARCH_MAX_CANDIDATES", "60"))
    if max_candidates >= 0:
        search_results = search_results[:max_candidates]
    
    models = []
    
    # 2. Fetch details/performance for ALL candidate IDs (up to client-side cap) CONCURRENTLY,
    #    then rank and slice. This makes "topN" deterministic and meaningful.
    #    Optimized for speed: use concurrent fetching like pgs_search_service.py
    candidates: List[PGSModelSummary] = []
    pgs_ids = [res["id"] for res in search_results]
    
    # Fetch details and performance concurrently (like pgs_search_service.py)
    max_workers = int(os.getenv("PGS_FETCH_MAX_WORKERS", "4"))
    details_map: Dict[str, Dict[str, Any]] = {}
    performance_map: Dict[str, List[Dict[str, Any]]] = {}
    
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
                    if data:  # Only store non-empty details
                        details_map[pgs_id] = data
                else:  # performance
                    performance_map[pgs_id] = data or []
            except Exception as e:
                logger.debug(f"Failed to fetch {req_type} for {pgs_id}: {e}")
                continue
    
    # Process fetched data
    for pgs_id in pgs_ids:
        details = details_map.get(pgs_id)
        if not details:
            continue
        
        performance = performance_map.get(pgs_id, [])
        auc, r2 = _extract_auc_r2_from_performance_records(performance)

        # Hard-coded Filter: Remove models where both are null
        if auc is None and r2 is None:
            continue

        cohorts = _extract_cohorts(details)

        phenotyping_reported = "Unknown"
        covariates = "Unknown"
        sampleset = "Unknown"
        if performance:
            first = performance[0] if isinstance(performance[0], dict) else {}
            phenotyping_reported = first.get("phenotyping_reported") or "Unknown"
            covariates = first.get("covariates") or "Unknown"
            ss = first.get("sampleset") or {}
            if isinstance(ss, dict):
                sampleset = ss.get("name") or ss.get("id") or "Unknown"

        summary = PGSModelSummary(
            id=pgs_id,
            trait_reported=details.get("trait_reported", "Unknown"),
            trait_efo=", ".join([t.get("label", "") for t in details.get("trait_efo", [])]),
            method_name=details.get("method_name", "Unknown"),
            variants_number=details.get("variants_number", 0),
            ancestry_distribution=_format_ancestry(details.get("ancestry_distribution", {})),
            publication=details.get("publication", {}).get("title", "Unknown"),
            date_release=details.get("date_release", "Unknown"),
            samples_training=_format_samples(details.get("samples_training", [])),
            performance_metrics={"auc": auc, "r2": r2},
            phenotyping_reported=phenotyping_reported,
            covariates=covariates,
            sampleset=sampleset,
            training_development_cohorts=cohorts
        )
        candidates.append(summary)

    # Ranking rule (deterministic) using Z-score normalization:
    # All four metrics (AUC, R², training sample size, variants_number) have equal weight.
    # Each metric is standardized using Z-score: z = (x - mean) / std
    # Final score = z_auc + z_r2 + z_samples + z_variants (higher is better)
    # Tie-break by PGS id asc for stability
    
    if not candidates:
        models = []
    else:
        # Collect all values for Z-score calculation
        auc_values = []
        r2_values = []
        sample_values = []
        variant_values = []
        
        for m in candidates:
            auc = m.performance_metrics.get("auc")
            r2 = m.performance_metrics.get("r2")
            n = _parse_sample_size(m.samples_training)
            
            if auc is not None:
                auc_values.append(float(auc))
            if r2 is not None:
                r2_values.append(float(r2))
            if n is not None:
                sample_values.append(float(n))
            variant_values.append(float(m.variants_number))
        
        # Calculate means and standard deviations
        def _mean_std(values: List[float]) -> Tuple[float, float]:
            if not values:
                return 0.0, 1.0
            mean_val = sum(values) / len(values)
            if len(values) == 1:
                return mean_val, 1.0
            variance = sum((x - mean_val) ** 2 for x in values) / len(values)
            std_val = variance ** 0.5
            return mean_val, std_val if std_val > 0 else 1.0
        
        auc_mean, auc_std = _mean_std(auc_values)
        r2_mean, r2_std = _mean_std(r2_values)
        sample_mean, sample_std = _mean_std(sample_values)
        variant_mean, variant_std = _mean_std(variant_values)
        
        # Calculate Z-score for each candidate and compute composite score
        def _rank_key(m: PGSModelSummary) -> Tuple[float, str]:
            auc = m.performance_metrics.get("auc")
            r2 = m.performance_metrics.get("r2")
            n = _parse_sample_size(m.samples_training)
            
            # Z-score normalization
            # If value is None, assign it the minimum z-score (penalize missing values)
            # This ensures missing values rank lower than any actual value
            if auc is not None:
                z_auc = (float(auc) - auc_mean) / auc_std if auc_std > 0 else 0.0
            else:
                # Use minimum z-score: if all values exist, use -3 (3 std devs below mean)
                # If no values exist, use 0
                z_auc = -3.0 if auc_values else 0.0
            
            if r2 is not None:
                z_r2 = (float(r2) - r2_mean) / r2_std if r2_std > 0 else 0.0
            else:
                z_r2 = -3.0 if r2_values else 0.0
            
            if n is not None:
                z_samples = (float(n) - sample_mean) / sample_std if sample_std > 0 else 0.0
            else:
                z_samples = -3.0 if sample_values else 0.0
            
            z_variants = (float(m.variants_number) - variant_mean) / variant_std if variant_std > 0 else 0.0
            
            # Composite score (higher is better)
            composite_score = z_auc + z_r2 + z_samples + z_variants
            
            return (composite_score, m.id)
        
        candidates.sort(key=_rank_key, reverse=True)
        models = candidates[:limit]
        
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
    
    total_n = sum(s.get("sample_number", 0) for s in samples)
    return f"n={total_n:,}"


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
        train_n = sum(int(s.get("sample_number") or 0) for s in train_samples)
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
    max_snippets: int = 5
):
    """
    Search domain knowledge for PRS model selection guidance.
    
    Implements sop.md L394-428 specification.
    Currently uses local file retrieval; will upgrade to web search.
    Token Budget: ~300 tokens.
    
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
            snippets=[],
            source_type="local"
        )
    
    # Parse into sections
    sections = _parse_markdown_sections(content)
    
    # Score and rank sections by relevance
    query_terms = query.lower().split()
    scored_sections = []
    
    for section_title, section_content in sections:
        score = _calculate_relevance(query_terms, section_title, section_content)
        if score > 0:
            scored_sections.append((section_title, section_content, score))
    
    # Sort by score descending
    scored_sections.sort(key=lambda x: x[2], reverse=True)
    
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


def _calculate_relevance(query_terms: List[str], title: str, content: str) -> float:
    """
    Calculate relevance score between query and section.
    
    Simple keyword matching - can be upgraded to embeddings later.
    """
    combined = (title + " " + content).lower()
    
    score = 0.0
    for term in query_terms:
        if term in combined:
            # Higher weight for title matches
            if term in title.lower():
                score += 3.0
            else:
                score += 1.0
            
            # Bonus for multiple occurrences
            count = combined.count(term)
            if count > 1:
                score += min(count * 0.2, 2.0)
    
    return score

