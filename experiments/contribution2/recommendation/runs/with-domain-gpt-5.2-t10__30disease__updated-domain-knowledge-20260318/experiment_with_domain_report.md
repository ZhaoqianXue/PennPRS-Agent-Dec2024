# Contribution2 Experiment 3: Catalog Search + Domain Knowledge

## Summary

- **Diseases**: 30
- **Trials per disease**: 10
- **Total trials**: 300
- **Model**: gpt-5.2
- **Estimated API cost**: $3.6476 (uncached input 1,369,200 tokens = $2.3961; cached input 0 tokens = $0.0000; output 89,393 tokens = $1.2515)

## Ablation Study Design

This three-arm ablation study isolates the incremental value of each Step 1 tool.
The candidate PGS model set is identical across all three arms; only the information depth changes.


| Arm                               | Components                                                                             | Candidate visibility               | What it tests                      |
| --------------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------- | ---------------------------------- |
| Prompt-Only Baseline              | GPT-5.2 + system prompt                                                                | PGS IDs only (no metadata)         | LLM parametric knowledge           |
| Catalog Search Only               | GPT-5.2 + system prompt + `prs_model_pgscatalog_search`                                | PGS IDs + full structured metadata | Value of structured catalog search |
| Catalog Search + Domain Knowledge | GPT-5.2 + system prompt + `prs_model_pgscatalog_search` + `prs_model_domain_knowledge` | PGS IDs + metadata + expert rules  | Value of curated domain knowledge  |


## High-Level Outcome

- Catalog Search + Domain Knowledge `Hit@1`: `16/30 = 53.33%`; `trial_hits = 157/300 = 52.33%`
- Catalog Search + Domain Knowledge `Hit@2`: `20/30 = 66.67%`; `trial_hits = 207/300 = 69.00%`
- Catalog Search + Domain Knowledge `Hit@3`: `24/30 = 80.00%`; `trial_hits = 240/300 = 80.00%`
- Catalog Search + Domain Knowledge `Hit@4`: `26/30 = 86.67%`; `trial_hits = 260/300 = 86.67%`
- Catalog Search + Domain Knowledge `Hit@5`: `27/30 = 90.00%`; `trial_hits = 270/300 = 90.00%`
- Catalog Search Only `Hit@1`: `14/30 = 46.67%`; `trial_hits = 140/300 = 46.67%`
- Catalog Search Only `Hit@2`: `18/30 = 60.00%`; `trial_hits = 181/300 = 60.33%`
- Catalog Search Only `Hit@3`: `24/30 = 80.00%`; `trial_hits = 237/300 = 79.00%`
- Catalog Search Only `Hit@4`: `24/30 = 80.00%`; `trial_hits = 239/300 = 79.67%`
- Catalog Search Only `Hit@5`: `24/30 = 80.00%`; `trial_hits = 240/300 = 80.00%`
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
- Catalog Search + Domain Knowledge `Top 5% Hit`: `16/30 = 53.33%`; `trial_hits = 157/300 = 52.33%`
- Catalog Search + Domain Knowledge `Top 10% Hit`: `18/30 = 60.00%`; `trial_hits = 171/300 = 57.00%`
- Catalog Search + Domain Knowledge `Top 15% Hit`: `21/30 = 70.00%`; `trial_hits = 204/300 = 68.00%`
- Catalog Search + Domain Knowledge `Top 20% Hit`: `21/30 = 70.00%`; `trial_hits = 206/300 = 68.67%`
- Catalog Search + Domain Knowledge `Top 25% Hit`: `21/30 = 70.00%`; `trial_hits = 213/300 = 71.00%`
- Catalog Search Only `Top 5% Hit`: `14/30 = 46.67%`; `trial_hits = 140/300 = 46.67%`
- Catalog Search Only `Top 10% Hit`: `15/30 = 50.00%`; `trial_hits = 153/300 = 51.00%`
- Catalog Search Only `Top 15% Hit`: `18/30 = 60.00%`; `trial_hits = 183/300 = 61.00%`
- Catalog Search Only `Top 20% Hit`: `19/30 = 63.33%`; `trial_hits = 189/300 = 63.00%`
- Catalog Search Only `Top 25% Hit`: `20/30 = 66.67%`; `trial_hits = 199/300 = 66.33%`
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
- Catalog Search + Domain Knowledge: `mean r / M = 0.3253` (30 modal selections); `trial mean r / M = 0.3251` (300 trials)
- Catalog Search Only: `mean r / M = 0.3873` (30 modal selections); `trial mean r / M = 0.3883` (300 trials)
- Prompt-Only Baseline: `mean r / M = 0.6901` (30 modal selections); `trial mean r / M = 0.6886` (300 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean (M - r) / M = 0.6747` (30 modal selections); `trial mean (M - r) / M = 0.6749` (300 trials)
- Catalog Search Only: `mean (M - r) / M = 0.6127` (30 modal selections); `trial mean (M - r) / M = 0.6117` (300 trials)
- Prompt-Only Baseline: `mean (M - r) / M = 0.3099` (30 modal selections); `trial mean (M - r) / M = 0.3114` (300 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Catalog Search + Domain Knowledge: `mean NRS = 0.7958` (30 modal selections); `trial mean NRS = 0.7959` (300 trials)
- Catalog Search Only: `mean NRS = 0.7256` (30 modal selections); `trial mean NRS = 0.7253` (300 trials)
- Prompt-Only Baseline: `mean NRS = 0.3715` (30 modal selections); `trial mean NRS = 0.3735` (300 trials)

## Experiment Setup

- **Step 1 tools**: prs_model_pgscatalog_search + prs_model_domain_knowledge
- **Domain Knowledge**: Enabled (local curated knowledge base)
- **Candidate pool**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us
- **Success rule**: report `Hit@k` for `k = 1..5` against the AoU benchmark ranking using the full disease/trial denominator; if a disease has fewer than `k` evaluated models, `Top@k` includes all available benchmark-ranked models
- **Benchmark tie handling**: if the AoU benchmark AUC is tied at the `k`-th cutoff, all tied models count as `Top@k`
- **Catalog Search Only reference**: compare against the matching archived `without-domain-gpt-5.2-t10__<dataset>` run under the same disease-list / 10-trial protocol

## Results by Disease

All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.
They are **not** PGS Catalog reported-AUC ranks.


| Ontology                         | N Models | Trial Hit@1..5                                        | Prompt-Only Baseline Hit@1..5     | Prompt-Only Baseline                                          | Catalog Search Only Hit@1..5      | Catalog Search Only                                                                        | Catalog Search + Domain Knowledge Hit@1..5 | Catalog Search + Domain Knowledge                                                         |
| -------------------------------- | -------- | ----------------------------------------------------- | --------------------------------- | ------------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------ | ----------------------------------------------------------------------------------------- |
| prostate cancer                  | 96       | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00%           | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS000030 (AUC rank 29/96): x8 PGS005241 (AUC rank 88/96): x2 | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS005238 (AUC rank 51/96): x10                                                            | 1:No, 2:No, 3:No, 4:No, 5:No               | PGS004155 (AUC rank 30/96): x10                                                           |
| thyroid carcinoma                | 32       | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00%       | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS000087 (AUC rank 19/32): x10                               | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS000208 (AUC rank 16/32): x10                                                            | 1:No, 2:No, 3:No, 4:Yes, 5:Yes             | PGS005259 (AUC rank 4/32): x10                                                            |
| hypothyroidism                   | 28       | 1:40.00%, 2:40.00%, 3:80.00%, 4:80.00%, 5:80.00%      | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS000759 (AUC rank 19/28): x9 PGS005272 (AUC rank 20/28): x1 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes   | PGS005218 (AUC rank 3/28): x10                                                             | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes            | PGS005268 (AUC rank 1/28): x4 PGS005218 (AUC rank 3/28): x4 PGS004790 (AUC rank 6/28): x2 |
| hodgkins lymphoma                | 27       | 1:90.00%, 2:90.00%, 3:90.00%, 4:90.00%, 5:90.00%      | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS000080 (AUC rank 17/27): x10                               | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10                                                             | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS000639 (AUC rank 1/27): x9 PGS000637 (AUC rank 11/27): x1                              |
| obstructive sleep apnea          | 20       | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS003204 (AUC rank 17/20): x10                               | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x7 PGS005219 (AUC rank 2/20): x3                                | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS005220 (AUC rank 1/20): x10                                                            |
| sleep apnea                      | 20       | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS003204 (AUC rank 17/20): x10                               | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10                                                             | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS005220 (AUC rank 1/20): x10                                                            |
| testicular neoplasm              | 14       | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00%           | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS000595 (AUC rank 13/14): x10                               | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes   | PGS001164 (AUC rank 3/14): x6 PGS000604 (AUC rank 10/14): x3 PGS000796 (AUC rank 1/14): x1 | 1:No, 2:No, 3:No, 4:No, 5:No               | PGS000604 (AUC rank 10/14): x10                                                           |
| uterine carcinoma                | 14       | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00%     | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS000073 (AUC rank 14/14): x7 PGS003428 (AUC rank 7/14): x3  | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS001795 (AUC rank 9/14): x10                                                             | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes            | PGS003381 (AUC rank 3/14): x10                                                            |
| kidney cancer                    | 10       | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes     | PGS000076 (AUC rank 5/10): x8 PGS004908 (AUC rank 1/10): x2   | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10                                                             | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS004908 (AUC rank 1/10): x10                                                            |
| obesity                          | 10       | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS001298 (AUC rank 8/10): x10                                | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS001298 (AUC rank 8/10): x10                                                             | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS005235 (AUC rank 1/10): x10                                                            |
| ankylosing spondylitis           | 9        | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00%       | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes  | PGS001267 (AUC rank 2/9): x9 PGS003420 (AUC rank 7/9): x1     | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes   | PGS001268 (AUC rank 3/9): x10                                                              | 1:No, 2:No, 3:No, 4:Yes, 5:Yes             | PGS002089 (AUC rank 4/9): x10                                                             |
| aortic stenosis                  | 8        | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS000739 (AUC rank 7/8): x10                                 | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS005252 (AUC rank 8/8): x10                                                              | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS005254 (AUC rank 1/8): x10                                                             |
| renal carcinoma                  | 8        | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes     | PGS000076 (AUC rank 5/8): x10                                 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/8): x10                                                              | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS004908 (AUC rank 1/8): x10                                                             |
| graves disease                   | 7        | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00%   | 1:No, 2:No, 3:No, 4:No, 5:Yes     | PGS001042 (AUC rank 5/7): x10                                 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes  | PGS005265 (AUC rank 2/7): x10                                                              | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes           | PGS005265 (AUC rank 2/7): x10                                                             |
| nodular goiter                   | 7        | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00%   | 1:No, 2:No, 3:No, 4:No, 5:Yes     | PGS001814 (AUC rank 5/7): x10                                 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes  | PGS005262 (AUC rank 2/7): x10                                                              | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes           | PGS005262 (AUC rank 2/7): x10                                                             |
| pulmonary embolism               | 7        | 1:0.00%, 2:30.00%, 3:30.00%, 4:30.00%, 5:30.00%       | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes   | PGS001277 (AUC rank 3/7): x10                                 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes  | PGS001280 (AUC rank 2/7): x10                                                              | 1:No, 2:No, 3:No, 4:No, 5:No               | PGS004460 (AUC rank 6/7): x5 PGS001280 (AUC rank 2/7): x3 PGS003861 (AUC rank 7/7): x2    |
| abdominal aortic aneurysm        | 6        | 1:10.00%, 2:10.00%, 3:100.00%, 4:100.00%, 5:100.00%   | 1:No, 2:No, 3:No, 4:No, 5:Yes     | PGS000753 (AUC rank 5/6): x10                                 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003973 (AUC rank 1/6): x8 PGS001784 (AUC rank 4/6): x2                                  | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes            | PGS003972 (AUC rank 3/6): x9 PGS003973 (AUC rank 1/6): x1                                 |
| age-related macular degeneration | 6        | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes    | PGS001834 (AUC rank 4/6): x10                                 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 1/6): x10                                                              | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS004606 (AUC rank 1/6): x10                                                             |
| cervical carcinoma               | 6        | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00%         | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000073 (AUC rank 1/6): x10                                 | 1:No, 2:No, 3:No, 4:No, 5:No      | PGS001299 (AUC rank 6/6): x7 PGS000073 (AUC rank 1/6): x2 PGS003428 (AUC rank 5/6): x1     | 1:No, 2:No, 3:No, 4:No, 5:Yes              | PGS003428 (AUC rank 5/6): x10                                                             |
| cutaneous melanoma               | 5        | 1:60.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00%  | 1:No, 2:No, 3:No, 4:No, 5:Yes     | PGS000339 (AUC rank 5/5): x10                                 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003382 (AUC rank 1/5): x10                                                              | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS003382 (AUC rank 1/5): x6 PGS004247 (AUC rank 2/5): x4                                 |
| late-onset alzheimer's disease   | 5        | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes     | PGS000053 (AUC rank 5/5): x10                                 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes   | PGS000334 (AUC rank 3/5): x10                                                              | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS000054 (AUC rank 1/5): x10                                                             |
| open-angle glaucoma              | 5        | 1:70.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00%  | 1:No, 2:No, 3:No, 4:No, 5:Yes     | PGS000350 (AUC rank 5/5): x10                                 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004944 (AUC rank 1/5): x10                                                              | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS004944 (AUC rank 1/5): x7 PGS001797 (AUC rank 2/5): x3                                 |
| alcohol dependence               | 4        | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes  | PGS000201 (AUC rank 2/4): x10                                 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x10                                                              | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS002738 (AUC rank 1/4): x10                                                             |
| hypertrophic cardiomyopathy      | 4        | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes  | PGS000739 (AUC rank 2/4): x10                                 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x10                                                              | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS004911 (AUC rank 1/4): x10                                                             |
| juvenile idiopathic arthritis    | 4        | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10                                 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10                                                              | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS000114 (AUC rank 1/4): x10                                                             |
| peripheral vascular disease      | 4        | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes    | PGS001843 (AUC rank 4/4): x10                                 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes  | PGS002055 (AUC rank 2/4): x8 PGS005217 (AUC rank 1/4): x2                                  | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS005217 (AUC rank 1/4): x10                                                             |
| hashimoto's thyroiditis          | 3        | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00%   | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes   | PGS005270 (AUC rank 3/3): x10                                 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes   | PGS005270 (AUC rank 3/3): x10                                                              | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes           | PGS005271 (AUC rank 2/3): x10                                                             |
| preeclampsia                     | 3        | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10                                 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10                                                              | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes          | PGS003586 (AUC rank 1/3): x10                                                             |
| skin carcinoma in situ           | 3        | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00%     | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes   | PGS000469 (AUC rank 3/3): x10                                 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x10                                                              | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes            | PGS000469 (AUC rank 3/3): x10                                                             |
| vitiligo                         | 3        | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00%   | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes  | PGS000738 (AUC rank 2/3): x10                                 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes   | PGS001536 (AUC rank 3/3): x10                                                              | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes           | PGS000738 (AUC rank 2/3): x10                                                             |


