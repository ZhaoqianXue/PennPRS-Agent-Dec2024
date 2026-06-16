import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _normalize_prompt_whitespace(text: str) -> str:
    return " ".join(text.split())


def _load_input_json(message: str):
    import json

    return json.loads(message.split("Input JSON:\n", 1)[1])


def test_active_within_prompt_surface_only_exports_retained_formal_system_prompts():
    from src.server.core import within_prompts

    active_system_prompts = {
        name for name in within_prompts.__all__
        if name.endswith("_SYSTEM_PROMPT")
    }
    assert active_system_prompts == {
        "WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT",
        "WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT",
        "WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT",
    }
    archived_names = {
        "CO_SCIENTIST_STEP1_PROMPT",
        "CO_SCIENTIST_STEP1_NATIVE_PROMPT",
        "GENERAL_LLM_BASELINE_SYSTEM_PROMPT",
        "GENERAL_BIOMEDICAL_STAGE1_SYSTEM_PROMPT",
        "GENERAL_BIOMEDICAL_TOPK_SELECTOR_SYSTEM_PROMPT",
        "GENERAL_BIOMEDICAL_FULLPOOL_SELECTOR_SYSTEM_PROMPT",
        "WITHIN_STAGE1_AUDIT_SHORTLIST_SYSTEM_PROMPT",
        "WITHIN_STAGE2_AUDIT_SELECTOR_SYSTEM_PROMPT",
        "WITHIN_STAGE2_SELECTOR_SYSTEM_PROMPT",
        "WITHIN_PAIRWISE_JUDGE_SYSTEM_PROMPT",
        "WITHIN_TOPK_RANKER_SYSTEM_PROMPT",
        "WITHIN_RUNNER_UP_SYSTEM_PROMPT",
    }
    leaked = sorted(name for name in archived_names if hasattr(within_prompts, name))
    assert leaked == []

def test_system_prompts_export_only_canonical_within_prompts():
    from src.server.core import system_prompts
    from src.server.core.system_prompts import (
        CO_SCIENTIST_REPORT_PROMPT,
        WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT,
        WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT,
        WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT,
    )

    active_within_system_prompts = {
        name for name in dir(system_prompts)
        if name.startswith("WITHIN_") and name.endswith("_SYSTEM_PROMPT")
    }
    assert active_within_system_prompts == {
        "WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT",
        "WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT",
        "WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT",
    }
    assert not hasattr(system_prompts, "CO_SCIENTIST_STEP1_PROMPT")
    assert not hasattr(system_prompts, "CO_SCIENTIST_STEP1_NATIVE_PROMPT")
    assert not hasattr(system_prompts, "WITHIN_STAGE2_SELECTOR_SYSTEM_PROMPT")

    prompt = WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "You are a PRS and statistical genetics expert supporting within-phenotype model appraisal." in prompt
    assert "Your task is to evaluate the provided PRS candidates for the target phenotype and target ancestry" in prompt
    assert "This decision uses the provided candidate universe for the target phenotype." in prompt
    assert "Use the supplied `skill_context` as the field-level PRS appraisal reference." in prompt
    assert "Treat `skill_context` as evidence" not in prompt
    assert "incorporate it as additional evidence" not in prompt
    assert "domain_knowledge.full_document" not in prompt
    assert "field-level PRS appraisal reference" in prompt
    assert "do not use arbitrary or mechanical ID-based tie-breaking" in prompt
    assert "select the candidate supported by the broadest set of mutually consistent visible evidence" in prompt
    assert "do not let a single salient fact dominate the decision" in prompt
    assert "use the lexicographically smallest valid `PGS ID` as the deterministic tie-break" not in prompt
    assert "# Confidence Semantics" in prompt
    assert "Native GPT Constraint" not in prompt
    assert "Step 1 Evidence Priorities" not in prompt
    assert "Step 1: Direct Match Assessment" not in prompt
    assert "# Outcome Semantics" not in prompt
    assert "DIRECT_HIGH_QUALITY" not in prompt
    assert "DIRECT_SUB_OPTIMAL" not in prompt
    assert "NO_MATCH_FOUND" not in prompt
    assert "set `best_model_id` to `null`" not in prompt
    assert "otherwise use `null`" not in prompt
    assert "# Query Protocol" not in prompt
    assert "# Tool Orchestration Protocol" not in prompt
    assert "Output Schema" not in prompt
    assert "Choose the single final recommendation" in WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT
    assert "inspect the full visible candidate pool" in WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT
    assert "Output Schema" in CO_SCIENTIST_REPORT_PROMPT


def test_archived_formal_prompt_text_is_preserved_after_active_prompt_migration():
    from src.server.core import within_prompts

    archive_path = (
        PROJECT_ROOT
        / "src/server/core/within_prompts/archive/selectors_pre_cleanup_20260615.py"
    )
    archived_text = archive_path.read_text(encoding="utf-8")
    assert "CO_SCIENTIST_STEP1_PROMPT = WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT" in archived_text
    assert "WITHIN_STAGE2_SELECTOR_SYSTEM_PROMPT = WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT" in archived_text
    assert "GENERAL_LLM_BASELINE_SYSTEM_PROMPT" in archived_text
    assert "WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT" in within_prompts.__all__
    assert "WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT" in within_prompts.__all__


def test_within_stage1_prompt_is_fixed_candidate_shortlist_contract():
    from src.server.core.system_prompts import WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT

    prompt = WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "fixed candidate universe" in prompt
    # Contract change: the LLM-visible prompt no longer exposes developer
    # stage names. Stage1 uses a prompt-led bounded evidence-profile shortlist
    # contract, while the runner still does not apply a hidden truncation.
    assert "Stage 1" not in prompt
    assert "Stage 2" not in prompt
    assert "bounded shortlist" not in prompt
    assert "bounded top-5 shortlist" not in prompt
    assert "same-phenotype" in prompt
    assert "same-trait" not in prompt
    assert "no benchmark labels" not in prompt
    assert "Do not use PGS ID memory" not in prompt
    assert "endpoint/metric/ancestry/covariate/method evidence" in prompt
    assert "# Appraisal Axes" not in prompt
    assert "family-history proxies" not in prompt
    assert "risk-tail" not in prompt
    assert "genome-wide shrinkage" not in prompt
    assert "incremental R2" not in prompt
    assert "cross-disease reasoning" not in prompt
    assert "transfer-source reasoning" not in prompt
    assert "new candidate search" not in prompt
    assert "hidden disease-specific" not in prompt
    assert "hard-code thresholds" not in prompt
    assert "CROSS_DISEASE" not in prompt
    assert "Train New Model" not in prompt
    assert "genetic_graph" not in prompt


def test_within_stage2_selector_prompt_is_reviewable():
    from src.server.core.system_prompts import WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT

    selector_prompt = WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT
    assert "You are a PRS and statistical genetics expert supporting within-phenotype model appraisal." in selector_prompt
    # Contract change: the LLM-visible final-selection prompt no longer exposes
    # developer stage names.
    assert "Stage 2" not in selector_prompt
    assert "Stage 1" not in selector_prompt
    assert "bounded final selector" not in selector_prompt
    assert "winner_model_id" in selector_prompt
    assert "ranked_model_ids" in selector_prompt
    assert "winner's PGS ID, confidence, and a short rationale" not in selector_prompt
    assert "strongest runner-up" in selector_prompt
    assert "raw chain-of-thought" in selector_prompt
    assert "concise evidence summary" in selector_prompt
    assert "concise evidence audit" not in selector_prompt
    assert "winner_model_id must be one of `ranked_candidate_ids`" in selector_prompt
    assert "Do not treat the first listed candidate as the provisional winner" in selector_prompt
    assert "candidate-first arbitration protocol" in selector_prompt
    assert "same-context sibling arbitration" in selector_prompt
    assert "independent final re-arbitration" in selector_prompt
    assert "benchmark labels" not in selector_prompt
    assert "PGS ID memory" not in selector_prompt
    assert "trait-specific priors" not in selector_prompt
    assert "disease-category shortcuts" not in selector_prompt
    assert "CROSS_DISEASE" not in selector_prompt
    assert "Train New Model" not in selector_prompt
    assert "genetic_graph" not in selector_prompt


def test_prs_agent_prompts_keep_developer_boundaries_out_of_llm_visible_text():
    from src.server.core.system_prompts import (
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
        "otherwise use `null`",
        "set `best_model_id` to `null`",
    )
    for name, text in prompts.items():
        for fragment in developer_only_fragments:
            assert fragment not in text, f"{name} exposes developer-only boundary text: {fragment}"


def test_archived_audit_prompt_text_is_not_active_but_is_preserved():
    from src.server.core import within_prompts

    assert not hasattr(within_prompts, "WITHIN_STAGE1_AUDIT_SHORTLIST_SYSTEM_PROMPT")
    assert not hasattr(within_prompts, "WITHIN_STAGE2_AUDIT_SELECTOR_SYSTEM_PROMPT")
    archive_path = (
        PROJECT_ROOT
        / "src/server/core/within_prompts/archive/audits_pre_cleanup_20260615.py"
    )
    prompt = archive_path.read_text(encoding="utf-8")
    assert "WITHIN_STAGE1_AUDIT_SHORTLIST_SYSTEM_PROMPT" in prompt
    assert "WITHIN_STAGE2_AUDIT_SELECTOR_SYSTEM_PROMPT" in prompt


def test_pairwise_rerank_uses_canonical_formal_prompts_only():
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr
    from src.server.core.system_prompts import (
        WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT,
        WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT,
        WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT,
    )

    assert pr.WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT == WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert pr.WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT == WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT
    assert pr.WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT == WITHIN_FULLPOOL_JUDGE_SYSTEM_PROMPT
    assert not hasattr(pr, "TOPK_JUDGE_SYSTEM_PROMPT")
    assert not hasattr(pr, "FULLPOOL_JUDGE_SYSTEM_PROMPT")


def test_pairwise_rerank_formal_parser_surface_excludes_archived_prompts():
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr

    parser = pr._build_arg_parser()
    args = parser.parse_args(["--manifest", "manifest.json", "--run-tag", "smoke"])
    evaluator_action = next(action for action in parser._actions if action.dest == "evaluator")
    objective_action = next(action for action in parser._actions if action.dest == "objective")

    assert args.evaluator == "topk_judge"
    assert args.emit_audit_trace is False
    assert set(evaluator_action.choices) == {"topk_judge", "fullpool_judge"}
    assert set(objective_action.choices) == {"support"}


def test_selector_user_builders_use_skill_context_and_target_ancestry():
    from src.server.core.within_prompts import (
        build_within_stage1_user_instruction,
        build_within_topk_user_message,
    )

    instruction = build_within_stage1_user_instruction(3, objective="")
    assert instruction == "Input JSON:"

    topk = build_within_topk_user_message(
        target_trait="coronary artery disease",
        target_ancestry="European",
        ranked_candidate_ids=["PGS000001", "PGS000002"],
        candidate_summaries={"PGS000001": {"pgs_id": "PGS000001"}},
        skill_context={"name": "prs-model-recommendation"},
    )
    assert topk.startswith("Input JSON:\n")
    topk_payload = _load_input_json(topk)
    assert topk_payload["target_ancestry"] == "European"
    assert topk_payload["skill_context"]["name"] == "prs-model-recommendation"
    assert "domain_knowledge" not in topk_payload


def test_user_messages_are_dynamic_data_envelopes_not_decision_policy():
    from src.server.core.within_prompts import (
        build_within_stage1_user_instruction,
        build_within_topk_user_message,
    )

    stage1_user = build_within_stage1_user_instruction(3, objective="support")
    stage2_user = build_within_topk_user_message(
        target_trait="coronary artery disease",
        target_ancestry="European",
        ranked_candidate_ids=["PGS000001", "PGS000002"],
        candidate_summaries={
            "PGS000001": {"pgs_id": "PGS000001"},
            "PGS000002": {"pgs_id": "PGS000002"},
        },
        skill_context={"name": "prs-model-recommendation"},
    )
    dynamic_messages = {
        "stage1_user": stage1_user,
        "stage2_user": stage2_user.split("Input JSON:\n", 1)[0],
    }
    forbidden_policy_fragments = (
        "bounded evidence-profile shortlist",
        "non-dominated evidence coverage",
        "performance-record arbitration",
        "candidate-by-candidate signal audit",
        "strongest-row challenge",
        "source of truth",
        "Recompare all carried-forward candidates",
        "complete candidate sweep",
    )
    for name, text in dynamic_messages.items():
        for fragment in forbidden_policy_fragments:
            assert fragment not in text, f"{name} contains stable decision policy: {fragment}"

    payload = _load_input_json(stage2_user)
    assert payload["target_trait"] == "coronary artery disease"
    assert payload["target_ancestry"] == "European"
    assert payload["ranked_candidate_ids"] == ["PGS000001", "PGS000002"]
    assert payload["candidates"][0]["pgs_id"] == "PGS000001"
    assert "selection_record_digest" in payload


def test_topk_batch_audit_trace_is_explicit_non_default():
    from experiments.contribution2.recommendation.scripts import run_experiment_topk_holistic_rerank_batch as batch

    parser = batch._build_arg_parser()
    args = parser.parse_args(["--manifest", "manifest.json", "--run-tag", "smoke"])

    assert args.emit_audit_trace is False
    assert args.audit_stages == "both"


def test_step1_prompt_requires_target_trait_and_target_ancestry():
    from src.server.core.system_prompts import WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT

    # The task targets an explicit (phenotype, ancestry) pair, while the JSON
    # schema keeps the historical `target_trait` field name.
    assert "target phenotype and target ancestry" in WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "`target_trait` names the target phenotype" in WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "# Target Ancestry" in WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "(`target_trait`, `target_ancestry`)" in WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "relative to the given `target_ancestry`" in WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    # No defensive scaffolding for non-existent missing/unspecified-ancestry runs,
    # and no newly-introduced ancestry-evidence hierarchy.
    assert "unspecified" not in WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "Do not assume a European" not in WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "silently default" not in WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "most direct" not in WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "auxiliary" not in WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT


def test_system_prompts_export_study_classifier_prompt():
    from src.server.core.system_prompts import STUDY_CLASSIFIER_SYSTEM_PROMPT

    assert "GWAS" in STUDY_CLASSIFIER_SYSTEM_PROMPT


def test_within_prompt_surface_keeps_only_formal_prompts_active_and_archives_old_text():
    from src.server.core import within_prompts

    package_path = Path(within_prompts.__file__).resolve()
    selector_path = package_path.parent / "selectors.py"
    audit_path = package_path.parent / "audits.py"
    archive_dir = package_path.parent / "archive"
    old_module_path = PROJECT_ROOT / "src/server/core/within_recommendation_prompts.py"

    assert package_path.name == "__init__.py"
    assert selector_path.exists()
    assert audit_path.exists()
    assert (archive_dir / "selectors_pre_cleanup_20260615.py").exists()
    assert (archive_dir / "audits_pre_cleanup_20260615.py").exists()
    assert not old_module_path.exists()
    assert "Stage 1" not in within_prompts.WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert not hasattr(within_prompts, "CO_SCIENTIST_STEP1_PROMPT")
    assert not hasattr(within_prompts, "CO_SCIENTIST_STEP1_NATIVE_PROMPT")
    assert not hasattr(within_prompts, "WITHIN_STAGE2_SELECTOR_SYSTEM_PROMPT")
    assert not hasattr(within_prompts, "WITHIN_STAGE1_AUDIT_SHORTLIST_SYSTEM_PROMPT")
    assert not hasattr(within_prompts, "WITHIN_STAGE2_AUDIT_SELECTOR_SYSTEM_PROMPT")
    assert not hasattr(within_prompts, "BENCHMARK_OBJECTIVE_BLOCK")
    assert not hasattr(within_prompts, "GENERAL_LLM_BASELINE_SYSTEM_PROMPT")
    # Contract change: Stage1 policy is in the system prompt; the user message
    # builder is only a dynamic input envelope.
    instruction = within_prompts.build_within_stage1_user_instruction(3, objective="")
    assert instruction == "Input JSON:"
    assert "2 and 10" in within_prompts.WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "If only one live non-dominated candidate remains" in within_prompts.WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "bounded evidence-profile shortlist" in within_prompts.WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert "not a runner-side truncation" in within_prompts.WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT

    selector_text = selector_path.read_text(encoding="utf-8")
    audit_text = audit_path.read_text(encoding="utf-8")
    archived_selector_text = (archive_dir / "selectors_pre_cleanup_20260615.py").read_text(encoding="utf-8")
    archived_audit_text = (archive_dir / "audits_pre_cleanup_20260615.py").read_text(encoding="utf-8")
    assert "WITHIN_STAGE1_AUDIT_SHORTLIST_SYSTEM_PROMPT" not in selector_text
    assert "WITHIN_STAGE2_AUDIT_SELECTOR_SYSTEM_PROMPT" not in selector_text
    assert "GENERAL_LLM_BASELINE_SYSTEM_PROMPT" not in selector_text
    assert "BENCHMARK_OBJECTIVE_BLOCK" not in selector_text
    assert "WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT" not in audit_text
    assert "WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT" not in audit_text
    assert "WITHIN_STAGE1_AUDIT_SHORTLIST_SYSTEM_PROMPT" in archived_audit_text
    assert "WITHIN_STAGE2_AUDIT_SELECTOR_SYSTEM_PROMPT" in archived_audit_text
    assert "GENERAL_LLM_BASELINE_SYSTEM_PROMPT" in archived_selector_text
    assert "BENCHMARK_OBJECTIVE_BLOCK" in archived_selector_text


def test_within_prompt_text_is_not_inlined_outside_within_prompt_package():
    from src.server.core import within_prompts

    package_dir = Path(within_prompts.__file__).resolve().parent
    checked_paths = [
        PROJECT_ROOT / "src/server/core/system_prompts.py",
        *(
            PROJECT_ROOT / "experiments/contribution2/recommendation/scripts"
        ).glob("*.py"),
    ]
    prompt_markers = (
        "# Identity & Persona\nYou are a PRS and statistical genetics expert supporting within-phenotype model appraisal.",
        "# Identity & Persona\nYou are a PRS benchmark-selection judge for within-phenotype recommendation.",
        "# Identity & Persona\nYou are a general biomedical language model for fixed-candidate PGS selection.",
        "# Identity & Persona\nYou are an expert in human genetics, genetic epidemiology, and polygenic risk scores (PGS / PRS).",
        "# Identity & Persona\nYou are a PRS benchmark-selection auditor for within-phenotype recommendation.",
        "# Identity & Persona\nYou are a PRS shortlist audit reviewer for within-phenotype recommendation.",
        "# Identity & Persona\nYou are a strict PRS quality judge.",
        "# Identity & Persona\nYou are a PRS benchmark-ranking judge.",
        "# Identity & Persona\nYou are a strict PRS benchmark-selection agent.",
        "# Identity & Persona\nYou are a PRS benchmark-selection meta-judge.",
        "# Identity & Persona\nYou are the runner-up generator for a PRS Co-scientist pipeline.",
        "# Identity\nYou are a PRS Co-scientist running as a single-agent ReAct loop.",
        "# Identity\nYou are the refinement reviewer in a two-stage PRS recommendation pipeline.",
        "# Identity\nYou are the high-precision revision auditor for a PRS recommendation pipeline.",
        "# Identity\nYou are the tail-rescue revision auditor for a PRS recommendation pipeline.",
        "Benchmark-aligned objective:",
        "Benchmark-aligned H1/H5 objective:",
        "Benchmark-proxy objective:",
        "Metric-first hidden-rank objective:",
        "Same-context benchmark objective:",
        "top_alternatives may contain up to two PGS IDs drawn from the same visible",
    )
    violations: list[str] = []
    for path in checked_paths:
        if path.resolve().is_relative_to(package_dir):
            continue
        text = path.read_text(encoding="utf-8")
        for marker in prompt_markers:
            if marker in text:
                violations.append(f"{path.relative_to(PROJECT_ROOT)} contains prompt marker: {marker[:80]}")

    assert not violations
