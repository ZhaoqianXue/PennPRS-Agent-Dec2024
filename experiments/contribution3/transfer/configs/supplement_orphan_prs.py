"""
Supplement trait_bundle_index.json with orphan PRS.

78 PRS (PGS005252-PGS005400 range) exist in the AUC matrices but are absent
from pgs_all_metadata_scores.csv (metadata snapshot version mismatch), so the
bundle builder never assigned them to any bundle. This script:

  1. Identifies orphan PRS (in AUC matrix, not in any bundle)
  2. Maps them to disease traits via Genetic_Agent/disease_preprocess/pgs_id_list_binary_combined.csv
  3. Maps 2 blood-pressure PRS via the measurement preprocess pgs_id_list CSV
  4. Adds each orphan PRS to the matching existing bundle(s)
  5. Writes updated trait_bundle_index.json

Usage:
  python experiments/contribution3/transfer/configs/supplement_orphan_prs.py
"""
from __future__ import annotations

import ast
import csv
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
BUNDLE_INDEX = (
    PROJECT_ROOT
    / "experiments"
    / "contribution3"
    / "transfer"
    / "runs"
    / "tool_calling_agent"
    / "trait_bundle_index.json"
)
ROOTCODE_MATRIX = (
    PROJECT_ROOT
    / "Genetic_Agent"
    / "result"
    / "aou_binary"
    / "prs_adjauc_matrix_binary_combined_rootcode.csv"
)
EXTEND_MATRIX = (
    PROJECT_ROOT
    / "Genetic_Agent"
    / "result"
    / "aou_extend_trait"
    / "prs_adjauc_matrix_binary_extend.csv"
)
DISEASE_ID_LIST = (
    PROJECT_ROOT
    / "Genetic_Agent"
    / "disease_preprocess"
    / "pgs_id_list_binary_combined.csv"
)

# ── Curated mapping: disease preprocess ontology name → existing bundle_id(s) ──
# Built by matching ontology names in pgs_id_list_binary_combined.csv to
# canonical_label values in trait_bundle_index.json.
ONTOLOGY_TO_BUNDLES: dict[str, list[str]] = {
    "aortic stenosis": ["efo_0009531"],                      # aortic valve disease
    "aortic valve disease": ["efo_0009531"],                  # aortic valve disease
    "atrial fibrillation": ["efo_0000275"],                   # atrial fibrillation
    "coronary artery disease": ["efo_0001645"],               # coronary artery disease
    "coronary atherosclerosis": ["mondo_0021661"],            # coronary atherosclerosis
    "dermatitis": ["mondo_0002406"],                          # dermatitis
    "graves disease": ["efo_0009189"],                        # hyperthyroidism (closest)
    "hashimoto's thyroiditis": ["efo_0004705"],               # hypothyroidism
    "heart disease": ["efo_0003777"],                         # heart disease
    "heart failure": ["efo_0003144"],                         # heart failure
    "hyperthyroidism": ["efo_0009189"],                       # hyperthyroidism
    "hypothyroidism": ["efo_0004705"],                        # hypothyroidism
    "nodular goiter": ["mondo_0000334", "mondo_0001658"],     # multinodular + nontoxic goiter
    "post-traumatic stress disorder": ["efo_0006788"],        # anxiety disorder (closest)
    "anxiety disorder": ["efo_0006788"],                      # anxiety disorder
    "psoriasis": ["efo_0000676"],                             # psoriasis
    "thyroid carcinoma": ["efo_0002892"],                     # thyroid carcinoma
    "type 1 diabetes mellitus": ["mondo_0005147"],            # type 1 diabetes mellitus
    "type 2 diabetes mellitus": ["mondo_0005148"],            # type 2 diabetes mellitus
}

# Blood-pressure PRS not in the disease CSV — mapped manually.
MANUAL_SUPPLEMENT: dict[str, list[str]] = {
    "PGS005350": ["efo_0006335"],   # systolic blood pressure
    "PGS005351": ["efo_0006336"],   # diastolic blood pressure
}


def _matrix_prs_ids(path: Path) -> set[str]:
    """Read PRS IDs from the first row of an AUC matrix CSV."""
    header = path.read_text().split("\n", 1)[0]
    ids: set[str] = set()
    for col in header.split(",")[1:]:
        pid = col.strip().replace("_hmPOS_GRCh38", "")
        if pid.startswith("PGS"):
            ids.add(pid)
    return ids


def _bundled_prs(bundles: list[dict]) -> set[str]:
    out: set[str] = set()
    for b in bundles:
        out.update(b["candidate_pgs_ids"])
    return out


def _load_disease_orphan_map(orphans: set[str]) -> dict[str, set[str]]:
    """Parse disease CSV → {orphan_pgs_id: set of ontology names}."""
    mapping: dict[str, set[str]] = {o: set() for o in orphans}
    with open(DISEASE_ID_LIST) as f:
        reader = csv.DictReader(f)
        for row in reader:
            ontology = row["ontology"].strip()
            try:
                pgs_ids = ast.literal_eval(row["pgs_ids"])
            except (ValueError, SyntaxError):
                continue
            for pid in pgs_ids:
                if pid in orphans:
                    mapping[pid].add(ontology)
    return mapping


def main() -> None:
    bundles = json.loads(BUNDLE_INDEX.read_text("utf-8"))
    bundle_by_id = {b["bundle_id"]: b for b in bundles}
    already = _bundled_prs(bundles)

    # Collect PRS from AUC matrices
    auc_prs: set[str] = set()
    for mpath in (ROOTCODE_MATRIX, EXTEND_MATRIX):
        if mpath.exists():
            auc_prs |= _matrix_prs_ids(mpath)

    orphans = auc_prs - already
    if not orphans:
        print("No orphan PRS found — bundle index is already complete.")
        return

    print(f"Found {len(orphans)} orphan PRS (in AUC matrix, not in any bundle)")

    # Map orphans to disease traits
    disease_map = _load_disease_orphan_map(orphans)

    # Resolve orphan → bundle_id assignments
    assignments: dict[str, set[str]] = {o: set() for o in orphans}
    for pgs_id, traits in disease_map.items():
        for trait in traits:
            tl = trait.lower().strip()
            if tl in ONTOLOGY_TO_BUNDLES:
                assignments[pgs_id].update(ONTOLOGY_TO_BUNDLES[tl])

    # Apply manual supplements (blood-pressure PRS)
    for pgs_id, bids in MANUAL_SUPPLEMENT.items():
        if pgs_id in orphans:
            assignments[pgs_id].update(bids)

    # Add orphans to bundles
    added = 0
    unresolved = []
    for pgs_id in sorted(orphans):
        target_bids = assignments.get(pgs_id, set())
        if not target_bids:
            unresolved.append(pgs_id)
            continue
        for bid in sorted(target_bids):
            bundle = bundle_by_id.get(bid)
            if bundle is None:
                print(f"  WARNING: bundle {bid} not found for {pgs_id}")
                continue
            if pgs_id not in bundle["candidate_pgs_ids"]:
                bundle["candidate_pgs_ids"].append(pgs_id)
                bundle["candidate_pgs_ids"].sort()
                bundle["n_models"] = len(bundle["candidate_pgs_ids"])
                added += 1
                print(f"  {pgs_id} -> {bid} ({bundle['canonical_label']})")

    if unresolved:
        print(f"\n  UNRESOLVED ({len(unresolved)}): {unresolved}")

    # Write back
    bundles.sort(key=lambda b: b["bundle_id"])
    BUNDLE_INDEX.write_text(json.dumps(bundles, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(f"\nDone: added {added} PRS-bundle assignments. Updated {BUNDLE_INDEX.name}")


if __name__ == "__main__":
    main()
