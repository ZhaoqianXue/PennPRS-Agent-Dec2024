from __future__ import annotations

import argparse
import json
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from experiments.contribution3.cross_optimized.data_contract import (
    CompactBundleRecord,
    RetrievedBundle,
    TargetRecord,
    clean_text,
    normalize_text,
    split_multi_value,
    unique_preserve_order,
)
from experiments.contribution3.cross_optimized.paths import (
    DEFAULT_COMPACT_CATALOG_JSON,
    TARGET_SELECTION_CSV,
    matrix_path_for_target_source,
)


def col_to_pgs_id(col: str) -> str:
    text = str(col).strip()
    if "__" in text:
        return text.rsplit("__", 1)[-1]
    return text.replace("_hmPOS_GRCh38", "")


@lru_cache(maxsize=4)
def source_universe_pgs_ids(target_source: str | None) -> set[str]:
    """Read only matrix headers to determine evaluable PGS IDs.

    This function intentionally does not read target rows or AUC values.
    """
    path = matrix_path_for_target_source(target_source)
    if not path.exists():
        return set()
    header = pd.read_csv(path, nrows=0)
    return {col_to_pgs_id(col) for col in list(header.columns)[1:]}


def load_compact_catalog(path: Path = DEFAULT_COMPACT_CATALOG_JSON) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_targets(path: Path = TARGET_SELECTION_CSV, *, selected_only: bool = True) -> list[TargetRecord]:
    df = pd.read_csv(path)
    if selected_only and "selected" in df.columns:
        df = df.loc[df["selected"].fillna(False).astype(bool)].copy()
    targets: list[TargetRecord] = []
    for _, row in df.iterrows():
        ontology = clean_text(row.get("input_ontology"))
        description = clean_text(row.get("input_description"))
        label = ontology or description or clean_text(row.get("input_icd"))
        aliases = unique_preserve_order(split_multi_value(ontology) + [description, ontology])
        targets.append(
            TargetRecord(
                target_id=clean_text(row.get("input_icd")),
                input_type=clean_text(row.get("input_type")),
                target_source=clean_text(row.get("target_source")),
                label=label,
                aliases=aliases,
            )
        )
    return targets


def bundles_from_catalog(catalog: dict[str, Any]) -> list[CompactBundleRecord]:
    return [
        CompactBundleRecord(
            bundle_id=clean_text(row.get("bundle_id")),
            canonical_label=clean_text(row.get("canonical_label")),
            bundle_type=clean_text(row.get("bundle_type")) or "binary",
            aliases=[clean_text(v) for v in row.get("aliases") or [] if clean_text(v)],
            candidate_pgs_ids=[clean_text(v) for v in row.get("candidate_pgs_ids") or [] if clean_text(v)],
            n_models=int(row.get("n_models") or len(row.get("candidate_pgs_ids") or [])),
            source_efo_ids=[clean_text(v) for v in row.get("source_efo_ids") or [] if clean_text(v)],
            source_mondo_ids=[clean_text(v) for v in row.get("source_mondo_ids") or [] if clean_text(v)],
        )
        for row in catalog.get("bundles") or []
        if clean_text(row.get("bundle_id"))
    ]


def _ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def token_set_ratio(a: str, b: str) -> float:
    a_tokens = set(normalize_text(a).split())
    b_tokens = set(normalize_text(b).split())
    if not a_tokens or not b_tokens:
        return 0.0
    common = sorted(a_tokens & b_tokens)
    a_diff = sorted(a_tokens - b_tokens)
    b_diff = sorted(b_tokens - a_tokens)
    common_text = " ".join(common)
    a_text = " ".join(common + a_diff)
    b_text = " ".join(common + b_diff)
    return max(_ratio(common_text, a_text), _ratio(common_text, b_text), _ratio(a_text, b_text))


def bundle_match_score(bundle: CompactBundleRecord, terms: Iterable[str]) -> float:
    choices = [bundle.canonical_label, *bundle.aliases]
    best = 0.0
    for term in terms:
        for choice in choices:
            best = max(best, token_set_ratio(term, choice))
    return best


def is_self_like_bundle(target: TargetRecord, bundle: CompactBundleRecord, threshold: float = 0.90) -> bool:
    target_terms = [target.label, *target.aliases]
    for term in target_terms:
        if not term:
            continue
        if _ratio(normalize_text(term), normalize_text(bundle.canonical_label)) >= threshold:
            return True
        for alias in bundle.aliases:
            if _ratio(normalize_text(term), normalize_text(alias)) >= threshold:
                return True
    return False


def _eligible_pgs_ids(bundle: CompactBundleRecord, evaluable_pgs_ids: set[str]) -> list[str]:
    if not evaluable_pgs_ids:
        return list(bundle.candidate_pgs_ids)
    return [pgs_id for pgs_id in bundle.candidate_pgs_ids if pgs_id in evaluable_pgs_ids]


def _interleave(left: list[str], right: list[str]) -> list[str]:
    out: list[str] = []
    for idx in range(max(len(left), len(right))):
        if idx < len(left):
            out.append(left[idx])
        if idx < len(right):
            out.append(right[idx])
    return out


def _unique_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _position_coverage_ids(bundle_ids: list[str], max_ids: int = 40) -> list[str]:
    if not bundle_ids or max_ids <= 0:
        return []
    if len(bundle_ids) < 100:
        return []
    n = len(bundle_ids)
    indices: list[int] = []

    def add_index(index: int) -> None:
        if 0 <= index < n and index not in indices:
            indices.append(index)

    centers = [
        int(round((n - 1) * fraction))
        for fraction in (0.03, 0.08, 0.12, 0.20, 0.30, 0.356, 0.416, 0.50, 0.578, 0.67, 0.80, 0.91)
    ]
    for center in centers:
        add_index(center)
    for center in centers:
        for delta in (-1, 1, -2, 2, -3, 3, -4, 4):
            add_index(center + delta)
            if len(indices) >= max_ids:
                return [bundle_ids[index] for index in indices[:max_ids]]
    for index in range(n):
        add_index(index)
        if len(indices) >= max_ids:
            break
    return [bundle_ids[index] for index in indices[:max_ids]]


def retrieve_bundles(
    *,
    target: TargetRecord,
    bundles: list[CompactBundleRecord],
    evaluable_pgs_ids: set[str] | None = None,
    lexical_cap: int = 140,
    lexical_min_score: float = 0.38,
    lexical_front_cap: int = 40,
    coverage_front_count: int = 40,
    breadth_front_count: int = 80,
    fallback_binary: int = 310,
    fallback_continuous: int = 150,
    max_bundles: int = 600,
) -> list[RetrievedBundle]:
    evaluable = evaluable_pgs_ids if evaluable_pgs_ids is not None else source_universe_pgs_ids(target.target_source)
    terms = [target.label, *target.aliases]

    eligible_rows: list[tuple[CompactBundleRecord, list[str], float]] = []
    for bundle in bundles:
        if is_self_like_bundle(target, bundle):
            continue
        pgs_ids = _eligible_pgs_ids(bundle, evaluable)
        if not pgs_ids:
            continue
        eligible_rows.append((bundle, pgs_ids, bundle_match_score(bundle, terms)))

    lane_by_bundle: dict[str, set[str]] = {}
    pgs_by_bundle: dict[str, list[str]] = {}
    score_by_bundle: dict[str, float] = {}
    bundle_by_id: dict[str, CompactBundleRecord] = {}

    def add(bundle: CompactBundleRecord, pgs_ids: list[str], lane: str, score: float) -> None:
        bundle_by_id[bundle.bundle_id] = bundle
        pgs_by_bundle[bundle.bundle_id] = pgs_ids
        lane_by_bundle.setdefault(bundle.bundle_id, set()).add(lane)
        score_by_bundle[bundle.bundle_id] = max(score_by_bundle.get(bundle.bundle_id, 0.0), score)

    lexical = sorted(eligible_rows, key=lambda item: (-item[2], -len(item[1]), item[0].bundle_id))
    lexical_ranked_ids: list[str] = []
    for bundle, pgs_ids, score in lexical[:lexical_cap]:
        if score >= lexical_min_score:
            add(bundle, pgs_ids, "lexical_or_ontology", score)
            lexical_ranked_ids.append(bundle.bundle_id)
        if score >= 0.72:
            add(bundle, pgs_ids, "near_axis", score)

    binary = sorted(
        (row for row in eligible_rows if row[0].bundle_type == "binary"),
        key=lambda item: (-len(item[1]), item[0].bundle_id),
    )
    continuous = sorted(
        (row for row in eligible_rows if row[0].bundle_type == "continuous"),
        key=lambda item: (-len(item[1]), item[0].bundle_id),
    )
    for bundle, pgs_ids, score in binary[:fallback_binary]:
        add(bundle, pgs_ids, "breadth_binary", score)
    for bundle, pgs_ids, score in continuous[:fallback_continuous]:
        add(bundle, pgs_ids, "breadth_continuous", score)

    breadth_ranked_ids = _interleave(
        [row[0].bundle_id for row in binary[:fallback_binary]],
        [row[0].bundle_id for row in continuous[:fallback_continuous]],
    )
    tail_ids = sorted(
        lane_by_bundle,
        key=lambda bid: (
            -score_by_bundle.get(bid, 0.0),
            -len(pgs_by_bundle.get(bid, [])),
            bundle_by_id[bid].bundle_type,
            bid,
        ),
    )
    coverage_ranked_ids = _position_coverage_ids(tail_ids, max_ids=coverage_front_count)
    ordered_ids = _unique_order(
        lexical_ranked_ids[:lexical_front_cap]
        + coverage_ranked_ids
        + breadth_ranked_ids[:breadth_front_count]
        + lexical_ranked_ids[lexical_front_cap:]
        + breadth_ranked_ids[breadth_front_count:]
        + tail_ids
    )[:max_bundles]

    return [
        RetrievedBundle(
            bundle=bundle_by_id[bundle_id],
            candidate_pgs_ids=pgs_by_bundle[bundle_id],
            lanes=sorted(lane_by_bundle[bundle_id]),
            position=idx + 1,
        )
        for idx, bundle_id in enumerate(ordered_ids)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build leak-free retrieved source-bundle dossiers.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_COMPACT_CATALOG_JSON)
    parser.add_argument("--targets", type=Path, default=TARGET_SELECTION_CSV)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-bundles", type=int, default=600)
    args = parser.parse_args()

    catalog = load_compact_catalog(args.catalog)
    bundles = bundles_from_catalog(catalog)
    targets = load_targets(args.targets)
    dossiers = []
    for target in targets:
        retrieved = retrieve_bundles(target=target, bundles=bundles, max_bundles=args.max_bundles)
        dossiers.append(
            {
                "target": target.to_prompt_dict(),
                "retrieved_bundles": [bundle.to_prompt_dict() for bundle in retrieved],
            }
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(dossiers, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(dossiers)} dossiers -> {args.out}")


if __name__ == "__main__":
    main()
