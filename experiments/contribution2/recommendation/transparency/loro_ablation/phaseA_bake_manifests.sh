#!/usr/bin/env bash
# Phase A: bake the 8 LORO with-domain manifests LOCALLY (no OpenAI call).
# Per section: ablate deployed corpus -> with_domain --mode prepare -> RESTORE
# corpus + verify sha256 -> verify the baked manifest dropped exactly that
# section. Fail-loud: abort on any sha mismatch or bake-check failure so the
# deployed skill is never left ablated.
set -euo pipefail
cd /Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent

PY=".venv/bin/python"
CORPUS="src/server/core/skills/prs-model-recommendation/references/pgs_evidence_appraisal.md"
W="experiments/contribution2/recommendation/transparency/loro_ablation"
ORIG="$W/pgs_evidence_appraisal.ORIGINAL.md"
ORIG_SHA="f30de7e302e2508c56ec274af02b93c7f4df80236a8fc8a7cafec8aebc936da4"
UNION="experiments/contribution2/disease_selection/efo_rebuild/selected_diseases_efoclean__44disease.csv"
GT="experiments/contribution2/disease_selection/efo_rebuild/ground-truth__efoclean"
WITHDOM="experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py"

# Map section key -> the H2 marker that must be ABSENT after ablation
# (bash 3.2 on macOS has no associative arrays, so use a case statement).
marker_for () {
  case "$1" in
    cross) echo "## Cross-cutting appraisal principles" ;;
    1) echo "## 1. predicted_trait" ;;
    2) echo "## 2. performance_metrics" ;;
    3) echo "## 3. source_of_variant_associations_gwas" ;;
    4) echo "## 4. score_development_training" ;;
    5) echo "## 5. development_method" ;;
    6) echo "## 6. variants" ;;
    7) echo "## 7. pgs_source" ;;
  esac
}

restore_and_verify () {
  cp "$ORIG" "$CORPUS"
  local a; a=$(shasum -a 256 "$CORPUS" | awk '{print $1}')
  if [ "$a" != "$ORIG_SHA" ]; then echo "❌ RESTORE FAILED sha=$a"; exit 1; fi
}

for sec in cross 1 2 3 4 5 6 7; do
  echo "================= LORO bake: section $sec ================="
  $PY "$W/ablate_section.py" --in "$ORIG" --out "$CORPUS" --section "$sec" | sed 's/^/  ablate: /'
  $PY "$WITHDOM" --mode prepare --model gpt-5.4 --trials 1 \
      --run-tag "loro-no-$sec" --union-csv "$UNION" --ground-truth-dir "$GT" \
      2>&1 | tail -1 | sed 's/^/  prepare: /'
  restore_and_verify
  echo "  ✅ corpus restored (sha ok)"
  # bake-check: target marker absent, a control marker present
  MAN="experiments/contribution2/recommendation/runs/with-domain-gpt-5.4-t1__44disease__loro-no-$sec/experiment_with_domain_batch_manifest.json"
  $PY - "$MAN" "$(marker_for "$sec")" <<'PY'
import json, sys
man, marker = sys.argv[1], sys.argv[2]
m = json.load(open(man))
um = m["requests"][0]["request"]["body"]["messages"][1]["content"]
fd = json.loads(um[um.find("Context:\n")+len("Context:\n"):])["domain_knowledge"]["full_document"]
absent = marker not in fd
# control: §2 should be present unless this IS §2; else check §1
ctrl = "## 1. predicted_trait" if marker.startswith("## 2.") else "## 2. performance_metrics"
ctrl_present = ctrl in fd
print(f"  bake-check: removed[{marker[:24]}...]={absent}  kept[{ctrl[:18]}...]={ctrl_present}  baked_len={len(fd)}")
if not (absent and ctrl_present):
    print("  ❌ BAKE-CHECK FAILED"); sys.exit(1)
PY
done
echo ""
echo "================= Phase A complete: 8 manifests baked, corpus verified ================="
shasum -a 256 "$CORPUS"
