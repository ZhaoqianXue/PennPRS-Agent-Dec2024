"""Assemble the within-trait three-method comparison table:

  (A) PRS Agent            -> with_domain summary `modal_hit_at_k`
  (B) General LLM selector -> without_domain summary `modal_hit_at_k`
  (C) PGS Catalog reported-max -> baseline `hit_at_k` block (deterministic, no LLM;
       identical in either summary because both embed the same baseline)

All three are scored by the SAME AoU-benchmark Hit@k scorer over the SAME
candidate pool, so the numbers are directly comparable. PRS Agent must
significantly beat both (B) and (C) on Hit@1..5 (Hit@1 the most important).

Usage:
  python generate_within_three_method_comparison.py \
      --agent-summary  <with-domain .../experiment_with_domain_summary.json> \
      --llm-summary    <without-domain .../experiment_without_domain_summary.json> \
      [--out <comparison.md>]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

KS = [1, 2, 3, 4, 5]


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _hits_acc(block: dict, k: int) -> tuple[int, float]:
    cell = (block or {}).get(str(k)) or {}
    return int(cell.get("hits") or 0), float(cell.get("accuracy") or 0.0)


def _cost(summary: dict) -> float | None:
    # batch cost is embedded by the runner when available
    for key in ("estimated_total_cost_usd", "cost_usd"):
        v = summary.get(key)
        if isinstance(v, (int, float)):
            return float(v)
    for key in ("cost", "batch_cost", "token_usage_cost"):
        bc = summary.get(key) or {}
        v = bc.get("estimated_total_cost_usd") if isinstance(bc, dict) else None
        if isinstance(v, (int, float)):
            return float(v)
    return None


def _cost_details(summary: dict) -> dict:
    for key in ("cost", "batch_cost", "token_usage_cost"):
        block = summary.get(key)
        if isinstance(block, dict) and isinstance(block.get("estimated_total_cost_usd"), (int, float)):
            return block
    for key in ("estimated_total_cost_usd", "cost_usd"):
        v = summary.get(key)
        if isinstance(v, (int, float)):
            return {"estimated_total_cost_usd": float(v)}
    return {}


def _hit_block(summary: dict) -> dict:
    return summary.get("modal_hit_at_k") or summary.get("trial_hit_at_k") or {}


def _format_cost(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value == 0:
        return "$0.00"
    return f"${value:.4f}"


def build_report(agent: dict, llm: dict) -> tuple[str, dict]:
    total = agent.get("total_ontologies") or llm.get("total_ontologies")
    model = agent.get("model") or llm.get("model")
    agent_hits = _hit_block(agent)
    llm_hits = _hit_block(llm)
    # Reported-max baseline is identical in both; prefer the agent run's copy.
    base = ((agent.get("baseline") or {}).get("hit_at_k")) or ((llm.get("baseline") or {}).get("hit_at_k")) or {}
    base_name = (agent.get("baseline") or {}).get("name") or (llm.get("baseline") or {}).get("name")

    rows = {
        "PRS Agent (LLM + harness + reworked skill)": agent_hits,
        "General LLM selector (no skill/tools)": llm_hits,
        f"PGS Catalog reported-max ({base_name})": base,
    }

    lines = []
    lines.append("# Within-trait three-method comparison\n")
    lines.append(f"- Disease set: **{total} diseases** | Model: **{model}** "
                 f"| Scorer: AoU-benchmark Hit@k (tie-aware top-k)\n")
    header = "| Method | " + " | ".join(f"Hit@{k}" for k in KS) + " |"
    sep = "|" + "---|" * (len(KS) + 1)
    lines.append(header)
    lines.append(sep)
    table = {}
    for label, block in rows.items():
        cells = []
        per_k = {}
        for k in KS:
            h, a = _hits_acc(block, k)
            cells.append(f"{h}/{total} ({a*100:.1f}%)")
            per_k[k] = {"hits": h, "accuracy": a}
        table[label] = per_k
        lines.append(f"| {label} | " + " | ".join(cells) + " |")

    # lift of the agent over the two foils at Hit@1
    a1 = _hits_acc(agent_hits, 1)[1]
    b1 = _hits_acc(llm_hits, 1)[1]
    c1 = _hits_acc(base, 1)[1]
    lines.append("")
    lines.append(f"- **Hit@1 lift**: PRS Agent {a1*100:.1f}% vs General LLM {b1*100:.1f}% "
                 f"({(a1-b1)*100:+.1f}pp) vs reported-max {c1*100:.1f}% ({(a1-c1)*100:+.1f}pp)")

    ac, lc = _cost(agent), _cost(llm)
    if ac is not None or lc is not None:
        lines.append(
            f"- **API cost ({model})**: PRS Agent {_format_cost(ac)} "
            f"| General LLM {_format_cost(lc)} "
            f"| PGS reported-max $0.00 (deterministic, no LLM calls)"
        )

    payload = {
        "total_diseases": total,
        "model": model,
        "table": table,
        "hit1": {"prs_agent": a1, "general_llm": b1, "reported_max": c1},
        "cost_usd": {"prs_agent": ac, "general_llm": lc, "reported_max": 0.0},
        "cost_details": {
            "prs_agent": _cost_details(agent),
            "general_llm": _cost_details(llm),
            "reported_max": {
                "method": "deterministic_reported_max_baseline_no_llm_calls",
                "estimated_total_cost_usd": 0.0,
            },
        },
    }
    return "\n".join(lines) + "\n", payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-summary", required=True)
    ap.add_argument("--llm-summary", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    agent = _load(args.agent_summary)
    llm = _load(args.llm_summary)
    md, payload = build_report(agent, llm)
    print(md)
    if args.out:
        out = Path(args.out)
        out.write_text(md, encoding="utf-8")
        out.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Wrote {out} and {out.with_suffix('.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
