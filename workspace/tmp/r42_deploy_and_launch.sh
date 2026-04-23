#!/bin/bash
# R42 helper: move uploaded files from /tmp/r42_uploads/ to canonical paths
# + launch vllm env setup in background + dry-run the resume orchestrator.
set -u
REPO=/media/data3/dengkw/idea04
STAGING=/tmp/r42_uploads

echo "=== Step 1: move R42 uploads to canonical paths ==="
install -m 0755 "${STAGING}/u_exec_008_resume.sh" "${REPO}/workspace/tmp/u_exec_008_resume.sh"
install -m 0755 "${STAGING}/r42_vllm_env_setup.sh" "${REPO}/workspace/tmp/r42_vllm_env_setup.sh"
install -m 0644 "${STAGING}/runner.py" "${REPO}/workspace/idea04_core/runner.py"
install -m 0644 "${STAGING}/validate_logs.py" "${REPO}/scripts/validate_logs.py"
install -m 0644 "${STAGING}/run_e017_fullval_seed.py" "${REPO}/scripts/run_e017_fullval_seed.py"
echo "  moved 5 files"

echo ""
echo "=== Step 2: sanity run updated validate_logs on seed=42 ==="
cd "${REPO}"
python3 scripts/validate_logs.py artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124129_seed42/edo_stage2_chain 2>&1 | tail -3 || true

echo ""
echo "=== Step 3: run unit tests on updated runner.py (R42 fsync + R41g cleanup) ==="
cd "${REPO}"
if [ -f workspace/idea04_core/test_r41g_runner_resume_integrity.py ]; then
  python3 -m pytest workspace/idea04_core/test_r41g_runner_resume_integrity.py -q 2>&1 | tail -10
fi

echo ""
echo "=== Step 4: launch R42 vllm env setup in background ==="
cd "${REPO}"
TS="$(date +%Y%m%d_%H%M%S)"
VLLM_SETUP_LOG="logs/r42_vllm_env_setup_${TS}_bg.log"
nohup bash workspace/tmp/r42_vllm_env_setup.sh > "${VLLM_SETUP_LOG}" 2>&1 &
VLLM_PID=$!
disown || true
sleep 2
echo "  vllm setup PID=${VLLM_PID}"
echo "  log=${VLLM_SETUP_LOG}"
ps -p ${VLLM_PID} 2>&1 || echo "  (NOT ALIVE — check log)"

echo ""
echo "=== Step 5: dry-run resume orchestrator (no processes launched) ==="
cd "${REPO}"
bash workspace/tmp/u_exec_008_resume.sh --dry-run 2>&1 | tail -80

echo ""
echo "================================================================"
echo "R42 deploy + launch DONE"
echo "  tail -f ${REPO}/${VLLM_SETUP_LOG}"
echo "================================================================"
