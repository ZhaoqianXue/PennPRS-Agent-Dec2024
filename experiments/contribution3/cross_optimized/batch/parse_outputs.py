from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from experiments.contribution3.cross_optimized.data_contract import clean_text


def extract_response_text(body: dict[str, Any]) -> str:
    output_text = body.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()
    chunks: list[str] = []
    for item in body.get("output") or []:
        if item.get("type") == "message":
            for content in item.get("content") or []:
                text = content.get("text")
                if isinstance(text, str):
                    chunks.append(text)
        elif item.get("type") in {"output_text", "text"} and isinstance(item.get("text"), str):
            chunks.append(item["text"])
    return "\n".join(chunk.strip() for chunk in chunks if chunk and chunk.strip()).strip()


def parse_json_response(row: dict[str, Any]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    custom_id = clean_text(row.get("custom_id"))
    if row.get("error"):
        raise ValueError(f"{custom_id}: batch row error: {row['error']}")
    response = row.get("response") or {}
    status_code = response.get("status_code")
    if status_code != 200:
        raise ValueError(f"{custom_id}: response status {status_code}")
    body = response.get("body") or {}
    text = extract_response_text(body)
    if not text:
        raise ValueError(f"{custom_id}: empty response text")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{custom_id}: response was not JSON: {exc}: {text[:300]}") from exc
    return custom_id, payload, body.get("usage") or {}


def parse_stage_a(batch_output: Path, outpath: Path) -> dict[str, list[str]]:
    selections: dict[str, list[str]] = {}
    with batch_output.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            custom_id, payload, _ = parse_json_response(json.loads(line))
            target_id = custom_id.split("__", 1)[-1]
            bundle_ids = (payload.get("selected_bundle_ids") or []) + (payload.get("frontier_bundle_ids") or [])
            seen: set[str] = set()
            selected = []
            for value in bundle_ids:
                bundle_id = clean_text(value)
                if not bundle_id or bundle_id in seen:
                    continue
                seen.add(bundle_id)
                selected.append(bundle_id)
            selections[target_id] = selected
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(selections, indent=2), encoding="utf-8")
    return selections


def parse_stage_b(batch_output: Path, outpath: Path) -> list[dict[str, Any]]:
    predictions: list[dict[str, Any]] = []
    with batch_output.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            custom_id, payload, usage = parse_json_response(json.loads(line))
            parts = custom_id.split("__")
            target_id = parts[1] if len(parts) >= 2 else custom_id.split("__", 1)[-1]
            row = {
                    "target_id": target_id,
                    "primary_pgs_id": clean_text(payload.get("primary_pgs_id")),
                    "source_bundle_id": clean_text(payload.get("source_bundle_id")),
                    "frontier_pgs_ids": [
                        clean_text(v) for v in payload.get("frontier_pgs_ids") or [] if clean_text(v)
                    ],
                    "confidence": clean_text(payload.get("confidence")),
                    "rationale": clean_text(payload.get("rationale")),
                    "evidence_cited": [
                        clean_text(v) for v in payload.get("evidence_cited") or [] if clean_text(v)
                    ],
                    "usage": usage,
                }
            if len(parts) >= 3:
                row["chunk_id"] = parts[2]
            predictions.append(row)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps({"predictions": predictions}, indent=2), encoding="utf-8")
    return predictions


def parse_stage_c(batch_output: Path, outpath: Path) -> list[dict[str, Any]]:
    predictions: list[dict[str, Any]] = []
    with batch_output.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            custom_id, payload, usage = parse_json_response(json.loads(line))
            parts = custom_id.split("__")
            target_id = parts[1] if len(parts) >= 2 else custom_id.split("__", 1)[-1]
            row = {
                "target_id": target_id,
                "accepted": bool(payload.get("accepted")),
                "primary_pgs_id": clean_text(payload.get("primary_pgs_id")),
                "source_bundle_id": clean_text(payload.get("source_bundle_id")),
                "frontier_pgs_ids": [
                    clean_text(v) for v in payload.get("frontier_pgs_ids") or [] if clean_text(v)
                ],
                "issues": [clean_text(v) for v in payload.get("issues") or [] if clean_text(v)],
                "rationale": clean_text(payload.get("rationale")),
                "usage": usage,
            }
            if parts and parts[0] == "stageCgroup" and len(parts) >= 3:
                row["group_id"] = parts[2]
            predictions.append(row)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps({"predictions": predictions}, indent=2), encoding="utf-8")
    return predictions


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse cross-optimized Batch API output JSONL.")
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("stage-a")
    a.add_argument("--batch-output", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    b = sub.add_parser("stage-b")
    b.add_argument("--batch-output", type=Path, required=True)
    b.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("stage-c")
    c.add_argument("--batch-output", type=Path, required=True)
    c.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "stage-a":
        result = parse_stage_a(args.batch_output, args.out)
    elif args.command == "stage-b":
        result = parse_stage_b(args.batch_output, args.out)
    else:
        result = parse_stage_c(args.batch_output, args.out)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
