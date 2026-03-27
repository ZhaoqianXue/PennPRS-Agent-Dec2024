# Domain Knowledge Ablation Study Report

## Overview

Each row represents a leave-one-out ablation: the full domain knowledge document with exactly one ## section removed. Delta columns show the change relative to the full-domain baseline.

Hit metrics are reported for both modal selections and all trials. Ranking metrics use the AoU benchmark rank `r` within a disease-specific candidate pool of size `M`.

## Modal Hit@1-5

| Variant | Removed Section | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|---------|----------------|-------|-------|-------|-------|-------|
| **Full (baseline)** | — | 28.0% | 56.0% | 64.0% | 73.3% | 74.7% |
| *No domain (lower bound)* | *all sections* | 24.0% (-4.0pp) | 37.3% (-18.7pp) | 56.0% (-8.0pp) | 62.7% (-10.7pp) | 64.0% (-10.7pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 25.3% (-2.7pp) | 46.7% (-9.3pp) | 54.7% (-9.3pp) | 65.3% (-8.0pp) | 70.7% (-4.0pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 26.7% (-1.3pp) | 52.0% (-4.0pp) | 61.3% (-2.7pp) | 69.3% (-4.0pp) | 72.0% (-2.7pp) |
| `no-section6-publication` | S6: publication | 26.7% (-1.3pp) | 46.7% (-9.3pp) | 54.7% (-9.3pp) | 68.0% (-5.3pp) | 73.3% (-1.3pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 28.0% (0.0pp) | 52.0% (-4.0pp) | 61.3% (-2.7pp) | 69.3% (-4.0pp) | 73.3% (-1.3pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 30.7% (+2.7pp) | 53.3% (-2.7pp) | 60.0% (-4.0pp) | 69.3% (-4.0pp) | 73.3% (-1.3pp) |
| `no-section5-method-name` | S5: method_name | 30.7% (+2.7pp) | 52.0% (-4.0pp) | 60.0% (-4.0pp) | 66.7% (-6.7pp) | 73.3% (-1.3pp) |
| `no-section7-variants-number` | S7: variants_number | 30.7% (+2.7pp) | 54.7% (-1.3pp) | 64.0% (0.0pp) | 73.3% (0.0pp) | 76.0% (+1.3pp) |

## Trial Hit@1-5

| Variant | Removed Section | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|---------|----------------|-------|-------|-------|-------|-------|
| **Full (baseline)** | — | 29.5% | 55.1% | 62.1% | 71.1% | 74.1% |
| *No domain (lower bound)* | *all sections* | 23.7% (-5.7pp) | 36.0% (-19.1pp) | 54.1% (-8.0pp) | 61.6% (-9.5pp) | 63.9% (-10.3pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 25.7% (-3.7pp) | 46.9% (-8.1pp) | 56.4% (-5.7pp) | 66.1% (-4.9pp) | 70.1% (-4.0pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 28.9% (-0.5pp) | 52.0% (-3.1pp) | 60.8% (-1.3pp) | 68.1% (-2.9pp) | 71.7% (-2.4pp) |
| `no-section6-publication` | S6: publication | 28.4% (-1.1pp) | 50.5% (-4.5pp) | 58.8% (-3.3pp) | 69.6% (-1.5pp) | 73.7% (-0.4pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 28.5% (-0.9pp) | 50.5% (-4.5pp) | 59.7% (-2.4pp) | 68.1% (-2.9pp) | 72.7% (-1.5pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 29.6% (+0.1pp) | 52.5% (-2.5pp) | 60.1% (-2.0pp) | 68.8% (-2.3pp) | 73.5% (-0.7pp) |
| `no-section5-method-name` | S5: method_name | 29.6% (+0.1pp) | 52.5% (-2.5pp) | 61.7% (-0.4pp) | 69.3% (-1.7pp) | 74.9% (+0.8pp) |
| `no-section7-variants-number` | S7: variants_number | 30.1% (+0.7pp) | 54.1% (-0.9pp) | 62.5% (+0.4pp) | 71.5% (+0.4pp) | 74.5% (+0.4pp) |

## Modal Top 5-25% Hit

| Variant | Removed Section | Top 5% | Top 10% | Top 15% | Top 20% | Top 25% |
|---------|----------------|--------|---------|---------|---------|---------|
| **Full (baseline)** | — | 40.0% | 44.0% | 53.3% | 56.0% | 57.3% |
| *No domain (lower bound)* | *all sections* | 29.3% (-10.7pp) | 33.3% (-10.7pp) | 38.7% (-14.7pp) | 41.3% (-14.7pp) | 46.7% (-10.7pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 34.7% (-5.3pp) | 37.3% (-6.7pp) | 48.0% (-5.3pp) | 49.3% (-6.7pp) | 52.0% (-5.3pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 36.0% (-4.0pp) | 38.7% (-5.3pp) | 46.7% (-6.7pp) | 50.7% (-5.3pp) | 56.0% (-1.3pp) |
| `no-section6-publication` | S6: publication | 36.0% (-4.0pp) | 38.7% (-5.3pp) | 49.3% (-4.0pp) | 52.0% (-4.0pp) | 56.0% (-1.3pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 38.7% (-1.3pp) | 44.0% (0.0pp) | 49.3% (-4.0pp) | 53.3% (-2.7pp) | 53.3% (-4.0pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 40.0% (0.0pp) | 42.7% (-1.3pp) | 53.3% (0.0pp) | 56.0% (0.0pp) | 57.3% (0.0pp) |
| `no-section5-method-name` | S5: method_name | 40.0% (0.0pp) | 42.7% (-1.3pp) | 53.3% (0.0pp) | 54.7% (-1.3pp) | 57.3% (0.0pp) |
| `no-section7-variants-number` | S7: variants_number | 41.3% (+1.3pp) | 45.3% (+1.3pp) | 54.7% (+1.3pp) | 57.3% (+1.3pp) | 61.3% (+4.0pp) |

## Trial Top 5-25% Hit

| Variant | Removed Section | Top 5% | Top 10% | Top 15% | Top 20% | Top 25% |
|---------|----------------|--------|---------|---------|---------|---------|
| **Full (baseline)** | — | 38.8% | 42.5% | 52.0% | 54.5% | 57.1% |
| *No domain (lower bound)* | *all sections* | 28.0% (-10.8pp) | 32.5% (-10.0pp) | 37.9% (-14.1pp) | 40.9% (-13.6pp) | 46.1% (-10.9pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 33.5% (-5.3pp) | 36.3% (-6.3pp) | 47.2% (-4.8pp) | 49.7% (-4.8pp) | 54.0% (-3.1pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 37.2% (-1.6pp) | 40.0% (-2.5pp) | 48.3% (-3.7pp) | 51.7% (-2.8pp) | 56.8% (-0.3pp) |
| `no-section6-publication` | S6: publication | 36.5% (-2.3pp) | 40.3% (-2.3pp) | 50.7% (-1.3pp) | 53.7% (-0.8pp) | 58.3% (+1.2pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 38.3% (-0.5pp) | 42.8% (+0.3pp) | 49.3% (-2.7pp) | 52.4% (-2.1pp) | 53.2% (-3.9pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 37.7% (-1.1pp) | 41.1% (-1.5pp) | 51.5% (-0.5pp) | 54.0% (-0.5pp) | 57.2% (+0.1pp) |
| `no-section5-method-name` | S5: method_name | 38.7% (-0.1pp) | 42.7% (+0.1pp) | 53.3% (+1.3pp) | 55.5% (+0.9pp) | 58.4% (+1.3pp) |
| `no-section7-variants-number` | S7: variants_number | 39.6% (+0.8pp) | 43.5% (+0.9pp) | 52.9% (+0.9pp) | 55.7% (+1.2pp) | 59.7% (+2.7pp) |

## Rank Fraction / Reverse Rank Fraction / NRS

- Rank Fraction: `r / M` where smaller is better.
- Reverse Rank Fraction: `(M - r) / M` where larger is better.
- Normalized Ranking Score: `NRS = (M - r) / (M - 1)` where larger is better.

| Variant | Removed Section | Modal r / M | Modal (M - r) / M | Modal NRS | Trial r / M | Trial (M - r) / M | Trial NRS |
|---------|----------------|-------------|-------------------|-----------|-------------|-------------------|-----------|
| **Full (baseline)** | — | 0.3910 | 0.6090 | 0.6995 | 0.3909 | 0.6091 | 0.7032 |
| *No domain (lower bound)* | *all sections* | 0.4806 (+0.0895) | 0.5194 (-0.0895) | 0.5860 (-0.1135) | 0.4882 (+0.0973) | 0.5118 (-0.0973) | 0.5771 (-0.1261) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 0.4410 (+0.0499) | 0.5590 (-0.0499) | 0.6410 (-0.0585) | 0.4343 (+0.0434) | 0.5657 (-0.0434) | 0.6472 (-0.0560) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 0.4139 (+0.0228) | 0.5861 (-0.0228) | 0.6653 (-0.0342) | 0.4116 (+0.0207) | 0.5884 (-0.0207) | 0.6725 (-0.0307) |
| `no-section6-publication` | S6: publication | 0.4184 (+0.0274) | 0.5816 (-0.0274) | 0.6765 (-0.0230) | 0.4049 (+0.0140) | 0.5951 (-0.0140) | 0.6885 (-0.0147) |
| `no-section2-performance-covariates` | S2: performance / covariates | 0.4078 (+0.0168) | 0.5922 (-0.0168) | 0.6731 (-0.0264) | 0.4160 (+0.0251) | 0.5840 (-0.0251) | 0.6674 (-0.0358) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 0.4000 (+0.0089) | 0.6000 (-0.0089) | 0.6993 (-0.0002) | 0.4038 (+0.0129) | 0.5962 (-0.0129) | 0.6910 (-0.0122) |
| `no-section5-method-name` | S5: method_name | 0.4033 (+0.0123) | 0.5967 (-0.0123) | 0.6943 (-0.0052) | 0.3966 (+0.0057) | 0.6034 (-0.0057) | 0.6977 (-0.0055) |
| `no-section7-variants-number` | S7: variants_number | 0.3884 (-0.0026) | 0.6116 (+0.0026) | 0.7079 (+0.0084) | 0.3955 (+0.0046) | 0.6045 (-0.0046) | 0.6991 (-0.0041) |

## Section Importance Ranking (by Hit@1 drop)

Sections sorted by the magnitude of Hit@1 drop when removed (largest drop = most important):

1. **S4: training_cohorts / ancestry** (`no-section4-training-cohorts-ancestry`): Hit@1 -2.7pp, NRS -5.9pp
2. **S1: trait / endpoint** (`no-section1-trait-endpoint`): Hit@1 -1.3pp, NRS -3.4pp
3. **S6: publication** (`no-section6-publication`): Hit@1 -1.3pp, NRS -2.3pp
4. **S2: performance / covariates** (`no-section2-performance-covariates`): Hit@1 0.0pp, NRS -2.6pp
5. **S3: validation_sample_size** (`no-section3-validation-sample-size`): Hit@1 +2.7pp, NRS -0.0pp
6. **S5: method_name** (`no-section5-method-name`): Hit@1 +2.7pp, NRS -0.5pp
7. **S7: variants_number** (`no-section7-variants-number`): Hit@1 +2.7pp, NRS +0.8pp

## Per-Disease Impact Analysis

For each variant, which diseases changed from Hit to Miss (regressions) or Miss to Hit (improvements) at Hit@1 compared to the full baseline.

### `no-section4-training-cohorts-ancestry` (S4: training_cohorts / ancestry)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, kidney failure, otosclerosis, urolithiasis
- **Improvements** (Miss->Hit): blood coagulation disease, psoriatic arthritis
- Net: -2 diseases

### `no-section1-trait-endpoint` (S1: trait / endpoint)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, otosclerosis
- **Improvements** (Miss->Hit): obesity
- Net: -1 diseases

### `no-section6-publication` (S6: publication)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, kidney failure, late-onset alzheimer's disease
- **Improvements** (Miss->Hit): blood coagulation disease, psoriatic arthritis
- Net: -1 diseases

### `no-section2-performance-covariates` (S2: performance / covariates)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, kidney failure, late-onset alzheimer's disease, otosclerosis
- **Improvements** (Miss->Hit): blood coagulation disease, heart failure, obesity, sleep apnea
- Net: +0 diseases

### `no-section3-validation-sample-size` (S3: validation_sample_size)

- **Regressions** (Hit->Miss): kidney failure
- **Improvements** (Miss->Hit): depressive disorder, obesity, psoriatic arthritis
- Net: +2 diseases

### `no-section5-method-name` (S5: method_name)

- **Regressions** (Hit->Miss): late-onset alzheimer's disease
- **Improvements** (Miss->Hit): blood coagulation disease, obesity, psoriatic arthritis
- Net: +2 diseases

### `no-section7-variants-number` (S7: variants_number)

- **Regressions** (Hit->Miss): otosclerosis
- **Improvements** (Miss->Hit): blood coagulation disease, obesity, psoriatic arthritis
- Net: +2 diseases

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
- parkinson disease
- peripheral vascular disease
- preeclampsia
- skin carcinoma in situ

### Fragile diseases (Hit@1 in baseline but Miss in at least one variant)

- **dilated cardiomyopathy**: lost in `no-section1-trait-endpoint`, `no-section2-performance-covariates`, `no-section4-training-cohorts-ancestry`, `no-section6-publication`
- **kidney failure**: lost in `no-section2-performance-covariates`, `no-section3-validation-sample-size`, `no-section4-training-cohorts-ancestry`, `no-section6-publication`
- **late-onset alzheimer's disease**: lost in `no-section2-performance-covariates`, `no-section5-method-name`, `no-section6-publication`
- **otosclerosis**: lost in `no-section1-trait-endpoint`, `no-section2-performance-covariates`, `no-section4-training-cohorts-ancestry`, `no-section7-variants-number`
- **urolithiasis**: lost in `no-section4-training-cohorts-ancestry`
