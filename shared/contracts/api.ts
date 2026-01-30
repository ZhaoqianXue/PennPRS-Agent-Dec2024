/**
 * @file api.ts
 * Shared API Contracts and Type Definitions for Phase 1.
 * Defines the core data structures for Quality Thresholds and Knowledge Graph.
 */

// --- Module 1: Quality Thresholds ---

/**
 * Quality Metrics Interface
 * Tracks quantitative indicators for quality assessment.
 */
export interface QualityMetrics {
    auc?: number;
    r2?: number;
    sample_size?: number;
    num_variants?: number; // Critical Polygenic Check
    ancestry_match_score?: number; // 0-1 Score
    publication_year?: number;
    is_polygenic?: boolean; // Derived from num_variants > 100
}

/**
 * Evaluated Model Card Extension
 * Fields injected by QualityEvaluator into the base model data.
 */
export interface EvaluatedModelCard {
    id: string;
    metrics: QualityMetrics;
    quality_reasoning?: string[]; // Explanations or caveats extracted from metadata
}


// --- Module 2: Knowledge Graph ---

/**
 * Knowledge Graph Node
 * Represents a Trait (Disease/Phenotype) in the Genetic Graph.
 * Strictly Trait-Only as per Module 2 Definition.
 */
export interface KnowledgeGraphNode {
    id: string;   // EFO ID or Standardized Trait Name
    label: string;
    h2?: number;  // Heritability (Node Weight)
}

/**
 * Genetic Correlation Edge
 * Represents a biological link between two traits based on GWAS Atlas.
 */
export interface GeneticCorrelationEdge {
    source: string;   // Source Trait ID
    target: string;   // Target Trait ID
    rg: number;       // Genetic Correlation Coefficient (-1 to 1)
    p_value: number;  // Significance (e.g. < 0.05)
    se?: number;      // Standard Error
}

/**
 * Graph Traversal Result
 * Returned by KnowledgeGraphService queries.
 */
export interface KnowledgeGraphResult {
    nodes: KnowledgeGraphNode[];
    edges: GeneticCorrelationEdge[];
}
