# Archived Code - Classification & Extraction Pipeline

> **Archive Date**: January 19, 2026  
> **Reason**: Strategy change from LLM-based extraction to curated database integration

## Background

This directory contains code and data from the deprecated Classification & Extraction Pipeline. The team decided to shift strategy after evaluating:

1. **Cost**: Processing large volumes of papers with LLMs is expensive
2. **Focus**: Building a knowledge database diverts effort from core platform features
3. **Existing Resources**: High-quality curated databases already exist

## New Approach

Instead of extracting data from literature using LLMs, the platform now uses API/Tool Calling to access curated databases:

| Data Type | Curated Database | Access Method |
|-----------|-----------------|---------------|
| **PRS Performance** | PGS Catalog | REST API |
| **Heritability** | GWAS Atlas, Pan-UK Biobank, UKBB LDSC | Download/API |
| **Genetic Correlations** | BIGA | API |

## Archived Contents

```
archived/
├── src/
│   ├── modules/literature/     # Extraction pipeline code
│   ├── lib/langextract/        # Extraction library
│   └── utils/langextract/      # Extraction utilities
├── scripts/
│   ├── validation/             # Classifier validation scripts
│   ├── testing/                # Extraction test scripts
│   └── debug/                  # Debugging scripts
├── data/
│   ├── literature/             # Extracted metrics
│   ├── test_results/           # Heritability test results
│   └── validation/             # Ground truth data
├── docs/project/               # Extraction-related documentation
├── frontend/app/               # Extraction demo UI
└── root_files/                 # Root-level extraction files
```

## Restoration

If needed, these files can be restored to their original locations. The original paths are preserved in the archive structure.

## Reference

See the original `docs/project/heritability_validation_strategy.md` in `archived/docs/project/` for details on the extraction pipeline design.
