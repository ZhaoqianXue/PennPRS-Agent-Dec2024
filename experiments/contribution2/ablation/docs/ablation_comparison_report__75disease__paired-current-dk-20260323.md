# Domain Knowledge Ablation Study Report

## Overview

Each row represents a leave-one-out ablation: the full domain knowledge document with exactly one ## section removed. Delta columns show the change relative to the full-domain baseline.

Hit metrics are reported for both modal selections and all trials. Ranking metrics use the AoU benchmark rank `r` within a disease-specific candidate pool of size `M`.

## Modal Hit@1-5

| Variant | Removed Section | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|---------|----------------|-------|-------|-------|-------|-------|
| **Full (baseline)** | — | 33.3% | 56.0% | 62.7% | 73.3% | 74.7% |
| *No domain (lower bound)* | *all sections* | 24.0% (-9.3pp) | 37.3% (-18.7pp) | 56.0% (-6.7pp) | 62.7% (-10.7pp) | 64.0% (-10.7pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 29.3% (-4.0pp) | 57.3% (+1.3pp) | 65.3% (+2.7pp) | 73.3% (0.0pp) | 76.0% (+1.3pp) |
| `no-section4-training-cohorts` | S4: training_cohorts | 29.3% (-4.0pp) | 53.3% (-2.7pp) | 61.3% (-1.3pp) | 72.0% (-1.3pp) | 76.0% (+1.3pp) |
| `no-critical-selection-evidence` | Critical selection evidence | 32.0% (-1.3pp) | 60.0% (+4.0pp) | 64.0% (+1.3pp) | 70.7% (-2.7pp) | 74.7% (0.0pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 32.0% (-1.3pp) | 58.7% (+2.7pp) | 65.3% (+2.7pp) | 73.3% (0.0pp) | 77.3% (+2.7pp) |
| `no-section7-publication` | S7: publication | 32.0% (-1.3pp) | 56.0% (0.0pp) | 61.3% (-1.3pp) | 70.7% (-2.7pp) | 76.0% (+1.3pp) |
| `no-section8-variants-number` | S8: variants_number | 33.3% (0.0pp) | 58.7% (+2.7pp) | 65.3% (+2.7pp) | 73.3% (0.0pp) | 74.7% (0.0pp) |
| `no-section5-method-name` | S5: method_name | 34.7% (+1.3pp) | 54.7% (-1.3pp) | 64.0% (+1.3pp) | 70.7% (-2.7pp) | 73.3% (-1.3pp) |
| `no-section9-disease-family` | S9: disease-family patterns | 34.7% (+1.3pp) | 54.7% (-1.3pp) | 60.0% (-2.7pp) | 73.3% (0.0pp) | 77.3% (+2.7pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 36.0% (+2.7pp) | 57.3% (+1.3pp) | 65.3% (+2.7pp) | 72.0% (-1.3pp) | 76.0% (+1.3pp) |
| `no-section6-ancestry` | S6: ancestry | 37.3% (+4.0pp) | 58.7% (+2.7pp) | 65.3% (+2.7pp) | 77.3% (+4.0pp) | 78.7% (+4.0pp) |

## Trial Hit@1-5

| Variant | Removed Section | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|---------|----------------|-------|-------|-------|-------|-------|
| **Full (baseline)** | — | 34.3% | 57.2% | 64.0% | 73.2% | 75.6% |
| *No domain (lower bound)* | *all sections* | 23.7% (-10.5pp) | 36.0% (-21.2pp) | 54.1% (-9.9pp) | 61.6% (-11.6pp) | 63.9% (-11.7pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 31.3% (-2.9pp) | 57.7% (+0.5pp) | 64.5% (+0.5pp) | 73.2% (0.0pp) | 76.4% (+0.8pp) |
| `no-section4-training-cohorts` | S4: training_cohorts | 31.6% (-2.7pp) | 55.9% (-1.3pp) | 63.2% (-0.8pp) | 73.1% (-0.1pp) | 76.7% (+1.1pp) |
| `no-critical-selection-evidence` | Critical selection evidence | 32.5% (-1.7pp) | 58.9% (+1.7pp) | 64.3% (+0.3pp) | 72.0% (-1.2pp) | 75.6% (0.0pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 33.2% (-1.1pp) | 57.3% (+0.1pp) | 64.0% (0.0pp) | 72.3% (-0.9pp) | 76.0% (+0.4pp) |
| `no-section7-publication` | S7: publication | 32.1% (-2.1pp) | 56.5% (-0.7pp) | 62.7% (-1.3pp) | 71.7% (-1.5pp) | 76.5% (+0.9pp) |
| `no-section8-variants-number` | S8: variants_number | 32.9% (-1.3pp) | 56.5% (-0.7pp) | 63.5% (-0.5pp) | 72.4% (-0.8pp) | 74.4% (-1.2pp) |
| `no-section5-method-name` | S5: method_name | 33.2% (-1.1pp) | 54.4% (-2.8pp) | 62.5% (-1.5pp) | 70.7% (-2.5pp) | 73.5% (-2.1pp) |
| `no-section9-disease-family` | S9: disease-family patterns | 34.9% (+0.7pp) | 57.1% (-0.1pp) | 63.3% (-0.7pp) | 74.4% (+1.2pp) | 78.5% (+2.9pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 34.7% (+0.4pp) | 56.8% (-0.4pp) | 64.7% (+0.7pp) | 72.5% (-0.7pp) | 76.5% (+0.9pp) |
| `no-section6-ancestry` | S6: ancestry | 35.9% (+1.6pp) | 57.6% (+0.4pp) | 64.9% (+0.9pp) | 74.3% (+1.1pp) | 76.3% (+0.7pp) |

## Modal Top 5-25% Hit

| Variant | Removed Section | Top 5% | Top 10% | Top 15% | Top 20% | Top 25% |
|---------|----------------|--------|---------|---------|---------|---------|
| **Full (baseline)** | — | 42.7% | 45.3% | 54.7% | 56.0% | 60.0% |
| *No domain (lower bound)* | *all sections* | 29.3% (-13.3pp) | 33.3% (-12.0pp) | 38.7% (-16.0pp) | 41.3% (-14.7pp) | 46.7% (-13.3pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 37.3% (-5.3pp) | 42.7% (-2.7pp) | 53.3% (-1.3pp) | 57.3% (+1.3pp) | 62.7% (+2.7pp) |
| `no-section4-training-cohorts` | S4: training_cohorts | 38.7% (-4.0pp) | 42.7% (-2.7pp) | 54.7% (0.0pp) | 56.0% (0.0pp) | 60.0% (0.0pp) |
| `no-critical-selection-evidence` | Critical selection evidence | 42.7% (0.0pp) | 45.3% (0.0pp) | 56.0% (+1.3pp) | 57.3% (+1.3pp) | 57.3% (-2.7pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 40.0% (-2.7pp) | 48.0% (+2.7pp) | 57.3% (+2.7pp) | 60.0% (+4.0pp) | 60.0% (0.0pp) |
| `no-section7-publication` | S7: publication | 41.3% (-1.3pp) | 44.0% (-1.3pp) | 53.3% (-1.3pp) | 56.0% (0.0pp) | 58.7% (-1.3pp) |
| `no-section8-variants-number` | S8: variants_number | 42.7% (0.0pp) | 44.0% (-1.3pp) | 54.7% (0.0pp) | 56.0% (0.0pp) | 58.7% (-1.3pp) |
| `no-section5-method-name` | S5: method_name | 44.0% (+1.3pp) | 45.3% (0.0pp) | 54.7% (0.0pp) | 56.0% (0.0pp) | 60.0% (0.0pp) |
| `no-section9-disease-family` | S9: disease-family patterns | 44.0% (+1.3pp) | 46.7% (+1.3pp) | 54.7% (0.0pp) | 57.3% (+1.3pp) | 58.7% (-1.3pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 44.0% (+1.3pp) | 46.7% (+1.3pp) | 57.3% (+2.7pp) | 60.0% (+4.0pp) | 61.3% (+1.3pp) |
| `no-section6-ancestry` | S6: ancestry | 45.3% (+2.7pp) | 49.3% (+4.0pp) | 57.3% (+2.7pp) | 60.0% (+4.0pp) | 64.0% (+4.0pp) |

## Trial Top 5-25% Hit

| Variant | Removed Section | Top 5% | Top 10% | Top 15% | Top 20% | Top 25% |
|---------|----------------|--------|---------|---------|---------|---------|
| **Full (baseline)** | — | 43.1% | 45.5% | 54.8% | 56.8% | 59.6% |
| *No domain (lower bound)* | *all sections* | 28.0% (-15.1pp) | 32.5% (-12.9pp) | 37.9% (-16.9pp) | 40.9% (-15.9pp) | 46.1% (-13.5pp) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 40.5% (-2.5pp) | 44.4% (-1.1pp) | 54.4% (-0.4pp) | 57.2% (+0.4pp) | 62.3% (+2.7pp) |
| `no-section4-training-cohorts` | S4: training_cohorts | 40.1% (-2.9pp) | 44.8% (-0.7pp) | 55.7% (+0.9pp) | 57.7% (+0.9pp) | 61.5% (+1.9pp) |
| `no-critical-selection-evidence` | Critical selection evidence | 42.0% (-1.1pp) | 45.5% (0.0pp) | 55.2% (+0.4pp) | 57.3% (+0.5pp) | 59.7% (+0.1pp) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 41.5% (-1.6pp) | 46.5% (+1.1pp) | 54.9% (+0.1pp) | 57.5% (+0.7pp) | 59.7% (+0.1pp) |
| `no-section7-publication` | S7: publication | 41.2% (-1.9pp) | 45.1% (-0.4pp) | 55.7% (+0.9pp) | 58.3% (+1.5pp) | 61.5% (+1.9pp) |
| `no-section8-variants-number` | S8: variants_number | 42.1% (-0.9pp) | 44.0% (-1.5pp) | 53.6% (-1.2pp) | 54.9% (-1.9pp) | 58.8% (-0.8pp) |
| `no-section5-method-name` | S5: method_name | 41.5% (-1.6pp) | 43.6% (-1.9pp) | 53.9% (-0.9pp) | 55.7% (-1.1pp) | 60.5% (+0.9pp) |
| `no-section9-disease-family` | S9: disease-family patterns | 44.3% (+1.2pp) | 46.9% (+1.5pp) | 56.5% (+1.7pp) | 59.5% (+2.7pp) | 62.0% (+2.4pp) |
| `no-section2-performance-covariates` | S2: performance / covariates | 42.8% (-0.3pp) | 46.4% (+0.9pp) | 56.5% (+1.7pp) | 58.9% (+2.1pp) | 61.2% (+1.6pp) |
| `no-section6-ancestry` | S6: ancestry | 43.7% (+0.7pp) | 46.1% (+0.7pp) | 55.7% (+0.9pp) | 58.0% (+1.2pp) | 61.6% (+2.0pp) |

## Rank Fraction / Reverse Rank Fraction / NRS

- Rank Fraction: `r / M` where smaller is better.
- Reverse Rank Fraction: `(M - r) / M` where larger is better.
- Normalized Ranking Score: `NRS = (M - r) / (M - 1)` where larger is better.

| Variant | Removed Section | Modal r / M | Modal (M - r) / M | Modal NRS | Trial r / M | Trial (M - r) / M | Trial NRS |
|---------|----------------|-------------|-------------------|-----------|-------------|-------------------|-----------|
| **Full (baseline)** | — | 0.3835 | 0.6165 | 0.7099 | 0.3829 | 0.6171 | 0.7122 |
| *No domain (lower bound)* | *all sections* | 0.4806 (+0.0971) | 0.5194 (-0.0971) | 0.5860 (-0.1239) | 0.4882 (+0.1053) | 0.5118 (-0.1053) | 0.5771 (-0.1351) |
| `no-section1-trait-endpoint` | S1: trait / endpoint | 0.3832 (-0.0003) | 0.6168 (+0.0003) | 0.7008 (-0.0091) | 0.3806 (-0.0023) | 0.6194 (+0.0023) | 0.7092 (-0.0030) |
| `no-section4-training-cohorts` | S4: training_cohorts | 0.3964 (+0.0129) | 0.6036 (-0.0129) | 0.7033 (-0.0066) | 0.3839 (+0.0010) | 0.6161 (-0.0010) | 0.7175 (+0.0053) |
| `no-critical-selection-evidence` | Critical selection evidence | 0.3898 (+0.0063) | 0.6102 (-0.0063) | 0.7007 (-0.0092) | 0.3824 (-0.0005) | 0.6176 (+0.0005) | 0.7092 (-0.0030) |
| `no-section3-validation-sample-size` | S3: validation_sample_size | 0.3737 (-0.0098) | 0.6263 (+0.0098) | 0.7200 (+0.0101) | 0.3829 (+0.0000) | 0.6171 (-0.0000) | 0.7111 (-0.0011) |
| `no-section7-publication` | S7: publication | 0.3971 (+0.0136) | 0.6029 (-0.0136) | 0.7029 (-0.0070) | 0.3815 (-0.0014) | 0.6185 (+0.0014) | 0.7202 (+0.0080) |
| `no-section8-variants-number` | S8: variants_number | 0.3809 (-0.0025) | 0.6191 (+0.0025) | 0.7113 (+0.0014) | 0.3909 (+0.0079) | 0.6091 (-0.0079) | 0.7024 (-0.0098) |
| `no-section5-method-name` | S5: method_name | 0.3766 (-0.0069) | 0.6234 (+0.0069) | 0.7274 (+0.0174) | 0.3810 (-0.0019) | 0.6190 (+0.0019) | 0.7211 (+0.0089) |
| `no-section9-disease-family` | S9: disease-family patterns | 0.3809 (-0.0025) | 0.6191 (+0.0025) | 0.7208 (+0.0108) | 0.3722 (-0.0108) | 0.6278 (+0.0108) | 0.7294 (+0.0172) |
| `no-section2-performance-covariates` | S2: performance / covariates | 0.3683 (-0.0152) | 0.6317 (+0.0152) | 0.7246 (+0.0147) | 0.3750 (-0.0079) | 0.6250 (+0.0079) | 0.7169 (+0.0047) |
| `no-section6-ancestry` | S6: ancestry | 0.3687 (-0.0148) | 0.6313 (+0.0148) | 0.7352 (+0.0253) | 0.3816 (-0.0013) | 0.6184 (+0.0013) | 0.7161 (+0.0039) |

## Section Importance Ranking (by Hit@1 drop)

Sections sorted by the magnitude of Hit@1 drop when removed (largest drop = most important):

1. **S1: trait / endpoint** (`no-section1-trait-endpoint`): Hit@1 -4.0pp, NRS -0.9pp
2. **S4: training_cohorts** (`no-section4-training-cohorts`): Hit@1 -4.0pp, NRS -0.7pp
3. **Critical selection evidence** (`no-critical-selection-evidence`): Hit@1 -1.3pp, NRS -0.9pp
4. **S3: validation_sample_size** (`no-section3-validation-sample-size`): Hit@1 -1.3pp, NRS +1.0pp
5. **S7: publication** (`no-section7-publication`): Hit@1 -1.3pp, NRS -0.7pp
6. **S8: variants_number** (`no-section8-variants-number`): Hit@1 0.0pp, NRS +0.1pp
7. **S5: method_name** (`no-section5-method-name`): Hit@1 +1.3pp, NRS +1.7pp
8. **S9: disease-family patterns** (`no-section9-disease-family`): Hit@1 +1.3pp, NRS +1.1pp
9. **S2: performance / covariates** (`no-section2-performance-covariates`): Hit@1 +2.7pp, NRS +1.5pp
10. **S6: ancestry** (`no-section6-ancestry`): Hit@1 +4.0pp, NRS +2.5pp

## Per-Disease Impact Analysis

For each variant, which diseases changed from Hit to Miss (regressions) or Miss to Hit (improvements) at Hit@1 compared to the full baseline.

### `no-section1-trait-endpoint` (S1: trait / endpoint)

- **Regressions** (Hit->Miss): blood coagulation disease, chronic obstructive pulmonary disease, kidney failure, otosclerosis
- **Improvements** (Miss->Hit): heart failure
- Net: -3 diseases

### `no-section4-training-cohorts` (S4: training_cohorts)

- **Regressions** (Hit->Miss): blood coagulation disease, chronic obstructive pulmonary disease, depressive disorder, kidney failure
- **Improvements** (Miss->Hit): psoriatic arthritis
- Net: -3 diseases

### `no-critical-selection-evidence` (Critical selection evidence)

- **Regressions** (Hit->Miss): blood coagulation disease
- Net: -1 diseases

### `no-section3-validation-sample-size` (S3: validation_sample_size)

- **Regressions** (Hit->Miss): sleep apnea
- Net: -1 diseases

### `no-section7-publication` (S7: publication)

- **Regressions** (Hit->Miss): blood coagulation disease, depressive disorder
- **Improvements** (Miss->Hit): psoriatic arthritis
- Net: -1 diseases

### `no-section8-variants-number` (S8: variants_number)

- **Regressions** (Hit->Miss): blood coagulation disease
- **Improvements** (Miss->Hit): heart failure
- Net: +0 diseases

### `no-section5-method-name` (S5: method_name)

- **Regressions** (Hit->Miss): depressive disorder
- **Improvements** (Miss->Hit): dilated cardiomyopathy, psoriatic arthritis
- Net: +1 diseases

### `no-section9-disease-family` (S9: disease-family patterns)

- **Regressions** (Hit->Miss): depressive disorder, late-onset alzheimer's disease, obesity
- **Improvements** (Miss->Hit): abdominal aortic aneurysm, heart failure, hypothyroidism, psoriatic arthritis
- Net: +1 diseases

### `no-section2-performance-covariates` (S2: performance / covariates)

- **Regressions** (Hit->Miss): kidney failure
- **Improvements** (Miss->Hit): dilated cardiomyopathy, heart failure, osteoporosis
- Net: +2 diseases

### `no-section6-ancestry` (S6: ancestry)

- **Improvements** (Miss->Hit): heart failure, osteoporosis, psoriatic arthritis
- Net: +3 diseases

## Disease Robustness Analysis

### Robust diseases (Hit@1 in baseline AND all ablation variants)

- alcohol dependence
- aortic stenosis
- bipolar disorder
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
- urolithiasis

### Fragile diseases (Hit@1 in baseline but Miss in at least one variant)

- **blood coagulation disease**: lost in `no-critical-selection-evidence`, `no-section1-trait-endpoint`, `no-section4-training-cohorts`, `no-section7-publication`, `no-section8-variants-number`
- **chronic obstructive pulmonary disease**: lost in `no-section1-trait-endpoint`, `no-section4-training-cohorts`
- **depressive disorder**: lost in `no-section4-training-cohorts`, `no-section5-method-name`, `no-section7-publication`, `no-section9-disease-family`
- **kidney failure**: lost in `no-section1-trait-endpoint`, `no-section2-performance-covariates`, `no-section4-training-cohorts`
- **late-onset alzheimer's disease**: lost in `no-section9-disease-family`
- **obesity**: lost in `no-section9-disease-family`
- **otosclerosis**: lost in `no-section1-trait-endpoint`
- **sleep apnea**: lost in `no-section3-validation-sample-size`
