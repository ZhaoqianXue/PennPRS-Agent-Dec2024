from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.contribution3.cross_optimized.data_contract import clean_text
from experiments.contribution3.cross_optimized.eval.evaluate_frozen import target_lookup
from experiments.contribution3.cross_optimized.leak_guard import assert_no_leakage
from experiments.contribution3.cross_optimized.retrieve.source_retriever import source_universe_pgs_ids


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_prediction_payload(path: Path) -> Any:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    raise ValueError(f"Unsupported prediction file suffix: {path.suffix}")


def _prediction_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        payload = payload.get("predictions", payload.get("results", []))
    if not isinstance(payload, list):
        raise ValueError("Prediction payload must be a list or contain a predictions/results list.")
    rows = []
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError("Prediction rows must be JSON objects.")
        rows.append(row)
    return rows


def assert_predictions_evaluable(payload: Any) -> None:
    targets = target_lookup()
    for row in _prediction_rows(payload):
        target_id = clean_text(row.get("target_id"))
        pgs_id = clean_text(row.get("primary_pgs_id")) or clean_text(row.get("recommended_model_id")) or clean_text(row.get("best_model_id"))
        if not target_id:
            raise ValueError("Prediction row is missing target_id.")
        if not pgs_id:
            raise ValueError(f"Prediction for {target_id} is missing primary_pgs_id.")
        target = targets.get(target_id)
        if target is None:
            raise ValueError(f"Prediction target {target_id} is not in the target manifest.")
        evaluable_ids = source_universe_pgs_ids(target["target_source"])
        if evaluable_ids and pgs_id not in evaluable_ids:
            raise ValueError(f"Prediction {target_id}/{pgs_id} is not evaluable in matrix header for {target['target_source']}.")


def freeze_predictions(predictions_path: Path, manifest_path: Path) -> dict[str, Any]:
    payload = load_prediction_payload(predictions_path)
    assert_no_leakage(payload, root=str(predictions_path))
    assert_predictions_evaluable(payload)
    manifest = {
        "schema_version": "cross_optimized.freeze_manifest.v1",
        "predictions_path": str(predictions_path),
        "predictions_sha256": sha256_file(predictions_path),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "leak_guard": "passed",
        "evaluable_guard": "passed",
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze leak-free cross-optimized predictions before evaluation.")
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    manifest = freeze_predictions(args.predictions, args.manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
