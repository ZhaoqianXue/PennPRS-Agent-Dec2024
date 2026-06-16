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
import copy
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
from src.server.core.within_prompts.archive.selectors_pre_cleanup_20260615 import (
    GENERAL_LLM_BASELINE_SYSTEM_PROMPT,
)


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _usage_int(usage: dict[str, Any], *keys: str) -> int:
    for key in keys:
        value = usage.get(key)
        if value is not None:
            return without_domain._safe_int(value)
    return 0


def _summarize_usage_cost(model: str, usage_records: list[dict[str, Any]]) -> dict[str, Any] | None:
    pricing_key, pricing = without_domain._pricing_for_model(
        model,
        without_domain.STANDARD_PRICING_PER_MILLION_USD,
    )
    if pricing is None:
        return None

    input_tokens = 0
    cached_tokens = 0
    output_tokens = 0
    total_tokens = 0
    for record in usage_records:
        usage = record.get("usage") or {}
        details = usage.get("prompt_tokens_details") or usage.get("input_tokens_details") or {}
        input_tokens += _usage_int(usage, "prompt_tokens", "input_tokens")
        output_tokens += _usage_int(usage, "completion_tokens", "output_tokens")
        total_tokens += _usage_int(usage, "total_tokens")
        cached_tokens += without_domain._safe_int(details.get("cached_tokens"))

    uncached_input_tokens = max(input_tokens - cached_tokens, 0)
    uncached_input_cost = uncached_input_tokens / 1_000_000 * pricing["input"]
    cached_input_cost = cached_tokens / 1_000_000 * pricing["cached_input"]
    output_cost = output_tokens / 1_000_000 * pricing["output"]
    total_cost = uncached_input_cost + cached_input_cost + output_cost
    return {
        "model_pricing_key": pricing_key or model,
        "token_usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached_tokens,
            "uncached_input_tokens": uncached_input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        },
        "pricing_per_million_tokens_usd": {
            "input": pricing["input"],
            "cached_input": pricing["cached_input"],
            "output": pricing["output"],
        },
        "method": "exact_chat_completion_usage_times_official_standard_tier_prices",
        "estimated_cost_breakdown_usd": {
            "uncached_input": round(uncached_input_cost, 4),
            "cached_input": round(cached_input_cost, 4),
            "output": round(output_cost, 4),
        },
        "estimated_total_cost_usd": round(total_cost, 4),
    }


def _run_one(
    client: OpenAI,
    request: dict[str, Any],
) -> tuple[str, dict[str, Any] | None, str | None, dict[str, Any] | None]:
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
        usage = response.usage.model_dump() if response.usage is not None else None
        return custom_id, {"custom_id": custom_id, "decisions": decisions, "error": None}, None, usage
    except Exception as exc:  # noqa: BLE001 - batch-style evaluator records per-request failures
        return custom_id, None, f"quick parallel eval failed: {type(exc).__name__}: {exc}", None


def _validate_manifest(
    manifest: dict[str, Any],
    *,
    require_general_llm_baseline_prompt: bool,
    require_stable_hash_shuffle: bool,
) -> None:
    requests = list(manifest.get("requests") or [])
    if require_stable_hash_shuffle:
        if manifest.get("candidate_order") != "stable_hash_shuffle":
            raise ValueError(f"manifest candidate_order is {manifest.get('candidate_order')!r}, expected stable_hash_shuffle")
        if any(request.get("candidate_order_source") != "stable_hash_shuffle" for request in requests):
            raise ValueError("at least one request does not use stable_hash_shuffle candidate_order_source")
        if any(request.get("candidate_order_matches_benchmark_order") for request in requests):
            raise ValueError("at least one request matches benchmark order")

    if require_general_llm_baseline_prompt:
        for request in requests:
            messages = request.get("request", {}).get("body", {}).get("messages") or []
            system = messages[0].get("content") if messages and messages[0].get("role") == "system" else None
            if system != GENERAL_LLM_BASELINE_SYSTEM_PROMPT:
                raise ValueError(f"{request.get('custom_id')}: system prompt is not GENERAL_LLM_BASELINE_SYSTEM_PROMPT")
            user_text = messages[1].get("content", "") if len(messages) > 1 else ""
            if "skill_context" in user_text or "domain_knowledge" in user_text:
                raise ValueError(f"{request.get('custom_id')}: general baseline request contains skill/domain context")


def main() -> int:
    parser = argparse.ArgumentParser(description="Parallel quick eval for a prepared c2 manifest")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-run-dir", required=True)
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--result-prefix", default="experiment_agent_harness_lift_fast")
    parser.add_argument("--model-override", default=None)
    parser.add_argument("--require-general-llm-baseline-prompt", action="store_true")
    parser.add_argument("--require-stable-hash-shuffle", action="store_true")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    output_run_dir = Path(args.output_run_dir)
    output_run_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _validate_manifest(
        manifest,
        require_general_llm_baseline_prompt=args.require_general_llm_baseline_prompt,
        require_stable_hash_shuffle=args.require_stable_hash_shuffle,
    )
    manifest = copy.deepcopy(manifest)
    if args.model_override:
        manifest["model"] = args.model_override
        for request in manifest.get("requests") or []:
            request["request"]["body"]["model"] = args.model_override
    requests = list(manifest.get("requests") or [])
    print(f"Manifest: {manifest_path} ({len(requests)} requests)")
    print(f"Output:   {output_run_dir}")
    print(f"Workers:  {args.workers}")
    print(f"Model:    {manifest.get('model')}")

    without_domain._configure_benchmark_sources(
        union_csv=manifest.get("union_csv"),
        ground_truth_dir=manifest.get("ground_truth_dir"),
    )

    client = _client()
    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}
    full_results: list[dict[str, Any]] = []
    usage_records: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(_run_one, client, request): request for request in requests}
        for index, future in enumerate(as_completed(futures), start=1):
            request = futures[future]
            ontology = request.get("ontology")
            custom_id, parsed, error, usage = future.result()
            if parsed is not None:
                parsed_outputs[custom_id] = parsed
            if error:
                error_map[custom_id] = error
            if usage is not None:
                usage_records.append({
                    "custom_id": custom_id,
                    "ontology": ontology,
                    "model": manifest.get("model"),
                    "usage": usage,
                })
            full_results.append({
                "custom_id": custom_id,
                "ontology": ontology,
                "parsed": parsed,
                "error": error,
                "usage": usage,
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
        "model_override": args.model_override,
        "required_general_llm_baseline_prompt": args.require_general_llm_baseline_prompt,
        "required_stable_hash_shuffle": args.require_stable_hash_shuffle,
    }
    summary["cost"] = _summarize_usage_cost(str(manifest.get("model") or ""), usage_records)

    _write_json(output_run_dir / f"{args.result_prefix}_raw_results.json", full_results)
    _write_json(output_run_dir / f"{args.result_prefix}_trial_results.json", trial_results)
    _write_json(output_run_dir / f"{args.result_prefix}_summary.json", summary)
    _write_json(output_run_dir / f"{args.result_prefix}_usage_records.json", usage_records)

    print("Hit@k:")
    for k in ["1", "2", "3", "4", "5"]:
        row = (summary.get("trial_hit_at_k") or {}).get(k) or {}
        print(f"  H{k}: {row.get('accuracy')} ({row.get('hits')}/{row.get('eligible')})")
    if summary.get("cost"):
        print(f"Cost: ${summary['cost']['estimated_total_cost_usd']}")
    if error_map:
        print(f"Errors: {len(error_map)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
