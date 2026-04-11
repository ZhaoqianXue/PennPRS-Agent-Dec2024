"""
Bar plots for cherry-picked paper Evaluation targets:
one PNG per (benchmark_family, target_id) case (25 figures: 12 + 13).

Each bar is one cross-trait group (trait bundle from trait_bundle_index.json):
height = max AUC on the target among all PRS listed for that bundle in the matrix row.
Bundles are sorted by that max AUC descending (best cross-trait on the left).

The transfer-matched bundle (eval detail: matched_bundle_id) is red; others blue.
PRS present in the matrix but not listed in any bundle get one extra bar
"PRS not in trait-bundle index" if needed.

Usage (from repo root):
  python experiments/contribution3/evaluation/plot_paper_target_auc_distribution.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVAL_DIR = Path(__file__).resolve().parent
TARGETS_JSON = EVAL_DIR / "paper_evaluation_targets.json"
FIGURES_DIR = EVAL_DIR / "figures"
TRANSFER_RUNS = PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent"
BUNDLE_INDEX_JSON = TRANSFER_RUNS / "trait_bundle_index.json"

UNASSIGNED_ID = "__unassigned_prs__"
# X-axis: trait text only (no bundle_id / ontology id).
MAX_LABEL_LEN = 52


def _load_evaluate_module():
    path = (
        PROJECT_ROOT
        / "experiments"
        / "contribution3"
        / "transfer"
        / "eval"
        / "evaluate_end_to_end.py"
    )
    spec = importlib.util.spec_from_file_location("evaluate_end_to_end", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _detail_lookup(detail_csv: Path) -> dict[str, dict]:
    df = pd.read_csv(detail_csv)
    out: dict[str, dict] = {}
    for _, row in df.iterrows():
        tid = str(row["target_id"]).strip()
        out[tid] = row.to_dict()
    return out


def _load_bundles() -> list[dict]:
    return json.loads(BUNDLE_INDEX_JSON.read_text(encoding="utf-8"))


def _bundle_rows_for_target(
    bundles: list[dict],
    auc_by_id: dict[str, float],
    *,
    matched_bundle_id: str | None,
    recommended_model_id: str,
) -> tuple[list[str], list[float], list[str], str | None]:
    """
    Returns (bundle_ids, max_aucs, xtick_labels, highlight_bundle_id).
    Sorted by max_auc descending (best first / left on plot).
    highlight_bundle_id is matched_bundle_id if it appears among rows, else None.
    """
    matched = str(matched_bundle_id).strip() if matched_bundle_id and str(matched_bundle_id) != "nan" else ""
    rec = str(recommended_model_id).strip()

    covered_prs: set[str] = set()
    rows: list[tuple[str, float, str]] = []

    for b in bundles:
        bid = str(b.get("bundle_id", "")).strip()
        label = str(b.get("canonical_label", bid)).strip()
        pgs_list = b.get("candidate_pgs_ids") or []
        aucs = [auc_by_id[p] for p in pgs_list if p in auc_by_id]
        if not aucs and bid == matched and rec in auc_by_id:
            for p in pgs_list:
                if p == rec and p in auc_by_id:
                    aucs.append(auc_by_id[p])
                    break
        if not aucs:
            continue
        for p in pgs_list:
            if p in auc_by_id:
                covered_prs.add(p)
        rows.append((bid, max(aucs), label))

    orphans = [p for p in auc_by_id if p not in covered_prs]
    if orphans:
        rows.append(
            (
                UNASSIGNED_ID,
                max(auc_by_id[p] for p in orphans),
                "PRS not in trait-bundle index",
            )
        )

    rows.sort(key=lambda t: (-t[1], t[0]))

    bundle_ids = [t[0] for t in rows]
    max_aucs = [t[1] for t in rows]
    labels = []
    for bid, _mx, lab in rows:
        if bid == UNASSIGNED_ID:
            labels.append(lab)
        else:
            short = lab if len(lab) <= MAX_LABEL_LEN else lab[: MAX_LABEL_LEN - 1] + "…"
            labels.append(short)

    highlight: str | None = matched if matched and matched in bundle_ids else None
    return bundle_ids, max_aucs, labels, highlight


def plot_one(
    *,
    benchmark_label: str,
    target_id: str,
    matched_bundle_id: str | None,
    selected_model_id: str,
    target_description: str,
    bundle_ids: list[str],
    max_aucs: list[float],
    x_labels: list[str],
    highlight_bundle_id: str | None,
    out_path: Path,
) -> None:
    sel = str(selected_model_id).strip()
    colors = [
        "#d62728" if bid == highlight_bundle_id else "#1f77b4" for bid in bundle_ids
    ]

    n = len(max_aucs)
    x = range(n)
    fig_w = min(52, max(12, n * 0.14))
    fig, ax = plt.subplots(figsize=(fig_w, 5.0), dpi=150)
    ax.bar(x, max_aucs, width=0.72, color=colors, edgecolor="none", linewidth=0)
    ax.set_xticks(list(x))
    ax.set_xticklabels(
        x_labels,
        rotation=90,
        ha="right",
        fontsize=max(4.5, min(7.5, 900 / max(n, 1))),
    )

    ymin = min(max_aucs)
    ymax = max(max_aucs)
    pad = (ymax - ymin) * 0.05 + 1e-6
    ax.set_ylim(ymin - pad, ymax + pad)

    ax.set_xlabel("Cross-trait source (trait bundle; best bundle left)")
    ax.set_ylabel("Max AUC (adjusted) within bundle on target")
    desc = str(target_description).replace("\n", " ")
    desc = " ".join(desc.split())
    if len(desc) > 90:
        desc = desc[:87] + "..."
    title = f"{benchmark_label} | {target_id} | matched bundle: {matched_bundle_id or 'n/a'} | PRS: {sel} | {desc}"
    ax.set_title(title, fontsize=8.5)
    ax.grid(axis="y", alpha=0.25, linestyle="--")

    legend_elements = [
        Patch(facecolor="#d62728", edgecolor="none", label="Matched cross-trait (transfer)"),
        Patch(facecolor="#1f77b4", edgecolor="none", label="Other cross-traits"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=8)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    e2e = _load_evaluate_module()
    bundles = _load_bundles()

    with open(TARGETS_JSON, encoding="utf-8") as f:
        cfg = json.load(f)

    b2b_ids: list[str] = cfg["binary_to_binary"]["target_ids"]
    b2c_ids: list[str] = cfg["binary_to_continuous"]["target_ids"]

    b2b_detail = _detail_lookup(
        TRANSFER_RUNS / "binary_to_binary" / "evaluation" / "all-tools__end_to_end_eval_detail.csv"
    )
    b2c_detail = _detail_lookup(
        TRANSFER_RUNS / "binary_to_continuous" / "evaluation" / "all-tools__end_to_end_eval_detail.csv"
    )

    n_ok = 0
    n_skip = 0

    def run_batch(
        label_short: str,
        benchmark_key: str,
        target_ids: list[str],
        detail_by_target: dict[str, dict],
    ) -> None:
        nonlocal n_ok, n_skip
        for target_id in target_ids:
            row = detail_by_target.get(target_id)
            if not row:
                print(f"skip {benchmark_key} {target_id}: no eval detail row")
                n_skip += 1
                continue
            if row.get("status") != "evaluated":
                print(f"skip {benchmark_key} {target_id}: status={row.get('status')}")
                n_skip += 1
                continue
            target_source = str(row["target_source"]).strip()
            sel = str(row["recommended_model_id"]).strip()
            matched_bid = row.get("matched_bundle_id")
            if not sel:
                print(f"skip {benchmark_key} {target_id}: missing recommended_model_id")
                n_skip += 1
                continue
            try:
                _, _, auc_by_id = e2e._build_full_matrix_ranking(target_id, target_source)
            except Exception as exc:
                print(f"skip {benchmark_key} {target_id}: matrix {exc}")
                n_skip += 1
                continue
            if sel not in auc_by_id:
                print(f"skip {benchmark_key} {target_id}: selected {sel} not in AUC row")
                n_skip += 1
                continue

            b_ids, m_aucs, x_labs, hi = _bundle_rows_for_target(
                bundles,
                auc_by_id,
                matched_bundle_id=str(matched_bid) if matched_bid is not None else None,
                recommended_model_id=sel,
            )

            out_name = f"{benchmark_key}__{target_id}__paper_eval_auc_bars.png"
            out_path = FIGURES_DIR / out_name
            plot_one(
                benchmark_label=label_short,
                target_id=target_id,
                matched_bundle_id=str(matched_bid).strip() if matched_bid else None,
                selected_model_id=sel,
                target_description=str(row.get("target_description", "")),
                bundle_ids=b_ids,
                max_aucs=m_aucs,
                x_labels=x_labs,
                highlight_bundle_id=hi,
                out_path=out_path,
            )
            if hi is None and matched_bid:
                print(
                    f"warn {benchmark_key} {target_id}: matched_bundle {matched_bid} has no bar "
                    f"(no candidate PRS in AUC row for that bundle)"
                )
            print(f"wrote {out_path.relative_to(PROJECT_ROOT)}")
            n_ok += 1

    run_batch("binary → binary", "binary_to_binary", b2b_ids, b2b_detail)
    run_batch("binary → continuous", "binary_to_continuous", b2c_ids, b2c_detail)

    print(f"done: {n_ok} figures, skipped {n_skip}")


if __name__ == "__main__":
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    main()