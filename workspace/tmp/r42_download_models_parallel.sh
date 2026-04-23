#!/bin/bash
# R42 parallel model download — runs concurrently with ongoing vllm pip install
# (saves ~30 min wait vs serial).
# venv's huggingface-cli is already usable (installed in Step 2 of v2 setup);
# model download does NOT depend on torch/vllm being fully installed.
set -u
cd /media/data3/dengkw/idea04

VENV="/media/data3/dengkw/venvs/vllm-py310"
MODELS_ROOT="/media/data3/dengkw/models"
export HF_ENDPOINT="https://hf-mirror.com"
export HF_HOME="${MODELS_ROOT}/hf_home"

TS="$(date +%Y%m%d_%H%M%S)"
LOG_DIR="/media/data3/dengkw/idea04/logs"
mkdir -p "${LOG_DIR}" "${MODELS_ROOT}"

if [ ! -x "${VENV}/bin/huggingface-cli" ]; then
  echo "ABORT: huggingface-cli not in venv ${VENV}/bin/. Wait for pip install huggingface_hub to finish."
  exit 1
fi

echo "launching parallel downloads:"
echo "  (a) microsoft/Phi-4-mini-instruct  → ${MODELS_ROOT}/phi4_mini_instruct"
echo "  (b) HuggingFaceTB/SmolLM3-3B       → ${MODELS_ROOT}/smollm3_3b"

# Clean empty qwen25 dir (v1 leftover)
if [ -d "${MODELS_ROOT}/qwen25_7b_instruct" ] && [ -z "$(ls -A "${MODELS_ROOT}/qwen25_7b_instruct" 2>/dev/null)" ]; then
  rmdir "${MODELS_ROOT}/qwen25_7b_instruct"
  echo "  (cleaned empty qwen25_7b_instruct dir)"
fi

LOG_PHI4="${LOG_DIR}/r42_download_phi4_${TS}.log"
LOG_SMOL="${LOG_DIR}/r42_download_smollm3_${TS}.log"

mkdir -p "${MODELS_ROOT}/phi4_mini_instruct" "${MODELS_ROOT}/smollm3_3b"

# Phi-4-mini (primary)
HF_ENDPOINT="${HF_ENDPOINT}" HF_HOME="${HF_HOME}" \
  nohup "${VENV}/bin/huggingface-cli" download \
    microsoft/Phi-4-mini-instruct \
    --local-dir "${MODELS_ROOT}/phi4_mini_instruct" \
    --local-dir-use-symlinks False \
  > "${LOG_PHI4}" 2>&1 &
PHI4_PID=$!
disown || true
echo "  Phi-4-mini PID=${PHI4_PID} log=${LOG_PHI4}"

sleep 1

# SmolLM3 (control)
HF_ENDPOINT="${HF_ENDPOINT}" HF_HOME="${HF_HOME}" \
  nohup "${VENV}/bin/huggingface-cli" download \
    HuggingFaceTB/SmolLM3-3B \
    --local-dir "${MODELS_ROOT}/smollm3_3b" \
    --local-dir-use-symlinks False \
  > "${LOG_SMOL}" 2>&1 &
SMOL_PID=$!
disown || true
echo "  SmolLM3-3B PID=${SMOL_PID} log=${LOG_SMOL}"

echo ""
echo "Both downloads launched in background."
echo "  watch:  tail -f ${LOG_PHI4} ${LOG_SMOL}"
echo "  sizes:  du -sh ${MODELS_ROOT}/phi4_mini_instruct ${MODELS_ROOT}/smollm3_3b"
echo ""
echo "Estimated completion: ~15-40 min (HF mirror bandwidth dependent)."
