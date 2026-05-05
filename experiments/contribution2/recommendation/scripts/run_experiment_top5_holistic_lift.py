"""Production candidate wrapper for c2 top-5 holistic hidden-benchmark rerank.

This is the kept R38-style same-trait PGS-selection harness:

1. Stage 1 reads the existing iterD-final Skill/H2-enriched manifest context and
   emits a primary pick plus a top-5 shortlist.
2. Stage 2 is a separated holistic evaluator that chooses the candidate most
   likely to rank highest in a hidden same-trait PGS performance benchmark.

The wrapper fixes the production-candidate architecture while delegating the
implementation to `run_experiment_pairwise_rerank.py`. It intentionally avoids
trait-specific rules, numeric formulas, disease-category shortcuts, or any new
external evidence channel.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_MANIFEST = (
    Path(__file__).resolve().parent.parent
    / "runs"
    / "minimal-lift-gpt-5.2-t1__89disease__iterD-final-cur89-t1-20260430-234950"
    / "experiment_minimal_lift_batch_manifest.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the kept c2 R38-style top-5 holistic hidden-benchmark harness."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--run-tag", required=True)
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL") or "gpt-5.2")
    parser.add_argument("--workers", type=int, default=30)
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set.")
        return 1

    # Import after argparse so `--help` stays fast and side-effect-light.
    from experiments.contribution2.recommendation.scripts.run_experiment_pairwise_rerank import (  # noqa: E402
        _run_pipeline,
    )

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base_runs = Path(__file__).resolve().parent.parent / "runs"
    safe_model = args.model.replace("/", "-")
    run_dir = base_runs / f"top5-holistic-lift-{safe_model}-t1__89disease__{args.run_tag}-{timestamp}"

    summary = _run_pipeline(
        manifest_path=args.manifest,
        output_run_dir=run_dir,
        model=args.model,
        workers=args.workers,
        top_k=5,
        evaluator="topk_judge",
        objective="hidden_benchmark",
        stage1_objective="support",
    )

    trial_h = summary.get("trial_hit_at_k") or {}
    print("\nFinal trial Hit@k:")
    for k in ["1", "2", "3", "4", "5"]:
        v = trial_h.get(k) or {}
        print(f"  Hit@{k}: hits={v.get('hits')}, eligible={v.get('eligible')}, accuracy={v.get('accuracy')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
