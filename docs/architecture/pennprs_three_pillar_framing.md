# PennPRS Agent — Three-Pillar Framing (2026 Harness Engineering Era)

Status: working positioning document, last updated 2026-05-03.
Scope: cross-cutting framing for PennPRS Agent paper(s) and product narrative. Applies to all contributions (c1 / c2 / c3).

Paper-facing source of truth: [`pennprs_agent_paper_framing.md`](pennprs_agent_paper_framing.md).

## Why this document exists

By 2026 the LLM-application community has converged on a vocabulary distinguishing *agent* from *workflow* from *harness* (Anthropic, OpenAI, LangChain). PennPRS Agent's existing modules were built before this vocabulary stabilized, so we need a single positioning doc that:

1. Names the three pillars we will claim.
2. Defines each pillar against the 2026 consensus so reviewers cannot reject the claim on definitional grounds.
3. Maps each existing PennPRS module (c2 = same-trait PGS recommendation, c3 = cross-trait transfer, etc.) to the pillar it instantiates.
4. Records what is upgrade work (architecture must change) versus framing work (architecture is fine, presentation must change).

## The three pillars

```
PennPRS Agent
├── Pillar 1: Single Agent              (top-level user-facing shell)
├── Pillar 2: Agent Harness Engineering (per-task orchestration layer)
│   ├── c2 harness   ← generator-evaluator harness candidate (see c2 positioning doc)
│   └── c3 harness   ← keep as-is, upgrade presentation only
└── Pillar 3: Agent Skill                (sealed empirical knowledge layer)
    └── prs_model_evaluator skill        (consumed by c2 + c3)
```

### Pillar 1 — Single Agent

**2026 definition** (Anthropic, *Building Effective Agents*; OpenAI Agents SDK):
> "Agents are systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks."
> "LLMs autonomously using tools in a loop."

**PennPRS instantiation:** the top-level conversational shell. The user states a goal ("recommend a PGS for atrial fibrillation"), the shell agent decides which capabilities to invoke (c2 same-trait selection, c3 cross-trait transfer, evaluation, etc.), maintains conversation state, and terminates when the user is satisfied. This is the Anthropic-textbook "agent" because the LLM controls the dispatch and termination.

### Pillar 2 — Agent Harness Engineering

**2026 definition** (Anthropic, [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps); OpenAI; Martin Fowler):
> "Agent = Model + Harness." Models have converged; differentiation is in the harness layer.
> Anthropic's three-agent harness pattern: **Planner / Generator / Evaluator**, with structured context handoffs (artifacts) and sprint contracts (per-stage schemas).
> *"Separating the agent doing the work from the agent judging it proves to be a strong lever to address evaluation issues."*

**Spectrum within harness engineering:**
- **Workflow harness** — predefined code paths; LLM is called at each step but does not direct control flow. Best for well-defined tasks. (Anthropic patterns: prompt chaining, parallelization / voting, routing, evaluator-optimizer.)
- **Agent harness** — contains LLM-driven loops with autonomous tool use. Best when flexibility is needed at scale.
- **Hybrid harness** — workflow scaffolding with one or more embedded agentic stages.

**PennPRS instantiation:** each contribution module is a harness. The harness pillar is where PennPRS's engineering novelty lives — the per-task orchestration patterns that wrap base LLM calls into reliable, evaluable pipelines.

| Module | Current harness type | Status |
|---|---|---|
| **c2** (same-trait PGS recommendation) | generator-evaluator harness candidate — sealed `SKILL.md` + heritability context are shared evidence; Stage 1 generates a top-5 shortlist; Stage 2 is a separated holistic hidden-benchmark evaluator. Current N=2 mean: H1=0.3820, H5=0.7921, with H2-H5 stronger than the top-3 pairwise alternative. | **Candidate active** — pure ReAct was empirically falsified on this fixed-candidate task because the model under-fetched Skill sections; current direction is bounded evaluator orchestration over the Skill/H2 substrate. See [c2 harness positioning doc](../../experiments/contribution2/recommendation/docs/harness_engineering_positioning.md). |
| **c3** (cross-trait transfer) | hybrid harness — Scout / Judge / Pick / Critic workflow stages + GATHER ReAct agent stage. The current paper-facing default is the iter11-family `no_all_tools_plus_pgs_skill` configuration: no h2 / OT / GC / biology evidence tools, archived cross-trait KB off, `prs_model_evaluator` Skill on at PICK / GLOBAL_PRIMARY_RECONCILIATION / CRITIC. Retained paired80 result: top_0.5%=23, top_25%=65. | **Architecture stable, default updated** — explicit role tagging in code/docs, ablation evidence that the PRS Skill is load-bearing and extra evidence tools regress this benchmark, three-pillar diagram for paper. See [c3 harness positioning doc](../../experiments/contribution3/transfer/docs/harness_engineering_positioning.md). |

### Pillar 3 — Agent Skill

**2026 definition** (Anthropic, Claude Code Skills; Agent Skill specification):
> A sealed, version-controlled bundle of empirical / procedural knowledge that an agent can load on demand. Distinct from prompts (which encode procedure) and from tools (which encode capability) — skills encode **knowledge**.

**PennPRS instantiation:** `src/server/core/skills/prs_model_evaluator/` — a sealed skill bundle that encodes empirical patterns about how to evaluate PGS Catalog records (PRS-only metric cleanliness, covariate-leakage detection, endpoint fidelity, ancestry breadth, etc.). Currently consumed by:

- **c2 production runner**: pre-fed into the system prompt of every PGS-selection LLM call.
- **c3 PICK / GLOBAL_PRIMARY_RECONCILIATION / CRITIC stages**: loaded per stage via `load_c3_view(stage, ...)`.

This is the only concrete "agent skill" in the system. c2's pure ReAct attempt showed that making the skill tool-callable is not automatically better for this benchmark: gpt-5.2 under-fetched the relevant sections. The current c2 harness therefore treats the skill as a sealed evidence substrate loaded into bounded evaluator agents, while c3 continues to use staged skill views.

## Module-to-pillar matrix (forward state)

| Pillar | c2 (post-upgrade) | c3 (current) | Top-level shell |
|---|---|---|---|
| Single Agent | — (sub-component) | — (sub-component) | ✅ |
| Harness Engineering | ✅ Generator-evaluator harness (Skill/H2 evidence + bounded holistic evaluator) | ✅ Hybrid harness (Anthropic three-agent pattern; 4 evidence tools + 1 skill) | — |
| Agent Skill | ✅ consumes prs_model_evaluator | ✅ consumes prs_model_evaluator | — |

## What changes, what doesn't

**Architecture upgrades:**
- c2: workflow → generator-evaluator harness. Same evidence inputs (SKILL.md + heritability), but a separated top-5 holistic hidden-benchmark evaluator replaces the single fixed workflow call. Pure ReAct and heavier evaluator consensus were tested and rejected for the production shape.

**Architecture stable:**
- c3: keep the iter11-family paper-facing default (`no_all_tools_plus_pgs_skill`). Multiple sessions of ablations have shown that adding h2 / OT / GC / biology evidence tools on top of the PRS Skill harness does not improve the paired80 benchmark.

**Presentation upgrades (both modules):**
- Code / docstring annotations mapping each stage to its Anthropic harness role.
- Ablation tables showing harness components are load-bearing.
- Paper-ready three-pillar diagram (this document is the single source of truth).

## What we deliberately do NOT claim

- We do **not** claim c2 is a pure ReAct agent. The current claim is narrower and more defensible: c2 is a Skill-grounded generator-evaluator harness over the sealed PRS Skill and heritability evidence.
- We do **not** claim every c3 stage is an agent — only GATHER is. The other 4 stages are workflow.
- We do **not** claim c3 is multi-agent in the Anthropic sense — it is a single-orchestrator harness with one agentic worker stage.
- We do **not** claim PennPRS supplants the human PRS analyst — it is harness-engineered assistance, not autonomous medical decision-making.

## Anchor sources (2026)

- Anthropic — [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- Anthropic — [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- Anthropic — [How we built our multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system)
- Anthropic — [Claude Code subagents docs](https://code.claude.com/docs/en/sub-agents)
- OpenAI — [Agents SDK (Python) docs](https://openai.github.io/openai-agents-python/)
- LangChain — [How to think about agent frameworks](https://www.langchain.com/blog/how-to-think-about-agent-frameworks)
- LangChain — [Improving deep agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)
- Martin Fowler — [Harness engineering](https://martinfowler.com/articles/harness-engineering.html)
- Princeton — [HAL harness leaderboard](https://github.com/princeton-pli/hal-harness) (ICLR 2026)
- Survey — [Agent Harness for LLM Agents: A Survey](https://www.preprints.org/manuscript/202604.0428)

(Per-module sources are cited in the per-module positioning docs.)
