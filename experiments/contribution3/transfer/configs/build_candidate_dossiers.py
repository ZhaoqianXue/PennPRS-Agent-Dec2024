from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.common import (
    BENCHMARK_FAMILIES,
    BUNDLE_INDEX_JSON,
    build_candidate_dossiers,
    build_trait_bundle_index,
    load_trait_bundle_index,
    target_dossiers_json,
    write_candidate_dossiers,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build benchmark-family-specific candidate dossiers for Contribution3.",
    )
    parser.add_argument(
        "--benchmark-family",
        choices=BENCHMARK_FAMILIES,
        default="binary_to_binary",
    )
    args = parser.parse_args()

    if BUNDLE_INDEX_JSON.exists():
        bundles = load_trait_bundle_index(BUNDLE_INDEX_JSON)
    else:
        bundles = build_trait_bundle_index()
    dossiers = build_candidate_dossiers(bundles, benchmark_family=args.benchmark_family)
    outpath = target_dossiers_json(args.benchmark_family)
    write_candidate_dossiers(dossiers, outpath)
    print(f"Wrote {len(dossiers)} candidate dossiers -> {outpath}")


if __name__ == "__main__":
    main()
