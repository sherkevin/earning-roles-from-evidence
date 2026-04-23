#!/bin/bash
# R41b n=50 follow-up smokes watcher — fires after E-017 seed=42 BOTH stages DONE.
# Runs MAD n=50 + MA-RAG n=50 + ReAgent n=50 in PARALLEL with the scheduler's
# seed=43 run (which will already be using 16 newapi workers).
#
# Per the operational corollary in [u_rollback_001_path_a_landed_20260420]:
# 16 workers (E-017 2 batches) + 3 smokes at workers=1 each = 19 concurrent.
# Observed in R41 first-round smoke: ~20% rate dip, immediately recovered
# post-smoke. Acceptable parallelism cost for the statistical-significance
# uplift from n=5 → n=50.
#
# Invariants:
#   - Smokes only launch if E-020.3 pre-flight probe reports newapi ACTIVE.
#   - Watcher writes progress every 3 min to artifacts/monitor/r41b_n50_*.log.
#   - Exits when all 3 n=50 batches have produced metrics.json.

set -u
cd /media/data3/dengkw/idea04

TS_START="$(date +%Y%m%d_%H%M%S)"
WATCH_LOG="artifacts/monitor/r41b_n50_watch_${TS_START}.log"
mkdir -p "$(dirname "${WATCH_LOG}")" logs/r41_smoke

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${WATCH_LOG}"
}

log "========================================================"
log "R41b n=50 WATCHER — waiting for E-017 seed=42 completion"
log "  (watches both stage2 + stage1 metrics.json emergence)"
log "========================================================"

SEED42_S2="artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124129_seed42/edo_stage2_chain"
SEED42_S1="artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124130_seed42/fixed_peer_calibrated"

# Step 1: wait (polling every 3 min) for both metrics.json
while true; do
  if [ -f "${SEED42_S2}/metrics.json" ] && [ -f "${SEED42_S1}/metrics.json" ]; then
    log "seed=42 BOTH batches DONE — proceeding to n=50 smoke launch"
    break
  fi
  S2L=$(wc -l < "${SEED42_S2}/_ckpt_preds.jsonl" 2>/dev/null || echo 0)
  S1L=$(wc -l < "${SEED42_S1}/_ckpt_preds.jsonl" 2>/dev/null || echo 0)
  S2_STAT=$([ -f "${SEED42_S2}/metrics.json" ] && echo DONE || echo running)
  S1_STAT=$([ -f "${SEED42_S1}/metrics.json" ] && echo DONE || echo running)
  log "poll: seed42 stage2=${S2L}/7405 ${S2_STAT} | stage1=${S1L}/7405 ${S1_STAT}"
  sleep 180
done

# Step 2: pre-flight quota probe
log "pre-flight quota probe before n=50 batch"
if ! bash workspace/tmp/newapi_quota_probe.sh 2>&1 | tee -a "${WATCH_LOG}" | grep -q "newapi ACTIVE"; then
  log "ABORT: quota not ACTIVE; n=50 smokes NOT launched. Manual intervention required."
  exit 2
fi

# Step 3: fire 3 smokes in parallel
TS="$(date +%Y%m%d_%H%M%S)"
MAD_OUT="artifacts/external_baselines/mad/r41b_n50_${TS}"
MARAG_OUT="artifacts/external_baselines/marag/r41b_n50_${TS}"
REAGENT_OUT="artifacts/external_baselines/reagent/r41b_n50_${TS}"
mkdir -p "${MAD_OUT}" "${MARAG_OUT}" "${REAGENT_OUT}"

log "launching MAD n=50"
nohup external_baselines/mad/venv_mad/bin/python \
    external_baselines/mad/hotpotqa/gen_hotpotqa.py \
      --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
      --n 50 --agents 3 --rounds 2 \
      --out-dir "${MAD_OUT}" \
    > logs/r41_smoke/mad_n50_${TS}.log 2>&1 &
MAD_PID=$!
echo "${MAD_PID}" > "${MAD_OUT}/.pid"
log "  MAD PID=${MAD_PID}"

log "launching MA-RAG n=50"
nohup external_baselines/marag/venv_marag/bin/python \
    external_baselines/marag/run_marag_hotpotqa.py \
      --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
      --n 50 \
      --out-dir "${MARAG_OUT}" \
    > logs/r41_smoke/marag_n50_${TS}.log 2>&1 &
MARAG_PID=$!
echo "${MARAG_PID}" > "${MARAG_OUT}/.pid"
log "  MA-RAG PID=${MARAG_PID}"

# E-018 ReAgent smoke RE-ENABLED in R41c after W3 workaround landed
# (replaces ReAgent's openai-SDK-based api_call with our urllib-based
# llm_client.call_llm). R41c n=5 pilot passed: 5/5 samples, F1=0.16
# (format-penalized but semantically correct). See `e018_reagent_adapter_inspection.md`
# §11.3 W3 + implementation_log.md [e_018_reagent_w3_workaround_20260420].
log "launching ReAgent n=50 (W3 patched, --no-mas)"
nohup external_baselines/reagent/venv_reagent/bin/python \
    external_baselines/reagent/run_reagent_hotpotqa.py \
      --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
      --n 50 \
      --out-dir "${REAGENT_OUT}" \
      --model gpt-4.1-mini \
      --no-mas \
    > logs/r41_smoke/reagent_n50_${TS}.log 2>&1 &
REAGENT_PID=$!
echo "${REAGENT_PID}" > "${REAGENT_OUT}/.pid"
log "  ReAgent PID=${REAGENT_PID}"

# Step 4: wait for the 3 live smokes metrics.json
log "waiting for 3 n=50 smokes (MAD + MA-RAG + ReAgent) to produce metrics.json..."
while true; do
  MAD_DONE=$([ -f "${MAD_OUT}/metrics.json" ] && echo DONE || echo running)
  MR_DONE=$([ -f "${MARAG_OUT}/metrics.json" ] && echo DONE || echo running)
  RA_DONE=$([ -f "${REAGENT_OUT}/metrics.json" ] && echo DONE || echo running)
  log "  MAD=${MAD_DONE} MA-RAG=${MR_DONE} ReAgent=${RA_DONE}"
  if [ "${MAD_DONE}" = DONE ] && [ "${MR_DONE}" = DONE ] && [ "${RA_DONE}" = DONE ]; then
    break
  fi
  sleep 180
done

# Step 5: final summary
log "========================================================"
log "3 n=50 smokes COMPLETE. Summary:"
for dir_name in "${MAD_OUT}" "${MARAG_OUT}" "${REAGENT_OUT}"; do
  if [ -f "${dir_name}/metrics.json" ]; then
    python3 -c "
import json
m = json.load(open('${dir_name}/metrics.json'))
print(f'  {m.get(\"host\", \"unknown\")}: EM={m.get(\"answer_em\", 0):.3f} F1={m.get(\"answer_f1\", 0):.3f} n={m.get(\"sample_count\", 0)} wall={m.get(\"wall_s\", 0):.0f}s')
" | tee -a "${WATCH_LOG}"
  fi
done
log "========================================================"
