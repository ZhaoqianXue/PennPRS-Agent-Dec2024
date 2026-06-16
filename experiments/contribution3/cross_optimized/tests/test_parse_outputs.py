from __future__ import annotations

import json

from experiments.contribution3.cross_optimized.batch.parse_outputs import parse_stage_a, parse_stage_b, parse_stage_c


def test_parse_stage_a_unions_selected_and_frontier_bundle_ids(tmp_path) -> None:
    output = tmp_path / "stage_a_output.jsonl"
    parsed = tmp_path / "selection.json"
    body = {
        "output_text": json.dumps(
            {
                "selected_bundle_ids": ["selected_a", "shared"],
                "frontier_bundle_ids": ["shared", "frontier_b"],
                "abstain": False,
                "rationale": "",
                "evidence_cited": [],
            }
        ),
        "usage": {},
    }
    output.write_text(
        json.dumps(
            {
                "custom_id": "stageA__X01",
                "response": {"status_code": 200, "body": body},
                "error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = parse_stage_a(output, parsed)

    assert result["X01"] == ["selected_a", "shared", "frontier_b"]


def test_parse_stage_b_preserves_chunk_id(tmp_path) -> None:
    output = tmp_path / "stage_b_output.jsonl"
    parsed = tmp_path / "predictions.json"
    body = {
        "output_text": json.dumps(
            {
                "primary_pgs_id": "PGS000003",
                "source_bundle_id": "source_3",
                "frontier_pgs_ids": ["PGS000003"],
                "confidence": "moderate",
                "rationale": "chunk rationale",
                "evidence_cited": ["source_3"],
            }
        ),
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }
    output.write_text(
        json.dumps(
            {
                "custom_id": "stageB__X01__chunk03",
                "response": {"status_code": 200, "body": body},
                "error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = parse_stage_b(output, parsed)

    assert result[0]["target_id"] == "X01"
    assert result[0]["chunk_id"] == "chunk03"


def test_parse_stage_c_extracts_final_predictions(tmp_path) -> None:
    output = tmp_path / "stage_c_output.jsonl"
    parsed = tmp_path / "predictions.json"
    body = {
        "output_text": json.dumps(
            {
                "accepted": True,
                "primary_pgs_id": "PGS000002",
                "source_bundle_id": "source_2",
                "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                "issues": [],
                "rationale": "final reconciliation",
            }
        ),
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }
    output.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "response": {"status_code": 200, "body": body},
                "error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = parse_stage_c(output, parsed)

    assert result[0]["target_id"] == "X01"
    assert result[0]["primary_pgs_id"] == "PGS000002"
    assert result[0]["accepted"] is True


def test_parse_stage_c_preserves_tournament_group_id(tmp_path) -> None:
    output = tmp_path / "stage_c_group_output.jsonl"
    parsed = tmp_path / "predictions.json"
    body = {
        "output_text": json.dumps(
            {
                "accepted": True,
                "primary_pgs_id": "PGS000002",
                "source_bundle_id": "source_2",
                "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                "issues": [],
                "rationale": "group finalists",
            }
        ),
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }
    output.write_text(
        json.dumps(
            {
                "custom_id": "stageCgroup__X01__group03",
                "response": {"status_code": 200, "body": body},
                "error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = parse_stage_c(output, parsed)

    assert result[0]["target_id"] == "X01"
    assert result[0]["group_id"] == "group03"
