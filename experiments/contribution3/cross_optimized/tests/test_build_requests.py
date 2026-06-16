from __future__ import annotations

import json

import pandas as pd

from experiments.contribution3.cross_optimized.batch.build_requests import (
    AGENT_VISIBLE_REVIEW_MODES,
    _agent_visible_review_mode,
    _coverage_lane_pgs_rows,
    _stage_d_instruction,
    build_stage_a_lines,
    build_stage_b_lines,
    build_stage_c_group_lines,
    build_stage_c_lines,
    _stage_d_audit_instruction,
    build_stage_d_audit_lines,
    build_stage_d_evidence_lines,
)
from experiments.contribution3.cross_optimized.batch.pairwise_league import PAIRWISE_SYSTEM_PROMPT
from experiments.contribution3.cross_optimized.batch.prompts import static_system_prompt


def test_stage_a_request_builder_scans_for_leaks(tmp_path) -> None:
    catalog = tmp_path / "catalog.json"
    targets = tmp_path / "targets.csv"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": "cross_optimized.v1",
                "pgs_records": [],
                "bundles": [
                    {
                        "bundle_id": "source",
                        "canonical_label": "Related source",
                        "bundle_type": "binary",
                        "aliases": ["Related source"],
                        "candidate_pgs_ids": ["PGS000001"],
                        "n_models": 1,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "input_type": "A",
                "target_source": "extend_trait",
                "input_icd": "X01",
                "input_ontology": "",
                "input_description": "Target disease",
                "selected": True,
            }
        ]
    ).to_csv(targets, index=False)

    lines = build_stage_a_lines(
        catalog_path=catalog,
        targets_path=targets,
        prompt_candidate_cap=10,
        max_dossier_bundles=10,
    )

    assert len(lines) == 1
    body = lines[0]["body"]
    payload = json.loads(body["input"][1]["content"])
    assert payload["target"]["target_id"] == "X01"
    assert "benchmark_top_model_id" not in body["input"][1]["content"]


def test_stage_b_canonicalizes_zero_padded_bundle_ids(tmp_path) -> None:
    catalog = tmp_path / "catalog.json"
    targets = tmp_path / "targets.csv"
    stage_a_selection = tmp_path / "stage_a_selection.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": "cross_optimized.v1",
                "pgs_records": [
                    {
                        "pgs_id": "PGS000001",
                        "mapped_trait_labels": ["sleep disorder"],
                    }
                ],
                "bundles": [
                    {
                        "bundle_id": "mondo_0100081",
                        "canonical_label": "sleep disorder",
                        "bundle_type": "binary",
                        "aliases": ["sleep disorder"],
                        "candidate_pgs_ids": ["PGS000001"],
                        "n_models": 1,
                        "source_efo_ids": [],
                        "source_mondo_ids": ["MONDO_0100081"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "input_type": "A",
                "target_source": "extend_trait",
                "input_icd": "F60",
                "input_ontology": "",
                "input_description": "Specific personality disorders",
                "selected": True,
            }
        ]
    ).to_csv(targets, index=False)
    stage_a_selection.write_text(json.dumps({"F60": ["mondo_0000100081"]}), encoding="utf-8")

    lines = build_stage_b_lines(
        stage_a_selection_path=stage_a_selection,
        catalog_path=catalog,
        targets_path=targets,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert [row["bundle"]["bundle_id"] for row in payload["source_bundles"]] == ["mondo_0100081"]


def test_static_prompt_contains_general_clinical_measurement_calibration() -> None:
    prompt = static_system_prompt("stage_c")

    assert "Clinical-vs-Measurement Calibration" in prompt
    assert "not a disease-category rule" in prompt
    assert "quantitative biomarker" in prompt
    assert "Allowed Inputs" in prompt
    assert "Treat missing evidence as unavailable" in prompt


def test_static_prompt_contains_same_source_pgs_model_calibration() -> None:
    prompt = static_system_prompt("stage_c")

    assert "Same-Source PGS Model Calibration" in prompt
    assert "headline metrics are not automatically comparable" in prompt
    assert "same source axis" in prompt
    assert "target-portable PRS signal" in prompt
    for fragment in ["hit@top", "evaluation matrix", "held-out", "oracle", "target rank"]:
        assert fragment not in prompt.lower()


def test_static_prompt_contains_binary_effect_size_calibration() -> None:
    prompt = static_system_prompt("stage_c")

    assert "Binary and Time-to-Event Effect Calibration" in prompt
    assert "odds ratios, hazard ratios, beta estimates" in prompt
    assert "clinical diagnosis" in prompt
    assert "not a formula" in prompt
    for fragment in ["hit@top", "evaluation matrix", "held-out", "oracle", "target rank"]:
        assert fragment not in prompt.lower()


def test_static_prompt_contains_general_tool_evidence_calibration() -> None:
    prompt = static_system_prompt("stage_c")

    assert "Tool Evidence Calibration" in prompt
    assert "OpenTargets" in prompt
    assert "auxiliary context" in prompt
    assert "not a formula" in prompt
    assert "not authority" in prompt
    assert "source-axis coherence" in prompt
    for fragment in [
        "hit@top",
        "top 0.5",
        "top-25",
        "evaluation matrix",
        "held-out",
        "oracle",
        "target rank",
        "benchmark",
        "predicted-risk tail",
    ]:
        assert fragment not in prompt.lower()


def test_llm_visible_prompts_do_not_name_hidden_evaluation_artifacts() -> None:
    prompts = [static_system_prompt(stage) for stage in ("stage_a", "stage_b", "stage_c")]
    prompts.append(PAIRWISE_SYSTEM_PROMPT)
    prompt_text = "\n".join(prompts).lower()

    forbidden_fragments = [
        "held-out evaluation",
        "evaluation matrix",
        "empirical oracle",
        "old target-level rank",
        "old target-specific rank",
        "previous run outcome",
        "target-specific learned answer",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in prompt_text


def test_stage_d_llm_visible_text_does_not_name_benchmark_objectives() -> None:
    forbidden_fragments = [
        "hit@top",
        "top 0.5",
        "top 1",
        "top-25",
        "top 25",
        "early-tail",
        "early_tail",
        "early-hit",
        "extreme-tail",
        "extreme_tail",
        "extreme top",
        "extreme-top",
        "very top tail",
        "predicted-risk tail",
        "tail precision",
        "precision",
        "mean performance",
        "broad coverage",
    ]
    for mode in AGENT_VISIBLE_REVIEW_MODES:
        text = f"{_agent_visible_review_mode(mode)}\n{_stage_d_instruction(mode, 'llm_lane_01')}".lower()
        for fragment in forbidden_fragments:
            assert fragment not in text


def test_stage_d_source_model_symmetric_review_is_llm_led_without_benchmark_terms() -> None:
    text = (
        f"{_agent_visible_review_mode('source_model_symmetric_review')}\n"
        f"{_stage_d_instruction('source_model_symmetric_review', '')}"
    ).lower()

    assert "symmetric source-then-model" in text
    assert "source-axis bridge" in text
    assert "model evidence" in text
    assert "not a formula" in text
    for fragment in [
        "hit@top",
        "top 0.5",
        "evaluation matrix",
        "held-out",
        "oracle",
        "target rank",
        "predicted-risk tail",
    ]:
        assert fragment not in text


def test_stage_d_structured_source_model_review_is_position_neutral() -> None:
    text = (
        f"{_agent_visible_review_mode('structured_source_model_review')}\n"
        f"{_stage_d_instruction('structured_source_model_review', '')}"
    ).lower()

    assert "structured source-model review" in text
    assert "same qualitative checklist" in text
    assert "candidate order is not evidence" in text
    assert "do not overcorrect toward later cards" in text
    assert "source bridge" in text
    assert "model evidence" in text
    for fragment in [
        "hit@top",
        "top 0.5",
        "evaluation matrix",
        "held-out",
        "oracle",
        "target rank",
        "predicted-risk tail",
    ]:
        assert fragment not in text


def test_stage_d_same_source_effect_size_audit_is_general_trait_guidance() -> None:
    text = (
        f"{_agent_visible_review_mode('same_source_effect_size_audit_review')}\n"
        f"{_stage_d_instruction('same_source_effect_size_audit_review', '')}"
    ).lower()

    assert "same-source effect-size audit" in text
    assert "odds ratios, hazard ratios, beta estimates" in text
    assert "not a formula" in text
    assert "no specific-trait" in text
    for fragment in [
        "hit@top",
        "top 0.5",
        "evaluation matrix",
        "held-out",
        "oracle",
        "target rank",
        "predicted-risk tail",
    ]:
        assert fragment not in text


def test_stage_d_anchor_challenger_gate_is_llm_led_general_review() -> None:
    text = (
        f"{_agent_visible_review_mode('anchor_challenger_gate_review')}\n"
        f"{_stage_d_instruction('anchor_challenger_gate_review', 'llm_lane_01')}"
    ).lower()

    assert "anchor-challenger gate" in text
    assert "llm-harness prior" in text
    assert "not an automatic winner" in text
    assert "coherent source-axis bridge" in text
    assert "materially stronger visible pgs evidence" in text
    assert "not a formula" in text
    for fragment in [
        "hit@top",
        "top 0.5",
        "evaluation matrix",
        "held-out",
        "oracle",
        "target rank",
        "predicted-risk tail",
    ]:
        assert fragment not in text


def test_stage_b_filters_pgs_records_to_evaluable_universe(tmp_path, monkeypatch) -> None:
    catalog = tmp_path / "catalog.json"
    targets = tmp_path / "targets.csv"
    stage_a_selection = tmp_path / "stage_a_selection.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": "cross_optimized.v1",
                "pgs_records": [
                    {"pgs_id": "PGS000001", "mapped_trait_labels": ["kept"]},
                    {"pgs_id": "PGS999999", "mapped_trait_labels": ["not evaluable"]},
                ],
                "bundles": [
                    {
                        "bundle_id": "source",
                        "canonical_label": "source",
                        "bundle_type": "binary",
                        "aliases": ["source"],
                        "candidate_pgs_ids": ["PGS000001", "PGS999999"],
                        "n_models": 2,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "input_type": "A",
                "target_source": "extend_trait",
                "input_icd": "X01",
                "input_ontology": "",
                "input_description": "Target disease",
                "selected": True,
            }
        ]
    ).to_csv(targets, index=False)
    stage_a_selection.write_text(json.dumps({"X01": ["source"]}), encoding="utf-8")
    monkeypatch.setattr(
        "experiments.contribution3.cross_optimized.batch.build_requests.source_universe_pgs_ids",
        lambda target_source: {"PGS000001"},
    )

    lines = build_stage_b_lines(
        stage_a_selection_path=stage_a_selection,
        catalog_path=catalog,
        targets_path=targets,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert [row["pgs_id"] for row in payload["source_bundles"][0]["pgs_records"]] == ["PGS000001"]


def test_stage_b_retrieval_floor_adds_harness_candidates(tmp_path, monkeypatch) -> None:
    catalog = tmp_path / "catalog.json"
    targets = tmp_path / "targets.csv"
    stage_a_selection = tmp_path / "stage_a_selection.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": "cross_optimized.v1",
                "pgs_records": [
                    {"pgs_id": "PGS000001", "mapped_trait_labels": ["selected"]},
                    {"pgs_id": "PGS000002", "mapped_trait_labels": ["floor"]},
                ],
                "bundles": [
                    {
                        "bundle_id": "selected",
                        "canonical_label": "Selected source",
                        "bundle_type": "binary",
                        "aliases": ["Selected source"],
                        "candidate_pgs_ids": ["PGS000001"],
                        "n_models": 1,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    },
                    {
                        "bundle_id": "floor",
                        "canonical_label": "Target-adjacent floor source",
                        "bundle_type": "binary",
                        "aliases": ["Target adjacent"],
                        "candidate_pgs_ids": ["PGS000002"],
                        "n_models": 1,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
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
    ).to_csv(targets, index=False)
    stage_a_selection.write_text(json.dumps({"X01": ["selected"]}), encoding="utf-8")
    monkeypatch.setattr(
        "experiments.contribution3.cross_optimized.batch.build_requests.source_universe_pgs_ids",
        lambda target_source: {"PGS000001", "PGS000002"},
    )

    lines = build_stage_b_lines(
        stage_a_selection_path=stage_a_selection,
        catalog_path=catalog,
        targets_path=targets,
        retrieval_floor_count=1,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert [row["bundle"]["bundle_id"] for row in payload["source_bundles"]] == ["selected", "floor"]


def test_stage_b_prioritizes_quality_metadata_before_pgs_cap(tmp_path, monkeypatch) -> None:
    catalog = tmp_path / "catalog.json"
    targets = tmp_path / "targets.csv"
    stage_a_selection = tmp_path / "stage_a_selection.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": "cross_optimized.v1",
                "pgs_records": [
                    {
                        "pgs_id": "PGS000001",
                        "method": "GWAS hits",
                        "variant_count": 10,
                        "ancestry_evaluation": "",
                        "mapped_trait_labels": ["source"],
                    },
                    {
                        "pgs_id": "PGS000002",
                        "method": "PRS-CSx",
                        "variant_count": 1000000,
                        "ancestry_evaluation": "Multi-ancestry (including European):100",
                        "mapped_trait_labels": ["source"],
                    },
                ],
                "bundles": [
                    {
                        "bundle_id": "source",
                        "canonical_label": "Source",
                        "bundle_type": "binary",
                        "aliases": ["Source"],
                        "candidate_pgs_ids": ["PGS000001", "PGS000002"],
                        "n_models": 2,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "input_type": "A",
                "target_source": "extend_trait",
                "input_icd": "X01",
                "input_ontology": "",
                "input_description": "Target disease",
                "selected": True,
            }
        ]
    ).to_csv(targets, index=False)
    stage_a_selection.write_text(json.dumps({"X01": ["source"]}), encoding="utf-8")
    monkeypatch.setattr(
        "experiments.contribution3.cross_optimized.batch.build_requests.source_universe_pgs_ids",
        lambda target_source: {"PGS000001", "PGS000002"},
    )

    lines = build_stage_b_lines(
        stage_a_selection_path=stage_a_selection,
        catalog_path=catalog,
        targets_path=targets,
        pgs_per_bundle_cap=1,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert [row["pgs_id"] for row in payload["source_bundles"][0]["pgs_records"]] == ["PGS000002"]


def test_stage_b_preserves_performance_rich_candidate_inside_pgs_cap(tmp_path, monkeypatch) -> None:
    catalog = tmp_path / "catalog.json"
    targets = tmp_path / "targets.csv"
    stage_a_selection = tmp_path / "stage_a_selection.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": "cross_optimized.v1",
                "pgs_records": [
                    {
                        "pgs_id": "PGS000001",
                        "method": "PRS-CSx",
                        "method_details": "",
                        "variant_count": 1000000,
                        "ancestry_evaluation": "European:100",
                        "mapped_trait_labels": ["source"],
                        "performance": {"performance_record_count": 0},
                    },
                    {
                        "pgs_id": "PGS000002",
                        "method": "PRS-CS",
                        "method_details": "",
                        "variant_count": 900000,
                        "ancestry_evaluation": "European:100",
                        "mapped_trait_labels": ["source"],
                        "performance": {"performance_record_count": 0},
                    },
                    {
                        "pgs_id": "PGS000003",
                        "method": "BOLT-LMM",
                        "method_details": "",
                        "variant_count": 100,
                        "ancestry_evaluation": "European:100",
                        "mapped_trait_labels": ["source"],
                        "performance": {
                            "performance_record_count": 4,
                            "evaluation_sample_max": 50000,
                            "best_r2": 0.13,
                        },
                    },
                ],
                "bundles": [
                    {
                        "bundle_id": "source",
                        "canonical_label": "Source",
                        "bundle_type": "continuous",
                        "aliases": ["Source"],
                        "candidate_pgs_ids": ["PGS000001", "PGS000002", "PGS000003"],
                        "n_models": 3,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "input_type": "A",
                "target_source": "extend_trait",
                "input_icd": "X01",
                "input_ontology": "",
                "input_description": "Target disease",
                "selected": True,
            }
        ]
    ).to_csv(targets, index=False)
    stage_a_selection.write_text(json.dumps({"X01": ["source"]}), encoding="utf-8")
    monkeypatch.setattr(
        "experiments.contribution3.cross_optimized.batch.build_requests.source_universe_pgs_ids",
        lambda target_source: {"PGS000001", "PGS000002", "PGS000003"},
    )

    lines = build_stage_b_lines(
        stage_a_selection_path=stage_a_selection,
        catalog_path=catalog,
        targets_path=targets,
        pgs_per_bundle_cap=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    exposed_ids = [row["pgs_id"] for row in payload["source_bundles"][0]["pgs_records"]]
    assert "PGS000001" in exposed_ids
    assert "PGS000003" in exposed_ids


def test_stage_b_compacts_pgs_records_for_large_batch_context(tmp_path, monkeypatch) -> None:
    catalog = tmp_path / "catalog.json"
    targets = tmp_path / "targets.csv"
    stage_a_selection = tmp_path / "stage_a_selection.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": "cross_optimized.v1",
                "pgs_records": [
                    {
                        "pgs_id": "PGS000001",
                        "pgs_name": "Verbose name",
                        "reported_trait": "Source trait",
                        "mapped_trait_labels": ["Source trait"],
                        "mapped_trait_ids": ["EFO_000001"],
                        "method": "PRS-CSx",
                        "method_details": "very long details " * 50,
                        "variant_count": 1000,
                        "ancestry_evaluation": "European:100",
                        "publication": {"doi": "10/example", "pmid": "123"},
                        "performance": {
                            "performance_record_count": 2,
                            "sample_set_count": 0,
                            "evaluation_sample_total": 0,
                            "best_auc": None,
                            "best_r2": 0.2,
                            "evaluation_ancestry": [],
                        },
                    }
                ],
                "bundles": [
                    {
                        "bundle_id": "source",
                        "canonical_label": "Source",
                        "bundle_type": "continuous",
                        "aliases": ["Source"],
                        "candidate_pgs_ids": ["PGS000001"],
                        "n_models": 1,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "input_type": "A",
                "target_source": "extend_trait",
                "input_icd": "X01",
                "input_ontology": "",
                "input_description": "Target disease",
                "selected": True,
            }
        ]
    ).to_csv(targets, index=False)
    stage_a_selection.write_text(json.dumps({"X01": ["source"]}), encoding="utf-8")
    monkeypatch.setattr(
        "experiments.contribution3.cross_optimized.batch.build_requests.source_universe_pgs_ids",
        lambda target_source: {"PGS000001"},
    )

    lines = build_stage_b_lines(
        stage_a_selection_path=stage_a_selection,
        catalog_path=catalog,
        targets_path=targets,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    pgs_record = payload["source_bundles"][0]["pgs_records"][0]
    assert "publication" not in pgs_record
    assert "pgs_name" not in pgs_record
    assert len(pgs_record["method_details"]) <= 90
    assert pgs_record["performance"] == {
        "performance_record_count": 2,
        "best_r2": 0.2,
    }


def test_stage_b_can_chunk_source_bundles_for_local_pickers(tmp_path, monkeypatch) -> None:
    catalog = tmp_path / "catalog.json"
    targets = tmp_path / "targets.csv"
    stage_a_selection = tmp_path / "stage_a_selection.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": "cross_optimized.v1",
                "pgs_records": [
                    {"pgs_id": f"PGS{i:06d}", "mapped_trait_labels": [f"source {i}"]}
                    for i in range(1, 5)
                ],
                "bundles": [
                    {
                        "bundle_id": f"source_{i}",
                        "canonical_label": f"Source {i}",
                        "bundle_type": "binary",
                        "aliases": [f"Source {i}"],
                        "candidate_pgs_ids": [f"PGS{i:06d}"],
                        "n_models": 1,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    }
                    for i in range(1, 5)
                ],
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "input_type": "A",
                "target_source": "extend_trait",
                "input_icd": "X01",
                "input_ontology": "",
                "input_description": "Target disease",
                "selected": True,
            }
        ]
    ).to_csv(targets, index=False)
    stage_a_selection.write_text(
        json.dumps({"X01": ["source_1", "source_2", "source_3", "source_4"]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "experiments.contribution3.cross_optimized.batch.build_requests.source_universe_pgs_ids",
        lambda target_source: {f"PGS{i:06d}" for i in range(1, 5)},
    )

    lines = build_stage_b_lines(
        stage_a_selection_path=stage_a_selection,
        catalog_path=catalog,
        targets_path=targets,
        retrieval_floor_count=0,
        bundle_chunk_size=2,
    )

    assert [line["custom_id"] for line in lines] == ["stageB__X01__chunk00", "stageB__X01__chunk01"]
    payloads = [json.loads(line["body"]["input"][1]["content"]) for line in lines]
    assert [row["bundle"]["bundle_id"] for row in payloads[0]["source_bundles"]] == ["source_1", "source_2"]
    assert [row["bundle"]["bundle_id"] for row in payloads[1]["source_bundles"]] == ["source_3", "source_4"]
    assert "8-12 diverse frontier_pgs_ids" in payloads[0]["instruction"]
    assert lines[0]["body"]["max_output_tokens"] >= 2400
    assert "rationale" in payloads[0]["instruction"]
    assert "<=120 words" in payloads[0]["instruction"]


def test_stage_c_groups_chunk_frontiers_for_reconciliation(tmp_path) -> None:
    catalog = tmp_path / "catalog.json"
    targets = tmp_path / "targets.csv"
    proposals = tmp_path / "proposals.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": "cross_optimized.v1",
                "pgs_records": [
                    {"pgs_id": "PGS000001", "reported_trait": "Trait 1", "mapped_trait_labels": ["Trait 1"]},
                    {"pgs_id": "PGS000002", "reported_trait": "Trait 2", "mapped_trait_labels": ["Trait 2"]},
                ],
                "bundles": [
                    {
                        "bundle_id": "source_1",
                        "canonical_label": "Source 1",
                        "bundle_type": "binary",
                        "aliases": ["Source 1"],
                        "candidate_pgs_ids": ["PGS000001"],
                        "n_models": 1,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    },
                    {
                        "bundle_id": "source_2",
                        "canonical_label": "Source 2",
                        "bundle_type": "binary",
                        "aliases": ["Source 2"],
                        "candidate_pgs_ids": ["PGS000002"],
                        "n_models": 1,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "input_type": "A",
                "target_source": "extend_trait",
                "input_icd": "X01",
                "input_ontology": "",
                "input_description": "Target disease",
                "selected": True,
            }
        ]
    ).to_csv(targets, index=False)
    proposals.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "chunk_id": "chunk00",
                        "primary_pgs_id": "PGS000001",
                        "source_bundle_id": "source_1",
                        "frontier_pgs_ids": ["PGS000001"],
                        "confidence": "moderate",
                        "rationale": "first chunk",
                    },
                    {
                        "target_id": "X01",
                        "chunk_id": "chunk01",
                        "primary_pgs_id": "PGS000002",
                        "source_bundle_id": "source_2",
                        "frontier_pgs_ids": ["PGS000002"],
                        "confidence": "moderate",
                        "rationale": "second chunk",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_c_lines(proposals_path=proposals, catalog_path=catalog, targets_path=targets)

    assert [line["custom_id"] for line in lines] == ["stageC__X01"]
    assert "cross-bundle Primary Reconciler" in lines[0]["body"]["input"][0]["content"]
    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert [row["chunk_id"] for row in payload["chunk_predictions"]] == ["chunk00", "chunk01"]
    assert [row["pgs_id"] for row in payload["frontier_pgs_records"]] == ["PGS000001", "PGS000002"]
    assert payload["frontier_pgs_records"][0]["source_bundles"] == [
        {"bundle_id": "source_1", "canonical_label": "Source 1", "aliases": ["Source 1"]}
    ]
    support = {row["pgs_id"]: row["stage_b_support"] for row in payload["frontier_pgs_records"]}
    assert support["PGS000001"]["primary_votes"] == 1
    assert support["PGS000001"]["frontier_votes"] == 1
    assert support["PGS000001"]["chunk_count"] == 1
    assert support["PGS000001"]["confidence_counts"] == {"moderate": 1}
    assert "stage_b_support" in payload["instruction"]


def test_stage_c_group_builder_splits_large_frontier_for_tournament(tmp_path) -> None:
    catalog = tmp_path / "catalog.json"
    targets = tmp_path / "targets.csv"
    proposals = tmp_path / "proposals.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": "cross_optimized.v1",
                "pgs_records": [
                    {"pgs_id": "PGS000001", "reported_trait": "Trait 1", "mapped_trait_labels": ["Trait 1"]},
                    {"pgs_id": "PGS000002", "reported_trait": "Trait 2", "mapped_trait_labels": ["Trait 2"]},
                ],
                "bundles": [
                    {
                        "bundle_id": "source_1",
                        "canonical_label": "Source 1",
                        "bundle_type": "binary",
                        "aliases": ["Source 1"],
                        "candidate_pgs_ids": ["PGS000001"],
                        "n_models": 1,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    },
                    {
                        "bundle_id": "source_2",
                        "canonical_label": "Source 2",
                        "bundle_type": "binary",
                        "aliases": ["Source 2"],
                        "candidate_pgs_ids": ["PGS000002"],
                        "n_models": 1,
                        "source_efo_ids": [],
                        "source_mondo_ids": [],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "input_type": "A",
                "target_source": "extend_trait",
                "input_icd": "X01",
                "input_ontology": "",
                "input_description": "Target disease",
                "selected": True,
            }
        ]
    ).to_csv(targets, index=False)
    proposals.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "chunk_id": "chunk00",
                        "primary_pgs_id": "PGS000001",
                        "source_bundle_id": "source_1",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                        "confidence": "moderate",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_c_group_lines(
        proposals_path=proposals,
        catalog_path=catalog,
        targets_path=targets,
        group_size=1,
    )

    assert [line["custom_id"] for line in lines] == ["stageCgroup__X01__group00", "stageCgroup__X01__group01"]
    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["candidate_group"]["group_index"] == 0
    assert payload["candidate_group"]["group_count"] == 2
    assert len(payload["frontier_pgs_records"]) == 1
    assert "tournament group" in payload["instruction"]
    assert "10-12" in payload["instruction"]
    assert lines[0]["body"]["max_output_tokens"] >= 1600


def test_coverage_lane_samples_large_bundle_positions() -> None:
    candidate_ids = [f"PGS{i:06d}" for i in range(1, 132)]
    pgs_lookup = {pgs_id: {"pgs_id": pgs_id} for pgs_id in candidate_ids}

    lane = _coverage_lane_pgs_rows(
        candidate_pgs_ids=candidate_ids,
        pgs_lookup=pgs_lookup,
        evaluable_pgs_ids=set(candidate_ids),
    )
    lane_ids = [row["pgs_id"] for row in lane[:24]]

    assert "PGS000017" in lane_ids
    assert "PGS000042" in lane_ids
    assert "PGS000119" in lane_ids


def test_stage_d_evidence_lines_keep_llm_authority_and_raw_tool_evidence(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta.json"
    open_targets = tmp_path / "open_targets.json"
    pairwise_reviews = tmp_path / "pairwise_reviews.json"

    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Trait 1",
                "mapped_trait_labels": ["Trait 1"],
                "performance": {"performance_record_count": 1},
                "stage_b_support": {"primary_votes": 1, "frontier_votes": 1},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Trait 2",
                "mapped_trait_labels": ["Trait 2"],
                "performance": {"performance_record_count": 4},
                "stage_b_support": {"primary_votes": 0, "frontier_votes": 1},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    open_targets.write_text(
        json.dumps({"X01": {"PGS000002": {"shared_gene_count": 3, "shared_genes": ["GENE1", "GENE2"]}}}),
        encoding="utf-8",
    )
    pairwise_reviews.write_text(
        json.dumps(
            {
                "schema_version": "cross_optimized.pairwise_review_evidence.v1",
                "evidence": {
                    "X01": {
                        "PGS000002": {
                            "policy": "Auxiliary LLM head-to-head arguments only; not authority.",
                            "head_to_head_reviews": [
                                {
                                    "opponent_pgs_id": "PGS000001",
                                    "outcome": "preferred",
                                    "confidence": "moderate",
                                    "rationale": "PGS000002 has stronger visible evidence.",
                                    "evidence_cited": ["performance.best_auc"],
                                }
                            ],
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        open_targets_evidence_path=open_targets,
        pairwise_review_evidence_path=pairwise_reviews,
        top_n=2,
    )

    assert len(lines) == 1
    assert lines[0]["custom_id"] == "stageD__X01"
    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["schema_version"] == "cross_optimized.stage_d_evidence.v1"
    assert payload["decision_authority"] == "llm_final"
    assert "LLM Harness > Skill > Tools" in payload["instruction"]
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    cards = {card["pgs_id"]: card for card in payload["candidate_evidence_cards"]}
    assert cards["PGS000002"]["llm_frontier_evidence"] == {
        "frontier_count": 1,
        "primary_count": 1,
        "included_by": ["llm_lane_01"],
        "primary_by": ["llm_lane_01"],
    }
    assert cards["PGS000002"]["open_targets_overlap"] == {
        "shared_gene_count": 3,
        "shared_genes": ["GENE1", "GENE2"],
    }
    assert cards["PGS000002"]["pairwise_review_evidence"]["head_to_head_reviews"][0]["outcome"] == "preferred"
    assert payload["harness_evidence_policy"]["pairwise_reviews"].startswith("Auxiliary LLM")


def test_stage_d_evidence_lines_can_omit_llm_provenance_from_candidate_cards(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta.json"
    advisor_predictions = tmp_path / "predictions_advisor.json"
    open_targets = tmp_path / "open_targets.json"

    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Trait 1",
                "mapped_trait_labels": ["Trait 1"],
                "performance": {"performance_record_count": 1},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Trait 2",
                "mapped_trait_labels": ["Trait 2"],
                "performance": {"performance_record_count": 4},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    open_targets.write_text(
        json.dumps({"X01": {"PGS000002": {"shared_gene_count": 3}}}),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions],
        open_targets_evidence_path=open_targets,
        prompt_mode="evidence_only_early_tail_panel_review",
        top_n=2,
        omit_llm_provenance=True,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    cards = {card["pgs_id"]: card for card in payload["candidate_evidence_cards"]}
    assert cards["PGS000002"]["reported_trait"] == "Trait 2"
    assert cards["PGS000002"]["open_targets_overlap"] == {"shared_gene_count": 3}
    for card in cards.values():
        assert "llm_frontier_evidence" not in card
        assert "non_decision_advisory_evidence" not in card
    assert payload["harness_policy"]["llm_provenance"] == "omitted_from_candidate_cards"
    payload_text = json.dumps(payload).lower()
    for fragment in [
        "llm_frontier_evidence",
        "non_decision_advisory_evidence",
        "hit@top",
        "evaluation matrix",
        "held-out",
        "oracle",
        "target rank",
    ]:
        assert fragment not in payload_text


def test_stage_d_anchor_precision_mode_names_anchor_lane_without_hard_winner(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "Trait 1"},
            {"pgs_id": "PGS000002", "reported_trait": "Trait 2"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="anchor_precision",
        anchor_lane="predictions_stage_c_meta_two_lane",
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["harness_policy"] == {
        "prompt_mode": "anchor_review",
        "anchor_lane": "llm_lane_01",
        "candidate_order": "input",
    }
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    assert "anchor review reconciler" in payload["instruction"]
    assert "preserve the anchor lane" in payload["instruction"]


def test_stage_d_anchor_evidence_burden_requires_llm_switch_justification(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_d_current_best.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.current_plus_expanded_frontier.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Anchor source",
                "performance": {"performance_record_count": 10, "best_auc": 0.8},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Closer but sparse source",
                "performance": {"performance_record_count": 1},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCexpanded__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="anchor_evidence_burden_review",
        anchor_lane="predictions_stage_d_current_best",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "anchor_evidence_burden_review"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    assert "anchor evidence-burden reconciler" in payload["instruction"]
    assert "not an automatic winner" in payload["instruction"]
    assert "two independent LLM-readable reasons" in payload["instruction"]
    assert "do not switch merely because the challenger has a closer-looking label" in payload["instruction"]


def test_stage_d_anchor_switch_audit_reviews_proposed_switch_without_rule(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_switch_candidates.jsonl"
    anchor_predictions = tmp_path / "predictions_stage_d_anchor.json"
    switch_predictions = tmp_path / "predictions_stage_d_proposed_switch.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.switch_audit_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "Anchor source"},
            {"pgs_id": "PGS000002", "reported_trait": "Proposed switch source"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCswitchAudit__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    anchor_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                        "rationale": "Anchor rationale",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    switch_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                        "rationale": "Proposed switch rationale",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[anchor_predictions, switch_predictions],
        prompt_mode="anchor_switch_audit_review",
        anchor_lane="predictions_stage_d_anchor",
        top_n=2,
        include_vote_rationales=True,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "anchor_switch_audit_review"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    assert "anchor switch-audit reconciler" in payload["instruction"]
    assert "proposed switch is a claim to audit, not evidence of correctness" in payload["instruction"]
    assert "do not use a revert rule" in payload["instruction"]
    assert "switch case" in payload["instruction"]


def test_stage_d_source_axis_precision_mode_uses_early_precision_language(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "Trait 1"},
            {"pgs_id": "PGS000002", "reported_trait": "Trait 2"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="source_axis_precision",
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["harness_policy"]["prompt_mode"] == "source_axis_review"
    assert "source-axis review reconciler" in payload["instruction"]
    assert "Do not select a broad proxy" in payload["instruction"]


def test_stage_d_challenger_audit_mode_pushes_llm_review_without_hard_winner(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Anchor trait",
                "performance": {"performance_record_count": 1},
                "stage_b_support": {"primary_votes": 1, "frontier_votes": 1},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Challenger trait",
                "performance": {"performance_record_count": 4},
                "stage_b_support": {"primary_votes": 0, "frontier_votes": 2},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="challenger_audit",
        anchor_lane="predictions_stage_c_meta_two_lane",
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "challenger_audit"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    assert "challenger audit" in payload["instruction"]
    assert "do not convert counts into a formula" in payload["instruction"]


def test_stage_d_source_axis_consensus_guard_protects_llm_consensus_without_formula(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "Anchor trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Challenger trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="source_axis_consensus_guard",
        anchor_lane="predictions_stage_c_meta_two_lane",
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "source_axis_consensus_guard"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    assert "source-axis consensus guard" in payload["instruction"]
    assert "not a threshold or formula" in payload["instruction"]


def test_stage_d_metadata_challenger_review_uses_advisor_as_non_decision_evidence(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    advisor_predictions = tmp_path / "predictions_metadata_advisor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Anchor trait",
                "performance": {"performance_record_count": 1},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Advisor trait",
                "performance": {"performance_record_count": 4},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
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

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions],
        prompt_mode="metadata_challenger_review",
        anchor_lane="predictions_stage_c_meta_two_lane",
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "metadata_challenger_review"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    cards = {card["pgs_id"]: card for card in payload["candidate_evidence_cards"]}
    assert cards["PGS000002"]["non_decision_advisory_evidence"] == {
        "frontier_count": 1,
        "primary_count": 1,
        "included_by": ["advisor_lane_01"],
        "primary_by": ["advisor_lane_01"],
    }
    assert "metadata challenger review" in payload["instruction"]
    assert "non-LLM metadata advisor is not a judge" in payload["instruction"]


def test_stage_d_rationale_grounded_review_adds_compact_llm_primary_rationales(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Anchor trait",
                "performance": {"performance_record_count": 1},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Challenger trait",
                "performance": {"performance_record_count": 4},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "source_bundle_id": "source_a",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                        "rationale": "Anchor has the most coherent source bridge. " * 20,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="rationale_grounded_review",
        include_vote_rationales=True,
        vote_rationale_char_limit=80,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "rationale_grounded_review"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    cards = {card["pgs_id"]: card for card in payload["candidate_evidence_cards"]}
    rationales = cards["PGS000001"]["llm_frontier_evidence"]["primary_rationales"]
    assert rationales == [
        {
            "lane": "llm_lane_01",
            "source_bundle_id": "source_a",
            "rationale": "Anchor has the most coherent source bridge. Anchor has the most coherent source...",
        }
    ]
    assert "primary_rationales" not in cards["PGS000002"]["llm_frontier_evidence"]
    assert "rationale-grounded LLM harness reconciler" in payload["instruction"]
    assert "Do not treat rationale count" in payload["instruction"]


def test_stage_d_accepts_medium_reasoning_effort(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [{"pgs_id": "PGS000001", "reported_trait": "Trait 1"}],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        reasoning_effort="medium",
        max_output_tokens=2200,
    )

    assert lines[0]["body"]["reasoning"] == {"effort": "medium"}
    assert lines[0]["body"]["max_output_tokens"] == 2200


def test_stage_d_robust_evidence_review_uses_pgs_strength_without_formula(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Trait 1",
                "performance": {"performance_record_count": 1},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Trait 2",
                "performance": {"performance_record_count": 6},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="robust_evidence_review",
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "robust_evidence_review"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    assert "robust evidence review" in payload["instruction"]
    assert "Do not convert validation breadth" in payload["instruction"]


def test_stage_d_signal_literate_review_compares_coherent_prs_signal_without_formula() -> None:
    instruction = _stage_d_instruction("signal_literate_review", "").lower()

    assert "signal-literate reconciler" in instruction
    assert "closer-looking source label" in instruction
    assert "materially stronger prs evidence" in instruction
    assert "numeric formula" in instruction


def test_stage_d_early_tail_robust_review_prioritizes_extreme_hit_without_formula(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Broad proxy trait",
                "performance": {"performance_record_count": 8},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Specific adjacent trait",
                "performance": {"performance_record_count": 3},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="early_tail_robust_review",
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "robust_source_evidence_review"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    assert "robust source-evidence review" in payload["instruction"]
    assert "effective target-transfer primary" in payload["instruction"]


def test_stage_d_tiered_tail_precision_review_uses_qualitative_tiers_without_formula(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Direct specific trait",
                "performance": {"performance_record_count": 1},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Broad proxy trait",
                "performance": {"performance_record_count": 8},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="tiered_tail_precision_review",
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "tiered_source_evidence_review"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    assert "tiered source-evidence reconciler" in payload["instruction"]
    assert "not disease-category rules or formulas" in payload["instruction"]
    assert "Use LLM frontier agreement" in payload["instruction"]


def test_stage_d_order_debiased_review_can_reverse_candidate_presentation(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "First trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Middle trait"},
            {"pgs_id": "PGS000003", "reported_trait": "Later trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002", "PGS000003"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="order_debiased_review",
        candidate_order="reverse_input",
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "order_debiased_review"
    assert payload["harness_policy"]["candidate_order"] == "reverse_input"
    assert [card["pgs_id"] for card in payload["candidate_evidence_cards"]] == [
        "PGS000003",
        "PGS000002",
        "PGS000001",
    ]
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    assert "Candidate card order is a harness presentation detail" in payload["instruction"]
    assert "do not switch to a later card because of position alone" in payload["instruction"]


def test_stage_d_advisor_duel_review_treats_advisor_as_trigger_not_authority(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_duel_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    advisor_predictions = tmp_path / "predictions_metadata_advisor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "LLM anchor trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Advisor challenger trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCduel__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
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

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions],
        prompt_mode="advisor_duel_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "advisor_duel_review"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    cards = {card["pgs_id"]: card for card in payload["candidate_evidence_cards"]}
    assert cards["PGS000002"]["non_decision_advisory_evidence"] == {
        "frontier_count": 1,
        "primary_count": 1,
        "included_by": ["advisor_lane_01"],
        "primary_by": ["advisor_lane_01"],
    }
    assert "two-candidate advisor-duel reconciler" in payload["instruction"]
    assert "not a rule, rank, vote, or authority" in payload["instruction"]
    assert "anchor-vs-challenger" in payload["instruction"]


def test_stage_d_advisor_duel_precision_switch_compares_symmetrically(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_duel_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    advisor_predictions = tmp_path / "predictions_metadata_advisor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "LLM anchor trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Advisor challenger trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCduel__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
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

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions],
        prompt_mode="advisor_duel_precision_switch",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "advisor_duel_symmetric_review"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    assert "symmetric two-candidate review duel" in payload["instruction"]
    assert "neither candidate is the default winner" in payload["instruction"]
    assert "not as authority" in payload["instruction"]


def test_stage_d_advisor_challenge_first_review_steelmans_but_does_not_defer(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_duel_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    advisor_predictions = tmp_path / "predictions_metadata_advisor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.duel_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "LLM anchor trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Advisor challenger trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCduel__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
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

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions],
        prompt_mode="advisor_challenge_first_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "advisor_challenge_first_review"
    payload_text = json.dumps(payload).lower()
    assert "advisor_score" not in payload_text
    assert "selected_score" not in payload_text
    assert "advisor challenge-first reconciler" in payload["instruction"]
    assert "steelman the advisor-surfaced candidate first" in payload["instruction"]
    assert "not advisor deference" in payload["instruction"]


def test_stage_d_advisor_panel_review_keeps_multiple_advisors_non_decision(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_panel_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    advisor_predictions_a = tmp_path / "predictions_metadata_advisor_a.json"
    advisor_predictions_b = tmp_path / "predictions_metadata_advisor_b.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.panel_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "LLM anchor trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Advisor challenger A trait"},
            {"pgs_id": "PGS000003", "reported_trait": "Advisor challenger B trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCpanel__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002", "PGS000003"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions_a.write_text(
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
    advisor_predictions_b.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000003",
                        "frontier_pgs_ids": ["PGS000003"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions_a, advisor_predictions_b],
        prompt_mode="advisor_panel_review",
        top_n=3,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "advisor_panel_review"
    assert len(payload["candidate_evidence_cards"]) == 3
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "advisor_score" not in payload_text
    assert "selected_score" not in payload_text
    cards = {card["pgs_id"]: card for card in payload["candidate_evidence_cards"]}
    assert cards["PGS000002"]["non_decision_advisory_evidence"]["primary_by"] == [
        "advisor_lane_01"
    ]
    assert cards["PGS000003"]["non_decision_advisory_evidence"]["primary_by"] == [
        "advisor_lane_02"
    ]
    assert "advisor-panel reconciler" in payload["instruction"]
    assert "not a ranking, vote, score, threshold, or authority" in payload["instruction"]
    assert "LLM anchor and all surfaced advisors" in payload["instruction"]


def test_stage_d_advisor_source_aware_panel_keeps_corrob_triggers_non_decision(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_panel_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    advisor_predictions_a = tmp_path / "predictions_metadata_advisor_a.json"
    advisor_predictions_b = tmp_path / "predictions_metadata_advisor_b.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.panel_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "LLM anchor trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Shared advisor challenger trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCpanel__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    for path in (advisor_predictions_a, advisor_predictions_b):
        path.write_text(
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

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions_a, advisor_predictions_b],
        prompt_mode="advisor_source_aware_panel_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "advisor_source_aware_panel_review"
    payload_text = json.dumps(payload).lower()
    assert "advisor_score" not in payload_text
    assert "selected_score" not in payload_text
    cards = {card["pgs_id"]: card for card in payload["candidate_evidence_cards"]}
    assert cards["PGS000002"]["non_decision_advisory_evidence"]["primary_count"] == 2
    assert "advisor-source-aware panel reconciler" in payload["instruction"]
    assert "corroboration triggers, not votes" in payload["instruction"]
    assert "never select from advisor agreement alone" in payload["instruction"]


def test_stage_d_harness_convergence_guard_treats_convergence_as_llm_evidence(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_harness_convergence_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    advisor_predictions_a = tmp_path / "predictions_stage_d_advisor_a.json"
    advisor_predictions_b = tmp_path / "predictions_stage_d_advisor_b.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.evidence_only_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "LLM converged source"},
            {"pgs_id": "PGS000002", "reported_trait": "Challenger source"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCevidenceOnly__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    for path in (advisor_predictions_a, advisor_predictions_b):
        path.write_text(
            json.dumps(
                {
                    "predictions": [
                        {
                            "target_id": "X01",
                            "primary_pgs_id": "PGS000001",
                            "frontier_pgs_ids": ["PGS000001"],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions_a, advisor_predictions_b],
        prompt_mode="harness_convergence_guard_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["harness_policy"]["prompt_mode"] == "harness_convergence_guard_review"
    cards = {card["pgs_id"]: card for card in payload["candidate_evidence_cards"]}
    assert cards["PGS000001"]["non_decision_advisory_evidence"]["primary_count"] == 2
    assert "harness-convergence guard reconciler" in payload["instruction"]
    assert "high-priority harness evidence" in payload["instruction"]
    assert "not a mechanical agreement rule" in payload["instruction"]


def test_stage_d_same_source_model_audit_compares_model_level_evidence(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "anchor.json"
    advisor_predictions = tmp_path / "advisor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.anchor_advisor_candidate_panel.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Shared source",
                "mapped_trait_ids": ["MONDO_000001"],
                "performance": {"performance_record_count": 2, "best_auc": 0.7},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Shared source",
                "mapped_trait_ids": ["MONDO_000001"],
                "performance": {"performance_record_count": 8},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCAnchorAdvisorPanel__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions],
        prompt_mode="same_source_model_audit_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["harness_policy"]["prompt_mode"] == "same_source_model_audit_review"
    assert "same-source model audit reconciler" in payload["instruction"]
    assert "source fit no longer decides the model choice" in payload["instruction"]
    assert "not universal across endpoints" in payload["instruction"]
    assert "review trigger only" in payload["instruction"]


def test_stage_d_source_equivalent_model_challenger_reduces_lane_inertia(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "anchor.json"
    advisor_predictions = tmp_path / "advisor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.anchor_advisor_candidate_panel.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Shared source",
                "mapped_trait_ids": ["MONDO_000001"],
                "method": "snpnet",
                "performance": {"performance_record_count": 5, "best_auc": 0.83},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Shared source",
                "mapped_trait_ids": ["MONDO_000001"],
                "method": "LDpred2.CV",
                "variant_count": 1000000,
                "performance": {"performance_record_count": 6, "best_or": 1.8},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCAnchorAdvisorPanel__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions],
        prompt_mode="source_equivalent_model_challenger_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["harness_policy"]["prompt_mode"] == "source_equivalent_model_challenger_review"
    instruction = payload["instruction"].lower()
    assert "source-equivalent model challenger reconciler" in instruction
    assert "lane convergence is weaker evidence" in instruction
    assert "not a universal transfer ordering" in instruction
    assert "do not select the advisor-surfaced model by rule" in instruction


def test_stage_d_same_source_metric_calibrated_review_is_llm_led(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "anchor.json"
    advisor_predictions = tmp_path / "advisor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.anchor_advisor_candidate_panel.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Shared source",
                "mapped_trait_ids": ["MONDO_000001"],
                "method": "snpnet",
                "performance": {"performance_record_count": 5, "best_auc": 0.9, "best_r2": 0.8},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Shared source",
                "mapped_trait_ids": ["MONDO_000001"],
                "method": "LDpred2.CV",
                "performance": {"performance_record_count": 6, "best_or": 1.8},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCAnchorAdvisorPanel__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions],
        prompt_mode="same_source_metric_calibrated_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["harness_policy"]["prompt_mode"] == "same_source_metric_calibrated_review"
    instruction = payload["instruction"].lower()
    assert "same-source metric-calibrated reconciler" in instruction
    assert "headline metrics are not automatically comparable" in instruction
    assert "provenance is review context only" in instruction
    assert "do not select by formula" in instruction


def test_stage_d_binary_effect_calibrated_review_is_llm_led(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "anchor.json"
    advisor_predictions = tmp_path / "advisor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.anchor_advisor_candidate_panel.v1",
        "target": {"target_id": "X01", "target_label": "Target diagnosis"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Shared diagnosis",
                "mapped_trait_ids": ["MONDO_000001"],
                "performance": {"best_auc": 0.9, "best_r2": 0.8},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Shared diagnosis",
                "mapped_trait_ids": ["MONDO_000001"],
                "performance": {"best_or": 1.9, "best_abs_beta": 0.4},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCAnchorAdvisorPanel__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions],
        prompt_mode="binary_effect_calibrated_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["harness_policy"]["prompt_mode"] == "binary_effect_calibrated_review"
    instruction = payload["instruction"].lower()
    assert "binary/time-to-event effect-calibrated reconciler" in instruction
    assert "odds ratios, hazard ratios, or beta estimates" in instruction
    assert "not a formula" in instruction
    assert "no disease-specific rule" in instruction


def test_stage_d_evidence_only_early_tail_panel_ignores_provenance_as_priority(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_evidence_only_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    advisor_predictions = tmp_path / "predictions_metadata_advisor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.evidence_only_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "Lane candidate trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Advisor candidate trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCevidenceOnly__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
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

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions],
        prompt_mode="evidence_only_early_tail_panel_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "evidence_only_panel_review"
    payload_text = json.dumps(payload).lower()
    assert "advisor_score" not in payload_text
    assert "selected_score" not in payload_text
    assert "evidence-only panel reconciler" in payload["instruction"]
    assert "Candidate provenance is not priority evidence" in payload["instruction"]
    assert "do not preserve an incumbent" in payload["instruction"]


def test_stage_d_extreme_tail_evidence_panel_prioritizes_tail_without_formula(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_extreme_tail_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    advisor_predictions = tmp_path / "predictions_metadata_advisor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.extreme_tail_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "Coherent bridge trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Strong PGS evidence trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCextremeTail__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
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

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        advisor_prediction_paths=[advisor_predictions],
        prompt_mode="extreme_tail_evidence_panel_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "evidence_panel_review"
    payload_text = json.dumps(payload).lower()
    assert "advisor_score" not in payload_text
    assert "selected_score" not in payload_text
    assert "evidence panel reconciler" in payload["instruction"]
    assert "source fit is a coherence gate, not an automatic winner" in payload["instruction"]
    assert "do not use a numeric formula" in payload["instruction"]


def test_stage_d_expanded_evidence_shortlist_keeps_source_triage_llm_led(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_expanded_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.expanded_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "Close source trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Strong coherent proxy trait"},
            {"pgs_id": "PGS000003", "reported_trait": "Broad weak proxy trait"},
            {"pgs_id": "PGS000004", "reported_trait": "Method-rich weak source trait"},
            {"pgs_id": "PGS000005", "reported_trait": "Alternative coherent source trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCexpanded__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": [
                            "PGS000001",
                            "PGS000002",
                            "PGS000003",
                            "PGS000004",
                            "PGS000005",
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="expanded_evidence_shortlist_review",
        top_n=5,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "expanded_evidence_shortlist_review"
    assert len(payload["candidate_evidence_cards"]) == 5
    payload_text = json.dumps(payload).lower()
    assert "advisor_score" not in payload_text
    assert "selected_score" not in payload_text
    assert "expanded evidence shortlist reconciler" in payload["instruction"]
    assert "source-axis triage" in payload["instruction"]
    assert "do not use candidate position" in payload["instruction"]


def test_stage_d_llm_lane_panel_review_reconciles_lanes_without_majority_vote(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_llm_lane_panel_candidates.jsonl"
    lane_a = tmp_path / "predictions_stage_d_lane_a.json"
    lane_b = tmp_path / "predictions_stage_d_lane_b.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.llm_lane_panel_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "First LLM lane trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Second LLM lane trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageClanePanel__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    lane_a.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    lane_b.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[lane_a, lane_b],
        prompt_mode="llm_lane_panel_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "llm_lane_panel_review"
    payload_text = json.dumps(payload).lower()
    assert "advisor_score" not in payload_text
    assert "selected_score" not in payload_text
    cards = {card["pgs_id"]: card for card in payload["candidate_evidence_cards"]}
    assert cards["PGS000001"]["llm_frontier_evidence"]["primary_by"] == [
        "llm_lane_01"
    ]
    assert cards["PGS000002"]["llm_frontier_evidence"]["primary_by"] == [
        "llm_lane_02"
    ]
    assert "LLM-lane panel reconciler" in payload["instruction"]
    assert "not a majority vote, threshold, rank, or formula" in payload["instruction"]
    assert "strongest lane-level qualitative case" in payload["instruction"]


def test_stage_d_llm_early_tail_tiebreak_review_is_llm_led_for_lane_disagreements(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_llm_tiebreak_candidates.jsonl"
    lane_a = tmp_path / "predictions_stage_d_lane_a.json"
    lane_b = tmp_path / "predictions_stage_d_lane_b.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.llm_tiebreak_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "Panel lane trait"},
            {"pgs_id": "PGS000002", "reported_trait": "Source-aware lane trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCtiebreak__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    lane_a.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    lane_b.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[lane_a, lane_b],
        prompt_mode="llm_early_tail_tiebreak_review",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "llm_lane_tiebreak_review"
    payload_text = json.dumps(payload).lower()
    assert "advisor_score" not in payload_text
    assert "selected_score" not in payload_text
    assert "LLM lane tie-break reconciler" in payload["instruction"]
    assert "not a lane vote, average, threshold, or merge rule" in payload["instruction"]
    assert "strongest target-transfer case" in payload["instruction"]


def test_stage_d_order_perturbation_tiebreak_ignores_lane_order_as_authority(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_order_candidates.jsonl"
    original_predictions = tmp_path / "predictions_original_order.json"
    reverse_predictions = tmp_path / "predictions_reverse_order.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.order_tiebreak_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "Original-order source"},
            {"pgs_id": "PGS000002", "reported_trait": "Reverse-order source"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCorder__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    original_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                        "rationale": "original lane rationale",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    reverse_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                        "rationale": "reverse lane rationale",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[original_predictions, reverse_predictions],
        prompt_mode="order_perturbation_tiebreak_review",
        candidate_order="pgs_id",
        include_vote_rationales=True,
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "order_perturbation_tiebreak_review"
    assert payload["harness_policy"]["candidate_order"] == "pgs_id"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    assert "order-perturbation tiebreak" in payload["instruction"]
    assert "presentation-sensitive disagreement" in payload["instruction"]
    assert "do not prefer the original-order lane or the reverse-order lane" in payload["instruction"]
    assert "input order" in payload["instruction"]


def test_stage_d_source_axis_blinded_review_can_omit_performance_fields(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_source_blinded_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_anchor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.source_blinded_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {
                "pgs_id": "PGS000001",
                "reported_trait": "Coherent source",
                "method": "PRS-CS",
                "performance": {"performance_record_count": 5, "best_auc": 0.9},
            },
            {
                "pgs_id": "PGS000002",
                "reported_trait": "Distant source",
                "method": "LDpred2",
                "performance": {"performance_record_count": 9, "best_auc": 0.95},
            },
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCsourceBlinded__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        prompt_mode="source_axis_blinded_review",
        performance_mode="source_only",
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["harness_policy"]["prompt_mode"] == "source_axis_blinded_review"
    assert "performance" not in payload["candidate_evidence_cards"][0]
    assert "performance" not in payload["candidate_evidence_cards"][1]
    instruction = payload["instruction"].lower()
    assert "source-axis blinded reconciler" in instruction
    assert "intentionally omitted" in instruction
    assert "do not infer weak model evidence from that omission" in instruction
    assert "benchmark" not in instruction
    assert "hit@top" not in instruction


def test_stage_d_advisor_contradiction_falsification_keeps_advisor_non_decision(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_advisor_contradiction_candidates.jsonl"
    llm_predictions = tmp_path / "predictions_llm_current.json"
    advisor_predictions = tmp_path / "predictions_metadata_primary_only_advisor.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.advisor_contradiction_candidates.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000001", "reported_trait": "LLM primary source"},
            {"pgs_id": "PGS000002", "reported_trait": "Advisor surfaced source"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageCadvisor__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    llm_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                        "rationale": "LLM current rationale",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    advisor_predictions.write_text(
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

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[llm_predictions],
        advisor_prediction_paths=[advisor_predictions],
        prompt_mode="advisor_contradiction_falsification_review",
        candidate_order="pgs_id",
        include_vote_rationales=True,
        top_n=2,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "advisor_contradiction_falsification_review"
    payload_text = json.dumps(payload).lower()
    assert "recommended" not in payload_text
    assert "score" not in payload_text
    cards = {card["pgs_id"]: card for card in payload["candidate_evidence_cards"]}
    assert cards["PGS000002"]["non_decision_advisory_evidence"]["primary_by"] == [
        "advisor_lane_01"
    ]
    assert "advisor contradiction falsification" in payload["instruction"]
    assert "non-decision advisor" in payload["instruction"]
    assert "not authority" in payload["instruction"]
    assert "falsify both cases" in payload["instruction"]


def test_stage_d_candidate_order_can_sort_by_pgs_id_without_changing_evidence(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    vote_predictions = tmp_path / "predictions_stage_c_meta_two_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000003", "reported_trait": "Trait 3"},
            {"pgs_id": "PGS000001", "reported_trait": "Trait 1"},
            {"pgs_id": "PGS000002", "reported_trait": "Trait 2"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000003",
                        "frontier_pgs_ids": ["PGS000003", "PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_evidence_lines(
        candidate_request_path=candidate_requests,
        vote_prediction_paths=[vote_predictions],
        candidate_order="pgs_id",
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert [card["pgs_id"] for card in payload["candidate_evidence_cards"]] == [
        "PGS000001",
        "PGS000002",
        "PGS000003",
    ]
    assert payload["harness_policy"]["candidate_order"] == "pgs_id"


def test_stage_d_audit_includes_draft_as_non_authoritative_context(tmp_path) -> None:
    candidate_requests = tmp_path / "stage_c_candidates.jsonl"
    draft_predictions = tmp_path / "predictions_stage_d_draft.json"
    comparison_draft_predictions = tmp_path / "predictions_stage_d_comparison_draft.json"
    vote_predictions = tmp_path / "predictions_stage_c_lane.json"
    candidate_payload = {
        "schema_version": "cross_optimized.stage_c.v1",
        "target": {"target_id": "X01", "target_label": "Target disease"},
        "frontier_pgs_records": [
            {"pgs_id": "PGS000002", "reported_trait": "Draft trait"},
            {"pgs_id": "PGS000001", "reported_trait": "Alternative trait"},
        ],
    }
    candidate_requests.write_text(
        json.dumps(
            {
                "custom_id": "stageC__X01",
                "body": {
                    "input": [
                        {"role": "system", "content": "existing stage c"},
                        {"role": "user", "content": json.dumps(candidate_payload)},
                    ]
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    draft_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000002",
                        "source_bundle_id": "source_draft",
                        "frontier_pgs_ids": ["PGS000002", "PGS000001"],
                        "issues": ["Draft uncertainty"],
                        "rationale": "Draft rationale",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    comparison_draft_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "source_bundle_id": "source_comparison",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                        "issues": ["Comparison uncertainty"],
                        "rationale": "Comparison rationale",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    vote_predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "X01",
                        "primary_pgs_id": "PGS000001",
                        "frontier_pgs_ids": ["PGS000001", "PGS000002"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    lines = build_stage_d_audit_lines(
        candidate_request_path=candidate_requests,
        draft_prediction_path=draft_predictions,
        comparison_draft_prediction_path=comparison_draft_predictions,
        vote_prediction_paths=[vote_predictions],
        candidate_order="pgs_id",
        audit_mode="dual_draft_adjudication",
        max_output_tokens=1800,
    )

    payload = json.loads(lines[0]["body"]["input"][1]["content"])
    assert payload["decision_authority"] == "llm_final"
    assert payload["harness_policy"]["prompt_mode"] == "dual_draft_adjudication"
    assert payload["draft_decision"]["primary_pgs_id"] == "PGS000002"
    assert payload["comparison_draft_decision"]["primary_pgs_id"] == "PGS000001"
    assert [card["pgs_id"] for card in payload["candidate_evidence_cards"]] == [
        "PGS000001",
        "PGS000002",
    ]
    assert lines[0]["body"]["max_output_tokens"] == 1800
    instruction = payload["instruction"]
    assert "not authority" in instruction
    assert "not a vote" in instruction
    assert "numeric formula" in instruction
    assert "Neither draft is authority" in instruction
    assert "benchmark" not in json.dumps(payload).lower()
    assert "oracle" not in json.dumps(payload).lower()


def test_stage_d_audit_instruction_modes_do_not_name_benchmark_objectives() -> None:
    forbidden_fragments = [
        "hit@top",
        "top 0.5",
        "top 1",
        "top-25",
        "top 25",
        "early-tail",
        "early_tail",
        "early-hit",
        "extreme-tail",
        "extreme_tail",
        "predicted-risk tail",
        "evaluation matrix",
        "oracle",
        "benchmark",
    ]
    for mode in ("standard", "conservative_switch", "dual_draft_adjudication"):
        text = _stage_d_audit_instruction(mode).lower()
        for fragment in forbidden_fragments:
            assert fragment not in text
