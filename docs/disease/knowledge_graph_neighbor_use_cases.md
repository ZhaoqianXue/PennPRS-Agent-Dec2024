# Knowledge Graph Neighbor Use Cases (Manual Screen)

- Updated: 2026-02-03
- Data sources (per SOP): `data/heritability/gwas_atlas/gwas_atlas.tsv` and `data/genetic_correlation/gwas_atlas/gwas_atlas_gc.tsv`
- Neighbor query implementation: `KnowledgeGraphService.get_prioritized_neighbors_v2()`
- Filters: `|rg_z_meta| > 2.0` and `h2_z_meta > 2.0`

## Purpose

Identify disease traits that reliably return **non-empty** neighbor lists from the local Genetic Architecture Knowledge Graph, so they can be used as stable demos/use cases for cross-trait recommendations.

## Cross-Disease Transfer Use Cases (Confirmed PGS Hit)

The following use cases are **confirmed** to satisfy BOTH:

- **Knowledge Graph neighbors exist** (`get_prioritized_neighbors_v2(resolved_target)` returns `neighbors_total > 0`)
- **PGS Catalog PRS hit exists** for at least one neighbor when scanning neighbors by **transfer_score (desc)**:
  - We scan neighbors in rank order until the **first** neighbor yields `associated_pgs_ids > 0` under PGS `/trait/search` (IDs-only precheck).
  - This matches the current Top-1 early-stop strategy in the Disease recommendation flow.

### Confirmed Use Cases (Target → first neighbor with PGS hit)

| Target (input) | KG resolved target | KG neighbors (total) | Neighbor (top1-hit) | Neighbor domain | Rank (hit/total) | transfer_score | rg_meta | PGS IDs (approx) |
|---|---|---:|---|---|---:|---:|---:|---:|
| `Type 2 diabetes` | `Type 2 Diabetes` | 872 | `Diabetes` | Endocrine | 1 / 872 | 0.027 | 0.815 | 313 |
| `Hypertension` | `Hypertension` | 597 | `High blood pressure` | Cardiovascular | 2 / 597 | 0.111 | 0.985 | 74 |
| `Atrial fibrillation` | `Atrial Fibrillation` | 322 | `Atrial fibrillation` | Cardiovascular | 3 / 322 | 0.024 | 1.082 | 61 |
| `Coronary artery disease` | `Coronary artery disease` | 492 | `Angina` | Cardiovascular | 10 / 492 | 0.003 | 0.334 | 19 |
| `Bipolar disorder` | `Bipolar disorder` | 494 | `Schizophrenia` | Psychiatric | 2 / 494 | 0.204 | 0.708 | 5 |
| `Major depressive disorder` | `Major depressive disorder` | 615 | `Schizophrenia` | Psychiatric | 2 / 615 | 0.053 | 0.360 | 5 |
| `Autism spectrum disorder` | `Autism spectrum disorder` | 418 | `Schizophrenia` | Psychiatric | 10 / 418 | 0.016 | 0.198 | 5 |
| `Schizophrenia` | `Schizophrenia` | 760 | `Bipolar disorder` | Psychiatric | 4 / 760 | 0.109 | 0.708 | 3 |
| `Alzheimer's disease` | `Alzheimer disease` | 373 | `Cholesterol` | Metabolic | 28 / 373 | 0.011 | 0.264 | 294 |

### Confirmed Non-Use-Cases (No PGS-hit neighbor found after scanning all KG neighbors)

These targets had **KG neighbors** but **no neighbor** produced any `associated_pgs_ids` via PGS `/trait/search` after scanning the entire neighbor list:

- `Breast cancer`
- `Prostate cancer`
- `Parkinson's disease`

## Important Notes (Trait ID Hygiene)

- **Use canonical KG trait IDs**: the v2 neighbor API expects a `trait_id` that matches a heritability canonical name (`uniqTrait`).
- **Exact/alias matching only**: free-form strings that do not appear as an alias in the heritability table will resolve to no node and return `neighbors=0`.
- **Example**:
  - Works: `Alzheimer disease`
  - Does not work: `Alzheimer's disease` (apostrophe variant)

## Recommended Use Cases (Neighbors > 0)

The following traits were manually verified to return `neighbors > 0` under the default v2 filters.

### Mental / Psychiatric

| Trait ID (copy-paste) | Neighbors (count) | Notes |
|---|---:|---|
| `Schizophrenia` | 760 | Strong connectivity; stable for cross-trait demo. |
| `Attention deficit hyperactivity disorder` | 734 | High neighbor count; good for showing diverse related traits. |
| `Major depressive disorder` | 615 | Reliable neighbor set; broad relevance. |
| `Depression` | 578 | Broad phenotype; many correlated traits. |
| `Bipolar disorder` | 494 | Strong overlap with schizophrenia-related traits. |
| `Autism spectrum disorder` | 418 | Reliable neighbors; good for neurodevelopmental demo. |

### Cardiovascular / Heart

| Trait ID (copy-paste) | Neighbors (count) | Notes |
|---|---:|---|
| `Hypertension` | 597 | Robust; showcases drug/biomarker correlations. |
| `Coronary artery disease` | 492 | Strong lipid-related neighbors; clinically intuitive. |
| `Atrial fibrillation` | 423 | Solid connectivity; good for arrhythmia-focused story. |

### Neurological / Neurodegenerative

| Trait ID (copy-paste) | Neighbors (count) | Notes |
|---|---:|---|
| `Alzheimer disease` | 373 | Works with exact spelling; demonstrates neurodegenerative network. |
| `Epilepsy` | 475 | High connectivity among neurological traits. |
| `Parkinson Disease` | 64 | Smaller neighbor set but still non-empty and interpretable. |

### Cancer (Registry/ICD10-style phenotypes)

These are **not** the same as the simple strings used in Fig. 3 cancer queries (e.g., `Breast cancer`). They are registry/ICD10-style phenotypes that exist in the current heritability table and have non-empty neighbors.

| Trait ID (copy-paste) | Neighbors (count) | Notes |
|---|---:|---|
| `Other and unspecified malignant neoplasm of skin` | 420 | Strong neighbor linkage with skin cancer phenotypes. |
| `Basal cell carcinoma` | 233 | Consistent neighbors; easy story. |
| `Malignant neoplasm of breast` | 73 | Neighbors exist; differs from `Breast cancer` string. |

## Known Non-Use-Cases (Neighbors = 0 under current data)

These were checked and returned `neighbors=0` in the current local KG v2 data:

- `Breast cancer`
- `Prostate cancer`
- `Colorectal cancer`
- `Pancreatic cancer` / `Pancreatic Cancer`
- `Melanoma`
- `Alzheimer's disease`

For the Fig. 3 cancer traits specifically, the limiting factor is typically **data coverage** and **trait naming mismatch** (many cancer strings do not exist as heritability `Trait`/`uniqTrait` aliases, and even when a cancer node exists in heritability, its study IDs may have no edges in the current genetic correlation dataset).

## How To Use This Document

- For backend evaluation: call `/agent/recommend` with one of the above `Trait ID` strings.
- For KG-only debugging: call the internal neighbor query via `genetic_graph_get_neighbors` (which uses `KnowledgeGraphService` under the hood).

