# Contribution2: Three-Arm Ablation Comparison

## Summary

- **Model**: gpt-5.2
- **Disease count**: 75

## Ablation Study Design

This three-arm ablation study isolates the incremental value of each Step 1 tool.
The candidate PGS model set is identical across all three arms; only the information depth changes.

| Arm | Components | Candidate visibility | What it tests |
|-----|-----------|---------------------|---------------|
| Prompt-Only Baseline | GPT-5.2 + system prompt | PGS IDs only (no metadata) | LLM parametric knowledge |
| Catalog Search Only | GPT-5.2 + system prompt + `prs_model_pgscatalog_search` | PGS IDs + full structured metadata | Value of structured catalog search |
| Catalog Search + Domain Knowledge | GPT-5.2 + system prompt + `prs_model_pgscatalog_search` + `prs_model_domain_knowledge` | PGS IDs + metadata + expert rules | Value of curated domain knowledge |

## High-Level Outcome

- Catalog Search + Domain Knowledge `Hit@1`: `28/75 = 37.33%`; `trial_hits = 272/750 = 36.27%`
- Catalog Search + Domain Knowledge `Hit@2`: `43/75 = 57.33%`; `trial_hits = 419/750 = 55.87%`
- Catalog Search + Domain Knowledge `Hit@3`: `51/75 = 68.00%`; `trial_hits = 496/750 = 66.13%`
- Catalog Search + Domain Knowledge `Hit@4`: `58/75 = 77.33%`; `trial_hits = 570/750 = 76.00%`
- Catalog Search + Domain Knowledge `Hit@5`: `59/75 = 78.67%`; `trial_hits = 582/750 = 77.60%`
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

- Catalog Search + Domain Knowledge `Top 5% Hit`: `33/75 = 44.00%`; `trial_hits = 319/750 = 42.53%`
- Catalog Search + Domain Knowledge `Top 10% Hit`: `37/75 = 49.33%`; `trial_hits = 350/750 = 46.67%`
- Catalog Search + Domain Knowledge `Top 15% Hit`: `44/75 = 58.67%`; `trial_hits = 420/750 = 56.00%`
- Catalog Search + Domain Knowledge `Top 20% Hit`: `46/75 = 61.33%`; `trial_hits = 443/750 = 59.07%`
- Catalog Search + Domain Knowledge `Top 25% Hit`: `47/75 = 62.67%`; `trial_hits = 460/750 = 61.33%`
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
- Catalog Search + Domain Knowledge: `mean r / M = 0.3829` (75 modal selections); `trial mean r / M = 0.3876` (750 trials)
- Catalog Search Only: `mean r / M = 0.4989` (75 modal selections); `trial mean r / M = 0.5071` (750 trials)
- Prompt-Only Baseline: `mean r / M = 0.6997` (75 modal selections); `trial mean r / M = 0.7008` (749 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean (M - r) / M = 0.6171` (75 modal selections); `trial mean (M - r) / M = 0.6124` (750 trials)
- Catalog Search Only: `mean (M - r) / M = 0.5011` (75 modal selections); `trial mean (M - r) / M = 0.4929` (750 trials)
- Prompt-Only Baseline: `mean (M - r) / M = 0.3003` (75 modal selections); `trial mean (M - r) / M = 0.2992` (749 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Catalog Search + Domain Knowledge: `mean NRS = 0.7327` (75 modal selections); `trial mean NRS = 0.7267` (750 trials)
- Catalog Search Only: `mean NRS = 0.5860` (75 modal selections); `trial mean NRS = 0.5771` (750 trials)
- Prompt-Only Baseline: `mean NRS = 0.3559` (75 modal selections); `trial mean NRS = 0.3548` (749 trials)


## Results by Disease

| Ontology | N Models | Prompt-Only Baseline Hit@1..5 | Prompt-Only Baseline | Catalog Search Only Hit@1..5 | Catalog Search Only | Catalog Search + Domain Knowledge Hit@1..5 | Catalog Search + Domain Knowledge |
|----------|----------|----------|----------|----------|----------|----------|----------|
| hypertension | 258 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000014 (AUC rank 98/258): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001320 (AUC rank 12/258): x5<br>PGS004236 (AUC rank 40/258): x5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004236 (AUC rank 40/258): x10 |
| breast carcinoma | 164 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000001 (AUC rank 88/164): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000007 (AUC rank 42/164): x7<br>PGS000015 (AUC rank 31/164): x2<br>PGS004153 (AUC rank 6/164): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004153 (AUC rank 6/164): x10 |
| arthritis | 107 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000114 (AUC rank 96/107): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001135 (AUC rank 15/107): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001135 (AUC rank 15/107): x10 |
| melanoma | 103 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000079 (AUC rank 22/103): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000743 (AUC rank 11/103): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004796 (AUC rank 15/103): x10 |
| prostate cancer | 96 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005241 (AUC rank 88/96): x6<br>PGS000030 (AUC rank 29/96): x4 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005238 (AUC rank 51/96): x9<br>PGS000662 (AUC rank 77/96): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004155 (AUC rank 30/96): x10 |
| coronary artery disease | 85 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000010 (AUC rank 75/85): x6<br>PGS005322 (AUC rank 80/85): x4 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003725 (AUC rank 2/85): x8<br>PGS002244 (AUC rank 37/85): x2 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004745 (AUC rank 4/85): x9<br>PGS003725 (AUC rank 2/85): x1 |
| asthma | 66 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000037 (AUC rank 61/66): x9<br>PGS005148 (AUC rank 66/66): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001344 (AUC rank 16/66): x5<br>PGS001787 (AUC rank 6/66): x4<br>PGS002727 (AUC rank 41/66): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004725 (AUC rank 1/66): x10 |
| dementia | 65 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000025 (AUC rank 42/65): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005170 (AUC rank 2/65): x8<br>PGS004281 (AUC rank 7/65): x1<br>PGS000929 (AUC rank 14/65): x1 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005170 (AUC rank 2/65): x9<br>PGS000929 (AUC rank 14/65): x1 |
| gout | 63 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000199 (AUC rank 31/63): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001789 (AUC rank 15/63): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004768 (AUC rank 1/63): x10 |
| atrial fibrillation | 61 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000016 (AUC rank 40/61): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005168 (AUC rank 52/61): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005168 (AUC rank 52/61): x10 |
| rheumatoid arthritis | 48 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004873 (AUC rank 4/48): x6<br>PGS000114 (AUC rank 35/48): x4 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004163 (AUC rank 3/48): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004163 (AUC rank 3/48): x8<br>PGS004819 (AUC rank 1/48): x2 |
| ovarian neoplasm | 42 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000048 (AUC rank 14/42): x9<br>PGS005166 (AUC rank 42/42): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000549 (AUC rank 18/42): x5<br>PGS000550 (AUC rank 34/42): x5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000550 (AUC rank 34/42): x5<br>PGS000549 (AUC rank 18/42): x4<br>PGS003394 (AUC rank 24/42): x1 |
| lung cancer | 35 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000070 (AUC rank 30/35): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004860 (AUC rank 1/35): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004860 (AUC rank 1/35): x8<br>PGS000789 (AUC rank 17/35): x2 |
| myocardial infarction | 35 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000117 (AUC rank 35/35): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001314 (AUC rank 21/35): x7<br>PGS001315 (AUC rank 18/35): x3 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005039 (AUC rank 2/35): x10 |
| heart failure | 34 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000709 (AUC rank 19/34): x9<br>PGS005319 (AUC rank 30/34): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001790 (AUC rank 11/34): x8<br>PGS005077 (AUC rank 4/34): x1<br>PGS005083 (AUC rank 5/34): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005097 (AUC rank 1/34): x10 |
| thyroid carcinoma | 32 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000087 (AUC rank 19/32): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000208 (AUC rank 16/32): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS005259 (AUC rank 4/32): x5<br>PGS000208 (AUC rank 16/32): x4<br>PGS000207 (AUC rank 15/32): x1 |
| psoriasis | 31 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000342 (AUC rank 24/31): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001312 (AUC rank 15/31): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002083 (AUC rank 9/31): x5<br>PGS001312 (AUC rank 15/31): x5 |
| depressive disorder | 30 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000138 (AUC rank 22/30): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002036 (AUC rank 21/30): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004760 (AUC rank 1/30): x10 |
| hypothyroidism | 28 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000759 (AUC rank 19/28): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x8<br>PGS004790 (AUC rank 6/28): x2 |
| hodgkins lymphoma | 27 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000080 (AUC rank 17/27): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000637 (AUC rank 11/27): x10 |
| kidney failure | 27 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000708 (AUC rank 3/27): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000708 (AUC rank 3/27): x8<br>PGS004492 (AUC rank 4/27): x2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004562 (AUC rank 1/27): x7<br>PGS004492 (AUC rank 4/27): x3 |
| chronic kidney disease | 22 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000728 (AUC rank 19/22): x9<br>PGS004224 (AUC rank 14/22): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002237 (AUC rank 12/22): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004158 (AUC rank 3/22): x8<br>PGS002237 (AUC rank 12/22): x2 |
| basal cell carcinoma | 20 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000119 (AUC rank 13/20): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000452 (AUC rank 4/20): x7<br>PGS000119 (AUC rank 13/20): x3 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000452 (AUC rank 4/20): x9<br>PGS000447 (AUC rank 14/20): x1 |
| sleep apnea | 20 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003204 (AUC rank 17/20): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x9<br>PGS003213 (AUC rank 4/20): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x9<br>PGS005219 (AUC rank 2/20): x1 |
| urinary bladder cancer | 20 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000071 (AUC rank 4/20): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000071 (AUC rank 4/20): x5<br>PGS000723 (AUC rank 8/20): x2<br>PGS000611 (AUC rank 11/20): x2<br>PGS000613 (AUC rank 5/20): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004687 (AUC rank 6/20): x5<br>PGS000613 (AUC rank 5/20): x2<br>PGS000611 (AUC rank 11/20): x2<br>PGS000071 (AUC rank 4/20): x1 |
| angina pectoris | 19 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000703 (AUC rank 12/19): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001262 (AUC rank 15/19): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005052 (AUC rank 2/19): x9<br>PGS004457 (AUC rank 11/19): x1 |
| squamous cell carcinoma | 18 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000120 (AUC rank 10/18): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000731 (AUC rank 11/18): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000461 (AUC rank 5/18): x10 |
| uterine cancer | 18 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000073 (AUC rank 18/18): x9 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000541 (AUC rank 7/18): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001795 (AUC rank 13/18): x9<br>PGS003381 (AUC rank 3/18): x1 |
| retinopathy | 17 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000819 (AUC rank 10/17): x9<br>PGS002269 (AUC rank 2/17): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002027 (AUC rank 9/17): x8<br>PGS000819 (AUC rank 10/17): x2 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002027 (AUC rank 9/17): x8<br>PGS000819 (AUC rank 10/17): x2 |
| glaucoma | 15 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000137 (AUC rank 6/15): x9<br>PGS001836 (AUC rank 11/15): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000137 (AUC rank 6/15): x5<br>PGS001792 (AUC rank 5/15): x4<br>PGS004944 (AUC rank 4/15): x1 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004766 (AUC rank 3/15): x10 |
| lupus erythematosus | 13 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000196 (AUC rank 5/13): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001870 (AUC rank 9/13): x6<br>PGS003960 (AUC rank 11/13): x2<br>PGS000328 (AUC rank 6/13): x1<br>PGS002082 (AUC rank 10/13): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002082 (AUC rank 10/13): x7<br>PGS000328 (AUC rank 6/13): x2<br>PGS000754 (AUC rank 12/13): x1 |
| lymphoid leukemia | 13 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000077 (AUC rank 9/13): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000788 (AUC rank 4/13): x7<br>PGS000077 (AUC rank 9/13): x3 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000788 (AUC rank 4/13): x5<br>PGS000077 (AUC rank 9/13): x5 |
| osteoporosis | 13 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001273 (AUC rank 5/13): x10 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001273 (AUC rank 5/13): x6<br>PGS001274 (AUC rank 4/13): x4 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004810 (AUC rank 1/13): x10 |
| testicular carcinoma | 13 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000595 (AUC rank 12/13): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001164 (AUC rank 3/13): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000604 (AUC rank 9/13): x9<br>PGS000796 (AUC rank 1/13): x1 |
| parkinson disease | 11 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000056 (AUC rank 7/11): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000903 (AUC rank 1/11): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000903 (AUC rank 1/11): x10 |
| chronic obstructive pulmonary disease | 10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001326 (AUC rank 10/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001783 (AUC rank 1/10): x8<br>PGS002062 (AUC rank 4/10): x2 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001788 (AUC rank 3/10): x9<br>PGS002062 (AUC rank 4/10): x1 |
| kidney cancer | 10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000076 (AUC rank 7/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 |
| obesity | 10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10): x9<br>PGS002033 (AUC rank 4/10): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005235 (AUC rank 1/10): x10 |
| ankylosing spondylitis | 9 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001267 (AUC rank 2/9): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001268 (AUC rank 3/9): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002089 (AUC rank 4/9): x10 |
| aortic stenosis | 8 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000739 (AUC rank 7/8): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005252 (AUC rank 8/8): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005254 (AUC rank 1/8): x10 |
| dilated cardiomyopathy | 8 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004861 (AUC rank 8/8): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004861 (AUC rank 8/8): x8<br>PGS004862 (AUC rank 4/8): x2 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004862 (AUC rank 4/8): x9<br>PGS004951 (AUC rank 1/8): x1 |
| hip osteoarthritis | 7 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000967 (AUC rank 4/7): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000967 (AUC rank 4/7): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002763 (AUC rank 1/7): x6<br>PGS004882 (AUC rank 2/7): x2<br>PGS004478 (AUC rank 3/7): x2 |
| hyperthyroidism | 7 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001042 (AUC rank 5/7): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001043 (AUC rank 7/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x10 |
| knee osteoarthritis | 7 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001192 (AUC rank 5/7): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002729 (AUC rank 7/7): x9<br>PGS001192 (AUC rank 5/7): x1 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002767 (AUC rank 2/7): x5<br>PGS002729 (AUC rank 7/7): x4<br>PGS004479 (AUC rank 4/7): x1 |
| macular degeneration | 7 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001013 (AUC rank 6/7): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 3/7): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 3/7): x10 |
| nodular goiter | 7 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001814 (AUC rank 5/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 |
| pulmonary embolism | 7 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001277 (AUC rank 3/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001280 (AUC rank 2/7): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003861 (AUC rank 7/7): x6<br>PGS004460 (AUC rank 6/7): x4 |
| abdominal aortic aneurysm | 6 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000753 (AUC rank 5/6): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003973 (AUC rank 1/6): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003972 (AUC rank 3/6): x10 |
| atopic eczema | 6 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001773 (AUC rank 5/6): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002755 (AUC rank 4/6): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002755 (AUC rank 4/6): x10 |
| cervical carcinoma | 6 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000073 (AUC rank 1/6): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 6/6): x8<br>PGS003428 (AUC rank 5/6): x2 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS003428 (AUC rank 5/6): x10 |
| late-onset alzheimer's disease | 5 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000053 (AUC rank 5/5): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000334 (AUC rank 3/5): x8<br>PGS000053 (AUC rank 5/5): x2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000054 (AUC rank 1/5): x10 |
| urolithiasis | 5 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001250 (AUC rank 3/5): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001250 (AUC rank 3/5): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004493 (AUC rank 2/5): x10 |
| alcohol dependence | 4 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000201 (AUC rank 2/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x10 |
| atrial flutter | 4 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001263 (AUC rank 4/4): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001263 (AUC rank 4/4): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001263 (AUC rank 4/4): x10 |
| hypertrophic cardiomyopathy | 4 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000739 (AUC rank 2/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x10 |
| juvenile idiopathic arthritis | 4 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 |
| peripheral vascular disease | 4 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001843 (AUC rank 4/4): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002055 (AUC rank 2/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005217 (AUC rank 1/4): x10 |
| psoriatic arthritis | 4 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000342 (AUC rank 2/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001287 (AUC rank 1/4): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000342 (AUC rank 2/4): x10 |
| sarcoidosis | 4 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000922 (AUC rank 2/4): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000922 (AUC rank 2/4): x6<br>PGS000923 (AUC rank 3/4): x4 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000922 (AUC rank 2/4): x9<br>PGS001872 (AUC rank 1/4): x1 |
| bilirubin metabolism disease | 3 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000924 (AUC rank 3/3): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000924 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002032 (AUC rank 2/3): x10 |
| bipolar disorder | 3 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002786 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002786 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002786 (AUC rank 1/3): x10 |
| blood coagulation disease | 3 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001033 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001033 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001033 (AUC rank 1/3): x7<br>PGS002034 (AUC rank 2/3): x3 |
| dupuytren contracture | 3 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001254 (AUC rank 3/3): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001254 (AUC rank 3/3): x9<br>PGS002092 (AUC rank 1/3): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002092 (AUC rank 1/3): x10 |
| hashimoto's thyroiditis | 3 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005270 (AUC rank 3/3): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005270 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005271 (AUC rank 2/3): x10 |
| preeclampsia | 3 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 |
| pulmonary fibrosis | 3 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001030 (AUC rank 3/3): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001030 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001791 (AUC rank 2/3): x8<br>PGS004695 (AUC rank 1/3): x2 |
| skin carcinoma in situ | 3 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000469 (AUC rank 3/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x8<br>PGS000469 (AUC rank 3/3): x2 |
| vitiligo | 3 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000738 (AUC rank 2/3): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001536 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000738 (AUC rank 2/3): x10 |
| autism spectrum disorder | 2 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000327 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000327 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000327 (AUC rank 2/2): x10 |
| congenital vitamin k-dependent coagulation factors deficiency | 2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001826 (AUC rank 1/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002034 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002034 (AUC rank 2/2): x10 |
| corneal dystrophy | 2 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001835 (AUC rank 2/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002042 (AUC rank 1/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002042 (AUC rank 1/2): x10 |
| iron metabolism disease | 2 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001823 (AUC rank 2/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002031 (AUC rank 1/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002031 (AUC rank 1/2): x10 |
| nasal cavity polyp | 2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004465 (AUC rank 1/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004535 (AUC rank 2/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004465 (AUC rank 1/2): x10 |
| nicotine dependence | 2 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001830 (AUC rank 2/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002037 (AUC rank 1/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002037 (AUC rank 1/2): x10 |
| otosclerosis | 2 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001255 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001255 (AUC rank 2/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002046 (AUC rank 1/2): x10 |