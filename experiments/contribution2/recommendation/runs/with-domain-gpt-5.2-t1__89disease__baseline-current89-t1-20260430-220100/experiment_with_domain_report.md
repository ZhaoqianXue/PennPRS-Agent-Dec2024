# Contribution2 Experiment 2: Catalog Search Only

## Summary

- **Diseases**: 89
- **Trials per disease**: 1
- **Total trials**: 89
- **Model**: gpt-5.2
- **Estimated API cost**: $0.0000 (uncached input 0 tokens = $0.0000; cached input 0 tokens = $0.0000; output 0 tokens = $0.0000)

## High-Level Outcome

- Catalog Search Only `Hit@1`: `29/89 = 32.58%`; `trial_hits = 29/89 = 32.58%`
- Catalog Search Only `Hit@2`: `48/89 = 53.93%`; `trial_hits = 48/89 = 53.93%`
- Catalog Search Only `Hit@3`: `57/89 = 64.04%`; `trial_hits = 57/89 = 64.04%`
- Catalog Search Only `Hit@4`: `62/89 = 69.66%`; `trial_hits = 62/89 = 69.66%`
- Catalog Search Only `Hit@5`: `66/89 = 74.16%`; `trial_hits = 66/89 = 74.16%`

## Percentile Hit

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.
- For each percentile threshold, define the tie-aware cutoff rank as `c_q = max(1, ceil(q/100 * M))`.
- A selection counts as `Top q% Hit` if its AoU benchmark rank satisfies `r <= c_q`.
- Denominator: fixed total disease count for modal selections and fixed total trial count for trial selections.
- Tie handling: if the AoU benchmark AUC is tied at cutoff rank `c_q`, all tied models count as `Top q%`.

- Catalog Search Only `Top 5% Hit`: `36/89 = 40.45%`; `trial_hits = 36/89 = 40.45%`
- Catalog Search Only `Top 10% Hit`: `38/89 = 42.70%`; `trial_hits = 38/89 = 42.70%`
- Catalog Search Only `Top 15% Hit`: `46/89 = 51.69%`; `trial_hits = 46/89 = 51.69%`
- Catalog Search Only `Top 20% Hit`: `50/89 = 56.18%`; `trial_hits = 50/89 = 56.18%`
- Catalog Search Only `Top 25% Hit`: `52/89 = 58.43%`; `trial_hits = 52/89 = 58.43%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Catalog Search Only: `mean r / M = 0.4062` (88 modal selections); `trial mean r / M = 0.4062` (88 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Catalog Search Only: `mean (M - r) / M = 0.5938` (88 modal selections); `trial mean (M - r) / M = 0.5938` (88 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Catalog Search Only: `mean NRS = 0.7070` (88 modal selections); `trial mean NRS = 0.7070` (88 trials)


## Experiment Setup

- **Step 1 tools**: prs_model_pgscatalog_search
- **Domain Knowledge**: Disabled
- **Candidate pool**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us
- **Success rule**: report `Hit@k` for `k = 1..5` against the AoU benchmark ranking using the full disease/trial denominator; if a disease has fewer than `k` evaluated models, `Top@k` includes all available benchmark-ranked models
- **Benchmark tie handling**: if the AoU benchmark AUC is tied at the `k`-th cutoff, all tied models count as `Top@k`

## Results by Disease

All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.
They are **not** PGS Catalog reported-AUC ranks.

| Ontology | N Models | Trial Hit@1..5 | Catalog Search Only Hit@1..5 | Catalog Search Only |
|----------|----------|---------------|-------------------------------------|--------------------------|
| hypertension | 258 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004236 (AUC rank 40/258): x1 |
| type 2 diabetes mellitus | 209 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002308 (AUC rank 22/209): x1 |
| breast carcinoma | 164 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004153 (AUC rank 6/164): x1 |
| arthritis | 107 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001135 (AUC rank 15/107): x1 |
| melanoma | 103 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002247 (AUC rank 4/103): x1 |
| prostate cancer | 96 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004155 (AUC rank 30/96): x1 |
| coronary artery disease | 85 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003725 (AUC rank 2/85): x1 |
| asthma | 66 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002727 (AUC rank 41/66): x1 |
| dementia | 65 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005170 (AUC rank 2/65): x1 |
| gout | 63 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001248 (AUC rank 20/63): x1 |
| atrial fibrillation | 61 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005168 (AUC rank 52/61): x1 |
| rheumatoid arthritis | 48 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004163 (AUC rank 3/48): x1 |
| ovarian neoplasm | 42 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000549 (AUC rank 18/42): x1 |
| lung cancer | 35 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000078 (AUC rank 18/35): x1 |
| myocardial infarction | 35 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005039 (AUC rank 2/35): x1 |
| heart failure | 34 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005097 (AUC rank 1/34): x1 |
| type 1 diabetes mellitus | 33 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000024 (AUC rank 23/33): x1 |
| thyroid carcinoma | 32 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000208 (AUC rank 16/32): x1 |
| psoriasis | 31 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001312 (AUC rank 15/31): x1 |
| depressive disorder | 30 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003333 (AUC rank 2/30): x1 |
| hypothyroidism | 28 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x1 |
| hodgkins lymphoma | 27 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x1 |
| kidney failure | 27 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000708 (AUC rank 3/27): x1 |
| chronic kidney disease | 22 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002237 (AUC rank 12/22): x1 |
| basal cell carcinoma | 20 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000454 (AUC rank 6/20): x1 |
| sleep apnea | 20 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x1 |
| urinary bladder cancer | 20 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000613 (AUC rank 5/20): x1 |
| angina pectoris | 19 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001262 (AUC rank 15/19): x1 |
| squamous cell carcinoma | 18 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS000461 (AUC rank 5/18): x1 |
| uterine cancer | 18 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003381 (AUC rank 3/18): x1 |
| glaucoma | 15 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001792 (AUC rank 5/15): x1 |
| lupus erythematosus | 13 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000328 (AUC rank 6/13): x1 |
| lymphoid leukemia | 13 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000077 (AUC rank 9/13): x1 |
| osteoporosis | 13 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS002768 (AUC rank 3/13): x1 |
| testicular carcinoma | 13 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | - |
| celiac disease | 11 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001301 (AUC rank 7/11): x1 |
| pancreatic carcinoma | 11 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000083 (AUC rank 3/11): x1 |
| parkinson disease | 11 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000903 (AUC rank 1/11): x1 |
| chronic obstructive pulmonary disease | 10 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001783 (AUC rank 1/10): x1 |
| kidney cancer | 10 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x1 |
| obesity | 10 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005235 (AUC rank 1/10): x1 |
| ankylosing spondylitis | 9 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001267 (AUC rank 2/9): x1 |
| aortic stenosis | 8 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005252 (AUC rank 8/8): x1 |
| dilated cardiomyopathy | 8 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004951 (AUC rank 1/8): x1 |
| multiple sclerosis | 8 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001270 (AUC rank 7/8): x1 |
| hip osteoarthritis | 7 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002763 (AUC rank 1/7): x1 |
| hyperthyroidism | 7 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x1 |
| knee osteoarthritis | 7 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002767 (AUC rank 2/7): x1 |
| macular degeneration | 7 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 3/7): x1 |
| nodular goiter | 7 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x1 |
| pulmonary embolism | 7 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001280 (AUC rank 2/7): x1 |
| abdominal aortic aneurysm | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS000753 (AUC rank 5/6): x1 |
| atopic eczema | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002755 (AUC rank 4/6): x1 |
| cervical carcinoma | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS003428 (AUC rank 5/6): x1 |
| cholelithiasis | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001174 (AUC rank 4/6): x1 |
| cirrhosis of liver | 6 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004621 (AUC rank 1/6): x1 |
| multiple myeloma | 6 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002281 (AUC rank 6/6): x1 |
| diverticular disease | 5 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000997 (AUC rank 2/5): x1 |
| late-onset alzheimer's disease | 5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000054 (AUC rank 1/5): x1 |
| schizophrenia | 5 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000136 (AUC rank 3/5): x1 |
| ulcerative colitis | 5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004253 (AUC rank 1/5): x1 |
| urolithiasis | 5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002075 (AUC rank 1/5): x1 |
| alcohol dependence | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002738 (AUC rank 1/4): x1 |
| atrial flutter | 4 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001263 (AUC rank 4/4): x1 |
| follicular lymphoma | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002304 (AUC rank 1/4): x1 |
| hypertrophic cardiomyopathy | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004911 (AUC rank 1/4): x1 |
| juvenile idiopathic arthritis | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000114 (AUC rank 1/4): x1 |
| peripheral vascular disease | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005217 (AUC rank 1/4): x1 |
| psoriatic arthritis | 4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001287 (AUC rank 1/4): x1 |
| retinal detachment | 4 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001137 (AUC rank 2/4): x1 |
| sarcoidosis | 4 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000922 (AUC rank 3/4): x1 |
| alcoholic liver cirrhosis | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004913 (AUC rank 1/3): x1 |
| bilirubin metabolism disease | 3 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002032 (AUC rank 2/3): x1 |
| bipolar disorder | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002786 (AUC rank 1/3): x1 |
| blood coagulation disease | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001033 (AUC rank 1/3): x1 |
| crohn's disease | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004254 (AUC rank 1/3): x1 |
| dupuytren contracture | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002092 (AUC rank 1/3): x1 |
| hashimoto's thyroiditis | 3 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005271 (AUC rank 2/3): x1 |
| preeclampsia | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003586 (AUC rank 1/3): x1 |
| pulmonary fibrosis | 3 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001791 (AUC rank 2/3): x1 |
| skin carcinoma in situ | 3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000471 (AUC rank 1/3): x1 |
| vitiligo | 3 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000738 (AUC rank 2/3): x1 |
| autism spectrum disorder | 2 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000327 (AUC rank 2/2): x1 |
| congenital vitamin k-dependent coagulation factors deficiency | 2 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002034 (AUC rank 2/2): x1 |
| corneal dystrophy | 2 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002042 (AUC rank 1/2): x1 |
| iron metabolism disease | 2 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002031 (AUC rank 1/2): x1 |
| nasal cavity polyp | 2 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004535 (AUC rank 2/2): x1 |
| nicotine dependence | 2 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002037 (AUC rank 1/2): x1 |
| otosclerosis | 2 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001255 (AUC rank 2/2): x1 |