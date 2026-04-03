from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from src.server.core.llm_config import get_llm
from src.server.core.pgs_catalog_client import PGSCatalogClient
from src.server.core.system_prompts import CO_SCIENTIST_STEP1_PROMPT
from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search


class Contribution2Step1Decision(BaseModel):
    outcome: str
    best_model_id: str | None = None
    confidence: str
    rationale: str


def _summarize_model_for_llm(model: Any) -> dict[str, Any]:
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


def _build_chain():
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CO_SCIENTIST_STEP1_PROMPT),
            (
                "human",
                "Perform direct-match assessment only. Use the context JSON below to select "
                "the best supported direct-match candidate and return exactly one JSON object "
                "with fields: outcome, best_model_id, confidence, rationale.\n\nContext:\n{context_json}",
            ),
        ]
    )
    structured = llm.with_structured_output(
        Contribution2Step1Decision,
        method="function_calling",
    )
    return prompt | structured


@lru_cache(maxsize=1)
def _cached_chain():
    return _build_chain()


def recommend_best_model_for_cross_trait(
    cross_trait_label: str,
    candidate_pgs_ids: list[str],
) -> dict[str, Any]:
    client = PGSCatalogClient()
    whitelist = set(candidate_pgs_ids)
    search_result = prs_model_pgscatalog_search(
        client,
        cross_trait_label,
        evaluated_pgs_whitelist=whitelist,
    )
    context = {
        "target_trait": cross_trait_label,
        "direct_models": {
            "query_trait": cross_trait_label,
            "total_found": search_result.total_found,
            "after_filter": search_result.after_filter,
            "models": [_summarize_model_for_llm(model) for model in search_result.models],
        },
        "domain_knowledge": {
            "query": "",
            "snippets": [],
            "source_type": "disabled_for_cross_trait_transfer",
        },
        "todo_recitation_path": "N/A",
        "todo_recitation": "",
    }
    decision = _cached_chain().invoke({"context_json": json.dumps(context, ensure_ascii=False)})
    return {
        "cross_trait_label": cross_trait_label,
        "candidate_pgs_ids": candidate_pgs_ids,
        "decision": decision.model_dump(),
    }
