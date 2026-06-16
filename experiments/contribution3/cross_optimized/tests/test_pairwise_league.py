from __future__ import annotations

import json

import pandas as pd

from experiments.contribution3.cross_optimized.batch.pairwise_league import (
    aggregate_pairwise_predictions,
    build_pairwise_review_evidence,
    build_pairwise_lines,
    build_switch_policy_predictions,
)


def _write_stage_c_request(path, *, target_id: str = "X01") -> None:
    body = {
        "model": "gpt-5.4-nano",
        "input": [
            {"role": "system", "content": "existing stage c"},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "schema_version": "cross_optimized.stage_c.v1",
                        "target": {
                            "target_id": target_id,
                            "input_type": "A",
                            "target_source": "extend_trait",
                            "label": "Target condition",
                            "aliases": ["Target condition"],
                        },
                        "frontier_pgs_records": [
                            {
                                "pgs_id": "PGS000001",
                                "reported_trait": "Trait one",
                                "mapped_trait_ids": ["EFO_000001"],
                                "performance": {"best_auc": 0.7},
                            },
                            {
                                "pgs_id": "PGS000002",
                                "reported_trait": "Trait two",
                                "mapped_trait_ids": ["EFO_000002"],
                                "performance": {"best_auc": 0.8},
                            },
                            {
                                "pgs_id": "PGS000003",
                                "reported_trait": "Trait three",
                                "mapped_trait_ids": ["EFO_000003"],
                                "performance": {"best_auc": 0.9},
                            },
                        ],
                    }
                ),
            },
        ],
    }
    path.write_text(
        json.dumps(
            {
                "custom_id": f"stageC__{target_id}",
                "method": "POST",
                "url": "/v1/responses",
                "body": body,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_build_pairwise_lines_uses_top_n_round_robin(tmp_path) -> None:
    source = tmp_path / "stage_c.jsonl"
    out = tmp_path / "targets.csv"
    _write_stage_c_request(source)
    pd.DataFrame(
        [
            {
                "input_type": "A",
                "target_source": "extend_trait",
                "input_icd": "X01",
                "input_ontology": "",
                "input_description": "Target condition",
                "selected": True,
            }
        ]
    ).to_csv(out, index=False)

    lines = build_pairwise_lines(
        candidate_request_path=source,
        targets_path=out,
        top_n=3,
        max_output_tokens=700,
    )

    assert len(lines) == 3
    assert {line["custom_id"] for line in lines} == {
        "pairwise__X01__i00__j01",
        "pairwise__X01__i00__j02",
        "pairwise__X01__i01__j02",
    }
    assert all(line["body"]["model"] == "gpt-5.4-nano" for line in lines)
    assert all(line["body"]["max_output_tokens"] == 700 for line in lines)
    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["pair"]["candidate_a"]["pgs_id"] == "PGS000001"
    assert payload["pair"]["candidate_b"]["pgs_id"] == "PGS000002"
    assert "benchmark_top_model_id" not in lines[0]["body"]["input"][1]["content"]


def test_aggregate_pairwise_predictions_uses_wins_then_input_order(tmp_path) -> None:
    source = tmp_path / "stage_c.jsonl"
    _write_stage_c_request(source)
    output = tmp_path / "pairwise_output.jsonl"
    output.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "custom_id": "pairwise__X01__i00__j01",
                        "response": {
                            "status_code": 200,
                            "body": {
                                "output_text": json.dumps(
                                    {
                                        "winner_pgs_id": "PGS000002",
                                        "loser_pgs_id": "PGS000001",
                                        "confidence": "moderate",
                                        "rationale": "candidate b is stronger",
                                        "evidence_cited": ["candidate_b.performance.best_auc"],
                                    }
                                ),
                                "usage": {"input_tokens": 10, "output_tokens": 5},
                            },
                        },
                        "error": None,
                    }
                ),
                json.dumps(
                    {
                        "custom_id": "pairwise__X01__i00__j02",
                        "response": {
                            "status_code": 200,
                            "body": {
                                "output_text": json.dumps(
                                    {
                                        "winner_pgs_id": "PGS000003",
                                        "loser_pgs_id": "PGS000001",
                                        "confidence": "moderate",
                                        "rationale": "candidate c is stronger",
                                        "evidence_cited": ["candidate_c.performance.best_auc"],
                                    }
                                ),
                                "usage": {"input_tokens": 10, "output_tokens": 5},
                            },
                        },
                        "error": None,
                    }
                ),
                json.dumps(
                    {
                        "custom_id": "pairwise__X01__i01__j02",
                        "response": {
                            "status_code": 200,
                            "body": {
                                "output_text": json.dumps(
                                    {
                                        "winner_pgs_id": "PGS000002",
                                        "loser_pgs_id": "PGS000003",
                                        "confidence": "moderate",
                                        "rationale": "candidate b wins head to head",
                                        "evidence_cited": ["candidate_a.reported_trait"],
                                    }
                                ),
                                "usage": {"input_tokens": 10, "output_tokens": 5},
                            },
                        },
                        "error": None,
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    predictions = aggregate_pairwise_predictions(
        candidate_request_path=source,
        pairwise_output_path=output,
        top_n=3,
        outpath=tmp_path / "predictions.json",
    )

    assert predictions[0]["target_id"] == "X01"
    assert predictions[0]["primary_pgs_id"] == "PGS000002"
    assert predictions[0]["frontier_pgs_ids"] == ["PGS000002", "PGS000003", "PGS000001"]
    assert predictions[0]["pairwise_wins"] == {"PGS000001": 0, "PGS000002": 2, "PGS000003": 1}


def test_aggregate_pairwise_predictions_recovers_truncated_json_prefix(tmp_path) -> None:
    source = tmp_path / "stage_c.jsonl"
    _write_stage_c_request(source)
    output = tmp_path / "pairwise_output.jsonl"
    output.write_text(
        json.dumps(
            {
                "custom_id": "pairwise__X01__i00__j01",
                "response": {
                    "status_code": 200,
                    "body": {
                        "output_text": (
                            '{"winner_pgs_id":"PGS000002","loser_pgs_id":"PGS000001",'
                            '"confidence":"moderate","rationale":"truncated'
                        ),
                        "usage": {"input_tokens": 10, "output_tokens": 5},
                    },
                },
                "error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    predictions = aggregate_pairwise_predictions(
        candidate_request_path=source,
        pairwise_output_path=output,
        top_n=2,
        outpath=tmp_path / "predictions.json",
    )

    assert predictions[0]["primary_pgs_id"] == "PGS000002"
    assert predictions[0]["pairwise_wins"] == {"PGS000001": 0, "PGS000002": 1}


def test_build_pairwise_review_evidence_keeps_reviews_non_authoritative(tmp_path) -> None:
    source = tmp_path / "stage_c.jsonl"
    _write_stage_c_request(source)
    output = tmp_path / "pairwise_output.jsonl"
    output.write_text(
        json.dumps(
            {
                "custom_id": "pairwise__X01__i00__j01",
                "response": {
                    "status_code": 200,
                    "body": {
                        "output_text": json.dumps(
                            {
                                "winner_pgs_id": "PGS000002",
                                "loser_pgs_id": "PGS000001",
                                "confidence": "moderate",
                                "rationale": "candidate b has a clearer bridge and stronger visible evidence",
                                "evidence_cited": ["candidate_b.performance.best_auc"],
                            }
                        ),
                        "usage": {"input_tokens": 10, "output_tokens": 5},
                    },
                },
                "error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    payload = build_pairwise_review_evidence(
        candidate_request_path=source,
        pairwise_output_path=output,
        top_n=2,
        outpath=tmp_path / "pairwise_evidence.json",
    )

    evidence = payload["evidence"]["X01"]
    assert evidence["PGS000002"]["policy"].startswith("Auxiliary LLM head-to-head arguments only")
    assert evidence["PGS000002"]["head_to_head_reviews"][0]["outcome"] == "preferred"
    assert evidence["PGS000001"]["head_to_head_reviews"][0]["outcome"] == "not_preferred"
    assert "tally" in evidence["PGS000001"]["policy"]


def test_build_switch_policy_predictions_uses_global_thresholds(tmp_path) -> None:
    proposed = tmp_path / "proposed.json"
    league = tmp_path / "league.json"
    proposed.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "source_bundle_id": "source_a",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    },
                    {
                        "target_id": "X02",
                        "primary_pgs_id": "PGS000003",
                        "source_bundle_id": "source_c",
                        "frontier_pgs_ids": ["PGS000003", "PGS000004"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    league.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "source_bundle_id": "source_b",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                        "pairwise_wins": {"PGS000001": 7, "PGS000002": 8},
                    },
                    {
                        "target_id": "X02",
                        "primary_pgs_id": "PGS000004",
                        "source_bundle_id": "source_d",
                        "frontier_pgs_ids": ["PGS000004", "PGS000003"],
                        "pairwise_wins": {"PGS000003": 9, "PGS000004": 8},
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    rows = build_switch_policy_predictions(
        proposed_predictions_path=proposed,
        league_predictions_path=league,
        outpath=tmp_path / "policy.json",
        challenger_min_wins=8,
        proposed_max_wins=8,
    )

    assert rows[0]["primary_pgs_id"] == "PGS000002"
    assert rows[0]["source_bundle_id"] == "source_b"
    assert rows[1]["primary_pgs_id"] == "PGS000003"
    assert rows[1]["source_bundle_id"] == "source_c"
