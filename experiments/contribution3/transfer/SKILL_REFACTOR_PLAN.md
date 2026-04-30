# Contribution3 Prompt-to-Skill Refactor — Execution Plan v2

> Based on the user's Handoff Brief (this file is the canonical plan;
> the brief is its source of truth for §1–§13). v2 incorporates a
> post-mortem from the v1 attempt — see §14.

## 0. Read this first: prior attempts have regressed

This refactor has been attempted before and **failed the performance bar**.
The hard constraint in §2 is non-negotiable. Documented failure modes from
prior attempts are listed in §11; v1 post-mortem is in §14.

**The single biggest known failure mode is naïve extraction that drops
nuance: a rule's *reason* often matters more than the rule itself, and
stripping the reason while keeping the threshold causes silent regression.**

---

## 1. Goal

Separate role/instruction content from domain knowledge content in
contribution3's six LLM stages, mirroring the architecture already in
place for contribution2. The extracted domain knowledge becomes a new,
runtime-loaded **skill** — sibling to the existing
`prs_model_domain_knowledge` skill — that the six contribution3 stages
invoke at runtime via the existing `context_json` channel. Prompts retain
only role definition + tool specs + output schema + halting/budget rules
+ forbidden actions.

**Scope: contribution3 only.** Do not modify contribution2 code, schemas,
KB, or any caller of contribution2 components in this task.

---

## 2. Hard constraint (non-negotiable)

Cross-trait benchmark performance, measured on the same target set and
metric definition as the existing **P21** run, must be **≥ P21**. The P21
run artifact is on disk at:

```
experiments/contribution3/transfer/runs/tool_calling_agent/unified/all-tools__p21_80target_20260424/results.json
experiments/contribution3/transfer/runs/tool_calling_agent/unified/evaluation__p21_80target_20260424/all-tools__end_to_end_eval_summary.json
```

Headline numbers to beat (overall, 80 targets, condition=all-tools, ablation=full):

| metric                 | P21    |
|------------------------|--------|
| top_0.5pct hit         | 0.3333 |
| top_1pct hit           | 0.4500 |
| top_1.5pct hit         | 0.4834 |
| top_2pct hit           | 0.5000 |
| top_2.5pct hit         | 0.5167 |
| frontier_oracle_hit    | 0.5125 |
| mean_gpr               | 0.7832 |
| mean_rank_fraction     | 0.1893 |

**Acceptance gate:** all five top-X percentile hit rates must be
≥ P21. mean_gpr / frontier_oracle_hit / mean_rank_fraction are
informational; failure on any top-X is failure on the gate.

---

## 3. Architectural framing — the 3-layer design (locked)

```
PennPRS Agent (instance of AgentSquare modular design space, ICLR 2025)
│
├── Planning module:    contribution3 6-stage pipeline
│                       (scout → gather → judge → pick → global_primary → critic)
│                       (+ pgs_triage sub-stage inside pick)
│
├── Reasoning module:   per-stage LLM call (single-shot or ReAct loop)
│
├── Tool Use module:    ★ this task lives entirely inside this module
│   ├── PRS Catalog low-level tools (existing)
│   ├── PRS Model Domain Knowledge Skill (contribution2; UNCHANGED)
│   │   └── prs_model_domain_knowledge.md
│   └── Cross-Trait Transfer Domain Knowledge Skill (NEW; THIS TASK)
│       ├── Level 1 metadata: tool schema / docstring (always available)
│       ├── Level 2 body: stage-conditional curated rules (loaded on call)
│       └── Level 3 resources: optional supplementary data (deferred)
│
└── Memory module:      EvidenceRegistry / bundle_notes (already exists; not modified)
```

The two domain-knowledge skills are **peers** in the Tool Use module,
sharing retrieval helpers from `src/server/core/tools/prs_model_tools.py`
(`_parse_markdown_sections`, `_calculate_relevance`,
`_expand_domain_query_terms`, `_extract_target_trait_phrase`,
`_normalize_phrase`). Code reuse is mandatory; do not reimplement.

Architectural anchors (see §13 for citations):
- AgentSquare (Shang et al., ICLR 2025) — Planning + Reasoning + Tool Use + Memory
- Agent Skills (arxiv 2602.12430, 2026) — three-level progressive disclosure
- Voyager (Wang et al., NeurIPS 2023) — skill library
- DeepRare (Lu et al., Nature 2026) — *"deliberately offloads knowledge to specialized agents rather than centralizing it in system prompts"*
- BioContextAI (Nat Biotech 2026) — MCP-style server / client / host decoupling
- AILA (Mandal et al., Nat Comm 2025) — *"domain knowledge does not translate to experimental capabilities"* (parametric / static-prompt knowledge insufficient)

---

## 4. Decision already made (final, do not revisit)

Two **separate** skills, not one merged KB:
- `prs_model_domain_knowledge` (contribution2) — unchanged in this task.
- New: cross-trait transfer skill (contribution3) — to be created.

Both share retrieval infrastructure. contribution2 only loads its own
skill; contribution3 loads its own usage of contribution2's skill (where
applicable) plus the new cross-trait skill.

---

## 5. Current state — facts

### 5.1 contribution3 prompt files

Pipeline orchestrator: `experiments/contribution3/transfer/agent.py`. Stages:
1. scout (single-shot, line ~333)
2. gather (ReAct, line ~520; per-round context built at line ~616)
3. judge (single-shot, line ~673)
4. pgs_triage (sub-stage of pick, line ~761; runs when bundle has > 12 PGSs)
5. pick (per-bundle, line ~717)
6. global_primary (single-shot, line ~895)
7. critic (single-shot, line ~1058)

All 7 prompts are literal string constants in
`experiments/contribution3/transfer/prompts/transfer_prompt.py`:
`SCOUT_PROMPT`, `GATHER_SYSTEM_PROMPT`, `JUDGE_PROMPT`, `PICK_PROMPT`,
`PGS_TRIAGE_PROMPT`, `GLOBAL_PRIMARY_PROMPT`, `CRITIC_PROMPT`.

Chain builder: `experiments/contribution3/transfer/llm_chains.py`,
`_build_chain()` at line 43. **Domain-knowledge injection MUST go through
`{context_json}`** by adding a field to the dict that is
JSON-serialized into that variable. Do not introduce new template
variables. Do not modify `_build_chain()`.

### 5.2 Mixed regions per prompt — empirical-claim sentences to extract

(Re-audited from current P21 state; line numbers approximate.)

| Prompt | Approx. line range | Knowledge themes embedded |
|---|---|---|
| `SCOUT_PROMPT` | 53–66 | n_models ≥ 30 generalist heuristic + **reason** "shared polygenic architecture spans many endpoints"; comorbidity (mental-health / metabolic / inflammation) selection patterns; do-include-when-uncertain |
| `GATHER_SYSTEM_PROMPT` | 98–116, 127–141 | Tool descriptions intermixed with claims about what OT/H2 reveal; OT-first triage strategy; H2 conservation; pleiotropy/comorbidity in `bundle_notes` because GC unavailable |
| `JUDGE_PROMPT` | 186–198 | Multi-channel agreement preferred over single signal; mechanism-supported > lexical-match; same-trait/near-same-trait → rank-1 by default; **negative rule:** do-not-over-rank-generic-cross-trait-over-direct-same-trait |
| `PICK_PROMPT` | 240–278 | Multi-ancestry validation breadth as primary transferability signal; transfer ≠ published peak; cross-trait + same-trait branches; consortium multi-ancestry > newer single-ancestry mega-cohort despite higher AUC; consistency > peak; **negative rule:** do-NOT-weight-ancestry-by-priority-tier |
| `PGS_TRIAGE_PROMPT` | 311–325 | Semantic match on reported_trait/trait_efo/trait_mapped; cross-trait branch favors raw-quality + large training cohort; method+year diversity; recent-large-cohort as one diversity axis (not a fixed tier) |
| `GLOBAL_PRIMARY_PROMPT` | 359–374 | Raw quality signals (sample, AUC/R², variant count, methodology); **load-bearing reason:** generic bundle (BMI/height/T2D) PGS can outperform same-trait bundle's best because polygenic architecture spans endpoints; per_bundle_evidence (significant GC, OT overlap) as tiebreaker |
| `CRITIC_PROMPT` | minimal | Mostly role/output spec; per-axis-top3 explanation; revise-only-when-orthogonal-axis-contradicts |

**Sentences that are pure role/output instructions (e.g., "Return a
JudgeResult with fields..." or "Halt when budget is exhausted") stay
verbatim in the prompt. Sentences that are empirical claims about
cross-trait genetics or PGS transfer move into the new KB — copied
verbatim, not paraphrased.**

### 5.3 Existing stub KB

`experiments/contribution3/transfer/knowledge/cross_trait_transfer_evidence_reference.md`
— ~98 lines, human-facing, **not loaded at runtime**. Decision: fold any
non-redundant content into the new KB; delete the stub only after the
80-target hard gate passes.

### 5.4 Reference architecture — contribution2 (style-locked)

Tool: `src/server/core/tools/prs_model_tools.py`, function
`prs_model_domain_knowledge` ~lines 864–979. Returns:
- `query`
- `full_document` (entire markdown, optionally with dynamic h2 prepend)
- `snippets[]` (top-k by relevance: `source` / `section` / `content` / `relevance_score`)
- `source_type`

Helpers (reuse, do not copy):
- `_parse_markdown_sections` — `##` / `###` splitter
- `_calculate_relevance` — keyword scoring (title +3, content +1, count +0.2 capped, target-trait +8 title / +4 content, hardcoded section triggers +4)
- `_expand_domain_query_terms` — alias expansion
- `_extract_target_trait_phrase` — trait phrase extraction
- `_normalize_phrase` — text normalization

KB: `src/server/core/knowledge/prs_model_domain_knowledge.md` — ~468 lines.
Style:
- Empirical-evidence-introduction paragraph at top (cross-cutting findings before any field-level rule).
- Per-section guidance with explicit positive-signal / warning-signal pairs.
- Trait-agnostic at the rule level — no "if target is X then..." disease-specific conditionals.
- **Reads as curated genetics-literate prose, not as bulleted instructions.** ← v1 violated this; v2 must not.

### 5.5 Performance baseline — P21

Located: §2. Target set: 80 unified targets (20 type-A + 60 type-B from `cmd_offline_unified` config). Metric: `official_metrics.hit_at_percent.top_X` and aggregates, computed by `cmd_evaluate_end_to_end`.

Project memory references baseline run `all-tools__20260413_124729`; verify on disk if needed (not required for this task — P21 is the gate).

---

## 6. Target state

### 6.1 Stage → KB section mapping (audit aid)

Trait-agnostic style mandatory. Section ordering / naming is execution-time discretion, but the dispatch table maps stages to section headers.

1. **Bundle Selection Heuristics** — for SCOUT.
2. **Evidence Channel Hierarchy** — for GATHER (and JUDGE shares).
3. **Same-Trait vs Cross-Trait Bundle Ranking** — for JUDGE.
4. **PGS Transferability Signals** — for PICK.
5. **Cross-Bundle Reconciliation** — for GLOBAL_PRIMARY.
6. **PGS Triage** — for pgs_triage.
7. **Critic Cross-Checks** — for CRITIC.

### 6.2 New artifacts

- `experiments/contribution3/transfer/knowledge/cross_trait_domain_knowledge.md` — the new KB. Structure-locked to §5.4 contribution2 style. **Content extracted VERBATIM from prompts where possible (see §11.1).** Estimated 350–500 lines.
- `experiments/contribution3/transfer/tools/cross_trait_domain_knowledge.py` — runtime callable mirroring `prs_model_domain_knowledge`'s signature/return shape. Reuses helpers from contribution2's tool module (import only; no copy-paste).
- Tool schema entry — added to `src/server/core/tool_schemas.py` for documentation/paper-writeup parity (Level 1 metadata in three-level disclosure). Not needed for runtime since contribution3 invokes the tool directly from agent.py code.
- 7 invocation sites in `agent.py` to inject `domain_knowledge` into per-stage `context_json`.

### 6.3 Modified artifacts

- 7 prompts in `transfer_prompt.py` — empirical-claim sentences extracted; role/instruction sentences preserved verbatim. Each prompt receives a short `# Domain knowledge` boilerplate above `# Constraints` pointing to the `domain_knowledge` field.
- `agent.py` — import + 7 inline `cross_trait_domain_knowledge(stage=...)` calls.
- `experiments/contribution3/transfer/tools/__init__.py` — export new tool.

### 6.4 Untouched

- contribution2 (tool / KB / schema / callers / prompts).
- `_build_chain()`, the `{context_json}` mechanism, all Pydantic schemas, the six-stage pipeline structure.
- `EvidenceRegistry` and `bundle_notes`.

---

## 7. Constraints (non-negotiable)

1. **Performance ≥ P21.** Same benchmark, target set, metric. See §2.
2. **No information loss.** Every empirical claim currently in the 7 prompts must appear in the new KB. Audit: list extracted sentences and match to KB sections.
3. **Trait-agnostic rules.** No disease-specific conditionals.
4. **Minimal prompt rewording.** Do not paraphrase role/instruction sentences during extraction. Only remove sentences that are domain knowledge. Diff must be reviewable line-by-line.
5. **Style parity.** Reader who knows `prs_model_domain_knowledge.md` should immediately recognize the new KB as a sibling — same heading conventions, same evidence-then-guidance pattern, same voice.
6. **Reuse, don't reimplement.** Refactor helpers in place if generalization is needed; verify contribution2 behavior unchanged.
7. **Stage-conditional retrieval.** PICK must not see SCOUT-only knowledge or vice versa. Stage-conditioned retrieval mandatory.
8. **Token budget.** Per-stage `context_json` payload should not balloon. Use snippet selection + full-doc fallback.
9. **Preserve negative rules.** "Do NOT weight ancestry by priority tier" / "do not over-rank generic cross-trait over direct same-trait" / "Do NOT invent IDs" — short, easy to lose, load-bearing.
10. **Preserve the *reason* attached to a rule.** "n_models ≥ 30 implies generalist prior" comes with "shared polygenic architecture spans many endpoints" — the reason is what lets the LLM judge edge cases. **This was the dominant v1 failure mode; see §14.**

---

## 8. Verification checklist

1. All 7 prompts no longer contain empirical-claim sentences. Audit table.
2. Every removed claim has a home in the new KB. Audit table.
3. New tool returns expected sections for each of the 7 stage parameters (smoke).
4. **20-target gate (NEW; see §15).** Run `cmd_offline_unified` on a 20-target subset (see §15 for selection). If any top-X metric falls below P21 by more than the noise margin (§15), STOP and revert.
5. **80-target final.** Only run if 20-target gate passes. Compare every top-X to P21; gate is "all five top-X ≥ P21".
6. End-to-end single target through all 7 stages with no runtime errors.
7. contribution2 behavior preserved: smoke test the contribution2 entry point.
8. Forbidden-phrase lint over both prompts and KB.
9. Commit message states what was done with the 98-line stub.

---

## 9. Open decisions made by execution

| Decision | Choice |
|---|---|
| New tool function name | `cross_trait_domain_knowledge` |
| New tool file | `experiments/contribution3/transfer/tools/cross_trait_domain_knowledge.py` (peer to existing tool files in contribution3 — proximity to consumer) |
| Helper reuse | Import from `src.server.core.tools.prs_model_tools` directly. No refactor of contribution2 unless a helper proves not transferable (see §11.6). |
| KB filename | `cross_trait_domain_knowledge.md` |
| KB directory | `experiments/contribution3/transfer/knowledge/` (already exists) |
| Section structure | One per stage (7 sections) + cross-cutting empirical introduction |
| context_json field name | `domain_knowledge` |
| Snippet logging | Skipped for now; add only if 20-target gate fails and we need ablation auditability |
| 98-line stub fate | Keep until 80-target gate passes; delete on cleanup |
| Level-3 resources | Deferred (not needed for parity with P21) |
| Tool schema entry | Documentation-only addition to `tool_schemas.py`; runtime injection from agent.py code |

---

## 10. Out of scope

- Any modification to contribution2 / contribution1.
- Pipeline structure changes / Pydantic schema changes.
- Embedding-based retrieval.
- Memory module changes.
- Paper Methods writeup.
- 3-way ablation (no-domain / system-prompt / skill+MCP).

---

## 11. Failure modes to watch for (from v1 + brief)

### 11.1 Naïve extraction that drops the *reason* attached to a rule
The SCOUT n_models ≥ 30 rule has the reason "shared polygenic architecture
spans many endpoints" attached. The PICK consortium-vs-mega-cohort tradeoff
has the reason "newer mega-cohort PGSs are frequently optimised for and
validated on a single ancestry, and their published AUC is inflated
relative to multi-ancestry transfer." If only the threshold or directive
is preserved without the reason, the LLM cannot judge edge cases.
**Mitigation: copy the rule + reason as a single coherent prose block
verbatim. Do not split into "rule bullet" + "reason bullet" lists.**

### 11.2 Stage-knowledge mismatch
Feeding PICK-stage knowledge to JUDGE silently degrades reasoning.
Stage-conditioned retrieval mandatory.

### 11.3 Style drift
If the new KB reads like a different author's voice from
`prs_model_domain_knowledge.md`, rewrite for parity before shipping.
**v1 violation: bullet-list "Key principle / Positive signals / Warning
signals" structure that contribution2 KB does not use. v2 uses prose
paragraphs with positive/warning sub-headers, mirroring contribution2.**

### 11.4 Token bloat from full-document injection at every stage
Use snippet selection + full-doc fallback. Watch token count when
verifying.

### 11.5 Loss of negative rules
Negative rules ("do NOT do X") are short, easy to miss during extraction,
load-bearing. Enumerate explicitly in §5.2 audit.

### 11.6 Helper subtle behavior
`_calculate_relevance` has hardcoded section-keyword triggers tuned for
contribution2. The new KB may need its own tuning. Verify retrieval on
the new KB before benchmarking.

### 11.7 Heritability injection collision
contribution2's tool prepends a dynamic h2 section to `full_document`
when a trait-specific h2 estimate is found. The new tool will NOT do
this — h2 is already in `EvidenceRegistry` for contribution3 stages
that need it.

---

## 12. Vocabulary (for the eventual paper Methods)

- "Agent skill" / "skill library" with Voyager (NeurIPS 2023) anchor.
- "MCP" / "MCP-style server" — already in 2026 Nature-tier vocabulary via DeepRare and BioContextAI.
- Avoid "Anthropic Skills" / "Claude Skills" branding.
- Frame both contributions as instances of AgentSquare's Tool Use module — domain-specialized agent skills with three-level progressive disclosure backed by an MCP-style retrieval interface.

---

## 13. References

- AgentSquare — Shang et al., ICLR 2025 — https://arxiv.org/abs/2410.06153
- Agent Skills survey — arxiv 2602.12430, 2026 — https://arxiv.org/abs/2602.12430
- Voyager — Wang et al., NeurIPS 2023 — https://arxiv.org/abs/2305.16291
- DeepRare — Lu et al., Nature 2026 — https://www.nature.com/articles/s41586-025-10097-9
- BioContextAI — Nat Biotech 2026 — https://www.nature.com/articles/s41587-025-02900-9
- AILA — Mandal et al., Nat Comm 2025 — https://www.nature.com/articles/s41467-025-64105-7
- PhenoAssistant — Nat Comm 2026 — https://www.nature.com/articles/s41467-026-71090-y
- BioMedAgent — Nat Biomed Eng 2026 — https://www.nature.com/articles/s41551-026-01634-6

---

## 14. Post-mortem of v1 attempt (2026-04-26)

**Result:** Hard gate failed. top_0.5/1/1.5/2/2.5pct all regressed by 12–15pp vs P21.

**Diagnosis:** Stage-level diagnostics showed a clean split.
- Scout / Gather / Judge / per-bundle Pick aggregated: `frontier_oracle_hit_rate` *improved* +11.25pp (0.5125 → 0.6250). Front half of pipeline: extraction was at worst neutral, partly beneficial.
- Global Primary Reconciliation: regressed badly. Frontier candidates were better, but the LLM picked worse primaries from those better candidates.

**Root causes (ordered by impact):**

1. **Lossy paraphrase** (§11.1). v1 KB structure was bullet lists like:
   ```
   Positive signals:
   - A generalist / anthropometric / metabolic bundle whose PGS carries
     markedly stronger raw performance than the same-trait bundle's best
   ```
   The original P21 prompt had this as a self-contained paragraph with
   the reason attached: *"Polygenic architecture frequently lets a
   high-quality metabolic PGS outperform a smaller same-trait PGS on an
   unrelated disease endpoint."* — the reason was severed during
   extraction. **v2 mitigation: prose paragraphs, copy verbatim.**

2. **Reasoning-bullet flattening** (§11.3). v1 flattened a paragraph that
   was structurally "REMINDER: do not dismiss generalist bundles" into a
   bullet entry equal to other "good signals." LLM attention is uniform
   across list items, so the reminder lost its emphasis.
   **v2 mitigation: keep reminders as separate prose paragraphs, mirroring
   contribution2's "When candidates are otherwise similar:" sub-headings.**

3. **Channel mismatch** (structural, not fully resolvable under §10).
   System prompt rules have stronger directive force than nested JSON
   field values. Brief settles this constraint. **v2 mitigation: short
   but assertive boilerplate in each prompt that explicitly directs the
   LLM to consult `domain_knowledge.primary_section` *before* writing
   its decision rationale.**

**v1 stages that worked (Scout/Gather/Judge/per-bundle Pick) suggest the
extraction is viable for set-valued / ranked-list decisions; v1 failure
on Global Primary suggests argmax decisions are sensitive to lossy
extraction. v2 must extract Global Primary content with extra care.**

---

## 15. 20-target gate (added v2)

The user requires a 20-target gate before running the full 80-target
benchmark. This is a budget guardrail — if v2 regresses, we revert
without burning 80-target API costs.

### 15.1 Target subset

20 of the 80 unified targets, drawn from the same dossier file used by P21
(`experiments/contribution3/transfer/runs/tool_calling_agent/unified/candidate_dossiers.json`),
selected as the **first 20 in the canonical order** (preserves
reproducibility; same selection P21 sees in its own first 20).

The expected 20-target acceptance numbers come from the P21 results.json
filtered to the same subset. Compute the per-target oracle hits at
0.5/1/1.5/2/2.5 pct from P21's existing per-target detail, and require
v2 to match or beat each on the same subset.

### 15.2 Gate pass criterion

For each top-X% metric:

```
v2_count >= P21_count - 1
```

Allowing slack of 1 hit per metric on the 20-target subset (~5pp slack)
to absorb LLM stochasticity. If v2 *misses* on more than one metric,
revert. If v2 strictly improves on all five, ship to 80-target.
If v2 ties P21 within slack on all five, ship to 80-target.

### 15.3 Decision flow

```
20-target run
  │
  ├── all five top-X ≥ P21_count - 1? ──YES──► run 80-target (Phase J)
  │                                  ──NO───► revert (Phase K)
  │
  └── runtime errors / contribution2 broke? ──► revert immediately
```

### 15.4 80-target gate (after 20-target passes)

```
80-target run
  │
  ├── all five top-X ≥ P21? ──YES──► finalize (delete stub, commit)
  │                        ──NO───► revert
  │
  └── any other metric regressed > 5pp? ──► investigate before commit
```

---

## 16. Execution order

| Phase | Action |
|---|---|
| A | Write this plan (DONE) |
| B | Confirm P21 baseline numbers (DONE — see §2) |
| C | Re-read 7 prompts; extract sentences with reasons + negatives intact |
| D | Author KB md in contribution2-style prose; verbatim where possible |
| E | Author tool function reusing helpers |
| F | Wire 7 injection sites |
| G | Strip prompts MINIMALLY |
| H | Lint + 3-target smoke (no errors) |
| I | **20-target gate** |
| J | **80-target final** (only if I passes) |
| K | Cleanup (delete stub) + commit / OR revert (if any gate fails) |
