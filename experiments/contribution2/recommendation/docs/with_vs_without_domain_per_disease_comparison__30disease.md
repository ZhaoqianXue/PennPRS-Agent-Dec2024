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

- Catalog Search + Domain Knowledge `Hit@1`: `17/30 = 56.67%`; `trial_hits = 165/300 = 55.00%`
- Catalog Search + Domain Knowledge `Hit@2`: `21/30 = 70.00%`; `trial_hits = 214/300 = 71.33%`
- Catalog Search + Domain Knowledge `Hit@3`: `24/30 = 80.00%`; `trial_hits = 240/300 = 80.00%`
- Catalog Search + Domain Knowledge `Hit@4`: `27/30 = 90.00%`; `trial_hits = 261/300 = 87.00%`
- Catalog Search + Domain Knowledge `Hit@5`: `28/30 = 93.33%`; `trial_hits = 271/300 = 90.33%`
- Catalog Search Only `Hit@1`: `14/30 = 46.67%`; `trial_hits = 140/300 = 46.67%`
- Catalog Search Only `Hit@2`: `18/30 = 60.00%`; `trial_hits = 181/300 = 60.33%`
- Catalog Search Only `Hit@3`: `24/30 = 80.00%`; `trial_hits = 237/300 = 79.00%`
- Catalog Search Only `Hit@4`: `24/30 = 80.00%`; `trial_hits = 239/300 = 79.67%`
- Catalog Search Only `Hit@5`: `24/30 = 80.00%`; `trial_hits = 240/300 = 80.00%`
- Prompt-Only Baseline `Hit@1`: `3/30 = 10.00%`; `trial_hits = 32/300 = 10.67%`
- Prompt-Only Baseline `Hit@2`: `7/30 = 23.33%`; `trial_hits = 71/300 = 23.67%`
- Prompt-Only Baseline `Hit@3`: `10/30 = 33.33%`; `trial_hits = 101/300 = 33.67%`
- Prompt-Only Baseline `Hit@4`: `12/30 = 40.00%`; `trial_hits = 121/300 = 40.33%`
- Prompt-Only Baseline `Hit@5`: `20/30 = 66.67%`; `trial_hits = 199/300 = 66.33%`

## Percentile Hit

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Percentiles evaluated: `q ∈ {5, 10, 15, 20, 25}`.
- For each percentile threshold, define the tie-aware cutoff rank as `c_q = max(1, ceil(q/100 * M))`.
- A selection counts as `Top q% Hit` if its AoU benchmark rank satisfies `r <= c_q`.
- Denominator: fixed total disease count for modal selections and fixed total trial count for trial selections.
- Tie handling: if the AoU benchmark AUC is tied at cutoff rank `c_q`, all tied models count as `Top q%`.

- Catalog Search + Domain Knowledge `Top 5% Hit`: `17/30 = 56.67%`; `trial_hits = 165/300 = 55.00%`
- Catalog Search + Domain Knowledge `Top 10% Hit`: `19/30 = 63.33%`; `trial_hits = 178/300 = 59.33%`
- Catalog Search + Domain Knowledge `Top 15% Hit`: `22/30 = 73.33%`; `trial_hits = 211/300 = 70.33%`
- Catalog Search + Domain Knowledge `Top 20% Hit`: `22/30 = 73.33%`; `trial_hits = 213/300 = 71.00%`
- Catalog Search + Domain Knowledge `Top 25% Hit`: `22/30 = 73.33%`; `trial_hits = 218/300 = 72.67%`
- Catalog Search Only `Top 5% Hit`: `14/30 = 46.67%`; `trial_hits = 140/300 = 46.67%`
- Catalog Search Only `Top 10% Hit`: `15/30 = 50.00%`; `trial_hits = 153/300 = 51.00%`
- Catalog Search Only `Top 15% Hit`: `18/30 = 60.00%`; `trial_hits = 183/300 = 61.00%`
- Catalog Search Only `Top 20% Hit`: `19/30 = 63.33%`; `trial_hits = 189/300 = 63.00%`
- Catalog Search Only `Top 25% Hit`: `20/30 = 66.67%`; `trial_hits = 199/300 = 66.33%`
- Prompt-Only Baseline `Top 5% Hit`: `3/30 = 10.00%`; `trial_hits = 32/300 = 10.67%`
- Prompt-Only Baseline `Top 10% Hit`: `3/30 = 10.00%`; `trial_hits = 32/300 = 10.67%`
- Prompt-Only Baseline `Top 15% Hit`: `4/30 = 13.33%`; `trial_hits = 41/300 = 13.67%`
- Prompt-Only Baseline `Top 20% Hit`: `4/30 = 13.33%`; `trial_hits = 41/300 = 13.67%`
- Prompt-Only Baseline `Top 25% Hit`: `4/30 = 13.33%`; `trial_hits = 41/300 = 13.67%`

## Rank Fraction (r / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `r / M`
- Scale: smaller is better.
- Interpretation: `r / M = 0.20` means the selected model is ranked in the top 20% of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean r / M = 0.2935` (30 modal selections); `trial mean r / M = 0.3038` (300 trials)
- Catalog Search Only: `mean r / M = 0.3873` (30 modal selections); `trial mean r / M = 0.3883` (300 trials)
- Prompt-Only Baseline: `mean r / M = 0.6901` (30 modal selections); `trial mean r / M = 0.6886` (300 trials)

## Reverse Rank Fraction ((M - r) / M)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `(M - r) / M`
- Scale: `0.0` means bottom-ranked; larger is better.
- Interpretation: values closer to `1.0` mean the selected model is closer to the top of the disease-specific candidate pool.
- Catalog Search + Domain Knowledge: `mean (M - r) / M = 0.7065` (30 modal selections); `trial mean (M - r) / M = 0.6962` (300 trials)
- Catalog Search Only: `mean (M - r) / M = 0.6127` (30 modal selections); `trial mean (M - r) / M = 0.6117` (300 trials)
- Prompt-Only Baseline: `mean (M - r) / M = 0.3099` (30 modal selections); `trial mean (M - r) / M = 0.3114` (300 trials)

## Normalized Ranking Score (NRS)

- Inputs: `M` = number of candidate PRS models for the disease; `r` = AoU benchmark rank of the selected model among those `M` candidates.
- Formula: `NRS = (M - r) / (M - 1)`
- Scale: `NRS = 1.0` means top-ranked; `NRS = 0.0` means bottom-ranked; larger is better.
- Catalog Search + Domain Knowledge: `mean NRS = 0.8403` (30 modal selections); `trial mean NRS = 0.8289` (300 trials)
- Catalog Search Only: `mean NRS = 0.7256` (30 modal selections); `trial mean NRS = 0.7253` (300 trials)
- Prompt-Only Baseline: `mean NRS = 0.3715` (30 modal selections); `trial mean NRS = 0.3735` (300 trials)

## Per-Disease Tables

### prostate cancer

Candidate pool: `96` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000566 | PGS000044 | PGS001292 | PGS000592 | PGS002793 | PGS004155 | PGS005238 | PGS000030 | Agent Input |
| AoU benchmark rank | 1/95 | 2/95 | 3/95 | 4/95 | 5/95 | 30/95 | 51/95 | 29/95 | Benchmark Only |
| AoU benchmark AUC | 0.6550 | 0.6295 | 0.6041 | 0.5748 | 0.5665 | 0.5492 | 0.5402 | 0.5495 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 8/10 trials | Benchmark Only |
| trait_reported | Prostate cancer | Prostate cancer | Family history of prostate cancer | Prostate cancer | Prostate cancer | Prostate cancer | Prostate carcinoma | Prostate cancer | Agent Input |
| trait_efo | prostate carcinoma | prostate carcinoma | family history of prostate cancer | prostate carcinoma | prostate carcinoma | prostate carcinoma | prostate carcinoma | prostate carcinoma | Agent Input |
| phenotyping_reported | Cancer of prostate | Elevated serum prostate-specific antigen (PSA) levels | Prostate cancer (FH) | Cancer of prostate | Prostate cancer risk | Prostate cancer | 5-year incident prostate cancer | Prostate cancer metastasis or death | Agent Input |
| method_name | PRS-CS | Known susceptibility loci (genome-wide significant SNPs) | snpnet | lassosum | Genome-wide significant SNPs | UKBB-EUR.MultiPRS.CV | LDpred2 | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM001251 | PPM000104 | PPM008960 | PPM001277 | PPM015450 | PPM019534 | PPM022696 | PPM013019 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | East Asian | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 5 | 1 | 1 | 6 | 10 | 16 | Agent Input |
| performance_metrics.auc | N/A | N/A | 0.5487 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | 0.0055 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.5910 | N/A | 0.5657 | 0.6160 | N/A | 0.7049 | 0.7890 | 0.6300 | Agent Input |
| performance_metrics.full_model_r2 | 0.0245 | N/A | 0.0115 | 0.0408 | N/A | 0.1280 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | 0.0170 | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.591, 'ci_lower': 0.573, 'ci_upper': 0.609} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.56572, 'ci_lower': 0.5538, 'ci_upper': 0.57764} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.616, 'ci_lower': 0.598, 'ci_upper': 0.635} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7049161, 'ci_lower': 0.70043717, 'ci_upper': 0.70939503} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.789, 'ci_lower': 0.782, 'ci_upper': 0.796} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.63} | Agent Input |
| performance_metrics.other_metrics | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0245} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.152} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.85, 'ci_lower': 1.76, 'ci_upper': 4.62} | {'name_long': 'OR (per 1-point increase in PRS)', 'name_short': 'OR (per 1-point increase in PRS)', 'estimate': 1.23, 'ci_lower': 1.1, 'ci_upper': 1.37} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01155} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.01702} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00547} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.54869, 'ci_lower': 0.53677, 'ci_upper': 0.56062} | {'name_long': "Nagelkerke's Pseudo-R²", 'name_short': "Nagelkerke's Pseudo-R²", 'estimate': 0.0408} {'name_long': 'Brier score', 'name_short': 'Brier score', 'estimate': 0.15} {'name_long': 'Odds Ratio (OR, top 1% vs. Rest)', 'name_short': 'Odds Ratio (OR, top 1% vs. Rest)', 'estimate': 2.55, 'ci_lower': 1.55, 'ci_upper': 4.2} | {'name_long': 'Odds Ratio (OR, top vs average percentile)', 'name_short': 'Odds Ratio (OR, top vs average percentile)', 'estimate': 2.87, 'ci_lower': 1.29, 'ci_upper': 6.4} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.12803272, 'ci_lower': 0.12275071, 'ci_upper': 0.13385339} | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.393, 'ci_lower': 1.3, 'ci_upper': 1.493} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.332, 'se': 0.0352} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.537, 'ci_lower': 1.433, 'ci_upper': 1.648} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.43, 'se': 0.0357} | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.16612832, 'ci_lower': 2.12587867, 'ci_upper': 2.20714003} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.77294139, 'ci_lower': 0.75418521, 'ci_upper': 0.79169757} | N/A | N/A | Agent Input |
| validation_sample_size | n=5,607 | n=17,012 | n=24,905 | n=5,607 | n=1,190 | n=171,474 | n=184,010 | n=1,991 | Agent Input |
| samples_training | n=5,650 | N/A | n=269,704 | n=5,650 | n=109,323 | n=9,671 | n=10,000 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (5%), EUR (95%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (2%), AMR (40%), EAS (1%), EUR (92%), MAE (3%) / DEV: AFR (3%), EAS (1%), EUR (96%) / EVAL: EAS (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (67%), SAS (33%) | GWAS: AFR (9%), AMR (3%), EAS (12%), EUR (76%) / DEV: EUR (100%) / EVAL: AFR (20%), EUR (60%), SAS (20%) | GWAS: EUR (100%) / EVAL: NR (10%), AFR (10%), EUR (70%), MAE (10%) | Agent Input |
| training_development_cohorts | MGI | ICR IGD PLCO ProtecT UKGPCS deCODE | UKB | MGI | AAPC BCFR BFBOCC BRICOH CBCS CIMBA CNIO CONSIT Chicago DEMOKRITOS DKFZ EMBRACE FCCC G-FaST GC-HBOC GEMO HCSC HEBCS HEBON HUNBOCS HVH ICO ICR IGD ILUH IOVHBOCS IPOBCS MAYO MSKCC MUV NCI OCGN OSU OUH PBCS PLCO ProtecT SWE-BRCA UKB UKGPCS UPENN UPITT VFCTG deCODE kConFab | UKB | UKB | N/A | Agent Input |
| publication.title | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Reducing overdiagnosis by polygenic risk-stratified screening: findings from the Finnish section of the ERSPC. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cancer PRSweb: An Online Repository with Polygenic Risk Scores for Major Cancer Traits and Their Evaluation in Two Independent Biobanks. | Application of European-specific polygenic risk scores for predicting prostate cancer risk in different ancestry populations. | Evaluation of polygenic scoring methods in five biobanks shows larger variation between biobanks than methods and finds benefits of ensemble learning. | Polygenic risk scores for prostate cancer: Comparative evaluations in UK and Australian cohorts. | Association analyses of more than 140,000 men identify 63 new prostate cancer susceptibility loci. | Agent Input |
| publication.journal | Am J Hum Genet | Br J Cancer | PLoS Genet | Am J Hum Genet | Prostate | Am J Hum Genet | HGG Adv | Nat Genet | Agent Input |
| date_release | 2020-12-15 | 2019-12-18 | 2021-10-21 | 2020-12-15 | 2022-09-29 | 2023-12-19 | 2025-10-06 | 2019-10-14 | Agent Input |
| variants_number | 1111494 | 66 | 602 | 1334 | 82 | 1139693 | 964607 | 147 | Agent Input |
| covariates | age, sex, batch PCs 1-4 | cancer stage, Gleason score | age, sex, UKB array type, Genotype PCs | age, sex, batch PCs 1-4 | disease diagnostic age or age at recruitment, subgroups and 10 principal components | 0 | Age-specific absolute risk adjusted by PGS relative risk | Unknown | Agent Input |


### thyroid carcinoma

Candidate pool: `32` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005260 | PGS005274 | PGS005273 | PGS005259 | PGS005258 | PGS005259 | PGS000208 | PGS000087 | Agent Input |
| AoU benchmark rank | 1/32 | 2/32 | 3/32 | 4/32 | 5/32 | 4/32 | 16/32 | 19/32 | Benchmark Only |
| AoU benchmark AUC | 0.8113 | 0.8069 | 0.8016 | 0.7865 | 0.6376 | 0.7865 | 0.5890 | 0.5868 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Thyroid carcenoma | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma vs benign nodular goiter | Thyroid carcenoma | Thyroid carcenoma | Thyroid carcenoma | Thyroid cancer | Thyroid cancer | Agent Input |
| trait_efo | thyroid carcinoma | benign, thyroid carcinoma, nodular goiter | benign, thyroid carcinoma, nodular goiter | thyroid carcinoma | thyroid carcinoma | thyroid carcinoma | thyroid carcinoma | thyroid carcinoma | Agent Input |
| phenotyping_reported | thyroid carcenoma | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma vs benign nodular goiter | thyroid carcenoma | thyroid carcenoma | thyroid carcenoma | Thyroid cancer | Incident thyroid cancer | Agent Input |
| method_name | PRSCS | PRSCS | PRSCS | PRSCS | Pruning and Thresholding (P+T) | PRSCS | Genome-wide significant variants | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM022743 | PPM022757 | PPM022756 | PPM022742 | PPM022741 | PPM022742 | PPM000632 | PPM002052 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6845 | 0.6135 | 0.6174 | 0.6953 | 0.6862 | 0.6953 | 0.7510 | 0.6790 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.684522760200784} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.613489463745261} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.617388005401901} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.695254013741303} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.686161285410893} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.695254013741303} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.751, 'ci_lower': 0.736, 'ci_upper': 0.768} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.679} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.666, 'se': 0.023} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.96019114706853} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.673041992501825} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49346171423604} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.401096723418125} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.55051776688383} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.438588918302023} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.03688674186851} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.71142253524162} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.02} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.016} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 2.03688674186851} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.71142253524162} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.57, 'ci_lower': 1.36, 'ci_upper': 1.82} | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=94,651 | n=130,279 | n=391,189 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BioMe BioVU HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB HUNT MGBB MGI NSGHI PMB UKB | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT KCPS LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT KCPS LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | AllofUs BBJ BioMe BioVU CKB EXCEED FinnGen HUNT KCPS LATVIANBIOBANK MGBB MGI MVP NSGHI PMB QSKIN UKB deCODE | NBS UKB | N/A | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Assessing thyroid cancer risk using polygenic risk scores. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | medRxiv | medRxiv | medRxiv | Proc Natl Acad Sci U S A | Nat Commun | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2020-07-01 | 2020-02-12 | Agent Input |
| variants_number | 1085170 | 1084965 | 1085164 | 1085173 | 84 | 1085173 | 10 | 12 | Agent Input |
| covariates | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | gender, birth year, family history of disease (1st or 2nd degree relative) | Age at assessment, sex,, genotyping array, PCs(1-15), body mass index (BMI <25 vs. 25≤BMI<30, BMI≥30) | Agent Input |


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
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 7/10 trials | 10/10 trials | 9/10 trials | Benchmark Only |
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


### obstructive sleep apnea

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
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 7/10 trials | 10/10 trials | Benchmark Only |
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
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
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


### testicular neoplasm

Candidate pool: `14` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000796 | PGS000600 | PGS001164 | PGS000599 | PGS000597 | PGS000604 | PGS001164 | PGS000595 | Agent Input |
| AoU benchmark rank | 1/13 | 2/13 | 3/13 | 4/13 | 5/13 | 10/13 | 3/13 | 13/13 | Benchmark Only |
| AoU benchmark AUC | 0.9212 | 0.9128 | 0.9044 | 0.9021 | 0.8730 | 0.7468 | 0.9044 | 0.4140 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | No | Yes | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 6/10 trials | 10/10 trials | Benchmark Only |
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


### uterine carcinoma

Candidate pool: `14` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000075 | PGS000786 | PGS003381 | PGS002735 | PGS004244 | PGS003381 | PGS001795 | PGS000073 | Agent Input |
| AoU benchmark rank | 1/14 | 2/14 | 3/14 | 4/14 | 5/14 | 3/14 | 9/14 | 14/14 | Benchmark Only |
| AoU benchmark AUC | 0.6120 | 0.6113 | 0.5970 | 0.5609 | 0.5519 | 0.5970 | 0.5044 | 0.4138 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | 10/10 trials | 7/10 trials | Benchmark Only |
| trait_reported | Endometrial cancer | Endometrial cancer | Uterine endometrial carcinoma | Endometrial cancer | Endometrial cancer | Uterine endometrial carcinoma | Uterine cancer | Cervical cancer | Agent Input |
| trait_efo | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | endometrial carcinoma | uterine carcinoma | cervical carcinoma | Agent Input |
| phenotyping_reported | Incident endometrial cancer | Incident endometrial cancer | uterine endometrial carcinoma | Risk of endometrial cancer | Endometrial cancer | uterine endometrial carcinoma | Uterine cancer | Incident cervical cancer | Agent Input |
| method_name | Genome-wide significant variants | 9 variants from Graff et al (PGS000075) with inverse variant weights | lassosum | Genome-wide significant variants | PRSice-2 | lassosum | PRS-CS-auto | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM002041 | PPM002057 | PPM016256 | PPM014832 | PPM020301 | PPM016256 | PPM009299 | PPM002039 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 3 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | 0.0019 | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7550 | 0.7540 | 0.7610 | 0.5600 | N/A | 0.7610 | 0.6600 | 0.7450 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.4860 | 0.1100 | N/A | N/A | 0.1100 | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.755} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.754} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.761} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.56, 'ci_lower': 0.54, 'ci_upper': 0.57} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.761} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.66} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75, 'se': 0.017} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.486} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11} | {'name_long': 'Odds ratio (OR, third vs first tertile)', 'name_short': 'Odds ratio (OR, third vs first tertile)', 'estimate': 1.55, 'ci_lower': 1.37, 'ci_upper': 1.74} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11} | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.001948} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.19, 'ci_lower': 1.1, 'ci_upper': 1.29} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.18, 'ci_lower': 1.09, 'ci_upper': 1.27} | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.25, 'ci_lower': 1.14, 'ci_upper': 1.36} | N/A | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.09, 'ci_upper': 1.37} | Agent Input |
| validation_sample_size | n=212,156 | n=212,156 | n=144,479 | n=118,636 | n=133,830 | n=144,479 | n=170,276 | n=211,795 | Agent Input |
| samples_training | N/A | N/A | N/A | n=1,757 | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: NR (34%), EUR (66%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (15%), EUR (84%), OTH (80%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | ANECS B58C CoRGI E2C2 HCS NBBS NSECG QIMR SEARCH WTCCC | N/A | N/A | N/A | N/A | BBJ BioMe BioVU CCPM CKB EB FinnGen HUNT MGBB MGI deCODE | TwinGene | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Development and evaluation of polygenic risk scores for prediction of endometrial cancer risk in European women. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Cancer Res | Genet Med | NPJ Precis Oncol | Cancer Res | Cell Genom | Nat Commun | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2023-01-19 | 2022-07-21 | 2023-12-15 | 2023-01-19 | 2022-09-08 | 2020-02-12 | Agent Input |
| variants_number | 9 | 9 | 529365 | 19 | 16 | 529365 | 911692 | 10 | Agent Input |
| covariates | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | Age at assessment, family history of cancer, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), age at menarche, body mass index, Menopausal status (pre-menopausal vs. post-menopausal vs. unknown or hysterectomy), ever used hormone replacement therapy, oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), | age, top 20 genetic principal components | Unknown | first 10 genetic principal components | age, top 20 genetic principal components | sex,age,age2,age*sex,age^2*sex, 20PCs | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Agent Input |


### kidney cancer

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS000787 | PGS000722 | PGS004245 | PGS000076 | PGS004908 | PGS004908 | PGS000076 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 1/10 | 1/10 | 5/10 | Benchmark Only |
| AoU benchmark AUC | 0.5824 | 0.5491 | 0.5488 | 0.5456 | 0.5441 | 0.5824 | 0.5824 | 0.5441 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 8/10 trials | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| trait_efo | renal carcinoma | renal cell carcinoma | renal carcinoma | renal cell carcinoma | renal cell carcinoma | renal carcinoma | renal carcinoma | renal cell carcinoma | Agent Input |
| phenotyping_reported | Kidney cancer | Incident kidney cancer | Incident kidney cancer | Kidney cancer | Incident kidney cancer | Kidney cancer | Kidney cancer | Incident kidney cancer | Agent Input |
| method_name | Genome-wide significant SNPs | 19 variants from Graff et al (PGS000076) with inverse variant weights | Genome-wide significant variants | PRSice-2 | Genome-wide significant variants | Genome-wide significant SNPs | Genome-wide significant SNPs | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM021361 | PPM002058 | PPM001652 | PPM020302 | PPM002042 | PPM021361 | PPM021361 | PPM002042 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 1 | 2 | 3 | 2 | 2 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7400 | 0.7220 | 0.5670 | N/A | 0.7220 | 0.7400 | 0.7400 | 0.7220 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.3660 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.723, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.567, 'ci_lower': 0.543, 'ci_upper': 0.591} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.724, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.724, 'se': 0.011} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.366} | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.15, 'ci_lower': 1.07, 'ci_upper': 1.24} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.02, 'ci_upper': 1.45} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.08, 'ci_upper': 1.26} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.08, 'ci_upper': 1.26} | Agent Input |
| validation_sample_size | n=324,805 | n=391,610 | n=400,812 | n=133,830 | n=391,610 | n=324,805 | n=324,805 | n=391,610 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | AHS ASHRAM ATBC BioVU CEERCC CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC ICR Karolinska Leeds MCCS MDACCS MDARCCS Moscow NCI NHS PHS PLCO RMHT SEARCH SORCE Tromso UKBS USKC Umea VARI VITAL WHI WHS WTCCC conFIRM deCODE | N/A | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | BBJ FinnGen NCI | BBJ FinnGen NCI | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Nat Genet | Nat Commun | JNCI Cancer Spectr | NPJ Precis Oncol | Nat Commun | Nat Genet | Nat Genet | Nat Commun | Agent Input |
| date_release | 2024-05-22 | 2021-05-28 | 2021-02-03 | 2023-12-15 | 2020-02-12 | 2024-05-22 | 2024-05-22 | 2020-02-12 | Agent Input |
| variants_number | 107 | 19 | 15 | 12 | 19 | 107 | 107 | 19 | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Genotyping array | first 10 genetic principal components | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Agent Input |


### obesity

Candidate pool: `10` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005235 | PGS005154 | PGS003959 | PGS002033 | PGS005145 | PGS005235 | PGS001298 | PGS001298 | Agent Input |
| AoU benchmark rank | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 1/10 | 8/10 | 8/10 | Benchmark Only |
| AoU benchmark AUC | 0.6311 | 0.6165 | 0.5798 | 0.5753 | 0.5667 | 0.6311 | 0.5549 | 0.5549 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Adiposity | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | Adiposity | Obesity (time-to-event) | Obesity (time-to-event) | Agent Input |
| trait_efo | obesity | obesity | obesity | obesity, overweight body mass index status, overnutrition | obesity | obesity | obesity | obesity | Agent Input |
| phenotyping_reported | Obesity (phecode: 278.1) | Obesity | Obesity | Overweight, obesity and other hyperalimentation | Obesity | Obesity (phecode: 278.1) | TTE obesity | TTE obesity | Agent Input |
| method_name | LDpred2-auto | CT-SLEB | Genome-wide significant SNPs | LDpred2 (bigsnpr) | PRS-CS | LDpred2-auto | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM022667 | PPM022374 | PPM019107 | PPM011135 | PPM022365 | PPM022667 | PPM008991 | PPM008991 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | East Asian | European, Not reported | European | East Asian | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 7 | 8 | 1 | 2 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.5757 | 0.5757 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | 0.0115 | 0.0115 | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.5956 | 0.5956 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | 0.0181 | 0.0181 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.0336 | 0.0336 | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59555, 'ci_lower': 0.58697, 'ci_upper': 0.60413} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.59555, 'ci_lower': 0.58697, 'ci_upper': 0.60413} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0789, 'ci_lower': 0.0651, 'ci_upper': 0.0927} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01814} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03355} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57573, 'ci_lower': 0.56713, 'ci_upper': 0.58434} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01814} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03355} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.57573, 'ci_lower': 0.56713, 'ci_upper': 0.58434} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.9704649488977} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 1.76187749677908} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.149, 'se': 0.028} | N/A | {'name_long': 'Beta', 'name_short': 'β', 'estimate': 1.60817500694587} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.9704649488977} | N/A | N/A | Agent Input |
| validation_sample_size | n=100,960 | n=58,688 | n=27,429 | n=20,000 | n=58,688 | n=100,960 | n=67,425 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | N/A | N/A | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (19%), EUR (81%) / EVAL: EAS (100%) | GWAS: NR (33%), EUR (67%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EAS (100%) / EVAL: EAS (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | EGG GIANT UKB | BBJ | N/A | UKB | BBJ | EGG GIANT UKB | UKB | UKB | Agent Input |
| publication.title | Modeling the genomic architecture of adiposity and anthropometrics across the lifespan. | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | The sulfur microbial diet and increased risk of obesity: Findings from a population-based prospective cohort study. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Assessment of polygenic risk score performance in East Asian populations for ten common diseases. | Modeling the genomic architecture of adiposity and anthropometrics across the lifespan. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Nat Commun | Commun Biol | Clin Nutr | Am J Hum Genet | Commun Biol | Nat Commun | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2025-10-06 | 2025-03-17 | 2023-10-17 | 2022-01-10 | 2025-03-17 | 2025-10-06 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 709828 | 443124 | 940 | 846292 | 908466 | 709828 | 9227 | 9227 | Agent Input |
| covariates | age, sex, batch, and the first 10 genetic principal components | age, sex | Age, sex, race, centres, education, Townsend deprivation index, household income, smoking, alcohol consumption, physical activity, sleep pattern, energy intake, and BMI, WC or BF% at baseline | sex, age, birth date, deprivation index, 16 PCs | age, sex | age, sex, batch, and the first 10 genetic principal components | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### ankylosing spondylitis

Candidate pool: `9` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS001876 | PGS001267 | PGS001268 | PGS002089 | PGS003424 | PGS002089 | PGS001268 | PGS001267 | Agent Input |
| AoU benchmark rank | 1/9 | 2/9 | 3/9 | 4/9 | 5/9 | 4/9 | 3/9 | 2/9 | Benchmark Only |
| AoU benchmark AUC | 0.7415 | 0.7397 | 0.7362 | 0.7188 | 0.6491 | 0.7188 | 0.7362 | 0.7397 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 9/10 trials | Benchmark Only |
| trait_reported | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis (time-to-event) | Ankylosing spondylitis | Agent Input |
| trait_efo | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | ankylosing spondylitis | Agent Input |
| phenotyping_reported | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | Ankylosing spondylitis | TTE ankylosing spondylitis | Ankylosing spondylitis | Agent Input |
| method_name | Penalized regression (bigstatsr) | snpnet | snpnet | LDpred2 (bigsnpr) | LDpred2 | LDpred2 (bigsnpr) | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM009896 | PPM008844 | PPM008849 | PPM011572 | PPM017077 | PPM011572 | PPM008849 | PPM008844 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | East Asian | European | European | European | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 1 | 5 | 5 | 5 | Agent Input |
| performance_metrics.auc | N/A | 0.7265 | 0.7346 | N/A | N/A | N/A | 0.7346 | 0.7265 | Agent Input |
| performance_metrics.r2 | N/A | 0.0988 | 0.1023 | N/A | N/A | N/A | 0.1023 | 0.0988 | Agent Input |
| performance_metrics.full_model_auc | N/A | 0.7433 | 0.7488 | N/A | 0.7605 | N/A | 0.7488 | 0.7433 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.1092 | 0.1150 | N/A | N/A | N/A | 0.1150 | 0.1092 | Agent Input |
| performance_metrics.incremental_auc | N/A | 0.1299 | 0.1269 | N/A | N/A | N/A | 0.1269 | 0.1299 | Agent Input |
| performance_metrics.classification_metrics | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74328, 'ci_lower': 0.70673, 'ci_upper': 0.77983} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.7605} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74878, 'ci_lower': 0.71314, 'ci_upper': 0.78442} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74328, 'ci_lower': 0.70673, 'ci_upper': 0.77983} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0797, 'ci_lower': 0.0653, 'ci_upper': 0.0941} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.10925} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12994} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.09877} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.72651, 'ci_lower': 0.68965, 'ci_upper': 0.76337} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0919, 'ci_lower': 0.0775, 'ci_upper': 0.1063} | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0919, 'ci_lower': 0.0775, 'ci_upper': 0.1063} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.115} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12686} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.10232} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.7346, 'ci_lower': 0.69884, 'ci_upper': 0.77037} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.10925} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.12994} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.09877} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.72651, 'ci_lower': 0.68965, 'ci_upper': 0.76337} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=18,262 | n=67,425 | n=67,425 | n=18,262 | n=1,298 | n=18,262 | n=67,425 | n=67,425 | Agent Input |
| samples_training | n=391,124 | n=269,704 | n=269,704 | n=391,124 | N/A | n=391,124 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | GWAS: EAS (100%) / EVAL: EAS (100%) | DEV: EUR (100%) / EVAL: EUR (60%), GME (20%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | N/A | UKB | UKB | UKB | Agent Input |
| publication.title | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Genome-wide association study reveals ethnicity-specific SNPs associated with ankylosing spondylitis in the Taiwanese population. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | Am J Hum Genet | PLoS Genet | PLoS Genet | Am J Hum Genet | J Transl Med | Am J Hum Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2022-01-10 | 2021-10-21 | 2021-10-21 | 2022-01-10 | 2023-02-08 | 2022-01-10 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 85 | 10 | 10 | 22026 | 100 | 22026 | 10 | 10 | Agent Input |
| covariates | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | sex, age, birth date, deprivation index, 16 PCs | Unknown | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### aortic stenosis

Candidate pool: `8` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005254 | PGS005255 | PGS005256 | PGS004911 | PGS004910 | PGS005254 | PGS005252 | PGS000739 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | 1/8 | 8/8 | 7/8 | Benchmark Only |
| AoU benchmark AUC | 0.6375 | 0.6233 | 0.6228 | 0.5181 | 0.5166 | 0.6375 | 0.3445 | 0.4740 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | No | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | No | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | No | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | No | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Aortic stenosis | Mean pressure gradient | Peak aortic velocity | Hypertrophic cardiomyopathy (MTAG) | Hypertrophic cardiomyopathy | Aortic stenosis | Aortic stenosis | Hypertrophic cardiomyopathy | Agent Input |
| trait_efo | aortic stenosis | aortic stenosis, aortic measurement | aortic stenosis, aortic measurement | hypertrophic cardiomyopathy | hypertrophic cardiomyopathy | aortic stenosis | aortic stenosis | hypertrophic cardiomyopathy | Agent Input |
| phenotyping_reported | incident aortic stenosis | incident aortic stenosis | incident aortic stenosis | Hypertrophic cardiomyopathy | Hypertrophic cardiomyopathy | incident aortic stenosis | Incident aortic stenosis cases | Hypertrophic cardiomyopathy | Agent Input |
| method_name | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | PRS-CS | LDPred2 | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM022737 | PPM022738 | PPM022739 | PPM021367 | PPM021366 | PPM022737 | PPM022733 | PPM018531 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | N/A | N/A | N/A | 0.8000 | 0.7300 | N/A | 0.8700 | 0.8210 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | 0.0480 | 0.0310 | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | N/A | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.8} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.73} | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.87} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.821, 'ci_lower': 0.772, 'ci_upper': 0.871} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.048} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.9} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.031} {'name_long': 'Odds ratio (OR, high vs median tertile)', 'name_short': 'Odds ratio (OR, high vs median tertile)', 'estimate': 5.5} | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.64, 'ci_lower': 1.5, 'ci_upper': 1.78} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.53, 'ci_lower': 1.4, 'ci_upper': 1.66} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.53, 'ci_lower': 1.41, 'ci_upper': 1.67} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 2.34} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.33} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.97} {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.26} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.64, 'ci_lower': 1.5, 'ci_upper': 1.78} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.92} | N/A | Agent Input |
| validation_sample_size | n=244,450 | n=244,450 | n=244,450 | n=343,182 | n=343,182 | n=244,450 | n=446,895 | n=184,511 | Agent Input |
| samples_training | n=205,483 | n=98,645 | n=96,385 | N/A | N/A | n=205,483 | n=47,691 | n=47,737 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: NR (2%), AFR (3%), EAS (80%), EUR (90%), OTH (60%), SAS (4%) / DEV: MAE (100%) / EVAL: EUR (40%), MAE (60%) | Agent Input |
| training_development_cohorts | N/A | N/A | N/A | BRRD GEL HCMR RBH-CRB | BRRD GEL HCMR RBH-CRB | N/A | MGBB | BRRD HCMR UKB | Agent Input |
| publication.title | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Evaluation of polygenic scores for hypertrophic cardiomyopathy in the general population and across clinical settings. | Multitrait analyses identify genetic variants associated with aortic valve function and aortic stenosis risk. | Genomic and transcriptomic analyses of aortic stenosis enhance therapeutic target discovery and disease prediction. | Common genetic variants and modifiable risk factors underpin hypertrophic cardiomyopathy susceptibility and expressivity. | Agent Input |
| publication.journal | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Nat Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2025-02-26 | 2025-02-26 | 2026-01-19 | 2026-01-19 | 2021-02-23 | Agent Input |
| variants_number | 1110912 | 1111632 | 1111632 | 374114 | 374190 | 1110912 | 1119377 | 27 | Agent Input |
| covariates | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | age, age^2, sex, PC1-10 | age, age^2, sex, PC1-10 | self-reported sex, age at DNA collection, age2 at DNA collection, and the first five principal components of genetic ancestry. | age, sex, genetic ancestry principal components 1-5, type 2 diabetes, hypertension, coronary artery disease, hyperlipidemia, body mass index, current smoking, renal failure. | Clinical risk factors (obesity, HTN, AF, CAD), HCM-ACMG rare variant carrier status, age, sex, genotyping array, and PCs 1-5 | Agent Input |


### renal carcinoma

Candidate pool: `8` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004908 | PGS000787 | PGS000722 | PGS004245 | PGS000076 | PGS004908 | PGS004908 | PGS000076 | Agent Input |
| AoU benchmark rank | 1/8 | 2/8 | 3/8 | 4/8 | 5/8 | 1/8 | 1/8 | 5/8 | Benchmark Only |
| AoU benchmark AUC | 0.5824 | 0.5491 | 0.5488 | 0.5456 | 0.5441 | 0.5824 | 0.5824 | 0.5441 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Kidney cancer | Agent Input |
| trait_efo | renal carcinoma | renal cell carcinoma | renal carcinoma | renal cell carcinoma | renal cell carcinoma | renal carcinoma | renal carcinoma | renal cell carcinoma | Agent Input |
| phenotyping_reported | Kidney cancer | Incident kidney cancer | Incident kidney cancer | Kidney cancer | Incident kidney cancer | Kidney cancer | Kidney cancer | Incident kidney cancer | Agent Input |
| method_name | Genome-wide significant SNPs | 19 variants from Graff et al (PGS000076) with inverse variant weights | Genome-wide significant variants | PRSice-2 | Genome-wide significant variants | Genome-wide significant SNPs | Genome-wide significant SNPs | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM021361 | PPM002058 | PPM001652 | PPM020302 | PPM002042 | PPM021361 | PPM021361 | PPM002042 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 1 | 2 | 3 | 2 | 2 | 3 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7400 | 0.7220 | 0.5670 | N/A | 0.7220 | 0.7400 | 0.7400 | 0.7220 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.3660 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.723, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.567, 'ci_lower': 0.543, 'ci_upper': 0.591} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.724, 'se': 0.011} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.74, 'ci_lower': 0.72, 'ci_upper': 0.75} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.722} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.724, 'se': 0.011} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.366} | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.15, 'ci_lower': 1.07, 'ci_upper': 1.24} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.02, 'ci_upper': 1.45} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.08, 'ci_upper': 1.26} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.5, 'ci_lower': 1.43, 'ci_upper': 1.58} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.16, 'ci_lower': 1.08, 'ci_upper': 1.26} | Agent Input |
| validation_sample_size | n=324,805 | n=391,610 | n=400,812 | n=133,830 | n=391,610 | n=324,805 | n=324,805 | n=391,610 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: AFR (70%), AMR (70%), EAS (16%), EUR (82%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | BBJ FinnGen NCI | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | AHS ASHRAM ATBC BioVU CEERCC CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC ICR Karolinska Leeds MCCS MDACCS MDARCCS Moscow NCI NHS PHS PLCO RMHT SEARCH SORCE Tromso UKBS USKC Umea VARI VITAL WHI WHS WTCCC conFIRM deCODE | N/A | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | BBJ FinnGen NCI | BBJ FinnGen NCI | AHS ASHRAM ATBC BioVU CPSII CeRePP DFHCC EPIC HPFS HUNT2 IARC Karolinska Leeds MCCS MDARCCS Moscow NCI NHS PHS PLCO SEARCH Tromso UKBS Umea VARI VITAL WHI WHS WTCCC conFIRM | Agent Input |
| publication.title | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Evaluating the Utility of Polygenic Risk Scores in Identifying High-Risk Individuals for Eight Common Cancers. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Multi-ancestry genome-wide association study of kidney cancer identifies 63 susceptibility regions. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Nat Genet | Nat Commun | JNCI Cancer Spectr | NPJ Precis Oncol | Nat Commun | Nat Genet | Nat Genet | Nat Commun | Agent Input |
| date_release | 2024-05-22 | 2021-05-28 | 2021-02-03 | 2023-12-15 | 2020-02-12 | 2024-05-22 | 2024-05-22 | 2020-02-12 | Agent Input |
| variants_number | 107 | 19 | 15 | 12 | 19 | 107 | 107 | 19 | Agent Input |
| covariates | Age, sex, PCs, BMI, smoking, hypertension | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Genotyping array | first 10 genetic principal components | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age, sex, PCs, BMI, smoking, hypertension | Age at assessment, sex, genotyping array, PCs(1-15), body mass index, smoking status (never vs. former vs. current), cigarette pack-years, ever diagnosed with hypertension | Agent Input |


### graves disease

Candidate pool: `7` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS005266 | PGS005265 | PGS005264 | PGS002023 | PGS001042 | PGS005265 | PGS005265 | PGS001042 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 2/7 | 2/7 | 5/7 | Benchmark Only |
| AoU benchmark AUC | 0.7677 | 0.7535 | 0.6667 | 0.6320 | 0.6290 | 0.7535 | 0.7535 | 0.6290 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Graves' disease | Graves' disease | Graves' disease | Thyrotoxicosis with or without goiter | Thyrotoxicosis [hyperthyroidism] (time-to-event) | Graves' disease | Graves' disease | Thyrotoxicosis [hyperthyroidism] (time-to-event) | Agent Input |
| trait_efo | Graves disease | Graves disease | Graves disease | Thyrotoxicosis | Thyrotoxicosis | Graves disease | Graves disease | Thyrotoxicosis | Agent Input |
| phenotyping_reported | graves' disease | graves' disease | graves' disease | Thyrotoxicosis with or without goiter | TTE thyrotoxicosis [hyperthyroidism] | graves' disease | graves' disease | TTE thyrotoxicosis [hyperthyroidism] | Agent Input |
| method_name | PRSCS | PRSCS | Pruning and Thresholding (P+T) | LDpred2 (bigsnpr) | snpnet | PRSCS | PRSCS | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM022749 | PPM022748 | PPM022747 | PPM011058 | PPM007972 | PPM022748 | PPM022748 | PPM007972 | Agent Input |
| performance_metrics.selected_validation_ancestry | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | European | African American or Afro-Caribbean, Hispanic or Latin American, European | African American or Afro-Caribbean, Hispanic or Latin American, European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 1 | 8 | 5 | 1 | 1 | 5 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | 0.6339 | N/A | N/A | 0.6339 | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | 0.0236 | N/A | N/A | 0.0236 | Agent Input |
| performance_metrics.full_model_auc | 0.6637 | 0.6652 | 0.6587 | N/A | 0.7130 | 0.6652 | 0.6652 | 0.7130 | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | 0.0591 | N/A | N/A | 0.0591 | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | 0.0467 | N/A | N/A | 0.0467 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.663730746326419} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.665220447565802} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.6587} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71296, 'ci_lower': 0.69708, 'ci_upper': 0.72884} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.665220447565802} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.665220447565802} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71296, 'ci_lower': 0.69708, 'ci_upper': 0.72884} | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0199, 'ci_lower': 0.0057, 'ci_upper': 0.034} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05914} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04673} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02359} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.63392, 'ci_lower': 0.61562, 'ci_upper': 0.65223} | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.05914} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04673} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.02359} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.63392, 'ci_lower': 0.61562, 'ci_upper': 0.65223} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.54332658848452} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.433940209108075} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.62508137678846} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.485557892551506} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.008} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.008} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.62508137678846} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.485557892551506} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.62508137678846} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.485557892551506} | N/A | Agent Input |
| validation_sample_size | n=94,651 | n=94,651 | n=94,651 | n=19,108 | n=67,425 | n=94,651 | n=94,651 | n=67,425 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=269,704 | N/A | N/A | n=269,704 | Agent Input |
| ancestry_distribution | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: NR (100%) / EVAL: MAE (100%) | GWAS: NR (100%) / EVAL: MAE (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | AllofUs BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | AllofUs BBJ BioMe BioVU FinnGen HUNT LATVIANBIOBANK MGBB MGI MVP NSGHI PMB UKB | UKB | Agent Input |
| publication.title | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Global multi-ancestry genetic study elucidates genes and biological pathways associated with thyroid cancer and benign thyroid diseases | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | medRxiv | medRxiv | medRxiv | Am J Hum Genet | PLoS Genet | medRxiv | medRxiv | PLoS Genet | Agent Input |
| date_release | 2026-01-19 | 2026-01-19 | 2026-01-19 | 2022-01-10 | 2021-10-21 | 2026-01-19 | 2026-01-19 | 2021-10-21 | Agent Input |
| variants_number | 1085170 | 1085173 | 112 | 279385 | 226 | 1085173 | 1085173 | 226 | Agent Input |
| covariates | Unknown | Unknown | Unknown | sex, age, birth date, deprivation index, 16 PCs | age, sex, UKB array type, Genotype PCs | Unknown | Unknown | age, sex, UKB array type, Genotype PCs | Agent Input |


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
| Selected PGS ID | PGS001278 | PGS001280 | PGS001277 | PGS001279 | PGS004530 | PGS001279 | PGS001280 | PGS001277 | Agent Input |
| AoU benchmark rank | 1/7 | 2/7 | 3/7 | 4/7 | 5/7 | 4/7 | 2/7 | 3/7 | Benchmark Only |
| AoU benchmark AUC | 0.5943 | 0.5916 | 0.5907 | 0.5885 | 0.5578 | 0.5885 | 0.5916 | 0.5907 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | Yes | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 4/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | previously: Blood clot in the leg (DVT) or lung | PE (time-to-event) | PE +/- DVT | previously: Blood clot in the lung | I26 (Pulmonary embolism) | previously: Blood clot in the lung | PE (time-to-event) | PE +/- DVT | Agent Input |
| trait_efo | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism, deep vein thrombosis | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism, deep vein thrombosis | pulmonary embolism | pulmonary embolism, deep vein thrombosis | Agent Input |
| phenotyping_reported | Blood clot in the leg (DVT) or lung | TTE PE | PE +/- DVT | Blood clot in the lung | I26 (Pulmonary embolism) | Blood clot in the lung | TTE PE | PE +/- DVT | Agent Input |
| method_name | snpnet | snpnet | snpnet | snpnet | RFDiseasemetaPRS | snpnet | snpnet | snpnet | Agent Input |
| performance_metrics.selected_performance_id | PPM008890 | PPM008900 | PPM008885 | PPM008897 | PPM020645 | PPM008897 | PPM008900 | PPM008885 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 5 | 5 | 5 | 5 | 1 | 5 | 5 | 5 | Agent Input |
| performance_metrics.auc | 0.5916 | 0.6077 | 0.6114 | 0.6003 | N/A | 0.6003 | 0.6077 | 0.6114 | Agent Input |
| performance_metrics.r2 | 0.0133 | 0.0140 | 0.0151 | 0.0115 | N/A | 0.0115 | 0.0140 | 0.0151 | Agent Input |
| performance_metrics.full_model_auc | 0.6535 | 0.6762 | 0.6750 | 0.6242 | N/A | 0.6242 | 0.6762 | 0.6750 | Agent Input |
| performance_metrics.full_model_r2 | 0.0337 | 0.0406 | 0.0400 | 0.0176 | N/A | 0.0176 | 0.0406 | 0.0400 | Agent Input |
| performance_metrics.incremental_auc | 0.0350 | 0.0293 | 0.0315 | 0.0446 | N/A | 0.0446 | 0.0293 | 0.0315 | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.65354, 'ci_lower': 0.63231, 'ci_upper': 0.67477} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67617, 'ci_lower': 0.64866, 'ci_upper': 0.70368} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67497, 'ci_lower': 0.64702, 'ci_upper': 0.70293} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62416, 'ci_lower': 0.60164, 'ci_upper': 0.64668} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.62416, 'ci_lower': 0.60164, 'ci_upper': 0.64668} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67617, 'ci_lower': 0.64866, 'ci_upper': 0.70368} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67497, 'ci_lower': 0.64702, 'ci_upper': 0.70293} | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03366} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03495} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01331} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.59164, 'ci_lower': 0.56886, 'ci_upper': 0.61442} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04057} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02926} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01403} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60765, 'ci_lower': 0.57812, 'ci_upper': 0.63719} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03998} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03149} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01508} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61144, 'ci_lower': 0.58149, 'ci_upper': 0.6414} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01763} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04457} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60034, 'ci_lower': 0.57683, 'ci_upper': 0.62385} | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.01763} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.04457} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01146} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60034, 'ci_lower': 0.57683, 'ci_upper': 0.62385} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.04057} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.02926} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01403} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.60765, 'ci_lower': 0.57812, 'ci_upper': 0.63719} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.03998} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.03149} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.01508} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.61144, 'ci_lower': 0.58149, 'ci_upper': 0.6414} | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.242446} | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=24,838 | n=24,905 | n=24,905 | n=67,349 | n=56,192 | n=67,349 | n=24,905 | n=24,905 | Agent Input |
| samples_training | n=269,382 | n=269,704 | n=269,704 | n=269,382 | n=174,489 | n=269,382 | n=269,704 | n=269,704 | Agent Input |
| ancestry_distribution | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | Agent Input |
| training_development_cohorts | UKB | UKB | UKB | UKB | UKB | UKB | UKB | UKB | Agent Input |
| publication.title | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Integration of risk factor polygenic risk score with disease polygenic risk score for disease prediction. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Agent Input |
| publication.journal | PLoS Genet | PLoS Genet | PLoS Genet | PLoS Genet | Commun Biol | PLoS Genet | PLoS Genet | PLoS Genet | Agent Input |
| date_release | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2021-10-21 | 2024-03-18 | 2021-10-21 | 2021-10-21 | 2021-10-21 | Agent Input |
| variants_number | 551 | 88 | 96 | 94 | 1059939 | 94 | 88 | 96 | Agent Input |
| covariates | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Unknown | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | age, sex, UKB array type, Genotype PCs | Agent Input |


### abdominal aortic aneurysm

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003973 | PGS003429 | PGS003972 | PGS001784 | PGS000753 | PGS003972 | PGS003973 | PGS000753 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 3/6 | 1/6 | 5/6 | Benchmark Only |
| AoU benchmark AUC | 0.6374 | 0.6341 | 0.6312 | 0.5618 | 0.5388 | 0.6312 | 0.6374 | 0.5388 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 8/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Agent Input |
| trait_efo | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Abdominal Aortic Aneurysm | Agent Input |
| phenotyping_reported | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Prevalent abdominal aortic aneurysm | Abdominal aortic aneurysm | Abdominal aortic aneurysm | Prevalent abdominal aortic aneurysm | Agent Input |
| method_name | PRS-CS | shaPRS + LDpred2 | PRS-CS | PRS-CS-auto | Pruning and Thresholding (P+T) | PRS-CS | PRS-CS | Pruning and Thresholding (P+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM019137 | PPM017103 | PPM019134 | PPM009288 | PPM001912 | PPM019134 | PPM019137 | PPM001912 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 1 | 3 | 1 | 7 | 3 | 1 | 7 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | 0.0147 | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.8820 | 0.7080 | 0.6900 | 0.8680 | N/A | 0.6900 | 0.8820 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.0055 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.882, 'ci_lower': 0.872, 'ci_upper': 0.892} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.708, 'ci_lower': 0.691, 'ci_upper': 0.725} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.868} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.69} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.882, 'ci_lower': 0.872, 'ci_upper': 0.892} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00547} | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.014661} | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | N/A | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37, 'ci_lower': 1.3, 'ci_upper': 1.44} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.37, 'ci_lower': 1.3, 'ci_upper': 1.44} | Agent Input |
| validation_sample_size | n=7,517 | n=91,731 | n=6,940 | n=350,767 | n=46,564 | n=6,940 | n=7,517 | n=46,564 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=8,772 | N/A | N/A | n=8,772 | Agent Input |
| ancestry_distribution | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: EUR (89%), MAE (11%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (60%), EAS (17%), EUR (82%), OTH (90%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (25%), EUR (75%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: AFR (8%), EUR (92%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: AFR (25%), EUR (75%) | Agent Input |
| training_development_cohorts | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | UKB | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS UKAGS UKB VIVA deCODE eMERGE | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI deCODE | MAYO-VDB MVP | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS UKAGS UKB VIVA deCODE eMERGE | ARIC CHB CHIP HUNT MAYO-VDB MGI MVP MyCode NZ PMB TABS deCODE eMERGE | MAYO-VDB MVP | Agent Input |
| publication.title | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Evaluating the cost-effectiveness of polygenic risk score-stratified screening for abdominal aortic aneurysm. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Genetic Architecture of Abdominal Aortic Aneurysm in the Million Veteran Program. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Genome-wide association meta-analysis identifies risk loci for abdominal aortic aneurysm and highlights PCSK9 as a therapeutic target. | Genetic Architecture of Abdominal Aortic Aneurysm in the Million Veteran Program. | Agent Input |
| publication.journal | Nat Genet | Nat Commun | Nat Genet | Cell Genom | Circulation | Nat Genet | Nat Genet | Circulation | Agent Input |
| date_release | 2023-11-01 | 2023-12-15 | 2023-11-01 | 2022-09-08 | 2021-04-07 | 2023-11-01 | 2023-11-01 | 2021-04-07 | Agent Input |
| variants_number | 1118997 | 831447 | 1118997 | 911440 | 29 | 1118997 | 1118997 | 29 | Agent Input |
| covariates | Age, Age^2, Sex | Unknown | Unknown | sex,age,age2,age*sex,age^2*sex, 20PCs | Age, sex, PCs (1-5) | Unknown | Age, Age^2, Sex | Age, sex, PCs (1-5) | Agent Input |


### age-related macular degeneration

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004606 | PGS002269 | PGS004952 | PGS001834 | PGS002041 | PGS004606 | PGS004606 | PGS001834 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 1/6 | 1/6 | 4/6 | Benchmark Only |
| AoU benchmark AUC | 0.6547 | 0.6530 | 0.6512 | 0.6133 | 0.6093 | 0.6547 | 0.6547 | 0.6133 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Age-related macular degeneration | Age-related macular degeneration | Age-related macular degeneration | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | Age-related macular degeneration | Age-related macular degeneration | Macular degeneration (senile) of retina NOS | Agent Input |
| trait_efo | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | age-related macular degeneration | Agent Input |
| phenotyping_reported | Age-related macular degeneration | Rentinal layer thickness (photoreceptor inner and outer segments) | Late age-related macular degeneration (Clinical Classification) | Macular degeneration (senile) of retina NOS | Macular degeneration (senile) of retina NOS | Age-related macular degeneration | Age-related macular degeneration | Macular degeneration (senile) of retina NOS | Agent Input |
| method_name | PRS-CS | Independent variants associated with AMD | Genome-wide significant SNPs | Penalized regression (bigstatsr) | LDpred2 (bigsnpr) | PRS-CS | PRS-CS | Penalized regression (bigstatsr) | Agent Input |
| performance_metrics.selected_performance_id | PPM020767 | PPM012920 | PPM021761 | PPM009564 | PPM011194 | PPM020767 | PPM020767 | PPM009564 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European, South Asian, Not reported | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 3 | 6 | 8 | 8 | 1 | 1 | 8 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7100 | N/A | 0.8420 | N/A | N/A | 0.7100 | 0.7100 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 84.2} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.71} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0175, 'ci_lower': 0.0034, 'ci_upper': 0.0315} | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0159, 'ci_lower': 0.0018, 'ci_upper': 0.0299} | N/A | N/A | {'name_long': 'Partial Correlation (partial-r)', 'name_short': 'Partial Correlation (partial-r)', 'estimate': 0.0175, 'ci_lower': 0.0034, 'ci_upper': 0.0315} | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | {'name_long': 'Beta', 'name_short': 'β', 'estimate': -0.21, 'ci_lower': -0.23, 'ci_upper': -0.19} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.41, 'ci_lower': 1.32, 'ci_upper': 1.5} | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.76, 'ci_lower': 1.73, 'ci_upper': 1.78} | N/A | Agent Input |
| validation_sample_size | n=163,011 | n=44,823 | n=1,232 | n=19,413 | n=19,413 | n=163,011 | n=163,011 | n=19,413 | Agent Input |
| samples_training | N/A | N/A | N/A | n=391,124 | n=391,124 | N/A | N/A | n=391,124 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: MAE (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (25%), EAS (12%), EUR (38%), GME (12%), SAS (12%) | Agent Input |
| training_development_cohorts | IAMDGC | AREDS BDES CWRU Columbia EUGENDA Edinburgh JHU MMAP Marshfield NHS RotES UCSD UWALF Vanderbilt | IAMDGC | UKB | UKB | IAMDGC | IAMDGC | UKB | Agent Input |
| publication.title | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Photoreceptor Layer Thinning Is an Early Biomarker for Age-Related Macular Degeneration: Epidemiologic and Genetic Evidence from UK Biobank OCT Data. | Genetic Risk Score Analysis Supports a Joint View of Two Classification Systems for Age-Related Macular Degeneration. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Genome-wide association analyses identify distinct genetic architectures for age-related macular degeneration across ancestries. | Portability of 245 polygenic scores when derived from the UK Biobank and applied to 9 ancestry groups from the same cohort | Agent Input |
| publication.journal | Nat Genet | Ophthalmology | Invest Ophthalmol Vis Sci | Am J Hum Genet | Am J Hum Genet | Nat Genet | Nat Genet | Am J Hum Genet | Agent Input |
| date_release | 2024-02-20 | 2022-04-01 | 2024-09-19 | 2022-01-10 | 2022-01-10 | 2024-02-20 | 2024-02-20 | 2022-01-10 | Agent Input |
| variants_number | 1000946 | 47 | 52 | 157 | 116538 | 1000946 | 1000946 | 157 | Agent Input |
| covariates | age, sex, principal components 1-10 | Age, age2 (to adjust for non-linear relationships with age), sex, smoking status, and the first ten principal components of genetic ancestry | Age, sex, survey membership, 10 PCs | sex, age, birth date, deprivation index, 16 PCs | sex, age, birth date, deprivation index, 16 PCs | age, sex, principal components 1-10 | age, sex, principal components 1-10 | sex, age, birth date, deprivation index, 16 PCs | Agent Input |


### cervical carcinoma

Candidate pool: `6` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS000073 | PGS000784 | PGS003389 | PGS005165 | PGS003428 | PGS003428 | PGS001299 | PGS000073 | Agent Input |
| AoU benchmark rank | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 5/6 | 6/6 | 1/6 | Benchmark Only |
| AoU benchmark AUC | 0.6925 | 0.6679 | 0.4759 | 0.4709 | 0.3846 | 0.3846 | 0.3401 | 0.6925 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | No | No | Yes | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | No | No | Yes | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | No | No | Yes | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | No | No | Yes | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | No | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 7/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Cervical cancer | Agent Input |
| trait_efo | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | cervical carcinoma | Agent Input |
| phenotyping_reported | Incident cervical cancer | Incident cervical cancer | cervical cancer | Cervical Cancer | Incident cervical cancer | Incident cervical cancer | Cervical cancer | Incident cervical cancer | Agent Input |
| method_name | Genome-wide significant variants | 10 variants from Graff et al (PGS000073) with inverse variant weights | lassosum | Known susceptibility loci (genome-wide significant SNPs) | LDpred | LDpred | snpnet | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM002039 | PPM002055 | PPM016264 | PPM022403 | PPM017102 | PPM017102 | PPM008994 | PPM002039 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | East Asian | European | European | European | European | Agent Input |
| performance_metrics.record_count | 2 | 1 | 1 | 1 | 1 | 1 | 5 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.5522 | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | 0.0026 | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7450 | 0.7450 | 0.5630 | 0.5660 | 0.6130 | 0.6130 | 0.7676 | 0.7450 | Agent Input |
| performance_metrics.full_model_r2 | N/A | 0.4370 | 0.0016 | N/A | N/A | N/A | 0.1128 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | 0.0068 | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75, 'se': 0.017} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.749, 'se': 0.017} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.563} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.566} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.613} | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.613} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.76761, 'ci_lower': 0.74661, 'ci_upper': 0.7886} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.745} {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.75, 'se': 0.017} | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.437} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.00158} | N/A | N/A | N/A | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.11284} {'name_long': 'Incremental AUROC (full-covars)', 'name_short': 'Incremental AUROC (full-covars)', 'estimate': 0.00676} {'name_long': 'PGS R2 (no covariates)', 'name_short': 'PGS R2 (no covariates)', 'estimate': 0.00263} {'name_long': 'PGS AUROC (no covariates)', 'name_short': 'PGS AUROC (no covariates)', 'estimate': 0.55215, 'ci_lower': 0.51478, 'ci_upper': 0.58952} | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.09, 'ci_upper': 1.37} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.21, 'ci_lower': 1.07, 'ci_upper': 1.35} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.2, 'ci_lower': 1.06, 'ci_upper': 1.36} {'name_long': 'Beta', 'name_short': 'β', 'estimate': 0.182} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.33, 'se': 0.069} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.33, 'se': 0.069} | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.22, 'ci_lower': 1.09, 'ci_upper': 1.37} | Agent Input |
| validation_sample_size | n=211,795 | n=211,795 | n=144,374 | n=57,359 | n=128,113 | n=128,113 | n=24,905 | n=211,795 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | n=4,295 | n=4,295 | n=269,704 | N/A | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EAS (100%) / EVAL: EAS (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | DEV: EUR (100%) / EVAL: AFR (20%), EAS (20%), EUR (40%), SAS (20%) | GWAS: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | TwinGene | NCI Seattle TwinGene Umea WTCCC | N/A | BBJ | EB FinnGen KP UKB | EB FinnGen KP UKB | UKB | TwinGene | Agent Input |
| publication.title | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Pan-cancer analysis demonstrates that integrating polygenic risk scores with modifiable risk factors improves risk prediction. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Polygenic risk scores for pan-cancer risk prediction in the Chinese population: A population-based cohort study based on the China Kadoorie Biobank. | GWAS meta-analyses clarify genetics of cervical phenotypes and inform risk stratification for cervical cancer. | GWAS meta-analyses clarify genetics of cervical phenotypes and inform risk stratification for cervical cancer. | Significant sparse polygenic risk scores across 813 traits in UK Biobank. | Cross-cancer evaluation of polygenic risk scores for 16 cancer types in two large cohorts. | Agent Input |
| publication.journal | Nat Commun | Nat Commun | Cancer Res | PLoS Med | Hum Mol Genet | Hum Mol Genet | PLoS Genet | Nat Commun | Agent Input |
| date_release | 2020-02-12 | 2021-05-28 | 2023-01-19 | 2025-03-17 | 2023-04-28 | 2023-04-28 | 2021-10-21 | 2020-02-12 | Agent Input |
| variants_number | 10 | 10 | 2814 | 15 | 2894555 | 2894555 | 24 | 10 | Agent Input |
| covariates | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | age, top 20 genetic principal components | Age,Sex (if applicable),Region,Top 10 genetic ancestry principal components | age, smoking | age, smoking | age, sex, UKB array type, Genotype PCs | Age at assessment, genotyping array, PCs(1-15), parity ( ≥1 live birth vs. none), oral contraceptive use (never used (0) vs. <20 years vs. ≥20 years), cigarette pack-years | Agent Input |


### cutaneous melanoma

Candidate pool: `5` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS003382 | PGS004247 | PGS000766 | PGS003745 | PGS000339 | PGS003382 | PGS003382 | PGS000339 | Agent Input |
| AoU benchmark rank | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | 1/5 | 1/5 | 5/5 | Benchmark Only |
| AoU benchmark AUC | 0.6239 | 0.5934 | 0.5886 | 0.5812 | 0.5663 | 0.6239 | 0.6239 | 0.5663 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 9/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Skin cutaneous melanoma | Melanoma | Cutaneous melanoma | Skin Melanoma | Cutaneous melanoma | Skin cutaneous melanoma | Skin cutaneous melanoma | Cutaneous melanoma | Agent Input |
| trait_efo | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | cutaneous melanoma | Agent Input |
| phenotyping_reported | skin cutaneous melanoma | Melanoma | Incident cutaneous melanoma | Skin Melanoma | Cutaneous melanoma in multiplex melanoma families | skin cutaneous melanoma | skin cutaneous melanoma | Cutaneous melanoma in multiplex melanoma families | Agent Input |
| method_name | Pruning and Thresholding (P+T) | PRSice-2 | Variants associated with melanoma | Genome-wide significant SNPs | Clumping and Thresholding (C+T) | Pruning and Thresholding (P+T) | Pruning and Thresholding (P+T) | Clumping and Thresholding (C+T) | Agent Input |
| performance_metrics.selected_performance_id | PPM016257 | PPM020304 | PPM001962 | PPM018501 | PPM000921 | PPM016257 | PPM016257 | PPM000921 | Agent Input |
| performance_metrics.selected_validation_ancestry | European | European | European | European | European | European | European | European | Agent Input |
| performance_metrics.record_count | 1 | 2 | 7 | 1 | 2 | 1 | 1 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.6820 | N/A | 0.6430 | N/A | N/A | 0.6820 | 0.6820 | N/A | Agent Input |
| performance_metrics.full_model_r2 | 0.0261 | N/A | N/A | N/A | N/A | 0.0261 | 0.0261 | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.682} | N/A | {'name_long': 'Concordance Statistic', 'name_short': 'C-index', 'estimate': 0.643, 'ci_lower': 0.584, 'ci_upper': 0.702} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.682} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.682} | N/A | Agent Input |
| performance_metrics.other_metrics | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0261} | N/A | N/A | N/A | {'name_long': 'Difference of PRS (deltaPRS; melanoma family cases vs. unrelated controls)', 'name_short': 'Difference of PRS (deltaPRS; melanoma family cases vs. unrelated controls)', 'estimate': 0.505, 'se': 0.036} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0261} | {'name_long': 'Proportion of the variance explained', 'name_short': 'R²', 'estimate': 0.0261} | {'name_long': 'Difference of PRS (deltaPRS; melanoma family cases vs. unrelated controls)', 'name_short': 'Difference of PRS (deltaPRS; melanoma family cases vs. unrelated controls)', 'estimate': 0.505, 'se': 0.036} | Agent Input |
| performance_metrics.effect_sizes | N/A | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.78, 'ci_lower': 1.62, 'ci_upper': 1.96} | {'name_long': 'Hazard Ratio', 'name_short': 'HR', 'estimate': 1.46, 'ci_lower': 1.2, 'ci_upper': 1.77} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.49, 'ci_lower': 1.34, 'ci_upper': 1.66} | N/A | N/A | N/A | N/A | Agent Input |
| validation_sample_size | n=273,786 | n=133,830 | n=12,712 | n=448 | n=3,066 | n=273,786 | n=273,786 | n=3,066 | Agent Input |
| samples_training | N/A | N/A | N/A | n=1,402 | n=3,666 | N/A | N/A | n=3,666 | Agent Input |
| ancestry_distribution | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / EVAL: EUR (100%) | GWAS: EUR (100%) / DEV: EUR (100%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | N/A | 23andMe AMFS CPSII DEMOKRITOS Essen-Heidelberg GenoMEL HPFS LMC MDACCS MELARISK MIA NHS PAH PLCO Q-MEGA SEARCH UKB WAMHS | UKB | BATS MIA PAH | N/A | N/A | BATS MIA PAH | Agent Input |
| publication.title | Common germline risk variants impact somatic alterations and clinical features across cancers. | Potential utility of risk stratification for multicancer screening with liquid biopsy tests. | Genomic Risk Score for Melanoma in a Prospective Study of Older Individuals. | Prognostic evaluation of polygenic risk score underlying pan-cancer analysis: evidence from two large-scale cohorts. | Multiplex melanoma families are enriched for polygenic risk. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Common germline risk variants impact somatic alterations and clinical features across cancers. | Multiplex melanoma families are enriched for polygenic risk. | Agent Input |
| publication.journal | Cancer Res | NPJ Precis Oncol | J Natl Cancer Inst | EBioMedicine | Hum Mol Genet | Cancer Res | Cancer Res | Hum Mol Genet | Agent Input |
| date_release | 2023-01-19 | 2023-12-15 | 2021-05-28 | 2023-06-01 | 2020-11-05 | 2023-01-19 | 2023-01-19 | 2020-11-05 | Agent Input |
| variants_number | 672 | 65 | 56 | 57 | 22 | 672 | 672 | 22 | Agent Input |
| covariates | age, sex, top 20 genetic principal components | first 10 genetic principal components | Sex, melanoma family history, treatment (aspirin/placebo), age at enrolment, PRS*treatment | Unknown | PCs (1-10) | age, sex, top 20 genetic principal components | age, sex, top 20 genetic principal components | PCs (1-10) | Agent Input |


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
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
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


### open-angle glaucoma

Candidate pool: `5` models. `Hit@1..5` are all defined; if `N Models < k`, `Top@k` expands to all available benchmark-ranked models.


| Field | Benchmark #1 | Benchmark #2 | Benchmark #3 | Benchmark #4 | Benchmark #5 | Catalog Search + Domain Knowledge | Catalog Search Only | Prompt-Only Baseline | Field Type |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Selected PGS ID | PGS004944 | PGS001797 | PGS002741 | PGS000764 | PGS000350 | PGS004944 | PGS004944 | PGS000350 | Agent Input |
| AoU benchmark rank | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | 1/5 | 1/5 | 5/5 | Benchmark Only |
| AoU benchmark AUC | 0.6405 | 0.6264 | 0.6173 | 0.5749 | 0.5668 | 0.6405 | 0.6405 | 0.5668 | Benchmark Only |
| Hit@1 | Yes | No | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@2 | Yes | Yes | No | No | No | Yes | Yes | No | Benchmark Only |
| Hit@3 | Yes | Yes | Yes | No | No | Yes | Yes | No | Benchmark Only |
| Hit@4 | Yes | Yes | Yes | Yes | No | Yes | Yes | No | Benchmark Only |
| Hit@5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Benchmark Only |
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | Benchmark rank #5 | 6/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
| trait_reported | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary-open angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma | Agent Input |
| trait_efo | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | open-angle glaucoma | Agent Input |
| phenotyping_reported | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma | Primary open-angle glaucoma | Primary-open angle glaucoma | Primary open-angle glaucoma | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma (self-reported) | Primary open-angle glaucoma | Agent Input |
| method_name | Lassosum | PRS-CS-auto | Genome-wide significant SNPs | SNPs associated with primary-open angle glaucoma were selected from the GWAS Catalog | Genome-wide significant variants | Lassosum | Lassosum | Genome-wide significant variants | Agent Input |
| performance_metrics.selected_performance_id | PPM021744 | PPM009313 | PPM014900 | PPM001956 | PPM000997 | PPM021744 | PPM021744 | PPM000997 | Agent Input |
| performance_metrics.selected_validation_ancestry | African unspecified, Hispanic or Latin American, East Asian, South Asian, European | European | European | African American or Afro-Caribbean, African unspecified | European | African unspecified, Hispanic or Latin American, East Asian, South Asian, European | African unspecified, Hispanic or Latin American, East Asian, South Asian, European | European | Agent Input |
| performance_metrics.record_count | 8 | 1 | 5 | 2 | 2 | 8 | 8 | 2 | Agent Input |
| performance_metrics.auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.r2 | N/A | 0.0315 | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.full_model_auc | 0.7480 | 0.7490 | 0.6700 | N/A | N/A | 0.7480 | 0.7480 | N/A | Agent Input |
| performance_metrics.full_model_r2 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.incremental_auc | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.classification_metrics | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.748} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.749} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.67, 'ci_lower': 0.66, 'ci_upper': 0.68} | N/A | N/A | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.748} | {'name_long': 'Area Under the Receiver-Operating Characteristic Curve', 'name_short': 'AUROC', 'estimate': 0.748} | N/A | Agent Input |
| performance_metrics.other_metrics | N/A | {'name_long': "Nagelkerke's R2 (covariates regressed out)", 'name_short': "Nagelkerke's R2 (covariates regressed out)", 'estimate': 0.031479} | N/A | {'name_long': 'Odds Ratio (OR per 1 point increase)', 'name_short': 'Odds Ratio (OR per 1 point increase)', 'estimate': 1.08, 'ci_lower': 1.06, 'ci_upper': 1.11} | N/A | N/A | N/A | N/A | Agent Input |
| performance_metrics.effect_sizes | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.74, 'ci_lower': 1.71, 'ci_upper': 1.77} | N/A | N/A | N/A | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.24, 'ci_lower': 1.21, 'ci_upper': 1.27} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.74, 'ci_lower': 1.71, 'ci_upper': 1.77} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.74, 'ci_lower': 1.71, 'ci_upper': 1.77} | {'name_long': 'Odds Ratio', 'name_short': 'OR', 'estimate': 1.24, 'ci_lower': 1.21, 'ci_upper': 1.27} | Agent Input |
| validation_sample_size | n=407,667 | n=7,128 | n=3,382 | n=3,830 | n=6,538 | n=407,667 | n=407,667 | n=6,538 | Agent Input |
| samples_training | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Agent Input |
| ancestry_distribution | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: AFR (2%), ASN (60%), EAS (18%), EUR (79%), OTH (60%) / EVAL: EUR (100%) | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: AFR (50%), EUR (50%) | GWAS: MAE (100%) / EVAL: MAO (100%) | GWAS: EUR (94%), MAO (6%) / EVAL: EUR (100%) | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: AFR (2%), EAS (12%), EUR (86%) / EVAL: MAE (100%) | GWAS: EUR (94%), MAO (6%) / EVAL: EUR (100%) | Agent Input |
| training_development_cohorts | N/A | BBJ BioMe BioVU CCPM EB FinnGen HUNT MGBB MGI TWB UCLA UKB | N/A | N/A | ALIENOR ANZRAG BATS BES BMES ERF FES GEP GHS GIST HPFS Iowa MEEI Marshfield NEIGHBOR NHS OHTS ORCADES QIMR REHS RES RS SCES SIMES SINDI TEST TwinsUK WGHS deCODE | N/A | N/A | ALIENOR ANZRAG BATS BES BMES ERF FES GEP GHS GIST HPFS Iowa MEEI Marshfield NEIGHBOR NHS OHTS ORCADES QIMR REHS RES RS SCES SIMES SINDI TEST TwinsUK WGHS deCODE | Agent Input |
| publication.title | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Global Biobank analyses provide lessons for developing polygenic risk scores across diverse cohorts. | Glaucoma genetic risk scores in the Million Veteran Program. | The Role of Genetic Ancestry as a Risk Factor for Primary Open-angle Glaucoma in African Americans. | Association of a Primary Open-Angle Glaucoma Genetic Risk Score With Earlier Age at Diagnosis. | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Deep Ocular Phenotyping Across Primary Open-Angle Glaucoma Genetic Burden. | Association of a Primary Open-Angle Glaucoma Genetic Risk Score With Earlier Age at Diagnosis. | Agent Input |
| publication.journal | JAMA Ophthalmol | Cell Genom | Ophthalmology | Invest Ophthalmol Vis Sci | JAMA Ophthalmol | JAMA Ophthalmol | JAMA Ophthalmol | JAMA Ophthalmol | Agent Input |
| date_release | 2024-08-29 | 2022-09-08 | 2022-08-03 | 2021-04-28 | 2020-12-08 | 2024-08-29 | 2024-08-29 | 2020-12-08 | Agent Input |
| variants_number | 144019 | 885417 | 127 | 23 | 12 | 144019 | 144019 | 12 | Agent Input |
| covariates | Age, age2, sex, ancestry | sex,age, 20PCs | Age, sex, and 10 sample-specific PCs | Age, ancestry (q0), gender | sex, DNA source, population structure | Age, age2, sex, ancestry | Age, age2, sex, ancestry | sex, DNA source, population structure | Agent Input |


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
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | Benchmark rank #4 | 10/10 trials | 8/10 trials | 10/10 trials | Benchmark Only |
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
| Selection frequency | Benchmark rank #1 | Benchmark rank #2 | Benchmark rank #3 | 10/10 trials | 10/10 trials | 10/10 trials | Benchmark Only |
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

