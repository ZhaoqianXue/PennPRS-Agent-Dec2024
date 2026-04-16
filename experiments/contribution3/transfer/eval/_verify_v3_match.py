"""Verify that agent.py v3 scoring matches offline sim (34/74).

Loads the frozen run artifacts, scores every card using agent.py's
_selection_priority_score, and compares the argmax to the offline sim's
DE-optimized weight vector applied to the 38-feature matrix.
"""
from __future__ import annotations
import csv, json, math, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.agent import (
    UNIFIED_CONFIG as cfg,
    _selection_priority_score,
)
from experiments.contribution3.transfer.prompts.transfer_prompt import (
    CandidateEvidenceCard,
    GeneticCorrelationEvidence,
    HeritabilityEvidence,
    OpenTargetsEvidence,
    TraitResolution,
)

RUN_DIR = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "all-tools__20260413_225653"
)


def _dummy_resolution(system: str = "gwas_atlas") -> TraitResolution:
    return TraitResolution(query="", system=system)


def build_card_from_light(c: dict) -> CandidateEvidenceCard:
    """Reconstruct a CandidateEvidenceCard from cards_light.json entry."""
    gc_rg_raw = c["gc_rg"] if c["gc_sig"] or c["gc_z"] > 0 else None
    gc = None
    if gc_rg_raw is not None or c["gc_z"] > 0:
        gc = GeneticCorrelationEvidence(
            target_resolution=_dummy_resolution("gwas_atlas"),
            candidate_resolution=_dummy_resolution("gwas_atlas"),
            pair_status="matched",
            rg=gc_rg_raw,
            z_score=c["gc_z"] if c["gc_z"] > 0 else None,
            p_value=0.001 if c["gc_sig"] else 0.5,
        )

    ot = OpenTargetsEvidence(
        target_resolution=_dummy_resolution("open_targets"),
        candidate_resolution=_dummy_resolution("open_targets"),
        pair_status="matched",
        weighted_shared_target_overlap_score=c["ot_ov"],
        shared_target_count=c["ot_sc"],
        therapeutic_area_match=c["ot_area"],
        shared_ancestor_count=c["ot_anc"],
        phenotype_overlap_score=c["ot_ph"],
        genetic_support_present=c["ot_gen"],
    )

    h2 = HeritabilityEvidence(
        shared_signal_ceiling_proxy=c["h2_ceil"],
    )

    return CandidateEvidenceCard(
        bundle_id=c["bid"],
        canonical_label=c["bid"],
        bundle_type="trait",
        n_models=c["n_mod"],
        archetype=c["arch"],
        phenotype_fidelity=c["arch"],
        phenotype_fidelity_score=c["fid"],
        lexical_match_score=c["lex"],
        shared_token_count=c["stok"],
        cheap_rank_score=c["cheap"],
        utility_score=c["util"],
        transferability_prior_score=c["prior"],
        gc=gc,
        h2=h2,
        open_targets=ot,
    )


def main():
    raw = json.loads((RUN_DIR / "cards_light.json").read_text())
    oracle_info = {}
    with open(RUN_DIR / "shortlist_recall.csv") as f:
        for r in csv.DictReader(f):
            oracle_info[r["target_id"]] = {
                "oid": r["transfer_eligible_global_oracle_bundle_id"],
                "in_sl": r["oracle_in_shortlist"] == "True",
            }

    hits, total = 0, 0
    mismatches = []
    for entry in raw:
        tid = entry["tid"]
        if entry.get("outcome") != "MATCHED":
            continue
        info = oracle_info.get(tid, {})
        oid = info.get("oid")
        if not oid or not info.get("in_sl"):
            continue
        bids = [c["bid"] for c in entry["cards"]]
        if oid not in bids:
            continue
        total += 1

        # Score using agent.py
        cards = [build_card_from_light(c) for c in entry["cards"]]
        scores = [_selection_priority_score(card, cfg) for card in cards]
        best_idx = max(range(len(scores)), key=lambda i: scores[i])
        selected_bid = cards[best_idx].bundle_id

        if selected_bid == oid:
            hits += 1
        else:
            oracle_idx = bids.index(oid)
            mismatches.append({
                "tid": tid,
                "oracle": oid,
                "selected": selected_bid,
                "oracle_score": scores[oracle_idx],
                "selected_score": scores[best_idx],
                "gap": scores[best_idx] - scores[oracle_idx],
            })

    print(f"Agent.py v3 scoring: {hits}/{total}")
    print(f"Expected (offline sim): 34/74")
    print(f"Match: {'YES' if hits == 34 else 'NO'}")

    if hits != 34:
        print(f"\nMismatches ({len(mismatches)}):")
        missed_tids = sorted([m["tid"] for m in mismatches])
        print(f"Missed: {missed_tids}")

        # Show closest misses
        mismatches.sort(key=lambda m: m["gap"])
        for m in mismatches[:10]:
            print(f"  {m['tid']}: oracle={m['oracle']} score={m['oracle_score']:.6f}, "
                  f"selected={m['selected']} score={m['selected_score']:.6f}, gap={m['gap']:.6f}")
    else:
        missed_tids = sorted([m["tid"] for m in mismatches])
        print(f"Missed: {missed_tids}")


if __name__ == "__main__":
    main()
