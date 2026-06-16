#!/usr/bin/env python3
"""LORO + 2x2 ablation analysis for the EFO-clean 44-disease within-trait benchmark.

Consumes the run summaries produced by Phase B (auto-discovered, missing runs
skipped) and emits a markdown report:
  1. Hit@1 master table across all arms (full skill / arm3 / arm4 / each LORO
     / General LLM / reported-max).
  2. Section-dissociation: Hit@1 delta vs full-skill per ablated section.
  3. Per-disease flip matrix across all LORO runs (separates a section-driven
     flip — flips only when THAT section is removed — from sampling noise that
     flips across unrelated sections too).
  4. LORO x offline-ledger concordance (honest overlap, not forced): of the
     section-2 right->wrong flips, how many were ledger-flagged skill_decisive.

Final pick per disease = per_disease[].modal_recommendation; Hit@1 =
modal_recommendation_rank == 1 (t=1, so modal == the single trial).
"""
import csv
import glob
import json
import os
from pathlib import Path

ROOT = Path("/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent")
RUNS = ROOT / "experiments/contribution2/recommendation/runs"
LEDGER = ROOT / "experiments/contribution2/recommendation/transparency/ledgers/_summary.csv"
OUT = ROOT / "experiments/contribution2/recommendation/transparency/loro_ablation/results/LORO_REPORT.md"

SECTIONS = ["cross", "1", "2", "3", "4", "5", "6", "7"]
SEC_LABEL = {
    "cross": "§0 cross-cutting", "1": "§1 predicted_trait",
    "2": "§2 performance_metrics", "3": "§3 gwas_source",
    "4": "§4 score_training", "5": "§5 dev_method",
    "6": "§6 variants", "7": "§7 pgs_source",
}


def _newest(pattern):
    hits = sorted(glob.glob(str(RUNS / pattern)), key=os.path.getmtime, reverse=True)
    return hits[0] if hits else None


def _load_summary(path, fname):
    if not path:
        return None
    p = Path(path) / fname
    if not p.exists():
        return None
    return json.load(open(p))


def picks(summary):
    """disease -> {pick, rank, hit1} from a topk/with_domain summary."""
    out = {}
    for d in (summary or {}).get("per_disease", []):
        rank = d.get("modal_recommendation_rank")
        out[d["ontology"]] = {
            "pick": d.get("modal_recommendation"),
            "rank": rank,
            "hit1": (rank == 1),
        }
    return out


def hit1_count(pk):
    return sum(1 for v in pk.values() if v["hit1"])


def cost_of(summary):
    return (summary or {}).get("cost", {}).get("estimated_total_cost_usd")


def main():
    # ---- discover runs ----
    ref_dir = _newest("topk-holistic-rerank-batch-gpt-5.4-t1__44disease__efoclean44-skillv2-2*")
    arm3_dir = _newest("topk-holistic-rerank-batch-gpt-5.4-t1__44disease__efoclean44-noskill-2stage-*")
    # prefer the byte-clean 7-section arm4 re-run; fall back to the original
    arm4_dir = (_newest("with-domain-gpt-5.4-t1__44disease__efoclean44-skillv2-singleshot-7sec")
                or _newest("with-domain-gpt-5.4-t1__44disease__efoclean44-skillv2-singleshot"))
    genllm_dir = _newest("without-domain-gpt-5.4-t1__44disease__efoclean44")
    loro_dirs = {s: _newest(f"topk-holistic-rerank-batch-gpt-5.4-t1__44disease__efoclean44-skillv2-loro-no-{s}-*")
                 for s in SECTIONS}

    TOPK_SUM = "experiment_topk_holistic_rerank_batch_summary.json"
    ref = _load_summary(ref_dir, TOPK_SUM)
    arm3 = _load_summary(arm3_dir, TOPK_SUM)
    arm4 = _load_summary(arm4_dir, "experiment_with_domain_summary.json")
    genllm = _load_summary(genllm_dir, "experiment_without_domain_summary.json")
    loro = {s: _load_summary(loro_dirs[s], TOPK_SUM) for s in SECTIONS}

    ref_pk = picks(ref)
    N = len(ref_pk) or 44

    # ---- ledger ----
    ledger = {}
    if LEDGER.exists():
        for r in csv.DictReader(open(LEDGER)):
            ledger[r["disease"]] = {
                "skill_decisive": str(r.get("skill_decisive")).lower() in ("true", "1"),
                "hit1": str(r.get("hit1")).lower() in ("true", "1"),
            }

    lines = ["# LORO + 2×2 ablation — EFO-clean 44-disease (gpt-5.4, t=1, batch)\n"]

    # ---- 1. master Hit@1 table ----
    lines.append("## 1. Hit@1 master table\n")
    lines.append("| Arm | harness | skill | Hit@1 | n/44 | Δ vs full | cost |")
    lines.append("|---|---|---|---:|---:|---:|---:|")
    ref_h = hit1_count(ref_pk) if ref else None

    def row(name, harness, skill, pk, summary):
        if pk is None:
            return f"| {name} | {harness} | {skill} | — | — | (pending) | — |"
        h = hit1_count(pk)
        d = f"{(h-ref_h)/N*100:+.1f}pp" if ref_h is not None else "—"
        c = cost_of(summary)
        return f"| {name} | {harness} | {skill} | {h/N*100:.1f}% | {h}/{N} | {d} | {('$'+format(c,'.2f')) if c else '—'} |"

    lines.append(row("PRS Agent (full)", "2-stage", "full", ref_pk, ref))
    lines.append(row("arm3 (harness−skill)", "2-stage", "empty", picks(arm3) if arm3 else None, arm3))
    lines.append(row("arm4 (skill−harness)", "single", "full", picks(arm4) if arm4 else None, arm4))
    for s in SECTIONS:
        lines.append(row(f"LORO −{SEC_LABEL[s]}", "2-stage", f"full−{s}", picks(loro[s]) if loro[s] else None, loro[s]))
    # General LLM + reported-max from genllm summary
    if genllm:
        gh = hit1_count(picks(genllm))
        lines.append(f"| General LLM | single | none | {gh/N*100:.1f}% | {gh}/{N} | {(gh-ref_h)/N*100:+.1f}pp | ${cost_of(genllm):.2f} |")
        b = genllm.get("baseline", {})
        bh = b.get("hits") or b.get("hit_at_k", {}).get("1", {}).get("hits")
        if bh is not None:
            lines.append(f"| reported-max | none | none | {bh/N*100:.1f}% | {bh}/{N} | {(bh-ref_h)/N*100:+.1f}pp | $0 |")
    lines.append("")

    # ---- 2. section dissociation ----
    lines.append("## 2. Section dissociation (Hit@1 Δ vs full skill)\n")
    lines.append("Hypothesis: −§2 drops toward General-LLM (20.4%); irrelevant sections ≈ unchanged.\n")
    lines.append("| ablated section | Hit@1 | Δ vs full | right→wrong | wrong→right | n flipped |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    flip_by_sec = {}
    for s in SECTIONS:
        pk = picks(loro[s]) if loro[s] else None
        if pk is None:
            lines.append(f"| {SEC_LABEL[s]} | — | (pending) | — | — | — |")
            continue
        h = hit1_count(pk)
        r2w = w2r = nflip = 0
        flips = {}
        for dis, rv in ref_pk.items():
            lv = pk.get(dis)
            if not lv:
                continue
            if lv["pick"] != rv["pick"]:
                nflip += 1
                flips[dis] = (rv, lv)
            if rv["hit1"] and not lv["hit1"]:
                r2w += 1
            if (not rv["hit1"]) and lv["hit1"]:
                w2r += 1
        flip_by_sec[s] = flips
        lines.append(f"| {SEC_LABEL[s]} | {h/N*100:.1f}% | {(h-ref_h)/N*100:+.1f}pp | {r2w} | {w2r} | {nflip} |")
    lines.append("")

    # ---- 3. per-disease flip matrix (section-driven vs noise) ----
    lines.append("## 3. Per-disease pick-flip matrix (✗ = pick changed vs full skill)\n")
    lines.append("A flip under ONE section (esp. §2) = section-driven; flips scattered across "
                 "unrelated sections = t=1 sampling noise.\n")
    avail = [s for s in SECTIONS if loro[s]]
    if avail:
        hdr = "| disease | full pick (rank) | ledger SD |" + "".join(f" −{s} |" for s in avail)
        lines.append(hdr)
        lines.append("|---|---|---|" + "|".join(["---"] * len(avail)) + "|")
        for dis in sorted(ref_pk):
            rv = ref_pk[dis]
            sd = "✓" if ledger.get(dis, {}).get("skill_decisive") else ""
            cells = []
            for s in avail:
                pk = picks(loro[s])
                lv = pk.get(dis)
                if not lv:
                    cells.append("?")
                elif lv["pick"] != rv["pick"]:
                    cells.append(f"✗→r{lv['rank']}")
                else:
                    cells.append("·")
            lines.append(f"| {dis} | {rv['pick']} (r{rv['rank']}) | {sd} | " + " | ".join(cells) + " |")
        lines.append("")

    # ---- 4. LORO x ledger concordance (honest) ----
    if loro.get("2"):
        lines.append("## 4. −§2 flips × offline decision-ledger (honest concordance)\n")
        pk2 = picks(loro["2"])
        r2w_dis = [d for d in ref_pk if ref_pk[d]["hit1"] and pk2.get(d) and not pk2[d]["hit1"]]
        sd_set = {d for d in ledger if ledger[d]["skill_decisive"]}
        overlap = [d for d in r2w_dis if d in sd_set]
        lines.append(f"- −§2 right→wrong flips: **{len(r2w_dis)}** — {r2w_dis}")
        lines.append(f"- of those, ledger-flagged skill_decisive: **{len(overlap)}/{len(r2w_dis)}** — {overlap}")
        lines.append(f"- (ledger skill_decisive total = {len(sd_set)}/44; this is an ATTRIBUTION oracle, "
                     f"so converged-but-attributed cases need not flip — partial overlap is expected & honest)")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")
    print("\n".join(lines[:40]))


if __name__ == "__main__":
    main()
