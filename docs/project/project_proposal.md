# PennGene Agent - Project Proposal

## Target Journal: Nature Genetics

## Executive Summary

PennGene Agent is an intelligent research platform for statistical genetics, providing unified access to curated genetic databases and custom model training capabilities. The platform leverages Large Language Models (LLMs) to enable natural language API/Tool Calling interactions with established databases, creating a "Genetic-Specific Co-Scientist" platform for Genetic-Disease research.

Our vision is to provide users with an industry-wide research synthesis for any queried disease (e.g., Alzheimer’s disease), integrating key metrics such as PRS Performance, Heritability, and Genetic Correlation. Inspired by the 'Deep Research' functionality of leading LLM platforms, we aim to deliver a specialized tool that rivals the depth of Gemini 3 Pro and GPT-5.2 while focusing exclusively on the Disease-to-Genetics domain.

**Current Focus**: Disease module with three integrated sub-modules:

| Sub-Module | Data Source (Read-Only) | User Training API |
|------------|------------------------|-------------------|
| **PRS Performance** | PGS Catalog | PennPRS API |
| **Heritability (h²)** | GWAS Atlas, Pan-UK Biobank, UKBB LDSC | TBD |
| **Genetic Correlation** | TBD | BIGA API |

**Paused Modules**: Protein (OmicsPred) and Image (IDPs) are temporarily suspended to focus on vertical depth in the Disease domain.

## Target Users

- **Clinical Researchers**: Users with individual-level data (outcome labels and genetic data) for local deployment
- **Bioinformaticians**: Users with GWAS summary statistics seeking to train custom PRS models
- **Medical Geneticists**: Users exploring existing PRS models and genetic architecture from curated databases
- **Epidemiologists**: Users investigating genetic relationships between diseases/traits

## Core Innovation: LLM-Powered Database Integration


### Technical Approach: Curated Database Integration

We integrate high-quality, expert-curated databases via LLM API/Tool Calling:

**Data Sources:**

| Data Type | Type | Database | Ancestries | Traits | Stats | Access |
|-----------|------|----------|------------|--------|-------|--------|
| **PRS Performance** | Meta-Platform | [PGS Catalog](https://www.pgscatalog.org/) | Multi (Global) | 666 traits | 5,251 scores | REST API |
| **Heritability** (Primary) | Meta-Platform | [GWAS Atlas](https://atlas.ctglab.nl/traitDB) | Multi (Global) | 3,307 traits | 4,756 GWAS | Download |
| **Heritability** (Supplementary) | Single-Cohort | [Pan-UK Biobank](https://pan.ukbb.broadinstitute.org/) | Multi (6 Groups) | 3,894 traits | 16,492 estimates | Download |
| **Heritability** (Supplementary) | Single-Cohort | [UKBB LDSC (Neale Lab)](https://nealelab.github.io/UKBB_ldsc/) | EUR | 4,541 traits | 11,685 estimates | Download |
| **Genetic Correlation** (Primary) | Meta-Platform | [GWAS Atlas](https://atlas.ctglab.nl/traitDB) | Multi (Global) | 3,307 traits | 1,393,615 $r_g$ pairs | Download |
| **Genetic Correlation** (Supplementary) | Single-Cohort | [GeneAtlas](http://geneatlas.roslin.ed.ac.uk/correlations/) | EUR | 778 traits (data) | 6,903 $r_g$ pairs | Download |

**User Training APIs:**

| Data Type | Training API | Purpose |
|-----------|-------------|--------|
| **PRS Performance** | [PennPRS](https://pennprs.org/) | Train custom PRS models |
| **Heritability** | TBD | - |
| **Genetic Correlation** | [BIGA](https://bigagwas.org/) | Calculate custom genetic correlations |

## Disease Module Architecture

The Disease module provides a comprehensive **Genetic Profile** for any queried disease, integrating three types of genetic metrics from curated sources:

```
                    ┌─────────────────────────────────────┐
                    │      [Disease Name]                 │
                    │      Genetic Profile                │
                    └─────────────────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │   LLM Agent: API/Tool Calling       │
                    │  ┌─────────────────────────────────┐│
                    │  │ Natural Language Interface      ││
                    │  │ → Queries curated databases     ││
                    │  │ → Aggregates structured data    ││
                    │  │ → Generates organized reports   ││
                    │  └─────────────────────────────────┘│
                    └─────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│ Heritability  │         │ PRS Models    │         │ Genetic       │
│     (h²)      │         │ (Performance) │         │ Correlations  │
├───────────────┤         ├───────────────┤         ├───────────────┤
│ GWAS Atlas    │         │ PGS Catalog   │         │ Data: TBD     │
│ Pan-UKB       │         │ (REST API)    │         │               │
│ UKBB LDSC     │         │               │         │               │
├───────────────┤         ├───────────────┤         ├───────────────┤
│ Train: TBD    │         │ Train custom  │         │ Train custom  │
│               │         │ via PennPRS   │         │ via BIGA      │
└───────────────┘         └───────────────┘         └───────────────┘
```

## Cross-Module Integration

### Unified Insights

The three sub-modules together provide a complete **Genetic Profile**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Alzheimer's Disease                                 │
│                     Genetic Profile                                     │
├────────────────────────┬────────────────────────┬───────────────────────┤
│     Heritability       │    PRS Performance     │  Genetic Correlations │
├────────────────────────┼────────────────────────┼───────────────────────┤
│                        │                        │                       │
│  h² = 0.24             │  Best AUC = 0.78       │  T2D: rg = +0.38      │
│  This sets the ceiling │  Best R² = 0.08        │  Depression: rg = +0.42│
│                        │                        │  Education: rg = -0.32│
│                        │                        │                       │
├────────────────────────┼────────────────────────┼───────────────────────┤
│  GWAS Atlas            │  PGS Catalog           │  Data: TBD            │
│  Pan-UKB, UKBB LDSC    │  (REST API)            │                       │
├────────────────────────┼────────────────────────┼───────────────────────┤
│  Train: TBD            │  Train via PennPRS     │  Train via BIGA       │
└────────────────────────┴────────────────────────┴───────────────────────┘
                                    │
                                    ▼
               ┌─────────────────────────────────────────┐
               │         Cross-Module Insights (LLM)     │
               │                                         │
               │  "Current PRS captures 33% of h².       │
               │  AD is genetically correlated with      │
               │  T2D—consider multi-trait PRS to        │
               │  improve prediction accuracy."          │
               └─────────────────────────────────────────┘
```

### Automated Gap Analysis

```
Gap Analysis for Alzheimer's Disease:

1. Heritability Ceiling
   h² = 0.24 (from GWAS Atlas)
   
2. Current Best PRS
   R² = 0.08 (from PGS Catalog)
   
3. Efficiency Calculation
   Efficiency = R² / h² = 0.08 / 0.24 = 33%
   
4. Improvement Potential
   67% of genetic signal remains uncaptured!
   
5. Suggested Next Steps
   - Consider multi-trait PRS incorporating T2D (rg = +0.38)
   - Explore trans-ancestry meta-analysis for larger GWAS
   - Investigate rare variant contributions
```