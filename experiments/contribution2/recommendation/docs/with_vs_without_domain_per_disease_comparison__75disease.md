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

- Catalog Search + Domain Knowledge `Hit@1`: `24/75 = 32.00%`; `trial_hits = 231/750 = 30.80%`
- Catalog Search + Domain Knowledge `Hit@2`: `42/75 = 56.00%`; `trial_hits = 407/750 = 54.27%`
- Catalog Search + Domain Knowledge `Hit@3`: `49/75 = 65.33%`; `trial_hits = 476/750 = 63.47%`
- Catalog Search + Domain Knowledge `Hit@4`: `53/75 = 70.67%`; `trial_hits = 523/750 = 69.73%`
- Catalog Search + Domain Knowledge `Hit@5`: `55/75 = 73.33%`; `trial_hits = 550/750 = 73.33%`
- Catalog Search Only `Hit@1`: `18/75 = 24.00%`; `trial_hits = 178/750 = 23.73%`
- Catalog Search Only `Hit@2`: `28/75 = 37.33%`; `trial_hits = 270/750 = 36.00%`
- Catalog Search Only `Hit@3`: `42/75 = 56.00%`; `trial_hits = 406/750 = 54.13%`
- Catalog Search Only `Hit@4`: `47/75 = 62.67%`; `trial_hits = 462/750 = 61.60%`
- Catalog Search Only `Hit@5`: `48/75 = 64.00%`; `trial_hits = 479/750 = 63.87%`
- Prompt-Only Baseline `Hit@1`: `7/75 = 9.33%`; `trial_hits = 70/750 = 9.33%`
- Prompt-Only Baseline `Hit@2`: `18/75 = 24.00%`; `trial_hits = 181/750 = 24.13%`
- Prompt-Only Baseline `Hit@3`: `26/75 = 34.67%`; `trial_hits = 261/750 = 34.80%`
- Prompt-Only Baseline `Hit@4`: `31/75 = 41.33%`; `trial_hits = 307/750 = 40.93%`
- Prompt-Only Baseline `Hit@5`: `39/75 = 52.00%`; `trial_hits = 387/750 = 51.60%`

## Percentile Hit

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.
- For each percentile threshold, define the tie-aware cutoff rank as `c_q = max(1, ceil(q/100 * M))`.
- A selection counts as `Top q% Hit` if its AoU benchmark rank satisfies `r <= c_q`.
- Denominator: fixed total disease count for modal selections and fixed total trial count for trial selections.
- Tie handling: if the AoU benchmark AUC is tied at cutoff rank `c_q`, all tied models count as `Top q%`.

- Catalog Search + Domain Knowledge `Top 5% Hit`: `33/75 = 44.00%`; `trial_hits = 308/750 = 41.07%`
- Catalog Search + Domain Knowledge `Top 10% Hit`: `35/75 = 46.67%`; `trial_hits = 337/750 = 44.93%`
- Catalog Search + Domain Knowledge `Top 15% Hit`: `43/75 = 57.33%`; `trial_hits = 411/750 = 54.80%`
- Catalog Search + Domain Knowledge `Top 20% Hit`: `45/75 = 60.00%`; `trial_hits = 430/750 = 57.33%`
- Catalog Search + Domain Knowledge `Top 25% Hit`: `45/75 = 60.00%`; `trial_hits = 442/750 = 58.93%`
- Catalog Search Only `Top 5% Hit`: `22/75 = 29.33%`; `trial_hits = 210/750 = 28.00%`
- Catalog Search Only `Top 10% Hit`: `25/75 = 33.33%`; `trial_hits = 244/750 = 32.53%`
- Catalog Search Only `Top 15% Hit`: `29/75 = 38.67%`; `trial_hits = 284/750 = 37.87%`
- Catalog Search Only `Top 20% Hit`: `31/75 = 41.33%`; `trial_hits = 307/750 = 40.93%`
- Catalog Search Only `Top 25% Hit`: `35/75 = 46.67%`; `trial_hits = 346/750 = 46.13%`
- Prompt-Only Baseline `Top 5% Hit`: `7/75 = 9.33%`; `trial_hits = 70/750 = 9.33%`
- Prompt-Only Baseline `Top 10% Hit`: `9/75 = 12.00%`; `trial_hits = 87/750 = 11.60%`
- Prompt-Only Baseline `Top 15% Hit`: `10/75 = 13.33%`; `trial_hits = 97/750 = 12.93%`
- Prompt-Only Baseline `Top 20% Hit`: `11/75 = 14.67%`; `trial_hits = 107/750 = 14.27%`
- Prompt-Only Baseline `Top 25% Hit`: `12/75 = 16.00%`; `trial_hits = 117/750 = 15.60%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean r / M = 0.4102` (75 modal selections); `trial mean r / M = 0.4141` (750 trials)
- Catalog Search Only: `mean r / M = 0.4989` (75 modal selections); `trial mean r / M = 0.5071` (750 trials)
- Prompt-Only Baseline: `mean r / M = 0.6997` (75 modal selections); `trial mean r / M = 0.7008` (749 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean (M - r) / M = 0.5898` (75 modal selections); `trial mean (M - r) / M = 0.5859` (750 trials)
- Catalog Search Only: `mean (M - r) / M = 0.5011` (75 modal selections); `trial mean (M - r) / M = 0.4929` (750 trials)
- Prompt-Only Baseline: `mean (M - r) / M = 0.3003` (75 modal selections); `trial mean (M - r) / M = 0.2992` (749 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Catalog Search + Domain Knowledge: `mean NRS = 0.7058` (75 modal selections); `trial mean NRS = 0.6978` (750 trials)
- Catalog Search Only: `mean NRS = 0.5860` (75 modal selections); `trial mean NRS = 0.5771` (750 trials)
- Prompt-Only Baseline: `mean NRS = 0.3559` (75 modal selections); `trial mean NRS = 0.3548` (749 trials)

## Per-Disease Tables

### hypertension

Candidate pool: `258` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004787 | PGS004786 | PGS004788 | PGS004785 | PGS002335 | PGS001320 | PGS001320 | PGS000014 | Agent Input |
| AoU benchmark rank | 1/258 | 2/258 | 3/258 | 4/258 | 5/258 | 12/258 | 12/258 | 98/258 | Benchmark Only |
| AoU benchmark AUC | 0.6460 | 0.6377 | 0.6377 | 0.6298 | 0.6227 | 0.6063 | 0.6063 | 0.5363 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 8/10 trials | 5/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Type 2 diabetes (T2D) | Agent Input |
| trait_efo | hypertension | hypertension | hypertension | hypertension | hypertension | hypertension | hypertension | type 2 diabetes mellitus | Agent Input |
| phenotyping_reported | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Type 2 diabetes | Agent Input |
| method_name | PRSmixPlus | PRSmix | PRSmixPlus | PRSmix | BOLT-LMM | snpnet | snpnet | LDpred | Agent Input |
| performance_metrics.selected_performance_id | PPM021012 | PPM021011 | PPM021013 | PPM021010 | PPM013198 | PPM009096 | PPM009096 | PPM000023 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | South Asian | South Asian | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 4 | 5 | 5 | 35 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | 0.6291 | 0.6291 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0649 | 0.0649 | 0.0290 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | 0.7189 | 0.7189 | 0.7300 | Agent Input |
| performance_metrics.full_model_r2 | 0.0730 | 0.0220 | 0.0270 | 0.0660 | 0.0527 | 0.1785 | 0.1785 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | 0.0442 | 0.0442 | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7189, 'ci_lower': 0.71489, 'ci_upper': 0.72291} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7189, 'ci_lower': 0.71489, 'ci_upper': 0.72291} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73, 'ci_lower': 0.72, 'ci_upper': 0.73} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.073, 'ci_lower': 0.063, 'ci_upper': 0.083} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.022, 'ci_lower': 0.016, 'ci_upper': 0.028} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.027, 'ci_lower': 0.02, 'ci_upper': 0.033} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.066, 'ci_lower': 0.056, 'ci_upper': 0.076} | {'name_long': 'Incremental R2 (full model vs. covariates alone)', 'name_short': 'Incremental R2 (full model vs. covariates alone)', 'estimate': 0.0527} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.17852} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04424} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.06493} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62908, 'ci_lower': 0.62467, 'ci_upper': 0.63349} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.17852} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04424} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.06493} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62908, 'ci_lower': 0.62467, 'ci_upper': 0.63349} | {'name_long': 'Nagelkerke’s R2 (estimate of variance explained by the PGS after covariate adjustment)', 'name_short': 'Nagelkerke’s R2 (estimate of variance explained by the PGS after covariate adjustment)', 'estimate': 0.029} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=9,462 | n=8,837 | n=8,837 | n=9,462 | n=43,392 | n=67,425 | n=67,425 | n=288,978 | Agent Input |
| samples_training | n=37,851 | n=35,350 | n=35,350 | n=37,851 | N/A | n=269,704 | n=269,704 | n=120,280 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: SAS (100%) / EVAL: SAS (100%) | DEV: SAS (100%) / EVAL: SAS (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: AFR (25%), EAS (25%), EUR (25%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: NR (5%), AFR (14%), AMR (5%), ASN (5%), EAS (14%), EUR (29%), GME (10%), MAE (5%), SAS (14%) | Agent Input |
| training_development_cohorts | AllofUs | G&H | G&H | AllofUs | UKB | UKB | UKB | DIAGRAM EPIC GERA UKB | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Leveraging fine-mapping and multipopulation training data to improve cross-population polygenic risk scores. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Genome-wide polygenic scores for common diseases identify individuals with risk equivalent to monogenic mutations. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | Cell Genom | Cell Genom | Nat Genet | PLoS Genet | PLoS Genet | Nat Genet | Agent Input |
| date_release | 2024-03-28 | 2024-03-28 | 2024-03-28 | 2024-03-28 | 2022-06-09 | 2021-10-21 | 2021-10-21 | 2019-10-14 | Agent Input |
| variants_number | 5191115 | 6622611 | 6622611 | 1170615 | 1109311 | 13791 | 13791 | 6917436 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, age*sex, assessment center, genotyping array, 10 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age; sex; Ancestry PC 1-4; genotyping chip | Agent Input |


### breast carcinoma

Candidate pool: `164` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004579 | PGS000508 | PGS004025 | PGS004053 | PGS000335 | PGS004153 | PGS000007 | PGS000001 | Agent Input |
| AoU benchmark rank | 1/163 | 2/163 | 3/163 | 4/163 | 5/163 | 6/163 | 42/163 | 88/163 | Benchmark Only |
| AoU benchmark AUC | 0.6358 | 0.6335 | 0.6332 | 0.6326 | 0.6319 | 0.6310 | 0.5995 | 0.5831 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | 7/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Breast cancer | Breast cancer (female) | Breast cancer | Breast cancer | Breast cancer | Breast cancer | Breast cancer | Breast cancer | Agent Input |
| trait_efo | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | Agent Input |
| phenotyping_reported | Breast cancer | Breast cancer [female] | Breast cancer | Breast cancer | Breast cancer | Breast cancer | Breast Cancer (personal history) | breast cancer | Agent Input |
| method_name | PRS-CS | PRS-CS | LDpred2-auto | megaprs.auto | PRS-CS | UKBB-EUR.MultiPRS.CV | LASSO penalized regression | SNPs passing genome-wide significance | Agent Input |
| performance_metrics.selected_performance_id | PPM020694 | PPM001193 | PPM019406 | PPM019418 | PPM000902 | PPM019388 | PPM000386 | PPM017270 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 6 | 6 | 13 | 6 | 10 | 19 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.6520 | 0.6598 | 0.6530 | N/A | 0.6625 | 0.7800 | 0.6280 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0548 | 0.0736 | 0.0677 | N/A | 0.0764 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.652, 'ci_lower': 0.645, 'ci_upper': 0.658} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65975886, 'ci_lower': 0.65001199, 'ci_upper': 0.66950573} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65298774, 'ci_lower': 0.64321086, 'ci_upper': 0.66276462} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66250277, 'ci_lower': 0.65279453, 'ci_upper': 0.67221102} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.628, 'ci_lower': 0.618, 'ci_upper': 0.638} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0548} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0805} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.38, 'ci_lower': 3.79, 'ci_upper': 5.07} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07358668, 'ci_lower': 0.06487413, 'ci_upper': 0.08290854} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.06765484, 'ci_lower': 0.05919841, 'ci_upper': 0.07667134} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07640178, 'ci_lower': 0.06786928, 'ci_upper': 0.08556093} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.79} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.756, 'ci_lower': 1.709, 'ci_upper': 1.804} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.563, 'se': 0.0138} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.80647225, 'ci_lower': 1.73980278, 'ci_upper': 1.87569651} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.59137591, 'ci_lower': 0.55377176, 'ci_upper': 0.62898006} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.75979222, 'ci_lower': 1.69513119, 'ci_upper': 1.82691975} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.56519574, 'ci_lower': 0.52776014, 'ci_upper': 0.60263135} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.71, 'ci_lower': 1.68, 'ci_upper': 1.75} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.82571574, 'ci_lower': 1.75833364, 'ci_upper': 1.89568002} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.60197209, 'ci_lower': 0.56436656, 'ci_upper': 0.63957762} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.38, 'ci_lower': 1.34, 'ci_upper': 1.42} | Agent Input |
| validation_sample_size | n=190,879 | n=68,531 | n=48,968 | n=48,968 | n=122,978 | n=48,968 | n=9,529 | n=200,195 | Agent Input |
| samples_training | N/A | n=68,451 | n=12,483 | n=12,483 | N/A | n=12,483 | n=10,444 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (17%), EUR (67%), MAE (17%) | GWAS: EUR (100%) / EVAL: NR (20%), EUR (80%) | Agent Input |
| training_development_cohorts | N/A | UKB | UKB | UKB | N/A | UKB | 2SISTER ABCFS ABCS ABCTB AOCS BBCC BBCS BCEES BCFR-NY BCFR-PA BCFR-UTAH BCINIS BIGGS BREOGAN BSUCH CBCS CCGP CECILE CGPS CNIO-BCS CPSII CTS DIETCOMPLYF ESTHER GC-HBOC GENICA GEPARSIXTO GESBC HCSC HEBCS HMBCS HUOCS KARBAC KBCP LMBC MABCS MARIE MBCSG MCBCS MCCS MEC MISS MMHS MSKCC MTLGEBCS NBCS NBHS NC-BCFR OBCS OFBCR ORIGO PBCS POSH PREFACE RBCS SASBAC SBCS SEARCH SKKDKFZS SMC SUCCESSB SUCCESSC SZBCS TNBCC UCIBCS UKOPS WHI pKARMA | N/A | Agent Input |
| publication.title | High-Resolution Genotyping of Formalin-Fixed Tissue Accurately Estimates Polygenic Risk Scores in Human Diseases. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | The role of polygenic risk and susceptibility genes in breast cancer over the course of life | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Polygenic Risk Scores for Prediction of Breast Cancer and Breast Cancer Subtypes. | Prediction of breast cancer risk based on profiling with common genetic variants. | Agent Input |
| publication.journal | Lab Invest | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Nat Commun | Am J Hum Genet | Am J Hum Genet | J Natl Cancer Inst | Agent Input |
| date_release | 2024-02-20 | 2020-12-15 | 2023-12-19 | 2023-12-19 | 2020-12-15 | 2023-12-19 | 2019-10-14 | 2019-10-14 | Agent Input |
| variants_number | 1088163 | 1120410 | 1041298 | 869407 | 1079089 | 1133268 | 3820 | 77 | Agent Input |
| covariates | Unknown | age, sex, batch PCs 1-4 | 0 | 0 | 10 ancestry PCs, batch, age as time scale | 0 | age, sex | Unknown | Agent Input |


### arthritis

Candidate pool: `107` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004819 | PGS004883 | PGS002767 | PGS004549 | PGS004547 | PGS001135 | PGS001135 | PGS000114 | Agent Input |
| AoU benchmark rank | 1/101 | 2/101 | 3/101 | 4/101 | 5/101 | 15/101 | 15/101 | 96/101 | Benchmark Only |
| AoU benchmark AUC | 0.5540 | 0.5455 | 0.5401 | 0.5390 | 0.5325 | 0.5151 | 0.5151 | 0.4990 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Rheumatoid Arthritis | Knee osteoarthritis | Knee osteoarthritis | M17 (Gonarthrosis [arthrosis of knee]) | M13 (Other arthritis) | Arthritis (nos) | Arthritis (nos) | Juvenile Idiopathic Arthritis | Agent Input |
| trait_efo | rheumatoid arthritis | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | arthritis | arthritis | arthritis | juvenile idiopathic arthritis | Agent Input |
| phenotyping_reported | Rheumatoid Arthritis | Incident knee osteoarthritis | Knee osteoarthritis | M17 (Gonarthrosis [arthrosis of knee]) | M13 (Other arthritis) | Arthritis (nos) | Arthritis (nos) | Juvenile Idiopathic Arthritis | Agent Input |
| method_name | PRSmixPlus | megaprs.auto | PRS-CS | RFDiseasemetaPRS | RFDiseasemetaPRS | snpnet | snpnet | SparSNP | Agent Input |
| performance_metrics.selected_performance_id | PPM021044 | PPM021240 | PPM014967 | PPM020664 | PPM020662 | PPM008405 | PPM008405 | PPM000263 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 7 | 1 | 1 | 1 | 5 | 5 | 4 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | 0.5393 | 0.5393 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0029 | 0.0029 | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.6000 | N/A | N/A | N/A | 0.6742 | 0.6742 | 0.7380 | Agent Input |
| performance_metrics.full_model_r2 | 0.0110 | N/A | N/A | N/A | N/A | 0.0547 | 0.0547 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | 0.0031 | 0.0031 | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.6, 'ci_lower': 0.58, 'ci_upper': 0.61} | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67424, 'ci_lower': 0.65969, 'ci_upper': 0.68878} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67424, 'ci_lower': 0.65969, 'ci_upper': 0.68878} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.705, 'ci_upper': 0.77} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.011, 'ci_lower': 0.007, 'ci_upper': 0.015} | N/A | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05468} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00314} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00291} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.53928, 'ci_lower': 0.52302, 'ci_upper': 0.55554} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05468} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00314} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00291} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.53928, 'ci_lower': 0.52302, 'ci_upper': 0.55554} | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.37, 'ci_lower': 1.3, 'ci_upper': 1.44} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.35, 'ci_lower': 1.3, 'ci_upper': 1.4} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.366693} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.262198} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.085, 'ci_lower': 1.773, 'ci_upper': 2.471} | Agent Input |
| validation_sample_size | n=9,462 | n=29,427 | n=39,444 | n=56,192 | n=56,192 | n=24,905 | n=24,905 | n=940 | Agent Input |
| samples_training | n=37,851 | n=404 | N/A | n=174,489 | n=174,489 | n=269,704 | n=269,704 | n=7,505 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AllofUs | 1000G | N/A | UKB | UKB | UKB | UKB | B58C UKBS WTCCC | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Agent Input |
| publication.journal | Cell Genom | Nat Commun | Am J Hum Genet | Commun Biol | Commun Biol | PLoS Genet | PLoS Genet | Ann Rheum Dis | Agent Input |
| date_release | 2024-03-28 | 2024-06-27 | 2022-11-07 | 2024-03-18 | 2024-03-18 | 2021-10-21 | 2021-10-21 | 2020-02-27 | Agent Input |
| variants_number | 2624228 | 952133 | 1052275 | 1059939 | 1059939 | 1028 | 1028 | 26 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | PCs 1-10 | age, sex, 10 PCs, technical covariates | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | sex, genetic PCs 1-10 | Agent Input |


### melanoma

Candidate pool: `103` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003382 | PGS003430 | PGS002246 | PGS002247 | PGS005208 | PGS002247 | PGS000743 | PGS000079 | Agent Input |
| AoU benchmark rank | 1/103 | 2/103 | 3/103 | 4/103 | 5/103 | 4/103 | 11/103 | 22/103 | Benchmark Only |
| AoU benchmark AUC | 0.6239 | 0.5994 | 0.5983 | 0.5967 | 0.5960 | 0.5967 | 0.5792 | 0.5664 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 8/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Skin cutaneous melanoma | Melanoma | Melanoma | Melanoma | Melanoma | Melanoma | Melanoma | Melanoma | Agent Input |
| trait_efo | cutaneous melanoma | melanoma | melanoma | melanoma | melanoma | melanoma | melanoma | melanoma | Agent Input |
| phenotyping_reported | skin cutaneous melanoma | Melanoma | Incident invasive melanoma | Incident invasive melanoma | Risk of melanoma in childhood cancer survivors | Incident invasive melanoma | Melanoma | Incident melanoma | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Maximum clumping and thresholding (maxCT) | Genome-wide significant variants | Genome-wide significant variants | Genome-wide significant SNPs | Genome-wide significant variants | Genome-wide significant variants | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM016257 | PPM017104 | PPM012822 | PPM012821 | PPM022589 | PPM012821 | PPM001828 | PPM002045 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 4 | 4 | 1 | 4 | 4 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6820 | 0.6340 | 0.6880 | 0.6910 | N/A | 0.6910 | 0.7400 | 0.6520 | Agent Input |
| performance_metrics.full_model_r2 | 0.0261 | N/A | 0.0700 | 0.0720 | N/A | 0.0720 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.682} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.634, 'ci_lower': 0.618, 'ci_upper': 0.661} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.688, 'ci_lower': 0.657, 'ci_upper': 0.718} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.691, 'ci_lower': 0.661, 'ci_upper': 0.722} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.691, 'ci_lower': 0.661, 'ci_upper': 0.722} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.71, 'ci_upper': 0.77} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.652} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.663, 'se': 0.008} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0261} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07, 'ci_lower': 0.048, 'ci_upper': 0.096} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.072, 'ci_lower': 0.051, 'ci_upper': 0.1} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.072, 'ci_lower': 0.051, 'ci_upper': 0.1} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.6, 'ci_lower': 1.31, 'ci_upper': 1.67} | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.43, 'ci_lower': 1.36, 'ci_upper': 1.49} | Agent Input |
| validation_sample_size | n=273,786 | n=109,597 | n=4,765 | n=4,765 | n=11,220 | n=4,765 | n=1,035 | n=392,803 | Agent Input |
| samples_training | N/A | n=16,434 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | GenoMEL UKB | N/A | N/A | MIA | N/A | N/A | 23andMe AMFS BATS HPFS MDACCS NHS Q-MEGA QIMR | Agent Input |
| publication.title | Common germline risk variants impact somatic alterations and clinical features across cancers. | Melanoma risk prediction based on a polygenic risk score and clinical risk factors. | Independent evaluation of melanoma polygenic risk scores in UK and Australian prospective cohorts. | Independent evaluation of melanoma polygenic risk scores in UK and Australian prospective cohorts. | Polygenic risk scores, radiation treatment exposures and subsequent cancer risk in childhood cancer survivors. | Independent evaluation of melanoma polygenic risk scores in UK and Australian prospective cohorts. | Assessing the Incremental Contribution of Common Genomic Variants to Melanoma Risk Prediction in Two Population-Based Studies. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Cancer Res | Melanoma Res | Br J Dermatol | Br J Dermatol | Nat Med | Br J Dermatol | J Invest Dermatol | Nat Commun | Agent Input |
| date_release | 2023-01-19 | 2023-10-17 | 2022-02-16 | 2022-02-16 | 2025-05-20 | 2022-02-16 | 2021-03-22 | 2020-02-12 | Agent Input |
| variants_number | 672 | 68 | 50 | 68 | 67 | 68 | 45 | 24 | Agent Input |
| covariates | age, sex, top 20 genetic principal components | Unknown | age, sex | age, sex | childhood cancer diagnosis, ancestry, age at childhood cancer diagnosis, radiation dose to the body region of the second cancer and chemotherapy exposure | age, sex | Traditional risk factors (hair colour, skin colour, eye colour, freckling as an adult, skin photosensitivity, self reported nevi, sunbed use, keratinocyte cancer personal history, first degree family history of melanoma, vacation sun exposure, blistering sunburns as a child), age, sex, recruitment city, self-reported European ancestry | Age at assessment, sex, genotyping array, PCs(1-15), frequency of UV protection use (always vs. most times vs. never out in the sun vs. never), time outdoors in summer (hours per day), ease of tanning (very easily, vs. moderate vs mild vs. mostly burn) | Agent Input |


### prostate cancer

Candidate pool: `96` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000566 | PGS000044 | PGS001292 | PGS000592 | PGS002793 | PGS004155 | PGS005238 | PGS005241 | Agent Input |
| AoU benchmark rank | 1/95 | 2/95 | 3/95 | 4/95 | 5/95 | 30/95 | 51/95 | 88/95 | Benchmark Only |
| AoU benchmark AUC | 0.6550 | 0.6295 | 0.6041 | 0.5748 | 0.5665 | 0.5492 | 0.5402 | 0.5071 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 8/10 trials | 9/10 trials | 6/10 trials | Benchmark Only |
| trait_reported | Prostate cancer | Prostate cancer | Family history of prostate cancer | Prostate cancer | Prostate cancer | Prostate cancer | Prostate carcinoma | Prostate carcinoma | Agent Input |
| trait_efo | prostate carcinoma | prostate carcinoma | family history of prostate cancer | prostate carcinoma | prostate carcinoma | prostate carcinoma | prostate carcinoma | prostate carcinoma | Agent Input |
| phenotyping_reported | Cancer of prostate | Elevated serum prostate-specific antigen (PSA) levels | Prostate cancer (FH) | Cancer of prostate | Prostate cancer risk | Prostate cancer | 5-year incident prostate cancer | 5-year incident prostate cancer | Agent Input |
| method_name | PRS-CS | Known susceptibility loci (genome-wide significant SNPs) | snpnet | lassosum | Genome-wide significant SNPs | UKBB-EUR.MultiPRS.CV | LDpred2 | SBayesRC | Agent Input |
| performance_metrics.selected_performance_id | PPM001251 | PPM000104 | PPM008960 | PPM001277 | PPM015450 | PPM019534 | PPM022696 | PPM022699 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | East Asian | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 5 | 1 | 1 | 6 | 10 | 10 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.5487 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0055 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5910 | N/A | 0.5657 | 0.6160 | N/A | 0.7049 | 0.7890 | 0.7580 | Agent Input |
| performance_metrics.full_model_r2 | 0.0245 | N/A | 0.0115 | 0.0408 | N/A | 0.1280 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0170 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.591, 'ci_lower': 0.573, 'ci_upper': 0.609} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.56572, 'ci_lower': 0.5538, 'ci_upper': 0.57764} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.616, 'ci_lower': 0.598, 'ci_upper': 0.635} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7049161, 'ci_lower': 0.70043717, 'ci_upper': 0.70939503} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.789, 'ci_lower': 0.782, 'ci_upper': 0.796} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.758, 'ci_lower': 0.751, 'ci_upper': 0.766} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0245} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.152} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.85, 'ci_lower': 1.76, 'ci_upper': 4.62} | {'name_long': 'OR (per 1-point increase in PRS)', 'name_short': 'OR (per 1-point increase in PRS)', 'estimate': 1.23, 'ci_lower': 1.1, 'ci_upper': 1.37} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01155} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01702} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00547} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.54869, 'ci_lower': 0.53677, 'ci_upper': 0.56062} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0408} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.15} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.55, 'ci_lower': 1.55, 'ci_upper': 4.2} | {'name_long': 'Odds Ratio (OR, top vs average percentile)', 'name_short': 'Odds Ratio (OR, top vs average percentile)', 'estimate': 2.87, 'ci_lower': 1.29, 'ci_upper': 6.4} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.12803272, 'ci_lower': 0.12275071, 'ci_upper': 0.13385339} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.393, 'ci_lower': 1.3, 'ci_upper': 1.493} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.332, 'se': 0.0352} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.537, 'ci_lower': 1.433, 'ci_upper': 1.648} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.43, 'se': 0.0357} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.16612832, 'ci_lower': 2.12587867, 'ci_upper': 2.20714003} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.77294139, 'ci_lower': 0.75418521, 'ci_upper': 0.79169757} | N/A | N/A | Agent Input |
| validation_sample_size | n=5,607 | n=17,012 | n=24,905 | n=5,607 | n=1,190 | n=171,474 | n=184,010 | n=184,010 | Agent Input |
| samples_training | n=5,650 | N/A | n=269,704 | n=5,650 | n=109,323 | n=9,671 | n=10,000 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (5%), EUR (95%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (2%), AMR (40%), EAS (1%), EUR (92%), MAE (3%) / DEV: AFR (3%), EAS (1%), EUR (96%) / EVAL: EAS (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: AFR (9%), AMR (3%), EAS (12%), EUR (76%) / DEV: EUR (100%) / EVAL: AFR (20%), EUR (60%), SAS (20%) | GWAS: AFR (9%), AMR (3%), EAS (12%), EUR (76%) / EVAL: AFR (20%), EUR (60%), SAS (20%) | Agent Input |
| training_development_cohorts | MGI | ICR IGD PLCO ProtecT UKGPCS deCODE | UKB | MGI | AAPC BCFR BFBOCC BRICOH CBCS CIMBA CNIO CONSIT Chicago DEMOKRITOS DKFZ EMBRACE FCCC G-FaST GC-HBOC GEMO HCSC HEBCS HEBON HUNBOCS HVH ICO ICR IGD ILUH IOVHBOCS IPOBCS MAYO MSKCC MUV NCI OCGN OSU OUH PBCS PLCO ProtecT SWE-BRCA UKB UKGPCS UPENN UPITT VFCTG deCODE kConFab | UKB | UKB | N/A | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Reducing overdiagnosis by polygenic risk-stratified screening: findings from the Finnish section of the ERSPC. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Application of European-specific polygenic risk scores for predicting prostate cancer risk in different ancestry populations. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Polygenic risk scores for prostate cancer: Comparative evaluations in UK and Australian cohorts. | Polygenic risk scores for prostate cancer: Comparative evaluations in UK and Australian cohorts. | Agent Input |
| publication.journal | Am J Hum Genet | Br J Cancer | PLoS Genet | Am J Hum Genet | Prostate | Am J Hum Genet | HGG Adv | HGG Adv | Agent Input |
| date_release | 2020-12-15 | 2019-12-18 | 2021-10-21 | 2020-12-15 | 2022-09-29 | 2023-12-19 | 2025-10-06 | 2025-10-06 | Agent Input |
| variants_number | 1111494 | 66 | 602 | 1334 | 82 | 1139693 | 964607 | 3802635 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | cancer stage, Gleason score | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | disease diagnostic age or age at recruitment, subgroups and 10 principal components | 0 | Age-specific absolute risk adjusted by PGS relative risk | Age-specific absolute risk adjusted by PGS relative risk | Agent Input |


### coronary artery disease

Candidate pool: `85` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005091 | PGS003725 | PGS004696 | PGS004745 | PGS004697 | PGS003725 | PGS003725 | PGS000010 | Agent Input |
| AoU benchmark rank | 1/85 | 2/85 | 3/85 | 4/85 | 5/85 | 2/85 | 2/85 | 75/85 | Benchmark Only |
| AoU benchmark AUC | 0.6207 | 0.6207 | 0.6160 | 0.6153 | 0.6140 | 0.6207 | 0.6207 | 0.5429 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 8/10 trials | 8/10 trials | 6/10 trials | Benchmark Only |
| trait_reported | Coronary artery disease | Coronary artery disease | Coronary heart disease | Coronary artery disease | Coronary heart disease | Coronary artery disease | Coronary artery disease | Coronary heart disease | Agent Input |
| trait_efo | coronary artery disease | coronary artery disease | coronary artery disease | coronary artery disease | coronary artery disease | coronary artery disease | coronary artery disease | coronary artery disease | Agent Input |
| phenotyping_reported | Prevalent coronary heart disease | Coronary artery disease | Incident coronary heart disease | Coronary artery disease | Incident coronary heart disease | Coronary artery disease | Coronary artery disease | Reccurent cardiovascular event (coronary heart disease death, non-fatal myocardial infraction, unstable angina pectoris, coronary artery bypass graft and Percutaneous coronary intervention) | Agent Input |
| method_name | LDPred2Auto | LDpred2 | PRS-CSx | PRSmixPlus | PRS-CSx | LDpred2 | LDpred2 | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM022179 | PPM018419 | PPM020904 | PPM020970 | PPM020903 | PPM018419 | PPM018419 | PPM012951 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African unspecified, Hispanic or Latin American, East Asian, South Asian, Not reported | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 3 | 11 | 5 | 1 | 5 | 11 | 11 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8000 | N/A | 0.7740 | N/A | 0.7730 | N/A | N/A | 0.7000 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0500 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.774} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.773} | N/A | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.7} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.143} | N/A | N/A | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.05, 'ci_lower': 0.04, 'ci_upper': 0.059} | N/A | N/A | N/A | {'name_long': 'NRI (GRS-added vs. baseline model)', 'name_short': 'NRI (GRS-added vs. baseline model)', 'estimate': 0.097} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.374, 'ci_lower': 1.343, 'ci_upper': 1.406} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.75, 'ci_lower': 1.71, 'ci_upper': 1.78} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.14, 'ci_lower': 2.1, 'ci_upper': 2.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65, 'ci_lower': 1.59, 'ci_upper': 1.71} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.55, 'ci_lower': 1.5, 'ci_upper': 1.6} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.75, 'ci_lower': 1.71, 'ci_upper': 1.78} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.14, 'ci_lower': 2.1, 'ci_upper': 2.19} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.75, 'ci_lower': 1.71, 'ci_upper': 1.78} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.14, 'ci_lower': 2.1, 'ci_upper': 2.19} | N/A | Agent Input |
| validation_sample_size | n=53,092 | n=308,264 | n=52,702 | n=7,465 | n=52,702 | n=308,264 | n=308,264 | n=4,932 | Agent Input |
| samples_training | N/A | n=116,649 | n=87,724 | n=29,863 | n=56,359 | n=116,649 | n=116,649 | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (4%), AMR (1%), EAS (13%), EUR (30%), MAE (53%) / EVAL: MAE (100%) | GWAS: MAE (100%) / DEV: EUR (100%) / EVAL: AFR (22%), AMR (11%), EAS (11%), EUR (22%), MAE (11%), SAS (22%) | GWAS: AFR (7%), AMR (3%), EAS (19%), EUR (71%) / DEV: AFR (19%), AMR (11%), EUR (64%), MAO (5%) / EVAL: AFR (20%), AMR (20%), EAS (20%), EUR (20%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (4%), AMR (2%), EAS (11%), EUR (83%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (20%), EAS (20%), EUR (20%), SAS (20%) | GWAS: MAE (100%) / DEV: EUR (100%) / EVAL: AFR (22%), AMR (11%), EAS (11%), EUR (22%), MAE (11%), SAS (22%) | GWAS: MAE (100%) / DEV: EUR (100%) / EVAL: AFR (22%), AMR (11%), EAS (11%), EUR (22%), MAE (11%), SAS (22%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ CKB FinnGen MVP | AGENT2D BBJ CARDIoGRAMplusC4D DIAMANTE FinnGen G&H GBMI GIANT GLGC MEGASTROKE MVP UKB | BBJ CARDIoGRAMplusC4D MVP UKB | AllofUs | BBJ CARDIoGRAMplusC4D MVP UKB | AGENT2D BBJ CARDIoGRAMplusC4D DIAMANTE FinnGen G&H GBMI GIANT GLGC MEGASTROKE MVP UKB | AGENT2D BBJ CARDIoGRAMplusC4D DIAMANTE FinnGen G&H GBMI GIANT GLGC MEGASTROKE MVP UKB | ADVANCE AtheroRemo CADomics CHARGE GerMIFS LURIC MIGen MedSTAR OHGS PennCATH WTCCC deCODE | Agent Input |
| publication.title | Evaluating Performance and Agreement of Coronary Heart Disease Polygenic Risk Scores. | A multi-ancestry polygenic risk score improves risk prediction for coronary artery disease. | Multi-Ancestry Polygenic Risk Score for Coronary Heart Disease Based on an Ancestrally Diverse Genome-Wide Association Study and Population-Specific Optimization. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Multi-Ancestry Polygenic Risk Score for Coronary Heart Disease Based on an Ancestrally Diverse Genome-Wide Association Study and Population-Specific Optimization. | A multi-ancestry polygenic risk score improves risk prediction for coronary artery disease. | A multi-ancestry polygenic risk score improves risk prediction for coronary artery disease. | Genetic risk, coronary heart disease events, and the clinical benefit of statin therapy: an analysis of primary and secondary prevention trials. | Agent Input |
| publication.journal | JAMA | Nat Med | Circ Genom Precis Med | Cell Genom | Circ Genom Precis Med | Nat Med | Nat Med | Lancet | Agent Input |
| date_release | 2024-11-21 | 2023-07-05 | 2024-03-18 | 2024-03-28 | 2024-03-18 | 2023-07-05 | 2023-07-05 | 2019-10-14 | Agent Input |
| variants_number | 1428772 | 1296172 | 1289980 | 4769577 | 1120251 | 1296172 | 1296172 | 27 | Agent Input |
| covariates | Age, sex, first 5 PCs | age, sex and the first ten principal components of genetic ancestry | age, sex, 10 PCs | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, 10 PCs | age, sex and the first ten principal components of genetic ancestry | age, sex and the first ten principal components of genetic ancestry | Hypertension, low-density lipoprotein cholesterol, high-density lipoprotein cholesterol, diabetes, sex, age, current smoking | Agent Input |


### asthma

Candidate pool: `66` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004725 | PGS004724 | PGS004726 | PGS004723 | PGS001782 | PGS002727 | PGS001344 | PGS000037 | Agent Input |
| AoU benchmark rank | 1/66 | 2/66 | 3/66 | 4/66 | 5/66 | 41/66 | 16/66 | 61/66 | Benchmark Only |
| AoU benchmark AUC | 0.6089 | 0.6054 | 0.6054 | 0.5997 | 0.5987 | 0.5523 | 0.5746 | 0.5234 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 8/10 trials | 5/10 trials | 9/10 trials | Benchmark Only |
| trait_reported | Asthma | Asthma | Asthma | Asthma | Asthma | Asthma | Asthma (diagnosed by doctor) | Asthma | Agent Input |
| trait_efo | asthma | asthma | asthma | asthma | asthma | asthma | asthma | asthma | Agent Input |
| phenotyping_reported | Asthma | Asthma | Asthma | Asthma | Asthma | Pediatric asthma | Asthma diagnosed by doctor | Asthma onset | Agent Input |
| method_name | PRSmixPlus | PRSmix | PRSmixPlus | PRSmix | PRS-CS-auto | PRS-CS | snpnet | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM020950 | PPM020949 | PPM020951 | PPM020948 | PPM009311 | PPM014751 | PPM009203 | PPM000084 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | South Asian | South Asian | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 5 | 5 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.6457 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0488 | N/A | 0.0597 | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | 0.6590 | 0.6600 | 0.6662 | 0.6100 | Agent Input |
| performance_metrics.full_model_r2 | 0.0390 | 0.0650 | 0.0690 | 0.0330 | N/A | 0.0400 | 0.0760 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.0798 | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.659} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66, 'ci_lower': 0.65, 'ci_upper': 0.67} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66621, 'ci_lower': 0.65552, 'ci_upper': 0.67691} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.61, 'ci_lower': 0.53, 'ci_upper': 0.7} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.039, 'ci_lower': 0.031, 'ci_upper': 0.047} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.065, 'ci_lower': 0.055, 'ci_upper': 0.075} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.069, 'ci_lower': 0.059, 'ci_upper': 0.08} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.033, 'ci_lower': 0.026, 'ci_upper': 0.04} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.048844} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07596} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.07977} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05973} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64568, 'ci_lower': 0.63475, 'ci_upper': 0.65662} | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.57, 'ci_lower': 1.55, 'ci_upper': 1.6} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.17, 'ci_lower': 1.01, 'ci_upper': 1.34} | Agent Input |
| validation_sample_size | n=9,462 | n=8,837 | n=8,837 | n=9,462 | n=7,128 | n=391,820 | n=19,857 | n=187 | Agent Input |
| samples_training | n=37,851 | n=35,350 | n=35,350 | n=37,851 | N/A | n=4,498 | n=216,121 | N/A | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: SAS (100%) / EVAL: SAS (100%) | DEV: SAS (100%) / EVAL: SAS (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (19%), EUR (76%), GME (9%), OTH (100%) / EVAL: EUR (100%) | GWAS: AFR (6%), AMR (100%), EAS (4%), EUR (90%) / DEV: MAE (100%) / EVAL: AFR (20%), AMR (20%), EAS (20%), EUR (20%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: MAE (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AllofUs | G&H | G&H | AllofUs | BBJ BioMe BioVU CCPM CKB EB FinnGen GS:SFHS HUNT MGBB MGI TWB UCLA UKB | eMERGE | UKB | ALSPAC AUGOSA B58C BAMSE BHS CAPPS ECRHS EGEA G.MAS GAIN.AST GAS KARELIA KSMU MAGICS MRCA-UKC PIAMA SAGE.AST SAPALDIA SEVERE SLSJ TOMSK UFA | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Multiancestral polygenic risk score for pediatric asthma. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Polygenic risk and the development and course of asthma: an analysis of data from a four-decade longitudinal study. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | Cell Genom | Cell Genom | Cell Genom | J Allergy Clin Immunol | PLoS Genet | Lancet Respir Med | Agent Input |
| date_release | 2024-03-28 | 2024-03-28 | 2024-03-28 | 2024-03-28 | 2022-09-08 | 2022-06-29 | 2021-10-21 | 2019-12-18 | Agent Input |
| variants_number | 3972232 | 2342250 | 2342250 | 985316 | 884043 | 985837 | 6139 | 15 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | sex,age, 20PCs | Unknown | age, sex, UKB array type, Genotype PCs | sex | Agent Input |


### dementia

Candidate pool: `65` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004287 | PGS005170 | PGS004289 | PGS004008 | PGS004283 | PGS005170 | PGS005170 | PGS000025 | Agent Input |
| AoU benchmark rank | 1/63 | 2/63 | 3/63 | 4/63 | 5/63 | 2/63 | 2/63 | 42/63 | Benchmark Only |
| AoU benchmark AUC | 0.5758 | 0.5649 | 0.5630 | 0.5626 | 0.5625 | 0.5649 | 0.5649 | 0.5146 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 8/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Alzheimer's disease | All-cause dementia | Alzheimer's disease | Alzheimer's disease | All-cause dementia | All-cause dementia | All-cause dementia | Alzheimer's disease | Agent Input |
| trait_efo | Alzheimer disease | dementia | Alzheimer disease | Alzheimer disease | dementia | dementia | dementia | Alzheimer disease | Agent Input |
| phenotyping_reported | Alzheimer's disease | Incident all-cause dementia | Alzheimer's disease | AD | All-cause dementia | Incident all-cause dementia | Incident all-cause dementia | Incident Alzheimer's disease | Agent Input |
| method_name | GenoBoost | integrative PRS of 24 component PRSs derived from LDPRED-2, C+T, PRS-CS | GenoBoost | lassosum.auto | GenoBoost | integrative PRS of 24 component PRSs derived from LDPRED-2, C+T, PRS-CS | integrative PRS of 24 component PRSs derived from LDPRED-2, C+T, PRS-CS | log-OR weighted sum of risk allele dosages | Agent Input |
| performance_metrics.selected_performance_id | PPM020355 | PPM022482 | PPM020357 | PPM019939 | PPM020351 | PPM022482 | PPM022482 | PPM000050 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 18 | 1 | 3 | 1 | 18 | 18 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8318 | 0.7610 | 0.8316 | 0.6629 | 0.8182 | 0.7610 | 0.7610 | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0418 | N/A | 0.0408 | 0.0635 | 0.0338 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.831790820495816} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.761} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.831624672285122} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66293386, 'ci_lower': 0.64863592, 'ci_upper': 0.6772318} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.81816338026915} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.761} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.761} | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Covariate-adjusted pseudo-R2', 'name_short': 'Covariate-adjusted pseudo-R2', 'estimate': 0.041820587946436} {'name_long': 'AUPRC', 'name_short': 'AUPRC', 'estimate': 0.831790820495816} | N/A | {'name_long': 'Covariate-adjusted pseudo-R2', 'name_short': 'Covariate-adjusted pseudo-R2', 'estimate': 0.040761373980392} {'name_long': 'AUPRC', 'name_short': 'AUPRC', 'estimate': 0.831624672285122} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.06348213, 'ci_lower': 0.05374272, 'ci_upper': 0.0761614} | {'name_long': 'Covariate-adjusted pseudo-R2', 'name_short': 'Covariate-adjusted pseudo-R2', 'estimate': 0.0338087996870553} {'name_long': 'AUPRC', 'name_short': 'AUPRC', 'estimate': 0.81816338026915} | N/A | N/A | {'name_long': 'ΔC-index between models with and without GRS', 'name_short': 'ΔC-index between models with and without GRS', 'estimate': 0.0043, 'ci_lower': 0.0019, 'ci_upper': 0.0067} | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.25, 'ci_lower': 1.11, 'ci_upper': 1.42} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.73288197, 'ci_lower': 1.65911417, 'ci_upper': 1.80992965} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.5497859, 'ci_lower': 0.50628383, 'ci_upper': 0.59328798} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.25, 'ci_lower': 1.11, 'ci_upper': 1.42} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.25, 'ci_lower': 1.11, 'ci_upper': 1.42} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.17, 'ci_lower': 1.13, 'ci_upper': 1.21} | Agent Input |
| validation_sample_size | n=67,428 | n=2,032 | n=67,428 | n=66,865 | n=67,428 | n=2,032 | n=2,032 | n=19,687 | Agent Input |
| samples_training | n=269,710 | n=2,039 | n=269,710 | N/A | n=269,710 | n=2,039 | n=2,039 | N/A | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (73%), MAE (27%) / DEV: EUR (100%) / EVAL: AFR (6%), AMR (6%), EAS (6%), EUR (83%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (73%), MAE (27%) / DEV: EUR (100%) / EVAL: AFR (6%), AMR (6%), EAS (6%), EUR (83%) | GWAS: EUR (73%), MAE (27%) / DEV: EUR (100%) / EVAL: AFR (6%), AMR (6%), EAS (6%), EUR (83%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | 3C ACE ADC AEGS1 AGES ALSPAC ARIC ASCOT ASPREE ASPS AugUR B58C BBJ BMES BRIGHT BioMe Bonn CADISP CARDIA CARDIOGENICS CCHS CFS CHARGE CHIP CHOP CHRIS CHS CKB COMPASS CROATIA-KORCULA CTMM Cilento CoLaus DCS DGI DIACORE DNA_Lacunar Danfund DemGene EADB EADI EB EPICPotsdam EPIC_CAD EPOZ ERF EUGENDA EXCEED EpiHealth FHS FINCAVAS FINRISK FTC FUSION FVG FamHS Fenland FinnGen GCKD GENOA GERAD GH70 GLACIER GMC GOLDN GOMAP GR@ACE GRAPHIC GRMIC GS:SFHS GeneRISK GerMIFS Glasgow GoDARTS HABC HCS HELIC HISAYAMA HNR HPFS HRS HUNT HVH HYPERGEN Health2006 Hoorn ICH INTERSTROKE InCHIANTI Inter99 JHS JoCoOA KCPS KORA LIFE-Adult LLFS LOLIPOP LURIC MANOLIS MDC MESA METASTROKE METSIM MGI MHI MIGen MVP MrOS MyCode NBS NEO NESDA NFBC66 NHS NICOLA NOMAS NSHD NTR OBB OGP ORCADES PAGES PARC PERADES PHS PMB POPGEN PREVEND PROCARDIS PROSPER QFS QIMR RACE RAINE REGARDS RISC ROSMAP RS SAHLSIS SHIP SIFAP SMART SORBS STRIP SardiNIA SiGN Steno THISEAS TRAILS TUM TwinGene TwinsUK UHU UKB UKHLS VIKING VIS Vejle WGHS WHI WHI-GARNET WHI-LLS YFS deCODE eMERGE | UKB | N/A | UKB | 3C ACE ADC AEGS1 AGES ALSPAC ARIC ASCOT ASPREE ASPS AugUR B58C BBJ BMES BRIGHT BioMe Bonn CADISP CARDIA CARDIOGENICS CCHS CFS CHARGE CHIP CHOP CHRIS CHS CKB COMPASS CROATIA-KORCULA CTMM Cilento CoLaus DCS DGI DIACORE DNA_Lacunar Danfund DemGene EADB EADI EB EPICPotsdam EPIC_CAD EPOZ ERF EUGENDA EXCEED EpiHealth FHS FINCAVAS FINRISK FTC FUSION FVG FamHS Fenland FinnGen GCKD GENOA GERAD GH70 GLACIER GMC GOLDN GOMAP GR@ACE GRAPHIC GRMIC GS:SFHS GeneRISK GerMIFS Glasgow GoDARTS HABC HCS HELIC HISAYAMA HNR HPFS HRS HUNT HVH HYPERGEN Health2006 Hoorn ICH INTERSTROKE InCHIANTI Inter99 JHS JoCoOA KCPS KORA LIFE-Adult LLFS LOLIPOP LURIC MANOLIS MDC MESA METASTROKE METSIM MGI MHI MIGen MVP MrOS MyCode NBS NEO NESDA NFBC66 NHS NICOLA NOMAS NSHD NTR OBB OGP ORCADES PAGES PARC PERADES PHS PMB POPGEN PREVEND PROCARDIS PROSPER QFS QIMR RACE RAINE REGARDS RISC ROSMAP RS SAHLSIS SHIP SIFAP SMART SORBS STRIP SardiNIA SiGN Steno THISEAS TRAILS TUM TwinGene TwinsUK UHU UKB UKHLS VIKING VIS Vejle WGHS WHI WHI-GARNET WHI-LLS YFS deCODE eMERGE | 3C ACE ADC AEGS1 AGES ALSPAC ARIC ASCOT ASPREE ASPS AugUR B58C BBJ BMES BRIGHT BioMe Bonn CADISP CARDIA CARDIOGENICS CCHS CFS CHARGE CHIP CHOP CHRIS CHS CKB COMPASS CROATIA-KORCULA CTMM Cilento CoLaus DCS DGI DIACORE DNA_Lacunar Danfund DemGene EADB EADI EB EPICPotsdam EPIC_CAD EPOZ ERF EUGENDA EXCEED EpiHealth FHS FINCAVAS FINRISK FTC FUSION FVG FamHS Fenland FinnGen GCKD GENOA GERAD GH70 GLACIER GMC GOLDN GOMAP GR@ACE GRAPHIC GRMIC GS:SFHS GeneRISK GerMIFS Glasgow GoDARTS HABC HCS HELIC HISAYAMA HNR HPFS HRS HUNT HVH HYPERGEN Health2006 Hoorn ICH INTERSTROKE InCHIANTI Inter99 JHS JoCoOA KCPS KORA LIFE-Adult LLFS LOLIPOP LURIC MANOLIS MDC MESA METASTROKE METSIM MGI MHI MIGen MVP MrOS MyCode NBS NEO NESDA NFBC66 NHS NICOLA NOMAS NSHD NTR OBB OGP ORCADES PAGES PARC PERADES PHS PMB POPGEN PREVEND PROCARDIS PROSPER QFS QIMR RACE RAINE REGARDS RISC ROSMAP RS SAHLSIS SHIP SIFAP SMART SORBS STRIP SardiNIA SiGN Steno THISEAS TRAILS TUM TwinGene TwinsUK UHU UKB UKHLS VIKING VIS Vejle WGHS WHI WHI-GARNET WHI-LLS YFS deCODE eMERGE | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | Agent Input |
| publication.title | A polygenic score method boosted by non-additive models. | Polygenic score integrating neurodegenerative and vascular risk informs dementia risk stratification. | A polygenic score method boosted by non-additive models. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | A polygenic score method boosted by non-additive models. | Polygenic score integrating neurodegenerative and vascular risk informs dementia risk stratification. | Polygenic score integrating neurodegenerative and vascular risk informs dementia risk stratification. | Evaluation of a Genetic Risk Score to Improve Risk Prediction for Alzheimer's Disease. | Agent Input |
| publication.journal | Nat Commun | Alzheimers Dement | Nat Commun | Am J Hum Genet | Nat Commun | Alzheimers Dement | Alzheimers Dement | J Alzheimers Dis | Agent Input |
| date_release | 2024-06-12 | 2025-04-17 | 2024-06-12 | 2023-12-19 | 2024-06-12 | 2025-04-17 | 2025-04-17 | 2019-10-14 | Agent Input |
| variants_number | 30 | 1320229 | 40 | 5663 | 90 | 1320229 | 1320229 | 19 | Agent Input |
| covariates | age, sex, PC1-10 | age at baseline, age^2, sex, the first 10 genetic principal components (PCs) of population stratification, and dosage of APOE ε4 and APOE ε2 alleles | age, sex, PC1-10 | 0 | age, sex, PC1-10 | age at baseline, age^2, sex, the first 10 genetic principal components (PCs) of population stratification, and dosage of APOE ε4 and APOE ε2 alleles | age at baseline, age^2, sex, the first 10 genetic principal components (PCs) of population stratification, and dosage of APOE ε4 and APOE ε2 alleles | age at baseline, sex, education level, APOE Ɛ4 status | Agent Input |


### gout

Candidate pool: `63` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004768 | PGS004160 | PGS004767 | PGS004076 | PGS004047 | PGS004160 | PGS001789 | PGS000199 | Agent Input |
| AoU benchmark rank | 1/59 | 2/59 | 3/59 | 4/59 | 5/59 | 2/59 | 15/59 | 31/59 | Benchmark Only |
| AoU benchmark AUC | 0.6693 | 0.6490 | 0.6467 | 0.6437 | 0.6433 | 0.6490 | 0.6268 | 0.5816 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Gout | Gout | Gout | Gout | Gout | Gout | Gout | Gout | Agent Input |
| trait_efo | gout | gout | gout | gout | gout | gout | gout | gout | Agent Input |
| phenotyping_reported | Gout | Gout | Gout | Gout | Gout | Gout | Gout | Gout diagnosis in patient with arthritis | Agent Input |
| method_name | PRSmixPlus | UKBB-EUR.MultiPRS.CV | PRSmix | megaprs.CV | LDpred2.CV | UKBB-EUR.MultiPRS.CV | PRS-CS-auto | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM020993 | PPM019864 | PPM020992 | PPM019879 | PPM019819 | PPM019864 | PPM009293 | PPM000582 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 6 | 1 | 6 | 6 | 6 | 3 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | 0.0312 | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.6936 | N/A | 0.6845 | 0.6851 | 0.6936 | 0.8070 | 0.8500 | Agent Input |
| performance_metrics.full_model_r2 | 0.0810 | 0.0893 | 0.0610 | 0.0788 | 0.0801 | 0.0893 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69364137, 'ci_lower': 0.68102136, 'ci_upper': 0.70626138} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.68450292, 'ci_lower': 0.67169718, 'ci_upper': 0.69730867} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.68510818, 'ci_lower': 0.67239174, 'ci_upper': 0.69782462} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69364137, 'ci_lower': 0.68102136, 'ci_upper': 0.70626138} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.807} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.85, 'ci_lower': 0.8, 'ci_upper': 0.91} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.081, 'ci_lower': 0.071, 'ci_upper': 0.092} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.08927641, 'ci_lower': 0.07728456, 'ci_upper': 0.10150747} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.061, 'ci_lower': 0.052, 'ci_upper': 0.071} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07884797, 'ci_lower': 0.06756619, 'ci_upper': 0.09040694} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.08005591, 'ci_lower': 0.0693014, 'ci_upper': 0.09177049} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.08927641, 'ci_lower': 0.07728456, 'ci_upper': 0.10150747} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.031208} | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.04859051, 'ci_lower': 1.95027604, 'ci_upper': 2.15186105} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.717152, 'ci_lower': 0.66797092, 'ci_upper': 0.76633307} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.97547041, 'ci_lower': 1.87984426, 'ci_upper': 2.07596098} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.68080655, 'ci_lower': 0.63118893, 'ci_upper': 0.73042417} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.99932119, 'ci_lower': 1.90150797, 'ci_upper': 2.1021659} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.69280772, 'ci_lower': 0.64264724, 'ci_upper': 0.74296819} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.04859051, 'ci_lower': 1.95027604, 'ci_upper': 2.15186105} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.717152, 'ci_lower': 0.66797092, 'ci_upper': 0.76633307} | N/A | N/A | Agent Input |
| validation_sample_size | n=9,462 | n=90,274 | n=9,462 | n=90,274 | n=90,274 | n=90,274 | n=359,345 | n=243 | Agent Input |
| samples_training | n=37,851 | n=6,704 | n=37,851 | n=6,704 | n=6,704 | n=6,704 | N/A | N/A | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: AFR (3%), ASN (2%), EAS (33%), EUR (60%), OTH (2%) / EVAL: AFR (33%), ASN (33%), EUR (33%) | GWAS: EUR (100%) / EVAL: EUR (67%), MAE (33%) | Agent Input |
| training_development_cohorts | AllofUs | UKB | AllofUs | UKB | UKB | UKB | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI UCLA | N/A | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Using genetics to prioritize diagnoses for rheumatology outpatients with inflammatory arthritis. | Agent Input |
| publication.journal | Cell Genom | Am J Hum Genet | Cell Genom | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Cell Genom | Sci Transl Med | Agent Input |
| date_release | 2024-03-28 | 2023-12-19 | 2024-03-28 | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2022-09-08 | 2020-06-03 | Agent Input |
| variants_number | 1580311 | 976174 | 908271 | 677631 | 865644 | 976174 | 910151 | 29 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | 0 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | 0 | 0 | 0 | sex,age,age2,age*sex,age^2*sex, 20PCs | Unknown | Agent Input |


### atrial fibrillation

Candidate pool: `61` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005313 | PGS005067 | PGS005287 | PGS005289 | PGS004706 | PGS005168 | PGS005168 | PGS000016 | Agent Input |
| AoU benchmark rank | 1/61 | 2/61 | 3/61 | 4/61 | 5/61 | 52/61 | 52/61 | 40/61 | Benchmark Only |
| AoU benchmark AUC | 0.6315 | 0.6236 | 0.6225 | 0.6211 | 0.6205 | 0.5580 | 0.5580 | 0.5796 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Atrial fibrillation | Atrial fibrillation (PheCode 427.21) | Atrial fibrillation | Atrial fibrillation | Atrial Fibrillation | Atrial fibrillation | Atrial fibrillation | Atrial fibrillation | Agent Input |
| trait_efo | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | Agent Input |
| phenotyping_reported | atrial fibrillation | Atrial fibrillation | Prevalent atrial fibrillation or flutter | Prevalent atrial fibrillation or flutter | Atrial Fibrillation | Atrial fibrillation | Atrial fibrillation | Atrial fibrillation | Agent Input |
| method_name | PRS-CSx | prscs | LDpred2 | LDpred2 | PRSmixPlus | PRS-CS | PRS-CS | LDpred | Agent Input |
| performance_metrics.selected_performance_id | PPM023035 | PPM021851 | PPM022995 | PPM022997 | PPM020931 | PPM022406 | PPM022406 | PPM000025 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African unspecified, South Asian, East Asian, Hispanic or Latin American, Other | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 3 | 1 | 1 | 1 | 45 | 45 | 13 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0.0290 | Agent Input |
| performance_metrics.full_model_auc | 0.7800 | 0.8276 | 0.7030 | 0.6813 | N/A | 0.8718 | 0.8718 | 0.7700 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.1469 | 0.1255 | 0.0440 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78, 'ci_lower': 0.778, 'ci_upper': 0.783} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.827583786719081} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.703} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6813004} | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.8718, 'ci_lower': 0.8657, 'ci_upper': 0.878} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.8718, 'ci_lower': 0.8657, 'ci_upper': 0.878} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.77, 'ci_lower': 0.76, 'ci_upper': 0.77} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.14693} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.12547} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.044, 'ci_lower': 0.036, 'ci_upper': 0.053} | N/A | N/A | {'name_long': 'Nagelkerke’s R2 (estimate of variance explained by the PGS after covariate adjustment)', 'name_short': 'Nagelkerke’s R2 (estimate of variance explained by the PGS after covariate adjustment)', 'estimate': 0.029} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.82, 'ci_lower': 1.79, 'ci_upper': 1.85} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.734, 'ci_lower': 1.66, 'ci_upper': 1.81} | N/A | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.6663} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.5106, 'se': 0.0206} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.6663} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.5106, 'se': 0.0206} | N/A | Agent Input |
| validation_sample_size | n=37,161 | n=25,409 | n=12,677 | n=7,525 | n=9,462 | n=52,757 | n=52,757 | n=288,978 | Agent Input |
| samples_training | N/A | N/A | n=2,500 | n=1,503 | n=37,851 | N/A | N/A | n=120,280 | Agent Input |
| ancestry_distribution | GWAS: AFR (5%), AMR (2%), EAS (6%), EUR (86%), SAS (2%) / EVAL: MAE (100%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (1%), AMR (1%), EAS (17%), EUR (80%), SAS (7%) / EVAL: EUR (100%) | GWAS: AFR (1%), AMR (1%), EAS (17%), EUR (80%), SAS (7%) / EVAL: EUR (100%) | GWAS: AFR (4%), AMR (2%), EAS (3%), EUR (90%) / DEV: EUR (100%) / EVAL: NR (12%), EUR (50%), MAE (25%), MAO (12%) | Agent Input |
| training_development_cohorts | AFGen BBJ FinnGen G&H HUNT MGI MVP MyCode SIMPLER UKB deCODE | MVP | MHI | MHI | AllofUs | AGES ARIC BBJ BioMe Broad CVDi CCAF CHB CHS EGCUT ENGAGE_AF-TIMI_48 FHS FinnGen GAPP GS:SFHS HRS LURIC MESA MGI MyCode Other PHB PIVUS PREVEND PROSPER RS SHIP SOLID-TIMI_52 SPHFC SiGN TwinGene ULSAM Vanderbilt WGHS WTCCC deCODE | AGES ARIC BBJ BioMe Broad CVDi CCAF CHB CHS EGCUT ENGAGE_AF-TIMI_48 FHS FinnGen GAPP GS:SFHS HRS LURIC MESA MGI MyCode Other PHB PIVUS PREVEND PROSPER RS SHIP SOLID-TIMI_52 SPHFC SiGN TwinGene ULSAM Vanderbilt WGHS WTCCC deCODE | UKB | Agent Input |
| publication.title | Cross-population GWAS and proteomics improve risk prediction and reveal mechanisms in atrial fibrillation. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Genetic analyses across cardiovascular traits: leveraging genetic correlations to empower locus discovery and prediction in common cardiovascular diseases. | Genetic analyses across cardiovascular traits: leveraging genetic correlations to empower locus discovery and prediction in common cardiovascular diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Meta-analysis of genome-wide associations and polygenic risk prediction for atrial fibrillation in more than 180,000 cases. | Meta-analysis of genome-wide associations and polygenic risk prediction for atrial fibrillation in more than 180,000 cases. | Genome-wide polygenic scores for common diseases identify individuals with risk equivalent to monogenic mutations. | Agent Input |
| publication.journal | Nat Commun | HGG Adv | NPJ Genom Med | NPJ Genom Med | Cell Genom | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2025-10-06 | 2024-10-08 | 2025-12-18 | 2025-12-18 | 2024-03-28 | 2025-03-17 | 2025-03-17 | 2019-10-14 | Agent Input |
| variants_number | 1271239 | 1273897 | 1016634 | 1016634 | 3576958 | 382963 | 382963 | 6730541 | Agent Input |
| covariates | age, sex | age, sex, 20 PCs | age, sex, four first principal components of genetic ancestry | age, sex, four first principal components of genetic ancestry | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, age^2, sex, geno_array, CHARGE-AF | age, age^2, sex, geno_array, CHARGE-AF | age; sex; Ancestry PC 1-4; genotyping chip | Agent Input |


### rheumatoid arthritis

Candidate pool: `48` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004819 | PGS004817 | PGS004163 | PGS004873 | PGS002769 | PGS004163 | PGS004163 | PGS004873 | Agent Input |
| AoU benchmark rank | 1/42 | 2/42 | 3/42 | 4/42 | 5/42 | 3/42 | 3/42 | 4/42 | Benchmark Only |
| AoU benchmark AUC | 0.6006 | 0.5889 | 0.5850 | 0.5824 | 0.5780 | 0.5850 | 0.5850 | 0.5824 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 6/10 trials | Benchmark Only |
| trait_reported | Rheumatoid Arthritis | Rheumatoid Arthritis | Rheumatoid arthritis | Rheumatoid arthritis | Seropositive rheumatoid arthritis | Rheumatoid arthritis | Rheumatoid arthritis | Rheumatoid arthritis | Agent Input |
| trait_efo | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | Agent Input |
| phenotyping_reported | Rheumatoid Arthritis | Rheumatoid Arthritis | Seropositive RA | Incident RA | Seropositive rheumatoid arthritis | Seropositive RA | Seropositive RA | Incident RA | Agent Input |
| method_name | PRSmixPlus | PRSmix | UKBB-EUR.MultiPRS.CV | megaprs.auto | PRS-CS | UKBB-EUR.MultiPRS.CV | UKBB-EUR.MultiPRS.CV | megaprs.auto | Agent Input |
| performance_metrics.selected_performance_id | PPM021044 | PPM021042 | PPM020029 | PPM021170 | PPM014969 | PPM020029 | PPM020029 | PPM021170 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 5 | 8 | 1 | 5 | 5 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.7469 | 0.8500 | N/A | 0.7469 | 0.7469 | 0.8500 | Agent Input |
| performance_metrics.full_model_r2 | 0.0110 | 0.0080 | 0.1376 | N/A | N/A | 0.1376 | 0.1376 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74694739, 'ci_lower': 0.71319269, 'ci_upper': 0.78070209} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.85, 'ci_lower': 0.77, 'ci_upper': 0.92} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74694739, 'ci_lower': 0.71319269, 'ci_upper': 0.78070209} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74694739, 'ci_lower': 0.71319269, 'ci_upper': 0.78070209} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.85, 'ci_lower': 0.77, 'ci_upper': 0.92} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.011, 'ci_lower': 0.007, 'ci_upper': 0.015} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.008, 'ci_lower': 0.004, 'ci_upper': 0.012} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1375903, 'ci_lower': 0.09865689, 'ci_upper': 0.18374268} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1375903, 'ci_lower': 0.09865689, 'ci_upper': 0.18374268} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1375903, 'ci_lower': 0.09865689, 'ci_upper': 0.18374268} | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.46183351, 'ci_lower': 2.16199209, 'ci_upper': 2.8032592} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.9009064, 'ci_lower': 0.77103006, 'ci_upper': 1.03078274} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.83, 'ci_lower': 1.14, 'ci_upper': 2.93} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.72, 'ci_lower': 1.61, 'ci_upper': 1.83} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.46183351, 'ci_lower': 2.16199209, 'ci_upper': 2.8032592} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.9009064, 'ci_lower': 0.77103006, 'ci_upper': 1.03078274} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.46183351, 'ci_lower': 2.16199209, 'ci_upper': 2.8032592} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.9009064, 'ci_lower': 0.77103006, 'ci_upper': 1.03078274} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.83, 'ci_lower': 1.14, 'ci_upper': 2.93} | Agent Input |
| validation_sample_size | n=9,462 | n=9,462 | n=90,274 | n=7,018 | n=39,444 | n=90,274 | n=90,274 | n=7,018 | Agent Input |
| samples_training | n=37,851 | n=37,851 | n=820 | n=404 | N/A | n=820 | n=820 | n=404 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (80%), SAS (20%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (28%), EUR (72%) / EVAL: EUR (100%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (80%), SAS (20%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (80%), SAS (20%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AllofUs | AllofUs | UKB | 1000G | N/A | UKB | UKB | 1000G | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | Am J Hum Genet | Nat Commun | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Nat Commun | Agent Input |
| date_release | 2024-03-28 | 2024-03-28 | 2023-12-19 | 2024-06-27 | 2022-11-07 | 2023-12-19 | 2023-12-19 | 2024-06-27 | Agent Input |
| variants_number | 2624228 | 786048 | 778275 | 551074 | 1083565 | 778275 | 778275 | 551074 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | 0 | PCs 1-10 | age, sex, 10 PCs, technical covariates | 0 | 0 | PCs 1-10 | Agent Input |


### ovarian neoplasm

Candidate pool: `42` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000793 | PGS000082 | PGS003741 | PGS004249 | PGS000158 | PGS000547 | PGS000549 | PGS000048 | Agent Input |
| AoU benchmark rank | 1/42 | 2/42 | 3/42 | 4/42 | 5/42 | 31/42 | 18/42 | 14/42 | Benchmark Only |
| AoU benchmark AUC | 0.6536 | 0.6420 | 0.6364 | 0.6334 | 0.6315 | 0.5482 | 0.6055 | 0.6151 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | 5/10 trials | 9/10 trials | Benchmark Only |
| trait_reported | Ovarian cancer | Ovarian cancer | Ovarian cancer | Ovarian cancer | Ovarian cancer | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Ovarian cancer | Agent Input |
| trait_efo | ovarian carcinoma | ovarian carcinoma | ovarian carcinoma | ovarian carcinoma | ovarian carcinoma | ovarian neoplasm | ovarian neoplasm | ovarian carcinoma | Agent Input |
| phenotyping_reported | Incident ovarian cancer | Incident ovarian cancer | Ovarian cancer | Ovarian cancer | Ovarian cancer | Malignant neoplasm of ovary | Malignant neoplasm of ovary | Ovarian cancer in BRCA2 mutation carriers | Agent Input |
| method_name | 36 variants from Graff et al (PGS000082) with inverse variant weights | Genome-wide significant variants | Genome-wide significant SNPs | PRSice-2 | Pruning and Thresholding (P+T) | GWAS Hits | GWAS Hits | Known susceptibility loci (genome-wide significant SNPs) | Agent Input |
| performance_metrics.selected_performance_id | PPM002064 | PPM002048 | PPM018497 | PPM020306 | PPM000478 | PPM001232 | PPM001234 | PPM000113 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 3 | 1 | 1 | 2 | 1 | 1 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6600 | 0.6560 | N/A | N/A | N/A | 0.5440 | 0.5670 | 0.6280 | Agent Input |
| performance_metrics.full_model_r2 | 0.1930 | N/A | N/A | N/A | N/A | 0.0038 | 0.0100 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.654, 'se': 0.015} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.656} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.655, 'se': 0.015} | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.544, 'ci_lower': 0.517, 'ci_upper': 0.573} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.567, 'ci_lower': 0.539, 'ci_upper': 0.595} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.628, 'ci_lower': 0.592, 'ci_upper': 0.665} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.193} | N/A | N/A | N/A | {'name_long': 'Mean realative risk', 'name_short': 'Mean realative risk', 'estimate': 1.12, 'ci_lower': 1.08, 'ci_upper': 1.16} {'name_long': 'Wilcoxon test (case vs. control) p-value', 'name_short': 'Wilcoxon test (case vs. control) p-value', 'estimate': 0.000145} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.00379} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0826} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 0.922, 'ci_lower': 0.347, 'ci_upper': 2.45} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.00996} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0824} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.76, 'ci_lower': 0.839, 'ci_upper': 3.69} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.2, 'ci_lower': 1.1, 'ci_upper': 1.32} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.13, 'ci_lower': 1.04, 'ci_upper': 1.24} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.15, 'ci_lower': 1.04, 'ci_upper': 1.28} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.03, 'ci_upper': 1.31} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.156, 'ci_lower': 1.051, 'ci_upper': 1.27} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.145, 'se': 0.0482} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.263, 'ci_lower': 1.15, 'ci_upper': 1.387} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.234, 'se': 0.0479} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.49, 'ci_lower': 1.34, 'ci_upper': 1.65} | Agent Input |
| validation_sample_size | n=211,958 | n=211,958 | n=501 | n=133,830 | n=7,551 | n=5,196 | n=5,196 | n=8,211 | Agent Input |
| samples_training | N/A | N/A | n=437 | N/A | N/A | n=5,130 | n=5,130 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AOCS B58C BCFR-AU BCFR-NY BCFR-PA BCFR-UTAH BFBOCC BMBSA BOCC BOCS BRICOH BioVU CIMBA CNIO COH CONSIT_TEAM CoRGI CopBCS DEMOKRITOS DFCI DKFZ DOVE DPMS EMBRACE EPIC FCCC FOTS FROC&GEOCS G-FaST GC-HBOC GEMO GOCS Georgetown HCSC HEBCS HEBON HJOCS HMOCS HOCS HOPE HUNBOCS HUOCS HUVH HeOCS ICO ICR IHCC INHERIT IOVHBOCS IPOBCS KUMC LAC-CCOC LUHR MALOVA MAYO MCGILL MDACCS MEC MOCS MOF MSKCC MUV NBS NC-BCFR NCI NCOCS NECC NHS NJOCS NNPIO NOCS NRG_ONCOLOGY NSUHS Nijmegen OCGN ODZH OFBCR OSUCCG OUH OVAL-BC PLCO POCS RMH RMH-OCS SEARCH SEARCH-OCS SHMC SWE SWE-BRCA Sisters TAMPERE TBOCS UBNS UC UCIOCS UCSF UDP UKCRC UKFOCR UKGRFOCR UKOPS UPENN UPITT VFCTG WCPSOCCI WCRI WOCS deCODE kConFab | AOCS B58C BCFR-AU BCFR-NY BCFR-PA BCFR-UTAH BFBOCC BMBSA BOCC BOCS BRICOH BioVU CNIO COH CONSIT_TEAM CoRGI CopBCS DEMOKRITOS DFCI DKFZ DOVE DPMS EMBRACE EPIC FCCC FOTS FROC&GEOCS G-FaST GC-HBOC GEMO GOCS Georgetown HCSC HEBCS HEBON HJOCS HMOCS HOCS HOPE HUNBOCS HUOCS HUVH HeOCS ICO ICR IHCC INHERIT IOVHBOCS IPOBCS KUMC LAC-CCOC LUHR MALOVA MAYO MCGILL MDACCS MEC MOCS MOF MSKCC MUV NBS NC-BCFR NCI NCOCS NECC NHS NJOCS NNPIO NOCS NRG_ONCOLOGY NSUHS Nijmegen OCGN ODZH OFBCR OSUCCG OUH OVAL-BC PLCO POCS RMH RMH-OCS SEARCH SEARCH-OCS SHMC SWE SWE-BRCA Sisters TAMPERE TBOCS UBNS UC UCIOCS UCSF UDP UKCRC UKFOCR UKGRFOCR UKOPS UPENN UPITT VFCTG WCPSOCCI WCRI WOCS deCODE kConFab | UKB | N/A | B58C CoRGI RMH-OCS SEARCH-OCS UKFOCR UKOPS | UKB | UKB | N/A | Agent Input |
| publication.title | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Prognostic evaluation of polygenic risk score underlying pan-cancer analysis: evidence from two large-scale cohorts. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Systematic evaluation of cancer-specific genetic risk score for 11 types of cancer in The Cancer Genome Atlas and Electronic Medical Records and Genomics cohorts. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Evaluation of Polygenic Risk Scores for Breast and Ovarian Cancer Risk Prediction in BRCA1 and BRCA2 Mutation Carriers. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | EBioMedicine | NPJ Precis Oncol | Cancer Med | Am J Hum Genet | Am J Hum Genet | J Natl Cancer Inst | Agent Input |
| date_release | 2021-05-28 | 2020-02-12 | 2023-06-01 | 2023-12-15 | 2020-04-29 | 2020-12-15 | 2020-12-15 | 2019-12-18 | Agent Input |
| variants_number | 36 | 36 | 28 | 25 | 11 | 6 | 16 | 17 | Agent Input |
| covariates | Age at assessment, family history of breast cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), BMI*menopausal status | Age at assessment, family history of breast cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), BMI*menopausal status | Unknown | first 10 genetic principal components | Unknown | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Country, birth year | Agent Input |


### lung cancer

Candidate pool: `35` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004860 | PGS002270 | PGS000721 | PGS004325 | PGS004884 | PGS000078 | PGS004860 | PGS000070 | Agent Input |
| AoU benchmark rank | 1/35 | 2/35 | 3/35 | 4/35 | 5/35 | 18/35 | 1/35 | 30/35 | Benchmark Only |
| AoU benchmark AUC | 0.5709 | 0.5654 | 0.5595 | 0.5595 | 0.5583 | 0.5432 | 0.5709 | 0.5285 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Agent Input |
| trait_efo | lung carcinoma | lung carcinoma | lung carcinoma | lung carcinoma | lung carcinoma | lung carcinoma | lung carcinoma | lung adenocarcinoma | Agent Input |
| phenotyping_reported | Incident lung cancer | Lung cancer | Lung cancer | Lung carcinogenesis (in smokers) | Incident lung cancer | Incident lung cancer | Incident lung cancer | Lung cancer | Agent Input |
| method_name | LDpred2 | Genome-wide significant variants | Genome-wide significant variants | Genome-wide significant SNPs | megaprs.auto | Genome-wide significant variants | LDpred2 | Genomewide-significant SNPs, filtered to be specific to Chinese ancestry individuals | Agent Input |
| performance_metrics.selected_performance_id | PPM021091 | PPM020290 | PPM020286 | PPM020438 | PPM021250 | PPM002044 | PPM021091 | PPM020283 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 4 | 2 | 7 | 4 | 1 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8930 | 0.7250 | 0.7380 | N/A | 0.6200 | 0.8460 | 0.8930 | 0.7260 | Agent Input |
| performance_metrics.full_model_r2 | 0.4900 | N/A | N/A | N/A | N/A | N/A | 0.4900 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.893, 'ci_lower': 0.887, 'ci_upper': 0.898} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.725, 'ci_lower': 0.697, 'ci_upper': 0.754} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.71, 'ci_upper': 0.766} | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.62, 'ci_lower': 0.61, 'ci_upper': 0.63} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.846} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.849, 'se': 0.006} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.893, 'ci_lower': 0.887, 'ci_upper': 0.898} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.726, 'ci_lower': 0.698, 'ci_upper': 0.754} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.49} | N/A | N/A | {'name_long': 'Hazard ratio (HR, highest PRS quintile and heavy smokers vs lowest PRS quintile and never smokers)', 'name_short': 'Hazard ratio (HR, highest PRS quintile and heavy smokers vs lowest PRS quintile and never smokers)', 'estimate': 4.63, 'ci_lower': 3.0, 'ci_upper': 7.13} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.49} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | N/A | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.24, 'ci_lower': 1.2, 'ci_upper': 1.28} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.11, 'ci_upper': 1.22} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | N/A | Agent Input |
| validation_sample_size | n=24,012 | n=1,202 | n=1,202 | n=308,490 | n=277,400 | n=392,539 | n=24,012 | n=1,202 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=404 | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (20%), EUR (80%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EAS (33%), EUR (67%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (27%), EUR (73%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (49%), EUR (51%) / EVAL: EAS (86%), EUR (14%) | Agent Input |
| training_development_cohorts | N/A | BBJ GAME-ON GELCAPS GLC IARC ICR ILCCO MDACC MRC NCI SLRI TRICL | ATBC B58C CARET EAGLE GAME-ON GECCO GELCAPS GLC HGF HUNT2 Harvard IARC ICR-GWAS LLP MDACCS NCI PLCO SLRI Tromso UKBS WTCCC deCODE | N/A | 1000G | ATBC B58C CARET EAGLE GELCAPS HGF HUNT2 Harvard IARC ICR-GWAS LLP MDACCS PLCO SLRI Tromso UKBS WTCCC deCODE | N/A | N/A | Agent Input |
| publication.title | Polygenic inheritance and its interplay with smoking history in predicting lung cancer diagnosis: a French-Canadian case-control cohort. | Association of smoking and polygenic risk with the incidence of lung cancer: a prospective cohort study. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Association of oxidative stress, programmed cell death, GSTM1 gene polymorphisms, smoking and the risk of lung carcinogenesis: A two-step Mendelian randomization study. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Polygenic inheritance and its interplay with smoking history in predicting lung cancer diagnosis: a French-Canadian case-control cohort. | Identification of risk loci and a polygenic risk score for lung cancer: a large-scale prospective cohort study in Chinese populations. | Agent Input |
| publication.journal | EBioMedicine | Br J Cancer | JNCI Cancer Spectr | Front Physiol | Nat Commun | Nat Commun | EBioMedicine | Lancet Respir Med | Agent Input |
| date_release | 2024-07-31 | 2022-04-01 | 2021-02-03 | 2024-01-11 | 2024-06-27 | 2020-02-12 | 2024-07-31 | 2020-02-12 | Agent Input |
| variants_number | 1143554 | 33 | 19 | 19 | 655479 | 109 | 1143554 | 19 | Agent Input |
| covariates | Sex, age,BMI, smocking status(ever or never smoker), and the first 10 ancestry-based PCA | Age, sex, current smoking status, BMI, forced expiratory volume in 1 second/forced vital capacity ratio | Age, sex, current smoking status, BMI, forced expiratory volume in 1 second/forced vital capacity ratio | Education, sex, genotype array, and the first ten important components | PCs 1-10 | Age at assessment, sex, genotyping array, PCs(1-15), family history of lung cancer, PM2.5 in 2010, cigarettes per day, years of smoking, smoking status (never vs. former vs. current), smoking status*cigarettes per day, smoking stutus*years of smoking | Sex, age,BMI, smocking status(ever or never smoker), and the first 10 ancestry-based PCA | Age, sex, current smoking status, BMI, forced expiratory volume in 1 second/forced vital capacity ratio | Agent Input |


### myocardial infarction

Candidate pool: `35` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005045 | PGS005039 | PGS005044 | PGS005041 | PGS005046 | PGS005039 | PGS001314 | PGS000117 | Agent Input |
| AoU benchmark rank | 1/35 | 2/35 | 3/35 | 4/35 | 5/35 | 2/35 | 21/35 | 35/35 | Benchmark Only |
| AoU benchmark AUC | 0.6044 | 0.6020 | 0.6019 | 0.6013 | 0.6010 | 0.6020 | 0.5447 | 0.4306 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 7/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Myocardial infarction (PheCode 411.2) | Myocardial infarction (PheCode 411.2) | Myocardial infarction (PheCode 411.2) | Myocardial infarction (PheCode 411.2) | Myocardial infarction (PheCode 411.2) | Myocardial infarction (PheCode 411.2) | Acute myocardial infarction (time-to-event) | Cardiovascular disease | Agent Input |
| trait_efo | myocardial infarction | myocardial infarction | myocardial infarction | myocardial infarction | myocardial infarction | myocardial infarction | myocardial infarction | cardiovascular disease | Agent Input |
| phenotyping_reported | Myocardial infarction | Myocardial infarction | Myocardial infarction | Myocardial infarction | Myocardial infarction | Myocardial infarction | TTE acute myocardial infarction | Incident cardiovascular disease (over age 55) | Agent Input |
| method_name | prscs | ldpred | prscs | prscs | prscsx | ldpred | snpnet | lassosum | Agent Input |
| performance_metrics.selected_performance_id | PPM021806 | PPM021907 | PPM021805 | PPM021809 | PPM021810 | PPM021907 | PPM009065 | PPM000829 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European, African unspecified, NR | Agent Input |
| performance_metrics.record_count | 3 | 3 | 3 | 3 | 3 | 3 | 5 | 22 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.5900 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | 0.0122 | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7839 | 0.7848 | 0.7836 | 0.7837 | 0.7834 | 0.7848 | 0.7771 | 0.7700 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | 0.1259 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.0093 | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.783850849010177} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.784836989151752} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.7836188471857} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.783728758270691} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.783365290706975} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.784836989151752} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.77705, 'ci_lower': 0.76156, 'ci_upper': 0.79255} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.77, 'ci_lower': 0.76, 'ci_upper': 0.78} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.12586} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00931} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01217} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.59003, 'ci_lower': 0.56941, 'ci_upper': 0.61066} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.554, 'ci_lower': 1.47, 'ci_upper': 1.64} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.578, 'ci_lower': 1.5, 'ci_upper': 1.67} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.546, 'ci_lower': 1.47, 'ci_upper': 1.63} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.535, 'ci_lower': 1.46, 'ci_upper': 1.62} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.527, 'ci_lower': 1.45, 'ci_upper': 1.61} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.578, 'ci_lower': 1.5, 'ci_upper': 1.67} | N/A | N/A | Agent Input |
| validation_sample_size | n=30,379 | n=30,379 | n=30,379 | n=30,379 | n=30,379 | n=30,379 | n=24,905 | n=147,985 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | n=269,704 | n=80,103 | Agent Input |
| ancestry_distribution | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: AFR (2%), AMR (2%), EAS (6%), EUR (75%), GME (1%), SAS (14%) / DEV: MAE (100%) / EVAL: EUR (17%), MAE (83%) | Agent Input |
| training_development_cohorts | MVP | MVP | MVP | MVP | MVP | MVP | UKB | ADVANCE AGES AIDHS ARIC BAS BioMe CARDIOGENICS CAS CCGB COROGENE DUKE_2 EGCUT FGENTCARD FHS FINRISK FamHS GENRIC GerMIFS GoDARTS HPS HSDS HSIEA ITH LIFE-HEART LOLIPOP LURIC MAYO-VDB MIGen MedSTAR OHGS PIVUS PROCARDIS PROMIS PROSPER PennCATH RS SDS TwinGene UKB ULSAM WGHS WTCCC | Agent Input |
| publication.title | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Predictive Accuracy of a Polygenic Risk Score-Enhanced Prediction Model vs a Clinical Risk Score for Coronary Artery Disease. | Agent Input |
| publication.journal | HGG Adv | HGG Adv | HGG Adv | HGG Adv | HGG Adv | HGG Adv | PLoS Genet | JAMA | Agent Input |
| date_release | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2021-10-21 | 2020-03-27 | Agent Input |
| variants_number | 1273897 | 1286612 | 1273897 | 1273897 | 1273891 | 1286612 | 1108 | 297862 | Agent Input |
| covariates | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, UKB array type, Genotype PCs | pooled cohort equations | Agent Input |


### heart failure

Candidate pool: `34` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005097 | PGS005078 | PGS005076 | PGS005077 | PGS005083 | PGS005097 | PGS001790 | PGS000709 | Agent Input |
| AoU benchmark rank | 1/33 | 2/33 | 3/33 | 4/33 | 5/33 | 1/33 | 11/33 | 19/33 | Benchmark Only |
| AoU benchmark AUC | 0.6110 | 0.5947 | 0.5938 | 0.5938 | 0.5931 | 0.6110 | 0.5781 | 0.5418 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 7/10 trials | 8/10 trials | 9/10 trials | Benchmark Only |
| trait_reported | Heart failure | Congestive heart failure (CHF), NOS (PheCode 428.1) | Congestive heart failure (CHF), NOS (PheCode 428.1) | Congestive heart failure (CHF), NOS (PheCode 428.1) | Congestive heart failure (CHF), NOS (PheCode 428.1) | Heart failure | Heart failure | Heart failure | Agent Input |
| trait_efo | heart failure | congestive heart failure | congestive heart failure | congestive heart failure | congestive heart failure | heart failure | heart failure | heart failure | Agent Input |
| phenotyping_reported | Prevalent heart failure | Congestive heart failure (CHF), NOS | Congestive heart failure (CHF), NOS | Congestive heart failure (CHF), NOS | Congestive heart failure (CHF), NOS | Prevalent heart failure | Heart Failure | Heart failure | Agent Input |
| method_name | PRS-CSx | ldpred | ldpred | ldpred | prscs | PRS-CSx | PRS-CS-auto | snpnet (multi-PRS) | Agent Input |
| performance_metrics.selected_performance_id | PPM022207 | PPM021961 | PPM021959 | PPM021960 | PPM021868 | PPM022207 | PPM009294 | PPM001614 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African unspecified | European | European | European | European | European, African unspecified | European | European | Agent Input |
| performance_metrics.record_count | 1 | 3 | 3 | 3 | 3 | 1 | 1 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | 0.0070 | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7200 | 0.7525 | 0.7532 | 0.7536 | 0.7537 | 0.7200 | 0.7500 | 0.6350 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.72, 'ci_lower': 0.72, 'ci_upper': 0.73} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75253114316328} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.753249050693995} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.753575892982002} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.753682708175126} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.72, 'ci_lower': 0.72, 'ci_upper': 0.73} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.75} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.635} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Brier skill score', 'name_short': 'Brier skill score', 'estimate': 0.065, 'ci_lower': 0.063, 'ci_upper': 0.068} | N/A | N/A | N/A | N/A | {'name_long': 'Brier skill score', 'name_short': 'Brier skill score', 'estimate': 0.065, 'ci_lower': 0.063, 'ci_upper': 0.068} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.006981} | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.442, 'ci_lower': 1.37, 'ci_upper': 1.52} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.443, 'ci_lower': 1.37, 'ci_upper': 1.52} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.452, 'ci_lower': 1.38, 'ci_upper': 1.53} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.455, 'ci_lower': 1.38, 'ci_upper': 1.54} | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.08, 'ci_lower': 1.06, 'ci_upper': 1.1} | Agent Input |
| validation_sample_size | n=40,989 | n=31,804 | n=31,804 | n=31,804 | n=31,804 | n=40,989 | n=358,905 | n=135,300 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | N/A | n=223,327 | Agent Input |
| ancestry_distribution | GWAS: AFR (6%), AMR (3%), EAS (11%), EUR (80%) / EVAL: MAE (100%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: AFR (6%), AMR (3%), EAS (11%), EUR (80%) / EVAL: MAE (100%) | GWAS: AFR (3%), ASN (2%), EAS (28%), EUR (65%), OTH (2%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ BioMe CKB FinnGen GBMI HERMES MVP MyCode UCLA eMERGE | MVP | MVP | MVP | MVP | BBJ BioMe CKB FinnGen GBMI HERMES MVP MyCode UCLA eMERGE | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT MGBB MGI UCLA | UKB | Agent Input |
| publication.title | Common-variant and rare-variant genetic architecture of heart failure across the allele-frequency spectrum. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Common-variant and rare-variant genetic architecture of heart failure across the allele-frequency spectrum. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Genetics of 35 blood and urine biomarkers in the UK Biobank. | Agent Input |
| publication.journal | Nat Genet | HGG Adv | HGG Adv | HGG Adv | HGG Adv | Nat Genet | Cell Genom | Nat Genet | Agent Input |
| date_release | 2025-04-17 | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2025-04-17 | 2022-09-08 | 2021-02-03 | Agent Input |
| variants_number | 1274692 | 1286612 | 1286612 | 1286612 | 1273897 | 1274692 | 910146 | 183287 | Agent Input |
| covariates | Age, sex, 5 genetic principal components | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | Age, sex, 5 genetic principal components | sex,age,age2,age*sex,age^2*sex, 20PCs | Age as time scale, sex, batch, PCs(1-10) | Agent Input |


### thyroid carcinoma

Candidate pool: `32` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005260 | PGS005274 | PGS005273 | PGS005259 | PGS005258 | PGS000630 | PGS000208 | PGS000087 | Agent Input |
| AoU benchmark rank | 1/32 | 2/32 | 3/32 | 4/32 | 5/32 | 14/32 | 16/32 | 19/32 | Benchmark Only |
| AoU benchmark AUC | 0.8113 | 0.8069 | 0.8016 | 0.7865 | 0.6376 | 0.5895 | 0.5890 | 0.5868 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Thyroid carcenoma | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma | Thyroid carcenoma | Thyroid cancer | Thyroid cancer | Thyroid cancer | Agent Input |
| trait_efo | thyroid carcinoma | benign, thyroid carcinoma, nodular goiter | benign, thyroid carcinoma, nodular goiter | thyroid carcinoma | thyroid carcinoma | thyroid carcinoma | thyroid carcinoma | thyroid carcinoma | Agent Input |
| phenotyping_reported | thyroid carcenoma | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma | thyroid carcenoma | Thyroid cancer | Thyroid cancer | Incident thyroid cancer | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | PRSCS | Pruning and Thresholding (P+T) | GWAS Hits | Genome-wide significant variants | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM022743 | PPM022757 | PPM022756 | PPM022742 | PPM022741 | PPM001315 | PPM000632 | PPM002052 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6845 | 0.6135 | 0.6174 | 0.6953 | 0.6862 | 0.6260 | 0.7510 | 0.6790 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | 0.0393 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.684522760200784} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.613489463745261} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.617388005401901} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.695254013741303} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.686161285410893} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.626, 'ci_lower': 0.597, 'ci_upper': 0.655} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.751, 'ci_lower': 0.736, 'ci_upper': 0.768} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.679} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.666, 'se': 0.023} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0393} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0811} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.53, 'ci_lower': 1.87, 'ci_upper': 6.66} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.96019114706853} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.673041992501825} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49346171423604} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.401096723418125} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.55051776688383} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.438588918302023} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.03688674186851} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.71142253524162} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.02} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.016} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.598, 'ci_lower': 1.439, 'ci_upper': 1.775} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.469, 'se': 0.0536} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.57, 'ci_lower': 1.36, 'ci_upper': 1.82} | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=4,270 | n=130,279 | n=391,189 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | n=4,481 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (50%), MAE (50%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BioMe BioVU HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT KCPS LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT KCPS LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | MGI | NBS UKB | N/A | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Assessing thyroid cancer risk using polygenic risk scores. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | medRxiv | Am J Hum Genet | Proc Natl Acad Sci U S A | Nat Commun | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2020-12-15 | 2020-07-01 | 2020-02-12 | Agent Input |
| variants_number | 1085170 | 1084965 | 1085164 | 1085173 | 84 | 10 | 10 | 12 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | age, sex, batch PCs 1-4 | gender, birth year, family history of disease (1st or 2nd degree relative) | Age at assessment, sex,, genotyping array, PCs(1-15), body mass index (BMI <25 vs. 25≤BMI<30, BMI≥30) | Agent Input |


### psoriasis

Candidate pool: `31` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005309 | PGS005311 | PGS004315 | PGS005312 | PGS005310 | PGS001312 | PGS001312 | PGS000342 | Agent Input |
| AoU benchmark rank | 1/24 | 2/24 | 3/24 | 4/24 | 5/24 | 15/24 | 15/24 | 24/24 | Benchmark Only |
| AoU benchmark AUC | 0.6087 | 0.6086 | 0.6014 | 0.5958 | 0.5958 | 0.5718 | 0.5718 | 0.5030 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Psoriasis | Psoriasis | Psoriasis | Psoriasis | Psoriasis | Psoriasis | Psoriasis | Psoriatic arthritis | Agent Input |
| trait_efo | psoriasis | psoriasis | psoriasis | psoriasis | psoriasis | psoriasis | psoriasis | psoriatic arthritis | Agent Input |
| phenotyping_reported | Severe psoriasis | Severe psoriasis (BSTOP) vs. any psoriasis (UKB) | Psoriasis severity | Severe psoriasis (BSTOP) vs. any psoriasis (UKB) | Severe psoriasis | Psoriasis | Psoriasis | Psoriatic arthritis | Agent Input |
| method_name | SBayesR | SBayesR | Genome-wide significant SNPs | SBayesR | SBayesR | snpnet | snpnet | GWAS-significant variants, HLA-specific significant variants. | Agent Input |
| performance_metrics.selected_performance_id | PPM023021 | PPM023031 | PPM020388 | PPM023032 | PPM023022 | PPM009057 | PPM009057 | PPM000971 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | NR | Agent Input |
| performance_metrics.record_count | 4 | 2 | 7 | 2 | 4 | 5 | 5 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | 0.6916 | 0.6916 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0523 | 0.0523 | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | 0.6975 | 0.6975 | 0.5620 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0610 | N/A | N/A | 0.0557 | 0.0557 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | 0.1451 | 0.1451 | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69754, 'ci_lower': 0.68165, 'ci_upper': 0.71343} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69754, 'ci_lower': 0.68165, 'ci_upper': 0.71343} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.562, 'ci_lower': 0.506, 'ci_upper': 0.618} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'name_short': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'estimate': 15.3} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.061} | {'name_long': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'name_short': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'estimate': 15.3} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05574} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.14505} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05226} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.69158, 'ci_lower': 0.6754, 'ci_upper': 0.70775} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05574} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.14505} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05226} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.69158, 'ci_lower': 0.6754, 'ci_upper': 0.70775} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49, 'ci_lower': 1.41, 'ci_upper': 1.57} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.02, 'ci_lower': 1.0, 'ci_upper': 1.06} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.38, 'ci_lower': 1.31, 'ci_upper': 1.45} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=14,167 | n=13,577 | n=654 | n=13,577 | n=14,167 | n=67,425 | n=67,425 | n=543 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | n=269,704 | n=269,704 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: NR (100%) | Agent Input |
| training_development_cohorts | CASP Genizon KIEL UCSF WTCCC | CASP Genizon KIEL UCSF WTCCC | N/A | CASP Genizon KIEL UCSF WTCCC | CASP Genizon KIEL UCSF WTCCC | UKB | UKB | N/A | Agent Input |
| publication.title | Genetic liability to psoriasis predicts severe disease outcomes. | Genetic liability to psoriasis predicts severe disease outcomes. | A partitioned 88-loci psoriasis genetic risk score reveals HLA and non-HLA contributions to clinical phenotypes in a Newfoundland psoriasis cohort. | Genetic liability to psoriasis predicts severe disease outcomes. | Genetic liability to psoriasis predicts severe disease outcomes. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Evaluation of a Genetic Risk Score for Diagnosis of Psoriatic Arthritis. | Agent Input |
| publication.journal | Genome Med | Genome Med | Front Genet | Genome Med | Genome Med | PLoS Genet | PLoS Genet | J Psoriasis Psoriatic Arthritis | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2024-01-11 | 2026-01-19 | 2026-01-19 | 2021-10-21 | 2021-10-21 | 2020-11-20 | Agent Input |
| variants_number | 513461 | 487311 | 88 | 487310 | 513460 | 204 | 204 | 11 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Unknown | Agent Input |


### depressive disorder

Candidate pool: `30` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004760 | PGS003333 | PGS004759 | PGS000907 | PGS004885 | PGS003333 | PGS002036 | PGS000138 | Agent Input |
| AoU benchmark rank | 1/30 | 2/30 | 3/30 | 4/30 | 5/30 | 2/30 | 21/30 | 22/30 | Benchmark Only |
| AoU benchmark AUC | 0.5779 | 0.5687 | 0.5650 | 0.5648 | 0.5504 | 0.5687 | 0.5230 | 0.5224 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 5/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Depression | Major Depressive Disorder | Depression | Major depressive disorder | Major depressive disorder | Major Depressive Disorder | Depression | Lifetime Major Depressive Disorder | Agent Input |
| trait_efo | major depressive disorder | major depressive disorder | major depressive disorder | major depressive disorder | major depressive disorder | major depressive disorder | depressive disorder | major depressive disorder | Agent Input |
| phenotyping_reported | Depression | Major Depressive Disorder | Depression | Muscle pain in Fluoxetine takers | Incident MDD | Major Depressive Disorder | Depression | Major Depressive Disorder status | Agent Input |
| method_name | PRSmixPlus | PRS-CS-auto | PRSmix | SBayesR | megaprs.auto | PRS-CS-auto | LDpred2 (bigsnpr) | LD-clumping and p-value thresholding (Ricopilli) | Agent Input |
| performance_metrics.selected_performance_id | PPM020985 | PPM016144 | PPM020984 | PPM002717 | PPM021256 | PPM016144 | PPM011155 | PPM000430 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 50 | 7 | 1 | 8 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | 0.6200 | N/A | N/A | 0.5611 | Agent Input |
| performance_metrics.full_model_r2 | 0.0240 | 0.0220 | 0.0160 | 0.7700 | N/A | 0.0220 | N/A | 0.0182 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.62, 'ci_lower': 0.58, 'ci_upper': 0.65} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.5611035} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.024, 'ci_lower': 0.018, 'ci_upper': 0.03} | {'name_long': 'Nagelkerke pseudo-R2', 'name_short': 'Nagelkerke pseudo-R2', 'estimate': 0.022} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.016, 'ci_lower': 0.011, 'ci_upper': 0.021} | {'name_long': "Variance explained (Nagelkerke's R2*100)", 'name_short': "Variance explained (Nagelkerke's R2*100)", 'estimate': 0.77} | N/A | {'name_long': 'Nagelkerke pseudo-R2', 'name_short': 'Nagelkerke pseudo-R2', 'estimate': 0.022} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0556, 'ci_lower': 0.041, 'ci_upper': 0.0703} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.018171054} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.3, 'ci_lower': 1.05, 'ci_upper': 1.6} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.36, 'ci_lower': 1.21, 'ci_upper': 1.53} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=9,462 | n=34,703 | n=9,462 | n=3,670 | n=7,018 | n=34,703 | n=17,764 | n=36,709 | Agent Input |
| samples_training | n=37,851 | N/A | n=37,851 | N/A | n=404 | N/A | n=391,124 | N/A | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AllofUs | 23andMe PGC UKB | AllofUs | N/A | 1000G | 23andMe PGC UKB | UKB | UKB | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Polygenic Liability to Depression Is Associated With Multiple Medical Conditions in the Electronic Health Record: Phenome-wide Association Study of 46,782 Individuals. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Understanding genetic risk factors for common side effects of antidepressant medications | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Polygenic Liability to Depression Is Associated With Multiple Medical Conditions in the Electronic Health Record: Phenome-wide Association Study of 46,782 Individuals. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Minimal phenotyping yields genome-wide association signals of low specificity for major depression. | Agent Input |
| publication.journal | Cell Genom | Biol Psychiatry | Cell Genom | Commun Med (Lond) | Nat Commun | Biol Psychiatry | Am J Hum Genet | Nat Genet | Agent Input |
| date_release | 2024-03-28 | 2022-12-06 | 2024-03-28 | 2021-10-07 | 2024-06-27 | 2022-12-06 | 2022-01-10 | 2020-04-29 | Agent Input |
| variants_number | 2141267 | 1088415 | 1538576 | 1773528 | 801544 | 1088415 | 807338 | 22274 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | Unknown | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | sex, age at study enrollment, genetic PCs 1-20 | PCs 1-10 | Unknown | sex, age, birth date, deprivation index, 16 PCs | Cohort | Agent Input |


### hypothyroidism

Candidate pool: `28` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005268 | PGS005269 | PGS005218 | PGS005267 | PGS004789 | PGS005218 | PGS005218 | PGS000759 | Agent Input |
| AoU benchmark rank | 1/28 | 2/28 | 3/28 | 4/28 | 5/28 | 3/28 | 3/28 | 19/28 | Benchmark Only |
| AoU benchmark AUC | 0.6575 | 0.6567 | 0.6289 | 0.6240 | 0.6231 | 0.6289 | 0.6289 | 0.5950 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Agent Input |
| trait_efo | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | Agent Input |
| phenotyping_reported | hypothyroidism | hypothyroidism | Incident hypothyroidism | hypothyroidism | Hypothyroidism | Incident hypothyroidism | Incident hypothyroidism | anti-PD-L1 induced hypothyroidism in cancer patients | Agent Input |
| method_name | PRSCS | PRSCS | PRS-CS | Pruning and Thresholding (P+T) | PRSmix | PRS-CS | PRS-CS | GCTA-COJO forward selection highest PPA variants | Agent Input |
| performance_metrics.selected_performance_id | PPM022751 | PPM022752 | PPM022617 | PPM022750 | PPM021014 | PPM022617 | PPM022617 | PPM001934 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 6 | 1 | 1 | 6 | 6 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6389 | 0.6386 | 0.8590 | 0.6400 | N/A | 0.8590 | 0.8590 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0410 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638920940728866} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638628477117025} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.859, 'ci_lower': 0.821, 'ci_upper': 0.897} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.859, 'ci_lower': 0.821, 'ci_upper': 0.897} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.859, 'ci_lower': 0.821, 'ci_upper': 0.897} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.041, 'ci_lower': 0.033, 'ci_upper': 0.049} | N/A | N/A | {'name_long': 'meta-analysis p-value', 'name_short': 'meta-analysis p-value', 'estimate': 7.52e-09} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65808867613792} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.505665539081399} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65210243632159} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.502048680634994} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.142} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.133} | N/A | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.52, 'ci_lower': 1.31, 'ci_upper': 1.74} | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=441,692 | n=94,651 | n=9,462 | n=441,692 | n=441,692 | n=1,584 | Agent Input |
| samples_training | N/A | N/A | n=1,146,562 | N/A | n=37,851 | n=1,146,562 | n=1,146,562 | n=408,959 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BioMe BioVU EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | 23andMe CHB DBDS EB FinnGen UKB deCODE | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs | 23andMe CHB DBDS EB FinnGen UKB deCODE | 23andMe CHB DBDS EB FinnGen UKB deCODE | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Genetic variation associated with thyroid autoimmunity shapes the systemic immune response to PD-1 checkpoint blockade. | Agent Input |
| publication.journal | medRxiv | medRxiv | Nat Genet | medRxiv | Cell Genom | Nat Genet | Nat Genet | Nat Commun | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2025-11-10 | 2026-01-19 | 2024-03-28 | 2025-11-10 | 2025-11-10 | 2021-06-11 | Agent Input |
| variants_number | 1085173 | 1085170 | 1110091 | 439 | 1109333 | 1110091 | 1110091 | 140 | Agent Input |
| covariates | Unknown | Unknown | age, sex, TSH, T4, anti-TPO, PC1, PC2, PC3, PC4 | Unknown | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, TSH, T4, anti-TPO, PC1, PC2, PC3, PC4 | age, sex, TSH, T4, anti-TPO, PC1, PC2, PC3, PC4 | 5 genotype PCs | Agent Input |


### hodgkins lymphoma

Candidate pool: `27` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000639 | PGS003449 | PGS000638 | PGS003454 | PGS000648 | PGS000639 | PGS000639 | PGS000080 | Agent Input |
| AoU benchmark rank | 1/27 | 2/27 | 3/27 | 4/27 | 5/27 | 1/27 | 1/27 | 17/27 | Benchmark Only |
| AoU benchmark AUC | 0.6180 | 0.6120 | 0.6014 | 0.5597 | 0.5586 | 0.6180 | 0.6180 | 0.5067 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Hodgkin's disease | Hodgkin lymphoma | Hodgkin's disease | Diffuse large B-cell lymphoma | Chronic lymphocytic leukemia | Hodgkin's disease | Hodgkin's disease | Non-Hodgkin's lymphoma | Agent Input |
| trait_efo | Hodgkins lymphoma | Hodgkins lymphoma | Hodgkins lymphoma | diffuse large B-cell lymphoma | chronic lymphocytic leukemia | Hodgkins lymphoma | Hodgkins lymphoma | non-Hodgkins lymphoma | Agent Input |
| phenotyping_reported | Hodgkin's disease | Chronic lymphocytic leukemia | Hodgkin's disease | Chronic lymphocytic leukemia | Lymphoid leukemia, chronic | Hodgkin's disease | Hodgkin's disease | Incident non-hodgkin's lymphoma | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Genome-wide significant SNPs | GWAS Hits | Genome-wide significant SNPs | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM001324 | PPM017231 | PPM001323 | PPM017225 | PPM001333 | PPM001324 | PPM001324 | PPM002046 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 4 | 1 | 4 | 1 | 1 | 1 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6200 | N/A | 0.6010 | N/A | 0.6960 | 0.6200 | 0.6200 | 0.6770 | Agent Input |
| performance_metrics.full_model_r2 | 0.0276 | N/A | 0.0193 | N/A | 0.1020 | 0.0276 | 0.0276 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62, 'ci_lower': 0.559, 'ci_upper': 0.688} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.601, 'ci_lower': 0.535, 'ci_upper': 0.671} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696, 'ci_lower': 0.621, 'ci_upper': 0.764} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62, 'ci_lower': 0.559, 'ci_upper': 0.688} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62, 'ci_lower': 0.559, 'ci_upper': 0.688} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.677} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.676, 'se': 0.01} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0276} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.64, 'ci_lower': 0.572, 'ci_upper': 12.2} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0193} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0824} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.62, 'ci_lower': 0.258, 'ci_upper': 10.1} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.102} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0776} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 12.9, 'ci_lower': 4.45, 'ci_upper': 37.6} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0276} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.64, 'ci_lower': 0.572, 'ci_upper': 12.2} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0276} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.64, 'ci_lower': 0.572, 'ci_upper': 12.2} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.476, 'ci_lower': 1.154, 'ci_upper': 1.889} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.39, 'se': 0.126} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.02, 'ci_lower': 0.97, 'ci_upper': 1.08} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.377, 'ci_lower': 1.08, 'ci_upper': 1.755} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.32, 'se': 0.124} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33, 'ci_lower': 1.14, 'ci_upper': 1.54} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.124, 'ci_lower': 1.648, 'ci_upper': 2.738} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.753, 'se': 0.13} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.476, 'ci_lower': 1.154, 'ci_upper': 1.889} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.39, 'se': 0.126} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.476, 'ci_lower': 1.154, 'ci_upper': 1.889} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.39, 'se': 0.126} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.09, 'ci_upper': 1.24} | Agent Input |
| validation_sample_size | n=775 | n=20,134 | n=775 | n=20,134 | n=756 | n=775 | n=775 | n=391,968 | Agent Input |
| samples_training | n=736 | N/A | n=736 | N/A | n=730 | n=736 | n=736 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (15%), EUR (85%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MGI | N/A | MGI | N/A | MGI | MGI | MGI | N/A | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Am J Hum Genet | Leukemia | Am J Hum Genet | Leukemia | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Nat Commun | Agent Input |
| date_release | 2020-12-15 | 2023-03-24 | 2020-12-15 | 2023-03-24 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-02-12 | Agent Input |
| variants_number | 20 | 21 | 16 | 5 | 44 | 20 | 20 | 19 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | Unknown | age, sex, batch PCs 1-4 | Unknown | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Age at assessment, sex, genotyping array, PCs(1-15) | Agent Input |


### kidney failure

Candidate pool: `27` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004562 | PGS004561 | PGS000708 | PGS004492 | PGS004158 | PGS000708 | PGS000708 | PGS000708 | Agent Input |
| AoU benchmark rank | 1/27 | 2/27 | 3/27 | 4/27 | 5/27 | 3/27 | 3/27 | 3/27 | Benchmark Only |
| AoU benchmark AUC | 0.5671 | 0.5570 | 0.5529 | 0.5309 | 0.5278 | 0.5529 | 0.5529 | 0.5529 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 8/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | N18 (Chronic renal failure) | N17 (Acute renal failure) | Kidney failure | N18 (Chronic renal failure) | Chronic kidney disease (CKD) | Kidney failure | Kidney failure | Kidney failure | Agent Input |
| trait_efo | kidney failure | acute kidney injury | kidney failure | kidney failure | chronic kidney disease | kidney failure | kidney failure | kidney failure | Agent Input |
| phenotyping_reported | N18 (Chronic renal failure) | N17 (Acute renal failure) | Diabetic kidney failure in all | N18 (Chronic renal failure) | Chronic kidney disease or dialysis | Diabetic kidney failure in all | Diabetic kidney failure in all | Diabetic kidney failure in all | Agent Input |
| method_name | RFDiseasemetaPRS | RFDiseasemetaPRS | snpnet (multi-PRS) | LDpred2 | UKBB-EUR.MultiPRS.CV | snpnet (multi-PRS) | snpnet (multi-PRS) | snpnet (multi-PRS) | Agent Input |
| performance_metrics.selected_performance_id | PPM020677 | PPM020676 | PPM001610 | PPM020607 | PPM019720 | PPM001610 | PPM001610 | PPM001610 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 6 | 1 | 6 | 6 | 6 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.7790 | N/A | 0.5917 | 0.7790 | 0.7790 | 0.7790 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0200 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.779} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59165352, 'ci_lower': 0.58198776, 'ci_upper': 0.60131927} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.779} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.779} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.779} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0199569, 'ci_lower': 0.01607829, 'ci_upper': 0.02453676} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.39548} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.153238} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.19, 'ci_lower': 1.13, 'ci_upper': 1.26} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.17082804315944} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.38924704, 'ci_lower': 1.34216238, 'ci_upper': 1.43798349} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.3287619, 'ci_lower': 0.29428203, 'ci_upper': 0.36324178} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.19, 'ci_lower': 1.13, 'ci_upper': 1.26} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.19, 'ci_lower': 1.13, 'ci_upper': 1.26} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.19, 'ci_lower': 1.13, 'ci_upper': 1.26} | Agent Input |
| validation_sample_size | n=56,192 | n=56,192 | n=135,300 | n=56,192 | n=90,274 | n=135,300 | n=135,300 | n=135,300 | Agent Input |
| samples_training | n=174,489 | n=174,489 | n=223,327 | n=174,489 | n=13,496 | n=223,327 | n=223,327 | n=223,327 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Genetics of 35 blood and urine biomarkers in the UK Biobank. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Genetics of 35 blood and urine biomarkers in the UK Biobank. | Genetics of 35 blood and urine biomarkers in the UK Biobank. | Genetics of 35 blood and urine biomarkers in the UK Biobank. | Agent Input |
| publication.journal | Commun Biol | Commun Biol | Nat Genet | Commun Biol | Am J Hum Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2024-03-18 | 2024-03-18 | 2021-02-03 | 2024-03-18 | 2023-12-19 | 2021-02-03 | 2021-02-03 | 2021-02-03 | Agent Input |
| variants_number | 1059939 | 1059939 | 183272 | 1059939 | 1135455 | 183272 | 183272 | 183272 | Agent Input |
| covariates | Unknown | Unknown | Age as time scale, sex, batch, PCs(1-10) | Unknown | 0 | Age as time scale, sex, batch, PCs(1-10) | Age as time scale, sex, batch, PCs(1-10) | Age as time scale, sex, batch, PCs(1-10) | Agent Input |


### chronic kidney disease

Candidate pool: `22` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004045 | PGS004030 | PGS004158 | PGS004074 | PGS004088 | PGS002237 | PGS002237 | PGS000728 | Agent Input |
| AoU benchmark rank | 1/22 | 2/22 | 3/22 | 4/22 | 5/22 | 12/22 | 12/22 | 19/22 | Benchmark Only |
| AoU benchmark AUC | 0.5566 | 0.5564 | 0.5562 | 0.5546 | 0.5546 | 0.5466 | 0.5466 | 0.5262 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 9/10 trials | Benchmark Only |
| trait_reported | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (stage 3 or greater) | Chronic kidney disease (stage 3 or greater) | Chronic kidney disease | Agent Input |
| trait_efo | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | Agent Input |
| phenotyping_reported | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic kidney disease (eGFR <45 ml/min per 1.73 m2) | Chronic kidney disease (eGFR <45 ml/min per 1.73 m2) | Estimated Glomerular Filtration Rate (eGFR) | Agent Input |
| method_name | LDpred2.CV | LDpred2-auto | UKBB-EUR.MultiPRS.CV | megaprs.CV | PRS-CS-auto | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | LD thinning | Agent Input |
| performance_metrics.selected_performance_id | PPM019694 | PPM019754 | PPM019720 | PPM019774 | PPM019790 | PPM018708 | PPM018708 | PPM001669 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 6 | 6 | 6 | 6 | 6 | 9 | 9 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5885 | 0.5887 | 0.5917 | 0.5887 | 0.5820 | 0.7800 | 0.7800 | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0187 | 0.0187 | 0.0200 | 0.0186 | 0.0162 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.58851351, 'ci_lower': 0.57882039, 'ci_upper': 0.59820663} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.58871735, 'ci_lower': 0.57899906, 'ci_upper': 0.59843563} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59165352, 'ci_lower': 0.58198776, 'ci_upper': 0.60131927} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.58867836, 'ci_lower': 0.57900777, 'ci_upper': 0.59834895} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.5819827, 'ci_lower': 0.5721855, 'ci_upper': 0.5917799} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78, 'ci_lower': 0.75, 'ci_upper': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78, 'ci_lower': 0.75, 'ci_upper': 0.8} | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01871484, 'ci_lower': 0.01517095, 'ci_upper': 0.0232003} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0187256, 'ci_lower': 0.01506559, 'ci_upper': 0.02314554} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0199569, 'ci_lower': 0.01607829, 'ci_upper': 0.02453676} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01859661, 'ci_lower': 0.01476562, 'ci_upper': 0.02283747} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01615694, 'ci_lower': 0.01278626, 'ci_upper': 0.020327} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37553032, 'ci_lower': 1.32885232, 'ci_upper': 1.42384795} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.31883934, 'ci_lower': 0.28431565, 'ci_upper': 0.35336303} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37576394, 'ci_lower': 1.32906928, 'ci_upper': 1.42409914} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.31900917, 'ci_lower': 0.28447891, 'ci_upper': 0.35353943} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.38924704, 'ci_lower': 1.34216238, 'ci_upper': 1.43798349} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.3287619, 'ci_lower': 0.29428203, 'ci_upper': 0.36324178} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37315168, 'ci_lower': 1.32665979, 'ci_upper': 1.42127286} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.3171086, 'ci_lower': 0.28266434, 'ci_upper': 0.35155285} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.34393774, 'ci_lower': 1.29844261, 'ci_upper': 1.39102695} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.29560392, 'ci_lower': 0.26116555, 'ci_upper': 0.33004229} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.47, 'ci_lower': 1.32, 'ci_upper': 1.65} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.47, 'ci_lower': 1.32, 'ci_upper': 1.65} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': -0.9, 'ci_lower': -1.45, 'ci_upper': -0.36} | Agent Input |
| validation_sample_size | n=90,274 | n=90,274 | n=90,274 | n=90,274 | n=90,274 | n=11,813 | n=11,813 | n=3,037 | Agent Input |
| samples_training | n=13,496 | n=13,496 | n=13,496 | n=13,496 | n=13,496 | n=279,819 | n=279,819 | N/A | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: AFR (14%), AMR (14%), ASN (14%), EUR (29%), MAE (29%) | DEV: EUR (100%) / EVAL: AFR (14%), AMR (14%), ASN (14%), EUR (29%), MAE (29%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | UKB | ADVANCE_TRIAL AFTER_EU AGES Airwave BBJ BioMe CHNS CHRIS CHS CoLaus DC DIACORE ERF FHS FINRISK FamHS GS:SFHS INGI-FVG JHS JUPITER KORA LIFE-Adult LIFE-HEART LLFS LOLIPOP LURIC LifeLines MDC-CC MESA MyCode OGP PIVUS PREVEND QIMR RS SAAR SCES SHIP SIMES SINDI SOLID-TIMI_52 STABILITY TwinGene UKB ULSAM Vanderbilt WGHS deCODE | Agent Input |
| publication.title | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Genome-wide polygenic score to predict chronic kidney disease across ancestries. | Genome-wide polygenic score to predict chronic kidney disease across ancestries. | Integrative analysis of the plasma proteome and polygenic risk of cardiometabolic diseases | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Nat Med | Nat Med | Nat Metab | Agent Input |
| date_release | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2022-01-10 | 2022-01-10 | 2021-02-23 | Agent Input |
| variants_number | 1050295 | 1050295 | 1135455 | 846995 | 1109217 | 471316 | 471316 | 1958860 | Agent Input |
| covariates | 0 | 0 | 0 | 0 | 0 | age, sex, alcohol, smoking, hypertension, diabetes, body mass index, nonsteroidal anti-inflammatory drug and angiotensin-converting enzyme inhibitor/angiotensin receptor blocker use, and visit year | age, sex, alcohol, smoking, hypertension, diabetes, body mass index, nonsteroidal anti-inflammatory drug and angiotensin-converting enzyme inhibitor/angiotensin receptor blocker use, and visit year | age, sex, 10 genetic PCs | Agent Input |


### basal cell carcinoma

Candidate pool: `20` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003417 | PGS003416 | PGS000453 | PGS000452 | PGS000455 | PGS000452 | PGS000452 | PGS000119 | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | 4/20 | 4/20 | 13/20 | Benchmark Only |
| AoU benchmark AUC | 0.6391 | 0.6356 | 0.6213 | 0.6213 | 0.6213 | 0.6213 | 0.6213 | 0.6120 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 7/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Basal cell carcinoma | Basal cell carcinoma (MTAG) | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Agent Input |
| trait_efo | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | Agent Input |
| phenotyping_reported | Keratinocyte cancers | Keratinocyte cancers | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Agent Input |
| method_name | Genome-wide significant SNPs | Genome-wide significant SNPs | GWAS Hits | GWAS Hits | Pruning and Thresholding (P+T) | GWAS Hits | GWAS Hits | GWAS Catalog SNPs | Agent Input |
| performance_metrics.selected_performance_id | PPM017070 | PPM017069 | PPM001138 | PPM001137 | PPM001140 | PPM001137 | PPM001137 | PPM000341 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.6110 | 0.6320 | 0.6110 | 0.6320 | 0.6320 | 0.6400 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0301 | 0.0487 | 0.0301 | 0.0487 | 0.0487 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.611, 'ci_lower': 0.604, 'ci_upper': 0.619} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.632, 'ci_lower': 0.616, 'ci_upper': 0.647} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.611, 'ci_lower': 0.604, 'ci_upper': 0.619} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.632, 'ci_lower': 0.616, 'ci_upper': 0.647} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.632, 'ci_lower': 0.616, 'ci_upper': 0.647} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64, 'ci_lower': 0.62, 'ci_upper': 0.66} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0301} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0813} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.8, 'ci_lower': 2.33, 'ci_upper': 3.36} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0487} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.106} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.61, 'ci_lower': 2.53, 'ci_upper': 5.15} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0301} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0813} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.8, 'ci_lower': 2.33, 'ci_upper': 3.36} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0487} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.106} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.61, 'ci_lower': 2.53, 'ci_upper': 5.15} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0487} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.106} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.61, 'ci_lower': 2.53, 'ci_upper': 5.15} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.56, 'ci_lower': 1.45, 'ci_upper': 1.67} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.66, 'ci_lower': 1.55, 'ci_upper': 1.79} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.511, 'ci_lower': 1.47, 'ci_upper': 1.554} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.413, 'se': 0.0142} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.663, 'ci_lower': 1.57, 'ci_upper': 1.761} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.508, 'se': 0.0293} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.511, 'ci_lower': 1.47, 'ci_upper': 1.554} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.413, 'se': 0.0142} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.663, 'ci_lower': 1.57, 'ci_upper': 1.761} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.508, 'se': 0.0293} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.663, 'ci_lower': 1.57, 'ci_upper': 1.761} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.508, 'se': 0.0293} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65, 'ci_lower': 1.56, 'ci_upper': 1.75} | Agent Input |
| validation_sample_size | n=18,933 | n=18,933 | n=60,018 | n=11,322 | n=60,018 | n=11,322 | n=11,322 | n=20,468 | Agent Input |
| samples_training | N/A | N/A | n=61,038 | n=11,734 | n=61,038 | n=11,734 | n=11,734 | n=10,234 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | GERA QSKIN UKB eMERGE | UKB | MGI | UKB | MGI | MGI | MGI | Agent Input |
| publication.title | A multi-phenotype analysis reveals 19 susceptibility loci for basal cell carcinoma and 15 for squamous cell carcinoma. | A multi-phenotype analysis reveals 19 susceptibility loci for basal cell carcinoma and 15 for squamous cell carcinoma. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Exploring various polygenic risk scores for skin cancer in the phenomes of the Michigan genomics initiative and the UK Biobank with a visual catalog: PRSWeb. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | PLoS Genet | Agent Input |
| date_release | 2023-02-08 | 2023-02-08 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-03-27 | Agent Input |
| variants_number | 273 | 462 | 28 | 28 | 28 | 28 | 28 | 32 | Agent Input |
| covariates | age, sex, 10 ancesty PCs | age, sex, 10 ancesty PCs | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch, PC1-4 | Agent Input |


### sleep apnea

Candidate pool: `20` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005220 | PGS005219 | PGS003479 | PGS003213 | PGS003857 | PGS005220 | PGS005220 | PGS003204 | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | 1/20 | 1/20 | 17/20 | Benchmark Only |
| AoU benchmark AUC | 0.5784 | 0.5454 | 0.5418 | 0.5217 | 0.5167 | 0.5784 | 0.5784 | 0.5006 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 8/10 trials | 9/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (AdjustedBMI) | Obstructive sleep apnea | Sleep apnea | Obstructive sleep apnea | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (UnadjustedBMI) | Sleep apnea | Agent Input |
| trait_efo | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | sleep apnea | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | sleep apnea | Agent Input |
| phenotyping_reported | Obstructive sleep apnea | Obstructive sleep apnea | DBP | Sleep Apnea | BMI adjusted obstructive sleep apnea | Obstructive sleep apnea | Obstructive sleep apnea | Sleep Apnea | Agent Input |
| method_name | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | LDpred2 | PRS-CS | Genome-wide significant SNPs | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | lassosum | Agent Input |
| performance_metrics.selected_performance_id | PPM022620 | PPM022619 | PPM017318 | PPM015955 | PPM018710 | PPM022620 | PPM022620 | PPM015959 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | Hispanic or Latin American | European | African unspecified, Asian unspecified, European, Hispanic or Latin American, Not reported | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 34 | 1 | 2 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7900 | 0.7900 | N/A | 0.5270 | 0.7700 | 0.7900 | 0.7900 | 0.4900 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.527, 'ci_lower': 0.517, 'ci_upper': 0.536} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.77, 'ci_lower': 0.75, 'ci_upper': 0.78} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.49, 'ci_lower': 0.482, 'ci_upper': 0.499} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.98, 'ci_lower': 1.74, 'ci_upper': 2.24} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.038, 'se': 0.093} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.106, 'ci_lower': 1.071, 'ci_upper': 1.142} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.101, 'se': 0.0162} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.014, 'se': 0.017} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 0.983, 'ci_lower': 0.952, 'ci_upper': 1.014} {'name_long': 'Beta', 'name_short': 'β', 'estimate': -0.0174, 'se': 0.016} | Agent Input |
| validation_sample_size | n=21,975 | n=21,975 | n=1,115 | n=21,354 | n=40,193 | n=21,975 | n=21,975 | n=21,354 | Agent Input |
| samples_training | N/A | N/A | N/A | n=21,209 | N/A | N/A | N/A | n=21,209 | Agent Input |
| ancestry_distribution | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (19%), AMR (8%), ASN (1%), EUR (72%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | FinnGen MGBB MVP | FinnGen MGBB MVP | N/A | UKB | MVP | FinnGen MGBB MVP | FinnGen MGBB MVP | FinnGen | Agent Input |
| publication.title | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Genetic determinants of cardiometabolic and pulmonary phenotypes and obstructive sleep apnoea in HCHS/SOL. | ExPRSweb: An online repository with polygenic risk scores for common health-related exposures. | Genome-wide association study of obstructive sleep apnoea in the Million Veteran Program uncovers genetic heterogeneity by sex. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | ExPRSweb: An online repository with polygenic risk scores for common health-related exposures. | Agent Input |
| publication.journal | EBioMedicine | EBioMedicine | EBioMedicine | Am J Hum Genet | EBioMedicine | EBioMedicine | EBioMedicine | Am J Hum Genet | Agent Input |
| date_release | 2025-06-16 | 2025-06-16 | 2023-03-24 | 2022-11-23 | 2023-09-01 | 2025-06-16 | 2025-06-16 | 2022-11-23 | Agent Input |
| variants_number | 984184 | 982740 | 836839 | 1111194 | 18 | 984184 | 984184 | 4360 | Agent Input |
| covariates | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | Age, sex, center, 5 genetic PCs, Hispanic/Latino background, BMI | SEX,AGE,Batch,PC1,PC2,PC3,PC4 | BMI, age, sex, genetic batch, PCs 1-10 | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | SEX,AGE,Batch,PC1,PC2,PC3,PC4 | Agent Input |


### urinary bladder cancer

Candidate pool: `20` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000152 | PGS001807 | PGS000782 | PGS000071 | PGS000613 | PGS000611 | PGS000071 | PGS000071 | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | 11/20 | 4/20 | 4/20 | Benchmark Only |
| AoU benchmark AUC | 0.5682 | 0.5583 | 0.5565 | 0.5565 | 0.5534 | 0.5481 | 0.5565 | 0.5565 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | 5/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Agent Input |
| trait_efo | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | Agent Input |
| phenotyping_reported | Bladder cancer | Cancer of bladder | Incident blader cancer | Incident blader cancer | Cancer of bladder | Cancer of bladder | Incident blader cancer | Incident blader cancer | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Penalized regression (bigstatsr) | 15 variants from Graff et al (PGS000071) with inverse variant weights | Genome-wide significant variants | Pruning and Thresholding (P+T) | GWAS Hits | Genome-wide significant variants | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM000472 | PPM009359 | PPM002053 | PPM002037 | PPM001298 | PPM001296 | PPM002037 | PPM002037 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 8 | 1 | 3 | 1 | 1 | 3 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.8040 | 0.8030 | 0.5710 | 0.5670 | 0.8030 | 0.8030 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.6280 | N/A | 0.0125 | 0.0114 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.804} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.814, 'se': 0.008} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.803} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.813, 'se': 0.008} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.571, 'ci_lower': 0.555, 'ci_upper': 0.588} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.567, 'ci_lower': 0.551, 'ci_upper': 0.584} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.803} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.813, 'se': 0.008} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.803} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.813, 'se': 0.008} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Mean realative risk', 'name_short': 'Mean realative risk', 'estimate': 1.04, 'ci_lower': 1.0, 'ci_upper': 1.08} {'name_long': 'Wilcoxon test (case vs. control) p-value', 'name_short': 'Wilcoxon test (case vs. control) p-value', 'estimate': 0.00377} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0197, 'ci_lower': 0.0058, 'ci_upper': 0.0336} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.628} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0125} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.91, 'ci_lower': 1.99, 'ci_upper': 4.24} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0114} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.66, 'ci_lower': 1.79, 'ci_upper': 3.93} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.3, 'ci_lower': 1.22, 'ci_upper': 1.39} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.28, 'ci_lower': 1.2, 'ci_upper': 1.37} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.301, 'ci_lower': 1.227, 'ci_upper': 1.379} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.263, 'se': 0.0299} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.284, 'ci_lower': 1.211, 'ci_upper': 1.361} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.25, 'se': 0.0298} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.28, 'ci_lower': 1.2, 'ci_upper': 1.37} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.28, 'ci_lower': 1.2, 'ci_upper': 1.37} | Agent Input |
| validation_sample_size | n=13,770 | n=19,893 | n=391,888 | n=391,888 | n=13,530 | n=13,530 | n=391,888 | n=391,888 | Agent Input |
| samples_training | N/A | n=391,124 | N/A | N/A | n=12,992 | n=12,992 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ICR NBCS NBS UMC deCODE | UKB | ASHRAM ATBC BBCS_b CPSII DBCS EAGLE EPIC FPCC FrBCS HPFS IBCS ICR LABCS LBCS MEC MSKBCS NBCS NBS NCBCS NEBCS NHS NeuBCS PLCO SANBCS SBCS SpBCS TBCS TXBCS UMC WHI deCODE | ATBC BBCS_b CPSII EAGLE EPIC FPCC FrBCS HPFS ICR LABCS MEC NBCS NBS NEBCS NHS PLCO SpBCS TXBCS UMC WHI deCODE | UKB | UKB | ATBC BBCS_b CPSII EAGLE EPIC FPCC FrBCS HPFS ICR LABCS MEC NBCS NBS NEBCS NHS PLCO SpBCS TXBCS UMC WHI deCODE | ATBC BBCS_b CPSII EAGLE EPIC FPCC FrBCS HPFS ICR LABCS MEC NBCS NBS NEBCS NHS PLCO SpBCS TXBCS UMC WHI deCODE | Agent Input |
| publication.title | Systematic evaluation of cancer-specific genetic risk score for 11 types of cancer in The Cancer Genome Atlas and Electronic Medical Records and Genomics cohorts. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Cancer Med | Am J Hum Genet | Nat Commun | Nat Commun | Am J Hum Genet | Am J Hum Genet | Nat Commun | Nat Commun | Agent Input |
| date_release | 2020-04-29 | 2022-01-10 | 2021-05-28 | 2020-02-12 | 2020-12-15 | 2020-12-15 | 2020-02-12 | 2020-02-12 | Agent Input |
| variants_number | 10 | 291 | 15 | 15 | 15 | 13 | 15 | 15 | Agent Input |
| covariates | Unknown | sex, age, birth date, deprivation index, 16 PCs | Age at assessment, sex, genotyping array, PCs(1-15), cigarette pack-years, smoking status(never vs. former vs. current), body mass index | Age at assessment, sex, genotyping array, PCs(1-15), cigarette pack-years, smoking status(never vs. former vs. current), body mass index | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Age at assessment, sex, genotyping array, PCs(1-15), cigarette pack-years, smoking status(never vs. former vs. current), body mass index | Age at assessment, sex, genotyping array, PCs(1-15), cigarette pack-years, smoking status(never vs. former vs. current), body mass index | Agent Input |


### angina pectoris

Candidate pool: `19` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005059 | PGS005052 | PGS005051 | PGS005050 | PGS005054 | PGS001262 | PGS001262 | PGS000703 | Agent Input |
| AoU benchmark rank | 1/19 | 2/19 | 3/19 | 4/19 | 5/19 | 15/19 | 15/19 | 12/19 | Benchmark Only |
| AoU benchmark AUC | 0.5653 | 0.5637 | 0.5637 | 0.5633 | 0.5621 | 0.5305 | 0.5305 | 0.5407 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 5/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Angina pectoris (PheCode 411.3) | Angina pectoris (PheCode 411.3) | Angina pectoris (PheCode 411.3) | Angina pectoris (PheCode 411.3) | Angina pectoris (PheCode 411.3) | Vascular/heart problems diagnosed by doctor Angina | Vascular/heart problems diagnosed by doctor Angina | Angina | Agent Input |
| trait_efo | angina pectoris | angina pectoris | angina pectoris | angina pectoris | angina pectoris | angina pectoris | angina pectoris | angina pectoris | Agent Input |
| phenotyping_reported | Angina pectoris | Angina pectoris | Angina pectoris | Angina pectoris | Angina pectoris | Vascular/heart problems diagnosed by doctor Angina | Vascular/heart problems diagnosed by doctor Angina | Angina | Agent Input |
| method_name | prscsx | ldpred | ldpred | ldpred | prscs | snpnet | snpnet | snpnet (multi-PRS) | Agent Input |
| performance_metrics.selected_performance_id | PPM021831 | PPM021925 | PPM021924 | PPM021923 | PPM021830 | PPM008819 | PPM008819 | PPM001595 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 3 | 3 | 3 | 3 | 3 | 5 | 5 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | 0.5868 | 0.5868 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0130 | 0.0130 | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7644 | 0.7662 | 0.7655 | 0.7651 | 0.7656 | 0.8073 | 0.8073 | 0.5926 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | 0.1747 | 0.1747 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | 0.0098 | 0.0098 | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.764350008110945} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.766245446279245} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.765455879253035} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.765078012482153} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.765602593839864} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.80729, 'ci_lower': 0.79886, 'ci_upper': 0.81571} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.80729, 'ci_lower': 0.79886, 'ci_upper': 0.81571} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.592624176561804} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.17468} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.0098} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01304} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.58683, 'ci_lower': 0.57429, 'ci_upper': 0.59937} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.17468} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.0098} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01304} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.58683, 'ci_lower': 0.57429, 'ci_upper': 0.59937} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.412, 'ci_lower': 1.35, 'ci_upper': 1.48} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.491, 'ci_lower': 1.42, 'ci_upper': 1.57} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.455, 'ci_lower': 1.38, 'ci_upper': 1.53} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.445, 'ci_lower': 1.37, 'ci_upper': 1.52} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.43, 'ci_lower': 1.36, 'ci_upper': 1.5} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=30,750 | n=30,750 | n=30,750 | n=30,750 | n=30,750 | n=49,472 | n=49,472 | n=87,413 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | n=198,364 | n=198,364 | n=223,327 | Agent Input |
| ancestry_distribution | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MVP | MVP | MVP | MVP | MVP | UKB | UKB | UKB | Agent Input |
| publication.title | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Genetics of 35 blood and urine biomarkers in the UK Biobank. | Agent Input |
| publication.journal | HGG Adv | HGG Adv | HGG Adv | HGG Adv | HGG Adv | PLoS Genet | PLoS Genet | Nat Genet | Agent Input |
| date_release | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2021-10-21 | 2021-10-21 | 2021-02-03 | Agent Input |
| variants_number | 1273891 | 1286612 | 1286612 | 1286612 | 1273665 | 1852 | 1852 | 183692 | Agent Input |
| covariates | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Age, sex, PCs(1-10) | Agent Input |


### squamous cell carcinoma

Candidate pool: `18` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000463 | PGS005209 | PGS000467 | PGS000464 | PGS000461 | PGS000461 | PGS000731 | PGS000120 | Agent Input |
| AoU benchmark rank | 1/18 | 2/18 | 3/18 | 4/18 | 5/18 | 5/18 | 11/18 | 10/18 | Benchmark Only |
| AoU benchmark AUC | 0.5921 | 0.5901 | 0.5897 | 0.5858 | 0.5858 | 0.5858 | 0.5702 | 0.5779 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Squamous cell carcinoma | Squamous cell carcinoma | Squamous cell carcinoma | Squamous cell carcinoma | Squamous cell carcinoma | Squamous cell carcinoma | Squamous cell carcinoma | Squamous cell carcinoma | Agent Input |
| trait_efo | squamous cell carcinoma | squamous cell carcinoma | squamous cell carcinoma | squamous cell carcinoma | squamous cell carcinoma | squamous cell carcinoma | squamous cell carcinoma | squamous cell carcinoma | Agent Input |
| phenotyping_reported | Squamous cell carcinoma | Risk of squamous cell carcinoma in childhood cancer survivors | Squamous cell carcinoma | Squamous cell carcinoma | Squamous cell carcinoma | Squamous cell carcinoma | Squamous cell carcinoma | Squamous cell carcinoma | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Genome-wide significant SNPs | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | GWAS Hits | GWAS Hits | RiskPipe (clumping and thresholding) | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM001148 | PPM022588 | PPM001152 | PPM001149 | PPM001146 | PPM001146 | PPM001671 | PPM000340 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5930 | N/A | 0.5830 | 0.5750 | 0.5990 | 0.5990 | 0.6050 | 0.5900 | Agent Input |
| performance_metrics.full_model_r2 | 0.0268 | N/A | 0.0261 | 0.0147 | 0.0304 | 0.0304 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.593, 'ci_lower': 0.573, 'ci_upper': 0.613} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.583, 'ci_lower': 0.564, 'ci_upper': 0.603} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.575, 'ci_lower': 0.567, 'ci_upper': 0.582} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.599, 'ci_lower': 0.579, 'ci_upper': 0.618} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.599, 'ci_lower': 0.579, 'ci_upper': 0.618} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.605} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59, 'ci_lower': 0.56, 'ci_upper': 0.61} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0268} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0977} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.74, 'ci_lower': 2.46, 'ci_upper': 5.68} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0261} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0978} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.75, 'ci_lower': 2.49, 'ci_upper': 5.64} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0147} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.082} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.19, 'ci_lower': 1.79, 'ci_upper': 2.67} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0304} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0974} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.51, 'ci_lower': 2.29, 'ci_upper': 5.39} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0304} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0974} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.51, 'ci_lower': 2.29, 'ci_upper': 5.39} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.448, 'ci_lower': 1.356, 'ci_upper': 1.546} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.37, 'se': 0.0335} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.2, 'ci_lower': 1.0, 'ci_upper': 1.44} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.43, 'ci_lower': 1.341, 'ci_upper': 1.525} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.358, 'se': 0.0328} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.332, 'ci_lower': 1.296, 'ci_upper': 1.369} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.287, 'se': 0.014} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.491, 'ci_lower': 1.395, 'ci_upper': 1.593} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.4, 'se': 0.0338} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.491, 'ci_lower': 1.395, 'ci_upper': 1.593} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.4, 'se': 0.0338} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.44, 'ci_lower': 1.41, 'ci_upper': 1.48} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.4, 'ci_lower': 1.31, 'ci_upper': 1.5} | Agent Input |
| validation_sample_size | n=8,473 | n=11,220 | n=8,473 | n=60,018 | n=8,473 | n=8,473 | n=88,924 | n=20,468 | Agent Input |
| samples_training | n=8,029 | N/A | n=8,029 | n=61,038 | n=8,029 | n=8,029 | N/A | n=10,234 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MGI | N/A | MGI | UKB | MGI | MGI | 23andMe | MGI | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Polygenic risk scores, radiation treatment exposures and subsequent cancer risk in childhood cancer survivors. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Disease risk scores for skin cancers. | Exploring various polygenic risk scores for skin cancer in the phenomes of the Michigan genomics initiative and the UK Biobank with a visual catalog: PRSWeb. | Agent Input |
| publication.journal | Am J Hum Genet | Nat Med | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Nat Commun | PLoS Genet | Agent Input |
| date_release | 2020-12-15 | 2025-05-20 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2021-02-23 | 2020-03-27 | Agent Input |
| variants_number | 7 | 20 | 6 | 14 | 13 | 13 | 14 | 10 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | childhood cancer diagnosis, ancestry, age at childhood cancer diagnosis, radiation dose to the body region of the second cancer and chemotherapy exposure | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Unknown | age, sex, batch, PC1-4 | Agent Input |


### uterine cancer

Candidate pool: `18` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000075 | PGS000786 | PGS003381 | PGS002300 | PGS000542 | PGS003381 | PGS000541 | PGS000073 | Agent Input |
| AoU benchmark rank | 1/18 | 2/18 | 3/18 | 4/18 | 5/18 | 3/18 | 7/18 | 18/18 | Benchmark Only |
| AoU benchmark AUC | 0.6120 | 0.6113 | 0.5970 | 0.5728 | 0.5680 | 0.5970 | 0.5571 | 0.4138 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | 10/10 trials | 9/10 trials | Benchmark Only |
| trait_reported | Endometrial cancer | Endometrial cancer | Uterine endometrial carcinoma | Endometrial cancer | Malignant neoplasm of uterus | Uterine endometrial carcinoma | Malignant neoplasm of uterus | Cervical cancer | Agent Input |
| trait_efo | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial cancer | uterine cancer | endometrial carcinoma | uterine cancer | cervical carcinoma | Agent Input |
| phenotyping_reported | Incident endometrial cancer | Incident endometrial cancer | uterine endometrial carcinoma | Endometrial cancer | Malignant neoplasm of uterus | uterine endometrial carcinoma | Malignant neoplasm of uterus | Incident cervical cancer | Agent Input |
| method_name | Genome-wide significant variants | 9 variants from Graff et al (PGS000075) with inverse variant weights | lassosum | Genome-wide significant variants | Pruning and Thresholding (P+T) | lassosum | GWAS Hits | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM002041 | PPM002057 | PPM016256 | PPM013029 | PPM001227 | PPM016256 | PPM001226 | PPM002039 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 3 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7550 | 0.7540 | 0.7610 | 0.6400 | 0.5720 | 0.7610 | 0.5760 | 0.7450 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.4860 | 0.1100 | N/A | 0.0126 | 0.1100 | 0.0133 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.755} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.754} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.761} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64, 'ci_lower': 0.61, 'ci_upper': 0.67} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.572, 'ci_lower': 0.549, 'ci_upper': 0.596} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.761} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.576, 'ci_lower': 0.553, 'ci_upper': 0.6} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75, 'se': 0.017} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.486} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0126} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.082} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.6, 'ci_lower': 1.5, 'ci_upper': 4.51} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0133} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.082} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.12, 'ci_lower': 1.17, 'ci_upper': 3.84} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.19, 'ci_lower': 1.1, 'ci_upper': 1.29} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.18, 'ci_lower': 1.09, 'ci_upper': 1.27} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.302, 'ci_lower': 1.2, 'ci_upper': 1.413} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.264, 'se': 0.0416} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.311, 'ci_lower': 1.209, 'ci_upper': 1.422} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.271, 'se': 0.0415} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.09, 'ci_upper': 1.37} | Agent Input |
| validation_sample_size | n=212,156 | n=212,156 | n=144,479 | n=629 | n=6,987 | n=144,479 | n=6,987 | n=211,795 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=7,131 | N/A | n=7,131 | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | ANECS B58C CoRGI E2C2 HCS NBBS NSECG QIMR SEARCH WTCCC | N/A | N/A | UKB | N/A | UKB | TwinGene | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Evaluating polygenic risk scores in assessing risk of nine solid and hematologic cancers in European descendants. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Cancer Res | Int J Cancer | Am J Hum Genet | Cancer Res | Am J Hum Genet | Nat Commun | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2023-01-19 | 2022-06-09 | 2020-12-15 | 2023-01-19 | 2020-12-15 | 2020-02-12 | Agent Input |
| variants_number | 9 | 9 | 529365 | 19 | 20 | 529365 | 18 | 10 | Agent Input |
| covariates | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | age, top 20 genetic principal components | Unknown | age, sex, batch PCs 1-4 | age, top 20 genetic principal components | age, sex, batch PCs 1-4 | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Agent Input |


### retinopathy

Candidate pool: `17` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004952 | PGS002269 | PGS004606 | PGS001834 | PGS002041 | PGS002027 | PGS002027 | PGS000819 | Agent Input |
| AoU benchmark rank | 1/11 | 2/11 | 3/11 | 4/11 | 5/11 | 9/11 | 9/11 | 10/11 | Benchmark Only |
| AoU benchmark AUC | 0.6375 | 0.6244 | 0.6171 | 0.5967 | 0.5966 | 0.5105 | 0.5105 | 0.5050 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 8/10 trials | 8/10 trials | 9/10 trials | Benchmark Only |
| trait_reported | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | Diabetic retinopathy | Diabetic retinopathy | Diabetic retinopathy | Agent Input |
| trait_efo | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | diabetic retinopathy | diabetic retinopathy | diabetic retinopathy | Agent Input |
| phenotyping_reported | Late age-related macular degeneration (Clinical Classification) | Rentinal layer thickness (photoreceptor inner and outer segments) | Age-related macular degeneration | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | Diabetic retinopathy | Diabetic retinopathy | Diabetic retinopathy in individuals with type 2 diabetes | Agent Input |
| method_name | Genome-wide significant SNPs | Independent variants associated with AMD | PRS-CS | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | LDpred2 (bigsnpr) | LDpred2 (bigsnpr) | LDpred | Agent Input |
| performance_metrics.selected_performance_id | PPM021761 | PPM012920 | PPM020767 | PPM009564 | PPM011194 | PPM011090 | PPM011090 | PPM002185 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European, South Asian, Not reported | European | European | European | European | European | European, African American or Afro-Caribbean, Hispanic or Latin American, Asian unspecified, Native American, NR | Agent Input |
| performance_metrics.record_count | 6 | 3 | 1 | 8 | 8 | 8 | 8 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8420 | N/A | 0.7100 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 84.2} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0175, 'ci_lower': 0.0034, 'ci_upper': 0.0315} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0159, 'ci_lower': 0.0018, 'ci_upper': 0.0299} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0451, 'ci_lower': 0.031, 'ci_upper': 0.0592} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0451, 'ci_lower': 0.031, 'ci_upper': 0.0592} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.41, 'ci_lower': 1.32, 'ci_upper': 1.5} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': -0.21, 'ci_lower': -0.23, 'ci_upper': -0.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.12, 'ci_lower': 1.04, 'ci_upper': 1.2} | Agent Input |
| validation_sample_size | n=1,232 | n=44,823 | n=163,011 | n=19,413 | n=19,413 | n=19,330 | n=19,330 | n=6,079 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=391,124 | n=391,124 | n=391,124 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: AFR (33%), EUR (33%), MAE (33%) | Agent Input |
| training_development_cohorts | IAMDGC | AREDS BDES CWRU Columbia EUGENDA Edinburgh JHU MMAP Marshfield NHS RotES UCSD UWALF Vanderbilt | IAMDGC | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Genetic Risk Score Analysis Supports a Joint View of Two Classification Systems for Age-Related Macular Degeneration. | Photoreceptor Layer Thinning Is an Early Biomarker for Age-Related Macular Degeneration: Epidemiologic and Genetic Evidence from UK Biobank OCT Data. | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Genome-wide polygenic risk score for retinopathy of type 2 diabetes. | Agent Input |
| publication.journal | Invest Ophthalmol Vis Sci | Ophthalmology | Nat Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Hum Mol Genet | Agent Input |
| date_release | 2024-09-19 | 2022-04-01 | 2024-02-20 | 2022-01-10 | 2022-01-10 | 2022-01-10 | 2022-01-10 | 2021-07-29 | Agent Input |
| variants_number | 52 | 47 | 1000946 | 157 | 116538 | 389029 | 389029 | 3537914 | Agent Input |
| covariates | Age, sex, survey membership, 10 PCs | Age, age2 (to adjust for non-linear relationships with age), sex, smoking status, and the first ten principal components of genetic ancestry | age, sex, principal components 1-10 | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | Agent Input |


### glaucoma

Candidate pool: `15` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002761 | PGS004765 | PGS004766 | PGS004944 | PGS001792 | PGS000137 | PGS000137 | PGS000137 | Agent Input |
| AoU benchmark rank | 1/15 | 2/15 | 3/15 | 4/15 | 5/15 | 6/15 | 6/15 | 6/15 | Benchmark Only |
| AoU benchmark AUC | 0.6258 | 0.6215 | 0.6212 | 0.5989 | 0.5967 | 0.5959 | 0.5959 | 0.5959 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | 5/10 trials | 9/10 trials | Benchmark Only |
| trait_reported | Glaucoma | Glaucoma | Glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Glaucoma | Glaucoma | Glaucoma | Agent Input |
| trait_efo | glaucoma | glaucoma | glaucoma | open-angle glaucoma | glaucoma | glaucoma | glaucoma | glaucoma | Agent Input |
| phenotyping_reported | Glaucoma | Glaucoma | Glaucoma | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma | Primary open-angle glaucoma (POAG) | Primary open-angle glaucoma (POAG) | Primary open-angle glaucoma (POAG) | Agent Input |
| method_name | PRS-CS | PRSmix | PRSmixPlus | Lassosum | PRS-CS-auto | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM014961 | PPM020990 | PPM020991 | PPM021744 | PPM009296 | PPM000422 | PPM000422 | PPM000422 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | African unspecified, Hispanic or Latin American, East Asian, South Asian, European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 8 | 2 | 14 | 14 | 14 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0321 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.7480 | 0.7770 | 0.8000 | 0.8000 | 0.8000 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0310 | 0.0310 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.748} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.777} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.031, 'ci_lower': 0.024, 'ci_upper': 0.038} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.031, 'ci_lower': 0.024, 'ci_upper': 0.038} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.03209} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.68, 'ci_lower': 1.59, 'ci_upper': 1.78} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.74, 'ci_lower': 1.71, 'ci_upper': 1.77} | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=39,444 | n=9,462 | n=9,462 | n=407,667 | n=347,396 | n=1,795 | n=1,795 | n=1,795 | Agent Input |
| samples_training | N/A | n=37,851 | n=37,851 | N/A | N/A | n=8,004 | n=8,004 | n=8,004 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: AFR (2%), EAS (25%), EUR (72%), OTH (90%) / EVAL: ASN (50%), EUR (50%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (75%), MAE (12%), SAS (12%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (75%), MAE (12%), SAS (12%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (75%), MAE (12%), SAS (12%) | Agent Input |
| training_development_cohorts | N/A | AllofUs | AllofUs | N/A | BBJ BioMe TWB UCLA | ANZRAG | ANZRAG | ANZRAG | Agent Input |
| publication.title | Systematic comparison of family history and polygenic risk across 24 common diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Multitrait analysis of glaucoma identifies new risk loci and enables polygenic prediction of disease susceptibility and progression. | Multitrait analysis of glaucoma identifies new risk loci and enables polygenic prediction of disease susceptibility and progression. | Multitrait analysis of glaucoma identifies new risk loci and enables polygenic prediction of disease susceptibility and progression. | Agent Input |
| publication.journal | Am J Hum Genet | Cell Genom | Cell Genom | JAMA Ophthalmol | Cell Genom | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2022-11-07 | 2024-03-28 | 2024-03-28 | 2024-08-29 | 2022-09-08 | 2020-03-27 | 2020-03-27 | 2020-03-27 | Agent Input |
| variants_number | 1082518 | 835476 | 837948 | 144019 | 911402 | 2673 | 2673 | 2673 | Agent Input |
| covariates | age, sex, 10 PCs, technical covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | Age, age2, sex, ancestry | sex,age,age2,age*sex,age^2*sex, 20PCs | age, sex, self-reported family history | age, sex, self-reported family history | age, sex, self-reported family history | Agent Input |


### lupus erythematosus

Candidate pool: `13` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000771 | PGS000772 | PGS000803 | PGS004917 | PGS000196 | PGS002082 | PGS001870 | PGS000196 | Agent Input |
| AoU benchmark rank | 1/12 | 2/12 | 3/12 | 4/12 | 5/12 | 10/12 | 9/12 | 5/12 | Benchmark Only |
| AoU benchmark AUC | 0.6046 | 0.5961 | 0.5925 | 0.5817 | 0.5783 | 0.5633 | 0.5671 | 0.5783 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | 6/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Lupus (localized and systemic) | Lupus (localized and systemic) | Systemic lupus erythematosus | Agent Input |
| trait_efo | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | lupus erythematosus | lupus erythematosus | systemic lupus erythematosus | Agent Input |
| phenotyping_reported | Renal disease age of onset | Renal disease | Erythematous conditions | Systemic lupus erythematosus | Systemic lupus erythematosus diagnosis in patient with arthritis | Lupus (localized and systemic) | Lupus (localized and systemic) | Systemic lupus erythematosus diagnosis in patient with arthritis | Agent Input |
| method_name | Genome-wide significant variants | Genome-wide significant variants | Variants significantly associated with systemic lupus erythematosus | Clumping of genome-wide significant variants | Pruning and Thresholding (P+T) | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM001996 | PPM001997 | PPM002104 | PPM021383 | PPM000573 | PPM011517 | PPM009849 | PPM000573 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European, Not reported, European, Asian unspecified, African unspecified, Not reported | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 15 | 1 | 3 | 8 | 8 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5760 | N/A | N/A | 0.6960 | 0.7900 | N/A | N/A | 0.7900 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.576, 'ci_lower': 0.518, 'ci_upper': 0.634} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79, 'ci_lower': 0.72, 'ci_upper': 0.85} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79, 'ci_lower': 0.72, 'ci_upper': 0.85} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Odds Ratio (OR, top 20% vs bottom 20%)', 'name_short': 'Odds Ratio (OR, top 20% vs bottom 20%)', 'estimate': 1.578, 'ci_lower': 1.25, 'ci_upper': 1.991} | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0212, 'ci_lower': 0.0072, 'ci_upper': 0.0352} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0184, 'ci_lower': 0.0043, 'ci_upper': 0.0324} | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.28, 'ci_lower': 1.22, 'ci_upper': 1.34} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.246, 'se': 0.024} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.01, 'ci_lower': 1.83, 'ci_upper': 2.22} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.7, 'se': 0.05} | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=524 | n=3,101 | n=50,429 | n=3,945 | n=245 | n=19,585 | n=19,585 | n=245 | Agent Input |
| samples_training | n=10,995 | n=3,076 | N/A | N/A | N/A | n=391,124 | n=391,124 | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (2%), AMR (1%), EAS (32%), EUR (53%), MAE (9%), MAO (2%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), AMR (1%), EAS (32%), EUR (53%), MAE (9%), MAO (2%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (21%), EUR (79%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (67%), MAE (33%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: EUR (67%), MAE (33%) | Agent Input |
| training_development_cohorts | CCHMC GENYO Illumina_iControlDB UAB UCLA UCSF UMN USC WASHU WFSM | CCHMC GENYO Illumina_iControlDB UAB UCLA UCSF UMN USC WASHU WFSM | N/A | N/A | N/A | UKB | UKB | N/A | Agent Input |
| publication.title | Genome-wide assessment of genetic risk for systemic lupus erythematosus and disease severity. | Genome-wide assessment of genetic risk for systemic lupus erythematosus and disease severity. | Pleiotropy of systemic lupus erythematosus risk alleles and cardiometabolic disorders: A phenome-wide association study and inverse-variance weighted meta-analysis. | Interactions Between Genome-Wide Genetic Factors and Smoking Influencing Risk of Systemic Lupus Erythematosus. | Using genetics to prioritize diagnoses for rheumatology outpatients with inflammatory arthritis. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Using genetics to prioritize diagnoses for rheumatology outpatients with inflammatory arthritis. | Agent Input |
| publication.journal | Hum Mol Genet | Hum Mol Genet | Lupus | Arthritis Rheumatol | Sci Transl Med | Am J Hum Genet | Am J Hum Genet | Sci Transl Med | Agent Input |
| date_release | 2021-05-28 | 2021-05-28 | 2021-06-11 | 2024-06-12 | 2020-06-03 | 2022-01-10 | 2022-01-10 | 2020-06-03 | Agent Input |
| variants_number | 95 | 95 | 41 | 97 | 55 | 361553 | 87 | 55 | Agent Input |
| covariates | Unknown | Unknown | PCs(1-5), median age in the electronic health record, sex | Unknown | Unknown | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | Agent Input |


### lymphoid leukemia

Candidate pool: `13` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000874 | PGS000648 | PGS002305 | PGS000788 | PGS003453 | PGS000077 | PGS000788 | PGS000077 | Agent Input |
| AoU benchmark rank | 1/13 | 2/13 | 3/13 | 4/13 | 5/13 | 9/13 | 4/13 | 9/13 | Benchmark Only |
| AoU benchmark AUC | 0.6645 | 0.6555 | 0.6537 | 0.6479 | 0.6364 | 0.6159 | 0.6479 | 0.6159 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 7/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Chronic lymphoid leukemia | Lymphocytic leukemia | Chronic lymphocytic leukemia | Lymphocytic leukemia | Lymphocytic leukemia | Lymphocytic leukemia | Agent Input |
| trait_efo | chronic lymphocytic leukemia | chronic lymphocytic leukemia | lymphoid leukemia | lymphoid leukemia | chronic lymphocytic leukemia | lymphoid leukemia | lymphoid leukemia | lymphoid leukemia | Agent Input |
| phenotyping_reported | Chronic lymphocytic leukemia in individuals with a family history of hematological cancers | Lymphoid leukemia, chronic | Chronic lymphoid leukemia | Incident Lymphocytic Leukemia | Chronic lymphocytic leukemia | Incident Lymphocytic Leukemia | Incident Lymphocytic Leukemia | Incident Lymphocytic Leukemia | Agent Input |
| method_name | Representative SNPs from chronic lymphocytic leukemia susceptibility loci | Pruning and Thresholding (P+T) | Genome-wide significant variants | 75 variants from Graff et al (PGS000077) with inverse variant weights | Genome-wide significant SNPs | Genome-wide significant variants | 75 variants from Graff et al (PGS000077) with inverse variant weights | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM002495 | PPM001333 | PPM013034 | PPM002059 | PPM017224 | PPM002043 | PPM002059 | PPM002043 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, NR | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 17 | 1 | 2 | 1 | 4 | 3 | 1 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8610 | 0.6960 | 0.5700 | 0.7380 | N/A | 0.7190 | 0.7380 | 0.7190 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.1020 | N/A | 0.4150 | N/A | N/A | 0.4150 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.861, 'ci_lower': 0.82, 'ci_upper': 0.9} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696, 'ci_lower': 0.621, 'ci_upper': 0.764} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.57, 'ci_lower': 0.54, 'ci_upper': 0.6} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.756, 'se': 0.015} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.719} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.735, 'se': 0.016} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.756, 'se': 0.015} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.719} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.735, 'se': 0.016} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.102} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0776} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 12.9, 'ci_lower': 4.45, 'ci_upper': 37.6} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.415} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.415} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 3.79, 'ci_lower': 2.44, 'ci_upper': 5.87} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.124, 'ci_lower': 1.648, 'ci_upper': 2.738} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.753, 'se': 0.13} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.7, 'ci_lower': 1.53, 'ci_upper': 1.88} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.17, 'ci_lower': 2.07, 'ci_upper': 2.28} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.45, 'ci_lower': 1.31, 'ci_upper': 1.61} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.7, 'ci_lower': 1.53, 'ci_upper': 1.88} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.45, 'ci_lower': 1.31, 'ci_upper': 1.61} | Agent Input |
| validation_sample_size | n=3,958 | n=756 | n=265 | n=391,338 | n=20,134 | n=391,338 | n=391,338 | n=391,338 | Agent Input |
| samples_training | N/A | n=730 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: NR (50%), AFR (12%), EUR (25%), MAE (12%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (6%), AFR (4%), AMR (8%), EUR (79%), MAO (3%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (4%), AMR (9%), EUR (84%), MAO (3%) / EVAL: EUR (100%) | GWAS: NR (6%), AFR (4%), AMR (8%), EUR (79%), MAO (3%) / EVAL: EUR (100%) | GWAS: AFR (4%), AMR (9%), EUR (84%), MAO (3%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ATBC BCCA CPSII ENGELA EPIC EpiLymph HPFS Italian_GxE MAYO MCCS MSKCC NCI-SEER NHS NSW NYU-WHS PLCO SCALE UCSF UCSF2 UK-CLL UTAH Yale | MGI | ATBC BCCA CPSII ENGELA EPIC EpiLymph HPFS Italian_GxE MAYO MCCS MSKCC NCI-SEER NHS NSW NYU-WHS PLCO SCALE UCSF UCSF2 UK-CLL UTAH Yale | ATBC B58C BCAC BCCA BFM COG CPSII DISCOVeRY-BMT ELCCS ENGELA EPIC ESCALE EpiLymph GAIN GMMG HNR HPFS Iowa-Mayo Italian_GxE KIEL MAYO MCCS MESA MRC MSKCC NCI-SEER NHS NICR NSW NYU-WHS PLCO PRACTICAL SCALE SJCRH UCSF UCSF2 UK-CLL UKBS UKCCS UTAH WHI WTCCC Yale | N/A | B58C COG GAIN MESA SJCRH UK-CLL WTCCC | ATBC B58C BCAC BCCA BFM COG CPSII DISCOVeRY-BMT ELCCS ENGELA EPIC ESCALE EpiLymph GAIN GMMG HNR HPFS Iowa-Mayo Italian_GxE KIEL MAYO MCCS MESA MRC MSKCC NCI-SEER NHS NICR NSW NYU-WHS PLCO PRACTICAL SCALE SJCRH UCSF UCSF2 UK-CLL UKBS UKCCS UTAH WHI WTCCC Yale | B58C COG GAIN MESA SJCRH UK-CLL WTCCC | Agent Input |
| publication.title | Association of polygenic risk score with the risk of chronic lymphocytic leukemia and monoclonal B-cell lymphocytosis. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Evaluating polygenic risk scores in assessing risk of nine solid and hematologic cancers in European descendants. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Blood | Am J Hum Genet | Int J Cancer | Nat Commun | Leukemia | Nat Commun | Nat Commun | Nat Commun | Agent Input |
| date_release | 2021-08-26 | 2020-12-15 | 2022-06-09 | 2021-05-28 | 2023-03-24 | 2020-02-12 | 2021-05-28 | 2020-02-12 | Agent Input |
| variants_number | 41 | 44 | 43 | 75 | 43 | 75 | 75 | 75 | Agent Input |
| covariates | Age, sex, study, socioeconomic status (when available) | age, sex, batch PCs 1-4 | Unknown | Age at assessment, sex, genotyping array, PCs(1-15) | Unknown | Age at assessment, sex, genotyping array, PCs(1-15) | Age at assessment, sex, genotyping array, PCs(1-15) | Age at assessment, sex, genotyping array, PCs(1-15) | Agent Input |


### osteoporosis

Candidate pool: `13` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004810 | PGS004809 | PGS002768 | PGS001274 | PGS001273 | PGS002768 | PGS001273 | PGS001273 | Agent Input |
| AoU benchmark rank | 1/13 | 2/13 | 3/13 | 4/13 | 5/13 | 3/13 | 5/13 | 5/13 | Benchmark Only |
| AoU benchmark AUC | 0.5758 | 0.5742 | 0.5647 | 0.5628 | 0.5544 | 0.5647 | 0.5544 | 0.5544 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | 6/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Osteoporosis | Osteoporosis | Osteoporosis | Osteoporosis without pathological fracture (time-to-event) | Osteoporosis | Osteoporosis | Osteoporosis | Osteoporosis | Agent Input |
| trait_efo | osteoporosis | osteoporosis | osteoporosis, heel bone mineral density | osteoporosis | osteoporosis | osteoporosis, heel bone mineral density | osteoporosis | osteoporosis | Agent Input |
| phenotyping_reported | Osteoporosis | Osteoporosis | Osteoporosis | TTE osteoporosis without pathological fracture | Osteoporosis | Osteoporosis | Osteoporosis | Osteoporosis | Agent Input |
| method_name | PRSmixPlus | PRSmix | PRS-CS | snpnet | snpnet | PRS-CS | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM021035 | PPM021034 | PPM014968 | PPM008870 | PPM008865 | PPM014968 | PPM008865 | PPM008865 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 5 | 5 | 1 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.5759 | 0.5685 | N/A | 0.5685 | 0.5685 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0095 | 0.0069 | N/A | 0.0069 | 0.0069 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.7965 | 0.7897 | N/A | 0.7897 | 0.7897 | Agent Input |
| performance_metrics.full_model_r2 | 0.0220 | 0.0110 | N/A | 0.1570 | 0.1457 | N/A | 0.1457 | 0.1457 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | 0.0078 | 0.0048 | N/A | 0.0048 | 0.0048 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79652, 'ci_lower': 0.78363, 'ci_upper': 0.8094} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78972, 'ci_lower': 0.77584, 'ci_upper': 0.8036} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78972, 'ci_lower': 0.77584, 'ci_upper': 0.8036} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78972, 'ci_lower': 0.77584, 'ci_upper': 0.8036} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.022, 'ci_lower': 0.016, 'ci_upper': 0.028} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.011, 'ci_lower': 0.007, 'ci_upper': 0.015} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.15697} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00777} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00945} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57595, 'ci_lower': 0.55816, 'ci_upper': 0.59374} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.14567} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00477} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00688} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.5685, 'ci_lower': 0.55009, 'ci_upper': 0.58691} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.14567} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00477} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00688} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.5685, 'ci_lower': 0.55009, 'ci_upper': 0.58691} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.14567} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00477} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00688} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.5685, 'ci_lower': 0.55009, 'ci_upper': 0.58691} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.25, 'ci_upper': 1.38} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.25, 'ci_upper': 1.38} | N/A | N/A | Agent Input |
| validation_sample_size | n=9,462 | n=9,462 | n=39,444 | n=24,905 | n=24,905 | n=39,444 | n=24,905 | n=24,905 | Agent Input |
| samples_training | n=37,851 | n=37,851 | N/A | n=269,704 | n=269,704 | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs | AllofUs | N/A | UKB | UKB | N/A | UKB | UKB | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | Am J Hum Genet | PLoS Genet | PLoS Genet | Am J Hum Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2024-03-28 | 2024-03-28 | 2022-11-07 | 2021-10-21 | 2021-10-21 | 2022-11-07 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 1876917 | 863731 | 1091549 | 1270 | 316 | 1091549 | 316 | 316 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, 10 PCs, technical covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, 10 PCs, technical covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### testicular carcinoma

Candidate pool: `13` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000796 | PGS000600 | PGS001164 | PGS000599 | PGS000597 | PGS000604 | PGS001164 | PGS000595 | Agent Input |
| AoU benchmark rank | 1/12 | 2/12 | 3/12 | 4/12 | 5/12 | 9/12 | 3/12 | 12/12 | Benchmark Only |
| AoU benchmark AUC | 0.9212 | 0.9128 | 0.9044 | 0.9021 | 0.8730 | 0.7468 | 0.9044 | 0.4140 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Agent Input |
| trait_efo | testicular carcinoma, Testicular Germ Cell Tumor | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | Agent Input |
| phenotyping_reported | Incident testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Agent Input |
| method_name | 52 variants from Graff et al (PGS000086) with inverse variant weights | lassosum | snpnet | Pruning and Thresholding (P+T) | lassosum | Pruning and Thresholding (P+T) | snpnet | GWAS Hits | Agent Input |
| performance_metrics.selected_performance_id | PPM002067 | PPM001285 | PPM008544 | PPM001284 | PPM001282 | PPM001289 | PPM008544 | PPM001280 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 3 | 1 | 1 | 1 | 3 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6296 | N/A | N/A | N/A | 0.6296 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0157 | N/A | N/A | N/A | 0.0157 | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7870 | 0.6360 | 0.8391 | 0.6370 | 0.6560 | 0.7030 | 0.8391 | 0.6580 | Agent Input |
| performance_metrics.full_model_r2 | 0.6050 | 0.0460 | 0.1291 | 0.0473 | 0.0487 | 0.0882 | 0.1291 | 0.0543 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0313 | N/A | N/A | N/A | 0.0313 | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.787} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.766, 'se': 0.033} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.636, 'ci_lower': 0.565, 'ci_upper': 0.698} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.83915, 'ci_lower': 0.8185, 'ci_upper': 0.85981} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.637, 'ci_lower': 0.568, 'ci_upper': 0.703} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.656, 'ci_lower': 0.593, 'ci_upper': 0.717} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.703, 'ci_lower': 0.659, 'ci_upper': 0.745} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.83915, 'ci_lower': 0.8185, 'ci_upper': 0.85981} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.658, 'ci_lower': 0.594, 'ci_upper': 0.719} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.605} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.046} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0839} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 6.35, 'ci_lower': 1.81, 'ci_upper': 22.3} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1291} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03126} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01573} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62956, 'ci_lower': 0.58302, 'ci_upper': 0.67611} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0473} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0844} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.35, 'ci_lower': 1.08, 'ci_upper': 17.5} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0487} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.084} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.72, 'ci_lower': 0.568, 'ci_upper': 13.1} | {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0793} {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0882} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.6, 'ci_lower': 1.75, 'ci_upper': 12.1} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1291} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03126} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01573} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62956, 'ci_lower': 0.58302, 'ci_upper': 0.67611} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0543} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0838} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.64, 'ci_lower': 0.535, 'ci_upper': 13.0} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.26, 'ci_lower': 1.71, 'ci_upper': 2.99} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.619, 'ci_lower': 1.267, 'ci_upper': 2.067} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.482, 'se': 0.125} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.628, 'ci_lower': 1.281, 'ci_upper': 2.069} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.487, 'se': 0.122} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.667, 'ci_lower': 1.296, 'ci_upper': 2.143} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.511, 'se': 0.128} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.106, 'ci_lower': 1.729, 'ci_upper': 2.565} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.745, 'se': 0.101} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.713, 'ci_lower': 1.33, 'ci_upper': 2.206} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.538, 'se': 0.129} | Agent Input |
| validation_sample_size | n=179,537 | n=755 | n=67,425 | n=755 | n=755 | n=1,484 | n=67,425 | n=755 | Agent Input |
| samples_training | N/A | n=776 | n=269,704 | n=776 | n=776 | n=1,671 | n=269,704 | n=776 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | B58C BCAC FCCC NCI Penn PennCATH SEARCH Sweden UKBS UKGPCS UKTCC UPENN | MGI | UKB | MGI | MGI | UKB | UKB | MGI | Agent Input |
| publication.title | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | PLoS Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | PLoS Genet | Am J Hum Genet | Agent Input |
| date_release | 2021-05-28 | 2020-12-15 | 2021-10-21 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2021-10-21 | 2020-12-15 | Agent Input |
| variants_number | 52 | 250 | 280 | 31 | 771 | 44 | 280 | 9 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15) | age, sex, batch PCs 1-4 | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | Agent Input |


### parkinson disease

Candidate pool: `11` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000903 | PGS004924 | PGS000902 | PGS000750 | PGS003763 | PGS000903 | PGS000903 | PGS000056 | Agent Input |
| AoU benchmark rank | 1/11 | 2/11 | 3/11 | 4/11 | 5/11 | 1/11 | 1/11 | 7/11 | Benchmark Only |
| AoU benchmark AUC | 0.5616 | 0.5523 | 0.5500 | 0.5430 | 0.5421 | 0.5616 | 0.5616 | 0.5254 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Agent Input |
| trait_efo | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Agent Input |
| phenotyping_reported | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Incident Parkinson Disease | Parkinson's disease | Parkinson's disease | Cognitive decline (time to MMSE 4-point decrease) | Agent Input |
| method_name | Clumping and Thresholding (C+T) | Genome-wide significant SNPs | Genome-wide significant variants | Genome-wide significant variants | Genome-wide significant SNPs | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM002664 | PPM021702 | PPM002665 | PPM001904 | PPM018563 | PPM002664 | PPM002664 | PPM000141 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, NR | European, African unspecified, Not reported | European, NR | European, NR | European | European, NR | European, NR | European | Agent Input |
| performance_metrics.record_count | 5 | 2 | 6 | 3 | 2 | 5 | 5 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6920 | N/A | 0.6510 | 0.7030 | N/A | 0.6920 | 0.6920 | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0540 | N/A | N/A | N/A | N/A | 0.0540 | 0.0540 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.692} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.651, 'ci_lower': 0.617, 'ci_upper': 0.684} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.703, 'ci_lower': 0.698, 'ci_upper': 0.708} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.692} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.692} | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.054} {'name_long': 'Odds Ratio (OR, top 25% vs bottom 25%)', 'name_short': 'Odds Ratio (OR, top 25% vs bottom 25%)', 'estimate': 6.25, 'ci_lower': 4.26, 'ci_upper': 9.28} | {'name_long': 'Odds ratio (OR, top vs bottom PGS quartile)', 'name_short': 'Odds ratio (OR, top vs bottom PGS quartile)', 'estimate': 3.79, 'ci_lower': 1.64, 'ci_upper': 8.73} | N/A | N/A | {'name_long': 'Hazard ratio (HR, high vs low tertile)', 'name_short': 'Hazard ratio (HR, high vs low tertile)', 'estimate': 1.72, 'ci_lower': 1.54, 'ci_upper': 1.93} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.054} {'name_long': 'Odds Ratio (OR, top 25% vs bottom 25%)', 'name_short': 'Odds Ratio (OR, top 25% vs bottom 25%)', 'estimate': 6.25, 'ci_lower': 4.26, 'ci_upper': 9.28} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.054} {'name_long': 'Odds Ratio (OR, top 25% vs bottom 25%)', 'name_short': 'Odds Ratio (OR, top 25% vs bottom 25%)', 'estimate': 6.25, 'ci_lower': 4.26, 'ci_upper': 9.28} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.709, 'se': 0.072} | N/A | N/A | N/A | N/A | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.709, 'se': 0.072} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.709, 'se': 0.072} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.44, 'ci_lower': 1.0, 'ci_upper': 2.07} | Agent Input |
| validation_sample_size | n=999 | n=3,482 | n=999 | n=486 | n=314,998 | n=999 | n=999 | n=285 | Agent Input |
| samples_training | n=1,473,098 | N/A | n=1,473,098 | N/A | N/A | n=1,473,098 | n=1,473,098 | N/A | Agent Input |
| ancestry_distribution | GWAS: MAE (100%) / DEV: MAE (100%) / EVAL: EUR (33%), MAE (33%), SAS (33%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: MAE (100%) / DEV: MAE (100%) / EVAL: NR (40%), MAE (60%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / DEV: MAE (100%) / EVAL: EUR (33%), MAE (33%), SAS (33%) | GWAS: MAE (100%) / DEV: MAE (100%) / EVAL: EUR (33%), MAE (33%), SAS (33%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | 23andMe HBS IPDGC PDBP PPMI UKB | N/A | 23andMe HBS IPDGC PDBP PPMI UKB | N/A | N/A | 23andMe HBS IPDGC PDBP PPMI UKB | 23andMe HBS IPDGC PDBP PPMI UKB | N/A | Agent Input |
| publication.title | Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. | Polygenic risk score for Parkinson's disease and olfaction among middle-aged to older women. | Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. | Excess of singleton loss-of-function variants in Parkinson's disease contributes to genetic risk. | Physical Frailty, Genetic Predisposition, and Incident Parkinson Disease. | Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. | Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. | Association of Polygenic Risk Score With Cognitive Decline and Motor Progression in Parkinson Disease. | Agent Input |
| publication.journal | Lancet Neurol | Parkinsonism Relat Disord | Lancet Neurol | J Med Genet | JAMA Neurol | Lancet Neurol | Lancet Neurol | JAMA Neurol | Agent Input |
| date_release | 2021-09-17 | 2024-07-31 | 2021-09-17 | 2021-03-22 | 2023-08-04 | 2021-09-17 | 2021-09-17 | 2019-12-18 | Agent Input |
| variants_number | 1805 | 90 | 90 | 43 | 44 | 1805 | 1805 | 23 | Agent Input |
| covariates | PCs(1-5), age, sex | Age, race, 5 PCs, self-reported sense of smell, education, smoking status, self-reported health status, and PM2.5 and NO2 in 2006 | PCs(1-5), age, sex | Sex, singleton loss of function variant count, Parkinson's disease family history. | genotyping array and the first 10 principal components of ancestry | PCs(1-5), age, sex | PCs(1-5), age, sex | sex, age at diagnosis | Agent Input |


### chronic obstructive pulmonary disease

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001783 | PGS004536 | PGS001788 | PGS002062 | PGS004466 | PGS001783 | PGS001783 | PGS001326 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 1/10 | 1/10 | 10/10 | Benchmark Only |
| AoU benchmark AUC | 0.6057 | 0.5966 | 0.5913 | 0.5764 | 0.5652 | 0.6057 | 0.6057 | 0.5113 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 8/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Chronic obstructive pulmonary disease | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Chronic airway obstruction | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Chronic obstructive pulmonary disease | Emphysema | Agent Input |
| trait_efo | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | emphysema | Agent Input |
| phenotyping_reported | Chronic obstructive pulmonary disease | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Chronic airway obstruction | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Chronic obstructive pulmonary disease | Emphysema | Agent Input |
| method_name | PRS-CS-auto | RFDiseasemetaPRS | PRS-CS-auto | LDpred2 (bigsnpr) | LDpred2 | PRS-CS-auto | PRS-CS-auto | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM009312 | PPM020651 | PPM009292 | PPM011358 | PPM020581 | PPM009312 | PPM009312 | PPM009121 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 8 | 1 | 1 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0.5691 | Agent Input |
| performance_metrics.r2 | 0.0381 | N/A | 0.0163 | N/A | N/A | 0.0381 | 0.0381 | 0.0053 | Agent Input |
| performance_metrics.full_model_auc | 0.7400 | N/A | 0.7150 | N/A | N/A | 0.7400 | 0.7400 | 0.7280 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0.0584 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0.0055 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.715} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.72797, 'ci_lower': 0.70437, 'ci_upper': 0.75156} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.038092} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.0163} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.047, 'ci_lower': 0.0327, 'ci_upper': 0.0613} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.038092} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.038092} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05838} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00547} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00531} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.56911, 'ci_lower': 0.54137, 'ci_upper': 0.59684} | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.487584} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.30838779665344} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=7,128 | n=56,192 | n=337,168 | n=18,735 | n=56,192 | n=7,128 | n=7,128 | n=67,425 | Agent Input |
| samples_training | N/A | n=174,489 | N/A | n=391,124 | n=174,489 | N/A | N/A | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: AFR (2%), ASN (2%), EAS (24%), EUR (72%), OTH (1%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (33%), EUR (61%), OTH (2%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (24%), EUR (72%), OTH (1%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (24%), EUR (72%), OTH (1%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI QSKIN TWB UCLA UKB deCODE | UKB | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI QSKIN TWB UCLA deCODE | UKB | UKB | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI QSKIN TWB UCLA UKB deCODE | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI QSKIN TWB UCLA UKB deCODE | UKB | Agent Input |
| publication.title | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Cell Genom | Commun Biol | Cell Genom | Am J Hum Genet | Commun Biol | Cell Genom | Cell Genom | PLoS Genet | Agent Input |
| date_release | 2022-09-08 | 2024-03-18 | 2022-09-08 | 2022-01-10 | 2024-03-18 | 2022-09-08 | 2022-09-08 | 2021-10-21 | Agent Input |
| variants_number | 884139 | 1059939 | 910082 | 811003 | 1059939 | 884139 | 884139 | 42 | Agent Input |
| covariates | sex,age, 20PCs | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | sex,age, 20PCs | sex,age, 20PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### kidney cancer

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS004245 | PGS000722 | PGS003744 | PGS000787 | PGS004908 | PGS004908 | PGS000076 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 1/10 | 1/10 | 7/10 | Benchmark Only |
| AoU benchmark AUC | 0.5841 | 0.5524 | 0.5513 | 0.5466 | 0.5456 | 0.5841 | 0.5841 | 0.5399 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Renal cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| trait_efo | renal carcinoma | renal cell carcinoma | renal carcinoma | renal carcinoma | renal cell carcinoma | renal carcinoma | renal carcinoma | renal cell carcinoma | Agent Input |
| phenotyping_reported | Kidney cancer | Kidney cancer | Incident kidney cancer | Renal cancer | Incident kidney cancer | Kidney cancer | Kidney cancer | Incident kidney cancer | Agent Input |
| method_name | Genome-wide significant SNPs | PRSice-2 | Genome-wide significant variants | Genome-wide significant SNPs | 19 variants from Graff et al (PGS000076) with inverse variant weights | Genome-wide significant SNPs | Genome-wide significant SNPs | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM021361 | PPM020302 | PPM001652 | PPM018500 | PPM002058 | PPM021361 | PPM021361 | PPM002042 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 2 | 1 | 1 | 1 | 2 | 2 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7400 | N/A | 0.5670 | N/A | 0.7220 | 0.7400 | 0.7400 | 0.7220 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.3660 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.567, 'ci_lower': 0.543, 'ci_upper': 0.591} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.723, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.724, 'se': 0.011} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.366} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.02, 'ci_upper': 1.45} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.24, 'ci_lower': 1.14, 'ci_upper': 1.35} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.15, 'ci_lower': 1.07, 'ci_upper': 1.24} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.08, 'ci_upper': 1.26} | Agent Input |
| validation_sample_size | n=324,805 | n=133,830 | n=400,812 | n=692 | n=391,610 | n=324,805 | n=324,805 | n=391,610 | Agent Input |
| samples_training | N/A | N/A | N/A | n=649 | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | N/A | AHS ASHRAM ATBC BioVU CEERCC CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC ICR Karolinska Leeds MCCS MDACCS MDARCCS Moscow NCI NHS PHS PLCO RMHT SEARCH SORCE Tromso UKBS USKC Umea VARI VITAL WHI WHS WTCCC conFIRM deCODE | UKB | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | BBJ FinnGen NCI | BBJ FinnGen NCI | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Prognostic evaluation of polygenic risk score underlying pan-cancer analysis: evidence from two large-scale cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Nat Genet | NPJ Precis Oncol | JNCI Cancer Spectr | EBioMedicine | Nat Commun | Nat Genet | Nat Genet | Nat Commun | Agent Input |
| date_release | 2024-05-22 | 2023-12-15 | 2021-02-03 | 2023-06-01 | 2021-05-28 | 2024-05-22 | 2024-05-22 | 2020-02-12 | Agent Input |
| variants_number | 107 | 12 | 15 | 14 | 19 | 107 | 107 | 19 | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | first 10 genetic principal components | Genotyping array | Unknown | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Agent Input |


### obesity

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005235 | PGS005154 | PGS003959 | PGS002033 | PGS005145 | PGS001298 | PGS001298 | PGS001298 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 8/10 | 8/10 | 8/10 | Benchmark Only |
| AoU benchmark AUC | 0.6479 | 0.6331 | 0.5909 | 0.5833 | 0.5771 | 0.5605 | 0.5605 | 0.5605 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 5/10 trials | 9/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Adiposity | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | Obesity (time-to-event) | Obesity (time-to-event) | Obesity (time-to-event) | Agent Input |
| trait_efo | obesity | obesity | obesity | obesity, overweight body mass index status, overnutrition | obesity | obesity | obesity | obesity | Agent Input |
| phenotyping_reported | Obesity (phecode: 278.1) | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | TTE obesity | TTE obesity | TTE obesity | Agent Input |
| method_name | LDpred2-auto | CT-SLEB | Genome-wide significant SNPs | LDpred2 (bigsnpr) | PRS-CS | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM022667 | PPM022374 | PPM019107 | PPM011135 | PPM022365 | PPM008991 | PPM008991 | PPM008991 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | East Asian | European, Not reported | European | East Asian | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 7 | 8 | 1 | 5 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | 0.5757 | 0.5757 | 0.5757 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0115 | 0.0115 | 0.0115 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | 0.5956 | 0.5956 | 0.5956 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | 0.0181 | 0.0181 | 0.0181 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | 0.0336 | 0.0336 | 0.0336 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59555, 'ci_lower': 0.58697, 'ci_upper': 0.60413} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59555, 'ci_lower': 0.58697, 'ci_upper': 0.60413} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59555, 'ci_lower': 0.58697, 'ci_upper': 0.60413} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0789, 'ci_lower': 0.0651, 'ci_upper': 0.0927} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01814} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03355} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57573, 'ci_lower': 0.56713, 'ci_upper': 0.58434} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01814} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03355} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57573, 'ci_lower': 0.56713, 'ci_upper': 0.58434} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01814} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03355} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57573, 'ci_lower': 0.56713, 'ci_upper': 0.58434} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.9704649488977} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 1.76187749677908} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.149, 'se': 0.028} | N/A | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 1.60817500694587} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=100,960 | n=58,688 | n=27,429 | n=20,000 | n=58,688 | n=67,425 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | N/A | n=269,704 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (19%), EUR (81%) / EVAL: EAS (100%) | GWAS: NR (33%), EUR (67%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EAS (100%) / EVAL: EAS (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | EGG GIANT UKB | BBJ | N/A | UKB | BBJ | UKB | UKB | UKB | Agent Input |
| publication.title | Modeling the genomic architecture of adiposity and anthropometrics across the lifespan. | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | The sulfur microbial diet and increased risk of obesity: Findings from a population-based prospective cohort study. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Commun Biol | Clin Nutr | Am J Hum Genet | Commun Biol | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2025-10-06 | 2025-03-17 | 2023-10-17 | 2022-01-10 | 2025-03-17 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 709828 | 443124 | 940 | 846292 | 908466 | 9227 | 9227 | 9227 | Agent Input |
| covariates | age, sex, batch, and the first 10 genetic principal components | age, sex | Age, sex, race, centres, education, Townsend deprivation index, household income, smoking, alcohol consumption, physical activity, sleep pattern, energy intake, and BMI, WC or BF% at baseline | sex, age, birth date, deprivation index, 16 PCs | age, sex | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### ankylosing spondylitis

Candidate pool: `9` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001876 | PGS001267 | PGS001268 | PGS002089 | PGS003424 | PGS001267 | PGS001268 | PGS001267 | Agent Input |
| AoU benchmark rank | 1/9 | 2/9 | 3/9 | 4/9 | 5/9 | 2/9 | 3/9 | 2/9 | Benchmark Only |
| AoU benchmark AUC | 0.7415 | 0.7397 | 0.7362 | 0.7188 | 0.6491 | 0.7397 | 0.7362 | 0.7397 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 7/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis | Agent Input |
| trait_efo | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | Agent Input |
| phenotyping_reported | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Ankylosing spondylitis | Agent Input |
| method_name | Penalized regression (bigstatsr) | snpnet | snpnet | LDpred2 (bigsnpr) | LDpred2 | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM009896 | PPM008844 | PPM008849 | PPM011572 | PPM017077 | PPM008844 | PPM008849 | PPM008844 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | East Asian | European | European | European | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 1 | 5 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | 0.7265 | 0.7346 | N/A | N/A | 0.7265 | 0.7346 | 0.7265 | Agent Input |
| performance_metrics.r2 | N/A | 0.0988 | 0.1023 | N/A | N/A | 0.0988 | 0.1023 | 0.0988 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.7433 | 0.7488 | N/A | 0.7605 | 0.7433 | 0.7488 | 0.7433 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.1092 | 0.1150 | N/A | N/A | 0.1092 | 0.1150 | 0.1092 | Agent Input |
| performance_metrics.incremental_auc | N/A | 0.1299 | 0.1269 | N/A | N/A | 0.1299 | 0.1269 | 0.1299 | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74328, 'ci_lower': 0.70673, 'ci_upper': 0.77983} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7605} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74328, 'ci_lower': 0.70673, 'ci_upper': 0.77983} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74328, 'ci_lower': 0.70673, 'ci_upper': 0.77983} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0797, 'ci_lower': 0.0653, 'ci_upper': 0.0941} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.10925} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12994} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.09877} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.72651, 'ci_lower': 0.68965, 'ci_upper': 0.76337} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0919, 'ci_lower': 0.0775, 'ci_upper': 0.1063} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.10925} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12994} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.09877} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.72651, 'ci_lower': 0.68965, 'ci_upper': 0.76337} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.10925} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12994} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.09877} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.72651, 'ci_lower': 0.68965, 'ci_upper': 0.76337} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=18,262 | n=67,425 | n=67,425 | n=18,262 | n=1,298 | n=67,425 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=269,704 | n=269,704 | n=391,124 | N/A | n=269,704 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | GWAS: EAS (100%) / EVAL: EAS (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | N/A | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Genome-wide association study reveals ethnicity-specific SNPs associated with ankylosing spondylitis in the Taiwanese population. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | PLoS Genet | Am J Hum Genet | J Transl Med | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2022-01-10 | 2023-02-08 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 85 | 10 | 10 | 22026 | 100 | 10 | 10 | 10 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### aortic stenosis

Candidate pool: `8` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005254 | PGS005255 | PGS005256 | PGS004911 | PGS004910 | PGS005252 | PGS005252 | PGS000739 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | 8/8 | 8/8 | 7/8 | Benchmark Only |
| AoU benchmark AUC | 0.6375 | 0.6233 | 0.6228 | 0.5181 | 0.5166 | 0.3445 | 0.3445 | 0.4740 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Aortic stenosis | Mean pressure gradient | Peak aortic velocity | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Aortic stenosis | Aortic stenosis | Hypertrophic cardiomyopathy | Agent Input |
| trait_efo | aortic stenosis | aortic stenosis, aortic measurement | aortic stenosis, aortic measurement | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | aortic stenosis | aortic stenosis | hypertrophic cardiomyopathy | Agent Input |
| phenotyping_reported | incident aortic stenosis | incident aortic stenosis | incident aortic stenosis | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Incident aortic stenosis cases | Incident aortic stenosis cases | Hypertrophic cardiomyopathy | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | LDPred2 | LDPred2 | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM022737 | PPM022738 | PPM022739 | PPM021367 | PPM021366 | PPM022733 | PPM022733 | PPM018531 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 3 | 3 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.8000 | 0.7300 | 0.8700 | 0.8700 | 0.8210 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0480 | 0.0310 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.87} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.87} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.821, 'ci_lower': 0.772, 'ci_upper': 0.871} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.031} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.5} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.64, 'ci_lower': 1.5, 'ci_upper': 1.78} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.53, 'ci_lower': 1.4, 'ci_upper': 1.66} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.53, 'ci_lower': 1.41, 'ci_upper': 1.67} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.97} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.26} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.92} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.92} | N/A | Agent Input |
| validation_sample_size | n=244,450 | n=244,450 | n=244,450 | n=343,182 | n=343,182 | n=446,895 | n=446,895 | n=184,511 | Agent Input |
| samples_training | n=205,483 | n=98,645 | n=96,385 | N/A | N/A | n=47,691 | n=47,691 | n=47,737 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (3%), EAS (80%), EUR (90%), OTH (60%), SAS (4%) / DEV: MAE (100%) / EVAL: EUR (40%), MAE (60%) | Agent Input |
| training_development_cohorts | N/A | N/A | N/A | BRRD GEL HCMR RBH-CRB | BRRD GEL HCMR RBH-CRB | MGBB | MGBB | BRRD HCMR UKB | Agent Input |
| publication.title | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Genomic and transcriptomic analyses of aortic stenosis enhance therapeutic target discovery and disease prediction. | Genomic and transcriptomic analyses of aortic stenosis enhance therapeutic target discovery and disease prediction. | Common genetic variants and modifiable risk factors underpin hypertrophic cardiomyopathy susceptibility and expressivity. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2025-02-26 | 2025-02-26 | 2026-01-19 | 2026-01-19 | 2021-02-23 | Agent Input |
| variants_number | 1110912 | 1111632 | 1111632 | 374114 | 374190 | 1119377 | 1119377 | 27 | Agent Input |
| covariates | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | age, age^2, sex, PC1-10 | age, age^2, sex, PC1-10 | age, sex, genetic ancestry principal components 1-5, type 2 diabetes, hypertension, coronary artery disease, hyperlipidemia, body mass index, current smoking, renal failure. | age, sex, genetic ancestry principal components 1-5, type 2 diabetes, hypertension, coronary artery disease, hyperlipidemia, body mass index, current smoking, renal failure. | Clinical risk factors (obesity, HTN, AF, CAD), HCM-ACMG rare variant carrier status, age, sex, genotyping array, and PCs 1-5 | Agent Input |


### dilated cardiomyopathy

Candidate pool: `8` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004951 | PGS004949 | PGS004947 | PGS004862 | PGS004948 | PGS004951 | PGS004861 | PGS004861 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | 1/8 | 8/8 | 8/8 | Benchmark Only |
| AoU benchmark AUC | 0.6480 | 0.6463 | 0.6396 | 0.6344 | 0.6225 | 0.6480 | 0.6099 | 0.6099 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | 8/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy | Dilated cardiomyopathy | Agent Input |
| trait_efo | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | Agent Input |
| phenotyping_reported | Clinical dilated cardiomyopathy | Non-ischemic dilated cardiomyopathy | Non-ischemic dilated cardiomyopathy | Dilated cardiomyopathy | Non-ischemic dilated cardiomyopathy | Clinical dilated cardiomyopathy | Dilated cardiomyopathy | Dilated cardiomyopathy | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM021758 | PPM021756 | PPM021754 | PPM021093 | PPM021755 | PPM021758 | PPM021092 | PPM021092 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European, Not reported | European, Not reported | European | European, Not reported | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6700 | 0.6800 | 0.6600 | 0.7100 | 0.6400 | 0.6700 | 0.7000 | 0.7000 | Agent Input |
| performance_metrics.full_model_r2 | 0.1620 | 0.2160 | 0.2350 | 0.0500 | 0.1860 | 0.1620 | 0.0480 | 0.0480 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.124} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.076} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.162} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.101} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.67, 'ci_lower': 0.65, 'ci_upper': 0.69} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.2023} | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.06} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.029} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.216} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.095} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.68, 'ci_lower': 0.66, 'ci_upper': 0.69} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.0052} | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.068} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.028} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.235} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.076} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.66, 'ci_lower': 0.63, 'ci_upper': 0.68} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.0109} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05} | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.049} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.018} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.186} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.06} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.64, 'ci_lower': 0.62, 'ci_upper': 0.66} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.0042} | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.124} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.076} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.162} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.101} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.67, 'ci_lower': 0.65, 'ci_upper': 0.69} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.2023} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.93} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.66, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.91} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.65, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.73} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.55, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.64} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.49, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.93} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.66, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.56} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.56} | Agent Input |
| validation_sample_size | n=7,761 | n=326,106 | n=96,016 | n=347,585 | n=326,106 | n=7,761 | n=347,585 | n=347,585 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (46%), MAE (54%) / EVAL: EUR (100%) | GWAS: EUR (91%), MAE (9%) / EVAL: MAE (100%) | GWAS: EUR (48%), MAE (52%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (91%), MAE (9%) / EVAL: MAE (100%) | GWAS: EUR (46%), MAE (54%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | FinnGen MGBB UKB | AUMC_DCM FinnGen MGBB | AUMC_DCM FinnGen UKB | HERMES | AUMC_DCM FinnGen MGBB | FinnGen MGBB UKB | HERMES | HERMES | Agent Input |
| publication.title | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association analysis provides insights into the molecular etiology of dilated cardiomyopathy. | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association analysis provides insights into the molecular etiology of dilated cardiomyopathy. | Genome-wide association analysis provides insights into the molecular etiology of dilated cardiomyopathy. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2024-12-16 | 2024-12-16 | 2024-12-16 | 2024-04-18 | 2024-12-16 | 2024-12-16 | 2024-04-18 | 2024-04-18 | Agent Input |
| variants_number | 1075760 | 1038394 | 1072247 | 709534 | 1068761 | 1075760 | 713932 | 713932 | Agent Input |
| covariates | Sex, PC1-12 | Age, age^2, sex, array, PC1-12 | Age, age^2, sex, PC1-12 | age, age^2, sex, PC1-10 | Age, age^2, sex, array, PC1-12 | Sex, PC1-12 | age, age^2, sex, PC1-10 | age, age^2, sex, PC1-10 | Agent Input |


### hip osteoarthritis

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002763 | PGS004882 | PGS004478 | PGS000967 | PGS002750 | PGS002763 | PGS000967 | PGS000967 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 1/7 | 4/7 | 4/7 | Benchmark Only |
| AoU benchmark AUC | 0.5508 | 0.5496 | 0.5360 | 0.5307 | 0.5277 | 0.5508 | 0.5307 | 0.5307 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Hip osteoarthritis | Hip osteoarthritis | M16 (Coxarthrosis [arthrosis of hip]) | Coxarthrosis [arthrosis of hip] (time-to-event) | Total hip replacement | Hip osteoarthritis | Coxarthrosis [arthrosis of hip] (time-to-event) | Coxarthrosis [arthrosis of hip] (time-to-event) | Agent Input |
| trait_efo | osteoarthritis, hip | osteoarthritis, hip | osteoarthritis, hip | osteoarthritis, hip | total hip arthroplasty, osteoarthritis, hip | osteoarthritis, hip | osteoarthritis, hip | osteoarthritis, hip | Agent Input |
| phenotyping_reported | Hip osteoarthritis | Incident hip osteoarthritis | M16 (Coxarthrosis [arthrosis of hip]) | TTE coxarthrosis [arthrosis of hip] | Hip replacement | Hip osteoarthritis | TTE coxarthrosis [arthrosis of hip] | TTE coxarthrosis [arthrosis of hip] | Agent Input |
| method_name | PRS-CS | megaprs.auto | LDpred2 | snpnet | Genome-wide significant SNPs | PRS-CS | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM014963 | PPM021236 | PPM020593 | PPM007662 | PPM014940 | PPM014963 | PPM007662 | PPM007662 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 7 | 1 | 5 | 3 | 1 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.5611 | N/A | N/A | 0.5611 | 0.5611 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0063 | N/A | N/A | 0.0063 | 0.0063 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.6000 | N/A | 0.6905 | N/A | N/A | 0.6905 | 0.6905 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0625 | N/A | N/A | 0.0625 | 0.0625 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | 0.0092 | N/A | N/A | 0.0092 | 0.0092 | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.6, 'ci_lower': 0.6, 'ci_upper': 0.6} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69051, 'ci_lower': 0.68108, 'ci_upper': 0.69995} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69051, 'ci_lower': 0.68108, 'ci_upper': 0.69995} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69051, 'ci_lower': 0.68108, 'ci_upper': 0.69995} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.06247} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00918} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00628} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.5611, 'ci_lower': 0.55051, 'ci_upper': 0.57168} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.06247} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00918} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00628} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.5611, 'ci_lower': 0.55051, 'ci_upper': 0.57168} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.06247} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00918} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00628} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.5611, 'ci_lower': 0.55051, 'ci_upper': 0.57168} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.38, 'ci_lower': 1.31, 'ci_upper': 1.46} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.4, 'ci_lower': 1.38, 'ci_upper': 1.42} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.29594864200374} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.23, 'ci_lower': 1.16, 'ci_upper': 1.3} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.38, 'ci_lower': 1.31, 'ci_upper': 1.46} | N/A | N/A | Agent Input |
| validation_sample_size | n=39,444 | n=412,090 | n=56,192 | n=67,425 | n=1,257 | n=39,444 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | n=404 | n=174,489 | n=269,704 | N/A | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | N/A | 1000G | UKB | UKB | N/A | N/A | UKB | UKB | Agent Input |
| publication.title | Systematic comparison of family history and polygenic risk across 24 common diseases. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Genomic Risk Score for Advanced Osteoarthritis in Older Adults. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | Nat Commun | Commun Biol | PLoS Genet | Arthritis Rheumatol | Am J Hum Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-11-07 | 2024-06-27 | 2024-03-18 | 2021-10-21 | 2022-09-08 | 2022-11-07 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 1052273 | 773587 | 1059939 | 634 | 37 | 1052273 | 634 | 634 | Agent Input |
| covariates | age, sex, 10 PCs, technical covariates | PCs 1-10 | Unknown | age, sex, UKB array type, Genotype PCs | Age, sex, body mass index, education, and index of relative socioeconomic advantage and disadvantage | age, sex, 10 PCs, technical covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### hyperthyroidism

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005266 | PGS005265 | PGS005264 | PGS002023 | PGS001042 | PGS005265 | PGS001043 | PGS001042 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 2/7 | 7/7 | 5/7 | Benchmark Only |
| AoU benchmark AUC | 0.7677 | 0.7535 | 0.6667 | 0.6320 | 0.6290 | 0.7535 | 0.6154 | 0.6290 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Graves' disease | Graves' disease | Graves' disease | Thyrotoxicosis with or without goiter | Thyrotoxicosis [hyperthyroidism] (time-to-event) | Graves' disease | Hyperthyroidism, thyrotoxicosis | Thyrotoxicosis [hyperthyroidism] (time-to-event) | Agent Input |
| trait_efo | Graves disease | Graves disease | Graves disease | Thyrotoxicosis | Thyrotoxicosis | Graves disease | hyperthyroidism, Thyrotoxicosis | Thyrotoxicosis | Agent Input |
| phenotyping_reported | graves' disease | graves' disease | graves' disease | Thyrotoxicosis with or without goiter | TTE thyrotoxicosis [hyperthyroidism] | graves' disease | Hyperthyroidism/thyrotoxicosis | TTE thyrotoxicosis [hyperthyroidism] | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | LDpred2 (bigsnpr) | snpnet | PRSCS | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM022749 | PPM022748 | PPM022747 | PPM011058 | PPM007972 | PPM022748 | PPM007977 | PPM007972 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 8 | 5 | 1 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | 0.6339 | N/A | 0.6323 | 0.6339 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0236 | N/A | 0.0216 | 0.0236 | Agent Input |
| performance_metrics.full_model_auc | 0.6637 | 0.6652 | 0.6587 | N/A | 0.7130 | 0.6652 | 0.7137 | 0.7130 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0591 | N/A | 0.0566 | 0.0591 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | 0.0467 | N/A | 0.0464 | 0.0467 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.663730746326419} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.665220447565802} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6587} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71296, 'ci_lower': 0.69708, 'ci_upper': 0.72884} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.665220447565802} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71366, 'ci_lower': 0.6965, 'ci_upper': 0.73082} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71296, 'ci_lower': 0.69708, 'ci_upper': 0.72884} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0199, 'ci_lower': 0.0057, 'ci_upper': 0.034} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05914} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04673} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02359} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.63392, 'ci_lower': 0.61562, 'ci_upper': 0.65223} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0566} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04641} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02158} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.6323, 'ci_lower': 0.61251, 'ci_upper': 0.6521} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05914} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04673} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02359} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.63392, 'ci_lower': 0.61562, 'ci_upper': 0.65223} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.54332658848452} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.433940209108075} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.62508137678846} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.485557892551506} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.008} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.008} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.62508137678846} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.485557892551506} | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=19,108 | n=67,425 | n=94,651 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=269,704 | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | Am J Hum Genet | PLoS Genet | medRxiv | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2022-01-10 | 2021-10-21 | 2026-01-19 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 1085170 | 1085173 | 112 | 279385 | 226 | 1085173 | 69 | 226 | Agent Input |
| covariates | Unknown | Unknown | Unknown | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### knee osteoarthritis

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004883 | PGS002767 | PGS004549 | PGS004479 | PGS001192 | PGS002767 | PGS002729 | PGS001192 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 2/7 | 7/7 | 5/7 | Benchmark Only |
| AoU benchmark AUC | 0.5546 | 0.5528 | 0.5461 | 0.5413 | 0.5246 | 0.5528 | 0.5080 | 0.5246 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | 9/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Knee osteoarthritis | Knee osteoarthritis | M17 (Gonarthrosis [arthrosis of knee]) | M17 (Gonarthrosis [arthrosis of knee]) | Gonarthrosis [arthrosis of knee] (time-to-event) | Knee osteoarthritis | Knee osteoarthritis | Gonarthrosis [arthrosis of knee] (time-to-event) | Agent Input |
| trait_efo | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | Agent Input |
| phenotyping_reported | Incident knee osteoarthritis | Knee osteoarthritis | M17 (Gonarthrosis [arthrosis of knee]) | M17 (Gonarthrosis [arthrosis of knee]) | TTE gonarthrosis [arthrosis of knee] | Knee osteoarthritis | Clinical osteoarthritis | TTE gonarthrosis [arthrosis of knee] | Agent Input |
| method_name | megaprs.auto | PRS-CS | RFDiseasemetaPRS | LDpred2 | snpnet | PRS-CS | Genome-wide significant variants | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM021240 | PPM014967 | PPM020664 | PPM020594 | PPM008613 | PPM014967 | PPM014792 | PPM008613 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 7 | 1 | 1 | 1 | 5 | 1 | 23 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | 0.5565 | N/A | N/A | 0.5565 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0068 | N/A | N/A | 0.0068 | Agent Input |
| performance_metrics.full_model_auc | 0.6000 | N/A | N/A | N/A | 0.6450 | N/A | 0.6600 | 0.6450 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0431 | N/A | N/A | 0.0431 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | 0.0104 | N/A | N/A | 0.0104 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.6, 'ci_lower': 0.58, 'ci_upper': 0.61} | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64504, 'ci_lower': 0.63733, 'ci_upper': 0.65274} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66, 'ci_lower': 0.61, 'ci_upper': 0.71} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64504, 'ci_lower': 0.63733, 'ci_upper': 0.65274} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04312} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.0104} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0068} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55655, 'ci_lower': 0.54824, 'ci_upper': 0.56485} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04312} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.0104} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0068} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55655, 'ci_lower': 0.54824, 'ci_upper': 0.56485} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.37, 'ci_lower': 1.3, 'ci_upper': 1.44} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.35, 'ci_lower': 1.3, 'ci_upper': 1.4} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.366693} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.32326102443575} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.35, 'ci_lower': 1.3, 'ci_upper': 1.4} | N/A | N/A | Agent Input |
| validation_sample_size | n=29,427 | n=39,444 | n=56,192 | n=56,192 | n=67,425 | n=39,444 | n=14,926 | n=67,425 | Agent Input |
| samples_training | n=404 | N/A | n=174,489 | n=174,489 | n=269,704 | N/A | N/A | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (1%), EUR (99%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | 1000G | N/A | UKB | UKB | UKB | N/A | BBJ EB GARP HUNT LLS MyCode UKB arcOGEN deCODE | UKB | Agent Input |
| publication.title | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Risk assessment for hip and knee osteoarthritis using polygenic risk scores. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | Commun Biol | Commun Biol | PLoS Genet | Am J Hum Genet | Arthritis Rheumatol | PLoS Genet | Agent Input |
| date_release | 2024-06-27 | 2022-11-07 | 2024-03-18 | 2024-03-18 | 2021-10-21 | 2022-11-07 | 2022-06-29 | 2021-10-21 | Agent Input |
| variants_number | 952133 | 1052275 | 1059939 | 1059939 | 4525 | 1052275 | 24 | 4525 | Agent Input |
| covariates | PCs 1-10 | age, sex, 10 PCs, technical covariates | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, 10 PCs, technical covariates | Age, sex, BMI | age, sex, UKB array type, Genotype PCs | Agent Input |


### macular degeneration

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004952 | PGS002269 | PGS004606 | PGS001834 | PGS002041 | PGS004606 | PGS004606 | PGS001013 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 3/7 | 3/7 | 6/7 | Benchmark Only |
| AoU benchmark AUC | 0.6375 | 0.6244 | 0.6171 | 0.5967 | 0.5966 | 0.6171 | 0.6171 | 0.5890 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | Age-related macular degeneration | Age-related macular degeneration | Macular degeneration | Agent Input |
| trait_efo | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | macular degeneration | Agent Input |
| phenotyping_reported | Late age-related macular degeneration (Clinical Classification) | Rentinal layer thickness (photoreceptor inner and outer segments) | Age-related macular degeneration | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | Age-related macular degeneration | Age-related macular degeneration | Eye problems/disorders Macular degeneration | Agent Input |
| method_name | Genome-wide significant SNPs | Independent variants associated with AMD | PRS-CS | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | PRS-CS | PRS-CS | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM021761 | PPM012920 | PPM020767 | PPM009564 | PPM011194 | PPM020767 | PPM020767 | PPM007832 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European, South Asian, Not reported | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 6 | 3 | 1 | 8 | 8 | 1 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0.5528 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0.0060 | Agent Input |
| performance_metrics.full_model_auc | 0.8420 | N/A | 0.7100 | N/A | N/A | 0.7100 | 0.7100 | 0.7026 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0.0670 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0.0057 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 84.2} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.70257, 'ci_lower': 0.6826, 'ci_upper': 0.72253} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0175, 'ci_lower': 0.0034, 'ci_upper': 0.0315} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0159, 'ci_lower': 0.0018, 'ci_upper': 0.0299} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.06704} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00573} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00599} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55283, 'ci_lower': 0.52939, 'ci_upper': 0.57627} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.41, 'ci_lower': 1.32, 'ci_upper': 1.5} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': -0.21, 'ci_lower': -0.23, 'ci_upper': -0.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | N/A | Agent Input |
| validation_sample_size | n=1,232 | n=44,823 | n=163,011 | n=19,413 | n=19,413 | n=163,011 | n=163,011 | n=22,208 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=391,124 | N/A | N/A | n=88,703 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | IAMDGC | AREDS BDES CWRU Columbia EUGENDA Edinburgh JHU MMAP Marshfield NHS RotES UCSD UWALF Vanderbilt | IAMDGC | UKB | UKB | IAMDGC | IAMDGC | UKB | Agent Input |
| publication.title | Genetic Risk Score Analysis Supports a Joint View of Two Classification Systems for Age-Related Macular Degeneration. | Photoreceptor Layer Thinning Is an Early Biomarker for Age-Related Macular Degeneration: Epidemiologic and Genetic Evidence from UK Biobank OCT Data. | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Invest Ophthalmol Vis Sci | Ophthalmology | Nat Genet | Am J Hum Genet | Am J Hum Genet | Nat Genet | Nat Genet | PLoS Genet | Agent Input |
| date_release | 2024-09-19 | 2022-04-01 | 2024-02-20 | 2022-01-10 | 2022-01-10 | 2024-02-20 | 2024-02-20 | 2021-10-21 | Agent Input |
| variants_number | 52 | 47 | 1000946 | 157 | 116538 | 1000946 | 1000946 | 53 | Agent Input |
| covariates | Age, sex, survey membership, 10 PCs | Age, age2 (to adjust for non-linear relationships with age), sex, smoking status, and the first ten principal components of genetic ancestry | age, sex, principal components 1-10 | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, principal components 1-10 | age, sex, principal components 1-10 | age, sex, UKB array type, Genotype PCs | Agent Input |


### nodular goiter

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005263 | PGS005262 | PGS005261 | PGS002022 | PGS001814 | PGS005262 | PGS005262 | PGS001814 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 2/7 | 2/7 | 5/7 | Benchmark Only |
| AoU benchmark AUC | 0.7033 | 0.6911 | 0.6158 | 0.5575 | 0.5493 | 0.6911 | 0.6911 | 0.5493 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Benign nodular goiter | Benign nodular goiter | Benign nodular goiter | Nontoxic multinodular goiter | Nontoxic multinodular goiter | Benign nodular goiter | Benign nodular goiter | Nontoxic multinodular goiter | Agent Input |
| trait_efo | benign, nodular goiter | benign, nodular goiter | benign, nodular goiter | multinodular goiter, nontoxic goiter | multinodular goiter, nontoxic goiter | benign, nodular goiter | benign, nodular goiter | multinodular goiter, nontoxic goiter | Agent Input |
| phenotyping_reported | benign nodular gioter | benign nodular gioter | benign nodular gioter | Nontoxic multinodular goiter | Nontoxic multinodular goiter | benign nodular gioter | benign nodular gioter | Nontoxic multinodular goiter | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | PRSCS | PRSCS | Penalized regression (bigstatsr) | Agent Input |
| performance_metrics.selected_performance_id | PPM022746 | PPM022745 | PPM022744 | PPM011050 | PPM009412 | PPM022745 | PPM022745 | PPM009412 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 8 | 8 | 1 | 1 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5876 | 0.5933 | 0.5854 | N/A | N/A | 0.5933 | 0.5933 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.587559211464932} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.593306633581433} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.585439091716637} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.593306633581433} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.593306633581433} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.024, 'ci_lower': 0.0098, 'ci_upper': 0.0382} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0277, 'ci_lower': 0.0135, 'ci_upper': 0.0419} | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0277, 'ci_lower': 0.0135, 'ci_upper': 0.0419} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.36199799551033} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.308952736001074} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.40838651920181} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.342444736541657} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.048} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.047} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.40838651920181} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.342444736541657} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.40838651920181} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.342444736541657} | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=19,043 | n=19,043 | n=94,651 | n=94,651 | n=19,043 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=391,124 | N/A | N/A | n=391,124 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | Am J Hum Genet | Am J Hum Genet | medRxiv | medRxiv | Am J Hum Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2022-01-10 | 2022-01-10 | 2026-01-19 | 2026-01-19 | 2022-01-10 | Agent Input |
| variants_number | 1085170 | 1085173 | 110 | 375470 | 322 | 1085173 | 1085173 | 322 | Agent Input |
| covariates | Unknown | Unknown | Unknown | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | Unknown | sex, age, birth date, deprivation index, 16 PCs | Agent Input |


### pulmonary embolism

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001278 | PGS001280 | PGS001277 | PGS001279 | PGS004530 | PGS001280 | PGS001280 | PGS001277 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 2/7 | 2/7 | 3/7 | Benchmark Only |
| AoU benchmark AUC | 0.5943 | 0.5916 | 0.5907 | 0.5885 | 0.5578 | 0.5916 | 0.5916 | 0.5907 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | previously: Blood clot in the leg (DVT) or lung | PE (time-to-event) | PE +/- DVT | previously: Blood clot in the lung | I26 (Pulmonary embolism) | PE (time-to-event) | PE (time-to-event) | PE +/- DVT | Agent Input |
| trait_efo | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism, deep vein thrombosis | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism | pulmonary embolism | pulmonary embolism, deep vein thrombosis | Agent Input |
| phenotyping_reported | Blood clot in the leg (DVT) or lung | TTE PE | PE +/- DVT | Blood clot in the lung | I26 (Pulmonary embolism) | TTE PE | TTE PE | PE +/- DVT | Agent Input |
| method_name | snpnet | snpnet | snpnet | snpnet | RFDiseasemetaPRS | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM008890 | PPM008900 | PPM008885 | PPM008897 | PPM020645 | PPM008900 | PPM008900 | PPM008885 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 1 | 5 | 5 | 5 | Agent Input |
| performance_metrics.auc | 0.5916 | 0.6077 | 0.6114 | 0.6003 | N/A | 0.6077 | 0.6077 | 0.6114 | Agent Input |
| performance_metrics.r2 | 0.0133 | 0.0140 | 0.0151 | 0.0115 | N/A | 0.0140 | 0.0140 | 0.0151 | Agent Input |
| performance_metrics.full_model_auc | 0.6535 | 0.6762 | 0.6750 | 0.6242 | N/A | 0.6762 | 0.6762 | 0.6750 | Agent Input |
| performance_metrics.full_model_r2 | 0.0337 | 0.0406 | 0.0400 | 0.0176 | N/A | 0.0406 | 0.0406 | 0.0400 | Agent Input |
| performance_metrics.incremental_auc | 0.0350 | 0.0293 | 0.0315 | 0.0446 | N/A | 0.0293 | 0.0293 | 0.0315 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65354, 'ci_lower': 0.63231, 'ci_upper': 0.67477} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67617, 'ci_lower': 0.64866, 'ci_upper': 0.70368} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67497, 'ci_lower': 0.64702, 'ci_upper': 0.70293} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62416, 'ci_lower': 0.60164, 'ci_upper': 0.64668} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67617, 'ci_lower': 0.64866, 'ci_upper': 0.70368} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67617, 'ci_lower': 0.64866, 'ci_upper': 0.70368} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67497, 'ci_lower': 0.64702, 'ci_upper': 0.70293} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03366} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03495} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01331} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.59164, 'ci_lower': 0.56886, 'ci_upper': 0.61442} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04057} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02926} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01403} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60765, 'ci_lower': 0.57812, 'ci_upper': 0.63719} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03998} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03149} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01508} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61144, 'ci_lower': 0.58149, 'ci_upper': 0.6414} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01763} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04457} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60034, 'ci_lower': 0.57683, 'ci_upper': 0.62385} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04057} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02926} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01403} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60765, 'ci_lower': 0.57812, 'ci_upper': 0.63719} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04057} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02926} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01403} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60765, 'ci_lower': 0.57812, 'ci_upper': 0.63719} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03998} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03149} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01508} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61144, 'ci_lower': 0.58149, 'ci_upper': 0.6414} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.242446} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=24,838 | n=24,905 | n=24,905 | n=67,349 | n=56,192 | n=24,905 | n=24,905 | n=24,905 | Agent Input |
| samples_training | n=269,382 | n=269,704 | n=269,704 | n=269,382 | n=174,489 | n=269,704 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Commun Biol | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2024-03-18 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 551 | 88 | 96 | 94 | 1059939 | 88 | 88 | 96 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### abdominal aortic aneurysm

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003973 | PGS003429 | PGS003972 | PGS001784 | PGS000753 | PGS000753 | PGS003973 | PGS000753 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 5/6 | 1/6 | 5/6 | Benchmark Only |
| AoU benchmark AUC | 0.6374 | 0.6341 | 0.6312 | 0.5618 | 0.5388 | 0.5388 | 0.6374 | 0.5388 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| trait_efo | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Agent Input |
| phenotyping_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Prevalent abdominal aortic aneurysm | Prevalent abdominal aortic aneurysm | Abdominal aortic aneurysm | Prevalent abdominal aortic aneurysm | Agent Input |
| method_name | PRS-CS | shaPRS + LDpred2 | PRS-CS | PRS-CS-auto | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | PRS-CS | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM019137 | PPM017103 | PPM019134 | PPM009288 | PPM001912 | PPM001912 | PPM019137 | PPM001912 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 3 | 1 | 7 | 7 | 1 | 7 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0147 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8820 | 0.7080 | 0.6900 | 0.8680 | N/A | N/A | 0.8820 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0055 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.882, 'ci_lower': 0.872, 'ci_upper': 0.892} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.708, 'ci_lower': 0.691, 'ci_upper': 0.725} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.868} | N/A | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.882, 'ci_lower': 0.872, 'ci_upper': 0.892} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00547} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.014661} | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37, 'ci_lower': 1.3, 'ci_upper': 1.44} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37, 'ci_lower': 1.3, 'ci_upper': 1.44} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37, 'ci_lower': 1.3, 'ci_upper': 1.44} | Agent Input |
| validation_sample_size | n=7,517 | n=91,731 | n=6,940 | n=350,767 | n=46,564 | n=46,564 | n=7,517 | n=46,564 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=8,772 | n=8,772 | N/A | n=8,772 | Agent Input |
| ancestry_distribution | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: EUR (89%), MAE (11%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (60%), EAS (17%), EUR (82%), OTH (90%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (25%), EUR (75%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (25%), EUR (75%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (25%), EUR (75%) | Agent Input |
| training_development_cohorts | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | UKB | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS UKAGS UKB VIVA deCODE eMERGE | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI deCODE | MAYO-VDB MVP | MAYO-VDB MVP | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | MAYO-VDB MVP | Agent Input |
| publication.title | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Evaluating the cost-effectiveness of polygenic risk score-stratified screening for abdominal aortic aneurysm. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Genetic Architecture of Abdominal Aortic Aneurysm in the Million Veteran Program. | Genetic Architecture of Abdominal Aortic Aneurysm in the Million Veteran Program. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Genetic Architecture of Abdominal Aortic Aneurysm in the Million Veteran Program. | Agent Input |
| publication.journal | Nat Genet | Nat Commun | Nat Genet | Cell Genom | Circulation | Circulation | Nat Genet | Circulation | Agent Input |
| date_release | 2023-11-01 | 2023-12-15 | 2023-11-01 | 2022-09-08 | 2021-04-07 | 2021-04-07 | 2023-11-01 | 2021-04-07 | Agent Input |
| variants_number | 1118997 | 831447 | 1118997 | 911440 | 29 | 29 | 1118997 | 29 | Agent Input |
| covariates | Age, Age^2, Sex | Unknown | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | Age, sex, PCs (1-5) | Age, sex, PCs (1-5) | Age, Age^2, Sex | Age, sex, PCs (1-5) | Agent Input |


### atopic eczema

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003486 | PGS004587 | PGS003459 | PGS002755 | PGS001773 | PGS002755 | PGS002755 | PGS001773 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 4/6 | 4/6 | 5/6 | Benchmark Only |
| AoU benchmark AUC | 0.5532 | 0.5510 | 0.5417 | 0.5138 | 0.4984 | 0.5138 | 0.5138 | 0.4984 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Atopic eczema | Atopic dermatitis | Atopic eczema or atopic disease | Atopic dermatitis | Moderate-to-severe atopic dermatitis | Atopic dermatitis | Atopic dermatitis | Moderate-to-severe atopic dermatitis | Agent Input |
| trait_efo | atopic eczema | atopic eczema | atopic eczema, allergic disease | atopic eczema | atopic eczema | atopic eczema | atopic eczema | atopic eczema | Agent Input |
| phenotyping_reported | Paradoxical eczema in biologic-treated psoriasis | Incident atopic dermatitis | Paradoxical eczema in biologic-treated psoriasis | Incident atopic dermatitis | Moderate-to-severe aotpic dermatitis | Incident atopic dermatitis | Incident atopic dermatitis | Moderate-to-severe aotpic dermatitis | Agent Input |
| method_name | Genome-wide significant SNPs | Genome-wide significant SNPs | Genome-wide significant SNPs | PRS-CS | Top 25 variants associated with moderate-to-severe atopic dermatitis within the Canadian cohorts GWAS | PRS-CS | PRS-CS | Top 25 variants associated with moderate-to-severe atopic dermatitis within the Canadian cohorts GWAS | Agent Input |
| performance_metrics.selected_performance_id | PPM017412 | PPM020707 | PPM017414 | PPM020709 | PPM009229 | PPM020709 | PPM020709 | PPM009229 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European, South East Asian, East Asian, South Asian, African American or Afro-Caribbean, Native American, Greater Middle Eastern (Middle Eastern, North African or Persian), Hispanic or Latin American, Not reported | European | European | European, South East Asian, East Asian, South Asian, African American or Afro-Caribbean, Native American, Greater Middle Eastern (Middle Eastern, North African or Persian), Hispanic or Latin American, Not reported | Agent Input |
| performance_metrics.record_count | 1 | 2 | 1 | 3 | 4 | 3 | 3 | 4 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5670 | N/A | 0.5850 | N/A | 0.9300 | N/A | N/A | 0.9300 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.4900 | N/A | N/A | 0.4900 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.567} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.585} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.93} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.93} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Hazard ratio (HR, high vs low PRS)', 'name_short': 'Hazard ratio (HR, high vs low PRS)', 'estimate': 1.153, 'ci_lower': 1.037, 'ci_upper': 1.282} | N/A | {'name_long': 'Hazard ratio (HR, high vs low PRS)', 'name_short': 'Hazard ratio (HR, high vs low PRS)', 'estimate': 1.249, 'ci_lower': 1.123, 'ci_upper': 1.391} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.49} | {'name_long': 'Hazard ratio (HR, high vs low PRS)', 'name_short': 'Hazard ratio (HR, high vs low PRS)', 'estimate': 1.249, 'ci_lower': 1.123, 'ci_upper': 1.391} | {'name_long': 'Hazard ratio (HR, high vs low PRS)', 'name_short': 'Hazard ratio (HR, high vs low PRS)', 'estimate': 1.249, 'ci_lower': 1.123, 'ci_upper': 1.391} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.49} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.89, 'ci_lower': 1.08, 'ci_upper': 3.3} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.83, 'ci_lower': 1.17, 'ci_upper': 2.84} | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=3,212 | n=337,910 | n=3,212 | n=337,910 | n=676 | n=337,910 | n=337,910 | n=676 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (100%), AFR (1%), AMR (2%), EAS (8%), EUR (88%) / EVAL: EUR (100%) | GWAS: MAE (100%) / EVAL: MAE (100%) | GWAS: NR (100%), AFR (1%), AMR (2%), EAS (8%), EUR (88%) / EVAL: EUR (100%) | GWAS: NR (100%), AFR (1%), AMR (2%), EAS (8%), EUR (88%) / EVAL: EUR (100%) | GWAS: MAE (100%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | N/A | EB FinnGen UKB | N/A | N/A | CHILD SLSJ | N/A | N/A | CHILD SLSJ | Agent Input |
| publication.title | Atopic polygenic risk score is associated with paradoxical eczema developing in psoriasis patients treated with biologics. | Association of air pollution and genetic risks with incidence of elderly-onset atopic dermatitis: A prospective cohort study. | Atopic polygenic risk score is associated with paradoxical eczema developing in psoriasis patients treated with biologics. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Polygenic risk score for atopic dermatitis in the Canadian population. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Polygenic risk score for atopic dermatitis in the Canadian population. | Agent Input |
| publication.journal | J Invest Dermatol | Ecotoxicol Environ Saf | J Invest Dermatol | Am J Hum Genet | J Allergy Clin Immunol | Am J Hum Genet | Am J Hum Genet | J Allergy Clin Immunol | Agent Input |
| date_release | 2023-04-12 | 2024-01-26 | 2023-04-12 | 2022-11-07 | 2021-11-25 | 2022-11-07 | 2022-11-07 | 2021-11-25 | Agent Input |
| variants_number | 71 | 23 | 170 | 1090702 | 25 | 1090702 | 1090702 | 25 | Agent Input |
| covariates | PCs 1-2 | sex, age, Townsend index, moderate physical and household income | PCs 1-2 | sex, age, Townsend index, moderate physical and household income | Age, sex, father's ethnicity, mother ethnicity | sex, age, Townsend index, moderate physical and household income | sex, age, Townsend index, moderate physical and household income | Age, sex, father's ethnicity, mother ethnicity | Agent Input |


### cervical carcinoma

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000073 | PGS000784 | PGS005165 | PGS003389 | PGS003428 | PGS003428 | PGS001299 | PGS000073 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 5/6 | 6/6 | 1/6 | Benchmark Only |
| AoU benchmark AUC | 0.6951 | 0.6706 | 0.4765 | 0.4762 | 0.3795 | 0.3795 | 0.3377 | 0.6951 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 8/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Agent Input |
| trait_efo | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | Agent Input |
| phenotyping_reported | Incident cervical cancer | Incident cervical cancer | Cervical Cancer | cervical cancer | Incident cervical cancer | Incident cervical cancer | Cervical cancer | Incident cervical cancer | Agent Input |
| method_name | Genome-wide significant variants | 10 variants from Graff et al (PGS000073) with inverse variant weights | Known susceptibility loci (genome-wide significant SNPs) | lassosum | LDpred | LDpred | snpnet | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM002039 | PPM002055 | PPM022403 | PPM016264 | PPM017102 | PPM017102 | PPM008994 | PPM002039 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | East Asian | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 1 | 1 | 1 | 1 | 5 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.5522 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | 0.0026 | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7450 | 0.7450 | 0.5660 | 0.5630 | 0.6130 | 0.6130 | 0.7676 | 0.7450 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.4370 | N/A | 0.0016 | N/A | N/A | 0.1128 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.0068 | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75, 'se': 0.017} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.017} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.566} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.563} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.613} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.613} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.76761, 'ci_lower': 0.74661, 'ci_upper': 0.7886} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75, 'se': 0.017} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.437} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00158} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11284} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00676} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00263} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55215, 'ci_lower': 0.51478, 'ci_upper': 0.58952} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.09, 'ci_upper': 1.37} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.21, 'ci_lower': 1.07, 'ci_upper': 1.35} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.2, 'ci_lower': 1.06, 'ci_upper': 1.36} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.182} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.33, 'se': 0.069} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.33, 'se': 0.069} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.09, 'ci_upper': 1.37} | Agent Input |
| validation_sample_size | n=211,795 | n=211,795 | n=57,359 | n=144,374 | n=128,113 | n=128,113 | n=24,905 | n=211,795 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=4,295 | n=4,295 | n=269,704 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (100%) / EVAL: EAS (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | TwinGene | NCI Seattle TwinGene Umea WTCCC | BBJ | N/A | EB FinnGen KP UKB | EB FinnGen KP UKB | UKB | TwinGene | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Polygenic risk scores for pan-cancer risk prediction in the Chinese population: A population-based cohort study based on the China Kadoorie Biobank. | Common germline risk variants impact somatic alterations and clinical features across cancers. | GWAS meta-analyses clarify genetics of cervical phenotypes and inform risk stratification for cervical cancer. | GWAS meta-analyses clarify genetics of cervical phenotypes and inform risk stratification for cervical cancer. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | PLoS Med | Cancer Res | Hum Mol Genet | Hum Mol Genet | PLoS Genet | Nat Commun | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2025-03-17 | 2023-01-19 | 2023-04-28 | 2023-04-28 | 2021-10-21 | 2020-02-12 | Agent Input |
| variants_number | 10 | 10 | 15 | 2814 | 2894555 | 2894555 | 24 | 10 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Age,Sex (if applicable),Region,Top 10 genetic ancestry principal components | age, top 20 genetic principal components | age, smoking | age, smoking | age, sex, UKB array type, Genotype PCs | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Agent Input |


### late-onset alzheimer's disease

Candidate pool: `5` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000054 | PGS002289 | PGS000334 | PGS004918 | PGS000053 | PGS000054 | PGS000334 | PGS000053 | Agent Input |
| AoU benchmark rank | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | 1/5 | 3/5 | 5/5 | Benchmark Only |
| AoU benchmark AUC | 0.5690 | 0.5203 | 0.5144 | 0.5114 | 0.4346 | 0.5690 | 0.5144 | 0.4346 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 8/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Alzheimer's disease (late onset) | Late-onset Alzheimer's disease | Late-onset Alzheimer’s disease | Late-onset Alzheimers disease (based on SNPs in genes involved in synaptic function) | Alzheimer's disease (late onset) | Alzheimer's disease (late onset) | Late-onset Alzheimer’s disease | Alzheimer's disease (late onset) | Agent Input |
| trait_efo | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | Agent Input |
| phenotyping_reported | Familial late-onset Alzheimer's disease (LOAD) | Pairs matching (short-term memory and attention) no. of correct online round 1 x age interaction | Late-onset Alzheimer’s disease | Late-onset Alzheimer's disease | Familial late-onset Alzheimer's disease (LOAD) | Familial late-onset Alzheimer's disease (LOAD) | Late-onset Alzheimer’s disease | Familial late-onset Alzheimer's disease (LOAD) | Agent Input |
| method_name | Genome-wide significant variants | GWAS-significant variants (including APOE) | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Genome-wide significant variants | Genome-wide significant variants | Clumping and Thresholding (C+T) | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM000135 | PPM012988 | PPM000901 | PPM021384 | PPM000133 | PPM000135 | PPM000901 | PPM000133 | Agent Input |
| performance_metrics.selected_validation_ancestry | Hispanic or Latin American | European | European | European | European | Hispanic or Latin American | European | European | Agent Input |
| performance_metrics.record_count | 3 | 13 | 2 | 1 | 3 | 3 | 2 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.7310 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.1910 | N/A | N/A | N/A | 0.1910 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.731} | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Difference in mean cognition per decacde increase in age per 1-SD higher GRS (%)', 'name_short': 'Difference in mean cognition per decacde increase in age per 1-SD higher GRS (%)', 'estimate': 11.5} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.191, 'ci_lower': 0.131, 'ci_upper': 0.269} | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.191, 'ci_lower': 0.131, 'ci_upper': 0.269} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.73, 'ci_lower': 1.57, 'ci_upper': 1.93} | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.29, 'ci_lower': 1.21, 'ci_upper': 1.37} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.73, 'ci_lower': 1.57, 'ci_upper': 1.93} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.29, 'ci_lower': 1.21, 'ci_upper': 1.37} | Agent Input |
| validation_sample_size | n=3,324 | n=497,087 | n=3,810 | n=136 | n=4,792 | n=3,324 | n=3,810 | n=4,792 | Agent Input |
| samples_training | N/A | N/A | N/A | n=439 | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (19%), EUR (81%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: NR (19%), EUR (81%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | IGAP UKB | ADGC BfDR CHARGE EADI GERAD | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | IGAP UKB | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | Agent Input |
| publication.title | Polygenic risk scores in familial Alzheimer disease. | Association of Genetic Variants Linked to Late-Onset Alzheimer Disease With Cognitive Test Performance by Midlife. | Risk prediction of late-onset Alzheimer's disease implies an oligogenic architecture. | Genetic variants in glutamate-, Aβ-, and tau-related pathways determine polygenic risk for Alzheimer's disease. | Polygenic risk scores in familial Alzheimer disease. | Polygenic risk scores in familial Alzheimer disease. | Risk prediction of late-onset Alzheimer's disease implies an oligogenic architecture. | Polygenic risk scores in familial Alzheimer disease. | Agent Input |
| publication.journal | Neurology | JAMA Netw Open | Nat Commun | Neurobiol Aging | Neurology | Neurology | Nat Commun | Neurology | Agent Input |
| date_release | 2019-12-18 | 2022-05-18 | 2020-10-16 | 2024-06-12 | 2019-12-18 | 2019-12-18 | 2020-10-16 | 2019-12-18 | Agent Input |
| variants_number | 21 | 23 | 22 | 8 | 21 | 21 | 22 | 21 | Agent Input |
| covariates | Age, sex | Unknown | Unknown | Unknown | Age, sex | Age, sex | Unknown | Age, sex | Agent Input |


### urolithiasis

Candidate pool: `5` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004563 | PGS004493 | PGS001250 | PGS004563 | PGS001250 | PGS001250 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 1/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.5566 | 0.5450 | 0.5376 | 0.5566 | 0.5376 | 0.5376 | Benchmark Only |
| Hit@1 | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | N20 (Calculus of kidney and ureter) | N20 (Calculus of kidney and ureter) | Calculus of kidney and ureter (time-to-event) | N20 (Calculus of kidney and ureter) | Calculus of kidney and ureter (time-to-event) | Calculus of kidney and ureter (time-to-event) | Agent Input |
| trait_efo | nephrolithiasis | nephrolithiasis | nephrolithiasis, ureterolithiasis | nephrolithiasis | nephrolithiasis, ureterolithiasis | nephrolithiasis, ureterolithiasis | Agent Input |
| phenotyping_reported | N20 (Calculus of kidney and ureter) | N20 (Calculus of kidney and ureter) | TTE calculus of kidney and ureter | N20 (Calculus of kidney and ureter) | TTE calculus of kidney and ureter | TTE calculus of kidney and ureter | Agent Input |
| method_name | RFDiseasemetaPRS | LDpred2 | snpnet | RFDiseasemetaPRS | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM020678 | PPM020608 | PPM008763 | PPM020678 | PPM008763 | PPM008763 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 5 | 1 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.5668 | N/A | 0.5668 | 0.5668 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0059 | N/A | 0.0059 | 0.0059 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.6649 | N/A | 0.6649 | 0.6649 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0350 | N/A | 0.0350 | 0.0350 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0149 | N/A | 0.0149 | 0.0149 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66491, 'ci_lower': 0.64839, 'ci_upper': 0.68143} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66491, 'ci_lower': 0.64839, 'ci_upper': 0.68143} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66491, 'ci_lower': 0.64839, 'ci_upper': 0.68143} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03503} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01494} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00592} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.56681, 'ci_lower': 0.54876, 'ci_upper': 0.58486} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03503} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01494} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00592} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.56681, 'ci_lower': 0.54876, 'ci_upper': 0.58486} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03503} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01494} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00592} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.56681, 'ci_lower': 0.54876, 'ci_upper': 0.58486} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.283041} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.22730929818809} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.283041} | N/A | N/A | Agent Input |
| validation_sample_size | n=56,192 | n=56,192 | n=67,425 | n=56,192 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=174,489 | n=174,489 | n=269,704 | n=174,489 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Commun Biol | Commun Biol | PLoS Genet | Commun Biol | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2024-03-18 | 2024-03-18 | 2021-10-21 | 2024-03-18 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 1059939 | 1059939 | 341 | 1059939 | 341 | 341 | Agent Input |
| covariates | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### alcohol dependence

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002738 | PGS000201 | PGS000202 | PGS002739 | PGS002738 | PGS002738 | PGS000201 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 1/4 | 1/4 | 2/4 | Benchmark Only |
| AoU benchmark AUC | 0.6051 | 0.5762 | 0.5742 | 0.5224 | 0.6051 | 0.6051 | 0.5762 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Alcohol use disorder | Problematic alcohol use | Problematic alcohol use | Alcohol use disorder | Alcohol use disorder | Alcohol use disorder | Problematic alcohol use | Agent Input |
| trait_efo | alcohol dependence | alcohol dependence measurement | alcohol dependence measurement | alcohol dependence | alcohol dependence | alcohol dependence | alcohol dependence measurement | Agent Input |
| phenotyping_reported | Alcohol use disorder | Alcohol use disorder (DSM-5 criteria count, log-transformed) | Alcohol use disorder (DSM-5 criteria count, log-transformed) | Alcohol use disorder | Alcohol use disorder | Alcohol use disorder | Alcohol use disorder (DSM-5 criteria count, log-transformed) | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CSx (gene-based) | PRS-CS | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM014841 | PPM000626 | PPM000629 | PPM014842 | PPM014841 | PPM014841 | PPM000626 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | African American or Afro-Caribbean | European | European | European | Agent Input |
| performance_metrics.record_count | 4 | 1 | 1 | 1 | 4 | 4 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.96, 'ci_lower': 1.54, 'ci_upper': 2.51} | {'name_long': 'ΔR-squared (vs. covariates alone)', 'name_short': 'ΔR-squared (vs. covariates alone)', 'estimate': 0.01192} | {'name_long': 'ΔR-squared (vs. covariates alone)', 'name_short': 'ΔR-squared (vs. covariates alone)', 'estimate': 0.00456} | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.76, 'ci_lower': 1.32, 'ci_upper': 2.34} | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.96, 'ci_lower': 1.54, 'ci_upper': 2.51} | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.96, 'ci_lower': 1.54, 'ci_upper': 2.51} | {'name_long': 'ΔR-squared (vs. covariates alone)', 'name_short': 'ΔR-squared (vs. covariates alone)', 'estimate': 0.01192} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 3.17, 'se': 1.87} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.099, 'se': 0.01} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.043, 'se': 0.019} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.17, 'se': 0.03} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 3.17, 'se': 1.87} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 3.17, 'se': 1.87} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.099, 'se': 0.01} | Agent Input |
| validation_sample_size | n=7,900 | n=7,599 | n=1,251 | n=6,315 | n=7,900 | n=7,900 | n=7,599 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (12%), EUR (88%) / EVAL: AFR (100%) | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MVP UKB | UKB | UKB | MVP PGC UKB | MVP UKB | MVP UKB | UKB | Agent Input |
| publication.title | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | Using polygenic scores for identifying individuals at increased risk of substance use disorders in clinical and population samples. | Using polygenic scores for identifying individuals at increased risk of substance use disorders in clinical and population samples. | Gene-based polygenic risk scores analysis of alcohol use disorder in African Americans. | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | Using polygenic scores for identifying individuals at increased risk of substance use disorders in clinical and population samples. | Agent Input |
| publication.journal | Alcohol Clin Exp Res | Transl Psychiatry | Transl Psychiatry | Transl Psychiatry | Alcohol Clin Exp Res | Alcohol Clin Exp Res | Transl Psychiatry | Agent Input |
| date_release | 2022-08-03 | 2020-07-01 | 2020-07-01 | 2022-08-03 | 2022-08-03 | 2022-08-03 | 2020-07-01 | Agent Input |
| variants_number | 326000 | 1094954 | 1083002 | 858 | 326000 | 326000 | 1094954 | Agent Input |
| covariates | Unknown | sex, age of last observation, 10 Genetic PCs, genotyping array, data collection site | sex, age of last observation, 10 Genetic PCs | Unknown | Unknown | Unknown | sex, age of last observation, 10 Genetic PCs, genotyping array, data collection site | Agent Input |


### atrial flutter

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002050 | PGS001841 | PGS001339 | PGS001263 | PGS001263 | PGS001263 | PGS001263 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 4/4 | 4/4 | 4/4 | Benchmark Only |
| AoU benchmark AUC | 0.5909 | 0.5856 | 0.5788 | 0.5785 | 0.5785 | 0.5785 | 0.5785 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Atrial fibrillation and flutter | Atrial fibrillation and flutter | Atrial fibrillation and flutter (time-to-event) | Atrial flutter | Atrial flutter | Atrial flutter | Atrial flutter | Agent Input |
| trait_efo | atrial fibrillation, atrial flutter | atrial fibrillation, atrial flutter | atrial fibrillation, atrial flutter | atrial flutter | atrial flutter | atrial flutter | atrial flutter | Agent Input |
| phenotyping_reported | Atrial fibrillation and flutter | Atrial fibrillation and flutter | TTE atrial fibrillation and flutter | Atrial flutter | Atrial flutter | Atrial flutter | Atrial flutter | Agent Input |
| method_name | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | snpnet | snpnet | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM011262 | PPM009618 | PPM009183 | PPM008822 | PPM008822 | PPM008822 | PPM008822 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 8 | 8 | 6 | 5 | 5 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6130 | 0.6172 | 0.6172 | 0.6172 | 0.6172 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0245 | 0.0252 | 0.0252 | 0.0252 | 0.0252 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.7766 | 0.7818 | 0.7818 | 0.7818 | 0.7818 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.1402 | 0.1422 | 0.1422 | 0.1422 | 0.1422 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0219 | 0.0217 | 0.0217 | 0.0217 | 0.0217 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.77656, 'ci_lower': 0.76352, 'ci_upper': 0.7896} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78179, 'ci_lower': 0.76842, 'ci_upper': 0.79516} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78179, 'ci_lower': 0.76842, 'ci_upper': 0.79516} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78179, 'ci_lower': 0.76842, 'ci_upper': 0.79516} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78179, 'ci_lower': 0.76842, 'ci_upper': 0.79516} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.1034, 'ci_lower': 0.0894, 'ci_upper': 0.1174} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.1026, 'ci_lower': 0.0885, 'ci_upper': 0.1165} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.14023} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02188} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02447} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.613, 'ci_lower': 0.59591, 'ci_upper': 0.6301} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1422} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02171} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02517} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61716, 'ci_lower': 0.59934, 'ci_upper': 0.63498} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1422} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02171} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02517} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61716, 'ci_lower': 0.59934, 'ci_upper': 0.63498} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1422} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02171} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02517} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61716, 'ci_lower': 0.59934, 'ci_upper': 0.63498} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1422} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02171} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02517} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61716, 'ci_lower': 0.59934, 'ci_upper': 0.63498} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,230 | n=19,230 | n=24,905 | n=24,905 | n=24,905 | n=24,905 | n=24,905 | Agent Input |
| samples_training | n=391,124 | n=391,124 | n=269,704 | n=269,704 | n=269,704 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (17%), EAS (17%), EUR (33%), MAO (17%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 554908 | 3980 | 2142 | 2087 | 2087 | 2087 | 2087 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### hypertrophic cardiomyopathy

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004911 | PGS000739 | PGS004910 | PGS000778 | PGS004911 | PGS004911 | PGS000739 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 1/4 | 1/4 | 2/4 | Benchmark Only |
| AoU benchmark AUC | 0.6036 | 0.5891 | 0.5873 | 0.5514 | 0.6036 | 0.6036 | 0.5891 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Agent Input |
| trait_efo | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | Agent Input |
| phenotyping_reported | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Clinical events in individuals with a pathogenic or likely pathogenic sarcomeric variant | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Agent Input |
| method_name | PRS-CS | Genome-wide significant variants | PRS-CS | Genome-wide significant variants | PRS-CS | PRS-CS | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM021367 | PPM018531 | PPM021366 | PPM002016 | PPM021367 | PPM021367 | PPM018531 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | Not reported | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 8 | 1 | 6 | 1 | 1 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8000 | 0.8210 | 0.7300 | N/A | 0.8000 | 0.8000 | 0.8210 | Agent Input |
| performance_metrics.full_model_r2 | 0.0480 | N/A | 0.0310 | N/A | 0.0480 | 0.0480 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.821, 'ci_lower': 0.772, 'ci_upper': 0.871} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.821, 'ci_lower': 0.772, 'ci_upper': 0.871} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.031} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.5} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.97} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.26} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.28, 'ci_lower': 1.06, 'ci_upper': 1.54} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.247, 'se': 0.095} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | N/A | Agent Input |
| validation_sample_size | n=343,182 | n=184,511 | n=343,182 | n=368 | n=343,182 | n=343,182 | n=184,511 | Agent Input |
| samples_training | N/A | n=47,737 | N/A | N/A | N/A | N/A | n=47,737 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (3%), EAS (80%), EUR (90%), OTH (60%), SAS (4%) / DEV: MAE (100%) / EVAL: EUR (40%), MAE (60%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / EVAL: NR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (3%), EAS (80%), EUR (90%), OTH (60%), SAS (4%) / DEV: MAE (100%) / EVAL: EUR (40%), MAE (60%) | Agent Input |
| training_development_cohorts | BRRD GEL HCMR RBH-CRB | BRRD HCMR UKB | BRRD GEL HCMR RBH-CRB | ERSPC LHSC MHI NL4 RBH-CRB UKDHP UMCG | BRRD GEL HCMR RBH-CRB | BRRD GEL HCMR RBH-CRB | BRRD HCMR UKB | Agent Input |
| publication.title | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Common genetic variants and modifiable risk factors underpin hypertrophic cardiomyopathy susceptibility and expressivity. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Shared genetic pathways contribute to risk of hypertrophic and dilated cardiomyopathies with opposite directions of effect. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Common genetic variants and modifiable risk factors underpin hypertrophic cardiomyopathy susceptibility and expressivity. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2025-02-26 | 2021-02-23 | 2025-02-26 | 2021-05-28 | 2025-02-26 | 2025-02-26 | 2021-02-23 | Agent Input |
| variants_number | 374114 | 27 | 374190 | 20 | 374114 | 374114 | 27 | Agent Input |
| covariates | age, age^2, sex, PC1-10 | Clinical risk factors (obesity, HTN, AF, CAD), HCM-ACMG rare variant carrier status, age, sex, genotyping array, and PCs 1-5 | age, age^2, sex, PC1-10 | Genetic relatedness matrix, sex | age, age^2, sex, PC1-10 | age, age^2, sex, PC1-10 | Clinical risk factors (obesity, HTN, AF, CAD), HCM-ACMG rare variant carrier status, age, sex, genotyping array, and PCs 1-5 | Agent Input |


### juvenile idiopathic arthritis

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000114 | PGS000325 | PGS000326 | PGS000324 | PGS000114 | PGS000114 | PGS000114 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 1/4 | 1/4 | 1/4 | Benchmark Only |
| AoU benchmark AUC | 0.5768 | 0.5517 | 0.5315 | 0.5230 | 0.5768 | 0.5768 | 0.5768 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Juvenile Idiopathic Arthritis | Oligoarthritis Juvenile Idiophatic Arthritis | Rheumatoid-factor-negative Polyarthritis (Juvenile Idiophatic Arthritis) | Enthesitis-related Juvenile Idiophatic Arthritis | Juvenile Idiopathic Arthritis | Juvenile Idiopathic Arthritis | Juvenile Idiopathic Arthritis | Agent Input |
| trait_efo | juvenile idiopathic arthritis | oligoarticular juvenile idiopathic arthritis | polyarticular juvenile idiopathic arthritis, rheumatoid factor negative | enthesitis-related juvenile idiopathic arthritis | juvenile idiopathic arthritis | juvenile idiopathic arthritis | juvenile idiopathic arthritis | Agent Input |
| phenotyping_reported | Juvenile Idiopathic Arthritis | Oligoarthritis Juvenile Idiophatic Arthritis | Rheumatoid-factor-negative Polyarthritis | Enthesitis-related Arthritis | Juvenile Idiopathic Arthritis | Juvenile Idiopathic Arthritis | Juvenile Idiopathic Arthritis | Agent Input |
| method_name | SparSNP | SparSNP | SparSNP | SparSNP | SparSNP | SparSNP | SparSNP | Agent Input |
| performance_metrics.selected_performance_id | PPM000263 | PPM000875 | PPM000877 | PPM000874 | PPM000263 | PPM000263 | PPM000263 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 4 | 4 | 4 | 4 | 4 | 4 | 4 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7380 | 0.8000 | 0.7600 | 0.9300 | 0.7380 | 0.7380 | 0.7380 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.705, 'ci_upper': 0.77} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8, 'ci_lower': 0.77, 'ci_upper': 0.84} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.76, 'ci_lower': 0.72, 'ci_upper': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.93, 'ci_lower': 0.86, 'ci_upper': 0.99} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.705, 'ci_upper': 0.77} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.705, 'ci_upper': 0.77} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.705, 'ci_upper': 0.77} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.085, 'ci_lower': 1.773, 'ci_upper': 2.471} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.93, 'ci_lower': 1.75, 'ci_upper': 2.13} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.51, 'ci_lower': 1.35, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 3.09, 'ci_lower': 2.07, 'ci_upper': 5.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.085, 'ci_lower': 1.773, 'ci_upper': 2.471} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.085, 'ci_lower': 1.773, 'ci_upper': 2.471} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.085, 'ci_lower': 1.773, 'ci_upper': 2.471} | Agent Input |
| validation_sample_size | n=940 | n=3,157 | n=3,089 | n=594 | n=940 | n=940 | n=940 | Agent Input |
| samples_training | n=7,505 | n=6,137 | n=5,733 | n=5,354 | n=7,505 | n=7,505 | n=7,505 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | Agent Input |
| publication.title | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Agent Input |
| publication.journal | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Agent Input |
| date_release | 2020-02-27 | 2020-09-18 | 2020-09-18 | 2020-09-18 | 2020-02-27 | 2020-02-27 | 2020-02-27 | Agent Input |
| variants_number | 26 | 21 | 12 | 138 | 26 | 26 | 26 | Agent Input |
| covariates | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | Agent Input |


### peripheral vascular disease

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005217 | PGS002055 | PGS005158 | PGS001843 | PGS005217 | PGS002055 | PGS001843 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 1/4 | 2/4 | 4/4 | Benchmark Only |
| AoU benchmark AUC | 0.5862 | 0.5195 | 0.5176 | 0.5123 | 0.5862 | 0.5195 | 0.5123 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 8/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral vascular disease, unspecified | Agent Input |
| trait_efo | peripheral arterial disease | peripheral vascular disease | peripheral arterial disease | peripheral vascular disease | peripheral arterial disease | peripheral vascular disease | peripheral vascular disease | Agent Input |
| phenotyping_reported | Incident peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease in type 2 diabetes | Peripheral vascular disease, unspecified | Incident peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral vascular disease, unspecified | Agent Input |
| method_name | LDpred2 | LDpred2 (bigsnpr) | Genome-wide significant SNPs | Penalized regression (bigstatsr) | LDpred2 | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | Agent Input |
| performance_metrics.selected_performance_id | PPM022612 | PPM011302 | PPM022378 | PPM009634 | PPM022612 | PPM011302 | PPM009634 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, East Asian, European, Greater Middle Eastern (Middle Eastern, North African or Persian), South Asian | European | European | European | African American or Afro-Caribbean, East Asian, European, Greater Middle Eastern (Middle Eastern, North African or Persian), South Asian | European | European | Agent Input |
| performance_metrics.record_count | 15 | 8 | 2 | 8 | 15 | 8 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7310 | N/A | N/A | N/A | 0.7310 | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.731} | N/A | N/A | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.731} | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0175, 'ci_lower': 0.0035, 'ci_upper': 0.0315} | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0151, 'ci_lower': 0.0011, 'ci_upper': 0.029} | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0175, 'ci_lower': 0.0035, 'ci_upper': 0.0315} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0151, 'ci_lower': 0.0011, 'ci_upper': 0.029} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.66, 'ci_lower': 1.61, 'ci_upper': 1.71} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.13, 'ci_lower': 1.03, 'ci_upper': 1.23} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.66, 'ci_lower': 1.61, 'ci_upper': 1.71} | N/A | N/A | Agent Input |
| validation_sample_size | n=304,294 | n=19,668 | n=10,836 | n=19,668 | n=304,294 | n=19,668 | n=19,668 | Agent Input |
| samples_training | n=96,239 | n=391,124 | N/A | n=391,124 | n=96,239 | n=391,124 | n=391,124 | Agent Input |
| ancestry_distribution | GWAS: NR (2%), AFR (70%), AMR (50%), EAS (7%), EUR (74%), MAE (14%), MAO (2%), OTH (6%), SAS (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (13%), EAS (13%), EUR (20%), GME (13%), MAE (7%), SAS (13%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: AFR (20%), AMR (8%), EUR (72%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: NR (2%), AFR (70%), AMR (50%), EAS (7%), EUR (74%), MAE (14%), MAO (2%), OTH (6%), SAS (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (13%), EAS (13%), EUR (20%), GME (13%), MAE (7%), SAS (13%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | Agent Input |
| training_development_cohorts | ARIC AWI-Gen BBJ BioMe CARDIA CARDIoGRAMplusC4D CFS CHOP CHS CKB COMPASS EPIC_CAD GERA GerMIFS HANDLS HISAYAMA HRS HUNT HYPERGEN HealthABC INTERSTROKE JHS JOCO JUPITER KCPS LOLIPOP MESA MGBB MVP Multiple Other PMB PROMIS REGARDS RHS SIGNET SiGN UKB WHI deCODE eMERGE | UKB | N/A | UKB | ARIC AWI-Gen BBJ BioMe CARDIA CARDIoGRAMplusC4D CFS CHOP CHS CKB COMPASS EPIC_CAD GERA GerMIFS HANDLS HISAYAMA HRS HUNT HYPERGEN HealthABC INTERSTROKE JHS JOCO JUPITER KCPS LOLIPOP MESA MGBB MVP Multiple Other PMB PROMIS REGARDS RHS SIGNET SiGN UKB WHI deCODE eMERGE | UKB | UKB | Agent Input |
| publication.title | Polygenic Prediction of Peripheral Artery Disease and Major Adverse Limb Events. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Modifiable Lifestyle Factors, Genetic Risk, and Incident Peripheral Artery Disease Among Individuals With Type 2 Diabetes: A Prospective Study. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Polygenic Prediction of Peripheral Artery Disease and Major Adverse Limb Events. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Agent Input |
| publication.journal | JAMA Cardiol | Am J Hum Genet | Diabetes Care | Am J Hum Genet | JAMA Cardiol | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2025-06-16 | 2022-01-10 | 2025-02-26 | 2022-01-10 | 2025-06-16 | 2022-01-10 | 2022-01-10 | Agent Input |
| variants_number | 1296292 | 599514 | 19 | 242 | 1296292 | 599514 | 242 | Agent Input |
| covariates | age, sex and the first ten principal components of genetic ancestry | sex, age, birth date, deprivation index, 16 PCs | age (continuous, years), sex (male, female), Townsend Deprivation Index (continuous), race/ethnicity (White, others), education attainment (college or university degree, A/AS levels or equivalent or O levels/GCSEs or equivalent or other professional qualifications, or none of the above), family history of CVD (yes, no), prevalence of hypertension (yes, no), use of antihypertensive medication (yes, no), use of lipidlowing medication (yes, no), use of aspirin (yes, no), diabetes duration (continuous, years), HbA1c (continuous, %), use of diabetes medication (none, only oral medication pills, or only insulin or combination of oral medications and insulin), genotype measurement batch, the first 10 principal components of ancestry, weighted healthy lifestyle scores (continuous) | sex, age, birth date, deprivation index, 16 PCs | age, sex and the first ten principal components of genetic ancestry | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Agent Input |


### psoriatic arthritis

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001287 | PGS000342 | PGS001287 | PGS001287 | PGS000342 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 1/2 | 1/2 | 2/2 | Benchmark Only |
| AoU benchmark AUC | 0.5731 | 0.5102 | 0.5731 | 0.5731 | 0.5102 | Benchmark Only |
| Hit@1 | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 8/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Psoriatic arthropathy | Psoriatic arthritis | Psoriatic arthropathy | Psoriatic arthropathy | Psoriatic arthritis | Agent Input |
| trait_efo | psoriatic arthritis | psoriatic arthritis | psoriatic arthritis | psoriatic arthritis | psoriatic arthritis | Agent Input |
| phenotyping_reported | Psoriatic arthropathy | Psoriatic arthritis | Psoriatic arthropathy | Psoriatic arthropathy | Psoriatic arthritis | Agent Input |
| method_name | snpnet | GWAS-significant variants, HLA-specific significant variants. | snpnet | snpnet | GWAS-significant variants, HLA-specific significant variants. | Agent Input |
| performance_metrics.selected_performance_id | PPM008935 | PPM000971 | PPM008935 | PPM008935 | PPM000971 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | NR | European | European | NR | Agent Input |
| performance_metrics.record_count | 5 | 1 | 5 | 5 | 1 | Agent Input |
| performance_metrics.auc | 0.6765 | N/A | 0.6765 | 0.6765 | N/A | Agent Input |
| performance_metrics.r2 | 0.0335 | N/A | 0.0335 | 0.0335 | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7281 | 0.5620 | 0.7281 | 0.7281 | 0.5620 | Agent Input |
| performance_metrics.full_model_r2 | 0.0515 | N/A | 0.0515 | 0.0515 | N/A | Agent Input |
| performance_metrics.incremental_auc | 0.0835 | N/A | 0.0835 | 0.0835 | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.72814, 'ci_lower': 0.67154, 'ci_upper': 0.78475} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.562, 'ci_lower': 0.506, 'ci_upper': 0.618} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.72814, 'ci_lower': 0.67154, 'ci_upper': 0.78475} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.72814, 'ci_lower': 0.67154, 'ci_upper': 0.78475} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.562, 'ci_lower': 0.506, 'ci_upper': 0.618} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05154} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08346} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0335} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.67648, 'ci_lower': 0.61155, 'ci_upper': 0.7414} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05154} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08346} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0335} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.67648, 'ci_lower': 0.61155, 'ci_upper': 0.7414} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05154} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08346} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0335} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.67648, 'ci_lower': 0.61155, 'ci_upper': 0.7414} | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=24,905 | n=543 | n=24,905 | n=24,905 | n=543 | Agent Input |
| samples_training | n=269,704 | N/A | n=269,704 | n=269,704 | N/A | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: NR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: NR (100%) | Agent Input |
| training_development_cohorts | UKB | N/A | UKB | UKB | N/A | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Evaluation of a Genetic Risk Score for Diagnosis of Psoriatic Arthritis. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Evaluation of a Genetic Risk Score for Diagnosis of Psoriatic Arthritis. | Agent Input |
| publication.journal | PLoS Genet | J Psoriasis Psoriatic Arthritis | PLoS Genet | PLoS Genet | J Psoriasis Psoriatic Arthritis | Agent Input |
| date_release | 2021-10-21 | 2020-11-20 | 2021-10-21 | 2021-10-21 | 2020-11-20 | Agent Input |
| variants_number | 36 | 11 | 36 | 36 | 11 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Unknown | Agent Input |


### sarcoidosis

Candidate pool: `4` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001872 | PGS000922 | PGS000923 | PGS000922 | PGS000922 | PGS000922 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 2/3 | 2/3 | 2/3 | Benchmark Only |
| AoU benchmark AUC | 0.5729 | 0.5641 | 0.5570 | 0.5641 | 0.5641 | 0.5641 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | 6/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Sarcoidosis | Sarcoidosis | Sarcoidosis (time-to-event) | Sarcoidosis | Sarcoidosis | Sarcoidosis | Agent Input |
| trait_efo | skin sarcoidosis | sarcoidosis | sarcoidosis | sarcoidosis | sarcoidosis | sarcoidosis | Agent Input |
| phenotyping_reported | Sarcoidosis | Sarcoidosis | TTE sarcoidosis | Sarcoidosis | Sarcoidosis | Sarcoidosis | Agent Input |
| method_name | Penalized regression (bigstatsr) | snpnet | snpnet | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM009865 | PPM007443 | PPM007447 | PPM007443 | PPM007443 | PPM007443 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 7 | 4 | 4 | 4 | 4 | 4 | Agent Input |
| performance_metrics.auc | N/A | 0.6428 | 0.6456 | 0.6428 | 0.6428 | 0.6428 | Agent Input |
| performance_metrics.r2 | N/A | 0.0174 | 0.0180 | 0.0174 | 0.0174 | 0.0174 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.6486 | 0.6545 | 0.6486 | 0.6486 | 0.6486 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0192 | 0.0209 | 0.0192 | 0.0192 | 0.0192 | Agent Input |
| performance_metrics.incremental_auc | N/A | 0.0919 | 0.0900 | 0.0919 | 0.0919 | 0.0919 | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6486, 'ci_lower': 0.60932, 'ci_upper': 0.68789} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65455, 'ci_lower': 0.6217, 'ci_upper': 0.6874} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6486, 'ci_lower': 0.60932, 'ci_upper': 0.68789} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6486, 'ci_lower': 0.60932, 'ci_upper': 0.68789} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6486, 'ci_lower': 0.60932, 'ci_upper': 0.68789} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0199, 'ci_lower': 0.0059, 'ci_upper': 0.0338} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01916} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.09187} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01741} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64282, 'ci_lower': 0.60353, 'ci_upper': 0.68211} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.02088} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.09004} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.018} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64561, 'ci_lower': 0.61168, 'ci_upper': 0.67954} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01916} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.09187} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01741} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64282, 'ci_lower': 0.60353, 'ci_upper': 0.68211} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01916} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.09187} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01741} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64282, 'ci_lower': 0.60353, 'ci_upper': 0.68211} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01916} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.09187} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01741} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64282, 'ci_lower': 0.60353, 'ci_upper': 0.68211} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,670 | n=67,425 | n=67,425 | n=67,425 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=269,704 | n=269,704 | n=269,704 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 79 | 12 | 22 | 12 | 12 | 12 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### bilirubin metabolism disease

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001824 | PGS002032 | PGS000924 | PGS002032 | PGS000924 | PGS000924 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 2/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.7228 | 0.7206 | 0.7166 | 0.7206 | 0.7166 | 0.7166 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Disorders of bilirubin excretion | Disorders of bilirubin excretion | Disorders of porphyrin and bilirubin metabolism (time-to-event) | Disorders of bilirubin excretion | Disorders of porphyrin and bilirubin metabolism (time-to-event) | Disorders of porphyrin and bilirubin metabolism (time-to-event) | Agent Input |
| trait_efo | bilirubin metabolism disease | bilirubin metabolism disease | bilirubin metabolism disease, porphyrin metabolism disease | bilirubin metabolism disease | bilirubin metabolism disease, porphyrin metabolism disease | bilirubin metabolism disease, porphyrin metabolism disease | Agent Input |
| phenotyping_reported | Disorders of bilirubin excretion | Disorders of bilirubin excretion | TTE disorders of porphyrin and bilirubin metabolism | Disorders of bilirubin excretion | TTE disorders of porphyrin and bilirubin metabolism | TTE disorders of porphyrin and bilirubin metabolism | Agent Input |
| method_name | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | snpnet | LDpred2 (bigsnpr) | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM009490 | PPM011128 | PPM007451 | PPM011128 | PPM007451 | PPM007451 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 7 | 7 | 4 | 7 | 4 | 4 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.8870 | N/A | 0.8870 | 0.8870 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.2184 | N/A | 0.2184 | 0.2184 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.9059 | N/A | 0.9059 | 0.9059 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.2371 | N/A | 0.2371 | 0.2371 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.2821 | N/A | 0.2821 | 0.2821 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.90591, 'ci_lower': 0.88325, 'ci_upper': 0.92858} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.90591, 'ci_lower': 0.88325, 'ci_upper': 0.92858} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.90591, 'ci_lower': 0.88325, 'ci_upper': 0.92858} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0716, 'ci_lower': 0.0577, 'ci_upper': 0.0854} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0716, 'ci_lower': 0.0578, 'ci_upper': 0.0854} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.23709} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.28213} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.21843} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.88697, 'ci_lower': 0.86397, 'ci_upper': 0.90997} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0716, 'ci_lower': 0.0578, 'ci_upper': 0.0854} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.23709} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.28213} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.21843} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.88697, 'ci_lower': 0.86397, 'ci_upper': 0.90997} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.23709} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.28213} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.21843} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.88697, 'ci_lower': 0.86397, 'ci_upper': 0.90997} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,924 | n=19,924 | n=67,425 | n=19,924 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=391,124 | n=269,704 | n=391,124 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | PLoS Genet | Am J Hum Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2022-01-10 | 2021-10-21 | 2022-01-10 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 22 | 19768 | 5 | 19768 | 5 | 5 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### bipolar disorder

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002786 | PGS002787 | PGS002788 | PGS002786 | PGS002786 | PGS002786 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 1/3 | 1/3 | 1/3 | Benchmark Only |
| AoU benchmark AUC | 0.5650 | 0.5599 | 0.5382 | 0.5650 | 0.5650 | 0.5650 | Benchmark Only |
| Hit@1 | Yes | No | No | Yes | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Bipolar disorder | Type 1 bipolar disorder | Type 2 bipolar disorder | Bipolar disorder | Bipolar disorder | Bipolar disorder | Agent Input |
| trait_efo | bipolar disorder | bipolar I disorder | bipolar II disorder | bipolar disorder | bipolar disorder | bipolar disorder | Agent Input |
| phenotyping_reported | Cognitive function (pattern comparison) | Psychiatric behavior (Dsm5 depression) | Psychiatric behavior (Sluggish cognitive tempo) | Cognitive function (pattern comparison) | Cognitive function (pattern comparison) | Cognitive function (pattern comparison) | Agent Input |
| method_name | SDPR | SDPR | SDPR | SDPR | SDPR | SDPR | Agent Input |
| performance_metrics.selected_performance_id | PPM015078 | PPM015158 | PPM015195 | PPM015078 | PPM015078 | PPM015078 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 50 | 50 | 50 | 50 | 50 | 50 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0025 | 0.0028 | 0.0031 | 0.0025 | 0.0025 | 0.0025 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00251110019585597} | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00275397293669774} | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00307366437856391} | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00251110019585597} | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00251110019585597} | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00251110019585597} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=2,524 | n=2,198 | n=2,524 | n=2,524 | n=2,524 | n=2,524 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | PGC | PGC | PGC | PGC | PGC | PGC | Agent Input |
| publication.title | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Agent Input |
| publication.journal | Transl Psychiatry | Transl Psychiatry | Transl Psychiatry | Transl Psychiatry | Transl Psychiatry | Transl Psychiatry | Agent Input |
| date_release | 2022-09-29 | 2022-09-29 | 2022-09-29 | 2022-09-29 | 2022-09-29 | 2022-09-29 | Agent Input |
| variants_number | 948996 | 937511 | 935292 | 948996 | 948996 | 948996 | Agent Input |
| covariates | age, PCs1-3 | age, PCs1-3 | age, PCs1-3 | age, PCs1-3 | age, PCs1-3 | age, PCs1-3 | Agent Input |


### blood coagulation disease

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001033 | PGS002034 | PGS001826 | PGS001033 | PGS001033 | PGS001033 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 1/3 | 1/3 | 1/3 | Benchmark Only |
| AoU benchmark AUC | 0.5721 | 0.5702 | 0.5695 | 0.5721 | 0.5721 | 0.5721 | Benchmark Only |
| Hit@1 | Yes | No | No | Yes | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 9/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Other coagulation defects (time-to-event) | Congenital deficiency of other clotting factors (including factor VII) | Congenital deficiency of other clotting factors (including factor VII) | Other coagulation defects (time-to-event) | Other coagulation defects (time-to-event) | Other coagulation defects (time-to-event) | Agent Input |
| trait_efo | blood coagulation disease | congenital vitamin K-dependent coagulation factors deficiency | congenital vitamin K-dependent coagulation factors deficiency | blood coagulation disease | blood coagulation disease | blood coagulation disease | Agent Input |
| phenotyping_reported | TTE other coagulation defects | Congenital deficiency of other clotting factors (including factor VII) | Congenital deficiency of other clotting factors (including factor VII) | TTE other coagulation defects | TTE other coagulation defects | TTE other coagulation defects | Agent Input |
| method_name | snpnet | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM007932 | PPM011143 | PPM009505 | PPM007932 | PPM007932 | PPM007932 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 5 | 4 | 4 | 5 | 5 | 5 | Agent Input |
| performance_metrics.auc | 0.6340 | N/A | N/A | 0.6340 | 0.6340 | 0.6340 | Agent Input |
| performance_metrics.r2 | 0.0578 | N/A | N/A | 0.0578 | 0.0578 | 0.0578 | Agent Input |
| performance_metrics.full_model_auc | 0.6562 | N/A | N/A | 0.6562 | 0.6562 | 0.6562 | Agent Input |
| performance_metrics.full_model_r2 | 0.0518 | N/A | N/A | 0.0518 | 0.0518 | 0.0518 | Agent Input |
| performance_metrics.incremental_auc | 0.1205 | N/A | N/A | 0.1205 | 0.1205 | 0.1205 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65623, 'ci_lower': 0.61832, 'ci_upper': 0.69414} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65623, 'ci_lower': 0.61832, 'ci_upper': 0.69414} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65623, 'ci_lower': 0.61832, 'ci_upper': 0.69414} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65623, 'ci_lower': 0.61832, 'ci_upper': 0.69414} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05179} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12049} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05781} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.63402, 'ci_lower': 0.60616, 'ci_upper': 0.66189} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0563, 'ci_lower': 0.0424, 'ci_upper': 0.0702} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0562, 'ci_lower': 0.0424, 'ci_upper': 0.0701} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05179} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12049} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05781} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.63402, 'ci_lower': 0.60616, 'ci_upper': 0.66189} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05179} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12049} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05781} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.63402, 'ci_lower': 0.60616, 'ci_upper': 0.66189} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05179} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12049} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05781} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.63402, 'ci_lower': 0.60616, 'ci_upper': 0.66189} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=67,425 | n=19,864 | n=19,864 | n=67,425 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=269,704 | n=391,124 | n=391,124 | n=269,704 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (75%), SAS (25%) | DEV: EUR (100%) / EVAL: EUR (75%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | PLoS Genet | Am J Hum Genet | Am J Hum Genet | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2021-10-21 | 2022-01-10 | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 1 | 32552 | 45 | 1 | 1 | 1 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### dupuytren contracture

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002092 | PGS001880 | PGS001254 | PGS002092 | PGS001254 | PGS001254 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 1/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.6784 | 0.6762 | 0.6323 | 0.6784 | 0.6323 | 0.6323 | Benchmark Only |
| Hit@1 | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | 9/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Contracture of palmar fascia [Dupuytren's disease] | Contracture of palmar fascia [Dupuytren's disease] | Dupuytren's contracture | Contracture of palmar fascia [Dupuytren's disease] | Dupuytren's contracture | Dupuytren's contracture | Agent Input |
| trait_efo | Dupuytren Contracture | Dupuytren Contracture | Dupuytren Contracture | Dupuytren Contracture | Dupuytren Contracture | Dupuytren Contracture | Agent Input |
| phenotyping_reported | Contracture of palmar fascia [Dupuytren's disease] | Contracture of palmar fascia [Dupuytren's disease] | Dupuytren's contracture | Contracture of palmar fascia [Dupuytren's disease] | Dupuytren's contracture | Dupuytren's contracture | Agent Input |
| method_name | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | snpnet | LDpred2 (bigsnpr) | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM011593 | PPM009925 | PPM008780 | PPM011593 | PPM008780 | PPM008780 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 7 | 7 | 2 | 7 | 2 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6646 | N/A | 0.6646 | 0.6646 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0247 | N/A | 0.0247 | 0.0247 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.7413 | N/A | 0.7413 | 0.7413 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0544 | N/A | 0.0544 | 0.0544 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0447 | N/A | 0.0447 | 0.0447 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74126, 'ci_lower': 0.69429, 'ci_upper': 0.78823} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74126, 'ci_lower': 0.69429, 'ci_upper': 0.78823} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74126, 'ci_lower': 0.69429, 'ci_upper': 0.78823} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0797, 'ci_lower': 0.0655, 'ci_upper': 0.0938} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0783, 'ci_lower': 0.0641, 'ci_upper': 0.0924} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05438} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04471} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02466} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.66457, 'ci_lower': 0.60823, 'ci_upper': 0.72091} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0797, 'ci_lower': 0.0655, 'ci_upper': 0.0938} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05438} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04471} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02466} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.66457, 'ci_lower': 0.60823, 'ci_upper': 0.72091} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05438} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04471} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02466} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.66457, 'ci_lower': 0.60823, 'ci_upper': 0.72091} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=18,971 | n=18,971 | n=67,425 | n=18,971 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=391,124 | n=269,704 | n=391,124 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | PLoS Genet | Am J Hum Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2022-01-10 | 2021-10-21 | 2022-01-10 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 484484 | 2443 | 11 | 484484 | 11 | 11 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### hashimoto's thyroiditis

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005272 | PGS005271 | PGS005270 | PGS005271 | PGS005270 | PGS005270 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 2/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.7941 | 0.7940 | 0.6412 | 0.7940 | 0.6412 | 0.6412 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Agent Input |
| trait_efo | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Agent Input |
| phenotyping_reported | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | PRSCS | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM022755 | PPM022754 | PPM022753 | PPM022754 | PPM022753 | PPM022753 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6054 | 0.6297 | 0.6387 | 0.6297 | 0.6387 | 0.6387 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.605418550899187} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.629725726511746} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638677809581895} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.629725726511746} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638677809581895} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638677809581895} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.41698139161814} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.348528828383883} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.54908058789994} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.437661585839951} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.037} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.037} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.54908058789994} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.437661585839951} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.037} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.037} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.037} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.037} | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=94,651 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | medRxiv | medRxiv | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | Agent Input |
| variants_number | 1085142 | 1085156 | 55 | 1085156 | 55 | 55 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Agent Input |


### preeclampsia

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003586 | PGS004593 | PGS003587 | PGS003586 | PGS003586 | PGS003586 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 1/3 | 1/3 | 1/3 | Benchmark Only |
| AoU benchmark AUC | 0.8077 | 0.7604 | 0.5709 | 0.8077 | 0.8077 | 0.8077 | Benchmark Only |
| Hit@1 | Yes | No | No | Yes | Yes | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Pre-eclampsia | Preeclampsia | Gestational hypertension | Pre-eclampsia | Pre-eclampsia | Pre-eclampsia | Agent Input |
| trait_efo | preeclampsia | preeclampsia | preeclampsia | preeclampsia | preeclampsia | preeclampsia | Agent Input |
| phenotyping_reported | Pre-eclampsia/eclampsia | Gestational hypertension | Pre-eclampsia/eclampsia | Pre-eclampsia/eclampsia | Pre-eclampsia/eclampsia | Pre-eclampsia/eclampsia | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM018280 | PPM020743 | PPM018281 | PPM018280 | PPM018280 | PPM018280 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.24, 'ci_upper': 1.38} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.14, 'ci_upper': 1.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.2, 'ci_lower': 1.14, 'ci_upper': 1.26} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.24, 'ci_upper': 1.38} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.24, 'ci_upper': 1.38} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.24, 'ci_upper': 1.38} | Agent Input |
| validation_sample_size | n=25,582 | n=138,317 | n=25,582 | n=25,582 | n=25,582 | n=25,582 | Agent Input |
| samples_training | n=212,034 | N/A | n=212,034 | n=212,034 | n=212,034 | n=212,034 | Agent Input |
| ancestry_distribution | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (1%), ASN (7%), EUR (91%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | N/A | BBJ BioMe EB FinnGen G&H MGBB UKB | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | Agent Input |
| publication.title | Polygenic prediction of preeclampsia and gestational hypertension. | Associations of polygenic risk scores for preeclampsia and blood pressure with hypertensive disorders of pregnancy. | Polygenic prediction of preeclampsia and gestational hypertension. | Polygenic prediction of preeclampsia and gestational hypertension. | Polygenic prediction of preeclampsia and gestational hypertension. | Polygenic prediction of preeclampsia and gestational hypertension. | Agent Input |
| publication.journal | Nat Med | J Hypertens | Nat Med | Nat Med | Nat Med | Nat Med | Agent Input |
| date_release | 2023-06-22 | 2024-01-26 | 2023-06-22 | 2023-06-22 | 2023-06-22 | 2023-06-22 | Agent Input |
| variants_number | 1087033 | 1102059 | 1087916 | 1087033 | 1087033 | 1087033 | Agent Input |
| covariates | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | Collection year, genotyping batch, and the first 10 genetic principal components | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | Agent Input |


### pulmonary fibrosis

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004695 | PGS001791 | PGS001030 | PGS001791 | PGS001030 | PGS001030 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 2/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.5512 | 0.5430 | 0.5394 | 0.5430 | 0.5394 | 0.5394 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Idiopathic pulmonary fibrosis | Idiopathic pulmonary fibrosis | Pulmonary fibrosis | Idiopathic pulmonary fibrosis | Pulmonary fibrosis | Pulmonary fibrosis | Agent Input |
| trait_efo | idiopathic pulmonary fibrosis | idiopathic pulmonary fibrosis | pulmonary fibrosis | idiopathic pulmonary fibrosis | pulmonary fibrosis | pulmonary fibrosis | Agent Input |
| phenotyping_reported | Incident idiopathic pulmonary fibrosis | Idiopathic pulmonary fibrosis | Pulmonary fibrosis | Idiopathic pulmonary fibrosis | Pulmonary fibrosis | Pulmonary fibrosis | Agent Input |
| method_name | Genome-wide significant SNPs | PRS-CS-auto | snpnet | PRS-CS-auto | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM020881 | PPM009295 | PPM007915 | PPM009295 | PPM007915 | PPM007915 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 5 | 1 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6252 | N/A | 0.6252 | 0.6252 | Agent Input |
| performance_metrics.r2 | N/A | 0.0059 | 0.0142 | 0.0059 | 0.0142 | 0.0142 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.7580 | 0.8015 | 0.7580 | 0.8015 | 0.8015 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0867 | N/A | 0.0867 | 0.0867 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0182 | N/A | 0.0182 | 0.0182 | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.758} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.80151, 'ci_lower': 0.7556, 'ci_upper': 0.84742} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.758} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.80151, 'ci_lower': 0.7556, 'ci_upper': 0.84742} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.80151, 'ci_lower': 0.7556, 'ci_upper': 0.84742} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Hazard ratio (HR, high vs low PRS quintile)', 'name_short': 'Hazard ratio (HR, high vs low PRS quintile)', 'estimate': 3.78, 'ci_lower': 3.3, 'ci_upper': 4.34} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.005929} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.08672} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01818} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0142} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.6252, 'ci_lower': 0.55618, 'ci_upper': 0.69423} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.005929} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.08672} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01818} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0142} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.6252, 'ci_lower': 0.55618, 'ci_upper': 0.69423} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.08672} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01818} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0142} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.6252, 'ci_lower': 0.55618, 'ci_upper': 0.69423} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=402,042 | n=347,350 | n=24,905 | n=347,350 | n=24,905 | n=24,905 | Agent Input |
| samples_training | N/A | N/A | n=269,704 | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (100%), ASN (3%), EAS (30%), EUR (65%), OTH (2%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: AFR (100%), ASN (3%), EAS (30%), EUR (65%), OTH (2%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | N/A | BBJ BioMe BioVU EB FinnGen G&H HUNT LifeLines MGBB MGI TWB UCLA | UKB | BBJ BioMe BioVU EB FinnGen G&H HUNT LifeLines MGBB MGI TWB UCLA | UKB | UKB | Agent Input |
| publication.title | Low-level ambient sulfur dioxide exposure and genetic susceptibility associated with incidence of idiopathic pulmonary fibrosis: A national prospective cohort study. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Chemosphere | Cell Genom | PLoS Genet | Cell Genom | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2024-03-18 | 2022-09-08 | 2021-10-21 | 2022-09-08 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 23 | 910439 | 51 | 910439 | 51 | 51 | Agent Input |
| covariates | Age, sex, education level, smoking status, pack-years of smoking, BMI | sex,age,age2,age*sex,age^2*sex, 20PCs | age, sex, UKB array type, Genotype PCs | sex,age,age2,age*sex,age^2*sex, 20PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### skin carcinoma in situ

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000471 | PGS000470 | PGS000469 | PGS000471 | PGS000471 | PGS000469 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 1/3 | 1/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.6010 | 0.5529 | 0.5041 | 0.6010 | 0.6010 | 0.5041 | Benchmark Only |
| Hit@1 | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Agent Input |
| trait_efo | skin carcinoma in situ | skin carcinoma in situ | skin carcinoma in situ | skin carcinoma in situ | skin carcinoma in situ | skin carcinoma in situ | Agent Input |
| phenotyping_reported | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Carcinoma in situ of skin | Agent Input |
| method_name | lassosum | Pruning and Thresholding (P+T) | PRS-CS | lassosum | lassosum | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM001156 | PPM001155 | PPM001154 | PPM001156 | PPM001156 | PPM001154 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5690 | 0.5570 | 0.5240 | 0.5690 | 0.5690 | 0.5240 | Agent Input |
| performance_metrics.full_model_r2 | 0.0255 | 0.0154 | 0.0014 | 0.0255 | 0.0255 | 0.0014 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.569, 'ci_lower': 0.541, 'ci_upper': 0.595} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.557, 'ci_lower': 0.531, 'ci_upper': 0.582} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.524, 'ci_lower': 0.499, 'ci_upper': 0.549} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.569, 'ci_lower': 0.541, 'ci_upper': 0.595} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.569, 'ci_lower': 0.541, 'ci_upper': 0.595} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.524, 'ci_lower': 0.499, 'ci_upper': 0.549} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0255} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0923} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.77, 'ci_lower': 2.24, 'ci_upper': 6.34} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0154} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.093} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.45, 'ci_lower': 1.34, 'ci_upper': 4.45} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.00141} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0939} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.48, 'ci_lower': 0.703, 'ci_upper': 3.1} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0255} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0923} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.77, 'ci_lower': 2.24, 'ci_upper': 6.34} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0255} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0923} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.77, 'ci_lower': 2.24, 'ci_upper': 6.34} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.00141} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0939} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.48, 'ci_lower': 0.703, 'ci_upper': 3.1} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.401, 'ci_lower': 1.297, 'ci_upper': 1.513} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.337, 'se': 0.0393} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.308, 'ci_lower': 1.208, 'ci_upper': 1.417} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.269, 'se': 0.0407} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.09, 'ci_lower': 1.001, 'ci_upper': 1.188} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.0865, 'se': 0.0437} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.401, 'ci_lower': 1.297, 'ci_upper': 1.513} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.337, 'se': 0.0393} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.401, 'ci_lower': 1.297, 'ci_upper': 1.513} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.337, 'se': 0.0393} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.09, 'ci_lower': 1.001, 'ci_upper': 1.188} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.0865, 'se': 0.0437} | Agent Input |
| validation_sample_size | n=5,500 | n=5,500 | n=5,500 | n=5,500 | n=5,500 | n=5,500 | Agent Input |
| samples_training | n=6,005 | n=6,005 | n=6,005 | n=6,005 | n=6,005 | n=6,005 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MGI | MGI | MGI | MGI | MGI | MGI | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-12-15 | Agent Input |
| variants_number | 7 | 5 | 1119238 | 7 | 7 | 1119238 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Agent Input |


### vitiligo

Candidate pool: `3` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000760 | PGS000738 | PGS001536 | PGS000738 | PGS001536 | PGS000738 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 2/3 | 3/3 | 2/3 | Benchmark Only |
| AoU benchmark AUC | 0.6417 | 0.6276 | 0.5669 | 0.6276 | 0.5669 | 0.6276 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 9/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Vitiligo | Vitiligo | Vitiligo (time-to-event) | Vitiligo | Vitiligo (time-to-event) | Vitiligo | Agent Input |
| trait_efo | Vitiligo | Vitiligo | Vitiligo | Vitiligo | Vitiligo | Vitiligo | Agent Input |
| phenotyping_reported | anti-PD-L1 induced hypothyroidism in cancer patients | Red hair | TTE vitiligo | Red hair | TTE vitiligo | Red hair | Agent Input |
| method_name | GCTA-COJO forward selection highest PPA variants | Genome-wide significant variants | snpnet | Genome-wide significant variants | snpnet | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM001935 | PPM018438 | PPM005219 | PPM018438 | PPM005219 | PPM018438 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 8 | 5 | 8 | 5 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6419 | N/A | 0.6419 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0162 | N/A | 0.0162 | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.6345 | N/A | 0.6345 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0386 | 0.0169 | 0.0386 | 0.0169 | 0.0386 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0816 | N/A | 0.0816 | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63449, 'ci_lower': 0.58754, 'ci_upper': 0.68144} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63449, 'ci_lower': 0.58754, 'ci_upper': 0.68144} | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'meta-analysis p-value', 'name_short': 'meta-analysis p-value', 'estimate': 1.1e-06} | {'name_long': 'pseudo R²', 'name_short': 'pseudo R²', 'estimate': 0.038569956} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01686} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08163} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01621} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64193, 'ci_lower': 0.59907, 'ci_upper': 0.68478} | {'name_long': 'pseudo R²', 'name_short': 'pseudo R²', 'estimate': 0.038569956} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01686} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08163} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01621} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64193, 'ci_lower': 0.59907, 'ci_upper': 0.68478} | {'name_long': 'pseudo R²', 'name_short': 'pseudo R²', 'estimate': 0.038569956} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.41, 'ci_lower': 1.22, 'ci_upper': 1.61} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.694777831} | N/A | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.694777831} | N/A | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.694777831} | Agent Input |
| validation_sample_size | n=1,584 | n=4,702 | n=67,425 | n=4,702 | n=67,425 | n=4,702 | Agent Input |
| samples_training | n=408,959 | N/A | n=269,704 | N/A | n=269,704 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | N/A | UKB | N/A | UKB | N/A | Agent Input |
| publication.title | Genetic variation associated with thyroid autoimmunity shapes the systemic immune response to PD-1 checkpoint blockade. | Family Clustering of Autoimmune Vitiligo Results Principally from Polygenic Inheritance of Common Risk Alleles. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Family Clustering of Autoimmune Vitiligo Results Principally from Polygenic Inheritance of Common Risk Alleles. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Family Clustering of Autoimmune Vitiligo Results Principally from Polygenic Inheritance of Common Risk Alleles. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | PLoS Genet | Am J Hum Genet | PLoS Genet | Am J Hum Genet | Agent Input |
| date_release | 2021-06-11 | 2021-02-23 | 2021-11-25 | 2021-02-23 | 2021-11-25 | 2021-02-23 | Agent Input |
| variants_number | 42 | 48 | 77 | 48 | 77 | 48 | Agent Input |
| covariates | 5 genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | Unknown | Agent Input |


### autism spectrum disorder

Candidate pool: `2` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002790 | PGS000327 | PGS000327 | PGS000327 | PGS000327 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 2/2 | 2/2 | 2/2 | Benchmark Only |
| AoU benchmark AUC | 0.6024 | 0.5670 | 0.5670 | 0.5670 | 0.5670 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Autism spectrum disorder | Autism spectrum disorder | Autism spectrum disorder | Autism spectrum disorder | Autism spectrum disorder | Agent Input |
| trait_efo | autism spectrum disorder | autism spectrum disorder | autism spectrum disorder | autism spectrum disorder | autism spectrum disorder | Agent Input |
| phenotyping_reported | Psychiatric behavior (withdrawn) | Autism spectrum disorder | Autism spectrum disorder | Autism spectrum disorder | Autism spectrum disorder | Agent Input |
| method_name | SDPR | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM015334 | PPM000879 | PPM000879 | PPM000879 | PPM000879 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 50 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0055 | 0.0245 | 0.0245 | 0.0245 | 0.0245 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00546477739838} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0245} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0245} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0245} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0245} | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33, 'ci_lower': 1.3, 'ci_upper': 1.36} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33, 'ci_lower': 1.3, 'ci_upper': 1.36} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33, 'ci_lower': 1.3, 'ci_upper': 1.36} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33, 'ci_lower': 1.3, 'ci_upper': 1.36} | Agent Input |
| validation_sample_size | n=2,198 | n=7,148 | n=7,148 | n=7,148 | n=7,148 | Agent Input |
| samples_training | N/A | n=28,592 | n=28,592 | n=28,592 | n=28,592 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | PGC iPSYCH | ACE AGP AGRE MONBOS NIMH PGC SSC iPSYCH | ACE AGP AGRE MONBOS NIMH PGC SSC iPSYCH | ACE AGP AGRE MONBOS NIMH PGC SSC iPSYCH | ACE AGP AGRE MONBOS NIMH PGC SSC iPSYCH | Agent Input |
| publication.title | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Identification of common genetic risk variants for autism spectrum disorder. | Identification of common genetic risk variants for autism spectrum disorder. | Identification of common genetic risk variants for autism spectrum disorder. | Identification of common genetic risk variants for autism spectrum disorder. | Agent Input |
| publication.journal | Transl Psychiatry | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2022-09-29 | 2020-09-18 | 2020-09-18 | 2020-09-18 | 2020-09-18 | Agent Input |
| variants_number | 916713 | 35087 | 35087 | 35087 | 35087 | Agent Input |
| covariates | age, PCs1-3 | Genetic PCs, genotyping wave | Genetic PCs, genotyping wave | Genetic PCs, genotyping wave | Genetic PCs, genotyping wave | Agent Input |


### congenital vitamin k-dependent coagulation factors deficiency

Candidate pool: `2` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001826 | PGS002034 | PGS002034 | PGS002034 | PGS001826 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 2/2 | 2/2 | 1/2 | Benchmark Only |
| AoU benchmark AUC | 0.7917 | 0.7841 | 0.7841 | 0.7841 | 0.7917 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Congenital deficiency of other clotting factors (including factor VII) | Congenital deficiency of other clotting factors (including factor VII) | Congenital deficiency of other clotting factors (including factor VII) | Congenital deficiency of other clotting factors (including factor VII) | Congenital deficiency of other clotting factors (including factor VII) | Agent Input |
| trait_efo | congenital vitamin K-dependent coagulation factors deficiency | congenital vitamin K-dependent coagulation factors deficiency | congenital vitamin K-dependent coagulation factors deficiency | congenital vitamin K-dependent coagulation factors deficiency | congenital vitamin K-dependent coagulation factors deficiency | Agent Input |
| phenotyping_reported | Congenital deficiency of other clotting factors (including factor VII) | Congenital deficiency of other clotting factors (including factor VII) | Congenital deficiency of other clotting factors (including factor VII) | Congenital deficiency of other clotting factors (including factor VII) | Congenital deficiency of other clotting factors (including factor VII) | Agent Input |
| method_name | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | LDpred2 (bigsnpr) | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | Agent Input |
| performance_metrics.selected_performance_id | PPM009505 | PPM011143 | PPM011143 | PPM011143 | PPM009505 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 4 | 4 | 4 | 4 | 4 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0562, 'ci_lower': 0.0424, 'ci_upper': 0.0701} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0563, 'ci_lower': 0.0424, 'ci_upper': 0.0702} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0563, 'ci_lower': 0.0424, 'ci_upper': 0.0702} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0563, 'ci_lower': 0.0424, 'ci_upper': 0.0702} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0562, 'ci_lower': 0.0424, 'ci_upper': 0.0701} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,864 | n=19,864 | n=19,864 | n=19,864 | n=19,864 | Agent Input |
| samples_training | n=391,124 | n=391,124 | n=391,124 | n=391,124 | n=391,124 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (75%), SAS (25%) | DEV: EUR (100%) / EVAL: EUR (75%), SAS (25%) | DEV: EUR (100%) / EVAL: EUR (75%), SAS (25%) | DEV: EUR (100%) / EVAL: EUR (75%), SAS (25%) | DEV: EUR (100%) / EVAL: EUR (75%), SAS (25%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2022-01-10 | 2022-01-10 | 2022-01-10 | 2022-01-10 | 2022-01-10 | Agent Input |
| variants_number | 45 | 32552 | 32552 | 32552 | 45 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Agent Input |


### corneal dystrophy

Candidate pool: `2` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002042 | PGS001835 | PGS002042 | PGS002042 | PGS001835 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 1/2 | 1/2 | 2/2 | Benchmark Only |
| AoU benchmark AUC | 0.7255 | 0.6968 | 0.7255 | 0.7255 | 0.6968 | Benchmark Only |
| Hit@1 | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Corneal dystrophy | Corneal dystrophy | Corneal dystrophy | Corneal dystrophy | Corneal dystrophy | Agent Input |
| trait_efo | corneal dystrophy | corneal dystrophy | corneal dystrophy | corneal dystrophy | corneal dystrophy | Agent Input |
| phenotyping_reported | Corneal dystrophy | Corneal dystrophy | Corneal dystrophy | Corneal dystrophy | Corneal dystrophy | Agent Input |
| method_name | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | Agent Input |
| performance_metrics.selected_performance_id | PPM011202 | PPM009572 | PPM011202 | PPM011202 | PPM009572 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 6 | 6 | 6 | 6 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0471, 'ci_lower': 0.033, 'ci_upper': 0.0611} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0384, 'ci_lower': 0.0243, 'ci_upper': 0.0525} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0471, 'ci_lower': 0.033, 'ci_upper': 0.0611} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0471, 'ci_lower': 0.033, 'ci_upper': 0.0611} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0384, 'ci_lower': 0.0243, 'ci_upper': 0.0525} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,321 | n=19,321 | n=19,321 | n=19,321 | n=19,321 | Agent Input |
| samples_training | n=391,124 | n=391,124 | n=391,124 | n=391,124 | n=391,124 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (17%), EUR (50%), GME (17%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (17%), EUR (50%), GME (17%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (17%), EUR (50%), GME (17%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (17%), EUR (50%), GME (17%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (17%), EUR (50%), GME (17%), SAS (17%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2022-01-10 | 2022-01-10 | 2022-01-10 | 2022-01-10 | 2022-01-10 | Agent Input |
| variants_number | 59944 | 38 | 59944 | 59944 | 38 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Agent Input |


### iron metabolism disease

Candidate pool: `2` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002031 | PGS001823 | PGS002031 | PGS002031 | PGS001823 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 1/2 | 1/2 | 2/2 | Benchmark Only |
| AoU benchmark AUC | 0.5661 | 0.5608 | 0.5661 | 0.5661 | 0.5608 | Benchmark Only |
| Hit@1 | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Disorders of iron metabolism | Disorders of iron metabolism | Disorders of iron metabolism | Disorders of iron metabolism | Disorders of iron metabolism | Agent Input |
| trait_efo | iron metabolism disease | iron metabolism disease | iron metabolism disease | iron metabolism disease | iron metabolism disease | Agent Input |
| phenotyping_reported | Disorders of iron metabolism | Disorders of iron metabolism | Disorders of iron metabolism | Disorders of iron metabolism | Disorders of iron metabolism | Agent Input |
| method_name | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | Agent Input |
| performance_metrics.selected_performance_id | PPM011122 | PPM009484 | PPM011122 | PPM011122 | PPM009484 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 6 | 6 | 6 | 6 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.1355, 'ci_lower': 0.1219, 'ci_upper': 0.1492} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.1307, 'ci_lower': 0.117, 'ci_upper': 0.1444} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.1355, 'ci_lower': 0.1219, 'ci_upper': 0.1492} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.1355, 'ci_lower': 0.1219, 'ci_upper': 0.1492} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.1307, 'ci_lower': 0.117, 'ci_upper': 0.1444} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,883 | n=19,883 | n=19,883 | n=19,883 | n=19,883 | Agent Input |
| samples_training | n=391,124 | n=391,124 | n=391,124 | n=391,124 | n=391,124 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (17%), EAS (17%), EUR (50%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (17%), EAS (17%), EUR (50%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (17%), EAS (17%), EUR (50%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (17%), EAS (17%), EUR (50%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (17%), EAS (17%), EUR (50%), SAS (17%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2022-01-10 | 2022-01-10 | 2022-01-10 | 2022-01-10 | 2022-01-10 | Agent Input |
| variants_number | 6713 | 654 | 6713 | 6713 | 654 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Agent Input |


### nasal cavity polyp

Candidate pool: `2` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004465 | PGS004535 | PGS004535 | PGS004535 | PGS004465 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 2/2 | 2/2 | 1/2 | Benchmark Only |
| AoU benchmark AUC | 0.5568 | 0.5498 | 0.5498 | 0.5498 | 0.5568 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | J33 (Nasal polyp) | J33 (Nasal polyp) | J33 (Nasal polyp) | J33 (Nasal polyp) | J33 (Nasal polyp) | Agent Input |
| trait_efo | Nasal Cavity Polyp | Nasal Cavity Polyp | Nasal Cavity Polyp | Nasal Cavity Polyp | Nasal Cavity Polyp | Agent Input |
| phenotyping_reported | J33 (Nasal polyp) | J33 (Nasal polyp) | J33 (Nasal polyp) | J33 (Nasal polyp) | J33 (Nasal polyp) | Agent Input |
| method_name | LDpred2 | RFDiseasemetaPRS | RFDiseasemetaPRS | RFDiseasemetaPRS | LDpred2 | Agent Input |
| performance_metrics.selected_performance_id | PPM020580 | PPM020650 | PPM020650 | PPM020650 | PPM020580 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.34960380988905} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.600668} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.600668} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.600668} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.34960380988905} | Agent Input |
| validation_sample_size | n=56,192 | n=56,192 | n=56,192 | n=56,192 | n=56,192 | Agent Input |
| samples_training | n=174,489 | n=174,489 | n=174,489 | n=174,489 | n=174,489 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Agent Input |
| publication.journal | Commun Biol | Commun Biol | Commun Biol | Commun Biol | Commun Biol | Agent Input |
| date_release | 2024-03-18 | 2024-03-18 | 2024-03-18 | 2024-03-18 | 2024-03-18 | Agent Input |
| variants_number | 1059939 | 1059939 | 1059939 | 1059939 | 1059939 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | Agent Input |


### nicotine dependence

Candidate pool: `2` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002037 | PGS001830 | PGS002037 | PGS002037 | PGS001830 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 1/2 | 1/2 | 2/2 | Benchmark Only |
| AoU benchmark AUC | 0.5974 | 0.5707 | 0.5974 | 0.5974 | 0.5707 | Benchmark Only |
| Hit@1 | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Tobacco use disorder | Tobacco use disorder | Tobacco use disorder | Tobacco use disorder | Tobacco use disorder | Agent Input |
| trait_efo | nicotine dependence | nicotine dependence | nicotine dependence | nicotine dependence | nicotine dependence | Agent Input |
| phenotyping_reported | Tobacco use disorder | Tobacco use disorder | Tobacco use disorder | Tobacco use disorder | Tobacco use disorder | Agent Input |
| method_name | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | Agent Input |
| performance_metrics.selected_performance_id | PPM011163 | PPM009533 | PPM011163 | PPM011163 | PPM009533 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 11 | 8 | 11 | 11 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0741, 'ci_lower': 0.0601, 'ci_upper': 0.0881} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0557, 'ci_lower': 0.0416, 'ci_upper': 0.0697} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0741, 'ci_lower': 0.0601, 'ci_upper': 0.0881} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0741, 'ci_lower': 0.0601, 'ci_upper': 0.0881} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0557, 'ci_lower': 0.0416, 'ci_upper': 0.0697} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,400 | n=19,400 | n=19,400 | n=19,400 | n=19,400 | Agent Input |
| samples_training | n=391,124 | n=391,124 | n=391,124 | n=391,124 | n=391,124 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (18%), AMR (9%), EAS (18%), EUR (36%), GME (9%), SAS (9%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (18%), AMR (9%), EAS (18%), EUR (36%), GME (9%), SAS (9%) | DEV: EUR (100%) / EVAL: AFR (18%), AMR (9%), EAS (18%), EUR (36%), GME (9%), SAS (9%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2022-01-10 | 2022-01-10 | 2022-01-10 | 2022-01-10 | 2022-01-10 | Agent Input |
| variants_number | 847691 | 13838 | 847691 | 847691 | 13838 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Agent Input |


### otosclerosis

Candidate pool: `2` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002046 | PGS001255 | PGS002046 | PGS001255 | PGS001255 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 1/2 | 2/2 | 2/2 | Benchmark Only |
| AoU benchmark AUC | 0.6377 | 0.6276 | 0.6377 | 0.6276 | 0.6276 | Benchmark Only |
| Hit@1 | Yes | No | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 7/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Otosclerosis | Otosclerosis (time-to-event) | Otosclerosis | Otosclerosis (time-to-event) | Otosclerosis (time-to-event) | Agent Input |
| trait_efo | otosclerosis | otosclerosis | otosclerosis | otosclerosis | otosclerosis | Agent Input |
| phenotyping_reported | Otosclerosis | TTE otosclerosis | Otosclerosis | TTE otosclerosis | TTE otosclerosis | Agent Input |
| method_name | LDpred2 (bigsnpr) | snpnet | LDpred2 (bigsnpr) | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM011232 | PPM008784 | PPM011232 | PPM008784 | PPM008784 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 6 | 4 | 6 | 4 | 4 | Agent Input |
| performance_metrics.auc | N/A | 0.6319 | N/A | 0.6319 | 0.6319 | Agent Input |
| performance_metrics.r2 | N/A | 0.0134 | N/A | 0.0134 | 0.0134 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.6532 | N/A | 0.6532 | 0.6532 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0209 | N/A | 0.0209 | 0.0209 | Agent Input |
| performance_metrics.incremental_auc | N/A | 0.0595 | N/A | 0.0595 | 0.0595 | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6532, 'ci_lower': 0.60975, 'ci_upper': 0.69665} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6532, 'ci_lower': 0.60975, 'ci_upper': 0.69665} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6532, 'ci_lower': 0.60975, 'ci_upper': 0.69665} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0182, 'ci_lower': 0.0043, 'ci_upper': 0.0321} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.02085} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05946} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01341} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.6319, 'ci_lower': 0.58724, 'ci_upper': 0.67656} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0182, 'ci_lower': 0.0043, 'ci_upper': 0.0321} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.02085} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05946} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01341} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.6319, 'ci_lower': 0.58724, 'ci_upper': 0.67656} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.02085} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05946} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01341} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.6319, 'ci_lower': 0.58724, 'ci_upper': 0.67656} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,770 | n=67,425 | n=19,770 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=269,704 | n=391,124 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (17%), EUR (50%), GME (17%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (17%), EUR (50%), GME (17%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | Am J Hum Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2021-10-21 | 2022-01-10 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 570308 | 213 | 570308 | 213 | 213 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |

