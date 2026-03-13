"""
Generate manuscript-style comparison figures for the Contribution2
recommendation experiment.

The script reads the archived with-domain and without-domain summaries for the
same 30-disease benchmark and produces:

1. A paired standardized-position plot that compares the relative benchmark
   position of the selected model for each disease on a shared 0-100 scale.
2. A side-by-side heatmap that shows how often each trial landed on benchmark
   ranks Top1-Top5 or outside Top5.

Usage:
  python experiments/contribution2/recommendation/scripts/plot_with_vs_without_domain_figures.py
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
RECOMMENDATION_DIR = PROJECT_ROOT / "experiments" / "contribution2" / "recommendation"
DEFAULT_WITH_SUMMARY = (
    RECOMMENDATION_DIR
    / "runs"
    / "with-domain-gpt-5.2-t10"
    / "experiment_with_domain_summary.json"
)
DEFAULT_WITHOUT_SUMMARY = (
    RECOMMENDATION_DIR
    / "runs"
    / "without-domain-gpt-5.2-t10"
    / "experiment_without_domain_summary.json"
)
DEFAULT_OUTPUT_DIR = (
    RECOMMENDATION_DIR / "figures" / "with-vs-without-domain-gpt-5.2-t10"
)
OUTPUT_STEM_STANDARDIZED = "figure1_standardized_relative_position"
OUTPUT_STEM_HEATMAP = "figure2_top_rank_heatmap"
HEATMAP_COLUMNS = ["Top1", "Top2", "Top3", "Top4", "Top5", ">5"]
WITHOUT_COLOR = "#C17C00"
WITH_COLOR = "#00798C"
LINE_COLOR = "#B8BDC7"
DELTA_POSITIVE_COLOR = "#2A6F97"
DELTA_NEGATIVE_COLOR = "#8A3B12"


@dataclass(frozen=True)
class DiseaseComparison:
    ontology: str
    display_name: str
    n_models: int
    without_rank: int
    with_rank: int
    without_rank_label: str
    with_rank_label: str
    without_score_pct: float
    with_score_pct: float
    delta_score_pct: float


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--with-summary",
        type=Path,
        default=DEFAULT_WITH_SUMMARY,
        help="Path to experiment_with_domain_summary.json",
    )
    parser.add_argument(
        "--without-summary",
        type=Path,
        default=DEFAULT_WITHOUT_SUMMARY,
        help="Path to experiment_without_domain_summary.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where figure files will be written",
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["png", "pdf"],
        help="Image formats to save, e.g. png pdf",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Raster DPI for PNG output",
    )
    return parser.parse_args()


def _load_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Summary JSON not found: {path}")
    return json.loads(path.read_text())


def _display_name(ontology: str) -> str:
    if not ontology:
        return ontology
    return ontology[0].upper() + ontology[1:]


def _standardized_position_pct(rank: int, n_models: int) -> float:
    if n_models <= 1:
        return 100.0
    return 100.0 * (n_models - rank) / (n_models - 1)


def _build_comparison_rows(
    with_summary: dict[str, Any],
    without_summary: dict[str, Any],
) -> list[DiseaseComparison]:
    with_entries = {entry["ontology"]: entry for entry in with_summary["per_disease"]}
    without_entries = {entry["ontology"]: entry for entry in without_summary["per_disease"]}

    if set(with_entries) != set(without_entries):
        missing_with = sorted(set(without_entries) - set(with_entries))
        missing_without = sorted(set(with_entries) - set(without_entries))
        raise ValueError(
            "Disease sets do not match between summaries. "
            f"Missing in with-domain: {missing_with}; missing in without-domain: {missing_without}"
        )

    rows: list[DiseaseComparison] = []
    for ontology in sorted(with_entries):
        with_entry = with_entries[ontology]
        without_entry = without_entries[ontology]
        with_n_models = int(with_entry["n_models"])
        without_n_models = int(without_entry["n_models"])
        if with_n_models != without_n_models:
            raise ValueError(
                f"n_models mismatch for {ontology}: with={with_n_models}, without={without_n_models}"
            )
        with_rank = int(with_entry["modal_recommendation_rank"])
        without_rank = int(without_entry["modal_recommendation_rank"])
        with_score_pct = _standardized_position_pct(with_rank, with_n_models)
        without_score_pct = _standardized_position_pct(without_rank, with_n_models)
        rows.append(
            DiseaseComparison(
                ontology=ontology,
                display_name=_display_name(ontology),
                n_models=with_n_models,
                without_rank=without_rank,
                with_rank=with_rank,
                without_rank_label=str(without_entry["modal_recommendation_rank_label"]),
                with_rank_label=str(with_entry["modal_recommendation_rank_label"]),
                without_score_pct=without_score_pct,
                with_score_pct=with_score_pct,
                delta_score_pct=with_score_pct - without_score_pct,
            )
        )

    rows.sort(
        key=lambda row: (row.delta_score_pct, row.with_score_pct, row.display_name.lower()),
        reverse=True,
    )
    return rows


def _trial_rank_distribution(entry: dict[str, Any]) -> dict[str, float]:
    trial_details = entry.get("trial_recommendations_detailed", [])
    total_trials = len(trial_details)
    if total_trials == 0:
        return {column: 0.0 for column in HEATMAP_COLUMNS}

    distribution = {column: 0.0 for column in HEATMAP_COLUMNS}
    for trial in trial_details:
        rank = trial.get("rank")
        if rank is None:
            continue
        if rank <= 5:
            distribution[f"Top{int(rank)}"] += 1.0
        else:
            distribution[">5"] += 1.0

    return {column: value / total_trials for column, value in distribution.items()}


def _build_heatmap_frame(
    entries_by_ontology: dict[str, dict[str, Any]],
    order: list[DiseaseComparison],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for comparison in order:
        entry = entries_by_ontology[comparison.ontology]
        distribution = _trial_rank_distribution(entry)
        row: dict[str, Any] = {"Disease": comparison.display_name}
        for rank in range(1, 6):
            column = f"Top{rank}"
            row[column] = np.nan if comparison.n_models < rank else distribution[column]
        row[">5"] = np.nan if comparison.n_models <= 5 else distribution[">5"]
        rows.append(row)
    return pd.DataFrame(rows).set_index("Disease")


def _summary_text(with_summary: dict[str, Any], without_summary: dict[str, Any]) -> str:
    with_mean = with_summary["nrs"]["modal_mean_nrs"] * 100.0
    without_mean = without_summary["nrs"]["modal_mean_nrs"] * 100.0
    with_hit1 = with_summary["modal_hit_at_k"]["1"]["accuracy"] * 100.0
    without_hit1 = without_summary["modal_hit_at_k"]["1"]["accuracy"] * 100.0
    return (
        f"Mean standardized score: with {with_mean:.1f} vs without {without_mean:.1f}\n"
        f"Modal Hit@1: with {with_hit1:.1f}% vs without {without_hit1:.1f}%"
    )


def _save_figure(fig: plt.Figure, stem: str, output_dir: Path, formats: list[str], dpi: int) -> list[Path]:
    output_paths: list[Path] = []
    for fmt in formats:
        fmt_normalized = fmt.lower()
        output_path = output_dir / f"{stem}.{fmt_normalized}"
        save_kwargs: dict[str, Any] = {"bbox_inches": "tight"}
        if fmt_normalized in {"png", "jpg", "jpeg", "tiff"}:
            save_kwargs["dpi"] = dpi
        fig.savefig(output_path, **save_kwargs)
        output_paths.append(output_path)
    return output_paths


def _plot_standardized_position(
    rows: list[DiseaseComparison],
    with_summary: dict[str, Any],
    without_summary: dict[str, Any],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> list[Path]:
    sns.set_theme(style="whitegrid")
    height = max(10.0, 0.36 * len(rows) + 2.6)
    fig = plt.figure(figsize=(13.8, height))
    grid = fig.add_gridspec(nrows=1, ncols=2, width_ratios=[5.8, 1.4], wspace=0.02)
    ax = fig.add_subplot(grid[0, 0])
    ax_rank = fig.add_subplot(grid[0, 1], sharey=ax)

    y_positions = np.arange(len(rows))
    for x in (0, 25, 50, 75, 100):
        ax.axvline(x, color="#E6E8EC", linewidth=1.0, zorder=0)

    for y, row in zip(y_positions, rows):
        line_color = DELTA_POSITIVE_COLOR if row.delta_score_pct >= 0 else DELTA_NEGATIVE_COLOR
        ax.plot(
            [row.without_score_pct, row.with_score_pct],
            [y, y],
            color=line_color,
            alpha=0.35,
            linewidth=2.0,
            solid_capstyle="round",
            zorder=1,
        )

    ax.scatter(
        [row.without_score_pct for row in rows],
        y_positions,
        s=54,
        color=WITHOUT_COLOR,
        edgecolor="white",
        linewidth=0.7,
        label="Without domain knowledge",
        zorder=3,
    )
    ax.scatter(
        [row.with_score_pct for row in rows],
        y_positions,
        s=54,
        color=WITH_COLOR,
        edgecolor="white",
        linewidth=0.7,
        label="With domain knowledge",
        zorder=4,
    )

    ax.set_xlim(-2, 102)
    ax.set_xlabel("Standardized relative benchmark position (%)")
    ax.set_yticks(y_positions)
    ax.set_yticklabels([row.display_name for row in rows], fontsize=9)
    ax.set_ylabel("Disease")
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.grid(axis="y", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", frameon=False)

    improved = sum(row.delta_score_pct > 0 for row in rows)
    worsened = sum(row.delta_score_pct < 0 for row in rows)
    unchanged = len(rows) - improved - worsened
    fig.suptitle(
        "Figure 1. Standardized benchmark position of the selected model for each disease",
        x=0.42,
        y=0.985,
        fontsize=15,
        fontweight="bold",
    )
    ax.set_title(
        f"Shared 0-100 scale across diseases. Improved: {improved}; worsened: {worsened}; unchanged: {unchanged}",
        fontsize=10.5,
        pad=10,
    )

    ax.text(
        0.015,
        0.99,
        _summary_text(with_summary, without_summary),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "#F7F8FA", "edgecolor": "#D8DCE3"},
    )

    ax_rank.set_xlim(0, 1)
    ax_rank.set_xticks([])
    ax_rank.tick_params(axis="y", left=False, labelleft=False)
    for spine in ax_rank.spines.values():
        spine.set_visible(False)
    ax_rank.set_title("Raw rank", fontsize=10.5, pad=10)
    for y, row in zip(y_positions, rows):
        ax_rank.text(
            0.02,
            y,
            f"{row.without_rank_label} -> {row.with_rank_label}",
            va="center",
            ha="left",
            fontsize=8.2,
            color="#4C5667",
        )

    ax.invert_yaxis()
    fig.text(
        0.06,
        0.02,
        "Score = 100 x (M - r) / (M - 1), where M is the candidate count for that disease and r is the benchmark rank of the selected model.",
        ha="left",
        va="bottom",
        fontsize=9,
        color="#4C5667",
    )
    fig.subplots_adjust(left=0.29, right=0.97, bottom=0.07, top=0.93)

    output_paths = _save_figure(
        fig,
        OUTPUT_STEM_STANDARDIZED,
        output_dir=output_dir,
        formats=formats,
        dpi=dpi,
    )
    plt.close(fig)
    return output_paths


def _plot_heatmap(
    rows: list[DiseaseComparison],
    with_summary: dict[str, Any],
    without_summary: dict[str, Any],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> list[Path]:
    sns.set_theme(style="white")
    with_entries = {entry["ontology"]: entry for entry in with_summary["per_disease"]}
    without_entries = {entry["ontology"]: entry for entry in without_summary["per_disease"]}

    without_frame = _build_heatmap_frame(without_entries, rows)
    with_frame = _build_heatmap_frame(with_entries, rows)

    cmap = LinearSegmentedColormap.from_list(
        "with_without_heatmap",
        ["#F6F8FB", "#B8D8E8", "#4C90B0", "#0C4A6E"],
    )
    cmap.set_bad("#EFEFEF")

    height = max(10.0, 0.34 * len(rows) + 2.8)
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(11.5, height),
        sharey=True,
        gridspec_kw={"wspace": 0.08},
    )
    fig.suptitle(
        "Figure 2. Trial frequency heatmap of benchmark ranks by disease",
        y=0.985,
        fontsize=15,
        fontweight="bold",
    )

    common_heatmap_kwargs = {
        "cmap": cmap,
        "vmin": 0.0,
        "vmax": 1.0,
        "linewidths": 0.6,
        "linecolor": "white",
        "cbar": False,
    }

    sns.heatmap(without_frame, ax=axes[0], **common_heatmap_kwargs)
    sns.heatmap(with_frame, ax=axes[1], **common_heatmap_kwargs)

    axes[0].set_title("Without domain knowledge", fontsize=11.5, pad=10)
    axes[1].set_title("With domain knowledge", fontsize=11.5, pad=10)
    axes[0].set_xlabel("Benchmark rank bucket")
    axes[1].set_xlabel("Benchmark rank bucket")
    axes[0].set_ylabel("Disease")
    axes[1].set_ylabel("")
    axes[1].tick_params(axis="y", left=False, labelleft=False)
    for ax in axes:
        ax.tick_params(axis="x", rotation=0)
        ax.tick_params(axis="y", labelsize=9)

    scalar_mappable = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0.0, vmax=1.0))
    scalar_mappable.set_array([])
    colorbar = fig.colorbar(
        scalar_mappable,
        ax=axes,
        fraction=0.028,
        pad=0.02,
    )
    colorbar.set_label("Trial frequency across 10 runs")

    fig.text(
        0.06,
        0.018,
        "Grey cells indicate that the benchmark rank is not applicable for that disease because the candidate pool is smaller than the column rank.",
        ha="left",
        va="bottom",
        fontsize=9,
        color="#4C5667",
    )
    fig.subplots_adjust(left=0.31, right=0.92, bottom=0.07, top=0.93)

    output_paths = _save_figure(
        fig,
        OUTPUT_STEM_HEATMAP,
        output_dir=output_dir,
        formats=formats,
        dpi=dpi,
    )
    plt.close(fig)
    return output_paths


def main() -> None:
    args = _parse_args()
    with_summary = _load_summary(args.with_summary)
    without_summary = _load_summary(args.without_summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = _build_comparison_rows(with_summary, without_summary)
    output_paths = []
    output_paths.extend(
        _plot_standardized_position(
            rows,
            with_summary=with_summary,
            without_summary=without_summary,
            output_dir=args.output_dir,
            formats=args.formats,
            dpi=args.dpi,
        )
    )
    output_paths.extend(
        _plot_heatmap(
            rows,
            with_summary=with_summary,
            without_summary=without_summary,
            output_dir=args.output_dir,
            formats=args.formats,
            dpi=args.dpi,
        )
    )

    print("Generated figure files:")
    for path in output_paths:
        print(path)


if __name__ == "__main__":
    main()
