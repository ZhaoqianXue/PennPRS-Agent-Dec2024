from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "output/doc"
WITHIN_SIMILAR_DELTA_AUC = 0.0025
CROSS_SIMILAR_DELTA_AUC = 0.01

WITHIN_BASELINE_SUMMARY = (
    ROOT
    / "experiments/contribution2/recommendation/runs/"
    / "without-domain-gpt-5.2-t1__89disease__baseline-current89-direct-20260505/"
    / "experiment_without_domain_summary.json"
)
WITHIN_AGENT_SUMMARY = (
    ROOT
    / "experiments/contribution2/recommendation/runs/"
    / "pairwise-rerank-gpt-5.2-t1__89disease__round42-top5-holistic-performance-proxy-fast-cur89-20260503-014640/"
    / "experiment_pairwise_rerank_summary.json"
)
CROSS_BASELINE_DETAIL = (
    ROOT
    / "experiments/contribution3/transfer/runs/tool_calling_agent/unified/"
    / "ablation__no_all_tools_tuned_breadth/"
    / "evaluation__gpt_no_harness_forced_normalized_20260521/"
    / "gpt-no-harness__end_to_end_eval_detail.csv"
)
CROSS_AGENT_DETAIL = (
    ROOT
    / "experiments/contribution3/transfer/runs/tool_calling_agent/unified/"
    / "ablation__no_all_tools_tuned_breadth/"
    / "evaluation__paired80_legacy_no_aou_tuned_HO_breadth_20260509_w20/"
    / "all-tools__end_to_end_eval_detail.csv"
)

WITHIN_DATA = OUTDIR / "prs_agent_within_trait_auc_scatter_all89_similar00025_sparse_labels_data.csv"
WITHIN_PNG = OUTDIR / "prs_agent_within_trait_auc_scatter_all89_similar00025_sparse_labels.png"
CROSS_DATA = OUTDIR / "prs_agent_cross_trait_auc_scatter_typeA60_similar001_sparse_labels_data.csv"
CROSS_PNG = OUTDIR / "prs_agent_cross_trait_auc_scatter_typeA60_similar001_sparse_labels.png"


LABEL_OVERRIDES = {
    "abdominal aortic aneurysm": "Aortic aneurysm",
    "atrial fibrillation": "Atrial fibrillation",
    "breast carcinoma": "Breast cancer",
    "chronic obstructive pulmonary disease": "Obstructive lung disease",
    "dupuytren contracture": "Dupuytren",
    "hashimoto's thyroiditis": "Hashimoto's thyroiditis",
    "late-onset alzheimer's disease": "Alzheimer's disease",
    "lymphoid leukemia": "Leukemia",
    "myocardial infarction": "Myocardial infarction",
    "peripheral vascular disease": "Vascular disease",
    "squamous cell carcinoma": "Squamous carcinoma",
    "thyroid carcinoma": "Thyroid cancer",
    "simple and mucopurulent chronic bronchitis": "Chronic bronchitis",
    "major depressive disorder, recurrent": "Recurrent depression",
    "reaction to severe stress, and adjustment disorders": "Adjustment disorder",
    "disorders of purine and pyrimidine metabolism": "Purine metabolism disorder",
    "calculus of lower urinary tract": "Lower urinary tract calculus",
    "epilepsy and recurrent seizures": "Epilepsy",
    "specific personality disorders": "Personality disorder",
    "leiomyoma of uterus": "Uterine leiomyoma",
    "deformity and disproportion of reconstructed breast": "Breast reconstruction disorder",
    "polyp of female genital tract": "Female genital tract polyp",
    "carcinoma in situ of breast": "Breast carcinoma in situ",
    "obstructive and reflux uropathy": "Obstructive/reflux uropathy",
    "congenital malformations of aortic and mitral valves": "Aortic/mitral valve malformation",
    "absent, scanty and rare menstruation": "Menstrual disorders",
    "atrioventricular and left bundle-branch block": "Atrioventricular/bundle-branch block",
    "human immunodeficiency virus [hiv] disease": "HIV disease",
    "delirium due to known physiological condition": "Delirium",
}


FORCED_LABELS = {
    "within": {"cervical carcinoma"},
    "cross": set(),
}


MANUAL_LABEL_POSITIONS = {
    "within": {
        "thyroid carcinoma": (0.592, 0.789, "left", "center"),
        "hashimoto's thyroiditis": (0.642, 0.803, "left", "center"),
        "obesity": (0.565, 0.656, "left", "center"),
        "abdominal aortic aneurysm": (0.596, 0.633, "left", "center"),
        "atrial fibrillation": (0.505, 0.633, "right", "center"),
        "sleep apnea": (0.600, 0.544, "left", "center"),
        "asthma": (0.614, 0.582, "left", "center"),
        "osteoporosis": (0.523, 0.552, "right", "center"),
        "cervical carcinoma": (0.360, 0.395, "left", "center"),
    },
    "cross": {
        "deformity and disproportion of reconstructed breast": (0.566, 0.730, "left", "center"),
        "polyp of female genital tract": (0.500, 0.555, "right", "center"),
        "respiratory failure": (0.500, 0.582, "right", "center"),
        "hypertrichosis": (0.463, 0.532, "left", "center"),
        "cholecystitis": (0.506, 0.560, "right", "center"),
        "simple and mucopurulent chronic bronchitis": (0.522, 0.578, "left", "center"),
        "carcinoma in situ of breast": (0.586, 0.648, "left", "center"),
        "chronic gout": (0.620, 0.662, "left", "center"),
        "obstructive and reflux uropathy": (0.525, 0.468, "left", "center"),
        "congenital malformations of aortic and mitral valves": (0.535, 0.494, "left", "center"),
        "absent, scanty and rare menstruation": (0.535, 0.514, "left", "center"),
    },
}


def display_name(raw: str) -> str:
    key = str(raw).strip().lower()
    if key in LABEL_OVERRIDES:
        return LABEL_OVERRIDES[key]
    name = str(raw).strip()
    small_words = {"and", "of", "in", "to", "with", "for", "the"}
    words = []
    for i, word in enumerate(name.split()):
        lower = word.lower()
        words.append(lower if i and lower in small_words else lower.capitalize())
    return " ".join(words)


def selected_auc(row: dict) -> tuple[str, float, int | float | None]:
    pgs_id = row["modal_recommendation"]
    auc = row["benchmark_auc_by_id"].get(pgs_id)
    rank = row.get("modal_recommendation_rank")
    return pgs_id, float(auc) if auc is not None else math.nan, rank


def build_within_data() -> pd.DataFrame:
    baseline = json.loads(WITHIN_BASELINE_SUMMARY.read_text(encoding="utf-8"))["per_disease"]
    agent = json.loads(WITHIN_AGENT_SUMMARY.read_text(encoding="utf-8"))["per_disease"]
    baseline_by_trait = {row["ontology"].lower(): row for row in baseline}
    agent_by_trait = {row["ontology"].lower(): row for row in agent}

    rows = []
    for trait in sorted(baseline_by_trait):
        if trait not in agent_by_trait:
            continue
        baseline_pgs, baseline_auc, baseline_rank = selected_auc(baseline_by_trait[trait])
        agent_pgs, agent_auc, agent_rank = selected_auc(agent_by_trait[trait])
        rows.append(
            {
                "disease": trait,
                "display_name": display_name(trait),
                "baseline_auc": baseline_auc,
                "prs_agent_auc": agent_auc,
                "delta_auc": agent_auc - baseline_auc,
                "baseline_pgs_id": baseline_pgs,
                "prs_agent_pgs_id": agent_pgs,
                "baseline_rank": baseline_rank,
                "prs_agent_rank": agent_rank,
                "n_models": baseline_by_trait[trait].get("n_models"),
            }
        )
    df = pd.DataFrame(rows)
    if len(df) != 89:
        raise RuntimeError(f"Expected 89 within-trait rows, got {len(df)}")
    return df


def build_cross_data() -> pd.DataFrame:
    baseline = pd.read_csv(CROSS_BASELINE_DETAIL)
    agent = pd.read_csv(CROSS_AGENT_DETAIL)
    merged = baseline.merge(
        agent,
        on="target_id",
        suffixes=("_baseline", "_agent"),
        validate="one_to_one",
    )
    merged = merged[merged["input_type_agent"].eq("A")].copy()
    rows = []
    for _, row in merged.iterrows():
        disease = str(row["target_description_agent"]).strip()
        baseline_auc = float(row["selected_model_auc_baseline"])
        agent_auc = float(row["selected_model_auc_agent"])
        rows.append(
            {
                "target_id": row["target_id"],
                "input_type": row["input_type_agent"],
                "disease": disease.lower(),
                "display_name": display_name(disease),
                "baseline_auc": baseline_auc,
                "prs_agent_auc": agent_auc,
                "delta_auc": agent_auc - baseline_auc,
                "baseline_pgs_id": row["recommended_model_id_baseline"],
                "prs_agent_pgs_id": row["recommended_model_id_agent"],
                "baseline_rank": row["selected_model_rank_baseline"],
                "prs_agent_rank": row["selected_model_rank_agent"],
                "benchmark_top_model_auc": row["benchmark_top_model_auc_agent"],
            }
        )
    df = pd.DataFrame(rows).sort_values(["input_type", "target_id"]).reset_index(drop=True)
    if len(df) != 60:
        raise RuntimeError(f"Expected 60 type-A cross-trait rows, got {len(df)}")
    return df


def axis_limits(df: pd.DataFrame) -> tuple[float, float]:
    vals = pd.concat([df["baseline_auc"], df["prs_agent_auc"]]).dropna()
    lower = min(0.50, math.floor((float(vals.min()) - 0.015) / 0.05) * 0.05)
    upper = math.ceil((float(vals.max()) + 0.020) / 0.05) * 0.05
    return lower, upper


def point_colors(df: pd.DataFrame, similar_delta_auc: float) -> list[str]:
    colors = []
    for delta in df["delta_auc"]:
        if delta > similar_delta_auc:
            colors.append("#2F74A8")
        elif delta < -similar_delta_auc:
            colors.append("#B7665A")
        else:
            colors.append("#9AA3A8")
    return colors


def performance_class(delta: float, similar_delta_auc: float) -> str:
    if pd.isna(delta):
        return "Missing"
    if delta > similar_delta_auc:
        return "Improved"
    if delta < -similar_delta_auc:
        return "Lower"
    return "Similar"


def performance_class_counts(df: pd.DataFrame, similar_delta_auc: float) -> dict[str, int]:
    return {
        "Improved": int((df["delta_auc"] > similar_delta_auc).sum()),
        "Similar": int(
            ((df["delta_auc"] >= -similar_delta_auc) & (df["delta_auc"] <= similar_delta_auc)).sum()
        ),
        "Lower": int((df["delta_auc"] < -similar_delta_auc).sum()),
    }


FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(str(path), size=size)


def ticks(lower: float, upper: float, step: float) -> list[float]:
    start = math.ceil((lower - 1e-9) / step) * step
    vals = []
    x = start
    while x <= upper + 1e-9:
        vals.append(round(x, 3))
        x += step
    return vals


def draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    fill: str,
    width: int,
    dash: int = 34,
    gap: int = 24,
) -> None:
    x0, y0 = start
    x1, y1 = end
    dx = x1 - x0
    dy = y1 - y0
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    dist = 0.0
    while dist < length:
        seg_end = min(dist + dash, length)
        draw.line(
            [
                (x0 + ux * dist, y0 + uy * dist),
                (x0 + ux * seg_end, y0 + uy * seg_end),
            ],
            fill=fill,
            width=width,
        )
        dist += dash + gap


def draw_rotated_text(
    image: Image.Image,
    xy: tuple[int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    fill: str,
    anchor: str = "mm",
) -> None:
    dummy = Image.new("RGBA", (10, 10))
    dummy_draw = ImageDraw.Draw(dummy)
    bbox = dummy_draw.textbbox((0, 0), text, font=text_font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    layer = Image.new("RGBA", (width + 20, height + 20), (255, 255, 255, 0))
    layer_draw = ImageDraw.Draw(layer)
    layer_draw.text((10 - bbox[0], 10 - bbox[1]), text, font=text_font, fill=fill)
    rotated = layer.rotate(90, expand=True)
    x, y = xy
    if anchor == "mm":
        x -= rotated.width // 2
        y -= rotated.height // 2
    image.alpha_composite(rotated, (x, y))


def candidate_label_positions(
    point: tuple[float, float],
    text_bbox: tuple[int, int, int, int],
    plot_box: tuple[int, int, int, int],
) -> list[tuple[int, int, tuple[int, int, int, int]]]:
    px, py = point
    left, top, right, bottom = plot_box
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    offsets = [
        (28, -42),
        (34, 16),
        (-text_w - 34, -42),
        (-text_w - 34, 16),
        (20, -78),
        (-text_w - 20, -78),
        (20, 50),
        (-text_w - 20, 50),
    ]
    positions = []
    for dx, dy in offsets:
        x = int(px + dx)
        y = int(py + dy)
        x = max(left + 8, min(x, right - text_w - 8))
        y = max(top + 8, min(y, bottom - text_h - 8))
        positions.append((x, y, (x, y, x + text_w, y + text_h)))
    return positions


def overlaps(a: tuple[int, int, int, int], b: tuple[int, int, int, int], pad: int = 8) -> bool:
    return not (a[2] + pad < b[0] or b[2] + pad < a[0] or a[3] + pad < b[1] or b[3] + pad < a[1])


def label_rows(
    df: pd.DataFrame,
    mode: str,
    top_n_labels: int,
    lower_n_labels: int,
    similar_delta_auc: float,
) -> pd.DataFrame:
    improved = df[df["delta_auc"] > similar_delta_auc].sort_values("delta_auc", ascending=False).head(top_n_labels)
    lower = df[df["delta_auc"] < -similar_delta_auc].sort_values("delta_auc", ascending=True).head(lower_n_labels)
    forced_names = FORCED_LABELS.get(mode, set())
    forced = df[df["disease"].isin(forced_names)]
    return pd.concat([improved, lower, forced]).drop_duplicates(subset=["disease"])


def plot_all_diseases(
    df: pd.DataFrame,
    mode: str,
    outfile: Path,
    top_n_labels: int,
    lower_n_labels: int,
    similar_delta_auc: float,
) -> None:
    df = df.dropna(subset=["baseline_auc", "prs_agent_auc"]).copy()
    lower, upper = axis_limits(df)
    scale = 2
    width, height = 2200 * scale, 2200 * scale
    image = Image.new("RGBA", (width, height), "white")
    draw = ImageDraw.Draw(image)

    left, top, right, bottom = (390 * scale, 130 * scale, 2040 * scale, 1780 * scale)
    plot_w = right - left
    plot_h = bottom - top

    def xy(x: float, y: float) -> tuple[float, float]:
        px = left + (x - lower) / (upper - lower) * plot_w
        py = bottom - (y - lower) / (upper - lower) * plot_h
        return px, py

    # Grid.
    for t in ticks(lower, upper, 0.025):
        px, _ = xy(t, lower)
        _, py = xy(lower, t)
        draw.line([(px, top), (px, bottom)], fill="#ECEFF1", width=2 * scale)
        draw.line([(left, py), (right, py)], fill="#ECEFF1", width=2 * scale)
    for t in ticks(lower, upper, 0.10):
        px, _ = xy(t, lower)
        _, py = xy(lower, t)
        draw.line([(px, top), (px, bottom)], fill="#D9DEE3", width=4 * scale)
        draw.line([(left, py), (right, py)], fill="#D9DEE3", width=4 * scale)

    # Axes and diagonal.
    draw.line([(left, bottom), (right, bottom)], fill="black", width=6 * scale)
    draw.line([(left, bottom), (left, top)], fill="black", width=6 * scale)
    draw_dashed_line(draw, xy(lower, lower), xy(upper, upper), fill="black", width=5 * scale)

    tick_font = font(34 * scale)
    axis_font = font(42 * scale, bold=True)
    label_font = font(26 * scale)
    legend_font = font(28 * scale)
    for t in ticks(lower, upper, 0.10):
        px, py0 = xy(t, lower)
        _, py = xy(lower, t)
        draw.line([(px, bottom), (px, bottom + 28 * scale)], fill="black", width=5 * scale)
        draw.line([(left - 28 * scale, py), (left, py)], fill="black", width=5 * scale)
        label = f"{t:.2f}"
        bbox = draw.textbbox((0, 0), label, font=tick_font)
        draw.text((px - (bbox[2] - bbox[0]) / 2, bottom + 46 * scale), label, font=tick_font, fill="black")
        draw.text((left - 78 * scale - (bbox[2] - bbox[0]), py - (bbox[3] - bbox[1]) / 2), label, font=tick_font, fill="black")

    x_label = "Baseline LLM selected-model AUC"
    x_bbox = draw.textbbox((0, 0), x_label, font=axis_font)
    draw.text(
        (left + plot_w / 2 - (x_bbox[2] - x_bbox[0]) / 2, bottom + 126 * scale),
        x_label,
        font=axis_font,
        fill="black",
    )
    draw_rotated_text(
        image,
        (82 * scale, top + plot_h // 2),
        "PRS Agent selected-model AUC",
        axis_font,
        "black",
    )

    # Points.
    point_radius = 10 * scale
    for (_, row), color in zip(df.iterrows(), point_colors(df, similar_delta_auc), strict=True):
        px, py = xy(float(row["baseline_auc"]), float(row["prs_agent_auc"]))
        draw.ellipse(
            (px - point_radius, py - point_radius, px + point_radius, py + point_radius),
            fill=color,
            outline="white",
            width=2 * scale,
        )

    # Callouts for the largest positive deltas and several lower-performing traits; all diseases remain plotted.
    placed: list[tuple[int, int, int, int]] = []
    plot_box = (left, top, right, bottom)
    manual_positions = MANUAL_LABEL_POSITIONS.get(mode, {})
    for _, row in label_rows(
        df,
        mode=mode,
        top_n_labels=top_n_labels,
        lower_n_labels=lower_n_labels,
        similar_delta_auc=similar_delta_auc,
    ).iterrows():
        label = row["display_name"]
        px, py = xy(float(row["baseline_auc"]), float(row["prs_agent_auc"]))
        text_bbox = draw.textbbox((0, 0), label, font=label_font)
        disease_key = str(row["disease"]).lower()
        if disease_key in manual_positions:
            label_x, label_y, ha, va = manual_positions[disease_key]
            label_px, label_py = xy(label_x, label_y)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            if ha == "right":
                tx = int(label_px - text_w)
            elif ha == "center":
                tx = int(label_px - text_w / 2)
            else:
                tx = int(label_px)
            if va == "center":
                ty = int(label_py - text_h / 2)
            else:
                ty = int(label_py)
            tx = max(left + 8, min(tx, right - text_w - 8))
            ty = max(top + 8, min(ty, bottom - text_h - 8))
            bbox = (tx, ty, tx + text_w, ty + text_h)
        else:
            candidates = candidate_label_positions((px, py), text_bbox, plot_box)
            chosen = candidates[0]
            for candidate in candidates:
                if not any(overlaps(candidate[2], existing, pad=14 * scale) for existing in placed):
                    chosen = candidate
                    break
            tx, ty, bbox = chosen
        placed.append(bbox)
        draw.line([(px, py), (tx, ty + (bbox[3] - bbox[1]) / 2)], fill="#555555", width=3 * scale)
        draw.text((tx, ty), label, font=label_font, fill="black")

    # Compact state legend, not an 80/89-item disease legend.
    counts = performance_class_counts(df, similar_delta_auc)
    legend_x = left
    legend_y = bottom + 285 * scale
    legend_items = [
        (f"Improved (n={counts['Improved']})", "#2F74A8"),
        (f"Similar (n={counts['Similar']})", "#9AA3A8"),
        (f"Lower (n={counts['Lower']})", "#B7665A"),
    ]
    draw.rounded_rectangle(
        (legend_x - 28 * scale, legend_y - 28 * scale, right, legend_y + 72 * scale),
        radius=12 * scale,
        fill="#EEF2F5",
    )
    cursor = legend_x
    for label, color in legend_items:
        draw.ellipse((cursor, legend_y, cursor + 24 * scale, legend_y + 24 * scale), fill=color, outline="white", width=2 * scale)
        draw.text((cursor + 38 * scale, legend_y - 7 * scale), label, font=legend_font, fill="black")
        text_w = draw.textbbox((0, 0), label, font=legend_font)[2]
        cursor += text_w + 120 * scale

    image = image.resize((width // scale, height // scale), Image.Resampling.LANCZOS).convert("RGB")
    outfile.parent.mkdir(parents=True, exist_ok=True)
    image.save(outfile, "PNG")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot all-disease PRS Agent AUC scatter figures without filtering.")
    parser.add_argument("--mode", choices=["within", "cross", "both"], default="both")
    args = parser.parse_args()

    if args.mode in {"within", "both"}:
        within = build_within_data()
        within["performance_class"] = within["delta_auc"].map(
            lambda delta: performance_class(delta, WITHIN_SIMILAR_DELTA_AUC)
        )
        within.to_csv(WITHIN_DATA, index=False)
        plot_all_diseases(
            within,
            "within",
            WITHIN_PNG,
            top_n_labels=5,
            lower_n_labels=3,
            similar_delta_auc=WITHIN_SIMILAR_DELTA_AUC,
        )
        print(f"within_rows={len(within)}")
        print(f"within_plotted={len(within.dropna(subset=['baseline_auc', 'prs_agent_auc']))}")
        print(f"within_data={WITHIN_DATA}")
        print(f"within_png={WITHIN_PNG}")

    if args.mode in {"cross", "both"}:
        cross = build_cross_data()
        cross["performance_class"] = cross["delta_auc"].map(
            lambda delta: performance_class(delta, CROSS_SIMILAR_DELTA_AUC)
        )
        cross.to_csv(CROSS_DATA, index=False)
        plot_all_diseases(
            cross,
            "cross",
            CROSS_PNG,
            top_n_labels=6,
            lower_n_labels=3,
            similar_delta_auc=CROSS_SIMILAR_DELTA_AUC,
        )
        print(f"cross_rows={len(cross)}")
        print(f"cross_plotted={len(cross.dropna(subset=['baseline_auc', 'prs_agent_auc']))}")
        print(f"cross_data={CROSS_DATA}")
        print(f"cross_png={CROSS_PNG}")


if __name__ == "__main__":
    main()
