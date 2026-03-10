# Contribution2 Experiment 2: With Domain Knowledge vs Without Domain Knowledge vs Baseline

## Summary

- **Model**: gpt-5.2
- **With Domain Knowledge**: 4/10 = 40.00%; `trial_hits = 43/100 = 43.00%`
- **Without Domain Knowledge**: 19/30 = 63.33%; `trial_hits = 190/300 = 63.33%`
- **Baseline**: 0/10 = 0.00%; `coverage = 6/10 = 60.00%`

## Results by Disease

| Ontology | N Models | Target_TopK | Baseline Hits Target | Baseline Models | Without Domain Knowledge Hits Target | Without Domain Knowledge | With Domain Knowledge Hits Target | With Domain Knowledge |
|----------|----------|-------------|----------------------|-----------------|--------------------------------------|--------------------------|-----------------------------------|-----------------------|
| prostate cancer | 96 | 1 | No | PGS001291 (AUC rank 18/96) | No | PGS005237 (AUC rank 72/96): x10 | No | PGS005238 (AUC rank 51/96): x10 |
| thyroid carcinoma | 32 | 3 | No | PGS001289 (AUC rank 24/32) | No | PGS001289 (AUC rank 24/32): x10 | No | PGS000208 (AUC rank 16/32): x8<br>PGS000209 (AUC rank 17/32): x2 |
| hypothyroidism | 28 | 1 | No | PGS001181 (AUC rank 14/28) | No | PGS005218 (AUC rank 3/28): x10 | No | PGS005218 (AUC rank 3/28): x7<br>PGS004935 (AUC rank 15/28): x3 |
| obstructive sleep apnea | 20 | 1 | No | - | Yes | PGS005220 (AUC rank 1/20): x10 | Yes | PGS005220 (AUC rank 1/20): x10 |
| sleep apnea | 20 | 1 | No | - | Yes | PGS005220 (AUC rank 1/20): x10 | Yes | PGS005220 (AUC rank 1/20): x10 |
| obesity | 10 | 1 | No | PGS001298 (AUC rank 8/10) | No | PGS001298 (AUC rank 8/10): x10 | Yes | PGS005235 (AUC rank 1/10): x10 |
| abdominal aortic aneurysm | 6 | 3 | No | - | Yes | PGS003973 (AUC rank 1/6): x10 | No | PGS003972 (AUC rank 3/6): x4<br>PGS000753 (AUC rank 5/6): x4<br>PGS003973 (AUC rank 1/6): x1<br>PGS001784 (AUC rank 4/6): x1 |
| cervical carcinoma | 6 | 1 | No | PGS001299 (AUC rank 6/6) | No | PGS001299 (AUC rank 6/6): x10 | No | PGS003428 (AUC rank 5/6): x9<br>PGS000073 (AUC rank 1/6): x1 |
| late-onset alzheimer's disease | 5 | 1 | No | - | No | PGS004918 (AUC rank 4/5): x6<br>PGS000334 (AUC rank 3/5): x4 | Yes | PGS000054 (AUC rank 1/5): x7<br>PGS000053 (AUC rank 5/5): x3 |
| vitiligo | 3 | 1 | No | PGS001536 (AUC rank 3/3) | No | PGS001536 (AUC rank 3/3): x10 | No | PGS000738 (AUC rank 2/3): x8<br>PGS001536 (AUC rank 3/3): x2 |