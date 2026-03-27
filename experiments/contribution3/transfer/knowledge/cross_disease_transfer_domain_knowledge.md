# Cross-Disease PRS Transfer Domain Knowledge

Purpose: field-level domain knowledge for cross-disease PRS transfer, summarizing empirical evidence on which genetic signals predict successful cross-disease PRS model transfer. This document is injected as optional additional evidence during LLM-based transfer candidate selection.

Empirical evidence supports the following principle ordering for predicting cross-disease PRS transfer success:

1. genetic correlation strength and statistical reliability
2. shared genetic mechanism evidence (shared genes, shared pathways)
3. neighbor trait heritability as a transfer ceiling
4. biological domain coherence and known disease cluster relationships

Cross-cutting empirical patterns:

- Cross-disease PRS transfer exploits shared genetic architecture (pleiotropy) between diseases. A PRS model built for disease B can predict disease A if the genetic variants driving B also influence A.
- The theoretical upper bound of transferable genetic variance is approximately rg^2 x h2_neighbor. This is a ceiling, not a guarantee. Actual transferred performance depends on the PRS model's ability to capture the neighbor's genetic architecture and the degree of true shared biology.
- Transfer works best when the shared genetic architecture reflects shared biological mechanisms, not statistical artifacts (LD-driven or population-stratification-driven correlations).
- A single strong signal (e.g., very high rg) does not guarantee successful transfer if other signals are absent or contradictory. Convergent evidence across multiple signal types is stronger than any single metric.
- Transfer is asymmetric: a PRS from disease B predicting disease A may perform differently than a PRS from A predicting B, because the two diseases may capture different fractions of their shared genetic architecture.

## 1. Genetic Correlation (rg)

Key empirical finding:

- rg is the primary statistical signal for cross-disease PRS transferability.
- |rg| reflects the proportion of genetic architecture shared between two diseases. Higher |rg| means more shared causal variants and regulatory mechanisms.
- rg is estimated from GWAS summary statistics using LD Score Regression (LDSC) and aggregated across multiple study pairs using inverse-variance weighted meta-analysis.

Positive signals (indicators of stronger transfer potential):

- high |rg| (above 0.5) with strong statistical support (|rg_z| well above 2)
- rg estimated from multiple independent study pairs (n_correlations > 3), indicating robustness across different cohorts and study designs
- consistent sign of rg across study pairs (all positive or all negative), indicating a stable genetic relationship
- rg between diseases in related biological domains, suggesting mechanistic plausibility

Warning signals (indicators of weaker or unreliable transfer):

- rg estimated from a single study pair (n_correlations = 1): the estimate may be cohort-specific or driven by sample overlap artifacts
- high |rg| but with large standard error (low |rg_z|): statistically unreliable despite appearing strong
- rg just above the significance threshold (|rg_z| barely above 2): borderline evidence
- rg between biologically unrelated diseases without shared gene evidence: may reflect LD or population stratification rather than true shared biology
- very high |rg| (above 0.8) between seemingly unrelated diseases: warrants skepticism unless corroborated by shared gene/pathway evidence

Sign and direction:

- Positive rg means concordant risk alleles: alleles that increase risk for disease A also increase risk for disease B. PRS transfers in the same direction.
- Negative rg means inversely correlated genetic risk: alleles increasing risk for A decrease risk for B. PRS may transfer in the opposite direction. This is biologically meaningful (e.g., autoimmune diseases vs. infections can show negative rg) but requires careful interpretation for PRS transfer.
- For PRS transfer purposes, |rg| (absolute value) determines the magnitude of shared signal. The sign determines whether the transferred PRS effect needs to be interpreted as concordant or discordant.

Interaction with study power:

- n_correlations (number of study pairs aggregated) is a proxy for the reliability of the rg estimate. Higher n_correlations increases confidence.
- rg from large, well-powered GWAS studies is more reliable than rg from small or underpowered studies. rg_z captures this: it reflects both effect size and precision.
- When two neighbors have similar |rg|, prefer the one with higher |rg_z| and more n_correlations.

## 2. Shared Gene/Pathway Evidence (Open Targets)

Key empirical finding:

- Shared genes provide mechanistic evidence for WHY genetic correlation exists between two diseases.
- Open Targets disease-target associations are scored based on multiple evidence types: genetic associations (GWAS), somatic mutations, known pathways, literature mining, animal models, and expression data. A high association score means robust multi-evidence support.
- Shared genes with high association scores in BOTH diseases are stronger evidence than genes ranked highly in only one disease. A gene strongly associated with both diseases is more likely to be a true shared causal gene.

Positive signals (indicators of stronger transfer):

- multiple shared genes (5 or more) with high association scores in both diseases: strong mechanistic evidence for shared biology
- shared genes belonging to coherent biological pathways relevant to both diseases: the shared genetics reflects shared biology, not coincidence
- shared genes with known druggability: suggests functional relevance and well-studied biological mechanisms
- shared genes in HLA/MHC region for autoimmune diseases: well-established shared genetic basis for autoimmune conditions
- gene-level evidence corroborated by pathway-level evidence: convergent biological signal

Warning signals:

- no shared genes despite moderate-to-high rg: the genetic correlation may be driven by distributed polygenic signal, LD, or population stratification rather than specific shared causal genes. Transfer may still work but with lower mechanistic confidence.
- shared genes with high score in one disease but very low score in the other: the gene may be primarily relevant to one disease, with the shared association being incidental
- all shared genes from a single pathway (e.g., only HLA genes): narrow mechanistic basis that may not generalize
- shared gene evidence driven entirely by literature co-mention rather than genetic association data: weaker mechanistic basis

Interaction with rg:

- High rg + many shared genes + coherent pathways = strongest transfer evidence. Both statistical and mechanistic signals converge.
- High rg + no shared genes = transfer may work based on distributed polygenic signal, but the mechanism is unclear. Lower confidence.
- Moderate rg + many shared genes = shared gene evidence strengthens the case for transfer beyond what rg alone suggests. The mechanistic evidence compensates for moderate statistical signal.
- Low rg + some shared genes = unlikely to support effective PRS transfer. Some shared biology exists but insufficient shared genetic architecture for meaningful PRS transfer.

## 3. Heritability (h2)

Key empirical finding:

- Heritability (h2) of the neighbor disease sets a ceiling for how much genetic signal its PRS model can capture.
- A neighbor with very low h2 has a PRS that captures little genetic variance in its own disease, limiting the transferable signal even with high rg.
- The target disease's h2 provides context: if the target itself has low h2, the ceiling for any PRS prediction (direct or transferred) is low.
- h2 is estimated from GWAS summary statistics and aggregated across studies via meta-analysis.

Positive signals:

- neighbor h2 above 0.1 with strong statistical support (h2_z above 3): the neighbor's genetic architecture is well-captured, providing meaningful signal for transfer
- h2 based on multiple aggregated studies (n_studies above 2): more reliable estimate
- neighbor from a well-powered GWAS domain (e.g., psychiatric, cardiometabolic): PRS models from these domains tend to have better predictive performance

Warning signals:

- very low neighbor h2 (below 0.05): the neighbor's PRS captures minimal genetic variance, limiting what can be transferred
- h2 estimated from a single small study: may be unreliable
- negative h2 estimate: artifact of small sample size or model misspecification, not biologically meaningful
- h2_z below 2: heritability estimate is not statistically different from zero

Transfer ceiling:

- The theoretical maximum proportion of variance in the target disease that can be explained by a transferred PRS is approximately rg^2 x h2_neighbor.
- Example: if rg = 0.6 and h2_neighbor = 0.3, the ceiling is 0.36 x 0.3 = 0.108 (about 11% of variance). This is a meaningful signal.
- Example: if rg = 0.2 and h2_neighbor = 0.05, the ceiling is 0.04 x 0.05 = 0.002 (0.2% of variance). This is negligible.
- Use the transfer ceiling to prioritize: neighbors with higher rg^2 x h2 are more likely to yield useful PRS transfer.

## 4. Domain and Biological Coherence

Key empirical finding:

- Diseases in the same biological domain (e.g., both psychiatric, both autoimmune, both cardiometabolic) often share regulatory architecture and biological pathways, making PRS transfer more biologically plausible.
- Cross-domain transfer CAN work when supported by strong rg and shared gene evidence, but requires a higher evidence threshold because the biological connection is less obvious.
- GWAS Atlas classifies traits into domains (Psychiatric, Neurological, Cardiovascular, Metabolic, Immunological, etc.). Same-domain neighbors have a prior advantage in biological plausibility.

Known high-transfer disease clusters:

- Autoimmune/inflammatory cluster: rheumatoid arthritis, lupus, type 1 diabetes, celiac disease, inflammatory bowel disease, Crohn's disease, ankylosing spondylitis. These diseases share extensive HLA/MHC-driven genetics and immune regulatory pathways. Cross-transfer within this cluster is often strong.
- Psychiatric cluster: schizophrenia, bipolar disorder, major depressive disorder, ADHD, autism spectrum disorder. These diseases share substantial distributed polygenic architecture across neurodevelopmental and synaptic pathways. rg values within this cluster are often 0.3-0.7.
- Cardiometabolic cluster: coronary artery disease, type 2 diabetes, obesity/BMI, hypertension, lipid levels. Shared metabolic and vascular pathways drive cross-disease genetic correlations.
- Neurodegenerative cluster: Alzheimer's disease, Parkinson's disease, dementia. Shared neuroinflammatory and protein aggregation pathways, though cross-rg is often modest.
- Atopic/allergic cluster: asthma, eczema/atopic dermatitis, allergic rhinitis, hay fever. Shared Th2-immune and epithelial barrier pathways.

Cross-domain transfer patterns worth noting:

- Psychiatric to autoimmune: moderate rg is frequently observed (e.g., depression and inflammatory bowel disease), mechanism often through shared inflammatory/neuroimmune pathways.
- Neurological to psychiatric: often meaningful rg for neurodegeneration-mood connections (e.g., Alzheimer's and depression).
- Cardiometabolic to psychiatric: moderate rg (e.g., BMI/obesity and depression, type 2 diabetes and schizophrenia), mechanism through metabolic and inflammatory pathways.
- Cancer cross-transfer: generally weaker than within-cluster for non-cancer groups. Some cancers share DNA repair or immune evasion pathways, but cancer PRS transfer is often limited to closely related cancer types (e.g., breast and ovarian via BRCA pathways).

When candidates are otherwise similar:

- Same-domain neighbors with comparable rg and shared gene evidence are preferred over cross-domain neighbors, because the biological coherence reduces the risk of spurious transfer.
- A cross-domain neighbor with substantially higher rg and strong shared gene evidence can outperform a same-domain neighbor with weaker genetic evidence. Domain is a prior, not a veto.
- Measurement traits (e.g., brain imaging measures, blood biomarkers) may show high rg with clinical diseases but their PRS models predict a different construct than the disease itself. Prefer clinical disease neighbors over measurement trait neighbors when both are available.
