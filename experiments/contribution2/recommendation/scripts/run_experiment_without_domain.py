"""
Contribution2 Experiment 1: Without Domain Knowledge batch evaluation.

This runner converts the formal Contribution2 Step 1 experiment into an OpenAI
Batch API workflow so the LLM decisions can be evaluated in parallel.

Workflow:
  1. Prepare local candidate metadata and benchmark labels for all diseases.
  2. Build one Step 1 request per disease-trial pair and write JSONL.
  3. Submit the JSONL file to the OpenAI Batch API.
  4. After the batch completes, download outputs and compute the experiment metrics.

Usage:
  python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py
  python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py --mode status
  python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py --mode collect
  python experiments/contribution2/recommendation/scripts/run_experiment_without_domain.py --mode prepare --limit 3 --trials 2
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Optional

import pandas as pd
from openai import OpenAI
from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel
import tiktoken

# Ensure project root in path (contribution2/recommendation/scripts -> repo root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent

# Load .env (OPENAI_API_KEY, OPENAI_MODEL, etc.) for online calls
try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Force Contribution2 without-domain settings before importing project modules.
os.environ["PENNPRS_STEP1_DISABLE_DOMAIN_KNOWLEDGE"] = "1"
os.environ["PENNPRS_STEP1_RUN_NO_DOMAIN_ABLATION"] = "0"
os.environ["PENNPRS_CONTRIB2_STRICT_LLM_ONLY"] = "1"

eval_pgs_path = (
    PROJECT_ROOT
    / "experiments"
    / "contribution2"
    / "recommendation"
    / "runs"
    / "ground-truth__contribution1"
    / "evaluated_pgs_per_ontology.json"
)
if eval_pgs_path.exists():
    os.environ["PENNPRS_CONTRIB2_EVALUATED_PGS_JSON"] = str(eval_pgs_path)

from src.server.core.llm_config import get_config
from src.server.core.system_prompts import CO_SCIENTIST_STEP1_PROMPT
from src.server.core.tools.prs_model_tools import (
    prs_model_performance_landscape,
    prs_model_pgscatalog_search,
)
from src.server.core.pgs_catalog_client import PGSCatalogClient

CONTRIB2_DIR = Path(__file__).parent.parent.parent
UNION_CSV = CONTRIB2_DIR / "disease_selection" / "runs" / "selected_diseases_contribution2_union.csv"
RECOMMENDATION_RUNS = Path(__file__).parent.parent / "runs"
DOCS_DIR = Path(__file__).parent.parent / "docs"
WITHOUT_DOMAIN_PER_DISEASE_DOC = DOCS_DIR / "without_domain_per_disease_comparison.md"
LOCAL_CACHE_DIR = Path(__file__).parent.parent / "cache"
GROUND_TRUTH_DIR = RECOMMENDATION_RUNS / "ground-truth__contribution1"
TOP_K_JSON = GROUND_TRUTH_DIR / "top_k_pgs_per_ontology.json"
EVALUATED_JSON = GROUND_TRUTH_DIR / "evaluated_pgs_per_ontology.json"
CONTRIB1_RESULT_DIR = PROJECT_ROOT / "experiments" / "contribution1" / "result" / "aou_icd_260217"
CHILDCODE_AUC_MATRIX = CONTRIB1_RESULT_DIR / "prs_adjauc_matrix_260217_childrencode.csv"
ROOTCODE_AUC_MATRIX = CONTRIB1_RESULT_DIR / "prs_adjauc_matrix_260217_rootcode.csv"
PREPARE_CACHE_VERSION = "v4"

ACTIVE_RUN_DIR: Optional[Path] = None
ACTIVE_RUN_TAG: Optional[str] = None
RESULTS_JSON = Path()
SUMMARY_JSON = Path()
REPORT_MD = Path()

BATCH_REQUESTS_JSONL = Path()
BATCH_MANIFEST_JSON = Path()
BATCH_JOB_JSON = Path()
BATCH_OUTPUT_JSONL = Path()
BATCH_ERROR_JSONL = Path()
ARCHIVE_ARTIFACTS: list[Path] = []

VALID_PGS_ID_RE = re.compile(r"^PGS\d+$")
MAX_CHAT_COMPLETIONS_N = 8
BATCH_PRICING_PER_MILLION_USD = {
    # Official OpenAI Batch-tier prices as of 2026-03-06.
    "gpt-5.2": {
        "input": 0.875,
        "cached_input": 0.0875,
        "output": 7.0,
    },
    "gpt-5.4": {
        "input": 1.25,
        "cached_input": 0.125,
        "output": 7.5,
    },
    "gpt-5-mini": {
        "input": 0.125,
        "cached_input": 0.0125,
        "output": 1.0,
    }
}
STANDARD_PRICING_PER_MILLION_USD = {
    # Official OpenAI Standard-tier prices as of 2026-03-06.
    "gpt-5.2": {
        "input": 1.75,
        "cached_input": 0.175,
        "output": 14.0,
    },
    "gpt-5.1": {
        "input": 1.25,
        "cached_input": 0.125,
        "output": 10.0,
    },
    "gpt-5": {
        "input": 1.25,
        "cached_input": 0.125,
        "output": 10.0,
    },
    "gpt-5-mini": {
        "input": 0.25,
        "cached_input": 0.025,
        "output": 2.0,
    },
    "gpt-5-nano": {
        "input": 0.05,
        "cached_input": 0.005,
        "output": 0.4,
    },
}

STEP1_RATIONALE_FEATURE_KEYWORDS = {
    "trait_match": ["trait", "phenotype", "proxy", "family history"],
    "auc": ["auc", "auroc", "roc"],
    "r2": ["r2", "r²", "variance explained"],
    "heritability": ["heritability", "h2", "h²", "ceiling"],
    "sample_size": ["sample", "n=", "cohort", "powered"],
    "ancestry": ["ancestry", "eur", "afr", "eas", "sas", "multi-ancestry"],
    "method": ["method", "ldpred", "prs-cs", "lassosum", "genoboost", "snpnet"],
    "variants": ["variant", "snp"],
    "covariates": ["covariate", "age", "sex", "pc"],
}

FIELD_ROWS: list[tuple[str, str]] = [
    ("Selected PGS ID", "agent_input"),
    ("AoU benchmark rank", "benchmark_only"),
    ("AoU benchmark AUC", "benchmark_only"),
    ("In Target_TopK", "benchmark_only"),
    ("Selection frequency", "benchmark_only"),
    ("trait_reported", "agent_input"),
    ("trait_efo", "agent_input"),
    ("phenotyping_reported", "agent_input"),
    ("method_name", "agent_input"),
    ("performance_metrics.selected_performance_id", "agent_input"),
    ("performance_metrics.selected_validation_ancestry", "agent_input"),
    ("performance_metrics.record_count", "agent_input"),
    ("performance_metrics.auc", "agent_input"),
    ("performance_metrics.r2", "agent_input"),
    ("performance_metrics.full_model_auc", "agent_input"),
    ("performance_metrics.full_model_r2", "agent_input"),
    ("performance_metrics.incremental_auc", "agent_input"),
    ("performance_metrics.classification_metrics", "agent_input"),
    ("performance_metrics.other_metrics", "agent_input"),
    ("performance_metrics.effect_sizes", "agent_input"),
    ("validation_sample_size", "agent_input"),
    ("samples_training", "agent_input"),
    ("ancestry_distribution", "agent_input"),
    ("training_development_cohorts", "agent_input"),
    ("publication.title", "agent_input"),
    ("publication.journal", "agent_input"),
    ("date_release", "agent_input"),
    ("variants_number", "agent_input"),
    ("covariates", "agent_input"),
]


class Step1Decision(BaseModel):
    outcome: str
    best_model_id: Optional[str] = None
    confidence: str
    rationale: str


def _normalize_ontology(s: str) -> str:
    return (s or "").strip().lower()


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return slug or "unknown"


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if pd.isna(value):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _whitelist_digest(candidate_model_ids: list[str]) -> str:
    joined = "\n".join(sorted(candidate_model_ids))
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()[:12]


def _model_name() -> str:
    config = get_config("disease_workflow")
    return os.getenv("OPENAI_MODEL") or config.model


def _extract_step1_rationale_features(rationale: str) -> list[str]:
    text = (rationale or "").lower()
    features: list[str] = []
    for feature, keywords in STEP1_RATIONALE_FEATURE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            features.append(feature)
    return features


def _summarize_model_for_llm(model: Any) -> dict[str, Any]:
    publication = getattr(model, "publication", None)
    if hasattr(publication, "model_dump"):
        publication = publication.model_dump()
    return {
        "id": getattr(model, "id", None),
        "trait_reported": getattr(model, "trait_reported", None),
        "trait_efo": getattr(model, "trait_efo", None),
        "method_name": getattr(model, "method_name", None),
        "variants_number": getattr(model, "variants_number", None),
        "ancestry_distribution": getattr(model, "ancestry_distribution", None),
        "publication": publication,
        "date_release": getattr(model, "date_release", None),
        "samples_training": getattr(model, "samples_training", None),
        "performance_metrics": getattr(model, "performance_metrics", None),
        "phenotyping_reported": getattr(model, "phenotyping_reported", None),
        "covariates": getattr(model, "covariates", None),
        "training_development_cohorts": getattr(model, "training_development_cohorts", None),
        "validation_sample_size": getattr(model, "validation_sample_size", None),
    }


def _model_from_summary(summary: dict[str, Any]) -> Any:
    return SimpleNamespace(**summary)


def _candidate_cache_path(ontology: str, candidate_model_ids: list[str]) -> Path:
    return (
        LOCAL_CACHE_DIR
        / "candidate_search"
        / f"{_slugify(ontology)}__{_whitelist_digest(candidate_model_ids)}.json"
    )


def _load_cached_candidate_bundle(
    ontology: str,
    candidate_model_ids: list[str],
    refresh_cache: bool,
) -> Optional[dict[str, Any]]:
    if refresh_cache:
        return None
    path = _candidate_cache_path(ontology, candidate_model_ids)
    if not path.exists():
        return None
    payload = _load_json(path)
    if payload.get("cache_version") != PREPARE_CACHE_VERSION:
        return None
    if payload.get("ontology") != ontology:
        return None
    if list(payload.get("candidate_model_ids") or []) != list(candidate_model_ids):
        return None
    return payload


def _write_cached_candidate_bundle(
    ontology: str,
    candidate_model_ids: list[str],
    total_found: int,
    candidate_model_summaries: list[dict[str, Any]],
    baseline: Optional[dict[str, Any]],
) -> None:
    path = _candidate_cache_path(ontology, candidate_model_ids)
    _write_json(
        path,
        {
            "cache_version": PREPARE_CACHE_VERSION,
            "ontology": ontology,
            "candidate_model_ids": candidate_model_ids,
            "total_found": total_found,
            "candidate_models": candidate_model_summaries,
            "baseline": baseline,
        },
    )


def _is_valid_output(recommended_id: Optional[str], candidate_id_set: set[str]) -> bool:
    if not recommended_id or not VALID_PGS_ID_RE.match(recommended_id):
        return False
    return recommended_id in candidate_id_set


def _benchmark_rank_map(rank_order: list[str]) -> dict[str, int]:
    return {pgs_id: idx + 1 for idx, pgs_id in enumerate(rank_order or []) if pgs_id}


def _rank_label(rank: Optional[int], n_models: int) -> str:
    if rank is None or n_models <= 0:
        return "-"
    return f"{rank}/{n_models}"


def _sort_disease_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: (-row["n_models"], row["ontology"]))


def _tiered_baseline(models: list[Any]) -> Optional[dict[str, Any]]:
    """
    Tiered baseline: Tier 1 uses PGS-only AUROC; Tier 2 falls back to full-model AUROC
    when no candidate has PGS-comparable AUROC. Achieves ~100% coverage.
    """
    best_model = None
    best_score = None
    tier_used = None

    # Tier 1: PGS-only AUROC (PRS-comparable)
    for model in models:
        perf = getattr(model, "performance_metrics", {}) or {}
        auc = _safe_float(perf.get("auc"))
        if auc is None:
            continue
        if best_score is None or auc > best_score:
            best_model = model
            best_score = auc
            tier_used = "pgs_only_auroc"

    # Tier 2: full-model AUROC when Tier 1 has no coverage
    if best_model is None:
        for model in models:
            perf = getattr(model, "performance_metrics", {}) or {}
            full_auc = _safe_float(perf.get("full_model_auc"))
            if full_auc is None:
                continue
            if best_score is None or full_auc > best_score:
                best_model = model
                best_score = full_auc
                tier_used = "full_model_auroc"

    if best_model is None or best_score is None:
        return None
    return {
        "pgs_id": getattr(best_model, "id", None),
        "reported_auc": round(best_score, 4),
        "tier": tier_used,
        "trait_reported": getattr(best_model, "trait_reported", None),
        "method_name": getattr(best_model, "method_name", None),
        "validation_sample_size": getattr(best_model, "validation_sample_size", None),
    }


def _best_reported_pgs_only_auc_baseline(models: list[Any]) -> Optional[dict[str, Any]]:
    """Alias for tiered baseline (backward compatible)."""
    return _tiered_baseline(models)


def _modal_recommendation(trial_rows: list[dict[str, Any]]) -> tuple[Optional[str], int]:
    valid_ids = [
        row["recommended_pgs_id"]
        for row in trial_rows
        if row.get("valid_output") and row.get("recommended_pgs_id")
    ]
    if not valid_ids:
        return None, 0
    counts = Counter(valid_ids)
    modal_id, modal_count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    return modal_id, modal_count


def _format_percent(value: float) -> str:
    return f"{value:.2%}"


def _format_currency(value: float) -> str:
    return f"${value:.4f}"


def _archive_dir_name(model: str, trials: int, run_tag: Optional[str] = None) -> str:
    safe_model = re.sub(r"[^A-Za-z0-9._-]+", "-", (model or "unknown")).strip("-")
    base = f"without-domain-{safe_model}-t{trials}"
    safe_tag = re.sub(r"[^A-Za-z0-9._-]+", "-", (run_tag or "").strip()).strip("-")
    return f"{base}__{safe_tag}" if safe_tag else base


def _set_run_paths(trials: int, model: Optional[str] = None, run_tag: Optional[str] = None) -> Path:
    global ACTIVE_RUN_DIR, ACTIVE_RUN_TAG
    global RESULTS_JSON, SUMMARY_JSON, REPORT_MD
    global BATCH_REQUESTS_JSONL, BATCH_MANIFEST_JSON, BATCH_JOB_JSON
    global BATCH_OUTPUT_JSONL, BATCH_ERROR_JSONL, ARCHIVE_ARTIFACTS

    if trials <= 0:
        raise ValueError("--trials must be a positive integer.")

    run_model = model or _model_name()
    ACTIVE_RUN_TAG = run_tag
    ACTIVE_RUN_DIR = RECOMMENDATION_RUNS / _archive_dir_name(run_model, trials, run_tag=run_tag)
    ACTIVE_RUN_DIR.mkdir(parents=True, exist_ok=True)

    RESULTS_JSON = ACTIVE_RUN_DIR / "experiment_without_domain_results.json"
    SUMMARY_JSON = ACTIVE_RUN_DIR / "experiment_without_domain_summary.json"
    REPORT_MD = ACTIVE_RUN_DIR / "experiment_without_domain_report.md"
    BATCH_REQUESTS_JSONL = ACTIVE_RUN_DIR / "experiment_without_domain_batch_requests.jsonl"
    BATCH_MANIFEST_JSON = ACTIVE_RUN_DIR / "experiment_without_domain_batch_manifest.json"
    BATCH_JOB_JSON = ACTIVE_RUN_DIR / "experiment_without_domain_batch_job.json"
    BATCH_OUTPUT_JSONL = ACTIVE_RUN_DIR / "experiment_without_domain_batch_output.jsonl"
    BATCH_ERROR_JSONL = ACTIVE_RUN_DIR / "experiment_without_domain_batch_errors.jsonl"
    ARCHIVE_ARTIFACTS = [
        TOP_K_JSON,
        EVALUATED_JSON,
        BATCH_JOB_JSON,
        BATCH_MANIFEST_JSON,
        BATCH_OUTPUT_JSONL,
        BATCH_ERROR_JSONL,
        BATCH_REQUESTS_JSONL,
        REPORT_MD,
        RESULTS_JSON,
        SUMMARY_JSON,
    ]
    return ACTIVE_RUN_DIR


def _load_ontology_filter(
    ontologies: Optional[list[str]],
    ontologies_file: Optional[str],
) -> Optional[set[str]]:
    values: list[str] = []
    for item in ontologies or []:
        if item and item.strip():
            values.append(item.strip())
    if ontologies_file:
        file_path = Path(ontologies_file)
        if not file_path.exists():
            raise FileNotFoundError(f"Ontology filter file not found: {file_path}")
        for line in file_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                values.append(line)
    normalized = {_normalize_ontology(item) for item in values if item}
    return normalized or None


def _choice_chunks(total_trials: int, max_n: int = MAX_CHAT_COMPLETIONS_N) -> list[int]:
    chunks: list[int] = []
    remaining = total_trials
    while remaining > 0:
        size = min(max_n, remaining)
        chunks.append(size)
        remaining -= size
    return chunks


def _require_ground_truth(
    union_df: pd.DataFrame,
    evaluated_data: dict[str, list[str]],
    top_k_data: dict[str, list[str]],
) -> Optional[str]:
    missing: list[str] = []
    for _, row in union_df.iterrows():
        ontology = str(row.get("Ontology", "")).strip()
        key = _normalize_ontology(ontology)
        if key not in evaluated_data:
            missing.append(f"{ontology}: missing evaluated_pgs_per_ontology entry")
        elif not evaluated_data.get(key):
            missing.append(f"{ontology}: empty evaluated_pgs_per_ontology entry")
        if key not in top_k_data:
            missing.append(f"{ontology}: missing top_k_pgs_per_ontology entry")
        elif not top_k_data.get(key):
            missing.append(f"{ontology}: empty top_k_pgs_per_ontology entry")
    if missing:
        return "\n".join(missing)
    return None


def _step1_context(
    ontology: str,
    candidate_models: list[Any],
    total_found: int,
    landscape: dict[str, Any],
) -> dict[str, Any]:
    return {
        "target_trait": ontology,
        "direct_models": {
            "query_trait": ontology,
            "total_found": total_found,
            "after_filter": len(candidate_models),
            "models": [_summarize_model_for_llm(model) for model in candidate_models],
        },
        "performance_landscape": landscape,
        "domain_knowledge": {
            "query": "",
            "snippets": [],
            "source_type": "disabled_by_ablation",
        },
        "todo_recitation_path": "N/A",
        "todo_recitation": "",
    }


def _step1_messages(context_json: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": CO_SCIENTIST_STEP1_PROMPT},
        {
            "role": "user",
            "content": (
                "Perform direct-match assessment only. Use the context JSON below to select the "
                "best supported direct-match candidate and return exactly one JSON object with "
                "fields: outcome, best_model_id, confidence, rationale.\n\n"
                f"Context:\n{context_json}"
            ),
        },
    ]


def _step1_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "step1_decision",
            "strict": True,
            "schema": to_strict_json_schema(Step1Decision),
        },
    }


def _build_batch_request(custom_id: str, context_json: str, n_choices: int) -> dict[str, Any]:
    config = get_config("disease_workflow")
    body: dict[str, Any] = {
        "model": _model_name(),
        "n": n_choices,
        "messages": _step1_messages(context_json),
        "response_format": _step1_response_format(),
    }
    if config.temperature is not None:
        body["temperature"] = config.temperature
    if config.max_tokens:
        body["max_tokens"] = config.max_tokens
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": body,
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record))
            handle.write("\n")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def _pricing_for_model(
    model_name: str,
    pricing_table: dict[str, dict[str, float]],
) -> tuple[Optional[str], Optional[dict[str, float]]]:
    lower = str(model_name or "").lower()
    for prefix, pricing in pricing_table.items():
        if lower.startswith(prefix):
            return prefix, pricing
    return None, None


def _estimate_batch_cost(batch_payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    usage = (batch_payload or {}).get("usage") or {}
    model_name = str((batch_payload or {}).get("model") or "")
    pricing_key, pricing = _pricing_for_model(model_name, BATCH_PRICING_PER_MILLION_USD)
    if pricing is None:
        return None

    input_tokens = _safe_int(usage.get("input_tokens"))
    input_details = usage.get("input_tokens_details") or {}
    cached_tokens = _safe_int(input_details.get("cached_tokens"))
    uncached_input_tokens = max(input_tokens - cached_tokens, 0)
    output_tokens = _safe_int(usage.get("output_tokens"))

    uncached_input_cost = uncached_input_tokens / 1_000_000 * pricing["input"]
    cached_input_cost = cached_tokens / 1_000_000 * pricing["cached_input"]
    output_cost = output_tokens / 1_000_000 * pricing["output"]
    total_cost = uncached_input_cost + cached_input_cost + output_cost

    return {
        "model_pricing_key": pricing_key or model_name,
        "token_usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached_tokens,
            "uncached_input_tokens": uncached_input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": _safe_int(usage.get("total_tokens")),
        },
        "pricing_per_million_tokens_usd": {
            "input": pricing["input"],
            "cached_input": pricing["cached_input"],
            "output": pricing["output"],
        },
        "method": "exact_batch_usage_times_official_batch_tier_prices",
        "estimated_cost_breakdown_usd": {
            "uncached_input": round(uncached_input_cost, 4),
            "cached_input": round(cached_input_cost, 4),
            "output": round(output_cost, 4),
        },
        "estimated_total_cost_usd": round(total_cost, 4),
    }


def _estimate_request_body_tokens(request_body: dict[str, Any], encoding: tiktoken.Encoding) -> int:
    payload = json.dumps(
        request_body,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return len(encoding.encode(payload))


def _estimate_trial_result_output_tokens(row: dict[str, Any], encoding: tiktoken.Encoding) -> int:
    decision = {
        "outcome": row.get("recommendation_type"),
        "best_model_id": row.get("recommended_pgs_id"),
        "confidence": row.get("recommendation_confidence"),
        "rationale": row.get("rationale"),
    }
    payload = json.dumps(
        decision,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return len(encoding.encode(payload))


def _estimate_quick_eval_cost_from_artifacts(
    *,
    manifest: dict[str, Any],
    trial_results: list[dict[str, Any]],
    model_name: str,
    calibration_run_dir: Optional[Path] = None,
) -> Optional[dict[str, Any]]:
    pricing_key, pricing = _pricing_for_model(model_name, STANDARD_PRICING_PER_MILLION_USD)
    if pricing is None:
        return None

    encoding = tiktoken.get_encoding("o200k_base")
    raw_input_tokens = sum(
        _estimate_request_body_tokens(request["request"]["body"], encoding)
        for request in manifest.get("requests", [])
    )
    raw_output_tokens = sum(
        _estimate_trial_result_output_tokens(row, encoding)
        for row in trial_results
    )

    input_ratio = 1.0
    output_ratio = 1.0
    cached_input_share = 0.0
    calibration_source = None

    if calibration_run_dir:
        job_path = calibration_run_dir / "experiment_without_domain_batch_job.json"
        manifest_path = calibration_run_dir / "experiment_without_domain_batch_manifest.json"
        results_path = calibration_run_dir / "experiment_without_domain_results.json"
        if job_path.exists() and manifest_path.exists() and results_path.exists():
            batch_payload = (_load_json(job_path) or {}).get("batch") or {}
            usage = batch_payload.get("usage") or {}
            exact_input_tokens = _safe_int(usage.get("input_tokens"))
            exact_output_tokens = _safe_int(usage.get("output_tokens"))
            cached_tokens = _safe_int((usage.get("input_tokens_details") or {}).get("cached_tokens"))

            reference_manifest = _load_json(manifest_path)
            reference_results = _load_json(results_path)
            reference_raw_input_tokens = sum(
                _estimate_request_body_tokens(request["request"]["body"], encoding)
                for request in reference_manifest.get("requests", [])
            )
            reference_raw_output_tokens = sum(
                _estimate_trial_result_output_tokens(row, encoding)
                for row in reference_results
            )

            if reference_raw_input_tokens > 0 and exact_input_tokens > 0:
                input_ratio = exact_input_tokens / reference_raw_input_tokens
            if reference_raw_output_tokens > 0 and exact_output_tokens > 0:
                output_ratio = exact_output_tokens / reference_raw_output_tokens
            if exact_input_tokens > 0:
                cached_input_share = cached_tokens / exact_input_tokens
            calibration_source = str(calibration_run_dir)

    input_tokens = round(raw_input_tokens * input_ratio)
    cached_input_tokens = round(input_tokens * cached_input_share)
    uncached_input_tokens = max(input_tokens - cached_input_tokens, 0)
    output_tokens = round(raw_output_tokens * output_ratio)

    uncached_input_cost = uncached_input_tokens / 1_000_000 * pricing["input"]
    cached_input_cost = cached_input_tokens / 1_000_000 * pricing["cached_input"]
    output_cost = output_tokens / 1_000_000 * pricing["output"]
    total_cost = uncached_input_cost + cached_input_cost + output_cost

    method = "estimated_quick_eval_tokens_from_request_response_content"
    if calibration_source:
        method += "_with_without_domain_batch_calibration"

    return {
        "model_pricing_key": pricing_key or model_name,
        "token_usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached_input_tokens,
            "uncached_input_tokens": uncached_input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        },
        "pricing_per_million_tokens_usd": {
            "input": pricing["input"],
            "cached_input": pricing["cached_input"],
            "output": pricing["output"],
        },
        "method": method,
        "calibration_source_run_dir": calibration_source,
        "estimated_cost_breakdown_usd": {
            "uncached_input": round(uncached_input_cost, 4),
            "cached_input": round(cached_input_cost, 4),
            "output": round(output_cost, 4),
        },
        "estimated_total_cost_usd": round(total_cost, 4),
        "estimation_notes": {
            "raw_input_tokens_from_tokenized_requests": raw_input_tokens,
            "raw_output_tokens_from_reconstructed_decisions": raw_output_tokens,
            "input_calibration_ratio": round(input_ratio, 6),
            "output_calibration_ratio": round(output_ratio, 6),
            "cached_input_share": round(cached_input_share, 6),
        },
    }


def _archive_current_outputs(summary: Optional[dict[str, Any]] = None) -> Path:
    if summary is not None:
        model = str(summary.get("model") or _model_name() or "unknown")
        trials = _safe_int(summary.get("trials_per_ontology"), default=10) or 10
        archive_dir = _set_run_paths(
            trials=trials,
            model=model,
            run_tag=str(summary.get("run_tag") or ACTIVE_RUN_TAG or "").strip() or None,
        )
    elif ACTIVE_RUN_DIR is not None:
        archive_dir = ACTIVE_RUN_DIR
    else:
        raise RuntimeError("Active run directory is not configured.")

    archive_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run directory: {archive_dir}")
    return archive_dir


def _prepare_manifest(
    limit: Optional[int],
    trials: int,
    refresh_cache: bool = False,
    ontology_filter: Optional[set[str]] = None,
) -> dict[str, Any]:
    if trials <= 0:
        raise ValueError("--trials must be a positive integer.")
    if not UNION_CSV.exists():
        raise FileNotFoundError(f"Union CSV not found: {UNION_CSV}")
    if not TOP_K_JSON.exists():
        raise FileNotFoundError(f"Top-K JSON not found: {TOP_K_JSON}")
    if not EVALUATED_JSON.exists():
        raise FileNotFoundError(f"Evaluated PGS JSON not found: {EVALUATED_JSON}")

    union_df = pd.read_csv(UNION_CSV)
    top_k_data = _load_json(TOP_K_JSON)
    evaluated_data = _load_json(EVALUATED_JSON)
    missing_ground_truth = _require_ground_truth(union_df, evaluated_data, top_k_data)
    if missing_ground_truth:
        raise RuntimeError(f"Contribution2 ground truth is incomplete:\n{missing_ground_truth}")

    rows = list(union_df.iterrows())
    if ontology_filter:
        rows = [
            row for row in rows
            if _normalize_ontology(str(row[1].get("Ontology", "")).strip()) in ontology_filter
        ]
    if limit:
        rows = rows[:limit]

    pgs_client = PGSCatalogClient()
    print("Building global performance landscape...")
    landscape = prs_model_performance_landscape(pgs_client, []).model_dump()
    print("Global performance landscape ready.")

    requests: list[dict[str, Any]] = []
    disease_metadata: list[dict[str, Any]] = []

    for index, (_, row) in enumerate(rows, start=1):
        ontology = str(row.get("Ontology", "")).strip()
        key = _normalize_ontology(ontology)
        n_models = _safe_int(row.get("N Models"))
        target_topk = _safe_int(row.get("Target_TopK"), default=1) or 1
        target_ranked_ids = list(top_k_data[key])
        target_topk_ids = target_ranked_ids[:target_topk]
        candidate_model_ids = list(evaluated_data[key])
        candidate_id_set = set(candidate_model_ids)

        print(f"[{index}/{len(rows)}] preparing {ontology} (Target_TopK={target_topk}, trials={trials})")
        cached_bundle = _load_cached_candidate_bundle(
            ontology=ontology,
            candidate_model_ids=candidate_model_ids,
            refresh_cache=refresh_cache,
        )
        if cached_bundle:
            total_found = _safe_int(cached_bundle.get("total_found"))
            candidate_model_summaries = list(cached_bundle.get("candidate_models") or [])
            candidate_models = [_model_from_summary(summary) for summary in candidate_model_summaries]
            baseline = cached_bundle.get("baseline")
            print(f"  using local cache ({len(candidate_models)} models)")
        else:
            candidate_result = prs_model_pgscatalog_search(
                pgs_client,
                ontology,
                evaluated_pgs_whitelist=candidate_id_set,
            )
            candidate_models = list(candidate_result.models)
            total_found = candidate_result.total_found
            candidate_model_summaries = [_summarize_model_for_llm(model) for model in candidate_models]
            baseline = _best_reported_pgs_only_auc_baseline(candidate_models)
            _write_cached_candidate_bundle(
                ontology=ontology,
                candidate_model_ids=candidate_model_ids,
                total_found=total_found,
                candidate_model_summaries=candidate_model_summaries,
                baseline=baseline,
            )
        context = _step1_context(
            ontology=ontology,
            candidate_models=candidate_models,
            total_found=total_found,
            landscape=landscape,
        )
        context_json = json.dumps(context, separators=(",", ":"), ensure_ascii=False)
        slug = _slugify(ontology)

        disease_metadata.append({
            "ontology": ontology,
            "ontology_key": key,
            "ontology_slug": slug,
            "n_models": n_models,
            "target_topk": target_topk,
            "benchmark_ranked_ids": target_ranked_ids,
            "target_topk_ids": target_topk_ids,
            "candidate_model_ids": candidate_model_ids,
            "candidate_models_visible_to_llm": candidate_model_summaries,
            "baseline": baseline,
            "total_found": total_found,
        })

        trial_start = 1
        for chunk_index, chunk_size in enumerate(_choice_chunks(trials), start=1):
            custom_id = f"{slug}__chunk_{chunk_index:02d}"
            requests.append({
                "custom_id": custom_id,
                "ontology": ontology,
                "trial_start": trial_start,
                "trials": chunk_size,
                "target_topk": target_topk,
                "target_topk_ids": target_topk_ids,
                "candidate_model_ids": candidate_model_ids,
                "request": _build_batch_request(
                    custom_id=custom_id,
                    context_json=context_json,
                    n_choices=chunk_size,
                ),
            })
            trial_start += chunk_size

    manifest = {
        "experiment": "without_domain_batch_formal",
        "model": _model_name(),
        "trials_per_ontology": trials,
        "total_ontologies": len(disease_metadata),
        "total_requests": len(requests),
        "run_tag": ACTIVE_RUN_TAG,
        "ontology_filter": sorted(ontology_filter) if ontology_filter else None,
        "disease_metadata": disease_metadata,
        "requests": requests,
    }
    return manifest


def _prepare(
    limit: Optional[int],
    trials: int,
    refresh_cache: bool = False,
    ontology_filter: Optional[set[str]] = None,
) -> dict[str, Any]:
    manifest = _prepare_manifest(
        limit=limit,
        trials=trials,
        refresh_cache=refresh_cache,
        ontology_filter=ontology_filter,
    )
    batch_requests = [row["request"] for row in manifest["requests"]]
    _write_jsonl(BATCH_REQUESTS_JSONL, batch_requests)
    _write_json(BATCH_MANIFEST_JSON, manifest)
    print(f"Wrote batch requests: {BATCH_REQUESTS_JSONL}")
    print(f"Wrote batch manifest: {BATCH_MANIFEST_JSON}")
    print(f"Prepared {manifest['total_requests']} Step 1 requests")
    return manifest


def _submit_batch() -> dict[str, Any]:
    if not BATCH_REQUESTS_JSONL.exists():
        raise FileNotFoundError(f"Batch requests not found: {BATCH_REQUESTS_JSONL}")
    if not BATCH_MANIFEST_JSON.exists():
        raise FileNotFoundError(f"Batch manifest not found: {BATCH_MANIFEST_JSON}")

    client = _client()
    with BATCH_REQUESTS_JSONL.open("rb") as handle:
        uploaded = client.files.create(file=handle, purpose="batch")

    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "experiment": "contribution2_without_domain",
            "manifest_file": BATCH_MANIFEST_JSON.name,
        },
    )
    job = {
        "batch_id": batch.id,
        "input_file_id": uploaded.id,
        "request_file": str(BATCH_REQUESTS_JSONL),
        "manifest_file": str(BATCH_MANIFEST_JSON),
        "status": batch.status,
        "batch": batch.model_dump(),
    }
    _write_json(BATCH_JOB_JSON, job)
    print(f"Uploaded batch input file: {uploaded.id}")
    print(f"Created batch job: {batch.id}")
    print(f"Status: {batch.status}")
    print(f"Saved job metadata: {BATCH_JOB_JSON}")
    return job


def _quick_eval() -> dict[str, Any]:
    if not BATCH_MANIFEST_JSON.exists():
        raise FileNotFoundError(
            f"Batch manifest not found: {BATCH_MANIFEST_JSON}. Run with --mode prepare first."
        )

    manifest = _load_json(BATCH_MANIFEST_JSON)
    client = _client()
    parsed_outputs: dict[str, dict[str, Any]] = {}
    error_map: dict[str, str] = {}

    for index, request in enumerate(manifest["requests"], start=1):
        custom_id = request["custom_id"]
        body = request["request"]["body"]
        ontology = request["ontology"]
        print(f"[quick-eval {index}/{len(manifest['requests'])}] {ontology}")
        try:
            response = client.chat.completions.create(**body)
            decisions: list[dict[str, Any]] = []
            for choice in response.choices:
                message = choice.message or {}
                content = _extract_message_content(getattr(message, "content", None))
                decision = Step1Decision.model_validate_json(content)
                decisions.append(decision.model_dump())
            parsed_outputs[custom_id] = {
                "custom_id": custom_id,
                "decisions": decisions,
                "error": None,
            }
        except Exception as exc:
            error_map[custom_id] = f"Quick eval failed: {type(exc).__name__}: {exc}"

    trial_results, summary = _build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )
    summary["execution_mode"] = "quick_eval_chat_completions"

    _write_json(RESULTS_JSON, trial_results)
    _write_json(SUMMARY_JSON, summary)
    _write_report(summary)
    per_disease_doc = _write_without_domain_per_disease_doc(summary)
    archive_dir = _archive_current_outputs(summary=summary)

    print(f"Results: {RESULTS_JSON}")
    print(f"Summary: {SUMMARY_JSON}")
    print(f"Report:  {REPORT_MD}")
    print(f"Per-disease doc: {per_disease_doc}")
    print(f"Archive: {archive_dir}")
    return summary


def _load_job(batch_id: Optional[str] = None) -> dict[str, Any]:
    if batch_id:
        return {"batch_id": batch_id}
    if not BATCH_JOB_JSON.exists():
        raise FileNotFoundError(
            f"Batch job file not found: {BATCH_JOB_JSON}. Run with --mode prepare-submit first."
        )
    return _load_json(BATCH_JOB_JSON)


def _status(batch_id: Optional[str]) -> dict[str, Any]:
    job = _load_job(batch_id=batch_id)
    client = _client()
    batch = client.batches.retrieve(job["batch_id"])
    payload = {
        "batch_id": batch.id,
        "status": batch.status,
        "input_file_id": batch.input_file_id,
        "output_file_id": batch.output_file_id,
        "error_file_id": batch.error_file_id,
        "request_counts": batch.request_counts.model_dump() if batch.request_counts else None,
        "batch": batch.model_dump(),
    }
    _write_json(BATCH_JOB_JSON, payload)
    print(json.dumps(payload, indent=2))
    return payload


def _extract_message_content(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif isinstance(item.get("output_text"), str):
                    parts.append(item["output_text"])
            elif item is not None:
                parts.append(str(item))
        return "".join(parts).strip()
    if content is None:
        return ""
    return str(content).strip()


def _parse_batch_output_line(record: dict[str, Any]) -> dict[str, Any]:
    custom_id = record.get("custom_id")
    response = record.get("response") or {}
    status_code = response.get("status_code")
    if status_code != 200:
        body = response.get("body") or {}
        error_payload = body.get("error") or record.get("error") or body
        return {
            "custom_id": custom_id,
            "error": f"HTTP {status_code}: {json.dumps(error_payload, ensure_ascii=False)}",
        }

    body = response.get("body") or {}
    try:
        decisions: list[dict[str, Any]] = []
        for choice in (body.get("choices") or []):
            message = (choice or {}).get("message") or {}
            content = _extract_message_content(message.get("content"))
            decision = Step1Decision.model_validate_json(content)
            decisions.append(decision.model_dump())
        if not decisions:
            raise ValueError("No choices returned in batch response")
        return {
            "custom_id": custom_id,
            "decisions": decisions,
            "error": None,
        }
    except Exception as exc:
        return {
            "custom_id": custom_id,
            "error": f"Failed to parse batch response: {type(exc).__name__}: {exc}",
        }


def _parse_error_file(raw_error_jsonl: str) -> dict[str, str]:
    errors: dict[str, str] = {}
    for line in raw_error_jsonl.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        custom_id = record.get("custom_id")
        if not custom_id:
            continue
        response = record.get("response") or {}
        body = response.get("body") or {}
        err = record.get("error") or body.get("error") or body or record
        errors[custom_id] = json.dumps(err, ensure_ascii=False)
    return errors


def _build_summary_and_results(
    manifest: dict[str, Any],
    parsed_outputs: dict[str, dict[str, Any]],
    error_map: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    disease_index = {row["ontology"]: row for row in manifest["disease_metadata"]}
    top_k_data = _load_json(TOP_K_JSON)
    trial_results: list[dict[str, Any]] = []

    for request in manifest["requests"]:
        custom_id = request["custom_id"]
        ontology = request["ontology"]
        disease_info = disease_index[ontology]
        parsed = parsed_outputs.get(custom_id)
        trial_start = request["trial_start"]

        if not parsed:
            error_text = error_map.get(custom_id, "Missing batch output for request")
            for trial in range(trial_start, trial_start + request["trials"]):
                trial_results.append({
                    "ontology": ontology,
                    "trial": trial,
                    "n_models": disease_info["n_models"],
                    "target_topk": request["target_topk"],
                    "target_topk_ids": request["target_topk_ids"],
                    "candidate_model_ids": request["candidate_model_ids"],
                    "recommended_pgs_id": None,
                    "recommendation_type": None,
                    "recommendation_confidence": None,
                    "valid_output": False,
                    "in_target_topk": False,
                    "rationale": None,
                    "rationale_features": [],
                    "error": error_text,
                })
            continue

        if parsed.get("error"):
            for trial in range(trial_start, trial_start + request["trials"]):
                trial_results.append({
                    "ontology": ontology,
                    "trial": trial,
                    "n_models": disease_info["n_models"],
                    "target_topk": request["target_topk"],
                    "target_topk_ids": request["target_topk_ids"],
                    "candidate_model_ids": request["candidate_model_ids"],
                    "recommended_pgs_id": None,
                    "recommendation_type": None,
                    "recommendation_confidence": None,
                    "valid_output": False,
                    "in_target_topk": False,
                    "rationale": None,
                    "rationale_features": [],
                    "error": parsed["error"],
                })
            continue

        decisions = parsed.get("decisions") or []
        candidate_id_set = set(request["candidate_model_ids"])
        if len(decisions) != request["trials"]:
            trial_error = (
                f"Expected {request['trials']} choices from batch response, "
                f"got {len(decisions)}"
            )
            for trial in range(trial_start, trial_start + request["trials"]):
                trial_results.append({
                    "ontology": ontology,
                    "trial": trial,
                    "n_models": disease_info["n_models"],
                    "target_topk": request["target_topk"],
                    "target_topk_ids": request["target_topk_ids"],
                    "candidate_model_ids": request["candidate_model_ids"],
                    "recommended_pgs_id": None,
                    "recommendation_type": None,
                    "recommendation_confidence": None,
                    "valid_output": False,
                    "in_target_topk": False,
                    "rationale": None,
                    "rationale_features": [],
                    "error": trial_error,
                })
            continue

        for offset, decision in enumerate(decisions):
            trial = trial_start + offset
            recommended_id = decision.get("best_model_id")
            valid_output = _is_valid_output(recommended_id, candidate_id_set)
            in_target = bool(valid_output and recommended_id in set(request["target_topk_ids"]))
            rationale = decision.get("rationale")
            trial_results.append({
                "ontology": ontology,
                "trial": trial,
                "n_models": disease_info["n_models"],
                "target_topk": request["target_topk"],
                "target_topk_ids": request["target_topk_ids"],
                "candidate_model_ids": request["candidate_model_ids"],
                "recommended_pgs_id": recommended_id,
                "recommendation_type": decision.get("outcome"),
                "recommendation_confidence": decision.get("confidence"),
                "valid_output": valid_output,
                "in_target_topk": in_target,
                "rationale": rationale,
                "rationale_features": _extract_step1_rationale_features(rationale or ""),
                "error": None,
            })

    per_disease: list[dict[str, Any]] = []
    for disease in manifest["disease_metadata"]:
        ontology = disease["ontology"]
        disease_trials = [row for row in trial_results if row["ontology"] == ontology]
        disease_trials.sort(key=lambda row: row["trial"])
        ontology_key = disease.get("ontology_key") or _normalize_ontology(ontology)
        benchmark_ranked_ids = list(disease.get("benchmark_ranked_ids") or top_k_data.get(ontology_key) or [])
        rank_map = _benchmark_rank_map(benchmark_ranked_ids)
        hit_count = sum(1 for row in disease_trials if row["in_target_topk"])
        valid_count = sum(1 for row in disease_trials if row["valid_output"])
        error_count = sum(1 for row in disease_trials if row["error"])
        trial_count = manifest["trials_per_ontology"]
        hit_rate = hit_count / trial_count
        valid_rate = valid_count / trial_count
        modal_id, modal_count = _modal_recommendation(disease_trials)
        modal_in_target = bool(modal_id and modal_id in set(disease["target_topk_ids"]))
        modal_rank = rank_map.get(modal_id)
        feature_counter = Counter(
            feature
            for trial in disease_trials
            for feature in trial.get("rationale_features", [])
        )
        # Recompute baseline using tiered logic (PGS-only AUC, then full-model AUC fallback)
        candidate_summaries = disease.get("candidate_models_visible_to_llm") or []
        if candidate_summaries:
            candidate_models = [_model_from_summary(s) for s in candidate_summaries]
            baseline = _tiered_baseline(candidate_models)
        else:
            baseline = disease.get("baseline")
        baseline_hit = bool(baseline and baseline.get("pgs_id") in set(disease["target_topk_ids"]))
        baseline_with_rank = None
        if baseline:
            baseline_with_rank = dict(baseline)
            baseline_rank = rank_map.get(baseline.get("pgs_id"))
            baseline_with_rank["rank"] = baseline_rank
            baseline_with_rank["rank_label"] = _rank_label(baseline_rank, disease["n_models"])

        trial_recommendations_detailed: list[dict[str, Any]] = []
        recommendation_counter: Counter[str] = Counter()
        for trial_row in disease_trials:
            recommended_id = trial_row.get("recommended_pgs_id")
            recommended_rank = rank_map.get(recommended_id)
            recommended_rank_label = _rank_label(recommended_rank, disease["n_models"])
            trial_row["recommended_rank"] = recommended_rank
            trial_row["recommended_rank_label"] = recommended_rank_label
            trial_recommendations_detailed.append({
                "trial": trial_row["trial"],
                "pgs_id": recommended_id,
                "rank": recommended_rank,
                "rank_label": recommended_rank_label,
                "in_target_topk": trial_row["in_target_topk"],
            })
            if recommended_id:
                recommendation_counter[recommended_id] += 1

        recommended_model_counts = [
            {
                "pgs_id": pgs_id,
                "count": count,
                "rank": rank_map.get(pgs_id),
                "rank_label": _rank_label(rank_map.get(pgs_id), disease["n_models"]),
            }
            for pgs_id, count in sorted(
                recommendation_counter.items(),
                key=lambda item: (-item[1], rank_map.get(item[0], 10**9), item[0]),
            )
        ]

        per_disease.append({
            "ontology": ontology,
            "n_models": disease["n_models"],
            "target_topk": disease["target_topk"],
            "benchmark_ranked_ids": benchmark_ranked_ids,
            "target_topk_ids": disease["target_topk_ids"],
            "candidate_model_ids": disease["candidate_model_ids"],
            "candidate_models_visible_to_llm": disease["candidate_models_visible_to_llm"],
            "trial_hits": hit_count,
            "trial_hit_rate": round(hit_rate, 4),
            "valid_outputs": valid_count,
            "valid_output_rate": round(valid_rate, 4),
            "errors": error_count,
            "modal_recommendation": modal_id,
            "modal_recommendation_count": modal_count,
            "modal_recommendation_rank": modal_rank,
            "modal_recommendation_rank_label": _rank_label(modal_rank, disease["n_models"]),
            "modal_recommendation_in_target_topk": modal_in_target,
            "trial_recommendations": [row["recommended_pgs_id"] for row in disease_trials],
            "trial_recommendations_detailed": trial_recommendations_detailed,
            "recommended_model_counts": recommended_model_counts,
            "feature_mentions": dict(sorted(feature_counter.items())),
            "baseline": baseline_with_rank,
            "baseline_in_target_topk": baseline_hit,
        })

    total_ontologies = len(per_disease)
    total_trials = len(trial_results)
    trial_hits = sum(1 for row in trial_results if row["in_target_topk"])
    valid_outputs = sum(1 for row in trial_results if row["valid_output"])
    trial_hit_rate = trial_hits / total_trials if total_trials else 0.0
    valid_output_rate = valid_outputs / total_trials if total_trials else 0.0
    majority_vote_hits = sum(1 for row in per_disease if row["modal_recommendation_in_target_topk"])
    majority_vote_accuracy = majority_vote_hits / total_ontologies if total_ontologies else 0.0
    baseline_hits = sum(1 for row in per_disease if row["baseline_in_target_topk"])
    baseline_available = sum(1 for row in per_disease if row.get("baseline"))
    baseline_accuracy = baseline_hits / total_ontologies if total_ontologies else 0.0

    summary = {
        "experiment": "without_domain_batch_formal",
        "domain_knowledge": False,
        "strict_llm_only": True,
        "cross_disease_enabled": False,
        "batch_mode": True,
        "run_tag": ACTIVE_RUN_TAG,
        "model": manifest["model"],
        "total_ontologies": total_ontologies,
        "trials_per_ontology": manifest["trials_per_ontology"],
        "majority_vote_hits": majority_vote_hits,
        "majority_vote_accuracy": round(majority_vote_accuracy, 4),
        "baseline": {
            "name": "tiered_baseline_pgs_only_auc_then_full_model_auroc",
            "available": baseline_available,
            "coverage": round(baseline_available / total_ontologies, 4) if total_ontologies else 0.0,
            "hits": baseline_hits,
            "accuracy": round(baseline_accuracy, 4),
        },
        "diagnostics": {
            "total_trials": total_trials,
            "trial_hits": trial_hits,
            "trial_hit_rate": round(trial_hit_rate, 4),
            "valid_outputs": valid_outputs,
            "valid_output_rate": round(valid_output_rate, 4),
        },
        "per_disease": per_disease,
    }
    return trial_results, summary


def _normalize_ontology_key(text: str) -> str:
    return _normalize_ontology(text)


def _load_aou_auc_lookup() -> dict[str, dict[str, float]]:
    union_df = pd.read_csv(UNION_CSV)
    child_matrix = pd.read_csv(CHILDCODE_AUC_MATRIX)
    root_matrix = pd.read_csv(ROOTCODE_AUC_MATRIX)

    lookup: dict[str, dict[str, float]] = {}
    child_row_map = child_matrix.set_index("trait")
    root_row_map = root_matrix.set_index("trait")

    for _, row in union_df.iterrows():
        ontology = str(row.get("Ontology", "")).strip()
        icd = str(row.get("ICD", "")).strip()
        source = str(row.get("Source", "")).strip().lower()
        if not ontology or not icd:
            continue

        matrix = child_row_map if source in {"childrencode", "both"} else root_row_map
        if icd not in matrix.index:
            continue

        auc_row = matrix.loc[icd]
        if isinstance(auc_row, pd.DataFrame):
            auc_row = auc_row.iloc[0]

        per_model: dict[str, float] = {}
        for column, value in auc_row.items():
            if column == "trait" or pd.isna(value):
                continue
            pgs_id = str(column).replace("_hmPOS_GRCh38", "")
            try:
                per_model[pgs_id] = float(value)
            except (TypeError, ValueError):
                continue
        lookup[_normalize_ontology_key(ontology)] = per_model

    return lookup


def _model_map(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(model.get("id")): model
        for model in (row.get("candidate_models_visible_to_llm") or [])
        if model.get("id")
    }


def _get_nested_field(model: Optional[dict[str, Any]], field: str) -> Any:
    if not model:
        return None
    if field == "Selected PGS ID":
        return model.get("id")
    if "." not in field:
        return model.get(field)
    value: Any = model
    for part in field.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _collapse_whitespace(text: str) -> str:
    return " ".join((text or "").split())


def _format_doc_value(value: Any, field: str) -> str:
    if value is None or value == "":
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        if not value:
            return "N/A"
        return _collapse_whitespace(" ".join(str(v) for v in value))
    if isinstance(value, dict):
        return _collapse_whitespace(json.dumps(value, sort_keys=True))

    text = str(value)
    text = text.replace("|", " / ").replace("\n", " ")
    text = _collapse_whitespace(text)
    return text or "N/A"


def _benchmark_rank_label(selected_id: Optional[str], row: dict[str, Any]) -> str:
    if not selected_id:
        return "N/A"
    ranked_ids = row.get("benchmark_ranked_ids") or []
    try:
        rank = ranked_ids.index(selected_id) + 1
        return f"{rank}/{len(ranked_ids)}"
    except ValueError:
        return "N/A"


def _benchmark_auc_value(
    ontology: str,
    selected_id: Optional[str],
    auc_lookup: dict[str, dict[str, float]],
) -> str:
    if not selected_id:
        return "N/A"
    value = auc_lookup.get(_normalize_ontology_key(ontology), {}).get(selected_id)
    if value is None:
        return "N/A"
    return f"{value:.4f}"


def _in_target_topk_label(selected_id: Optional[str], row: dict[str, Any]) -> str:
    if not selected_id:
        return "N/A"
    return "Yes" if selected_id in (row.get("target_topk_ids") or []) else "No"


def _build_per_disease_doc_value(
    field: str,
    ontology: str,
    selected_id: Optional[str],
    row: dict[str, Any],
    model_map: dict[str, dict[str, Any]],
    auc_lookup: dict[str, dict[str, float]],
    selection_label: str,
) -> str:
    if field == "Selected PGS ID":
        return selected_id or "N/A"
    if field == "AoU benchmark rank":
        return _benchmark_rank_label(selected_id, row)
    if field == "AoU benchmark AUC":
        return _benchmark_auc_value(ontology, selected_id, auc_lookup)
    if field == "In Target_TopK":
        return _in_target_topk_label(selected_id, row)
    if field == "Selection frequency":
        return selection_label

    model = model_map.get(selected_id or "")
    return _format_doc_value(_get_nested_field(model, field), field)


def _target_columns(row: dict[str, Any]) -> list[tuple[str, Optional[str], str]]:
    target_ids = list(row.get("target_topk_ids") or [])
    columns: list[tuple[str, Optional[str], str]] = []
    for idx, target_id in enumerate(target_ids, start=1):
        columns.append((f"Target #{idx}", target_id, f"Benchmark target #{idx}"))
    if not columns:
        columns.append(("Target #1", None, "Benchmark target #1"))
    return columns


def _recompute_baseline_in_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """Recompute tiered baseline for each disease in summary and update aggregate."""
    per_disease = summary.get("per_disease") or []
    total_ontologies = len(per_disease)

    for row in per_disease:
        candidate_summaries = row.get("candidate_models_visible_to_llm") or []
        if not candidate_summaries:
            continue
        candidate_models = [_model_from_summary(s) for s in candidate_summaries]
        baseline = _tiered_baseline(candidate_models)
        baseline_with_rank = None
        if baseline:
            baseline_with_rank = dict(baseline)
            rank_map = _benchmark_rank_map(row.get("benchmark_ranked_ids") or [])
            baseline_rank = rank_map.get(baseline.get("pgs_id"))
            baseline_with_rank["rank"] = baseline_rank
            baseline_with_rank["rank_label"] = _rank_label(baseline_rank, row.get("n_models", 0))
        row["baseline"] = baseline_with_rank
        row["baseline_in_target_topk"] = bool(
            baseline and baseline.get("pgs_id") in set(row.get("target_topk_ids") or [])
        )

    baseline_hits = sum(1 for row in per_disease if row.get("baseline_in_target_topk"))
    baseline_available = sum(1 for row in per_disease if row.get("baseline"))
    baseline_accuracy = baseline_hits / total_ontologies if total_ontologies else 0.0

    if "baseline" not in summary:
        summary["baseline"] = {}
    summary["baseline"].update({
        "name": "tiered_baseline_pgs_only_auc_then_full_model_auroc",
        "available": baseline_available,
        "coverage": round(baseline_available / total_ontologies, 4) if total_ontologies else 0.0,
        "hits": baseline_hits,
        "accuracy": round(baseline_accuracy, 4),
    })
    return summary


def _write_without_domain_per_disease_doc(summary: dict[str, Any]) -> Path:
    auc_lookup = _load_aou_auc_lookup()
    per_disease_rows = _sort_disease_rows(summary["per_disease"])

    lines = [
        "# Without Domain Knowledge: Per-Disease Comparison",
        "",
        "## Scope",
        "",
        "This report is a disease-by-disease comparison built from the without-domain experiment summary and the underlying AoU benchmark matrices.",
        "",
        "Field Type labels in the last column indicate whether a row is part of the current agent input (`Agent Input`) or post-hoc evaluation metadata used only for benchmark/experiment analysis (`Benchmark Only`).",
        "",
        "Each disease table includes all models in the benchmark `Target_TopK` set, listed in benchmark order as `Target #1..#K`.",
        "",
        "## High-Level Outcome",
        "",
        (
            f"- Without Domain Knowledge: "
            f"`{summary['majority_vote_hits']}/{summary['total_ontologies']} = {_format_percent(summary['majority_vote_accuracy'])}`; "
            f"`trial_hits = {summary['diagnostics']['trial_hits']}/{summary['diagnostics']['total_trials']} = {_format_percent(summary['diagnostics']['trial_hit_rate'])}`"
        ),
        (
            f"- Baseline: `{summary['baseline']['hits']}/{summary['total_ontologies']} = "
            f"{_format_percent(summary['baseline']['accuracy'])}`"
        ),
        "",
        "## Per-Disease Tables",
        "",
    ]

    for row in per_disease_rows:
        ontology = row["ontology"]
        models = _model_map(row)
        target_columns = _target_columns(row)
        without_id = row.get("modal_recommendation")
        baseline_id = (row.get("baseline") or {}).get("pgs_id")

        header = ["Field"] + [label for label, _, _ in target_columns] + ["Without Domain Knowledge", "Baseline", "Field Type"]
        separator = ["---"] * len(header)

        lines.extend([
            f"### {ontology}",
            "",
            f"Candidate pool: `{row['n_models']}` models. Benchmark `Target_TopK`: `{row['target_topk']}`.",
            "",
            "",
            f"| {' | '.join(header)} |",
            f"| {' | '.join(separator)} |",
        ])

        for field, field_type in FIELD_ROWS:
            values = [field]
            for _, target_id, selection_label in target_columns:
                values.append(
                    _build_per_disease_doc_value(
                        field=field,
                        ontology=ontology,
                        selected_id=target_id,
                        row=row,
                        model_map=models,
                        auc_lookup=auc_lookup,
                        selection_label=selection_label,
                    )
                )
            values.append(
                _build_per_disease_doc_value(
                    field=field,
                    ontology=ontology,
                    selected_id=without_id,
                    row=row,
                    model_map=models,
                    auc_lookup=auc_lookup,
                    selection_label=f"{row.get('modal_recommendation_count', 0)}/{summary['trials_per_ontology']} trials",
                )
            )
            values.append(
                _build_per_disease_doc_value(
                    field=field,
                    ontology=ontology,
                    selected_id=baseline_id,
                    row=row,
                    model_map=models,
                    auc_lookup=auc_lookup,
                    selection_label="Rule-based baseline",
                )
            )
            values.append("Agent Input" if field_type == "agent_input" else "Benchmark Only")
            lines.append(f"| {' | '.join(values)} |")

        lines.extend(["", ""])

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    WITHOUT_DOMAIN_PER_DISEASE_DOC.write_text("\n".join(lines), encoding="utf-8")
    return WITHOUT_DOMAIN_PER_DISEASE_DOC


def _write_report(summary: dict[str, Any]) -> None:
    total_ontologies = summary["total_ontologies"]
    total_trials = summary["diagnostics"]["total_trials"]
    majority_vote_hits = summary["majority_vote_hits"]
    majority_vote_accuracy = summary["majority_vote_accuracy"]
    trial_hits = summary["diagnostics"]["trial_hits"]
    trial_hit_rate = summary["diagnostics"]["trial_hit_rate"]
    baseline_hits = summary["baseline"]["hits"]
    baseline_accuracy = summary["baseline"]["accuracy"]
    cost = summary.get("cost") or {}
    token_usage = cost.get("token_usage") or {}
    cost_breakdown = cost.get("estimated_cost_breakdown_usd") or {}
    per_disease_rows = _sort_disease_rows(summary["per_disease"])

    lines = [
        "# Contribution2 Experiment 1: Without Domain Knowledge",
        "",
        "## Summary",
        "",
        f"- **Diseases**: {total_ontologies}",
        f"- **Trials per disease**: {summary['trials_per_ontology']}",
        f"- **Total trials**: {total_trials}",
        f"- **Model**: {summary['model']}",
        (
            f"- **Estimated API cost**: {_format_currency(cost.get('estimated_total_cost_usd', 0.0))} "
            f"(uncached input {token_usage.get('uncached_input_tokens', 0):,} tokens = "
            f"{_format_currency(cost_breakdown.get('uncached_input', 0.0))}; "
            f"cached input {token_usage.get('cached_input_tokens', 0):,} tokens = "
            f"{_format_currency(cost_breakdown.get('cached_input', 0.0))}; "
            f"output {token_usage.get('output_tokens', 0):,} tokens = "
            f"{_format_currency(cost_breakdown.get('output', 0.0))})"
        ),
        (
            f"- **Overall Recommended Model Accuracy**: {majority_vote_hits}/{total_ontologies} = "
            f"{_format_percent(majority_vote_accuracy)}; "
            f"`trial_hits = {trial_hits}/{total_trials} = {_format_percent(trial_hit_rate)}`"
        ),
        (
            f"- **Baseline (tiered: PGS-only AUROC, then full-model AUROC fallback)**: "
            f"{baseline_hits}/{total_ontologies} = {_format_percent(baseline_accuracy)}"
        ),
        "",
        "## Experiment Setup",
        "",
        "- **Step 1 tools**: prs_model_pgscatalog_search + prs_model_performance_landscape",
        "- **Domain Knowledge**: Disabled",
        "- **Candidate pool**: restricted to disease-specific `N Models` that were successfully evaluated in Contribution1 on All of Us",
        "- **Success rule**: a run is successful iff the recommended `PGS ID` belongs to that disease's `Target_TopK` set",
        "- **Baseline rule**: tiered—Tier 1 uses highest PGS-only AUROC; Tier 2 falls back to highest full-model AUROC when no candidate has PGS-comparable AUROC",
        "",
        "## Results by Disease",
        "",
        "All ranks below are **AUC ranks from the All of Us benchmark** among the disease-specific `N Models`, sorted from highest AUC to lowest AUC.",
        "They are **not** PGS Catalog reported-AUC ranks.",
        "",
        "| Ontology | N Models | Target_TopK | Trial Hits | Without Domain Knowledge Hits Target | Without Domain Knowledge | Baseline Hits Target | Baseline Models |",
        "|----------|----------|-------------|------------|------------------------|------------|----------------------|-----------------|",
    ]

    for row in per_disease_rows:
        modal_hit = "Yes" if row["modal_recommendation_in_target_topk"] else "No"
        recommendation_models = "<br>".join(
            f"{item['pgs_id']} (AUC rank {item['rank_label']}): x{item['count']}"
            for item in (row.get("recommended_model_counts") or [])
        ) or "-"
        baseline = row.get("baseline") or {}
        baseline_id = baseline.get("pgs_id")
        baseline_rank_label = baseline.get("rank_label") or "-"
        baseline_text = (
            f"{baseline_id} (AUC rank {baseline_rank_label})"
            if baseline_id
            else "-"
        )
        baseline_hit = "Yes" if row["baseline_in_target_topk"] else "No"
        lines.append(
            f"| {row['ontology']} | {row['n_models']} | {row['target_topk']} | "
            f"{row['trial_hits']}/{summary['trials_per_ontology']} | "
            f"{modal_hit} | {recommendation_models} | {baseline_hit} | {baseline_text} |"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def _collect(batch_id: Optional[str]) -> dict[str, Any]:
    if not BATCH_MANIFEST_JSON.exists():
        raise FileNotFoundError(
            f"Batch manifest not found: {BATCH_MANIFEST_JSON}. Run with --mode prepare or --mode prepare-submit first."
        )
    manifest = _load_json(BATCH_MANIFEST_JSON)
    job = _load_job(batch_id=batch_id)
    client = _client()
    batch = client.batches.retrieve(job["batch_id"])

    if batch.status != "completed":
        raise RuntimeError(
            f"Batch {batch.id} is not completed yet (status={batch.status}). Run --mode status and retry later."
        )
    if not batch.output_file_id:
        raise RuntimeError(f"Batch {batch.id} completed without output_file_id.")

    raw_output_jsonl = client.files.retrieve_content(batch.output_file_id)
    BATCH_OUTPUT_JSONL.write_text(raw_output_jsonl, encoding="utf-8")

    raw_error_jsonl = ""
    if batch.error_file_id:
        raw_error_jsonl = client.files.retrieve_content(batch.error_file_id)
        BATCH_ERROR_JSONL.write_text(raw_error_jsonl, encoding="utf-8")

    parsed_outputs: dict[str, dict[str, Any]] = {}
    for line in raw_output_jsonl.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        parsed = _parse_batch_output_line(record)
        parsed_outputs[parsed["custom_id"]] = parsed

    error_map = _parse_error_file(raw_error_jsonl) if raw_error_jsonl else {}
    trial_results, summary = _build_summary_and_results(
        manifest=manifest,
        parsed_outputs=parsed_outputs,
        error_map=error_map,
    )
    summary["cost"] = _estimate_batch_cost(batch.model_dump())

    _write_json(RESULTS_JSON, trial_results)
    _write_json(SUMMARY_JSON, summary)
    _write_report(summary)
    per_disease_doc = _write_without_domain_per_disease_doc(summary)
    archive_dir = _archive_current_outputs(summary=summary)

    job_payload = {
        "batch_id": batch.id,
        "status": batch.status,
        "input_file_id": batch.input_file_id,
        "output_file_id": batch.output_file_id,
        "error_file_id": batch.error_file_id,
        "request_counts": batch.request_counts.model_dump() if batch.request_counts else None,
        "batch": batch.model_dump(),
        "manifest_file": str(BATCH_MANIFEST_JSON),
        "output_jsonl_file": str(BATCH_OUTPUT_JSONL),
        "error_jsonl_file": str(BATCH_ERROR_JSONL) if batch.error_file_id else None,
    }
    _write_json(BATCH_JOB_JSON, job_payload)

    print(f"Collected batch output: {BATCH_OUTPUT_JSONL}")
    if batch.error_file_id:
        print(f"Collected batch errors: {BATCH_ERROR_JSONL}")
    print(f"Results: {RESULTS_JSON}")
    print(f"Summary: {SUMMARY_JSON}")
    print(f"Report:  {REPORT_MD}")
    print(f"Per-disease doc: {per_disease_doc}")
    print(f"Archive: {archive_dir}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Contribution2 Experiment 1: Without Domain Knowledge batch evaluation")
    parser.add_argument(
        "--mode",
        choices=["prepare", "prepare-submit", "status", "collect", "archive-current", "quick-eval"],
        default="prepare-submit",
        help="Batch workflow step (default: prepare-submit)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Prepare only the first N ontologies for debugging")
    parser.add_argument("--trials", type=int, default=10, help="Number of repeated trials per ontology (default: 10)")
    parser.add_argument("--batch-id", type=str, default=None, help="Optional batch ID override for status/collect")
    parser.add_argument("--model", type=str, default=None, help="Optional OpenAI model override for this run directory")
    parser.add_argument("--ontology", action="append", default=None, help="Run only the specified ontology (repeatable)")
    parser.add_argument("--ontologies-file", type=str, default=None, help="Path to a newline-delimited ontology filter file")
    parser.add_argument("--run-tag", type=str, default=None, help="Optional tag appended to the run directory name")
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Ignore experiment-local prepare cache and refetch candidate metadata",
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set. Configure .env before running.")
        return 1

    if args.model:
        os.environ["OPENAI_MODEL"] = args.model

    ontology_filter = _load_ontology_filter(args.ontology, args.ontologies_file)
    _set_run_paths(trials=args.trials, model=args.model, run_tag=args.run_tag)

    try:
        if args.mode == "prepare":
            _prepare(
                limit=args.limit,
                trials=args.trials,
                refresh_cache=args.refresh_cache,
                ontology_filter=ontology_filter,
            )
        elif args.mode == "prepare-submit":
            _prepare(
                limit=args.limit,
                trials=args.trials,
                refresh_cache=args.refresh_cache,
                ontology_filter=ontology_filter,
            )
            _submit_batch()
        elif args.mode == "status":
            _status(batch_id=args.batch_id)
        elif args.mode == "collect":
            _collect(batch_id=args.batch_id)
        elif args.mode == "archive-current":
            _archive_current_outputs()
        elif args.mode == "quick-eval":
            _quick_eval()
        else:
            raise ValueError(f"Unsupported mode: {args.mode}")
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
