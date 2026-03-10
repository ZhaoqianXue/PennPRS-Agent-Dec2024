# Contribution2 Experiment 2: With Domain Knowledge vs Without Domain Knowledge vs Baseline

## Summary

- **Model**: gpt-5.2
- **With Domain Knowledge**: 1/5 = 20.00%; `trial_hits = 12/50 = 24.00%`
- **Without Domain Knowledge**: 19/30 = 63.33%; `trial_hits = 190/300 = 63.33%`
- **Baseline**: 0/5 = 0.00%; `coverage = 3/5 = 60.00%`

## Results by Disease

| Ontology | N Models | Target_TopK | Baseline Hits Target | Baseline Models | Without Domain Knowledge Hits Target | Without Domain Knowledge | With Domain Knowledge Hits Target | With Domain Knowledge |
|----------|----------|-------------|----------------------|-----------------|--------------------------------------|--------------------------|-----------------------------------|-----------------------|
| prostate cancer | 96 | 1 | No | PGS001291 (AUC rank 18/96) | No | PGS005237 (AUC rank 72/96): x10 | No | PGS005238 (AUC rank 51/96): x9<br>PGS004155 (AUC rank 30/96): x1 |
| thyroid carcinoma | 32 | 3 | No | PGS001289 (AUC rank 24/32) | No | PGS001289 (AUC rank 24/32): x10 | No | PGS000208 (AUC rank 16/32): x10 |
| hypothyroidism | 28 | 1 | No | PGS001181 (AUC rank 14/28) | No | PGS005218 (AUC rank 3/28): x10 | No | PGS004935 (AUC rank 15/28): x7<br>PGS005218 (AUC rank 3/28): x3 |
| abdominal aortic aneurysm | 6 | 3 | No | - | Yes | PGS003973 (AUC rank 1/6): x10 | No | PGS000753 (AUC rank 5/6): x7<br>PGS003972 (AUC rank 3/6): x3 |
| late-onset alzheimer's disease | 5 | 1 | No | - | No | PGS004918 (AUC rank 4/5): x6<br>PGS000334 (AUC rank 3/5): x4 | Yes | PGS000054 (AUC rank 1/5): x9<br>PGS000053 (AUC rank 5/5): x1 |