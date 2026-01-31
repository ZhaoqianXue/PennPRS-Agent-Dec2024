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

The agent's capabilities are organized into **three external Tool Sets** (Action Space) and one internal **Reasoning & Persona** (Cognitive Space):

- **PRS Model Tools**:
    <!-- For direct model searching, metadata retrieval, and model filtering/selection. -->
    - **`prs_model_pgscatalog_search`**: Searches for trait-specific PRS models and retrieves full metadata.
        - *Purpose*: To retrieve all available PRS models associated with a specific trait and return comprehensive metadata fields, providing the full raw data required for downstream filtering and evaluation.
    - **`prs_model_web_search`**: Wrapper for Google Search/PubMed to fetch *Clinical Guidelines and Review Papers*. 
        - *Purpose*: To enable the LLM to acquire extensive PRS knowledge and become a PRS expert, ensuring it can excellently perform PRS model selection tasks.
    - **`prs_model_performance_profiler`**: Calculates statistical distributions across all retrieved candidate models.
        - *Purpose*: To provide a holistic performance landscape for the entire pool of retrieved models, enabling the LLM Agent to statistically distinguish and select candidates based on their standing within the global distribution.
    - **`prs_model_genetic_parameters`**: Fetches $h^2$ and $r_g$ data for a given trait.
        - *Purpose*: To assist the Agent in selecting or filtering PRS models by providing theoretical performance bounds ($h^2$) and identifying genetic proxies ($r_g$).

- **Genetic Graph Tools**:
    <!-- For traversing Knowledge Graphs ($h^2$, $r_g$) and providing scientific validation. -->
    - **`genetic_graph_get_neighbors`**: Traverses the Knowledge Graph to find **genetically correlated traits**.
        - *Purpose*: To identify traits that share a significant genetic basis with the target trait, providing the initial candidates for cross-disease model recommendation.
    - **`genetic_graph_rank_correlated_traits`**: Ranks **genetically correlated traits** based on heritability and genetic correlation strength.
        - *Purpose*: To prioritize candidate proxy traits by weighting their genetic overlap ($r_g$) against their own genetic signal strength ($h^2$), ensuring recommendations focus on the most biologically and statistically viable alternatives.
    - **`genetic_graph_verify_study_power`**: Fetches study metadata (sample size, cohorts) to assess the statistical reliability of the correlation.
        - *Purpose*: To provide the LLM with the underlying statistical evidence (sample sizes, population composition) of the correlation data, enabling the Agent to perform quality control and filter out noisy or underpowered genetic links.
    - **`genetic_graph_cross_validate_mechanism`**: Cross-references shared genetic loci/genes (via Open Targets/PheWAS) to provide biological rationale for the correlation.
        - *Purpose*: To construct a biological reasoning context by identifying shared genetic loci or target genes, transforming a statistical correlation into a mechanistic justification for model transfer.

- **PennPRS Tools**:
    <!-- For interfacing with the PennPRS backend for autonomous model training. -->
    - **`pennprs_train_model`**: Interfaces with the PennPRS backend to initiate and monitor autonomous model training.
        - *Purpose*: To provide a pathway for generating high-quality, trait-specific models when existing models are insufficient, ensuring the Agent can offer a complete solution from discovery to implementation.

- **Reasoning & Persona (Internal)**: The central logic responsible for "fine-dining" answer synthesis, ensuring every response is reasoned, evidence-backed, and maintains the specialized co-scientist persona.

## Implementation Plan

1.  **Phase 1: Foundation**

    - **Module 1: PGS Catalog Data Schema**: Define the data interface and metadata extraction for PGS models.

    - **Module 2: Knowledge Graph**: Integrate `genetic_correlation` and `heritability` into a discovery system for **genetically correlated traits**.

2.  **Phase 2: Agent Core**

    The following engineering constraints are **mandatory** (derived from LLM Agentic Engineering Knowledge Base):

    - **Module 3: Tools**
        - Wrap **PRS Model, Genetic Graph, and PennPRS** functionalities as callable tool interfaces using `domain_action` prefixing.
        - **Static Tool Binding with Masking**: All tools defined at session start; availability controlled via logit masking, not dynamic injection. *(Manus: Mask, Don't Remove)*
        - **Consistent Tool Naming**: Use standardized domain prefixes (e.g., `domain_action`) for efficient logit mask grouping. *(Manus: Prefix-Based Action Selection)*
        - **Self-Contained & Robust**: Each tool must be error-tolerant with unambiguous input/output schemas. *(Anthropic: Tool Design)*
        - **Minimal Viable Tool Set**: Curate the smallest set covering functionality; avoid ambiguous decision points. *(Anthropic: Tool Curation)*
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
- **Not Implemented**:
    
### Module 2 - Knowledge Graph Definition

#### GWAS Atlas Data Schema

Based on `data/heritability/gwas_atlas/gwas_atlas.tsv` and `data/genetic_correlation/gwas_atlas/gwas_atlas_gc.tsv`, the following fields are available for constructing the Knowledge Graph.

##### 1. Heritability Dataset (`data/heritability/gwas_atlas/gwas_atlas.tsv`)

| Field Name | Description | Note |
| :--- | :--- | :--- |
| **`id`** | Internal GWAS Atlas numeric ID for the study | |
| **`PMID`** | PubMed Identifier of the publication | |
| **`Year`** | Year of publication | |
| **`File`** | Link or name of the source summary statistics file | |
| **`Website`** | Source website for the data | |
| **`Consortium`** | Research consortium (e.g., PGC, UKB) | |
| **`Domain`** | Top-level trait category (e.g., Psychiatric) | |
| **`ChapterLevel`** | ICD-10 based chapter classification | |
| **`SubchapterLevel`** | Specific subchapter classification | |
| **`Trait`** | Human-readable trait name | Used for labeling nodes |
| **`uniqTrait`** | **Primary Key**. Unique string identifier for the trait-study pair | Links to GC dataset |
| **`Population`** | Ancestry composition of the cohort | Default: EUR |
| **`Ncase`** | Number of cases (for binary traits) | |
| **`Ncontrol`** | Number of controls (for binary traits) | |
| **`N`** | **Total Sample Size**. Total number of individuals | Key for study prioritization |
| **`Genome`** | Genome build (e.g., hg18, hg19) | |
| **`Nsnps`** | Number of SNPs used in the heritability analysis | |
| **`Nhits`** | Number of genome-wide significant hits reported | |
| **`SNPh2`** | **Observed scale SNP heritability ($h^2_{obs}$)** | Main node attribute |
| **`SNPh2_se`** | Standard error of $h^2_{obs}$ | |
| **`SNPh2_z`** | **Z-score of $h^2_{obs}$ ($h^2\_Z$)** | Used for heritability validity |
| **`SNPh2_l`** | Liability scale SNP heritability ($h^2_{lia}$) | |
| **`SNPh2_l_se`** | Standard error of $h^2_{lia}$ | |
| **`LambdaGC`** | Genomic inflation factor ($\lambda_{GC}$) | |
| **`Chi2`** | Mean $\chi^2$ statistic | |
| **`Intercept`** | LD Score Regression intercept | |
| **`Note`** | Additional notes (e.g., population prevalence used for liability scale) | |
| **`DateAdded`** | Date the record was added to GWAS Atlas | |
| **`DateLastModified`** | Date of last record update | |

##### 2. Genetic Correlation Dataset (`data/genetic_correlation/gwas_atlas/gwas_atlas_gc.tsv`)

| Field Name | Description | Note |
| :--- | :--- | :--- |
| **`id1`** | Identifier for Trait 1 | Corresponds to `id` in Heritability TSV |
| **`id2`** | Identifier for Trait 2 | Corresponds to `id` in Heritability TSV |
| **`rg`** | **Genetic Correlation Coefficient ($r_g$)** | Primary edge weight |
| **`se`** | Standard error of $r_g$ | |
| **`z`** | Z-score of $r_g$ | |
| **`p`** | **P-value of $r_g$** | Used for significance filtering |
| **`gcov_int`** | Genetic covariance intercept | |
| **`gcov_int_se`** | Standard error of the intercept | |

#### Data Reality Analysis

The GWAS Atlas datasets form a natural graph structure, but with a critical nuance:

| Dataset | Format | Granularity |
|:---|:---|:---|
| Heritability | Node list | **Study-level** (each row = one Study) |
| Genetic Correlation | Edge list | **Study-pair-level** (each edge = one Study1-Study2 pair) |

**Critical Insight**: The `id` in both datasets refers to **Study**, not **Trait**. The same Trait can have multiple Studies:

| Trait | Study Count |
|:---|:---:|
| High-density lipoprotein cholesterol | 31 |
| Waist-hip ratio | 30 |
| Body Mass Index | 25 |
| Schizophrenia | 4 |

This means a single Trait-pair (e.g., HDL vs BMI) may have up to 31 x 25 = 775 edges at the Study level.

#### Graph Schema: Trait-Centric with Study Provenance

**Design Principle**: Each Trait has exactly **ONE node**, but retains **ALL Study information** as provenance.

##### Node Schema (Traits)

| Attribute | Type | Description |
|:---|:---|:---|
| `trait_id` | string | Canonical trait name (`uniqTrait`). **Primary Key**. |
| `domain` | string | Top-level category (e.g., Psychiatric) |
| `chapter_level` | string | ICD-10 chapter classification |
| `h2_meta` | float | **Meta-analyzed $h^2$** (inverse-variance weighted) |
| `h2_se_meta` | float | SE of meta-analyzed $h^2$ |
| `h2_z_meta` | float | Z-score of meta-analyzed $h^2$ |
| `n_studies` | int | Number of Studies aggregated |
| `studies` | array | All Studies for this Trait (full provenance) |

- **Data Source**: `src/server/modules/heritability/gwas_atlas_client.py`
- **Study Provenance**: Each element in `studies` contains `{study_id, pmid, year, population, n, snp_h2, snp_h2_se, snp_h2_z, consortium, ...}`.
- **NA Handling**: Studies without valid $h^2$ estimates are excluded from meta-analysis but retained in provenance.

##### Edge Schema (Genetic Correlations)

| Attribute | Type | Description |
|:---|:---|:---|
| `source_trait` | string | Source trait canonical name |
| `target_trait` | string | Target trait canonical name |
| `rg_meta` | float | **Meta-analyzed $r_g$** (inverse-variance weighted) |
| `rg_se_meta` | float | SE of meta-analyzed $r_g$ |
| `rg_z_meta` | float | Z-score of meta-analyzed $r_g$ |
| `rg_p_meta` | float | P-value of meta-analyzed $r_g$ |
| `n_correlations` | int | Number of Study-pair correlations aggregated |
| `correlations` | array | All Study-pair correlations (full provenance) |

- **Data Source**: `src/server/modules/genetic_correlation/gwas_atlas_client.py`
- **Constraint**: No self-loops (edges between Studies of the same Trait are excluded).

##### Aggregation Strategy: Inverse-Variance Weighted Meta-Analysis

Both Node ($h^2$) and Edge ($r_g$) aggregation use the same fixed-effect meta-analysis formula:

$$\theta_{meta} = \frac{\sum_i w_i \cdot \theta_i}{\sum_i w_i}, \quad w_i = \frac{1}{SE_i^2}$$

$$SE_{meta} = \frac{1}{\sqrt{\sum_i w_i}}$$

$$Z_{meta} = \frac{\theta_{meta}}{SE_{meta}}, \quad P_{meta} = 2 \cdot \Phi(-|Z_{meta}|)$$

Where $\theta$ represents either $h^2$ (for nodes) or $r_g$ (for edges).

This approach:
- Weights estimates by precision (1/SE^2), giving more influence to well-powered studies.
- Provides a single, consolidated estimate per Trait (node) or Trait-pair (edge).
- Retains all individual estimates in `studies` (node) / `correlations` (edge) arrays for transparency.
- Maintains full provenance for reproducibility and sensitivity analysis.

#### Interaction Logic (Dynamic Service)

The Knowledge Graph is implemented as a **Virtual/Dynamic Graph**, constructed on-demand with Trait-level aggregation.

- **Input**: Target Trait (e.g., "Alzheimer's disease").
- **Graph Construction**:
    1. **Node Aggregation**: Group Studies by `uniqTrait`, apply inverse-variance weighted meta-analysis for $h^2$.
    2. **Edge Aggregation**: For each Trait pair, apply inverse-variance weighted meta-analysis for $r_g$.
    3. **Self-Loop Removal**: Exclude edges where source and target are the same Trait.
- **Traversal & Prioritization**: 
    1. Query neighbors where `|rg_z_meta| > 2` (Meta-analyzed $r_g$ significance, ~p < 0.05).
    2. Filter neighbors where `h2_z_meta > 2` (Meta-analyzed heritability validity).
    3. Rank neighbors by weighted score: **$r_{g,meta}^2 \times h^2_{meta}$** to favor traits that are both highly correlated and biologically viable for PRS transfer.
- **Output**: Prioritized list of **genetically correlated traits** to serve as search candidates for Module 1.

#### Implementation Status

- **Implemented (v1 - Study-Level, Legacy)**: 
    - `KnowledgeGraphService` with `GWASAtlasGCClient`.
    - Dynamic Graph Construction (Nodes/Edges).
    - Filter: `p < 0.05` significance threshold.
    - **Node Heritability**: `get_neighbors()` queries `GWASAtlasClient` and populates $h^2$ attributes.
    - **Weighted Scoring**: `get_prioritized_neighbors()` ranks neighbors by $r_g^2 \times h^2$ score.
    - **ID Mapping**: Bidirectional mapping via `get_trait_name_by_id()` and `get_trait_id_by_name()`.

- **Implemented (v2 - Trait-Centric with Meta-Analysis)**:
    - **Data Models**: `TraitNode`, `GeneticCorrelationEdgeMeta`, `TraitCentricGraphResult` with full schema per spec.
    - **Meta-Analysis Pipeline**: `inverse_variance_meta_analysis()` utility function implementing the formula.
    - **TraitAggregator**: Groups Studies by `uniqTrait`, applies meta-analysis, populates `h2_meta`, `h2_se_meta`, `h2_z_meta`, `n_studies`, `studies[]`.
    - **EdgeAggregator**: Groups Study-pairs by Trait-pair, applies meta-analysis, populates `rg_meta`, `rg_se_meta`, `rg_z_meta`, `rg_p_meta`, `n_correlations`, `correlations[]`.
    - **Self-Loop Removal**: Edges between Studies of the same Trait are excluded during aggregation.
    - **New Service Methods**:
        - `get_trait_node(trait_id)`: Returns `TraitNode` with meta-analyzed heritability.
        - `get_prioritized_neighbors_v2(trait_id, rg_z_threshold, h2_z_threshold)`: Trait-level prioritization with Z-score filtering.
        - `get_trait_centric_graph(trait_id)`: Returns complete `TraitCentricGraphResult`.
    - **Unified Filtering**: Uses `|rg_z_meta| > 2` and `h2_z_meta > 2` (Z-score based, consistent approach).

- **Not Implemented**:
    - None. Module 2 core functionality is complete.

### Module 3 - Tools

#### Tool Definitions

1.  **PRS Model Tools**
    - `prs_model_pgscatalog_search`
    - `prs_model_web_search`
    - `prs_model_performance_profiler`
    - `prs_model_genetic_parameters`

2.  **Genetic Graph Tools**
    - `genetic_graph_get_neighbors`
    - `genetic_graph_rank_correlated_traits`
    - `genetic_graph_verify_study_power`
    - `genetic_graph_cross_validate_mechanism`

3.  **PennPRS Tools**
    - `pennprs_train_model`


#### Implementation Status

- **Implemented**:
    -   `PGSCatalog Search` (wrapped via `PGSCatalogClient` in Module 1).
- **Not Implemented**:


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