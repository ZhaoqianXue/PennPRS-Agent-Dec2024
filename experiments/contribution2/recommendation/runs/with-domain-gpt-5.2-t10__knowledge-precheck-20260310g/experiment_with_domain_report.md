# Contribution2 Experiment 2: With Domain Knowledge

## Summary

- **Diseases**: 10
- **Trials per disease**: 10
- **Total trials**: 100
- **Model**: gpt-5.2
- **Estimated API cost**: $1.4617 (uncached input 584,808 tokens = $1.0234; cached input 0 tokens = $0.0000; output 31,304 tokens = $0.4383)
- **Overall Recommended Model Accuracy**: 5/10 = 50.00%; `trial_hits = 47/100 = 47.00%`
- **Without Domain Knowledge**: 19/10 = 63.33%; `trial_hits = 190/300 = 63.33%`

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
| prostate cancer | 96 | 1 | 0/10 | No | PGS005238 (AUC rank 51/96): x10 | No | PGS005237 (AUC rank 72/96): x10 |
| thyroid carcinoma | 32 | 3 | 0/10 | No | PGS000208 (AUC rank 16/32): x9<br>PGS000209 (AUC rank 17/32): x1 | No | PGS001289 (AUC rank 24/32): x10 |
| hypothyroidism | 28 | 1 | 0/10 | No | PGS004935 (AUC rank 15/28): x6<br>PGS005218 (AUC rank 3/28): x4 | No | PGS005218 (AUC rank 3/28): x10 |
| obstructive sleep apnea | 20 | 1 | 10/10 | Yes | PGS005220 (AUC rank 1/20): x10 | Yes | PGS005220 (AUC rank 1/20): x10 |
| sleep apnea | 20 | 1 | 10/10 | Yes | PGS005220 (AUC rank 1/20): x10 | Yes | PGS005220 (AUC rank 1/20): x10 |
| obesity | 10 | 1 | 10/10 | Yes | PGS005235 (AUC rank 1/10): x10 | No | PGS001298 (AUC rank 8/10): x10 |
| abdominal aortic aneurysm | 6 | 3 | 10/10 | Yes | PGS003972 (AUC rank 3/6): x10 | Yes | PGS003973 (AUC rank 1/6): x10 |
| cervical carcinoma | 6 | 1 | 0/10 | No | PGS003428 (AUC rank 5/6): x10 | No | PGS001299 (AUC rank 6/6): x10 |
| late-onset alzheimer's disease | 5 | 1 | 7/10 | Yes | PGS000054 (AUC rank 1/5): x7<br>PGS000053 (AUC rank 5/5): x3 | No | PGS004918 (AUC rank 4/5): x6<br>PGS000334 (AUC rank 3/5): x4 |
| vitiligo | 3 | 1 | 0/10 | No | PGS000738 (AUC rank 2/3): x8<br>PGS001536 (AUC rank 3/3): x2 | No | PGS001536 (AUC rank 3/3): x10 |