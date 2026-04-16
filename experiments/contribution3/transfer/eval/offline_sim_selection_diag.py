"""Diagnose why 25 targets are always missed: what gets selected vs oracle?"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution3.transfer.eval.offline_sim_selection_80 import (
    load_data, score_linear, _extract_fields, _cards_from_row,
    UNIFIED_RESULTS, UNIFIED_DOSSIERS,
)
from experiments.contribution3.transfer.eval.shortlist_recall import build_shortlist_recall_rows
from experiments.contribution3.transfer.agent import UNIFIED_CONFIG


def main():
    prepared, unreachable = load_data()
    total = len(prepared)

    # Use best linear weights from optimization
    w = (2.929, 0.0135, 0.3514, 1.4729, 0.9624, 0.1757, 1.7909)

    print(f"Prepared: {total}, unreachable: {len(unreachable)}\n")

    # Classify each target
    bmi_id = "efo_0004340"
    oracle_is_bmi = 0
    selected_is_bmi = 0
    oracle_bmi_hit = 0
    oracle_nonbmi_hit = 0
    oracle_nonbmi_miss = 0

    always_missed = {'C22', 'C54', 'C56', 'D04', 'D05', 'D50', 'E79', 'F22', 'F60',
                     'I11', 'I27', 'I44', 'J96', 'K02', 'K04', 'K21', 'K85', 'L05',
                     'L57', 'N10', 'N25', 'N52', 'N84', 'Q23', 'S52'}

    print("=" * 120)
    print(f"{'TID':<6} {'Oracle':>15} {'Selected':>15} {'Status':<8} "
          f"{'O.Prior':>7} {'S.Prior':>7} {'O.Fid':>6} {'S.Fid':>6} "
          f"{'O.OT':>6} {'S.OT':>6} {'O.GCrg':>7} {'S.GCrg':>7} "
          f"{'O.Scr':>8} {'S.Scr':>8} {'O.nMod':>6} {'S.nMod':>6}")
    print("-" * 120)

    for tid, oracle_id, fields_by_id in sorted(prepared, key=lambda x: x[0]):
        best_id = max(fields_by_id, key=lambda bid: score_linear(fields_by_id[bid], w))
        hit = best_id == oracle_id
        of = fields_by_id[oracle_id]
        sf = fields_by_id[best_id]
        os = score_linear(of, w)
        ss = score_linear(sf, w)

        if of["bundle_id"] == bmi_id:
            oracle_is_bmi += 1
        if sf["bundle_id"] == bmi_id:
            selected_is_bmi += 1

        if hit:
            if of["bundle_id"] == bmi_id:
                oracle_bmi_hit += 1
            else:
                oracle_nonbmi_hit += 1
        else:
            oracle_nonbmi_miss += 1

        marker = "HIT" if hit else ("MISS*" if tid in always_missed else "MISS")
        print(f"{tid:<6} {oracle_id[:15]:>15} {best_id[:15]:>15} {marker:<8} "
              f"{of['prior']:>7.3f} {sf['prior']:>7.3f} {of['fidelity']:>6.3f} {sf['fidelity']:>6.3f} "
              f"{of['ot_overlap']:>6.2f} {sf['ot_overlap']:>6.2f} {of['gc_rg']:>7.3f} {sf['gc_rg']:>7.3f} "
              f"{os:>8.4f} {ss:>8.4f} {of['n_models']:>6} {sf['n_models']:>6}")

    print()
    print(f"Oracle is BMI: {oracle_is_bmi}/{total}")
    print(f"Selected is BMI: {selected_is_bmi}/{total}")
    print(f"Oracle=BMI & HIT: {oracle_bmi_hit}")
    print(f"Oracle≠BMI & HIT: {oracle_nonbmi_hit}")
    print(f"Oracle≠BMI & MISS: {oracle_nonbmi_miss}")

    # For always-missed targets: what's the score gap?
    print(f"\n{'='*80}")
    print("Always-missed targets: oracle score vs best score, and score rank of oracle")
    print(f"{'='*80}")
    for tid, oracle_id, fields_by_id in sorted(prepared, key=lambda x: x[0]):
        if tid not in always_missed:
            continue
        scores = {bid: score_linear(fields_by_id[bid], w) for bid in fields_by_id}
        oracle_score = scores[oracle_id]
        # Rank of oracle
        sorted_scores = sorted(scores.values(), reverse=True)
        oracle_rank = sorted_scores.index(oracle_score) + 1
        best_id = max(scores, key=scores.get)
        best_score = scores[best_id]
        of = fields_by_id[oracle_id]
        sf = fields_by_id[best_id]

        print(f"\n{tid}: oracle={oracle_id}, rank={oracle_rank}/{len(scores)}, "
              f"gap={best_score-oracle_score:.4f}")
        print(f"  Oracle:   prior={of['prior']:.3f} fid={of['fidelity']:.3f} util={of['utility']:.3f} "
              f"cheap={of['cheap']:.3f} ot={of['ot_overlap']:.2f} gc={of['gc_rg']:.3f}(sig={of['gc_significant']}) "
              f"nmod={of['n_models']} endpoint={of['is_same_endpoint']} concordant={of['concordant']}")
        print(f"  Selected: prior={sf['prior']:.3f} fid={sf['fidelity']:.3f} util={sf['utility']:.3f} "
              f"cheap={sf['cheap']:.3f} ot={sf['ot_overlap']:.2f} gc={sf['gc_rg']:.3f}(sig={sf['gc_significant']}) "
              f"nmod={sf['n_models']} endpoint={sf['is_same_endpoint']} concordant={sf['concordant']}")
        # What features does oracle win on?
        wins = []
        if of['prior'] > sf['prior']: wins.append('prior')
        if of['fidelity'] > sf['fidelity']: wins.append('fidelity')
        if of['utility'] > sf['utility']: wins.append('utility')
        if of['ot_overlap'] > sf['ot_overlap']: wins.append('ot_overlap')
        if of['gc_rg'] > sf['gc_rg']: wins.append('gc_rg')
        if of['n_models'] < sf['n_models'] and sf['n_models'] > 50: wins.append('fewer_models')
        if of['concordant'] and not sf['concordant']: wins.append('concordant')
        if of['is_same_endpoint'] and not sf['is_same_endpoint']: wins.append('same_endpoint')
        print(f"  Oracle wins on: {wins if wins else 'NOTHING'}")

    # Check: for "always missed" targets, is there ANY single feature where oracle > selected?
    print(f"\n{'='*80}")
    print("Feature dominance: can oracle EVER beat selected on any feature?")
    print(f"{'='*80}")
    can_win = Counter()
    never_win = []
    for tid, oracle_id, fields_by_id in sorted(prepared, key=lambda x: x[0]):
        if tid not in always_missed:
            continue
        best_id = max(fields_by_id, key=lambda bid: score_linear(fields_by_id[bid], w))
        of = fields_by_id[oracle_id]
        sf = fields_by_id[best_id]
        wins = []
        for feat in ['prior', 'fidelity', 'utility', 'cheap', 'ot_overlap', 'gc_rg']:
            if of[feat] > sf[feat]:
                wins.append(feat)
                can_win[feat] += 1
        if of['concordant'] and not sf['concordant']:
            wins.append('concordant')
            can_win['concordant'] += 1
        if of['is_same_endpoint'] and not sf['is_same_endpoint']:
            wins.append('same_endpoint')
            can_win['same_endpoint'] += 1
        if not wins:
            never_win.append(tid)

    print(f"Feature-level wins: {dict(can_win)}")
    print(f"Oracle wins on NOTHING (Pareto-dominated): {never_win} ({len(never_win)}/{len(always_missed)})")

    # Also check: what if we use the FULL dossier for scoring, not just shortlist?
    # The shortlist restricts which bundles can be selected.
    # But is the oracle perhaps just not competitive on ANY feature?
    print(f"\n{'='*80}")
    print("Selected bundle distribution across always-missed")
    print(f"{'='*80}")
    selected_dist = Counter()
    for tid, oracle_id, fields_by_id in sorted(prepared, key=lambda x: x[0]):
        if tid not in always_missed:
            continue
        best_id = max(fields_by_id, key=lambda bid: score_linear(fields_by_id[bid], w))
        selected_dist[best_id] += 1
    for bid, count in selected_dist.most_common(10):
        print(f"  {bid}: selected {count}x")


if __name__ == "__main__":
    main()
