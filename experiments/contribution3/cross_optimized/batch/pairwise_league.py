from __future__ import annotations

import argparse
import itertools
import json
import re
from pathlib import Path
from typing import Any

from experiments.contribution3.cross_optimized.batch.parse_outputs import extract_response_text, parse_json_response
from experiments.contribution3.cross_optimized.batch.prompts import dumps_compact, response_json_schema
from experiments.contribution3.cross_optimized.data_contract import clean_text, compact_text
from experiments.contribution3.cross_optimized.leak_guard import assert_no_leakage
from experiments.contribution3.cross_optimized.paths import TARGET_SELECTION_CSV
from experiments.contribution3.cross_optimized.retrieve.source_retriever import load_targets


DEFAULT_MODEL = "gpt-5.4-nano"

PAIRWISE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "winner_pgs_id": {"type": "string"},
        "loser_pgs_id": {"type": "string"},
        "confidence": {"type": "string", "enum": ["low", "moderate", "high"]},
        "rationale": {"type": "string", "maxLength": 600},
        "evidence_cited": {"type": "array", "items": {"type": "string"}, "maxItems": 8},
    },
    "required": ["winner_pgs_id", "loser_pgs_id", "confidence", "rationale", "evidence_cited"],
}


PAIRWISE_SYSTEM_PROMPT = """You are a pairwise cross-trait PRS judge.

Use only the target and the two candidate records in the user payload. Treat missing evidence as unavailable; do not assume access to hidden files, private data, external calculations, or prior decisions.

Task: choose which one of candidate_a or candidate_b should be the better primary PGS for cross-trait transfer to the target.

Decision discipline:
- Decide source-trait coherence first: direct, construct-adjacent, measurement/proxy, upstream, downstream, or biological bridge.
- When comparing a clinical source and a measurement source, do not automatically prefer either type. A measurement source needs a concrete target bridge; a diagnosis or construct source needs credible PRS evidence.
- Then compare PGS record quality: endpoint fit, method context, variant count, training/evaluation ancestry, publication context, and visible PGS Catalog performance metadata.
- Do not pick a broad proxy from scale, recency, method branding, support counts, or validation breadth alone unless the source remains coherent for the target.
- Do not pick the closest-looking label automatically if the record is weak and the other source has a clearer bridge plus stronger visible PGS evidence.
- Do not compute or cite numeric formulas.

Return winner_pgs_id and loser_pgs_id from the two input candidates only. Keep rationale terse and cite field paths."""


def _batch_line(custom_id: str, body: dict[str, Any]) -> dict[str, Any]:
    assert_no_leakage(body, root=custom_id)
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/responses",
        "body": body,
    }


def _response_body(
    *,
    model: str,
    user_payload: dict[str, Any],
    max_output_tokens: int = 420,
) -> dict[str, Any]:
    return {
        "model": model,
        "input": [
            {"role": "system", "content": PAIRWISE_SYSTEM_PROMPT},
            {"role": "user", "content": dumps_compact(user_payload)},
        ],
        "reasoning": {"effort": "low"},
        "text": {"format": response_json_schema("cross_pairwise_league_decision", PAIRWISE_SCHEMA)},
        "max_output_tokens": max_output_tokens,
    }


def _unique_candidate_records(records: list[dict[str, Any]], top_n: int) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for record in records:
        pgs_id = clean_text(record.get("pgs_id"))
        if not pgs_id or pgs_id in seen:
            continue
        seen.add(pgs_id)
        out.append(record)
        if len(out) >= top_n:
            break
    return out


def _target_lookup(targets_path: Path) -> dict[str, dict[str, Any]]:
    return {target.target_id: target.to_prompt_dict() for target in load_targets(targets_path)}


def load_candidate_contexts(
    *,
    candidate_request_path: Path,
    top_n: int,
    targets_path: Path = TARGET_SELECTION_CSV,
) -> dict[str, dict[str, Any]]:
    if top_n <= 1:
        raise ValueError("top_n must be greater than 1.")
    targets = _target_lookup(targets_path) if targets_path.exists() else {}
    contexts: dict[str, dict[str, Any]] = {}
    with candidate_request_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            parts = clean_text(row.get("custom_id")).split("__")
            target_id = parts[1] if len(parts) >= 2 else ""
            body = row.get("body") or {}
            user_text = ((body.get("input") or [{}, {}])[1] or {}).get("content")
            payload = json.loads(user_text)
            target = payload.get("target") or {}
            target_id = clean_text(target.get("target_id")) or target_id
            if not target_id:
                continue
            target = {**targets.get(target_id, {}), **target}
            records = _unique_candidate_records(payload.get("frontier_pgs_records") or [], top_n=top_n)
            if len(records) < 2:
                continue
            contexts[target_id] = {
                "target": target,
                "candidates": records,
            }
    return contexts


def build_pairwise_lines(
    *,
    candidate_request_path: Path,
    targets_path: Path = TARGET_SELECTION_CSV,
    model: str = DEFAULT_MODEL,
    top_n: int = 12,
    max_output_tokens: int = 420,
) -> list[dict[str, Any]]:
    contexts = load_candidate_contexts(
        candidate_request_path=candidate_request_path,
        targets_path=targets_path,
        top_n=top_n,
    )
    lines: list[dict[str, Any]] = []
    for target_id, context in contexts.items():
        candidates = context["candidates"]
        for idx_a, idx_b in itertools.combinations(range(len(candidates)), 2):
            payload = {
                "schema_version": "cross_optimized.pairwise_league.v1",
                "target": context["target"],
                "pair": {
                    "candidate_a_index": idx_a,
                    "candidate_b_index": idx_b,
                    "candidate_a": candidates[idx_a],
                    "candidate_b": candidates[idx_b],
                },
                "instruction": (
                    "Pick exactly one winner from candidate_a.pgs_id or candidate_b.pgs_id. "
                    "Treat this as a final-primary head-to-head comparison for this target."
                ),
            }
            body = _response_body(
                model=model,
                user_payload=payload,
                max_output_tokens=max_output_tokens,
            )
            custom_id = f"pairwise__{target_id}__i{idx_a:02d}__j{idx_b:02d}"
            lines.append(_batch_line(custom_id, body))
    return lines


def write_jsonl(lines: list[dict[str, Any]], outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with outpath.open("w", encoding="utf-8") as handle:
        for line in lines:
            handle.write(json.dumps(line, ensure_ascii=False) + "\n")


def _parse_pair_indices(custom_id: str) -> tuple[str, int, int] | None:
    match = re.fullmatch(r"pairwise__(.+)__i(\d+)__j(\d+)", custom_id)
    if not match:
        return None
    return match.group(1), int(match.group(2)), int(match.group(3))


def _parse_pairwise_output(path: Path) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            custom_id = clean_text(row.get("custom_id"))
            parsed = _parse_pair_indices(custom_id)
            if parsed is None:
                continue
            try:
                custom_id, payload, usage = parse_json_response(row)
            except ValueError:
                body = (row.get("response") or {}).get("body") or {}
                payload = _recover_truncated_pairwise_payload(extract_response_text(body))
                usage = body.get("usage") or {}
                if payload is None:
                    target_id, idx_a, idx_b = parsed
                    decisions.append(
                        {
                            "target_id": target_id,
                            "candidate_a_index": idx_a,
                            "candidate_b_index": idx_b,
                            "winner_pgs_id": "",
                            "loser_pgs_id": "",
                            "confidence": "",
                            "rationale": "unrecoverable pairwise output",
                            "evidence_cited": [],
                            "usage": usage,
                        }
                    )
                    continue
            target_id, idx_a, idx_b = parsed
            decisions.append(
                {
                    "target_id": target_id,
                    "candidate_a_index": idx_a,
                    "candidate_b_index": idx_b,
                    "winner_pgs_id": clean_text(payload.get("winner_pgs_id")),
                    "loser_pgs_id": clean_text(payload.get("loser_pgs_id")),
                    "confidence": clean_text(payload.get("confidence")),
                    "rationale": clean_text(payload.get("rationale")),
                    "evidence_cited": [
                        clean_text(value) for value in payload.get("evidence_cited") or [] if clean_text(value)
                    ],
                    "usage": usage,
                }
            )
    return decisions


def _recover_truncated_pairwise_payload(text: str) -> dict[str, Any] | None:
    if not text:
        return None

    def field(name: str) -> str:
        match = re.search(rf'"{re.escape(name)}"\s*:\s*"([^"]+)"', text)
        return clean_text(match.group(1)) if match else ""

    winner = field("winner_pgs_id")
    loser = field("loser_pgs_id")
    confidence = field("confidence") or "low"
    if confidence not in {"low", "moderate", "high"}:
        confidence = "low"
    if not winner or not loser:
        return None
    return {
        "winner_pgs_id": winner,
        "loser_pgs_id": loser,
        "confidence": confidence,
        "rationale": "recovered from truncated JSON prefix",
        "evidence_cited": [],
    }


def _source_bundle_id(record: dict[str, Any]) -> str:
    source_bundles = record.get("source_bundles") or []
    if source_bundles and isinstance(source_bundles[0], dict):
        bundle_id = clean_text(source_bundles[0].get("bundle_id"))
        if bundle_id:
            return bundle_id
    support = record.get("stage_b_support") or {}
    support_ids = support.get("source_bundle_ids") or []
    if support_ids:
        return clean_text(support_ids[0])
    mapped_ids = [clean_text(value) for value in record.get("mapped_trait_ids") or [] if clean_text(value)]
    return "|".join(mapped_ids[:2])


def aggregate_pairwise_predictions(
    *,
    candidate_request_path: Path,
    pairwise_output_path: Path,
    outpath: Path,
    top_n: int = 12,
    targets_path: Path = TARGET_SELECTION_CSV,
) -> list[dict[str, Any]]:
    contexts = load_candidate_contexts(
        candidate_request_path=candidate_request_path,
        targets_path=targets_path,
        top_n=top_n,
    )
    decisions = _parse_pairwise_output(pairwise_output_path)
    decisions_by_target: dict[str, list[dict[str, Any]]] = {}
    for decision in decisions:
        decisions_by_target.setdefault(decision["target_id"], []).append(decision)

    predictions: list[dict[str, Any]] = []
    for target_id, context in contexts.items():
        candidates = context["candidates"]
        candidate_ids = [clean_text(candidate.get("pgs_id")) for candidate in candidates]
        wins = {pgs_id: 0 for pgs_id in candidate_ids}
        losses = {pgs_id: 0 for pgs_id in candidate_ids}
        invalid_count = 0
        for decision in decisions_by_target.get(target_id, []):
            idx_a = int(decision["candidate_a_index"])
            idx_b = int(decision["candidate_b_index"])
            if idx_a >= len(candidate_ids) or idx_b >= len(candidate_ids):
                invalid_count += 1
                continue
            pair_ids = {candidate_ids[idx_a], candidate_ids[idx_b]}
            winner = clean_text(decision.get("winner_pgs_id"))
            loser = clean_text(decision.get("loser_pgs_id"))
            if winner not in pair_ids or loser not in pair_ids or winner == loser:
                invalid_count += 1
                continue
            wins[winner] += 1
            losses[loser] += 1

        original_index = {pgs_id: idx for idx, pgs_id in enumerate(candidate_ids)}
        ranked_ids = sorted(
            candidate_ids,
            key=lambda pgs_id: (-wins[pgs_id], losses[pgs_id], original_index[pgs_id]),
        )
        primary_id = ranked_ids[0]
        primary_record = candidates[original_index[primary_id]]
        issues = []
        if invalid_count:
            issues.append(f"{invalid_count} invalid pairwise decisions ignored")
        predictions.append(
            {
                "target_id": target_id,
                "accepted": True,
                "primary_pgs_id": primary_id,
                "source_bundle_id": _source_bundle_id(primary_record),
                "frontier_pgs_ids": ranked_ids[:12],
                "issues": issues,
                "rationale": compact_text(
                    f"Pairwise league winner over top {len(candidate_ids)} candidates: "
                    f"{primary_id} with {wins[primary_id]} wins and {losses[primary_id]} losses. "
                    "Tie-breaks use original frozen candidate order.",
                    600,
                ),
                "pairwise_wins": wins,
                "pairwise_losses": losses,
            }
        )

    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps({"predictions": predictions}, indent=2), encoding="utf-8")
    return predictions


def build_pairwise_review_evidence(
    *,
    candidate_request_path: Path,
    pairwise_output_path: Path,
    outpath: Path,
    top_n: int = 12,
    targets_path: Path = TARGET_SELECTION_CSV,
    rationale_char_limit: int = 260,
) -> dict[str, Any]:
    contexts = load_candidate_contexts(
        candidate_request_path=candidate_request_path,
        targets_path=targets_path,
        top_n=top_n,
    )
    decisions = _parse_pairwise_output(pairwise_output_path)
    records_by_target: dict[str, dict[str, dict[str, Any]]] = {}
    for target_id, context in contexts.items():
        candidates = context["candidates"]
        candidate_ids = [clean_text(candidate.get("pgs_id")) for candidate in candidates]
        records_by_target[target_id] = {
            pgs_id: {
                "policy": (
                    "Auxiliary LLM head-to-head arguments only; not authority, not a tally, "
                    "and not a rule for final selection."
                ),
                "head_to_head_reviews": [],
            }
            for pgs_id in candidate_ids
            if pgs_id
        }

    for decision in decisions:
        target_id = clean_text(decision.get("target_id"))
        if target_id not in contexts:
            continue
        candidates = contexts[target_id]["candidates"]
        idx_a = int(decision["candidate_a_index"])
        idx_b = int(decision["candidate_b_index"])
        if idx_a >= len(candidates) or idx_b >= len(candidates):
            continue
        pair_ids = {
            clean_text(candidates[idx_a].get("pgs_id")),
            clean_text(candidates[idx_b].get("pgs_id")),
        }
        winner = clean_text(decision.get("winner_pgs_id"))
        loser = clean_text(decision.get("loser_pgs_id"))
        if winner not in pair_ids or loser not in pair_ids or winner == loser:
            continue
        rationale = compact_text(decision.get("rationale"), rationale_char_limit)
        evidence_cited = [
            compact_text(value, 120)
            for value in decision.get("evidence_cited") or []
            if clean_text(value)
        ][:5]
        for pgs_id, outcome, opponent in (
            (winner, "preferred", loser),
            (loser, "not_preferred", winner),
        ):
            target_records = records_by_target.get(target_id) or {}
            pgs_record = target_records.get(pgs_id)
            if pgs_record is None:
                continue
            pgs_record["head_to_head_reviews"].append(
                {
                    "opponent_pgs_id": opponent,
                    "outcome": outcome,
                    "confidence": clean_text(decision.get("confidence")),
                    "rationale": rationale,
                    "evidence_cited": evidence_cited,
                }
            )

    payload = {
        "schema_version": "cross_optimized.pairwise_review_evidence.v1",
        "evidence": records_by_target,
    }
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def _load_prediction_rows(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("predictions", data.get("results", []))
    if not isinstance(data, list):
        raise ValueError(f"Prediction file must contain a list: {path}")
    return [row for row in data if isinstance(row, dict)]


def build_switch_policy_predictions(
    *,
    proposed_predictions_path: Path,
    league_predictions_path: Path,
    outpath: Path,
    challenger_min_wins: int = 8,
    proposed_max_wins: int = 8,
) -> list[dict[str, Any]]:
    proposed = {clean_text(row.get("target_id")): row for row in _load_prediction_rows(proposed_predictions_path)}
    league = {clean_text(row.get("target_id")): row for row in _load_prediction_rows(league_predictions_path)}
    rows: list[dict[str, Any]] = []
    for target_id, proposed_row in proposed.items():
        if not target_id:
            continue
        league_row = league.get(target_id) or {}
        proposed_id = clean_text(proposed_row.get("primary_pgs_id"))
        challenger_id = clean_text(league_row.get("primary_pgs_id"))
        wins = league_row.get("pairwise_wins") or {}
        proposed_wins = int(wins.get(proposed_id, -1))
        challenger_wins = int(wins.get(challenger_id, -1))
        switched = (
            bool(challenger_id)
            and challenger_id != proposed_id
            and challenger_wins >= challenger_min_wins
            and 0 <= proposed_wins <= proposed_max_wins
        )
        primary_id = challenger_id if switched else proposed_id
        frontier: list[str] = []
        for pgs_id in [
            primary_id,
            *(proposed_row.get("frontier_pgs_ids") or []),
            *(league_row.get("frontier_pgs_ids") or []),
        ]:
            clean_id = clean_text(pgs_id)
            if clean_id and clean_id not in frontier:
                frontier.append(clean_id)
        rows.append(
            {
                "target_id": target_id,
                "accepted": True,
                "primary_pgs_id": primary_id,
                "source_bundle_id": (
                    clean_text(league_row.get("source_bundle_id"))
                    if switched
                    else clean_text(proposed_row.get("source_bundle_id"))
                ),
                "frontier_pgs_ids": frontier[:12],
                "issues": [],
                "rationale": (
                    f"Global switch policy: challenger_min_wins={challenger_min_wins}, "
                    f"proposed_max_wins={proposed_max_wins}, switched={switched}. "
                    f"proposed_wins={proposed_wins}, challenger_wins={challenger_wins}."
                ),
            }
        )
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps({"predictions": rows}, indent=2), encoding="utf-8")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and aggregate pairwise-league cross-optimized batches.")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--candidate-request", type=Path, required=True)
    build.add_argument("--targets", type=Path, default=TARGET_SELECTION_CSV)
    build.add_argument("--model", default=DEFAULT_MODEL)
    build.add_argument("--top-n", type=int, default=12)
    build.add_argument("--max-output-tokens", type=int, default=420)
    build.add_argument("--out", type=Path, required=True)

    aggregate = sub.add_parser("aggregate")
    aggregate.add_argument("--candidate-request", type=Path, required=True)
    aggregate.add_argument("--pairwise-output", type=Path, required=True)
    aggregate.add_argument("--targets", type=Path, default=TARGET_SELECTION_CSV)
    aggregate.add_argument("--top-n", type=int, default=12)
    aggregate.add_argument("--out", type=Path, required=True)

    evidence = sub.add_parser("evidence")
    evidence.add_argument("--candidate-request", type=Path, required=True)
    evidence.add_argument("--pairwise-output", type=Path, required=True)
    evidence.add_argument("--targets", type=Path, default=TARGET_SELECTION_CSV)
    evidence.add_argument("--top-n", type=int, default=12)
    evidence.add_argument("--rationale-char-limit", type=int, default=260)
    evidence.add_argument("--out", type=Path, required=True)

    policy = sub.add_parser("switch-policy")
    policy.add_argument("--proposed-predictions", type=Path, required=True)
    policy.add_argument("--league-predictions", type=Path, required=True)
    policy.add_argument("--challenger-min-wins", type=int, default=8)
    policy.add_argument("--proposed-max-wins", type=int, default=8)
    policy.add_argument("--out", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "build":
        lines = build_pairwise_lines(
            candidate_request_path=args.candidate_request,
            targets_path=args.targets,
            model=args.model,
            top_n=args.top_n,
            max_output_tokens=args.max_output_tokens,
        )
        write_jsonl(lines, args.out)
        print(f"Wrote {len(lines)} pairwise requests -> {args.out}")
    elif args.command == "aggregate":
        predictions = aggregate_pairwise_predictions(
            candidate_request_path=args.candidate_request,
            pairwise_output_path=args.pairwise_output,
            targets_path=args.targets,
            top_n=args.top_n,
            outpath=args.out,
        )
        print(f"Wrote {len(predictions)} pairwise-league predictions -> {args.out}")
    elif args.command == "evidence":
        payload = build_pairwise_review_evidence(
            candidate_request_path=args.candidate_request,
            pairwise_output_path=args.pairwise_output,
            targets_path=args.targets,
            top_n=args.top_n,
            rationale_char_limit=args.rationale_char_limit,
            outpath=args.out,
        )
        n_targets = len(payload.get("evidence") or {})
        print(f"Wrote pairwise review evidence for {n_targets} targets -> {args.out}")
    else:
        predictions = build_switch_policy_predictions(
            proposed_predictions_path=args.proposed_predictions,
            league_predictions_path=args.league_predictions,
            challenger_min_wins=args.challenger_min_wins,
            proposed_max_wins=args.proposed_max_wins,
            outpath=args.out,
        )
        print(f"Wrote {len(predictions)} switch-policy predictions -> {args.out}")


if __name__ == "__main__":
    main()
