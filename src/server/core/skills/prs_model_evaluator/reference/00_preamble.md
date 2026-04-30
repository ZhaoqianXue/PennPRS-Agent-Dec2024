# PRS Model Domain Knowledge

Purpose: field-level domain knowledge for PRS model selection, summarizing empirical evidence on which model characteristics predict real-world external validation performance.

Empirical evidence supports the following factor importance ordering for predicting real-world PRS performance:

1. phenotype alignment and endpoint fidelity
2. comparable reported performance (effect sizes, PRS-comparable metrics)
3. transportability context (ancestry, training cohorts, study archetype)
4. method family and model structure (method_name, variants_number)
5. weak signals from publication context, date, validation sample size

Cross-cutting empirical patterns:

- Reliable selection depends only on visible metadata fields.
- Partial mismatches lower confidence but do not invalidate a candidate unless the mismatch is explicit.
- Missing evidence lowers confidence in a candidate.
- No single attractive field reliably compensates for weaknesses across other dimensions.
- A model from a disease-focused multi-cohort study consistently outperforms a pan-trait framework score in external validation unless the framework score has clearly stronger endpoint AND metric evidence.
- When several endpoint-faithful candidates from the same disease-focused study family form a coherent cluster, that cluster is strong evidence and typically outperforms a lone exact-label or lone high-AUC candidate whose apparent edge comes mainly from recency, exact wording, or a single full-model metric.
- Basic demographic adjustment (`age`, `age^2`, `sex`, PCs, batch, genotyping array) is not heavy clinical leakage. Family history, treatment terms, disease biomarkers, and horizon-conditioned absolute-risk packaging are.
- Unknown covariates are a weaker penalty than explicit non-comparable covariates. Family history, treatment-aware terms, biomarker adjustment, strong mediator adjustment, and risk-wrapper packaging are not less concerning simply because they are explicitly disclosed.
- Horizon-conditioned packaging, age-specific absolute-risk packaging, and named clinical risk calculators (e.g., `CHARGE-AF`, Framingham, QRISK, pooled cohort equations, `5-year risk`, `absolute risk`, `screening risk`) are strong negative evidence for standalone PRS quality. These are deployment packages, not cleaner PRS evidence. A candidate that uses such packaging is typically outperformed in external validation by a direct disease model with only demographic/PC-style covariates, even when the packaged model has much larger validation support.
- A full-model AUROC that is boosted by biomarkers, family history, or a clinical risk calculator is a heavily discounted advantage. A high full-model AUROC that comes only from age/sex/PCs or standard exposure covariates is informative but still secondary to endpoint fidelity.
- Cross-cancer, cross-disease, or pan-trait framework scores do not reliably outperform a disease-specific direct-match score unless the framework score has clearly better endpoint fidelity and cleaner comparable metrics. Large validation alone is not sufficient.
- An older exact-label portability score, sparse UKB score, or generic framework score that appears to beat a newer disease-focused or multi-cohort direct-match score solely because the older score reports an explicit PRS-only AUROC, has a familiar method name, or has a much larger validation sample is typically a selection artifact rather than genuine superiority.
- `Phenotype risk score`, `phenotype risk`, broad EHR phenotype summary, or similar phenotype-derived clinical packaging represents severe comparability leakage. A direct disease PRS candidate is the stronger choice over such a package unless no cleaner disease candidate exists.
- Bundled non-genetic risk packaging (named clinical calculators, family-history packages, PM2.5 or broad environmental bundles, smoking interaction terms) is a stronger penalty than ordinary demographic or simple epidemiologic adjustment.
- Within the same publication family and the same exact disease endpoint, modest differences in validation size, wording, or study framing are weak signals. The sibling with materially stronger OR/HR, cleaner PRS-only metrics, or cleaner covariates is the stronger choice.
- Within same-endpoint near-clone families, when the endpoint and covariates are effectively identical, a stronger regularized sibling with better AUROC/OR evidence outperforms a weaker sparse sibling.
- Spelling noise, minor formatting variants, or trivial wording differences are not meaningful endpoint mismatches when `trait_reported`, `trait_efo`, and `phenotyping_reported` all point to the same disease entity.
- Disease-focused multi-cohort meta-analysis models with exact endpoints and only basic demographic covariates are typically the stronger choice over older prevalent-endpoint sparse models, even when the older model has a larger single-biobank validation sample.
- An MTAG-enhanced variant from the same disease study family is a stronger choice than the base variant — MTAG leverages genetically correlated trait information to boost power and is not a cross-trait contamination signal.

