# Standard Operating Procedure

## Target Journal: Nature Genetics

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
    - **Base Model Embeddings (HOLD)**: To find mathematical similarities between existing PRS models.

- **Validation**: Utilize the **All of Us** cohort (NIH research program) as the gold standard to validate the performance of recommended models.

- **LLM Strategy (Co-Scientist Expert Persona)**: The platform is engineered as a **specialized Co-Scientist** rather than a generic assistant.
    - **Core Philosophy**: **Context-Driven Scientific Reasoning.** The Agent achieves expert-level performance by using tools to dynamically construct a **"Scientific Reasoning Context"**. Instead of relying solely on internal weights, it actively fetches **Scientific Standards and Evidence** (e.g., theoretical limits, statistical baselines, expert consensus) to **guide discovery, evaluate quality, and orchestrate execution**. This enables the Agent to act as a rigorous intellectual partner capable of navigating complex research workflows independently, rather than merely verifying isolated facts.
    - **Management Constraint**: All system prompts must be centralized in a **single file** to facilitate management and version control.

## Architecture

### Immutable Architectural Constraint: Single Agent Loop

To achieve the "Co-scientist" level of autonomy and reasoning, the system **MUST** be built as a **Single Agent Architecture** (powered by **gpt-5-mini**). The agent acts as a unified central brain, utilizing **Dynamic Planning** and **Tool-Augmented Generation** to navigate the complex recommendation workflow within a **single persistent conversation state**. Multi-agent delegation or sub-agent hierarchies are strictly prohibited to maintain persona integrity and state coherence.

The agent's capabilities are organized into **four external Toolsets** and one internal **Core Logic**:

- **PRS Model Tools**: For direct model searching in catalogs and quantitative quality threshold assessment.
- **Genetic Graph Tools**: For traversing Knowledge Graphs (h2, rg, embeddings) to identify genetic proxies.
- **Scientific Evidence Tools**: For retrieving literature, benchmarks, and clinical consensus to build the reasoning context.
- **PennPRS Tools**: For interfacing with the PennPRS backend for autonomous model training.
- **Reasoning & Persona (Internal)**: The central logic responsible for "fine-dining" answer synthesis, ensuring every response is reasoned, evidence-backed, and maintains the specialized co-scientist persona.

## Implementation Plan

1.  **Phase 1: Foundation**

    - **Module 1: PGS Catalog Data Schema**: Define the data interface and metadata extraction for PGS models.

    - **Module 2: Knowledge Graph**: Integrate `genetic_correlation` and `heritability` into a graph-based proxy discovery system.

2.  **Phase 2: Agent Core**

    The following engineering constraints are **mandatory** (derived from LLM Agentic Engineering Knowledge Base):

    - **Module 3: Toolset**
        - Wrap **PGS Catalog, GWAS Atlas, and PennPRS** as callable tool interfaces.
        - **Static Tool Binding with Masking**: All tools defined at session start; availability controlled via logit masking, not dynamic injection. *(Manus: Mask, Don't Remove)*
        - **Consistent Tool Naming**: Use standardized domain prefixes (e.g., `domain_action`) for efficient logit mask grouping. *(Manus: Prefix-Based Action Selection)*
        - **Self-Contained & Robust**: Each tool must be error-tolerant with unambiguous input/output schemas. *(Anthropic: Tool Design)*
        - **Minimal Viable Toolset**: Curate the smallest set covering functionality; avoid ambiguous decision points. *(Anthropic: Tool Curation)*
        - **JIT Context Loading**: Tools return lightweight references (IDs, paths); full data loaded on-demand. *(Anthropic: Just-in-time context strategies)*
        - **Append-Only Context**: Serialize tool results deterministically; no mid-loop modification to preserve KV-cache. *(Manus: Design Around the KV-Cache)*
        - **Error Trace Retention**: Failed tool calls remain in history as explicit feedback; no retry-and-hide. *(Manus: Keep the Wrong Stuff In)*

    - **Module 4: System Prompt**
        - Develop the **gpt-5-mini** prompt with Plan-and-Solve decision logic.
        - Define JSON/Markdown templates for recommendation reports.
        - **Prompt Altitude**: Write at the right abstraction level; avoid hardcoding brittle logic or vague guidance. *(Anthropic: Right Altitude)*
        - **Attention Manipulation via Recitation**: Implement `todo.md` style progress tracking to push objectives into recent attention span. *(Manus: Manipulate Attention Through Recitation)*

## Implementation Log

### Module 1 - PGS Catalog Data Schema

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

#### Agent Context Injection

The structured metadata fields above are serialized into the agent's context window for LLM-driven evaluation. The agent uses this data to assess model quality dynamically via **JIT Context Loading** - initially receiving lightweight references (PGS IDs), then loading full metadata on-demand.

#### Implementation Status

- **Implemented**: 
    - `PGSCatalogClient` for API queries.
    - `QualityMetrics` data schema (Pydantic model matching `shared/contracts/api.ts`).
    - `QualityEvaluator.extract_metrics()` for structured metadata extraction from raw API responses.

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
    1. Query neighbors where `p_value < 0.05` (rg Significance).
    2. Filter neighbors where `h2_z > 2` (Heritability Validity).
    3. Rank neighbors by a weighted score of **$r_g^2 \times h^2_{proxy\_node}$** to favor proxies that are both highly correlated and biologically viable for PRS transfer.
- **Output**: Prioritized list of genetically related traits (Proxies) to serve as search candidates for Module 1.

#### Implementation Status

- **Implemented**: 
    - `KnowledgeGraphService` wrapping `GWASAtlasGCClient`.
    - Dynamic Graph Construction (Nodes/Edges).
    - Filter: `p < 0.05` significance threshold applied.
    - **Node Heritability**: `get_neighbors()` now queries `GWASAtlasClient` (heritability module) and populates $h^2$ attributes for each graph node.
    - **Weighted Scoring**: `get_prioritized_neighbors()` method ranks neighbors by $r_g^2 \times h^2$ score, excluding nodes without $h^2$ data.
    - **ID Mapping**: `GWASAtlasGCClient` now supports bidirectional mapping via `get_trait_name_by_id()` and `get_trait_id_by_name()` methods.
- **Not Implemented**:
    - None. Module 2 core functionality is complete.

### Module 3 - Toolset

#### Implementation Status

- **Not Implemented**:
    - **Web Search Client (Consensus Retrieval)**: Wrapper for Google Search/PubMed to fetch **Clinical Guidelines and Review Papers**. Purpose: To answer "What is the current clinical consensus and SOTA method for this disease?"
    - **PGS Stats Aggregator (Market Benchmarking)**: Tool to calculate statistical distributions (e.g., top 10% AUC) from the catalog. Purpose: To answer "How does this candidate compare to the global average?"
    - **GWAS Atlas Interface (Theoretical Calibration)**: (Extends Module 2) Explicitly used to fetch $h^2$ limits. Purpose: To answer "Is the model's performance theoretically plausible given the trait's heritability?"

### Module 4 - System Prompt

#### LLM-Driven Quality Thresholds

Instead of hard-coded heuristic tiers, we will leverage the **Large Lange Model** to determine model quality dynamically.

- **Mechanism**: The Agent will receive the structured metadata (fields listed above) in its context window.
- **Prompt Logic**: The system prompt will instruct the LLM to evaluate models.
- **Evolution Note**: Initial metadata-based judgments may be limited. Subsequent **Tool-Driven JIT Context Loading** (e.g., autonomously invoking tools for deep methodology scrutiny, study design validation, or cross-referencing external benchmarks) enables the **Co-scientist Expert Scrutiny** phase. This ensures that the agent resolves high-stakes ambiguity through first-hand evidence to reach a definitive scientific judgment, while efficiently managing the attention budget.

#### Implementation Status
- **Not Implemented**:
    - **LLM Prompt Logic**: The dynamic reasoning prompt ("Plan-and-Solve") to consume these grades is part of Phase 2 (Module 4).
    - **Co-Scientist Expert Selection**: Logic to construct the **"Evaluation Reference Frame"** using the three knowledge tools (Theoretical $h^2$, Market Stats, Clinical Consensus) to strictly filter qualified models.