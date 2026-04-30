# TODO — contribution2 harness + skill upgrade

Status: deferred. Recorded after the contribution3 prs_model_evaluator
skill landed (see `src/server/core/skills/prs_model_evaluator/SKILL.md`
and `experiments/contribution3/transfer/tools/prs_model_evaluator_skill.py`).
contribution2 currently still uses the legacy single-shot pipeline
calling `prs_model_domain_knowledge(query, max_snippets=8)` directly
and is intentionally untouched.

## Why bother

Empirical baseline (75-disease, gpt-5.2, t=10):
- `with-domain` (DK on, single-shot): top-1 = 0.3333, top-5 = 0.7467
- `without-domain` (DK off, single-shot): top-1 = 0.2400, top-5 = 0.6400
- `tiered_pgs_only_auc` baseline: top-1 = 0.0933

Lift over random (median pool size = 7): with-DK ≈ 2.3×; without-DK ≈ 1.7×.
Lift over the AUC-only baseline: with-DK ≈ 3.6× at top-1.

DK already extracts most of the available signal. Remaining headroom is
bounded by an irreducible noise ceiling (PGS quasi-tying on the AoU
validation cohort — multiple same-disease PGSs are within sample-noise
of each other). Best-case ceiling is ~50–65 % top-1; the right harness
work targets the gap from 33 % → ~40–45 %, not 33 % → 80 %.

## Work items (rough priority order)

### P1 — cheapest interventions, highest expected lift

1. **CRITIC verification pass.** Add a second LLM call after the picker
   returns its choice. CRITIC sees the same candidate records plus the
   prs_model_evaluator skill text, and is asked to revise the pick only
   if the chosen candidate violates a leakage / packaging pattern that
   the picker missed. Pure verification — no candidate scoring, no hard
   rules. Estimated lift: +3–6 pp top-1.

2. **Cross-trial conflict resolution.** Today: t=10 trials → modal
   majority vote. When the modal vote is split (≤6 of 10 agree) and the
   top two PGSs are different, run a head-to-head deliberation prompt
   that compares the two finalists explicitly using the DK rules.
   Estimated lift: +1–2 pp top-1, mostly on the hard-tail diseases.

3. **Triage step for long-tail diseases (candidate pool ≥ 30).** Mirror
   contribution3's PGS triage stage (compact summaries → narrow to
   top-15 → full describe). Pool sizes range 2–258; the long tail is
   where the picker truncates. Estimated lift: +1–3 pp top-1 on the
   ~22 / 75 diseases with pool ≥ 30.

### P2 — agent-skill packaging

4. **Refactor c2's `prs_model_domain_knowledge(query, max_snippets=8)`
   call to invoke the prs_model_evaluator skill instead.** The skill
   already wraps the same source corpus (single source of truth — see
   `src/server/core/skills/prs_model_evaluator/SKILL.md`). For c2 this
   gives:
   - Procedural overview prelude that frames the rules as a checklist
     for the LLM, not a passive reference. Modest expected lift from
     better LLM compliance.
   - Frontmatter description loaded into the system prompt so the
     intent of the rules is visible in the conversation transcript
     without paying for the body tokens.
   - Single canonical entry point shared between c1 / c2 / c3.

   Implementation: keep the existing
   `prs_model_domain_knowledge(query, max_snippets=8)` API as a thin
   wrapper that dispatches to the skill loader. Existing call sites in
   `experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py`
   can stay unchanged; the function returns the same `DomainKnowledgeResult`
   shape.

5. **Verify zero behaviour regression.** Run a paired
   `with-domain-skill-wrapped` vs current `with-domain` arm on the 75-disease
   benchmark (10 trials each). Acceptance: top-k accuracy within ±1 pp at
   every k. Only ship the wrapper if the gate passes; otherwise debug
   the prompt-text rendering difference.

### P3 — tool-augmented evidence (bigger lift, bigger surface area)

6. **GATHER-equivalent evidence enrichment.** Per candidate, fetch
   per-ancestry reported AUCs, training-trait heritability, and
   study-family clustering signals. These are not currently visible to
   c2's single-shot picker. Estimated lift: +3–5 pp top-1, but requires
   contribution3-style harness wiring (BudgetGuard, EvidenceRegistry,
   per-stage prompt builders). Significant engineering investment;
   schedule only if P1 + P2 fall short of target.

### P4 — structural safety net (LOW PRIORITY, may conflict with policy)

7. **Deterministic prefilter for explicit leakage covariates.** REQUIRES
   POLICY DECISION before scheduling. The project rule is "LLM-led
   decisions, no hardcoded rules dominating". A black-listed-covariate
   prefilter would be a deterministic gate; only land it if the team
   decides that explicit leakage covariates are a hard hygiene boundary
   (analogous to the c3 harness `harness:breadth_floor` mechanism that
   adds candidates without ranking them). Until then, treat the leakage
   patterns as advisory text in the skill and let the LLM decide.

## Out of scope

- Full c3-style 6-stage pipeline (SCOUT → JUDGE → PICK → RECONCILE →
  CRITIC). Wrong shape for c2: candidate pool is small and decisions
  are single-shot. The components above are the c2-appropriate slice.
- Modifying `src/server/core/knowledge/prs_model_domain_knowledge.md`.
  This is the shared source of truth used by both c2 and c3
  (prs_model_evaluator skill slices it). Edits must preserve the
  section structure documented in
  `src/server/core/skills/prs_model_evaluator/SKILL.md`.

## Estimated combined lift

P1 (1+2+3) on top of current with-domain baseline: 33.3 % → ~37–43 %
top-1. Diminishing returns after that until P3 lands new evidence
channels. Hard ceiling around 50–65 % from cohort noise, regardless of
harness investment.
