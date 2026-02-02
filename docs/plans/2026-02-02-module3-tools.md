# Module 3 - Tools Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the 5 remaining tools defined in `sop.md` Module 3 (L352-622), following TDD and engineering constraints.

**Architecture:** Each tool is a wrapper function that:
1. Takes strongly-typed input parameters
2. Calls underlying Module 1/2 services or external APIs
3. Returns strongly-typed Pydantic models matching sop.md schemas
4. Includes error handling with structured error objects

**Tech Stack:** Python 3.11, Pydantic v2, pytest, httpx (async HTTP)

**Reference:** `.agent/blueprints/sop.md` L352-622

---

## Implementation Order (by dependency)

| Priority | Tool | Reason |
|:---|:---|:---|
| P1 | `prs_model_performance_landscape` | Pure computation, no external deps |
| P2 | `genetic_graph_verify_study_power` | Needs `get_edge_provenance()` in KG service |
| P3 | `prs_model_pgscatalog_search` (filter enhancement) | Add [Agent + UI] field filtering |
| P4 | `prs_model_domain_knowledge` | Needs constrained web search API |
| P5 | `genetic_graph_validate_mechanism` | Needs Open Targets API client |
| P6 | `pennprs_train_model` | Needs PennPRS form schema |

---

## Task 1: Create Tool Schemas (Pydantic Models)

**Files:**
- Create: `src/server/core/tool_schemas.py`
- Test: `tests/unit/test_tool_schemas.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_tool_schemas.py
import pytest
from src.server.core.tool_schemas import (
    PGSSearchResult, PGSModelSummary,
    PerformanceLandscape, MetricDistribution, TopPerformerSummary,
    NeighborResult, RankedNeighbor,
    StudyPowerResult, CorrelationProvenance,
    MechanismValidation, SharedGene,
    TrainingConfig
)

def test_pgs_model_summary_schema():
    """Test PGSModelSummary can be instantiated with required fields."""
    summary = PGSModelSummary(
        id="PGS000025",
        trait_reported="Type 2 Diabetes",
        trait_efo="type 2 diabetes mellitus",
        method_name="LDpred2",
        variants_number=100000,
        ancestry_distribution="EUR (100%)",
        publication="Smith et al. 2020",
        date_release="2020-01-01",
        samples_training="n=50000",
        performance_metrics={"auc": 0.75, "r2": 0.15},
        phenotyping_reported="Type 2 Diabetes",
        covariates="age, sex, PC1-10",
        sampleset="UKB"
    )
    assert summary.id == "PGS000025"
    assert summary.performance_metrics["auc"] == 0.75

def test_performance_landscape_schema():
    """Test PerformanceLandscape can be instantiated."""
    dist = MetricDistribution(
        min=0.5, max=0.85, median=0.7, p25=0.65, p75=0.78, missing_count=2
    )
    top = TopPerformerSummary(pgs_id="PGS000001", auc=0.85, r2=0.2, percentile_rank=98.0)
    landscape = PerformanceLandscape(
        total_models=10,
        auc_distribution=dist,
        r2_distribution=dist,
        top_performer=top,
        verdict_context="Top model is +15% above median"
    )
    assert landscape.total_models == 10
    assert landscape.top_performer.percentile_rank == 98.0

def test_neighbor_result_schema():
    """Test NeighborResult for genetic graph."""
    neighbor = RankedNeighbor(
        trait_id="Schizophrenia",
        domain="Psychiatric",
        rg_meta=0.6,
        rg_z_meta=5.2,
        h2_meta=0.8,
        transfer_score=0.288,  # 0.6^2 * 0.8
        n_correlations=3
    )
    result = NeighborResult(
        target_trait="Bipolar Disorder",
        target_h2_meta=0.7,
        neighbors=[neighbor]
    )
    assert len(result.neighbors) == 1
    assert result.neighbors[0].transfer_score == 0.288

def test_study_power_result_schema():
    """Test StudyPowerResult for edge provenance."""
    prov = CorrelationProvenance(
        study1_id=123, study1_n=50000, study1_population="EUR", study1_pmid="12345678",
        study2_id=456, study2_n=40000, study2_population="EUR", study2_pmid="87654321",
        rg=0.65, se=0.05, p=1e-10
    )
    result = StudyPowerResult(
        source_trait="Crohn's disease",
        target_trait="Ulcerative colitis",
        rg_meta=0.56,
        n_correlations=2,
        correlations=[prov]
    )
    assert result.n_correlations == 2

def test_mechanism_validation_schema():
    """Test MechanismValidation for biological evidence."""
    gene = SharedGene(
        gene_symbol="IL23R",
        gene_id="ENSG00000162594",
        source_association=0.92,
        target_association=0.87,
        druggability="High",
        pathways=["IL-17 signaling"]
    )
    validation = MechanismValidation(
        source_trait="Crohn's disease",
        target_trait="Ulcerative colitis",
        shared_genes=[gene],
        shared_pathways=["Inflammatory bowel disease pathway"],
        mechanism_summary="Both share IL23R pathogenic pathway",
        confidence_level="High"
    )
    assert len(validation.shared_genes) == 1
    assert validation.confidence_level == "High"

def test_training_config_schema():
    """Test TrainingConfig for PennPRS form."""
    config = TrainingConfig(
        target_trait="Type 2 Diabetes",
        recommended_method="LDpred2",
        method_rationale="Best for polygenic traits with large GWAS",
        gwas_summary_stats="https://example.com/gwas.txt",
        ld_reference="1000G EUR",
        ancestry="EUR",
        validation_cohort="UKB",
        agent_confidence="High",
        estimated_runtime="~2 hours"
    )
    assert config.recommended_method == "LDpred2"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_tool_schemas.py -v`
Expected: FAIL with "cannot import name 'PGSSearchResult'"

**Step 3: Write minimal implementation**

```python
# src/server/core/tool_schemas.py
"""
Tool I/O Schemas for Module 3 Tools.
Implements sop.md L352-622 Output Schema specifications.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# --- PRS Model Tools Schemas ---

class PGSModelSummary(BaseModel):
    """Summary of a PGS model with [Agent + UI] fields only."""
    id: str = Field(..., description="Unique Model ID (e.g., PGS000025)")
    trait_reported: str = Field(..., description="Original reported trait")
    trait_efo: str = Field(..., description="EFO Ontology mapping")
    method_name: str = Field(..., description="Algorithm used (e.g., LDpred2)")
    variants_number: int = Field(..., description="Count of variants in model")
    ancestry_distribution: str = Field(..., description="Ancestry breakdown")
    publication: str = Field(..., description="Publication metadata")
    date_release: str = Field(..., description="Date the score was released")
    samples_training: str = Field(..., description="Samples used for training")
    performance_metrics: Dict[str, Optional[float]] = Field(
        ..., description="Metrics (auc, r2, etc.)"
    )
    phenotyping_reported: str = Field(..., description="Phenotype description in validation")
    covariates: str = Field(..., description="Covariates used in validation")
    sampleset: Optional[str] = Field(None, description="Sample set used for validation")


class PGSSearchResult(BaseModel):
    """Result from prs_model_pgscatalog_search tool."""
    query_trait: str
    total_found: int
    after_filter: int
    models: List[PGSModelSummary]


class MetricDistribution(BaseModel):
    """Statistical distribution for a performance metric."""
    min: float
    max: float
    median: float
    p25: float
    p75: float
    missing_count: int


class TopPerformerSummary(BaseModel):
    """Summary of the top performing model."""
    pgs_id: str
    auc: Optional[float]
    r2: Optional[float]
    percentile_rank: float


class PerformanceLandscape(BaseModel):
    """Result from prs_model_performance_landscape tool."""
    total_models: int
    auc_distribution: MetricDistribution
    r2_distribution: MetricDistribution
    top_performer: TopPerformerSummary
    verdict_context: str


# --- Genetic Graph Tools Schemas ---

class RankedNeighbor(BaseModel):
    """A genetically correlated trait with ranking score."""
    trait_id: str = Field(..., description="Trait canonical name")
    domain: str = Field(..., description="Trait domain (e.g., Psychiatric)")
    rg_meta: float = Field(..., description="Meta-analyzed genetic correlation")
    rg_z_meta: float = Field(..., description="Z-score of rg")
    h2_meta: float = Field(..., description="Neighbor's meta-analyzed heritability")
    transfer_score: float = Field(..., description="rg^2 * h2 score")
    n_correlations: int = Field(..., description="Number of study-pairs aggregated")
    # NOTE: h2_se_meta, rg_se_meta, rg_p_meta intentionally omitted for token efficiency.


class NeighborResult(BaseModel):
    """Result from genetic_graph_get_neighbors tool."""
    target_trait: str
    target_h2_meta: float
    neighbors: List[RankedNeighbor]


class CorrelationProvenance(BaseModel):
    """Detailed provenance for a single correlation measurement."""
    study1_id: int
    study1_n: int
    study1_population: str
    study1_pmid: str
    study2_id: int
    study2_n: int
    study2_population: str
    study2_pmid: str
    rg: float
    se: float
    p: float


class StudyPowerResult(BaseModel):
    """Result from genetic_graph_verify_study_power tool."""
    source_trait: str
    target_trait: str
    rg_meta: float
    n_correlations: int
    correlations: List[CorrelationProvenance]


class SharedGene(BaseModel):
    """A gene shared between two traits."""
    gene_symbol: str = Field(..., description="e.g., IL23R")
    gene_id: str = Field(..., description="ENSG ID")
    source_association: float = Field(..., description="Disease A association score")
    target_association: float = Field(..., description="Disease B association score")
    druggability: str = Field(..., description="High, Medium, Low")
    pathways: List[str] = Field(default_factory=list)


class MechanismValidation(BaseModel):
    """Result from genetic_graph_validate_mechanism tool."""
    source_trait: str
    target_trait: str
    shared_genes: List[SharedGene]
    shared_pathways: List[str]
    mechanism_summary: str
    confidence_level: str  # High, Moderate, Low


# --- PennPRS Tools Schemas ---

class TrainingConfig(BaseModel):
    """Result from pennprs_train_model tool."""
    # Pre-filled by Agent
    target_trait: str
    recommended_method: str
    method_rationale: str
    
    # Form fields (editable by user)
    gwas_summary_stats: str
    ld_reference: str
    ancestry: str
    validation_cohort: Optional[str] = None
    
    # Metadata
    agent_confidence: str
    estimated_runtime: str


# --- Error Schema ---

class ToolError(BaseModel):
    """Structured error for tool failures. Supports Error Trace Retention."""
    tool_name: str
    error_type: str
    error_message: str
    context: Dict[str, Any] = Field(default_factory=dict)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_tool_schemas.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/server/core/tool_schemas.py tests/unit/test_tool_schemas.py
git commit -m "feat(module3): add tool I/O schemas per sop.md L352-622"
```

---

## Task 2: Implement `prs_model_performance_landscape` Tool

**Files:**
- Create: `src/server/core/tools/prs_model_tools.py`
- Test: `tests/unit/test_prs_model_tools.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_prs_model_tools.py
import pytest
from src.server.core.tool_schemas import PGSModelSummary, PerformanceLandscape
from src.server.core.tools.prs_model_tools import prs_model_performance_landscape

def test_performance_landscape_basic():
    """Test performance landscape calculation with basic input."""
    models = [
        PGSModelSummary(
            id="PGS001", trait_reported="T2D", trait_efo="efo", method_name="LDpred2",
            variants_number=100, ancestry_distribution="EUR", publication="Pub1",
            date_release="2020-01-01", samples_training="n=1000",
            performance_metrics={"auc": 0.75, "r2": 0.15},
            phenotyping_reported="T2D", covariates="age,sex", sampleset=None
        ),
        PGSModelSummary(
            id="PGS002", trait_reported="T2D", trait_efo="efo", method_name="PRS-CS",
            variants_number=200, ancestry_distribution="EUR", publication="Pub2",
            date_release="2021-01-01", samples_training="n=2000",
            performance_metrics={"auc": 0.80, "r2": 0.20},
            phenotyping_reported="T2D", covariates="age,sex", sampleset=None
        ),
        PGSModelSummary(
            id="PGS003", trait_reported="T2D", trait_efo="efo", method_name="C+T",
            variants_number=50, ancestry_distribution="EUR", publication="Pub3",
            date_release="2019-01-01", samples_training="n=500",
            performance_metrics={"auc": 0.70, "r2": 0.10},
            phenotyping_reported="T2D", covariates="age,sex", sampleset=None
        ),
    ]
    
    result = prs_model_performance_landscape(models)
    
    assert isinstance(result, PerformanceLandscape)
    assert result.total_models == 3
    assert result.auc_distribution.min == 0.70
    assert result.auc_distribution.max == 0.80
    assert result.auc_distribution.median == 0.75
    assert result.top_performer.pgs_id == "PGS002"
    assert result.top_performer.auc == 0.80

def test_performance_landscape_with_missing_metrics():
    """Test handling of models with missing AUC/R2."""
    models = [
        PGSModelSummary(
            id="PGS001", trait_reported="T2D", trait_efo="efo", method_name="LDpred2",
            variants_number=100, ancestry_distribution="EUR", publication="Pub1",
            date_release="2020-01-01", samples_training="n=1000",
            performance_metrics={"auc": 0.75, "r2": None},  # Missing R2
            phenotyping_reported="T2D", covariates="age,sex", sampleset=None
        ),
        PGSModelSummary(
            id="PGS002", trait_reported="T2D", trait_efo="efo", method_name="PRS-CS",
            variants_number=200, ancestry_distribution="EUR", publication="Pub2",
            date_release="2021-01-01", samples_training="n=2000",
            performance_metrics={"auc": None, "r2": 0.20},  # Missing AUC
            phenotyping_reported="T2D", covariates="age,sex", sampleset=None
        ),
    ]
    
    result = prs_model_performance_landscape(models)
    
    assert result.auc_distribution.missing_count == 1
    assert result.r2_distribution.missing_count == 1

def test_performance_landscape_empty_input():
    """Test handling of empty model list."""
    result = prs_model_performance_landscape([])
    
    assert result.total_models == 0
    assert result.verdict_context == "No models available for analysis"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_prs_model_tools.py -v`
Expected: FAIL with "cannot import name 'prs_model_performance_landscape'"

**Step 3: Write minimal implementation**

```python
# src/server/core/tools/prs_model_tools.py
"""
PRS Model Tools for Module 3.
Implements sop.md L356-462 tool specifications.
"""
from typing import List, Optional
from statistics import median, quantiles
from src.server.core.tool_schemas import (
    PGSModelSummary, PerformanceLandscape, MetricDistribution, TopPerformerSummary
)


def prs_model_performance_landscape(models: List[PGSModelSummary]) -> PerformanceLandscape:
    """
    Calculate statistical distributions across all retrieved candidate models.
    
    Implements sop.md L430-462 specification.
    Token Budget: ~200 tokens.
    
    Args:
        models: Filtered models from prs_model_pgscatalog_search
        
    Returns:
        PerformanceLandscape with distributions and top performer
    """
    if not models:
        return PerformanceLandscape(
            total_models=0,
            auc_distribution=MetricDistribution(
                min=0, max=0, median=0, p25=0, p75=0, missing_count=0
            ),
            r2_distribution=MetricDistribution(
                min=0, max=0, median=0, p25=0, p75=0, missing_count=0
            ),
            top_performer=TopPerformerSummary(pgs_id="N/A", auc=None, r2=None, percentile_rank=0),
            verdict_context="No models available for analysis"
        )
    
    # Extract metrics, handling None values
    auc_values = []
    r2_values = []
    auc_missing = 0
    r2_missing = 0
    
    for m in models:
        auc = m.performance_metrics.get("auc")
        r2 = m.performance_metrics.get("r2")
        
        if auc is not None:
            auc_values.append((m.id, auc))
        else:
            auc_missing += 1
            
        if r2 is not None:
            r2_values.append((m.id, r2))
        else:
            r2_missing += 1
    
    # Calculate AUC distribution
    auc_distribution = _calculate_distribution([v for _, v in auc_values], auc_missing)
    r2_distribution = _calculate_distribution([v for _, v in r2_values], r2_missing)
    
    # Find top performer (by AUC, fallback to R2)
    top_performer = _find_top_performer(auc_values, r2_values)
    
    # Generate verdict context
    if auc_values:
        best_auc = max(v for _, v in auc_values)
        median_auc = auc_distribution.median
        pct_above = ((best_auc - median_auc) / median_auc * 100) if median_auc > 0 else 0
        verdict = f"Top model is +{pct_above:.0f}% above median AUC"
    else:
        verdict = "Performance data limited"
    
    return PerformanceLandscape(
        total_models=len(models),
        auc_distribution=auc_distribution,
        r2_distribution=r2_distribution,
        top_performer=top_performer,
        verdict_context=verdict
    )


def _calculate_distribution(values: List[float], missing_count: int) -> MetricDistribution:
    """Calculate statistical distribution for a list of values."""
    if not values:
        return MetricDistribution(
            min=0, max=0, median=0, p25=0, p75=0, missing_count=missing_count
        )
    
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    
    if n >= 4:
        q = quantiles(sorted_vals, n=4)
        p25, med, p75 = q[0], q[1], q[2]
    elif n >= 2:
        med = median(sorted_vals)
        p25 = sorted_vals[0]
        p75 = sorted_vals[-1]
    else:
        med = sorted_vals[0]
        p25 = p75 = med
    
    return MetricDistribution(
        min=min(sorted_vals),
        max=max(sorted_vals),
        median=med,
        p25=p25,
        p75=p75,
        missing_count=missing_count
    )


def _find_top_performer(
    auc_values: List[tuple], 
    r2_values: List[tuple]
) -> TopPerformerSummary:
    """Find the top performing model by AUC (preferred) or R2."""
    if auc_values:
        top_id, top_auc = max(auc_values, key=lambda x: x[1])
        # Find corresponding R2
        r2_map = dict(r2_values)
        top_r2 = r2_map.get(top_id)
        # Calculate percentile
        all_aucs = [v for _, v in auc_values]
        rank = sum(1 for v in all_aucs if v <= top_auc) / len(all_aucs) * 100
    elif r2_values:
        top_id, top_r2 = max(r2_values, key=lambda x: x[1])
        top_auc = None
        all_r2s = [v for _, v in r2_values]
        rank = sum(1 for v in all_r2s if v <= top_r2) / len(all_r2s) * 100
    else:
        return TopPerformerSummary(pgs_id="N/A", auc=None, r2=None, percentile_rank=0)
    
    return TopPerformerSummary(
        pgs_id=top_id,
        auc=top_auc,
        r2=top_r2,
        percentile_rank=rank
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_prs_model_tools.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/server/core/tools/__init__.py src/server/core/tools/prs_model_tools.py tests/unit/test_prs_model_tools.py
git commit -m "feat(module3): implement prs_model_performance_landscape tool"
```

---

## Task 3: Implement `get_edge_provenance()` in KnowledgeGraphService

**Files:**
- Modify: `src/server/modules/knowledge_graph/service.py`
- Test: `tests/unit/test_knowledge_graph_enhanced.py`

**Step 1: Write the failing test**

```python
# Add to tests/unit/test_knowledge_graph_enhanced.py

def test_get_edge_provenance_returns_study_pairs(knowledge_graph_service):
    """Test get_edge_provenance returns detailed study-pair data."""
    # Use traits known to have correlations in test data
    result = knowledge_graph_service.get_edge_provenance(
        source_trait="Schizophrenia",
        target_trait="Bipolar disorder"
    )
    
    assert result is not None
    assert hasattr(result, 'source_trait')
    assert hasattr(result, 'target_trait')
    assert hasattr(result, 'rg_meta')
    assert hasattr(result, 'correlations')
    assert isinstance(result.correlations, list)
    # Each correlation should have study metadata
    if result.correlations:
        corr = result.correlations[0]
        assert hasattr(corr, 'study1_id')
        assert hasattr(corr, 'study1_n')
        assert hasattr(corr, 'rg')

def test_get_edge_provenance_nonexistent_returns_none(knowledge_graph_service):
    """Test get_edge_provenance returns None for non-existent edge."""
    result = knowledge_graph_service.get_edge_provenance(
        source_trait="NonExistent1",
        target_trait="NonExistent2"
    )
    assert result is None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_knowledge_graph_enhanced.py::test_get_edge_provenance_returns_study_pairs -v`
Expected: FAIL with "AttributeError: 'KnowledgeGraphService' object has no attribute 'get_edge_provenance'"

**Step 3: Write minimal implementation**

Add to `src/server/modules/knowledge_graph/service.py`:

```python
def get_edge_provenance(
    self,
    source_trait: str,
    target_trait: str
) -> Optional[StudyPowerResult]:
    """
    Get detailed study-pair provenance for a specific genetic correlation edge.
    
    Implements sop.md Module 3 genetic_graph_verify_study_power dependency.
    JIT Loading: Only called when Agent needs deep quality control.
    
    Args:
        source_trait: Source trait canonical name
        target_trait: Target trait canonical name
        
    Returns:
        StudyPowerResult with correlation provenance, or None if edge not found
    """
    # Get raw correlations between these traits
    correlations_df = self.gc_client.get_correlations_for_trait(source_trait)
    
    if correlations_df.empty:
        return None
    
    # Filter to edges involving target_trait
    edge_correlations = correlations_df[
        correlations_df['trait2'].str.lower() == target_trait.lower()
    ]
    
    if edge_correlations.empty:
        return None
    
    # Build provenance list
    from src.server.core.tool_schemas import StudyPowerResult, CorrelationProvenance
    
    provenance_list = []
    for _, row in edge_correlations.iterrows():
        # Get study metadata from heritability data
        study1_meta = self._get_study_metadata(row.get('id1', 0))
        study2_meta = self._get_study_metadata(row.get('id2', 0))
        
        prov = CorrelationProvenance(
            study1_id=int(row.get('id1', 0)),
            study1_n=study1_meta.get('n', 0),
            study1_population=study1_meta.get('population', 'Unknown'),
            study1_pmid=study1_meta.get('pmid', ''),
            study2_id=int(row.get('id2', 0)),
            study2_n=study2_meta.get('n', 0),
            study2_population=study2_meta.get('population', 'Unknown'),
            study2_pmid=study2_meta.get('pmid', ''),
            rg=float(row.get('rg', 0)),
            se=float(row.get('se', 0)),
            p=float(row.get('p', 1))
        )
        provenance_list.append(prov)
    
    # Calculate meta-analyzed rg
    from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
    rg_values = [(p.rg, p.se) for p in provenance_list if p.se > 0]
    if rg_values:
        rg_meta, _, _ = inverse_variance_meta_analysis(
            [v for v, _ in rg_values],
            [s for _, s in rg_values]
        )
    else:
        rg_meta = provenance_list[0].rg if provenance_list else 0

    return StudyPowerResult(
        source_trait=source_trait,
        target_trait=target_trait,
        rg_meta=rg_meta,
        n_correlations=len(provenance_list),
        correlations=provenance_list
    )

def _get_study_metadata(self, study_id: int) -> dict:
    """Get study metadata (n, population, pmid) from heritability data."""
    if not hasattr(self, '_study_cache'):
        # Build cache from heritability data
        self._study_cache = {}
        if self.h2_client:
            h2_data = self.h2_client.get_all_estimates()
            for est in h2_data:
                self._study_cache[est.study_id] = {
                    'n': est.sample_size,
                    'population': getattr(est, 'population', 'Unknown'),
                    'pmid': getattr(est, 'pmid', '')
                }
    return self._study_cache.get(study_id, {'n': 0, 'population': 'Unknown', 'pmid': ''})
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_knowledge_graph_enhanced.py::test_get_edge_provenance_returns_study_pairs -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/server/modules/knowledge_graph/service.py tests/unit/test_knowledge_graph_enhanced.py
git commit -m "feat(module3): implement get_edge_provenance for verify_study_power tool"
```

---

## Task 4: Implement `genetic_graph_verify_study_power` Tool Wrapper

**Files:**
- Create: `src/server/core/tools/genetic_graph_tools.py`
- Test: `tests/unit/test_genetic_graph_tools.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_genetic_graph_tools.py
import pytest
from unittest.mock import Mock, MagicMock
from src.server.core.tool_schemas import StudyPowerResult, CorrelationProvenance
from src.server.core.tools.genetic_graph_tools import genetic_graph_verify_study_power

@pytest.fixture
def mock_kg_service():
    """Create mock KnowledgeGraphService."""
    service = Mock()
    service.get_edge_provenance.return_value = StudyPowerResult(
        source_trait="Schizophrenia",
        target_trait="Bipolar disorder",
        rg_meta=0.65,
        n_correlations=2,
        correlations=[
            CorrelationProvenance(
                study1_id=123, study1_n=50000, study1_population="EUR", study1_pmid="12345",
                study2_id=456, study2_n=40000, study2_population="EUR", study2_pmid="67890",
                rg=0.60, se=0.05, p=1e-8
            )
        ]
    )
    return service

def test_verify_study_power_returns_result(mock_kg_service):
    """Test tool wrapper calls service and returns result."""
    result = genetic_graph_verify_study_power(
        mock_kg_service,
        source_trait="Schizophrenia",
        target_trait="Bipolar disorder"
    )
    
    assert isinstance(result, StudyPowerResult)
    assert result.source_trait == "Schizophrenia"
    assert result.n_correlations == 2
    mock_kg_service.get_edge_provenance.assert_called_once_with(
        source_trait="Schizophrenia",
        target_trait="Bipolar disorder"
    )

def test_verify_study_power_handles_none():
    """Test tool returns ToolError when edge not found."""
    from src.server.core.tool_schemas import ToolError
    
    service = Mock()
    service.get_edge_provenance.return_value = None
    
    result = genetic_graph_verify_study_power(
        service,
        source_trait="NonExistent",
        target_trait="AlsoNonExistent"
    )
    
    assert isinstance(result, ToolError)
    assert result.tool_name == "genetic_graph_verify_study_power"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_genetic_graph_tools.py -v`
Expected: FAIL with "cannot import name 'genetic_graph_verify_study_power'"

**Step 3: Write minimal implementation**

```python
# src/server/core/tools/genetic_graph_tools.py
"""
Genetic Graph Tools for Module 3.
Implements sop.md L464-562 tool specifications.
"""
from typing import Union
from src.server.core.tool_schemas import (
    StudyPowerResult, NeighborResult, RankedNeighbor, ToolError
)


def genetic_graph_verify_study_power(
    kg_service,  # KnowledgeGraphService
    source_trait: str,
    target_trait: str
) -> Union[StudyPowerResult, ToolError]:
    """
    Fetch detailed study-pair provenance for a genetic correlation edge.
    
    Implements sop.md L497-530 specification.
    JIT Loading: Only called when Agent needs deep quality control.
    Token Budget: ~300 tokens.
    
    Args:
        kg_service: KnowledgeGraphService instance
        source_trait: Source trait canonical name
        target_trait: Target trait canonical name
        
    Returns:
        StudyPowerResult with provenance, or ToolError if edge not found
    """
    try:
        result = kg_service.get_edge_provenance(
            source_trait=source_trait,
            target_trait=target_trait
        )
        
        if result is None:
            return ToolError(
                tool_name="genetic_graph_verify_study_power",
                error_type="EdgeNotFound",
                error_message=f"No genetic correlation edge found between '{source_trait}' and '{target_trait}'",
                context={"source_trait": source_trait, "target_trait": target_trait}
            )
        
        return result
        
    except Exception as e:
        return ToolError(
            tool_name="genetic_graph_verify_study_power",
            error_type=type(e).__name__,
            error_message=str(e),
            context={"source_trait": source_trait, "target_trait": target_trait}
        )


def genetic_graph_get_neighbors(
    kg_service,  # KnowledgeGraphService
    trait_id: str,
    rg_z_threshold: float = 2.0,
    h2_z_threshold: float = 2.0,
    limit: int = 10
) -> Union[NeighborResult, ToolError]:
    """
    Get pre-ranked genetically correlated traits.
    
    Implements sop.md L464-495 specification.
    Auto-sorted by rg^2 * h2 (descending).
    Token Budget: ~100 tokens per neighbor.
    
    Args:
        kg_service: KnowledgeGraphService instance
        trait_id: Target trait canonical name
        rg_z_threshold: Minimum |rg_z_meta| (default 2.0)
        h2_z_threshold: Minimum h2_z_meta (default 2.0)
        limit: Maximum neighbors to return (default 10)
        
    Returns:
        NeighborResult with ranked neighbors, or ToolError on failure
    """
    try:
        # Call existing v2 method
        graph_result = kg_service.get_prioritized_neighbors_v2(
            trait_id=trait_id,
            rg_z_threshold=rg_z_threshold,
            h2_z_threshold=h2_z_threshold
        )
        
        if graph_result is None:
            return ToolError(
                tool_name="genetic_graph_get_neighbors",
                error_type="TraitNotFound",
                error_message=f"Trait '{trait_id}' not found in Knowledge Graph",
                context={"trait_id": trait_id}
            )
        
        # Get target trait h2
        target_node = kg_service.get_trait_node(trait_id)
        target_h2 = target_node.h2_meta if target_node else 0.0
        
        # Convert to tool output schema
        neighbors = []
        for node, edge in graph_result.neighbors[:limit]:
            neighbor = RankedNeighbor(
                trait_id=node.trait_id,
                domain=node.domain or "Unknown",
                rg_meta=edge.rg_meta,
                rg_z_meta=edge.rg_z_meta,
                h2_meta=node.h2_meta,
                transfer_score=edge.rg_meta ** 2 * node.h2_meta,
                n_correlations=edge.n_correlations
            )
            neighbors.append(neighbor)
        
        return NeighborResult(
            target_trait=trait_id,
            target_h2_meta=target_h2,
            neighbors=neighbors
        )
        
    except Exception as e:
        return ToolError(
            tool_name="genetic_graph_get_neighbors",
            error_type=type(e).__name__,
            error_message=str(e),
            context={"trait_id": trait_id}
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_genetic_graph_tools.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/server/core/tools/genetic_graph_tools.py tests/unit/test_genetic_graph_tools.py
git commit -m "feat(module3): implement genetic_graph_verify_study_power and get_neighbors tools"
```

---

## Task 5: Implement `prs_model_pgscatalog_search` Filter Enhancement

**Files:**
- Modify: `src/server/core/tools/prs_model_tools.py`
- Test: `tests/unit/test_prs_model_tools.py`

**Step 1: Write the failing test**

```python
# Add to tests/unit/test_prs_model_tools.py

def test_pgscatalog_search_filters_empty_metrics():
    """Test that models with both AUC and R2 null are filtered out."""
    from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search
    from unittest.mock import Mock
    
    # Mock PGSCatalogClient
    mock_client = Mock()
    mock_client.search_scores.return_value = [
        {"id": "PGS001"},
        {"id": "PGS002"},
        {"id": "PGS003"},
    ]
    
    # Mock get_score_details and get_score_performance
    def mock_details(pgs_id):
        return {
            "id": pgs_id,
            "trait_reported": "T2D",
            "trait_efo": [{"label": "T2D"}],
            "method_name": "LDpred2",
            "variants_number": 100,
            "ancestry_distribution": {"gwas": {"EUR": 1.0}},
            "publication": {"title": "Test"},
            "date_release": "2020-01-01",
            "samples_training": [{"sample_number": 1000}],
        }
    
    def mock_performance(pgs_id):
        if pgs_id == "PGS001":
            return [{"effect_sizes": [{"name_short": "AUC", "estimate": 0.75}]}]
        elif pgs_id == "PGS002":
            return [{"effect_sizes": [{"name_short": "R²", "estimate": 0.15}]}]
        else:  # PGS003 has no metrics
            return [{"effect_sizes": []}]
    
    mock_client.get_score_details.side_effect = mock_details
    mock_client.get_score_performance.side_effect = mock_performance
    
    result = prs_model_pgscatalog_search(mock_client, "Type 2 Diabetes")
    
    assert result.total_found == 3
    assert result.after_filter == 2  # PGS003 filtered out
    assert len(result.models) == 2
    assert all(m.id in ["PGS001", "PGS002"] for m in result.models)
```

**Step 2-5:** Follow TDD cycle as above.

---

## Task 6 (Future): `prs_model_domain_knowledge`

Requires:
- Google Custom Search API setup
- Domain whitelist configuration
- Snippet extraction and summarization

**Deferred until API credentials available.**

---

## Task 7 (Future): `genetic_graph_validate_mechanism`

Requires:
- Open Targets Platform API client
- PheWAS Catalog integration
- Gene/pathway mapping logic

**Deferred until API integration complete.**

---

## Task 8 (Future): `pennprs_train_model`

Requires:
- PennPRS API form schema definition
- Form field mapping logic

**Deferred until PennPRS integration ready.**

---

## Verification Checklist

Before marking Module 3 complete:

- [ ] All schema tests pass
- [ ] `prs_model_performance_landscape` test passes
- [ ] `genetic_graph_verify_study_power` test passes
- [ ] `genetic_graph_get_neighbors` tool wrapper test passes
- [ ] `prs_model_pgscatalog_search` filter test passes
- [ ] All existing tests still pass (`pytest tests/ -v`)
- [ ] Tools directory has `__init__.py` with exports
- [ ] sop.md Implementation Status updated

---

## Execution Note

**Plan complete. Two execution options:**

1. **Subagent-Driven (this session)** - Dispatch fresh subagent per task, review between tasks
2. **Parallel Session (separate)** - Open new session with executing-plans

**Which approach?**
