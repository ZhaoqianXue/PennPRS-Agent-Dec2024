#!/usr/bin/env python3
"""
Fetch all PGS Catalog metadata for a given PRS model (score details + performance).

Usage:
    python scripts/utilities/fetch_pgs_model.py [PGS_ID]
    python scripts/utilities/fetch_pgs_model.py PGS003852
    python scripts/utilities/fetch_pgs_model.py PGS003852 -o output/pgs_model.json

Output:
    - Pretty-prints full data to stdout
    - Optionally writes merged JSON to file (--output / -o)
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.server.core.pgs_catalog_client import PGSCatalogClient


def fetch_pgs_model(pgs_id: str) -> dict:
    """
    Fetch all available information for a PGS model from PGS Catalog REST API.

    Returns a dict with keys:
        - score: full metadata from /rest/score/{pgs_id}
        - performance: list of performance records from /rest/performance/search
    """
    client = PGSCatalogClient()
    score = client.get_score_details(pgs_id)
    performance = client.get_score_performance(pgs_id)

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
        description="Fetch all PGS Catalog metadata for a PRS model."
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
        pgs_id = f"PGS{pgs_id}"  # Allow "003852" -> "PGS003852"

    print(f"Fetching PGS model: {pgs_id}\n")
    data = fetch_pgs_model(pgs_id)

    # Pretty print to stdout
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

    # Save to file if requested
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n[Saved] JSON written to {out_path}")

    return 0 if data["score"] else 1


if __name__ == "__main__":
    sys.exit(main())
