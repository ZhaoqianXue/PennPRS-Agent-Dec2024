from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _client():
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("The openai package is required to submit Batch API jobs.") from exc
    return OpenAI()


def submit_batch(
    *,
    jsonl_path: Path,
    job_out: Path,
    endpoint: str = "/v1/responses",
    completion_window: str = "24h",
    metadata: dict[str, str] | None = None,
) -> dict[str, Any]:
    client = _client()
    with jsonl_path.open("rb") as handle:
        uploaded = client.files.create(file=handle, purpose="batch")
    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint=endpoint,
        completion_window=completion_window,
        metadata=metadata or {},
    )
    payload = {
        "schema_version": "cross_optimized.batch_job.v1",
        "input_jsonl": str(jsonl_path),
        "input_file_id": uploaded.id,
        "batch_id": batch.id,
        "endpoint": endpoint,
        "completion_window": completion_window,
        "status": getattr(batch, "status", None),
    }
    job_out.parent.mkdir(parents=True, exist_ok=True)
    job_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit a cross-optimized Batch API request JSONL.")
    parser.add_argument("--jsonl", type=Path, required=True)
    parser.add_argument("--job-out", type=Path, required=True)
    parser.add_argument("--endpoint", default="/v1/responses")
    parser.add_argument("--completion-window", default="24h")
    parser.add_argument("--metadata", type=json.loads, default={})
    args = parser.parse_args()

    payload = submit_batch(
        jsonl_path=args.jsonl,
        job_out=args.job_out,
        endpoint=args.endpoint,
        completion_window=args.completion_window,
        metadata=args.metadata,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
