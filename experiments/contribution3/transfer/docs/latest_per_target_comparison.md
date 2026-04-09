# Contribution3 Transfer: Per-Target Hit Report

## Scope

This report is a target-by-target detailed hit report for the current transfer evaluation.

- Generated at: `2026-04-07 17:01 EDT`
- It only focuses on `Top 5/10/15/20/25% Hit`.
- `Best Hit Tier` means the smallest percentile threshold hit by the selected model.
- `Better Hit Tier` compares only the hit-tier profile, not AUC/GPR or any other metric.

## `binary_to_binary`

- Targets: `23`; `all-tools better=3`, `gpt-only better=3`, `tie=17`.
- `gpt-only` hit counts: `Top 5% = 11/23`, `Top 10% = 16/23`, `Top 15% = 16/23`, `Top 20% = 17/23`, `Top 25% = 18/23`
- `all-tools` hit counts: `Top 5% = 12/23`, `Top 10% = 15/23`, `Top 15% = 15/23`, `Top 20% = 18/23`, `Top 25% = 19/23`

| Target ID | Target | gpt-only Transfer -> Model | gpt-only Best Hit Tier | gpt-only Top 5% | Top 10% | Top 15% | Top 20% | Top 25% | all-tools Transfer -> Model | all-tools Best Hit Tier | all-tools Top 5% | Top 10% | Top 15% | Top 20% | Top 25% | Better Hit Tier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `D03` | Melanoma in situ | skin carcinoma in situ -> PGS000471 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | skin carcinoma in situ -> PGS000471 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `D04` | Carcinoma in situ of skin of other parts of face | non-melanoma skin carcinoma -> PGS001040 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | non-melanoma skin carcinoma -> PGS001040 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `D05` | Intraductal carcinoma in situ of left breast | luminal A breast carcinoma -> PGS000212 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | HER2 negative breast carcinoma -> PGS000213 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `D24` | Benign neoplasm of breast | breast carcinoma -> PGS000015 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | breast carcinoma -> PGS000015 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `E01` | Iodine-deficiency related thyroid disorders and allied cond Iodine-deficiency related thyroid disorders and allied conditions | hypothyroidism -> PGS000965 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | hypothyroidism -> PGS001816 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `E08` | Diabetes due to underlying condition w/o complications Diabetes mellitus due to underlying condition without complications | metabolic syndrome -> PGS004928 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | type 1 diabetes mellitus -> PGS000024 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `gpt-only` |
| `E11` | Type 2 diabetes mellitus | metabolic syndrome -> PGS004928 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | gestational diabetes -> PGS002256 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `gpt-only` |
| `E79` | Hyperuricemia w/o signs of inflam arthrit and tophaceous dis Hyperuricemia without signs of inflammatory arthritis and tophaceous disease | gout -> PGS001789 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | gout -> PGS001789 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `F22` | Delusional disorders | major depressive disorder -> PGS003333 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | major depressive disorder -> PGS003333 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `F31` | Bipolar disorder | schizophrenia -> PGS000136 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | schizophrenia -> PGS000135 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `F60` | Borderline personality disorder | major depressive disorder -> PGS003333 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | major depressive disorder -> PGS003333 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `F90` | Attention-deficit hyperactivity disorder | major depressive disorder -> PGS003333 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | major depressive disorder -> PGS003333 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `J33` | Polyp of nasal cavity | asthma -> PGS001787 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | asthma -> PGS001787 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `J43` | Emphysema | FEV/FVC ratio -> PGS002643 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | asthma -> PGS001787 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | `all-tools` |
| `K70` | Alcoholic cirrhosis of liver without ascites | non-alcoholic fatty liver disease -> PGS000655 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | non-alcoholic fatty liver disease -> PGS000655 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `tie` |
| `M05` | Rheumatoid arthritis | psoriatic arthritis -> PGS001287 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | hypothyroidism -> PGS001816 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `all-tools` |
| `M1A` | Chronic gout | chronic kidney disease -> PGS002237 | `Top 20%` | `No` | `No` | `No` | `Yes` | `Yes` | chronic kidney disease -> PGS002237 | `Top 20%` | `No` | `No` | `No` | `Yes` | `Yes` | `tie` |
| `N40` | Benign prostatic hyperplasia without lower urinry tract symp Benign prostatic hyperplasia without lower urinary tract symptoms | prostate carcinoma -> PGS000333 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | prostate carcinoma -> PGS000333 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `tie` |
| `N52` | Male erectile dysfunction | type 2 diabetes mellitus -> PGS000014 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | type 1 diabetes mellitus -> PGS000024 | `Top 20%` | `No` | `No` | `No` | `Yes` | `Yes` | `all-tools` |
| `N65` | Disproportion of reconstructed breast | breast carcinoma -> PGS000015 | `Top 25%` | `No` | `No` | `No` | `No` | `Yes` | breast carcinoma -> PGS000015 | `Top 25%` | `No` | `No` | `No` | `No` | `Yes` | `tie` |
| `N91` | Absent, scanty and rare menstruation | hypothyroidism -> PGS000965 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | hypothyroidism -> PGS001816 | `Top 20%` | `No` | `No` | `No` | `Yes` | `Yes` | `gpt-only` |
| `Q23` | Congenital insufficiency of aortic valve | atrial fibrillation -> PGS000016 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | atrial fibrillation -> PGS000016 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `S52` | Unspecified fracture of the lower end of left radius | upper extremity fracture -> PGS001026 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | bone fracture -> PGS002137 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |

## `binary_to_continuous`

- Targets: `29`; `all-tools better=6`, `gpt-only better=5`, `tie=18`.
- `gpt-only` hit counts: `Top 5% = 9/29`, `Top 10% = 14/29`, `Top 15% = 16/29`, `Top 20% = 16/29`, `Top 25% = 16/29`
- `all-tools` hit counts: `Top 5% = 9/29`, `Top 10% = 11/29`, `Top 15% = 15/29`, `Top 20% = 16/29`, `Top 25% = 16/29`

| Target ID | Target | gpt-only Transfer -> Model | gpt-only Best Hit Tier | gpt-only Top 5% | Top 10% | Top 15% | Top 20% | Top 25% | all-tools Transfer -> Model | all-tools Best Hit Tier | all-tools Top 5% | Top 10% | Top 15% | Top 20% | Top 25% | Better Hit Tier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `B20` | Human immunodeficiency virus [HIV] disease | rheumatoid arthritis -> PGS001310 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | chronic kidney disease -> PGS002237 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `tie` |
| `C54` | Malignant neoplasm of endometrium | breast carcinoma -> PGS000015 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | ovarian carcinoma -> PGS002250 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `tie` |
| `C56` | Malignant neoplasm of unspecified ovary | breast carcinoma -> PGS000015 | `Top 15%` | `No` | `No` | `Yes` | `Yes` | `Yes` | breast carcinoma -> PGS000015 | `Top 15%` | `No` | `No` | `Yes` | `Yes` | `Yes` | `tie` |
| `D25` | Leiomyoma of uterus | uterine benign neoplasm -> PGS002021 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | uterine benign neoplasm -> PGS002021 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `D47` | Monoclonal gammopathy | rheumatoid arthritis -> PGS001310 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | lung carcinoma -> PGS000740 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `tie` |
| `E08` | Diabetes due to underlying condition w/o complications Diabetes mellitus due to underlying condition without complications | metabolic syndrome -> PGS004928 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | type 1 diabetes mellitus -> PGS000024 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `gpt-only` |
| `E10` | Type 1 diabetes mellitus | gestational diabetes -> PGS002256 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | gestational diabetes -> PGS002256 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `tie` |
| `E11` | Type 2 diabetes mellitus | metabolic syndrome -> PGS004928 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | gestational diabetes -> PGS002256 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `gpt-only` |
| `F11` | Opioid dependence, uncomplicated | nicotine dependence -> PGS002037 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | nicotine dependence -> PGS002037 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `F50` | Eating disorders | major depressive disorder -> PGS003333 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | joint disease -> PGS004550 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | `gpt-only` |
| `G30` | Alzheimer's disease | stroke -> PGS002724 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | eye measurement -> PGS001363 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `tie` |
| `I11` | Hypertensive heart disease with heart failure | congestive heart failure -> PGS005077 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | congestive heart failure -> PGS005077 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `I15` | Hypertension secondary to endocrine disorders | essential hypertension -> PGS000957 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | essential hypertension -> PGS004526 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `all-tools` |
| `I16` | Hypertensive urgency | hypertension -> PGS001320 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | hypertension -> PGS001320 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `I27` | Cor pulmonale (chronic) | chronic obstructive pulmonary disease -> PGS001788 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | chronic obstructive pulmonary disease -> PGS001788 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `J33` | Polyp of nasal cavity | asthma -> PGS001787 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | asthma -> PGS001787 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `J41` | Simple chronic bronchitis | FEV/FVC ratio -> PGS002643 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | emphysema -> PGS001326 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `all-tools` |
| `J96` | Acute respiratory failure with hypoxia | respiratory tract infectious disorder -> PGS000925 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | heart failure -> PGS005097 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `all-tools` |
| `K02` | Dental caries | type 2 diabetes mellitus -> PGS000330 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | type 2 diabetes mellitus -> PGS000014 | `Top 15%` | `No` | `No` | `Yes` | `Yes` | `Yes` | `gpt-only` |
| `K42` | Umbilical hernia | Inguinal hernia -> PGS000948 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | chronic kidney disease -> PGS002237 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `all-tools` |
| `K43` | Ventral hernia | Inguinal hernia -> PGS000948 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | Umbilical hernia -> PGS004542 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `tie` |
| `K65` | Peritoneal abscess | inflammatory bowel disease -> PGS004051 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | inflammatory bowel disease -> PGS004067 [model_not_in_full_matrix] | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `tie` |
| `K74` | Fibrosis and cirrhosis of liver | alcoholic liver cirrhosis -> PGS000704 | `Top 10%` | `No` | `Yes` | `Yes` | `Yes` | `Yes` | alcoholic liver cirrhosis -> PGS004913 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `all-tools` |
| `K80` | Cholelithiasis | metabolic syndrome -> PGS004928 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | diabetes mellitus -> PGS001327 | `Top 20%` | `No` | `No` | `No` | `Yes` | `Yes` | `gpt-only` |
| `K81` | Cholecystitis | body mass index -> PGS000027 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | body mass index -> PGS000027 | `Top 5%` | `Yes` | `Yes` | `Yes` | `Yes` | `Yes` | `tie` |
| `L02` | Cutaneous abscess, furuncle and carbuncle | type 2 diabetes mellitus -> PGS000014 | `Top 15%` | `No` | `No` | `Yes` | `Yes` | `Yes` | type 2 diabetes mellitus -> PGS000014 | `Top 15%` | `No` | `No` | `Yes` | `Yes` | `Yes` | `tie` |
| `L03` | Cellulitis | psoriasis -> PGS001312 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | type 2 diabetes mellitus -> PGS000014 | `Top 15%` | `No` | `No` | `Yes` | `Yes` | `Yes` | `all-tools` |
| `N04` | Nephrotic syndrome with unspecified morphologic changes | chronic kidney disease -> PGS002237 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | chronic kidney disease -> PGS002237 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `tie` |
| `N26` | Atrophy of kidney (terminal) | chronic kidney disease -> PGS002237 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | chronic kidney disease -> PGS002237 | `>Top 25%` | `No` | `No` | `No` | `No` | `No` | `tie` |
