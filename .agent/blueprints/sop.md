# Standard Operating Procedure

## Title
PennPRS Agent

## Target Journal
Nature Genetics

## Brainstorming
- Focus on PRS model recommendation applications. (Take Alzheimer's disease (AD) as the example)
- Take features from AD PRS models available on PGS Catalog.
- If there is matched diseases, select the best one.
- If there is no matched disease, we can (i) selected genetically related diseases (one or more); (2) train the model on PennPRS. 
- We may use h2, genetic correlation, and base model embedding information to first build a knowledge graph among diseases. How to weight these resources? 
- Need validation, All of US? 
- Write initial version of prompts (i) same disease (ii) cross diseases, talking with GPT for design, and we can further refine. 
- Start with some selected diseases (cancer, mental diseases, neurodegenetive diseses, heart diseases) to build up the pipeline.
- **Contribution1: The first Benchmarking for PGS Catalog models, and how AI tools can select the model**
    - Overlap with All of US phenotypes for the phenotype space.
    - Benchmarking all PGS Catalog models on All of US, get a performance matrix.
    - `data/all_of_us/num_cases_1000.csv` is a list of traits with number of cases > 1000 in All of US. There are 1511 traits in total, which is a bit large. We have to select around 100 traits based on sample size and disease category. Some traits are parent level and some are children level. A parent level disease may have several subcategories. We can research and select about 100 traits.
- **Contribution2: Understand how the GPT-5 use these captured PRS model features (sample size, ancestry, method, training cohort, etc.)** (Mapping Step 1)
    - If there are issues, we can correct and add domain principles [how human PRS researcher select PRS models for AD]
    - Check the initial performance from GPT. 
- **Contribution3: LLM-based local graph around AD https://kumo.ai/research/recommendation-systems-llms-graph-transformers/ (Improving recommendation systems with LLMs and Graph Transformers)** (Mapping Step 2a)
    - We may use "genetic similarity information" learned by GPT  (from non-AD available models in PGS Catalog) and other data resources. 
    - With this local graph, we can build a graph around AD, such as including BD, CD, DD, ED, FD, etc.
    - Then we can recommend non-AD models for AD. 
    - We aim to show that add local graph can improve over not-using graph. Especially when there is no matched disease, the performance is better. 
    - Output: 
        (1) AD models, evaluation/score. 
        (2) AD-related models. 
    - Check the initial performance from GPT. 

## Contributions

This paper makes the following contributions:

- **C1: The First Comprehensive Benchmark of PGS Catalog Models** (Infrastructure)
    - **Claim**: We present the first systematic benchmarking of PGS Catalog models evaluated on a unified, large-scale cohort (All of Us), enabling direct cross-model performance comparison.
    - **Approach**: Select approximately 100 representative diseases/traits from All of Us (from `data/all_of_us/num_cases_1000.csv`, filtered by sample size and disease category), apply all corresponding PGS Catalog models to All of Us individual-level data, and produce a standardized **Performance Matrix** (traits x models x metrics).
    - **Nature**: Data engineering and computational evaluation. This contribution is independent of the AI Agent and serves as the **gold-standard ground truth** for validating C2 and C3.
- **C2: LLM-Based PRS Model Selection** (Core Project Value = Step 1)
    - **Claim**: PennPRS Agent, powered by GPT-5.2 with domain-specific tool calling, can select the best-performing PRS model from the full pool of PGS Catalog candidates, matching or exceeding naive selection baselines.
    - **Approach**: The Agent ingests model metadata (`[Agent + UI]` fields: sample size, ancestry, method, training cohort, performance metrics, etc.), constructs an Evaluation Reference Frame from evidence explicitly present in context, and outputs a ranked recommendation. `prs_model_performance_landscape` is always provided; `prs_model_domain_knowledge` is injected as optional additional evidence. Contribution2 uses a controlled Step 1 ablation that keeps the Step 1 prompt fixed and toggles only whether `prs_model_domain_knowledge` is present in context, while logging structured artifacts for feature attribution analysis.
    - **Validation**: C1's Performance Matrix serves as ground truth. We evaluate both default and ablation settings against the benchmark-optimal model for each disease, and quantify agreement/feature shifts.
- **C3: LLM-Based Local Graph for Cross-Disease Model Transfer** (Methodological Innovation = Step 2a)
    - **Claim**: For diseases without existing PRS models, PennPRS Agent leverages an LLM-based local knowledge graph to discover genetically related diseases and recommend their PRS models as effective substitutes.
    - **Approach**: Construct a local graph around the target disease (e.g., Alzheimer's disease) and apply a reranker that combines genetic graph structure (`transfer_score`, `rg_meta`, `n_correlations`), PGS availability pre-checks, and semantic similarity between target and neighbor traits. Inspired by [Kumo AI: Improving Recommendation Systems with LLMs and Graph Transformers](../knowledge/recommendation_system/kumo_recommendation_llm_graph_transformers.md).
    - **Validation**: C1's Performance Matrix serves as ground truth. Hold-out evaluation: for diseases with known PGS models, remove direct models from the candidate pool, compare transfer-score-only ranking vs local-graph reranking, and measure transferred-model performance against direct-model benchmark performance.

## LLM Agentic Engineering Knowledge Base

**To ensure the autonomy and reliability of the single llm agent system, this project must strictly adhere to the engineering standards detailed in the following documentation, each of which MUST be read in its entirety:**

- [Anthropic: Long-Running Agents](../knowledge/context_engineering/anthropic_long_running_agents.md)
- [Anthropic: Effective Context Engineering](../knowledge/context_engineering/anthropic_context_engineering.md)
- [Manus: Context Engineering](../knowledge/context_engineering/manus_context_engineering.md)

## Objective
The core objective is to evolve the **PRS (Polygenic Risk Score) Model Recommendation System** beyond simple direct matching by leveraging genetic architecture to enable intelligent cross-disease recommendations.

- **Recommendation Logic (Sequential Workflow)**:
    - **Step 1: Direct Match Assessment**: Search for existing models for the target disease.
        - *High-Quality Match*: If models exist and pass the quality threshold, recommend the best-performing one and **stop after Step 1**. **Always offer Direct Training as a follow-up option.**
        - *Sub-optimal Match*: If models exist but fail the quality threshold:
            - Recommend the best available **direct** model as a baseline.
            - **Proceed to Step 2** and also return the best **cross-disease** candidate models (neighbor traits) with genetic evidence.
        - *No Match*: If no direct models exist:
            - **Proceed to Step 2** and return the best **cross-disease** candidate models (neighbor traits) if available.
            - If Step 2 yields no viable transfer candidates, return `NO_MATCH_FOUND`.
    - **Step 2: Augmented Recommendation**: Triggered when direct models are insufficient or missing.
        - *Cross-Disease Transfer*: Discover **genetically related diseases** using the Knowledge Graph and provide biological validation for the correlation to support model transfer decisions.
        - *On-Demand Training*: Regardless of the recommendation outcome, the system always provides a "Direct Training" option at the end of the report. The **PennPRS** training pipeline is only initiated after explicit user interaction.
    - **Automation Note**: The recommendation generation (Steps 1 and 2) is **fully autonomous**. The training pipeline (PennPRS) is **on-demand**, triggered by explicit user confirmation from the recommendation report.

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

### Immutable Architectural Constraint: Single Agent + Tool Calling

To achieve the "Co-scientist" level of autonomy and reasoning, the system **MUST** be built as a **Single Agent Architecture** (powered by **gpt-5.2**). The agent acts as a unified central brain, utilizing **Dynamic Planning** and **Tool-Augmented Generation** to navigate the complex recommendation workflow within a **single persistent conversation state**. Multi-agent delegation or sub-agent hierarchies are strictly prohibited to maintain persona integrity and state coherence.

PennPRS Agent employs a Single Agent architecture with Tool Calling (powered by **gpt-5.2**). The agent operates within a single persistent conversation state and invokes specialized tools for PRS model search, genetic graph traversal, biological validation, and training configuration. The workflow is encoded as a **Sequential Recommendation Pipeline** with autonomous decision-making.

### High-Level Architecture

```
                          PennPRS Agent (Single Agent)
    ┌──────────────────────────────────────────────────────────────────────┐
    │                                                                      │
    │                    PennPRS Agent (gpt-5.2)                           │
    │                    ──────────────────────────                        │
    │                    Single persistent conversation state               │
    │                    Tool Calling enabled                               │
    │                    Co-Scientist Expert Persona                        │
    │                                                                      │
    ├──────────────────────────────────────────────────────────────────────┤
    │                                                                      │
    │   ┌──────────────────────────────────────────────────────────────┐   │
    │   │                    TOOL REGISTRY (9 Tools)                    │   │
    │   ├──────────────────────────────────────────────────────────────┤   │
    │   │                                                              │   │
    │   │  ┌───────────────────────────┐  ┌────────────────────────┐  │   │
    │   │  │  PRS MODEL TOOLS (3)      │  │ GENETIC GRAPH TOOLS (3)│  │   │
    │   │  │  ─────────────────        │  │ ───────────────────    │  │   │
    │   │  │  prs_model_pgscatalog     │  │ genetic_graph_get      │  │   │
    │   │  │  _search                  │  │ _neighbors             │  │   │
    │   │  │  prs_model_domain         │  │ genetic_graph_verify   │  │   │
    │   │  │  _knowledge               │  │ _study_power           │  │   │
    │   │  │  prs_model_performance    │  │ genetic_graph_validate │  │   │
    │   │  │  _landscape               │  │ _mechanism             │  │   │
    │   │  └───────────────────────────┘  └────────────────────────┘  │   │
    │   │                                                              │   │
    │   │  ┌───────────────────────────┐  ┌────────────────────────┐  │   │
    │   │  │ TRAIT RESOLUTION (2)      │  │ PENNPRS TOOLS (1)      │  │   │
    │   │  │ ────────────────────      │  │ ─────────────────      │  │   │
    │   │  │ trait_synonym_expand      │  │ pennprs_train_model    │  │   │
    │   │  │ resolve_efo_and           │  │                        │  │   │
    │   │  │ _mondo_ids               │  │                        │  │   │
    │   │  └───────────────────────────┘  └────────────────────────┘  │   │
    │   │                                                              │   │
    │   └──────────────────────────────────────────────────────────────┘   │
    │                                                                      │
    │   ┌──────────────────────────────────────────────────────────────┐   │
    │   │               EXTERNAL DATA SOURCES                          │   │
    │   │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌───────────┐  │   │
    │   │  │PGS Catalog│ │GWAS Atlas│ │ Open Targets │ │ PennPRS   │  │   │
    │   │  │  REST API │ │ (h², rg) │ │ + ExPheWAS   │ │Train. API │  │   │
    │   │  └──────────┘ └──────────┘ └──────────────┘ └───────────┘  │   │
    │   └──────────────────────────────────────────────────────────────┘   │
    │                                                                      │
    └──────────────────────────────────────────────────────────────────────┘
```

### Tool Calling Workflow

The Agent enforces the PennPRS Sequential Recommendation Pipeline through tool calling.
```
Step 1: Direct Match Assessment
───────────────────────────────
    prs_model_pgscatalog_search(target_trait)
           │
           ├──[No models found]──► Proceed to Step 2a
           ▼
    prs_model_performance_landscape(candidates) ──┐
    prs_model_domain_knowledge(query) [optional] ─┤
           │                                       │
           ▼                                       │
    ┌─────────────────────────────────────────────────────────────────┐
    │              LLM QUALITY EVALUATION (Evaluation Reference Frame)│
    │                                                                  │
    │  Agent combines:                                                 │
    │    - Candidate metadata (always)                                 │
    │    - Market Statistics (from performance_landscape)              │
    │    - Clinical Consensus (from domain_knowledge, if available)    │
    │                                                                  │
    │         ├──[HIGH_QUALITY]──► Generate Report (Direct)            │
    │         │                    + Offer "Train New Model" option     │
    │         │                    ──► DONE                            │
    │         │                                                        │
    │         ├──[SUB_OPTIMAL]──► Recommend best available as baseline │
    │         │                   ──► Proceed to Step 2a               │
    │         │                                                        │
    │         └──[NO_MATCH]──► Proceed to Step 2a                      │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘

Step 2a: Cross-Disease Transfer
───────────────────────────────
    trait_synonym_expand(target_trait, include_icd10=False, include_efo=False)
           │
           ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    NEIGHBOR DISCOVERY LOOP                        │
    │                                                                  │
    │  FOR each expanded_query:                                        │
    │    genetic_graph_get_neighbors(expanded_query)                    │
    │  Merge & deduplicate results by trait_id                         │
    │         │                                                        │
    │         ├──[ALL empty]──► OUTCOME: NO_MATCH_FOUND                │
    │         │                 ──► Generate Report + "Train" option    │
    │         ▼                                                        │
    │  neighbor_traits[] (sorted by transfer_score desc)               │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │           LOCAL GRAPH RERANKING (Rule + Linear Score)            │
    │                                                                  │
    │  1) Pre-check PGS IDs for top-K neighbors (IDs only)             │
    │  2) Compute local_graph_score for each neighbor using:            │
    │       - graph_transfer (transfer_score)                           │
    │       - graph_rg (|rg_meta|)                                      │
    │       - graph_power (n_correlations)                              │
    │       - pgs_hits (pre-check count)                                │
    │       - semantic_similarity (target vs neighbor trait text)       │
    │  3) Apply rule gates (e.g., min PGS hits)                         │
    │  4) Select top-N reranked neighbors for model hydration           │
    │                                                                  │
    │  IF no neighbor selected:                                         │
    │    OUTCOME: NO_MATCH_FOUND                                        │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘
           │
           ▼
    FOR each selected_neighbor_trait:
        prs_model_pgscatalog_search(selected_neighbor_trait)
           │
           ├──[No models]──► continue
           ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │               EVIDENCE COLLECTION (for Report)                   │
    │               ─────────────────────────────────                  │
    │  (These tools do NOT affect workflow decisions)                   │
    │                                                                  │
    │  trait_synonym_expand(target_trait + neighbor_trait)              │
    │         │                                                        │
    │         ▼                                                        │
    │  resolve_efo_and_mondo_ids(both traits)                          │
    │         │                                                        │
    │         ▼                                                        │
    │  genetic_graph_validate_mechanism(EFO/MONDO IDs)                 │
    │    ──► Biological evidence (shared genes, pathways)              │
    │                                                                  │
    │  genetic_graph_verify_study_power(target, neighbor)              │
    │    ──► Statistical evidence (sample sizes, cohorts)              │
    │                                                                  │
    │  prs_model_performance_landscape(neighbor_models)                │
    │    ──► Quality evaluation of neighbor models                     │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘
           │
           ▼
    IF qualified_transfer_models found:
        OUTCOME: CROSS_DISEASE
    ELSE:
        OUTCOME: NO_MATCH_FOUND

Step 2b: On-Demand Training (Human-in-the-Loop)
────────────────────────────────────────────────
    [Appended to ALL report types as a follow-up option]

    User clicks "Train New Model" in the report UI
           │
           ▼
    pennprs_train_model(target_trait, agent_context)
           │
           ▼
    UI displays pre-filled training configuration form
           │
           ▼
    User reviews/modifies ──► submits ──► PennPRS Training API
```

### Tool Sets Overview

The agent's capabilities are organized into **three external Tool Sets** (Action Space), **one Trait Resolution Tool Set** (Helper Tools), and one internal **Reasoning & Persona** (Cognitive Space):

- **PRS Model Tools**:
    <!-- For direct model searching, metadata retrieval, and model filtering/selection. -->
    - **`prs_model_pgscatalog_search`**: Searches for trait-specific PRS models and retrieves full metadata.
        - *Purpose*: To retrieve all available PRS models associated with a specific trait and return comprehensive metadata fields, providing the full raw data required for downstream filtering and evaluation.
    - **`prs_model_domain_knowledge`**: Retrieves snippets from a **curated local PRS knowledge base** focused on Step 1 model selection rules, endpoint integrity, transportability heuristics, and method priors.
        - *Purpose*: To inject stable, high-signal PRS selection guidance into the LLM context without relying on live web search. The curated local knowledge base is intentionally compact so the Agent receives consistent selection rules and avoids unbounded context pollution.
    - **`prs_model_performance_landscape`**: Calculates statistical distributions across all retrieved candidate models.
        - *Purpose*: To provide a holistic performance landscape for the entire pool of retrieved models, enabling the LLM Agent to statistically distinguish and select candidates based on their standing within the global distribution.

- **Genetic Graph Tools**:
    <!-- For traversing Knowledge Graphs ($h^2$, $r_g$) and providing scientific validation. -->
    - **`genetic_graph_get_neighbors`**: Traverses the Knowledge Graph to find **genetically correlated traits**, pre-ranked by transfer viability score ($r_g^2 \times h^2$).
        - *Purpose*: To identify and prioritize traits that share a significant genetic basis with the target trait, providing **ranked** candidates for cross-disease model recommendation. The deterministic ranking (genetic overlap weighted by signal strength) is applied automatically to avoid unnecessary tool call overhead.
  - **`genetic_graph_verify_study_power`**: Fetches detailed study-pair metadata (sample sizes, cohorts, populations) for a specific genetic correlation edge.
        - *Purpose*: To provide statistical evidence for the recommendation report. **This tool does NOT affect workflow decisions** - it is called after PRS models are found for genetically correlated traits to collect detailed study-pair provenance (sample sizes, cohorts, populations) for inclusion in the final report. Called on-demand after model discovery, not during initial neighbor discovery.
  - **`genetic_graph_validate_mechanism`**: Cross-references shared genetic loci/genes (via [Open Targets](https://platform.opentargets.org) and [ExPheWAS](https://exphewas.statgen.org)) to provide biological rationale for the correlation. **This tool is the Agent's "Biological Translator".**
        - *Purpose*: To provide biological evidence for the recommendation report. **This tool does NOT affect workflow decisions** - it is called after PRS models are found for genetically correlated traits to collect biological mechanism evidence (shared genes, pathways) for inclusion in the final report. The tool transforms "statistical correlation" into "biological causal logic":
            1. **Find shared loci/genes**: By interfacing with both [Open Targets](https://platform.opentargets.org) and [ExPheWAS](https://exphewas.statgen.org), identify which specific genes or genetic loci jointly control both diseases.
            2. **Construct explanatory context**: It provides not just a number, but an "evidence list". For example: "Both diseases share the pathogenic pathway of the IL23R gene."
            3. **Enrich report evidence**: The biological mechanism evidence from this tool provides scientific justification for cross-disease model recommendations in the final report, making the recommendation transparent and evidence-based.
        - *Input Requirements*: Requires EFO/MONDO IDs (not ICD-10 codes or trait names). The tool accepts both EFO and MONDO IDs (if available) and automatically tries both, merging results to maximize coverage. This is critical because some diseases may have data only in MONDO (e.g., Type 2 Diabetes) while others may have better coverage in EFO.
        - *Summary*: It is the Agent's "biological translator", responsible for providing biological evidence that supports cross-disease model recommendations in the final report. **Note**: This tool is called AFTER models are found, not as a decision gate.

- **Trait Resolution Tools** (Helper Tools):
    <!-- For optimizing trait queries and resolving disease ontology IDs. -->
    - **`trait_synonym_expand`**: Expands a trait query with synonyms and semantically equivalent terms using LLM.
        - *Purpose*: Discover alternative trait names that might be used in different data sources, ensuring comprehensive coverage across naming conventions. Used specifically for Knowledge Graph queries where exact trait name matching is required.
        - *Usage*: Called before `genetic_graph_get_neighbors` (excluding codes) and before `resolve_efo_and_mondo_ids` for `genetic_graph_validate_mechanism`. NOT used for `prs_model_pgscatalog_search` as PGS Catalog handles trait name matching internally.
    - **`resolve_efo_and_mondo_ids`**: Resolves both EFO and MONDO IDs for a trait by searching PGS Catalog and Open Targets.
        - *Purpose*: Get disease ontology IDs required by Open Targets API. Returns both EFO and MONDO IDs (if available) to maximize coverage, as some diseases may have data only in one ontology.
        - *Usage*: Called before `genetic_graph_validate_mechanism` to convert trait names to EFO/MONDO IDs.

- **PennPRS Tools**:
    <!-- For interfacing with the PennPRS backend for model training configuration. -->
    - **`pennprs_train_model`**: Generates a **recommended training configuration** based on the Agent's reasoning context (target trait, available GWAS data, recommended method, parameters).
        - *Purpose*: To prepare a pre-filled training request form for user review. The Agent synthesizes its scientific judgment into actionable configuration values. **This tool is triggered by explicit user action from any recommendation output.**
        - *Output*: JSON configuration object displayed in the UI as an editable form.
        - *Interaction Model*: **Human-in-the-Loop** — Agent proposes the configuration upon user request, user reviews/modifies if needed, then submits via UI action.

- **Reasoning & Persona (System Prompt)**: The cognitive core of the agent, implemented as a structured system prompt that:
    - **Encodes the Sequential Workflow**: Instructs the LLM to navigate Step 1 (Direct Match Assessment) → Step 2 (Augmented Recommendation) decision logic autonomously.
    - **Constructs the Evaluation Reference Frame**: Uses evidence explicitly present in context. Candidate metadata and `prs_model_performance_landscape` are always available; `prs_model_domain_knowledge` is incorporated only when injected as optional additional evidence.
    - **Maintains Co-Scientist Persona**: Ensures all responses are reasoned, evidence-backed, and reflect the specialized scientific partner voice.
    - **Manages Attention via Recitation**: Uses structured scratchpad/todo tracking to push critical objectives into the LLM's recent attention span.

## Implementation Plan

1.  **Phase 1: Foundation**

    - **Module 1: PGS Catalog Data Schema**: Define the data interface and metadata extraction for PGS models.

    - **Module 2: Knowledge Graph**: Integrate `genetic_correlation` and `heritability` into a discovery system for **genetically correlated traits**.

2.  **Phase 2: Agent Core**

    The following engineering constraints are **mandatory** (derived from LLM Agentic Engineering Knowledge Base):

    - **Module 3: Tools**
        - Wrap **PRS Model, Genetic Graph, and PennPRS** functionalities as callable tool interfaces using `domain_action` prefixing.
        - **Static Tool Binding with Masking**: All tools defined at session start; availability controlled via logit masking, not dynamic injection. *(Manus: Mask, Don't Remove)*
        - **Consistent Tool Naming**: Use standardized domain prefixes (e.g., `prs_model_*`, `genetic_graph_*`, `pennprs_*`) for efficient logit mask grouping. *(Manus: Prefix-Based Action Selection)*
        - **Self-Contained & Robust**: Each tool must be error-tolerant with unambiguous input/output schemas. *(Anthropic: Tool Design)*
        - **Minimal Viable Tool Set**: Curate the smallest set covering functionality; avoid ambiguous decision points. *(Anthropic: Tool Curation)*
        - **JIT Context Loading**: Tools return lightweight references (IDs, paths); full data loaded on-demand. *(Anthropic: Just-in-time context strategies)*
        - **File System as Context (Large Observations)**: Large tool observations MUST be persisted to disk and referenced by stable paths/IDs, not injected verbatim into the LLM context. *(Manus: Use the File System as Context)*
            - **Rule**: If a tool output exceeds a configured size threshold (e.g., >50KB JSON or >2,000 tokens equivalent), the tool MUST:
                1. Persist the full payload to a file (under `output/agent_artifacts/` or an equivalent runtime artifact directory).
                2. Return a compact in-context summary plus a **stable reference**: `{artifact_id, artifact_path, sha256, content_type, bytes, summary}`.
            - **Restorable Compression**: Context compaction MUST be reversible by preserving the `artifact_path` (and `url` when applicable). Never discard the reference.
            - **Human-safe**: Artifact paths must never include secrets; redact tokens/credentials before writing.
        - **Append-Only Context**: Serialize tool results deterministically; no mid-loop modification to preserve KV-cache. *(Manus: Design Around the KV-Cache)*
        - **Stable Prompt Prefix (KV-cache)**: Keep the system prompt + tool definitions prefix **bitwise stable** across turns/sessions. Avoid any dynamic tokens at the beginning of the prompt (e.g., timestamps, random IDs, run counters). *(Manus: Design Around the KV-Cache)*
            - **Hard rule**: Never include "Current time", "Today is ...", or per-request metadata in the system prompt header. If time is needed, retrieve it via a tool and place it in the append-only observation stream.
            - **Deterministic serialization**: For JSON-like tool outputs, enforce stable key ordering and canonical formatting (e.g., sorted keys, stable float rounding policy, stable whitespace).
        - **Cache Breakpoints (Optional)**: If the serving stack supports explicit cache breakpoints, place a breakpoint **after** the stable prefix (system prompt + tool schemas) and avoid moving it. *(Manus: Design Around the KV-Cache)*
        - **Error Trace Retention**: Failed tool calls remain in history as explicit feedback; no retry-and-hide. *(Manus: Keep the Wrong Stuff In)*

    - **Module 4: System Prompt**
        - **Persona Definition**: Define the Co-scientist Expert voice, tone, response patterns, and boundaries (what it will/won't do).
        - **Plan-and-Solve Decision Logic**: Develop the **gpt-5.2** prompt encoding the Sequential Workflow (L27-35) as structured decision steps with explicit transition conditions.
        - **Evaluation Reference Frame Construction**: Specify how the agent reasons from evidence explicitly present in context, with `prs_model_domain_knowledge` treated as optional additional evidence rather than a separate prompt policy.
        - **Tool Orchestration Protocol**: Define the logical flow for selecting and chaining tools. Specifically, guide the agent to use `genetic_graph_validate_mechanism` as a biological validator for traits discovered via `genetic_graph_get_neighbors`.
        - **Human-in-the-Loop Integration**: Define how the agent provides the "Train New Model" option at the end of every recommendation report, waiting for user interaction before calling `pennprs_train_model`.
        - **Scratchpad/State Format**: Define the `todo.md` style internal state tracking format for workflow progress. *(Manus: Manipulate Attention Through Recitation)*
        - **Output Report Templates**: Define JSON/Markdown templates for recommendation reports with required fields and evidence citations.
        - **Error Recovery Protocol**: Specify agent behavior when tools fail (retry logic, fallback strategies, escalation to human).
        - **Prompt Altitude**: Write at the right abstraction level; avoid hardcoding brittle logic or vague guidance. *(Anthropic: Right Altitude)*

## Implementation Log

### Module 1 - PGS Catalog Data Schema

#### PGS Catalog Models Available Fields
Based on `src/server/core/pgs_catalog_client.py` and `pgscatalog/PGS_Catalog/rest_api/serializers.py`, the following fields are available from the PGS Catalog API. 

**Target Classification**: `[Agent + UI]` fields are serialized into the LLM context for scientific reasoning, whereas `[UI Only]` fields are passed exclusively to the frontend for comprehensive model detail presentation to minimize agent context noise.

| Field Name (API Key) | Example1 | Example2 | Description | Source | Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`id`** | PGS000831 | PGS000018 | Unique Model ID | Score | [Agent + UI] |
| **`name`** | Total_cholesterol_PGS | metaGRS_CAD | Model display name | Score | [UI Only] |
| **`trait_reported`** | Total cholesterol | Coronary artery disease | Original reported trait | Score | [Agent + UI] |
| **`trait_additional`** | null | null | Additional trait information | Score | [UI Only] |
| **`trait_efo`** | total cholesterol measurement | coronary artery disease | EFO Ontology mappings | Score | [Agent + UI] |
| **`method_name`** | Pruning of FDR filtered SNPs | metaGRS | Algorithm used (e.g. LDpred2) | Score | [Agent + UI] |
| **`method_params`** | FDR < 5%, r^2 < 0.2 | metaGRS log(HR) mixing... | Parameters used in the method | Score | [UI Only] |
| **`variants_number`** | 1,032 | 1,745,179 | Count of variants in model | Score | [Agent + UI] |
| **`variants_interactions`** | 0 | 0 | Variant interactions info | Score | [UI Only] |
| **`variants_genomebuild`** | hg19 | hg19 | Genome build (e.g. GRCh37) | Score | [UI Only] |
| **`weight_type`** | beta | NR | Type of weights used | Score | [UI Only] |
| **`ancestry_distribution`** | GWAS: EUR (100%) | GWAS: AFR (100%) | Detailed ancestry breakdown | Score | [Agent + UI] |
| **`publication.title`** | Genetic Predisposition Impacts... | Genomic Risk Prediction of... | Full publication title | Score/Performance | [Agent + UI] |
| **`publication.journal`** | Nat Commun | medRxiv Preprint | Journal or venue name | Score/Performance | [Agent + UI] |
| **`publication.doi`** | 10.1038/s41467-020-16483-3 | 10.1101/2025.05.15.25327513 | DOI | Score/Performance | [UI Only] |
| **`date_release`** | 2021-07-29 | 2019-10-14 | Date the score was released | Score | [Agent + UI] |
| **`license`** | CC BY-NC-ND 4.0 | PGS obtained from the... | Usage license | Score | [UI Only] |
| **`ftp_scoring_file`** | https://ftp.ebi.ac.uk/... | https://ftp.ebi.ac.uk/... | URL to original scoring file | Score | [UI Only] |
| **`ftp_harmonized_scoring_files`** | GRCh37, GRCh38 URLs | GRCh37, GRCh38 URLs | URL to harmonized scoring files | Score | [UI Only] |
| **`matches_publication`** | True | True | Flag if score matches publication | Score | [UI Only] |
| **`samples_variants`** | n=283,785 | n=382,026 | GWAS discovery sample size (samples used for variant selection) | Score | [UI Only] |
| **`samples_training`** | n=0 | n=3,000 | Samples used for training | Score | [Agent + UI] |
| **`performance_metrics`** | AUC: 0.63; full_model_auc: 0.91; classification_metrics: [...]; other_metrics: [...] | HR: 1.71, R2: 0.05; full_model_r2: 0.18; classification_metrics: [...]; other_metrics: [...] | Representative-record metrics summary. Top-level AUC/R2 are PRS-comparable metrics when explicitly available; full-model AUROC/R² and full Classification Metrics / Other Metrics from the selected validation record are also retained for sanity checking. | Performance | [Agent + UI] |
| **`phenotyping_reported`** | Total cholesterol | Incident coronary artery disease | Phenotype description in validation | Performance | [Agent + UI] |
| **`covariates`** | Age, sex, PCs(1-7), season | sex, genetic PCs (1-10)... | Covariates used in validation | Performance | [Agent + UI] |
| **`sampleset`** | null | null | Sample set used for validation | Performance | [UI Only] |
| **`validation_sample_size`** | n=482,629 | n=5,762 | Validation cohort sample size from the same representative validation record used for `performance_metrics` | Performance | [Agent + UI] |
| **`performance_comments`** | null | null | Additional performance notes | Performance | [UI Only] |
| **`associated_pgs_id`** | PGS000831 | PGS000018 | The PGS ID associated with performance | Performance | [UI Only] |

#### Agent Context Injection

The structured metadata fields above provide the foundational evidence for evaluation. The agent utilizes **JIT Context Loading** to dynamically construct a **Scientific Reasoning Context**—transforming lightweight model references into a rigorous evaluation frame by fetching candidate metadata, performance landscapes, and optional domain knowledge to guide scientific judgment.

**Target Classification**: The `[Agent + UI]` fields in the table above are serialized into the LLM context for scientific reasoning, whereas `[UI Only]` fields are passed exclusively to the frontend for comprehensive model detail presentation to minimize agent context noise.

**Combined Results Workflow**:
1. `prs_model_pgscatalog_search` returns only fields with Target `[Agent + UI]`; `[UI Only]` metadata such as `variants_genomebuild`, `samples_variants`, `publication.doi`, and `sampleset` is excluded from agent/LLM context.
   - For scores with multiple performance records, the agent-facing `performance_metrics`, `phenotyping_reported`, `covariates`, and `validation_sample_size` are aligned to one representative validation record: highest-result European validation if available, otherwise highest-result validation overall.
   - Representative-record selection prefers PRS-comparable metrics first (`PGS AUROC (no covariates)`, `PGS R2 (no covariates)`, or covariates-regressed-out PRS R²). If no PRS-comparable metric exists, full-model metrics are used only to choose the representative record, not to redefine the top-level PRS-comparable `performance_metrics.auc`.
   - The selected record keeps full `classification_metrics` and `other_metrics` instead of compressing them away.
2. **No AUC/R² pre-filtering**: All models from retrieval are included (aligned with C1 for consistency).
3. **Combined context injection**: The filtered search results and `prs_model_performance_landscape` results are always returned to the LLM. `prs_model_domain_knowledge` is injected simultaneously only when enabled for that run.
4. **LLM Decision**: The Agent makes a determination of **High-Quality Match / Sub-optimal Match / No Match**.

**Open Question**: For different Traits, should we implement different filtering standards, or trust that the LLM has this capability? (To be determined during implementation.)

**Pain Point (Trait/Disease-Conditioned Thresholding)**:
- Empirically, **the AUC gain curve is highly disease-specific**: different diseases exhibit dramatically different AUC improvements as GWAS sample size increases (and similarly for other variables such as `variants_number`, PRS method, and ancestry composition).
- Example evidence: see Fig. 3 in [Wang et al., 2020, *Nature Communications*](https://www.nature.com/articles/s41467-020-16483-3), where the projected AUC-vs-sample-size trajectories differ substantially across cancer types (different slopes, saturation points, and apparent ceilings).
- Implication for the Agent: **a single global heuristic threshold (e.g., fixed AUC cutoff or fixed N cutoff) is brittle** and may over-filter valid models for some diseases while under-filtering for others. The evaluation reference frame must allow **disease-conditioned interpretation** using `prs_model_performance_landscape` plus any additional evidence explicitly present in context, including `prs_model_domain_knowledge` when enabled, rather than hard-coded universal cutoffs.

#### Implementation Status

- **Implemented**: 
    - `PGSCatalogClient` for API queries.
    - `QualityMetrics` data schema (Pydantic model matching `shared/contracts/api.ts`).
    - `QualityEvaluator.extract_metrics()` for structured metadata extraction from raw API responses.
- **Not Implemented**:
    - #### Agent Context Injection

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
        - `get_edge_provenance(source_trait, target_trait)`: Returns detailed study-pair provenance for genetic correlation edges. Used by Module 3 `genetic_graph_verify_study_power` tool.
    - **Unified Filtering**: Uses `|rg_z_meta| > 2` and `h2_z_meta > 2` (Z-score based, consistent approach).

- **Not Implemented**:
    - None. Module 2 core functionality is complete.

### Module 3 - Tools

#### Tool Specifications

##### 1. PRS Model Tools

###### `prs_model_pgscatalog_search`

| Attribute | Specification |
|:---|:---|
| **Input** | `trait_query: str` — User's target trait (e.g., "Type 2 Diabetes", "Schizophrenia") |
| **Output** | `PGSSearchResult` — Filtered list of models with `[Agent + UI]` fields only |
| **Data Source** | PGS Catalog REST API (`/rest/score/search`) |
| **Dependency** | `PGSCatalogClient` (Module 1) |
| **AUC/R² Filter** | **DISABLED**. Includes all models from retrieval (no filter). Aligned with Contribution1 pgs_id_list for C2 consistency. |
| **Ranking** | **DISABLED**. Returns models in API raw order (PGS Catalog trait-search response order). No Z-score sorting. |
| **Top-N Limit** | **DISABLED**. Returns ALL filtered models (no truncation). Aligned with Contribution1 benchmarking; typical traits have 3-96 models, within LLM context capacity. |
| **Retrieval Alignment (C2)** | PGS Catalog `/trait/search`: full pagination (follow `next` until empty); collect **`associated_pgs_ids` only** (no `child_associated_pgs_ids`) to match Contribution1 `download_pgs` logic. |
| **Query Strategy** | **Call `prs_model_pgscatalog_search` directly with trait name** (no synonym expansion needed). PGS Catalog handles trait name matching internally and returns comprehensive results. Synonym expansion is unnecessary and adds overhead without significant benefit. |

```python
# Output Schema
class PGSSearchResult:
    query_trait: str
    total_found: int
    after_filter: int
    models: list[PGSModelSummary]  # [Agent + UI] fields only; all filtered models (Top-N strategy disabled)

class PGSModelSummary:
    id: str                    # PGS000025
    trait_reported: str
    trait_efo: str
    method_name: str
    variants_number: int
    ancestry_distribution: str
    publication: PublicationMetadata
    date_release: str
    samples_training: str
    performance_metrics: dict  # {auc: float|None, r2: float|None, pgs_only_auc: float|None, pgs_only_r2: float|None, full_model_auc: float|None, full_model_r2: float|None, incremental_auc: float|None, selected_performance_id: str, selected_validation_ancestry: str, record_count: int, classification_metrics: list[dict], other_metrics: list[dict], effect_sizes: list[dict], ...}
    phenotyping_reported: str
    covariates: str
    training_development_cohorts: list[str]  # union of cohort short names from training/development samples

class PublicationMetadata:
    title: str
    journal: str
```

###### `prs_model_domain_knowledge`

| Attribute | Specification |
|:---|:---|
| **Input** | `query: str` — Domain knowledge query (e.g., "PRS clinical utility for CAD", "AUC thresholds for clinical PRS") |
| **Output** | `DomainKnowledgeResult` — Structured snippets from the curated local knowledge base with trait-specific local heritability augmentation |
| **Data Source** | **Local curated Markdown knowledge base** — `src/server/core/knowledge/prs_model_domain_knowledge.md` + local heritability tables under `data/heritability/*` |
| **Dependency** | Local retrieval plus local heritability lookup |
| **Token Budget** | Max 5 snippets per query; compact local snippets only |

```python
# Knowledge Base Source
KNOWLEDGE_BASE_PATH = "src/server/core/knowledge/prs_model_domain_knowledge.md"

# Output Schema
class DomainKnowledgeResult:
    query: str
    full_document: str
    snippets: list[KnowledgeSnippet]
    source_type: str  # "local"

class KnowledgeSnippet:
    source: str
    section: str
    content: str
    relevance_score: float
```

###### `prs_model_performance_landscape`

| Attribute | Specification |
|:---|:---|
| **Input** | `candidate_models: list[PGSModelSummary]` — Candidate models from `prs_model_pgscatalog_search` (passed for workflow ergonomics) |
| **Output** | `PerformanceLandscape` — **Global** statistical reference frame (restricted fields) |
| **Data Source** | PGS Catalog REST API: `/rest/score/all` (metadata) + `/rest/performance/all` (AUC/R²) |
| **Dependency** | None (pure computation) |
| **Token Budget** | ~200 tokens (compact statistical summary) |

```python
# Output Schema
class PerformanceLandscape:
    total_models: int

    # IMPORTANT: Landscape must be restricted to the following 7 categories only:
    # 1) Ancestry
    # 2) Sample Size
    # 3) AUC
    # 4) R²
    # 5) Variants (SNPs)
    # 6) Training/Development Cohorts
    # 7) PRS Methods

    ancestry: dict[str, int]                     # counts by ancestry code (best-effort parse)
    sample_size: MetricDistribution              # training sample size distribution
    auc: MetricDistribution                      # PRS-comparable AUROC distribution
    r2: MetricDistribution                       # PRS-comparable R² distribution
    variants: MetricDistribution                 # variants_number distribution
    training_development_cohorts: dict[str, int] # counts by cohort short name
    prs_methods: dict[str, int]                  # counts by PRS method

# Aggregation Note (Global Reference):
# - The global landscape is computed across ALL scores in `/rest/score/all`.
# - AUC/R² are aggregated per PGS id using the same representative-record rule as candidate summaries.
# - Prefer explicit PRS-comparable metrics (`PGS AUROC (no covariates)`, `PGS R2 (no covariates)`,
#   or covariates-regressed-out PRS R²) from that selected validation record.
# - If a score reports only full-model AUROC/R², keep those for sanity checking in candidate metadata,
#   but count the comparable landscape AUC/R² as missing.

class MetricDistribution:
    min: float
    max: float
    median: float
    p25: float
    p75: float
    missing_count: int
```

##### 2. Genetic Graph Tools

###### `genetic_graph_get_neighbors`

| Attribute | Specification |
|:---|:---|
| **Input** | `trait_id: str` — Target trait canonical name (e.g., "Schizophrenia") |
| **Output** | `NeighborResult` — Pre-ranked list of genetically correlated traits |
| **Data Source** | GWAS Atlas (Module 2 Knowledge Graph) |
| **Dependency** | `KnowledgeGraphService.get_prioritized_neighbors_v2()` |
| **Ranking** | Auto-sorted by $r_g^2 \times h^2$ (descending) |
| **Filters** | `\|rg_z_meta\| > 2`, `h2_z_meta > 2` |
| **Token Budget** | ~100 tokens per neighbor; max 10 neighbors |
| **Trait Resolution** | Internally uses `resolve_trait_id()` which **only supports exact and alias matching** (no fuzzy matching). If no exact/alias match is found, the tool gracefully returns an empty neighbor list (`neighbors=[]`) rather than attempting broad token-overlap matching. This ensures that only reliable, semantically relevant traits are returned. |
| **Query Strategy** | **Use trait synonym expansion** (excluding codes) via `trait_synonym_expand(target_trait, include_icd10=False, include_efo=False)`. Call for each expanded query and merge neighbors (deduplicate by trait_id). **Do NOT use ICD-10/EFO codes** - GWAS Atlas data schema does not include trait codes (see L310-391: GWAS Atlas Data Schema - fields only include `Trait`, `uniqTrait`, `ChapterLevel`, etc., but no ICD-10/EFO/MONDO code fields). The synonym expansion provides semantic breadth, while internal trait resolution ensures accuracy by only accepting exact/alias matches. |

```python
# Output Schema
class NeighborResult:
    query_trait: Optional[str]  # Original user query (if resolved/mapped)
    resolved_by: Optional[str]  # Resolution method: exact | alias | none
    resolution_confidence: Optional[str]  # High | Moderate | Low
    target_trait: str
    target_h2_meta: float
    neighbors: list[RankedNeighbor]  # Empty list if no neighbors found (graceful handling)

class RankedNeighbor:
    trait_id: str
    domain: str           # e.g., "Psychiatric"
    rg_meta: float        # Genetic correlation
    rg_z_meta: float
    h2_meta: float        # Neighbor's heritability
    transfer_score: float # rg² × h²
    n_correlations: int   # Number of study-pairs aggregated
    # NOTE: h2_se_meta, rg_se_meta, rg_p_meta intentionally omitted for token efficiency.
    #       Use genetic_graph_verify_study_power for detailed provenance if needed.
```

###### `genetic_graph_verify_study_power`

| Attribute | Specification |
|:---|:---|
| **Input** | `source_trait: str`, `target_trait: str` — Trait pair to investigate |
| **Output** | `StudyPowerResult` — Detailed study-pair provenance for the edge |
| **Data Source** | GWAS Atlas GC dataset (Module 2) |
| **Dependency** | `KnowledgeGraphService.get_edge_provenance()` |
| **JIT Loading** | Called after PRS models are found for genetically correlated traits to collect statistical evidence for the report. **Does NOT affect workflow decisions.** |
| **Token Budget** | ~300 tokens (provenance details) |

```python
# Output Schema
class StudyPowerResult:
    source_trait: str
    target_trait: str
    rg_meta: float
    n_correlations: int
    
    correlations: list[CorrelationProvenance]

class CorrelationProvenance:
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
```

###### `genetic_graph_validate_mechanism`

| Attribute | Specification |
|:---|:---|
| **Input** | `source_trait_efo: str`, `target_trait_efo: str` — EFO IDs for both traits (required by Open Targets API). Optional: `source_trait_mondo: str`, `target_trait_mondo: str` — MONDO IDs for both traits. |
| **Output** | `MechanismValidation` — Shared genes/loci evidence |
| **Data Source** | Open Targets Platform API, PheWAS Catalog (ExPheWAS API) |
| **Dependency** | External API clients (Open Targets GraphQL, ExPheWAS REST) |
| **JIT Loading** | Called after PRS models are found for genetically correlated traits to collect biological evidence for the report. **Does NOT affect workflow decisions.** |
| **Token Budget** | ~500 tokens (biological evidence summary) |
| **Query Strategy** | **Requires EFO/MONDO IDs** (not ICD-10 codes or trait names). Use `resolve_efo_and_mondo_ids()` to get BOTH EFO and MONDO IDs for both traits. The tool automatically tries both IDs (if provided) and merges results by deduplicating gene targets and keeping the highest association score. This maximizes coverage since some diseases may have data only in MONDO (e.g., Type 2 Diabetes) while others may have better coverage in EFO. Open Targets Platform uses EFO/MONDO IDs, not ICD-10 codes. |

```python
# Output Schema
class MechanismValidation:
    source_trait: str
    target_trait: str
    
    shared_genes: list[SharedGene]
    shared_pathways: list[str]
    
    mechanism_summary: str  # LLM-digestible explanation
    confidence_level: str   # "High", "Moderate", "Low"

class SharedGene:
    gene_symbol: str       # e.g., "IL23R"
    gene_id: str           # ENSG ID
    source_association: float  # Disease A association score
    target_association: float  # Disease B association score
    druggability: str      # "High", "Medium", "Low"
    pathways: list[str]
```

##### 3. PennPRS Tools

###### `pennprs_train_model`

| Attribute | Specification |
|:---|:---|
| **Input** | Agent's reasoning context (trait, GWAS availability, method recommendation) |
| **Output** | `TrainingConfig` — Pre-filled form configuration for user review |
| **Data Source** | Agent's accumulated context + PennPRS API schema |
| **Dependency** | PennPRS API form schema |
| **Interaction** | **Human-in-the-Loop** — UI displays form, user submits |
| **Token Budget** | ~300 tokens (form configuration) |

```python
# Output Schema
class TrainingConfig:
    # Pre-filled by Agent
    target_trait: str
    recommended_method: str  # e.g., "LDpred2", "PRS-CS"
    method_rationale: str    # Agent's reasoning for method choice
    
    # Form fields (editable by user)
    gwas_summary_stats: str  # URL or file path
    ld_reference: str        # e.g., "1000G EUR"
    ancestry: str            # Target population
    validation_cohort: str   # Optional
    
    # Metadata
    agent_confidence: str    # "High", "Moderate", "Low"
    estimated_runtime: str   # e.g., "~2 hours"

# UI Action (not agent tool)
# User reviews form → clicks "Submit" → PennPRS API called
```

#### Engineering Constraints Compliance

| Constraint | Implementation |
|:---|:---|
| **Static Tool Binding with Masking** | All 7 core tools + 3 helper tools defined at session start; availability controlled via logit masking based on workflow state |
| **Consistent Tool Naming** | `prs_model_*`, `genetic_graph_*`, `pennprs_*` prefixes for efficient logit mask grouping |
| **Self-Contained & Robust** | Each tool has explicit Input/Output schema; error handling returns structured error objects |
| **Minimal Viable Tool Set** | 7 core tools + 2 helper tools (trait_synonym_expand, resolve_efo_and_mondo_ids) covering full workflow; no ambiguous decision points |
| **JIT Context Loading** | `verify_study_power` and `validate_mechanism` loaded on-demand, not during initial discovery |
| **Append-Only Context** | Tool results serialized deterministically; no mid-loop modification |
| **Error Trace Retention** | Failed tool calls remain in history with error details for Agent learning |

#### Implementation Status

- **Implemented**:
    - `prs_model_pgscatalog_search`: Wrapped via `PGSCatalogClient` (Module 1). No AUC/R² filter; returns all models from retrieval. `[Agent + UI]` fields. Optional `evaluated_pgs_whitelist` for Contribution2: when set (via `PENNPRS_CONTRIB2_EVALUATED_PGS_JSON`), only models in the All of Us evaluated set (N Models) are returned.
    - `prs_model_performance_landscape`: `src/server/core/tools/prs_model_tools.py` - Pure computation tool for statistical distributions.
    - `prs_model_domain_knowledge`: `src/server/core/tools/prs_model_tools.py` - Intended implementation for Contribution2 Step 1. Retrieves from the curated local Markdown knowledge base `src/server/core/knowledge/prs_model_domain_knowledge.md` and augments it with trait-specific local heritability summaries from `data/heritability/*`.
    - `genetic_graph_get_neighbors`: `src/server/core/tools/genetic_graph_tools.py` - Uses `KnowledgeGraphService.get_prioritized_neighbors_v2()`.
    - `genetic_graph_verify_study_power`: `src/server/core/tools/genetic_graph_tools.py` - Uses `KnowledgeGraphService.get_edge_provenance()`.
    - `genetic_graph_validate_mechanism`: `src/server/core/tools/genetic_graph_tools.py` - Integrated support for both [Open Targets](https://platform.opentargets.org) and [ExPheWAS](https://exphewas.statgen.org). Supports both EFO and MONDO IDs, automatically tries both and merges results to maximize coverage.
    - `pennprs_train_model`: `src/server/core/tools/pennprs_tools.py` - Intelligent method recommendation + PennPRS API submission.
    - **Helper Tools**:
        - `trait_synonym_expand`: `src/server/core/tools/trait_tools.py` - LLM-based trait synonym expansion for comprehensive coverage. Called at the start of the workflow to expand trait queries for ALL subsequent tool calls.
        - `resolve_efo_and_mondo_ids`: `src/server/modules/disease/recommendation_agent.py` - Multi-source EFO/MONDO ID resolution via PGS Catalog and Open Targets.

- **Not Implemented**:
    - **Web-Search for Domain Knowledge**: Integration with a web search API for live data retrieval from authoritative domains (transition from local RAG to real-time search).


### Module 4 - System Prompt

#### Prompt Architecture

The System Prompt is structured into **four functional layers**:

| Layer | Purpose | Example Content |
|:---|:---|:---|
| **Identity & Persona** | Establishes the agent's voice and boundaries | "You are a PRS Co-scientist..." |
| **Workflow Encoding** | Instructs the Sequential Workflow logic | "Step 1: Search for direct models..." |
| **Tool Orchestration** | Guides tool selection and chaining | "When quality is sub-optimal, use genetic_graph_get_neighbors..." |
| **Output Schema** | Defines report structure | JSON/Markdown template requirements |

#### Co-Scientist Persona Definition

| Attribute | Specification |
|:---|:---|
| **Voice** | Expert, collaborative, evidence-driven |
| **Tone** | Precise, confident when supported by evidence; appropriately uncertain when data is limited |
| **Boundaries** | Will not hallucinate performance metrics; will cite sources; will recommend human review for edge cases |
| **Response Pattern** | Reasoning → Evidence → Recommendation → Caveats |

#### LLM-Driven Quality Thresholds

Instead of hard-coded heuristic tiers, we leverage the **Large Language Model** to determine model quality dynamically.

- **Mechanism**: The Agent receives structured metadata (`[Agent + UI]` fields from Module 1) in its context window.
- **Evaluation Reference Frame**: The Agent constructs a scientific judgment framework using:
    1. **Candidate metadata + validation evidence** from `prs_model_pgscatalog_search`: What does the model explicitly report about phenotype alignment, performance, ancestry, method, and study design?
    2. **Market Statistics** via `prs_model_performance_landscape`: How does this model compare to the distribution of all available models?
    3. **Optional Clinical Consensus** via `prs_model_domain_knowledge`: When provided, what additional endpoint-integrity, transportability, or disease-specific cautions should be applied?
- **Evolution Note**: Initial metadata-based judgments may be limited. Optional **Tool-Driven JIT Context Loading** through `prs_model_domain_knowledge` enables the **Co-scientist Expert Scrutiny** phase for Step 1 decisions without changing the core Step 1 prompt.

#### Sequential Workflow Encoding

The prompt must encode the following decision logic from the Objective section (L27-35):

```
STEP 1: DIRECT MATCH ASSESSMENT
1. Call prs_model_pgscatalog_search directly with target_trait (no synonym expansion needed)
2. Evaluate models using candidate metadata and prs_model_performance_landscape
3. If enabled for the run, inject prs_model_domain_knowledge as additional Step 1 evidence
4. For Contribution2 analysis, support a controlled ablation mode where the Step 1 prompt stays fixed and only the presence/absence of `prs_model_domain_knowledge` in context is toggled; log Step 1 decisions as structured artifacts.
IF direct_models_exist AND quality >= HIGH_THRESHOLD:
    OUTCOME: DIRECT_HIGH_QUALITY
ELIF direct_models_exist AND quality < HIGH_THRESHOLD:
    RECOMMEND best_available_as_baseline
    PROCEED_TO STEP 2A
ELSE:  # no direct models
    PROCEED_TO STEP 2A

STEP 2A: CROSS-DISEASE TRANSFER
1. Call trait_synonym_expand(target_trait, include_icd10=False, include_efo=False) to get expanded synonyms (excluding codes)
2. Query genetic_graph_get_neighbors for EACH expanded query and merge results (deduplicate by trait_id) → neighbor_traits[]
   - **Note**: If `genetic_graph_get_neighbors` returns an empty neighbor list (`neighbors=[]`), this indicates that no exact/alias matches were found in the Knowledge Graph. The tool gracefully handles this case without errors. If ALL expanded queries yield empty results, proceed directly to OUTCOME: NO_MATCH_FOUND.
3. IF neighbor_traits[] is empty:
   OUTCOME: NO_MATCH_FOUND
ELSE:
   - **Local Graph Reranking (Rule + Linear Score)**:
     - Build a candidate pool from merged `neighbor_traits[]`.
     - Run a **fast PGS pre-check** (IDs only; no heavy hydration) for top-K neighbors.
     - Compute `local_graph_score` for each candidate:
       - `graph_transfer` (transfer_score)
       - `graph_rg` (|rg_meta|)
       - `graph_power` (n_correlations)
       - `pgs_hits` (pre-check count)
       - `semantic_similarity` (target vs neighbor trait text similarity)
     - Apply rule gates (e.g., minimum PGS hit count) and select top-N neighbors after reranking.
     - If no neighbor is selected, proceed to OUTCOME: NO_MATCH_FOUND.
   - For each selected `neighbor_trait`:
     - Call `prs_model_pgscatalog_search` directly with `neighbor_trait` (no synonym expansion needed).
     - IF models found:
       - **For genetic_graph_validate_mechanism**: Resolve disease ontology IDs for target_trait and neighbor_trait:
           - For target_trait: Expand synonyms (excluding codes) using trait_synonym_expand
           - For neighbor_trait: Expand synonyms (excluding codes) using trait_synonym_expand
           - Then use `resolve_efo_and_mondo_ids()` to get BOTH EFO and MONDO IDs for both traits, using a multi-source strategy:
               - Prefer PGS Catalog trait mapping first (PGS `/trait/search` results and/or score `trait_efo`).
               - Only query Open Targets when PGS sources are missing or ambiguous (small score gap between top candidates).
               - Do not cache trait→ID mappings to avoid stale external ontology updates; rely on deterministic scoring and explicit ambiguity handling.
       - Call genetic_graph_validate_mechanism with EFO and MONDO IDs (if available) - the tool will automatically try both and merge results to maximize coverage. **Purpose**: Collect biological evidence for the report (does NOT affect workflow decision).
       - Call genetic_graph_verify_study_power(source_trait=target_trait, target_trait=neighbor_trait). **Purpose**: Collect statistical evidence for the report (does NOT affect workflow decision).
       - Evaluate model quality using prs_model_performance_landscape
4. IF qualified_transfer_models found:
    OUTCOME: CROSS_DISEASE
ELSE:
    OUTCOME: NO_MATCH_FOUND

STEP 2B: HUMAN-IN-THE-LOOP TRAINING (ON-DEMAND)
- Regardless of OUTCOME (DIRECT, CROSS_DISEASE, or NO_MATCH), the final report MUST include a "Train New Model" option.
- IF user_triggers_training:
    - Generate pennprs_train_model configuration based on target_trait context.
```

**Tool Usage Clarification**: PRS Model Tools are used in BOTH Step 1 (for target trait) AND Step 2a (for related traits). The distinction is the **trait being queried**, not the workflow phase.

#### KV-cache Safety Rules (Prompt Prefix Stability)

The prompt must be designed to maximize KV-cache reuse in agentic loops:

- **Stable prefix requirement**: The prefix containing the system prompt and tool schemas MUST remain identical across turns.
- **Forbidden at prompt head**: timestamps, request IDs, random seeds, "today's date", run counters, or any dynamic metadata.
- **If time is required**: fetch it via a tool and record it in the append-only observation stream (never inside the stable prefix).
- **Tool schema stability**: tool definitions must not be injected/removed mid-run; control availability via masking.

#### Scratchpad / State Management

Following the "Attention Manipulation via Recitation" principle, the agent maintains a structured internal state:

```markdown
## Current Task Progress
- [x] Step 1: Query PGS Catalog for "Type 2 Diabetes" (target trait)
- [x] Step 1: Evaluate 5 models against performance landscape
- [x] Step 1 Decision: SUB-OPTIMAL match (best AUC=0.65, below clinical threshold)
- [x] Step 2a: Query Knowledge Graph for genetically correlated traits
- [x] Step 2a: Found related trait: "Obesity"
- [x] Step 2a: Validated biological mechanism for "Obesity" (shared FTO pathway)
- [x] Step 2a: Query PGS Catalog for "Obesity" → 8 models found
- [ ] Step 2a: Evaluate "Obesity" models against performance landscape
- [ ] Step 2a Decision: Recommend cross-disease model OR report no match
- [ ] On-Demand: Offer "Train New Model" option in final report
...
```

This format ensures critical objectives remain in the LLM's recent attention span across tool call boundaries.

#### Output Report Template

The report structure varies by `recommendation_type`. Note that the "Train New Model" option is a UI action provided at the end of ALL report types.

```json
{
  "recommendation_type": "DIRECT_HIGH_QUALITY | DIRECT_SUB_OPTIMAL | CROSS_DISEASE | NO_MATCH_FOUND",
  "primary_recommendation": {
    "pgs_id": "PGS000025",           // For DIRECT_* and CROSS_DISEASE
    "source_trait": "...",            // For CROSS_DISEASE only
    "confidence": "High | Moderate | Low",
    "rationale": "..."
  },
  "alternative_recommendations": [...],
  
  // Step 1 Evidence (DIRECT_HIGH_QUALITY, DIRECT_SUB_OPTIMAL)
  "direct_match_evidence": {
    "models_evaluated": 5,
    "performance_metrics": {...},       // From prs_model_performance_landscape
    "clinical_benchmarks": [...]        // From prs_model_domain_knowledge
  },
  
  // Step 2 Evidence - Cross-Disease (CROSS_DISEASE only)
  "cross_disease_evidence": {
    "source_trait": "Obesity",
    "rg_meta": 0.85,
    "transfer_score": 0.72,
    
    // From genetic_graph_get_neighbors
    "related_traits_evaluated": ["Obesity", "Metabolic Syndrome"],
    
    // From genetic_graph_validate_mechanism (supports genetic correlation interpretation and transfer rationale)
    "shared_genes": ["FTO", "MC4R"],
    "biological_rationale": "Both traits share obesity-related genetic architecture.",
    
    // From prs_model_pgscatalog_search(related_trait)
    "source_trait_models": {
      "models_found": 8,
      "best_model_id": "PGS000XXX",
      "best_model_auc": 0.78
    }
  },

  // Step 2 Trace (DIRECT_SUB_OPTIMAL, NO_MATCH_FOUND, CROSS_DISEASE)
  // Required to make cross-disease reasoning auditable and demo-friendly.
  "genetic_graph_ran": true,
  "genetic_graph_neighbors": ["Obesity", "Metabolic Syndrome"],
  "genetic_graph_evidence": [
    {
      "neighbor_trait": "Obesity",
      "rg_meta": 0.85,
      "transfer_score": 0.72,
      "neighbor_models_found": 8,
      "neighbor_best_model_id": "PGS000XXX",
      "neighbor_best_model_auc": 0.78,
      "mechanism_confidence": "High",
      "mechanism_summary": "Both traits share 6 gene(s). Top: FTO. Pathways: ...",
      "shared_genes": ["FTO", "MC4R"],
      "study_power": {
        "n_correlations": 12,
        "rg_meta": 0.84
      }
    }
  ],
  "genetic_graph_errors": [],
  
  "caveats_and_limitations": [...],
  "follow_up_options": [
    {
      "label": "Train New Model on PennPRS",
      "action": "TRIGGER_PENNPRS_CONFIG",
      "context": "Provides best-in-class configuration recommendation"
    }
  ]
}
```

**Field Scoping by Recommendation Type**:

| Field | DIRECT_HIGH_QUALITY | DIRECT_SUB_OPTIMAL | CROSS_DISEASE | NO_MATCH_FOUND |
|:---|:---:|:---:|:---:|:---:|
| `direct_match_evidence` | Required | Required | Optional | - |
| `cross_disease_evidence` | - | - | Required | - |
| `genetic_graph_evidence` | - | Required | Required | Required |
| `follow_up_options` | Required | Required | Required | Required |

#### Engineering Constraints Compliance

| Constraint | Implementation |
|:---|:---|
| **Prompt Altitude** | Encode high-level decision logic; avoid hardcoding specific thresholds (let LLM reason) |
| **Attention via Recitation** | File-backed `todo.md` is updated and re-injected near the end of context (`output/agent_artifacts/todo_<id>.md`) |
| **Persona Consistency** | Identity layer loaded at start of every conversation |
| **Error Trace Retention** | Prompt instructs agent to acknowledge and reason about failed tool calls |
| **JIT Context Loading** | Prompt guides agent to call deep-dive tools only when needed |
| **File System as Context** | Large context payloads are externalized to `output/agent_artifacts/` and referenced by stable artifact metadata |

#### Implementation Status

- **Implemented**:
    - **Centralized Prompts**: System prompts consolidated in `src/server/core/system_prompts.py`.
    - **Persona Definition**: Co-scientist voice/tone guidelines and boundary specifications.
    - **Plan-and-Solve Prompt Structure**: Layered prompt architecture with workflow encoding (Step 1 + Report prompts).
    - **Evaluation Reference Frame Logic**: Explicit instructions to use evidence present in context, with `prs_model_domain_knowledge` treated as optional additional evidence rather than a separate prompt policy.
    - **Scratchpad Format**: File-backed `todo.md` recitation via `src/server/core/recitation_todo.py` + `src/server/modules/disease/recommendation_agent.py`.
    - **File System as Context**: Deterministic artifact externalization via `src/server/core/agent_artifacts.py` + `output/agent_artifacts/`.
    - **Output Report Schema**: JSON template for final recommendations.
    - **Error Recovery Protocol**: Tool failure handling and graceful fallback instructions.
    - **Low-Mechanism Handling**: Weak mechanism evidence routed to alternatives with caveats.
