# Module 2: Trait-Centric Knowledge Graph Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor the Knowledge Graph to use Trait-level nodes with Meta-Analysis aggregation for both $h^2$ and $r_g$, retaining full Study provenance.

**Architecture:** The current implementation operates at Study-level (each GWAS Atlas `id` is a separate node). The new design aggregates Studies by `uniqTrait`, applying inverse-variance weighted meta-analysis to consolidate multiple estimates. Nodes store `h2_meta` and `studies[]`, edges store `rg_meta` and `correlations[]`.

**Tech Stack:** Python, Pydantic, Pandas, pytest, scipy.stats

---

## Task 1: Define New Data Models

**Files:**
- Modify: `src/server/modules/knowledge_graph/models.py`
- Test: `tests/unit/test_knowledge_graph_models.py`

### Step 1: Write the failing test

Create `tests/unit/test_knowledge_graph_models.py`:

```python
"""
Unit Tests for Module 2: Knowledge Graph Models.
Tests the new Trait-Centric data models with Meta-Analysis fields.
"""
import pytest
from pydantic import ValidationError


def test_trait_node_has_meta_analyzed_fields():
    """Test that TraitNode model includes h2_meta, h2_se_meta, h2_z_meta, n_studies, studies."""
    from src.server.modules.knowledge_graph.models import TraitNode
    
    node = TraitNode(
        trait_id="Schizophrenia",
        domain="Psychiatric",
        chapter_level="Mental Disorders",
        h2_meta=0.45,
        h2_se_meta=0.03,
        h2_z_meta=15.0,
        n_studies=4,
        studies=[
            {"study_id": 9, "pmid": "21926974", "n": 21856, "snp_h2": 0.55, "snp_h2_se": 0.04}
        ]
    )
    
    assert node.trait_id == "Schizophrenia"
    assert node.h2_meta == 0.45
    assert node.h2_z_meta == 15.0
    assert node.n_studies == 4
    assert len(node.studies) == 1


def test_genetic_correlation_edge_has_meta_analyzed_fields():
    """Test that GeneticCorrelationEdgeMeta model includes rg_meta, rg_se_meta, rg_z_meta, rg_p_meta."""
    from src.server.modules.knowledge_graph.models import GeneticCorrelationEdgeMeta
    
    edge = GeneticCorrelationEdgeMeta(
        source_trait="Schizophrenia",
        target_trait="Bipolar disorder",
        rg_meta=0.68,
        rg_se_meta=0.04,
        rg_z_meta=17.0,
        rg_p_meta=1e-30,
        n_correlations=12,
        correlations=[
            {"source_study_id": 9, "target_study_id": 5, "rg": 0.65, "se": 0.05, "p": 0.001}
        ]
    )
    
    assert edge.source_trait == "Schizophrenia"
    assert edge.rg_meta == 0.68
    assert edge.rg_z_meta == 17.0
    assert edge.n_correlations == 12
```

### Step 2: Run test to verify it fails

Run: `pytest tests/unit/test_knowledge_graph_models.py -v`
Expected: FAIL with "cannot import name 'TraitNode' from 'src.server.modules.knowledge_graph.models'"

### Step 3: Write minimal implementation

Modify `src/server/modules/knowledge_graph/models.py`:

```python
"""
Data Models for Knowledge Graph (Module 2).
Implements Trait-Centric schema with Meta-Analysis aggregation per sop.md.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StudyProvenance(BaseModel):
    """Individual study data for provenance tracking."""
    study_id: int = Field(..., description="GWAS Atlas numeric ID")
    pmid: Optional[str] = Field(None, description="PubMed Identifier")
    year: Optional[int] = Field(None, description="Publication year")
    population: Optional[str] = Field(None, description="Ancestry")
    n: Optional[int] = Field(None, description="Sample size")
    snp_h2: Optional[float] = Field(None, description="SNP heritability estimate")
    snp_h2_se: Optional[float] = Field(None, description="SE of h2")
    snp_h2_z: Optional[float] = Field(None, description="Z-score of h2")
    consortium: Optional[str] = Field(None, description="Research consortium")


class TraitNode(BaseModel):
    """
    Represents a Trait Node with meta-analyzed heritability.
    Each Trait has exactly ONE node, aggregating ALL Study information.
    """
    trait_id: str = Field(..., description="Canonical trait name (uniqTrait). Primary Key.")
    domain: Optional[str] = Field(None, description="Top-level category (e.g., Psychiatric)")
    chapter_level: Optional[str] = Field(None, description="ICD-10 chapter classification")
    h2_meta: Optional[float] = Field(None, description="Meta-analyzed h2 (inverse-variance weighted)")
    h2_se_meta: Optional[float] = Field(None, description="SE of meta-analyzed h2")
    h2_z_meta: Optional[float] = Field(None, description="Z-score of meta-analyzed h2")
    n_studies: int = Field(0, description="Number of Studies aggregated")
    studies: List[Dict[str, Any]] = Field(default_factory=list, description="All Studies for provenance")


class CorrelationProvenance(BaseModel):
    """Individual study-pair correlation for provenance tracking."""
    source_study_id: int = Field(..., description="Source study GWAS Atlas ID")
    target_study_id: int = Field(..., description="Target study GWAS Atlas ID")
    rg: float = Field(..., description="Genetic correlation coefficient")
    se: Optional[float] = Field(None, description="Standard error")
    z: Optional[float] = Field(None, description="Z-score")
    p: Optional[float] = Field(None, description="P-value")


class GeneticCorrelationEdgeMeta(BaseModel):
    """
    Represents a Genetic Correlation Edge with meta-analyzed rg.
    Each Trait-pair has exactly ONE edge, aggregating ALL Study-pair correlations.
    """
    source_trait: str = Field(..., description="Source trait canonical name")
    target_trait: str = Field(..., description="Target trait canonical name")
    rg_meta: float = Field(..., description="Meta-analyzed rg (inverse-variance weighted)")
    rg_se_meta: Optional[float] = Field(None, description="SE of meta-analyzed rg")
    rg_z_meta: Optional[float] = Field(None, description="Z-score of meta-analyzed rg")
    rg_p_meta: Optional[float] = Field(None, description="P-value of meta-analyzed rg")
    n_correlations: int = Field(0, description="Number of Study-pair correlations aggregated")
    correlations: List[Dict[str, Any]] = Field(default_factory=list, description="All correlations for provenance")


class TraitCentricGraphResult(BaseModel):
    """Response model for trait-centric graph queries."""
    nodes: List[TraitNode] = Field(default_factory=list)
    edges: List[GeneticCorrelationEdgeMeta] = Field(default_factory=list)


# --- Legacy Models (preserved for backward compatibility) ---

class KnowledgeGraphNode(BaseModel):
    """ Represents a Trait Node (Legacy) """
    id: str = Field(..., description="EFO ID or Trait Name")
    label: str = Field(..., description="Display Name")
    h2: Optional[float] = Field(None, description="Heritability")


class GeneticCorrelationEdge(BaseModel):
    """ Represents a relationship edge (Legacy) """
    source: str = Field(..., description="Source Trait ID")
    target: str = Field(..., description="Target Trait ID")
    rg: float = Field(..., description="Genetic Correlation Coefficient")
    p_value: float = Field(..., description="Significance P-value")
    se: Optional[float] = Field(None, description="Standard Error")


class KnowledgeGraphResult(BaseModel):
    """ Response model for graph queries (Legacy) """
    nodes: List[KnowledgeGraphNode] = Field(default_factory=list)
    edges: List[GeneticCorrelationEdge] = Field(default_factory=list)


class PrioritizedNeighbor(BaseModel):
    """
    Represents a neighbor trait with weighted score for prioritization.
    Score = rg^2 * h2 (genetic correlation squared times heritability)
    """
    trait_id: str = Field(..., description="Trait ID (GWAS Atlas numeric ID)")
    trait_name: str = Field(..., description="Trait display name")
    rg: float = Field(..., description="Genetic correlation coefficient")
    h2: float = Field(..., description="Heritability of the correlated trait")
    score: float = Field(..., description="Weighted score: rg^2 * h2")
    p_value: float = Field(..., description="Significance P-value of genetic correlation")
```

### Step 4: Run test to verify it passes

Run: `pytest tests/unit/test_knowledge_graph_models.py -v`
Expected: PASS

### Step 5: Commit

```bash
git add tests/unit/test_knowledge_graph_models.py src/server/modules/knowledge_graph/models.py
git commit -m "feat(kg): add TraitNode and GeneticCorrelationEdgeMeta models with meta-analysis fields"
```

---

## Task 2: Implement Meta-Analysis Utility Function

**Files:**
- Create: `src/server/modules/knowledge_graph/meta_analysis.py`
- Test: `tests/unit/test_meta_analysis.py`

### Step 1: Write the failing test

Create `tests/unit/test_meta_analysis.py`:

```python
"""
Unit Tests for Meta-Analysis utility functions.
Tests the inverse-variance weighted meta-analysis formula.
"""
import pytest
import math


def test_meta_analysis_single_estimate():
    """Single estimate should return the same value."""
    from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
    
    estimates = [0.5]
    standard_errors = [0.1]
    
    result = inverse_variance_meta_analysis(estimates, standard_errors)
    
    assert result["theta_meta"] == pytest.approx(0.5, rel=1e-6)
    assert result["se_meta"] == pytest.approx(0.1, rel=1e-6)


def test_meta_analysis_two_estimates():
    """Two estimates should be weighted by inverse variance."""
    from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
    
    # Estimate 1: theta=0.4, se=0.1 -> weight = 1/0.01 = 100
    # Estimate 2: theta=0.6, se=0.2 -> weight = 1/0.04 = 25
    # theta_meta = (100*0.4 + 25*0.6) / (100 + 25) = (40 + 15) / 125 = 0.44
    # se_meta = 1/sqrt(125) = 0.0894
    estimates = [0.4, 0.6]
    standard_errors = [0.1, 0.2]
    
    result = inverse_variance_meta_analysis(estimates, standard_errors)
    
    assert result["theta_meta"] == pytest.approx(0.44, rel=1e-3)
    assert result["se_meta"] == pytest.approx(1/math.sqrt(125), rel=1e-3)
    assert result["z_meta"] == pytest.approx(0.44 / (1/math.sqrt(125)), rel=1e-3)


def test_meta_analysis_empty_input():
    """Empty input should return None values."""
    from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
    
    result = inverse_variance_meta_analysis([], [])
    
    assert result["theta_meta"] is None
    assert result["se_meta"] is None


def test_meta_analysis_skips_invalid_se():
    """Should skip estimates with zero or negative SE."""
    from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis
    
    estimates = [0.5, 0.6, 0.7]
    standard_errors = [0.1, 0.0, -0.1]  # Only first is valid
    
    result = inverse_variance_meta_analysis(estimates, standard_errors)
    
    assert result["theta_meta"] == pytest.approx(0.5, rel=1e-6)
    assert result["n_valid"] == 1
```

### Step 2: Run test to verify it fails

Run: `pytest tests/unit/test_meta_analysis.py -v`
Expected: FAIL with "cannot import name 'inverse_variance_meta_analysis'"

### Step 3: Write minimal implementation

Create `src/server/modules/knowledge_graph/meta_analysis.py`:

```python
"""
Meta-Analysis Utilities for Knowledge Graph.
Implements inverse-variance weighted meta-analysis formula per sop.md.

Formula:
    theta_meta = sum(w_i * theta_i) / sum(w_i), where w_i = 1/SE_i^2
    SE_meta = 1 / sqrt(sum(w_i))
    Z_meta = theta_meta / SE_meta
    P_meta = 2 * Phi(-|Z_meta|)
"""
import math
from typing import List, Dict, Any, Optional
from scipy import stats


def inverse_variance_meta_analysis(
    estimates: List[float],
    standard_errors: List[float]
) -> Dict[str, Any]:
    """
    Perform fixed-effect inverse-variance weighted meta-analysis.
    
    Args:
        estimates: List of effect estimates (h2 or rg values)
        standard_errors: List of corresponding standard errors
        
    Returns:
        Dictionary with:
            - theta_meta: Meta-analyzed estimate
            - se_meta: Standard error of meta-analyzed estimate
            - z_meta: Z-score
            - p_meta: Two-tailed P-value
            - n_valid: Number of valid estimates used
    """
    if len(estimates) != len(standard_errors):
        raise ValueError("estimates and standard_errors must have same length")
    
    # Filter valid pairs (SE > 0)
    valid_pairs = [
        (est, se) for est, se in zip(estimates, standard_errors)
        if se is not None and se > 0 and est is not None and not math.isnan(est) and not math.isnan(se)
    ]
    
    n_valid = len(valid_pairs)
    
    if n_valid == 0:
        return {
            "theta_meta": None,
            "se_meta": None,
            "z_meta": None,
            "p_meta": None,
            "n_valid": 0
        }
    
    # Calculate weights and weighted sum
    weights = [1.0 / (se ** 2) for _, se in valid_pairs]
    sum_weights = sum(weights)
    
    theta_meta = sum(w * est for (est, _), w in zip(valid_pairs, weights)) / sum_weights
    se_meta = 1.0 / math.sqrt(sum_weights)
    z_meta = theta_meta / se_meta
    p_meta = 2 * stats.norm.sf(abs(z_meta))  # Two-tailed
    
    return {
        "theta_meta": theta_meta,
        "se_meta": se_meta,
        "z_meta": z_meta,
        "p_meta": p_meta,
        "n_valid": n_valid
    }
```

### Step 4: Run test to verify it passes

Run: `pytest tests/unit/test_meta_analysis.py -v`
Expected: PASS

### Step 5: Commit

```bash
git add tests/unit/test_meta_analysis.py src/server/modules/knowledge_graph/meta_analysis.py
git commit -m "feat(kg): add inverse-variance weighted meta-analysis utility"
```

---

## Task 3: Implement Trait Aggregator

**Files:**
- Create: `src/server/modules/knowledge_graph/trait_aggregator.py`
- Test: `tests/unit/test_trait_aggregator.py`

### Step 1: Write the failing test

Create `tests/unit/test_trait_aggregator.py`:

```python
"""
Unit Tests for Trait Aggregator.
Tests grouping Studies by uniqTrait and applying meta-analysis.
"""
import pytest
import pandas as pd


def test_aggregate_heritability_by_trait():
    """Test aggregating multiple studies for the same trait."""
    from src.server.modules.knowledge_graph.trait_aggregator import TraitAggregator
    
    # Create mock heritability dataframe with 3 studies for "Schizophrenia"
    h2_data = pd.DataFrame({
        "id": [9, 10, 11],
        "uniqTrait": ["Schizophrenia", "Schizophrenia", "Schizophrenia"],
        "Domain": ["Psychiatric", "Psychiatric", "Psychiatric"],
        "ChapterLevel": ["Mental", "Mental", "Mental"],
        "PMID": ["111", "222", "333"],
        "N": [10000, 20000, 30000],
        "SNPh2": [0.5, 0.45, 0.48],
        "SNPh2_se": [0.05, 0.04, 0.03],
        "SNPh2_z": [10.0, 11.25, 16.0]
    })
    
    aggregator = TraitAggregator(h2_df=h2_data)
    
    result = aggregator.get_trait_node("Schizophrenia")
    
    assert result is not None
    assert result.trait_id == "Schizophrenia"
    assert result.n_studies == 3
    assert len(result.studies) == 3
    assert result.h2_meta is not None
    assert result.h2_z_meta is not None


def test_aggregate_heritability_trait_not_found():
    """Test that None is returned for unknown trait."""
    from src.server.modules.knowledge_graph.trait_aggregator import TraitAggregator
    
    h2_data = pd.DataFrame({
        "id": [1],
        "uniqTrait": ["Diabetes"],
        "SNPh2": [0.3],
        "SNPh2_se": [0.05]
    })
    
    aggregator = TraitAggregator(h2_df=h2_data)
    
    result = aggregator.get_trait_node("Unknown Trait")
    
    assert result is None


def test_get_all_trait_ids():
    """Test getting list of all unique trait IDs."""
    from src.server.modules.knowledge_graph.trait_aggregator import TraitAggregator
    
    h2_data = pd.DataFrame({
        "id": [1, 2, 3],
        "uniqTrait": ["Trait A", "Trait A", "Trait B"],
        "SNPh2": [0.3, 0.4, 0.5],
        "SNPh2_se": [0.05, 0.06, 0.07]
    })
    
    aggregator = TraitAggregator(h2_df=h2_data)
    
    traits = aggregator.get_all_trait_ids()
    
    assert len(traits) == 2
    assert "Trait A" in traits
    assert "Trait B" in traits
```

### Step 2: Run test to verify it fails

Run: `pytest tests/unit/test_trait_aggregator.py -v`
Expected: FAIL with "cannot import name 'TraitAggregator'"

### Step 3: Write minimal implementation

Create `src/server/modules/knowledge_graph/trait_aggregator.py`:

```python
"""
Trait Aggregator for Knowledge Graph.
Groups Studies by uniqTrait and applies meta-analysis to create TraitNodes.
"""
import pandas as pd
import logging
from typing import Optional, List, Dict, Any

from src.server.modules.knowledge_graph.models import TraitNode
from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis

logger = logging.getLogger(__name__)


class TraitAggregator:
    """
    Aggregates Study-level data by Trait (uniqTrait).
    Creates TraitNode objects with meta-analyzed h2 and full study provenance.
    """
    
    def __init__(self, h2_df: pd.DataFrame):
        """
        Initialize with heritability DataFrame.
        
        Args:
            h2_df: DataFrame with columns including 'uniqTrait', 'SNPh2', 'SNPh2_se', etc.
        """
        self._df = h2_df
        self._trait_groups = None
        self._preprocess()
    
    def _preprocess(self):
        """Group studies by uniqTrait."""
        if self._df.empty:
            self._trait_groups = {}
            return
        
        if 'uniqTrait' not in self._df.columns:
            logger.warning("'uniqTrait' column not found in DataFrame")
            self._trait_groups = {}
            return
            
        self._trait_groups = {
            name: group for name, group in self._df.groupby('uniqTrait')
        }
    
    def get_all_trait_ids(self) -> List[str]:
        """Get list of all unique trait IDs."""
        return list(self._trait_groups.keys())
    
    def get_trait_node(self, trait_id: str) -> Optional[TraitNode]:
        """
        Get aggregated TraitNode for a given trait ID.
        
        Args:
            trait_id: Trait canonical name (uniqTrait)
            
        Returns:
            TraitNode with meta-analyzed h2 and study provenance, or None if not found
        """
        if trait_id not in self._trait_groups:
            return None
        
        group = self._trait_groups[trait_id]
        
        # Extract h2 estimates and SEs
        estimates = group['SNPh2'].dropna().tolist()
        ses = group['SNPh2_se'].dropna().tolist() if 'SNPh2_se' in group.columns else []
        
        # Ensure same length
        min_len = min(len(estimates), len(ses)) if ses else 0
        estimates = estimates[:min_len]
        ses = ses[:min_len]
        
        # Apply meta-analysis
        if estimates and ses:
            meta_result = inverse_variance_meta_analysis(estimates, ses)
        else:
            meta_result = {"theta_meta": None, "se_meta": None, "z_meta": None, "n_valid": 0}
        
        # Build study provenance
        studies = []
        for _, row in group.iterrows():
            study = {
                "study_id": int(row['id']) if pd.notna(row.get('id')) else None,
                "pmid": str(row.get('PMID', '')) if pd.notna(row.get('PMID')) else None,
                "n": int(row['N']) if pd.notna(row.get('N')) else None,
                "snp_h2": float(row['SNPh2']) if pd.notna(row.get('SNPh2')) else None,
                "snp_h2_se": float(row['SNPh2_se']) if pd.notna(row.get('SNPh2_se')) else None,
                "snp_h2_z": float(row['SNPh2_z']) if pd.notna(row.get('SNPh2_z')) else None,
            }
            studies.append(study)
        
        # Get domain and chapter from first row
        first_row = group.iloc[0]
        domain = str(first_row.get('Domain', '')) if pd.notna(first_row.get('Domain')) else None
        chapter = str(first_row.get('ChapterLevel', '')) if pd.notna(first_row.get('ChapterLevel')) else None
        
        return TraitNode(
            trait_id=trait_id,
            domain=domain,
            chapter_level=chapter,
            h2_meta=meta_result["theta_meta"],
            h2_se_meta=meta_result["se_meta"],
            h2_z_meta=meta_result["z_meta"],
            n_studies=len(studies),
            studies=studies
        )
```

### Step 4: Run test to verify it passes

Run: `pytest tests/unit/test_trait_aggregator.py -v`
Expected: PASS

### Step 5: Commit

```bash
git add tests/unit/test_trait_aggregator.py src/server/modules/knowledge_graph/trait_aggregator.py
git commit -m "feat(kg): add TraitAggregator for grouping studies by uniqTrait with meta-analysis"
```

---

## Task 4: Implement Edge Aggregator

**Files:**
- Create: `src/server/modules/knowledge_graph/edge_aggregator.py`
- Test: `tests/unit/test_edge_aggregator.py`

### Step 1: Write the failing test

Create `tests/unit/test_edge_aggregator.py`:

```python
"""
Unit Tests for Edge Aggregator.
Tests grouping Study-pair correlations by Trait-pair and applying meta-analysis.
"""
import pytest
import pandas as pd


def test_aggregate_edges_by_trait_pair():
    """Test aggregating multiple study-pair edges into one trait-pair edge."""
    from src.server.modules.knowledge_graph.edge_aggregator import EdgeAggregator
    
    # Create mock GC dataframe: 2 study-pairs between same trait-pair
    gc_data = pd.DataFrame({
        "id1": [9, 10],   # Both map to Trait A
        "id2": [5, 5],    # Both map to Trait B
        "rg": [0.5, 0.55],
        "se": [0.1, 0.08],
        "z": [5.0, 6.875],
        "p": [1e-6, 1e-10]
    })
    
    # ID to Trait mapping
    id_to_trait = {9: "Trait A", 10: "Trait A", 5: "Trait B"}
    
    aggregator = EdgeAggregator(gc_df=gc_data, id_to_trait_map=id_to_trait)
    
    result = aggregator.get_aggregated_edge("Trait A", "Trait B")
    
    assert result is not None
    assert result.source_trait == "Trait A"
    assert result.target_trait == "Trait B"
    assert result.n_correlations == 2
    assert len(result.correlations) == 2
    assert result.rg_meta is not None  # Meta-analyzed value
    assert result.rg_z_meta is not None


def test_aggregate_edges_excludes_self_loops():
    """Test that edges between studies of the same trait are excluded."""
    from src.server.modules.knowledge_graph.edge_aggregator import EdgeAggregator
    
    gc_data = pd.DataFrame({
        "id1": [9, 10],
        "id2": [10, 11],  # id 9,10,11 all map to same trait
        "rg": [0.9, 0.95],
        "se": [0.02, 0.03],
        "z": [45, 31],
        "p": [0, 0]
    })
    
    id_to_trait = {9: "Trait A", 10: "Trait A", 11: "Trait A"}
    
    aggregator = EdgeAggregator(gc_df=gc_data, id_to_trait_map=id_to_trait)
    
    # Should return None (self-loop)
    result = aggregator.get_aggregated_edge("Trait A", "Trait A")
    
    assert result is None


def test_get_neighbors_for_trait():
    """Test getting all neighbor traits for a given trait."""
    from src.server.modules.knowledge_graph.edge_aggregator import EdgeAggregator
    
    gc_data = pd.DataFrame({
        "id1": [1, 1],
        "id2": [2, 3],
        "rg": [0.5, 0.6],
        "se": [0.1, 0.1],
        "z": [5, 6],
        "p": [1e-5, 1e-7]
    })
    
    id_to_trait = {1: "Trait A", 2: "Trait B", 3: "Trait C"}
    
    aggregator = EdgeAggregator(gc_df=gc_data, id_to_trait_map=id_to_trait)
    
    neighbors = aggregator.get_neighbor_traits("Trait A")
    
    assert len(neighbors) == 2
    assert "Trait B" in neighbors
    assert "Trait C" in neighbors
```

### Step 2: Run test to verify it fails

Run: `pytest tests/unit/test_edge_aggregator.py -v`
Expected: FAIL with "cannot import name 'EdgeAggregator'"

### Step 3: Write minimal implementation

Create `src/server/modules/knowledge_graph/edge_aggregator.py`:

```python
"""
Edge Aggregator for Knowledge Graph.
Groups Study-pair correlations by Trait-pair and applies meta-analysis.
"""
import pandas as pd
import logging
from typing import Optional, List, Dict, Set, Tuple
from collections import defaultdict

from src.server.modules.knowledge_graph.models import GeneticCorrelationEdgeMeta
from src.server.modules.knowledge_graph.meta_analysis import inverse_variance_meta_analysis

logger = logging.getLogger(__name__)


class EdgeAggregator:
    """
    Aggregates Study-pair correlations by Trait-pair.
    Creates GeneticCorrelationEdgeMeta objects with meta-analyzed rg and full provenance.
    """
    
    def __init__(self, gc_df: pd.DataFrame, id_to_trait_map: Dict[int, str]):
        """
        Initialize with genetic correlation DataFrame and ID mapping.
        
        Args:
            gc_df: DataFrame with columns 'id1', 'id2', 'rg', 'se', 'z', 'p'
            id_to_trait_map: Mapping from study ID to trait name
        """
        self._df = gc_df
        self._id_to_trait = id_to_trait_map
        self._trait_pair_edges: Dict[Tuple[str, str], List[pd.Series]] = defaultdict(list)
        self._trait_neighbors: Dict[str, Set[str]] = defaultdict(set)
        self._preprocess()
    
    def _normalize_pair(self, trait1: str, trait2: str) -> Tuple[str, str]:
        """Normalize trait pair to consistent order."""
        return (trait1, trait2) if trait1 <= trait2 else (trait2, trait1)
    
    def _preprocess(self):
        """Group study-pair edges by trait-pair, excluding self-loops."""
        if self._df.empty:
            return
        
        for _, row in self._df.iterrows():
            id1 = int(row['id1'])
            id2 = int(row['id2'])
            
            trait1 = self._id_to_trait.get(id1)
            trait2 = self._id_to_trait.get(id2)
            
            if trait1 is None or trait2 is None:
                continue
            
            # Exclude self-loops
            if trait1 == trait2:
                continue
            
            pair_key = self._normalize_pair(trait1, trait2)
            self._trait_pair_edges[pair_key].append(row)
            
            # Track neighbors
            self._trait_neighbors[trait1].add(trait2)
            self._trait_neighbors[trait2].add(trait1)
    
    def get_neighbor_traits(self, trait_id: str) -> List[str]:
        """Get list of neighbor traits for a given trait."""
        return list(self._trait_neighbors.get(trait_id, set()))
    
    def get_aggregated_edge(
        self, 
        source_trait: str, 
        target_trait: str
    ) -> Optional[GeneticCorrelationEdgeMeta]:
        """
        Get aggregated edge between two traits.
        
        Args:
            source_trait: Source trait canonical name
            target_trait: Target trait canonical name
            
        Returns:
            GeneticCorrelationEdgeMeta with meta-analyzed rg, or None if not found
        """
        # Exclude self-loops
        if source_trait == target_trait:
            return None
        
        pair_key = self._normalize_pair(source_trait, target_trait)
        
        if pair_key not in self._trait_pair_edges:
            return None
        
        rows = self._trait_pair_edges[pair_key]
        
        # Extract rg estimates and SEs
        estimates = [float(r['rg']) for r in rows if pd.notna(r.get('rg'))]
        ses = [float(r['se']) for r in rows if pd.notna(r.get('se'))]
        
        min_len = min(len(estimates), len(ses))
        estimates = estimates[:min_len]
        ses = ses[:min_len]
        
        # Apply meta-analysis
        if estimates and ses:
            meta_result = inverse_variance_meta_analysis(estimates, ses)
        else:
            return None
        
        if meta_result["theta_meta"] is None:
            return None
        
        # Build correlation provenance
        correlations = []
        for row in rows:
            corr = {
                "source_study_id": int(row['id1']),
                "target_study_id": int(row['id2']),
                "rg": float(row['rg']) if pd.notna(row.get('rg')) else None,
                "se": float(row['se']) if pd.notna(row.get('se')) else None,
                "z": float(row['z']) if pd.notna(row.get('z')) else None,
                "p": float(row['p']) if pd.notna(row.get('p')) else None,
            }
            correlations.append(corr)
        
        return GeneticCorrelationEdgeMeta(
            source_trait=source_trait,
            target_trait=target_trait,
            rg_meta=meta_result["theta_meta"],
            rg_se_meta=meta_result["se_meta"],
            rg_z_meta=meta_result["z_meta"],
            rg_p_meta=meta_result["p_meta"],
            n_correlations=len(correlations),
            correlations=correlations
        )
```

### Step 4: Run test to verify it passes

Run: `pytest tests/unit/test_edge_aggregator.py -v`
Expected: PASS

### Step 5: Commit

```bash
git add tests/unit/test_edge_aggregator.py src/server/modules/knowledge_graph/edge_aggregator.py
git commit -m "feat(kg): add EdgeAggregator for grouping study-pair correlations by trait-pair"
```

---

## Task 5: Refactor KnowledgeGraphService to Use Trait-Centric Graph

**Files:**
- Modify: `src/server/modules/knowledge_graph/service.py`
- Test: `tests/unit/test_knowledge_graph_trait_centric.py`

### Step 1: Write the failing test

Create `tests/unit/test_knowledge_graph_trait_centric.py`:

```python
"""
Unit Tests for Trait-Centric Knowledge Graph Service.
Tests the refactored service with meta-analysis aggregation.
"""
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd


def test_get_trait_node_returns_aggregated_node():
    """Test that get_trait_node returns a TraitNode with meta-analyzed h2."""
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService
    from src.server.modules.knowledge_graph.models import TraitNode
    
    # Mock the underlying data
    mock_h2_df = pd.DataFrame({
        "id": [9, 10],
        "uniqTrait": ["Schizophrenia", "Schizophrenia"],
        "SNPh2": [0.5, 0.45],
        "SNPh2_se": [0.05, 0.04],
        "SNPh2_z": [10.0, 11.25],
        "Domain": ["Psychiatric", "Psychiatric"],
        "ChapterLevel": ["Mental", "Mental"]
    })
    
    with patch.object(KnowledgeGraphService, '_load_heritability_df', return_value=mock_h2_df):
        service = KnowledgeGraphService()
        
        node = service.get_trait_node("Schizophrenia")
        
        assert node is not None
        assert isinstance(node, TraitNode)
        assert node.trait_id == "Schizophrenia"
        assert node.n_studies == 2
        assert node.h2_meta is not None


def test_get_prioritized_neighbors_uses_meta_analysis():
    """Test that prioritized neighbors use rg_meta and h2_meta for scoring."""
    from src.server.modules.knowledge_graph.service import KnowledgeGraphService
    from src.server.modules.knowledge_graph.models import PrioritizedNeighborMeta
    
    # This test verifies the new scoring formula: rg_meta^2 * h2_meta
    # And that filtering uses |rg_z_meta| > 2 and h2_z_meta > 2
    
    mock_h2_df = pd.DataFrame({
        "id": [1, 2],
        "uniqTrait": ["Target", "Neighbor"],
        "SNPh2": [0.4, 0.5],
        "SNPh2_se": [0.03, 0.04],
        "SNPh2_z": [13.3, 12.5],
        "Domain": ["A", "B"]
    })
    
    mock_gc_df = pd.DataFrame({
        "id1": [1],
        "id2": [2],
        "rg": [0.6],
        "se": [0.05],
        "z": [12.0],
        "p": [1e-10]
    })
    
    with patch.object(KnowledgeGraphService, '_load_heritability_df', return_value=mock_h2_df):
        with patch.object(KnowledgeGraphService, '_load_gc_df', return_value=mock_gc_df):
            service = KnowledgeGraphService()
            
            neighbors = service.get_prioritized_neighbors_v2("Target")
            
            assert len(neighbors) >= 1
            neighbor = neighbors[0]
            assert neighbor.trait_id == "Neighbor"
            # Score should be rg_meta^2 * h2_meta
            expected_score = 0.6**2 * 0.5
            assert neighbor.score == pytest.approx(expected_score, rel=0.1)
```

### Step 2: Run test to verify it fails

Run: `pytest tests/unit/test_knowledge_graph_trait_centric.py -v`
Expected: FAIL with "KnowledgeGraphService object has no attribute 'get_trait_node'"

### Step 3: Write minimal implementation

Modify `src/server/modules/knowledge_graph/service.py` to add new methods:

```python
# Add to existing imports
from src.server.modules.knowledge_graph.trait_aggregator import TraitAggregator
from src.server.modules.knowledge_graph.edge_aggregator import EdgeAggregator
from src.server.modules.knowledge_graph.models import (
    TraitNode,
    GeneticCorrelationEdgeMeta,
    TraitCentricGraphResult,
    # ... existing imports
)

# Add to KnowledgeGraphService class:

    def _load_heritability_df(self) -> pd.DataFrame:
        """Load heritability DataFrame. Override for testing."""
        return self.h2_client.df
    
    def _load_gc_df(self) -> pd.DataFrame:
        """Load GC DataFrame. Override for testing."""
        return self.gc_client._data
    
    def _build_id_to_trait_map(self, h2_df: pd.DataFrame) -> Dict[int, str]:
        """Build mapping from study ID to trait name."""
        if h2_df.empty:
            return {}
        return dict(zip(h2_df['id'].astype(int), h2_df['uniqTrait'].astype(str)))
    
    def get_trait_node(self, trait_id: str) -> Optional[TraitNode]:
        """
        Get aggregated TraitNode for a given trait.
        
        Args:
            trait_id: Trait canonical name (uniqTrait)
            
        Returns:
            TraitNode with meta-analyzed h2 and study provenance
        """
        h2_df = self._load_heritability_df()
        aggregator = TraitAggregator(h2_df=h2_df)
        return aggregator.get_trait_node(trait_id)
    
    def get_prioritized_neighbors_v2(
        self,
        trait_id: str,
        rg_z_threshold: float = 2.0,
        h2_z_threshold: float = 2.0
    ) -> List[PrioritizedNeighbor]:
        """
        Get neighbors ranked by meta-analyzed score: rg_meta^2 * h2_meta.
        
        Uses Trait-level aggregation per sop.md Module 2 spec.
        
        Args:
            trait_id: Source Trait ID (uniqTrait)
            rg_z_threshold: Minimum |rg_z_meta| (default 2.0, ~p<0.05)
            h2_z_threshold: Minimum h2_z_meta (default 2.0)
            
        Returns:
            List of PrioritizedNeighbor sorted by score descending
        """
        h2_df = self._load_heritability_df()
        gc_df = self._load_gc_df()
        
        # Build aggregators
        id_to_trait = self._build_id_to_trait_map(h2_df)
        trait_aggregator = TraitAggregator(h2_df=h2_df)
        edge_aggregator = EdgeAggregator(gc_df=gc_df, id_to_trait_map=id_to_trait)
        
        # Get neighbor traits
        neighbor_traits = edge_aggregator.get_neighbor_traits(trait_id)
        
        prioritized = []
        
        for neighbor_id in neighbor_traits:
            # Get edge
            edge = edge_aggregator.get_aggregated_edge(trait_id, neighbor_id)
            if edge is None:
                continue
            
            # Filter by rg significance
            if edge.rg_z_meta is None or abs(edge.rg_z_meta) <= rg_z_threshold:
                continue
            
            # Get neighbor node
            neighbor_node = trait_aggregator.get_trait_node(neighbor_id)
            if neighbor_node is None:
                continue
            
            # Filter by h2 validity
            if neighbor_node.h2_z_meta is None or neighbor_node.h2_z_meta <= h2_z_threshold:
                continue
            
            # Calculate score: rg_meta^2 * h2_meta
            score = (edge.rg_meta ** 2) * neighbor_node.h2_meta
            
            neighbor = PrioritizedNeighbor(
                trait_id=neighbor_id,
                trait_name=neighbor_id,  # trait_id is the canonical name
                rg=edge.rg_meta,
                h2=neighbor_node.h2_meta,
                score=score,
                p_value=edge.rg_p_meta or 0.0
            )
            prioritized.append(neighbor)
        
        # Sort by score descending
        prioritized.sort(key=lambda x: x.score, reverse=True)
        
        return prioritized
```

### Step 4: Run test to verify it passes

Run: `pytest tests/unit/test_knowledge_graph_trait_centric.py -v`
Expected: PASS

### Step 5: Commit

```bash
git add tests/unit/test_knowledge_graph_trait_centric.py src/server/modules/knowledge_graph/service.py
git commit -m "feat(kg): add trait-centric methods with meta-analysis aggregation"
```

---

## Task 6: Update sop.md Implementation Status

**Files:**
- Modify: `.agent/blueprints/sop.md`

### Step 1: Update Implementation Status

After all tests pass, update the Implementation Status section in sop.md:

```markdown
#### Implementation Status

- **Implemented**: 
    - `KnowledgeGraphService` with Trait-Centric graph construction.
    - `TraitAggregator`: Groups Studies by `uniqTrait`, applies inverse-variance weighted meta-analysis for $h^2$.
    - `EdgeAggregator`: Groups Study-pairs by Trait-pair, applies meta-analysis for $r_g$.
    - **Meta-Analysis Pipeline**: `inverse_variance_meta_analysis()` utility function.
    - **Node Schema**: `TraitNode` with `h2_meta`, `h2_se_meta`, `h2_z_meta`, `n_studies`, `studies[]`.
    - **Edge Schema**: `GeneticCorrelationEdgeMeta` with `rg_meta`, `rg_se_meta`, `rg_z_meta`, `rg_p_meta`, `n_correlations`, `correlations[]`.
    - **Filter Logic**: `|rg_z_meta| > 2` and `h2_z_meta > 2`.
    - **Weighted Scoring**: `rg_meta^2 * h2_meta` ranking.
    - **Legacy Compatibility**: Original `get_neighbors()` and `get_prioritized_neighbors()` preserved.
- **Not Implemented**:
    - None. Module 2 core functionality is complete.
```

### Step 2: Commit

```bash
git add .agent/blueprints/sop.md
git commit -m "docs: update Module 2 implementation status to complete"
```

---

## Summary

| Task | Component | Status |
|:---|:---|:---:|
| 1 | New Data Models (TraitNode, GeneticCorrelationEdgeMeta) | TODO |
| 2 | Meta-Analysis Utility Function | TODO |
| 3 | TraitAggregator | TODO |
| 4 | EdgeAggregator | TODO |
| 5 | KnowledgeGraphService Refactor | TODO |
| 6 | sop.md Update | TODO |

**Total Estimated Time:** 2-3 hours following TDD methodology.
