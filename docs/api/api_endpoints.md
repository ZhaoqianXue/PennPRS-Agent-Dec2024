# PennPRS Agent - API Endpoints Reference

This document provides a comprehensive reference for all REST API endpoints exposed by the PennPRS Agent backend.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: TBD

## API Sections

1. [Disease Agent API](#disease-agent-api)
2. [Protein Agent API](#protein-agent-api)
3. [Open Targets API](#open-targets-api)
4. [Classification API](#classification-api)
5. [Utility API](#utility-api)

---

## Disease Agent API

### Invoke Disease Agent

**Endpoint**: `POST /agent/invoke`

Invokes the disease PRS agent with a message. Supports model search, recommendations, and training workflows.

**Request Body**:
```json
{
  "message": "string",
  "request_id": "string (optional)"
}
```

**Response**:
```json
{
  "response": "string",
  "structured_response": {
    "type": "model_cards | training_started | report | ...",
    "data": { ... }
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{"message": "Search PRS models for Alzheimer disease"}'
```

---

### Recommend PRS Models (Co-Scientist)

**Endpoint**: `POST /agent/recommend`

Generate a structured PRS model recommendation report using the co-scientist prompt.

**Request Body**:
```json
{
  "trait": "string"
}
```

**Response**:
```json
{
  "recommendation_type": "DIRECT_HIGH_QUALITY | DIRECT_SUB_OPTIMAL | CROSS_DISEASE | NO_MATCH_FOUND",
  "primary_recommendation": {
    "pgs_id": "PGS000025",
    "source_trait": "string",
    "confidence": "High | Moderate | Low",
    "rationale": "string"
  },
  "alternative_recommendations": [],
  "direct_match_evidence": {
    "models_evaluated": 5,
    "performance_metrics": {},
    "clinical_benchmarks": []
  },
  "cross_disease_evidence": {
    "source_trait": "string",
    "rg_meta": 0.85,
    "transfer_score": 0.72,
    "related_traits_evaluated": [],
    "shared_genes": [],
    "biological_rationale": "string",
    "source_trait_models": {
      "models_found": 8,
      "best_model_id": "PGS000XXX",
      "best_model_auc": 0.78
    }
  },
  "caveats_and_limitations": [],
  "follow_up_options": [
    {
      "label": "Train New Model on PennPRS",
      "action": "TRIGGER_PENNPRS_CONFIG",
      "context": "string"
    }
  ]
}
```

---

### Get Search Progress

**Endpoint**: `GET /agent/progress/{request_id}`

Get the progress of a long-running search request.

**Response**:
```json
{
  "status": "running | completed",
  "total": 100,
  "fetched": 45,
  "current_action": "Fetching model details..."
}
```

---

## Protein Agent API

### Invoke Protein Agent

**Endpoint**: `POST /protein/invoke`

Invokes the protein PRS agent for OmicsPred score search.

**Request Body**:
```json
{
  "message": "string",
  "request_id": "string (optional)",
  "platform": "string (optional)"
}
```

**Response**:
```json
{
  "response": "string",
  "structured_response": {
    "type": "protein_model_cards",
    "data": {
      "model_cards": [ ... ],
      "raw_results": [ ... ]
    }
  }
}
```

---

### List Protein Platforms

**Endpoint**: `GET /protein/platforms`

List all available proteomics platforms from OmicsPred.

**Response**:
```json
{
  "platforms": [
    {
      "name": "Olink Explore 1536",
      "count": 1472
    },
    {
      "name": "SomaScan v4",
      "count": 4979
    }
  ]
}
```

---

### Get Protein Score Details

**Endpoint**: `GET /protein/score/{score_id}`

Get detailed information for a specific OmicsPred score.

**Response**:
```json
{
  "id": "OPGS000001",
  "name": "...",
  "trait_reported": "...",
  "performance": {
    "r2": 0.15,
    "rho": 0.38
  }
}
```

---

## Open Targets API

### Full Search (All Entity Types)

**Endpoint**: `POST /opentargets/search/full`

Search all entity types (diseases, targets, drugs) sorted by relevance.

**Request Body**:
```json
{
  "query": "string",
  "page": 0,
  "size": 10
}
```

**Response**:
```json
{
  "hits": [
    {
      "id": "MONDO_0004975",
      "name": "Alzheimer disease",
      "entity_type": "disease",
      "score": 0.95
    }
  ],
  "total": 42
}
```

---

### Grouped Search (Autocomplete)

**Endpoint**: `POST /opentargets/search/grouped`

Returns results organized by entity type for autocomplete UI.

**Request Body**:
```json
{
  "query": "string",
  "size": 50
}
```

**Response**:
```json
{
  "topHit": { ... },
  "diseases": [ ... ],
  "targets": [ ... ],
  "drugs": [ ... ],
  "studies": [ ... ]
}
```

---

### Search Diseases

**Endpoint**: `POST /opentargets/search/disease`

Search only diseases/phenotypes.

**Request Body**:
```json
{
  "query": "string",
  "page": 0,
  "size": 10
}
```

---

### Search Targets (Genes/Proteins)

**Endpoint**: `POST /opentargets/search/target`

Search only targets (genes/proteins).

**Request Body**:
```json
{
  "query": "string",
  "page": 0,
  "size": 10
}
```

---

### Get Disease Details

**Endpoint**: `GET /opentargets/disease/{disease_id}`

Get detailed information about a disease.

**Parameters**:
- `disease_id`: Disease ID (e.g., "MONDO_0004975", "EFO_0000249")

**Response**:
```json
{
  "id": "MONDO_0004975",
  "name": "Alzheimer disease",
  "description": "...",
  "synonyms": [ ... ],
  "therapeuticAreas": [ ... ]
}
```

---

## Classification API

### Classify Trait

**Endpoint**: `POST /agent/classify_trait`

Classify whether a trait is Binary (disease) or Continuous (quantitative).

**Request Body**:
```json
{
  "trait_name": "string",
  "sample_info": "string (optional)"
}
```

**Response**:
```json
{
  "trait_type": "Binary | Continuous",
  "ancestry": "EUR | AFR | EAS | SAS | AMR",
  "confidence": "high | medium | low"
}
```

---

### Classify Study (Agentic)

**Endpoint**: `POST /agent/classify_study`

Agentic study classification using GWAS Catalog API data.

**Request Body**:
```json
{
  "study_id": "GCST90012877"
}
```

**Response**:
```json
{
  "study_id": "GCST90012877",
  "trait_type": "Continuous",
  "sample_size": 472868,
  "n_cases": null,
  "n_controls": null,
  "neff": null,
  "ancestry": "EUR",
  "confidence": "high",
  "reasoning": "Beta coefficients indicate continuous analysis"
}
```

---

## Utility API

### Health Check

**Endpoint**: `GET /`

Health check endpoint.

**Response**:
```json
{
  "status": "PennPRS Agent API is running"
}
```

---

## Error Responses

All endpoints may return the following error format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `400`: Bad Request - Invalid input
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server-side error

---

## Rate Limits

Currently no rate limiting is implemented. For production deployment, consider adding:
- Request rate limiting per IP
- API key authentication
- Usage quotas

---

*Document Version: 1.0*
*Last Updated: 2026-01-08*
