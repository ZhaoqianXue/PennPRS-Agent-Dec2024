"""LLM-led cross-trait transfer agent (v-final).

Five stages, each a single LLM call (Stage 2 is a ReAct loop of LLM calls):
  Stage 1  SCOUT    - choose probe bundles
  Stage 2  GATHER   - ReAct evidence-gathering, LLM self-terminates
  Stage 3  JUDGE    - fresh LLM call ranks bundles
  Stage 4  PICK     - fresh LLM call per top-K bundle, picks PGS models
  Stage 5  CRITIC   - fresh LLM call revises frontier if evidence contradicts

No weights, no thresholds, no deterministic overrides. `harness.py` drops
invalid IDs but never substitutes replacements. `EvidenceRegistry` is the
persistent memory that Judge and Critic consume (not the ReAct scratchpad).

See REFACTOR_PLAN.md for the full architectural rationale.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, replace
from typing import Any, Optional

from experiments.contribution3.transfer.common import (
    CandidateBundleDossier,
    TraitBundle,
)
from experiments.contribution3.transfer.harness import (
    BudgetGuard,
    ToolDispatcher,
    filter_known_bundle_ids,
)
from experiments.contribution3.transfer.schemas import (
    BundleRanking,
    CritiqueDecision,
    FrontierModel,
    ModelFrontier,
    RoundDirective,
    ScoutDirective,
    ToolCall,
)
from experiments.contribution3.transfer.state import (
    AgentTrace,
    EvidenceRegistry,
    ProvenanceLog,
    RoundState,
)
from experiments.contribution3.transfer.tools import (
    biology_retrieve_related_bundles,
    cross_trait_domain_knowledge,  # ARCHIVED: see tools/__init__.py
    describe_pgs_model,
    genetic_correlation_batch_estimator,
    get_heritability,
    get_open_targets_overlap,
    prs_model_evaluator_skill,
)
from experiments.contribution3.transfer.llm_chains import (
    critic_chain,
    gather_chain,
    global_primary_chain,
    judge_chain,
    pgs_triage_chain,
    pick_chain,
    scout_chain,
)
from experiments.contribution3.transfer.tools.pgs import compact_pgs_summary

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Runtime toggles — module-level baseline (kept for backward compat)
# ---------------------------------------------------------------------------
# Module-level compatibility switches remain for legacy v16-style runs. Current
# paper-facing defaults flow through `ToolAblationConfig` via driver.py.
ENABLE_BIOLOGY_HELPER = True
ENABLE_GC_BATCH = True


# ---------------------------------------------------------------------------
# Tool-level ablation configuration
# ---------------------------------------------------------------------------
@dataclass
class ToolAblationConfig:
    """Per-run toggles for the 4 evidence-channel tools and sealed skill.

    Each flag governs both the LLM-callable surface (Gather dispatcher) and
    any harness-orchestrated invocation of the same tool, so an ablated
    tool is fully removed from the pipeline (LLM cannot call it; harness
    does not auto-invoke it). Downstream consumers (Judge / Critic / GP)
    observe the corresponding EvidenceRegistry slot as None.
    """

    # Current contribution3 comparison isolates the prs_model_evaluator
    # skill value over no_all_tools: all evidence tools default off; the
    # production augmentation over no_all_tools is the prs_model_evaluator
    # skill as context-only guidance at PGS_TRIAGE / PICK.
    #
    # `enable_skill` (the cross_trait_domain_knowledge KB) is ARCHIVED
    # for production use because paired80 measured zero lift over the
    # `no_all_tools` baseline (skill_only top_0.5%=0.325 == no_all_tools
    # top_0.5%=0.325; mean_rank, mean_gpr, hit_at_k all bit-identical).
    # The default value remains True ONLY for historical reproducibility
    # of pre-archive batch runs; production ablation labels added after
    # the archive (see driver.py) explicitly set `enable_skill=False`.
    enable_h2: bool = False
    enable_ot: bool = False             # gates `get_open_targets_overlap` in Gather (LLM-callable)
    enable_gc_batch: bool = False       # gates Stage 3.5 `genetic_correlation_batch_estimator`
    enable_ot_late_batch: bool = False  # harness OT audit after Pick candidate set is known
    enable_biology: bool = False        # gates Scout-time `biology_retrieve_related_bundles` (only entry)
    enable_skill: bool = True           # ARCHIVED: cross_trait_domain_knowledge KB (paired80 zero lift); default kept True for legacy reproducibility only
    enable_skill_reference_lane: bool = False
    enable_pgs_quality_skill: bool = False  # gates prs_model_evaluator skill at PGS_TRIAGE/PICK (production active)
    enable_pgs_quality_prompt_block: bool = False  # explicit system-prompt declaration; iter12 regressed, default off
    enable_pgs_quality_reference_lane: bool = False  # independent iter11-style no-evidence reference for final LLM arbitration
    enable_h2_global_primary_context: bool = False  # expose h2 records to cross-bundle GP, not upstream selection

    def disabled_tools(self) -> list[str]:
        out: list[str] = []
        if not self.enable_h2:
            out.append("get_heritability")
        if not (self.enable_ot or self.enable_ot_late_batch):
            out.append("get_open_targets_overlap")
        if not self.enable_gc_batch:
            out.append("genetic_correlation_batch_estimator")
        if not self.enable_biology:
            out.append("biology")
        if not self.enable_skill:
            out.append("cross_trait_domain_knowledge")
        if not self.enable_pgs_quality_skill:
            out.append("prs_model_evaluator_skill")
        if not self.enable_pgs_quality_reference_lane:
            out.append("pgs_quality_reference_lane")
        if self.enable_h2 and not self.enable_h2_global_primary_context:
            out.append("h2_global_primary_context")
        return out


# ---------------------------------------------------------------------------
# Public entry point — old-compatible signature preserved
# ---------------------------------------------------------------------------

def run_transfer_agent(
    dossier: CandidateBundleDossier,
    *,
    max_tool_calls: int = 40,
    stale_rounds: int = 1,
    max_gather_rounds: int = 8,
    model_frontier_budget_per_bundle: int = 8,
    enable_critic: bool = True,
    stop_after: Optional[str] = None,
    benchmark_family: str = "unified",
    tool_ablation: Optional[ToolAblationConfig] = None,
    skill_reference_override: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Run the full five-stage LLM-led transfer agent for one target.

    Returns a dict with `target`, `decision`, and `trace` keys.
    `decision.outcome` is either "MATCHED" (frontier produced) or
    "ABSTAINED" (no valid frontier survived harness hygiene).
    """
    target = dossier.target
    bundle_lookup: dict[str, TraitBundle] = {b.bundle_id: b for b in dossier.candidates}
    known_ids = set(bundle_lookup.keys())

    cfg = tool_ablation or ToolAblationConfig()

    registry = EvidenceRegistry(stale_rounds=stale_rounds)
    budget = BudgetGuard(max_tool_calls=max_tool_calls)
    trace = AgentTrace(target_id=target.target_id, target_label=target.target_label)
    trace.tool_ablation_config = {
        "enable_h2": cfg.enable_h2,
        "enable_ot": cfg.enable_ot,
        "enable_gc_batch": cfg.enable_gc_batch,
        "enable_ot_late_batch": cfg.enable_ot_late_batch,
        "enable_biology": cfg.enable_biology,
        "enable_skill": cfg.enable_skill,
        "enable_skill_reference_lane": cfg.enable_skill_reference_lane,
        "enable_pgs_quality_skill": cfg.enable_pgs_quality_skill,
        "enable_pgs_quality_prompt_block": cfg.enable_pgs_quality_prompt_block,
        "enable_pgs_quality_reference_lane": cfg.enable_pgs_quality_reference_lane,
        "enable_h2_global_primary_context": cfg.enable_h2_global_primary_context,
        "disabled_tools": cfg.disabled_tools(),
    }

    skill_reference: Optional[dict[str, Any]] = None
    if cfg.enable_skill_reference_lane and stop_after != "bundle_posterior":
        if skill_reference_override:
            skill_reference = _normalize_skill_reference(
                skill_reference_override,
                dossier=dossier,
            )
        else:
            skill_reference = _run_skill_reference_lane(
                dossier=dossier,
                cfg=cfg,
                max_tool_calls=max_tool_calls,
                stale_rounds=stale_rounds,
                max_gather_rounds=max_gather_rounds,
                model_frontier_budget_per_bundle=model_frontier_budget_per_bundle,
                enable_critic=enable_critic,
                benchmark_family=benchmark_family,
            )
        trace.skill_reference_json = skill_reference
    elif cfg.enable_pgs_quality_reference_lane and stop_after != "bundle_posterior":
        skill_reference = _run_pgs_quality_reference_lane(
            dossier=dossier,
            max_tool_calls=max_tool_calls,
            stale_rounds=stale_rounds,
            max_gather_rounds=max_gather_rounds,
            model_frontier_budget_per_bundle=model_frontier_budget_per_bundle,
            enable_critic=enable_critic,
            benchmark_family=benchmark_family,
        )
        trace.skill_reference_json = skill_reference

    # Pre-populate registry with bundle metadata (not a tool call — hygiene).
    for bundle in dossier.candidates:
        registry.set_bundle_meta(
            bundle_id=bundle.bundle_id,
            canonical_label=bundle.canonical_label,
            aliases=list(bundle.aliases or []),
            n_models=int(bundle.n_models or 0),
            efo_ids=list(bundle.source_efo_ids or []),
            mondo_ids=list(bundle.source_mondo_ids or []),
        )

    # ------------------------------------------------------------------
    # Stage 1 — SCOUT
    # ------------------------------------------------------------------
    scout_out = _run_scout(
        target=target,
        bundle_lookup=bundle_lookup,
        trace=trace,
        cfg=cfg,
    )
    probe_ids, dropped = filter_known_bundle_ids(scout_out.probe_bundle_ids, known_ids)
    for d in dropped:
        trace.provenance.tag(
            field_path=f"scout.probe_bundle_ids[{d}]",
            value=d,
            source="harness:drop_invalid_id",
            detail="scout_suggested_unknown_bundle_id",
        )
    trace.scout_directive_json = {
        "probe_bundle_ids": probe_ids,
        "used_biology_retrieval": scout_out.used_biology_retrieval,
        "rationale": scout_out.rationale,
        "dropped_invalid_ids": dropped,
    }
    if skill_reference:
        ref_bundle_id = skill_reference.get("reference_bundle_id")
        if ref_bundle_id in known_ids and ref_bundle_id not in probe_ids:
            probe_ids.append(ref_bundle_id)
            trace.scout_directive_json["probe_bundle_ids"] = probe_ids
            trace.provenance.tag(
                field_path=f"scout.probe_bundle_ids[{ref_bundle_id}]",
                value=ref_bundle_id,
                source="harness:skill_reference_lane",
                detail="no-skill reference source exposed for skill-guided comparison",
            )
    for bid in probe_ids:
        trace.provenance.tag(
            field_path=f"scout.probe_bundle_ids[{bid}]",
            value=bid,
            source="llm:stage_1",
        )

    # ------------------------------------------------------------------
    # Stage 2 — GATHER (ReAct loop)
    # ------------------------------------------------------------------
    dispatcher = _build_tool_dispatcher(
        target=target,
        bundle_lookup=bundle_lookup,
        registry=registry,
        budget=budget,
        cfg=cfg,
    )
    _run_gather(
        target=target,
        probe_ids=probe_ids,
        bundle_lookup=bundle_lookup,
        registry=registry,
        dispatcher=dispatcher,
        budget=budget,
        max_rounds=max_gather_rounds,
        trace=trace,
        cfg=cfg,
    )

    # ------------------------------------------------------------------
    # Stage 2.5 — h2 batch (harness-orchestrated, fast local lookups)
    # Populates EvidenceRegistry h2 fields early, but the prompt configs
    # hide h2 from Gather/Judge/Pick/Global Primary. The final Critic can
    # consume h2 as one orthogonal verification axis.
    # ------------------------------------------------------------------
    if cfg.enable_h2:
        _run_h2_batch(
            target=target,
            registry=registry,
            probe_ids=probe_ids,
            bundle_lookup=bundle_lookup,
            trace=trace,
        )

    # ------------------------------------------------------------------
    # Stage 3 — JUDGE
    # (GC batch is at Stage 3.5, AFTER Judge — see v15 architectural
    # change. Judge ranks bundles using OT/h2/notes; the rg axis
    # informs the downstream argmax stages (Pick / Global Primary /
    # Critic) where it disambiguates candidates of similar raw quality.)
    # ------------------------------------------------------------------
    judge_out = _run_judge(
        target=target,
        registry=registry,
        budget=budget,
        trace=trace,
        cfg=cfg,
    )
    judge_bundle_ids = [rb.bundle_id for rb in judge_out.ranked_bundles]
    kept_ranked, judge_dropped = filter_known_bundle_ids(judge_bundle_ids, known_ids)
    for d in judge_dropped:
        trace.provenance.tag(
            field_path=f"judge.ranked_bundles[{d}]",
            value=d,
            source="harness:drop_invalid_id",
            detail="judge_returned_unknown_bundle_id",
        )
    kept_ranked_objs = [rb for rb in judge_out.ranked_bundles if rb.bundle_id in kept_ranked]
    trace.judge_output_json = {
        "ranked_bundles": [rb.model_dump() for rb in kept_ranked_objs],
        "k_chosen_for_picker": judge_out.k_chosen_for_picker,
        "rationale": judge_out.rationale,
        "dropped_invalid_ids": judge_dropped,
    }
    for rb in kept_ranked_objs:
        trace.provenance.tag(
            field_path=f"judge.ranked_bundles[{rb.bundle_id}]",
            value=rb.bundle_id,
            source="llm:stage_3",
        )

    if stop_after == "bundle_posterior" or not kept_ranked_objs:
        return _assemble_output(
            dossier=dossier,
            trace=trace,
            bundle_ranking=judge_out,
            kept_ranked_objs=kept_ranked_objs,
            model_frontier=None,
            critic=None,
            stop_after=stop_after,
        )

    # ------------------------------------------------------------------
    # Stage 4 — PICK (per top-K bundle)
    # ------------------------------------------------------------------
    # P8a: Judge's k_chosen_for_picker decides how many supporting
    # bundles Pick hydrates. P17: also inject up to BREADTH_FLOOR
    # high-n_models bundles from the probe pool as "fallback" supporting
    # bundles if Judge didn't already include them. This is a breadth
    # safety net (not a re-ranking): well-powered generalist GWAS
    # bundles are frequent empirical cross-trait sources whose PGSs
    # often dominate AoU AUC even when Judge's lexical / OT signal
    # ranks more specific bundles higher. Pick + Reconciliation
    # remain the LLM-led decision layer.
    PICK_MIN_JUDGE_BUNDLES = 6
    PICK_MAX_JUDGE_BUNDLES = 8
    k_preferred = max(1, int(judge_out.k_chosen_for_picker or 1))
    k = min(max(k_preferred, PICK_MIN_JUDGE_BUNDLES), len(kept_ranked_objs), PICK_MAX_JUDGE_BUNDLES)
    top_k_bundles = list(kept_ranked_objs[:k])
    # Inject up to BREADTH_FLOOR additional probe-pool bundles that
    # (a) Gather actually queried OT for AND got >0 shared_targets with
    # the target (so we know they have real biological overlap), and
    # (b) are large generalist bundles by n_models. This protects
    # Pick + Reconciliation from missing high-quality cross-trait
    # transfer sources when Judge ranks more specific bundles higher.
    # The relevance filter avoids injecting unrelated huge bundles
    # (e.g., neuroimaging into a dermatology target) which would
    # waste LLM tokens and PGS Catalog API budget.
    BREADTH_FLOOR = 3
    BREADTH_MIN_N_MODELS = 30
    already_in_topk = {rb.bundle_id for rb in top_k_bundles}

    def _has_ot_overlap(bid: str) -> int:
        ev = registry.get(bid)
        if ev is None or not ev.ot:
            return 0
        return int((ev.ot or {}).get("shared_target_count_total") or len((ev.ot or {}).get("shared_targets") or []))

    probed_breadth_candidates = [
        bundle_lookup[bid]
        for bid in probe_ids
        if (
            bid in bundle_lookup
            and bid not in already_in_topk
            and int(bundle_lookup[bid].n_models or 0) >= BREADTH_MIN_N_MODELS
            and _has_ot_overlap(bid) > 0
        )
    ]
    probed_breadth_candidates.sort(
        key=lambda b: (-int(b.n_models or 0), -_has_ot_overlap(b.bundle_id), b.bundle_id),
    )
    next_rank = (top_k_bundles[-1].rank + 1) if top_k_bundles else 1
    from experiments.contribution3.transfer.schemas import RankedBundle
    for bundle in probed_breadth_candidates[:BREADTH_FLOOR]:
        top_k_bundles.append(
            RankedBundle(
                bundle_id=bundle.bundle_id,
                rank=next_rank,
                confidence="Low",
                rationale=f"harness:breadth_floor — n_models={bundle.n_models}, ot_shared={_has_ot_overlap(bundle.bundle_id)}; injected to broaden Pick exposure.",
                evidence_cited=[],
            )
        )
        trace.provenance.tag(
            field_path=f"judge.ranked_bundles[{bundle.bundle_id}]",
            value=bundle.bundle_id,
            source="harness:breadth_floor",
            detail=f"n_models={bundle.n_models}",
        )
        next_rank += 1

    # Complement the high-n breadth floor with a small mechanism floor:
    # some highly target-relevant bundles have few PGSs, so they are not
    # captured by n_models-based breadth protection. If Gather found
    # strong OT overlap, expose a couple of those bundles to Pick and let
    # the LLM decide. This is candidate exposure, not a deterministic
    # ranking rule.
    MECHANISM_FLOOR = 0
    MECHANISM_MIN_OT_SHARED = 5
    already_in_topk = {rb.bundle_id for rb in top_k_bundles}
    probed_mechanism_candidates = [
        bundle_lookup[bid]
        for bid in probe_ids
        if (
            bid in bundle_lookup
            and bid not in already_in_topk
            and (bundle_lookup[bid].candidate_pgs_ids or [])
            and _has_ot_overlap(bid) >= MECHANISM_MIN_OT_SHARED
        )
    ]
    probed_mechanism_candidates.sort(
        key=lambda b: (-_has_ot_overlap(b.bundle_id), -int(b.n_models or 0), b.bundle_id),
    )
    for bundle in probed_mechanism_candidates[:MECHANISM_FLOOR]:
        top_k_bundles.append(
            RankedBundle(
                bundle_id=bundle.bundle_id,
                rank=next_rank,
                confidence="Moderate",
                rationale=f"harness:mechanism_floor — ot_shared={_has_ot_overlap(bundle.bundle_id)}; injected to preserve a strong low-n_models mechanism candidate for Pick exposure.",
                evidence_cited=[],
            )
        )
        trace.provenance.tag(
            field_path=f"judge.ranked_bundles[{bundle.bundle_id}]",
            value=bundle.bundle_id,
            source="harness:breadth_floor:mechanism",
            detail=f"ot_shared={_has_ot_overlap(bundle.bundle_id)}",
        )
        next_rank += 1

    # Optional late OT audit: fetch raw Open Targets overlap only for the
    # bundle set already selected for Pick. This keeps OT from reshaping the
    # upstream candidate pool while still giving Critic an orthogonal evidence
    # axis for cross-bundle contradictions.
    if cfg.enable_ot_late_batch and not cfg.enable_ot:
        _run_ot_late_batch(
            target=target,
            registry=registry,
            top_k_bundle_ids=[rb.bundle_id for rb in top_k_bundles],
            bundle_lookup=bundle_lookup,
            trace=trace,
        )

    reference_pgs_by_bundle: dict[str, str] = {}
    if skill_reference:
        ref_bundle_id = str(skill_reference.get("reference_bundle_id") or "")
        ref_pgs_id = str(skill_reference.get("reference_primary_pgs_id") or "")
        if ref_bundle_id in bundle_lookup and ref_pgs_id:
            reference_pgs_by_bundle[ref_bundle_id] = ref_pgs_id
            if ref_bundle_id not in {rb.bundle_id for rb in top_k_bundles}:
                top_k_bundles.append(
                    RankedBundle(
                        bundle_id=ref_bundle_id,
                        rank=next_rank,
                        confidence="Moderate",
                        rationale=(
                            "harness:skill_reference_lane — source bundle from an "
                            "independent no-skill LLM pass; exposed so the final "
                            "LLM can compare it with skill-guided evidence."
                        ),
                        evidence_cited=[],
                    )
                )
                trace.provenance.tag(
                    field_path=f"judge.ranked_bundles[{ref_bundle_id}]",
                    value=ref_bundle_id,
                    source="harness:skill_reference_lane",
                    detail="skill-only reference bundle exposed to Pick",
                )
                next_rank += 1

    # ------------------------------------------------------------------
    # Stage 3.5 — Batch genetic-correlation augmentation
    # Position: AFTER Judge has ranked bundles AND after breadth-floor
    # augmentation; BEFORE Pick hydrates per-bundle PGS records.
    #
    # Shortlist: Judge's top-K bundle IDs (typically 5-8 plus 0-3 breadth
    # bundles). Reasoning: (1) Judge picks the candidates that matter, so
    # we only spend rg estimation on the bundles Pick will actually
    # hydrate; (2) keeping rg out of Judge's input prevents Judge from
            # over-promoting broad upstream bundles whose
    # polygenic-spillover rg satisfies any "strong-rg" rule (verified
    # failure mode in v13/v14 ablations); (3) the rg signal is most
    # useful for argmax decisions (Pick's per-bundle primary, Global
    # Primary's cross-bundle reconciliation, Critic's verification axis)
    # where bundles of comparable raw quality need disambiguation.
    #
    # Selective trigger: when Judge's top-K consists entirely of
    # same-trait bundles (label exact match), there is nothing for rg
    # to disambiguate — skip the batch call.
    # ------------------------------------------------------------------
    if ENABLE_GC_BATCH and cfg.enable_gc_batch:
        _run_gc_batch(
            target=target,
            registry=registry,
            top_k_bundle_ids=[rb.bundle_id for rb in top_k_bundles],
            bundle_lookup=bundle_lookup,
            trace=trace,
        )

    model_frontier = _run_pick(
        target=target,
        top_k_bundles=top_k_bundles,
        bundle_lookup=bundle_lookup,
        registry=registry,
        budget=budget,
        frontier_budget_per_bundle=model_frontier_budget_per_bundle,
        trace=trace,
        cfg=cfg,
        reference_pgs_by_bundle=reference_pgs_by_bundle,
    )
    if skill_reference is not None:
        model_frontier = _include_skill_reference_candidate(
            model_frontier=model_frontier,
            skill_reference=skill_reference,
            bundle_lookup=bundle_lookup,
            registry=registry,
            trace=trace,
        )

    # Stage 4.5 — GLOBAL PRIMARY RECONCILIATION
    # Per-bundle Pick can miss the best cross-bundle primary because each
    # Pick call sees only one bundle. Cross-bundle reconciliation gives
    # the LLM one last look at all per-bundle picks side-by-side before
    # committing to a primary.
    # Still LLM-led (no weights / no tiers) — it simply reorders the
    # candidate set the picker already produced.
    if model_frontier is not None and len(top_k_bundles) > 1:
        judge_ranks = {rb.bundle_id: rb.rank for rb in top_k_bundles}
        model_frontier = _run_global_primary_reconciliation(
            target=target,
            model_frontier=model_frontier,
            bundle_lookup=bundle_lookup,
            registry=registry,
            judge_ranks=judge_ranks,
            trace=trace,
            cfg=cfg,
            skill_reference=skill_reference,
        )

    # ------------------------------------------------------------------
    # Stage 5 — CRITIC
    # ------------------------------------------------------------------
    critic_out: Optional[CritiqueDecision] = None
    if enable_critic and model_frontier is not None:
        critic_out = _run_critic(
            target=target,
            registry=registry,
            proposed_frontier=model_frontier,
            trace=trace,
            cfg=cfg,
            skill_reference=skill_reference,
        )

    return _assemble_output(
        dossier=dossier,
        trace=trace,
        bundle_ranking=judge_out,
        kept_ranked_objs=kept_ranked_objs,
        model_frontier=model_frontier,
        critic=critic_out,
        stop_after=stop_after,
    )


# ---------------------------------------------------------------------------
# Stage 1 — SCOUT
# ---------------------------------------------------------------------------

def _run_scout(
    *,
    target,
    bundle_lookup: dict[str, TraitBundle],
    trace: AgentTrace,
    cfg: Optional["ToolAblationConfig"] = None,
) -> ScoutDirective:
    """Stage 1 Scout — LLM picks probe bundles from the universe.

    May flag `invoke_biology_retrieval=True`; if so the harness makes a
    second LLM call (`biology_retrieve_related_bundles`) and unions its
    output with `probe_bundle_ids`. The helper only ADDS candidates.
    """
    cfg = cfg or ToolAblationConfig()
    prompt_cfg = replace(cfg, enable_h2=False, enable_gc_batch=False)
    universe = [
        {
            "bundle_id": b.bundle_id,
            "canonical_label": b.canonical_label,
            "aliases": list(b.aliases or [])[:3],
            "n_models": int(b.n_models or 0),
        }
        for b in bundle_lookup.values()
    ]
    _scout_dk = cross_trait_domain_knowledge(
        stage="scout",
        query=(
            f"target_trait: {target.target_label}; "
            f"aliases: {','.join(list(target.aliases or [])[:6])}"
        ),
        cfg=prompt_cfg,
    )
    context: dict[str, Any] = {
        "target_label": target.target_label,
        "target_aliases": list(target.aliases or []),
        "target_code": getattr(target, "target_code", None),
        "bundle_universe_size": len(universe),
        "bundle_universe": universe,
    }
    if prompt_cfg.enable_skill:
        context["cross_trait_guidance"] = _scout_dk.primary_section
    try:
        directive: ScoutDirective = scout_chain(prompt_cfg).invoke(
            {"context_json": json.dumps(context, ensure_ascii=False, default=str)}
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Scout LLM call failed: %s — returning all universe IDs", exc)
        return ScoutDirective(
            probe_bundle_ids=list(bundle_lookup.keys()),
            invoke_biology_retrieval=False,
            biology_retrieval_reason="",
            used_biology_retrieval=False,
            rationale=f"scout_llm_error:{exc}; full-universe fallback (non-ranking)",
        )

    # Biology retrieval augmentation — ADDITIVE only.
    # Gated by per-run cfg.enable_biology AND module-level ENABLE_BIOLOGY_HELPER.
    if ENABLE_BIOLOGY_HELPER and cfg.enable_biology and directive.invoke_biology_retrieval:
        result = biology_retrieve_related_bundles(
            target_label=target.target_label,
            target_aliases=list(target.aliases or []),
            bundle_universe=universe,
            reason=directive.biology_retrieval_reason or "",
        )
        trace.increment_tool_call("biology_retrieve_related_bundles")
        # Persist the typed tool output to the trace for audit / ablation.
        trace.scout_biology_json = result.model_dump()
        # Filter to known bundle_ids and merge additively into the probe pool.
        helper_ids = [
            s.bundle_id for s in result.suggestions if s.bundle_id in bundle_lookup
        ]
        merged = list(directive.probe_bundle_ids)
        seen = set(merged)
        for hid in helper_ids:
            if hid not in seen:
                merged.append(hid)
                seen.add(hid)
        directive.probe_bundle_ids = merged
        # `used_biology_retrieval` reflects whether the tool actually ran;
        # success is independent of whether the LLM emitted any kept IDs.
        directive.used_biology_retrieval = result.skipped_reason is None
    else:
        directive.used_biology_retrieval = False
        trace.scout_biology_json = None

    return directive


# ---------------------------------------------------------------------------
# Stage 2 — GATHER
# ---------------------------------------------------------------------------

def _build_tool_dispatcher(
    *,
    target,
    bundle_lookup: dict[str, TraitBundle],
    registry: EvidenceRegistry,
    budget: BudgetGuard,
    cfg: Optional[ToolAblationConfig] = None,
) -> ToolDispatcher:
    cfg = cfg or ToolAblationConfig()
    dispatcher = ToolDispatcher(
        bundle_universe={bid: b for bid, b in bundle_lookup.items()},
        target_label=target.target_label,
        target_aliases=list(target.aliases or []),
        registry=registry,
        budget=budget,
    )

    def _resolve_bundle(bundle_id: str | None, candidate_label: str | None):
        """Tolerate LLM calls that provided either bundle_id or the
        candidate label. Hygiene only — no ranking, no substitution
        beyond exact-label lookup.
        """
        if bundle_id and bundle_id in bundle_lookup:
            return bundle_lookup[bundle_id]
        if candidate_label:
            needle = candidate_label.strip().lower()
            for b in bundle_lookup.values():
                if (b.canonical_label or "").strip().lower() == needle:
                    return b
                for a in b.aliases or []:
                    if (a or "").strip().lower() == needle:
                        return b
        return None

    def _tool_ot(
        bundle_id: str | None = None,
        candidate_label: str | None = None,
        target_label: str | None = None,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        bundle = _resolve_bundle(bundle_id, candidate_label)
        if bundle is None:
            return {"error": "unknown_bundle_id_or_candidate_label"}
        target_query = target_label or "; ".join(
            [str(x) for x in [target.target_label, *list(target.aliases or [])[:8]] if x]
        )
        candidate_query = "; ".join(
            [str(x) for x in [bundle.canonical_label, *list(bundle.aliases or [])[:8]] if x]
        )
        return get_open_targets_overlap(
            target_label_or_efo=target_query,
            candidate_label_or_efo=candidate_query,
        )

    if cfg.enable_ot:
        dispatcher.register("get_open_targets_overlap", _tool_ot)
    return dispatcher


# ---------------------------------------------------------------------------
# Stage 2.5 — Batch h2 augmentation (harness-orchestrated)
# ---------------------------------------------------------------------------


def _run_h2_batch(
    *,
    target,
    registry: EvidenceRegistry,
    probe_ids: list[str],
    bundle_lookup: dict[str, TraitBundle],
    trace: AgentTrace,
    ancestry: str = "EUR",
    max_calls: int = 50,
) -> None:
    """Stage 2.5 — Pre-fetch heritability for target + each probe bundle.

    Mirrors the GC-batch architecture: harness fetches deterministically,
    writes to EvidenceRegistry, and Global Primary / Critic consume
    `h2_target / h2_candidate` from the digest. The LLM never calls h2
    directly.

    Cost is per-target: 1 GWAS-Atlas-aggregator lookup for the target
    label + 1 per probe bundle (capped at `max_calls`). Each lookup is a
    local-file aggregator call (sub-100ms after warm-up), not an LLM
    call, so wall-time overhead is negligible.

    No same-trait skip: identical-label probe bundles still have h2
    populated for symmetry in the late reconciliation stages.
    """
    payload: dict[str, Any] = {
        "target_label": target.target_label,
        "ancestry": ancestry,
        "n_probes": len(probe_ids),
        "n_called": 0,
        "n_with_records": 0,
        "skipped_reason": None,
        "max_calls": max_calls,
    }

    if not probe_ids:
        payload["skipped_reason"] = "no_probes"
        trace.h2_batch_json = payload
        return

    target_h2 = get_heritability(trait_label=target.target_label, ancestry=ancestry)
    trace.increment_tool_call("get_heritability")
    payload["n_called"] += 1
    target_h2_clean = [r for r in (target_h2 or []) if not (isinstance(r, dict) and r.get("error"))]
    payload["n_target_records"] = len(target_h2_clean)

    for bid in probe_ids[:max_calls]:
        bundle = bundle_lookup.get(bid)
        if bundle is None:
            continue
        label = (bundle.canonical_label or "").strip()
        if not label:
            continue
        candidate_h2 = get_heritability(trait_label=label, ancestry=ancestry)
        trace.increment_tool_call("get_heritability")
        payload["n_called"] += 1
        candidate_h2_clean = [r for r in (candidate_h2 or []) if not (isinstance(r, dict) and r.get("error"))]
        if candidate_h2_clean:
            payload["n_with_records"] += 1
        registry.set_h2(
            bundle_id=bid,
            source_h2=target_h2_clean if target_h2_clean else None,
            candidate_h2=candidate_h2_clean if candidate_h2_clean else None,
            round_idx=99,
        )

    trace.h2_batch_json = payload


# ---------------------------------------------------------------------------
# Stage 3.25 — Late Open Targets audit augmentation
# ---------------------------------------------------------------------------


def _run_ot_late_batch(
    *,
    target,
    registry: EvidenceRegistry,
    top_k_bundle_ids: list[str],
    bundle_lookup: dict[str, TraitBundle],
    trace: AgentTrace,
    max_calls: int = 12,
) -> None:
    """Fetch Open Targets overlap for the bundles already exposed to Pick.

    This is intentionally later and narrower than the LLM-callable Gather
    path. It does not alter Scout, Gather, Judge, Pick, or Global Primary;
    it only makes raw OT overlap available to the final Critic audit.
    """
    payload: dict[str, Any] = {
        "target_label": target.target_label,
        "n_topk": len(top_k_bundle_ids),
        "n_called": 0,
        "n_with_shared_targets": 0,
        "skipped_reason": None,
        "max_calls": max_calls,
    }
    if not top_k_bundle_ids:
        payload["skipped_reason"] = "no_topk"
        trace.ot_late_batch_json = payload
        return

    target_query = "; ".join(
        [str(x) for x in [target.target_label, *list(target.aliases or [])[:8]] if x]
    )
    seen: set[str] = set()
    for bid in top_k_bundle_ids:
        if payload["n_called"] >= max_calls:
            break
        if bid in seen:
            continue
        seen.add(bid)
        bundle = bundle_lookup.get(bid)
        if bundle is None:
            continue
        ev = registry.get(bid)
        if ev is not None and ev.ot is not None:
            continue
        candidate_query = "; ".join(
            [str(x) for x in [bundle.canonical_label, *list(bundle.aliases or [])[:8]] if x]
        )
        if not candidate_query:
            continue
        result = get_open_targets_overlap(
            target_label_or_efo=target_query,
            candidate_label_or_efo=candidate_query,
        )
        trace.increment_tool_call("get_open_targets_overlap")
        payload["n_called"] += 1
        if int((result or {}).get("shared_target_count_total") or len((result or {}).get("shared_targets") or [])) > 0:
            payload["n_with_shared_targets"] += 1
        registry.set_ot(bundle_id=bid, payload=result, round_idx=99)

    trace.ot_late_batch_json = payload


# ---------------------------------------------------------------------------
# Stage 3.5 — Batch GC augmentation
# ---------------------------------------------------------------------------


def _is_same_trait_label(target_label: str, candidate_label: str) -> bool:
    """Cheap same-trait heuristic for skipping GC. Compares case-folded
    canonical labels; aliases are not considered (intentionally narrow —
    near-same-trait labels still get rg estimated)."""
    if not target_label or not candidate_label:
        return False
    return target_label.strip().lower() == candidate_label.strip().lower()


def _run_gc_batch(
    *,
    target,
    registry: EvidenceRegistry,
    top_k_bundle_ids: list[str],
    bundle_lookup: dict[str, TraitBundle],
    trace: AgentTrace,
) -> None:
    """Augment EvidenceRegistry.gc with batch-estimated rg for the
    cross-trait subset of Judge's top-K bundle list.

    Position contract: this is called AFTER `_run_judge` has ranked the
    probe pool AND after the breadth-floor augmentation step has
    appended fallback high-`n_models` bundles to `top_k_bundles`. The
    candidate list is therefore exactly the bundles Pick will hydrate
    — no priority heuristic, no risk that Judge's bundle ranking gets
    contaminated by rg signal.

    Filtering: same-trait bundles (label exact match) are skipped
    because their rg ≈ 1.0 by construction is uninformative; bundles
    whose `gc` slot is already populated are skipped (defensive).

    Writes per-bundle GC payload via `registry.set_gc(...)`. Pick reads
    these via `bundle_evidence.gc`; Critic reads them via the abs_rg
    axis of `_build_per_axis_top3`.
    """
    n_topk = len(top_k_bundle_ids)
    n_same_trait = 0
    candidates: list[dict[str, Any]] = []
    for bid in top_k_bundle_ids:
        bundle = bundle_lookup.get(bid)
        if bundle is None:
            continue
        label = bundle.canonical_label or ""
        if not label:
            continue
        if _is_same_trait_label(target.target_label, label):
            n_same_trait += 1
            continue
        ev = registry.get(bid)
        if ev is not None and ev.gc is not None:
            continue  # already populated
        candidates.append({"bundle_id": bid, "candidate_label": label})

    if not candidates:
        trace.gc_batch_json = {
            "target_label": target.target_label,
            "estimates": [],
            "n_topk": n_topk,
            "n_same_trait_skipped": n_same_trait,
            "n_candidates_total": 0,
            "n_estimated": 0,
            "skipped_reason": "no_cross_trait_in_judge_topk",
        }
        return

    result = genetic_correlation_batch_estimator(
        target_label=target.target_label,
        target_aliases=list(target.aliases or []),
        candidates=candidates,
    )
    trace.increment_tool_call("genetic_correlation_batch_estimator")
    payload = result.model_dump()
    payload["n_topk"] = n_topk
    payload["n_same_trait_skipped"] = n_same_trait
    trace.gc_batch_json = payload

    if result.skipped_reason:
        logger.warning(
            "GC batch returned no estimates for %s: %s",
            target.target_label,
            result.skipped_reason,
        )
        return

    for est in result.estimates:
        registry.set_gc(
            bundle_id=est.bundle_id,
            payload=est.as_registry_payload(),
            round_idx=99,
        )


def _run_gather(
    *,
    target,
    probe_ids: list[str],
    bundle_lookup: dict[str, TraitBundle],
    registry: EvidenceRegistry,
    dispatcher: ToolDispatcher,
    budget: BudgetGuard,
    max_rounds: int,
    trace: AgentTrace,
    cfg: Optional["ToolAblationConfig"] = None,
) -> None:
    """Stage 2 Gather — ReAct loop; LLM emits RoundDirective each round.

    Halts on (in order):
      - done=True from LLM -> halt_reason = "llm_terminated"
      - budget exhausted -> halt_reason = "budget_exhausted_before_done"
      - max_rounds reached without done -> halt_reason = "budget_exhausted_before_done"
    """
    cfg = cfg or ToolAblationConfig()
    prompt_cfg = replace(cfg, enable_h2=False, enable_gc_batch=False)
    if not probe_ids or budget.max_tool_calls <= 0:
        trace.gather_halt_reason = "not_applicable"
        trace.gather_tool_calls_consumed = 0
        return

    halt = False
    for round_idx in range(max_rounds):
        if not budget.can_spend(1):
            trace.gather_halt_reason = "budget_exhausted_before_done"
            break

        context = _build_gather_context(
            target=target,
            probe_ids=probe_ids,
            registry=registry,
            budget=budget,
            round_idx=round_idx,
            cfg=prompt_cfg,
        )
        try:
            directive: RoundDirective = gather_chain(prompt_cfg).invoke(
                {"context_json": json.dumps(context, ensure_ascii=False, default=str)}
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gather LLM call round %d failed: %s", round_idx, exc)
            # Per plan §12.1 — no deterministic fallback. Record the round
            # and halt; the Judge will see what evidence has been gathered.
            trace.gather_rounds.append(
                RoundState(
                    round_idx=round_idx,
                    directive_json={"error": f"llm_error:{exc}"},
                    tool_calls_executed=[],
                )
            )
            trace.gather_halt_reason = "budget_exhausted_before_done"
            break

        # Register LLM notes into the registry.
        for bundle_id, note in (directive.bundle_notes or {}).items():
            if bundle_id in bundle_lookup:
                registry.add_note(bundle_id=bundle_id, round_idx=round_idx, note=note)

        # Execute tool calls in order.
        tool_results: list[dict[str, Any]] = []
        for tc in directive.tool_calls:
            if not budget.can_spend(1):
                tool_results.append(
                    {"tool": tc.tool, "args": tc.args, "error": "budget_exhausted"}
                )
                break
            result = dispatcher.call(tc, round_idx=round_idx)
            tool_results.append(result)
            # Tool-level observability: count successful invocations only
            # (errors / budget_exhausted / unknown_tool do not count).
            if "error" not in result:
                trace.increment_tool_call(tc.tool)

        trace.gather_rounds.append(
            RoundState(
                round_idx=round_idx,
                directive_json=directive.model_dump(),
                tool_calls_executed=tool_results,
            )
        )

        # Sliding-window truncation of raw tool outputs from prompt history.
        registry.truncate_raw_after(round_idx)

        if directive.done:
            trace.gather_halt_reason = "llm_terminated"
            halt = True
            break
        if not budget.can_spend(1):
            trace.gather_halt_reason = "budget_exhausted_before_done"
            break
    else:
        trace.gather_halt_reason = "budget_exhausted_before_done"

    if halt is False and trace.gather_halt_reason == "not_applicable":
        trace.gather_halt_reason = "budget_exhausted_before_done"
    trace.gather_tool_calls_consumed = budget.consumed


def _build_gather_context(
    *,
    target,
    probe_ids: list[str],
    registry: EvidenceRegistry,
    budget: BudgetGuard,
    round_idx: int,
    cfg: Optional["ToolAblationConfig"] = None,
) -> dict[str, Any]:
    """Shape the per-round directive input for the Gather LLM."""
    cfg = cfg or ToolAblationConfig()
    # Per-bundle coverage summary keeps the prompt compact while
    # letting the LLM see which bundles still lack evidence. Only
    # the channels enabled by cfg are surfaced so the LLM cannot
    # form expectations about disabled channels.
    coverage: list[dict[str, Any]] = []
    for bid in probe_ids:
        ev = registry.get(bid)
        if ev is None:
            row = {
                "bundle_id": bid,
                "label": None,
                "note_rounds": [],
            }
            if cfg.enable_gc_batch:
                row["has_gc"] = False
            if cfg.enable_ot:
                row["has_ot"] = False
            if cfg.enable_h2:
                row["has_h2_source"] = False
                row["has_h2_candidate"] = False
            coverage.append(row)
            continue
        row = {
            "bundle_id": bid,
            "label": ev.canonical_label,
            "n_models": ev.n_models,
            "note_rounds": sorted(ev.notes.keys()),
        }
        if cfg.enable_gc_batch:
            row["has_gc"] = ev.gc is not None
        if cfg.enable_ot:
            row["has_ot"] = ev.ot is not None
        if cfg.enable_h2:
            row["has_h2_source"] = ev.h2_source is not None
            row["has_h2_candidate"] = ev.h2_candidate is not None
        coverage.append(row)
    _gather_dk = cross_trait_domain_knowledge(
        stage="gather",
        query=(
            f"target_trait: {target.target_label}; "
            f"aliases: {','.join(list(target.aliases or [])[:6])}"
        ),
        cfg=cfg,
    )
    out: dict[str, Any] = {
        "target": {
            "target_label": target.target_label,
            "target_aliases": list(target.aliases or []),
            "target_code": target.target_code,
        },
        "round_idx": round_idx,
        "remaining_tool_calls": budget.remaining,
        "probe_bundle_ids": probe_ids,
        "probe_coverage": coverage,
        "recent_raw_tool_outputs": registry.round_tool_outputs,
    }
    if cfg.enable_skill:
        out["cross_trait_guidance"] = _gather_dk.primary_section
    return out


# ---------------------------------------------------------------------------
# Stage 3 — JUDGE
# ---------------------------------------------------------------------------

def _run_judge(
    *,
    target,
    registry: EvidenceRegistry,
    budget: BudgetGuard,
    trace: AgentTrace,
    picker_budget_hint: int = 15,
    cfg: Optional["ToolAblationConfig"] = None,
) -> BundleRanking:
    """Stage 3 Judge — fresh LLM call consuming EvidenceRegistry digest.

    The Judge gets raw evidence (gc / h2 / ot / notes) per bundle and
    produces a ranking. No weights, no post-processing re-merge.
    """
    cfg = cfg or ToolAblationConfig()
    prompt_cfg = replace(cfg, enable_h2=False, enable_gc_batch=False)
    _judge_dk = cross_trait_domain_knowledge(
        stage="judge",
        query=(
            f"target_trait: {target.target_label}; "
            f"aliases: {','.join(list(target.aliases or [])[:6])}"
        ),
        cfg=prompt_cfg,
    )
    context: dict[str, Any] = {
        "target": {
            "target_id": target.target_id,
            "target_code": target.target_code,
            "target_label": target.target_label,
            "aliases": list(target.aliases or []),
            "target_type": getattr(target, "target_type", None),
        },
        "evidence_registry_digest": json.loads(registry.compress_for_prompt(cfg=prompt_cfg)),
        "budget_hint": picker_budget_hint,
    }
    if prompt_cfg.enable_skill:
        context["cross_trait_guidance"] = _judge_dk.primary_section
    try:
        result: BundleRanking = judge_chain(prompt_cfg).invoke(
            {"context_json": json.dumps(context, ensure_ascii=False, default=str)}
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Judge LLM call failed: %s", exc)
        # No deterministic fallback (per plan §12.1): return empty ranking
        # so the harness abstains rather than silently re-ranking.
        return BundleRanking(
            ranked_bundles=[],
            k_chosen_for_picker=1,
            rationale=f"judge_llm_error:{exc}",
        )
    return result


# ---------------------------------------------------------------------------
# Stage 4 — PICK
# ---------------------------------------------------------------------------

def _run_pick(
    *,
    target,
    top_k_bundles,
    bundle_lookup: dict[str, TraitBundle],
    registry: EvidenceRegistry,
    budget: BudgetGuard,
    frontier_budget_per_bundle: int,
    trace: AgentTrace,
    cfg: Optional["ToolAblationConfig"] = None,
    reference_pgs_by_bundle: Optional[dict[str, str]] = None,
) -> Optional[ModelFrontier]:
    """Stage 4 Pick — per top-K bundle, lazy `describe_pgs_model` + LLM rank.

    For each bundle in `top_k_bundles` (in Judge rank order), fetches up
    to `frontier_budget_per_bundle` PGS model records (lazily), then
    asks the LLM to rank/select among them. The union of all per-bundle
    picks forms the final model frontier, with the first bundle's primary
    pick as the global `primary_pgs_id`.

    No quality anchor, no ancestry-tier reordering.
    """
    cfg = cfg or ToolAblationConfig()
    prompt_cfg = replace(cfg, enable_h2=False, enable_gc_batch=False)
    reference_pgs_by_bundle = reference_pgs_by_bundle or {}
    if not top_k_bundles:
        return None

    aggregated_frontier: list = []
    primary_pgs_id: Optional[str] = None

    per_bundle_outputs: list[dict[str, Any]] = []
    # When a bundle has more than TRIAGE_THRESHOLD PGSs, first run a compact
    # triage LLM call that narrows the list before full describe+Pick. This
    # keeps the Pick prompt well-sized and avoids truncating long candidate
    # lists (where the oracle PGS is often buried at a high index).
    TRIAGE_THRESHOLD = 12
    FULL_HYDRATE_CAP = 18

    for ranked_bundle in top_k_bundles:
        bundle_id = ranked_bundle.bundle_id
        bundle = bundle_lookup.get(bundle_id)
        if bundle is None or not (bundle.candidate_pgs_ids or []):
            continue

        full_pgs_list = list(bundle.candidate_pgs_ids)
        if len(full_pgs_list) > TRIAGE_THRESHOLD:
            triage_candidates = [compact_pgs_summary(pid) for pid in full_pgs_list]
            triage_candidates = [c for c in triage_candidates if c.get("pgs_id")]
            _triage_dk = cross_trait_domain_knowledge(
                stage="pgs_triage",
                query=(
                    f"target_trait: {target.target_label}; "
                    f"supporting_bundle: {bundle.canonical_label}; "
                    f"transfer multi-ancestry validation"
                ),
                cfg=prompt_cfg,
            )
            _triage_pgs_skill = prs_model_evaluator_skill(stage="pgs_triage", cfg=prompt_cfg)
            triage_context: dict[str, Any] = {
                "target": {
                    "target_label": target.target_label,
                    "target_aliases": list(target.aliases or []),
                    "target_code": getattr(target, "target_code", None),
                },
                "supporting_bundle": {
                    "bundle_id": bundle.bundle_id,
                    "canonical_label": bundle.canonical_label,
                },
                "compact_summaries": triage_candidates,
                "max_selected": FULL_HYDRATE_CAP,
            }
            if prompt_cfg.enable_skill:
                triage_context["cross_trait_guidance"] = _triage_dk.primary_section
            if _triage_pgs_skill.enabled:
                # Advisory text from prs_model_evaluator skill at TRIAGE.
                #
                # Iter8 rationale: TRIAGE is the choke point that
                # determines which ~15 of N candidates downstream PICK
                # ever sees. If TRIAGE narrows to endpoint-fidelity-
                # specific labels alone, the surviving set loses method-
                # family / training-cohort / validation-breadth
                # diversity, which hurts the WHOLE pick-quality
                # distribution (top_0.5% through top_25%) — not just
                # oracle hit. SKILL.md procedural overview gives TRIAGE
                # a balanced consideration set so the surviving 15 span
                # the diversity that PICK needs to make a good choice
                # across every quality threshold.
                triage_context["pgs_quality_guidance"] = _triage_pgs_skill.primary_section
            try:
                triage = pgs_triage_chain(prompt_cfg).invoke(
                    {"context_json": json.dumps(triage_context, ensure_ascii=False, default=str)}
                )
                known_pgs = {c["pgs_id"] for c in triage_candidates if c.get("pgs_id")}
                triaged_pgs = [p for p in triage.selected_pgs_ids if p in known_pgs]
                if not triaged_pgs:
                    triaged_pgs = full_pgs_list[:FULL_HYDRATE_CAP]
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "PGS triage LLM call failed for bundle %s: %s — falling back to first %d PGSs",
                    bundle_id,
                    exc,
                    FULL_HYDRATE_CAP,
                )
                triaged_pgs = full_pgs_list[:FULL_HYDRATE_CAP]
        else:
            triaged_pgs = full_pgs_list

        reference_pgs_id = reference_pgs_by_bundle.get(bundle_id)
        if reference_pgs_id and reference_pgs_id in full_pgs_list and reference_pgs_id not in triaged_pgs:
            triaged_pgs = [reference_pgs_id] + triaged_pgs
            seen_triaged: set[str] = set()
            triaged_pgs = [
                pid for pid in triaged_pgs
                if not (pid in seen_triaged or seen_triaged.add(pid))
            ][:FULL_HYDRATE_CAP]

        # Full describe for the triaged subset.
        pgs_records: dict[str, Any] = {}
        for pgs_id in triaged_pgs:
            cached = registry.get(bundle_id)
            if cached is not None and pgs_id in cached.model_records:
                pgs_records[pgs_id] = cached.model_records[pgs_id]
                continue
            try:
                record = describe_pgs_model(pgs_id=pgs_id)
            except Exception as exc:  # noqa: BLE001
                logger.warning("describe_pgs_model(%s) failed: %s", pgs_id, exc)
                record = {"pgs_id": pgs_id, "error": f"describe_error:{exc}"}
            pgs_records[pgs_id] = record
            registry.set_model_record(
                bundle_id=bundle_id, pgs_id=pgs_id, record=record, round_idx=99
            )

        bundle_evidence = registry.get(bundle_id)
        # v16: Pick stage does NOT see `gc` — rg is bundle-level signal
        # appropriate for cross-bundle reconciliation (Global Primary)
        # and orthogonal-axis verification (Critic), not for within-bundle
        # PGS selection. Including it here in v15 added noise to the
        # frontier (verified on v15 80-target: in_frontier 21→19,
        # frontier_hit 53→52, top_2.5% −4 vs v11). Global Primary still
        # sees rg via `per_bundle_evidence`; Critic via per_axis_top3.
        evidence_dump: dict[str, Any] = {
            "notes": {str(k): v for k, v in (bundle_evidence.notes or {}).items()}
            if bundle_evidence
            else {},
        }
        if cfg.enable_ot:
            evidence_dump["ot"] = bundle_evidence.ot if bundle_evidence else None
        _pick_dk = cross_trait_domain_knowledge(
            stage="pick",
            query=(
                f"target_trait: {target.target_label}; "
                f"supporting_bundle: {bundle.canonical_label}; "
                f"transfer multi-ancestry validation"
            ),
            cfg=prompt_cfg,
        )
        _pick_pgs_skill = prs_model_evaluator_skill(stage="pick", cfg=prompt_cfg)
        context: dict[str, Any] = {
            "target": {
                "target_label": target.target_label,
                "target_aliases": list(target.aliases or []),
                "target_code": getattr(target, "target_code", None),
            },
            "supporting_bundle": {
                "bundle_id": bundle.bundle_id,
                "canonical_label": bundle.canonical_label,
                "aliases": list(bundle.aliases or [])[:4],
            },
            "bundle_evidence": evidence_dump,
            "model_records": pgs_records,
            "model_frontier_budget": frontier_budget_per_bundle,
        }
        if prompt_cfg.enable_skill:
            context["cross_trait_guidance"] = _pick_dk.primary_section
        if _pick_pgs_skill.enabled:
            # Advisory text from prs_model_evaluator skill. Source-of-truth
            # corpus shared with contribution2 (loader does not modify).
            context["pgs_quality_guidance"] = _pick_pgs_skill.primary_section
        try:
            bundle_frontier: ModelFrontier = pick_chain(prompt_cfg).invoke(
                {"context_json": json.dumps(context, ensure_ascii=False, default=str)}
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Pick LLM call failed for bundle %s: %s", bundle_id, exc
            )
            continue
        per_bundle_outputs.append(
            {
                "bundle_id": bundle_id,
                "frontier": [fm.model_dump() for fm in bundle_frontier.frontier],
                "primary_pgs_id": bundle_frontier.primary_pgs_id,
                "rationale": bundle_frontier.rationale,
            }
        )

        seen_pgs: set[str] = {fm.pgs_id for fm in aggregated_frontier}
        for fm in bundle_frontier.frontier:
            if fm.pgs_id in seen_pgs:
                continue
            # Enforce the bundle_id reported in the frontier matches the
            # bundle being picked from — hygiene, not ranking.
            fm.bundle_id = bundle_id
            aggregated_frontier.append(fm)
            seen_pgs.add(fm.pgs_id)

        if primary_pgs_id is None and bundle_frontier.primary_pgs_id:
            # The overall primary is the top-ranked pick from the Judge's
            # #1 supporting bundle.
            primary_pgs_id = bundle_frontier.primary_pgs_id

    trace.pick_output_json = {"per_bundle": per_bundle_outputs}

    if not aggregated_frontier:
        return None

    # If no primary came from the first bundle, fall back to the first
    # aggregated frontier entry (still an LLM pick — just from a later bundle).
    if primary_pgs_id is None:
        primary_pgs_id = aggregated_frontier[0].pgs_id

    # Re-rank positions to 1..N in aggregation order (LLM-provided order
    # from each bundle, concatenated in Judge rank order). This is not
    # reordering — just renumbering contiguous ranks.
    for idx, fm in enumerate(aggregated_frontier, start=1):
        fm.rank = idx

    return ModelFrontier(
        frontier=aggregated_frontier,
        primary_pgs_id=primary_pgs_id,
        rationale="Aggregated across top-K supporting bundles in Judge rank order.",
    )


def _include_skill_reference_candidate(
    *,
    model_frontier: Optional[ModelFrontier],
    skill_reference: Optional[dict[str, Any]],
    bundle_lookup: dict[str, TraitBundle],
    registry: EvidenceRegistry,
    trace: AgentTrace,
) -> Optional[ModelFrontier]:
    """Keep the no-skill reference PGS visible to final LLM reconciliation."""
    if not skill_reference:
        return model_frontier
    ref_bundle_id = str(skill_reference.get("reference_bundle_id") or "")
    ref_pgs_id = str(skill_reference.get("reference_primary_pgs_id") or "")
    if not ref_bundle_id or not ref_pgs_id:
        return model_frontier
    bundle = bundle_lookup.get(ref_bundle_id)
    if bundle is None or ref_pgs_id not in set(bundle.candidate_pgs_ids or []):
        return model_frontier
    if model_frontier and any(fm.pgs_id == ref_pgs_id for fm in model_frontier.frontier):
        return model_frontier

    ev = registry.get(ref_bundle_id)
    record = (ev.model_records.get(ref_pgs_id) if ev else None)
    if record is None:
        try:
            record = describe_pgs_model(pgs_id=ref_pgs_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("describe_pgs_model(%s) failed for skill reference: %s", ref_pgs_id, exc)
            record = {"pgs_id": ref_pgs_id, "error": f"describe_error:{exc}"}
        registry.set_model_record(
            bundle_id=ref_bundle_id,
            pgs_id=ref_pgs_id,
            record=record,
            round_idx=100,
        )

    frontier = list(model_frontier.frontier) if model_frontier else []
    frontier.append(
        FrontierModel(
            pgs_id=ref_pgs_id,
            bundle_id=ref_bundle_id,
            rank=len(frontier) + 1,
            confidence="Moderate",
            rationale=(
                "No-skill reference lane primary included for final LLM "
                "comparison with skill-guided evidence."
            ),
        )
    )
    for idx, fm in enumerate(frontier, start=1):
        fm.rank = idx
    trace.provenance.tag(
        field_path=f"frontier[{ref_pgs_id}]",
        value=ref_pgs_id,
        source="harness:skill_reference_lane",
        detail="no-skill reference primary retained in final candidate set",
    )
    return ModelFrontier(
        frontier=frontier,
        primary_pgs_id=model_frontier.primary_pgs_id if model_frontier else ref_pgs_id,
        rationale=(
            (model_frontier.rationale if model_frontier else "")
            + " No-skill reference primary retained for final LLM comparison."
        ).strip(),
    )


# ---------------------------------------------------------------------------
# Stage 5 — CRITIC
# ---------------------------------------------------------------------------

def _run_global_primary_reconciliation(
    *,
    target,
    model_frontier: ModelFrontier,
    bundle_lookup: dict[str, TraitBundle],
    registry: EvidenceRegistry,
    judge_ranks: dict[str, int],
    trace: AgentTrace,
    cfg: Optional["ToolAblationConfig"] = None,
    skill_reference: Optional[dict[str, Any]] = None,
) -> ModelFrontier:
    """Cross-bundle LLM reconciliation.

    Assembles a candidate context from all PGSs in `model_frontier`
    (the union of per-bundle Pick outputs) with their full metadata
    and per-bundle evidence, then asks the LLM to pick the single best
    primary and reorder the frontier. Preserves every candidate.
    """
    cfg = cfg or ToolAblationConfig()
    gp_cfg = replace(
        cfg,
        enable_h2=bool(cfg.enable_h2 and cfg.enable_h2_global_primary_context),
        enable_gc_batch=False,
    )
    if not model_frontier.frontier:
        return model_frontier

    pick_primary_by_bundle: dict[str, str] = {}
    pick_rank_by_bundle_pgs: dict[tuple[str, str], int] = {}
    for entry in (trace.pick_output_json or {}).get("per_bundle") or []:
        bundle_id = str(entry.get("bundle_id") or "")
        primary = str(entry.get("primary_pgs_id") or "")
        if bundle_id and primary:
            pick_primary_by_bundle[bundle_id] = primary
        for fm in entry.get("frontier") or []:
            pid = str(fm.get("pgs_id") or "")
            if not bundle_id or not pid:
                continue
            try:
                pick_rank_by_bundle_pgs[(bundle_id, pid)] = int(fm.get("rank") or 0)
            except (TypeError, ValueError):
                continue

    candidates_ctx: list[dict[str, Any]] = []
    bundle_evidence_ctx: dict[str, Any] = {}
    reference_primary_pgs_id = (
        str(skill_reference.get("reference_primary_pgs_id") or "")
        if skill_reference else ""
    )
    tool_lane_primary_pgs_id = str(model_frontier.primary_pgs_id or "")
    for fm in model_frontier.frontier:
        bev = registry.get(fm.bundle_id)
        if fm.bundle_id not in bundle_evidence_ctx:
            bundle_evidence_ctx[fm.bundle_id] = _summarize_bundle_evidence_for_gp(bev, gp_cfg)
        record = (bev.model_records.get(fm.pgs_id) if bev else None) or {}
        training_samples = record.get("training_samples") or []
        total_training = 0
        for s in training_samples:
            try:
                total_training += int(s.get("sample_number") or 0)
            except (TypeError, ValueError):
                continue
        perf_summary = _summarize_pgs_performance_for_gp(record)
        pub_date = (record.get("publication") or {}).get("date")
        bundle = bundle_lookup.get(fm.bundle_id)
        candidates_ctx.append(
            {
                "pgs_id": fm.pgs_id,
                "source_bundle_id": fm.bundle_id,
                "source_bundle_label": bundle.canonical_label if bundle else None,
                "per_bundle_rank": judge_ranks.get(fm.bundle_id),
                "method_name": record.get("method_name"),
                "variants_number": record.get("variants_number"),
                "reported_trait": record.get("reported_trait"),
                "trait_efo": _compact_trait_terms(record.get("trait_efo") or []),
                "trait_mapped": _compact_trait_terms(record.get("trait_mapped") or []),
                "training_ancestry_distribution": record.get("training_ancestry_distribution") or {},
                "publication_year": (pub_date or "")[:4] if pub_date else None,
                "training_sample_total": total_training,
                "performance_summary": perf_summary["summary"],
                "performance_digest": perf_summary["digest"],
                "bundle_evidence_ref": fm.bundle_id,
                "is_pick_primary_for_bundle": pick_primary_by_bundle.get(fm.bundle_id) == fm.pgs_id,
                "pick_rank_within_bundle": pick_rank_by_bundle_pgs.get((fm.bundle_id, fm.pgs_id)),
                "is_skill_only_reference_primary": (
                    bool(reference_primary_pgs_id) and fm.pgs_id == reference_primary_pgs_id
                ),
                "is_tool_lane_primary_before_arbitration": (
                    bool(tool_lane_primary_pgs_id) and fm.pgs_id == tool_lane_primary_pgs_id
                ),
                "pick_stage_rationale": (fm.rationale or "")[:500],
                "pick_stage_confidence": fm.confidence,
            }
        )

    context = {
        "target": {
            "target_label": target.target_label,
            "target_aliases": list(target.aliases or []),
            "target_code": getattr(target, "target_code", None),
        },
        "candidates": candidates_ctx,
        "bundle_evidence_by_id": bundle_evidence_ctx,
    }
    if skill_reference:
        reference_key = (
            "pgs_quality_reference"
            if getattr(cfg, "enable_pgs_quality_reference_lane", False)
            else "skill_only_reference"
        )
        context[reference_key] = {
            "reference_primary_pgs_id": skill_reference.get("reference_primary_pgs_id"),
            "reference_bundle_id": skill_reference.get("reference_bundle_id"),
            "reference_bundle_label": skill_reference.get("reference_bundle_label"),
            "reference_frontier_pgs_ids": skill_reference.get("reference_frontier_pgs_ids") or [],
            "reference_rationale": skill_reference.get("reference_rationale") or "",
            "reference_lane_description": skill_reference.get("reference_lane_description") or "",
        }
    _gp_dk = cross_trait_domain_knowledge(
        stage="global_primary",
        query=(
            f"target_trait: {target.target_label}; "
            "cross-bundle primary reconciliation"
        ),
        cfg=gp_cfg,
    )
    if gp_cfg.enable_skill:
        context["cross_trait_guidance"] = _gp_dk.primary_section
    # NOTE: pgs_model_evaluator skill is intentionally NOT injected at
    # GLOBAL_PRIMARY_RECONCILIATION. Iteration-0 paired80 measurement
    # showed skill at this stage caused the LLM to switch primaries to
    # bundles whose source trait looked "endpoint-cleaner" but
    # transferred worse on AoU validation (6 of 9 top_0.5% losses were
    # bundle-level switches at this stage). The cross-bundle decision
    # belongs to the LLM weighing per-bundle Pick output, not to within-
    # bundle PGS-quality reasoning. Reconcile is intentionally skill-free
    # so it preserves Pick's bundle preference.
    try:
        decision = global_primary_chain(gp_cfg).invoke(
            {"context_json": json.dumps(context, ensure_ascii=False, default=str)}
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Global primary reconciliation failed: %s — keeping Pick frontier unchanged", exc)
        return model_frontier

    valid_ids = {fm.pgs_id for fm in model_frontier.frontier}
    if decision.primary_pgs_id not in valid_ids:
        logger.warning(
            "Global primary %s not among Pick candidates — keeping original", decision.primary_pgs_id
        )
        return model_frontier

    # Reorder frontier per LLM; preserve all originals even if LLM omits.
    by_pgs = {fm.pgs_id: fm for fm in model_frontier.frontier}
    seen: set[str] = set()
    reordered: list = []
    for pid in decision.ordered_frontier_pgs_ids:
        if pid in seen or pid not in by_pgs:
            continue
        seen.add(pid)
        reordered.append(by_pgs[pid])
    for fm in model_frontier.frontier:
        if fm.pgs_id not in seen:
            reordered.append(fm)
            seen.add(fm.pgs_id)

    # Make sure primary is first in reordered.
    if reordered and reordered[0].pgs_id != decision.primary_pgs_id:
        head = by_pgs[decision.primary_pgs_id]
        reordered = [head] + [fm for fm in reordered if fm.pgs_id != decision.primary_pgs_id]

    for idx, fm in enumerate(reordered, start=1):
        fm.rank = idx

    trace.provenance.tag(
        field_path="global_primary_reconciliation.primary_pgs_id",
        value=decision.primary_pgs_id,
        source="llm:stage_4",
        detail=decision.rationale[:200],
    )
    return ModelFrontier(
        frontier=reordered,
        primary_pgs_id=decision.primary_pgs_id,
        rationale=f"Global reconciliation. {decision.rationale}",
    )


def _summarize_pgs_performance_for_gp(record: dict[str, Any]) -> dict[str, Any]:
    records = record.get("performance_records") or []
    digest: list[dict[str, Any]] = []
    ancestries: set[str] = set()
    best_auc: Optional[float] = None
    best_r2: Optional[float] = None
    largest_sample_count = 0
    summed_sample_count = 0
    records_with_metrics = 0
    for rec in records:
        if not isinstance(rec, dict):
            continue
        sample_count = 0
        for sample in rec.get("samples") or []:
            try:
                sample_count += int(sample.get("sample_number") or 0)
            except (AttributeError, TypeError, ValueError):
                continue
        metrics = rec.get("performance_metrics") or rec.get("performance_metric") or {}
        auc = _metric_max(metrics, is_auc=True)
        r2 = _metric_max(metrics, is_auc=False)
        ancestry = rec.get("ancestry_broad")
        if not ancestry:
            sample_ancestries = {
                str(sample.get("ancestry_broad") or "").strip()
                for sample in rec.get("samples") or []
                if str(sample.get("ancestry_broad") or "").strip()
            }
            ancestry = sorted(sample_ancestries)
        raw_ancestries = ancestry if isinstance(ancestry, list) else [ancestry]
        for raw in raw_ancestries:
            text = str(raw or "").strip()
            if text:
                ancestries.add(text)
        summed_sample_count += sample_count
        largest_sample_count = max(largest_sample_count, sample_count)
        if auc is not None:
            best_auc = auc if best_auc is None else max(best_auc, auc)
        if r2 is not None:
            best_r2 = r2 if best_r2 is None else max(best_r2, r2)
        if auc is not None or r2 is not None:
            records_with_metrics += 1
        if len(digest) < 5:
            digest.append(
                {
                    "ancestry_broad": ancestry,
                    "sample_count": sample_count,
                    "best_auc": auc,
                    "best_r2": r2,
                }
            )

    existing_summary = record.get("performance_summary") if isinstance(record, dict) else None
    summary = existing_summary if isinstance(existing_summary, dict) else {}
    summary = {
        "record_count": summary.get("record_count", len(records)),
        "records_with_metrics": summary.get("records_with_metrics", records_with_metrics),
        "ancestry_broad_values": summary.get("ancestry_broad_values", sorted(ancestries)),
        "summed_sample_count": summary.get("summed_sample_count", summed_sample_count),
        "largest_sample_count": summary.get("largest_sample_count", largest_sample_count),
        "best_auc": summary.get("best_auc", best_auc),
        "best_r2": summary.get("best_r2", best_r2),
    }
    return {"summary": summary, "digest": digest}


def _compact_trait_terms(items: Any, cap: int = 4) -> list[Any]:
    out: list[Any] = []
    if not isinstance(items, list):
        return out
    for item in items[:cap]:
        if isinstance(item, dict):
            row = {}
            if item.get("id"):
                row["id"] = item.get("id")
            if item.get("label"):
                row["label"] = item.get("label")
            elif item.get("name"):
                row["label"] = item.get("name")
            out.append(row or str(item)[:120])
        else:
            out.append(str(item)[:120])
    return out


def _summarize_bundle_evidence_for_gp(bev, cfg: ToolAblationConfig) -> dict[str, Any]:
    if bev is None:
        return {}
    out: dict[str, Any] = {}
    if cfg.enable_gc_batch:
        out["gc"] = bev.gc
    if cfg.enable_h2:
        out["h2_candidate"] = (bev.h2_candidate or [])[:3]
    if cfg.enable_ot:
        out["ot"] = _summarize_ot_for_gp(bev.ot)
    return out


def _summarize_ot_for_gp(ot: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    if not ot:
        return None

    def _target(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "gene": row.get("gene"),
            "target_id": row.get("target_id"),
            "source_score": row.get("source_score"),
            "candidate_score": row.get("candidate_score"),
        }

    def _pathway(row: dict[str, Any]) -> dict[str, Any]:
        genes = row.get("shared_target_genes") or []
        return {
            "pathway_name": row.get("pathway_name"),
            "shared_target_gene_count": len(genes) if isinstance(genes, list) else None,
            "shared_target_genes": genes[:5] if isinstance(genes, list) else [],
        }

    def _id_name(row: dict[str, Any]) -> dict[str, Any]:
        return {"id": row.get("id"), "name": row.get("name")}

    return {
        "target_efo": ot.get("target_efo"),
        "candidate_efo": ot.get("candidate_efo"),
        "unavailable_reason": ot.get("unavailable_reason"),
        "shared_target_count_total": ot.get("shared_target_count_total")
        or len(ot.get("shared_targets") or []),
        "shared_pathway_count_total": ot.get("shared_pathway_count_total")
        or len(ot.get("shared_pathways") or []),
        "phenotype_count_total": ot.get("phenotype_count_total")
        or len(ot.get("phenotypes") or []),
        "therapeutic_areas": [_id_name(r) for r in (ot.get("therapeutic_areas") or [])[:5] if isinstance(r, dict)],
        "ancestors": [_id_name(r) for r in (ot.get("ancestors") or [])[:5] if isinstance(r, dict)],
        "shared_targets_top": [_target(r) for r in (ot.get("shared_targets") or [])[:5] if isinstance(r, dict)],
        "shared_pathways_top": [_pathway(r) for r in (ot.get("shared_pathways") or [])[:5] if isinstance(r, dict)],
    }


def _metric_max(metrics: Any, is_auc: bool) -> Optional[float]:
    """Mirror of tools.pgs._metric_max for in-agent use (no priority tiers)."""
    if not isinstance(metrics, dict):
        return None
    best: Optional[float] = None
    for _, entries in metrics.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            name = " ".join(
                str(part or "")
                for part in (entry.get("name_long"), entry.get("name_short"))
            ).lower()
            is_auc_like = any(t in name for t in ("auroc", "auc", "c-index", "c-stat"))
            is_r2_like = ("r2" in name) or ("r-squared" in name) or ("r²" in name)
            if is_auc and not is_auc_like:
                continue
            if (not is_auc) and not is_r2_like:
                continue
            est = entry.get("estimate") or entry.get("value")
            try:
                f = float(est)
            except (TypeError, ValueError):
                continue
            if best is None or f > best:
                best = f
    return best


def _run_critic(
    *,
    target,
    registry: EvidenceRegistry,
    proposed_frontier: ModelFrontier,
    trace: AgentTrace,
    cfg: Optional["ToolAblationConfig"] = None,
    skill_reference: Optional[dict[str, Any]] = None,
) -> Optional[CritiqueDecision]:
    """Stage 5 Critic — fresh LLM call verifies frontier against raw
    evidence. May revise if an orthogonal evidence axis contradicts.

    The Critic sees the proposed frontier plus the top-3 bundles on
    each raw evidence axis, computed here from `EvidenceRegistry`
    (compute-side, not decision-side: plain sort by one raw field each).
    """
    cfg = cfg or ToolAblationConfig()
    per_axis_top3 = _build_per_axis_top3(registry, cfg=cfg)
    context = {
        "target": {
            "target_label": target.target_label,
            "target_aliases": list(target.aliases or []),
            "target_code": getattr(target, "target_code", None),
        },
        "proposed_frontier": [fm.model_dump() for fm in proposed_frontier.frontier],
        "proposed_primary_pgs_id": proposed_frontier.primary_pgs_id,
        "per_axis_top3": per_axis_top3,
    }
    if skill_reference:
        reference_key = (
            "pgs_quality_reference"
            if getattr(cfg, "enable_pgs_quality_reference_lane", False)
            else "skill_only_reference"
        )
        context[reference_key] = {
            "reference_primary_pgs_id": skill_reference.get("reference_primary_pgs_id"),
            "reference_bundle_id": skill_reference.get("reference_bundle_id"),
            "reference_bundle_label": skill_reference.get("reference_bundle_label"),
            "reference_frontier_pgs_ids": skill_reference.get("reference_frontier_pgs_ids") or [],
        }
    _critic_dk = cross_trait_domain_knowledge(
        stage="critic",
        query=(
            f"target_trait: {target.target_label}; "
            "critic revision; orthogonal evidence contradiction"
        ),
        cfg=cfg,
    )
    if cfg.enable_skill:
        context["cross_trait_guidance"] = _critic_dk.primary_section
    # NOTE: pgs_model_evaluator skill is intentionally NOT injected at
    # CRITIC. Critic's job is to flag clear orthogonal-evidence
    # contradictions of the proposed primary. Adding the long PGS-quality
    # corpus here invites the LLM to second-guess Pick on tie-breaker
    # patterns rather than on contradictory evidence. Iteration-0 showed
    # the heaviest skill influence at the cross-bundle stages produced
    # bundle-level regressions; CRITIC is held skill-free for the same
    # reason until measurement justifies otherwise.
    try:
        result: CritiqueDecision = critic_chain(cfg).invoke(
            {"context_json": json.dumps(context, ensure_ascii=False, default=str)}
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Critic LLM call failed: %s — keeping proposed frontier", exc)
        return CritiqueDecision(
            kept=True,
            rationale=f"critic_llm_error:{exc}; proposed frontier kept unchanged",
        )
    trace.critic_output_json = result.model_dump()
    return result


def _build_per_axis_top3(
    registry: EvidenceRegistry,
    cfg: Optional["ToolAblationConfig"] = None,
) -> dict[str, list[dict[str, Any]]]:
    """Plain sort by raw evidence per axis. No composite score.

    Axes:
      - abs_rg: bundles with `gc.rg` sorted by |rg| descending (significant first).
      - p_value_asc: bundles with `gc.p_value` sorted ascending.
      - shared_targets_count: bundles with `ot.shared_targets`, by count desc.
      - candidate_h2: bundles with `h2_candidate` sorted by h2 desc.
      - phenotype_overlap_count: bundles by `ot.phenotypes` count desc.

    Each entry carries {bundle_id, label, raw_evidence}. No weights here;
    the LLM can see these orthogonal orderings.
    """
    all_ev = registry.snapshot()

    def _abs_rg(ev):
        rg = (ev.gc or {}).get("rg")
        try:
            return abs(float(rg))
        except (TypeError, ValueError):
            return None

    def _p(ev):
        p = (ev.gc or {}).get("p_value")
        try:
            return float(p)
        except (TypeError, ValueError):
            return None

    def _shared(ev):
        ot = ev.ot or {}
        return int(ot.get("shared_target_count_total") or len(ot.get("shared_targets") or []))

    def _h2(ev):
        arr = ev.h2_candidate or []
        best = None
        for r in arr:
            h = r.get("h2") if isinstance(r, dict) else None
            if h is None:
                continue
            try:
                f = float(h)
                if best is None or f > best:
                    best = f
            except (TypeError, ValueError):
                continue
        return best

    def _pheno(ev):
        ot = ev.ot or {}
        return int(ot.get("phenotype_count_total") or len(ot.get("phenotypes") or []))

    def _axis(fn, descending=True, positive_only=True, label_key=None):
        items = []
        for bid, ev in all_ev.items():
            val = fn(ev)
            if val is None:
                continue
            if positive_only and val <= 0:
                continue
            items.append((bid, ev, val))
        items.sort(key=lambda t: t[2], reverse=descending)
        return [
            {
                "bundle_id": bid,
                "label": ev.canonical_label,
                "value": val,
                "raw_gc": ev.gc,
                "raw_ot_shared_count": (
                    int((ev.ot or {}).get("shared_target_count_total") or len((ev.ot or {}).get("shared_targets") or []))
                    if ev.ot else 0
                ),
                "raw_h2_candidate": ev.h2_candidate,
            }
            for bid, ev, val in items[:3]
        ]

    cfg = cfg or ToolAblationConfig()
    out: dict[str, list[dict[str, Any]]] = {}
    if cfg.enable_gc_batch:
        out["abs_rg"] = _axis(_abs_rg, descending=True, positive_only=True)
        out["p_value_asc"] = _axis(_p, descending=False, positive_only=False)
    include_ot = cfg.enable_ot or cfg.enable_ot_late_batch
    if include_ot:
        out["shared_targets_count"] = _axis(_shared, descending=True, positive_only=True)
        out["phenotype_overlap_count"] = _axis(_pheno, descending=True, positive_only=True)
    if cfg.enable_h2:
        out["candidate_h2"] = _axis(_h2, descending=True, positive_only=True)
    return out


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def _assemble_output(
    *,
    dossier: CandidateBundleDossier,
    trace: AgentTrace,
    bundle_ranking: BundleRanking,
    kept_ranked_objs: list,
    model_frontier: Optional[ModelFrontier],
    critic: Optional[CritiqueDecision],
    stop_after: Optional[str],
) -> dict[str, Any]:
    target = dossier.target
    frontier_bundle_ids = [rb.bundle_id for rb in kept_ranked_objs]

    final_frontier: Optional[ModelFrontier] = model_frontier
    apply_critic_revision = (
        critic is not None
        and not critic.kept
        and critic.revised_frontier is not None
    )
    if apply_critic_revision and model_frontier is not None and critic is not None:
        proposed_bundle = _frontier_bundle_for_pgs(
            model_frontier, model_frontier.primary_pgs_id
        )
        revised_primary = critic.revised_primary_pgs_id or critic.revised_frontier[0].pgs_id
        revised_frontier_for_check = ModelFrontier(
            frontier=critic.revised_frontier,
            primary_pgs_id=revised_primary,
            rationale=critic.rationale,
        )
        revised_bundle = _frontier_bundle_for_pgs(revised_frontier_for_check, revised_primary)
        if proposed_bundle and revised_bundle and proposed_bundle == revised_bundle:
            apply_critic_revision = False

    if apply_critic_revision and critic is not None and critic.revised_frontier is not None:
        # P8a-faithful behavior: Critic may replace the frontier with its
        # own revised frontier + primary, but only for cross-bundle evidence
        # contradictions. Same-bundle PGS argmax stays with Pick / GP because
        # Critic does not receive full model records.
        final_frontier = ModelFrontier(
            frontier=critic.revised_frontier,
            primary_pgs_id=critic.revised_primary_pgs_id or critic.revised_frontier[0].pgs_id,
            rationale=critic.rationale,
        )
        for fm in final_frontier.frontier:
            trace.provenance.tag(
                field_path=f"frontier[{fm.pgs_id}]",
                value=fm.pgs_id,
                source="llm:stage_5",
            )
    elif model_frontier is not None:
        for fm in model_frontier.frontier:
            trace.provenance.tag(
                field_path=f"frontier[{fm.pgs_id}]",
                value=fm.pgs_id,
                source="llm:stage_4",
            )

    outcome = "MATCHED" if (final_frontier and final_frontier.frontier) else "ABSTAINED"
    primary_bundle_id = (
        final_frontier.frontier[0].bundle_id if final_frontier and final_frontier.frontier else None
    )
    best_cross_trait = None
    if primary_bundle_id:
        bundle = next((b for b in dossier.candidates if b.bundle_id == primary_bundle_id), None)
        best_cross_trait = bundle.canonical_label if bundle else None

    # Populate evaluate_end_to_end.py-compatible id lists.
    scout_probe_ids = (
        (trace.scout_directive_json or {}).get("probe_bundle_ids") or []
    )
    per_bundle = (trace.pick_output_json or {}).get("per_bundle") or []
    pick_local_champion_ids: list[str] = []
    for entry in per_bundle:
        for fm in entry.get("frontier") or []:
            pid = fm.get("pgs_id")
            if pid and pid not in pick_local_champion_ids:
                pick_local_champion_ids.append(pid)
    model_frontier_pgs_ids = (
        [fm.pgs_id for fm in final_frontier.frontier] if final_frontier else []
    )
    bundle_pgs_lookup = {
        b.bundle_id: list(b.candidate_pgs_ids or []) for b in dossier.candidates
    }

    # evidence_state.candidate_cards for evaluator I/O — bundle_id +
    # candidate_pgs_ids only (no derived scores).
    evidence_candidate_cards = [
        {
            "bundle_id": b.bundle_id,
            "canonical_label": b.canonical_label,
            "candidate_pgs_ids": list(b.candidate_pgs_ids or []),
        }
        for b in dossier.candidates
    ]

    decision: dict[str, Any] = {
        "outcome": outcome,
        "best_cross_trait": best_cross_trait,
        "primary_bundle_id": primary_bundle_id,
        "best_bundle_id": primary_bundle_id,
        "frontier_bundle_ids": frontier_bundle_ids,
        "frontier_bundle_weights": {},  # LLM-led, no weights; kept empty for API compat.
        "confidence": _aggregate_confidence(kept_ranked_objs),
        "stage2": _stage2_block(final_frontier, bundle_ranking),
        "critic": critic.model_dump() if critic is not None else None,
        "evidence_state": {"candidate_cards": evidence_candidate_cards},
        "search_trace": {
            "model_budget_by_bundle": {},
            # evaluate_end_to_end.py expected fields:
            "probed_bundle_ids": list(scout_probe_ids),
            "supporting_bundle_ids": list(frontier_bundle_ids),
            "local_champion_ids": list(pick_local_champion_ids),
            "model_frontier_ids": list(model_frontier_pgs_ids),
            # Helpers for readers wanting to compute oracle_in_X without
            # rebuilding per-bundle pgs lookups:
            "bundle_pgs_lookup": bundle_pgs_lookup,
            # Observability:
            "scout_probe_count": len(scout_probe_ids),
            "gather_halt_reason": trace.gather_halt_reason,
            "gather_tool_calls_consumed": trace.gather_tool_calls_consumed,
        },
        "stop_after": stop_after,
    }

    if final_frontier is not None and final_frontier.frontier:
        decision["best_model_id"] = final_frontier.primary_pgs_id
        decision["recommended_model_ids"] = [fm.pgs_id for fm in final_frontier.frontier]
        decision["model_frontier"] = [fm.model_dump() for fm in final_frontier.frontier]
    else:
        decision["best_model_id"] = None
        decision["recommended_model_ids"] = []
        decision["model_frontier"] = []

    # Union of candidate PGS IDs across all frontier (Judge-ranked) bundles.
    # This is the breadth of what the agent actually explored for this target;
    # distinct from `recommended_model_ids` (the final LLM-ordered frontier).
    union_ids: list[str] = []
    seen_union: set[str] = set()
    for bid in frontier_bundle_ids:
        for pgs_id in bundle_pgs_lookup.get(bid, []):
            if pgs_id in seen_union:
                continue
            seen_union.add(pgs_id)
            union_ids.append(pgs_id)
    decision["candidate_pgs_ids"] = union_ids
    decision["candidate_pgs_ids_union"] = union_ids

    return {
        "target": target.model_dump(),
        "decision": decision,
        "trace": trace.to_dict(),
    }


# ---------------------------------------------------------------------------
# Skill-only reference lane
# ---------------------------------------------------------------------------

def _normalize_skill_reference(
    reference: dict[str, Any],
    *,
    dossier: CandidateBundleDossier,
) -> dict[str, Any]:
    """Validate a frozen no-skill reference against the current dossier.

    This is paired-ablation hygiene: the no-skill baseline decision is
    allowed to be shown to the skill-enabled lane as a reference, but stale
    bundle identities must be repaired by PGS membership before the LLM sees
    it.
    """
    normalized = dict(reference or {})
    ref_bundle_id = str(normalized.get("reference_bundle_id") or "")
    ref_pgs_id = str(normalized.get("reference_primary_pgs_id") or "")
    if not ref_bundle_id or not ref_pgs_id:
        return normalized

    known_bundle = next((b for b in dossier.candidates if b.bundle_id == ref_bundle_id), None)
    if known_bundle is None or ref_pgs_id not in set(known_bundle.candidate_pgs_ids or []):
        containing_bundle = next(
            (b for b in dossier.candidates if ref_pgs_id in set(b.candidate_pgs_ids or [])),
            None,
        )
        if containing_bundle is None:
            normalized["skipped_reason"] = "reference_pgs_not_in_dossier"
            return normalized
        known_bundle = containing_bundle
        normalized["reference_bundle_id"] = containing_bundle.bundle_id

    normalized["reference_bundle_label"] = known_bundle.canonical_label
    normalized.setdefault("outcome", "MATCHED")
    normalized.setdefault("reference_frontier_pgs_ids", [])
    normalized.setdefault("reference_rationale", "")
    normalized["reference_source"] = normalized.get("reference_source") or "frozen_no_skill_baseline"
    return normalized


def _run_skill_reference_lane(
    *,
    dossier: CandidateBundleDossier,
    cfg: ToolAblationConfig,
    max_tool_calls: int,
    stale_rounds: int,
    max_gather_rounds: int,
    model_frontier_budget_per_bundle: int,
    enable_critic: bool,
    benchmark_family: str,
) -> Optional[dict[str, Any]]:
    """Run an independent no-skill pass and return its primary candidate.

    This is a reference for the final LLM reconciliation, not a deterministic
    selection rule. The skill-guided lane must still choose the final primary.
    """
    ref_cfg = ToolAblationConfig(
        enable_h2=False,
        enable_ot=False,
        enable_gc_batch=False,
        enable_biology=False,
        enable_skill=False,
        enable_skill_reference_lane=False,
    )
    try:
        result = run_transfer_agent(
            dossier=dossier,
            max_tool_calls=0 if max_tool_calls <= 0 else max_tool_calls,
            stale_rounds=stale_rounds,
            max_gather_rounds=max_gather_rounds,
            model_frontier_budget_per_bundle=model_frontier_budget_per_bundle,
            enable_critic=enable_critic,
            stop_after=None,
            benchmark_family=benchmark_family,
            tool_ablation=ref_cfg,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("No-skill reference lane failed: %s", exc)
        return {"error": f"no_skill_reference_lane_error:{exc}"}

    decision = result.get("decision") or {}
    ref_bundle_id = decision.get("best_bundle_id") or decision.get("primary_bundle_id")
    ref_pgs_id = decision.get("best_model_id")
    if not ref_bundle_id or not ref_pgs_id:
        return {
            "outcome": decision.get("outcome"),
            "reference_bundle_id": ref_bundle_id,
            "reference_primary_pgs_id": ref_pgs_id,
            "skipped_reason": "no_no_skill_reference_primary",
        }

    known_bundle = next((b for b in dossier.candidates if b.bundle_id == ref_bundle_id), None)
    if known_bundle is None or ref_pgs_id not in set(known_bundle.candidate_pgs_ids or []):
        # The assembled decision can carry a stale primary_bundle_id after
        # cross-bundle reconciliation. Resolve by PGS membership in the current
        # dossier so the reference candidate remains available for LLM
        # arbitration. This is identity hygiene only, not a ranking rule.
        containing_bundle = next(
            (b for b in dossier.candidates if ref_pgs_id in set(b.candidate_pgs_ids or [])),
            None,
        )
        if containing_bundle is None:
            return {
                "outcome": decision.get("outcome"),
                "reference_bundle_id": ref_bundle_id,
                "reference_primary_pgs_id": ref_pgs_id,
                "skipped_reason": "reference_pgs_not_in_dossier",
            }
        known_bundle = containing_bundle
        ref_bundle_id = containing_bundle.bundle_id

    return _normalize_skill_reference({
        "outcome": decision.get("outcome"),
        "reference_bundle_id": ref_bundle_id,
        "reference_bundle_label": known_bundle.canonical_label,
        "reference_primary_pgs_id": ref_pgs_id,
        "reference_frontier_pgs_ids": list(decision.get("recommended_model_ids") or []),
        "reference_rationale": (
            (decision.get("stage2") or {}).get("decision_rationale")
            or (decision.get("stage2") or {}).get("rationale")
            or decision.get("selection_reason")
            or ""
        ),
        "reference_source": "internal_no_skill_reference_lane",
    }, dossier=dossier)


def _run_pgs_quality_reference_lane(
    *,
    dossier: CandidateBundleDossier,
    max_tool_calls: int,
    stale_rounds: int,
    max_gather_rounds: int,
    model_frontier_budget_per_bundle: int,
    enable_critic: bool,
    benchmark_family: str,
) -> Optional[dict[str, Any]]:
    """Run the current PGS-skill/no-evidence lane as an LLM reference.

    This is not a selection rule. The tool-assisted lane still reaches final
    reconciliation, where the LLM sees both candidate judgments and chooses.
    """
    ref_cfg = ToolAblationConfig(
        enable_h2=False,
        enable_ot=False,
        enable_ot_late_batch=False,
        enable_gc_batch=False,
        enable_biology=False,
        enable_skill=False,
        enable_skill_reference_lane=False,
        enable_pgs_quality_skill=True,
        enable_pgs_quality_reference_lane=False,
    )
    try:
        result = run_transfer_agent(
            dossier=dossier,
            max_tool_calls=0 if max_tool_calls <= 0 else max_tool_calls,
            stale_rounds=stale_rounds,
            max_gather_rounds=max_gather_rounds,
            model_frontier_budget_per_bundle=model_frontier_budget_per_bundle,
            enable_critic=enable_critic,
            stop_after=None,
            benchmark_family=benchmark_family,
            tool_ablation=ref_cfg,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("PGS-quality reference lane failed: %s", exc)
        return {"error": f"pgs_quality_reference_lane_error:{exc}"}

    decision = result.get("decision") or {}
    ref_bundle_id = decision.get("best_bundle_id") or decision.get("primary_bundle_id")
    ref_pgs_id = decision.get("best_model_id")
    if not ref_bundle_id or not ref_pgs_id:
        return {
            "outcome": decision.get("outcome"),
            "reference_bundle_id": ref_bundle_id,
            "reference_primary_pgs_id": ref_pgs_id,
            "skipped_reason": "no_pgs_quality_reference_primary",
            "reference_source": "internal_pgs_quality_reference_lane",
        }

    known_bundle = next((b for b in dossier.candidates if b.bundle_id == ref_bundle_id), None)
    if known_bundle is None or ref_pgs_id not in set(known_bundle.candidate_pgs_ids or []):
        containing_bundle = next(
            (b for b in dossier.candidates if ref_pgs_id in set(b.candidate_pgs_ids or [])),
            None,
        )
        if containing_bundle is None:
            return {
                "outcome": decision.get("outcome"),
                "reference_bundle_id": ref_bundle_id,
                "reference_primary_pgs_id": ref_pgs_id,
                "skipped_reason": "reference_pgs_not_in_dossier",
                "reference_source": "internal_pgs_quality_reference_lane",
            }
        known_bundle = containing_bundle
        ref_bundle_id = containing_bundle.bundle_id

    normalized = _normalize_skill_reference({
        "outcome": decision.get("outcome"),
        "reference_bundle_id": ref_bundle_id,
        "reference_bundle_label": known_bundle.canonical_label,
        "reference_primary_pgs_id": ref_pgs_id,
        "reference_frontier_pgs_ids": list(decision.get("recommended_model_ids") or []),
        "reference_rationale": (
            (decision.get("stage2") or {}).get("decision_rationale")
            or (decision.get("stage2") or {}).get("rationale")
            or decision.get("selection_reason")
            or ""
        ),
        "reference_source": "internal_pgs_quality_reference_lane",
    }, dossier=dossier)
    normalized["reference_lane_description"] = "PGS quality skill with evidence tools disabled"
    return normalized


def _frontier_bundle_for_pgs(frontier: ModelFrontier, pgs_id: Optional[str]) -> Optional[str]:
    if not pgs_id:
        return None
    for fm in frontier.frontier:
        if fm.pgs_id == pgs_id:
            return fm.bundle_id
    return None


def _aggregate_confidence(kept_ranked_objs: list) -> str:
    if not kept_ranked_objs:
        return "Low"
    top = kept_ranked_objs[0].confidence
    return top


def _stage2_block(
    final_frontier: Optional[ModelFrontier],
    bundle_ranking: BundleRanking,
) -> dict[str, Any]:
    if final_frontier is None:
        return {
            "model_frontier": [],
            "primary_model_id": None,
            "bundles_hydrated": [],
            "model_universe_size": 0,
            "confidence": "Low",
            "decision_rationale": "",
        }
    return {
        "model_frontier": [fm.model_dump() for fm in final_frontier.frontier],
        "primary_model_id": final_frontier.primary_pgs_id,
        "bundles_hydrated": sorted({fm.bundle_id for fm in final_frontier.frontier}),
        "model_universe_size": len(final_frontier.frontier),
        "confidence": final_frontier.frontier[0].confidence if final_frontier.frontier else "Low",
        "decision_rationale": final_frontier.rationale or bundle_ranking.rationale,
    }
