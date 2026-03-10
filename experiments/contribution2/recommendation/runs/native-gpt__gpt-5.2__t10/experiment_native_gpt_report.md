# Contribution2 Experiment 1: Native GPT

## Summary

- **Diseases**: 30
- **Trials per disease**: 10
- **Total trials**: 300
- **Model**: gpt-5.2
- **Estimated API cost**: $1.1735 (uncached input 619,180 tokens = $0.5418; cached input 51,072 tokens = $0.0045; output 89,600 tokens = $0.6272)
- **Overall Recommended Model Accuracy**: 20/30 = 66.67%
- **Baseline (highest reported AUC in PGS Catalog metadata)**: 11/30 = 36.67%

## Experiment Setup

- **Step 1 tools**: prs_model_pgscatalog_search + prs_model_performance_landscape
- **Domain Knowledge**: Disabled
- **Candidate pool**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us
- **Success rule**: a run is successful iff the recommended `PGS ID` belongs to that disease's `Target_TopK` set
- **Baseline rule**: choose the candidate model with the highest reported AUC in PGS Catalog metadata

## Results by Disease

All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.
They are **not** PGS Catalog reported-AUC ranks.


| Ontology                         | N Models | Target_TopK | Trial Hits | Native GPT Hits Target | Native GPT                                                  | Baseline Hits Target | Baseline Models            |
| -------------------------------- | -------- | ----------- | ---------- | ---------------------- | ----------------------------------------------------------- | -------------------- | -------------------------- |
| prostate cancer                  | 96       | 1           | 0/10       | No                     | PGS005237 (AUC rank 72/96): x10                             | No                   | PGS001291 (AUC rank 18/96) |
| thyroid carcinoma                | 32       | 3           | 0/10       | No                     | PGS001289 (AUC rank 24/32): x10                             | No                   | PGS001289 (AUC rank 24/32) |
| hypothyroidism                   | 28       | 1           | 0/10       | No                     | PGS005218 (AUC rank 3/28): x10                              | No                   | PGS005218 (AUC rank 3/28)  |
| hodgkins lymphoma                | 27       | 3           | 10/10      | Yes                    | PGS000639 (AUC rank 1/27): x10                              | No                   | PGS000874 (AUC rank 10/27) |
| obstructive sleep apnea          | 20       | 1           | 10/10      | Yes                    | PGS005220 (AUC rank 1/20): x10                              | No                   | PGS005219 (AUC rank 2/20)  |
| sleep apnea                      | 20       | 1           | 9/10       | Yes                    | PGS005220 (AUC rank 1/20): x9 PGS005219 (AUC rank 2/20): x1 | No                   | PGS005219 (AUC rank 2/20)  |
| testicular neoplasm              | 14       | 5           | 10/10      | Yes                    | PGS001164 (AUC rank 3/14): x10                              | Yes                  | PGS001164 (AUC rank 3/14)  |
| uterine carcinoma                | 14       | 4           | 0/10       | No                     | PGS001795 (AUC rank 9/14): x10                              | No                   | PGS001299 (AUC rank 10/14) |
| kidney cancer                    | 10       | 1           | 10/10      | Yes                    | PGS004908 (AUC rank 1/10): x10                              | Yes                  | PGS004908 (AUC rank 1/10)  |
| obesity                          | 10       | 1           | 0/10       | No                     | PGS001298 (AUC rank 8/10): x10                              | No                   | PGS001298 (AUC rank 8/10)  |
| ankylosing spondylitis           | 9        | 3           | 10/10      | Yes                    | PGS001268 (AUC rank 3/9): x10                               | Yes                  | PGS001268 (AUC rank 3/9)   |
| aortic stenosis                  | 8        | 3           | 0/10       | No                     | PGS005252 (AUC rank 8/8): x10                               | No                   | PGS005252 (AUC rank 8/8)   |
| renal carcinoma                  | 8        | 1           | 10/10      | Yes                    | PGS004908 (AUC rank 1/8): x10                               | Yes                  | PGS004908 (AUC rank 1/8)   |
| graves disease                   | 7        | 2           | 10/10      | Yes                    | PGS005265 (AUC rank 2/7): x10                               | No                   | PGS001042 (AUC rank 5/7)   |
| nodular goiter                   | 7        | 2           | 10/10      | Yes                    | PGS005262 (AUC rank 2/7): x10                               | No                   | PGS005273 (AUC rank 6/7)   |
| pulmonary embolism               | 7        | 4           | 10/10      | Yes                    | PGS001279 (AUC rank 4/7): x10                               | Yes                  | PGS001279 (AUC rank 4/7)   |
| abdominal aortic aneurysm        | 6        | 3           | 8/10       | Yes                    | PGS003973 (AUC rank 1/6): x8 PGS001784 (AUC rank 4/6): x2   | Yes                  | PGS003973 (AUC rank 1/6)   |
| age-related macular degeneration | 6        | 3           | 10/10      | Yes                    | PGS004606 (AUC rank 1/6): x10                               | Yes                  | PGS004952 (AUC rank 3/6)   |
| cervical carcinoma               | 6        | 1           | 0/10       | No                     | PGS001299 (AUC rank 6/6): x10                               | No                   | PGS001299 (AUC rank 6/6)   |
| cutaneous melanoma               | 5        | 1           | 10/10      | Yes                    | PGS003382 (AUC rank 1/5): x10                               | Yes                  | PGS003382 (AUC rank 1/5)   |
| late-onset alzheimer's disease   | 5        | 1           | 0/10       | No                     | PGS000334 (AUC rank 3/5): x8 PGS004918 (AUC rank 4/5): x2   | No                   | PGS004918 (AUC rank 4/5)   |
| open-angle glaucoma              | 5        | 1           | 10/10      | Yes                    | PGS004944 (AUC rank 1/5): x10                               | No                   | PGS001797 (AUC rank 2/5)   |
| alcohol dependence               | 4        | 1           | 10/10      | Yes                    | PGS002738 (AUC rank 1/4): x10                               | No                   | -                          |
| hypertrophic cardiomyopathy      | 4        | 3           | 10/10      | Yes                    | PGS004911 (AUC rank 1/4): x10                               | Yes                  | PGS000739 (AUC rank 2/4)   |
| juvenile idiopathic arthritis    | 4        | 1           | 10/10      | Yes                    | PGS000114 (AUC rank 1/4): x10                               | No                   | PGS000324 (AUC rank 4/4)   |
| peripheral vascular disease      | 4        | 1           | 10/10      | Yes                    | PGS005217 (AUC rank 1/4): x10                               | Yes                  | PGS005217 (AUC rank 1/4)   |
| hashimoto's thyroiditis          | 3        | 2           | 0/10       | No                     | PGS005270 (AUC rank 3/3): x10                               | No                   | PGS005270 (AUC rank 3/3)   |
| preeclampsia                     | 3        | 1           | 10/10      | Yes                    | PGS003586 (AUC rank 1/3): x10                               | No                   | -                          |
| skin carcinoma in situ           | 3        | 1           | 10/10      | Yes                    | PGS000471 (AUC rank 1/3): x10                               | Yes                  | PGS000471 (AUC rank 1/3)   |
| vitiligo                         | 3        | 1           | 0/10       | No                     | PGS001536 (AUC rank 3/3): x10                               | No                   | PGS001536 (AUC rank 3/3)   |


