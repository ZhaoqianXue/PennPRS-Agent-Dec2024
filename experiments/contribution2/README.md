# Contribution2: LLM-Based PRS Model Selection

This module advances Contribution2 of the PennPRS Agent paper: understanding how GPT uses captured PRS model features (sample size, ancestry, method, training cohort, etc.) to select optimal models.

## Folder Structure (per `.agent/rules/rules.md`)

```
contribution2/
├── configs/          # Experiment configurations (select_diseases_contribution2.py)
├── runs/             # Results and logs (selected diseases, reports)
├── metrics/          # Performance metric records (full metrics)
├── analysis/         # Result analysis scripts
└── README.md
```

## Disease Selection (Step 1)

Before evaluating the Agent, we select a set of diseases from the All of Us benchmark (Contribution1) based on three criteria.

### Data Source

- **AUC Matrix**: `../contribution1/result/aou_icd_260217/prs_adjauc_matrix_260217_rootcode.csv`
- **Metadata**: `../contribution1/result/aou_icd_260217/prs_adjauc_metadata_260217_rootcode.csv`

### Selection Criteria

| Criterion | Definition | Threshold |
|-----------|------------|-----------|
| **1. Top vs Rest Distinguishability** | Any cliff in top tier | Any of (T1, T2, T3 vs Rest) >= 0.02 |
| **1b. Top-1 AUC Floor** | Best model must perform reasonably | Top-1 AUC >= 0.55 |
| **2. Overall AUC Level** | Candidate models should perform reasonably | Mean AUC across all models >= 0.52 |
| **3. Genetic Significance** | Disease has genetic epidemiology relevance, not niche | Whitelist + exclusion list |

### Top vs Rest Gaps (Three Metrics)

- **Top-1 vs Rest**: Top-1 AUC - max(Rest AUC) = Top-1 - Top-2.
- **Top-2 vs Rest**: Top-2 AUC - max(Rest AUC) = Top-2 - Top-3.
- **Top-3 vs Rest**: Top-3 AUC - max(Rest AUC) = Top-3 - Top-4.

C1: pass if any of (T1 vs Rest, T2 vs Rest, T3 vs Rest) >= 0.02. Top-1 floor >= 0.55.

### Outputs (per `rules.md` experiments structure)

| Path | Description |
|------|--------------|
| `runs/selected_diseases_contribution2.csv` | Final selected diseases (rootcode, one per ICD root) |
| `runs/selected_diseases_contribution2_childrencode.csv` | Final selected diseases (childrencode) |
| `runs/disease_selection_report.md` | Rootcode report |
| `runs/disease_selection_report_childrencode.md` | Childrencode report |
| `metrics/disease_selection_full_metrics.csv` | Full metrics for all ontologies (rootcode) |
| `metrics/disease_selection_full_metrics_childrencode.csv` | Full metrics (childrencode) |

### Running the Selection

```bash
# Rootcode (default)
python configs/select_diseases_contribution2.py

# Childrencode
python configs/select_diseases_contribution2.py --childrencode
```

### Selected Diseases (25)

Per SOP categories: **cancer** (breast, prostate, lung, ovarian, thyroid, renal, melanoma, skin, her2-negative breast), **mental** (bipolar disorder, MDD, dementia), **neurodegenerative** (Alzheimer's, Parkinson's), **heart** (heart failure, myocardial infarction, atrial fibrillation), plus metabolic (obesity), autoimmune (lupus, ankylosing spondylitis), thyroid (Hashimoto's, Graves, hypothyroidism), gout, glaucoma.
