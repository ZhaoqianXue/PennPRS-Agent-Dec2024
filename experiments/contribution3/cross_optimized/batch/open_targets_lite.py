from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from experiments.contribution3.cross_optimized.data_contract import clean_text, compact_text


ONTOLOGY_PREFIXES = ("EFO_", "MONDO_", "HP_", "Orphanet_")
QUERY_SPLIT_RE = re.compile(r"\s*(?:[,;/|]|\band\b)\s*", flags=re.IGNORECASE)
BRACKETED_TEXT_RE = re.compile(r"\[[^\]]+\]|\([^)]*\)")


def _extract_user_payloads(candidate_request_path: Path) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    with candidate_request_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if not raw_line.strip():
                continue
            row = json.loads(raw_line)
            inputs = ((row.get("body") or {}).get("input") or [])
            if len(inputs) >= 2 and isinstance(inputs[1].get("content"), str):
                payloads.append(json.loads(inputs[1]["content"]))
    return payloads


def _expanded_queries(values: list[Any], *, cap: int = 10) -> list[str]:
    queries: list[str] = []
    seen: set[str] = set()

    def add(value: Any) -> None:
        text = compact_text(value, 160)
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            queries.append(text)

    for value in values:
        text = compact_text(value, 160)
        if not text:
            continue
        add(text)
        unbracketed = re.sub(r"\s+", " ", BRACKETED_TEXT_RE.sub(" ", text)).strip()
        add(unbracketed)
        for part in QUERY_SPLIT_RE.split(unbracketed):
            part = re.sub(r"\s+", " ", part).strip(" -")
            if len(part) >= 4:
                add(part)
        if len(queries) >= cap:
            return queries[:cap]
    return queries[:cap]


def _first_ontology_id(values: list[Any]) -> str:
    for value in values:
        text = clean_text(value)
        if text.startswith(ONTOLOGY_PREFIXES):
            return text
    return ""


def _search_first_disease_id(client: Any, queries: list[str]) -> str:
    for query in queries:
        result = client.search_diseases(query, size=3)
        hits = result.get("hits") if isinstance(result, dict) else []
        for hit in hits or []:
            hit_id = clean_text(hit.get("id") if isinstance(hit, dict) else getattr(hit, "id", ""))
            if hit_id:
                return hit_id
    return ""


def _target_queries(target: dict[str, Any]) -> list[str]:
    return _expanded_queries(
        [
            target.get("input_ontology"),
            target.get("ontology_id"),
            target.get("label"),
            target.get("target_label"),
            target.get("input_description"),
            *(target.get("aliases") or []),
        ]
    )


def _candidate_queries(card: dict[str, Any]) -> list[str]:
    return _expanded_queries([*(card.get("mapped_trait_labels") or []), card.get("reported_trait")])


def _resolve_target_disease_id(
    *,
    target: dict[str, Any],
    client: Any,
    resolve_cache: dict[tuple[str, tuple[str, ...]], str],
) -> str:
    direct_id = _first_ontology_id(_target_queries(target))
    if direct_id:
        return direct_id
    queries = tuple(_target_queries(target))
    key = ("target", queries)
    if key not in resolve_cache:
        resolve_cache[key] = _search_first_disease_id(client, list(queries))
    return resolve_cache[key]


def _resolve_candidate_disease_id(
    *,
    card: dict[str, Any],
    client: Any,
    resolve_cache: dict[tuple[str, tuple[str, ...]], str],
) -> str:
    direct_id = _first_ontology_id(card.get("mapped_trait_ids") or [])
    if direct_id:
        return direct_id
    queries = tuple(_candidate_queries(card))
    key = ("candidate", queries)
    if key not in resolve_cache:
        resolve_cache[key] = _search_first_disease_id(client, list(queries))
    return resolve_cache[key]


def _profile_for_id(
    *,
    disease_id: str,
    client: Any,
    profile_cache: dict[str, dict[str, Any]],
    profile_page_size: int,
) -> dict[str, Any]:
    if not disease_id:
        return {}
    if disease_id not in profile_cache:
        profile_cache[disease_id] = client.get_disease_target_profile(disease_id, page_size=profile_page_size)
    return profile_cache[disease_id]


def _datatype_ids(row: dict[str, Any]) -> list[str]:
    values = []
    for item in row.get("datatypeScores") or []:
        if isinstance(item, dict):
            value = clean_text(item.get("id"))
            if value:
                values.append(value)
    return sorted(set(values))


def _associated_target_lookup(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in profile.get("associated_targets") or []:
        target_id = clean_text(row.get("id"))
        if target_id:
            out[target_id] = {
                "gene": clean_text(row.get("approvedSymbol")),
                "target_id": target_id,
                "datatypes": _datatype_ids(row),
            }
    return out


def _shared_entity_rows(target_profile: dict[str, Any], candidate_profile: dict[str, Any], key: str) -> list[dict[str, Any]]:
    target_rows = {
        clean_text(row.get("id")): {"id": clean_text(row.get("id")), "name": clean_text(row.get("name"))}
        for row in target_profile.get(key) or []
        if isinstance(row, dict) and clean_text(row.get("id"))
    }
    candidate_ids = {
        clean_text(row.get("id"))
        for row in candidate_profile.get(key) or []
        if isinstance(row, dict) and clean_text(row.get("id"))
    }
    return [target_rows[row_id] for row_id in sorted(set(target_rows) & candidate_ids)]


def _pair_evidence(
    *,
    target_disease_id: str,
    candidate_disease_id: str,
    card: dict[str, Any],
    target_profile: dict[str, Any],
    candidate_profile: dict[str, Any],
    shared_gene_cap: int,
) -> dict[str, Any]:
    target_lookup = _associated_target_lookup(target_profile)
    candidate_lookup = _associated_target_lookup(candidate_profile)
    shared_ids = [target_id for target_id in target_lookup if target_id in candidate_lookup]
    return {
        "target_disease_id": target_disease_id,
        "target_disease_label": clean_text(target_profile.get("name")),
        "candidate_disease_id": candidate_disease_id,
        "candidate_disease_label": clean_text(candidate_profile.get("name")),
        "candidate_trait_basis": {
            "mapped_trait_ids": [clean_text(v) for v in card.get("mapped_trait_ids") or [] if clean_text(v)][:3],
            "mapped_trait_labels": [clean_text(v) for v in card.get("mapped_trait_labels") or [] if clean_text(v)][:3],
            "reported_trait": compact_text(card.get("reported_trait"), 120),
        },
        "target_associated_gene_count": len(target_lookup),
        "candidate_associated_gene_count": len(candidate_lookup),
        "shared_gene_count": len(shared_ids),
        "shared_genes": [
            {
                "gene": target_lookup[target_id]["gene"] or candidate_lookup[target_id]["gene"],
                "target_id": target_id,
                "target_datatypes": target_lookup[target_id]["datatypes"],
                "candidate_datatypes": candidate_lookup[target_id]["datatypes"],
            }
            for target_id in shared_ids[:shared_gene_cap]
        ],
        "shared_therapeutic_areas": _shared_entity_rows(target_profile, candidate_profile, "therapeutic_areas"),
        "shared_ancestors": _shared_entity_rows(target_profile, candidate_profile, "ancestors"),
    }


def compact_open_targets_bridge_card(raw: dict[str, Any], *, shared_gene_cap: int = 5) -> dict[str, Any]:
    if raw.get("unavailable_reason"):
        return {
            "target_disease_id": clean_text(raw.get("target_disease_id")),
            "candidate_disease_id": clean_text(raw.get("candidate_disease_id")),
            "unavailable_reason": clean_text(raw.get("unavailable_reason")),
            "caveats": ["OpenTargets disease mapping was unavailable for this pair"],
        }

    target_disease_id = clean_text(raw.get("target_disease_id"))
    candidate_disease_id = clean_text(raw.get("candidate_disease_id"))
    target_label = clean_text(raw.get("target_disease_label"))
    candidate_label = clean_text(raw.get("candidate_disease_label"))
    relationship_observations: list[str] = []
    if target_disease_id and candidate_disease_id and target_disease_id == candidate_disease_id:
        relationship_observations.append("same ontology id")
    elif target_disease_id or candidate_disease_id:
        relationship_observations.append("different ontology ids")

    for row in raw.get("shared_therapeutic_areas") or []:
        if isinstance(row, dict):
            name = clean_text(row.get("name"))
            if name:
                relationship_observations.append(f"shared therapeutic area: {name}")
                break
    for row in raw.get("shared_ancestors") or []:
        if isinstance(row, dict):
            name = clean_text(row.get("name"))
            if name:
                relationship_observations.append(f"shared ancestor: {name}")
                break

    shared_gene_count = int(raw.get("shared_gene_count") or 0)
    target_gene_count = int(raw.get("target_associated_gene_count") or 0)
    candidate_gene_count = int(raw.get("candidate_associated_gene_count") or 0)
    if shared_gene_count:
        relationship_observations.append(
            "shared associated targets: "
            f"{shared_gene_count} of target_top{target_gene_count} and candidate_top{candidate_gene_count}"
        )
    else:
        relationship_observations.append(
            f"no shared associated targets in target_top{target_gene_count} and candidate_top{candidate_gene_count}"
        )

    examples: list[dict[str, Any]] = []
    for row in (raw.get("shared_genes") or [])[:shared_gene_cap]:
        if not isinstance(row, dict):
            continue
        examples.append(
            {
                "gene": clean_text(row.get("gene")),
                "target_id": clean_text(row.get("target_id")),
                "target_datatypes": [clean_text(value) for value in row.get("target_datatypes") or [] if clean_text(value)],
                "candidate_datatypes": [
                    clean_text(value) for value in row.get("candidate_datatypes") or [] if clean_text(value)
                ],
            }
        )

    card: dict[str, Any] = {
        "target_disease_id": target_disease_id,
        "target_disease_label": target_label,
        "candidate_disease_id": candidate_disease_id,
        "candidate_disease_label": candidate_label,
        "candidate_trait_basis": raw.get("candidate_trait_basis") or {},
        "relationship_observations": relationship_observations,
        "shared_target_examples": examples,
        "caveats": [
            "associated target overlap is raw OpenTargets context, not a causal or predictive claim",
            "top-page associated targets can overrepresent broad, well-studied traits",
        ],
    }
    return {key: value for key, value in card.items() if value not in (None, "", [], {})}


def build_open_targets_lite_evidence(
    *,
    candidate_request_path: Path,
    client: Any,
    top_n: int = 7,
    profile_page_size: int = 80,
    shared_gene_cap: int = 20,
    evidence_mode: str = "raw",
) -> dict[str, Any]:
    if top_n <= 0:
        raise ValueError("top_n must be positive.")
    if evidence_mode not in {"raw", "bridge_card"}:
        raise ValueError("evidence_mode must be one of: raw, bridge_card.")
    resolve_cache: dict[tuple[str, tuple[str, ...]], str] = {}
    profile_cache: dict[str, dict[str, Any]] = {}
    out: dict[str, Any] = {
        "schema_version": (
            "cross_optimized.open_targets_bridge_card.v1"
            if evidence_mode == "bridge_card"
            else "cross_optimized.open_targets_lite.v1"
        ),
        "parameters": {
            "top_n": top_n,
            "profile_page_size": profile_page_size,
            "shared_gene_cap": shared_gene_cap,
            "evidence_mode": evidence_mode,
        },
    }
    for payload in _extract_user_payloads(candidate_request_path):
        target = payload.get("target") or {}
        target_id = clean_text(target.get("target_id"))
        if not target_id:
            continue
        target_disease_id = _resolve_target_disease_id(target=target, client=client, resolve_cache=resolve_cache)
        target_profile = _profile_for_id(
            disease_id=target_disease_id,
            client=client,
            profile_cache=profile_cache,
            profile_page_size=profile_page_size,
        )
        records = payload.get("candidate_evidence_cards") or payload.get("frontier_pgs_records") or []
        for card in records[:top_n]:
            if not isinstance(card, dict):
                continue
            pgs_id = clean_text(card.get("pgs_id"))
            if not pgs_id:
                continue
            candidate_disease_id = _resolve_candidate_disease_id(card=card, client=client, resolve_cache=resolve_cache)
            candidate_profile = _profile_for_id(
                disease_id=candidate_disease_id,
                client=client,
                profile_cache=profile_cache,
                profile_page_size=profile_page_size,
            )
            if not target_disease_id or not candidate_disease_id:
                evidence = {
                    "target_disease_id": target_disease_id,
                    "candidate_disease_id": candidate_disease_id,
                    "unavailable_reason": "target_or_candidate_not_resolved",
                }
            else:
                evidence = _pair_evidence(
                    target_disease_id=target_disease_id,
                    candidate_disease_id=candidate_disease_id,
                    card=card,
                    target_profile=target_profile,
                    candidate_profile=candidate_profile,
                    shared_gene_cap=shared_gene_cap,
                )
            if evidence_mode == "bridge_card":
                evidence = compact_open_targets_bridge_card(evidence, shared_gene_cap=min(shared_gene_cap, 5))
            out.setdefault(target_id, {})[pgs_id] = evidence
    return out


def _default_client() -> Any:
    from src.server.core.opentargets_client import OpenTargetsClient

    return OpenTargetsClient()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build cost-aware raw OpenTargets Lite evidence for Stage D.")
    parser.add_argument("--candidate-request", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--top-n", type=int, default=7)
    parser.add_argument("--profile-page-size", type=int, default=80)
    parser.add_argument("--shared-gene-cap", type=int, default=20)
    parser.add_argument("--evidence-mode", default="raw", choices=["raw", "bridge_card"])
    args = parser.parse_args()

    evidence = build_open_targets_lite_evidence(
        candidate_request_path=args.candidate_request,
        client=_default_client(),
        top_n=args.top_n,
        profile_page_size=args.profile_page_size,
        shared_gene_cap=args.shared_gene_cap,
        evidence_mode=args.evidence_mode,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    target_count = len([key for key in evidence if key not in {"schema_version", "parameters"}])
    pair_count = sum(
        len(value)
        for key, value in evidence.items()
        if key not in {"schema_version", "parameters"} and isinstance(value, dict)
    )
    print(f"Wrote OpenTargets Lite evidence for {target_count} targets / {pair_count} pairs -> {args.out}")


if __name__ == "__main__":
    main()
