# Contribution3: Continuous-to-Continuous Cross List Report (loinccode)

## Terminology

- **Input continuous trait**: Measurement trait needing transfer support
  - **Type A (matrix)**: In C1's LOINC incremental-R2 matrix (has ground truth for verification)
  - Continuous inputs here are restricted to `include_in_analysis == 1` in `prs_incrementalr2_metadata`
- **Output continuous trait**: Measurement trait whose PRS models are recommended for the input continuous trait
- PGS models with unknown source ontology are **excluded**

## Cross-list workflow

1. **Define Type A input traits** — use **Cross-Disease PRS Beats Self** only.
2. **Determine output traits** — for each continuous input, link retained cross PGS → LOINC trait metadata.
3. **Cross-Trait Transfer** — evaluate whether continuous-trait PRS models can usefully transfer to the input continuous trait.

## Selection Criterion (Type A)

- At least one non-self continuous-trait PGS model has cross incremental R2 > best self incremental R2
- When self incremental R2 exists: require **cross incremental R2 − self best incremental R2 > 0.0025** per retained model
- Require **Top Cross incremental R2 > 0.02** for the input trait to enter the cross-list
- Exclude input traits with **self best incremental R2 > 0.05** (strong self PRS)

## Type A Summary

| Metric | Count |
|--------|-------|
| **Type A cross-list input traits** (Cross beats self) | **2** |
| Total Type A rows in matrix filter (incl. Self optimal) | 32 |
| With self incremental R2 | 32 |
| Without self incremental R2 | 0 |
| Self optimal (reference only; not cross-list inputs) | 30 |
| Any cross candidates | 2 |

## Type A: Continuous PRS Beats Self

*Included in **Type A cross-list input traits**.*

Total: 2 traits

| Input LOINC | Input Trait | Self Best Incremental R2 | Top Cross Incremental R2 | Improvement | Output LOINC | Top Output Trait | N Cross | N Output Traits |
|-------------|-------------|--------------------------|--------------------------|-------------|--------------|------------------|---------|-----------------|
| 1884-6 | apolipoprotein b measurement | 0.038225 | 0.059508 | +0.0213 | 18262-6 | low density lipoprotein cholesterol meas | 32 | 4 |
| 1869-7 | apolipoprotein a 1 measurement | 0.01264 | 0.024816 | +0.0122 | 10835-7 | lipoprotein a measurement | 12 | 4 |

## Type A: Self Models Already Optimal

*Not included in **Type A cross-list input traits** (self PRS sufficient under current rules; reference only).*

Total: 30 traits

| Input LOINC | Input Trait | Self Best Incremental R2 | Self N Models |
|-------------|-------------|--------------------------|---------------|
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