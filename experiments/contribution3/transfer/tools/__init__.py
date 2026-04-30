"""Raw-data-only tool package for the LLM-led cross-trait transfer agent.

Each tool returns **raw fields** consumed directly by the LLM. Derived
scores, confidence tiers, priority rankings, and threshold flags are
FORBIDDEN here — see REFACTOR_PLAN.md §5.

Skills (advisory text only; LLM-led decision-making preserved):

- `cross_trait_domain_knowledge` — ARCHIVED FOR PRODUCTION. Empirically
  verified to provide zero lift on top of `no_all_tools` baseline on
  paired80 (skill_only top_0.5%=0.325 == no_all_tools top_0.5%=0.325).
  Kept importable for historical reproducibility and ablation parity;
  default ablations should not enable it. See driver.py for the
  archived ablation labels.
- `prs_model_evaluator_skill` — ACTIVE. Stage-aware loader for the
  Anthropic Agent Skill at src/server/core/skills/prs_model_evaluator/.
  Reads SKILL.md procedural overview and slices the source corpus
  (src/server/core/knowledge/prs_model_domain_knowledge.md, the same
  corpus consumed by contribution2 unchanged) per-stage. Injected at
  PICK / GLOBAL_PRIMARY_RECONCILIATION / CRITIC stages when
  `enable_pgs_quality_skill=True`.

Legal imports:
    from experiments.contribution3.transfer.tools import (
        genetic_correlation_batch_estimator,
        get_heritability,
        get_open_targets_overlap,
        describe_pgs_model,
        biology_retrieve_related_bundles,
        cross_trait_domain_knowledge,        # archived; see note above
        prs_model_evaluator_skill,           # active
    )

`describe_pgs_model` is a HARNESS-only tool: imported by agent.py for
Pick-stage PGS hydration, but NOT registered as an LLM-callable tool
in the Gather dispatcher (the LLM cannot invoke it directly).
"""
from experiments.contribution3.transfer.tools.cross_trait_domain_knowledge import (
    cross_trait_domain_knowledge,
)
from experiments.contribution3.transfer.tools.gc_batch import (
    GCBatchResult,
    GCCandidateEstimate,
    genetic_correlation_batch_estimator,
)
from experiments.contribution3.transfer.tools.h2 import get_heritability
from experiments.contribution3.transfer.tools.ot import get_open_targets_overlap
from experiments.contribution3.transfer.tools.pgs import (
    compact_pgs_summary,
    describe_pgs_model,
)
from experiments.contribution3.transfer.tools.biology import (
    biology_retrieve_related_bundles,
)
from experiments.contribution3.transfer.tools.prs_model_evaluator_skill import (
    PgsModelEvaluatorResult,
    prs_model_evaluator_skill,
)

__all__ = [
    "genetic_correlation_batch_estimator",
    "GCBatchResult",
    "GCCandidateEstimate",
    "get_heritability",
    "get_open_targets_overlap",
    "describe_pgs_model",
    "compact_pgs_summary",
    "biology_retrieve_related_bundles",
    "cross_trait_domain_knowledge",
    "prs_model_evaluator_skill",
    "PgsModelEvaluatorResult",
]
