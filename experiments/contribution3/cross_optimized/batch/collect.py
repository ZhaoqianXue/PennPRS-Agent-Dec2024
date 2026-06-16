from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _client():
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("The openai package is required to collect Batch API jobs.") from exc
    return OpenAI()


def _read_text_response(response: Any) -> str:
    text_attr = getattr(response, "text", None)
    if callable(text_attr):
        return text_attr()
    if isinstance(text_attr, str):
        return text_attr
    content = getattr(response, "content", None)
    if isinstance(content, bytes):
        return content.decode("utf-8")
    if isinstance(content, str):
        return content
    return str(response)


def collect_batch(
    *,
    batch_id: str,
    output_path: Path,
    error_path: Path | None = None,
    status_out: Path | None = None,
) -> dict[str, Any]:
    client = _client()
    batch = client.batches.retrieve(batch_id)
    status_payload = {
        "schema_version": "cross_optimized.batch_status.v1",
        "batch_id": batch_id,
        "status": getattr(batch, "status", None),
        "output_file_id": getattr(batch, "output_file_id", None),
        "error_file_id": getattr(batch, "error_file_id", None),
    }
    if status_out:
        status_out.parent.mkdir(parents=True, exist_ok=True)
        status_out.write_text(json.dumps(status_payload, indent=2), encoding="utf-8")
    output_file_id = status_payload["output_file_id"]
    if output_file_id:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(_read_text_response(client.files.content(output_file_id)), encoding="utf-8")
    error_file_id = status_payload["error_file_id"]
    if error_file_id and error_path:
        error_path.parent.mkdir(parents=True, exist_ok=True)
        error_path.write_text(_read_text_response(client.files.content(error_file_id)), encoding="utf-8")
    return status_payload


def _batch_id_from_job(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    batch_id = str(data.get("batch_id") or "").strip()
    if not batch_id:
        raise ValueError(f"No batch_id found in {path}")
    return batch_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect cross-optimized Batch API output.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--batch-id")
    source.add_argument("--job", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--errors", type=Path)
    parser.add_argument("--status-out", type=Path)
    args = parser.parse_args()

    batch_id = args.batch_id or _batch_id_from_job(args.job)
    status = collect_batch(
        batch_id=batch_id,
        output_path=args.output,
        error_path=args.errors,
        status_out=args.status_out,
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
