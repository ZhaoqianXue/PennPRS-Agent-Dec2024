# Contribution2 Experiment 1: Native GPT (Batch Formal Protocol)

## Summary

- **Diseases**: 30
- **Trials per disease**: 10
- **Total trials**: 300
- **Model**: gpt-5.2
- **Execution mode**: OpenAI Batch API
- **Step 1 tools**: prs_model_pgscatalog_search + prs_model_performance_landscape
- **Domain Knowledge**: Disabled
- **Strict LLM-only mode**: Enabled (no fallback, no auto-filled recommendation)
- **Mean disease hit rate**: 65.67%
- **Majority-vote accuracy**: 20/30 = 66.67%
- **Baseline (highest reported AUC in PGS Catalog metadata)**: 11/30 = 36.67%

## Per-Disease Results


| Ontology                         | N Models | Target_TopK | Trial Hits | Modal Recommendation | Modal In Target | Baseline  | Baseline In Target |
| -------------------------------- | -------- | ----------- | ---------- | -------------------- | --------------- | --------- | ------------------ |
| abdominal aortic aneurysm        | 6        | 3           | 8/10       | PGS003973            | Yes             | PGS003973 | Yes                |
| age-related macular degeneration | 6        | 3           | 10/10      | PGS004606            | Yes             | PGS004952 | Yes                |
| alcohol dependence               | 4        | 1           | 10/10      | PGS002738            | Yes             | -         | No                 |
| ankylosing spondylitis           | 9        | 3           | 10/10      | PGS001268            | Yes             | PGS001268 | Yes                |
| aortic stenosis                  | 8        | 3           | 0/10       | PGS005252            | No              | PGS005252 | No                 |
| cervical carcinoma               | 6        | 1           | 0/10       | PGS001299            | No              | PGS001299 | No                 |
| cutaneous melanoma               | 5        | 1           | 10/10      | PGS003382            | Yes             | PGS003382 | Yes                |
| graves disease                   | 7        | 2           | 10/10      | PGS005265            | Yes             | PGS001042 | No                 |
| hashimoto's thyroiditis          | 3        | 2           | 0/10       | PGS005270            | No              | PGS005270 | No                 |
| hodgkins lymphoma                | 27       | 3           | 10/10      | PGS000639            | Yes             | PGS000874 | No                 |
| hypertrophic cardiomyopathy      | 4        | 3           | 10/10      | PGS004911            | Yes             | PGS000739 | Yes                |
| hypothyroidism                   | 28       | 1           | 0/10       | PGS005218            | No              | PGS005218 | No                 |
| juvenile idiopathic arthritis    | 4        | 1           | 10/10      | PGS000114            | Yes             | PGS000324 | No                 |
| kidney cancer                    | 10       | 1           | 10/10      | PGS004908            | Yes             | PGS004908 | Yes                |
| late-onset alzheimer's disease   | 5        | 1           | 0/10       | PGS000334            | No              | PGS004918 | No                 |
| nodular goiter                   | 7        | 2           | 10/10      | PGS005262            | Yes             | PGS005273 | No                 |
| obesity                          | 10       | 1           | 0/10       | PGS001298            | No              | PGS001298 | No                 |
| obstructive sleep apnea          | 20       | 1           | 10/10      | PGS005220            | Yes             | PGS005219 | No                 |
| open-angle glaucoma              | 5        | 1           | 10/10      | PGS004944            | Yes             | PGS001797 | No                 |
| peripheral vascular disease      | 4        | 1           | 10/10      | PGS005217            | Yes             | PGS005217 | Yes                |
| preeclampsia                     | 3        | 1           | 10/10      | PGS003586            | Yes             | -         | No                 |
| prostate cancer                  | 96       | 1           | 0/10       | PGS005237            | No              | PGS001291 | No                 |
| pulmonary embolism               | 7        | 4           | 10/10      | PGS001279            | Yes             | PGS001279 | Yes                |
| renal carcinoma                  | 8        | 1           | 10/10      | PGS004908            | Yes             | PGS004908 | Yes                |
| skin carcinoma in situ           | 3        | 1           | 10/10      | PGS000471            | Yes             | PGS000471 | Yes                |
| sleep apnea                      | 20       | 1           | 9/10       | PGS005220            | Yes             | PGS005219 | No                 |
| testicular neoplasm              | 14       | 5           | 10/10      | PGS001164            | Yes             | PGS001164 | Yes                |
| thyroid carcinoma                | 32       | 3           | 0/10       | PGS001289            | No              | PGS001289 | No                 |
| uterine carcinoma                | 14       | 4           | 0/10       | PGS001795            | No              | PGS001299 | No                 |
| vitiligo                         | 3        | 1           | 0/10       | PGS001536            | No              | PGS001536 | No                 |


