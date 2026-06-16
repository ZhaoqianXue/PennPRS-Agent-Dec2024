# PRS Agent Paper Framing: LLM Orchestration + Agent Harnesses + Skill/Tool Layer

Status: paper-facing engineering positioning, last updated 2026-05-19.
Scope: this document is the preferred engineering framing for PRS Agent as an integrated system. It should be used when writing the Nature Genetics manuscript, response letters, architecture diagrams, and engineering-methods text.
Related: `docs/architecture/prs_tool_and_skill_layer.md`, `experiments/contribution2/recommendation/docs/harness_engineering_positioning.md`, `experiments/contribution3/transfer/docs/harness_engineering_positioning.md`, `experiments/contribution2/recommendation/docs/2026_harness_engineering_sources.md`.

Proposal-to-paper mapping note: after the 2026-05-14 group discussion, proposal `C.4.1-C.4.4 Aim 2a-2d` should be treated as upstream material for the paper Results section, including the Results overview. Proposal `C.4.4 Aim 2e: Agent design` should be rewritten as compressed methodology / Methods-facing text, not as the paper Results overview.

Writing-use note: this document is technical provenance for the paper Methodology, Supplement, and rewritten proposal Aim 2e. When material from this document is used in proposal Aim 2a-2d or the paper Results, translate it into PRS research language and avoid foregrounding harness/ReAct/Skill terminology. For Methods, lead with the positive architecture rather than with defensive claims about single-agent or multi-agent boundaries.

## Core Thesis

Paper-facing architecture should frame PRS Agent as an integrated PRS decision system with three ordered layers:

1. an LLM orchestration layer that interprets user requests and coordinates PRS capabilities;
2. a task-specific agent harness layer that implements within-phenotype recommendation and cross-phenotype transfer;
3. a PRS Model Skill and tool layer that exposes the PRS Model Skill, PGS retrieval, PRS evidence tools and PennPRS interfaces.

This framing is clearer than `foundation-model controller` plus `evidence-and-skill substrate`. It also avoids implying that PRS Agent contains a separate central agent inside itself. A reader should immediately know what each layer does: the LLM orchestration layer coordinates the PRS task, the task-specific agent harness layer defines the recommendation procedures, and the PRS Model Skill and tool layer supplies reusable model-review guidance and executable PRS interfaces.

The clean paper-facing formulation is:

```text
PRS Agent
├── Layer 1: LLM orchestration layer
│   └── LLM-powered task orchestration: interprets the user's scientific goal,
│       formulates the PRS task, selects the appropriate harness and synthesizes
│       the returned evidence into a final explanation
│
├── Layer 2: Task-specific agent harness layer
│   ├── within-phenotype PGS recommendation
│   │   └── Skill/H2-grounded generator -> final selection step
│   └── cross-phenotype transfer
│       └── planner -> evidence gathering -> ranking -> critic review
│
└── Layer 3: PRS Model Skill and tool layer
    ├── PRS Model Skill (`prs_model_evaluator`): trait-agnostic PGS record
    │   evaluation rules, empirical caveats, metric interpretation,
    │   ancestry/endpoint/overfitting checks and domain decision heuristics
    ├── PGS Catalog retrieval and model hydration tools
    ├── PRS evidence tools: heritability lookup, genetic correlation estimation
    │   and Open Targets evidence
    └── PennPRS model-training interface and downstream analysis planning

Planned proposal-facing extension
└── PRS recommendation record
    └── persistent PRS analysis state: phenotype definition,
        candidate model universe, evidence snapshots, model landscape,
        recommendation rationale, training configuration, and validation plan
```

PGS candidate sets, source-phenotype bundles, evidence summaries, model landscapes, training configurations, validation plans and recommendation records are artifacts produced by the task-specific agent harness layer or PennPRS interfaces through calls into the PRS Model Skill and tool layer. They should not be presented as top-level architecture components.

For current paper-facing cross-phenotype writing, genetic-correlation and Open Targets evidence should be framed as supporting evidence that documents the plausibility of a proposed transfer. Do not foreground a generic biology-retrieval tool or imply that these evidence channels replace model-level PGS evaluation.

In one sentence:

> PRS Agent is a PRS decision system built around LLM orchestration, task-specific agent harnesses and a PRS Model Skill and tool layer: the orchestration layer interprets the user's PRS goal and selects the appropriate route; the agent harness layer executes within-phenotype recommendation or cross-phenotype transfer; and the Skill and tool layer provides the PRS Model Skill, PGS retrieval, PRS evidence tools and PennPRS interfaces.

## Layer 1: LLM Orchestration Layer

Use `LLM orchestration layer`, `LLM-driven orchestration` or `PRS task orchestration` in manuscript-facing Methods. Avoid `central PRS agent` as the primary term because PRS Agent is intended to be presented as a single-agent system; naming an internal `central agent` can make the architecture sound like DeepRare-style multi-agent coordination. Avoid `foundation-model controller` because it sounds like a model-management component rather than the scientific coordinator of a PRS task.

The LLM orchestration layer is responsible for:

- understanding the user's scientific goal;
- formulating the request as a PRS model-recommendation, transfer, model-development, downstream-analysis or explanation task;
- invoking the corresponding harnessed specialist capability;
- passing structured inputs to the task-specific agent harness layer or PennPRS interfaces;
- synthesizing harness outputs into a user-facing scientific explanation.

Nature sample alignment:

- DeepRare uses `central host agent` for the component that coordinates system-wide diagnostic operations.
- DeepRare is a multi-agent system, so `central host agent` is not the best paper-facing analogy for PRS Agent.
- TissueLab uses LLM orchestration language for the component that plans and executes model workflows; this is the better analogy for a single-agent PRS system.
- Cognitive Layer Architecture uses `controller` in the context of model-agnostic scaffolding, but that term is less clear for PRS Agent unless it is paired with the PRS task role.

Recommended wording:

> The LLM orchestration layer interprets the user's scientific goal, formulates the corresponding PRS task and invokes the task-specific harness required for model recommendation, transfer, model development or downstream analysis.

Avoid:

- "c2 and c3 are two agents."
- "PRS Agent is a multi-agent system."
- "Every stage is autonomous."
- "central PRS agent" as a standalone component name in the paper opening.
- "foundation-model controller" as a standalone component name in the paper opening.

## Layer 2: Task-Specific Agent Harness Layer

The task-specific agent harness layer is the main agent harness engineering contribution. It translates a PRS recommendation task selected by the orchestration layer into a bounded scientific decision procedure with explicit inputs, stage contracts, tool boundaries, evidence handoffs, final-selection logic and evaluation traces. The harness layer sits between orchestration and tools: it decides when and how PRS tools and the PRS Model Skill are used for within-phenotype recommendation or cross-phenotype transfer.

This layer includes two paper-facing harness families:

- within-phenotype PGS recommendation;
- cross-phenotype transfer.

Recommended wording:

> The task-specific agent harness layer implements the scientific decision procedure for PRS model recommendation. Within-phenotype recommendation uses a bounded generator-selection harness, whereas cross-phenotype transfer uses staged source-phenotype search, model selection and critic review.

Avoid:

- describing c2 and c3 as separate user-facing agents;
- implying that every harness stage is autonomous;
- calling simple deterministic data retrieval a harness by itself.

## Layer 3: PRS Model Skill And Tool Layer

The third layer should be named as a layer of PRS Model Skill and tools, not as an `evidence-and-skill substrate`. The project does not contain PGS data inside the agent itself. Candidate PGS sets and evidence artifacts are obtained through tools that query or hydrate external resources, and they are then interpreted through the PRS Model Skill. `PRS Model Skill and tool layer` foregrounds the reusable Skill as a manuscript contribution while preserving the executable tool boundary.

This layer includes:

- the PRS Model Skill, implemented internally as `prs_model_evaluator`, which provides trait-agnostic PGS record evaluation rules and empirical caveats;
- PGS Catalog search, retrieval and model hydration tools;
- PRS evidence tools, including heritability lookup, genetic correlation estimation and Open Targets evidence when enabled;
- PennPRS model-training interface and downstream analysis planning.

The PRS Model Skill belongs in this layer because it is a reusable Skill resource consumed by multiple harnesses. It should not be merged conceptually with the PGS candidate set itself. The candidate set is data returned by retrieval tools; the Skill supplies the PRS model-selection criteria used to evaluate records in that candidate set.

Recommended wording:

> The PRS Model Skill and tool layer exposes the reusable Skill guidance and executable interfaces needed by the harnesses: the PRS Model Skill for trait-agnostic PGS record evaluation, PGS Catalog retrieval and hydration, PRS evidence tools and PennPRS analysis interfaces.

Avoid:

- "the substrate constructs candidate PGS sets" without naming retrieval tools;
- implying that PGS Catalog data live inside the agent;
- implying that the PRS Model Skill decides source-phenotype relevance by itself.

## Harness Details: Within-Phenotype And Cross-Phenotype

The harness layer is where most of the engineering novelty lives. The correct framing is task-specific orchestration around a base LLM, with explicit evidence, stage contracts, tool boundaries and evaluation loops.

### c2: Same-Trait Generator-Evaluator Harness

c2 should be framed as a harness-engineered same-trait PGS-selection capability inside PRS Agent.

Current production candidate:

- production wrapper: `experiments/contribution2/recommendation/scripts/run_experiment_top5_holistic_lift.py`;
- architecture: R38-style top-5 holistic hidden-benchmark reranking;
- PRS evidence inputs: sealed PRS Model Skill implementation (`prs_model_evaluator`) plus heritability records;
- Stage 1: generator proposes a primary pick plus bounded top-5 shortlist from Skill/H2-enriched context;
- Stage 2: final selection step chooses the recommended PGS from the shortlist.

Recommended wording:

> c2 implements a Skill-grounded generator-selection harness for same-trait PGS selection. A generator proposes a bounded top-5 shortlist from the PRS Model Skill and heritability evidence, and a final selection step chooses the recommended model under a hidden-benchmark selection frame.

This is harness engineering because it separates candidate generation from final selection and uses a bounded selection layer over sealed PRS evidence inputs. It should not be described as a pure ReAct agent. Pure ReAct was tested and rejected for c2 because the model under-fetched Skill sections on this fixed-candidate benchmark.

Avoid:

- "c2 is a true ReAct agent."
- "c2 autonomously decides when to read all Skill/H2 evidence" if the kept production path preloads the Skill/H2 evidence.
- "c2 is only a prompt" because the kept architecture is a generator-selection harness with N=2 fresh verification over the iterD floor.

### c3: Cross-Trait Hybrid Agent Harness

c3 is the stronger agent-harness case study.

Current framing:

- workflow scaffold: Scout -> Judge -> Pick -> Critic;
- embedded ReAct stage: GATHER;
- GATHER lets the LLM choose tool calls and termination through `RoundDirective.tool_calls` and `RoundDirective.done`;
- tool surface: h2, genetic correlation batch estimation, Open Targets overlap and PGS model hydration;
- persistent evidence summary, especially genetic correlation estimation and Open Targets overlap for cross-trait plausibility;
- independent evaluator: Critic.

Recommended wording:

> c3 implements a hybrid agent harness for cross-trait transfer. A planner proposes candidate probes, a ReAct evidence-gathering agent uses domain tools to build an evidence summary, including genetic correlation and Open Targets evidence when enabled, ranking stages select transferable models, and an independent critic audits the final recommendation.

This is the cleanest module-level match to the 2026 harness-engineering vocabulary: planner/generator/evaluator separation, LLM-directed tool use, evidence handoffs, and independent critique.

Avoid:

- "c3 is a multi-agent system" unless we later introduce multiple collaborating autonomous agents.
- "all c3 stages are agents"; only GATHER is the true ReAct-style agentic stage.
- "c3 should convert every stage to an agent"; well-defined decision points are better left as workflow stages.

## PRS Model Skill Details

The PRS Model Skill is the shared Skill resource inside the PRS Model Skill and tool layer. Its runtime implementation is `prs_model_evaluator`. It should not be reduced to "a prompt."

Recommended wording:

> The PRS Model Skill is a sealed, version-controlled domain knowledge layer shared across PRS Agent capabilities. It encodes empirical PGS-selection heuristics, endpoint-fidelity checks, metric interpretation rules, ancestry considerations, and leakage/overfitting cautions.

c2 and c3 consume the same Skill differently because the task shapes differ:

- c2 uses the Skill as a full PRS evidence input because the same-trait fixed-candidate task benefits from complete priming and bounded evaluation.
- c3 uses staged Skill views and evidence summaries because cross-trait transfer requires progressive disclosure and iterative evidence gathering.

This preserves the PRS Model Skill framing without forcing every module into the same ReAct shape.

## Planned Extension: PRS Recommendation Record

Status: TODO / proposal-facing future work. This component can be proposed in the rewritten, methodology-facing Aim 2e using `we will implement`, but it should not be described as current completed functionality outside a Preliminary Results section.

The planned record should not be framed as generic conversational memory or user-preference memory. It should be a persistent PRS recommendation record that preserves the evidence trail behind each recommendation: normalized phenotype definitions, target population and ancestry context, candidate PRS model sets, model-landscape summaries, heritability evidence, cross-trait genetic correlation and Open Targets evidence, shortlist decisions, final recommendations, PennPRS training configurations, database versions, and validation plans.

Recommended proposal framing:

> We will generate a PRS recommendation record for each request to preserve the full evidence trail behind the recommendation. This record will include the normalized phenotype definition, target population, candidate PRS model set, model-landscape summary, heritability evidence, cross-trait genetic correlation and Open Targets evidence, shortlist decisions, final recommendation, PennPRS training configuration, database versions, and validation plan. The record will allow users and reviewers to trace each recommendation back to concrete PRS evidence, making the analysis reproducible and updateable under human oversight.

Design constraints:

- do not describe this as generic agent memory, user-preference memory, or long-term conversation memory;
- store PRS evidence artifacts, model metadata, provenance, database versions, training configurations, and validation plans;
- make the recommendation record inspectable by users and reviewers;
- treat benchmark failures and user corrections as logged evidence for expert review and future benchmark-gated maintenance, not as a core Aim 2e architecture claim.

## Recommended Manuscript Paragraph

> PRS Agent is organized around LLM orchestration, a task-specific agent harness layer and a PRS Model Skill and tool layer for PRS decision-making. The orchestration layer formulates the user's scientific goal as a PRS task and invokes the appropriate route. The agent harness layer executes the recommendation procedure: within-phenotype recommendation uses a Skill-grounded generator-selection design, whereas cross-phenotype transfer uses staged evidence gathering, ranking and critic review. The Skill and tool layer provides the PRS Model Skill, PGS Catalog retrieval and hydration, PRS evidence tools and PennPRS analysis interfaces.

## Claims We Can Defend

- PRS Agent uses LLM orchestration to invoke harness-engineered specialist capabilities.
- c2 is a Skill-grounded generator-selection harness, not merely a single-shot prompt.
- c3 is a hybrid agent harness with one true ReAct evidence-gathering stage.
- The PRS Model Skill and tool layer exposes the shared PRS Model Skill, PGS retrieval, PRS evidence tools and PennPRS interfaces.
- Harness architecture is load-bearing because c2 R38 improves over iterD-final across Hit@1-Hit@5 in N=2 fresh verification, and c3's iter11 paper-facing harness improves over the no-all-tools baseline while retaining explicit evidence gathering and critique.

## Claims To Avoid

- Do not claim c2 is a pure ReAct/autonomous tool-use agent.
- Do not claim c2 and c3 are separate agents.
- Do not claim PRS Agent is a multi-agent system.
- Do not claim every c3 stage is agentic.
- Do not claim the Skill is just prompt text.
- Do not claim the system is an autonomous medical decision-maker; it is harness-engineered scientific assistance for PGS analysis.

## 2026 Source Alignment For Methods

The framing above is aligned with 2026 Nature-family and ICLR agent-system literature. These references should be treated as the external architecture anchors when writing the paper Methods.

- **LLM orchestration for scientific execution.** CellVoyager (Nature Methods 2026) frames a computational biology agent as an LLM-built system that generates and implements analyses inside an executable notebook environment. SR-Scientist (ICLR 2026) similarly elevates the LLM from a proposal module to a long-horizon, tool-driven scientific agent that writes code, analyzes data, evaluates hypotheses and optimizes from feedback. This supports `LLM orchestration layer` as the top layer rather than `central agent`.
- **Harness/scaffold as a load-bearing evaluation unit.** AstaBench (ICLR 2026 oral) argues that agent evaluation requires reproducible tools, standardized interfaces, agent classes and trajectories; HAL (ICLR 2026) formalizes a cost-aware, third-party harness for evaluating agents across benchmarks and reports full traces. This supports making `task-specific agent harness layer` a first-class Methods architecture component, not an implementation detail.
- **Tool layer as executable scientific interface.** Tools are under-documented (ICLR 2026) treats tool retrieval and tool descriptions as an independent bottleneck for tool-using agents. This supports naming PGS Catalog retrieval, evidence tools and PennPRS interfaces explicitly instead of hiding them inside a generic evidence layer.
- **Skills as reusable procedural/domain capabilities.** PolySkill (ICLR 2026) separates a skill's abstract goal from its execution and studies reusable skills in agents. SkillsBench (2026 benchmark) explicitly separates skills, agent harnesses and models into distinct abstraction layers. The SoK on Agentic Skills (2026 preprint; not venue-final) defines skills as reusable procedural capabilities with applicability conditions, execution policies, termination criteria and reusable interfaces. These sources support treating the PRS Model Skill as a reusable PRS skill inside the PRS Model Skill and tool layer rather than as a prompt.
- **Biomedical agent naming contrast.** DeepRare (Nature 2026) and CellAgent (ICLR 2026) use central-host / multi-agent language because they are explicitly multi-agent systems. PRS Agent should not borrow that naming in the paper opening. TissueLab and CellVoyager are better style analogies for single-agent or orchestration-centered biomedical systems.

Engineering guidance from Anthropic and OpenAI remains useful for implementation wording, but it should be treated as secondary to the 2026 paper anchors above when drafting Nature Genetics Methods:

- Anthropic distinguishes workflows from agents; this supports describing c2 as a generator-selection harness and c3's GATHER as the true agentic stage.
- Anthropic's 2026 harness-design writing emphasizes planner/generator/evaluator separation, evidence handoffs and independent review roles.
- Anthropic's Agent Skills guidance defines skills as organized instruction/resource bundles with progressive disclosure.
- OpenAI Agents SDK documentation supports describing agentic applications as models configured with tools, guardrails, structured outputs, state and tracing.
- OpenAI skill-evaluation guidance supports evaluating both outcomes and process traces when making claims about PRS Model Skill value.

## References

- Alber, S. et al. [CellVoyager: AI CompBio agent generates new insights by autonomously analyzing biological data](https://www.nature.com/articles/s41592-026-03029-6). Nature Methods 23, 749-759 (2026). Nature-style anchor for single-agent computational biology execution in a notebook environment.
- Zhao, W. et al. [An agentic system for rare disease diagnosis with traceable reasoning](https://www.nature.com/articles/s41586-025-10097-9). Nature (2026). Multi-agent contrast; use for traceable evidence and tool integration, not for `central host agent` naming in PRS Agent.
- Rollwage, M. et al. [A cognitive layer architecture to support large-language model performance in psychotherapy interactions](https://www.nature.com/articles/s41591-026-04278-w). Nature Medicine (2026). Layer/scaffold anchor for domain reasoning components around LLMs.
- Bragg, J. et al. [AstaBench: Rigorous Benchmarking of AI Agents with a Scientific Research Suite](https://openreview.net/forum?id=M7TNf5J26u). ICLR 2026 Oral. Anchor for standardized tools, interfaces, agent classes, trajectories and scientific-agent evaluation.
- Kapoor, S. et al. [Holistic Agent Leaderboard: The Missing Infrastructure for AI Agent Evaluation](https://hal.cs.princeton.edu/). ICLR 2026. Anchor for agent evaluation harnesses, trace logging, cost-aware comparison and scaffold sensitivity.
- Lu, X. et al. [Tools are under-documented: Simple Document Expansion Boosts Tool Retrieval](https://openreview.net/forum?id=g9D9MgG7iW). ICLR 2026 Poster. Anchor for treating tool descriptions and retrieval as a first-class layer.
- Xia, S., Sun, Y. & Liu, P. [SR-Scientist: Scientific Equation Discovery With Agentic AI](https://openreview.net/forum?id=KBN6oUx5uL). ICLR 2026 Poster. Anchor for long-horizon, tool-driven scientific agents.
- Yu, S., Li, G., Shi, W. & Qi, P. [PolySkill: Learning Generalizable Skills Through Polymorphic Abstraction For Continual Learning](https://openreview.net/forum?id=KdEsujyiSV). ICLR 2026 Poster. Anchor for skill abstraction and reusable agent skills.
- SkillsBench Team. [SkillsBench: Benchmarking How Well Skills Work Across Diverse Tasks](https://www.skillsbench.ai/). 2026 benchmark/resource. Useful for the skills / agent harness / model abstraction split; not a Nature/ICLR anchor unless later venue-final.
- Jiang, Y. et al. [SoK: Agentic Skills -- Beyond Tool Use in LLM Agents](https://arxiv.org/abs/2602.20867). arXiv:2602.20867 (2026). Lower-weight skill terminology reference; use only when a broader skill definition is needed.
- Anthropic. [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents). Defines the workflow/agent boundary and recommends adding agentic complexity only when it measurably improves outcomes.
- Anthropic. [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps). Introduces the planner/generator/evaluator harness pattern, evidence handoffs, and separated review design.
- Anthropic. [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills). Defines Agent Skills as organized instruction/resource bundles with progressive disclosure.
- OpenAI. [Agents SDK overview](https://developers.openai.com/api/docs/guides/agents). Describes agentic applications with tools, orchestration, state, approvals, and observability.
- OpenAI. [Agents SDK: Agents](https://openai.github.io/openai-agents-python/agents/). Defines an agent as an LLM configured with instructions, tools, and optional runtime behavior such as handoffs, guardrails, and structured outputs.
- OpenAI. [Agents SDK: Tools](https://openai.github.io/openai-agents-python/tools/). Documents function tools, hosted tools, tool search, and agents-as-tools as the execution surface for agentic applications.
- OpenAI. [Agents SDK: Guardrails](https://openai.github.io/openai-agents-python/guardrails/). Documents input, output, and tool guardrails for workflow boundaries.
- OpenAI. [Agents SDK: Tracing](https://openai.github.io/openai-agents-python/tracing/). Documents tracing of LLM generations, tool calls, handoffs, guardrails, and custom events.
- OpenAI. [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills). Frames agent skills as testable artifacts and recommends outcome/process/style/efficiency evals.
