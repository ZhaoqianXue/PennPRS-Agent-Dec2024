from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.common import (
    BUNDLE_INDEX_JSON,
    TARGET_DOSSIERS_JSON,
    build_candidate_dossiers,
    build_trait_bundle_index,
    load_trait_bundle_index,
    write_candidate_dossiers,
)


def main() -> None:
    if BUNDLE_INDEX_JSON.exists():
        bundles = load_trait_bundle_index(BUNDLE_INDEX_JSON)
    else:
        bundles = build_trait_bundle_index()
    dossiers = build_candidate_dossiers(bundles)
    write_candidate_dossiers(dossiers, TARGET_DOSSIERS_JSON)
    print(f"Wrote {len(dossiers)} candidate dossiers -> {TARGET_DOSSIERS_JSON}")


if __name__ == "__main__":
    main()
