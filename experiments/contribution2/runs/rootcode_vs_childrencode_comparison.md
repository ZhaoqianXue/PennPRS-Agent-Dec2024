# Rootcode vs Childrencode Selection Comparison

## Summary

| Metric | Rootcode | Childrencode |
|--------|----------|--------------|
| **Final selected (dedup by ICD root)** | 45 | 51 |
| QC1 pass (T1..T5 vs Rest ≥ 0.025) | 33 | 37 |
| QC2 pass (genetic significance) | 58 | 56 |
| QC3 pass (Mean AUC ≥ 0.5 & Top-1 ≥ 0.55) | 85 | 95 |
| QC1=Yes in final selected | 21 | 35 |
| QC1=No in final selected | 24 | 16 |

## Key Differences

### 1. Childrencode selects 6 more diseases (51 vs 45)

Childrencode yields more unique ICD roots because it operates on finer-grained phenotypes (ICD children codes). Different children under the same root can have different AUC profiles; when deduplicating by root, childrencode may keep a different child (e.g., a subtype with stronger PRS performance) than rootcode, which aggregates at the root level.

### 2. More QC1=Yes in childrencode (35 vs 21)

Childrencode shows stronger top-model distinguishability (Tk vs Rest ≥ 0.025) in the final set. Sub-phenotypes often have steeper AUC cliffs than aggregated root phenotypes.

### 3. ICD roots only in Rootcode (4)

| ICD | Ontology |
|-----|----------|
| C62 | Testicular neoplasm |
| M08 | Juvenile idiopathic arthritis |
| N18 | Chronic kidney disease |
| O14 | Preeclampsia |

### 4. ICD roots only in Childrencode (10)

| ICD | Ontology |
|-----|----------|
| C54 | Uterine carcinoma |
| E11 | Diabetic eye disease |
| G30 | Late-onset Alzheimer's disease |
| G47 | Sleep apnea |
| H18 | Corneal disease |
| H35 | Age-related macular degeneration |
| I42 | Hypertrophic cardiomyopathy |
| I73 | Peripheral vascular disease |
| L20 | Atopic eczema |
| M72 | Dupuytren contracture |

### 5. Ontology / subtype differences (same ICD root, both selected)

| ICD | Rootcode ontology | Childrencode ontology |
|-----|-------------------|------------------------|
| I25 | Coronary atherosclerosis | Coronary artery disease |
| H40 | Glaucoma | Open-angle glaucoma |

## Usage

```bash
# Rootcode (default)
python experiments/contribution2/configs/select_diseases_contribution2.py

# Childrencode
python experiments/contribution2/configs/select_diseases_contribution2.py --childrencode
```

## Output Files

| Rootcode | Childrencode |
|----------|--------------|
| selected_diseases_contribution2.csv | selected_diseases_contribution2_childrencode.csv |
| disease_selection_full_metrics.csv | disease_selection_full_metrics_childrencode.csv |
| disease_selection_report.md | disease_selection_report_childrencode.md |
