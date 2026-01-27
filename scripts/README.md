# Scripts Directory

This directory contains utility scripts organized by purpose.

## Directory Structure

```
scripts/
├── README.md                    # This file
├── validation/                  # Classifier validation and benchmark scripts
├── testing/                     # Feature and integration testing scripts
├── utilities/                   # General-purpose utility scripts
├── data_processing/             # Data transformation and audit scripts
├── debug/                       # Debugging and troubleshooting scripts
└── download/                    # Data download scripts
```

## Subdirectories

### `validation/` - Classifier Validation & Benchmarking

Scripts for validating and benchmarking the LLM classifier accuracy.

| Script | Purpose |
|--------|---------|
| `build_heritability_ground_truth.py` | Build ground truth dataset for heritability classification |
| `test_heritability_classifier.py` | Test classifier accuracy on heritability ground truth |
| `test_pgs_catalog_accuracy.py` | Test PRS classifier accuracy on PGS Catalog papers |
| `benchmark_classifier.py` | Benchmark classifier performance |
| `benchmark_classifier_optimized.py` | Optimized version of classifier benchmark |

### `testing/` - Feature & Integration Testing

Scripts for testing specific features and full pipeline integration.

| Script | Purpose |
|--------|---------|
| `test_pmc_heritability_extraction.py` | Test heritability extraction from PMC full text |
| `test_alzheimers_pipeline.py` | Test pipeline on Alzheimer's disease papers |
| `test_europe_pmc.py` | Test Europe PMC API integration |
| `test_local_search.py` | Test local search functionality |
| `test_parallel_classifier.py` | Test parallel classification |

### `utilities/` - General Utilities

Miscellaneous utility scripts for various tasks.

| Script | Purpose |
|--------|---------|
| `check_pmc_fulltext.py` | Check PMC full-text availability |
| `fetch_pmc_xml.py` | Fetch XML from PMC |
| `verify_cohorts_fix.py` | Verify cohorts data fix |
| `verify_omicspred_details.py` | Verify OmicsPred details |
| `inspect_pennprs_file.py` | Inspect PennPRS file format |
| `benchmark_search.py` | Benchmark search performance |

### `data_processing/` - Data Transformation

Scripts for processing and auditing data.

| Script | Purpose |
|--------|---------|
| `dump_full_pgs_data.py` | Dump full PGS Catalog data |
| `dump_gene_json.py` | Export gene data to JSON |
| `final_data_audit.py` | Perform final data audit |
| `count_detailed_results.py` | Count and summarize results |

### `debug/` - Debugging Scripts

Debugging and troubleshooting scripts.

### `download/` - Download Scripts

Scripts for downloading external data.

## Usage

Most scripts can be run directly from the project root:

```bash
# Example: Run heritability extraction test
python scripts/testing/test_pmc_heritability_extraction.py

# Example: Run classifier validation
python scripts/validation/test_heritability_classifier.py
```

## Notes

- All scripts should be run from the **project root directory**
- Ensure `.env` file is configured with required API keys
- Install dependencies: `pip install -r requirements.txt`
