# Contribution2 Experiment 2: With Domain Knowledge

## Summary

- **Diseases**: 60
- **Trials per disease**: 10
- **Total trials**: 600
- **Model**: gpt-5.2
- **Estimated API cost**: $3.8559 (uncached input 2,854,992 tokens = $2.4981; cached input 945,408 tokens = $0.0827; output 182,156 tokens = $1.2751)
- **With Domain Modal Hit@1**: 21/60 = 35.00%; `trial_hits = 216/600 = 36.00%`
- **With Domain Modal Hit@2**: 34/60 = 56.67%; `trial_hits = 340/600 = 56.67%`
- **With Domain Modal Hit@3**: 32/54 = 59.26%; `trial_hits = 321/540 = 59.44%`
- **With Domain Modal Hit@4**: 31/48 = 64.58%; `trial_hits = 305/480 = 63.54%`
- **With Domain Modal Hit@5**: 28/43 = 65.12%; `trial_hits = 281/430 = 65.35%`
- **Without Domain Modal Hit@1**: 16/60 = 26.67%; `trial_hits = 157/600 = 26.17%`
- **Without Domain Modal Hit@2**: 23/60 = 38.33%; `trial_hits = 224/600 = 37.33%`
- **Without Domain Modal Hit@3**: 24/54 = 44.44%; `trial_hits = 231/540 = 42.78%`
- **Without Domain Modal Hit@4**: 22/48 = 45.83%; `trial_hits = 218/480 = 45.42%`
- **Without Domain Modal Hit@5**: 20/43 = 46.51%; `trial_hits = 192/430 = 44.65%`

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`, with `r = 1` as best and `r = M` as worst.
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- With Domain Knowledge: `mean NRS = 0.7387` (60 modal selections); `trial mean NRS = 0.7395` (600 trials)
- Without Domain Knowledge: `mean NRS = 0.5873` (60 modal selections); `trial mean NRS = 0.5807` (600 trials)

## Experiment Setup

- **Step 1 tools**: prs_model_pgscatalog_search + prs_model_domain_knowledge + prs_model_performance_landscape
- **Domain Knowledge**: Enabled (local curated knowledge base)
- **Candidate pool**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us
- **Success rule**: report `Hit@k` for `k = 1..5` against the AoU benchmark ranking; diseases with fewer than `k` evaluated models are excluded from the `Hit@k` denominator
- **Benchmark tie handling**: if the AoU benchmark AUC is tied at the `k`-th cutoff, all tied models count as `Top@k`
- **Without Domain Knowledge reference**: compare against `without-domain-gpt-5.2-t10` under the same 30-disease / 10-trial protocol

## Results by Disease

All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.
They are **not** PGS Catalog reported-AUC ranks.

| Ontology | N Models | Eligible Ks | Trial Hit@1..5 | With Domain Knowledge Hit@1..5 | With Domain Knowledge | Without Domain Knowledge Hit@1..5 | Without Domain Knowledge |
|----------|----------|-------------|---------------|----------------------------------|-----------------------|-------------------------------------|--------------------------|
| hypertension | 258 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001320 (AUC rank 12/258): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001320 (AUC rank 12/258): x5<br>PGS004236 (AUC rank 40/258): x5 |
| breast carcinoma | 164 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004153 (AUC rank 6/164): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004153 (AUC rank 6/164): x7<br>PGS000007 (AUC rank 42/164): x2<br>PGS000015 (AUC rank 31/164): x1 |
| melanoma | 103 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:40.00%, 5:40.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS002247 (AUC rank 4/103): x4<br>PGS000079 (AUC rank 22/103): x3<br>PGS000790 (AUC rank 24/103): x3 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000079 (AUC rank 22/103): x5<br>PGS000743 (AUC rank 11/103): x3<br>PGS000813 (AUC rank 14/103): x2 |
| prostate cancer | 96 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS004155 (AUC rank 30/96): x4<br>PGS005238 (AUC rank 51/96): x3<br>PGS000582 (AUC rank 92/96): x2<br>PGS004042 (AUC rank 43/96): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005238 (AUC rank 51/96): x10 |
| coronary artery disease | 85 | 1,2,3,4,5 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003725 (AUC rank 2/85): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001780 (AUC rank 30/85): x3<br>PGS000013 (AUC rank 31/85): x3<br>PGS000018 (AUC rank 33/85): x3<br>PGS003725 (AUC rank 2/85): x1 |
| asthma | 66 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:20.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002727 (AUC rank 41/66): x7<br>PGS001782 (AUC rank 5/66): x2<br>PGS005134 (AUC rank 11/66): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002727 (AUC rank 41/66): x5<br>PGS001344 (AUC rank 16/66): x3<br>PGS001787 (AUC rank 6/66): x2 |
| gout | 63 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:10.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001789 (AUC rank 15/63): x9<br>PGS004047 (AUC rank 5/63): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001789 (AUC rank 15/63): x9<br>PGS004160 (AUC rank 2/63): x1 |
| atrial fibrillation | 61 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005168 (AUC rank 52/61): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005168 (AUC rank 52/61): x10 |
| rheumatoid arthritis | 48 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004163 (AUC rank 3/48): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004163 (AUC rank 3/48): x10 |
| lung cancer | 35 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000078 (AUC rank 18/35): x9<br>PGS000789 (AUC rank 17/35): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004860 (AUC rank 1/35): x9<br>PGS000789 (AUC rank 17/35): x1 |
| myocardial infarction | 35 | 1,2,3,4,5 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005039 (AUC rank 2/35): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005039 (AUC rank 2/35): x7<br>PGS001314 (AUC rank 21/35): x3 |
| heart failure | 34 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005097 (AUC rank 1/34): x10 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS005083 (AUC rank 5/34): x6<br>PGS001790 (AUC rank 11/34): x4 |
| thyroid carcinoma | 32 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:20.00%, 5:20.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000208 (AUC rank 16/32): x8<br>PGS005259 (AUC rank 4/32): x2 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000208 (AUC rank 16/32): x10 |
| psoriasis | 31 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001312 (AUC rank 15/31): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001312 (AUC rank 15/31): x10 |
| hypothyroidism | 28 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:90.00%, 4:90.00%, 5:90.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x9<br>PGS004935 (AUC rank 15/28): x1 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x9<br>PGS000965 (AUC rank 13/28): x1 |
| hodgkins lymphoma | 27 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 |
| major depressive disorder | 24 | 1,2,3,4,5 | 1:10.00%, 2:30.00%, 3:30.00%, 4:30.00%, 5:30.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003578 (AUC rank 10/24): x3<br>PGS003333 (AUC rank 2/24): x2<br>PGS003580 (AUC rank 9/24): x2<br>PGS004760 (AUC rank 1/24): x1<br>PGS002759 (AUC rank 7/24): x1<br>PGS003576 (AUC rank 8/24): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003578 (AUC rank 10/24): x10 |
| chronic kidney disease | 22 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002237 (AUC rank 12/22): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS002237 (AUC rank 12/22): x10 |
| ovarian carcinoma | 21 | 1,2,3,4,5 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000082 (AUC rank 2/21): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000082 (AUC rank 2/21): x7<br>PGS000793 (AUC rank 1/21): x2<br>PGS003385 (AUC rank 17/21): x1 |
| basal cell carcinoma | 20 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:40.00%, 4:40.00%, 5:40.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000119 (AUC rank 13/20): x6<br>PGS000452 (AUC rank 4/20): x4 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000119 (AUC rank 13/20): x10 |
| sleep apnea | 20 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x7<br>PGS003213 (AUC rank 4/20): x2<br>PGS005219 (AUC rank 2/20): x1 |
| urinary bladder cancer | 20 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:20.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000611 (AUC rank 11/20): x6<br>PGS000613 (AUC rank 5/20): x2<br>PGS000610 (AUC rank 10/20): x2 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000611 (AUC rank 11/20): x6<br>PGS000723 (AUC rank 8/20): x2<br>PGS000613 (AUC rank 5/20): x1<br>PGS000610 (AUC rank 10/20): x1 |
| glaucoma | 15 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004944 (AUC rank 4/15): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000137 (AUC rank 6/15): x8<br>PGS001792 (AUC rank 5/15): x2 |
| uterine carcinoma | 14 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003381 (AUC rank 3/14): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001795 (AUC rank 9/14): x10 |
| osteoporosis | 13 | 1,2,3,4,5 | 1:10.00%, 2:10.00%, 3:10.00%, 4:30.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001273 (AUC rank 5/13): x7<br>PGS001274 (AUC rank 4/13): x2<br>PGS004810 (AUC rank 1/13): x1 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001274 (AUC rank 4/13): x10 |
| testicular carcinoma | 13 | 1,2,3,4,5 | 1:10.00%, 2:10.00%, 3:10.00%, 4:10.00%, 5:10.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000604 (AUC rank 9/13): x9<br>PGS000796 (AUC rank 1/13): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000604 (AUC rank 9/13): x8<br>PGS000796 (AUC rank 1/13): x1<br>PGS001164 (AUC rank 3/13): x1 |
| parkinson disease | 11 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000903 (AUC rank 1/11): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000903 (AUC rank 1/11): x10 |
| systemic lupus erythematosus | 11 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:60.00%, 5:60.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004917 (AUC rank 4/11): x6<br>PGS003960 (AUC rank 9/11): x2<br>PGS000754 (AUC rank 10/11): x2 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003960 (AUC rank 9/11): x8<br>PGS004917 (AUC rank 4/11): x2 |
| chronic obstructive pulmonary disease | 10 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001783 (AUC rank 1/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001783 (AUC rank 1/10): x7<br>PGS001332 (AUC rank 9/10): x3 |
| kidney cancer | 10 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 |
| obesity | 10 | 1,2,3,4,5 | 1:90.00%, 2:90.00%, 3:90.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005235 (AUC rank 1/10): x9<br>PGS002033 (AUC rank 4/10): x1 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10): x10 |
| acute lymphoblastic leukemia | 9 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003448 (AUC rank 9/9): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003448 (AUC rank 9/9): x10 |
| ankylosing spondylitis | 9 | 1,2,3,4,5 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001267 (AUC rank 2/9): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001268 (AUC rank 3/9): x10 |
| aortic stenosis | 8 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005254 (AUC rank 1/8): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005252 (AUC rank 8/8): x10 |
| dilated cardiomyopathy | 8 | 1,2,3,4,5 | 1:0.00%, 2:10.00%, 3:10.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004862 (AUC rank 4/8): x9<br>PGS004949 (AUC rank 2/8): x1 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004862 (AUC rank 4/8): x10 |
| hyperthyroidism | 7 | 1,2,3,4,5 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001043 (AUC rank 7/7): x10 |
| knee osteoarthritis | 7 | 1,2,3,4,5 | 1:0.00%, 2:70.00%, 3:70.00%, 4:70.00%, 5:70.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS002767 (AUC rank 2/7): x7<br>PGS002729 (AUC rank 7/7): x3 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001192 (AUC rank 5/7): x6<br>PGS002729 (AUC rank 7/7): x4 |
| nodular goiter | 7 | 1,2,3,4,5 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001814 (AUC rank 5/7): x7<br>PGS005262 (AUC rank 2/7): x2<br>PGS002022 (AUC rank 4/7): x1 |
| pulmonary embolism | 7 | 1,2,3,4,5 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001280 (AUC rank 2/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001280 (AUC rank 2/7): x10 |
| abdominal aortic aneurysm | 6 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:60.00%, 4:60.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003972 (AUC rank 3/6): x6<br>PGS000753 (AUC rank 5/6): x4 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001784 (AUC rank 4/6): x9<br>PGS003973 (AUC rank 1/6): x1 |
| age-related macular degeneration | 6 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 1/6): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 1/6): x10 |
| cervical carcinoma | 6 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS003428 (AUC rank 5/6): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 6/6): x10 |
| late-onset alzheimer's disease | 5 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000054 (AUC rank 1/5): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS000334 (AUC rank 3/5): x5<br>PGS004918 (AUC rank 4/5): x3<br>PGS000053 (AUC rank 5/5): x2 |
| alcohol dependence | 4 | 1,2,3,4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS002738 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS002738 (AUC rank 1/4): x10 |
| atrial flutter | 4 | 1,2,3,4 | 1:0.00%, 2:0.00%, 3:0.00%, 4:100.00%, 5:N/A | 1:No, 2:No, 3:No, 4:Yes, 5:N/A | PGS001263 (AUC rank 4/4): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:N/A | PGS001263 (AUC rank 4/4): x10 |
| hypertrophic cardiomyopathy | 4 | 1,2,3,4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS004911 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS004911 (AUC rank 1/4): x10 |
| juvenile idiopathic arthritis | 4 | 1,2,3,4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS000114 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS000114 (AUC rank 1/4): x10 |
| peripheral vascular disease | 4 | 1,2,3,4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS005217 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS005217 (AUC rank 1/4): x10 |
| psoriatic arthritis | 4 | 1,2 | 1:100.00%, 2:100.00%, 3:N/A, 4:N/A, 5:N/A | 1:Yes, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS001287 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS001287 (AUC rank 1/4): x10 |
| sarcoidosis | 4 | 1,2,3 | 1:0.00%, 2:100.00%, 3:100.00%, 4:N/A, 5:N/A | 1:No, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS000922 (AUC rank 2/4): x10 | 1:No, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS000922 (AUC rank 2/4): x8<br>PGS000923 (AUC rank 3/4): x2 |
| bipolar disorder | 3 | 1,2,3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:N/A, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS002786 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS002786 (AUC rank 1/3): x10 |
| hashimoto's thyroiditis | 3 | 1,2,3 | 1:0.00%, 2:100.00%, 3:100.00%, 4:N/A, 5:N/A | 1:No, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS005271 (AUC rank 2/3): x10 | 1:No, 2:No, 3:Yes, 4:N/A, 5:N/A | PGS005270 (AUC rank 3/3): x10 |
| nephrolithiasis | 3 | 1,2,3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:N/A, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS004563 (AUC rank 1/3): x10 | 1:No, 2:No, 3:Yes, 4:N/A, 5:N/A | PGS001250 (AUC rank 3/3): x10 |
| preeclampsia | 3 | 1,2,3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:N/A, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS003586 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS003586 (AUC rank 1/3): x10 |
| vitiligo | 3 | 1,2,3 | 1:0.00%, 2:80.00%, 3:100.00%, 4:N/A, 5:N/A | 1:No, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS000738 (AUC rank 2/3): x8<br>PGS001536 (AUC rank 3/3): x2 | 1:No, 2:No, 3:Yes, 4:N/A, 5:N/A | PGS001536 (AUC rank 3/3): x10 |
| acute kidney injury | 2 | 1,2 | 1:100.00%, 2:100.00%, 3:N/A, 4:N/A, 5:N/A | 1:Yes, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS004561 (AUC rank 1/2): x10 | 1:Yes, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS004561 (AUC rank 1/2): x10 |
| autism spectrum disorder | 2 | 1,2 | 1:0.00%, 2:100.00%, 3:N/A, 4:N/A, 5:N/A | 1:No, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS000327 (AUC rank 2/2): x10 | 1:No, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS000327 (AUC rank 2/2): x10 |
| idiopathic pulmonary fibrosis | 2 | 1,2 | 1:100.00%, 2:100.00%, 3:N/A, 4:N/A, 5:N/A | 1:Yes, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS004695 (AUC rank 1/2): x10 | 1:No, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS001791 (AUC rank 2/2): x10 |
| nicotine dependence | 2 | 1,2 | 1:100.00%, 2:100.00%, 3:N/A, 4:N/A, 5:N/A | 1:Yes, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS002037 (AUC rank 1/2): x10 | 1:Yes, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS002037 (AUC rank 1/2): x10 |
| otosclerosis | 2 | 1,2 | 1:40.00%, 2:100.00%, 3:N/A, 4:N/A, 5:N/A | 1:No, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS001255 (AUC rank 2/2): x6<br>PGS002046 (AUC rank 1/2): x4 | 1:No, 2:Yes, 3:N/A, 4:N/A, 5:N/A | PGS001255 (AUC rank 2/2): x10 |