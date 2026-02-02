# Module 4 System Prompt Implementation Plan
 
> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.
 
**Goal:** Implement the Module 4 co-scientist system prompt, centralize system prompts, and add a backend recommendation agent entrypoint aligned with the SOP.
 
**Architecture:** Centralize all system prompts in a single backend module, then create a recommendation agent that builds tool context and uses the Module 4 prompt to produce a structured recommendation report. Expose a dedicated API endpoint without breaking the current UI flow.
 
**Tech Stack:** Python, FastAPI, LangChain, LangGraph, Pydantic
 
---
 
### Task 1: Centralize system prompts
 
**Files:**
- Create: `src/server/core/system_prompts.py`
- Modify: `src/server/modules/disease/agentic_study_classifier.py`
- Test: `tests/unit/test_system_prompts.py`
 
**Step 1: Write the failing test**
 
```python
def test_system_prompts_export_co_scientist_prompts():
    from src.server.core.system_prompts import (
        CO_SCIENTIST_STEP1_PROMPT,
        CO_SCIENTIST_REPORT_PROMPT
    )
    assert "Step 1: Direct Match Assessment" in CO_SCIENTIST_STEP1_PROMPT
    assert "Output Schema" in CO_SCIENTIST_REPORT_PROMPT
```
 
**Step 2: Run test to verify it fails**
 
Run: `pytest tests/unit/test_system_prompts.py::test_system_prompts_export_co_scientist_prompt -v`
Expected: FAIL with "No module named 'src.server.core.system_prompts'"
 
**Step 3: Write minimal implementation**
 
```python
CO_SCIENTIST_STEP1_PROMPT = "..."
CO_SCIENTIST_REPORT_PROMPT = "..."
STUDY_CLASSIFIER_SYSTEM_PROMPT = "..."
```
 
**Step 4: Run test to verify it passes**
 
Run: `pytest tests/unit/test_system_prompts.py::test_system_prompts_export_co_scientist_prompt -v`
Expected: PASS
 
**Step 5: Commit**
 
```bash
git add src/server/core/system_prompts.py src/server/modules/disease/agentic_study_classifier.py tests/unit/test_system_prompts.py
git commit -m "feat: centralize system prompts"
```
 
---
 
### Task 2: Add recommendation report schema and agent logic
 
**Files:**
- Modify: `src/server/modules/disease/models.py`
- Create: `src/server/modules/disease/recommendation_agent.py`
- Test: `tests/unit/test_recommendation_agent.py`
 
**Step 1: Write the failing test**
 
```python
def test_resolve_efo_id_returns_none_for_no_hits():
    from src.server.modules.disease.recommendation_agent import resolve_efo_id
    class StubClient:
        def search_diseases(self, query, page=0, size=10):
            return {"hits": []}
    assert resolve_efo_id("Example Trait", StubClient()) is None
```
 
**Step 2: Run test to verify it fails**
 
Run: `pytest tests/unit/test_recommendation_agent.py::test_resolve_efo_id_returns_none_for_no_hits -v`
Expected: FAIL with "cannot import name 'resolve_efo_id'"
 
**Step 3: Write minimal implementation**
 
```python
def resolve_efo_id(trait_name, ot_client):
    results = ot_client.search_diseases(trait_name, page=0, size=5)
    hits = results.get("hits", [])
    return hits[0].id if hits else None
```
 
**Step 4: Run test to verify it passes**
 
Run: `pytest tests/unit/test_recommendation_agent.py::test_resolve_efo_id_returns_none_for_no_hits -v`
Expected: PASS
 
**Step 5: Commit**
 
```bash
git add src/server/modules/disease/models.py src/server/modules/disease/recommendation_agent.py tests/unit/test_recommendation_agent.py
git commit -m "feat: add recommendation agent scaffolding"
```
 
---
 
### Task 3: Expose recommendation endpoint
 
**Files:**
- Modify: `src/server/main.py`
- Test: `tests/unit/test_recommendation_agent.py`
 
**Step 1: Write the failing test**
 
```python
def test_recommendation_endpoint_shape(client):
    resp = client.post("/agent/recommend", json={"trait": "Type 2 Diabetes"})
    assert resp.status_code == 200
    assert "recommendation_type" in resp.json()
```
 
**Step 2: Run test to verify it fails**
 
Run: `pytest tests/unit/test_recommendation_agent.py::test_recommendation_endpoint_shape -v`
Expected: FAIL with "404 Not Found"
 
**Step 3: Write minimal implementation**
 
```python
@app.post("/agent/recommend")
async def recommend(...):
    return report.model_dump()
```
 
**Step 4: Run test to verify it passes**
 
Run: `pytest tests/unit/test_recommendation_agent.py::test_recommendation_endpoint_shape -v`
Expected: PASS
 
**Step 5: Commit**
 
```bash
git add src/server/main.py tests/unit/test_recommendation_agent.py
git commit -m "feat: add recommendation endpoint"
```
 
---
 
### Task 4: Verification checklist
 
**Files:**
- Verify: `@.agent/skills/verification-before-completion/SKILL.md`
- Verify: `@.agent/skills/test-driven-development/SKILL.md`
 
**Step 1: Run unit tests**
 
Run: `pytest tests/unit/test_system_prompts.py tests/unit/test_recommendation_agent.py -v`
Expected: PASS
 
**Step 2: Run lint checks (if configured)**
 
Run: `python -m pytest --collect-only`
Expected: PASS
