# OmicsPred Data Directory

This directory stores genetic score data retrieved from **OmicsPred** (https://www.omicspred.org/).

## File Descriptions

- **`omicspred_scores_full.tsv`**: 
  - **Description**: A full list and metadata of all genetic scores available on the OmicsPred platform.
  - **Content**: Includes Score IDs (OPGS ID), associated protein/metabolite names, model methods (e.g., Bayesian Ridge regression), training sample sizes, discovery populations, reference genome versions, and publication DOIs.
  - **Usage**: Serves as the underlying database for local PRS recommendations and analytical features.

- **`download_progress.json`**:
  - **Description**: A JSON file tracking data download progress, used for resuming downloads or monitoring acquired score data.

- **`templates/`**:
  - **Description**: Contains HTML page templates (e.g., platforms and score detail pages) used for displaying OmicsPred data.

## About OmicsPred
OmicsPred is an atlas of genetic scores for the prediction of multi-omics data (e.g., proteomics, metabolomics, transcriptomics). This project leverages this data to provide statistically rigorous ranking inference and model suggestions.
