"""Raw-data-only tool package for the LLM-led cross-trait transfer agent.

Each tool returns **raw fields** consumed directly by the LLM. Derived
scores, confidence tiers, priority rankings, and threshold flags are
FORBIDDEN here — see REFACTOR_PLAN.md §5.

The cross_trait_domain_knowledge skill is a peer of contribution2's
prs_model_domain_knowledge skill — see SKILL_REFACTOR_PLAN.md.

Legal imports:
    from experiments.contribution3.transfer.tools import (
        genetic_correlation_batch_estimator,
        get_heritability,
        get_open_targets_overlap,
        describe_pgs_model,
        biology_retrieve_related_bundles,
        cross_trait_domain_knowledge,
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
]
