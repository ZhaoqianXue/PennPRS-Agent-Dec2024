"""Stage-by-stage analysis for a completed unified transfer run."""
import json, sys, argparse
from pathlib import Path
import pandas as pd

def main(run_id):
    root = Path("experiments/contribution3/transfer/runs/tool_calling_agent/unified")
    eval_dir = root / "evaluation" / f"{run_id}" if run_id else root / "evaluation"
    # run_batch writes evaluation dir via evaluation_dir helper; pick newest
    summaries = sorted(root.glob("evaluation*/all-tools__end_to_end_eval_summary.json"))
    summary_paths = list(root.glob(f"evaluation*/all-tools__end_to_end_eval_summary.json"))
    if run_id:
        # the run outputs under evaluation/<run_id>
        candidate = root / "evaluation" / f"{run_id}" / "all-tools__end_to_end_eval_summary.json"
        if candidate.exists():
            summary_paths = [candidate]
    if not summary_paths:
        print(f"No summary found for {run_id}"); return
    # take newest
    summary_path = sorted(summary_paths, key=lambda p: p.stat().st_mtime)[-1]
    print(f"Summary: {summary_path}")
    summary = json.loads(summary_path.read_text())
    print("\n=== Official macro (A/B) metrics ===")
    print(json.dumps(summary.get("official_metrics",{}), indent=2))
    print("\n=== By input_type ===")
    for label, sub in summary.get("by_input_type",{}).items():
        print(f"  {label}: n={sub['n_targets']} cov={sub['coverage']} hit@0.5%={sub['official_metrics']['hit_at_percent'].get('top_0_5pct')} hit@1%={sub['official_metrics']['hit_at_percent'].get('top_1pct')} hit@2.5%={sub['official_metrics']['hit_at_percent'].get('top_2_5pct')} oracle_in_probe={sub['stagewise_diagnostics']['oracle_in_probe_pool']} oracle_in_supporting={sub['stagewise_diagnostics']['oracle_in_supporting_bundles']} oracle_in_frontier={sub['stagewise_diagnostics']['oracle_in_model_frontier']} local_champion_conv={sub['stagewise_diagnostics']['local_champion_conversion']} tournament_conv={sub['stagewise_diagnostics']['global_tournament_conversion']}")
    print("\n=== Failure label counts ===")
    print(json.dumps(summary.get("failure_label_counts",{}), indent=2))
    print("\n=== Stagewise diagnostics (overall) ===")
    print(json.dumps(summary.get("stagewise_diagnostics",{}), indent=2))
    # Load detail csv
    detail_path = summary_path.with_name(summary_path.name.replace("_summary.json","_detail.csv"))
    if detail_path.exists():
        df = pd.read_csv(detail_path)
        print(f"\nDetail rows: {len(df)}")
        # Where are rank losses?
        lost = df[df["status"]=="evaluated"].copy()
        lost["rank_bucket"] = pd.cut(
            lost["selected_model_rank_fraction"].fillna(1.0),
            bins=[0,0.005,0.01,0.015,0.02,0.025,0.05,0.1,0.25,0.5,1.0],
            labels=["<=0.5%","0.5-1%","1-1.5%","1.5-2%","2-2.5%","2.5-5%","5-10%","10-25%","25-50%","50-100%"]
        )
        print("\n=== Rank fraction buckets ===")
        print(lost.groupby("rank_bucket")["target_id"].count())
        # Stage attrition
        def drop_stage(row):
            if not row.get("oracle_in_probe_pool"): return "1. shortlist_miss"
            if not row.get("oracle_in_supporting_bundles"): return "2. probe_retain_miss"
            if not row.get("oracle_in_local_champions"): return "3. local_champion_miss"
            if not row.get("oracle_in_model_frontier"): return "4. global_tournament_miss"
            return "5. oracle_hit"
        df["drop_stage"] = df.apply(drop_stage, axis=1)
        print("\n=== Oracle drop stage ===")
        print(df.groupby("drop_stage")["target_id"].count())
        # Examples per stage
        for stage in ("1. shortlist_miss","2. probe_retain_miss","3. local_champion_miss","4. global_tournament_miss"):
            subset = df[df["drop_stage"]==stage]
            if not subset.empty:
                print(f"\n-- {stage} examples ({len(subset)} targets) --")
                show_cols = ["target_id","target_description","input_type","matched_cross_trait","benchmark_top_model_id","recommended_model_id","selected_model_rank_fraction","failure_label"]
                print(subset[[c for c in show_cols if c in subset.columns]].head(10).to_string(index=False))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", default="")
    args = p.parse_args()
    main(args.run_id)
