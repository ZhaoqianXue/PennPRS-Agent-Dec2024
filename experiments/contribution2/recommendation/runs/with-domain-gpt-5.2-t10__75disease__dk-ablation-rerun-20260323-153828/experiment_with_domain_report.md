# Contribution2 Experiment 3: Catalog Search + Domain Knowledge

## Summary

- **Diseases**: 75
- **Trials per disease**: 10
- **Total trials**: 750
- **Model**: gpt-5.2
- **Estimated API cost**: $3.6354 (uncached input 2,364,522 tokens = $2.0690; cached input 901,632 tokens = $0.0789; output 212,502 tokens = $1.4875)

## Ablation Study Design

This three-arm ablation study isolates the incremental value of each Step 1 tool.
The candidate PGS model set is identical across all three arms; only the information depth changes.

| Arm | Components | Candidate visibility | What it tests |
|-----|-----------|---------------------|---------------|
| Prompt-Only Baseline | GPT-5.2 + system prompt | PGS IDs only (no metadata) | LLM parametric knowledge |
| Catalog Search Only | GPT-5.2 + system prompt + `prs_model_pgscatalog_search` | PGS IDs + full structured metadata | Value of structured catalog search |
| Catalog Search + Domain Knowledge | GPT-5.2 + system prompt + `prs_model_pgscatalog_search` + `prs_model_domain_knowledge` | PGS IDs + metadata + expert rules | Value of curated domain knowledge |

## High-Level Outcome

- Catalog Search + Domain Knowledge `Hit@1`: `22/75 = 29.33%`; `trial_hits = 222/750 = 29.60%`
- Catalog Search + Domain Knowledge `Hit@2`: `40/75 = 53.33%`; `trial_hits = 403/750 = 53.73%`
- Catalog Search + Domain Knowledge `Hit@3`: `44/75 = 58.67%`; `trial_hits = 455/750 = 60.67%`
- Catalog Search + Domain Knowledge `Hit@4`: `50/75 = 66.67%`; `trial_hits = 515/750 = 68.67%`
- Catalog Search + Domain Knowledge `Hit@5`: `56/75 = 74.67%`; `trial_hits = 558/750 = 74.40%`
- Catalog Search Only `Hit@1`: `18/75 = 24.00%`; `trial_hits = 178/750 = 23.73%`
- Catalog Search Only `Hit@2`: `28/75 = 37.33%`; `trial_hits = 270/750 = 36.00%`
- Catalog Search Only `Hit@3`: `42/75 = 56.00%`; `trial_hits = 406/750 = 54.13%`
- Catalog Search Only `Hit@4`: `47/75 = 62.67%`; `trial_hits = 462/750 = 61.60%`
- Catalog Search Only `Hit@5`: `48/75 = 64.00%`; `trial_hits = 479/750 = 63.87%`
- Prompt-Only Baseline `Hit@1`: `7/75 = 9.33%`; `trial_hits = 70/750 = 9.33%`
- Prompt-Only Baseline `Hit@2`: `18/75 = 24.00%`; `trial_hits = 181/750 = 24.13%`
- Prompt-Only Baseline `Hit@3`: `26/75 = 34.67%`; `trial_hits = 261/750 = 34.80%`
- Prompt-Only Baseline `Hit@4`: `31/75 = 41.33%`; `trial_hits = 307/750 = 40.93%`
- Prompt-Only Baseline `Hit@5`: `39/75 = 52.00%`; `trial_hits = 387/750 = 51.60%`

## Percentile Hit

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.
- For each percentile threshold, define the tie-aware cutoff rank as `c_q = max(1, ceil(q/100 * M))`.
- A selection counts as `Top q% Hit` if its AoU benchmark rank satisfies `r <= c_q`.
- Denominator: fixed total disease count for modal selections and fixed total trial count for trial selections.
- Tie handling: if the AoU benchmark AUC is tied at cutoff rank `c_q`, all tied models count as `Top q%`.

- Catalog Search + Domain Knowledge `Top 5% Hit`: `28/75 = 37.33%`; `trial_hits = 280/750 = 37.33%`
- Catalog Search + Domain Knowledge `Top 10% Hit`: `31/75 = 41.33%`; `trial_hits = 315/750 = 42.00%`
- Catalog Search + Domain Knowledge `Top 15% Hit`: `37/75 = 49.33%`; `trial_hits = 385/750 = 51.33%`
- Catalog Search + Domain Knowledge `Top 20% Hit`: `39/75 = 52.00%`; `trial_hits = 405/750 = 54.00%`
- Catalog Search + Domain Knowledge `Top 25% Hit`: `41/75 = 54.67%`; `trial_hits = 427/750 = 56.93%`
- Catalog Search Only `Top 5% Hit`: `22/75 = 29.33%`; `trial_hits = 210/750 = 28.00%`
- Catalog Search Only `Top 10% Hit`: `25/75 = 33.33%`; `trial_hits = 244/750 = 32.53%`
- Catalog Search Only `Top 15% Hit`: `29/75 = 38.67%`; `trial_hits = 284/750 = 37.87%`
- Catalog Search Only `Top 20% Hit`: `31/75 = 41.33%`; `trial_hits = 307/750 = 40.93%`
- Catalog Search Only `Top 25% Hit`: `35/75 = 46.67%`; `trial_hits = 346/750 = 46.13%`
- Prompt-Only Baseline `Top 5% Hit`: `7/75 = 9.33%`; `trial_hits = 70/750 = 9.33%`
- Prompt-Only Baseline `Top 10% Hit`: `9/75 = 12.00%`; `trial_hits = 87/750 = 11.60%`
- Prompt-Only Baseline `Top 15% Hit`: `10/75 = 13.33%`; `trial_hits = 97/750 = 12.93%`
- Prompt-Only Baseline `Top 20% Hit`: `11/75 = 14.67%`; `trial_hits = 107/750 = 14.27%`
- Prompt-Only Baseline `Top 25% Hit`: `12/75 = 16.00%`; `trial_hits = 117/750 = 15.60%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean r / M = 0.4286` (75 modal selections); `trial mean r / M = 0.4220` (749 trials)
- Catalog Search Only: `mean r / M = 0.4989` (75 modal selections); `trial mean r / M = 0.5071` (750 trials)
- Prompt-Only Baseline: `mean r / M = 0.6997` (75 modal selections); `trial mean r / M = 0.7008` (749 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean (M - r) / M = 0.5714` (75 modal selections); `trial mean (M - r) / M = 0.5780` (749 trials)
- Catalog Search Only: `mean (M - r) / M = 0.5011` (75 modal selections); `trial mean (M - r) / M = 0.4929` (750 trials)
- Prompt-Only Baseline: `mean (M - r) / M = 0.3003` (75 modal selections); `trial mean (M - r) / M = 0.2992` (749 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Catalog Search + Domain Knowledge: `mean NRS = 0.6772` (75 modal selections); `trial mean NRS = 0.6866` (749 trials)
- Catalog Search Only: `mean NRS = 0.5860` (75 modal selections); `trial mean NRS = 0.5771` (750 trials)
- Prompt-Only Baseline: `mean NRS = 0.3559` (75 modal selections); `trial mean NRS = 0.3548` (749 trials)

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

| Ontology | N Models | Trial Hit@1..5 | Prompt-Only Baseline Hit@1..5 | Prompt-Only Baseline | Catalog Search Only Hit@1..5 | Catalog Search Only | Catalog Search + Domain Knowledge Hit@1..5 | Catalog Search + Domain Knowledge |
|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| hypertension | 258 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000014 (AUC rank 98/258): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001320 (AUC rank 12/258): x5<br>PGS004236 (AUC rank 40/258): x5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004236 (AUC rank 40/258): x9<br>PGS001320 (AUC rank 12/258): x1 |
| breast carcinoma | 164 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000001 (AUC rank 88/164): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000007 (AUC rank 42/164): x7<br>PGS000015 (AUC rank 31/164): x2<br>PGS004153 (AUC rank 6/164): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004153 (AUC rank 6/164): x9<br>PGS000332 (AUC rank 17/164): x1 |
| arthritis | 107 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000114 (AUC rank 96/107): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001135 (AUC rank 15/107): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001135 (AUC rank 15/107): x10 |
| melanoma | 103 | 1:0.00%, 2:0.00%, 3:0.00%, 4:50.00%, 5:50.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000079 (AUC rank 22/103): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000743 (AUC rank 11/103): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002247 (AUC rank 4/103): x5<br>PGS000422 (AUC rank 28/103): x2<br>PGS000766 (AUC rank 8/103): x1<br>PGS000813 (AUC rank 14/103): x1<br>PGS000424 (AUC rank 17/103): x1 |
| prostate cancer | 96 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005241 (AUC rank 88/96): x6<br>PGS000030 (AUC rank 29/96): x4 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005238 (AUC rank 51/96): x9<br>PGS000662 (AUC rank 77/96): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004155 (AUC rank 30/96): x6<br>PGS004042 (AUC rank 43/96): x1<br>PGS004139 (AUC rank 62/96): x1<br>PGS003415 (AUC rank 79/96): x1<br>PGS004584 (AUC rank -): x1 |
| coronary artery disease | 85 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000010 (AUC rank 75/85): x6<br>PGS005322 (AUC rank 80/85): x4 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003725 (AUC rank 2/85): x8<br>PGS002244 (AUC rank 37/85): x2 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003725 (AUC rank 2/85): x10 |
| asthma | 66 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000037 (AUC rank 61/66): x9<br>PGS005148 (AUC rank 66/66): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001344 (AUC rank 16/66): x5<br>PGS001787 (AUC rank 6/66): x4<br>PGS002727 (AUC rank 41/66): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002727 (AUC rank 41/66): x8<br>PGS001344 (AUC rank 16/66): x2 |
| dementia | 65 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000025 (AUC rank 42/65): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005170 (AUC rank 2/65): x8<br>PGS004281 (AUC rank 7/65): x1<br>PGS000929 (AUC rank 14/65): x1 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005170 (AUC rank 2/65): x10 |
| gout | 63 | 1:0.00%, 2:20.00%, 3:20.00%, 4:20.00%, 5:20.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000199 (AUC rank 31/63): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001789 (AUC rank 15/63): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001789 (AUC rank 15/63): x8<br>PGS004160 (AUC rank 2/63): x2 |
| atrial fibrillation | 61 | 1:10.00%, 2:10.00%, 3:10.00%, 4:10.00%, 5:10.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000016 (AUC rank 40/61): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005168 (AUC rank 52/61): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005168 (AUC rank 52/61): x9<br>PGS005313 (AUC rank 1/61): x1 |
| rheumatoid arthritis | 48 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004873 (AUC rank 4/48): x6<br>PGS000114 (AUC rank 35/48): x4 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004163 (AUC rank 3/48): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004163 (AUC rank 3/48): x10 |
| ovarian neoplasm | 42 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000048 (AUC rank 14/42): x9<br>PGS005166 (AUC rank 42/42): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000549 (AUC rank 18/42): x5<br>PGS000550 (AUC rank 34/42): x5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000550 (AUC rank 34/42): x8<br>PGS000549 (AUC rank 18/42): x2 |
| lung cancer | 35 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000070 (AUC rank 30/35): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004860 (AUC rank 1/35): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000078 (AUC rank 18/35): x10 |
| myocardial infarction | 35 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000117 (AUC rank 35/35): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001314 (AUC rank 21/35): x7<br>PGS001315 (AUC rank 18/35): x3 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005039 (AUC rank 2/35): x10 |
| heart failure | 34 | 1:10.00%, 2:10.00%, 3:10.00%, 4:20.00%, 5:80.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000709 (AUC rank 19/34): x9<br>PGS005319 (AUC rank 30/34): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001790 (AUC rank 11/34): x8<br>PGS005077 (AUC rank 4/34): x1<br>PGS005083 (AUC rank 5/34): x1 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS005083 (AUC rank 5/34): x6<br>PGS001790 (AUC rank 11/34): x2<br>PGS005097 (AUC rank 1/34): x1<br>PGS005077 (AUC rank 4/34): x1 |
| thyroid carcinoma | 32 | 1:0.00%, 2:0.00%, 3:0.00%, 4:40.00%, 5:40.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000087 (AUC rank 19/32): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000208 (AUC rank 16/32): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005259 (AUC rank 4/32): x4<br>PGS000208 (AUC rank 16/32): x4<br>PGS000207 (AUC rank 15/32): x2 |
| psoriasis | 31 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000342 (AUC rank 24/31): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001312 (AUC rank 15/31): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001312 (AUC rank 15/31): x10 |
| depressive disorder | 30 | 1:40.00%, 2:50.00%, 3:50.00%, 4:50.00%, 5:50.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000138 (AUC rank 22/30): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002036 (AUC rank 21/30): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002036 (AUC rank 21/30): x5<br>PGS004760 (AUC rank 1/30): x4<br>PGS003333 (AUC rank 2/30): x1 |
| hypothyroidism | 28 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000759 (AUC rank 19/28): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x10 |
| hodgkins lymphoma | 27 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000080 (AUC rank 17/27): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 |
| kidney failure | 27 | 1:50.00%, 2:50.00%, 3:90.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000708 (AUC rank 3/27): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000708 (AUC rank 3/27): x8<br>PGS004492 (AUC rank 4/27): x2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004562 (AUC rank 1/27): x5<br>PGS000708 (AUC rank 3/27): x4<br>PGS004492 (AUC rank 4/27): x1 |
| chronic kidney disease | 22 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000728 (AUC rank 19/22): x9<br>PGS004224 (AUC rank 14/22): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002237 (AUC rank 12/22): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002237 (AUC rank 12/22): x10 |
| basal cell carcinoma | 20 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000119 (AUC rank 13/20): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000452 (AUC rank 4/20): x7<br>PGS000119 (AUC rank 13/20): x3 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000452 (AUC rank 4/20): x10 |
| sleep apnea | 20 | 1:20.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003204 (AUC rank 17/20): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x9<br>PGS003213 (AUC rank 4/20): x1 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005219 (AUC rank 2/20): x8<br>PGS005220 (AUC rank 1/20): x2 |
| urinary bladder cancer | 20 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:30.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000071 (AUC rank 4/20): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000071 (AUC rank 4/20): x5<br>PGS000723 (AUC rank 8/20): x2<br>PGS000611 (AUC rank 11/20): x2<br>PGS000613 (AUC rank 5/20): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000611 (AUC rank 11/20): x7<br>PGS000613 (AUC rank 5/20): x3 |
| angina pectoris | 19 | 1:0.00%, 2:60.00%, 3:60.00%, 4:60.00%, 5:60.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000703 (AUC rank 12/19): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001262 (AUC rank 15/19): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005052 (AUC rank 2/19): x6<br>PGS004527 (AUC rank 10/19): x3<br>PGS001262 (AUC rank 15/19): x1 |
| squamous cell carcinoma | 18 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000120 (AUC rank 10/18): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000731 (AUC rank 11/18): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000461 (AUC rank 5/18): x10 |
| uterine cancer | 18 | 1:0.00%, 2:0.00%, 3:40.00%, 4:40.00%, 5:40.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000073 (AUC rank 18/18): x9 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000541 (AUC rank 7/18): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001795 (AUC rank 13/18): x6<br>PGS003381 (AUC rank 3/18): x4 |
| retinopathy | 17 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000819 (AUC rank 10/17): x9<br>PGS002269 (AUC rank 2/17): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002027 (AUC rank 9/17): x8<br>PGS000819 (AUC rank 10/17): x2 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000819 (AUC rank 10/17): x6<br>PGS002027 (AUC rank 9/17): x4 |
| glaucoma | 15 | 1:0.00%, 2:0.00%, 3:0.00%, 4:10.00%, 5:90.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000137 (AUC rank 6/15): x9<br>PGS001836 (AUC rank 11/15): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000137 (AUC rank 6/15): x5<br>PGS001792 (AUC rank 5/15): x4<br>PGS004944 (AUC rank 4/15): x1 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001792 (AUC rank 5/15): x8<br>PGS004944 (AUC rank 4/15): x1<br>PGS001797 (AUC rank 7/15): x1 |
| lupus erythematosus | 13 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000196 (AUC rank 5/13): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001870 (AUC rank 9/13): x6<br>PGS003960 (AUC rank 11/13): x2<br>PGS000328 (AUC rank 6/13): x1<br>PGS002082 (AUC rank 10/13): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000328 (AUC rank 6/13): x5<br>PGS000754 (AUC rank 12/13): x3<br>PGS002082 (AUC rank 10/13): x2 |
| lymphoid leukemia | 13 | 1:0.00%, 2:0.00%, 3:0.00%, 4:80.00%, 5:80.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000077 (AUC rank 9/13): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000788 (AUC rank 4/13): x7<br>PGS000077 (AUC rank 9/13): x3 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000788 (AUC rank 4/13): x8<br>PGS000077 (AUC rank 9/13): x2 |
| osteoporosis | 13 | 1:20.00%, 2:20.00%, 3:20.00%, 4:20.00%, 5:50.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001273 (AUC rank 5/13): x10 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001273 (AUC rank 5/13): x6<br>PGS001274 (AUC rank 4/13): x4 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001273 (AUC rank 5/13): x3<br>PGS004565 (AUC rank 8/13): x3<br>PGS004810 (AUC rank 1/13): x2<br>PGS005155 (AUC rank 12/13): x2 |
| testicular carcinoma | 13 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000595 (AUC rank 12/13): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001164 (AUC rank 3/13): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000604 (AUC rank 9/13): x10 |
| parkinson disease | 11 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000056 (AUC rank 7/11): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000903 (AUC rank 1/11): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000903 (AUC rank 1/11): x10 |
| chronic obstructive pulmonary disease | 10 | 1:90.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001326 (AUC rank 10/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001783 (AUC rank 1/10): x8<br>PGS002062 (AUC rank 4/10): x2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001783 (AUC rank 1/10): x9<br>PGS004536 (AUC rank 2/10): x1 |
| kidney cancer | 10 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000076 (AUC rank 7/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 |
| obesity | 10 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10): x9<br>PGS002033 (AUC rank 4/10): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005235 (AUC rank 1/10): x10 |
| ankylosing spondylitis | 9 | 1:0.00%, 2:0.00%, 3:0.00%, 4:90.00%, 5:90.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001267 (AUC rank 2/9): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001268 (AUC rank 3/9): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002089 (AUC rank 4/9): x9<br>PGS003420 (AUC rank 7/9): x1 |
| aortic stenosis | 8 | 1:60.00%, 2:60.00%, 3:60.00%, 4:60.00%, 5:60.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000739 (AUC rank 7/8): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005252 (AUC rank 8/8): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005254 (AUC rank 1/8): x6<br>PGS005252 (AUC rank 8/8): x4 |
| dilated cardiomyopathy | 8 | 1:50.00%, 2:90.00%, 3:90.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004861 (AUC rank 8/8): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004861 (AUC rank 8/8): x8<br>PGS004862 (AUC rank 4/8): x2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004951 (AUC rank 1/8): x5<br>PGS004949 (AUC rank 2/8): x4<br>PGS004862 (AUC rank 4/8): x1 |
| hip osteoarthritis | 7 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000967 (AUC rank 4/7): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000967 (AUC rank 4/7): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002763 (AUC rank 1/7): x10 |
| hyperthyroidism | 7 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001042 (AUC rank 5/7): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001043 (AUC rank 7/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x10 |
| knee osteoarthritis | 7 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001192 (AUC rank 5/7): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002729 (AUC rank 7/7): x9<br>PGS001192 (AUC rank 5/7): x1 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002767 (AUC rank 2/7): x10 |
| macular degeneration | 7 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001013 (AUC rank 6/7): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 3/7): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 3/7): x10 |
| nodular goiter | 7 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001814 (AUC rank 5/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 |
| pulmonary embolism | 7 | 1:0.00%, 2:30.00%, 3:30.00%, 4:30.00%, 5:30.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001277 (AUC rank 3/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001280 (AUC rank 2/7): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004460 (AUC rank 6/7): x5<br>PGS001280 (AUC rank 2/7): x3<br>PGS003861 (AUC rank 7/7): x2 |
| abdominal aortic aneurysm | 6 | 1:0.00%, 2:0.00%, 3:40.00%, 4:40.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000753 (AUC rank 5/6): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003973 (AUC rank 1/6): x10 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000753 (AUC rank 5/6): x6<br>PGS003972 (AUC rank 3/6): x4 |
| atopic eczema | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001773 (AUC rank 5/6): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002755 (AUC rank 4/6): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002755 (AUC rank 4/6): x10 |
| cervical carcinoma | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000073 (AUC rank 1/6): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 6/6): x8<br>PGS003428 (AUC rank 5/6): x2 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS003428 (AUC rank 5/6): x10 |
| late-onset alzheimer's disease | 5 | 1:30.00%, 2:30.00%, 3:30.00%, 4:30.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000053 (AUC rank 5/5): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000334 (AUC rank 3/5): x8<br>PGS000053 (AUC rank 5/5): x2 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000053 (AUC rank 5/5): x7<br>PGS000054 (AUC rank 1/5): x3 |
| urolithiasis | 5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001250 (AUC rank 3/5): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001250 (AUC rank 3/5): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004563 (AUC rank 1/5): x10 |
| alcohol dependence | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000201 (AUC rank 2/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x10 |
| atrial flutter | 4 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001263 (AUC rank 4/4): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001263 (AUC rank 4/4): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001263 (AUC rank 4/4): x10 |
| hypertrophic cardiomyopathy | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000739 (AUC rank 2/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x10 |
| juvenile idiopathic arthritis | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 |
| peripheral vascular disease | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001843 (AUC rank 4/4): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002055 (AUC rank 2/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005217 (AUC rank 1/4): x10 |
| psoriatic arthritis | 4 | 1:30.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000342 (AUC rank 2/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001287 (AUC rank 1/4): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000342 (AUC rank 2/4): x7<br>PGS001287 (AUC rank 1/4): x3 |
| sarcoidosis | 4 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000922 (AUC rank 2/4): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000922 (AUC rank 2/4): x6<br>PGS000923 (AUC rank 3/4): x4 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000922 (AUC rank 2/4): x10 |
| bilirubin metabolism disease | 3 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000924 (AUC rank 3/3): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000924 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002032 (AUC rank 2/3): x10 |
| bipolar disorder | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002786 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002786 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002786 (AUC rank 1/3): x10 |
| blood coagulation disease | 3 | 1:10.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001033 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001033 (AUC rank 1/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002034 (AUC rank 2/3): x9<br>PGS001033 (AUC rank 1/3): x1 |
| dupuytren contracture | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001254 (AUC rank 3/3): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001254 (AUC rank 3/3): x9<br>PGS002092 (AUC rank 1/3): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002092 (AUC rank 1/3): x10 |
| hashimoto's thyroiditis | 3 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005270 (AUC rank 3/3): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005270 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005271 (AUC rank 2/3): x10 |
| preeclampsia | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 |
| pulmonary fibrosis | 3 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001030 (AUC rank 3/3): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001030 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001791 (AUC rank 2/3): x10 |
| skin carcinoma in situ | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000469 (AUC rank 3/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x10 |
| vitiligo | 3 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000738 (AUC rank 2/3): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001536 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000738 (AUC rank 2/3): x10 |
| autism spectrum disorder | 2 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000327 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000327 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000327 (AUC rank 2/2): x10 |
| congenital vitamin k-dependent coagulation factors deficiency | 2 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001826 (AUC rank 1/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002034 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002034 (AUC rank 2/2): x10 |
| corneal dystrophy | 2 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001835 (AUC rank 2/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002042 (AUC rank 1/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002042 (AUC rank 1/2): x10 |
| iron metabolism disease | 2 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001823 (AUC rank 2/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002031 (AUC rank 1/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002031 (AUC rank 1/2): x10 |
| nasal cavity polyp | 2 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004465 (AUC rank 1/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004535 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004535 (AUC rank 2/2): x10 |
| nicotine dependence | 2 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001830 (AUC rank 2/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002037 (AUC rank 1/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002037 (AUC rank 1/2): x10 |
| otosclerosis | 2 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001255 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001255 (AUC rank 2/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002046 (AUC rank 1/2): x10 |