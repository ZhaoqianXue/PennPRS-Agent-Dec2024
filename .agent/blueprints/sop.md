# Standard Operating Procedure 

## Brainstorming

- Focus on PRS model recommendation applications.
- If there is matched diseases, select the best one.
- If there is no matched disease, we can (i) selected genetically related diseases (one or more); (2) train the model on PennPRS. 
- We may use h2, genetic correlation, and base model embedding information to first build a knowledge graph among diseases. How to weight these resources? 
- Need validation, All of US? 
- Write initial version of prompts (i) same disease (ii) cross diseases, talking with GPT for design, and we can further refine. 
- Start with some selected diseases (cancer, mental diseases, neurodegenetive diseses, heart diseases) to build up the pipeline.

## LLM Agentic Engineering Knowledge Base

**To ensure the autonomy and reliability of the single llm agent system, this project must strictly adhere to the engineering standards detailed in the following documentation, each of which MUST be read in its entirety:**

- [Anthropic: Long-Running Agents](../knowledge/context_engineering/anthropic_long_running_agents.md)
- [Anthropic: Effective Context Engineering](../knowledge/context_engineering/anthropic_context_engineering.md)
- [Manus: Context Engineering](../knowledge/context_engineering/manus_context_engineering.md)

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

- **LLM Strategy (Co-Scientist Expert Persona)**: The platform is engineered as a **specialized Co-Scientist** rather than a generic assistant. By mastering deep domain knowledge (PRS methodology, genetic architecture, and clinical statistics), the agent acts as an expert evaluator capable of high-level model selection and sophisticated cross-disease reasoning.
    - **Management Constraint**: All system prompts must be centralized in a **single file** to facilitate management and version control.

## Architecture

### Immutable Architectural Constraint: Single Agent Loop

To achieve the "Co-scientist" level of autonomy and reasoning, the system **MUST** be built as a **Single Agent Architecture** (powered by **gpt-5-mini**). The agent acts as a unified central brain, utilizing **Dynamic Planning** and **Tool-Augmented Generation** to navigate the complex recommendation workflow within a **single persistent conversation state**. Multi-agent delegation or sub-agent hierarchies are strictly prohibited to maintain persona integrity and state coherence.

The agent's capabilities are organized into three external **Toolsets** and one internal **Core Logic**:

- **PRS Model Tools**: For direct model searching in catalogs and quantitative quality threshold assessment.
- **Genetic Graph Tools**: For traversing Knowledge Graphs (h2, rg, embeddings) to identify genetic proxies.
- **PennPRS Tools**: For interfacing with the PennPRS backend for autonomous model training.
- **Reasoning & Persona (Internal)**: The central logic responsible for "fine-dining" answer synthesis, ensuring every response is reasoned, evidence-backed, and maintains the specialized co-scientist persona.

### Agent Engineering Constraints

To ensure agent reliability and long-horizon coherence, the following architectural decisions are **mandatory** (derived from LLM Agentic Engineering Knowledge Base):

1. **Static Tool Binding with Masking**
   - All tools are **defined at session start** and remain constant throughout the agent loop.
   - Tool availability is controlled via **logit masking** (constrained decoding), not dynamic injection/removal.
   - This preserves **KV-cache efficiency** and prevents model confusion from disappearing tool definitions.
   - *Reference: Manus - "Mask, Don't Remove"*

2. **JIT (Just-In-Time) Context Loading**
   - Tools return **lightweight references** (IDs, file paths, URLs) instead of full data objects.
   - Full data is loaded **on-demand** when the agent explicitly requests it.
   - This preserves **context budget** and enables progressive disclosure.
   - *Example*: `search_pgs_catalog()` returns `[PGS000025, PGS000142]` instead of full model metadata.
   - *Reference: Anthropic - "Just in time context strategies"*

3. **Error Trace Retention**
   - Failed tool calls and error messages **remain in the message history**.
   - The agent is allowed to "see" its own failures to avoid repeating the same mistake.
   - No automatic retry-and-hide behavior; errors are explicit feedback.
   - *Reference: Manus - "Keep the Wrong Stuff In"*

4. **Monolithic State (Strict Single Agent)**
   - The system is built on a **single LLM loop** without delegating to sub-agents.
   - This prevents context fragmentation and ensures the **Co-Scientist persona** has full visibility of every step.
   - Any logic that would traditionally be a "separate agent" must be implemented as a **tool calling capability** within the same brain.
   - *Rationale: Direct accountability and persona consistency.*

## Implementation Plan

1.  **Phase 1: Foundation & Metrics (Success Definition)**
    - **Module 1: Define Quality Thresholds**: Establish quantitative metrics (e.g., $R^2$, AUC, sample size) for the agent to distinguish between "High-Quality" and "Sub-optimal" matches.
    - **Module 2: Build Knowledge Graph (KG)**: Integrate `genetic_correlation`, `heritability`, and model embeddings into a developer-accessible graph search space.

2.  **Phase 2: Agent Core & Toolset Engineering**
    - **Module 3: Prompt Engineering**: Develop the specialized **gpt-5-mini** system prompt, focusing on **Plan-and-Solve** logic and "Fine-dining" persona. *(Constraints: #2 JIT Context Loading)*
    - **Module 4: Toolset Implementation**: Standardize and wrap **PRS Model Tools, Genetic Graph Tools, and PennPRS Tools** as reliable tool-calling interfaces. *(Constraints: #1 Static Tool Binding, #2 JIT Context Loading)*
    - **Module 5: Dynamic Planning**: Implement the autonomous logic for the agent to navigate between assessment and augmented paths without manual intervention. *(Constraints: #3 Error Trace Retention)*

3.  **Phase 3: Deep System Integration**
    - **Module 6: PennPRS Backend Bridge**: Finalize the API integration for **PennPRS Tools** to enable one-click autonomous model training execution.
    - **Module 7: Execution Environment**: Ensure the agent can securely invoke tools and process genomic metadata in a stable server-side environment.

4.  **Phase 4: Pilot & Fine-Dining Synthesis**
    - **Module 8: Output Synthesis Tuning**: Refine the agent’s ability to weave fragmented tool results into evidence-backed, professional co-scientist reports.
    - **Module 9: Pipeline Pilot**: Execute end-to-end development runs for **Cancer, Mental, Neurodegenerative, and Heart Diseases**.

## Implementation Log

### Module 1 - Quality Thresholds Definition

#### PGS Catalog Models Available Fields
Based on `src/server/core/pgs_catalog_client.py` and `pgscatalog/PGS_Catalog/rest_api/serializers.py`, the following fields are available from the PGS Catalog API (combining Score and Performance endpoints).

| Field Name (API Key) | Description | Source |
| :--- | :--- | :--- |
| **`id`** | Unique Model ID (e.g., PGS000025) | Score |
| **`name`** | Model display name | Score |
| **`trait_reported`** | Original reported trait | Score |
| **`trait_additional`** | Additional trait information | Score |
| **`trait_efo`** | EFO Ontology mappings | Score |
| **`method_name`** | Algorithm used (e.g. LDpred2) | Score |
| **`method_params`** | Parameters used in the method | Score |
| **`variants_number`** | Count of variants in model | Score |
| **`variants_interactions`** | Variant interactions info | Score |
| **`variants_genomebuild`** | Genome build (e.g. GRCh37) | Score |
| **`weight_type`** | Type of weights used | Score |
| **`ancestry_distribution`** | Detailed ancestry breakdown | Score |
| **`publication`** | Publication metadata (DOI, PMID, etc.) | Score/Performance |
| **`date_release`** | Date the score was released | Score |
| **`license`** | Usage license | Score |
| **`ftp_scoring_file`** | URL to original scoring file | Score |
| **`ftp_harmonized_scoring_files`** | URL to harmonized scoring file | Score |
| **`matches_publication`** | Flag if score matches publication | Score |
| **`samples_variants`** | Samples used for variant selection | Score |
| **`samples_training`** | Samples used for training | Score |
| **`performance_metrics`** | Metrics (AUC, R2, etc.) | Performance |
| **`phenotyping_reported`** | Phenotype description in validation | Performance |
| **`covariates`** | Covariates used in validation | Performance |
| **`sampleset`** | Sample set used for validation | Performance |
| **`performance_comments`** | Additional performance notes | Performance |
| **`associated_pgs_id`** | The PGS ID associated with performance | Performance |

#### LLM-Driven Quality Thresholds

Instead of hard-coded heuristic tiers, we will leverage the **Large Lange Model** to determine model quality dynamically.

- **Mechanism**: The Agent will receive the structured metadata (fields listed above) in its context window.
- **Prompt Logic**: The system prompt will instruct the LLM to evaluate models.
- **Evolution Note**: Initial metadata-based judgments may be limited. Subsequent **Tool-Driven JIT Context Loading** (e.g., autonomously invoking tools for deep methodology scrutiny, study design validation, or cross-referencing external benchmarks) enables the **Co-scientist Expert Scrutiny** phase. This ensures that the agent resolves high-stakes ambiguity through first-hand evidence to reach a definitive scientific judgment, while efficiently managing the attention budget.

#### Implementation Status

- **Implemented**: 
    - Deterministic `QualityEvaluator` (Python) to pre-calculate `RecommendationGrade` (Gold/Silver/Bronze) based on strict metadata thresholds (e.g. `num_variants > 100`, `sample_size > 50k`).
    - Strong Types (`QualityMetrics`, `RecommendationGrade`).
    - **Agentic Study Classifier**: LLM-powered classification of study methodology (Binary vs Continuous) and automated sample size extraction (Neff calculation) from GWAS Catalog metadata.
- **Not Implemented**:
    - **LLM Prompt Logic**: The dynamic reasoning prompt ("Plan-and-Solve") to consume these grades is part of Phase 2 (Module 3).
    - **Co-Scientist Expert Selection**: Advanced reasoning logic that leverages domain knowledge to critically evaluate, compare, and select the best PRS model(s) from the candidate set, providing professional scientific rationale for recommendations.

### Module 2 - Knowledge Graph Definition

#### Graph Schema

The Knowledge Graph is defined as a **Genetic Architecture Graph**, capturing both trait-specific signals and shared risk.

- **Nodes**: **Traits**.
    - **Attributes**: **Heritability ($h^2$)**. Used as a "Signal Strength" weight to prioritize traits with robust genetic architectures as viable proxy sources.
    - **Data Source**: `src/server/modules/heritability/gwas_atlas_client.py` (Local pre-computed TSV).
    - **Metrics**: $h^2$ (Observed scale).
- **Edges**: **Genetic Correlation ($r_g$)**.
    - **Data Source**: `src/server/modules/genetic_correlation/gwas_atlas_client.py` (Local pre-computed TSV).
    - **Metrics**: $r_g$ (Coefficient), $SE$, $P$-value.
- **Constraint**: No Model Nodes, no Embedding Similarity edges, no Ontology edges.

#### Interaction Logic (Dynamic Service)

The Knowledge Graph is implemented as a **Virtual/Dynamic Graph**, constructed on-demand from local GWAS Atlas data.

- **Input**: Target Trait (e.g., "Alzheimer's").
- **Traversal & Prioritization**: 
    1. Query neighbors where `p_value < 0.05` (Significance).
    2. Rank neighbors by a weighted score of **$r_g^2 \times h^2_{proxy\_node}$** to favor proxies that are both highly correlated and biologically viable for PRS transfer.
- **Output**: Prioritized list of genetically related traits (Proxies) to serve as search candidates for Module 1.

#### Implementation Status

- **Implemented**: 
    - `KnowledgeGraphService` wrapping `GWASAtlasGCClient`.
    - Dynamic Graph Construction (Nodes/Edges).
    - Filter: `p < 0.05` significance threshold applied.
- **Not Implemented**:
    - **Node Heritability**: Heritability ($h^2$) attributes are currently `None` in graph nodes; integration with the heritability client is pending.
    - **Weighted Scoring**: Ranking neighbors by $r_g^2 \times h^2$ (to prioritize proxies) is not yet implemented.
    - **ID Mapping**: Automatic conversion between EFO IDs and GWAS Atlas Numeric IDs is mocked/pending.
