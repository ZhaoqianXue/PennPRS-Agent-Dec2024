"""Tool-ablation pilot driver: loop over tool/skill ablations and aggregate results.

Conditions (all run on the unified benchmark family with --condition all-tools):
  - full              -> baseline (h2/OT/GC/biology on; skill on)
  - add_*             -> skill on; start from no_all_tools and enable only
                         the named evidence channel(s)
  - no_h2_tool        -> get_heritability disabled
  - no_ot_tool        -> get_open_targets_overlap disabled
  - no_gc_tool        -> genetic_correlation_batch_estimator disabled
  - no_biology_tool   -> Scout-time biology_retrieve_related_bundles disabled (only entry)
  - no_skill          -> cross_trait_domain_knowledge KB injection disabled (tools still on)
  - no_all_tools      -> all evidence tools off (skill still on)

For each condition: runs the agent, derives Stage 2 recommendations, then
runs evaluate_end_to_end_condition. Finally aggregates a single comparison
table (CSV + Markdown) into the run output directory.

Designed for 20-target development pilots and the final full-family run.

Usage:
    python -m experiments.contribution3.transfer.batch.run_tool_ablation_pilot \
        --target-ids B20,D05,D24,D25,F11,F31,F33,G56,I16,J41,K02,K42,K81,L02,M1A,M86,N04,N10,N40,N91 \
        --run-id pilot_$(date +%Y%m%d_%H%M%S) \
        --workers 20

If --target-ids is omitted, the full benchmark family is used.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.common import (
    benchmark_ablation_run_dir,
    condition_results_json,
    evaluation_dir,
    normalize_transfer_ablation,
)
from experiments.contribution3.transfer.driver import TRANSFER_ABLATIONS

DEFAULT_ABLATIONS = (
    "no_all_tools",
    "add_h2_tool",
    "add_gc_tool",
    "add_h2_gc_tools",
    "full",
    "all_evidence_tools",
)

CONDITION = "all-tools"
BENCHMARK_FAMILY = "unified"


def _runner(args: list[str]) -> int:
    """Run a subprocess invocation of run_batch.py and stream output."""
    cmd = [sys.executable, "-m", "experiments.contribution3.transfer.batch.run_batch", *args]
    print(f"\n$ {' '.join(cmd)}\n", flush=True)
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return proc.returncode


def _split_ablation_list(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return DEFAULT_ABLATIONS
    values: list[str] = []
    seen: set[str] = set()
    for item in str(raw).split(","):
        label = normalize_transfer_ablation(item)
        if not label or label in seen:
            continue
        if label not in TRANSFER_ABLATIONS:
            raise ValueError(
                f"Unsupported ablation: {item}. Expected one of {', '.join(TRANSFER_ABLATIONS)}."
            )
        seen.add(label)
        values.append(label)
    return tuple(values) or DEFAULT_ABLATIONS


def run_one(ablation: str, *, target_ids: str, run_id: str, workers: int) -> bool:
    """Execute the run -> recommend -> evaluate triplet for one ablation."""
    common = [
        "--benchmark-family", BENCHMARK_FAMILY,
        "--condition", CONDITION,
        "--ablation", ablation,
        "--run-id", run_id,
    ]

    rc = _runner([
        "run", *common,
        "--workers", str(workers),
        *(["--target-ids", target_ids] if target_ids else []),
    ])
    if rc != 0:
        print(f"[{ablation}] run step failed (rc={rc})", flush=True)
        return False

    rc = _runner(["recommend", *common])
    if rc != 0:
        print(f"[{ablation}] recommend step failed (rc={rc})", flush=True)
        return False

    rc = _runner(["evaluate-end-to-end", *common])
    if rc != 0:
        print(f"[{ablation}] evaluate step failed (rc={rc})", flush=True)
        return False

    return True


def _load_summary(ablation: str, run_id: str) -> Optional[dict]:
    eval_dir = evaluation_dir(BENCHMARK_FAMILY, run_id=run_id, ablation=ablation)
    summary_path = eval_dir / f"{CONDITION}__end_to_end_eval_summary.json"
    if not summary_path.exists():
        print(f"[{ablation}] missing summary file: {summary_path}", flush=True)
        return None
    return json.loads(summary_path.read_text())


def _load_detail_rows(ablation: str, run_id: str) -> list[dict]:
    eval_dir = evaluation_dir(BENCHMARK_FAMILY, run_id=run_id, ablation=ablation)
    detail_path = eval_dir / f"{CONDITION}__end_to_end_eval_detail.csv"
    if not detail_path.exists():
        print(f"[{ablation}] missing detail file: {detail_path}", flush=True)
        return []
    with open(detail_path, newline="") as fh:
        return list(csv.DictReader(fh))


def _load_results(ablation: str, run_id: str) -> Optional[list]:
    results_path = condition_results_json(
        condition=CONDITION,
        benchmark_family=BENCHMARK_FAMILY,
        run_id=run_id,
        ablation=ablation,
    )
    if not results_path.exists():
        print(f"[{ablation}] missing results file: {results_path}", flush=True)
        return None
    return json.loads(results_path.read_text())


def _aggregate_tool_call_counts(results: list) -> dict[str, dict]:
    """Per ablation, sum tool_call_counts across all targets + count populated registry slots."""
    totals: dict[str, int] = {}
    targets_using: dict[str, int] = {}
    for entry in results:
        trace = entry.get("trace", {})
        counts = trace.get("tool_call_counts") or {}
        for tool, n in counts.items():
            totals[tool] = totals.get(tool, 0) + int(n)
            if int(n) > 0:
                targets_using[tool] = targets_using.get(tool, 0) + 1
    return {
        "n_targets": len(results),
        "tool_call_total": totals,
        "n_targets_using_tool": targets_using,
    }


def _safe_float(value) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _conditional_eval_metrics(detail_rows: list[dict]) -> dict[str, float | int | None]:
    """Metrics over actually evaluated targets only.

    Official summaries keep the full benchmark denominator, which is right for
    final 80-target reporting but obscures 20-target pilot comparisons. These
    conditional fields make the development subset's hit counts/rates explicit.
    """
    eval_rows = [r for r in detail_rows if r.get("status") == "evaluated"]
    n_eval = len(eval_rows)
    out: dict[str, float | int | None] = {"conditional_n_evaluated": n_eval}
    if not n_eval:
        return out

    gprs = [_safe_float(r.get("selected_model_gpr")) for r in eval_rows]
    regrets = [_safe_float(r.get("absolute_auc_regret")) for r in eval_rows]
    gprs = [v for v in gprs if v is not None]
    regrets = [v for v in regrets if v is not None]
    out["conditional_mean_gpr"] = (sum(gprs) / len(gprs)) if gprs else None
    out["conditional_mean_auc_regret"] = (sum(regrets) / len(regrets)) if regrets else None

    pct_defs = [
        ("top_0_5pct", 0.005),
        ("top_1pct", 0.010),
        ("top_1_5pct", 0.015),
        ("top_2pct", 0.020),
        ("top_2_5pct", 0.025),
    ]
    rank_fracs = [_safe_float(r.get("selected_model_rank_fraction")) for r in eval_rows]
    for key, pct in pct_defs:
        count = sum(1 for v in rank_fracs if v is not None and v <= pct)
        out[f"conditional_{key}_count"] = count
        out[f"conditional_{key}"] = count / n_eval
    return out


def _build_comparison_table(
    ablations: tuple[str, ...],
    summaries: dict[str, dict],
    tool_stats: dict[str, dict],
    conditional_stats: dict[str, dict],
) -> tuple[str, list[dict]]:
    """Return (markdown_table, list-of-rows-for-csv)."""
    rows: list[dict] = []
    for ablation in ablations:
        s = summaries.get(ablation) or {}
        official = (s.get("official_metrics") or {})
        hit_at = (official.get("hit_at_percent") or {})
        legacy = ((s.get("diagnostics") or {}).get("legacy_hit_at_percent") or {})
        ts = tool_stats.get(ablation) or {}
        cs = conditional_stats.get(ablation) or {}
        row = {
            "ablation": ablation,
            "n_targets": s.get("n_targets"),
            "n_evaluated": s.get("n_evaluated"),
            "mean_gpr": official.get("mean_gpr"),
            "top_0.5pct": hit_at.get("top_0_5pct"),
            "top_1pct":   hit_at.get("top_1pct"),
            "top_1.5pct": hit_at.get("top_1_5pct"),
            "top_2pct":   hit_at.get("top_2pct"),
            "top_2.5pct": hit_at.get("top_2_5pct"),
            "top_5pct":   legacy.get("top_5pct"),
            "top_10pct":  legacy.get("top_10pct"),
            "top_25pct":  legacy.get("top_25pct"),
            "cond_mean_gpr": cs.get("conditional_mean_gpr"),
            "cond_top_0.5_count": cs.get("conditional_top_0_5pct_count"),
            "cond_top_0.5": cs.get("conditional_top_0_5pct"),
            "cond_top_1_count": cs.get("conditional_top_1pct_count"),
            "cond_top_1": cs.get("conditional_top_1pct"),
            "cond_top_1.5_count": cs.get("conditional_top_1_5pct_count"),
            "cond_top_1.5": cs.get("conditional_top_1_5pct"),
            "cond_top_2_count": cs.get("conditional_top_2pct_count"),
            "cond_top_2": cs.get("conditional_top_2pct"),
            "cond_top_2.5_count": cs.get("conditional_top_2_5pct_count"),
            "cond_top_2.5": cs.get("conditional_top_2_5pct"),
            "tool_calls_h2":  (ts.get("tool_call_total") or {}).get("get_heritability", 0),
            "tool_calls_ot":  (ts.get("tool_call_total") or {}).get("get_open_targets_overlap", 0),
            "tool_calls_gc":  (ts.get("tool_call_total") or {}).get("genetic_correlation_batch_estimator", 0),
            "tool_calls_bio_scout":  (ts.get("tool_call_total") or {}).get("biology_retrieve_related_bundles", 0),
        }
        rows.append(row)

    headers = list(rows[0].keys()) if rows else []
    md_lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for r in rows:
        md_lines.append("| " + " | ".join(str(r[h]) if r[h] is not None else "-" for h in headers) + " |")
    return "\n".join(md_lines), rows


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target-ids", default="",
                   help="Comma-separated target IDs (default: full benchmark family).")
    p.add_argument("--run-id", required=True)
    p.add_argument("--workers", type=int, default=20)
    p.add_argument("--ablations", default="",
                   help="Comma-separated ablation labels (default: additive single-tool suite).")
    p.add_argument("--skip-run", action="store_true",
                   help="Skip the agent runs, only re-aggregate existing artifacts.")
    args = p.parse_args()
    ablations = _split_ablation_list(args.ablations)

    print(f"=== Tool-ablation pilot: run_id={args.run_id}", flush=True)
    print(f"=== Conditions: {ablations}", flush=True)
    print(f"=== Target IDs: {args.target_ids or '<full benchmark family>'}", flush=True)
    print(f"=== Workers: {args.workers}", flush=True)

    if not args.skip_run:
        for ablation in ablations:
            t0 = time.time()
            ok = run_one(
                ablation,
                target_ids=args.target_ids,
                run_id=args.run_id,
                workers=args.workers,
            )
            elapsed = time.time() - t0
            print(f"\n=== [{ablation}] {'OK' if ok else 'FAIL'} in {elapsed:.1f}s\n", flush=True)
            if not ok:
                print("Pilot aborted due to failure above.", flush=True)
                sys.exit(1)

    # Aggregate
    summaries = {ab: _load_summary(ab, args.run_id) for ab in ablations}
    detail_rows = {ab: _load_detail_rows(ab, args.run_id) for ab in ablations}
    results_per_ab = {ab: _load_results(ab, args.run_id) for ab in ablations}
    tool_stats = {
        ab: (_aggregate_tool_call_counts(results_per_ab[ab]) if results_per_ab[ab] else {})
        for ab in ablations
    }
    conditional_stats = {
        ab: _conditional_eval_metrics(detail_rows[ab])
        for ab in ablations
    }

    md_table, csv_rows = _build_comparison_table(ablations, summaries, tool_stats, conditional_stats)

    # Write under the baseline run's evaluation_dir for convenience
    out_dir = evaluation_dir(BENCHMARK_FAMILY, run_id=args.run_id, ablation="full")
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"tool_ablation_pilot__{args.run_id}.md"
    csv_path = out_dir / f"tool_ablation_pilot__{args.run_id}.csv"
    json_path = out_dir / f"tool_ablation_pilot__{args.run_id}.json"

    md_path.write_text(
        f"# Tool-ablation pilot — run_id={args.run_id}\n\n"
        f"Conditions: {', '.join(ablations)}\n\n"
        f"## Comparison table\n\n{md_table}\n\n"
        f"## Per-ablation tool-call totals\n\n"
        + json.dumps(tool_stats, indent=2)
    )

    import csv as _csv
    with open(csv_path, "w", newline="") as fh:
        if csv_rows:
            writer = _csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            for row in csv_rows:
                writer.writerow(row)

    json_path.write_text(json.dumps({
        "run_id": args.run_id,
        "ablations": list(ablations),
        "summaries": summaries,
        "tool_stats": tool_stats,
        "conditional_stats": conditional_stats,
    }, indent=2, default=str))

    print(f"\n=== Wrote: {md_path}")
    print(f"=== Wrote: {csv_path}")
    print(f"=== Wrote: {json_path}")
    print(f"\n{md_table}\n")


if __name__ == "__main__":
    main()
