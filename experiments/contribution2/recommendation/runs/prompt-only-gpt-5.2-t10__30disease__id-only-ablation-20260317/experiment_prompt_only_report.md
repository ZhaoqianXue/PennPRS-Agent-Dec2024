# Contribution2 Experiment 1: Prompt-Only Baseline

## Summary

- **Diseases**: 30
- **Trials per disease**: 10
- **Total trials**: 300
- **Model**: gpt-5.2
- **Valid output rate**: 300/300 = 100.00%
- **Estimated API cost**: $0.3949 (uncached input 61,476 tokens = $0.0538; cached input 0 tokens = $0.0000; output 48,729 tokens = $0.3411)

## High-Level Outcome

- Prompt-Only Baseline `Hit@1`: `3/30 = 10.00%`; `trial_hits = 32/300 = 10.67%`
- Prompt-Only Baseline `Hit@2`: `7/30 = 23.33%`; `trial_hits = 71/300 = 23.67%`
- Prompt-Only Baseline `Hit@3`: `10/30 = 33.33%`; `trial_hits = 101/300 = 33.67%`
- Prompt-Only Baseline `Hit@4`: `12/30 = 40.00%`; `trial_hits = 121/300 = 40.33%`
- Prompt-Only Baseline `Hit@5`: `20/30 = 66.67%`; `trial_hits = 199/300 = 66.33%`

## Percentile Hit

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.
- For each percentile threshold, define the tie-aware cutoff rank as `c_q = max(1, ceil(q/100 * M))`.
- A selection counts as `Top q% Hit` if its AoU benchmark rank satisfies `r <= c_q`.
- Denominator: fixed total disease count for modal selections and fixed total trial count for trial selections.
- Tie handling: if the AoU benchmark AUC is tied at cutoff rank `c_q`, all tied models count as `Top q%`.

- Prompt-Only Baseline `Top 5% Hit`: `3/30 = 10.00%`; `trial_hits = 32/300 = 10.67%`
- Prompt-Only Baseline `Top 10% Hit`: `3/30 = 10.00%`; `trial_hits = 32/300 = 10.67%`
- Prompt-Only Baseline `Top 15% Hit`: `4/30 = 13.33%`; `trial_hits = 41/300 = 13.67%`
- Prompt-Only Baseline `Top 20% Hit`: `4/30 = 13.33%`; `trial_hits = 41/300 = 13.67%`
- Prompt-Only Baseline `Top 25% Hit`: `4/30 = 13.33%`; `trial_hits = 41/300 = 13.67%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Prompt-Only Baseline: `mean r / M = 0.6901` (30 modal selections); `trial mean r / M = 0.6886` (300 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Prompt-Only Baseline: `mean (M - r) / M = 0.3099` (30 modal selections); `trial mean (M - r) / M = 0.3114` (300 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Prompt-Only Baseline: `mean NRS = 0.3715` (30 modal selections); `trial mean NRS = 0.3735` (300 trials)


## Experiment Setup

- **Step 1 tools**: none (candidate PGS IDs visible, all metadata stripped)
- **Domain Knowledge**: Disabled
- **Candidate pool visibility to LLM**: ID-only (no trait, method, performance, or other metadata)
- **Candidate pool for evaluation**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us
- **Success rule**: report `Hit@k` for `k = 1..5` against the AoU benchmark ranking using the full disease/trial denominator; if a disease has fewer than `k` evaluated models, `Top@k` includes all available benchmark-ranked models
- **Benchmark tie handling**: if the AoU benchmark AUC is tied at the `k`-th cutoff, all tied models count as `Top@k`

## Results by Disease

All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.
They are **not** PGS Catalog reported-AUC ranks.

| Ontology | N Models | Trial Hit@1..5 | Prompt-Only Baseline Hit@1..5 | Prompt-Only Baseline |
|----------|----------|---------------|------------------------------|------------------------|
| prostate cancer | 96 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000030 (AUC rank 29/96): x8<br>PGS005241 (AUC rank 88/96): x2 |
| thyroid carcinoma | 32 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000087 (AUC rank 19/32): x10 |
| hypothyroidism | 28 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000759 (AUC rank 19/28): x9<br>PGS005272 (AUC rank 20/28): x1 |
| hodgkins lymphoma | 27 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000080 (AUC rank 17/27): x10 |
| obstructive sleep apnea | 20 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003204 (AUC rank 17/20): x10 |
| sleep apnea | 20 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003204 (AUC rank 17/20): x10 |
| testicular neoplasm | 14 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000595 (AUC rank 13/14): x10 |
| uterine carcinoma | 14 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000073 (AUC rank 14/14): x7<br>PGS003428 (AUC rank 7/14): x3 |
| kidney cancer | 10 | 1:20.00%, 2:20.00%, 3:20.00%, 4:20.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000076 (AUC rank 5/10): x8<br>PGS004908 (AUC rank 1/10): x2 |
| obesity | 10 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10): x10 |
| ankylosing spondylitis | 9 | 1:0.00%, 2:90.00%, 3:90.00%, 4:90.00%, 5:90.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001267 (AUC rank 2/9): x9<br>PGS003420 (AUC rank 7/9): x1 |
| aortic stenosis | 8 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000739 (AUC rank 7/8): x10 |
| renal carcinoma | 8 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000076 (AUC rank 5/8): x10 |
| graves disease | 7 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001042 (AUC rank 5/7): x10 |
| nodular goiter | 7 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001814 (AUC rank 5/7): x10 |
| pulmonary embolism | 7 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001277 (AUC rank 3/7): x10 |
| abdominal aortic aneurysm | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000753 (AUC rank 5/6): x10 |
| age-related macular degeneration | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001834 (AUC rank 4/6): x10 |
| cervical carcinoma | 6 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000073 (AUC rank 1/6): x10 |
| cutaneous melanoma | 5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000339 (AUC rank 5/5): x10 |
| late-onset alzheimer's disease | 5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000053 (AUC rank 5/5): x10 |
| open-angle glaucoma | 5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000350 (AUC rank 5/5): x10 |
| alcohol dependence | 4 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000201 (AUC rank 2/4): x10 |
| hypertrophic cardiomyopathy | 4 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000739 (AUC rank 2/4): x10 |
| juvenile idiopathic arthritis | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 |
| peripheral vascular disease | 4 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001843 (AUC rank 4/4): x10 |
| hashimoto's thyroiditis | 3 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005270 (AUC rank 3/3): x10 |
| preeclampsia | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 |
| skin carcinoma in situ | 3 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000469 (AUC rank 3/3): x10 |
| vitiligo | 3 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000738 (AUC rank 2/3): x10 |