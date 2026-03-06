# Contribution2 Disease Selection Report (childrencode)

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
- **QC3**: Filter pool by AUC thresholds. No dedup (each ICD children code independent).

## Selected Diseases

Total selected (QC1=Yes only): 28

| Ontology | ICD | N Models | Max | Mean | Median | Min | Top-1 | Top-2 | Top-3 | Top-4 | Top-5 | Top-6 | Top-7 | Top-8 | Top-9 | Top-10 | Case N | QC1 (≥0.025) |
|----------|-----|----------|-----|------|--------|-----|-------|-------|-------|-------|-------|-------|-------|-------|--------|--------|-----|---------------------|
| hashimoto's thyroiditis | E063 | 3 | 0.7941 | 0.7431 | 0.794 | 0.6412 | 0.7941 | 0.794 | 0.6412 | - | - | - | - | - | - | - | 4403 | Yes |
| graves disease | E0500 | 7 | 0.7677 | 0.67 | 0.632 | 0.6154 | 0.7677 | 0.7535 | 0.6667 | 0.632 | 0.629 | 0.6259 | 0.6154 | - | - | - | 1249 | Yes |
| ankylosing spondylitis | M459 | 9 | 0.7415 | 0.6443 | 0.6491 | 0.533 | 0.7415 | 0.7397 | 0.7362 | 0.7188 | 0.6491 | 0.5846 | 0.5629 | 0.533 | 0.533 | - | 595 | Yes |
| age-related macular degeneration | H353131 | 6 | 0.6547 | 0.6168 | 0.6323 | 0.5195 | 0.6547 | 0.653 | 0.6512 | 0.6133 | 0.6093 | 0.5195 | - | - | - | - | 1185 | Yes |
| vitiligo | L80 | 3 | 0.6417 | 0.6121 | 0.6276 | 0.5669 | 0.6417 | 0.6276 | 0.5669 | - | - | - | - | - | - | - | 612 | Yes |
| thyroid carcinoma | C73 | 32 | 0.8113 | 0.6069 | 0.5889 | 0.5276 | 0.8113 | 0.8069 | 0.8016 | 0.7865 | 0.6376 | 0.6331 | 0.6299 | 0.6099 | 0.5999 | 0.597 | 1810 | Yes |
| open-angle glaucoma | H401131 | 5 | 0.6405 | 0.6052 | 0.6173 | 0.5668 | 0.6405 | 0.6264 | 0.6173 | 0.5749 | 0.5668 | - | - | - | - | - | 1065 | Yes |
| hypothyroidism | E039 | 28 | 0.6575 | 0.6026 | 0.6073 | 0.5538 | 0.6575 | 0.6567 | 0.6289 | 0.624 | 0.6231 | 0.6218 | 0.6216 | 0.6166 | 0.6146 | 0.6129 | 29932 | Yes |
| cutaneous melanoma | C439 | 5 | 0.6239 | 0.5907 | 0.5886 | 0.5663 | 0.6239 | 0.5934 | 0.5886 | 0.5812 | 0.5663 | - | - | - | - | - | 1591 | Yes |
| abdominal aortic aneurysm | I714 | 6 | 0.6374 | 0.588 | 0.5965 | 0.525 | 0.6374 | 0.6341 | 0.6312 | 0.5618 | 0.5388 | 0.525 | - | - | - | - | 1630 | Yes |
| hypertrophic cardiomyopathy | I422 | 4 | 0.6036 | 0.5829 | 0.5882 | 0.5514 | 0.6036 | 0.5891 | 0.5873 | 0.5514 | - | - | - | - | - | - | 712 | Yes |
| nodular goiter | E042 | 7 | 0.7033 | 0.5738 | 0.5575 | 0.4457 | 0.7033 | 0.6911 | 0.6158 | 0.5575 | 0.5493 | 0.454 | 0.4457 | - | - | - | 6466 | Yes |
| obesity | E669 | 10 | 0.6311 | 0.5736 | 0.5639 | 0.5424 | 0.6311 | 0.6165 | 0.5798 | 0.5753 | 0.5667 | 0.5611 | 0.5606 | 0.5549 | 0.5479 | 0.5424 | 39152 | Yes |
| alcohol dependence | F1020 | 4 | 0.6051 | 0.5695 | 0.5752 | 0.5224 | 0.6051 | 0.5762 | 0.5742 | 0.5224 | - | - | - | - | - | - | 3795 | Yes |
| pulmonary embolism | I2699 | 7 | 0.5943 | 0.5666 | 0.5885 | 0.5129 | 0.5943 | 0.5916 | 0.5907 | 0.5885 | 0.5578 | 0.5306 | 0.5129 | - | - | - | 4552 | Yes |
| skin carcinoma in situ | D0439 | 3 | 0.601 | 0.5527 | 0.5529 | 0.5041 | 0.601 | 0.5529 | 0.5041 | - | - | - | - | - | - | - | 641 | Yes |
| renal carcinoma | C649 | 8 | 0.5824 | 0.5454 | 0.5449 | 0.5197 | 0.5824 | 0.5491 | 0.5488 | 0.5456 | 0.5441 | 0.541 | 0.5325 | 0.5197 | - | - | 995 | Yes |
| kidney cancer | C649 | 10 | 0.5824 | 0.5394 | 0.5426 | 0.5153 | 0.5824 | 0.5491 | 0.5488 | 0.5456 | 0.5441 | 0.541 | 0.5325 | 0.5197 | 0.5153 | 0.5153 | 995 | Yes |
| prostate carcinoma | C61 | 93 | 0.655 | 0.5392 | 0.5407 | 0.4573 | 0.655 | 0.6295 | 0.5748 | 0.5665 | 0.5641 | 0.564 | 0.5619 | 0.5608 | 0.5603 | 0.5589 | 5390 | Yes |
| prostate cancer | C61 | 96 | 0.655 | 0.5387 | 0.5407 | 0.4573 | 0.655 | 0.6295 | 0.6041 | 0.5748 | 0.5665 | 0.5641 | 0.564 | 0.5619 | 0.5608 | 0.5603 | 5390 | Yes |
| peripheral vascular disease | I739 | 4 | 0.5862 | 0.5339 | 0.5186 | 0.5123 | 0.5862 | 0.5195 | 0.5176 | 0.5123 | - | - | - | - | - | - | 8004 | Yes |
| aortic stenosis | I350 | 8 | 0.6375 | 0.5298 | 0.5173 | 0.3445 | 0.6375 | 0.6233 | 0.6228 | 0.5181 | 0.5166 | 0.5021 | 0.474 | 0.3445 | - | - | 3985 | Yes |
| hodgkins lymphoma | C8190 | 27 | 0.618 | 0.5275 | 0.52 | 0.4838 | 0.618 | 0.612 | 0.6014 | 0.5597 | 0.5586 | 0.554 | 0.5464 | 0.542 | 0.542 | 0.5379 | 305 | Yes |
| obstructive sleep apnea | G4733 | 20 | 0.5784 | 0.5132 | 0.5041 | 0.4984 | 0.5784 | 0.5454 | 0.5418 | 0.5217 | 0.5167 | 0.5137 | 0.5117 | 0.5115 | 0.5069 | 0.5053 | 34474 | Yes |
| sleep apnea | G4733 | 20 | 0.5784 | 0.5132 | 0.5041 | 0.4984 | 0.5784 | 0.5454 | 0.5418 | 0.5217 | 0.5167 | 0.5137 | 0.5117 | 0.5115 | 0.5069 | 0.5053 | 34474 | Yes |
| uterine carcinoma | C541 | 14 | 0.612 | 0.5132 | 0.5236 | 0.4138 | 0.612 | 0.6113 | 0.597 | 0.5609 | 0.5519 | 0.5326 | 0.5263 | 0.5209 | 0.5044 | 0.4564 | 937 | Yes |
| late-onset alzheimer's disease | G301 | 5 | 0.569 | 0.5099 | 0.5144 | 0.4346 | 0.569 | 0.5203 | 0.5144 | 0.5114 | 0.4346 | - | - | - | - | - | 218 | Yes |
| cervical carcinoma | C539 | 6 | 0.6925 | 0.5053 | 0.4734 | 0.3401 | 0.6925 | 0.6679 | 0.4759 | 0.4709 | 0.3846 | 0.3401 | - | - | - | - | 361 | Yes |

## Summary Statistics

| Metric | Count |
|--------|-------|
| Ontologies passing QC1 (T1..T5 vs Rest >= 0.025) | 37 |
| Ontologies passing QC2 (genetic significance) | 55 |
| Ontologies passing QC3 (Mean AUC >= 0.5 & Top-1 >= 0.55) | 95 |
| Final selected (QC1=Yes) | 28 |
| Total pool before QC1 filter | 61 |