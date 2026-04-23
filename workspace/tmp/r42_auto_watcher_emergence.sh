#!/bin/bash
# ============================================================================
# R42 auto-watcher daemon: wait 3 parallel jobs ready → fire emergence pipeline
# ============================================================================
# User R42 directive: "挂一个等待脚本到后台然后继续做其他事情，只需要结束
# 之后去看看跑的怎么样就行了". This script is that watcher.
#
# Monitors:
#   (1) vllm pip install:  check `python -c "import vllm"` in venv
#   (2) Phi-4-mini download: check /media/data3/dengkw/models/phi4_mini_instruct/
#                            has >= 4 .safetensors files (typical Phi-4-mini shards)
#   (3) SmolLM3-3B download: check /media/data3/dengkw/models/smollm3_3b/
#                            has >= 1 .safetensors file
#
# When (1) + (2) are both READY (SmolLM3 is a bonus; pipeline uses Phi-4 only),
# fire r42_emergence_pipeline.sh in nohup and exit.
#
# Idempotency: if emergence_pipeline result already exists for today, skip.
# Safety: timeout after 2 hours to avoid runaway polling.
# ============================================================================

set -u
cd /media/data3/dengkw/idea04
mkdir -p logs artifacts/monitor

WATCH_LOG="artifacts/monitor/r42_auto_watcher_$(date +%Y%m%d_%H%M%S).log"
VENV="/media/data3/dengkw/venvs/vllm-py310"
PHI4_DIR="/media/data3/dengkw/models/phi4_mini_instruct"
SMOL_DIR="/media/data3/dengkw/models/smollm3_3b"
PIPELINE="workspace/tmp/r42_emergence_pipeline.sh"

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${WATCH_LOG}"
}

log "================================================================"
log "R42 auto-watcher daemon: wait 3 parallel jobs → fire emergence pipeline"
log "  polling every 60 s, max 120 min (2 h)"
log "  log: ${WATCH_LOG}"
log "================================================================"

MAX_ITER=120   # 120 × 60 s = 2 h
for i in $(seq 1 ${MAX_ITER}); do
  # Check (1) vllm installed
  if "${VENV}/bin/python3" -c "import vllm, torch" >/dev/null 2>&1; then
    vllm_ready=1
  else
    vllm_ready=0
  fi

  # Check (2) Phi-4-mini weights on disk
  if [ -d "${PHI4_DIR}" ]; then
    phi4_files=$(ls "${PHI4_DIR}"/*.safetensors 2>/dev/null | wc -l)
  else
    phi4_files=0
  fi

  # Check (3) SmolLM3 weights on disk
  if [ -d "${SMOL_DIR}" ]; then
    smol_files=$(ls "${SMOL_DIR}"/*.safetensors 2>/dev/null | wc -l)
  else
    smol_files=0
  fi

  log "iter ${i}/${MAX_ITER}  vllm_ready=${vllm_ready}  phi4_safetensors=${phi4_files}  smollm3_safetensors=${smol_files}"

  # Fire when vllm + Phi-4-mini both ready (SmolLM3 is bonus)
  if [ "${vllm_ready}" -eq 1 ] && [ "${phi4_files}" -ge 2 ]; then
    log "PRECONDITIONS SATISFIED — firing emergence pipeline"
    break
  fi

  sleep 60
done

if [ "${vllm_ready}" -ne 1 ] || [ "${phi4_files}" -lt 2 ]; then
  log "TIMEOUT after ${MAX_ITER} min. Leaving models to finish + user can re-run pipeline manually."
  exit 2
fi

# Fire pipeline in the background so THIS watcher returns cleanly.
TS="$(date +%Y%m%d_%H%M%S)"
PIPELINE_LOG="logs/r42_emergence_pipeline_auto_${TS}.log"
log "launching: nohup bash ${PIPELINE} > ${PIPELINE_LOG} 2>&1 &"
nohup bash "${PIPELINE}" > "${PIPELINE_LOG}" 2>&1 &
PIPE_PID=$!
disown || true
log "pipeline PID=${PIPE_PID}  log=${PIPELINE_LOG}"

log ""
log "Watcher done. Pipeline launched (PID=${PIPE_PID})."
log "  tail -f ${PIPELINE_LOG}"
log "  find result: ls /media/data3/dengkw/idea04/artifacts/emergence/phi4_mini_n5_*"
