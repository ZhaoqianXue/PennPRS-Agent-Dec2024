# Cross-Trait Transfer Benchmark Report

_This report summarizes Type B targets only. Type A targets are included in the benchmark CSV outputs but intentionally excluded from this markdown report._

## Selection Rules


| Target Type | Selection Standard |
|-------------|--------------------|
| Type A target<br>- no self AUC benchmark | - `top_cross_auc >= 0.55`<br>- `best_split_gap >= 0.000` (sort cross diseases/traits by AUC, compute adjacent gaps `AUC_k - AUC_(k+1)`, and take the largest one as `best_split_gap`) |
| Type B target<br>- self AUC benchmark available | - `self_best_auc < 0.60`<br>- `top_cross_auc >= 0.55`<br>- `cross_auc - self_auc >= 0.025`<br>- `best_split_gap >= 0.000` (sort cross diseases/traits by AUC, compute adjacent gaps `AUC_k - AUC_(k+1)`, and take the largest one as `best_split_gap`) |

## Binary-to-Binary

- Screened target traits: **121** (Type B only)
- **Selected for benchmark: 24**

### Selected Targets (Binary-to-Binary)

| ICD | Description | Cross Diseases Beating Self | Top Self AUC | Top Cross AUC | Top Cross Name | Top Improvement | Best Split | Best Gap |
|-----|-------------|-----------------------------|--------------|---------------|----------------|-----------------|------------|----------|
| N40 | Benign prostatic hyperplasia without low | 2 / 128 | 0.5236 | 0.6423 | Malignant neoplasm of prostate / Inflammatory disease of prostate | +0.1186 | Top-2 | 0.0998 |
| M05 | Rheumatoid arthritis | 7 / 128 | 0.5559 | 0.6595 | Unspecified osteoarthritis / Gout / Systemic disord of conn tiss in oth diseases classd elswhr / Rheumatoid arthritis | +0.1036 | Top-4 | 0.0522 |
| C54 | Malignant neoplasm of endometrium | 62 / 127 | 0.5332 | 0.6314 | Major depressive disorder | +0.0982 | Top-104 | 0.0130 |
| J43 | Emphysema | 16 / 128 | 0.5292 | 0.6137 | Chronic obstructive pulmonary disease | +0.0845 | Top-1 | 0.0299 |
| G30 | Alzheimer's disease | 24 / 128 | 0.5910 | 0.6624 | Major depressive disorder | +0.0714 | Top-1 | 0.0134 |
| D25 | Leiomyoma of uterus | 11 / 128 | 0.5264 | 0.5865 | Other benign neoplasm of uterus | +0.0601 | Top-1 | 0.0224 |
| I27 | Cor pulmonale (chronic) | 19 / 128 | 0.5243 | 0.5840 | Obesity | +0.0597 | Top-7 | 0.0104 |
| S52 | Unspecified fracture of the lower end of | 2 / 128 | 0.5212 | 0.5777 | nasal bones / Age-related osteoporosis w/o current pathological fracture | +0.0564 | Top-2 | 0.0507 |
| N04 | Nephrotic syndrome with unspecified morp | 15 / 128 | 0.5450 | 0.6009 | Malignant neoplasm of unsp part of unsp bronchus or lung | +0.0560 | Top-15 | 0.0105 |
| F43 | Post-traumatic stress disorder | 16 / 128 | 0.5017 | 0.5542 | Major depressive disorder | +0.0525 | Top-1 | 0.0149 |
| F03 | Unsp dementia | 4 / 128 | 0.5758 | 0.6228 | Major depressive disorder | +0.0470 | Top-126 | 0.0240 |
| D04 | Carcinoma in situ of skin of other parts | 2 / 128 | 0.5802 | 0.6258 | Malignant melanoma of skin | +0.0456 | Top-3 | 0.0550 |
| I21 | Acute myocardial infarction | 3 / 128 | 0.5779 | 0.6223 | Coronary atherosclerosis due to calcified coronary lesion | +0.0444 | Top-3 | 0.0238 |
| C56 | Malignant neoplasm of unspecified ovary | 5 / 128 | 0.5858 | 0.6291 | Malignant neoplasm of prostate / Inflammatory disease of prostate | +0.0433 | Top-119 | 0.0176 |
| F31 | Bipolar disorder | 1 / 128 | 0.5637 | 0.6063 | Major depressive disorder | +0.0426 | Top-1 | 0.0307 |
| J33 | Polyp of nasal cavity | 1 / 128 | 0.5557 | 0.5979 | asthma | +0.0423 | Top-4 | 0.0272 |
| M34 | Systemic sclerosis [scleroderma] | 2 / 128 | 0.5754 | 0.6161 | Systemic disord of conn tiss in oth diseases classd elswhr / Systemic lupus erythematosus | +0.0407 | Top-2 | 0.0187 |
| L03 | Cellulitis | 8 / 128 | 0.5191 | 0.5564 | Obesity | +0.0373 | Top-6 | 0.0069 |
| F90 | Attention-deficit hyperactivity disorder | 1 / 128 | 0.5205 | 0.5571 | Major depressive disorder | +0.0366 | Top-1 | 0.0266 |
| L55 | Sunburn | 6 / 128 | 0.5208 | 0.5571 | Essential (primary) hypertension | +0.0364 | Top-127 | 0.0102 |
| N02 | Recurrent and persistent hematuria w oth | 10 / 128 | 0.5198 | 0.5526 | asthma | +0.0327 | Top-115 | 0.0047 |
| G40 | Epilepsy | 1 / 128 | 0.5256 | 0.5546 | Headache | +0.0290 | Top-35 | 0.0061 |
| E88 | Metabolic syndrome and other insulin res | 2 / 128 | 0.5320 | 0.5604 | Obesity | +0.0284 | Top-127 | 0.0068 |
| I24 | Non-ST elevation (NSTEMI) myocardial inf | 1 / 127 | 0.5802 | 0.6070 | Coronary atherosclerosis due to calcified coronary lesion | +0.0268 | Top-9 | 0.0100 |

### Rejected Targets (Binary-to-Binary): 97

Primary rejection reasons:

| Reason | Count |
|--------|-------|
| Type B: self AUC >= 0.60 | 31 |
| Type B: no qualifying cross disease | 59 |
| Type B: top cross disease AUC < 0.55 | 7 |

## Binary-to-Continuous

- Screened target traits: **121** (Type B only)
- **Selected for benchmark: 12**

### Selected Targets (Binary-to-Continuous)

| ICD | Description | Cross Traits Beating Self | Top Self AUC | Top Cross AUC | Top Cross Name | Top Improvement | Best Split | Best Gap |
|-----|-------------|---------------------------|--------------|---------------|----------------|-----------------|------------|----------|
| C54 | Malignant neoplasm of endometrium | 21 / 36 | 0.5332 | 0.6336 | Hemoglobin [Mass/volume] in Blood / Erythrocyte [DistWidth] in Blood by Automated count | +0.1003 | Top-35 | 0.0269 |
| N04 | Nephrotic syndrome with unspecified morp | 2 / 36 | 0.5450 | 0.6190 | Body weight / Body mass index (BMI) [Ratio] | +0.0741 | Top-2 | 0.0511 |
| I27 | Cor pulmonale (chronic) | 2 / 36 | 0.5243 | 0.5949 | Body weight / Body mass index (BMI) [Ratio] | +0.0706 | Top-2 | 0.0470 |
| G30 | Alzheimer's disease | 11 / 36 | 0.5910 | 0.6597 | Erythrocytes [#/volume] in Blood by Automated count | +0.0687 | Top-34 | 0.0498 |
| C56 | Malignant neoplasm of unspecified ovary | 5 / 36 | 0.5858 | 0.6489 | Cholesterol in HDL [Mass/volume] in Serum or Plasma | +0.0631 | Top-34 | 0.0466 |
| D25 | Leiomyoma of uterus | 3 / 36 | 0.5264 | 0.5733 | Estradiol (E2) [Mass/volume] in Serum or Plasma | +0.0469 | Top-35 | 0.0348 |
| L03 | Cellulitis | 2 / 36 | 0.5191 | 0.5647 | Body weight / Body mass index (BMI) [Ratio] | +0.0457 | Top-2 | 0.0258 |
| L55 | Sunburn | 4 / 36 | 0.5208 | 0.5583 | Hemoglobin A1c/Hemoglobin.total in Blood / Hemoglobin [Mass/volume] in Blood | +0.0375 | Top-35 | 0.0114 |
| N02 | Recurrent and persistent hematuria w oth | 3 / 36 | 0.5198 | 0.5552 | Body weight / Body mass index (BMI) [Ratio] | +0.0354 | Top-33 | 0.0154 |
| J33 | Polyp of nasal cavity | 2 / 36 | 0.5557 | 0.5902 | Eosinophils [#/volume] in Blood by Automated count / Eosinophils/Leukocytes in Blood by Automated count | +0.0346 | Top-2 | 0.0425 |
| E88 | Metabolic syndrome and other insulin res | 2 / 36 | 0.5320 | 0.5633 | Body weight / Body mass index (BMI) [Ratio] | +0.0313 | Top-2 | 0.0213 |
| J43 | Emphysema | 3 / 36 | 0.5292 | 0.5585 | Body weight / Body mass index (BMI) [Ratio] | +0.0293 | Top-3 | 0.0115 |

### Rejected Targets (Binary-to-Continuous): 109

Primary rejection reasons:

| Reason | Count |
|--------|-------|
| Type B: self AUC >= 0.60 | 31 |
| Type B: no qualifying cross trait | 71 |
| Type B: top cross trait AUC < 0.55 | 7 |

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
