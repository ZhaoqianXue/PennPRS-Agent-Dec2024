from __future__ import annotations

import json

import pytest

from experiments.contribution3.cross_optimized.batch.freeze_predictions import freeze_predictions


def test_freeze_rejects_prediction_outside_evaluable_universe(tmp_path) -> None:
    predictions = tmp_path / "predictions.json"
    manifest = tmp_path / "manifest.json"
    predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "F60",
                        "primary_pgs_id": "PGS999999999",
                        "source_bundle_id": "source",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="not evaluable"):
        freeze_predictions(predictions, manifest)


def test_freeze_accepts_evaluable_prediction(tmp_path) -> None:
    predictions = tmp_path / "predictions.json"
    manifest = tmp_path / "manifest.json"
    predictions.write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "target_id": "F60",
                        "primary_pgs_id": "PGS002759",
                        "source_bundle_id": "mondo_0002009",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    payload = freeze_predictions(predictions, manifest)

    assert payload["evaluable_guard"] == "passed"
