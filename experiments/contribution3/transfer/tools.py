from __future__ import annotations

from collections import defaultdict
from typing import Any, Literal, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from thefuzz import fuzz

from experiments.contribution3.transfer.common import (
    TraitBundle,
    load_gwas_gc_lookup_tables,
    normalize_text,
    resolve_texts_to_gwas_ids,
)
from experiments.contribution3.transfer.prompts.transfer_prompt import (
    GeneticCorrelationEvidence,
    GeneticCorrelationPairOption,
    HeritabilityDatum,
    HeritabilityEvidence,
    OpenTargetsEvidence,
    OpenTargetsSharedTarget,
    TraitResolution,
    TraitResolutionHit,
)
from src.server.core.opentargets_client import OpenTargetsClient
from src.server.modules.heritability.aggregator import HeritabilityAggregator
from src.server.modules.heritability.models import HeritabilityEstimate


ResponseFormat = Literal["concise", "detailed"]
DEFAULT_TOP_RESOLUTIONS = 3
OT_DATATYPE_WEIGHTS = {
    "genetic_association": 1.0,
    "clinical": 0.7,
    "somatic_mutation": 0.6,
    "affected_pathway": 0.55,
    "rna_expression": 0.45,
    "animal_model": 0.45,
    "known_drug": 0.45,
    "literature": 0.25,
}


class CrossTraitGeneticCorrelationInput(BaseModel):
    target_trait: str = Field(..., description="Target trait label")
    candidate_bundle_ids: list[str] = Field(..., description="Subset of candidate bundle IDs to inspect")
    response_format: ResponseFormat = Field(
        "concise",
        description="Controls response verbosity: concise or detailed.",
    )


class CrossTraitHeritabilityInput(BaseModel):
    target_trait: str = Field(..., description="Target trait label")
    candidate_bundle_ids: list[str] = Field(..., description="Subset of candidate bundle IDs to inspect")
    ancestry: str = Field("EUR", description="Preferred ancestry when choosing best heritability estimate")
    response_format: ResponseFormat = Field(
        "concise",
        description="Controls response verbosity: concise or detailed.",
    )


class CrossTraitOpenTargetsInput(BaseModel):
    target_trait: str = Field(..., description="Target trait label")
    candidate_bundle_ids: list[str] = Field(..., description="Subset of candidate bundle IDs to inspect")
    response_format: ResponseFormat = Field(
        "concise",
        description="Controls response verbosity: concise or detailed.",
    )


def _resolution_confidence(score: float | None) -> Literal["High", "Moderate", "Low", "Unresolved"]:
    if score is None:
        return "Unresolved"
    if score >= 90:
        return "High"
    if score >= 78:
        return "Moderate"
    if score >= 60:
        return "Low"
    return "Unresolved"


def _best_signal_strength(rg: float | None, p_value: float | None) -> str:
    if rg is None or p_value is None:
        return "Unavailable"
    abs_rg = abs(float(rg))
    if p_value < 0.05 and abs_rg >= 0.30:
        return "Strong"
    if p_value < 0.05 and abs_rg >= 0.15:
        return "Moderate"
    if abs_rg > 0:
        return "Weak"
    return "Unavailable"


def _estimate_match_score(query: str, label: str) -> float:
    if not query or not label:
        return 0.0
    return float(fuzz.token_set_ratio(normalize_text(query), normalize_text(label)))


def _weighted_datatype_support(raw_scores: dict[str, float]) -> float:
    if not raw_scores:
        return 0.0
    support = 0.0
    for datatype_id, score in raw_scores.items():
        support += OT_DATATYPE_WEIGHTS.get(datatype_id, 0.4) * float(score or 0.0)
    return support


def _normalize_datatype_scores(entries: list[dict[str, Any]]) -> dict[str, float]:
    normalized: dict[str, float] = {}
    for entry in entries or []:
        key = str(entry.get("id") or "").strip().lower()
        if not key:
            continue
        normalized[key] = float(entry.get("score") or 0.0)
    return normalized


class CrossTraitToolbox:
    def __init__(self, bundles: list[TraitBundle]):
        self.bundle_lookup = {bundle.bundle_id: bundle for bundle in bundles}
        self.heritability = HeritabilityAggregator()
        self.ot_client = OpenTargetsClient()
        self.gc_data, self.id_to_gwas_name, _, _ = load_gwas_gc_lookup_tables()
        self._target_gc_resolution_cache: dict[str, list[dict[str, Any]]] = {}
        self._bundle_gc_resolution_cache: dict[str, list[dict[str, Any]]] = {}
        self._target_ot_resolution_cache: dict[str, list[dict[str, Any]]] = {}
        self._bundle_ot_resolution_cache: dict[str, list[dict[str, Any]]] = {}
        self._target_h2_cache: dict[tuple[str, str], list[HeritabilityDatum]] = {}
        self._bundle_h2_cache: dict[tuple[str, str], list[HeritabilityDatum]] = {}
        self._ot_profile_cache: dict[tuple[str, ResponseFormat], dict[str, Any]] = {}

    def _candidate_bundle(self, bundle_id: str) -> Optional[TraitBundle]:
        return self.bundle_lookup.get(bundle_id)

    def _texts_for_target(self, target_trait: str) -> list[str]:
        parts = [part.strip() for part in str(target_trait or "").split(";") if part.strip()]
        return [*parts, str(target_trait or "").strip()]

    def _texts_for_bundle(self, bundle: TraitBundle) -> list[str]:
        return [bundle.canonical_label, *bundle.aliases]

    def _build_trait_resolution(
        self,
        *,
        query: str,
        system: Literal["gwas_atlas", "open_targets"],
        matches: list[dict[str, Any]],
        unavailable_reason: Optional[str] = None,
    ) -> TraitResolution:
        best = matches[0] if matches else None
        return TraitResolution(
            query=query,
            system=system,
            best_id=str(best.get("id")) if best and best.get("id") is not None else None,
            best_label=str(best.get("label")) if best and best.get("label") is not None else None,
            matched_text=str(best.get("matched_text")) if best and best.get("matched_text") is not None else None,
            confidence=_resolution_confidence(best.get("score") if best else None),
            alternatives=[
                TraitResolutionHit(
                    id=str(match.get("id") or ""),
                    label=str(match.get("label") or ""),
                    score=float(match.get("score") or 0.0),
                    source=str(match.get("matched_text") or ""),
                )
                for match in matches
            ],
            unavailable_reason=unavailable_reason,
        )

    def _resolve_to_gwas_candidates(self, texts: list[str], top_k: int = DEFAULT_TOP_RESOLUTIONS) -> list[dict[str, Any]]:
        best_by_id: dict[int, dict[str, Any]] = {}
        for text in texts:
            for trait_id, matched_name, score in resolve_texts_to_gwas_ids([text], min_score=60)[:top_k]:
                existing = best_by_id.get(trait_id)
                record = {
                    "id": int(trait_id),
                    "label": str(matched_name),
                    "score": float(score),
                    "matched_text": text,
                }
                if existing is None or record["score"] > existing["score"]:
                    best_by_id[trait_id] = record
        return sorted(best_by_id.values(), key=lambda item: (-item["score"], item["id"]))[:top_k]

    def _resolve_target_gc(self, target_trait: str) -> list[dict[str, Any]]:
        key = normalize_text(target_trait)
        if key not in self._target_gc_resolution_cache:
            self._target_gc_resolution_cache[key] = self._resolve_to_gwas_candidates(self._texts_for_target(target_trait))
        return self._target_gc_resolution_cache[key]

    def _resolve_bundle_gc(self, bundle: TraitBundle) -> list[dict[str, Any]]:
        if bundle.bundle_id not in self._bundle_gc_resolution_cache:
            self._bundle_gc_resolution_cache[bundle.bundle_id] = self._resolve_to_gwas_candidates(
                self._texts_for_bundle(bundle)
            )
        return self._bundle_gc_resolution_cache[bundle.bundle_id]

    def _search_hit_id(self, hit: Any) -> str:
        if hasattr(hit, "id"):
            return str(getattr(hit, "id") or "")
        if isinstance(hit, dict):
            return str(hit.get("id") or "")
        return ""

    def _search_hit_label(self, hit: Any) -> str:
        if hasattr(hit, "name"):
            return str(getattr(hit, "name") or "")
        if isinstance(hit, dict):
            return str(hit.get("name") or hit.get("label") or "")
        return ""

    def _search_hit_score(self, hit: Any) -> float:
        if hasattr(hit, "score"):
            return float(getattr(hit, "score") or 0.0)
        if isinstance(hit, dict):
            return float(hit.get("score") or 0.0)
        return 0.0

    def _resolve_to_ot_candidates(self, texts: list[str], top_k: int = DEFAULT_TOP_RESOLUTIONS) -> list[dict[str, Any]]:
        best_by_id: dict[str, dict[str, Any]] = {}
        for text in texts:
            try:
                results = self.ot_client.search_diseases(text, page=0, size=max(8, top_k * 2))
            except Exception:
                continue
            for hit in results.get("hits", []):
                hit_id = self._search_hit_id(hit)
                if not hit_id:
                    continue
                label = self._search_hit_label(hit)
                score = self._search_hit_score(hit)
                lexical = _estimate_match_score(text, label)
                combined = max(score * 100.0, lexical)
                record = {
                    "id": hit_id,
                    "label": label,
                    "score": combined,
                    "matched_text": text,
                }
                existing = best_by_id.get(hit_id)
                if existing is None or record["score"] > existing["score"]:
                    best_by_id[hit_id] = record
        return sorted(best_by_id.values(), key=lambda item: (-item["score"], item["id"]))[:top_k]

    def _resolve_target_ot(self, target_trait: str) -> list[dict[str, Any]]:
        key = normalize_text(target_trait)
        if key not in self._target_ot_resolution_cache:
            self._target_ot_resolution_cache[key] = self._resolve_to_ot_candidates(self._texts_for_target(target_trait))
        return self._target_ot_resolution_cache[key]

    def _resolve_bundle_ot(self, bundle: TraitBundle) -> list[dict[str, Any]]:
        if bundle.bundle_id not in self._bundle_ot_resolution_cache:
            preset: list[dict[str, Any]] = []
            for ontology_id in [*bundle.source_efo_ids, *bundle.source_mondo_ids]:
                preset.append(
                    {
                        "id": ontology_id,
                        "label": bundle.canonical_label,
                        "score": 100.0,
                        "matched_text": bundle.canonical_label,
                    }
                )
            if not preset:
                preset = self._resolve_to_ot_candidates(self._texts_for_bundle(bundle))
            self._bundle_ot_resolution_cache[bundle.bundle_id] = preset[:DEFAULT_TOP_RESOLUTIONS]
        return self._bundle_ot_resolution_cache[bundle.bundle_id]

    def _estimate_to_datum(self, estimate: HeritabilityEstimate, query: str) -> HeritabilityDatum:
        return HeritabilityDatum(
            trait_name=estimate.trait_name,
            trait_id=estimate.trait_id,
            h2_obs=float(estimate.h2_obs) if estimate.h2_obs is not None else None,
            h2_obs_se=float(estimate.h2_obs_se) if estimate.h2_obs_se is not None else None,
            population=estimate.population,
            source=estimate.source.value,
            n_samples=estimate.n_samples,
            method=estimate.method,
            h2_z=estimate.h2_z,
            match_score=_estimate_match_score(query, estimate.trait_name),
        )

    def _search_h2_profile(
        self,
        query: str,
        texts: list[str],
        ancestry: str,
        *,
        top_k: int,
        cache_key: tuple[str, str],
        cache: dict[tuple[str, str], list[HeritabilityDatum]],
    ) -> list[HeritabilityDatum]:
        if cache_key in cache:
            return cache[cache_key]
        deduped: dict[tuple[str, str, str, float], HeritabilityDatum] = {}
        for text in texts:
            try:
                estimates = self.heritability.search(text, ancestry=ancestry, min_score=60, limit=top_k)
            except Exception:
                continue
            for estimate in estimates:
                datum = self._estimate_to_datum(estimate, text)
                if datum.h2_obs is None:
                    continue
                dedupe_key = (
                    datum.trait_name,
                    datum.source or "",
                    datum.population or "",
                    float(datum.h2_obs),
                )
                existing = deduped.get(dedupe_key)
                if existing is None or datum.match_score > existing.match_score:
                    deduped[dedupe_key] = datum
        profile = sorted(
            deduped.values(),
            key=lambda datum: (
                -datum.match_score,
                -(datum.n_samples or 0),
                -(datum.h2_obs or 0.0),
                datum.h2_obs_se or 9999.0,
            ),
        )[:top_k]
        cache[cache_key] = profile
        return profile

    def _fetch_ot_profile(self, disease_id: str, response_format: ResponseFormat) -> dict[str, Any]:
        cache_key = (disease_id, response_format)
        if cache_key not in self._ot_profile_cache:
            page_size = 50 if response_format == "detailed" else 25
            try:
                self._ot_profile_cache[cache_key] = self.ot_client.get_disease_target_profile(
                    disease_id,
                    page_size=page_size,
                )
            except Exception as exc:
                self._ot_profile_cache[cache_key] = {
                    "id": disease_id,
                    "name": None,
                    "associated_targets": [],
                    "clinical_candidate_count": None,
                    "therapeutic_areas": [],
                    "ancestors": [],
                    "unavailable_reason": f"open_targets_profile_fetch_failed:{exc.__class__.__name__}",
                }
        return self._ot_profile_cache[cache_key]

    def _shared_targets_from_profiles(
        self,
        source_profile: dict[str, Any],
        candidate_profile: dict[str, Any],
        response_format: ResponseFormat,
    ) -> tuple[list[OpenTargetsSharedTarget], list[str], bool]:
        source_targets = {
            str(row.get("id") or ""): row
            for row in source_profile.get("associated_targets") or []
            if row.get("id")
        }
        candidate_targets = {
            str(row.get("id") or ""): row
            for row in candidate_profile.get("associated_targets") or []
            if row.get("id")
        }
        shared_ids = set(source_targets) & set(candidate_targets)
        shared: list[OpenTargetsSharedTarget] = []
        all_pathways: set[str] = set()
        genetic_support_present = False

        for target_id in shared_ids:
            source_row = source_targets[target_id]
            candidate_row = candidate_targets[target_id]
            source_datatype_scores = _normalize_datatype_scores(source_row.get("datatypeScores") or [])
            candidate_datatype_scores = _normalize_datatype_scores(candidate_row.get("datatypeScores") or [])
            if source_datatype_scores.get("genetic_association", 0.0) > 0.10 and candidate_datatype_scores.get(
                "genetic_association", 0.0
            ) > 0.10:
                genetic_support_present = True
            weighted_overlap = min(
                float(source_row.get("score") or 0.0),
                float(candidate_row.get("score") or 0.0),
            ) * (( _weighted_datatype_support(source_datatype_scores) + _weighted_datatype_support(candidate_datatype_scores) ) / 2.0)
            pathways = self.ot_client.get_target_pathways(target_id)
            if response_format == "concise":
                pathways = pathways[:5]
            all_pathways.update(pathways)
            shared.append(
                OpenTargetsSharedTarget(
                    target_id=target_id,
                    symbol=str(source_row.get("approvedSymbol") or candidate_row.get("approvedSymbol") or target_id),
                    source_score=float(source_row.get("score") or 0.0),
                    candidate_score=float(candidate_row.get("score") or 0.0),
                    min_score=min(
                        float(source_row.get("score") or 0.0),
                        float(candidate_row.get("score") or 0.0),
                    ),
                    weighted_overlap=round(weighted_overlap, 6),
                    source_datatype_scores=source_datatype_scores,
                    candidate_datatype_scores=candidate_datatype_scores,
                    pathways=pathways,
                )
            )

        shared.sort(
            key=lambda row: (
                -row.weighted_overlap,
                -row.min_score,
                row.symbol,
            )
        )
        limit = 8 if response_format == "detailed" else 4
        return shared[:limit], sorted(all_pathways), genetic_support_present

    def _therapeutic_area_overlap(
        self,
        source_profile: dict[str, Any],
        candidate_profile: dict[str, Any],
    ) -> tuple[bool, list[str], list[str], list[str]]:
        source_tas = {
            ta["id"]: ta.get("name") or ta["id"]
            for ta in source_profile.get("therapeutic_areas") or []
        }
        candidate_tas = {
            ta["id"]: ta.get("name") or ta["id"]
            for ta in candidate_profile.get("therapeutic_areas") or []
        }
        shared_ids = set(source_tas) & set(candidate_tas)
        shared_names = sorted(source_tas[tid] for tid in shared_ids)
        return (
            bool(shared_ids),
            shared_names,
            sorted(source_tas.values()),
            sorted(candidate_tas.values()),
        )

    def _ancestor_overlap(
        self,
        source_profile: dict[str, Any],
        candidate_profile: dict[str, Any],
    ) -> tuple[int, list[str]]:
        source_anc = {
            anc["id"]: anc.get("name") or anc["id"]
            for anc in source_profile.get("ancestors") or []
        }
        candidate_anc = {
            anc["id"]: anc.get("name") or anc["id"]
            for anc in candidate_profile.get("ancestors") or []
        }
        shared_ids = set(source_anc) & set(candidate_anc)
        # Exclude very broad ancestors (therapeutic area level) already captured above.
        source_ta_ids = {ta["id"] for ta in source_profile.get("therapeutic_areas") or []}
        candidate_ta_ids = {ta["id"] for ta in candidate_profile.get("therapeutic_areas") or []}
        ta_ids = source_ta_ids | candidate_ta_ids
        specific_shared = sorted(source_anc[aid] for aid in shared_ids if aid not in ta_ids)
        return len(specific_shared), specific_shared

    def _phenotype_overlap(
        self,
        source_id: str,
        candidate_id: str,
        response_format: ResponseFormat,
    ) -> tuple[int, list[str], float]:
        page_size = 100 if response_format == "detailed" else 50
        try:
            source_phenos = self.ot_client.get_disease_phenotypes(source_id, page_size=page_size)
        except Exception:
            source_phenos = []
        try:
            candidate_phenos = self.ot_client.get_disease_phenotypes(candidate_id, page_size=page_size)
        except Exception:
            candidate_phenos = []
        source_hpo = {p["hpo_id"]: p.get("hpo_name") or p["hpo_id"] for p in source_phenos}
        candidate_hpo = {p["hpo_id"]: p.get("hpo_name") or p["hpo_id"] for p in candidate_phenos}
        shared_ids = set(source_hpo) & set(candidate_hpo)
        shared_names = sorted(source_hpo[hid] for hid in shared_ids)
        total = len(set(source_hpo) | set(candidate_hpo))
        overlap_score = len(shared_ids) / total if total > 0 else 0.0
        limit = 10 if response_format == "detailed" else 5
        return len(shared_ids), shared_names[:limit], round(overlap_score, 4)

    def cross_trait_genetic_correlation(
        self,
        target_trait: str,
        candidate_bundle_ids: list[str],
        response_format: ResponseFormat = "concise",
    ) -> dict[str, Any]:
        target_matches = self._resolve_target_gc(target_trait)
        target_resolution = self._build_trait_resolution(
            query=target_trait,
            system="gwas_atlas",
            matches=target_matches,
            unavailable_reason="target_not_resolved_to_gwas_atlas" if not target_matches else None,
        )
        rows: list[dict[str, Any]] = []
        for bundle_id in candidate_bundle_ids:
            bundle = self._candidate_bundle(bundle_id)
            if bundle is None:
                continue
            candidate_matches = self._resolve_bundle_gc(bundle)
            candidate_resolution = self._build_trait_resolution(
                query=bundle.canonical_label,
                system="gwas_atlas",
                matches=candidate_matches,
                unavailable_reason="candidate_not_resolved_to_gwas_atlas" if not candidate_matches else None,
            )

            if not target_matches:
                evidence = GeneticCorrelationEvidence(
                    target_resolution=target_resolution,
                    candidate_resolution=candidate_resolution,
                    pair_status="target_unresolved",
                    provenance_status="not_available",
                    unavailable_reason="target_not_resolved_to_gwas_atlas",
                )
                rows.append({"bundle_id": bundle.bundle_id, "canonical_label": bundle.canonical_label, **evidence.model_dump()})
                continue

            if not candidate_matches:
                evidence = GeneticCorrelationEvidence(
                    target_resolution=target_resolution,
                    candidate_resolution=candidate_resolution,
                    pair_status="candidate_unresolved",
                    provenance_status="not_available",
                    unavailable_reason="candidate_not_resolved_to_gwas_atlas",
                )
                rows.append({"bundle_id": bundle.bundle_id, "canonical_label": bundle.canonical_label, **evidence.model_dump()})
                continue

            pair_options: list[tuple[GeneticCorrelationPairOption, dict[str, Any]]] = []
            for target_match in target_matches[: (3 if response_format == "detailed" else 1)]:
                for candidate_match in candidate_matches[: (3 if response_format == "detailed" else 1)]:
                    pair_df = self.gc_data[
                        (
                            (self.gc_data["id1"] == target_match["id"])
                            & (self.gc_data["id2"] == candidate_match["id"])
                        )
                        | (
                            (self.gc_data["id1"] == candidate_match["id"])
                            & (self.gc_data["id2"] == target_match["id"])
                        )
                    ]
                    pair_option = GeneticCorrelationPairOption(
                        target_trait_id=int(target_match["id"]),
                        target_trait_label=str(target_match["label"]),
                        candidate_trait_id=int(candidate_match["id"]),
                        candidate_trait_label=str(candidate_match["label"]),
                        score=float(target_match["score"] + candidate_match["score"]),
                    )
                    if pair_df.empty:
                        pair_options.append((pair_option, {}))
                        continue
                    best = pair_df.sort_values("p", ascending=True).iloc[0]
                    pair_options.append(
                        (
                            pair_option,
                            {
                                "rg": float(best["rg"]),
                                "z": float(best["z"]),
                                "p": float(best["p"]),
                            },
                        )
                    )

            found_pairs = [pair for pair in pair_options if pair[1]]
            if found_pairs:
                best_pair, metrics = sorted(
                    found_pairs,
                    key=lambda item: (item[1]["p"], -abs(item[1]["rg"]), -item[0].score),
                )[0]
                evidence = GeneticCorrelationEvidence(
                    target_resolution=target_resolution,
                    candidate_resolution=candidate_resolution,
                    pair_status="resolved_pair_found",
                    best_pair=best_pair,
                    alternative_pairs=[
                        pair_option
                        for pair_option, _ in pair_options[1 : (6 if response_format == "detailed" else 2)]
                    ],
                    rg=metrics["rg"],
                    z_score=metrics["z"],
                    p_value=metrics["p"],
                    study_count=None,
                    provenance_status="lookup_only",
                    evidence_strength=_best_signal_strength(metrics["rg"], metrics["p"]),
                )
            else:
                evidence = GeneticCorrelationEvidence(
                    target_resolution=target_resolution,
                    candidate_resolution=candidate_resolution,
                    pair_status="pair_not_found",
                    best_pair=pair_options[0][0] if pair_options else None,
                    alternative_pairs=[
                        pair_option
                        for pair_option, _ in pair_options[1 : (6 if response_format == "detailed" else 2)]
                    ],
                    provenance_status="lookup_only",
                    unavailable_reason="pair_not_found_in_gwas_atlas_gc",
                )
            rows.append({"bundle_id": bundle.bundle_id, "canonical_label": bundle.canonical_label, **evidence.model_dump()})
        return {"target_trait": target_trait, "response_format": response_format, "results": rows}

    def cross_trait_heritability(
        self,
        target_trait: str,
        candidate_bundle_ids: list[str],
        ancestry: str = "EUR",
        response_format: ResponseFormat = "concise",
    ) -> dict[str, Any]:
        target_profile = self._search_h2_profile(
            target_trait,
            self._texts_for_target(target_trait),
            ancestry,
            top_k=6 if response_format == "detailed" else 3,
            cache_key=(normalize_text(target_trait), ancestry),
            cache=self._target_h2_cache,
        )
        target_best_h2 = target_profile[0].h2_obs if target_profile else None
        rows: list[dict[str, Any]] = []
        for bundle_id in candidate_bundle_ids:
            bundle = self._candidate_bundle(bundle_id)
            if bundle is None:
                continue
            candidate_profile = self._search_h2_profile(
                bundle.canonical_label,
                self._texts_for_bundle(bundle),
                ancestry,
                top_k=6 if response_format == "detailed" else 3,
                cache_key=(bundle.bundle_id, ancestry),
                cache=self._bundle_h2_cache,
            )
            candidate_best_h2 = candidate_profile[0].h2_obs if candidate_profile else None
            best_n = candidate_profile[0].n_samples if candidate_profile else None
            best_se = candidate_profile[0].h2_obs_se if candidate_profile else None
            confidence_tier = "Low"
            if candidate_best_h2 is not None:
                if (best_n or 0) >= 100000 and (best_se or 0.0) <= 0.05:
                    confidence_tier = "High"
                elif (best_n or 0) >= 50000:
                    confidence_tier = "Moderate"
                else:
                    confidence_tier = "Low"

            shared_ceiling = None
            if target_best_h2 is not None and candidate_best_h2 is not None:
                shared_ceiling = min(target_best_h2, candidate_best_h2)
            elif candidate_best_h2 is not None:
                shared_ceiling = candidate_best_h2

            evidence = HeritabilityEvidence(
                ancestry=ancestry,
                target_profile=target_profile,
                candidate_profile=candidate_profile,
                target_best_h2=target_best_h2,
                candidate_best_h2=candidate_best_h2,
                candidate_signal_capacity=candidate_best_h2,
                shared_signal_ceiling_proxy=shared_ceiling,
                confidence_tier=confidence_tier,
                unavailable_reason=None if candidate_profile else "no_heritability_estimate_found",
            )
            rows.append({"bundle_id": bundle.bundle_id, "canonical_label": bundle.canonical_label, **evidence.model_dump()})
        return {
            "target_trait": target_trait,
            "ancestry": ancestry,
            "response_format": response_format,
            "results": rows,
        }

    def cross_trait_open_targets(
        self,
        target_trait: str,
        candidate_bundle_ids: list[str],
        response_format: ResponseFormat = "concise",
    ) -> dict[str, Any]:
        target_matches = self._resolve_target_ot(target_trait)
        target_resolution = self._build_trait_resolution(
            query=target_trait,
            system="open_targets",
            matches=target_matches,
            unavailable_reason="target_not_resolved_to_opentargets" if not target_matches else None,
        )
        rows: list[dict[str, Any]] = []
        for bundle_id in candidate_bundle_ids:
            bundle = self._candidate_bundle(bundle_id)
            if bundle is None:
                continue
            candidate_matches = self._resolve_bundle_ot(bundle)
            candidate_resolution = self._build_trait_resolution(
                query=bundle.canonical_label,
                system="open_targets",
                matches=candidate_matches,
                unavailable_reason="candidate_not_resolved_to_opentargets" if not candidate_matches else None,
            )

            if not target_matches:
                evidence = OpenTargetsEvidence(
                    target_resolution=target_resolution,
                    candidate_resolution=candidate_resolution,
                    pair_status="target_unresolved",
                    unavailable_reason="target_not_resolved_to_opentargets",
                )
                rows.append({"bundle_id": bundle.bundle_id, "canonical_label": bundle.canonical_label, **evidence.model_dump()})
                continue
            if not candidate_matches:
                evidence = OpenTargetsEvidence(
                    target_resolution=target_resolution,
                    candidate_resolution=candidate_resolution,
                    pair_status="candidate_unresolved",
                    unavailable_reason="candidate_not_resolved_to_opentargets",
                )
                rows.append({"bundle_id": bundle.bundle_id, "canonical_label": bundle.canonical_label, **evidence.model_dump()})
                continue

            best_evidence: OpenTargetsEvidence | None = None
            best_tuple: tuple[float, int] | None = None
            target_limit = 2 if response_format == "detailed" else 1
            candidate_limit = 2 if response_format == "detailed" else 1
            for target_match in target_matches[:target_limit]:
                for candidate_match in candidate_matches[:candidate_limit]:
                    source_profile = self._fetch_ot_profile(str(target_match["id"]), response_format)
                    candidate_profile = self._fetch_ot_profile(str(candidate_match["id"]), response_format)
                    profile_unavailable_reason = source_profile.get("unavailable_reason") or candidate_profile.get(
                        "unavailable_reason"
                    )
                    if profile_unavailable_reason:
                        evidence = OpenTargetsEvidence(
                            target_resolution=self._build_trait_resolution(
                                query=target_trait,
                                system="open_targets",
                                matches=[target_match],
                            ),
                            candidate_resolution=self._build_trait_resolution(
                                query=bundle.canonical_label,
                                system="open_targets",
                                matches=[candidate_match],
                            ),
                            pair_status="unavailable",
                            source_association_count=len(source_profile.get("associated_targets") or []),
                            candidate_association_count=len(candidate_profile.get("associated_targets") or []),
                            target_clinical_candidate_count=source_profile.get("clinical_candidate_count"),
                            candidate_clinical_candidate_count=candidate_profile.get("clinical_candidate_count"),
                            unavailable_reason=profile_unavailable_reason,
                        )
                        compare_tuple = (-1.0, 0)
                        if best_tuple is None or compare_tuple > best_tuple:
                            best_tuple = compare_tuple
                            best_evidence = evidence
                        continue
                    shared_targets, shared_pathways, genetic_support_present = self._shared_targets_from_profiles(
                        source_profile,
                        candidate_profile,
                        response_format,
                    )
                    weighted_overlap = round(sum(target.weighted_overlap for target in shared_targets), 6)
                    literature_scores = [
                        (target.source_datatype_scores.get("literature", 0.0) + target.candidate_datatype_scores.get("literature", 0.0)) / 2.0
                        for target in shared_targets
                    ]
                    genetic_scores = [
                        (target.source_datatype_scores.get("genetic_association", 0.0) + target.candidate_datatype_scores.get("genetic_association", 0.0)) / 2.0
                        for target in shared_targets
                    ]
                    avg_literature = sum(literature_scores) / len(literature_scores) if literature_scores else 0.0
                    avg_genetic = sum(genetic_scores) / len(genetic_scores) if genetic_scores else 0.0
                    literature_dominance_warning = bool(shared_targets) and avg_literature > (avg_genetic * 1.2 + 0.05)
                    if weighted_overlap >= 1.2 and len(shared_targets) >= 3 and genetic_support_present:
                        confidence_level = "High"
                    elif weighted_overlap >= 0.20 and shared_targets:
                        confidence_level = "Moderate"
                    else:
                        confidence_level = "Low"
                    if not shared_targets:
                        pair_status = "no_shared_targets"
                    else:
                        pair_status = "resolved_overlap"

                    if shared_pathways:
                        if len(shared_pathways) <= max(4, len(shared_targets) * 2):
                            pathway_specificity = "specific"
                        elif len(shared_pathways) <= max(12, len(shared_targets) * 4):
                            pathway_specificity = "moderate"
                        else:
                            pathway_specificity = "broad"
                    else:
                        pathway_specificity = "unknown"

                    # Therapeutic area overlap
                    ta_match, shared_ta_names, src_ta_names, cand_ta_names = self._therapeutic_area_overlap(
                        source_profile, candidate_profile,
                    )
                    # Ontology ancestor overlap
                    ancestor_count, shared_ancestor_names = self._ancestor_overlap(
                        source_profile, candidate_profile,
                    )
                    # Phenotype (HPO) overlap
                    pheno_count, shared_pheno_names, pheno_overlap_score = self._phenotype_overlap(
                        str(target_match["id"]), str(candidate_match["id"]), response_format,
                    )

                    mechanism_summary = None
                    if shared_targets:
                        top_symbol = shared_targets[0].symbol
                        mechanism_summary = (
                            f"Shared target overlap found for {len(shared_targets)} targets; "
                            f"top shared target = {top_symbol}; weighted_overlap = {weighted_overlap:.3f}."
                        )
                    else:
                        mechanism_summary = "No shared target overlap found in the retrieved Open Targets profiles."

                    evidence = OpenTargetsEvidence(
                        target_resolution=self._build_trait_resolution(
                            query=target_trait,
                            system="open_targets",
                            matches=[target_match],
                        ),
                        candidate_resolution=self._build_trait_resolution(
                            query=bundle.canonical_label,
                            system="open_targets",
                            matches=[candidate_match],
                        ),
                        pair_status=pair_status,
                        source_association_count=len(source_profile.get("associated_targets") or []),
                        candidate_association_count=len(candidate_profile.get("associated_targets") or []),
                        weighted_shared_target_overlap_score=weighted_overlap,
                        shared_target_count=len(shared_targets),
                        top_shared_targets=shared_targets,
                        shared_pathway_clusters=shared_pathways[: (12 if response_format == "detailed" else 5)],
                        pathway_specificity=pathway_specificity,
                        target_clinical_candidate_count=source_profile.get("clinical_candidate_count"),
                        candidate_clinical_candidate_count=candidate_profile.get("clinical_candidate_count"),
                        therapeutic_area_match=ta_match,
                        shared_therapeutic_areas=shared_ta_names,
                        source_therapeutic_areas=src_ta_names,
                        candidate_therapeutic_areas=cand_ta_names,
                        shared_ancestor_count=ancestor_count,
                        shared_ancestors=shared_ancestor_names[: (20 if response_format == "detailed" else 8)],
                        shared_phenotype_count=pheno_count,
                        shared_phenotypes=shared_pheno_names,
                        phenotype_overlap_score=pheno_overlap_score,
                        literature_dominance_warning=literature_dominance_warning,
                        genetic_support_present=genetic_support_present,
                        confidence_level=confidence_level,
                        mechanism_summary=mechanism_summary,
                    )
                    compare_tuple = (weighted_overlap, len(shared_targets))
                    if best_tuple is None or compare_tuple > best_tuple:
                        best_tuple = compare_tuple
                        best_evidence = evidence

            if best_evidence is None:
                best_evidence = OpenTargetsEvidence(
                    target_resolution=target_resolution,
                    candidate_resolution=candidate_resolution,
                    pair_status="unavailable",
                    unavailable_reason="open_targets_profile_unavailable",
                )
            rows.append({"bundle_id": bundle.bundle_id, "canonical_label": bundle.canonical_label, **best_evidence.model_dump()})
        return {"target_trait": target_trait, "response_format": response_format, "results": rows}

    def build_tools(self) -> list[StructuredTool]:
        return [
            StructuredTool.from_function(
                func=self.cross_trait_genetic_correlation,
                name="cross_trait_genetic_correlation",
                description=(
                    "Retrieve deterministic GWAS Atlas cross-trait genetic correlation evidence, "
                    "including trait resolution artifacts, best resolved pair, alternative pairs, "
                    "rg/z/p, and pair status. Use response_format='detailed' for shortlist-stage evidence."
                ),
                args_schema=CrossTraitGeneticCorrelationInput,
            ),
            StructuredTool.from_function(
                func=self.cross_trait_heritability,
                name="cross_trait_heritability",
                description=(
                    "Retrieve target and candidate heritability profiles, including per-source h2 estimates, "
                    "signal-capacity summary, and shared-signal ceiling proxy. Use response_format='detailed' "
                    "for shortlist-stage evidence."
                ),
                args_schema=CrossTraitHeritabilityInput,
            ),
            StructuredTool.from_function(
                func=self.cross_trait_open_targets,
                name="cross_trait_open_targets",
                description=(
                    "Retrieve richer Open Targets mechanism evidence, including target resolution, shared target "
                    "overlap, datatype score breakdowns, pathway specificity, clinical candidate counts, and "
                    "literature-dominance warnings. Use response_format='detailed' for shortlist-stage evidence."
                ),
                args_schema=CrossTraitOpenTargetsInput,
            ),
        ]
