# Contribution2 Experiment 2: With Domain Knowledge vs Without Domain Knowledge vs Baseline

## Summary

- **Model**: gpt-5.2
- **With Domain Knowledge**: 19/30 = 63.33%; `trial_hits = 179/300 = 59.67%`
- **Without Domain Knowledge**: 14/30 = 46.67%; `trial_hits = 134/300 = 44.67%`
- **Baseline**: 0/30 = 0.00%

## Results by Disease

| Ontology | N Models | Eligible Ks | Baseline Hit@1..5 | Baseline Models | Without Domain Knowledge Hit@1..5 | Without Domain Knowledge | With Domain Knowledge Hit@1..5 | With Domain Knowledge |
|----------|----------|-------------|-------------------|-----------------|-------------------------------------|--------------------------|----------------------------------|-----------------------|
| prostate cancer | 96 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001291 (AUC rank 18/96) | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005237 (AUC rank 72/96): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005238 (AUC rank 51/96): x7<br>PGS000719 (AUC rank 11/96): x2<br>PGS004155 (AUC rank 30/96): x1 |
| thyroid carcinoma | 32 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001289 (AUC rank 24/32) | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001289 (AUC rank 24/32): x10 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS000208 (AUC rank 16/32): x10 |
| hypothyroidism | 28 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001181 (AUC rank 14/28) | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS005218 (AUC rank 3/28): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005268 (AUC rank 1/28): x7<br>PGS004935 (AUC rank 15/28): x2<br>PGS005218 (AUC rank 3/28): x1 |
| hodgkins lymphoma | 27 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000639 (AUC rank 1/27): x10 |
| obstructive sleep apnea | 20 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 |
| sleep apnea | 20 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005220 (AUC rank 1/20): x10 |
| testicular neoplasm | 14 | 1,2,3,4,5 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001164 (AUC rank 3/14) | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001164 (AUC rank 3/14): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000796 (AUC rank 1/14): x5<br>PGS000604 (AUC rank 10/14): x3<br>PGS001164 (AUC rank 3/14): x1<br>PGS000602 (AUC rank 7/14): x1 |
| uterine carcinoma | 14 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 10/14) | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001795 (AUC rank 9/14): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003381 (AUC rank 3/14): x10 |
| kidney cancer | 10 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/10): x10 |
| obesity | 10 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10) | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001298 (AUC rank 8/10): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005235 (AUC rank 1/10): x10 |
| ankylosing spondylitis | 9 | 1,2,3,4,5 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001268 (AUC rank 3/9) | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001268 (AUC rank 3/9): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001267 (AUC rank 2/9): x10 |
| aortic stenosis | 8 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:No, 5:No | PGS005252 (AUC rank 8/8): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005254 (AUC rank 1/8): x10 |
| renal carcinoma | 8 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/8): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004908 (AUC rank 1/8): x10 |
| graves disease | 7 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS001042 (AUC rank 5/7) | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005265 (AUC rank 2/7): x10 |
| nodular goiter | 7 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS005262 (AUC rank 2/7): x10 |
| pulmonary embolism | 7 | 1,2,3,4,5 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS001277 (AUC rank 3/7) | 1:No, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS001280 (AUC rank 2/7): x7<br>PGS001279 (AUC rank 4/7): x3 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS003861 (AUC rank 7/7): x6<br>PGS001280 (AUC rank 2/7): x4 |
| abdominal aortic aneurysm | 6 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003973 (AUC rank 1/6): x10 | 1:No, 2:No, 3:Yes, 4:Yes, 5:Yes | PGS003972 (AUC rank 3/6): x8<br>PGS000753 (AUC rank 5/6): x2 |
| age-related macular degeneration | 6 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 1/6): x6<br>PGS004952 (AUC rank 3/6): x4 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004606 (AUC rank 1/6): x10 |
| cervical carcinoma | 6 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 6/6) | 1:No, 2:No, 3:No, 4:No, 5:No | PGS001299 (AUC rank 6/6): x10 | 1:No, 2:No, 3:No, 4:No, 5:Yes | PGS003428 (AUC rank 5/6): x8<br>PGS000073 (AUC rank 1/6): x2 |
| cutaneous melanoma | 5 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003382 (AUC rank 1/5): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS003382 (AUC rank 1/5): x8<br>PGS000766 (AUC rank 3/5): x2 |
| late-onset alzheimer's disease | 5 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:No, 2:No, 3:No, 4:Yes, 5:Yes | PGS004918 (AUC rank 4/5): x6<br>PGS000334 (AUC rank 3/5): x4 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS000054 (AUC rank 1/5): x8<br>PGS000053 (AUC rank 5/5): x2 |
| open-angle glaucoma | 5 | 1,2,3,4,5 | 1:No, 2:No, 3:No, 4:No, 5:No | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004944 (AUC rank 1/5): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:Yes | PGS004944 (AUC rank 1/5): x9<br>PGS001797 (AUC rank 2/5): x1 |
| alcohol dependence | 4 | 1,2,3,4 | 1:No, 2:No, 3:No, 4:No, 5:N/A | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS002738 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS002738 (AUC rank 1/4): x10 |
| hypertrophic cardiomyopathy | 4 | 1,2,3,4 | 1:No, 2:No, 3:No, 4:No, 5:N/A | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS004911 (AUC rank 1/4): x8<br>PGS000739 (AUC rank 2/4): x2 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS004911 (AUC rank 1/4): x10 |
| juvenile idiopathic arthritis | 4 | 1,2,3,4 | 1:No, 2:No, 3:No, 4:No, 5:N/A | - | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS000114 (AUC rank 1/4): x10 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS000114 (AUC rank 1/4): x10 |
| peripheral vascular disease | 4 | 1,2,3,4 | 1:No, 2:No, 3:No, 4:No, 5:N/A | - | 1:No, 2:No, 3:No, 4:Yes, 5:N/A | PGS001843 (AUC rank 4/4): x9<br>PGS002055 (AUC rank 2/4): x1 | 1:Yes, 2:Yes, 3:Yes, 4:Yes, 5:N/A | PGS005217 (AUC rank 1/4): x10 |
| hashimoto's thyroiditis | 3 | 1,2,3 | 1:No, 2:No, 3:No, 4:N/A, 5:N/A | - | 1:No, 2:No, 3:Yes, 4:N/A, 5:N/A | PGS005270 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS005271 (AUC rank 2/3): x8<br>PGS005270 (AUC rank 3/3): x2 |
| preeclampsia | 3 | 1,2,3 | 1:No, 2:No, 3:No, 4:N/A, 5:N/A | - | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS003586 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS003586 (AUC rank 1/3): x10 |
| skin carcinoma in situ | 3 | 1,2,3 | 1:No, 2:No, 3:No, 4:N/A, 5:N/A | - | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS000471 (AUC rank 1/3): x10 | 1:Yes, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS000471 (AUC rank 1/3): x10 |
| vitiligo | 3 | 1,2,3 | 1:No, 2:No, 3:Yes, 4:N/A, 5:N/A | PGS001536 (AUC rank 3/3) | 1:No, 2:No, 3:Yes, 4:N/A, 5:N/A | PGS001536 (AUC rank 3/3): x10 | 1:No, 2:Yes, 3:Yes, 4:N/A, 5:N/A | PGS000738 (AUC rank 2/3): x7<br>PGS001536 (AUC rank 3/3): x3 |