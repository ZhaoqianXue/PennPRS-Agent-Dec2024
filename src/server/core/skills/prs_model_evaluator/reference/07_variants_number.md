## 7. variants_number

Key empirical finding:

- `variants_number` is a moderate structural signal. For most diseases, more variants correlate with better external validation performance within the same method family.
- Variant count is most informative for comparing candidates **within** the same method family. Cross-method variant count comparison (e.g., genome-wide shrinkage vs GWAS-hits) reflects the method distinction already captured in Section 5 and is not an independent signal.

Within-method variant count comparison:

- For the **same method family**, the model with more variants is generally the stronger choice — the additional variants capture more polygenic signal.
- For **same-publication siblings** using the same method, a 1.5x or greater variant count difference is a meaningful structural signal.

Exceptions:

- For diseases with strong individual-locus effects (e.g., some cancers, autoimmune diseases, macular degeneration), GWAS-hits models with few variants can be competitive. For a meaningful minority of diseases, the variant count signal is weak or reversed.
- Very low variant counts (single-digit to low-tens) combined with a pan-trait framework origin is a warning sign: the model likely does not capture enough polygenic signal for complex traits.

