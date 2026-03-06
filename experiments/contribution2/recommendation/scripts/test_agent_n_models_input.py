"""
Test that when searching union CSV ontologies with the evaluated PGS whitelist,
the Agent receives exactly the N Models (evaluated PGS IDs) as input.

Compares prs_model_pgscatalog_search(ontology, evaluated_pgs_whitelist=whitelist)
output against evaluated_pgs_per_ontology.json for each ontology.

Usage:
  python experiments/contribution2/scripts/test_agent_n_models_input.py
  python experiments/contribution2/scripts/test_agent_n_models_input.py --limit 3  # Quick test
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

# Add project root to path (contribution2/recommendation/scripts -> repo root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CONTRIB2_DIR = Path(__file__).parent.parent.parent
UNION_CSV = CONTRIB2_DIR / "disease_selection" / "runs" / "selected_diseases_contribution2_union.csv"
EVALUATED_JSON = Path(__file__).parent.parent / "runs" / "evaluated_pgs_per_ontology.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Agent receives N Models for union CSV ontologies")
    parser.add_argument("--limit", type=int, default=None, help="Test only first N ontologies (avoids API rate limits)")
    args = parser.parse_args()
    if not UNION_CSV.exists():
        print(f"Union CSV not found: {UNION_CSV}")
        return 1
    if not EVALUATED_JSON.exists():
        print(f"Evaluated PGS JSON not found: {EVALUATED_JSON}")
        print("Run: python experiments/contribution2/recommendation/configs/generate_evaluated_pgs_list.py")
        return 1

    union_df = pd.read_csv(UNION_CSV)
    with open(EVALUATED_JSON, encoding="utf-8") as f:
        evaluated = json.load(f)

    from src.server.core.pgs_catalog_client import PGSCatalogClient
    from src.server.core.tools.prs_model_tools import prs_model_pgscatalog_search

    client = PGSCatalogClient()
    passed = 0
    failed: list[dict] = []

    rows = list(union_df.iterrows())
    if args.limit:
        rows = rows[: args.limit]
        print(f"Testing first {args.limit} ontologies only (--limit {args.limit})\n")

    for _, row in rows:
        ontology = str(row.get("Ontology", "")).strip()
        n_models_csv = row.get("N Models", "")
        expected_ids = set(evaluated.get(ontology.lower(), []))

        if not expected_ids:
            print(f"  [SKIP] {ontology}: no evaluated PGS in JSON")
            continue

        whitelist = expected_ids
        result = prs_model_pgscatalog_search(
            client,
            ontology,
            evaluated_pgs_whitelist=whitelist,
        )
        returned_ids = {m.id for m in result.models}

        if returned_ids == expected_ids:
            passed += 1
            print(f"  [OK]   {ontology}: {len(returned_ids)} models match N Models")
        else:
            missing = expected_ids - returned_ids
            extra = returned_ids - expected_ids
            failed.append({
                "ontology": ontology,
                "n_models_csv": n_models_csv,
                "expected": len(expected_ids),
                "returned": len(returned_ids),
                "missing": missing,
                "extra": extra,
            })
            print(f"  [FAIL] {ontology}: expected {len(expected_ids)}, got {len(returned_ids)}")
            if missing:
                print(f"         Missing from Agent input: {sorted(missing)[:5]}{'...' if len(missing) > 5 else ''}")
            if extra:
                print(f"         Extra in Agent input: {sorted(extra)[:5]}{'...' if len(extra) > 5 else ''}")

    total = len(rows)
    print()
    print(f"Result: {passed}/{total} ontologies pass (Agent input == N Models)")
    if failed:
        print(f"Failed: {[f['ontology'] for f in failed]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
