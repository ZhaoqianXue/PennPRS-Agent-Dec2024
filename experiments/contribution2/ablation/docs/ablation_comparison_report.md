# Domain Knowledge Ablation Study Report

## Overview

Each row represents a leave-one-out ablation: the full domain knowledge document with exactly one ## section removed. Delta columns show the change relative to the full-domain baseline.

Hit metrics are reported for both modal selections and all trials. Ranking metrics use the AoU benchmark rank `r` within a disease-specific candidate pool of size `M`.

## Modal Hit@1-5

| Variant | Removed Section | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|---------|----------------|-------|-------|-------|-------|-------|
| **Full (baseline)** | — | 56.7% | 73.3% | 83.3% | 86.7% | 90.0% |
| *No domain (lower bound)* | *all sections* | 46.7% (-10.0pp) | 56.7% (-16.7pp) | 73.3% (-10.0pp) | 80.0% (-6.7pp) | 80.0% (-10.0pp) |
| `no-section9-disease-family` | S9: disease-family patterns | 46.7% (-10.0pp) | 70.0% (-3.3pp) | 76.7% (-6.7pp) | 86.7% (0.0pp) | 93.3% (+3.3pp) |
| `no-critical-selection-evidence` | Critical selection evidence | 53.3% (-3.3pp) | 73.3% (0.0pp) | 80.0% (-3.3pp) | 86.7% (0.0pp) | 93.3% (+3.3pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 53.3% (-3.3pp) | 73.3% (0.0pp) | 76.7% (-6.7pp) | 83.3% (-3.3pp) | 86.7% (-3.3pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 56.7% (0.0pp) | 73.3% (0.0pp) | 83.3% (0.0pp) | 90.0% (+3.3pp) | 93.3% (+3.3pp) |
| `no-section4-training-cohorts` | S4: training_cohorts | 56.7% (0.0pp) | 73.3% (0.0pp) | 83.3% (0.0pp) | 83.3% (-3.3pp) | 86.7% (-3.3pp) |
| `no-section5-method-name` | S5: method_name | 56.7% (0.0pp) | 76.7% (+3.3pp) | 86.7% (+3.3pp) | 90.0% (+3.3pp) | 93.3% (+3.3pp) |
| `no-section7-publication` | S7: publication | 56.7% (0.0pp) | 76.7% (+3.3pp) | 80.0% (-3.3pp) | 86.7% (0.0pp) | 90.0% (0.0pp) |
| `no-section8-variants-number` | S8: variants_number | 56.7% (0.0pp) | 76.7% (+3.3pp) | 83.3% (0.0pp) | 86.7% (0.0pp) | 90.0% (0.0pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 60.0% (+3.3pp) | 80.0% (+6.7pp) | 83.3% (0.0pp) | 86.7% (0.0pp) | 90.0% (0.0pp) |
| `no-section6-ancestry` | S6: ancestry | 60.0% (+3.3pp) | 76.7% (+3.3pp) | 83.3% (0.0pp) | 90.0% (+3.3pp) | 93.3% (+3.3pp) |

## Trial Hit@1-5

| Variant | Removed Section | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|---------|----------------|-------|-------|-------|-------|-------|
| **Full (baseline)** | — | 58.0% | 75.0% | 82.7% | 87.3% | 91.3% |
| *No domain (lower bound)* | *all sections* | 44.7% (-13.3pp) | 54.7% (-20.3pp) | 74.0% (-8.7pp) | 80.0% (-7.3pp) | 80.0% (-11.3pp) |
| `no-section9-disease-family` | S9: disease-family patterns | 47.7% (-10.3pp) | 71.7% (-3.3pp) | 78.3% (-4.3pp) | 84.7% (-2.7pp) | 92.3% (+1.0pp) |
| `no-critical-selection-evidence` | Critical selection evidence | 53.7% (-4.3pp) | 73.7% (-1.3pp) | 80.0% (-2.7pp) | 85.0% (-2.3pp) | 90.3% (-1.0pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 53.3% (-4.7pp) | 73.7% (-1.3pp) | 78.3% (-4.3pp) | 82.7% (-4.7pp) | 87.7% (-3.7pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 54.7% (-3.3pp) | 68.0% (-7.0pp) | 80.3% (-2.3pp) | 86.0% (-1.3pp) | 90.3% (-1.0pp) |
| `no-section4-training-cohorts` | S4: training_cohorts | 55.3% (-2.7pp) | 74.0% (-1.0pp) | 84.7% (+2.0pp) | 86.7% (-0.7pp) | 90.0% (-1.3pp) |
| `no-section5-method-name` | S5: method_name | 56.0% (-2.0pp) | 76.0% (+1.0pp) | 85.0% (+2.3pp) | 88.0% (+0.7pp) | 91.7% (+0.3pp) |
| `no-section7-publication` | S7: publication | 54.7% (-3.3pp) | 75.3% (+0.3pp) | 81.7% (-1.0pp) | 86.7% (-0.7pp) | 90.7% (-0.7pp) |
| `no-section8-variants-number` | S8: variants_number | 55.0% (-3.0pp) | 75.0% (0.0pp) | 82.7% (0.0pp) | 86.7% (-0.7pp) | 90.0% (-1.3pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 58.3% (+0.3pp) | 75.7% (+0.7pp) | 82.0% (-0.7pp) | 85.7% (-1.7pp) | 90.3% (-1.0pp) |
| `no-section6-ancestry` | S6: ancestry | 58.3% (+0.3pp) | 75.7% (+0.7pp) | 83.0% (+0.3pp) | 87.7% (+0.3pp) | 91.3% (0.0pp) |

## Modal Top 5-25% Hit

| Variant | Removed Section | Top 5% | Top 10% | Top 15% | Top 20% | Top 25% |
|---------|----------------|--------|---------|---------|---------|---------|
| **Full (baseline)** | — | 56.7% | 60.0% | 73.3% | 73.3% | 76.7% |
| *No domain (lower bound)* | *all sections* | 46.7% (-10.0pp) | 50.0% (-10.0pp) | 60.0% (-13.3pp) | 63.3% (-10.0pp) | 66.7% (-10.0pp) |
| `no-section9-disease-family` | S9: disease-family patterns | 46.7% (-10.0pp) | 53.3% (-6.7pp) | 66.7% (-6.7pp) | 66.7% (-6.7pp) | 70.0% (-6.7pp) |
| `no-critical-selection-evidence` | Critical selection evidence | 53.3% (-3.3pp) | 60.0% (0.0pp) | 73.3% (0.0pp) | 73.3% (0.0pp) | 76.7% (0.0pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 53.3% (-3.3pp) | 56.7% (-3.3pp) | 66.7% (-6.7pp) | 66.7% (-6.7pp) | 70.0% (-6.7pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 56.7% (0.0pp) | 66.7% (+6.7pp) | 80.0% (+6.7pp) | 80.0% (+6.7pp) | 80.0% (+3.3pp) |
| `no-section4-training-cohorts` | S4: training_cohorts | 56.7% (0.0pp) | 56.7% (-3.3pp) | 70.0% (-3.3pp) | 70.0% (-3.3pp) | 73.3% (-3.3pp) |
| `no-section5-method-name` | S5: method_name | 56.7% (0.0pp) | 63.3% (+3.3pp) | 80.0% (+6.7pp) | 80.0% (+6.7pp) | 80.0% (+3.3pp) |
| `no-section7-publication` | S7: publication | 56.7% (0.0pp) | 60.0% (0.0pp) | 73.3% (0.0pp) | 73.3% (0.0pp) | 76.7% (0.0pp) |
| `no-section8-variants-number` | S8: variants_number | 56.7% (0.0pp) | 60.0% (0.0pp) | 76.7% (+3.3pp) | 76.7% (+3.3pp) | 76.7% (0.0pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 60.0% (+3.3pp) | 63.3% (+3.3pp) | 80.0% (+6.7pp) | 80.0% (+6.7pp) | 80.0% (+3.3pp) |
| `no-section6-ancestry` | S6: ancestry | 60.0% (+3.3pp) | 63.3% (+3.3pp) | 76.7% (+3.3pp) | 76.7% (+3.3pp) | 76.7% (0.0pp) |

## Trial Top 5-25% Hit

| Variant | Removed Section | Top 5% | Top 10% | Top 15% | Top 20% | Top 25% |
|---------|----------------|--------|---------|---------|---------|---------|
| **Full (baseline)** | — | 58.0% | 62.0% | 75.7% | 76.0% | 77.7% |
| *No domain (lower bound)* | *all sections* | 44.7% (-13.3pp) | 48.0% (-14.0pp) | 57.0% (-18.7pp) | 60.3% (-15.7pp) | 63.7% (-14.0pp) |
| `no-section9-disease-family` | S9: disease-family patterns | 47.7% (-10.3pp) | 53.3% (-8.7pp) | 68.0% (-7.7pp) | 68.3% (-7.7pp) | 72.0% (-5.7pp) |
| `no-critical-selection-evidence` | Critical selection evidence | 53.7% (-4.3pp) | 58.0% (-4.0pp) | 70.7% (-5.0pp) | 70.7% (-5.3pp) | 74.3% (-3.3pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 53.3% (-4.7pp) | 57.3% (-4.7pp) | 67.3% (-8.3pp) | 67.3% (-8.7pp) | 72.0% (-5.7pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 54.7% (-3.3pp) | 62.0% (0.0pp) | 73.3% (-2.3pp) | 73.3% (-2.7pp) | 73.3% (-4.3pp) |
| `no-section4-training-cohorts` | S4: training_cohorts | 55.3% (-2.7pp) | 58.7% (-3.3pp) | 72.0% (-3.7pp) | 72.0% (-4.0pp) | 76.7% (-1.0pp) |
| `no-section5-method-name` | S5: method_name | 56.0% (-2.0pp) | 61.0% (-1.0pp) | 77.3% (+1.7pp) | 77.3% (+1.3pp) | 77.7% (0.0pp) |
| `no-section7-publication` | S7: publication | 54.7% (-3.3pp) | 59.7% (-2.3pp) | 73.7% (-2.0pp) | 73.7% (-2.3pp) | 76.7% (-1.0pp) |
| `no-section8-variants-number` | S8: variants_number | 55.0% (-3.0pp) | 59.0% (-3.0pp) | 73.7% (-2.0pp) | 74.3% (-1.7pp) | 76.0% (-1.7pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 58.3% (+0.3pp) | 62.0% (0.0pp) | 75.7% (0.0pp) | 75.7% (-0.3pp) | 77.0% (-0.7pp) |
| `no-section6-ancestry` | S6: ancestry | 58.3% (+0.3pp) | 61.0% (-1.0pp) | 74.3% (-1.3pp) | 74.3% (-1.7pp) | 75.7% (-2.0pp) |

## Rank Fraction / Reverse Rank Fraction / NRS

- Rank Fraction: `r / M` where smaller is better.
- Reverse Rank Fraction: `(M - r) / M` where larger is better.
- Normalized Ranking Score: `NRS = (M - r) / (M - 1)` where larger is better.

| Variant | Removed Section | Modal r / M | Modal (M - r) / M | Modal NRS | Trial r / M | Trial (M - r) / M | Trial NRS |
|---------|----------------|-------------|-------------------|-----------|-------------|-------------------|-----------|
| **Full (baseline)** | — | 0.3010 | 0.6990 | 0.8321 | 0.2888 | 0.7112 | 0.8441 |
| *No domain (lower bound)* | *all sections* | 0.4256 (+0.1246) | 0.5744 (-0.1246) | 0.6790 (-0.1531) | 0.4302 (+0.1414) | 0.5698 (-0.1414) | 0.6736 (-0.1704) |
| `no-section9-disease-family` | S9: disease-family patterns | 0.3226 (+0.0216) | 0.6774 (-0.0216) | 0.8008 (-0.0313) | 0.3260 (+0.0372) | 0.6740 (-0.0372) | 0.7974 (-0.0467) |
| `no-critical-selection-evidence` | Critical selection evidence | 0.3071 (+0.0062) | 0.6929 (-0.0062) | 0.8223 (-0.0098) | 0.3096 (+0.0208) | 0.6904 (-0.0208) | 0.8205 (-0.0236) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 0.3102 (+0.0092) | 0.6898 (-0.0092) | 0.8203 (-0.0118) | 0.3167 (+0.0279) | 0.6833 (-0.0279) | 0.8126 (-0.0315) |
| `no-section2-performance-covariates` | S2: performance / covariates | 0.2837 (-0.0172) | 0.7163 (+0.0172) | 0.8463 (+0.0142) | 0.3154 (+0.0265) | 0.6846 (-0.0265) | 0.8091 (-0.0350) |
| `no-section4-training-cohorts` | S4: training_cohorts | 0.3051 (+0.0042) | 0.6949 (-0.0042) | 0.8278 (-0.0043) | 0.2940 (+0.0051) | 0.7060 (-0.0051) | 0.8389 (-0.0052) |
| `no-section5-method-name` | S5: method_name | 0.2747 (-0.0263) | 0.7253 (+0.0263) | 0.8597 (+0.0276) | 0.2853 (-0.0035) | 0.7147 (+0.0035) | 0.8484 (+0.0044) |
| `no-section7-publication` | S7: publication | 0.2955 (-0.0055) | 0.7045 (+0.0055) | 0.8379 (+0.0058) | 0.2972 (+0.0084) | 0.7028 (-0.0084) | 0.8350 (-0.0091) |
| `no-section8-variants-number` | S8: variants_number | 0.2889 (-0.0120) | 0.7111 (+0.0120) | 0.8449 (+0.0128) | 0.2933 (+0.0045) | 0.7067 (-0.0045) | 0.8398 (-0.0043) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 0.2707 (-0.0303) | 0.7293 (+0.0303) | 0.8657 (+0.0335) | 0.2897 (+0.0009) | 0.7103 (-0.0009) | 0.8441 (+0.0000) |
| `no-section6-ancestry` | S6: ancestry | 0.2797 (-0.0213) | 0.7203 (+0.0213) | 0.8539 (+0.0218) | 0.2944 (+0.0056) | 0.7056 (-0.0056) | 0.8372 (-0.0068) |

## Section Importance Ranking (by Hit@1 drop)

Sections sorted by the magnitude of Hit@1 drop when removed (largest drop = most important):

1. **S9: disease-family patterns** (`no-section9-disease-family`): Hit@1 -10.0pp, NRS -3.1pp
2. **Critical selection evidence** (`no-critical-selection-evidence`): Hit@1 -3.3pp, NRS -1.0pp
3. **S1: trait / endpoint** (`no-section1-trait-endpoint`): Hit@1 -3.3pp, NRS -1.2pp
4. **S2: performance / covariates** (`no-section2-performance-covariates`): Hit@1 0.0pp, NRS +1.4pp
5. **S4: training_cohorts** (`no-section4-training-cohorts`): Hit@1 0.0pp, NRS -0.4pp
6. **S5: method_name** (`no-section5-method-name`): Hit@1 0.0pp, NRS +2.8pp
7. **S7: publication** (`no-section7-publication`): Hit@1 0.0pp, NRS +0.6pp
8. **S8: variants_number** (`no-section8-variants-number`): Hit@1 0.0pp, NRS +1.3pp
9. **S3: validation_sample_size** (`no-section3-validation-sample-size`): Hit@1 +3.3pp, NRS +3.4pp
10. **S6: ancestry** (`no-section6-ancestry`): Hit@1 +3.3pp, NRS +2.2pp

## Per-Disease Impact Analysis

For each variant, which diseases changed from Hit to Miss (regressions) or Miss to Hit (improvements) at Hit@1 compared to the full baseline.

### `no-section9-disease-family` (S9: disease-family patterns)

- **Regressions** (Hit->Miss): late-onset alzheimer's disease, obesity, open-angle glaucoma, peripheral vascular disease
- **Improvements** (Miss->Hit): abdominal aortic aneurysm
- Net: -3 diseases

### `no-critical-selection-evidence` (Critical selection evidence)

- **Regressions** (Hit->Miss): open-angle glaucoma
- Net: -1 diseases

### `no-section1-trait-endpoint` (S1: trait / endpoint)

- **Regressions** (Hit->Miss): open-angle glaucoma
- Net: -1 diseases

### `no-section2-performance-covariates` (S2: performance / covariates)

- **Regressions** (Hit->Miss): obstructive sleep apnea
- **Improvements** (Miss->Hit): abdominal aortic aneurysm
- Net: +0 diseases

### `no-section7-publication` (S7: publication)

- **Regressions** (Hit->Miss): open-angle glaucoma
- **Improvements** (Miss->Hit): abdominal aortic aneurysm
- Net: +0 diseases

### `no-section3-validation-sample-size` (S3: validation_sample_size)

- **Improvements** (Miss->Hit): abdominal aortic aneurysm
- Net: +1 diseases

### `no-section6-ancestry` (S6: ancestry)

- **Improvements** (Miss->Hit): hypothyroidism
- Net: +1 diseases

## Disease Robustness Analysis

### Robust diseases (Hit@1 in baseline AND all ablation variants)

- age-related macular degeneration
- alcohol dependence
- aortic stenosis
- cutaneous melanoma
- hodgkins lymphoma
- hypertrophic cardiomyopathy
- juvenile idiopathic arthritis
- kidney cancer
- preeclampsia
- renal carcinoma
- skin carcinoma in situ
- sleep apnea

### Fragile diseases (Hit@1 in baseline but Miss in at least one variant)

- **late-onset alzheimer's disease**: lost in `no-section9-disease-family`
- **obesity**: lost in `no-section9-disease-family`
- **obstructive sleep apnea**: lost in `no-section2-performance-covariates`
- **open-angle glaucoma**: lost in `no-critical-selection-evidence`, `no-section1-trait-endpoint`, `no-section7-publication`, `no-section9-disease-family`
- **peripheral vascular disease**: lost in `no-section9-disease-family`
