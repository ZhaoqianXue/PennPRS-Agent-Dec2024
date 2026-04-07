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
    is_self_like_bundle,
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
    "gpt-only": [],
    "dossier-only": [],
    "gc-only": ["cross_trait_genetic_correlation"],
    "gc-h2": ["cross_trait_genetic_correlation", "cross_trait_heritability"],
    "all-tools": [
        "cross_trait_genetic_correlation",
        "cross_trait_heritability",
        "cross_trait_open_targets",
    ],
}


def build_dossier_context(
    dossier: CandidateBundleDossier,
    gc_prescreening: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    gc_rank: dict[str, int] = {}
    if gc_prescreening:
        for idx, row in enumerate(gc_prescreening):
            gc_rank[row.get("bundle_id", "")] = idx

    candidates_data = [
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
    ]
    if gc_rank:
        max_rank = len(candidates_data) + 1
        candidates_data.sort(key=lambda c: gc_rank.get(c["bundle_id"], max_rank))

    context: dict[str, Any] = {"target": dossier.target.model_dump()}
    if gc_prescreening:
        context["gc_prescreening"] = [
            {
                "bundle_id": row.get("bundle_id"),
                "canonical_label": row.get("canonical_label"),
                "rg_meta": row.get("rg_meta"),
                "p_value": row.get("p_value"),
                "unavailable_reason": row.get("unavailable_reason"),
            }
            for row in gc_prescreening
        ]
    context["candidate_bundle_dossier"] = candidates_data
    return context


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


def _prescreen_gc_for_candidates(
    dossier: CandidateBundleDossier,
    toolbox: CrossTraitToolbox,
) -> list[dict[str, Any]]:
    """Pre-compute GC for all candidate bundles against the target trait.

    Returns results sorted by |rg| descending (unavailable candidates last).
    Also populates the toolbox resolution caches so subsequent agent tool
    calls avoid redundant lookups.
    """
    target_label = dossier.target.target_label or ""
    all_bundle_ids = [c.bundle_id for c in dossier.candidates]
    gc_result = toolbox.cross_trait_genetic_correlation(target_label, all_bundle_ids)
    results: list[dict[str, Any]] = gc_result.get("results", [])
    for row in results:
        rg = row.get("rg_meta")
        row["_abs_rg"] = abs(rg) if rg is not None else -1.0
    results.sort(key=lambda r: (-r["_abs_rg"], r.get("p_value") or 999.0))
    return results


def _gc_driven_fallback(
    dossier: CandidateBundleDossier,
    gc_prescreening: list[dict[str, Any]],
    condition: str,
) -> dict[str, Any] | None:
    """When the agent returns NO_MATCH, rescue by selecting the strongest GC candidate.

    Only activates when a candidate has |rg| >= 0.15 and p < 0.05 — i.e.
    there IS a genetically correlated cross-trait, the agent just chose not to
    select it.  A moderate match (GPR ~0.3) is far better than NO_MATCH
    (GPR = 0).
    """
    if condition in ("gpt-only", "dossier-only"):
        return None

    for gc_row in gc_prescreening:
        rg = gc_row.get("rg_meta")
        p_val = gc_row.get("p_value")
        if rg is None or p_val is None:
            continue
        if abs(rg) < 0.15 or p_val >= 0.05:
            continue

        bundle_id = gc_row.get("bundle_id", "")
        bundle = next(
            (c for c in dossier.candidates if c.bundle_id == bundle_id), None
        )
        if bundle is None:
            continue
        if is_self_like_bundle(dossier.target, bundle):
            continue

        return {
            "outcome": "MATCHED",
            "best_bundle_id": bundle.bundle_id,
            "best_cross_trait": bundle.canonical_label,
            "candidate_pgs_ids": bundle.candidate_pgs_ids,
            "confidence": "Moderate",
            "rationale": (
                f"GC-driven fallback: {bundle.canonical_label} has "
                f"rg={rg:.3f} (p={p_val:.2e}) with the target trait."
            ),
            "evidence_summary": {
                "gc_fallback": True,
                "rg": rg,
                "p_value": p_val,
            },
        }
    return None


def _expand_with_secondary_bundles(
    primary_bundle_id: str,
    dossier: CandidateBundleDossier,
    gc_prescreening: list[dict[str, Any]],
    primary_pgs_ids: list[str],
    *,
    max_secondary: int = 2,
    min_abs_rg: float = 0.25,
    max_p: float = 0.05,
) -> list[str]:
    """Merge PGS IDs from secondary high-GC bundles into the model universe.

    This expands the candidate set for Contribution2 Step 1, increasing the
    chance that the best-performing PGS model is available for selection.
    """
    candidate_lookup = {c.bundle_id: c for c in dossier.candidates}
    merged = set(primary_pgs_ids)
    added = 0
    for gc_row in gc_prescreening:
        if added >= max_secondary:
            break
        rg = gc_row.get("rg_meta")
        p_val = gc_row.get("p_value")
        if rg is None or p_val is None:
            continue
        bid = gc_row.get("bundle_id", "")
        if bid == primary_bundle_id:
            continue
        if abs(rg) < min_abs_rg or p_val >= max_p:
            continue
        bundle = candidate_lookup.get(bid)
        if bundle is None:
            continue
        if is_self_like_bundle(dossier.target, bundle):
            continue
        merged.update(bundle.candidate_pgs_ids)
        added += 1
    return sorted(merged)


def _sanitize_decision(
    decision: CrossTraitMatchDecision,
    dossier: CandidateBundleDossier,
    tool_trace: list[dict[str, Any]],
    condition: str = "",
    gc_prescreening: list[dict[str, Any]] | None = None,
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
    is_self = any(
        fuzz.token_set_ratio(normalize_text(bundle.canonical_label), normalize_text(target_text)) >= 90
        for target_text in target_texts
        if target_text
    )
    if is_self:
        payload["outcome"] = "NO_MATCH"
        payload["best_bundle_id"] = None
        payload["best_cross_trait"] = None
        payload["candidate_pgs_ids"] = []
        payload["rationale"] = (
            f"{payload.get('rationale', '').strip()} "
            "This match was downgraded to NO_MATCH because the selected bundle is self-like to the target trait, and cross-trait transfer must not return a self match."
        ).strip()
        return payload

    # --- Evidence gate (relaxed) ---
    selected_gc_available = False
    selected_gc_from_prescreening = False
    selected_ot_confidence: str | None = None
    selected_ot_gene_count = 0

    # Check tool trace evidence
    for tool_call in tool_trace:
        for result_row in (tool_call.get("result") or {}).get("results", []):
            if result_row.get("bundle_id") != bundle.bundle_id:
                continue
            if tool_call.get("name") == "cross_trait_genetic_correlation" and result_row.get("rg_meta") is not None:
                selected_gc_available = True
            if tool_call.get("name") == "cross_trait_open_targets":
                selected_ot_confidence = str(result_row.get("confidence_level") or "")
                selected_ot_gene_count = len(result_row.get("shared_genes") or [])

    # Also check GC pre-screening for evidence
    if not selected_gc_available and gc_prescreening:
        for gc_row in gc_prescreening:
            if gc_row.get("bundle_id") == bundle.bundle_id and gc_row.get("rg_meta") is not None:
                p_val = gc_row.get("p_value")
                if p_val is not None and p_val < 0.05:
                    selected_gc_available = True
                    selected_gc_from_prescreening = True
                break

    ot_conf_lower = str(selected_ot_confidence or "").lower()
    ot_sufficient = ot_conf_lower in ("high", "moderate") and selected_ot_gene_count >= 3

    if condition not in ("gpt-only", "dossier-only") and not selected_gc_available and not ot_sufficient:
        payload["outcome"] = "NO_MATCH"
        payload["best_bundle_id"] = None
        payload["best_cross_trait"] = None
        payload["candidate_pgs_ids"] = []
        payload["rationale"] = (
            f"{payload.get('rationale', '').strip()} "
            "This match was downgraded to NO_MATCH because no usable genetic correlation evidence was available "
            "and Open Targets evidence did not reach sufficient confidence."
        ).strip()
        return payload

    payload["outcome"] = "MATCHED"
    payload["best_bundle_id"] = bundle.bundle_id
    payload["best_cross_trait"] = bundle.canonical_label
    payload["candidate_pgs_ids"] = bundle.candidate_pgs_ids
    return payload


def run_cross_trait_agent(
    dossier: CandidateBundleDossier,
    condition: Literal["gpt-only", "dossier-only", "gc-only", "gc-h2", "all-tools"],
    bundles: list[TraitBundle] | None = None,
    toolbox: CrossTraitToolbox | None = None,
    max_steps: int = 8,
) -> dict[str, Any]:
    if condition not in CONDITION_TOOLS:
        raise ValueError(f"Unsupported condition: {condition}")
    if toolbox is None and bundles is None:
        raise ValueError("Either bundles or toolbox must be provided.")

    if toolbox is None:
        assert bundles is not None
        toolbox = CrossTraitToolbox(bundles)

    # --- GC pre-screening: batch lookup for all candidates before agent loop ---
    gc_prescreening: list[dict[str, Any]] = []
    if condition not in ("gpt-only", "dossier-only"):
        gc_prescreening = _prescreen_gc_for_candidates(dossier, toolbox)

    context = build_dossier_context(dossier, gc_prescreening=gc_prescreening)
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
        "gc_prescreening": context.get("gc_prescreening", []),
        "tool_trace": tool_trace,
        "agent_transcript": transcript,
    }
    decision = _cached_finalize_chain().invoke(
        {"context_json": json.dumps(decision_context, ensure_ascii=False)}
    )
    sanitized = _sanitize_decision(
        decision, dossier, tool_trace, condition=condition,
        gc_prescreening=gc_prescreening,
    )

    # --- NO_MATCH fallback: rescue with strongest GC candidate ---
    if sanitized["outcome"] == "NO_MATCH" and gc_prescreening:
        fallback = _gc_driven_fallback(dossier, gc_prescreening, condition)
        if fallback is not None:
            sanitized = fallback

    # --- Multi-bundle expansion: merge PGS IDs from related bundles ---
    if sanitized["outcome"] == "MATCHED" and gc_prescreening:
        sanitized["candidate_pgs_ids"] = _expand_with_secondary_bundles(
            primary_bundle_id=sanitized["best_bundle_id"],
            dossier=dossier,
            gc_prescreening=gc_prescreening,
            primary_pgs_ids=sanitized["candidate_pgs_ids"],
        )

    return {
        "target": dossier.target.model_dump(),
        "condition": condition,
        "tool_trace": tool_trace,
        "gc_prescreening_count": len(gc_prescreening),
        "decision": sanitized,
    }


def write_agent_results(results: list[dict[str, Any]], outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(results, indent=2, ensure_ascii=False))
