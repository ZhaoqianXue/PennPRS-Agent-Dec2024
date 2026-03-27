"""
Manual mapping from cross-list ontology names to GWAS Atlas uniqTrait.

Some cross-list diseases have no direct GWAS Atlas match (marked as None).
These will have rg-only graphs with 0 neighbors.
"""

# ICD -> best GWAS Atlas uniqTrait match (or None if no match)
CROSS_LIST_TO_GWAS_ATLAS: dict[str, str | None] = {
    # --- 41 beats_self diseases ---
    "G301": "Alzheimer disease",
    "M0579": "Rheumatoid Arthritis",
    "N40": None,  # benign prostatic hyperplasia: no match (prostate cancer is different)
    "C54": None,  # endometrial cancer: no GWAS Atlas entry
    "F4310": None,  # PTSD: no direct match
    "B02": None,  # herpes zoster: no direct match
    "I2781": None,  # cor pulmonale: no match
    "J439": None,  # emphysema: no direct match (COPD not in GWAS Atlas either)
    "S52502A": "Bone mineral density",  # radius fracture -> BMD as proxy
    "I219": "Coronary artery disease",  # acute MI -> CAD
    "N049": "Childhood idiopathic nephrotic syndrome",
    "D259": None,  # uterine fibroid: no match
    "Q742": None,  # congenital limb deformities: no match
    "F0390": None,  # dementia: not in GWAS Atlas (Alzheimer is, but dementia is different)
    "F3181": "Bipolar disorder",
    "L4050": "Psoriasis",  # psoriatic arthritis -> Psoriasis
    "J300": "Hayfever/Allergic Rhinitis",  # vasomotor rhinitis -> allergic rhinitis
    "L281": "Eczema",  # prurigo nodularis -> Eczema as closest
    "D04": "Carcinoma in situ",  # skin carcinoma in situ
    "L0390": None,  # cellulitis: no match
    "C56": "Epithelial ovarian cancer",
    "G4752": None,  # REM sleep behavior disorder: no match
    "M47816": "Ankylosing spondylitis",  # spondylosis -> AS (closest spinal)
    "J33": None,  # nasal polyp: no match
    "G589": None,  # mononeuropathy: no match
    "N189": "Chronic kidney disease",
    "E8881": None,  # metabolic syndrome: no match
    "D649": None,  # anemia: no direct disease match (only hemoglobin measurements)
    "G40909": "Epilepsy",
    "I49": "Atrial fibrillation",  # Brugada/arrhythmia -> AF
    "M35": None,  # polymyalgia rheumatica: no match
    "F90": "Attention deficit hyperactivity disorder",
    "D689": None,  # blood coagulation disease: no direct match
    "C4492": "Squamous cell",  # squamous cell carcinoma
    "E83": None,  # iron metabolism disease: no disease match (only measurements)
    "N02": None,  # IgA glomerulonephritis: no match
    "E0590": "Hyperthyroidism",  # thyrotoxicosis -> hyperthyroidism
    "R9431": None,  # abnormal EKG: no match
    "I5032": "Heart failure",
    "I4892": "Atrial fibrillation",  # atrial flutter -> AF
    "I24": "Coronary artery disease",  # MI -> CAD
    # --- 11 no_self_auc diseases ---
    "B079": None,  # common wart: no match
    "E271": None,  # adrenal insufficiency: no match
    "F209": "Schizophrenia",
    "H209": None,  # iritis: no match
    "H33001": None,  # retinal break: no match
    "I8390": None,  # varicose veins: no match
    "L559": None,  # sunburn: no match
    "L821": None,  # seborrheic keratosis: no match
    "R55": None,  # syncope: no match
    "M34": None,  # systemic scleroderma: no direct match
    "M93": None,  # slipped epiphyses: no match
}

# Count stats
_mapped = sum(1 for v in CROSS_LIST_TO_GWAS_ATLAS.values() if v is not None)
_unmapped = sum(1 for v in CROSS_LIST_TO_GWAS_ATLAS.values() if v is None)
# 22 mapped, 30 unmapped
