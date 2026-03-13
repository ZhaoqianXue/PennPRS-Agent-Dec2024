# Current-Method Canonical Union

- Base eligibility: `min_n_models = 2`
- Raw current-method ontology union size (before canonical merge): `70`
- Canonical merged union size: `60`
- Output CSV can be used directly by `recommendation/configs/generate_evaluated_pgs_list.py`; manual `Target_TopK` annotation is no longer required.

## Canonical Merge Rule

- Prefer the manually specified canonical ontology label for each merge group.
- If multiple rows share the canonical label, prefer larger `N With AUC`.
- If still tied, prefer larger `Max`.
- Final deterministic fallback: higher `Mean`, then `childrencode` over `rootcode`.

## Collapsed Groups

Groups collapsed: `10`

| Canonical Ontology | Representative Ontology | Lookup Source | Source Coverage | Merged Ontologies | N With AUC | Max |
|--------------------|-------------------------|---------------|-----------------|-------------------|------------|-----|
| glaucoma | glaucoma | childrencode | both | glaucoma; open-angle glaucoma | 15 | 0.6258 |
| hyperthyroidism | hyperthyroidism | rootcode | both | graves disease; hyperthyroidism | 7 | 0.6211 |
| kidney cancer | kidney cancer | rootcode | both | kidney cancer; renal carcinoma | 10 | 0.5841 |
| melanoma | melanoma | childrencode | both | cutaneous melanoma; melanoma | 103 | 0.6239 |
| myocardial infarction | myocardial infarction | childrencode | both | acute myocardial infarction; myocardial infarction | 35 | 0.6044 |
| nodular goiter | nodular goiter | childrencode | both | multinodular goiter; nodular goiter | 7 | 0.7033 |
| ovarian carcinoma | ovarian carcinoma | childrencode | both | ovarian carcinoma; ovarian serous carcinoma | 21 | 0.6536 |
| peripheral vascular disease | peripheral vascular disease | childrencode | both | peripheral arterial disease; peripheral vascular disease | 4 | 0.5862 |
| prostate cancer | prostate cancer | childrencode | both | prostate cancer; prostate carcinoma | 95 | 0.655 |
| sleep apnea | sleep apnea | childrencode | childrencode | obstructive sleep apnea; sleep apnea | 20 | 0.5784 |