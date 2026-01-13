# PennPRS Agent - Project Proposal

## Executive Summary

PennPRS Agent is an intelligent research platform for statistical genetics, providing automated literature curation, structured data extraction, and custom model training capabilities. The platform leverages Large Language Models (LLMs) to systematically extract key genetic metrics from PubMed literature, creating a unified, traceable database for Polygenic Risk Score (PRS) research.

**Current Focus**: Disease module with three integrated sub-modules:
1. **PRS Performance** - Model discovery and training
2. **Heritability (h²)** - SNP-heritability estimates
3. **Genetic Correlation** - Cross-trait genetic relationships

**Paused Modules**: Protein (OmicsPred) and Image (IDPs) are temporarily suspended to focus on vertical depth in the Disease domain.

---

## Target Users

- **Clinical Researchers**: Users with individual-level data (outcome labels and genetic data) for local deployment
- **Bioinformaticians**: Users with GWAS summary statistics seeking to train custom PRS models
- **Medical Geneticists**: Users exploring existing PRS models and genetic architecture from public literature
- **Epidemiologists**: Users investigating genetic relationships between diseases/traits

---

## Core Innovation: LLM-Powered Literature Curation

### The Problem

Current resources like PGS Catalog rely on manual curation, which is:
- **Slow**: Updates depend on human reviewers
- **Limited**: Only covers PRS models, not heritability or genetic correlations
- **Fragmented**: Information scattered across multiple databases

### Our Solution

| Aspect | PGS Catalog (Current) | PennPRS Agent (Proposed) |
|--------|----------------------|--------------------------|
| **Literature Discovery** | LitSuggest ML (requires training data) | LLM zero-shot + rule-based enhancement |
| **Information Extraction** | Manual curator reads papers | LLM Agent automatically extracts |
| **Update Frequency** | Depends on manual review | Real-time / daily automated updates |
| **Coverage** | PRS models only | PRS + h² + rg (three-in-one) |
| **Trainability** | Published models only | Integrated PennPRS + BIGA training APIs |
| **Traceability** | Citations present but not emphasized | Every data point directly links to PubMed |

### Technical Approach

We learn from and extend PGS Catalog's approach:

> *PGS Catalog uses a LitSuggest-based ML system trained on 1,704 curated publications to automate PubMed screening. The algorithm is not original to PGS Catalog but an adaptation of NCBI tools. LitSuggest itself uses machine learning models for document classification, optimizing recommendations without requiring PGS team to invent new algorithms.*

**Our enhancement**: Replace the training-dependent ML classifier with LLM-based zero-shot classification and structured extraction, while maintaining PGS Catalog's data schema for compatibility.

---

## Disease Module Architecture

The Disease module provides a comprehensive **Genetic Profile** for any queried disease, integrating three types of genetic metrics:

```
                    ┌─────────────────────────────────────┐
                    │      [Disease Name]                 │
                    │      Genetic Profile                │
                    └─────────────────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │         Unified Data Layer          │
                    │  ┌─────────────────────────────────┐│
                    │  │ LLM Agent + LitSuggest-style ML ││
                    │  │ → Scans PubMed weekly           ││
                    │  │ → Extracts structured metrics   ││
                    │  │ → Links to original papers      ││
                    │  └─────────────────────────────────┘│
                    └─────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│ Heritability  │         │ PRS Models    │         │ Genetic       │
│     (h²)      │         │ (Performance) │         │ Correlations  │
├───────────────┤         ├───────────────┤         ├───────────────┤
│ SOTA estimate │         │ SOTA model    │         │ SOTA rg       │
│ + history     │         │ + all models  │         │ + all pairs   │
│ [PMID Links]  │         │ [PMID Links]  │         │ [PMID Links]  │
├───────────────┤         ├───────────────┤         ├───────────────┤
│  Read-only    │         │ Train custom  │         │ Train custom  │
│  (no API)     │         │ via PennPRS   │         │ via BIGA      │
└───────────────┘         └───────────────┘         └───────────────┘
```

---

## Sub-Module 1: PRS Performance

### Purpose

Search, compare, and train Polygenic Risk Score models for disease risk prediction.

### Data Sources (Dual-Source Architecture)

PRS Performance utilizes a **Dual-Source Architecture** to ensure comprehensive coverage of the latest research:

| Data Source | Status | Description | Value |
|--------|------|------|------|
| **PGS Catalog API** | ✅ Completed | Expert-curated standardized PRS models | High quality, structured, downloadable weight files |
| **LLM Literature Extraction** | 🚧 Under Development | Automatically extract PRS performance data from PubMed literature | Covers the latest models not yet indexed by PGS Catalog |
| **PennPRS API** | ✅ Completed | User-defined model training | Supports personalized model development |

**Why is LLM Literature Extraction necessary?**
- PGS Catalog relies on manual review, resulting in a 6-12 month lag.
- Many high-quality PRS studies remain unindexed long after publication.
- LLM can automatically extract key metrics like AUC, R², variants, and method from papers.
- All extracted data retains PMID links, ensuring full traceability.

### Data Schema

Follows PGS Catalog structure for compatibility:

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Unique identifier | PGS000025 or CUSTOM-AD-2024 |
| `name` | Model name | AD-PRS-2024-Lambert |
| `trait` | Target trait | Alzheimer's Disease |
| `variants_number` | Number of variants | 84 |
| `ancestry` | Training population | European |
| `method` | PRS method | PRS-CS, LDpred2, C+T |
| `r2` | Variance explained | 0.08 |
| `auc` | AUC for binary traits | 0.78 |
| `sample_size` | Training sample size | 388,000 |
| `publication` | Source paper | Nature Genetics 2024 |
| `pmid` | PubMed ID with link | PMID:38xxxxxx |
| `gwas_id` | Source GWAS | GCST90012877 |

### User Experience: Alzheimer's Disease Example

```
┌────────────────────────────────────────────────────────────────┐
│ PRS Models for Alzheimer's Disease                             │
│ Data Source: PennPRS Database (PGS-style curation)             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Literature-Curated Models (via LitSuggest-style ML):           │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ Model: AD-PRS-2024-Lambert                                 │ │
│ │ Source: Nature Genetics 2024                               │ │
│ │ PubMed: PMID:38xxxxxx [Link]                               │ │
│ │                                                            │ │
│ │ • AUC: 0.78 (European, N=388,000)                          │ │
│ │ • R2: 0.08                                                 │ │
│ │ • Variants: 84                                             │ │
│ │ • Method: PRS-CS                                           │ │
│ │ • Training GWAS: GCST90012877                              │ │
│ │                                                            │ │
│ │ [View Details] [Download Weights]                          │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                │
│ Found 47 curated models from literature scan                   │
│                                                                │
│ [Filter by ancestry] [Sort by AUC] [Train Custom Model]        │
│                                      ↓                         │
│                              Uses PennPRS API                  │
└────────────────────────────────────────────────────────────────┘
```

### Agentic Pipeline Architecture (Supervisor + Workers)

```
      ┌─────────────────────────────────┐
      │        SUPERVISOR AGENT          │
      │  (Orchestrator - Not an LLM)     │
      ├─────────────────────────────────┤
      │ • Manages workflow state        │
      │ • Routes papers to workers      │
      │ • Aggregates results            │
      │ • Handles retries/errors        │
      └───────────────┬─────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│CLASSIFIER AGT │ │ EXTRACTOR AGTS│ │VALIDATOR AGT  │
│     (LLM)     │ │   (LLM x 3)   │ │ (Rule-based)  │
├───────────────┤ ├───────────────┤ ├───────────────┤
│ Task: Multi-  │ │┌─────────────┐│ │ Task: Schema  │
│ label classification││PRS Extractor││ │ validation +  │
│               │ │├─────────────┤│ │ deduplication │
│ Input: Abstract ││h2 Extractor ││ │               │
│               │ │├─────────────┤│ │ NOT an LLM!   │
│ Output: Labels│ ││rg Extractor ││ │(Deterministic)│
└───────────────┘ │└─────────────┘│ └───────────────┘
                  └───────────────┘
```

### System Pipeline

| Step | Implementation | Output |
|------|----------------|------|
| **Literature Discovery** | LLM zero-shot + PubMed E-utilities, periodic automated scanning | Relevant paper PMID list |
| **Paper Classification** | LLM determines if papers contain extractable PRS model data | Class labels + Confidence |
| **Information Extraction** | LLM Agent extracts: AUC, R², sample size, method, ancestry, variants | PGS-compatible structured data |
| **De-duplication** | Compare with existing PGS Catalog data to avoid duplicates | Unique new models |
| **Database Construction** | Structured storage, visualized alongside PGS Catalog data | Unified PRS model database |
| **Training Capability** | Users can train custom models via PennPRS API | Custom PRS models |

### Key Questions Answered

- "What PRS models exist for this disease in the literature?"
- "What is the current state-of-the-art (SOTA) model?"
- "Can I train a custom model with my own GWAS data?"

### Scientific Value

| Insight | Explanation |
|---------|-------------|
| **Beyond PGS Catalog** | Captures models from new papers not yet curated |
| **Structured + Traceable** | Every data point links to original publication |
| **Trainable** | Not satisfied with existing models? Train via PennPRS API |

---

## Sub-Module 2: Heritability (h²)

### Purpose

Provide literature-curated SNP-heritability estimates with full provenance, enabling researchers to understand the theoretical upper bound for PRS prediction.

### Data Sources

**LLM-curated PubMed extraction only** (no training API for h² - calculation requires individual-level or full summary statistics)

### Data Schema

| Field | Description | Example |
|-------|-------------|---------|
| `trait` | Target trait | Alzheimer's Disease |
| `h2` | SNP-heritability estimate | 0.24 |
| `se` | Standard error | 0.03 |
| `method` | Estimation method | LDSC, GCTA, GREML |
| `sample_size` | Sample size | 455,258 |
| `ancestry` | Population | European |
| `publication` | Source paper | Jansen et al., Nat Genet 2019 |
| `pmid` | PubMed ID with link | PMID:30617256 |
| `year` | Publication year | 2019 |

### User Experience: Alzheimer's Disease Example

```
┌────────────────────────────────────────────────────────────────┐
│ SNP-Heritability of Alzheimer's Disease                        │
│ Data Source: LLM-curated from PubMed literature                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   SOTA Estimate (from most recent meta-analysis):              │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │  h2 = 0.24 (SE: 0.03)                                    │ │
│   │  Source: Jansen et al., Nature Genetics 2019             │ │
│   │  PubMed: PMID:30617256 [Link]                            │ │
│   │  Sample: N = 455,258                                     │ │
│   │  Ancestry: European                                      │ │
│   │  Method: LDSC                                            │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                │
│   Historical Estimates (extracted from 12 papers):             │
│   ┌────────────────────────────────────────────────────────┐   │
│   │  Year  │ h2    │ N        │ Method │ PMID              │   │
│   │  2024  │ 0.26  │ 788,989  │ LDSC   │ 38xxxxxx [Link]  │   │
│   │  2022  │ 0.23  │ 472,868  │ LDSC   │ 35xxxxxx [Link]  │   │
│   │  2019  │ 0.24  │ 455,258  │ LDSC   │ 30617256 [Link]  │   │
│   │  2017  │ 0.19  │ 74,046   │ GCTA   │ 28xxxxxx [Link]  │   │
│   └────────────────────────────────────────────────────────┘   │
│                                                                │
│   LLM Summary:                                                 │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │ "AD has a moderate SNP-heritability (~24%), indicating   │ │
│   │ that common variants explain about a quarter of disease  │ │
│   │ liability. Estimates have remained stable across studies │ │
│   │ as sample sizes increased from 74K to 789K."             │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                │
│   Gap Analysis:                                                │
│   • Current best PRS R2 = 0.08                                 │
│   • Heritability h2 = 0.24                                     │
│   • Captured: 33% (0.08/0.24) -> 67% room for improvement      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### System Pipeline

| Step | Implementation |
|------|----------------|
| **Literature Search** | LLM Agent queries PubMed: `"[Disease]" AND ("heritability" OR "h2" OR "SNP-heritability")` |
| **Information Extraction** | LLM extracts: h² estimate, SE, sample size, method, ancestry |
| **SOTA Identification** | Automatically identifies most recent, largest-sample study as current SOTA |
| **Literature Linking** | All data points directly link to PubMed source |

### Key Questions Answered

- "What is the SNP-heritability of this disease?"
- "Which paper reported this estimate?"
- "How have estimates evolved as GWAS sample sizes increased?"
- "What is the theoretical ceiling for PRS prediction?"

### Scientific Value

| Insight | Explanation |
|---------|-------------|
| **Traceable SOTA** | Not a magic number, but explicit source: "h²=0.24 from Jansen 2019, N=455K" |
| **Historical Trend** | Visualize whether h² estimates stabilize as GWAS scales up |
| **Gap Analysis** | Combine with PRS data to calculate model efficiency: R²/h² |
| **Literature Entry Point** | Researchers can click through to read original papers |

### Gap Analysis: Why This Matters

The h² estimate sets the **theoretical upper bound** for PRS prediction:

```
If h² = 0.24 (24% of variance is genetic)
And best PRS R² = 0.08 (8% of variance explained)

Then: Efficiency = R²/h² = 0.08/0.24 = 33%

Interpretation: Current PRS captures only 33% of available genetic signal.
               There is 67% room for improvement!
```

This gap may be due to:
1. Insufficient GWAS sample size
2. Rare variants not captured
3. Suboptimal PRS methods
4. Poor cross-population generalization

---

## Sub-Module 3: Genetic Correlation

### Purpose

Provide literature-curated genetic correlation (rg) estimates between traits, and enable custom correlation calculation via BIGA API.

### Data Sources

1. **LLM-curated PubMed extraction**: Published rg estimates from literature
2. **BIGA API** (https://bigagwas.org/): Custom genetic correlation training

### Data Schema

| Field | Description | Example |
|-------|-------------|---------|
| `trait1` | First trait | Alzheimer's Disease |
| `trait2` | Second trait | Type 2 Diabetes |
| `rg` | Genetic correlation | +0.38 |
| `se` | Standard error | 0.05 |
| `p_value` | P-value | 1.2e-8 |
| `method` | Estimation method | LDSC, HDL, GNOVA |
| `publication` | Source paper | Smith et al., 2023 |
| `pmid` | PubMed ID with link | PMID:35xxxxxx |

### User Experience: Alzheimer's Disease Example

```
┌────────────────────────────────────────────────────────────────┐
│ Genetic Correlations with Alzheimer's Disease                  │
│ Data Source: LLM-curated from PubMed + BIGA Training API       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Literature-Curated Correlations (from 8 papers):               │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │  Trait                 │ rg     │ SE    │ Source           │ │
│ │  ─────────────────────────────────────────────────────────│ │
│ │  Type 2 Diabetes       │ +0.38  │ 0.05  │ PMID:35xxxxx     │ │
│ │  Coronary Artery Dis.  │ +0.25  │ 0.04  │ PMID:34xxxxx     │ │
│ │  Depression            │ +0.42  │ 0.06  │ PMID:33xxxxx     │ │
│ │  Educational Attainment│ -0.32  │ 0.03  │ PMID:30xxxxx     │ │
│ │  Cognitive Function    │ -0.45  │ 0.04  │ PMID:31xxxxx     │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                │
│ LLM Summary:                                                   │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ "AD shows positive genetic correlations with metabolic   │   │
│ │ (T2D, CAD) and psychiatric (depression) traits. Strong   │   │
│ │ negative correlations with cognitive/educational traits  │   │
│ │ suggest shared protective genetic factors."              │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ Train Custom Genetic Correlation Model                   │   │
│ │                                                          │   │
│ │ Want to calculate rg between AD and a new trait?         │   │
│ │                                                          │   │
│ │ Trait 1: Alzheimer's Disease (GCST90012877)              │   │
│ │ Trait 2: [Select or upload GWAS summary stats]           │   │
│ │                                                          │   │
│ │ Method: ( ) LDSC  ( ) HDL  ( ) GNOVA                     │   │
│ │                                                          │   │
│ │ [Submit to BIGA API]                                     │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### System Pipeline

| Step | Implementation |
|------|----------------|
| **Literature Search** | LLM Agent queries PubMed: `"[Disease]" AND ("genetic correlation" OR "rg" OR "LDSC")` |
| **Information Extraction** | LLM extracts: correlated traits, rg values, SE, method |
| **SOTA Aggregation** | Compile results from multiple papers into unified view |
| **Training Capability** | Users can call BIGA API to calculate new genetic correlations |

### Key Questions Answered

- "What traits are genetically correlated with this disease?"
- "Which papers reported these correlations?"
- "Can I calculate the genetic correlation between this disease and a new trait I'm interested in?"

### Scientific Value

| Finding | Clinical/Research Significance |
|---------|-------------------------------|
| **Literature Integration** | Aggregate rg estimates scattered across dozens of papers |
| **Traceability** | Every rg value links to original paper, not a black-box database |
| **Extensibility** | If users have new GWAS data, calculate new rg via BIGA API |
| **Hypothesis Generation** | LLM summaries help non-experts understand biological implications |

### Interpreting Genetic Correlations

| AD Correlation | Interpretation |
|----------------|----------------|
| AD ↔ T2D: rg = +0.38 | Metabolic pathways may be involved in AD pathogenesis. Could diabetes drugs (e.g., metformin) be protective for AD? |
| AD ↔ Education: rg = -0.32 | Genetic support for "cognitive reserve" hypothesis. Higher education associated with lower AD risk partly through shared genetics. |
| AD ↔ Depression: rg = +0.42 | Depression may not just be an early symptom of AD, but share causal mechanisms. Consider psychiatric comorbidity in clinical management. |

---

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
│  h2 = 0.24             │  Best AUC = 0.78       │  T2D: rg = +0.38      │
│  This sets the ceiling │  Best R2 = 0.08        │  Depression: rg = +0.42│
│                        │                        │  Education: rg = -0.32│
│                        │                        │                       │
├────────────────────────┼────────────────────────┼───────────────────────┤
│  Jansen 2019           │  Lambert 2024          │  Multiple sources     │
│  [PMID Link]           │  [PMID Link]           │  [PMID Links]         │
├────────────────────────┼────────────────────────┼───────────────────────┤
│  Read-only             │  Train via PennPRS     │  Train via BIGA       │
└────────────────────────┴────────────────────────┴───────────────────────┘
                                    │
                                    ▼
               ┌─────────────────────────────────────────┐
               │         Cross-Module Insights (LLM)     │
               │                                         │
               │  "Current PRS captures 33% of h2.       │
               │  AD is genetically correlated with      │
               │  T2D—consider multi-trait PRS to        │
               │  improve prediction accuracy."          │
               └─────────────────────────────────────────┘
```

### Automated Gap Analysis

```
Gap Analysis for Alzheimer's Disease:

1. Heritability Ceiling
   h2 = 0.24 (from Jansen 2019, PMID:30617256)
   
2. Current Best PRS
   R2 = 0.08 (from Lambert 2024, PMID:38xxxxxx)
   
3. Efficiency Calculation
   Efficiency = R2 / h2 = 0.08 / 0.24 = 33%
   
4. Improvement Potential
   67% of genetic signal remains uncaptured!
   
5. Suggested Next Steps
   - Consider multi-trait PRS incorporating T2D (rg = +0.38)
   - Explore trans-ancestry meta-analysis for larger GWAS
   - Investigate rare variant contributions
```

---

## Tech Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| React 18 | UI Framework |
| Next.js 15 | Full-stack Framework (App Router) |
| TypeScript | Type Safety |
| Tailwind CSS | Styling |
| shadcn/ui | UI Components |
| Framer Motion | Animations |
| Recharts | Data Visualization |
| Lucide Icons | Icon Library |

### Backend

| Technology | Purpose |
|------------|---------|
| FastAPI | REST API Framework |
| LangGraph | Agentic Workflow Orchestration |
| LangChain | LLM Integration |
| Pydantic | Data Validation |
| OpenAI GPT | Large Language Model |

### Data Infrastructure

| Resource | Usage |
|----------|-------|
| PGS Catalog API | PRS model metadata (existing) |
| PennPRS API | PRS model training (existing + enhanced) |
| BIGA API | Genetic correlation training (new) |
| PubMed E-utilities | Literature search and retrieval |
| LitSuggest-style ML | Literature classification (following PGS Catalog approach) |

### External APIs

| API | Purpose | Integration |
|-----|---------|-------------|
| PennPRS (https://pennprs.org/) | Train custom PRS models | Full integration |
| BIGA (https://bigagwas.org/) | Calculate genetic correlations | New integration |
| PubMed E-utilities | Literature search | LLM Agent access |
| PGS Catalog REST | Reference data | Existing integration |

---