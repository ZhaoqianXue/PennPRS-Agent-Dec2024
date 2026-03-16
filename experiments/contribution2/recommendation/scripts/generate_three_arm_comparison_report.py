"""
Generate a three-arm comparison report for Contribution2 recommendation runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain


def _load_summary(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Summary not found: {path}")
    summary = json.loads(path.read_text(encoding="utf-8"))
    without_domain._ensure_summary_hit_metrics(summary)
    return summary


def _format_models(items: list[dict]) -> str:
    return "<br>".join(
        f"{item['pgs_id']} (AUC rank {item['rank_label']}): x{item['count']}"
        for item in (items or [])
    ) or "-"


def _write_report(
    prompt_summary: dict,
    search_summary: dict,
    domain_summary: dict,
    output_path: Path,
) -> Path:
    prompt_rank_fraction = without_domain._compute_rank_metric_summary(prompt_summary, without_domain._rank_fraction)
    search_rank_fraction = without_domain._compute_rank_metric_summary(search_summary, without_domain._rank_fraction)
    domain_rank_fraction = without_domain._compute_rank_metric_summary(domain_summary, without_domain._rank_fraction)

    prompt_reverse_rank_fraction = without_domain._compute_rank_metric_summary(
        prompt_summary, without_domain._reverse_rank_fraction
    )
    search_reverse_rank_fraction = without_domain._compute_rank_metric_summary(
        search_summary, without_domain._reverse_rank_fraction
    )
    domain_reverse_rank_fraction = without_domain._compute_rank_metric_summary(
        domain_summary, without_domain._reverse_rank_fraction
    )

    prompt_nrs = without_domain._compute_nrs_metrics(prompt_summary)
    search_nrs = without_domain._compute_nrs_metrics(search_summary)
    domain_nrs = without_domain._compute_nrs_metrics(domain_summary)

    prompt_rows = {row["ontology"]: row for row in prompt_summary["per_disease"]}
    search_rows = {row["ontology"]: row for row in search_summary["per_disease"]}
    domain_rows = {row["ontology"]: row for row in domain_summary["per_disease"]}
    per_disease_rows = without_domain._sort_disease_rows(domain_summary["per_disease"])

    lines = [
        "# Contribution2 Three-Arm Comparison",
        "",
        "## Summary",
        "",
        f"- **Model**: {domain_summary['model']}",
        f"- **Diseases**: {domain_summary['total_ontologies']}",
        f"- **Trials per disease**: {domain_summary['trials_per_ontology']}",
        f"- **Union CSV**: `{domain_summary.get('union_csv') or search_summary.get('union_csv') or prompt_summary.get('union_csv')}`",
        "",
        "## High-Level Outcome",
        "",
        *[
            (
                f"- {without_domain.PROMPT_ONLY_LABEL} `Hit@{k}`: "
                f"`{prompt_summary['modal_hit_at_k'][str(k)]['hits']}/{prompt_summary['modal_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(prompt_summary['modal_hit_at_k'][str(k)]['accuracy'] or 0.0)}`; "
                f"`trial_hits = {prompt_summary['trial_hit_at_k'][str(k)]['hits']}/{prompt_summary['trial_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(prompt_summary['trial_hit_at_k'][str(k)]['accuracy'] or 0.0)}`"
            )
            for k in without_domain.BENCHMARK_HIT_KS
        ],
        *[
            (
                f"- {without_domain.SEARCH_ONLY_LABEL} `Hit@{k}`: "
                f"`{search_summary['modal_hit_at_k'][str(k)]['hits']}/{search_summary['modal_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(search_summary['modal_hit_at_k'][str(k)]['accuracy'] or 0.0)}`; "
                f"`trial_hits = {search_summary['trial_hit_at_k'][str(k)]['hits']}/{search_summary['trial_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(search_summary['trial_hit_at_k'][str(k)]['accuracy'] or 0.0)}`"
            )
            for k in without_domain.BENCHMARK_HIT_KS
        ],
        *[
            (
                f"- {without_domain.DOMAIN_KNOWLEDGE_LABEL} `Hit@{k}`: "
                f"`{domain_summary['modal_hit_at_k'][str(k)]['hits']}/{domain_summary['modal_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(domain_summary['modal_hit_at_k'][str(k)]['accuracy'] or 0.0)}`; "
                f"`trial_hits = {domain_summary['trial_hit_at_k'][str(k)]['hits']}/{domain_summary['trial_hit_at_k'][str(k)]['eligible']} = "
                f"{without_domain._format_percent(domain_summary['trial_hit_at_k'][str(k)]['accuracy'] or 0.0)}`"
            )
            for k in without_domain.BENCHMARK_HIT_KS
        ],
        "",
        f"- **{without_domain.PROMPT_ONLY_LABEL} valid output rate**: `{prompt_summary['diagnostics']['valid_outputs']}/{prompt_summary['diagnostics']['total_trials']} = {without_domain._format_percent(prompt_summary['diagnostics']['valid_output_rate'])}`",
        f"- **{without_domain.SEARCH_ONLY_LABEL} valid output rate**: `{search_summary['diagnostics']['valid_outputs']}/{search_summary['diagnostics']['total_trials']} = {without_domain._format_percent(search_summary['diagnostics']['valid_output_rate'])}`",
        f"- **{without_domain.DOMAIN_KNOWLEDGE_LABEL} valid output rate**: `{domain_summary['diagnostics']['valid_outputs']}/{domain_summary['diagnostics']['total_trials']} = {without_domain._format_percent(domain_summary['diagnostics']['valid_output_rate'])}`",
        "",
        *without_domain._percentile_hit_section_lines([
            (without_domain.PROMPT_ONLY_LABEL, prompt_summary["modal_percentile_hit"], prompt_summary["trial_percentile_hit"]),
            (without_domain.SEARCH_ONLY_LABEL, search_summary["modal_percentile_hit"], search_summary["trial_percentile_hit"]),
            (without_domain.DOMAIN_KNOWLEDGE_LABEL, domain_summary["modal_percentile_hit"], domain_summary["trial_percentile_hit"]),
        ]),
        *without_domain._rank_metric_section_lines(
            title="Rank Fraction (r / M)",
            metric_display="r / M",
            formula_text="r / M",
            scale_lines=[
                "- Scale: smaller is better.",
                "- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.",
            ],
            metrics_by_label=[
                (without_domain.PROMPT_ONLY_LABEL, prompt_rank_fraction),
                (without_domain.SEARCH_ONLY_LABEL, search_rank_fraction),
                (without_domain.DOMAIN_KNOWLEDGE_LABEL, domain_rank_fraction),
            ],
        ),
        *without_domain._rank_metric_section_lines(
            title="Reverse Rank Fraction ((M - r) / M)",
            metric_display="(M - r) / M",
            formula_text="(M - r) / M",
            scale_lines=[
                "- Scale: `0.0` means bottom-ranked; larger is better.",
                "- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.",
            ],
            metrics_by_label=[
                (without_domain.PROMPT_ONLY_LABEL, prompt_reverse_rank_fraction),
                (without_domain.SEARCH_ONLY_LABEL, search_reverse_rank_fraction),
                (without_domain.DOMAIN_KNOWLEDGE_LABEL, domain_reverse_rank_fraction),
            ],
        ),
        *without_domain._rank_metric_section_lines(
            title="Normalized Ranking Score (NRS)",
            metric_display="NRS",
            formula_text="NRS = (M - r) / (M - 1)",
            scale_lines=[
                "- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.",
            ],
            metrics_by_label=[
                (without_domain.PROMPT_ONLY_LABEL, prompt_nrs),
                (without_domain.SEARCH_ONLY_LABEL, search_nrs),
                (without_domain.DOMAIN_KNOWLEDGE_LABEL, domain_nrs),
            ],
        ),
        "",
        "## Results by Disease",
        "",
        f"| Ontology | N Models | {without_domain.PROMPT_ONLY_LABEL} Hit@1..5 | {without_domain.PROMPT_ONLY_LABEL} | {without_domain.SEARCH_ONLY_LABEL} Hit@1..5 | {without_domain.SEARCH_ONLY_LABEL} | {without_domain.DOMAIN_KNOWLEDGE_LABEL} Hit@1..5 | {without_domain.DOMAIN_KNOWLEDGE_LABEL} |",
        "|----------|----------|------------------------------|------------------------|---------------------------|----------------------|--------------------------------------|------------------------------------|",
    ]

    for row in per_disease_rows:
        ontology = row["ontology"]
        prompt_row = prompt_rows[ontology]
        search_row = search_rows[ontology]
        domain_row = domain_rows[ontology]
        lines.append(
            f"| {ontology} | {row['n_models']} | "
            f"{without_domain._format_hit_vector(prompt_row.get('modal_recommendation_hit_at_k') or {})} | {_format_models(prompt_row.get('recommended_model_counts') or [])} | "
            f"{without_domain._format_hit_vector(search_row.get('modal_recommendation_hit_at_k') or {})} | {_format_models(search_row.get('recommended_model_counts') or [])} | "
            f"{without_domain._format_hit_vector(domain_row.get('modal_recommendation_hit_at_k') or {})} | {_format_models(domain_row.get('recommended_model_counts') or [])} |"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a three-arm Contribution2 comparison report")
    parser.add_argument("--prompt-summary", required=True, help="Path to experiment_prompt_only_summary.json")
    parser.add_argument("--search-summary", required=True, help="Path to experiment_without_domain_summary.json")
    parser.add_argument("--domain-summary", required=True, help="Path to experiment_with_domain_summary.json")
    parser.add_argument(
        "--output-report",
        default=None,
        help="Optional output markdown path. Defaults to the domain-summary run directory.",
    )
    args = parser.parse_args()

    prompt_path = Path(args.prompt_summary)
    search_path = Path(args.search_summary)
    domain_path = Path(args.domain_summary)
    output_path = (
        Path(args.output_report)
        if args.output_report
        else domain_path.parent / "experiment_three_arm_comparison_report.md"
    )

    prompt_summary = _load_summary(prompt_path)
    search_summary = _load_summary(search_path)
    domain_summary = _load_summary(domain_path)
    path = _write_report(prompt_summary, search_summary, domain_summary, output_path)
    print(f"Three-arm report: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
