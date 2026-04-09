from __future__ import annotations

import csv
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from experiments.contribution3.transfer.common import (
    BENCHMARK_FAMILIES,
    TRANSFER_DIR,
    condition_recommendations_json,
    condition_results_json,
    evaluation_dir,
)

CONDITIONS = ("gpt-only", "all-tools")
HIT_PERCENTS = (5, 10, 15, 20, 25)
DOCS_DIR = TRANSFER_DIR / "docs"
OVERVIEW_REPORT = DOCS_DIR / "latest_end_to_end_report.md"
PER_TARGET_REPORT = DOCS_DIR / "latest_per_target_comparison.md"


@dataclass(frozen=True)
class RunArtifacts:
    benchmark_family: str
    condition: str
    summary_path: Path
    detail_path: Path
    results_path: Path
    recommendations_path: Path
    summary: dict[str, Any]
    detail_rows: list[dict[str, str]]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    return float(text)


def _coerce_int(value: Any) -> int | None:
    number = _coerce_float(value)
    if number is None:
        return None
    return int(number)


def _condense_text(value: Any) -> str:
    text = " ".join(str(value or "").split()).strip()
    if not text:
        return "—"
    words = text.split()
    if len(words) % 2 == 0:
        half = len(words) // 2
        if words[:half] == words[half:]:
            return " ".join(words[:half])
    return text


def _escape_md(value: Any) -> str:
    return _condense_text(value).replace("|", "\\|")


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.2f}%"


def _fmt_pct_delta(value: float | None) -> str:
    if value is None:
        return "—"
    sign = "+" if value > 0 else ""
    return f"{sign}{value * 100:.2f}pp"


def _doc_link(path: Path) -> str:
    rel = os.path.relpath(path, DOCS_DIR)
    label = os.path.relpath(path, TRANSFER_DIR).replace(os.sep, "/")
    return f"[{label}]({rel})"


def _target_sort_key(target_id: str) -> tuple[str, int, str]:
    text = str(target_id or "").strip()
    prefix = "".join(ch for ch in text if ch.isalpha())
    suffix = "".join(ch for ch in text if ch.isdigit())
    return (prefix, int(suffix) if suffix else 0, text)


def _selection_text(row: dict[str, str]) -> str:
    if not row:
        return "—"
    trait = _condense_text(row.get("matched_cross_trait"))
    model = _condense_text(row.get("recommended_model_id"))
    status = _condense_text(row.get("status"))
    selection = f"{trait} -> {model}"
    if status != "evaluated":
        selection = f"{selection} [{status}]"
    return selection


def _official_hit_value(summary: dict[str, Any], percent: int) -> float | None:
    return _coerce_float(
        (summary.get("official_metrics") or {})
        .get("hit_at_percent", {})
        .get(f"top_{percent}pct")
    )


def _is_top_percent_hit(row: dict[str, str], percent: int) -> bool:
    if row.get("status") != "evaluated":
        return False
    rank = _coerce_float(row.get("selected_model_rank"))
    candidate_count = _coerce_int(row.get("candidate_count"))
    if rank is None or candidate_count is None or candidate_count <= 0:
        return False
    threshold = max(1, math.ceil(candidate_count * (percent / 100.0)))
    return rank <= threshold


def _hit_status_text(row: dict[str, str], percent: int) -> str:
    if row.get("status") != "evaluated":
        return "N/A"
    return "Yes" if _is_top_percent_hit(row, percent) else "No"


def _best_hit_tier(row: dict[str, str]) -> str:
    if row.get("status") != "evaluated":
        return "N/A"
    for percent in HIT_PERCENTS:
        if _is_top_percent_hit(row, percent):
            return f"Top {percent}%"
    return ">Top 25%"


def _best_hit_tier_score(tier: str) -> int:
    ordering = {
        "Top 5%": 0,
        "Top 10%": 1,
        "Top 15%": 2,
        "Top 20%": 3,
        "Top 25%": 4,
        ">Top 25%": 5,
        "N/A": 6,
    }
    return ordering.get(tier, 6)


def _better_hit_tier(gpt_row: dict[str, str], all_tools_row: dict[str, str]) -> str:
    gpt_tier = _best_hit_tier(gpt_row)
    all_tools_tier = _best_hit_tier(all_tools_row)
    gpt_score = _best_hit_tier_score(gpt_tier)
    all_tools_score = _best_hit_tier_score(all_tools_tier)
    if gpt_score == all_tools_score:
        return "tie"
    return "all-tools" if all_tools_score < gpt_score else "gpt-only"


def _load_artifacts() -> dict[tuple[str, str], RunArtifacts]:
    artifacts: dict[tuple[str, str], RunArtifacts] = {}
    missing: list[Path] = []
    for family in BENCHMARK_FAMILIES:
        for condition in CONDITIONS:
            summary_path = evaluation_dir(family) / f"{condition}__end_to_end_eval_summary.json"
            detail_path = evaluation_dir(family) / f"{condition}__end_to_end_eval_detail.csv"
            results_path = condition_results_json(condition, benchmark_family=family)
            recommendations_path = condition_recommendations_json(condition, benchmark_family=family)
            for path in (summary_path, detail_path, results_path, recommendations_path):
                if not path.exists():
                    missing.append(path)
            if missing:
                continue
            artifacts[(family, condition)] = RunArtifacts(
                benchmark_family=family,
                condition=condition,
                summary_path=summary_path,
                detail_path=detail_path,
                results_path=results_path,
                recommendations_path=recommendations_path,
                summary=_load_json(summary_path),
                detail_rows=_load_csv_rows(detail_path),
            )
    if missing:
        raise FileNotFoundError(
            "Missing transfer evaluation artifacts. Run the transfer batch pipeline first:\n"
            + "\n".join(str(path) for path in missing)
        )
    return artifacts


def _macro_hit(artifacts: dict[tuple[str, str], RunArtifacts], condition: str, percent: int) -> float | None:
    values = [
        _official_hit_value(artifacts[(family, condition)].summary, percent)
        for family in BENCHMARK_FAMILIES
    ]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return sum(values) / len(values)


def _family_hit(
    artifacts: dict[tuple[str, str], RunArtifacts],
    family: str,
    condition: str,
    percent: int,
) -> float | None:
    return _official_hit_value(artifacts[(family, condition)].summary, percent)


def _condition_hit_counts(
    artifacts: dict[tuple[str, str], RunArtifacts],
    family: str,
    condition: str,
) -> dict[int, int]:
    rows = artifacts[(family, condition)].detail_rows
    return {
        percent: sum(1 for row in rows if _is_top_percent_hit(row, percent))
        for percent in HIT_PERCENTS
    }


def _source_file_lines(artifacts: dict[tuple[str, str], RunArtifacts]) -> list[str]:
    lines: list[str] = []
    for family in BENCHMARK_FAMILIES:
        lines.append(f"### `{family}`")
        lines.append("")
        for condition in CONDITIONS:
            artifact = artifacts[(family, condition)]
            lines.append(
                f"- `{condition}`: "
                f"{_doc_link(artifact.summary_path)}, "
                f"{_doc_link(artifact.detail_path)}, "
                f"{_doc_link(artifact.results_path)}, "
                f"{_doc_link(artifact.recommendations_path)}"
            )
        lines.append("")
    return lines


def _build_overview_report(artifacts: dict[tuple[str, str], RunArtifacts]) -> str:
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    deltas = {
        percent: (_macro_hit(artifacts, "all-tools", percent) or 0.0)
        - (_macro_hit(artifacts, "gpt-only", percent) or 0.0)
        for percent in HIT_PERCENTS
    }
    better = [percent for percent in HIT_PERCENTS if deltas[percent] > 0]
    worse = [percent for percent in HIT_PERCENTS if deltas[percent] < 0]
    same = [percent for percent in HIT_PERCENTS if deltas[percent] == 0]

    lines: list[str] = []
    lines.append("# Contribution3 Transfer: Latest End-to-End Evaluation Report")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(
        "This report is generated from the latest completed transfer batch outputs under "
        "`experiments/contribution3/transfer/runs/tool_calling_agent`."
    )
    lines.append("")
    lines.append(f"- Generated at: `{generated_at}`")
    lines.append("- Conditions compared: `gpt-only` vs `all-tools`")
    lines.append(f"- Benchmark families: `{BENCHMARK_FAMILIES[0]}`, `{BENCHMARK_FAMILIES[1]}`")
    lines.append("- This report only uses the native `official_metrics.hit_at_percent` outputs from `evaluate_end_to_end.py`.")
    lines.append("- Other c3 metrics are intentionally omitted here.")
    lines.append("- Companion per-target report: "
                 f"[latest_per_target_comparison.md]({PER_TARGET_REPORT.name})")
    lines.append("")
    lines.append("## Transfer Study Design")
    lines.append("")
    lines.append("This comparison keeps the benchmark target set fixed and changes only the transfer / recommendation condition.")
    lines.append("")
    lines.append("| Arm | Transfer step | Recommendation step | What it tests |")
    lines.append("| --- | --- | --- | --- |")
    lines.append("| `gpt-only` | LLM-only cross-trait transfer without tool evidence | Contribution2 recommendation without domain knowledge | Parametric transfer baseline |")
    lines.append("| `all-tools` | Tool-assisted cross-trait transfer with evidence tools | Contribution2 recommendation with domain knowledge | Value of tool-assisted transfer plus domain-informed model selection |")
    lines.append("")
    lines.append("## High-Level Outcome")
    lines.append("")
    lines.append(
        f"- `all-tools` is better at: "
        f"{', '.join(f'`Top {percent}%`' for percent in better) if better else '`none`'}."
    )
    lines.append(
        f"- `gpt-only` is better at: "
        f"{', '.join(f'`Top {percent}%`' for percent in worse) if worse else '`none`'}."
    )
    lines.append(
        f"- Tied at: "
        f"{', '.join(f'`Top {percent}%`' for percent in same) if same else '`none`'}."
    )
    lines.append("")
    lines.append("## Percentile Hit Definition")
    lines.append("")
    lines.append("- Inputs: `M` = number of benchmark-eligible PGS models for the target in the full AoU matrix; `r` = tie-averaged benchmark rank of the selected PGS among those `M` models.")
    lines.append("- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.")
    lines.append("- For each threshold, define `c_q = max(1, ceil(q/100 * M))`.")
    lines.append("- A selection counts as `Top q% Hit` if the AoU benchmark rank satisfies `r <= c_q`.")
    lines.append("- The values below come directly from `official_metrics.hit_at_percent` in the c3 summary JSON.")
    lines.append("- Larger is better.")
    lines.append("")
    for percent in HIT_PERCENTS:
        lines.append(f"## Top {percent}% Hit")
        lines.append("")
        lines.append(
            f"- `gpt-only`: `overall average = {_fmt_pct(_macro_hit(artifacts, 'gpt-only', percent))}`; "
            + "; ".join(
                f"`{family}={_fmt_pct(_family_hit(artifacts, family, 'gpt-only', percent))}`"
                for family in BENCHMARK_FAMILIES
            )
        )
        lines.append(
            f"- `all-tools`: `overall average = {_fmt_pct(_macro_hit(artifacts, 'all-tools', percent))}`; "
            + "; ".join(
                f"`{family}={_fmt_pct(_family_hit(artifacts, family, 'all-tools', percent))}`"
                for family in BENCHMARK_FAMILIES
            )
        )
        lines.append(
            f"- `delta (all-tools - gpt-only)`: `overall average = {_fmt_pct_delta(deltas[percent])}`; "
            + "; ".join(
                f"`{family}={_fmt_pct_delta((_family_hit(artifacts, family, 'all-tools', percent) or 0.0) - (_family_hit(artifacts, family, 'gpt-only', percent) or 0.0))}`"
                for family in BENCHMARK_FAMILIES
            )
        )
        lines.append("")
    lines.append("## Hit Summary Table")
    lines.append("")
    lines.append("| Threshold | gpt-only Overall Average | all-tools Overall Average | Delta (all-tools - gpt-only) |")
    lines.append("| --- | ---: | ---: | ---: |")
    for percent in HIT_PERCENTS:
        lines.append(
            f"| `Top {percent}%` | {_fmt_pct(_macro_hit(artifacts, 'gpt-only', percent))} | "
            f"{_fmt_pct(_macro_hit(artifacts, 'all-tools', percent))} | {_fmt_pct_delta(deltas[percent])} |"
        )
    lines.append("")
    lines.append("## Family Breakdown")
    lines.append("")
    lines.append("| Threshold | binary_to_binary gpt-only | binary_to_binary all-tools | binary_to_continuous gpt-only | binary_to_continuous all-tools |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for percent in HIT_PERCENTS:
        lines.append(
            f"| `Top {percent}%` | "
            f"{_fmt_pct(_family_hit(artifacts, 'binary_to_binary', 'gpt-only', percent))} | "
            f"{_fmt_pct(_family_hit(artifacts, 'binary_to_binary', 'all-tools', percent))} | "
            f"{_fmt_pct(_family_hit(artifacts, 'binary_to_continuous', 'gpt-only', percent))} | "
            f"{_fmt_pct(_family_hit(artifacts, 'binary_to_continuous', 'all-tools', percent))} |"
        )
    lines.append("")
    lines.append("## Source Files")
    lines.append("")
    lines.extend(_source_file_lines(artifacts))
    return "\n".join(lines).strip() + "\n"


def _build_per_target_report(artifacts: dict[tuple[str, str], RunArtifacts]) -> str:
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines: list[str] = []
    lines.append("# Contribution3 Transfer: Per-Target Hit Report")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This report is a target-by-target detailed hit report for the current transfer evaluation.")
    lines.append("")
    lines.append(f"- Generated at: `{generated_at}`")
    lines.append("- It only focuses on `Top 5/10/15/20/25% Hit`.")
    lines.append("- `Best Hit Tier` means the smallest percentile threshold hit by the selected model.")
    lines.append("- `Better Hit Tier` compares only the hit-tier profile, not AUC/GPR or any other metric.")
    lines.append("")

    for family in BENCHMARK_FAMILIES:
        gpt_rows = {
            row["target_id"]: row for row in artifacts[(family, "gpt-only")].detail_rows
        }
        all_tools_rows = {
            row["target_id"]: row for row in artifacts[(family, "all-tools")].detail_rows
        }
        target_ids = sorted(set(gpt_rows) | set(all_tools_rows), key=_target_sort_key)
        better_counts = {
            label: sum(
                1
                for target_id in target_ids
                if _better_hit_tier(gpt_rows.get(target_id, {}), all_tools_rows.get(target_id, {})) == label
            )
            for label in ("all-tools", "gpt-only", "tie")
        }
        gpt_hit_counts = _condition_hit_counts(artifacts, family, "gpt-only")
        all_tools_hit_counts = _condition_hit_counts(artifacts, family, "all-tools")

        lines.append(f"## `{family}`")
        lines.append("")
        lines.append(
            f"- Targets: `{len(target_ids)}`; "
            f"`all-tools better={better_counts['all-tools']}`, "
            f"`gpt-only better={better_counts['gpt-only']}`, "
            f"`tie={better_counts['tie']}`."
        )
        lines.append(
            "- `gpt-only` hit counts: "
            + ", ".join(
                f"`Top {percent}% = {gpt_hit_counts[percent]}/{len(target_ids)}`"
                for percent in HIT_PERCENTS
            )
        )
        lines.append(
            "- `all-tools` hit counts: "
            + ", ".join(
                f"`Top {percent}% = {all_tools_hit_counts[percent]}/{len(target_ids)}`"
                for percent in HIT_PERCENTS
            )
        )
        lines.append("")
        lines.append(
            "| Target ID | Target | gpt-only Transfer -> Model | gpt-only Best Hit Tier | "
            "gpt-only Top 5% | Top 10% | Top 15% | Top 20% | Top 25% | "
            "all-tools Transfer -> Model | all-tools Best Hit Tier | "
            "all-tools Top 5% | Top 10% | Top 15% | Top 20% | Top 25% | Better Hit Tier |"
        )
        lines.append(
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
        )
        for target_id in target_ids:
            gpt_row = gpt_rows.get(target_id, {})
            all_tools_row = all_tools_rows.get(target_id, {})
            target = _condense_text(
                gpt_row.get("target_description") or all_tools_row.get("target_description")
            )
            lines.append(
                f"| `{target_id}` | {_escape_md(target)} | "
                f"{_escape_md(_selection_text(gpt_row))} | `{_best_hit_tier(gpt_row)}` | "
                f"`{_hit_status_text(gpt_row, 5)}` | `{_hit_status_text(gpt_row, 10)}` | "
                f"`{_hit_status_text(gpt_row, 15)}` | `{_hit_status_text(gpt_row, 20)}` | `{_hit_status_text(gpt_row, 25)}` | "
                f"{_escape_md(_selection_text(all_tools_row))} | `{_best_hit_tier(all_tools_row)}` | "
                f"`{_hit_status_text(all_tools_row, 5)}` | `{_hit_status_text(all_tools_row, 10)}` | "
                f"`{_hit_status_text(all_tools_row, 15)}` | `{_hit_status_text(all_tools_row, 20)}` | `{_hit_status_text(all_tools_row, 25)}` | "
                f"`{_better_hit_tier(gpt_row, all_tools_row)}` |"
            )
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def generate_markdown_reports() -> dict[str, Path]:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    artifacts = _load_artifacts()
    OVERVIEW_REPORT.write_text(_build_overview_report(artifacts), encoding="utf-8")
    PER_TARGET_REPORT.write_text(_build_per_target_report(artifacts), encoding="utf-8")
    return {
        "overview": OVERVIEW_REPORT,
        "per_target": PER_TARGET_REPORT,
    }
