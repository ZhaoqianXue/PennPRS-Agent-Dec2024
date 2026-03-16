# Contribution2 Experiment 3: Catalog Search + Domain Knowledge vs Catalog Search Only

## Summary

- **Model**: gpt-5.2
- **Disease count**: 30

## High-Level Outcome

- Catalog Search + Domain Knowledge `Hit@1`: `17/30 = 56.67%`; `trial_hits = 172/300 = 57.33%`
- Catalog Search + Domain Knowledge `Hit@2`: `22/30 = 73.33%`; `trial_hits = 216/300 = 72.00%`
- Catalog Search + Domain Knowledge `Hit@3`: `25/30 = 83.33%`; `trial_hits = 245/300 = 81.67%`
- Catalog Search + Domain Knowledge `Hit@4`: `26/30 = 86.67%`; `trial_hits = 261/300 = 87.00%`
- Catalog Search + Domain Knowledge `Hit@5`: `27/30 = 90.00%`; `trial_hits = 273/300 = 91.00%`
- Catalog Search Only `Hit@1`: `14/30 = 46.67%`; `trial_hits = 140/300 = 46.67%`
- Catalog Search Only `Hit@2`: `18/30 = 60.00%`; `trial_hits = 181/300 = 60.33%`
- Catalog Search Only `Hit@3`: `24/30 = 80.00%`; `trial_hits = 237/300 = 79.00%`
- Catalog Search Only `Hit@4`: `24/30 = 80.00%`; `trial_hits = 239/300 = 79.67%`
- Catalog Search Only `Hit@5`: `24/30 = 80.00%`; `trial_hits = 240/300 = 80.00%`

## Percentile Hit

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.
- For each percentile threshold, define the tie-aware cutoff rank as `c_q = max(1, ceil(q/100 * M))`.
- A selection counts as `Top q% Hit` if its AoU benchmark rank satisfies `r <= c_q`.
- Denominator: fixed total disease count for modal selections and fixed total trial count for trial selections.
- Tie handling: if the AoU benchmark AUC is tied at cutoff rank `c_q`, all tied models count as `Top q%`.

- Catalog Search + Domain Knowledge `Top 5% Hit`: `17/30 = 56.67%`; `trial_hits = 172/300 = 57.33%`
- Catalog Search + Domain Knowledge `Top 10% Hit`: `19/30 = 63.33%`; `trial_hits = 188/300 = 62.67%`
- Catalog Search + Domain Knowledge `Top 15% Hit`: `23/30 = 76.67%`; `trial_hits = 224/300 = 74.67%`
- Catalog Search + Domain Knowledge `Top 20% Hit`: `23/30 = 76.67%`; `trial_hits = 224/300 = 74.67%`
- Catalog Search + Domain Knowledge `Top 25% Hit`: `23/30 = 76.67%`; `trial_hits = 224/300 = 74.67%`
- Catalog Search Only `Top 5% Hit`: `14/30 = 46.67%`; `trial_hits = 140/300 = 46.67%`
- Catalog Search Only `Top 10% Hit`: `15/30 = 50.00%`; `trial_hits = 153/300 = 51.00%`
- Catalog Search Only `Top 15% Hit`: `18/30 = 60.00%`; `trial_hits = 183/300 = 61.00%`
- Catalog Search Only `Top 20% Hit`: `19/30 = 63.33%`; `trial_hits = 189/300 = 63.00%`
- Catalog Search Only `Top 25% Hit`: `20/30 = 66.67%`; `trial_hits = 199/300 = 66.33%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean r / M = 0.3004` (30 modal selections); `trial mean r / M = 0.3116` (300 trials)
- Catalog Search Only: `mean r / M = 0.3873` (30 modal selections); `trial mean r / M = 0.3883` (300 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean (M - r) / M = 0.6996` (30 modal selections); `trial mean (M - r) / M = 0.6884` (300 trials)
- Catalog Search Only: `mean (M - r) / M = 0.6127` (30 modal selections); `trial mean (M - r) / M = 0.6117` (300 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Catalog Search + Domain Knowledge: `mean NRS = 0.8319` (30 modal selections); `trial mean NRS = 0.8179` (300 trials)
- Catalog Search Only: `mean NRS = 0.7256` (30 modal selections); `trial mean NRS = 0.7253` (300 trials)


## Results by Disease

| Ontology | N Models | Catalog Search Only Hit@1..5 | Catalog Search Only | Catalog Search + Domain Knowledge Hit@1..5 | Catalog Search + Domain Knowledge |
|----------|----------|-------------------------------------|--------------------------|----------------------------------|-----------------------|
| prostate cancer | 96 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005238 (AUC rank 51/96): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004155 (AUC rank 30/96): x5<br>PGS005238 (AUC rank 51/96): x4<br>PGS003415 (AUC rank 79/96): x1 |
| thyroid carcinoma | 32 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000208 (AUC rank 16/32): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS005259 (AUC rank 4/32): x10 |
| hypothyroidism | 28 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x6<br>PGS005268 (AUC rank 1/28): x4 |
| hodgkins lymphoma | 27 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 |
| obstructive sleep apnea | 20 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x7<br>PGS005219 (AUC rank 2/20): x3 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 |
| sleep apnea | 20 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 |
| testicular neoplasm | 14 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001164 (AUC rank 3/14): x6<br>PGS000604 (AUC rank 10/14): x3<br>PGS000796 (AUC rank 1/14): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000604 (AUC rank 10/14): x10 |
| uterine carcinoma | 14 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001795 (AUC rank 9/14): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003381 (AUC rank 3/14): x9<br>PGS000075 (AUC rank 1/14): x1 |
| kidney cancer | 10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 |
| obesity | 10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005235 (AUC rank 1/10): x10 |
| ankylosing spondylitis | 9 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001268 (AUC rank 3/9): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001267 (AUC rank 2/9): x7<br>PGS002089 (AUC rank 4/9): x3 |
| aortic stenosis | 8 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005252 (AUC rank 8/8): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005254 (AUC rank 1/8): x10 |
| renal carcinoma | 8 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/8): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/8): x10 |
| graves disease | 7 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x10 |
| nodular goiter | 7 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 |
| pulmonary embolism | 7 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001280 (AUC rank 2/7): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003861 (AUC rank 7/7): x7<br>PGS001279 (AUC rank 4/7): x3 |
| abdominal aortic aneurysm | 6 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003973 (AUC rank 1/6): x8<br>PGS001784 (AUC rank 4/6): x2 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003972 (AUC rank 3/6): x10 |
| age-related macular degeneration | 6 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 1/6): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 1/6): x10 |
| cervical carcinoma | 6 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 6/6): x7<br>PGS000073 (AUC rank 1/6): x2<br>PGS003428 (AUC rank 5/6): x1 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS003428 (AUC rank 5/6): x10 |
| cutaneous melanoma | 5 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003382 (AUC rank 1/5): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003382 (AUC rank 1/5): x9<br>PGS000766 (AUC rank 3/5): x1 |
| late-onset alzheimer's disease | 5 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000334 (AUC rank 3/5): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000054 (AUC rank 1/5): x8<br>PGS000053 (AUC rank 5/5): x2 |
| open-angle glaucoma | 5 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004944 (AUC rank 1/5): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004944 (AUC rank 1/5): x10 |
| alcohol dependence | 4 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x10 |
| hypertrophic cardiomyopathy | 4 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x10 |
| juvenile idiopathic arthritis | 4 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 |
| peripheral vascular disease | 4 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002055 (AUC rank 2/4): x8<br>PGS005217 (AUC rank 1/4): x2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005217 (AUC rank 1/4): x10 |
| hashimoto's thyroiditis | 3 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005270 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005271 (AUC rank 2/3): x7<br>PGS005270 (AUC rank 3/3): x3 |
| preeclampsia | 3 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 |
| skin carcinoma in situ | 3 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x10 |
| vitiligo | 3 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001536 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000738 (AUC rank 2/3): x10 |