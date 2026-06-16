from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ModelPrice:
    input_per_1m: float
    cached_input_per_1m: float
    output_per_1m: float
    reasoning_output_per_1m: float | None = None
    batch_discount: float = 1.0


def load_price_manifest(path: Path) -> dict[str, ModelPrice]:
    data = json.loads(path.read_text(encoding="utf-8"))
    prices: dict[str, ModelPrice] = {}
    for model, row in data.items():
        prices[model] = ModelPrice(
            input_per_1m=float(row["input_per_1m"]),
            cached_input_per_1m=float(row.get("cached_input_per_1m", row["input_per_1m"])),
            output_per_1m=float(row["output_per_1m"]),
            reasoning_output_per_1m=(
                float(row["reasoning_output_per_1m"])
                if row.get("reasoning_output_per_1m") is not None
                else None
            ),
            batch_discount=float(row.get("batch_discount", 1.0)),
        )
    return prices


def _usage_from_output_line(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    response = row.get("response") or {}
    body = response.get("body") or {}
    usage = body.get("usage")
    if not usage:
        raise ValueError(f"Missing usage for custom_id={row.get('custom_id')}")
    model = body.get("model")
    if not model:
        raise ValueError(f"Missing model for custom_id={row.get('custom_id')}")
    return str(model), usage


def _estimate_cost(model: str, usage: dict[str, Any], price: ModelPrice) -> dict[str, Any]:
    prompt_tokens = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
    completion_tokens = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
    prompt_details = usage.get("prompt_tokens_details") or usage.get("input_tokens_details") or {}
    completion_details = usage.get("completion_tokens_details") or usage.get("output_tokens_details") or {}
    cached_tokens = int(prompt_details.get("cached_tokens") or 0)
    reasoning_tokens = int(completion_details.get("reasoning_tokens") or 0)
    uncached_tokens = max(prompt_tokens - cached_tokens, 0)
    visible_output_tokens = max(completion_tokens - reasoning_tokens, 0)
    reasoning_price = price.reasoning_output_per_1m or price.output_per_1m
    cost = (
        uncached_tokens * price.input_per_1m
        + cached_tokens * price.cached_input_per_1m
        + visible_output_tokens * price.output_per_1m
        + reasoning_tokens * reasoning_price
    ) / 1_000_000
    cost *= price.batch_discount
    return {
        "model": model,
        "prompt_tokens": prompt_tokens,
        "cached_tokens": cached_tokens,
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "estimated_cost_usd": round(cost, 8),
    }


def build_cost_ledger(batch_output_jsonl: Path, price_manifest: Path, outpath: Path) -> list[dict[str, Any]]:
    prices = load_price_manifest(price_manifest)
    rows: list[dict[str, Any]] = []
    with batch_output_jsonl.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            model, usage = _usage_from_output_line(row)
            if model not in prices:
                raise ValueError(f"Model {model!r} not found in price manifest.")
            estimate = _estimate_cost(model, usage, prices[model])
            rows.append(
                {
                    "custom_id": row.get("custom_id"),
                    "request_id": (row.get("response") or {}).get("request_id"),
                    **estimate,
                }
            )
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with outpath.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a token/cost ledger from Batch API output JSONL.")
    parser.add_argument("--batch-output", type=Path, required=True)
    parser.add_argument("--price-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    rows = build_cost_ledger(args.batch_output, args.price_manifest, args.out)
    total = round(sum(float(row["estimated_cost_usd"]) for row in rows), 8)
    print(f"Wrote {len(rows)} ledger rows -> {args.out}")
    print(f"Total estimated cost USD: {total}")


if __name__ == "__main__":
    main()
