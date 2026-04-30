# `skill_overrides/` — contribution3-private overrides for the prs-model-evaluator skill

Files placed in this folder are **only** loaded by the contribution3
transfer pipeline's stage-aware skill loader. They are **never** read
by contribution2's view of the prs-model-evaluator skill, and they are
**never** part of the portable skill folder at
`src/server/core/skills/prs_model_evaluator/`.

This separation keeps the canonical skill folder portable to other
projects (no consumer-specific subdirectories) while still letting
contribution3 layer experiment-specific guidance on top of it at
load time.

## The three c3 modification patterns

When a c3 experiment wants to change what the skill says without
altering what contribution2 reads from the same folder, the supported
patterns are:

### Pattern 1 — ADD content (new c3-only material)

Use when contribution3 needs guidance that contribution2 doesn't.

1. Write the new content as a `.md` file under this folder.
2. List its filename in `STAGE_TO_OVERRIDE_FILES[stage]` in
   `src/server/core/tools/prs_model_evaluator_skill.py` for whichever
   stage(s) should consume it.

contribution2's view (`load_c2_view`) ignores `skill_overrides/`
entirely, so the additions are invisible there.

### Pattern 2 — REMOVE content from c3 (c2 still gets it)

Use when contribution3 wants to skip a section that contribution2 still
needs. Simplest case: the routine c3 default already loads no
`reference/*.md` files at any stage (true progressive disclosure), so
"remove" is the default.

To remove a reference section that some other stage was opting into,
drop the filename from `STAGE_TO_REFERENCE_FILES[stage]`.

contribution2's view always concatenates the full `reference/*.md` set,
so the removal is invisible there.

### Pattern 3 — MODIFY shared content for c3 only (c2 sees the original)

Use when contribution3 wants different empirical guidance than what the
canonical corpus says — for example, softening Section 1's
endpoint-fidelity priority for cross-trait transfer scoring while
contribution2 keeps using the canonical Section 1 unchanged.

**Do NOT directly edit `reference/01_*.md` for this.** That file is
byte-equal to the canonical corpus (sync test enforces); editing it
would either break the sync test or, if you also edit the canonical
.md to match, change contribution2's behaviour.

The supported way is the **omit + add** combination:

1. Author the c3-specific replacement as a new `.md` file under this
   folder. Example name: `pick_endpoint_fidelity_for_transfer.md`.
2. In `src/server/core/tools/prs_model_evaluator_skill.py`:
   - Remove the canonical filename (e.g. `01_trait_reported_*.md`)
     from `STAGE_TO_REFERENCE_FILES[stage]` for the stage(s) where you
     want the swap. (If the stage's tuple was empty by default,
     "remove" is a no-op.)
   - Add the replacement filename to `STAGE_TO_OVERRIDE_FILES[stage]`.

The c3 view at that stage now contains your replacement content
instead of the canonical Section 1. The c2 view is byte-identical to
the canonical .md, before and after.

This pattern is verified end-to-end by
`test_c3_can_modify_shared_section_via_omit_and_add_without_touching_c2`
in `experiments/contribution3/transfer/tests/test_skill_two_view_contract.py`.

## When NOT to put a file here

If the change is a correction to the **shared empirical patterns** in
the canonical corpus that should also benefit contribution2, edit
`src/server/core/skills/prs_model_evaluator/reference/*.md` AND
`src/server/core/knowledge/prs_model_domain_knowledge.md` together.
The c2-compat sync test
(`experiments/contribution3/transfer/tests/test_skill_c2_compat_sync.py`)
fails until the two views are aligned, which is the safety guard for
"contribution2 unchanged".

## Load discipline (loader contract)

The c3 loader composes per-stage skill text in this order, each
optional:

1. `SKILL.md` body (always loaded when the skill is enabled).
2. Selected `reference/NN_*.md` files for the stage (per
   `STAGE_TO_REFERENCE_FILES`; default empty).
3. Selected files from this folder for the stage (per
   `STAGE_TO_OVERRIDE_FILES`; default empty).

Override files are concatenated additively after reference files; they
do not replace reference files automatically (Pattern 3 above is the
explicit replacement recipe).
