#!/bin/bash
# R43 (2026-04-23) download retry wrapper — restart Phi-4-mini + SmolLM3-3B
# hf downloads that died from httpx.ConnectTimeout / SSL handshake timeout.
# Uses hf CLI's built-in resume (skips files already present + retries partials).
# Adds up to 10 retry attempts per model; sleeps 30 s between attempts.
set -u
cd /media/data3/dengkw/idea04

VENV="/media/data3/dengkw/venvs/vllm-py310"
MODELS_ROOT="/media/data3/dengkw/models"
export HF_ENDPOINT="https://hf-mirror.com"
export HF_HOME="${MODELS_ROOT}/hf_home"
export HF_HUB_ENABLE_HF_TRANSFER=0

TS="$(date +%Y%m%d_%H%M%S)"
LOG_DIR="/media/data3/dengkw/idea04/logs"
mkdir -p "${LOG_DIR}"

download_with_retry(){
  local repo="$1"
  local target="$2"
  local tag="$3"
  local log="${LOG_DIR}/r43_download_${tag}_${TS}.log"

  {
    echo "=============================================================="
    echo "R43 download retry loop for ${repo}"
    echo "  target: ${target}"
    echo "  log:    ${log}"
    echo "=============================================================="
  } >> "${log}"

  for i in $(seq 1 10); do
    echo "[$(date '+%F %T')] attempt ${i}/10 starting" | tee -a "${log}"
    set +e
    "${VENV}/bin/hf" download "${repo}" --local-dir "${target}" --max-workers 2 >> "${log}" 2>&1
    rc=$?
    set -e
    if [ ${rc} -eq 0 ]; then
      echo "[$(date '+%F %T')] attempt ${i}/10 SUCCESS (rc=0)" | tee -a "${log}"
      return 0
    fi
    echo "[$(date '+%F %T')] attempt ${i}/10 failed rc=${rc}; sleep 30 s and retry" | tee -a "${log}"
    sleep 30
  done
  echo "[$(date '+%F %T')] GIVE UP after 10 attempts" | tee -a "${log}"
  return 1
}

# Start in parallel
download_with_retry microsoft/Phi-4-mini-instruct "${MODELS_ROOT}/phi4_mini_instruct" phi4 &
PHI4_PID=$!
sleep 1
download_with_retry HuggingFaceTB/SmolLM3-3B "${MODELS_ROOT}/smollm3_3b" smollm3 &
SMOL_PID=$!

echo "launched:"
echo "  Phi-4-mini  retry-wrapper PID=${PHI4_PID}  log=logs/r43_download_phi4_${TS}.log"
echo "  SmolLM3-3B retry-wrapper PID=${SMOL_PID}  log=logs/r43_download_smollm3_${TS}.log"
echo ""
echo "Both retry wrappers will try up to 10 × per model; each hf download auto-resumes via HF cache."
echo "Engineer runs this in nohup so wrappers survive SSH disconnect."
