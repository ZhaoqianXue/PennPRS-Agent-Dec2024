"""
Generate figures for Catalog Search vs Catalog Search + Domain Knowledge comparison.

1. Heatmap: Top 40 PRS models by AOU AUC per disease.
   X-axis: Top 40 PRS models (Rank 1-40 by AOU benchmark). Gray fill for cells
        where the disease has fewer than 40 candidate models.
Y-axis: Disease (one row per disease), ordered by Results by Disease.
Color:  AOU AUC (continuous colormap).
Icons:  One ○ and one △ per disease row (not per cell):
    - X-position = mean benchmark rank of that method's selections (weighted by repeats).
    - Number next to each marker = mean benchmark rank (x-axis value), not trial count.
    - If both means tie, △ is drawn left of ○.

2. NRS scatter: Horizontal scatter plot.
   X-axis: Normalized Ranking Score (NRS, 0-1).
   Y-axis: Disease (one row per disease).
   Two points per disease: Catalog Search Only (orange) and Catalog Search + Domain Knowledge (teal).

Usage:
  python experiments/contribution2/recommendation/scripts/plot_top10_auc_heatmap.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RECOMMENDATION_DIR = PROJECT_ROOT / "experiments" / "contribution2" / "recommendation"
DEFAULT_WITH_SUMMARY = (
    RECOMMENDATION_DIR
    / "runs"
    / "with-domain-gpt-5.2-t10__75disease__with-dk-only-20260323-171012"
    / "experiment_with_domain_summary.json"
)
DEFAULT_WITHOUT_SUMMARY = (
    RECOMMENDATION_DIR
    / "runs"
    / "without-domain-gpt-5.2-t10__75disease__three-arm-rerun-20260316"
    / "experiment_without_domain_summary.json"
)
DEFAULT_OUTPUT_DIR = RECOMMENDATION_DIR / "figures" / "with-vs-without-domain-gpt-5.2-t10"
OUTPUT_STEM = "figure_top10_auc_heatmap"
OUTPUT_STEM_NRS = "figure_nrs_comparison"
TOP_K = 40

# Legend labels: circle = CS, triangle = DK (one marker per method per row at mean rank)
ICON_CS_ONLY = ("o", "Catalog Search Only")
ICON_DK_ONLY = ("^", "Catalog Search + Domain Knowledge")


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


def _sort_disease_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Match Results by Disease order: n_models desc, then ontology asc."""
    return sorted(rows, key=lambda row: (-row["n_models"], row["ontology"]))


def _display_name(ontology: str) -> str:
    if not ontology:
        return ontology
    return ontology[0].upper() + ontology[1:]


def _build_heatmap_data(
    with_summary: dict[str, Any],
    without_summary: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """
    Build AUC matrix and per-row mean-rank markers for overlay.
    Returns: (auc_frame, row_markers_df, disease_order)
    """
    with_entries = {e["ontology"]: e for e in with_summary["per_disease"]}
    without_entries = {e["ontology"]: e for e in without_summary["per_disease"]}

    if set(with_entries) != set(without_entries):
        missing_with = sorted(set(without_entries) - set(with_entries))
        missing_without = sorted(set(with_entries) - set(without_entries))
        raise ValueError(
            "Disease sets do not match between summaries. "
            f"Missing in with-domain: {missing_with}; missing in without-domain: {missing_without}"
        )

    sorted_rows = _sort_disease_rows(list(with_entries.values()))
    disease_order = [_display_name(row["ontology"]) for row in sorted_rows]

    auc_rows: list[dict[str, Any]] = []
    row_marker_rows: list[dict[str, Any]] = []

    for row in sorted_rows:
        ontology = row["ontology"]
        with_entry = with_entries[ontology]
        without_entry = without_entries[ontology]

        n_models = int(with_entry["n_models"])
        ranked_ids = list(with_entry.get("benchmark_ranked_ids") or [])
        auc_by_id = dict(with_entry.get("benchmark_auc_by_id") or {})
        cs_trials = [str(x) for x in (without_entry.get("trial_recommendations") or [])]
        dk_trials = [str(x) for x in (with_entry.get("trial_recommendations") or [])]

        auc_row: dict[str, Any] = {"Disease": _display_name(ontology)}

        for rank in range(1, TOP_K + 1):
            col = f"Rank {rank}"
            if rank > n_models:
                auc_row[col] = np.nan
            else:
                pgs_id = ranked_ids[rank - 1] if rank <= len(ranked_ids) else None
                if pgs_id:
                    auc_row[col] = auc_by_id.get(pgs_id, np.nan)
                else:
                    auc_row[col] = np.nan

        # One circle / triangle per row: mean rank of selections (frequency-weighted via repeated ids)
        rank_by_id: dict[str, int] = {}
        for ridx, pid in enumerate(ranked_ids, start=1):
            if pid:
                rank_by_id[str(pid)] = ridx
        cs_ranks = [rank_by_id[t] for t in cs_trials if t in rank_by_id]
        dk_ranks = [rank_by_id[t] for t in dk_trials if t in rank_by_id]
        mean_cs = float(np.mean(cs_ranks)) if cs_ranks else np.nan
        mean_dk = float(np.mean(dk_ranks)) if dk_ranks else np.nan
        row_marker_rows.append(
            {
                "Disease": _display_name(ontology),
                "mean_cs_rank": mean_cs,
                "mean_dk_rank": mean_dk,
                "n_cs": len(cs_ranks),
                "n_dk": len(dk_ranks),
            }
        )

        auc_rows.append(auc_row)

    auc_frame = pd.DataFrame(auc_rows).set_index("Disease")
    row_markers_df = pd.DataFrame(row_marker_rows).set_index("Disease")

    return auc_frame, row_markers_df, disease_order


def _mean_rank_to_x(mean_rank: float) -> float:
    """Map mean benchmark rank (1-based) to seaborn heatmap x coordinate (cell center)."""
    return (mean_rank - 1.0) + 0.5


def _format_mean_rank_label(mean_rank: float) -> str:
    """Human-readable label for mean rank (1..TOP_K) next to markers."""
    if np.isnan(mean_rank):
        return ""
    r = float(mean_rank)
    if abs(r - round(r)) < 1e-5:
        return str(int(round(r)))
    return f"{r:.1f}"


def _plot_heatmap(
    auc_frame: pd.DataFrame,
    row_markers_df: pd.DataFrame,
    disease_order: list[str],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> list[Path]:
    sns.set_theme(style="white")
    cmap = plt.cm.viridis
    cmap = cmap.copy()
    cmap.set_bad("#B0B0B0")  # Gray for NaN (disease has < rank models)

    all_vals = auc_frame.values.flatten()
    valid = all_vals[~np.isnan(all_vals)]
    # Use full range of AUC values that appear in the heatmap
    vmin = float(np.min(valid)) if len(valid) > 0 else 0.5
    vmax = float(np.max(valid)) if len(valid) > 0 else 0.9

    height = max(12.0, 0.26 * len(disease_order) + 4.0)
    width = 1.15 * TOP_K + 1.0  # Scale width with number of rank columns
    fig = plt.figure(figsize=(width, height))
    gs = fig.add_gridspec(nrows=2, ncols=1, height_ratios=[0.08, 0.92], hspace=0.01)

    # Top row: Selection method legend (avoids overlap with colorbar)
    ax_legend = fig.add_subplot(gs[0])
    ax_legend.set_axis_off()

    from matplotlib.lines import Line2D

    ICON_COLOR = "#1a1a1a"
    ICON_EDGE = "white"
    legend_elements = [
        Line2D(
            [0], [0], marker="o", color="w", markerfacecolor=ICON_COLOR,
            markeredgecolor=ICON_EDGE, markeredgewidth=1.0, markersize=12,
            label=ICON_CS_ONLY[1],
        ),
        Line2D(
            [0], [0], marker="^", color="w", markerfacecolor=ICON_COLOR,
            markeredgecolor=ICON_EDGE, markeredgewidth=1.0, markersize=12,
            label=ICON_DK_ONLY[1],
        ),
    ]
    ax_legend.legend(
        handles=legend_elements,
        loc="center left",
        ncol=3,
        fontsize=13,
        title="Selection method",
        title_fontsize=14,
    )

    # Bottom row: heatmap
    ax = fig.add_subplot(gs[1])
    sns.heatmap(
        auc_frame,
        ax=ax,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        linewidths=0.4,
        linecolor="white",
        cbar_kws={
            "label": "AOU AUC",
            "shrink": 0.5,
            "aspect": 30,
        },
        annot=False,
    )
    # Enlarge colorbar label and tick fonts; show min, max, and intermediate ticks
    cbar_ticks = np.linspace(vmin, vmax, 6)
    for cax in fig.axes:
        if cax not in (ax, ax_legend):
            cax.tick_params(labelsize=12)
            cax.set_ylabel(cax.get_ylabel(), fontsize=13)
            cax.set_yticks(cbar_ticks)
            cax.set_yticklabels([f"{t:.2f}" for t in cbar_ticks])

    # One ○ and one △ per row at mean selection rank; tie -> △ left, ○ right
    ICON_EDGE_WIDTH = 1.2
    COUNT_OFFSET = 0.15
    TIE_X_OFFSET = 0.14

    for i, disease in enumerate(auc_frame.index):
        row = row_markers_df.loc[disease]
        mean_cs = float(row["mean_cs_rank"]) if pd.notna(row["mean_cs_rank"]) else np.nan
        mean_dk = float(row["mean_dk_rank"]) if pd.notna(row["mean_dk_rank"]) else np.nan
        n_cs = int(row["n_cs"])
        n_dk = int(row["n_dk"])

        tie = (
            not np.isnan(mean_cs)
            and not np.isnan(mean_dk)
            and abs(mean_cs - mean_dk) < 1e-6
        )
        x_cs = _mean_rank_to_x(mean_cs) if not np.isnan(mean_cs) else np.nan
        x_dk = _mean_rank_to_x(mean_dk) if not np.isnan(mean_dk) else np.nan
        if tie:
            x_dk -= TIE_X_OFFSET
            x_cs += TIE_X_OFFSET

        y = i + 0.5

        def _draw_marker(x: float, marker: str, n_sel: int, mean_rank: float) -> None:
            if np.isnan(x) or n_sel <= 0 or np.isnan(mean_rank):
                return
            ax.scatter(
                x,
                y,
                marker=marker,
                s=55,
                c=ICON_COLOR,
                edgecolors=ICON_EDGE,
                linewidths=ICON_EDGE_WIDTH,
                zorder=5,
            )
            ax.text(
                x + COUNT_OFFSET,
                y,
                _format_mean_rank_label(mean_rank),
                ha="left",
                va="center",
                fontsize=7,
                color="black",
                fontweight="bold",
                zorder=6,
                path_effects=[pe.withStroke(linewidth=2.5, foreground="white")],
            )

        # Draw DK (triangle) first so it stays visually behind if overlapping; tie: △ left
        _draw_marker(x_dk, ICON_DK_ONLY[0], n_dk, mean_dk)
        _draw_marker(x_cs, ICON_CS_ONLY[0], n_cs, mean_cs)

    ax.set_xlabel("Top 40 PRS models (AOU benchmark rank)", fontsize=14)
    ax.set_ylabel("Disease", fontsize=14)
    ax.set_title("Top 40 PRS models by AOU AUC per disease", fontsize=16, fontweight="bold")
    ax.tick_params(axis="x", rotation=0, labelsize=12)
    ax.tick_params(axis="y", labelsize=11)

    fig.subplots_adjust(left=0.22, right=0.90, bottom=0.02, top=0.94)

    output_paths: list[Path] = []
    for fmt in formats:
        fmt_normalized = fmt.lower()
        output_path = output_dir / f"{OUTPUT_STEM}.{fmt_normalized}"
        save_kwargs: dict[str, Any] = {"bbox_inches": "tight"}
        if fmt_normalized in {"png", "jpg", "jpeg", "tiff"}:
            save_kwargs["dpi"] = dpi
        fig.savefig(output_path, **save_kwargs)
        output_paths.append(output_path)
    plt.close(fig)
    return output_paths


def _nrs(rank: int, n_models: int) -> float:
    """NRS = (M - r) / (M - 1); 1.0 = top, 0.0 = bottom."""
    if n_models <= 1:
        return 1.0
    return (n_models - rank) / (n_models - 1)


def _build_nrs_data(
    with_summary: dict[str, Any],
    without_summary: dict[str, Any],
) -> tuple[list[str], list[float], list[float]]:
    """Returns (disease_order, cs_nrs_list, dk_nrs_list)."""
    with_entries = {e["ontology"]: e for e in with_summary["per_disease"]}
    without_entries = {e["ontology"]: e for e in without_summary["per_disease"]}
    if set(with_entries) != set(without_entries):
        raise ValueError("Disease sets do not match between summaries")
    sorted_rows = _sort_disease_rows(list(with_entries.values()))
    diseases: list[str] = []
    cs_nrs: list[float] = []
    dk_nrs: list[float] = []
    for row in sorted_rows:
        ont = row["ontology"]
        n = int(row["n_models"])
        cs_rank = int((without_entries[ont].get("modal_recommendation_rank")) or n)
        dk_rank = int((with_entries[ont].get("modal_recommendation_rank")) or n)
        diseases.append(ont[0].upper() + ont[1:] if ont else ont)
        cs_nrs.append(_nrs(cs_rank, n))
        dk_nrs.append(_nrs(dk_rank, n))
    return diseases, cs_nrs, dk_nrs


def _plot_nrs_scatter(
    diseases: list[str],
    cs_nrs: list[float],
    dk_nrs: list[float],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> list[Path]:
    """Horizontal scatter with lollipop-style lines: Y=Disease, X=NRS; line connects CS and DK."""
    sns.set_theme(style="whitegrid")
    n = len(diseases)
    height = max(10.0, 0.28 * n + 2.0)
    fig, ax = plt.subplots(figsize=(8, height))
    y_pos = np.arange(n)

    # Lollipop-style connecting lines: green=DK>CS, red=DK<CS, gray=equal
    COLOR_IMPROVE = "#228B22"
    COLOR_WORSE = "#B22222"
    COLOR_SAME = "#7F7F7F"
    n_improve = sum(1 for i in range(n) if dk_nrs[i] > cs_nrs[i])
    n_worse = sum(1 for i in range(n) if dk_nrs[i] < cs_nrs[i])
    n_same = n - n_improve - n_worse
    for i in range(n):
        delta = dk_nrs[i] - cs_nrs[i]
        if delta > 0:
            color = COLOR_IMPROVE
        elif delta < 0:
            color = COLOR_WORSE
        else:
            color = COLOR_SAME
        ax.plot(
            [cs_nrs[i], dk_nrs[i]],
            [y_pos[i], y_pos[i]],
            color=color,
            linewidth=2.0,
            solid_capstyle="round",
            zorder=1,
        )

    ax.scatter(
        cs_nrs,
        y_pos,
        s=55,
        c="#C17C00",
        edgecolors="white",
        linewidths=0.8,
        label="Catalog Search Only",
        zorder=3,
    )
    ax.scatter(
        dk_nrs,
        y_pos,
        s=55,
        c="#00798C",
        edgecolors="white",
        linewidths=0.8,
        label="Catalog Search + Domain Knowledge",
        zorder=4,
    )
    ax.set_xlim(-0.05, 1.05)
    ax.set_xlabel("Normalized Ranking Score (NRS)", fontsize=12)
    ax.set_ylabel("Disease", fontsize=12)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(diseases, fontsize=9)
    ax.set_title("NRS by disease: Catalog Search Only vs Catalog Search + Domain Knowledge", fontsize=13, fontweight="bold")
    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([0], [0], color="#C17C00", marker="o", linestyle="", markersize=8, label="Catalog Search Only"),
        Line2D([0], [0], color="#00798C", marker="o", linestyle="", markersize=8, label="Catalog Search + Domain Knowledge"),
        Line2D([0], [0], color=COLOR_IMPROVE, linewidth=3, label=f"DK > CS (improved): {n_improve}"),
        Line2D([0], [0], color=COLOR_WORSE, linewidth=3, label=f"DK < CS (worsened): {n_worse}"),
        Line2D([0], [0], color=COLOR_SAME, linewidth=3, label=f"DK = CS (unchanged): {n_same}"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=9)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.5)
    fig.subplots_adjust(left=0.28, right=0.95, bottom=0.03, top=0.96)
    output_paths: list[Path] = []
    for fmt in formats:
        fn = fmt.lower()
        path = output_dir / f"{OUTPUT_STEM_NRS}.{fn}"
        kw: dict[str, Any] = {"bbox_inches": "tight"}
        if fn in {"png", "jpg", "jpeg", "tiff"}:
            kw["dpi"] = dpi
        fig.savefig(path, **kw)
        output_paths.append(path)
    plt.close(fig)
    return output_paths


def main() -> None:
    args = _parse_args()
    with_summary = _load_summary(args.with_summary)
    without_summary = _load_summary(args.without_summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    auc_frame, row_markers_df, disease_order = _build_heatmap_data(with_summary, without_summary)
    output_paths = _plot_heatmap(
        auc_frame=auc_frame,
        row_markers_df=row_markers_df,
        disease_order=disease_order,
        output_dir=args.output_dir,
        formats=args.formats,
        dpi=args.dpi,
    )

    diseases, cs_nrs, dk_nrs = _build_nrs_data(with_summary, without_summary)
    output_paths.extend(
        _plot_nrs_scatter(
            diseases=diseases,
            cs_nrs=cs_nrs,
            dk_nrs=dk_nrs,
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
