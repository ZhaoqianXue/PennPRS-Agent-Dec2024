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

// --- Module 4: Recommendation Report ---

export type RecommendationType =
    | "DIRECT_HIGH_QUALITY"
    | "DIRECT_SUB_OPTIMAL"
    | "CROSS_DISEASE"
    | "NO_MATCH_FOUND";

export interface PrimaryRecommendation {
    pgs_id?: string;
    source_trait?: string;
    confidence: "High" | "Moderate" | "Low";
    rationale: string;
}

export interface DirectMatchEvidence {
    models_evaluated: number;
    performance_metrics: Record<string, unknown>;
    clinical_benchmarks: string[];
}

export interface CrossDiseaseModelSummary {
    models_found: number;
    best_model_id?: string;
    best_model_auc?: number;
}

export interface CrossDiseaseEvidence {
    source_trait: string;
    rg_meta?: number;
    transfer_score?: number;
    related_traits_evaluated: string[];
    shared_genes: string[];
    biological_rationale?: string;
    source_trait_models?: CrossDiseaseModelSummary;
}

export interface StudyPowerSummary {
    n_correlations: number;
    rg_meta?: number;
}

export interface GeneticGraphEvidence {
    neighbor_trait: string;
    rg_meta?: number;
    transfer_score?: number;
    neighbor_models_found: number;
    neighbor_best_model_id?: string;
    neighbor_best_model_auc?: number;
    mechanism_confidence?: string;
    mechanism_summary?: string;
    shared_genes: string[];
    study_power?: StudyPowerSummary;
}

export interface FollowUpOption {
    label: string;
    action: string;
    context: string;
}

export interface RecommendationReport {
    recommendation_type: RecommendationType;
    primary_recommendation?: PrimaryRecommendation | null;
    alternative_recommendations: PrimaryRecommendation[];
    direct_match_evidence?: DirectMatchEvidence | null;
    cross_disease_evidence?: CrossDiseaseEvidence | null;
    genetic_graph_evidence?: GeneticGraphEvidence[];
    genetic_graph_ran?: boolean;
    genetic_graph_neighbors?: string[];
    genetic_graph_errors?: string[];
    caveats_and_limitations: string[];
    follow_up_options: FollowUpOption[];
}
