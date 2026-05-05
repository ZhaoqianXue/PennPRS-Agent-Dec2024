# Contribution3 Harness Engineering Positioning

Status: working positioning document, last updated 2026-05-03.
Parent: [`docs/architecture/pennprs_three_pillar_framing.md`](../../../../docs/architecture/pennprs_three_pillar_framing.md)
Related: [`../CROSS_TRAIT_TRANSFER_SPEC.md`](../CROSS_TRAIT_TRANSFER_SPEC.md), [`../REFACTOR_PLAN.md`](../REFACTOR_PLAN.md)

## Where c3 sits in the three-pillar framing

c3 is a **harness engineering** instantiation under Pillar 2 — cross-trait PGS transfer. Specifically, c3 is a **hybrid harness**: workflow scaffolding (Scout → Judge → Pick → Critic) with **one true ReAct agent stage** (GATHER) embedded.

By the 2026 Anthropic / OpenAI / LangChain consensus:
- A "single agent" requires LLM-driven loop + autonomous tool use → c3's GATHER stage qualifies; the other 4 stages do not.
- An "agent harness" is the orchestration layer wrapping such an agent → c3 as a whole qualifies.
- A "multi-agent system" requires multiple agents collaborating with handoffs → c3 does **not** qualify (only one agentic stage; the rest is workflow with structured handoffs).

c3 maps onto Anthropic's three-agent harness pattern (from their *Harness design for long-running application development* post):

| Anthropic harness role | c3 stage | Type |
|---|---|---|
| **Planner** (brief → spec) | SCOUT (target_label → probe_bundle_ids) | single LLM call (workflow) |
| **Generator** (execute spec, maintain coherence) | GATHER + JUDGE + PICK + GLOBAL_PRIMARY_RECONCILIATION | GATHER is ReAct agent loop; rest are single LLM calls |
| **Evaluator** (independent grader) | CRITIC | single LLM call (workflow) |
| Structured context handoffs (artifacts) | EvidenceRegistry, GC batch / OT registry | — |
| Sprint contracts | per-stage Pydantic schemas in `schemas.py` | — |

Anthropic's load-bearing principle quote — *"Separating the agent doing the work from the agent judging it proves to be a strong lever to address evaluation issues"* — directly matches c3's PICK / RECONCILE vs CRITIC split.

## GATHER is the single agentic stage

Code reference: [`agent.py`](../agent.py) Stage 2 GATHER (function `_run_gather`).

The agentic loop:
- LLM emits a `RoundDirective` per round containing `tool_calls` (LLM-chosen) and a `done` flag (LLM-chosen termination).
- Python harness dispatches the tool calls, records results into the registry, and re-enters the loop.
- Halts on (in priority order): `done=True` from LLM → `llm_terminated`; budget exhausted → `budget_exhausted_before_done`; max_rounds without done → `budget_exhausted_before_done`.

This is the Anthropic-textbook definition of an agent: *"LLMs autonomously using tools in a loop, maintaining control over how they accomplish tasks."*

Optional tool surface implemented by the GATHER/harness stack (not all enabled in the paper-facing default):
- `get_heritability` (h2) — disabled in the current default.
- `genetic_correlation_batch_estimator` (GC) — disabled in the current default.
- `get_open_targets_overlap` (OT) — disabled in the current default.
- `biology_retrieve_related_bundles` (biology) — disabled in the current default.
- `describe_pgs_model` / PGS Catalog hydration — retained downstream for model selection.

The current paper-facing default keeps the ReAct/harness structure but ablates h2 / GC / OT / biology evidence channels, leaves the archived cross-trait KB off, and enables the `prs_model_evaluator` Skill as advisory context at the PGS-selection stages (`PGS_TRIAGE` and `PICK`). The Skill is not injected as a global system-prompt rule block by default; it is delivered through `context_json["pgs_quality_guidance"]`, which matches the empirically retained iter11-family behavior and avoids over-weighting the Skill text.

The other 4 stages (SCOUT / JUDGE / PICK / CRITIC) are single-shot structured-output LLM calls — workflow, not agent.

## Production state: stable default

- Current paper-facing default: `no_all_tools_plus_pgs_skill` / iter11-family run.
- Retained reference run: `all-tools__paired80_pgs_skill_iter11_repeat2_20260430_024834_w20`.
- Retained paired80 performance: top_0.5%=23/80, top_1%=30/80, top_2.5%=36/80, top_5%=42/80, top_25%=65/80, mean rank fraction=0.1584, mean GPR=0.8419.
- v16 is now historical, not the paper-facing default. v16 reached top_0.5%=21 and top_25%=64 on the paired80 benchmark.
- More than 30 architectural variants attempted across multiple sessions (h2 framing, GC redesigns, OT synthesis, PICK metric_priority, GP cross-bundle override, full Codex 27-round exploration of the 18-target bottom_75% tail) did not beat the retained iter11-family default in a way worth keeping.

2026-05-03 follow-up iteration confirmed this freeze decision. Four narrow post-iter11 variants were tried and rejected:

| Variant | Mechanism | Paired80 result | Decision |
|---|---|---|---|
| Prompt-declared PGS Skill | Expose `pgs_quality_guidance` explicitly in active-stage system prompts | top_0.5%=16, top_1%=24, top_25%=60 | rejected |
| Tail-robust GP prompt | Add generic top25 rescue guidance at Global Primary | top_0.5%=20, top_1%=28, top_25%=59 | rejected |
| No-skill control reference lane | Add independent control candidate for final arbitration | top_0.5%=18, top_1%=27, top_25%=62 | rejected |
| h2 at Global Primary | Expose h2 records to cross-bundle reconciliation | top_0.5%=19, top_1%=28, top_5%=44, top_25%=62 | rejected |

The mechanism was consistent: extra final-stage guidance can improve isolated mid-tail cases, but it perturbs too many top-tail choices. The production default therefore remains the lighter iter11-family Skill harness, and failed scratch artifacts were removed rather than retained as candidate runs.

## Decision: architecture frozen, presentation upgraded

Architectural lever is currently low-return; further changes should be benchmark-gated. What remains is **presentation-level work** to make the harness engineering claim defensible to reviewers.

**Architecture: NO change.** In particular:
- Do not add more agentic stages. The other 4 are well-defined decision points; converting them to agents violates Anthropic's "workflows are better for well-defined tasks" guidance and risks regressing the locked-in performance.
- Do not change the paper-facing default tool surface without a paired80 lift: h2 / GC / OT / biology remain off, archived cross-trait KB remains off, and `prs_model_evaluator` remains on as context-only PGS-selection Skill guidance.
- Do not change halt conditions, budgets, or schemas.

**Presentation: upgrades planned.**

1. **Explicit Anthropic role tags** in `agent.py` docstrings and key call sites (`_run_scout` → "Planner", `_run_gather` → "Generator (agentic)", `_run_judge` / `_run_pick` / `_run_global_primary` → "Generator (workflow)", `_run_critic` → "Evaluator").
2. **Ablation table** showing each harness component is load-bearing:
   - GATHER ReAct loop vs single-shot Gather (defends the agentic stage)
   - With vs without CRITIC (defends generator/evaluator separation)
   - With vs without each evidence tool (h2, GC, OT, biology) — already partly captured, consolidate.
3. **Harness threshold non-load-bearingness**: ablation over `max_tool_calls` / `max_gather_rounds` / probe shortlist sizes — show these aren't load-bearing, supporting the "LLM-led, harness-orchestrated" claim.
4. **Three-pillar diagram** for the paper: c2 minimal generator-evaluator harness on the left, c3 full hybrid harness on the right, both consuming the prs_model_evaluator skill from below, both invoked by the top-level PennPRS shell agent above.

## Why c3 is the more interesting harness case study

For paper framing, c3 carries the heavier load on the "Agent Harness Engineering" pillar:

- It instantiates the **complete Anthropic three-agent pattern** (Planner / Generator / Evaluator), not a degenerate two-role version.
- It contains a **real ReAct agent** stage with 5-tool surface and LLM-controlled termination.
- It demonstrates **structured context handoffs** (EvidenceRegistry, GC batch, OT registry) that Anthropic's harness post explicitly highlights.
- It enforces **separation of generation and evaluation** (Pick/Reconcile vs Critic), which Anthropic flags as "a strong lever."
- It supports **progressive disclosure / context compaction** (PGS triage → hydrate; bundle dossier compaction).

c2 provides the contrasting **minimal generator-evaluator harness** end of the spectrum: a Skill/H2-grounded same-trait shortlist generator plus a separated holistic evaluator. The two together demonstrate harness engineering across a range, rather than two near-identical harnesses.

## Sources

(See parent doc for full anchor source list. c3-specific:)
- Anthropic — [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (three-agent pattern; separation-of-concerns quote)
- Anthropic — [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) (workflow vs agent boundary)
- Princeton — [HAL harness leaderboard](https://github.com/princeton-pli/hal-harness) (ICLR 2026 — empirical evidence that harness tuning matters more than model swaps)
