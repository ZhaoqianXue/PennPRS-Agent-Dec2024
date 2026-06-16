from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from experiments.contribution2.recommendation.direct_baseline_sufficiency import (
    adjudicate_direct_baseline_sufficiency,
)
from experiments.contribution3.transfer.common import DEFAULT_TRANSFER_ABLATION

from .artifact_store import (
    C2_RUN_DIR,
    C2_SOURCE_MANIFEST,
    C3_DOSSIER_PATH,
    C3_EVAL_SUMMARY_PATH,
    C3_RESULT_PATH,
    PROJECT_ROOT,
    cached_examples,
    find_c2_artifact,
    find_c3_dossier,
    find_c3_result,
    format_candidate_model_preview,
    load_c2_artifacts,
    selected_candidate_summary,
    slugify,
)
from .models import (
    AgentTraceStep,
    FinalRecommendation,
    PennPRSAgentResponse,
    SameTraitQualityAssessment,
)


LIVE_RUNS_DIR = PROJECT_ROOT / "experiments" / "pennprs_agent_live_runs"


def _display_path(path: Any) -> str:
    artifact_path = Path(path)
    try:
        return str(artifact_path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(artifact_path)


def get_examples() -> dict[str, Any]:
    return {"examples": cached_examples()}


def recommend(target_trait: str, mode: str = "cached") -> PennPRSAgentResponse:
    started = time.time()
    warnings: list[str] = []
    errors: list[str] = []
    artifacts: list[dict[str, Any]] = []

    target_trait = target_trait.strip()
    if mode == "live":
        same_trait_result = _run_live_same_trait(target_trait, warnings, errors, artifacts)
    else:
        same_trait_result = _load_cached_same_trait(target_trait, warnings, errors, artifacts)

    assessment = _assess_same_trait(
        target_trait=target_trait,
        same_trait_result=same_trait_result,
        use_llm=mode == "live",
    )
    same_trait_result = _public_same_trait_result(same_trait_result)
    transfer_result = None
    if not assessment.accept_direct_baseline:
        if mode == "live":
            transfer_result = _run_live_transfer(target_trait, warnings, errors, artifacts)
        else:
            transfer_result = _load_cached_transfer(target_trait, warnings, errors, artifacts)

    final = _build_final_recommendation(same_trait_result, assessment, transfer_result)
    trace = _build_trace(target_trait, same_trait_result, assessment, transfer_result, final)
    elapsed_ms = round((time.time() - started) * 1000, 1)

    return PennPRSAgentResponse(
        target_trait=target_trait,
        mode=mode,  # type: ignore[arg-type]
        same_trait_result=same_trait_result,
        same_trait_quality_assessment=assessment,
        transfer_result=transfer_result,
        final_recommendation=final,
        agent_trace_steps=trace,
        artifacts_used=artifacts,
        warnings=warnings,
        errors=errors,
        timing={"elapsed_ms": elapsed_ms, "completed_at": datetime.utcnow().isoformat() + "Z"},
    )


def _load_cached_same_trait(
    target_trait: str,
    warnings: list[str],
    errors: list[str],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    match = find_c2_artifact(target_trait)
    artifacts.append({
        "name": "same-trait retained run",
        "path": str(C2_RUN_DIR.relative_to(PROJECT_ROOT)),
        "role": "cached same-trait baseline",
    })
    if not match:
        warnings.append("No cached same-trait artifact matched the target trait.")
        return _unavailable_same_trait(target_trait)
    if match.get("match_kind") == "candidate_label_fuzzy":
        warnings.append(
            "Cached same-trait matching used a low-confidence candidate-label fallback; "
            "the harness will require transfer evidence before finalizing."
        )
    return _same_trait_result_from_artifact(
        target_trait=target_trait,
        match=match,
        execution_mode="cached",
    )


def _same_trait_result_from_artifact(
    *,
    target_trait: str,
    match: dict[str, Any],
    execution_mode: str,
) -> dict[str, Any]:
    row = match.get("result") or {}
    stage1 = match.get("stage1") or {}
    stage2 = match.get("stage2") or {}
    metadata = match.get("metadata") or {}
    pgs_id = row.get("recommended_pgs_id")
    selected = selected_candidate_summary(metadata, pgs_id)
    preview = format_candidate_model_preview(selected)
    previews = _candidate_model_previews(
        metadata.get("candidate_models_visible_to_llm") or [],
        preferred_ids=[
            pgs_id,
            *(stage2.get("ranked_candidate_ids") or []),
            *(row.get("candidate_model_ids") or []),
        ],
    )
    perf = (selected or {}).get("performance_metrics") or {}
    return {
        "status": "found",
        "execution_mode": execution_mode,
        "resolved_trait": row.get("ontology") or metadata.get("ontology") or target_trait,
        "match_score": round(float(match.get("score") or 1.0), 3),
        "match_kind": match.get("match_kind") or "runner_output",
        "matched_label": match.get("matched_label"),
        "recommendation_type": row.get("recommendation_type"),
        "pgs_id": pgs_id,
        "confidence": row.get("recommendation_confidence"),
        "rationale": stage2.get("rationale") or row.get("rationale") or (stage1.get("decision") or {}).get("rationale"),
        "models_evaluated": row.get("n_models") or len(row.get("candidate_model_ids") or []),
        "candidate_model_ids": row.get("candidate_model_ids") or [],
        "shortlist_model_ids": stage2.get("ranked_candidate_ids") or [],
        "selected_model_evidence": {
            "trait_reported": (selected or {}).get("trait_reported"),
            "trait_efo": (selected or {}).get("trait_efo"),
            "method": (selected or {}).get("method_name"),
            "ancestry_distribution": (selected or {}).get("ancestry_distribution"),
            "samples_training": (selected or {}).get("samples_training"),
            "validation_sample_size": (selected or {}).get("validation_sample_size"),
            "performance_metrics": perf,
        },
        "model_preview": preview,
        "model_previews": previews,
        "_sufficiency_context": _sufficiency_context_from_match(match, pgs_id),
    }


def _sufficiency_context_from_match(match: dict[str, Any], pgs_id: Optional[str]) -> dict[str, Any]:
    stage1 = match.get("stage1") or {}
    stage2 = match.get("stage2") or {}
    metadata = match.get("metadata") or {}
    stage1_decision = stage1.get("decision") or {}
    shortlist_ids = list(stage2.get("ranked_candidate_ids") or [])
    candidate_ids = []
    for candidate_id in [pgs_id, *shortlist_ids]:
        if candidate_id and candidate_id not in candidate_ids:
            candidate_ids.append(candidate_id)
    candidate_summaries = []
    for candidate in metadata.get("candidate_models_visible_to_llm") or []:
        candidate_id = candidate.get("id") or candidate.get("pgs_id")
        if candidate_id in candidate_ids:
            candidate_summaries.append(candidate)
    return {
        "stage1_decision": stage1_decision,
        "stage2_decision": {
            "winner_model_id": stage2.get("winner_model_id"),
            "confidence": stage2.get("confidence"),
            "rationale": stage2.get("rationale"),
            "ranked_candidate_ids": shortlist_ids,
            "error": stage2.get("error"),
        },
        "candidate_summaries": candidate_summaries,
        "domain_knowledge": _domain_knowledge_from_stage1(stage1),
    }


def _domain_knowledge_from_stage1(stage1: dict[str, Any]) -> dict[str, Any]:
    raw_context = stage1.get("context_json")
    if not isinstance(raw_context, str) or not raw_context.strip():
        return {}
    try:
        context = json.loads(raw_context)
    except json.JSONDecodeError:
        return {}
    domain = context.get("domain_knowledge")
    return domain if isinstance(domain, dict) else {}


def _public_same_trait_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in result.items()
        if not str(key).startswith("_")
    }


def _candidate_model_previews(
    candidate_summaries: list[dict[str, Any]],
    preferred_ids: list[Optional[str]],
) -> list[dict[str, Any]]:
    by_id = {
        candidate.get("id"): candidate
        for candidate in candidate_summaries
        if candidate.get("id")
    }
    ordered_ids: list[str] = []
    for candidate_id in preferred_ids:
        if candidate_id and candidate_id in by_id and candidate_id not in ordered_ids:
            ordered_ids.append(candidate_id)
    for candidate in candidate_summaries:
        candidate_id = candidate.get("id")
        if candidate_id and candidate_id not in ordered_ids:
            ordered_ids.append(candidate_id)

    previews = [
        format_candidate_model_preview(by_id[candidate_id])
        for candidate_id in ordered_ids
    ]
    return [preview for preview in previews if preview]


def _unavailable_same_trait(target_trait: str) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "execution_mode": "none",
        "resolved_trait": target_trait,
        "match_score": 0.0,
        "match_kind": "none",
        "matched_label": None,
        "recommendation_type": "NO_MATCH_FOUND",
        "pgs_id": None,
        "confidence": "Low",
        "rationale": "No same-trait PGS baseline could be selected from the available evidence.",
        "models_evaluated": 0,
        "candidate_model_ids": [],
        "shortlist_model_ids": [],
        "selected_model_evidence": {},
        "model_preview": None,
        "_sufficiency_context": {},
    }


def _assess_same_trait(
    *,
    target_trait: str,
    same_trait_result: dict[str, Any],
    use_llm: bool,
) -> SameTraitQualityAssessment:
    context = same_trait_result.get("_sufficiency_context") or {}
    decision = adjudicate_direct_baseline_sufficiency(
        target_trait=target_trait,
        same_trait_result=same_trait_result,
        stage1_decision=context.get("stage1_decision"),
        stage2_decision=context.get("stage2_decision"),
        candidate_summaries=context.get("candidate_summaries"),
        domain_knowledge=context.get("domain_knowledge"),
        use_llm=use_llm,
    )
    return SameTraitQualityAssessment(
        accept_direct_baseline=decision.accept_direct_baseline,
        rationale=decision.rationale,
    )


def _load_cached_transfer(
    target_trait: str,
    warnings: list[str],
    errors: list[str],
    artifacts: list[dict[str, Any]],
) -> Optional[dict[str, Any]]:
    artifacts.append({
        "name": "transfer retained run",
        "path": _display_path(C3_RESULT_PATH),
        "role": "cached transfer recommendation",
    })
    artifacts.append({
        "name": "transfer retained evaluation summary",
        "path": _display_path(C3_EVAL_SUMMARY_PATH),
        "role": "cached transfer benchmark summary",
    })
    if not C3_RESULT_PATH.exists():
        warnings.append(
            "Cached transfer artifact unavailable; skipping transfer escalation instead of failing the request. "
            f"Missing artifact: {_display_path(C3_RESULT_PATH)}"
        )
        return None
    try:
        match = find_c3_result(target_trait)
    except (OSError, json.JSONDecodeError) as exc:
        warnings.append(
            "Cached transfer artifact could not be read; skipping transfer escalation instead of failing the request. "
            f"{type(exc).__name__}: {exc}"
        )
        return None
    if not match:
        warnings.append("No cached transfer artifact matched the target trait.")
        return None
    return _transfer_result_from_artifact(
        match["result"],
        execution_mode="cached",
        match_score=match["score"],
        match_kind=match.get("match_kind"),
        matched_label=match.get("matched_label"),
    )


def _transfer_result_from_artifact(
    row: dict[str, Any],
    *,
    execution_mode: str,
    match_score: float = 1.0,
    match_kind: Optional[str] = None,
    matched_label: Optional[str] = None,
) -> dict[str, Any]:
    target = row.get("target") or {}
    decision = row.get("decision") or {}
    stage2 = decision.get("stage2") or {}
    best_id = decision.get("best_model_id") or stage2.get("primary_model_id")
    frontier = decision.get("model_frontier") or stage2.get("model_frontier") or []
    selected = next((item for item in frontier if item.get("pgs_id") == best_id), None)
    source_trait = decision.get("best_cross_trait")
    recommended_ids = decision.get("recommended_model_ids") or []
    frontier_ids = [item.get("pgs_id") for item in frontier if item.get("pgs_id")]
    return {
        "status": "found" if decision.get("outcome") == "MATCHED" and best_id else "unavailable",
        "execution_mode": execution_mode,
        "target_trait": target.get("target_label"),
        "match_score": round(float(match_score or 1.0), 3),
        "match_kind": match_kind,
        "matched_label": matched_label,
        "outcome": decision.get("outcome"),
        "source_trait": source_trait,
        "source_bundle_id": decision.get("best_bundle_id") or decision.get("primary_bundle_id"),
        "pgs_id": best_id,
        "confidence": decision.get("confidence") or (selected or {}).get("confidence"),
        "rationale": (selected or {}).get("rationale") or stage2.get("decision_rationale") or decision.get("selection_reason"),
        "frontier_model_ids": frontier_ids,
        "frontier": frontier[:10],
        "model_previews": _transfer_model_previews(
            source_trait=source_trait,
            frontier=frontier,
            preferred_ids=[best_id, *recommended_ids, *frontier_ids],
        ),
        "trace_summary": {
            "frontier_bundle_ids": decision.get("frontier_bundle_ids") or [],
            "candidate_pgs_count": len(decision.get("candidate_pgs_ids_union") or decision.get("candidate_pgs_ids") or []),
            "tool_ablation_config": ((row.get("trace") or {}).get("tool_ablation_config") or {}),
        },
    }


def _transfer_model_previews(
    *,
    source_trait: Optional[str],
    frontier: list[dict[str, Any]],
    preferred_ids: list[Optional[str]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    source_match = None
    if source_trait:
        source_match = find_c2_artifact(source_trait)
        if source_match:
            metadata = source_match.get("metadata") or {}
            candidates.extend(metadata.get("candidate_models_visible_to_llm") or [])

    wanted_ids = {candidate_id for candidate_id in preferred_ids if candidate_id}
    if wanted_ids and source_match:
        known_ids = {candidate.get("id") for candidate in candidates if candidate.get("id")}
        if not wanted_ids.issubset(known_ids):
            artifacts = load_c2_artifacts()
            for metadata in artifacts.get("metadata_by_ontology", {}).values():
                for candidate in metadata.get("candidate_models_visible_to_llm") or []:
                    candidate_id = candidate.get("id")
                    if candidate_id in wanted_ids and candidate_id not in known_ids:
                        candidates.append(candidate)
                        known_ids.add(candidate_id)

    previews = _candidate_model_previews(candidates, preferred_ids)
    if previews:
        return previews

    fallback_trait = source_trait or "Cross-trait transfer"
    return [
        {
            "id": item.get("pgs_id"),
            "name": item.get("pgs_id"),
            "trait": fallback_trait,
            "ancestry": "Cross-trait transfer",
            "method": "Transfer recommendation",
            "source": "PGS Catalog",
            "metrics": {},
        }
        for item in frontier[:10]
        if item.get("pgs_id")
    ]


def _build_final_recommendation(
    same_trait_result: dict[str, Any],
    assessment: SameTraitQualityAssessment,
    transfer_result: Optional[dict[str, Any]],
) -> FinalRecommendation:
    if assessment.accept_direct_baseline:
        return FinalRecommendation(
            recommendation_source="same_trait",
            recommended_pgs_id=same_trait_result.get("pgs_id"),
            recommended_trait=same_trait_result.get("resolved_trait"),
            confidence=same_trait_result.get("confidence"),
            summary="Use the selected same-trait PGS baseline; transfer escalation was not needed.",
        )
    if transfer_result and transfer_result.get("status") == "found" and transfer_result.get("pgs_id"):
        return FinalRecommendation(
            recommendation_source="cross_trait_transfer",
            recommended_pgs_id=transfer_result.get("pgs_id"),
            recommended_trait=transfer_result.get("source_trait"),
            confidence=transfer_result.get("confidence"),
            summary="Use the transfer recommendation while retaining the same-trait baseline as the required comparator.",
        )
    if same_trait_result.get("pgs_id"):
        return FinalRecommendation(
            recommendation_source="same_trait",
            recommended_pgs_id=same_trait_result.get("pgs_id"),
            recommended_trait=same_trait_result.get("resolved_trait"),
            confidence=same_trait_result.get("confidence"),
            summary="Transfer evidence was unavailable; keep the weak same-trait baseline visible as the fallback recommendation.",
        )
    return FinalRecommendation(
        recommendation_source="none",
        summary="No same-trait or transfer PGS recommendation could be established from the available evidence.",
    )


def _build_trace(
    target_trait: str,
    same_trait_result: dict[str, Any],
    assessment: SameTraitQualityAssessment,
    transfer_result: Optional[dict[str, Any]],
    final: FinalRecommendation,
) -> list[AgentTraceStep]:
    transfer_found = bool(transfer_result and transfer_result.get("status") == "found")
    transfer_status = "completed" if transfer_found else "skipped"
    transfer_detail = (
        f"Transfer candidate selected from {transfer_result.get('source_trait')}."
        if transfer_found
        else "Same-trait evidence was sufficient, so transfer escalation was skipped."
    )
    if not assessment.accept_direct_baseline and not transfer_found:
        transfer_status = "failed"
        transfer_detail = "Transfer escalation was requested, but no transfer recommendation was available."
    return [
        AgentTraceStep(
            id="target",
            title="Target trait received",
            status="completed",
            detail=f"Target trait: {target_trait}",
        ),
        AgentTraceStep(
            id="same-trait",
            title="Same-trait PGS baseline",
            status="completed" if same_trait_result.get("status") == "found" else "failed",
            detail=(
                f"Selected {same_trait_result.get('pgs_id')} for {same_trait_result.get('resolved_trait')}."
                if same_trait_result.get("pgs_id")
                else "No usable same-trait baseline was selected."
            ),
        ),
        AgentTraceStep(
            id="quality",
            title="Direct-baseline sufficiency decision",
            status="completed",
            detail=assessment.rationale,
        ),
        AgentTraceStep(
            id="transfer",
            title="Conditional transfer escalation",
            status=transfer_status,  # type: ignore[arg-type]
            detail=transfer_detail,
        ),
        AgentTraceStep(
            id="final",
            title="Final recommendation",
            status="completed" if final.recommendation_source != "none" else "failed",
            detail=final.summary,
        ),
    ]


def _run_live_same_trait(
    target_trait: str,
    warnings: list[str],
    errors: list[str],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    artifacts.append({
        "name": "same-trait production wrapper source manifest",
        "path": str(C2_SOURCE_MANIFEST.relative_to(PROJECT_ROOT)),
        "role": "live one-row same-trait input source",
    })
    if not os.getenv("OPENAI_API_KEY"):
        errors.append("Live same-trait runner requires OPENAI_API_KEY.")
        return _unavailable_same_trait(target_trait)

    match = find_c2_artifact(target_trait)
    if match and match.get("request") and match.get("metadata"):
        try:
            return _run_live_c2_one_row(target_trait, match, warnings, artifacts)
        except Exception as exc:
            warnings.append(f"Production same-trait one-row runner failed: {type(exc).__name__}: {exc}")

    warnings.append("No production manifest row matched this target; running direct-only same-trait assessment.")
    try:
        return _run_live_same_trait_direct_only(target_trait)
    except Exception as exc:
        errors.append(f"Live direct-only same-trait fallback failed: {type(exc).__name__}: {exc}")
        return _unavailable_same_trait(target_trait)


def _run_live_same_trait_direct_only(target_trait: str) -> dict[str, Any]:
    from src.server.core.agent_artifacts import stable_json_dumps
    from src.server.core.pgs_catalog_client import PGSCatalogClient
    from src.server.core.tools.prs_model_tools import (
        prs_model_domain_knowledge,
        prs_model_pgscatalog_search,
    )
    from src.server.modules.disease.recommendation_agent import (
        TOP_MODELS_INLINE,
        _build_step1_chain,
        _invoke_step1_chain,
        _summarize_search_result_for_llm,
    )

    pgs_result = prs_model_pgscatalog_search(PGSCatalogClient(), target_trait)
    domain_query = (
        f"target_trait: {target_trait}; PRS clinical thresholds AUC R2 heritability ceiling sanity-check "
        "must-pass gates phenotype alignment endpoint specificity "
        "external transfer reliability ancestry compatibility "
        "ranking features penalties method priors validation sample size tie-break "
        "time-to-event horizon-specific incident case-control dominant subtype "
        "PGS-only no-covariates incremental AUROC "
        "snpnet biobank transportability"
    )
    knowledge = prs_model_domain_knowledge(domain_query)
    step1_context = {
        "target_trait": target_trait,
        "direct_models": pgs_result.model_dump(),
        "direct_models_artifact": None,
        "domain_knowledge": knowledge.model_dump(),
    }
    chain = _build_step1_chain()
    step1_decision, _error = _invoke_step1_chain(
        chain=chain,
        context_payload=step1_context,
        pgs_result=pgs_result,
    )
    pgs_id = step1_decision.best_model_id
    candidate_summaries = [
        _model_to_candidate_summary(model)
        for model in (pgs_result.models or [])[:TOP_MODELS_INLINE]
    ]
    selected = next(
        (candidate for candidate in candidate_summaries if candidate.get("id") == pgs_id),
        None,
    )
    status = "found" if pgs_id else "unavailable"
    return {
        "status": status,
        "execution_mode": "live_direct_only_same_trait",
        "resolved_trait": target_trait,
        "match_score": 1.0 if pgs_id else 0.0,
        "match_kind": "live_direct_only",
        "matched_label": target_trait,
        "recommendation_type": step1_decision.outcome,
        "pgs_id": pgs_id,
        "confidence": step1_decision.confidence,
        "rationale": step1_decision.rationale,
        "models_evaluated": getattr(pgs_result, "after_filter", 0) or len(pgs_result.models or []),
        "candidate_model_ids": [
            getattr(model, "id", None)
            for model in (pgs_result.models or [])
            if getattr(model, "id", None)
        ],
        "shortlist_model_ids": [pgs_id] if pgs_id else [],
        "selected_model_evidence": _selected_evidence_from_candidate(selected),
        "model_preview": format_candidate_model_preview(selected),
        "model_previews": _candidate_model_previews(candidate_summaries, [pgs_id]),
        "_sufficiency_context": {
            "stage1_decision": step1_decision.model_dump(),
            "stage2_decision": {},
            "candidate_summaries": candidate_summaries,
            "domain_knowledge": knowledge.model_dump(),
            "direct_models_summary": _summarize_search_result_for_llm(pgs_result),
            "context_json": stable_json_dumps(step1_context),
        },
    }


def _model_to_candidate_summary(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return dict(model)


def _selected_evidence_from_candidate(candidate: Optional[dict[str, Any]]) -> dict[str, Any]:
    if not candidate:
        return {}
    return {
        "trait_reported": candidate.get("trait_reported"),
        "trait_efo": candidate.get("trait_efo"),
        "method": candidate.get("method_name"),
        "ancestry_distribution": candidate.get("ancestry_distribution"),
        "samples_training": candidate.get("samples_training"),
        "validation_sample_size": candidate.get("validation_sample_size"),
        "performance_metrics": candidate.get("performance_metrics") or {},
    }


def _run_live_c2_one_row(
    target_trait: str,
    match: dict[str, Any],
    warnings: list[str],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    artifacts_data = load_c2_artifacts()
    metadata = match["metadata"]
    ontology = metadata.get("ontology")
    reused_run = _latest_completed_live_same_trait_run(target_trait)
    if reused_run is not None:
        warnings.append(f"Reused completed live same-trait run: {_display_path(reused_run)}")
        artifacts.append({
            "name": "same-trait live output",
            "path": str(reused_run.relative_to(PROJECT_ROOT)),
            "role": "reused live same-trait runner output",
        })
        return _same_trait_result_from_live_run(
            target_trait=target_trait,
            match=match,
            metadata=metadata,
            ontology=ontology,
            run_dir=reused_run,
            execution_mode="live_one_row_production_runner_reused",
        )

    request = match["request"]
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    run_dir = LIVE_RUNS_DIR / f"same-trait-{slugify(target_trait)}-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    one_row_manifest = dict(artifacts_data["manifest"])
    one_row_manifest["requests"] = [request]
    one_row_manifest["disease_metadata"] = [metadata]
    one_row_manifest["total_ontologies"] = 1
    one_row_manifest["total_requests"] = 1
    manifest_path = run_dir / "one_row_manifest.json"
    manifest_path.write_text(json.dumps(one_row_manifest, indent=2), encoding="utf-8")
    artifacts.append({
        "name": "same-trait live one-row manifest",
        "path": str(manifest_path.relative_to(PROJECT_ROOT)),
        "role": "live same-trait runner input",
    })

    from experiments.contribution2.recommendation.scripts.run_experiment_pairwise_rerank import _run_pipeline

    _run_pipeline(
        manifest_path=manifest_path,
        output_run_dir=run_dir,
        model=os.getenv("OPENAI_MODEL") or "gpt-5.2",
        workers=1,
        top_k=None,
        evaluator="topk_judge",
        objective="support",
        stage1_objective="support",
    )
    artifacts.append({
        "name": "same-trait live output",
        "path": str(run_dir.relative_to(PROJECT_ROOT)),
        "role": "live same-trait runner output",
    })
    return _same_trait_result_from_live_run(
        target_trait=target_trait,
        match=match,
        metadata=metadata,
        ontology=ontology,
        run_dir=run_dir,
        execution_mode="live_one_row_production_runner",
    )


def _latest_completed_live_same_trait_run(target_trait: str) -> Optional[Path]:
    slug = slugify(target_trait)
    required = (
        "experiment_pairwise_rerank_results.json",
        "experiment_pairwise_rerank_summary.json",
        "experiment_pairwise_rerank_stage1_results.json",
        "experiment_pairwise_rerank_stage2_results.json",
    )
    candidates = sorted(
        LIVE_RUNS_DIR.glob(f"same-trait-{slug}-*"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for run_dir in candidates:
        if not all((run_dir / filename).exists() for filename in required):
            continue
        try:
            summary = json.loads((run_dir / "experiment_pairwise_rerank_summary.json").read_text(encoding="utf-8"))
        except Exception:
            continue
        rerank = summary.get("pairwise_rerank") or {}
        if (
            rerank.get("execution_architecture") == "two_stage_rerank"
            and rerank.get("evaluator") == "topk_judge"
            and rerank.get("candidate_range") == "evidence_determined"
        ):
            return run_dir
    return None


def _same_trait_result_from_live_run(
    *,
    target_trait: str,
    match: dict[str, Any],
    metadata: dict[str, Any],
    ontology: Optional[str],
    run_dir: Path,
    execution_mode: str,
) -> dict[str, Any]:
    live_result = json.loads((run_dir / "experiment_pairwise_rerank_results.json").read_text(encoding="utf-8"))[0]
    stage1_path = run_dir / "experiment_pairwise_rerank_stage1_results.json"
    live_stage1 = (
        json.loads(stage1_path.read_text(encoding="utf-8"))[0]
        if stage1_path.exists()
        else {}
    )
    fullpool_path = run_dir / "experiment_pairwise_rerank_fullpool_results.json"
    selector_path = fullpool_path if fullpool_path.exists() else run_dir / "experiment_pairwise_rerank_stage2_results.json"
    selector_rows = json.loads(selector_path.read_text(encoding="utf-8"))
    live_selector = next((row for row in selector_rows if row.get("ontology") == ontology), {})
    return _same_trait_result_from_artifact(
        target_trait=target_trait,
        match={
            "score": match.get("score"),
            "result": live_result,
            "stage1": live_stage1,
            "stage2": live_selector,
            "metadata": metadata,
            "match_kind": match.get("match_kind"),
            "matched_label": match.get("matched_label"),
        },
        execution_mode=execution_mode,
    )


def _run_live_transfer(
    target_trait: str,
    warnings: list[str],
    errors: list[str],
    artifacts: list[dict[str, Any]],
) -> Optional[dict[str, Any]]:
    if not os.getenv("OPENAI_API_KEY"):
        errors.append("Live transfer runner requires OPENAI_API_KEY.")
        return None
    try:
        artifacts.append({
            "name": "transfer retained candidate dossiers",
            "path": str(C3_DOSSIER_PATH.relative_to(PROJECT_ROOT)),
            "role": "live transfer target dossier source",
        })
        dossier_data = find_c3_dossier(target_trait)
        if not dossier_data:
            warnings.append(
                "No retained cross-trait dossier matched this target; live transfer was not run. "
                "Prepare a single-target Contribution 3 dossier before rerunning live transfer."
            )
            return None

        from experiments.contribution3.transfer.common import CandidateBundleDossier
        from experiments.contribution3.transfer.driver import run_cross_trait_agent, write_agent_results

        dossier = CandidateBundleDossier.model_validate(dossier_data)
        result = run_cross_trait_agent(
            dossier,
            condition="all-tools",
            benchmark_family="unified",
            ablation=DEFAULT_TRANSFER_ABLATION,
        )
        stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        run_dir = LIVE_RUNS_DIR / f"transfer-{slugify(target_trait)}-{stamp}"
        outpath = run_dir / "results.json"
        write_agent_results([result], outpath)
        artifacts.append({
            "name": "transfer live output",
            "path": str(outpath.relative_to(PROJECT_ROOT)),
            "role": "live transfer runner output",
        })
        return _transfer_result_from_artifact(result, execution_mode="live_single_trait")
    except Exception as exc:
        errors.append(f"Live transfer runner failed: {type(exc).__name__}: {exc}")
        return None
