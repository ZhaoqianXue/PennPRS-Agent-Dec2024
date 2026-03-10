# Contribution2 Experiment 2: GPT + prs_model_domain_knowledge vs Native GPT vs Baseline

## Summary

- **Model**: gpt-5.2
- **GPT + prs_model_domain_knowledge**: 25/30 = 83.33%
- **Native GPT**: 20/30 = 66.67%
- **Baseline**: 11/30 = 36.67%

## Results by Disease

| Ontology | N Models | Target_TopK | Baseline Hits Target | Baseline Models | Native GPT Hits Target | Native GPT | Domain GPT Hits Target | Domain GPT |
|----------|----------|-------------|----------------------|-----------------|------------------------|------------|------------------------|------------|
| prostate cancer | 96 | 1 | No | PGS001291 (AUC rank 18/96) | No | PGS005237 (AUC rank 72/96): x10 | No | PGS000719 (AUC rank 11/96): x4<br>PGS003415 (AUC rank 79/96): x3<br>PGS000795 (AUC rank 54/96): x2<br>PGS000084 (AUC rank 75/96): x1 |
| thyroid carcinoma | 32 | 3 | No | PGS001289 (AUC rank 24/32) | No | PGS001289 (AUC rank 24/32): x10 | No | PGS004954 (AUC rank 8/32): x9<br>PGS005259 (AUC rank 4/32): x1 |
| hypothyroidism | 28 | 1 | No | PGS005218 (AUC rank 3/28) | No | PGS005218 (AUC rank 3/28): x10 | No | PGS005218 (AUC rank 3/28): x10 |
| hodgkins lymphoma | 27 | 3 | No | PGS000874 (AUC rank 10/27) | Yes | PGS000639 (AUC rank 1/27): x10 | Yes | PGS000639 (AUC rank 1/27): x10 |
| obstructive sleep apnea | 20 | 1 | No | PGS005219 (AUC rank 2/20) | Yes | PGS005220 (AUC rank 1/20): x10 | Yes | PGS005220 (AUC rank 1/20): x10 |
| sleep apnea | 20 | 1 | No | PGS005219 (AUC rank 2/20) | Yes | PGS005220 (AUC rank 1/20): x9<br>PGS005219 (AUC rank 2/20): x1 | Yes | PGS005220 (AUC rank 1/20): x10 |
| testicular neoplasm | 14 | 5 | Yes | PGS001164 (AUC rank 3/14) | Yes | PGS001164 (AUC rank 3/14): x10 | Yes | PGS000796 (AUC rank 1/14): x10 |
| uterine carcinoma | 14 | 4 | No | PGS001299 (AUC rank 10/14) | No | PGS001795 (AUC rank 9/14): x10 | Yes | PGS003381 (AUC rank 3/14): x10 |
| kidney cancer | 10 | 1 | Yes | PGS004908 (AUC rank 1/10) | Yes | PGS004908 (AUC rank 1/10): x10 | Yes | PGS004908 (AUC rank 1/10): x10 |
| obesity | 10 | 1 | No | PGS001298 (AUC rank 8/10) | No | PGS001298 (AUC rank 8/10): x10 | Yes | PGS005235 (AUC rank 1/10): x6<br>PGS003959 (AUC rank 3/10): x3<br>PGS003400 (AUC rank 9/10): x1 |
| ankylosing spondylitis | 9 | 3 | Yes | PGS001268 (AUC rank 3/9) | Yes | PGS001268 (AUC rank 3/9): x10 | Yes | PGS001267 (AUC rank 2/9): x10 |
| aortic stenosis | 8 | 3 | No | PGS005252 (AUC rank 8/8) | No | PGS005252 (AUC rank 8/8): x10 | Yes | PGS005254 (AUC rank 1/8): x10 |
| renal carcinoma | 8 | 1 | Yes | PGS004908 (AUC rank 1/8) | Yes | PGS004908 (AUC rank 1/8): x10 | Yes | PGS004908 (AUC rank 1/8): x10 |
| graves disease | 7 | 2 | No | PGS001042 (AUC rank 5/7) | Yes | PGS005265 (AUC rank 2/7): x10 | Yes | PGS005265 (AUC rank 2/7): x10 |
| nodular goiter | 7 | 2 | No | PGS005273 (AUC rank 6/7) | Yes | PGS005262 (AUC rank 2/7): x10 | Yes | PGS005262 (AUC rank 2/7): x10 |
| pulmonary embolism | 7 | 4 | Yes | PGS001279 (AUC rank 4/7) | Yes | PGS001279 (AUC rank 4/7): x10 | Yes | PGS001279 (AUC rank 4/7): x9<br>PGS003861 (AUC rank 7/7): x1 |
| abdominal aortic aneurysm | 6 | 3 | Yes | PGS003973 (AUC rank 1/6) | Yes | PGS003973 (AUC rank 1/6): x8<br>PGS001784 (AUC rank 4/6): x2 | Yes | PGS003973 (AUC rank 1/6): x10 |
| age-related macular degeneration | 6 | 3 | Yes | PGS004952 (AUC rank 3/6) | Yes | PGS004606 (AUC rank 1/6): x10 | Yes | PGS004606 (AUC rank 1/6): x10 |
| cervical carcinoma | 6 | 1 | No | PGS001299 (AUC rank 6/6) | No | PGS001299 (AUC rank 6/6): x10 | Yes | PGS000073 (AUC rank 1/6): x10 |
| cutaneous melanoma | 5 | 1 | Yes | PGS003382 (AUC rank 1/5) | Yes | PGS003382 (AUC rank 1/5): x10 | Yes | PGS003382 (AUC rank 1/5): x9<br>PGS000766 (AUC rank 3/5): x1 |
| late-onset alzheimer's disease | 5 | 1 | No | PGS004918 (AUC rank 4/5) | No | PGS000334 (AUC rank 3/5): x8<br>PGS004918 (AUC rank 4/5): x2 | No | PGS000334 (AUC rank 3/5): x10 |
| open-angle glaucoma | 5 | 1 | No | PGS001797 (AUC rank 2/5) | Yes | PGS004944 (AUC rank 1/5): x10 | Yes | PGS004944 (AUC rank 1/5): x10 |
| alcohol dependence | 4 | 1 | No | - | Yes | PGS002738 (AUC rank 1/4): x10 | Yes | PGS002738 (AUC rank 1/4): x8<br>PGS000201 (AUC rank 2/4): x2 |
| hypertrophic cardiomyopathy | 4 | 3 | Yes | PGS000739 (AUC rank 2/4) | Yes | PGS004911 (AUC rank 1/4): x10 | Yes | PGS004911 (AUC rank 1/4): x10 |
| juvenile idiopathic arthritis | 4 | 1 | No | PGS000324 (AUC rank 4/4) | Yes | PGS000114 (AUC rank 1/4): x10 | Yes | PGS000114 (AUC rank 1/4): x10 |
| peripheral vascular disease | 4 | 1 | Yes | PGS005217 (AUC rank 1/4) | Yes | PGS005217 (AUC rank 1/4): x10 | Yes | PGS005217 (AUC rank 1/4): x10 |
| hashimoto's thyroiditis | 3 | 2 | No | PGS005270 (AUC rank 3/3) | No | PGS005270 (AUC rank 3/3): x10 | Yes | PGS005271 (AUC rank 2/3): x10 |
| preeclampsia | 3 | 1 | No | - | Yes | PGS003586 (AUC rank 1/3): x10 | Yes | PGS003586 (AUC rank 1/3): x10 |
| skin carcinoma in situ | 3 | 1 | Yes | PGS000471 (AUC rank 1/3) | Yes | PGS000471 (AUC rank 1/3): x10 | Yes | PGS000471 (AUC rank 1/3): x10 |
| vitiligo | 3 | 1 | No | PGS001536 (AUC rank 3/3) | No | PGS001536 (AUC rank 3/3): x10 | No | PGS000738 (AUC rank 2/3): x10 |