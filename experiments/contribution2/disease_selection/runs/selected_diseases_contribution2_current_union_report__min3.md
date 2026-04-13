# Current-Method Canonical Union

- Base eligibility: `min_n_models = 3`
- QC1 gate: `disabled (QC1 retained as diagnostic column only)`
- Raw current-method ontology union size (before canonical merge): `88`
- Canonical merged union size: `81`
- Output CSV can be used directly by `recommendation/configs/generate_evaluated_pgs_list.py`; manual `Target_TopK` annotation is no longer required.

## Canonical Merge Rule

- Before canonical grouping, resolve designated parent/child or near-synonym overlap groups by model coverage, then suppress a small set of over-broad umbrella labels.
- Prefer the manually specified canonical ontology label for each merge group.
- If multiple rows share the canonical label, prefer larger `N With AUC`.
- If still tied, prefer larger `Max`.
- Final deterministic fallback: higher `Mean`, then `childrencode` over `rootcode`.

## Collapsed Groups

Groups collapsed: `6`

| Canonical Ontology | Representative Ontology | Lookup Source | Source Coverage | Merged Ontologies | N With AUC | Max |
|--------------------|-------------------------|---------------|-----------------|-------------------|------------|-----|
| glaucoma | glaucoma | childrencode | both | glaucoma; open-angle glaucoma | 15 | 0.6258 |
| hyperthyroidism | hyperthyroidism | rootcode | both | graves disease; hyperthyroidism | 7 | 0.6211 |
| kidney cancer | kidney cancer | rootcode | both | kidney cancer; renal carcinoma | 10 | 0.5841 |
| melanoma | melanoma | childrencode | both | cutaneous melanoma; melanoma | 103 | 0.6239 |
| prostate cancer | prostate cancer | childrencode | both | prostate cancer; prostate carcinoma | 95 | 0.655 |
| sleep apnea | sleep apnea | childrencode | childrencode | obstructive sleep apnea; sleep apnea | 20 | 0.5784 |