## 3. validation_sample_size

Key empirical finding:

- `validation_sample_size` is a **very weak signal** for real-world PRS performance. It is a **last-resort tie-break**, not a meaningful differentiator.
- Larger validation sample size does not reliably predict better real-world performance. Selecting based primarily on validation size rarely leads to the best-performing model in external validation.
- `validation_sample_size` is most informative when drawn from the same representative validation record used for `performance_metrics`, `phenotyping_reported`, and `covariates`.

Warning signals (indicators of weaker real-world performance):

- a large validation sample is being used to justify a weaker phenotype match
- a very large validation sample is being used to rescue non-comparable AUC
- a large validation sample comes from a pan-trait single-biobank framework while a smaller but well-powered disease-focused study cohort has cleaner endpoint evidence
- a large validation sample is the primary justification for selection — this rarely predicts better external validation performance

When candidates are otherwise similar:

- Validation size is informative as a tie-break only when ALL other signals (endpoint, method, variants, performance, study design) are genuinely indistinguishable.
- Large validation size increases trust only after phenotype alignment is acceptable, and even then only minimally.
- Huge validation support alone does not reliably outperform a cleaner endpoint, a better method family, more variants, or a cleaner covariate design.
- Very large validation from a portability-framework study does not automatically outweigh a moderately large validation from a disease-focused multi-cohort study.
- Modest validation-size differences within the same publication family are essentially meaningless.
- Larger validation size does not reliably outperform a candidate with materially stronger methodological properties, variant count, or effect sizes.
- Large validation from a well-designed disease-focused study can be mildly supportive when the candidate is already endpoint-comparable and other signals are genuinely similar.

