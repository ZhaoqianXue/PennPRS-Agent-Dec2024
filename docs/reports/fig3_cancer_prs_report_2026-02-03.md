# Fig. 3 Cancer PRS Recommendation Report (Enterprise Brief)

- Generated at: 2026-02-03
- Scope: 14 cancer traits from Fig. 3 (Zhang et al., 2020)
- Backend run artifacts: `output/reports/cancer_fig3_20260203_053732/`

## Executive Summary

This report summarizes a full backend execution of the PRS Model Recommendation SOP (`/agent/recommend`) across the 14 Fig. 3 cancer traits. For each cancer, the system:

- Executed a live recommendation run (LLM + tool calls) to determine recommendation outcome and a primary PGS model (if available).
- Executed a live PGS Catalog search to quantify availability and compute best observed AUC/R² among retrieved candidates.
- Persisted raw artifacts per cancer panel for auditability and reproducibility.

### Headline results

- Recommendation types (14 cancers total):
  - DIRECT_HIGH_QUALITY: 4
  - DIRECT_SUB_OPTIMAL: 9
  - NO_MATCH_FOUND: 1

- Best-AUC ranking (top 5):
  - Testicular: best AUC=0.982 (primary=PGS001164)
  - Prostate: best AUC=0.970 (primary=PGS000333)
  - Melanoma: best AUC=0.935 (primary=PGS001304)
  - Colorectal: best AUC=0.905 (primary=PGS003433)
  - Lung: best AUC=0.893 (primary=PGS004860)

## Slide Outline (Speaker Notes)

- Slide 1: Why Fig. 3 cancers (benchmark panel; stress-test model availability and quality tiers)
- Slide 2: Method (live `/agent/recommend` + live PGS Catalog search; artifacts saved)
- Slide 3: Portfolio view (type breakdown + Top AUC ranking)
- Slide 4: Per-cancer recommendations (primary PGS IDs and key metrics)
- Slide 5: Operational learnings (catalog rate limits; KG neighbor coverage)
- Slide 6: Next steps (KG trait resolution improvements; training option integration)

## Methodology (What Ran)

### Execution unit

For each trait query, the backend executed a real `/agent/recommend` call and recorded the full response JSON as an artifact.

### Additional availability quantification

Separately, a real PGS Catalog search was executed for the same trait query to compute:

- Total scores found in PGS Catalog
- Post-filter count (scores with performance signal)
- Best observed AUC and best observed R² among the returned top-ranked candidates (up to 25)

### Artifact layout

For each cancer panel:

- `output/reports/cancer_fig3_20260203_053732/raw/<panel_slug>/recommendation_report.json`
- `output/reports/cancer_fig3_20260203_053732/raw/<panel_slug>/pgs_search_result.json`

## Results Table (Slide-Ready)

| Panel | Trait query | PGS total found | After filter | Best AUC | Best R² | Recommendation type | Primary PGS ID | Confidence | Raw artifacts |
|---|---|---:|---:|---:|---:|---|---|---|---|
| CLL | Chronic lymphocytic leukemia | 8 | 7 | 0.861 |  | DIRECT_SUB_OPTIMAL | PGS000874 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/cll |
| Esophageal | Esophageal cancer | 8 | 8 | 0.819 | 0.012 | DIRECT_SUB_OPTIMAL | PGS003388 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/esophageal |
| Testicular | Testicular cancer | 14 | 13 | 0.982 | 0.605 | DIRECT_SUB_OPTIMAL | PGS001164 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/testicular |
| Oropharyngeal | Oropharyngeal cancer | 0 | 0 |  |  | NO_MATCH_FOUND |  | Low | output/reports/cancer_fig3_20260203_053732/raw/oropharyngeal |
| Pancreas | Pancreatic cancer | 12 | 8 | 0.830 | 0.439 | DIRECT_SUB_OPTIMAL | PGS000794 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/pancreas |
| Renal | Renal cancer | 10 | 7 | 0.740 | 0.366 | DIRECT_SUB_OPTIMAL | PGS004908 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/renal |
| Glioma | Glioma | 4 | 3 | 0.758 | 0.022 | DIRECT_SUB_OPTIMAL | PGS003384 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/glioma |
| Melanoma | Melanoma | 103 | 25 | 0.935 | 0.240 | DIRECT_HIGH_QUALITY | PGS001304 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/melanoma |
| Colorectal | Colorectal cancer | 75 | 25 | 0.905 | 0.598 | DIRECT_HIGH_QUALITY | PGS003433 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/colorectal |
| Endometrial | Endometrial cancer | 9 | 7 | 0.761 | 0.486 | DIRECT_SUB_OPTIMAL | PGS003381 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/endometrial |
| Ovarian | Ovarian cancer | 21 | 15 | 0.717 | 0.193 | DIRECT_SUB_OPTIMAL | PGS003385 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/ovarian |
| Lung | Lung cancer | 35 | 25 | 0.893 | 0.799 | DIRECT_SUB_OPTIMAL | PGS004860 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/lung |
| Prostate | Prostate cancer | 96 | 25 | 0.970 | 0.510 | DIRECT_HIGH_QUALITY | PGS000333 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/prostate |
| Breast | Breast cancer | 164 | 25 | 0.836 | 0.189 | DIRECT_HIGH_QUALITY | PGS001336 | Moderate | output/reports/cancer_fig3_20260203_053732/raw/breast |

## Talking Points (One-Liners)

- Portfolio result: 13/14 cancers have at least one PGS candidate; 4/14 are classified DIRECT_HIGH_QUALITY by the current backend policy.
- The highest observed AUC appears in Testicular cancer (AUC=0.982), followed by Prostate and Melanoma.
- One cancer (Oropharyngeal) returns NO_MATCH_FOUND in PGS Catalog under the current trait query string; this is a naming/coverage stress-test case.

## Operational Notes (Engineering-Grade)

### PGS Catalog rate limits

During the batch run, the PGS Catalog API returned frequent HTTP 429 (rate limiting) and occasional HTTP 500. The client retried with backoff and the overall run completed successfully. For production hardening:

- Add caching for score/performance lookups within a run.
- Add concurrency control for per-score detail fetches.
- Persist intermediate results to allow incremental resume.

### Genetic Graph coverage in this run

For cancers classified DIRECT_SUB_OPTIMAL or NO_MATCH_FOUND, the workflow executed the knowledge-graph neighbor query. In this batch run, the returned neighbor list was empty (neighbors=0) for each of these cancers, which implies:

- The current KG trait resolution did not map these cancer trait strings to canonical KG trait IDs (or cancer coverage is sparse in the underlying GWAS Atlas traits list).
- As a result, no cross-disease transfer candidates were surfaced, and no downstream mechanism/study-power evidence was added.

This is a functional limitation for “cross-cancer transfer” and should be prioritized if cross-disease recommendations are a product requirement.

### Report schema robustness

One run emitted a Pydantic validation warning during report construction (`genetic_graph_neighbors` was `None` instead of `[]`), and the system fell back to a minimal report based on Step 1 decision. The HTTP response remained 200. This should be fixed to keep reports schema-stable for downstream consumers.

## Next Steps

- Improve KG trait canonicalization for cancer traits (synonym mapping, carcinoma/cancer normalization, ontology bridging).
- Add a deterministic “query rewrite” fallback for NO_MATCH_FOUND (e.g., alternate trait strings).
- Add a fast “presentation payload” export (single JSON) to drive frontend demos without recomputation.

## References

- Zhang YD, et al. Assessment of polygenic architecture and risk prediction based on common variants across fourteen cancers. *Nature Communications*. 2020. DOI: `10.1038/s41467-020-16483-3`

