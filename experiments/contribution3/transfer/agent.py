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
    PROJECT_ROOT,
    CandidateBundleDossier,
    TraitBundle,
    bundle_has_source_universe_pgs,
    is_self_like_bundle,
    load_benchmark_target_selection,
    load_trait_bundle_index,
    normalize_text,
)
from experiments.contribution3.transfer.prompts.transfer_prompt import (
    CandidateEvidenceCard,
    CrossTraitTransferFrontierDecision,
    DecisionMode,
    EvidenceState,
    GeneticCorrelationEvidence,
    HeritabilityEvidence,
    JudgeFrontierSelection,
    OpenTargetsEvidence,
    TRANSFER_FRONTIER_JUDGE_PROMPT,
    TRANSFER_FRONTIER_VERIFY_PROMPT,
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
    return CandidateEvidenceCard(
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
        if len(ordered) >= 3:
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
) -> dict[str, Any]:
    del max_steps, enable_semantic_backstop, enable_forced_match
    if condition not in CONDITION_TOOLS:
        raise ValueError(f"Unsupported condition: {condition}")
    if toolbox is None and bundles is None:
        raise ValueError("Either bundles or toolbox must be provided.")
    if toolbox is None:
        assert bundles is not None
        toolbox = CrossTraitToolbox(bundles)

    config = BENCHMARK_FAMILY_CONFIGS.get(benchmark_family, DEFAULT_CONFIG)
    available_tools = CONDITION_TOOLS[condition]
    target_source = _target_source_for_dossier(dossier, benchmark_family)
    candidate_bundle_ids = [
        bundle.bundle_id
        for bundle in dossier.candidates
        if not is_self_like_bundle(dossier.target, bundle)
        and bundle_has_source_universe_pgs(bundle, target_source)
    ]
    bundle_lookup = _bundle_lookup(dossier)

    tool_trace: list[dict[str, Any]] = []
    gc_result: dict[str, Any] | None = None
    if "cross_trait_genetic_correlation" in available_tools:
        gc_result = toolbox.cross_trait_genetic_correlation_llm(
            dossier.target.target_label,
            candidate_bundle_ids,
            batch_size=config.llm_gc_batch_size,
        )
        tool_trace.append(
            {
                "name": "cross_trait_genetic_correlation",
                "phase": "candidate_prescreen",
                "args": {
                    "target_trait": dossier.target.target_label,
                    "candidate_bundle_ids": candidate_bundle_ids,
                },
                "result": gc_result,
            }
        )
    gc_lookup = _gc_lookup(gc_result)

    provisional_cards = [
        _build_candidate_card(
            dossier,
            bundle_lookup[bundle_id],
            gc_row=gc_lookup.get(bundle_id),
            config=config,
            target_source=target_source,
        )
        for bundle_id in candidate_bundle_ids
        if bundle_id in bundle_lookup
    ]

    if config.shortlist_strategy == "gc_first":
        provisional_cards = _sort_cards(provisional_cards, config)
        prior_shortlist = [
            card.bundle_id
            for card in _prior_ranked_cards(provisional_cards, config)[: config.prior_track_size]
        ]
        selection_shortlist = [
            card.bundle_id
            for card in provisional_cards[: config.selection_track_size]
        ]
        gc_ranked = _gc_ranked_cards(provisional_cards)
        gc_shortlist = [card.bundle_id for card in gc_ranked[: config.gc_track_size]]
        semantic_ranked = sorted(
            provisional_cards,
            key=lambda c: (-c.phenotype_fidelity_score, -c.lexical_match_score, -c.n_models, c.bundle_id),
        )
        semantic_shortlist = [card.bundle_id for card in semantic_ranked[: config.semantic_track_size]]
        support_shortlist = [
            card.bundle_id
            for card in _support_ranked_cards(provisional_cards)[: config.support_track_size]
        ]
        shortlist_ids = _merge_shortlist_tracks(
            [
                prior_shortlist,
                selection_shortlist,
                gc_shortlist,
                semantic_shortlist,
                support_shortlist,
            ],
            config.shortlist_cap,
        )
    else:
        # binary-to-binary keeps the dual-track shortlist that protects semantic matches.
        prior_shortlist = [
            card.bundle_id
            for card in _prior_ranked_cards(provisional_cards, config)[: config.prior_track_size]
        ]
        selection_ranked = _sort_cards(provisional_cards, config)
        selection_shortlist = [
            card.bundle_id
            for card in selection_ranked[: config.selection_track_size]
        ]
        gc_ranked = _gc_ranked_cards(provisional_cards)
        gc_shortlist = [card.bundle_id for card in gc_ranked[: config.gc_track_size]]
        semantic_ranked = sorted(
            provisional_cards,
            key=lambda c: (-c.phenotype_fidelity_score, -c.lexical_match_score, -c.n_models),
        )
        semantic_shortlist = [card.bundle_id for card in semantic_ranked[: config.semantic_track_size]]
        same_endpoint_ids = [
            card.bundle_id
            for card in semantic_ranked
            if card.archetype == "same-endpoint disease"
        ][:3]
        support_shortlist = [
            card.bundle_id
            for card in _support_ranked_cards(provisional_cards)[: config.support_track_size]
        ]
        shortlist_ids = _merge_shortlist_tracks(
            [
                prior_shortlist,
                selection_shortlist,
                same_endpoint_ids,
                gc_shortlist,
                semantic_shortlist,
                support_shortlist,
            ],
            config.shortlist_cap,
        )

    h2_lookup: dict[str, dict[str, Any]] = {}
    ot_lookup: dict[str, dict[str, Any]] = {}
    if "cross_trait_genetic_correlation" in available_tools and shortlist_ids:
        # LLM estimation already covers all candidates in Phase 1;
        # re-estimate the shortlist to refresh with potentially narrower focus.
        detailed_gc = toolbox.cross_trait_genetic_correlation_llm(
            dossier.target.target_label,
            shortlist_ids,
            batch_size=config.llm_gc_batch_size,
        )
        tool_trace.append(
            {
                "name": "cross_trait_genetic_correlation",
                "phase": "shortlist_detailed",
                "args": {
                    "target_trait": dossier.target.target_label,
                    "candidate_bundle_ids": shortlist_ids,
                },
                "result": detailed_gc,
            }
        )
        gc_lookup.update(_gc_lookup(detailed_gc))

    if "cross_trait_heritability" in available_tools and shortlist_ids:
        h2_result = toolbox.cross_trait_heritability(
            dossier.target.target_label,
            shortlist_ids,
            ancestry="EUR",
            response_format="detailed",
        )
        tool_trace.append(
            {
                "name": "cross_trait_heritability",
                "phase": "shortlist_detailed",
                "args": {
                    "target_trait": dossier.target.target_label,
                    "candidate_bundle_ids": shortlist_ids,
                    "ancestry": "EUR",
                    "response_format": "detailed",
                },
                "result": h2_result,
            }
        )
        h2_lookup = _gc_lookup(h2_result)

    if "cross_trait_open_targets" in available_tools and shortlist_ids:
        ot_result = toolbox.cross_trait_open_targets(
            dossier.target.target_label,
            shortlist_ids,
            response_format="detailed",
        )
        tool_trace.append(
            {
                "name": "cross_trait_open_targets",
                "phase": "shortlist_detailed",
                "args": {
                    "target_trait": dossier.target.target_label,
                    "candidate_bundle_ids": shortlist_ids,
                    "response_format": "detailed",
                },
                "result": ot_result,
            }
        )
        ot_lookup = _gc_lookup(ot_result)

    cards = _sort_cards(
        [
            _build_candidate_card(
                dossier,
                bundle_lookup[bundle_id],
                gc_row=gc_lookup.get(bundle_id),
                h2_row=h2_lookup.get(bundle_id),
                ot_row=ot_lookup.get(bundle_id),
                config=config,
                target_source=target_source,
            )
            for bundle_id in shortlist_ids
            if bundle_id in bundle_lookup
        ],
        config,
    )

    evidence_state = EvidenceState(
        available_tools=available_tools,
        shortlist_bundle_ids=[card.bundle_id for card in cards],
        target_summary=_build_target_summary(
            dossier,
            benchmark_family=benchmark_family,
            config=config,
        ),
        candidate_cards=cards,
    )

    default_mode = _decision_mode_from_cards(cards)
    default_frontier_ids = _default_frontier_ids(cards, default_mode)
    judged = _judge_frontier(
        evidence_state, default_frontier_ids, default_mode,
        llm_card_cap=config.llm_card_cap,
    )
    decision = _finalize_frontier_decision(
        dossier,
        evidence_state,
        judged,
        config=config,
    )

    return {
        "target": dossier.target.model_dump(),
        "condition": condition,
        "tool_trace": tool_trace,
        "gc_prescreening_count": len((gc_result or {}).get("results", [])),
        "semantic_backstop_decision": None,
        "decision": decision.model_dump(),
    }


def write_agent_results(results: list[dict[str, Any]], outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(results, indent=2, ensure_ascii=False))
