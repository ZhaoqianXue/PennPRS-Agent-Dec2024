"""
PGS Catalog -> UI ModelData formatting helpers.

This module exists so the Co-Scientist frontend can reuse the PRS-Disease
preview card UI (ModelCard/ModelGrid/SearchSummaryView) without duplicating
formatting logic in the browser.

All comments/strings are in English by project convention.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.server.core.pgs_catalog_client import PGSCatalogClient
from src.server.modules.disease.pgs_search_service import (
    _fetch_pgs_details_and_performance_concurrently,
)


def _safe_float(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def _extract_auc_r2_from_performance_records(
    performance_records: List[Dict[str, Any]],
) -> Tuple[Optional[float], Optional[float]]:
    """
    Best-effort extraction of AUC and R² from PGS performance records.

    Note: This intentionally mirrors the logic used elsewhere in the codebase,
    but stays self-contained so UI endpoints don't depend on internal tool code.
    """

    def _is_delta_metric(name: str) -> bool:
        n = (name or "").lower()
        return ("delta" in n) or ("change" in n) or ("Δ" in name)

    best_auc: Optional[float] = None
    best_r2: Optional[float] = None

    for rec in performance_records or []:
        if not isinstance(rec, dict):
            continue
        perf = rec.get("performance_metrics") or {}
        if not isinstance(perf, dict):
            continue

        # AUC candidates (class_acc + othermetrics)
        auc_candidates: List[float] = []
        for acc in perf.get("class_acc", []) or []:
            if not isinstance(acc, dict):
                continue
            name = f"{acc.get('name_short', '')}{acc.get('name_long', '')}"
            if _is_delta_metric(name):
                continue
            if "auc" in name.lower() or "auroc" in name.lower() or "c-index" in name.lower():
                v = _safe_float(acc.get("estimate"))
                if v is not None:
                    auc_candidates.append(v)
        for om in perf.get("othermetrics", []) or []:
            if not isinstance(om, dict):
                continue
            name = f"{om.get('name_short', '')}{om.get('name_long', '')}"
            if _is_delta_metric(name):
                continue
            if "auc" in name.lower() or "auroc" in name.lower() or "c-index" in name.lower() or "area under" in name.lower():
                v = _safe_float(om.get("estimate"))
                if v is not None:
                    auc_candidates.append(v)

        # R² candidates (othermetrics)
        r2_candidates: List[float] = []
        for om in perf.get("othermetrics", []) or []:
            if not isinstance(om, dict):
                continue
            name = f"{om.get('name_short', '')}{om.get('name_long', '')}".lower()
            if "r2" in name or "r^2" in name or "variance" in name:
                v = _safe_float(om.get("estimate"))
                if v is not None:
                    r2_candidates.append(v)

        auc_val = max(auc_candidates) if auc_candidates else None
        r2_val = max(r2_candidates) if r2_candidates else None

        if auc_val is not None:
            best_auc = auc_val if best_auc is None else max(best_auc, auc_val)
        if r2_val is not None:
            best_r2 = r2_val if best_r2 is None else max(best_r2, r2_val)

    return best_auc, best_r2


def _extract_dev_cohorts(details: Dict[str, Any]) -> str:
    cohorts: List[str] = []
    for s in details.get("samples_training", []) or []:
        if not isinstance(s, dict):
            continue
        for c in s.get("cohorts", []) or []:
            if isinstance(c, dict) and c.get("name_short"):
                cohorts.append(str(c.get("name_short")))
    # De-dup but keep stable order.
    seen = set()
    ordered = []
    for c in cohorts:
        if c not in seen:
            seen.add(c)
            ordered.append(c)
    return ", ".join(ordered)


def _extract_ancestry(details: Dict[str, Any]) -> str:
    # Prefer training samples ancestry_broad (more human-readable).
    ancestries: List[str] = []
    for s in details.get("samples_training", []) or []:
        if not isinstance(s, dict):
            continue
        a = s.get("ancestry_broad")
        if a:
            ancestries.append(str(a))
    seen = set()
    ordered = []
    for a in ancestries:
        if a not in seen:
            seen.add(a)
            ordered.append(a)
    if ordered:
        return ", ".join(ordered)

    # Fallback to ancestry_distribution keys (best-effort).
    dist = details.get("ancestry_distribution") or {}
    if isinstance(dist, dict):
        for stage in ("gwas", "dev", "eval"):
            stage_dist = (dist.get(stage) or {}).get("dist")
            if isinstance(stage_dist, dict) and stage_dist:
                return ", ".join([str(k) for k in stage_dist.keys()])
    return "N/A"


def _extract_sample_size(details: Dict[str, Any]) -> Optional[int]:
    total = 0
    found = False
    for s in details.get("samples_training", []) or []:
        if not isinstance(s, dict):
            continue
        n = s.get("sample_number")
        try:
            if n is not None:
                total += int(n)
                found = True
        except Exception:
            continue
    return total if found else None


def format_pgs_score_for_ui(
    *,
    pgs_id: str,
    details: Dict[str, Any],
    performance: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Convert raw PGS score details/performance to the frontend ModelData shape.
    """
    auc, r2 = _extract_auc_r2_from_performance_records(performance)
    sample_size = _extract_sample_size(details)
    dev_cohorts = _extract_dev_cohorts(details)
    ancestry = _extract_ancestry(details)

    publication = details.get("publication") or {}
    pub_title = publication.get("title") if isinstance(publication, dict) else None
    pub_pmid = publication.get("PMID") if isinstance(publication, dict) else None
    pub_doi = publication.get("doi") if isinstance(publication, dict) else None

    # Prefer ftp_scoring_file when present (direct file path).
    download_url = details.get("ftp_scoring_file") or None

    return {
        "id": pgs_id,
        "name": details.get("name") or pgs_id,
        "trait": details.get("trait_reported") or "Unknown",
        "ancestry": ancestry,
        "method": details.get("method_name") or "Unknown",
        "metrics": {
            "AUC": auc,
            "R2": r2,
        },
        "source": "PGS Catalog",
        "download_url": download_url,
        "num_variants": details.get("variants_number") or 0,
        "sample_size": sample_size,
        "dev_cohorts": dev_cohorts,
        "publication": {
            "date": details.get("date_release") or "Unknown",
            "citation": pub_title or (f"PMID: {pub_pmid}" if pub_pmid else "Unknown"),
            "id": str(pub_pmid or ""),
            "doi": str(pub_doi or ""),
        } if (pub_title or pub_pmid or pub_doi) else None,
    }


def get_single_pgs_model_card(pgs_id: str) -> Dict[str, Any]:
    """
    Fetch and format a single PGS score as a UI model card.
    """
    client = PGSCatalogClient()
    details = client.get_score_details(pgs_id) or {}
    performance = client.get_score_performance(pgs_id) or []
    return format_pgs_score_for_ui(pgs_id=pgs_id, details=details, performance=performance)


def search_pgs_model_cards(trait: str, limit: int = 25) -> List[Dict[str, Any]]:
    """
    Search PGS Catalog by trait and return formatted UI model cards.
    """
    client = PGSCatalogClient()
    results = client.search_scores(trait) or []
    pgs_ids = [r.get("id") for r in results if r.get("id")]
    pgs_ids = pgs_ids[: max(0, int(limit))]

    details_map, performance_map = _fetch_pgs_details_and_performance_concurrently(
        pgs_client=client,
        pgs_ids=pgs_ids,
        request_id=None,
        max_workers=20,
        progress_update_interval=5,
    )

    cards: List[Dict[str, Any]] = []
    for pid in pgs_ids:
        details = details_map.get(pid) or {}
        perf = performance_map.get(pid) or []
        if not details:
            continue
        cards.append(format_pgs_score_for_ui(pgs_id=pid, details=details, performance=perf))

    # Sort by best AUC desc (fallback to 0).
    def _auc_key(c: Dict[str, Any]) -> float:
        try:
            return float((c.get("metrics") or {}).get("AUC") or 0.0)
        except Exception:
            return 0.0

    cards.sort(key=_auc_key, reverse=True)
    return cards

