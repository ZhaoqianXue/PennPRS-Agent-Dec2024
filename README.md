# PennPRS_Agent

An intelligent agent system for automated PRS (Polygenic Risk Score) model training, focusing on ADRD (Alzheimer's Disease and Related Dementias) risk prediction and stratification.

## Project Structure

```
PennPRS_Agent/
├── docs/                          # Technical documentation & Proposals
│   ├── function4_technical_documentation.md
│   ├── project_proposal.md
│   └── pgs_catalog_description.md
├── scripts/                       # Debug and utility scripts
│   └── debug_workflow.py
├── data/                          # Data resources
│   └── pgs_all_metadata/          # PGS Catalog metadata
├── src/                           # Source code (Backend)
├── frontend/                      # Source code (Frontend)
├── tests/                         # Test suites
├── pennprs-agent/                 # READ-ONLY reference directory
├── .cursorrules                   # Cursor IDE configuration
└── README.md                      # This file
```

## Getting Started

### 1. Backend Setup
From the root directory, run:
```bash
export PYTHONPATH=$PYTHONPATH:. && python3 src/main.py
# export PYTHONPATH=$PYTHONPATH:. && python3 src/main.py --reload
```

### 2. Frontend Setup
From the root directory, run:
```bash
cd frontend && npm run dev
```

## Documentation


### Core Documentation

- **`docs/project_proposal.md`**: Project overview, user requirements, core functions, and tech stack. Describes the four main functions:
  - Function(1): Benchmarking AD PRS Methods
  - Function(2): The One - ensemble models cross phenotypes
  - Function(3): Proteomics PRS Models
  - Function(4): Training PRS Models

- **`docs/function4_technical_documentation.md`**: Comprehensive technical documentation for Function(4) - Training PRS Models. Includes the new 3-Step Interactive Workflow:
  - **Step 0**: Disease Selection (AD, T2D, etc.)
  - **Step 1**: Model Recommendation & Training (Model Cards with Comparison)
  - **Step 2**: Downstream Applications (Evaluation, Ensemble, Proteomics)

- **`docs/pgs_catalog_description.md`**: Complete guide to PGS Catalog usage, including:
  - FTP structure and metadata organization
  - Scoring file formats (formatted and harmonized)
  - REST API access methods
  - Column schemas and data formats

### Reference Documentation

- **`pennprs-agent/README.md`**: Reference guide for PennPRS API usage (READ-ONLY). Contains:
  - PennPRS Tools overview and quick start guide
  - Web application features (Gradio interface)
  - Command-line tool usage examples
  - API tool methods (`PennPRSTool` class)
  - Default model parameters
  - Supported PRS methods and populations
  - **Note**: This directory is read-only and serves as a reference for understanding PennPRS API interactions

## Cursor Rules (`.cursorrules`)

The `.cursorrules` file defines critical project conventions:

### Read-Only Reference Directory
- **`pennprs-agent/`** folder is **READ-ONLY** - serves only as reference for understanding PennPRS API usage
- Do not modify or use code from this directory

### Project Structure Standards
- Source code → `/src`
- Tests → `/tests`
- Documentation → `/docs`
- Temporary output → `/output`
- **Do not create files in the root directory**

### Code Generation Rules
- All code, comments, and strings must be in English
- Follow PEP8 for Python code
- Use semantic, readable file names

## Tech Stack

- **Frontend**: React + Next.js + TypeScript + Tailwind CSS
- **Backend**: FastAPI + LangGraph + Pydantic
- **LLM**: gpt-5-mini

## External Resources

- **PennPRS**: https://pennprs.org/
- **PGS Catalog**: https://www.pgscatalog.org/
- **FinnGen**: ADRD GWAS data and pre-trained models

