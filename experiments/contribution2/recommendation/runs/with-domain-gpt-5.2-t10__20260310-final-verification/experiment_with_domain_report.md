# Contribution2 Experiment 2: With Domain Knowledge

## Summary

- **Diseases**: 30
- **Trials per disease**: 10
- **Total trials**: 300
- **Model**: gpt-5.2
- **Estimated API cost**: $1.4854 (uncached input 890,308 tokens = $0.7790; cached input 453,888 tokens = $0.0397; output 95,231 tokens = $0.6666)
- **Overall Recommended Model Accuracy**: 18/30 = 60.00%; `trial_hits = 193/300 = 64.33%`
- **Without Domain Knowledge**: 19/30 = 63.33%; `trial_hits = 190/300 = 63.33%`

## Experiment Setup

- **Step 1 tools**: prs_model_pgscatalog_search + prs_model_domain_knowledge + prs_model_performance_landscape
- **Domain Knowledge**: Enabled (local curated knowledge base)
- **Candidate pool**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us
- **Success rule**: a run is successful iff the recommended `PGS ID` belongs to that disease's `Target_TopK` set
- **Without Domain Knowledge reference**: compare against `without-domain-gpt-5.2-t10` under the same 30-disease / 10-trial protocol

## Results by Disease

All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.
They are **not** PGS Catalog reported-AUC ranks.

| Ontology | N Models | Target_TopK | Trial Hits | With Domain Knowledge Hits Target | With Domain Knowledge | Without Domain Knowledge Hits Target | Without Domain Knowledge |
|----------|----------|-------------|------------|-----------------------------------|-----------------------|--------------------------------------|--------------------------|
| prostate cancer | 96 | 1 | 0/10 | No | PGS005238 (AUC rank 51/96): x8<br>PGS001291 (AUC rank 18/96): x1<br>PGS004155 (AUC rank 30/96): x1 | No | PGS005237 (AUC rank 72/96): x10 |
| thyroid carcinoma | 32 | 3 | 0/10 | No | PGS000208 (AUC rank 16/32): x8<br>PGS000209 (AUC rank 17/32): x2 | No | PGS001289 (AUC rank 24/32): x10 |
| hypothyroidism | 28 | 1 | 0/10 | No | PGS004935 (AUC rank 15/28): x8<br>PGS005218 (AUC rank 3/28): x2 | No | PGS005218 (AUC rank 3/28): x10 |
| hodgkins lymphoma | 27 | 3 | 10/10 | Yes | PGS000639 (AUC rank 1/27): x10 | Yes | PGS000639 (AUC rank 1/27): x10 |
| obstructive sleep apnea | 20 | 1 | 5/10 | No | PGS005220 (AUC rank 1/20): x5<br>PGS005219 (AUC rank 2/20): x5 | Yes | PGS005220 (AUC rank 1/20): x10 |
| sleep apnea | 20 | 1 | 9/10 | Yes | PGS005220 (AUC rank 1/20): x9<br>PGS005219 (AUC rank 2/20): x1 | Yes | PGS005220 (AUC rank 1/20): x10 |
| testicular neoplasm | 14 | 5 | 4/10 | No | PGS000604 (AUC rank 10/14): x5<br>PGS000796 (AUC rank 1/14): x4<br>PGS000602 (AUC rank 7/14): x1 | Yes | PGS001164 (AUC rank 3/14): x10 |
| uterine carcinoma | 14 | 4 | 9/10 | Yes | PGS003381 (AUC rank 3/14): x9<br>PGS001795 (AUC rank 9/14): x1 | No | PGS001795 (AUC rank 9/14): x10 |
| kidney cancer | 10 | 1 | 10/10 | Yes | PGS004908 (AUC rank 1/10): x10 | Yes | PGS004908 (AUC rank 1/10): x10 |
| obesity | 10 | 1 | 0/10 | No | PGS002033 (AUC rank 4/10): x10 | No | PGS001298 (AUC rank 8/10): x10 |
| ankylosing spondylitis | 9 | 3 | 9/10 | Yes | PGS001267 (AUC rank 2/9): x9<br>PGS002089 (AUC rank 4/9): x1 | Yes | PGS001268 (AUC rank 3/9): x10 |
| aortic stenosis | 8 | 3 | 10/10 | Yes | PGS005254 (AUC rank 1/8): x10 | No | PGS005252 (AUC rank 8/8): x10 |
| renal carcinoma | 8 | 1 | 10/10 | Yes | PGS004908 (AUC rank 1/8): x10 | Yes | PGS004908 (AUC rank 1/8): x10 |
| graves disease | 7 | 2 | 10/10 | Yes | PGS005265 (AUC rank 2/7): x10 | Yes | PGS005265 (AUC rank 2/7): x10 |
| nodular goiter | 7 | 2 | 10/10 | Yes | PGS005262 (AUC rank 2/7): x10 | Yes | PGS005262 (AUC rank 2/7): x10 |
| pulmonary embolism | 7 | 4 | 2/10 | No | PGS003861 (AUC rank 7/7): x8<br>PGS001280 (AUC rank 2/7): x1<br>PGS001279 (AUC rank 4/7): x1 | Yes | PGS001280 (AUC rank 2/7): x7<br>PGS001279 (AUC rank 4/7): x3 |
| abdominal aortic aneurysm | 6 | 3 | 0/10 | No | PGS000753 (AUC rank 5/6): x10 | Yes | PGS003973 (AUC rank 1/6): x10 |
| age-related macular degeneration | 6 | 3 | 10/10 | Yes | PGS004606 (AUC rank 1/6): x10 | Yes | PGS004606 (AUC rank 1/6): x6<br>PGS004952 (AUC rank 3/6): x4 |
| cervical carcinoma | 6 | 1 | 1/10 | No | PGS003428 (AUC rank 5/6): x8<br>PGS000073 (AUC rank 1/6): x1<br>PGS001299 (AUC rank 6/6): x1 | No | PGS001299 (AUC rank 6/6): x10 |
| cutaneous melanoma | 5 | 1 | 5/10 | No | PGS003382 (AUC rank 1/5): x5<br>PGS000766 (AUC rank 3/5): x5 | Yes | PGS003382 (AUC rank 1/5): x10 |
| late-onset alzheimer's disease | 5 | 1 | 0/10 | No | PGS000053 (AUC rank 5/5): x10 | No | PGS004918 (AUC rank 4/5): x6<br>PGS000334 (AUC rank 3/5): x4 |
| open-angle glaucoma | 5 | 1 | 10/10 | Yes | PGS004944 (AUC rank 1/5): x10 | Yes | PGS004944 (AUC rank 1/5): x10 |
| alcohol dependence | 4 | 1 | 10/10 | Yes | PGS002738 (AUC rank 1/4): x10 | Yes | PGS002738 (AUC rank 1/4): x10 |
| hypertrophic cardiomyopathy | 4 | 3 | 10/10 | Yes | PGS004911 (AUC rank 1/4): x10 | Yes | PGS004911 (AUC rank 1/4): x8<br>PGS000739 (AUC rank 2/4): x2 |
| juvenile idiopathic arthritis | 4 | 1 | 10/10 | Yes | PGS000114 (AUC rank 1/4): x10 | Yes | PGS000114 (AUC rank 1/4): x10 |
| peripheral vascular disease | 4 | 1 | 10/10 | Yes | PGS005217 (AUC rank 1/4): x10 | No | PGS001843 (AUC rank 4/4): x9<br>PGS002055 (AUC rank 2/4): x1 |
| hashimoto's thyroiditis | 3 | 2 | 9/10 | Yes | PGS005271 (AUC rank 2/3): x9<br>PGS005270 (AUC rank 3/3): x1 | No | PGS005270 (AUC rank 3/3): x10 |
| preeclampsia | 3 | 1 | 10/10 | Yes | PGS003586 (AUC rank 1/3): x10 | Yes | PGS003586 (AUC rank 1/3): x10 |
| skin carcinoma in situ | 3 | 1 | 10/10 | Yes | PGS000471 (AUC rank 1/3): x10 | Yes | PGS000471 (AUC rank 1/3): x10 |
| vitiligo | 3 | 1 | 0/10 | No | PGS000738 (AUC rank 2/3): x7<br>PGS001536 (AUC rank 3/3): x3 | No | PGS001536 (AUC rank 3/3): x10 |