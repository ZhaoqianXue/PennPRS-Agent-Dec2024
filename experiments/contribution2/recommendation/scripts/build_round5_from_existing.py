"""Round 5 — Consistency-routed pairwise reranking, built from existing artifacts.

This script is the *deterministic* post-processor that produced Round 5's
production result. It consumes two existing run directories — iterD-final
(pristine baseline) and Round 1 pairwise-rerank — and routes each ontology to
the higher-quality pick:

  Routing rule:
    if iterD-final's Stage 1 pick == Round 1's Stage 1 best_model_id:
        # The schema augmentation in Round 1's Stage 1 did NOT perturb the
        # primary pick on this ontology. The pairwise rerank was applied to
        # a shortlist anchored at the same primary as iterD-final.
        # Use Round 1's pairwise final pick.
        final_pick = round1_summary.modal_recommendation
    else:
        # Round 1's schema-augmented Stage 1 produced a different primary
        # than iterD-final's pristine Stage 1. The pairwise stage was
        # operating on a perturbed shortlist; we cannot rule out spurious
        # overrules. Fall back to iterD-final's pristine pick.
        final_pick = iterD_final_pick

The router is *advisory consensus*: when two picker prompt variants agree on
the primary, the pairwise rerank is trusted. When they disagree, the iterD
baseline is preserved. This is the "structured uncertainty handling" pattern
from Phase 1 research (Bavaresco et al. 2026: confidence-based routing
improves head-to-head selection by trusting only high-confidence judgments —
agreement across two prompts is a usable confidence proxy).

Why this is deterministic where the fresh-run version was not:
  Empirical observation in this codebase: gpt-5.2 produces non-trivial
  cross-API stochasticity even at temperature=0 + seed=42. iterD-final's
  picks (via OpenAI Batch API) and Stage 0 picks (via chat.completions) on
  the same prompts disagree on ~14 / 89 ontologies. Reproducing the Round 5
  routing therefore requires the *exact* artifacts that anchor the routing,
  not regenerated samples.

Outputs are written into a fresh run directory under recommendation/runs/.
Schema and file naming match the existing minimal-lift / pairwise-rerank
runs so downstream tooling (per-disease report, summary diff, etc.) can
consume them unchanged.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution2.recommendation.scripts import run_experiment_minimal_lift  # noqa: F401
from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain


def _build(
    *,
    iterD_run_dir: Path,
    round1_run_dir: Path,
    output_run_dir: Path,
) -> dict[str, Any]:
    output_run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run directory: {output_run_dir}")

    iterD_summary = json.loads(
        (iterD_run_dir / "experiment_minimal_lift_summary.json").read_text(encoding="utf-8")
    )
    round1_summary = json.loads(
        (round1_run_dir / "experiment_pairwise_rerank_summary.json").read_text(encoding="utf-8")
    )
    round1_stage1 = json.loads(
        (round1_run_dir / "experiment_pairwise_rerank_stage1_results.json").read_text(encoding="utf-8")
    )
    manifest_path = iterD_run_dir / "experiment_minimal_lift_batch_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    iterD_pick = {pd["ontology"]: pd.get("modal_recommendation") for pd in iterD_summary["per_disease"]}
    round1_pick = {pd["ontology"]: pd.get("modal_recommendation") for pd in round1_summary["per_disease"]}
    round1_s1_pick = {
        r["ontology"]: ((r.get("decision") or {}).get("best_model_id"))
        for r in round1_stage1
        if r.get("decision")
    }
    round1_top3 = round1_summary["pairwise_rerank"]["top3_by_ontology"]
    round1_borda = round1_summary["pairwise_rerank"]["borda_scores_by_ontology"]

    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    routing_decision_by_ontology: dict[str, str] = {}
    fallback_count = 0
    consistent_count = 0

    iterD_per_disease = {pd["ontology"]: pd for pd in iterD_summary["per_disease"]}
    round1_per_disease = {pd["ontology"]: pd for pd in round1_summary["per_disease"]}

    for request in manifest["requests"]:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        iD_primary = iterD_pick.get(ontology)
        r1_s1_primary = round1_s1_pick.get(ontology)
        if iD_primary is None and r1_s1_primary is None:
            error_map[custom_id] = "Both iterD and Round 1 Stage 1 missing decisions"
            routing_decision_by_ontology[ontology] = "both_missing"
            continue
        if iD_primary == r1_s1_primary and iD_primary is not None:
            # Consistent → trust Round 1's pairwise rerank output
            final_pick = round1_pick.get(ontology) or iD_primary
            routing_decision_by_ontology[ontology] = "consistent_borda"
            consistent_count += 1
            iD_row = iterD_per_disease.get(ontology) or {}
            r1_row = round1_per_disease.get(ontology) or {}
            outcome = "DIRECT_HIGH_QUALITY"
            confidence = "Moderate"
            rationale = (
                "Consistency-routed pairwise rerank: iterD-final pristine Stage 1 and "
                "Round 1 schema-augmented Stage 1 agree on primary; trusting Round 1's "
                "Borda-aggregated pairwise winner."
            )
            if final_pick != iD_primary:
                rationale = (
                    rationale
                    + f" | Pairwise rerank promoted runner-up {final_pick} over consistent primary {iD_primary}."
                )
        else:
            # Disagree → fall back to iterD-final pristine pick
            final_pick = iD_primary
            routing_decision_by_ontology[ontology] = "fallback_disagree"
            fallback_count += 1
            rationale = (
                f"Consistency-routed fallback: iterD-final pristine Stage 1 picked {iD_primary} "
                f"but Round 1 schema-augmented Stage 1 picked {r1_s1_primary}; the schema "
                f"augmentation perturbed the primary, so we fall back to the pristine baseline."
            )
            outcome = "DIRECT_HIGH_QUALITY"
            confidence = "Moderate"

        parsed_outputs[custom_id] = {
            "custom_id": custom_id,
            "decisions": [{
                "outcome": outcome,
                "best_model_id": final_pick,
                "confidence": confidence,
                "rationale": rationale,
            }],
            "error": None,
        }

    # Wire output paths
    without_domain.RESULTS_JSON = output_run_dir / "experiment_consistency_routed_results.json"
    without_domain.SUMMARY_JSON = output_run_dir / "experiment_consistency_routed_summary.json"
    without_domain.REPORT_MD = output_run_dir / "experiment_consistency_routed_report.md"
    without_domain.BATCH_REQUESTS_JSONL = output_run_dir / "experiment_consistency_routed_batch_requests.jsonl"
    without_domain.BATCH_MANIFEST_JSON = output_run_dir / "experiment_consistency_routed_batch_manifest.json"
    without_domain.BATCH_JOB_JSON = output_run_dir / "experiment_consistency_routed_batch_job.json"
    without_domain.BATCH_OUTPUT_JSONL = output_run_dir / "experiment_consistency_routed_batch_output.jsonl"
    without_domain.BATCH_ERROR_JSONL = output_run_dir / "experiment_consistency_routed_batch_errors.jsonl"
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
    summary["execution_mode"] = "consistency_routed_post_processing_of_iterD_and_round1"
    summary["consistency_routed"] = {
        "iterD_run_dir": str(iterD_run_dir),
        "round1_run_dir": str(round1_run_dir),
        "consistent_count": consistent_count,
        "fallback_count": fallback_count,
        "routing_decision_by_ontology": routing_decision_by_ontology,
        "round1_top3_by_ontology": round1_top3,
        "round1_borda_scores_by_ontology": round1_borda,
    }

    without_domain._write_json(without_domain.RESULTS_JSON, trial_results)
    without_domain._write_json(without_domain.SUMMARY_JSON, summary)
    print(f"\nResults: {without_domain.RESULTS_JSON}")
    print(f"Summary: {without_domain.SUMMARY_JSON}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Round 5 result deterministically from iterD + Round 1 artifacts")
    parser.add_argument("--iterD-run-dir", type=str, required=True)
    parser.add_argument("--round1-run-dir", type=str, required=True)
    parser.add_argument("--run-tag", type=str, required=True)
    parser.add_argument("--model", type=str, default="gpt-5.2")
    args = parser.parse_args()

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base_runs = Path(__file__).parent.parent / "runs"
    run_dir_name = f"consistency-routed-pairwise-{args.model}-t1__89disease__{args.run_tag}-{timestamp}"
    output_run_dir = base_runs / run_dir_name

    summary = _build(
        iterD_run_dir=Path(args.iterD_run_dir),
        round1_run_dir=Path(args.round1_run_dir),
        output_run_dir=output_run_dir,
    )
    trial_h = summary.get("trial_hit_at_k") or {}
    print("\nFinal trial Hit@k:")
    for k in ["1", "2", "3", "4", "5"]:
        v = trial_h.get(k) or {}
        print(f"  Hit@{k}: hits={v.get('hits')}, eligible={v.get('eligible')}, "
              f"accuracy={v.get('accuracy')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
