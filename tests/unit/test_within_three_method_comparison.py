from experiments.contribution2.recommendation.scripts.generate_within_three_method_comparison import (
    _cost,
    build_report,
)


def test_cost_reads_topk_runner_cost_block() -> None:
    summary = {"cost": {"estimated_total_cost_usd": 1.2345}}

    assert _cost(summary) == 1.2345


def test_report_includes_dynamic_model_costs_and_reported_baseline_zero() -> None:
    agent_summary = {
        "total_ontologies": 44,
        "model": "gpt-5.4",
        "trial_hit_at_k": {"1": {"hits": 20, "accuracy": 20 / 44}},
        "baseline": {
            "name": "reported_max_auroc_or_c_index_disease_consistent",
            "hit_at_k": {"1": {"hits": 4, "accuracy": 4 / 44}},
        },
        "cost": {"estimated_total_cost_usd": 1.2345},
    }
    llm_summary = {
        "total_ontologies": 44,
        "model": "gpt-5.4",
        "trial_hit_at_k": {"1": {"hits": 9, "accuracy": 9 / 44}},
        "cost": {"estimated_total_cost_usd": 0.6789},
    }

    md, payload = build_report(agent_summary, llm_summary)

    assert "**API cost (gpt-5.4)**" in md
    assert "PRS Agent $1.2345" in md
    assert "General LLM $0.6789" in md
    assert "PGS reported-max $0.00" in md
    assert payload["cost_usd"] == {
        "prs_agent": 1.2345,
        "general_llm": 0.6789,
        "reported_max": 0.0,
    }
