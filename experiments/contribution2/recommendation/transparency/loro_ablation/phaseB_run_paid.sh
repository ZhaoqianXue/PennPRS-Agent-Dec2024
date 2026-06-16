#!/usr/bin/env bash
# Phase B: submit the paid OpenAI batch runs. Reads PRE-BAKED manifests from
# Phase A (no skill-file editing here). arm4 bakes the untouched full skillv2.
# Each run is fail-soft: a failure is logged and the driver continues.
cd /Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent

PY=".venv/bin/python"
RUNS="experiments/contribution2/recommendation/runs"
TOPK="experiments/contribution2/recommendation/scripts/run_experiment_topk_holistic_rerank_batch.py"
WITHDOM="experiments/contribution2/recommendation/scripts/run_experiment_with_domain.py"
UNION="experiments/contribution2/disease_selection/efo_rebuild/selected_diseases_efoclean__44disease.csv"
GT="experiments/contribution2/disease_selection/efo_rebuild/ground-truth__efoclean"
ARM2_MAN="$RUNS/without-domain-gpt-5.4-t1__44disease__efoclean44/experiment_without_domain_batch_manifest.json"
LOG="experiments/contribution2/recommendation/transparency/loro_ablation/results/phaseB.log"
mkdir -p "$(dirname "$LOG")"

stamp () { date "+%Y-%m-%d %H:%M:%S"; }
say () { echo "[$(stamp)] $*" | tee -a "$LOG"; }

hit1 () {  # $1 = run-tag substring -> print majority_vote_accuracy from newest matching topk summary
  local dir; dir=$(ls -dt "$RUNS"/topk-holistic-rerank-batch-gpt-5.4-t1__44disease__"$1"-* 2>/dev/null | head -1)
  [ -z "$dir" ] && { echo "NO_DIR"; return; }
  $PY -c "import json,sys;s=json.load(open('$dir/experiment_topk_holistic_rerank_batch_summary.json'));print(f\"Hit@1={s.get('majority_vote_accuracy')}  cost=\${s.get('cost',{}).get('estimated_total_cost_usd')}  dir=$dir\")" 2>/dev/null || echo "NO_SUMMARY ($dir)"
}

run_topk () {  # $1 = manifest, $2 = run-tag
  say "TOPK START tag=$2"
  if $PY "$TOPK" --manifest "$1" --run-tag "$2" --model gpt-5.4 --mode run \
        --top-k 5 --objective performance_proxy --stage1-objective support \
        --poll-interval-seconds 30 >>"$LOG" 2>&1; then
    say "TOPK DONE  tag=$2 -> $(hit1 "$2")"
  else
    say "TOPK FAIL  tag=$2 (see log)"
  fi
}

say "================= PHASE B BEGIN ================="

# ---- arm3: 2-stage harness, EMPTY skill (reuse arm2 without-domain manifest) ----
run_topk "$ARM2_MAN" "efoclean44-noskill-2stage"

# ---- LORO x8: 2-stage harness, full skill minus one section ----
for sec in 2 cross 1 3 4 5 6 7; do
  MAN="$RUNS/with-domain-gpt-5.4-t1__44disease__loro-no-$sec/experiment_with_domain_batch_manifest.json"
  if [ -f "$MAN" ]; then run_topk "$MAN" "efoclean44-skillv2-loro-no-$sec"
  else say "TOPK SKIP  loro-no-$sec (manifest missing: $MAN)"; fi
done

# ---- arm4: single-shot with_domain, FULL skill (deployed skillv2) ----
A4_TAG="efoclean44-skillv2-singleshot"
A4_DIR="$RUNS/with-domain-gpt-5.4-t1__44disease__$A4_TAG"
A4_JOB="$A4_DIR/experiment_with_domain_batch_job.json"
say "ARM4 START prepare-submit tag=$A4_TAG"
if $PY "$WITHDOM" --mode prepare-submit --model gpt-5.4 --trials 1 \
      --run-tag "$A4_TAG" --union-csv "$UNION" --ground-truth-dir "$GT" >>"$LOG" 2>&1; then
  # poll batch to terminal state, then collect
  $PY - "$A4_JOB" <<'PY' >>"$LOG" 2>&1
import json,sys,time
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv(".env")
job=json.load(open(sys.argv[1])); bid=job["batch_id"]; c=OpenAI()
while True:
    b=c.batches.retrieve(bid); print("[arm4] status",b.status,flush=True)
    if b.status in {"completed","failed","expired","cancelled"}: break
    time.sleep(30)
PY
  if $PY "$WITHDOM" --mode collect --model gpt-5.4 --trials 1 \
        --run-tag "$A4_TAG" --union-csv "$UNION" --ground-truth-dir "$GT" >>"$LOG" 2>&1; then
    H=$($PY -c "import json;s=json.load(open('$A4_DIR/experiment_with_domain_summary.json'));print(f\"Hit@1={s.get('majority_vote_accuracy')}  cost=\${s.get('cost',{}).get('estimated_total_cost_usd')}\")" 2>/dev/null || echo "NO_SUMMARY")
    say "ARM4 DONE -> $H  dir=$A4_DIR"
  else
    say "ARM4 COLLECT FAIL (see log)"
  fi
else
  say "ARM4 PREPARE-SUBMIT FAIL (see log)"
fi

say "================= PHASE B COMPLETE ================="
echo "FINAL deployed corpus sha:" | tee -a "$LOG"
shasum -a 256 src/server/core/skills/prs-model-recommendation/references/pgs_evidence_appraisal.md | tee -a "$LOG"
