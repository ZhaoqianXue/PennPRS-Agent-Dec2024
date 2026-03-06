"""
Contribution2 Experiment 1: Native GPT batch evaluation.

This runner converts the formal Contribution2 Step 1 experiment into an OpenAI
Batch API workflow so the LLM decisions can be evaluated in parallel.

Workflow:
  1. Prepare local candidate metadata and benchmark labels for all diseases.
  2. Build one Step 1 request per disease-trial pair and write JSONL.
  3. Submit the JSONL file to the OpenAI Batch API.
  4. After the batch completes, download outputs and compute the experiment metrics.

Usage:
  python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py
  python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py --mode status
  python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py --mode collect
  python experiments/contribution2/recommendation/scripts/run_experiment_native_gpt.py --mode prepare --limit 3 --trials 2
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any, Optional

import pandas as pd
from openai import OpenAI
from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel

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

# Force Contribution2 native-GPT settings before importing project modules.
os.environ["PENNPRS_STEP1_DISABLE_DOMAIN_KNOWLEDGE"] = "1"
os.environ["PENNPRS_STEP1_RUN_NO_DOMAIN_ABLATION"] = "0"
os.environ["PENNPRS_CONTRIB2_STRICT_LLM_ONLY"] = "1"

eval_pgs_path = (
    PROJECT_ROOT
    / "experiments"
    / "contribution2"
    / "recommendation"
    / "runs"
    / "evaluated_pgs_per_ontology.json"
)
if eval_pgs_path.exists():
    os.environ["PENNPRS_CONTRIB2_EVALUATED_PGS_JSON"] = str(eval_pgs_path)

from src.server.core.llm_config import get_config
from src.server.core.system_prompts import CO_SCIENTIST_STEP1_NATIVE_PROMPT
from src.server.core.tools.prs_model_tools import (
    prs_model_performance_landscape,
    prs_model_pgscatalog_search,
)
from src.server.core.pgs_catalog_client import PGSCatalogClient

CONTRIB2_DIR = Path(__file__).parent.parent.parent
UNION_CSV = CONTRIB2_DIR / "disease_selection" / "runs" / "selected_diseases_contribution2_union.csv"
RECOMMENDATION_RUNS = Path(__file__).parent.parent / "runs"
TOP_K_JSON = RECOMMENDATION_RUNS / "top_k_pgs_per_ontology.json"
EVALUATED_JSON = RECOMMENDATION_RUNS / "evaluated_pgs_per_ontology.json"

RESULTS_JSON = RECOMMENDATION_RUNS / "experiment_native_gpt_results.json"
SUMMARY_JSON = RECOMMENDATION_RUNS / "experiment_native_gpt_summary.json"
REPORT_MD = RECOMMENDATION_RUNS / "experiment_native_gpt_report.md"

BATCH_REQUESTS_JSONL = RECOMMENDATION_RUNS / "experiment_native_gpt_batch_requests.jsonl"
BATCH_MANIFEST_JSON = RECOMMENDATION_RUNS / "experiment_native_gpt_batch_manifest.json"
BATCH_JOB_JSON = RECOMMENDATION_RUNS / "experiment_native_gpt_batch_job.json"
BATCH_OUTPUT_JSONL = RECOMMENDATION_RUNS / "experiment_native_gpt_batch_output.jsonl"
BATCH_ERROR_JSONL = RECOMMENDATION_RUNS / "experiment_native_gpt_batch_errors.jsonl"

BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 42
VALID_PGS_ID_RE = re.compile(r"^PGS\d+$")
MAX_CHAT_COMPLETIONS_N = 8

STEP1_RATIONALE_FEATURE_KEYWORDS = {
    "trait_match": ["trait", "phenotype", "proxy", "family history"],
    "auc": ["auc", "auroc", "roc"],
    "r2": ["r2", "r²", "variance explained"],
    "sample_size": ["sample", "n=", "cohort", "powered"],
    "ancestry": ["ancestry", "eur", "afr", "eas", "sas", "multi-ancestry"],
    "method": ["method", "ldpred", "prs-cs", "lassosum", "genoboost", "snpnet"],
    "variants": ["variant", "snp"],
    "covariates": ["covariate", "age", "sex", "pc"],
}


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
    return {
        "id": getattr(model, "id", None),
        "trait_reported": getattr(model, "trait_reported", None),
        "trait_efo": getattr(model, "trait_efo", None),
        "method_name": getattr(model, "method_name", None),
        "variants_number": getattr(model, "variants_number", None),
        "ancestry_distribution": getattr(model, "ancestry_distribution", None),
        "publication": getattr(model, "publication", None),
        "date_release": getattr(model, "date_release", None),
        "samples_training": getattr(model, "samples_training", None),
        "performance_metrics": getattr(model, "performance_metrics", None),
        "phenotyping_reported": getattr(model, "phenotyping_reported", None),
        "covariates": getattr(model, "covariates", None),
        "sampleset": getattr(model, "sampleset", None),
        "training_development_cohorts": getattr(model, "training_development_cohorts", None),
        "variants_genomebuild": getattr(model, "variants_genomebuild", None),
        "samples_variants": getattr(model, "samples_variants", None),
        "validation_sample_size": getattr(model, "validation_sample_size", None),
    }


def _bootstrap_mean_ci(values: list[float]) -> Optional[dict[str, float]]:
    if not values:
        return None
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(values)
    means: list[float] = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lower_idx = int(0.025 * (BOOTSTRAP_RESAMPLES - 1))
    upper_idx = int(0.975 * (BOOTSTRAP_RESAMPLES - 1))
    return {
        "lower": round(means[lower_idx], 4),
        "upper": round(means[upper_idx], 4),
    }


def _is_valid_output(recommended_id: Optional[str], candidate_id_set: set[str]) -> bool:
    if not recommended_id or not VALID_PGS_ID_RE.match(recommended_id):
        return False
    return recommended_id in candidate_id_set


def _best_reported_auc_baseline(models: list[Any]) -> Optional[dict[str, Any]]:
    best_model = None
    best_auc = None
    for model in models:
        perf = getattr(model, "performance_metrics", {}) or {}
        auc = _safe_float(perf.get("auc"))
        if auc is None:
            continue
        if best_auc is None or auc > best_auc:
            best_model = model
            best_auc = auc
    if best_model is None or best_auc is None:
        return None
    return {
        "pgs_id": getattr(best_model, "id", None),
        "reported_auc": round(best_auc, 4),
        "trait_reported": getattr(best_model, "trait_reported", None),
        "method_name": getattr(best_model, "method_name", None),
        "validation_sample_size": getattr(best_model, "validation_sample_size", None),
    }


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
        {"role": "system", "content": CO_SCIENTIST_STEP1_NATIVE_PROMPT},
        {
            "role": "user",
            "content": (
                "Perform STEP 1 only. Use the context JSON below to decide whether the direct "
                "match quality is HIGH, SUB_OPTIMAL, or NO_MATCH_FOUND. "
                "Return JSON with fields: outcome, best_model_id, confidence, rationale.\n\n"
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
        "temperature": config.temperature,
        "n": n_choices,
        "messages": _step1_messages(context_json),
        "response_format": _step1_response_format(),
    }
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


def _prepare_manifest(limit: Optional[int], trials: int) -> dict[str, Any]:
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
        candidate_result = prs_model_pgscatalog_search(
            pgs_client,
            ontology,
            evaluated_pgs_whitelist=candidate_id_set,
        )
        candidate_models = list(candidate_result.models)
        baseline = _best_reported_auc_baseline(candidate_models)
        context = _step1_context(
            ontology=ontology,
            candidate_models=candidate_models,
            total_found=candidate_result.total_found,
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
            "target_topk_ids": target_topk_ids,
            "candidate_model_ids": candidate_model_ids,
            "candidate_models_visible_to_llm": [_summarize_model_for_llm(model) for model in candidate_models],
            "baseline": baseline,
            "total_found": candidate_result.total_found,
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
        "experiment": "native_gpt_batch_formal",
        "model": _model_name(),
        "trials_per_ontology": trials,
        "total_ontologies": len(disease_metadata),
        "total_requests": len(requests),
        "disease_metadata": disease_metadata,
        "requests": requests,
    }
    return manifest


def _prepare(limit: Optional[int], trials: int) -> dict[str, Any]:
    manifest = _prepare_manifest(limit=limit, trials=trials)
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
            "experiment": "contribution2_native_gpt",
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
        hit_count = sum(1 for row in disease_trials if row["in_target_topk"])
        valid_count = sum(1 for row in disease_trials if row["valid_output"])
        error_count = sum(1 for row in disease_trials if row["error"])
        trial_count = manifest["trials_per_ontology"]
        hit_rate = hit_count / trial_count
        valid_rate = valid_count / trial_count
        modal_id, modal_count = _modal_recommendation(disease_trials)
        modal_in_target = bool(modal_id and modal_id in set(disease["target_topk_ids"]))
        feature_counter = Counter(
            feature
            for trial in disease_trials
            for feature in trial.get("rationale_features", [])
        )
        baseline = disease.get("baseline")
        baseline_hit = bool(baseline and baseline.get("pgs_id") in set(disease["target_topk_ids"]))

        per_disease.append({
            "ontology": ontology,
            "n_models": disease["n_models"],
            "target_topk": disease["target_topk"],
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
            "modal_recommendation_in_target_topk": modal_in_target,
            "trial_recommendations": [row["recommended_pgs_id"] for row in disease_trials],
            "feature_mentions": dict(sorted(feature_counter.items())),
            "baseline": baseline,
            "baseline_in_target_topk": baseline_hit,
        })

    total_ontologies = len(per_disease)
    total_trials = len(trial_results)
    trial_hits = sum(1 for row in trial_results if row["in_target_topk"])
    valid_outputs = sum(1 for row in trial_results if row["valid_output"])
    trial_hit_rate = trial_hits / total_trials if total_trials else 0.0
    valid_output_rate = valid_outputs / total_trials if total_trials else 0.0
    disease_hit_rates = [row["trial_hit_rate"] for row in per_disease]
    mean_disease_hit_rate = mean(disease_hit_rates) if disease_hit_rates else 0.0
    bootstrap_ci = _bootstrap_mean_ci(disease_hit_rates)
    majority_vote_hits = sum(1 for row in per_disease if row["modal_recommendation_in_target_topk"])
    majority_vote_accuracy = majority_vote_hits / total_ontologies if total_ontologies else 0.0
    baseline_hits = sum(1 for row in per_disease if row["baseline_in_target_topk"])
    baseline_accuracy = baseline_hits / total_ontologies if total_ontologies else 0.0

    summary = {
        "experiment": "native_gpt_batch_formal",
        "domain_knowledge": False,
        "strict_llm_only": True,
        "cross_disease_enabled": False,
        "batch_mode": True,
        "model": manifest["model"],
        "total_ontologies": total_ontologies,
        "trials_per_ontology": manifest["trials_per_ontology"],
        "mean_disease_hit_rate": round(mean_disease_hit_rate, 4),
        "majority_vote_hits": majority_vote_hits,
        "majority_vote_accuracy": round(majority_vote_accuracy, 4),
        "baseline": {
            "name": "highest_reported_auc_in_pgscatalog_metadata",
            "hits": baseline_hits,
            "accuracy": round(baseline_accuracy, 4),
        },
        "diagnostics": {
            "total_trials": total_trials,
            "trial_hits": trial_hits,
            "trial_hit_rate": round(trial_hit_rate, 4),
            "valid_outputs": valid_outputs,
            "valid_output_rate": round(valid_output_rate, 4),
            "mean_disease_hit_rate_bootstrap_95ci": bootstrap_ci,
        },
        "per_disease": per_disease,
    }
    return trial_results, summary


def _write_report(summary: dict[str, Any]) -> None:
    total_ontologies = summary["total_ontologies"]
    total_trials = summary["diagnostics"]["total_trials"]
    mean_disease_hit_rate = summary["mean_disease_hit_rate"]
    majority_vote_hits = summary["majority_vote_hits"]
    majority_vote_accuracy = summary["majority_vote_accuracy"]
    baseline_hits = summary["baseline"]["hits"]
    baseline_accuracy = summary["baseline"]["accuracy"]

    lines = [
        "# Contribution2 Experiment 1: Native GPT (Batch Formal Protocol)",
        "",
        "## Summary",
        "",
        f"- **Diseases**: {total_ontologies}",
        f"- **Trials per disease**: {summary['trials_per_ontology']}",
        f"- **Total trials**: {total_trials}",
        f"- **Model**: {summary['model']}",
        "- **Execution mode**: OpenAI Batch API",
        "- **Step 1 tools**: prs_model_pgscatalog_search + prs_model_performance_landscape",
        "- **Domain Knowledge**: Disabled",
        "- **Strict LLM-only mode**: Enabled (no fallback, no auto-filled recommendation)",
        f"- **Mean disease hit rate**: {_format_percent(mean_disease_hit_rate)}",
        f"- **Majority-vote accuracy**: {majority_vote_hits}/{total_ontologies} = {_format_percent(majority_vote_accuracy)}",
        (
            f"- **Baseline (highest reported AUC in PGS Catalog metadata)**: "
            f"{baseline_hits}/{total_ontologies} = {_format_percent(baseline_accuracy)}"
        ),
        "",
        "## Per-Disease Results",
        "",
        "| Ontology | N Models | Target_TopK | Trial Hits | Modal Recommendation | Modal In Target | Baseline | Baseline In Target |",
        "|----------|----------|-------------|------------|----------------------|-----------------|----------|--------------------|",
    ]

    for row in summary["per_disease"]:
        modal_id = row["modal_recommendation"] or "-"
        modal_hit = "Yes" if row["modal_recommendation_in_target_topk"] else "No"
        baseline_id = (row["baseline"] or {}).get("pgs_id") or "-"
        baseline_hit = "Yes" if row["baseline_in_target_topk"] else "No"
        lines.append(
            f"| {row['ontology']} | {row['n_models']} | {row['target_topk']} | "
            f"{row['trial_hits']}/{summary['trials_per_ontology']} | "
            f"{modal_id} | {modal_hit} | {baseline_id} | {baseline_hit} |"
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

    _write_json(RESULTS_JSON, trial_results)
    _write_json(SUMMARY_JSON, summary)
    _write_report(summary)

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
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Contribution2 Experiment 1: Native GPT batch evaluation")
    parser.add_argument(
        "--mode",
        choices=["prepare", "prepare-submit", "status", "collect"],
        default="prepare-submit",
        help="Batch workflow step (default: prepare-submit)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Prepare only the first N ontologies for debugging")
    parser.add_argument("--trials", type=int, default=10, help="Number of repeated trials per ontology (default: 10)")
    parser.add_argument("--batch-id", type=str, default=None, help="Optional batch ID override for status/collect")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set. Configure .env before running.")
        return 1

    try:
        if args.mode == "prepare":
            _prepare(limit=args.limit, trials=args.trials)
        elif args.mode == "prepare-submit":
            _prepare(limit=args.limit, trials=args.trials)
            _submit_batch()
        elif args.mode == "status":
            _status(batch_id=args.batch_id)
        elif args.mode == "collect":
            _collect(batch_id=args.batch_id)
        else:
            raise ValueError(f"Unsupported mode: {args.mode}")
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
