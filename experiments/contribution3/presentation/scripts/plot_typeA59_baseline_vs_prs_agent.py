from __future__ import annotations

import json
import math
from pathlib import Path
from textwrap import fill

import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


PROJECT_ROOT = Path(__file__).resolve().parents[4]
EVAL_DIR = (
    PROJECT_ROOT
    / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "ablation__no_all_tools_tuned_breadth"
    / "evaluation__typeA59_legacy80_no_aou_recomputed_20260526_143244"
)
INPUT_DETAIL = EVAL_DIR / "typeA59_baseline_vs_prs_agent_detail.csv"
INPUT_SUMMARY = EVAL_DIR / "typeA59_baseline_vs_prs_agent_summary.json"
OUTPUT_DIR = PROJECT_ROOT / "experiments/contribution3/presentation/figures_typeA59"
TIE_THRESHOLD = 0.0025


plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42
mpl.rcParams.update(
    {
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 1.2,
        "xtick.major.width": 1.1,
        "ytick.major.width": 1.1,
        "xtick.major.size": 4,
        "ytick.major.size": 4,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "legend.frameon": False,
    }
)


COLORS = {
    "baseline": "#777777",
    "agent": "#011F5B",
    "agent_light": "#6E8BBE",
    "gain": "#2A9D8F",
    "loss": "#B65A5C",
    "neutral": "#C8CDD2",
    "grid": "#E6E9ED",
    "axis": "#1B1B1B",
    "text": "#111111",
    "muted": "#6D737A",
    "pale_blue": "#DCE6F5",
    "pale_green": "#DCEFEA",
    "pale_red": "#F2D8D7",
}


CATEGORY_COLORS = {
    "Cancer": "#B76E79",
    "Cardiometabolic": "#4E79A7",
    "Immune/endocrine": "#59A14F",
    "Neurologic/psychiatric": "#9C755F",
    "Respiratory": "#76B7B2",
    "Renal/urologic": "#F28E2B",
    "Infectious/inflammatory": "#EDC948",
    "Other": "#8F8F8F",
}


def save_figure(fig: plt.Figure, stem: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_DIR / f"{stem}.png", dpi=450, bbox_inches="tight", pad_inches=0.08)


def markdown_table(frame: pd.DataFrame) -> str:
    header = "| " + " | ".join(frame.columns) + " |"
    divider = "| " + " | ".join(["---"] + ["---:"] * (len(frame.columns) - 1)) + " |"
    rows = ["| " + " | ".join(str(row[col]) for col in frame.columns) + " |" for _, row in frame.iterrows()]
    return "\n".join([header, divider, *rows])


def save_table_png(
    frame: pd.DataFrame,
    title: str,
    stem: str,
    figsize: tuple[float, float],
    footnote: str | None = None,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")
    ax.text(0.5, 0.985, title, transform=ax.transAxes, ha="center", va="top", fontsize=17, fontweight="bold")
    table_top = 0.89
    table_bottom = 0.08 if footnote else 0.04
    table = ax.table(
        cellText=frame.values,
        colLabels=frame.columns,
        loc="center",
        cellLoc="center",
        colLoc="center",
        bbox=[0.02, table_bottom, 0.96, table_top - table_bottom],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10.3)
    table.scale(1, 1.18)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#D8DEE6")
        cell.set_linewidth(0.8)
        if r == 0:
            cell.set_facecolor("#E9EEF6")
            cell.get_text().set_fontweight("bold")
            cell.get_text().set_color(COLORS["text"])
        elif r % 2 == 0:
            cell.set_facecolor("#F7F9FB")
        else:
            cell.set_facecolor("white")
        if c == 0:
            cell.get_text().set_ha("left")
            cell.PAD = 0.045
        else:
            cell.PAD = 0.035
    if footnote:
        ax.text(
            0.02,
            0.025,
            footnote,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=9.4,
            color=COLORS["muted"],
        )
    save_figure(fig, stem)
    plt.close(fig)


def add_panel_label(ax: plt.Axes, label: str, x: float = -0.12, y: float = 1.06) -> None:
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=16,
        fontweight="bold",
        color=COLORS["text"],
    )


def apply_grid(ax: plt.Axes, axis: str = "both") -> None:
    ax.grid(True, which="major", axis=axis, color=COLORS["grid"], linewidth=1.1)
    ax.set_axisbelow(True)


def title_case_label(name: str) -> str:
    if pd.isna(name):
        return ""
    special = {
        "hiv": "HIV",
        "gwas": "GWAS",
        "ldl": "LDL",
        "hdl": "HDL",
        "c-reactive": "C-reactive",
        "alzheimer's": "Alzheimer's",
        "crohn's": "Crohn's",
        "hodgkin's": "Hodgkin's",
        "parkinson's": "Parkinson's",
    }
    cleaned = str(name).replace("[", "").replace("]", "")
    words = []
    for word in cleaned.split():
        low = word.lower()
        words.append(special.get(low, word.capitalize()))
    return " ".join(words)


def short_target_label(row: pd.Series) -> str:
    overrides = {
        "D05": "Breast carcinoma in situ",
        "C22": "Liver/bile duct cancer",
        "E79": "Purine metabolism disorder",
        "F33": "Recurrent depression",
        "I44": "Atrioventricular block",
        "J41": "Chronic bronchitis",
        "J96": "Respiratory failure",
        "K43": "Ventral hernia",
        "L68": "Hypertrichosis",
        "M1A": "Chronic gout",
        "N26": "Kidney atrophy",
        "N65": "Breast reconstruction disorder",
        "N84": "Female genital tract polyp",
        "N91": "Rare menstruation",
        "Q23": "Aortic/mitral valve malformation",
    }
    return overrides.get(str(row["target_id"]), title_case_label(row["target_description"]))


def category_for_trait(name: str) -> str:
    s = str(name).lower()
    if any(k in s for k in ["carcinoma", "cancer", "neoplasm", "lymphoma", "leukemia", "melanoma", "myeloma"]):
        return "Cancer"
    if any(
        k in s
        for k in [
            "coronary",
            "myocardial",
            "atrial",
            "heart",
            "hypertension",
            "obesity",
            "diabetes",
            "aortic",
            "cardiomyopathy",
            "body mass",
            "cholesterol",
            "triglyceride",
            "valve",
            "gout",
            "uric acid",
        ]
    ):
        return "Cardiometabolic"
    if any(
        k in s
        for k in [
            "arthritis",
            "psoriasis",
            "lupus",
            "crohn",
            "colitis",
            "thyroid",
            "testosterone",
            "estradiol",
            "osteoporosis",
            "cellulitis",
            "dermatitis",
        ]
    ):
        return "Immune/endocrine"
    if any(
        k in s
        for k in [
            "alzheimer",
            "dementia",
            "parkinson",
            "schizophrenia",
            "depressive",
            "depression",
            "bipolar",
            "anxiety",
            "autism",
            "opioid",
            "personality",
            "obsessive",
            "glaucoma",
            "migraine",
        ]
    ):
        return "Neurologic/psychiatric"
    if any(k in s for k in ["asthma", "pulmonary", "lung", "respiratory", "bronchitis", "emphysema"]):
        return "Respiratory"
    if any(k in s for k in ["kidney", "urinary", "urolithiasis", "bladder", "renal"]):
        return "Renal/urologic"
    if any(k in s for k in ["hiv", "hepatitis", "candidiasis", "infection", "inflammatory", "abscess", "peritonitis"]):
        return "Infectious/inflammatory"
    return "Other"


def load_inputs() -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(INPUT_DETAIL)
    summary = json.loads(INPUT_SUMMARY.read_text())
    df["target_label"] = df.apply(short_target_label, axis=1)
    df["baseline_source_label"] = df["matched_cross_trait_baseline"].map(title_case_label)
    df["agent_source_label"] = df["matched_cross_trait_prs_agent"].map(title_case_label)
    df["target_category"] = df["target_description"].map(category_for_trait)
    df["agent_source_category"] = df["matched_cross_trait_prs_agent"].map(category_for_trait)
    df["baseline_source_category"] = df["matched_cross_trait_baseline"].map(category_for_trait)
    return df, summary


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def count_pct(x: float, n: int) -> str:
    hits = int(round(x * n))
    return f"{hits}/{n} ({x * 100:.1f}%)"


def plot_overall_performance(df: pd.DataFrame, summary: dict) -> None:
    fig = plt.figure(figsize=(15.8, 9.4))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.32, width_ratios=[1.18, 1.0])

    ax = fig.add_subplot(gs[:, 0])
    apply_grid(ax)
    status_specs = [
        ("higher", df["delta_selected_auc"] > TIE_THRESHOLD, COLORS["gain"], "Higher with PRS Agent"),
        ("similar", df["delta_selected_auc"].abs() <= TIE_THRESHOLD, COLORS["neutral"], f"Similar |Delta AUC| <= {TIE_THRESHOLD:g}"),
        ("lower", df["delta_selected_auc"] < -TIE_THRESHOLD, COLORS["loss"], "Lower with PRS Agent"),
    ]
    for _, mask, color, label in status_specs:
        group = df.loc[mask]
        ax.scatter(
            group["selected_model_auc_baseline"],
            group["selected_model_auc_prs_agent"],
            s=64,
            color=color,
            edgecolor="white",
            linewidth=0.7,
            alpha=0.96,
            label=f"{label} (n={len(group)})",
            zorder=3,
        )

    lo = 0.45
    hi = max(df["selected_model_auc_baseline"].max(), df["selected_model_auc_prs_agent"].max()) + 0.02
    hi = max(0.72, min(0.78, math.ceil(hi * 20) / 20))
    ax.plot([lo, hi], [lo, hi], linestyle=(0, (5, 4)), color="black", linewidth=2.0, zorder=2)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Baseline LLM selected-model AUC", fontsize=15, fontweight="bold")
    ax.set_ylabel("PRS Agent selected-model AUC", fontsize=15, fontweight="bold")
    ax.tick_params(labelsize=12)
    add_panel_label(ax, "a", -0.1, 1.03)

    label_positions = {
        "N65": (0.605, 0.739, "left"),
        "D05": (0.625, 0.688, "left"),
        "M1A": (0.655, 0.668, "left"),
        "E79": (0.612, 0.632, "left"),
        "J41": (0.468, 0.595, "left"),
        "J96": (0.468, 0.578, "left"),
        "F33": (0.468, 0.548, "left"),
        "N26": (0.468, 0.526, "left"),
        "K43": (0.468, 0.564, "left"),
    }
    for target_id, (tx, ty, ha) in label_positions.items():
        row = df.loc[df["target_id"].eq(target_id)]
        if row.empty:
            continue
        r = row.iloc[0]
        label = short_target_label(r)
        if len(label) > 27:
            label = fill(label, 24)
        ax.annotate(
            label,
            xy=(r["selected_model_auc_baseline"], r["selected_model_auc_prs_agent"]),
            xytext=(tx, ty),
            fontsize=9.3,
            ha=ha,
            va="center",
            arrowprops=dict(arrowstyle="-", lw=1.0, color="#555555", shrinkA=1, shrinkB=3),
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.72, pad=0.8),
            color=COLORS["text"],
        )

    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=color, markeredgecolor="white", markersize=8, label=f"{label} (n={int(mask.sum())})")
        for _, mask, color, label in status_specs
    ]
    ax.legend(handles=legend_handles, loc="upper left", fontsize=10, ncol=1, handletextpad=0.3, borderaxespad=0.2)
    if df["candidate_count_prs_agent"].nunique() == 1:
        model_count_text = f"Benchmark universe: {int(df['candidate_count_prs_agent'].iloc[0]):,} PRS models per target"
    else:
        model_count_text = f"Benchmark universe: median {df['candidate_count_prs_agent'].median():,.0f} PRS models per target"
    ax.text(
        0.98,
        0.035,
        model_count_text,
        transform=ax.transAxes,
        fontsize=10.0,
        color=COLORS["muted"],
        ha="right",
        va="bottom",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.78, pad=0.8),
    )

    ax_metric = fig.add_subplot(gs[0, 1])
    add_panel_label(ax_metric, "b", -0.12, 1.08)
    metric_names = ["Selected-model AUC", "Global percentile rank"]
    base_vals = [summary["baseline"]["mean_selected_auc"], summary["baseline"]["mean_gpr"]]
    agent_vals = [summary["prs_agent"]["mean_selected_auc"], summary["prs_agent"]["mean_gpr"]]
    x = np.arange(len(metric_names))
    width = 0.34
    ax_metric.bar(x - width / 2, base_vals, width, color=COLORS["baseline"], label="Baseline LLM")
    ax_metric.bar(x + width / 2, agent_vals, width, color=COLORS["agent"], label="PRS Agent")
    for i, (bv, av) in enumerate(zip(base_vals, agent_vals)):
        ax_metric.text(i - width / 2, bv + 0.018, f"{bv:.3f}", ha="center", va="bottom", fontsize=11.5, fontweight="bold")
        ax_metric.text(i + width / 2, av + 0.018, f"{av:.3f}", ha="center", va="bottom", fontsize=11.5, fontweight="bold")
        ax_metric.text(i, max(bv, av) + 0.07, f"+{av - bv:.3f}", ha="center", va="bottom", fontsize=11.2, color=COLORS["gain"], fontweight="bold")
    ax_metric.set_xticks(x)
    ax_metric.set_xticklabels(metric_names, fontsize=11.5, fontweight="bold")
    ax_metric.set_ylim(0.45, 0.92)
    ax_metric.set_ylabel("Mean value across 59 targets", fontsize=13, fontweight="bold")
    ax_metric.tick_params(axis="y", labelsize=11)
    apply_grid(ax_metric, "y")
    ax_metric.legend(loc="upper left", fontsize=10)

    ax_top = fig.add_subplot(gs[1, 1])
    add_panel_label(ax_top, "c", -0.12, 1.08)
    pct_keys = [
        ("top_0_5pct", "Hit@top 0.5%"),
        ("top_1pct", "Hit@top 1%"),
        ("top_2_5pct", "Hit@top 2.5%"),
        ("top_5pct", "Hit@top 5%"),
        ("top_25pct", "Hit@top 25%"),
    ]
    base_hits = []
    agent_hits = []
    for key, _ in pct_keys:
        if key in summary["baseline"]["hit_at_percent"]:
            base_hits.append(summary["baseline"]["hit_at_percent"][key])
            agent_hits.append(summary["prs_agent"]["hit_at_percent"][key])
        else:
            base_hits.append(summary["baseline"]["legacy_hit_at_percent"][key])
            agent_hits.append(summary["prs_agent"]["legacy_hit_at_percent"][key])
    x = np.arange(len(pct_keys))
    width = 0.34
    ax_top.bar(x - width / 2, base_hits, width, color=COLORS["baseline"], label="Baseline LLM")
    ax_top.bar(x + width / 2, agent_hits, width, color=COLORS["agent"], label="PRS Agent")
    n = int(summary["n_targets"])
    for i, (bv, av) in enumerate(zip(base_hits, agent_hits)):
        ax_top.text(i - width / 2, bv + 0.018, f"{round(bv*n):.0f}/{n}", ha="center", va="bottom", fontsize=9.3)
        ax_top.text(i + width / 2, av + 0.018, f"{round(av*n):.0f}/{n}", ha="center", va="bottom", fontsize=9.3, fontweight="bold")
    ax_top.set_xticks(x)
    ax_top.set_xticklabels([label for _, label in pct_keys], fontsize=10.2, fontweight="bold", rotation=15, ha="right")
    ax_top.set_ylabel("Selection accuracy", fontsize=13, fontweight="bold")
    ax_top.set_ylim(0, 0.88)
    ax_top.tick_params(axis="y", labelsize=11)
    apply_grid(ax_top, "y")
    ax_top.legend(loc="upper left", fontsize=10)

    fig.suptitle(
        "PRS Agent improves cross-phenotype PRS model transfer across 59 targets",
        fontsize=18,
        fontweight="bold",
        y=0.99,
    )
    save_figure(fig, "fig1_cross_overall_performance_typeA59")
    plt.close(fig)


def plot_delta_waterfall(df: pd.DataFrame) -> None:
    gains = df.loc[df["delta_selected_auc"] > TIE_THRESHOLD].sort_values("delta_selected_auc", ascending=False).reset_index(drop=True)
    near = df.loc[df["delta_selected_auc"].abs() <= TIE_THRESHOLD].copy()
    losses = df.loc[df["delta_selected_auc"] < -TIE_THRESHOLD].sort_values("delta_selected_auc").reset_index(drop=True)

    gap = 4
    near_width = 8
    x_gain = np.arange(len(gains))
    near_left = len(gains) + gap
    near_center = near_left + near_width / 2
    x_loss = near_left + near_width + gap + np.arange(len(losses))

    fig = plt.figure(figsize=(17.2, 7.4))
    gs = gridspec.GridSpec(1, 2, figure=fig, width_ratios=[1.40, 1.00], wspace=0.26)
    ax = fig.add_subplot(gs[0, 0])
    ax.bar(x_gain, gains["delta_selected_auc"], color=COLORS["gain"], width=0.82, alpha=0.95)
    ax.bar(x_loss, losses["delta_selected_auc"], color=COLORS["loss"], width=0.82, alpha=0.95)
    ax.axvspan(near_left, near_left + near_width, color="#ECEFF2", alpha=1.0, zorder=0)
    ax.axhline(0, color=COLORS["axis"], linewidth=1.4)
    apply_grid(ax, "y")
    ax.set_xlim(-1, x_loss[-1] + 1 if len(losses) else near_left + near_width + 1)
    ymax = max(abs(df["delta_selected_auc"].min()), abs(df["delta_selected_auc"].max()))
    ax.set_ylim(-max(0.075, ymax * 1.18), max(0.18, ymax * 1.08))
    ax.set_ylabel("AUC gain from PRS Agent", fontsize=15, fontweight="bold")
    ax.set_xlabel("Targets ordered by selected-model AUC change", fontsize=14, fontweight="bold")
    ax.tick_params(axis="y", labelsize=12)
    ax.set_xticks([])

    ax.text(0, ax.get_ylim()[1] * 0.92, f"Higher: {len(gains)}", color=COLORS["gain"], fontsize=13, fontweight="bold", ha="left")
    ax.text(
        near_center,
        ax.get_ylim()[1] * 0.52,
        f"Near-tie\n|Delta AUC| <= {TIE_THRESHOLD:g}\n{len(near)} targets hidden",
        color=COLORS["muted"],
        fontsize=12,
        fontweight="bold",
        ha="center",
        va="center",
    )
    if len(losses):
        ax.text(x_loss[0], ax.get_ylim()[0] * 0.86, f"Lower: {len(losses)}", color=COLORS["loss"], fontsize=13, fontweight="bold", ha="left")

    ax_table = fig.add_subplot(gs[0, 1])
    ax_table.axis("off")
    ax_table.text(0.00, 0.98, "Representative transfer changes", transform=ax_table.transAxes, fontsize=15, fontweight="bold", va="top")
    ax_table.text(0.00, 0.925, "Baseline AUC -> PRS Agent AUC; delta shown at right", transform=ax_table.transAxes, fontsize=10.2, color=COLORS["muted"], va="top")

    top_gain_table = gains.head(6)
    top_loss_table = losses.head(4)
    table_rows = [("Largest gains", None, COLORS["gain"])] + [(None, row, COLORS["gain"]) for _, row in top_gain_table.iterrows()]
    table_rows += [("Lower selected-model AUC", None, COLORS["loss"])] + [(None, row, COLORS["loss"]) for _, row in top_loss_table.iterrows()]
    y = 0.84
    for header, row, color in table_rows:
        if header:
            ax_table.text(0.00, y, header, transform=ax_table.transAxes, fontsize=12.3, fontweight="bold", color=color, va="center")
            y -= 0.052
            continue
        target = short_target_label(row)
        if len(target) > 24:
            target = fill(target, 22)
        ax_table.text(0.00, y, target, transform=ax_table.transAxes, fontsize=9.7, va="center", ha="left")
        ax_table.text(
            0.62,
            y,
            f"{row['selected_model_auc_baseline']:.3f} -> {row['selected_model_auc_prs_agent']:.3f}",
            transform=ax_table.transAxes,
            fontsize=9.7,
            va="center",
            ha="left",
            color=COLORS["text"],
        )
        ax_table.text(
            0.98,
            y,
            f"{row['delta_selected_auc']:+.3f}",
            transform=ax_table.transAxes,
            fontsize=9.5,
            va="center",
            ha="right",
            color=color,
            fontweight="bold",
        )
        ax_table.plot([0, 1], [y - 0.037, y - 0.037], transform=ax_table.transAxes, color=COLORS["grid"], lw=1)
        y -= 0.076

    fig.suptitle("Cross-phenotype AUC gains are concentrated in a subset of transfer targets", fontsize=18, fontweight="bold", y=0.99)
    save_figure(fig, "fig2_cross_delta_auc_waterfall_typeA59")
    plt.close(fig)


def plot_transfer_source_landscape(df: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(16.4, 9.2))
    gs = gridspec.GridSpec(2, 2, figure=fig, width_ratios=[0.92, 1.08], height_ratios=[1.0, 1.0], hspace=0.45, wspace=0.36)

    ax = fig.add_subplot(gs[:, 0])
    add_panel_label(ax, "a", -0.12, 1.04)
    frontier = df["frontier_candidate_pgs_id_count_prs_agent"]
    bins = [25, 50, 100, 200, 400, 800]
    counts, _, _ = ax.hist(frontier, bins=bins, color=COLORS["agent_light"], edgecolor="white", linewidth=1.2)
    ax.set_xscale("log")
    ax.set_xticks(bins)
    ax.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
    ax.set_xlabel("PRS models in transfer frontier", fontsize=14, fontweight="bold")
    ax.set_ylabel("Number of targets", fontsize=14, fontweight="bold")
    ax.tick_params(labelsize=12)
    apply_grid(ax, "y")
    median_n = frontier.median()
    ax.axvline(median_n, color=COLORS["agent"], linewidth=2.2)
    ax.text(median_n * 1.06, max(counts) * 0.93 if len(counts) else 1, f"median = {median_n:.0f}", fontsize=11, color=COLORS["agent"], fontweight="bold", va="top")
    ax.text(
        0.04,
        0.95,
        f"range: {int(frontier.min())}-{int(frontier.max())} models",
        transform=ax.transAxes,
        fontsize=11.5,
        fontweight="bold",
        va="top",
    )

    ax2 = fig.add_subplot(gs[0, 1])
    add_panel_label(ax2, "b", -0.10, 1.06)
    source_counts = df["agent_source_label"].value_counts().head(14).sort_values()
    y = np.arange(len(source_counts))
    ax2.hlines(y, xmin=0, xmax=source_counts.values, color=COLORS["neutral"], linewidth=5.0, zorder=2)
    ax2.scatter(source_counts.values, y, s=60, color=COLORS["agent_light"], edgecolor="white", linewidth=0.8, zorder=3)
    ax2.set_yticks(y)
    ax2.set_yticklabels([fill(x, 28) if len(x) > 30 else x for x in source_counts.index], fontsize=9.5)
    ax2.set_xlabel("Targets selecting source trait", fontsize=13, fontweight="bold")
    ax2.set_xlim(0, max(source_counts.max() + 1, 6))
    ax2.tick_params(axis="x", labelsize=11)
    apply_grid(ax2, "x")
    for yi, value in zip(y, source_counts.values):
        ax2.text(value + 0.10, yi, f"{int(value)}", va="center", fontsize=10.2, fontweight="bold")
    ax2.set_title("Most reused PRS Agent source traits", fontsize=13.5, fontweight="bold", pad=10)

    ax3 = fig.add_subplot(gs[1, 1])
    add_panel_label(ax3, "c", -0.13, 1.12)
    target_order = ["Cancer", "Cardiometabolic", "Immune/endocrine", "Neurologic/psychiatric", "Respiratory", "Renal/urologic", "Infectious/inflammatory", "Other"]
    source_order = target_order
    mat = pd.crosstab(df["target_category"], df["agent_source_category"]).reindex(index=target_order, columns=source_order, fill_value=0)
    im = ax3.imshow(mat.values, cmap=mpl.colors.LinearSegmentedColormap.from_list("cross_heat", ["#F5F7FA", "#6E8BBE", "#011F5B"]))
    ax3.set_xticks(np.arange(len(source_order)))
    ax3.set_yticks(np.arange(len(target_order)))
    ax3.set_xticklabels([fill(x, 16) for x in source_order], fontsize=8.2, rotation=35, ha="right")
    ax3.set_yticklabels(target_order, fontsize=8.8)
    ax3.set_xlabel("Selected source-trait category", fontsize=12, fontweight="bold")
    ax3.set_ylabel("Target category", fontsize=12, fontweight="bold")
    ax3.set_title("Target-to-source transfer categories", fontsize=13.5, fontweight="bold", pad=10)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            value = int(mat.iat[i, j])
            if value:
                ax3.text(j, i, str(value), ha="center", va="center", fontsize=9.5, fontweight="bold", color="white" if value >= 4 else COLORS["text"])
    cbar = fig.colorbar(im, ax=ax3, fraction=0.046, pad=0.02)
    cbar.ax.tick_params(labelsize=9)

    fig.suptitle("Cross-phenotype transfer uses a broad but structured source-trait space", fontsize=18, fontweight="bold", y=0.99)
    save_figure(fig, "fig3_cross_transfer_source_landscape_typeA59")
    plt.close(fig)


def plot_micro_case_studies(df: pd.DataFrame) -> None:
    case_ids = ["D05", "J41", "M1A", "E79", "F33", "N26"]
    case_df = df.set_index("target_id").loc[[x for x in case_ids if x in set(df["target_id"])]] .reset_index()
    fig, axes = plt.subplots(2, 3, figsize=(16.7, 9.8), sharex=True)
    axes_flat = axes.ravel()
    x_min = 0.48
    x_max = max(case_df["benchmark_top_model_auc_prs_agent"].max(), case_df["selected_model_auc_prs_agent"].max(), case_df["selected_model_auc_baseline"].max()) + 0.03
    x_max = min(0.74, max(0.64, math.ceil(x_max * 20) / 20))

    for i, (_, row) in enumerate(case_df.iterrows()):
        ax = axes_flat[i]
        add_panel_label(ax, chr(ord("a") + i), -0.12, 1.08)
        target = short_target_label(row)
        if len(target) > 24:
            target = fill(target, 23)
        ax.set_title(f"{target}\nsource-trait transfer", fontsize=12.5, fontweight="bold", pad=12)
        ax.axvline(row["benchmark_top_model_auc_prs_agent"], color=COLORS["neutral"], linestyle=(0, (4, 3)), linewidth=1.5, zorder=1)
        ax.text(
            row["benchmark_top_model_auc_prs_agent"],
            2.23,
            f"best {row['benchmark_top_model_auc_prs_agent']:.3f}",
            fontsize=8.7,
            color=COLORS["muted"],
            ha="center",
            va="bottom",
        )
        rows = [
            ("Baseline LLM", row["baseline_source_label"], row["recommended_model_id_baseline"], row["selected_model_auc_baseline"], row["selected_model_rank_baseline"], row["selected_model_gpr_baseline"], COLORS["baseline"], 1.60),
            ("PRS Agent", row["agent_source_label"], row["recommended_model_id_prs_agent"], row["selected_model_auc_prs_agent"], row["selected_model_rank_prs_agent"], row["selected_model_gpr_prs_agent"], COLORS["agent"], 0.70),
        ]
        for method, source, model_id, auc, rank, gpr, color, yy in rows:
            ax.hlines(yy, x_min, auc, color=color, linewidth=7.0, alpha=0.88, zorder=2)
            ax.scatter([auc], [yy], s=105, color=color, edgecolor="white", linewidth=0.9, zorder=4)
            ax.text(x_min + 0.002, yy + 0.23, method, fontsize=10.2, fontweight="bold", color=color, ha="left", va="center")
            source_text = fill(str(source), 27)
            ax.text(
                x_min + 0.002,
                yy - 0.22,
                f"{source_text}\n{model_id}; rank {int(rank)}/2958; GPR {gpr:.3f}",
                fontsize=7.9,
                color=COLORS["text"],
                ha="left",
                va="top",
                linespacing=1.05,
            )
            ax.text(auc + 0.003, yy, f"{auc:.3f}", fontsize=9.3, color=color, fontweight="bold", ha="left", va="center")
        ax.text(
            0.98,
            0.08,
            f"Delta AUC {row['delta_selected_auc']:+.3f}\nDelta GPR {row['delta_gpr']:+.3f}",
            transform=ax.transAxes,
            fontsize=9.0,
            color=COLORS["gain"] if row["delta_selected_auc"] > 0 else COLORS["loss"],
            fontweight="bold",
            ha="right",
            va="bottom",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.78, pad=0.7),
        )
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(0.15, 2.55)
        ax.set_yticks([])
        ax.set_xlabel("AoU benchmark AUC", fontsize=11.5, fontweight="bold")
        ax.tick_params(axis="x", labelsize=10)
        apply_grid(ax, "x")
    for j in range(len(case_df), len(axes_flat)):
        axes_flat[j].axis("off")
    handles = [
        Line2D([0], [0], marker="o", color=COLORS["baseline"], markerfacecolor=COLORS["baseline"], markersize=8, linewidth=5, label="Baseline LLM selected"),
        Line2D([0], [0], marker="o", color=COLORS["agent"], markerfacecolor=COLORS["agent"], markersize=8, linewidth=5, label="PRS Agent selected"),
        Line2D([0], [0], color=COLORS["neutral"], linestyle=(0, (4, 3)), linewidth=1.7, label="Best empirical cross-phenotype model"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=11, bbox_to_anchor=(0.5, 0.005))
    fig.suptitle("Micro case studies: source-trait transfer decisions behind selected PRS models", fontsize=18, fontweight="bold", y=1.01)
    fig.subplots_adjust(bottom=0.13, top=0.88, wspace=0.28, hspace=0.55)
    save_figure(fig, "fig4_cross_micro_transfer_case_studies_typeA59")
    plt.close(fig)


def write_source_data(df: pd.DataFrame, summary: dict) -> None:
    source_dir = OUTPUT_DIR / "source_data"
    source_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(source_dir / "typeA59_baseline_vs_prs_agent.csv", index=False)
    (source_dir / "typeA59_baseline_vs_prs_agent_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    case_ids = ["D05", "J41", "M1A", "E79", "F33", "N26"]
    df.loc[df["target_id"].isin(case_ids)].to_csv(source_dir / "typeA59_micro_case_studies.csv", index=False)


def write_cross_evaluation_table(summary: dict) -> None:
    source_dir = OUTPUT_DIR / "source_data"
    source_dir.mkdir(parents=True, exist_ok=True)
    n = int(summary["n_targets"])
    rows = []
    ordered = [
        ("top_0_5pct", "Hit@top 0.5%"),
        ("top_1pct", "Hit@top 1%"),
        ("top_1_5pct", "Hit@top 1.5%"),
        ("top_2pct", "Hit@top 2%"),
        ("top_2_5pct", "Hit@top 2.5%"),
        ("top_5pct", "Hit@top 5%"),
        ("top_10pct", "Hit@top 10%"),
        ("top_25pct", "Hit@top 25%"),
    ]
    for key, label in ordered:
        if key in summary["baseline"]["hit_at_percent"]:
            base = summary["baseline"]["hit_at_percent"][key]
            agent = summary["prs_agent"]["hit_at_percent"][key]
        else:
            base = summary["baseline"]["legacy_hit_at_percent"][key]
            agent = summary["prs_agent"]["legacy_hit_at_percent"][key]
        rows.append(
            {
                "Metric": label,
                "Baseline LLM": count_pct(base, n),
                "PRS Agent": count_pct(agent, n),
                "Improvement": f"+{round(agent * n) - round(base * n)} hits ({(agent - base) * 100:+.1f} pp)",
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(source_dir / "table1_cross_percentile_evaluation_matrix.csv", index=False)
    (source_dir / "table1_cross_percentile_evaluation_matrix.md").write_text(markdown_table(frame) + "\n")
    save_table_png(
        frame,
        "Cross-phenotype Hit@top-percentile recommendation accuracy",
        "table1_cross_percentile_evaluation_matrix_typeA59",
        figsize=(12.5, 5.4),
        footnote="Hit@top-percentile records whether the selected PGS model falls within the empirical top percentile of the cross-phenotype benchmark universe.",
    )


def write_readme(df: pd.DataFrame, summary: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    readme = OUTPUT_DIR / "README.md"
    lines = [
        "# Type A59 cross-phenotype baseline vs PRS Agent presentation figures",
        "",
        "These figures compare two methods: Baseline LLM and PRS Agent.",
        "",
        "## Files",
        "- `fig1_cross_overall_performance_typeA59`: scatter + mean AUC/GPR + Hit@top-percentile accuracy.",
        "- `fig2_cross_delta_auc_waterfall_typeA59`: target-level selected-model AUC gains/losses with representative transfer changes.",
        "- `fig3_cross_transfer_source_landscape_typeA59`: transfer frontier size, reused source traits, and target-to-source categories.",
        "- `fig4_cross_micro_transfer_case_studies_typeA59`: source-trait transfer case studies for selected targets.",
        "- `table1_cross_percentile_evaluation_matrix_typeA59`: Hit@top-percentile cross-phenotype evaluation matrix.",
        "",
        "Each figure/table image is exported as PNG.",
        "",
        "## Key numbers",
        f"- Coverage: Baseline {summary['baseline']['coverage']:.3f}; PRS Agent {summary['prs_agent']['coverage']:.3f}.",
        f"- Mean selected-model AUC: {summary['baseline']['mean_selected_auc']:.3f} -> {summary['prs_agent']['mean_selected_auc']:.3f}.",
        f"- Mean global percentile rank: {summary['baseline']['mean_gpr']:.3f} -> {summary['prs_agent']['mean_gpr']:.3f}.",
        f"- Mean absolute AUC regret: {summary['baseline']['mean_absolute_auc_regret']:.3f} -> {summary['prs_agent']['mean_absolute_auc_regret']:.3f}.",
        f"- Paired AUC: {summary['paired_auc']['n_improved_auc']} improved, {summary['paired_auc']['n_tied_auc']} tied, {summary['paired_auc']['n_worse_auc']} lower.",
        f"- Transfer frontier size: median {df['frontier_candidate_pgs_id_count_prs_agent'].median():.0f}; range {int(df['frontier_candidate_pgs_id_count_prs_agent'].min())}-{int(df['frontier_candidate_pgs_id_count_prs_agent'].max())}.",
        "",
        "## Source data",
        "- `source_data/typeA59_baseline_vs_prs_agent.csv`",
        "- `source_data/typeA59_baseline_vs_prs_agent_summary.json`",
        "- `source_data/typeA59_micro_case_studies.csv`",
        "- `source_data/table1_cross_percentile_evaluation_matrix.csv`",
    ]
    readme.write_text("\n".join(lines) + "\n")


def main() -> int:
    df, summary = load_inputs()
    write_source_data(df, summary)
    plot_overall_performance(df, summary)
    plot_delta_waterfall(df)
    plot_transfer_source_landscape(df)
    plot_micro_case_studies(df)
    write_cross_evaluation_table(summary)
    write_readme(df, summary)
    print(f"Wrote figures to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
