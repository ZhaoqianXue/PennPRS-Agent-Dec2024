"""Extract minimal card data from results.json for fast offline simulation.

Produces a compact JSON with only the fields needed for scoring optimization.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RESULTS = (
    PROJECT_ROOT / "experiments/contribution3/transfer/runs/tool_calling_agent/unified"
    / "all-tools__20260413_225653/results.json"
)
OUT = RESULTS.parent / "cards_light.json"


def extract():
    print(f"Loading {RESULTS} ({RESULTS.stat().st_size / 1e6:.0f} MB)...")
    results = json.loads(RESULTS.read_text())
    print(f"  {len(results)} entries loaded.")

    compact = []
    for row in results:
        target = row.get("target") or {}
        tid = str(target.get("target_id") or "").strip()
        decision = row.get("decision") or {}
        outcome = decision.get("outcome")
        selected_id = decision.get("best_bundle_id")
        es = decision.get("evidence_state") or {}
        raw_cards = es.get("candidate_cards") or []

        cards = []
        for c in raw_cards:
            gc = c.get("gc") or {}
            ot = c.get("open_targets") or {}
            h2 = c.get("h2") or {}
            gc_rg_raw = gc.get("rg")
            gc_rg = abs(float(gc_rg_raw)) if gc_rg_raw is not None else 0.0
            gc_p = float(gc.get("p_value")) if gc.get("p_value") is not None else 1.0
            gc_z = abs(float(gc.get("z_score") or 0)) if gc.get("z_score") is not None else 0.0
            gc_sig = gc_p < 0.05 if gc_rg_raw is not None else False

            ot_overlap = float(ot.get("weighted_shared_target_overlap_score") or 0)
            ot_shared = int(ot.get("shared_target_count") or 0)
            ot_area = bool(ot.get("therapeutic_area_match"))
            ot_anc = int(ot.get("shared_ancestor_count") or 0)
            ot_pheno = float(ot.get("phenotype_overlap_score") or 0)
            ot_genetic = bool(ot.get("genetic_support_present"))
            ot_supported = ot_overlap >= 0.20 and ot_shared >= 1

            h2_ceiling = float(h2.get("shared_signal_ceiling_proxy") or 0)

            cards.append({
                "bid": c.get("bundle_id"),
                "prior": c.get("transferability_prior_score", 0),
                "util": c.get("utility_score", 0),
                "cheap": c.get("cheap_rank_score", 0),
                "fid": c.get("phenotype_fidelity_score", 0),
                "n_mod": c.get("n_models", 0),
                "lex": c.get("lexical_match_score", 0),
                "stok": c.get("shared_token_count", 0),
                "arch": c.get("archetype", ""),
                "gc_rg": round(gc_rg, 4),
                "gc_p": round(gc_p, 6),
                "gc_z": round(gc_z, 3),
                "gc_sig": gc_sig,
                "ot_ov": round(ot_overlap, 4),
                "ot_sc": ot_shared,
                "ot_area": ot_area,
                "ot_anc": ot_anc,
                "ot_ph": round(ot_pheno, 4),
                "ot_gen": ot_genetic,
                "ot_sup": ot_supported,
                "h2_ceil": round(h2_ceiling, 6),
                "conc": gc_sig and ot_supported,
            })

        compact.append({
            "tid": tid,
            "outcome": outcome,
            "selected": selected_id,
            "cards": cards,
        })

    OUT.write_text(json.dumps(compact, separators=(",", ":")))
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB, {len(compact)} targets)")


if __name__ == "__main__":
    extract()
