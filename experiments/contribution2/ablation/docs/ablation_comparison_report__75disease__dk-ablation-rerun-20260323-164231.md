# Domain Knowledge Ablation Study Report

## Overview

Each row represents a leave-one-out ablation: the full domain knowledge document with exactly one ## section removed. Delta columns show the change relative to the full-domain baseline.

Hit metrics are reported for both modal selections and all trials. Ranking metrics use the AoU benchmark rank `r` within a disease-specific candidate pool of size `M`.

## Modal Hit@1-5

| Variant | Removed Section | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|---------|----------------|-------|-------|-------|-------|-------|
| **Full (baseline)** | — | 29.3% | 52.0% | 58.7% | 66.7% | 70.7% |
| *No domain (lower bound)* | *all sections* | 24.0% (-5.3pp) | 37.3% (-14.7pp) | 56.0% (-2.7pp) | 62.7% (-4.0pp) | 64.0% (-6.7pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 25.3% (-4.0pp) | 49.3% (-2.7pp) | 60.0% (+1.3pp) | 69.3% (+2.7pp) | 72.0% (+1.3pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 28.0% (-1.3pp) | 49.3% (-2.7pp) | 57.3% (-1.3pp) | 65.3% (-1.3pp) | 69.3% (-1.3pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 28.0% (-1.3pp) | 48.0% (-4.0pp) | 56.0% (-2.7pp) | 62.7% (-4.0pp) | 70.7% (0.0pp) |
| `no-section5-method-name` | S5: method_name | 28.0% (-1.3pp) | 48.0% (-4.0pp) | 58.7% (0.0pp) | 69.3% (+2.7pp) | 72.0% (+1.3pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 29.3% (0.0pp) | 52.0% (0.0pp) | 60.0% (+1.3pp) | 69.3% (+2.7pp) | 72.0% (+1.3pp) |
| `no-section6-publication` | S6: publication | 29.3% (0.0pp) | 50.7% (-1.3pp) | 57.3% (-1.3pp) | 69.3% (+2.7pp) | 72.0% (+1.3pp) |
| `no-section7-variants-number` | S7: variants_number | 29.3% (0.0pp) | 52.0% (0.0pp) | 60.0% (+1.3pp) | 68.0% (+1.3pp) | 70.7% (0.0pp) |

## Trial Hit@1-5

| Variant | Removed Section | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|---------|----------------|-------|-------|-------|-------|-------|
| **Full (baseline)** | — | 29.5% | 53.3% | 60.3% | 68.1% | 71.7% |
| *No domain (lower bound)* | *all sections* | 23.7% (-5.7pp) | 36.0% (-17.3pp) | 54.1% (-6.1pp) | 61.6% (-6.5pp) | 63.9% (-7.9pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 28.4% (-1.1pp) | 50.4% (-2.9pp) | 59.9% (-0.4pp) | 68.4% (+0.3pp) | 71.3% (-0.4pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 27.7% (-1.7pp) | 49.5% (-3.9pp) | 57.2% (-3.1pp) | 65.3% (-2.8pp) | 69.9% (-1.9pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 27.9% (-1.6pp) | 48.8% (-4.5pp) | 57.1% (-3.2pp) | 64.7% (-3.5pp) | 70.9% (-0.8pp) |
| `no-section5-method-name` | S5: method_name | 30.5% (+1.1pp) | 51.3% (-2.0pp) | 61.5% (+1.2pp) | 70.5% (+2.4pp) | 73.7% (+2.0pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 29.7% (+0.3pp) | 52.3% (-1.1pp) | 60.5% (+0.3pp) | 68.8% (+0.7pp) | 72.8% (+1.1pp) |
| `no-section6-publication` | S6: publication | 30.0% (+0.5pp) | 52.5% (-0.8pp) | 60.5% (+0.3pp) | 70.0% (+1.9pp) | 73.1% (+1.3pp) |
| `no-section7-variants-number` | S7: variants_number | 29.1% (-0.4pp) | 52.9% (-0.4pp) | 61.5% (+1.2pp) | 69.5% (+1.3pp) | 72.5% (+0.8pp) |

## Modal Top 5-25% Hit

| Variant | Removed Section | Top 5% | Top 10% | Top 15% | Top 20% | Top 25% |
|---------|----------------|--------|---------|---------|---------|---------|
| **Full (baseline)** | — | 37.3% | 38.7% | 50.7% | 53.3% | 57.3% |
| *No domain (lower bound)* | *all sections* | 29.3% (-8.0pp) | 33.3% (-5.3pp) | 38.7% (-12.0pp) | 41.3% (-12.0pp) | 46.7% (-10.7pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 36.0% (-1.3pp) | 40.0% (+1.3pp) | 49.3% (-1.3pp) | 50.7% (-2.7pp) | 56.0% (-1.3pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 37.3% (0.0pp) | 38.7% (0.0pp) | 46.7% (-4.0pp) | 48.0% (-5.3pp) | 49.3% (-8.0pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 37.3% (0.0pp) | 40.0% (+1.3pp) | 46.7% (-4.0pp) | 50.7% (-2.7pp) | 53.3% (-4.0pp) |
| `no-section5-method-name` | S5: method_name | 36.0% (-1.3pp) | 37.3% (-1.3pp) | 45.3% (-5.3pp) | 49.3% (-4.0pp) | 53.3% (-4.0pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 38.7% (+1.3pp) | 41.3% (+2.7pp) | 52.0% (+1.3pp) | 54.7% (+1.3pp) | 57.3% (0.0pp) |
| `no-section6-publication` | S6: publication | 38.7% (+1.3pp) | 41.3% (+2.7pp) | 49.3% (-1.3pp) | 50.7% (-2.7pp) | 56.0% (-1.3pp) |
| `no-section7-variants-number` | S7: variants_number | 36.0% (-1.3pp) | 40.0% (+1.3pp) | 49.3% (-1.3pp) | 53.3% (0.0pp) | 57.3% (0.0pp) |

## Trial Top 5-25% Hit

| Variant | Removed Section | Top 5% | Top 10% | Top 15% | Top 20% | Top 25% |
|---------|----------------|--------|---------|---------|---------|---------|
| **Full (baseline)** | — | 37.7% | 39.6% | 50.8% | 53.7% | 57.1% |
| *No domain (lower bound)* | *all sections* | 28.0% (-9.7pp) | 32.5% (-7.1pp) | 37.9% (-12.9pp) | 40.9% (-12.8pp) | 46.1% (-10.9pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 37.2% (-0.5pp) | 39.9% (+0.3pp) | 49.5% (-1.3pp) | 51.6% (-2.1pp) | 56.1% (-0.9pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 36.1% (-1.6pp) | 38.5% (-1.1pp) | 46.8% (-4.0pp) | 48.7% (-5.1pp) | 50.3% (-6.8pp) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 36.1% (-1.6pp) | 38.9% (-0.7pp) | 47.1% (-3.7pp) | 50.0% (-3.7pp) | 52.7% (-4.4pp) |
| `no-section5-method-name` | S5: method_name | 38.7% (+0.9pp) | 40.3% (+0.7pp) | 49.6% (-1.2pp) | 53.7% (0.0pp) | 58.1% (+1.1pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 38.3% (+0.5pp) | 40.8% (+1.2pp) | 52.1% (+1.3pp) | 55.3% (+1.6pp) | 59.2% (+2.1pp) |
| `no-section6-publication` | S6: publication | 39.1% (+1.3pp) | 41.6% (+2.0pp) | 51.3% (+0.5pp) | 53.1% (-0.7pp) | 57.5% (+0.4pp) |
| `no-section7-variants-number` | S7: variants_number | 36.5% (-1.2pp) | 40.5% (+0.9pp) | 50.1% (-0.7pp) | 53.7% (0.0pp) | 58.3% (+1.2pp) |

## Rank Fraction / Reverse Rank Fraction / NRS

- Rank Fraction: `r / M` where smaller is better.
- Reverse Rank Fraction: `(M - r) / M` where larger is better.
- Normalized Ranking Score: `NRS = (M - r) / (M - 1)` where larger is better.

| Variant | Removed Section | Modal r / M | Modal (M - r) / M | Modal NRS | Trial r / M | Trial (M - r) / M | Trial NRS |
|---------|----------------|-------------|-------------------|-----------|-------------|-------------------|-----------|
| **Full (baseline)** | — | 0.4070 | 0.5930 | 0.6881 | 0.4051 | 0.5949 | 0.6890 |
| *No domain (lower bound)* | *all sections* | 0.4806 (+0.0735) | 0.5194 (-0.0735) | 0.5860 (-0.1021) | 0.4882 (+0.0831) | 0.5118 (-0.0831) | 0.5771 (-0.1119) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 0.4204 (+0.0134) | 0.5796 (-0.0134) | 0.6625 (-0.0256) | 0.4147 (+0.0096) | 0.5853 (-0.0096) | 0.6718 (-0.0171) |
| `no-section2-performance-covariates` | S2: performance / covariates | 0.4342 (+0.0271) | 0.5658 (-0.0271) | 0.6442 (-0.0438) | 0.4320 (+0.0269) | 0.5680 (-0.0269) | 0.6479 (-0.0411) |
| `no-section4-training-cohorts-ancestry` | S4: training_cohorts / ancestry | 0.4379 (+0.0309) | 0.5621 (-0.0309) | 0.6507 (-0.0374) | 0.4368 (+0.0317) | 0.5632 (-0.0317) | 0.6505 (-0.0385) |
| `no-section5-method-name` | S5: method_name | 0.4196 (+0.0126) | 0.5804 (-0.0126) | 0.6708 (-0.0173) | 0.3966 (-0.0085) | 0.6034 (+0.0085) | 0.6951 (+0.0061) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 0.4025 (-0.0045) | 0.5975 (+0.0045) | 0.6989 (+0.0108) | 0.4032 (-0.0020) | 0.5968 (+0.0020) | 0.6955 (+0.0065) |
| `no-section6-publication` | S6: publication | 0.4115 (+0.0045) | 0.5885 (-0.0045) | 0.6811 (-0.0070) | 0.4027 (-0.0024) | 0.5973 (+0.0024) | 0.6893 (+0.0004) |
| `no-section7-variants-number` | S7: variants_number | 0.4078 (+0.0008) | 0.5922 (-0.0008) | 0.6870 (-0.0011) | 0.4013 (-0.0039) | 0.5987 (+0.0039) | 0.6925 (+0.0036) |

## Section Importance Ranking (by Hit@1 drop)

Sections sorted by the magnitude of Hit@1 drop when removed (largest drop = most important):

1. **S1: trait / endpoint** (`no-section1-trait-endpoint`): Hit@1 -4.0pp, NRS -2.6pp
2. **S2: performance / covariates** (`no-section2-performance-covariates`): Hit@1 -1.3pp, NRS -4.4pp
3. **S4: training_cohorts / ancestry** (`no-section4-training-cohorts-ancestry`): Hit@1 -1.3pp, NRS -3.7pp
4. **S5: method_name** (`no-section5-method-name`): Hit@1 -1.3pp, NRS -1.7pp
5. **S3: validation_sample_size** (`no-section3-validation-sample-size`): Hit@1 0.0pp, NRS +1.1pp
6. **S6: publication** (`no-section6-publication`): Hit@1 0.0pp, NRS -0.7pp
7. **S7: variants_number** (`no-section7-variants-number`): Hit@1 0.0pp, NRS -0.1pp

## Per-Disease Impact Analysis

For each variant, which diseases changed from Hit to Miss (regressions) or Miss to Hit (improvements) at Hit@1 compared to the full baseline.

### `no-section1-trait-endpoint` (S1: trait / endpoint)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, sleep apnea, urolithiasis
- Net: -3 diseases

### `no-section2-performance-covariates` (S2: performance / covariates)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, late-onset alzheimer's disease, psoriatic arthritis
- **Improvements** (Miss->Hit): kidney failure, obesity
- Net: -1 diseases

### `no-section4-training-cohorts-ancestry` (S4: training_cohorts / ancestry)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, sleep apnea
- **Improvements** (Miss->Hit): kidney failure
- Net: -1 diseases

### `no-section5-method-name` (S5: method_name)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, late-onset alzheimer's disease
- **Improvements** (Miss->Hit): kidney failure
- Net: -1 diseases

### `no-section3-validation-sample-size` (S3: validation_sample_size)

- **Regressions** (Hit->Miss): dilated cardiomyopathy, sleep apnea
- **Improvements** (Miss->Hit): kidney failure, otosclerosis
- Net: +0 diseases

### `no-section6-publication` (S6: publication)

- **Regressions** (Hit->Miss): sleep apnea
- **Improvements** (Miss->Hit): kidney failure
- Net: +0 diseases

### `no-section7-variants-number` (S7: variants_number)

- **Regressions** (Hit->Miss): sleep apnea
- **Improvements** (Miss->Hit): obesity
- Net: +0 diseases

## Disease Robustness Analysis

### Robust diseases (Hit@1 in baseline AND all ablation variants)

- alcohol dependence
- bipolar disorder
- blood coagulation disease
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

- **dilated cardiomyopathy**: lost in `no-section1-trait-endpoint`, `no-section2-performance-covariates`, `no-section3-validation-sample-size`, `no-section4-training-cohorts-ancestry`, `no-section5-method-name`
- **late-onset alzheimer's disease**: lost in `no-section2-performance-covariates`, `no-section5-method-name`
- **psoriatic arthritis**: lost in `no-section2-performance-covariates`
- **sleep apnea**: lost in `no-section1-trait-endpoint`, `no-section3-validation-sample-size`, `no-section4-training-cohorts-ancestry`, `no-section6-publication`, `no-section7-variants-number`
- **urolithiasis**: lost in `no-section1-trait-endpoint`
