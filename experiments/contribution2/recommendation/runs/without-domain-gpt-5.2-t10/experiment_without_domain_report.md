# Contribution2 Experiment 1: Without Domain Knowledge

## Summary

- **Diseases**: 30
- **Trials per disease**: 10
- **Total trials**: 300
- **Model**: gpt-5.2
- **Estimated API cost**: $1.0176 (uncached input 613,194 tokens = $0.5365; cached input 36,992 tokens = $0.0032; output 68,256 tokens = $0.4778)
- **Modal Hit@1**: 14/30 = 46.67%; `trial_hits = 134/300 = 44.67%`
- **Modal Hit@2**: 17/30 = 56.67%; `trial_hits = 164/300 = 54.67%`
- **Modal Hit@3**: 22/30 = 73.33%; `trial_hits = 222/300 = 74.00%`
- **Modal Hit@4**: 20/26 = 76.92%; `trial_hits = 200/260 = 76.92%`
- **Modal Hit@5**: 16/22 = 72.73%; `trial_hits = 160/220 = 72.73%`
- **Baseline Hit@1**: 6/30 = 20.00% (coverage 28/30)
- **Baseline Hit@2**: 10/30 = 33.33% (coverage 28/30)
- **Baseline Hit@3**: 16/30 = 53.33% (coverage 28/30)
- **Baseline Hit@4**: 16/26 = 61.54% (coverage 25/26)
- **Baseline Hit@5**: 14/22 = 63.64% (coverage 22/22)

## Experiment Setup

- **Step 1 tools**: prs_model_pgscatalog_search + prs_model_performance_landscape
- **Domain Knowledge**: Disabled
- **Candidate pool**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us
- **Success rule**: report `Hit@k` for `k = 1..5` against the AoU benchmark ranking; diseases with fewer than `k` evaluated models are excluded from the `Hit@k` denominator
- **Baseline rule**: tiered—Tier 1 uses highest PGS-only AUROC; Tier 2 falls back to highest full-model AUROC when no candidate has PGS-comparable AUROC
- **Benchmark tie handling**: if the AoU benchmark AUC is tied at the `k`-th cutoff, all tied models count as `Top@k`

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`, with `r = 1` as best and `r = M` as worst.
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Without Domain Knowledge: `mean NRS = 0.6790` (30 modal selections); `trial mean NRS = 0.6736` (300 trials)

## Results by Disease

All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.
They are **not** PGS Catalog reported-AUC ranks.

| Ontology | N Models | Eligible Ks | Trial Hit@1..5 | Without Domain Knowledge Hit@1..5 | Without Domain Knowledge | Baseline Hit@1..5 | Baseline Models |
|----------|----------|-------------|---------------|-------------------------------------|--------------------------|-------------------|-----------------|
| prostate cancer | 96 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005237 (AUC rank 72/96): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001291 (AUC rank 18/96) |
| thyroid carcinoma | 32 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001289 (AUC rank 24/32): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001289 (AUC rank 24/32) |
| hypothyroidism | 28 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28) |
| hodgkins lymphoma | 27 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000874 (AUC rank 10/27) |
| obstructive sleep apnea | 20 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005219 (AUC rank 2/20) |
| sleep apnea | 20 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005219 (AUC rank 2/20) |
| testicular neoplasm | 14 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001164 (AUC rank 3/14): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001164 (AUC rank 3/14) |
| uterine carcinoma | 14 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001795 (AUC rank 9/14): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 10/14) |
| kidney cancer | 10 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10) |
| obesity | 10 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10) |
| ankylosing spondylitis | 9 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001268 (AUC rank 3/9): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001268 (AUC rank 3/9) |
| aortic stenosis | 8 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005252 (AUC rank 8/8): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005252 (AUC rank 8/8) |
| renal carcinoma | 8 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/8): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/8) |
| graves disease | 7 | 1,2,3,4,5 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x10 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001042 (AUC rank 5/7) |
| nodular goiter | 7 | 1,2,3,4,5 | 1:0.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005273 (AUC rank 6/7) |
| pulmonary embolism | 7 | 1,2,3,4,5 | 1:0.00%, 2:70.00%, 3:70.00%, 4:100.00%, 5:100.00% | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001280 (AUC rank 2/7): x7<br>PGS001279 (AUC rank 4/7): x3 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS001279 (AUC rank 4/7) |
| abdominal aortic aneurysm | 6 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003973 (AUC rank 1/6): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003973 (AUC rank 1/6) |
| age-related macular degeneration | 6 | 1,2,3,4,5 | 1:60.00%, 2:60.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 1/6): x6<br>PGS004952 (AUC rank 3/6): x4 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS004952 (AUC rank 3/6) |
| cervical carcinoma | 6 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:0.00%, 4:0.00%, 5:0.00% | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 6/6): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 6/6) |
| cutaneous melanoma | 5 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003382 (AUC rank 1/5): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003382 (AUC rank 1/5) |
| late-onset alzheimer's disease | 5 | 1,2,3,4,5 | 1:0.00%, 2:0.00%, 3:40.00%, 4:100.00%, 5:100.00% | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004918 (AUC rank 4/5): x6<br>PGS000334 (AUC rank 3/5): x4 | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004918 (AUC rank 4/5) |
| open-angle glaucoma | 5 | 1,2,3,4,5 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:100.00% | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004944 (AUC rank 1/5): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001797 (AUC rank 2/5) |
| alcohol dependence | 4 | 1,2,3,4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS002738 (AUC rank 1/4): x10 | 1:No, 2:No, 3:No, 4:No, 5:N/A | - |
| hypertrophic cardiomyopathy | 4 | 1,2,3,4 | 1:80.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS004911 (AUC rank 1/4): x8<br>PGS000739 (AUC rank 2/4): x2 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS000739 (AUC rank 2/4) |
| juvenile idiopathic arthritis | 4 | 1,2,3,4 | 1:100.00%, 2:100.00%, 3:100.00%, 4:100.00%, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS000114 (AUC rank 1/4): x10 | 1:No, 2:No, 3:No, 4:Yes, 5:N/A | PGS000324 (AUC rank 4/4) |
| peripheral vascular disease | 4 | 1,2,3,4 | 1:0.00%, 2:10.00%, 3:10.00%, 4:100.00%, 5:N/A | 1:No, 2:No, 3:No, 4:Yes, 5:N/A | PGS001843 (AUC rank 4/4): x9<br>PGS002055 (AUC rank 2/4): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS005217 (AUC rank 1/4) |
| hashimoto's thyroiditis | 3 | 1,2,3 | 1:0.00%, 2:0.00%, 3:100.00%, 4:N/A, 5:N/A | 1:No, 2:No, 3:Yes, 4:N/A, 5:N/A | PGS005270 (AUC rank 3/3): x10 | 1:No, 2:No, 3:Yes, 4:N/A, 5:N/A | PGS005270 (AUC rank 3/3) |
| preeclampsia | 3 | 1,2,3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:N/A, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS003586 (AUC rank 1/3): x10 | 1:No, 2:No, 3:No, 4:N/A, 5:N/A | - |
| skin carcinoma in situ | 3 | 1,2,3 | 1:100.00%, 2:100.00%, 3:100.00%, 4:N/A, 5:N/A | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS000471 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS000471 (AUC rank 1/3) |
| vitiligo | 3 | 1,2,3 | 1:0.00%, 2:0.00%, 3:100.00%, 4:N/A, 5:N/A | 1:No, 2:No, 3:Yes, 4:N/A, 5:N/A | PGS001536 (AUC rank 3/3): x10 | 1:No, 2:No, 3:Yes, 4:N/A, 5:N/A | PGS001536 (AUC rank 3/3) |