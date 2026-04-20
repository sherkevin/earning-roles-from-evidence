#!/bin/bash
# E-017 server scheduler: monitor seed=42 → launch seed=43 → launch seed=44 → run paired_bootstrap_ci.
# Per engineer's "newapi parallelism cap = 2" lesson, we run 2 batches in parallel per seed,
# and seeds sequentially.
set -u
cd /media/data3/dengkw/idea04
mkdir -p logs
unset LLM_BACKEND LLM_BASE_URL LLM_API_KEY LLM_MODEL
export PYTHONPATH=/media/data3/dengkw/idea04/workspace:/media/data3/dengkw/idea04/scripts

OUT_ROOT="artifacts/round2_gpt41mini_stage2_fullval"
SCHED_LOG="logs/e017_scheduler_$(date +%Y%m%d_%H%M%S).log"

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${SCHED_LOG}"
}

wait_for_metrics(){
  local stage2_dir="$1"
  local stage1_dir="$2"
  while true; do
    if [ -f "${stage2_dir}/metrics.json" ] && [ -f "${stage1_dir}/metrics.json" ]; then
      log "  → metrics.json present in BOTH"
      break
    fi
    if [ -f "${stage2_dir}/_ckpt_preds.jsonl" ]; then
      s2_lines=$(wc -l < "${stage2_dir}/_ckpt_preds.jsonl")
    else
      s2_lines=0
    fi
    if [ -f "${stage1_dir}/_ckpt_preds.jsonl" ]; then
      s1_lines=$(wc -l < "${stage1_dir}/_ckpt_preds.jsonl")
    else
      s1_lines=0
    fi
    s2_done=$([ -f "${stage2_dir}/metrics.json" ] && echo "DONE" || echo "running")
    s1_done=$([ -f "${stage1_dir}/metrics.json" ] && echo "DONE" || echo "running")
    log "  ckpt: stage2=${s2_lines}/7405 ${s2_done} | stage1=${s1_lines}/7405 ${s1_done}"
    sleep 60
  done
}

launch_seed(){
  local seed="$1"
  local run_id="$2"   # used as dir prefix; if empty, autogen
  log "==== launching seed=${seed} ===="
  if [ -n "${run_id}" ]; then
    local s2_dir="${OUT_ROOT}/${run_id}/edo_stage2_chain"
    local s1_dir="${OUT_ROOT}/${run_id}/fixed_peer_calibrated"
    mkdir -p "${s2_dir}" "${s1_dir}"
    log "  stage2 run_dir=${s2_dir}"
    log "  stage1 run_dir=${s1_dir}"
    nohup python3 -u scripts/run_e017_fullval_seed.py \
        --seed ${seed} --method edo_stage2_chain \
        --workers 8 --run-dir "${s2_dir}" \
        > "logs/e017_seed${seed}_stage2.log" 2>&1 &
    s2_pid=$!
    sleep 1
    nohup python3 -u scripts/run_e017_fullval_seed.py \
        --seed ${seed} --method fixed_peer_calibrated \
        --workers 8 --run-dir "${s1_dir}" \
        > "logs/e017_seed${seed}_stage1.log" 2>&1 &
    s1_pid=$!
    log "  stage2 PID=${s2_pid}  stage1 PID=${s1_pid}"
    echo "${s2_dir}" > "/tmp/e017_current_s2_dir"
    echo "${s1_dir}" > "/tmp/e017_current_s1_dir"
  fi
}

# === Step 1: Wait for seed=42 (already running with PIDs 217406+217416) ===
log "Step 1: waiting for seed=42 (already running, PIDs 217406+217416)"
SEED42_S2="${OUT_ROOT}/run_20260419_124129_seed42/edo_stage2_chain"
SEED42_S1="${OUT_ROOT}/run_20260419_124130_seed42/fixed_peer_calibrated"
wait_for_metrics "${SEED42_S2}" "${SEED42_S1}"
log "Step 1 ✓ seed=42 complete"

# Validate seed=42
log "Step 1.5: validate_logs seed=42"
python3 scripts/validate_logs.py "${SEED42_S2}" 2>&1 | tee -a "${SCHED_LOG}" | tail -5
python3 scripts/validate_logs.py "${SEED42_S1}" 2>&1 | tee -a "${SCHED_LOG}" | tail -5

# === Step 2: launch seed=43 ===
RUN_ID_43="run_$(date +%Y%m%d_%H%M%S)_seed43"
launch_seed 43 "${RUN_ID_43}"
sleep 10
SEED43_S2="${OUT_ROOT}/${RUN_ID_43}/edo_stage2_chain"
SEED43_S1="${OUT_ROOT}/${RUN_ID_43}/fixed_peer_calibrated"
wait_for_metrics "${SEED43_S2}" "${SEED43_S1}"
log "Step 2 ✓ seed=43 complete"
python3 scripts/validate_logs.py "${SEED43_S2}" 2>&1 | tee -a "${SCHED_LOG}" | tail -5
python3 scripts/validate_logs.py "${SEED43_S1}" 2>&1 | tee -a "${SCHED_LOG}" | tail -5

# === Step 3: launch seed=44 ===
RUN_ID_44="run_$(date +%Y%m%d_%H%M%S)_seed44"
launch_seed 44 "${RUN_ID_44}"
sleep 10
SEED44_S2="${OUT_ROOT}/${RUN_ID_44}/edo_stage2_chain"
SEED44_S1="${OUT_ROOT}/${RUN_ID_44}/fixed_peer_calibrated"
wait_for_metrics "${SEED44_S2}" "${SEED44_S1}"
log "Step 3 ✓ seed=44 complete"
python3 scripts/validate_logs.py "${SEED44_S2}" 2>&1 | tee -a "${SCHED_LOG}" | tail -5
python3 scripts/validate_logs.py "${SEED44_S1}" 2>&1 | tee -a "${SCHED_LOG}" | tail -5

# === Step 4: paired_bootstrap_ci.py across 3 seeds ===
log "Step 4: paired_bootstrap_ci.py across 3 seeds"
python3 scripts/paired_bootstrap_ci.py \
    --root "${OUT_ROOT}" \
    --method-a fixed_peer_calibrated \
    --method-b edo_stage2_chain \
    --seeds 42,43,44 \
    --B 10000 \
    --out "${OUT_ROOT}/paired_stats_3seed.csv" 2>&1 | tee -a "${SCHED_LOG}"

log "==== E-017 fullval batch complete ===="
log "deliverables:"
log "  ${OUT_ROOT}/run_20260419_124129_seed42/edo_stage2_chain/metrics.json"
log "  ${OUT_ROOT}/run_20260419_124130_seed42/fixed_peer_calibrated/metrics.json"
log "  ${OUT_ROOT}/${RUN_ID_43}/{edo_stage2_chain,fixed_peer_calibrated}/metrics.json"
log "  ${OUT_ROOT}/${RUN_ID_44}/{edo_stage2_chain,fixed_peer_calibrated}/metrics.json"
log "  ${OUT_ROOT}/paired_stats_3seed.csv"
