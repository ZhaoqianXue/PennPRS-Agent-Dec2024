"""
Run LLM batch inference for Cross-Disease Transfer experiments.

Three conditions:
  - rg-only: h2 + rg signals only (no shared genes), basic prompt
  - graph-no-dk: h2 + rg + shared genes, full prompt, no domain knowledge
  - graph-with-dk: h2 + rg + shared genes, full prompt + domain knowledge

Usage:
  python -m experiments.contribution3.transfer.batch.run_batch build [--condition rg-only|graph-no-dk|graph-with-dk|all]
  python -m experiments.contribution3.transfer.batch.run_batch submit --condition <cond>
  python -m experiments.contribution3.transfer.batch.run_batch collect --condition <cond>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

TRANSFER_DIR = Path(__file__).resolve().parents[1]
LOCAL_GRAPHS_DIR = TRANSFER_DIR / "runs" / "local_graphs"
DOCUMENTS_DIR = TRANSFER_DIR / "runs" / "documents"
LLM_RESULTS_DIR = TRANSFER_DIR / "runs" / "llm_results"
DK_PATH = TRANSFER_DIR / "knowledge" / "cross_disease_transfer_domain_knowledge.md"

CONDITIONS = ["rg-only", "graph-no-dk", "graph-with-dk"]
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------
def to_strict_json_schema(model_class: type[BaseModel]) -> dict[str, Any]:
    """Convert Pydantic model to strict JSON schema for OpenAI structured output."""
    schema = model_class.model_json_schema()
    # Make all properties required and add additionalProperties: false
    _make_strict(schema)
    return schema


def _make_strict(schema: dict[str, Any]) -> None:
    """Recursively make a JSON schema strict."""
    if schema.get("type") == "object":
        schema["additionalProperties"] = False
        if "properties" in schema:
            schema["required"] = list(schema["properties"].keys())
            for prop in schema["properties"].values():
                _make_strict(prop)
    if "items" in schema:
        _make_strict(schema["items"])
    if "$defs" in schema:
        for defn in schema["$defs"].values():
            _make_strict(defn)


# ---------------------------------------------------------------------------
# Build rg-only document (strips shared genes section)
# ---------------------------------------------------------------------------
def strip_shared_genes(doc: str) -> str:
    """Remove shared gene lines from a local graph document (for rg-only condition)."""
    lines = doc.split("\n")
    out = []
    skip = False
    for line in lines:
        if line.startswith("- Shared Genes"):
            skip = True
            continue
        if line.startswith("  Top genes:") or line.startswith("  Shared pathways:"):
            continue
        if skip and (line.startswith("##") or line.startswith("#") or line.startswith("- ")):
            skip = False
        if not skip:
            out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Build batch requests
# ---------------------------------------------------------------------------
def build_requests(condition: str) -> list[dict[str, Any]]:
    """Build JSONL batch requests for a given condition."""
    from experiments.contribution3.transfer.prompts.transfer_prompt import (
        TRANSFER_SYSTEM_PROMPT,
        TRANSFER_SYSTEM_PROMPT_RG_ONLY,
        TransferDecision,
    )

    # Load domain knowledge
    dk_text = ""
    if condition == "graph-with-dk" and DK_PATH.exists():
        dk_text = DK_PATH.read_text()

    # Get system prompt
    if condition == "rg-only":
        system_prompt = TRANSFER_SYSTEM_PROMPT_RG_ONLY
    else:
        system_prompt = TRANSFER_SYSTEM_PROMPT

    # Response format (structured output)
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "transfer_decision",
            "strict": True,
            "schema": to_strict_json_schema(TransferDecision),
        },
    }

    requests = []

    # Find all local graph documents
    doc_files = sorted(DOCUMENTS_DIR.glob("local_graph_*.md"))
    for doc_path in doc_files:
        icd = doc_path.stem.replace("local_graph_", "")

        # Load corresponding JSON to check if it has neighbors
        json_path = LOCAL_GRAPHS_DIR / f"local_graph_{icd}.json"
        if not json_path.exists():
            continue
        with open(json_path) as f:
            graph = json.load(f)
        if not graph.get("neighbors"):
            continue  # Skip diseases with no neighbors

        # Load document
        doc_text = doc_path.read_text()

        # For rg-only condition, strip shared genes
        if condition == "rg-only":
            doc_text = strip_shared_genes(doc_text)

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add domain knowledge as a separate system message if applicable
        if dk_text:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "# Cross-Disease Transfer Domain Knowledge\n\n"
                        "The following domain knowledge document provides empirical "
                        "guidance for evaluating cross-disease PRS transfer candidates. "
                        "Incorporate it as additional evidence.\n\n"
                        + dk_text
                    ),
                }
            )

        # Add the local graph as user message
        messages.append(
            {
                "role": "user",
                "content": (
                    "Based on the following local knowledge graph, "
                    "select the best transfer candidate diseases.\n\n"
                    + doc_text
                ),
            }
        )

        request = {
            "custom_id": f"{condition}__{icd}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": MODEL,
                "messages": messages,
                "temperature": 0.3,
                "max_completion_tokens": 4096,
                "response_format": response_format,
            },
        }
        requests.append(request)

    return requests


def cmd_build(args: argparse.Namespace) -> None:
    """Build batch request JSONL files."""
    conditions = CONDITIONS if args.condition == "all" else [args.condition]

    for cond in conditions:
        requests = build_requests(cond)
        if not requests:
            print(f"[{cond}] No requests (no diseases with neighbors). Skipping.")
            continue

        out_dir = LLM_RESULTS_DIR / cond
        out_dir.mkdir(parents=True, exist_ok=True)
        jsonl_path = out_dir / "batch_requests.jsonl"

        with open(jsonl_path, "w") as f:
            for req in requests:
                f.write(json.dumps(req) + "\n")

        print(f"[{cond}] Built {len(requests)} requests -> {jsonl_path}")


# ---------------------------------------------------------------------------
# Submit batch
# ---------------------------------------------------------------------------
def cmd_submit(args: argparse.Namespace) -> None:
    """Submit batch to OpenAI API."""
    from openai import OpenAI

    cond = args.condition
    out_dir = LLM_RESULTS_DIR / cond
    jsonl_path = out_dir / "batch_requests.jsonl"

    if not jsonl_path.exists():
        print(f"[{cond}] No batch_requests.jsonl found. Run 'build' first.")
        return

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Upload file
    with open(jsonl_path, "rb") as f:
        uploaded = client.files.create(file=f, purpose="batch")
    print(f"[{cond}] Uploaded: {uploaded.id}")

    # Create batch
    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"experiment": f"contribution3_transfer_{cond}"},
    )
    print(f"[{cond}] Batch created: {batch.id} (status={batch.status})")

    # Save job info
    job = {
        "batch_id": batch.id,
        "input_file_id": uploaded.id,
        "condition": cond,
        "status": batch.status,
        "model": MODEL,
    }
    job_path = out_dir / "batch_job.json"
    with open(job_path, "w") as f:
        json.dump(job, f, indent=2)
    print(f"[{cond}] Job info saved to {job_path}")


# ---------------------------------------------------------------------------
# Collect results
# ---------------------------------------------------------------------------
def cmd_collect(args: argparse.Namespace) -> None:
    """Collect completed batch results."""
    from openai import OpenAI

    cond = args.condition
    out_dir = LLM_RESULTS_DIR / cond
    job_path = out_dir / "batch_job.json"

    if not job_path.exists():
        print(f"[{cond}] No batch_job.json found. Run 'submit' first.")
        return

    with open(job_path) as f:
        job = json.load(f)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    batch = client.batches.retrieve(job["batch_id"])

    print(f"[{cond}] Batch {batch.id}: status={batch.status}")

    if batch.status != "completed":
        print(f"  Not completed yet. Check back later.")
        # Update status
        job["status"] = batch.status
        with open(job_path, "w") as f:
            json.dump(job, f, indent=2)
        return

    # Download output
    raw_output = client.files.retrieve_content(batch.output_file_id)
    output_path = out_dir / "batch_output.jsonl"
    output_path.write_text(raw_output, encoding="utf-8")

    # Download errors if any
    if batch.error_file_id:
        raw_errors = client.files.retrieve_content(batch.error_file_id)
        error_path = out_dir / "batch_errors.jsonl"
        error_path.write_text(raw_errors, encoding="utf-8")

    # Parse results
    results = {}
    for line in raw_output.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        custom_id = record.get("custom_id", "")
        response = record.get("response", {})
        status_code = response.get("status_code")

        if status_code != 200:
            results[custom_id] = {
                "custom_id": custom_id,
                "error": f"HTTP {status_code}",
                "decision": None,
            }
            continue

        body = response.get("body", {})
        choices = body.get("choices", [])
        if not choices:
            results[custom_id] = {
                "custom_id": custom_id,
                "error": "No choices",
                "decision": None,
            }
            continue

        content = choices[0].get("message", {}).get("content", "")
        try:
            decision = json.loads(content)
        except json.JSONDecodeError:
            decision = {"raw_content": content}

        # Extract ICD from custom_id (format: condition__ICD)
        icd = custom_id.split("__", 1)[-1] if "__" in custom_id else custom_id

        results[custom_id] = {
            "custom_id": custom_id,
            "icd": icd,
            "error": None,
            "decision": decision,
        }

    # Save parsed results
    parsed_path = out_dir / "parsed_results.json"
    with open(parsed_path, "w") as f:
        json.dump(results, f, indent=2)

    n_ok = sum(1 for r in results.values() if r.get("error") is None)
    n_err = sum(1 for r in results.values() if r.get("error") is not None)
    print(f"[{cond}] Collected {n_ok} results, {n_err} errors -> {parsed_path}")

    # Update job status
    job["status"] = "collected"
    with open(job_path, "w") as f:
        json.dump(job, f, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="C3 Transfer LLM Batch Runner")
    sub = parser.add_subparsers(dest="command")

    build_p = sub.add_parser("build", help="Build batch request JSONL files")
    build_p.add_argument(
        "--condition", default="all", choices=CONDITIONS + ["all"]
    )

    submit_p = sub.add_parser("submit", help="Submit batch to OpenAI API")
    submit_p.add_argument("--condition", required=True, choices=CONDITIONS)

    collect_p = sub.add_parser("collect", help="Collect completed batch results")
    collect_p.add_argument("--condition", required=True, choices=CONDITIONS)

    args = parser.parse_args()
    if args.command == "build":
        cmd_build(args)
    elif args.command == "submit":
        cmd_submit(args)
    elif args.command == "collect":
        cmd_collect(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
