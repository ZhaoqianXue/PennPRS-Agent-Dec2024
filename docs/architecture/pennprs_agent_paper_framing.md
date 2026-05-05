# PennPRS Agent Paper Framing: Single Agent + Harness Engineering + Agent Skill

Status: paper-facing engineering positioning, last updated 2026-05-03.
Scope: this document is the preferred engineering framing for PennPRS Agent as an integrated system. It should be used when writing the Nature Genetics manuscript, response letters, architecture diagrams, and engineering-methods text.

## Core Thesis

PennPRS Agent should be framed as one integrated single-agent scientific decision system, not as a collection of separate agents.

The clean three-layer formulation is:

```text
PennPRS Agent
├── Layer 1: Single LLM Agent
│   └── user-facing scientific assistant: understands the user's PGS-selection goal,
│       selects the appropriate specialist capability, explains the result, and
│       terminates the user interaction
│
├── Layer 2: Agent Harness Engineering
│   ├── c2: same-trait PGS selection harness
│   │   └── Skill/H2-grounded generator -> separated evaluator
│   └── c3: cross-trait transfer harness
│       └── planner -> ReAct evidence gathering -> ranker -> critic
│
└── Layer 3: Agent Skill
    └── prs_model_evaluator Skill
        └── PGS evaluation rules, empirical caveats, metric interpretation,
            ancestry/endpoint/overfitting checks, and domain decision heuristics
```

In one sentence:

> PennPRS Agent is a single-agent scientific assistant built on agent harness engineering: a user-facing LLM agent routes PGS-selection goals into specialized, skill-grounded harnesses, including a same-trait generator-evaluator harness and a cross-trait hybrid ReAct evidence-gathering harness, both grounded in a sealed PRS evaluation Skill and heritability evidence.

## Layer 1: Single LLM Agent

The single-agent claim belongs at the top-level PennPRS Agent interface, not inside every contribution module.

The top-level agent is responsible for:

- understanding the user's scientific goal;
- deciding whether the task is same-trait PGS selection, cross-trait transfer, comparison, or explanation;
- invoking the corresponding harnessed specialist capability;
- maintaining user-facing state across the conversation;
- explaining recommendations and stopping once the user's goal has been handled.

This is the right level for the "single agent" claim because c2 and c3 are not separate user-facing agents. They are specialist capabilities invoked by the same top-level scientific assistant.

Recommended wording:

> PennPRS Agent exposes a single user-facing LLM agent. Internally, the agent routes PGS-selection goals to harness-engineered specialist capabilities rather than relying on one monolithic prompt.

Avoid:

- "c2 and c3 are two agents."
- "PennPRS Agent is a multi-agent system."
- "Every stage is autonomous."

## Layer 2: Agent Harness Engineering

The harness layer is where most of the engineering novelty lives. The correct framing is not "one prompt with tools"; it is "task-specific orchestration around a base LLM, with structured evidence, explicit stage contracts, tool boundaries, and evaluation loops."

### c2: Same-Trait Generator-Evaluator Harness

c2 should be framed as a harness-engineered same-trait PGS-selection capability inside PennPRS Agent.

Current production candidate:

- production wrapper: `experiments/contribution2/recommendation/scripts/run_experiment_top5_holistic_lift.py`;
- architecture: R38-style top-5 holistic hidden-benchmark reranking;
- evidence substrate: sealed `prs_model_evaluator` Skill plus heritability records;
- Stage 1: generator proposes a primary pick plus bounded top-5 shortlist from Skill/H2-enriched context;
- Stage 2: separated holistic evaluator selects the final PGS from the shortlist.

Recommended wording:

> c2 implements a Skill-grounded generator-evaluator harness for same-trait PGS selection. A generator proposes a bounded top-5 shortlist from PRS Skill and heritability evidence, and a separated evaluator selects the final model under a hidden-benchmark selection frame.

This is harness engineering because it separates generation from evaluation and uses a bounded evaluator layer over a sealed evidence substrate. It should not be described as a pure ReAct agent. Pure ReAct was tested and rejected for c2 because the model under-fetched Skill sections on this fixed-candidate benchmark.

Avoid:

- "c2 is a true ReAct agent."
- "c2 autonomously decides when to read all Skill/H2 evidence" if the kept production path preloads the evidence substrate.
- "c2 is only a prompt" because the kept architecture is a generator-evaluator harness with N=2 fresh verification over the iterD floor.

### c3: Cross-Trait Hybrid Agent Harness

c3 is the stronger agent-harness case study.

Current framing:

- workflow scaffold: Scout -> Judge -> Pick -> Critic;
- embedded ReAct stage: GATHER;
- GATHER lets the LLM choose tool calls and termination through `RoundDirective.tool_calls` and `RoundDirective.done`;
- tool surface: h2, genetic correlation batch estimation, Open Targets overlap, biology bundle retrieval, and PGS model hydration;
- persistent structured memory: `EvidenceRegistry`;
- independent evaluator: Critic.

Recommended wording:

> c3 implements a hybrid agent harness for cross-trait transfer. A planner proposes candidate probes, a ReAct evidence-gathering agent autonomously calls domain tools into a structured EvidenceRegistry, ranking stages select transferable models, and an independent critic audits the final recommendation.

This is the cleanest module-level match to the 2026 harness-engineering vocabulary: planner/generator/evaluator separation, LLM-directed tool use, structured context handoffs, evidence registry, and independent critique.

Avoid:

- "c3 is a multi-agent system" unless we later introduce multiple collaborating autonomous agents.
- "all c3 stages are agents"; only GATHER is the true ReAct-style agentic stage.
- "c3 should convert every stage to an agent"; well-defined decision points are better left as workflow stages.

## Layer 3: Agent Skill

The `prs_model_evaluator` Skill is the shared domain skill layer. It should not be reduced to "a prompt."

Recommended wording:

> The `prs_model_evaluator` Skill is a sealed, version-controlled domain knowledge layer shared across PennPRS Agent capabilities. It encodes empirical PGS-selection heuristics, endpoint-fidelity checks, metric interpretation rules, ancestry considerations, and leakage/overfitting cautions.

c2 and c3 consume the same skill differently because the task shapes differ:

- c2 uses the Skill as a full evidence substrate because the same-trait fixed-candidate task benefits from complete priming and bounded evaluation.
- c3 uses staged Skill views and structured evidence because cross-trait transfer requires progressive disclosure and iterative evidence gathering.

This preserves the Agent Skill story without forcing every module into the same ReAct shape.

## Recommended Manuscript Paragraph

> PennPRS Agent is a single-agent scientific assistant built around harness-engineered PGS-selection capabilities. Rather than relying on a single monolithic prompt, the user-facing LLM agent routes tasks to specialist harnesses: c2 implements a Skill-grounded generator-evaluator harness for same-trait PGS selection, while c3 implements a hybrid agent harness for cross-trait transfer with an embedded ReAct evidence-gathering loop, structured EvidenceRegistry, and independent critic. Both capabilities are grounded in the same sealed `prs_model_evaluator` Agent Skill and heritability evidence, allowing domain knowledge to be versioned, reused, evaluated, and ablated across tasks.

## Claims We Can Defend

- PennPRS Agent is a single user-facing LLM agent with harness-engineered specialist capabilities.
- c2 is a Skill-grounded generator-evaluator harness, not merely a single-shot prompt.
- c3 is a hybrid agent harness with one true ReAct evidence-gathering stage.
- The PRS Skill is a shared, sealed, version-controlled domain skill layer.
- Harness architecture is load-bearing because c2 R38 improves over iterD-final across Hit@1-Hit@5 in N=2 fresh verification, and c3's iter11 paper-facing harness improves over the no-all-tools baseline while retaining structured evidence gathering and critique.

## Claims To Avoid

- Do not claim c2 is a pure ReAct/autonomous tool-use agent.
- Do not claim c2 and c3 are separate agents.
- Do not claim PennPRS Agent is a multi-agent system.
- Do not claim every c3 stage is agentic.
- Do not claim the Skill is just prompt text.
- Do not claim the system is an autonomous medical decision-maker; it is harness-engineered scientific assistance for PGS analysis.

## Source Alignment

The framing above is aligned with current Anthropic and OpenAI engineering guidance:

- Anthropic distinguishes workflows from agents: workflows follow predefined code paths, while agents dynamically direct their own processes and tool usage. This supports describing c2 as a workflow/generator-evaluator harness and c3's GATHER as the true agentic stage.
- Anthropic's 2026 harness-design writing emphasizes planner/generator/evaluator separation, structured artifacts, and independent evaluator roles. This supports c3's Scout/Gather/Pick/Critic structure and c2's separated evaluator.
- Anthropic's Agent Skills guidance defines skills as organized folders of instructions, scripts, and resources, with progressive disclosure and domain-specific specialization. This supports treating `prs_model_evaluator` as a shared skill layer rather than a prompt.
- OpenAI's Agents SDK describes agents as LLMs configured with instructions, tools, handoffs, guardrails, and structured outputs, while the SDK owns turns, tools, guardrails, handoffs, and sessions. This supports positioning PennPRS Agent as a top-level agent whose specialist capabilities are implemented through harnessed orchestration.
- OpenAI's skill-evaluation guidance emphasizes evaluating both outcomes and process traces, including whether a skill was invoked and whether the expected steps occurred. This supports keeping c2/c3 benchmark tables, trace evidence, and ablation results as part of the engineering claim.

## References

- Anthropic. [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents). Defines the workflow/agent boundary and recommends adding agentic complexity only when it measurably improves outcomes.
- Anthropic. [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps). Introduces the planner/generator/evaluator harness pattern, structured handoffs, and separated evaluator design.
- Anthropic. [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills). Defines Agent Skills as organized instruction/resource bundles with progressive disclosure.
- OpenAI. [Agents SDK overview](https://developers.openai.com/api/docs/guides/agents). Describes agentic applications with tools, orchestration, state, approvals, and observability.
- OpenAI. [Agents SDK: Agents](https://openai.github.io/openai-agents-python/agents/). Defines an agent as an LLM configured with instructions, tools, and optional runtime behavior such as handoffs, guardrails, and structured outputs.
- OpenAI. [Agents SDK: Tools](https://openai.github.io/openai-agents-python/tools/). Documents function tools, hosted tools, tool search, and agents-as-tools as the execution surface for agentic applications.
- OpenAI. [Agents SDK: Guardrails](https://openai.github.io/openai-agents-python/guardrails/). Documents input, output, and tool guardrails for workflow boundaries.
- OpenAI. [Agents SDK: Tracing](https://openai.github.io/openai-agents-python/tracing/). Documents tracing of LLM generations, tool calls, handoffs, guardrails, and custom events.
- OpenAI. [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills). Frames agent skills as testable artifacts and recommends outcome/process/style/efficiency evals.
