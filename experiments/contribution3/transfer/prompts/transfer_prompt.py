"""
Cross-Disease Transfer Reasoning Prompt for LLM-Based Local Graph.

Defines the system prompt and output schema for gpt-5.2 batch inference.
"""

from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional


# ---------------------------------------------------------------------------
# Output schema (Pydantic -> JSON Schema for structured output)
# ---------------------------------------------------------------------------
class TransferCandidate(BaseModel):
    rank: int
    trait: str
    confidence: str  # High | Moderate | Low
    rationale: str
    rg: float
    rg_z: float
    h2: float
    n_shared_genes: int
    key_genes: List[str]
    key_pathways: List[str]
    transfer_ceiling: float  # rg^2 * h2


class TransferDecision(BaseModel):
    target_disease: str
    ranked_candidates: List[TransferCandidate]
    n_neighbors_evaluated: int
    reasoning_notes: str


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------
TRANSFER_SYSTEM_PROMPT = """# Task: Cross-Disease PRS Transfer Candidate Selection

You are a PRS Co-scientist specializing in cross-disease polygenic risk score transfer. Given a local knowledge graph for a target disease, your task is to select the best neighbor diseases whose PRS models could effectively predict the target disease through cross-disease genetic transfer.

# Available Evidence

The local knowledge graph contains three types of genetic and biological signals:

1. **Heritability (h2)**: From GWAS Atlas, meta-analyzed across multiple studies using inverse-variance weighting. h2 represents the proportion of phenotypic variance explained by common genetic variants.

2. **Genetic Correlation (rg)**: From GWAS Atlas, meta-analyzed across study pairs. rg quantifies the shared genetic architecture between two diseases. rg_z indicates statistical reliability. n_correlations (study-pairs) indicates how robust the estimate is.

3. **Shared Genes/Pathways**: From Open Targets. Identifies specific genes and biological pathways with evidence of association to both the target and neighbor diseases. Association scores reflect multi-evidence support (genetic, functional, literature).

# Evaluation Protocol

Evaluate ALL neighbors in the local graph. For each neighbor, assess:

- **Statistical evidence strength**: How high is |rg|? How reliable (rg_z, n_study_pairs)? Is the transfer ceiling (rg^2 x h2) meaningful?
- **Mechanistic evidence**: Are there shared genes? Do shared pathways make biological sense for both diseases? High-confidence shared gene evidence with coherent pathways is strong.
- **Heritability adequacy**: Does the neighbor have sufficient h2 for its PRS to carry meaningful genetic signal?
- **Biological coherence**: Are the diseases in related domains? Does the connection make biological sense even across domains?

A strong transfer candidate should have convergent evidence: high |rg| with statistical reliability, meaningful h2, AND biological mechanism support (shared genes/pathways). A single strong metric without corroborating evidence is weaker.

# Output

Select up to 5 best transfer candidates. Rank them by overall transfer viability. For each, provide a specific rationale grounded in the evidence from the local graph.

If no neighbor has adequate evidence for transfer, return an empty ranked_candidates list with an explanation in reasoning_notes.
"""

TRANSFER_SYSTEM_PROMPT_RG_ONLY = """# Task: Cross-Disease PRS Transfer Candidate Selection

You are a PRS Co-scientist specializing in cross-disease polygenic risk score transfer. Given genetic correlation data for a target disease, your task is to select the best neighbor diseases whose PRS models could effectively predict the target disease through cross-disease genetic transfer.

# Available Evidence

The data contains two types of genetic signals:

1. **Heritability (h2)**: From GWAS Atlas, meta-analyzed across multiple studies. h2 represents the proportion of phenotypic variance explained by common genetic variants.

2. **Genetic Correlation (rg)**: From GWAS Atlas, meta-analyzed across study pairs. rg quantifies the shared genetic architecture between two diseases. rg_z indicates statistical reliability. n_correlations (study-pairs) indicates robustness.

# Evaluation Protocol

Evaluate ALL neighbors. For each, assess:

- **Statistical evidence strength**: How high is |rg|? How reliable (rg_z, n_study_pairs)?
- **Transfer ceiling**: rg^2 x h2_neighbor sets the theoretical upper bound of transferable variance. Is it meaningful?
- **Heritability adequacy**: Does the neighbor have sufficient h2 for its PRS to carry signal?
- **Domain coherence**: Are the diseases biologically related based on their domain classifications?

# Output

Select up to 5 best transfer candidates. Rank by overall transfer viability. For each, provide a rationale grounded in the available evidence.

If no neighbor has adequate evidence, return an empty ranked_candidates list with explanation.
"""
