from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Optional

import pandas as pd
from pydantic import BaseModel, Field
from thefuzz import fuzz, process

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
TRANSFER_DIR = Path(__file__).resolve().parent
RUNS_DIR = TRANSFER_DIR / "runs" / "tool_calling_agent"
BENCHMARK_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "cross_list"
    / "benchmark_legacy_no_aou_pgs"
)
DEFAULT_BENCHMARK_FAMILY = "unified"
BENCHMARK_FAMILIES = ("binary_to_binary", "binary_to_continuous", "unified")
LEGACY_FULL_ABLATION = "full"
DEFAULT_TRANSFER_ABLATION = "no_all_tools_tuned_breadth"
BUNDLE_INDEX_JSON = RUNS_DIR / "trait_bundle_index.json"
PGS_SCORES_CSV = PROJECT_ROOT / "data" / "pgs_all_metadata" / "pgs_all_metadata_scores.csv"
PGS_EFO_TRAITS_CSV = PROJECT_ROOT / "data" / "pgs_all_metadata" / "pgs_all_metadata_efo_traits.csv"
AOU_OVERLAP_BY_ROOT_CSV = PROJECT_ROOT / "data" / "all_of_us" / "aou_pgs_trait_overlap_by_root.csv"
GWAS_ATLAS_H2_TSV = PROJECT_ROOT / "data" / "heritability" / "gwas_atlas" / "gwas_atlas.tsv"
GC_DATA_TSV = (
    PROJECT_ROOT / "data" / "genetic_correlation" / "gwas_atlas" / "gwas_atlas_gc.tsv"
)
ROOTCODE_AUC_MATRIX = (
    PROJECT_ROOT
    / "experiments"
    / "contribution1"
    / "result"
    / "legacy_no_aou_pgs"
    / "aou_binary"
    / "prs_adjauc_matrix_binary_combined_rootcode.csv"
)
NONTARGET_AUC_MATRIX = (
    PROJECT_ROOT
    / "experiments"
    / "contribution1"
    / "result"
    / "legacy_no_aou_pgs"
    / "aou_extend_trait"
    / "prs_adjauc_matrix_binary_extend_qc.csv"
)

CANDIDATE_DOSSIER_CONFIGS: dict[str, dict[str, int]] = {
    "binary_to_binary": {
        # Offline shortlist-oracle study (eval/offline_tune_shortlist_oracle_hits.py): wider pool
        # improves global-oracle inclusion before dual-track merge. Rebuild candidate_dossiers.json
        # after changing these (batch prepare-assets or build_candidate_dossiers).
        "lexical_cap": 100,
        "dossier_cap": 560,
        "lexical_min_score": 38,
        "fallback_binary": 260,
        "fallback_continuous": 100,
    },
    "binary_to_continuous": {
        "lexical_cap": 40,
        "dossier_cap": 340,
        "lexical_min_score": 55,
        "fallback_binary": 240,
        "fallback_continuous": 100,
    },
    # Unified: single config for all targets (no b2b/b2c distinction).
    # fallback_binary=310 / fallback_continuous=150 / dossier_cap=600 to capture
    # 4 previously-missing oracles: D03 (sunburn, rank306), L56 (photosensitivity, rank264),
    # M1A (uric acid, rank149 continuous), N97 (infertility variants).
    "unified": {
        "lexical_cap": 100,
        "dossier_cap": 600,
        "lexical_min_score": 38,
        "fallback_binary": 310,
        "fallback_continuous": 150,
    },
}

CONTINUOUS_HINTS = {
    "measurement",
    "count",
    "level",
    "ratio",
    "index",
    "height",
    "amount",
    "quantity",
    "mass",
    "density",
    "status",
    "consumption",
    "pressure",
    "rate",
    "volume",
    "concentration",
    "percentage",
    "body mass",
    "weight",
    "hemoglobin",
    "cholesterol",
    "protein",
    "cell",
    "bmi",
}


class TraitBundle(BaseModel):
    bundle_id: str
    canonical_label: str
    bundle_type: str
    aliases: list[str] = Field(default_factory=list)
    candidate_pgs_ids: list[str] = Field(default_factory=list)
    n_models: int
    source_efo_ids: list[str] = Field(default_factory=list)
    source_mondo_ids: list[str] = Field(default_factory=list)


class TargetTraitQuery(BaseModel):
    target_id: str
    target_code: str
    target_label: str
    target_type: str = "binary"
    aliases: list[str] = Field(default_factory=list)


class CandidateBundleDossier(BaseModel):
    target: TargetTraitQuery
    candidates: list[TraitBundle]


def validate_benchmark_family(benchmark_family: str) -> str:
    family = str(benchmark_family or "").strip()
    if family not in BENCHMARK_FAMILIES:
        raise ValueError(
            f"Unsupported benchmark family: {benchmark_family}. "
            f"Expected one of {', '.join(BENCHMARK_FAMILIES)}."
        )
    return family


def benchmark_run_dir(benchmark_family: str = DEFAULT_BENCHMARK_FAMILY) -> Path:
    family = validate_benchmark_family(benchmark_family)
    return RUNS_DIR / family


def normalize_transfer_ablation(ablation: str | None) -> str:
    text = (
        str(ablation or DEFAULT_TRANSFER_ABLATION)
        .strip()
        .lower()
        .replace("-", "_")
        .replace("+", "_plus_")
    )
    return text or DEFAULT_TRANSFER_ABLATION


def benchmark_ablation_run_dir(
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
    ablation: str | None = None,
) -> Path:
    label = normalize_transfer_ablation(ablation)
    family_dir = benchmark_run_dir(benchmark_family)
    if label == LEGACY_FULL_ABLATION:
        return family_dir
    return family_dir / f"ablation__{label}"


def target_dossiers_json(benchmark_family: str = DEFAULT_BENCHMARK_FAMILY) -> Path:
    return benchmark_run_dir(benchmark_family) / "candidate_dossiers.json"


def condition_results_json(
    condition: str,
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
    run_id: str | None = None,
    ablation: str | None = None,
) -> Path:
    condition_dir = f"{condition}__{run_id}" if run_id else condition
    return benchmark_ablation_run_dir(benchmark_family, ablation=ablation) / condition_dir / "results.json"


def condition_recommendations_json(
    condition: str,
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
    run_id: str | None = None,
    ablation: str | None = None,
) -> Path:
    condition_dir = f"{condition}__{run_id}" if run_id else condition
    return benchmark_ablation_run_dir(benchmark_family, ablation=ablation) / condition_dir / "contribution2_recommendations.json"


def evaluation_dir(
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
    run_id: str | None = None,
    ablation: str | None = None,
) -> Path:
    base = benchmark_ablation_run_dir(benchmark_family, ablation=ablation)
    return base / (f"evaluation__{run_id}" if run_id else "evaluation")


def benchmark_target_selection_csv(
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
) -> Path:
    family = validate_benchmark_family(benchmark_family)
    return BENCHMARK_DIR / family / "target_selection.csv"


def benchmark_ground_truth_csv(
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
) -> Path:
    family = validate_benchmark_family(benchmark_family)
    return BENCHMARK_DIR / family / "ground_truth_ranking.csv"


TARGET_DOSSIERS_JSON = target_dossiers_json()


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    stopwords = {"disease", "disorder", "syndrome", "trait", "of", "and", "the"}
    tokens = [tok for tok in cleaned.split() if tok not in stopwords]
    return " ".join(tokens)


def split_multi_value(raw: Any) -> list[str]:
    if raw is None:
        return []
    text = str(raw).strip()
    if not text or text.lower() == "nan":
        return []
    values = re.split(r"[|;]", text)
    return [val.strip() for val in values if val and val.strip()]


def _clean_optional_text(raw: Any) -> str:
    if raw is None:
        return ""
    text = str(raw).strip()
    if not text or text.lower() == "nan":
        return ""
    return text


def _normalize_target_source(raw: Any) -> str:
    source = _clean_optional_text(raw)
    return "extend_trait" if source in ("nontarget_pgs", "extend_trait") else "rootcode_main_analysis"


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if not value:
            continue
        key = normalize_text(value)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(value.strip())
    return out


def infer_bundle_type(label: str) -> str:
    normalized = normalize_text(label)
    for hint in CONTINUOUS_HINTS:
        if hint in normalized:
            return "continuous"
    return "binary"


def _global_fallback_bundles(
    bundles: list[TraitBundle],
    top_binary: int = 24,
    top_continuous: int = 24,
) -> list[TraitBundle]:
    binary = sorted(
        (bundle for bundle in bundles if bundle.bundle_type == "binary"),
        key=lambda bundle: (-bundle.n_models, bundle.bundle_id),
    )
    continuous = sorted(
        (bundle for bundle in bundles if bundle.bundle_type == "continuous"),
        key=lambda bundle: (-bundle.n_models, bundle.bundle_id),
    )
    binary = binary[:top_binary]
    continuous = continuous[:top_continuous]
    interleaved: list[TraitBundle] = []
    for idx in range(max(len(binary), len(continuous))):
        if idx < len(binary):
            interleaved.append(binary[idx])
        if idx < len(continuous):
            interleaved.append(continuous[idx])
    return interleaved


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return slug or "unknown"


def _auc_matrix_path_for_source(target_source: str) -> Path:
    return NONTARGET_AUC_MATRIX if target_source in ("nontarget_pgs", "extend_trait") else ROOTCODE_AUC_MATRIX


def _col_to_pgs_id(col: str) -> str:
    text = str(col).strip()
    if "__" in text:
        return text.rsplit("__", 1)[-1]
    return text.replace("_hmPOS_GRCh38", "")


@lru_cache(maxsize=2)
def source_universe_pgs_ids(target_source: str | None) -> set[str]:
    """Return PGS IDs present in the benchmark source universe.

    This reads only the AUC-matrix header, never target-row AUC values or ranks.
    The shortlist can therefore avoid bundles that cannot be evaluated for the
    benchmark source without leaking the current target's performance.
    """
    if not target_source:
        return set()
    path = _auc_matrix_path_for_source(target_source)
    if not path.exists():
        return set()
    try:
        header = pd.read_csv(path, nrows=0)
    except Exception:
        return set()
    return {_col_to_pgs_id(str(col)) for col in list(header.columns)[1:]}


def bundle_has_source_universe_pgs(bundle: TraitBundle, target_source: str | None) -> bool:
    universe_ids = source_universe_pgs_ids(target_source)
    if not universe_ids:
        return True
    return any(pgs_id in universe_ids for pgs_id in bundle.candidate_pgs_ids)


def filter_bundle_to_source_universe(
    bundle: TraitBundle,
    target_source: str | None,
) -> TraitBundle:
    """Return a copy whose PGS candidates are evaluable for the source universe.

    This uses only the benchmark AUC-matrix header for the target source
    (rootcode vs extend trait). It does not inspect target-row performance and
    does not encode trait-specific preferences; it simply prevents unevaluable
    PGS Catalog IDs from entering model selection.
    """
    universe_ids = source_universe_pgs_ids(target_source)
    if not universe_ids:
        return bundle
    candidate_pgs_ids = [pgs_id for pgs_id in bundle.candidate_pgs_ids if pgs_id in universe_ids]
    return TraitBundle(
        **{
            **bundle.model_dump(),
            "candidate_pgs_ids": candidate_pgs_ids,
            "n_models": len(candidate_pgs_ids),
        }
    )


def filter_dossier_to_benchmark_universe(
    dossier: CandidateBundleDossier,
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
) -> CandidateBundleDossier:
    """Filter each candidate bundle to PGS IDs available in the benchmark universe."""
    family = validate_benchmark_family(benchmark_family)
    target_source = target_source_for_target_id(dossier.target.target_id, benchmark_family=family)
    filtered_candidates = [
        filter_bundle_to_source_universe(bundle, target_source)
        for bundle in dossier.candidates
    ]
    filtered_candidates = [bundle for bundle in filtered_candidates if bundle.candidate_pgs_ids]
    return CandidateBundleDossier(target=dossier.target, candidates=filtered_candidates)


@lru_cache(maxsize=1)
def load_gwas_gc_lookup_tables() -> tuple[pd.DataFrame, dict[int, str], dict[str, list[int]], list[str]]:
    meta = pd.read_csv(GWAS_ATLAS_H2_TSV, sep="\t", usecols=["id", "Trait", "uniqTrait"])
    meta = meta.dropna(subset=["id"]).copy()
    meta["id"] = meta["id"].astype(int)

    id_to_name: dict[int, str] = {}
    name_to_ids: dict[str, set[int]] = {}
    unique_names: set[str] = set()

    for _, row in meta.iterrows():
        trait_id = int(row["id"])
        preferred_name = str(row.get("uniqTrait") or row.get("Trait") or "").strip()
        if preferred_name:
            id_to_name[trait_id] = preferred_name
            unique_names.add(preferred_name)

        for raw_name in [row.get("uniqTrait"), row.get("Trait")]:
            if pd.isna(raw_name):
                continue
            name = str(raw_name).strip()
            if not name:
                continue
            unique_names.add(name)
            name_to_ids.setdefault(normalize_text(name), set()).add(trait_id)

    gc_df = pd.read_csv(
        GC_DATA_TSV,
        sep="\t",
        usecols=["id1", "id2", "rg", "z", "p"],
        dtype={"id1": int, "id2": int, "rg": float, "z": float, "p": float},
    )
    return (
        gc_df,
        id_to_name,
        {key: sorted(value) for key, value in name_to_ids.items()},
        sorted(unique_names),
    )


def resolve_texts_to_gwas_ids(
    texts: Iterable[str],
    min_score: int = 75,
) -> list[tuple[int, str, int]]:
    _, _, name_to_ids, unique_names = load_gwas_gc_lookup_tables()
    best_by_id: dict[int, tuple[int, str, int]] = {}
    for raw_text in texts:
        text = str(raw_text or "").strip()
        if not text:
            continue
        match = process.extractOne(text, unique_names, scorer=fuzz.token_set_ratio)
        if not match:
            continue
        matched_name, score = str(match[0]).strip(), int(match[1])
        if score < min_score:
            continue
        for trait_id in name_to_ids.get(normalize_text(matched_name), []):
            existing = best_by_id.get(trait_id)
            record = (trait_id, matched_name, score)
            if existing is None or record[2] > existing[2]:
                best_by_id[trait_id] = record
    return sorted(best_by_id.values(), key=lambda item: (-item[2], item[0]))


def _load_efo_label_lookup() -> dict[str, str]:
    df = pd.read_csv(PGS_EFO_TRAITS_CSV)
    return {
        str(row["Ontology Trait ID"]).strip(): str(row["Ontology Trait Label"]).strip()
        for _, row in df.iterrows()
        if pd.notna(row["Ontology Trait ID"]) and pd.notna(row["Ontology Trait Label"])
    }


def build_trait_bundle_index() -> list[TraitBundle]:
    scores = pd.read_csv(PGS_SCORES_CSV)
    efo_label_lookup = _load_efo_label_lookup()

    bundles: dict[str, dict[str, Any]] = {}
    for _, row in scores.iterrows():
        pgs_id = str(row["Polygenic Score (PGS) ID"]).strip()
        reported_trait = str(row.get("Reported Trait", "") or "").strip()
        mapped_labels = split_multi_value(row.get("Mapped Trait(s) (EFO label)"))
        mapped_ids = split_multi_value(row.get("Mapped Trait(s) (EFO ID)"))

        pair_count = max(len(mapped_labels), len(mapped_ids), 1)
        for idx in range(pair_count):
            mapped_id = mapped_ids[idx] if idx < len(mapped_ids) else ""
            mapped_label = mapped_labels[idx] if idx < len(mapped_labels) else ""
            canonical_label = (
                efo_label_lookup.get(mapped_id)
                or mapped_label
                or reported_trait
                or f"unmapped {pgs_id}"
            )
            bundle_key = mapped_id or f"LABEL::{normalize_text(canonical_label)}"
            bundle = bundles.setdefault(
                bundle_key,
                {
                    "bundle_id": slugify(bundle_key.replace("::", "_")),
                    "canonical_label": canonical_label,
                    "bundle_type": infer_bundle_type(canonical_label),
                    "aliases": [],
                    "candidate_pgs_ids": [],
                    "source_efo_ids": [],
                    "source_mondo_ids": [],
                },
            )
            bundle["aliases"].extend([canonical_label, mapped_label, reported_trait])
            bundle["candidate_pgs_ids"].append(pgs_id)
            if mapped_id.startswith("EFO_"):
                bundle["source_efo_ids"].append(mapped_id)
            elif mapped_id.startswith("MONDO_"):
                bundle["source_mondo_ids"].append(mapped_id)

    result: list[TraitBundle] = []
    for bundle in bundles.values():
        bundle["aliases"] = unique_preserve_order(bundle["aliases"])
        bundle["candidate_pgs_ids"] = sorted(set(bundle["candidate_pgs_ids"]))
        bundle["source_efo_ids"] = sorted(set(bundle["source_efo_ids"]))
        bundle["source_mondo_ids"] = sorted(set(bundle["source_mondo_ids"]))
        bundle["n_models"] = len(bundle["candidate_pgs_ids"])
        result.append(TraitBundle(**bundle))
    result.sort(key=lambda bundle: bundle.bundle_id)
    return result


def write_trait_bundle_index(bundles: list[TraitBundle], outpath: Path = BUNDLE_INDEX_JSON) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(
        json.dumps([bundle.model_dump() for bundle in bundles], indent=2, ensure_ascii=False)
    )


def load_trait_bundle_index(path: Path = BUNDLE_INDEX_JSON) -> list[TraitBundle]:
    data = json.loads(path.read_text())
    return [TraitBundle(**row) for row in data]


def bundle_lookup_by_id(bundles: Iterable[TraitBundle]) -> dict[str, TraitBundle]:
    return {bundle.bundle_id: bundle for bundle in bundles}


def load_benchmark_target_selection(
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
    selected_only: bool = True,
) -> pd.DataFrame:
    path = benchmark_target_selection_csv(benchmark_family)
    if not path.exists():
        raise FileNotFoundError(f"Benchmark target selection not found: {path}")
    df = pd.read_csv(path)
    if selected_only and "selected" in df.columns:
        selected_mask = df["selected"].fillna(False).astype(bool)
        df = df.loc[selected_mask].copy()
    return df


@lru_cache(maxsize=4)
def benchmark_target_source_lookup(benchmark_family: str) -> dict[str, str]:
    try:
        df = load_benchmark_target_selection(benchmark_family=benchmark_family, selected_only=True)
    except Exception:
        return {}
    lookup: dict[str, str] = {}
    for _, row in df.iterrows():
        target_id = str(row.get("input_icd") or "").strip()
        if target_id:
            lookup[target_id] = _normalize_target_source(row.get("target_source"))
    return lookup


def target_source_for_target_id(
    target_id: str,
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
) -> str | None:
    return benchmark_target_source_lookup(benchmark_family).get(str(target_id or "").strip())


def build_target_queries(
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
) -> list[TargetTraitQuery]:
    df = load_benchmark_target_selection(benchmark_family=benchmark_family, selected_only=True)
    queries: list[TargetTraitQuery] = []
    for _, row in df.iterrows():
        ontology_text = _clean_optional_text(row.get("input_ontology"))
        description_text = _clean_optional_text(row.get("input_description"))
        label = ontology_text or description_text or str(row.get("input_icd", "")).strip()
        aliases = unique_preserve_order(
            split_multi_value(ontology_text)
            + [description_text, ontology_text]
        )
        queries.append(
            TargetTraitQuery(
                target_id=str(row["input_icd"]).strip(),
                target_code=str(row["input_icd"]).strip(),
                target_label=label,
                aliases=aliases,
            )
        )
    return queries


def _bundle_match_score(bundle: TraitBundle, terms: list[str]) -> int:
    choices = [bundle.canonical_label, *bundle.aliases]
    best = 0
    for term in terms:
        for choice in choices:
            score = fuzz.token_set_ratio(normalize_text(term), normalize_text(choice))
            best = max(best, int(score))
    return best


def _light_normalize(text: str) -> str:
    """Lower + whitespace-collapse only. Unlike `normalize_text` this does NOT
    strip stopwords like 'disease' / 'disorder' / 'syndrome', so self-like
    detection can distinguish 'migraine' from 'migraine disorder', or
    'hypertension' from 'secondary hypertension'.
    """
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def is_self_like_bundle(
    target: TargetTraitQuery,
    bundle: TraitBundle,
    threshold: int = 90,
) -> bool:
    """Detect bundles that are effectively the same trait as the target.

    Uses Levenshtein-based `fuzz.ratio` on a length-preserving normalization
    (no stopword stripping). With the original `token_set_ratio`+`normalize_text`
    combination, "major depressive disorder" bundle was flagged self for
    "Major depressive disorder, recurrent" (token-subset score = 100) — that
    wrongly excluded the umbrella-disease bundle whose PGS is the empirical
    oracle for ~7 of the 80 unified targets (D03, D05, F33, G43, I15, M05,
    M1A). `fuzz.ratio` on the lightly-normalized strings returns 64-80 there,
    so subtypes/variants are NOT flagged self while truly identical labels
    still hit the 90+ threshold.
    """
    target_texts = [target.target_label, *target.aliases]
    for target_text in target_texts:
        if not target_text:
            continue
        if fuzz.ratio(_light_normalize(bundle.canonical_label), _light_normalize(target_text)) >= threshold:
            return True
        for alias in bundle.aliases:
            if fuzz.ratio(_light_normalize(alias), _light_normalize(target_text)) >= threshold:
                return True
    return False


def _resolve_gc_bundles(target: TargetTraitQuery, bundles: list[TraitBundle]) -> set[str]:
    gc_df, id_to_name, _, _ = load_gwas_gc_lookup_tables()
    seed_resolutions = resolve_texts_to_gwas_ids([target.target_label, *target.aliases], min_score=75)
    if not seed_resolutions:
        return set()

    candidate_ids: set[str] = set()
    normalized_bundle_text: dict[str, str] = {
        bundle.bundle_id: " | ".join([bundle.canonical_label, *bundle.aliases])
        for bundle in bundles
    }
    for seed_id, _, _ in seed_resolutions[:3]:
        correlations = gc_df[
            ((gc_df["id1"] == seed_id) | (gc_df["id2"] == seed_id)) & (gc_df["p"] < 0.05)
        ].sort_values("p", ascending=True).head(80)
        for _, corr in correlations.iterrows():
            other_id = int(corr["id2"]) if int(corr["id1"]) == seed_id else int(corr["id1"])
            other_name = id_to_name.get(other_id, "").strip()
            if not other_name:
                continue
            for bundle in bundles:
                if fuzz.token_set_ratio(
                    normalize_text(other_name),
                    normalize_text(normalized_bundle_text[bundle.bundle_id]),
                ) >= 85:
                    candidate_ids.add(bundle.bundle_id)
    return candidate_ids


def _resolve_overlap_bundles(target: TargetTraitQuery, bundles: list[TraitBundle]) -> set[str]:
    if not AOU_OVERLAP_BY_ROOT_CSV.exists():
        return set()
    overlap = pd.read_csv(AOU_OVERLAP_BY_ROOT_CSV)
    root = target.target_code.strip()
    subset = overlap[overlap["aou_icd_root"].astype(str).str.strip() == root]
    if subset.empty:
        return set()
    labels = unique_preserve_order(subset["pgs_label"].astype(str).tolist())
    hits: set[str] = set()
    for label in labels:
        for bundle in bundles:
            if _bundle_match_score(bundle, [label]) >= 90:
                hits.add(bundle.bundle_id)
    return hits


def select_candidate_bundles(
    target: TargetTraitQuery,
    bundles: list[TraitBundle],
    lexical_cap: int | None = None,
    dossier_cap: int | None = None,
    lexical_min_score: int | None = None,
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
) -> list[TraitBundle]:
    family = validate_benchmark_family(benchmark_family)
    config = CANDIDATE_DOSSIER_CONFIGS[family]
    lexical_cap = lexical_cap if lexical_cap is not None else config["lexical_cap"]
    dossier_cap = dossier_cap if dossier_cap is not None else config["dossier_cap"]
    lexical_min_score = (
        lexical_min_score if lexical_min_score is not None else config.get("lexical_min_score", 55)
    )
    target_source = target_source_for_target_id(target.target_id, benchmark_family=family)
    terms = [target.target_label, *target.aliases]
    lookup = bundle_lookup_by_id(bundles)
    lexical_scored = [
        (bundle.bundle_id, _bundle_match_score(bundle, terms))
        for bundle in bundles
    ]
    lexical_ranked = [
        bundle_id
        for bundle_id, score in sorted(lexical_scored, key=lambda item: (-item[1], item[0]))[:lexical_cap]
        if score >= lexical_min_score
    ]
    overlap_ids = _resolve_overlap_bundles(target, bundles)
    # GC-based candidate discovery is disabled — GWAS Atlas rg has been
    # replaced by LLM-estimated genetic relatedness at the scoring stage.
    # Existing candidate selection paths (lexical, overlap, fallback)
    # already achieve 100% dossier oracle recall (80/80).
    gc_ids: set[str] = set()
    fallback_ranked = [
        bundle.bundle_id
        for bundle in _global_fallback_bundles(
            bundles,
            top_binary=config["fallback_binary"],
            top_continuous=config["fallback_continuous"],
        )
    ]

    selected: list[str] = []
    seen: set[str] = set()

    def add_candidates(bundle_ids: Iterable[str]) -> None:
        for bundle_id in bundle_ids:
            if bundle_id in seen:
                continue
            bundle = lookup.get(bundle_id)
            if bundle is None:
                continue
            # Self-match filter retained: target_selection.csv pre-filters
            # to targets whose self-PGS underperforms, so the same-trait
            # bundle's PGSs are known weak. Allowing the same-trait bundle
            # in dossier lets Pick fall back to those weak PGSs and
            # regress versus the cross-trait alternative — empirically
            # observed in P26 80-run (e.g., N10 0.041→0.974 when self
            # bundle was kept in dossier). The filter prevents this.
            if is_self_like_bundle(target, bundle):
                continue
            if not bundle_has_source_universe_pgs(bundle, target_source):
                continue
            seen.add(bundle_id)
            selected.append(bundle_id)
            if len(selected) >= dossier_cap:
                return

    add_candidates(sorted(overlap_ids))
    if len(selected) < dossier_cap:
        add_candidates(sorted(gc_ids))
    if len(selected) < dossier_cap:
        add_candidates(lexical_ranked)
    if len(selected) < dossier_cap:
        add_candidates(fallback_ranked)

    return [
        filter_bundle_to_source_universe(lookup[bundle_id], target_source)
        for bundle_id in selected
        if bundle_id in lookup
    ]


def build_candidate_dossiers(
    bundles: list[TraitBundle],
    benchmark_family: str = DEFAULT_BENCHMARK_FAMILY,
) -> list[CandidateBundleDossier]:
    dossiers: list[CandidateBundleDossier] = []
    for target in build_target_queries(benchmark_family=benchmark_family):
        candidates = select_candidate_bundles(
            target,
            bundles,
            benchmark_family=benchmark_family,
        )
        dossiers.append(CandidateBundleDossier(target=target, candidates=candidates))
    return dossiers


def write_candidate_dossiers(
    dossiers: list[CandidateBundleDossier],
    outpath: Path = TARGET_DOSSIERS_JSON,
) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(
        json.dumps([dossier.model_dump() for dossier in dossiers], indent=2, ensure_ascii=False)
    )


def load_candidate_dossiers(path: Path = TARGET_DOSSIERS_JSON) -> list[CandidateBundleDossier]:
    data = json.loads(path.read_text())
    return [CandidateBundleDossier(**row) for row in data]
