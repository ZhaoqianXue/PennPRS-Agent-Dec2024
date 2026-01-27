'use client';

import React, { useState } from 'react';
import { ExternalLink, BookOpen, FileText, Database, Activity, Info } from 'lucide-react';

// --- DATA ---
// Embedded JSON results from the test run (GPT-5.1 + Length Filter)
const RESULTS_DATA = {
    "total_papers": 5,
    "successful_extractions": 3,
    "failed_extractions": 2,
    "total_estimates": 38,
    "extractions": [
        {
            "pmid": "40906820",
            "pmcid": "PMC12419754",
            "title": "Alzheimer disease is (sometimes) highly heritable: Drivers of variation in heritability estimates for binary traits, a systematic review.",
            "num_extractions": 30,
            "extractions": [
                {
                    "id": "H2-40906820-001",
                    "trait": "Late-onset Alzheimer's disease (LOAD)",
                    "h2": 0.24,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML using individual-level data; ~499,757 genotyped SNPs, elderly screened and population controls, no age/sex covariates reported here",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 7139,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.9,
                    "evidence_html": "<div class=\"evidence-snippet\">...Table 2 ). The first LOAD GCTA heritability estimates were published in 2013 ( Table 2 and Fig 3 ). <mark class=\"highlight\">The resulting LOAD heritability estimate of 24% was based on a sample of 7,139 participants (3,290 cases, 3,849 controls) that included both elderly screened and population controls [</mark> 71 , 72 ]. Concurrently, Ridge et al. (2013) leveraged the Alzheimer's Disease Genetics Consortium ...</div>"
                },
                {
                    "id": "H2-40906820-002",
                    "trait": "Late-onset Alzheimer's disease (LOAD)",
                    "h2": 0.33,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML using ADGC dataset; HapMap Phase II imputed (~2,042,116 SNPs after QC)",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 10922,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.9,
                    "evidence_html": null
                },
                {
                    "id": "H2-40906820-003",
                    "trait": "Late-onset Alzheimer's disease (LOAD)",
                    "h2": 0.53,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML using 2016 ADGC update; 8,712,879 SNPs (1000 Genomes imputation), restricted to individuals with non-missing data on 21 known AD genes",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 9699,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.9,
                    "evidence_html": "<div class=\"evidence-snippet\">.... The ADGC dataset has since continued to expand, facilitating more comprehensive analyses of LOAD. <mark class=\"highlight\">A 2016 update included data from 30 studies within the ADGC, and the heritability estimate increased to 53%. This study included only 9,699 individuals (3,877 cases, 5,822 controls) [</mark> 75 ]. This sample size was smaller in this latter study due to the requirement for non-missing data...</div>"
                },
                {
                    "id": "H2-40906820-004",
                    "trait": "Late-onset Alzheimer's disease (LOAD), age 60–69 years",
                    "h2": 0.169,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML on two-phase ADGC data; up to ~38M imputed SNPs; covariates included age, sex, principal components, and cohort indicators",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 12698,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.85,
                    "evidence_html": null
                },
                {
                    "id": "H2-40906820-005",
                    "trait": "Late-onset Alzheimer's disease (LOAD), age >80 years",
                    "h2": 0.241,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML on two-phase ADGC data; up to ~38M imputed SNPs; covariates included age, sex, principal components, and cohort indicators",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 5198,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.85,
                    "evidence_html": null
                },
                {
                    "id": "H2-40906820-006",
                    "trait": "Late-onset Alzheimer's disease (LOAD), women",
                    "h2": 0.215,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML on two-phase ADGC data, sex-stratified; up to ~38M imputed SNPs; includes cohort indicators",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.8,
                    "evidence_html": "<div class=\"evidence-snippet\">...age (n = 5,198; h 2 = 24.1%) compared with those aged 60–69 years of age (n = 12,698; h 2 = 16.9%). <mark class=\"highlight\">Differences by sex were subtler with a slightly higher LOAD heritability among women (21.5%) compared with men (19.5%) [</mark> 78 ]. Overall, variation in study design, case definition, and sample characteristics can greatly i...</div>"
                },
                {
                    "id": "H2-40906820-007",
                    "trait": "Late-onset Alzheimer's disease (LOAD), men",
                    "h2": 0.195,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML on two-phase ADGC data, sex-stratified; up to ~38M imputed SNPs; includes cohort indicators",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.8,
                    "evidence_html": "<div class=\"evidence-snippet\">...age (n = 5,198; h 2 = 24.1%) compared with those aged 60–69 years of age (n = 12,698; h 2 = 16.9%). <mark class=\"highlight\">Differences by sex were subtler with a slightly higher LOAD heritability among women (21.5%) compared with men (19.5%) [</mark> 78 ]. Overall, variation in study design, case definition, and sample characteristics can greatly i...</div>"
                },
                {
                    "id": "H2-40906820-008",
                    "trait": "Late-onset Alzheimer's disease (LOAD), overall (two-phase ADGC with cohort indicators)",
                    "h2": 0.19,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML including cohort indicators as covariates on two-phase ADGC data",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 17896,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.8,
                    "evidence_html": null
                },
                {
                    "id": "H2-40906820-009",
                    "trait": "Late-onset Alzheimer's disease (LOAD), overall (two-phase ADGC without cohort indicators)",
                    "h2": 0.32,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML on same data as Lo et al. 2019 but omitting cohort indicators (sensitivity analysis)",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 17896,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.8,
                    "evidence_html": "<div class=\"evidence-snippet\">...ohorts [ 76 ]. This approach yielded a lower estimate of 19% for LOAD compared to previous studies. <mark class=\"highlight\">Their sensitivity analysis showed an increase to 32% when cohort indicators were removed, revealing a substantial cohort effect.</mark> Wang et al. (2021) similarly incorporated cohort indicators in their analysis of 2-phase ADGC data,...</div>"
                },
                {
                    "id": "H2-40906820-010",
                    "trait": "Late-onset Alzheimer's disease (LOAD), overall (two-phase ADGC analysis by Wang et al. 2021)",
                    "h2": 0.21,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML on 2-phase ADGC data with cohort indicators, similar approach to Lo et al. 2019",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 17896,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.75,
                    "evidence_html": "<div class=\"evidence-snippet\">...owed an increase to 32% when cohort indicators were removed, revealing a substantial cohort effect. <mark class=\"highlight\">Wang et al. (2021) similarly incorporated cohort indicators in their analysis of 2-phase ADGC data, obtaining an expected comparable heritability estimate of 21% [</mark> 78 ]. While GCTA-based approaches have significantly advanced our understanding of LOAD heritabilit...</div>"
                },
                {
                    "id": "H2-40906820-011",
                    "trait": "Late-onset Alzheimer's disease (LOAD), histopathologically confirmed (range across 5 cohorts)",
                    "h2": 0.31,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML in Baker et al. (2023) using consistent model with 5% liability threshold across five independent cohorts; lower end of reported range for histopathologically confirmed LOAD",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.7,
                    "evidence_html": "<div class=\"evidence-snippet\">... Clinical diagnosis have inherent misdiagnosis rates [ 83 ] that can affect heritability estimates. <mark class=\"highlight\">Baker et al (2023) illustrated this by demonstrating that the histopathologically confirmed LOAD yielded higher heritability estimates (31% - 57%) compared to clinically diagnosed LOAD (12% - 32%) when applying a consistent model with a 5% liability threshold to five independent cohorts [</mark> 79 ]. Notably, within the Amsterdam Dementia Cohort, using the amyloid-confirmed cases showed a her...</div>"
                },
                {
                    "id": "H2-40906820-012",
                    "trait": "Late-onset Alzheimer's disease (LOAD), histopathologically confirmed (range across 5 cohorts)",
                    "h2": 0.57,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML in Baker et al. (2023) with 5% liability threshold; upper end of histopathologically confirmed LOAD range",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.7,
                    "evidence_html": "<div class=\"evidence-snippet\">...at can affect heritability estimates. Baker et al (2023) illustrated this by demonstrating that the <mark class=\"highlight\">histopathologically confirmed LOAD yielded higher heritability estimates (31% - 57%) </mark>compared to clinically diagnosed LOAD (12% - 32%) when applying a consistent model with a 5% liabili...</div>"
                },
                {
                    "id": "H2-40906820-013",
                    "trait": "Late-onset Alzheimer's disease (LOAD), clinically diagnosed (range across 5 cohorts)",
                    "h2": 0.12,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML in Baker et al. (2023) with 5% liability threshold; lower end of clinically diagnosed LOAD range",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.7,
                    "evidence_html": "<div class=\"evidence-snippet\">...he histopathologically confirmed LOAD yielded higher heritability estimates (31% - 57%) compared to <mark class=\"highlight\">clinically diagnosed LOAD (12% - 32%) when applying a consistent model with a 5% liability threshold to five independent cohorts [</mark> 79 ]. Notably, within the Amsterdam Dementia Cohort, using the amyloid-confirmed cases showed a her...</div>"
                },
                {
                    "id": "H2-40906820-014",
                    "trait": "Late-onset Alzheimer's disease (LOAD), clinically diagnosed (range across 5 cohorts)",
                    "h2": 0.32,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML in Baker et al. (2023) with 5% liability threshold; upper end of clinically diagnosed LOAD range",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.7,
                    "evidence_html": "<div class=\"evidence-snippet\">...he histopathologically confirmed LOAD yielded higher heritability estimates (31% - 57%) compared to <mark class=\"highlight\">clinically diagnosed LOAD (12% - 32%) when applying a consistent model with a 5% liability threshold to five independent cohorts [</mark> 79 ]. Notably, within the Amsterdam Dementia Cohort, using the amyloid-confirmed cases showed a her...</div>"
                },
                {
                    "id": "H2-40906820-015",
                    "trait": "Late-onset Alzheimer's disease (LOAD), Amsterdam Dementia Cohort, amyloid-confirmed cases",
                    "h2": 0.57,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML within Amsterdam Dementia Cohort, amyloid-confirmed LOAD, 5% liability threshold",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.8,
                    "evidence_html": "<div class=\"evidence-snippet\">... when applying a consistent model with a 5% liability threshold to five independent cohorts [ 79 ]. <mark class=\"highlight\">Notably, within the Amsterdam Dementia Cohort, using the amyloid-confirmed cases showed a heritability estimate of 57%, while the clinical diagnosed cases from the same population yielded an estimate of 25%.</mark> This marked difference emphasizes the significant impact of diagnostic criteria on heritability est...</div>"
                },
                {
                    "id": "H2-40906820-016",
                    "trait": "Late-onset Alzheimer's disease (LOAD), Amsterdam Dementia Cohort, clinically diagnosed cases",
                    "h2": 0.25,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "GCTA-GREML within Amsterdam Dementia Cohort, clinically diagnosed LOAD, 5% liability threshold",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.8,
                    "evidence_html": "<div class=\"evidence-snippet\">...threshold to five independent cohorts [ 79 ]. Notably, within the Amsterdam Dementia Cohort, using the<mark class=\"highlight\"> amyloid-confirmed cases showed a heritability estimate of 57%, while the clinical diagnosed cases from the same population yielded an estimate of 25%.</mark> This marked difference emphasizes the significant impact of diagnostic criteria on heritability est...</div>"
                },
                {
                    "id": "H2-40906820-017",
                    "trait": "Late-onset Alzheimer's disease (LOAD), proportion of variance explained by APOE (Lee et al. 2013)",
                    "h2": 0.04,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "Variance component attributable to APOE using proxy SNPs within GCTA framework",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 7139,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.75,
                    "evidence_html": null
                },
                {
                    "id": "H2-40906820-018",
                    "trait": "Late-onset Alzheimer's disease (LOAD), proportion of variance explained by APOE (upper reported value)",
                    "h2": 0.1342,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "Variance component attributable to APOE ε2/ε4 or ε4 (some using BLUP regression on ε4 count) across GCTA-based studies",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.7,
                    "evidence_html": null
                },
                {
                    "id": "H2-40906820-019",
                    "trait": "Late-onset Alzheimer's disease (LOAD), LDSC observed-scale using Lambert et al. 2013 IGAP stage 1",
                    "h2": 0.0688,
                    "se": null,
                    "scale": "observed",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "LDSC on IGAP stage 1 summary statistics (Lambert et al. 2013)",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 54162,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.85,
                    "evidence_html": "<div class=\"evidence-snippet\">...ariation on the heritability estimates can be seen in studies leveraging summary statistics [ 24 ]. <mark class=\"highlight\">Zheng et al. (2017) and Chen et al. (2021) reported similar observed-scale heritability estimates of 6.88% and 6.80%, respectively [</mark> 87 , 89 ]. In contrast, the Brainstorm Consortium et al. (2018) provided a markedly different liabi...</div>"
                },
                {
                    "id": "H2-40906820-020",
                    "trait": "Late-onset Alzheimer's disease (LOAD), LDSC observed-scale using Lambert et al. 2013 IGAP stage 1 (alternative analysis)",
                    "h2": 0.068,
                    "se": null,
                    "scale": "observed",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "LDSC on same IGAP Lambert et al. 2013 data in Chen et al. 2021",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 54162,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.85,
                    "evidence_html": "<div class=\"evidence-snippet\">...ariation on the heritability estimates can be seen in studies leveraging summary statistics [ 24 ]. <mark class=\"highlight\">Zheng et al. (2017) and Chen et al. (2021) reported similar observed-scale heritability estimates of 6.88% and 6.80%, respectively [</mark> 87 , 89 ]. In contrast, the Brainstorm Consortium et al. (2018) provided a markedly different liabi...</div>"
                },
                {
                    "id": "H2-40906820-021",
                    "trait": "Late-onset Alzheimer's disease (LOAD), LDSC liability-scale using Lambert et al. 2013 IGAP stage 1 (Brainstorm Consortium)",
                    "h2": 0.13,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "LDSC with liability-scale transformation assuming population prevalence 17%",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 54162,
                    "ancestry": "European",
                    "prevalence": 0.17,
                    "confidence": 0.85,
                    "evidence_html": "<div class=\"evidence-snippet\">...eported similar observed-scale heritability estimates of 6.88% and 6.80%, respectively [ 87 , 89 ]. <mark class=\"highlight\">In contrast, the Brainstorm Consortium et al. (2018) provided a markedly different liability-scale heritability estimate of 13%, using a population prevalence of 17% for the transformation [</mark> 88 ]. Liability scale heritability is critical in adjusting for the ascertainment of the binary tra...</div>"
                },
                {
                    "id": "H2-40906820-022",
                    "trait": "Late-onset Alzheimer's disease (LOAD), LDSC using Kunkle et al. 2019 IGAP stage 1",
                    "h2": 0.07,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "LDSC on Kunkle et al. 2019 IGAP stage 1 data (5% assumed prevalence in some re-evaluations, but text here cites 7% liability-scale)",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 63926,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.7,
                    "evidence_html": null
                },
                {
                    "id": "H2-40906820-023",
                    "trait": "Late-onset Alzheimer's disease (LOAD), LDSC range across four datasets (re-evaluation using LDSC, 5% prevalence)",
                    "h2": 0.09,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Re-evaluation study using LDSC on four datasets, assuming 5% prevalence; lower end of reported range",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.65,
                    "evidence_html": "<div class=\"evidence-snippet\">... resulted in a large range of heritability estimates with a consistent population prevalence of 5%: <mark class=\"highlight\">the LOAD heritability estimates using LDSC ranged from 9% to 17% [</mark> 97 ] and 3% to 42% [ 98 ]. As expected, the GCTA estimates were higher at 25% to 31% [ 97 ]. LDAK e...</div>"
                },
                {
                    "id": "H2-40906820-024",
                    "trait": "Late-onset Alzheimer's disease (LOAD), LDSC range across four datasets (re-evaluation using LDSC, 5% prevalence)",
                    "h2": 0.17,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Same LDSC re-evaluation, upper end of range at 5% prevalence",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.65,
                    "evidence_html": "<div class=\"evidence-snippet\">... resulted in a large range of heritability estimates with a consistent population prevalence of 5%: <mark class=\"highlight\">the LOAD heritability estimates using LDSC ranged from 9% to 17% [</mark> 97 ] and 3% to 42% [ 98 ]. As expected, the GCTA estimates were higher at 25% to 31% [ 97 ]. LDAK e...</div>"
                },
                {
                    "id": "H2-40906820-025",
                    "trait": "Late-onset Alzheimer's disease (LOAD), LDSC range across ten datasets (re-evaluation using LDSC, 5% prevalence)",
                    "h2": 0.03,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Second LDSC-only re-evaluation across ten studies, 5% prevalence; lower end of range",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.65,
                    "evidence_html": null
                },
                {
                    "id": "H2-40906820-026",
                    "trait": "Late-onset Alzheimer's disease (LOAD), LDSC range across ten datasets (re-evaluation using LDSC, 5% prevalence)",
                    "h2": 0.42,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Same LDSC-only re-evaluation, upper end of range at 5% prevalence",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.65,
                    "evidence_html": null
                },
                {
                    "id": "H2-40906820-027",
                    "trait": "Late-onset Alzheimer's disease (LOAD), GCTA range across four datasets (re-evaluation using GCTA, 5% prevalence)",
                    "h2": 0.25,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "Re-evaluation using GCTA-GREML across four datasets, 5% prevalence; lower end of reported range",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.65,
                    "evidence_html": "<div class=\"evidence-snippet\">...f 5%: the LOAD heritability estimates using LDSC ranged from 9% to 17% [ 97 ] and 3% to 42% [ 98 ]. <mark class=\"highlight\">As expected, the GCTA estimates were higher at 25% to 31% [</mark> 97 ]. LDAK estimates generally aligned more closely with GCTA, and estimates derived from LDAK were...</div>"
                },
                {
                    "id": "H2-40906820-028",
                    "trait": "Late-onset Alzheimer's disease (LOAD), GCTA range across four datasets (re-evaluation using GCTA, 5% prevalence)",
                    "h2": 0.31,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "GCTA",
                    "method_detail": "Same GCTA re-evaluation, upper end of range at 5% prevalence",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.65,
                    "evidence_html": "<div class=\"evidence-snippet\">...f 5%: the LOAD heritability estimates using LDSC ranged from 9% to 17% [ 97 ] and 3% to 42% [ 98 ]. <mark class=\"highlight\">As expected, the GCTA estimates were higher at 25% to 31% [</mark> 97 ]. LDAK estimates generally aligned more closely with GCTA, and estimates derived from LDAK were...</div>"
                },
                {
                    "id": "H2-40906820-029",
                    "trait": "Late-onset Alzheimer's disease (LOAD), LDAK estimate using Kunkle et al. 2019 data",
                    "h2": 0.21,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "other",
                    "method_detail": "LDAK (accounts for MAF and LD in SNP weights) applied to Kunkle et al. 2019 GWAS, assuming 5% prevalence",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 63926,
                    "ancestry": "European",
                    "prevalence": 0.05,
                    "confidence": 0.75,
                    "evidence_html": null
                },
                {
                    "id": "H2-40906820-030",
                    "trait": "Late-onset Alzheimer's disease (LOAD), integrated GWAS+GWAX (de la Fuente et al. 2022)",
                    "h2": 0.31,
                    "se": null,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Method integrating standard GWAS and GWAX while correcting for attenuation; LDSC-based liability-scale estimate (exact point not explicitly given here, but de la Fuente 2022 typically reports ~31%)",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.5,
                    "evidence_html": null
                }
            ]
        },
        {
            "pmid": "40919893",
            "pmcid": "PMC12415860",
            "title": "Identification of pathogenic cell types and shared genetic loci and genes for Alzheimer's disease and inflammatory bowel disease.",
            "num_extractions": 4,
            "extractions": [
                {
                    "id": "H2-40919893-001",
                    "trait": "Alzheimer's disease (AD)",
                    "h2": 0.0217,
                    "se": 0.002,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Single-trait stratified LDSC (baseline-LD model) on GWAS AD summary statistics; liability-scale SNP heritability",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.9,
                    "evidence_html": "<div class=\"evidence-snippet\">...liminary genome-wide association analysis for AD as shown in Fig. 3(A) and Supplementary Fig. S2A . <mark class=\"highlight\">We first applied stratified LDSC (S-LDSC) [ 8 ] with the baseline-LD model [ 36 ] to estimate the liability-scale SNP heritability for AD and each of IBD, UC and CD ( Table 1 ). Single-trait LDSC shows SNP heritability estimates of 0.0217 (SE = 0.002) for GWAS AD , 0.3259 (SE = 0.0302) for GWAS IBD , 0.4836 (SE = 0.0533) for GWAS CD and 0.2745 (SE = 0.0315) for GWAS UC .</mark> Mean χ 2 statistics for GWAS AD , GWAS IBD , GWAS CD and GWAS UC are 1.2769, 1.2837, 1.2322 and 1.1...</div>"
                },
                {
                    "id": "H2-40919893-002",
                    "trait": "Inflammatory bowel disease (IBD)",
                    "h2": 0.3259,
                    "se": 0.0302,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Single-trait stratified LDSC (baseline-LD model) on GWAS IBD summary statistics; liability-scale SNP heritability",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.9,
                    "evidence_html": "<div class=\"evidence-snippet\">...liminary genome-wide association analysis for AD as shown in Fig. 3(A) and Supplementary Fig. S2A . <mark class=\"highlight\">We first applied stratified LDSC (S-LDSC) [ 8 ] with the baseline-LD model [ 36 ] to estimate the liability-scale SNP heritability for AD and each of IBD, UC and CD ( Table 1 ). Single-trait LDSC shows SNP heritability estimates of 0.0217 (SE = 0.002) for GWAS AD , 0.3259 (SE = 0.0302) for GWAS IBD , 0.4836 (SE = 0.0533) for GWAS CD and 0.2745 (SE = 0.0315) for GWAS UC .</mark> Mean χ 2 statistics for GWAS AD , GWAS IBD , GWAS CD and GWAS UC are 1.2769, 1.2837, 1.2322 and 1.1...</div>"
                },
                {
                    "id": "H2-40919893-003",
                    "trait": "Crohn's disease (CD)",
                    "h2": 0.4836,
                    "se": 0.0533,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Single-trait stratified LDSC (baseline-LD model) on GWAS CD summary statistics; liability-scale SNP heritability",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.9,
                    "evidence_html": "<div class=\"evidence-snippet\">...liminary genome-wide association analysis for AD as shown in Fig. 3(A) and Supplementary Fig. S2A . <mark class=\"highlight\">We first applied stratified LDSC (S-LDSC) [ 8 ] with the baseline-LD model [ 36 ] to estimate the liability-scale SNP heritability for AD and each of IBD, UC and CD ( Table 1 ). Single-trait LDSC shows SNP heritability estimates of 0.0217 (SE = 0.002) for GWAS AD , 0.3259 (SE = 0.0302) for GWAS IBD , 0.4836 (SE = 0.0533) for GWAS CD and 0.2745 (SE = 0.0315) for GWAS UC .</mark> Mean χ 2 statistics for GWAS AD , GWAS IBD , GWAS CD and GWAS UC are 1.2769, 1.2837, 1.2322 and 1.1...</div>"
                },
                {
                    "id": "H2-40919893-004",
                    "trait": "Ulcerative colitis (UC)",
                    "h2": 0.2745,
                    "se": 0.0315,
                    "scale": "liability",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Single-trait stratified LDSC (baseline-LD model) on GWAS UC summary statistics; liability-scale SNP heritability",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.9,
                    "evidence_html": "<div class=\"evidence-snippet\">...liminary genome-wide association analysis for AD as shown in Fig. 3(A) and Supplementary Fig. S2A . <mark class=\"highlight\">We first applied stratified LDSC (S-LDSC) [ 8 ] with the baseline-LD model [ 36 ] to estimate the liability-scale SNP heritability for AD and each of IBD, UC and CD ( Table 1 ). Single-trait LDSC shows SNP heritability estimates of 0.0217 (SE = 0.002) for GWAS AD , 0.3259 (SE = 0.0302) for GWAS IBD , 0.4836 (SE = 0.0533) for GWAS CD and 0.2745 (SE = 0.0315) for GWAS UC .</mark> Mean χ 2 statistics for GWAS AD , GWAS IBD , GWAS CD and GWAS UC are 1.2769, 1.2837, 1.2322 and 1.1...</div>"
                }
            ]
        },
        {
            "pmid": "40593228",
            "pmcid": "PMC12218862",
            "title": "Uncovering pleiotropic loci in allergic rhinitis and leukocyte traits through multi-trait GWAS.",
            "num_extractions": 4,
            "extractions": [
                {
                    "id": "H2-40593228-001",
                    "trait": "Allergic rhinitis (AR) – European population",
                    "h2": 0.0208,
                    "se": null,
                    "scale": "observed",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Single-trait LD Score regression using GWAS summary statistics for AR (UK Biobank); HapMap3 SNP LD scores for European ancestry; INFO > 0.9; SNP-based heritability estimated on observed scale.",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 484598,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.94,
                    "evidence_html": "<div class=\"evidence-snippet\">...Welch's t-test was then used to compare CD28 gene expression levels across these groups. ## Results <mark class=\"highlight\">We utilized LDSC to estimate SNP-based heritability, thereby determining the proportion of phenotypic variance explained by the detected variants. Based on the summary statistics from GWAS on allergic rhinitis, the estimated heritability on the observed scale was 2.08% in the European population and 1.03% in the East Asian population.</mark> For eosinophils, the estimated heritability on the observed scale was 19.64% in Europeans and 11.14...</div>"
                },
                {
                    "id": "H2-40593228-002",
                    "trait": "Allergic rhinitis (AR) – East Asian population",
                    "h2": 0.0103,
                    "se": null,
                    "scale": "observed",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Single-trait LD Score regression using GWAS summary statistics for AR (BioBank Japan); HapMap3 SNP LD scores for East Asian ancestry; INFO > 0.9; SNP-based heritability estimated on observed scale.",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": 161563,
                    "ancestry": "East Asian",
                    "prevalence": null,
                    "confidence": 0.94,
                    "evidence_html": "<div class=\"evidence-snippet\">...Welch's t-test was then used to compare CD28 gene expression levels across these groups. ## Results <mark class=\"highlight\">We utilized LDSC to estimate SNP-based heritability, thereby determining the proportion of phenotypic variance explained by the detected variants. Based on the summary statistics from GWAS on allergic rhinitis, the estimated heritability on the observed scale was 2.08% in the European population and 1.03% in the East Asian population.</mark> For eosinophils, the estimated heritability on the observed scale was 19.64% in Europeans and 11.14...</div>"
                },
                {
                    "id": "H2-40593228-003",
                    "trait": "Eosinophil counts – European population",
                    "h2": 0.1964,
                    "se": null,
                    "scale": "observed",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Single-trait LD Score regression using hematological trait GWAS summary statistics (eosinophil counts) in Europeans; HapMap3 SNP LD scores for European ancestry; INFO > 0.9; SNP-based heritability estimated on observed scale.",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "European",
                    "prevalence": null,
                    "confidence": 0.9,
                    "evidence_html": "<div class=\"evidence-snippet\">...population and 1.03% in the East Asian population. <mark class=\"highlight\">For eosinophils, the estimated heritability on the observed scale was 19.64% in Europeans</mark> and 11.14% in East Asians (Supplemental Table 2 ) . We next investigated the genetic correlations of allergic rhinitis with the seven leukocyte traits using cross-tr...</div>"
                },
                {
                    "id": "H2-40593228-004",
                    "trait": "Eosinophil counts – East Asian population",
                    "h2": 0.1114,
                    "se": null,
                    "scale": "observed",
                    "p_value": null,
                    "z_score": null,
                    "method": "LDSC",
                    "method_detail": "Single-trait LD Score regression using hematological trait GWAS summary statistics (eosinophil counts) in East Asians; HapMap3 SNP LD scores for East Asian ancestry; INFO > 0.9; SNP-based heritability estimated on observed scale.",
                    "intercept": null,
                    "lambda_gc": null,
                    "sample_size": null,
                    "ancestry": "East Asian",
                    "prevalence": null,
                    "confidence": 0.9,
                    "evidence_html": null
                }
            ]
        },
        {
            "pmid": "40596977",
            "pmcid": "PMC12211776",
            "title": "Integrated genetic analysis of Alzheimer's disease and stroke subtypes: insights from LDSC, PLACO, and MR studies.",
            "num_extractions": 0,
            "extractions": []
        },
        {
            "pmid": "41399369",
            "pmcid": "PMC12702048",
            "title": "Similarities and differences between Alzheimer's disease and schizophrenia: drug target Mendelian randomization and transcriptome analysis",
            "num_extractions": 0,
            "extractions": []
        }
    ]
};

// Simple link helper
const getLink = (pmcid: string, pmid?: string) => {
    if (pmcid) return `https://www.ncbi.nlm.nih.gov/pmc/articles/${pmcid}/`;
    if (pmid) return `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`;
    return '#';
};

export default function ExtractionDemoPage() {
    const [selectedPaperIndex, setSelectedPaperIndex] = useState(0);
    const selectedPaper = RESULTS_DATA.extractions[selectedPaperIndex];

    return (
        <div className="flex h-screen bg-gray-50 text-slate-800 font-sans">
            {/* Sidebar */}
            <div className="w-1/4 min-w-[300px] border-r border-gray-200 bg-white flex flex-col">
                <div className="p-6 border-b border-gray-100">
                    <h1 className="text-xl font-bold text-indigo-600 flex items-center gap-2">
                        <Activity className="w-6 h-6" /> Heritability Monitor
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">Validation Run: 5 Papers</p>
                    <div className="mt-4 flex gap-2 text-xs font-medium">
                        <span className="px-2 py-1 rounded-full bg-green-100 text-green-700">{RESULTS_DATA.successful_extractions} Success</span>
                        <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-600">{RESULTS_DATA.failed_extractions} Empty</span>
                    </div>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-2">
                    {RESULTS_DATA.extractions.map((paper, idx) => (
                        <button
                            key={idx}
                            onClick={() => setSelectedPaperIndex(idx)}
                            className={`w-full text-left p-3 rounded-xl transition-all duration-200 border group ${selectedPaperIndex === idx
                                    ? 'bg-indigo-50 border-indigo-200 shadow-sm'
                                    : 'bg-white border-transparent hover:bg-gray-50 hover:border-gray-200'
                                }`}
                        >
                            <div className="flex justify-between items-start mb-1">
                                <span className={`text-xs font-mono px-1.5 py-0.5 rounded ${selectedPaperIndex === idx ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-500'}`}>
                                    {paper.pmcid || 'Unknown ID'}
                                </span>
                                {paper.num_extractions > 0 ? (
                                    <span className="text-[10px] font-bold bg-green-100 text-green-600 px-1.5 py-0.5 rounded-full">{paper.num_extractions} Est</span>
                                ) : (
                                    <span className="text-[10px] font-bold bg-gray-100 text-gray-400 px-1.5 py-0.5 rounded-full">Empty</span>
                                )}
                            </div>
                            <h3 className={`text-sm font-semibold leading-snug line-clamp-2 ${selectedPaperIndex === idx ? 'text-indigo-900' : 'text-gray-700'
                                }`}>
                                {paper.title}
                            </h3>
                        </button>
                    ))}
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-y-auto">
                {selectedPaper ? (
                    <div className="max-w-5xl mx-auto p-10">
                        {/* Paper Header */}
                        <div className="mb-8 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
                            <div className="flex items-start justify-between gap-4">
                                <div>
                                    <div className="flex items-center gap-3 mb-3">
                                        {selectedPaper.pmcid && (
                                            <span className="px-2.5 py-1 text-xs font-bold rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-100 flex items-center gap-1">
                                                <Database className="w-3 h-3" /> {selectedPaper.pmcid}
                                            </span>
                                        )}
                                        {selectedPaper.pmid && (
                                            <span className="px-2.5 py-1 text-xs font-bold rounded-lg bg-blue-50 text-blue-700 border border-blue-100">
                                                PMID: {selectedPaper.pmid}
                                            </span>
                                        )}
                                    </div>
                                    <h2 className="text-2xl font-bold text-gray-900 leading-tight">
                                        {selectedPaper.title}
                                    </h2>
                                </div>
                                <a
                                    href={getLink(selectedPaper.pmcid, selectedPaper.pmid)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex-shrink-0 p-3 bg-gray-50 text-gray-500 rounded-xl hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
                                    title="View Original Paper"
                                >
                                    <ExternalLink className="w-5 h-5" />
                                </a>
                            </div>
                        </div>

                        {/* Extractions List */}
                        {selectedPaper.extractions.length === 0 ? (
                            <div className="bg-white border-2 border-dashed border-gray-200 rounded-2xl p-16 text-center">
                                <div className="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-6 text-gray-300">
                                    <FileText className="w-10 h-10" />
                                </div>
                                <h3 className="text-xl font-bold text-gray-900">No Heritability Data Found</h3>
                                <p className="text-gray-500 mt-2 max-w-lg mx-auto leading-relaxed">
                                    The extraction engine parsed this document but found no entries matching the heritability schema.
                                    This typically indicates the paper discusses genetic correlation, biological mechanisms, or qualitative reviews without reporting quantitative h² estimates.
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-8">
                                {selectedPaper.extractions.map((est) => (
                                    <div key={est.id} className="relative bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden group hover:shadow-md transition-all duration-300">
                                        {/* Confidence Indicator */}
                                        <div className="absolute top-0 right-0 p-4">
                                            <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold shadow-sm ${est.confidence >= 0.8 ? 'bg-green-100 text-green-700 border border-green-200' :
                                                    est.confidence >= 0.5 ? 'bg-yellow-100 text-yellow-700 border border-yellow-200' :
                                                        'bg-red-100 text-red-700 border border-red-200'
                                                }`}>
                                                {est.confidence >= 0.8 ? 'High Confidence' : 'Review Needed'} ({(est.confidence * 100).toFixed(0)}%)
                                            </div>
                                        </div>

                                        {/* Main Card Content */}
                                        <div className="p-8">
                                            <div className="pr-32 mb-6">
                                                <h4 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-2">
                                                    {est.trait}
                                                </h4>
                                                <div className="flex items-center gap-2 text-xs text-gray-400 font-mono">
                                                    <span>ID: {est.id}</span>
                                                </div>
                                            </div>

                                            {/* Detailed Grid */}
                                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-8 bg-gray-50/50 p-6 rounded-xl border border-gray-100">
                                                <DataPoint label="Heritability (h²)" value={est.h2} highlight />
                                                <DataPoint label="Stand. Error (SE)" value={est.se} />
                                                <DataPoint label="P-value" value={est.p_value} />
                                                <DataPoint label="Scale" value={est.scale} />

                                                <DataPoint label="Method" value={est.method} />
                                                <DataPoint label="Sample Size (N)" value={est.sample_size} />
                                                <DataPoint label="Ancestry" value={est.ancestry} className="col-span-2" />

                                                <DataPoint label="Intercept" value={est.intercept} />
                                                <DataPoint label="Lambda GC" value={est.lambda_gc} />
                                                <DataPoint label="Z-Score" value={est.z_score} />
                                                <DataPoint label="Prevalence" value={est.prevalence} />
                                            </div>

                                            {/* Method Details */}
                                            {est.method_detail && (
                                                <div className="mb-6">
                                                    <h5 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2 flex items-center gap-2">
                                                        <Info className="w-3 h-3" /> Method Details
                                                    </h5>
                                                    <p className="text-sm text-gray-700 bg-slate-50 p-3 rounded-lg border border-slate-100">
                                                        {est.method_detail}
                                                    </p>
                                                </div>
                                            )}

                                            {/* Evidence Section */}
                                            <div>
                                                <h5 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2 flex items-center gap-2">
                                                    <BookOpen className="w-3 h-3" /> Source Evidence
                                                </h5>
                                                {est.evidence_html ? (
                                                    <div
                                                        className="prose prose-sm max-w-none text-gray-600 bg-yellow-50/30 p-4 rounded-lg border-l-4 border-yellow-400 italic [&_.evidence-snippet_mark.highlight]:bg-yellow-200 [&_.evidence-snippet_mark.highlight]:text-yellow-900 [&_.evidence-snippet_mark.highlight]:px-1 [&_.evidence-snippet_mark.highlight]:rounded [&_.evidence-snippet_mark.highlight]:font-semibold"
                                                        dangerouslySetInnerHTML={{ __html: est.evidence_html || '' }}
                                                    />
                                                ) : (
                                                    <div className="flex items-center gap-2 text-sm text-gray-400 bg-gray-50 p-4 rounded-lg border border-gray-100 italic">
                                                        <Info className="w-4 h-4" /> Evidence visualization not available for this extraction.
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                    </div>
                ) : (
                    <div className="flex h-full items-center justify-center text-gray-400">
                        Select a paper to view results
                    </div>
                )}
            </div>
        </div>
    );
}

function DataPoint({ label, value, highlight, className = '' }: { label: string, value: any, highlight?: boolean, className?: string }) {
    const displayValue = value === null || value === undefined ? (
        <span className="text-gray-300 italic text-xs">None</span>
    ) : (
        <span className={highlight ? "text-indigo-600 font-bold" : "text-gray-900 font-medium"}>
            {String(value)}
        </span>
    );

    return (
        <div className={`flex flex-col ${className}`}>
            <span className="text-[10px] uppercase tracking-wider font-bold text-gray-400 mb-1">{label}</span>
            <div className="text-sm">{displayValue}</div>
        </div>
    )
}
