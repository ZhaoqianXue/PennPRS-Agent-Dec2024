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
│   └── ...                            # Module docs
├── src/                               # Source code
│   ├── client/                        # Frontend (Next.js)
│   │   ├── app/                       # App router
│   │   └── package.json               # Client dependencies
│   ├── server/                        # Backend (FastAPI)
│   │   ├── main.py                    # Entry point
│   │   ├── core/                      # Core logic & clients
│   │   ├── modules/                   # Functional modules
│   │   └── requirements.txt           # Backend dependencies
│   └── core/                          # Domain algorithms (R/Python)
├── shared/                            # Shared code
│   └── contracts/                     # Shared types/constants
├── data/                              # Data resources
├── output/                            # Generated outputs (logs, results, etc.)
│   └── logs/                          # Backend and frontend logs
├── scripts/                           # Utility scripts
├── tests/                             # Test suites
│   ├── unit/                          # Unit tests
│   └── integration/                   # Integration tests
├── pennprs-agent/                     # READ-ONLY reference directory
├── pgscatalog/                        # READ-ONLY reference directory
├── .cursorrules                       # Cursor IDE configuration
├── package.json                       # Root scripts
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
# Create a Python >=3.9 virtualenv and install backend deps
bash scripts/setup_server_venv.sh

# Set environment variables
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY

# Start the backend server
# Option A (recommended): use the helper script (prefers .venv)
bash scripts/run_server.sh
# For development with auto-reload:
bash scripts/run_server.sh --reload
```

### 2. Frontend Setup

From the root directory:

```bash
cd src/client
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

### Frontend (`src/client`)
- **Framework**: React 18 + Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui, Lucide Icons

### Backend (`src/server`)
- **Framework**: FastAPI
- **Agent Framework**: LangGraph + LangChain
- **Data Validation**: Pydantic
- **LLM**: OpenAI GPT models (configurable via `src/server/core/llm_config.py`)

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

All LLM models are centrally configured in `src/server/core/llm_config.py`. The project uses `gpt-5.2` as the default model.

## Cursor Rules (`.cursorrules`)

### Read-Only Reference Directories
- **`pennprs-agent/`** and **`pgscatalog/`** folders are **READ-ONLY** - they serve only as references for API usage and data structures.

### Project Structure Standards
- Frontend code → `/src/client`
- Backend code → `/src/server`
- Shared code → `/shared`
- Tests → `/tests`
- **Do not create files in the root directory**

## External Resources

- **PennPRS**: https://pennprs.org/
- **PGS Catalog**: https://www.pgscatalog.org/
- **OmicsPred**: https://www.omicspred.org/
- **Open Targets Platform**: https://platform.opentargets.org/
- **GWAS Catalog**: https://www.ebi.ac.uk/gwas/

## License

© 2026 PennPRS Team. All rights reserved.
