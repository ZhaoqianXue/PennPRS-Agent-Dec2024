# Cross-Trait Transfer Benchmark Report

## Selection Rules

| Scenario | Rule |
|----------|------|
| Type A target | No self AUC benchmark is available. Keep it only if at least one cross disease/trait reaches AUC > 0.55. |
| Type B target | A self AUC benchmark is available. Keep it only if self AUC < 0.60 and at least 1 cross disease/trait beats self by more than 0.025 AUC. |
| All targets: clustering requirement | Sort cross diseases/traits by AUC, compute all adjacent gaps `AUC_k - AUC_(k+1)`, and require `best_split_gap >= 0.025`. |
| All selected targets | The top cross disease/trait must still reach AUC > 0.55. |

## Binary-to-Binary

- Screened target traits: **125** (Type A: 4, Type B: 121)
- **Selected for benchmark: 9** (Type A: 1, Type B: 8)

### Selected Targets (Binary-to-Binary)

| ICD | Description | Type | Qualifying Diseases | Top Self AUC | Top Cross AUC | Top Cross Name | Top Improvement | Best Split | Best Gap |
|-----|-------------|------|---------------------|--------------|---------------|----------------|-----------------|------------|----------|
| N40 | Benign prostatic hyperplasia without low | B | 2 / 128 | 0.5236 | 0.6423 | Malignant neoplasm of prostate / Inflammatory disease of pro | +0.1186 | Top-2 | 0.0998 |
| M05 | Rheumatoid arthritis | B | 7 / 128 | 0.5559 | 0.6595 | Gout / Unspecified osteoarthritis | +0.1036 | Top-4 | 0.0522 |
| J43 | Emphysema | B | 16 / 128 | 0.5292 | 0.6137 | Chronic obstructive pulmonary disease | +0.0845 | Top-1 | 0.0299 |
| S52 | Unspecified fracture of the lower end of | B | 2 / 128 | 0.5212 | 0.5777 | nasal bones / Age-related osteoporosis w/o current pathologi | +0.0564 | Top-2 | 0.0507 |
| D04 | Carcinoma in situ of skin of other parts | B | 2 / 128 | 0.5802 | 0.6258 | Malignant melanoma of skin | +0.0456 | Top-3 | 0.0550 |
| F31 | Bipolar disorder | B | 1 / 128 | 0.5637 | 0.6063 | Major depressive disorder | +0.0426 | Top-1 | 0.0307 |
| J33 | Polyp of nasal cavity | B | 1 / 128 | 0.5557 | 0.5979 | asthma | +0.0423 | Top-4 | 0.0272 |
| F90 | Attention-deficit hyperactivity disorder | B | 1 / 128 | 0.5205 | 0.5571 | Major depressive disorder | +0.0366 | Top-1 | 0.0266 |
| H20 | Unspecified iridocyclitis | A | 5 / 129 | - | 0.5709 | Unspecified osteoarthritis / Rheumatoid arthritis | - | Top-5 | 0.0303 |

### Rejected Targets (Binary-to-Binary): 116

Primary rejection reasons:

| Reason | Count |
|--------|-------|
| Type A: no cross disease above 0.55 | 2 |
| Type A: best split gap < 0.025 | 1 |
| Type B: self AUC >= 0.60 | 31 |
| Type B: no qualifying cross disease | 59 |
| Type B: top cross disease AUC <= 0.55 | 7 |
| Type B: best split gap < 0.025 | 16 |

## Binary-to-Continuous

- Screened target traits: **125** (Type A: 4, Type B: 121)
- **Selected for benchmark: 9** (Type A: 1, Type B: 8)

### Selected Targets (Binary-to-Continuous)

| ICD | Description | Type | Qualifying Traits | Top Self AUC | Top Cross AUC | Top Cross Name | Top Improvement | Best Split | Best Gap |
|-----|-------------|------|-------------------|--------------|---------------|----------------|-----------------|------------|----------|
| C54 | Malignant neoplasm of endometrium | B | 21 / 36 | 0.5332 | 0.6336 | Hemoglobin [Mass/volume] in Blood / Erythrocyte [DistWidth]  | +0.1003 | Top-35 | 0.0269 |
| N04 | Nephrotic syndrome with unspecified morp | B | 2 / 36 | 0.5450 | 0.6190 | Body weight / Body mass index (BMI) [Ratio] | +0.0741 | Top-2 | 0.0511 |
| I27 | Cor pulmonale (chronic) | B | 2 / 36 | 0.5243 | 0.5949 | Body weight / Body mass index (BMI) [Ratio] | +0.0706 | Top-2 | 0.0470 |
| G30 | Alzheimer's disease | B | 11 / 36 | 0.5910 | 0.6597 | Erythrocytes [#/volume] in Blood by Automated count | +0.0687 | Top-34 | 0.0498 |
| C56 | Malignant neoplasm of unspecified ovary | B | 5 / 36 | 0.5858 | 0.6489 | Cholesterol in HDL [Mass/volume] in Serum or Plasma | +0.0631 | Top-34 | 0.0466 |
| D25 | Leiomyoma of uterus | B | 3 / 36 | 0.5264 | 0.5733 | Estradiol (E2) [Mass/volume] in Serum or Plasma | +0.0469 | Top-35 | 0.0348 |
| L03 | Cellulitis | B | 2 / 36 | 0.5191 | 0.5647 | Body weight / Body mass index (BMI) [Ratio] | +0.0457 | Top-2 | 0.0258 |
| J33 | Polyp of nasal cavity | B | 2 / 36 | 0.5557 | 0.5902 | Eosinophils [#/volume] in Blood by Automated count / Eosinop | +0.0346 | Top-2 | 0.0425 |
| M93 | slipped upper femoral epiphysis | A | 2 / 36 | - | 0.5837 | Body weight / Body mass index (BMI) [Ratio] | - | Top-2 | 0.0358 |

### Rejected Targets (Binary-to-Continuous): 116

Primary rejection reasons:

| Reason | Count |
|--------|-------|
| Type A: no cross trait above 0.55 | 3 |
| Type B: self AUC >= 0.60 | 31 |
| Type B: no qualifying cross trait | 71 |
| Type B: top cross trait AUC <= 0.55 | 7 |
| Type B: best split gap < 0.025 | 4 |

## Sensitivity Analysis Note

To assess robustness of target selection to parameter choices, re-run with:
```
python build_benchmark.py --delta 0.02  # more lenient
python build_benchmark.py --delta 0.03  # more strict
python build_benchmark.py --kmin 2      # require two qualifying diseases
python build_benchmark.py --min-best-split-gap 0.03  # require a larger cluster break
python build_benchmark.py --max-self-auc 0.58  # stricter self-AUC gate
```

Compare the number of selected targets and ground truth rankings across runs.
