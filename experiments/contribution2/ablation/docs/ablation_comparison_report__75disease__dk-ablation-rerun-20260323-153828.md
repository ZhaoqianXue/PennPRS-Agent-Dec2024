# Domain Knowledge Ablation Study Report

## Overview

Each row represents a leave-one-out ablation: the full domain knowledge document with exactly one ## section removed. Delta columns show the change relative to the full-domain baseline.

Hit metrics are reported for both modal selections and all trials. Ranking metrics use the AoU benchmark rank `r` within a disease-specific candidate pool of size `M`.

## Modal Hit@1-5


| Variant                                 | Removed Section                 | Hit@1          | Hit@2           | Hit@3          | Hit@4          | Hit@5           |
| --------------------------------------- | ------------------------------- | -------------- | --------------- | -------------- | -------------- | --------------- |
| **Full (baseline)**                     | —                               | 29.3%          | 53.3%           | 58.7%          | 66.7%          | 74.7%           |
| *No domain (lower bound)*               | *all sections*                  | 24.0% (-5.3pp) | 37.3% (-16.0pp) | 56.0% (-2.7pp) | 62.7% (-4.0pp) | 64.0% (-10.7pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 26.7% (-2.7pp) | 50.7% (-2.7pp)  | 58.7% (0.0pp)  | 69.3% (+2.7pp) | 76.0% (+1.3pp)  |
| `no-section1-trait-endpoint`            | S1: trait / endpoint            | 28.0% (-1.3pp) | 52.0% (-1.3pp)  | 61.3% (+2.7pp) | 70.7% (+4.0pp) | 74.7% (0.0pp)   |
| `no-section6-publication`               | S6: publication                 | 28.0% (-1.3pp) | 50.7% (-2.7pp)  | 57.3% (-1.3pp) | 68.0% (+1.3pp) | 73.3% (-1.3pp)  |
| `no-section2-performance-covariates`    | S2: performance / covariates    | 30.7% (+1.3pp) | 52.0% (-1.3pp)  | 61.3% (+2.7pp) | 68.0% (+1.3pp) | 73.3% (-1.3pp)  |
| `no-section3-validation-sample-size`    | S3: validation_sample_size      | 30.7% (+1.3pp) | 56.0% (+2.7pp)  | 62.7% (+4.0pp) | 70.7% (+4.0pp) | 73.3% (-1.3pp)  |
| `no-section7-variants-number`           | S7: variants_number             | 30.7% (+1.3pp) | 53.3% (0.0pp)   | 60.0% (+1.3pp) | 68.0% (+1.3pp) | 73.3% (-1.3pp)  |
| `no-section5-method-name`               | S5: method_name                 | 33.3% (+4.0pp) | 56.0% (+2.7pp)  | 64.0% (+5.3pp) | 74.7% (+8.0pp) | 77.3% (+2.7pp)  |


## Trial Hit@1-5


| Variant                                 | Removed Section                 | Hit@1          | Hit@2           | Hit@3          | Hit@4          | Hit@5           |
| --------------------------------------- | ------------------------------- | -------------- | --------------- | -------------- | -------------- | --------------- |
| **Full (baseline)**                     | —                               | 29.6%          | 53.7%           | 60.7%          | 68.7%          | 74.4%           |
| *No domain (lower bound)*               | *all sections*                  | 23.7% (-5.9pp) | 36.0% (-17.7pp) | 54.1% (-6.5pp) | 61.6% (-7.1pp) | 63.9% (-10.5pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 27.9% (-1.7pp) | 50.8% (-2.9pp)  | 58.7% (-2.0pp) | 67.2% (-1.5pp) | 72.7% (-1.7pp)  |
| `no-section1-trait-endpoint`            | S1: trait / endpoint            | 29.1% (-0.5pp) | 52.9% (-0.8pp)  | 62.0% (+1.3pp) | 69.9% (+1.2pp) | 74.0% (-0.4pp)  |
| `no-section6-publication`               | S6: publication                 | 28.7% (-0.9pp) | 52.3% (-1.5pp)  | 59.2% (-1.5pp) | 68.8% (+0.1pp) | 73.6% (-0.8pp)  |
| `no-section2-performance-covariates`    | S2: performance / covariates    | 31.2% (+1.6pp) | 52.0% (-1.7pp)  | 60.9% (+0.3pp) | 68.0% (-0.7pp) | 73.3% (-1.1pp)  |
| `no-section3-validation-sample-size`    | S3: validation_sample_size      | 30.8% (+1.2pp) | 55.3% (+1.6pp)  | 62.0% (+1.3pp) | 70.7% (+2.0pp) | 74.4% (0.0pp)   |
| `no-section7-variants-number`           | S7: variants_number             | 31.7% (+2.1pp) | 55.1% (+1.3pp)  | 61.9% (+1.2pp) | 69.7% (+1.1pp) | 74.8% (+0.4pp)  |
| `no-section5-method-name`               | S5: method_name                 | 31.6% (+2.0pp) | 54.4% (+0.7pp)  | 62.3% (+1.6pp) | 71.2% (+2.5pp) | 75.5% (+1.1pp)  |


## Modal Top 5-25% Hit


| Variant                                 | Removed Section                 | Top 5%         | Top 10%        | Top 15%         | Top 20%         | Top 25%        |
| --------------------------------------- | ------------------------------- | -------------- | -------------- | --------------- | --------------- | -------------- |
| **Full (baseline)**                     | —                               | 37.3%          | 41.3%          | 49.3%           | 52.0%           | 54.7%          |
| *No domain (lower bound)*               | *all sections*                  | 29.3% (-8.0pp) | 33.3% (-8.0pp) | 38.7% (-10.7pp) | 41.3% (-10.7pp) | 46.7% (-8.0pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 34.7% (-2.7pp) | 40.0% (-1.3pp) | 49.3% (0.0pp)   | 52.0% (0.0pp)   | 57.3% (+2.7pp) |
| `no-section1-trait-endpoint`            | S1: trait / endpoint            | 37.3% (0.0pp)  | 44.0% (+2.7pp) | 52.0% (+2.7pp)  | 54.7% (+2.7pp)  | 57.3% (+2.7pp) |
| `no-section6-publication`               | S6: publication                 | 37.3% (0.0pp)  | 41.3% (0.0pp)  | 50.7% (+1.3pp)  | 53.3% (+1.3pp)  | 54.7% (0.0pp)  |
| `no-section2-performance-covariates`    | S2: performance / covariates    | 38.7% (+1.3pp) | 44.0% (+2.7pp) | 50.7% (+1.3pp)  | 53.3% (+1.3pp)  | 54.7% (0.0pp)  |
| `no-section3-validation-sample-size`    | S3: validation_sample_size      | 40.0% (+2.7pp) | 42.7% (+1.3pp) | 52.0% (+2.7pp)  | 54.7% (+2.7pp)  | 56.0% (+1.3pp) |
| `no-section7-variants-number`           | S7: variants_number             | 37.3% (0.0pp)  | 38.7% (-2.7pp) | 48.0% (-1.3pp)  | 52.0% (0.0pp)   | 54.7% (0.0pp)  |
| `no-section5-method-name`               | S5: method_name                 | 44.0% (+6.7pp) | 48.0% (+6.7pp) | 57.3% (+8.0pp)  | 60.0% (+8.0pp)  | 64.0% (+9.3pp) |


## Trial Top 5-25% Hit


| Variant                                 | Removed Section                 | Top 5%         | Top 10%        | Top 15%         | Top 20%         | Top 25%         |
| --------------------------------------- | ------------------------------- | -------------- | -------------- | --------------- | --------------- | --------------- |
| **Full (baseline)**                     | —                               | 37.3%          | 42.0%          | 51.3%           | 54.0%           | 56.9%           |
| *No domain (lower bound)*               | *all sections*                  | 28.0% (-9.3pp) | 32.5% (-9.5pp) | 37.9% (-13.5pp) | 40.9% (-13.1pp) | 46.1% (-10.8pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 35.6% (-1.7pp) | 40.7% (-1.3pp) | 49.9% (-1.5pp)  | 52.5% (-1.5pp)  | 56.3% (-0.7pp)  |
| `no-section1-trait-endpoint`            | S1: trait / endpoint            | 37.9% (+0.5pp) | 42.9% (+0.9pp) | 51.6% (+0.3pp)  | 54.7% (+0.7pp)  | 56.7% (-0.3pp)  |
| `no-section6-publication`               | S6: publication                 | 37.1% (-0.3pp) | 42.3% (+0.3pp) | 52.3% (+0.9pp)  | 54.4% (+0.4pp)  | 56.1% (-0.8pp)  |
| `no-section2-performance-covariates`    | S2: performance / covariates    | 39.5% (+2.1pp) | 43.5% (+1.5pp) | 51.5% (+0.1pp)  | 54.4% (+0.4pp)  | 56.0% (-0.9pp)  |
| `no-section3-validation-sample-size`    | S3: validation_sample_size      | 39.7% (+2.4pp) | 43.3% (+1.3pp) | 52.4% (+1.1pp)  | 54.9% (+0.9pp)  | 56.9% (0.0pp)   |
| `no-section7-variants-number`           | S7: variants_number             | 39.5% (+2.1pp) | 42.0% (0.0pp)  | 52.4% (+1.1pp)  | 55.5% (+1.5pp)  | 58.5% (+1.6pp)  |
| `no-section5-method-name`               | S5: method_name                 | 40.7% (+3.3pp) | 44.3% (+2.3pp) | 54.3% (+2.9pp)  | 57.7% (+3.7pp)  | 60.5% (+3.6pp)  |


## Rank Fraction / Reverse Rank Fraction / NRS

- Rank Fraction: `r / M` where smaller is better.
- Reverse Rank Fraction: `(M - r) / M` where larger is better.
- Normalized Ranking Score: `NRS = (M - r) / (M - 1)` where larger is better.


| Variant                                 | Removed Section                 | Modal r / M      | Modal (M - r) / M | Modal NRS        | Trial r / M      | Trial (M - r) / M | Trial NRS        |
| --------------------------------------- | ------------------------------- | ---------------- | ----------------- | ---------------- | ---------------- | ----------------- | ---------------- |
| **Full (baseline)**                     | —                               | 0.4099           | 0.5901            | 0.6772           | 0.4043           | 0.5957            | 0.6866           |
| *No domain (lower bound)*               | *all sections*                  | 0.4806 (+0.0706) | 0.5194 (-0.0706)  | 0.5860 (-0.0912) | 0.4882 (+0.0839) | 0.5118 (-0.0839)  | 0.5771 (-0.1095) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 0.4048 (-0.0052) | 0.5952 (+0.0052)  | 0.6926 (+0.0154) | 0.4172 (+0.0129) | 0.5828 (-0.0129)  | 0.6789 (-0.0077) |
| `no-section1-trait-endpoint`            | S1: trait / endpoint            | 0.4124 (+0.0024) | 0.5876 (-0.0024)  | 0.6712 (-0.0060) | 0.4116 (+0.0073) | 0.5884 (-0.0073)  | 0.6742 (-0.0124) |
| `no-section6-publication`               | S6: publication                 | 0.4199 (+0.0100) | 0.5801 (-0.0100)  | 0.6745 (-0.0027) | 0.4116 (+0.0073) | 0.5884 (-0.0073)  | 0.6822 (-0.0044) |
| `no-section2-performance-covariates`    | S2: performance / covariates    | 0.4213 (+0.0113) | 0.5787 (-0.0113)  | 0.6613 (-0.0159) | 0.4180 (+0.0137) | 0.5820 (-0.0137)  | 0.6655 (-0.0211) |
| `no-section3-validation-sample-size`    | S3: validation_sample_size      | 0.4041 (-0.0059) | 0.5959 (+0.0059)  | 0.6845 (+0.0073) | 0.3998 (-0.0045) | 0.6002 (+0.0045)  | 0.6899 (+0.0033) |
| `no-section7-variants-number`           | S7: variants_number             | 0.4094 (-0.0005) | 0.5906 (+0.0005)  | 0.6797 (+0.0025) | 0.3979 (-0.0064) | 0.6021 (+0.0064)  | 0.6966 (+0.0100) |
| `no-section5-method-name`               | S5: method_name                 | 0.3712 (-0.0387) | 0.6288 (+0.0387)  | 0.7320 (+0.0548) | 0.3904 (-0.0139) | 0.6096 (+0.0139)  | 0.7076 (+0.0210) |


## Section Importance Ranking (by Hit@1 drop)

Sections sorted by the magnitude of Hit@1 drop when removed (largest drop = most important):

1. **S4: training_cohorts / ancestry** (`no-section4-training-cohorts-ancestry`): Hit@1 -2.7pp, NRS +1.5pp
2. **S1: trait / endpoint** (`no-section1-trait-endpoint`): Hit@1 -1.3pp, NRS -0.6pp
3. **S6: publication** (`no-section6-publication`): Hit@1 -1.3pp, NRS -0.3pp
4. **S2: performance / covariates** (`no-section2-performance-covariates`): Hit@1 +1.3pp, NRS -1.6pp
5. **S3: validation_sample_size** (`no-section3-validation-sample-size`): Hit@1 +1.3pp, NRS +0.7pp
6. **S7: variants_number** (`no-section7-variants-number`): Hit@1 +1.3pp, NRS +0.2pp
7. **S5: method_name** (`no-section5-method-name`): Hit@1 +4.0pp, NRS +5.5pp

## Per-Disease Impact Analysis

For each variant, which diseases changed from Hit to Miss (regressions) or Miss to Hit (improvements) at Hit@1 compared to the full baseline.

### `no-section4-training-cohorts-ancestry` (S4: training_cohorts / ancestry)

- **Regressions** (Hit->Miss): aortic stenosis, dilated cardiomyopathy, obesity
- **Improvements** (Miss->Hit): psoriatic arthritis
- Net: -2 diseases

### `no-section1-trait-endpoint` (S1: trait / endpoint)

- **Regressions** (Hit->Miss): aortic stenosis, dilated cardiomyopathy, kidney failure
- **Improvements** (Miss->Hit): depressive disorder, lymphoid leukemia
- Net: -1 diseases

### `no-section6-publication` (S6: publication)

- **Regressions** (Hit->Miss): aortic stenosis, dilated cardiomyopathy, kidney failure
- **Improvements** (Miss->Hit): psoriatic arthritis, sleep apnea
- Net: -1 diseases

### `no-section2-performance-covariates` (S2: performance / covariates)

- **Regressions** (Hit->Miss): aortic stenosis
- **Improvements** (Miss->Hit): heart failure, osteoporosis
- Net: +1 diseases

### `no-section3-validation-sample-size` (S3: validation_sample_size)

- **Regressions** (Hit->Miss): aortic stenosis, dilated cardiomyopathy
- **Improvements** (Miss->Hit): heart failure, late-onset alzheimer's disease, sleep apnea
- Net: +1 diseases

### `no-section7-variants-number` (S7: variants_number)

- **Regressions** (Hit->Miss): aortic stenosis, dilated cardiomyopathy, obesity
- **Improvements** (Miss->Hit): blood coagulation disease, depressive disorder, heart failure, sleep apnea
- Net: +1 diseases

### `no-section5-method-name` (S5: method_name)

- **Regressions** (Hit->Miss): aortic stenosis
- **Improvements** (Miss->Hit): blood coagulation disease, late-onset alzheimer's disease, psoriatic arthritis, sleep apnea
- Net: +3 diseases

## Disease Robustness Analysis

### Robust diseases (Hit@1 in baseline AND all ablation variants)

- alcohol dependence
- bipolar disorder
- chronic obstructive pulmonary disease
- corneal dystrophy
- dupuytren contracture
- hip osteoarthritis
- hodgkins lymphoma
- hypertrophic cardiomyopathy
- iron metabolism disease
- juvenile idiopathic arthritis
- kidney cancer
- nicotine dependence
- otosclerosis
- parkinson disease
- peripheral vascular disease
- preeclampsia
- skin carcinoma in situ
- urolithiasis

### Fragile diseases (Hit@1 in baseline but Miss in at least one variant)

- **aortic stenosis**: lost in `no-section1-trait-endpoint`, `no-section2-performance-covariates`, `no-section3-validation-sample-size`, `no-section4-training-cohorts-ancestry`, `no-section5-method-name`, `no-section6-publication`, `no-section7-variants-number`
- **dilated cardiomyopathy**: lost in `no-section1-trait-endpoint`, `no-section3-validation-sample-size`, `no-section4-training-cohorts-ancestry`, `no-section6-publication`, `no-section7-variants-number`
- **kidney failure**: lost in `no-section1-trait-endpoint`, `no-section6-publication`
- **obesity**: lost in `no-section4-training-cohorts-ancestry`, `no-section7-variants-number`

