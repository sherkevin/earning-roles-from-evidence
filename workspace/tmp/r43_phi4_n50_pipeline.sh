#!/usr/bin/env bash
# R43 Phi-4-mini n=50 diagnostic pipeline.
# Runs after the repaired n=5 smoke. This is still smoke/diagnostic evidence,
# not an E-030 paper-grade canonical gpt-4.1-mini matrix cell.

set -u
cd /media/data3/dengkw/idea04

mkdir -p logs artifacts/emergence
TS="$(date +%Y%m%d_%H%M%S)"
LOG="logs/r43_phi4_n50_pipeline_${TS}.log"
OUT_ROOT="artifacts/emergence/phi4_mini_n50_${TS}"

log() {
  echo "[$(date '+%F %T')] $*" | tee -a "${LOG}"
}

export LLM_BACKEND="local_vllm"
export LLM_BASE_URL="http://localhost:8001/v1"
export LLM_API_KEY="EMPTY"
export LLM_MODEL="phi4-mini"
export SKIP_QUOTA_PREFLIGHT=1

log "R43 Phi-4-mini n=50 diagnostic pipeline"
log "out=${OUT_ROOT}"
log "backend=${LLM_BACKEND} base=${LLM_BASE_URL} model=${LLM_MODEL}"

if ! curl -s --max-time 5 "${LLM_BASE_URL}/models" | grep -q "phi4-mini"; then
  log "ABORT: local vLLM server on port 8001 is not serving phi4-mini."
  exit 2
fi

run_one() {
  local method="$1"
  local run_dir="${OUT_ROOT}/${method}"
  local method_log="logs/r43_phi4_n50_${method}_${TS}.log"
  mkdir -p "${run_dir}"
  if [ -f "${run_dir}/metrics.json" ]; then
    log "${method}: metrics already present; skipping."
    return 0
  fi
  log "${method}: launching n=50"
  python3 -u scripts/run_e017_fullval_seed.py \
    --seed 42 \
    --method "${method}" \
    --workers 1 \
    --config configs/phi4_mini_hotpotqa_smoke.yaml \
    --n 50 \
    --samples-jsonl artifacts/seed/hotpotqa_validation_100.jsonl \
    --run-dir "${run_dir}" \
    --skip-preflight \
    --consec-zero-halt 0 \
    > "${method_log}" 2>&1
  local rc=$?
  if [ "${rc}" -ne 0 ]; then
    log "${method}: FAILED rc=${rc}; tail follows"
    tail -60 "${method_log}" | tee -a "${LOG}"
    return "${rc}"
  fi
  log "${method}: DONE"
  python3 - <<PY | tee -a "${LOG}"
import json
d=json.load(open("${run_dir}/metrics.json"))
print("${method}: F1={:.4f} EM={:.4f} n={} tok/sample={}".format(
    d.get("answer_f1", 0.0),
    d.get("answer_em", 0.0),
    d.get("sample_count", "?"),
    d.get("api_total_tokens_per_sample", "?"),
))
PY
}

run_one single_agent
run_one edo_stage2_chain

python3 - <<PY | tee -a "${LOG}"
import json
from pathlib import Path
root = Path("${OUT_ROOT}")
single = json.load(open(root / "single_agent" / "metrics.json"))
multi = json.load(open(root / "edo_stage2_chain" / "metrics.json"))
print("Delta_Phi4_n50_F1={:+.4f}".format(multi["answer_f1"] - single["answer_f1"]))
print("Delta_Phi4_n50_EM={:+.4f}".format(multi["answer_em"] - single["answer_em"]))
PY

log "DONE out=${OUT_ROOT}"
