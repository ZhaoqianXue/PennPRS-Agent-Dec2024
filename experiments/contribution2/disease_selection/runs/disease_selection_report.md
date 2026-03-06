# Contribution2 Disease Selection Report (rootcode)

## Selection Criteria

### QC1: Top PRS Model Distinguishability
- **Tk vs Rest**: Top-k AUC - Top-(k+1) AUC (cliff between rank k and k+1).
- **Threshold**: Pass if any of (T1, T2, T3, T4, T5 vs Rest) >= 0.025.

### QC2: Genetic Significance (keyword screening)
- **Whitelist**: Ontology name matches GENETICALLY_SIGNIFICANT_KEYWORDS.
- **Blacklist**: Exclude if matches NICHE_EXCLUSION_KEYWORDS.

### QC3: AUC Thresholds (filtering step)
- **Mean AUC** >= 0.5, **Top-1 AUC** >= 0.55.

### Staged Logic (no intersection, no count limit)
- **QC2**: Genetic significance pool (whitelist add, blacklist subtract).
- **QC1 + QC2**: Pool = QC2 OR QC1 (additive: genetic significance OR distinguishability).
- **QC3**: Filter pool by AUC thresholds. Dedup by ICD root.

## Selected Diseases

Total selected (QC1=Yes only): 21

| Ontology | ICD | N Models | Max | Mean | Median | Min | Top-1 | Top-2 | Top-3 | Top-4 | Top-5 | Top-6 | Top-7 | Top-8 | Top-9 | Top-10 | Case N | QC1 (≥0.025) |
|----------|-----|----------|-----|------|--------|-----|-------|-------|-------|-------|-------|-------|-------|-------|--------|--------|-----|---------------------|
| testicular neoplasm | C62 | 14 | 0.9212 | 0.771 | 0.7888 | 0.414 | 0.9212 | 0.9128 | 0.9044 | 0.9021 | 0.873 | 0.8314 | 0.7888 | 0.7888 | 0.7482 | 0.7468 | 204 | Yes |
| hashimoto's thyroiditis | E06 | 3 | 0.7643 | 0.7198 | 0.7629 | 0.6321 | 0.7643 | 0.7629 | 0.6321 | - | - | - | - | - | - | - | 4905 | Yes |
| preeclampsia | O14 | 3 | 0.8077 | 0.713 | 0.7604 | 0.5709 | 0.8077 | 0.7604 | 0.5709 | - | - | - | - | - | - | - | 590 | Yes |
| ankylosing spondylitis | M45 | 9 | 0.7154 | 0.6327 | 0.6396 | 0.5342 | 0.7154 | 0.7144 | 0.7121 | 0.703 | 0.6396 | 0.5819 | 0.5596 | 0.5342 | 0.5342 | - | 744 | Yes |
| vitiligo | L80 | 3 | 0.6417 | 0.6121 | 0.6276 | 0.5669 | 0.6417 | 0.6276 | 0.5669 | - | - | - | - | - | - | - | 612 | Yes |
| thyroid carcinoma | C73 | 32 | 0.8113 | 0.6069 | 0.5889 | 0.5276 | 0.8113 | 0.8069 | 0.8016 | 0.7865 | 0.6376 | 0.6331 | 0.6299 | 0.6099 | 0.5999 | 0.597 | 1810 | Yes |
| hypothyroidism | E03 | 28 | 0.6557 | 0.6017 | 0.6059 | 0.5535 | 0.6557 | 0.6548 | 0.6274 | 0.6232 | 0.6221 | 0.6205 | 0.6202 | 0.6162 | 0.6131 | 0.6118 | 31455 | Yes |
| cutaneous melanoma | C43 | 5 | 0.6138 | 0.5979 | 0.6011 | 0.5685 | 0.6138 | 0.6076 | 0.6011 | 0.5981 | 0.5685 | - | - | - | - | - | 2589 | Yes |
| graves disease | E05 | 7 | 0.6211 | 0.5853 | 0.5743 | 0.5628 | 0.6211 | 0.6176 | 0.5914 | 0.5743 | 0.5665 | 0.5634 | 0.5628 | - | - | - | 3830 | Yes |
| obesity | E66 | 10 | 0.6479 | 0.5831 | 0.5732 | 0.5469 | 0.6479 | 0.6331 | 0.5909 | 0.5833 | 0.5771 | 0.5694 | 0.5666 | 0.5605 | 0.5553 | 0.5469 | 48647 | Yes |
| abdominal aortic aneurysm | I71 | 6 | 0.5904 | 0.5655 | 0.5684 | 0.5287 | 0.5904 | 0.5888 | 0.5837 | 0.5532 | 0.5479 | 0.5287 | - | - | - | - | 4276 | Yes |
| pulmonary embolism | I26 | 7 | 0.5909 | 0.5646 | 0.5865 | 0.5122 | 0.5909 | 0.5891 | 0.5885 | 0.5865 | 0.5558 | 0.5292 | 0.5122 | - | - | - | 4804 | Yes |
| alcohol dependence | F10 | 4 | 0.5876 | 0.5585 | 0.5586 | 0.5291 | 0.5876 | 0.5595 | 0.5577 | 0.5291 | - | - | - | - | - | - | 10402 | Yes |
| nodular goiter | E04 | 7 | 0.6694 | 0.5558 | 0.5395 | 0.4464 | 0.6694 | 0.6587 | 0.584 | 0.5395 | 0.5355 | 0.4573 | 0.4464 | - | - | - | 12899 | Yes |
| skin carcinoma in situ | D04 | 3 | 0.5802 | 0.5544 | 0.5665 | 0.5165 | 0.5802 | 0.5665 | 0.5165 | - | - | - | - | - | - | - | 3035 | Yes |
| renal carcinoma | C64 | 8 | 0.5841 | 0.5478 | 0.5461 | 0.5209 | 0.5841 | 0.5524 | 0.5513 | 0.5466 | 0.5456 | 0.5419 | 0.5399 | 0.5209 | - | - | 1376 | Yes |
| juvenile idiopathic arthritis | M08 | 4 | 0.5768 | 0.5458 | 0.5416 | 0.523 | 0.5768 | 0.5517 | 0.5315 | 0.523 | - | - | - | - | - | - | 221 | Yes |
| prostate carcinoma | C61 | 93 | 0.655 | 0.5392 | 0.5407 | 0.4573 | 0.655 | 0.6295 | 0.5748 | 0.5665 | 0.5641 | 0.564 | 0.5619 | 0.5608 | 0.5603 | 0.5589 | 5390 | Yes |
| hodgkins lymphoma | C81 | 27 | 0.6093 | 0.5203 | 0.5168 | 0.4685 | 0.6093 | 0.6048 | 0.5914 | 0.5671 | 0.5621 | 0.5348 | 0.5276 | 0.5269 | 0.5254 | 0.5209 | 415 | Yes |
| aortic stenosis | I35 | 8 | 0.5684 | 0.5131 | 0.5105 | 0.4106 | 0.5684 | 0.5559 | 0.5537 | 0.5107 | 0.5103 | 0.4981 | 0.4971 | 0.4106 | - | - | 9315 | Yes |
| cervical carcinoma | C53 | 6 | 0.6951 | 0.5059 | 0.4763 | 0.3377 | 0.6951 | 0.6706 | 0.4765 | 0.4762 | 0.3795 | 0.3377 | - | - | - | - | 392 | Yes |

## Summary Statistics

| Metric | Count |
|--------|-------|
| Ontologies passing QC1 (T1..T5 vs Rest >= 0.025) | 33 |
| Ontologies passing QC2 (genetic significance) | 57 |
| Ontologies passing QC3 (Mean AUC >= 0.5 & Top-1 >= 0.55) | 85 |
| Final selected (QC1=Yes) | 21 |
| Total pool before QC1 filter | 45 |