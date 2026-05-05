#!/usr/bin/env python3
"""
Fetch PGS Catalog metadata for a PRS model (standalone version).

This script is self-contained and does not import project modules.
Stdlib only — colleagues can copy this file and run it directly.

Single-PGS usage (default):
    python fetch_pgs_model_standalone.py PGS003852
    python fetch_pgs_model_standalone.py PGS003852 -o output/pgs_model.json

Bulk usage — fetch every PGS in the catalog as JSONL (one line per PGS):
    python fetch_pgs_model_standalone.py --all -o pgs_full_rest_dump.jsonl
    python fetch_pgs_model_standalone.py --all -o out.jsonl --workers 8

Bulk mode is resumable: re-running with the same -o appends only the
PGS IDs that aren't already present in the JSONL.

Output schema (per PGS, identical for single & bulk):
    {"pgs_id": "...", "score": {...full /rest/score/{id} JSON...},
     "performance": [...full /rest/performance/search results...]}
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://www.pgscatalog.org/rest"
DEFAULT_TIMEOUT_S = 30
MAX_RETRIES = 5
BACKOFF_BASE_S = 0.6
BACKOFF_MAX_S = 8.0
JITTER_S = 0.2
USER_AGENT = "fetch_pgs_model_standalone/1.0"


def _parse_retry_after_seconds(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    try:
        return float(value.strip())
    except Exception:
        return None


def _sleep_with_backoff(attempt: int, retry_after: Optional[float] = None) -> None:
    wait_s = retry_after if retry_after is not None else min(
        BACKOFF_MAX_S, BACKOFF_BASE_S * (2 ** attempt)
    )
    wait_s += random.uniform(0.0, JITTER_S)
    time.sleep(wait_s)


def _do_request(url: str) -> Any:
    last_exc: Optional[Exception] = None

    for attempt in range(MAX_RETRIES + 1):
        req = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urlopen(req, timeout=DEFAULT_TIMEOUT_S) as resp:
                raw = resp.read()
                return json.loads(raw.decode("utf-8"))
        except HTTPError as exc:
            last_exc = exc
            status = exc.code

            if status == 429:
                retry_after = _parse_retry_after_seconds(exc.headers.get("Retry-After"))
                print(
                    f"Warning: rate limited (429) for {url}; retrying "
                    f"(attempt {attempt + 1}/{MAX_RETRIES + 1})",
                    file=sys.stderr,
                )
                if attempt < MAX_RETRIES:
                    _sleep_with_backoff(attempt, retry_after=retry_after)
                    continue

            if 500 <= status < 600 and attempt < MAX_RETRIES:
                print(
                    f"Warning: server error ({status}) for {url}; retrying "
                    f"(attempt {attempt + 1}/{MAX_RETRIES + 1})",
                    file=sys.stderr,
                )
                _sleep_with_backoff(attempt)
                continue

            raise
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                print(
                    f"Warning: request failed for {url} ({type(exc).__name__}); retrying "
                    f"(attempt {attempt + 1}/{MAX_RETRIES + 1})",
                    file=sys.stderr,
                )
                _sleep_with_backoff(attempt)
                continue
            raise

    if last_exc:
        raise last_exc
    raise RuntimeError(f"PGS Catalog request failed for {url}")


def _request_json(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    query = f"?{urlencode(params, doseq=True)}" if params else ""
    return _do_request(f"{BASE_URL}{path}{query}")


def get_score_details(pgs_id: str) -> Dict[str, Any]:
    try:
        return _request_json(f"/score/{pgs_id}")
    except Exception as exc:
        print(f"Error getting PGS details for {pgs_id}: {exc}", file=sys.stderr)
        return {}


def get_score_performance(pgs_id: str) -> List[Dict[str, Any]]:
    try:
        data = _request_json("/performance/search", params={"pgs_id": pgs_id})
        return data.get("results", []) or []
    except Exception as exc:
        print(f"Error getting PGS performance for {pgs_id}: {exc}", file=sys.stderr)
        return []


def fetch_pgs_model(pgs_id: str) -> Dict[str, Any]:
    score = get_score_details(pgs_id)
    performance = get_score_performance(pgs_id)

    if not score:
        print(f"Warning: No score details found for {pgs_id}", file=sys.stderr)
    if not performance:
        print(f"Info: No performance records for {pgs_id}", file=sys.stderr)

    return {
        "pgs_id": pgs_id,
        "score": score,
        "performance": performance,
    }


def iter_all_score_ids(page_size: int = 50) -> Iterator[str]:
    url = f"{BASE_URL}/score/all?limit={page_size}"
    while url:
        data = _do_request(url)
        for item in (data.get("results") or []):
            pid = item.get("id")
            if pid:
                yield pid
        url = data.get("next")


def _read_existing_pgs_ids(path: Path) -> set:
    if not path.exists():
        return set()
    seen: set = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            pid = rec.get("pgs_id")
            if pid:
                seen.add(pid)
    return seen


def fetch_all(output_path: Path, workers: int = 8, page_size: int = 50) -> int:
    print(f"[1/3] Listing all PGS IDs via /score/all (page_size={page_size})...", file=sys.stderr)
    all_ids: List[str] = list(iter_all_score_ids(page_size))
    total = len(all_ids)
    print(f"      catalog size: {total}", file=sys.stderr)

    seen = _read_existing_pgs_ids(output_path)
    todo = [pid for pid in all_ids if pid not in seen]
    print(
        f"[2/3] Resume check: already in {output_path.name}: {len(seen)}; "
        f"remaining: {len(todo)}",
        file=sys.stderr,
    )
    if not todo:
        print("Nothing to do.", file=sys.stderr)
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_lock = threading.Lock()
    completed = 0
    failed: List[Tuple[str, str]] = []
    start = time.time()

    def _task(pid: str) -> Tuple[str, Optional[Dict[str, Any]], Optional[str]]:
        try:
            rec = fetch_pgs_model(pid)
            if not rec.get("score"):
                return pid, None, "empty score (likely API error after retries)"
            return pid, rec, None
        except Exception as exc:
            return pid, None, f"{type(exc).__name__}: {exc}"

    print(f"[3/3] Fetching {len(todo)} PGS with {workers} workers...", file=sys.stderr)
    with output_path.open("a", encoding="utf-8") as fout:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_task, pid): pid for pid in todo}
            for fut in as_completed(futures):
                pid, rec, err = fut.result()
                completed += 1
                if rec is not None:
                    line = json.dumps(rec, ensure_ascii=False)
                    with write_lock:
                        fout.write(line + "\n")
                        fout.flush()
                else:
                    failed.append((pid, err or "unknown"))
                if completed % 50 == 0 or completed == len(todo):
                    elapsed = time.time() - start
                    rate = completed / max(elapsed, 1e-6)
                    eta = (len(todo) - completed) / max(rate, 1e-6)
                    print(
                        f"  progress {completed}/{len(todo)} "
                        f"(rate={rate:.1f}/s, eta={eta/60:.1f}min, fail={len(failed)})",
                        file=sys.stderr,
                        flush=True,
                    )

    written = completed - len(failed)
    print(
        f"\nDone. Wrote {written} new records to {output_path} "
        f"(total in file now: {len(seen) + written}).",
        file=sys.stderr,
    )
    if failed:
        print(f"  {len(failed)} PGS failed; first 10:", file=sys.stderr)
        for pid, err in failed[:10]:
            print(f"    {pid}: {err}", file=sys.stderr)
        print(f"  Re-run the same command to retry only the missing PGS.", file=sys.stderr)
    return 0 if not failed else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch PGS Catalog metadata for a PRS model (standalone). "
                    "Use --all to fetch every PGS in the catalog as JSONL."
    )
    parser.add_argument(
        "pgs_id",
        nargs="?",
        default=None,
        help="PGS Catalog ID (e.g. PGS003852). Ignored when --all is set. "
             "Default for single-PGS mode: PGS003852",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output path. Single-PGS mode: JSON file (default: pgs_model_{PGS_ID}.json). "
             "--all mode: JSONL file (default: pgs_full_rest_dump.jsonl).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Fetch every PGS in the catalog. Writes JSONL (one PGS per line) to --output. "
             "Resumable: skips PGS IDs already present in the output file.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Concurrent workers for --all mode (default: 8).",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="Page size for /score/all enumeration in --all mode (default: 50).",
    )
    args = parser.parse_args()

    if args.all:
        out_path = args.output if args.output is not None else Path("pgs_full_rest_dump.jsonl")
        return fetch_all(out_path, workers=args.workers, page_size=args.page_size)

    pgs_id = (args.pgs_id or "PGS003852").strip()
    if not pgs_id.upper().startswith("PGS"):
        pgs_id = f"PGS{pgs_id}"

    out_path = args.output if args.output is not None else Path(f"pgs_model_{pgs_id}.json")

    print(f"Fetching PGS model: {pgs_id}\n")
    data = fetch_pgs_model(pgs_id)

    print("=" * 60)
    print("SCORE METADATA (from /rest/score/{id})")
    print("=" * 60)
    print(json.dumps(data["score"], indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print(f"PERFORMANCE RECORDS ({len(data['performance'])} records)")
    print("=" * 60)
    for i, rec in enumerate(data["performance"]):
        print(f"\n--- Record #{i + 1} (id={rec.get('id', 'N/A')}) ---")
        print(json.dumps(rec, indent=2, ensure_ascii=False))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n[Saved] JSON written to {out_path}")

    return 0 if data["score"] else 1


if __name__ == "__main__":
    sys.exit(main())
