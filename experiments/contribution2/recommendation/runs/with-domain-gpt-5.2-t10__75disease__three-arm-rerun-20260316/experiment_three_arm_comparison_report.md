# Contribution2 Three-Arm Comparison

## Summary

- **Model**: gpt-5.2
- **Diseases**: 75
- **Trials per disease**: 10
- **Union CSV**: `experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_current_union__75disease.csv`

## High-Level Outcome

- Prompt-Only Baseline `Hit@1`: `0/75 = 0.00%`; `trial_hits = 0/750 = 0.00%`
- Prompt-Only Baseline `Hit@2`: `0/75 = 0.00%`; `trial_hits = 0/750 = 0.00%`
- Prompt-Only Baseline `Hit@3`: `0/75 = 0.00%`; `trial_hits = 0/750 = 0.00%`
- Prompt-Only Baseline `Hit@4`: `0/75 = 0.00%`; `trial_hits = 0/750 = 0.00%`
- Prompt-Only Baseline `Hit@5`: `0/75 = 0.00%`; `trial_hits = 0/750 = 0.00%`
- Catalog Search Only `Hit@1`: `18/75 = 24.00%`; `trial_hits = 178/750 = 23.73%`
- Catalog Search Only `Hit@2`: `28/75 = 37.33%`; `trial_hits = 270/750 = 36.00%`
- Catalog Search Only `Hit@3`: `42/75 = 56.00%`; `trial_hits = 406/750 = 54.13%`
- Catalog Search Only `Hit@4`: `47/75 = 62.67%`; `trial_hits = 462/750 = 61.60%`
- Catalog Search Only `Hit@5`: `48/75 = 64.00%`; `trial_hits = 479/750 = 63.87%`
- Catalog Search + Domain Knowledge `Hit@1`: `26/75 = 34.67%`; `trial_hits = 269/750 = 35.87%`
- Catalog Search + Domain Knowledge `Hit@2`: `40/75 = 53.33%`; `trial_hits = 406/750 = 54.13%`
- Catalog Search + Domain Knowledge `Hit@3`: `47/75 = 62.67%`; `trial_hits = 471/750 = 62.80%`
- Catalog Search + Domain Knowledge `Hit@4`: `53/75 = 70.67%`; `trial_hits = 538/750 = 71.73%`
- Catalog Search + Domain Knowledge `Hit@5`: `56/75 = 74.67%`; `trial_hits = 560/750 = 74.67%`

- **Prompt-Only Baseline valid output rate**: `0/750 = 0.00%`
- **Catalog Search Only valid output rate**: `750/750 = 100.00%`
- **Catalog Search + Domain Knowledge valid output rate**: `750/750 = 100.00%`

## Percentile Hit

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.
- For each percentile threshold, define the tie-aware cutoff rank as `c_q = max(1, ceil(q/100 * M))`.
- A selection counts as `Top q% Hit` if its AoU benchmark rank satisfies `r <= c_q`.
- Denominator: fixed total disease count for modal selections and fixed total trial count for trial selections.
- Tie handling: if the AoU benchmark AUC is tied at cutoff rank `c_q`, all tied models count as `Top q%`.

- Prompt-Only Baseline `Top 5% Hit`: `0/75 = 0.00%`; `trial_hits = 0/750 = 0.00%`
- Prompt-Only Baseline `Top 10% Hit`: `0/75 = 0.00%`; `trial_hits = 0/750 = 0.00%`
- Prompt-Only Baseline `Top 15% Hit`: `0/75 = 0.00%`; `trial_hits = 0/750 = 0.00%`
- Prompt-Only Baseline `Top 20% Hit`: `0/75 = 0.00%`; `trial_hits = 0/750 = 0.00%`
- Prompt-Only Baseline `Top 25% Hit`: `0/75 = 0.00%`; `trial_hits = 0/750 = 0.00%`
- Catalog Search Only `Top 5% Hit`: `22/75 = 29.33%`; `trial_hits = 210/750 = 28.00%`
- Catalog Search Only `Top 10% Hit`: `25/75 = 33.33%`; `trial_hits = 244/750 = 32.53%`
- Catalog Search Only `Top 15% Hit`: `29/75 = 38.67%`; `trial_hits = 284/750 = 37.87%`
- Catalog Search Only `Top 20% Hit`: `31/75 = 41.33%`; `trial_hits = 307/750 = 40.93%`
- Catalog Search Only `Top 25% Hit`: `35/75 = 46.67%`; `trial_hits = 346/750 = 46.13%`
- Catalog Search + Domain Knowledge `Top 5% Hit`: `31/75 = 41.33%`; `trial_hits = 320/750 = 42.67%`
- Catalog Search + Domain Knowledge `Top 10% Hit`: `35/75 = 46.67%`; `trial_hits = 357/750 = 47.60%`
- Catalog Search + Domain Knowledge `Top 15% Hit`: `41/75 = 54.67%`; `trial_hits = 411/750 = 54.80%`
- Catalog Search + Domain Knowledge `Top 20% Hit`: `42/75 = 56.00%`; `trial_hits = 428/750 = 57.07%`
- Catalog Search + Domain Knowledge `Top 25% Hit`: `46/75 = 61.33%`; `trial_hits = 463/750 = 61.73%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Prompt-Only Baseline: `mean r / M = N/A` (0 modal selections); `trial mean r / M = N/A` (0 trials)
- Catalog Search Only: `mean r / M = 0.4989` (75 modal selections); `trial mean r / M = 0.5071` (750 trials)
- Catalog Search + Domain Knowledge: `mean r / M = 0.4102` (75 modal selections); `trial mean r / M = 0.4044` (750 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Prompt-Only Baseline: `mean (M - r) / M = N/A` (0 modal selections); `trial mean (M - r) / M = N/A` (0 trials)
- Catalog Search Only: `mean (M - r) / M = 0.5011` (75 modal selections); `trial mean (M - r) / M = 0.4929` (750 trials)
- Catalog Search + Domain Knowledge: `mean (M - r) / M = 0.5898` (75 modal selections); `trial mean (M - r) / M = 0.5956` (750 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Prompt-Only Baseline: `mean NRS = N/A` (0 modal selections); `trial mean NRS = N/A` (0 trials)
- Catalog Search Only: `mean NRS = 0.5860` (75 modal selections); `trial mean NRS = 0.5771` (750 trials)
- Catalog Search + Domain Knowledge: `mean NRS = 0.6977` (75 modal selections); `trial mean NRS = 0.7062` (750 trials)


## Results by Disease

| Ontology | N Models | Prompt-Only Baseline Hit@1..5 | Prompt-Only Baseline | Catalog Search Only Hit@1..5 | Catalog Search Only | Catalog Search + Domain Knowledge Hit@1..5 | Catalog Search + Domain Knowledge |
|----------|----------|------------------------------|------------------------|---------------------------|----------------------|--------------------------------------|------------------------------------|
| hypertension | 258 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001320 (AUC rank 12/258): x5<br>PGS004236 (AUC rank 40/258): x5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001320 (AUC rank 12/258): x8<br>PGS004236 (AUC rank 40/258): x2 |
| breast carcinoma | 164 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000007 (AUC rank 42/164): x7<br>PGS000015 (AUC rank 31/164): x2<br>PGS004153 (AUC rank 6/164): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004153 (AUC rank 6/164): x9<br>PGS000015 (AUC rank 31/164): x1 |
| arthritis | 107 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001135 (AUC rank 15/107): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001135 (AUC rank 15/107): x10 |
| melanoma | 103 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000743 (AUC rank 11/103): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000790 (AUC rank 24/103): x5<br>PGS002247 (AUC rank 4/103): x3<br>PGS000743 (AUC rank 11/103): x1<br>PGS000079 (AUC rank 22/103): x1 |
| prostate cancer | 96 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005238 (AUC rank 51/96): x9<br>PGS000662 (AUC rank 77/96): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004155 (AUC rank 30/96): x9<br>PGS003415 (AUC rank 79/96): x1 |
| coronary artery disease | 85 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003725 (AUC rank 2/85): x8<br>PGS002244 (AUC rank 37/85): x2 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003725 (AUC rank 2/85): x9<br>PGS002244 (AUC rank 37/85): x1 |
| asthma | 66 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001344 (AUC rank 16/66): x5<br>PGS001787 (AUC rank 6/66): x4<br>PGS002727 (AUC rank 41/66): x1 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001782 (AUC rank 5/66): x6<br>PGS002061 (AUC rank 15/66): x2<br>PGS005134 (AUC rank 11/66): x1<br>PGS001344 (AUC rank 16/66): x1 |
| dementia | 65 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005170 (AUC rank 2/65): x8<br>PGS004281 (AUC rank 7/65): x1<br>PGS000929 (AUC rank 14/65): x1 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005170 (AUC rank 2/65): x10 |
| gout | 63 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001789 (AUC rank 15/63): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001789 (AUC rank 15/63): x10 |
| atrial fibrillation | 61 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005168 (AUC rank 52/61): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005313 (AUC rank 1/61): x5<br>PGS005168 (AUC rank 52/61): x5 |
| rheumatoid arthritis | 48 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004163 (AUC rank 3/48): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002745 (AUC rank 17/48): x7<br>PGS004163 (AUC rank 3/48): x3 |
| ovarian neoplasm | 42 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000549 (AUC rank 18/42): x5<br>PGS000550 (AUC rank 34/42): x5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000550 (AUC rank 34/42): x10 |
| lung cancer | 35 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004860 (AUC rank 1/35): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000078 (AUC rank 18/35): x8<br>PGS004860 (AUC rank 1/35): x2 |
| myocardial infarction | 35 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001314 (AUC rank 21/35): x7<br>PGS001315 (AUC rank 18/35): x3 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005039 (AUC rank 2/35): x9<br>PGS001315 (AUC rank 18/35): x1 |
| heart failure | 34 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001790 (AUC rank 11/34): x8<br>PGS005077 (AUC rank 4/34): x1<br>PGS005083 (AUC rank 5/34): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005097 (AUC rank 1/34): x10 |
| thyroid carcinoma | 32 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000208 (AUC rank 16/32): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS005259 (AUC rank 4/32): x10 |
| psoriasis | 31 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001312 (AUC rank 15/31): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001312 (AUC rank 15/31): x10 |
| depressive disorder | 30 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002036 (AUC rank 21/30): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002036 (AUC rank 21/30): x10 |
| hypothyroidism | 28 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005268 (AUC rank 1/28): x6<br>PGS005218 (AUC rank 3/28): x4 |
| hodgkins lymphoma | 27 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 |
| kidney failure | 27 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000708 (AUC rank 3/27): x8<br>PGS004492 (AUC rank 4/27): x2 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000708 (AUC rank 3/27): x6<br>PGS004562 (AUC rank 1/27): x2<br>PGS004492 (AUC rank 4/27): x2 |
| chronic kidney disease | 22 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002237 (AUC rank 12/22): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004158 (AUC rank 3/22): x10 |
| basal cell carcinoma | 20 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000452 (AUC rank 4/20): x7<br>PGS000119 (AUC rank 13/20): x3 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000452 (AUC rank 4/20): x5<br>PGS000119 (AUC rank 13/20): x3<br>PGS000448 (AUC rank 15/20): x2 |
| sleep apnea | 20 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x9<br>PGS003213 (AUC rank 4/20): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 |
| urinary bladder cancer | 20 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000071 (AUC rank 4/20): x5<br>PGS000723 (AUC rank 8/20): x2<br>PGS000611 (AUC rank 11/20): x2<br>PGS000613 (AUC rank 5/20): x1 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000613 (AUC rank 5/20): x5<br>PGS000611 (AUC rank 11/20): x3<br>PGS000071 (AUC rank 4/20): x2 |
| angina pectoris | 19 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001262 (AUC rank 15/19): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001262 (AUC rank 15/19): x8<br>PGS005048 (AUC rank 7/19): x2 |
| squamous cell carcinoma | 18 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000731 (AUC rank 11/18): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000461 (AUC rank 5/18): x10 |
| uterine cancer | 18 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000541 (AUC rank 7/18): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003381 (AUC rank 3/18): x10 |
| retinopathy | 17 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002027 (AUC rank 9/17): x8<br>PGS000819 (AUC rank 10/17): x2 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002027 (AUC rank 9/17): x7<br>PGS000819 (AUC rank 10/17): x3 |
| glaucoma | 15 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000137 (AUC rank 6/15): x5<br>PGS001792 (AUC rank 5/15): x4<br>PGS004944 (AUC rank 4/15): x1 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004944 (AUC rank 4/15): x9<br>PGS001792 (AUC rank 5/15): x1 |
| lupus erythematosus | 13 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001870 (AUC rank 9/13): x6<br>PGS003960 (AUC rank 11/13): x2<br>PGS000328 (AUC rank 6/13): x1<br>PGS002082 (AUC rank 10/13): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000328 (AUC rank 6/13): x7<br>PGS004917 (AUC rank 4/13): x1<br>PGS001870 (AUC rank 9/13): x1<br>PGS000754 (AUC rank 12/13): x1 |
| lymphoid leukemia | 13 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000788 (AUC rank 4/13): x7<br>PGS000077 (AUC rank 9/13): x3 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000077 (AUC rank 9/13): x10 |
| osteoporosis | 13 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001273 (AUC rank 5/13): x6<br>PGS001274 (AUC rank 4/13): x4 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004810 (AUC rank 1/13): x10 |
| testicular carcinoma | 13 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001164 (AUC rank 3/13): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000604 (AUC rank 9/13): x10 |
| parkinson disease | 11 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000903 (AUC rank 1/11): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000903 (AUC rank 1/11): x10 |
| chronic obstructive pulmonary disease | 10 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001783 (AUC rank 1/10): x8<br>PGS002062 (AUC rank 4/10): x2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001783 (AUC rank 1/10): x10 |
| kidney cancer | 10 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 |
| obesity | 10 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10): x9<br>PGS002033 (AUC rank 4/10): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005235 (AUC rank 1/10): x10 |
| ankylosing spondylitis | 9 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001268 (AUC rank 3/9): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001267 (AUC rank 2/9): x6<br>PGS001268 (AUC rank 3/9): x2<br>PGS002089 (AUC rank 4/9): x2 |
| aortic stenosis | 8 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005252 (AUC rank 8/8): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005254 (AUC rank 1/8): x10 |
| dilated cardiomyopathy | 8 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004861 (AUC rank 8/8): x8<br>PGS004862 (AUC rank 4/8): x2 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004861 (AUC rank 8/8): x10 |
| hip osteoarthritis | 7 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000967 (AUC rank 4/7): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002763 (AUC rank 1/7): x10 |
| hyperthyroidism | 7 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001043 (AUC rank 7/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x10 |
| knee osteoarthritis | 7 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002729 (AUC rank 7/7): x9<br>PGS001192 (AUC rank 5/7): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002729 (AUC rank 7/7): x9<br>PGS002767 (AUC rank 2/7): x1 |
| macular degeneration | 7 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 3/7): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 3/7): x10 |
| nodular goiter | 7 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 |
| pulmonary embolism | 7 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001280 (AUC rank 2/7): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001279 (AUC rank 4/7): x9<br>PGS003861 (AUC rank 7/7): x1 |
| abdominal aortic aneurysm | 6 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003973 (AUC rank 1/6): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003972 (AUC rank 3/6): x10 |
| atopic eczema | 6 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002755 (AUC rank 4/6): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002755 (AUC rank 4/6): x9<br>PGS004587 (AUC rank 2/6): x1 |
| cervical carcinoma | 6 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 6/6): x8<br>PGS003428 (AUC rank 5/6): x2 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS003428 (AUC rank 5/6): x10 |
| late-onset alzheimer's disease | 5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000334 (AUC rank 3/5): x8<br>PGS000053 (AUC rank 5/5): x2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000054 (AUC rank 1/5): x10 |
| urolithiasis | 5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001250 (AUC rank 3/5): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004563 (AUC rank 1/5): x10 |
| alcohol dependence | 4 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x10 |
| atrial flutter | 4 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001263 (AUC rank 4/4): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001263 (AUC rank 4/4): x10 |
| hypertrophic cardiomyopathy | 4 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x10 |
| juvenile idiopathic arthritis | 4 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x10 |
| peripheral vascular disease | 4 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002055 (AUC rank 2/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005217 (AUC rank 1/4): x10 |
| psoriatic arthritis | 4 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001287 (AUC rank 1/4): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000342 (AUC rank 2/4): x6<br>PGS001287 (AUC rank 1/4): x4 |
| sarcoidosis | 4 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000922 (AUC rank 2/4): x6<br>PGS000923 (AUC rank 3/4): x4 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000922 (AUC rank 2/4): x10 |
| bilirubin metabolism disease | 3 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000924 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002032 (AUC rank 2/3): x8<br>PGS001824 (AUC rank 1/3): x2 |
| bipolar disorder | 3 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002786 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002786 (AUC rank 1/3): x10 |
| blood coagulation disease | 3 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001033 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001033 (AUC rank 1/3): x10 |
| dupuytren contracture | 3 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001254 (AUC rank 3/3): x9<br>PGS002092 (AUC rank 1/3): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002092 (AUC rank 1/3): x10 |
| hashimoto's thyroiditis | 3 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005270 (AUC rank 3/3): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005271 (AUC rank 2/3): x5<br>PGS005270 (AUC rank 3/3): x5 |
| preeclampsia | 3 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x10 |
| pulmonary fibrosis | 3 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001030 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001791 (AUC rank 2/3): x10 |
| skin carcinoma in situ | 3 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x10 |
| vitiligo | 3 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001536 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000738 (AUC rank 2/3): x10 |
| autism spectrum disorder | 2 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000327 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000327 (AUC rank 2/2): x10 |
| congenital vitamin k-dependent coagulation factors deficiency | 2 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002034 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002034 (AUC rank 2/2): x10 |
| corneal dystrophy | 2 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002042 (AUC rank 1/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002042 (AUC rank 1/2): x10 |
| iron metabolism disease | 2 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002031 (AUC rank 1/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002031 (AUC rank 1/2): x10 |
| nasal cavity polyp | 2 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004535 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004535 (AUC rank 2/2): x10 |
| nicotine dependence | 2 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002037 (AUC rank 1/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002037 (AUC rank 1/2): x10 |
| otosclerosis | 2 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001255 (AUC rank 2/2): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002046 (AUC rank 1/2): x8<br>PGS001255 (AUC rank 2/2): x2 |