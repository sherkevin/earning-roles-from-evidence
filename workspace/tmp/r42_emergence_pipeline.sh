#!/bin/bash
# ============================================================================
# R42 emergence pipeline: vLLM server launch + Phi-4-mini smoke
# ============================================================================
# Purpose (R41h pivot Option A/C, user-ACK 2026-04-21):
#   End-to-end orchestrator that waits for vLLM env + Phi-4-mini model to be
#   ready, launches vllm OpenAI-compat server on GPU 1 port 8001, probes
#   readiness, then runs two back-to-back smoke batches:
#
#     (a) Phi-4-mini × single_agent   × HotpotQA n=5   (emergence NULL baseline)
#     (b) Phi-4-mini × edo_stage2_chain × HotpotQA n=5 (emergence EXPT backbone)
#
#   If both pass, scale to n=50 for the same pair. Emit Δ_Phi4 = F1_multi − F1_single
#   which is the falsifiable emergence metric (cf. small_model_emergence_plan.md §4).
#
# Why engineer runs this (not scientist):
#   User R42 ACK "你去执行这些操作，注意模型和实验都要放在服务器上".
#   Model (Phi-4-mini-instruct + SmolLM3-3B) and experiments run server-only.
#   Engineer does NOT touch edo_paper.tex or run reviewer batches.
#
# Idempotency:
#   - Step 1 pre-flight: skip if vLLM server already responding on :8001
#   - Step 2 smoke: skip if run_dir/metrics.json already exists
#   - Safe to re-run after partial completion
#
# Cross-ref:
#   - docs/paper/small_model_emergence_plan.md §4 (emergence falsifiable form)
#   - configs/llm.json local_vllm block (R42 E-6 routing)
#   - workspace/idea04_core/llm_providers.py _is_local_vllm_routable (R42 E-6)
#   - workspace/idea04_core/methods.py:285,450 (single_agent method, pre-existing)
# ============================================================================

set -u
cd /media/data3/dengkw/idea04
mkdir -p logs artifacts/emergence artifacts/monitor

TS="$(date +%Y%m%d_%H%M%S)"
PIPELINE_LOG="logs/r42_emergence_pipeline_${TS}.log"
PID_FILE="logs/r42_emergence_pids_${TS}.txt"

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${PIPELINE_LOG}"
}

VENV_DIR="/media/data3/dengkw/venvs/vllm-py310"
MODEL_DIR="/media/data3/dengkw/models/phi4_mini_instruct"
SERVED_NAME="phi4-mini"
VLLM_PORT=8001
VLLM_GPU=1

# ----------------------------------------------------------------------------
# Step 0: env + model readiness checks
# ----------------------------------------------------------------------------
log "================================================================"
log "R42 emergence pipeline (Phi-4-mini × {single_agent, edo_stage2_chain})"
log "================================================================"

log ""
log "Step 0: env + model readiness"
if [ ! -f "${VENV_DIR}/bin/python3" ]; then
  log "ABORT: venv not ready at ${VENV_DIR}. Re-run r42_vllm_env_setup_v2.sh first."
  exit 2
fi
if ! "${VENV_DIR}/bin/python3" -c "import vllm" >/dev/null 2>&1; then
  log "ABORT: vllm not installed in venv. Check r42_vllm_env_setup_v2 log."
  exit 2
fi
if [ ! -d "${MODEL_DIR}" ] || ! ls "${MODEL_DIR}"/*.safetensors >/dev/null 2>&1; then
  log "ABORT: Phi-4-mini model not ready at ${MODEL_DIR}."
  log "       HF mirror download is still running — wait + re-run."
  exit 2
fi
log "Step 0 ✓ venv + model both ready."

# ----------------------------------------------------------------------------
# Step 1: launch vllm OpenAI-compat server (on GPU 1, port 8001)
# ----------------------------------------------------------------------------
log ""
log "Step 1: ensure vllm server running on http://localhost:${VLLM_PORT}"

# Probe first
if curl -s --max-time 5 "http://localhost:${VLLM_PORT}/v1/models" 2>/dev/null | grep -q "${SERVED_NAME}"; then
  log "  vllm server already up on :${VLLM_PORT} — reusing."
else
  log "  no server on :${VLLM_PORT}; launching..."
  VLLM_LOG="logs/vllm_phi4_mini_${TS}.log"
  # R43 (2026-04-23) fix: server lacks system python3-dev; torch._inductor +
  # triton sampler both JIT-compile cuda_utils.c which needs Python.h.
  # Solution: extracted libpython3.10-dev + python3.10-dev .deb to
  # /media/data3/dengkw/python-headers-310/usr/include/python3.10 (userland, no
  # sudo) and point gcc at it via C_INCLUDE_PATH. Also keep --enforce-eager
  # as defense-in-depth to minimize torch.compile surface, and clear any
  # stale compile cache.
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
      --gpu-memory-utilization 0.85 \
      --trust-remote-code \
      --enforce-eager \
    > "${VLLM_LOG}" 2>&1 &
  VLLM_PID=$!
  disown || true
  echo "vllm_server pid=${VLLM_PID} gpu=${VLLM_GPU} port=${VLLM_PORT} log=${VLLM_LOG}" >> "${PID_FILE}"
  log "  vllm server PID=${VLLM_PID} log=${VLLM_LOG}"

  # Wait up to 3 min for server to come up
  log "  waiting for /v1/models to respond (up to 180 s)..."
  ready=0
  for i in $(seq 1 36); do
    sleep 5
    if curl -s --max-time 3 "http://localhost:${VLLM_PORT}/v1/models" 2>/dev/null | grep -q "${SERVED_NAME}"; then
      ready=1
      log "  vllm ready after ${i}×5 s (${i}0 s)"
      break
    fi
    # Check if process died
    if ! ps -p ${VLLM_PID} >/dev/null 2>&1; then
      log "  ABORT: vllm process ${VLLM_PID} died; tail log:"
      tail -20 "${VLLM_LOG}" | tee -a "${PIPELINE_LOG}"
      exit 3
    fi
  done
  if [ "${ready}" -eq 0 ]; then
    log "  ABORT: vllm did not respond within 180 s; tail log:"
    tail -20 "${VLLM_LOG}" | tee -a "${PIPELINE_LOG}"
    exit 3
  fi
fi

# Smoke the endpoint
log "  sanity: POST /v1/chat/completions with 'hello':"
RESP=$(curl -s --max-time 30 -X POST "http://localhost:${VLLM_PORT}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer EMPTY" \
  -d "{\"model\":\"${SERVED_NAME}\",\"messages\":[{\"role\":\"user\",\"content\":\"say hi\"}],\"max_tokens\":16,\"temperature\":0.0}")
log "  response (first 300 char): ${RESP:0:300}"
if ! echo "$RESP" | grep -q '"content"'; then
  log "  WARN: vllm server did not return a proper chat completion. Continuing anyway."
fi

# ----------------------------------------------------------------------------
# Step 2: run Phi-4-mini smoke batches (single_agent + edo_stage2_chain)
# ----------------------------------------------------------------------------
log ""
log "Step 2: run emergence smoke — Phi-4-mini × {single_agent, edo_stage2_chain} × HotpotQA n=5"

SAMPLES="/media/data3/dengkw/idea04/artifacts/seed/hotpotqa_validation_100.jsonl"
OUT_ROOT="/media/data3/dengkw/idea04/artifacts/emergence/phi4_mini_n5_${TS}"
mkdir -p "${OUT_ROOT}"
export OUT_ROOT

# All Phi-4-mini runs force local_vllm backend via env override; this bypasses
# any newapi / oversea auto-routing and points the runner at localhost:8001.
export LLM_BACKEND="local_vllm"
export LLM_BASE_URL="http://localhost:${VLLM_PORT}/v1"
export LLM_API_KEY="EMPTY"
export LLM_MODEL="${SERVED_NAME}"
# Skip quota pre-flight (it probes newapi which has nothing to do with phi-4)
export SKIP_QUOTA_PREFLIGHT=1

run_smoke(){
  local method="$1"
  local out_dir="${OUT_ROOT}/${method}"
  if [ -f "${out_dir}/metrics.json" ]; then
    log "  ${method}: already done (metrics.json present); skipping."
    return 0
  fi
  mkdir -p "${out_dir}"
  log "  launching ${method} n=5 ..."
  local method_log="logs/r42_phi4_smoke_${method}_${TS}.log"
  "${VENV_DIR}/bin/python3" -u scripts/run_e017_fullval_seed.py \
      --seed 42 \
      --method "${method}" \
      --workers 1 \
      --config configs/phi4_mini_hotpotqa_smoke.yaml \
      --n 5 \
      --samples-jsonl "${SAMPLES}" \
      --run-dir "${out_dir}" \
      --skip-preflight \
      --consec-zero-halt 0 \
    > "${method_log}" 2>&1
  local rc=$?
  echo "smoke_${method} rc=${rc} log=${method_log}" >> "${PID_FILE}"
  if [ "${rc}" -ne 0 ]; then
    log "    ${method}: FAILED rc=${rc}; tail log:"
    tail -40 "${method_log}" | tee -a "${PIPELINE_LOG}"
    return "${rc}"
  fi
  log "    ${method}: command finished rc=0 log=${method_log}"
}

# fixed_peer_calibrated can stand in for single-agent via "hop_count=1" but here
# we explicitly use the pre-existing METHOD_NAMES single_agent.
# Run sequentially to avoid GPU contention and make failure attribution clean.
if ! run_smoke single_agent; then
  log "  single_agent smoke failed; continuing to edo_stage2_chain for diagnosis."
fi
if ! run_smoke edo_stage2_chain; then
  log "  edo_stage2_chain smoke failed; report will mark the run incomplete."
fi

# Wait for both to finish
log "  checking smoke method outputs..."
for method in single_agent edo_stage2_chain; do
  if [ ! -f "${OUT_ROOT}/${method}/metrics.json" ]; then
    log "  ${method}: missing metrics.json after command; tail log:"
    tail -30 "logs/r42_phi4_smoke_${method}_${TS}.log" | tee -a "${PIPELINE_LOG}"
    continue
  fi
  log "  ${method}: DONE"
  "${VENV_DIR}/bin/python3" -c "
import json
d = json.load(open('${OUT_ROOT}/${method}/metrics.json'))
print(f'    F1={d.get(\"answer_f1\", \"?\")}  EM={d.get(\"answer_em\", \"?\")}  n={d.get(\"sample_count\", \"?\")}  tok/sample={d.get(\"api_total_tokens_per_sample\", \"?\")}')
" 2>&1 | tee -a "${PIPELINE_LOG}"
done

# ----------------------------------------------------------------------------
# Step 3: compute Δ_Phi4 and emit emergence report
# ----------------------------------------------------------------------------
log ""
log "Step 3: emergence metric Δ_Phi4 = F1_multi − F1_single"

"${VENV_DIR}/bin/python3" - <<'PYEOF' | tee -a "${PIPELINE_LOG}"
import json, os
root = os.environ.get("OUT_ROOT") or ""
if not root:
    # Derive from the log environment (fallback)
    import glob
    candidates = sorted(glob.glob("/media/data3/dengkw/idea04/artifacts/emergence/phi4_mini_n5_*/"))
    root = candidates[-1].rstrip("/") if candidates else ""

def _metric(p):
    try:
        return json.load(open(p))
    except Exception:
        return None

single = _metric(f"{root}/single_agent/metrics.json") if root else None
multi  = _metric(f"{root}/edo_stage2_chain/metrics.json") if root else None
if not single or not multi:
    print(f"  [emergence] incomplete: single={bool(single)} multi={bool(multi)}")
else:
    delta_f1 = multi["answer_f1"] - single["answer_f1"]
    delta_em = multi["answer_em"] - single["answer_em"]
    print(f"  [emergence] F1_single={single['answer_f1']:.4f} F1_multi={multi['answer_f1']:.4f}")
    print(f"  [emergence] EM_single={single['answer_em']:.4f} EM_multi={multi['answer_em']:.4f}")
    print(f"  [emergence] Δ_Phi4_F1 = {delta_f1:+.4f}  ({'EMERGENCE' if delta_f1 > 0 else 'NULL'})")
    print(f"  [emergence] Δ_Phi4_EM = {delta_em:+.4f}")
PYEOF

log ""
log "================================================================"
log "R42 emergence pipeline DONE"
log "  log:    ${PIPELINE_LOG}"
log "  PIDs:   ${PID_FILE}"
log "  out:    ${OUT_ROOT}"
log ""
log "  Next steps after smoke success:"
log "    - scale to n=50 each with the same script (pass --n 50 to run_e017)"
log "    - add SmolLM3-3B control run (swap VLLM_PORT=8002, model=smollm3_3b)"
log "    - add gpt-4.1-mini × single_agent n=5 smoke when U-EXEC-008 recharges"
log "      (completes Δ_large side of the emergence comparison)"
log "================================================================"
