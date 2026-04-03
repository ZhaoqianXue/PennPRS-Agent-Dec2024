from __future__ import annotations

import json
from typing import Any, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from thefuzz import fuzz

from experiments.contribution3.transfer.common import (
    TraitBundle,
    load_gwas_gc_lookup_tables,
    normalize_text,
    resolve_texts_to_gwas_ids,
)
from src.server.core.opentargets_client import OpenTargetsClient
from src.server.core.tools.genetic_graph_tools import genetic_graph_validate_mechanism
from src.server.modules.heritability.aggregator import HeritabilityAggregator


class CrossTraitGeneticCorrelationInput(BaseModel):
    target_trait: str = Field(..., description="Target trait label")
    candidate_bundle_ids: list[str] = Field(..., description="Subset of candidate bundle IDs to inspect")


class CrossTraitHeritabilityInput(BaseModel):
    candidate_bundle_ids: list[str] = Field(..., description="Subset of candidate bundle IDs to inspect")
    ancestry: str = Field("EUR", description="Preferred ancestry when choosing best heritability estimate")


class CrossTraitOpenTargetsInput(BaseModel):
    target_trait: str = Field(..., description="Target trait label")
    candidate_bundle_ids: list[str] = Field(..., description="Subset of candidate bundle IDs to inspect")


class CrossTraitToolbox:
    def __init__(self, bundles: list[TraitBundle]):
        self.bundle_lookup = {bundle.bundle_id: bundle for bundle in bundles}
        self.heritability = HeritabilityAggregator()
        self.ot_client = OpenTargetsClient()
        self.gc_data, self.id_to_gwas_name, _, _ = load_gwas_gc_lookup_tables()
        self._target_resolution_cache: dict[str, Optional[tuple[int, str, int]]] = {}
        self._bundle_gc_resolution_cache: dict[str, Optional[tuple[int, str, int]]] = {}
        self._bundle_h2_cache: dict[str, dict[str, Any]] = {}
        self._bundle_ot_id_cache: dict[str, tuple[Optional[str], Optional[str]]] = {}
        self._target_ot_cache: dict[str, tuple[Optional[str], Optional[str]]] = {}

    def _candidate_bundle(self, bundle_id: str) -> Optional[TraitBundle]:
        return self.bundle_lookup.get(bundle_id)

    @staticmethod
    def _search_hit_id(hit: Any) -> str:
        if hasattr(hit, "id"):
            return str(getattr(hit, "id") or "")
        if isinstance(hit, dict):
            return str(hit.get("id") or "")
        return ""

    def _resolve_to_gwas_trait(self, texts: list[str]) -> Optional[tuple[int, str, int]]:
        resolutions = resolve_texts_to_gwas_ids(texts, min_score=70)
        return resolutions[0] if resolutions else None

    def _resolve_target_gc(self, target_trait: str) -> Optional[tuple[int, str, int]]:
        key = normalize_text(target_trait)
        if key not in self._target_resolution_cache:
            texts = [part.strip() for part in target_trait.split(";")] + [target_trait]
            self._target_resolution_cache[key] = self._resolve_to_gwas_trait(texts)
        return self._target_resolution_cache[key]

    def _resolve_bundle_gc(self, bundle: TraitBundle) -> Optional[tuple[int, str, int]]:
        if bundle.bundle_id not in self._bundle_gc_resolution_cache:
            texts = [bundle.canonical_label, *bundle.aliases]
            self._bundle_gc_resolution_cache[bundle.bundle_id] = self._resolve_to_gwas_trait(texts)
        return self._bundle_gc_resolution_cache[bundle.bundle_id]

    def _resolve_target_ot(self, target_trait: str) -> tuple[Optional[str], Optional[str]]:
        key = normalize_text(target_trait)
        if key in self._target_ot_cache:
            return self._target_ot_cache[key]

        efo_id: Optional[str] = None
        mondo_id: Optional[str] = None
        for query in [part.strip() for part in target_trait.split(";")] + [target_trait]:
            try:
                results = self.ot_client.search_diseases(query, page=0, size=8)
            except Exception:
                continue
            for hit in results.get("hits", []):
                hit_id = self._search_hit_id(hit)
                if hit_id.startswith("EFO_") and efo_id is None:
                    efo_id = hit_id
                elif hit_id.startswith("MONDO_") and mondo_id is None:
                    mondo_id = hit_id
                if efo_id and mondo_id:
                    break
            if efo_id or mondo_id:
                break
        self._target_ot_cache[key] = (efo_id, mondo_id)
        return efo_id, mondo_id

    def _resolve_bundle_ot(self, bundle: TraitBundle) -> tuple[Optional[str], Optional[str]]:
        if bundle.bundle_id in self._bundle_ot_id_cache:
            return self._bundle_ot_id_cache[bundle.bundle_id]

        efo_id = bundle.source_efo_ids[0] if bundle.source_efo_ids else None
        mondo_id = bundle.source_mondo_ids[0] if bundle.source_mondo_ids else None
        if not efo_id and not mondo_id:
            for query in [bundle.canonical_label, *bundle.aliases]:
                try:
                    results = self.ot_client.search_diseases(query, page=0, size=5)
                except Exception:
                    continue
                for hit in results.get("hits", []):
                    hit_id = self._search_hit_id(hit)
                    if hit_id.startswith("EFO_") and efo_id is None:
                        efo_id = hit_id
                    elif hit_id.startswith("MONDO_") and mondo_id is None:
                        mondo_id = hit_id
                    if efo_id or mondo_id:
                        break
                if efo_id or mondo_id:
                    break

        self._bundle_ot_id_cache[bundle.bundle_id] = (efo_id, mondo_id)
        return efo_id, mondo_id

    def cross_trait_genetic_correlation(
        self, target_trait: str, candidate_bundle_ids: list[str]
    ) -> dict[str, Any]:
        target_resolution = self._resolve_target_gc(target_trait)
        rows: list[dict[str, Any]] = []
        for bundle_id in candidate_bundle_ids:
            bundle = self._candidate_bundle(bundle_id)
            if bundle is None:
                continue
            candidate_resolution = self._resolve_bundle_gc(bundle)
            row: dict[str, Any] = {
                "bundle_id": bundle.bundle_id,
                "canonical_label": bundle.canonical_label,
                "source": "gwas_atlas",
                "target_resolution": target_resolution[1] if target_resolution else None,
                "candidate_resolution": candidate_resolution[1] if candidate_resolution else None,
                "rg_meta": None,
                "rg_z_meta": None,
                "n_correlations": None,
                "p_value": None,
                "unavailable_reason": None,
            }
            if target_resolution is None:
                row["unavailable_reason"] = "target_not_resolved_to_gwas_atlas"
            elif candidate_resolution is None:
                row["unavailable_reason"] = "candidate_not_resolved_to_gwas_atlas"
            else:
                pair_df = self.gc_data[
                    (
                        (self.gc_data["id1"] == target_resolution[0])
                        & (self.gc_data["id2"] == candidate_resolution[0])
                    )
                    | (
                        (self.gc_data["id1"] == candidate_resolution[0])
                        & (self.gc_data["id2"] == target_resolution[0])
                    )
                ]
                if pair_df.empty:
                    row["unavailable_reason"] = "pair_not_found_in_gwas_atlas_gc"
                else:
                    best = pair_df.sort_values("p", ascending=True).iloc[0]
                    row["rg_meta"] = float(best["rg"])
                    row["rg_z_meta"] = float(best["z"])
                    row["p_value"] = float(best["p"])
            rows.append(row)
        return {"target_trait": target_trait, "results": rows}

    def cross_trait_heritability(
        self, candidate_bundle_ids: list[str], ancestry: str = "EUR"
    ) -> dict[str, Any]:
        rows: list[dict[str, Any]] = []
        for bundle_id in candidate_bundle_ids:
            bundle = self._candidate_bundle(bundle_id)
            if bundle is None:
                continue
            if bundle.bundle_id not in self._bundle_h2_cache:
                best = None
                for query in [bundle.canonical_label, *bundle.aliases]:
                    estimate = self.heritability.get_best_estimate(query, ancestry=ancestry)
                    if estimate is None:
                        continue
                    if best is None:
                        best = estimate
                    else:
                        best_score = (best.n_samples or 0, -(best.h2_obs_se or 9999.0))
                        new_score = (estimate.n_samples or 0, -(estimate.h2_obs_se or 9999.0))
                        if new_score > best_score:
                            best = estimate
                if best is None:
                    self._bundle_h2_cache[bundle.bundle_id] = {
                        "bundle_id": bundle.bundle_id,
                        "canonical_label": bundle.canonical_label,
                        "best_h2": None,
                        "source": None,
                        "ancestry": ancestry,
                        "confidence": "Low",
                        "unavailable_reason": "no_heritability_estimate_found",
                    }
                else:
                    confidence = "High" if (best.n_samples or 0) >= 50000 else "Moderate"
                    self._bundle_h2_cache[bundle.bundle_id] = {
                        "bundle_id": bundle.bundle_id,
                        "canonical_label": bundle.canonical_label,
                        "best_h2": float(best.h2_obs),
                        "source": best.source.value,
                        "ancestry": best.population,
                        "confidence": confidence,
                        "unavailable_reason": None,
                    }
            rows.append(self._bundle_h2_cache[bundle.bundle_id])
        return {"ancestry": ancestry, "results": rows}

    def cross_trait_open_targets(
        self, target_trait: str, candidate_bundle_ids: list[str]
    ) -> dict[str, Any]:
        target_efo, target_mondo = self._resolve_target_ot(target_trait)
        rows: list[dict[str, Any]] = []
        for bundle_id in candidate_bundle_ids:
            bundle = self._candidate_bundle(bundle_id)
            if bundle is None:
                continue
            candidate_efo, candidate_mondo = self._resolve_bundle_ot(bundle)
            row: dict[str, Any] = {
                "bundle_id": bundle.bundle_id,
                "canonical_label": bundle.canonical_label,
                "shared_genes": [],
                "shared_pathways": [],
                "confidence_level": None,
                "mechanism_summary": None,
                "unavailable_reason": None,
            }
            if not target_efo and not target_mondo:
                row["unavailable_reason"] = "target_not_resolved_to_opentargets"
            elif not candidate_efo and not candidate_mondo:
                row["unavailable_reason"] = "candidate_not_resolved_to_opentargets"
            else:
                result = genetic_graph_validate_mechanism(
                    ot_client=self.ot_client,
                    source_trait_efo=target_efo or "",
                    target_trait_efo=candidate_efo or "",
                    source_trait_name=target_trait,
                    target_trait_name=bundle.canonical_label,
                    source_trait_mondo=target_mondo,
                    target_trait_mondo=candidate_mondo,
                )
                if hasattr(result, "error_type"):
                    row["unavailable_reason"] = getattr(result, "error_type", "open_targets_failed")
                else:
                    row["shared_genes"] = [gene.gene_symbol for gene in result.shared_genes[:10]]
                    row["shared_pathways"] = result.shared_pathways[:10]
                    row["confidence_level"] = result.confidence_level
                    row["mechanism_summary"] = result.mechanism_summary
            rows.append(row)
        return {"target_trait": target_trait, "results": rows}

    def build_tools(self) -> list[StructuredTool]:
        return [
            StructuredTool.from_function(
                func=self.cross_trait_genetic_correlation,
                name="cross_trait_genetic_correlation",
                description=(
                    "Lookup GWAS Atlas genetic correlation evidence for a target trait against "
                    "a batch of candidate cross-trait bundles."
                ),
                args_schema=CrossTraitGeneticCorrelationInput,
            ),
            StructuredTool.from_function(
                func=self.cross_trait_heritability,
                name="cross_trait_heritability",
                description=(
                    "Lookup best available heritability estimates for a batch of candidate "
                    "cross-trait bundles."
                ),
                args_schema=CrossTraitHeritabilityInput,
            ),
            StructuredTool.from_function(
                func=self.cross_trait_open_targets,
                name="cross_trait_open_targets",
                description=(
                    "Lookup Open Targets shared-gene and shared-pathway evidence for a target "
                    "trait against a batch of candidate cross-trait bundles."
                ),
                args_schema=CrossTraitOpenTargetsInput,
            ),
        ]

    @staticmethod
    def dump_tool_result(result: dict[str, Any]) -> str:
        return json.dumps(result, ensure_ascii=False)
