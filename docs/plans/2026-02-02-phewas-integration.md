# Implementation Plan - PheWAS Integration for Mechanism Validation

**Goal:** Integrate PheWAS (Phenome-Wide Association Study) evidence into the `validate_mechanism` tool to provide additional multi-omics proof for cross-disease PRS model recommendation.

**Skill:** subagent-driven-development
**Rules:** rules.md (Monorepo, Contract-First, gpt-5.2 default)

---

## Tasks

### Task 1: Update Tool Schemas for PheWAS Evidence
- **Files:** `src/server/core/tool_schemas.py`
- **Description:** Add optional PheWAS evidence fields to `MechanismValidation` and `SharedGene` to accommodate cross-referencing from PheWAS Catalog.
- **Context:** The Agent needs to know if a gene-disease association is backed by PheWAS data.

### Task 2: Implement PheWAS API Client
- **Files:** `src/server/core/phewas_client.py`
- **Description:** Create a robust Python client for ExPheWAS API (`https://exphewas.statgen.org/v1/api`).
- **Endpoints to wrap:** 
    - `GET /outcome` (Search for outcome ID by EFO/Name)
    - `GET /outcome/<id>/results` (Fetch gene associations for an outcome)
    - `GET /gene/<ensembl>/results` (Fetch associations for a gene across all phenotypes)

### Task 3: Update `genetic_graph_validate_mechanism` Tool
- **Files:** `src/server/core/tools/genetic_graph_tools.py`
- **Description:** 
    - Update the tool to initialize and use `PheWASClient`.
    - Implement cross-referencing logic: Find shared genes that are significant in BOTH Open Targets AND PheWAS.
    - Update the `mechanism_summary` to include PheWAS evidence ("... and further validated by PheWAS evidence in UK Biobank").

### Task 4: Comprehensive Testing
- **Files:** `tests/unit/test_phewas_client.py`, `tests/unit/test_genetic_graph_tools_enhanced.py`
- **Description:** 
    - Unit tests for `PheWASClient` (Mock API).
    - Integration tests for `validate_mechanism` with dual-source (OT + PheWAS) validation.

### Task 5: Update SOP Implementation Log
- **Files:** `.agent/blueprints/sop.md`
- **Description:** Mark PheWAS integration as COMPLETED in the implementation log. Remove the "Future Upgrade" note.

---

## Verification Checklist
- [ ] `tool_schemas.py` updated with PheWAS fields.
- [ ] `PheWASClient` passes unit tests with 100% coverage on core methods.
- [ ] `validate_mechanism` returns evidence from both OT and PheWAS.
- [ ] SOP status updated.
