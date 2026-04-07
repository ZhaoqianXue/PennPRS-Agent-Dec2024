from __future__ import annotations

from typing import Any, Iterable

from src.server.core.agent_artifacts import maybe_externalize_json
from src.server.core.tool_schemas import PGSSearchResult
from src.server.core.tools.prs_model_tools import (
    hydrate_pgs_model_summaries,
    prs_model_domain_knowledge,
)
from src.server.core.pgs_catalog_client import PGSCatalogClient
from src.server.modules.disease.recommendation_agent import (
    MAX_INLINE_CONTEXT_BYTES,
    TOP_MODELS_INLINE,
    Step1Decision,
    _build_step1_chain,
    _empty_domain_knowledge,
    _invoke_step1_chain,
    _summarize_search_result_for_llm,
)


def _dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for raw in values or []:
        value = str(raw or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _build_step1_domain_query(target_trait: str) -> str:
    return (
        f"target_trait: {target_trait}; PRS clinical thresholds AUC R2 heritability ceiling sanity-check "
        "must-pass gates phenotype alignment endpoint specificity "
        "external transfer reliability ancestry compatibility "
        "ranking features penalties method priors validation sample size tie-break "
        "time-to-event horizon-specific incident case-control dominant subtype "
        "PGS-only no-covariates incremental AUROC "
        "snpnet biobank transportability"
    )


def _build_todo_recitation(
    *,
    original_target_trait: str,
    matched_cross_trait: str,
    candidate_count: int,
) -> str:
    return "\n".join(
        [
            "# Current Task Progress",
            f"[x] Original target trait = {original_target_trait or 'Unknown'}",
            f"[x] Matched cross trait = {matched_cross_trait or 'Unknown'}",
            f"[x] Step 1: Hydrate explicit bundle whitelist ({candidate_count} candidates)",
            "[x] Step 1: Evaluate direct-match candidates",
        ]
    )


def _build_explicit_search_result(
    *,
    client: PGSCatalogClient,
    matched_cross_trait: str,
    candidate_pgs_ids: list[str],
) -> tuple[PGSSearchResult, list[str]]:
    requested_ids = _dedupe_preserve_order(candidate_pgs_ids)
    models = hydrate_pgs_model_summaries(client, requested_ids)
    return (
        PGSSearchResult(
            query_trait=matched_cross_trait,
            total_found=len(requested_ids),
            after_filter=len(models),
            models=models,
        ),
        requested_ids,
    )


def _build_retrieval_payload(
    requested_candidate_pgs_ids: list[str],
    pgs_result: PGSSearchResult,
) -> dict[str, Any]:
    hydrated_model_ids = [model.id for model in pgs_result.models]
    missing_candidate_pgs_ids = [
        pgs_id for pgs_id in requested_candidate_pgs_ids if pgs_id not in hydrated_model_ids
    ]
    unexpected_model_ids = [
        pgs_id for pgs_id in hydrated_model_ids if pgs_id not in requested_candidate_pgs_ids
    ]
    return {
        "mode": "explicit_candidate_pgs_ids",
        "requested_candidate_pgs_ids": requested_candidate_pgs_ids,
        "requested_candidate_count": len(requested_candidate_pgs_ids),
        "hydrated_model_ids": hydrated_model_ids,
        "hydrated_model_count": len(hydrated_model_ids),
        "missing_candidate_pgs_ids": missing_candidate_pgs_ids,
        "unexpected_model_ids": unexpected_model_ids,
        "universe_matches_candidate_ids": (
            hydrated_model_ids == requested_candidate_pgs_ids
            and not missing_candidate_pgs_ids
            and not unexpected_model_ids
        ),
    }


def recommend_best_model_for_cross_trait(
    *,
    original_target_trait: str,
    matched_cross_trait: str,
    matched_bundle_id: str | None,
    candidate_pgs_ids: list[str],
    use_domain_knowledge: bool = True,
) -> dict[str, Any]:
    client = PGSCatalogClient()
    pgs_result, requested_ids = _build_explicit_search_result(
        client=client,
        matched_cross_trait=matched_cross_trait,
        candidate_pgs_ids=candidate_pgs_ids,
    )
    retrieval = _build_retrieval_payload(requested_ids, pgs_result)

    domain_query = _build_step1_domain_query(matched_cross_trait)
    if use_domain_knowledge:
        knowledge = prs_model_domain_knowledge(domain_query) or _empty_domain_knowledge(
            domain_query,
            source_type="missing",
        )
    else:
        knowledge = _empty_domain_knowledge(domain_query, source_type="disabled_gpt_only")

    direct_models_dump = pgs_result.model_dump()
    direct_models_inline, direct_models_artifact = maybe_externalize_json(
        payload=direct_models_dump,
        artifact_prefix=f"cross_trait_direct_models_{matched_bundle_id or 'unknown_bundle'}",
        max_inline_bytes=MAX_INLINE_CONTEXT_BYTES,
        max_inline_tokens=2_000,
        summary_builder=lambda _: _summarize_search_result_for_llm(
            pgs_result,
            top_n=TOP_MODELS_INLINE,
        ),
    )
    step1_context = {
        "target_trait": matched_cross_trait,
        "original_target_trait": original_target_trait,
        "matched_cross_trait": matched_cross_trait,
        "matched_bundle_id": matched_bundle_id,
        "candidate_retrieval_mode": "explicit_candidate_pgs_ids",
        "direct_models": direct_models_inline,
        "direct_models_artifact": (
            direct_models_artifact.model_dump() if direct_models_artifact else None
        ),
        "domain_knowledge": knowledge.model_dump(),
        "todo_recitation_path": "N/A",
        "todo_recitation": _build_todo_recitation(
            original_target_trait=original_target_trait,
            matched_cross_trait=matched_cross_trait,
            candidate_count=pgs_result.after_filter,
        ),
    }

    if pgs_result.after_filter == 0:
        step1_decision = Step1Decision(
            outcome="NO_MATCH_FOUND",
            best_model_id=None,
            confidence="Low",
            rationale=(
                "The matched cross-trait bundle did not yield any hydratable candidate PGS models, "
                "so Contribution2 Step 1 could not evaluate a recommendation."
            ),
        )
        step1_error = None
    else:
        step1_decision, step1_error = _invoke_step1_chain(
            chain=_build_step1_chain(),
            context_payload=step1_context,
            pgs_result=pgs_result,
        )
        if step1_decision.outcome == "NO_MATCH_FOUND":
            step1_decision = Step1Decision(
                outcome="DIRECT_SUB_OPTIMAL",
                best_model_id=step1_decision.best_model_id or pgs_result.models[0].id,
                confidence=step1_decision.confidence,
                rationale=(
                    f"[Contribution3 explicit-whitelist override] Models exist "
                    f"(after_filter={pgs_result.after_filter}); NO_MATCH_FOUND invalid. "
                    f"Original: {step1_decision.rationale}"
                ),
            )

    return {
        "original_target_trait": original_target_trait,
        "matched_cross_trait": matched_cross_trait,
        "matched_bundle_id": matched_bundle_id,
        "candidate_pgs_ids": requested_ids,
        "retrieval": retrieval,
        "domain_query": domain_query,
        "domain_knowledge_source": knowledge.source_type,
        "decision": step1_decision.model_dump(),
        "step1_error": step1_error,
    }
