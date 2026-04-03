# Rootcode vs Childrencode Selection Comparison

## Scope

This comparison reflects the current default code path in `select_diseases_contribution2.py`:

- `min_n_models = 2`
- `QC1`: pass if any of `T1..T5 vs Rest >= 0.025`
- `QC2`: exact curated exception allowlist hard-add; non-match is neutral
- blacklist still applies as hard exclusion
- rootcode dedup by `icd_root`, preferring higher `n_with_auc`, then higher `max_auc`

## Summary

| Metric | Rootcode | Childrencode |
|--------|----------|--------------|
| Final selected rows (after QC3) | 56 | 67 |
| QC1=Yes rows in final output | 28 | 41 |
| QC2 allowlist rows in final output | 28 | 26 |
| QC2-only rows (`QC1=No`, `QC2=Yes`) | 28 | 26 |
| Unique ICD roots in final output | 56 | 58 |
| Raw ontology union across both outputs | \- | 74 |
| Canonical merged union across both selected outputs | \- | 67 |

## Key Differences

### 1. Childrencode now outputs 11 more rows and covers 2 more ICD roots

Under the current exact-match QC2 logic, childrencode keeps 67 rows versus 56 for rootcode. After collapsing to ICD roots, childrencode now covers 58 unique roots versus 56 for rootcode. The extra childrencode rows are therefore a mix of subtype expansions and genuinely broader root coverage.

### 2. QC2 allowlist still contributes a large share of the final output

QC2 contributes 28 rows in rootcode and 26 rows in childrencode. All of these QC2 rows are `QC2-only`, meaning they would not be kept by QC1 alone.

### 3. ICD roots only in Rootcode (8)

| ICD Root | Ontology |
|----------|----------|
| C50 | Breast carcinoma |
| C62 | Testicular carcinoma |
| C91 | Acute lymphoblastic leukemia |
| H80 | Otosclerosis |
| I24 | Myocardial infarction |
| M08 | Juvenile idiopathic arthritis |
| N18 | Chronic kidney disease |
| O14 | Preeclampsia |

### 4. ICD roots only in Childrencode (10)

| ICD Root | Selected child code | Ontology |
|----------|---------------------|----------|
| C54 | C541 | Uterine carcinoma |
| E83 | E8319 | Iron metabolism disease |
| G30 | G301 | Late-onset Alzheimer's disease |
| G47 | G4733 | Sleep apnea; Obstructive sleep apnea |
| H18 | H1851 | Corneal dystrophy |
| H35 | H353131 | Age-related macular degeneration |
| I73 | I739 | Peripheral vascular disease |
| J84 | J84112 | Idiopathic pulmonary fibrosis |
| L20 | L2084 | Atopic eczema |
| M72 | M720 | Dupuytren contracture |

### 5. Shared ICD roots still expand into ontology-label splits

Representative raw splits:

| ICD Root | Rootcode ontology | Childrencode ontology |
|----------|-------------------|------------------------|
| C43 | Melanoma | Cutaneous melanoma; Melanoma |
| C61 | Prostate cancer | Prostate cancer; Prostate carcinoma |
| C64 | Kidney cancer | Kidney cancer; Renal carcinoma |
| H40 | Glaucoma | Glaucoma; Open-angle glaucoma |
| I21 | Acute myocardial infarction | Acute myocardial infarction; Myocardial infarction |
| I42 | Dilated cardiomyopathy | Dilated cardiomyopathy; Hypertrophic cardiomyopathy |
| I48 | Atrial fibrillation | Atrial fibrillation; Atrial flutter |
| L40 | Psoriasis | Psoriasis; Psoriatic arthritis |

Applying the canonical merge map to these selected outputs reduces the raw `74`-disease union to `67`. Separately, the broader current-method union builder used elsewhere in the pipeline now yields `76` diseases because it keeps QC1 as a diagnostic column and gates only on QC3 plus blacklist handling.

## Usage

```bash
# Rootcode (default)
python experiments/contribution2/disease_selection/configs/select_diseases_contribution2.py

# Childrencode
python experiments/contribution2/disease_selection/configs/select_diseases_contribution2.py --childrencode

# Canonicalized current-method union
python experiments/contribution2/disease_selection/configs/build_current_method_union.py

# Legacy base eligibility
python experiments/contribution2/disease_selection/configs/select_diseases_contribution2.py --min-n-models 3
python experiments/contribution2/disease_selection/configs/build_current_method_union.py --min-n-models 3
```

## Output Files

| Rootcode | Childrencode |
|----------|--------------|
| `runs/intermediate/selected_diseases_contribution2.csv` | `runs/intermediate/selected_diseases_contribution2_childrencode.csv` |
| `metrics/disease_selection_full_metrics.csv` | `metrics/disease_selection_full_metrics_childrencode.csv` |
| `runs/disease_selection_report.md` | `runs/disease_selection_report_childrencode.md` |
