"""
Generate a comparative ablation report across all completed ablation variants.

Reads summary JSONs from experiments/contribution2/ablation/runs/ and the
full-domain baseline from experiments/contribution2/recommendation/runs/,
then produces a consolidated Markdown report.

Usage:
    python experiments/contribution2/ablation/scripts/generate_ablation_report.py

    # Specify a custom baseline
    python experiments/contribution2/ablation/scripts/generate_ablation_report.py \
        --baseline-summary path/to/experiment_with_domain_summary.json

    # Also include without-domain as a lower bound
    python experiments/contribution2/ablation/scripts/generate_ablation_report.py \
        --without-domain-summary path/to/experiment_without_domain_summary.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
ABLATION_DIR = Path(__file__).resolve().parent.parent
ABLATION_RUNS_DIR = ABLATION_DIR / "runs"
DOCS_DIR = ABLATION_DIR / "docs"
RECOMMENDATION_RUNS = PROJECT_ROOT / "experiments" / "contribution2" / "recommendation" / "runs"
VARIANTS_DIR = ABLATION_DIR / "variants"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _find_latest_baseline(dataset_label: Optional[str] = None) -> Optional[Path]:
    """Find the most recent with-domain summary in recommendation/runs/."""
    dataset_suffix = f"__{dataset_label}" if dataset_label else "__30disease"
    candidates = sorted(
        RECOMMENDATION_RUNS.glob(
            f"with-domain-gpt-5.2-t10{dataset_suffix}*/experiment_with_domain_summary.json"
        ),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _run_dir_matches(
    run_dir: Path,
    dataset_label: Optional[str] = None,
    run_tag: Optional[str] = None,
) -> bool:
    name = run_dir.name
    if dataset_label and f"__{dataset_label}" not in name:
        return False
    if run_tag and not name.endswith(f"__{run_tag}"):
        return False
    return True


def _find_ablation_summaries(
    dataset_label: Optional[str] = None,
    run_tag: Optional[str] = None,
) -> dict[str, Path]:
    """Find all ablation summary JSONs, keyed by variant_id."""
    results: dict[str, Path] = {}
    for run_dir in sorted(ABLATION_RUNS_DIR.iterdir()):
        if not run_dir.is_dir() or not run_dir.name.startswith("ablation-"):
            continue
        if not _run_dir_matches(run_dir, dataset_label=dataset_label, run_tag=run_tag):
            continue
        summary = run_dir / "experiment_ablation_summary.json"
        if summary.exists():
            s = _load_json(summary)
            variant_id = s.get("ablation_variant", run_dir.name)
            results[variant_id] = summary
    return results


def _extract_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    """Extract key metrics from a summary JSON."""
    modal_hit = summary.get("modal_hit_at_k", {})
    trial_hit = summary.get("trial_hit_at_k", {})
    modal_percentile_hit = summary.get("modal_percentile_hit", {})
    trial_percentile_hit = summary.get("trial_percentile_hit", {})
    nrs = summary.get("nrs", {})

    # Build per-disease lookup
    per_disease_list = summary.get("per_disease", [])
    per_disease: dict[str, dict[str, Any]] = {}
    for entry in per_disease_list:
        ontology = entry.get("ontology", "")
        if ontology:
            per_disease[ontology] = entry

    modal_rank_fraction_values: list[float] = []
    modal_reverse_rank_fraction_values: list[float] = []
    trial_rank_fraction_values: list[float] = []
    trial_reverse_rank_fraction_values: list[float] = []

    for entry in per_disease_list:
        n_models = entry.get("n_models")
        modal_rank = entry.get("modal_recommendation_rank")
        if isinstance(n_models, int) and n_models > 0 and isinstance(modal_rank, int) and modal_rank > 0:
            modal_rank_fraction_values.append(modal_rank / n_models)
            modal_reverse_rank_fraction_values.append((n_models - modal_rank) / n_models)

        for trial_detail in entry.get("trial_recommendations_detailed") or []:
            trial_rank = trial_detail.get("rank")
            if isinstance(n_models, int) and n_models > 0 and isinstance(trial_rank, int) and trial_rank > 0:
                trial_rank_fraction_values.append(trial_rank / n_models)
                trial_reverse_rank_fraction_values.append((n_models - trial_rank) / n_models)

    return {
        "modal_hit_at_k": {
            str(k): modal_hit.get(str(k), {}).get("accuracy", 0.0) for k in range(1, 6)
        },
        "trial_hit_at_k": {
            str(k): trial_hit.get(str(k), {}).get("accuracy", 0.0) for k in range(1, 6)
        },
        "modal_percentile_hit": {
            str(k): modal_percentile_hit.get(str(k), {}).get("accuracy", 0.0)
            for k in (5, 10, 15, 20, 25)
        },
        "trial_percentile_hit": {
            str(k): trial_percentile_hit.get(str(k), {}).get("accuracy", 0.0)
            for k in (5, 10, 15, 20, 25)
        },
        "modal_rank_fraction": _mean(modal_rank_fraction_values),
        "trial_rank_fraction": _mean(trial_rank_fraction_values),
        "modal_reverse_rank_fraction": _mean(modal_reverse_rank_fraction_values),
        "trial_reverse_rank_fraction": _mean(trial_reverse_rank_fraction_values),
        "modal_nrs": nrs.get("modal_mean_nrs", 0.0),
        "trial_nrs": nrs.get("trial_mean_nrs", 0.0),
        "per_disease": per_disease,
    }


def _fmt_pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def _fmt_delta(v: float) -> str:
    sign = "+" if v > 0 else ""
    return f"{sign}{v * 100:.1f}pp"


def _fmt_num(v: float) -> str:
    return f"{v:.4f}"


def _fmt_num_delta(v: float) -> str:
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.4f}"


def _metric_cell_pct(value: float, baseline_value: float) -> str:
    return f"{_fmt_pct(value)} ({_fmt_delta(value - baseline_value)})"


def _metric_cell_num(value: float, baseline_value: float) -> str:
    return f"{_fmt_num(value)} ({_fmt_num_delta(value - baseline_value)})"


def _variant_label(variant_id: str) -> str:
    """Human-readable label for a variant."""
    labels = {
        "no-section1-trait-endpoint": "S1: trait / endpoint",
        "no-section2-performance-covariates": "S2: performance / covariates",
        "no-section3-validation-sample-size": "S3: validation_sample_size",
        "no-section4-training-cohorts-ancestry": "S4: training_cohorts / ancestry",
        "no-section5-method-name": "S5: method_name",
        "no-section6-publication": "S6: publication",
        "no-section7-variants-number": "S7: variants_number",
    }
    return labels.get(variant_id, variant_id)


def _generate_report(
    baseline_summary: dict[str, Any],
    ablation_summaries: dict[str, dict[str, Any]],
    without_domain_summary: Optional[dict[str, Any]] = None,
) -> str:
    """Generate the full ablation comparison report."""
    baseline = _extract_metrics(baseline_summary)
    ablations = {vid: _extract_metrics(s) for vid, s in ablation_summaries.items()}

    lines: list[str] = []
    lines.append("# Domain Knowledge Ablation Study Report")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("Each row represents a leave-one-out ablation: the full domain knowledge document "
                 "with exactly one ## section removed. Delta columns show the change relative to "
                 "the full-domain baseline.")
    lines.append("")
    lines.append("Hit metrics are reported for both modal selections and all trials. "
                 "Ranking metrics use the AoU benchmark rank `r` within a disease-specific "
                 "candidate pool of size `M`.")
    lines.append("")

    variant_order = sorted(
        ablations.keys(),
        key=lambda vid: ablations[vid]["modal_hit_at_k"]["1"] - baseline["modal_hit_at_k"]["1"],
    )
    bm = baseline["modal_hit_at_k"]
    baseline_percentile = baseline["modal_percentile_hit"]
    baseline_trial_hit = baseline["trial_hit_at_k"]
    baseline_trial_percentile = baseline["trial_percentile_hit"]
    wd = _extract_metrics(without_domain_summary) if without_domain_summary else None

    # --- Modal hit@k ---
    lines.append("## Modal Hit@1-5")
    lines.append("")
    header = "| Variant | Removed Section | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |"
    sep = "|---------|----------------|-------|-------|-------|-------|-------|"
    lines.append(header)
    lines.append(sep)
    lines.append(
        f"| **Full (baseline)** | — | {_fmt_pct(bm['1'])} | {_fmt_pct(bm['2'])} | {_fmt_pct(bm['3'])} | "
        f"{_fmt_pct(bm['4'])} | {_fmt_pct(bm['5'])} |"
    )
    if wd:
        wm = wd["modal_hit_at_k"]
        lines.append(
            f"| *No domain (lower bound)* | *all sections* | {_metric_cell_pct(wm['1'], bm['1'])} | "
            f"{_metric_cell_pct(wm['2'], bm['2'])} | {_metric_cell_pct(wm['3'], bm['3'])} | "
            f"{_metric_cell_pct(wm['4'], bm['4'])} | {_metric_cell_pct(wm['5'], bm['5'])} |"
        )
    for vid in variant_order:
        am = ablations[vid]["modal_hit_at_k"]
        lines.append(
            f"| `{vid}` | {_variant_label(vid)} | {_metric_cell_pct(am['1'], bm['1'])} | "
            f"{_metric_cell_pct(am['2'], bm['2'])} | {_metric_cell_pct(am['3'], bm['3'])} | "
            f"{_metric_cell_pct(am['4'], bm['4'])} | {_metric_cell_pct(am['5'], bm['5'])} |"
        )
    lines.append("")

    # --- Trial hit@k ---
    lines.append("## Trial Hit@1-5")
    lines.append("")
    lines.append(header)
    lines.append(sep)
    lines.append(
        f"| **Full (baseline)** | — | {_fmt_pct(baseline_trial_hit['1'])} | {_fmt_pct(baseline_trial_hit['2'])} | "
        f"{_fmt_pct(baseline_trial_hit['3'])} | {_fmt_pct(baseline_trial_hit['4'])} | {_fmt_pct(baseline_trial_hit['5'])} |"
    )
    if wd:
        wt = wd["trial_hit_at_k"]
        lines.append(
            f"| *No domain (lower bound)* | *all sections* | {_metric_cell_pct(wt['1'], baseline_trial_hit['1'])} | "
            f"{_metric_cell_pct(wt['2'], baseline_trial_hit['2'])} | {_metric_cell_pct(wt['3'], baseline_trial_hit['3'])} | "
            f"{_metric_cell_pct(wt['4'], baseline_trial_hit['4'])} | {_metric_cell_pct(wt['5'], baseline_trial_hit['5'])} |"
        )
    for vid in variant_order:
        at = ablations[vid]["trial_hit_at_k"]
        lines.append(
            f"| `{vid}` | {_variant_label(vid)} | {_metric_cell_pct(at['1'], baseline_trial_hit['1'])} | "
            f"{_metric_cell_pct(at['2'], baseline_trial_hit['2'])} | {_metric_cell_pct(at['3'], baseline_trial_hit['3'])} | "
            f"{_metric_cell_pct(at['4'], baseline_trial_hit['4'])} | {_metric_cell_pct(at['5'], baseline_trial_hit['5'])} |"
        )
    lines.append("")

    # --- Modal percentile hit ---
    lines.append("## Modal Top 5-25% Hit")
    lines.append("")
    percentile_header = "| Variant | Removed Section | Top 5% | Top 10% | Top 15% | Top 20% | Top 25% |"
    percentile_sep = "|---------|----------------|--------|---------|---------|---------|---------|"
    lines.append(percentile_header)
    lines.append(percentile_sep)
    lines.append(
        f"| **Full (baseline)** | — | {_fmt_pct(baseline_percentile['5'])} | {_fmt_pct(baseline_percentile['10'])} | "
        f"{_fmt_pct(baseline_percentile['15'])} | {_fmt_pct(baseline_percentile['20'])} | {_fmt_pct(baseline_percentile['25'])} |"
    )
    if wd:
        wp = wd["modal_percentile_hit"]
        lines.append(
            f"| *No domain (lower bound)* | *all sections* | {_metric_cell_pct(wp['5'], baseline_percentile['5'])} | "
            f"{_metric_cell_pct(wp['10'], baseline_percentile['10'])} | {_metric_cell_pct(wp['15'], baseline_percentile['15'])} | "
            f"{_metric_cell_pct(wp['20'], baseline_percentile['20'])} | {_metric_cell_pct(wp['25'], baseline_percentile['25'])} |"
        )
    for vid in variant_order:
        ap = ablations[vid]["modal_percentile_hit"]
        lines.append(
            f"| `{vid}` | {_variant_label(vid)} | {_metric_cell_pct(ap['5'], baseline_percentile['5'])} | "
            f"{_metric_cell_pct(ap['10'], baseline_percentile['10'])} | {_metric_cell_pct(ap['15'], baseline_percentile['15'])} | "
            f"{_metric_cell_pct(ap['20'], baseline_percentile['20'])} | {_metric_cell_pct(ap['25'], baseline_percentile['25'])} |"
        )
    lines.append("")

    # --- Trial percentile hit ---
    lines.append("## Trial Top 5-25% Hit")
    lines.append("")
    lines.append(percentile_header)
    lines.append(percentile_sep)
    lines.append(
        f"| **Full (baseline)** | — | {_fmt_pct(baseline_trial_percentile['5'])} | {_fmt_pct(baseline_trial_percentile['10'])} | "
        f"{_fmt_pct(baseline_trial_percentile['15'])} | {_fmt_pct(baseline_trial_percentile['20'])} | {_fmt_pct(baseline_trial_percentile['25'])} |"
    )
    if wd:
        wtp = wd["trial_percentile_hit"]
        lines.append(
            f"| *No domain (lower bound)* | *all sections* | {_metric_cell_pct(wtp['5'], baseline_trial_percentile['5'])} | "
            f"{_metric_cell_pct(wtp['10'], baseline_trial_percentile['10'])} | {_metric_cell_pct(wtp['15'], baseline_trial_percentile['15'])} | "
            f"{_metric_cell_pct(wtp['20'], baseline_trial_percentile['20'])} | {_metric_cell_pct(wtp['25'], baseline_trial_percentile['25'])} |"
        )
    for vid in variant_order:
        atp = ablations[vid]["trial_percentile_hit"]
        lines.append(
            f"| `{vid}` | {_variant_label(vid)} | {_metric_cell_pct(atp['5'], baseline_trial_percentile['5'])} | "
            f"{_metric_cell_pct(atp['10'], baseline_trial_percentile['10'])} | {_metric_cell_pct(atp['15'], baseline_trial_percentile['15'])} | "
            f"{_metric_cell_pct(atp['20'], baseline_trial_percentile['20'])} | {_metric_cell_pct(atp['25'], baseline_trial_percentile['25'])} |"
        )
    lines.append("")

    # --- Ranking metrics ---
    lines.append("## Rank Fraction / Reverse Rank Fraction / NRS")
    lines.append("")
    lines.append("- Rank Fraction: `r / M` where smaller is better.")
    lines.append("- Reverse Rank Fraction: `(M - r) / M` where larger is better.")
    lines.append("- Normalized Ranking Score: `NRS = (M - r) / (M - 1)` where larger is better.")
    lines.append("")
    ranking_header = (
        "| Variant | Removed Section | Modal r / M | Modal (M - r) / M | Modal NRS | "
        "Trial r / M | Trial (M - r) / M | Trial NRS |"
    )
    ranking_sep = (
        "|---------|----------------|-------------|-------------------|-----------|"
        "-------------|-------------------|-----------|"
    )
    lines.append(ranking_header)
    lines.append(ranking_sep)
    lines.append(
        f"| **Full (baseline)** | — | {_fmt_num(baseline['modal_rank_fraction'])} | "
        f"{_fmt_num(baseline['modal_reverse_rank_fraction'])} | {_fmt_num(baseline['modal_nrs'])} | "
        f"{_fmt_num(baseline['trial_rank_fraction'])} | {_fmt_num(baseline['trial_reverse_rank_fraction'])} | {_fmt_num(baseline['trial_nrs'])} |"
    )
    if wd:
        lines.append(
            f"| *No domain (lower bound)* | *all sections* | {_metric_cell_num(wd['modal_rank_fraction'], baseline['modal_rank_fraction'])} | "
            f"{_metric_cell_num(wd['modal_reverse_rank_fraction'], baseline['modal_reverse_rank_fraction'])} | {_metric_cell_num(wd['modal_nrs'], baseline['modal_nrs'])} | "
            f"{_metric_cell_num(wd['trial_rank_fraction'], baseline['trial_rank_fraction'])} | {_metric_cell_num(wd['trial_reverse_rank_fraction'], baseline['trial_reverse_rank_fraction'])} | {_metric_cell_num(wd['trial_nrs'], baseline['trial_nrs'])} |"
        )
    for vid in variant_order:
        am = ablations[vid]
        lines.append(
            f"| `{vid}` | {_variant_label(vid)} | {_metric_cell_num(am['modal_rank_fraction'], baseline['modal_rank_fraction'])} | "
            f"{_metric_cell_num(am['modal_reverse_rank_fraction'], baseline['modal_reverse_rank_fraction'])} | {_metric_cell_num(am['modal_nrs'], baseline['modal_nrs'])} | "
            f"{_metric_cell_num(am['trial_rank_fraction'], baseline['trial_rank_fraction'])} | {_metric_cell_num(am['trial_reverse_rank_fraction'], baseline['trial_reverse_rank_fraction'])} | {_metric_cell_num(am['trial_nrs'], baseline['trial_nrs'])} |"
        )
    lines.append("")

    # --- Section importance ranking ---
    lines.append("## Section Importance Ranking (by Hit@1 drop)")
    lines.append("")
    lines.append("Sections sorted by the magnitude of Hit@1 drop when removed (largest drop = most important):")
    lines.append("")

    importance = sorted(
        ablations.items(),
        key=lambda item: item[1]["modal_hit_at_k"]["1"] - baseline["modal_hit_at_k"]["1"],
    )
    for rank, (vid, metrics) in enumerate(importance, 1):
        delta1 = metrics["modal_hit_at_k"]["1"] - baseline["modal_hit_at_k"]["1"]
        delta_nrs = metrics["modal_nrs"] - baseline["modal_nrs"]
        lines.append(
            f"{rank}. **{_variant_label(vid)}** (`{vid}`): "
            f"Hit@1 {_fmt_delta(delta1)}, NRS {_fmt_delta(delta_nrs)}"
        )
    lines.append("")

    # --- Per-disease impact analysis ---
    lines.append("## Per-Disease Impact Analysis")
    lines.append("")
    lines.append("For each variant, which diseases changed from Hit to Miss (regressions) "
                 "or Miss to Hit (improvements) at Hit@1 compared to the full baseline.")
    lines.append("")

    baseline_pd = baseline["per_disease"]
    for vid in variant_order:
        ablation_pd = ablations[vid]["per_disease"]
        regressions: list[str] = []
        improvements: list[str] = []

        all_diseases = set(baseline_pd.keys()) | set(ablation_pd.keys())
        for disease in sorted(all_diseases):
            b_hit = baseline_pd.get(disease, {}).get("modal_recommendation_hit_at_k", {}).get("1", False)
            a_hit = ablation_pd.get(disease, {}).get("modal_recommendation_hit_at_k", {}).get("1", False)
            if b_hit and not a_hit:
                regressions.append(disease)
            elif not b_hit and a_hit:
                improvements.append(disease)

        if regressions or improvements:
            lines.append(f"### `{vid}` ({_variant_label(vid)})")
            lines.append("")
            if regressions:
                lines.append(f"- **Regressions** (Hit->Miss): {', '.join(regressions)}")
            if improvements:
                lines.append(f"- **Improvements** (Miss->Hit): {', '.join(improvements)}")
            lines.append(f"- Net: {len(improvements) - len(regressions):+d} diseases")
            lines.append("")

    # --- Robustness analysis ---
    lines.append("## Disease Robustness Analysis")
    lines.append("")
    lines.append("### Robust diseases (Hit@1 in baseline AND all ablation variants)")
    lines.append("")

    all_diseases = sorted(baseline_pd.keys())
    robust = []
    fragile = []
    for disease in all_diseases:
        b_hit = baseline_pd.get(disease, {}).get("modal_recommendation_hit_at_k", {}).get("1", False)
        if not b_hit:
            continue
        all_keep = all(
            ablations[vid]["per_disease"].get(disease, {}).get("modal_recommendation_hit_at_k", {}).get("1", False)
            for vid in ablations
        )
        if all_keep:
            robust.append(disease)
        else:
            failing_variants = [
                vid for vid in ablations
                if not ablations[vid]["per_disease"].get(disease, {}).get("modal_recommendation_hit_at_k", {}).get("1", False)
            ]
            fragile.append((disease, failing_variants))

    if robust:
        for d in robust:
            lines.append(f"- {d}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("### Fragile diseases (Hit@1 in baseline but Miss in at least one variant)")
    lines.append("")
    if fragile:
        for d, variants in fragile:
            lines.append(f"- **{d}**: lost in {', '.join(f'`{v}`' for v in variants)}")
    else:
        lines.append("- (none)")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate comparative ablation report"
    )
    parser.add_argument(
        "--baseline-summary",
        type=str,
        default=None,
        help="Path to the full-domain baseline summary JSON. Auto-detected if not provided.",
    )
    parser.add_argument(
        "--without-domain-summary",
        type=str,
        default=None,
        help="Optional path to the without-domain summary JSON (shown as lower bound).",
    )
    parser.add_argument(
        "--dataset-label",
        type=str,
        default=None,
        help="Optional dataset label filter (for example: 30disease or 75disease).",
    )
    parser.add_argument(
        "--run-tag",
        type=str,
        default=None,
        help="Optional run tag filter. Only ablation run dirs ending with this tag are included.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help=f"Output report path (default: {DOCS_DIR / 'ablation_comparison_report.md'})",
    )
    args = parser.parse_args()

    # Load baseline
    if args.baseline_summary:
        baseline_path = Path(args.baseline_summary)
    else:
        baseline_path = _find_latest_baseline(dataset_label=args.dataset_label)
        if not baseline_path:
            print("ERROR: No with-domain baseline summary found. Use --baseline-summary.")
            return 1
    print(f"Baseline: {baseline_path}")
    baseline_summary = _load_json(baseline_path)

    # Load without-domain (optional)
    without_domain_summary = None
    if args.without_domain_summary:
        without_domain_summary = _load_json(Path(args.without_domain_summary))
        print(f"Without-domain lower bound: {args.without_domain_summary}")
    else:
        # Auto-detect
        wd_candidates = sorted(
            RECOMMENDATION_RUNS.glob(
                f"without-domain-gpt-5.2-t10__{args.dataset_label or '30disease'}*/experiment_without_domain_summary.json"
            ),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if wd_candidates:
            without_domain_summary = _load_json(wd_candidates[0])
            print(f"Without-domain lower bound (auto): {wd_candidates[0]}")

    # Load ablation summaries
    ablation_paths = _find_ablation_summaries(
        dataset_label=args.dataset_label,
        run_tag=args.run_tag,
    )
    if not ablation_paths:
        print("ERROR: No ablation summaries found in runs/. Run ablation experiments first.")
        return 1
    print(f"Found {len(ablation_paths)} ablation variants: {list(ablation_paths.keys())}")

    ablation_summaries = {vid: _load_json(path) for vid, path in ablation_paths.items()}

    # Generate report
    report = _generate_report(
        baseline_summary=baseline_summary,
        ablation_summaries=ablation_summaries,
        without_domain_summary=without_domain_summary,
    )

    # Write output
    output_path = Path(args.output) if args.output else DOCS_DIR / "ablation_comparison_report.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"\nReport written to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
