#!/usr/bin/env python3
"""
Fetch PGS Catalog metadata for a given PRS model (standalone version).

This script is self-contained and does not import project modules.

Usage:
    python scripts/utilities/fetch_pgs_model_standalone.py [PGS_ID]
    python scripts/utilities/fetch_pgs_model_standalone.py PGS003852
    python scripts/utilities/fetch_pgs_model_standalone.py PGS003852 -o output/pgs_model.json

Output:
    - Pretty-prints full data to stdout
    - Optionally writes merged JSON to file (--output / -o)
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
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


def _request_json(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    query = f"?{urlencode(params, doseq=True)}" if params else ""
    url = f"{BASE_URL}{path}{query}"
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch all PGS Catalog metadata for a PRS model (standalone)."
    )
    parser.add_argument(
        "pgs_id",
        nargs="?",
        default="PGS003852",
        help="PGS Catalog ID (e.g. PGS003852). Default: PGS003852",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write merged JSON to this file (e.g. output/pgs_model.json)",
    )
    args = parser.parse_args()

    pgs_id = args.pgs_id.strip()
    if not pgs_id.upper().startswith("PGS"):
        pgs_id = f"PGS{pgs_id}"

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

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n[Saved] JSON written to {out_path}")

    return 0 if data["score"] else 1


if __name__ == "__main__":
    sys.exit(main())
