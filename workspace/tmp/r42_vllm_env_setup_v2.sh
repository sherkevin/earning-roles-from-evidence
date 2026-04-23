#!/bin/bash
# ============================================================================
# R42 E-5 v2: vLLM env + 2026 STRONGEST <7B agentic SLM download
# ============================================================================
# Purpose:
#   Per user R42 feedback "Qwen2.5-7B-Instruct 已经很老了，要专门用于多agent任务
#   的 <7B 超强最新模型作为底座", download Phi-4-mini-instruct (2026 <7B
#   reasoning leader per WebSearch 2026-04) + SmolLM3-3B (HF fully-open recipe
#   with dual-mode /think vs /no_think) as two Option-A/C-ready local
#   backbones. Qwen2.5-7B is superseded by this v2 script.
#
# Changes vs v1:
#   - Do NOT pin torch==2.4.1 (conflicted with vllm 0.6.6 → torch 2.5.1).
#     Let pip resolver pick a vllm+torch combo that supports Phi-4-mini
#     (Phi-4-mini needs vllm ≥ 0.7.0 per HF model card).
#   - Let pip pick a recent vllm (≥ 0.7.0) so Phi-4/SmolLM3 architectures
#     are natively supported (vllm 0.6.x only goes up to Qwen2/Llama3 era).
#   - Switch Step 3 model from Qwen2.5-7B-Instruct to:
#       (a) microsoft/Phi-4-mini-instruct     (3.8B, MIT, reasoning leader)
#       (b) HuggingFaceTB/SmolLM3-3B          (3B, Apache 2.0, dual-mode)
#   - Delete prior venv (scrap 16M empty skeleton) + rebuild clean.
# ============================================================================

set -u
cd /media/data3/dengkw/idea04
mkdir -p logs artifacts/monitor

TS="$(date +%Y%m%d_%H%M%S)"
SETUP_LOG="logs/r42_vllm_env_setup_v2_${TS}.log"

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${SETUP_LOG}"
}

VENV_ROOT="/media/data3/dengkw/venvs"
VENV_NAME="vllm-py310"
VENV_DIR="${VENV_ROOT}/${VENV_NAME}"
MODELS_ROOT="/media/data3/dengkw/models"

# Primary: Phi-4-mini-instruct — 2026 <7B reasoning leader, MIT license
PHI4_NAME="microsoft/Phi-4-mini-instruct"
PHI4_DIR="${MODELS_ROOT}/phi4_mini_instruct"
# Control: SmolLM3-3B — HF fully-open recipe, dual-mode /think
SMOLLM3_NAME="HuggingFaceTB/SmolLM3-3B"
SMOLLM3_DIR="${MODELS_ROOT}/smollm3_3b"

DATA3_TMP="/media/data3/dengkw/tmp"
DATA3_PIP_CACHE="/media/data3/dengkw/pip_cache"
mkdir -p "${DATA3_TMP}" "${DATA3_PIP_CACHE}" "${MODELS_ROOT}"
export TMPDIR="${DATA3_TMP}"
export PIP_CACHE_DIR="${DATA3_PIP_CACHE}"
export HF_ENDPOINT="https://hf-mirror.com"
export HF_HOME="${MODELS_ROOT}/hf_home"

log "================================================================"
log "R42 E-5 v2: vLLM env + 2026 strongest <7B agentic SLM download"
log "  venv:          ${VENV_DIR}"
log "  primary:       ${PHI4_NAME}"
log "  control:       ${SMOLLM3_NAME}"
log "  HF mirror:     ${HF_ENDPOINT}"
log "  TMPDIR:        ${TMPDIR}"
log "  PIP_CACHE:     ${PIP_CACHE_DIR}"
log "================================================================"

# ----------------------------------------------------------------------------
# Step 0: clean v1 venv (was stuck at 16M with torch/vllm conflict)
# ----------------------------------------------------------------------------
log ""
log "Step 0: clean v1 venv"
if [ -d "${VENV_DIR}" ]; then
  log "  rm -rf ${VENV_DIR}"
  rm -rf "${VENV_DIR}"
fi

# ----------------------------------------------------------------------------
# Step 1: create fresh venv
# ----------------------------------------------------------------------------
log ""
log "Step 1: create fresh venv ${VENV_DIR}"
~/.local/bin/virtualenv "${VENV_DIR}" -p python3.10 >> "${SETUP_LOG}" 2>&1
if [ ! -f "${VENV_DIR}/bin/python3" ]; then
  log "FATAL: venv creation failed"
  exit 2
fi

# ----------------------------------------------------------------------------
# Step 2: pip install vllm (let resolver pick vllm + torch combo)
# ----------------------------------------------------------------------------
log ""
log "Step 2: pip install vllm + deps (no version pin → resolver picks latest compatible)"

"${VENV_DIR}/bin/pip" install --upgrade pip wheel >> "${SETUP_LOG}" 2>&1

# Install order:
#   1. huggingface_hub first so hf_hub download works even if later steps hit issues
#   2. vllm last (pulls its own torch + transformers); let resolver pick
# vllm >= 0.7 has Phi-4 support; >= 0.7.3 has SmolLM3 support (per vllm release notes)
log "  installing huggingface_hub + vllm ..."
log "  (pip install cold start 5-15 min; logs stream to ${SETUP_LOG})"

"${VENV_DIR}/bin/pip" install \
    'huggingface_hub>=0.24' \
    >> "${SETUP_LOG}" 2>&1
HF_RC=$?
if [ "${HF_RC}" -ne 0 ]; then
  log "FATAL: huggingface_hub install exit=${HF_RC}"
  tail -15 "${SETUP_LOG}" | tee -a "${SETUP_LOG}"
  exit 2
fi
log "  huggingface_hub installed ✓"

# Try vllm latest minor available; fall back to 0.8 / 0.7 if latest has issues
log "  installing vllm (unpinned, resolver picks best) ..."
"${VENV_DIR}/bin/pip" install \
    'vllm' \
    --extra-index-url https://download.pytorch.org/whl/cu121 \
    >> "${SETUP_LOG}" 2>&1
VLLM_RC=$?
if [ "${VLLM_RC}" -ne 0 ]; then
  log "  latest vllm failed; trying vllm>=0.7,<0.9 ..."
  "${VENV_DIR}/bin/pip" install \
      'vllm>=0.7,<0.9' \
      --extra-index-url https://download.pytorch.org/whl/cu121 \
      >> "${SETUP_LOG}" 2>&1
  VLLM_RC=$?
fi
if [ "${VLLM_RC}" -ne 0 ]; then
  log "FATAL: vllm install exit=${VLLM_RC}; tail ${SETUP_LOG}:"
  tail -30 "${SETUP_LOG}"
  exit 2
fi

# Final check
log "  installed versions:"
"${VENV_DIR}/bin/python3" -c "
import torch, vllm, transformers, huggingface_hub
print(f'  torch={torch.__version__} cuda_available={torch.cuda.is_available()}')
print(f'  vllm={vllm.__version__}')
print(f'  transformers={transformers.__version__}')
print(f'  huggingface_hub={huggingface_hub.__version__}')
" 2>&1 | tee -a "${SETUP_LOG}"

# ----------------------------------------------------------------------------
# Step 3a: download microsoft/Phi-4-mini-instruct (primary)
# ----------------------------------------------------------------------------
log ""
log "Step 3a: download ${PHI4_NAME}"

if [ -d "${PHI4_DIR}" ] && ls "${PHI4_DIR}"/*.safetensors >/dev/null 2>&1; then
  log "  already present at ${PHI4_DIR}; skipping."
else
  mkdir -p "${PHI4_DIR}"
  HF_ENDPOINT="${HF_ENDPOINT}" HF_HOME="${HF_HOME}" \
    "${VENV_DIR}/bin/huggingface-cli" download \
      "${PHI4_NAME}" \
      --local-dir "${PHI4_DIR}" \
      --local-dir-use-symlinks False \
      >> "${SETUP_LOG}" 2>&1
  PHI4_RC=$?
  log "  Phi-4-mini download exit=${PHI4_RC}"
  du -sh "${PHI4_DIR}" 2>&1 | tee -a "${SETUP_LOG}"
fi

# ----------------------------------------------------------------------------
# Step 3b: download HuggingFaceTB/SmolLM3-3B (control)
# ----------------------------------------------------------------------------
log ""
log "Step 3b: download ${SMOLLM3_NAME}"

if [ -d "${SMOLLM3_DIR}" ] && ls "${SMOLLM3_DIR}"/*.safetensors >/dev/null 2>&1; then
  log "  already present at ${SMOLLM3_DIR}; skipping."
else
  mkdir -p "${SMOLLM3_DIR}"
  HF_ENDPOINT="${HF_ENDPOINT}" HF_HOME="${HF_HOME}" \
    "${VENV_DIR}/bin/huggingface-cli" download \
      "${SMOLLM3_NAME}" \
      --local-dir "${SMOLLM3_DIR}" \
      --local-dir-use-symlinks False \
      >> "${SETUP_LOG}" 2>&1
  SMOL_RC=$?
  log "  SmolLM3-3B download exit=${SMOL_RC}"
  du -sh "${SMOLLM3_DIR}" 2>&1 | tee -a "${SETUP_LOG}"
fi

# ----------------------------------------------------------------------------
# Step 4: smoke-check imports only (no actual model load)
# ----------------------------------------------------------------------------
log ""
log "Step 4: smoke-check vllm module import"
"${VENV_DIR}/bin/python3" -c "
from vllm import LLM, SamplingParams
print('vllm.LLM import OK')
" 2>&1 | tee -a "${SETUP_LOG}"

log ""
log "================================================================"
log "R42 E-5 v2 setup COMPLETE."
log "  venv:     ${VENV_DIR}"
log "  primary:  ${PHI4_DIR}  (${PHI4_NAME})"
log "  control:  ${SMOLLM3_DIR}  (${SMOLLM3_NAME})"
log ""
log "  To start Phi-4-mini vLLM server on 1× RTX 3090 (example):"
log "    nohup ${VENV_DIR}/bin/python3 -m vllm.entrypoints.openai.api_server \\"
log "      --model ${PHI4_DIR} \\"
log "      --served-model-name phi4-mini \\"
log "      --port 8001 --tensor-parallel-size 1 --dtype bfloat16 \\"
log "      --gpu-memory-utilization 0.85 --trust-remote-code \\"
log "      > logs/vllm_phi4_mini_\$(date +%Y%m%d_%H%M%S).log 2>&1 &"
log ""
log "  probe:   curl -s http://localhost:8001/v1/models | python3 -m json.tool"
log "================================================================"
