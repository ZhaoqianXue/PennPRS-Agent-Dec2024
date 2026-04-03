# Contribution3: Continuous-to-Continuous Cross List Report (loinccode)

## Terminology

- **Target trait**: Trait being predicted / transferred into
  - Continuous target traits here are restricted to `include_in_analysis == 1` in `prs_incrementalr2_metadata`
  - **Type A**: target traits **without self incremental R2**
  - **Type B**: target traits **with self incremental R2**
- **Cross trait**: Trait whose PRS models are recommended for the target trait (continuous trait resolved from LOINC metadata mapping)
- PGS models with unknown source ontology are **excluded**

## Cross-list workflow

1. **Partition screened target traits** into Type A (without self incremental R2) and Type B (with self incremental R2).
2. **Retain cross-list target traits** — Type A target traits need at least one qualifying cross model; Type B target traits need a cross model that beats self.
3. **Determine cross traits** — for each retained continuous target trait, link retained cross PGS → LOINC trait metadata.
4. **Cross-Trait Transfer** — evaluate whether continuous-trait PRS models can usefully transfer to the target trait.

## Selection Criterion

- Type A (without self incremental R2): require at least one non-self continuous-trait PGS model
- Type B (with self incremental R2): require at least one non-self continuous-trait PGS model with cross incremental R2 > best self incremental R2
- When self incremental R2 exists: require **cross incremental R2 − self best incremental R2 > 0.0025** per retained model
- Require **Top Cross incremental R2 > 0.02** for the target trait to enter the cross-list
- Exclude target traits with **self best incremental R2 > 0.05** (strong self PRS)

## Type A / Type B Summary

| Metric | Count |
|--------|-------|
| **Cross-list target traits** (retained Type A ∪ retained Type B) | **2** |
| — Retained Type A (Without Self incremental R2 + qualifying cross) | 0 |
| — Retained Type B (With Self incremental R2 + cross beats self) | 2 |
| Total screened rows in matrix filter | 32 |
| Type A total (Without Self incremental R2) | 0 |
| — Type A without qualifying cross | 0 |
| Type B total (With Self incremental R2) | 32 |
| — Type B self optimal | 30 |
| Any cross candidates | 2 |


## Type B: Cross-Trait PRS Beats Self

*Included in the retained cross-list target traits.*

Total: 2 target traits

| Target LOINC | Target Trait | Self Best Incremental R2 | Top Cross Incremental R2 | Improvement | Cross Trait LOINC | Top Cross Trait | N Cross Models | N Unique Cross Traits |
|--------------|--------------|--------------------------|--------------------------|-------------|-------------------|-----------------|----------------|-------------------------|
| 1884-6 | apolipoprotein b measurement | 0.038225 | 0.059508 | +0.0213 | 18262-6 | low density lipoprotein cholesterol meas | 32 | 4 |
| 1869-7 | apolipoprotein a 1 measurement | 0.01264 | 0.024816 | +0.0122 | 10835-7 | lipoprotein a measurement | 12 | 4 |

## Type B: Self Models Already Optimal

*Not included in the retained cross-list target traits (self PRS sufficient under current rules; reference only).*

Total: 30 target traits

| Target LOINC | Target Trait | Self Best Incremental R2 | Self N Models |
|--------------|--------------|--------------------------|---------------|
| 18262-6 | low density lipoprotein cholesterol measurement | 0.046121 | 121 |
| 8462-4 | diastolic blood pressure | 0.037693 | 53 |
| 62292-8 | vitamin d level | 0.034668 | 44 |
| 26478-8 | lymphocyte percentage of leukocytes | 0.031294 | 9 |
| 26511-6 | neutrophil percentage of leukocytes | 0.027413 | 9 |
| 28539-5 | mean corpuscular hemoglobin | 0.016272 | 23 |
| 713-8 | eosinophil percentage of leukocytes | 0.013458 | 9 |
| 2986-8 | testosterone measurement | 0.012353 | 10 |
| 30522-7 | c-reactive protein measurement | 0.006384 | 35 |
| 8867-4 | ventricular rate measurement | 0.006142 | 2 |
| 706-2 | basophil percentage of leukocytes | 0.005882 | 5 |
| 8480-6 | systolic blood pressure | 0.003472 | 75 |
| 711-2 | eosinophil count | 0.002844 | 28 |
| 2243-4 | estradiol measurement | 0.002454 | 11 |
| 742-7 | monocyte count | 0.001998 | 31 |
| 26474-7 | lymphocyte count | 0.001548 | 27 |
| 751-8 | neutrophil count | 0.001333 | 22 |
| 704-7 | basophil count | 0.000817 | 14 |
| 39156-5 | body mass index | 0.000722 | 125 |
| 3084-1 | uric acid measurement | 0.000332 | 2 |
| 777-3 | platelet count | 0.000162 | 26 |
| 2093-3 | total cholesterol measurement | 9.7e-05 | 70 |
| 4548-4 | hba1c measurement | 9.2e-05 | 40 |
| 718-7 | hemoglobin measurement | 6.6e-05 | 91 |
| 2571-8 | triglyceride measurement | 6e-05 | 75 |
| 2085-9 | high density lipoprotein cholesterol measurement | 5.2e-05 | 92 |
| 4544-3 | hematocrit | 5.2e-05 | 14 |
| 789-8 | erythrocyte count | 5.2e-05 | 23 |
| 786-4 | mean corpuscular hemoglobin concentration | 3.7e-05 | 6 |
| 788-0 | red cell distribution width | 1.9e-05 | 19 |