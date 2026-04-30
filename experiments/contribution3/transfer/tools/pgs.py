"""PGS model introspection — lazy per-PGS, all performance records preserved.

The deleted `_select_representative_performance_record` used to pick one
performance row before the LLM could see alternatives. This tool returns
the FULL performance record list; the LLM chooses what matters.

Called lazily (one PGS at a time) to avoid prompt bloat when bundles
have 20+ models. The harness populates `EvidenceRegistry.model_records`
as each call completes.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from src.server.core.pgs_catalog_client import PGSCatalogClient
from src.server.core.tools.prs_model_tools import (
    _cached_get_score_details,
    _cached_get_score_performance,
)

logger = logging.getLogger(__name__)

_CLIENT: Optional[PGSCatalogClient] = None


def _get_client() -> PGSCatalogClient:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = PGSCatalogClient()
    return _CLIENT


def _normalize_performance_record(rec: dict[str, Any]) -> dict[str, Any]:
    """Minimal flattening — preserve all metric entries unpruned."""
    return {
        "id": rec.get("id"),
        "ppm_id": rec.get("ppm_id"),
        "sampleset_id": (rec.get("sampleset") or {}).get("id"),
        "sampleset_name": (rec.get("sampleset") or {}).get("sample_id"),
        "ancestry_broad": (rec.get("sampleset") or {}).get("ancestry_broad"),
        "samples": (rec.get("sampleset") or {}).get("samples") or [],
        "phenotyping_reported": rec.get("phenotyping_reported"),
        "covariates": rec.get("covariates"),
        "performance_metrics": rec.get("performance_metrics") or rec.get("performance_metric") or {},
        "publication_date": (rec.get("publication") or {}).get("date_publication"),
        "publication_pmid": (rec.get("publication") or {}).get("PMID"),
        "publication_title": (rec.get("publication") or {}).get("title"),
    }


def _metric_max(metrics: Any, is_auc: bool) -> Optional[float]:
    """Return max raw numeric metric for AUC-like or R2-like names.

    This is a compact data summary, not a ranking rule: it exposes raw
    magnitudes so the LLM can compare the underlying PGS records.
    """
    if not isinstance(metrics, dict):
        return None
    best: Optional[float] = None
    for key, entries in metrics.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            name = " ".join(
                str(part or "")
                for part in (entry.get("name_long"), entry.get("name_short"), key)
            ).lower()
            is_auc_like = any(t in name for t in ("auroc", "auc", "c-index", "c-stat"))
            is_r2_like = ("r2" in name) or ("r-squared" in name) or ("r²" in name)
            if is_auc and not is_auc_like:
                continue
            if (not is_auc) and not is_r2_like:
                continue
            est = entry.get("estimate") or entry.get("value")
            try:
                f = float(est)
            except (TypeError, ValueError):
                continue
            if best is None or f > best:
                best = f
    return best


def _record_sample_count(rec: dict[str, Any]) -> int:
    sampleset = rec.get("sampleset") or {}
    samples = sampleset.get("samples") or rec.get("samples") or []
    sample_count = 0
    for sample in samples:
        try:
            sample_count += int(sample.get("sample_number") or 0)
        except (AttributeError, TypeError, ValueError):
            continue
    return sample_count


def _record_ancestry(rec: dict[str, Any]) -> Any:
    sampleset = rec.get("sampleset") or {}
    ancestry = sampleset.get("ancestry_broad") or rec.get("ancestry_broad")
    if ancestry:
        return ancestry
    values: set[str] = set()
    for sample in sampleset.get("samples") or rec.get("samples") or []:
        text = str(sample.get("ancestry_broad") or "").strip()
        if text:
            values.add(text)
    return sorted(values)


def _performance_digest_entry(rec: dict[str, Any]) -> dict[str, Any]:
    metrics = rec.get("performance_metrics") or rec.get("performance_metric") or {}
    return {
        "ancestry_broad": _record_ancestry(rec),
        "sample_count": _record_sample_count(rec),
        "best_auc": _metric_max(metrics, True),
        "best_r2": _metric_max(metrics, False),
    }


def _summarize_performance_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    digests = [_performance_digest_entry(rec) for rec in records or [] if isinstance(rec, dict)]
    ancestries: set[str] = set()
    for digest in digests:
        raw = digest.get("ancestry_broad")
        values = raw if isinstance(raw, list) else [raw]
        for value in values:
            text = str(value or "").strip()
            if text:
                ancestries.add(text)

    best_auc: Optional[float] = None
    best_r2: Optional[float] = None
    largest_sample_count = 0
    summed_sample_count = 0
    records_with_metrics = 0
    for digest in digests:
        sample_count = int(digest.get("sample_count") or 0)
        summed_sample_count += sample_count
        largest_sample_count = max(largest_sample_count, sample_count)
        auc = digest.get("best_auc")
        r2 = digest.get("best_r2")
        if auc is not None:
            best_auc = auc if best_auc is None else max(best_auc, auc)
        if r2 is not None:
            best_r2 = r2 if best_r2 is None else max(best_r2, r2)
        if auc is not None or r2 is not None:
            records_with_metrics += 1

    return {
        "record_count": len(records or []),
        "records_with_metrics": records_with_metrics,
        "ancestry_broad_values": sorted(ancestries),
        "summed_sample_count": summed_sample_count,
        "largest_sample_count": largest_sample_count,
        "best_auc": best_auc,
        "best_r2": best_r2,
    }


def compact_pgs_summary(pgs_id: str) -> dict[str, Any]:
    """Minimal metadata for triage (no full performance records, but a
    tiny performance-metric digest so the LLM can see raw quality signal
    without blowing context).

    Keys returned:
      pgs_id, name, method_name, variants_number, reported_trait,
      trait_efo, trait_mapped, training_ancestry_broad, publication_year,
      publication_journal, performance_summary, performance_digest.

    `performance_summary` is aggregated across all performance records.
    `performance_digest` is a list of at most 4 entries across the PGS's
    performance records:
      - {ancestry, sample_count, best_auc, best_r2}
    where best_auc / best_r2 are the raw max values taken across all
    metric entries within that performance record (no tier, no priority).
    """
    pgs_id = str(pgs_id or "").strip().upper()
    if not pgs_id:
        return {"error": "empty_pgs_id"}
    client = _get_client()
    try:
        details = _cached_get_score_details(client, pgs_id) or {}
    except Exception as exc:  # noqa: BLE001
        logger.warning("PGS compact summary fetch failed for %s: %s", pgs_id, exc)
        return {"pgs_id": pgs_id, "error": f"details_error:{exc}"}
    try:
        performance = _cached_get_score_performance(client, pgs_id) or []
    except Exception as exc:  # noqa: BLE001
        logger.warning("PGS performance fetch failed for %s: %s", pgs_id, exc)
        performance = []

    ancestry = details.get("ancestry_distribution") or {}
    broad_list: list[str] = []
    if isinstance(ancestry, dict):
        for block in ancestry.values():
            if isinstance(block, dict):
                bb = block.get("ancestry_broad") or block.get("broad") or []
                if isinstance(bb, list):
                    broad_list.extend(str(x) for x in bb)
                elif isinstance(bb, str):
                    broad_list.append(bb)

    performance_digest = [_performance_digest_entry(rec) for rec in performance[:4]]

    pub = details.get("publication") or {}
    return {
        "pgs_id": details.get("id") or pgs_id,
        "name": details.get("name"),
        "method_name": details.get("method_name"),
        "variants_number": details.get("variants_number"),
        "reported_trait": details.get("trait_reported"),
        "trait_efo": details.get("trait_efo") or [],
        "trait_mapped": details.get("trait_mapped") or [],
        "training_ancestry_broad": sorted(set(broad_list)),
        "publication_year": (pub.get("date_publication") or "")[:4] if pub.get("date_publication") else None,
        "publication_journal": pub.get("journal"),
        "performance_summary": _summarize_performance_records(performance),
        "performance_digest": performance_digest,
    }


def describe_pgs_model(pgs_id: str) -> dict[str, Any]:
    """Return the full PGS Catalog record for one score.

    Output keys:
        pgs_id, method, variants_number, ftp_scoring_file,
        training_samples, training_ancestry_distribution,
        reported_trait, trait_efo, trait_mapped, trait_additional,
        publication (reduced to authors/journal/year/PMID/title),
        performance_records: list of ALL performance records, each with
            sampleset / ancestry_broad / samples / covariates /
            performance_metrics (unfiltered). No "primary" field
            selection, no ancestry tier preference.
    """
    pgs_id = str(pgs_id or "").strip().upper()
    if not pgs_id:
        return {"error": "empty_pgs_id"}
    client = _get_client()
    try:
        details = _cached_get_score_details(client, pgs_id) or {}
    except Exception as exc:  # noqa: BLE001
        logger.warning("PGS details fetch failed for %s: %s", pgs_id, exc)
        return {"pgs_id": pgs_id, "error": f"details_error:{exc}"}
    try:
        performance = _cached_get_score_performance(client, pgs_id) or []
    except Exception as exc:  # noqa: BLE001
        logger.warning("PGS performance fetch failed for %s: %s", pgs_id, exc)
        performance = []

    pub = details.get("publication") or {}
    out = {
        "pgs_id": details.get("id") or pgs_id,
        "name": details.get("name"),
        "method_name": details.get("method_name"),
        "method_params": details.get("method_params"),
        "variants_number": details.get("variants_number"),
        "ftp_scoring_file": details.get("ftp_scoring_file"),
        "reported_trait": details.get("trait_reported"),
        "trait_efo": details.get("trait_efo") or [],
        "trait_mapped": details.get("trait_mapped") or [],
        "trait_additional": details.get("trait_additional"),
        "training_samples": details.get("samples_variants") or [],
        "training_ancestry_distribution": details.get("ancestry_distribution") or {},
        "publication": {
            "id": pub.get("id"),
            "date": pub.get("date_publication"),
            "title": pub.get("title"),
            "journal": pub.get("journal"),
            "PMID": pub.get("PMID"),
            "doi": pub.get("doi"),
            "authors": pub.get("authors"),
        },
        "performance_summary": _summarize_performance_records(performance),
        "performance_records": [_normalize_performance_record(r) for r in performance],
    }
    return out
