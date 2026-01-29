# Proposal 

## Brainstorming

- Focus on PRS model recommendation applications.
- If there is matched diseases, select the best one.
- If there is no matched disease, we can (i) selected genetically related diseases (one or more); (2) train the model on PennPRS. 
- We may use h2, genetic correlation, and base model embedding information to first build a knowledge graph among diseases. How to weight these resources? 
- Need validation, All of US? 
- Write initial version of prompts (i) same disease (ii) cross diseases, talking with GPT for design, and we can further refine. 
- Start with some selected diseases (cancer, mental diseases, neurodegenetive diseses, heart diseases) to build up the pipeline.

## Objective

The core objective is to evolve the **PRS (Polygenic Risk Score) Model Recommendation System** beyond simple direct matching by leveraging genetic architecture to enable intelligent cross-disease recommendations.

- **Recommendation Logic (Sequential Workflow)**:
    - **Step 1: Direct Match Assessment**: Search for existing models for the target disease.
        - *High-Quality Match*: If models exist and pass the quality threshold, recommend the best-performing one.
        - *Sub-optimal Match*: If models exist but fail the quality threshold, recommend the best available as a baseline and **proceed to Step 2**.
        - *No Match*: If no direct models exist, **proceed to Step 2**.
    - **Step 2: Augmented Recommendation**: Triggered when direct models are insufficient or missing.
        - *Cross-Disease Transfer*: Recommend models from **genetically related diseases** using the Knowledge Graph.
        - *Direct Training*: Initiate a new model training pipeline on **PennPRS**.
    - **Automation Note**: This entire pipeline is **fully autonomous**. Aside from the initial search query, no further user input or manual intervention is required to navigate through the assessment and augmentation steps.

- **Product Vision & Benchmarking**:
    - **Positioning**: This system benchmarks against the world's most powerful Generative LLMs (**ChatGPT, Claude, Gemini**), but is specifically engineered and optimized for the **PRS domain**.
    - **User Experience**: The interaction model mirrors the simplicity of leading AI assistants—users simply input a query into a search bar. Behind the scenes, the **LLM Agent** autonomously orchestrates reasoning, tool calls, and data retrieval to deliver a "fine-dining" (precision-crafted) response.
    - **Differentiator**: Unlike general-purpose LLMs that typically return text, links, or videos, our system provides:
        1. **Direct Model Access**: Immediate delivery of the specific PRS models.
        2. **Evidence-Based Context**: A curated selection of related models backed by genetic evidence (rg/h2).
        3. **Seamless Integration**: The ability for users to directly apply and execute these models within the **PennPRS** ecosystem.

- **Disease Knowledge Graph**: Build a "brain" for the system using:
    - **h² (Heritability)**: To understand the genetic contribution to the trait.
    - **Genetic Correlation (rg)**: To quantify the pleiotropy and shared genetic risk between diseases.
    - **Base Model Embeddings**: To find mathematical similarities between existing PRS models.

- **Validation**: Utilize the **All of Us** cohort (NIH research program) as the gold standard to validate the performance of recommended models.

- **LLM Strategy**: Develop specialized prompts for the agent to act as a co-scientist, handling both same-disease optimization and cross-disease reasoning.
    - **Management Constraint**: All system prompts must be centralized in a **single file** to facilitate management and version control.

## Architecture

To achieve the "Co-scientist" level of autonomy and reasoning, the system will be built using a **Single Agent Architecture** (powered by **gpt-5-mini** as per project standards). The agent acts as a unified central brain, utilizing **Dynamic Planning** and **Tool-Augmented Generation** to navigate the complex recommendation workflow.

The agent's capabilities are organized into three external **Toolsets** and one internal **Core Logic**:

- **PRS Model Tools**: For direct model searching in catalogs and quantitative quality threshold assessment.
- **Genetic Graph Tools**: For traversing Knowledge Graphs (h2, rg, embeddings) to identify genetic proxies.
- **PennPRS Tools**: For interfacing with the PennPRS backend for autonomous model training.
- **Reasoning & Persona (Internal)**: The central logic responsible for "fine-dining" answer synthesis, ensuring every response is reasoned, evidence-backed, and maintains the specialized co-scientist persona.

## Implementation Plan

1.  **Phase 1: Foundation & Metrics (Success Definition)**
    - **Module 1: Define Quality Thresholds**: Establish quantitative metrics (e.g., $R^2$, AUC, sample size) for the agent to distinguish between "High-Quality" and "Sub-optimal" matches.
    - **Module 2: Build Knowledge Graph (KG)**: Integrate `genetic_correlation`, `heritability`, and model embeddings into a developer-accessible graph search space.

2.  **Phase 2: Agent Core & Toolset Engineering**
    - **Module 3: Prompt Engineering**: Develop the specialized **gpt-5-mini** system prompt, focusing on **Plan-and-Solve** logic and "Fine-dining" persona.
    - **Module 4: Toolset Implementation**: Standardize and wrap **PRS Model Tools, Genetic Graph Tools, and PennPRS Tools** as reliable tool-calling interfaces.
    - **Module 5: Dynamic Planning**: Implement the autonomous logic for the agent to navigate between assessment and augmented paths without manual intervention.

3.  **Phase 3: Deep System Integration**
    - **Module 6: PennPRS Backend Bridge**: Finalize the API integration for **PennPRS Tools** to enable one-click autonomous model training execution.
    - **Module 7: Execution Environment**: Ensure the agent can securely invoke tools and process genomic metadata in a stable server-side environment.

4.  **Phase 4: Pilot & Fine-Dining Synthesis**
    - **Module 8: Output Synthesis Tuning**: Refine the agent’s ability to weave fragmented tool results into evidence-backed, professional co-scientist reports.
    - **Module 9: Pipeline Pilot**: Execute end-to-end development runs for **Cancer, Mental, Neurodegenerative, and Heart Diseases**.

## Implementation Log

### Module 1 - Quality Thresholds Definition

#### 1. Available Fields Analysis
Based on `src/server/modules/disease/workflow.py` (Lines 327-359), the following fields are extracted from PGS Catalog relative to Quality Control.

| Field Name | Description | Quality Relevance | Analysis & Recommendation |
| :--- | :--- | :--- | :--- |
| **`id`** | Unique Model ID (e.g., PGS000025) | **High** | Essential for tracking and citation. |
| **`name` / `pgs_name`** | Model display name | Low | No impact on scientific quality, purely descriptive. |
| **`trait` / `trait_reported`** | Original reported trait | **High** | Must match query context. Used for broad filtering. |
| **`trait_detailed`** | Specific phenotype description | Medium | Useful for disambiguation (e.g. Type 1 vs Type 2 Diabetes). |
| **`mapped_traits`** | EFO Ontology IDs/Labels | **Critical** | Standardized trait mapping. Used for cross-disease KG linking. |
| **`metrics`** | Aggregated AUC/R2/Beta/OR/HR | **Critical** | Top-level performance indicator. Primary sorting key. |
| **`performance_detailed`** | List of validation records | **Critical** | **Gold Standard**. Contains ancestry-specific metrics essential for matching user demographics. |
| **`sample_size`** | Total N (Training + Validation) | **High** | Proxy for statistical power. >50k preferred. |
| **`ancestry`** | Major ancestry group | **Critical** | Strict filter. Model must match user population (default EUR). |
| **`ancestry_distribution`** | Detailed % breakdown (e.g. 90% EUR) | **High** | Allows fine-grained matching (e.g. Admixed populations). |
| **`method` / `method_name`** | Algorithm used (e.g. LDpred2) | **Medium** | Newer Bayesian methods generally outperform heuristic C+T. |
| **`num_variants`** | Count of SNPs in model | **Critical** | **Polygenic Check**. <100 implies oligogenic/pathway scores (not true PRS); >1M is standard. |
| **`publication`** | Date, Journal, Author | **High** | **Recency Filter**. Pre-2018 models often obsolete. |
| **`download_url`** | FTP link to scoring file | **Critical** | **Pass/Fail**. No file = unusable. |
| **`license`** | Terms of Use | Low | Only affects commercial viability, not scientific accuracy. |
| **`genome_build`** | GRCh37 vs GRCh38 | Low | Technical detail, handled by LiftOver if needed. |
| **`dev_cohorts`** | Training datasets (e.g. UKB) | Medium | UK Biobank models generally high quality. |
| **`covariates`** | Adjustments (Age, Sex, PCs) | Medium | More covariates = rigorous validation. |

#### 2. Quality Thresholds (LLM-Driven)

Instead of hard-coded heuristic tiers, we will leverage the **LLM's reasoning capabilities** to determine model quality dynamically.

- **Mechanism**: The Agent will receive the structured metadata (fields listed above) in its context window.
- **Prompt Logic**: The system prompt will instruct the LLM to evaluate models based on:
    - **Performance Metrics**: AUC/R2 validity.
    - **Sample Size & Ancestry**: Match quality.
    - **Methodology**: Technical sophistication (e.g., Bayesian vs. C+T).
    - **Polygenic Validation**: Variant count checks (>100 as proxy).
- **Evolution Note**: Initial metadata-based judgments may be limited. Subsequent **PRS Model Knowledge Enhancement** (e.g., retrieving full paper context, study design validation, or external quality benchmarks) will be applied to refine and correct the LLM's assessment of the PRS Model itself, distinct from the cross-disease Knowledge Graph.

#### 3. Implementation Status (Phase 1)
- **Implemented**: 
    - Deterministic `QualityEvaluator` (Python) to pre-calculate `RecommendationGrade` (Gold/Silver/Bronze) based on strict metadata thresholds (e.g. `num_variants > 100`, `sample_size > 50k`).
    - Strong Types (`QualityMetrics`, `RecommendationGrade`).
- **Not Implemented**:
    - **LLM Prompt Logic**: The dynamic reasoning prompt ("Plan-and-Solve") to consume these grades is part of Phase 2 (Module 3).
    - **Methodology Text Analysis**: Deep parsing of "methodology" or "study design" strings is not yet implemented.

### Module 2 - Knowledge Graph Definition

#### 1. Graph Schema
The Knowledge Graph is strictly defined as a **pure Genetic Correlation Network** sourced from GWAS Atlas.

- **Nodes**: **Traits** (Source: GWAS Atlas Ontology).
- **Edges**: **Genetic Correlation ($r_g$) Only**.
    - **Data Source**: `src/server/modules/genetic_correlation/gwas_atlas_client.py` (Local pre-computed TSV).
    - **Metrics**: $r_g$ (Coefficient), $SE$, $P$-value.
    - **Constraint**: No Model Nodes, no Embedding Similarity edges, no Ontology edges.

#### 2. Interaction Logic (Dynamic Service)

The Knowledge Graph is implemented as a **Virtual/Dynamic Graph**, constructed on-demand from local GWAS Atlas data.

- **Input**: Target Trait (e.g., "Alzheimer's").
- **Traversal**: Query neighbors where `p_value < 0.05` (Significance).
- **Output**: List of genetically related traits (Proxies) to serve as search candidates for Module 1.

#### 3. Implementation Status (Phase 1)
- **Implemented**: 
    - `KnowledgeGraphService` wrapping `GWASAtlasGCClient`.
    - Dynamic Graph Construction (Nodes/Edges).
    - Filter: `p < 0.05` only. (No `|rg|` threshold applied).
- **Not Implemented**:
    - **ID Mapping**: Automatic conversion between EFO IDs and GWAS Atlas Numeric IDs is mocked/pending.
