#!/usr/bin/env python3
"""
Overlap All of Us traits with PGS Catalog traits (v5 - alphanumeric tokenizing).

Matching tiers:
    Tier 1  (exact):       normalized label/synonym exact match
    Tier 1b (exact_core):  core name (ICD modifiers stripped) exact match
    Tier 1c (synonym_map): medical synonym / ICD-to-clinical term mapping
    Tier 2  (token):       token-based overlap coefficient >= 0.80

Confidence (two levels only):
    HIGH   = Tier 1 / 1b / 1c  (exact string identity after normalization)
    MEDIUM = Tier 2             (token overlap with coefficient >= 0.80)

Output:
    aou_pgs_trait_overlap.csv          (all row-level matches)
    aou_pgs_trait_overlap_by_root.csv  (deduplicated by icd_root)
    aou_pgs_trait_overlap_by_pgs.csv   (deduplicated by pgs_id)
    aou_pgs_trait_no_match.csv         (AOU traits without match)

Usage:
    python scripts/data_processing/overlap_aou_pgs_traits.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
AOU_CSV = PROJECT_ROOT / "data" / "all_of_us" / "num_cases_1000.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "all_of_us" / "aou_pgs_trait_overlap.csv"
OUTPUT_ROOT_CSV = PROJECT_ROOT / "data" / "all_of_us" / "aou_pgs_trait_overlap_by_root.csv"
OUTPUT_PGS_CSV = PROJECT_ROOT / "data" / "all_of_us" / "aou_pgs_trait_overlap_by_pgs.csv"
OUTPUT_NO_MATCH_CSV = PROJECT_ROOT / "data" / "all_of_us" / "aou_pgs_trait_no_match.csv"
PGS_API_BASE = "https://www.pgscatalog.org/rest"
PGS_PAGE_SIZE = 100

# Confidence levels (only two)
CONFIDENCE_HIGH = "HIGH"      # exact match (all Tier 1 variants)
CONFIDENCE_MEDIUM = "MEDIUM"  # token_overlap with overlap_coefficient >= 0.80

# ---------------------------------------------------------------------------
# Medical stopwords and normalization
# ---------------------------------------------------------------------------
MEDICAL_STOPWORDS = {
    "unspecified", "other", "specified", "unsp", "disease", "disorder",
    "syndrome", "measurement", "trait", "of", "the", "and", "or", "in",
    "with", "without", "w", "wo", "w/o", "not", "no", "nos", "nec",
    "due", "to", "by", "for", "a", "an", "on", "at", "from",
    "initial", "encounter", "subsequent", "sequela",
    "right", "left", "bilateral", "unilateral", "midline",
    "upper", "lower", "anterior", "posterior", "lateral", "medial",
    "proximal", "distal",
    "site", "region", "area", "part", "parts", "limb", "extremity",
    "extremities",
    "adult", "pediatric", "juvenile", "infantile", "neonatal",
    "mild", "moderate", "severe", "stage", "grade", "degree",
    "type", "form", "forms", "kind",
    "first", "second", "third", "1", "2", "3", "4", "i", "ii", "iii", "iv",
    "episode", "episodes", "recurrent", "single",
    "intractable", "refractory",
    "status", "migrainosus", "epilepticus",
    "current", "previous", "history",
    "remission", "partial", "full", "complete",
    "complications", "complication", "complicated", "uncomplicated",
    "obstruction", "gangrene", "bleeding", "hemorrhage",
    "pathological", "pathologic", "fracture",
    "ear", "foot", "hand", "knee", "hip", "shoulder",
    "ankle", "wrist", "finger", "toe", "elbow",
    "skin", "subcutaneous", "tissue",
    "congestive", "systolic", "diastolic",
    "native", "coronary", "artery",
    "pre", "post",
    # Additional ICD-10 modifier words
    "classified", "elsewhere", "associated",
    "acquired", "congenital",
}

# Single-token overlaps that are too generic/ambiguous to trust.
AMBIGUOUS_SINGLE_TOKENS = {
    "cancer", "malignant", "benign",
    "diabetic", "metabolic", "lipoprotein",
    "disease", "disorder", "syndrome", "condition",
    "injury", "measurement", "procedure",
}

# Disease categories can still include non-disease concepts
# (e.g., exam/lab results, risk/susceptibility terms).
NON_DISEASE_LABEL_TERMS = {
    "abnormal", "measurement", "amount", "count", "percentage", "ratio",
    "volume", "index", "score", "concentration", "level", "marker",
    "susceptibility", "risk", "exposure", "status", "profile",
}

NON_DISEASE_LABEL_PHRASES = {
    "age at ",
    "genetic susceptibility",
    "polygenic risk",
    "risk score",
    "abnormal ekg",
    "abnormal ecg",
}

# PGS labels that are too generic to be matched via token overlap
GENERIC_PGS_LABELS = {
    # Modifier-only or too generic
    "recurrent", "benign", "female", "male", "cancer", "disease",
    "medical procedure", "complication", "vitamin", "device", "device complication",
    # Organ-system level (too broad)
    "heart disease", "endocrine system disease", "eye disease",
    "skin disease", "respiratory system disease",
    "digestive system disease", "cardiovascular disease",
    "mental or behavioural disorder", "intestinal disease",
    "esophageal disease", "pancreas disease", "joint disease",
    "metabolic disease", "allergic disease", "thyroid disease",
    "connective tissue disease", "soft tissue disease",
    "prostate disease", "corneal disease",
    # Measurement-type traits (not diseases)
    "aortic measurement", "lifestyle measurement",
    "snoring measurement", "glucose measurement",
    "bone tissue density",
    # Injury-type traits
    "knee injury",
    # Multi-word but misleading when only partial tokens overlap
    "congenital vitamin k-dependent coagulation factors deficiency",
    "childhood onset asthma", "central nervous system cancer",
    "malignant laryngeal neoplasm",
    # Neoplasm terms that cause cross-organ false positives
    "benign digestive system neoplasm",
    "uterine benign neoplasm",
    "benign colon neoplasm",
    # Measurement traits that match clinical conditions wrongly
    "white matter hyperintensity measurement",
    "bmi-adjusted fasting blood glucose measurement",
    "heel bone mineral density",
    "glucose tolerance test",
    "menstrual cycle attribute",
    "prostate specific antigen amount",
    "age-related hearing impairment",
    "alcohol use disorder measurement",
}

# Known false-positive pairs: (substring_in_aou_core, pgs_label_lower)
FALSE_POSITIVE_PAIRS = {
    # Completely different conditions with similar names
    ("spondylosis", "spondyloarthropathy"),
    ("calculus of gallbladder", "urolithiasis"),
    ("calculus of bile duct", "urolithiasis"),
    ("hydronephrosis", "nephrotic syndrome"),
    ("cyst of pancreas", "pancreatic neoplasm"),
    ("other specified diseases of pancreas", "pancreatic neoplasm"),
    ("disease of pancreas", "pancreatic neoplasm"),
    ("hyperuricemia", "arthritis"),
    ("herpesviral vesicular dermatitis", "dermatitis"),
    # Hypertension subtypes that are different diseases
    ("portal hypertension", "hypertension"),
    ("pulmonary hypertension", "hypertension"),
    ("ocular hypertension", "hypertension"),
    ("hypertension secondary to endocrine disorders", "hypertension"),
    ("secondary hypertension", "hypertension"),
    # Negated / comorbidity conditions
    ("acute cystitis with hematuria", "hematuria"),
    ("acute cystitis without hematuria", "hematuria"),
    ("pulmonary embolism without acute cor pulmonale", "cor pulmonale"),
    ("anemia in chronic kidney disease", "chronic kidney disease"),
    ("hypertensive chronic kidney disease", "chronic kidney disease"),
    ("cerebral infarction", "cerebrovascular disorder"),
    ("insomnia due to other mental disorder", "mental or behavioural disorder"),
    ("recurrent oral aphthae", "recurrent"),
    ("acute recurrent maxillary sinusitis", "recurrent"),
    ("pain in thoracic spine", "chest pain"),
    ("other specified diseases of anus and rectum", "digestive system disease"),
    # Spelling-similar but medically distinct
    ("hypotension", "hypertension"),
    ("hyperparathyroidism", "hyperthyroidism"),
    ("hypocalcemia", "hypoglycemia"),
    ("acidosis", "sarcoidosis"),
    ("scoliosis", "sarcoidosis"),
    ("nail dystrophy", "corneal dystrophy"),
    ("lyme disease", "liver disease"),
    # Organ mismatch for neoplasms
    ("benign neoplasm of skin", "benign colon neoplasm"),
    ("malignant neoplasm", "malignant laryngeal neoplasm"),
    ("secondary malignant neoplasm of bone", "malignant laryngeal neoplasm"),
    ("genetic susceptibility to malignant neoplasm", "malignant laryngeal neoplasm"),
    ("calculus of gallbladder", "cholecystitis"),
    ("chronic pulmonary edema", "chronic obstructive pulmonary disease"),
    ("metabolic encephalopathy", "metabolic disease"),
    ("metabolic encephalopathy", "metabolic syndrome"),
    ("agranulocytosis secondary to cancer chemotherapy", "skin cancer"),
    ("secondary malignant neoplasm", "skin cancer"),
    ("genetic susceptibility to other malignant neoplasm", "skin cancer"),
    ("right bundle branch block", "brugada syndrome"),
    ("right bundlebranch block", "brugada syndrome"),
    ("bundle branch block", "brugada syndrome"),
    ("bundlebranch block", "brugada syndrome"),
    ("type 2 diabetes", "gestational diabetes"),
    ("type 1 diabetes", "gestational diabetes"),
    ("malignant primary neoplasm unspecified", "brain cancer"),
    ("squamous cell carcinoma of skin", "esophageal cancer"),
    ("diabetic neurological complication", "diabetic eye disease"),
    ("diabetic autonomic poly neuropathy", "diabetic eye disease"),
    ("diabetic autonomic polyneuropathy", "diabetic eye disease"),
    ("disorders of lipoprotein metabolism", "lipoprotein a measurement"),
    ("disorder of lipoprotein metabolism", "lipoprotein a measurement"),
    ("lipoprotein deficiency", "lipoprotein a measurement"),
    # Vitamin cross-matching (now stricter with alphanumeric tokenizing)
    ("vitamin d", "vitamin b12 deficiency"),
    ("vitamin b12", "vitamin d deficiency"),
    ("vitamin b12", "vitamin d measurement"),
    ("vitamin deficiency", "vitamin b12 deficiency"),
    ("vitamin deficiency", "vitamin d deficiency"),
    # Diabetes type mismatch
    ("type 1 diabetes", "type 2 diabetes"),
    ("type 2 diabetes", "type 1 diabetes"),
    ("type 1 diabetes", "type 2 diabetes mellitus"),
    ("type 2 diabetes", "type 1 diabetes mellitus"),
    # Vascular location mismatch
    ("atherosclerosis of aorta", "coronary atherosclerosis"),
    ("aortic atherosclerosis", "coronary atherosclerosis"),
    # Cancer subtype mismatch
    ("squamous cell carcinoma of skin", "head and neck squamous cell carcinoma"),
    # Nervous system mismatch
    ("symptoms and signs involving the nervous system", "peripheral nervous system disease"),
    ("degenerative disease of nervous system", "peripheral nervous system disease"),
    # White matter
    ("white matter disease", "white matter hyperintensity measurement"),
    # Device vs Complication
    ("dependence on other enabling machines and devices", "device complication"),
}

IDENTITY_CHANGING_PREFIXES = {
    "hypertension": {"portal", "pulmonary", "ocular", "intracranial", "secondary"},
    "diabetes": {"type 1", "type 2", "gestational"},
    "diabetes mellitus": {"type 1", "type 2", "gestational"},
}

# ---------------------------------------------------------------------------
# Cancer organ mapping: ICD "malignant neoplasm of X" -> clinical names
# ---------------------------------------------------------------------------
CANCER_ORGAN_MAP = {
    "breast": ["breast cancer", "breast carcinoma"],
    "thyroid": ["thyroid cancer", "thyroid carcinoma"],
    "colon": ["colon cancer", "colorectal cancer"],
    "lung": ["lung cancer", "lung carcinoma"],
    "kidney": ["kidney cancer", "renal cell carcinoma"],
    "ovary": ["ovarian cancer"],
    "ovaries": ["ovarian cancer"],
    "pancreas": ["pancreatic cancer"],
    "liver": ["liver cancer", "hepatocellular carcinoma"],
    "stomach": ["gastric cancer", "stomach cancer"],
    "brain": ["brain cancer", "glioma", "glioblastoma"],
    "cervix": ["cervical cancer"],
    "endometri": ["endometrial cancer"],
    "rectum": ["rectal cancer", "colorectal cancer"],
    "esophag": ["esophageal cancer"],
    "testis": ["testicular cancer"],
    "larynx": ["laryngeal cancer"],
    "bladder": ["urinary bladder cancer", "bladder cancer"],
    "uterus": ["uterine cancer", "endometrial cancer"],
}

# Direct cross-terminology synonym mappings
DIRECT_SYNONYM_MAP = {
    "cerebral infarction": ["ischemic stroke", "stroke"],
    "transient cerebral ischemic attack": ["transient ischemic attack"],
}

# ---------------------------------------------------------------------------
# Plural normalization for token matching
# ---------------------------------------------------------------------------
_PLURAL_MAP = {
    "veins": "vein", "arteries": "artery", "valves": "valve",
    "cells": "cell", "glands": "gland", "nerves": "nerve",
    "organs": "organ", "nodes": "node", "vessels": "vessel",
    "muscles": "muscle", "bones": "bone", "joints": "joint",
    "kidneys": "kidney", "lungs": "lung", "follicles": "follicle",
    "nodules": "nodule", "polyps": "polyp", "ulcers": "ulcer",
    "tumors": "tumor", "lesions": "lesion", "infections": "infection",
}

# Words that should NOT get trailing-s stripped
_SINGULAR_EXCEPTIONS = {
    "diabetes", "herpes", "rabies", "mumps", "measles", "meninges",
    "shingles", "rickets", "pertussis", "scabies",
}


def _singularize(word: str) -> str:
    """Normalize common medical plurals for token matching."""
    if word in _PLURAL_MAP:
        return _PLURAL_MAP[word]
    if word in _SINGULAR_EXCEPTIONS or len(word) < 5:
        return word
    # Strip trailing 's' for simple plurals, avoiding medical -sis/-tis/-tus
    if word.endswith("s") and not word.endswith(("sis", "tis", "tus", "ous", "ius")):
        return word[:-1]
    return word


def _normalize(s: str) -> str:
    """Normalize: lowercase, remove apostrophes and hyphens, collapse spaces."""
    s = s.lower().strip()
    # Remove apostrophes (Crohn's -> crohns, Hodgkin's -> hodgkins)
    s = s.replace("\u2019", "").replace("\u2018", "").replace("'", "")
    # Remove hyphens (gastro-esophageal -> gastroesophageal)
    s = s.replace("-", "")
    s = re.sub(r"[,;()\[\]]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _extract_aou_trait_name(raw: str) -> str:
    """Extract canonical trait name from AOU CSV (handles duplicated format)."""
    parts = re.split(r"\s{2,}", raw.strip())
    return parts[0].strip() if parts else raw.strip()


def _extract_core_name(name: str) -> str:
    """Strip ICD-10 modifiers to extract the core disease concept."""
    n = _normalize(name)
    # Remove common ICD-10 trailing qualifiers
    n = re.sub(r"\b(unspecified|not specified|nos)\b", "", n)
    n = re.sub(r"\b(right|left|bilateral|unilateral)\b", "", n)
    n = re.sub(r"\b(initial encounter|subsequent encounter|sequela)\b", "", n)
    n = re.sub(r"\b(w/o|without|with)\b", " ", n)
    # Additional ICD-10 modifiers
    n = re.sub(r"\b(intractable|not intractable|refractory)\b", "", n)
    n = re.sub(r"\bstatus (migrainosus|epilepticus)\b", "", n)
    n = re.sub(r"\b(complications?|complicated|uncomplicated)\b", "", n)
    n = re.sub(r"\b(nonruptured|ruptured|without rupture|with rupture)\b", "", n)
    n = re.sub(r"\bnot elsewhere classified\b", "", n)
    n = re.sub(r"\b(nec|spcf|recur)\b", "", n)
    n = re.sub(r"\b(due to|caused by|associated)\b", " ", n)
    n = re.sub(r"\b(acute|subacute)\b", "", n)
    # Remove site/body part qualifiers often seen in ICD
    n = re.sub(r"\b(site|region|area|unsp)\b", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def _tokenize(name: str) -> set[str]:
    """Tokenize a name into content words (stopwords removed, plurals normalized)."""
    # Keep hyphen as boundary for tokenization to avoid merged tokens
    # (e.g. "attention-deficit" -> "attention", "deficit").
    normalized = name.lower().strip()
    normalized = normalized.replace("\u2019", "").replace("\u2018", "").replace("'", "")
    normalized = normalized.replace("-", " ")
    normalized = re.sub(r"[,;()\[\]]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    # Include digits in words (e.g. type 2, vitamin b12)
    words = re.findall(r"[a-z0-9]+", normalized)
    tokens = set()
    for w in words:
        if w not in MEDICAL_STOPWORDS and len(w) > 1:  # Allow 2-char tokens like 'b12'
            tokens.add(_singularize(w))
    return tokens


def _is_disease_trait(trait: dict) -> bool:
    """
    Keep only disease-like PGS traits.
    We accept categories containing 'disease' or 'disorder', and 'cancer'.
    """
    categories = trait.get("trait_categories") or []
    if not categories:
        return False
    is_disease_category = False
    for cat in categories:
        c = (cat or "").strip().lower()
        if "disease" in c or "disorder" in c or c == "cancer":
            is_disease_category = True
            break
    if not is_disease_category:
        return False

    label_n = _normalize(trait.get("label") or "")
    if not label_n:
        return False
    if label_n in GENERIC_PGS_LABELS:
        return False
    for phrase in NON_DISEASE_LABEL_PHRASES:
        if phrase in label_n:
            return False

    label_tokens = set(re.findall(r"[a-z0-9]+", label_n))
    if label_tokens & NON_DISEASE_LABEL_TERMS:
        return False

    return True


def _overlap_coefficient(set_a: set, set_b: set) -> float:
    """Compute overlap coefficient: |A & B| / min(|A|, |B|)."""
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / min(len(set_a), len(set_b))


def _is_false_positive(aou_core: str, pgs_label: str) -> bool:
    """Check if a match is a known false positive."""
    aou_n = _normalize(aou_core)
    pgs_n = pgs_label.lower().strip()
    # Check strict pairs first
    for fp_aou, fp_pgs in FALSE_POSITIVE_PAIRS:
        if fp_aou in aou_n and fp_pgs == pgs_n:
            # Special check for diabetes type mismatch to be symmetrical
            if "type 1" in fp_aou and "type 2" in pgs_n: return True
            if "type 2" in fp_aou and "type 1" in pgs_n: return True
            return True
        # Reverse check for symmetric pairs
        if fp_aou in pgs_n and fp_pgs == aou_n:
            return True

    # Check prefix mismatches
    for base_term, bad_prefixes in IDENTITY_CHANGING_PREFIXES.items():
        if pgs_n == base_term:
            for prefix in bad_prefixes:
                if prefix in aou_n:
                    return True
    return False


def _generate_candidate_names(name: str) -> list[str]:
    """Generate alternative clinical names from ICD-style names."""
    n = _normalize(name)
    core = _normalize(_extract_core_name(name))
    candidates: list[str] = []

    # Cancer mapping: "malignant neoplasm of X" -> "X cancer/carcinoma"
    if "malignant neoplasm" in n:
        for organ_key, cancer_names in CANCER_ORGAN_MAP.items():
            if organ_key in n:
                candidates.extend(cancer_names)

    # Benign colon neoplasm subsite variants -> parent colon neoplasm trait.
    if "benign neoplasm" in n and "colon" in n:
        candidates.extend(["benign neoplasm of colon", "benign colon neoplasm"])

    # Direct cross-terminology mappings
    for key, vals in DIRECT_SYNONYM_MAP.items():
        if key in core:
            candidates.extend(vals)

    return candidates


# ---------------------------------------------------------------------------
# PGS Catalog API
# ---------------------------------------------------------------------------
def fetch_pgs_traits() -> list[dict]:
    """Fetch all traits from PGS Catalog REST API (paginated)."""
    all_traits: list[dict] = []
    next_url: str | None = f"{PGS_API_BASE}/trait/all?limit={PGS_PAGE_SIZE}"
    page = 0
    while next_url:
        page += 1
        print(f"  Fetching page {page}...", end=" ", flush=True)
        resp = requests.get(next_url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        all_traits.extend(results)
        print(f"got {len(results)} traits")
        next_url = data.get("next")
        if next_url and not next_url.startswith("http"):
            next_url = f"{PGS_API_BASE}{next_url}" if next_url.startswith("/") else None
    return all_traits


def build_pgs_index(traits: list[dict]) -> dict:
    """Build search indices from PGS traits."""
    by_label: dict[str, dict] = {}
    by_synonym: dict[str, dict] = {}
    all_names: list[tuple[str, dict, str]] = []
    for t in traits:
        label = t.get("label") or ""
        nlabel = _normalize(label)
        if nlabel:
            by_label[nlabel] = t
            all_names.append((nlabel, t, "label"))
        for syn in t.get("trait_synonyms") or []:
            nsyn = _normalize(syn)
            if nsyn and nsyn not in by_label:
                if nsyn not in by_synonym:
                    by_synonym[nsyn] = t
                all_names.append((nsyn, t, "synonym"))
    return {"by_label": by_label, "by_synonym": by_synonym, "all_names": all_names}


# ---------------------------------------------------------------------------
# AOU traits
# ---------------------------------------------------------------------------
def load_aou_traits() -> list[dict]:
    """Load All of Us traits from CSV."""
    rows: list[dict] = []
    with open(AOU_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_name = row.get("trait_name", "")
            name = _extract_aou_trait_name(raw_name)
            rows.append({
                "trait_name": name,
                "raw_trait_name": raw_name,
                "num_cases": row.get("num_cases"),
                "num_controls": row.get("num_controls"),
                "icd_children": row.get("icd_children"),
                "icd_root": row.get("icd_root"),
            })
    return rows


# ---------------------------------------------------------------------------
# Matching engine
# ---------------------------------------------------------------------------
def _try_exact(name_norm: str, pgs_index: dict, aou_raw: str,
               tier: str, fmt: str) -> tuple[dict, str, str, str, float] | None:
    """Try exact match against label or synonym index. Returns match tuple or None."""
    for key in ("by_label", "by_synonym"):
        if name_norm in pgs_index[key]:
            t = pgs_index[key][name_norm]
            if not _is_disease_trait(t):
                continue
            if not _is_false_positive(aou_raw, t.get("label", "")):
                src = "PGS label" if key == "by_label" else "PGS synonym"
                evidence = fmt.format(name_norm, src)
                return t, tier, evidence, CONFIDENCE_HIGH, 1.0
    return None


def match_trait(
    aou_name: str,
    pgs_index: dict,
) -> tuple[dict | None, str, str, str, float]:
    """
    Match an AOU trait name to a PGS trait.

    Returns: (pgs_trait_or_None, match_tier, match_evidence, confidence, similarity)

    confidence: HIGH / MEDIUM (categorical).
        HIGH   = exact match (label, synonym, core, or synonym_map)
        MEDIUM = token_overlap with overlap_coefficient >= 0.80

    similarity: continuous metric within tier:
        For exact tiers:  always 1.0
        For token_overlap: overlap_coefficient = |A & B| / min(|A|, |B|)
    """
    aou_norm = _normalize(aou_name)
    aou_core = _extract_core_name(aou_name)
    aou_core_norm = _normalize(aou_core)
    aou_tokens = _tokenize(aou_name)

    if not aou_norm:
        return None, "", "", "", 0.0

    # --- Tier 1: Exact normalized match ---
    m = _try_exact(aou_norm, pgs_index, aou_name,
                   "exact_label", "'{0}' == {1}")
    if m:
        # Determine if it was label or synonym for tier name
        if aou_norm in pgs_index["by_label"]:
            return m
        return (m[0], "exact_synonym", m[2], m[3], m[4])

    m = _try_exact(aou_norm, pgs_index, aou_name,
                   "exact_synonym", "'{0}' == {1}")
    if m:
        return m

    # --- Tier 1b: Exact match on core name ---
    if aou_core_norm != aou_norm:
        for key, tier_name in [("by_label", "exact_core"), ("by_synonym", "exact_core_syn")]:
            if aou_core_norm in pgs_index[key]:
                t = pgs_index[key][aou_core_norm]
                if not _is_disease_trait(t):
                    continue
                if not _is_false_positive(aou_name, t.get("label", "")):
                    src = "PGS label" if key == "by_label" else "PGS synonym"
                    evidence = f"core '{aou_core_norm}' == {src}"
                    return t, tier_name, evidence, CONFIDENCE_HIGH, 1.0

    # --- Tier 1c: Medical synonym mapping ---
    candidates = _generate_candidate_names(aou_name)
    for cand in candidates:
        cand_norm = _normalize(cand)
        for key, tier_name in [("by_label", "synonym_map"), ("by_synonym", "synonym_map")]:
            if cand_norm in pgs_index[key]:
                t = pgs_index[key][cand_norm]
                if not _is_disease_trait(t):
                    continue
                if not _is_false_positive(aou_name, t.get("label", "")):
                    src = "PGS label" if key == "by_label" else "PGS synonym"
                    evidence = f"synonym_map '{cand_norm}' == {src} (from '{aou_core_norm}')"
                    return t, tier_name, evidence, CONFIDENCE_HIGH, 1.0

    # --- Tier 2: Token-based overlap (minimum coeff 0.80) ---
    best_match: dict | None = None
    best_coeff = 0.0
    best_n = 0
    best_evidence = ""

    # Evaluate all label/synonym name variants and keep the best hit per PGS trait.
    best_by_trait: dict[str, tuple[float, int, dict, str]] = {}

    for pgs_name, pgs_trait, source in pgs_index["all_names"]:
        pgs_id = pgs_trait.get("id", "")
        pgs_label = (pgs_trait.get("label") or "").lower()
        if not _is_disease_trait(pgs_trait):
            continue

        if pgs_label in GENERIC_PGS_LABELS:
            continue
        if _is_false_positive(aou_name, pgs_label):
            continue

        pgs_tokens = _tokenize(pgs_name)
        if len(pgs_tokens) < 1:
            continue

        overlap = aou_tokens & pgs_tokens
        n_overlap = len(overlap)
        coeff = _overlap_coefficient(aou_tokens, pgs_tokens)

        # Require >= 2 content words OR 1 word with >= 6 chars
        min_words = 2
        if len(pgs_tokens) == 1:
            the_word = list(pgs_tokens)[0]
            if len(the_word) >= 6 and the_word in aou_tokens:
                min_words = 1
            else:
                continue

        if n_overlap >= min_words and coeff >= 0.80:
            # Single-token matches coming only from synonym text are noisy.
            if source == "synonym" and n_overlap == 1:
                continue

            if n_overlap == 1:
                only_token = next(iter(overlap))
                if only_token in AMBIGUOUS_SINGLE_TOKENS:
                    continue

            evidence = (
                f"tokens overlap: {overlap} "
                f"(coeff={coeff:.2f}, n={n_overlap}) "
                f"via {source} '{pgs_name}'"
            )
            existing = best_by_trait.get(pgs_id)
            if existing is None or (coeff, n_overlap) > (existing[0], existing[1]):
                best_by_trait[pgs_id] = (coeff, n_overlap, pgs_trait, evidence)

    if best_by_trait:
        best_coeff, best_n, best_match, best_evidence = max(
            best_by_trait.values(),
            key=lambda item: (item[0], item[1]),
        )
        return best_match, "token_overlap", best_evidence, CONFIDENCE_MEDIUM, best_coeff

    # No match found (fuzzy tier removed)
    return None, "", "", "", 0.0


def find_all_overlaps(
    aou_rows: list[dict],
    pgs_index: dict,
) -> tuple[list[dict], list[dict]]:
    """Find all AOU-PGS overlaps. Returns (matched, unmatched)."""
    matched: list[dict] = []
    unmatched: list[dict] = []

    for i, row in enumerate(aou_rows):
        name = row["trait_name"]
        pgs_trait, tier, evidence, confidence, similarity = match_trait(name, pgs_index)

        if pgs_trait:
            matched.append({
                "aou_trait_name": name,
                "aou_num_cases": row["num_cases"],
                "aou_num_controls": row["num_controls"],
                "aou_icd_children": row["icd_children"],
                "aou_icd_root": row["icd_root"],
                "pgs_id": pgs_trait.get("id", ""),
                "pgs_label": pgs_trait.get("label", ""),
                "pgs_categories": "|".join(pgs_trait.get("trait_categories") or []),
                "pgs_num_models": len(pgs_trait.get("associated_pgs_ids") or []),
                "match_tier": tier,
                "confidence": confidence,
                "similarity": f"{similarity:.3f}",
                "match_evidence": evidence,
            })
        else:
            unmatched.append({
                "aou_trait_name": name,
                "aou_num_cases": row["num_cases"],
                "aou_num_controls": row["num_controls"],
                "aou_icd_children": row["icd_children"],
                "aou_icd_root": row["icd_root"],
            })

        if (i + 1) % 200 == 0:
            print(f"  Processed {i + 1}/{len(aou_rows)} AOU traits...")

    return matched, unmatched


def deduplicate_by_root(matched: list[dict]) -> list[dict]:
    """Deduplicate by icd_root, keeping highest confidence then cases."""
    conf_rank = {CONFIDENCE_HIGH: 2, CONFIDENCE_MEDIUM: 1}
    root_best: dict[str, dict] = {}
    for row in matched:
        root = row["aou_icd_root"]
        rank = conf_rank.get(row["confidence"], 0)
        sim = float(row["similarity"])
        cases = int(row["aou_num_cases"])
        if root not in root_best:
            root_best[root] = row
        else:
            e_rank = conf_rank.get(root_best[root]["confidence"], 0)
            e_sim = float(root_best[root]["similarity"])
            e_cases = int(root_best[root]["aou_num_cases"])
            if (rank, sim, cases) > (e_rank, e_sim, e_cases):
                root_best[root] = row
    return sorted(root_best.values(), key=lambda r: int(r["aou_num_cases"]), reverse=True)


def deduplicate_by_pgs(matched: list[dict]) -> list[dict]:
    """Aggregate by pgs_id (PGS trait-centric view)."""
    conf_rank = {CONFIDENCE_HIGH: 2, CONFIDENCE_MEDIUM: 1}
    pgs_groups: dict[str, list[dict]] = {}
    for row in matched:
        pid = row["pgs_id"]
        if pid not in pgs_groups:
            pgs_groups[pid] = []
        pgs_groups[pid].append(row)

    results: list[dict] = []
    for pid, rows in pgs_groups.items():
        roots = sorted({r["aou_icd_root"] for r in rows})
        best_row = max(
            rows,
            key=lambda r: (
                conf_rank.get(r["confidence"], 0),
                float(r["similarity"]),
                int(r["aou_num_cases"]),
            ),
        )
        max_cases = max(int(r["aou_num_cases"]) for r in rows)
        total_cases = sum(int(r["aou_num_cases"]) for r in rows)
        results.append({
            "pgs_id": pid,
            "pgs_label": best_row["pgs_label"],
            "pgs_categories": best_row["pgs_categories"],
            "pgs_num_models": best_row["pgs_num_models"],
            "n_aou_roots": len(roots),
            "aou_roots": "|".join(roots),
            "max_aou_cases": max_cases,
            "total_aou_cases": total_cases,
            "best_confidence": best_row["confidence"],
            "best_similarity": best_row["similarity"],
            "best_match_tier": best_row["match_tier"],
            "best_aou_trait": best_row["aou_trait_name"],
            "match_evidence": best_row["match_evidence"],
        })
    results.sort(key=lambda r: r["total_aou_cases"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
MATCHED_FIELDS = [
    "aou_trait_name", "aou_num_cases", "aou_num_controls",
    "aou_icd_children", "aou_icd_root",
    "pgs_id", "pgs_label", "pgs_categories", "pgs_num_models",
    "match_tier", "confidence", "similarity", "match_evidence",
]
PGS_FIELDS = [
    "pgs_id", "pgs_label", "pgs_categories", "pgs_num_models",
    "n_aou_roots", "aou_roots", "max_aou_cases", "total_aou_cases",
    "best_confidence", "best_similarity", "best_match_tier",
    "best_aou_trait", "match_evidence",
]
UNMATCHED_FIELDS = [
    "aou_trait_name", "aou_num_cases", "aou_num_controls",
    "aou_icd_children", "aou_icd_root",
]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  Wrote {len(rows)} rows -> {path}")


def print_summary(
    aou_rows: list[dict],
    matched: list[dict],
    unmatched: list[dict],
    deduped_root: list[dict],
    deduped_pgs: list[dict],
) -> None:
    print("\n" + "=" * 70)
    print("OVERLAP SUMMARY")
    print("=" * 70)

    # Primary metric: PGS traits
    print("\n  [PRIMARY] PGS Catalog traits with AOU overlap:")
    conf_pgs: dict[str, int] = {}
    for row in deduped_pgs:
        c = row["best_confidence"]
        conf_pgs[c] = conf_pgs.get(c, 0) + 1
    print(f"    Total unique PGS traits:     {len(deduped_pgs)}")
    for conf in [CONFIDENCE_HIGH, CONFIDENCE_MEDIUM]:
        print(f"      {conf:8s}: {conf_pgs.get(conf, 0):>4d}")

    print(f"\n  [SECONDARY] AOU icd_root codes:")
    print(f"    Total unique icd_roots:      {len(deduped_root)}")

    print(f"\n  [RAW] Row-level counts:")
    print(f"    AOU traits loaded:           {len(aou_rows)}")
    print(f"    AOU traits matched:          {len(matched)}")
    print(f"    AOU traits unmatched:        {len(unmatched)}")

    # Confidence breakdown by icd_root
    conf_root: dict[str, int] = {}
    for row in deduped_root:
        c = row["confidence"]
        conf_root[c] = conf_root.get(c, 0) + 1
    print("\n  Confidence breakdown (by icd_root):")
    for conf in [CONFIDENCE_HIGH, CONFIDENCE_MEDIUM]:
        print(f"    {conf:8s}: {conf_root.get(conf, 0):>4d}")

    # Match tier breakdown
    tier_counts: dict[str, int] = {}
    for row in deduped_root:
        t = row["match_tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1
    print("\n  Match tier breakdown (by icd_root):")
    for t in sorted(tier_counts.keys()):
        print(f"    {t:20s}: {tier_counts[t]:>4d}")

    # Category distribution (by PGS trait)
    cat_counts: dict[str, int] = {}
    for row in deduped_pgs:
        cats = row["pgs_categories"].split("|") if row["pgs_categories"] else ["Unknown"]
        for cat in cats:
            cat = cat.strip()
            if cat:
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
    print("\n  Disease category distribution (by PGS trait):")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat:35s}: {cnt:>4d}")

    print("=" * 70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 70)
    print("AOU x PGS Catalog Trait Overlap (v5 - alphanumeric tokenizing)")
    print("=" * 70)

    print("\n[1/5] Fetching PGS Catalog traits...")
    pgs_traits = fetch_pgs_traits()
    print(f"  Total PGS traits: {len(pgs_traits)}")

    print("\n[2/5] Loading All of Us traits...")
    aou_rows = load_aou_traits()
    print(f"  Total AOU traits: {len(aou_rows)}")

    print("\n[3/5] Building PGS index...")
    pgs_index = build_pgs_index(pgs_traits)
    print(f"  PGS label entries:   {len(pgs_index['by_label'])}")
    print(f"  PGS synonym entries: {len(pgs_index['by_synonym'])}")
    print(f"  Total name entries:  {len(pgs_index['all_names'])}")

    print("\n[4/5] Computing overlap...")
    matched, unmatched = find_all_overlaps(aou_rows, pgs_index)

    print("\n[5/5] Deduplicating...")
    deduped_root = deduplicate_by_root(matched)
    deduped_pgs = deduplicate_by_pgs(matched)

    print("\nWriting output files...")
    write_csv(OUTPUT_CSV, matched, MATCHED_FIELDS)
    write_csv(OUTPUT_ROOT_CSV, deduped_root, MATCHED_FIELDS)
    write_csv(OUTPUT_PGS_CSV, deduped_pgs, PGS_FIELDS)
    write_csv(OUTPUT_NO_MATCH_CSV, unmatched, UNMATCHED_FIELDS)

    print_summary(aou_rows, matched, unmatched, deduped_root, deduped_pgs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
