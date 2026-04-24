#!/bin/bash
# ============================================================================
# R43 SmolLM3-3B auto-watcher (parallel to r42_auto_watcher_emergence.sh)
# ============================================================================
# Polls every 60 s for SmolLM3-3B readiness + fires
# `r43_smollm3_emergence_pipeline.sh` in nohup.
#
# Preconditions (both required):
#   (1) `python -c "import vllm, torch"` success in venv
#   (2) /media/data3/dengkw/models/smollm3_3b/ has >= 1 safetensors file
#
# Timeout: 2 hours.
# Idempotent: safe to re-run (pipeline skips cells with metrics.json).
# ============================================================================
set -u
cd /media/data3/dengkw/idea04
mkdir -p logs artifacts/monitor

WATCH_LOG="artifacts/monitor/r43_smollm3_auto_watcher_$(date +%Y%m%d_%H%M%S).log"
VENV="/media/data3/dengkw/venvs/vllm-py310"
SMOL_DIR="/media/data3/dengkw/models/smollm3_3b"
PIPELINE="workspace/tmp/r43_smollm3_emergence_pipeline.sh"

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${WATCH_LOG}"
}

log "=================================================="
log "R43 SmolLM3-3B auto-watcher"
log "  polls every 60 s, max 120 min"
log "  log: ${WATCH_LOG}"
log "=================================================="

MAX_ITER=120
for i in $(seq 1 ${MAX_ITER}); do
  if "${VENV}/bin/python3" -c "import vllm, torch" >/dev/null 2>&1; then
    vllm_ready=1
  else
    vllm_ready=0
  fi
  if [ -d "${SMOL_DIR}" ]; then
    smol_files=$(ls "${SMOL_DIR}"/*.safetensors 2>/dev/null | wc -l)
  else
    smol_files=0
  fi
  log "iter ${i}/${MAX_ITER}  vllm=${vllm_ready}  smollm3_safetensors=${smol_files}"
  if [ "${vllm_ready}" -eq 1 ] && [ "${smol_files}" -ge 1 ]; then
    log "PRECONDITIONS SATISFIED"
    break
  fi
  sleep 60
done

if [ "${vllm_ready}" -ne 1 ] || [ "${smol_files}" -lt 1 ]; then
  log "TIMEOUT — leaving download to finish; re-run watcher or pipeline manually."
  exit 2
fi

TS="$(date +%Y%m%d_%H%M%S)"
PIPELINE_LOG="logs/r43_smollm3_pipeline_auto_${TS}.log"
log "launching: nohup bash ${PIPELINE} > ${PIPELINE_LOG} 2>&1 &"
nohup bash "${PIPELINE}" > "${PIPELINE_LOG}" 2>&1 &
PIPE_PID=$!
disown || true
log "SmolLM3 pipeline PID=${PIPE_PID}  log=${PIPELINE_LOG}"
log "Watcher done."
