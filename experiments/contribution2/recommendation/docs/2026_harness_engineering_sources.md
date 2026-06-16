# 2026 Harness Engineering — External Sources Used in Contribution 2

This document records the live-internet sources fetched during the Phase 1
research that grounded the contribution-2 same-trait Hit@1 lift work
(Round 1 pairwise reranking → Round 5 consistency-routed pairwise). All
URLs were fetched directly via WebFetch / WebSearch tools — they are
*external* references, not local-corpus material.

The architectural claims most directly load-bearing for c2's Round 5
production candidate are flagged in **bold**.

## 2026 paper anchors for PRS Agent Methods architecture

These are the higher-weight sources to cite or emulate when writing the
Nature Genetics Methods architecture. They should take priority over blog
terminology when manuscript wording and figure labels are chosen.

- **[CellVoyager: AI CompBio agent generates new insights by autonomously analyzing biological data](https://www.nature.com/articles/s41592-026-03029-6)** — Nature Methods 2026. Supports a single-agent scientific pattern in which an LLM-driven system generates and executes computational biology analyses in an executable environment. Use as an anchor for `LLM orchestration layer` and task execution in scientific software.
- **[An agentic system for rare disease diagnosis with traceable reasoning](https://www.nature.com/articles/s41586-025-10097-9)** — Nature 2026. Supports traceable evidence, specialized tools, and ranked biomedical outputs. Use as a contrast case: DeepRare is explicitly multi-agent, so do not borrow its `central host agent` naming for PRS Agent.
- **[A cognitive layer architecture to support large-language model performance in psychotherapy interactions](https://www.nature.com/articles/s41591-026-04278-w)** — Nature Medicine 2026. Supports layer/scaffold language for domain reasoning components that augment a general-purpose LLM.
- **[AstaBench: Rigorous Benchmarking of AI Agents with a Scientific Research Suite](https://openreview.net/forum?id=M7TNf5J26u)** — ICLR 2026 Oral. Supports standardized tools, interfaces, agent classes, traces, and controlled scientific-agent evaluation.
- **[Holistic Agent Leaderboard: The Missing Infrastructure for AI Agent Evaluation](https://hal.cs.princeton.edu/)** — ICLR 2026. Supports treating the harness/scaffold as part of the evaluated system, with cost-aware comparison and trace logging.
- **[Tools are under-documented: Simple Document Expansion Boosts Tool Retrieval](https://openreview.net/forum?id=g9D9MgG7iW)** — ICLR 2026 Poster. Supports explicit tool documentation and tool-retrieval boundaries as first-class engineering choices.
- **[SR-Scientist: Scientific Equation Discovery With Agentic AI](https://openreview.net/forum?id=KBN6oUx5uL)** — ICLR 2026 Poster. Supports long-horizon, tool-driven scientific agents that write code, analyze data, evaluate hypotheses, and optimize from feedback.
- **[PolySkill: Learning Generalizable Skills Through Polymorphic Abstraction For Continual Learning](https://openreview.net/forum?id=KdEsujyiSV)** — ICLR 2026 Poster. Supports reusable skills and the separation between a skill's abstract goal and execution.
- [SkillsBench: Benchmarking How Well Skills Work Across Diverse Tasks](https://www.skillsbench.ai/) — 2026 benchmark/resource. Useful for the skills / agent harness / model abstraction split; treat as a current resource rather than a Nature/ICLR anchor unless venue-final status changes.
- [SoK: Agentic Skills -- Beyond Tool Use in LLM Agents](https://arxiv.org/abs/2602.20867) — 2026 preprint. Useful for skill terminology: reusable procedural capability, applicability conditions, execution policies, termination criteria, and reusable interfaces. Use as lower-weight support because it is not venue-final.

Recommended architecture vocabulary derived from these sources:

```text
PRS Agent
├── LLM orchestration layer
├── task-specific harness layer
└── PRS tool-and-skill layer
```

Do not mix `layer, layer, harnesses` in final manuscript prose. Either call all
three `layers` in architecture documentation or write "three architectural
components" in the paper opening while preserving the same order.

## Anthropic engineering blog (2026)

- **[Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)** — three-agent (planner / generator / evaluator) architecture; "stock LLM is a poor evaluator of its own work"; separated-evaluator principle.
- **[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)** — minimal-high-signal-tokens principle; just-in-time retrieval; classification / selection vs open-ended task patterns.
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — structured handoff artifacts; signal carrying between stages.
- [Scaling Managed Agents — decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) — context object outside the model's context window; durable session.
- [Building effective agents](https://www.anthropic.com/research/building-effective-agents) — five core patterns (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer).
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — progressive disclosure as a context-engineering primitive.
- [Anthropic Engineering Blog index](https://www.anthropic.com/engineering)

## OpenAI / OpenAI Cookbook (2026)

- [Testing agent skills systematically with evals](https://developers.openai.com/blog/eval-skills) — eval-driven iteration discipline; "let real failures drive coverage".
- [Self-evolving agents — autonomous agent retraining](https://developers.openai.com/cookbook/examples/partners/self_evolving_agents/autonomous_agent_retraining) — generator/evaluator separation; metaprompt optimization loop.

## Independent 2026 commentary on harness engineering

- [Anthropic's three-agent harness — InfoQ](https://www.infoq.com/news/2026/04/anthropic-three-agent-harness-ai/) — secondary writeup of the planner/generator/evaluator architecture.
- [Agent harness engineering — Addy Osmani](https://addyosmani.com/blog/agent-harness-engineering/) — ratchet principle; "ten focused tools beat fifty bloated"; harness as living system.
- [LLM fan-out 101: self-consistency, consensus, and voting patterns — Kinde](https://www.kinde.com/learn/ai-for-software-engineering/workflows/llm-fan-out-101-self-consistency-consensus-and-voting-patterns/) — when parallel sampling helps vs hurts; consensus voting tactics.

## Academic sources directly cited by Round 1 / Round 5

- **[Bavaresco et al. 2026 — When LLM Judge Scores Look Good but Best-of-N Decisions Fail](https://arxiv.org/html/2603.12520)** — within-prompt vs global correlation; pairwise judging recovers 21.1%→61.2% in matched best-of-2; confidence-based routing as the practical fix. Single most load-bearing reference for c2 Round 1 + Round 5.
- [Wang & Lou 2025 — Ranked Voting based Self-Consistency of Large Language Models](https://arxiv.org/html/2505.10772v1) — Borda / IRV / MRR voting on ranked LLM outputs; 4.95% lift on lightweight, 2.68%–3.51% on 7B–9B class. Considered for c2 Round 2 (rolled back: regressed H1 –3.4pp at gpt-5.2).

## Provenance

These URLs were fetched live during the May 2026 c2 harness-upgrade task. The
fetched content informed the Round 1 (pairwise rerank) and Round 5
(consistency-routed pairwise) architectures recorded in
`experiments/contribution2/recommendation/scripts/run_experiment_pairwise_rerank.py`
and `experiments/contribution2/recommendation/scripts/build_round5_from_existing.py`.

Every architectural lever in those scripts can be traced back to a specific
quoted principle from one of the URLs above; conversely, no lever was added
without an external grounding source. This is the audit trail that the
"Ground recs in literature" memory rule requires.

## ReAct agent design (Phase 1, 2026-05-02)

Sources fetched during the c2 ReAct-pivot Phase 1, focused specifically on
ReAct-pattern engineering (tool design discipline, scratchpad / observation
management, termination heuristics, "just enough agent" minimal-surface
practice, when ReAct beats workflow and when it doesn't).

### Anthropic 2026 ReAct / agent guidance

- **[Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)** — agents vs workflows; agents recommended only for "open-ended problems where it's difficult or impossible to predict the required number of steps"; tools need "example usage, edge cases, input format requirements, and clear boundaries from other tools"; agents need "ground truth from the environment at each step" and "stopping conditions (such as a maximum number of iterations)"; poka-yoke parameter design.
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — re-read for ReAct framing: just-in-time loading via "lightweight identifiers" loaded via tools mirrors human cognition; "tool result clearing" is one of the safest forms of compaction; progressive disclosure as the load-bearing principle for a 2-tool agent over a sealed knowledge skill.

### LangChain / LangGraph 2026 ReAct guidance

- **[LangGraph TypeScript ReAct agent guide](https://langgraphjs.guide/agents/react-agent/)** — "detailed tool descriptions achieve up to 25% better tool selection accuracy"; default recursion limit 25 to "prevent runaway loops"; structured `ToolMessage` observation envelopes; LLM-decided termination via "if the LLM produced a final response without tool calls, the loop terminates"; tool errors should be **caught inside the tool and returned as descriptive messages** (not exceptions) so the LLM can choose an alternative — exception-based failure terminates the agent unhelpfully. ReAct *underperforms* on simple single-API tasks, sub-second latency, deterministic workflows, and 15+ tool surfaces.
- [LangChain — Improving deep agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) — build-verify loop; `PreCompletionChecklistMiddleware` enforces verification before termination; `LoopDetectionMiddleware` tracks per-action repetition counts to break "doom loops"; anti-patterns: incomplete verification, myopic execution, poor time-management.
- [LangGraph ReAct tool-calling — Markaicode](https://markaicode.com/langgraph-react-agent-tool-calling/) — concrete one-iteration anatomy (Reason → Act → Observe), `add_messages` reducer for append-only history, conditional-edge termination on absence of `tool_calls`, recommendation to track `step_count` and terminate after N iterations to bound hallucinated-tool loops.

### OpenAI 2026 ReAct guidance

- [OpenAI Agents SDK (Python) docs](https://openai.github.io/openai-agents-python/) — built-in agent loop "handles tool invocation, sends results back to the LLM, and continues until the task is complete"; function tools auto-schemas via Pydantic; guardrails run in parallel and "fail fast"; handoffs / agents-as-tools for delegation.

### Independent 2026 commentary on ReAct

- **[Lance Martin — Agent design (Jan 2026)](https://rlancemartin.github.io/2026/01/09/agent_design/)** — "successful agents use surprisingly few tools (Claude Code: ~12; Manus: <20)"; offload context to filesystem rather than maintain in-context; the "just enough agent" principle: minimize context consumption through progressive disclosure, action-space hierarchy, and strategic offloading; Recursive Language Models (RLM) as a 2026+ trend where models absorb context-management duties themselves.
- **[Composio — How to build tools for AI agents: a field guide](https://composio.dev/blog/how-to-build-tools-for-ai-agents-a-field-guide)** — tool description template "Tool to <what it does>. Use when <specific situation>"; descriptions ≤1024 chars; document hidden rules ("at least one of X,Y,Z is required") explicitly; use enums over free-form strings; minimize top-level parameters; embed concrete examples in descriptions; reports "almost 10x drop in tool failures" after applying this discipline.
- [IBM — What is a ReAct agent?](https://www.ibm.com/think/topics/react-agent) — ReAct's separation of reasoning tokens from tool invocation reduces hallucinated tool actions; max-iterations cap to avoid endless loops; alternative termination: LLM-emitted confidence threshold.
- [Capabl — ReAct vs ReWOO vs CodeAct vs Reflexion](https://capabl.in/blog/agentic-ai-design-patterns-react-rewoo-codeact-and-beyond) — ReAct excels at dynamic environments with mid-execution self-correction; underperforms structured / repeatable workflows due to sequential token cost; ReWOO trades real-time improvisation for upfront efficiency.
- [Simon Willison — Agentic engineering anti-patterns](https://simonwillison.net/guides/agentic-engineering-patterns/anti-patterns/) — primary anti-pattern: shipping unreviewed agent output; agent productions need functional verification, scope discipline, and proof-of-effort artifacts. Useful as a "do not declare success on noise" reminder mirroring c2's Round-5 reproducibility failure.

### Load-bearing claims for c2 ReAct rounds

- Tool descriptions are 25%-of-accuracy levers (LangGraph) → invest in section-addressed `read_skill_section` description.
- Tool errors must return descriptive messages, not raise (LangGraph) → so the LLM can self-correct if it asks for a missing skill section.
- LLM-decided termination is the default ReAct termination — but a hard max-iterations cap is the safety floor (LangGraph + Anthropic + Markaicode).
- Just-in-time evidence loading via tool calls *is the upgrade* over iterD-final's pre-fed 55K corpus (Anthropic context engineering + Lance Martin "just enough agent").
- Workflow remains better for "deterministic, structured" tasks (Capabl + Anthropic). The c2 ReAct pivot is justified specifically by the noise-floor diagnosis in `diagnose.md`, not by an a-priori belief that ReAct dominates here.
