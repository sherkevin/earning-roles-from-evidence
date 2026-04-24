#!/bin/bash
# ============================================================================
# R43 SmolLM3-3B parallel emergence pipeline: vLLM on GPU 4 port 8002
# ============================================================================
# Purpose (R43 2026-04-23):
#   Second vLLM server for SmolLM3-3B as a control backbone in the emergence
#   experiment (in addition to Phi-4-mini on GPU 1 port 8001). Reuses the same
#   run_e017_fullval_seed.py harness with LLM_BACKEND=local_vllm override so
#   no newapi quota is touched.
#
# Why parallel:
#   GPU 4 is 24 GiB idle, SmolLM3-3B bf16 ≈ 6 GiB, plenty of headroom. Running
#   both backbones concurrently halves calendar time to collect the 3-data-
#   point emergence curve (Phi-4-mini / SmolLM3-3B / gpt-4.1-mini).
#
# Cross-ref:
#   - r42_emergence_pipeline.sh (Phi-4-mini counterpart on GPU 1 port 8001)
#   - docs/paper/small_model_emergence_plan.md §4
#   - Python.h / pyconfig.h userland fix: /media/data3/dengkw/python-headers-310/
# ============================================================================

set -u
cd /media/data3/dengkw/idea04
mkdir -p logs artifacts/emergence

TS="$(date +%Y%m%d_%H%M%S)"
PIPELINE_LOG="logs/r43_smollm3_pipeline_${TS}.log"
PID_FILE="logs/r43_smollm3_pids_${TS}.txt"

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${PIPELINE_LOG}"
}

VENV_DIR="/media/data3/dengkw/venvs/vllm-py310"
MODEL_DIR="/media/data3/dengkw/models/smollm3_3b"
SERVED_NAME="smollm3-3b"
VLLM_PORT=8002
VLLM_GPU=4

log "================================================================"
log "R43 SmolLM3-3B emergence pipeline (control backbone)"
log "================================================================"

if [ ! -f "${VENV_DIR}/bin/python3" ]; then
  log "ABORT: venv not ready at ${VENV_DIR}."
  exit 2
fi
if [ ! -d "${MODEL_DIR}" ] || ! ls "${MODEL_DIR}"/*.safetensors >/dev/null 2>&1; then
  log "ABORT: SmolLM3-3B model not ready at ${MODEL_DIR}."
  exit 2
fi
log "Step 0 ✓ venv + model both ready."

log ""
log "Step 1: ensure vllm server on http://localhost:${VLLM_PORT} (GPU ${VLLM_GPU})"
if curl -s --max-time 5 "http://localhost:${VLLM_PORT}/v1/models" 2>/dev/null | grep -q "${SERVED_NAME}"; then
  log "  vllm server already up on :${VLLM_PORT} — reusing."
else
  log "  no server on :${VLLM_PORT}; launching..."
  VLLM_LOG="logs/vllm_smollm3_${TS}.log"
  rm -rf /home/dengkw/.cache/vllm/torch_compile_cache/ 2>/dev/null || true
  export C_INCLUDE_PATH="/media/data3/dengkw/python-headers-310/usr/include/python3.10:${C_INCLUDE_PATH:-}"
  export CPLUS_INCLUDE_PATH="/media/data3/dengkw/python-headers-310/usr/include/python3.10:${CPLUS_INCLUDE_PATH:-}"
  CUDA_VISIBLE_DEVICES=${VLLM_GPU} \
  C_INCLUDE_PATH="/media/data3/dengkw/python-headers-310/usr/include/python3.10:${C_INCLUDE_PATH:-}" \
  CPLUS_INCLUDE_PATH="/media/data3/dengkw/python-headers-310/usr/include/python3.10:${CPLUS_INCLUDE_PATH:-}" \
    nohup "${VENV_DIR}/bin/python3" -m vllm.entrypoints.openai.api_server \
      --model "${MODEL_DIR}" \
      --served-model-name "${SERVED_NAME}" \
      --port ${VLLM_PORT} \
      --tensor-parallel-size 1 \
      --dtype bfloat16 \
      --gpu-memory-utilization 0.90 \
      --max-model-len 32768 \
      --trust-remote-code \
      --enforce-eager \
    > "${VLLM_LOG}" 2>&1 &
  VLLM_PID=$!
  disown || true
  echo "vllm_server pid=${VLLM_PID} gpu=${VLLM_GPU} port=${VLLM_PORT} log=${VLLM_LOG}" >> "${PID_FILE}"
  log "  vllm server PID=${VLLM_PID} log=${VLLM_LOG}"

  log "  waiting for /v1/models to respond (up to 180 s)..."
  ready=0
  for i in $(seq 1 36); do
    sleep 5
    if curl -s --max-time 3 "http://localhost:${VLLM_PORT}/v1/models" 2>/dev/null | grep -q "${SERVED_NAME}"; then
      ready=1
      log "  vllm ready after ${i}x5 s (${i}0 s)"
      break
    fi
    if ! ps -p ${VLLM_PID} >/dev/null 2>&1; then
      log "  ABORT: vllm process ${VLLM_PID} died; tail log:"
      tail -30 "${VLLM_LOG}" | tee -a "${PIPELINE_LOG}"
      exit 3
    fi
  done
  if [ "${ready}" -eq 0 ]; then
    log "  ABORT: vllm did not respond within 180 s; tail log:"
    tail -30 "${VLLM_LOG}" | tee -a "${PIPELINE_LOG}"
    exit 3
  fi
fi

log "  sanity: POST /v1/chat/completions with 'hello':"
RESP=$(curl -s --max-time 30 -X POST "http://localhost:${VLLM_PORT}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer EMPTY" \
  -d "{\"model\":\"${SERVED_NAME}\",\"messages\":[{\"role\":\"user\",\"content\":\"say hi\"}],\"max_tokens\":16,\"temperature\":0.0}")
log "  response (first 300 char): ${RESP:0:300}"

log ""
log "Step 2: run SmolLM3-3B smoke — {single_agent, edo_stage2_chain} x HotpotQA n=5"

SAMPLES="/media/data3/dengkw/idea04/artifacts/seed/hotpotqa_validation_100.jsonl"
OUT_ROOT="/media/data3/dengkw/idea04/artifacts/emergence/smollm3_3b_n5_${TS}"
mkdir -p "${OUT_ROOT}"

export LLM_BACKEND="local_vllm"
export LLM_BASE_URL="http://localhost:${VLLM_PORT}/v1"
export LLM_API_KEY="EMPTY"
export LLM_MODEL="${SERVED_NAME}"
export SKIP_QUOTA_PREFLIGHT=1

run_smoke(){
  local method="$1"
  local out_dir="${OUT_ROOT}/${method}"
  if [ -f "${out_dir}/metrics.json" ]; then
    log "  ${method}: already done; skipping."
    return 0
  fi
  mkdir -p "${out_dir}"
  log "  launching ${method} n=5 ..."
  local method_log="logs/r43_smollm3_smoke_${method}_${TS}.log"
  nohup "${VENV_DIR}/bin/python3" -u scripts/run_e017_fullval_seed.py \
      --seed 42 \
      --method "${method}" \
      --workers 4 \
      --n 5 \
      --samples-jsonl "${SAMPLES}" \
      --run-dir "${out_dir}" \
      --skip-preflight \
      --consec-zero-halt 0 \
    > "${method_log}" 2>&1 &
  local pid=$!
  disown || true
  echo "smoke_${method} pid=${pid} log=${method_log}" >> "${PID_FILE}"
  log "    ${method} PID=${pid} log=${method_log}"
}

run_smoke single_agent
sleep 2
run_smoke edo_stage2_chain

log "  waiting for both smoke methods to finish (up to 20 min each)..."
for method in single_agent edo_stage2_chain; do
  t=0
  while [ ! -f "${OUT_ROOT}/${method}/metrics.json" ] && [ ${t} -lt 1200 ]; do
    sleep 30
    t=$((t+30))
  done
  if [ ! -f "${OUT_ROOT}/${method}/metrics.json" ]; then
    log "  ${method}: TIMEOUT; tail log:"
    tail -30 "logs/r43_smollm3_smoke_${method}_${TS}.log" | tee -a "${PIPELINE_LOG}"
    continue
  fi
  log "  ${method}: DONE"
  "${VENV_DIR}/bin/python3" -c "
import json
d = json.load(open('${OUT_ROOT}/${method}/metrics.json'))
print(f'    F1={d.get(\"answer_f1\", \"?\")}  EM={d.get(\"answer_em\", \"?\")}  n={d.get(\"sample_count\", \"?\")}  tok/sample={d.get(\"api_total_tokens_per_sample\", \"?\")}')
" 2>&1 | tee -a "${PIPELINE_LOG}"
done

log ""
log "Step 3: emergence metric Delta_SmolLM3 = F1_multi - F1_single"

export OUT_ROOT
"${VENV_DIR}/bin/python3" - <<'PYEOF' | tee -a "${PIPELINE_LOG}"
import json, os
root = os.environ.get("OUT_ROOT") or ""
def _metric(p):
    try: return json.load(open(p))
    except: return None
single = _metric(f"{root}/single_agent/metrics.json")
multi  = _metric(f"{root}/edo_stage2_chain/metrics.json")
if not single or not multi:
    print(f"  [emergence] incomplete: single={bool(single)} multi={bool(multi)}")
else:
    delta = multi["answer_f1"] - single["answer_f1"]
    print(f"  [emergence] F1_single={single['answer_f1']:.4f}  F1_multi={multi['answer_f1']:.4f}")
    print(f"  [emergence] Delta_SmolLM3_F1 = {delta:+.4f}  ({'EMERGENCE' if delta > 0 else 'NULL'})")
PYEOF

log ""
log "================================================================"
log "R43 SmolLM3-3B emergence pipeline DONE"
log "  log: ${PIPELINE_LOG}"
log "  out: ${OUT_ROOT}"
log "================================================================"
