"""Pre-fetch PGS Catalog metadata (details + performance) for every distinct
PGS ID referenced by `trait_bundle_index.json` and save the result to a
pickle under `data/pgs_catalog_cache/`.

Development-only utility. In production the transfer pipeline fetches
metadata on-demand through the PGSCatalogClient; in development we want to
pay the network cost once and reuse across dozens of debug runs.

Run:
    python experiments/contribution3/transfer/scripts/prefetch_pgs_catalog_cache.py

Takes ~10-30 min on a clean cache, ~1 min when the file already has most
entries (only fetches the delta).
"""
from __future__ import annotations
import os
import pickle
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from experiments.contribution3.transfer.common import (
    load_trait_bundle_index,
    BUNDLE_INDEX_JSON,
)
from src.server.core.pgs_catalog_client import PGSCatalogClient
from src.server.core.tools import prs_model_tools

import pandas as pd


CACHE_DIR = ROOT / "data" / "pgs_catalog_cache"
CACHE_FILE = CACHE_DIR / "pgs_catalog_cache.pkl"

# Benchmark-universe PGS IDs — the only ones the AUC evaluation can rank. We
# restrict the dev cache to exactly these so the one-time pre-fetch cost is
# ~3196 fetches instead of ~5276 (the superset in the trait_bundle_index).
AUC_MATRIX_PATHS = [
    ROOT / "experiments/contribution1/result/aou_extend_trait/prs_adjauc_matrix_binary_extend_qc.csv",
    ROOT / "experiments/contribution1/result/aou_binary/prs_adjauc_matrix_binary_combined_rootcode.csv",
]


def _col_to_pgs(c: str) -> str:
    s = str(c).strip()
    if "__" in s:
        s = s.rsplit("__", 1)[-1]
    return s.replace("_hmPOS_GRCh38", "")


def _benchmark_pgs_universe() -> set[str]:
    pgs: set[str] = set()
    for path in AUC_MATRIX_PATHS:
        df = pd.read_csv(path, index_col=0, nrows=1)
        pgs.update(_col_to_pgs(c) for c in df.columns)
    return pgs


def main() -> None:
    bundles = load_trait_bundle_index(BUNDLE_INDEX_JSON)
    index_pgs = {pgs for b in bundles for pgs in b.candidate_pgs_ids}
    benchmark_pgs = _benchmark_pgs_universe()
    # Only fetch PGS that are BOTH in the index (reachable via dossier) AND in
    # the benchmark evaluation universe (AUC columns). Anything outside the
    # benchmark universe can't ever contribute to eval reachability metrics.
    all_pgs = sorted(index_pgs & benchmark_pgs)
    print(
        f"Found {len(all_pgs)} distinct PGS IDs "
        f"(index={len(index_pgs)}, benchmark={len(benchmark_pgs)}, overlap={len(all_pgs)})"
    )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    existing: dict = {"details": {}, "performance": {}}
    if CACHE_FILE.exists():
        with CACHE_FILE.open("rb") as f:
            existing = pickle.load(f)
        print(
            f"Existing cache: {len(existing.get('details', {}))} details, "
            f"{len(existing.get('performance', {}))} performance entries"
        )

    missing = [p for p in all_pgs if p not in existing.get("details", {}) or p not in existing.get("performance", {})]
    print(f"Need to fetch: {len(missing)} PGS")
    if not missing:
        print("Cache is up to date. Nothing to do.")
        return

    # Prime the in-memory caches with whatever is already on disk so the
    # cached-fetch wrappers return existing entries without a network call.
    prs_model_tools._PGS_DETAILS_CACHE.update(existing.get("details", {}))
    prs_model_tools._PGS_PERFORMANCE_CACHE.update(existing.get("performance", {}))

    client = PGSCatalogClient()
    max_workers = int(os.getenv("PGS_FETCH_MAX_WORKERS", "16"))
    start = time.time()

    def _fetch(pgs_id: str) -> tuple[str, object, object]:
        det = prs_model_tools._cached_get_score_details(client, pgs_id)
        perf = prs_model_tools._cached_get_score_performance(client, pgs_id)
        return pgs_id, det, perf

    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_fetch, pgs_id): pgs_id for pgs_id in missing}
        for fut in as_completed(futures):
            try:
                fut.result()
            except Exception as exc:
                pgs_id = futures[fut]
                print(f"[WARN] {pgs_id} failed: {exc}")
            completed += 1
            if completed % 50 == 0 or completed == len(missing):
                elapsed = time.time() - start
                rate = completed / max(elapsed, 1e-6)
                eta = (len(missing) - completed) / max(rate, 1e-6)
                print(
                    f"  progress {completed}/{len(missing)} "
                    f"(rate={rate:.1f}/s, eta={eta/60:.1f}min)",
                    flush=True,
                )

    # Persist combined cache (includes whatever was cached on disk + new fetches).
    # We grab the final in-memory caches — they already include every success.
    details_out = dict(prs_model_tools._PGS_DETAILS_CACHE)
    performance_out = dict(prs_model_tools._PGS_PERFORMANCE_CACHE)
    with CACHE_FILE.open("wb") as f:
        pickle.dump({"details": details_out, "performance": performance_out}, f)
    print(
        f"Saved {len(details_out)} details + {len(performance_out)} performance "
        f"entries to {CACHE_FILE}"
    )


if __name__ == "__main__":
    main()
