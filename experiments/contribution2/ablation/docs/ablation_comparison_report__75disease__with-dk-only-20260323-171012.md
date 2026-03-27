# Domain Knowledge Ablation Study Report

## Overview

Each row represents a leave-one-out ablation: the full domain knowledge document with exactly one ## section removed. Delta columns show the change relative to the full-domain baseline.

Hit metrics are reported for both modal selections and all trials. Ranking metrics use the AoU benchmark rank `r` within a disease-specific candidate pool of size `M`.

## Modal Hit@1-5


| Variant                                 | Removed Section                 | Hit@1          | Hit@2           | Hit@3           | Hit@4          | Hit@5          |
| --------------------------------------- | ------------------------------- | -------------- | --------------- | --------------- | -------------- | -------------- |
| **Full (baseline)**                     | —                               | 32.0%          | 56.0%           | 65.3%           | 70.7%          | 73.3%          |
| *No domain (lower bound)*               | *all sections*                  | 24.0% (-8.0pp) | 37.3% (-18.7pp) | 56.0% (-9.3pp)  | 62.7% (-8.0pp) | 64.0% (-9.3pp) |
| `no-section2-performance-covariates`    | S2: performance / covariates    | 24.0% (-8.0pp) | 46.7% (-9.3pp)  | 56.0% (-9.3pp)  | 66.7% (-4.0pp) | 69.3% (-4.0pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 28.0% (-4.0pp) | 45.3% (-10.7pp) | 54.7% (-10.7pp) | 61.3% (-9.3pp) | 68.0% (-5.3pp) |
| `no-section5-method-name`               | S5: method_name                 | 28.0% (-4.0pp) | 49.3% (-6.7pp)  | 58.7% (-6.7pp)  | 69.3% (-1.3pp) | 73.3% (0.0pp)  |
| `no-section1-trait-endpoint`            | S1: trait / endpoint            | 30.7% (-1.3pp) | 49.3% (-6.7pp)  | 57.3% (-8.0pp)  | 68.0% (-2.7pp) | 70.7% (-2.7pp) |
| `no-section7-variants-number`           | S7: variants_number             | 30.7% (-1.3pp) | 53.3% (-2.7pp)  | 61.3% (-4.0pp)  | 69.3% (-1.3pp) | 73.3% (0.0pp)  |
| `no-section3-validation-sample-size`    | S3: validation_sample_size      | 32.0% (0.0pp)  | 53.3% (-2.7pp)  | 61.3% (-4.0pp)  | 70.7% (0.0pp)  | 73.3% (0.0pp)  |
| `no-section6-publication`               | S6: publication                 | 32.0% (0.0pp)  | 53.3% (-2.7pp)  | 60.0% (-5.3pp)  | 65.3% (-5.3pp) | 69.3% (-4.0pp) |


## Trial Hit@1-5


| Variant                                 | Removed Section                 | Hit@1          | Hit@2           | Hit@3          | Hit@4          | Hit@5          |
| --------------------------------------- | ------------------------------- | -------------- | --------------- | -------------- | -------------- | -------------- |
| **Full (baseline)**                     | —                               | 30.8%          | 54.3%           | 63.5%          | 69.7%          | 73.3%          |
| *No domain (lower bound)*               | *all sections*                  | 23.7% (-7.1pp) | 36.0% (-18.3pp) | 54.1% (-9.3pp) | 61.6% (-8.1pp) | 63.9% (-9.5pp) |
| `no-section2-performance-covariates`    | S2: performance / covariates    | 26.7% (-4.1pp) | 48.7% (-5.6pp)  | 56.9% (-6.5pp) | 66.8% (-2.9pp) | 70.4% (-2.9pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 28.7% (-2.1pp) | 47.7% (-6.5pp)  | 57.3% (-6.1pp) | 65.1% (-4.7pp) | 69.9% (-3.5pp) |
| `no-section5-method-name`               | S5: method_name                 | 28.8% (-2.0pp) | 50.7% (-3.6pp)  | 59.6% (-3.9pp) | 69.1% (-0.7pp) | 73.1% (-0.3pp) |
| `no-section1-trait-endpoint`            | S1: trait / endpoint            | 30.3% (-0.5pp) | 50.8% (-3.5pp)  | 58.8% (-4.7pp) | 68.1% (-1.6pp) | 71.5% (-1.9pp) |
| `no-section7-variants-number`           | S7: variants_number             | 30.1% (-0.7pp) | 52.3% (-2.0pp)  | 60.5% (-2.9pp) | 69.2% (-0.5pp) | 73.3% (0.0pp)  |
| `no-section3-validation-sample-size`    | S3: validation_sample_size      | 30.8% (0.0pp)  | 53.6% (-0.7pp)  | 61.2% (-2.3pp) | 69.5% (-0.3pp) | 72.1% (-1.2pp) |
| `no-section6-publication`               | S6: publication                 | 30.7% (-0.1pp) | 52.3% (-2.0pp)  | 60.1% (-3.3pp) | 67.3% (-2.4pp) | 71.5% (-1.9pp) |


## Modal Top 5-25% Hit


| Variant                                 | Removed Section                 | Top 5%          | Top 10%         | Top 15%         | Top 20%         | Top 25%         |
| --------------------------------------- | ------------------------------- | --------------- | --------------- | --------------- | --------------- | --------------- |
| **Full (baseline)**                     | —                               | 44.0%           | 46.7%           | 57.3%           | 60.0%           | 60.0%           |
| *No domain (lower bound)*               | *all sections*                  | 29.3% (-14.7pp) | 33.3% (-13.3pp) | 38.7% (-18.7pp) | 41.3% (-18.7pp) | 46.7% (-13.3pp) |
| `no-section2-performance-covariates`    | S2: performance / covariates    | 34.7% (-9.3pp)  | 37.3% (-9.3pp)  | 45.3% (-12.0pp) | 48.0% (-12.0pp) | 50.7% (-9.3pp)  |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 33.3% (-10.7pp) | 36.0% (-10.7pp) | 42.7% (-14.7pp) | 45.3% (-14.7pp) | 52.0% (-8.0pp)  |
| `no-section5-method-name`               | S5: method_name                 | 37.3% (-6.7pp)  | 38.7% (-8.0pp)  | 49.3% (-8.0pp)  | 52.0% (-8.0pp)  | 56.0% (-4.0pp)  |
| `no-section1-trait-endpoint`            | S1: trait / endpoint            | 38.7% (-5.3pp)  | 40.0% (-6.7pp)  | 46.7% (-10.7pp) | 49.3% (-10.7pp) | 57.3% (-2.7pp)  |
| `no-section7-variants-number`           | S7: variants_number             | 38.7% (-5.3pp)  | 41.3% (-5.3pp)  | 53.3% (-4.0pp)  | 56.0% (-4.0pp)  | 60.0% (0.0pp)   |
| `no-section3-validation-sample-size`    | S3: validation_sample_size      | 40.0% (-4.0pp)  | 42.7% (-4.0pp)  | 52.0% (-5.3pp)  | 56.0% (-4.0pp)  | 58.7% (-1.3pp)  |
| `no-section6-publication`               | S6: publication                 | 38.7% (-5.3pp)  | 41.3% (-5.3pp)  | 50.7% (-6.7pp)  | 53.3% (-6.7pp)  | 56.0% (-4.0pp)  |


## Trial Top 5-25% Hit


| Variant                                 | Removed Section                 | Top 5%          | Top 10%         | Top 15%         | Top 20%         | Top 25%         |
| --------------------------------------- | ------------------------------- | --------------- | --------------- | --------------- | --------------- | --------------- |
| **Full (baseline)**                     | —                               | 41.1%           | 44.9%           | 54.8%           | 57.3%           | 58.9%           |
| *No domain (lower bound)*               | *all sections*                  | 28.0% (-13.1pp) | 32.5% (-12.4pp) | 37.9% (-16.9pp) | 40.9% (-16.4pp) | 46.1% (-12.8pp) |
| `no-section2-performance-covariates`    | S2: performance / covariates    | 36.8% (-4.3pp)  | 38.9% (-6.0pp)  | 46.8% (-8.0pp)  | 49.2% (-8.1pp)  | 51.3% (-7.6pp)  |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 35.2% (-5.9pp)  | 38.9% (-6.0pp)  | 46.8% (-8.0pp)  | 49.9% (-7.5pp)  | 54.9% (-4.0pp)  |
| `no-section5-method-name`               | S5: method_name                 | 37.3% (-3.7pp)  | 39.5% (-5.5pp)  | 49.6% (-5.2pp)  | 52.5% (-4.8pp)  | 55.9% (-3.1pp)  |
| `no-section1-trait-endpoint`            | S1: trait / endpoint            | 38.3% (-2.8pp)  | 41.5% (-3.5pp)  | 48.9% (-5.9pp)  | 51.7% (-5.6pp)  | 57.3% (-1.6pp)  |
| `no-section7-variants-number`           | S7: variants_number             | 38.0% (-3.1pp)  | 40.8% (-4.1pp)  | 51.7% (-3.1pp)  | 54.1% (-3.2pp)  | 58.5% (-0.4pp)  |
| `no-section3-validation-sample-size`    | S3: validation_sample_size      | 39.5% (-1.6pp)  | 42.1% (-2.8pp)  | 51.2% (-3.6pp)  | 54.1% (-3.2pp)  | 56.1% (-2.8pp)  |
| `no-section6-publication`               | S6: publication                 | 37.9% (-3.2pp)  | 41.1% (-3.9pp)  | 50.5% (-4.3pp)  | 53.7% (-3.6pp)  | 56.9% (-2.0pp)  |


## Rank Fraction / Reverse Rank Fraction / NRS

- Rank Fraction: `r / M` where smaller is better.
- Reverse Rank Fraction: `(M - r) / M` where larger is better.
- Normalized Ranking Score: `NRS = (M - r) / (M - 1)` where larger is better.


| Variant                                 | Removed Section                 | Modal r / M      | Modal (M - r) / M | Modal NRS        | Trial r / M      | Trial (M - r) / M | Trial NRS        |
| --------------------------------------- | ------------------------------- | ---------------- | ----------------- | ---------------- | ---------------- | ----------------- | ---------------- |
| **Full (baseline)**                     | —                               | 0.3952           | 0.6048            | 0.7058           | 0.3982           | 0.6018            | 0.6978           |
| *No domain (lower bound)*               | *all sections*                  | 0.4806 (+0.0853) | 0.5194 (-0.0853)  | 0.5860 (-0.1198) | 0.4882 (+0.0900) | 0.5118 (-0.0900)  | 0.5771 (-0.1207) |
| `no-section2-performance-covariates`    | S2: performance / covariates    | 0.4273 (+0.0320) | 0.5727 (-0.0320)  | 0.6494 (-0.0564) | 0.4310 (+0.0328) | 0.5690 (-0.0328)  | 0.6492 (-0.0485) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 0.4480 (+0.0528) | 0.5520 (-0.0528)  | 0.6370 (-0.0688) | 0.4323 (+0.0340) | 0.5677 (-0.0340)  | 0.6555 (-0.0423) |
| `no-section5-method-name`               | S5: method_name                 | 0.4185 (+0.0232) | 0.5815 (-0.0232)  | 0.6711 (-0.0347) | 0.4107 (+0.0124) | 0.5893 (-0.0124)  | 0.6796 (-0.0182) |
| `no-section1-trait-endpoint`            | S1: trait / endpoint            | 0.4132 (+0.0179) | 0.5868 (-0.0179)  | 0.6775 (-0.0284) | 0.4113 (+0.0130) | 0.5887 (-0.0130)  | 0.6766 (-0.0212) |
| `no-section7-variants-number`           | S7: variants_number             | 0.3918 (-0.0034) | 0.6082 (+0.0034)  | 0.7054 (-0.0004) | 0.3998 (+0.0016) | 0.6002 (-0.0016)  | 0.6916 (-0.0062) |
| `no-section3-validation-sample-size`    | S3: validation_sample_size      | 0.3925 (-0.0027) | 0.6075 (+0.0027)  | 0.6999 (-0.0059) | 0.4003 (+0.0021) | 0.5997 (-0.0021)  | 0.6890 (-0.0088) |
| `no-section6-publication`               | S6: publication                 | 0.4104 (+0.0152) | 0.5896 (-0.0152)  | 0.6899 (-0.0160) | 0.4097 (+0.0115) | 0.5903 (-0.0115)  | 0.6849 (-0.0129) |


## Section Importance Ranking (by Hit@1 drop)

Sections sorted by the magnitude of Hit@1 drop when removed (largest drop = most important):

1. **S2: performance / covariates** (`no-section2-performance-covariates`): Hit@1 -8.0pp, NRS -5.6pp
2. **S4: training_cohorts / ancestry** (`no-section4-training-cohorts-ancestry`): Hit@1 -4.0pp, NRS -6.9pp
3. **S5: method_name** (`no-section5-method-name`): Hit@1 -4.0pp, NRS -3.5pp
4. **S1: trait / endpoint** (`no-section1-trait-endpoint`): Hit@1 -1.3pp, NRS -2.8pp
5. **S7: variants_number** (`no-section7-variants-number`): Hit@1 -1.3pp, NRS -0.0pp
6. **S3: validation_sample_size** (`no-section3-validation-sample-size`): Hit@1 0.0pp, NRS -0.6pp
7. **S6: publication** (`no-section6-publication`): Hit@1 0.0pp, NRS -1.6pp

## Per-Disease Impact Analysis

For each variant, which diseases changed from Hit to Miss (regressions) or Miss to Hit (improvements) at Hit@1 compared to the full baseline.

### `no-section2-performance-covariates` (S2: performance / covariates)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, heart failure, late-onset alzheimer's disease, otosclerosis, peripheral vascular disease, psoriatic arthritis
- Net: -6 diseases

### `no-section4-training-cohorts-ancestry` (S4: training_cohorts / ancestry)

- **Regressions** (Hit->Miss): dupuytren contracture, heart failure, otosclerosis, sleep apnea
- **Improvements** (Miss->Hit): kidney failure
- Net: -3 diseases

### `no-section5-method-name` (S5: method_name)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, heart failure, late-onset alzheimer's disease, otosclerosis
- **Improvements** (Miss->Hit): kidney failure
- Net: -3 diseases

### `no-section1-trait-endpoint` (S1: trait / endpoint)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, heart failure, otosclerosis
- **Improvements** (Miss->Hit): kidney failure, obesity
- Net: -1 diseases

### `no-section7-variants-number` (S7: variants_number)

- **Regressions** (Hit->Miss): chronic obstructive pulmonary disease, heart failure, otosclerosis
- **Improvements** (Miss->Hit): aortic stenosis, obesity
- Net: -1 diseases

### `no-section3-validation-sample-size` (S3: validation_sample_size)

- **Regressions** (Hit->Miss): heart failure, psoriatic arthritis
- **Improvements** (Miss->Hit): kidney failure, obesity
- Net: +0 diseases

### `no-section6-publication` (S6: publication)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, heart failure, sleep apnea
- **Improvements** (Miss->Hit): abdominal aortic aneurysm, kidney failure, obesity
- Net: +0 diseases

## Disease Robustness Analysis

### Robust diseases (Hit@1 in baseline AND all ablation variants)

- alcohol dependence
- bipolar disorder
- blood coagulation disease
- corneal dystrophy
- hip osteoarthritis
- hodgkins lymphoma
- hypertrophic cardiomyopathy
- iron metabolism disease
- juvenile idiopathic arthritis
- kidney cancer
- nicotine dependence
- parkinson disease
- preeclampsia
- skin carcinoma in situ
- urolithiasis

### Fragile diseases (Hit@1 in baseline but Miss in at least one variant)

- **chronic obstructive pulmonary disease**: lost in `no-section7-variants-number`
- **dilated cardiomyopathy**: lost in `no-section1-trait-endpoint`, `no-section2-performance-covariates`, `no-section5-method-name`, `no-section6-publication`
- **dupuytren contracture**: lost in `no-section4-training-cohorts-ancestry`
- **heart failure**: lost in `no-section1-trait-endpoint`, `no-section2-performance-covariates`, `no-section3-validation-sample-size`, `no-section4-training-cohorts-ancestry`, `no-section5-method-name`, `no-section6-publication`, `no-section7-variants-number`
- **late-onset alzheimer's disease**: lost in `no-section2-performance-covariates`, `no-section5-method-name`
- **otosclerosis**: lost in `no-section1-trait-endpoint`, `no-section2-performance-covariates`, `no-section4-training-cohorts-ancestry`, `no-section5-method-name`, `no-section7-variants-number`
- **peripheral vascular disease**: lost in `no-section2-performance-covariates`
- **psoriatic arthritis**: lost in `no-section2-performance-covariates`, `no-section3-validation-sample-size`
- **sleep apnea**: lost in `no-section4-training-cohorts-ancestry`, `no-section6-publication`

