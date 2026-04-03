from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.common import (
    BUNDLE_INDEX_JSON,
    build_trait_bundle_index,
    write_trait_bundle_index,
)


def main() -> None:
    bundles = build_trait_bundle_index()
    write_trait_bundle_index(bundles, BUNDLE_INDEX_JSON)
    print(f"Wrote {len(bundles)} trait bundles -> {BUNDLE_INDEX_JSON}")


if __name__ == "__main__":
    main()
