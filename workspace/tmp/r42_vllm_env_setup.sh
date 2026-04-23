#!/bin/bash
# ============================================================================
# R42 E-5: vLLM environment setup + Qwen2.5-7B-Instruct model download
# ============================================================================
# Purpose:
#   Pre-build the vLLM serving environment on the idle server GPUs so that
#   if user later approves R41h emergence pivot (Option A/C), engineer can
#   start smoke experiments in 5 min instead of 2-3 hours.
#
# Scope (intentionally conservative, no-pivot-commit):
#   - Create new venv /media/data3/dengkw/venvs/vllm-py310/
#   - Install vllm 0.6.x + torch 2.4.x + transformers (~5 GB pip)
#   - Download Qwen/Qwen2.5-7B-Instruct (~14 GB) via HF mirror
#     (literature-confirmed in NAACL 2025 panel paper, HotpotQA F1=0.5946 baseline)
#   - NO llm.json modification, NO single_agent method, NO smoke experiments.
#     Those wait on scientist S-179 decision + user U-XXX-emergence-pivot-decide.
#
# Even if user later picks Option B (stay on newapi), the venv is reusable
# for any future local inference work + Qwen2.5-7B is a canonical reference
# point independent of emergence framing (e.g., reviewer may ask "what does
# a non-API open model do on your benchmark" — we have the weights ready).
#
# Idempotency:
#   - Skips venv creation if already exists
#   - Skips model download if directory exists + has safetensors
#   - Safe to re-run
#
# Cost:
#   - Disk: ~14 GB (model) + ~5 GB (venv pip) = ~19 GB, well within 662 GB free
#   - Time: ~5 min pip + ~45-90 min model download (depends on HF mirror speed)
#   - Bandwidth: ~14 GB over HF mirror
# ============================================================================

set -u
cd /media/data3/dengkw/idea04
mkdir -p logs artifacts/monitor

TS="$(date +%Y%m%d_%H%M%S)"
SETUP_LOG="logs/r42_vllm_env_setup_${TS}.log"

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${SETUP_LOG}"
}

VENV_ROOT="/media/data3/dengkw/venvs"
VENV_NAME="vllm-py310"
VENV_DIR="${VENV_ROOT}/${VENV_NAME}"
MODELS_ROOT="/media/data3/dengkw/models"
QWEN25_NAME="Qwen/Qwen2.5-7B-Instruct"
QWEN25_DIR="${MODELS_ROOT}/qwen25_7b_instruct"

# CRITICAL: /dev/sde2 (the "/" partition) is only 93 GB and currently 88 GB
# used (123 MB free). pip default TMPDIR=/tmp and pip cache=~/.cache/pip both
# land there and will fail with ENOSPC on multi-GB wheels (torch 800 MB +
# vllm deps). Redirect both to /media/data3 which has 662 GB free.
DATA3_TMP="/media/data3/dengkw/tmp"
DATA3_PIP_CACHE="/media/data3/dengkw/pip_cache"
mkdir -p "${DATA3_TMP}" "${DATA3_PIP_CACHE}"
export TMPDIR="${DATA3_TMP}"
export PIP_CACHE_DIR="${DATA3_PIP_CACHE}"

export HF_ENDPOINT="https://hf-mirror.com"
export HF_HOME="${MODELS_ROOT}/hf_home"

log "================================================================"
log "R42 E-5: vLLM env + Qwen2.5-7B-Instruct download"
log "  venv:       ${VENV_DIR}"
log "  model:      ${QWEN25_NAME} → ${QWEN25_DIR}"
log "  HF mirror:  ${HF_ENDPOINT}"
log "  HF_HOME:    ${HF_HOME}"
log "  TMPDIR:     ${TMPDIR}   (redirected away from full /)"
log "  PIP_CACHE:  ${PIP_CACHE_DIR}"
log "  / free:     $(df -h / | tail -1 | awk '{print \$4}')"
log "  /media/data3 free: $(df -h /media/data3 | tail -1 | awk '{print \$4}')"
log "================================================================"

# ----------------------------------------------------------------------------
# Step 1: create venv (if missing)
# ----------------------------------------------------------------------------
log ""
log "Step 1: create venv ${VENV_DIR} (if missing)"

mkdir -p "${VENV_ROOT}" "${MODELS_ROOT}" "${HF_HOME}"

if [ -d "${VENV_DIR}" ] && [ -f "${VENV_DIR}/bin/python3" ]; then
  log "  venv already exists; skipping creation."
else
  log "  creating venv via virtualenv ..."
  ~/.local/bin/virtualenv "${VENV_DIR}" -p python3.10 2>&1 | tee -a "${SETUP_LOG}"
fi

# Sanity
"${VENV_DIR}/bin/python3" --version 2>&1 | tee -a "${SETUP_LOG}"

# ----------------------------------------------------------------------------
# Step 2: install vllm + torch + transformers (if missing)
# ----------------------------------------------------------------------------
log ""
log "Step 2: pip install vllm + torch + transformers"

"${VENV_DIR}/bin/pip" install --upgrade pip 2>&1 | tail -5 | tee -a "${SETUP_LOG}"

# Check if already installed (idempotent).
# CRITICAL: do NOT pipe to tee — pipe's exit code is tee's (always 0) so
# the if-branch would unconditionally skip install. Redirect output to log
# without a pipe.
if "${VENV_DIR}/bin/python3" -c "import vllm, torch" >/dev/null 2>&1; then
  VLLM_VERSION=$("${VENV_DIR}/bin/python3" -c "import vllm; print(vllm.__version__)" 2>/dev/null || echo "?")
  log "  vllm (v${VLLM_VERSION}) + torch already installed; skipping pip install."
else
  log "  installing vllm 0.6.x + torch + transformers ..."
  log "  (this typically takes 5-15 min; log tail below)"
  # Use the HF mirror's proxy and pytorch official index. Tsinghua mirror
  # doesn't host vllm wheels of every minor; fall back to pypi default.
  "${VENV_DIR}/bin/pip" install \
      "torch==2.4.1" \
      "vllm==0.6.6.post1" \
      "transformers>=4.45,<4.50" \
      "huggingface_hub>=0.23,<0.27" \
      --extra-index-url https://download.pytorch.org/whl/cu121 \
      >> "${SETUP_LOG}" 2>&1
  PIP_RC=$?
  log "  pip install exit=${PIP_RC}"
  if [ "${PIP_RC}" -ne 0 ]; then
    log "  ABORT: pip install failed. Tail of SETUP_LOG for context:"
    tail -30 "${SETUP_LOG}"
    exit 2
  fi
fi

# Final sanity
log "  installed versions:"
"${VENV_DIR}/bin/python3" -c "
import torch, vllm, transformers
print(f'  torch={torch.__version__} cuda_available={torch.cuda.is_available()}')
print(f'  vllm={vllm.__version__}')
print(f'  transformers={transformers.__version__}')
" 2>&1 | tee -a "${SETUP_LOG}"

# ----------------------------------------------------------------------------
# Step 3: download Qwen2.5-7B-Instruct via HF mirror
# ----------------------------------------------------------------------------
log ""
log "Step 3: download ${QWEN25_NAME}"

if [ -d "${QWEN25_DIR}" ] && ls "${QWEN25_DIR}"/*.safetensors >/dev/null 2>&1; then
  log "  model already present at ${QWEN25_DIR}; skipping download."
else
  log "  downloading via huggingface-cli + HF_ENDPOINT=${HF_ENDPOINT} ..."
  mkdir -p "${QWEN25_DIR}"
  HF_ENDPOINT="${HF_ENDPOINT}" HF_HOME="${HF_HOME}" \
    "${VENV_DIR}/bin/huggingface-cli" download \
      "${QWEN25_NAME}" \
      --local-dir "${QWEN25_DIR}" \
      --local-dir-use-symlinks False \
      2>&1 | tail -20 | tee -a "${SETUP_LOG}"
fi

# Sanity: list + size
log "  ${QWEN25_DIR} size:"
du -sh "${QWEN25_DIR}" 2>&1 | tee -a "${SETUP_LOG}"
ls "${QWEN25_DIR}" 2>&1 | tee -a "${SETUP_LOG}"

# ----------------------------------------------------------------------------
# Step 4: smoke-check (load model on 1× RTX 3090 briefly, don't serve)
# ----------------------------------------------------------------------------
log ""
log "Step 4: smoke-load ${QWEN25_NAME} via vllm (import-only; no server launch)"

# This is a cheap import check + does NOT start a vllm server.
# Full serve command is documented below for the pivot session.
"${VENV_DIR}/bin/python3" -c "
from vllm import LLM, SamplingParams
print('vllm LLM class import OK')
# Don't actually load model — 14 GB load can take minutes and holds GPU.
" 2>&1 | tee -a "${SETUP_LOG}"

log ""
log "================================================================"
log "R42 E-5 setup COMPLETE."
log "  venv:  ${VENV_DIR}"
log "  model: ${QWEN25_DIR}"
log ""
log "  If user approves R41h pivot (Option A/C), to start vllm server:"
log ""
log "    nohup ${VENV_DIR}/bin/python3 -m vllm.entrypoints.openai.api_server \\"
log "      --model ${QWEN25_DIR} \\"
log "      --served-model-name qwen25-7b \\"
log "      --port 8001 --tensor-parallel-size 1 --dtype bfloat16 \\"
log "      --gpu-memory-utilization 0.85 \\"
log "      > logs/vllm_qwen25_7b_\$(date +%Y%m%d_%H%M%S).log 2>&1 &"
log ""
log "  Then probe:  curl -s http://localhost:8001/v1/models | python3 -m json.tool"
log "================================================================"
