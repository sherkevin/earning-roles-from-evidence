#!/bin/bash
# R41d MuSiQue matrix watcher — fires AFTER the current HotpotQA workload
# (E-017 seed=43/44 + HotpotQA n=50 smokes) is done, to keep newapi load below
# the "2 batches × 8 workers" safe envelope.
#
# Launches the (systems × MuSiQue) matrix:
#   - TCPB Stage-2 (edo_stage2_chain) n=50
#   - TCPB Stage-1 (fixed_peer_calibrated) n=50  [baseline-1]
#   - MAD n=50
#   - MA-RAG n=50
#   - ReAgent n=50 (W3 patched)
#
# = 5 systems × 1 benchmark = 5 batches of 50 samples each.
# Per user's R41d instruction: "正常应该是一个试验矩阵 (baseline + 1) * (data)个实验".
# HotpotQA matrix already running under earlier watchers (E-017 seed 42/43/44
# for TCPB + R41b watcher for 3 external); this watcher adds the MuSiQue row.

set -u
cd /media/data3/dengkw/idea04

TS_START="$(date +%Y%m%d_%H%M%S)"
WATCH_LOG="artifacts/monitor/r41d_musique_matrix_watch_${TS_START}.log"
mkdir -p "$(dirname "${WATCH_LOG}")" logs/r41d_matrix

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${WATCH_LOG}"
}

log "================================================================"
log "R41d MuSiQue matrix watcher — 5 systems × MuSiQue n=50"
log "  will fire ONLY AFTER: seed=43 stage2+stage1 DONE + n=50 HotpotQA DONE"
log "================================================================"

# Step 1: wait for HotpotQA workload to finish
SEED43_S2=""
SEED43_S1=""
MAD50=""
MR50=""
RA50=""

find_latest_seed(){
  ls -d artifacts/round2_gpt41mini_stage2_fullval/run_*_seed43/ 2>/dev/null | sort -r | head -1
}
find_n50(){
  ls -d artifacts/external_baselines/"$1"/r41b_n50_*/ 2>/dev/null | sort -r | head -1
}

while true; do
  S43_DIR=$(find_latest_seed)
  S43_S2_DONE="unknown"
  S43_S1_DONE="unknown"
  if [ -n "${S43_DIR}" ]; then
    S43_S2_DONE=$([ -f "${S43_DIR}edo_stage2_chain/metrics.json" ] && echo DONE || echo running)
    S43_S1_DONE=$([ -f "${S43_DIR}fixed_peer_calibrated/metrics.json" ] && echo DONE || echo running)
  fi
  MAD_DIR=$(find_n50 mad); MAD_DONE=$([ -n "${MAD_DIR}" ] && [ -f "${MAD_DIR}metrics.json" ] && echo DONE || echo running)
  MR_DIR=$(find_n50 marag); MR_DONE=$([ -n "${MR_DIR}" ] && [ -f "${MR_DIR}metrics.json" ] && echo DONE || echo running)
  RA_DIR=$(find_n50 reagent); RA_DONE=$([ -n "${RA_DIR}" ] && [ -f "${RA_DIR}metrics.json" ] && echo DONE || echo running)

  log "poll: seed43_s2=${S43_S2_DONE} | seed43_s1=${S43_S1_DONE} | MAD50=${MAD_DONE} | MARAG50=${MR_DONE} | REAGENT50=${RA_DONE}"

  if [ "${S43_S2_DONE}" = DONE ] && [ "${S43_S1_DONE}" = DONE ] \
     && [ "${MAD_DONE}" = DONE ] && [ "${MR_DONE}" = DONE ] \
     && [ "${RA_DONE}" = DONE ]; then
    log "All HotpotQA workload DONE — proceeding to MuSiQue matrix."
    break
  fi
  sleep 300  # 5-min poll
done

# Step 2: pre-flight
log "pre-flight quota probe"
if ! bash workspace/tmp/newapi_quota_probe.sh 2>&1 | tee -a "${WATCH_LOG}" | grep -q "newapi ACTIVE"; then
  log "ABORT: quota not ACTIVE; MuSiQue matrix NOT launched."
  exit 2
fi

# Step 3: fire 5 matrix batches in parallel (all n=50 on MuSiQue)
TS="$(date +%Y%m%d_%H%M%S)"
MATRIX_DIR="artifacts/matrix/musique_n50_${TS}"
mkdir -p "${MATRIX_DIR}"

SAMPLES="artifacts/seed/musique_validation_200.jsonl"
if [ ! -f "${SAMPLES}" ]; then
  log "ABORT: MuSiQue seed file ${SAMPLES} missing. Run scripts/prep_musique_seed.py first."
  exit 2
fi

# TCPB Stage-2
TCPB_S2_OUT="${MATRIX_DIR}/tcpb_stage2"
mkdir -p "${TCPB_S2_OUT}"
log "launching TCPB Stage-2 on MuSiQue n=50"
nohup python3 -u scripts/run_e017_fullval_seed.py \
    --seed 42 --method edo_stage2_chain --workers 4 --n 50 \
    --samples-jsonl "${SAMPLES}" \
    --run-dir "${TCPB_S2_OUT}" \
  > logs/r41d_matrix/tcpb_s2_${TS}.log 2>&1 &
TCPB_S2_PID=$!
log "  TCPB Stage-2 PID=${TCPB_S2_PID}"

# TCPB Stage-1 (baseline-1, the key control)
TCPB_S1_OUT="${MATRIX_DIR}/tcpb_stage1"
mkdir -p "${TCPB_S1_OUT}"
log "launching TCPB Stage-1 on MuSiQue n=50"
nohup python3 -u scripts/run_e017_fullval_seed.py \
    --seed 42 --method fixed_peer_calibrated --workers 4 --n 50 \
    --samples-jsonl "${SAMPLES}" \
    --run-dir "${TCPB_S1_OUT}" \
  > logs/r41d_matrix/tcpb_s1_${TS}.log 2>&1 &
TCPB_S1_PID=$!
log "  TCPB Stage-1 PID=${TCPB_S1_PID}"

# MAD
MAD_OUT="${MATRIX_DIR}/mad"
mkdir -p "${MAD_OUT}"
log "launching MAD on MuSiQue n=50"
nohup external_baselines/mad/venv_mad/bin/python \
    external_baselines/mad/hotpotqa/gen_hotpotqa.py \
      --samples-jsonl "${SAMPLES}" \
      --n 50 --agents 3 --rounds 2 \
      --out-dir "${MAD_OUT}" \
  > logs/r41d_matrix/mad_${TS}.log 2>&1 &
MAD_PID=$!
log "  MAD PID=${MAD_PID}"

# MA-RAG
MARAG_OUT="${MATRIX_DIR}/marag"
mkdir -p "${MARAG_OUT}"
log "launching MA-RAG on MuSiQue n=50"
nohup external_baselines/marag/venv_marag/bin/python \
    external_baselines/marag/run_marag_hotpotqa.py \
      --samples-jsonl "${SAMPLES}" \
      --n 50 \
      --out-dir "${MARAG_OUT}" \
  > logs/r41d_matrix/marag_${TS}.log 2>&1 &
MARAG_PID=$!
log "  MA-RAG PID=${MARAG_PID}"

# ReAgent (W3 patched)
REAGENT_OUT="${MATRIX_DIR}/reagent"
mkdir -p "${REAGENT_OUT}"
log "launching ReAgent on MuSiQue n=50 (W3 + --no-mas)"
nohup external_baselines/reagent/venv_reagent/bin/python \
    external_baselines/reagent/run_reagent_hotpotqa.py \
      --samples-jsonl "${SAMPLES}" \
      --n 50 \
      --out-dir "${REAGENT_OUT}" \
      --model gpt-4.1-mini --no-mas \
  > logs/r41d_matrix/reagent_${TS}.log 2>&1 &
REAGENT_PID=$!
log "  ReAgent PID=${REAGENT_PID}"

log "All 5 matrix batches launched. PIDs: TCPB_S2=${TCPB_S2_PID} TCPB_S1=${TCPB_S1_PID} MAD=${MAD_PID} MARAG=${MARAG_PID} REAGENT=${REAGENT_PID}"

# Step 4: wait for all metrics.json
log "waiting for all 5 MuSiQue n=50 batches..."
while true; do
  T2_DONE=$([ -f "${TCPB_S2_OUT}/metrics.json" ] && echo DONE || echo running)
  T1_DONE=$([ -f "${TCPB_S1_OUT}/metrics.json" ] && echo DONE || echo running)
  MAD_DONE=$([ -f "${MAD_OUT}/metrics.json" ] && echo DONE || echo running)
  MR_DONE=$([ -f "${MARAG_OUT}/metrics.json" ] && echo DONE || echo running)
  RA_DONE=$([ -f "${REAGENT_OUT}/metrics.json" ] && echo DONE || echo running)
  log "  TCPB_S2=${T2_DONE} TCPB_S1=${T1_DONE} MAD=${MAD_DONE} MARAG=${MR_DONE} REAGENT=${RA_DONE}"
  if [ "${T2_DONE}" = DONE ] && [ "${T1_DONE}" = DONE ] \
     && [ "${MAD_DONE}" = DONE ] && [ "${MR_DONE}" = DONE ] \
     && [ "${RA_DONE}" = DONE ]; then
    break
  fi
  sleep 180
done

# Step 5: final summary via summarize script
log "================================================================"
log "MuSiQue n=50 matrix COMPLETE. Running summarize_external_smokes.py..."
python3 scripts/summarize_external_smokes.py 2>&1 | tee -a "${WATCH_LOG}" | tail -30
log "================================================================"
