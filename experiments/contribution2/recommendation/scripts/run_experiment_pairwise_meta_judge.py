"""Pairwise meta-judge postprocessor for Contribution2.

This runner consumes an existing pairwise-rerank run, keeps its Stage 1 shortlist
and Stage 2 pairwise judgments, then adds a bounded meta-judge:

  Stage 3: one LLM call per ontology sees:
    - the Stage 1 ranked shortlist
    - visible candidate records for the shortlist
    - all pairwise winners, confidence labels, and rationales
    - the same skill + heritability domain_knowledge from the original manifest

The meta-judge chooses only from the shortlist. It cannot introduce a new PGS and
does not use benchmark labels. This tests whether a single aggregator can resolve
local pairwise inconsistencies without trait-specific rules or numeric formulas.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI
from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_minimal_lift  # noqa: F401
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain
from src.server.core.within_prompts import WITHIN_META_JUDGE_SYSTEM_PROMPT


class MetaJudgment(BaseModel):
    winner_model_id: str
    confidence: str
    rationale: str


META_JUDGE_SYSTEM_PROMPT = WITHIN_META_JUDGE_SYSTEM_PROMPT


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "meta_judgment",
            "strict": True,
            "schema": to_strict_json_schema(MetaJudgment),
        },
    }


def _llm_call(client: OpenAI, *, model: str, messages: list[dict[str, str]]) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format=_response_format(),
        temperature=0,
        seed=42,
    )
    content = response.choices[0].message.content
    if isinstance(content, list):
        return "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
        ).strip()
    return (content or "").strip()


def _candidate_summary_lookup(disease_metadata: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for row in disease_metadata:
        ontology = row["ontology"]
        out[ontology] = {}
        for summary in row.get("candidate_models_visible_to_llm") or []:
            pgs_id = summary.get("pgs_id") or summary.get("id")
            if pgs_id:
                out[ontology][pgs_id] = summary
    return out


def _domain_by_ontology(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for request in manifest["requests"]:
        ontology = request["ontology"]
        if ontology in out:
            continue
        original_user = request["request"]["body"]["messages"][1]["content"]
        marker = "Context:\n"
        idx = original_user.find(marker)
        if idx < 0:
            out[ontology] = {}
            continue
        try:
            ctx = json.loads(original_user[idx + len(marker):])
            out[ontology] = ctx.get("domain_knowledge") or {}
        except Exception:
            out[ontology] = {}
    return out


def _run_meta_one(
    *,
    client: OpenAI,
    model: str,
    ontology: str,
    ranked_candidate_ids: list[str],
    candidate_summaries: dict[str, dict[str, Any]],
    pairwise_results: list[dict[str, Any]],
    domain_knowledge: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "target_trait": ontology,
        "ranked_candidate_ids": ranked_candidate_ids,
        "candidates": [
            candidate_summaries.get(pgs_id, {"pgs_id": pgs_id, "missing": True})
            for pgs_id in ranked_candidate_ids
        ],
        "pairwise_judgments": pairwise_results,
        "domain_knowledge": domain_knowledge,
    }
    messages = [
        {"role": "system", "content": META_JUDGE_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Resolve the shortlist below. winner_model_id must be one of "
                "ranked_candidate_ids.\n\n"
                f"Context:\n{json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}"
            ),
        },
    ]
    try:
        content = _llm_call(client, model=model, messages=messages)
        judgment = MetaJudgment.model_validate_json(content)
        winner = judgment.winner_model_id.strip()
        if winner not in set(ranked_candidate_ids):
            return {
                "ontology": ontology,
                "winner_model_id": None,
                "confidence": judgment.confidence,
                "rationale": judgment.rationale,
                "error": f"winner '{winner}' not in ranked_candidate_ids",
            }
        return {
            "ontology": ontology,
            "winner_model_id": winner,
            "confidence": judgment.confidence,
            "rationale": judgment.rationale,
            "error": None,
        }
    except Exception as exc:
        return {
            "ontology": ontology,
            "winner_model_id": None,
            "confidence": None,
            "rationale": None,
            "error": f"MetaJudge {type(exc).__name__}: {exc}",
        }


def _build(
    *,
    source_run_dir: Path,
    manifest_path: Path,
    output_run_dir: Path,
    model: str,
    workers: int,
) -> dict[str, Any]:
    output_run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run directory: {output_run_dir}")
    print(f"Source pairwise run: {source_run_dir}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_summary = json.loads(
        (source_run_dir / "experiment_pairwise_rerank_summary.json").read_text(encoding="utf-8")
    )
    source_stage1 = json.loads(
        (source_run_dir / "experiment_pairwise_rerank_stage1_results.json").read_text(encoding="utf-8")
    )
    source_stage2 = json.loads(
        (source_run_dir / "experiment_pairwise_rerank_stage2_results.json").read_text(encoding="utf-8")
    )

    ranked_by_ontology = (
        source_summary.get("pairwise_rerank", {}).get("ranked_candidates_by_ontology")
        or source_summary.get("pairwise_rerank", {}).get("top3_by_ontology")
        or {}
    )
    pairwise_by_ontology: dict[str, list[dict[str, Any]]] = {}
    for row in source_stage2:
        pairwise_by_ontology.setdefault(row["ontology"], []).append(row)

    candidate_by_ontology = _candidate_summary_lookup(manifest["disease_metadata"])
    domain_by_ontology = _domain_by_ontology(manifest)
    client = _client()

    print(f"\n=== Stage 3 (meta-judge) — {len(ranked_by_ontology)} ontologies, workers={workers} ===")
    meta_results: dict[str, dict[str, Any]] = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                _run_meta_one,
                client=client,
                model=model,
                ontology=ontology,
                ranked_candidate_ids=list(ranked_ids or []),
                candidate_summaries=candidate_by_ontology.get(ontology, {}),
                pairwise_results=pairwise_by_ontology.get(ontology, []),
                domain_knowledge=domain_by_ontology.get(ontology, {}),
            ): ontology
            for ontology, ranked_ids in ranked_by_ontology.items()
            if len(ranked_ids or []) >= 2
        }
        done = 0
        for future in as_completed(futures):
            res = future.result()
            meta_results[res["ontology"]] = res
            done += 1
            status = "ok" if res["error"] is None else "ERR"
            print(f"  [meta {done}/{len(futures)}] {status} {res['ontology']} -> {res.get('winner_model_id')}")
    print(f"Stage 3 elapsed: {time.time() - t0:.1f}s")
    (output_run_dir / "experiment_pairwise_meta_judge_stage3_results.json").write_text(
        json.dumps(list(meta_results.values()), indent=2),
        encoding="utf-8",
    )

    stage1_by_ontology = {
        row["ontology"]: row.get("decision") or {}
        for row in source_stage1
        if row.get("decision")
    }

    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    for request in manifest["requests"]:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        ranked = ranked_by_ontology.get(ontology) or []
        stage1_decision = stage1_by_ontology.get(ontology) or {}
        meta = meta_results.get(ontology) or {}
        final_pick: Optional[str] = meta.get("winner_model_id")
        if not final_pick:
            final_pick = stage1_decision.get("best_model_id") or (ranked[0] if ranked else None)
        if not final_pick:
            error_map[custom_id] = meta.get("error") or "No final pick"
            continue
        parsed_outputs[custom_id] = {
            "custom_id": custom_id,
            "decisions": [{
                "outcome": stage1_decision.get("outcome") or "DIRECT_HIGH_QUALITY",
                "best_model_id": final_pick,
                "confidence": meta.get("confidence") or "Moderate",
                "rationale": meta.get("rationale") or "Pairwise meta-judge fallback.",
            }],
            "error": None,
        }

    without_domain.RESULTS_JSON = output_run_dir / "experiment_pairwise_meta_judge_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_pairwise_meta_judge_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_pairwise_meta_judge_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_pairwise_meta_judge_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_pairwise_meta_judge_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_pairwise_meta_judge_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_pairwise_meta_judge_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_pairwise_meta_judge_batch_errors.jsonl"
    without_domain.ACTIVE_RUN_DIR = output_run_dir
    without_domain._configure_benchmark_sources(
        union_csv=manifest.get("union_csv"),
        ground_truth_dir=manifest.get("ground_truth_dir"),
    )
    trial_results, summary = without_domain._build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )
    summary["execution_mode"] = "pairwise_meta_judge_chat_completions"
    summary["pairwise_meta_judge"] = {
        "source_run_dir": str(source_run_dir),
        "stage3_count": len(meta_results),
        "ranked_candidates_by_ontology": ranked_by_ontology,
    }

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)
    print(f"\nResults: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Meta-judge over an existing pairwise-rerank run")
    parser.add_argument("--source-run-dir", type=str, required=True)
    parser.add_argument("--manifest", type=str, required=True)
    parser.add_argument("--run-tag", type=str, required=True)
    parser.add_argument("--model", type=str, default="gpt-5.2")
    parser.add_argument("--workers", type=int, default=30)
    args = parser.parse_args()

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base_runs = Path(__file__).parent.parent / "runs"
    run_dir_name = f"pairwise-meta-judge-{args.model}-t1__89disease__{args.run_tag}-{timestamp}"
    output_run_dir = base_runs / run_dir_name

    summary = _build(
        source_run_dir=Path(args.source_run_dir),
        manifest_path=Path(args.manifest),
        output_run_dir=output_run_dir,
        model=args.model,
        workers=args.workers,
    )
    trial_h = summary.get("trial_hit_at_k") or {}
    print("\nFinal trial Hit@k:")
    for k in ["1", "2", "3", "4", "5"]:
        v = trial_h.get(k) or {}
        print(f"  Hit@{k}: hits={v.get('hits')}, eligible={v.get('eligible')}, accuracy={v.get('accuracy')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
