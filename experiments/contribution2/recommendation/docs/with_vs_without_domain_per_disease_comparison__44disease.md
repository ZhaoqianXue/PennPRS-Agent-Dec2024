# Three-Arm Ablation: Per-Disease Comparison

## Scope

This report is a disease-by-disease comparison across three ablation arms, built from the latest experiment summaries and the underlying AoU benchmark matrices.

Field Type labels in the last column indicate whether a row is part of the current agent input (`Agent Input`) or post-hoc evaluation metadata used only for benchmark/experiment analysis (`Benchmark Only`).

Each disease table includes benchmark-ranked models `Benchmark #1..#5` (or fewer when the disease has fewer than 5 evaluated models), followed by the selections from each ablation arm.
Rows `Hit@1`..`Hit@5` are evaluated over the full disease/trial set; when a disease has fewer than `k` evaluated models, `Top@k` includes all available benchmark-ranked models for that disease.

## Ablation Study Design

This three-arm ablation study isolates the incremental value of each Step 1 tool.
The candidate PGS model set is identical across all three arms; only the information depth changes.

| Arm | Components | Candidate visibility | What it tests |
|-----|-----------|---------------------|---------------|
| Prompt-Only Baseline | GPT-5.2 + system prompt | PGS IDs only (no metadata) | LLM parametric knowledge |
| Catalog Search Only | GPT-5.2 + system prompt + `prs_model_pgscatalog_search` | PGS IDs + full structured metadata | Value of structured catalog search |
| Catalog Search + Domain Knowledge | GPT-5.2 + system prompt + `prs_model_pgscatalog_search` + `prs_model_domain_knowledge` | PGS IDs + metadata + expert rules | Value of curated domain knowledge |

## High-Level Outcome

- Catalog Search + Domain Knowledge `Hit@1`: `18/44 = 40.91%`; `trial_hits = 18/44 = 40.91%`
- Catalog Search + Domain Knowledge `Hit@2`: `22/44 = 50.00%`; `trial_hits = 22/44 = 50.00%`
- Catalog Search + Domain Knowledge `Hit@3`: `26/44 = 59.09%`; `trial_hits = 26/44 = 59.09%`
- Catalog Search + Domain Knowledge `Hit@4`: `29/44 = 65.91%`; `trial_hits = 29/44 = 65.91%`
- Catalog Search + Domain Knowledge `Hit@5`: `30/44 = 68.18%`; `trial_hits = 30/44 = 68.18%`
- Catalog Search Only `Hit@1`: `9/44 = 20.45%`; `trial_hits = 9/44 = 20.45%`
- Catalog Search Only `Hit@2`: `15/44 = 34.09%`; `trial_hits = 15/44 = 34.09%`
- Catalog Search Only `Hit@3`: `23/44 = 52.27%`; `trial_hits = 23/44 = 52.27%`
- Catalog Search Only `Hit@4`: `26/44 = 59.09%`; `trial_hits = 26/44 = 59.09%`
- Catalog Search Only `Hit@5`: `29/44 = 65.91%`; `trial_hits = 29/44 = 65.91%`

## Percentile Hit

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.
- For each percentile threshold, define the tie-aware cutoff rank as `c_q = max(1, ceil(q/100 * M))`.
- A selection counts as `Top q% Hit` if its AoU benchmark rank satisfies `r <= c_q`.
- Denominator: fixed total disease count for modal selections and fixed total trial count for trial selections.
- Tie handling: if the AoU benchmark AUC is tied at cutoff rank `c_q`, all tied models count as `Top q%`.

- Catalog Search + Domain Knowledge `Top 5% Hit`: `21/44 = 47.73%`; `trial_hits = 21/44 = 47.73%`
- Catalog Search + Domain Knowledge `Top 10% Hit`: `24/44 = 54.55%`; `trial_hits = 24/44 = 54.55%`
- Catalog Search + Domain Knowledge `Top 15% Hit`: `27/44 = 61.36%`; `trial_hits = 27/44 = 61.36%`
- Catalog Search + Domain Knowledge `Top 20% Hit`: `28/44 = 63.64%`; `trial_hits = 28/44 = 63.64%`
- Catalog Search + Domain Knowledge `Top 25% Hit`: `29/44 = 65.91%`; `trial_hits = 29/44 = 65.91%`
- Catalog Search Only `Top 5% Hit`: `11/44 = 25.00%`; `trial_hits = 11/44 = 25.00%`
- Catalog Search Only `Top 10% Hit`: `14/44 = 31.82%`; `trial_hits = 14/44 = 31.82%`
- Catalog Search Only `Top 15% Hit`: `21/44 = 47.73%`; `trial_hits = 21/44 = 47.73%`
- Catalog Search Only `Top 20% Hit`: `21/44 = 47.73%`; `trial_hits = 21/44 = 47.73%`
- Catalog Search Only `Top 25% Hit`: `25/44 = 56.82%`; `trial_hits = 25/44 = 56.82%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean r / M = 0.3077` (44 modal selections); `trial mean r / M = 0.3077` (44 trials)
- Catalog Search Only: `mean r / M = 0.3648` (44 modal selections); `trial mean r / M = 0.3648` (44 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean (M - r) / M = 0.6923` (44 modal selections); `trial mean (M - r) / M = 0.6923` (44 trials)
- Catalog Search Only: `mean (M - r) / M = 0.6352` (44 modal selections); `trial mean (M - r) / M = 0.6352` (44 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Catalog Search + Domain Knowledge: `mean NRS = 0.7487` (44 modal selections); `trial mean NRS = 0.7487` (44 trials)
- Catalog Search Only: `mean NRS = 0.6863` (44 modal selections); `trial mean NRS = 0.6863` (44 trials)

## Per-Disease Tables

### type 2 diabetes mellitus

Candidate pool: `146` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004838 | PGS004840 | PGS005246 | PGS005329 | PGS005324 | PGS002308 | PGS002308 | Agent Input |
| AoU benchmark rank | 1/146 | 2/146 | 3/146 | 4/146 | 5/146 | 9/146 | 9/146 | Benchmark Only |
| AoU benchmark AUC | 0.6669 | 0.6669 | 0.6614 | 0.6546 | 0.6537 | 0.6472 | 0.6472 | Benchmark Only |
| Hit@1 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Type 2 diabetes (T2D) | Type 2 diabetes (T2D) | Type 2 diabetes (T2D) | Type 2 Diabetes Mellitus | Type 2 Diabetes Mellitus | Type 2 diabetes (T2D) | Type 2 diabetes (T2D) | Agent Input |
| trait_efo | type 2 diabetes mellitus | type 2 diabetes mellitus | type 2 diabetes mellitus | type 2 diabetes mellitus | type 2 diabetes mellitus | type 2 diabetes mellitus | type 2 diabetes mellitus | Agent Input |
| phenotyping_reported | Prediabetes | Type 2 diabetes | Type 2 diabetes | Unknown | Incident Type 2 Diabetes Mellitus | Type 2 diabetes | Type 2 diabetes | Agent Input |
| method_name | PRSmix | PRSmixPlus | PRS-CSx | PRS-CSx | PRS-CSx | PRS-CSx | PRS-CSx | Agent Input |
| performance_metrics.selected_performance_id | PPM022872 | PPM021065 | PPM022727 | N/A | PPM023076 | PPM013064 | PPM013064 | Agent Input |
| performance_metrics.selected_validation_ancestry | Greater Middle Eastern (Middle Eastern, North African or Persian) | South Asian | European | N/A | Hispanic or Latin American | European | European | Agent Input |
| performance_metrics.record_count | 3 | 1 | 1 | 0 | 1 | 12 | 12 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6590 | N/A | 0.7860 | N/A | N/A | 0.7930 | 0.7930 | Agent Input |
| performance_metrics.full_model_r2 | 0.0990 | 0.0650 | N/A | N/A | N/A | 0.0920 | 0.0920 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.659, 'ci_lower': 0.644, 'ci_upper': 0.675} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.786, 'ci_lower': 0.779, 'ci_upper': 0.793} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.793} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.793} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.099} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.065, 'ci_lower': 0.055, 'ci_upper': 0.075} | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.092} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.092} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.374, 'ci_lower': 1.283, 'ci_upper': 1.471} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.01, 'ci_lower': 1.94, 'ci_upper': 2.09} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.77, 'ci_lower': 2.44, 'ci_upper': 3.13} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.96, 'ci_lower': 1.91, 'ci_upper': 2.02} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.96, 'ci_lower': 1.91, 'ci_upper': 2.02} | Agent Input |
| validation_sample_size | n=4,534 | n=8,837 | n=22,063 | N/A | n=12,309 | n=54,793 | n=54,793 | Agent Input |
| samples_training | n=35,350 | n=35,350 | N/A | n=38,745 | n=38,745 | N/A | N/A | Agent Input |
| ancestry_distribution | DEV: SAS (100%) / EVAL: GME (67%), SAS (33%) | DEV: SAS (100%) / EVAL: SAS (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / DEV: NR (6%), AFR (5%), AMR (4%), ASN (2%), EUR (84%), OTH (10%) | GWAS: MAE (100%) / DEV: NR (6%), AFR (5%), AMR (4%), ASN (2%), EUR (84%), OTH (10%) / EVAL: AMR (100%) | GWAS: AFR (2%), EAS (16%), EUR (82%) / EVAL: AFR (42%), AMR (8%), EAS (25%), EUR (8%), GME (17%) | GWAS: AFR (2%), EAS (16%), EUR (82%) / EVAL: AFR (42%), AMR (8%), EAS (25%), EUR (8%), GME (17%) | Agent Input |
| training_development_cohorts | G&H | G&H | N/A | MGBB | MGBB | N/A | N/A | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Polygenic risk score for type 2 diabetes shows context-dependent effects across populations. | Obstructive sleep apnea mediates genetic risk of Diabetes Mellitus in Hispanic and Latino communities. | Obstructive sleep apnea mediates genetic risk of Diabetes Mellitus in Hispanic and Latino communities. | Development and validation of a trans-ancestry polygenic risk score for type 2 diabetes in diverse populations. | Development and validation of a trans-ancestry polygenic risk score for type 2 diabetes in diverse populations. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | Nat Commun | Commun Med (Lond) | Commun Med (Lond) | Genome Med | Genome Med | Agent Input |
| date_release | 2024-03-28 | 2024-03-28 | 2025-10-06 | 2025-11-10 | 2025-11-10 | 2022-07-05 | 2022-07-05 | Agent Input |
| variants_number | 6586458 | 6586458 | 1111848 | 1112468 | 1279733 | 1259754 | 1259754 | Agent Input |
| covariates | sex, baseline age, BMI, PCs1-10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, BMI, sub-study, and first 10 PCs | Unknown | age, sex, BMI, study center, and genetic PCs | age, sex, top 10 PCs, study site | age, sex, top 10 PCs, study site | Agent Input |


### breast carcinoma

Candidate pool: `134` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004579 | PGS000508 | PGS004025 | PGS004053 | PGS000335 | PGS004153 | PGS004153 | Agent Input |
| AoU benchmark rank | 1/134 | 2/134 | 3/134 | 4/134 | 5/134 | 6/134 | 6/134 | Benchmark Only |
| AoU benchmark AUC | 0.6358 | 0.6335 | 0.6332 | 0.6326 | 0.6319 | 0.6310 | 0.6310 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Breast cancer | Breast cancer (female) | Breast cancer | Breast cancer | Breast cancer | Breast cancer | Breast cancer | Agent Input |
| trait_efo | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | Agent Input |
| phenotyping_reported | Breast cancer | Breast cancer [female] | Breast cancer | Breast cancer | Breast cancer | Breast cancer | Breast cancer | Agent Input |
| method_name | PRS-CS | PRS-CS | LDpred2-auto | megaprs.auto | PRS-CS | UKBB-EUR.MultiPRS.CV | UKBB-EUR.MultiPRS.CV | Agent Input |
| performance_metrics.selected_performance_id | PPM020694 | PPM001193 | PPM019402 | PPM019414 | PPM000902 | PPM019384 | PPM019384 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 6 | 6 | 13 | 6 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.6520 | 0.6559 | 0.6500 | N/A | 0.6601 | 0.6601 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0548 | 0.0691 | 0.0639 | N/A | 0.0727 | 0.0727 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.652, 'ci_lower': 0.645, 'ci_upper': 0.658} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65593151, 'ci_lower': 0.65157997, 'ci_upper': 0.66028305} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6499628, 'ci_lower': 0.64560075, 'ci_upper': 0.65432486} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66011868, 'ci_lower': 0.65578171, 'ci_upper': 0.66445565} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66011868, 'ci_lower': 0.65578171, 'ci_upper': 0.66445565} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0548} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0805} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.38, 'ci_lower': 3.79, 'ci_upper': 5.07} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.06912671, 'ci_lower': 0.06491623, 'ci_upper': 0.07286341} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.063865, 'ci_lower': 0.05988493, 'ci_upper': 0.0675063} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07267078, 'ci_lower': 0.06845349, 'ci_upper': 0.07630969} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07267078, 'ci_lower': 0.06845349, 'ci_upper': 0.07630969} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.79} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.756, 'ci_lower': 1.709, 'ci_upper': 1.804} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.563, 'se': 0.0138} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.77035216, 'ci_lower': 1.74117276, 'ci_upper': 1.80002055} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.57117849, 'ci_lower': 0.55455889, 'ci_upper': 0.58779808} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.72899314, 'ci_lower': 1.70061022, 'ci_upper': 1.75784976} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.54753924, 'ci_lower': 0.53098714, 'ci_upper': 0.56409133} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.71, 'ci_lower': 1.68, 'ci_upper': 1.75} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.79574426, 'ci_lower': 1.76611997, 'ci_upper': 1.82586546} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.58541957, 'ci_lower': 0.56878504, 'ci_upper': 0.6020541} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.79574426, 'ci_lower': 1.76611997, 'ci_upper': 1.82586546} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.58541957, 'ci_lower': 0.56878504, 'ci_upper': 0.6020541} | Agent Input |
| validation_sample_size | n=190,879 | n=68,531 | n=217,530 | n=217,530 | n=122,978 | n=217,530 | n=217,530 | Agent Input |
| samples_training | N/A | n=68,451 | n=12,483 | n=12,483 | N/A | n=12,483 | n=12,483 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | Agent Input |
| training_development_cohorts | N/A | UKB | UKB | UKB | N/A | UKB | UKB | Agent Input |
| publication.title | High-Resolution Genotyping of Formalin-Fixed Tissue Accurately Estimates Polygenic Risk Scores in Human Diseases. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | The role of polygenic risk and susceptibility genes in breast cancer over the course of life | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Agent Input |
| publication.journal | Lab Invest | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Nat Commun | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2024-02-20 | 2020-12-15 | 2023-12-19 | 2023-12-19 | 2020-12-15 | 2023-12-19 | 2023-12-19 | Agent Input |
| variants_number | 1088163 | 1120410 | 1041298 | 869407 | 1079089 | 1133268 | 1133268 | Agent Input |
| covariates | Unknown | age, sex, batch PCs 1-4 | 0 | 0 | 10 ancestry PCs, batch, age as time scale | 0 | 0 | Agent Input |


### prostate carcinoma

Candidate pool: `89` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000566 | PGS000044 | PGS000592 | PGS002793 | PGS000576 | PGS004155 | PGS004155 | Agent Input |
| AoU benchmark rank | 1/89 | 2/89 | 3/89 | 4/89 | 5/89 | 26/89 | 26/89 | Benchmark Only |
| AoU benchmark AUC | 0.6550 | 0.6295 | 0.5748 | 0.5665 | 0.5641 | 0.5492 | 0.5492 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Prostate cancer | Prostate cancer | Prostate cancer | Prostate cancer | Prostate cancer | Prostate cancer | Prostate cancer | Agent Input |
| trait_efo | prostate carcinoma | prostate carcinoma | prostate carcinoma | prostate carcinoma | prostate carcinoma | prostate carcinoma | prostate carcinoma | Agent Input |
| phenotyping_reported | Cancer of prostate | aggressive prostate cancer (Gleason score ⩾7) | Cancer of prostate | Prostate cancer risk | Cancer of prostate | Prostate cancer | Prostate cancer | Agent Input |
| method_name | PRS-CS | Known susceptibility loci (genome-wide significant SNPs) | lassosum | Genome-wide significant SNPs | lassosum | UKBB-EUR.MultiPRS.CV | UKBB-EUR.MultiPRS.CV | Agent Input |
| performance_metrics.selected_performance_id | PPM001251 | PPM000105 | PPM001277 | PPM015450 | PPM001261 | PPM019534 | PPM019534 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | East Asian | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 1 | 1 | 1 | 6 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5910 | N/A | 0.6160 | N/A | 0.6070 | 0.7049 | 0.7049 | Agent Input |
| performance_metrics.full_model_r2 | 0.0245 | N/A | 0.0408 | N/A | 0.0358 | 0.1280 | 0.1280 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.591, 'ci_lower': 0.573, 'ci_upper': 0.609} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.616, 'ci_lower': 0.598, 'ci_upper': 0.635} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.607, 'ci_lower': 0.589, 'ci_upper': 0.627} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7049161, 'ci_lower': 0.70043717, 'ci_upper': 0.70939503} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7049161, 'ci_lower': 0.70043717, 'ci_upper': 0.70939503} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0245} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.152} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.85, 'ci_lower': 1.76, 'ci_upper': 4.62} | {'name_long': 'OR (above vs. below 50th percentile of PRS)', 'name_short': 'OR (above vs. below 50th percentile of PRS)', 'estimate': 1.56, 'ci_lower': 1.15, 'ci_upper': 2.1} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0408} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.15} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.55, 'ci_lower': 1.55, 'ci_upper': 4.2} | {'name_long': 'Odds Ratio (OR, top vs average percentile)', 'name_short': 'Odds Ratio (OR, top vs average percentile)', 'estimate': 2.87, 'ci_lower': 1.29, 'ci_upper': 6.4} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0358} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.151} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.46, 'ci_lower': 1.5, 'ci_upper': 4.01} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.12803272, 'ci_lower': 0.12275071, 'ci_upper': 0.13385339} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.12803272, 'ci_lower': 0.12275071, 'ci_upper': 0.13385339} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.393, 'ci_lower': 1.3, 'ci_upper': 1.493} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.332, 'se': 0.0352} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.537, 'ci_lower': 1.433, 'ci_upper': 1.648} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.43, 'se': 0.0357} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.489, 'ci_lower': 1.39, 'ci_upper': 1.596} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.398, 'se': 0.0353} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.16612832, 'ci_lower': 2.12587867, 'ci_upper': 2.20714003} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.77294139, 'ci_lower': 0.75418521, 'ci_upper': 0.79169757} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.16612832, 'ci_lower': 2.12587867, 'ci_upper': 2.20714003} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.77294139, 'ci_lower': 0.75418521, 'ci_upper': 0.79169757} | Agent Input |
| validation_sample_size | n=5,607 | n=4,967 | n=5,607 | n=1,190 | n=5,607 | n=171,474 | n=171,474 | Agent Input |
| samples_training | n=5,650 | N/A | n=5,650 | n=109,323 | n=5,650 | n=9,671 | n=9,671 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (5%), EUR (95%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (2%), AMR (40%), EAS (1%), EUR (92%), MAE (3%) / DEV: AFR (3%), EAS (1%), EUR (96%) / EVAL: EAS (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | Agent Input |
| training_development_cohorts | MGI | ICR IGD PLCO ProtecT UKGPCS deCODE | MGI | AAPC BCFR BFBOCC BRICOH CBCS CIMBA CNIO CONSIT Chicago DEMOKRITOS DKFZ EMBRACE FCCC G-FaST GC-HBOC GEMO HCSC HEBCS HEBON HUNBOCS HVH ICO ICR IGD ILUH IOVHBOCS IPOBCS MAYO MSKCC MUV NCI OCGN OSU OUH PBCS PLCO ProtecT SWE-BRCA UKB UKGPCS UPENN UPITT VFCTG deCODE kConFab | MGI | UKB | UKB | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Reducing overdiagnosis by polygenic risk-stratified screening: findings from the Finnish section of the ERSPC. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Application of European-specific polygenic risk scores for predicting prostate cancer risk in different ancestry populations. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Agent Input |
| publication.journal | Am J Hum Genet | Br J Cancer | Am J Hum Genet | Prostate | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2020-12-15 | 2019-12-18 | 2020-12-15 | 2022-09-29 | 2020-12-15 | 2023-12-19 | 2023-12-19 | Agent Input |
| variants_number | 1111494 | 66 | 1334 | 82 | 905 | 1139693 | 1139693 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | Unknown | age, sex, batch PCs 1-4 | disease diagnostic age or age at recruitment, subgroups and 10 principal components | age, sex, batch PCs 1-4 | 0 | 0 | Agent Input |


### coronary artery disease

Candidate pool: `77` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003725 | PGS004696 | PGS004697 | PGS003726 | PGS004746 | PGS003725 | PGS003725 | Agent Input |
| AoU benchmark rank | 1/77 | 2/77 | 3/77 | 4/77 | 5/77 | 1/77 | 1/77 | Benchmark Only |
| AoU benchmark AUC | 0.6177 | 0.6120 | 0.6101 | 0.6088 | 0.6073 | 0.6177 | 0.6177 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Coronary artery disease | Coronary heart disease | Coronary heart disease | Coronary artery disease | Coronary artery disease | Coronary artery disease | Coronary artery disease | Agent Input |
| trait_efo | coronary artery disorder | coronary artery disorder | coronary artery disorder | coronary artery disorder | coronary artery disorder | coronary artery disorder | coronary artery disorder | Agent Input |
| phenotyping_reported | Coronary artery disease | Incident coronary heart disease | Incident coronary heart disease | Coronary artery disease | Coronary artery disease | Coronary artery disease | Coronary artery disease | Agent Input |
| method_name | LDpred2 | PRS-CSx | PRS-CSx | LDpred2 | PRSmixPlus | LDpred2 | LDpred2 | Agent Input |
| performance_metrics.selected_performance_id | PPM018419 | PPM020904 | PPM020903 | PPM018427 | PPM020971 | PPM018419 | PPM018419 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | South Asian | European | European | Agent Input |
| performance_metrics.record_count | 11 | 5 | 5 | 4 | 1 | 11 | 11 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.7740 | 0.7730 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0200 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.774} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.773} | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.02, 'ci_lower': 0.014, 'ci_upper': 0.026} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.75, 'ci_lower': 1.71, 'ci_upper': 1.78} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.14, 'ci_lower': 2.1, 'ci_upper': 2.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65, 'ci_lower': 1.59, 'ci_upper': 1.71} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.55, 'ci_lower': 1.5, 'ci_upper': 1.6} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.73, 'ci_lower': 1.69, 'ci_upper': 1.76} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.75, 'ci_lower': 1.71, 'ci_upper': 1.78} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.14, 'ci_lower': 2.1, 'ci_upper': 2.19} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.75, 'ci_lower': 1.71, 'ci_upper': 1.78} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.14, 'ci_lower': 2.1, 'ci_upper': 2.19} | Agent Input |
| validation_sample_size | n=308,264 | n=52,702 | n=52,702 | n=308,264 | n=8,837 | n=308,264 | n=308,264 | Agent Input |
| samples_training | n=116,649 | n=87,724 | n=56,359 | n=116,649 | n=35,350 | n=116,649 | n=116,649 | Agent Input |
| ancestry_distribution | GWAS: MAE (100%) / DEV: EUR (100%) / EVAL: AFR (22%), AMR (11%), EAS (11%), EUR (22%), MAE (11%), SAS (22%) | GWAS: AFR (7%), AMR (3%), EAS (19%), EUR (71%) / DEV: AFR (19%), AMR (11%), EUR (64%), MAO (5%) / EVAL: AFR (20%), AMR (20%), EAS (20%), EUR (20%), SAS (20%) | GWAS: AFR (4%), AMR (2%), EAS (11%), EUR (83%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (20%), EAS (20%), EUR (20%), SAS (20%) | GWAS: MAE (100%) / DEV: EUR (100%) / EVAL: AFR (25%), EAS (25%), EUR (25%), SAS (25%) | DEV: SAS (100%) / EVAL: SAS (100%) | GWAS: MAE (100%) / DEV: EUR (100%) / EVAL: AFR (22%), AMR (11%), EAS (11%), EUR (22%), MAE (11%), SAS (22%) | GWAS: MAE (100%) / DEV: EUR (100%) / EVAL: AFR (22%), AMR (11%), EAS (11%), EUR (22%), MAE (11%), SAS (22%) | Agent Input |
| training_development_cohorts | AGENT2D BBJ CARDIoGRAMplusC4D DIAMANTE FinnGen G&H GBMI GIANT GLGC MEGASTROKE MVP UKB | BBJ CARDIoGRAMplusC4D MVP UKB | BBJ CARDIoGRAMplusC4D MVP UKB | BBJ CARDIoGRAMplusC4D FinnGen G&H MVP UKB | G&H | AGENT2D BBJ CARDIoGRAMplusC4D DIAMANTE FinnGen G&H GBMI GIANT GLGC MEGASTROKE MVP UKB | AGENT2D BBJ CARDIoGRAMplusC4D DIAMANTE FinnGen G&H GBMI GIANT GLGC MEGASTROKE MVP UKB | Agent Input |
| publication.title | A multi-ancestry polygenic risk score improves risk prediction for coronary artery disease. | Multi-Ancestry Polygenic Risk Score for Coronary Heart Disease Based on an Ancestrally Diverse Genome-Wide Association Study and Population-Specific Optimization. | Multi-Ancestry Polygenic Risk Score for Coronary Heart Disease Based on an Ancestrally Diverse Genome-Wide Association Study and Population-Specific Optimization. | A multi-ancestry polygenic risk score improves risk prediction for coronary artery disease. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | A multi-ancestry polygenic risk score improves risk prediction for coronary artery disease. | A multi-ancestry polygenic risk score improves risk prediction for coronary artery disease. | Agent Input |
| publication.journal | Nat Med | Circ Genom Precis Med | Circ Genom Precis Med | Nat Med | Cell Genom | Nat Med | Nat Med | Agent Input |
| date_release | 2023-07-05 | 2024-03-18 | 2024-03-18 | 2023-07-05 | 2024-03-28 | 2023-07-05 | 2023-07-05 | Agent Input |
| variants_number | 1296172 | 1289980 | 1120251 | 1296172 | 6483064 | 1296172 | 1296172 | Agent Input |
| covariates | age, sex and the first ten principal components of genetic ancestry | age, sex, 10 PCs | age, sex, 10 PCs | age, sex and the first ten principal components of genetic ancestry | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex and the first ten principal components of genetic ancestry | age, sex and the first ten principal components of genetic ancestry | Agent Input |


### hypertension

Candidate pool: `65` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004786 | PGS004788 | PGS002335 | PGS002701 | PGS002998 | PGS004236 | PGS004236 | Agent Input |
| AoU benchmark rank | 1/65 | 2/65 | 3/65 | 4/65 | 5/65 | 31/65 | 31/65 | Benchmark Only |
| AoU benchmark AUC | 0.6377 | 0.6377 | 0.6227 | 0.6225 | 0.6172 | 0.5683 | 0.5683 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Agent Input |
| trait_efo | hypertensive disorder | hypertensive disorder | hypertensive disorder | hypertensive disorder | hypertensive disorder | hypertensive disorder | hypertensive disorder | Agent Input |
| phenotyping_reported | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Prevelant hypertension | Prevelant hypertension | Agent Input |
| method_name | PRSmix | PRSmixPlus | BOLT-LMM | SBayesR | PRS-CS | PRSsum | PRSsum | Agent Input |
| performance_metrics.selected_performance_id | PPM021011 | PPM021013 | PPM013198 | PPM014662 | PPM015875 | PPM020255 | PPM020255 | Agent Input |
| performance_metrics.selected_validation_ancestry | South Asian | South Asian | European | European | European | European, African American or Afro-Caribbean, Hispanic or Latin American, Asian unspecified | European, African American or Afro-Caribbean, Hispanic or Latin American, Asian unspecified | Agent Input |
| performance_metrics.record_count | 1 | 1 | 4 | 4 | 1 | 3 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | 0.6300 | 0.7640 | 0.7640 | Agent Input |
| performance_metrics.full_model_r2 | 0.0220 | 0.0270 | 0.0527 | 0.0506 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63, 'ci_lower': 0.622, 'ci_upper': 0.639} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.764, 'ci_lower': 0.751, 'ci_upper': 0.777} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.764, 'ci_lower': 0.751, 'ci_upper': 0.777} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.022, 'ci_lower': 0.016, 'ci_upper': 0.028} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.027, 'ci_lower': 0.02, 'ci_upper': 0.033} | {'name_long': 'Incremental R2 (full model vs. covariates alone)', 'name_short': 'Incremental R2 (full model vs. covariates alone)', 'estimate': 0.0527} | {'name_long': 'Incremental R2 (full model vs. covariates alone)', 'name_short': 'Incremental R2 (full model vs. covariates alone)', 'estimate': 0.0506} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.67, 'ci_lower': 1.617, 'ci_upper': 1.725} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.513, 'se': 0.0165} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.1, 'ci_lower': 1.99, 'ci_upper': 2.21} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.1, 'ci_lower': 1.99, 'ci_upper': 2.21} | Agent Input |
| validation_sample_size | n=8,837 | n=8,837 | n=43,392 | n=43,392 | n=23,316 | n=39,035 | n=39,035 | Agent Input |
| samples_training | n=35,350 | n=35,350 | N/A | N/A | n=23,307 | n=10,314 | n=10,314 | Agent Input |
| ancestry_distribution | DEV: SAS (100%) / EVAL: SAS (100%) | DEV: SAS (100%) / EVAL: SAS (100%) | GWAS: EUR (100%) / EVAL: AFR (25%), EAS (25%), EUR (25%), SAS (25%) | GWAS: EUR (100%) / EVAL: AFR (25%), EAS (25%), EUR (25%), SAS (25%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (12%), AMR (4%), ASN (90%), EUR (41%), MAE (42%), OTH (50%) / DEV: NR (6%), AFR (27%), AMR (41%), ASN (2%), EUR (24%) / EVAL: MAE (100%) | GWAS: AFR (12%), AMR (4%), ASN (90%), EUR (41%), MAE (42%), OTH (50%) / DEV: NR (6%), AFR (27%), AMR (41%), ASN (2%), EUR (24%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | G&H | G&H | UKB | UKB | MGI UKB | BioMe MVP UKB | BioMe MVP UKB | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Leveraging fine-mapping and multipopulation training data to improve cross-population polygenic risk scores. | Leveraging fine-mapping and multipopulation training data to improve cross-population polygenic risk scores. | ExPRSweb: An online repository with polygenic risk scores for common health-related exposures. | A multi-ethnic polygenic risk score is associated with hypertension prevalence and progression throughout adulthood. | A multi-ethnic polygenic risk score is associated with hypertension prevalence and progression throughout adulthood. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | Nat Genet | Nat Genet | Am J Hum Genet | Nat Commun | Nat Commun | Agent Input |
| date_release | 2024-03-28 | 2024-03-28 | 2022-06-09 | 2022-06-09 | 2022-11-23 | 2023-12-15 | 2023-12-15 | Agent Input |
| variants_number | 6622611 | 6622611 | 1109311 | 973782 | 1113832 | 398805 | 398805 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, age*sex, assessment center, genotyping array, 10 PCs | age, sex, age*sex, assessment center, genotyping array, 10 PCs | SEX,AGE,Batch,PC1,PC2,PC3,PC4 | sex, age, age2, study site, race/ethnic background, smoking status, BMI, and 11 ancestral principal components | sex, age, age2, study site, race/ethnic background, smoking status, BMI, and 11 ancestral principal components | Agent Input |


### asthma

Candidate pool: `63` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004724 | PGS004726 | PGS001782 | PGS001787 | PGS004877 | PGS001782 | PGS001344 | Agent Input |
| AoU benchmark rank | 1/63 | 2/63 | 3/63 | 4/63 | 5/63 | 3/63 | 14/63 | Benchmark Only |
| AoU benchmark AUC | 0.6043 | 0.6043 | 0.5984 | 0.5925 | 0.5912 | 0.5984 | 0.5739 | Benchmark Only |
| Hit@1 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Asthma | Asthma | Asthma | Asthma | Asthma | Asthma | Asthma (diagnosed by doctor) | Agent Input |
| trait_efo | asthma | asthma | asthma | asthma | asthma | asthma | asthma | Agent Input |
| phenotyping_reported | Asthma | Asthma | Asthma | Asthma | Incident Asthma | Asthma | Asthma diagnosed by doctor | Agent Input |
| method_name | PRSmix | PRSmixPlus | PRS-CS-auto | PRS-CS-auto | megaprs.auto | PRS-CS-auto | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM020949 | PPM020951 | PPM009311 | PPM009291 | PPM021200 | PPM009311 | PPM009205 | Agent Input |
| performance_metrics.selected_validation_ancestry | South Asian | South Asian | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 6 | 7 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.6427 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0488 | 0.0352 | N/A | 0.0488 | 0.0569 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.6590 | 0.6400 | 0.6100 | 0.6590 | 0.6536 | Agent Input |
| performance_metrics.full_model_r2 | 0.0650 | 0.0690 | N/A | N/A | N/A | N/A | 0.0673 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.0904 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.659} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.61, 'ci_lower': 0.61, 'ci_upper': 0.62} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.659} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65364, 'ci_lower': 0.64713, 'ci_upper': 0.66016} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.065, 'ci_lower': 0.055, 'ci_upper': 0.075} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.069, 'ci_lower': 0.059, 'ci_upper': 0.08} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.048844} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.035168} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.048844} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.06727} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.09037} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05689} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64265, 'ci_lower': 0.63609, 'ci_upper': 0.64921} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.42, 'ci_lower': 1.41, 'ci_upper': 1.44} | N/A | N/A | Agent Input |
| validation_sample_size | n=8,837 | n=8,837 | n=7,128 | n=351,578 | n=412,090 | n=7,128 | n=53,936 | Agent Input |
| samples_training | n=35,350 | n=35,350 | N/A | N/A | n=404 | N/A | n=216,121 | Agent Input |
| ancestry_distribution | DEV: SAS (100%) / EVAL: SAS (100%) | DEV: SAS (100%) / EVAL: SAS (100%) | GWAS: AFR (2%), ASN (2%), EAS (19%), EUR (76%), GME (9%), OTH (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (25%), EUR (70%), OTH (1%) / EVAL: AFR (17%), ASN (17%), EAS (17%), EUR (17%), GME (17%), OTH (17%) | GWAS: AFR (2%), AMR (30%), EAS (100%), EUR (97%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (19%), EUR (76%), GME (9%), OTH (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | G&H | G&H | BBJ BioMe BioVU CCPM CKB EB FinnGen GS:SFHS HUNT MGBB MGI TWB UCLA UKB | BBJ BioMe BioVU CCPM CKB EB FinnGen GS:SFHS HUNT MGBB MGI TWB UCLA | 1000G | BBJ BioMe BioVU CCPM CKB EB FinnGen GS:SFHS HUNT MGBB MGI TWB UCLA UKB | UKB | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | Cell Genom | Cell Genom | Nat Commun | Cell Genom | PLoS Genet | Agent Input |
| date_release | 2024-03-28 | 2024-03-28 | 2022-09-08 | 2022-09-08 | 2024-06-27 | 2022-09-08 | 2021-10-21 | Agent Input |
| variants_number | 2342250 | 2342250 | 884043 | 909990 | 870454 | 884043 | 6139 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | sex,age, 20PCs | sex,age,age2,age*sex,age^2*sex, 20PCs | PCs 1-10 | sex,age, 20PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### alzheimer disease

Candidate pool: `47` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001348 | PGS001349 | PGS004289 | PGS000945 | PGS003956 | PGS004034 | PGS004285 | Agent Input |
| AoU benchmark rank | 1/47 | 2/47 | 3/47 | 4/47 | 5/47 | 29/47 | 32/47 | Benchmark Only |
| AoU benchmark AUC | 0.5910 | 0.5839 | 0.5818 | 0.5775 | 0.5722 | 0.4708 | 0.4619 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Alzheimer's disease (algorithmically-defined) | Alzheimer's disease (time-to-event) | Alzheimer's disease | Dementia in Alzheimer's disease (time-to-event) | Alzheimer's disease | Alzheimer's disease | Alzheimer's disease | Agent Input |
| trait_efo | Alzheimer disease | Alzheimer disease | Alzheimer disease | dementia, Alzheimer disease | Alzheimer disease | Alzheimer disease | Alzheimer disease | Agent Input |
| phenotyping_reported | AD alzheimer's disease | TTE alzheimer's disease | Alzheimer's disease | TTE dementia in alzheimer's disease | Mild cognitive impairment | AD | Alzheimer's disease | Agent Input |
| method_name | snpnet | snpnet | GenoBoost | snpnet | PRSice-2 | LDpred2-auto | GenoBoost | Agent Input |
| performance_metrics.selected_performance_id | PPM009224 | PPM009228 | PPM020357 | PPM007554 | PPM019087 | PPM019929 | PPM020353 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Hispanic or Latin American | European | European | Agent Input |
| performance_metrics.record_count | 4 | 4 | 1 | 4 | 2 | 3 | 1 | Agent Input |
| performance_metrics.auc | 0.7235 | 0.7124 | N/A | 0.7527 | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | 0.0568 | 0.0527 | N/A | 0.0654 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8686 | 0.8666 | 0.8316 | 0.8916 | N/A | 0.6237 | 0.8336 | Agent Input |
| performance_metrics.full_model_r2 | 0.1517 | 0.1542 | 0.0408 | 0.1668 | N/A | 0.0349 | 0.0421 | Agent Input |
| performance_metrics.incremental_auc | 0.0529 | 0.0466 | N/A | 0.0546 | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8686, 'ci_lower': 0.84242, 'ci_upper': 0.89478} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8666, 'ci_lower': 0.84246, 'ci_upper': 0.89075} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.831624672285122} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8916, 'ci_lower': 0.86249, 'ci_upper': 0.9207} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62370319, 'ci_lower': 0.61877662, 'ci_upper': 0.62862975} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.833604804388662} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1517} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05292} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05685} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.72349, 'ci_lower': 0.67813, 'ci_upper': 0.76886} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.15418} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04665} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05271} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.71238, 'ci_lower': 0.66844, 'ci_upper': 0.75632} | {'name_long': 'Covariate-adjusted pseudo-R2', 'name_short': 'Covariate-adjusted pseudo-R2', 'estimate': 0.040761373980392} {'name_long': 'AUPRC', 'name_short': 'AUPRC', 'estimate': 0.831624672285122} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.16679} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05458} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.06543} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.75273, 'ci_lower': 0.69847, 'ci_upper': 0.80699} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03490039, 'ci_lower': 0.03207661, 'ci_upper': 0.03776512} | {'name_long': 'Covariate-adjusted pseudo-R2', 'name_short': 'Covariate-adjusted pseudo-R2', 'estimate': 0.0420988165670099} {'name_long': 'AUPRC', 'name_short': 'AUPRC', 'estimate': 0.833604804388662} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.14, 'ci_lower': 1.02, 'ci_upper': 1.28} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53210388, 'ci_lower': 1.50892339, 'ci_upper': 1.55564048} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.42664188, 'ci_lower': 0.41139641, 'ci_upper': 0.44188734} | N/A | Agent Input |
| validation_sample_size | n=67,425 | n=67,425 | n=67,428 | n=67,425 | n=4,189 | n=389,004 | n=67,428 | Agent Input |
| samples_training | n=269,704 | n=269,704 | n=269,710 | n=269,704 | N/A | N/A | n=269,710 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | GWAS: AFR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | N/A | N/A | UKB | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | A polygenic score method boosted by non-additive models. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | A polygenic risk score for Alzheimer's disease constructed using APOE-region variants has stronger association than APOE alleles with mild cognitive impairment in Hispanic/Latino adults in the U.S. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | A polygenic score method boosted by non-additive models. | Agent Input |
| publication.journal | PLoS Genet | PLoS Genet | Nat Commun | PLoS Genet | Alzheimers Res Ther | Am J Hum Genet | Nat Commun | Agent Input |
| date_release | 2021-10-21 | 2021-10-21 | 2024-06-12 | 2021-10-21 | 2023-10-17 | 2023-12-19 | 2024-06-12 | Agent Input |
| variants_number | 15 | 6 | 40 | 26 | 157 | 1046908 | 20 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, PC1-10 | age, sex, UKB array type, Genotype PCs | age at the HCHS/SOL baseline visit, time from HCHS/SOL baseline to the SOL-INCA visit, sex, study center, 5 principal components, and APOE-ϵ4 and APOE-ϵ2 allele counts | 0 | age, sex, PC1-10 | Agent Input |


### atrial fibrillation

Candidate pool: `46` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005313 | PGS005287 | PGS005289 | PGS005288 | PGS005291 | PGS005313 | PGS005313 | Agent Input |
| AoU benchmark rank | 1/46 | 2/46 | 3/46 | 4/46 | 5/46 | 1/46 | 1/46 | Benchmark Only |
| AoU benchmark AUC | 0.6256 | 0.6178 | 0.6156 | 0.6144 | 0.6116 | 0.6256 | 0.6256 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Atrial fibrillation | Atrial fibrillation | Atrial fibrillation | Atrial fibrillation | Atrial fibrillation | Atrial fibrillation | Atrial fibrillation | Agent Input |
| trait_efo | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | Agent Input |
| phenotyping_reported | atrial fibrillation | Prevalent atrial fibrillation or flutter | Prevalent atrial fibrillation or flutter | Prevalent atrial fibrillation or flutter | Prevalent atrial fibrillation or flutter | atrial fibrillation | atrial fibrillation | Agent Input |
| method_name | PRS-CSx | LDpred2 | LDpred2 | LDpred2 | LDpred2 | PRS-CSx | PRS-CSx | Agent Input |
| performance_metrics.selected_performance_id | PPM023035 | PPM022995 | PPM022997 | PPM022996 | PPM022999 | PPM023035 | PPM023035 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African unspecified, South Asian, East Asian, Hispanic or Latin American, Other | European | European | European | European | European, African unspecified, South Asian, East Asian, Hispanic or Latin American, Other | European, African unspecified, South Asian, East Asian, Hispanic or Latin American, Other | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7800 | 0.7030 | 0.6813 | 0.6900 | 0.6933 | 0.7800 | 0.7800 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.1469 | 0.1255 | 0.1154 | 0.1177 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78, 'ci_lower': 0.778, 'ci_upper': 0.783} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.703} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6813004} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.689964} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6933057} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78, 'ci_lower': 0.778, 'ci_upper': 0.783} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78, 'ci_lower': 0.778, 'ci_upper': 0.783} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.14693} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.12547} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11543} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11768} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.82, 'ci_lower': 1.79, 'ci_upper': 1.85} | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.82, 'ci_lower': 1.79, 'ci_upper': 1.85} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.82, 'ci_lower': 1.79, 'ci_upper': 1.85} | Agent Input |
| validation_sample_size | n=37,161 | n=12,677 | n=7,525 | n=5,152 | n=5,152 | n=37,161 | n=37,161 | Agent Input |
| samples_training | N/A | n=2,500 | n=1,503 | n=997 | n=997 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (5%), AMR (2%), EAS (6%), EUR (86%), SAS (2%) / EVAL: MAE (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (5%), AMR (2%), EAS (6%), EUR (86%), SAS (2%) / EVAL: MAE (100%) | GWAS: AFR (5%), AMR (2%), EAS (6%), EUR (86%), SAS (2%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | AFGen BBJ FinnGen G&H HUNT MGI MVP MyCode SIMPLER UKB deCODE | MHI | MHI | MHI | MHI | AFGen BBJ FinnGen G&H HUNT MGI MVP MyCode SIMPLER UKB deCODE | AFGen BBJ FinnGen G&H HUNT MGI MVP MyCode SIMPLER UKB deCODE | Agent Input |
| publication.title | Cross-population GWAS and proteomics improve risk prediction and reveal mechanisms in atrial fibrillation. | Genetic analyses across cardiovascular traits: leveraging genetic correlations to empower locus discovery and prediction in common cardiovascular diseases. | Genetic analyses across cardiovascular traits: leveraging genetic correlations to empower locus discovery and prediction in common cardiovascular diseases. | Genetic analyses across cardiovascular traits: leveraging genetic correlations to empower locus discovery and prediction in common cardiovascular diseases. | Genetic analyses across cardiovascular traits: leveraging genetic correlations to empower locus discovery and prediction in common cardiovascular diseases. | Cross-population GWAS and proteomics improve risk prediction and reveal mechanisms in atrial fibrillation. | Cross-population GWAS and proteomics improve risk prediction and reveal mechanisms in atrial fibrillation. | Agent Input |
| publication.journal | Nat Commun | NPJ Genom Med | NPJ Genom Med | NPJ Genom Med | NPJ Genom Med | Nat Commun | Nat Commun | Agent Input |
| date_release | 2025-10-06 | 2025-12-18 | 2025-12-18 | 2025-12-18 | 2025-12-18 | 2025-10-06 | 2025-10-06 | Agent Input |
| variants_number | 1271239 | 1016634 | 1016634 | 1016634 | 1045170 | 1271239 | 1271239 | Agent Input |
| covariates | age, sex | age, sex, four first principal components of genetic ancestry | age, sex, four first principal components of genetic ancestry | age, sex, four first principal components of genetic ancestry | age, sex, four first principal components of genetic ancestry | age, sex | age, sex | Agent Input |


### melanoma

Candidate pool: `44` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003430 | PGS002246 | PGS002247 | PGS005208 | PGS000813 | PGS002247 | PGS002247 | Agent Input |
| AoU benchmark rank | 1/44 | 2/44 | 3/44 | 4/44 | 5/44 | 3/44 | 3/44 | Benchmark Only |
| AoU benchmark AUC | 0.6106 | 0.6102 | 0.6098 | 0.6088 | 0.5902 | 0.6098 | 0.6098 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Melanoma | Melanoma | Melanoma | Melanoma | Melanoma | Melanoma | Melanoma | Agent Input |
| trait_efo | melanoma | melanoma | melanoma | melanoma | melanoma | melanoma | melanoma | Agent Input |
| phenotyping_reported | Melanoma | Incident invasive melanoma | Incident invasive melanoma | Risk of melanoma in childhood cancer survivors | Familial cutaneous melanoma in non-carriers of a CDKN2A mutation | Incident invasive melanoma | Incident invasive melanoma | Agent Input |
| method_name | Maximum clumping and thresholding (maxCT) | Genome-wide significant variants | Genome-wide significant variants | Genome-wide significant SNPs | SNPs significantly associated with melanoma | Genome-wide significant variants | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM017104 | PPM012813 | PPM012812 | PPM022589 | PPM002147 | PPM012812 | PPM012812 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 4 | 4 | 1 | 3 | 4 | 4 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6340 | N/A | N/A | N/A | 0.7700 | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.634, 'ci_lower': 0.618, 'ci_upper': 0.661} | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.77, 'ci_lower': 0.75, 'ci_upper': 0.79} | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Odds ratio (OR, top 10% vs. middle 20%)', 'name_short': 'Odds ratio (OR, top 10% vs. middle 20%)', 'estimate': 5.7, 'ci_lower': 3.93, 'ci_upper': 8.28} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.73, 'ci_lower': 1.65, 'ci_upper': 1.81} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.8, 'ci_lower': 1.71, 'ci_upper': 1.88} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.6, 'ci_lower': 1.31, 'ci_upper': 1.67} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.12, 'ci_lower': 1.9, 'ci_upper': 2.35} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.8, 'ci_lower': 1.71, 'ci_upper': 1.88} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.8, 'ci_lower': 1.71, 'ci_upper': 1.88} | Agent Input |
| validation_sample_size | n=109,597 | n=395,647 | n=395,647 | n=11,220 | n=3,841 | n=395,647 | n=395,647 | Agent Input |
| samples_training | n=16,434 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | GenoMEL UKB | N/A | N/A | MIA | AMFS Essen-Heidelberg GenoMEL Harvard LMC MDACCS MELARISK Q-MEGA SEARCH WAMHS | N/A | N/A | Agent Input |
| publication.title | Melanoma risk prediction based on a polygenic risk score and clinical risk factors. | Independent evaluation of melanoma polygenic risk scores in UK and Australian prospective cohorts. | Independent evaluation of melanoma polygenic risk scores in UK and Australian prospective cohorts. | Polygenic risk scores, radiation treatment exposures and subsequent cancer risk in childhood cancer survivors. | Association between a 46-SNP Polygenic Risk Score and melanoma risk in Dutch patients with familial melanoma. | Independent evaluation of melanoma polygenic risk scores in UK and Australian prospective cohorts. | Independent evaluation of melanoma polygenic risk scores in UK and Australian prospective cohorts. | Agent Input |
| publication.journal | Melanoma Res | Br J Dermatol | Br J Dermatol | Nat Med | J Med Genet | Br J Dermatol | Br J Dermatol | Agent Input |
| date_release | 2023-10-17 | 2022-02-16 | 2022-02-16 | 2025-05-20 | 2021-07-02 | 2022-02-16 | 2022-02-16 | Agent Input |
| variants_number | 68 | 50 | 68 | 67 | 46 | 68 | 68 | Agent Input |
| covariates | Unknown | age, sex, self-reported ethnicity, ease of tanning, 20 genetic PCs | age, sex, self-reported ethnicity, ease of tanning, 20 genetic PCs | childhood cancer diagnosis, ancestry, age at childhood cancer diagnosis, radiation dose to the body region of the second cancer and chemotherapy exposure | Age, sex | age, sex, self-reported ethnicity, ease of tanning, 20 genetic PCs | age, sex, self-reported ethnicity, ease of tanning, 20 genetic PCs | Agent Input |


### type 1 diabetes mellitus

Candidate pool: `33` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001817 | PGS002025 | PGS004175 | PGS004162 | PGS004171 | PGS004093 | PGS000021 | Agent Input |
| AoU benchmark rank | 1/33 | 2/33 | 3/33 | 4/33 | 5/33 | 21/33 | 32/33 | Benchmark Only |
| AoU benchmark AUC | 0.6783 | 0.6744 | 0.6743 | 0.6702 | 0.6689 | 0.6475 | 0.5553 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Type 1 diabetes (T1D) | Type 1 diabetes (T1D) | Type 1 diabetes | Type 1 diabetes (T1D) | Type 1 diabetes | Type 1 diabetes (T1D) | Type 1 diabetes (T1D) | Agent Input |
| trait_efo | type 1 diabetes mellitus | type 1 diabetes mellitus | type 1 diabetes mellitus | type 1 diabetes mellitus | type 1 diabetes mellitus | type 1 diabetes mellitus | type 1 diabetes mellitus | Agent Input |
| phenotyping_reported | Type 1 diabetes | Type 1 diabetes | Type 1 diabetes | T1D | Type 1 diabetes | T1D | Type 1 diabetes | Agent Input |
| method_name | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | LASSO | UKBB-EUR.MultiPRS.CV | LASSO | PRS-CS-auto | SNP associations curated from the literature | Agent Input |
| performance_metrics.selected_performance_id | PPM009436 | PPM011074 | PPM020108 | PPM019961 | PPM020104 | PPM019986 | PPM000049 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 8 | 8 | 1 | 5 | 1 | 5 | 14 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.7000 | 0.7187 | 0.7000 | 0.7422 | 0.8930 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0746 | N/A | 0.0984 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71872811, 'ci_lower': 0.71109285, 'ci_upper': 0.72636337} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74220929, 'ci_lower': 0.7347773, 'ci_upper': 0.74964128} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.893} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0752, 'ci_lower': 0.061, 'ci_upper': 0.0893} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0824, 'ci_lower': 0.0682, 'ci_upper': 0.0965} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07462299, 'ci_lower': 0.06945443, 'ci_upper': 0.08005629} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.09841157, 'ci_lower': 0.09204504, 'ci_upper': 0.10511922} | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.27887095, 'ci_lower': 2.20957694, 'ci_upper': 2.35033807} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.82368012, 'ci_lower': 0.79280107, 'ci_upper': 0.85455918} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.44507683, 'ci_lower': 2.37411415, 'ci_upper': 2.51816059} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.89407654, 'ci_lower': 0.86462438, 'ci_upper': 0.92352871} | N/A | Agent Input |
| validation_sample_size | n=18,975 | n=18,975 | n=45,334 | n=322,349 | n=45,334 | n=322,349 | n=374,000 | Agent Input |
| samples_training | n=391,124 | n=391,124 | n=200,000 | n=804 | n=200,000 | n=804 | n=3,852 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (7%), EUR (89%), OTH (4%) / DEV: EUR (100%) / EVAL: EUR (80%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (7%), EUR (89%), OTH (4%) / DEV: EUR (100%) / EVAL: EUR (80%), SAS (20%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (20%), EUR (60%), MAE (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | N/A | UKB | N/A | UKB | WTCCC | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Biobank-scale methods and projections for sparse polygenic prediction from machine learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Biobank-scale methods and projections for sparse polygenic prediction from machine learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | A Type 1 Diabetes Genetic Risk Score Can Aid Discrimination Between Type 1 and Type 2 Diabetes in Young Adults. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Sci Rep | Am J Hum Genet | Sci Rep | Am J Hum Genet | Diabetes Care | Agent Input |
| date_release | 2022-01-10 | 2022-01-10 | 2023-12-15 | 2023-12-19 | 2023-12-15 | 2023-12-19 | 2019-10-14 | Agent Input |
| variants_number | 825 | 106800 | 315 | 62645 | 520 | 61651 | 33 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | year of birth, sex | 0 | year of birth, sex | 0 | Unknown | Agent Input |


### gout

Candidate pool: `30` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004160 | PGS004076 | PGS004047 | PGS004018 | PGS000711 | PGS004160 | PGS004160 | Agent Input |
| AoU benchmark rank | 1/30 | 2/30 | 3/30 | 4/30 | 5/30 | 1/30 | 1/30 | Benchmark Only |
| AoU benchmark AUC | 0.6481 | 0.6431 | 0.6424 | 0.6414 | 0.6400 | 0.6481 | 0.6481 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Gout | Gout | Gout | Gout | Gout | Gout | Gout | Agent Input |
| trait_efo | gout | gout | gout | gout | gout | gout | gout | Agent Input |
| phenotyping_reported | Gout | Gout | Gout | Gout | Gout | Gout | Gout | Agent Input |
| method_name | UKBB-EUR.MultiPRS.CV | megaprs.CV | LDpred2.CV | lassosum.CV | snpnet (multi-PRS) | UKBB-EUR.MultiPRS.CV | UKBB-EUR.MultiPRS.CV | Agent Input |
| performance_metrics.selected_performance_id | PPM019860 | PPM019875 | PPM019812 | PPM019911 | PPM001616 | PPM019860 | PPM019860 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 6 | 6 | 6 | 6 | 2 | 6 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6414 | 0.6344 | 0.6383 | 0.6334 | 0.6730 | 0.6414 | 0.6414 | Agent Input |
| performance_metrics.full_model_r2 | 0.0462 | 0.0413 | 0.0431 | 0.0408 | N/A | 0.0462 | 0.0462 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64137707, 'ci_lower': 0.63546764, 'ci_upper': 0.64728649} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63435306, 'ci_lower': 0.62841613, 'ci_upper': 0.64028998} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63826477, 'ci_lower': 0.63237721, 'ci_upper': 0.64415233} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63337189, 'ci_lower': 0.62746646, 'ci_upper': 0.63927731} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.673} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64137707, 'ci_lower': 0.63546764, 'ci_upper': 0.64728649} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64137707, 'ci_lower': 0.63546764, 'ci_upper': 0.64728649} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04620449, 'ci_lower': 0.04249866, 'ci_upper': 0.05008491} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04132122, 'ci_lower': 0.03772231, 'ci_upper': 0.0451372} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04312949, 'ci_lower': 0.03957846, 'ci_upper': 0.04698389} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04076241, 'ci_lower': 0.03719796, 'ci_upper': 0.04435327} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04620449, 'ci_lower': 0.04249866, 'ci_upper': 0.05008491} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04620449, 'ci_lower': 0.04249866, 'ci_upper': 0.05008491} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.67706433, 'ci_lower': 1.64102293, 'ci_upper': 1.7138973} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.51704484, 'ci_lower': 0.49531979, 'ci_upper': 0.5387699} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.6370911, 'ci_lower': 1.60165217, 'ci_upper': 1.67331416} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.49292094, 'ci_lower': 0.4710357, 'ci_upper': 0.51480619} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65591648, 'ci_lower': 1.61999787, 'ci_upper': 1.69263148} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.50435462, 'ci_lower': 0.48242483, 'ci_upper': 0.52628441} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.6311933, 'ci_lower': 1.59590072, 'ci_upper': 1.66726636} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.48931183, 'ci_lower': 0.46743829, 'ci_upper': 0.51118537} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.58, 'ci_lower': 1.51, 'ci_upper': 1.65} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.67706433, 'ci_lower': 1.64102293, 'ci_upper': 1.7138973} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.51704484, 'ci_lower': 0.49531979, 'ci_upper': 0.5387699} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.67706433, 'ci_lower': 1.64102293, 'ci_upper': 1.7138973} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.51704484, 'ci_lower': 0.49531979, 'ci_upper': 0.5387699} | Agent Input |
| validation_sample_size | n=257,781 | n=257,781 | n=257,781 | n=257,781 | n=135,300 | n=257,781 | n=257,781 | Agent Input |
| samples_training | n=6,704 | n=6,704 | n=6,704 | n=6,704 | n=223,327 | n=6,704 | n=6,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Genetics of 35 blood and urine biomarkers in the UK Biobank. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Nat Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2021-02-03 | 2023-12-19 | 2023-12-19 | Agent Input |
| variants_number | 976174 | 677631 | 865644 | 100595 | 183332 | 976174 | 976174 | Agent Input |
| covariates | 0 | 0 | 0 | 0 | Age as time scale, sex, batch, PCs(1-10) | 0 | 0 | Agent Input |


### thyroid carcinoma

Candidate pool: `27` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001799 | PGS001794 | PGS004954 | PGS003746 | PGS000797 | PGS000209 | PGS000208 | Agent Input |
| AoU benchmark rank | 1/27 | 2/27 | 3/27 | 4/27 | 5/27 | 12/27 | 11/27 | Benchmark Only |
| AoU benchmark AUC | 0.6331 | 0.6299 | 0.6099 | 0.5999 | 0.5970 | 0.5888 | 0.5890 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Thyroid cancer | Thyroid cancer | Thyroid cancer | Thyroid cancer | Thyroid cancer | Thyroid cancer | Thyroid cancer | Agent Input |
| trait_efo | thyroid gland carcinoma | thyroid gland carcinoma | thyroid gland carcinoma | thyroid gland carcinoma | thyroid gland carcinoma | thyroid gland carcinoma | thyroid gland carcinoma | Agent Input |
| phenotyping_reported | Thyroid cancer | Thyroid cancer | Thyroid cancer | Thyroid cancer | Incident thyroid cancer | Thyroid cancer | Thyroid cancer | Agent Input |
| method_name | PRS-CS-auto | PRS-CS-auto | Genome-wide significant SNPs | Genome-wide significant SNPs | 12 variants from Graff et al (PGS000087) with inverse variant weights | Genome-wide significant variants | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM009315 | PPM009298 | PPM021769 | PPM018502 | PPM002068 | PPM000633 | PPM000632 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | African American or Afro-Caribbean, Asian unspecified, European, Native American, Not reported | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | 0.0104 | 0.0137 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6850 | 0.6760 | 0.7000 | N/A | 0.7010 | 0.6940 | 0.7510 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.3100 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.685} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.676} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.701} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.692, 'se': 0.022} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.694, 'ci_lower': 0.673, 'ci_upper': 0.716} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.751, 'ci_lower': 0.736, 'ci_upper': 0.768} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.010362} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.013659} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.31} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.63, 'ci_lower': 1.44, 'ci_upper': 1.85} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.75, 'ci_lower': 1.53, 'ci_upper': 2.01} | N/A | N/A | Agent Input |
| validation_sample_size | n=7,128 | n=358,476 | n=73,346 | n=360 | n=391,189 | n=408,479 | n=130,279 | Agent Input |
| samples_training | N/A | N/A | N/A | n=179 | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (90%), EAS (16%), EUR (83%), OTH (70%) / EVAL: EUR (100%) | GWAS: AFR (1%), EAS (21%), EUR (77%), OTH (90%) / EVAL: EUR (100%) | GWAS: AFR (90%), AMR (70%), EAS (16%), EUR (83%) / EVAL: MAE (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BioMe BioVU CCPM EB FinnGen GS:SFHS HUNT LifeLines MGBB MGI QSKIN UCLA UKB deCODE | BioMe BioVU CCPM EB FinnGen GS:SFHS HUNT LifeLines MGBB MGI QSKIN UCLA deCODE | N/A | UKB | ICR NBS ODZH RUNMC deCODE | UKB deCODE | NBS UKB | Agent Input |
| publication.title | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Thyroid Cancer Polygenic Risk Score Improves Classification of Thyroid Nodules as Benign or Malignant. | Prognostic evaluation of polygenic risk score underlying pan-cancer analysis: evidence from two large-scale cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Assessing thyroid cancer risk using polygenic risk scores. | Assessing thyroid cancer risk using polygenic risk scores. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | J Clin Endocrinol Metab | EBioMedicine | Nat Commun | Proc Natl Acad Sci U S A | Proc Natl Acad Sci U S A | Agent Input |
| date_release | 2022-09-08 | 2022-09-08 | 2024-09-19 | 2023-06-01 | 2021-05-28 | 2020-07-01 | 2020-07-01 | Agent Input |
| variants_number | 885482 | 911462 | 26 | 11 | 12 | 10 | 10 | Agent Input |
| covariates | sex,age, 20PCs | sex,age,age2,age*sex,age^2*sex, 20PCs | Age, sex, genotyping batch, 10 PCs | Unknown | Age at assessment, sex,, genotyping array, PCs(1-15), body mass index (BMI <25 vs. 25≤BMI<30, BMI≥30) | gender, birth year | gender, birth year, family history of disease (1st or 2nd degree relative) | Agent Input |


### rheumatoid arthritis

Candidate pool: `25` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004163 | PGS004873 | PGS004064 | PGS004049 | PGS002769 | PGS004163 | PGS004257 | Agent Input |
| AoU benchmark rank | 1/25 | 2/25 | 3/25 | 4/25 | 5/25 | 1/25 | 10/25 | Benchmark Only |
| AoU benchmark AUC | 0.5712 | 0.5669 | 0.5633 | 0.5629 | 0.5623 | 0.5712 | 0.5566 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Rheumatoid arthritis | Rheumatoid arthritis | Rheumatoid arthritis | Rheumatoid arthritis | Seropositive rheumatoid arthritis | Rheumatoid arthritis | Rheumatoid arthritis | Agent Input |
| trait_efo | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | Agent Input |
| phenotyping_reported | Seropositive RA | Incident RA | Seropositive RA | Seropositive RA | Seropositive rheumatoid arthritis | Seropositive RA | Rheumatoid arthritis | Agent Input |
| method_name | UKBB-EUR.MultiPRS.CV | megaprs.auto | megaprs.auto | LDpred2.CV | PRS-CS | UKBB-EUR.MultiPRS.CV | GenoBoost | Agent Input |
| performance_metrics.selected_performance_id | PPM020026 | PPM021171 | PPM020036 | PPM020001 | PPM014969 | PPM020026 | PPM020325 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 5 | 8 | 5 | 5 | 1 | 5 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6528 | 0.6500 | 0.6417 | 0.6351 | N/A | 0.6528 | 0.6609 | Agent Input |
| performance_metrics.full_model_r2 | 0.0480 | N/A | 0.0407 | 0.0367 | N/A | 0.0480 | 0.0119 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65279323, 'ci_lower': 0.64709296, 'ci_upper': 0.6584935} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.65, 'ci_lower': 0.65, 'ci_upper': 0.66} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64168565, 'ci_lower': 0.63597003, 'ci_upper': 0.64740127} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63510175, 'ci_lower': 0.62933904, 'ci_upper': 0.64086446} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65279323, 'ci_lower': 0.64709296, 'ci_upper': 0.6584935} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.660865982537907} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04802428, 'ci_lower': 0.0444714, 'ci_upper': 0.05161881} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04068007, 'ci_lower': 0.03737711, 'ci_upper': 0.04388012} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03670435, 'ci_lower': 0.03357391, 'ci_upper': 0.04012387} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04802428, 'ci_lower': 0.0444714, 'ci_upper': 0.05161881} | {'name_long': 'AUPRC', 'name_short': 'AUPRC', 'estimate': 0.045614380454329} {'name_long': 'Covariate-adjusted pseudo-R2', 'name_short': 'Covariate-adjusted pseudo-R2', 'estimate': 0.0119079155075658} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.7540178, 'ci_lower': 1.71840512, 'ci_upper': 1.79036854} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.56190904, 'ci_lower': 0.5413966, 'ci_upper': 0.58242149} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.65, 'ci_lower': 1.62, 'ci_upper': 1.69} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.67650034, 'ci_lower': 1.64253856, 'ci_upper': 1.71116433} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.51670849, 'ci_lower': 0.49624295, 'ci_upper': 0.53717403} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.6397232, 'ci_lower': 1.60628474, 'ci_upper': 1.67385776} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.49452745, 'ci_lower': 0.47392389, 'ci_upper': 0.515131} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.72, 'ci_lower': 1.61, 'ci_upper': 1.83} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.7540178, 'ci_lower': 1.71840512, 'ci_upper': 1.79036854} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.56190904, 'ci_lower': 0.5413966, 'ci_upper': 0.58242149} | N/A | Agent Input |
| validation_sample_size | n=388,890 | n=412,090 | n=388,890 | n=388,890 | n=39,444 | n=388,890 | n=67,428 | Agent Input |
| samples_training | n=820 | n=404 | n=820 | n=820 | N/A | n=820 | n=269,710 | Agent Input |
| ancestry_distribution | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (80%), SAS (20%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (80%), SAS (20%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (80%), SAS (20%) | GWAS: EAS (28%), EUR (72%) / EVAL: EUR (100%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (80%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | 1000G | UKB | UKB | N/A | UKB | UKB | Agent Input |
| publication.title | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | A polygenic score method boosted by non-additive models. | Agent Input |
| publication.journal | Am J Hum Genet | Nat Commun | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Nat Commun | Agent Input |
| date_release | 2023-12-19 | 2024-06-27 | 2023-12-19 | 2023-12-19 | 2022-11-07 | 2023-12-19 | 2024-06-12 | Agent Input |
| variants_number | 778275 | 551074 | 402214 | 373627 | 1083565 | 778275 | 20 | Agent Input |
| covariates | 0 | PCs 1-10 | 0 | 0 | age, sex, 10 PCs, technical covariates | 0 | age, sex, PC1-10 | Agent Input |


### chronic kidney disease

Candidate pool: `22` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004045 | PGS004030 | PGS004158 | PGS004074 | PGS004088 | PGS002237 | PGS002237 | Agent Input |
| AoU benchmark rank | 1/22 | 2/22 | 3/22 | 4/22 | 5/22 | 12/22 | 12/22 | Benchmark Only |
| AoU benchmark AUC | 0.5566 | 0.5564 | 0.5562 | 0.5546 | 0.5546 | 0.5466 | 0.5466 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (stage 3 or greater) | Chronic kidney disease (stage 3 or greater) | Agent Input |
| trait_efo | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | Agent Input |
| phenotyping_reported | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic Kidney Disease (stage 3 or greater) | Chronic Kidney Disease (stage 3 or greater) | Agent Input |
| method_name | LDpred2.CV | LDpred2-auto | UKBB-EUR.MultiPRS.CV | megaprs.CV | PRS-CS-auto | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM019686 | PPM019746 | PPM019716 | PPM019766 | PPM019782 | PPM012722 | PPM012722 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 6 | 6 | 6 | 6 | 6 | 9 | 9 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5508 | 0.5500 | 0.5529 | 0.5514 | 0.5492 | 0.7500 | 0.7500 | Agent Input |
| performance_metrics.full_model_r2 | 0.0061 | 0.0058 | 0.0066 | 0.0062 | 0.0057 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.55079959, 'ci_lower': 0.54489488, 'ci_upper': 0.55670431} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.54995305, 'ci_lower': 0.54405258, 'ci_upper': 0.55585351} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.55286759, 'ci_lower': 0.54695878, 'ci_upper': 0.5587764} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.55139033, 'ci_lower': 0.54546982, 'ci_upper': 0.55731084} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.54923924, 'ci_lower': 0.5433243, 'ci_upper': 0.55515418} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.75} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00607993, 'ci_lower': 0.00470563, 'ci_upper': 0.00760115} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00576181, 'ci_lower': 0.00443121, 'ci_upper': 0.00725396} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00660549, 'ci_lower': 0.00515137, 'ci_upper': 0.00817172} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00624273, 'ci_lower': 0.00487883, 'ci_upper': 0.00778005} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00565456, 'ci_lower': 0.00431514, 'ci_upper': 0.00712059} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.19905545, 'ci_lower': 1.17464211, 'ci_upper': 1.2239762} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.18153413, 'ci_lower': 0.16096351, 'ci_upper': 0.20210474} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.19336836, 'ci_lower': 1.16906302, 'ci_upper': 1.21817902} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.17677986, 'ci_lower': 0.15620259, 'ci_upper': 0.19735714} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.20835711, 'ci_lower': 1.18374816, 'ci_upper': 1.23347765} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.18926168, 'ci_lower': 0.16868581, 'ci_upper': 0.20983754} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.20198176, 'ci_lower': 1.17750562, 'ci_upper': 1.22696667} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.18397166, 'ci_lower': 0.16339832, 'ci_upper': 0.204545} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.19129762, 'ci_lower': 1.16704613, 'ci_upper': 1.21605305} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.17504315, 'ci_lower': 0.15447588, 'ci_upper': 0.19561041} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49, 'ci_lower': 1.47, 'ci_upper': 1.5} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49, 'ci_lower': 1.47, 'ci_upper': 1.5} | Agent Input |
| validation_sample_size | n=383,843 | n=383,843 | n=383,843 | n=383,843 | n=383,843 | n=141,247 | n=141,247 | Agent Input |
| samples_training | n=13,496 | n=13,496 | n=13,496 | n=13,496 | n=13,496 | n=279,819 | n=279,819 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: AFR (14%), AMR (14%), ASN (14%), EUR (29%), MAE (29%) | DEV: EUR (100%) / EVAL: AFR (14%), AMR (14%), ASN (14%), EUR (29%), MAE (29%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Genome-wide polygenic score to predict chronic kidney disease across ancestries. | Genome-wide polygenic score to predict chronic kidney disease across ancestries. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Nat Med | Nat Med | Agent Input |
| date_release | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2022-01-10 | 2022-01-10 | Agent Input |
| variants_number | 1050295 | 1050295 | 1135455 | 846995 | 1109217 | 471316 | 471316 | Agent Input |
| covariates | 0 | 0 | 0 | 0 | 0 | Age, Sex, Diabetes and 4 PCs | Age, Sex, Diabetes and 4 PCs | Agent Input |


### major depressive disorder

Candidate pool: `22` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003333 | PGS000907 | PGS004885 | PGS002789 | PGS002759 | PGS004885 | PGS004885 | Agent Input |
| AoU benchmark rank | 1/22 | 2/22 | 3/22 | 4/22 | 5/22 | 3/22 | 3/22 | Benchmark Only |
| AoU benchmark AUC | 0.5687 | 0.5648 | 0.5504 | 0.5493 | 0.5468 | 0.5504 | 0.5504 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Major Depressive Disorder | Major depressive disorder | Major depressive disorder | Major depressive disorder | Depression | Major depressive disorder | Major depressive disorder | Agent Input |
| trait_efo | major depressive disorder | major depressive disorder | major depressive disorder | major depressive disorder | major depressive disorder | major depressive disorder | major depressive disorder | Agent Input |
| phenotyping_reported | Major Depressive Disorder | Headaches in Sertraline takers | Incident MDD | Cognitive function (fluid composite) | Depression | Incident MDD | Incident MDD | Agent Input |
| method_name | PRS-CS-auto | SBayesR | megaprs.auto | SDPR | PRS-CS | megaprs.auto | megaprs.auto | Agent Input |
| performance_metrics.selected_performance_id | PPM016144 | PPM002680 | PPM021257 | PPM015270 | PPM014959 | PPM021257 | PPM021257 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 50 | 7 | 50 | 1 | 7 | 7 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.5800 | N/A | N/A | 0.5800 | 0.5800 | Agent Input |
| performance_metrics.full_model_r2 | 0.0220 | 0.0200 | N/A | 0.0014 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.58, 'ci_lower': 0.58, 'ci_upper': 0.58} | N/A | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.58, 'ci_lower': 0.58, 'ci_upper': 0.58} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.58, 'ci_lower': 0.58, 'ci_upper': 0.58} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Nagelkerke pseudo-R2', 'name_short': 'Nagelkerke pseudo-R2', 'estimate': 0.022} | {'name_long': "Variance explained (Nagelkerke's R2*100)", 'name_short': "Variance explained (Nagelkerke's R2*100)", 'estimate': 0.02} | N/A | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00137314877601709} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.03, 'ci_lower': 0.95, 'ci_upper': 1.11} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.24, 'ci_lower': 1.23, 'ci_upper': 1.25} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.26, 'ci_lower': 1.22, 'ci_upper': 1.3} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.24, 'ci_lower': 1.23, 'ci_upper': 1.25} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.24, 'ci_lower': 1.23, 'ci_upper': 1.25} | Agent Input |
| validation_sample_size | n=34,703 | n=5,719 | n=412,090 | n=68,614 | n=39,444 | n=412,090 | n=412,090 | Agent Input |
| samples_training | N/A | N/A | n=404 | N/A | N/A | n=404 | n=404 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | 23andMe PGC UKB | N/A | 1000G | 23andMe GS:SFHS PGC deCODE iPSYCH | N/A | 1000G | 1000G | Agent Input |
| publication.title | Polygenic Liability to Depression Is Associated With Multiple Medical Conditions in the Electronic Health Record: Phenome-wide Association Study of 46,782 Individuals. | Understanding genetic risk factors for common side effects of antidepressant medications | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Systematic comparison of family history and polygenic risk across 24 common diseases. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Agent Input |
| publication.journal | Biol Psychiatry | Commun Med (Lond) | Nat Commun | Transl Psychiatry | Am J Hum Genet | Nat Commun | Nat Commun | Agent Input |
| date_release | 2022-12-06 | 2021-10-07 | 2024-06-27 | 2022-09-29 | 2022-11-07 | 2024-06-27 | 2024-06-27 | Agent Input |
| variants_number | 1088415 | 1773528 | 801544 | 943784 | 1091613 | 801544 | 801544 | Agent Input |
| covariates | Unknown | sex, age at study enrollment, genetic PCs 1-20 | PCs 1-10 | age, PCs1-10 | age, sex, 10 PCs, technical covariates | PCs 1-10 | PCs 1-10 | Agent Input |


### psoriasis

Candidate pool: `22` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005311 | PGS005309 | PGS004315 | PGS005312 | PGS005310 | PGS001312 | PGS001312 | Agent Input |
| AoU benchmark rank | 1/22 | 2/22 | 3/22 | 4/22 | 5/22 | 15/22 | 15/22 | Benchmark Only |
| AoU benchmark AUC | 0.6000 | 0.5999 | 0.5954 | 0.5896 | 0.5892 | 0.5665 | 0.5665 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Psoriasis | Psoriasis | Psoriasis | Psoriasis | Psoriasis | Psoriasis | Psoriasis | Agent Input |
| trait_efo | psoriasis | psoriasis | psoriasis | psoriasis | psoriasis | psoriasis | psoriasis | Agent Input |
| phenotyping_reported | Severe psoriasis (BSTOP) vs. any psoriasis (UKB) | Severe psoriasis | Family history of psoriasis | Severe psoriasis (BSTOP) vs. any psoriasis (UKB) | Severe psoriasis | Psoriasis | Psoriasis | Agent Input |
| method_name | SBayesR | SBayesR | Genome-wide significant SNPs | SBayesR | SBayesR | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM023031 | PPM023021 | PPM020383 | PPM023032 | PPM023022 | PPM009057 | PPM009057 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 4 | 7 | 2 | 4 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | 0.6916 | 0.6916 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0523 | 0.0523 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | 0.6975 | 0.6975 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0067 | N/A | N/A | 0.0557 | 0.0557 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | 0.1451 | 0.1451 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69754, 'ci_lower': 0.68165, 'ci_upper': 0.71343} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69754, 'ci_lower': 0.68165, 'ci_upper': 0.71343} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'name_short': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'estimate': 15.3} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0067} | {'name_long': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'name_short': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'estimate': 15.3} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05574} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.14505} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05226} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.69158, 'ci_lower': 0.6754, 'ci_upper': 0.70775} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05574} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.14505} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05226} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.69158, 'ci_lower': 0.6754, 'ci_upper': 0.70775} | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49, 'ci_lower': 1.41, 'ci_upper': 1.57} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.02, 'ci_lower': 1.0, 'ci_upper': 1.04} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.38, 'ci_lower': 1.31, 'ci_upper': 1.45} | N/A | N/A | Agent Input |
| validation_sample_size | n=13,577 | n=14,167 | n=654 | n=13,577 | n=14,167 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | CASP Genizon KIEL UCSF WTCCC | CASP Genizon KIEL UCSF WTCCC | N/A | CASP Genizon KIEL UCSF WTCCC | CASP Genizon KIEL UCSF WTCCC | UKB | UKB | Agent Input |
| publication.title | Genetic liability to psoriasis predicts severe disease outcomes. | Genetic liability to psoriasis predicts severe disease outcomes. | A partitioned 88-loci psoriasis genetic risk score reveals HLA and non-HLA contributions to clinical phenotypes in a Newfoundland psoriasis cohort. | Genetic liability to psoriasis predicts severe disease outcomes. | Genetic liability to psoriasis predicts severe disease outcomes. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Genome Med | Genome Med | Front Genet | Genome Med | Genome Med | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2024-01-11 | 2026-01-19 | 2026-01-19 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 487311 | 513461 | 88 | 487310 | 513460 | 204 | 204 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### ovarian neoplasm

Candidate pool: `21` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000546 | PGS000559 | PGS000560 | PGS000553 | PGS000552 | PGS000550 | PGS000550 | Agent Input |
| AoU benchmark rank | 1/21 | 2/21 | 3/21 | 4/21 | 5/21 | 18/21 | 18/21 | Benchmark Only |
| AoU benchmark AUC | 0.5640 | 0.5623 | 0.5623 | 0.5611 | 0.5530 | 0.4952 | 0.4952 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Agent Input |
| trait_efo | ovarian neoplasm | ovarian neoplasm | ovarian neoplasm | ovarian neoplasm | ovarian neoplasm | ovarian neoplasm | ovarian neoplasm | Agent Input |
| phenotyping_reported | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Agent Input |
| method_name | PRS-CS | GWAS Hits | GWAS Hits | GWAS Hits | lassosum | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM001231 | PPM001244 | PPM001245 | PPM001238 | PPM001237 | PPM001235 | PPM001235 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5260 | 0.5540 | 0.5520 | 0.5560 | 0.5520 | 0.5680 | 0.5680 | Agent Input |
| performance_metrics.full_model_r2 | 0.0022 | 0.0052 | 0.0082 | 0.0053 | 0.0055 | 0.0113 | 0.0113 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.526, 'ci_lower': 0.498, 'ci_upper': 0.554} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.554, 'ci_lower': 0.509, 'ci_upper': 0.597} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.552, 'ci_lower': 0.523, 'ci_upper': 0.581} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.556, 'ci_lower': 0.53, 'ci_upper': 0.584} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.552, 'ci_lower': 0.523, 'ci_upper': 0.58} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.568, 'ci_lower': 0.542, 'ci_upper': 0.595} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.568, 'ci_lower': 0.542, 'ci_upper': 0.595} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.00221} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0827} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.97, 'ci_lower': 0.973, 'ci_upper': 4.0} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.00516} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0827} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 0.784, 'ci_lower': 0.142, 'ci_upper': 4.32} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.00819} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0824} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.76, 'ci_lower': 0.839, 'ci_upper': 3.69} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.00531} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0825} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.76, 'ci_lower': 0.839, 'ci_upper': 3.69} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.00552} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0825} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.97, 'ci_lower': 0.97, 'ci_upper': 3.99} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0113} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0823} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.76, 'ci_lower': 0.838, 'ci_upper': 3.7} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0113} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0823} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.76, 'ci_lower': 0.838, 'ci_upper': 3.7} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.119, 'ci_lower': 1.017, 'ci_upper': 1.231} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.112, 'se': 0.0488} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.183, 'ci_lower': 1.015, 'ci_upper': 1.378} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.168, 'se': 0.078} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.233, 'ci_lower': 1.125, 'ci_upper': 1.352} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.21, 'se': 0.047} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.188, 'ci_lower': 1.079, 'ci_upper': 1.308} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.172, 'se': 0.0491} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.19, 'ci_lower': 1.084, 'ci_upper': 1.308} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.174, 'se': 0.048} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.286, 'ci_lower': 1.169, 'ci_upper': 1.414} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.251, 'se': 0.0485} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.286, 'ci_lower': 1.169, 'ci_upper': 1.414} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.251, 'se': 0.0485} | Agent Input |
| validation_sample_size | n=5,196 | n=1,904 | n=5,196 | n=5,196 | n=5,196 | n=5,196 | n=5,196 | Agent Input |
| samples_training | n=5,130 | n=2,122 | n=5,130 | n=5,130 | n=5,130 | n=5,130 | n=5,130 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | MGI | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | Agent Input |
| variants_number | 1115189 | 21 | 21 | 10 | 41269 | 1115189 | 1115189 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Agent Input |


### basal cell carcinoma

Candidate pool: `20` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003417 | PGS003416 | PGS000730 | PGS000452 | PGS000453 | PGS003416 | PGS000730 | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | 2/20 | 3/20 | Benchmark Only |
| AoU benchmark AUC | 0.6025 | 0.5996 | 0.5937 | 0.5912 | 0.5912 | 0.5996 | 0.5937 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Basal cell carcinoma | Basal cell carcinoma (MTAG) | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma (MTAG) | Basal cell carcinoma | Agent Input |
| trait_efo | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | Agent Input |
| phenotyping_reported | Keratinocyte cancers | Keratinocyte cancers | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Keratinocyte cancers | Basal cell carcinoma | Agent Input |
| method_name | Genome-wide significant SNPs | Genome-wide significant SNPs | RiskPipe (clumping and thresholding) | GWAS Hits | GWAS Hits | Genome-wide significant SNPs | RiskPipe (clumping and thresholding) | Agent Input |
| performance_metrics.selected_performance_id | PPM017070 | PPM017069 | PPM001670 | PPM001137 | PPM001138 | PPM017069 | PPM001670 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.6240 | 0.6320 | 0.6110 | N/A | 0.6240 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0487 | 0.0301 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.624} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.632, 'ci_lower': 0.616, 'ci_upper': 0.647} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.611, 'ci_lower': 0.604, 'ci_upper': 0.619} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.624} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0487} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.106} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.61, 'ci_lower': 2.53, 'ci_upper': 5.15} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0301} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0813} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.8, 'ci_lower': 2.33, 'ci_upper': 3.36} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.56, 'ci_lower': 1.45, 'ci_upper': 1.67} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.66, 'ci_lower': 1.55, 'ci_upper': 1.79} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.57, 'ci_lower': 1.55, 'ci_upper': 1.6} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.663, 'ci_lower': 1.57, 'ci_upper': 1.761} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.508, 'se': 0.0293} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.511, 'ci_lower': 1.47, 'ci_upper': 1.554} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.413, 'se': 0.0142} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.66, 'ci_lower': 1.55, 'ci_upper': 1.79} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.57, 'ci_lower': 1.55, 'ci_upper': 1.6} | Agent Input |
| validation_sample_size | n=18,933 | n=18,933 | n=88,924 | n=11,322 | n=60,018 | n=18,933 | n=88,924 | Agent Input |
| samples_training | N/A | N/A | N/A | n=11,734 | n=61,038 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | GERA QSKIN UKB eMERGE | 23andMe | MGI | UKB | GERA QSKIN UKB eMERGE | 23andMe | Agent Input |
| publication.title | A multi-phenotype analysis reveals 19 susceptibility loci for basal cell carcinoma and 15 for squamous cell carcinoma. | A multi-phenotype analysis reveals 19 susceptibility loci for basal cell carcinoma and 15 for squamous cell carcinoma. | Disease risk scores for skin cancers. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | A multi-phenotype analysis reveals 19 susceptibility loci for basal cell carcinoma and 15 for squamous cell carcinoma. | Disease risk scores for skin cancers. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Nat Commun | Am J Hum Genet | Am J Hum Genet | Nat Commun | Nat Commun | Agent Input |
| date_release | 2023-02-08 | 2023-02-08 | 2021-02-23 | 2020-12-15 | 2020-12-15 | 2023-02-08 | 2021-02-23 | Agent Input |
| variants_number | 273 | 462 | 47 | 28 | 28 | 462 | 47 | Agent Input |
| covariates | age, sex, 10 ancesty PCs | age, sex, 10 ancesty PCs | Unknown | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, 10 ancesty PCs | Unknown | Agent Input |


### hypothyroidism

Candidate pool: `20` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005218 | PGS002336 | PGS000761 | PGS002024 | PGS002702 | PGS005218 | PGS005218 | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | 1/20 | 1/20 | Benchmark Only |
| AoU benchmark AUC | 0.6274 | 0.6202 | 0.6162 | 0.6131 | 0.6118 | 0.6274 | 0.6274 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Agent Input |
| trait_efo | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | Agent Input |
| phenotyping_reported | Hypothyroidism | Hypothyroidism | anti-PD-L1 induced hypothyroidism in cancer patients | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Agent Input |
| method_name | PRS-CS | BOLT-LMM | LDpred2-auto | LDpred2 (bigsnpr) | SBayesR | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM022613 | PPM013199 | PPM001936 | PPM011066 | PPM014663 | PPM022613 | PPM022613 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 6 | 4 | 1 | 8 | 4 | 6 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0247 | N/A | N/A | 0.0206 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Incremental R2 (full model vs. covariates alone)', 'name_short': 'Incremental R2 (full model vs. covariates alone)', 'estimate': 0.0247} | {'name_long': 'meta-analysis p-value', 'name_short': 'meta-analysis p-value', 'estimate': 5.49e-09} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.122, 'ci_lower': 0.1083, 'ci_upper': 0.1357} | {'name_long': 'Incremental R2 (full model vs. covariates alone)', 'name_short': 'Incremental R2 (full model vs. covariates alone)', 'estimate': 0.0206} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.01, 'ci_lower': 1.99, 'ci_upper': 2.03} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.49, 'ci_lower': 1.3, 'ci_upper': 1.71} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.01, 'ci_lower': 1.99, 'ci_upper': 2.03} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.01, 'ci_lower': 1.99, 'ci_upper': 2.03} | Agent Input |
| validation_sample_size | n=441,692 | n=43,505 | n=1,584 | n=19,852 | n=43,505 | n=441,692 | n=441,692 | Agent Input |
| samples_training | n=1,146,562 | N/A | n=408,959 | n=391,124 | N/A | n=1,146,562 | n=1,146,562 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: AFR (25%), EAS (25%), EUR (25%), SAS (25%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: AFR (25%), EAS (25%), EUR (25%), SAS (25%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | 23andMe CHB DBDS EB FinnGen UKB deCODE | UKB | UKB | UKB | UKB | 23andMe CHB DBDS EB FinnGen UKB deCODE | 23andMe CHB DBDS EB FinnGen UKB deCODE | Agent Input |
| publication.title | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Leveraging fine-mapping and multipopulation training data to improve cross-population polygenic risk scores. | Genetic variation associated with thyroid autoimmunity shapes the systemic immune response to PD-1 checkpoint blockade. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Leveraging fine-mapping and multipopulation training data to improve cross-population polygenic risk scores. | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Commun | Am J Hum Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2025-11-10 | 2022-06-09 | 2021-06-11 | 2022-01-10 | 2022-06-09 | 2025-11-10 | 2025-11-10 | Agent Input |
| variants_number | 1110091 | 1109311 | 1099649 | 632597 | 889041 | 1110091 | 1110091 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4 | age, sex, age*sex, assessment center, genotyping array, 10 PCs | 5 genotype PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, age*sex, assessment center, genotyping array, 10 PCs | age, sex, PC1, PC2, PC3, PC4 | age, sex, PC1, PC2, PC3, PC4 | Agent Input |


### lung carcinoma

Candidate pool: `20` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004860 | PGS002270 | PGS000721 | PGS004325 | PGS004884 | PGS004860 | PGS004884 | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | 1/20 | 5/20 | Benchmark Only |
| AoU benchmark AUC | 0.5597 | 0.5595 | 0.5521 | 0.5521 | 0.5511 | 0.5597 | 0.5511 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Agent Input |
| trait_efo | lung carcinoma | lung carcinoma | lung carcinoma | lung carcinoma | lung carcinoma | lung carcinoma | lung carcinoma | Agent Input |
| phenotyping_reported | Incident lung cancer | Incident lung cancer | Incident lung cancer | Lung carcinogenesis (in smokers) | Incident lung cancer | Incident lung cancer | Incident lung cancer | Agent Input |
| method_name | LDpred2 | Genome-wide significant variants | Genome-wide significant variants | Genome-wide significant SNPs | megaprs.auto | LDpred2 | megaprs.auto | Agent Input |
| performance_metrics.selected_performance_id | PPM021091 | PPM012923 | PPM001650 | PPM020438 | PPM021250 | PPM021091 | PPM021250 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 4 | 2 | 7 | 1 | 7 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8930 | N/A | 0.5910 | N/A | 0.6200 | 0.8930 | 0.6200 | Agent Input |
| performance_metrics.full_model_r2 | 0.4900 | N/A | N/A | N/A | N/A | 0.4900 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.893, 'ci_lower': 0.887, 'ci_upper': 0.898} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.591, 'ci_lower': 0.576, 'ci_upper': 0.606} | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.62, 'ci_lower': 0.61, 'ci_upper': 0.63} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.893, 'ci_lower': 0.887, 'ci_upper': 0.898} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.62, 'ci_lower': 0.61, 'ci_upper': 0.63} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.49} | N/A | N/A | {'name_long': 'Hazard ratio (HR, highest PRS quintile and heavy smokers vs lowest PRS quintile and never smokers)', 'name_short': 'Hazard ratio (HR, highest PRS quintile and heavy smokers vs lowest PRS quintile and never smokers)', 'estimate': 4.63, 'ci_lower': 3.0, 'ci_upper': 7.13} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.49} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.11, 'ci_upper': 1.22} | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.24, 'ci_lower': 1.2, 'ci_upper': 1.28} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.24, 'ci_lower': 1.2, 'ci_upper': 1.28} | Agent Input |
| validation_sample_size | n=24,012 | n=345,794 | n=400,812 | n=308,490 | n=277,400 | n=24,012 | n=277,400 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=404 | N/A | n=404 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (20%), EUR (80%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EAS (33%), EUR (67%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (27%), EUR (73%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (27%), EUR (73%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | BBJ GAME-ON GELCAPS GLC IARC ICR ILCCO MDACC MRC NCI SLRI TRICL | ATBC B58C CARET EAGLE GAME-ON GECCO GELCAPS GLC HGF HUNT2 Harvard IARC ICR-GWAS LLP MDACCS NCI PLCO SLRI Tromso UKBS WTCCC deCODE | N/A | 1000G | N/A | 1000G | Agent Input |
| publication.title | Polygenic inheritance and its interplay with smoking history in predicting lung cancer diagnosis: a French-Canadian case-control cohort. | Association of smoking and polygenic risk with the incidence of lung cancer: a prospective cohort study. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Association of oxidative stress, programmed cell death, GSTM1 gene polymorphisms, smoking and the risk of lung carcinogenesis: A two-step Mendelian randomization study. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Polygenic inheritance and its interplay with smoking history in predicting lung cancer diagnosis: a French-Canadian case-control cohort. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Agent Input |
| publication.journal | EBioMedicine | Br J Cancer | JNCI Cancer Spectr | Front Physiol | Nat Commun | EBioMedicine | Nat Commun | Agent Input |
| date_release | 2024-07-31 | 2022-04-01 | 2021-02-03 | 2024-01-11 | 2024-06-27 | 2024-07-31 | 2024-06-27 | Agent Input |
| variants_number | 1143554 | 33 | 19 | 19 | 655479 | 1143554 | 655479 | Agent Input |
| covariates | Sex, age,BMI, smocking status(ever or never smoker), and the first 10 ancestry-based PCA | Age, sex, education, Townsend deprivation index, income, BMI, diet, physical activity, alcohol consumption, occupational exposure, passive smoking, relatedness and first 20 principal components of ancestry | Genotyping array | Education, sex, genotype array, and the first ten important components | PCs 1-10 | Sex, age,BMI, smocking status(ever or never smoker), and the first 10 ancestry-based PCA | PCs 1-10 | Agent Input |


### urinary bladder carcinoma

Candidate pool: `19` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000152 | PGS001807 | PGS000782 | PGS000071 | PGS000613 | PGS000071 | PGS000782 | Agent Input |
| AoU benchmark rank | 1/19 | 2/19 | 3/19 | 4/19 | 5/19 | 4/19 | 3/19 | Benchmark Only |
| AoU benchmark AUC | 0.5682 | 0.5583 | 0.5565 | 0.5565 | 0.5534 | 0.5565 | 0.5565 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Agent Input |
| trait_efo | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | Agent Input |
| phenotyping_reported | Bladder cancer | Cancer of bladder | Incident blader cancer | Bladder cancer | Cancer of bladder | Bladder cancer | Incident blader cancer | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Penalized regression (bigstatsr) | 15 variants from Graff et al (PGS000071) with inverse variant weights | Genome-wide significant variants | Pruning and Thresholding (P+T) | Genome-wide significant variants | 15 variants from Graff et al (PGS000071) with inverse variant weights | Agent Input |
| performance_metrics.selected_performance_id | PPM000472 | PPM009359 | PPM002053 | PPM000191 | PPM001298 | PPM000191 | PPM002053 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 8 | 1 | 3 | 1 | 3 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.8040 | N/A | 0.5710 | N/A | 0.8040 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.6280 | N/A | 0.0125 | N/A | 0.6280 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.804} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.814, 'se': 0.008} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.571, 'ci_lower': 0.555, 'ci_upper': 0.588} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.804} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.814, 'se': 0.008} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Mean realative risk', 'name_short': 'Mean realative risk', 'estimate': 1.04, 'ci_lower': 1.0, 'ci_upper': 1.08} {'name_long': 'Wilcoxon test (case vs. control) p-value', 'name_short': 'Wilcoxon test (case vs. control) p-value', 'estimate': 0.00377} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0197, 'ci_lower': 0.0058, 'ci_upper': 0.0336} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.628} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0125} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.91, 'ci_lower': 1.99, 'ci_upper': 4.24} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.628} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.3, 'ci_lower': 1.22, 'ci_upper': 1.39} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.3, 'ci_lower': 1.25, 'ci_upper': 1.36} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.301, 'ci_lower': 1.227, 'ci_upper': 1.379} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.263, 'se': 0.0299} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.3, 'ci_lower': 1.25, 'ci_upper': 1.36} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.3, 'ci_lower': 1.22, 'ci_upper': 1.39} | Agent Input |
| validation_sample_size | n=13,770 | n=19,893 | n=391,888 | n=412,602 | n=13,530 | n=412,602 | n=391,888 | Agent Input |
| samples_training | N/A | n=391,124 | N/A | N/A | n=12,992 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ICR NBCS NBS UMC deCODE | UKB | ASHRAM ATBC BBCS_b CPSII DBCS EAGLE EPIC FPCC FrBCS HPFS IBCS ICR LABCS LBCS MEC MSKBCS NBCS NBS NCBCS NEBCS NHS NeuBCS PLCO SANBCS SBCS SpBCS TBCS TXBCS UMC WHI deCODE | ATBC BBCS_b CPSII EAGLE EPIC FPCC FrBCS HPFS ICR LABCS MEC NBCS NBS NEBCS NHS PLCO SpBCS TXBCS UMC WHI deCODE | UKB | ATBC BBCS_b CPSII EAGLE EPIC FPCC FrBCS HPFS ICR LABCS MEC NBCS NBS NEBCS NHS PLCO SpBCS TXBCS UMC WHI deCODE | ASHRAM ATBC BBCS_b CPSII DBCS EAGLE EPIC FPCC FrBCS HPFS IBCS ICR LABCS LBCS MEC MSKBCS NBCS NBS NCBCS NEBCS NHS NeuBCS PLCO SANBCS SBCS SpBCS TBCS TXBCS UMC WHI deCODE | Agent Input |
| publication.title | Systematic evaluation of cancer-specific genetic risk score for 11 types of cancer in The Cancer Genome Atlas and Electronic Medical Records and Genomics cohorts. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Agent Input |
| publication.journal | Cancer Med | Am J Hum Genet | Nat Commun | Nat Commun | Am J Hum Genet | Nat Commun | Nat Commun | Agent Input |
| date_release | 2020-04-29 | 2022-01-10 | 2021-05-28 | 2020-02-12 | 2020-12-15 | 2020-02-12 | 2021-05-28 | Agent Input |
| variants_number | 10 | 291 | 15 | 15 | 15 | 15 | 15 | Agent Input |
| covariates | Unknown | sex, age, birth date, deprivation index, 16 PCs | Age at assessment, sex, genotyping array, PCs(1-15), cigarette pack-years, smoking status(never vs. former vs. current), body mass index | Genotyping reagent kit (GERA cohort only), genotyping array (UK Biobank only), age, sex, 10 PCs. | age, sex, batch PCs 1-4 | Genotyping reagent kit (GERA cohort only), genotyping array (UK Biobank only), age, sex, 10 PCs. | Age at assessment, sex, genotyping array, PCs(1-15), cigarette pack-years, smoking status(never vs. former vs. current), body mass index | Agent Input |


### heart failure

Candidate pool: `16` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005097 | PGS001790 | PGS005299 | PGS004532 | PGS005303 | PGS005097 | PGS001790 | Agent Input |
| AoU benchmark rank | 1/16 | 2/16 | 3/16 | 4/16 | 5/16 | 1/16 | 2/16 | Benchmark Only |
| AoU benchmark AUC | 0.6015 | 0.5752 | 0.5726 | 0.5595 | 0.5444 | 0.6015 | 0.5752 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Heart failure | Heart failure | Heart failure | I50 (Heart failure) | Heart failure | Heart failure | Heart failure | Agent Input |
| trait_efo | heart failure | heart failure | heart failure | heart failure | heart failure | heart failure | heart failure | Agent Input |
| phenotyping_reported | Prevalent heart failure | Heart Failure | Prevalent heart failure | I50 (Heart failure) | Prevalent heart failure | Prevalent heart failure | Heart Failure | Agent Input |
| method_name | PRS-CSx | PRS-CS-auto | LDpred2 | RFDiseasemetaPRS | LDpred2 | PRS-CSx | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | PPM022207 | PPM009294 | PPM023007 | PPM020647 | PPM023011 | PPM022207 | PPM009294 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African unspecified | European | European | European | European | European, African unspecified | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | 0.0070 | N/A | N/A | N/A | N/A | 0.0070 | Agent Input |
| performance_metrics.full_model_auc | 0.7200 | 0.7500 | 0.6160 | N/A | 0.6130 | 0.7200 | 0.7500 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0345 | N/A | 0.0327 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.72, 'ci_lower': 0.72, 'ci_upper': 0.73} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.616} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.613} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.72, 'ci_lower': 0.72, 'ci_upper': 0.73} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.75} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Brier skill score', 'name_short': 'Brier skill score', 'estimate': 0.065, 'ci_lower': 0.063, 'ci_upper': 0.068} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.006981} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03455} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03272} | {'name_long': 'Brier skill score', 'name_short': 'Brier skill score', 'estimate': 0.065, 'ci_lower': 0.063, 'ci_upper': 0.068} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.006981} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.267132} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=40,989 | n=358,905 | n=12,677 | n=56,192 | n=12,677 | n=40,989 | n=358,905 | Agent Input |
| samples_training | N/A | N/A | N/A | n=174,489 | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (6%), AMR (3%), EAS (11%), EUR (80%) / EVAL: MAE (100%) | GWAS: AFR (3%), ASN (2%), EAS (28%), EUR (65%), OTH (2%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (6%), AMR (3%), EAS (11%), EUR (80%) / EVAL: MAE (100%) | GWAS: AFR (3%), ASN (2%), EAS (28%), EUR (65%), OTH (2%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ BioMe CKB FinnGen GBMI HERMES MVP MyCode UCLA eMERGE | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT MGBB MGI UCLA | N/A | UKB | N/A | BBJ BioMe CKB FinnGen GBMI HERMES MVP MyCode UCLA eMERGE | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT MGBB MGI UCLA | Agent Input |
| publication.title | Common-variant and rare-variant genetic architecture of heart failure across the allele-frequency spectrum. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Genetic analyses across cardiovascular traits: leveraging genetic correlations to empower locus discovery and prediction in common cardiovascular diseases. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Genetic analyses across cardiovascular traits: leveraging genetic correlations to empower locus discovery and prediction in common cardiovascular diseases. | Common-variant and rare-variant genetic architecture of heart failure across the allele-frequency spectrum. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | Nat Genet | Cell Genom | NPJ Genom Med | Commun Biol | NPJ Genom Med | Nat Genet | Cell Genom | Agent Input |
| date_release | 2025-04-17 | 2022-09-08 | 2025-12-18 | 2024-03-18 | 2025-12-18 | 2025-04-17 | 2022-09-08 | Agent Input |
| variants_number | 1274692 | 910146 | 923722 | 1059939 | 1042531 | 1274692 | 910146 | Agent Input |
| covariates | Age, sex, 5 genetic principal components | sex,age,age2,age*sex,age^2*sex, 20PCs | age, sex, four first principal components of genetic ancestry | Unknown | age, sex, four first principal components of genetic ancestry | Age, sex, 5 genetic principal components | sex,age,age2,age*sex,age^2*sex, 20PCs | Agent Input |


### testicular carcinoma

Candidate pool: `13` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000796 | PGS000086 | PGS000600 | PGS001164 | PGS000599 | PGS000796 | PGS000796 | Agent Input |
| AoU benchmark rank | 1/13 | 2/13 | 3/13 | 4/13 | 5/13 | 1/13 | 1/13 | Benchmark Only |
| AoU benchmark AUC | 0.9212 | 0.9182 | 0.9128 | 0.9044 | 0.9021 | 0.9212 | 0.9212 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Testicular cancer | Testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Testicular cancer | Testicular cancer | Agent Input |
| trait_efo | testicular cancer, testicular germ cell tumor | testicular cancer, testicular germ cell tumor | testicular cancer | testicular cancer | testicular cancer | testicular cancer, testicular germ cell tumor | testicular cancer, testicular germ cell tumor | Agent Input |
| phenotyping_reported | Incident testicular cancer | Incident testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Incident testicular cancer | Incident testicular cancer | Agent Input |
| method_name | 52 variants from Graff et al (PGS000086) with inverse variant weights | Genome-wide significant variants | lassosum | snpnet | Pruning and Thresholding (P+T) | 52 variants from Graff et al (PGS000086) with inverse variant weights | 52 variants from Graff et al (PGS000086) with inverse variant weights | Agent Input |
| performance_metrics.selected_performance_id | PPM002067 | PPM002051 | PPM001285 | PPM008544 | PPM001284 | PPM002067 | PPM002067 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 1 | 3 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.6296 | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0157 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7870 | 0.7830 | 0.6360 | 0.8391 | 0.6370 | 0.7870 | 0.7870 | Agent Input |
| performance_metrics.full_model_r2 | 0.6050 | N/A | 0.0460 | 0.1291 | 0.0473 | 0.6050 | 0.6050 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | 0.0313 | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.787} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.766, 'se': 0.033} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.783} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.034} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.636, 'ci_lower': 0.565, 'ci_upper': 0.698} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.83915, 'ci_lower': 0.8185, 'ci_upper': 0.85981} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.637, 'ci_lower': 0.568, 'ci_upper': 0.703} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.787} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.766, 'se': 0.033} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.787} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.766, 'se': 0.033} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.605} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.046} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0839} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 6.35, 'ci_lower': 1.81, 'ci_upper': 22.3} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1291} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03126} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01573} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62956, 'ci_lower': 0.58302, 'ci_upper': 0.67611} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0473} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0844} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.35, 'ci_lower': 1.08, 'ci_upper': 17.5} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.605} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.605} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.26, 'ci_lower': 1.71, 'ci_upper': 2.99} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.18, 'ci_lower': 1.66, 'ci_upper': 2.87} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.619, 'ci_lower': 1.267, 'ci_upper': 2.067} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.482, 'se': 0.125} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.628, 'ci_lower': 1.281, 'ci_upper': 2.069} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.487, 'se': 0.122} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.26, 'ci_lower': 1.71, 'ci_upper': 2.99} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.26, 'ci_lower': 1.71, 'ci_upper': 2.99} | Agent Input |
| validation_sample_size | n=179,537 | n=179,537 | n=755 | n=67,425 | n=755 | n=179,537 | n=179,537 | Agent Input |
| samples_training | N/A | N/A | n=776 | n=269,704 | n=776 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | B58C BCAC FCCC NCI Penn PennCATH SEARCH Sweden UKBS UKGPCS UKTCC UPENN | B58C FCCC NCI PennCATH UKBS UKTCC UPENN | MGI | UKB | MGI | B58C BCAC FCCC NCI Penn PennCATH SEARCH Sweden UKBS UKGPCS UKTCC UPENN | B58C BCAC FCCC NCI Penn PennCATH SEARCH Sweden UKBS UKGPCS UKTCC UPENN | Agent Input |
| publication.title | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Am J Hum Genet | PLoS Genet | Am J Hum Genet | Nat Commun | Nat Commun | Agent Input |
| date_release | 2021-05-28 | 2020-02-12 | 2020-12-15 | 2021-10-21 | 2020-12-15 | 2021-05-28 | 2021-05-28 | Agent Input |
| variants_number | 52 | 52 | 250 | 280 | 31 | 52 | 52 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15) | Age at assessment, genotyping array, PCs(1-15) | age, sex, batch PCs 1-4 | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | Age at assessment, genotyping array, PCs(1-15) | Age at assessment, genotyping array, PCs(1-15) | Agent Input |


### osteoporosis

Candidate pool: `11` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002768 | PGS001274 | PGS001273 | PGS004560 | PGS002095 | PGS002768 | PGS002768 | Agent Input |
| AoU benchmark rank | 1/11 | 2/11 | 3/11 | 4/11 | 5/11 | 1/11 | 1/11 | Benchmark Only |
| AoU benchmark AUC | 0.5633 | 0.5603 | 0.5479 | 0.5473 | 0.5449 | 0.5633 | 0.5633 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Osteoporosis | Osteoporosis without pathological fracture (time-to-event) | Osteoporosis | M81 (Osteoporosis without pathological fracture) | Osteoporosis | Osteoporosis | Osteoporosis | Agent Input |
| trait_efo | heel bone mineral density, osteoporosis | osteoporosis | osteoporosis | osteoporosis | osteoporosis | heel bone mineral density, osteoporosis | heel bone mineral density, osteoporosis | Agent Input |
| phenotyping_reported | Osteoporosis | TTE osteoporosis without pathological fracture | Osteoporosis | M81 (Osteoporosis without pathological fracture) | Osteoporosis | Osteoporosis | Osteoporosis | Agent Input |
| method_name | PRS-CS | snpnet | snpnet | RFDiseasemetaPRS | LDpred2 (bigsnpr) | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM014968 | PPM008872 | PPM008867 | PPM020675 | PPM011616 | PPM014968 | PPM014968 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 5 | 5 | 1 | 8 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | 0.5742 | 0.5684 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | 0.0089 | 0.0070 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.7749 | 0.7643 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.1278 | 0.1146 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | 0.0080 | 0.0059 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.77492, 'ci_lower': 0.76604, 'ci_upper': 0.7838} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7643, 'ci_lower': 0.75478, 'ci_upper': 0.77381} | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.12779} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00797} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0089} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57419, 'ci_lower': 0.56237, 'ci_upper': 0.586} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1146} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00589} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00698} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.5684, 'ci_lower': 0.55603, 'ci_upper': 0.58076} | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0268, 'ci_lower': 0.013, 'ci_upper': 0.0407} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.25, 'ci_upper': 1.38} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.320825} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.25, 'ci_upper': 1.38} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.25, 'ci_upper': 1.38} | Agent Input |
| validation_sample_size | n=39,444 | n=67,425 | n=67,425 | n=56,192 | n=19,982 | n=39,444 | n=39,444 | Agent Input |
| samples_training | N/A | n=269,704 | n=269,704 | n=174,489 | n=391,124 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | UKB | UKB | UKB | UKB | N/A | N/A | Agent Input |
| publication.title | Systematic comparison of family history and polygenic risk across 24 common diseases. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Systematic comparison of family history and polygenic risk across 24 common diseases. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | PLoS Genet | Commun Biol | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2022-11-07 | 2021-10-21 | 2021-10-21 | 2024-03-18 | 2022-01-10 | 2022-11-07 | 2022-11-07 | Agent Input |
| variants_number | 1091549 | 1270 | 316 | 1059939 | 658775 | 1091549 | 1091549 | Agent Input |
| covariates | age, sex, 10 PCs, technical covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Unknown | sex, age, birth date, deprivation index, 16 PCs | age, sex, 10 PCs, technical covariates | age, sex, 10 PCs, technical covariates | Agent Input |


### parkinson disease

Candidate pool: `11` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000903 | PGS004924 | PGS000902 | PGS000750 | PGS003763 | PGS000903 | PGS000903 | Agent Input |
| AoU benchmark rank | 1/11 | 2/11 | 3/11 | 4/11 | 5/11 | 1/11 | 1/11 | Benchmark Only |
| AoU benchmark AUC | 0.5616 | 0.5523 | 0.5500 | 0.5430 | 0.5421 | 0.5616 | 0.5616 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Agent Input |
| trait_efo | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Agent Input |
| phenotyping_reported | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Incident Parkinson Disease | Parkinson's disease | Parkinson's disease | Agent Input |
| method_name | Clumping and Thresholding (C+T) | Genome-wide significant SNPs | Genome-wide significant variants | Genome-wide significant variants | Genome-wide significant SNPs | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM012831 | PPM021702 | PPM018547 | PPM001904 | PPM018563 | PPM012831 | PPM012831 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European, African unspecified, Not reported | Other, European | European, NR | European | European | European | Agent Input |
| performance_metrics.record_count | 5 | 2 | 6 | 3 | 2 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6450 | N/A | N/A | 0.7030 | N/A | 0.6450 | 0.6450 | Agent Input |
| performance_metrics.full_model_r2 | 0.3480 | N/A | N/A | N/A | N/A | 0.3480 | 0.3480 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.645, 'ci_lower': 0.63, 'ci_upper': 0.66} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.703, 'ci_lower': 0.698, 'ci_upper': 0.708} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.645, 'ci_lower': 0.63, 'ci_upper': 0.66} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.645, 'ci_lower': 0.63, 'ci_upper': 0.66} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Nagelkerke’s Pseudo-R2', 'name_short': 'Nagelkerke’s Pseudo-R2', 'estimate': 0.348} | {'name_long': 'Odds ratio (OR, top vs bottom PGS quartile)', 'name_short': 'Odds ratio (OR, top vs bottom PGS quartile)', 'estimate': 3.79, 'ci_lower': 1.64, 'ci_upper': 8.73} | N/A | N/A | {'name_long': 'Hazard ratio (HR, high vs low tertile)', 'name_short': 'Hazard ratio (HR, high vs low tertile)', 'estimate': 1.72, 'ci_lower': 1.54, 'ci_upper': 1.93} | {'name_long': 'Nagelkerke’s Pseudo-R2', 'name_short': 'Nagelkerke’s Pseudo-R2', 'estimate': 0.348} | {'name_long': 'Nagelkerke’s Pseudo-R2', 'name_short': 'Nagelkerke’s Pseudo-R2', 'estimate': 0.348} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.575, 'ci_lower': 1.444, 'ci_upper': 1.717} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.4541, 'se': 0.0443} | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=6,378 | n=3,482 | n=3,427 | n=486 | n=314,998 | n=6,378 | n=6,378 | Agent Input |
| samples_training | n=1,473,098 | N/A | n=1,473,098 | N/A | N/A | n=1,473,098 | n=1,473,098 | Agent Input |
| ancestry_distribution | GWAS: MAE (100%) / DEV: MAE (100%) / EVAL: EUR (33%), MAE (33%), SAS (33%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: MAE (100%) / DEV: MAE (100%) / EVAL: NR (40%), MAE (60%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / DEV: MAE (100%) / EVAL: EUR (33%), MAE (33%), SAS (33%) | GWAS: MAE (100%) / DEV: MAE (100%) / EVAL: EUR (33%), MAE (33%), SAS (33%) | Agent Input |
| training_development_cohorts | 23andMe HBS IPDGC PDBP PPMI UKB | N/A | 23andMe HBS IPDGC PDBP PPMI UKB | N/A | N/A | 23andMe HBS IPDGC PDBP PPMI UKB | 23andMe HBS IPDGC PDBP PPMI UKB | Agent Input |
| publication.title | Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. | Polygenic risk score for Parkinson's disease and olfaction among middle-aged to older women. | Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. | Excess of singleton loss-of-function variants in Parkinson's disease contributes to genetic risk. | Physical Frailty, Genetic Predisposition, and Incident Parkinson Disease. | Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. | Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. | Agent Input |
| publication.journal | Lancet Neurol | Parkinsonism Relat Disord | Lancet Neurol | J Med Genet | JAMA Neurol | Lancet Neurol | Lancet Neurol | Agent Input |
| date_release | 2021-09-17 | 2024-07-31 | 2021-09-17 | 2021-03-22 | 2023-08-04 | 2021-09-17 | 2021-09-17 | Agent Input |
| variants_number | 1805 | 90 | 90 | 43 | 44 | 1805 | 1805 | Agent Input |
| covariates | sex, age and first three PCs | Age, race, 5 PCs, self-reported sense of smell, education, smoking status, self-reported health status, and PM2.5 and NO2 in 2006 | Unknown | Sex, singleton loss of function variant count, Parkinson's disease family history. | genotyping array and the first 10 principal components of ancestry | sex, age and first three PCs | sex, age and first three PCs | Agent Input |


### celiac disease

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000040 | PGS001856 | PGS004930 | PGS001894 | PGS002067 | PGS000040 | PGS000316 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 1/10 | 10/10 | Benchmark Only |
| AoU benchmark AUC | 0.5900 | 0.5891 | 0.5887 | 0.5861 | 0.5855 | 0.5900 | 0.5172 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Coeliac disease | Celiac disease | Celiac disease | Diagnosed with coeliac disease or gluten sensitivity | Celiac disease | Coeliac disease | Coeliac disease | Agent Input |
| trait_efo | celiac disease | celiac disease | celiac disease | celiac disease | celiac disease | celiac disease | celiac disease | Agent Input |
| phenotyping_reported | Coeliac disease | Celiac disease | Celiac disease | Diagnosed with coeliac disease or gluten sensitivity | Celiac disease | Coeliac disease | Coeliac disease | Agent Input |
| method_name | SparSNP | Penalized regression (bigstatsr) | SnpNet | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | SparSNP | Log‐additive GRS | Agent Input |
| performance_metrics.selected_performance_id | PPM000097 | PPM009738 | PPM021718 | PPM010036 | PPM011398 | PPM000097 | PPM000804 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 7 | 7 | 1 | 7 | 7 | 7 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8700 | N/A | 0.6700 | N/A | N/A | 0.8700 | 0.8790 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.87} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.87} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.879, 'ci_lower': 0.87, 'ci_upper': 0.888} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.1196, 'ci_lower': 0.1043, 'ci_upper': 0.1348} | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0993, 'ci_lower': 0.0763, 'ci_upper': 0.1223} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.1241, 'ci_lower': 0.1088, 'ci_upper': 0.1393} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.52, 'ci_lower': 1.35, 'ci_upper': 1.71} | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=10,304 | n=16,106 | n=8,417 | n=7,142 | n=16,106 | n=10,304 | n=379,767 | Agent Input |
| samples_training | n=6,785 | n=391,124 | n=285,899 | n=391,124 | n=391,124 | n=6,785 | n=24,269 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: NR (50%), EUR (50%) | Agent Input |
| training_development_cohorts | B58C | UKB | UKB | UKB | UKB | B58C | B58C UKBS | Agent Input |
| publication.title | Accurate and robust genomic prediction of celiac disease using statistical learning. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Polygenic risk score portability for common diseases across genetically diverse populations. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Accurate and robust genomic prediction of celiac disease using statistical learning. | A single nucleotide polymorphism genetic risk score to aid diagnosis of coeliac disease: a pilot study in clinical care. | Agent Input |
| publication.journal | PLoS Genet | Am J Hum Genet | Human Genomics | Am J Hum Genet | Am J Hum Genet | PLoS Genet | Aliment Pharmacol Ther | Agent Input |
| date_release | 2019-12-18 | 2022-01-10 | 2024-09-19 | 2022-01-10 | 2022-01-10 | 2019-12-18 | 2020-08-19 | Agent Input |
| variants_number | 228 | 1661 | 463 | 484 | 58231 | 228 | 53 | Agent Input |
| covariates | Unknown | sex, age, birth date, deprivation index, 16 PCs | Unknown | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | Unknown | Agent Input |


### dementia

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004283 | PGS004281 | PGS000945 | PGS000929 | PGS004284 | PGS004281 | PGS004281 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 2/10 | 2/10 | Benchmark Only |
| AoU benchmark AUC | 0.5625 | 0.5591 | 0.5523 | 0.5515 | 0.5474 | 0.5591 | 0.5591 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | All-cause dementia | All-cause dementia | Dementia in Alzheimer's disease (time-to-event) | All-cause dementia (algorithmically-defined) | All-cause dementia | All-cause dementia | All-cause dementia | Agent Input |
| trait_efo | dementia | dementia | dementia, Alzheimer disease | dementia | dementia | dementia | dementia | Agent Input |
| phenotyping_reported | All-cause dementia | All-cause dementia | TTE dementia in alzheimer's disease | AD all cause dementia | All-cause dementia | All-cause dementia | All-cause dementia | Agent Input |
| method_name | GenoBoost | GenoBoost | snpnet | snpnet | GenoBoost | GenoBoost | GenoBoost | Agent Input |
| performance_metrics.selected_performance_id | PPM020351 | PPM020349 | PPM007554 | PPM007476 | PPM020352 | PPM020349 | PPM020349 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 4 | 5 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.7527 | 0.6270 | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0654 | 0.0235 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8182 | 0.8190 | 0.8916 | 0.8156 | 0.8189 | 0.8190 | 0.8190 | Agent Input |
| performance_metrics.full_model_r2 | 0.0338 | 0.0342 | 0.1668 | 0.1165 | 0.0342 | 0.0342 | 0.0342 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0546 | 0.0229 | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.81816338026915} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.818965564821918} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8916, 'ci_lower': 0.86249, 'ci_upper': 0.9207} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.81557, 'ci_lower': 0.79434, 'ci_upper': 0.8368} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.818864171341326} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.818965564821918} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.818965564821918} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Covariate-adjusted pseudo-R2', 'name_short': 'Covariate-adjusted pseudo-R2', 'estimate': 0.0338087996870553} {'name_long': 'AUPRC', 'name_short': 'AUPRC', 'estimate': 0.81816338026915} | {'name_long': 'Covariate-adjusted pseudo-R2', 'name_short': 'Covariate-adjusted pseudo-R2', 'estimate': 0.0341767843321088} {'name_long': 'AUPRC', 'name_short': 'AUPRC', 'estimate': 0.818965564821918} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.16679} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05458} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.06543} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.75273, 'ci_lower': 0.69847, 'ci_upper': 0.80699} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11649} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02294} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02346} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62703, 'ci_lower': 0.59629, 'ci_upper': 0.65777} | {'name_long': 'Covariate-adjusted pseudo-R2', 'name_short': 'Covariate-adjusted pseudo-R2', 'estimate': 0.0341516519974033} {'name_long': 'AUPRC', 'name_short': 'AUPRC', 'estimate': 0.818864171341326} | {'name_long': 'Covariate-adjusted pseudo-R2', 'name_short': 'Covariate-adjusted pseudo-R2', 'estimate': 0.0341767843321088} {'name_long': 'AUPRC', 'name_short': 'AUPRC', 'estimate': 0.818965564821918} | {'name_long': 'Covariate-adjusted pseudo-R2', 'name_short': 'Covariate-adjusted pseudo-R2', 'estimate': 0.0341767843321088} {'name_long': 'AUPRC', 'name_short': 'AUPRC', 'estimate': 0.818965564821918} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=67,428 | n=67,428 | n=67,425 | n=67,425 | n=67,428 | n=67,428 | n=67,428 | Agent Input |
| samples_training | n=269,710 | n=269,710 | n=269,704 | n=269,704 | n=269,710 | n=269,710 | n=269,710 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | A polygenic score method boosted by non-additive models. | A polygenic score method boosted by non-additive models. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | A polygenic score method boosted by non-additive models. | A polygenic score method boosted by non-additive models. | A polygenic score method boosted by non-additive models. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | PLoS Genet | PLoS Genet | Nat Commun | Nat Commun | Nat Commun | Agent Input |
| date_release | 2024-06-12 | 2024-06-12 | 2021-10-21 | 2021-10-21 | 2024-06-12 | 2024-06-12 | 2024-06-12 | Agent Input |
| variants_number | 90 | 110 | 26 | 6 | 50 | 110 | 110 | Agent Input |
| covariates | age, sex, PC1-10 | age, sex, PC1-10 | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, PC1-10 | age, sex, PC1-10 | age, sex, PC1-10 | Agent Input |


### obesity

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005235 | PGS005154 | PGS003959 | PGS002033 | PGS005145 | PGS005235 | PGS005154 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 1/10 | 2/10 | Benchmark Only |
| AoU benchmark AUC | 0.6479 | 0.6331 | 0.5909 | 0.5833 | 0.5771 | 0.6479 | 0.6331 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Adiposity | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | Adiposity | Obesity | Agent Input |
| trait_efo | obesity disorder | obesity disorder | obesity disorder | overweight body mass index status, overnutrition, obesity disorder | obesity disorder | obesity disorder | obesity disorder | Agent Input |
| phenotyping_reported | Obesity (phecode: 278.1) | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | Obesity (phecode: 278.1) | Obesity | Agent Input |
| method_name | LDpred2-auto | CT-SLEB | Genome-wide significant SNPs | LDpred2 (bigsnpr) | PRS-CS | LDpred2-auto | CT-SLEB | Agent Input |
| performance_metrics.selected_performance_id | PPM022667 | PPM022374 | PPM019107 | PPM011135 | PPM022365 | PPM022667 | PPM022374 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | East Asian | European, Not reported | European | East Asian | European | East Asian | Agent Input |
| performance_metrics.record_count | 2 | 1 | 7 | 8 | 1 | 2 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0789, 'ci_lower': 0.0651, 'ci_upper': 0.0927} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.9704649488977} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 1.76187749677908} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.149, 'se': 0.028} | N/A | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 1.60817500694587} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.9704649488977} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 1.76187749677908} | Agent Input |
| validation_sample_size | n=100,960 | n=58,688 | n=27,429 | n=20,000 | n=58,688 | n=100,960 | n=58,688 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (19%), EUR (81%) / EVAL: EAS (100%) | GWAS: NR (33%), EUR (67%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EAS (100%) / EVAL: EAS (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (19%), EUR (81%) / EVAL: EAS (100%) | Agent Input |
| training_development_cohorts | EGG GIANT UKB | BBJ | N/A | UKB | BBJ | EGG GIANT UKB | BBJ | Agent Input |
| publication.title | Modeling the genomic architecture of adiposity and anthropometrics across the lifespan. | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | The sulfur microbial diet and increased risk of obesity: Findings from a population-based prospective cohort study. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | Modeling the genomic architecture of adiposity and anthropometrics across the lifespan. | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | Agent Input |
| publication.journal | Nat Commun | Commun Biol | Clin Nutr | Am J Hum Genet | Commun Biol | Nat Commun | Commun Biol | Agent Input |
| date_release | 2025-10-06 | 2025-03-17 | 2023-10-17 | 2022-01-10 | 2025-03-17 | 2025-10-06 | 2025-03-17 | Agent Input |
| variants_number | 709828 | 443124 | 940 | 846292 | 908466 | 709828 | 443124 | Agent Input |
| covariates | age, sex, batch, and the first 10 genetic principal components | age, sex | Age, sex, race, centres, education, Townsend deprivation index, household income, smoking, alcohol consumption, physical activity, sleep pattern, energy intake, and BMI, WC or BF% at baseline | sex, age, birth date, deprivation index, 16 PCs | age, sex | age, sex, batch, and the first 10 genetic principal components | age, sex | Agent Input |


### pancreatic carcinoma

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000663 | PGS000794 | PGS000083 | PGS004250 | PGS000725 | PGS000794 | PGS000794 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 2/10 | 2/10 | Benchmark Only |
| AoU benchmark AUC | 0.5690 | 0.5682 | 0.5659 | 0.5657 | 0.5613 | 0.5682 | 0.5682 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Pancreatic cancer | Pancreatic cancer | Pancreatic cancer | Pancreatic cancer | Pancreatic cancer | Pancreatic cancer | Pancreatic cancer | Agent Input |
| trait_efo | exocrine pancreatic carcinoma | exocrine pancreatic carcinoma | exocrine pancreatic carcinoma | exocrine pancreatic carcinoma | exocrine pancreatic carcinoma | exocrine pancreatic carcinoma | exocrine pancreatic carcinoma | Agent Input |
| phenotyping_reported | Pancreatic cancer | Incident pancreatic cancer | Incident pancreatic cancer | Pancreatic cancer | Incident Pancreatic cancer | Incident pancreatic cancer | Incident pancreatic cancer | Agent Input |
| method_name | Genome-wide significant variants | 22 variants from Graff et al (PGS000083) with inverse variant weights | Genome-wide significant variants | PRSice-2 | Genome-wide significant variants | 22 variants from Graff et al (PGS000083) with inverse variant weights | 22 variants from Graff et al (PGS000083) with inverse variant weights | Agent Input |
| performance_metrics.selected_performance_id | PPM001369 | PPM002065 | PPM002049 | PPM020307 | PPM001655 | PPM002065 | PPM002065 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 5 | 1 | 3 | 2 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6500 | 0.7450 | 0.7450 | N/A | 0.6390 | 0.7450 | 0.7450 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.4390 | N/A | N/A | N/A | 0.4390 | 0.4390 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.743, 'se': 0.012} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.742, 'se': 0.012} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.639, 'ci_lower': 0.613, 'ci_upper': 0.664} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.743, 'se': 0.012} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.743, 'se': 0.012} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.439} | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.439} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.439} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37, 'ci_lower': 1.22, 'ci_upper': 1.53} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.49, 'ci_lower': 1.37, 'ci_upper': 1.63} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.49, 'ci_lower': 1.36, 'ci_upper': 1.62} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.37, 'ci_lower': 1.16, 'ci_upper': 1.61} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.49, 'ci_lower': 1.37, 'ci_upper': 1.63} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.49, 'ci_lower': 1.37, 'ci_upper': 1.63} | Agent Input |
| validation_sample_size | n=1,591 | n=391,491 | n=391,491 | n=133,830 | n=400,812 | n=391,491 | n=391,491 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (12%), EUR (87%), MAO (1%) / EVAL: EAS (33%), EUR (67%) | GWAS: NR (12%), EUR (87%), MAO (1%) / EVAL: EUR (100%) | GWAS: NR (12%), EUR (87%), MAO (1%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (12%), EUR (87%), MAO (1%) / EVAL: EUR (100%) | GWAS: NR (12%), EUR (87%), MAO (1%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AHS ATBC CLUEII CPSII DFCI-GCC EPIC HPFS IARC Iowa-Mayo JHH MAYO MCCS MDACCS MEC MSKCC NHS NYU-WHS PACIFIC PANDoRA PANKRAS-II PHS PLCO QIMR SELECT SMWHS Toronto UCSF VITAL WHI WHS Yale | AHS ATBC CLUEII CPSII DFCI-GCC EPIC HPFS IARC Iowa-Mayo JHH MAYO MCCS MDACCS MEC MSKCC NHS NYU-WHS PACIFIC PANDoRA PANKRAS-II PANSCAN PHS PLCO QIMR SELECT SMWHS Toronto UCSF VITAL WHI WHS Yale | AHS ATBC CLUEII CPSII DFCI-GCC EPIC HPFS IARC Iowa-Mayo JHH MAYO MCCS MDACCS MEC MSKCC NHS NYU-WHS PACIFIC PANDoRA PANKRAS-II PHS PLCO QIMR SELECT SMWHS Toronto UCSF VITAL WHI WHS Yale | N/A | AHS ATBC CLUEII CPSII DFCI-GCC EPIC HPFS IARC JHH MAYO MCCS MDACCS MEC MSKCC NHS NYU-WHS PANDoRA PANKRAS-II PHS PLCO QIMR SELECT SMWHS UCSF VITAL WHI WHS Yale | AHS ATBC CLUEII CPSII DFCI-GCC EPIC HPFS IARC Iowa-Mayo JHH MAYO MCCS MDACCS MEC MSKCC NHS NYU-WHS PACIFIC PANDoRA PANKRAS-II PANSCAN PHS PLCO QIMR SELECT SMWHS Toronto UCSF VITAL WHI WHS Yale | AHS ATBC CLUEII CPSII DFCI-GCC EPIC HPFS IARC Iowa-Mayo JHH MAYO MCCS MDACCS MEC MSKCC NHS NYU-WHS PACIFIC PANDoRA PANKRAS-II PANSCAN PHS PLCO QIMR SELECT SMWHS Toronto UCSF VITAL WHI WHS Yale | Agent Input |
| publication.title | Genetic and Circulating Biomarker Data Improve Risk Prediction for Pancreatic Cancer in the General Population. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Agent Input |
| publication.journal | Cancer Epidemiol Biomarkers Prev | Nat Commun | Nat Commun | NPJ Precis Oncol | JNCI Cancer Spectr | Nat Commun | Nat Commun | Agent Input |
| date_release | 2021-01-07 | 2021-05-28 | 2020-02-12 | 2023-12-15 | 2021-02-03 | 2021-05-28 | 2021-05-28 | Agent Input |
| variants_number | 22 | 22 | 22 | 19 | 22 | 22 | 22 | Agent Input |
| covariates | matching factors, age, cohort (also gender), race/ethnicity, smoking status, fasting status, month/year of blood collection, body mass index, waist-to-hip ratio, diabetic status | Age at assessment, sex, genotyping array, PCs(1-15), family history of cancer (prostate, breast, lung, bowel), body mass index, cigarette pack-years, smoking status (never vs. former vs. current) | Age at assessment, sex, genotyping array, PCs(1-15), family history of cancer (prostate, breast, lung, bowel), body mass index, cigarette pack-years, smoking status (never vs. former vs. current) | first 10 genetic principal components | Genotyping array | Age at assessment, sex, genotyping array, PCs(1-15), family history of cancer (prostate, breast, lung, bowel), body mass index, cigarette pack-years, smoking status (never vs. former vs. current) | Age at assessment, sex, genotyping array, PCs(1-15), family history of cancer (prostate, breast, lung, bowel), body mass index, cigarette pack-years, smoking status (never vs. former vs. current) | Agent Input |


### systemic lupus erythematosus

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000771 | PGS000772 | PGS000803 | PGS004917 | PGS000196 | PGS004917 | PGS000328 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 4/10 | 6/10 | Benchmark Only |
| AoU benchmark AUC | 0.6020 | 0.5948 | 0.5900 | 0.5790 | 0.5766 | 0.5790 | 0.5761 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Agent Input |
| trait_efo | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | Agent Input |
| phenotyping_reported | Renal disease age of onset | Renal disease | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus diagnosis in patient with arthritis | Systemic lupus erythematosus | Systemic lupus erythematosus | Agent Input |
| method_name | Genome-wide significant variants | Genome-wide significant variants | Variants significantly associated with systemic lupus erythematosus | Clumping of genome-wide significant variants | Pruning and Thresholding (P+T) | Clumping of genome-wide significant variants | Genomewide-significant variants (sourced from PMID:28509669) | Agent Input |
| performance_metrics.selected_performance_id | PPM001996 | PPM001997 | PPM002102 | PPM021383 | PPM000567 | PPM021383 | PPM000882 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European, Not reported, European, Asian unspecified, African unspecified, Not reported | European, African unspecified, Asian unspecified, NR | European, Not reported, European, Asian unspecified, African unspecified, Not reported | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 15 | 1 | 3 | 1 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5760 | N/A | N/A | 0.6960 | 0.7400 | 0.6960 | 0.7100 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.576, 'ci_lower': 0.518, 'ci_upper': 0.634} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.7, 'ci_upper': 0.78} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Odds Ratio (OR, top 20% vs bottom 20%)', 'name_short': 'Odds Ratio (OR, top 20% vs bottom 20%)', 'estimate': 1.578, 'ci_lower': 1.25, 'ci_upper': 1.991} | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio (OR; highest vs. lowest quartile)', 'name_short': 'Odds Ratio (OR; highest vs. lowest quartile)', 'estimate': 7.48, 'ci_lower': 6.73, 'ci_upper': 8.32} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.71, 'ci_lower': 1.6, 'ci_upper': 1.82} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.534, 'se': 0.034} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.01, 'ci_lower': 1.83, 'ci_upper': 2.22} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.7, 'se': 0.05} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.01, 'ci_lower': 1.83, 'ci_upper': 2.22} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.7, 'se': 0.05} | N/A | Agent Input |
| validation_sample_size | n=524 | n=3,101 | n=47,917 | n=3,945 | n=1,211 | n=3,945 | n=15,383 | Agent Input |
| samples_training | n=10,995 | n=3,076 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (2%), AMR (1%), EAS (32%), EUR (53%), MAE (9%), MAO (2%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), AMR (1%), EAS (32%), EUR (53%), MAE (9%), MAO (2%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (21%), EUR (79%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (67%), MAE (33%) | GWAS: EAS (21%), EUR (79%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | CCHMC GENYO Illumina_iControlDB UAB UCLA UCSF UMN USC WASHU WFSM | CCHMC GENYO Illumina_iControlDB UAB UCLA UCSF UMN USC WASHU WFSM | N/A | N/A | N/A | N/A | N/A | Agent Input |
| publication.title | Genome-wide assessment of genetic risk for systemic lupus erythematosus and disease severity. | Genome-wide assessment of genetic risk for systemic lupus erythematosus and disease severity. | Pleiotropy of systemic lupus erythematosus risk alleles and cardiometabolic disorders: A phenome-wide association study and inverse-variance weighted meta-analysis. | Interactions Between Genome-Wide Genetic Factors and Smoking Influencing Risk of Systemic Lupus Erythematosus. | Using genetics to prioritize diagnoses for rheumatology outpatients with inflammatory arthritis. | Interactions Between Genome-Wide Genetic Factors and Smoking Influencing Risk of Systemic Lupus Erythematosus. | High genetic risk score is associated with early disease onset, damage accrual and decreased survival in systemic lupus erythematosus. | Agent Input |
| publication.journal | Hum Mol Genet | Hum Mol Genet | Lupus | Arthritis Rheumatol | Sci Transl Med | Arthritis Rheumatol | Ann Rheum Dis | Agent Input |
| date_release | 2021-05-28 | 2021-05-28 | 2021-06-11 | 2024-06-12 | 2020-06-03 | 2024-06-12 | 2020-09-18 | Agent Input |
| variants_number | 95 | 95 | 41 | 97 | 55 | 97 | 57 | Agent Input |
| covariates | Unknown | Unknown | PCs(1-5), median age in the electronic health record, sex | Unknown | Unknown | Unknown | Unknown | Agent Input |


### ankylosing spondylitis

Candidate pool: `9` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001267 | PGS001876 | PGS001268 | PGS002089 | PGS003424 | PGS003420 | PGS001268 | Agent Input |
| AoU benchmark rank | 1/9 | 2/9 | 3/9 | 4/9 | 5/9 | 7/9 | 3/9 | Benchmark Only |
| AoU benchmark AUC | 0.7154 | 0.7144 | 0.7121 | 0.7030 | 0.6396 | 0.5596 | 0.7121 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Agent Input |
| trait_efo | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | Agent Input |
| phenotyping_reported | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Agent Input |
| method_name | snpnet | Penalized regression (bigstatsr) | snpnet | LDpred2 (bigsnpr) | LDpred2 | PRS-CS | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM008844 | PPM009896 | PPM008849 | PPM011572 | PPM017077 | PPM017073 | PPM008849 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | East Asian | East Asian | European | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 1 | 1 | 5 | Agent Input |
| performance_metrics.auc | 0.7265 | N/A | 0.7346 | N/A | N/A | N/A | 0.7346 | Agent Input |
| performance_metrics.r2 | 0.0988 | N/A | 0.1023 | N/A | N/A | N/A | 0.1023 | Agent Input |
| performance_metrics.full_model_auc | 0.7433 | N/A | 0.7488 | N/A | 0.7605 | 0.7886 | 0.7488 | Agent Input |
| performance_metrics.full_model_r2 | 0.1092 | N/A | 0.1150 | N/A | N/A | N/A | 0.1150 | Agent Input |
| performance_metrics.incremental_auc | 0.1299 | N/A | 0.1269 | N/A | N/A | N/A | 0.1269 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74328, 'ci_lower': 0.70673, 'ci_upper': 0.77983} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7605} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7886} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.10925} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12994} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.09877} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.72651, 'ci_lower': 0.68965, 'ci_upper': 0.76337} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0797, 'ci_lower': 0.0653, 'ci_upper': 0.0941} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0919, 'ci_lower': 0.0775, 'ci_upper': 0.1063} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=67,425 | n=18,262 | n=67,425 | n=18,262 | n=1,298 | n=1,298 | n=67,425 | Agent Input |
| samples_training | n=269,704 | n=391,124 | n=269,704 | n=391,124 | N/A | N/A | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | GWAS: EAS (100%) / EVAL: EAS (100%) | GWAS: EAS (100%) / EVAL: EAS (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | N/A | N/A | UKB | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Genome-wide association study reveals ethnicity-specific SNPs associated with ankylosing spondylitis in the Taiwanese population. | Genome-wide association study reveals ethnicity-specific SNPs associated with ankylosing spondylitis in the Taiwanese population. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | PLoS Genet | Am J Hum Genet | PLoS Genet | Am J Hum Genet | J Transl Med | J Transl Med | PLoS Genet | Agent Input |
| date_release | 2021-10-21 | 2022-01-10 | 2021-10-21 | 2022-01-10 | 2023-02-08 | 2023-02-08 | 2021-10-21 | Agent Input |
| variants_number | 10 | 85 | 10 | 22026 | 100 | 100 | 10 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### chronic obstructive pulmonary disease

Candidate pool: `9` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001783 | PGS004536 | PGS001788 | PGS002062 | PGS004466 | PGS001788 | PGS001788 | Agent Input |
| AoU benchmark rank | 1/9 | 2/9 | 3/9 | 4/9 | 5/9 | 3/9 | 3/9 | Benchmark Only |
| AoU benchmark AUC | 0.6057 | 0.5966 | 0.5913 | 0.5764 | 0.5652 | 0.5913 | 0.5913 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Chronic obstructive pulmonary disease | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Chronic airway obstruction | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Chronic obstructive pulmonary disease | Agent Input |
| trait_efo | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | Agent Input |
| phenotyping_reported | Chronic obstructive pulmonary disease | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Chronic airway obstruction | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Chronic obstructive pulmonary disease | Agent Input |
| method_name | PRS-CS-auto | RFDiseasemetaPRS | PRS-CS-auto | LDpred2 (bigsnpr) | LDpred2 | PRS-CS-auto | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | PPM009312 | PPM020651 | PPM009292 | PPM011358 | PPM020581 | PPM009292 | PPM009292 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 8 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | 0.0381 | N/A | 0.0163 | N/A | N/A | 0.0163 | 0.0163 | Agent Input |
| performance_metrics.full_model_auc | 0.7400 | N/A | 0.7150 | N/A | N/A | 0.7150 | 0.7150 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.715} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.715} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.715} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.038092} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.0163} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.047, 'ci_lower': 0.0327, 'ci_upper': 0.0613} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.0163} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.0163} | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.487584} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.30838779665344} | N/A | N/A | Agent Input |
| validation_sample_size | n=7,128 | n=56,192 | n=337,168 | n=18,735 | n=56,192 | n=337,168 | n=337,168 | Agent Input |
| samples_training | N/A | n=174,489 | N/A | n=391,124 | n=174,489 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (2%), ASN (2%), EAS (24%), EUR (72%), OTH (1%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (33%), EUR (61%), OTH (2%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (33%), EUR (61%), OTH (2%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (33%), EUR (61%), OTH (2%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI QSKIN TWB UCLA UKB deCODE | UKB | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI QSKIN TWB UCLA deCODE | UKB | UKB | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI QSKIN TWB UCLA deCODE | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI QSKIN TWB UCLA deCODE | Agent Input |
| publication.title | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | Cell Genom | Commun Biol | Cell Genom | Am J Hum Genet | Commun Biol | Cell Genom | Cell Genom | Agent Input |
| date_release | 2022-09-08 | 2024-03-18 | 2022-09-08 | 2022-01-10 | 2024-03-18 | 2022-09-08 | 2022-09-08 | Agent Input |
| variants_number | 884139 | 1059939 | 910082 | 811003 | 1059939 | 910082 | 910082 | Agent Input |
| covariates | sex,age, 20PCs | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | sex,age,age2,age*sex,age^2*sex, 20PCs | Agent Input |


### chronic lymphocytic leukemia

Candidate pool: `8` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000874 | PGS000648 | PGS000646 | PGS000647 | PGS003453 | PGS000874 | PGS003453 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | 1/8 | 5/8 | Benchmark Only |
| AoU benchmark AUC | 0.6073 | 0.6041 | 0.5861 | 0.5861 | 0.5818 | 0.6073 | 0.5818 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | No | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Agent Input |
| trait_efo | B-cell chronic lymphocytic leukemia | B-cell chronic lymphocytic leukemia | B-cell chronic lymphocytic leukemia | B-cell chronic lymphocytic leukemia | B-cell chronic lymphocytic leukemia | B-cell chronic lymphocytic leukemia | B-cell chronic lymphocytic leukemia | Agent Input |
| phenotyping_reported | Chronic lymphocytic leukemia | Lymphoid leukemia, chronic | Lymphoid leukemia, chronic | Lymphoid leukemia, chronic | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Agent Input |
| method_name | Representative SNPs from chronic lymphocytic leukemia susceptibility loci | Pruning and Thresholding (P+T) | GWAS Hits | GWAS Hits | Genome-wide significant SNPs | Representative SNPs from chronic lymphocytic leukemia susceptibility loci | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | PPM002493 | PPM001333 | PPM001331 | PPM001332 | PPM017224 | PPM002493 | PPM017224 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, NR | European | European | European | European | European, NR | European | Agent Input |
| performance_metrics.record_count | 17 | 1 | 1 | 1 | 4 | 17 | 4 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7900 | 0.6960 | 0.6960 | 0.6750 | N/A | 0.7900 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.1020 | 0.0973 | 0.0689 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.79, 'ci_lower': 0.78, 'ci_upper': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696, 'ci_lower': 0.621, 'ci_upper': 0.764} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696, 'ci_lower': 0.628, 'ci_upper': 0.765} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.675, 'ci_lower': 0.64, 'ci_upper': 0.707} | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.79, 'ci_lower': 0.78, 'ci_upper': 0.8} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.102} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0776} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 12.9, 'ci_lower': 4.45, 'ci_upper': 37.6} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0973} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0779} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 11.3, 'ci_lower': 3.76, 'ci_upper': 33.9} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0689} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0795} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.11, 'ci_lower': 1.97, 'ci_upper': 8.6} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.49, 'ci_lower': 2.28, 'ci_upper': 2.8} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.124, 'ci_lower': 1.648, 'ci_upper': 2.738} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.753, 'se': 0.13} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.104, 'ci_lower': 1.628, 'ci_upper': 2.718} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.744, 'se': 0.131} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.874, 'ci_lower': 1.639, 'ci_upper': 2.144} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.628, 'se': 0.0685} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.17, 'ci_lower': 2.07, 'ci_upper': 2.28} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.49, 'ci_lower': 2.28, 'ci_upper': 2.8} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.17, 'ci_lower': 2.07, 'ci_upper': 2.28} | Agent Input |
| validation_sample_size | n=3,958 | n=756 | n=756 | n=2,758 | n=20,134 | n=3,958 | n=20,134 | Agent Input |
| samples_training | N/A | n=730 | n=730 | n=2,833 | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: NR (50%), AFR (12%), EUR (25%), MAE (12%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: NR (50%), AFR (12%), EUR (25%), MAE (12%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ATBC BCCA CPSII ENGELA EPIC EpiLymph HPFS Italian_GxE MAYO MCCS MSKCC NCI-SEER NHS NSW NYU-WHS PLCO SCALE UCSF UCSF2 UK-CLL UTAH Yale | MGI | MGI | UKB | N/A | ATBC BCCA CPSII ENGELA EPIC EpiLymph HPFS Italian_GxE MAYO MCCS MSKCC NCI-SEER NHS NSW NYU-WHS PLCO SCALE UCSF UCSF2 UK-CLL UTAH Yale | N/A | Agent Input |
| publication.title | Association of polygenic risk score with the risk of chronic lymphocytic leukemia and monoclonal B-cell lymphocytosis. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Association of polygenic risk score with the risk of chronic lymphocytic leukemia and monoclonal B-cell lymphocytosis. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Agent Input |
| publication.journal | Blood | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Leukemia | Blood | Leukemia | Agent Input |
| date_release | 2021-08-26 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2023-03-24 | 2021-08-26 | 2023-03-24 | Agent Input |
| variants_number | 41 | 44 | 32 | 32 | 43 | 41 | 43 | Agent Input |
| covariates | Age, sex, study, socioeconomic status (when available) | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Unknown | Age, sex, study, socioeconomic status (when available) | Unknown | Agent Input |


### glaucoma

Candidate pool: `8` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002761 | PGS001792 | PGS000137 | PGS001323 | PGS002043 | PGS002761 | PGS001792 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | 1/8 | 2/8 | Benchmark Only |
| AoU benchmark AUC | 0.5984 | 0.5787 | 0.5747 | 0.5556 | 0.5551 | 0.5984 | 0.5787 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Glaucoma | Primary open-angle glaucoma | Glaucoma | Glaucoma (time-to-event) | Glaucoma | Glaucoma | Primary open-angle glaucoma | Agent Input |
| trait_efo | glaucoma | glaucoma | glaucoma | glaucoma | glaucoma | glaucoma | glaucoma | Agent Input |
| phenotyping_reported | Glaucoma | Primary open-angle glaucoma | Glaucoma | TTE glaucoma | Glaucoma | Glaucoma | Primary open-angle glaucoma | Agent Input |
| method_name | PRS-CS | PRS-CS-auto | Clumping and Thresholding (C+T) | snpnet | LDpred2 (bigsnpr) | PRS-CS | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | PPM014961 | PPM009296 | PPM000423 | PPM009111 | PPM011208 | PPM014961 | PPM009296 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 14 | 5 | 8 | 1 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.6199 | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | 0.0321 | N/A | 0.0220 | N/A | N/A | 0.0321 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.7770 | 0.6600 | 0.7042 | N/A | N/A | 0.7770 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0647 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | 0.0364 | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.777} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66, 'ci_lower': 0.64, 'ci_upper': 0.68} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.70422, 'ci_lower': 0.69334, 'ci_upper': 0.7151} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.777} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.03209} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.06469} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.0364} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02201} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61994, 'ci_lower': 0.60732, 'ci_upper': 0.63256} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0458, 'ci_lower': 0.0318, 'ci_upper': 0.0598} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.03209} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.68, 'ci_lower': 1.59, 'ci_upper': 1.78} | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.68, 'ci_lower': 1.59, 'ci_upper': 1.78} | N/A | Agent Input |
| validation_sample_size | n=39,444 | n=347,396 | n=3,112 | n=67,425 | n=19,592 | n=39,444 | n=347,396 | Agent Input |
| samples_training | N/A | N/A | n=8,004 | n=269,704 | n=391,124 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), EAS (25%), EUR (72%), OTH (90%) / EVAL: ASN (50%), EUR (50%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (75%), MAE (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), EAS (25%), EUR (72%), OTH (90%) / EVAL: ASN (50%), EUR (50%) | Agent Input |
| training_development_cohorts | N/A | BBJ BioMe TWB UCLA | ANZRAG | UKB | UKB | N/A | BBJ BioMe TWB UCLA | Agent Input |
| publication.title | Systematic comparison of family history and polygenic risk across 24 common diseases. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Multitrait analysis of glaucoma identifies new risk loci and enables polygenic prediction of disease susceptibility and progression. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Systematic comparison of family history and polygenic risk across 24 common diseases. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | Am J Hum Genet | Cell Genom | Nat Genet | PLoS Genet | Am J Hum Genet | Am J Hum Genet | Cell Genom | Agent Input |
| date_release | 2022-11-07 | 2022-09-08 | 2020-03-27 | 2021-10-21 | 2022-01-10 | 2022-11-07 | 2022-09-08 | Agent Input |
| variants_number | 1082518 | 911402 | 2673 | 2066 | 672952 | 1082518 | 911402 | Agent Input |
| covariates | age, sex, 10 PCs, technical covariates | sex,age,age2,age*sex,age^2*sex, 20PCs | Unknown | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, 10 PCs, technical covariates | sex,age,age2,age*sex,age^2*sex, 20PCs | Agent Input |


### knee osteoarthritis

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004883 | PGS002767 | PGS004549 | PGS004479 | PGS001192 | PGS002767 | PGS004883 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 2/7 | 1/7 | Benchmark Only |
| AoU benchmark AUC | 0.5511 | 0.5493 | 0.5482 | 0.5415 | 0.5267 | 0.5493 | 0.5511 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Knee osteoarthritis | Knee osteoarthritis | M17 (Gonarthrosis [arthrosis of knee]) | M17 (Gonarthrosis [arthrosis of knee]) | Gonarthrosis [arthrosis of knee] (time-to-event) | Knee osteoarthritis | Knee osteoarthritis | Agent Input |
| trait_efo | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | Agent Input |
| phenotyping_reported | Incident knee osteoarthritis | Knee osteoarthritis | M17 (Gonarthrosis [arthrosis of knee]) | M17 (Gonarthrosis [arthrosis of knee]) | TTE gonarthrosis [arthrosis of knee] | Knee osteoarthritis | Incident knee osteoarthritis | Agent Input |
| method_name | megaprs.auto | PRS-CS | RFDiseasemetaPRS | LDpred2 | snpnet | PRS-CS | megaprs.auto | Agent Input |
| performance_metrics.selected_performance_id | PPM021243 | PPM014967 | PPM020664 | PPM020594 | PPM008613 | PPM014967 | PPM021243 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 7 | 1 | 1 | 1 | 5 | 1 | 7 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | 0.5565 | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0068 | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5900 | N/A | N/A | N/A | 0.6450 | N/A | 0.5900 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0431 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | 0.0104 | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.59, 'ci_lower': 0.58, 'ci_upper': 0.59} | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64504, 'ci_lower': 0.63733, 'ci_upper': 0.65274} | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.59, 'ci_lower': 0.58, 'ci_upper': 0.59} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04312} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.0104} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0068} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55655, 'ci_lower': 0.54824, 'ci_upper': 0.56485} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.32, 'ci_lower': 1.31, 'ci_upper': 1.34} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.35, 'ci_lower': 1.3, 'ci_upper': 1.4} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.366693} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.32326102443575} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.35, 'ci_lower': 1.3, 'ci_upper': 1.4} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.32, 'ci_lower': 1.31, 'ci_upper': 1.34} | Agent Input |
| validation_sample_size | n=412,090 | n=39,444 | n=56,192 | n=56,192 | n=67,425 | n=39,444 | n=412,090 | Agent Input |
| samples_training | n=404 | N/A | n=174,489 | n=174,489 | n=269,704 | N/A | n=404 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | 1000G | N/A | UKB | UKB | UKB | N/A | 1000G | Agent Input |
| publication.title | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Systematic comparison of family history and polygenic risk across 24 common diseases. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | Commun Biol | Commun Biol | PLoS Genet | Am J Hum Genet | Nat Commun | Agent Input |
| date_release | 2024-06-27 | 2022-11-07 | 2024-03-18 | 2024-03-18 | 2021-10-21 | 2022-11-07 | 2024-06-27 | Agent Input |
| variants_number | 952133 | 1052275 | 1059939 | 1059939 | 4525 | 1052275 | 952133 | Agent Input |
| covariates | PCs 1-10 | age, sex, 10 PCs, technical covariates | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, 10 PCs, technical covariates | PCs 1-10 | Agent Input |


### multiple sclerosis

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002726 | PGS004699 | PGS001831 | PGS002038 | PGS000809 | PGS002726 | PGS002726 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 1/7 | 1/7 | Benchmark Only |
| AoU benchmark AUC | 0.6986 | 0.6693 | 0.6431 | 0.6419 | 0.6332 | 0.6986 | 0.6986 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Multiple sclerosis | Multiple sclerosis | Multiple sclerosis | Multiple sclerosis | Multiple sclerosis | Multiple sclerosis | Multiple sclerosis | Agent Input |
| trait_efo | multiple sclerosis | multiple sclerosis | multiple sclerosis | multiple sclerosis | multiple sclerosis | multiple sclerosis | multiple sclerosis | Agent Input |
| phenotyping_reported | Multiple sclerosis | Multiple sclerosis in individuals with undifferentiated optic neuritis | Multiple sclerosis | Multiple sclerosis | Multiple Sclerosis | Multiple sclerosis | Multiple sclerosis | Agent Input |
| method_name | Genome-wide significant variants | Genome-wide significant SNPs | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | Clumping of variants associated with multiple sclerosis | Genome-wide significant variants | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM014749 | PPM020921 | PPM009541 | PPM011171 | PPM002139 | PPM014749 | PPM014749 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European, Not reported | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 4 | 7 | 7 | 3 | 2 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7300 | N/A | N/A | N/A | 0.7650 | 0.7300 | 0.7300 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0690 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73, 'ci_lower': 0.72, 'ci_upper': 0.74} | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.765, 'se': 0.042} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73, 'ci_lower': 0.72, 'ci_upper': 0.74} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73, 'ci_lower': 0.72, 'ci_upper': 0.74} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Odds ratio (OR, top 10% vs median)', 'name_short': 'Odds ratio (OR, top 10% vs median)', 'estimate': 5.3, 'ci_lower': 4.7, 'ci_upper': 6.0} | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0367, 'ci_lower': 0.0226, 'ci_upper': 0.0508} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0396, 'ci_lower': 0.0255, 'ci_upper': 0.0536} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.069} | {'name_long': 'Odds ratio (OR, top 10% vs median)', 'name_short': 'Odds ratio (OR, top 10% vs median)', 'estimate': 5.3, 'ci_lower': 4.7, 'ci_upper': 6.0} | {'name_long': 'Odds ratio (OR, top 10% vs median)', 'name_short': 'Odds ratio (OR, top 10% vs median)', 'estimate': 5.3, 'ci_lower': 4.7, 'ci_upper': 6.0} | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.29, 'ci_lower': 1.07, 'ci_upper': 1.55} | N/A | N/A | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.63} | N/A | N/A | Agent Input |
| validation_sample_size | n=253,419 | n=545 | n=19,299 | n=19,299 | n=8,370 | n=253,419 | n=253,419 | Agent Input |
| samples_training | N/A | N/A | n=391,124 | n=391,124 | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / EVAL: NR (25%), MAE (75%) | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | IMSGC | N/A | UKB | UKB | ANZgene B58C BWH BayerScheringPharma CAHRES CHOP EGEA GAS GENMETS Gene_MSA_CH Gene_MSA_NL Gene_MSA_US HYPERGENES IMSGC IMSGC_UK IMSGC_US Illumina_iControlDB KORA MG_GWAS NBBS POPGEN PROCARDIS WTCCC | IMSGC | IMSGC | Agent Input |
| publication.title | Polygenic risk score association with multiple sclerosis susceptibility and phenotype in Europeans. | Applying a genetic risk score model to enhance prediction of future multiple sclerosis diagnosis at first presentation with optic neuritis. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Contribution of common risk variants to multiple sclerosis in Orkney and Shetland. | Polygenic risk score association with multiple sclerosis susceptibility and phenotype in Europeans. | Polygenic risk score association with multiple sclerosis susceptibility and phenotype in Europeans. | Agent Input |
| publication.journal | Brain | Nat Commun | Am J Hum Genet | Am J Hum Genet | Eur J Hum Genet | Brain | Brain | Agent Input |
| date_release | 2022-06-29 | 2024-03-18 | 2022-01-10 | 2022-01-10 | 2021-07-02 | 2022-06-29 | 2022-06-29 | Agent Input |
| variants_number | 476399 | 307 | 491 | 129077 | 127 | 476399 | 476399 | Agent Input |
| covariates | Unknown | Age, sex | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Age, sex, PCs(1-2) | Unknown | Unknown | Agent Input |


### pulmonary embolism

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001278 | PGS001280 | PGS001277 | PGS001279 | PGS004530 | PGS003861 | PGS001280 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 7/7 | 2/7 | Benchmark Only |
| AoU benchmark AUC | 0.5909 | 0.5891 | 0.5885 | 0.5865 | 0.5558 | 0.5122 | 0.5891 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | previously: Blood clot in the leg (DVT) or lung | PE (time-to-event) | PE +/- DVT | previously: Blood clot in the lung | I26 (Pulmonary embolism) | Pulmonary embolism | PE (time-to-event) | Agent Input |
| trait_efo | deep vein thrombosis, pulmonary embolism | pulmonary embolism | deep vein thrombosis, pulmonary embolism | deep vein thrombosis, pulmonary embolism | pulmonary embolism | pulmonary embolism | pulmonary embolism | Agent Input |
| phenotyping_reported | Blood clot in the leg (DVT) or lung | TTE PE | PE +/- DVT | Blood clot in the lung | I26 (Pulmonary embolism) | Pulmonary embolism | TTE PE | Agent Input |
| method_name | snpnet | snpnet | snpnet | snpnet | RFDiseasemetaPRS | PRSice-2 | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM008892 | PPM008902 | PPM008887 | PPM008897 | PPM020645 | PPM018751 | PPM008902 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | East Asian | European | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 1 | 1 | 5 | Agent Input |
| performance_metrics.auc | 0.5896 | 0.6000 | 0.5981 | 0.6003 | N/A | N/A | 0.6000 | Agent Input |
| performance_metrics.r2 | 0.0155 | 0.0136 | 0.0129 | 0.0115 | N/A | N/A | 0.0136 | Agent Input |
| performance_metrics.full_model_auc | 0.6352 | 0.6510 | 0.6466 | 0.6242 | N/A | 0.7650 | 0.6510 | Agent Input |
| performance_metrics.full_model_r2 | 0.0292 | 0.0306 | 0.0287 | 0.0176 | N/A | N/A | 0.0306 | Agent Input |
| performance_metrics.incremental_auc | 0.0384 | 0.0342 | 0.0341 | 0.0446 | N/A | N/A | 0.0342 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63525, 'ci_lower': 0.6226, 'ci_upper': 0.64791} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65102, 'ci_lower': 0.6355, 'ci_upper': 0.66654} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64659, 'ci_lower': 0.63085, 'ci_upper': 0.66233} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62416, 'ci_lower': 0.60164, 'ci_upper': 0.64668} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.765} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65102, 'ci_lower': 0.6355, 'ci_upper': 0.66654} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.02918} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03836} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01554} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.58956, 'ci_lower': 0.57602, 'ci_upper': 0.6031} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03061} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03417} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01357} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.59996, 'ci_lower': 0.58313, 'ci_upper': 0.61679} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.02867} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03414} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0129} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.59812, 'ci_lower': 0.58116, 'ci_upper': 0.61507} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01763} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04457} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60034, 'ci_lower': 0.57683, 'ci_upper': 0.62385} | N/A | {'name_long': 'Odds ratio (OR, 30-70th quantile vs <90th quantile)', 'name_short': 'Odds ratio (OR, 30-70th quantile vs <90th quantile)', 'estimate': 5.08, 'ci_lower': 4.109, 'ci_upper': 6.282} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03061} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03417} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01357} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.59996, 'ci_lower': 0.58313, 'ci_upper': 0.61679} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.242446} | N/A | N/A | Agent Input |
| validation_sample_size | n=67,349 | n=67,425 | n=67,425 | n=67,349 | n=56,192 | n=9,456 | n=67,425 | Agent Input |
| samples_training | n=269,382 | n=269,704 | n=269,704 | n=269,382 | n=174,489 | N/A | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (100%) / EVAL: EAS (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | CURES_China | UKB | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Genome-wide association analyses identified novel susceptibility loci for pulmonary embolism among Han Chinese population. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Commun Biol | BMC Med | PLoS Genet | Agent Input |
| date_release | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2024-03-18 | 2023-09-01 | 2021-10-21 | Agent Input |
| variants_number | 551 | 88 | 96 | 94 | 1059939 | 288 | 88 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### abdominal aortic aneurysm

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003972 | PGS003973 | PGS003429 | PGS001784 | PGS000753 | PGS003972 | PGS001784 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 1/6 | 4/6 | Benchmark Only |
| AoU benchmark AUC | 0.5904 | 0.5888 | 0.5837 | 0.5532 | 0.5479 | 0.5904 | 0.5532 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| trait_efo | abdominal aortic aneurysm | abdominal aortic aneurysm | abdominal aortic aneurysm | abdominal aortic aneurysm | abdominal aortic aneurysm | abdominal aortic aneurysm | abdominal aortic aneurysm | Agent Input |
| phenotyping_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Prevalent abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| method_name | PRS-CS | PRS-CS | shaPRS + LDpred2 | PRS-CS-auto | Pruning and Thresholding (P+T) | PRS-CS | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | PPM019135 | PPM019137 | PPM017103 | PPM009288 | PPM001912 | PPM019135 | PPM009288 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 3 | 1 | 1 | 1 | 7 | 3 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0147 | N/A | N/A | 0.0147 | Agent Input |
| performance_metrics.full_model_auc | 0.6600 | 0.8820 | 0.7080 | 0.8680 | N/A | 0.6600 | 0.8680 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0055 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.882, 'ci_lower': 0.872, 'ci_upper': 0.892} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.708, 'ci_lower': 0.691, 'ci_upper': 0.725} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.868} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.868} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00547} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.014661} | N/A | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.014661} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37, 'ci_lower': 1.3, 'ci_upper': 1.44} | N/A | N/A | Agent Input |
| validation_sample_size | n=7,324 | n=7,517 | n=91,731 | n=350,767 | n=46,564 | n=7,324 | n=350,767 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=8,772 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: EUR (89%), MAE (11%) / EVAL: EUR (100%) | GWAS: AFR (60%), EAS (17%), EUR (82%), OTH (90%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (25%), EUR (75%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (60%), EAS (17%), EUR (82%), OTH (90%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS UKAGS UKB VIVA deCODE eMERGE | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | UKB | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI deCODE | MAYO-VDB MVP | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS UKAGS UKB VIVA deCODE eMERGE | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI deCODE | Agent Input |
| publication.title | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Evaluating the cost-effectiveness of polygenic risk score-stratified screening for abdominal aortic aneurysm. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Genetic Architecture of Abdominal Aortic Aneurysm in the Million Veteran Program. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Commun | Cell Genom | Circulation | Nat Genet | Cell Genom | Agent Input |
| date_release | 2023-11-01 | 2023-11-01 | 2023-12-15 | 2022-09-08 | 2021-04-07 | 2023-11-01 | 2022-09-08 | Agent Input |
| variants_number | 1118997 | 1118997 | 831447 | 911440 | 29 | 1118997 | 911440 | Agent Input |
| covariates | Unknown | Age, Age^2, Sex | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | Age, sex, PCs (1-5) | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | Agent Input |


### angina pectoris

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004527 | PGS004457 | PGS000703 | PGS001261 | PGS001260 | PGS001262 | PGS001261 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 6/6 | 4/6 | Benchmark Only |
| AoU benchmark AUC | 0.5573 | 0.5409 | 0.5407 | 0.5384 | 0.5365 | 0.5305 | 0.5384 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | I20 (Angina pectoris) | I20 (Angina pectoris) | Angina | Angina pectoris (time-to-event) | Angina | Vascular/heart problems diagnosed by doctor Angina | Angina pectoris (time-to-event) | Agent Input |
| trait_efo | angina pectoris | angina pectoris | angina pectoris | angina pectoris | angina pectoris | angina pectoris | angina pectoris | Agent Input |
| phenotyping_reported | I20 (Angina pectoris) | I20 (Angina pectoris) | Angina | TTE angina pectoris | Angina | Vascular/heart problems diagnosed by doctor Angina | TTE angina pectoris | Agent Input |
| method_name | RFDiseasemetaPRS | LDpred2 | snpnet (multi-PRS) | snpnet | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM020642 | PPM020572 | PPM001595 | PPM008814 | PPM008809 | PPM008819 | PPM008814 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 5 | 5 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.5749 | 0.5744 | 0.5868 | 0.5749 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0116 | 0.0111 | 0.0130 | 0.0116 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.5926 | 0.7420 | 0.7417 | 0.8073 | 0.7420 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.1159 | 0.1146 | 0.1747 | 0.1159 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | 0.0114 | 0.0111 | 0.0098 | 0.0114 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.592624176561804} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.742, 'ci_lower': 0.73458, 'ci_upper': 0.74942} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74167, 'ci_lower': 0.73419, 'ci_upper': 0.74914} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.80729, 'ci_lower': 0.79886, 'ci_upper': 0.81571} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.742, 'ci_lower': 0.73458, 'ci_upper': 0.74942} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11586} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01139} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01162} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57494, 'ci_lower': 0.56568, 'ci_upper': 0.5842} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11464} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01108} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01112} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57435, 'ci_lower': 0.565, 'ci_upper': 0.58369} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.17468} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.0098} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01304} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.58683, 'ci_lower': 0.57429, 'ci_upper': 0.59937} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11586} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01139} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01162} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57494, 'ci_lower': 0.56568, 'ci_upper': 0.5842} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.429443} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.30967614536041} | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=56,192 | n=56,192 | n=87,413 | n=67,425 | n=67,425 | n=49,472 | n=67,425 | Agent Input |
| samples_training | n=174,489 | n=174,489 | n=223,327 | n=269,704 | n=269,704 | n=198,364 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Genetics of 35 blood and urine biomarkers in the UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Commun Biol | Commun Biol | Nat Genet | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2024-03-18 | 2024-03-18 | 2021-02-03 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 1059939 | 1059939 | 183692 | 2524 | 2562 | 1852 | 2524 | Agent Input |
| covariates | Unknown | Unknown | Age, sex, PCs(1-10) | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### cervical carcinoma

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000073 | PGS000784 | PGS005165 | PGS003389 | PGS003428 | PGS003428 | PGS003428 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 5/6 | 5/6 | Benchmark Only |
| AoU benchmark AUC | 0.6951 | 0.6706 | 0.4765 | 0.4762 | 0.3795 | 0.3795 | 0.3795 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Agent Input |
| trait_efo | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | Agent Input |
| phenotyping_reported | Incident cervical cancer | Incident cervical cancer | Cervical Cancer | cervical cancer | Incident cervical cancer | Incident cervical cancer | Incident cervical cancer | Agent Input |
| method_name | Genome-wide significant variants | 10 variants from Graff et al (PGS000073) with inverse variant weights | Known susceptibility loci (genome-wide significant SNPs) | lassosum | LDpred | LDpred | LDpred | Agent Input |
| performance_metrics.selected_performance_id | PPM002039 | PPM002055 | PPM022403 | PPM016264 | PPM017102 | PPM017102 | PPM017102 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | East Asian | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7450 | 0.7450 | 0.5660 | 0.5630 | 0.6130 | 0.6130 | 0.6130 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.4370 | N/A | 0.0016 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75, 'se': 0.017} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.017} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.566} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.563} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.613} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.613} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.613} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.437} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00158} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.09, 'ci_upper': 1.37} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.21, 'ci_lower': 1.07, 'ci_upper': 1.35} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.2, 'ci_lower': 1.06, 'ci_upper': 1.36} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.182} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.33, 'se': 0.069} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.33, 'se': 0.069} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.33, 'se': 0.069} | Agent Input |
| validation_sample_size | n=211,795 | n=211,795 | n=57,359 | n=144,374 | n=128,113 | n=128,113 | n=128,113 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=4,295 | n=4,295 | n=4,295 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (100%) / EVAL: EAS (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | TwinGene | NCI Seattle TwinGene Umea WTCCC | BBJ | N/A | EB FinnGen KP UKB | EB FinnGen KP UKB | EB FinnGen KP UKB | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Polygenic risk scores for pan-cancer risk prediction in the Chinese population: A population-based cohort study based on the China Kadoorie Biobank. | Common germline risk variants impact somatic alterations and clinical features across cancers. | GWAS meta-analyses clarify genetics of cervical phenotypes and inform risk stratification for cervical cancer. | GWAS meta-analyses clarify genetics of cervical phenotypes and inform risk stratification for cervical cancer. | GWAS meta-analyses clarify genetics of cervical phenotypes and inform risk stratification for cervical cancer. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | PLoS Med | Cancer Res | Hum Mol Genet | Hum Mol Genet | Hum Mol Genet | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2025-03-17 | 2023-01-19 | 2023-04-28 | 2023-04-28 | 2023-04-28 | Agent Input |
| variants_number | 10 | 10 | 15 | 2814 | 2894555 | 2894555 | 2894555 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Age,Sex (if applicable),Region,Top 10 genetic ancestry principal components | age, top 20 genetic principal components | age, smoking | age, smoking | age, smoking | Agent Input |


### cholelithiasis

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004546 | PGS002072 | PGS001861 | PGS001174 | PGS004476 | PGS004546 | PGS001174 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 1/6 | 4/6 | Benchmark Only |
| AoU benchmark AUC | 0.5569 | 0.5503 | 0.5478 | 0.5409 | 0.5334 | 0.5569 | 0.5409 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | K80 (Cholelithiasis) | Cholelithiasis and cholecystitis | Cholelithiasis and cholecystitis | Cholelithiasis (time-to-event) | K80 (Cholelithiasis) | K80 (Cholelithiasis) | Cholelithiasis (time-to-event) | Agent Input |
| trait_efo | cholelithiasis | Cholecystitis, cholelithiasis | Cholecystitis, cholelithiasis | cholelithiasis | cholelithiasis | cholelithiasis | cholelithiasis | Agent Input |
| phenotyping_reported | K80 (Cholelithiasis) | Cholelithiasis and cholecystitis | Cholelithiasis and cholecystitis | TTE cholelithiasis | K80 (Cholelithiasis) | K80 (Cholelithiasis) | TTE cholelithiasis | Agent Input |
| method_name | RFDiseasemetaPRS | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | snpnet | LDpred2 | RFDiseasemetaPRS | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM020661 | PPM011437 | PPM009777 | PPM008584 | PPM020591 | PPM020661 | PPM008584 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 8 | 8 | 5 | 1 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.6163 | N/A | N/A | 0.6163 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0257 | N/A | N/A | 0.0257 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.6742 | N/A | N/A | 0.6742 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0585 | N/A | N/A | 0.0585 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | 0.0405 | N/A | N/A | 0.0405 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67421, 'ci_lower': 0.66558, 'ci_upper': 0.68284} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67421, 'ci_lower': 0.66558, 'ci_upper': 0.68284} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.098, 'ci_lower': 0.0842, 'ci_upper': 0.1117} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0948, 'ci_lower': 0.081, 'ci_upper': 0.1085} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05848} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04052} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02571} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61632, 'ci_lower': 0.60704, 'ci_upper': 0.62561} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05848} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04052} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02571} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61632, 'ci_lower': 0.60704, 'ci_upper': 0.62561} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.298622} | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.219425436525} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.298622} | N/A | Agent Input |
| validation_sample_size | n=56,192 | n=19,908 | n=19,908 | n=67,425 | n=56,192 | n=56,192 | n=67,425 | Agent Input |
| samples_training | n=174,489 | n=391,124 | n=391,124 | n=269,704 | n=174,489 | n=174,489 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Commun Biol | Am J Hum Genet | Am J Hum Genet | PLoS Genet | Commun Biol | Commun Biol | PLoS Genet | Agent Input |
| date_release | 2024-03-18 | 2022-01-10 | 2022-01-10 | 2021-10-21 | 2024-03-18 | 2024-03-18 | 2021-10-21 | Agent Input |
| variants_number | 1059939 | 428587 | 2059 | 970 | 1059939 | 1059939 | 970 | Agent Input |
| covariates | Unknown | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### dilated cardiomyopathy

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004949 | PGS004951 | PGS004862 | PGS004950 | PGS004948 | PGS004949 | PGS004862 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 1/6 | 3/6 | Benchmark Only |
| AoU benchmark AUC | 0.5716 | 0.5709 | 0.5669 | 0.5645 | 0.5630 | 0.5716 | 0.5669 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy | Dilated cardiomyopathy | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy (MTAG) | Agent Input |
| trait_efo | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | Agent Input |
| phenotyping_reported | Non-ischemic dilated cardiomyopathy | Clinical dilated cardiomyopathy | Dilated cardiomyopathy | Clinical dilated cardiomyopathy | Non-ischemic dilated cardiomyopathy | Non-ischemic dilated cardiomyopathy | Dilated cardiomyopathy | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM021756 | PPM021758 | PPM021093 | PPM021757 | PPM021755 | PPM021756 | PPM021093 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, Not reported | European | European | European | European, Not reported | European, Not reported | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6800 | 0.6700 | 0.7100 | 0.6400 | 0.6400 | 0.6800 | 0.7100 | Agent Input |
| performance_metrics.full_model_r2 | 0.2160 | 0.1620 | 0.0500 | 0.1300 | 0.1860 | 0.2160 | 0.0500 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.06} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.029} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.216} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.095} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.68, 'ci_lower': 0.66, 'ci_upper': 0.69} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.0052} | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.124} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.076} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.162} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.101} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.67, 'ci_lower': 0.65, 'ci_upper': 0.69} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.2023} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05} | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.101} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.052} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.13} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.073} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.64, 'ci_lower': 0.62, 'ci_upper': 0.66} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.1765} | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.049} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.018} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.186} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.06} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.64, 'ci_lower': 0.62, 'ci_upper': 0.66} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.0042} | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.06} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.029} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.216} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.095} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.68, 'ci_lower': 0.66, 'ci_upper': 0.69} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.0052} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.91} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.65, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.93} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.66, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.71} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.54, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.64} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.49, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.91} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.65, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76} | Agent Input |
| validation_sample_size | n=326,106 | n=7,761 | n=347,585 | n=7,761 | n=326,106 | n=326,106 | n=347,585 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (91%), MAE (9%) / EVAL: MAE (100%) | GWAS: EUR (46%), MAE (54%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (46%), MAE (54%) / EVAL: EUR (100%) | GWAS: EUR (91%), MAE (9%) / EVAL: MAE (100%) | GWAS: EUR (91%), MAE (9%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AUMC_DCM FinnGen MGBB | FinnGen MGBB UKB | HERMES | FinnGen MGBB UKB | AUMC_DCM FinnGen MGBB | AUMC_DCM FinnGen MGBB | HERMES | Agent Input |
| publication.title | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association analysis provides insights into the molecular etiology of dilated cardiomyopathy. | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association analysis provides insights into the molecular etiology of dilated cardiomyopathy. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2024-12-16 | 2024-12-16 | 2024-04-18 | 2024-12-16 | 2024-12-16 | 2024-12-16 | 2024-04-18 | Agent Input |
| variants_number | 1038394 | 1075760 | 709534 | 1098677 | 1068761 | 1038394 | 709534 | Agent Input |
| covariates | Age, age^2, sex, array, PC1-12 | Sex, PC1-12 | age, age^2, sex, PC1-10 | Sex, PC1-12 | Age, age^2, sex, array, PC1-12 | Age, age^2, sex, array, PC1-12 | age, age^2, sex, PC1-10 | Agent Input |


### multiple myeloma

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002306 | PGS003450 | PGS000653 | PGS000654 | PGS000652 | PGS002281 | PGS002281 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 6/6 | 6/6 | Benchmark Only |
| AoU benchmark AUC | 0.5577 | 0.5466 | 0.5439 | 0.5414 | 0.5207 | 0.4364 | 0.4364 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Multiple myeloma | Multiple myeloma | Multiple myeloma | Multiple myeloma | Multiple myeloma | Multiple myeloma | Multiple myeloma | Agent Input |
| trait_efo | plasma cell myeloma | plasma cell myeloma | plasma cell myeloma | plasma cell myeloma | plasma cell myeloma | plasma cell myeloma | plasma cell myeloma | Agent Input |
| phenotyping_reported | Multiple myeloma | Chronic lymphocytic leukemia | Multiple myeloma | Multiple myeloma | Multiple myeloma | Multiple myeloma | Multiple myeloma | Agent Input |
| method_name | Genome-wide significant variants | Genome-wide significant SNPs | GWAS Hits | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Genome-wide significant variants | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM013035 | PPM017229 | PPM001338 | PPM001339 | PPM001337 | PPM012970 | PPM012970 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 4 | 1 | 1 | 1 | 2 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6900 | N/A | 0.5770 | 0.5760 | 0.5470 | 0.6440 | 0.6440 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0145 | 0.0137 | 0.0095 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69, 'ci_lower': 0.64, 'ci_upper': 0.7} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.577, 'ci_lower': 0.537, 'ci_upper': 0.617} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.576, 'ci_lower': 0.536, 'ci_upper': 0.616} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.547, 'ci_lower': 0.479, 'ci_upper': 0.613} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.644, 'ci_lower': 0.622, 'ci_upper': 0.666} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.644, 'ci_lower': 0.622, 'ci_upper': 0.666} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0145} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0818} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.2, 'ci_lower': 0.855, 'ci_upper': 5.66} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0137} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0818} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.2, 'ci_lower': 0.854, 'ci_upper': 5.66} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.00945} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0823} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.6, 'ci_lower': 0.593, 'ci_upper': 11.4} | {'name_long': 'Odds Ratio (OR, highest vs lowest quintiles)', 'name_short': 'Odds Ratio (OR, highest vs lowest quintiles)', 'estimate': 3.18, 'ci_lower': 2.34, 'ci_upper': 4.33} | {'name_long': 'Odds Ratio (OR, highest vs lowest quintiles)', 'name_short': 'Odds Ratio (OR, highest vs lowest quintiles)', 'estimate': 3.18, 'ci_lower': 2.34, 'ci_upper': 4.33} | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.09, 'ci_lower': 1.02, 'ci_upper': 1.16} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.327, 'ci_lower': 1.165, 'ci_upper': 1.511} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.283, 'se': 0.0663} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.316, 'ci_lower': 1.156, 'ci_upper': 1.499} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.275, 'se': 0.0662} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.24, 'ci_lower': 1.005, 'ci_upper': 1.529} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.215, 'se': 0.107} | N/A | N/A | Agent Input |
| validation_sample_size | n=290 | n=20,134 | n=2,738 | n=2,738 | n=908 | n=2,395 | n=2,395 | Agent Input |
| samples_training | N/A | N/A | n=3,377 | n=3,377 | n=1,067 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | N/A | UKB | UKB | MGI | N/A | N/A | Agent Input |
| publication.title | Evaluating polygenic risk scores in assessing risk of nine solid and hematologic cancers in European descendants. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | A polygenic risk score for multiple myeloma risk prediction. | A polygenic risk score for multiple myeloma risk prediction. | Agent Input |
| publication.journal | Int J Cancer | Leukemia | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Eur J Hum Genet | Eur J Hum Genet | Agent Input |
| date_release | 2022-06-09 | 2023-03-24 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2022-04-13 | 2022-04-13 | Agent Input |
| variants_number | 23 | 24 | 22 | 21 | 27 | 23 | 23 | Agent Input |
| covariates | Unknown | Unknown | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Age, sex, and geographic region of origin | Age, sex, and geographic region of origin | Agent Input |


### varicose veins

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002057 | PGS001845 | PGS000938 | PGS000937 | PGS004463 | PGS000937 | PGS000938 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 4/6 | 3/6 | Benchmark Only |
| AoU benchmark AUC | 0.5804 | 0.5741 | 0.5652 | 0.5613 | 0.5545 | 0.5613 | 0.5652 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 1/1 trials | 1/1 trials | Benchmark Only |
| trait_reported | Varicose veins | Varicose veins | Varicose veins of lower extremities (time-to-event) | Varicose veins | I83 (Varicose veins of lower extremities) | Varicose veins | Varicose veins of lower extremities (time-to-event) | Agent Input |
| trait_efo | Varicose veins | Varicose veins | Varicose veins | Varicose veins | Varicose veins | Varicose veins | Varicose veins | Agent Input |
| phenotyping_reported | Varicose veins | Varicose veins | TTE varicose veins of lower extremities | Varicose veins | I83 (Varicose veins of lower extremities) | Varicose veins | TTE varicose veins of lower extremities | Agent Input |
| method_name | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | snpnet | snpnet | LDpred2 | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM011318 | PPM009650 | PPM007521 | PPM007516 | PPM020578 | PPM007516 | PPM007521 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 8 | 8 | 5 | 5 | 1 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6114 | 0.6078 | N/A | 0.6078 | 0.6114 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0209 | 0.0187 | N/A | 0.0187 | 0.0209 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.6456 | 0.6352 | N/A | 0.6352 | 0.6456 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0368 | 0.0286 | N/A | 0.0286 | 0.0368 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0508 | 0.0548 | N/A | 0.0548 | 0.0508 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64564, 'ci_lower': 0.63595, 'ci_upper': 0.65534} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63516, 'ci_lower': 0.62363, 'ci_upper': 0.64669} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63516, 'ci_lower': 0.62363, 'ci_upper': 0.64669} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64564, 'ci_lower': 0.63595, 'ci_upper': 0.65534} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0824, 'ci_lower': 0.0681, 'ci_upper': 0.0967} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0701, 'ci_lower': 0.0558, 'ci_upper': 0.0844} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03681} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05082} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02091} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61143, 'ci_lower': 0.60132, 'ci_upper': 0.62154} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.02861} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05484} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01871} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60775, 'ci_lower': 0.59597, 'ci_upper': 0.61953} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.02861} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05484} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01871} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60775, 'ci_lower': 0.59597, 'ci_upper': 0.61953} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03681} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05082} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02091} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61143, 'ci_lower': 0.60132, 'ci_upper': 0.62154} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.29902422017589} | N/A | N/A | Agent Input |
| validation_sample_size | n=18,550 | n=18,550 | n=67,425 | n=67,425 | n=56,192 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=391,124 | n=269,704 | n=269,704 | n=174,489 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | PLoS Genet | PLoS Genet | Commun Biol | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2024-03-18 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 760630 | 15748 | 2563 | 2603 | 1059939 | 2603 | 2563 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |
