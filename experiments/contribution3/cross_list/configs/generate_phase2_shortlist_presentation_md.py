"""Generate a presentation-friendly Markdown document for the final Phase 2 shortlist.

The document is built from the current Phase 2 outputs and is intended for
manual review / presentation, not as a new analytical source of truth.
"""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PHASE2_DIR = BASE_DIR / "analysis" / "phase2"
B2B_DETAIL_PATH = BASE_DIR / "runs" / "binary_to_binary" / "cross_list_detail.csv"
B2C_DETAIL_PATH = BASE_DIR / "runs" / "binary_to_continuous" / "cross_list_detail.csv"
SUMMARY_PATH = PHASE2_DIR / "binary_target_cross_trait_summary.csv"
SHORTLIST_PATH = PHASE2_DIR / "binary_cross_trait_shortlist.csv"
B2B_SHORTLIST_PATH = PHASE2_DIR / "b2b_cross_trait_shortlist.csv"
B2C_SHORTLIST_PATH = PHASE2_DIR / "b2c_cross_trait_shortlist.csv"
OUTPUT_PATH = PHASE2_DIR / "binary_cross_trait_shortlist_presentation.md"


def load_csv(path: Path):
    with open(path) as f:
        return list(csv.DictReader(f))


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def parse_float(value: str):
    text = str(value).strip()
    if not text:
        return None
    return float(text)


def safe_text(value: str) -> str:
    text = str(value or "").replace("\n", " ").strip()
    return text.replace("|", r"\|")


def short_label(value: str) -> str:
    parts = [part.strip() for part in str(value or "").split(";") if part.strip()]
    return parts[0] if parts else str(value or "").strip()


def unique_display_labels(values):
    split_values = {
        value: [part.strip() for part in str(value or "").split(";") if part.strip()]
        for value in values
    }
    labels = {}
    for value, parts in split_values.items():
        if not parts:
            labels[value] = str(value or "").strip()
            continue
        chosen = parts[0]
        for n_parts in range(1, len(parts) + 1):
            candidate = "; ".join(parts[:n_parts])
            collision = False
            for other_value, other_parts in split_values.items():
                if other_value == value:
                    continue
                other_candidate = "; ".join(other_parts[: min(n_parts, len(other_parts))]) if other_parts else str(other_value or "").strip()
                if candidate == other_candidate:
                    collision = True
                    break
            if not collision:
                chosen = candidate
                break
        labels[value] = chosen
    return labels


def format_number(value, decimals: int = 6) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""
        value = float(text)
    return f"{value:.{decimals}f}"


def format_int(value) -> str:
    if value is None or value == "":
        return ""
    return str(int(value))


def median_or_none(values):
    return statistics.median(values) if values else None


def mean_or_none(values):
    return statistics.mean(values) if values else None


def effective_improvement(row, has_self_col: str, improvement_col: str, metric_col: str):
    raw_improvement = str(row.get(improvement_col, "")).strip()
    if raw_improvement:
        return float(raw_improvement)
    if not parse_bool(row.get(has_self_col, "")):
        raw_metric = str(row.get(metric_col, "")).strip()
        if raw_metric:
            return float(raw_metric)
    return None


def load_detail_stats():
    stats = {}

    def ingest(rows, stream: str, target_col: str, cross_col: str, code_col: str | None, has_self_col: str):
        grouped = defaultdict(list)
        for row in rows:
            cross_trait = row.get(cross_col, "")
            if not cross_trait:
                continue
            metric = parse_float(row.get("cross_auc", ""))
            if metric is None:
                continue
            eff = effective_improvement(
                row=row,
                has_self_col=has_self_col,
                improvement_col="auc_improvement",
                metric_col="cross_auc",
            )
            if eff is None:
                continue
            code = row.get(code_col, "") if code_col else ""
            key = (stream, row[target_col], cross_trait, code)
            grouped[key].append(
                {
                    "pgs_id": row["output_pgs_id"],
                    "cross_auc": metric,
                    "effective_improvement": eff,
                }
            )

        for key, items in grouped.items():
            best = max(
                items,
                key=lambda item: (
                    item["effective_improvement"],
                    item["cross_auc"],
                    item["pgs_id"],
                ),
            )
            cross_metrics = [item["cross_auc"] for item in items]
            eff_metrics = [item["effective_improvement"] for item in items]
            stats[key] = {
                "n_prs_models": len(items),
                "best_pgs_id": best["pgs_id"],
                "best_cross_auc": max(cross_metrics),
                "mean_cross_auc": mean_or_none(cross_metrics),
                "median_cross_auc": median_or_none(cross_metrics),
                "best_effective_improvement": max(eff_metrics),
                "mean_effective_improvement": mean_or_none(eff_metrics),
                "median_effective_improvement": median_or_none(eff_metrics),
            }

    ingest(
        load_csv(B2B_DETAIL_PATH),
        stream="b2b",
        target_col="input_icd",
        cross_col="output_disease",
        code_col=None,
        has_self_col="has_self_auc",
    )
    ingest(
        load_csv(B2C_DETAIL_PATH),
        stream="b2c",
        target_col="input_icd",
        cross_col="output_ontology",
        code_col="output_loinc",
        has_self_col="has_self_auc",
    )

    return stats


def render_table(rows, headers):
    if not rows:
        return "_None._\n"

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(safe_text(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines) + "\n"


def describe_cross_trait_types(rows, fallback_streams: str) -> str:
    type_set = {str(row.get("cross_trait_type", "")).strip() for row in rows if str(row.get("cross_trait_type", "")).strip()}
    if not type_set:
        stream_map = {"b2b": "binary", "b2c": "continuous"}
        type_set = {stream_map.get(code.strip(), "") for code in str(fallback_streams or "").split(";") if code.strip()}
        type_set.discard("")
    if type_set == {"binary"}:
        return "binary only"
    if type_set == {"continuous"}:
        return "continuous only"
    if type_set == {"binary", "continuous"}:
        return "binary + continuous"
    return ", ".join(sorted(type_set))


def build_target_tables(summary_rows, shortlist_rows):
    shortlist_by_target = defaultdict(list)
    for row in shortlist_rows:
        shortlist_by_target[row["target_id"]].append(row)

    type_a_rows = []
    type_b_rows = []
    for row in sorted(summary_rows, key=lambda item: item["target_icd"]):
        target_rows = shortlist_by_target.get(row["target_icd"], [])
        unique_cross_traits = {
            (
                r["cross_trait_type"],
                r["cross_trait"],
            )
            for r in target_rows
        }

        n_recommended = str(len(unique_cross_traits))
        cross_trait_types = describe_cross_trait_types(target_rows, row["streams_present"])
        top_cross_trait = short_label(row["top_cross_trait"])

        if row["input_type"] == "A":
            type_a_rows.append(
                {
                    "Target ICD": row["target_icd"],
                    "Target Trait": short_label(row["target_trait"]),
                    "Available Cross Trait Types": cross_trait_types,
                    "N Recommended Cross Traits": n_recommended,
                    "Top Recommended Cross Trait": top_cross_trait,
                    "Top Recommended Cross Trait AUC": format_number(row["top_cross_trait_improvement"]),
                    "Top Recommended Cross Trait Plausibility": row["top_cross_trait_plausibility"],
                }
            )
        else:
            type_b_rows.append(
                {
                    "Target ICD": row["target_icd"],
                    "Target Trait": short_label(row["target_trait"]),
                    "Available Cross Trait Types": cross_trait_types,
                    "N Recommended Cross Traits": n_recommended,
                    "Top Recommended Cross Trait": top_cross_trait,
                    "Top AUC Gain vs Self": format_number(row["top_cross_trait_improvement"]),
                    "Top Recommended Cross Trait Plausibility": row["top_cross_trait_plausibility"],
                }
            )

    type_a_headers = [
        "Target ICD",
        "Target Trait",
        "Available Cross Trait Types",
        "N Recommended Cross Traits",
        "Top Recommended Cross Trait",
        "Top Recommended Cross Trait AUC",
        "Top Recommended Cross Trait Plausibility",
    ]
    type_b_headers = [
        "Target ICD",
        "Target Trait",
        "Available Cross Trait Types",
        "N Recommended Cross Traits",
        "Top Recommended Cross Trait",
        "Top AUC Gain vs Self",
        "Top Recommended Cross Trait Plausibility",
    ]
    return type_a_headers, type_a_rows, type_b_headers, type_b_rows


def build_cross_trait_sections(summary_rows, shortlist_rows, detail_stats):
    shortlist_by_target = defaultdict(list)
    for row in shortlist_rows:
        shortlist_by_target[row["target_id"]].append(row)

    type_a_sections = []
    type_b_sections = []

    target_order = sorted(summary_rows, key=lambda row: (row["input_type"], row["target_icd"]))
    type_a_headers = [
        "Rank",
        "Cross Trait Type",
        "Cross Trait",
        "Biological Plausibility",
        "Why It Was Kept",
        "N Candidate PRS Models",
        "Best PGS ID",
        "Best PGS AUC",
        "Median PGS AUC",
    ]
    type_b_headers = [
        "Rank",
        "Cross Trait Type",
        "Cross Trait",
        "Biological Plausibility",
        "Why It Was Kept",
        "N Candidate PRS Models",
        "Best PGS ID",
        "Best PGS AUC",
        "Median PGS AUC",
        "Best AUC Gain vs Self",
        "Median AUC Gain vs Self",
    ]

    for summary in target_order:
        target_id = summary["target_icd"]
        target_trait = short_label(summary["target_trait"])
        rows = sorted(
            shortlist_by_target.get(target_id, []),
            key=lambda row: int(row["combined_shortlist_rank"]),
        )

        section_lines = [f"#### {target_id} — {target_trait}", ""]
        section_lines.append(
            f"- `Input Type`: {summary['input_type']}  "
            f"`Available Cross Trait Types`: {describe_cross_trait_types(rows, summary['streams_present']) or 'N/A'}"
        )
        section_lines.append(
            f"- `N Recommended Cross Traits`: {summary['n_shortlisted_pairs_total']}  "
            f"`Top Recommended Cross Trait`: {short_label(summary.get('top_cross_trait', '') or 'N/A')}"
        )
        section_lines.append("")

        if not rows:
            best_available = short_label(summary.get("best_available_cross_trait", "") or "N/A")
            best_available_type = describe_cross_trait_types(
                [{"cross_trait_type": "binary" if summary.get("best_available_stream") == "b2b" else "continuous"}]
                if summary.get("best_available_stream")
                else [],
                summary.get("best_available_stream", ""),
            ) or "N/A"
            best_available_tier = summary.get("best_available_tier", "") or "N/A"
            best_available_plaus = summary.get("best_available_plausibility", "") or "N/A"
            best_available_imp = summary.get("best_available_improvement", "") or "N/A"
            section_lines.append(
                f"No shortlisted cross trait. Best available candidate: "
                f"`{best_available}` (`{best_available_type}`, Plausibility `{best_available_plaus}`, "
                f"Score `{best_available_imp}`, previous Tier `{best_available_tier}`)."
            )
            section_lines.append("")
        else:
            label_map = unique_display_labels([row["cross_trait"] for row in rows])
            table_rows = []
            for row in rows:
                key = (
                    row["stream"],
                    row["target_id"],
                    row["cross_trait"],
                    row.get("cross_trait_code", ""),
                )
                stats = detail_stats.get(key, {})
                table_rows.append(
                    {
                        "Rank": row["combined_shortlist_rank"],
                        "Cross Trait Type": row["cross_trait_type"],
                        "Cross Trait": label_map.get(row["cross_trait"], short_label(row["cross_trait"])),
                        "Biological Plausibility": row["plausibility"],
                        "Why It Was Kept": row.get("plausibility_reason", ""),
                        "N Candidate PRS Models": stats.get("n_prs_models", row.get("n_models", "")),
                        "Best PGS ID": stats.get("best_pgs_id", ""),
                        "Best PGS AUC": format_number(stats.get("best_cross_auc", row.get("best_cross_metric", ""))),
                        "Median PGS AUC": format_number(stats.get("median_cross_auc")),
                        "Best AUC Gain vs Self": format_number(
                            stats.get("best_effective_improvement", row.get("best_improvement", ""))
                        ),
                        "Median AUC Gain vs Self": format_number(stats.get("median_effective_improvement")),
                    }
                )
            if summary["input_type"] == "A":
                for row in table_rows:
                    row.pop("Best AUC Gain vs Self", None)
                    row.pop("Median AUC Gain vs Self", None)
                section_lines.append(render_table(table_rows, type_a_headers).rstrip())
            else:
                section_lines.append(render_table(table_rows, type_b_headers).rstrip())
            section_lines.append("")

        block = "\n".join(section_lines)
        if summary["input_type"] == "A":
            type_a_sections.append(block)
        else:
            type_b_sections.append(block)

    return type_a_sections, type_b_sections


def generate_markdown():
    summary_rows = load_csv(SUMMARY_PATH)
    shortlist_rows = load_csv(SHORTLIST_PATH)
    stream_shortlist_rows = load_csv(B2B_SHORTLIST_PATH) + load_csv(B2C_SHORTLIST_PATH)
    detail_stats = load_detail_stats()

    reason_map = {}
    for row in stream_shortlist_rows:
        key = (
            row["stream"],
            row["target_id"],
            row["cross_trait"],
            row.get("cross_trait_code", ""),
        )
        reason_map[key] = row.get("plausibility_reason", "")

    for row in shortlist_rows:
        key = (
            row["stream"],
            row["target_id"],
            row["cross_trait"],
            row.get("cross_trait_code", ""),
        )
        row["plausibility_reason"] = reason_map.get(key, "")

    type_a_target_headers, type_a_targets, type_b_target_headers, type_b_targets = build_target_tables(summary_rows, shortlist_rows)
    type_a_sections, type_b_sections = build_cross_trait_sections(summary_rows, shortlist_rows, detail_stats)

    n_type_a = sum(1 for row in summary_rows if row["input_type"] == "A")
    n_type_b = sum(1 for row in summary_rows if row["input_type"] == "B")
    n_with_shortlist = sum(1 for row in summary_rows if row["shortlist_status"] == "has_recommended_cross_trait")
    n_without_shortlist = sum(1 for row in summary_rows if row["shortlist_status"] == "no_recommended_cross_trait")

    parts = [
        "# Final Binary-Input Cross-Trait Shortlist",
        "",
        "This document is generated from the current Phase 2 outputs for presentation use.",
        "",
        "## Scope",
        "",
        f"- Binary-input retained target universe: `{len(summary_rows)}`",
        f"- Type A target traits: `{n_type_a}`",
        f"- Type B target traits: `{n_type_b}`",
        f"- Targets with shortlisted cross traits: `{n_with_shortlist}`",
        f"- Targets without shortlisted cross traits: `{n_without_shortlist}`",
        "",
        "## Notes",
        "",
        "- `Type A target trait` means this target trait does not have a self AUC benchmark in Contribution1, so cross-trait selection is based on cross-trait PRS performance alone.",
        "- `Type B target trait` means this target trait does have a self AUC benchmark in Contribution1, so cross traits are compared against the target's own self PRS.",
        "- One ICD corresponds to one target trait. The long semicolon-separated source label is a synonym bundle, not multiple different target traits. This document shows only the first synonym as the short display name for readability.",
        "- `Available Cross Trait Types` means whether the final recommended cross traits for a target come from binary traits, continuous traits, or both.",
        "- For Type A cross traits, Phase 2 now keeps only candidates with `Best PGS AUC > 0.55`.",
        "- `Best PGS AUC` and `Median PGS AUC` are computed across all candidate PGS models under that cross trait.",
        "- For Type B, `AUC Gain vs Self` means `cross-trait best AUC - self-trait best AUC`.",
        "- `Why It Was Kept` is the current Phase 2 biological plausibility note, not an external causal validation result.",
        "",
        "## 1. Target Trait",
        "",
        "### 1.1 Type A Target Trait",
        "",
        render_table(type_a_targets, type_a_target_headers).rstrip(),
        "",
        "### 1.2 Type B Target Trait",
        "",
        render_table(type_b_targets, type_b_target_headers).rstrip(),
        "",
        "## 2. Target Trait's Cross Trait",
        "",
        "### 2.1 Type A Target Trait's Cross Trait",
        "",
        "\n".join(type_a_sections).rstrip(),
        "",
        "### 2.2 Type B Target Trait's Cross Trait",
        "",
        "\n".join(type_b_sections).rstrip(),
        "",
    ]

    OUTPUT_PATH.write_text("\n".join(parts) + "\n")
    print(f"Wrote presentation markdown to: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_markdown()
