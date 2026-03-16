# Contribution2 Experiment 1: Prompt-Only Baseline

## Summary

- **Diseases**: 30
- **Trials per disease**: 10
- **Total trials**: 300
- **Model**: gpt-5.2
- **Valid output rate**: 0/300 = 0.00%
- **Estimated API cost**: $0.2191 (uncached input 56,152 tokens = $0.0491; cached input 0 tokens = $0.0000; output 24,281 tokens = $0.1700)

## High-Level Outcome

- Prompt-Only Baseline `Hit@1`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Hit@2`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Hit@3`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Hit@4`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Hit@5`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`

## Percentile Hit

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.
- For each percentile threshold, define the tie-aware cutoff rank as `c_q = max(1, ceil(q/100 * M))`.
- A selection counts as `Top q% Hit` if its AoU benchmark rank satisfies `r <= c_q`.
- Denominator: fixed total disease count for modal selections and fixed total trial count for trial selections.
- Tie handling: if the AoU benchmark AUC is tied at cutoff rank `c_q`, all tied models count as `Top q%`.

- Prompt-Only Baseline `Top 5% Hit`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Top 10% Hit`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Top 15% Hit`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Top 20% Hit`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`
- Prompt-Only Baseline `Top 25% Hit`: `0/30 = 0.00%`; `trial_hits = 0/300 = 0.00%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Prompt-Only Baseline: `mean r / M = N/A` (0 modal selections); `trial mean r / M = N/A` (0 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Prompt-Only Baseline: `mean (M - r) / M = N/A` (0 modal selections); `trial mean (M - r) / M = N/A` (0 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Prompt-Only Baseline: `mean NRS = N/A` (0 modal selections); `trial mean NRS = N/A` (0 trials)


## Experiment Setup

- **Step 1 tools**: none
- **Domain Knowledge**: Disabled
- **Candidate pool visibility to LLM**: hidden
- **Candidate pool for evaluation**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us
- **Success rule**: report `Hit@k` for `k = 1..5` against the AoU benchmark ranking using the full disease/trial denominator; if a disease has fewer than `k` evaluated models, `Top@k` includes all available benchmark-ranked models
- **Benchmark tie handling**: if the AoU benchmark AUC is tied at the `k`-th cutoff, all tied models count as `Top@k`

## Results by Disease

All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.
They are **not** PGS Catalog reported-AUC ranks.

| Ontology | N Models | Trial Hit@1..5 | Prompt-Only Baseline Hit@1..5 | Prompt-Only Baseline |
|----------|----------|---------------|------------------------------|------------------------|
| prostate cancer | 96 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| thyroid carcinoma | 32 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| hypothyroidism | 28 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| hodgkins lymphoma | 27 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| obstructive sleep apnea | 20 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| sleep apnea | 20 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| testicular neoplasm | 14 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| uterine carcinoma | 14 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| kidney cancer | 10 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| obesity | 10 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| ankylosing spondylitis | 9 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| aortic stenosis | 8 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| renal carcinoma | 8 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| graves disease | 7 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| nodular goiter | 7 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| pulmonary embolism | 7 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| abdominal aortic aneurysm | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| age-related macular degeneration | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| cervical carcinoma | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| cutaneous melanoma | 5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| late-onset alzheimer's disease | 5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| open-angle glaucoma | 5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| alcohol dependence | 4 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| hypertrophic cardiomyopathy | 4 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| juvenile idiopathic arthritis | 4 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| peripheral vascular disease | 4 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| hashimoto's thyroiditis | 3 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| preeclampsia | 3 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| skin carcinoma in situ | 3 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| vitiligo | 3 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |