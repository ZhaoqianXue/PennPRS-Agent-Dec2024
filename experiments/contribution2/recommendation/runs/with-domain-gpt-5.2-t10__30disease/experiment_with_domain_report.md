# Contribution2 Experiment 2: With Domain Knowledge

## Summary

- **Diseases**: 30
- **Trials per disease**: 10
- **Total trials**: 300
- **Model**: gpt-5.2
- **Estimated API cost**: $1.3193 (uncached input 668,300 tokens = $0.5848; cached input 804,096 tokens = $0.0704; output 94,881 tokens = $0.6642)

## High-Level Outcome

- With Domain Knowledge `Hit@1`: `19/30 = 63.33%`; `trial_hits = 179/300 = 59.67%`
- With Domain Knowledge `Hit@2`: `24/30 = 80.00%`; `trial_hits = 229/300 = 76.33%`
- With Domain Knowledge `Hit@3`: `26/30 = 86.67%`; `trial_hits = 256/300 = 85.33%`
- With Domain Knowledge `Hit@4`: `26/30 = 86.67%`; `trial_hits = 256/300 = 85.33%`
- With Domain Knowledge `Hit@5`: `27/30 = 90.00%`; `trial_hits = 268/300 = 89.33%`
- Without Domain Knowledge `Hit@1`: `14/30 = 46.67%`; `trial_hits = 134/300 = 44.67%`
- Without Domain Knowledge `Hit@2`: `17/30 = 56.67%`; `trial_hits = 164/300 = 54.67%`
- Without Domain Knowledge `Hit@3`: `22/30 = 73.33%`; `trial_hits = 222/300 = 74.00%`
- Without Domain Knowledge `Hit@4`: `24/30 = 80.00%`; `trial_hits = 240/300 = 80.00%`
- Without Domain Knowledge `Hit@5`: `24/30 = 80.00%`; `trial_hits = 240/300 = 80.00%`

## Percentile Hit

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.
- For each percentile threshold, define the tie-aware cutoff rank as `c_q = max(1, ceil(q/100 * M))`.
- A selection counts as `Top q% Hit` if its AoU benchmark rank satisfies `r <= c_q`.
- Denominator: fixed total disease count for modal selections and fixed total trial count for trial selections.
- Tie handling: if the AoU benchmark AUC is tied at cutoff rank `c_q`, all tied models count as `Top q%`.

- With Domain Knowledge `Top 5% Hit`: `19/30 = 63.33%`; `trial_hits = 179/300 = 59.67%`
- With Domain Knowledge `Top 10% Hit`: `19/30 = 63.33%`; `trial_hits = 180/300 = 60.00%`
- With Domain Knowledge `Top 15% Hit`: `23/30 = 76.67%`; `trial_hits = 226/300 = 75.33%`
- With Domain Knowledge `Top 20% Hit`: `23/30 = 76.67%`; `trial_hits = 227/300 = 75.67%`
- With Domain Knowledge `Top 25% Hit`: `23/30 = 76.67%`; `trial_hits = 228/300 = 76.00%`
- Without Domain Knowledge `Top 5% Hit`: `14/30 = 46.67%`; `trial_hits = 134/300 = 44.67%`
- Without Domain Knowledge `Top 10% Hit`: `15/30 = 50.00%`; `trial_hits = 144/300 = 48.00%`
- Without Domain Knowledge `Top 15% Hit`: `18/30 = 60.00%`; `trial_hits = 171/300 = 57.00%`
- Without Domain Knowledge `Top 20% Hit`: `19/30 = 63.33%`; `trial_hits = 181/300 = 60.33%`
- Without Domain Knowledge `Top 25% Hit`: `20/30 = 66.67%`; `trial_hits = 191/300 = 63.67%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- With Domain Knowledge: `mean r / M = 0.2948` (30 modal selections); `trial mean r / M = 0.3063` (300 trials)
- Without Domain Knowledge: `mean r / M = 0.4264` (30 modal selections); `trial mean r / M = 0.4310` (300 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- With Domain Knowledge: `mean (M - r) / M = 0.7052` (30 modal selections); `trial mean (M - r) / M = 0.6937` (300 trials)
- Without Domain Knowledge: `mean (M - r) / M = 0.5736` (30 modal selections); `trial mean (M - r) / M = 0.5690` (300 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- With Domain Knowledge: `mean NRS = 0.8391` (30 modal selections); `trial mean NRS = 0.8238` (300 trials)
- Without Domain Knowledge: `mean NRS = 0.6790` (30 modal selections); `trial mean NRS = 0.6736` (300 trials)

## Experiment Setup

- **Step 1 tools**: prs_model_pgscatalog_search + prs_model_domain_knowledge
- **Domain Knowledge**: Enabled (local curated knowledge base)
- **Candidate pool**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us
- **Success rule**: report `Hit@k` for `k = 1..5` against the AoU benchmark ranking using the full disease/trial denominator; if a disease has fewer than `k` evaluated models, `Top@k` includes all available benchmark-ranked models
- **Benchmark tie handling**: if the AoU benchmark AUC is tied at the `k`-th cutoff, all tied models count as `Top@k`
- **Without Domain Knowledge reference**: compare against the matching archived `without-domain-gpt-5.2-t10__<dataset>` run under the same disease-list / 10-trial protocol

## Results by Disease

All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.
They are **not** PGS Catalog reported-AUC ranks.

| Ontology | N Models | Trial Hit@1..5 | With Domain Knowledge Hit@1..5 | With Domain Knowledge | Without Domain Knowledge Hit@1..5 | Without Domain Knowledge |
|----------|----------|---------------|----------------------------------|-----------------------|-------------------------------------|--------------------------|
| prostate cancer | 96 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005238 (AUC rank 51/96): x7<br>PGS000719 (AUC rank 11/96): x2<br>PGS004155 (AUC rank 30/96): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005237 (AUC rank 72/96): x10 |
| thyroid carcinoma | 32 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000208 (AUC rank 16/32): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001289 (AUC rank 24/32): x10 |
| hypothyroidism | 28 | 1:70.00%, 2:70.00%, 3:80.00%, 4:80.00%, 5:80.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005268 (AUC rank 1/28): x7<br>PGS004935 (AUC rank 15/28): x2<br>PGS005218 (AUC rank 3/28): x1 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x10 |
| hodgkins lymphoma | 27 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 |
| obstructive sleep apnea | 20 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 |
| sleep apnea | 20 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 |
| testicular neoplasm | 14 | 1:50.00%, 2:50.00%, 3:60.00%, 4:60.00%, 5:60.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000796 (AUC rank 1/14): x5<br>PGS000604 (AUC rank 10/14): x3<br>PGS001164 (AUC rank 3/14): x1<br>PGS000602 (AUC rank 7/14): x1 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001164 (AUC rank 3/14): x10 |
| uterine carcinoma | 14 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003381 (AUC rank 3/14): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001795 (AUC rank 9/14): x10 |
| kidney cancer | 10 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 |
| obesity | 10 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005235 (AUC rank 1/10): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10): x10 |
| ankylosing spondylitis | 9 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001267 (AUC rank 2/9): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001268 (AUC rank 3/9): x10 |
| aortic stenosis | 8 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005254 (AUC rank 1/8): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005252 (AUC rank 8/8): x10 |
| renal carcinoma | 8 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/8): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/8): x10 |
| graves disease | 7 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x10 |
| nodular goiter | 7 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 |
| pulmonary embolism | 7 | 1:0.00%, 2:40.00%, 3:40.00%, 4:40.00%, 5:40.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003861 (AUC rank 7/7): x6<br>PGS001280 (AUC rank 2/7): x4 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001280 (AUC rank 2/7): x7<br>PGS001279 (AUC rank 4/7): x3 |
| abdominal aortic aneurysm | 6 | 1:0.00%, 2:0.00%, 3:80.00%, 4:80.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003972 (AUC rank 3/6): x8<br>PGS000753 (AUC rank 5/6): x2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003973 (AUC rank 1/6): x10 |
| age-related macular degeneration | 6 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 1/6): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 1/6): x6<br>PGS004952 (AUC rank 3/6): x4 |
| cervical carcinoma | 6 | 1:20.00%, 2:20.00%, 3:20.00%, 4:20.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS003428 (AUC rank 5/6): x8<br>PGS000073 (AUC rank 1/6): x2 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 6/6): x10 |
| cutaneous melanoma | 5 | 1:80.00%, 2:80.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003382 (AUC rank 1/5): x8<br>PGS000766 (AUC rank 3/5): x2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003382 (AUC rank 1/5): x10 |
| late-onset alzheimer's disease | 5 | 1:80.00%, 2:80.00%, 3:80.00%, 4:80.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000054 (AUC rank 1/5): x8<br>PGS000053 (AUC rank 5/5): x2 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004918 (AUC rank 4/5): x6<br>PGS000334 (AUC rank 3/5): x4 |
| open-angle glaucoma | 5 | 1:90.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004944 (AUC rank 1/5): x9<br>PGS001797 (AUC rank 2/5): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004944 (AUC rank 1/5): x10 |
| alcohol dependence | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x10 |
| hypertrophic cardiomyopathy | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x8<br>PGS000739 (AUC rank 2/4): x2 |
| juvenile idiopathic arthritis | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 |
| peripheral vascular disease | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005217 (AUC rank 1/4): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001843 (AUC rank 4/4): x9<br>PGS002055 (AUC rank 2/4): x1 |
| hashimoto's thyroiditis | 3 | 1:0.00%, 2:80.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005271 (AUC rank 2/3): x8<br>PGS005270 (AUC rank 3/3): x2 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005270 (AUC rank 3/3): x10 |
| preeclampsia | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 |
| skin carcinoma in situ | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x10 |
| vitiligo | 3 | 1:0.00%, 2:70.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000738 (AUC rank 2/3): x7<br>PGS001536 (AUC rank 3/3): x3 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001536 (AUC rank 3/3): x10 |
