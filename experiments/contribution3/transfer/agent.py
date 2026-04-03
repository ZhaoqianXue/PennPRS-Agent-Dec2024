from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from thefuzz import fuzz

from experiments.contribution3.transfer.common import (
    CandidateBundleDossier,
    TraitBundle,
    normalize_text,
)
from experiments.contribution3.transfer.prompts.transfer_prompt import (
    CrossTraitMatchDecision,
    FINALIZE_TRANSFER_DECISION_PROMPT,
    TOOL_CALLING_TRANSFER_SYSTEM_PROMPT,
)
from experiments.contribution3.transfer.tools import CrossTraitToolbox
from src.server.core.llm_config import get_llm


CONDITION_TOOLS: dict[str, list[str]] = {
    "dossier-only": [],
    "gc-only": ["cross_trait_genetic_correlation"],
    "gc-h2": ["cross_trait_genetic_correlation", "cross_trait_heritability"],
    "all-tools": [
        "cross_trait_genetic_correlation",
        "cross_trait_heritability",
        "cross_trait_open_targets",
    ],
}


def build_dossier_context(dossier: CandidateBundleDossier) -> dict[str, Any]:
    return {
        "target": dossier.target.model_dump(),
        "candidate_bundle_dossier": [
            {
                "bundle_id": candidate.bundle_id,
                "canonical_label": candidate.canonical_label,
                "bundle_type": candidate.bundle_type,
                "aliases": candidate.aliases,
                "candidate_pgs_ids": candidate.candidate_pgs_ids,
                "n_models": candidate.n_models,
                "source_efo_ids": candidate.source_efo_ids,
                "source_mondo_ids": candidate.source_mondo_ids,
            }
            for candidate in dossier.candidates
        ],
    }


def _build_finalize_chain():
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", FINALIZE_TRANSFER_DECISION_PROMPT),
            (
                "human",
                "Return one strict JSON decision from the context below.\n\nContext:\n{context_json}",
            ),
        ]
    )
    structured = llm.with_structured_output(
        CrossTraitMatchDecision,
        method="function_calling",
    )
    return prompt | structured


@lru_cache(maxsize=1)
def _cached_finalize_chain():
    return _build_finalize_chain()


@lru_cache(maxsize=1)
def _cached_base_llm():
    return get_llm("disease_workflow")


def _sanitize_decision(
    decision: CrossTraitMatchDecision,
    dossier: CandidateBundleDossier,
    tool_trace: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_lookup = {candidate.bundle_id: candidate for candidate in dossier.candidates}
    payload = decision.model_dump()
    outcome = str(payload.get("outcome") or "").upper()
    bundle_id = payload.get("best_bundle_id")

    if outcome != "MATCHED":
        payload["outcome"] = "NO_MATCH"
        payload["best_bundle_id"] = None
        payload["best_cross_trait"] = None
        payload["candidate_pgs_ids"] = []
        return payload

    bundle = candidate_lookup.get(str(bundle_id or "").strip())
    if bundle is None:
        payload["outcome"] = "NO_MATCH"
        payload["best_bundle_id"] = None
        payload["best_cross_trait"] = None
        payload["candidate_pgs_ids"] = []
        payload["rationale"] = (
            f"{payload.get('rationale', '').strip()} "
            "The proposed bundle was not present in the static candidate dossier, so the decision was downgraded to NO_MATCH."
        ).strip()
        return payload

    target_texts = [dossier.target.target_label, *dossier.target.aliases]
    is_self_like = any(
        fuzz.token_set_ratio(normalize_text(bundle.canonical_label), normalize_text(target_text)) >= 90
        for target_text in target_texts
        if target_text
    )
    if is_self_like:
        payload["outcome"] = "NO_MATCH"
        payload["best_bundle_id"] = None
        payload["best_cross_trait"] = None
        payload["candidate_pgs_ids"] = []
        payload["rationale"] = (
            f"{payload.get('rationale', '').strip()} "
            "This match was downgraded to NO_MATCH because the selected bundle is self-like to the target trait, and cross-trait transfer must not return a self match."
        ).strip()
        return payload

    selected_gc_available = False
    selected_ot_confidence: str | None = None
    for tool_call in tool_trace:
        for result_row in (tool_call.get("result") or {}).get("results", []):
            if result_row.get("bundle_id") != bundle.bundle_id:
                continue
            if tool_call.get("name") == "cross_trait_genetic_correlation" and result_row.get("rg_meta") is not None:
                selected_gc_available = True
            if tool_call.get("name") == "cross_trait_open_targets":
                selected_ot_confidence = str(result_row.get("confidence_level") or "")

    if not selected_gc_available and str(selected_ot_confidence or "").lower() != "high":
        payload["outcome"] = "NO_MATCH"
        payload["best_bundle_id"] = None
        payload["best_cross_trait"] = None
        payload["candidate_pgs_ids"] = []
        payload["rationale"] = (
            f"{payload.get('rationale', '').strip()} "
            "This match was downgraded to NO_MATCH because no usable genetic correlation evidence was available and Open Targets evidence did not reach High confidence."
        ).strip()
        return payload

    payload["outcome"] = "MATCHED"
    payload["best_bundle_id"] = bundle.bundle_id
    payload["best_cross_trait"] = bundle.canonical_label
    payload["candidate_pgs_ids"] = bundle.candidate_pgs_ids
    return payload


def run_cross_trait_agent(
    dossier: CandidateBundleDossier,
    condition: Literal["dossier-only", "gc-only", "gc-h2", "all-tools"],
    bundles: list[TraitBundle] | None = None,
    toolbox: CrossTraitToolbox | None = None,
    max_steps: int = 8,
) -> dict[str, Any]:
    if condition not in CONDITION_TOOLS:
        raise ValueError(f"Unsupported condition: {condition}")
    if toolbox is None and bundles is None:
        raise ValueError("Either bundles or toolbox must be provided.")

    context = build_dossier_context(dossier)
    if toolbox is None:
        assert bundles is not None
        toolbox = CrossTraitToolbox(bundles)
    tools = [
        tool
        for tool in toolbox.build_tools()
        if tool.name in set(CONDITION_TOOLS[condition])
    ]

    llm = _cached_base_llm()
    tool_llm = llm.bind_tools(tools) if tools else llm

    messages: list[Any] = [
        SystemMessage(content=TOOL_CALLING_TRANSFER_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Review the target trait and candidate bundle dossier below. "
                "Use tools if needed, then stop when you have enough evidence.\n\n"
                f"Context:\n{json.dumps(context, ensure_ascii=False)}"
            )
        ),
    ]
    tool_trace: list[dict[str, Any]] = []

    for _ in range(max_steps):
        ai_message = tool_llm.invoke(messages)
        messages.append(ai_message)
        tool_calls = getattr(ai_message, "tool_calls", None) or []
        if not tool_calls:
            break
        for call in tool_calls:
            name = call["name"]
            args = call.get("args", {})
            tool = next(tool for tool in tools if tool.name == name)
            result = tool.invoke(args)
            tool_trace.append({"name": name, "args": args, "result": result})
            messages.append(
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False),
                    tool_call_id=call["id"],
                    name=name,
                )
            )

    transcript = []
    for msg in messages:
        msg_type = getattr(msg, "type", msg.__class__.__name__)
        content = getattr(msg, "content", "")
        if isinstance(content, list):
            content = json.dumps(content, ensure_ascii=False)
        transcript.append({"type": msg_type, "content": str(content)})

    decision_context = {
        "target": context["target"],
        "candidate_bundle_dossier": context["candidate_bundle_dossier"],
        "tool_trace": tool_trace,
        "agent_transcript": transcript,
    }
    decision = _cached_finalize_chain().invoke(
        {"context_json": json.dumps(decision_context, ensure_ascii=False)}
    )
    return {
        "target": dossier.target.model_dump(),
        "condition": condition,
        "tool_trace": tool_trace,
        "decision": _sanitize_decision(decision, dossier, tool_trace),
    }


def write_agent_results(results: list[dict[str, Any]], outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(results, indent=2, ensure_ascii=False))
