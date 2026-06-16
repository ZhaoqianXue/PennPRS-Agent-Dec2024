from __future__ import annotations

import json

from experiments.contribution3.cross_optimized.batch.stage_d_panels import (
    build_anchor_challenger_shortlist_lines,
    build_anchor_advisor_panel_lines,
    build_frontier_compression_lines,
    build_llm_union_panel_lines,
)


def _request_line(target_id: str, records: list[dict]) -> dict:
    payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": target_id, "label": "Target", "input_type": "A", "target_source": "extend_trait"},
        "chunk_predictions": [],
        "frontier_pgs_records": records,
        "instruction": "Choose the final primary PGS only from frontier_pgs_records.pgs_id.",
    }
    return {
        "custom_id": f"stageC__{target_id}",
        "method": "POST",
        "url": "/v1/responses",
        "body": {
            "model": "gpt-5.4-nano",
            "input": [
                {"role": "system", "content": "system"},
                {"role": "user", "content": json.dumps(payload, separators=(",", ":"))},
            ],
        },
    }


def test_build_llm_union_panel_uses_current_lane_union_without_scores(tmp_path) -> None:
    source_request = tmp_path / "stage_c.jsonl"
    source_request.write_text(
        json.dumps(
            _request_line(
                "T01",
                [
                    {"pgs_id": "PGS000001", "reported_trait": "A"},
                    {"pgs_id": "PGS000002", "reported_trait": "B"},
                    {"pgs_id": "PGS000003", "reported_trait": "C"},
                ],
            )
        )
        + "\n",
        encoding="utf-8",
    )
    lane_a = tmp_path / "lane_a.json"
    lane_a.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "T01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000001", "PGS999999"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    lane_b = tmp_path / "lane_b.json"
    lane_b.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "T01",
                        "primary_pgs_id": "PGS000003",
                        "frontier_pgs_ids": ["PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_llm_union_panel_lines(
        record_source_request_paths=[source_request],
        prediction_paths=[lane_a, lane_b],
        frontier_limit_per_prediction=2,
        max_candidates=3,
    )

    assert len(lines) == 1
    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert [row["pgs_id"] for row in payload["frontier_pgs_records"]] == [
        "PGS000002",
        "PGS000001",
        "PGS000003",
    ]
    assert payload["candidate_supply_note"]["source"] == "current_llm_lane_union"
    assert payload["candidate_supply_note"]["missing_candidate_ids"] == ["PGS999999"]
    instruction = payload["instruction"].lower()
    assert "vote, score, rank, threshold" in instruction
    assert "hit@top" not in instruction


def test_build_anchor_advisor_panel_separates_non_decision_advisors(tmp_path) -> None:
    source_request = tmp_path / "stage_c.jsonl"
    source_request.write_text(
        json.dumps(
            _request_line(
                "T01",
                [
                    {"pgs_id": "PGS000001", "reported_trait": "Anchor frontier"},
                    {"pgs_id": "PGS000002", "reported_trait": "LLM anchor"},
                    {"pgs_id": "PGS000003", "reported_trait": "Advisor surfaced"},
                    {"pgs_id": "PGS000004", "reported_trait": "Advisor frontier"},
                ],
            )
        )
        + "\n",
        encoding="utf-8",
    )
    anchor = tmp_path / "anchor.json"
    anchor.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "T01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000001", "PGS999999"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor = tmp_path / "advisor.json"
    advisor.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "T01",
                        "primary_pgs_id": "PGS000003",
                        "frontier_pgs_ids": ["PGS000004"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_anchor_advisor_panel_lines(
        record_source_request_paths=[source_request],
        anchor_prediction_paths=[anchor],
        advisor_prediction_paths=[advisor],
        anchor_frontier_limit_per_prediction=2,
        advisor_frontier_limit_per_prediction=0,
        max_candidates=3,
    )

    assert len(lines) == 1
    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert [row["pgs_id"] for row in payload["frontier_pgs_records"]] == [
        "PGS000002",
        "PGS000001",
        "PGS000003",
    ]
    note = payload["candidate_supply_note"]
    assert note["source"] == "current_llm_anchor_and_nondecision_advisor_union"
    assert note["anchor_prediction_file_count"] == 1
    assert note["advisor_prediction_file_count"] == 1
    assert note["missing_candidate_ids"] == ["PGS999999"]
    instruction = payload["instruction"].lower()
    assert "non-decision advisor" in instruction
    assert "not a vote, score, rank, threshold, or authority" in instruction
    assert "hit@top" not in instruction
    assert "evaluation matrix" not in instruction


def test_build_anchor_advisor_panel_can_keep_only_source_equivalent_challengers(tmp_path) -> None:
    source_request = tmp_path / "stage_c.jsonl"
    source_request.write_text(
        json.dumps(
            _request_line(
                "T01",
                [
                    {"pgs_id": "PGS000001", "reported_trait": "Anchor", "mapped_trait_ids": ["MONDO_1"]},
                    {"pgs_id": "PGS000002", "reported_trait": "Same source", "mapped_trait_ids": ["MONDO_1"]},
                    {"pgs_id": "PGS000003", "reported_trait": "Different source", "mapped_trait_ids": ["MONDO_2"]},
                ],
            )
        )
        + "\n",
        encoding="utf-8",
    )
    anchor = tmp_path / "anchor.json"
    anchor.write_text(
        json.dumps(
            {
                "predictions": [
                    {"target_id": "T01", "primary_pgs_id": "PGS000001", "frontier_pgs_ids": []}
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor = tmp_path / "advisor.json"
    advisor.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "T01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000003"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_anchor_advisor_panel_lines(
        record_source_request_paths=[source_request],
        anchor_prediction_paths=[anchor],
        advisor_prediction_paths=[advisor],
        anchor_frontier_limit_per_prediction=0,
        advisor_frontier_limit_per_prediction=2,
        max_candidates=4,
        source_equivalent_challengers_only=True,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert [row["pgs_id"] for row in payload["frontier_pgs_records"]] == ["PGS000001", "PGS000002"]
    assert payload["candidate_supply_note"]["source_equivalent_challengers_only"] is True


def test_build_anchor_challenger_shortlist_reviews_anchor_without_making_it_authority(tmp_path) -> None:
    source_request = tmp_path / "stage_c_high_recall.jsonl"
    source_request.write_text(
        json.dumps(
            _request_line(
                "T01",
                [
                    {"pgs_id": "PGS000001", "reported_trait": "Anchor source"},
                    {"pgs_id": "PGS000002", "reported_trait": "Challenger source"},
                    {"pgs_id": "PGS000003", "reported_trait": "Alternative source"},
                ],
            )
        )
        + "\n",
        encoding="utf-8",
    )
    anchor = tmp_path / "anchor_prediction.json"
    anchor.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "T01",
                        "primary_pgs_id": "PGS000002",
                        "source_bundle_id": "source_b",
                        "frontier_pgs_ids": ["PGS000001"],
                        "issues": ["uncertain bridge"],
                        "rationale": "The current anchor favors PGS000002 from provided metadata.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_anchor_challenger_shortlist_lines(
        record_source_request_paths=[source_request],
        anchor_prediction_path=anchor,
        max_candidates=3,
        max_frontier_ids=2,
    )

    assert len(lines) == 1
    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["schema_version"] == "cross_optimized.stage_c.anchor_challenger_shortlist.v1"
    assert payload["anchor_decision"]["primary_pgs_id"] == "PGS000002"
    assert payload["anchor_decision"]["frontier_pgs_ids"] == ["PGS000001"]
    assert [row["pgs_id"] for row in payload["frontier_pgs_records"]] == [
        "PGS000002",
        "PGS000001",
        "PGS000003",
    ]
    note = payload["candidate_supply_note"]
    assert note["source"] == "anchor_challenger_high_recall_shortlist"
    assert note["anchor_primary_present"] is True
    instruction = payload["instruction"].lower()
    assert "not authority" in instruction
    assert "not a vote, score, rank, threshold, or rule" in instruction
    for forbidden in [
        "hit@top",
        "evaluation matrix",
        "oracle",
        "target rank",
        "tail",
        "benchmark",
    ]:
        assert forbidden not in instruction


def test_build_frontier_compression_lines_keeps_llm_led_low_noise_panel(tmp_path) -> None:
    source_request = tmp_path / "stage_c_high_recall.jsonl"
    source_request.write_text(
        json.dumps(
            _request_line(
                "T01",
                [
                    {"pgs_id": "PGS000001", "reported_trait": "Candidate one"},
                    {"pgs_id": "PGS000002", "reported_trait": "Candidate two"},
                    {"pgs_id": "PGS000003", "reported_trait": "Candidate three"},
                ],
            )
        )
        + "\n",
        encoding="utf-8",
    )

    lines = build_frontier_compression_lines(
        record_source_request_paths=[source_request],
        max_candidates=3,
        target_frontier_size=2,
    )

    assert len(lines) == 1
    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["schema_version"] == "cross_optimized.stage_c.frontier_compression.v1"
    assert [row["pgs_id"] for row in payload["frontier_pgs_records"]] == [
        "PGS000001",
        "PGS000002",
        "PGS000003",
    ]
    assert payload["candidate_supply_note"]["source"] == "llm_frontier_compression"
    assert payload["candidate_supply_note"]["target_frontier_size"] == 2
    instruction = payload["instruction"].lower()
    assert "compress this high-recall panel" in instruction
    assert "same source-then-model checklist" in instruction
    assert "candidate order is context only" in instruction
    for forbidden in [
        "hit@top",
        "evaluation matrix",
        "oracle",
        "target rank",
        "predicted-risk tail",
        "benchmark",
    ]:
        assert forbidden not in instruction
