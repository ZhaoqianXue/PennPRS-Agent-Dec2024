"""Open Targets overlap tool — expanded raw-data extraction.

2026-04-24 rewrite: broader page size, pathway overlap, drug/clinical
candidate overlap, phenotype overlap, ancestor / therapeutic area
overlap. Still raw-data only (no scoring tiers, no derived confidence).

The LLM consumer reasons over:
  - shared_targets (gene-level overlap, expanded to 200 per side)
  - shared_pathways (Reactome-level overlap — new)
  - shared_phenotypes (HPO-level overlap)
  - therapeutic_areas, ancestors (ontology-level overlap)
  - clinical_candidate_counts (per-side drug-pipeline size — new)

Nothing is pre-ranked; the LLM decides weight.
"""
from __future__ import annotations

import logging
import re
from functools import lru_cache
from typing import Any, Optional

from src.server.core.opentargets_client import OpenTargetsClient

logger = logging.getLogger(__name__)

_CLIENT: Optional[OpenTargetsClient] = None

# Configuration knobs (I/O budget, not decision).
DEFAULT_PAGE_SIZE = 120           # I/O budget for disease profiles
PATHWAY_HYDRATE_CAP = 12          # per side: fetch pathways for top-N gene targets
PHENOTYPE_PAGE_SIZE = 150
SHARED_TARGET_OUTPUT_CAP = 40
SHARED_PATHWAY_OUTPUT_CAP = 20
ANCESTOR_OUTPUT_CAP = 20
PHENOTYPE_OUTPUT_CAP = 25
_LABEL_SPLIT_RE = re.compile(r"\s*[;\n|]\s*")


def _get_client() -> OpenTargetsClient:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = OpenTargetsClient()
    return _CLIENT


def _iter_label_queries(label: str) -> list[str]:
    """Return general disease-search queries from a possibly alias-joined label."""
    raw = str(label or "").strip()
    if not raw:
        return []
    queries: list[str] = []
    seen: set[str] = set()

    def _add(text: str) -> None:
        text = str(text or "").strip()
        key = text.lower()
        if text and key not in seen:
            queries.append(text)
            seen.add(key)

    _add(raw)
    for part in _LABEL_SPLIT_RE.split(raw):
        _add(part)
    return queries


def _first_search_result_id(query: str) -> Optional[str]:
    try:
        matches = _search_diseases_cached(query, 3) or []
    except Exception as exc:  # noqa: BLE001
        logger.warning("OT disease search failed for '%s': %s", query, exc)
        return None
    if isinstance(matches, dict):
        candidates = matches.get("hits") or matches.get("diseases") or matches.get("data") or []
    elif isinstance(matches, list):
        candidates = matches
    else:
        candidates = []
    if not candidates:
        return None
    first = candidates[0]
    if isinstance(first, dict):
        return first.get("id") or first.get("disease_id")
    return getattr(first, "id", None)


@lru_cache(maxsize=4096)
def _search_diseases_cached(query: str, size: int) -> Any:
    return _get_client().search_diseases(query, size=size)


@lru_cache(maxsize=4096)
def _disease_profile_cached(efo_id: str, page_size: int) -> dict[str, Any]:
    return _get_client().get_disease_target_profile(efo_id, page_size=page_size)


@lru_cache(maxsize=8192)
def _target_pathways_cached(ensembl_id: str) -> tuple[str, ...]:
    names = _get_client().get_target_pathways(ensembl_id) or []
    return tuple(str(n).strip() for n in names if n and str(n).strip())


@lru_cache(maxsize=4096)
def _disease_phenotypes_cached(efo_id: str, page_size: int) -> tuple[tuple[tuple[str, Any], ...], ...]:
    rows = _get_client().get_disease_phenotypes(efo_id, page_size=page_size) or []
    out = []
    for row in rows:
        if isinstance(row, dict):
            out.append(tuple(sorted(row.items())))
    return tuple(out)


def _resolve_label_to_efo(label: str) -> Optional[str]:
    label = str(label or "").strip()
    if not label:
        return None
    if label.startswith(("EFO_", "MONDO_", "HP_", "Orphanet_")):
        return label
    for query in _iter_label_queries(label):
        resolved = _first_search_result_id(query)
        if resolved:
            return resolved
    return None


def _profile_shared_targets(profile: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "gene": t.get("approvedSymbol"),
            "target_id": t.get("id"),
            "approved_name": t.get("approvedName"),
            "score": t.get("score"),
            "datatype_scores": t.get("datatypeScores") or [],
        }
        for t in profile.get("associated_targets") or []
    ]


def _fetch_target_pathways(ensembl_ids: list[str]) -> dict[str, list[str]]:
    """Return {ensembl_id -> list[pathway_name]} for the given targets.

    One OT API call per target (cheap; the agent only calls OT on a
    few candidate bundles per Gather round).
    """
    out: dict[str, list[str]] = {}
    for eid in ensembl_ids:
        if not eid:
            continue
        try:
            names = _target_pathways_cached(eid)
        except Exception as exc:  # noqa: BLE001
            logger.debug("OT pathway fetch for %s failed: %s", eid, exc)
            names = []
        out[eid] = [str(n).strip() for n in names if n and str(n).strip()]
    return out


def get_open_targets_overlap(
    target_label_or_efo: str,
    candidate_label_or_efo: str,
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict[str, Any]:
    """Return raw Open Targets overlap fields for a (target, candidate) pair.

    Output keys (all raw, no tiers):
        shared_targets:    [{gene, target_id, source_score, candidate_score,
                             source_datatype_scores, candidate_datatype_scores}]
        shared_pathways:   [{pathway_name, shared_target_genes: [symbol]}]
        ancestors:         [{id, name}] — shared ontology ancestors
        therapeutic_areas: [{id, name}] — shared top-level areas
        phenotypes:        [{hpo_id, hpo_name, frequency}] — shared HPO
        target_profile_target_count, candidate_profile_target_count,
        target_clinical_candidate_count, candidate_clinical_candidate_count,
        target_efo / candidate_efo

    Forbidden (not computed): weighted_overlap, confidence_level,
    genetic_support_present, any derived score.
    """
    target_efo = _resolve_label_to_efo(target_label_or_efo)
    candidate_efo = _resolve_label_to_efo(candidate_label_or_efo)
    out: dict[str, Any] = {
        "target_label": target_label_or_efo,
        "candidate_label": candidate_label_or_efo,
        "target_efo": target_efo,
        "candidate_efo": candidate_efo,
        "shared_targets": [],
        "shared_pathways": [],
        "ancestors": [],
        "therapeutic_areas": [],
        "phenotypes": [],
        "target_profile_target_count": 0,
        "candidate_profile_target_count": 0,
        "shared_target_count_total": 0,
        "shared_pathway_count_total": 0,
        "ancestor_count_total": 0,
        "phenotype_count_total": 0,
        "target_clinical_candidate_count": None,
        "candidate_clinical_candidate_count": None,
    }
    if not target_efo or not candidate_efo:
        out["unavailable_reason"] = (
            "target_not_resolved_to_efo" if not target_efo else "candidate_not_resolved_to_efo"
        )
        return out

    try:
        target_profile = _disease_profile_cached(target_efo, page_size)
        candidate_profile = _disease_profile_cached(candidate_efo, page_size)
    except Exception as exc:  # noqa: BLE001
        logger.warning("OT profile fetch failed: %s", exc)
        out["unavailable_reason"] = f"ot_profile_error:{exc}"
        return out

    target_targets = _profile_shared_targets(target_profile)
    candidate_targets = _profile_shared_targets(candidate_profile)
    candidate_by_id = {t["target_id"]: t for t in candidate_targets if t.get("target_id")}

    # Gene-level shared targets (sorted by combined score for the pathway
    # hydration step; the shared_targets list output preserves this order
    # so the LLM sees strongest-evidence shared genes first).
    shared: list[dict[str, Any]] = []
    for t in target_targets:
        c = candidate_by_id.get(t.get("target_id"))
        if c is None:
            continue
        shared.append(
            {
                "gene": t.get("gene"),
                "target_id": t.get("target_id"),
                "approved_name": t.get("approved_name"),
                "source_score": t.get("score"),
                "candidate_score": c.get("score"),
                "source_datatype_scores": t.get("datatype_scores"),
                "candidate_datatype_scores": c.get("datatype_scores"),
            }
        )

    def _combined_score(row: dict[str, Any]) -> float:
        try:
            return float(row.get("source_score") or 0) + float(row.get("candidate_score") or 0)
        except (TypeError, ValueError):
            return 0.0

    shared.sort(key=_combined_score, reverse=True)

    # Pathway overlap: compute for the top-N shared genes on BOTH sides
    # by looking up target pathways and intersecting.
    pathway_hydrate_ids = [row["target_id"] for row in shared[:PATHWAY_HYDRATE_CAP] if row.get("target_id")]
    pathway_map = _fetch_target_pathways(pathway_hydrate_ids)
    pathway_to_genes: dict[str, list[str]] = {}
    for row in shared[:PATHWAY_HYDRATE_CAP]:
        eid = row.get("target_id")
        if not eid:
            continue
        for pw in pathway_map.get(eid, []):
            pathway_to_genes.setdefault(pw, []).append(row.get("gene") or eid)

    # Only include pathways shared across 2+ shared genes (true overlap
    # signal, not a single-gene pathway listing).
    shared_pathways = [
        {"pathway_name": pw, "shared_target_genes": sorted(set(genes))}
        for pw, genes in pathway_to_genes.items()
        if len(set(genes)) >= 2
    ]
    shared_pathways.sort(key=lambda r: -len(r["shared_target_genes"]))

    target_areas = {ta["id"]: ta for ta in (target_profile.get("therapeutic_areas") or [])}
    candidate_areas = {ta["id"]: ta for ta in (candidate_profile.get("therapeutic_areas") or [])}
    shared_areas = [target_areas[k] for k in set(target_areas) & set(candidate_areas)]

    target_anc = {a["id"]: a for a in (target_profile.get("ancestors") or [])}
    candidate_anc = {a["id"]: a for a in (candidate_profile.get("ancestors") or [])}
    shared_anc = [target_anc[k] for k in set(target_anc) & set(candidate_anc)]

    try:
        target_phens = [
            dict(items) for items in _disease_phenotypes_cached(target_efo, PHENOTYPE_PAGE_SIZE)
        ]
        candidate_phens = [
            dict(items) for items in _disease_phenotypes_cached(candidate_efo, PHENOTYPE_PAGE_SIZE)
        ]
    except Exception as exc:  # noqa: BLE001
        logger.debug("OT phenotype fetch failed: %s", exc)
        target_phens = candidate_phens = []

    candidate_hpo_ids = {p.get("hpo_id") for p in candidate_phens}
    shared_phens = [p for p in target_phens if p.get("hpo_id") in candidate_hpo_ids]

    out.update(
        {
            "shared_targets": shared[:SHARED_TARGET_OUTPUT_CAP],
            "shared_pathways": shared_pathways[:SHARED_PATHWAY_OUTPUT_CAP],
            "ancestors": shared_anc[:ANCESTOR_OUTPUT_CAP],
            "therapeutic_areas": shared_areas,
            "phenotypes": shared_phens[:PHENOTYPE_OUTPUT_CAP],
            "target_profile_target_count": len(target_targets),
            "candidate_profile_target_count": len(candidate_targets),
            "shared_target_count_total": len(shared),
            "shared_pathway_count_total": len(shared_pathways),
            "ancestor_count_total": len(shared_anc),
            "phenotype_count_total": len(shared_phens),
            "target_clinical_candidate_count": target_profile.get("clinical_candidate_count"),
            "candidate_clinical_candidate_count": candidate_profile.get("clinical_candidate_count"),
        }
    )
    return out
