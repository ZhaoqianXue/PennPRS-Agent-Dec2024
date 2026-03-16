# Without Domain Knowledge: Per-Disease Comparison

## Scope

This report is a disease-by-disease comparison built from the without-domain experiment summary and the underlying AoU benchmark matrices.

Field Type labels in the last column indicate whether a row is part of the current agent input (`Agent Input`) or post-hoc evaluation metadata used only for benchmark/experiment analysis (`Benchmark Only`).

Each disease table includes the benchmark top-ranked models `Benchmark #1..#5` (or fewer when the disease has fewer than 5 evaluated models).
Rows `Hit@1`..`Hit@5` use eligible-only denominators; diseases with fewer than `k` evaluated models are marked `N/A` for `Hit@k`.

## High-Level Outcome

- Without Domain Knowledge `Hit@1`: `16/60 = 26.67%`; `trial_hits = 157/600 = 26.17%`
- Without Domain Knowledge `Hit@2`: `23/60 = 38.33%`; `trial_hits = 224/600 = 37.33%`
- Without Domain Knowledge `Hit@3`: `24/54 = 44.44%`; `trial_hits = 231/540 = 42.78%`
- Without Domain Knowledge `Hit@4`: `22/48 = 45.83%`; `trial_hits = 218/480 = 45.42%`
- Without Domain Knowledge `Hit@5`: `20/43 = 46.51%`; `trial_hits = 192/430 = 44.65%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Without Domain Knowledge: `mean r / M = 0.4953` (60 modal selections); `trial mean r / M = 0.5007` (600 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Without Domain Knowledge: `mean (M - r) / M = 0.5047` (60 modal selections); `trial mean (M - r) / M = 0.4993` (600 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Without Domain Knowledge: `mean NRS = 0.5873` (60 modal selections); `trial mean NRS = 0.5807` (600 trials)


## Per-Disease Tables

### hypertension

Candidate pool: `258` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004787 | PGS004786 | PGS004788 | PGS004785 | PGS002335 | PGS001320 | Agent Input |
| AoU benchmark rank | 1/258 | 2/258 | 3/258 | 4/258 | 5/258 | 12/258 | Benchmark Only |
| AoU benchmark AUC | 0.6460 | 0.6377 | 0.6377 | 0.6298 | 0.6227 | 0.6063 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 5/10 trials | Benchmark Only |
| trait_reported | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Agent Input |
| trait_efo | hypertension | hypertension | hypertension | hypertension | hypertension | hypertension | Agent Input |
| phenotyping_reported | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Hypertension | Agent Input |
| method_name | PRSmixPlus | PRSmix | PRSmixPlus | PRSmix | BOLT-LMM | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM021012 | PPM021011 | PPM021013 | PPM021010 | PPM013198 | PPM009096 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | South Asian | South Asian | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 4 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | 0.6291 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0649 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | 0.7189 | Agent Input |
| performance_metrics.full_model_r2 | 0.0730 | 0.0220 | 0.0270 | 0.0660 | 0.0527 | 0.1785 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | 0.0442 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7189, 'ci_lower': 0.71489, 'ci_upper': 0.72291} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.073, 'ci_lower': 0.063, 'ci_upper': 0.083} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.022, 'ci_lower': 0.016, 'ci_upper': 0.028} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.027, 'ci_lower': 0.02, 'ci_upper': 0.033} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.066, 'ci_lower': 0.056, 'ci_upper': 0.076} | {'name_long': 'Incremental R2 (full model vs. covariates alone)', 'name_short': 'Incremental R2 (full model vs. covariates alone)', 'estimate': 0.0527} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.17852} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04424} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.06493} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62908, 'ci_lower': 0.62467, 'ci_upper': 0.63349} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=9,462 | n=8,837 | n=8,837 | n=9,462 | n=43,392 | n=67,425 | Agent Input |
| samples_training | n=37,851 | n=35,350 | n=35,350 | n=37,851 | N/A | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: SAS (100%) / EVAL: SAS (100%) | DEV: SAS (100%) / EVAL: SAS (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: AFR (25%), EAS (25%), EUR (25%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs | G&H | G&H | AllofUs | UKB | UKB | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Leveraging fine-mapping and multipopulation training data to improve cross-population polygenic risk scores. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | Cell Genom | Cell Genom | Nat Genet | PLoS Genet | Agent Input |
| date_release | 2024-03-28 | 2024-03-28 | 2024-03-28 | 2024-03-28 | 2022-06-09 | 2021-10-21 | Agent Input |
| variants_number | 5191115 | 6622611 | 6622611 | 1170615 | 1109311 | 13791 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, age*sex, assessment center, genotyping array, 10 PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### breast carcinoma

Candidate pool: `164` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004579 | PGS000508 | PGS004025 | PGS004053 | PGS000335 | PGS004153 | Agent Input |
| AoU benchmark rank | 1/163 | 2/163 | 3/163 | 4/163 | 5/163 | 6/163 | Benchmark Only |
| AoU benchmark AUC | 0.6358 | 0.6335 | 0.6332 | 0.6326 | 0.6319 | 0.6310 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 7/10 trials | Benchmark Only |
| trait_reported | Breast cancer | Breast cancer (female) | Breast cancer | Breast cancer | Breast cancer | Breast cancer | Agent Input |
| trait_efo | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | breast carcinoma | Agent Input |
| phenotyping_reported | Breast cancer | Breast cancer [female] | Breast cancer | Breast cancer | Breast cancer | Breast cancer | Agent Input |
| method_name | PRS-CS | PRS-CS | LDpred2-auto | megaprs.auto | PRS-CS | UKBB-EUR.MultiPRS.CV | Agent Input |
| performance_metrics.selected_performance_id | PPM020694 | PPM001193 | PPM019406 | PPM019418 | PPM000902 | PPM019388 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 6 | 6 | 13 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.6520 | 0.6598 | 0.6530 | N/A | 0.6625 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0548 | 0.0736 | 0.0677 | N/A | 0.0764 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.652, 'ci_lower': 0.645, 'ci_upper': 0.658} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65975886, 'ci_lower': 0.65001199, 'ci_upper': 0.66950573} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65298774, 'ci_lower': 0.64321086, 'ci_upper': 0.66276462} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66250277, 'ci_lower': 0.65279453, 'ci_upper': 0.67221102} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0548} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0805} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.38, 'ci_lower': 3.79, 'ci_upper': 5.07} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07358668, 'ci_lower': 0.06487413, 'ci_upper': 0.08290854} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.06765484, 'ci_lower': 0.05919841, 'ci_upper': 0.07667134} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07640178, 'ci_lower': 0.06786928, 'ci_upper': 0.08556093} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.79} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.756, 'ci_lower': 1.709, 'ci_upper': 1.804} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.563, 'se': 0.0138} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.80647225, 'ci_lower': 1.73980278, 'ci_upper': 1.87569651} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.59137591, 'ci_lower': 0.55377176, 'ci_upper': 0.62898006} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.75979222, 'ci_lower': 1.69513119, 'ci_upper': 1.82691975} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.56519574, 'ci_lower': 0.52776014, 'ci_upper': 0.60263135} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.71, 'ci_lower': 1.68, 'ci_upper': 1.75} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.82571574, 'ci_lower': 1.75833364, 'ci_upper': 1.89568002} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.60197209, 'ci_lower': 0.56436656, 'ci_upper': 0.63957762} | Agent Input |
| validation_sample_size | n=190,879 | n=68,531 | n=48,968 | n=48,968 | n=122,978 | n=48,968 | Agent Input |
| samples_training | N/A | n=68,451 | n=12,483 | n=12,483 | N/A | n=12,483 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | Agent Input |
| training_development_cohorts | N/A | UKB | UKB | UKB | N/A | UKB | Agent Input |
| publication.title | High-Resolution Genotyping of Formalin-Fixed Tissue Accurately Estimates Polygenic Risk Scores in Human Diseases. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | The role of polygenic risk and susceptibility genes in breast cancer over the course of life | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Agent Input |
| publication.journal | Lab Invest | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Nat Commun | Am J Hum Genet | Agent Input |
| date_release | 2024-02-20 | 2020-12-15 | 2023-12-19 | 2023-12-19 | 2020-12-15 | 2023-12-19 | Agent Input |
| variants_number | 1088163 | 1120410 | 1041298 | 869407 | 1079089 | 1133268 | Agent Input |
| covariates | Unknown | age, sex, batch PCs 1-4 | 0 | 0 | 10 ancestry PCs, batch, age as time scale | 0 | Agent Input |


### melanoma

Candidate pool: `103` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003382 | PGS003430 | PGS002246 | PGS002247 | PGS005208 | PGS000079 | Agent Input |
| AoU benchmark rank | 1/103 | 2/103 | 3/103 | 4/103 | 5/103 | 22/103 | Benchmark Only |
| AoU benchmark AUC | 0.6239 | 0.5994 | 0.5983 | 0.5967 | 0.5960 | 0.5664 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 5/10 trials | Benchmark Only |
| trait_reported | Skin cutaneous melanoma | Melanoma | Melanoma | Melanoma | Melanoma | Melanoma | Agent Input |
| trait_efo | cutaneous melanoma | melanoma | melanoma | melanoma | melanoma | melanoma | Agent Input |
| phenotyping_reported | skin cutaneous melanoma | Melanoma | Incident invasive melanoma | Incident invasive melanoma | Risk of melanoma in childhood cancer survivors | Incident melanoma | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Maximum clumping and thresholding (maxCT) | Genome-wide significant variants | Genome-wide significant variants | Genome-wide significant SNPs | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM016257 | PPM017104 | PPM012822 | PPM012821 | PPM022589 | PPM002045 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 4 | 4 | 1 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6820 | 0.6340 | 0.6880 | 0.6910 | N/A | 0.6520 | Agent Input |
| performance_metrics.full_model_r2 | 0.0261 | N/A | 0.0700 | 0.0720 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.682} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.634, 'ci_lower': 0.618, 'ci_upper': 0.661} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.688, 'ci_lower': 0.657, 'ci_upper': 0.718} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.691, 'ci_lower': 0.661, 'ci_upper': 0.722} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.652} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.663, 'se': 0.008} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0261} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07, 'ci_lower': 0.048, 'ci_upper': 0.096} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.072, 'ci_lower': 0.051, 'ci_upper': 0.1} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.6, 'ci_lower': 1.31, 'ci_upper': 1.67} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.43, 'ci_lower': 1.36, 'ci_upper': 1.49} | Agent Input |
| validation_sample_size | n=273,786 | n=109,597 | n=4,765 | n=4,765 | n=11,220 | n=392,803 | Agent Input |
| samples_training | N/A | n=16,434 | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | GenoMEL UKB | N/A | N/A | MIA | 23andMe AMFS BATS HPFS MDACCS NHS Q-MEGA QIMR | Agent Input |
| publication.title | Common germline risk variants impact somatic alterations and clinical features across cancers. | Melanoma risk prediction based on a polygenic risk score and clinical risk factors. | Independent evaluation of melanoma polygenic risk scores in UK and Australian prospective cohorts. | Independent evaluation of melanoma polygenic risk scores in UK and Australian prospective cohorts. | Polygenic risk scores, radiation treatment exposures and subsequent cancer risk in childhood cancer survivors. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Cancer Res | Melanoma Res | Br J Dermatol | Br J Dermatol | Nat Med | Nat Commun | Agent Input |
| date_release | 2023-01-19 | 2023-10-17 | 2022-02-16 | 2022-02-16 | 2025-05-20 | 2020-02-12 | Agent Input |
| variants_number | 672 | 68 | 50 | 68 | 67 | 24 | Agent Input |
| covariates | age, sex, top 20 genetic principal components | Unknown | age, sex | age, sex | childhood cancer diagnosis, ancestry, age at childhood cancer diagnosis, radiation dose to the body region of the second cancer and chemotherapy exposure | Age at assessment, sex, genotyping array, PCs(1-15), frequency of UV protection use (always vs. most times vs. never out in the sun vs. never), time outdoors in summer (hours per day), ease of tanning (very easily, vs. moderate vs mild vs. mostly burn) | Agent Input |


### prostate cancer

Candidate pool: `96` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000566 | PGS000044 | PGS001292 | PGS000592 | PGS002793 | PGS005238 | Agent Input |
| AoU benchmark rank | 1/95 | 2/95 | 3/95 | 4/95 | 5/95 | 51/95 | Benchmark Only |
| AoU benchmark AUC | 0.6550 | 0.6295 | 0.6041 | 0.5748 | 0.5665 | 0.5402 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Prostate cancer | Prostate cancer | Family history of prostate cancer | Prostate cancer | Prostate cancer | Prostate carcinoma | Agent Input |
| trait_efo | prostate carcinoma | prostate carcinoma | family history of prostate cancer | prostate carcinoma | prostate carcinoma | prostate carcinoma | Agent Input |
| phenotyping_reported | Cancer of prostate | Elevated serum prostate-specific antigen (PSA) levels | Prostate cancer (FH) | Cancer of prostate | Prostate cancer risk | 5-year incident prostate cancer | Agent Input |
| method_name | PRS-CS | Known susceptibility loci (genome-wide significant SNPs) | snpnet | lassosum | Genome-wide significant SNPs | LDpred2 | Agent Input |
| performance_metrics.selected_performance_id | PPM001251 | PPM000104 | PPM008960 | PPM001277 | PPM015450 | PPM022696 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | East Asian | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 5 | 1 | 1 | 10 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.5487 | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0055 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5910 | N/A | 0.5657 | 0.6160 | N/A | 0.7890 | Agent Input |
| performance_metrics.full_model_r2 | 0.0245 | N/A | 0.0115 | 0.0408 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0170 | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.591, 'ci_lower': 0.573, 'ci_upper': 0.609} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.56572, 'ci_lower': 0.5538, 'ci_upper': 0.57764} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.616, 'ci_lower': 0.598, 'ci_upper': 0.635} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.789, 'ci_lower': 0.782, 'ci_upper': 0.796} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0245} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.152} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.85, 'ci_lower': 1.76, 'ci_upper': 4.62} | {'name_long': 'OR (per 1-point increase in PRS)', 'name_short': 'OR (per 1-point increase in PRS)', 'estimate': 1.23, 'ci_lower': 1.1, 'ci_upper': 1.37} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01155} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01702} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00547} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.54869, 'ci_lower': 0.53677, 'ci_upper': 0.56062} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0408} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.15} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.55, 'ci_lower': 1.55, 'ci_upper': 4.2} | {'name_long': 'Odds Ratio (OR, top vs average percentile)', 'name_short': 'Odds Ratio (OR, top vs average percentile)', 'estimate': 2.87, 'ci_lower': 1.29, 'ci_upper': 6.4} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.393, 'ci_lower': 1.3, 'ci_upper': 1.493} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.332, 'se': 0.0352} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.537, 'ci_lower': 1.433, 'ci_upper': 1.648} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.43, 'se': 0.0357} | N/A | N/A | Agent Input |
| validation_sample_size | n=5,607 | n=17,012 | n=24,905 | n=5,607 | n=1,190 | n=184,010 | Agent Input |
| samples_training | n=5,650 | N/A | n=269,704 | n=5,650 | n=109,323 | n=10,000 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (5%), EUR (95%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (2%), AMR (40%), EAS (1%), EUR (92%), MAE (3%) / DEV: AFR (3%), EAS (1%), EUR (96%) / EVAL: EAS (100%) | GWAS: AFR (9%), AMR (3%), EAS (12%), EUR (76%) / DEV: EUR (100%) / EVAL: AFR (20%), EUR (60%), SAS (20%) | Agent Input |
| training_development_cohorts | MGI | ICR IGD PLCO ProtecT UKGPCS deCODE | UKB | MGI | AAPC BCFR BFBOCC BRICOH CBCS CIMBA CNIO CONSIT Chicago DEMOKRITOS DKFZ EMBRACE FCCC G-FaST GC-HBOC GEMO HCSC HEBCS HEBON HUNBOCS HVH ICO ICR IGD ILUH IOVHBOCS IPOBCS MAYO MSKCC MUV NCI OCGN OSU OUH PBCS PLCO ProtecT SWE-BRCA UKB UKGPCS UPENN UPITT VFCTG deCODE kConFab | UKB | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Reducing overdiagnosis by polygenic risk-stratified screening: findings from the Finnish section of the ERSPC. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Application of European-specific polygenic risk scores for predicting prostate cancer risk in different ancestry populations. | Polygenic risk scores for prostate cancer: Comparative evaluations in UK and Australian cohorts. | Agent Input |
| publication.journal | Am J Hum Genet | Br J Cancer | PLoS Genet | Am J Hum Genet | Prostate | HGG Adv | Agent Input |
| date_release | 2020-12-15 | 2019-12-18 | 2021-10-21 | 2020-12-15 | 2022-09-29 | 2025-10-06 | Agent Input |
| variants_number | 1111494 | 66 | 602 | 1334 | 82 | 964607 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | cancer stage, Gleason score | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | disease diagnostic age or age at recruitment, subgroups and 10 principal components | Age-specific absolute risk adjusted by PGS relative risk | Agent Input |


### coronary artery disease

Candidate pool: `85` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005091 | PGS003725 | PGS004696 | PGS004745 | PGS004697 | PGS000013 | Agent Input |
| AoU benchmark rank | 1/85 | 2/85 | 3/85 | 4/85 | 5/85 | 31/85 | Benchmark Only |
| AoU benchmark AUC | 0.6207 | 0.6207 | 0.6160 | 0.6153 | 0.6140 | 0.5764 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 3/10 trials | Benchmark Only |
| trait_reported | Coronary artery disease | Coronary artery disease | Coronary heart disease | Coronary artery disease | Coronary heart disease | Coronary artery disease | Agent Input |
| trait_efo | coronary artery disease | coronary artery disease | coronary artery disease | coronary artery disease | coronary artery disease | coronary artery disease | Agent Input |
| phenotyping_reported | Prevalent coronary heart disease | Coronary artery disease | Incident coronary heart disease | Coronary artery disease | Incident coronary heart disease | Coronary artery disease | Agent Input |
| method_name | LDPred2Auto | LDpred2 | PRS-CSx | PRSmixPlus | PRS-CSx | LDpred | Agent Input |
| performance_metrics.selected_performance_id | PPM022179 | PPM018419 | PPM020904 | PPM020970 | PPM020903 | PPM000022 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African unspecified, Hispanic or Latin American, East Asian, South Asian, Not reported | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 3 | 11 | 5 | 1 | 5 | 50 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0400 | Agent Input |
| performance_metrics.full_model_auc | 0.8000 | N/A | 0.7740 | N/A | 0.7730 | 0.8100 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0500 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.774} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.773} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.81, 'ci_lower': 0.81, 'ci_upper': 0.81} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.143} | N/A | N/A | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.05, 'ci_lower': 0.04, 'ci_upper': 0.059} | N/A | {'name_long': 'Nagelkerke’s R2 (estimate of variance explained by the PGS after covariate adjustment)', 'name_short': 'Nagelkerke’s R2 (estimate of variance explained by the PGS after covariate adjustment)', 'estimate': 0.04} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.374, 'ci_lower': 1.343, 'ci_upper': 1.406} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.75, 'ci_lower': 1.71, 'ci_upper': 1.78} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.14, 'ci_lower': 2.1, 'ci_upper': 2.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65, 'ci_lower': 1.59, 'ci_upper': 1.71} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.55, 'ci_lower': 1.5, 'ci_upper': 1.6} | N/A | Agent Input |
| validation_sample_size | n=53,092 | n=308,264 | n=52,702 | n=7,465 | n=52,702 | n=288,978 | Agent Input |
| samples_training | N/A | n=116,649 | n=87,724 | n=29,863 | n=56,359 | n=120,280 | Agent Input |
| ancestry_distribution | GWAS: AFR (4%), AMR (1%), EAS (13%), EUR (30%), MAE (53%) / EVAL: MAE (100%) | GWAS: MAE (100%) / DEV: EUR (100%) / EVAL: AFR (22%), AMR (11%), EAS (11%), EUR (22%), MAE (11%), SAS (22%) | GWAS: AFR (7%), AMR (3%), EAS (19%), EUR (71%) / DEV: AFR (19%), AMR (11%), EUR (64%), MAO (5%) / EVAL: AFR (20%), AMR (20%), EAS (20%), EUR (20%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (4%), AMR (2%), EAS (11%), EUR (83%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (20%), EAS (20%), EUR (20%), SAS (20%) | GWAS: AFR (2%), AMR (2%), EAS (6%), EUR (75%), GME (1%), SAS (14%) / DEV: EUR (100%) / EVAL: NR (3%), AFR (10%), AMR (10%), ASN (2%), EAS (5%), EUR (49%), MAE (16%), SAS (6%) | Agent Input |
| training_development_cohorts | BBJ CKB FinnGen MVP | AGENT2D BBJ CARDIoGRAMplusC4D DIAMANTE FinnGen G&H GBMI GIANT GLGC MEGASTROKE MVP UKB | BBJ CARDIoGRAMplusC4D MVP UKB | AllofUs | BBJ CARDIoGRAMplusC4D MVP UKB | ADVANCE AGES AIDHS ARIC BAS BioMe CARDIOGENICS CAS CCGB COROGENE DUKE_2 EGCUT FGENTCARD FHS FINRISK FamHS GENRIC GerMIFS GoDARTS HPS HSDS HSIEA ITH LIFE-HEART LOLIPOP LURIC MAYO-VDB MIGen MedSTAR OHGS PIVUS PROCARDIS PROMIS PROSPER PennCATH RS SDS TwinGene UKB ULSAM WGHS WTCCC | Agent Input |
| publication.title | Evaluating Performance and Agreement of Coronary Heart Disease Polygenic Risk Scores. | A multi-ancestry polygenic risk score improves risk prediction for coronary artery disease. | Multi-Ancestry Polygenic Risk Score for Coronary Heart Disease Based on an Ancestrally Diverse Genome-Wide Association Study and Population-Specific Optimization. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Multi-Ancestry Polygenic Risk Score for Coronary Heart Disease Based on an Ancestrally Diverse Genome-Wide Association Study and Population-Specific Optimization. | Genome-wide polygenic scores for common diseases identify individuals with risk equivalent to monogenic mutations. | Agent Input |
| publication.journal | JAMA | Nat Med | Circ Genom Precis Med | Cell Genom | Circ Genom Precis Med | Nat Genet | Agent Input |
| date_release | 2024-11-21 | 2023-07-05 | 2024-03-18 | 2024-03-28 | 2024-03-18 | 2019-10-14 | Agent Input |
| variants_number | 1428772 | 1296172 | 1289980 | 4769577 | 1120251 | 6630150 | Agent Input |
| covariates | Age, sex, first 5 PCs | age, sex and the first ten principal components of genetic ancestry | age, sex, 10 PCs | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, 10 PCs | age; sex; Ancestry PC 1-4; genotyping chip | Agent Input |


### asthma

Candidate pool: `66` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004725 | PGS004724 | PGS004726 | PGS004723 | PGS001782 | PGS002727 | Agent Input |
| AoU benchmark rank | 1/66 | 2/66 | 3/66 | 4/66 | 5/66 | 41/66 | Benchmark Only |
| AoU benchmark AUC | 0.6089 | 0.6054 | 0.6054 | 0.5997 | 0.5987 | 0.5523 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 5/10 trials | Benchmark Only |
| trait_reported | Asthma | Asthma | Asthma | Asthma | Asthma | Asthma | Agent Input |
| trait_efo | asthma | asthma | asthma | asthma | asthma | asthma | Agent Input |
| phenotyping_reported | Asthma | Asthma | Asthma | Asthma | Asthma | Pediatric asthma | Agent Input |
| method_name | PRSmixPlus | PRSmix | PRSmixPlus | PRSmix | PRS-CS-auto | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM020950 | PPM020949 | PPM020951 | PPM020948 | PPM009311 | PPM014751 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | South Asian | South Asian | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0488 | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | 0.6590 | 0.6600 | Agent Input |
| performance_metrics.full_model_r2 | 0.0390 | 0.0650 | 0.0690 | 0.0330 | N/A | 0.0400 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.659} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66, 'ci_lower': 0.65, 'ci_upper': 0.67} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.039, 'ci_lower': 0.031, 'ci_upper': 0.047} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.065, 'ci_lower': 0.055, 'ci_upper': 0.075} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.069, 'ci_lower': 0.059, 'ci_upper': 0.08} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.033, 'ci_lower': 0.026, 'ci_upper': 0.04} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.048844} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.57, 'ci_lower': 1.55, 'ci_upper': 1.6} | Agent Input |
| validation_sample_size | n=9,462 | n=8,837 | n=8,837 | n=9,462 | n=7,128 | n=391,820 | Agent Input |
| samples_training | n=37,851 | n=35,350 | n=35,350 | n=37,851 | N/A | n=4,498 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: SAS (100%) / EVAL: SAS (100%) | DEV: SAS (100%) / EVAL: SAS (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (19%), EUR (76%), GME (9%), OTH (100%) / EVAL: EUR (100%) | GWAS: AFR (6%), AMR (100%), EAS (4%), EUR (90%) / DEV: MAE (100%) / EVAL: AFR (20%), AMR (20%), EAS (20%), EUR (20%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs | G&H | G&H | AllofUs | BBJ BioMe BioVU CCPM CKB EB FinnGen GS:SFHS HUNT MGBB MGI TWB UCLA UKB | eMERGE | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Multiancestral polygenic risk score for pediatric asthma. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | Cell Genom | Cell Genom | Cell Genom | J Allergy Clin Immunol | Agent Input |
| date_release | 2024-03-28 | 2024-03-28 | 2024-03-28 | 2024-03-28 | 2022-09-08 | 2022-06-29 | Agent Input |
| variants_number | 3972232 | 2342250 | 2342250 | 985316 | 884043 | 985837 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | sex,age, 20PCs | Unknown | Agent Input |


### gout

Candidate pool: `63` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004768 | PGS004160 | PGS004767 | PGS004076 | PGS004047 | PGS001789 | Agent Input |
| AoU benchmark rank | 1/59 | 2/59 | 3/59 | 4/59 | 5/59 | 15/59 | Benchmark Only |
| AoU benchmark AUC | 0.6693 | 0.6490 | 0.6467 | 0.6437 | 0.6433 | 0.6268 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | Benchmark Only |
| trait_reported | Gout | Gout | Gout | Gout | Gout | Gout | Agent Input |
| trait_efo | gout | gout | gout | gout | gout | gout | Agent Input |
| phenotyping_reported | Gout | Gout | Gout | Gout | Gout | Gout | Agent Input |
| method_name | PRSmixPlus | UKBB-EUR.MultiPRS.CV | PRSmix | megaprs.CV | LDpred2.CV | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | PPM020993 | PPM019864 | PPM020992 | PPM019879 | PPM019819 | PPM009293 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 6 | 1 | 6 | 6 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0312 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.6936 | N/A | 0.6845 | 0.6851 | 0.8070 | Agent Input |
| performance_metrics.full_model_r2 | 0.0810 | 0.0893 | 0.0610 | 0.0788 | 0.0801 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69364137, 'ci_lower': 0.68102136, 'ci_upper': 0.70626138} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.68450292, 'ci_lower': 0.67169718, 'ci_upper': 0.69730867} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.68510818, 'ci_lower': 0.67239174, 'ci_upper': 0.69782462} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.807} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.081, 'ci_lower': 0.071, 'ci_upper': 0.092} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.08927641, 'ci_lower': 0.07728456, 'ci_upper': 0.10150747} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.061, 'ci_lower': 0.052, 'ci_upper': 0.071} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.07884797, 'ci_lower': 0.06756619, 'ci_upper': 0.09040694} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.08005591, 'ci_lower': 0.0693014, 'ci_upper': 0.09177049} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.031208} | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.04859051, 'ci_lower': 1.95027604, 'ci_upper': 2.15186105} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.717152, 'ci_lower': 0.66797092, 'ci_upper': 0.76633307} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.97547041, 'ci_lower': 1.87984426, 'ci_upper': 2.07596098} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.68080655, 'ci_lower': 0.63118893, 'ci_upper': 0.73042417} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.99932119, 'ci_lower': 1.90150797, 'ci_upper': 2.1021659} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.69280772, 'ci_lower': 0.64264724, 'ci_upper': 0.74296819} | N/A | Agent Input |
| validation_sample_size | n=9,462 | n=90,274 | n=9,462 | n=90,274 | n=90,274 | n=359,345 | Agent Input |
| samples_training | n=37,851 | n=6,704 | n=37,851 | n=6,704 | n=6,704 | N/A | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: AFR (3%), ASN (2%), EAS (33%), EUR (60%), OTH (2%) / EVAL: AFR (33%), ASN (33%), EUR (33%) | Agent Input |
| training_development_cohorts | AllofUs | UKB | AllofUs | UKB | UKB | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI UCLA | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | Cell Genom | Am J Hum Genet | Cell Genom | Am J Hum Genet | Am J Hum Genet | Cell Genom | Agent Input |
| date_release | 2024-03-28 | 2023-12-19 | 2024-03-28 | 2023-12-19 | 2023-12-19 | 2022-09-08 | Agent Input |
| variants_number | 1580311 | 976174 | 908271 | 677631 | 865644 | 910151 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | 0 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | 0 | 0 | sex,age,age2,age*sex,age^2*sex, 20PCs | Agent Input |


### atrial fibrillation

Candidate pool: `61` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005313 | PGS005067 | PGS005287 | PGS005289 | PGS004706 | PGS005168 | Agent Input |
| AoU benchmark rank | 1/61 | 2/61 | 3/61 | 4/61 | 5/61 | 52/61 | Benchmark Only |
| AoU benchmark AUC | 0.6315 | 0.6236 | 0.6225 | 0.6211 | 0.6205 | 0.5580 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Atrial fibrillation | Atrial fibrillation (PheCode 427.21) | Atrial fibrillation | Atrial fibrillation | Atrial Fibrillation | Atrial fibrillation | Agent Input |
| trait_efo | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | atrial fibrillation | Agent Input |
| phenotyping_reported | atrial fibrillation | Atrial fibrillation | Prevalent atrial fibrillation or flutter | Prevalent atrial fibrillation or flutter | Atrial Fibrillation | Atrial fibrillation | Agent Input |
| method_name | PRS-CSx | prscs | LDpred2 | LDpred2 | PRSmixPlus | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM023035 | PPM021851 | PPM022995 | PPM022997 | PPM020931 | PPM022406 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African unspecified, South Asian, East Asian, Hispanic or Latin American, Other | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 3 | 1 | 1 | 1 | 45 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7800 | 0.8276 | 0.7030 | 0.6813 | N/A | 0.8718 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.1469 | 0.1255 | 0.0440 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78, 'ci_lower': 0.778, 'ci_upper': 0.783} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.827583786719081} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.703} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6813004} | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.8718, 'ci_lower': 0.8657, 'ci_upper': 0.878} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.14693} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.12547} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.044, 'ci_lower': 0.036, 'ci_upper': 0.053} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.82, 'ci_lower': 1.79, 'ci_upper': 1.85} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.734, 'ci_lower': 1.66, 'ci_upper': 1.81} | N/A | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.6663} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.5106, 'se': 0.0206} | Agent Input |
| validation_sample_size | n=37,161 | n=25,409 | n=12,677 | n=7,525 | n=9,462 | n=52,757 | Agent Input |
| samples_training | N/A | N/A | n=2,500 | n=1,503 | n=37,851 | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (5%), AMR (2%), EAS (6%), EUR (86%), SAS (2%) / EVAL: MAE (100%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (1%), AMR (1%), EAS (17%), EUR (80%), SAS (7%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AFGen BBJ FinnGen G&H HUNT MGI MVP MyCode SIMPLER UKB deCODE | MVP | MHI | MHI | AllofUs | AGES ARIC BBJ BioMe Broad CVDi CCAF CHB CHS EGCUT ENGAGE_AF-TIMI_48 FHS FinnGen GAPP GS:SFHS HRS LURIC MESA MGI MyCode Other PHB PIVUS PREVEND PROSPER RS SHIP SOLID-TIMI_52 SPHFC SiGN TwinGene ULSAM Vanderbilt WGHS WTCCC deCODE | Agent Input |
| publication.title | Cross-population GWAS and proteomics improve risk prediction and reveal mechanisms in atrial fibrillation. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Genetic analyses across cardiovascular traits: leveraging genetic correlations to empower locus discovery and prediction in common cardiovascular diseases. | Genetic analyses across cardiovascular traits: leveraging genetic correlations to empower locus discovery and prediction in common cardiovascular diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Meta-analysis of genome-wide associations and polygenic risk prediction for atrial fibrillation in more than 180,000 cases. | Agent Input |
| publication.journal | Nat Commun | HGG Adv | NPJ Genom Med | NPJ Genom Med | Cell Genom | Nat Genet | Agent Input |
| date_release | 2025-10-06 | 2024-10-08 | 2025-12-18 | 2025-12-18 | 2024-03-28 | 2025-03-17 | Agent Input |
| variants_number | 1271239 | 1273897 | 1016634 | 1016634 | 3576958 | 382963 | Agent Input |
| covariates | age, sex | age, sex, 20 PCs | age, sex, four first principal components of genetic ancestry | age, sex, four first principal components of genetic ancestry | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, age^2, sex, geno_array, CHARGE-AF | Agent Input |


### rheumatoid arthritis

Candidate pool: `48` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004819 | PGS004817 | PGS004163 | PGS004873 | PGS002769 | PGS004163 | Agent Input |
| AoU benchmark rank | 1/42 | 2/42 | 3/42 | 4/42 | 5/42 | 3/42 | Benchmark Only |
| AoU benchmark AUC | 0.6006 | 0.5889 | 0.5850 | 0.5824 | 0.5780 | 0.5850 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Rheumatoid Arthritis | Rheumatoid Arthritis | Rheumatoid arthritis | Rheumatoid arthritis | Seropositive rheumatoid arthritis | Rheumatoid arthritis | Agent Input |
| trait_efo | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | rheumatoid arthritis | Agent Input |
| phenotyping_reported | Rheumatoid Arthritis | Rheumatoid Arthritis | Seropositive RA | Incident RA | Seropositive rheumatoid arthritis | Seropositive RA | Agent Input |
| method_name | PRSmixPlus | PRSmix | UKBB-EUR.MultiPRS.CV | megaprs.auto | PRS-CS | UKBB-EUR.MultiPRS.CV | Agent Input |
| performance_metrics.selected_performance_id | PPM021044 | PPM021042 | PPM020029 | PPM021170 | PPM014969 | PPM020029 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 5 | 8 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.7469 | 0.8500 | N/A | 0.7469 | Agent Input |
| performance_metrics.full_model_r2 | 0.0110 | 0.0080 | 0.1376 | N/A | N/A | 0.1376 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74694739, 'ci_lower': 0.71319269, 'ci_upper': 0.78070209} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.85, 'ci_lower': 0.77, 'ci_upper': 0.92} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74694739, 'ci_lower': 0.71319269, 'ci_upper': 0.78070209} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.011, 'ci_lower': 0.007, 'ci_upper': 0.015} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.008, 'ci_lower': 0.004, 'ci_upper': 0.012} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1375903, 'ci_lower': 0.09865689, 'ci_upper': 0.18374268} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1375903, 'ci_lower': 0.09865689, 'ci_upper': 0.18374268} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.46183351, 'ci_lower': 2.16199209, 'ci_upper': 2.8032592} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.9009064, 'ci_lower': 0.77103006, 'ci_upper': 1.03078274} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.83, 'ci_lower': 1.14, 'ci_upper': 2.93} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.72, 'ci_lower': 1.61, 'ci_upper': 1.83} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.46183351, 'ci_lower': 2.16199209, 'ci_upper': 2.8032592} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.9009064, 'ci_lower': 0.77103006, 'ci_upper': 1.03078274} | Agent Input |
| validation_sample_size | n=9,462 | n=9,462 | n=90,274 | n=7,018 | n=39,444 | n=90,274 | Agent Input |
| samples_training | n=37,851 | n=37,851 | n=820 | n=404 | N/A | n=820 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (80%), SAS (20%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (28%), EUR (72%) / EVAL: EUR (100%) | GWAS: EAS (81%), EUR (19%) / DEV: EUR (100%) / EVAL: EUR (80%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs | AllofUs | UKB | 1000G | N/A | UKB | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | Am J Hum Genet | Nat Commun | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2024-03-28 | 2024-03-28 | 2023-12-19 | 2024-06-27 | 2022-11-07 | 2023-12-19 | Agent Input |
| variants_number | 2624228 | 786048 | 778275 | 551074 | 1083565 | 778275 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | 0 | PCs 1-10 | age, sex, 10 PCs, technical covariates | 0 | Agent Input |


### lung cancer

Candidate pool: `35` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004860 | PGS002270 | PGS000721 | PGS004325 | PGS004884 | PGS004860 | Agent Input |
| AoU benchmark rank | 1/35 | 2/35 | 3/35 | 4/35 | 5/35 | 1/35 | Benchmark Only |
| AoU benchmark AUC | 0.5709 | 0.5654 | 0.5595 | 0.5595 | 0.5583 | 0.5709 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | Benchmark Only |
| trait_reported | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Lung cancer | Agent Input |
| trait_efo | lung carcinoma | lung carcinoma | lung carcinoma | lung carcinoma | lung carcinoma | lung carcinoma | Agent Input |
| phenotyping_reported | Incident lung cancer | Lung cancer | Lung cancer | Lung carcinogenesis (in smokers) | Incident lung cancer | Incident lung cancer | Agent Input |
| method_name | LDpred2 | Genome-wide significant variants | Genome-wide significant variants | Genome-wide significant SNPs | megaprs.auto | LDpred2 | Agent Input |
| performance_metrics.selected_performance_id | PPM021091 | PPM020290 | PPM020286 | PPM020438 | PPM021250 | PPM021091 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 4 | 2 | 7 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8930 | 0.7250 | 0.7380 | N/A | 0.6200 | 0.8930 | Agent Input |
| performance_metrics.full_model_r2 | 0.4900 | N/A | N/A | N/A | N/A | 0.4900 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.893, 'ci_lower': 0.887, 'ci_upper': 0.898} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.725, 'ci_lower': 0.697, 'ci_upper': 0.754} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.71, 'ci_upper': 0.766} | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.62, 'ci_lower': 0.61, 'ci_upper': 0.63} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.893, 'ci_lower': 0.887, 'ci_upper': 0.898} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.49} | N/A | N/A | {'name_long': 'Hazard ratio (HR, highest PRS quintile and heavy smokers vs lowest PRS quintile and never smokers)', 'name_short': 'Hazard ratio (HR, highest PRS quintile and heavy smokers vs lowest PRS quintile and never smokers)', 'estimate': 4.63, 'ci_lower': 3.0, 'ci_upper': 7.13} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.49} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | N/A | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.24, 'ci_lower': 1.2, 'ci_upper': 1.28} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | Agent Input |
| validation_sample_size | n=24,012 | n=1,202 | n=1,202 | n=308,490 | n=277,400 | n=24,012 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=404 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (20%), EUR (80%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EAS (33%), EUR (67%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (27%), EUR (73%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | BBJ GAME-ON GELCAPS GLC IARC ICR ILCCO MDACC MRC NCI SLRI TRICL | ATBC B58C CARET EAGLE GAME-ON GECCO GELCAPS GLC HGF HUNT2 Harvard IARC ICR-GWAS LLP MDACCS NCI PLCO SLRI Tromso UKBS WTCCC deCODE | N/A | 1000G | N/A | Agent Input |
| publication.title | Polygenic inheritance and its interplay with smoking history in predicting lung cancer diagnosis: a French-Canadian case-control cohort. | Association of smoking and polygenic risk with the incidence of lung cancer: a prospective cohort study. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Association of oxidative stress, programmed cell death, GSTM1 gene polymorphisms, smoking and the risk of lung carcinogenesis: A two-step Mendelian randomization study. | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Polygenic inheritance and its interplay with smoking history in predicting lung cancer diagnosis: a French-Canadian case-control cohort. | Agent Input |
| publication.journal | EBioMedicine | Br J Cancer | JNCI Cancer Spectr | Front Physiol | Nat Commun | EBioMedicine | Agent Input |
| date_release | 2024-07-31 | 2022-04-01 | 2021-02-03 | 2024-01-11 | 2024-06-27 | 2024-07-31 | Agent Input |
| variants_number | 1143554 | 33 | 19 | 19 | 655479 | 1143554 | Agent Input |
| covariates | Sex, age,BMI, smocking status(ever or never smoker), and the first 10 ancestry-based PCA | Age, sex, current smoking status, BMI, forced expiratory volume in 1 second/forced vital capacity ratio | Age, sex, current smoking status, BMI, forced expiratory volume in 1 second/forced vital capacity ratio | Education, sex, genotype array, and the first ten important components | PCs 1-10 | Sex, age,BMI, smocking status(ever or never smoker), and the first 10 ancestry-based PCA | Agent Input |


### myocardial infarction

Candidate pool: `35` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005045 | PGS005039 | PGS005044 | PGS005041 | PGS005046 | PGS005039 | Agent Input |
| AoU benchmark rank | 1/35 | 2/35 | 3/35 | 4/35 | 5/35 | 2/35 | Benchmark Only |
| AoU benchmark AUC | 0.6044 | 0.6020 | 0.6019 | 0.6013 | 0.6010 | 0.6020 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 7/10 trials | Benchmark Only |
| trait_reported | Myocardial infarction (PheCode 411.2) | Myocardial infarction (PheCode 411.2) | Myocardial infarction (PheCode 411.2) | Myocardial infarction (PheCode 411.2) | Myocardial infarction (PheCode 411.2) | Myocardial infarction (PheCode 411.2) | Agent Input |
| trait_efo | myocardial infarction | myocardial infarction | myocardial infarction | myocardial infarction | myocardial infarction | myocardial infarction | Agent Input |
| phenotyping_reported | Myocardial infarction | Myocardial infarction | Myocardial infarction | Myocardial infarction | Myocardial infarction | Myocardial infarction | Agent Input |
| method_name | prscs | ldpred | prscs | prscs | prscsx | ldpred | Agent Input |
| performance_metrics.selected_performance_id | PPM021806 | PPM021907 | PPM021805 | PPM021809 | PPM021810 | PPM021907 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 3 | 3 | 3 | 3 | 3 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7839 | 0.7848 | 0.7836 | 0.7837 | 0.7834 | 0.7848 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.783850849010177} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.784836989151752} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.7836188471857} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.783728758270691} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.783365290706975} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.784836989151752} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.554, 'ci_lower': 1.47, 'ci_upper': 1.64} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.578, 'ci_lower': 1.5, 'ci_upper': 1.67} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.546, 'ci_lower': 1.47, 'ci_upper': 1.63} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.535, 'ci_lower': 1.46, 'ci_upper': 1.62} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.527, 'ci_lower': 1.45, 'ci_upper': 1.61} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.578, 'ci_lower': 1.5, 'ci_upper': 1.67} | Agent Input |
| validation_sample_size | n=30,379 | n=30,379 | n=30,379 | n=30,379 | n=30,379 | n=30,379 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | Agent Input |
| training_development_cohorts | MVP | MVP | MVP | MVP | MVP | MVP | Agent Input |
| publication.title | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Agent Input |
| publication.journal | HGG Adv | HGG Adv | HGG Adv | HGG Adv | HGG Adv | HGG Adv | Agent Input |
| date_release | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2024-10-08 | Agent Input |
| variants_number | 1273897 | 1286612 | 1273897 | 1273897 | 1273891 | 1286612 | Agent Input |
| covariates | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | Agent Input |


### heart failure

Candidate pool: `34` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005097 | PGS005078 | PGS005076 | PGS005077 | PGS005083 | PGS005083 | Agent Input |
| AoU benchmark rank | 1/33 | 2/33 | 3/33 | 4/33 | 5/33 | 5/33 | Benchmark Only |
| AoU benchmark AUC | 0.6110 | 0.5947 | 0.5938 | 0.5938 | 0.5931 | 0.5931 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | Benchmark Only |
| trait_reported | Heart failure | Congestive heart failure (CHF), NOS (PheCode 428.1) | Congestive heart failure (CHF), NOS (PheCode 428.1) | Congestive heart failure (CHF), NOS (PheCode 428.1) | Congestive heart failure (CHF), NOS (PheCode 428.1) | Congestive heart failure (CHF), NOS (PheCode 428.1) | Agent Input |
| trait_efo | heart failure | congestive heart failure | congestive heart failure | congestive heart failure | congestive heart failure | congestive heart failure | Agent Input |
| phenotyping_reported | Prevalent heart failure | Congestive heart failure (CHF), NOS | Congestive heart failure (CHF), NOS | Congestive heart failure (CHF), NOS | Congestive heart failure (CHF), NOS | Congestive heart failure (CHF), NOS | Agent Input |
| method_name | PRS-CSx | ldpred | ldpred | ldpred | prscs | prscs | Agent Input |
| performance_metrics.selected_performance_id | PPM022207 | PPM021961 | PPM021959 | PPM021960 | PPM021868 | PPM021868 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African unspecified | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 3 | 3 | 3 | 3 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7200 | 0.7525 | 0.7532 | 0.7536 | 0.7537 | 0.7537 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.72, 'ci_lower': 0.72, 'ci_upper': 0.73} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75253114316328} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.753249050693995} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.753575892982002} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.753682708175126} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.753682708175126} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Brier skill score', 'name_short': 'Brier skill score', 'estimate': 0.065, 'ci_lower': 0.063, 'ci_upper': 0.068} | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.442, 'ci_lower': 1.37, 'ci_upper': 1.52} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.443, 'ci_lower': 1.37, 'ci_upper': 1.52} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.452, 'ci_lower': 1.38, 'ci_upper': 1.53} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.455, 'ci_lower': 1.38, 'ci_upper': 1.54} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.455, 'ci_lower': 1.38, 'ci_upper': 1.54} | Agent Input |
| validation_sample_size | n=40,989 | n=31,804 | n=31,804 | n=31,804 | n=31,804 | n=31,804 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (6%), AMR (3%), EAS (11%), EUR (80%) / EVAL: MAE (100%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | GWAS: NR (50%), AFR (10%), AMR (4%), EUR (36%) / EVAL: AFR (33%), AMR (33%), EUR (33%) | Agent Input |
| training_development_cohorts | BBJ BioMe CKB FinnGen GBMI HERMES MVP MyCode UCLA eMERGE | MVP | MVP | MVP | MVP | MVP | Agent Input |
| publication.title | Common-variant and rare-variant genetic architecture of heart failure across the allele-frequency spectrum. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Comparison of Methods for Building Polygenic Scores for Diverse Populations. | Agent Input |
| publication.journal | Nat Genet | HGG Adv | HGG Adv | HGG Adv | HGG Adv | HGG Adv | Agent Input |
| date_release | 2025-04-17 | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2024-10-08 | 2024-10-08 | Agent Input |
| variants_number | 1274692 | 1286612 | 1286612 | 1286612 | 1273897 | 1273897 | Agent Input |
| covariates | Age, sex, 5 genetic principal components | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | age, sex, 20 PCs | Agent Input |


### thyroid carcinoma

Candidate pool: `32` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005260 | PGS005274 | PGS005273 | PGS005259 | PGS005258 | PGS000208 | Agent Input |
| AoU benchmark rank | 1/32 | 2/32 | 3/32 | 4/32 | 5/32 | 16/32 | Benchmark Only |
| AoU benchmark AUC | 0.8113 | 0.8069 | 0.8016 | 0.7865 | 0.6376 | 0.5890 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Thyroid carcenoma | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma | Thyroid carcenoma | Thyroid cancer | Agent Input |
| trait_efo | thyroid carcinoma | benign, thyroid carcinoma, nodular goiter | benign, thyroid carcinoma, nodular goiter | thyroid carcinoma | thyroid carcinoma | thyroid carcinoma | Agent Input |
| phenotyping_reported | thyroid carcenoma | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma | thyroid carcenoma | Thyroid cancer | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | PRSCS | Pruning and Thresholding (P+T) | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM022743 | PPM022757 | PPM022756 | PPM022742 | PPM022741 | PPM000632 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6845 | 0.6135 | 0.6174 | 0.6953 | 0.6862 | 0.7510 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.684522760200784} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.613489463745261} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.617388005401901} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.695254013741303} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.686161285410893} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.751, 'ci_lower': 0.736, 'ci_upper': 0.768} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.96019114706853} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.673041992501825} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49346171423604} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.401096723418125} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.55051776688383} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.438588918302023} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.03688674186851} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.71142253524162} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.02} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.016} | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=130,279 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BioMe BioVU HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT KCPS LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT KCPS LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | NBS UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Assessing thyroid cancer risk using polygenic risk scores. | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | medRxiv | Proc Natl Acad Sci U S A | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2020-07-01 | Agent Input |
| variants_number | 1085170 | 1084965 | 1085164 | 1085173 | 84 | 10 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | gender, birth year, family history of disease (1st or 2nd degree relative) | Agent Input |


### psoriasis

Candidate pool: `31` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005309 | PGS005311 | PGS004315 | PGS005312 | PGS005310 | PGS001312 | Agent Input |
| AoU benchmark rank | 1/24 | 2/24 | 3/24 | 4/24 | 5/24 | 15/24 | Benchmark Only |
| AoU benchmark AUC | 0.6087 | 0.6086 | 0.6014 | 0.5958 | 0.5958 | 0.5718 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Psoriasis | Psoriasis | Psoriasis | Psoriasis | Psoriasis | Psoriasis | Agent Input |
| trait_efo | psoriasis | psoriasis | psoriasis | psoriasis | psoriasis | psoriasis | Agent Input |
| phenotyping_reported | Severe psoriasis | Severe psoriasis (BSTOP) vs. any psoriasis (UKB) | Psoriasis severity | Severe psoriasis (BSTOP) vs. any psoriasis (UKB) | Severe psoriasis | Psoriasis | Agent Input |
| method_name | SBayesR | SBayesR | Genome-wide significant SNPs | SBayesR | SBayesR | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM023021 | PPM023031 | PPM020388 | PPM023032 | PPM023022 | PPM009057 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 4 | 2 | 7 | 2 | 4 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | 0.6916 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0523 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | 0.6975 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0610 | N/A | N/A | 0.0557 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | 0.1451 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69754, 'ci_lower': 0.68165, 'ci_upper': 0.71343} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'name_short': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'estimate': 15.3} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.061} | {'name_long': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'name_short': 'Percentage of cases with risk >95th percentile of UKB psoraisis cases', 'estimate': 15.3} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05574} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.14505} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.05226} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.69158, 'ci_lower': 0.6754, 'ci_upper': 0.70775} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49, 'ci_lower': 1.41, 'ci_upper': 1.57} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.02, 'ci_lower': 1.0, 'ci_upper': 1.06} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.38, 'ci_lower': 1.31, 'ci_upper': 1.45} | N/A | Agent Input |
| validation_sample_size | n=14,167 | n=13,577 | n=654 | n=13,577 | n=14,167 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | CASP Genizon KIEL UCSF WTCCC | CASP Genizon KIEL UCSF WTCCC | N/A | CASP Genizon KIEL UCSF WTCCC | CASP Genizon KIEL UCSF WTCCC | UKB | Agent Input |
| publication.title | Genetic liability to psoriasis predicts severe disease outcomes. | Genetic liability to psoriasis predicts severe disease outcomes. | A partitioned 88-loci psoriasis genetic risk score reveals HLA and non-HLA contributions to clinical phenotypes in a Newfoundland psoriasis cohort. | Genetic liability to psoriasis predicts severe disease outcomes. | Genetic liability to psoriasis predicts severe disease outcomes. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Genome Med | Genome Med | Front Genet | Genome Med | Genome Med | PLoS Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2024-01-11 | 2026-01-19 | 2026-01-19 | 2021-10-21 | Agent Input |
| variants_number | 513461 | 487311 | 88 | 487310 | 513460 | 204 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### hypothyroidism

Candidate pool: `28` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005268 | PGS005269 | PGS005218 | PGS005267 | PGS004789 | PGS005218 | Agent Input |
| AoU benchmark rank | 1/28 | 2/28 | 3/28 | 4/28 | 5/28 | 3/28 | Benchmark Only |
| AoU benchmark AUC | 0.6575 | 0.6567 | 0.6289 | 0.6240 | 0.6231 | 0.6289 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | Benchmark Only |
| trait_reported | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Hypothyroidism | Agent Input |
| trait_efo | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | hypothyroidism | Agent Input |
| phenotyping_reported | hypothyroidism | hypothyroidism | Incident hypothyroidism | hypothyroidism | Hypothyroidism | Incident hypothyroidism | Agent Input |
| method_name | PRSCS | PRSCS | PRS-CS | Pruning and Thresholding (P+T) | PRSmix | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM022751 | PPM022752 | PPM022617 | PPM022750 | PPM021014 | PPM022617 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 6 | 1 | 1 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6389 | 0.6386 | 0.8590 | 0.6400 | N/A | 0.8590 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0410 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638920940728866} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638628477117025} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.859, 'ci_lower': 0.821, 'ci_upper': 0.897} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.859, 'ci_lower': 0.821, 'ci_upper': 0.897} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.041, 'ci_lower': 0.033, 'ci_upper': 0.049} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65808867613792} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.505665539081399} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65210243632159} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.502048680634994} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.142} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.133} | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=441,692 | n=94,651 | n=9,462 | n=441,692 | Agent Input |
| samples_training | N/A | N/A | n=1,146,562 | N/A | n=37,851 | n=1,146,562 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BioMe BioVU EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | 23andMe CHB DBDS EB FinnGen UKB deCODE | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs | 23andMe CHB DBDS EB FinnGen UKB deCODE | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Genome-wide association study and polygenic risk prediction of hypothyroidism. | Agent Input |
| publication.journal | medRxiv | medRxiv | Nat Genet | medRxiv | Cell Genom | Nat Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2025-11-10 | 2026-01-19 | 2024-03-28 | 2025-11-10 | Agent Input |
| variants_number | 1085173 | 1085170 | 1110091 | 439 | 1109333 | 1110091 | Agent Input |
| covariates | Unknown | Unknown | age, sex, TSH, T4, anti-TPO, PC1, PC2, PC3, PC4 | Unknown | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, TSH, T4, anti-TPO, PC1, PC2, PC3, PC4 | Agent Input |


### hodgkins lymphoma

Candidate pool: `27` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000639 | PGS003449 | PGS000638 | PGS003454 | PGS000648 | PGS000639 | Agent Input |
| AoU benchmark rank | 1/27 | 2/27 | 3/27 | 4/27 | 5/27 | 1/27 | Benchmark Only |
| AoU benchmark AUC | 0.6180 | 0.6120 | 0.6014 | 0.5597 | 0.5586 | 0.6180 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Hodgkin's disease | Hodgkin lymphoma | Hodgkin's disease | Diffuse large B-cell lymphoma | Chronic lymphocytic leukemia | Hodgkin's disease | Agent Input |
| trait_efo | Hodgkins lymphoma | Hodgkins lymphoma | Hodgkins lymphoma | diffuse large B-cell lymphoma | chronic lymphocytic leukemia | Hodgkins lymphoma | Agent Input |
| phenotyping_reported | Hodgkin's disease | Chronic lymphocytic leukemia | Hodgkin's disease | Chronic lymphocytic leukemia | Lymphoid leukemia, chronic | Hodgkin's disease | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Genome-wide significant SNPs | GWAS Hits | Genome-wide significant SNPs | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM001324 | PPM017231 | PPM001323 | PPM017225 | PPM001333 | PPM001324 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 4 | 1 | 4 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6200 | N/A | 0.6010 | N/A | 0.6960 | 0.6200 | Agent Input |
| performance_metrics.full_model_r2 | 0.0276 | N/A | 0.0193 | N/A | 0.1020 | 0.0276 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62, 'ci_lower': 0.559, 'ci_upper': 0.688} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.601, 'ci_lower': 0.535, 'ci_upper': 0.671} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696, 'ci_lower': 0.621, 'ci_upper': 0.764} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62, 'ci_lower': 0.559, 'ci_upper': 0.688} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0276} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.64, 'ci_lower': 0.572, 'ci_upper': 12.2} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0193} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0824} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 1.62, 'ci_lower': 0.258, 'ci_upper': 10.1} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.102} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0776} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 12.9, 'ci_lower': 4.45, 'ci_upper': 37.6} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0276} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.64, 'ci_lower': 0.572, 'ci_upper': 12.2} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.476, 'ci_lower': 1.154, 'ci_upper': 1.889} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.39, 'se': 0.126} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.02, 'ci_lower': 0.97, 'ci_upper': 1.08} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.377, 'ci_lower': 1.08, 'ci_upper': 1.755} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.32, 'se': 0.124} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33, 'ci_lower': 1.14, 'ci_upper': 1.54} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.124, 'ci_lower': 1.648, 'ci_upper': 2.738} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.753, 'se': 0.13} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.476, 'ci_lower': 1.154, 'ci_upper': 1.889} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.39, 'se': 0.126} | Agent Input |
| validation_sample_size | n=775 | n=20,134 | n=775 | n=20,134 | n=756 | n=775 | Agent Input |
| samples_training | n=736 | N/A | n=736 | N/A | n=730 | n=736 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MGI | N/A | MGI | N/A | MGI | MGI | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Agent Input |
| publication.journal | Am J Hum Genet | Leukemia | Am J Hum Genet | Leukemia | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2020-12-15 | 2023-03-24 | 2020-12-15 | 2023-03-24 | 2020-12-15 | 2020-12-15 | Agent Input |
| variants_number | 20 | 21 | 16 | 5 | 44 | 20 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | Unknown | age, sex, batch PCs 1-4 | Unknown | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Agent Input |


### major depressive disorder

Candidate pool: `24` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004760 | PGS003333 | PGS004759 | PGS000907 | PGS004885 | PGS003578 | Agent Input |
| AoU benchmark rank | 1/24 | 2/24 | 3/24 | 4/24 | 5/24 | 10/24 | Benchmark Only |
| AoU benchmark AUC | 0.5779 | 0.5687 | 0.5650 | 0.5648 | 0.5504 | 0.5443 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Depression | Major Depressive Disorder | Depression | Major depressive disorder | Major depressive disorder | Major Depressive Disorder (Lifetime) | Agent Input |
| trait_efo | major depressive disorder | major depressive disorder | major depressive disorder | major depressive disorder | major depressive disorder | major depressive disorder | Agent Input |
| phenotyping_reported | Depression | Major Depressive Disorder | Depression | Muscle pain in Fluoxetine takers | Incident MDD | Major depressive disorder | Agent Input |
| method_name | PRSmixPlus | PRS-CS-auto | PRSmix | SBayesR | megaprs.auto | PRSice-2 | Agent Input |
| performance_metrics.selected_performance_id | PPM020985 | PPM016144 | PPM020984 | PPM002717 | PPM021256 | PPM018275 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 50 | 7 | 10 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | 0.6200 | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0240 | 0.0220 | 0.0160 | 0.7700 | N/A | 0.0257 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.62, 'ci_lower': 0.58, 'ci_upper': 0.65} | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.024, 'ci_lower': 0.018, 'ci_upper': 0.03} | {'name_long': 'Nagelkerke pseudo-R2', 'name_short': 'Nagelkerke pseudo-R2', 'estimate': 0.022} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.016, 'ci_lower': 0.011, 'ci_upper': 0.021} | {'name_long': "Variance explained (Nagelkerke's R2*100)", 'name_short': "Variance explained (Nagelkerke's R2*100)", 'estimate': 0.77} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0257} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.3, 'ci_lower': 1.05, 'ci_upper': 1.6} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.36, 'ci_lower': 1.21, 'ci_upper': 1.53} | N/A | Agent Input |
| validation_sample_size | n=9,462 | n=34,703 | n=9,462 | n=3,670 | n=7,018 | n=42,250 | Agent Input |
| samples_training | n=37,851 | N/A | n=37,851 | N/A | n=404 | n=67,164 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (10%), ASN (20%), EAS (10%), EUR (40%) | Agent Input |
| training_development_cohorts | AllofUs | 23andMe PGC UKB | AllofUs | N/A | 1000G | UKB | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Polygenic Liability to Depression Is Associated With Multiple Medical Conditions in the Electronic Health Record: Phenome-wide Association Study of 46,782 Individuals. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Understanding genetic risk factors for common side effects of antidepressant medications | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Phenotype integration improves power and preserves specificity in biobank-based genetic studies of MDD | Agent Input |
| publication.journal | Cell Genom | Biol Psychiatry | Cell Genom | Commun Med (Lond) | Nat Commun | bioRxiv | Agent Input |
| date_release | 2024-03-28 | 2022-12-06 | 2024-03-28 | 2021-10-07 | 2024-06-27 | 2023-04-12 | Agent Input |
| variants_number | 2141267 | 1088415 | 1538576 | 1773528 | 801544 | 4786322 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | Unknown | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | sex, age at study enrollment, genetic PCs 1-20 | PCs 1-10 | PCs 1-10 | Agent Input |


### chronic kidney disease

Candidate pool: `22` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004045 | PGS004030 | PGS004158 | PGS004074 | PGS004088 | PGS002237 | Agent Input |
| AoU benchmark rank | 1/22 | 2/22 | 3/22 | 4/22 | 5/22 | 12/22 | Benchmark Only |
| AoU benchmark AUC | 0.5566 | 0.5564 | 0.5562 | 0.5546 | 0.5546 | 0.5466 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (CKD) | Chronic kidney disease (stage 3 or greater) | Agent Input |
| trait_efo | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | chronic kidney disease | Agent Input |
| phenotyping_reported | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic kidney disease or dialysis | Chronic kidney disease (eGFR <45 ml/min per 1.73 m2) | Agent Input |
| method_name | LDpred2.CV | LDpred2-auto | UKBB-EUR.MultiPRS.CV | megaprs.CV | PRS-CS-auto | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM019694 | PPM019754 | PPM019720 | PPM019774 | PPM019790 | PPM018708 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 6 | 6 | 6 | 6 | 6 | 9 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5885 | 0.5887 | 0.5917 | 0.5887 | 0.5820 | 0.7800 | Agent Input |
| performance_metrics.full_model_r2 | 0.0187 | 0.0187 | 0.0200 | 0.0186 | 0.0162 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.58851351, 'ci_lower': 0.57882039, 'ci_upper': 0.59820663} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.58871735, 'ci_lower': 0.57899906, 'ci_upper': 0.59843563} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59165352, 'ci_lower': 0.58198776, 'ci_upper': 0.60131927} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.58867836, 'ci_lower': 0.57900777, 'ci_upper': 0.59834895} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.5819827, 'ci_lower': 0.5721855, 'ci_upper': 0.5917799} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78, 'ci_lower': 0.75, 'ci_upper': 0.8} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01871484, 'ci_lower': 0.01517095, 'ci_upper': 0.0232003} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0187256, 'ci_lower': 0.01506559, 'ci_upper': 0.02314554} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0199569, 'ci_lower': 0.01607829, 'ci_upper': 0.02453676} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01859661, 'ci_lower': 0.01476562, 'ci_upper': 0.02283747} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01615694, 'ci_lower': 0.01278626, 'ci_upper': 0.020327} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37553032, 'ci_lower': 1.32885232, 'ci_upper': 1.42384795} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.31883934, 'ci_lower': 0.28431565, 'ci_upper': 0.35336303} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37576394, 'ci_lower': 1.32906928, 'ci_upper': 1.42409914} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.31900917, 'ci_lower': 0.28447891, 'ci_upper': 0.35353943} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.38924704, 'ci_lower': 1.34216238, 'ci_upper': 1.43798349} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.3287619, 'ci_lower': 0.29428203, 'ci_upper': 0.36324178} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37315168, 'ci_lower': 1.32665979, 'ci_upper': 1.42127286} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.3171086, 'ci_lower': 0.28266434, 'ci_upper': 0.35155285} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.34393774, 'ci_lower': 1.29844261, 'ci_upper': 1.39102695} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.29560392, 'ci_lower': 0.26116555, 'ci_upper': 0.33004229} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.47, 'ci_lower': 1.32, 'ci_upper': 1.65} | Agent Input |
| validation_sample_size | n=90,274 | n=90,274 | n=90,274 | n=90,274 | n=90,274 | n=11,813 | Agent Input |
| samples_training | n=13,496 | n=13,496 | n=13,496 | n=13,496 | n=13,496 | n=279,819 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | DEV: EUR (100%) / EVAL: AFR (14%), AMR (14%), ASN (14%), EUR (29%), MAE (29%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Genome-wide polygenic score to predict chronic kidney disease across ancestries. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Nat Med | Agent Input |
| date_release | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2023-12-19 | 2022-01-10 | Agent Input |
| variants_number | 1050295 | 1050295 | 1135455 | 846995 | 1109217 | 471316 | Agent Input |
| covariates | 0 | 0 | 0 | 0 | 0 | age, sex, alcohol, smoking, hypertension, diabetes, body mass index, nonsteroidal anti-inflammatory drug and angiotensin-converting enzyme inhibitor/angiotensin receptor blocker use, and visit year | Agent Input |


### ovarian carcinoma

Candidate pool: `21` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000793 | PGS000082 | PGS003741 | PGS004249 | PGS000158 | PGS000082 | Agent Input |
| AoU benchmark rank | 1/21 | 2/21 | 3/21 | 4/21 | 5/21 | 2/21 | Benchmark Only |
| AoU benchmark AUC | 0.6536 | 0.6420 | 0.6364 | 0.6334 | 0.6315 | 0.6420 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 7/10 trials | Benchmark Only |
| trait_reported | Ovarian cancer | Ovarian cancer | Ovarian cancer | Ovarian cancer | Ovarian cancer | Ovarian cancer | Agent Input |
| trait_efo | ovarian carcinoma | ovarian carcinoma | ovarian carcinoma | ovarian carcinoma | ovarian carcinoma | ovarian carcinoma | Agent Input |
| phenotyping_reported | Incident ovarian cancer | Incident ovarian cancer | Ovarian cancer | Ovarian cancer | Ovarian cancer | Incident ovarian cancer | Agent Input |
| method_name | 36 variants from Graff et al (PGS000082) with inverse variant weights | Genome-wide significant variants | Genome-wide significant SNPs | PRSice-2 | Pruning and Thresholding (P+T) | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM002064 | PPM002048 | PPM018497 | PPM020306 | PPM000478 | PPM002048 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 3 | 1 | 1 | 2 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6600 | 0.6560 | N/A | N/A | N/A | 0.6560 | Agent Input |
| performance_metrics.full_model_r2 | 0.1930 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.654, 'se': 0.015} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.656} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.655, 'se': 0.015} | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.656} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.655, 'se': 0.015} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.193} | N/A | N/A | N/A | {'name_long': 'Mean realative risk', 'name_short': 'Mean realative risk', 'estimate': 1.12, 'ci_lower': 1.08, 'ci_upper': 1.16} {'name_long': 'Wilcoxon test (case vs. control) p-value', 'name_short': 'Wilcoxon test (case vs. control) p-value', 'estimate': 0.000145} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.2, 'ci_lower': 1.1, 'ci_upper': 1.32} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.13, 'ci_lower': 1.04, 'ci_upper': 1.24} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.15, 'ci_lower': 1.04, 'ci_upper': 1.28} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.03, 'ci_upper': 1.31} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.13, 'ci_lower': 1.04, 'ci_upper': 1.24} | Agent Input |
| validation_sample_size | n=211,958 | n=211,958 | n=501 | n=133,830 | n=7,551 | n=211,958 | Agent Input |
| samples_training | N/A | N/A | n=437 | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AOCS B58C BCFR-AU BCFR-NY BCFR-PA BCFR-UTAH BFBOCC BMBSA BOCC BOCS BRICOH BioVU CIMBA CNIO COH CONSIT_TEAM CoRGI CopBCS DEMOKRITOS DFCI DKFZ DOVE DPMS EMBRACE EPIC FCCC FOTS FROC&GEOCS G-FaST GC-HBOC GEMO GOCS Georgetown HCSC HEBCS HEBON HJOCS HMOCS HOCS HOPE HUNBOCS HUOCS HUVH HeOCS ICO ICR IHCC INHERIT IOVHBOCS IPOBCS KUMC LAC-CCOC LUHR MALOVA MAYO MCGILL MDACCS MEC MOCS MOF MSKCC MUV NBS NC-BCFR NCI NCOCS NECC NHS NJOCS NNPIO NOCS NRG_ONCOLOGY NSUHS Nijmegen OCGN ODZH OFBCR OSUCCG OUH OVAL-BC PLCO POCS RMH RMH-OCS SEARCH SEARCH-OCS SHMC SWE SWE-BRCA Sisters TAMPERE TBOCS UBNS UC UCIOCS UCSF UDP UKCRC UKFOCR UKGRFOCR UKOPS UPENN UPITT VFCTG WCPSOCCI WCRI WOCS deCODE kConFab | AOCS B58C BCFR-AU BCFR-NY BCFR-PA BCFR-UTAH BFBOCC BMBSA BOCC BOCS BRICOH BioVU CNIO COH CONSIT_TEAM CoRGI CopBCS DEMOKRITOS DFCI DKFZ DOVE DPMS EMBRACE EPIC FCCC FOTS FROC&GEOCS G-FaST GC-HBOC GEMO GOCS Georgetown HCSC HEBCS HEBON HJOCS HMOCS HOCS HOPE HUNBOCS HUOCS HUVH HeOCS ICO ICR IHCC INHERIT IOVHBOCS IPOBCS KUMC LAC-CCOC LUHR MALOVA MAYO MCGILL MDACCS MEC MOCS MOF MSKCC MUV NBS NC-BCFR NCI NCOCS NECC NHS NJOCS NNPIO NOCS NRG_ONCOLOGY NSUHS Nijmegen OCGN ODZH OFBCR OSUCCG OUH OVAL-BC PLCO POCS RMH RMH-OCS SEARCH SEARCH-OCS SHMC SWE SWE-BRCA Sisters TAMPERE TBOCS UBNS UC UCIOCS UCSF UDP UKCRC UKFOCR UKGRFOCR UKOPS UPENN UPITT VFCTG WCPSOCCI WCRI WOCS deCODE kConFab | UKB | N/A | B58C CoRGI RMH-OCS SEARCH-OCS UKFOCR UKOPS | AOCS B58C BCFR-AU BCFR-NY BCFR-PA BCFR-UTAH BFBOCC BMBSA BOCC BOCS BRICOH BioVU CNIO COH CONSIT_TEAM CoRGI CopBCS DEMOKRITOS DFCI DKFZ DOVE DPMS EMBRACE EPIC FCCC FOTS FROC&GEOCS G-FaST GC-HBOC GEMO GOCS Georgetown HCSC HEBCS HEBON HJOCS HMOCS HOCS HOPE HUNBOCS HUOCS HUVH HeOCS ICO ICR IHCC INHERIT IOVHBOCS IPOBCS KUMC LAC-CCOC LUHR MALOVA MAYO MCGILL MDACCS MEC MOCS MOF MSKCC MUV NBS NC-BCFR NCI NCOCS NECC NHS NJOCS NNPIO NOCS NRG_ONCOLOGY NSUHS Nijmegen OCGN ODZH OFBCR OSUCCG OUH OVAL-BC PLCO POCS RMH RMH-OCS SEARCH SEARCH-OCS SHMC SWE SWE-BRCA Sisters TAMPERE TBOCS UBNS UC UCIOCS UCSF UDP UKCRC UKFOCR UKGRFOCR UKOPS UPENN UPITT VFCTG WCPSOCCI WCRI WOCS deCODE kConFab | Agent Input |
| publication.title | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Prognostic evaluation of polygenic risk score underlying pan-cancer analysis: evidence from two large-scale cohorts. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Systematic evaluation of cancer-specific genetic risk score for 11 types of cancer in The Cancer Genome Atlas and Electronic Medical Records and Genomics cohorts. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | EBioMedicine | NPJ Precis Oncol | Cancer Med | Nat Commun | Agent Input |
| date_release | 2021-05-28 | 2020-02-12 | 2023-06-01 | 2023-12-15 | 2020-04-29 | 2020-02-12 | Agent Input |
| variants_number | 36 | 36 | 28 | 25 | 11 | 36 | Agent Input |
| covariates | Age at assessment, family history of breast cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), BMI*menopausal status | Age at assessment, family history of breast cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), BMI*menopausal status | Unknown | first 10 genetic principal components | Unknown | Age at assessment, family history of breast cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), BMI*menopausal status | Agent Input |


### basal cell carcinoma

Candidate pool: `20` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003417 | PGS003416 | PGS000453 | PGS000452 | PGS000455 | PGS000119 | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | 13/20 | Benchmark Only |
| AoU benchmark AUC | 0.6391 | 0.6356 | 0.6213 | 0.6213 | 0.6213 | 0.6120 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Basal cell carcinoma | Basal cell carcinoma (MTAG) | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Agent Input |
| trait_efo | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | basal cell carcinoma | Agent Input |
| phenotyping_reported | Keratinocyte cancers | Keratinocyte cancers | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Basal cell carcinoma | Agent Input |
| method_name | Genome-wide significant SNPs | Genome-wide significant SNPs | GWAS Hits | GWAS Hits | Pruning and Thresholding (P+T) | GWAS Catalog SNPs | Agent Input |
| performance_metrics.selected_performance_id | PPM017070 | PPM017069 | PPM001138 | PPM001137 | PPM001140 | PPM000341 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.6110 | 0.6320 | 0.6110 | 0.6400 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0301 | 0.0487 | 0.0301 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.611, 'ci_lower': 0.604, 'ci_upper': 0.619} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.632, 'ci_lower': 0.616, 'ci_upper': 0.647} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.611, 'ci_lower': 0.604, 'ci_upper': 0.619} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64, 'ci_lower': 0.62, 'ci_upper': 0.66} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0301} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0813} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.8, 'ci_lower': 2.33, 'ci_upper': 3.36} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0487} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.106} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 3.61, 'ci_lower': 2.53, 'ci_upper': 5.15} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0301} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0813} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.8, 'ci_lower': 2.33, 'ci_upper': 3.36} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.56, 'ci_lower': 1.45, 'ci_upper': 1.67} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.66, 'ci_lower': 1.55, 'ci_upper': 1.79} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.511, 'ci_lower': 1.47, 'ci_upper': 1.554} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.413, 'se': 0.0142} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.663, 'ci_lower': 1.57, 'ci_upper': 1.761} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.508, 'se': 0.0293} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.511, 'ci_lower': 1.47, 'ci_upper': 1.554} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.413, 'se': 0.0142} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.65, 'ci_lower': 1.56, 'ci_upper': 1.75} | Agent Input |
| validation_sample_size | n=18,933 | n=18,933 | n=60,018 | n=11,322 | n=60,018 | n=20,468 | Agent Input |
| samples_training | N/A | N/A | n=61,038 | n=11,734 | n=61,038 | n=10,234 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | GERA QSKIN UKB eMERGE | UKB | MGI | UKB | MGI | Agent Input |
| publication.title | A multi-phenotype analysis reveals 19 susceptibility loci for basal cell carcinoma and 15 for squamous cell carcinoma. | A multi-phenotype analysis reveals 19 susceptibility loci for basal cell carcinoma and 15 for squamous cell carcinoma. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Exploring various polygenic risk scores for skin cancer in the phenomes of the Michigan genomics initiative and the UK Biobank with a visual catalog: PRSWeb. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | PLoS Genet | Agent Input |
| date_release | 2023-02-08 | 2023-02-08 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2020-03-27 | Agent Input |
| variants_number | 273 | 462 | 28 | 28 | 28 | 32 | Agent Input |
| covariates | age, sex, 10 ancesty PCs | age, sex, 10 ancesty PCs | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch, PC1-4 | Agent Input |


### sleep apnea

Candidate pool: `20` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005220 | PGS005219 | PGS003479 | PGS003213 | PGS003857 | PGS005220 | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | 1/20 | Benchmark Only |
| AoU benchmark AUC | 0.5784 | 0.5454 | 0.5418 | 0.5217 | 0.5167 | 0.5784 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 7/10 trials | Benchmark Only |
| trait_reported | Obstructive sleep apnea (UnadjustedBMI) | Obstructive sleep apnea (AdjustedBMI) | Obstructive sleep apnea | Sleep apnea | Obstructive sleep apnea | Obstructive sleep apnea (UnadjustedBMI) | Agent Input |
| trait_efo | obstructive sleep apnea | obstructive sleep apnea | obstructive sleep apnea | sleep apnea | obstructive sleep apnea | obstructive sleep apnea | Agent Input |
| phenotyping_reported | Obstructive sleep apnea | Obstructive sleep apnea | DBP | Sleep Apnea | BMI adjusted obstructive sleep apnea | Obstructive sleep apnea | Agent Input |
| method_name | weighted PRSsummation PRS-CSs | weighted PRSsummation PRS-CSs | LDpred2 | PRS-CS | Genome-wide significant SNPs | weighted PRSsummation PRS-CSs | Agent Input |
| performance_metrics.selected_performance_id | PPM022620 | PPM022619 | PPM017318 | PPM015955 | PPM018710 | PPM022620 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | Hispanic or Latin American | European | African unspecified, Asian unspecified, European, Hispanic or Latin American, Not reported | European, African American or Afro-Caribbean, East Asian, Hispanic or Latin American | Agent Input |
| performance_metrics.record_count | 1 | 1 | 34 | 1 | 2 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7900 | 0.7900 | N/A | 0.5270 | 0.7700 | 0.7900 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.527, 'ci_lower': 0.517, 'ci_upper': 0.536} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.77, 'ci_lower': 0.75, 'ci_upper': 0.78} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.98, 'ci_lower': 1.74, 'ci_upper': 2.24} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.038, 'se': 0.093} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.106, 'ci_lower': 1.071, 'ci_upper': 1.142} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.101, 'se': 0.0162} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.014, 'se': 0.017} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.53, 'ci_lower': 1.39, 'ci_upper': 1.68} | Agent Input |
| validation_sample_size | n=21,975 | n=21,975 | n=1,115 | n=21,354 | n=40,193 | n=21,975 | Agent Input |
| samples_training | N/A | N/A | N/A | n=21,209 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (19%), AMR (8%), ASN (1%), EUR (72%) / EVAL: MAE (100%) | GWAS: NR (10%), AFR (12%), AMR (5%), ASN (90%), EUR (82%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | FinnGen MGBB MVP | FinnGen MGBB MVP | N/A | UKB | MVP | FinnGen MGBB MVP | Agent Input |
| publication.title | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Genetic determinants of cardiometabolic and pulmonary phenotypes and obstructive sleep apnoea in HCHS/SOL. | ExPRSweb: An online repository with polygenic risk scores for common health-related exposures. | Genome-wide association study of obstructive sleep apnoea in the Million Veteran Program uncovers genetic heterogeneity by sex. | Polygenic scores for obstructive sleep apnoea reveal pathways contributing to cardiovascular disease. | Agent Input |
| publication.journal | EBioMedicine | EBioMedicine | EBioMedicine | Am J Hum Genet | EBioMedicine | EBioMedicine | Agent Input |
| date_release | 2025-06-16 | 2025-06-16 | 2023-03-24 | 2022-11-23 | 2023-09-01 | 2025-06-16 | Agent Input |
| variants_number | 984184 | 982740 | 836839 | 1111194 | 18 | 984184 | Agent Input |
| covariates | age, sex, self-reported race/ethnicity , BMI and 11PCs | age, sex, self-reported race/ethnicity , BMI and 11PCs | Age, sex, center, 5 genetic PCs, Hispanic/Latino background, BMI | SEX,AGE,Batch,PC1,PC2,PC3,PC4 | BMI, age, sex, genetic batch, PCs 1-10 | age, sex, self-reported race/ethnicity , BMI and 11PCs | Agent Input |


### urinary bladder cancer

Candidate pool: `20` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000152 | PGS001807 | PGS000782 | PGS000071 | PGS000613 | PGS000611 | Agent Input |
| AoU benchmark rank | 1/20 | 2/20 | 3/20 | 4/20 | 5/20 | 11/20 | Benchmark Only |
| AoU benchmark AUC | 0.5682 | 0.5583 | 0.5565 | 0.5565 | 0.5534 | 0.5481 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | Benchmark Only |
| trait_reported | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Bladder cancer | Agent Input |
| trait_efo | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | urinary bladder carcinoma | Agent Input |
| phenotyping_reported | Bladder cancer | Cancer of bladder | Incident blader cancer | Incident blader cancer | Cancer of bladder | Cancer of bladder | Agent Input |
| method_name | Pruning and Thresholding (P+T) | Penalized regression (bigstatsr) | 15 variants from Graff et al (PGS000071) with inverse variant weights | Genome-wide significant variants | Pruning and Thresholding (P+T) | GWAS Hits | Agent Input |
| performance_metrics.selected_performance_id | PPM000472 | PPM009359 | PPM002053 | PPM002037 | PPM001298 | PPM001296 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 8 | 1 | 3 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.8040 | 0.8030 | 0.5710 | 0.5670 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.6280 | N/A | 0.0125 | 0.0114 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.804} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.814, 'se': 0.008} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.803} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.813, 'se': 0.008} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.571, 'ci_lower': 0.555, 'ci_upper': 0.588} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.567, 'ci_lower': 0.551, 'ci_upper': 0.584} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Mean realative risk', 'name_short': 'Mean realative risk', 'estimate': 1.04, 'ci_lower': 1.0, 'ci_upper': 1.08} {'name_long': 'Wilcoxon test (case vs. control) p-value', 'name_short': 'Wilcoxon test (case vs. control) p-value', 'estimate': 0.00377} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0197, 'ci_lower': 0.0058, 'ci_upper': 0.0336} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.628} | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0125} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.91, 'ci_lower': 1.99, 'ci_upper': 4.24} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0114} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0821} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.66, 'ci_lower': 1.79, 'ci_upper': 3.93} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.3, 'ci_lower': 1.22, 'ci_upper': 1.39} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.28, 'ci_lower': 1.2, 'ci_upper': 1.37} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.301, 'ci_lower': 1.227, 'ci_upper': 1.379} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.263, 'se': 0.0299} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.284, 'ci_lower': 1.211, 'ci_upper': 1.361} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.25, 'se': 0.0298} | Agent Input |
| validation_sample_size | n=13,770 | n=19,893 | n=391,888 | n=391,888 | n=13,530 | n=13,530 | Agent Input |
| samples_training | N/A | n=391,124 | N/A | N/A | n=12,992 | n=12,992 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ICR NBCS NBS UMC deCODE | UKB | ASHRAM ATBC BBCS_b CPSII DBCS EAGLE EPIC FPCC FrBCS HPFS IBCS ICR LABCS LBCS MEC MSKBCS NBCS NBS NCBCS NEBCS NHS NeuBCS PLCO SANBCS SBCS SpBCS TBCS TXBCS UMC WHI deCODE | ATBC BBCS_b CPSII EAGLE EPIC FPCC FrBCS HPFS ICR LABCS MEC NBCS NBS NEBCS NHS PLCO SpBCS TXBCS UMC WHI deCODE | UKB | UKB | Agent Input |
| publication.title | Systematic evaluation of cancer-specific genetic risk score for 11 types of cancer in The Cancer Genome Atlas and Electronic Medical Records and Genomics cohorts. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Agent Input |
| publication.journal | Cancer Med | Am J Hum Genet | Nat Commun | Nat Commun | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2020-04-29 | 2022-01-10 | 2021-05-28 | 2020-02-12 | 2020-12-15 | 2020-12-15 | Agent Input |
| variants_number | 10 | 291 | 15 | 15 | 15 | 13 | Agent Input |
| covariates | Unknown | sex, age, birth date, deprivation index, 16 PCs | Age at assessment, sex, genotyping array, PCs(1-15), cigarette pack-years, smoking status(never vs. former vs. current), body mass index | Age at assessment, sex, genotyping array, PCs(1-15), cigarette pack-years, smoking status(never vs. former vs. current), body mass index | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Agent Input |


### glaucoma

Candidate pool: `15` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002761 | PGS004765 | PGS004766 | PGS004944 | PGS001792 | PGS000137 | Agent Input |
| AoU benchmark rank | 1/15 | 2/15 | 3/15 | 4/15 | 5/15 | 6/15 | Benchmark Only |
| AoU benchmark AUC | 0.6258 | 0.6215 | 0.6212 | 0.5989 | 0.5967 | 0.5959 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 8/10 trials | Benchmark Only |
| trait_reported | Glaucoma | Glaucoma | Glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Glaucoma | Agent Input |
| trait_efo | glaucoma | glaucoma | glaucoma | open-angle glaucoma | glaucoma | glaucoma | Agent Input |
| phenotyping_reported | Glaucoma | Glaucoma | Glaucoma | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma | Primary open-angle glaucoma (POAG) | Agent Input |
| method_name | PRS-CS | PRSmix | PRSmixPlus | Lassosum | PRS-CS-auto | Clumping and Thresholding (C+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM014961 | PPM020990 | PPM020991 | PPM021744 | PPM009296 | PPM000422 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | African unspecified, Hispanic or Latin American, East Asian, South Asian, European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 8 | 2 | 14 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0321 | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.7480 | 0.7770 | 0.8000 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0310 | 0.0310 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.748} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.777} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.031, 'ci_lower': 0.024, 'ci_upper': 0.038} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.031, 'ci_lower': 0.024, 'ci_upper': 0.038} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.03209} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.68, 'ci_lower': 1.59, 'ci_upper': 1.78} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.74, 'ci_lower': 1.71, 'ci_upper': 1.77} | N/A | N/A | Agent Input |
| validation_sample_size | n=39,444 | n=9,462 | n=9,462 | n=407,667 | n=347,396 | n=1,795 | Agent Input |
| samples_training | N/A | n=37,851 | n=37,851 | N/A | N/A | n=8,004 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: AFR (2%), EAS (25%), EUR (72%), OTH (90%) / EVAL: ASN (50%), EUR (50%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (75%), MAE (12%), SAS (12%) | Agent Input |
| training_development_cohorts | N/A | AllofUs | AllofUs | N/A | BBJ BioMe TWB UCLA | ANZRAG | Agent Input |
| publication.title | Systematic comparison of family history and polygenic risk across 24 common diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Multitrait analysis of glaucoma identifies new risk loci and enables polygenic prediction of disease susceptibility and progression. | Agent Input |
| publication.journal | Am J Hum Genet | Cell Genom | Cell Genom | JAMA Ophthalmol | Cell Genom | Nat Genet | Agent Input |
| date_release | 2022-11-07 | 2024-03-28 | 2024-03-28 | 2024-08-29 | 2022-09-08 | 2020-03-27 | Agent Input |
| variants_number | 1082518 | 835476 | 837948 | 144019 | 911402 | 2673 | Agent Input |
| covariates | age, sex, 10 PCs, technical covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | Age, age2, sex, ancestry | sex,age,age2,age*sex,age^2*sex, 20PCs | age, sex, self-reported family history | Agent Input |


### uterine carcinoma

Candidate pool: `14` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000075 | PGS000786 | PGS003381 | PGS002735 | PGS004244 | PGS001795 | Agent Input |
| AoU benchmark rank | 1/14 | 2/14 | 3/14 | 4/14 | 5/14 | 9/14 | Benchmark Only |
| AoU benchmark AUC | 0.6120 | 0.6113 | 0.5970 | 0.5609 | 0.5519 | 0.5044 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Endometrial cancer | Endometrial cancer | Uterine endometrial carcinoma | Endometrial cancer | Endometrial cancer | Uterine cancer | Agent Input |
| trait_efo | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | uterine carcinoma | Agent Input |
| phenotyping_reported | Incident endometrial cancer | Incident endometrial cancer | uterine endometrial carcinoma | Risk of endometrial cancer | Endometrial cancer | Uterine cancer | Agent Input |
| method_name | Genome-wide significant variants | 9 variants from Graff et al (PGS000075) with inverse variant weights | lassosum | Genome-wide significant variants | PRSice-2 | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | PPM002041 | PPM002057 | PPM016256 | PPM014832 | PPM020301 | PPM009299 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 3 | 1 | 1 | 2 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0019 | Agent Input |
| performance_metrics.full_model_auc | 0.7550 | 0.7540 | 0.7610 | 0.5600 | N/A | 0.6600 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.4860 | 0.1100 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.755} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.754} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.761} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.56, 'ci_lower': 0.54, 'ci_upper': 0.57} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.486} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11} | {'name_long': 'Odds ratio (OR, third vs first tertile)', 'name_short': 'Odds ratio (OR, third vs first tertile)', 'estimate': 1.55, 'ci_lower': 1.37, 'ci_upper': 1.74} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.001948} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.19, 'ci_lower': 1.1, 'ci_upper': 1.29} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.18, 'ci_lower': 1.09, 'ci_upper': 1.27} | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.25, 'ci_lower': 1.14, 'ci_upper': 1.36} | N/A | Agent Input |
| validation_sample_size | n=212,156 | n=212,156 | n=144,479 | n=118,636 | n=133,830 | n=170,276 | Agent Input |
| samples_training | N/A | N/A | N/A | n=1,757 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (15%), EUR (84%), OTH (80%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | ANECS B58C CoRGI E2C2 HCS NBBS NSECG QIMR SEARCH WTCCC | N/A | N/A | N/A | BBJ BioMe BioVU CCPM CKB EB FinnGen HUNT MGBB MGI deCODE | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Development and evaluation of polygenic risk scores for prediction of endometrial cancer risk in European women. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Cancer Res | Genet Med | NPJ Precis Oncol | Cell Genom | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2023-01-19 | 2022-07-21 | 2023-12-15 | 2022-09-08 | Agent Input |
| variants_number | 9 | 9 | 529365 | 19 | 16 | 911692 | Agent Input |
| covariates | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | age, top 20 genetic principal components | Unknown | first 10 genetic principal components | sex,age,age2,age*sex,age^2*sex, 20PCs | Agent Input |


### osteoporosis

Candidate pool: `13` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004810 | PGS004809 | PGS002768 | PGS001274 | PGS001273 | PGS001274 | Agent Input |
| AoU benchmark rank | 1/13 | 2/13 | 3/13 | 4/13 | 5/13 | 4/13 | Benchmark Only |
| AoU benchmark AUC | 0.5758 | 0.5742 | 0.5647 | 0.5628 | 0.5544 | 0.5628 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Osteoporosis | Osteoporosis | Osteoporosis | Osteoporosis without pathological fracture (time-to-event) | Osteoporosis | Osteoporosis without pathological fracture (time-to-event) | Agent Input |
| trait_efo | osteoporosis | osteoporosis | osteoporosis, heel bone mineral density | osteoporosis | osteoporosis | osteoporosis | Agent Input |
| phenotyping_reported | Osteoporosis | Osteoporosis | Osteoporosis | TTE osteoporosis without pathological fracture | Osteoporosis | TTE osteoporosis without pathological fracture | Agent Input |
| method_name | PRSmixPlus | PRSmix | PRS-CS | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM021035 | PPM021034 | PPM014968 | PPM008870 | PPM008865 | PPM008870 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 5 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.5759 | 0.5685 | 0.5759 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0095 | 0.0069 | 0.0095 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.7965 | 0.7897 | 0.7965 | Agent Input |
| performance_metrics.full_model_r2 | 0.0220 | 0.0110 | N/A | 0.1570 | 0.1457 | 0.1570 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | 0.0078 | 0.0048 | 0.0078 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79652, 'ci_lower': 0.78363, 'ci_upper': 0.8094} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78972, 'ci_lower': 0.77584, 'ci_upper': 0.8036} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79652, 'ci_lower': 0.78363, 'ci_upper': 0.8094} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.022, 'ci_lower': 0.016, 'ci_upper': 0.028} | {'name_long': 'Incremental R2 (Full model versus model with only covariates)', 'name_short': 'Incremental R2 (Full model versus model with only covariates)', 'estimate': 0.011, 'ci_lower': 0.007, 'ci_upper': 0.015} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.15697} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00777} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00945} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57595, 'ci_lower': 0.55816, 'ci_upper': 0.59374} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.14567} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00477} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00688} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.5685, 'ci_lower': 0.55009, 'ci_upper': 0.58691} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.15697} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00777} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00945} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57595, 'ci_lower': 0.55816, 'ci_upper': 0.59374} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.25, 'ci_upper': 1.38} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=9,462 | n=9,462 | n=39,444 | n=24,905 | n=24,905 | n=24,905 | Agent Input |
| samples_training | n=37,851 | n=37,851 | N/A | n=269,704 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs | AllofUs | N/A | UKB | UKB | UKB | Agent Input |
| publication.title | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Cell Genom | Cell Genom | Am J Hum Genet | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2024-03-28 | 2024-03-28 | 2022-11-07 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 1876917 | 863731 | 1091549 | 1270 | 316 | 1270 | Agent Input |
| covariates | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, PC9, PC10 | age, sex, 10 PCs, technical covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### testicular carcinoma

Candidate pool: `13` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000796 | PGS000600 | PGS001164 | PGS000599 | PGS000597 | PGS000604 | Agent Input |
| AoU benchmark rank | 1/12 | 2/12 | 3/12 | 4/12 | 5/12 | 9/12 | Benchmark Only |
| AoU benchmark AUC | 0.9212 | 0.9128 | 0.9044 | 0.9021 | 0.8730 | 0.7468 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 8/10 trials | Benchmark Only |
| trait_reported | Testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Malignant neoplasm of testis | Agent Input |
| trait_efo | testicular carcinoma, Testicular Germ Cell Tumor | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | testicular carcinoma | Agent Input |
| phenotyping_reported | Incident testicular cancer | Malignant neoplasm of testis | Testicular cancer | Malignant neoplasm of testis | Malignant neoplasm of testis | Malignant neoplasm of testis | Agent Input |
| method_name | 52 variants from Graff et al (PGS000086) with inverse variant weights | lassosum | snpnet | Pruning and Thresholding (P+T) | lassosum | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM002067 | PPM001285 | PPM008544 | PPM001284 | PPM001282 | PPM001289 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 3 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6296 | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0157 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7870 | 0.6360 | 0.8391 | 0.6370 | 0.6560 | 0.7030 | Agent Input |
| performance_metrics.full_model_r2 | 0.6050 | 0.0460 | 0.1291 | 0.0473 | 0.0487 | 0.0882 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0313 | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.787} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.766, 'se': 0.033} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.636, 'ci_lower': 0.565, 'ci_upper': 0.698} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.83915, 'ci_lower': 0.8185, 'ci_upper': 0.85981} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.637, 'ci_lower': 0.568, 'ci_upper': 0.703} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.656, 'ci_lower': 0.593, 'ci_upper': 0.717} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.703, 'ci_lower': 0.659, 'ci_upper': 0.745} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.605} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.046} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0839} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 6.35, 'ci_lower': 1.81, 'ci_upper': 22.3} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1291} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03126} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01573} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.62956, 'ci_lower': 0.58302, 'ci_upper': 0.67611} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0473} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0844} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.35, 'ci_lower': 1.08, 'ci_upper': 17.5} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0487} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.084} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.72, 'ci_lower': 0.568, 'ci_upper': 13.1} | {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0793} {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0882} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.6, 'ci_lower': 1.75, 'ci_upper': 12.1} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.26, 'ci_lower': 1.71, 'ci_upper': 2.99} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.619, 'ci_lower': 1.267, 'ci_upper': 2.067} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.482, 'se': 0.125} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.628, 'ci_lower': 1.281, 'ci_upper': 2.069} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.487, 'se': 0.122} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.667, 'ci_lower': 1.296, 'ci_upper': 2.143} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.511, 'se': 0.128} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.106, 'ci_lower': 1.729, 'ci_upper': 2.565} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.745, 'se': 0.101} | Agent Input |
| validation_sample_size | n=179,537 | n=755 | n=67,425 | n=755 | n=755 | n=1,484 | Agent Input |
| samples_training | N/A | n=776 | n=269,704 | n=776 | n=776 | n=1,671 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | B58C BCAC FCCC NCI Penn PennCATH SEARCH Sweden UKBS UKGPCS UKTCC UPENN | MGI | UKB | MGI | MGI | UKB | Agent Input |
| publication.title | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | PLoS Genet | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2021-05-28 | 2020-12-15 | 2021-10-21 | 2020-12-15 | 2020-12-15 | 2020-12-15 | Agent Input |
| variants_number | 52 | 250 | 280 | 31 | 771 | 44 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15) | age, sex, batch PCs 1-4 | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Agent Input |


### parkinson disease

Candidate pool: `11` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000903 | PGS004924 | PGS000902 | PGS000750 | PGS003763 | PGS000903 | Agent Input |
| AoU benchmark rank | 1/11 | 2/11 | 3/11 | 4/11 | 5/11 | 1/11 | Benchmark Only |
| AoU benchmark AUC | 0.5616 | 0.5523 | 0.5500 | 0.5430 | 0.5421 | 0.5616 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Agent Input |
| trait_efo | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Parkinson disease | Agent Input |
| phenotyping_reported | Parkinson's disease | Parkinson's disease | Parkinson's disease | Parkinson's disease | Incident Parkinson Disease | Parkinson's disease | Agent Input |
| method_name | Clumping and Thresholding (C+T) | Genome-wide significant SNPs | Genome-wide significant variants | Genome-wide significant variants | Genome-wide significant SNPs | Clumping and Thresholding (C+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM002664 | PPM021702 | PPM002665 | PPM001904 | PPM018563 | PPM002664 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, NR | European, African unspecified, Not reported | European, NR | European, NR | European | European, NR | Agent Input |
| performance_metrics.record_count | 5 | 2 | 6 | 3 | 2 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6920 | N/A | 0.6510 | 0.7030 | N/A | 0.6920 | Agent Input |
| performance_metrics.full_model_r2 | 0.0540 | N/A | N/A | N/A | N/A | 0.0540 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.692} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.651, 'ci_lower': 0.617, 'ci_upper': 0.684} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.703, 'ci_lower': 0.698, 'ci_upper': 0.708} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.692} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.054} {'name_long': 'Odds Ratio (OR, top 25% vs bottom 25%)', 'name_short': 'Odds Ratio (OR, top 25% vs bottom 25%)', 'estimate': 6.25, 'ci_lower': 4.26, 'ci_upper': 9.28} | {'name_long': 'Odds ratio (OR, top vs bottom PGS quartile)', 'name_short': 'Odds ratio (OR, top vs bottom PGS quartile)', 'estimate': 3.79, 'ci_lower': 1.64, 'ci_upper': 8.73} | N/A | N/A | {'name_long': 'Hazard ratio (HR, high vs low tertile)', 'name_short': 'Hazard ratio (HR, high vs low tertile)', 'estimate': 1.72, 'ci_lower': 1.54, 'ci_upper': 1.93} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.054} {'name_long': 'Odds Ratio (OR, top 25% vs bottom 25%)', 'name_short': 'Odds Ratio (OR, top 25% vs bottom 25%)', 'estimate': 6.25, 'ci_lower': 4.26, 'ci_upper': 9.28} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.709, 'se': 0.072} | N/A | N/A | N/A | N/A | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.709, 'se': 0.072} | Agent Input |
| validation_sample_size | n=999 | n=3,482 | n=999 | n=486 | n=314,998 | n=999 | Agent Input |
| samples_training | n=1,473,098 | N/A | n=1,473,098 | N/A | N/A | n=1,473,098 | Agent Input |
| ancestry_distribution | GWAS: MAE (100%) / DEV: MAE (100%) / EVAL: EUR (33%), MAE (33%), SAS (33%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: MAE (100%) / DEV: MAE (100%) / EVAL: NR (40%), MAE (60%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / DEV: MAE (100%) / EVAL: EUR (33%), MAE (33%), SAS (33%) | Agent Input |
| training_development_cohorts | 23andMe HBS IPDGC PDBP PPMI UKB | N/A | 23andMe HBS IPDGC PDBP PPMI UKB | N/A | N/A | 23andMe HBS IPDGC PDBP PPMI UKB | Agent Input |
| publication.title | Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. | Polygenic risk score for Parkinson's disease and olfaction among middle-aged to older women. | Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. | Excess of singleton loss-of-function variants in Parkinson's disease contributes to genetic risk. | Physical Frailty, Genetic Predisposition, and Incident Parkinson Disease. | Identification of novel risk loci, causal insights, and heritable risk for Parkinson's disease: a meta-analysis of genome-wide association studies. | Agent Input |
| publication.journal | Lancet Neurol | Parkinsonism Relat Disord | Lancet Neurol | J Med Genet | JAMA Neurol | Lancet Neurol | Agent Input |
| date_release | 2021-09-17 | 2024-07-31 | 2021-09-17 | 2021-03-22 | 2023-08-04 | 2021-09-17 | Agent Input |
| variants_number | 1805 | 90 | 90 | 43 | 44 | 1805 | Agent Input |
| covariates | PCs(1-5), age, sex | Age, race, 5 PCs, self-reported sense of smell, education, smoking status, self-reported health status, and PM2.5 and NO2 in 2006 | PCs(1-5), age, sex | Sex, singleton loss of function variant count, Parkinson's disease family history. | genotyping array and the first 10 principal components of ancestry | PCs(1-5), age, sex | Agent Input |


### systemic lupus erythematosus

Candidate pool: `11` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000771 | PGS000772 | PGS000803 | PGS004917 | PGS000196 | PGS003960 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 9/10 | Benchmark Only |
| AoU benchmark AUC | 0.6046 | 0.5961 | 0.5925 | 0.5817 | 0.5783 | 0.5623 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 8/10 trials | Benchmark Only |
| trait_reported | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Systemic lupus erythematosus | Agent Input |
| trait_efo | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | systemic lupus erythematosus | Agent Input |
| phenotyping_reported | Renal disease age of onset | Renal disease | Erythematous conditions | Systemic lupus erythematosus | Systemic lupus erythematosus diagnosis in patient with arthritis | Systemic lupus erythematosus | Agent Input |
| method_name | Genome-wide significant variants | Genome-wide significant variants | Variants significantly associated with systemic lupus erythematosus | Clumping of genome-wide significant variants | Pruning and Thresholding (P+T) | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | PPM001996 | PPM001997 | PPM002104 | PPM021383 | PPM000573 | PPM019118 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European, Not reported, European, Asian unspecified, African unspecified, Not reported | European | European, African unspecified, Asian unspecified, Not reported | Agent Input |
| performance_metrics.record_count | 2 | 1 | 15 | 1 | 3 | 6 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5760 | N/A | N/A | 0.6960 | 0.7900 | 0.8900 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.576, 'ci_lower': 0.518, 'ci_upper': 0.634} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.79, 'ci_lower': 0.72, 'ci_upper': 0.85} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.89, 'ci_lower': 0.87, 'ci_upper': 0.9} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Odds Ratio (OR, top 20% vs bottom 20%)', 'name_short': 'Odds Ratio (OR, top 20% vs bottom 20%)', 'estimate': 1.578, 'ci_lower': 1.25, 'ci_upper': 1.991} | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.28, 'ci_lower': 1.22, 'ci_upper': 1.34} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.246, 'se': 0.024} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.01, 'ci_lower': 1.83, 'ci_upper': 2.22} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.7, 'se': 0.05} | N/A | N/A | Agent Input |
| validation_sample_size | n=524 | n=3,101 | n=50,429 | n=3,945 | n=245 | n=3,048 | Agent Input |
| samples_training | n=10,995 | n=3,076 | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (2%), AMR (1%), EAS (32%), EUR (53%), MAE (9%), MAO (2%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), AMR (1%), EAS (32%), EUR (53%), MAE (9%), MAO (2%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (21%), EUR (79%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (67%), MAE (33%) | GWAS: EAS (6%), EUR (94%) / EVAL: AFR (33%), EUR (33%), MAE (33%) | Agent Input |
| training_development_cohorts | CCHMC GENYO Illumina_iControlDB UAB UCLA UCSF UMN USC WASHU WFSM | CCHMC GENYO Illumina_iControlDB UAB UCLA UCSF UMN USC WASHU WFSM | N/A | N/A | N/A | N/A | Agent Input |
| publication.title | Genome-wide assessment of genetic risk for systemic lupus erythematosus and disease severity. | Genome-wide assessment of genetic risk for systemic lupus erythematosus and disease severity. | Pleiotropy of systemic lupus erythematosus risk alleles and cardiometabolic disorders: A phenome-wide association study and inverse-variance weighted meta-analysis. | Interactions Between Genome-Wide Genetic Factors and Smoking Influencing Risk of Systemic Lupus Erythematosus. | Using genetics to prioritize diagnoses for rheumatology outpatients with inflammatory arthritis. | Phenotype Risk Score but Not Genetic Risk Score Aids in Identifying Individuals With Systemic Lupus Erythematosus in the Electronic Health Record. | Agent Input |
| publication.journal | Hum Mol Genet | Hum Mol Genet | Lupus | Arthritis Rheumatol | Sci Transl Med | Arthritis Rheumatol | Agent Input |
| date_release | 2021-05-28 | 2021-05-28 | 2021-06-11 | 2024-06-12 | 2020-06-03 | 2023-10-17 | Agent Input |
| variants_number | 95 | 95 | 41 | 97 | 55 | 57 | Agent Input |
| covariates | Unknown | Unknown | PCs(1-5), median age in the electronic health record, sex | Unknown | Unknown | phenotype risk score | Agent Input |


### chronic obstructive pulmonary disease

Candidate pool: `10` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001783 | PGS004536 | PGS001788 | PGS002062 | PGS004466 | PGS001783 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 1/10 | Benchmark Only |
| AoU benchmark AUC | 0.6057 | 0.5966 | 0.5913 | 0.5764 | 0.5652 | 0.6057 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 7/10 trials | Benchmark Only |
| trait_reported | Chronic obstructive pulmonary disease | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Chronic airway obstruction | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Agent Input |
| trait_efo | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | chronic obstructive pulmonary disease | Agent Input |
| phenotyping_reported | Chronic obstructive pulmonary disease | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Chronic airway obstruction | J44 (Other chronic obstructive pulmonary disease) | Chronic obstructive pulmonary disease | Agent Input |
| method_name | PRS-CS-auto | RFDiseasemetaPRS | PRS-CS-auto | LDpred2 (bigsnpr) | LDpred2 | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | PPM009312 | PPM020651 | PPM009292 | PPM011358 | PPM020581 | PPM009312 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 8 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | 0.0381 | N/A | 0.0163 | N/A | N/A | 0.0381 | Agent Input |
| performance_metrics.full_model_auc | 0.7400 | N/A | 0.7150 | N/A | N/A | 0.7400 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.715} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.038092} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.0163} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.047, 'ci_lower': 0.0327, 'ci_upper': 0.0613} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.038092} | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.487584} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.30838779665344} | N/A | Agent Input |
| validation_sample_size | n=7,128 | n=56,192 | n=337,168 | n=18,735 | n=56,192 | n=7,128 | Agent Input |
| samples_training | N/A | n=174,489 | N/A | n=391,124 | n=174,489 | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (2%), ASN (2%), EAS (24%), EUR (72%), OTH (1%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (33%), EUR (61%), OTH (2%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (2%), ASN (2%), EAS (24%), EUR (72%), OTH (1%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI QSKIN TWB UCLA UKB deCODE | UKB | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI QSKIN TWB UCLA deCODE | UKB | UKB | BBJ BioMe BioVU CCPM CKB EB FinnGen G&H GS:SFHS HUNT LifeLines MGBB MGI QSKIN TWB UCLA UKB deCODE | Agent Input |
| publication.title | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | Cell Genom | Commun Biol | Cell Genom | Am J Hum Genet | Commun Biol | Cell Genom | Agent Input |
| date_release | 2022-09-08 | 2024-03-18 | 2022-09-08 | 2022-01-10 | 2024-03-18 | 2022-09-08 | Agent Input |
| variants_number | 884139 | 1059939 | 910082 | 811003 | 1059939 | 884139 | Agent Input |
| covariates | sex,age, 20PCs | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | sex,age, 20PCs | Agent Input |


### kidney cancer

Candidate pool: `10` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS004245 | PGS000722 | PGS003744 | PGS000787 | PGS004908 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 1/10 | Benchmark Only |
| AoU benchmark AUC | 0.5841 | 0.5524 | 0.5513 | 0.5466 | 0.5456 | 0.5841 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Renal cancer | Kidney cancer | Kidney cancer | Agent Input |
| trait_efo | renal carcinoma | renal cell carcinoma | renal carcinoma | renal carcinoma | renal cell carcinoma | renal carcinoma | Agent Input |
| phenotyping_reported | Kidney cancer | Kidney cancer | Incident kidney cancer | Renal cancer | Incident kidney cancer | Kidney cancer | Agent Input |
| method_name | Genome-wide significant SNPs | PRSice-2 | Genome-wide significant variants | Genome-wide significant SNPs | 19 variants from Graff et al (PGS000076) with inverse variant weights | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | PPM021361 | PPM020302 | PPM001652 | PPM018500 | PPM002058 | PPM021361 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 2 | 1 | 1 | 1 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7400 | N/A | 0.5670 | N/A | 0.7220 | 0.7400 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.3660 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.567, 'ci_lower': 0.543, 'ci_upper': 0.591} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.723, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.366} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.02, 'ci_upper': 1.45} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.24, 'ci_lower': 1.14, 'ci_upper': 1.35} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.15, 'ci_lower': 1.07, 'ci_upper': 1.24} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | Agent Input |
| validation_sample_size | n=324,805 | n=133,830 | n=400,812 | n=692 | n=391,610 | n=324,805 | Agent Input |
| samples_training | N/A | N/A | N/A | n=649 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | N/A | AHS ASHRAM ATBC BioVU CEERCC CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC ICR Karolinska Leeds MCCS MDACCS MDARCCS Moscow NCI NHS PHS PLCO RMHT SEARCH SORCE Tromso UKBS USKC Umea VARI VITAL WHI WHS WTCCC conFIRM deCODE | UKB | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | BBJ FinnGen NCI | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Prognostic evaluation of polygenic risk score underlying pan-cancer analysis: evidence from two large-scale cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Agent Input |
| publication.journal | Nat Genet | NPJ Precis Oncol | JNCI Cancer Spectr | EBioMedicine | Nat Commun | Nat Genet | Agent Input |
| date_release | 2024-05-22 | 2023-12-15 | 2021-02-03 | 2023-06-01 | 2021-05-28 | 2024-05-22 | Agent Input |
| variants_number | 107 | 12 | 15 | 14 | 19 | 107 | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | first 10 genetic principal components | Genotyping array | Unknown | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Age, sex, PCs, BMI, smoking, hypertension | Agent Input |


### obesity

Candidate pool: `10` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005235 | PGS005154 | PGS003959 | PGS002033 | PGS005145 | PGS001298 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 8/10 | Benchmark Only |
| AoU benchmark AUC | 0.6479 | 0.6331 | 0.5909 | 0.5833 | 0.5771 | 0.5605 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Adiposity | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | Obesity (time-to-event) | Agent Input |
| trait_efo | obesity | obesity | obesity | obesity, overweight body mass index status, overnutrition | obesity | obesity | Agent Input |
| phenotyping_reported | Obesity (phecode: 278.1) | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | TTE obesity | Agent Input |
| method_name | LDpred2-auto | CT-SLEB | Genome-wide significant SNPs | LDpred2 (bigsnpr) | PRS-CS | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM022667 | PPM022374 | PPM019107 | PPM011135 | PPM022365 | PPM008991 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | East Asian | European, Not reported | European | East Asian | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 7 | 8 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | 0.5757 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0115 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | 0.5956 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | 0.0181 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | 0.0336 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59555, 'ci_lower': 0.58697, 'ci_upper': 0.60413} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0789, 'ci_lower': 0.0651, 'ci_upper': 0.0927} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01814} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03355} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57573, 'ci_lower': 0.56713, 'ci_upper': 0.58434} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.9704649488977} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 1.76187749677908} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.149, 'se': 0.028} | N/A | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 1.60817500694587} | N/A | Agent Input |
| validation_sample_size | n=100,960 | n=58,688 | n=27,429 | n=20,000 | n=58,688 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | N/A | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (19%), EUR (81%) / EVAL: EAS (100%) | GWAS: NR (33%), EUR (67%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EAS (100%) / EVAL: EAS (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | EGG GIANT UKB | BBJ | N/A | UKB | BBJ | UKB | Agent Input |
| publication.title | Modeling the genomic architecture of adiposity and anthropometrics across the lifespan. | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | The sulfur microbial diet and increased risk of obesity: Findings from a population-based prospective cohort study. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Commun Biol | Clin Nutr | Am J Hum Genet | Commun Biol | PLoS Genet | Agent Input |
| date_release | 2025-10-06 | 2025-03-17 | 2023-10-17 | 2022-01-10 | 2025-03-17 | 2021-10-21 | Agent Input |
| variants_number | 709828 | 443124 | 940 | 846292 | 908466 | 9227 | Agent Input |
| covariates | age, sex, batch, and the first 10 genetic principal components | age, sex | Age, sex, race, centres, education, Townsend deprivation index, household income, smoking, alcohol consumption, physical activity, sleep pattern, energy intake, and BMI, WC or BF% at baseline | sex, age, birth date, deprivation index, 16 PCs | age, sex | age, sex, UKB array type, Genotype PCs | Agent Input |


### acute lymphoblastic leukemia

Candidate pool: `9` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000874 | PGS000648 | PGS000646 | PGS000647 | PGS003453 | PGS003448 | Agent Input |
| AoU benchmark rank | 1/9 | 2/9 | 3/9 | 4/9 | 5/9 | 9/9 | Benchmark Only |
| AoU benchmark AUC | 0.6073 | 0.6041 | 0.5861 | 0.5861 | 0.5818 | 0.5257 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Acute lymphoblastic leukemia | Agent Input |
| trait_efo | chronic lymphocytic leukemia | chronic lymphocytic leukemia | chronic lymphocytic leukemia | chronic lymphocytic leukemia | chronic lymphocytic leukemia | acute lymphoblastic leukemia | Agent Input |
| phenotyping_reported | Chronic lymphocytic leukemia in individuals with a family history of hematological cancers | Lymphoid leukemia, chronic | Lymphoid leukemia, chronic | Lymphoid leukemia, chronic | Chronic lymphocytic leukemia | Chronic lymphocytic leukemia | Agent Input |
| method_name | Representative SNPs from chronic lymphocytic leukemia susceptibility loci | Pruning and Thresholding (P+T) | GWAS Hits | GWAS Hits | Genome-wide significant SNPs | Genome-wide significant SNPs | Agent Input |
| performance_metrics.selected_performance_id | PPM002495 | PPM001333 | PPM001331 | PPM001332 | PPM017224 | PPM017230 | Agent Input |
| performance_metrics.selected_validation_ancestry | European, NR | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 17 | 1 | 1 | 1 | 4 | 4 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8610 | 0.6960 | 0.6960 | 0.6750 | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.1020 | 0.0973 | 0.0689 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.861, 'ci_lower': 0.82, 'ci_upper': 0.9} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696, 'ci_lower': 0.621, 'ci_upper': 0.764} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.696, 'ci_lower': 0.628, 'ci_upper': 0.765} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.675, 'ci_lower': 0.64, 'ci_upper': 0.707} | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.102} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0776} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 12.9, 'ci_lower': 4.45, 'ci_upper': 37.6} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0973} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0779} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 11.3, 'ci_lower': 3.76, 'ci_upper': 33.9} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0689} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.0795} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 4.11, 'ci_lower': 1.97, 'ci_upper': 8.6} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 3.79, 'ci_lower': 2.44, 'ci_upper': 5.87} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.124, 'ci_lower': 1.648, 'ci_upper': 2.738} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.753, 'se': 0.13} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.104, 'ci_lower': 1.628, 'ci_upper': 2.718} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.744, 'se': 0.131} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.874, 'ci_lower': 1.639, 'ci_upper': 2.144} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.628, 'se': 0.0685} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.17, 'ci_lower': 2.07, 'ci_upper': 2.28} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 0.95, 'ci_lower': 0.9, 'ci_upper': 1.0} | Agent Input |
| validation_sample_size | n=3,958 | n=756 | n=756 | n=2,758 | n=20,134 | n=20,134 | Agent Input |
| samples_training | N/A | n=730 | n=730 | n=2,833 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: NR (50%), AFR (12%), EUR (25%), MAE (12%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (5%), AMR (14%), EUR (81%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ATBC BCCA CPSII ENGELA EPIC EpiLymph HPFS Italian_GxE MAYO MCCS MSKCC NCI-SEER NHS NSW NYU-WHS PLCO SCALE UCSF UCSF2 UK-CLL UTAH Yale | MGI | MGI | UKB | N/A | N/A | Agent Input |
| publication.title | Association of polygenic risk score with the risk of chronic lymphocytic leukemia and monoclonal B-cell lymphocytosis. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Distinct germline genetic susceptibility profiles identified for common non-Hodgkin lymphoma subtypes. | Agent Input |
| publication.journal | Blood | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Leukemia | Leukemia | Agent Input |
| date_release | 2021-08-26 | 2020-12-15 | 2020-12-15 | 2020-12-15 | 2023-03-24 | 2023-03-24 | Agent Input |
| variants_number | 41 | 44 | 32 | 32 | 43 | 15 | Agent Input |
| covariates | Age, sex, study, socioeconomic status (when available) | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | age, sex, batch PCs 1-4 | Unknown | Unknown | Agent Input |


### ankylosing spondylitis

Candidate pool: `9` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001876 | PGS001267 | PGS001268 | PGS002089 | PGS003424 | PGS001268 | Agent Input |
| AoU benchmark rank | 1/9 | 2/9 | 3/9 | 4/9 | 5/9 | 3/9 | Benchmark Only |
| AoU benchmark AUC | 0.7415 | 0.7397 | 0.7362 | 0.7188 | 0.6491 | 0.7362 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Agent Input |
| trait_efo | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | Agent Input |
| phenotyping_reported | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Agent Input |
| method_name | Penalized regression (bigstatsr) | snpnet | snpnet | LDpred2 (bigsnpr) | LDpred2 | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM009896 | PPM008844 | PPM008849 | PPM011572 | PPM017077 | PPM008849 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | East Asian | European | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | 0.7265 | 0.7346 | N/A | N/A | 0.7346 | Agent Input |
| performance_metrics.r2 | N/A | 0.0988 | 0.1023 | N/A | N/A | 0.1023 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.7433 | 0.7488 | N/A | 0.7605 | 0.7488 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.1092 | 0.1150 | N/A | N/A | 0.1150 | Agent Input |
| performance_metrics.incremental_auc | N/A | 0.1299 | 0.1269 | N/A | N/A | 0.1269 | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74328, 'ci_lower': 0.70673, 'ci_upper': 0.77983} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7605} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0797, 'ci_lower': 0.0653, 'ci_upper': 0.0941} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.10925} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12994} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.09877} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.72651, 'ci_lower': 0.68965, 'ci_upper': 0.76337} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0919, 'ci_lower': 0.0775, 'ci_upper': 0.1063} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=18,262 | n=67,425 | n=67,425 | n=18,262 | n=1,298 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=269,704 | n=269,704 | n=391,124 | N/A | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | GWAS: EAS (100%) / EVAL: EAS (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | N/A | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Genome-wide association study reveals ethnicity-specific SNPs associated with ankylosing spondylitis in the Taiwanese population. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | PLoS Genet | Am J Hum Genet | J Transl Med | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2022-01-10 | 2023-02-08 | 2021-10-21 | Agent Input |
| variants_number | 85 | 10 | 10 | 22026 | 100 | 10 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### aortic stenosis

Candidate pool: `8` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005254 | PGS005255 | PGS005256 | PGS004911 | PGS004910 | PGS005252 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | 8/8 | Benchmark Only |
| AoU benchmark AUC | 0.6375 | 0.6233 | 0.6228 | 0.5181 | 0.5166 | 0.3445 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Aortic stenosis | Mean pressure gradient | Peak aortic velocity | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Aortic stenosis | Agent Input |
| trait_efo | aortic stenosis | aortic stenosis, aortic measurement | aortic stenosis, aortic measurement | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | aortic stenosis | Agent Input |
| phenotyping_reported | incident aortic stenosis | incident aortic stenosis | incident aortic stenosis | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Incident aortic stenosis cases | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | LDPred2 | Agent Input |
| performance_metrics.selected_performance_id | PPM022737 | PPM022738 | PPM022739 | PPM021367 | PPM021366 | PPM022733 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.8000 | 0.7300 | 0.8700 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0480 | 0.0310 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.87} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.031} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.5} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.64, 'ci_lower': 1.5, 'ci_upper': 1.78} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.53, 'ci_lower': 1.4, 'ci_upper': 1.66} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.53, 'ci_lower': 1.41, 'ci_upper': 1.67} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.97} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.26} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.92} | Agent Input |
| validation_sample_size | n=244,450 | n=244,450 | n=244,450 | n=343,182 | n=343,182 | n=446,895 | Agent Input |
| samples_training | n=205,483 | n=98,645 | n=96,385 | N/A | N/A | n=47,691 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | N/A | N/A | BRRD GEL HCMR RBH-CRB | BRRD GEL HCMR RBH-CRB | MGBB | Agent Input |
| publication.title | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Genomic and transcriptomic analyses of aortic stenosis enhance therapeutic target discovery and disease prediction. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2025-02-26 | 2025-02-26 | 2026-01-19 | Agent Input |
| variants_number | 1110912 | 1111632 | 1111632 | 374114 | 374190 | 1119377 | Agent Input |
| covariates | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | age, age^2, sex, PC1-10 | age, age^2, sex, PC1-10 | age, sex, genetic ancestry principal components 1-5, type 2 diabetes, hypertension, coronary artery disease, hyperlipidemia, body mass index, current smoking, renal failure. | Agent Input |


### dilated cardiomyopathy

Candidate pool: `8` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004951 | PGS004949 | PGS004947 | PGS004862 | PGS004948 | PGS004862 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | 4/8 | Benchmark Only |
| AoU benchmark AUC | 0.6480 | 0.6463 | 0.6396 | 0.6344 | 0.6225 | 0.6344 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy (MTAG) | Dilated cardiomyopathy | Dilated cardiomyopathy (MTAG) | Agent Input |
| trait_efo | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | dilated cardiomyopathy | Agent Input |
| phenotyping_reported | Clinical dilated cardiomyopathy | Non-ischemic dilated cardiomyopathy | Non-ischemic dilated cardiomyopathy | Dilated cardiomyopathy | Non-ischemic dilated cardiomyopathy | Dilated cardiomyopathy | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM021758 | PPM021756 | PPM021754 | PPM021093 | PPM021755 | PPM021093 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European, Not reported | European, Not reported | European | European, Not reported | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6700 | 0.6800 | 0.6600 | 0.7100 | 0.6400 | 0.7100 | Agent Input |
| performance_metrics.full_model_r2 | 0.1620 | 0.2160 | 0.2350 | 0.0500 | 0.1860 | 0.0500 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.124} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.076} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.162} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.101} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.67, 'ci_lower': 0.65, 'ci_upper': 0.69} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.2023} | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.06} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.029} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.216} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.095} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.68, 'ci_lower': 0.66, 'ci_upper': 0.69} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.0052} | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.068} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.028} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.235} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.076} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.66, 'ci_lower': 0.63, 'ci_upper': 0.68} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.0109} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05} | {'name_long': 'Nagelkerke pseudo-R^2 full model', 'name_short': 'Nagelkerke pseudo-R^2 full model', 'estimate': 0.049} {'name_long': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'name_short': 'Nagelkerke pseudo-R^2 delta PRS/residual', 'estimate': 0.018} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) full model', 'estimate': 0.186} {'name_long': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'name_short': 'Liability-scale R^2 (assuming 0.4% prev) delta PRS/residual', 'estimate': 0.06} {'name_long': 'Univariate (PRS only) AUC', 'name_short': 'Univariate (PRS only) AUC', 'estimate': 0.64, 'ci_lower': 0.62, 'ci_upper': 0.66} {'name_long': 'Univariate (PRS only) AUPRC', 'name_short': 'Univariate (PRS only) AUPRC', 'estimate': 0.0042} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.93} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.66, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.91} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.65, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.73} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.55, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.64} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.49, 'se': 0.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76} | Agent Input |
| validation_sample_size | n=7,761 | n=326,106 | n=96,016 | n=347,585 | n=326,106 | n=347,585 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (46%), MAE (54%) / EVAL: EUR (100%) | GWAS: EUR (91%), MAE (9%) / EVAL: MAE (100%) | GWAS: EUR (48%), MAE (52%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (91%), MAE (9%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | FinnGen MGBB UKB | AUMC_DCM FinnGen MGBB | AUMC_DCM FinnGen UKB | HERMES | AUMC_DCM FinnGen MGBB | HERMES | Agent Input |
| publication.title | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association analysis provides insights into the molecular etiology of dilated cardiomyopathy. | Genome-wide association study reveals mechanisms underlying dilated cardiomyopathy and myocardial resilience. | Genome-wide association analysis provides insights into the molecular etiology of dilated cardiomyopathy. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2024-12-16 | 2024-12-16 | 2024-12-16 | 2024-04-18 | 2024-12-16 | 2024-04-18 | Agent Input |
| variants_number | 1075760 | 1038394 | 1072247 | 709534 | 1068761 | 709534 | Agent Input |
| covariates | Sex, PC1-12 | Age, age^2, sex, array, PC1-12 | Age, age^2, sex, PC1-12 | age, age^2, sex, PC1-10 | Age, age^2, sex, array, PC1-12 | age, age^2, sex, PC1-10 | Agent Input |


### hyperthyroidism

Candidate pool: `7` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005266 | PGS005265 | PGS005264 | PGS001042 | PGS002023 | PGS001043 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 7/7 | Benchmark Only |
| AoU benchmark AUC | 0.6211 | 0.6176 | 0.5914 | 0.5743 | 0.5665 | 0.5628 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Graves' disease | Graves' disease | Graves' disease | Thyrotoxicosis [hyperthyroidism] (time-to-event) | Thyrotoxicosis with or without goiter | Hyperthyroidism, thyrotoxicosis | Agent Input |
| trait_efo | Graves disease | Graves disease | Graves disease | Thyrotoxicosis | Thyrotoxicosis | hyperthyroidism, Thyrotoxicosis | Agent Input |
| phenotyping_reported | graves' disease | graves' disease | graves' disease | TTE thyrotoxicosis [hyperthyroidism] | Thyrotoxicosis with or without goiter | Hyperthyroidism/thyrotoxicosis | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | snpnet | LDpred2 (bigsnpr) | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM022749 | PPM022748 | PPM022747 | PPM007972 | PPM011058 | PPM007977 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 5 | 8 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | 0.6339 | N/A | 0.6323 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0236 | N/A | 0.0216 | Agent Input |
| performance_metrics.full_model_auc | 0.6637 | 0.6652 | 0.6587 | 0.7130 | N/A | 0.7137 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0591 | N/A | 0.0566 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | 0.0467 | N/A | 0.0464 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.663730746326419} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.665220447565802} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6587} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71296, 'ci_lower': 0.69708, 'ci_upper': 0.72884} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71366, 'ci_lower': 0.6965, 'ci_upper': 0.73082} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05914} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04673} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02359} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.63392, 'ci_lower': 0.61562, 'ci_upper': 0.65223} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0199, 'ci_lower': 0.0057, 'ci_upper': 0.034} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0566} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04641} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02158} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.6323, 'ci_lower': 0.61251, 'ci_upper': 0.6521} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.54332658848452} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.433940209108075} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.62508137678846} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.485557892551506} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.008} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.008} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=67,425 | n=19,108 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | n=269,704 | n=391,124 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | PLoS Genet | Am J Hum Genet | PLoS Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2021-10-21 | 2022-01-10 | 2021-10-21 | Agent Input |
| variants_number | 1085170 | 1085173 | 112 | 226 | 279385 | 69 | Agent Input |
| covariates | Unknown | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### knee osteoarthritis

Candidate pool: `7` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004883 | PGS002767 | PGS004549 | PGS004479 | PGS001192 | PGS001192 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 5/7 | Benchmark Only |
| AoU benchmark AUC | 0.5546 | 0.5528 | 0.5461 | 0.5413 | 0.5246 | 0.5246 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | Benchmark Only |
| trait_reported | Knee osteoarthritis | Knee osteoarthritis | M17 (Gonarthrosis [arthrosis of knee]) | M17 (Gonarthrosis [arthrosis of knee]) | Gonarthrosis [arthrosis of knee] (time-to-event) | Gonarthrosis [arthrosis of knee] (time-to-event) | Agent Input |
| trait_efo | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | osteoarthritis, knee | Agent Input |
| phenotyping_reported | Incident knee osteoarthritis | Knee osteoarthritis | M17 (Gonarthrosis [arthrosis of knee]) | M17 (Gonarthrosis [arthrosis of knee]) | TTE gonarthrosis [arthrosis of knee] | TTE gonarthrosis [arthrosis of knee] | Agent Input |
| method_name | megaprs.auto | PRS-CS | RFDiseasemetaPRS | LDpred2 | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM021240 | PPM014967 | PPM020664 | PPM020594 | PPM008613 | PPM008613 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 7 | 1 | 1 | 1 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | 0.5565 | 0.5565 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0068 | 0.0068 | Agent Input |
| performance_metrics.full_model_auc | 0.6000 | N/A | N/A | N/A | 0.6450 | 0.6450 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0431 | 0.0431 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | 0.0104 | 0.0104 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.6, 'ci_lower': 0.58, 'ci_upper': 0.61} | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64504, 'ci_lower': 0.63733, 'ci_upper': 0.65274} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.64504, 'ci_lower': 0.63733, 'ci_upper': 0.65274} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04312} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.0104} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0068} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55655, 'ci_lower': 0.54824, 'ci_upper': 0.56485} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04312} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.0104} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0068} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55655, 'ci_lower': 0.54824, 'ci_upper': 0.56485} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.37, 'ci_lower': 1.3, 'ci_upper': 1.44} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.35, 'ci_lower': 1.3, 'ci_upper': 1.4} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.366693} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.32326102443575} | N/A | N/A | Agent Input |
| validation_sample_size | n=29,427 | n=39,444 | n=56,192 | n=56,192 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=404 | N/A | n=174,489 | n=174,489 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | 1000G | N/A | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | A unified framework for estimating country-specific cumulative incidence for 18 diseases stratified by polygenic risk. | Systematic comparison of family history and polygenic risk across 24 common diseases. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | Commun Biol | Commun Biol | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2024-06-27 | 2022-11-07 | 2024-03-18 | 2024-03-18 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 952133 | 1052275 | 1059939 | 1059939 | 4525 | 4525 | Agent Input |
| covariates | PCs 1-10 | age, sex, 10 PCs, technical covariates | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### nodular goiter

Candidate pool: `7` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005263 | PGS005262 | PGS005261 | PGS002022 | PGS001814 | PGS001814 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 5/7 | Benchmark Only |
| AoU benchmark AUC | 0.7033 | 0.6911 | 0.6158 | 0.5575 | 0.5493 | 0.5493 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 7/10 trials | Benchmark Only |
| trait_reported | Benign nodular goiter | Benign nodular goiter | Benign nodular goiter | Nontoxic multinodular goiter | Nontoxic multinodular goiter | Nontoxic multinodular goiter | Agent Input |
| trait_efo | benign, nodular goiter | benign, nodular goiter | benign, nodular goiter | multinodular goiter, nontoxic goiter | multinodular goiter, nontoxic goiter | multinodular goiter, nontoxic goiter | Agent Input |
| phenotyping_reported | benign nodular gioter | benign nodular gioter | benign nodular gioter | Nontoxic multinodular goiter | Nontoxic multinodular goiter | Nontoxic multinodular goiter | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | Penalized regression (bigstatsr) | Agent Input |
| performance_metrics.selected_performance_id | PPM022746 | PPM022745 | PPM022744 | PPM011050 | PPM009412 | PPM009412 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 8 | 8 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5876 | 0.5933 | 0.5854 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.587559211464932} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.593306633581433} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.585439091716637} | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.024, 'ci_lower': 0.0098, 'ci_upper': 0.0382} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0277, 'ci_lower': 0.0135, 'ci_upper': 0.0419} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0277, 'ci_lower': 0.0135, 'ci_upper': 0.0419} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.36199799551033} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.308952736001074} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.40838651920181} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.342444736541657} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.048} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.047} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=19,043 | n=19,043 | n=19,043 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=391,124 | n=391,124 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2022-01-10 | 2022-01-10 | 2022-01-10 | Agent Input |
| variants_number | 1085170 | 1085173 | 110 | 375470 | 322 | 322 | Agent Input |
| covariates | Unknown | Unknown | Unknown | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Agent Input |


### pulmonary embolism

Candidate pool: `7` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001278 | PGS001280 | PGS001277 | PGS001279 | PGS004530 | PGS001280 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 2/7 | Benchmark Only |
| AoU benchmark AUC | 0.5943 | 0.5916 | 0.5907 | 0.5885 | 0.5578 | 0.5916 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | previously: Blood clot in the leg (DVT) or lung | PE (time-to-event) | PE +/- DVT | previously: Blood clot in the lung | I26 (Pulmonary embolism) | PE (time-to-event) | Agent Input |
| trait_efo | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism, deep vein thrombosis | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism | Agent Input |
| phenotyping_reported | Blood clot in the leg (DVT) or lung | TTE PE | PE +/- DVT | Blood clot in the lung | I26 (Pulmonary embolism) | TTE PE | Agent Input |
| method_name | snpnet | snpnet | snpnet | snpnet | RFDiseasemetaPRS | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM008890 | PPM008900 | PPM008885 | PPM008897 | PPM020645 | PPM008900 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 1 | 5 | Agent Input |
| performance_metrics.auc | 0.5916 | 0.6077 | 0.6114 | 0.6003 | N/A | 0.6077 | Agent Input |
| performance_metrics.r2 | 0.0133 | 0.0140 | 0.0151 | 0.0115 | N/A | 0.0140 | Agent Input |
| performance_metrics.full_model_auc | 0.6535 | 0.6762 | 0.6750 | 0.6242 | N/A | 0.6762 | Agent Input |
| performance_metrics.full_model_r2 | 0.0337 | 0.0406 | 0.0400 | 0.0176 | N/A | 0.0406 | Agent Input |
| performance_metrics.incremental_auc | 0.0350 | 0.0293 | 0.0315 | 0.0446 | N/A | 0.0293 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65354, 'ci_lower': 0.63231, 'ci_upper': 0.67477} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67617, 'ci_lower': 0.64866, 'ci_upper': 0.70368} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67497, 'ci_lower': 0.64702, 'ci_upper': 0.70293} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62416, 'ci_lower': 0.60164, 'ci_upper': 0.64668} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67617, 'ci_lower': 0.64866, 'ci_upper': 0.70368} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03366} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03495} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01331} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.59164, 'ci_lower': 0.56886, 'ci_upper': 0.61442} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04057} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02926} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01403} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60765, 'ci_lower': 0.57812, 'ci_upper': 0.63719} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03998} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03149} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01508} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61144, 'ci_lower': 0.58149, 'ci_upper': 0.6414} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01763} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04457} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60034, 'ci_lower': 0.57683, 'ci_upper': 0.62385} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04057} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02926} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01403} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60765, 'ci_lower': 0.57812, 'ci_upper': 0.63719} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.242446} | N/A | Agent Input |
| validation_sample_size | n=24,838 | n=24,905 | n=24,905 | n=67,349 | n=56,192 | n=24,905 | Agent Input |
| samples_training | n=269,382 | n=269,704 | n=269,704 | n=269,382 | n=174,489 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Commun Biol | PLoS Genet | Agent Input |
| date_release | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2024-03-18 | 2021-10-21 | Agent Input |
| variants_number | 551 | 88 | 96 | 94 | 1059939 | 88 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### abdominal aortic aneurysm

Candidate pool: `6` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003973 | PGS003429 | PGS003972 | PGS001784 | PGS000753 | PGS001784 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 4/6 | Benchmark Only |
| AoU benchmark AUC | 0.6374 | 0.6341 | 0.6312 | 0.5618 | 0.5388 | 0.5618 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | Benchmark Only |
| trait_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| trait_efo | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Agent Input |
| phenotyping_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Prevalent abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| method_name | PRS-CS | shaPRS + LDpred2 | PRS-CS | PRS-CS-auto | Pruning and Thresholding (P+T) | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | PPM019137 | PPM017103 | PPM019134 | PPM009288 | PPM001912 | PPM009288 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 3 | 1 | 7 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0147 | N/A | 0.0147 | Agent Input |
| performance_metrics.full_model_auc | 0.8820 | 0.7080 | 0.6900 | 0.8680 | N/A | 0.8680 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0055 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.882, 'ci_lower': 0.872, 'ci_upper': 0.892} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.708, 'ci_lower': 0.691, 'ci_upper': 0.725} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.868} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.868} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00547} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.014661} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.014661} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37, 'ci_lower': 1.3, 'ci_upper': 1.44} | N/A | Agent Input |
| validation_sample_size | n=7,517 | n=91,731 | n=6,940 | n=350,767 | n=46,564 | n=350,767 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=8,772 | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: EUR (89%), MAE (11%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (60%), EAS (17%), EUR (82%), OTH (90%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (25%), EUR (75%) | GWAS: AFR (60%), EAS (17%), EUR (82%), OTH (90%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | UKB | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS UKAGS UKB VIVA deCODE eMERGE | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI deCODE | MAYO-VDB MVP | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI deCODE | Agent Input |
| publication.title | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Evaluating the cost-effectiveness of polygenic risk score-stratified screening for abdominal aortic aneurysm. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Genetic Architecture of Abdominal Aortic Aneurysm in the Million Veteran Program. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | Nat Genet | Nat Commun | Nat Genet | Cell Genom | Circulation | Cell Genom | Agent Input |
| date_release | 2023-11-01 | 2023-12-15 | 2023-11-01 | 2022-09-08 | 2021-04-07 | 2022-09-08 | Agent Input |
| variants_number | 1118997 | 831447 | 1118997 | 911440 | 29 | 911440 | Agent Input |
| covariates | Age, Age^2, Sex | Unknown | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | Age, sex, PCs (1-5) | sex,age,age2,age*sex,age^2*sex, 20PCs | Agent Input |


### age-related macular degeneration

Candidate pool: `6` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004606 | PGS002269 | PGS004952 | PGS001834 | PGS002041 | PGS004606 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 1/6 | Benchmark Only |
| AoU benchmark AUC | 0.6547 | 0.6530 | 0.6512 | 0.6133 | 0.6093 | 0.6547 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | Age-related macular degeneration | Agent Input |
| trait_efo | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | Agent Input |
| phenotyping_reported | Age-related macular degeneration | Rentinal layer thickness (photoreceptor inner and outer segments) | Late age-related macular degeneration (Clinical Classification) | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | Age-related macular degeneration | Agent Input |
| method_name | PRS-CS | Independent variants associated with AMD | Genome-wide significant SNPs | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM020767 | PPM012920 | PPM021761 | PPM009564 | PPM011194 | PPM020767 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European, South Asian, Not reported | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 3 | 6 | 8 | 8 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7100 | N/A | 0.8420 | N/A | N/A | 0.7100 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 84.2} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0175, 'ci_lower': 0.0034, 'ci_upper': 0.0315} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0159, 'ci_lower': 0.0018, 'ci_upper': 0.0299} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': -0.21, 'ci_lower': -0.23, 'ci_upper': -0.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.41, 'ci_lower': 1.32, 'ci_upper': 1.5} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | Agent Input |
| validation_sample_size | n=163,011 | n=44,823 | n=1,232 | n=19,413 | n=19,413 | n=163,011 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=391,124 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | IAMDGC | AREDS BDES CWRU Columbia EUGENDA Edinburgh JHU MMAP Marshfield NHS RotES UCSD UWALF Vanderbilt | IAMDGC | UKB | UKB | IAMDGC | Agent Input |
| publication.title | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Photoreceptor Layer Thinning Is an Early Biomarker for Age-Related Macular Degeneration: Epidemiologic and Genetic Evidence from UK Biobank OCT Data. | Genetic Risk Score Analysis Supports a Joint View of Two Classification Systems for Age-Related Macular Degeneration. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Agent Input |
| publication.journal | Nat Genet | Ophthalmology | Invest Ophthalmol Vis Sci | Am J Hum Genet | Am J Hum Genet | Nat Genet | Agent Input |
| date_release | 2024-02-20 | 2022-04-01 | 2024-09-19 | 2022-01-10 | 2022-01-10 | 2024-02-20 | Agent Input |
| variants_number | 1000946 | 47 | 52 | 157 | 116538 | 1000946 | Agent Input |
| covariates | age, sex, principal components 1-10 | Age, age2 (to adjust for non-linear relationships with age), sex, smoking status, and the first ten principal components of genetic ancestry | Age, sex, survey membership, 10 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, principal components 1-10 | Agent Input |


### cervical carcinoma

Candidate pool: `6` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000073 | PGS000784 | PGS005165 | PGS003389 | PGS003428 | PGS001299 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 6/6 | Benchmark Only |
| AoU benchmark AUC | 0.6951 | 0.6706 | 0.4765 | 0.4762 | 0.3795 | 0.3377 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | Benchmark Only |
| trait_reported | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Agent Input |
| trait_efo | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | Agent Input |
| phenotyping_reported | Incident cervical cancer | Incident cervical cancer | Cervical Cancer | cervical cancer | Incident cervical cancer | Cervical cancer | Agent Input |
| method_name | Genome-wide significant variants | 10 variants from Graff et al (PGS000073) with inverse variant weights | Known susceptibility loci (genome-wide significant SNPs) | lassosum | LDpred | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM002039 | PPM002055 | PPM022403 | PPM016264 | PPM017102 | PPM008994 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | East Asian | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 1 | 1 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | 0.5522 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | 0.0026 | Agent Input |
| performance_metrics.full_model_auc | 0.7450 | 0.7450 | 0.5660 | 0.5630 | 0.6130 | 0.7676 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.4370 | N/A | 0.0016 | N/A | 0.1128 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | 0.0068 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75, 'se': 0.017} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.017} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.566} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.563} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.613} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.76761, 'ci_lower': 0.74661, 'ci_upper': 0.7886} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.437} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00158} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11284} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00676} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00263} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55215, 'ci_lower': 0.51478, 'ci_upper': 0.58952} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.09, 'ci_upper': 1.37} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.21, 'ci_lower': 1.07, 'ci_upper': 1.35} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.2, 'ci_lower': 1.06, 'ci_upper': 1.36} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.182} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.33, 'se': 0.069} | N/A | Agent Input |
| validation_sample_size | n=211,795 | n=211,795 | n=57,359 | n=144,374 | n=128,113 | n=24,905 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=4,295 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (100%) / EVAL: EAS (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | TwinGene | NCI Seattle TwinGene Umea WTCCC | BBJ | N/A | EB FinnGen KP UKB | UKB | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Polygenic risk scores for pan-cancer risk prediction in the Chinese population: A population-based cohort study based on the China Kadoorie Biobank. | Common germline risk variants impact somatic alterations and clinical features across cancers. | GWAS meta-analyses clarify genetics of cervical phenotypes and inform risk stratification for cervical cancer. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | PLoS Med | Cancer Res | Hum Mol Genet | PLoS Genet | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2025-03-17 | 2023-01-19 | 2023-04-28 | 2021-10-21 | Agent Input |
| variants_number | 10 | 10 | 15 | 2814 | 2894555 | 24 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Age,Sex (if applicable),Region,Top 10 genetic ancestry principal components | age, top 20 genetic principal components | age, smoking | age, sex, UKB array type, Genotype PCs | Agent Input |


### late-onset alzheimer's disease

Candidate pool: `5` models. Eligible `Hit@k`: `1,2,3,4,5`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000054 | PGS002289 | PGS000334 | PGS004918 | PGS000053 | PGS000334 | Agent Input |
| AoU benchmark rank | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | 3/5 | Benchmark Only |
| AoU benchmark AUC | 0.5690 | 0.5203 | 0.5144 | 0.5114 | 0.4346 | 0.5144 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 5/10 trials | Benchmark Only |
| trait_reported | Alzheimer's disease (late onset) | Late-onset Alzheimer's disease | Late-onset Alzheimer’s disease | Late-onset Alzheimers disease (based on SNPs in genes involved in synaptic function) | Alzheimer's disease (late onset) | Late-onset Alzheimer’s disease | Agent Input |
| trait_efo | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | late-onset Alzheimer's disease | Agent Input |
| phenotyping_reported | Familial late-onset Alzheimer's disease (LOAD) | Pairs matching (short-term memory and attention) no. of correct online round 1 x age interaction | Late-onset Alzheimer’s disease | Late-onset Alzheimer's disease | Familial late-onset Alzheimer's disease (LOAD) | Late-onset Alzheimer’s disease | Agent Input |
| method_name | Genome-wide significant variants | GWAS-significant variants (including APOE) | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Genome-wide significant variants | Clumping and Thresholding (C+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM000135 | PPM012988 | PPM000901 | PPM021384 | PPM000133 | PPM000901 | Agent Input |
| performance_metrics.selected_validation_ancestry | Hispanic or Latin American | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 3 | 13 | 2 | 1 | 3 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.7310 | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.1910 | N/A | N/A | 0.1910 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.731} | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Difference in mean cognition per decacde increase in age per 1-SD higher GRS (%)', 'name_short': 'Difference in mean cognition per decacde increase in age per 1-SD higher GRS (%)', 'estimate': 11.5} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.191, 'ci_lower': 0.131, 'ci_upper': 0.269} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.191, 'ci_lower': 0.131, 'ci_upper': 0.269} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.73, 'ci_lower': 1.57, 'ci_upper': 1.93} | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.29, 'ci_lower': 1.21, 'ci_upper': 1.37} | N/A | Agent Input |
| validation_sample_size | n=3,324 | n=497,087 | n=3,810 | n=136 | n=4,792 | n=3,810 | Agent Input |
| samples_training | N/A | N/A | N/A | n=439 | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: AMR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (19%), EUR (81%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (19%), EUR (81%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | IGAP UKB | ADGC BfDR CHARGE EADI GERAD | ACT ADC ADNI AGES CHS EADI FHS GERAD GSK LOAD MAYO MIRAGE OHSU ROSMAP RS TGEN UMVUMSS UPITT WASHU | IGAP UKB | Agent Input |
| publication.title | Polygenic risk scores in familial Alzheimer disease. | Association of Genetic Variants Linked to Late-Onset Alzheimer Disease With Cognitive Test Performance by Midlife. | Risk prediction of late-onset Alzheimer's disease implies an oligogenic architecture. | Genetic variants in glutamate-, Aβ-, and tau-related pathways determine polygenic risk for Alzheimer's disease. | Polygenic risk scores in familial Alzheimer disease. | Risk prediction of late-onset Alzheimer's disease implies an oligogenic architecture. | Agent Input |
| publication.journal | Neurology | JAMA Netw Open | Nat Commun | Neurobiol Aging | Neurology | Nat Commun | Agent Input |
| date_release | 2019-12-18 | 2022-05-18 | 2020-10-16 | 2024-06-12 | 2019-12-18 | 2020-10-16 | Agent Input |
| variants_number | 21 | 23 | 22 | 8 | 21 | 22 | Agent Input |
| covariates | Age, sex | Unknown | Unknown | Unknown | Age, sex | Unknown | Agent Input |


### alcohol dependence

Candidate pool: `4` models. Eligible `Hit@k`: `1,2,3,4`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002738 | PGS000201 | PGS000202 | PGS002739 | PGS002738 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 1/4 | Benchmark Only |
| AoU benchmark AUC | 0.6051 | 0.5762 | 0.5742 | 0.5224 | 0.6051 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | Benchmark Only |
| trait_reported | Alcohol use disorder | Problematic alcohol use | Problematic alcohol use | Alcohol use disorder | Alcohol use disorder | Agent Input |
| trait_efo | alcohol dependence | alcohol dependence measurement | alcohol dependence measurement | alcohol dependence | alcohol dependence | Agent Input |
| phenotyping_reported | Alcohol use disorder | Alcohol use disorder (DSM-5 criteria count, log-transformed) | Alcohol use disorder (DSM-5 criteria count, log-transformed) | Alcohol use disorder | Alcohol use disorder | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CSx (gene-based) | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM014841 | PPM000626 | PPM000629 | PPM014842 | PPM014841 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | African American or Afro-Caribbean | European | Agent Input |
| performance_metrics.record_count | 4 | 1 | 1 | 1 | 4 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.96, 'ci_lower': 1.54, 'ci_upper': 2.51} | {'name_long': 'ΔR-squared (vs. covariates alone)', 'name_short': 'ΔR-squared (vs. covariates alone)', 'estimate': 0.01192} | {'name_long': 'ΔR-squared (vs. covariates alone)', 'name_short': 'ΔR-squared (vs. covariates alone)', 'estimate': 0.00456} | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.76, 'ci_lower': 1.32, 'ci_upper': 2.34} | {'name_long': 'Odds Ratio (OR top 10% vs rest)', 'name_short': 'Odds Ratio (OR top 10% vs rest)', 'estimate': 1.96, 'ci_lower': 1.54, 'ci_upper': 2.51} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 3.17, 'se': 1.87} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.099, 'se': 0.01} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.043, 'se': 0.019} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.17, 'se': 0.03} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 3.17, 'se': 1.87} | Agent Input |
| validation_sample_size | n=7,900 | n=7,599 | n=1,251 | n=6,315 | n=7,900 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (12%), EUR (88%) / EVAL: AFR (100%) | GWAS: AFR (14%), AMR (4%), EAS (30%), EUR (82%), SAS (5%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | MVP UKB | UKB | UKB | MVP PGC UKB | MVP UKB | Agent Input |
| publication.title | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | Using polygenic scores for identifying individuals at increased risk of substance use disorders in clinical and population samples. | Using polygenic scores for identifying individuals at increased risk of substance use disorders in clinical and population samples. | Gene-based polygenic risk scores analysis of alcohol use disorder in African Americans. | Evaluating risk for alcohol use disorder: Polygenic risk scores and family history. | Agent Input |
| publication.journal | Alcohol Clin Exp Res | Transl Psychiatry | Transl Psychiatry | Transl Psychiatry | Alcohol Clin Exp Res | Agent Input |
| date_release | 2022-08-03 | 2020-07-01 | 2020-07-01 | 2022-08-03 | 2022-08-03 | Agent Input |
| variants_number | 326000 | 1094954 | 1083002 | 858 | 326000 | Agent Input |
| covariates | Unknown | sex, age of last observation, 10 Genetic PCs, genotyping array, data collection site | sex, age of last observation, 10 Genetic PCs | Unknown | Unknown | Agent Input |


### atrial flutter

Candidate pool: `4` models. Eligible `Hit@k`: `1,2,3,4`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002050 | PGS001841 | PGS001339 | PGS001263 | PGS001263 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 4/4 | Benchmark Only |
| AoU benchmark AUC | 0.5909 | 0.5856 | 0.5788 | 0.5785 | 0.5785 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | Benchmark Only |
| trait_reported | Atrial fibrillation and flutter | Atrial fibrillation and flutter | Atrial fibrillation and flutter (time-to-event) | Atrial flutter | Atrial flutter | Agent Input |
| trait_efo | atrial fibrillation, atrial flutter | atrial fibrillation, atrial flutter | atrial fibrillation, atrial flutter | atrial flutter | atrial flutter | Agent Input |
| phenotyping_reported | Atrial fibrillation and flutter | Atrial fibrillation and flutter | TTE atrial fibrillation and flutter | Atrial flutter | Atrial flutter | Agent Input |
| method_name | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM011262 | PPM009618 | PPM009183 | PPM008822 | PPM008822 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 8 | 8 | 6 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6130 | 0.6172 | 0.6172 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0245 | 0.0252 | 0.0252 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.7766 | 0.7818 | 0.7818 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.1402 | 0.1422 | 0.1422 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0219 | 0.0217 | 0.0217 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.77656, 'ci_lower': 0.76352, 'ci_upper': 0.7896} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78179, 'ci_lower': 0.76842, 'ci_upper': 0.79516} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.78179, 'ci_lower': 0.76842, 'ci_upper': 0.79516} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.1034, 'ci_lower': 0.0894, 'ci_upper': 0.1174} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.1026, 'ci_lower': 0.0885, 'ci_upper': 0.1165} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.14023} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02188} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02447} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.613, 'ci_lower': 0.59591, 'ci_upper': 0.6301} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1422} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02171} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02517} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61716, 'ci_lower': 0.59934, 'ci_upper': 0.63498} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.1422} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02171} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02517} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61716, 'ci_lower': 0.59934, 'ci_upper': 0.63498} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,230 | n=19,230 | n=24,905 | n=24,905 | n=24,905 | Agent Input |
| samples_training | n=391,124 | n=391,124 | n=269,704 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (17%), EAS (17%), EUR (33%), MAO (17%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 554908 | 3980 | 2142 | 2087 | 2087 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### hypertrophic cardiomyopathy

Candidate pool: `4` models. Eligible `Hit@k`: `1,2,3,4`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004911 | PGS000739 | PGS004910 | PGS000778 | PGS004911 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 1/4 | Benchmark Only |
| AoU benchmark AUC | 0.6036 | 0.5891 | 0.5873 | 0.5514 | 0.6036 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | Benchmark Only |
| trait_reported | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy (MTAG) | Agent Input |
| trait_efo | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | Agent Input |
| phenotyping_reported | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | Clinical events in individuals with a pathogenic or likely pathogenic sarcomeric variant | Hypertrophic cardiomyopathy | Agent Input |
| method_name | PRS-CS | Genome-wide significant variants | PRS-CS | Genome-wide significant variants | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM021367 | PPM018531 | PPM021366 | PPM002016 | PPM021367 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | Not reported | European | Agent Input |
| performance_metrics.record_count | 1 | 8 | 1 | 6 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8000 | 0.8210 | 0.7300 | N/A | 0.8000 | Agent Input |
| performance_metrics.full_model_r2 | 0.0480 | N/A | 0.0310 | N/A | 0.0480 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.821, 'ci_lower': 0.772, 'ci_upper': 0.871} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.031} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.5} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.97} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.26} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.28, 'ci_lower': 1.06, 'ci_upper': 1.54} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.247, 'se': 0.095} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | Agent Input |
| validation_sample_size | n=343,182 | n=184,511 | n=343,182 | n=368 | n=343,182 | Agent Input |
| samples_training | N/A | n=47,737 | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (3%), EAS (80%), EUR (90%), OTH (60%), SAS (4%) / DEV: MAE (100%) / EVAL: EUR (40%), MAE (60%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / EVAL: NR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BRRD GEL HCMR RBH-CRB | BRRD HCMR UKB | BRRD GEL HCMR RBH-CRB | ERSPC LHSC MHI NL4 RBH-CRB UKDHP UMCG | BRRD GEL HCMR RBH-CRB | Agent Input |
| publication.title | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Common genetic variants and modifiable risk factors underpin hypertrophic cardiomyopathy susceptibility and expressivity. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Shared genetic pathways contribute to risk of hypertrophic and dilated cardiomyopathies with opposite directions of effect. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2025-02-26 | 2021-02-23 | 2025-02-26 | 2021-05-28 | 2025-02-26 | Agent Input |
| variants_number | 374114 | 27 | 374190 | 20 | 374114 | Agent Input |
| covariates | age, age^2, sex, PC1-10 | Clinical risk factors (obesity, HTN, AF, CAD), HCM-ACMG rare variant carrier status, age, sex, genotyping array, and PCs 1-5 | age, age^2, sex, PC1-10 | Genetic relatedness matrix, sex | age, age^2, sex, PC1-10 | Agent Input |


### juvenile idiopathic arthritis

Candidate pool: `4` models. Eligible `Hit@k`: `1,2,3,4`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000114 | PGS000325 | PGS000326 | PGS000324 | PGS000114 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 1/4 | Benchmark Only |
| AoU benchmark AUC | 0.5768 | 0.5517 | 0.5315 | 0.5230 | 0.5768 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | Benchmark Only |
| trait_reported | Juvenile Idiopathic Arthritis | Oligoarthritis Juvenile Idiophatic Arthritis | Rheumatoid-factor-negative Polyarthritis (Juvenile Idiophatic Arthritis) | Enthesitis-related Juvenile Idiophatic Arthritis | Juvenile Idiopathic Arthritis | Agent Input |
| trait_efo | juvenile idiopathic arthritis | oligoarticular juvenile idiopathic arthritis | polyarticular juvenile idiopathic arthritis, rheumatoid factor negative | enthesitis-related juvenile idiopathic arthritis | juvenile idiopathic arthritis | Agent Input |
| phenotyping_reported | Juvenile Idiopathic Arthritis | Oligoarthritis Juvenile Idiophatic Arthritis | Rheumatoid-factor-negative Polyarthritis | Enthesitis-related Arthritis | Juvenile Idiopathic Arthritis | Agent Input |
| method_name | SparSNP | SparSNP | SparSNP | SparSNP | SparSNP | Agent Input |
| performance_metrics.selected_performance_id | PPM000263 | PPM000875 | PPM000877 | PPM000874 | PPM000263 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 4 | 4 | 4 | 4 | 4 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7380 | 0.8000 | 0.7600 | 0.9300 | 0.7380 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.705, 'ci_upper': 0.77} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8, 'ci_lower': 0.77, 'ci_upper': 0.84} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.76, 'ci_lower': 0.72, 'ci_upper': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.93, 'ci_lower': 0.86, 'ci_upper': 0.99} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.738, 'ci_lower': 0.705, 'ci_upper': 0.77} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.085, 'ci_lower': 1.773, 'ci_upper': 2.471} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.93, 'ci_lower': 1.75, 'ci_upper': 2.13} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.51, 'ci_lower': 1.35, 'ci_upper': 1.68} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 3.09, 'ci_lower': 2.07, 'ci_upper': 5.04} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.085, 'ci_lower': 1.773, 'ci_upper': 2.471} | Agent Input |
| validation_sample_size | n=940 | n=3,157 | n=3,089 | n=594 | n=940 | Agent Input |
| samples_training | n=7,505 | n=6,137 | n=5,733 | n=5,354 | n=7,505 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | B58C UKBS WTCCC | Agent Input |
| publication.title | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Genomic risk scores for juvenile idiopathic arthritis and its subtypes. | Agent Input |
| publication.journal | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Ann Rheum Dis | Agent Input |
| date_release | 2020-02-27 | 2020-09-18 | 2020-09-18 | 2020-09-18 | 2020-02-27 | Agent Input |
| variants_number | 26 | 21 | 12 | 138 | 26 | Agent Input |
| covariates | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | sex, genetic PCs 1-10 | Agent Input |


### peripheral vascular disease

Candidate pool: `4` models. Eligible `Hit@k`: `1,2,3,4`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005217 | PGS002055 | PGS005158 | PGS001843 | PGS005217 | Agent Input |
| AoU benchmark rank | 1/4 | 2/4 | 3/4 | 4/4 | 1/4 | Benchmark Only |
| AoU benchmark AUC | 0.5862 | 0.5195 | 0.5176 | 0.5123 | 0.5862 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | Benchmark Only |
| trait_reported | Peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease | Agent Input |
| trait_efo | peripheral arterial disease | peripheral vascular disease | peripheral arterial disease | peripheral vascular disease | peripheral arterial disease | Agent Input |
| phenotyping_reported | Incident peripheral artery disease | Peripheral vascular disease, unspecified | Peripheral artery disease in type 2 diabetes | Peripheral vascular disease, unspecified | Incident peripheral artery disease | Agent Input |
| method_name | LDpred2 | LDpred2 (bigsnpr) | Genome-wide significant SNPs | Penalized regression (bigstatsr) | LDpred2 | Agent Input |
| performance_metrics.selected_performance_id | PPM022612 | PPM011302 | PPM022378 | PPM009634 | PPM022612 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, East Asian, European, Greater Middle Eastern (Middle Eastern, North African or Persian), South Asian | European | European | European | African American or Afro-Caribbean, East Asian, European, Greater Middle Eastern (Middle Eastern, North African or Persian), South Asian | Agent Input |
| performance_metrics.record_count | 15 | 8 | 2 | 8 | 15 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7310 | N/A | N/A | N/A | 0.7310 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.731} | N/A | N/A | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.731} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0175, 'ci_lower': 0.0035, 'ci_upper': 0.0315} | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0151, 'ci_lower': 0.0011, 'ci_upper': 0.029} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.66, 'ci_lower': 1.61, 'ci_upper': 1.71} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.13, 'ci_lower': 1.03, 'ci_upper': 1.23} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.66, 'ci_lower': 1.61, 'ci_upper': 1.71} | Agent Input |
| validation_sample_size | n=304,294 | n=19,668 | n=10,836 | n=19,668 | n=304,294 | Agent Input |
| samples_training | n=96,239 | n=391,124 | N/A | n=391,124 | n=96,239 | Agent Input |
| ancestry_distribution | GWAS: NR (2%), AFR (70%), AMR (50%), EAS (7%), EUR (74%), MAE (14%), MAO (2%), OTH (6%), SAS (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (13%), EAS (13%), EUR (20%), GME (13%), MAE (7%), SAS (13%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: AFR (20%), AMR (8%), EUR (72%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: NR (2%), AFR (70%), AMR (50%), EAS (7%), EUR (74%), MAE (14%), MAO (2%), OTH (6%), SAS (100%) / DEV: EUR (100%) / EVAL: AFR (20%), AMR (13%), EAS (13%), EUR (20%), GME (13%), MAE (7%), SAS (13%) | Agent Input |
| training_development_cohorts | ARIC AWI-Gen BBJ BioMe CARDIA CARDIoGRAMplusC4D CFS CHOP CHS CKB COMPASS EPIC_CAD GERA GerMIFS HANDLS HISAYAMA HRS HUNT HYPERGEN HealthABC INTERSTROKE JHS JOCO JUPITER KCPS LOLIPOP MESA MGBB MVP Multiple Other PMB PROMIS REGARDS RHS SIGNET SiGN UKB WHI deCODE eMERGE | UKB | N/A | UKB | ARIC AWI-Gen BBJ BioMe CARDIA CARDIoGRAMplusC4D CFS CHOP CHS CKB COMPASS EPIC_CAD GERA GerMIFS HANDLS HISAYAMA HRS HUNT HYPERGEN HealthABC INTERSTROKE JHS JOCO JUPITER KCPS LOLIPOP MESA MGBB MVP Multiple Other PMB PROMIS REGARDS RHS SIGNET SiGN UKB WHI deCODE eMERGE | Agent Input |
| publication.title | Polygenic Prediction of Peripheral Artery Disease and Major Adverse Limb Events. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Modifiable Lifestyle Factors, Genetic Risk, and Incident Peripheral Artery Disease Among Individuals With Type 2 Diabetes: A Prospective Study. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Polygenic Prediction of Peripheral Artery Disease and Major Adverse Limb Events. | Agent Input |
| publication.journal | JAMA Cardiol | Am J Hum Genet | Diabetes Care | Am J Hum Genet | JAMA Cardiol | Agent Input |
| date_release | 2025-06-16 | 2022-01-10 | 2025-02-26 | 2022-01-10 | 2025-06-16 | Agent Input |
| variants_number | 1296292 | 599514 | 19 | 242 | 1296292 | Agent Input |
| covariates | age, sex and the first ten principal components of genetic ancestry | sex, age, birth date, deprivation index, 16 PCs | age (continuous, years), sex (male, female), Townsend Deprivation Index (continuous), race/ethnicity (White, others), education attainment (college or university degree, A/AS levels or equivalent or O levels/GCSEs or equivalent or other professional qualifications, or none of the above), family history of CVD (yes, no), prevalence of hypertension (yes, no), use of antihypertensive medication (yes, no), use of lipidlowing medication (yes, no), use of aspirin (yes, no), diabetes duration (continuous, years), HbA1c (continuous, %), use of diabetes medication (none, only oral medication pills, or only insulin or combination of oral medications and insulin), genotype measurement batch, the first 10 principal components of ancestry, weighted healthy lifestyle scores (continuous) | sex, age, birth date, deprivation index, 16 PCs | age, sex and the first ten principal components of genetic ancestry | Agent Input |


### psoriatic arthritis

Candidate pool: `4` models. Eligible `Hit@k`: `1,2`.


| Field | Benchmark #1 | Benchmark #2 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001287 | PGS000342 | PGS001287 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 1/2 | Benchmark Only |
| AoU benchmark AUC | 0.5731 | 0.5102 | 0.5731 | Benchmark Only |
| Hit@1 | Yes | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | N/A | N/A | N/A | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | Benchmark Only |
| trait_reported | Psoriatic arthropathy | Psoriatic arthritis | Psoriatic arthropathy | Agent Input |
| trait_efo | psoriatic arthritis | psoriatic arthritis | psoriatic arthritis | Agent Input |
| phenotyping_reported | Psoriatic arthropathy | Psoriatic arthritis | Psoriatic arthropathy | Agent Input |
| method_name | snpnet | GWAS-significant variants, HLA-specific significant variants. | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM008935 | PPM000971 | PPM008935 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | NR | European | Agent Input |
| performance_metrics.record_count | 5 | 1 | 5 | Agent Input |
| performance_metrics.auc | 0.6765 | N/A | 0.6765 | Agent Input |
| performance_metrics.r2 | 0.0335 | N/A | 0.0335 | Agent Input |
| performance_metrics.full_model_auc | 0.7281 | 0.5620 | 0.7281 | Agent Input |
| performance_metrics.full_model_r2 | 0.0515 | N/A | 0.0515 | Agent Input |
| performance_metrics.incremental_auc | 0.0835 | N/A | 0.0835 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.72814, 'ci_lower': 0.67154, 'ci_upper': 0.78475} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.562, 'ci_lower': 0.506, 'ci_upper': 0.618} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.72814, 'ci_lower': 0.67154, 'ci_upper': 0.78475} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05154} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08346} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0335} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.67648, 'ci_lower': 0.61155, 'ci_upper': 0.7414} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05154} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08346} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.0335} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.67648, 'ci_lower': 0.61155, 'ci_upper': 0.7414} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=24,905 | n=543 | n=24,905 | Agent Input |
| samples_training | n=269,704 | N/A | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: NR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | N/A | UKB | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Evaluation of a Genetic Risk Score for Diagnosis of Psoriatic Arthritis. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | PLoS Genet | J Psoriasis Psoriatic Arthritis | PLoS Genet | Agent Input |
| date_release | 2021-10-21 | 2020-11-20 | 2021-10-21 | Agent Input |
| variants_number | 36 | 11 | 36 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


### sarcoidosis

Candidate pool: `4` models. Eligible `Hit@k`: `1,2,3`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001872 | PGS000922 | PGS000923 | PGS000922 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 2/3 | Benchmark Only |
| AoU benchmark AUC | 0.5729 | 0.5641 | 0.5570 | 0.5641 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 8/10 trials | Benchmark Only |
| trait_reported | Sarcoidosis | Sarcoidosis | Sarcoidosis (time-to-event) | Sarcoidosis | Agent Input |
| trait_efo | skin sarcoidosis | sarcoidosis | sarcoidosis | sarcoidosis | Agent Input |
| phenotyping_reported | Sarcoidosis | Sarcoidosis | TTE sarcoidosis | Sarcoidosis | Agent Input |
| method_name | Penalized regression (bigstatsr) | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM009865 | PPM007443 | PPM007447 | PPM007443 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 7 | 4 | 4 | 4 | Agent Input |
| performance_metrics.auc | N/A | 0.6428 | 0.6456 | 0.6428 | Agent Input |
| performance_metrics.r2 | N/A | 0.0174 | 0.0180 | 0.0174 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.6486 | 0.6545 | 0.6486 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0192 | 0.0209 | 0.0192 | Agent Input |
| performance_metrics.incremental_auc | N/A | 0.0919 | 0.0900 | 0.0919 | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6486, 'ci_lower': 0.60932, 'ci_upper': 0.68789} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65455, 'ci_lower': 0.6217, 'ci_upper': 0.6874} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6486, 'ci_lower': 0.60932, 'ci_upper': 0.68789} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0199, 'ci_lower': 0.0059, 'ci_upper': 0.0338} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01916} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.09187} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01741} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64282, 'ci_lower': 0.60353, 'ci_upper': 0.68211} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.02088} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.09004} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.018} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64561, 'ci_lower': 0.61168, 'ci_upper': 0.67954} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01916} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.09187} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01741} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64282, 'ci_lower': 0.60353, 'ci_upper': 0.68211} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,670 | n=67,425 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=269,704 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (29%), EUR (43%), GME (14%), SAS (14%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 79 | 12 | 22 | 12 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### bipolar disorder

Candidate pool: `3` models. Eligible `Hit@k`: `1,2,3`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002786 | PGS002787 | PGS002788 | PGS002786 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 1/3 | Benchmark Only |
| AoU benchmark AUC | 0.5650 | 0.5599 | 0.5382 | 0.5650 | Benchmark Only |
| Hit@1 | Yes | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | Benchmark Only |
| trait_reported | Bipolar disorder | Type 1 bipolar disorder | Type 2 bipolar disorder | Bipolar disorder | Agent Input |
| trait_efo | bipolar disorder | bipolar I disorder | bipolar II disorder | bipolar disorder | Agent Input |
| phenotyping_reported | Cognitive function (pattern comparison) | Psychiatric behavior (Dsm5 depression) | Psychiatric behavior (Sluggish cognitive tempo) | Cognitive function (pattern comparison) | Agent Input |
| method_name | SDPR | SDPR | SDPR | SDPR | Agent Input |
| performance_metrics.selected_performance_id | PPM015078 | PPM015158 | PPM015195 | PPM015078 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 50 | 50 | 50 | 50 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0025 | 0.0028 | 0.0031 | 0.0025 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00251110019585597} | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00275397293669774} | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00307366437856391} | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00251110019585597} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=2,524 | n=2,198 | n=2,524 | n=2,524 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | PGC | PGC | PGC | PGC | Agent Input |
| publication.title | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Agent Input |
| publication.journal | Transl Psychiatry | Transl Psychiatry | Transl Psychiatry | Transl Psychiatry | Agent Input |
| date_release | 2022-09-29 | 2022-09-29 | 2022-09-29 | 2022-09-29 | Agent Input |
| variants_number | 948996 | 937511 | 935292 | 948996 | Agent Input |
| covariates | age, PCs1-3 | age, PCs1-3 | age, PCs1-3 | age, PCs1-3 | Agent Input |


### hashimoto's thyroiditis

Candidate pool: `3` models. Eligible `Hit@k`: `1,2,3`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005272 | PGS005271 | PGS005270 | PGS005270 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.7941 | 0.7940 | 0.6412 | 0.6412 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | Benchmark Only |
| trait_reported | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Lymphocytic thyroiditis | Agent Input |
| trait_efo | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Hashimoto's thyroiditis | Agent Input |
| phenotyping_reported | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | lymphocytic thyroiditis | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM022755 | PPM022754 | PPM022753 | PPM022753 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6054 | 0.6297 | 0.6387 | 0.6387 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.605418550899187} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.629725726511746} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638677809581895} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.638677809581895} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.41698139161814} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.348528828383883} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.54908058789994} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.437661585839951} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.037} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.037} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.037} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.037} | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=94,651 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI NSGHI PMB UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | Agent Input |
| variants_number | 1085142 | 1085156 | 55 | 55 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Agent Input |


### nephrolithiasis

Candidate pool: `3` models. Eligible `Hit@k`: `1,2,3`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004563 | PGS004493 | PGS001250 | PGS001250 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.5566 | 0.5450 | 0.5376 | 0.5376 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | Benchmark Only |
| trait_reported | N20 (Calculus of kidney and ureter) | N20 (Calculus of kidney and ureter) | Calculus of kidney and ureter (time-to-event) | Calculus of kidney and ureter (time-to-event) | Agent Input |
| trait_efo | nephrolithiasis | nephrolithiasis | nephrolithiasis, ureterolithiasis | nephrolithiasis, ureterolithiasis | Agent Input |
| phenotyping_reported | N20 (Calculus of kidney and ureter) | N20 (Calculus of kidney and ureter) | TTE calculus of kidney and ureter | TTE calculus of kidney and ureter | Agent Input |
| method_name | RFDiseasemetaPRS | LDpred2 | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM020678 | PPM020608 | PPM008763 | PPM008763 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.5668 | 0.5668 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0059 | 0.0059 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.6649 | 0.6649 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | 0.0350 | 0.0350 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0149 | 0.0149 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66491, 'ci_lower': 0.64839, 'ci_upper': 0.68143} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66491, 'ci_lower': 0.64839, 'ci_upper': 0.68143} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03503} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01494} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00592} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.56681, 'ci_lower': 0.54876, 'ci_upper': 0.58486} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03503} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01494} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00592} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.56681, 'ci_lower': 0.54876, 'ci_upper': 0.58486} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.283041} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.22730929818809} | N/A | N/A | Agent Input |
| validation_sample_size | n=56,192 | n=56,192 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=174,489 | n=174,489 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Commun Biol | Commun Biol | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2024-03-18 | 2024-03-18 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 1059939 | 1059939 | 341 | 341 | Agent Input |
| covariates | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### preeclampsia

Candidate pool: `3` models. Eligible `Hit@k`: `1,2,3`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003586 | PGS004593 | PGS003587 | PGS003586 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 1/3 | Benchmark Only |
| AoU benchmark AUC | 0.8077 | 0.7604 | 0.5709 | 0.8077 | Benchmark Only |
| Hit@1 | Yes | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | Benchmark Only |
| trait_reported | Pre-eclampsia | Preeclampsia | Gestational hypertension | Pre-eclampsia | Agent Input |
| trait_efo | preeclampsia | preeclampsia | preeclampsia | preeclampsia | Agent Input |
| phenotyping_reported | Pre-eclampsia/eclampsia | Gestational hypertension | Pre-eclampsia/eclampsia | Pre-eclampsia/eclampsia | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | Agent Input |
| performance_metrics.selected_performance_id | PPM018280 | PPM020743 | PPM018281 | PPM018280 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.24, 'ci_upper': 1.38} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.14, 'ci_upper': 1.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.2, 'ci_lower': 1.14, 'ci_upper': 1.26} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.31, 'ci_lower': 1.24, 'ci_upper': 1.38} | Agent Input |
| validation_sample_size | n=25,582 | n=138,317 | n=25,582 | n=25,582 | Agent Input |
| samples_training | n=212,034 | N/A | n=212,034 | n=212,034 | Agent Input |
| ancestry_distribution | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: MAE (100%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (1%), ASN (7%), EUR (91%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (30%), AMR (50%), ASN (21%), EUR (78%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | N/A | BBJ BioMe EB FinnGen G&H MGBB UKB | BBJ BioMe EB FinnGen G&H InterPregGen MGBB MGI UKB | Agent Input |
| publication.title | Polygenic prediction of preeclampsia and gestational hypertension. | Associations of polygenic risk scores for preeclampsia and blood pressure with hypertensive disorders of pregnancy. | Polygenic prediction of preeclampsia and gestational hypertension. | Polygenic prediction of preeclampsia and gestational hypertension. | Agent Input |
| publication.journal | Nat Med | J Hypertens | Nat Med | Nat Med | Agent Input |
| date_release | 2023-06-22 | 2024-01-26 | 2023-06-22 | 2023-06-22 | Agent Input |
| variants_number | 1087033 | 1102059 | 1087916 | 1087033 | Agent Input |
| covariates | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | Collection year, genotyping batch, and the first 10 genetic principal components | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | maternal age at delivery, age2, and the first ten principal components of genetic ancestry | Agent Input |


### vitiligo

Candidate pool: `3` models. Eligible `Hit@k`: `1,2,3`.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000760 | PGS000738 | PGS001536 | PGS001536 | Agent Input |
| AoU benchmark rank | 1/3 | 2/3 | 3/3 | 3/3 | Benchmark Only |
| AoU benchmark AUC | 0.6417 | 0.6276 | 0.5669 | 0.5669 | Benchmark Only |
| Hit@1 | Yes | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | Yes | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | Benchmark Only |
| trait_reported | Vitiligo | Vitiligo | Vitiligo (time-to-event) | Vitiligo (time-to-event) | Agent Input |
| trait_efo | Vitiligo | Vitiligo | Vitiligo | Vitiligo | Agent Input |
| phenotyping_reported | anti-PD-L1 induced hypothyroidism in cancer patients | Red hair | TTE vitiligo | TTE vitiligo | Agent Input |
| method_name | GCTA-COJO forward selection highest PPA variants | Genome-wide significant variants | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM001935 | PPM018438 | PPM005219 | PPM005219 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 8 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.6419 | 0.6419 | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0162 | 0.0162 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | 0.6345 | 0.6345 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0386 | 0.0169 | 0.0169 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0816 | 0.0816 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63449, 'ci_lower': 0.58754, 'ci_upper': 0.68144} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63449, 'ci_lower': 0.58754, 'ci_upper': 0.68144} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'meta-analysis p-value', 'name_short': 'meta-analysis p-value', 'estimate': 1.1e-06} | {'name_long': 'pseudo R²', 'name_short': 'pseudo R²', 'estimate': 0.038569956} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01686} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08163} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01621} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64193, 'ci_lower': 0.59907, 'ci_upper': 0.68478} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01686} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.08163} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01621} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.64193, 'ci_lower': 0.59907, 'ci_upper': 0.68478} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.41, 'ci_lower': 1.22, 'ci_upper': 1.61} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.694777831} | N/A | N/A | Agent Input |
| validation_sample_size | n=1,584 | n=4,702 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=408,959 | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | N/A | UKB | UKB | Agent Input |
| publication.title | Genetic variation associated with thyroid autoimmunity shapes the systemic immune response to PD-1 checkpoint blockade. | Family Clustering of Autoimmune Vitiligo Results Principally from Polygenic Inheritance of Common Risk Alleles. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Am J Hum Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2021-06-11 | 2021-02-23 | 2021-11-25 | 2021-11-25 | Agent Input |
| variants_number | 42 | 48 | 77 | 77 | Agent Input |
| covariates | 5 genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### acute kidney injury

Candidate pool: `2` models. Eligible `Hit@k`: `1,2`.


| Field | Benchmark #1 | Benchmark #2 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004561 | PGS004491 | PGS004561 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 1/2 | Benchmark Only |
| AoU benchmark AUC | 0.5570 | 0.5217 | 0.5570 | Benchmark Only |
| Hit@1 | Yes | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | N/A | N/A | N/A | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | Benchmark Only |
| trait_reported | N17 (Acute renal failure) | N17 (Acute renal failure) | N17 (Acute renal failure) | Agent Input |
| trait_efo | acute kidney injury | acute kidney injury | acute kidney injury | Agent Input |
| phenotyping_reported | N17 (Acute renal failure) | N17 (Acute renal failure) | N17 (Acute renal failure) | Agent Input |
| method_name | RFDiseasemetaPRS | LDpred2 | RFDiseasemetaPRS | Agent Input |
| performance_metrics.selected_performance_id | PPM020676 | PPM020606 | PPM020676 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.153238} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.08493121737329} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.153238} | Agent Input |
| validation_sample_size | n=56,192 | n=56,192 | n=56,192 | Agent Input |
| samples_training | n=174,489 | n=174,489 | n=174,489 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | Agent Input |
| publication.title | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Agent Input |
| publication.journal | Commun Biol | Commun Biol | Commun Biol | Agent Input |
| date_release | 2024-03-18 | 2024-03-18 | 2024-03-18 | Agent Input |
| variants_number | 1059939 | 1059939 | 1059939 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Agent Input |


### autism spectrum disorder

Candidate pool: `2` models. Eligible `Hit@k`: `1,2`.


| Field | Benchmark #1 | Benchmark #2 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002790 | PGS000327 | PGS000327 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 2/2 | Benchmark Only |
| AoU benchmark AUC | 0.6024 | 0.5670 | 0.5670 | Benchmark Only |
| Hit@1 | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | N/A | N/A | N/A | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | Benchmark Only |
| trait_reported | Autism spectrum disorder | Autism spectrum disorder | Autism spectrum disorder | Agent Input |
| trait_efo | autism spectrum disorder | autism spectrum disorder | autism spectrum disorder | Agent Input |
| phenotyping_reported | Psychiatric behavior (withdrawn) | Autism spectrum disorder | Autism spectrum disorder | Agent Input |
| method_name | SDPR | Clumping and Thresholding (C+T) | Clumping and Thresholding (C+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM015334 | PPM000879 | PPM000879 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | Agent Input |
| performance_metrics.record_count | 50 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0055 | 0.0245 | 0.0245 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'partial R²', 'name_short': 'partial R²', 'estimate': 0.00546477739838} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0245} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0245} | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33, 'ci_lower': 1.3, 'ci_upper': 1.36} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33, 'ci_lower': 1.3, 'ci_upper': 1.36} | Agent Input |
| validation_sample_size | n=2,198 | n=7,148 | n=7,148 | Agent Input |
| samples_training | N/A | n=28,592 | n=28,592 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | PGC iPSYCH | ACE AGP AGRE MONBOS NIMH PGC SSC iPSYCH | ACE AGP AGRE MONBOS NIMH PGC SSC iPSYCH | Agent Input |
| publication.title | Sex-specific genetic association between psychiatric disorders and cognition, behavior and brain imaging in children and adults. | Identification of common genetic risk variants for autism spectrum disorder. | Identification of common genetic risk variants for autism spectrum disorder. | Agent Input |
| publication.journal | Transl Psychiatry | Nat Genet | Nat Genet | Agent Input |
| date_release | 2022-09-29 | 2020-09-18 | 2020-09-18 | Agent Input |
| variants_number | 916713 | 35087 | 35087 | Agent Input |
| covariates | age, PCs1-3 | Genetic PCs, genotyping wave | Genetic PCs, genotyping wave | Agent Input |


### idiopathic pulmonary fibrosis

Candidate pool: `2` models. Eligible `Hit@k`: `1,2`.


| Field | Benchmark #1 | Benchmark #2 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004695 | PGS001791 | PGS001791 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 2/2 | Benchmark Only |
| AoU benchmark AUC | 0.6742 | 0.6449 | 0.6449 | Benchmark Only |
| Hit@1 | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | N/A | N/A | N/A | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | Benchmark Only |
| trait_reported | Idiopathic pulmonary fibrosis | Idiopathic pulmonary fibrosis | Idiopathic pulmonary fibrosis | Agent Input |
| trait_efo | idiopathic pulmonary fibrosis | idiopathic pulmonary fibrosis | idiopathic pulmonary fibrosis | Agent Input |
| phenotyping_reported | Incident idiopathic pulmonary fibrosis | Idiopathic pulmonary fibrosis | Idiopathic pulmonary fibrosis | Agent Input |
| method_name | Genome-wide significant SNPs | PRS-CS-auto | PRS-CS-auto | Agent Input |
| performance_metrics.selected_performance_id | PPM020881 | PPM009295 | PPM009295 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | 0.0059 | 0.0059 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.7580 | 0.7580 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.758} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.758} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Hazard ratio (HR, high vs low PRS quintile)', 'name_short': 'Hazard ratio (HR, high vs low PRS quintile)', 'estimate': 3.78, 'ci_lower': 3.3, 'ci_upper': 4.34} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.005929} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.005929} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=402,042 | n=347,350 | n=347,350 | Agent Input |
| samples_training | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (100%), ASN (3%), EAS (30%), EUR (65%), OTH (2%) / EVAL: EUR (100%) | GWAS: AFR (100%), ASN (3%), EAS (30%), EUR (65%), OTH (2%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | BBJ BioMe BioVU EB FinnGen G&H HUNT LifeLines MGBB MGI TWB UCLA | BBJ BioMe BioVU EB FinnGen G&H HUNT LifeLines MGBB MGI TWB UCLA | Agent Input |
| publication.title | Low-level ambient sulfur dioxide exposure and genetic susceptibility associated with incidence of idiopathic pulmonary fibrosis: A national prospective cohort study. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Agent Input |
| publication.journal | Chemosphere | Cell Genom | Cell Genom | Agent Input |
| date_release | 2024-03-18 | 2022-09-08 | 2022-09-08 | Agent Input |
| variants_number | 23 | 910439 | 910439 | Agent Input |
| covariates | Age, sex, education level, smoking status, pack-years of smoking, BMI | sex,age,age2,age*sex,age^2*sex, 20PCs | sex,age,age2,age*sex,age^2*sex, 20PCs | Agent Input |


### nicotine dependence

Candidate pool: `2` models. Eligible `Hit@k`: `1,2`.


| Field | Benchmark #1 | Benchmark #2 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002037 | PGS001830 | PGS002037 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 1/2 | Benchmark Only |
| AoU benchmark AUC | 0.5974 | 0.5707 | 0.5974 | Benchmark Only |
| Hit@1 | Yes | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | N/A | N/A | N/A | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | Benchmark Only |
| trait_reported | Tobacco use disorder | Tobacco use disorder | Tobacco use disorder | Agent Input |
| trait_efo | nicotine dependence | nicotine dependence | nicotine dependence | Agent Input |
| phenotyping_reported | Tobacco use disorder | Tobacco use disorder | Tobacco use disorder | Agent Input |
| method_name | LDpred2 (bigsnpr) | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | Agent Input |
| performance_metrics.selected_performance_id | PPM011163 | PPM009533 | PPM011163 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | Agent Input |
| performance_metrics.record_count | 11 | 8 | 11 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0741, 'ci_lower': 0.0601, 'ci_upper': 0.0881} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0557, 'ci_lower': 0.0416, 'ci_upper': 0.0697} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0741, 'ci_lower': 0.0601, 'ci_upper': 0.0881} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,400 | n=19,400 | n=19,400 | Agent Input |
| samples_training | n=391,124 | n=391,124 | n=391,124 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (18%), AMR (9%), EAS (18%), EUR (36%), GME (9%), SAS (9%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (18%), AMR (9%), EAS (18%), EUR (36%), GME (9%), SAS (9%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Agent Input |
| publication.journal | Am J Hum Genet | Am J Hum Genet | Am J Hum Genet | Agent Input |
| date_release | 2022-01-10 | 2022-01-10 | 2022-01-10 | Agent Input |
| variants_number | 847691 | 13838 | 847691 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | Agent Input |


### otosclerosis

Candidate pool: `2` models. Eligible `Hit@k`: `1,2`.


| Field | Benchmark #1 | Benchmark #2 | Without Domain Knowledge | Field Type |
| --- | --- | --- | --- | --- |
| Selected PGS ID | PGS002046 | PGS001255 | PGS001255 | Agent Input |
| AoU benchmark rank | 1/2 | 2/2 | 2/2 | Benchmark Only |
| AoU benchmark AUC | 0.6377 | 0.6276 | 0.6276 | Benchmark Only |
| Hit@1 | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | Yes | Benchmark Only |
| Hit@3 | N/A | N/A | N/A | Benchmark Only |
| Hit@4 | N/A | N/A | N/A | Benchmark Only |
| Hit@5 | N/A | N/A | N/A | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | 10/10 trials | Benchmark Only |
| trait_reported | Otosclerosis | Otosclerosis (time-to-event) | Otosclerosis (time-to-event) | Agent Input |
| trait_efo | otosclerosis | otosclerosis | otosclerosis | Agent Input |
| phenotyping_reported | Otosclerosis | TTE otosclerosis | TTE otosclerosis | Agent Input |
| method_name | LDpred2 (bigsnpr) | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM011232 | PPM008784 | PPM008784 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | Agent Input |
| performance_metrics.record_count | 6 | 4 | 4 | Agent Input |
| performance_metrics.auc | N/A | 0.6319 | 0.6319 | Agent Input |
| performance_metrics.r2 | N/A | 0.0134 | 0.0134 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.6532 | 0.6532 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0209 | 0.0209 | Agent Input |
| performance_metrics.incremental_auc | N/A | 0.0595 | 0.0595 | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6532, 'ci_lower': 0.60975, 'ci_upper': 0.69665} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6532, 'ci_lower': 0.60975, 'ci_upper': 0.69665} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0182, 'ci_lower': 0.0043, 'ci_upper': 0.0321} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.02085} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05946} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01341} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.6319, 'ci_lower': 0.58724, 'ci_upper': 0.67656} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.02085} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.05946} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01341} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.6319, 'ci_lower': 0.58724, 'ci_upper': 0.67656} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=19,770 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (17%), EUR (50%), GME (17%), SAS (17%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | DEV: EUR (100%) / EVAL: AFR (25%), EUR (50%), SAS (25%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 570308 | 213 | 213 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |

