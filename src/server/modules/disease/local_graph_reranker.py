from typing import Any, Callable, Dict, List, Optional, Sequence


DEFAULT_LOCAL_GRAPH_WEIGHTS: Dict[str, float] = {
    "graph_transfer": 0.45,
    "graph_rg": 0.15,
    "graph_power": 0.10,
    "pgs_hits": 0.20,
    "semantic_similarity": 0.10,
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _normalize_by_max(value: float, max_value: float) -> float:
    if max_value <= 0:
        return 0.0
    normalized = value / max_value
    if normalized < 0:
        return 0.0
    if normalized > 1:
        return 1.0
    return normalized


def _merge_weights(custom_weights: Optional[Dict[str, float]]) -> Dict[str, float]:
    merged = dict(DEFAULT_LOCAL_GRAPH_WEIGHTS)
    if custom_weights:
        for key, val in custom_weights.items():
            merged[key] = _safe_float(val, merged.get(key, 0.0))
    return merged


def rerank_neighbors_with_local_graph(
    target_trait: str,
    neighbors: Sequence[Any],
    pgs_hit_counts: Dict[str, int],
    similarity_fn: Optional[Callable[[str, str], float]] = None,
    weights: Optional[Dict[str, float]] = None,
    min_pgs_hits: int = 1,
) -> List[Dict[str, Any]]:
    """
    Prototype local graph reranker (rule + linear score).

    Score components:
    - graph_transfer: normalized transfer_score
    - graph_rg: normalized abs(rg_meta)
    - graph_power: normalized n_correlations
    - pgs_hits: normalized PGS precheck hit count
    - semantic_similarity: trait semantic proximity
    """
    if not neighbors:
        return []

    scorer = similarity_fn or (lambda _a, _b: 0.0)
    merged_weights = _merge_weights(weights)
    candidates: List[Dict[str, Any]] = []

    transfers = [_safe_float(getattr(n, "transfer_score", 0.0)) for n in neighbors]
    abs_rgs = [abs(_safe_float(getattr(n, "rg_meta", 0.0))) for n in neighbors]
    powers = [max(0, _safe_int(getattr(n, "n_correlations", 0))) for n in neighbors]
    hit_vals = [
        max(0, _safe_int(pgs_hit_counts.get(getattr(n, "trait_id", "") or "", 0)))
        for n in neighbors
    ]

    max_transfer = max(transfers) if transfers else 0.0
    max_abs_rg = max(abs_rgs) if abs_rgs else 0.0
    max_power = max(powers) if powers else 0.0
    max_hits = max(hit_vals) if hit_vals else 0

    for n in neighbors:
        trait_id = getattr(n, "trait_id", "") or ""
        transfer_score = _safe_float(getattr(n, "transfer_score", 0.0))
        abs_rg = abs(_safe_float(getattr(n, "rg_meta", 0.0)))
        n_correlations = max(0, _safe_int(getattr(n, "n_correlations", 0)))
        pgs_hit_count = max(0, _safe_int(pgs_hit_counts.get(trait_id, 0)))
        semantic_similarity = _safe_float(scorer(target_trait, trait_id), 0.0)

        transfer_norm = _normalize_by_max(transfer_score, max_transfer)
        rg_norm = _normalize_by_max(abs_rg, max_abs_rg)
        power_norm = _normalize_by_max(float(n_correlations), float(max_power))
        hit_norm = _normalize_by_max(float(pgs_hit_count), float(max_hits))
        semantic_norm = semantic_similarity
        if semantic_norm < 0:
            semantic_norm = 0.0
        if semantic_norm > 1:
            semantic_norm = 1.0

        local_graph_score = (
            merged_weights["graph_transfer"] * transfer_norm
            + merged_weights["graph_rg"] * rg_norm
            + merged_weights["graph_power"] * power_norm
            + merged_weights["pgs_hits"] * hit_norm
            + merged_weights["semantic_similarity"] * semantic_norm
        )

        rule_failures: List[str] = []
        if pgs_hit_count < min_pgs_hits:
            rule_failures.append("insufficient_pgs_hits")
        if transfer_score <= 0:
            rule_failures.append("non_positive_transfer_score")

        candidates.append({
            "trait_id": trait_id,
            "domain": getattr(n, "domain", "Unknown"),
            "transfer_score": transfer_score,
            "rg_meta": _safe_float(getattr(n, "rg_meta", 0.0)),
            "n_correlations": n_correlations,
            "pgs_hit_count": pgs_hit_count,
            "semantic_similarity": semantic_norm,
            "transfer_norm": transfer_norm,
            "rg_norm": rg_norm,
            "power_norm": power_norm,
            "pgs_hit_norm": hit_norm,
            "local_graph_score": local_graph_score,
            "passes_rules": len(rule_failures) == 0,
            "rule_failures": rule_failures,
        })

    candidates.sort(
        key=lambda c: (
            c["passes_rules"],
            c["local_graph_score"],
            c["transfer_score"],
            c["pgs_hit_count"],
        ),
        reverse=True,
    )
    for idx, candidate in enumerate(candidates, start=1):
        candidate["local_graph_rank"] = idx
    return candidates


def select_neighbors_from_local_graph(
    ranked_candidates: Sequence[Dict[str, Any]],
    top_n: int = 3,
) -> List[str]:
    if not ranked_candidates or top_n <= 0:
        return []

    rule_passing = [c for c in ranked_candidates if c.get("passes_rules")]
    selected = rule_passing[:top_n] if rule_passing else list(ranked_candidates)[:top_n]
    return [str(c.get("trait_id") or "") for c in selected if c.get("trait_id")]
