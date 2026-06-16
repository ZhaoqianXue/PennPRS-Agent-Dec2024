from __future__ import annotations

import argparse
import colorsys
import json
from pathlib import Path

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox, ScaledTranslation

try:
    from adjustText import adjust_text
except ImportError:  # pragma: no cover
    adjust_text = None


ROOT = Path(__file__).resolve().parents[1]
WITHIN_DATA = ROOT / "output/doc/prs_agent_auc_scatter_29_v7_data.csv"
CROSS_DATA = ROOT / "output/doc/prs_agent_cross_trait_auc_scatter_typeA59_source_data.csv"
WITHIN82_DATA = ROOT / "output/doc/prs_agent_auc_scatter_82disease_source_data.csv"
CROSS_TYPEA59_DETAIL = (
    ROOT
    / "experiments/contribution3/transfer/runs/tool_calling_agent/unified/"
    / "ablation__no_all_tools_tuned_breadth/"
    / "evaluation__typeA59_legacy80_no_aou_recomputed_20260526_143244/"
    / "typeA59_baseline_vs_prs_agent_detail.csv"
)
WITHIN82_BASELINE_SUMMARY = (
    ROOT
    / "experiments/contribution2/recommendation/runs/without-domain-gpt-5.2-t1__82disease__c82-within-baseline-20260526/experiment_without_domain_summary.json"
)
WITHIN82_AGENT_SUMMARY = (
    ROOT
    / "experiments/contribution2/recommendation/runs/pairwise-rerank-gpt-5.2-t1__82disease__c82-within-agent-top5-final-20260526-20260526-120628/experiment_pairwise_rerank_summary.json"
)
OUTDIR = ROOT / "output/doc"


WITHIN_TOP_LABELS = {
    "obesity": "Obesity",
    "atrial fibrillation": "Atrial fibrillation",
    "angina pectoris": "Angina",
    "dupuytren contracture": "Dupuytren",
    "gout": "Gout",
}

WITHIN_EXCLUDED_AFTER_AOU_FILTER = {
    "hashimoto's thyroiditis",
    "thyroid carcinoma",
}

WITHIN_LEGEND_LABELS = {
    "abdominal aortic aneurysm": "Aortic aneurysm",
    "angina pectoris": "Angina",
    "breast carcinoma": "Breast cancer",
    "chronic obstructive pulmonary disease": "Obstructive lung disease",
    "dupuytren contracture": "Dupuytren",
    "hashimoto's thyroiditis": "Hashimoto's thyroiditis",
    "late-onset alzheimer's disease": "Alzheimer's disease",
    "lymphoid leukemia": "Leukemia",
    "peripheral vascular disease": "Vascular disease",
    "squamous cell carcinoma": "Squamous carcinoma",
    "thyroid carcinoma": "Thyroid cancer",
}

WITHIN82_TOP_LABELS = {
    "obesity": "Obesity",
    "ulcerative colitis": "Ulcerative colitis",
    "abdominal aortic aneurysm": "Aortic aneurysm",
    "dupuytren contracture": "Dupuytren",
    "type 2 diabetes mellitus": "Type 2 diabetes",
    "coronary artery disease": "Coronary artery disease",
    "myocardial infarction": "Myocardial infarction",
    "late-onset alzheimer's disease": "Alzheimer's disease",
}

WITHIN82_LEGEND_LABELS = {
    "abdominal aortic aneurysm": "Aortic aneurysm",
    "alcoholic liver cirrhosis": "Alcoholic liver cirrhosis",
    "ankylosing spondylitis": "Ankylosing spondylitis",
    "angina pectoris": "Angina",
    "asthma": "Asthma",
    "atrial fibrillation": "Atrial fibrillation",
    "basal cell carcinoma": "Basal cell carcinoma",
    "bilirubin metabolism disease": "Bilirubin metabolism disease",
    "breast carcinoma": "Breast cancer",
    "cervical carcinoma": "Cervical cancer",
    "chronic lymphocytic leukemia": "Chronic lymphocytic leukemia",
    "chronic obstructive pulmonary disease": "Obstructive lung disease",
    "coronary artery disease": "Coronary artery disease",
    "crohn's disease": "Crohn's disease",
    "depressive disorder": "Depressive disorder",
    "dupuytren contracture": "Dupuytren",
    "glaucoma": "Glaucoma",
    "gout": "Gout",
    "hip osteoarthritis": "Hip osteoarthritis",
    "kidney failure": "Kidney failure",
    "late-onset alzheimer's disease": "Alzheimer's disease",
    "lupus erythematosus": "Lupus erythematosus",
    "myocardial infarction": "Myocardial infarction",
    "osteoporosis": "Osteoporosis",
    "ovarian neoplasm": "Ovarian neoplasm",
    "prostate cancer": "Prostate cancer",
    "pulmonary fibrosis": "Pulmonary fibrosis",
    "rheumatoid arthritis": "Rheumatoid arthritis",
    "type 2 diabetes mellitus": "Type 2 diabetes",
    "type 1 diabetes mellitus": "Type 1 diabetes",
    "ulcerative colitis": "Ulcerative colitis",
}

WITHIN82_EXCLUDED_DISEASES = {
    "ankylosing spondylitis",
    "bilirubin metabolism disease",
    "cervical carcinoma",
    "ovarian neoplasm",
    "testicular carcinoma",
}

WITHIN82_NEAR_ZERO_DISEASES = {
    "asthma",
    "breast carcinoma",
    "crohn's disease",
    "glaucoma",
    "gout",
    "rheumatoid arthritis",
    "type 1 diabetes mellitus",
}

WITHIN82_NEGATIVE_DISEASES = {
    "lupus erythematosus",
    "osteoporosis",
}

CROSS_TOP_LABELS = {
    "simple and mucopurulent chronic bronchitis": "Chronic bronchitis",
    "chronic gout": "Chronic gout",
    "cholecystitis": "Cholecystitis",
    "persistent mood [affective] disorders": "Persistent mood disorder",
    "umbilical hernia": "Umbilical hernia",
}

CROSS_LEGEND_LABELS = {
    "acute pyelonephritis": "Acute pyelonephritis",
    "benign mammary dysplasia": "Benign mammary dysplasia",
    "deformity and disproportion of reconstructed breast": "Breast reconstruction disorder",
    "dissociative and conversion disorders": "Dissociative/conversion disorders",
    "female infertility": "Female infertility",
    "esophageal varices": "Esophageal varices",
    "polyp of female genital tract": "Female genital tract polyp",
    "hypertrichosis": "Hypertrichosis",
    "absent, scanty and rare menstruation": "Menstrual disorders",
    "respiratory failure": "Respiratory failure",
    "emphysema": "Emphysema",
    "cholecystitis": "Cholecystitis",
    "chronic viral hepatitis": "Chronic viral hepatitis",
    "delusional disorders": "Delusional disorders",
    "chronic bronchitis": "Chronic bronchitis",
    "hypertensive crisis": "Hypertensive crisis",
    "melanoma in situ": "Melanoma in situ",
    "migraine": "Migraine",
    "myocardial infarction": "Myocardial infarction",
    "bipolar disorder": "Bipolar disorder",
    "chronic gout": "Chronic gout",
    "purine metabolism disorder": "Purine metabolism disorder",
    "ventral hernia": "Ventral hernia",
    "recurrent depression": "Recurrent depression",
    "epilepsy": "Epilepsy",
    "benign breast neoplasm": "Benign breast neoplasm",
    "personality disorder": "Personality disorder",
    "umbilical hernia": "Umbilical hernia",
    "adjustment disorder": "Adjustment disorder",
    "uterine leiomyoma": "Uterine leiomyoma",
    "urinary tract calculus": "Urinary tract calculus",
    "obsessive-compulsive disorder": "Obsessive-compulsive disorder",
    "skin carcinoma in situ": "Skin carcinoma in situ",
    "acute myocardial infarction": "Acute myocardial infarction",
    "benign neoplasm of breast": "Benign breast neoplasm",
    "carcinoma in situ of skin": "Skin carcinoma in situ",
    "calculus of lower urinary tract": "Lower urinary tract calculus",
    "disorders of purine and pyrimidine metabolism": "Purine metabolism disorder",
    "epilepsy and recurrent seizures": "Epilepsy",
    "leiomyoma of uterus": "Uterine leiomyoma",
    "major depressive disorder, recurrent": "Major depressive disorder",
    "reaction to severe stress, and adjustment disorders": "Adjustment disorder",
    "simple and mucopurulent chronic bronchitis": "Chronic bronchitis",
    "specific personality disorders": "Personality disorder",
    "carcinoma in situ of breast": "Breast carcinoma in situ",
    "inflammatory disorders of breast": "Inflammatory breast disease",
    "skin changes due to chronic exposure to nonionizing radiation": "Chronic skin photodamage",
    "atrophy of kidney (terminal)": "Kidney atrophy",
    "peritonitis": "Peritonitis",
    "cocaine related disorders": "Cocaine-related disorder",
    "opioid related disorders": "Opioid-related disorder",
    "cutaneous abscess, furuncle and carbuncle": "Cutaneous abscess",
    "osteomyelitis": "Osteomyelitis",
    "secondary hypertension": "Secondary hypertension",
    "persistent mood [affective] disorders": "Persistent mood disorder",
    "human immunodeficiency virus [hiv] disease": "HIV disease",
    "acute pancreatitis": "Acute pancreatitis",
    "delirium due to known physiological condition": "Delirium",
}

CROSS_NEAR_ZERO_DISEASES = {
    "acute pyelonephritis",
    "benign mammary dysplasia",
    "dissociative and conversion disorders",
    "esophageal varices",
    "female infertility",
    "migraine",
}

CROSS_NEGATIVE_DISEASES = {
    "chronic viral hepatitis",
    "delusional disorders",
}

CROSS_EXCLUDED_DISEASES = {
    "carcinoma in situ of breast",
    "cocaine related disorders",
    "deformity and disproportion of reconstructed breast",
    "hypertensive heart disease",
    "major depressive disorder, recurrent",
    "melanoma in situ",
    "obsessive-compulsive disorder",
    "opioid related disorders",
    "skin changes due to chronic exposure to nonionizing radiation",
}

PUBLICATION_COLORS = {
    # Muted publication palette with deliberately separated neighboring hues.
    "abdominal aortic aneurysm": "#B64A3A",
    "angina pectoris": "#5B7FC5",
    "ankylosing spondylitis": "#C8A43A",
    "atrial fibrillation": "#D99A2B",
    "asthma": "#B6543E",
    "breast carcinoma": "#7A5A3A",
    "chronic obstructive pulmonary disease": "#607D8B",
    "dilated cardiomyopathy": "#4E9B4E",
    "dupuytren contracture": "#3BA7A8",
    "glaucoma": "#3574B8",
    "gout": "#7D62B2",
    "crohn's disease": "#8D9F3F",
    "hashimoto's thyroiditis": "#2E8B75",
    "heart failure": "#C05A6A",
    "hip osteoarthritis": "#E0704E",
    "hyperthyroidism": "#A05EB5",
    "kidney failure": "#5DA5D1",
    "knee osteoarthritis": "#88A63A",
    "late-onset alzheimer's disease": "#C49A2C",
    "lupus erythematosus": "#B279A2",
    "lymphoid leukemia": "#D65F5F",
    "melanoma": "#9A6B4A",
    "myocardial infarction": "#4F9BD3",
    "obesity": "#D88A72",
    "otosclerosis": "#5FA36D",
    "ovarian neoplasm": "#6A4C93",
    "osteoporosis": "#C28E4E",
    "peripheral vascular disease": "#5F7EB4",
    "retinal detachment": "#A6A64A",
    "squamous cell carcinoma": "#D586B7",
    "thyroid carcinoma": "#A86A90",
    "type 1 diabetes mellitus": "#6E9F75",
    "uterine cancer": "#79BFA4",
    "alcoholic liver cirrhosis": "#B08968",
    "basal cell carcinoma": "#C9826B",
    "bilirubin metabolism disease": "#B8A34F",
    "cervical carcinoma": "#B35C9E",
    "chronic lymphocytic leukemia": "#9D6B8E",
    "coronary artery disease": "#4E8A5B",
    "dementia": "#8C7AA9",
    "depressive disorder": "#A66E9E",
    "prostate cancer": "#B96E7D",
    "pulmonary fibrosis": "#6F8FA3",
    "rheumatoid arthritis": "#B9A15B",
    "sarcoidosis": "#8CA06A",
    "testicular carcinoma": "#8D6B3D",
    "type 2 diabetes mellitus": "#D6A03A",
    "ulcerative colitis": "#5C8EB8",
    "deformity and disproportion of reconstructed breast": "#BD6B5F",
    "acute pyelonephritis": "#7AAE8A",
    "benign mammary dysplasia": "#C98974",
    "polyp of female genital tract": "#6E8DC8",
    "hypertrichosis": "#BFA45B",
    "absent, scanty and rare menstruation": "#B38B5E",
    "dissociative and conversion disorders": "#8E77B8",
    "female infertility": "#C79C48",
    "simple and mucopurulent chronic bronchitis": "#5FAFAE",
    "carcinoma in situ of breast": "#C26876",
    "respiratory failure": "#7F6DB1",
    "chronic gout": "#6CA4C9",
    "disorders of purine and pyrimidine metabolism": "#91A955",
    "umbilical hernia": "#C69A32",
    "inflammatory disorders of breast": "#A95E5E",
    "ventral hernia": "#A86DB8",
    "chronic viral hepatitis": "#A95E5E",
    "skin changes due to chronic exposure to nonionizing radiation": "#6A8F9D",
    "cholecystitis": "#B88D2B",
    "delusional disorders": "#7F6DB1",
    "esophageal varices": "#8FA05A",
    "diabetes mellitus due to underlying condition": "#C9A23F",
    "hypertensive heart disease": "#6B9D63",
    "hypertensive crisis": "#B96E7D",
    "melanoma in situ": "#9A6B4A",
    "migraine": "#6C8FC4",
    "major depressive disorder, recurrent": "#A66E9E",
    "atrophy of kidney (terminal)": "#5D8FA8",
    "benign neoplasm of breast": "#D18364",
    "specific personality disorders": "#8C7AA9",
    "peritonitis": "#9B6F4A",
    "cocaine related disorders": "#9D6B8E",
    "opioid related disorders": "#A66A8E",
    "cutaneous abscess, furuncle and carbuncle": "#C06BA5",
    "osteomyelitis": "#79A879",
    "secondary hypertension": "#4E8A5B",
    "calculus of lower urinary tract": "#D99A2B",
    "persistent mood [affective] disorders": "#A66E9E",
    "human immunodeficiency virus [hiv] disease": "#5DA5D1",
    "acute pancreatitis": "#D36F4F",
    "delirium due to known physiological condition": "#6F8FA3",
}


LAYOUTS = {
    "v16": {
        "name": "local-balanced",
        "figsize": (9.2, 7.1),
        "ax_rect": [0.155, 0.37, 0.66, 0.51],
        "legend_rect": [0.055, 0.035, 0.89, 0.255],
        "fontsize": 8.2,
        "point_size": 56,
        "label_positions": {
            "thyroid carcinoma": (0.510, 0.806, "left", "center"),
            "hashimoto's thyroiditis": (0.655, 0.807, "left", "center"),
            "obesity": (0.506, 0.666, "left", "center"),
            "ovarian neoplasm": (0.505, 0.644, "left", "center"),
            "atrial fibrillation": (0.608, 0.637, "left", "center"),
            "abdominal aortic aneurysm": (0.608, 0.659, "left", "center"),
            "hyperthyroidism": (0.609, 0.616, "left", "center"),
            "peripheral vascular disease": (0.607, 0.591, "left", "center"),
            "late-onset alzheimer's disease": (0.604, 0.561, "left", "center"),
        },
    },
    "v17": {
        "name": "compact-reference",
        "figsize": (9.0, 6.8),
        "ax_rect": [0.15, 0.365, 0.65, 0.50],
        "legend_rect": [0.055, 0.035, 0.89, 0.25],
        "fontsize": 7.8,
        "point_size": 52,
        "label_positions": {
            "thyroid carcinoma": (0.515, 0.807, "left", "center"),
            "hashimoto's thyroiditis": (0.665, 0.806, "left", "center"),
            "obesity": (0.507, 0.665, "left", "center"),
            "ovarian neoplasm": (0.504, 0.644, "left", "center"),
            "atrial fibrillation": (0.594, 0.641, "left", "center"),
            "abdominal aortic aneurysm": (0.611, 0.657, "left", "center"),
            "hyperthyroidism": (0.606, 0.613, "left", "center"),
            "peripheral vascular disease": (0.533, 0.590, "left", "center"),
            "late-onset alzheimer's disease": (0.508, 0.556, "left", "center"),
        },
    },
    "v18": {
        "name": "wide-with-right-gutter",
        "figsize": (9.8, 6.9),
        "ax_rect": [0.13, 0.365, 0.57, 0.50],
        "legend_rect": [0.055, 0.035, 0.89, 0.25],
        "fontsize": 8.0,
        "point_size": 54,
        "label_positions": {
            "thyroid carcinoma": (0.507, 0.805, "left", "center"),
            "hashimoto's thyroiditis": (0.653, 0.807, "left", "center"),
            "obesity": (0.505, 0.665, "left", "center"),
            "ovarian neoplasm": (0.505, 0.644, "left", "center"),
            "abdominal aortic aneurysm": (0.824, 0.651, "left", "center"),
            "atrial fibrillation": (0.824, 0.629, "left", "center"),
            "hyperthyroidism": (0.824, 0.608, "left", "center"),
            "peripheral vascular disease": (0.824, 0.586, "left", "center"),
            "late-onset alzheimer's disease": (0.824, 0.560, "left", "center"),
        },
    },
    "v19": {
        "name": "left-right-callouts",
        "figsize": (9.4, 6.95),
        "ax_rect": [0.15, 0.37, 0.61, 0.50],
        "legend_rect": [0.055, 0.035, 0.89, 0.255],
        "fontsize": 8.0,
        "point_size": 54,
        "label_positions": {
            "thyroid carcinoma": (0.507, 0.805, "left", "center"),
            "hashimoto's thyroiditis": (0.657, 0.806, "left", "center"),
            "obesity": (0.508, 0.667, "left", "center"),
            "ovarian neoplasm": (0.507, 0.644, "left", "center"),
            "abdominal aortic aneurysm": (0.650, 0.661, "left", "center"),
            "atrial fibrillation": (0.651, 0.637, "left", "center"),
            "hyperthyroidism": (0.650, 0.612, "left", "center"),
            "peripheral vascular disease": (0.500, 0.589, "left", "center"),
            "late-onset alzheimer's disease": (0.501, 0.555, "left", "center"),
        },
    },
    "v20": {
        "name": "auto-repel-reference",
        "figsize": (9.1, 7.2),
        "ax_rect": [0.17, 0.405, 0.58, 0.465],
        "legend_rect": [0.065, 0.035, 0.87, 0.220],
        "legend_fontsize": 7.0,
        "legend_markersize": 5.1,
        "fontsize": 7.4,
        "point_size": 43,
        "auto_adjust": True,
        "label_positions": {
            "thyroid carcinoma": (0.512, 0.804, "left", "center"),
            "hashimoto's thyroiditis": (0.658, 0.806, "left", "center"),
            "obesity": (0.511, 0.661, "left", "center"),
            "ovarian neoplasm": (0.505, 0.641, "left", "center"),
            "abdominal aortic aneurysm": (0.610, 0.656, "left", "center"),
            "atrial fibrillation": (0.604, 0.633, "left", "center"),
            "hyperthyroidism": (0.607, 0.612, "left", "center"),
            "peripheral vascular disease": (0.530, 0.592, "left", "center"),
            "late-onset alzheimer's disease": (0.509, 0.555, "left", "center"),
        },
    },
    "v21": {
        "name": "open-gutter-reference",
        "figsize": (9.4, 7.05),
        "ax_rect": [0.15, 0.405, 0.56, 0.465],
        "legend_rect": [0.065, 0.035, 0.87, 0.218],
        "legend_fontsize": 7.0,
        "legend_markersize": 5.1,
        "fontsize": 7.5,
        "point_size": 44,
        "label_positions": {
            "thyroid carcinoma": (0.510, 0.804, "left", "center"),
            "hashimoto's thyroiditis": (0.654, 0.806, "left", "center"),
            "obesity": (0.506, 0.663, "left", "center"),
            "ovarian neoplasm": (0.505, 0.643, "left", "center"),
            "abdominal aortic aneurysm": (0.728, 0.651, "left", "center"),
            "atrial fibrillation": (0.728, 0.628, "left", "center"),
            "hyperthyroidism": (0.728, 0.607, "left", "center"),
            "peripheral vascular disease": (0.728, 0.586, "left", "center"),
            "late-onset alzheimer's disease": (0.728, 0.559, "left", "center"),
        },
    },
    "v22": {
        "name": "manual-publication-compact",
        "figsize": (9.0, 7.0),
        "ax_rect": [0.165, 0.410, 0.57, 0.455],
        "legend_rect": [0.065, 0.030, 0.87, 0.215],
        "legend_fontsize": 6.9,
        "legend_markersize": 5.0,
        "fontsize": 7.1,
        "point_size": 42,
        "axis_labelsize": 11.3,
        "title_fontsize": 14.6,
        "label_positions": {
            "thyroid carcinoma": (0.510, 0.803, "left", "center"),
            "hashimoto's thyroiditis": (0.654, 0.806, "left", "center"),
            "obesity": (0.507, 0.659, "left", "center"),
            "ovarian neoplasm": (0.509, 0.640, "left", "center"),
            "abdominal aortic aneurysm": (0.619, 0.650, "left", "center"),
            "atrial fibrillation": (0.615, 0.630, "left", "center"),
            "hyperthyroidism": (0.614, 0.611, "left", "center"),
            "peripheral vascular disease": (0.534, 0.588, "left", "center"),
            "late-onset alzheimer's disease": (0.508, 0.553, "left", "center"),
        },
    },
    "v23": {
        "name": "manual-publication-4col-legend",
        "figsize": (9.2, 6.65),
        "ax_rect": [0.158, 0.390, 0.57, 0.475],
        "legend_rect": [0.055, 0.030, 0.89, 0.185],
        "legend_ncol": 4,
        "legend_fontsize": 6.5,
        "legend_markersize": 4.7,
        "fontsize": 7.0,
        "point_size": 42,
        "axis_labelsize": 11.2,
        "title_fontsize": 14.4,
        "label_positions": {
            "thyroid carcinoma": (0.510, 0.803, "left", "center"),
            "hashimoto's thyroiditis": (0.654, 0.806, "left", "center"),
            "obesity": (0.507, 0.659, "left", "center"),
            "ovarian neoplasm": (0.509, 0.640, "left", "center"),
            "abdominal aortic aneurysm": (0.619, 0.650, "left", "center"),
            "atrial fibrillation": (0.615, 0.630, "left", "center"),
            "hyperthyroidism": (0.614, 0.611, "left", "center"),
            "peripheral vascular disease": (0.534, 0.588, "left", "center"),
            "late-onset alzheimer's disease": (0.508, 0.553, "left", "center"),
        },
    },
    "v24": {
        "name": "wide-axis-clean-callouts",
        "figsize": (10.2, 7.0),
        "ax_rect": [0.115, 0.410, 0.72, 0.455],
        "legend_rect": [0.055, 0.030, 0.89, 0.215],
        "legend_fontsize": 6.95,
        "legend_markersize": 5.0,
        "fontsize": 7.35,
        "point_size": 43,
        "axis_labelsize": 11.4,
        "title_fontsize": 14.8,
        "xlim": (0.50, 0.86),
        "ylim": (0.50, 0.82),
        "diag_end": 0.82,
        "label_positions": {
            "thyroid carcinoma": (0.510, 0.804, "left", "center"),
            "hashimoto's thyroiditis": (0.655, 0.806, "left", "center"),
            "obesity": (0.506, 0.660, "left", "center"),
            "ovarian neoplasm": (0.506, 0.640, "left", "center"),
            "abdominal aortic aneurysm": (0.676, 0.651, "left", "center"),
            "atrial fibrillation": (0.676, 0.630, "left", "center"),
            "hyperthyroidism": (0.676, 0.610, "left", "center"),
            "peripheral vascular disease": (0.676, 0.589, "left", "center"),
            "late-onset alzheimer's disease": (0.676, 0.562, "left", "center"),
        },
    },
    "v25": {
        "name": "wide-axis-final-candidate",
        "figsize": (10.0, 6.9),
        "ax_rect": [0.120, 0.412, 0.70, 0.455],
        "legend_rect": [0.055, 0.030, 0.89, 0.212],
        "legend_fontsize": 6.95,
        "legend_markersize": 5.0,
        "fontsize": 7.55,
        "point_size": 45,
        "axis_labelsize": 11.4,
        "title_fontsize": 14.8,
        "xlim": (0.50, 0.84),
        "ylim": (0.50, 0.82),
        "diag_end": 0.82,
        "label_positions": {
            "thyroid carcinoma": (0.510, 0.804, "left", "center"),
            "hashimoto's thyroiditis": (0.654, 0.806, "left", "center"),
            "obesity": (0.506, 0.660, "left", "center"),
            "ovarian neoplasm": (0.506, 0.640, "left", "center"),
            "abdominal aortic aneurysm": (0.666, 0.652, "left", "center"),
            "atrial fibrillation": (0.666, 0.631, "left", "center"),
            "hyperthyroidism": (0.666, 0.611, "left", "center"),
            "peripheral vascular disease": (0.666, 0.589, "left", "center"),
            "late-onset alzheimer's disease": (0.666, 0.562, "left", "center"),
        },
    },
    "v26": {
        "name": "no-title-separated-points",
        "figsize": (10.0, 6.35),
        "ax_rect": [0.120, 0.435, 0.70, 0.505],
        "legend_rect": [0.055, 0.030, 0.89, 0.220],
        "legend_fontsize": 6.95,
        "legend_markersize": 5.0,
        "fontsize": 7.25,
        "label_fontfamily": "Helvetica",
        "label_fontweight": "normal",
        "label_path_effect": False,
        "point_size": 28,
        "point_linewidth": 0.85,
        "point_alpha": 0.94,
        "axis_labelsize": 11.4,
        "show_title": False,
        "xlim": (0.50, 0.84),
        "ylim": (0.50, 0.82),
        "diag_end": 0.82,
        "point_offsets": {
            "abdominal aortic aneurysm": (-4.2, -2.0),
            "atrial fibrillation": (4.2, 2.0),
            "kidney failure": (-1.9, 1.2),
            "retinal detachment": (-3.0, -2.2),
            "breast carcinoma": (-1.5, 1.0),
            "glaucoma": (1.5, -1.0),
            "dupuytren contracture": (1.4, 1.0),
            "gout": (-1.4, -1.0),
            "myocardial infarction": (-1.3, 1.0),
            "uterine cancer": (1.3, -1.0),
            "angina pectoris": (-1.3, 1.0),
            "hip osteoarthritis": (1.3, -1.0),
            "melanoma": (0.4, 0.3),
            "squamous cell carcinoma": (1.2, 1.0),
            "heart failure": (-2.2, 1.6),
            "squamous cell carcinoma": (3.5, 1.5),
        },
        "label_positions": {
            "thyroid carcinoma": (0.510, 0.804, "left", "center"),
            "hashimoto's thyroiditis": (0.654, 0.806, "left", "center"),
            "obesity": (0.506, 0.660, "left", "center"),
            "ovarian neoplasm": (0.506, 0.640, "left", "center"),
            "atrial fibrillation": (0.658, 0.632, "left", "center"),
            "hyperthyroidism": (0.666, 0.611, "left", "center"),
            "peripheral vascular disease": (0.666, 0.589, "left", "center"),
            "late-onset alzheimer's disease": (0.666, 0.562, "left", "center"),
            "dupuytren contracture": (0.665, 0.679, "left", "center"),
            "gout": (0.665, 0.666, "left", "center"),
        },
    },
}


LAYOUTS["v27"] = {**LAYOUTS["v26"], "name": "requested-labels"}
LAYOUTS["v28"] = {
    **LAYOUTS["v26"],
    "name": "reference-font-labels",
    "fontsize": 7.65,
    "legend_fontsize": 7.05,
}
LAYOUTS["v29"] = {
    **LAYOUTS["v28"],
    "name": "reference-font-clean-gout",
    "label_positions": {
        **LAYOUTS["v28"]["label_positions"],
        "dupuytren contracture": (0.666, 0.680, "left", "center"),
        "gout": (0.617, 0.668, "right", "center"),
    },
}
LAYOUTS["v30"] = {
    **LAYOUTS["v29"],
    "name": "arial-ggplot-labels",
    "fontsize": 8.35,
    "legend_fontsize": 7.15,
    "label_fontfamily": "Arial",
    "label_fontweight": "normal",
    "label_color": "#000000",
    "label_positions": {
        **LAYOUTS["v29"]["label_positions"],
        "thyroid carcinoma": (0.510, 0.804, "left", "center"),
        "hashimoto's thyroiditis": (0.654, 0.807, "left", "center"),
        "obesity": (0.506, 0.661, "left", "center"),
        "atrial fibrillation": (0.657, 0.633, "left", "center"),
        "hyperthyroidism": (0.666, 0.609, "left", "center"),
        "peripheral vascular disease": (0.666, 0.587, "left", "center"),
        "late-onset alzheimer's disease": (0.666, 0.562, "left", "center"),
        "dupuytren contracture": (0.666, 0.680, "left", "center"),
        "gout": (0.618, 0.668, "right", "center"),
    },
}
LAYOUTS["v31"] = {
    **LAYOUTS["v30"],
    "name": "nature-extended-data-font",
    "fontsize": 8.15,
    "label_fontfamily": "Arial",
    "label_fontweight": "medium",
    "label_color": "#000000",
    "global_fontfamily": "Arial",
    "legend_fontsize": 7.15,
}
LAYOUTS["v32"] = {
    **LAYOUTS["v31"],
    "name": "disease-labels-plus2pt",
    "fontsize": 10.15,
}
LAYOUTS["v33"] = {
    **LAYOUTS["v32"],
    "name": "separated-gout-dupuytren-labels",
    "label_positions": {
        **LAYOUTS["v32"]["label_positions"],
        "gout": (0.601, 0.667, "right", "center"),
        "dupuytren contracture": (0.672, 0.680, "left", "center"),
    },
}
LAYOUTS["v34"] = {
    **LAYOUTS["v33"],
    "name": "staggered-right-labels",
    "label_positions": {
        **LAYOUTS["v33"]["label_positions"],
        "dupuytren contracture": (0.625, 0.698, "center", "center"),
        "atrial fibrillation": (0.650, 0.635, "left", "center"),
        "hyperthyroidism": (0.680, 0.614, "left", "center"),
        "peripheral vascular disease": (0.660, 0.590, "left", "center"),
        "late-onset alzheimer's disease": (0.682, 0.562, "left", "center"),
    },
}
LAYOUTS["v35"] = {
    **LAYOUTS["v34"],
    "name": "open-space-label-layout",
    "label_positions": {
        **LAYOUTS["v34"]["label_positions"],
        "obesity": (0.512, 0.675, "left", "center"),
        "gout": (0.594, 0.688, "right", "center"),
        "dupuytren contracture": (0.624, 0.718, "center", "center"),
        "atrial fibrillation": (0.646, 0.639, "left", "center"),
        "hyperthyroidism": (0.674, 0.618, "left", "center"),
        "peripheral vascular disease": (0.642, 0.592, "left", "center"),
        "late-onset alzheimer's disease": (0.676, 0.557, "left", "center"),
    },
}

LAYOUTS["v36"] = {
    **LAYOUTS["v35"],
    "name": "open-space-label-layout-refined",
    "label_positions": {
        **LAYOUTS["v35"]["label_positions"],
        "obesity": (0.510, 0.682, "left", "center"),
        "gout": (0.585, 0.700, "right", "center"),
        "dupuytren contracture": (0.602, 0.738, "center", "center"),
        "atrial fibrillation": (0.650, 0.646, "left", "center"),
        "hyperthyroidism": (0.692, 0.623, "left", "center"),
        "peripheral vascular disease": (0.640, 0.586, "left", "center"),
        "late-onset alzheimer's disease": (0.686, 0.552, "left", "center"),
    },
}

LAYOUTS["v37"] = {
    **LAYOUTS["v36"],
    "name": "balanced-labels-thicker-callouts",
    "legend_fontsize": 9.15,
    "legend_markersize": 6.2,
    "legend_rect": [0.045, 0.025, 0.91, 0.255],
    "arrow_lw": 0.82,
    "arrow_shrinkA": 1,
    "arrow_shrinkB": 0.4,
    "label_positions": {
        **LAYOUTS["v36"]["label_positions"],
        "obesity": (0.525, 0.675, "center", "center"),
        "gout": (0.562, 0.705, "center", "center"),
        "dupuytren contracture": (0.590, 0.735, "center", "center"),
        "atrial fibrillation": (0.654, 0.652, "left", "center"),
        "hyperthyroidism": (0.704, 0.626, "left", "center"),
        "peripheral vascular disease": (0.532, 0.610, "left", "center"),
        "late-onset alzheimer's disease": (0.686, 0.552, "left", "center"),
    },
}

LAYOUTS["v38"] = {
    **LAYOUTS["v37"],
    "name": "balanced-left-column-callouts",
    "legend_rect": [0.045, 0.025, 0.91, 0.250],
    "label_positions": {
        **LAYOUTS["v37"]["label_positions"],
        "obesity": (0.520, 0.680, "left", "center"),
        "gout": (0.520, 0.715, "left", "center"),
        "dupuytren contracture": (0.515, 0.745, "left", "center"),
        "atrial fibrillation": (0.656, 0.652, "left", "center"),
        "hyperthyroidism": (0.704, 0.626, "left", "center"),
        "peripheral vascular disease": (0.640, 0.590, "left", "center"),
        "late-onset alzheimer's disease": (0.686, 0.554, "left", "center"),
    },
}

LAYOUTS["v39"] = {
    **LAYOUTS["v38"],
    "name": "diagonal-callout-balance",
    "arrow_lw": 0.95,
    "arrow_shrinkA": 0.8,
    "arrow_shrinkB": 0.0,
    "label_positions": {
        **LAYOUTS["v38"]["label_positions"],
        "obesity": (0.512, 0.676, "left", "center"),
        "gout": (0.528, 0.708, "left", "center"),
        "dupuytren contracture": (0.606, 0.748, "center", "center"),
        "atrial fibrillation": (0.646, 0.656, "left", "center"),
        "hyperthyroidism": (0.708, 0.626, "left", "center"),
        "peripheral vascular disease": (0.624, 0.588, "left", "center"),
        "late-onset alzheimer's disease": (0.670, 0.550, "left", "center"),
    },
}

LAYOUTS["v40"] = {
    **LAYOUTS["v39"],
    "name": "final-balanced-callouts",
    "label_positions": {
        **LAYOUTS["v39"]["label_positions"],
        "obesity": (0.512, 0.676, "left", "center"),
        "gout": (0.522, 0.715, "left", "center"),
        "dupuytren contracture": (0.600, 0.760, "center", "center"),
        "atrial fibrillation": (0.670, 0.654, "left", "center"),
        "hyperthyroidism": (0.714, 0.624, "left", "center"),
        "peripheral vascular disease": (0.620, 0.586, "left", "center"),
        "late-onset alzheimer's disease": (0.656, 0.548, "left", "center"),
    },
}

LAYOUTS["v41"] = {
    **LAYOUTS["v40"],
    "name": "wide-panel-larger-points",
    "aspect": "auto",
    "ax_rect": [0.080, 0.435, 0.875, 0.505],
    "legend_rect": [0.045, 0.025, 0.91, 0.250],
    "point_size": 42,
    "point_linewidth": 1.05,
    "label_positions": {
        **LAYOUTS["v40"]["label_positions"],
        "obesity": (0.510, 0.676, "left", "center"),
        "gout": (0.520, 0.715, "left", "center"),
        "dupuytren contracture": (0.590, 0.760, "center", "center"),
        "atrial fibrillation": (0.662, 0.656, "left", "center"),
        "hyperthyroidism": (0.690, 0.625, "left", "center"),
        "peripheral vascular disease": (0.616, 0.586, "left", "center"),
        "late-onset alzheimer's disease": (0.648, 0.548, "left", "center"),
    },
}

LAYOUTS["v42"] = {
    **LAYOUTS["v40"],
    "name": "proportional-square-panel",
    "figsize": (10.0, 8.8),
    "ax_rect": [0.210, 0.380, 0.555, 0.595],
    "legend_rect": [0.135, 0.035, 0.730, 0.260],
    "legend_fontsize": 9.15,
    "legend_markersize": 6.2,
    "point_size": 46,
    "point_linewidth": 1.05,
    "arrow_lw": 0.95,
    "arrow_shrinkA": 0.8,
    "arrow_shrinkB": 0.0,
    "label_positions": {
        **LAYOUTS["v40"]["label_positions"],
        "obesity": (0.512, 0.676, "left", "center"),
        "gout": (0.522, 0.715, "left", "center"),
        "dupuytren contracture": (0.600, 0.760, "center", "center"),
        "atrial fibrillation": (0.670, 0.654, "left", "center"),
        "hyperthyroidism": (0.714, 0.624, "left", "center"),
        "peripheral vascular disease": (0.620, 0.586, "left", "center"),
        "late-onset alzheimer's disease": (0.656, 0.548, "left", "center"),
    },
}

LAYOUTS["v43"] = {
    **LAYOUTS["v42"],
    "name": "proportional-square-panel-compact-legend",
    "legend_rect": [0.140, 0.040, 0.720, 0.230],
    "legend_columnspacing": 0.95,
    "legend_labelspacing": 0.18,
    "label_positions": {
        **LAYOUTS["v42"]["label_positions"],
        "dupuytren contracture": (0.596, 0.763, "center", "center"),
        "atrial fibrillation": (0.674, 0.654, "left", "center"),
        "hyperthyroidism": (0.706, 0.623, "left", "center"),
        "peripheral vascular disease": (0.615, 0.584, "left", "center"),
        "late-onset alzheimer's disease": (0.648, 0.548, "left", "center"),
    },
}

LAYOUTS["v44"] = {
    **LAYOUTS["v43"],
    "name": "compact-proportional-proposal",
    "figsize": (8.4, 7.4),
    "point_size": 46,
    "point_linewidth": 1.05,
    "legend_fontsize": 9.15,
    "legend_markersize": 6.2,
}

LAYOUTS["v45"] = {
    **LAYOUTS["v44"],
    "name": "compact-proposal-full-legend-short-labels",
    "figsize": (7.2, 6.35),
    "legend_rect": [0.000, 0.035, 1.000, 0.245],
    "legend_columnspacing": 0.78,
    "legend_handletextpad": 0.35,
    "legend_labelspacing": 0.18,
}

LAYOUTS["v46"] = {
    **LAYOUTS["v45"],
    "name": "compact-less-side-space-no-overlap",
    "figsize": (6.4, 6.2),
    "ax_rect": [0.195, 0.380, 0.610, 0.590],
    "legend_rect": [0.000, 0.020, 1.000, 0.215],
    "x_labelpad": 10,
    "y_labelpad": 11,
}

LAYOUTS["v47"] = {
    **LAYOUTS["v46"],
    "name": "reduced-margins-full-bleed-legend",
    "figsize": (6.05, 6.05),
    "ax_rect": [0.185, 0.385, 0.635, 0.590],
    "legend_rect": [-0.070, -0.015, 1.140, 0.245],
}

LAYOUTS["v48"] = {
    **LAYOUTS["v47"],
    "name": "tighter-sides-full-bleed-legend",
    "figsize": (6.00, 6.35),
    "ax_rect": [0.170, 0.425, 0.675, 0.545],
    "legend_rect": [-0.090, -0.018, 1.180, 0.285],
    "fontsize": 12.15,
    "legend_fontsize": 11.15,
    "axis_labelsize": 13.4,
    "tick_labelsize": 12.5,
}

WITHIN_AOU_FILTERED_OVERRIDES = {
    "xlim": (0.50, 0.70),
    "ylim": (0.50, 0.70),
    "diag_start": 0.50,
    "diag_end": 0.70,
    "arrow_shrinkA": 10.0,
    "arrow_shrinkB": 0.6,
    "label_positions": {
        "dupuytren contracture": (0.659, 0.690, "left", "center"),
        "gout": (0.575, 0.686, "left", "center"),
        "obesity": (0.505, 0.665, "left", "center"),
        "atrial fibrillation": (0.602, 0.640, "right", "center"),
        "angina pectoris": (0.505, 0.584, "left", "center"),
    },
    "point_offsets": {
        "abdominal aortic aneurysm": (-4.2, -2.0),
        "atrial fibrillation": (4.2, 2.0),
        "kidney failure": (-1.9, 1.2),
        "retinal detachment": (-3.0, -2.2),
        "breast carcinoma": (-1.5, 1.0),
        "glaucoma": (1.5, -1.0),
        "dupuytren contracture": (1.4, 1.0),
        "gout": (-1.4, -1.0),
        "myocardial infarction": (-1.3, 1.0),
        "uterine cancer": (1.3, -1.0),
        "angina pectoris": (-1.3, 1.0),
        "hip osteoarthritis": (1.3, -1.0),
        "melanoma": (0.4, 0.3),
        "heart failure": (-2.2, 1.6),
        "squamous cell carcinoma": (3.5, 1.5),
    },
}

CROSS_LAYOUT_OVERRIDES = {
    "figsize": (6.70, 7.05),
    "ax_rect": [0.170, 0.420, 0.700, 0.545],
    "legend_rect": [-0.095, -0.018, 1.190, 0.315],
    "xlim": (0.50, 0.70),
    "ylim": (0.50, 0.70),
    "diag_start": 0.50,
    "diag_end": 0.70,
    "arrow_shrinkA": 10.0,
    "arrow_shrinkB": 0.6,
    "arrow_lw": 0.90,
    "legend_ncol": 3,
    "legend_fontsize": 8.4,
    "legend_markersize": 5.1,
    "legend_columnspacing": 0.90,
    "legend_labelspacing": 0.20,
    "fontsize": 8.7,
    "axis_labelsize": 13.0,
    "tick_labelsize": 11.2,
    "label_positions": {
        "simple and mucopurulent chronic bronchitis": (0.505, 0.646, "left", "center"),
        "chronic gout": (0.634, 0.686, "left", "center"),
        "cholecystitis": (0.585, 0.556, "left", "center"),
        "persistent mood [affective] disorders": (0.545, 0.510, "left", "center"),
        "umbilical hernia": (0.595, 0.635, "right", "center"),
    },
    "point_offsets": {
        "chronic gout": (-1.8, 1.3),
        "disorders of purine and pyrimidine metabolism": (1.8, -1.3),
        "ventral hernia": (-1.6, 1.0),
        "umbilical hernia": (1.6, -1.0),
        "benign neoplasm of breast": (-1.5, 0.8),
        "specific personality disorders": (1.4, -0.8),
    },
}

WITHIN82_LAYOUT_OVERRIDES = {
    "figsize": (6.70, 7.05),
    "ax_rect": [0.175, 0.420, 0.690, 0.550],
    "legend_rect": [-0.085, -0.018, 1.170, 0.315],
    "xlim": (0.50, 0.70),
    "ylim": (0.50, 0.70),
    "diag_start": 0.50,
    "diag_end": 0.70,
    "arrow_shrinkA": 2.0,
    "arrow_shrinkB": 0.6,
    "arrow_lw": 0.90,
    "legend_ncol": 3,
    "legend_fontsize": 8.9,
    "legend_markersize": 5.3,
    "fontsize": 9.4,
    "auto_adjust": False,
    "axis_labelsize": 13.0,
    "tick_labelsize": 11.2,
    "label_positions": {
        "ulcerative colitis": (0.548, 0.693, "left", "center"),
        "dupuytren contracture": (0.690, 0.695, "right", "center"),
        "obesity": (0.505, 0.665, "left", "center"),
        "abdominal aortic aneurysm": (0.505, 0.636, "left", "center"),
        "myocardial infarction": (0.505, 0.612, "left", "center"),
        "late-onset alzheimer's disease": (0.552, 0.526, "left", "center"),
        "type 2 diabetes mellitus": (0.608, 0.658, "right", "center"),
        "coronary artery disease": (0.613, 0.596, "left", "center"),
    },
    "point_offsets": {
        "testicular carcinoma": (1.2, 0.8),
        "coronary artery disease": (-1.4, 1.0),
        "type 2 diabetes mellitus": (1.4, -1.0),
        "myocardial infarction": (-1.0, 1.2),
        "angina pectoris": (1.0, -1.2),
        "kidney failure": (-1.1, 1.0),
        "dementia": (1.1, -1.0),
        "pulmonary fibrosis": (-1.0, 1.0),
        "prostate cancer": (1.0, -1.0),
        "lupus erythematosus": (-1.1, 1.1),
        "osteoporosis": (1.2, -1.0),
        "ovarian neoplasm": (-1.2, -1.0),
        "gout": (1.0, 1.0),
        "glaucoma": (-1.0, -1.0),
    },
}


def soften(hex_color: str) -> tuple[float, float, float]:
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    s = min(0.42, s * 0.72)
    l = 0.58 if l < 0.58 else min(0.70, l)
    return colorsys.hls_to_rgb(h, l, s)


def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))


def title_case_label(text: str) -> str:
    replacements = {
        "late-onset alzheimer's disease": "Late-onset Alzheimer's disease",
    }
    return replacements.get(text.lower(), text.capitalize())


def build_within82_source_data() -> None:
    baseline = json.loads(WITHIN82_BASELINE_SUMMARY.read_text(encoding="utf-8"))
    agent = json.loads(WITHIN82_AGENT_SUMMARY.read_text(encoding="utf-8"))
    baseline_rows = {row["ontology"]: row for row in baseline["per_disease"]}
    agent_rows = {row["ontology"]: row for row in agent["per_disease"]}
    rows: list[dict[str, object]] = []
    for ontology in sorted(set(baseline_rows) & set(agent_rows)):
        base_row = baseline_rows[ontology]
        agent_row = agent_rows[ontology]
        baseline_pgs = base_row.get("modal_recommendation")
        agent_pgs = agent_row.get("modal_recommendation")
        baseline_auc = (base_row.get("benchmark_auc_by_id") or {}).get(baseline_pgs)
        agent_auc = (agent_row.get("benchmark_auc_by_id") or {}).get(agent_pgs)
        if baseline_auc is None or agent_auc is None:
            continue
        disease_key = ontology.lower()
        rows.append(
            {
                "disease": disease_key,
                "baseline_auc": float(baseline_auc),
                "prs_agent_auc": float(agent_auc),
                "delta_auc": float(agent_auc) - float(baseline_auc),
                "baseline_pgs_id": baseline_pgs,
                "prs_agent_pgs_id": agent_pgs,
                "baseline_rank": base_row.get("modal_recommendation_rank"),
                "prs_agent_rank": agent_row.get("modal_recommendation_rank"),
                "display_name": title_case_label(ontology),
                "color": PUBLICATION_COLORS.get(disease_key, "#777777"),
            }
        )
    pd.DataFrame(rows).to_csv(WITHIN82_DATA, index=False)


def build_cross_typea59_source_data() -> None:
    df = pd.read_csv(CROSS_TYPEA59_DETAIL)
    rows: list[dict[str, object]] = []
    for _, row in df.iterrows():
        disease_key = str(row["target_description"]).strip().lower()
        rows.append(
            {
                "target_id": row["target_id"],
                "input_type": row["input_type"],
                "disease": disease_key,
                "baseline_auc": float(row["selected_model_auc_baseline"]),
                "prs_agent_auc": float(row["selected_model_auc_prs_agent"]),
                "delta_auc": float(row["delta_selected_auc"]),
                "baseline_pgs_id": row["recommended_model_id_baseline"],
                "prs_agent_pgs_id": row["recommended_model_id_prs_agent"],
                "baseline_rank": row["selected_model_rank_baseline"],
                "prs_agent_rank": row["selected_model_rank_prs_agent"],
                "display_name": CROSS_LEGEND_LABELS.get(disease_key, title_case_label(disease_key)),
                "color": PUBLICATION_COLORS.get(disease_key, "#777777"),
            }
        )
    out = pd.DataFrame(rows)
    if len(out) != 59:
        raise RuntimeError(f"Expected 59 cross-trait rows, got {len(out)}")
    out.to_csv(CROSS_DATA, index=False)


def mode_assets(mode: str) -> tuple[Path, dict[str, str], dict[str, str], dict]:
    if mode == "within":
        return WITHIN_DATA, WITHIN_TOP_LABELS, WITHIN_LEGEND_LABELS, WITHIN_AOU_FILTERED_OVERRIDES
    if mode == "within82":
        build_within82_source_data()
        return WITHIN82_DATA, WITHIN82_TOP_LABELS, WITHIN82_LEGEND_LABELS, WITHIN82_LAYOUT_OVERRIDES
    if mode == "cross":
        build_cross_typea59_source_data()
        return CROSS_DATA, CROSS_TOP_LABELS, CROSS_LEGEND_LABELS, CROSS_LAYOUT_OVERRIDES
    raise ValueError(f"Unsupported mode: {mode}")


def load_data(theta: float, mode: str) -> pd.DataFrame:
    data_path, _, _, _ = mode_assets(mode)
    df = pd.read_csv(data_path)
    df["disease_key"] = df["disease"].str.lower()
    if mode == "within":
        df = df[~df["disease_key"].isin(WITHIN_EXCLUDED_AFTER_AOU_FILTER)].copy()
    if mode == "within82":
        df = df[~df["disease_key"].isin(WITHIN82_EXCLUDED_DISEASES)].copy()
        keep_extra = df["disease_key"].isin(WITHIN82_NEAR_ZERO_DISEASES | WITHIN82_NEGATIVE_DISEASES)
        keep_gain = df["delta_auc"] >= theta
        in_axis_window = (
            df["baseline_auc"].between(0.50, 0.70)
            & df["prs_agent_auc"].between(0.50, 0.70)
        )
        df = df[(keep_gain | keep_extra) & in_axis_window].copy()
        df = df.sort_values("display_name")
    elif mode == "cross":
        df = df[~df["disease_key"].isin(CROSS_EXCLUDED_DISEASES)].copy()
        keep_extra = df["disease_key"].isin(CROSS_NEAR_ZERO_DISEASES | CROSS_NEGATIVE_DISEASES)
        keep_gain = df["delta_auc"] >= theta
        in_axis_window = (
            df["baseline_auc"].between(0.50, 0.70)
            & df["prs_agent_auc"].between(0.50, 0.70)
        )
        df = df[(keep_gain | keep_extra) & in_axis_window].copy()
        df = df.sort_values("display_name")
    else:
        df = df[df["delta_auc"] >= theta].copy()
    if mode == "within":
        df = df.sort_values("display_name")
    df["plot_color"] = [
        hex_to_rgb(PUBLICATION_COLORS[key]) if key in PUBLICATION_COLORS else soften(color)
        for key, color in zip(df["disease_key"], df["color"])
    ]
    return df


def setup_axes(fig: plt.Figure, cfg: dict) -> plt.Axes:
    ax = fig.add_axes(cfg["ax_rect"])
    ax.set_xlim(*cfg.get("xlim", (0.50, 0.82)))
    ax.set_ylim(*cfg.get("ylim", (0.50, 0.82)))
    ax.set_aspect(cfg.get("aspect", "equal"), adjustable="box")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(0.10))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.10))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(0.025))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.025))
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.grid(True, which="major", color="#d9dde1", linewidth=1.35, zorder=0)
    ax.grid(True, which="minor", color="#eceeef", linewidth=0.72, zorder=0)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_linewidth(1.8)
        ax.spines[spine].set_color("black")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.tick_params(
        axis="both",
        which="major",
        direction="out",
        width=1.6,
        length=8,
        labelsize=cfg.get("tick_labelsize", 10.5),
        pad=8,
    )
    ax.tick_params(axis="both", which="minor", direction="out", width=0.8, length=4)
    labelsize = cfg.get("axis_labelsize", 12.4)
    ax.set_xlabel(
        "Baseline LLM selected-model AUC",
        fontsize=labelsize,
        fontweight="bold",
        labelpad=cfg.get("x_labelpad", 13),
    )
    ax.set_ylabel(
        "PRS Agent selected-model AUC",
        fontsize=labelsize,
        fontweight="bold",
        labelpad=cfg.get("y_labelpad", 14),
    )
    return ax


def add_legend(fig: plt.Figure, df: pd.DataFrame, cfg: dict, legend_labels: dict[str, str]) -> None:
    x, y, w, h = cfg["legend_rect"]
    fig.add_artist(
        Rectangle(
            (x, y),
            w,
            h,
            transform=fig.transFigure,
            facecolor="#e8ecef",
            edgecolor="#e8ecef",
            zorder=0,
        )
    )
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markerfacecolor=row.plot_color,
            markeredgecolor="none",
            markersize=cfg.get("legend_markersize", 6.8),
            label=(
                f"{row.target_id} {legend_labels.get(row.disease_key, row.display_name)}"
                if cfg.get("legend_prefix_icd", False)
                else legend_labels.get(row.disease_key, row.display_name)
            ),
        )
        for row in df.itertuples()
    ]
    fig.legend(
        handles=handles,
        loc="center",
        bbox_to_anchor=(x + w / 2, y + h / 2),
        ncol=cfg.get("legend_ncol", 3),
        frameon=False,
        fontsize=cfg.get("legend_fontsize", 8.2),
        handletextpad=cfg.get("legend_handletextpad", 0.45),
        columnspacing=cfg.get("legend_columnspacing", 1.15),
        labelspacing=cfg.get("legend_labelspacing", 0.25),
        borderaxespad=0.0,
    )


def draw_plot(
    df: pd.DataFrame,
    cfg: dict,
    outstem: str,
    *,
    top_labels: dict[str, str],
    legend_labels: dict[str, str],
) -> tuple[int, int]:
    plt.rcParams.update(
        {
            "font.family": cfg.get("global_fontfamily", "Arial"),
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "text.antialiased": True,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    fig = plt.figure(figsize=cfg["figsize"], facecolor="white")
    if cfg.get("show_title", True):
        fig.suptitle(
            "PRS Agent selected-model AUC vs. LLM baseline",
            x=0.50,
            y=0.962,
            fontsize=cfg.get("title_fontsize", 15.2),
            fontweight="bold",
        )
    ax = setup_axes(fig, cfg)
    diag_start = cfg.get("diag_start", 0.50)
    diag_end = cfg.get("diag_end", 0.82)
    ax.plot([diag_start, diag_end], [diag_start, diag_end], linestyle=(0, (5, 5)), color="black", linewidth=1.65, zorder=1)

    point_offsets = cfg.get("point_offsets", {})
    if point_offsets:
        for row in df.itertuples():
            dx_pt, dy_pt = point_offsets.get(row.disease_key, (0.0, 0.0))
            transform = ax.transData + ScaledTranslation(dx_pt / 72, dy_pt / 72, fig.dpi_scale_trans)
            ax.scatter(
                [row.baseline_auc],
                [row.prs_agent_auc],
                s=cfg["point_size"],
                c=[row.plot_color],
                edgecolors="white",
                linewidths=cfg.get("point_linewidth", 0.8),
                alpha=cfg.get("point_alpha", 0.96),
                transform=transform,
                zorder=3,
            )
    else:
        ax.scatter(
            df["baseline_auc"],
            df["prs_agent_auc"],
            s=cfg["point_size"],
            c=list(df["plot_color"]),
            edgecolors="white",
            linewidths=cfg.get("point_linewidth", 0.8),
            alpha=cfg.get("point_alpha", 0.96),
            zorder=3,
        )

    label_texts = []
    target_x = []
    target_y = []
    for disease_key, text in top_labels.items():
        row = df[df["disease_key"] == disease_key]
        if row.empty:
            continue
        r = row.iloc[0]
        if disease_key not in cfg["label_positions"]:
            continue
        tx, ty, ha, va = cfg["label_positions"][disease_key]
        xycoords = "data"
        dx_pt, dy_pt = point_offsets.get(disease_key, (0.0, 0.0))
        if dx_pt or dy_pt:
            xycoords = ax.transData + ScaledTranslation(dx_pt / 72, dy_pt / 72, fig.dpi_scale_trans)
        if cfg.get("auto_adjust"):
            txt = ax.text(
                tx,
                ty,
                text,
                ha=ha,
                va=va,
                fontsize=cfg["fontsize"],
                fontfamily=cfg.get("label_fontfamily", "Helvetica"),
                fontweight=cfg.get("label_fontweight", "normal"),
                color=cfg.get("label_color", "#161616"),
                linespacing=0.90,
                zorder=4,
            )
            if cfg.get("label_path_effect", True):
                txt.set_path_effects([pe.withStroke(linewidth=2.0, foreground="white")])
            label_texts.append(txt)
            target_x.append(r["baseline_auc"])
            target_y.append(r["prs_agent_auc"])
        else:
            ann = ax.annotate(
                text,
                xy=(r["baseline_auc"], r["prs_agent_auc"]),
                xycoords=xycoords,
                xytext=(tx, ty),
                textcoords="data",
                ha=ha,
                va=va,
                fontsize=cfg["fontsize"],
                fontfamily=cfg.get("label_fontfamily", "Helvetica"),
                fontweight=cfg.get("label_fontweight", "normal"),
                color=cfg.get("label_color", "#161616"),
                linespacing=0.90,
                annotation_clip=False,
                arrowprops={
                    "arrowstyle": "-",
                    "color": "#595959",
                    "lw": cfg.get("arrow_lw", 0.52),
                    "shrinkA": cfg.get("arrow_shrinkA", 2),
                    "shrinkB": cfg.get("arrow_shrinkB", 3),
                    "connectionstyle": "arc3,rad=0",
                },
                zorder=4,
            )
            if cfg.get("label_path_effect", True):
                ann.set_path_effects([pe.withStroke(linewidth=2.1, foreground="white")])
            label_texts.append(ann)

    if cfg.get("auto_adjust") and adjust_text is not None:
        adjust_text(
            label_texts,
            x=df["baseline_auc"].tolist(),
            y=df["prs_agent_auc"].tolist(),
            target_x=target_x,
            target_y=target_y,
            ax=ax,
            ensure_inside_axes=True,
            prevent_crossings=True,
            force_text=(0.35, 0.55),
            force_static=(0.38, 0.42),
            force_pull=(0.015, 0.015),
            expand=(1.08, 1.22),
            max_move=(16, 16),
            iter_lim=450,
            min_arrow_len=3,
            arrowprops={"arrowstyle": "-", "color": "#595959", "lw": 0.50, "shrinkA": 2, "shrinkB": 3},
        )

    add_legend(fig, df, cfg, legend_labels)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    label_boxes = [t.get_window_extent(renderer).expanded(1.03, 1.10) for t in label_texts]
    label_overlaps = 0
    for i, box_i in enumerate(label_boxes):
        for box_j in label_boxes[i + 1 :]:
            if Bbox.overlaps(box_i, box_j):
                label_overlaps += 1
    point_overlaps = 0
    point_xy = []
    for row in df.itertuples():
        dx_pt, dy_pt = point_offsets.get(row.disease_key, (0.0, 0.0))
        if dx_pt or dy_pt:
            transform = ax.transData + ScaledTranslation(dx_pt / 72, dy_pt / 72, fig.dpi_scale_trans)
        else:
            transform = ax.transData
        point_xy.append(transform.transform((row.baseline_auc, row.prs_agent_auc)))
    for box in label_boxes:
        for x, y in point_xy:
            if box.contains(x, y):
                point_overlaps += 1
    for ext in ["png", "svg", "pdf"]:
        path = OUTDIR / f"{outstem}.{ext}"
        if ext == "png":
            fig.savefig(path, dpi=600, bbox_inches="tight", facecolor="white")
        else:
            fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return label_overlaps, point_overlaps


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theta", type=float, default=0.005)
    parser.add_argument("--versions", nargs="*", default=["v48"])
    parser.add_argument("--mode", choices=["within", "within82", "cross"], default="within")
    args = parser.parse_args()

    df = load_data(args.theta, args.mode)
    _, top_labels, legend_labels, layout_overrides = mode_assets(args.mode)
    print(f"filtered diseases: {len(df)}")
    for version in args.versions:
        cfg = {**LAYOUTS[version], **layout_overrides}
        theta_tag = f"theta{str(args.theta).replace('.', '')}"
        mode_tag = "" if args.mode == "within" else f"{args.mode}_"
        outstem = f"prs_agent_{mode_tag}auc_scatter_{theta_tag}_callout_top{len(top_labels)}_{version}_{cfg['name']}"
        label_overlaps, point_overlaps = draw_plot(
            df,
            cfg,
            outstem,
            top_labels=top_labels,
            legend_labels=legend_labels,
        )
        df.drop(columns=["plot_color"]).to_csv(OUTDIR / f"{outstem}_data.csv", index=False)
        print(f"{version}: label-overlaps={label_overlaps}, label-point-overlaps={point_overlaps}, stem={outstem}")


if __name__ == "__main__":
    main()
