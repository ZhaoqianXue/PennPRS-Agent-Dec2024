# PennPRS Agent Documentation

This directory contains all technical documentation for the PennPRS Agent platform.

## Documentation Structure

```
docs/
├── README.md                           # This file - Documentation index
├── architecture/                       # System architecture and design
│   └── web_flow_redesign.md           # Web application flow and page architecture
├── protein/                            # PennPRS-Protein module (OmicsPred)
│   └── technical_documentation.md     # Protein module technical docs
├── disease/                            # PennPRS-Disease module
│   ├── technical_documentation.md     # Disease module technical docs
│   ├── development_log.md             # Development progress and roadmap
│   └── agentic_study_classifier.md    # Agentic GWAS classifier docs
├── api/                                # API documentation
│   └── api_endpoints.md               # Backend API reference
├── data/                               # Data schemas and formats
│   ├── pgs_catalog_description.md     # PGS Catalog data format
│   └── OMICSPRED_TSV_SCHEMA.md        # OmicsPred data schema
└── project/                            # Project-level documentation
    └── project_proposal.md            # Project overview and proposal
```

## Quick Links

### Core Modules

| Module | Description | Documentation |
|--------|-------------|---------------|
| **PennPRS-Disease** | Disease risk prediction using PGS Catalog models | [Disease Docs](./disease/technical_documentation.md) |
| **PennPRS-Protein** | Protein expression prediction using OmicsPred | [Protein Docs](./protein/technical_documentation.md) |
| **PennPRS-Image** | Image-derived phenotypes prediction | *Coming Soon* |

### Technical References

| Document | Description |
|----------|-------------|
| [API Endpoints](./api/api_endpoints.md) | Backend REST API reference |
| [Web Flow Design](./architecture/web_flow_redesign.md) | Frontend architecture and user flow |
| [Agentic Classifier](./disease/agentic_study_classifier.md) | Intelligent GWAS study classification |
| [PGS Catalog Schema](./data/pgs_catalog_description.md) | PGS Catalog data format reference |
| [OmicsPred Schema](./data/OMICSPRED_TSV_SCHEMA.md) | OmicsPred TSV data format |

### Project Management

| Document | Description |
|----------|-------------|
| [Project Proposal](./project/project_proposal.md) | Project overview, goals, and scope |
| [Development Log](./disease/development_log.md) | Development progress and history |

---

*Last Updated: 2026-01-08*
