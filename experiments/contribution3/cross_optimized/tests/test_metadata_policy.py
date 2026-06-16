from __future__ import annotations

import json

from experiments.contribution3.cross_optimized.batch.metadata_policy import (
    build_frontier_vote_window_policy_predictions,
    build_llm_count_ensemble_policy_predictions,
    build_record_count_policy_predictions,
    build_record_count_vote_guard_window_policy_predictions,
    build_record_count_window_policy_predictions,
)


def test_record_count_policy_chooses_highest_record_count_in_top_n(tmp_path) -> None:
    request = tmp_path / "stage_c.jsonl"
    request.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "method": "POST",
                "url": "/v1/responses",
                "body": {
                    "input": [
                        {"role": "system", "content": "unused"},
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "target": {"target_id": "X01"},
                                    "frontier_pgs_records": [
                                        {
                                            "pgs_id": "PGS000001",
                                            "performance": {
                                                "performance_record_count": 2,
                                                "best_auc": 0.99,
                                            },
                                            "source_bundles": [{"bundle_id": "source_1"}],
                                        },
                                        {
                                            "pgs_id": "PGS000002",
                                            "performance": {
                                                "performance_record_count": 8,
                                                "evaluation_sample_total": 100,
                                                "best_auc": 0.7,
                                            },
                                            "source_bundles": [{"bundle_id": "source_2"}],
                                        },
                                    ],
                                }
                            ),
                        },
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    rows = build_record_count_policy_predictions(
        candidate_request_path=request,
        top_n=2,
        outpath=tmp_path / "predictions.json",
    )

    assert rows[0]["primary_pgs_id"] == "PGS000002"
    assert rows[0]["source_bundle_id"] == "source_2"
    assert rows[0]["frontier_pgs_ids"] == ["PGS000002", "PGS000001"]


def test_record_count_window_policy_switches_to_stronger_challenge_window(tmp_path) -> None:
    request = tmp_path / "stage_c.jsonl"
    records = [
        {
            "pgs_id": f"PGS00000{idx}",
            "performance": {
                "performance_record_count": record_count,
                "best_auc": 0.5 + idx / 100,
            },
            "source_bundles": [{"bundle_id": f"source_{idx}"}],
        }
        for idx, record_count in enumerate([2, 4, 9, 3, 5, 7, 10, 1], start=1)
    ]
    request.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "unused"},
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "target": {"target_id": "X01"},
                                    "frontier_pgs_records": records,
                                }
                            ),
                        },
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    rows = build_record_count_window_policy_predictions(
        candidate_request_path=request,
        base_top_n=6,
        challenge_top_n=7,
        min_record_margin=1,
        outpath=tmp_path / "predictions.json",
    )

    assert rows[0]["primary_pgs_id"] == "PGS000007"
    assert rows[0]["source_bundle_id"] == "source_7"
    assert rows[0]["frontier_pgs_ids"][:3] == ["PGS000007", "PGS000003", "PGS000001"]


def test_record_count_window_policy_keeps_base_without_record_count_margin(tmp_path) -> None:
    request = tmp_path / "stage_c.jsonl"
    records = [
        {
            "pgs_id": f"PGS00000{idx}",
            "performance": {
                "performance_record_count": record_count,
                "best_auc": 0.5 + idx / 100,
            },
            "source_bundles": [{"bundle_id": f"source_{idx}"}],
        }
        for idx, record_count in enumerate([2, 4, 9, 3, 5, 7, 9, 1], start=1)
    ]
    request.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "unused"},
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "target": {"target_id": "X01"},
                                    "frontier_pgs_records": records,
                                }
                            ),
                        },
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    rows = build_record_count_window_policy_predictions(
        candidate_request_path=request,
        base_top_n=6,
        challenge_top_n=7,
        min_record_margin=1,
        outpath=tmp_path / "predictions.json",
    )

    assert rows[0]["primary_pgs_id"] == "PGS000003"
    assert rows[0]["source_bundle_id"] == "source_3"


def test_frontier_vote_window_policy_switches_to_supported_challenger(tmp_path) -> None:
    request = tmp_path / "stage_c.jsonl"
    records = [
        {
            "pgs_id": f"PGS00000{idx}",
            "performance": {"performance_record_count": record_count},
            "stage_b_support": {"frontier_votes": frontier_votes},
            "source_bundles": [{"bundle_id": f"source_{idx}"}],
        }
        for idx, (record_count, frontier_votes) in enumerate(
            [(2, 1), (4, 1), (9, 2), (3, 1), (5, 1), (7, 1), (12, 8), (1, 20)],
            start=1,
        )
    ]
    request.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "unused"},
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "target": {"target_id": "X01"},
                                    "frontier_pgs_records": records,
                                }
                            ),
                        },
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    rows = build_frontier_vote_window_policy_predictions(
        candidate_request_path=request,
        base_top_n=6,
        challenge_top_n=7,
        min_record_margin=1,
        outpath=tmp_path / "predictions.json",
    )

    assert rows[0]["primary_pgs_id"] == "PGS000007"
    assert rows[0]["source_bundle_id"] == "source_7"
    assert rows[0]["frontier_pgs_ids"][:3] == ["PGS000007", "PGS000003", "PGS000001"]


def test_frontier_vote_window_policy_keeps_base_when_supported_challenger_is_smaller(tmp_path) -> None:
    request = tmp_path / "stage_c.jsonl"
    records = [
        {
            "pgs_id": f"PGS00000{idx}",
            "performance": {"performance_record_count": record_count},
            "stage_b_support": {"frontier_votes": frontier_votes},
            "source_bundles": [{"bundle_id": f"source_{idx}"}],
        }
        for idx, (record_count, frontier_votes) in enumerate(
            [(2, 1), (4, 1), (9, 2), (3, 1), (5, 1), (7, 1), (8, 8), (1, 20)],
            start=1,
        )
    ]
    request.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "unused"},
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "target": {"target_id": "X01"},
                                    "frontier_pgs_records": records,
                                }
                            ),
                        },
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    rows = build_frontier_vote_window_policy_predictions(
        candidate_request_path=request,
        base_top_n=6,
        challenge_top_n=7,
        min_record_margin=1,
        outpath=tmp_path / "predictions.json",
    )

    assert rows[0]["primary_pgs_id"] == "PGS000003"
    assert rows[0]["source_bundle_id"] == "source_3"


def test_record_count_vote_guard_window_policy_switches_when_vote_support_is_close(tmp_path) -> None:
    request = tmp_path / "stage_c.jsonl"
    records = [
        {
            "pgs_id": f"PGS00000{idx}",
            "performance": {"performance_record_count": record_count},
            "stage_b_support": {"frontier_votes": frontier_votes},
            "source_bundles": [{"bundle_id": f"source_{idx}"}],
        }
        for idx, (record_count, frontier_votes) in enumerate(
            [(2, 1), (4, 1), (9, 4), (3, 1), (5, 1), (7, 1), (10, 3), (1, 20)],
            start=1,
        )
    ]
    request.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "unused"},
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "target": {"target_id": "X01"},
                                    "frontier_pgs_records": records,
                                }
                            ),
                        },
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    rows = build_record_count_vote_guard_window_policy_predictions(
        candidate_request_path=request,
        base_top_n=6,
        challenge_top_n=7,
        min_record_margin=1,
        min_frontier_vote_delta=-1,
        outpath=tmp_path / "predictions.json",
    )

    assert rows[0]["primary_pgs_id"] == "PGS000007"
    assert rows[0]["source_bundle_id"] == "source_7"


def test_record_count_vote_guard_window_policy_blocks_weakly_supported_challenger(tmp_path) -> None:
    request = tmp_path / "stage_c.jsonl"
    records = [
        {
            "pgs_id": f"PGS00000{idx}",
            "performance": {"performance_record_count": record_count},
            "stage_b_support": {"frontier_votes": frontier_votes},
            "source_bundles": [{"bundle_id": f"source_{idx}"}],
        }
        for idx, (record_count, frontier_votes) in enumerate(
            [(2, 1), (4, 1), (9, 5), (3, 1), (5, 1), (7, 1), (10, 3), (1, 20)],
            start=1,
        )
    ]
    request.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "unused"},
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "target": {"target_id": "X01"},
                                    "frontier_pgs_records": records,
                                }
                            ),
                        },
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    rows = build_record_count_vote_guard_window_policy_predictions(
        candidate_request_path=request,
        base_top_n=6,
        challenge_top_n=7,
        min_record_margin=1,
        min_frontier_vote_delta=-1,
        outpath=tmp_path / "predictions.json",
    )

    assert rows[0]["primary_pgs_id"] == "PGS000003"
    assert rows[0]["source_bundle_id"] == "source_3"


def test_llm_count_ensemble_policy_boosts_close_record_count_candidate(tmp_path) -> None:
    request = tmp_path / "stage_c.jsonl"
    records = [
        {
            "pgs_id": "PGS000001",
            "performance": {"performance_record_count": 100},
            "stage_b_support": {"frontier_votes": 2},
            "source_bundles": [{"bundle_id": "source_1"}],
        },
        {
            "pgs_id": "PGS000002",
            "performance": {"performance_record_count": 90},
            "stage_b_support": {"frontier_votes": 2},
            "source_bundles": [{"bundle_id": "source_2"}],
        },
        {
            "pgs_id": "PGS000003",
            "performance": {"performance_record_count": 1},
            "stage_b_support": {"frontier_votes": 1},
            "source_bundles": [{"bundle_id": "source_3"}],
        },
    ]
    request.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "unused"},
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "target": {"target_id": "X01"},
                                    "frontier_pgs_records": records,
                                }
                            ),
                        },
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    llm_predictions = tmp_path / "llm_predictions.json"
    llm_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    rows = build_llm_count_ensemble_policy_predictions(
        candidate_request_path=request,
        vote_prediction_paths=[llm_predictions],
        llm_count_weight=0.5,
        top_n=3,
        outpath=tmp_path / "predictions.json",
    )

    assert rows[0]["primary_pgs_id"] == "PGS000002"
    assert rows[0]["source_bundle_id"] == "source_2"


def test_llm_count_ensemble_policy_falls_back_to_record_count_without_votes(tmp_path) -> None:
    request = tmp_path / "stage_c.jsonl"
    records = [
        {
            "pgs_id": "PGS000001",
            "performance": {"performance_record_count": 100},
            "source_bundles": [{"bundle_id": "source_1"}],
        },
        {
            "pgs_id": "PGS000002",
            "performance": {"performance_record_count": 90},
            "source_bundles": [{"bundle_id": "source_2"}],
        },
    ]
    request.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "unused"},
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "target": {"target_id": "X01"},
                                    "frontier_pgs_records": records,
                                }
                            ),
                        },
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    llm_predictions = tmp_path / "llm_predictions.json"
    llm_predictions.write_text(json.dumps({"predictions": []}), encoding="utf-8")

    rows = build_llm_count_ensemble_policy_predictions(
        candidate_request_path=request,
        vote_prediction_paths=[llm_predictions],
        llm_count_weight=0.5,
        top_n=2,
        outpath=tmp_path / "predictions.json",
    )

    assert rows[0]["primary_pgs_id"] == "PGS000001"
    assert rows[0]["source_bundle_id"] == "source_1"
