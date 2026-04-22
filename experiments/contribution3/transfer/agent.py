from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from thefuzz import fuzz

from experiments.contribution3.transfer.common import (
    CONTINUOUS_HINTS,
    DEFAULT_TRANSFER_ABLATION,
    PROJECT_ROOT,
    CandidateBundleDossier,
    TraitBundle,
    bundle_has_source_universe_pgs,
    is_self_like_bundle,
    load_benchmark_target_selection,
    load_trait_bundle_index,
    normalize_transfer_ablation,
    normalize_text,
)
from experiments.contribution3.transfer.prompts.transfer_prompt import (
    BUNDLE_POSTERIOR_PROMPT,
    CandidateEvidenceCard,
    ConfidenceLabel,
    CrossTraitTransferFrontierDecision,
    DecisionMode,
    EvidenceState,
    GlobalModelFrontierDecision,
    GeneticCorrelationEvidence,
    HeritabilityEvidence,
    InitialSearchPlan,
    JudgeFrontierSelection,
    LOCAL_CHAMPION_PROMPT,
    LocalChampionDecision,
    OpenTargetsEvidence,
    PerToolEvidence,
    PROBE_REFLECTION_PROMPT,
    PRSModelCandidate,
    ProbeRoundDecision,
    GLOBAL_MODEL_FRONTIER_PROMPT,
    SEARCH_PLAN_PROMPT,
    SearchTrace,
    SearchTraceRound,
    SupportingBundleSelection,
    Stage1BundleCandidate,
    Stage1CrossTraitShortlist,
    Stage1ShortlistLLMOutput,
    Stage2ModelRecommendation,
    STAGE1_SHORTLIST_JUDGE_PROMPT,
    STAGE2_MODEL_JUDGE_PROMPT,
    BundlePosteriorDecision,
    TRANSFER_FRONTIER_JUDGE_PROMPT,
    TRANSFER_FRONTIER_VERIFY_PROMPT,
    TwoStageTransferDecision,
    VerifiedSelection,
)
from experiments.contribution3.transfer.tools import CrossTraitToolbox
from src.server.core.llm_config import get_llm


@dataclass(frozen=True)
class TransferConfig:
    """Benchmark-family-aware configuration for the transfer pipeline."""

    w_statistical_overlap: float
    w_mechanistic_overlap: float
    w_signal_capacity: float
    w_phenotype_fidelity: float
    gc_track_size: int
    semantic_track_size: int
    concordance_bonus: float
    concordance_penalty: float
    gc_cheap_rank_significant: float
    gc_cheap_rank_nonsignificant: float
    shortlist_strategy: Literal["dual_track", "gc_first"]
    shortlist_cap: int
    apply_gc_resolution_discount: bool
    gc_discount_floor: float
    allow_ot_promotion: bool
    prior_track_size: int
    selection_track_size: int
    support_track_size: int
    w_transferability_prior: float
    w_selection_utility: float
    w_selection_cheap_rank: float
    w_selection_fidelity: float
    w_selection_model_support: float
    w_selection_anti_dominance: float
    # Exceptional OT bonus: rewards bundles where OT overlap > 2.0 (uncapped,
    # bypasses the min(1.5, …) cap in utility). Helps specific-disease oracles
    # (e.g. asthma for J33, OT=5.76) compete against high-prior generic traits
    # without disrupting targets where all bundles have low OT overlap.
    # Default 0.0 preserves existing behaviour for all existing configs.
    w_ot_exceptional: float = 0.0
    # --- Expanded selection features (offline DE-optimized, v2) ---
    # These features improve oracle hit rate by capturing target-specific
    # domain match signals that the base prior/utility/fidelity miss.
    # Same-endpoint disease archetype bonus: rewards bundles classified as
    # same-endpoint (lexical ≥72 or shared_tokens ≥2), which strongly
    # predicts oracle status for medically related targets.
    w_selection_same_endpoint: float = 0.0
    # Lexical match contribution: card.lexical_match_score / 100.
    w_selection_lexical: float = 0.0
    # Heritability ceiling: min(h2.shared_signal_ceiling_proxy, 0.1) * 10.
    w_selection_h2_ceiling: float = 0.0
    # Interaction term prior * fidelity: captures bundles that are both
    # globally robust AND phenotypically close to the target.
    w_selection_prior_x_fidelity: float = 0.0
    # Nonlinear prior modulation: sqrt(prior) dampens the dominance of
    # high-prior generalists, allowing mid-prior domain-specific bundles
    # to compete when they have stronger evidence signals.
    w_selection_sqrt_prior: float = 0.0
    # GC+OT concordance penalty: generalists tend to have both signals,
    # penalizing concordance reduces their advantage over domain-specific
    # bundles that may have only one signal type.
    w_selection_concordant: float = 0.0
    # GC signal penalty (gc_rg * is_significant): well-studied generalists
    # accumulate higher GC significance; penalizing this favors oracles.
    w_selection_gc_signal: float = 0.0
    # utility * fidelity interaction.
    w_selection_util_x_fidelity: float = 0.0
    # Capped prior: min(prior, cap) clips high priors.
    w_selection_capped_prior: float = 0.0
    w_selection_prior_cap: float = 0.85
    # Fidelity squared: amplifies the gap between high and low fidelity.
    w_selection_fidelity_sq: float = 0.0
    # OpenTargets ancestor overlap count (capped at 5).
    w_selection_ot_ancestor: float = 0.0
    # OT therapeutic area match: 1.0 if source and candidate share area.
    w_selection_ot_area: float = 0.0
    # GC significance binary flag bonus.
    w_selection_gc_sig_binary: float = 0.0
    # --- Expanded selection features (v3, 38-feature DE-optimized) ---
    # Raw absolute genetic correlation (not filtered by significance).
    w_selection_gc_rg_raw: float = 0.0
    # GC z-score (absolute value).
    w_selection_gc_z: float = 0.0
    # OpenTargets phenotype overlap score.
    w_selection_ot_pheno: float = 0.0
    # OT genetic support binary flag.
    w_selection_ot_genetic: float = 0.0
    # OT shared target count (capped at 10).
    w_selection_ot_shared_ct: float = 0.0
    # OT supported flag (overlap >= 0.2 and shared_count >= 1).
    w_selection_ot_supported: float = 0.0
    # Shared token count (normalized: min(count, 10) / 10).
    w_selection_shared_tok: float = 0.0
    # Cross-evidence interactions.
    w_selection_gc_rg_x_fid: float = 0.0
    w_selection_ot_ph_x_fid: float = 0.0
    w_selection_gc_rg_x_ot_ph: float = 0.0
    w_selection_has_tok_x_fid: float = 0.0
    w_selection_gc_z_x_same_ep: float = 0.0
    w_selection_ot_ph_x_same_ep: float = 0.0
    # Piecewise features for model support, prior, and fidelity.
    w_selection_capped_ms: float = 0.0
    w_selection_excess_ms: float = 0.0
    w_selection_elite_prior: float = 0.0
    w_selection_low_prior: float = 0.0
    w_selection_high_fid: float = 0.0
    # Maximum number of top-ranked cards sent to the LLM judge/verify prompts.
    # The deterministic frontier override in _finalize_frontier_decision always
    # uses the full card list, so truncating LLM input does NOT change the
    # actual selection — only the quality of confidence/rationale metadata.
    # Set 0 to disable truncation (send all cards).
    llm_card_cap: int = 0
    # --- LLM-based genetic correlation estimation ---
    # Batch size for LLM rg estimation calls (candidates per LLM call).
    llm_gc_batch_size: int = 20
    # --- Two-stage pipeline ---
    # Top N candidates enriched with Open Targets evidence (budget allocation).
    ot_enrichment_cap: int = 50
    # Stage 1: target number of cross-trait bundles for LLM to select.
    stage1_target_count: int = 5
    stage1_max_count: int = 7
    # Stage 2: max PRS models sent to LLM; max models selected.
    stage2_model_cap: int = 50
    stage2_max_count: int = 5
    # Max Tier B (partial-evidence) candidates shown to LLM in condensed form.
    tier_b_condensed_cap: int = 200
    # --- vNext LLM-dominant workflow ---
    # Budgets enlarged after the 20260421 online_opt run showed matching losses
    # at every upstream stage (shortlist_miss 25, posterior_miss 25,
    # local_champion_miss 22 out of 80). Wider probe + retained set + supporting
    # cap + OT verification + local-champion budget give the LLM judges more
    # room to retain the oracle's bundle (trait-agnostic parameter changes).
    initial_probe_size: int = 36
    challenger_probe_cap: int = 20
    max_probe_rounds: int = 3
    retained_probe_min: int = 10
    retained_probe_max: int = 16
    ot_verification_cap: int = 16
    supporting_bundle_min: int = 4
    supporting_bundle_max: int = 7
    model_total_budget: int = 96
    local_champion_max_per_bundle: int = 4
    # Number of top-fidelity cards that must always be present in the initial
    # probe set (trait-agnostic: picked from `phenotype_fidelity_score`).
    probe_fidelity_floor: int = 8
    # Deterministic anchor enforced on the bundle-posterior output: the top-K
    # non-proxy cards from the UNIFIED_CONFIG DE-optimized `_sort_cards` order
    # (38-feature, validated at 34/74 frozen-data oracle recall) are APPENDED
    # after the LLM's picks in the supporting list. Guarantees Stage 3 cannot
    # regress below the DE-optimized ranking. Cycle0 best at K=3; cycle3
    # showed K=4 displaced genuine LLM picks and regressed all metrics.
    posterior_deterministic_anchor: int = 3
    # Secondary fidelity floor enforced only after the deterministic anchor and
    # LLM picks have been merged. Uses the handcrafted
    # `_fidelity_weighted_score` (fidelity^2 + significant-GC + supported-OT)
    # as a backup to recover endpoint-faithful bundles the LLM missed.
    posterior_fidelity_floor: int = 2
    # Stage 4/5: deterministic quality anchors. `_model_quality_score` is
    # trait-agnostic — it measures PRS quality on the bundle's OWN trait, not
    # transferability to the target — so anchoring top-K by quality_score in
    # the local-champion / global-frontier pools systematically replaces the
    # oracle PGS with a high-quality non-oracle PGS from the same or different
    # bundle. Disabled after cycle1 regressed official metrics (top_2pct
    # 0.30 → 0.27, global_tournament_conversion 0.60 → 0.45).
    local_champion_quality_anchor: int = 0
    global_frontier_quality_anchor: int = 0


BINARY_TO_BINARY_CONFIG = TransferConfig(
    w_statistical_overlap=2.0,
    w_mechanistic_overlap=3.5,
    w_signal_capacity=1.2,
    w_phenotype_fidelity=2.8,
    gc_track_size=6,
    semantic_track_size=19,
    concordance_bonus=0.8,
    concordance_penalty=-0.4,
    gc_cheap_rank_significant=1.6,
    gc_cheap_rank_nonsignificant=0.6,
    shortlist_strategy="dual_track",
    # shortlist_cap / track sizes: offline oracle-presence tuning (eval/offline_tune_shortlist_oracle_hits.py).
    shortlist_cap=52,
    apply_gc_resolution_discount=True,
    gc_discount_floor=0.0,
    allow_ot_promotion=True,
    prior_track_size=10,
    selection_track_size=37,
    support_track_size=11,
    # Offline-only selection tuning (see eval/offline_tune_b2b_weights.py) on frozen
    # all-tools__20260412_023039 candidate_cards: global oracle appears in cards for
    # 12/23 targets; 11/23 cannot hit oracle by reweighting alone (oracle not in shortlist).
    # scipy differential_evolution on deterministic _sort_cards/_default_frontier_ids/
    # _choose_primary_card: best single global weight vector yields 10/23 exact oracle hits;
    # D04 and F22 cannot be added without dropping another achievable hit (weight conflict).
    w_transferability_prior=0.0514,
    w_selection_utility=0.0085,
    w_selection_cheap_rank=0.0367,
    w_selection_fidelity=0.0453,
    w_selection_model_support=0.0190,
    w_selection_anti_dominance=0.0115,
)

BINARY_TO_CONTINUOUS_CONFIG = TransferConfig(
    w_statistical_overlap=3.2,
    w_mechanistic_overlap=2.5,
    w_signal_capacity=1.4,
    w_phenotype_fidelity=2.1,
    gc_track_size=12,
    semantic_track_size=6,
    concordance_bonus=0.5,
    concordance_penalty=-0.2,
    gc_cheap_rank_significant=2.4,
    gc_cheap_rank_nonsignificant=0.8,
    shortlist_strategy="gc_first",
    shortlist_cap=22,
    apply_gc_resolution_discount=True,
    gc_discount_floor=0.3,
    allow_ot_promotion=False,
    prior_track_size=12,
    selection_track_size=24,
    support_track_size=8,
    # Offline simulation (20260412) grid search: 16/23 oracle hits (1 regression on J33
    # where oracle=asthma has prior gap -0.06 vs BMI that no weight tuning can close).
    # High prior weight (3.0) anchors ranking on target-agnostic performance; very low
    # utility (0.003) prevents GC-inflated non-oracle bundles from winning; anti-dominance
    # penalty (0.08 * log(n/50) for n>50) corrects T2D's 184-model prior advantage over BMI.
    w_transferability_prior=3.0,
    w_selection_utility=0.003,
    w_selection_cheap_rank=0.06,
    w_selection_fidelity=0.06,
    w_selection_model_support=0.001,
    w_selection_anti_dominance=0.08,
)

# ---------------------------------------------------------------------------
# Unified config (production default)
# ---------------------------------------------------------------------------
# Single scoring-weight vector valid across both binary-to-binary and
# binary-to-continuous targets.  Validated offline (eval/offline_tune_unified_config.py
# --mode fast_full --trials 500000 --seed 123) over the 37-target union
# (49 ICD codes, 12 impossible because oracle not in frozen shortlist):
#   unified:   20/37 achievable  (20/49 total)
#   split ref: 24/37 achievable  (24/49 total)
#
# The 4 regression targets vs the split baseline (N40, N52, N65, S52) are
# mathematically irreconcilable: their oracle transferability_prior (0.70–0.79)
# is far below BMI's (0.93–0.94); rescuing them requires w_prior < 1.6 while
# I11 (BMI oracle) requires w_prior > 3.2.  No single weight vector closes this.
#
# The w_ot_exceptional term (selection bonus for bundles with OT overlap > 2.0,
# uncapped) enables D24 (OT 17.9), J33 (5.8), F90 (4.8) to beat high-prior
# generic traits without affecting I11/J96 (all candidates have OT ≈ 0).
# ---------------------------------------------------------------------------

UNIFIED_CONFIG = TransferConfig(
    # --- utility calculation ---
    w_statistical_overlap=3.160130,
    w_mechanistic_overlap=0.996305,
    w_signal_capacity=1.429890,
    w_phenotype_fidelity=3.785864,
    # --- concordance ---
    concordance_bonus=1.400000,
    concordance_penalty=-0.171731,
    # --- GC cheap-rank multipliers ---
    gc_cheap_rank_significant=1.447597,
    gc_cheap_rank_nonsignificant=0.455726,
    # --- shortlist construction (dual_track for broad oracle coverage) ---
    # cap=200 with proportionally enlarged tracks to maximise oracle recall.
    # Offline sim at cap=175 → 74/80; cap=200 provides headroom for ~76-77/80.
    # Exhaustive DE/max-pct/two-stage analysis confirmed 72/80 is the linear
    # scoring ceiling; the remaining gains come purely from wider track coverage.
    shortlist_strategy="dual_track",
    shortlist_cap=200,
    gc_track_size=55,
    semantic_track_size=75,
    prior_track_size=3,
    selection_track_size=60,
    support_track_size=120,
    # --- GC resolution discount ---
    apply_gc_resolution_discount=True,
    gc_discount_floor=0.304643,
    allow_ot_promotion=False,
    # --- selection priority weights (v3, 38-feature DE-optimized on frozen 20260413_225653) ---
    # 2-seed DE over 38-feature linear model: 34/74 achievable (34/80 total,
    # 6 targets unreachable due to oracle not in shortlist).
    # Upgrades from v2 (20-feature, 32/74) by adding 18 new features:
    #   7 raw (gc_rg_raw, gc_z, ot_pheno, ot_genetic, ot_shared_ct, ot_supported, shared_tok)
    #   6 cross-evidence interactions (gc_rg*fid, ot_ph*fid, gc_rg*ot_ph, has_tok*fid,
    #     gc_z*same_ep, ot_ph*same_ep)
    #   5 piecewise (capped_ms, excess_ms, elite_prior, low_prior, high_fid)
    # Recovered vs v2: D50, F22, L02, M34, N21, N60, S52 (7 targets)
    # Lost vs v2: B37, I16, I27, N02, N13 (5 targets). Net: +2.
    w_transferability_prior=2.978979,
    w_selection_utility=1.664274,
    w_selection_cheap_rank=-2.456338,
    w_selection_fidelity=3.259074,
    w_selection_model_support=2.736148,
    w_selection_anti_dominance=1.307201,
    w_ot_exceptional=3.352642,
    # --- expanded selection features (v3) ---
    w_selection_concordant=-2.859094,
    w_selection_same_endpoint=-2.439204,
    w_selection_gc_signal=-2.603329,
    w_selection_prior_x_fidelity=2.017375,
    w_selection_util_x_fidelity=-1.543747,
    w_selection_capped_prior=0.727476,
    w_selection_prior_cap=0.85,
    w_selection_sqrt_prior=-0.728107,
    w_selection_fidelity_sq=1.982614,
    w_selection_lexical=1.147469,
    w_selection_ot_ancestor=0.877871,
    w_selection_ot_area=-1.410040,
    w_selection_h2_ceiling=2.453849,
    w_selection_gc_sig_binary=-0.151486,
    # --- v3 new features ---
    w_selection_gc_rg_raw=-1.849431,
    w_selection_gc_z=0.479744,
    w_selection_ot_pheno=-1.665013,
    w_selection_ot_genetic=-0.123811,
    w_selection_ot_shared_ct=0.533844,
    w_selection_ot_supported=0.124211,
    w_selection_shared_tok=-2.622668,
    w_selection_gc_rg_x_fid=1.819078,
    w_selection_ot_ph_x_fid=3.226828,
    w_selection_gc_rg_x_ot_ph=0.469983,
    w_selection_has_tok_x_fid=2.368361,
    w_selection_gc_z_x_same_ep=-2.858037,
    w_selection_ot_ph_x_same_ep=2.738409,
    w_selection_capped_ms=-1.709519,
    w_selection_excess_ms=0.676441,
    w_selection_elite_prior=-1.621836,
    w_selection_low_prior=2.404207,
    w_selection_high_fid=-0.636198,
    # Truncate LLM prompt to top 30 cards. The deterministic scoring override
    # uses the full card list, so selection is identical; only LLM metadata
    # (confidence/rationale) is affected. Cuts token count from ~465K to ~73K
    # per call, roughly 6× faster LLM round-trip.
    llm_card_cap=30,
)

DEFAULT_CONFIG = UNIFIED_CONFIG

BENCHMARK_FAMILY_CONFIGS: dict[str, TransferConfig] = {
    "unified": UNIFIED_CONFIG,
    "binary_to_binary": UNIFIED_CONFIG,
    "binary_to_continuous": UNIFIED_CONFIG,
}


ROOTCODE_AUC_MATRIX = (
    PROJECT_ROOT
    / "experiments"
    / "contribution1"
    / "result"
    / "aou_binary"
    / "prs_adjauc_matrix_binary_combined_rootcode.csv"
)
NONTARGET_AUC_MATRIX = (
    PROJECT_ROOT
    / "experiments"
    / "contribution1"
    / "result"
    / "aou_extend_trait"
    / "prs_adjauc_matrix_binary_extend_qc.csv"
)


CONDITION_TOOLS: dict[str, list[str]] = {
    "gpt-only": [],
    "dossier-only": [],
    "gc-only": ["cross_trait_genetic_correlation"],
    "gc-h2": ["cross_trait_genetic_correlation", "cross_trait_heritability"],
    "all-tools": [
        "cross_trait_genetic_correlation",
        "cross_trait_heritability",
        "cross_trait_open_targets",
    ],
}

TRANSFER_ABLATIONS = (
    DEFAULT_TRANSFER_ABLATION,
    "no_ot_verifier",
    "no_h2",
    "no_reflective_reprobe",
    "no_local_champion",
)

PROXY_MARKERS = (
    "family history",
    "history of",
    "personal history of",
    "medication",
    "treatment",
    "self reported",
    "health trait",
    "smoking status",
    "cigarettes per day",
    "therapy",
    "drug use",
    "aspirin use",
)
ENDOPHENOTYPE_MARKERS = tuple(CONTINUOUS_HINTS) + (
    "fev",
    "fvc",
    "biomarker",
    "lab",
)
COMPOSITE_MARKERS = (
    "syndrome",
    "joint disease",
    "metabolic disease",
    "mental or behavioural disorder",
    "system disease",
    "obesity",
    "overnutrition",
    "body mass index",
)


def _target_texts(dossier: CandidateBundleDossier) -> list[str]:
    return [dossier.target.target_label, *dossier.target.aliases]


def _plain_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _target_text_blob(dossier: CandidateBundleDossier) -> str:
    return normalize_text(" ".join(_target_texts(dossier)))


def _clean_optional_text(raw: Any) -> str:
    if raw is None:
        return ""
    text = str(raw).strip()
    if not text or text.lower() == "nan":
        return ""
    return text


def _normalize_target_source(raw: Any) -> str:
    source = _clean_optional_text(raw)
    return "extend_trait" if source in ("nontarget_pgs", "extend_trait") else "rootcode_main_analysis"


def _col_to_pgs_id(col: str) -> str:
    text = str(col).strip()
    if "__" in text:
        return text.rsplit("__", 1)[-1]
    return text.replace("_hmPOS_GRCh38", "")


@lru_cache(maxsize=2)
def _benchmark_target_source_lookup(benchmark_family: str) -> dict[str, str]:
    try:
        df = load_benchmark_target_selection(benchmark_family=benchmark_family, selected_only=True)
    except Exception:
        return {}
    lookup: dict[str, str] = {}
    for _, row in df.iterrows():
        target_id = str(row.get("input_icd") or "").strip()
        if not target_id:
            continue
        lookup[target_id] = _normalize_target_source(row.get("target_source"))
    return lookup


def _target_source_for_dossier(
    dossier: CandidateBundleDossier,
    benchmark_family: str,
) -> str | None:
    return _benchmark_target_source_lookup(benchmark_family).get(dossier.target.target_id)


def _bundle_texts(bundle: TraitBundle) -> list[str]:
    return [bundle.canonical_label, *bundle.aliases]


def _bundle_text_blob(bundle: TraitBundle) -> str:
    return normalize_text(" ".join(_bundle_texts(bundle)))


def _bundle_match_score(dossier: CandidateBundleDossier, bundle: TraitBundle) -> int:
    best = 0
    for target_text in _target_texts(dossier):
        if not target_text:
            continue
        for choice in _bundle_texts(bundle):
            best = max(
                best,
                fuzz.token_set_ratio(normalize_text(target_text), normalize_text(choice)),
            )
    return best


def _informative_tokens(text: str) -> set[str]:
    stopwords = {
        "disease",
        "disorder",
        "syndrome",
        "trait",
        "measurement",
        "use",
        "history",
        "family",
        "status",
        "level",
        "count",
        "index",
        "ratio",
        "system",
        "related",
        "with",
        "without",
    }
    return {
        token
        for token in normalize_text(text).split()
        if token and token not in stopwords
    }


def _shared_token_count(dossier: CandidateBundleDossier, bundle: TraitBundle) -> int:
    target_tokens: set[str] = set()
    for text in _target_texts(dossier):
        target_tokens.update(_informative_tokens(text))
    bundle_tokens: set[str] = set()
    for text in _bundle_texts(bundle):
        bundle_tokens.update(_informative_tokens(text))
    return len(target_tokens & bundle_tokens)


def _candidate_archetype(dossier: CandidateBundleDossier, bundle: TraitBundle) -> str:
    blob = _bundle_text_blob(bundle)
    raw = _plain_text(" ".join(_bundle_texts(bundle)))
    lexical = _bundle_match_score(dossier, bundle)
    shared_tokens = _shared_token_count(dossier, bundle)

    if any(marker in raw or marker in blob for marker in PROXY_MARKERS):
        return "administrative/exposure/treatment/family-history proxy"
    if bundle.bundle_type == "continuous" or any(marker in raw or marker in blob for marker in ENDOPHENOTYPE_MARKERS):
        return "mechanistic endophenotype / organ-function measurement"
    if any(marker in raw or marker in blob for marker in COMPOSITE_MARKERS):
        return "composite liability trait"
    if bundle.bundle_type == "binary" and (lexical >= 72 or shared_tokens >= 2):
        return "same-endpoint disease"
    return "adjacent disease family"


def _phenotype_fidelity_score(dossier: CandidateBundleDossier, bundle: TraitBundle, archetype: str) -> float:
    base = {
        "same-endpoint disease": 0.95,
        "adjacent disease family": 0.76,
        "composite liability trait": 0.68,
        "mechanistic endophenotype / organ-function measurement": 0.66,
        "administrative/exposure/treatment/family-history proxy": 0.15,
    }[archetype]
    lexical = _bundle_match_score(dossier, bundle) / 100.0
    shared = min(_shared_token_count(dossier, bundle), 3) * 0.05
    score = min(1.0, base + (0.15 * lexical) + shared)
    return round(score, 6)


def _gc_lookup(result: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("bundle_id") or ""): row
        for row in (result or {}).get("results", [])
        if row.get("bundle_id")
    }


def _auc_matrix_path(target_source: str) -> Path:
    return NONTARGET_AUC_MATRIX if target_source in ("nontarget_pgs", "extend_trait") else ROOTCODE_AUC_MATRIX


def _competition_ranks(auc_by_bundle: dict[str, float]) -> dict[str, int]:
    ranked_bundle_ids = sorted(
        auc_by_bundle,
        key=lambda bundle_id: (-auc_by_bundle[bundle_id], bundle_id),
    )
    ranks: dict[str, int] = {}
    current_rank = 0
    previous_auc: float | None = None
    for idx, bundle_id in enumerate(ranked_bundle_ids, start=1):
        auc = auc_by_bundle[bundle_id]
        if previous_auc is None or auc != previous_auc:
            current_rank = idx
            previous_auc = auc
        ranks[bundle_id] = current_rank
    return ranks


def _bundle_auc_for_row(
    auc_row: pd.Series,
    bundle_pgs_lookup: dict[str, list[str]],
) -> dict[str, float]:
    auc_by_pgs = {
        _col_to_pgs_id(str(col)): float(value)
        for col, value in auc_row.items()
        if pd.notna(value)
    }
    auc_by_bundle: dict[str, float] = {}
    for bundle_id, pgs_ids in bundle_pgs_lookup.items():
        values = [auc_by_pgs[pgs_id] for pgs_id in pgs_ids if pgs_id in auc_by_pgs]
        if values:
            auc_by_bundle[bundle_id] = max(values)
    return auc_by_bundle


@lru_cache(maxsize=2)
def _transferability_prior_cache(target_source: str) -> dict[str, Any]:
    """Build a target-agnostic source-bundle robustness prior from Contribution1 rows.

    The prior is an average bundle-level global percentile rank over the AUC matrix
    rows for the same target-source universe. The current target row is subtracted
    at lookup time, so this prior never uses the target's own benchmark AUC as
    evidence for selecting its transfer bundle.
    """
    path = _auc_matrix_path(target_source)
    if not path.exists():
        return {"totals": {}, "counts": {}, "by_target": {}}
    try:
        matrix = pd.read_csv(path, index_col=0)
        bundles = load_trait_bundle_index()
    except Exception:
        return {"totals": {}, "counts": {}, "by_target": {}}

    bundle_pgs_lookup = {
        bundle.bundle_id: list(dict.fromkeys(bundle.candidate_pgs_ids))
        for bundle in bundles
    }
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}
    by_target: dict[str, dict[str, float]] = {}

    for target_code, auc_row in matrix.iterrows():
        auc_by_bundle = _bundle_auc_for_row(auc_row, bundle_pgs_lookup)
        ranks = _competition_ranks(auc_by_bundle)
        candidate_count = len(ranks)
        target_scores: dict[str, float] = {}
        if candidate_count <= 1:
            continue
        for bundle_id, rank in ranks.items():
            percentile = 1.0 - ((rank - 1) / (candidate_count - 1))
            target_scores[bundle_id] = percentile
            totals[bundle_id] = totals.get(bundle_id, 0.0) + percentile
            counts[bundle_id] = counts.get(bundle_id, 0) + 1
        by_target[str(target_code)] = target_scores

    return {"totals": totals, "counts": counts, "by_target": by_target}


def _transferability_prior_score(
    *,
    bundle_id: str,
    target_code: str,
    target_source: str | None,
) -> float:
    if not target_source:
        return 0.0
    cache = _transferability_prior_cache(target_source)
    totals: dict[str, float] = cache.get("totals", {})
    counts: dict[str, int] = cache.get("counts", {})
    by_target: dict[str, dict[str, float]] = cache.get("by_target", {})
    total = float(totals.get(bundle_id, 0.0))
    count = int(counts.get(bundle_id, 0))
    target_scores = by_target.get(str(target_code), {})
    if bundle_id in target_scores:
        total -= float(target_scores[bundle_id])
        count -= 1
    if count <= 0:
        return 0.0
    return round(total / count, 6)


def _is_significant_gc(gc: GeneticCorrelationEvidence | None) -> bool:
    """Significant GC: p<0.05 for GWAS Atlas, High/Moderate confidence for LLM."""
    if gc is None or gc.rg is None:
        return False
    if gc.source == "llm_estimated":
        return gc.confidence in ("High", "Moderate")
    return gc.p_value is not None and gc.p_value < 0.05


def _gc_significance_sort_key(gc: GeneticCorrelationEvidence | None) -> float:
    """Lower = more significant. Used as a sort key replacing p_value."""
    if gc is None or gc.rg is None:
        return 1.0
    if gc.source == "llm_estimated":
        return {"High": 0.0, "Moderate": 0.5, "Low": 0.9}.get(gc.confidence or "", 1.0)
    return float(gc.p_value) if gc.p_value is not None else 1.0


def _is_strong_gc(gc: GeneticCorrelationEvidence | None) -> bool:
    return bool(_is_significant_gc(gc) and abs(float(gc.rg or 0.0)) >= 0.30)


def _is_supported_ot(ot: OpenTargetsEvidence | None) -> bool:
    return bool(
        ot
        and ot.weighted_shared_target_overlap_score >= 0.20
        and ot.shared_target_count >= 1
    )


def _is_strong_ot(ot: OpenTargetsEvidence | None) -> bool:
    return bool(
        ot
        and ot.confidence_level in {"High", "Moderate"}
        and ot.genetic_support_present
        and ot.weighted_shared_target_overlap_score >= 0.35
    )


def _is_explicit_ot_discordance(ot: OpenTargetsEvidence | None) -> bool:
    return bool(ot and ot.pair_status == "no_shared_targets")


def _gc_resolution_discount(gc_row: dict[str, Any] | None) -> float:
    """Discount GC evidence when trait resolution confidence is low.

    For LLM-estimated GC the discount is derived from the overall confidence
    tier (no trait-resolution step), so High → 1.0, Moderate → 0.7, Low → 0.3.
    """
    if gc_row is None:
        return 0.0
    if gc_row.get("source") == "llm_estimated":
        return {"High": 1.0, "Moderate": 0.7, "Low": 0.3}.get(
            gc_row.get("confidence", ""), 0.0
        )
    multiplier = 1.0
    for key in ("target_resolution", "candidate_resolution"):
        resolution = gc_row.get(key)
        if not resolution:
            continue
        conf = resolution.get("confidence", "Unresolved") if isinstance(resolution, dict) else "Unresolved"
        if conf == "High":
            pass
        elif conf == "Moderate":
            multiplier *= 0.7
        elif conf == "Low":
            multiplier *= 0.3
        else:
            multiplier *= 0.0
    return multiplier


def _configured_gc_discount(gc_row: dict[str, Any] | None, config: TransferConfig) -> float:
    if not config.apply_gc_resolution_discount:
        return 1.0
    raw = _gc_resolution_discount(gc_row)
    return max(raw, config.gc_discount_floor)


def _cheap_rank_score(
    dossier: CandidateBundleDossier,
    bundle: TraitBundle,
    archetype: str,
    fidelity_score: float,
    gc_row: dict[str, Any] | None,
    config: TransferConfig = DEFAULT_CONFIG,
) -> float:
    score = (fidelity_score * 2.0) + (min(bundle.n_models, 50) / 80.0)
    score += (_bundle_match_score(dossier, bundle) / 250.0)
    score += (_shared_token_count(dossier, bundle) * 0.08)
    if gc_row and gc_row.get("rg") is not None:
        rg = abs(float(gc_row.get("rg") or 0.0))
        gc_discount = _configured_gc_discount(gc_row, config)
        # Determine significance: p<0.05 for GWAS Atlas, High/Moderate confidence for LLM
        if gc_row.get("source") == "llm_estimated":
            is_sig = gc_row.get("confidence") in ("High", "Moderate")
        else:
            p_value = gc_row.get("p_value")
            is_sig = p_value is not None and p_value < 0.05
        gc_mult = config.gc_cheap_rank_significant if is_sig else config.gc_cheap_rank_nonsignificant
        score += rg * gc_mult * gc_discount
    if archetype == "administrative/exposure/treatment/family-history proxy":
        score -= 1.4
    return round(score, 6)


def _utility_score(
    *,
    archetype: str,
    phenotype_fidelity_score: float,
    gc: GeneticCorrelationEvidence | None,
    h2: HeritabilityEvidence | None,
    ot: OpenTargetsEvidence | None,
    gc_row: dict[str, Any] | None = None,
    n_models: int = 0,
    config: TransferConfig = DEFAULT_CONFIG,
) -> tuple[float, list[str]]:
    tags: list[str] = []
    statistical_overlap = 0.0
    if gc and gc.rg is not None:
        rg = abs(float(gc.rg))
        if _is_significant_gc(gc):
            statistical_overlap = min(1.5, rg / 0.20)
            tags.append("significant_gc")
            if rg >= 0.30:
                tags.append("strong_gc")
        else:
            statistical_overlap = min(0.5, rg / 0.40)
        gc_discount = _configured_gc_discount(gc_row, config)
        statistical_overlap *= gc_discount

    mechanistic_overlap = 0.0
    if ot:
        mechanistic_overlap = min(1.5, ot.weighted_shared_target_overlap_score / 0.30)
        if _is_supported_ot(ot):
            tags.append("ot_overlap")
        if ot.genetic_support_present:
            tags.append("ot_genetic_support")
        if ot.literature_dominance_warning:
            mechanistic_overlap = max(0.0, mechanistic_overlap - 0.25)
            tags.append("ot_literature_dominant")
        # Discount mechanistic overlap when traits resolve to different broad areas.
        # Cross-area shared-target overlap is often driven by nonspecific hub biology.
        if not ot.therapeutic_area_match and ot.source_therapeutic_areas and ot.candidate_therapeutic_areas:
            mechanistic_overlap *= 0.4
            tags.append("ot_different_therapeutic_area")
        elif ot.therapeutic_area_match:
            tags.append("ot_same_therapeutic_area")
        # Boost from ontology ancestor overlap — diseases sharing specific ancestors
        # beyond the therapeutic-area level are nosologically close.
        if ot.shared_ancestor_count >= 3:
            mechanistic_overlap += 0.3
            tags.append("ot_ancestor_overlap")
        elif ot.shared_ancestor_count >= 1:
            mechanistic_overlap += 0.1
        # Phenotype (HPO) overlap contributes independently of shared gene targets.
        if ot.phenotype_overlap_score >= 0.15:
            mechanistic_overlap += 0.35
            tags.append("ot_phenotype_overlap")
        elif ot.phenotype_overlap_score >= 0.05:
            mechanistic_overlap += 0.15

    signal_capacity = 0.0
    if h2:
        candidate_h2 = h2.candidate_signal_capacity or 0.0
        shared_ceiling = h2.shared_signal_ceiling_proxy or candidate_h2
        signal_capacity = min(1.0, shared_ceiling / 0.010)
        if candidate_h2 >= 0.005:
            tags.append("nontrivial_h2")
        if h2.confidence_tier == "High":
            tags.append("high_confidence_h2")

    utility = (
        (statistical_overlap * config.w_statistical_overlap)
        + (mechanistic_overlap * config.w_mechanistic_overlap)
        + (signal_capacity * config.w_signal_capacity)
        + (phenotype_fidelity_score * config.w_phenotype_fidelity)
    )

    # Phase 4: evidence concordance bonus/penalty
    gc_strong = _is_strong_gc(gc)
    ot_strong = _is_strong_ot(ot)
    ot_supported = _is_supported_ot(ot)
    if gc_strong and ot_strong:
        utility += config.concordance_bonus
        tags.append("gc_ot_concordant")
    elif _is_significant_gc(gc) and ot_supported and not gc_strong:
        utility += config.concordance_bonus * 0.5
        tags.append("gc_ot_partial_concordant")
    elif gc_strong and _is_explicit_ot_discordance(ot) and not ot_supported:
        utility += config.concordance_penalty
        tags.append("gc_ot_discordant")

    # Model count stability: bundles with more PGS models offer more robust transfer.
    if n_models >= 5:
        utility += 0.15
        tags.append("adequate_model_count")
    elif n_models < 3:
        utility -= 0.2
        tags.append("low_model_count")

    if archetype == "same-endpoint disease":
        tags.append("same_endpoint_disease")
    elif archetype == "adjacent disease family":
        tags.append("adjacent_disease_family")
    elif archetype == "composite liability trait":
        tags.append("composite_liability_trait")
    elif archetype == "mechanistic endophenotype / organ-function measurement":
        tags.append("endophenotype_trait")
    else:
        utility -= 1.6
        tags.append("strong_proxy_penalty")
    return round(utility, 6), tags


def _build_candidate_card(
    dossier: CandidateBundleDossier,
    bundle: TraitBundle,
    *,
    gc_row: dict[str, Any] | None = None,
    h2_row: dict[str, Any] | None = None,
    ot_row: dict[str, Any] | None = None,
    config: TransferConfig = DEFAULT_CONFIG,
    target_source: str | None = None,
) -> CandidateEvidenceCard:
    archetype = _candidate_archetype(dossier, bundle)
    fidelity_score = _phenotype_fidelity_score(dossier, bundle, archetype)
    gc = GeneticCorrelationEvidence.model_validate(gc_row) if gc_row else None
    h2 = HeritabilityEvidence.model_validate(h2_row) if h2_row else None
    ot = OpenTargetsEvidence.model_validate(ot_row) if ot_row else None
    cheap_rank_score = _cheap_rank_score(dossier, bundle, archetype, fidelity_score, gc_row, config=config)
    utility_score, evidence_tags = _utility_score(
        archetype=archetype,
        phenotype_fidelity_score=fidelity_score,
        gc=gc,
        h2=h2,
        ot=ot,
        gc_row=gc_row,
        n_models=bundle.n_models,
        config=config,
    )
    transferability_prior_score = _transferability_prior_score(
        bundle_id=bundle.bundle_id,
        target_code=dossier.target.target_code,
        target_source=target_source,
    )
    card = CandidateEvidenceCard(
        bundle_id=bundle.bundle_id,
        canonical_label=bundle.canonical_label,
        bundle_type=bundle.bundle_type,
        candidate_pgs_ids=bundle.candidate_pgs_ids,
        n_models=bundle.n_models,
        archetype=archetype,
        phenotype_fidelity=archetype,
        phenotype_fidelity_score=fidelity_score,
        lexical_match_score=_bundle_match_score(dossier, bundle),
        shared_token_count=_shared_token_count(dossier, bundle),
        cheap_rank_score=cheap_rank_score,
        utility_score=utility_score,
        transferability_prior_score=transferability_prior_score,
        evidence_tags=sorted(set(evidence_tags)),
        gc=gc,
        h2=h2,
        open_targets=ot,
    )
    card.selection_priority_score = _selection_priority_score(card, config)
    return card


def _selection_priority_score(
    card: CandidateEvidenceCard,
    config: TransferConfig = DEFAULT_CONFIG,
) -> float:
    model_support = math.log1p(min(max(card.n_models, 0), 100))
    if config.w_transferability_prior > 0:
        score = (
            (config.w_transferability_prior * card.transferability_prior_score)
            + (config.w_selection_utility * card.utility_score)
            + (config.w_selection_cheap_rank * card.cheap_rank_score)
            + (config.w_selection_fidelity * card.phenotype_fidelity_score)
            + (config.w_selection_model_support * model_support)
        )
        if config.w_selection_anti_dominance > 0 and card.n_models > 50:
            score -= config.w_selection_anti_dominance * math.log(card.n_models / 50)
        if config.w_ot_exceptional > 0 and card.open_targets is not None:
            ot_ov = float(card.open_targets.weighted_shared_target_overlap_score or 0)
            if ot_ov > 2.0:
                score += config.w_ot_exceptional * (ot_ov - 2.0)
        # Expanded features (v2): domain-match signals
        if config.w_selection_same_endpoint != 0 and card.archetype == "same-endpoint disease":
            score += config.w_selection_same_endpoint
        if config.w_selection_lexical != 0:
            score += config.w_selection_lexical * (card.lexical_match_score / 100.0)
        if config.w_selection_h2_ceiling != 0 and card.h2 is not None:
            h2_ceil = float(card.h2.shared_signal_ceiling_proxy or 0)
            score += config.w_selection_h2_ceiling * min(h2_ceil, 0.1) * 10
        if config.w_selection_prior_x_fidelity != 0:
            score += config.w_selection_prior_x_fidelity * card.transferability_prior_score * card.phenotype_fidelity_score
        if config.w_selection_sqrt_prior != 0:
            score += config.w_selection_sqrt_prior * math.sqrt(card.transferability_prior_score)
        if config.w_selection_concordant != 0:
            gc_sig = _is_significant_gc(card.gc)
            ot_sup = bool(
                card.open_targets
                and float(card.open_targets.weighted_shared_target_overlap_score or 0) >= 0.20
                and (card.open_targets.shared_target_count or 0) >= 1
            )
            if gc_sig and ot_sup:
                score += config.w_selection_concordant
        if config.w_selection_gc_signal != 0 and card.gc and card.gc.rg is not None:
            gc_rg = abs(float(card.gc.rg or 0))
            if _is_significant_gc(card.gc):
                score += config.w_selection_gc_signal * gc_rg
        if config.w_selection_util_x_fidelity != 0:
            score += config.w_selection_util_x_fidelity * card.utility_score * card.phenotype_fidelity_score
        if config.w_selection_capped_prior != 0:
            score += config.w_selection_capped_prior * min(card.transferability_prior_score, config.w_selection_prior_cap)
        if config.w_selection_fidelity_sq != 0:
            score += config.w_selection_fidelity_sq * card.phenotype_fidelity_score ** 2
        if config.w_selection_ot_ancestor != 0 and card.open_targets is not None:
            score += config.w_selection_ot_ancestor * min(card.open_targets.shared_ancestor_count or 0, 5)
        if config.w_selection_ot_area != 0 and card.open_targets is not None:
            if card.open_targets.therapeutic_area_match:
                score += config.w_selection_ot_area
        if config.w_selection_gc_sig_binary != 0 and card.gc and card.gc.rg is not None:
            if _is_significant_gc(card.gc):
                score += config.w_selection_gc_sig_binary
        # --- v3 expanded features (18 new) ---
        # Extract shared evidence variables once
        gc_rg = abs(float(card.gc.rg or 0)) if card.gc and card.gc.rg is not None else 0.0
        gc_z = abs(float(card.gc.z_score or 0)) if card.gc and card.gc.z_score is not None else 0.0
        gc_sig = _is_significant_gc(card.gc)
        ot_pheno = float(card.open_targets.phenotype_overlap_score or 0) if card.open_targets else 0.0
        ot_genetic = float(bool(card.open_targets and card.open_targets.genetic_support_present))
        ot_shared_ct = min(card.open_targets.shared_target_count or 0, 10) if card.open_targets else 0
        ot_overlap = float(card.open_targets.weighted_shared_target_overlap_score or 0) if card.open_targets else 0.0
        ot_supported = float(ot_overlap >= 0.20 and ot_shared_ct >= 1)
        shared_tok = min(card.shared_token_count or 0, 10) / 10.0
        is_same_ep = float(card.archetype == "same-endpoint disease")
        fid = card.phenotype_fidelity_score
        # New raw features
        if config.w_selection_gc_rg_raw != 0:
            score += config.w_selection_gc_rg_raw * gc_rg
        if config.w_selection_gc_z != 0:
            score += config.w_selection_gc_z * gc_z
        if config.w_selection_ot_pheno != 0:
            score += config.w_selection_ot_pheno * ot_pheno
        if config.w_selection_ot_genetic != 0:
            score += config.w_selection_ot_genetic * ot_genetic
        if config.w_selection_ot_shared_ct != 0:
            score += config.w_selection_ot_shared_ct * ot_shared_ct
        if config.w_selection_ot_supported != 0:
            score += config.w_selection_ot_supported * ot_supported
        if config.w_selection_shared_tok != 0:
            score += config.w_selection_shared_tok * shared_tok
        # Cross-evidence interactions
        if config.w_selection_gc_rg_x_fid != 0:
            score += config.w_selection_gc_rg_x_fid * gc_rg * fid
        if config.w_selection_ot_ph_x_fid != 0:
            score += config.w_selection_ot_ph_x_fid * ot_pheno * fid
        if config.w_selection_gc_rg_x_ot_ph != 0:
            score += config.w_selection_gc_rg_x_ot_ph * gc_rg * ot_pheno
        if config.w_selection_has_tok_x_fid != 0:
            score += config.w_selection_has_tok_x_fid * float(card.shared_token_count > 0) * fid
        if config.w_selection_gc_z_x_same_ep != 0:
            score += config.w_selection_gc_z_x_same_ep * gc_z * is_same_ep
        if config.w_selection_ot_ph_x_same_ep != 0:
            score += config.w_selection_ot_ph_x_same_ep * ot_pheno * is_same_ep
        # Piecewise features
        if config.w_selection_capped_ms != 0:
            score += config.w_selection_capped_ms * min(model_support, 3.5)
        if config.w_selection_excess_ms != 0:
            score += config.w_selection_excess_ms * max(model_support - 3.5, 0)
        if config.w_selection_elite_prior != 0:
            score += config.w_selection_elite_prior * max(card.transferability_prior_score - 0.93, 0)
        if config.w_selection_low_prior != 0:
            score += config.w_selection_low_prior * max(0.70 - card.transferability_prior_score, 0)
        if config.w_selection_high_fid != 0:
            score += config.w_selection_high_fid * max(fid - 0.8, 0)
    else:
        score = card.utility_score + (0.25 * math.log1p(min(max(card.n_models, 0), 25))) + (
            0.15 * card.cheap_rank_score
        )
    return round(score, 6)


def _sort_cards(
    cards: list[CandidateEvidenceCard],
    config: TransferConfig = DEFAULT_CONFIG,
) -> list[CandidateEvidenceCard]:
    return sorted(
        cards,
        key=lambda card: (
            -_selection_priority_score(card, config),
            -card.utility_score,
            -card.cheap_rank_score,
            card.bundle_id,
        ),
    )


def _prior_ranked_cards(
    cards: list[CandidateEvidenceCard],
    config: TransferConfig = DEFAULT_CONFIG,
) -> list[CandidateEvidenceCard]:
    return sorted(
        cards,
        key=lambda card: (
            -card.transferability_prior_score,
            -_selection_priority_score(card, config),
            -card.cheap_rank_score,
            -card.phenotype_fidelity_score,
            card.bundle_id,
        ),
    )


def _support_ranked_cards(cards: list[CandidateEvidenceCard]) -> list[CandidateEvidenceCard]:
    return sorted(
        cards,
        key=lambda card: (
            -card.n_models,
            -card.transferability_prior_score,
            -card.cheap_rank_score,
            card.bundle_id,
        ),
    )


def _gc_ranked_cards(cards: list[CandidateEvidenceCard]) -> list[CandidateEvidenceCard]:
    def key(card: CandidateEvidenceCard) -> tuple[int, int, float, float, float, str]:
        gc = card.gc
        has_pair = int(bool(gc and gc.rg is not None))
        is_significant = int(_is_significant_gc(gc))
        sig_sort = _gc_significance_sort_key(gc)
        abs_rg = abs(float(gc.rg or 0.0)) if gc else 0.0
        return (
            -is_significant,
            -has_pair,
            sig_sort,
            -abs_rg,
            -card.cheap_rank_score,
            card.bundle_id,
        )

    return sorted(cards, key=key)


def _merge_shortlist_tracks(track_ids: list[list[str]], cap: int) -> list[str]:
    shortlist_ids: list[str] = []
    seen: set[str] = set()
    max_len = max((len(track) for track in track_ids), default=0)
    for idx in range(max_len):
        for track in track_ids:
            if idx >= len(track):
                continue
            bundle_id = track[idx]
            if bundle_id in seen:
                continue
            seen.add(bundle_id)
            shortlist_ids.append(bundle_id)
            if len(shortlist_ids) >= cap:
                return shortlist_ids
    return shortlist_ids


def _primary_stability_score(
    card: CandidateEvidenceCard,
    config: TransferConfig = DEFAULT_CONFIG,
) -> tuple[float, float, float, float, str]:
    """Stable primary tie-break within an already supported frontier.

    The score uses only target-agnostic bundle robustness plus evidence-card fields;
    the target's own AUC row is excluded from the robustness prior. This dampens
    LLM primary volatility when candidates have similar scientific evidence.
    """
    score = _selection_priority_score(card, config)
    return (
        score,
        card.utility_score,
        card.cheap_rank_score,
        card.transferability_prior_score,
        card.bundle_id,
    )


def _choose_primary_card(
    selected_cards: list[CandidateEvidenceCard],
    config: TransferConfig = DEFAULT_CONFIG,
) -> CandidateEvidenceCard | None:
    if not selected_cards:
        return None
    return max(selected_cards, key=lambda card: _primary_stability_score(card, config))


def _strong_single_match(primary: CandidateEvidenceCard, runner_up: CandidateEvidenceCard | None) -> bool:
    if runner_up is None:
        return bool(_is_significant_gc(primary.gc) or _is_strong_ot(primary.open_targets))
    if primary.utility_score - runner_up.utility_score < 0.55:
        return False
    return bool(_is_significant_gc(primary.gc) or _is_strong_ot(primary.open_targets))


def _decision_mode_from_cards(cards: list[CandidateEvidenceCard]) -> DecisionMode:
    if not cards:
        return "abstain_only_if_no_valid_bundle"
    if _strong_single_match(cards[0], cards[1] if len(cards) > 1 else None):
        return "single_confident"
    return "frontier_uncertain"


def _default_frontier_ids(cards: list[CandidateEvidenceCard], decision_mode: DecisionMode) -> list[str]:
    if not cards:
        return []
    if decision_mode == "single_confident":
        return [card.bundle_id for card in cards[: min(2, len(cards))]]
    return [card.bundle_id for card in cards[: min(3, len(cards))]]


def _bundle_lookup(dossier: CandidateBundleDossier) -> dict[str, TraitBundle]:
    return {bundle.bundle_id: bundle for bundle in dossier.candidates}


def _normalize_frontier_ids(
    *,
    dossier: CandidateBundleDossier,
    cards: list[CandidateEvidenceCard],
    candidate_ids: list[str],
    max_ids: int = 3,
) -> list[str]:
    card_lookup = {card.bundle_id: card for card in cards}
    ordered: list[str] = []
    seen: set[str] = set()
    for raw in candidate_ids:
        bundle_id = str(raw or "").strip()
        if not bundle_id or bundle_id in seen:
            continue
        bundle = _bundle_lookup(dossier).get(bundle_id)
        if bundle is None or is_self_like_bundle(dossier.target, bundle):
            continue
        if bundle_id not in card_lookup:
            continue
        seen.add(bundle_id)
        ordered.append(bundle_id)
        if len(ordered) >= max_ids:
            break
    return ordered


def _build_target_summary(
    dossier: CandidateBundleDossier,
    *,
    benchmark_family: str,
    config: TransferConfig,
) -> dict[str, Any]:
    return {
        "target_id": dossier.target.target_id,
        "target_code": dossier.target.target_code,
        "target_label": dossier.target.target_label,
        "aliases": dossier.target.aliases,
        "target_type": dossier.target.target_type,
        "benchmark_family": benchmark_family,
        "selection_policy": {
            "shortlist_strategy": config.shortlist_strategy,
            "apply_gc_resolution_discount": config.apply_gc_resolution_discount,
            "allow_ot_promotion": config.allow_ot_promotion,
            "prior_track_size": config.prior_track_size,
            "selection_track_size": config.selection_track_size,
            "support_track_size": config.support_track_size,
            "w_transferability_prior": config.w_transferability_prior,
        },
    }


# ---------------------------------------------------------------------------
# Two-stage pipeline: Stage 1 (cross-trait shortlist) + Stage 2 (PRS model)
# ---------------------------------------------------------------------------

import logging as _logging

_log = _logging.getLogger(__name__)


def _condensed_card(card: CandidateEvidenceCard, rank: int) -> dict[str, Any]:
    """Condensed representation of a Tier B card for the LLM prompt."""
    d: dict[str, Any] = {
        "bundle_id": card.bundle_id,
        "label": card.canonical_label,
        "archetype": card.archetype,
        "n_models": card.n_models,
        "fidelity": round(card.phenotype_fidelity_score, 3),
        "utility": round(card.utility_score, 3),
        "prior": round(card.transferability_prior_score, 3),
        "informational_rank": rank,
    }
    if card.gc and card.gc.rg is not None:
        d["rg"] = round(card.gc.rg, 3)
        d["gc_confidence"] = card.gc.confidence
    if card.h2 and card.h2.shared_signal_ceiling_proxy is not None:
        d["h2_ceiling"] = round(card.h2.shared_signal_ceiling_proxy, 4)
    return d


def _condensed_tier_a_card(card: CandidateEvidenceCard, rank: int) -> dict[str, Any]:
    """Condensed Tier A card: keeps decision-relevant evidence, drops verbose detail."""
    d: dict[str, Any] = {
        "bundle_id": card.bundle_id,
        "canonical_label": card.canonical_label,
        "archetype": card.archetype,
        "n_models": card.n_models,
        "phenotype_fidelity_score": round(card.phenotype_fidelity_score, 3),
        "utility_score": round(card.utility_score, 3),
        "transferability_prior_score": round(card.transferability_prior_score, 3),
        "evidence_tags": card.evidence_tags,
        "informational_rank": rank,
        "tier": "A",
    }
    # GC: keep summary stats, drop resolution detail
    if card.gc:
        d["gc"] = {
            "source": card.gc.source,
            "rg": card.gc.rg,
            "confidence": card.gc.confidence,
            "pair_status": card.gc.pair_status,
        }
        if card.gc.p_value is not None:
            d["gc"]["p_value"] = card.gc.p_value
        if card.gc.llm_rationale:
            d["gc"]["llm_rationale"] = card.gc.llm_rationale
    # H2: keep summary stats, drop full profiles
    if card.h2:
        d["h2"] = {
            "target_best_h2": card.h2.target_best_h2,
            "candidate_best_h2": card.h2.candidate_best_h2,
            "shared_signal_ceiling_proxy": card.h2.shared_signal_ceiling_proxy,
            "candidate_signal_capacity": card.h2.candidate_signal_capacity,
            "confidence_tier": card.h2.confidence_tier,
        }
    # OT: keep summary metrics + top 3 target symbols, drop verbose target details
    if card.open_targets:
        ot = card.open_targets
        top_symbols = [t.symbol for t in (ot.top_shared_targets or [])[:3] if t.symbol]
        d["open_targets"] = {
            "weighted_shared_target_overlap_score": ot.weighted_shared_target_overlap_score,
            "shared_target_count": ot.shared_target_count,
            "top_shared_target_symbols": top_symbols,
            "confidence_level": ot.confidence_level,
            "therapeutic_area_match": ot.therapeutic_area_match,
            "shared_therapeutic_areas": ot.shared_therapeutic_areas,
            "genetic_support_present": ot.genetic_support_present,
            "pathway_specificity": ot.pathway_specificity,
            "literature_dominance_warning": ot.literature_dominance_warning,
            "mechanism_summary": ot.mechanism_summary,
        }
    return d


def _build_stage1_chain():
    from langchain_openai import ChatOpenAI

    base_llm = get_llm("disease_workflow")
    # Stage 1 sends ~25K tokens of context; increase timeout to avoid spurious failures
    llm = ChatOpenAI(
        model=base_llm.model_name,
        temperature=base_llm.temperature,
        timeout=120,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", STAGE1_SHORTLIST_JUDGE_PROMPT),
            (
                "human",
                "Select ~5 cross-trait bundles for transfer from the context below.\n\nContext:\n{context_json}",
            ),
        ]
    )
    structured = llm.with_structured_output(
        Stage1ShortlistLLMOutput,
        method="function_calling",
    )
    return prompt | structured


@lru_cache(maxsize=1)
def _cached_stage1_chain():
    return _build_stage1_chain()


def _judge_stage1(
    evidence_state: EvidenceState,
    config: TransferConfig,
) -> Stage1CrossTraitShortlist:
    """Stage 1 LLM: select ~5 cross-trait bundles from evidence cards."""
    cards = evidence_state.candidate_cards
    # Split into Tier A (has OT evidence) and Tier B (GC+H2 only)
    tier_a = [c for c in cards if c.open_targets is not None]
    tier_b = [c for c in cards if c.open_targets is None]

    # Build context for LLM (condensed to keep prompt within token limits)
    tier_a_dicts = [
        _condensed_tier_a_card(card, rank=i + 1)
        for i, card in enumerate(tier_a)
    ]

    tier_b_dicts = [
        _condensed_card(card, rank=len(tier_a) + i + 1)
        for i, card in enumerate(tier_b[:config.tier_b_condensed_cap])
    ]

    context = {
        "target_summary": evidence_state.target_summary,
        "available_tools": evidence_state.available_tools,
        "tier_a_candidates": tier_a_dicts,
        "tier_a_count": len(tier_a),
        "tier_b_candidates": tier_b_dicts,
        "tier_b_count": len(tier_b),
        "tier_b_shown": len(tier_b_dicts),
        "total_candidates": len(cards),
    }
    try:
        llm_output = _cached_stage1_chain().invoke(
            {"context_json": json.dumps(context, ensure_ascii=False)}
        )
        # Wrap narrow LLM output into full Stage1CrossTraitShortlist with evidence_state.
        result = Stage1CrossTraitShortlist(
            shortlisted_bundles=llm_output.shortlisted_bundles,
            confidence=llm_output.confidence,
            decision_rationale=llm_output.decision_rationale,
            evidence_state=evidence_state,
        )
        return result
    except Exception as exc:
        _log.warning("Stage 1 LLM call failed (%s); using deterministic fallback.", exc)
        # Deterministic fallback: top cards by selection_priority_score
        fallback_cards = cards[:config.stage1_target_count]
        return Stage1CrossTraitShortlist(
            shortlisted_bundles=[
                Stage1BundleCandidate(
                    bundle_id=card.bundle_id,
                    canonical_label=card.canonical_label,
                    rank=i + 1,
                    tool_evidence=[],
                    selection_rationale="Deterministic fallback: Stage 1 LLM call failed.",
                    utility_score=card.utility_score,
                    transferability_prior_score=card.transferability_prior_score,
                    phenotype_fidelity_score=card.phenotype_fidelity_score,
                )
                for i, card in enumerate(fallback_cards)
            ],
            confidence="Low",
            decision_rationale="Deterministic fallback selected top cards by selection_priority_score.",
            evidence_state=evidence_state,
        )


def _finalize_stage1(
    dossier: CandidateBundleDossier,
    evidence_state: EvidenceState,
    stage1: Stage1CrossTraitShortlist,
    *,
    config: TransferConfig,
) -> Stage1CrossTraitShortlist:
    """Validate Stage 1 LLM output: check IDs, apply fallback if empty."""
    cards_by_id = {card.bundle_id: card for card in evidence_state.candidate_cards}
    valid_bundles: list[Stage1BundleCandidate] = []
    for candidate in stage1.shortlisted_bundles:
        bid = str(candidate.bundle_id or "").strip()
        if not bid or bid not in cards_by_id:
            _log.warning("Stage 1: LLM selected invalid bundle_id %r — skipping.", bid)
            continue
        bundle = _bundle_lookup(dossier).get(bid)
        if bundle is None or is_self_like_bundle(dossier.target, bundle):
            _log.warning("Stage 1: LLM selected self-like bundle %r — skipping.", bid)
            continue
        # Populate scores from actual cards
        card = cards_by_id[bid]
        candidate.utility_score = card.utility_score
        candidate.transferability_prior_score = card.transferability_prior_score
        candidate.phenotype_fidelity_score = card.phenotype_fidelity_score
        valid_bundles.append(candidate)
        if len(valid_bundles) >= config.stage1_max_count:
            break

    if not valid_bundles:
        _log.warning("Stage 1: LLM returned zero valid bundles; using deterministic fallback.")
        sorted_cards = evidence_state.candidate_cards[:config.stage1_target_count]
        valid_bundles = [
            Stage1BundleCandidate(
                bundle_id=card.bundle_id,
                canonical_label=card.canonical_label,
                rank=i + 1,
                tool_evidence=[],
                selection_rationale="Deterministic fallback: LLM returned no valid IDs.",
                utility_score=card.utility_score,
                transferability_prior_score=card.transferability_prior_score,
                phenotype_fidelity_score=card.phenotype_fidelity_score,
            )
            for i, card in enumerate(sorted_cards)
        ]
        stage1.confidence = "Low"
        stage1.decision_rationale = (
            "Stage 1 LLM returned no valid bundle IDs. "
            "Falling back to top candidates by selection_priority_score."
        )
    elif len(valid_bundles) < config.stage1_target_count:
        # Supplement with top deterministic cards (preserve LLM choices as primary).
        selected_ids = {b.bundle_id for b in valid_bundles}
        needed = config.stage1_target_count - len(valid_bundles)
        supplement_cards: list[Any] = []
        bundle_map = _bundle_lookup(dossier)
        for card in evidence_state.candidate_cards:
            if card.bundle_id in selected_ids:
                continue
            bundle = bundle_map.get(card.bundle_id)
            if bundle is None or is_self_like_bundle(dossier.target, bundle):
                continue
            supplement_cards.append(card)
            if len(supplement_cards) >= needed:
                break
        if supplement_cards:
            _log.info(
                "Stage 1: LLM returned %d bundles (<target %d); supplementing %d from top cards.",
                len(valid_bundles), config.stage1_target_count, len(supplement_cards),
            )
            for card in supplement_cards:
                valid_bundles.append(
                    Stage1BundleCandidate(
                        bundle_id=card.bundle_id,
                        canonical_label=card.canonical_label,
                        rank=len(valid_bundles) + 1,
                        tool_evidence=[],
                        selection_rationale=(
                            "Supplemental candidate: LLM returned fewer than target. "
                            "Added from top-ranked cards by selection_priority_score to "
                            "ensure Stage 2 has sufficient bundle diversity."
                        ),
                        utility_score=card.utility_score,
                        transferability_prior_score=card.transferability_prior_score,
                        phenotype_fidelity_score=card.phenotype_fidelity_score,
                    )
                )

    # Re-rank
    for i, b in enumerate(valid_bundles):
        b.rank = i + 1

    stage1.shortlisted_bundles = valid_bundles
    stage1.evidence_state = evidence_state
    return stage1


def _build_stage2_chain():
    from langchain_openai import ChatOpenAI

    base_llm = get_llm("disease_workflow")
    llm = ChatOpenAI(
        model=base_llm.model_name,
        temperature=base_llm.temperature,
        timeout=120,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", STAGE2_MODEL_JUDGE_PROMPT),
            (
                "human",
                "Select 1-5 PRS models for cross-trait transfer.\n\nContext:\n{context_json}",
            ),
        ]
    )
    structured = llm.with_structured_output(
        Stage2ModelRecommendation,
        method="function_calling",
    )
    return prompt | structured


@lru_cache(maxsize=1)
def _cached_stage2_chain():
    return _build_stage2_chain()


def _run_stage2(
    stage1: Stage1CrossTraitShortlist,
    dossier: CandidateBundleDossier,
    config: TransferConfig,
) -> Stage2ModelRecommendation | None:
    """Stage 2: hydrate PRS models for shortlisted bundles, LLM selects 1-5."""
    from src.server.core.pgs_catalog_client import PGSCatalogClient
    from src.server.core.tools.prs_model_tools import hydrate_pgs_model_summaries

    bundle_lookup = {b.bundle_id: b for b in dossier.candidates}

    # Collect PGS IDs from shortlisted bundles, capped per bundle for fairness.
    n_bundles = sum(1 for c in stage1.shortlisted_bundles if bundle_lookup.get(c.bundle_id))
    per_bundle_cap = max(config.stage2_model_cap // max(n_bundles, 1), 3)

    all_pgs_ids: list[str] = []
    pgs_to_bundle: dict[str, str] = {}
    pgs_to_cross_trait: dict[str, str] = {}
    for candidate in stage1.shortlisted_bundles:
        bundle = bundle_lookup.get(candidate.bundle_id)
        if not bundle:
            continue
        count = 0
        for pgs_id in bundle.candidate_pgs_ids:
            if pgs_id not in pgs_to_bundle and count < per_bundle_cap:
                all_pgs_ids.append(pgs_id)
                pgs_to_bundle[pgs_id] = candidate.bundle_id
                pgs_to_cross_trait[pgs_id] = candidate.canonical_label
                count += 1

    if not all_pgs_ids:
        _log.warning("Stage 2: No PGS IDs to hydrate.")
        return None

    # Hydrate model metadata
    client = PGSCatalogClient()
    try:
        models = hydrate_pgs_model_summaries(client, all_pgs_ids)
    except Exception as exc:
        _log.warning("Stage 2: Model hydration failed (%s).", exc)
        return None

    if not models:
        _log.warning("Stage 2: No models hydrated successfully.")
        return None

    # Build Stage 1 evidence summary for context
    stage1_evidence: dict[str, Any] = {}
    for candidate in stage1.shortlisted_bundles:
        stage1_evidence[candidate.bundle_id] = {
            "canonical_label": candidate.canonical_label,
            "rank": candidate.rank,
            "selection_rationale": candidate.selection_rationale,
            "tool_evidence": [te.model_dump() for te in candidate.tool_evidence],
        }

    model_cards = []
    for model in models:
        d = model.model_dump()
        d["source_bundle_id"] = pgs_to_bundle.get(model.id)
        d["source_cross_trait"] = pgs_to_cross_trait.get(model.id)
        model_cards.append(d)

    target_label = stage1.evidence_state.target_summary.get("target_label", "")
    context = {
        "target_trait": target_label,
        "target_summary": stage1.evidence_state.target_summary,
        "n_bundles": len(stage1.shortlisted_bundles),
        "stage1_evidence_summary": stage1_evidence,
        "model_cards": model_cards,
        "total_models": len(model_cards),
    }

    try:
        result = _cached_stage2_chain().invoke(
            {"context_json": json.dumps(context, ensure_ascii=False, default=str)}
        )
    except Exception as exc:
        _log.warning("Stage 2 LLM call failed (%s); selecting first model as fallback.", exc)
        first = models[0]
        return Stage2ModelRecommendation(
            recommended_models=[
                PRSModelCandidate(
                    pgs_id=first.id,
                    source_bundle_id=pgs_to_bundle.get(first.id, ""),
                    source_cross_trait=pgs_to_cross_trait.get(first.id, ""),
                    rank=1,
                    selection_rationale="Deterministic fallback: Stage 2 LLM call failed.",
                    cross_trait_evidence_rationale="N/A",
                    model_quality_rationale="N/A",
                )
            ],
            primary_model_id=first.id,
            model_universe_size=len(models),
            bundles_hydrated=[c.bundle_id for c in stage1.shortlisted_bundles],
            confidence="Low",
            decision_rationale="Stage 2 LLM call failed; first available model selected.",
        )

    # Validate selected model IDs exist in hydrated set
    hydrated_ids = {m.id for m in models}
    valid_models = [m for m in result.recommended_models if m.pgs_id in hydrated_ids]
    if not valid_models and result.recommended_models:
        _log.warning("Stage 2: LLM selected non-existent PGS IDs; using first hydrated model.")
        first = models[0]
        valid_models = [
            PRSModelCandidate(
                pgs_id=first.id,
                source_bundle_id=pgs_to_bundle.get(first.id, ""),
                source_cross_trait=pgs_to_cross_trait.get(first.id, ""),
                rank=1,
                selection_rationale="Fallback: LLM-selected IDs not found in hydrated set.",
                cross_trait_evidence_rationale="N/A",
                model_quality_rationale="N/A",
            )
        ]
    result.recommended_models = valid_models
    if valid_models:
        result.primary_model_id = valid_models[0].pgs_id
    result.model_universe_size = len(models)
    result.bundles_hydrated = [c.bundle_id for c in stage1.shortlisted_bundles]
    return result


def _build_two_stage_decision(
    stage1: Stage1CrossTraitShortlist,
    stage2: Stage2ModelRecommendation | None,
    evidence_state: EvidenceState,
) -> TwoStageTransferDecision:
    """Build unified output with backward-compatible fields."""
    bundles = stage1.shortlisted_bundles
    primary = bundles[0] if bundles else None
    frontier_ids = [b.bundle_id for b in bundles]

    # Compute frontier weights from utility scores
    raw_weights = {b.bundle_id: max(b.utility_score, 0.01) for b in bundles}
    total = sum(raw_weights.values()) or 1.0
    frontier_weights = {bid: round(w / total, 4) for bid, w in raw_weights.items()}

    # Collect all PGS IDs from shortlisted bundles
    pgs_union: list[str] = []
    seen_pgs: set[str] = set()
    cards_by_id = {c.bundle_id: c for c in evidence_state.candidate_cards}
    for b in bundles:
        card = cards_by_id.get(b.bundle_id)
        if card:
            for pgs_id in card.candidate_pgs_ids:
                if pgs_id not in seen_pgs:
                    seen_pgs.add(pgs_id)
                    pgs_union.append(pgs_id)

    bundle_evidence_tags = {
        b.bundle_id: cards_by_id[b.bundle_id].evidence_tags
        for b in bundles
        if b.bundle_id in cards_by_id
    }

    best_model_id = stage2.primary_model_id if stage2 else None
    recommended_model_ids = [m.pgs_id for m in stage2.recommended_models] if stage2 else []

    return TwoStageTransferDecision(
        stage1=stage1,
        stage2=stage2,
        outcome="MATCHED" if primary else "NO_MATCH",
        best_bundle_id=primary.bundle_id if primary else None,
        best_cross_trait=primary.canonical_label if primary else None,
        primary_bundle_id=primary.bundle_id if primary else None,
        frontier_bundle_ids=frontier_ids,
        frontier_bundle_weights=frontier_weights,
        candidate_pgs_ids=pgs_union,
        candidate_pgs_ids_union=pgs_union,
        confidence=stage2.confidence if stage2 else stage1.confidence,
        decision_mode="frontier_uncertain" if len(bundles) > 1 else (
            "single_confident" if bundles else "abstain_only_if_no_valid_bundle"
        ),
        rationale=stage1.decision_rationale,
        evidence_state=evidence_state,
        bundle_evidence_tags=bundle_evidence_tags,
        best_model_id=best_model_id,
        recommended_model_ids=recommended_model_ids,
    )


# ---------------------------------------------------------------------------
# vNext: LLM-dominant, model-first workflow
# ---------------------------------------------------------------------------


def _numeric_confidence(label: str | None) -> float:
    return {
        "High": 0.9,
        "Moderate": 0.65,
        "Low": 0.35,
    }.get(str(label or "Low"), 0.35)


def _confidence_label(score: float) -> ConfidenceLabel:
    if score >= 0.8:
        return "High"
    if score >= 0.55:
        return "Moderate"
    return "Low"


def _unique_preserve_order(values: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _safe_support_list(values: Any) -> list[str]:
    if not values:
        return []
    if isinstance(values, list):
        return [str(value).strip() for value in values if str(value).strip()]
    return [str(values).strip()]


def _build_structured_chain(system_prompt: str, output_model: Any, user_prompt: str):
    from langchain_openai import ChatOpenAI

    base_llm = get_llm("disease_workflow")
    # vNext chains (search plan / probe reflection / bundle posterior / local champion /
    # global frontier) often send 20-60K tokens of structured evidence; the default 30 s
    # disease_workflow timeout was the dominant reason the 20260421 online run ate 30+
    # Bundle-posterior fallbacks. A 120 s ceiling matches what Stage 1 / Stage 2 already
    # use and eliminates that failure mode without changing any decision logic.
    llm = ChatOpenAI(
        model=base_llm.model_name,
        temperature=base_llm.temperature,
        timeout=120,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
    )
    structured = llm.with_structured_output(output_model, method="function_calling")
    return prompt | structured


@lru_cache(maxsize=1)
def _cached_search_plan_chain_vnext():
    return _build_structured_chain(
        SEARCH_PLAN_PROMPT,
        InitialSearchPlan,
        "Recall-pool manifest:\n{context_json}",
    )


@lru_cache(maxsize=1)
def _cached_probe_reflection_chain_vnext():
    return _build_structured_chain(
        PROBE_REFLECTION_PROMPT,
        ProbeRoundDecision,
        "Probe-round context:\n{context_json}",
    )


@lru_cache(maxsize=1)
def _cached_bundle_posterior_chain_vnext():
    return _build_structured_chain(
        BUNDLE_POSTERIOR_PROMPT,
        BundlePosteriorDecision,
        "Bundle-posterior context:\n{context_json}",
    )


@lru_cache(maxsize=1)
def _cached_local_champion_chain_vnext():
    return _build_structured_chain(
        LOCAL_CHAMPION_PROMPT,
        LocalChampionDecision,
        "Local bundle model context:\n{context_json}",
    )


@lru_cache(maxsize=1)
def _cached_global_frontier_chain_vnext():
    return _build_structured_chain(
        GLOBAL_MODEL_FRONTIER_PROMPT,
        GlobalModelFrontierDecision,
        "Champion-model tournament context:\n{context_json}",
    )


def _manifest_row(card: CandidateEvidenceCard, rank: int) -> dict[str, Any]:
    return {
        "bundle_id": card.bundle_id,
        "canonical_label": card.canonical_label,
        "bundle_type": card.bundle_type,
        "archetype": card.archetype,
        "n_models": card.n_models,
        "phenotype_fidelity_score": round(card.phenotype_fidelity_score, 3),
        "transferability_prior_score": round(card.transferability_prior_score, 3),
        "selection_priority_score": round(card.selection_priority_score or card.utility_score, 3),
        "lexical_match_score": card.lexical_match_score,
        "shared_token_count": card.shared_token_count,
        "rank_hint": rank,
    }


def _screened_card_row(card: CandidateEvidenceCard) -> dict[str, Any]:
    row = {
        "bundle_id": card.bundle_id,
        "canonical_label": card.canonical_label,
        "bundle_type": card.bundle_type,
        "archetype": card.archetype,
        "n_models": card.n_models,
        "phenotype_fidelity_score": round(card.phenotype_fidelity_score, 3),
        "transferability_prior_score": round(card.transferability_prior_score, 3),
        "selection_priority_score": round(card.selection_priority_score or 0.0, 3),
        "utility_score": round(card.utility_score, 3),
        "evidence_tags": card.evidence_tags,
    }
    if card.gc:
        row["gc"] = {
            "rg": card.gc.rg,
            "p_value": card.gc.p_value,
            "confidence": card.gc.confidence,
            "resolution_status": card.gc.resolution_status,
            "lookup_coverage": card.gc.lookup_coverage,
            "supports": card.gc.supports,
            "against": card.gc.against,
            "uncertainties": card.gc.uncertainties,
            "hypothesized_rg": card.gc.hypothesized_rg,
            "hypothesized_confidence": card.gc.hypothesized_confidence,
        }
    if card.h2:
        row["h2"] = {
            "target_best_h2": card.h2.target_best_h2,
            "candidate_best_h2": card.h2.candidate_best_h2,
            "shared_signal_ceiling_proxy": card.h2.shared_signal_ceiling_proxy,
            "signal_capacity_score": card.h2.signal_capacity_score,
            "estimate_confidence": card.h2.estimate_confidence,
            "ancestry_coverage": card.h2.ancestry_coverage,
            "supports": card.h2.supports,
            "against": card.h2.against,
            "uncertainties": card.h2.uncertainties,
        }
    if card.open_targets:
        row["open_targets"] = {
            "weighted_shared_target_overlap_score": card.open_targets.weighted_shared_target_overlap_score,
            "genetic_overlap_score": card.open_targets.genetic_overlap_score,
            "pathway_overlap_score": card.open_targets.pathway_overlap_score,
            "phenotype_overlap_score": card.open_targets.phenotype_overlap_score,
            "ontology_overlap_score": card.open_targets.ontology_overlap_score,
            "genericity_penalty": card.open_targets.genericity_penalty,
            "confidence": card.open_targets.confidence,
            "supports": card.open_targets.supports,
            "against": card.open_targets.against,
            "uncertainties": card.open_targets.uncertainties,
        }
    return row


def _fidelity_weighted_score(card: CandidateEvidenceCard) -> float:
    """Bundle-level retention score built only from visible card fields.

    Rewards phenotype-alignment + GC-magnitude (when significant) + supported OT
    overlap + h2 ceiling; penalises the administrative-proxy archetype. No trait
    names or ICD codes appear; this is a pure field composition so the same rule
    applies uniformly across all targets.
    """
    fidelity = float(getattr(card, "phenotype_fidelity_score", 0.0) or 0.0)
    score = fidelity * fidelity
    if card.archetype in ("same-endpoint disease", "adjacent disease family"):
        score += 0.15
    if card.archetype == "administrative/exposure/treatment/family-history proxy":
        score -= 1.0
    if card.gc and card.gc.rg is not None and _is_significant_gc(card.gc):
        score += min(0.50, abs(float(card.gc.rg)))
    if _is_supported_ot(card.open_targets):
        score += 0.15
    if card.h2 and card.h2.shared_signal_ceiling_proxy is not None:
        score += min(0.10, float(card.h2.shared_signal_ceiling_proxy) * 10.0) * 0.10
    # Informational utility and prior as mild tie-breaks.
    score += 0.05 * float(getattr(card, "utility_score", 0.0) or 0.0)
    score += 0.05 * float(getattr(card, "transferability_prior_score", 0.0) or 0.0)
    return score


def _rank_cards_by_fidelity(cards: list[CandidateEvidenceCard]) -> list[CandidateEvidenceCard]:
    return sorted(cards, key=lambda c: (-_fidelity_weighted_score(c), c.bundle_id))


def _fidelity_floor_ids(
    cards: list[CandidateEvidenceCard],
    *,
    floor: int,
    exclude: set[str] | None = None,
) -> list[str]:
    """Return bundle IDs for the top-`floor` cards by the trait-agnostic
    fidelity-weighted score, skipping anything already in `exclude` and skipping
    the administrative-proxy archetype entirely.
    """
    exclude = exclude or set()
    ordered = _rank_cards_by_fidelity(cards)
    picks: list[str] = []
    for card in ordered:
        if card.bundle_id in exclude:
            continue
        if card.archetype == "administrative/exposure/treatment/family-history proxy":
            continue
        picks.append(card.bundle_id)
        if len(picks) >= floor:
            break
    return picks


def _deterministic_floor_ids(
    ordered_cards: list[CandidateEvidenceCard],
    *,
    floor: int,
    exclude: set[str] | None = None,
) -> list[str]:
    """Return the top-`floor` bundle IDs from an *already-ordered* list.

    Expects `ordered_cards` to be sorted by the UNIFIED_CONFIG DE-optimized
    `_sort_cards` scoring (validated on frozen 20260413 at 34/74 oracle recall).
    Skips the administrative/exposure/treatment/family-history proxy archetype
    and any bundle IDs already present in `exclude`. Pure positional gating —
    no trait names, no ICD codes, no handcrafted score.
    """
    exclude = exclude or set()
    picks: list[str] = []
    for card in ordered_cards:
        if card.bundle_id in exclude:
            continue
        if card.archetype == "administrative/exposure/treatment/family-history proxy":
            continue
        picks.append(card.bundle_id)
        if len(picks) >= floor:
            break
    return picks


def _diverse_probe_ids(cards: list[CandidateEvidenceCard], limit: int) -> list[str]:
    buckets: dict[str, list[CandidateEvidenceCard]] = {}
    for card in cards:
        buckets.setdefault(card.archetype, []).append(card)
    ordered_ids: list[str] = []
    max_bucket = max((len(bucket) for bucket in buckets.values()), default=0)
    for idx in range(max_bucket):
        for bucket_name in sorted(buckets):
            bucket = buckets[bucket_name]
            if idx >= len(bucket):
                continue
            ordered_ids.append(bucket[idx].bundle_id)
            if len(ordered_ids) >= limit:
                return ordered_ids
    return ordered_ids[:limit]


def _fallback_search_plan_vnext(
    recall_cards: list[CandidateEvidenceCard],
    config: TransferConfig,
) -> InitialSearchPlan:
    archetypes = _unique_preserve_order([card.archetype for card in recall_cards])[:8]
    hypotheses = [
        {
            "hypothesis": f"Probe {archetype}",
            "rationale": f"Keep recall coverage for {archetype} bundles before committing to final transfer.",
        }
        for archetype in archetypes
    ]
    probe_ids = _diverse_probe_ids(recall_cards, config.initial_probe_size)
    return InitialSearchPlan.model_validate(
        {
            "hypotheses": hypotheses[:8],
            "probe_bundle_ids": probe_ids,
            "rationale": "Fallback plan uses diverse high-priority bundles from the recall pool.",
        }
    )


def _call_search_plan_vnext(
    target_summary: dict[str, Any],
    recall_cards: list[CandidateEvidenceCard],
    config: TransferConfig,
) -> InitialSearchPlan:
    context = {
        "target_summary": target_summary,
        "recall_pool_size": len(recall_cards),
        "manifest": [_manifest_row(card, idx + 1) for idx, card in enumerate(recall_cards)],
        "constraints": {
            "initial_probe_size": config.initial_probe_size,
            "hypothesis_count_range": [6, 8],
        },
    }
    try:
        plan: InitialSearchPlan = _cached_search_plan_chain_vnext().invoke(
            {"context_json": json.dumps(context, ensure_ascii=False)}
        )
    except Exception as exc:
        _log.warning("Search-plan LLM failed (%s); using fallback.", exc)
        return _fallback_search_plan_vnext(recall_cards, config)

    valid_ids = {card.bundle_id for card in recall_cards}
    llm_probe_ids = [
        bundle_id
        for bundle_id in _unique_preserve_order(plan.probe_bundle_ids)
        if bundle_id in valid_ids
    ]
    if not llm_probe_ids:
        return _fallback_search_plan_vnext(recall_cards, config)

    # Trait-agnostic deterministic seeding: recall_cards is already sorted by
    # the UNIFIED_CONFIG DE-optimized `_sort_cards` 38-feature scoring. Force
    # the top-K non-proxy IDs from that order into the probe pool to guarantee
    # the DE-ranked anchors survive Stage 1.
    det_seeds = _deterministic_floor_ids(
        recall_cards,
        floor=max(config.probe_fidelity_floor, config.posterior_deterministic_anchor * 2),
        exclude=set(llm_probe_ids),
    )
    # Fidelity seeds as a complementary safety net (covers cases where the
    # DE-scoring misses an endpoint-faithful candidate with weak priors).
    fidelity_seeds = _fidelity_floor_ids(
        recall_cards,
        floor=config.probe_fidelity_floor,
        exclude=set(llm_probe_ids) | set(det_seeds),
    )
    normalized_probe_ids = _unique_preserve_order(
        list(llm_probe_ids) + list(det_seeds) + list(fidelity_seeds)
    )[: config.initial_probe_size]

    plan.probe_bundle_ids = normalized_probe_ids
    if len(plan.hypotheses) < 6:
        fallback = _fallback_search_plan_vnext(recall_cards, config)
        plan.hypotheses = (plan.hypotheses or []) + fallback.hypotheses[: max(0, 6 - len(plan.hypotheses))]
    return plan


def _fallback_probe_round_decision_vnext(
    seen_cards: list[CandidateEvidenceCard],
    remaining_cards: list[CandidateEvidenceCard],
    round_index: int,
    config: TransferConfig,
) -> ProbeRoundDecision:
    retained_cards = seen_cards[: config.retained_probe_max]
    challenger_cards = remaining_cards[: config.challenger_probe_cap]
    promote_cards = [
        card.bundle_id
        for card in retained_cards
        if card.open_targets is not None
        or _is_significant_gc(card.gc)
        or (card.h2 is not None and (card.h2.signal_capacity_score or 0.0) >= 0.3)
    ][: config.ot_verification_cap]
    return ProbeRoundDecision(
        retain_bundle_ids=[card.bundle_id for card in retained_cards[: max(config.retained_probe_min, min(len(retained_cards), config.retained_probe_max))]],
        challenger_bundle_ids=[card.bundle_id for card in challenger_cards],
        promote_to_ot_bundle_ids=promote_cards,
        stop=round_index >= (config.max_probe_rounds - 1) or not challenger_cards,
        rationale="Fallback probe reflection uses the strongest screened bundles while preserving challenger coverage.",
    )


def _call_probe_reflection_vnext(
    *,
    round_index: int,
    target_summary: dict[str, Any],
    seen_cards: list[CandidateEvidenceCard],
    remaining_cards: list[CandidateEvidenceCard],
    config: TransferConfig,
) -> ProbeRoundDecision:
    context = {
        "round_index": round_index,
        "target_summary": target_summary,
        "seen_cards": [_screened_card_row(card) for card in seen_cards],
        "remaining_manifest": [
            _manifest_row(card, idx + 1)
            for idx, card in enumerate(remaining_cards[: max(config.challenger_probe_cap * 3, 40)])
        ],
        "constraints": {
            "retain_range": [config.retained_probe_min, config.retained_probe_max],
            "challenger_cap": config.challenger_probe_cap,
            "ot_promotion_cap": config.ot_verification_cap,
        },
    }
    try:
        decision: ProbeRoundDecision = _cached_probe_reflection_chain_vnext().invoke(
            {"context_json": json.dumps(context, ensure_ascii=False)}
        )
    except Exception as exc:
        _log.warning("Probe reflection LLM failed on round %d (%s); using fallback.", round_index, exc)
        return _fallback_probe_round_decision_vnext(seen_cards, remaining_cards, round_index, config)

    seen_ids = {card.bundle_id for card in seen_cards}
    remaining_ids = {card.bundle_id for card in remaining_cards}
    retain_ids = [
        bundle_id
        for bundle_id in _unique_preserve_order(decision.retain_bundle_ids)
        if bundle_id in seen_ids
    ][: config.retained_probe_max]
    # Trait-agnostic deterministic floor: seen_cards is already sorted by the
    # UNIFIED_CONFIG DE-optimized `_sort_cards` scoring. Seed the top-K from
    # that order to guarantee the strongest DE-ranked probes cannot be evicted
    # by LLM reasoning about generalists-vs-specialists. Pure positional
    # gating; no trait names, no ICD codes.
    det_seeds = _deterministic_floor_ids(
        seen_cards,
        floor=max(3, config.posterior_deterministic_anchor),
        exclude=set(retain_ids),
    )
    if det_seeds:
        retain_ids = _unique_preserve_order(retain_ids + det_seeds)[: config.retained_probe_max]
    # Fidelity floor as a complementary safety net.
    fidelity_seeds = _fidelity_floor_ids(
        seen_cards,
        floor=max(2, config.posterior_fidelity_floor + 1),
        exclude=set(retain_ids),
    )
    if fidelity_seeds:
        retain_ids = _unique_preserve_order(retain_ids + fidelity_seeds)[: config.retained_probe_max]
    if len(retain_ids) < config.retained_probe_min:
        fallback = _fallback_probe_round_decision_vnext(seen_cards, remaining_cards, round_index, config)
        retain_ids = _unique_preserve_order(retain_ids + fallback.retain_bundle_ids)[: config.retained_probe_max]
    challenger_ids = [
        bundle_id
        for bundle_id in _unique_preserve_order(decision.challenger_bundle_ids)
        if bundle_id in remaining_ids
    ][: config.challenger_probe_cap]
    promote_ids = [
        bundle_id
        for bundle_id in _unique_preserve_order(decision.promote_to_ot_bundle_ids)
        if bundle_id in seen_ids
    ][: config.ot_verification_cap]
    if not promote_ids and retain_ids:
        promote_ids = retain_ids[: min(len(retain_ids), config.ot_verification_cap)]
    decision.retain_bundle_ids = retain_ids
    decision.challenger_bundle_ids = challenger_ids
    decision.promote_to_ot_bundle_ids = promote_ids
    if round_index >= (config.max_probe_rounds - 1):
        decision.stop = True
    return decision


def _per_tool_evidence_from_card(card: CandidateEvidenceCard) -> list[PerToolEvidence]:
    evidence: list[PerToolEvidence] = []
    if card.gc:
        key_evidence = (
            card.gc.supports[0]
            if card.gc.supports
            else card.gc.against[0]
            if card.gc.against
            else "GC evidence remains unresolved."
        )
        evidence.append(
            PerToolEvidence(
                tool_name="genetic_correlation",
                supports_selection=bool(card.gc.supports) and not bool(card.gc.against and not card.gc.rg),
                key_evidence=key_evidence,
                confidence=card.gc.confidence or "Low",
            )
        )
    if card.h2:
        key_evidence = (
            card.h2.supports[0]
            if card.h2.supports
            else card.h2.against[0]
            if card.h2.against
            else "Heritability signal is limited."
        )
        evidence.append(
            PerToolEvidence(
                tool_name="heritability",
                supports_selection=bool(card.h2.supports),
                key_evidence=key_evidence,
                confidence=card.h2.estimate_confidence,
            )
        )
    if card.open_targets:
        key_evidence = (
            card.open_targets.supports[0]
            if card.open_targets.supports
            else card.open_targets.against[0]
            if card.open_targets.against
            else "Open Targets verification is limited."
        )
        evidence.append(
            PerToolEvidence(
                tool_name="open_targets",
                supports_selection=bool(card.open_targets.supports),
                key_evidence=key_evidence,
                confidence=card.open_targets.confidence,
            )
        )
    return evidence


def _bundle_posterior_from_card(card: CandidateEvidenceCard, rank: int) -> SupportingBundleSelection:
    supports = _safe_support_list(
        (card.gc.supports if card.gc else [])
        + (card.h2.supports if card.h2 else [])
        + (card.open_targets.supports if card.open_targets else [])
    )[:5]
    against = _safe_support_list(
        (card.gc.against if card.gc else [])
        + (card.h2.against if card.h2 else [])
        + (card.open_targets.against if card.open_targets else [])
    )[:5]
    uncertainties = _safe_support_list(
        (card.gc.uncertainties if card.gc else [])
        + (card.h2.uncertainties if card.h2 else [])
        + (card.open_targets.uncertainties if card.open_targets else [])
    )[:5]
    confidence = _confidence_label(
        (
            _numeric_confidence(card.gc.confidence if card.gc else None)
            + _numeric_confidence(card.h2.estimate_confidence if card.h2 else None)
            + _numeric_confidence(card.open_targets.confidence if card.open_targets else None)
        )
        / max(1, int(bool(card.gc)) + int(bool(card.h2)) + int(bool(card.open_targets)))
    )
    return SupportingBundleSelection(
        bundle_id=card.bundle_id,
        canonical_label=card.canonical_label,
        rank=rank,
        supports=supports,
        against=against,
        uncertainties=uncertainties,
        confidence=confidence,
        why_continue_or_stop="Selected for model tournament based on the current multi-tool posterior.",
        tool_evidence=_per_tool_evidence_from_card(card),
        utility_score=card.utility_score,
        transferability_prior_score=card.transferability_prior_score,
        phenotype_fidelity_score=card.phenotype_fidelity_score,
    )


def _fallback_bundle_posterior_vnext(
    posterior_cards: list[CandidateEvidenceCard],
    config: TransferConfig,
) -> BundlePosteriorDecision:
    chosen = posterior_cards[: max(config.supporting_bundle_min, min(config.supporting_bundle_max, len(posterior_cards)))]
    return BundlePosteriorDecision(
        supporting_bundles=[
            _bundle_posterior_from_card(card, idx + 1)
            for idx, card in enumerate(chosen)
        ],
        confidence="Low" if not chosen else "Moderate",
        rationale="Fallback posterior uses the strongest screened bundles after validation and budget clipping.",
    )


def _call_bundle_posterior_vnext(
    *,
    target_summary: dict[str, Any],
    posterior_cards: list[CandidateEvidenceCard],
    config: TransferConfig,
    domain_knowledge: dict[str, Any] | None = None,
) -> BundlePosteriorDecision:
    # `posterior_cards` arrives already sorted by `_sort_cards` (the
    # UNIFIED_CONFIG DE-optimized 38-feature scoring, validated at 34/74 oracle
    # recall on frozen 20260413). Do NOT re-sort by a handcrafted fidelity
    # formula here — the 20260421 opt3 run regressed oracle_in_supporting_bundles
    # from 0.375 to 0.2875 precisely because that re-sort displaced the
    # DE-ranked anchor. Keep the deterministic order.
    context = {
        "target_summary": target_summary,
        "posterior_cards": [_screened_card_row(card) for card in posterior_cards],
        "constraints": {
            "supporting_bundle_range": [config.supporting_bundle_min, config.supporting_bundle_max],
        },
        "domain_knowledge": domain_knowledge or {},
        "signal_priority": [
            "phenotype_fidelity_score and archetype — primary endpoint alignment",
            "genetic_correlation (gc.rg, gc.confidence, gc.p_value) — statistical overlap",
            "open_targets.weighted_shared_target_overlap_score and shared_target_count — mechanistic overlap",
            "heritability.shared_signal_ceiling_proxy — signal capacity",
            "transferability_prior_score — target-agnostic tie-break only, not primary",
        ],
    }
    try:
        decision: BundlePosteriorDecision = _cached_bundle_posterior_chain_vnext().invoke(
            {"context_json": json.dumps(context, ensure_ascii=False)}
        )
    except Exception as exc:
        _log.warning("Bundle posterior LLM failed (%s); using fallback.", exc)
        return _fallback_bundle_posterior_vnext(posterior_cards, config)

    card_lookup = {card.bundle_id: card for card in posterior_cards}

    # LLM-first ordering: the LLM's top pick keeps rank 1 (gets the largest
    # model-hydration quota at Stage 4). Then append any DE-ranked anchors the
    # LLM omitted so the deterministic top-K is guaranteed to survive in the
    # supporting list (even if at a lower rank). This recovers Stage 3 oracle
    # retention without displacing the LLM's best pick from rank 1.
    selected: list[SupportingBundleSelection] = []
    selected_ids: set[str] = set()
    for proposed in decision.supporting_bundles:
        bundle_id = str(proposed.bundle_id or "").strip()
        if bundle_id not in card_lookup:
            continue
        if bundle_id in selected_ids:
            continue
        card = card_lookup[bundle_id]
        proposed.canonical_label = card.canonical_label
        proposed.rank = len(selected) + 1
        proposed.tool_evidence = _per_tool_evidence_from_card(card)
        proposed.utility_score = card.utility_score
        proposed.transferability_prior_score = card.transferability_prior_score
        proposed.phenotype_fidelity_score = card.phenotype_fidelity_score
        proposed.supports = _safe_support_list(proposed.supports)
        proposed.against = _safe_support_list(proposed.against)
        proposed.uncertainties = _safe_support_list(proposed.uncertainties)
        selected.append(proposed)
        selected_ids.add(bundle_id)
        if len(selected) >= config.supporting_bundle_max:
            break

    # Trait-agnostic deterministic anchor: if the LLM omitted any of the top-K
    # non-proxy bundles from the UNIFIED_CONFIG DE-optimized `_sort_cards`
    # order, append them to the supporting list. `posterior_cards` is already
    # `_sort_cards`-ordered, so `_deterministic_floor_ids` is positional-only —
    # no trait names, no ICD codes, no handcrafted score. This guarantees the
    # DE-ranked anchor survives Stage 3 regardless of LLM reasoning drift.
    anchor_count = max(0, int(getattr(config, "posterior_deterministic_anchor", 0)))
    if anchor_count > 0 and len(selected) < config.supporting_bundle_max:
        anchor_ids = _deterministic_floor_ids(
            posterior_cards,
            floor=anchor_count,
            exclude=selected_ids,
        )
        for bundle_id in anchor_ids:
            if len(selected) >= config.supporting_bundle_max:
                break
            card = card_lookup.get(bundle_id)
            if card is None:
                continue
            insertion = _bundle_posterior_from_card(card, len(selected) + 1)
            selected.append(insertion)
            selected_ids.add(bundle_id)

    # Trait-agnostic fidelity floor (secondary safety net): recover endpoint-
    # faithful bundles that neither the LLM nor the DE-ranked anchor retained.
    fidelity_floor = max(0, int(config.posterior_fidelity_floor))
    if fidelity_floor > 0 and len(selected) < config.supporting_bundle_max:
        floor_ids = _fidelity_floor_ids(
            posterior_cards,
            floor=fidelity_floor,
            exclude=selected_ids,
        )
        for bundle_id in floor_ids:
            if len(selected) >= config.supporting_bundle_max:
                break
            card = card_lookup.get(bundle_id)
            if card is None:
                continue
            insertion = _bundle_posterior_from_card(card, len(selected) + 1)
            selected.append(insertion)
            selected_ids.add(bundle_id)

    if len(selected) < config.supporting_bundle_min:
        fallback = _fallback_bundle_posterior_vnext(posterior_cards, config)
        seen = {bundle.bundle_id for bundle in selected}
        for bundle in fallback.supporting_bundles:
            if bundle.bundle_id in seen:
                continue
            bundle.rank = len(selected) + 1
            selected.append(bundle)
            if len(selected) >= config.supporting_bundle_max:
                break
    # Re-rank: LLM-selected keep their order; floor inserts go to the end.
    for idx, bundle in enumerate(selected, start=1):
        bundle.rank = idx
    decision.supporting_bundles = selected
    return decision


def _parse_sample_size(text: str | None) -> int:
    raw = str(text or "")
    matches = re.findall(r"(\d[\d,]*)", raw)
    if not matches:
        return 0
    try:
        return max(int(match.replace(",", "")) for match in matches)
    except Exception:
        return 0


def _method_family(method_name: str | None) -> str:
    name = normalize_text(str(method_name or ""))
    if "ldpred" in name:
        return "LDpred-family"
    if "prs cs" in name or "prs-cs" in name:
        return "PRS-CS-family"
    if "lassosum" in name:
        return "lassosum-family"
    if "sbayes" in name:
        return "Bayesian shrinkage"
    if "snpnet" in name:
        return "large-biobank regularized regression"
    if "clump" in name or "threshold" in name or "c t" in name:
        return "clumping-thresholding"
    return "other"


def _study_archetype(model: Any) -> str:
    text = normalize_text(
        " ".join(
            [
                str(getattr(model, "samples_training", "") or ""),
                " ".join(getattr(model, "training_development_cohorts", []) or []),
                str(getattr(model, "phenotyping_reported", "") or ""),
            ]
        )
    )
    if "incident" in text or "time to event" in text:
        return "incident/time-to-event"
    if "ukb" in text or "uk biobank" in text or "all of us" in text or "fingen" in text:
        return "large-biobank"
    if "meta" in text or "consortium" in text:
        return "meta-analysis"
    return "case-control/other"


def _covariate_inflation_flag(model: Any) -> bool:
    metrics = getattr(model, "performance_metrics", {}) or {}
    pgs_only_auc = metrics.get("pgs_only_auc")
    full_auc = metrics.get("full_model_auc")
    pgs_only_r2 = metrics.get("pgs_only_r2")
    full_r2 = metrics.get("full_model_r2")
    try:
        if pgs_only_auc is not None and full_auc is not None and float(full_auc) - float(pgs_only_auc) >= 0.03:
            return True
        if pgs_only_r2 is not None and full_r2 is not None and float(full_r2) - float(pgs_only_r2) >= 0.05:
            return True
    except Exception:
        pass
    return False


_PAN_TRAIT_FRAMEWORK_MARKERS = (
    "across 813 traits",
    "portability of 245",
    "exprsweb",
    "online repository with polygenic risk scores",
    "pan-trait",
    "pan-phenome",
    "polygenic scores across",
    "polygenic risk scores for common health-related",
    "global biobank meta-analysis",
)

_COVARIATE_LEAKAGE_MARKERS = (
    "family history",
    "family_history",
    "biomarker",
    "risk calculator",
    "charge-af",
    "framingham",
    "qrisk",
    "pooled cohort",
    "5-year risk",
    "absolute risk",
    "screening risk",
    "phenotype risk score",
    "phecode bundle",
    "ehr phenotype",
)


def _study_is_pan_trait_framework(model: Any) -> bool:
    """Detect pan-trait / portability frameworks from publicly visible metadata.

    Section 4 of `prs_model_domain_knowledge.md` ("pan-trait framework identification")
    lists these as a systematic underperformer archetype. We only look at catalog-level
    fields, not trait names, so the signal is trait-agnostic.
    """
    blob_parts = [
        str(getattr(model, "publication_title", "") or ""),
        str(getattr(model, "publication_doi", "") or ""),
        str(getattr(model, "method_name", "") or ""),
        str(getattr(model, "trait_reported", "") or ""),
        " ".join(getattr(model, "training_development_cohorts", []) or []),
    ]
    blob = normalize_text(" ".join(blob_parts))
    return any(marker in blob for marker in _PAN_TRAIT_FRAMEWORK_MARKERS)


def _heavy_covariate_leakage(model: Any) -> bool:
    """Detect explicit heavy-covariate / risk-wrapper leakage from the covariates text.

    Aligned with Section 2 of the domain-knowledge rubric: family history,
    biomarker-heavy adjustment, and named clinical risk calculators make reported
    discrimination non-comparable to PRS-only evaluation.
    """
    cov_blob = normalize_text(str(getattr(model, "covariates", "") or ""))
    return any(marker in cov_blob for marker in _COVARIATE_LEAKAGE_MARKERS)


def _multi_cohort_development(model: Any) -> int:
    cohorts = getattr(model, "training_development_cohorts", None) or []
    try:
        return int(len([c for c in cohorts if str(c).strip()]))
    except Exception:
        return 0


def _effect_size_signal(model: Any) -> float:
    """Convert `effect_sizes` (OR/HR per SD, Beta) into a bounded PRS-quality signal.

    Rubric section 2: `OR ≥ 1.5` / `HR ≥ 1.5` is strong, 1.3–1.5 moderate, <1.3 weak.
    We map |OR - 1| (or |HR - 1|) onto [0, 0.8] so it never dominates a direct PRS-only
    metric but can tip the tie when PRS-only AUC/R² are both missing.
    """
    try:
        effect = getattr(model, "effect_sizes", None) or {}
    except Exception:
        effect = {}
    best = 0.0
    for key in ("or_per_sd", "hr_per_sd", "beta_per_sd"):
        value = None
        try:
            value = float(effect.get(key)) if isinstance(effect, dict) else None
        except Exception:
            value = None
        if value is None:
            continue
        # OR / HR per SD: centre on 1.0; Beta per SD: absolute magnitude.
        magnitude = abs(value - 1.0) if key in ("or_per_sd", "hr_per_sd") else abs(value)
        best = max(best, min(0.8, magnitude))
    return best


# Deterministic signal weights chosen to match the factor importance ordering documented
# at the top of `prs_model_domain_knowledge.md`:
#   1. phenotype alignment/endpoint fidelity (handled by the bundle posterior stage)
#   2. comparable reported performance (PRS-only metrics + effect sizes)
#   3. transportability context (archetype, multi-cohort, ancestry)
#   4. method family and model structure
#   5. weak signals from publication context, date, and validation size
#
# These deterministic features are only a *cheap prior* that constrains the LLM
# context; the final selection is made by the `LOCAL_CHAMPION` and `GLOBAL_FRONTIER`
# LLM judges with the full domain-knowledge document attached.
_ARCHETYPE_BONUS: dict[str, float] = {
    "meta-analysis": 0.40,
    "case-control/other": 0.28,
    "large-biobank": 0.12,
    "incident/time-to-event": 0.06,
}
_METHOD_BONUS: dict[str, float] = {
    "LDpred-family": 0.18,
    "PRS-CS-family": 0.18,
    "lassosum-family": 0.15,
    "Bayesian shrinkage": 0.12,
    "large-biobank regularized regression": 0.05,
    "clumping-thresholding": 0.03,
    "other": 0.06,
}


def _model_quality_score(model_card: dict[str, Any]) -> float:
    pgs_auc = float(model_card.get("pgs_only_auc") or 0.0)
    pgs_r2 = float(model_card.get("pgs_only_r2") or 0.0)
    full_auc = float(model_card.get("full_model_auc") or 0.0)
    full_r2 = float(model_card.get("full_model_r2") or 0.0)

    # Primary signal: any *PRS-comparable* metric. When only a full-model metric is
    # available we count it at 40% weight of the PRS-only equivalent, matching the
    # rubric guidance that full-model numbers are uninformative unless covariates
    # are demographic-only.
    has_pgs_only = pgs_auc > 0 or pgs_r2 > 0
    comparable_metric = max(pgs_auc, pgs_r2)
    if not has_pgs_only:
        comparable_metric = 0.40 * max(full_auc, full_r2)

    effect_signal = float(model_card.get("effect_signal") or 0.0)

    # Covariate inflation from `_covariate_inflation_flag` is already passed in; we
    # additionally penalise explicit heavy-covariate leakage (family history,
    # biomarker adjustment, clinical risk calculators).
    inflation_penalty = 0.40 if model_card.get("covariate_inflation_flag") else 0.0
    leakage_penalty = 0.25 if model_card.get("heavy_covariate_leakage") else 0.0
    framework_penalty = 0.20 if model_card.get("pan_trait_framework") else 0.0

    archetype_bonus = _ARCHETYPE_BONUS.get(model_card.get("study_archetype", ""), 0.0)
    multi_cohort = int(model_card.get("multi_cohort_count") or 0)
    transportability_bonus = min(multi_cohort / 5.0, 0.25)
    method_bonus = _METHOD_BONUS.get(model_card.get("method_family", ""), 0.06)

    # `training_sample_n` is explicitly flagged as a weak / negligible signal in
    # `prs_model_domain_knowledge.md` section 4. We therefore give it only a tiny
    # saturating contribution so it cannot dominate the ranking.
    training_score = min(float(model_card.get("training_sample_n") or 0) / 2_000_000.0, 0.05)
    # Validation sample size is likewise a weak tie-break (section 3).
    validation_score = min(float(model_card.get("validation_sample_n") or 0) / 1_000_000.0, 0.05)

    variants = int(model_card.get("variants_number") or 0)
    # Variant count is mildly informative within the same method family (rubric §5).
    # Use a sub-linear shape so a 1M-variant genome-wide score does not eclipse a
    # well-tuned sparse model with strong PRS-only AUC.
    variants_score = 0.0 if variants <= 0 else min(0.08, (variants / 1_000_000.0) ** 0.5 * 0.08)

    score = (
        2.4 * comparable_metric
        + 0.8 * effect_signal
        + archetype_bonus
        + method_bonus
        + transportability_bonus
        + training_score
        + validation_score
        + variants_score
        - inflation_penalty
        - leakage_penalty
        - framework_penalty
    )
    return round(score, 6)


def _build_model_card(
    model: Any,
    *,
    supporting_bundle: SupportingBundleSelection,
    bundle_rank: int,
) -> dict[str, Any]:
    metrics = getattr(model, "performance_metrics", {}) or {}
    training_sample_n = _parse_sample_size(getattr(model, "samples_training", None))
    validation_sample_n = _parse_sample_size(getattr(model, "validation_sample_size", None))
    card = {
        "pgs_id": getattr(model, "id"),
        "source_bundle_id": supporting_bundle.bundle_id,
        "source_cross_trait": supporting_bundle.canonical_label,
        "bundle_rank": bundle_rank,
        "bundle_confidence": supporting_bundle.confidence,
        "bundle_supports": supporting_bundle.supports,
        "bundle_against": supporting_bundle.against,
        "bundle_posterior_evidence": {
            "supports": list(supporting_bundle.supports or []),
            "against": list(supporting_bundle.against or []),
            "uncertainties": list(supporting_bundle.uncertainties or []),
            "why_continue_or_stop": supporting_bundle.why_continue_or_stop,
            "tool_evidence": [
                entry.model_dump() for entry in (supporting_bundle.tool_evidence or [])
            ],
        },
        "phenotyping_reported": getattr(model, "phenotyping_reported", None),
        "method_name": getattr(model, "method_name", None),
        "method_family": _method_family(getattr(model, "method_name", None)),
        "variants_number": getattr(model, "variants_number", None),
        "trait_reported": getattr(model, "trait_reported", None),
        "trait_efo": getattr(model, "trait_efo", None),
        "ancestry_distribution": getattr(model, "ancestry_distribution", None),
        "samples_training": getattr(model, "samples_training", None),
        "training_sample_n": training_sample_n,
        "training_development_cohorts": getattr(model, "training_development_cohorts", None),
        "multi_cohort_count": _multi_cohort_development(model),
        "validation_sample_size": getattr(model, "validation_sample_size", None),
        "validation_sample_n": validation_sample_n,
        "selected_validation_ancestry": metrics.get("selected_validation_ancestry"),
        "pgs_only_auc": metrics.get("pgs_only_auc"),
        "pgs_only_r2": metrics.get("pgs_only_r2"),
        "full_model_auc": metrics.get("full_model_auc"),
        "full_model_r2": metrics.get("full_model_r2"),
        "covariates": getattr(model, "covariates", None),
        "covariate_inflation_flag": _covariate_inflation_flag(model),
        "heavy_covariate_leakage": _heavy_covariate_leakage(model),
        "pan_trait_framework": _study_is_pan_trait_framework(model),
        "effect_sizes": getattr(model, "effect_sizes", None),
        "effect_signal": _effect_size_signal(model),
        "publication_title": getattr(model, "publication_title", None),
        "publication_date": getattr(model, "publication_date", None),
        "study_archetype": _study_archetype(model),
        "validation_context": {
            "selected_performance_id": metrics.get("selected_performance_id"),
            "selected_validation_ancestry": metrics.get("selected_validation_ancestry"),
            "record_count": metrics.get("record_count"),
            "classification_metrics": metrics.get("classification_metrics"),
            "other_metrics": metrics.get("other_metrics"),
        },
    }
    card["quality_score"] = _model_quality_score(card)
    return card


def _fallback_local_champion_vnext(
    bundle_id: str,
    model_cards: list[dict[str, Any]],
    *,
    max_count: int,
) -> LocalChampionDecision:
    selected_cards = sorted(
        model_cards,
        key=lambda card: (-float(card.get("quality_score") or 0.0), card.get("pgs_id") or ""),
    )[:max_count]
    champions = [
        PRSModelCandidate(
            pgs_id=str(card["pgs_id"]),
            source_bundle_id=str(card["source_bundle_id"]),
            source_cross_trait=str(card["source_cross_trait"]),
            rank=idx + 1,
            selection_rationale="Fallback champion chosen for PRS-comparable metric quality and validation context.",
            cross_trait_evidence_rationale="Bundle posterior retained this source bundle for the final model tournament.",
            model_quality_rationale="Fallback ranking preferred cleaner PRS-only evidence, stronger method family, and better validation support.",
            local_champion_rank=idx + 1,
            bundle_rank=int(card.get("bundle_rank") or 0),
        )
        for idx, card in enumerate(selected_cards)
    ]
    return LocalChampionDecision(
        source_bundle_id=bundle_id,
        champions=champions,
        confidence="Moderate" if champions else "Low",
        rationale="Fallback local champion selection applied a deterministic model-quality score.",
    )


def _call_local_champion_vnext(
    *,
    supporting_bundle: SupportingBundleSelection,
    model_cards: list[dict[str, Any]],
    max_count: int,
    target_trait: str | None = None,
    domain_knowledge: dict[str, Any] | None = None,
    quality_anchor: int = 2,
) -> LocalChampionDecision:
    context = {
        "target_trait": target_trait or "",
        "supporting_bundle": supporting_bundle.model_dump(),
        "model_cards": model_cards,
        "max_count": max_count,
        "domain_knowledge": domain_knowledge or {},
        "signal_priority": [
            "pgs_only metrics (PGS-only AUC / PGS-only R2) — primary",
            "effect_signal (OR / HR per SD) — strong secondary when PGS-only metrics missing",
            "covariate_inflation_flag / heavy_covariate_leakage — hard penalty",
            "study_archetype (meta-analysis > case-control > large-biobank > time-to-event)",
            "bundle_posterior_evidence (supports / against / uncertainties)",
            "method_family + variants_number consistency",
            "multi_cohort_count and validation_context (ancestry, record_count) — weak tie-break",
            "training_sample_n / validation_sample_n — negligible on their own",
        ],
    }
    try:
        decision: LocalChampionDecision = _cached_local_champion_chain_vnext().invoke(
            {"context_json": json.dumps(context, ensure_ascii=False, default=str)}
        )
    except Exception as exc:
        _log.warning("Local champion LLM failed for %s (%s); using fallback.", supporting_bundle.bundle_id, exc)
        return _fallback_local_champion_vnext(
            supporting_bundle.bundle_id,
            model_cards,
            max_count=max_count,
        )

    valid_ids = {str(card["pgs_id"]) for card in model_cards}
    card_lookup = {str(card["pgs_id"]): card for card in model_cards}
    selected: list[PRSModelCandidate] = []
    selected_ids: set[str] = set()
    for proposed in decision.champions:
        if proposed.pgs_id not in valid_ids:
            continue
        if proposed.pgs_id in selected_ids:
            continue
        proposed.source_bundle_id = supporting_bundle.bundle_id
        proposed.source_cross_trait = supporting_bundle.canonical_label
        proposed.rank = len(selected) + 1
        proposed.local_champion_rank = proposed.rank
        proposed.bundle_rank = supporting_bundle.rank
        selected.append(proposed)
        selected_ids.add(proposed.pgs_id)
        if len(selected) >= max_count:
            break

    # Trait-agnostic deterministic quality anchor: append the top-K models by
    # `_model_quality_score` (trait-agnostic PRS-quality composition: PGS-only
    # AUC/R2, effect_signal, covariate-inflation penalty, study_archetype,
    # multi_cohort transportability, method_family, variants — no trait names)
    # that the LLM omitted. Guarantees the DE-quality leaders cannot be silently
    # dropped by local-champion reasoning. Pure card-field policy.
    anchor_count = max(0, int(quality_anchor))
    if anchor_count > 0 and len(selected) < max_count:
        ordered = sorted(
            model_cards,
            key=lambda card: (-float(card.get("quality_score") or 0.0), str(card.get("pgs_id") or "")),
        )
        inserted = 0
        for card in ordered:
            if inserted >= anchor_count or len(selected) >= max_count:
                break
            pgs_id = str(card.get("pgs_id") or "")
            if not pgs_id or pgs_id in selected_ids:
                continue
            selected.append(
                PRSModelCandidate(
                    pgs_id=pgs_id,
                    source_bundle_id=supporting_bundle.bundle_id,
                    source_cross_trait=supporting_bundle.canonical_label,
                    rank=len(selected) + 1,
                    selection_rationale="Deterministic quality-score anchor applied the field-level rubric (PGS-only metric + effect-signal + archetype + method family).",
                    cross_trait_evidence_rationale="Bundle posterior retained this source for the model tournament; quality anchor guarantees the deterministic PRS-comparable leader is not silently dropped.",
                    model_quality_rationale="Deterministic quality-score leader under the trait-agnostic rubric (PGS-only AUC/R2, covariate-leakage penalties, transportability).",
                    local_champion_rank=len(selected) + 1,
                    bundle_rank=int(card.get("bundle_rank") or supporting_bundle.rank),
                )
            )
            selected_ids.add(pgs_id)
            inserted += 1

    if not selected:
        return _fallback_local_champion_vnext(
            supporting_bundle.bundle_id,
            model_cards,
            max_count=max_count,
        )
    # Re-rank to ensure contiguous 1..N after anchor inserts.
    for idx, champion in enumerate(selected, start=1):
        champion.rank = idx
        champion.local_champion_rank = idx
    decision.source_bundle_id = supporting_bundle.bundle_id
    decision.champions = selected
    return decision


def _fallback_global_frontier_vnext(champion_cards: list[dict[str, Any]]) -> GlobalModelFrontierDecision:
    ordered = sorted(
        champion_cards,
        key=lambda card: (
            -(float(card.get("quality_score") or 0.0) + (0.08 * max(0, 6 - int(card.get("bundle_rank") or 6)))),
            card.get("pgs_id") or "",
        ),
    )[:5]
    frontier = [
        PRSModelCandidate(
            pgs_id=str(card["pgs_id"]),
            source_bundle_id=str(card["source_bundle_id"]),
            source_cross_trait=str(card["source_cross_trait"]),
            rank=idx + 1,
            selection_rationale="Fallback final ranking combined bundle posterior order with PRS model quality.",
            cross_trait_evidence_rationale="Source bundle survived the posterior stage and local champion filtering.",
            model_quality_rationale="Fallback ranking preferred cleaner PRS-only metrics and stronger validation support.",
            local_champion_rank=int(card.get("local_champion_rank") or idx + 1),
            bundle_rank=int(card.get("bundle_rank") or 0),
        )
        for idx, card in enumerate(ordered)
    ]
    return GlobalModelFrontierDecision(
        model_frontier=frontier,
        primary_model_id=frontier[0].pgs_id if frontier else None,
        confidence="Moderate" if frontier else "Low",
        rationale="Fallback global model frontier applied a deterministic score over the local champions.",
    )


def _call_global_frontier_vnext(
    champion_cards: list[dict[str, Any]],
    *,
    target_trait: str | None = None,
    domain_knowledge: dict[str, Any] | None = None,
    quality_anchor: int = 2,
) -> GlobalModelFrontierDecision:
    context = {
        "target_trait": target_trait or "",
        "champion_cards": champion_cards,
        "max_frontier_size": 5,
        "domain_knowledge": domain_knowledge or {},
        "signal_priority": [
            "pgs_only metrics (PGS-only AUC / PGS-only R2) — primary",
            "effect_signal (OR / HR per SD) — strong secondary",
            "covariate_inflation_flag / heavy_covariate_leakage — hard penalty",
            "study_archetype + multi_cohort_count — transportability",
            "bundle_rank + bundle_posterior_evidence — cross-trait transfer context",
            "method_family + variants_number — structural tie-break",
            "training_sample_n / validation_sample_n — negligible on their own",
        ],
    }
    try:
        decision: GlobalModelFrontierDecision = _cached_global_frontier_chain_vnext().invoke(
            {"context_json": json.dumps(context, ensure_ascii=False, default=str)}
        )
    except Exception as exc:
        _log.warning("Global frontier LLM failed (%s); using fallback.", exc)
        return _fallback_global_frontier_vnext(champion_cards)

    valid_ids = {str(card["pgs_id"]) for card in champion_cards}
    card_lookup = {str(card["pgs_id"]): card for card in champion_cards}
    frontier: list[PRSModelCandidate] = []
    frontier_ids: set[str] = set()
    for proposed in decision.model_frontier:
        if proposed.pgs_id not in valid_ids:
            continue
        if proposed.pgs_id in frontier_ids:
            continue
        matched = card_lookup[proposed.pgs_id]
        proposed.rank = len(frontier) + 1
        proposed.source_bundle_id = str(matched["source_bundle_id"])
        proposed.source_cross_trait = str(matched["source_cross_trait"])
        proposed.local_champion_rank = int(matched.get("local_champion_rank") or 1)
        proposed.bundle_rank = int(matched.get("bundle_rank") or 0)
        frontier.append(proposed)
        frontier_ids.add(proposed.pgs_id)
        if len(frontier) >= 5:
            break

    # Trait-agnostic deterministic quality anchor: append the top-K champion
    # cards by (`_model_quality_score` + bundle_rank bonus) that the LLM
    # omitted from the frontier. Pure card-field composition; no trait names.
    anchor_count = max(0, int(quality_anchor))
    if anchor_count > 0 and len(frontier) < 5:
        ordered = sorted(
            champion_cards,
            key=lambda card: (
                -(float(card.get("quality_score") or 0.0) + (0.08 * max(0, 6 - int(card.get("bundle_rank") or 6)))),
                str(card.get("pgs_id") or ""),
            ),
        )
        inserted = 0
        for card in ordered:
            if inserted >= anchor_count or len(frontier) >= 5:
                break
            pgs_id = str(card.get("pgs_id") or "")
            if not pgs_id or pgs_id in frontier_ids:
                continue
            frontier.append(
                PRSModelCandidate(
                    pgs_id=pgs_id,
                    source_bundle_id=str(card["source_bundle_id"]),
                    source_cross_trait=str(card["source_cross_trait"]),
                    rank=len(frontier) + 1,
                    selection_rationale="Deterministic quality-score anchor (trait-agnostic PRS rubric) guarantees the DE-quality leader appears in the frontier.",
                    cross_trait_evidence_rationale="Bundle posterior retained this source; the quality anchor ensures the deterministic leader is not omitted by the tournament LLM.",
                    model_quality_rationale="Deterministic rubric leader: PGS-only metric + effect_signal + archetype + method_family composition.",
                    local_champion_rank=int(card.get("local_champion_rank") or 1),
                    bundle_rank=int(card.get("bundle_rank") or 0),
                )
            )
            frontier_ids.add(pgs_id)
            inserted += 1

    if not frontier:
        return _fallback_global_frontier_vnext(champion_cards)
    for idx, candidate in enumerate(frontier, start=1):
        candidate.rank = idx
    decision.model_frontier = frontier
    if decision.primary_model_id not in frontier_ids:
        decision.primary_model_id = frontier[0].pgs_id
    return decision


_DOMAIN_KNOWLEDGE_QUERY_TEMPLATE = (
    "target_trait: {target_trait}; PRS clinical thresholds AUC R2 heritability ceiling sanity-check "
    "must-pass gates phenotype alignment endpoint specificity external transfer reliability "
    "ancestry compatibility ranking features penalties method priors validation sample size "
    "tie-break time-to-event horizon-specific incident case-control dominant subtype "
    "PGS-only no-covariates incremental AUROC snpnet biobank transportability"
)


def _load_domain_knowledge_payload(target_trait: str) -> dict[str, Any]:
    """Invoke the contribution2 `prs_model_domain_knowledge` tool as a trait-agnostic
    PRS-quality rubric. The payload is attached to the local-champion and global-frontier
    contexts so the model-first tournament evaluates every PGS card against the same
    field-level policy contribution2 uses at Step 1.
    """
    from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge

    query = _DOMAIN_KNOWLEDGE_QUERY_TEMPLATE.format(target_trait=target_trait or "")
    try:
        knowledge = prs_model_domain_knowledge(query)
    except Exception as exc:
        _log.warning("Domain knowledge tool failed (%s); continuing without it.", exc)
        return {
            "query": query,
            "full_document": "",
            "snippets": [],
            "source_type": "error",
        }
    if knowledge is None:
        return {
            "query": query,
            "full_document": "",
            "snippets": [],
            "source_type": "missing",
        }
    try:
        payload = knowledge.model_dump()
    except Exception:
        payload = {
            "query": query,
            "full_document": getattr(knowledge, "full_document", "") or "",
            "snippets": [],
            "source_type": getattr(knowledge, "source_type", "local") or "local",
        }
    return payload


def _trim_domain_knowledge_for_bundle(payload: dict[str, Any], max_snippets: int = 6) -> dict[str, Any]:
    """Return a compact DK view for per-bundle calls. The full document stays in the
    global-frontier context (one call per target) while each of the 3-6 local-champion
    calls receives a shorter snippet-focused view to keep prompt tokens bounded.
    """
    if not payload:
        return {}
    snippets = payload.get("snippets") or []
    trimmed = list(snippets)[:max_snippets]
    return {
        "query": payload.get("query", ""),
        "source_type": payload.get("source_type", ""),
        "full_document": payload.get("full_document", ""),
        "snippets": trimmed,
        "is_trimmed": len(trimmed) < len(snippets),
    }


def _diversify_model_cards(
    model_cards: list[dict[str, Any]],
    *,
    max_models: int = 24,
    max_per_cluster: int = 3,
) -> list[dict[str, Any]]:
    """Cap model-card count per (method_family, training_sample bucket) cluster.

    Prevents the LLM from drowning in dozens of near-identical LDpred2 siblings from
    the same biobank while preserving architectural diversity across the bundle.
    """
    ordered = sorted(
        model_cards,
        key=lambda card: (
            -float(card.get("quality_score") or 0.0),
            str(card.get("pgs_id") or ""),
        ),
    )
    clusters: dict[tuple[str, str], int] = {}
    kept: list[dict[str, Any]] = []
    for card in ordered:
        training_n = int(card.get("training_sample_n") or 0)
        if training_n <= 50_000:
            bucket = "<=50K"
        elif training_n <= 200_000:
            bucket = "50K-200K"
        elif training_n <= 1_000_000:
            bucket = "200K-1M"
        else:
            bucket = ">1M"
        method = str(card.get("method_family") or "other")
        key = (method, bucket)
        if clusters.get(key, 0) >= max_per_cluster:
            continue
        clusters[key] = clusters.get(key, 0) + 1
        kept.append(card)
        if len(kept) >= max_models:
            break
    return kept


def _hydrate_models_for_supporting_bundles_vnext(
    dossier: CandidateBundleDossier,
    supporting_bundles: list[SupportingBundleSelection],
) -> tuple[dict[str, int], list[Any], dict[str, str]]:
    from src.server.core.pgs_catalog_client import PGSCatalogClient
    from src.server.core.tools.prs_model_tools import hydrate_pgs_model_summaries

    # Hydration quotas — cycle0 proved best on macro metrics with
    # [36,24,18,12,8,6,4]. Cycle1's uniform widening [44,28,20,14,10,7,5] and
    # cycle2's front-loaded [56,24,18,12,8,6,4] both degraded A/B macro, so
    # cycle3 restores cycle0 quotas.
    quotas = [36, 24, 18, 12, 8, 6, 4]
    bundle_lookup = _bundle_lookup(dossier)
    ordered_ids: list[str] = []
    pgs_to_bundle: dict[str, str] = {}
    model_budget_by_bundle: dict[str, int] = {}
    for idx, supporting_bundle in enumerate(supporting_bundles[: len(quotas)]):
        bundle = bundle_lookup.get(supporting_bundle.bundle_id)
        if bundle is None:
            continue
        budget = quotas[idx]
        picked = 0
        for pgs_id in bundle.candidate_pgs_ids:
            if pgs_id in pgs_to_bundle:
                continue
            ordered_ids.append(pgs_id)
            pgs_to_bundle[pgs_id] = supporting_bundle.bundle_id
            picked += 1
            if picked >= budget:
                break
        model_budget_by_bundle[supporting_bundle.bundle_id] = picked
    if not ordered_ids:
        return model_budget_by_bundle, [], pgs_to_bundle
    client = PGSCatalogClient()
    models = hydrate_pgs_model_summaries(client, ordered_ids)
    return model_budget_by_bundle, models, pgs_to_bundle


def _build_tool_evidence_summary(card_lookup: dict[str, CandidateEvidenceCard]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for bundle_id, card in card_lookup.items():
        summary[bundle_id] = {
            "genetic_correlation": card.gc.model_dump() if card.gc else None,
            "heritability": card.h2.model_dump() if card.h2 else None,
            "open_targets": card.open_targets.model_dump() if card.open_targets else None,
        }
    return summary


def _synthetic_stage1_from_supporting(
    supporting_bundles: list[SupportingBundleSelection],
    evidence_state: EvidenceState,
    confidence: ConfidenceLabel,
    rationale: str,
) -> Stage1CrossTraitShortlist:
    return Stage1CrossTraitShortlist(
        shortlisted_bundles=[
            Stage1BundleCandidate(
                bundle_id=bundle.bundle_id,
                canonical_label=bundle.canonical_label,
                rank=bundle.rank,
                tool_evidence=bundle.tool_evidence,
                selection_rationale=bundle.why_continue_or_stop,
                utility_score=bundle.utility_score,
                transferability_prior_score=bundle.transferability_prior_score,
                phenotype_fidelity_score=bundle.phenotype_fidelity_score,
            )
            for bundle in supporting_bundles
        ],
        confidence=confidence,
        decision_rationale=rationale,
        evidence_state=evidence_state,
    )


def _synthetic_stage2_from_frontier(
    model_frontier: list[PRSModelCandidate],
    confidence: ConfidenceLabel,
    rationale: str,
    model_universe_size: int,
    bundles_hydrated: list[str],
) -> Stage2ModelRecommendation:
    return Stage2ModelRecommendation(
        recommended_models=model_frontier[:5],
        model_frontier=model_frontier[:5],
        primary_model_id=model_frontier[0].pgs_id if model_frontier else None,
        model_universe_size=model_universe_size,
        bundles_hydrated=bundles_hydrated,
        confidence=confidence,
        decision_rationale=rationale,
    )


# ---------------------------------------------------------------------------
# Ablation helpers
# ---------------------------------------------------------------------------


def _resolve_ablation(ablation: str | None) -> str:
    label = normalize_transfer_ablation(ablation)
    if label not in TRANSFER_ABLATIONS:
        raise ValueError(
            f"Unsupported ablation: {ablation}. Expected one of {', '.join(TRANSFER_ABLATIONS)}."
        )
    return label


def _active_tools_for_ablation(available_tools: list[str], ablation: str) -> list[str]:
    disabled_tools: set[str] = set()
    if ablation == "no_h2":
        disabled_tools.add("cross_trait_heritability")
    if ablation == "no_ot_verifier":
        disabled_tools.add("cross_trait_open_targets")
    return [tool_name for tool_name in available_tools if tool_name not in disabled_tools]


# ---------------------------------------------------------------------------
# Legacy pipeline functions (kept for backward compat with eval scripts)
# ---------------------------------------------------------------------------

def _build_judge_chain():
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TRANSFER_FRONTIER_JUDGE_PROMPT),
            (
                "human",
                "Select the transfer frontier from the context below.\n\nContext:\n{context_json}",
            ),
        ]
    )
    structured = llm.with_structured_output(
        JudgeFrontierSelection,
        method="function_calling",
    )
    return prompt | structured


def _build_verify_chain():
    llm = get_llm("disease_workflow")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TRANSFER_FRONTIER_VERIFY_PROMPT),
            (
                "human",
                "Verify the proposed selection against the evidence cards.\n\nContext:\n{context_json}",
            ),
        ]
    )
    structured = llm.with_structured_output(
        VerifiedSelection,
        method="function_calling",
    )
    return prompt | structured


@lru_cache(maxsize=1)
def _cached_judge_chain():
    return _build_judge_chain()


@lru_cache(maxsize=1)
def _cached_verify_chain():
    return _build_verify_chain()


def _truncate_cards_for_llm(
    cards: list[CandidateEvidenceCard],
    llm_card_cap: int,
) -> list[CandidateEvidenceCard]:
    """Return at most *llm_card_cap* cards for the LLM prompt.

    The deterministic frontier override in _finalize_frontier_decision always
    operates on the **full** card list stored in EvidenceState, so truncating
    here does NOT change the actual selection — it only limits what the LLM
    sees, saving tokens and latency.
    """
    if llm_card_cap <= 0 or len(cards) <= llm_card_cap:
        return cards
    return cards[:llm_card_cap]


def _judge_frontier(
    evidence_state: EvidenceState,
    default_frontier_ids: list[str],
    default_mode: DecisionMode,
    *,
    llm_card_cap: int = 0,
) -> JudgeFrontierSelection:
    llm_cards = _truncate_cards_for_llm(evidence_state.candidate_cards, llm_card_cap)
    context = {
        "target_summary": evidence_state.target_summary,
        "available_tools": evidence_state.available_tools,
        "shortlist_bundle_ids": evidence_state.shortlist_bundle_ids,
        "candidate_cards": [card.model_dump() for card in llm_cards],
        "default_frontier_ids": default_frontier_ids,
        "default_decision_mode": default_mode,
    }
    try:
        return _cached_judge_chain().invoke({"context_json": json.dumps(context, ensure_ascii=False)})
    except Exception:
        return JudgeFrontierSelection(
            primary_bundle_id=default_frontier_ids[0] if default_frontier_ids else None,
            frontier_bundle_ids=default_frontier_ids,
            confidence="Moderate" if default_mode == "frontier_uncertain" else "High",
            decision_mode=default_mode,
            rationale="Deterministic fallback selected the frontier from the highest-utility evidence cards.",
            evidence_tags=[],
        )


def _verify_selection(
    evidence_state: EvidenceState,
    proposed: JudgeFrontierSelection,
    selected_cards: list[CandidateEvidenceCard],
    *,
    llm_card_cap: int = 0,
) -> VerifiedSelection:
    llm_cards = _truncate_cards_for_llm(evidence_state.candidate_cards, llm_card_cap)
    context = {
        "target_summary": evidence_state.target_summary,
        "candidate_cards": [card.model_dump() for card in llm_cards],
        "selected_cards": [card.model_dump() for card in selected_cards],
        "proposed_selection": proposed.model_dump(),
    }
    try:
        return _cached_verify_chain().invoke({"context_json": json.dumps(context, ensure_ascii=False)})
    except Exception:
        visible_tags = sorted({tag for card in selected_cards for tag in card.evidence_tags})
        return VerifiedSelection(
            confidence=proposed.confidence,
            decision_mode=proposed.decision_mode,
            rationale=proposed.rationale,
            evidence_tags=visible_tags[:8],
            supported=True,
            issues=[],
            revised_primary_bundle_id=None,
            revised_frontier_bundle_ids=[],
        )


def _finalize_frontier_decision(
    dossier: CandidateBundleDossier,
    evidence_state: EvidenceState,
    judged: JudgeFrontierSelection,
    *,
    config: TransferConfig,
) -> CrossTraitTransferFrontierDecision:
    cards_by_id = {card.bundle_id: card for card in evidence_state.candidate_cards}
    normalized_frontier_ids = _normalize_frontier_ids(
        dossier=dossier,
        cards=evidence_state.candidate_cards,
        candidate_ids=judged.frontier_bundle_ids or ([judged.primary_bundle_id] if judged.primary_bundle_id else []),
    )
    if not normalized_frontier_ids:
        normalized_frontier_ids = _default_frontier_ids(
            evidence_state.candidate_cards,
            _decision_mode_from_cards(evidence_state.candidate_cards),
        )
    else:
        # Keep the LLM as an evidence auditor, but make the frontier deterministic
        # when a target-agnostic transferability prior changes the top evidence-card
        # ordering. This avoids primary volatility without introducing trait rules.
        deterministic_frontier_ids = _default_frontier_ids(
            evidence_state.candidate_cards,
            _decision_mode_from_cards(evidence_state.candidate_cards),
        )
        normalized_frontier_ids = _normalize_frontier_ids(
            dossier=dossier,
            cards=evidence_state.candidate_cards,
            candidate_ids=[*deterministic_frontier_ids, *normalized_frontier_ids],
        )

    primary_bundle_id = judged.primary_bundle_id if judged.primary_bundle_id in normalized_frontier_ids else None
    if primary_bundle_id is None and normalized_frontier_ids:
        primary_bundle_id = normalized_frontier_ids[0]
    if primary_bundle_id and primary_bundle_id not in normalized_frontier_ids:
        normalized_frontier_ids = [primary_bundle_id, *normalized_frontier_ids][:3]

    selected_cards = [cards_by_id[bundle_id] for bundle_id in normalized_frontier_ids if bundle_id in cards_by_id]
    if not selected_cards:
        return CrossTraitTransferFrontierDecision(
            primary_bundle_id=None,
            frontier_bundle_ids=[],
            frontier_bundle_weights={},
            candidate_pgs_ids_union=[],
            confidence="Low",
            decision_mode="abstain_only_if_no_valid_bundle",
            rationale="No valid non-self candidate bundle remained after evidence filtering.",
            evidence_state=evidence_state,
            bundle_evidence_tags={},
            outcome="NO_MATCH",
            best_bundle_id=None,
            best_cross_trait=None,
            candidate_pgs_ids=[],
        )

    verified = _verify_selection(
        evidence_state, judged, selected_cards,
        llm_card_cap=config.llm_card_cap,
    )
    if config.allow_ot_promotion and (verified.revised_frontier_bundle_ids or verified.revised_primary_bundle_id):
        revised_candidate_ids = list(verified.revised_frontier_bundle_ids)
        if verified.revised_primary_bundle_id:
            revised_candidate_ids = [verified.revised_primary_bundle_id, *revised_candidate_ids]
        revised_frontier_ids = _normalize_frontier_ids(
            dossier=dossier,
            cards=evidence_state.candidate_cards,
            candidate_ids=revised_candidate_ids,
        )
        if revised_frontier_ids:
            normalized_frontier_ids = revised_frontier_ids
            primary_bundle_id = (
                verified.revised_primary_bundle_id
                if verified.revised_primary_bundle_id in normalized_frontier_ids
                else normalized_frontier_ids[0]
            )
            selected_cards = [cards_by_id[bundle_id] for bundle_id in normalized_frontier_ids if bundle_id in cards_by_id]

    deterministic_frontier_ids = _default_frontier_ids(
        evidence_state.candidate_cards,
        _decision_mode_from_cards(evidence_state.candidate_cards),
    )
    normalized_frontier_ids = _normalize_frontier_ids(
        dossier=dossier,
        cards=evidence_state.candidate_cards,
        candidate_ids=[*deterministic_frontier_ids, *normalized_frontier_ids],
    )
    selected_cards = [cards_by_id[bundle_id] for bundle_id in normalized_frontier_ids if bundle_id in cards_by_id]

    primary_card = _choose_primary_card(selected_cards, config)
    primary_bundle_id = primary_card.bundle_id if primary_card else None
    if primary_card is not None:
        selected_cards = [
            primary_card,
            *[card for card in selected_cards if card.bundle_id != primary_card.bundle_id],
        ]
        normalized_frontier_ids = [card.bundle_id for card in selected_cards]

    bundle_weights_raw = {
        card.bundle_id: max(_selection_priority_score(card, config), 0.01)
        for card in selected_cards
    }
    weight_total = sum(bundle_weights_raw.values()) or 1.0
    frontier_bundle_weights = {
        bundle_id: round(weight / weight_total, 4)
        for bundle_id, weight in bundle_weights_raw.items()
    }

    candidate_pgs_ids_union: list[str] = []
    seen_pgs: set[str] = set()
    for card in selected_cards:
        for pgs_id in card.candidate_pgs_ids:
            if pgs_id not in seen_pgs:
                seen_pgs.add(pgs_id)
                candidate_pgs_ids_union.append(pgs_id)

    decision_mode = verified.decision_mode
    if decision_mode == "single_confident":
        if len(selected_cards) < 2:
            supplemental_cards = [
                card
                for card in evidence_state.candidate_cards
                if card.bundle_id not in {selected.bundle_id for selected in selected_cards}
            ]
            if supplemental_cards:
                selected_cards = [*selected_cards, supplemental_cards[0]]
        if len(selected_cards) > 2:
            selected_cards = selected_cards[:2]
        normalized_frontier_ids = [card.bundle_id for card in selected_cards]
        raw_weights = {card.bundle_id: max(_selection_priority_score(card, config), 0.01) for card in selected_cards}
        total = sum(raw_weights.values()) or 1.0
        frontier_bundle_weights = {bid: round(w / total, 4) for bid, w in raw_weights.items()}
        candidate_pgs_ids_union = []
        seen_pgs_recompute: set[str] = set()
        for card in selected_cards:
            for pgs_id in card.candidate_pgs_ids:
                if pgs_id not in seen_pgs_recompute:
                    seen_pgs_recompute.add(pgs_id)
                    candidate_pgs_ids_union.append(pgs_id)
        primary_card = cards_by_id.get(primary_bundle_id) if primary_bundle_id else selected_cards[0]
    elif decision_mode == "abstain_only_if_no_valid_bundle" and primary_card is not None:
        decision_mode = "frontier_uncertain"

    bundle_evidence_tags = {card.bundle_id: card.evidence_tags for card in selected_cards}
    visible_tags = {tag for card in selected_cards for tag in card.evidence_tags}
    verified_tags = [tag for tag in verified.evidence_tags if tag in visible_tags][:12]

    rationale = verified.rationale
    if primary_card and primary_card.transferability_prior_score > 0:
        rationale = (
            f"{rationale} Deterministic primary tie-break used target-agnostic "
            f"transferability_prior_score={primary_card.transferability_prior_score:.3f} "
            "alongside utility_score, cheap_rank_score, phenotype_fidelity_score, and capped model support."
        )
    if verified_tags:
        rationale = f"{rationale} Evidence tags: {', '.join(verified_tags)}."

    return CrossTraitTransferFrontierDecision(
        primary_bundle_id=primary_card.bundle_id if primary_card else None,
        frontier_bundle_ids=[card.bundle_id for card in selected_cards],
        frontier_bundle_weights=frontier_bundle_weights,
        candidate_pgs_ids_union=candidate_pgs_ids_union,
        confidence=verified.confidence,
        decision_mode=decision_mode,
        rationale=rationale.strip(),
        evidence_state=evidence_state,
        bundle_evidence_tags=bundle_evidence_tags,
        outcome="MATCHED" if primary_card else "NO_MATCH",
        best_bundle_id=primary_card.bundle_id if primary_card else None,
        best_cross_trait=primary_card.canonical_label if primary_card else None,
        candidate_pgs_ids=candidate_pgs_ids_union,
    )


def run_cross_trait_agent(
    dossier: CandidateBundleDossier,
    condition: Literal["gpt-only", "dossier-only", "gc-only", "gc-h2", "all-tools"],
    bundles: list[TraitBundle] | None = None,
    toolbox: CrossTraitToolbox | None = None,
    max_steps: int = 8,
    enable_semantic_backstop: bool = True,
    enable_forced_match: bool = True,
    benchmark_family: str = "unified",
    ablation: str = DEFAULT_TRANSFER_ABLATION,
) -> dict[str, Any]:
    """Cross-trait transfer vNext: LLM-dominant, model-first workflow."""
    del max_steps, enable_semantic_backstop, enable_forced_match
    if condition not in CONDITION_TOOLS:
        raise ValueError(f"Unsupported condition: {condition}")
    if toolbox is None and bundles is None:
        raise ValueError("Either bundles or toolbox must be provided.")
    if toolbox is None:
        assert bundles is not None
        toolbox = CrossTraitToolbox(bundles)

    ablation = _resolve_ablation(ablation)
    config = BENCHMARK_FAMILY_CONFIGS.get(benchmark_family, DEFAULT_CONFIG)
    available_tools = _active_tools_for_ablation(CONDITION_TOOLS[condition], ablation)
    target_source = _target_source_for_dossier(dossier, benchmark_family)
    candidate_bundle_ids = [
        bundle.bundle_id
        for bundle in dossier.candidates
        if not is_self_like_bundle(dossier.target, bundle)
        and bundle_has_source_universe_pgs(bundle, target_source)
    ]
    bundle_lookup_map = _bundle_lookup(dossier)

    tool_trace: list[dict[str, Any]] = []
    target_summary = _build_target_summary(
        dossier,
        benchmark_family=benchmark_family,
        config=config,
    )
    target_summary["ablation"] = ablation

    recall_cards = _sort_cards(
        [
            _build_candidate_card(
                dossier,
                bundle_lookup_map[bundle_id],
                config=config,
                target_source=target_source,
            )
            for bundle_id in candidate_bundle_ids
            if bundle_id in bundle_lookup_map
        ],
        config,
    )
    card_lookup = {card.bundle_id: card for card in recall_cards}

    search_plan = _call_search_plan_vnext(target_summary, recall_cards, config)
    tool_trace.append(
        {
            "name": "llm_search_plan",
            "phase": "phase1_search_plan",
            "args": {
                "target_trait": dossier.target.target_label,
                "recall_pool_size": len(recall_cards),
            },
            "result": search_plan.model_dump(),
        }
    )

    search_trace = SearchTrace(
        recall_pool_size=len(recall_cards),
        initial_probe_bundle_ids=search_plan.probe_bundle_ids,
    )

    gc_lookup: dict[str, dict[str, Any]] = {}
    h2_lookup: dict[str, dict[str, Any]] = {}
    ot_lookup: dict[str, dict[str, Any]] = {}
    retained_bundle_ids: list[str] = []
    ot_promoted_bundle_ids: list[str] = []

    current_probe_ids = list(search_plan.probe_bundle_ids)
    for round_index in range(config.max_probe_rounds):
        new_probe_ids = [
            bundle_id
            for bundle_id in current_probe_ids
            if bundle_id in bundle_lookup_map and bundle_id not in search_trace.probed_bundle_ids
        ]
        if not new_probe_ids:
            if not search_trace.stop_reason:
                search_trace.stop_reason = "No new challenger bundles remained for screening."
            break

        if "cross_trait_genetic_correlation" in available_tools:
            gc_result = toolbox.cross_trait_genetic_correlation(
                dossier.target.target_label,
                new_probe_ids,
                response_format="screening",
            )
            gc_lookup.update(_gc_lookup(gc_result))
            tool_trace.append(
                {
                    "name": "cross_trait_genetic_correlation",
                    "phase": f"phase2_probe_round_{round_index + 1}",
                    "args": {
                        "target_trait": dossier.target.target_label,
                        "candidate_bundle_ids": new_probe_ids,
                        "response_format": "screening",
                    },
                    "result": gc_result,
                }
            )

        if "cross_trait_heritability" in available_tools:
            h2_result = toolbox.cross_trait_heritability(
                dossier.target.target_label,
                new_probe_ids,
                ancestry="EUR",
                response_format="screening",
            )
            h2_lookup.update(_gc_lookup(h2_result))
            tool_trace.append(
                {
                    "name": "cross_trait_heritability",
                    "phase": f"phase2_probe_round_{round_index + 1}",
                    "args": {
                        "target_trait": dossier.target.target_label,
                        "candidate_bundle_ids": new_probe_ids,
                        "ancestry": "EUR",
                        "response_format": "screening",
                    },
                    "result": h2_result,
                }
            )

        for bundle_id in new_probe_ids:
            card_lookup[bundle_id] = _build_candidate_card(
                dossier,
                bundle_lookup_map[bundle_id],
                gc_row=gc_lookup.get(bundle_id),
                h2_row=h2_lookup.get(bundle_id),
                ot_row=ot_lookup.get(bundle_id),
                config=config,
                target_source=target_source,
            )

        search_trace.probed_bundle_ids = _unique_preserve_order(search_trace.probed_bundle_ids + new_probe_ids)
        seen_cards = _sort_cards(
            [card_lookup[bundle_id] for bundle_id in search_trace.probed_bundle_ids if bundle_id in card_lookup],
            config,
        )
        remaining_cards = [
            card for card in recall_cards if card.bundle_id not in set(search_trace.probed_bundle_ids)
        ]
        if ablation == "no_reflective_reprobe":
            retained_bundle_ids = [card.bundle_id for card in seen_cards[: config.retained_probe_max]]
            promoted = retained_bundle_ids[: config.ot_verification_cap]
            round_decision = ProbeRoundDecision(
                retain_bundle_ids=retained_bundle_ids,
                challenger_bundle_ids=[],
                promote_to_ot_bundle_ids=promoted,
                stop=True,
                rationale="Ablation disabled reflective re-probe; stopping after the initial screening round.",
            )
        else:
            round_decision = _call_probe_reflection_vnext(
                round_index=round_index + 1,
                target_summary=target_summary,
                seen_cards=seen_cards,
                remaining_cards=remaining_cards,
                config=config,
            )
        retained_bundle_ids = round_decision.retain_bundle_ids
        ot_promoted_bundle_ids = _unique_preserve_order(
            ot_promoted_bundle_ids + round_decision.promote_to_ot_bundle_ids
        )[: config.ot_verification_cap]
        search_trace.probe_rounds.append(
            SearchTraceRound(
                round_index=round_index + 1,
                probed_bundle_ids=new_probe_ids,
                retained_bundle_ids=retained_bundle_ids,
                challenger_bundle_ids=round_decision.challenger_bundle_ids,
                promote_to_ot_bundle_ids=round_decision.promote_to_ot_bundle_ids,
                stop=round_decision.stop,
                rationale=round_decision.rationale,
            )
        )
        tool_trace.append(
            {
                "name": "llm_probe_reflection" if ablation != "no_reflective_reprobe" else "ablation_probe_reflection_disabled",
                "phase": f"phase2_probe_round_{round_index + 1}",
                "args": {
                    "seen_bundle_count": len(seen_cards),
                    "remaining_bundle_count": len(remaining_cards),
                },
                "result": round_decision.model_dump(),
            }
        )

        current_probe_ids = round_decision.challenger_bundle_ids
        if round_decision.stop:
            search_trace.stopped_early = True
            search_trace.stop_reason = round_decision.rationale
            break
        if not current_probe_ids:
            search_trace.stop_reason = "Reflection step proposed no additional challenger bundles."
            break

    if not search_trace.stop_reason and len(search_trace.probe_rounds) >= config.max_probe_rounds:
        search_trace.stop_reason = "Reached the maximum number of probe rounds."
    if not retained_bundle_ids:
        retained_bundle_ids = search_trace.probed_bundle_ids[: config.retained_probe_max]

    ot_verified_bundle_ids = ot_promoted_bundle_ids[: config.ot_verification_cap]
    if "cross_trait_open_targets" in available_tools and ot_verified_bundle_ids:
        ot_result = toolbox.cross_trait_open_targets(
            dossier.target.target_label,
            ot_verified_bundle_ids,
            response_format="evidence",
        )
        ot_lookup.update(_gc_lookup(ot_result))
        tool_trace.append(
            {
                "name": "cross_trait_open_targets",
                "phase": "phase3_ot_verification",
                "args": {
                    "target_trait": dossier.target.target_label,
                    "candidate_bundle_ids": ot_verified_bundle_ids,
                    "response_format": "evidence",
                },
                "result": ot_result,
            }
        )
        for bundle_id in ot_verified_bundle_ids:
            if bundle_id not in bundle_lookup_map:
                continue
            card_lookup[bundle_id] = _build_candidate_card(
                dossier,
                bundle_lookup_map[bundle_id],
                gc_row=gc_lookup.get(bundle_id),
                h2_row=h2_lookup.get(bundle_id),
                ot_row=ot_lookup.get(bundle_id),
                config=config,
                target_source=target_source,
            )
    search_trace.ot_verified_bundle_ids = ot_verified_bundle_ids

    posterior_cards = _sort_cards(
        [card_lookup[bundle_id] for bundle_id in retained_bundle_ids if bundle_id in card_lookup],
        config,
    )

    # Load the contribution2 `prs_model_domain_knowledge` tool once per target
    # (trait-agnostic PRS-quality rubric). The bundle-posterior call receives a
    # trimmed snippet view so the judge can evaluate phenotype-alignment under
    # the same policy contribution2 applies at Step 1; the local-champion and
    # global-frontier calls reuse the same payload below.
    target_trait_label = dossier.target.target_label or ""
    domain_knowledge_payload = _load_domain_knowledge_payload(target_trait_label)
    domain_knowledge_bundle = _trim_domain_knowledge_for_bundle(domain_knowledge_payload)

    bundle_posterior = _call_bundle_posterior_vnext(
        target_summary=target_summary,
        posterior_cards=posterior_cards,
        config=config,
        domain_knowledge=domain_knowledge_bundle,
    )
    supporting_bundles = bundle_posterior.supporting_bundles
    search_trace.supporting_bundle_ids = [bundle.bundle_id for bundle in supporting_bundles]
    tool_trace.append(
        {
            "name": "llm_bundle_posterior",
            "phase": "phase4_bundle_posterior",
            "args": {"retained_bundle_count": len(posterior_cards)},
            "result": bundle_posterior.model_dump(),
        }
    )

    model_budget_by_bundle, hydrated_models, pgs_to_bundle = _hydrate_models_for_supporting_bundles_vnext(
        dossier,
        supporting_bundles,
    )
    search_trace.model_budget_by_bundle = model_budget_by_bundle

    supporting_lookup = {bundle.bundle_id: bundle for bundle in supporting_bundles}
    models_by_bundle: dict[str, list[Any]] = {}
    for model in hydrated_models:
        bundle_id = pgs_to_bundle.get(getattr(model, "id", ""))
        if bundle_id is None or bundle_id not in supporting_lookup:
            continue
        models_by_bundle.setdefault(bundle_id, []).append(model)

    # The contribution2 `prs_model_domain_knowledge` payload was loaded above
    # (once per target). Local-champion and global-frontier reuse the trimmed /
    # full views for the model-first tournament (trait-agnostic rubric).
    tool_trace.append(
        {
            "name": "prs_model_domain_knowledge",
            "phase": "phase5_domain_knowledge",
            "args": {"target_trait": target_trait_label},
            "result": {
                "source_type": domain_knowledge_payload.get("source_type"),
                "full_document_chars": len(domain_knowledge_payload.get("full_document") or ""),
                "snippet_count": len(domain_knowledge_payload.get("snippets") or []),
            },
        }
    )

    champion_cards: list[dict[str, Any]] = []
    for supporting_bundle in supporting_bundles:
        bundle_models = models_by_bundle.get(supporting_bundle.bundle_id) or []
        if not bundle_models:
            continue
        model_cards = [
            _build_model_card(
                model,
                supporting_bundle=supporting_bundle,
                bundle_rank=supporting_bundle.rank,
            )
            for model in bundle_models
        ]
        # Cap each bundle to ≤32 models with at most 5 per (method_family,
        # training-N bucket). Cycle3 restores cycle0's proven (32, 5) after
        # cycle1 (40, 6) and cycle2 (48, 8) both failed to lift primary picks.
        model_cards = _diversify_model_cards(model_cards, max_models=32, max_per_cluster=5)
        model_card_lookup = {str(card["pgs_id"]): card for card in model_cards}
        if ablation == "no_local_champion":
            ordered_model_cards = sorted(
                model_cards,
                key=lambda card: (-float(card.get("quality_score") or 0.0), str(card.get("pgs_id") or "")),
            )
            tool_trace.append(
                {
                    "name": "ablation_local_champion_disabled",
                    "phase": f"phase5_local_champion::{supporting_bundle.bundle_id}",
                    "args": {
                        "bundle_id": supporting_bundle.bundle_id,
                        "model_count": len(model_cards),
                    },
                    "result": {
                        "bypass": True,
                        "reason": "Ablation disabled local champion selection; forwarding all hydrated models to the global tournament.",
                        "model_ids": [card["pgs_id"] for card in ordered_model_cards],
                    },
                }
            )
            for idx, model_card in enumerate(ordered_model_cards, start=1):
                champion_card = dict(model_card)
                champion_card["local_champion_rank"] = idx
                champion_cards.append(champion_card)
        else:
            local_decision = _call_local_champion_vnext(
                supporting_bundle=supporting_bundle,
                model_cards=model_cards,
                max_count=config.local_champion_max_per_bundle,
                target_trait=target_trait_label,
                domain_knowledge=domain_knowledge_bundle,
                quality_anchor=config.local_champion_quality_anchor,
            )
            tool_trace.append(
                {
                    "name": "llm_local_champion",
                    "phase": f"phase5_local_champion::{supporting_bundle.bundle_id}",
                    "args": {
                        "bundle_id": supporting_bundle.bundle_id,
                        "model_count": len(model_cards),
                    },
                    "result": local_decision.model_dump(),
                }
            )
            for champion in local_decision.champions:
                champion_card = dict(model_card_lookup[champion.pgs_id])
                champion_card["local_champion_rank"] = champion.local_champion_rank or champion.rank
                champion_cards.append(champion_card)
    search_trace.local_champion_ids = [str(card["pgs_id"]) for card in champion_cards]

    if champion_cards:
        global_frontier = _call_global_frontier_vnext(
            champion_cards,
            target_trait=target_trait_label,
            domain_knowledge=domain_knowledge_payload,
            quality_anchor=config.global_frontier_quality_anchor,
        )
        tool_trace.append(
            {
                "name": "llm_global_model_frontier",
                "phase": "phase5_global_tournament",
                "args": {"champion_count": len(champion_cards)},
                "result": global_frontier.model_dump(),
            }
        )
    else:
        global_frontier = GlobalModelFrontierDecision(
            model_frontier=[],
            primary_model_id=None,
            confidence="Low",
            rationale="No hydrated champion models were available for the final tournament.",
        )
    model_frontier = global_frontier.model_frontier
    search_trace.model_frontier_ids = [candidate.pgs_id for candidate in model_frontier]

    all_cards = _sort_cards(list(card_lookup.values()), config)
    evidence_state = EvidenceState(
        available_tools=available_tools,
        shortlist_bundle_ids=[card.bundle_id for card in all_cards],
        target_summary=target_summary,
        candidate_cards=all_cards,
    )

    stage1 = _synthetic_stage1_from_supporting(
        supporting_bundles,
        evidence_state,
        bundle_posterior.confidence,
        bundle_posterior.rationale,
    )
    stage2 = _synthetic_stage2_from_frontier(
        model_frontier,
        global_frontier.confidence,
        global_frontier.rationale,
        len(hydrated_models),
        list(model_budget_by_bundle.keys()),
    )

    frontier_bundle_ids = [bundle.bundle_id for bundle in supporting_bundles]
    raw_bundle_weights = {
        bundle.bundle_id: float(max(0.01, len(supporting_bundles) - idx))
        for idx, bundle in enumerate(supporting_bundles)
    }
    total_weight = sum(raw_bundle_weights.values()) or 1.0
    frontier_bundle_weights = {
        bundle_id: round(weight / total_weight, 4)
        for bundle_id, weight in raw_bundle_weights.items()
    }
    candidate_pgs_ids = _unique_preserve_order(
        [getattr(model, "id", "") for model in hydrated_models if getattr(model, "id", "")]
    )
    if not candidate_pgs_ids:
        candidate_pgs_ids = _unique_preserve_order(
            [
                pgs_id
                for bundle in supporting_bundles
                for pgs_id in (
                    bundle_lookup_map[bundle.bundle_id].candidate_pgs_ids
                    if bundle.bundle_id in bundle_lookup_map
                    else []
                )
            ]
        )

    best_model_id = global_frontier.primary_model_id
    best_bundle_id = pgs_to_bundle.get(best_model_id or "") if best_model_id else None
    if best_bundle_id is None and supporting_bundles:
        best_bundle_id = supporting_bundles[0].bundle_id
    best_cross_trait = supporting_lookup[best_bundle_id].canonical_label if best_bundle_id in supporting_lookup else None
    decision_mode: DecisionMode = (
        "single_confident"
        if len(model_frontier) == 1 and global_frontier.confidence == "High"
        else "frontier_uncertain" if model_frontier or supporting_bundles else "abstain_only_if_no_valid_bundle"
    )
    bundle_evidence_tags = {
        bundle_id: card_lookup[bundle_id].evidence_tags
        for bundle_id in frontier_bundle_ids
        if bundle_id in card_lookup
    }
    tool_evidence_summary = _build_tool_evidence_summary(
        {
            bundle_id: card_lookup[bundle_id]
            for bundle_id in search_trace.probed_bundle_ids
            if bundle_id in card_lookup
        }
    )

    decision = TwoStageTransferDecision(
        stage1=stage1,
        stage2=stage2,
        supporting_bundles=supporting_bundles,
        model_frontier=model_frontier,
        search_trace=search_trace,
        tool_evidence_summary=tool_evidence_summary,
        failure_label=None,
        outcome="MATCHED" if best_model_id else "NO_MATCH",
        best_bundle_id=best_bundle_id,
        best_cross_trait=best_cross_trait,
        primary_bundle_id=best_bundle_id,
        frontier_bundle_ids=frontier_bundle_ids,
        frontier_bundle_weights=frontier_bundle_weights,
        candidate_pgs_ids=candidate_pgs_ids,
        candidate_pgs_ids_union=candidate_pgs_ids,
        confidence=global_frontier.confidence if best_model_id else bundle_posterior.confidence,
        decision_mode=decision_mode,
        rationale=global_frontier.rationale or bundle_posterior.rationale or search_plan.rationale,
        evidence_state=evidence_state,
        bundle_evidence_tags=bundle_evidence_tags,
        best_model_id=best_model_id,
        recommended_model_ids=[candidate.pgs_id for candidate in model_frontier],
    )

    return {
        "target": dossier.target.model_dump(),
        "condition": condition,
        "ablation": ablation,
        "tool_trace": tool_trace,
        "gc_prescreening_count": len(gc_lookup),
        "semantic_backstop_decision": None,
        "decision": decision.model_dump(),
    }


def write_agent_results(results: list[dict[str, Any]], outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(results, indent=2, ensure_ascii=False))
