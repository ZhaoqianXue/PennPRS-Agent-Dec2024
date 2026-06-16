"""Select 5 debug targets by failure-mode, not by trait name.

Reads the latest evaluation's per-target report and samples one target
per diagnostic condition (see REFACTOR_PLAN.md §9). The selection is
deterministic (`seed=42`) so the debug set is stable across iterations
but **not** hardcoded to specific trait IDs — re-running against a new
evaluation snapshot yields a new, still-blind selection.

Usage:
    python -m experiments.contribution3.transfer.scripts.pick_debug_targets \
        --eval-dir experiments/contribution3/transfer/runs/tool_calling_agent/unified/evaluation__online_opt_next_20260422_203403 \
        --output experiments/contribution3/transfer/scripts/debug_targets.json

Outputs a JSON file with five `{target_id, target_label, picked_for, ...}`
entries. The agent code never imports this file; it is consumed only by
the debug CLI flag.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


SELECTION_CONDITIONS: list[dict[str, Any]] = [
    {
        "key": "regression_guard",
        "description": "Currently succeeding — oracle already in model frontier",
        "filter": lambda row: _as_bool(row.get("oracle_in_model_frontier")),
    },
    {
        "key": "lost_at_bundle_posterior",
        "description": "Oracle entered probe pool but was dropped before reaching the supporting-bundle set",
        "filter": lambda row: _as_bool(row.get("oracle_in_probe_pool"))
        and not _as_bool(row.get("oracle_in_supporting_bundles")),
    },
    {
        "key": "lost_at_model_frontier",
        "description": "Oracle reached supporting bundles but not the final model frontier",
        "filter": lambda row: _as_bool(row.get("oracle_in_supporting_bundles"))
        and not _as_bool(row.get("oracle_in_model_frontier")),
    },
    {
        "key": "oracle_outside_probe_pool",
        "description": "Oracle not in probe pool (retrieval-bound; honest limit for biology retrieval)",
        "filter": lambda row: not _as_bool(row.get("oracle_in_probe_pool")),
    },
    {
        "key": "cross_modality",
        "description": "Non-primary input type (e.g. endophenotype / continuous target)",
        "filter": lambda row: str(row.get("input_type") or "").strip().upper() not in {"A", ""}
        or str(row.get("target_source") or "").strip().lower() in {"nontarget_pgs", "extend_trait"},
    },
]


def _as_bool(value: Any, *, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "t", "y"}:
        return True
    if text in {"false", "0", "no", "f", "n"}:
        return False
    return default


def _locate_per_target_csv(eval_dir: Path) -> Path:
    for name in (
        "per_target_report.csv",
        "per_target_report.tsv",
        "all-tools__end_to_end_eval_detail.csv",
    ):
        candidate = eval_dir / name
        if candidate.exists():
            return candidate
    # Fall back to any `*_eval_detail.csv` the evaluator emits.
    for candidate in sorted(eval_dir.glob("*__end_to_end_eval_detail.csv")):
        return candidate
    raise FileNotFoundError(
        f"No per_target_report.csv or *eval_detail.csv in {eval_dir} "
        "— cannot pick debug targets"
    )


def _read_rows(csv_path: Path) -> list[dict[str, Any]]:
    with csv_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _pick_one(
    rows: list[dict[str, Any]],
    predicate,
    rng: random.Random,
    already_picked: set[str],
) -> Optional[dict[str, Any]]:
    pool = [r for r in rows if r.get("target_id") not in already_picked and predicate(r)]
    if not pool:
        return None
    return rng.choice(pool)


def pick_debug_targets(
    eval_dir: Path,
    *,
    seed: int = 42,
) -> list[dict[str, Any]]:
    csv_path = _locate_per_target_csv(eval_dir)
    rows = _read_rows(csv_path)
    if not rows:
        raise ValueError(f"Empty per-target report: {csv_path}")
    rng = random.Random(seed)
    picks: list[dict[str, Any]] = []
    already: set[str] = set()
    for condition in SELECTION_CONDITIONS:
        row = _pick_one(rows, condition["filter"], rng, already)
        if row is None:
            picks.append(
                {
                    "picked_for": condition["key"],
                    "description": condition["description"],
                    "status": "no_matching_target",
                    "target_id": None,
                    "target_label": None,
                }
            )
            continue
        target_id = str(row.get("target_id") or "").strip()
        already.add(target_id)
        picks.append(
            {
                "picked_for": condition["key"],
                "description": condition["description"],
                "status": "picked",
                "target_id": target_id,
                "target_label": str(row.get("target_description") or row.get("target_label") or "").strip(),
                "oracle_in_probe_pool": row.get("oracle_in_probe_pool"),
                "oracle_in_supporting_bundles": row.get("oracle_in_supporting_bundles"),
                "oracle_in_model_frontier": row.get("oracle_in_model_frontier"),
                "benchmark_family": row.get("benchmark_family"),
                "input_type": row.get("input_type"),
                "target_source": row.get("target_source"),
                "selected_model_rank_fraction": row.get("selected_model_rank_fraction"),
                "benchmark_top_model_id": row.get("benchmark_top_model_id"),
            }
        )
    return picks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    picks = pick_debug_targets(args.eval_dir, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(picks, indent=2, ensure_ascii=False))
    print(f"Wrote {len(picks)} debug target picks to {args.output}")
    for p in picks:
        print(f"  [{p['picked_for']}] {p.get('target_id') or '-'} {p.get('target_label') or ''}")


if __name__ == "__main__":
    main()
