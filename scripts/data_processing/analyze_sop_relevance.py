#!/usr/bin/env python3
"""
Analyze which pgs_labels in aou_pgs_trait_overlap_by_pgs.csv are unrelated to
the four disease categories specified in sop.md lines 17-18:
- cancer
- mental diseases
- neurodegenerative diseases
- heart diseases
"""

import csv
from pathlib import Path

# Disease categories from sop.md:17-18
SOP_CATEGORIES = {
    "cancer": {
        "keywords": ["carcinoma", "cancer", "melanoma", "lymphoma", "neoplasm", "malignant"],
        "explicit": ["breast carcinoma", "basal cell carcinoma", "prostate cancer", "thyroid carcinoma",
                     "endometrial cancer", "squamous cell carcinoma", "lung cancer", "cutaneous melanoma",
                     "urinary bladder cancer", "non-hodgkins lymphoma", "colon carcinoma", "skin cancer"],
        # PGS Catalog labels as Cancer but medically NOT cancer:
        "exclude": ["epidermal inclusion cyst", "common wart", "uterine fibroid", "pulmonary fibrosis"],
    },
    "mental": {
        "keywords": ["depressive", "depression", "anxiety", "schizophrenia", "bipolar", "adhd",
                     "attention deficit", "post-traumatic stress", "ptsd", "nicotine dependence",
                     "alcohol dependence", "eating disorder"],
        "explicit": ["anxiety disorder", "major depressive disorder", "depressive disorder",
                     "post-traumatic stress disorder", "nicotine dependence", "alcohol dependence",
                     "attention deficit hyperactivity disorder", "bipolar disorder", "bipolar ii disorder",
                     "eating disorder", "schizophrenia"],
    },
    "neurodegenerative": {
        "keywords": ["dementia", "parkinson", "alzheimer", "multiple sclerosis", "macular degeneration",
                     "neurodegenerative"],
        "explicit": ["dementia", "parkinson disease", "multiple sclerosis", "macular degeneration",
                     "age-related macular degeneration"],
        # Neurological but NOT neurodegenerative (headache, sleep, epilepsy, etc.):
        "exclude": ["headache", "headache disorder", "migraine", "insomnia", "sleep apnea",
                    "obstructive sleep apnea", "sleep disorder", "deafness", "hearing loss", "epilepsy",
                    "peripheral nervous system disease"],
    },
    "heart": {
        "keywords": ["heart", "cardiovascular", "cardiac", "myocardial", "atrial", "stroke",
                     "hypertension", "angina", "cardiomyopathy", "atherosclerosis", "embolism",
                     "aneurysm", "coronary", "aortic", "mitral", "cerebrovascular", "syncope"],
        "explicit": ["essential hypertension", "angina pectoris", "atrial fibrillation",
                     "congestive heart failure", "myocardial infarction", "heart failure",
                     "aortic valve disease", "peripheral vascular disease", "cardiomyopathy",
                     "atrial flutter", "ischemic stroke", "cerebrovascular disorder",
                     "aortic stenosis", "coronary atherosclerosis", "mitral valve prolapse",
                     "myocardial ischemia", "coronary artery disease", "pulmonary embolism",
                     "abdominal aortic aneurysm", "dilated cardiomyopathy", "brain aneurysm",
                     "acute myocardial infarction"],
        # Vascular but not heart disease:
        "exclude": ["hemorrhoid", "varicose veins"],
    },
}


def normalize_label(label: str) -> str:
    return label.strip().lower()


def is_related_to_category(label: str, category: str) -> bool:
    """Check if pgs_label is related to the given category."""
    norm = normalize_label(label)
    cat = SOP_CATEGORIES[category]

    # Explicit exclusions for this category (if any)
    exclude_list = cat.get("exclude", [])
    if any(norm == ex for ex in exclude_list):
        return False

    # Explicit matches
    if any(norm == ex for ex in cat["explicit"]):
        return True

    # Keyword matches
    for kw in cat["keywords"]:
        if kw in norm:
            return True

    return False


def is_related_to_any_sop_category(label: str) -> bool:
    """Check if pgs_label is related to any of the four SOP categories."""
    for cat in SOP_CATEGORIES:
        if is_related_to_category(label, cat):
            return True
    return False


# Extended categories for all traits (no "unrelated" - every trait gets a category)
# Check order matters: more specific first
EXTENDED_CATEGORIES = [
    # SOP focus categories (priority)
    ("cancer", lambda n: _match_cancer(n)),
    ("mental", lambda n: _match_mental(n)),
    ("neurodegenerative", lambda n: _match_neurodegenerative(n)),
    ("heart", lambda n: _match_heart(n)),
    # Other disease categories
    ("digestive", lambda n: any(k in n for k in [
        "gastritis", "reflux", "esophagitis", "barrett", "duodenitis", "duodenal ulcer",
        "celiac", "crohn", "colitis", "polyp", "appendicitis", "liver", "cirrhosis",
        "biliary", "gastroesophageal"
    ])),
    ("metabolic", lambda n: any(k in n for k in [
        "diabetes", "obesity", "gout", "metabolic syndrome", "bilirubin", "vitamin b12"
    ])),
    ("renal", lambda n: any(k in n for k in [
        "kidney", "nephrolithiasis", "ureterolithiasis", "urinary tract", "urinary system"
    ])),
    ("autoimmune", lambda n: any(k in n for k in [
        "lupus", "rheumatoid arthritis", "sjogren", "hashimoto", "psoriatic arthritis"
    ])),
    ("musculoskeletal", lambda n: any(k in n for k in [
        "osteoarthritis", "arthritis", "spondylosis", "osteoporosis", "polymyalgia",
        "intervertebral disc", "ganglion", "synovium", "tendon", "bursa"
    ])),
    ("ophthalmology", lambda n: any(k in n for k in [
        "cataract", "glaucoma", "retinopathy"
    ])),
    ("dermatology", lambda n: any(k in n for k in [
        "dermatitis", "eczema", "psoriasis", "seborrheic keratosis", "cellulitis",
        "follicular cyst", "epidermal inclusion cyst", "common wart", "keratosis"
    ])),
    ("respiratory", lambda n: any(k in n for k in [
        "asthma", "rhinitis", "copd", "emphysema", "pulmonary fibrosis", "nasal polyp",
        "obstructive pulmonary", "chronic obstructive pulmonary"
    ])),
    ("infectious", lambda n: any(k in n for k in [
        "covid", "herpes", "zoster", "respiratory tract infectious"
    ])),
    ("endocrine", lambda n: any(k in n for k in [
        "hypothyroidism", "goiter", "thyrotoxicosis", "thyroiditis", "adrenal"
    ])),
    ("neurological", lambda n: any(k in n for k in [
        "headache", "migraine", "insomnia", "sleep apnea", "sleep disorder",
        "deafness", "hearing loss", "epilepsy", "peripheral nervous", "neuropathy"
    ])),
    ("hematology", lambda n: any(k in n for k in [
        "anemia", "coagulation"
    ])),
    ("gynecology", lambda n: any(k in n for k in [
        "endometriosis", "prolapse of female genital", "uterine fibroid"
    ])),
    ("urology", lambda n: any(k in n for k in ["prostatic hyperplasia", "benign prostatic"])),
    ("vascular", lambda n: any(k in n for k in [
        "hemorrhoid", "varicose veins"
    ])),
    ("drug_allergy", lambda n: "drug allergy" in n),
]


def _match_cancer(n: str) -> bool:
    exclude = ["epidermal inclusion cyst", "common wart", "uterine fibroid", "pulmonary fibrosis"]
    if n in exclude:
        return False
    return any(k in n for k in ["carcinoma", "cancer", "melanoma", "lymphoma", "neoplasm", "malignant"])


def _match_mental(n: str) -> bool:
    return any(k in n for k in [
        "depressive", "depression", "anxiety", "schizophrenia", "bipolar",
        "attention deficit", "post-traumatic stress", "ptsd", "nicotine dependence",
        "alcohol dependence", "eating disorder"
    ])


def _match_neurodegenerative(n: str) -> bool:
    exclude = ["headache", "headache disorder", "migraine", "insomnia", "sleep apnea",
              "obstructive sleep apnea", "sleep disorder", "deafness", "hearing loss",
              "epilepsy", "peripheral nervous system disease"]
    if n in exclude:
        return False
    return any(k in n for k in ["dementia", "parkinson", "multiple sclerosis", "macular degeneration"])


def _match_heart(n: str) -> bool:
    exclude = ["hemorrhoid", "varicose veins"]
    if n in exclude:
        return False
    return any(k in n for k in [
        "heart", "cardiovascular", "myocardial", "atrial", "stroke", "hypertension",
        "angina", "cardiomyopathy", "atherosclerosis", "embolism", "aneurysm",
        "coronary", "aortic", "mitral", "cerebrovascular", "syncope", "peripheral vascular"
    ])


def get_sop_label(label: str) -> str:
    """
    Get category label for a pgs_label. Every trait gets a category.
    Returns one of: cancer, mental, neurodegenerative, heart, digestive, metabolic,
    renal, musculoskeletal, ophthalmology, dermatology, respiratory, infectious,
    endocrine, neurological, autoimmune, hematology, gynecology, vascular, drug_allergy.
    """
    norm = normalize_label(label)
    for cat, matcher in EXTENDED_CATEGORIES:
        if matcher(norm):
            return cat
    return "other"


def add_label_column_to_csv():
    """Add/update label column in aou_pgs_trait_overlap_by_pgs.csv."""
    csv_path = Path(__file__).parent.parent.parent / "data" / "all_of_us" / "aou_pgs_trait_overlap_by_pgs.csv"
    label_col = "label"

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_fieldnames = reader.fieldnames
        rows = list(reader)

    # Dedupe columns: keep first occurrence only
    seen = set()
    fieldnames = []
    for f in raw_fieldnames:
        if f not in seen:
            seen.add(f)
            fieldnames.append(f)

    # Ensure single label column after pgs_label
    fieldnames = [f for f in fieldnames if f != label_col]
    if "pgs_label" in fieldnames:
        idx = fieldnames.index("pgs_label") + 1
        fieldnames.insert(idx, label_col)
    else:
        fieldnames.append(label_col)

    for row in rows:
        row[label_col] = get_sop_label(row["pgs_label"])

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    print(f"Updated column '{label_col}' in {csv_path}")


def main():
    csv_path = Path(__file__).parent.parent.parent / "data" / "all_of_us" / "aou_pgs_trait_overlap_by_pgs.csv"
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    pgs_labels = [r["pgs_label"] for r in rows]
    related = []
    unrelated = []

    for label in pgs_labels:
        if is_related_to_any_sop_category(label):
            related.append(label)
        else:
            unrelated.append(label)

    print("=" * 60)
    print("SOP.md lines 17-18: cancer, mental diseases, neurodegenerative diseases, heart diseases")
    print("=" * 60)
    print(f"\nTotal pgs_labels: {len(pgs_labels)}")
    print(f"Related to at least one SOP category: {len(related)}")
    print(f"UNRELATED (almost no overlap): {len(unrelated)}")
    print("\n" + "-" * 60)
    print("UNRELATED pgs_labels (sorted):")
    print("-" * 60)
    for l in sorted(unrelated):
        print(f"  - {l}")
    print("\n" + "-" * 60)
    print("RELATED pgs_labels (for reference):")
    print("-" * 60)
    for l in sorted(related):
        cats = [c for c in SOP_CATEGORIES if is_related_to_category(l, c)]
        print(f"  - {l} [{', '.join(cats)}]")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--add-label":
        add_label_column_to_csv()
    else:
        main()
