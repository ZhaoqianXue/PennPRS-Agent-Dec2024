"""Parallel chat.completions evaluator for c2 batch manifests.

Use this for hypothesis search. It consumes an existing prepared manifest
(`request.body` entries in the same format used by OpenAI Batch), executes
those requests with local ThreadPoolExecutor workers, then writes summary JSON
through the same `run_experiment_without_domain` evaluation functions.

Batch API remains the final verification surface; this script is the c2
equivalent of c3's fast local execution loop for cheap iteration.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from experiments.contribution2.recommendation.scripts import run_experiment_without_domain as without_domain


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _run_one(client: OpenAI, request: dict[str, Any]) -> tuple[str, dict[str, Any] | None, str | None]:
    custom_id = request["custom_id"]
    body = request["request"]["body"]
    try:
        response = client.chat.completions.create(**body)
        decisions: list[dict[str, Any]] = []
        for choice in response.choices:
            message = choice.message
            content = without_domain._extract_message_content(getattr(message, "content", None))
            decision = without_domain.Step1Decision.model_validate_json(content)
            decisions.append(decision.model_dump())
        return custom_id, {"custom_id": custom_id, "decisions": decisions, "error": None}, None
    except Exception as exc:  # noqa: BLE001 - batch-style evaluator records per-request failures
        return custom_id, None, f"quick parallel eval failed: {type(exc).__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Parallel quick eval for a prepared c2 manifest")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-run-dir", required=True)
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--result-prefix", default="experiment_agent_harness_lift_fast")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    output_run_dir = Path(args.output_run_dir)
    output_run_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requests = list(manifest.get("requests") or [])
    print(f"Manifest: {manifest_path} ({len(requests)} requests)")
    print(f"Output:   {output_run_dir}")
    print(f"Workers:  {args.workers}")

    without_domain._configure_benchmark_sources(
        union_csv=manifest.get("union_csv"),
        ground_truth_dir=manifest.get("ground_truth_dir"),
    )

    client = _client()
    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    full_results: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(_run_one, client, request): request for request in requests}
        for index, future in enumerate(as_completed(futures), start=1):
            request = futures[future]
            ontology = request.get("ontology")
            custom_id, parsed, error = future.result()
            if parsed is not None:
                parsed_outputs[custom_id] = parsed
            if error:
                error_map[custom_id] = error
            full_results.append({
                "custom_id": custom_id,
                "ontology": ontology,
                "parsed": parsed,
                "error": error,
            })
            if index % 10 == 0 or index == len(requests):
                print(f"[{index}/{len(requests)}] complete")

    trial_results, summary = without_domain._build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )
    summary["execution_mode"] = "quick_eval_parallel_chat_completions"
    summary["quick_eval_parallel"] = {
        "workers": args.workers,
        "manifest": str(manifest_path),
        "errors": len(error_map),
    }

    _write_json(output_run_dir / f"{args.result_prefix}_raw_results.json", full_results)
    _write_json(output_run_dir / f"{args.result_prefix}_trial_results.json", trial_results)
    _write_json(output_run_dir / f"{args.result_prefix}_summary.json", summary)

    print("Hit@k:")
    for k in ["1", "2", "3", "4", "5"]:
        row = (summary.get("trial_hit_at_k") or {}).get(k) or {}
        print(f"  H{k}: {row.get('accuracy')} ({row.get('hits')}/{row.get('eligible')})")
    if error_map:
        print(f"Errors: {len(error_map)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
