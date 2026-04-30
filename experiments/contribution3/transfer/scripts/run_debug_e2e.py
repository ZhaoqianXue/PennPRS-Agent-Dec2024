"""P7 gate: end-to-end run over the 5 debug targets.

Loads the dossiers for the 5 picked debug targets, runs the full
five-stage LLM-led transfer agent for each, and reports:
  - oracle_in_probe_pool  (retrieval ceiling)
  - oracle_in_bundle_ranking  (post-Judge)
  - oracle_in_model_frontier  (post-Pick + Critic)
  - selected_model_rank_fraction  (from the benchmark ground-truth CSV)
  - top_0_5pct / top_2_5pct / top_5pct / top_10pct  (aggregate across
    the N debug targets)
  - halt_reason distribution

No full-80 run; this is the gate before scaling.

Usage:
  python -m experiments.contribution3.transfer.scripts.run_debug_e2e \
      --debug-json experiments/contribution3/transfer/scripts/debug_targets.json \
      --output experiments/contribution3/transfer/scripts/debug_e2e_results.json
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.common import (  # noqa: E402
    _normalize_target_source,
    load_benchmark_target_selection,
    load_candidate_dossiers,
    target_dossiers_json,
)
from experiments.contribution3.transfer.driver import (  # noqa: E402
    run_cross_trait_agent,
)


def _resolve_target_source(target_id: str, benchmark_family: str) -> str:
    """Determine 'rootcode_main_analysis' vs 'extend_trait' for a target_id.

    The benchmark selection CSV carries the `target_source` column which
    decides which AUC matrix to load. We look the row up by input_icd.
    """
    try:
        df = load_benchmark_target_selection(benchmark_family=benchmark_family, selected_only=True)
    except Exception:
        return "rootcode_main_analysis"
    row = df[df["input_icd"].astype(str).str.strip() == str(target_id).strip()]
    if row.empty:
        return "rootcode_main_analysis"
    return _normalize_target_source(row.iloc[0].get("target_source"))

logger = logging.getLogger("debug_e2e")


def _load_debug_targets(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text())


def _find_oracle_bundle_id(dossier, oracle_pgs: str) -> str | None:
    for b in dossier.candidates:
        if oracle_pgs in (b.candidate_pgs_ids or []):
            return b.bundle_id
    return None


def _rank_fraction_from_matrix(
    selected_pgs: str | None,
    target_id: str,
    target_source: str,
) -> tuple[float | None, int | None, str | None]:
    """Compute (rank_fraction, candidate_count, top_pgs_id) via AOU AUC matrix.

    Uses the same evaluator-side AUC matrices so the numbers are
    directly comparable with the production `evaluate_end_to_end.py`.
    """
    from experiments.contribution3.transfer.eval.evaluate_end_to_end import (  # local import to avoid import-time overhead
        _build_full_matrix_ranking,
    )
    try:
        ranked_ids, rank_map, _auc_by_id = _build_full_matrix_ranking(target_id, target_source)
    except (KeyError, FileNotFoundError):
        return None, None, None
    top_pgs = ranked_ids[0] if ranked_ids else None
    if not selected_pgs:
        return None, len(ranked_ids), top_pgs
    pgs_upper = selected_pgs.upper()
    rank = rank_map.get(pgs_upper)
    if rank is None or not ranked_ids:
        return None, len(ranked_ids), top_pgs
    return rank / len(ranked_ids), len(ranked_ids), top_pgs


def run(args: argparse.Namespace) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    debug = _load_debug_targets(Path(args.debug_json))
    dossiers = load_candidate_dossiers(target_dossiers_json(args.benchmark_family))
    by_id = {d.target.target_id: d for d in dossiers}

    results: list[dict[str, Any]] = []
    halt_counter: Counter[str] = Counter()
    per_pct: dict[str, float] = {
        "top_0_5pct": 0.0,
        "top_2_5pct": 0.0,
        "top_5pct": 0.0,
        "top_10pct": 0.0,
    }
    valid_targets = 0

    for pick in debug:
        target_id = pick.get("target_id")
        oracle_pgs = (pick.get("benchmark_top_model_id") or "").strip().upper()
        if not target_id or not oracle_pgs:
            continue
        dossier = by_id.get(target_id)
        if dossier is None:
            logger.warning("no dossier for target %s", target_id)
            continue
        oracle_bundle = _find_oracle_bundle_id(dossier, oracle_pgs)
        probe_has_oracle = oracle_bundle is not None  # by construction here
        t0 = time.time()
        decision_blob = run_cross_trait_agent(
            dossier=dossier,
            condition=args.condition,
            benchmark_family=args.benchmark_family,
            ablation="full",
        )
        elapsed = time.time() - t0

        decision = decision_blob.get("decision") or {}
        trace = decision_blob.get("trace") or {}
        gather = trace.get("gather") or {}
        halt_reason = str(gather.get("halt_reason") or "not_applicable")
        halt_counter[halt_reason] += 1

        bundle_ranking = (trace.get("judge") or {}).get("ranked_bundles") or []
        bundle_ranking_ids = [b.get("bundle_id") for b in bundle_ranking]
        oracle_in_bundle_ranking = (
            oracle_bundle is not None and oracle_bundle in bundle_ranking_ids
        )
        model_frontier = decision.get("model_frontier") or []
        frontier_ids = [str(m.get("pgs_id")).upper() for m in model_frontier if m.get("pgs_id")]
        oracle_in_model_frontier = oracle_pgs in frontier_ids
        primary_pgs = (decision.get("best_model_id") or "").upper() or None

        target_source = _resolve_target_source(target_id, args.benchmark_family)
        frac, candidate_count, top_pgs = _rank_fraction_from_matrix(
            primary_pgs, target_id, target_source
        )
        valid_targets += 1 if frac is not None else 0
        if frac is not None:
            if frac <= 0.005:
                per_pct["top_0_5pct"] += 1
            if frac <= 0.025:
                per_pct["top_2_5pct"] += 1
            if frac <= 0.05:
                per_pct["top_5pct"] += 1
            if frac <= 0.10:
                per_pct["top_10pct"] += 1

        row = {
            "target_id": target_id,
            "picked_for": pick.get("picked_for"),
            "target_label": dossier.target.target_label,
            "oracle_pgs_id_ground_truth": top_pgs,
            "benchmark_top_model_id_hint": oracle_pgs,
            "oracle_bundle_id": oracle_bundle,
            "candidate_count": candidate_count,
            "oracle_in_probe_pool": probe_has_oracle,
            "oracle_in_bundle_ranking": oracle_in_bundle_ranking,
            "oracle_in_model_frontier": oracle_in_model_frontier,
            "primary_pgs_id": primary_pgs,
            "primary_rank_fraction": frac,
            "frontier_ids": frontier_ids,
            "halt_reason": halt_reason,
            "elapsed_s": round(elapsed, 1),
            "outcome": decision.get("outcome"),
        }
        logger.info(
            "[P7] %s %s oracle=%s primary=%s frac=%s hit_bundle=%s hit_frontier=%s halt=%s",
            target_id,
            pick.get("picked_for"),
            oracle_pgs,
            primary_pgs,
            f"{frac:.4f}" if frac is not None else "-",
            oracle_in_bundle_ranking,
            oracle_in_model_frontier,
            halt_reason,
        )
        results.append(row)

    n = max(1, valid_targets)
    aggregate = {
        k: round(v / n, 4) for k, v in per_pct.items()
    }
    summary = {
        "n_targets": len(results),
        "n_rank_fraction_computed": valid_targets,
        "halt_reason_counts": dict(halt_counter),
        "oracle_in_probe_pool_rate": round(
            sum(1 for r in results if r["oracle_in_probe_pool"]) / max(1, len(results)), 4
        ),
        "oracle_in_bundle_ranking_rate": round(
            sum(1 for r in results if r["oracle_in_bundle_ranking"]) / max(1, len(results)), 4
        ),
        "oracle_in_model_frontier_rate": round(
            sum(1 for r in results if r["oracle_in_model_frontier"]) / max(1, len(results)), 4
        ),
        "top_pct_on_primary": aggregate,
    }

    outpath = Path(args.output)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps({"summary": summary, "per_target": results}, indent=2, ensure_ascii=False, default=str))
    logger.info("=== SUMMARY ===")
    logger.info(json.dumps(summary, indent=2))
    logger.info("wrote %s", outpath)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--debug-json", required=True, type=str)
    p.add_argument("--output", required=True, type=str)
    p.add_argument("--benchmark-family", default="unified")
    p.add_argument("--condition", default="all-tools")
    args = p.parse_args()
    run(args)


if __name__ == "__main__":
    main()
