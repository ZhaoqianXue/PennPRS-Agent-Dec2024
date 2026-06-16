from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from experiments.contribution3.transfer.common import (
    CandidateBundleDossier,
    condition_recommendations_json,
    condition_results_json,
)


DIRECT_BASELINE_CONDITION = "gpt-no-harness"
MAX_ALIASES_PER_BUNDLE = 4


class DirectNoHarnessSelection(BaseModel):
    """Single-shot GPT-only cross-trait PRS selection.

    This schema deliberately contains only the final direct choice. It has no
    fields for gathered evidence, tool traces, staged rankings, retries, or
    PRS-skill reasoning because those are exactly what this baseline removes.
    """

    outcome: Literal["MATCHED"] = Field(
        default="MATCHED",
        description="Forced-choice baseline: always select one provided source bundle and one PGS ID."
    )
    best_bundle_id: str = Field(
        description="One bundle_id copied exactly from the candidate list.",
    )
    best_model_id: str = Field(
        description="One PGS ID copied exactly from the selected bundle.",
    )
    confidence: Literal["High", "Moderate", "Low"] = "Low"
    rationale: str = Field(
        default="",
        description="Brief direct-prompt rationale. No external evidence or tool output.",
    )


SYSTEM_PROMPT = """You are GPT-5.2 being evaluated as a strict forced-choice direct-prompt baseline for cross-trait PRS model selection.

This is a no-agent-harness condition:
- Use only the target trait and candidate list provided in this single prompt.
- Do not call tools, request additional evidence, simulate tool output, or describe a multi-stage workflow.
- Do not use PRS-specific expert Skill rules. Make only a direct semantic and biomedical plausibility judgment from the candidate names.
- You must select exactly one candidate source bundle and exactly one PGS ID from that same bundle for every target.
- Even if all candidates are weak, choose the most plausible available candidate. Do not abstain.

The selected best_model_id must be copied exactly from the pgs_ids list of the selected best_bundle_id."""


def _compact_candidate(bundle) -> dict[str, Any]:
    return {
        "bundle_id": bundle.bundle_id,
        "source_trait": bundle.canonical_label,
        "trait_type": bundle.bundle_type,
        "aliases": bundle.aliases[:MAX_ALIASES_PER_BUNDLE],
        "n_models": bundle.n_models,
        "pgs_ids": bundle.candidate_pgs_ids,
    }


def build_direct_prompt_context(dossier: CandidateBundleDossier) -> str:
    payload = {
        "target": {
            "target_id": dossier.target.target_id,
            "target_label": dossier.target.target_label,
            "aliases": dossier.target.aliases,
        },
        "candidate_bundles": [
            _compact_candidate(bundle)
            for bundle in dossier.candidates
        ],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def invoke_direct_selection(dossier: CandidateBundleDossier) -> DirectNoHarnessSelection:
    from langchain_core.messages import HumanMessage, SystemMessage

    from src.server.core.llm_config import get_llm

    llm = get_llm("disease_workflow")
    chain = llm.with_structured_output(
        DirectNoHarnessSelection,
        method="function_calling",
    )
    return chain.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=build_direct_prompt_context(dossier)),
        ]
    )


def _candidate_cards(dossier: CandidateBundleDossier) -> list[dict[str, Any]]:
    return [
        {
            "bundle_id": bundle.bundle_id,
            "canonical_label": bundle.canonical_label,
            "bundle_type": bundle.bundle_type,
            "candidate_pgs_ids": bundle.candidate_pgs_ids,
            "n_models": bundle.n_models,
        }
        for bundle in dossier.candidates
    ]


def _empty_decision(selection: DirectNoHarnessSelection, validation_error: str | None) -> dict[str, Any]:
    return {
        "outcome": "NO_MATCH",
        "best_cross_trait": None,
        "primary_bundle_id": None,
        "best_bundle_id": None,
        "frontier_bundle_ids": [],
        "frontier_bundle_weights": {},
        "confidence": selection.confidence,
        "stage2": {},
        "critic": None,
        "evidence_state": {"candidate_cards": []},
        "search_trace": {
            "direct_no_harness": True,
            "tool_calls": 0,
            "agent_stages": 0,
            "repairs": 0,
        },
        "best_model_id": None,
        "recommended_model_ids": [],
        "model_frontier": [],
        "candidate_pgs_ids": [],
        "candidate_pgs_ids_union": [],
        "rationale": selection.rationale,
        "validation_error": validation_error,
        "raw_selection": selection.model_dump(),
    }


def build_direct_result_record(
    dossier: CandidateBundleDossier,
    selection: DirectNoHarnessSelection,
    *,
    condition: str = DIRECT_BASELINE_CONDITION,
) -> dict[str, Any]:
    bundle_by_id = {bundle.bundle_id: bundle for bundle in dossier.candidates}

    validation_error: str | None = None
    format_normalization_applied = False
    selected_bundle = None
    best_model_id: str | None = None
    if selection.outcome == "MATCHED":
        selected_bundle = bundle_by_id.get(str(selection.best_bundle_id or "").strip())
        if selected_bundle is None:
            validation_error = f"Selected bundle_id {selection.best_bundle_id!r} is not in the candidate list."
            selected_bundle = next(
                (bundle for bundle in dossier.candidates if bundle.candidate_pgs_ids),
                None,
            )
            format_normalization_applied = selected_bundle is not None
        elif str(selection.best_model_id or "").strip() not in selected_bundle.candidate_pgs_ids:
            validation_error = (
                f"Selected best_model_id {selection.best_model_id!r} does not belong to "
                f"selected bundle_id {selection.best_bundle_id!r}."
            )
            format_normalization_applied = True
    else:
        validation_error = "Model returned NO_MATCH."

    if selected_bundle is not None and selected_bundle.candidate_pgs_ids:
        requested_model_id = str(selection.best_model_id or "").strip()
        best_model_id = (
            requested_model_id
            if requested_model_id in selected_bundle.candidate_pgs_ids
            else selected_bundle.candidate_pgs_ids[0]
        )

    if selected_bundle is None or best_model_id is None:
        decision = _empty_decision(selection, validation_error)
        decision["evidence_state"] = {"candidate_cards": _candidate_cards(dossier)}
    else:
        candidate_pgs_ids = list(selected_bundle.candidate_pgs_ids)
        decision = {
            "outcome": "MATCHED",
            "best_cross_trait": selected_bundle.canonical_label,
            "primary_bundle_id": selected_bundle.bundle_id,
            "best_bundle_id": selected_bundle.bundle_id,
            "frontier_bundle_ids": [selected_bundle.bundle_id],
            "frontier_bundle_weights": {selected_bundle.bundle_id: 1.0},
            "confidence": selection.confidence,
            "stage2": {
                "primary_model_id": best_model_id,
                "recommended_models": [
                    {
                        "pgs_id": best_model_id,
                        "bundle_id": selected_bundle.bundle_id,
                        "rank": 1,
                        "confidence": selection.confidence,
                        "rationale": selection.rationale,
                    }
                ],
                "model_universe_size": len(candidate_pgs_ids),
                "decision_rationale": selection.rationale,
            },
            "critic": None,
            "evidence_state": {"candidate_cards": _candidate_cards(dossier)},
            "search_trace": {
                "direct_no_harness": True,
                "tool_calls": 0,
                "agent_stages": 0,
                "repairs": 0,
                "format_normalization_applied": format_normalization_applied,
                "probed_bundle_ids": [],
                "supporting_bundle_ids": [selected_bundle.bundle_id],
                "local_champion_ids": [best_model_id],
                "model_frontier_ids": [best_model_id],
                "bundle_pgs_lookup": {
                    selected_bundle.bundle_id: candidate_pgs_ids,
                },
            },
            "best_model_id": best_model_id,
            "recommended_model_ids": [best_model_id],
            "model_frontier": [
                {
                    "pgs_id": best_model_id,
                    "bundle_id": selected_bundle.bundle_id,
                    "rank": 1,
                    "confidence": selection.confidence,
                    "rationale": selection.rationale,
                }
            ],
            "candidate_pgs_ids": candidate_pgs_ids,
            "candidate_pgs_ids_union": candidate_pgs_ids,
            "rationale": selection.rationale,
            "validation_error": validation_error,
            "format_normalization_applied": format_normalization_applied,
            "raw_selection": selection.model_dump(),
        }

    return {
        "target": dossier.target.model_dump(),
        "condition": condition,
        "baseline_type": "single_shot_gpt_no_agent_harness",
        "decision": decision,
    }


def build_direct_recommendation_record(
    result: dict[str, Any],
    *,
    condition: str = DIRECT_BASELINE_CONDITION,
) -> dict[str, Any]:
    decision = result.get("decision") or {}
    target = result.get("target") or {}
    record = {
        "target": target,
        "condition": condition,
        "transfer_decision": decision,
        "recommendation": None,
    }
    if decision.get("outcome") != "MATCHED":
        return record

    best_model_id = decision.get("best_model_id")
    record["recommendation"] = {
        "original_target_trait": str(target.get("target_label") or "").strip(),
        "matched_cross_trait": decision.get("best_cross_trait"),
        "matched_bundle_id": decision.get("best_bundle_id"),
        "frontier_bundle_ids": decision.get("frontier_bundle_ids") or [],
        "frontier_bundle_weights": decision.get("frontier_bundle_weights") or {},
        "candidate_pgs_ids": decision.get("candidate_pgs_ids") or [],
        "retrieval": {
            "direct_no_harness": True,
            "tool_calls": 0,
            "agent_stages": 0,
            "repairs": 0,
            "hydrated_model_count": len(decision.get("candidate_pgs_ids") or []),
            "frontier_model_count": 1 if best_model_id else 0,
            "bundles_hydrated": [decision.get("best_bundle_id")] if decision.get("best_bundle_id") else [],
            "universe_matches_candidate_ids": (
                True if best_model_id and best_model_id in (decision.get("candidate_pgs_ids") or []) else None
            ),
            "missing_candidate_pgs_ids": [],
        },
        "decision": {
            "outcome": "DIRECT_HIGH_QUALITY" if best_model_id else "NO_MATCH_FOUND",
            "best_model_id": best_model_id,
            "confidence": decision.get("confidence", "Low"),
            "rationale": decision.get("rationale", ""),
        },
        "recommended_model_ids": decision.get("recommended_model_ids") or [],
    }
    return record


def write_direct_artifacts(
    results: list[dict[str, Any]],
    *,
    condition: str = DIRECT_BASELINE_CONDITION,
    benchmark_family: str,
    run_id: str | None,
    ablation: str,
) -> tuple[Path, Path]:
    results_path = condition_results_json(
        condition,
        benchmark_family=benchmark_family,
        run_id=run_id,
        ablation=ablation,
    )
    recommendations_path = condition_recommendations_json(
        condition,
        benchmark_family=benchmark_family,
        run_id=run_id,
        ablation=ablation,
    )
    results_path.parent.mkdir(parents=True, exist_ok=True)
    recommendations_path.parent.mkdir(parents=True, exist_ok=True)

    recommendations = [
        build_direct_recommendation_record(result, condition=condition)
        for result in results
    ]
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    recommendations_path.write_text(json.dumps(recommendations, indent=2, ensure_ascii=False))
    return results_path, recommendations_path


def run_direct_baseline(
    dossiers: list[CandidateBundleDossier],
    *,
    condition: str = DIRECT_BASELINE_CONDITION,
    workers: int = 1,
    progress: bool = True,
) -> list[dict[str, Any]]:
    if workers <= 1:
        results: list[dict[str, Any]] = []
        for dossier in dossiers:
            selection = invoke_direct_selection(dossier)
            result = build_direct_result_record(dossier, selection, condition=condition)
            results.append(result)
            if progress:
                _print_progress(condition, len(results), len(dossiers), result)
        return results

    results_lock = threading.Lock()
    results: list[dict[str, Any] | None] = [None] * len(dossiers)
    done_count = 0

    def _process(idx: int, dossier: CandidateBundleDossier) -> tuple[int, dict[str, Any]]:
        selection = invoke_direct_selection(dossier)
        return idx, build_direct_result_record(dossier, selection, condition=condition)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_process, i, dossier): i for i, dossier in enumerate(dossiers)}
        for future in as_completed(futures):
            idx, result = future.result()
            with results_lock:
                results[idx] = result
                done_count += 1
                current = done_count
            if progress:
                _print_progress(condition, current, len(dossiers), result)

    return [result for result in results if result is not None]


def _print_progress(condition: str, done: int, total: int, result: dict[str, Any]) -> None:
    target = result.get("target") or {}
    decision = result.get("decision") or {}
    print(
        f"[{condition}] ({done}/{total}) {target.get('target_id')}: "
        f"{decision.get('outcome')} {decision.get('best_cross_trait') or '-'} "
        f"-> {decision.get('best_model_id') or '-'}",
        flush=True,
    )
