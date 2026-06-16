# Contribution3 Harness Engineering Positioning

Status: working positioning document, last updated 2026-05-19.
Parent: [`docs/architecture/pennprs_agent_paper_framing.md`](../../../../docs/architecture/pennprs_agent_paper_framing.md)
Related: [`../CROSS_TRAIT_TRANSFER_SPEC.md`](../CROSS_TRAIT_TRANSFER_SPEC.md), [`../REFACTOR_PLAN.md`](../REFACTOR_PLAN.md)

## Where c3 sits in the PRS Agent architecture

c3 is the **cross-phenotype / cross-trait transfer harness** inside the paper-facing PRS Agent architecture:

```text
LLM orchestration layer
└── Task-specific agent harness layer
    └── c3 cross-phenotype transfer harness
        └── calls PRS Model Skill and tool layer:
            PGS hydration, h2, genetic correlation, Open Targets,
            PRS Model Skill (`prs_model_evaluator`) when PGS records are compared
```

The LLM orchestration layer invokes c3 only when no target-phenotype PGS model exists for the target phenotype. c3 is a task-specific hybrid harness: workflow scaffolding (Scout -> Judge -> Pick -> Critic) with one true ReAct agent stage (GATHER) embedded.

By the 2026 agent-system vocabulary:
- the top-level paper architecture is an integrated PRS decision system with LLM orchestration;
- the c3 harness sits in the task-specific agent harness layer and controls evidence gathering, ranking and critic review;
- c3's GATHER stage qualifies as the agentic tool-use loop because the LLM chooses tool calls and termination;
- the other c3 stages are structured LLM calls / workflow stages, not autonomous agents;
- a multi-agent system requires multiple agents collaborating with handoffs, which c3 does **not** introduce.

c3 maps onto planner / generator / evaluator harness patterns in contemporary agent-harness writing:

| Anthropic harness role | c3 stage | Type |
|---|---|---|
| **Planner** (brief → spec) | SCOUT (target_label → probe_bundle_ids) | single LLM call (workflow) |
| **Generator** (execute spec, maintain coherence) | GATHER + JUDGE + PICK + GLOBAL_PRIMARY_RECONCILIATION | GATHER is ReAct agent loop; rest are single LLM calls |
| **Evaluator** (independent grader) | CRITIC | single LLM call (workflow) |
| Evidence handoffs (artifacts) | EvidenceRegistry, GC batch / OT registry | — |
| Sprint contracts | per-stage Pydantic schemas in `schemas.py` | — |

Anthropic's load-bearing principle quote — *"Separating the agent doing the work from the agent judging it proves to be a strong lever to address evaluation issues"* — directly matches c3's PICK / RECONCILE vs CRITIC split.

## GATHER is the single agentic stage

Code reference: [`agent.py`](../agent.py) Stage 2 GATHER (function `_run_gather`).

The agentic loop:
- LLM emits a `RoundDirective` per round containing `tool_calls` (LLM-chosen) and a `done` flag (LLM-chosen termination).
- Python harness dispatches the tool calls, records results into the registry, and re-enters the loop.
- Halts on (in priority order): `done=True` from LLM → `llm_terminated`; budget exhausted → `budget_exhausted_before_done`; max_rounds without done → `budget_exhausted_before_done`.

This is the paper-facing reason c3 can be described as a hybrid agent harness: the harness as a whole is staged and controlled, but the GATHER stage is an LLM-directed tool-use loop.

Optional tool surface implemented by the GATHER/harness stack (not all enabled in the paper-facing default):
- `get_heritability` (h2) — disabled in the current default.
- `genetic_correlation_batch_estimator` (GC) — disabled in the current default.
- `get_open_targets_overlap` (OT) — disabled in the current default.
- `describe_pgs_model` / PGS Catalog hydration — retained downstream for model selection.

The current paper-facing default keeps the ReAct/harness structure, ablates h2 / GC / OT evidence channels, leaves the archived cross-trait KB off, and uses tuned Harness Only V1. It does not read C3 PRS Model Skill overrides. Manuscript-facing writing should not foreground the deprecated biology-retrieval surface.

The other 4 stages (SCOUT / JUDGE / PICK / CRITIC) are single-shot structured-output LLM calls — workflow, not agent.

## Production state: retained tuned Harness Only result

- Current paper-facing default: `no_all_tools_tuned_breadth`.
- Retained run: `all-tools__paired80_legacy_no_aou_tuned_HO_breadth_20260509_w20`.
- Formal comparator: `no_all_tools` / `all-tools__paired80_legacy_no_aou_harness_only_20260508_w20`.
- Retained paired80 legacy no-AoU performance: mean GPR=0.8417, official top_0.5%=0.2750, top_1%=0.4334, top_2.5%=0.4667, legacy top_5%=0.4875, legacy top_25%=0.7750.

The current C3 result is a tuned Harness Only configuration, not a PRS Model Skill result. It keeps h2 / GC / OT evidence channels off and does not read C3 skill overrides. The retained change is the breadth_floor no-OT fallback, which restores an existing candidate-exposure safety net when Open Targets evidence is ablated.


## Decision: architecture frozen, presentation upgraded

Architectural lever is currently low-return; further changes should be benchmark-gated. What remains is **presentation-level work** to make the harness engineering claim defensible to reviewers.

**Architecture: NO change.** In particular:
- Do not add more agentic stages. The other 4 are well-defined decision points; converting them to agents violates Anthropic's "workflows are better for well-defined tasks" guidance and risks regressing the locked-in performance.
- Do not change the paper-facing default tool surface without a paired80 lift: h2 / GC / OT remain off, archived cross-trait KB remains off, and C3 PRS Model Skill overrides remain off.
- Do not change halt conditions, budgets, or schemas.

**Presentation: upgrades planned.**

1. **Explicit Anthropic role tags** in `agent.py` docstrings and key call sites (`_run_scout` → "Planner", `_run_gather` → "Generator (agentic)", `_run_judge` / `_run_pick` / `_run_global_primary` → "Generator (workflow)", `_run_critic` → "Evaluator").
2. **Ablation table** showing each harness component is load-bearing:
   - GATHER ReAct loop vs single-shot Gather (defends the agentic stage)
   - With vs without CRITIC (defends generator/evaluator separation)
   - With vs without each evidence tool (h2, GC, OT) — already partly captured, consolidate.
3. **Harness threshold non-load-bearingness**: ablation over `max_tool_calls` / `max_gather_rounds` / probe shortlist sizes — show these aren't load-bearing, supporting the "LLM-led, harness-orchestrated" claim.
4. **LLM orchestration + task-specific agent harness layer + PRS Model Skill and tool layer diagram** for the paper: c2 minimal generator-selection harness and c3 hybrid transfer harness should sit in the middle harness layer; both consume PRS tools and the PRS Model Skill from the lower Skill/tool layer; both are selected by the upper LLM orchestration layer.

## Why c3 is the more interesting harness case study

For paper framing, c3 carries the heavier load in the **task-specific agent harness layer**:

- It instantiates the **complete Anthropic three-agent pattern** (Planner / Generator / Evaluator), not a degenerate two-role version.
- It contains a **real ReAct agent** stage with 5-tool surface and LLM-controlled termination.
- It demonstrates **evidence handoffs** (EvidenceRegistry, GC batch, OT registry) between stages.
- It enforces **separation of generation and evaluation** (Pick/Reconcile vs Critic), which Anthropic flags as "a strong lever."
- It supports **progressive disclosure / context compaction** (PGS triage → hydrate; bundle dossier compaction).

c2 provides the contrasting **minimal generator-selection harness** end of the spectrum: a Skill/H2-grounded same-trait shortlist generator plus a final-selection step. The two together demonstrate harness engineering across a range, rather than two near-identical harnesses.

## Sources

See the parent framing document for the full 2026 architecture reference list. The c3-specific takeaways are:

- AstaBench (ICLR 2026) and HAL (ICLR 2026) support treating c3 as an evaluable harness with controlled tools, traces, costs and scaffold sensitivity.
- SR-Scientist (ICLR 2026) supports long-horizon scientific agents that use executable tools and feedback rather than a static proposal-only LLM role.
- Tools are under-documented (ICLR 2026) supports explicit documentation of the c3 tool surface and boundaries.
- PolySkill (ICLR 2026), SkillsBench (2026 resource) and the Agentic Skills SoK (2026 preprint) support treating PGS model evaluation rules as reusable skills consumed by harnesses, while keeping source-phenotype relevance outside the PRS Model Skill boundary.
- Anthropic — [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) remains useful for planner / generator / evaluator wording.
- Anthropic — [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) remains useful for workflow vs agent boundary language.
