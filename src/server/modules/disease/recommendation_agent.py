import os
import re
import logging
from typing import Any, Dict, List, Optional, Literal, Callable, Tuple, Set

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from src.server.core.llm_config import get_llm
from src.server.core.system_prompts import (
    CO_SCIENTIST_STEP1_PROMPT,
    CO_SCIENTIST_STEP1_NATIVE_PROMPT,
    CO_SCIENTIST_REPORT_PROMPT
)
from src.server.core.pgs_catalog_client import PGSCatalogClient
from src.server.core.opentargets_client import OpenTargetsClient
from src.server.core.phewas_client import PheWASClient
from src.server.modules.knowledge_graph.service import KnowledgeGraphService
from src.server.core.tool_schemas import (
    ToolError,
    NeighborResult,
    MechanismValidation,
    DomainKnowledgeResult,
    PGSSearchResult,
)
from thefuzz import fuzz
from uuid import uuid4

from src.server.core.agent_artifacts import maybe_externalize_json, stable_json_dumps
from src.server.core.recitation_todo import RecitationTodo
from src.server.core.agent_artifacts import get_artifacts_dir
from src.server.core.state import search_progress
from src.server.core.tools.prs_model_tools import (
    prs_model_pgscatalog_search,
    prs_model_performance_landscape,
    prs_model_domain_knowledge
)
from src.server.core.tools.genetic_graph_tools import (
    genetic_graph_get_neighbors,
    genetic_graph_validate_mechanism,
    genetic_graph_verify_study_power
)
# NOTE: According to Single Agent Principle, tool calls should ideally be decided by the LLM Agent
# via system prompts. The Agent is guided via system prompts to use trait_synonym_expand at the start
# to expand trait queries for comprehensive coverage across all tools.
from src.server.core.tools.trait_tools import trait_synonym_expand
from src.server.modules.disease.models import (
    RecommendationReport,
    FollowUpOption,
    GeneticGraphEvidence,
    StudyPowerSummary,
    PrimaryRecommendation,
    DirectMatchEvidence
)
from src.server.modules.disease.local_graph_reranker import (
    rerank_neighbors_with_local_graph,
    select_neighbors_from_local_graph,
)


class Step1Decision(BaseModel):
    outcome: Literal["DIRECT_HIGH_QUALITY", "DIRECT_SUB_OPTIMAL", "NO_MATCH_FOUND"]
    best_model_id: Optional[str] = None
    confidence: Literal["High", "Moderate", "Low"]
    rationale: str


class EfoCandidate(BaseModel):
    id: str
    label: str
    score: float
    source: Literal["pgs_trait", "pgs_score", "ot"]


EFO_GAP_THRESHOLD = 0.08
MAX_EFO_VALIDATION = 2
MAX_PGS_EFO_MODELS = 3
MAX_OT_HITS = 8
OT_SCORE_WEIGHT = 0.6
SIMILARITY_WEIGHT = 0.4
CONSENSUS_BONUS = 0.12
NON_EFO_ID_PENALTY = 0.05

# Context engineering thresholds (Manus: Use the File System as Context)
MAX_INLINE_CONTEXT_BYTES = 50_000
TOP_MODELS_INLINE = 10
MAX_STUDY_POWER_CHECKS = 2

STEP1_DISABLE_DOMAIN_ENV = "PENNPRS_STEP1_DISABLE_DOMAIN_KNOWLEDGE"
STEP1_RUN_ABLATION_ENV = "PENNPRS_STEP1_RUN_NO_DOMAIN_ABLATION"
LOCAL_GRAPH_NEIGHBOR_LIMIT_ENV = "PENNPRS_LOCAL_GRAPH_KG_NEIGHBOR_LIMIT"
LOCAL_GRAPH_PREFILTER_ENV = "PENNPRS_LOCAL_GRAPH_PREFILTER_TOP_K"
LOCAL_GRAPH_PROCESS_TOP_N_ENV = "PENNPRS_LOCAL_GRAPH_PROCESS_TOP_N"
LOCAL_GRAPH_MIN_PGS_HITS_ENV = "PENNPRS_LOCAL_GRAPH_MIN_PGS_HITS"
LOCAL_GRAPH_WEIGHT_TRANSFER_ENV = "PENNPRS_LOCAL_GRAPH_WEIGHT_TRANSFER"
LOCAL_GRAPH_WEIGHT_RG_ENV = "PENNPRS_LOCAL_GRAPH_WEIGHT_RG"
LOCAL_GRAPH_WEIGHT_POWER_ENV = "PENNPRS_LOCAL_GRAPH_WEIGHT_POWER"
LOCAL_GRAPH_WEIGHT_PGS_ENV = "PENNPRS_LOCAL_GRAPH_WEIGHT_PGS_HITS"
LOCAL_GRAPH_WEIGHT_SEMANTIC_ENV = "PENNPRS_LOCAL_GRAPH_WEIGHT_SEMANTIC"
# When set, path to evaluated_pgs_per_ontology.json; restricts Step 1 models to N Models (All of Us evaluated set)
CONTRIB2_EVALUATED_PGS_JSON_ENV = "PENNPRS_CONTRIB2_EVALUATED_PGS_JSON"
CONTRIB2_STRICT_LLM_ONLY_ENV = "PENNPRS_CONTRIB2_STRICT_LLM_ONLY"

STEP1_RATIONALE_FEATURE_KEYWORDS = {
    "trait_match": ["trait", "phenotype", "proxy", "family history"],
    "auc": ["auc", "auroc", "roc"],
    "r2": ["r2", "r²", "variance explained"],
    "sample_size": ["sample", "n=", "cohort", "powered"],
    "ancestry": ["ancestry", "eur", "afr", "eas", "sas", "multi-ancestry"],
    "method": ["method", "ldpred", "prs-cs", "lassosum", "genoboost", "snpnet"],
    "variants": ["variant", "snp"],
    "covariates": ["covariate", "age", "sex", "pc"],
}


TRAIN_NEW_MODEL_OPTION = FollowUpOption(
    label="Train New Model on PennPRS",
    action="TRIGGER_PENNPRS_CONFIG",
    context="Provides best-in-class configuration recommendation"
)


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int, min_value: int, max_value: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(min_value, min(max_value, value))


def _env_float(name: str, default: float, min_value: float, max_value: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return max(min_value, min(max_value, value))


# Cached evaluated PGS whitelist (Contribution2: ontology -> set of PGS IDs)
_contrib2_evaluated_pgs_cache: Optional[Dict[str, List[str]]] = None


def _get_evaluated_pgs_whitelist_for_trait(target_trait: str) -> Optional[Set[str]]:
    """
    Return set of evaluated PGS IDs for the given trait when Contribution2 filter is enabled.
    Returns None if env not set or trait not found.
    """
    path = os.getenv(CONTRIB2_EVALUATED_PGS_JSON_ENV)
    if not path or not path.strip():
        return None
    global _contrib2_evaluated_pgs_cache
    if _contrib2_evaluated_pgs_cache is None:
        try:
            with open(path.strip(), encoding="utf-8") as f:
                import json
                data = json.load(f)
            _contrib2_evaluated_pgs_cache = dict(data) if isinstance(data, dict) else {}
        except Exception as e:
            logger.warning("Failed to load Contribution2 evaluated PGS whitelist: %s", e)
            _contrib2_evaluated_pgs_cache = {}
    key = (target_trait or "").strip().lower()
    pgs_list = _contrib2_evaluated_pgs_cache.get(key)
    if pgs_list is None:
        return None
    return set(pgs_list)


def _normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    stopwords = {"disease", "syndrome", "disorder", "trait", "of", "and"}
    tokens = [t for t in cleaned.split() if t not in stopwords]
    return " ".join(tokens)


def _similarity_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return fuzz.token_set_ratio(_normalize_text(a), _normalize_text(b)) / 100.0


def _slugify(text: str, max_len: int = 40) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    if not normalized:
        return "unknown"
    return normalized[:max_len]


def _summarize_model_for_llm(model: Any) -> Dict[str, Any]:
    # PGSModelSummary is a Pydantic model; keep only high-signal [Agent + UI] fields.
    publication = getattr(model, "publication", None)
    if hasattr(publication, "model_dump"):
        publication = publication.model_dump()
    return {
        "id": getattr(model, "id", None),
        "trait_reported": getattr(model, "trait_reported", None),
        "trait_efo": getattr(model, "trait_efo", None),
        "method_name": getattr(model, "method_name", None),
        "variants_number": getattr(model, "variants_number", None),
        "ancestry_distribution": getattr(model, "ancestry_distribution", None),
        "publication": publication,
        "date_release": getattr(model, "date_release", None),
        "samples_training": getattr(model, "samples_training", None),
        "performance_metrics": getattr(model, "performance_metrics", None),
        "phenotyping_reported": getattr(model, "phenotyping_reported", None),
        "covariates": getattr(model, "covariates", None),
        "training_development_cohorts": getattr(model, "training_development_cohorts", None),
        "validation_sample_size": getattr(model, "validation_sample_size", None),
    }


def _summarize_search_result_for_llm(search_result: Any, top_n: int = TOP_MODELS_INLINE) -> Dict[str, Any]:
    models = getattr(search_result, "models", []) or []
    return {
        "query_trait": getattr(search_result, "query_trait", None),
        "total_found": getattr(search_result, "total_found", None),
        "after_filter": getattr(search_result, "after_filter", None),
        "top_models": [_summarize_model_for_llm(m) for m in models[:top_n]],
    }


def _build_step1_feature_table(models: List[Any], top_n: int = TOP_MODELS_INLINE) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for m in (models or [])[:top_n]:
        pm = getattr(m, "performance_metrics", {}) or {}
        rows.append({
            "id": getattr(m, "id", None),
            "trait_reported": getattr(m, "trait_reported", None),
            "method_name": getattr(m, "method_name", None),
            "auc": pm.get("auc"),
            "r2": pm.get("r2"),
            "samples_training": getattr(m, "samples_training", None),
            "validation_sample_size": getattr(m, "validation_sample_size", None),
            "ancestry_distribution": getattr(m, "ancestry_distribution", None),
            "variants_number": getattr(m, "variants_number", None),
            "phenotyping_reported": getattr(m, "phenotyping_reported", None),
            "covariates": getattr(m, "covariates", None),
            "training_development_cohorts": getattr(m, "training_development_cohorts", None),
        })
    return rows


def _empty_domain_knowledge(query: str, source_type: str = "disabled") -> DomainKnowledgeResult:
    return DomainKnowledgeResult(query=query, snippets=[], source_type=source_type)


def _extract_step1_rationale_features(rationale: str) -> List[str]:
    text = (rationale or "").lower()
    features: List[str] = []
    for feature, keywords in STEP1_RATIONALE_FEATURE_KEYWORDS.items():
        if any(k in text for k in keywords):
            features.append(feature)
    return features


def _write_json_artifact(prefix: str, payload: Dict[str, Any]) -> Optional[str]:
    try:
        path = get_artifacts_dir() / f"{prefix}_{uuid4().hex[:12]}.json"
        path.write_text(stable_json_dumps(payload), encoding="utf-8")
        return str(path)
    except Exception as exc:
        logger.warning(
            f"Failed to persist artifact '{prefix}': {type(exc).__name__}: {exc}"
        )
        return None


def _fallback_step1_decision(
    pgs_result: PGSSearchResult,
    error_message: str
) -> Step1Decision:
    return Step1Decision(
        outcome="NO_MATCH_FOUND" if pgs_result.after_filter == 0 else "DIRECT_SUB_OPTIMAL",
        best_model_id=pgs_result.models[0].id if pgs_result.models else None,
        confidence="Low",
        rationale=f"Fallback decision due to Step 1 failure: {error_message}"
    )


def _invoke_step1_chain(
    chain: Any,
    context_payload: Dict[str, Any],
    pgs_result: PGSSearchResult
) -> Tuple[Step1Decision, Optional[Dict[str, Any]]]:
    try:
        decision = chain.invoke({"context_json": stable_json_dumps(context_payload)})
        return decision, None
    except Exception as exc:
        decision = _fallback_step1_decision(pgs_result, str(exc))
        err = {
            "tool_name": "step1_decision",
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        }
        return decision, err


def _best_model_stats(models: List[Any]) -> Dict[str, Any]:
    best_id = None
    best_auc = None
    for m in models or []:
        pm = getattr(m, "performance_metrics", {}) or {}
        auc = pm.get("auc")
        if auc is None:
            continue
        try:
            auc_val = float(auc)
        except Exception:
            continue
        if best_auc is None or auc_val > best_auc:
            best_auc = auc_val
            best_id = getattr(m, "id", None)
    return {"best_model_id": best_id, "best_model_auc": best_auc}


def _is_valid_disease_id(disease_id: str) -> bool:
    if not disease_id:
        return False
    return bool(re.match(r"^(EFO|MONDO)_\d+$", str(disease_id).strip()))


def _extract_pgs_trait_search_candidates(
    trait_name: str,
    pgs_client: Optional[PGSCatalogClient]
) -> List[EfoCandidate]:
    if not pgs_client:
        return []

    raw_traits = pgs_client.search_traits(trait_name)
    candidates: List[EfoCandidate] = []
    for t in raw_traits or []:
        efo_id = t.get("id") or ""
        label = t.get("label") or t.get("trait") or t.get("name") or ""
        if not _is_valid_disease_id(efo_id):
            continue
        score = _similarity_score(trait_name, label) if label else 0.0
        candidates.append(EfoCandidate(
            id=str(efo_id),
            label=str(label),
            score=score,
            source="pgs_trait"
        ))
    return candidates


def _extract_pgs_efo_candidates(
    trait_name: str,
    pgs_models: Optional[List[Any]],
    pgs_client: Optional[PGSCatalogClient]
) -> List[EfoCandidate]:
    if not pgs_models or not pgs_client:
        return []

    candidates: List[EfoCandidate] = []
    for model in pgs_models[:MAX_PGS_EFO_MODELS]:
        model_id = getattr(model, "id", None) or (model.get("id") if isinstance(model, dict) else None)
        if not model_id:
            continue
        details = pgs_client.get_score_details(model_id)
        for trait in details.get("trait_efo", []) or []:
            efo_id = trait.get("id")
            label = trait.get("label") or ""
            if efo_id:
                score = _similarity_score(trait_name, label)
                candidates.append(EfoCandidate(
                    id=efo_id,
                    label=label,
                    score=score,
                    source="pgs_score"
                ))
    return candidates


def _extract_ot_efo_candidates(
    trait_name: str,
    ot_client: OpenTargetsClient
) -> List[EfoCandidate]:
    try:
        results = ot_client.search_diseases(trait_name, page=0, size=MAX_OT_HITS)
    except Exception as exc:
        # Open Targets is an external dependency and can intermittently fail.
        # This workflow should degrade gracefully and continue using PGS-derived candidates.
        logger.warning(
            "Open Targets disease search failed; skipping OT candidates. "
            f"trait='{trait_name}', error_type={type(exc).__name__}, error='{exc}'"
        )
        return []
    hits = results.get("hits", []) if isinstance(results, dict) else []
    candidates: List[EfoCandidate] = []
    if not hits:
        return candidates

    for hit in hits:
        if isinstance(hit, dict):
            efo_id = hit.get("id")
            label = hit.get("name") or hit.get("label") or ""
            ot_score = float(hit.get("score") or 0.0)
        else:
            efo_id = getattr(hit, "id", None)
            label = getattr(hit, "name", "") or ""
            ot_score = float(getattr(hit, "score", 0.0) or 0.0)

        if not efo_id:
            continue

        if not _is_valid_disease_id(str(efo_id)):
            continue

        sim_score = _similarity_score(trait_name, label)
        combined = (OT_SCORE_WEIGHT * ot_score) + (SIMILARITY_WEIGHT * sim_score)
        candidates.append(EfoCandidate(
            id=str(efo_id),
            label=label,
            score=combined,
            source="ot"
        ))

    return candidates


def resolve_efo_candidates(
    trait_name: str,
    ot_client: OpenTargetsClient,
    pgs_client: Optional[PGSCatalogClient] = None,
    pgs_models: Optional[List[Any]] = None
) -> List[EfoCandidate]:
    trait_candidates = _extract_pgs_trait_search_candidates(trait_name, pgs_client)
    score_candidates = _extract_pgs_efo_candidates(trait_name, pgs_models, pgs_client)
    pgs_candidates = trait_candidates + score_candidates

    # Only query Open Targets when PGS sources are missing or ambiguous.
    ot_candidates: List[EfoCandidate] = []
    if not pgs_candidates:
        ot_candidates = _extract_ot_efo_candidates(trait_name, ot_client)
    else:
        ordered_pgs = sorted(pgs_candidates, key=lambda c: c.score, reverse=True)
        if len(ordered_pgs) > 1:
            score_gap = ordered_pgs[0].score - ordered_pgs[1].score
            if score_gap < EFO_GAP_THRESHOLD:
                ot_candidates = _extract_ot_efo_candidates(trait_name, ot_client)

    merged = pgs_candidates + ot_candidates
    if not merged:
        return []

    # Aggregate by ID to promote multi-source consensus and reduce ambiguity.
    by_id: Dict[str, Dict[str, Any]] = {}
    for c in merged:
        if not _is_valid_disease_id(c.id):
            continue
        entry = by_id.get(c.id)
        if not entry:
            by_id[c.id] = {
                "id": c.id,
                "label": c.label or "",
                "best_score": float(c.score),
                "best_source": c.source,
                "sources": {c.source},
            }
        else:
            entry["sources"].add(c.source)
            if float(c.score) > float(entry["best_score"]):
                entry["best_score"] = float(c.score)
                entry["best_source"] = c.source
            if not entry["label"] and c.label:
                entry["label"] = c.label

    aggregated: List[EfoCandidate] = []
    for efo_id, entry in by_id.items():
        sources = entry["sources"]
        consensus_bonus = CONSENSUS_BONUS * max(0, len(sources) - 1)
        score = float(entry["best_score"]) + consensus_bonus
        if not str(efo_id).startswith("EFO_"):
            score = max(0.0, score - NON_EFO_ID_PENALTY)
        aggregated.append(EfoCandidate(
            id=efo_id,
            label=entry["label"],
            score=score,
            source=entry["best_source"]
        ))

    return sorted(aggregated, key=lambda c: c.score, reverse=True)


def resolve_efo_id(
    trait_name: str,
    ot_client: OpenTargetsClient,
    pgs_client: Optional[PGSCatalogClient] = None,
    pgs_models: Optional[List[Any]] = None
) -> Optional[str]:
    candidates = resolve_efo_candidates(
        trait_name=trait_name,
        ot_client=ot_client,
        pgs_client=pgs_client,
        pgs_models=pgs_models
    )
    return candidates[0].id if candidates else None


def resolve_efo_and_mondo_ids(
    trait_name: str,
    ot_client: OpenTargetsClient,
    pgs_client: Optional[PGSCatalogClient] = None,
    pgs_models: Optional[List[Any]] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Resolve both EFO and MONDO IDs for a trait.
    
    Returns:
        Tuple of (efo_id, mondo_id). Either or both may be None.
    """
    candidates = resolve_efo_candidates(
        trait_name=trait_name,
        ot_client=ot_client,
        pgs_client=pgs_client,
        pgs_models=pgs_models
    )
    
    efo_id = None
    mondo_id = None
    
    for candidate in candidates:
        if candidate.id.startswith("EFO_") and efo_id is None:
            efo_id = candidate.id
        elif candidate.id.startswith("MONDO_") and mondo_id is None:
            mondo_id = candidate.id
        
        # Stop if we have both
        if efo_id and mondo_id:
            break
    
    return (efo_id, mondo_id)


def select_best_efo_candidate(
    target_trait_name: str,
    target_efo_id: Optional[str],
    neighbor_trait_name: str,
    candidates: List[EfoCandidate],
    target_mondo_id: Optional[str] = None,
    validate_fn: Optional[Callable[[str, str], Any]] = None,
    gap_threshold: float = EFO_GAP_THRESHOLD,
    max_validate: int = MAX_EFO_VALIDATION
) -> Tuple[Optional[EfoCandidate], Optional[MechanismValidation]]:
    """
    Select best EFO candidate for neighbor trait using mechanism validation.
    
    Args:
        target_trait_name: Target trait name
        target_efo_id: Target trait EFO ID
        target_mondo_id: Target trait MONDO ID
        neighbor_trait_name: Neighbor trait name
        candidates: List of EFO candidates for neighbor trait
        validate_fn: Function that takes (source_trait, target_trait) and returns MechanismValidation
        gap_threshold: Score gap threshold for skipping validation
        max_validate: Maximum number of candidates to validate
        
    Returns:
        Tuple of (best_candidate, best_mechanism)
    """
    if not candidates:
        return None, None

    ordered = sorted(candidates, key=lambda c: c.score, reverse=True)
    if len(ordered) == 1 or not validate_fn or (not target_efo_id and not target_mondo_id):
        return ordered[0], None

    score_gap = ordered[0].score - ordered[1].score
    if score_gap >= gap_threshold:
        return ordered[0], None

    best_candidate = ordered[0]
    best_mechanism = None
    best_rank = (-1, -1, -1)

    for candidate in ordered[:max_validate]:
        try:
            result = validate_fn(
                candidate.id,
                candidate.id,
                neighbor_trait_name,
                target_trait_name
            )
        except TypeError:
            # Backward compatibility for older validate_fn signature.
            result = validate_fn(neighbor_trait_name, target_trait_name)
        if isinstance(result, ToolError):
            continue
        rank = _mechanism_rank(result)
        if rank > best_rank:
            best_rank = rank
            best_candidate = candidate
            best_mechanism = result

    return best_candidate, best_mechanism


def _mechanism_rank(mechanism: MechanismValidation) -> Tuple[int, int, int]:
    confidence_rank = {"High": 3, "Moderate": 2, "Low": 1}
    confidence = confidence_rank.get(mechanism.confidence_level, 0)
    shared_genes = len(mechanism.shared_genes)
    phewas_hits = mechanism.phewas_evidence_count
    return (confidence, shared_genes, phewas_hits)


def ensure_follow_up_options(report: RecommendationReport) -> RecommendationReport:
    actions = {opt.action for opt in report.follow_up_options}
    if TRAIN_NEW_MODEL_OPTION.action not in actions:
        report.follow_up_options.append(TRAIN_NEW_MODEL_OPTION)
    return report


def _ensure_list_fields_not_none(report: RecommendationReport) -> RecommendationReport:
    """
    Ensure all list fields in the report are not None.
    LLM may return None for optional list fields, which causes Pydantic validation errors.
    """
    updates = {}
    if report.genetic_graph_evidence is None:
        updates["genetic_graph_evidence"] = []
    if report.genetic_graph_neighbors is None:
        updates["genetic_graph_neighbors"] = []
    if report.genetic_graph_errors is None:
        updates["genetic_graph_errors"] = []
    if report.alternative_recommendations is None:
        updates["alternative_recommendations"] = []
    if report.caveats_and_limitations is None:
        updates["caveats_and_limitations"] = []
    if report.follow_up_options is None:
        updates["follow_up_options"] = []
    
    if updates:
        return report.model_copy(update=updates)
    return report


def _build_step1_chain(use_native_prompt: bool = False):
    llm = get_llm("disease_workflow")
    system_prompt = CO_SCIENTIST_STEP1_NATIVE_PROMPT if use_native_prompt else CO_SCIENTIST_STEP1_PROMPT
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", (
            "Perform STEP 1 only. Use the context JSON below to decide whether the direct "
            "match quality is HIGH, SUB_OPTIMAL, or NO_MATCH_FOUND. "
            "Return JSON with fields: outcome, best_model_id, confidence, rationale.\n\n"
            "Context:\n{context_json}"
        ))
    ])
    structured_llm = llm.with_structured_output(
        Step1Decision,
        method="json_schema",
        strict=True
    )
    return prompt | structured_llm


def _build_report_chain():
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages([
        ("system", CO_SCIENTIST_REPORT_PROMPT),
        ("human", (
            "Generate the final recommendation report using the context JSON. "
            "Return JSON only.\n\nContext:\n{context_json}"
        ))
    ])
    structured_llm = llm.with_structured_output(
        RecommendationReport,
        # RecommendationReport is a complex nested schema; `json_schema` strict mode
        # can be rejected by some OpenAI models. Use function calling for robustness.
        method="function_calling"
    )
    return prompt | structured_llm


def recommend_models(
    target_trait: str,
    force_step1_outcome: Optional[Literal["DIRECT_HIGH_QUALITY", "DIRECT_SUB_OPTIMAL", "NO_MATCH_FOUND"]] = None,
    request_id: Optional[str] = None
) -> RecommendationReport:
    pgs_client = PGSCatalogClient()
    # Important: defer heavy initializations until needed.
    # KnowledgeGraphService loads large correlation tables and can take minutes on first load.
    # If we initialize it before STEP 1, the frontend can look "stuck" at "Initializing...".
    ot_client: Optional[OpenTargetsClient] = None
    phewas_client: Optional[PheWASClient] = None
    kg_service: Optional[KnowledgeGraphService] = None

    tool_errors: List[Dict[str, Any]] = []
    step1_disable_domain_knowledge = _env_flag(STEP1_DISABLE_DOMAIN_ENV, default=False)
    step1_run_ablation = _env_flag(STEP1_RUN_ABLATION_ENV, default=False)
    strict_llm_only = _env_flag(CONTRIB2_STRICT_LLM_ONLY_ENV, default=False)

    local_graph_neighbor_limit = _env_int(
        LOCAL_GRAPH_NEIGHBOR_LIMIT_ENV, default=50, min_value=10, max_value=200
    )
    local_graph_prefilter_top_k = _env_int(
        LOCAL_GRAPH_PREFILTER_ENV, default=50, min_value=1, max_value=200
    )
    local_graph_process_top_n = _env_int(
        LOCAL_GRAPH_PROCESS_TOP_N_ENV, default=3, min_value=1, max_value=20
    )
    local_graph_min_pgs_hits = _env_int(
        LOCAL_GRAPH_MIN_PGS_HITS_ENV, default=1, min_value=0, max_value=1000
    )
    local_graph_weights = {
        "graph_transfer": _env_float(LOCAL_GRAPH_WEIGHT_TRANSFER_ENV, 0.45, 0.0, 1.0),
        "graph_rg": _env_float(LOCAL_GRAPH_WEIGHT_RG_ENV, 0.15, 0.0, 1.0),
        "graph_power": _env_float(LOCAL_GRAPH_WEIGHT_POWER_ENV, 0.10, 0.0, 1.0),
        "pgs_hits": _env_float(LOCAL_GRAPH_WEIGHT_PGS_ENV, 0.20, 0.0, 1.0),
        "semantic_similarity": _env_float(LOCAL_GRAPH_WEIGHT_SEMANTIC_ENV, 0.10, 0.0, 1.0),
    }

    # ---------------------------------------------------------------------
    # Recitation todo (Manus: Manipulate Attention Through Recitation)
    # ---------------------------------------------------------------------
    todo_path = get_artifacts_dir() / f"todo_{uuid4().hex[:12]}.md"
    todo = RecitationTodo(
        path=todo_path,
        title="Current Task Progress",
        items=[
            ("Step 1: Query PGS Catalog for target trait", False),
            ("Step 1: Evaluate models against performance landscape", False),
            ("Step 2a: Query Knowledge Graph for related traits", False),
            ("Step 2a: Validate biological mechanism", False),
            ("Step 2a: Evaluate related-trait models", False),
            ("On-Demand: Offer 'Train New Model' option in final report", False),
        ]
    )
    todo.write()

    # Update progress: Step 1 started
    # Note: Don't override total/fetched here - prs_model_tools.py will set them correctly
    if request_id and request_id in search_progress:
            search_progress[request_id].update({
                "current_action": f"Searching PRS models for '{target_trait}'",
                "current_step": "step-1"
            })

    # Step 1: Direct match assessment
    # NOTE: According to Single Agent Principle, tool calls should be decided by the LLM Agent via system prompts.
    # However, this orchestrator provides a deterministic workflow for performance.
    # The Agent is guided via system prompts to call prs_model_pgscatalog_search directly with target_trait.
    # No synonym expansion needed for PGS Catalog search - it handles trait name matching internally.
    # When PENNPRS_CONTRIB2_EVALUATED_PGS_JSON is set, restrict to N Models (All of Us evaluated set).
    evaluated_whitelist = _get_evaluated_pgs_whitelist_for_trait(target_trait)
    pgs_result = prs_model_pgscatalog_search(
        pgs_client,
        target_trait,
        request_id=request_id,
        evaluated_pgs_whitelist=evaluated_whitelist,
    )
    
    todo.set_done("Step 1: Query PGS Catalog for target trait")
    todo.write()

    # Update progress: Step 2 started
    if request_id and request_id in search_progress:
        search_progress[request_id].update({
            "fetched": 2,
            "current_action": "Analyzing performance metrics",
            "current_step": "step-2"
        })

    domain_query = (
        f"target_trait: {target_trait}; PRS clinical thresholds AUC R2 "
        "must-pass gates phenotype alignment endpoint specificity "
        "external transfer reliability ancestry compatibility "
        "ranking features penalties method priors validation sample size tie-break "
        "time-to-event horizon-specific incident case-control dominant subtype "
        "snpnet biobank transportability"
    )
    knowledge_with_domain: Optional[DomainKnowledgeResult] = None
    if (not step1_disable_domain_knowledge) or step1_run_ablation:
        knowledge_with_domain = prs_model_domain_knowledge(domain_query)

    if step1_disable_domain_knowledge:
        knowledge = _empty_domain_knowledge(domain_query, source_type="disabled_by_ablation")
    else:
        knowledge = knowledge_with_domain or _empty_domain_knowledge(
            domain_query,
            source_type="missing"
        )

    landscape = prs_model_performance_landscape(pgs_client, pgs_result.models)
    todo.set_done("Step 1: Evaluate models against performance landscape")
    todo.write()

    # Update progress: Step 3 started
    if request_id and request_id in search_progress:
        search_progress[request_id].update({
            "fetched": 3,
            "current_action": "Reviewing clinical standards",
            "current_step": "step-3"
        })

    direct_models_dump = pgs_result.model_dump()
    direct_models_inline, direct_models_artifact = maybe_externalize_json(
        payload=direct_models_dump,
        artifact_prefix=f"direct_models_{_slugify(target_trait)}",
        max_inline_bytes=MAX_INLINE_CONTEXT_BYTES,
        max_inline_tokens=2_000,
        summary_builder=lambda _: _summarize_search_result_for_llm(pgs_result, top_n=TOP_MODELS_INLINE)
    )

    step1_context = {
        "target_trait": target_trait,
        "direct_models": direct_models_inline,
        "direct_models_artifact": direct_models_artifact.model_dump() if direct_models_artifact else None,
        "performance_landscape": landscape.model_dump(),
        "domain_knowledge": knowledge.model_dump(),
        "todo_recitation_path": str(todo_path),
        "todo_recitation": todo.render()
    }

    step1_decision = None
    step1_shadow_decision: Optional[Step1Decision] = None
    step1_ablation_summary: Optional[Dict[str, Any]] = None
    step1_ablation_artifact_path: Optional[str] = None

    # Test mode: Force Step 1 outcome (for testing Genetic Graph Tools)
    if force_step1_outcome:
        step1_decision = Step1Decision(
            outcome=force_step1_outcome,
            best_model_id=pgs_result.models[0].id if pgs_result.models else None,
            confidence="Low",
            rationale=f"FORCED for testing: {force_step1_outcome}"
        )
        logger.info(f"TEST MODE: Forcing Step 1 outcome to {force_step1_outcome}")
    else:
        chain = _build_step1_chain(use_native_prompt=step1_disable_domain_knowledge)
        step1_decision, main_step1_error = _invoke_step1_chain(
            chain=chain,
            context_payload=step1_context,
            pgs_result=pgs_result
        )
        if main_step1_error:
            if strict_llm_only:
                raise RuntimeError(
                    "Step 1 decision failed in strict LLM-only mode: "
                    f"{main_step1_error['error_type']}: {main_step1_error['error_message']}"
                )
            tool_errors.append(main_step1_error)

        if step1_run_ablation:
            if step1_disable_domain_knowledge:
                if knowledge_with_domain is None:
                    knowledge_with_domain = prs_model_domain_knowledge(domain_query)
                shadow_domain = knowledge_with_domain or _empty_domain_knowledge(
                    domain_query, source_type="missing"
                )
                shadow_label = "with_domain_shadow"
            else:
                shadow_domain = _empty_domain_knowledge(
                    domain_query, source_type="disabled_by_ablation"
                )
                shadow_label = "without_domain_shadow"

            shadow_context = dict(step1_context)
            shadow_context["domain_knowledge"] = shadow_domain.model_dump()
            shadow_chain = _build_step1_chain(use_native_prompt=not step1_disable_domain_knowledge)
            step1_shadow_decision, shadow_step1_error = _invoke_step1_chain(
                chain=shadow_chain,
                context_payload=shadow_context,
                pgs_result=pgs_result
            )
            if shadow_step1_error:
                shadow_step1_error["tool_name"] = f"{shadow_label}_step1_decision"
                tool_errors.append(shadow_step1_error)

    # Contribution2 sanity: When evaluated_pgs_whitelist is used, Step 1 models == N Models.
    # NO_MATCH_FOUND is impossible (models exist). Override LLM if it incorrectly returns it.
    if (
        os.getenv(CONTRIB2_EVALUATED_PGS_JSON_ENV)
        and pgs_result.after_filter > 0
        and not strict_llm_only
    ):
        if step1_decision.outcome == "NO_MATCH_FOUND":
            step1_decision = Step1Decision(
                outcome="DIRECT_SUB_OPTIMAL",
                best_model_id=step1_decision.best_model_id or (pgs_result.models[0].id if pgs_result.models else None),
                confidence=step1_decision.confidence,
                rationale=f"[Contribution2 override] Models exist (after_filter={pgs_result.after_filter}); "
                f"NO_MATCH_FOUND invalid. Overridden to DIRECT_SUB_OPTIMAL. Original: {step1_decision.rationale}"
            )
            logger.info("Contribution2: Overrode NO_MATCH_FOUND -> DIRECT_SUB_OPTIMAL (models exist)")

    logger.info(
        f"Step 1 decision: outcome={step1_decision.outcome}, "
        f"confidence={step1_decision.confidence}, "
        f"best_model_id={step1_decision.best_model_id}, "
        f"pgs_total_found={pgs_result.total_found}, "
        f"pgs_after_filter={pgs_result.after_filter}, "
        f"models_returned={len(pgs_result.models)}, "
        f"domain_knowledge_enabled={not step1_disable_domain_knowledge}"
    )

    step1_ablation_summary = {
        "domain_knowledge_main_enabled": not step1_disable_domain_knowledge,
        "shadow_enabled": step1_run_ablation,
        "main_decision": step1_decision.model_dump(),
        "main_rationale_features": _extract_step1_rationale_features(step1_decision.rationale),
        "shadow_decision": step1_shadow_decision.model_dump() if step1_shadow_decision else None,
        "shadow_rationale_features": (
            _extract_step1_rationale_features(step1_shadow_decision.rationale)
            if step1_shadow_decision else None
        ),
    }

    if step1_disable_domain_knowledge or step1_run_ablation:
        step1_ablation_payload = {
            "target_trait": target_trait,
            "settings": {
                "disable_domain_knowledge": step1_disable_domain_knowledge,
                "run_no_domain_ablation": step1_run_ablation,
            },
            "domain_query": domain_query,
            "main_domain_knowledge_source": knowledge.source_type,
            "shadow_domain_knowledge_source": (
                "enabled" if (step1_shadow_decision and step1_disable_domain_knowledge) else "disabled"
            ) if step1_shadow_decision else None,
            "model_feature_table": _build_step1_feature_table(pgs_result.models),
            "main_decision": step1_decision.model_dump(),
            "main_rationale_features": _extract_step1_rationale_features(step1_decision.rationale),
            "shadow_decision": step1_shadow_decision.model_dump() if step1_shadow_decision else None,
            "shadow_rationale_features": (
                _extract_step1_rationale_features(step1_shadow_decision.rationale)
                if step1_shadow_decision else None
            ),
        }
        step1_ablation_artifact_path = _write_json_artifact(
            prefix=f"step1_ablation_{_slugify(target_trait)}",
            payload=step1_ablation_payload
        )

    # Update progress: Step 3 completed, decision made
    if request_id and request_id in search_progress:
        search_progress[request_id].update({
            "fetched": 3,
            "current_action": "Step 1 assessment complete",
            "current_step": "step-3"
        })

    cross_disease_candidates: List[Dict[str, Any]] = []
    weak_mechanism_traits: List[str] = []
    genetic_graph_evidence: List[GeneticGraphEvidence] = []
    genetic_graph_neighbors: List[str] = []
    genetic_graph_errors: List[str] = []
    local_graph_rerank_summary: Optional[Dict[str, Any]] = None
    local_graph_rerank_artifact_path: Optional[str] = None

    run_cross_disease = step1_decision.outcome in {"DIRECT_SUB_OPTIMAL", "NO_MATCH_FOUND"}

    # Contribution2: Step 1 only. Skip Step 2a (genetic graph/heritability) to avoid loading
    # GWAS Atlas h2/gc data. The experiment evaluates direct match selection only.
    if os.getenv(CONTRIB2_EVALUATED_PGS_JSON_ENV):
        run_cross_disease = False

    # If not running cross-disease, mark steps 4-5 as skipped and move to final
    if not run_cross_disease and request_id and request_id in search_progress:
        search_progress[request_id].update({
            "fetched": 5,  # Skip to step 5 (which will be skipped)
            "current_action": "Direct match found, skipping cross-disease analysis",
            "current_step": "step-final"
        })

    if run_cross_disease:
        # Heavy services are only required for cross-disease analysis.
        # Lazily instantiate them here so STEP 1 progress starts immediately.
        ot_client = OpenTargetsClient()
        phewas_client = PheWASClient()
        kg_service = KnowledgeGraphService()

        # Update progress: Step 4 started (cross-disease)
        if request_id and request_id in search_progress:
                search_progress[request_id].update({
                    "fetched": 4,
                    "current_action": "Exploring genetic relationships",
                    "current_step": "step-4"
                })
        # Step 2a: Cross-disease transfer
        # NOTE: According to Single Agent Principle, the Agent should decide to call
        # trait_synonym_expand and genetic_graph_get_neighbors via system prompts.
        # This orchestrator maintains backward compatibility by calling tools directly.
        # Expand trait synonyms (excluding codes) for Knowledge Graph search
        synonym_result = trait_synonym_expand(target_trait, include_icd10=False, include_efo=False)
        expanded_queries = [target_trait]  # Fallback to original trait if expansion fails
        if hasattr(synonym_result, 'expanded_queries') and synonym_result.expanded_queries:
            # Filter out codes from expanded queries (GWAS Atlas doesn't support codes)
            def _is_code(query: str) -> bool:
                if query.startswith(('EFO_', 'MONDO_')):
                    return True
                if len(query) >= 2 and query[0] in ('C', 'E', 'I') and query[1:].replace('.', '').isdigit():
                    return True
                return False
            expanded_queries = [q for q in synonym_result.expanded_queries if not _is_code(q)]
            logger.info(f"Expanded '{target_trait}' to {len(expanded_queries)} queries for Knowledge Graph search (excluding codes)")
        elif isinstance(synonym_result, ToolError):
            logger.warning(f"Synonym expansion failed for '{target_trait}', using original trait name: {synonym_result.error_message}")
            tool_errors.append(synonym_result.model_dump())
        
        # Search Knowledge Graph for each expanded query and merge neighbors
        # Only accept results where the resolved trait is semantically related to the original query
        # Reject fuzzy matches that resolve to generic/unrelated traits (e.g., "Prostatic cancer" -> "Cancer")
        all_neighbors = []
        seen_trait_ids = set()
        for query in expanded_queries:
            query_result = genetic_graph_get_neighbors(
                kg_service,
                trait_id=query,
                limit=local_graph_neighbor_limit
            )
            if isinstance(query_result, ToolError):
                continue
            if hasattr(query_result, 'neighbors') and query_result.neighbors:
                for neighbor in query_result.neighbors:
                    if neighbor.trait_id not in seen_trait_ids:
                        all_neighbors.append(neighbor)
                        seen_trait_ids.add(neighbor.trait_id)
        
        # Create merged neighbors result
        if all_neighbors:
            # Get target node for h2_meta
            target_node = kg_service.get_trait_node(target_trait)
            target_h2_val = target_node.h2_meta if target_node else None
            target_h2 = float(target_h2_val) if isinstance(target_h2_val, (int, float)) else 0.0
            
            # Keep neighbors ordered by transfer_score.
            # Selection strategy is applied later (scan until first neighbor with PGS hits).
            sorted_neighbors = sorted(all_neighbors, key=lambda n: n.transfer_score, reverse=True)
            selected_neighbors = sorted_neighbors
            
            neighbors_result = NeighborResult(
                query_trait=target_trait,
                resolved_by="synonym_expansion",
                resolution_confidence="High",
                target_trait=target_trait,
                target_h2_meta=target_h2,
                neighbors=selected_neighbors
            )
        else:
            neighbors_result = None
        if isinstance(neighbors_result, ToolError):
            tool_errors.append(neighbors_result.model_dump())
            neighbors_result = None
        
        todo.set_done("Step 2a: Query Knowledge Graph for related traits")
        todo.write()

        # Update progress: Step 5 started (biological validation)
        if request_id and request_id in search_progress:
                search_progress[request_id].update({
                    "fetched": 5,
                    "current_action": "Validating biological mechanisms",
                    "current_step": "step-5"
                })
    else:
        neighbors_result = None

    if isinstance(neighbors_result, ToolError):
        tool_errors.append(neighbors_result.model_dump())
        genetic_graph_errors.append(neighbors_result.error_message)
    elif isinstance(neighbors_result, NeighborResult):
        genetic_graph_neighbors = [n.trait_id for n in neighbors_result.neighbors]
        target_efo, target_mondo = resolve_efo_and_mondo_ids(
            trait_name=target_trait,
            ot_client=ot_client,
            pgs_client=pgs_client,
            pgs_models=pgs_result.models
        )
        if not target_efo and not target_mondo:
            tool_errors.append({
                "tool_name": "resolve_efo_and_mondo_ids",
                "error_type": "DiseaseIdNotFound",
                "error_message": f"No EFO or MONDO ID resolved for target trait '{target_trait}'",
                "context": {"trait": target_trait}
            })

        # Local graph reranking: combine graph structure with PRS availability and
        # semantic closeness. This extends pure transfer_score ranking and avoids
        # over-reliance on top-1 early stop.
        ordered_candidates = list(neighbors_result.neighbors or [])
        precheck_candidates = ordered_candidates[:local_graph_prefilter_top_k]
        pgs_hit_counts: Dict[str, int] = {}
        for n in precheck_candidates:
            neighbor_trait = getattr(n, "trait_id", "") or ""
            if not neighbor_trait:
                continue
            try:
                pgs_hit_counts[neighbor_trait] = len(pgs_client.search_scores(neighbor_trait))
            except Exception as exc:
                pgs_hit_counts[neighbor_trait] = 0
                tool_errors.append({
                    "tool_name": "pgs_catalog_search_precheck",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "context": {"neighbor_trait": neighbor_trait}
                })

        local_graph_ranked = rerank_neighbors_with_local_graph(
            target_trait=target_trait,
            neighbors=precheck_candidates,
            pgs_hit_counts=pgs_hit_counts,
            similarity_fn=_similarity_score,
            weights=local_graph_weights,
            min_pgs_hits=local_graph_min_pgs_hits,
        )
        selected_neighbor_traits = select_neighbors_from_local_graph(
            ranked_candidates=local_graph_ranked,
            top_n=local_graph_process_top_n,
        )
        local_graph_ranked_by_trait = {c["trait_id"]: c for c in local_graph_ranked}
        neighbors_by_trait = {getattr(n, "trait_id", ""): n for n in precheck_candidates}
        neighbors_to_process = [
            neighbors_by_trait[trait]
            for trait in selected_neighbor_traits
            if trait in neighbors_by_trait
        ]

        local_graph_rerank_summary = {
            "prefilter_top_k": local_graph_prefilter_top_k,
            "process_top_n": local_graph_process_top_n,
            "min_pgs_hits": local_graph_min_pgs_hits,
            "weights": local_graph_weights,
            "candidate_count": len(precheck_candidates),
            "selected_neighbors": selected_neighbor_traits,
            "top_ranked": local_graph_ranked[:max(10, local_graph_process_top_n)],
        }
        local_graph_rerank_artifact_path = _write_json_artifact(
            prefix=f"local_graph_rerank_{_slugify(target_trait)}",
            payload={
                "target_trait": target_trait,
                "summary": local_graph_rerank_summary,
                "all_ranked_candidates": local_graph_ranked,
            }
        )

        for neighbor in neighbors_to_process:
            neighbor_trait = neighbor.trait_id
            # NOTE: According to Single Agent Principle, the Agent should decide to call
            # prs_model_pgscatalog_search via system prompts.
            # This orchestrator maintains backward compatibility by calling tools directly.
            # No synonym expansion needed for PGS Catalog search - it handles trait name matching internally.
            neighbor_models = prs_model_pgscatalog_search(pgs_client, neighbor_trait)
            if isinstance(neighbor_models, ToolError):
                tool_errors.append(neighbor_models.model_dump())
                neighbor_models = PGSSearchResult(
                    query_trait=neighbor_trait,
                    total_found=0,
                    after_filter=0,
                    models=[]
                )
            neighbor_models_found = neighbor_models.after_filter

            neighbor_models_dump = neighbor_models.model_dump()
            neighbor_models_inline, neighbor_models_artifact = maybe_externalize_json(
                payload=neighbor_models_dump,
                artifact_prefix=f"neighbor_models_{_slugify(neighbor_trait)}",
                max_inline_bytes=MAX_INLINE_CONTEXT_BYTES,
                max_inline_tokens=2_000,
                summary_builder=lambda _: _summarize_search_result_for_llm(neighbor_models, top_n=TOP_MODELS_INLINE)
            )

            best_stats = _best_model_stats(neighbor_models.models)
            rerank_meta = local_graph_ranked_by_trait.get(neighbor_trait, {})
            
            # Collect evidence tools: called AFTER models are found (if any models found)
            mechanism_summary = None
            mechanism_confidence = "Low"
            study_power_summary = None
            selected_candidate = None
            
            if neighbor_models_found > 0:
                # Resolve EFO/MONDO IDs for evidence collection
                neighbor_candidates = resolve_efo_candidates(
                    trait_name=neighbor_trait,
                    ot_client=ot_client,
                    pgs_client=pgs_client,
                    pgs_models=neighbor_models.models
                )
                
                neighbor_efo, neighbor_mondo = resolve_efo_and_mondo_ids(
                    trait_name=neighbor_trait,
                    ot_client=ot_client,
                    pgs_client=pgs_client,
                    pgs_models=neighbor_models.models
                )
                
                selected_candidate = neighbor_candidates[0] if neighbor_candidates else None
                if not selected_candidate and (neighbor_efo or neighbor_mondo):
                    # Fallback: create candidate from resolved IDs
                    selected_candidate = EfoCandidate(
                        id=neighbor_efo or neighbor_mondo or "",
                        label=neighbor_trait,
                        score=1.0,
                        source="ot"  # Default to "ot" as fallback
                    )
                
                # Call genetic_graph_validate_mechanism to collect biological evidence (does NOT affect workflow decision)
                mechanism = genetic_graph_validate_mechanism(
                    ot_client,
                    source_trait_efo=neighbor_efo or "",
                    target_trait_efo=target_efo or "",
                    source_trait_name=neighbor_trait,
                    target_trait_name=target_trait,
                    phewas_client=phewas_client,
                    source_trait_mondo=neighbor_mondo,
                    target_trait_mondo=target_mondo
                )
                
                if isinstance(mechanism, ToolError):
                    tool_errors.append(mechanism.model_dump())
                elif isinstance(mechanism, MechanismValidation):
                    mechanism_summary = _summarize_mechanism(mechanism)
                    mechanism_confidence = mechanism.confidence_level
                
                # Call genetic_graph_verify_study_power to collect statistical evidence (does NOT affect workflow decision)
                study_power = genetic_graph_verify_study_power(
                    kg_service,
                    source_trait=target_trait,
                    target_trait=neighbor_trait
                )
                if isinstance(study_power, ToolError):
                    tool_errors.append(study_power.model_dump())
                else:
                    study_power_summary = StudyPowerSummary(
                        n_correlations=study_power.n_correlations,
                        rg_meta=study_power.rg_meta
                    )

            candidate = {
                "neighbor_trait": neighbor_trait,
                "neighbor_domain": neighbor.domain,
                "rg_meta": neighbor.rg_meta,
                "transfer_score": neighbor.transfer_score,
                "local_graph_score": rerank_meta.get("local_graph_score"),
                "local_graph_rank": rerank_meta.get("local_graph_rank"),
                "local_graph_pgs_hit_count": rerank_meta.get("pgs_hit_count"),
                "local_graph_rule_passed": rerank_meta.get("passes_rules"),
                "local_graph_rule_failures": rerank_meta.get("rule_failures"),
                "neighbor_efo_id": selected_candidate.id if selected_candidate else None,
                "neighbor_efo_source": selected_candidate.source if selected_candidate else None,
                "mechanism_validation": mechanism_summary,
                "mechanism_confidence": mechanism_confidence,
                "mechanism_is_weak": mechanism_confidence == "Low",
                "mechanism_missing": mechanism_summary is None,
                "neighbor_models": neighbor_models_inline,
                "neighbor_models_artifact": neighbor_models_artifact.model_dump() if neighbor_models_artifact else None,
                "neighbor_models_best": best_stats,
                "neighbor_models_found": neighbor_models_found,
                "study_power_summary": study_power_summary.model_dump() if study_power_summary else None
            }
            cross_disease_candidates.append(candidate)
            
            # Note: mechanism_confidence is collected for report evidence only, not used as decision gate

            # Ensure shared_genes is always a list, never None
            shared_genes_list = []
            if isinstance(mechanism_summary, dict):
                shared_genes_raw = mechanism_summary.get("shared_genes")
                if shared_genes_raw is not None:
                    shared_genes_list = shared_genes_raw if isinstance(shared_genes_raw, list) else []
            
            genetic_graph_evidence.append(
                GeneticGraphEvidence(
                    neighbor_trait=neighbor_trait,
                    rg_meta=neighbor.rg_meta,
                    transfer_score=neighbor.transfer_score,
                    neighbor_models_found=neighbor_models_found,
                    neighbor_best_model_id=best_stats.get("best_model_id"),
                    neighbor_best_model_auc=best_stats.get("best_model_auc"),
                    mechanism_confidence=mechanism_confidence,
                    mechanism_summary=mechanism_summary.get("mechanism_summary") if isinstance(mechanism_summary, dict) else None,
                    shared_genes=shared_genes_list,
                    study_power=study_power_summary
                )
            )

        todo.set_done("Step 2a: Validate biological mechanism")
        todo.set_done("Step 2a: Evaluate related-trait models")
        todo.write()

    # Final report generation
    final_context_full = {
        "target_trait": target_trait,
        "step1_decision": step1_decision.model_dump(),
        "step1_context": step1_context,
        "step1_ablation_summary": step1_ablation_summary,
        "step1_ablation_artifact": step1_ablation_artifact_path,
        "cross_disease_candidates": cross_disease_candidates,
        "local_graph_rerank_summary": local_graph_rerank_summary,
        "local_graph_rerank_artifact": local_graph_rerank_artifact_path,
        "weak_mechanism_traits": weak_mechanism_traits,
        "tool_errors": tool_errors,
        "scratchpad": _build_scratchpad(step1_decision, cross_disease_candidates),
        "todo_recitation_path": str(todo_path),
        "todo_recitation": todo.render()
    }

    # Manus: Use the File System as Context
    # If the final context is large, persist and provide a compact inline view.
    final_context_inline, final_context_artifact = maybe_externalize_json(
        payload=final_context_full,
        artifact_prefix=f"recommendation_context_{_slugify(target_trait)}",
        max_inline_bytes=MAX_INLINE_CONTEXT_BYTES,
        max_inline_tokens=2_000,
        summary_builder=lambda p: {
            "target_trait": p.get("target_trait"),
            "step1_decision": p.get("step1_decision"),
            "step1_ablation_summary": p.get("step1_ablation_summary"),
            "step1_ablation_artifact": p.get("step1_ablation_artifact"),
            "direct_models_summary": _summarize_search_result_for_llm(pgs_result, top_n=TOP_MODELS_INLINE),
            "local_graph_rerank_summary": p.get("local_graph_rerank_summary"),
            "local_graph_rerank_artifact": p.get("local_graph_rerank_artifact"),
            "cross_disease_candidates_summary": [
                {
                    "neighbor_trait": c.get("neighbor_trait"),
                    "transfer_score": c.get("transfer_score"),
                    "local_graph_score": c.get("local_graph_score"),
                    "local_graph_rank": c.get("local_graph_rank"),
                    "local_graph_pgs_hit_count": c.get("local_graph_pgs_hit_count"),
                    "mechanism_confidence": c.get("mechanism_confidence"),
                    "neighbor_models_best": c.get("neighbor_models_best"),
                    "neighbor_models_artifact": c.get("neighbor_models_artifact"),
                }
                for c in (p.get("cross_disease_candidates") or [])
            ],
            "weak_mechanism_traits": p.get("weak_mechanism_traits"),
            "tool_errors_count": len(p.get("tool_errors") or []),
            "todo_recitation_path": p.get("todo_recitation_path"),
            "todo_recitation": p.get("todo_recitation"),
        }
    )

    report_input_context = {
        "inline_context": final_context_inline,
        "artifact_context": final_context_artifact.model_dump() if final_context_artifact else None
    }

    try:
        report_chain = _build_report_chain()
        report = report_chain.invoke(
            {"context_json": stable_json_dumps(report_input_context)}
        )
        # Ensure all list fields are not None (LLM may return None for optional fields)
        report = _ensure_list_fields_not_none(report)
        logger.info(
            f"Report generated: recommendation_type={report.recommendation_type}, "
            f"step1_outcome={step1_decision.outcome if step1_decision else 'None'}"
        )
    except Exception as exc:
        if strict_llm_only:
            raise RuntimeError(
                f"Report generation failed in strict LLM-only mode: {type(exc).__name__}: {exc}"
            ) from exc

        # Update progress: Final step (report generation) - before LLM call
        if request_id and request_id in search_progress:
            search_progress[request_id].update({
                "fetched": 6,
                "current_action": "Generating report",
                "current_step": "step-final"
            })

        # Fallback: Use Step 1 decision to determine recommendation_type
        # This ensures we don't lose the Step 1 assessment even if report generation fails
        fallback_recommendation_type = "NO_MATCH_FOUND"
        fallback_primary_recommendation = None
        fallback_direct_match_evidence = None
        
        if step1_decision:
            if step1_decision.outcome == "DIRECT_HIGH_QUALITY":
                fallback_recommendation_type = "DIRECT_HIGH_QUALITY"
                if step1_decision.best_model_id:
                    fallback_primary_recommendation = PrimaryRecommendation(
                        pgs_id=step1_decision.best_model_id,
                        source_trait=None,
                        confidence=step1_decision.confidence,
                        rationale=step1_decision.rationale
                    )
                    fallback_direct_match_evidence = DirectMatchEvidence(
                        models_evaluated=len(pgs_result.models),
                        performance_metrics=landscape.model_dump() if landscape else {},
                        clinical_benchmarks=[]
                    )
            elif step1_decision.outcome == "DIRECT_SUB_OPTIMAL":
                fallback_recommendation_type = "DIRECT_SUB_OPTIMAL"
                if step1_decision.best_model_id:
                    fallback_primary_recommendation = PrimaryRecommendation(
                        pgs_id=step1_decision.best_model_id,
                        source_trait=None,
                        confidence=step1_decision.confidence,
                        rationale=step1_decision.rationale
                    )
                    fallback_direct_match_evidence = DirectMatchEvidence(
                        models_evaluated=len(pgs_result.models),
                        performance_metrics=landscape.model_dump() if landscape else {},
                        clinical_benchmarks=[]
                    )
            # If step1_decision.outcome is "NO_MATCH_FOUND", keep fallback_recommendation_type as "NO_MATCH_FOUND"
        
        logger.warning(
            f"Report generation failed, using fallback based on Step 1 decision: "
            f"step1_outcome={step1_decision.outcome if step1_decision else 'None'}, "
            f"fallback_recommendation_type={fallback_recommendation_type}, "
            f"error={exc}"
        )

        report = RecommendationReport(
            recommendation_type=fallback_recommendation_type,
            primary_recommendation=fallback_primary_recommendation,
            alternative_recommendations=[],
            direct_match_evidence=fallback_direct_match_evidence,
            cross_disease_evidence=None,
            genetic_graph_evidence=[],
            genetic_graph_ran=run_cross_disease,
            genetic_graph_neighbors=genetic_graph_neighbors if (run_cross_disease and genetic_graph_neighbors) else [],
            genetic_graph_errors=genetic_graph_errors if (run_cross_disease and genetic_graph_errors) else [],
            caveats_and_limitations=[
                f"Failed to generate structured report: {exc}",
                "Report generated using fallback logic based on Step 1 assessment."
            ],
            follow_up_options=[]
        )

    # Contribution2 safety: If LLM omitted primary_recommendation but Step 1 has best_model_id,
    # fill it from step1_decision to avoid spurious MISS in evaluation.
    if (
        os.getenv(CONTRIB2_EVALUATED_PGS_JSON_ENV)
        and not strict_llm_only
        and report.primary_recommendation is None
        and step1_decision
        and step1_decision.outcome in {"DIRECT_HIGH_QUALITY", "DIRECT_SUB_OPTIMAL"}
        and step1_decision.best_model_id
    ):
        report = report.model_copy(
            update={
                "primary_recommendation": PrimaryRecommendation(
                    pgs_id=step1_decision.best_model_id,
                    source_trait=None,
                    confidence=step1_decision.confidence,
                    rationale=step1_decision.rationale or "Contribution2: filled from Step 1 decision",
                )
            }
        )
        logger.info("Contribution2: Filled primary_recommendation from step1_decision.best_model_id")

    report = ensure_follow_up_options(report)
    # Update genetic graph fields with actual values
    # Ensure all list fields are never None (Pydantic validation requirement)
    report = report.model_copy(update={
        "genetic_graph_evidence": genetic_graph_evidence if run_cross_disease else [],
        "genetic_graph_ran": run_cross_disease,
        "genetic_graph_neighbors": genetic_graph_neighbors if (run_cross_disease and genetic_graph_neighbors) else [],
        "genetic_graph_errors": genetic_graph_errors if (run_cross_disease and genetic_graph_errors) else []
    })
    return report


def _summarize_mechanism(mechanism: MechanismValidation) -> Dict[str, Any]:
    # Ensure shared_genes is always a list, handle None or empty cases
    shared_genes_list = []
    if mechanism.shared_genes is not None:
        shared_genes_list = [g.gene_symbol for g in mechanism.shared_genes[:10]]
    
    return {
        "shared_genes": shared_genes_list,
        "shared_pathways": mechanism.shared_pathways[:10] if mechanism.shared_pathways else [],
        "phewas_evidence_count": mechanism.phewas_evidence_count,
        "mechanism_summary": mechanism.mechanism_summary,
        "confidence_level": mechanism.confidence_level
    }


def _build_scratchpad(
    step1_decision: Step1Decision,
    cross_candidates: List[Dict[str, Any]]
) -> List[str]:
    progress = [
        f"[x] Step 1: Direct match outcome = {step1_decision.outcome}"
    ]
    if cross_candidates:
        progress.append("[x] Step 2a: Cross-disease candidates evaluated")
    else:
        progress.append("[ ] Step 2a: Cross-disease candidates evaluated")
    progress.append("[ ] On-Demand: Offer 'Train New Model' option in final report")
    return progress
