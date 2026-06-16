## 8. Cross-trait transfer considerations

Key empirical finding:

- When a target trait has no high-quality same-trait PGS, or its same-trait PGS underperforms in external validation, a cross-trait PGS from a related bundle can be a stronger choice. The patterns below govern how to identify, evaluate, and rank cross-trait transfer sources.

### 8.1 Bundle universe and breadth at probe selection

- Bundles with a large number of PGS models (high `n_models`) reflect well-studied, well-powered GWAS phenotypes — typically broad anthropometric, metabolic, hematological, or blood-pressure measurements. Their PGSs are frequent empirical cross-trait transfer sources, even when the bundle label does not lexically match the target, because shared polygenic architecture spans many disease endpoints. A small number (top few) of the highest-`n_models` bundles in the candidate universe should be considered as probes for any target.
- Bundles whose labels describe a plausible comorbidity, upstream cause, or downstream consequence of the target — even when no keyword overlaps — are valid probe candidates. Erring toward inclusion at the probe stage is preferred; downstream stages filter with actual evidence.
- Aliases of the target (synonyms, MONDO/EFO parents, anatomical or organ-system parents) are valid probe seeds even when lexical overlap with the target label is weak.

### 8.2 Mechanistic evidence at bundle ranking

- A cross-trait bundle with mechanism-supported overlap with the target — significant Open Targets shared targets, shared Reactome pathways, or known comorbidity / pleiotropy — outperforms a lexical-match bundle that lacks any mechanistic support.
- Open Targets gene/pathway overlap is the primary mechanistic evidence channel: it reveals whether two traits share genetic architecture by overlapping targets, pathways, or phenotypes, even when labels differ.
- Genetic correlation magnitude with target-cohort p-value, Open Targets shared-target count, and heritability of both target and candidate provide orthogonal evidence channels. Bundles where multiple orthogonal channels agree are stronger candidates than bundles with only one strong channel.
- Synonyms and narrower variants of the target disease are the single most reliable bundle-level signal for transferability when present. A bundle whose `canonical_label` is the same disease as the target (or an EFO/MONDO parent covering it) is a strong same-axis source. A direct same-trait or near-same-trait match should outrank a generic cross-trait bundle unless the same-trait bundle's evidence is absent or contradicts transfer.

### 8.3 Within-bundle PGS choice for transfer

- The primary signal of transferability of an individual PGS to a diverse multi-ancestry validation cohort is breadth of independent validation: count of `performance_records` whose `ancestry_broad` values span multiple distinct populations. A PGS validated across multiple ancestries (e.g., EUR, EAS, AFR) generalises better than a PGS validated only on a single ancestry, regardless of single-cohort published AUC.
- Newer mega-cohort PGSs are frequently optimised for and validated on a single ancestry (often EUR), which inflates their published metrics relative to multi-ancestry transfer. Newer or larger does not automatically translate to better external validation.
- Older consortium-derived PGSs that have been independently replicated across multiple ancestral populations are stronger cross-trait transfer candidates than brand-new mega-cohort PGSs validated only on their training ancestry, even when the older PGS has a lower single-cohort published AUC.
- The highest published AUC on a single cohort is not a sufficient signal in isolation; consistent (not necessarily peak) raw AUC / R² across several independent cohorts is a stronger robustness signal.
- When the supporting bundle's `canonical_label` differs from the target (cross-trait transfer), the model's own training quality still matters: large training sample, high raw validation AUC / R² on large independent cohorts, recent methodology, broad genome coverage. Pair these with the multi-ancestry breadth signal.

### 8.4 Cross-bundle reconciliation of the final primary

- Generalist anthropometric / metabolic bundles (BMI, height, lipid panel, blood pressure, hemoglobin) should not be dismissed as candidates. When such a bundle contains a PGS with broad multi-ancestry validation, it is frequently the more reliable primary for cross-trait transfer even when a same-trait bundle's per-bundle top pick has a higher single-cohort published metric. Polygenic architecture can let a high-quality metabolic PGS outperform a smaller same-trait PGS on an unrelated disease endpoint.
- A primary PGS chosen with strong raw quality signals (large `training_sample_total`, high raw `best_auc` / `best_r2` on large validation cohorts, modern method, well-powered variant count) is preferred over a primary chosen on label match alone.
- When two candidates look comparable on raw quality and on multi-ancestry breadth, the one whose source bundle has stronger per-bundle evidence (significant genetic correlation, large Open Targets shared-target overlap) with the target is the more reliable choice.

### 8.5 Within-bundle PGS triage

- When a supporting bundle contains many PGS models, triage should prioritise PGSs whose `reported_trait` / `trait_mapped` / `trait_efo` are semantically closest to the supporting bundle's `canonical_label` and to the target_label.
- For cross-trait transfer (bundle trait differs from target trait), prefer models with strong raw `performance_digest.best_auc` / `best_r2` on large training cohorts; for cross-trait transfer the model's own quality matters most.
- Diverse triaged sets (different `method_name` values, different `publication_year` ranges) are more likely to surface a transfer-strong PGS than triaged sets clustered on one method or one publication wave.
