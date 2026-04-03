"""
Phase 2 Cross-Trait Filtering for Retained Binary-Input Targets
===============================================================
2.1  Biological plausibility annotation (expanded rules + coverage audit)
2.2  Specificity-weighted ranking (improved tier logic)
2.3  Pair-level tiering (target trait -> cross trait)
2.4  Plausibility coverage audit
2.5  Cross-trait shortlist outputs
2.6  Target readiness summary (secondary / compatibility)

Operates on binary-input streams only: b2b, b2c.
"""

import csv
import json
import math
import sys
from collections import defaultdict, Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "runs"
B2B_DIR = BASE / "binary_to_binary"
B2C_DIR = BASE / "binary_to_continuous"
PHASE1_DIR = BASE.parent / "analysis" / "phase1"
OUTPUT_DIR = BASE.parent / "analysis" / "phase2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Keep binary-input cross-trait recommendations concise enough for manual review.
MAX_SHORTLIST_PER_TARGET_PER_STREAM = 5
MAX_PRINTED_ROWS_PER_TIER = 12

# Align Type A pair-level retention with the upstream cross_list rule:
# if there is no self AUC, a shortlisted cross trait must itself be strong enough.
TYPE_A_MIN_PAIR_CROSS_AUC = 0.55

# Remove stale continuous-input Phase 2 outputs so the directory reflects the
# current binary-input-only scope.
for stale_pattern in ("c2b_*.csv", "c2c_*.csv"):
    for stale_path in OUTPUT_DIR.glob(stale_pattern):
        stale_path.unlink()

# Import trait_mapping for ready-for-transfer output
TRANSFER_DIR = Path(__file__).resolve().parent.parent.parent / "transfer"
sys.path.insert(0, str(TRANSFER_DIR / "configs"))
try:
    from trait_mapping import CROSS_LIST_TO_GWAS_ATLAS
    HAS_TRAIT_MAPPING = True
    print(f"Loaded trait_mapping: {sum(1 for v in CROSS_LIST_TO_GWAS_ATLAS.values() if v)} mapped, "
          f"{sum(1 for v in CROSS_LIST_TO_GWAS_ATLAS.values() if not v)} unmapped")
except ImportError:
    HAS_TRAIT_MAPPING = False
    CROSS_LIST_TO_GWAS_ATLAS = {}
    print("[WARN] trait_mapping.py not found — ready-for-transfer output will be skipped")


# ═══════════════════════════════════════════════════════════════════════════════
# Biological system classification
# ═══════════════════════════════════════════════════════════════════════════════

# Map ICD root code → biological system
# Extended: covers all ICD codes appearing in cross-list and trait_mapping
ICD_SYSTEM = {
    # Neoplasms
    "C34": "neoplasm_lung", "C43": "neoplasm_skin", "C44": "neoplasm_skin",
    "C54": "neoplasm_gynecologic", "C56": "neoplasm_gynecologic",
    "C61": "neoplasm_prostate", "C64": "neoplasm_renal",
    "C67": "neoplasm_urologic", "C85": "neoplasm_hematologic",
    "D04": "neoplasm_skin", "D25": "neoplasm_gynecologic", "D26": "neoplasm_gynecologic",
    # Cardiovascular
    "I10": "cardiovascular_hypertension",
    "I20": "cardiovascular_coronary", "I21": "cardiovascular_coronary",
    "I24": "cardiovascular_coronary", "I25": "cardiovascular_coronary",
    "I27": "cardiovascular_pulmonary", "I42": "cardiovascular",
    "I48": "cardiovascular_arrhythmia", "I49": "cardiovascular_arrhythmia",
    "I50": "cardiovascular_heartfailure",
    "I70": "cardiovascular_peripheral", "I71": "cardiovascular",
    "I83": "cardiovascular_venous",
    # Metabolic / Endocrine
    "E05": "endocrine_thyroid", "E06": "endocrine_thyroid",
    "E66": "metabolic_obesity", "E83": "metabolic_mineral", "E88": "metabolic",
    # Mental / Behavioral
    "F03": "neuropsych_dementia", "F10": "mental_substance", "F17": "mental_substance",
    "F20": "mental_psychotic", "F31": "mental_mood", "F32": "mental_mood",
    "F41": "mental_anxiety", "F43": "mental_stress", "F90": "mental_neurodevelopmental",
    # Neurological
    "G20": "neurological_movement", "G30": "neuropsych_dementia",
    "G40": "neurological_epilepsy", "G47": "neurological_sleep",
    "G58": "neurological_peripheral",
    # Respiratory
    "J30": "respiratory_allergic", "J33": "respiratory_upper",
    "J43": "respiratory_obstructive", "J44": "respiratory_obstructive",
    "J45": "respiratory_allergic",
    # Musculoskeletal
    "M05": "musculoskeletal_autoimmune", "M06": "musculoskeletal_autoimmune",
    "M10": "musculoskeletal_metabolic", "M19": "musculoskeletal",
    "M34": "musculoskeletal_autoimmune", "M35": "musculoskeletal_autoimmune",
    "M36": "musculoskeletal_autoimmune",
    "M45": "musculoskeletal_autoimmune", "M47": "musculoskeletal",
    "M81": "musculoskeletal_bone", "M84": "musculoskeletal_bone",
    "M93": "musculoskeletal_bone",
    # Skin
    "L03": "skin_infectious", "L28": "skin_autoimmune", "L40": "skin_autoimmune",
    "L55": "skin", "L82": "skin",
    # Genitourinary
    "N02": "renal", "N04": "renal", "N18": "renal",
    "N40": "genitourinary_prostate", "N41": "genitourinary_prostate",
    # Hematologic
    "D64": "hematologic_rbc", "D68": "hematologic_coagulation",
    # Infectious
    "B02": "infectious_viral", "B07": "infectious_viral",
    # Congenital
    "Q74": "congenital_musculoskeletal",
    # Injury
    "S52": "musculoskeletal_bone",
    # Symptoms / Signs
    "R51": "neurological_pain", "R55": "cardiovascular_syncope",
    "R94": "cardiovascular",
    # Eye
    "H20": "autoimmune_eye", "H33": "ophthalmologic",
    # Adrenal
    "E27": "endocrine_adrenal",
}

# Keyword → system mapping for output disease/ontology names
# Order matters: more specific keywords first
KEYWORD_SYSTEM = [
    # Neoplasm
    (["endometrial cancer", "uterine cancer", "uterine carcinoma", "uterine corpus"], "neoplasm_gynecologic"),
    (["ovarian"], "neoplasm_gynecologic"),
    (["uterine benign neoplasm", "uterine fibroid"], "neoplasm_gynecologic"),
    (["prostate cancer", "prostate carcinoma", "prostate disease"], "neoplasm_prostate"),
    (["melanoma"], "neoplasm_skin"),
    (["skin cancer", "skin carcinoma", "basal cell", "squamous cell carcinoma"], "neoplasm_skin"),
    (["lung cancer", "lung carcinoma", "lung adenocarcinoma"], "neoplasm_lung"),
    (["breast carcinoma", "breast cancer"], "neoplasm_breast"),
    (["thyroid carcinoma"], "neoplasm_thyroid"),
    (["colorectal cancer", "colon cancer"], "neoplasm_gi"),
    (["renal cell", "kidney cancer"], "neoplasm_renal"),
    (["bladder cancer"], "neoplasm_urologic"),
    (["lymphoma", "leukemia"], "neoplasm_hematologic"),
    (["cancer", "carcinoma", "neoplasm", "tumor"], "neoplasm_other"),
    # Cardiovascular
    (["coronary artery disease", "coronary atherosclerosis"], "cardiovascular_coronary"),
    (["myocardial infarction", "heart attack"], "cardiovascular_coronary"),
    (["angina"], "cardiovascular_coronary"),
    (["heart failure"], "cardiovascular_heartfailure"),
    (["heart disease", "cardiomyopathy"], "cardiovascular"),
    (["aortic aneurysm", "aortic dissection"], "cardiovascular"),
    (["atrial fibrillation", "atrial flutter", "arrhythmia", "brugada"], "cardiovascular_arrhythmia"),
    (["peripheral arterial", "peripheral vascular", "intermittent claudication"], "cardiovascular_peripheral"),
    (["hypertension", "blood pressure", "systolic", "diastolic"], "cardiovascular_hypertension"),
    (["pulmonary embolism", "venous thromboembolism", "phlebitis", "deep vein"], "cardiovascular_venous"),
    (["stroke", "cerebrovascular", "cerebral infarction"], "cardiovascular_cerebrovascular"),
    (["syncope"], "cardiovascular_syncope"),
    # Metabolic
    (["obesity", "overnutrition", "body mass index", "body weight", "waist circumference",
      "waist-hip ratio"], "metabolic_obesity"),
    (["type 2 diabetes", "type ii diabetes", "t2d"], "metabolic_diabetes"),
    (["diabetes", "hba1c", "glucose", "insulin resistance"], "metabolic_diabetes"),
    (["cholesterol", "lipoprotein", "triglyceride", "lipid", "apolipoprotein"], "metabolic_lipid"),
    (["metabolic syndrome"], "metabolic"),
    (["uric acid", "urate"], "metabolic_urate"),
    (["iron", "ferritin", "transferrin"], "metabolic_mineral"),
    (["nodular goiter", "thyroid", "hyperthyroidism", "hypothyroidism", "thyrotoxicosis"], "endocrine_thyroid"),
    (["adrenal insufficiency", "cortisol", "addison"], "endocrine_adrenal"),
    # Mental / Behavioral
    (["depressive disorder", "major depressive", "depression"], "mental_mood"),
    (["bipolar"], "mental_mood"),
    (["schizophrenia", "psychosis"], "mental_psychotic"),
    (["anxiety"], "mental_anxiety"),
    (["post-traumatic stress", "ptsd"], "mental_stress"),
    (["attention deficit", "adhd"], "mental_neurodevelopmental"),
    (["autism"], "mental_neurodevelopmental"),
    (["insomnia", "sleep"], "neurological_sleep"),
    (["nicotine dependence", "smoking", "alcohol dependence", "substance"], "mental_substance"),
    # Neurological
    (["alzheimer", "dementia"], "neuropsych_dementia"),
    (["parkinson"], "neurological_movement"),
    (["epilepsy", "seizure"], "neurological_epilepsy"),
    (["headache", "migraine"], "neurological_pain"),
    (["neuropathy", "mononeuropathy", "polyneuropathy"], "neurological_peripheral"),
    # Respiratory
    (["asthma"], "respiratory_allergic"),
    (["copd", "chronic obstructive pulmonary"], "respiratory_obstructive"),
    (["emphysema"], "respiratory_obstructive"),
    (["nasal polyp", "sinusitis", "rhinitis"], "respiratory_upper"),
    (["allergic rhinitis", "hay fever"], "respiratory_allergic"),
    # Musculoskeletal
    (["rheumatoid arthritis", "scleroderma", "lupus", "connective tissue disease",
      "ankylosing spondylitis", "polymyalgia"], "musculoskeletal_autoimmune"),
    (["psoriatic arthritis"], "musculoskeletal_autoimmune"),
    (["arthritis", "osteoarthritis", "spondylosis"], "musculoskeletal"),
    (["osteoporosis", "bone fracture", "bone density", "bone mineral"], "musculoskeletal_bone"),
    (["gout"], "musculoskeletal_metabolic"),
    # Autoimmune / Allergic / Skin
    (["eczema", "dermatitis", "psoriasis", "atopic", "prurigo"], "skin_autoimmune"),
    (["allergic rhinitis"], "respiratory_allergic"),
    (["iritis", "uveitis"], "autoimmune_eye"),
    (["celiac", "inflammatory bowel", "crohn", "ulcerative colitis"], "gi_autoimmune"),
    (["type 1 diabetes", "type i diabetes", "t1d"], "autoimmune_endocrine"),
    # Renal
    (["nephrotic", "glomerulonephritis", "kidney disease", "kidney failure",
      "chronic kidney", "renal failure"], "renal"),
    (["nephrolithiasis", "kidney stone"], "renal"),
    # Skin
    (["cellulitis"], "skin_infectious"),
    (["epidermal", "seborrheic", "keratosis"], "skin"),
    (["sunburn"], "skin"),
    (["wart", "verruca"], "infectious_viral"),
    # Blood
    (["hemoglobin", "erythrocyte", "hematocrit", "red cell", "red blood cell",
      "mean corpuscular"], "hematologic_rbc"),
    (["eosinophil", "basophil", "lymphocyte", "neutrophil", "white blood",
      "monocyte"], "hematologic_wbc"),
    (["coagulation", "thrombocyte", "platelet", "fibrinogen"], "hematologic_coagulation"),
    (["anemia", "iron deficiency anemia"], "hematologic_rbc"),
    (["c-reactive protein", "crp", "interleukin", "inflammatory marker"], "inflammatory"),
    # Hormonal
    (["estradiol", "testosterone", "hormone", "sex hormone binding"], "endocrine_reproductive"),
    # Liver
    (["alanine aminotransferase", "aspartate aminotransferase", "gamma-glutamyl",
      "alkaline phosphatase", "bilirubin", "albumin", "liver"], "hepatic"),
    # Renal markers
    (["creatinine", "cystatin", "glomerular filtration", "egfr", "urea"], "renal_marker"),
    # Ophthalmologic
    (["retinal", "macular", "glaucoma", "cataract"], "ophthalmologic"),
    (["intraocular pressure"], "ophthalmologic"),
    # Infectious
    (["herpes zoster", "shingles"], "infectious_viral"),
    # Varicose
    (["varicose"], "cardiovascular_venous"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# Biological plausibility rules (EXPANDED)
# Format: (system_a, system_b, plausibility, reason)
# Rules are checked bidirectionally; prefix matching is also applied.
# ═══════════════════════════════════════════════════════════════════════════════

PLAUSIBILITY_RULES = [
    # ─── SAME system = high plausibility ────────────────────────────────
    ("SAME", "SAME", "high", "same disease family"),

    # ─── Cardiovascular internal ────────────────────────────────────────
    ("cardiovascular_coronary", "cardiovascular", "high", "same cardiovascular system"),
    ("cardiovascular_coronary", "cardiovascular_hypertension", "high", "hypertension → CAD pathway"),
    ("cardiovascular_coronary", "cardiovascular_heartfailure", "high", "CAD → heart failure pathway"),
    ("cardiovascular_coronary", "cardiovascular_peripheral", "high", "shared atherosclerosis"),
    ("cardiovascular_coronary", "cardiovascular_cerebrovascular", "high", "shared atherosclerosis/thrombosis"),
    ("cardiovascular_coronary", "cardiovascular_arrhythmia", "medium", "ischemic arrhythmia"),
    ("cardiovascular_hypertension", "cardiovascular_heartfailure", "high", "hypertension → HF pathway"),
    ("cardiovascular_hypertension", "cardiovascular_cerebrovascular", "high", "hypertension → stroke pathway"),
    ("cardiovascular_hypertension", "cardiovascular_arrhythmia", "medium", "hypertension → AF pathway"),
    ("cardiovascular_heartfailure", "cardiovascular_arrhythmia", "high", "HF ↔ AF bidirectional"),
    ("cardiovascular_pulmonary", "respiratory_obstructive", "high", "COPD → cor pulmonale pathway"),
    ("cardiovascular_venous", "hematologic_coagulation", "high", "coagulation → VTE pathway"),
    ("cardiovascular_arrhythmia", "cardiovascular_cerebrovascular", "high", "AF → cardioembolic stroke"),

    # ─── Cardiovascular ↔ Metabolic ────────────────────────────────────
    ("cardiovascular", "metabolic_obesity", "medium", "obesity → CVD risk factor"),
    ("cardiovascular_coronary", "metabolic_lipid", "high", "lipids → atherosclerosis pathway"),
    ("cardiovascular", "metabolic_lipid", "high", "lipids → CVD pathway"),
    ("cardiovascular_coronary", "metabolic_obesity", "medium", "obesity → CAD risk factor"),
    ("cardiovascular_coronary", "metabolic_diabetes", "high", "diabetes → accelerated atherosclerosis"),
    ("cardiovascular", "metabolic_diabetes", "medium", "diabetes → CVD pathway"),
    ("cardiovascular_hypertension", "metabolic_obesity", "high", "obesity → hypertension"),
    ("cardiovascular_hypertension", "metabolic_diabetes", "medium", "shared metabolic syndrome"),
    ("cardiovascular_hypertension", "renal", "high", "renal-hypertension axis"),
    ("cardiovascular_hypertension", "renal_marker", "high", "renal function ↔ BP"),
    ("cardiovascular_peripheral", "metabolic_diabetes", "high", "diabetes → PAD pathway"),
    ("cardiovascular_pulmonary", "metabolic_obesity", "medium", "obesity → cor pulmonale pathway"),
    ("cardiovascular_cerebrovascular", "metabolic_diabetes", "medium", "diabetes → stroke risk"),
    ("cardiovascular_cerebrovascular", "metabolic_lipid", "medium", "lipids → stroke via atherosclerosis"),

    # ─── Cardiovascular ↔ Other ────────────────────────────────────────
    ("cardiovascular_cerebrovascular", "neuropsych_dementia", "medium", "vascular dementia pathway"),
    ("cardiovascular_arrhythmia", "endocrine_thyroid", "high", "thyroid → AF pathway"),
    ("cardiovascular", "inflammatory", "medium", "CRP as CVD risk marker"),
    ("cardiovascular_coronary", "inflammatory", "medium", "inflammation in atherosclerosis"),

    # ─── Respiratory ───────────────────────────────────────────────────
    ("respiratory_obstructive", "respiratory_obstructive", "high", "same respiratory obstructive"),
    ("respiratory_upper", "respiratory_allergic", "high", "shared allergic/eosinophilic pathway"),
    ("respiratory_allergic", "skin_autoimmune", "high", "atopic march: asthma ↔ eczema"),
    ("respiratory_allergic", "hematologic_wbc", "high", "eosinophils in allergic disease"),
    ("respiratory_upper", "hematologic_wbc", "high", "eosinophils in nasal polyps"),
    ("respiratory_obstructive", "metabolic_obesity", "medium", "obesity worsens COPD"),
    ("respiratory_obstructive", "mental_substance", "medium", "smoking → COPD pathway"),

    # ─── Musculoskeletal / Autoimmune ──────────────────────────────────
    ("musculoskeletal_autoimmune", "musculoskeletal", "high", "related joint diseases"),
    ("musculoskeletal_autoimmune", "autoimmune_eye", "high", "HLA-B27 shared autoimmune"),
    ("musculoskeletal_autoimmune", "skin_autoimmune", "high", "psoriatic arthritis / shared autoimmune"),
    ("musculoskeletal_autoimmune", "gi_autoimmune", "high", "shared HLA / autoimmune pathway"),
    ("musculoskeletal_autoimmune", "inflammatory", "high", "CRP/inflammatory markers in RA/AS"),
    ("musculoskeletal_autoimmune", "autoimmune_endocrine", "medium", "shared autoimmune genetic risk"),
    ("musculoskeletal_autoimmune", "renal", "medium", "lupus nephritis / autoimmune renal"),
    ("musculoskeletal_bone", "musculoskeletal_bone", "high", "same bone metabolism"),
    ("musculoskeletal_bone", "endocrine_reproductive", "high", "estrogen → bone density pathway"),
    ("musculoskeletal_bone", "endocrine_thyroid", "medium", "thyroid → bone metabolism"),
    ("musculoskeletal_bone", "metabolic_mineral", "high", "mineral metabolism in bone health"),
    ("musculoskeletal_bone", "renal", "medium", "renal osteodystrophy / CKD-bone"),
    ("musculoskeletal_metabolic", "metabolic_urate", "high", "uric acid → gout pathway"),
    ("musculoskeletal_metabolic", "renal", "medium", "urate/gout → renal pathway"),

    # ─── Neoplasm ──────────────────────────────────────────────────────
    ("neoplasm_gynecologic", "endocrine_reproductive", "high", "hormonal pathway in gynecologic cancer"),
    ("neoplasm_gynecologic", "metabolic_obesity", "medium", "obesity → endometrial cancer risk"),
    ("neoplasm_skin", "neoplasm_skin", "high", "same skin neoplasm family"),
    ("neoplasm_prostate", "genitourinary_prostate", "high", "same prostate tissue"),
    ("neoplasm_prostate", "endocrine_reproductive", "medium", "testosterone in prostate cancer"),
    ("neoplasm_breast", "endocrine_reproductive", "high", "hormonal pathway in breast cancer"),

    # ─── Neuropsychiatric ──────────────────────────────────────────────
    ("neuropsych_dementia", "neuropsych_dementia", "high", "same dementia spectrum"),
    ("neuropsych_dementia", "neurological_movement", "medium", "shared neurodegeneration (Lewy body overlap)"),
    ("mental_mood", "mental_stress", "high", "shared stress/mood pathway"),
    ("mental_mood", "mental_anxiety", "high", "shared mood/anxiety pathway"),
    ("mental_mood", "mental_neurodevelopmental", "medium", "shared psychiatric genetic risk"),
    ("mental_mood", "mental_substance", "medium", "mood-substance comorbidity pathway"),
    ("mental_psychotic", "mental_mood", "medium", "shared psychiatric genetic risk (rg~0.3)"),
    ("mental_psychotic", "mental_neurodevelopmental", "medium", "shared neurodevelopmental genetic risk"),
    ("mental_anxiety", "mental_stress", "high", "shared anxiety/stress pathway"),
    ("mental_anxiety", "mental_substance", "medium", "anxiety-substance comorbidity"),
    ("mental_neurodevelopmental", "mental_substance", "medium", "ADHD → substance risk pathway"),
    ("mental_neurodevelopmental", "neurological_sleep", "medium", "ADHD ↔ sleep pathway"),
    ("neurological_sleep", "metabolic_obesity", "medium", "sleep apnea ↔ obesity"),
    ("neurological_sleep", "cardiovascular_arrhythmia", "medium", "sleep apnea → AF"),

    # ─── Metabolic internal ────────────────────────────────────────────
    ("metabolic", "metabolic_obesity", "high", "obesity → metabolic syndrome"),
    ("metabolic_obesity", "metabolic_diabetes", "high", "obesity → diabetes pathway"),
    ("metabolic_obesity", "metabolic_lipid", "high", "obesity → dyslipidemia"),
    ("metabolic_obesity", "hematologic_rbc", "medium", "obesity affects hematologic parameters"),
    ("metabolic_obesity", "hepatic", "medium", "obesity → NAFLD pathway"),
    ("metabolic_obesity", "inflammatory", "medium", "adiposity → chronic inflammation"),
    ("metabolic_diabetes", "renal", "high", "diabetic nephropathy"),
    ("metabolic_diabetes", "renal_marker", "high", "diabetic nephropathy → eGFR decline"),
    ("metabolic_diabetes", "metabolic_lipid", "high", "diabetic dyslipidemia"),
    ("metabolic_diabetes", "neurological_peripheral", "medium", "diabetic neuropathy"),
    ("metabolic_diabetes", "ophthalmologic", "medium", "diabetic retinopathy"),
    ("metabolic_diabetes", "hepatic", "medium", "diabetes → liver disease pathway"),
    ("metabolic_lipid", "hepatic", "medium", "lipid metabolism in liver"),
    ("metabolic", "cardiovascular_hypertension", "medium", "metabolic syndrome includes hypertension"),
    ("metabolic_mineral", "hematologic_rbc", "high", "iron → hemoglobin synthesis"),

    # ─── Renal ─────────────────────────────────────────────────────────
    ("renal", "cardiovascular", "medium", "CKD → CVD risk pathway"),
    ("renal", "cardiovascular_coronary", "medium", "CKD → accelerated atherosclerosis"),
    ("renal", "cardiovascular_heartfailure", "medium", "cardiorenal syndrome"),
    ("renal", "hematologic_rbc", "high", "EPO axis: kidney → erythropoiesis"),
    ("renal", "musculoskeletal_bone", "medium", "renal osteodystrophy / CKD-MBD"),
    ("renal", "metabolic_mineral", "medium", "renal mineral handling"),
    ("renal_marker", "renal", "high", "renal markers reflect kidney function"),
    ("renal_marker", "hematologic_rbc", "medium", "eGFR ↔ hemoglobin via EPO"),
    ("renal", "metabolic_obesity", "low", "weak: obesity confounding only"),
    ("renal", "respiratory_allergic", "low", "IgA nephropathy-asthma: weak link"),

    # ─── Skin ──────────────────────────────────────────────────────────
    ("skin_autoimmune", "gi_autoimmune", "medium", "shared autoimmune / Th17 pathway"),
    ("skin_autoimmune", "autoimmune_eye", "medium", "shared autoimmune pathway"),
    ("skin_autoimmune", "hematologic_wbc", "medium", "immune cells in skin autoimmunity"),
    ("skin_infectious", "metabolic_obesity", "medium", "obesity → cellulitis risk factor"),

    # ─── Hematologic ───────────────────────────────────────────────────
    ("hematologic_wbc", "inflammatory", "high", "WBC/inflammatory shared pathway"),
    ("hematologic_coagulation", "cardiovascular_coronary", "medium", "thrombosis in MI"),

    # ─── Endocrine ─────────────────────────────────────────────────────
    ("endocrine_thyroid", "metabolic_obesity", "medium", "thyroid ↔ metabolic rate"),
    ("endocrine_thyroid", "musculoskeletal_bone", "medium", "thyroid → bone metabolism"),
    ("endocrine_thyroid", "cardiovascular_arrhythmia", "high", "hyperthyroidism → AF"),
    ("endocrine_reproductive", "musculoskeletal_bone", "high", "sex hormones → bone density"),
    ("endocrine_reproductive", "metabolic_obesity", "medium", "hormones ↔ body composition"),

    # ─── Known non-specific / confounded (explicitly LOW) ──────────────
    ("neoplasm_gynecologic", "mental_mood", "low", "likely confounded via BMI/lifestyle"),
    ("neoplasm_gynecologic", "cardiovascular_hypertension", "low", "likely confounded via BMI"),
    ("neoplasm_gynecologic", "neurological_sleep", "low", "likely confounded via BMI"),
    ("neuropsych_dementia", "mental_mood", "low", "confounded: depression as prodrome, not causal genetic"),
    ("neuropsych_dementia", "hematologic_rbc", "low", "no direct genetic pathway"),
]


def classify_system_from_icd(icd_code):
    """Get biological system from ICD root code.
    Tries exact match first, then progressively shorter prefixes."""
    if icd_code in ICD_SYSTEM:
        return ICD_SYSTEM[icd_code]
    # Try shorter prefixes (e.g., "I219" → "I21" → "I2")
    for length in range(len(icd_code) - 1, 1, -1):
        prefix = icd_code[:length]
        if prefix in ICD_SYSTEM:
            return ICD_SYSTEM[prefix]
    return f"unknown_{icd_code}"


def classify_system_from_ontology(ontology_text):
    """Get biological system from output ontology/disease name using keywords."""
    text_lower = ontology_text.lower()
    for keywords, system in KEYWORD_SYSTEM:
        if any(kw in text_lower for kw in keywords):
            return system
    return "unknown"


def get_broad_system(system):
    """Get the broadest category."""
    return system.split("_")[0]


def assess_plausibility(input_system, output_system):
    """Assess biological plausibility of input→output pair."""
    # Same exact system
    if input_system == output_system:
        return "high", "identical disease system"

    # Same broad system (e.g., both cardiovascular_*)
    if (get_broad_system(input_system) == get_broad_system(output_system)
            and not input_system.startswith("unknown")
            and not output_system.startswith("unknown")):
        return "high", f"same broad system: {get_broad_system(input_system)}"

    # Check explicit rules (both directions)
    for sys_a, sys_b, plaus, reason in PLAUSIBILITY_RULES:
        if sys_a == "SAME":
            continue
        # Try exact match
        if input_system == sys_a and output_system == sys_b:
            return plaus, reason
        if input_system == sys_b and output_system == sys_a:
            return plaus, reason
        # Try prefix match
        if input_system.startswith(sys_a) and output_system.startswith(sys_b):
            return plaus, reason
        if input_system.startswith(sys_b) and output_system.startswith(sys_a):
            return plaus, reason

    # Default: if no rule matches, it's low plausibility
    return "low", f"no known pathway: {input_system} → {output_system}"


# ═══════════════════════════════════════════════════════════════════════════════
# Load Phase 1 specificity data (with graceful fallback)
# ═══════════════════════════════════════════════════════════════════════════════

def load_pgs_specificity(label):
    """Load PGS specificity scores from Phase 1."""
    path = PHASE1_DIR / f"1_1_pgs_specificity_{label}.csv"
    spec = {}
    if not path.exists():
        print(f"[WARN] Phase 1 specificity not found for {label}: {path}")
        return spec
    with open(path) as f:
        for r in csv.DictReader(f):
            spec[r["pgs_id"]] = float(r["specificity_score"])
    return spec


def load_output_hub(label):
    """Load output hub frequency from Phase 1."""
    path = PHASE1_DIR / f"1_2_output_hub_{label}.csv"
    hubs = {}
    if not path.exists():
        print(f"[WARN] Phase 1 hub data not found for {label}: {path}")
        return hubs
    with open(path) as f:
        for r in csv.DictReader(f):
            cross_trait = r.get("cross_trait") or r.get("output")
            n_targets_served = r.get("n_target_traits_served") or r.get("n_input_diseases_served")
            if cross_trait and n_targets_served:
                hubs[cross_trait] = int(n_targets_served)
    return hubs


def load_detail_rows(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def load_summary_cross_list_inputs(path, n_col="n_cross_models_beating_self"):
    with open(path) as f:
        return [r for r in csv.DictReader(f)
                if int(r[n_col]) > 0]


def load_binary_target_universe(stream_configs):
    """Load the fixed retained binary-input target universe from cross_list runs.

    Phase 2 should not delete retained targets from the report universe. Even if a
    target has no Tier 1/2 cross trait after filtering, it should still appear in
    the target-level summary with an empty shortlist.
    """
    target_meta = {}
    for label, cfg in stream_configs.items():
        summary_path = cfg["dir"] / "cross_list_summary.csv"
        if not summary_path.exists():
            continue
        for row in load_summary_cross_list_inputs(summary_path):
            target_id = row[cfg["input_id_col"]]
            meta = target_meta.setdefault(target_id, {
                "target_id": target_id,
                "target_trait": row.get("input_ontology", "")[:80],
                "input_type": row.get("input_type", ""),
                "has_self": row.get(cfg["has_self_col"], ""),
                "streams": set(),
            })
            if not meta["target_trait"]:
                meta["target_trait"] = row.get("input_ontology", "")[:80]
            if _parse_bool(row.get(cfg["has_self_col"], "")):
                meta["has_self"] = row.get(cfg["has_self_col"], "")
            if not meta["input_type"] and row.get("input_type"):
                meta["input_type"] = row["input_type"]
            meta["streams"].add(label)

    for meta in target_meta.values():
        meta["streams"] = ";".join(sorted(meta["streams"]))

    return target_meta


def _parse_bool(value):
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def _effective_improvement(row, improvement_col, metric_col, has_self_col):
    """Use the same downstream ranking logic for Type A and Type B.

    If self score exists, use the explicit improvement column.
    If self score is missing (Type A), fall back to the cross metric itself.
    """
    raw_improvement = str(row.get(improvement_col, "")).strip()
    if raw_improvement:
        return float(raw_improvement)
    if not _parse_bool(row.get(has_self_col, "")):
        raw_metric = str(row.get(metric_col, "")).strip()
        if raw_metric:
            return float(raw_metric)
    return None


def _passes_pair_retention_floor(row):
    """Additional pair-level retention guardrails beyond tiering.

    For Type A targets (no self AUC), keep only cross traits whose own best AUC
    clears the same absolute floor used by upstream cross_list entry logic.
    """
    if not _parse_bool(row.get("has_self", "")):
        metric = row.get("best_cross_metric", "")
        if metric in {"", None}:
            return False
        return float(metric) > TYPE_A_MIN_PAIR_CROSS_AUC
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# Unified stream analysis
# ═══════════════════════════════════════════════════════════════════════════════

STREAM_CONFIGS = {
    "b2b": {
        "dir": B2B_DIR,
        "input_id_col": "input_icd",
        "output_col": "output_disease",
        "metric_col": "cross_auc",
        "improvement_col": "auc_improvement",
        "self_metric_col": "self_best_auc",
        "has_self_col": "has_self_auc",
        "metric_label": "AUC",
        "is_binary_input": True,
    },
    "b2c": {
        "dir": B2C_DIR,
        "input_id_col": "input_icd",
        "output_col": "output_ontology",
        "metric_col": "cross_auc",
        "improvement_col": "auc_improvement",
        "self_metric_col": "self_best_auc",
        "has_self_col": "has_self_auc",
        "metric_label": "AUC",
        "is_binary_input": True,
        "extra_cols": ["output_loinc"],
    },
}


def assign_tier(plausibility, n_out_for_input, best_imp, weighted_score):
    """Improved tier assignment with gradient logic.

    Tier 1 — HIGH confidence:
      - plausibility=high AND n_out<=15 AND improvement>=0.025
      - OR plausibility=high AND n_out>15 AND improvement>=0.050 AND weighted_score>=0.001
        (high plausibility + strong signal can overcome noisy input)

    Tier 2 — MEDIUM confidence:
      - plausibility=medium AND improvement>=0.025
      - OR plausibility=high AND n_out>15 AND improvement>=0.025
        (high plausibility but noisy input, not meeting Tier 1 thresholds)
      - OR plausibility=low AND improvement>=0.050
        (unknown pathway but very strong signal worth investigating)

    Tier 3 — LOW confidence / reference:
      - everything else
    """
    if plausibility == "high" and n_out_for_input <= 15 and best_imp >= 0.025:
        return 1
    if plausibility == "high" and n_out_for_input > 15 and best_imp >= 0.050 and weighted_score >= 0.001:
        return 1
    if plausibility == "medium" and best_imp >= 0.025:
        return 2
    if plausibility == "high" and n_out_for_input > 15 and best_imp >= 0.025:
        return 2
    if plausibility == "low" and best_imp >= 0.050:
        return 2
    return 3


def analyze_stream(label, cfg):
    """Analyze a single stream: annotate, rank, tier."""
    stream_dir = cfg["dir"]
    detail_path = stream_dir / "cross_list_detail.csv"
    summary_path = stream_dir / "cross_list_summary.csv"

    if not detail_path.exists() or not summary_path.exists():
        print(f"\n[WARN] Skipping {label}: files not found")
        return []

    print(f"\n{'=' * 70}")
    print(f"Phase 2: {label.upper()} Analysis")
    print(f"{'=' * 70}")

    input_id_col = cfg["input_id_col"]
    output_col = cfg["output_col"]
    metric_col = cfg["metric_col"]
    improvement_col = cfg["improvement_col"]
    self_metric_col = cfg["self_metric_col"]
    has_self_col = cfg["has_self_col"]
    is_binary = cfg["is_binary_input"]
    extra_cols = cfg.get("extra_cols", [])

    detail = load_detail_rows(detail_path)
    summary = load_summary_cross_list_inputs(summary_path)
    cross_list_input_ids = {r[input_id_col] for r in summary}

    pgs_spec = load_pgs_specificity(label)
    hubs = load_output_hub(label)

    # Group detail by (input_id, output) — disease/trait-level pairs
    pair_data = defaultdict(lambda: {"models": [], "metrics": [], "improvements": [], "extra": {}})
    for r in detail:
        if r[input_id_col] not in cross_list_input_ids:
            continue
        raw_metric = str(r.get(metric_col, "")).strip()
        if not raw_metric:
            continue
        eff_improvement = _effective_improvement(r, improvement_col, metric_col, has_self_col)
        if eff_improvement is None:
            continue
        key = (r[input_id_col], r[output_col])
        pair_data[key]["models"].append(r["output_pgs_id"])
        pair_data[key]["metrics"].append(float(raw_metric))
        pair_data[key]["improvements"].append(eff_improvement)
        pair_data[key]["input_ontology"] = r["input_ontology"]
        pair_data[key]["self_metric"] = r.get(self_metric_col, "")
        pair_data[key]["has_self"] = r.get(has_self_col, "")
        for ec in extra_cols:
            if ec in r:
                pair_data[key]["extra"][ec] = r[ec]

    if not pair_data:
        print(f"  No qualifying pairs found for {label}")
        return []

    # Get n_unique_outputs per input
    input_n_outputs = defaultdict(int)
    for (inp_id, _) in pair_data:
        input_n_outputs[inp_id] += 1

    rows = []
    for (input_id, output_name), data in pair_data.items():
        # System classification
        if is_binary:
            input_system = classify_system_from_icd(input_id)
        else:
            input_system = classify_system_from_ontology(data["input_ontology"])
        output_system = classify_system_from_ontology(output_name)
        plausibility, plaus_reason = assess_plausibility(input_system, output_system)

        best_metric = max(data["metrics"])
        best_imp = max(data["improvements"])
        n_models = len(data["models"])

        model_specs = [pgs_spec.get(m, 0) for m in data["models"]]
        best_model_spec = max(model_specs) if model_specs else 0

        hub_freq = hubs.get(output_name, 0)
        output_spec = 1.0 / hub_freq if hub_freq > 0 else 0

        n_out_for_input = input_n_outputs[input_id]

        weighted_score = best_imp * best_model_spec * output_spec

        tier = assign_tier(plausibility, n_out_for_input, best_imp, weighted_score)

        row = {
            "input_id": input_id,
            "input_ontology": data["input_ontology"][:60],
            "has_self": data["has_self"],
            "self_best_metric": data["self_metric"],
            "output_name": output_name[:80],
            "input_system": input_system,
            "output_system": output_system,
            "plausibility": plausibility,
            "plausibility_reason": plaus_reason,
            "n_models": n_models,
            "best_cross_metric": round(best_metric, 6),
            "best_improvement": round(best_imp, 6),
            "best_model_specificity": round(best_model_spec, 4),
            "output_hub_freq": hub_freq,
            "input_n_outputs": n_out_for_input,
            "weighted_score": round(weighted_score, 8),
            "tier": tier,
        }
        # Add extra columns
        for ec in extra_cols:
            row[ec] = data["extra"].get(ec, "")
        rows.append(row)

    # Sort by tier, then weighted_score desc
    rows.sort(key=lambda x: (x["tier"], -x["weighted_score"]))

    retained_rank = defaultdict(int)
    for r in rows:
        r["pair_retain_flag"] = r["tier"] <= 2 and _passes_pair_retention_floor(r)
        if r["pair_retain_flag"]:
            retained_rank[r["input_id"]] += 1
            r["retained_rank_within_input"] = retained_rank[r["input_id"]]
        else:
            r["retained_rank_within_input"] = ""

    # Write full annotated CSV
    outpath = OUTPUT_DIR / f"{label}_annotated_pairs.csv"
    with open(outpath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    # Print compact summary by tier
    metric_label = cfg["metric_label"]
    for tier_num in [1, 2, 3]:
        tier_rows = [r for r in rows if r["tier"] == tier_num]
        tier_label = {1: "HIGH confidence", 2: "MEDIUM confidence", 3: "LOW confidence / reference"}
        print(f"\n--- Tier {tier_num}: {tier_label[tier_num]} ({len(tier_rows)} pairs) ---")
        if tier_rows:
            print(f"  {'Target':<10s} {'Target Trait':<30s} {'→':>1s} {'Cross Trait':<35s} {'Plaus':>6s} {metric_label+'+':>7s} {'N_out':>5s} {'Hub':>4s} {'Score':>10s}")
            for r in tier_rows[:MAX_PRINTED_ROWS_PER_TIER]:
                print(f"  {r['input_id']:<10s} {r['input_ontology'][:30]:<30s} → {r['output_name'][:35]:<35s} {r['plausibility']:>6s} {r['best_improvement']:>7.4f} {r['input_n_outputs']:>5d} {r['output_hub_freq']:>4d} {r['weighted_score']:>10.6f}")
            if len(tier_rows) > MAX_PRINTED_ROWS_PER_TIER:
                print(f"  ... {len(tier_rows) - MAX_PRINTED_ROWS_PER_TIER} additional pairs omitted")

    # Per-target summary: best tier
    print(f"\n--- Per-Target Best Pair ({label}) ---")
    input_best = {}
    for r in rows:
        inp = r["input_id"]
        if inp not in input_best or r["tier"] < input_best[inp]["tier"]:
            input_best[inp] = r
    for inp in sorted(input_best, key=lambda x: input_best[x]["tier"]):
        r = input_best[inp]
        print(f"  {inp:<10s} Best Tier={r['tier']}  → {r['output_name'][:45]:<45s} ({r['plausibility']}, {metric_label}+{r['best_improvement']:.4f})")

    return rows


# ═══════════════════════════════════════════════════════════════════════════════
# Run all streams
# ═══════════════════════════════════════════════════════════════════════════════

all_results = {}
for label, cfg in STREAM_CONFIGS.items():
    all_results[label] = analyze_stream(label, cfg)


# ═══════════════════════════════════════════════════════════════════════════════
# 2.4  Plausibility Coverage Audit
# ═══════════════════════════════════════════════════════════════════════════════

def plausibility_coverage_audit(all_results):
    """Audit how many pairs fall into each plausibility level.
    Flag uncovered system pairs that might need new rules."""
    print(f"\n\n{'=' * 70}")
    print("2.4 Plausibility Coverage Audit")
    print("=" * 70)

    audit_rows = []

    for label, rows in all_results.items():
        if not rows:
            continue

        total = len(rows)
        plaus_counts = Counter(r["plausibility"] for r in rows)
        no_pathway = [r for r in rows if "no known pathway" in r["plausibility_reason"]]

        print(f"\n--- {label} ({total} pairs) ---")
        for p in ["high", "medium", "low"]:
            n = plaus_counts.get(p, 0)
            pct = n / total * 100
            print(f"  {p:>6s}: {n:>4d} pairs ({pct:5.1f}%)")

        print(f"\n  Pairs with 'no known pathway': {len(no_pathway)} ({len(no_pathway)/total*100:.1f}%)")

        # Find the most frequent uncovered system pairs
        uncovered_pairs = Counter()
        for r in no_pathway:
            pair_key = f"{r['input_system']} → {r['output_system']}"
            uncovered_pairs[pair_key] += 1

        if uncovered_pairs:
            print(f"\n  Top 20 uncovered system pairs (need rule review):")
            print(f"    {'System Pair':<60s} {'Count':>5s}")
            for pair, count in uncovered_pairs.most_common(20):
                print(f"    {pair:<60s} {count:>5d}")

        # Per-tier plausibility breakdown
        print(f"\n  Plausibility breakdown by tier:")
        for tier_num in [1, 2, 3]:
            tier_rows = [r for r in rows if r["tier"] == tier_num]
            if not tier_rows:
                continue
            tier_plaus = Counter(r["plausibility"] for r in tier_rows)
            parts = ", ".join(f"{p}={tier_plaus.get(p,0)}" for p in ["high", "medium", "low"])
            print(f"    Tier {tier_num} ({len(tier_rows)} pairs): {parts}")

        audit_rows.append({
            "stream": label,
            "total_pairs": total,
            "n_high": plaus_counts.get("high", 0),
            "n_medium": plaus_counts.get("medium", 0),
            "n_low": plaus_counts.get("low", 0),
            "pct_high": round(plaus_counts.get("high", 0) / total * 100, 1),
            "pct_medium": round(plaus_counts.get("medium", 0) / total * 100, 1),
            "pct_low": round(plaus_counts.get("low", 0) / total * 100, 1),
            "n_no_pathway": len(no_pathway),
            "pct_no_pathway": round(len(no_pathway) / total * 100, 1),
        })

    if audit_rows:
        outpath = OUTPUT_DIR / "plausibility_coverage_audit.csv"
        with open(outpath, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=audit_rows[0].keys())
            w.writeheader()
            w.writerows(audit_rows)
        print(f"\nCoverage audit saved to: {outpath}")

    return audit_rows


audit_results = plausibility_coverage_audit(all_results)


# ═══════════════════════════════════════════════════════════════════════════════
# 2.5  Cross-Trait Shortlists (primary Phase 2 output)
# ═══════════════════════════════════════════════════════════════════════════════

binary_streams = dict(all_results)
binary_target_universe = load_binary_target_universe(STREAM_CONFIGS)


def _pair_sort_key(row):
    return (
        row["tier"],
        -row["weighted_score"],
        -row["best_improvement"],
        -row["best_cross_metric"],
        row["output_name"],
    )


def _retain_rows(rows):
    return [r for r in rows if r.get("pair_retain_flag")]


def build_stream_cross_trait_shortlist(label, rows):
    retained = sorted(_retain_rows(rows), key=_pair_sort_key)
    grouped = defaultdict(list)
    for r in retained:
        grouped[r["input_id"]].append(r)

    shortlisted = []
    for input_id in sorted(grouped):
        ordered = grouped[input_id]
        selected = []
        selected_keys = set()
        seen_systems = set()

        for reason in ("best_by_output_system", "best_remaining"):
            for r in ordered:
                pair_key = (
                    r["output_name"],
                    r.get("output_loinc", ""),
                    r["output_system"],
                )
                if pair_key in selected_keys:
                    continue
                if reason == "best_by_output_system" and r["output_system"] in seen_systems:
                    continue

                row = dict(r)
                row["stream"] = label
                row["target_id"] = r["input_id"]
                row["target_trait"] = r["input_ontology"]
                row["cross_trait"] = r["output_name"]
                row["cross_trait_code"] = r.get("output_loinc", "")
                row["cross_trait_type"] = "continuous" if label == "b2c" else "binary"
                row["shortlist_reason"] = reason
                selected.append(row)
                selected_keys.add(pair_key)
                seen_systems.add(r["output_system"])

                if len(selected) >= MAX_SHORTLIST_PER_TARGET_PER_STREAM:
                    break
            if len(selected) >= MAX_SHORTLIST_PER_TARGET_PER_STREAM:
                break

        for rank, row in enumerate(selected, start=1):
            row["shortlist_rank_within_target"] = rank
            shortlisted.append(row)

    shortlisted.sort(key=lambda r: (r["target_id"], r["shortlist_rank_within_target"]))
    return shortlisted


def build_cross_trait_shortlists(binary_streams, target_universe):
    print(f"\n\n{'=' * 70}")
    print("2.5 Cross-Trait Shortlists")
    print("=" * 70)

    shortlist_by_stream = {}
    retained_by_stream = {}

    for label, rows in binary_streams.items():
        retained = sorted(_retain_rows(rows), key=_pair_sort_key)
        retained_by_stream[label] = retained
        shortlist = build_stream_cross_trait_shortlist(label, rows)
        shortlist_by_stream[label] = shortlist

        outpath = OUTPUT_DIR / f"{label}_cross_trait_shortlist.csv"
        if shortlist:
            with open(outpath, "w", newline="") as f:
                fieldnames = [
                    "stream",
                    "target_id",
                    "target_trait",
                    "cross_trait_type",
                    "cross_trait_code",
                    "cross_trait",
                    "shortlist_rank_within_target",
                    "shortlist_reason",
                    "tier",
                    "plausibility",
                    "plausibility_reason",
                    "best_cross_metric",
                    "best_improvement",
                    "n_models",
                    "best_model_specificity",
                    "output_hub_freq",
                    "output_system",
                    "weighted_score",
                    "has_self",
                    "self_best_metric",
                ]
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows([{k: row.get(k, "") for k in fieldnames} for row in shortlist])

        retained_targets = {r["input_id"] for r in retained}
        print(f"\n--- {label.upper()} shortlist ---")
        print(f"  Retained pairs before shortlist: {len(retained)}")
        print(f"  Shortlisted pairs:              {len(shortlist)}")
        print(f"  Targets covered:                {len(retained_targets)}")
        if retained_targets:
            print(f"  Mean shortlist size / target:   {len(shortlist)/len(retained_targets):.1f}")
        print(f"  Output file: {outpath}")

    combined = []
    for label, rows in shortlist_by_stream.items():
        combined.extend(rows)
    combined.sort(key=lambda r: (r["target_id"], _pair_sort_key(r), r["stream"]))

    combined_rank = defaultdict(int)
    for row in combined:
        combined_rank[row["target_id"]] += 1
        row["combined_shortlist_rank"] = combined_rank[row["target_id"]]

    combined_outpath = OUTPUT_DIR / "binary_cross_trait_shortlist.csv"
    if combined:
        with open(combined_outpath, "w", newline="") as f:
            fieldnames = [
                "target_id",
                "target_trait",
                "combined_shortlist_rank",
                "stream",
                "cross_trait_type",
                "cross_trait_code",
                "cross_trait",
                "shortlist_rank_within_target",
                "shortlist_reason",
                "tier",
                "plausibility",
                "best_cross_metric",
                "best_improvement",
                "n_models",
                "best_model_specificity",
                "output_hub_freq",
                "output_system",
                "weighted_score",
                "has_self",
                "self_best_metric",
            ]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows([{k: row.get(k, "") for k in fieldnames} for row in combined])

    all_binary_targets = sorted(target_universe)
    stream_shortlist_map = {
        label: defaultdict(list) for label in shortlist_by_stream
    }
    stream_retained_map = {
        label: defaultdict(list) for label in retained_by_stream
    }
    stream_all_map = {
        label: defaultdict(list) for label in binary_streams
    }
    for label, rows in shortlist_by_stream.items():
        for row in rows:
            stream_shortlist_map[label][row["target_id"]].append(row)
    for label, rows in retained_by_stream.items():
        for row in rows:
            stream_retained_map[label][row["input_id"]].append(row)
    for label, rows in binary_streams.items():
        for row in rows:
            stream_row = dict(row)
            stream_row["stream"] = label
            stream_all_map[label][row["input_id"]].append(stream_row)

    summary_rows = []
    for target_id in all_binary_targets:
        meta = target_universe[target_id]
        b2b_rows = stream_shortlist_map["b2b"].get(target_id, [])
        b2c_rows = stream_shortlist_map["b2c"].get(target_id, [])
        combined_rows = sorted(b2b_rows + b2c_rows, key=lambda r: (r["tier"], -r["weighted_score"], -r["best_improvement"], r["stream"], r["cross_trait"]))
        all_candidate_rows = sorted(
            stream_all_map["b2b"].get(target_id, []) + stream_all_map["b2c"].get(target_id, []),
            key=lambda r: (r["tier"], -r["weighted_score"], -r["best_improvement"], r["output_name"]),
        )
        top_any = combined_rows[0] if combined_rows else None
        top_b2b = b2b_rows[0] if b2b_rows else None
        top_b2c = b2c_rows[0] if b2c_rows else None
        top_available = all_candidate_rows[0] if all_candidate_rows else None

        summary_rows.append({
            "target_icd": target_id,
            "target_trait": meta["target_trait"][:80],
            "input_type": meta["input_type"],
            "streams_present": meta["streams"],
            "has_self": meta["has_self"],
            "shortlist_status": "has_recommended_cross_trait" if combined_rows else "no_recommended_cross_trait",
            "n_retained_pairs_b2b": len(stream_retained_map["b2b"].get(target_id, [])),
            "n_retained_pairs_b2c": len(stream_retained_map["b2c"].get(target_id, [])),
            "n_retained_pairs_total": (
                len(stream_retained_map["b2b"].get(target_id, []))
                + len(stream_retained_map["b2c"].get(target_id, []))
            ),
            "n_shortlisted_pairs_b2b": len(b2b_rows),
            "n_shortlisted_pairs_b2c": len(b2c_rows),
            "n_shortlisted_pairs_total": len(combined_rows),
            "top_cross_trait": top_any["cross_trait"] if top_any else "",
            "top_cross_trait_stream": top_any["stream"] if top_any else "",
            "top_cross_trait_tier": top_any["tier"] if top_any else "",
            "top_cross_trait_plausibility": top_any["plausibility"] if top_any else "",
            "top_cross_trait_improvement": top_any["best_improvement"] if top_any else "",
            "best_available_cross_trait": top_available["output_name"] if top_available else "",
            "best_available_stream": top_available["stream"] if top_available else "",
            "best_available_tier": top_available["tier"] if top_available else "",
            "best_available_plausibility": top_available["plausibility"] if top_available else "",
            "best_available_improvement": top_available["best_improvement"] if top_available else "",
            "top_b2b_cross_trait": top_b2b["cross_trait"] if top_b2b else "",
            "top_b2b_tier": top_b2b["tier"] if top_b2b else "",
            "top_b2b_improvement": top_b2b["best_improvement"] if top_b2b else "",
            "top_b2c_cross_trait": top_b2c["cross_trait"] if top_b2c else "",
            "top_b2c_tier": top_b2c["tier"] if top_b2c else "",
            "top_b2c_improvement": top_b2c["best_improvement"] if top_b2c else "",
            "shortlisted_b2b_cross_traits": "; ".join(row["cross_trait"] for row in b2b_rows),
            "shortlisted_b2c_cross_traits": "; ".join(row["cross_trait"] for row in b2c_rows),
        })

    summary_rows.sort(key=lambda r: (-r["n_shortlisted_pairs_total"], r["target_icd"]))
    summary_outpath = OUTPUT_DIR / "binary_target_cross_trait_summary.csv"
    if summary_rows:
        with open(summary_outpath, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
            w.writeheader()
            w.writerows(summary_rows)

    print(f"\nCombined binary cross-trait shortlist: {combined_outpath}")
    print(f"Binary target cross-trait summary:    {summary_outpath}")
    print(f"Binary retained targets in universe:  {len(all_binary_targets)}")
    print(f"Targets with shortlist output:        {sum(1 for row in summary_rows if row['n_shortlisted_pairs_total'] > 0)}")
    print(f"Targets without Tier 1/2 cross trait: {sum(1 for row in summary_rows if row['n_shortlisted_pairs_total'] == 0)}")

    return shortlist_by_stream, combined, summary_rows


shortlist_by_stream, binary_shortlist_rows, binary_cross_trait_summary = build_cross_trait_shortlists(
    binary_streams,
    binary_target_universe,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Cross-stream consolidated view (secondary target summary)
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n\n{'=' * 70}")
print("Consolidated: Best Pair Tier per Binary-Input Target")
print("=" * 70)


def consolidate_streams(stream_results, id_label):
    """Consolidate best tier per input across streams."""
    all_ids = set()
    stream_best = {label: {} for label in stream_results}

    for label, rows in stream_results.items():
        for r in rows:
            inp = r["input_id"]
            all_ids.add(inp)
            if inp not in stream_best[label] or r["tier"] < stream_best[label][inp]["tier"] or \
               (r["tier"] == stream_best[label][inp]["tier"] and r["weighted_score"] > stream_best[label][inp]["weighted_score"]):
                stream_best[label][inp] = r

    if not all_ids:
        return {}

    # Overall best tier
    overall = {}
    for inp in all_ids:
        tiers = [stream_best[label][inp]["tier"]
                 for label in stream_results if inp in stream_best[label]]
        overall[inp] = min(tiers) if tiers else 99

    # Print
    stream_labels = list(stream_results.keys())
    header = f"\n{id_label:<10s} {'Ontology':<35s} {'Overall':>7s}"
    for sl in stream_labels:
        header += f" | {sl} Tier"
    print(header)
    print("-" * (60 + 12 * len(stream_labels)))

    for inp in sorted(all_ids, key=lambda x: overall[x]):
        ont = ""
        for sl in stream_labels:
            if inp in stream_best[sl]:
                ont = stream_best[sl][inp]["input_ontology"][:35]
                break
        line = f"{inp:<10s} {ont:<35s} Tier {overall[inp]:>1d} "
        for sl in stream_labels:
            if inp in stream_best[sl]:
                r = stream_best[sl][inp]
                line += f" | T{r['tier']}  {r['output_name'][:25]:<25s}"
            else:
                line += f" | -                            "
        print(line)

    # Count
    for t in [1, 2, 3]:
        ids_at_tier = sorted([inp for inp, tier in overall.items() if tier == t])
        print(f"\nTier {t}: {len(ids_at_tier)} inputs — {ids_at_tier}")

    return overall


print("\n--- Binary-input target traits (ICD) ---")
binary_overall = consolidate_streams(binary_streams, "ICD")


# ═══════════════════════════════════════════════════════════════════════════════
# 2.6  Target Readiness Summary (secondary / compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

def build_ready_for_transfer(binary_overall, all_results):
    """Build a target-level readiness CSV for downstream transfer tooling.

    This is kept as a secondary compatibility output; the primary Phase 2
    outputs are the cross-trait shortlist CSVs above.
    """
    print(f"\n\n{'=' * 70}")
    print("2.6 Target Readiness Summary")
    print("=" * 70)

    if not HAS_TRAIT_MAPPING:
        print("[SKIP] trait_mapping not available — cannot build ready-for-transfer list")
        return

    # Collect best pair per (ICD, stream)
    icd_stream_best = {}
    for label in ["b2b", "b2c"]:
        for r in all_results.get(label, []):
            key = (r["input_id"], label)
            if key not in icd_stream_best or r["tier"] < icd_stream_best[key]["tier"] or \
               (r["tier"] == icd_stream_best[key]["tier"] and r["weighted_score"] > icd_stream_best[key]["weighted_score"]):
                icd_stream_best[key] = r

    rows = []
    dossier_ids = set()
    dossier_path = TRANSFER_DIR / "runs" / "tool_calling_agent" / "binary_candidate_dossiers.json"
    if dossier_path.exists():
        try:
            dossier_payload = json.loads(dossier_path.read_text())
            dossier_ids = {item["target"]["target_id"] for item in dossier_payload if item.get("target")}
        except Exception:
            dossier_ids = set()

    result_ids = set()
    results_path = TRANSFER_DIR / "runs" / "tool_calling_agent" / "all-tools" / "results.json"
    if results_path.exists():
        try:
            results_payload = json.loads(results_path.read_text())
            result_ids = {
                item["target"]["target_id"]
                for item in results_payload
                if item.get("target") and item["target"].get("target_id")
            }
        except Exception:
            result_ids = set()

    for icd in sorted(binary_overall.keys(), key=lambda x: binary_overall[x]):
        overall_tier = binary_overall[icd]

        # GWAS Atlas mapping status
        gwas_trait = CROSS_LIST_TO_GWAS_ATLAS.get(icd)
        has_mapping = gwas_trait is not None
        mapping_status = "mapped" if has_mapping else "unmapped"

        has_candidate_dossier = icd in dossier_ids
        has_agent_result = icd in result_ids

        # Readiness assessment
        if has_mapping and has_agent_result:
            readiness = "complete"
        elif has_mapping and has_candidate_dossier:
            readiness = "agent_ready"
        elif has_mapping:
            readiness = "mapping_ready"
        else:
            readiness = "needs_mapping"

        # Best b2b pair
        b2b_r = icd_stream_best.get((icd, "b2b"))
        b2c_r = icd_stream_best.get((icd, "b2c"))

        ont = ""
        if b2b_r:
            ont = b2b_r["input_ontology"]
        elif b2c_r:
            ont = b2c_r["input_ontology"]

        rows.append({
            "input_icd": icd,
            "input_ontology": ont[:60],
            "overall_tier": overall_tier,
            "gwas_atlas_trait": gwas_trait or "",
            "mapping_status": mapping_status,
            "has_candidate_dossier": has_candidate_dossier,
            "has_agent_result": has_agent_result,
            "readiness": readiness,
            "b2b_best_tier": b2b_r["tier"] if b2b_r else "",
            "b2b_best_output": b2b_r["output_name"][:50] if b2b_r else "",
            "b2b_best_plausibility": b2b_r["plausibility"] if b2b_r else "",
            "b2b_best_improvement": b2b_r["best_improvement"] if b2b_r else "",
            "b2c_best_tier": b2c_r["tier"] if b2c_r else "",
            "b2c_best_output": b2c_r["output_name"][:50] if b2c_r else "",
            "b2c_best_plausibility": b2c_r["plausibility"] if b2c_r else "",
            "b2c_best_improvement": b2c_r["best_improvement"] if b2c_r else "",
        })

    # Write CSV
    outpath = OUTPUT_DIR / "ready_for_transfer.csv"
    with open(outpath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    # Print summary
    readiness_counts = Counter(r["readiness"] for r in rows)
    tier_counts = Counter(r["overall_tier"] for r in rows)
    mapped_count = sum(1 for r in rows if r["mapping_status"] == "mapped")

    print(f"\nTotal target traits: {len(rows)}")
    print(f"\nMapping status:")
    print(f"  Mapped to GWAS Atlas:   {mapped_count}")
    print(f"  Unmapped:               {len(rows) - mapped_count}")

    print(f"\nReadiness status:")
    for status in ["complete", "agent_ready", "mapping_ready", "needs_mapping"]:
        n = readiness_counts.get(status, 0)
        print(f"  {status:<20s}: {n:>3d}")

    print(f"\nBy overall tier:")
    for t in [1, 2, 3]:
        tier_rows = [r for r in rows if r["overall_tier"] == t]
        mapped_in_tier = sum(1 for r in tier_rows if r["mapping_status"] == "mapped")
        complete_in_tier = sum(1 for r in tier_rows if r["readiness"] == "complete")
        print(f"  Tier {t}: {len(tier_rows)} target traits, {mapped_in_tier} mapped, {complete_in_tier} with agent results")

    # Detailed table
    print(f"\n{'ICD':<10s} {'Ontology':<35s} {'Tier':>4s} {'Mapped':>6s} {'Dossier':>7s} {'Agent':>5s} {'Readiness':<15s} {'GWAS Trait':<30s}")
    print("-" * 120)
    for r in rows:
        print(f"{r['input_icd']:<10s} {r['input_ontology'][:35]:<35s} "
              f"{r['overall_tier']:>4d} "
              f"{'Y' if r['mapping_status']=='mapped' else 'N':>6s} "
              f"{'Y' if r['has_candidate_dossier'] else 'N':>7s} "
              f"{'Y' if r['has_agent_result'] else 'N':>5s} "
              f"{r['readiness']:<15s} "
              f"{r['gwas_atlas_trait'][:30]:<30s}")

    # Highlight actionable items
    print(f"\n--- Actionable: Tier 1/2 target traits needing work ---")
    for r in rows:
        if r["overall_tier"] <= 2 and r["readiness"] != "complete":
            action = ""
            if r["readiness"] == "needs_mapping":
                action = "NEED: GWAS Atlas trait mapping"
            elif r["readiness"] == "mapping_ready":
                action = "NEED: Build candidate dossier"
            elif r["readiness"] == "agent_ready":
                action = "NEED: Run all-tools agent"
            print(f"  {r['input_icd']:<10s} Tier {r['overall_tier']}  {r['readiness']:<15s}  {action}")

    print(f"\nCompatibility target summary saved to: {outpath}")
    return rows


transfer_candidates = build_ready_for_transfer(binary_overall, all_results)

print(f"\n{'=' * 70}")
print(f"Phase 2 analysis complete. Output files in: {OUTPUT_DIR}")
print(f"{'=' * 70}")
