# PennPRS Agent

A comprehensive intelligent agent platform for Polygenic Risk Score (PRS) analysis, featuring disease risk prediction, proteomics scoring, and automated model training. The platform integrates data from PGS Catalog, PennPRS, OmicsPred, and Open Targets.

## Features

- **PennPRS-Disease**: Search, evaluate, and train PRS models for complex disease risk prediction
- **PennPRS-Protein**: Predict protein expression levels using OmicsPred genetic scores
- **PennPRS-Image**: Predict image-derived phenotypes (IDPs) - *Coming Soon*
- **Multi-Ancestry Support**: Train and evaluate models across diverse populations
- **Agentic Workflow**: LangGraph-powered intelligent classification and recommendation

## Project Structure

```
PennPRS_Agent/
├── docs/                              # Technical documentation
│   ├── README.md                      # Documentation index
│   ├── architecture/                  # System architecture docs
│   │   └── web_flow_redesign.md      # Web application flow
│   ├── protein/                       # Protein module docs
│   │   └── technical_documentation.md
│   ├── disease/                       # Disease module docs
│   │   ├── technical_documentation.md
│   │   ├── development_log.md
│   │   └── agentic_study_classifier.md
│   ├── api/                           # API documentation
│   │   └── api_endpoints.md
│   ├── data/                          # Data schema docs
│   │   ├── pgs_catalog_description.md
│   │   └── OMICSPRED_TSV_SCHEMA.md
│   └── project/                       # Project-level docs
│       └── project_proposal.md
├── src/                               # Backend source code
│   ├── main.py                        # FastAPI entry point
│   ├── core/                          # Core clients and utilities
│   │   ├── llm_config.py             # Centralized LLM configuration
│   │   ├── pennprs_client.py         # PennPRS API client
│   │   ├── pgs_catalog_client.py     # PGS Catalog API client
│   │   ├── omicspred_client.py       # OmicsPred local data client
│   │   └── opentargets_client.py     # Open Targets Platform client
│   ├── modules/                       # Functional modules
│   │   ├── protein/                   # Protein workflow (LangGraph)
│   │   └── disease/                   # Disease workflow (LangGraph)
│   ├── utils/                         # Common utilities
│   └── interfaces/                    # Interface layer
├── frontend/                          # React/Next.js frontend
│   ├── app/                           # Next.js app router
│   │   └── page.tsx                  # Main landing page
│   └── components/                    # React components
│       ├── DiseasePage.tsx           # Disease module page
│       ├── ProteinPage.tsx           # Protein module page
│       ├── ModelGrid.tsx             # Model card grid
│       ├── TrainingConfigForm.tsx    # Training configuration
│       ├── MultiAncestryTrainingForm.tsx  # Multi-ancestry training
│       └── ...                        # Additional components
├── data/                              # Data resources
│   ├── pgs_all_metadata/             # PGS Catalog metadata (local cache)
│   ├── omicspred/                    # OmicsPred scores database (~185MB TSV)
│   └── pennprs_gwas_metadata/        # PennPRS GWAS metadata
├── scripts/                           # Debug and utility scripts
│   ├── debug/                        # Debugging scripts
│   └── download/                     # Data download scripts
├── tests/                             # Test suites
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── fixtures/                     # Test data and mocks
├── pennprs-agent/                     # READ-ONLY reference directory
├── .cursorrules                       # Cursor IDE configuration
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API key

### 1. Backend Setup

From the root directory:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY

# Start the backend server
export PYTHONPATH=$PYTHONPATH:. && python3 src/main.py
# For development with auto-reload:
export PYTHONPATH=$PYTHONPATH:. && python3 src/main.py --reload
```

### 2. Frontend Setup

From the root directory:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to access the application.

## Documentation

For comprehensive documentation, see [`docs/README.md`](./docs/README.md).

### Core Modules

| Module | Documentation | Description |
|--------|---------------|-------------|
| **PennPRS-Disease** | [Disease Docs](./docs/disease/technical_documentation.md) | Disease risk prediction with PGS Catalog integration |
| **PennPRS-Protein** | [Protein Docs](./docs/protein/technical_documentation.md) | Protein expression prediction using OmicsPred |
| **Agentic Classifier** | [Classifier Docs](./docs/disease/agentic_study_classifier.md) | Intelligent GWAS study classification |

### API Reference

| Endpoint | Description |
|----------|-------------|
| `/agent/invoke` | Disease PRS agent interaction |
| `/protein/invoke` | Protein PRS agent interaction |
| `/opentargets/*` | Open Targets Platform search |
| `/agent/classify_study` | Agentic GWAS study classification |

See [API Endpoints Documentation](./docs/api/api_endpoints.md) for complete reference.

## Tech Stack

### Frontend
- **Framework**: React 18 + Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui, Lucide Icons
- **Animations**: Framer Motion
- **Charts**: Recharts

### Backend
- **Framework**: FastAPI
- **Agent Framework**: LangGraph + LangChain
- **Data Validation**: Pydantic
- **LLM**: OpenAI GPT models (configurable via `src/core/llm_config.py`)

### Data Sources
- **PGS Catalog**: Disease PRS models and metadata
- **PennPRS**: Training API and public models
- **OmicsPred**: Proteomics genetic scores
- **Open Targets Platform**: Disease and gene search
- **GWAS Catalog**: Study classification data

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM |
| `PENNPRS_EMAIL` | No | Default email for PennPRS API jobs |

### LLM Configuration

All LLM models are centrally configured in `src/core/llm_config.py`:

```python
from src.core.llm_config import get_llm

# Get configured LLM instance
llm = get_llm("disease_workflow")
llm = get_llm("agentic_classifier")
llm = get_llm("protein_workflow")
```

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

## External Resources

- **PennPRS**: https://pennprs.org/
- **PGS Catalog**: https://www.pgscatalog.org/
- **OmicsPred**: https://www.omicspred.org/
- **Open Targets Platform**: https://platform.opentargets.org/
- **GWAS Catalog**: https://www.ebi.ac.uk/gwas/

## License

© 2026 PennPRS Team. All rights reserved.
