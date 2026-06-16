import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _request_with_context(context: dict[str, object]) -> dict[str, object]:
    return {
        "custom_id": "example_trait__chunk_01",
        "ontology": "example trait",
        "candidate_model_ids": ["PGS000001", "PGS000002"],
        "request": {
            "body": {
                "messages": [
                    {"role": "system", "content": "old"},
                    {
                        "role": "user",
                        "content": "Old instruction\n\nContext:\n"
                        + json.dumps(context, separators=(",", ":")),
                    },
                ]
            }
        },
    }


def test_without_domain_general_llm_is_single_stage_true_general_baseline():
    from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as wd
    from src.server.core import within_prompts
    from src.server.core.within_prompts import WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    from src.server.core.within_prompts.archive.selectors_pre_cleanup_20260615 import (
        GENERAL_BIOMEDICAL_STAGE1_SYSTEM_PROMPT,
        GENERAL_LLM_BASELINE_SYSTEM_PROMPT,
    )

    assert not hasattr(within_prompts, "GENERAL_BIOMEDICAL_STAGE1_SYSTEM_PROMPT")
    assert not hasattr(within_prompts, "GENERAL_LLM_BASELINE_SYSTEM_PROMPT")

    context = wd._step1_context(
        "example trait",
        candidate_models=[],
        total_found=0,
        target_ancestry="European",
    )
    context_json = json.dumps(context, separators=(",", ":"))
    messages = wd._step1_messages(context_json)

    # Single LLM call: exactly one system + one user message, no second stage.
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    system_prompt = messages[0]["content"]
    user_prompt = messages[1]["content"]

    # The general llm baseline routes to the dedicated true-general-baseline
    # prompt -- NOT the skill-augmented GENERAL_BIOMEDICAL prompt and NOT the
    # PRS Agent specialist prompt.
    assert system_prompt == GENERAL_LLM_BASELINE_SYSTEM_PROMPT
    assert system_prompt != GENERAL_BIOMEDICAL_STAGE1_SYSTEM_PROMPT
    assert system_prompt != WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT

    # A real domain-expert persona (mirroring DeepRare / MedRAG fair baselines),
    # not the discredited "general biomedical language model" label and not a
    # PRS specialist role.
    assert "expert in human genetics" in system_prompt
    assert "general biomedical language model" not in system_prompt
    assert "PRS model-selection specialist" not in system_prompt
    assert "PRS Agent" not in system_prompt

    # No skill/scaffold, no 2-stage, no hidden-benchmark/performance-proxy, and
    # no inlined PRS appraisal rubric (that knowledge belongs to the skill/agent).
    banned_terms = [
        "skill_context",
        "domain_knowledge",
        "specialist",
        "sealed",
        "hidden benchmark",
        "hidden_benchmark",
        "performance_proxy",
        "performance-proxy",
        "Stage 2",
        "rerank",
        "Appraisal Axes",
        "Shortlist Discipline",
        "PRS-only",
        "full-model",
        "covariate",
        "leakage",
        "near-clone",
        "study-family",
    ]
    combined = system_prompt + "\n" + user_prompt
    for term in banned_terms:
        assert term not in combined, f"general llm prompt must not contain {term!r}"

    assert "skill_context" not in context
    assert "domain_knowledge" not in context
    assert "todo_recitation" not in context
    assert "top_alternatives" not in user_prompt
    assert "outcome, best_model_id, confidence, rationale" in user_prompt


def test_two_stage_rerank_rejects_general_llm_manifest():
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr
    from experiments.contribution2.recommendation.scripts import run_experiment_topk_holistic_rerank_batch as batch

    context = {
        "target_trait": "example trait",
        "target_ancestry": "European",
        "direct_models": {
            "models": [
                {"pgs_id": "PGS000001", "trait_reported": "example trait"},
                {"pgs_id": "PGS000002", "trait_reported": "example trait"},
            ]
        },
        "skill_context": {
            "name": "prs-model-recommendation",
            "source_type": "disabled_by_ablation",
        },
    }
    manifest = {
        "skill_context": False,
        "experiment": "without_domain_batch_formal",
        "requests": [_request_with_context(context)],
        "disease_metadata": [
            {
                "ontology": "example trait",
                "candidate_models_visible_to_llm": context["direct_models"]["models"],
            }
        ],
    }

    assert pr._manifest_uses_general_biomedical_llm(manifest)
    try:
        batch._build_stage1_requests(
            manifest=manifest,
            model="gpt-5.4",
            top_k=5,
            stage1_objective="support",
        )
    except ValueError as exc:
        assert "archived" in str(exc)
    else:
        raise AssertionError("general llm manifest must not build rerank Stage 1 requests")

    try:
        batch._build_stage2_requests(
            manifest=manifest,
            stage1_results={
                "example_trait__chunk_01": {
                    "decision": {
                        "best_model_id": "PGS000001",
                        "top_alternatives": ["PGS000002"],
                    }
                }
            },
            model="gpt-5.4",
            top_k=5,
            objective="support",
        )
    except ValueError as exc:
        assert "archived" in str(exc)
    else:
        raise AssertionError("general llm manifest must not build rerank Stage 2 requests")


def test_prompt_only_no_skill_manifest_can_use_single_stage_fullpool_only(tmp_path, monkeypatch):
    from experiments.contribution2.recommendation.scripts import run_experiment_pairwise_rerank as pr

    context = {
        "target_trait": "example trait",
        "target_ancestry": "European",
        "direct_models": {
            "models": [
                {"id": "PGS000001", "trait_reported": "example trait"},
                {"id": "PGS000002", "trait_reported": "example trait"},
            ]
        },
    }
    manifest = {
        "skill_context": True,
        "prompt_only_no_skill": True,
        "experiment": "with_domain_batch_formal",
        "candidate_order": "stable_hash_shuffle",
        "candidate_order_seed": "unit-test-seed",
        "requests": [{
            **_request_with_context(context),
            "benchmark_ranked_ids": ["PGS000002", "PGS000001"],
            "candidate_order_source": "stable_hash_shuffle",
            "candidate_order_seed": "unit-test-seed",
            "candidate_order_matches_benchmark_order": False,
            "benchmark_top1_position_in_candidate_order": 2,
        }],
        "disease_metadata": [
            {
                "ontology": "example trait",
                "candidate_models_visible_to_llm": context["direct_models"]["models"],
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def fail_stage1(*args, **kwargs):
        raise AssertionError("prompt-only fullpool must not call Stage 1")

    observed = {}

    def fake_fullpool(*args, **kwargs):
        observed["general_biomedical_llm"] = kwargs["general_biomedical_llm"]
        observed["skill_context"] = kwargs["skill_context"]
        return {
            "ontology": kwargs["ontology"],
            "ranked_candidate_ids": kwargs["ranked_candidate_ids"],
            "winner_model_id": "PGS000001",
            "confidence": "Moderate",
            "rationale": "test rationale",
            "error": None,
        }

    monkeypatch.setattr(pr, "_client", lambda: object())
    monkeypatch.setattr(pr, "_run_stage1_for_request", fail_stage1)
    monkeypatch.setattr(pr, "_run_stage2_for_fullpool", fake_fullpool)
    monkeypatch.setattr(
        pr.without_domain,
        "_build_summary_and_results",
        lambda *, manifest, parsed_outputs, error_map: (
            [{"ontology": "example trait", "recommended_pgs_id": "PGS000001"}],
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
    assert meta["prompt_profile"] == "prs_agent_specialist"
    assert meta["execution_architecture"] == "single_stage_fullpool"
    assert meta["stage1_count"] == 0
    assert meta["candidate_order_source"] == "stable_hash_shuffle"
    assert meta["candidate_order_matches_benchmark_count"] == 0
    assert observed["general_biomedical_llm"] is False
    assert observed["skill_context"] == {}
    assert not (tmp_path / "run" / "experiment_pairwise_rerank_stage1_results.json").exists()


def test_prs_agent_manifest_still_routes_to_specialist_skill_and_two_stage():
    from experiments.contribution2.recommendation.scripts import run_experiment_topk_holistic_rerank_batch as batch
    from src.server.core.within_prompts import (
        WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT,
        WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT,
    )

    context = {
        "target_trait": "example trait",
        "target_ancestry": "European",
        "direct_models": {
            "models": [
                {"pgs_id": "PGS000001", "trait_reported": "example trait"},
                {"pgs_id": "PGS000002", "trait_reported": "example trait"},
            ]
        },
        "skill_context": {
            "name": "prs-model-recommendation",
            "full_text": "PRS skill guidance",
            "source_type": "local",
        },
    }
    manifest = {
        "skill_context": True,
        "experiment": "with_domain_batch_formal",
        "requests": [_request_with_context(context)],
        "disease_metadata": [
            {
                "ontology": "example trait",
                "candidate_models_visible_to_llm": context["direct_models"]["models"],
            }
        ],
    }

    stage1_rows = batch._build_stage1_requests(
        manifest=manifest,
        model="gpt-5.4",
        top_k=5,
        stage1_objective="support",
    )
    stage2_rows, _, _ = batch._build_stage2_requests(
        manifest=manifest,
        stage1_results={
            "example_trait__chunk_01": {
                "decision": {
                    "best_model_id": "PGS000001",
                    "top_alternatives": ["PGS000002"],
                }
            }
        },
        model="gpt-5.4",
        top_k=5,
        objective="support",
    )

    assert stage1_rows[0]["body"]["messages"][0]["content"] == WITHIN_STAGE1_SHORTLIST_SYSTEM_PROMPT
    assert (
        "PRS and statistical genetics expert supporting within-phenotype model appraisal"
        in stage1_rows[0]["body"]["messages"][0]["content"]
    )
    assert "skill_context" in stage1_rows[0]["body"]["messages"][1]["content"]
    assert "prs-model-recommendation" in stage1_rows[0]["body"]["messages"][1]["content"]
    assert stage2_rows[0]["body"]["messages"][0]["content"] == WITHIN_STAGE2_COMPACT_SELECTOR_SYSTEM_PROMPT
    # Contract change: the LLM-visible final-selection prompt no longer exposes
    # the developer stage name; routing is still verified by prompt identity above.
    assert "Stage 2" not in stage2_rows[0]["body"]["messages"][0]["content"]
    assert "skill_context" in stage2_rows[0]["body"]["messages"][1]["content"]
    assert "prs-model-recommendation" in stage2_rows[0]["body"]["messages"][1]["content"]
