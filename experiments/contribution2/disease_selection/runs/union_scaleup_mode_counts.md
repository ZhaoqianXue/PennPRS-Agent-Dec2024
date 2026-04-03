# Union Disease Counts Under Three Selection Modes

## Scope

This note compares the final `raw ontology-level union` size under three modes while preserving the same base eligibility used by `select_diseases_contribution2.py`:

- `include_in_analysis == 1` from Contribution1 metadata
- at least `N` candidate PGS models, where `N` depends on the configuration
- enough evaluated AUC values to compute per-ontology metrics

So `no filtering` below means `no QC1 / no QC2 / no QC3`, not `include every raw ontology in Contribution1`.
These counts are computed **before** any later canonical merge-map step that collapses duplicate or parent/child ontology labels.

## Results

| Base eligibility | No QC filtering union | QC3-only union | Current-method union |
|------------------|----------------------|----------------|----------------------|
| `min_n_models = 2` (new default) | **137** | **92** | **85** |
| `min_n_models = 3` (legacy base eligibility) | **108** | **79** | **75** |

The current on-disk benchmark file [selected_diseases_contribution2_union__30disease.csv](/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution2/disease_selection/runs/selected_diseases_contribution2_union__30disease.csv) is a frozen manual 30-disease benchmark created under older selection settings and is not auto-synced to the current code.
The canonicalized current-method union produced by [build_current_method_union.py](/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution2/disease_selection/configs/build_current_method_union.py) further collapses these raw counts to `76` (default) and `68` (`min_n_models = 3`).

## Mode Definitions

### 1. No QC filtering

- No `QC1`
- No `QC2`
- No blacklist
- No `QC3`
- Keep the same structural post-processing as current pipeline:
  - rootcode dedup by `icd_root`
  - childrencode keeps all rows
  - final union is the ontology-level union of rootcode and childrencode outputs

### 2. QC3 only

- Apply only `QC3`: `mean_auc >= 0.5` and `top1_auc >= 0.55`
- No `QC1`
- No `QC2`
- No blacklist
- Keep the same rootcode/childrencode post-processing and ontology-level union rule

QC3-only union model-count breakdown under the legacy `min_n_models = 3` base eligibility (`100` diseases):

| Condition on `N Models` | Disease count |
|-------------------------|---------------|
| `> 1` | `100` |
| `> 2` | `100` |
| `> 3` | `88` |

Note: this is expected because the pipeline's base eligibility already requires at least `3` candidate PGS models before any QC mode is applied. So there are `12` QC3-only union diseases with exactly `3` models.

### 3. Current method

- Pool = `QC2 OR QC1`
- Apply hard blacklist
- Apply `QC3`
- Rootcode dedup by `icd_root`
- Final output keeps both `QC1` rows and `QC2` exception-allowlisted rows
- `QC1` uses `Top-1..Top-5 vs Rest`
- `QC2` is an exception allowlist with exact curated ontology-name matches; non-match is neutral
- The frozen 30-disease manual union file is still maintained separately and must be rebuilt manually if you want the benchmark to follow the current code.

## Takeaway

- With the new default `min_n_models = 2`, the three raw union sizes become `137 / 92 / 85`.
- With legacy `min_n_models = 3`, the three raw union sizes become `108 / 79 / 75`.
- After canonical merge-map collapsing, the current-method union becomes `76` (default) and `68` (`min_n_models = 3`).
- The existing 30-disease union benchmark remains a frozen historical artifact rather than the output of the current code.
