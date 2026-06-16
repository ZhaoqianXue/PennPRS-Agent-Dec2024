"""Guardrails for the within-phenotype Hit@1 skill/prompt rework.

These tests pin the contract the rework establishes (see
`experiments/contribution2/recommendation/analysis/target10_hit1/DIAGNOSIS.md`):

1. the prs-model-recommendation skill carries no hardcoded PGS IDs;
2. the skill carries no disease-specific answer rules for the 10 target traits;
3. the LLM-visible production prompts leak no benchmark rank / AUC / top-1 answer;
4. the skill and prompts stay schema- and routing-compatible;
5. the skill is free of developer stage names and imperative-negative phrasing;
6. the LLM-visible production prompts expose no developer stage names;
7. the within Stage-1 PRS Agent arm uses a bounded 2-10 evidence-profile
   shortlist, while Stage-2/final-selection surfaces and General/no-skill
   baselines do not impose their own candidate-count steering.
8. evidence_flags is absent from the production path after the failed schema
   enrichment ablation;
9. the field-level appraisal reference follows the current single-record schema
   order;
10. the live PennPRS Agent path uses bounded LLM-led Stage-1 carry-forward
    with machine-validated 2-10 boundaries, and no benchmark objective framing.

Scope. "Production prompt surface" is the set of prompts and user-instruction
builders actually used by the within PRS Agent arm (Stage-1 ranking + Stage-2
final selection in `run_experiment_pairwise_rerank.py`, plus the general-LLM
comparison arm). Opt-in ablation objective blocks (benchmark-aligned, etc.) and
the non-default audit/transparency prompts are deliberately out of scope: they
are never part of the production decision path, and the benchmark-aligned blocks
exist precisely to ablate against the neutral path.
"""
import re
import sys
import json
import hashlib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SKILL_DIR = PROJECT_ROOT / "src" / "server" / "core" / "skills" / "prs-model-recommendation"
SKILL_MD_PATH = SKILL_DIR / "SKILL.md"
SKILL_REFERENCE_PATH = SKILL_DIR / "references" / "pgs_evidence_appraisal.md"

SOURCE_ORDER_BEST_SKILL_CONTEXT_SHA256 = (
    "c207a4db9fac51d2440d6d8146235c5b528b2d2f37557e0b228f3d0427c49ac6"
)

TARGET10_ONTOLOGY_TERMS = (
    "alzheimer disease",
    "asthma",
    "breast carcinoma",
    "hypertension",
    "major depressive disorder",
    "ovarian neoplasm",
    "prostate carcinoma",
    "psoriasis",
    "thyroid carcinoma",
    "type 2 diabetes mellitus",
)

# Schema placeholders that are legitimately present in output-format examples
# (not real benchmark answers).
PGS_PLACEHOLDERS = {"PGS000XXX", "PGS000YYY"}

STAGE_WORDS = ("Stage 1", "Stage 2", "Stage one", "Stage two")
IMPERATIVE_NEGATIVES = ("do not", "don't", "never", "must not")

# Count / top-k phrasing that would impose a fixed candidate range outside the
# within PRS Agent Stage-1 bounded shortlist contract.
COUNT_PATTERNS = (
    r"\bup to\b",
    r"\btop[-\s]?k\b",
    r"\btop[-\s]?\d+\b",
    r"\bbounded shortlist\b",
    r"\bfixed shortlist\b",
    r"\b(?:two|three|four|five|\d+)\s+(?:best[-\s]supported\s+)?(?:runners?-?up|alternatives|candidates|PGS IDs)\b",
    r"\b(?:runners?-?up|alternatives|candidates)\s+(?:of\s+)?(?:up to\s+)?(?:two|three|four|five|\d+)\b",
)

# Benchmark-answer leakage (rank values, AUC values, or a "predict the hidden
# benchmark rank" objective). Anti-leakage phrasing ("no benchmark labels",
# "use ... benchmark labels" inside a prohibition) is allowed and excluded.
# Anti-leakage phrasing such as "no benchmark labels" / "use hidden benchmark
# labels" inside a prohibition is allowed and excluded via the `label` lookahead.
BENCHMARK_LEAKAGE_PATTERNS = (
    r"hidden\s+(?:external\s+)?benchmark(?!\s+labels?)",
    r"rank\s*#?\s*1\s+in",
    r"benchmark[- ]aligned objective",
    r"benchmark[- ]proxy",
    r"benchmark rank(?:s)?\b(?!\s+labels?)",
    r"benchmark AUC",
)


# --------------------------------------------------------------------------- #
# Surfaces under test
# --------------------------------------------------------------------------- #

def _skill_view() -> str:
    from src.server.core.tools.prs_model_evaluator_skill import load_recommendation_view
    return load_recommendation_view()


def _skill_md_text() -> str:
    return SKILL_MD_PATH.read_text(encoding="utf-8")


def _skill_reference_text() -> str:
    return SKILL_REFERENCE_PATH.read_text(encoding="utf-8")


def _skill_raw_text() -> str:
    parts = [_skill_md_text()]
    if SKILL_REFERENCE_PATH.exists():
        parts.append(_skill_reference_text())
    return "\n\n".join(parts)


def _target10_terms_from_manifest() -> tuple[str, ...]:
    return TARGET10_ONTOLOGY_TERMS


def _production_prompts() -> dict[str, str]:
    from src.server.core.within_prompts import (
        WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT,
        WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT,
        WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT,
        build_within_stage1_user_instruction,
        build_within_topk_user_message,
    )

    summaries = {"PGS000001": {"pgs_id": "PGS000001"}, "PGS000002": {"pgs_id": "PGS000002"}}
    return {
        "within_stage1_system": WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT,
        "within_stage2_system": WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT,
        "within_fullpool_system": WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT,
        "within_stage1_user_support": build_within_stage1_user_instruction(3, objective="support"),
        "within_stage1_user_empty": build_within_stage1_user_instruction(3, objective=""),
        "within_stage2_user": build_within_topk_user_message(
            target_trait="t", target_ancestry="European",
            ranked_candidate_ids=["PGS000001", "PGS000002"],
            candidate_summaries=summaries, skill_context={},
        ),
    }


def _fullpool_prompt_surfaces() -> dict[str, str]:
    from src.server.core.within_prompts import (
        WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT,
        build_within_topk_user_message,
    )

    summaries = {"PGS000001": {"pgs_id": "PGS000001"}, "PGS000002": {"pgs_id": "PGS000002"}}
    return {
        "within_fullpool_system": WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT,
        "within_fullpool_user": build_within_topk_user_message(
            target_trait="t", target_ancestry="European",
            ranked_candidate_ids=["PGS000001", "PGS000002"],
            candidate_summaries=summaries, skill_context={},
        ),
    }


# --------------------------------------------------------------------------- #
# 1. No PGS-ID hardcode in the skill
# --------------------------------------------------------------------------- #

def test_skill_has_no_hardcoded_pgs_ids():
    ids = set(re.findall(r"PGS\d{4,}", _skill_view())) | set(re.findall(r"PGS\d{4,}", _skill_raw_text()))
    assert ids == set(), f"skill must not hardcode PGS IDs; found {sorted(ids)}"


# --------------------------------------------------------------------------- #
# 2. No disease-specific answer leakage for the 10 target traits
# --------------------------------------------------------------------------- #

def test_skill_has_no_target_trait_answer_leakage():
    view = _skill_view().lower()
    leaked = [t for t in _target10_terms_from_manifest() if t in view]
    assert leaked == [], f"skill must stay trait-agnostic; named target traits: {leaked}"


# --------------------------------------------------------------------------- #
# 3. No benchmark rank / AUC / top-1 leakage in production prompts
# --------------------------------------------------------------------------- #

def test_production_prompts_have_no_benchmark_leakage():
    for name, text in _production_prompts().items():
        for pat in BENCHMARK_LEAKAGE_PATTERNS:
            assert not re.search(pat, text, re.I), f"{name} leaks benchmark answer via /{pat}/"
        # No real PGS IDs other than schema placeholders.
        real_ids = set(re.findall(r"PGS\d{4,}", text)) - PGS_PLACEHOLDERS - {"PGS000001", "PGS000002"}
        assert real_ids == set(), f"{name} contains non-placeholder PGS IDs {sorted(real_ids)}"


def test_fullpool_prompts_have_no_benchmark_or_external_validation_framing():
    forbidden = (
        r"hidden\s+(?:external\s+)?benchmark",
        r"external\s+benchmark",
        r"benchmark\s+rank",
        r"rank\s*#?\s*1",
        r"#1",
        r"top[-\s]?1",
        r"external-validation performance",
        r"external validation performance",
    )
    for name, text in _fullpool_prompt_surfaces().items():
        for pat in forbidden:
            assert not re.search(pat, text, re.I), f"{name} contains forbidden fullpool framing /{pat}/"


def test_production_prompts_have_no_external_validation_or_benchmark_selection_framing():
    forbidden = (
        r"external-validation performance",
        r"external validation performance",
        r"external validation shortlist",
        r"benchmark-selection",
        r"benchmark selection",
    )
    for name, text in _production_prompts().items():
        for pat in forbidden:
            assert not re.search(pat, text, re.I), f"{name} contains forbidden production framing /{pat}/"


# --------------------------------------------------------------------------- #
# 4. Schema and routing compatibility
# --------------------------------------------------------------------------- #

def test_skill_view_is_schema_aligned_and_nonempty():
    view = _skill_view()
    assert view.strip(), "recommendation view is empty"
    assert "PGS Evidence Appraisal" in view  # corpus title contract
    assert "validation ancestry matches the `target_ancestry`" in view  # ancestry contract
    for section in (
        "predicted_trait", "development_method", "variants", "pgs_source",
        "source_of_variant_associations_gwas", "score_development_training",
        "performance_metrics",
    ):
        assert section in view, f"skill view dropped schema section {section}"


def test_skill_view_preserves_generic_metric_availability_bias_guidance():
    view = _skill_view()
    required_fragments = (
        "displayed AUROC",
        "cumulative-incidence",
        "repeated modest C-index",
        "no AUROC",
        "strong per-SD effect",
        "family history",
        "absolute-risk wrapper",
    )
    for fragment in required_fragments:
        assert fragment in view, f"skill view dropped generic failure-mode guidance: {fragment}"


def test_recommendation_skill_restores_source_order_best_split_contract():
    skill = _skill_md_text()
    reference = _skill_reference_text()

    assert SKILL_REFERENCE_PATH.exists()
    assert "# PGS Evidence Appraisal" not in skill
    assert "# PGS Evidence Appraisal" in reference
    assert "`references/pgs_evidence_appraisal.md`" in skill
    assert "read only when more detail is needed for a field-level comparison" in skill
    assert "within-trait" in skill
    assert "same-trait" in skill
    assert "single-file production skill" not in skill

    reference_only_fragments = (
        "Field-level appraisal patterns",
        "## 8. performance_metrics",
        "labs, strong mediators, and absolute-risk calculators",
        "Multi-trait analyses",
    )
    for fragment in reference_only_fragments:
        assert fragment in reference
        assert fragment not in skill


def test_recommendation_runtime_view_matches_archived_source_order_best_skill_context():
    digest = hashlib.sha256(_skill_view().encode("utf-8")).hexdigest()
    assert digest == SOURCE_ORDER_BEST_SKILL_CONTEXT_SHA256


def test_stage1_user_instruction_preserves_output_schema():
    from src.server.core.within_prompts import WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT

    instruction = WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    for field in ("outcome", "best_model_id", "top_alternatives", "confidence", "rationale"):
        assert field in instruction, f"Stage-1 instruction dropped schema field {field}"


def test_stage1_system_prompt_uses_non_dominated_evidence_coverage():
    from src.server.core.within_prompts import WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT

    instruction = WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "non-dominated evidence coverage" in instruction
    assert "materially different credible evidence axes" in instruction
    assert "evidence-profile audit" in instruction
    assert "active evidence profile" in instruction
    assert "near-duplicate records" in instruction
    assert "clearly weaker duplicates" in instruction
    assert "unresolved profile" in instruction
    assert "could plausibly become the final recommendation" not in instruction
    assert "list every other candidate" not in instruction


def test_within_stage1_uses_bounded_evidence_profile_shortlist():
    from src.server.core.within_prompts import (
        WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT,
    )

    prompt = WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    combined = prompt

    assert "2 and 10" in combined
    assert "bounded evidence-profile shortlist" in combined
    assert "not a numeric score" in combined
    assert "not a runner-side truncation" in combined
    assert "merge weaker near-clone" in combined
    assert "Do not pad" in combined
    assert "Do not exceed 10" in combined
    assert "exact visible-ID check" in combined
    assert "If only one live non-dominated candidate remains" in combined
    assert "top_alternatives=[]" in combined
    assert "`top_alternatives` cannot contain more than 9 IDs" in combined
    assert "same-context sibling" not in combined
    assert "integrative, ensemble, or model-mixing" not in combined
    assert "not an automatic veto" not in combined
    assert "single strongest non-target-ancestry representative" not in combined


def test_stage1_prompt_delegates_field_level_prs_rules_to_skill_reference():
    from src.server.core.tools.prs_model_evaluator_skill import load_recommendation_view
    from src.server.core.within_prompts import WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT

    prompt = WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    skill_view = load_recommendation_view()

    assert "Use the supplied `skill_context` as the field-level PRS appraisal reference." in prompt
    assert "system prompt controls the shortlist procedure" in prompt
    for domain_rule in (
        "family history",
        "genome-wide shrinkage",
    ):
        assert domain_rule in skill_view
        assert domain_rule not in prompt


def test_stage1_system_prompt_uses_coverage_not_final_selection_preemption():
    from src.server.core.within_prompts import WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT

    prompt = WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "non-dominated evidence coverage" in prompt
    assert "evidence-profile audit" in prompt
    assert "active evidence profile" in prompt
    assert "near-duplicate records" in prompt
    assert "final selection pass" in prompt
    assert "clearly weaker duplicates" in prompt
    assert "unresolved profile" in prompt
    assert "reasonable path to become the final recommendation" not in prompt
    assert "competitive-support standard" not in prompt


def test_prs_agent_system_prompts_hide_developer_only_boundaries():
    from src.server.core.within_prompts import (
        WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT,
        WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT,
    )

    prompts = {
        "stage1": WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT,
        "stage2": WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT,
    }
    developer_only_fragments = (
        "cross-disease reasoning",
        "transfer-source reasoning",
        "new candidate search",
        "benchmark labels",
        "hidden disease-specific",
        "hard-code thresholds",
        "PGS ID memory",
        "trait-specific priors",
        "disease-category shortcuts",
        "NO_MATCH_FOUND",
        "# Outcome Semantics",
        "set `best_model_id` to `null`",
        "otherwise use `null`",
    )
    for name, text in prompts.items():
        assert "PRS and statistical genetics expert supporting within-phenotype model appraisal" in text
        for fragment in developer_only_fragments:
            assert fragment not in text, f"{name} exposes developer-only boundary text: {fragment}"


def test_stage2_prompt_does_not_treat_upstream_order_as_evidence_prior():
    from src.server.core import within_prompts
    from src.server.core.within_prompts import WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT

    prompt = WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT
    assert "order is not evidence" in prompt
    assert "Do not treat the first listed candidate as the provisional winner" in prompt
    assert "independent final re-arbitration" in prompt
    assert "weak prior" not in prompt
    assert not hasattr(within_prompts, "WITHIN_PAIRWISE_JUDGE_SYSTEM_PROMPT")


def test_stage2_prompt_uses_metric_family_arbitration():
    from src.server.core.within_prompts import (
        WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT,
        build_within_topk_user_message,
    )

    prompt = WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT
    assert "metric-family arbitration" in prompt
    assert "performance-record arbitration" in prompt
    assert "candidate-first arbitration protocol" in prompt
    assert "same-context sibling arbitration" in prompt
    assert "candidate-by-candidate strongest-signal audit" in prompt
    assert "strongest visible support remains untested" in prompt
    assert "Do not average away" in prompt
    assert "concrete endpoint, covariate, ancestry, sample-context, or metric-comparability defect" in prompt
    assert "system prompt controls the selection procedure" in prompt
    assert "the skill controls how PRS evidence fields should be interpreted" in prompt
    assert "Arbitration ladder" not in prompt
    assert "family history" not in prompt
    assert "tail enrichment" not in prompt
    assert "PRS-CS/PRS-CS-auto" not in prompt

    user_message = build_within_topk_user_message(
        target_trait="t",
        target_ancestry="European",
        ranked_candidate_ids=["PGS000001", "PGS000002"],
        candidate_summaries={"PGS000001": {"pgs_id": "PGS000001"}, "PGS000002": {"pgs_id": "PGS000002"}},
        skill_context={},
    )
    assert "performance-record arbitration" not in user_message
    assert "candidate-by-candidate signal audit" not in user_message
    assert "best endpoint-compatible performance record" not in user_message
    assert "strongest-row challenge" not in user_message
    assert "selection_record_digest" in user_message
    assert "selection_proxy" not in user_message
    assert "Schema-derived first-pass proxy ranking" not in user_message
    assert "first-pass proxy winner" not in user_message
    assert "rank-1" not in user_message
    assert "source of truth" not in user_message


def test_stage2_prompt_requires_complete_candidate_sweep_for_strongest_challenger():
    from src.server.core.within_prompts import WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT

    prompt = WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT
    assert "complete candidate sweep" in prompt
    assert "strongest challenger" in prompt
    assert "outside the first plausible narrative pair" in prompt
    assert "endpoint-compatible genetic-signal evidence" in prompt


def test_stage2_replay_from_run_can_filter_selected_ontologies(tmp_path):
    from experiments.contribution2.recommendation.analysis.target10_hit1 import (
        replay_stage2_from_run,
    )

    rows = [
        {"ontology": "condition a"},
        {"ontology": "condition b"},
        {"ontology": "condition c"},
    ]
    assert replay_stage2_from_run._filter_stage2_rows(rows, None) == rows
    assert replay_stage2_from_run._filter_stage2_rows(rows, {"condition b"}) == [
        {"ontology": "condition b"}
    ]

    ontology_file = tmp_path / "ontologies.txt"
    ontology_file.write_text("# comment\ncondition a\ncondition c\n", encoding="utf-8")
    selected = replay_stage2_from_run._load_selected_ontologies(
        ontology_values=["condition b"],
        ontologies_file=ontology_file,
    )
    assert selected == {"condition a", "condition b", "condition c"}

    with pytest.raises(ValueError, match="Selected ontologies not present"):
        replay_stage2_from_run._filter_stage2_rows(rows, {"condition d"})


def test_stage2_replay_inspection_parses_current_input_json_envelope():
    from experiments.contribution2.recommendation.analysis.target10_hit1 import (
        replay_stage2_from_run,
    )

    stage1_rows = [{
        "ontology": "placeholder trait",
        "context_json": json.dumps({
            "target_trait": "placeholder trait",
            "target_ancestry": "European",
            "skill_context": {},
            "direct_models": {
                "models": [
                    {"id": "PGS000003", "predicted_trait": {"trait_reported": "placeholder trait"}},
                    {"id": "PGS000001", "predicted_trait": {"trait_reported": "placeholder trait"}},
                ],
            },
        }),
        "decision": {
            "best_model_id": "PGS000003",
            "top_alternatives": ["PGS000001"],
        },
    }]
    stage2_rows = [{
        "ontology": "placeholder trait",
        "ranked_candidate_ids": ["PGS000003", "PGS000001"],
    }]

    inspection = replay_stage2_from_run._inspect_messages(
        stage1_rows=stage1_rows,
        stage2_rows=stage2_rows,
    )

    assert inspection["request_count"] == 1
    assert inspection["stage2_candidate_order"] == "source"
    assert inspection["stage2_universe_equals_stage1_carried_forward"] is True
    assert inspection["forbidden_prompt_hits"] == []


def test_stage2_topk_judge_schema_requires_full_llm_ranked_candidate_order():
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr
    from src.server.core.within_prompts import WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT

    schema = pr._topk_response_format()["json_schema"]["schema"]
    assert "ranked_model_ids" in schema["properties"]
    assert "ranked_model_ids" in schema["required"]
    prompt = WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT
    assert "ranked_model_ids" in prompt
    assert "winner_model_id must equal the first ID in ranked_model_ids" in prompt


def test_stage2_prompt_requires_heterogeneous_metric_family_challenger_audit():
    from src.server.core.tools.prs_model_evaluator_skill import load_recommendation_view
    from src.server.core.within_prompts import WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT

    prompt = WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT
    skill_view = load_recommendation_view()
    assert "strongest materially different challenger" in prompt
    assert "family-history adjustment" not in prompt
    assert "family history" in skill_view
    assert "genome-wide shrinkage" in skill_view
    assert "validation ancestry matches the `target_ancestry`" in skill_view


def test_stage2_prompt_delegates_field_level_prs_rules_to_skill_reference():
    from src.server.core.tools.prs_model_evaluator_skill import load_recommendation_view
    from src.server.core.within_prompts import WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT

    prompt = WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT
    skill_view = load_recommendation_view()

    for domain_rule in (
        "family history",
        "genome-wide shrinkage",
    ):
        assert domain_rule in skill_view
        assert domain_rule not in prompt

    for orchestration_rule in (
        "ranked_candidate_ids",
        "complete candidate sweep",
        "strongest runner-up",
        "winner_model_id",
    ):
        assert orchestration_rule in prompt


def test_stage2_user_message_exposes_neutral_selection_record_digest():
    from src.server.core.within_prompts import build_within_topk_user_message

    user_message = build_within_topk_user_message(
        target_trait="placeholder condition",
        target_ancestry="European",
        ranked_candidate_ids=["PGS000001"],
        candidate_summaries={
            "PGS000001": {
                "pgs_id": "PGS000001",
                    "predicted_trait": {"trait_reported": "Placeholder condition"},
                "development_method": {"method_name": "PRS-CS-auto"},
                "variants": {"variants_number": 900000},
                "pgs_source": {
                    "publication_title": "Example score paper",
                    "publication_journal": "Example Journal",
                    "date_release": "2026-01-01",
                },
                "performance_metrics": [{
                        "phenotyping_reported": "Placeholder condition",
                    "covariates": "age, sex, 10 PCs",
                    "evaluation_samples": [{
                        "ancestry": "European",
                        "sample_numbers": {"individuals": 10000, "cases": 4000, "controls": 6000},
                        "cohorts": ["UKB"],
                    }],
                    "classification_metrics": [{"metric_name": "AUROC", "estimate": 0.64}],
                    "other_metrics": [{
                        "metric_name": "Incremental R2 (full model vs. covariates alone)",
                        "estimate": 0.05,
                    }],
                    "effect_sizes": [{"metric_name": "OR", "estimate": 1.4}],
                }],
            },
        },
        skill_context={},
    )
    payload = __import__("json").loads(user_message.split("Input JSON:\n", 1)[1])

    digest = payload["selection_record_digest"]
    assert len(digest) == 1
    assert digest[0]["pgs_id"] == "PGS000001"
    assert digest[0]["method_name"] == "PRS-CS-auto"
    assert digest[0]["variants_number"] == 900000
    forbidden_digest_keys = {"selection_proxy", "rank", "score", "tier", "winner"}
    assert forbidden_digest_keys.isdisjoint(digest[0])
    record = digest[0]["performance_record_digest"][0]
    assert record["evaluation_samples"][0]["ancestry"] == "European"
    assert record["metrics"]["classification"][0]["name"] == "AUROC"
    assert record["metrics"]["other"][0]["estimate"] == 0.05
    assert record["metrics"]["effects"][0]["name"] == "OR"
    assert payload["candidates"][0]["performance_metrics"][0]["phenotyping_reported"] == "Placeholder condition"
    assert "candidates" in payload, "raw candidates JSON remains the source of truth"


def test_neutral_digest_marks_performance_record_truncation_without_selection_signal():
    from src.server.core.within_prompts.selectors import _selection_record_digest

    digest = _selection_record_digest(
        target_trait="placeholder",
        target_ancestry="European",
        ranked_candidate_ids=["PGS000001"],
        candidate_summaries={
            "PGS000001": {
                "pgs_id": "PGS000001",
                "performance_metrics": [
                    {
                        "performance_id": f"PPM{i:06d}",
                        "phenotyping_reported": "placeholder",
                        "classification_metrics": [{"metric_name": "AUROC", "estimate": 0.5}],
                    }
                    for i in range(10)
                ],
            },
        },
    )

    item = digest[0]
    assert item["performance_record_count"] == 10
    assert item["performance_digest_truncated"] is True
    forbidden_keys = {"selection_proxy", "rank", "score", "tier", "winner"}
    assert forbidden_keys.isdisjoint(item)
    assert len(item["performance_record_digest"]) == 8


def test_production_selector_source_has_no_proxy_ranker_or_trait_hack():
    import inspect
    from src.server.core.within_prompts import selectors

    production_sources = "\n".join(
        inspect.getsource(obj)
        for obj in (
            selectors._selection_record_digest,
            selectors.build_within_topk_user_message,
        )
    )
    forbidden = (
        "_selection_proxy_scores",
        "_candidate_signal_summary",
        "_endpoint_quality",
        "selection_proxy",
        "proxy_winner",
        "mandatory first-pass",
        "Select the rank-1",
        "rank-1 proxy",
        "psoria" + "sis",
        "demen" + "tia",
        "time-to-" + "event",
    )
    for term in forbidden:
        assert term not in production_sources


def test_neutral_digest_contains_no_candidate_level_rank_score_tier_or_winner():
    from src.server.core.within_prompts.selectors import _selection_record_digest

    digest = _selection_record_digest(
        target_trait="placeholder",
        target_ancestry="European",
        ranked_candidate_ids=["PGS000002", "PGS000001"],
        candidate_summaries={
            "PGS000001": {"pgs_id": "PGS000001", "development_method": {"method_name": "A"}},
            "PGS000002": {"pgs_id": "PGS000002", "development_method": {"method_name": "B"}},
        },
    )
    assert [item["pgs_id"] for item in digest] == ["PGS000002", "PGS000001"]
    forbidden_keys = {"selection_proxy", "rank", "score", "tier", "winner"}
    for item in digest:
        assert forbidden_keys.isdisjoint(item)


def test_domain_knowledge_tool_still_serves_the_skill():
    from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge
    result = prs_model_domain_knowledge("target_trait: x; target_ancestry: European")
    assert result.full_document
    assert "PGS Evidence Appraisal" in result.full_document


def test_recommendation_skill_metadata_and_text_match_runtime_boundaries():
    text = _skill_md_text()

    assert "Use when choosing or verifying the best same-phenotype PGS Catalog model" in text
    assert "Do not use for cross-phenotype transfer" in text
    assert "new model training" in text
    assert "full-pool baseline judging" in text
    assert "candidate records are not visible" in text
    assert "reasoning order below, strongest predictor first" in text
    assert "`references/pgs_evidence_appraisal.md`" in text
    assert "read only when more detail is needed" in text
    assert "single-file production skill" not in text
    assert "reference corpus" not in text
    assert "within-trait" in text
    assert "same-trait" in text


def test_routing_still_separates_within_and_general_arms():
    from src.server.core import within_prompts

    assert hasattr(within_prompts, "WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT")
    assert not hasattr(within_prompts, "GENERAL_BIOMEDICAL_STAGE1_SYSTEM_PROMPT")
    archive_path = PROJECT_ROOT / "src/server/core/within_prompts/archive/selectors_pre_cleanup_20260615.py"
    assert "GENERAL_BIOMEDICAL_STAGE1_SYSTEM_PROMPT" in archive_path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# 5. Skill: no stage words, no body-level imperative negatives
# --------------------------------------------------------------------------- #

def test_skill_is_free_of_stage_words_and_imperative_negatives():
    for label, text in (("view", _skill_view()), ("raw", _skill_raw_text())):
        low = text.lower()
        for w in STAGE_WORDS:
            assert w.lower() not in low, f"skill ({label}) contains developer stage word {w!r}"

    raw_body = _skill_raw_text().split("---", 2)[-1].lower()
    view_low = _skill_view().lower()
    for label, low in (("view", view_low), ("raw_body", raw_body)):
        for w in IMPERATIVE_NEGATIVES:
            assert not re.search(rf"\b{re.escape(w)}\b", low), \
                f"skill ({label}) contains imperative-negative {w!r}"


# --------------------------------------------------------------------------- #
# 6. Production prompts expose no developer stage names
# --------------------------------------------------------------------------- #

def test_production_prompts_expose_no_stage_words():
    for name, text in _production_prompts().items():
        for w in STAGE_WORDS:
            assert w not in text, f"{name} exposes developer stage word {w!r}"


# --------------------------------------------------------------------------- #
# 7. Bounded Stage-1 shortlist, no downstream fixed-count steering
# --------------------------------------------------------------------------- #

def test_skill_stage2_general_and_fullpool_surfaces_impose_no_candidate_count():
    prompts = _production_prompts()
    surfaces = {
        "skill_view": _skill_view(),
        **{
            name: text
            for name, text in prompts.items()
            if not name.startswith("within_stage1")
        },
    }
    for name, text in surfaces.items():
        for pat in COUNT_PATTERNS:
            assert not re.search(pat, text, re.I), f"{name} imposes a candidate count via /{pat}/"


def test_fullpool_prompts_do_not_hint_fixed_shortlist_or_candidate_count():
    for name, text in _fullpool_prompt_surfaces().items():
        for pat in COUNT_PATTERNS:
            assert not re.search(pat, text, re.I), f"{name} imposes a fullpool candidate count via /{pat}/"


# --------------------------------------------------------------------------- #
# 7b. Runners use production evidence-bound mode, not legacy fixed top-k
# --------------------------------------------------------------------------- #

def test_runner_top_k_defaults_to_production_evidence_bound_mode():
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr
    from experiments.contribution2.recommendation.scripts import run_experiment_topk_holistic_rerank_batch as batch

    # The production sentinel maps every "all candidates from the evidence-bound
    # Stage-1 shortlist" spelling to None; an explicit positive integer is still
    # honoured for legacy ablations.
    for spelling in ("all", "none", "0", "-1", ""):
        assert pr._parse_top_k(spelling) is None
    assert pr._parse_top_k("5") == 5

    # Both production runners default to the LLM-led evidence-bound Stage-1
    # contract, with machine validation rather than silent truncation.
    for build_parser in (pr._build_arg_parser, batch._build_arg_parser):
        args = build_parser().parse_args(["--manifest", "m.json", "--run-tag", "t"])
        assert args.top_k is None, "runner must default to production evidence-bound mode"


def test_runner_candidate_range_metadata_distinguishes_universe_from_evidence_range():
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr

    fullpool = pr._candidate_range_metadata(evaluator="fullpool_judge", top_k=None)
    evidence = pr._candidate_range_metadata(evaluator="topk_judge", top_k=None)
    fixed = pr._candidate_range_metadata(evaluator="topk_judge", top_k=5)

    assert fullpool["candidate_range"] == "candidate_pool_universe"
    assert evidence["candidate_range"] == "evidence_determined"
    assert fixed["candidate_range"] == "fixed_count"
    assert "context window" in fullpool["engineering_limit"]
    assert "machine-validated at 10 carried candidates" in evidence["engineering_limit"]


def test_fullpool_pipeline_is_single_stage_and_never_calls_stage1(tmp_path, monkeypatch):
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr

    context = {
        "target_trait": "placeholder trait",
        "target_ancestry": "European",
        "skill_context": {"source_type": "test"},
    }
    manifest = {
        "requests": [{
            "custom_id": "placeholder_trait__chunk_01",
            "ontology": "placeholder trait",
            "candidate_model_ids": ["PGS000001", "PGS000002"],
            "request": {
                "body": {
                    "messages": [
                        {"role": "system", "content": "s"},
                        {"role": "user", "content": "Context:\n" + __import__("json").dumps(context)},
                    ]
                }
            },
        }],
        "disease_metadata": [{
            "ontology": "placeholder trait",
            "candidate_models": [
                {"id": "PGS000001", "trait_reported": "placeholder trait"},
                {"id": "PGS000002", "trait_reported": "placeholder trait"},
            ],
        }],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(__import__("json").dumps(manifest), encoding="utf-8")

    def fail_stage1(*args, **kwargs):
        raise AssertionError("fullpool_judge must not call Stage 1")

    monkeypatch.setattr(pr, "_client", lambda: object())
    monkeypatch.setattr(pr, "_run_stage1_for_request", fail_stage1)
    monkeypatch.setattr(
        pr,
        "_run_stage2_for_fullpool",
        lambda *args, **kwargs: {
            "ontology": kwargs["ontology"],
            "ranked_candidate_ids": kwargs["ranked_candidate_ids"],
            "winner_model_id": kwargs["ranked_candidate_ids"][0],
            "confidence": "Moderate",
            "rationale": "test rationale",
            "error": None,
        },
    )
    monkeypatch.setattr(
        pr.without_domain,
        "_build_summary_and_results",
        lambda *, manifest, parsed_outputs, error_map: (
            [{"ontology": "placeholder trait", "recommended_pgs_id": "PGS000001"}],
            {"trial_hit_at_k": {"1": {"hits": 1, "eligible": 1, "accuracy": 1.0}}},
        ),
    )
    monkeypatch.setattr(pr.without_domain, "_configure_benchmark_sources", lambda **kwargs: None)

    summary = pr._run_pipeline(
        manifest_path=manifest_path,
        output_run_dir=tmp_path / "run",
        model="gpt-5.4-mini",
        workers=1,
        top_k=None,
        evaluator="fullpool_judge",
        objective="support",
        stage1_objective="support",
    )

    meta = summary["pairwise_rerank"]
    assert meta["execution_architecture"] == "single_stage_fullpool"
    assert meta["stage1_count"] == 0
    assert meta["stage2_count"] == 0
    assert meta["single_stage_count"] == 1
    assert meta["fullpool_count"] == 1
    assert meta["borda_revised_count"] == 0
    assert not (tmp_path / "run" / "experiment_pairwise_rerank_stage1_results.json").exists()


def test_stage1_response_schema_caps_top_alternatives_at_nine():
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr

    schema = pr._stage1_response_format()["json_schema"]["schema"]
    assert schema["properties"]["top_alternatives"]["maxItems"] == 9


def test_step1_ranked_decision_rejects_more_than_nine_alternatives():
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr

    ids = [f"PGS{i:06d}" for i in range(1, 11)]
    with pytest.raises(Exception, match="top_alternatives"):
        pr.Step1RankedDecision(
            outcome="DIRECT_HIGH_QUALITY",
            best_model_id="PGS000000",
            top_alternatives=ids,
            confidence="Moderate",
            rationale="test",
        )


def test_select_ranked_candidates_rejects_overlarge_production_stage1_shortlist():
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr

    ids = [f"PGS{i:04d}" for i in range(1, 31)]
    with pytest.raises(ValueError, match="Stage1 carried set exceeds 10"):
        pr._select_ranked_candidates(
            best_model_id=ids[0],
            top_alternatives=ids[1:11],
            candidate_id_set=set(ids),
            top_k=None,
        )


def test_select_ranked_candidates_legacy_top_k_ablation_still_caps_explicitly():
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr

    ids = [f"PGS{i:04d}" for i in range(1, 31)]
    out = pr._select_ranked_candidates(
        best_model_id=ids[0],
        top_alternatives=ids[1:],
        candidate_id_set=set(ids),
        top_k=3,
    )
    assert out == ids[:3]


def test_stable_hash_candidate_order_breaks_benchmark_order():
    from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as wo

    benchmark_order = [
        "PGS004838",
        "PGS004840",
        "PGS005246",
        "PGS005329",
        "PGS005324",
        "PGS005242",
        "PGS005110",
        "PGS004870",
    ]
    ordered = wo._order_candidate_ids_for_llm(
        ontology="placeholder condition",
        candidate_model_ids=benchmark_order,
        benchmark_ranked_ids=benchmark_order,
        candidate_order="stable_hash_shuffle",
        candidate_order_seed="unit-test-seed",
    )
    ordered_again = wo._order_candidate_ids_for_llm(
        ontology="placeholder condition",
        candidate_model_ids=benchmark_order,
        benchmark_ranked_ids=benchmark_order,
        candidate_order="stable_hash_shuffle",
        candidate_order_seed="unit-test-seed",
    )

    assert ordered == ordered_again
    assert set(ordered) == set(benchmark_order)
    assert ordered != benchmark_order
    assert ordered[0] != benchmark_order[0], "benchmark top1 must not be deterministically first"


def test_candidate_order_metadata_records_source_and_top1_position():
    from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as wo

    benchmark_order = ["PGS000001", "PGS000002", "PGS000003"]
    candidate_order = ["PGS000003", "PGS000001", "PGS000002"]

    metadata = wo._candidate_order_metadata(
        candidate_model_ids=candidate_order,
        benchmark_ranked_ids=benchmark_order,
        candidate_order="stable_hash_shuffle",
        candidate_order_seed="unit-test-seed",
    )

    assert metadata["candidate_order_source"] == "stable_hash_shuffle"
    assert metadata["candidate_order_seed"] == "unit-test-seed"
    assert metadata["candidate_order_matches_benchmark_order"] is False
    assert metadata["benchmark_top1_position_in_candidate_order"] == 2


# --------------------------------------------------------------------------- #
# 8. evidence_flags removed from the production path
# --------------------------------------------------------------------------- #

def test_evidence_flags_are_not_wired_into_prs_agent_context_builder():
    import inspect
    from experiments.contribution2.recommendation.scripts import run_experiment_with_domain as wd

    assert "evidence_flags" not in inspect.getsource(wd._step1_context)
    assert "annotate_record" not in inspect.getsource(wd._step1_context)


def test_evidence_flags_text_and_module_are_removed():
    assert "evidence_flags" not in _skill_raw_text()
    assert "evidence_flags" not in _skill_view()
    assert not (PROJECT_ROOT / "src/server/core/tools/pgs_evidence_flags.py").exists()
    assert not (PROJECT_ROOT / "tests/unit/test_pgs_evidence_flags.py").exists()


def test_with_domain_and_minimal_lift_contexts_do_not_emit_evidence_flags():
    from experiments.contribution2.recommendation.scripts import run_experiment_minimal_lift as ml
    from experiments.contribution2.recommendation.scripts import run_experiment_with_domain as wd

    model = {"id": "PGS000000", "trait_reported": "placeholder"}
    for builder in (wd._step1_context, ml._step1_context):
        context = builder("placeholder trait", [model], 1, "European")
        assert "evidence_flags" not in repr(context)
        for candidate in context["direct_models"]["models"]:
            assert "evidence_flags" not in candidate


def test_general_baseline_context_remains_evidence_flag_free():
    from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as wo

    context = wo._step1_context(
        ontology="placeholder trait",
        candidate_models=[{"id": "PGS000000", "trait_reported": "placeholder"}],
        total_found=1,
        target_ancestry="European",
    )
    assert "evidence_flags" not in repr(context)


# --------------------------------------------------------------------------- #
# 9. Field-level reference follows current single-record schema order
# --------------------------------------------------------------------------- #

def test_pgs_evidence_appraisal_section_order_matches_single_record_schema():
    from src.server.core.tools.pgs_single_record import build_single_record

    schema_order = list(build_single_record("PGS003725").keys())
    reference_text = _skill_reference_text()
    headings = re.findall(r"^## (?:\d+\. )?([A-Za-z0-9_]+)(?:\b|$)", reference_text, flags=re.M)
    field_headings = [heading for heading in headings if heading in schema_order]

    assert field_headings == schema_order, (
        "pgs_evidence_appraisal.md field-level appraisal headings must match the current "
        f"single-record schema order; expected {schema_order}, found {field_headings}"
    )
    assert "Cross-cutting principles" not in reference_text


# --------------------------------------------------------------------------- #
# 10. Live path uses production evidence-bound/support framing
# --------------------------------------------------------------------------- #

def test_live_same_trait_runner_uses_clean_double_stage_evidence_bound_support_objective():
    import ast

    service_path = PROJECT_ROOT / "src/server/modules/pennprs_agent/service.py"
    tree = ast.parse(service_path.read_text(encoding="utf-8"))
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_run_pipeline"
    ]
    assert calls, "live service must call the same-trait pipeline"
    for call in calls:
        kwargs = {kw.arg: kw.value for kw in call.keywords if kw.arg}
        top_k = kwargs.get("top_k")
        evaluator = kwargs.get("evaluator")
        objective = kwargs.get("objective")
        stage1_objective = kwargs.get("stage1_objective")
        legacy_two_stage_fullpool = kwargs.get("legacy_two_stage_fullpool")
        assert top_k is None or isinstance(top_k, ast.Constant) and top_k.value is None
        assert isinstance(evaluator, ast.Constant) and evaluator.value == "topk_judge"
        assert isinstance(objective, ast.Constant) and objective.value == "support"
        assert isinstance(stage1_objective, ast.Constant) and stage1_objective.value == "support"
        assert legacy_two_stage_fullpool is None or (
            isinstance(legacy_two_stage_fullpool, ast.Constant)
            and legacy_two_stage_fullpool.value is False
        )


def test_double_stage_pipeline_stage2_universe_equals_stage1_carry_forward(tmp_path, monkeypatch):
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr

    context = {
        "target_trait": "placeholder trait",
        "target_ancestry": "European",
        "skill_context": {"source_type": "test"},
    }
    manifest = {
        "requests": [{
            "custom_id": "placeholder_trait__chunk_01",
            "ontology": "placeholder trait",
            "candidate_model_ids": ["PGS000001", "PGS000002", "PGS000003", "PGS000004"],
            "request": {
                "body": {
                    "messages": [
                        {"role": "system", "content": "s"},
                        {"role": "user", "content": "Context:\n" + __import__("json").dumps(context)},
                    ]
                }
            },
        }],
        "disease_metadata": [{
            "ontology": "placeholder trait",
            "candidate_models_visible_to_llm": [
                {"id": "PGS000001", "trait_reported": "placeholder trait"},
                {"id": "PGS000002", "trait_reported": "placeholder trait"},
                {"id": "PGS000003", "trait_reported": "placeholder trait"},
                {"id": "PGS000004", "trait_reported": "placeholder trait"},
            ],
        }],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(__import__("json").dumps(manifest), encoding="utf-8")

    captured_stage2_universes = []

    monkeypatch.setattr(pr, "_client", lambda: object())
    monkeypatch.setattr(
        pr,
        "_run_stage1_for_request",
        lambda *args, **kwargs: {
            "custom_id": "placeholder_trait__chunk_01",
            "ontology": "placeholder trait",
            "decision": {
                "outcome": "DIRECT_HIGH_QUALITY",
                "best_model_id": "PGS000003",
                "top_alternatives": ["PGS000001"],
                "confidence": "Moderate",
                "rationale": "test rationale",
            },
            "context_json": __import__("json").dumps(context),
            "error": None,
        },
    )

    def fake_stage2(*args, **kwargs):
        captured_stage2_universes.append(list(kwargs["ranked_candidate_ids"]))
        return {
            "ontology": kwargs["ontology"],
            "ranked_candidate_ids": kwargs["ranked_candidate_ids"],
            "winner_model_id": kwargs["ranked_candidate_ids"][0],
            "confidence": "Moderate",
            "rationale": "test rationale",
            "error": None,
        }

    monkeypatch.setattr(pr, "_run_stage2_for_topk", fake_stage2)
    monkeypatch.setattr(
        pr.without_domain,
        "_build_summary_and_results",
        lambda *, manifest, parsed_outputs, error_map: (
            [{"ontology": "placeholder trait", "recommended_pgs_id": "PGS000003"}],
            {"trial_hit_at_k": {"1": {"hits": 1, "eligible": 1, "accuracy": 1.0}}},
        ),
    )
    monkeypatch.setattr(pr.without_domain, "_configure_benchmark_sources", lambda **kwargs: None)

    summary = pr._run_pipeline(
        manifest_path=manifest_path,
        output_run_dir=tmp_path / "run",
        model="gpt-5.4-mini",
        workers=1,
        top_k=None,
        evaluator="topk_judge",
        objective="support",
        stage1_objective="support",
    )

    assert captured_stage2_universes == [["PGS000003", "PGS000001"]]
    assert set(captured_stage2_universes[0]) == {"PGS000001", "PGS000003"}
    assert summary["pairwise_rerank"]["execution_architecture"] == "two_stage_rerank"
    assert summary["pairwise_rerank"]["ranked_candidates_by_ontology"] == {
        "placeholder trait": ["PGS000003", "PGS000001"]
    }


def test_stage2_replay_keeps_source_order_by_default_and_supports_stable_hash_ablation():
    from experiments.contribution2.recommendation.analysis.target10_hit1 import (
        replay_stage2_from_run,
    )

    assert replay_stage2_from_run.DEFAULT_STAGE2_CANDIDATE_ORDER == "source"
    source_order = ["PGS000003", "PGS000001"]
    default_order = replay_stage2_from_run._order_stage2_candidate_ids(
        ontology="placeholder trait",
        ranked_candidate_ids=source_order,
        candidate_order=replay_stage2_from_run.DEFAULT_STAGE2_CANDIDATE_ORDER,
        candidate_order_seed=replay_stage2_from_run.DEFAULT_STAGE2_CANDIDATE_ORDER_SEED,
    )
    stable_order = replay_stage2_from_run._order_stage2_candidate_ids(
        ontology="placeholder trait",
        ranked_candidate_ids=source_order,
        candidate_order="stable_hash_shuffle",
        candidate_order_seed=replay_stage2_from_run.DEFAULT_STAGE2_CANDIDATE_ORDER_SEED,
    )

    assert default_order == source_order
    assert stable_order == ["PGS000001", "PGS000003"]
    assert set(stable_order) == set(source_order)
