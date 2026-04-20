#!/bin/bash
# R41 smoke + monitor launcher — fire MAD + MA-RAG smokes in parallel with E-017,
# then spin a lightweight watcher to snapshot all 4 jobs every 5 min.
#
# Per user instruction (2026-04-20, Session R41): "尽量把远程服务器的资源都利用上,
# 减少实验等待时间 ... 挂一个等待脚本到后台然后继续做其他事情".
#
# Invariants:
#   - E-020 pre-flight probe already gates each smoke launch (SKIP_QUOTA_PREFLIGHT unset).
#   - smoke workers = 1 each → total newapi load = E-017 16 workers + 2 smoke 1-worker
#     = 18 ≈ within observed safe envelope (16 from [u_rollback_001_path_a_landed_20260420]
#     operational corollary; 2 extra single-worker batches are low-burst).
#   - smokes write to timestamped dirs under artifacts/external_baselines/<system>/
#     so no existing data is touched.
#   - watcher itself uses 0 LLM calls.

set -u
cd /media/data3/dengkw/idea04

TS="$(date +%Y%m%d_%H%M%S)"
MONITOR_DIR="artifacts/monitor"
WATCH_LOG="${MONITOR_DIR}/r41_watch_${TS}.log"
MAD_OUT="artifacts/external_baselines/mad/r41_smoke_${TS}"
MARAG_OUT="artifacts/external_baselines/marag/r41_smoke_${TS}"

mkdir -p "${MONITOR_DIR}" "${MAD_OUT}" "${MARAG_OUT}" logs/r41_smoke

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${WATCH_LOG}"
}

log "=============================================================="
log "R41 PARALLEL SMOKE + MONITOR LAUNCHER"
log "  E-017 seed=42 workers already running (PID 321426 stage2 / 321436 stage1)"
log "  scheduler PID 321499 will auto-chain seed=43 + seed=44"
log "  this script: fire MAD + MA-RAG smoke, then watch all 4 every 5 min"
log "=============================================================="

# ---------------------------------------------------------------------------
# Step A: Pre-flight quota probe (STOP if depleted)
# ---------------------------------------------------------------------------
log "Step A: quota pre-flight probe"
if ! bash workspace/tmp/newapi_quota_probe.sh 2>&1 | tee -a "${WATCH_LOG}" | grep -q "newapi ACTIVE"; then
  log "ABORT: newapi not ACTIVE; smokes will not launch."
  exit 2
fi
log "  ✓ newapi ACTIVE"

# ---------------------------------------------------------------------------
# Step B: Launch MAD smoke (5 samples, 1 agent-triplet × 2 rounds)
# ---------------------------------------------------------------------------
log "Step B: launching E-015 MAD smoke (5 samples, agents=3 rounds=2)"
(
  cd external_baselines/mad
  source venv_mad/bin/activate 2>/dev/null || true
  # Fall back to system python3 if venv isn't importable
  PYBIN=venv_mad/bin/python
  [ -x "${PYBIN}" ] || PYBIN=python3
  cd /media/data3/dengkw/idea04
  nohup "external_baselines/mad/${PYBIN##*/venv_mad/}" \
    external_baselines/mad/hotpotqa/gen_hotpotqa.py \
      --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
      --n 5 --agents 3 --rounds 2 \
      --out-dir "${MAD_OUT}" \
    > logs/r41_smoke/mad_${TS}.log 2>&1 &
  echo $! > "${MAD_OUT}/.pid"
) || log "  WARNING: MAD launch subshell exited non-zero"
MAD_PID=$(cat "${MAD_OUT}/.pid" 2>/dev/null || echo "")
log "  MAD PID=${MAD_PID:-UNKNOWN}  log=logs/r41_smoke/mad_${TS}.log"

# ---------------------------------------------------------------------------
# Step C: Launch MA-RAG smoke (5 samples, Path A gold-context)
# ---------------------------------------------------------------------------
log "Step C: launching E-018 MA-RAG smoke (5 samples, Path A gold-context)"
(
  cd /media/data3/dengkw/idea04
  PYBIN=external_baselines/marag/venv_marag/bin/python
  [ -x "${PYBIN}" ] || PYBIN=python3
  nohup "${PYBIN}" external_baselines/marag/run_marag_hotpotqa.py \
      --samples-jsonl artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl \
      --n 5 \
      --out-dir "${MARAG_OUT}" \
    > logs/r41_smoke/marag_${TS}.log 2>&1 &
  echo $! > "${MARAG_OUT}/.pid"
) || log "  WARNING: MA-RAG launch subshell exited non-zero"
MARAG_PID=$(cat "${MARAG_OUT}/.pid" 2>/dev/null || echo "")
log "  MA-RAG PID=${MARAG_PID:-UNKNOWN}  log=logs/r41_smoke/marag_${TS}.log"

# ---------------------------------------------------------------------------
# Step D: Background watcher (every 5 min, appends to WATCH_LOG)
# ---------------------------------------------------------------------------
WATCH_STATE="${MONITOR_DIR}/r41_state_${TS}.json"

watcher_body(){
  while true; do
    S2_CKPT=$(wc -l < artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124129_seed42/edo_stage2_chain/_ckpt_preds.jsonl 2>/dev/null || echo 0)
    S1_CKPT=$(wc -l < artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124130_seed42/fixed_peer_calibrated/_ckpt_preds.jsonl 2>/dev/null || echo 0)
    S2_DONE=$([ -f artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124129_seed42/edo_stage2_chain/metrics.json ] && echo "DONE" || echo "running")
    S1_DONE=$([ -f artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124130_seed42/fixed_peer_calibrated/metrics.json ] && echo "DONE" || echo "running")
    MAD_ALIVE=$([ -n "${MAD_PID}" ] && kill -0 "${MAD_PID}" 2>/dev/null && echo "alive" || echo "exit")
    MARAG_ALIVE=$([ -n "${MARAG_PID}" ] && kill -0 "${MARAG_PID}" 2>/dev/null && echo "alive" || echo "exit")
    # seed 43/44 emergence
    S43=$(ls -d artifacts/round2_gpt41mini_stage2_fullval/run_*_seed43 2>/dev/null | head -1 || echo "")
    S44=$(ls -d artifacts/round2_gpt41mini_stage2_fullval/run_*_seed44 2>/dev/null | head -1 || echo "")

    log "SNAPSHOT seed42 s2=${S2_CKPT}/7405 ${S2_DONE} | s1=${S1_CKPT}/7405 ${S1_DONE} | MAD=${MAD_ALIVE} | MARAG=${MARAG_ALIVE} | seed43=${S43:-none} | seed44=${S44:-none}"

    # State JSON snapshot for programmatic reads
    cat > "${WATCH_STATE}" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "seed42_stage2_ckpt": ${S2_CKPT:-0},
  "seed42_stage2_done": "${S2_DONE}",
  "seed42_stage1_ckpt": ${S1_CKPT:-0},
  "seed42_stage1_done": "${S1_DONE}",
  "mad_smoke_status": "${MAD_ALIVE}",
  "mad_smoke_pid": "${MAD_PID:-}",
  "marag_smoke_status": "${MARAG_ALIVE}",
  "marag_smoke_pid": "${MARAG_PID:-}",
  "seed43_run_dir": "${S43}",
  "seed44_run_dir": "${S44}"
}
EOF

    # Quota health check every cycle — cheap (1 API call = $0.00001)
    Q=$(bash workspace/tmp/newapi_quota_probe.sh 2>/dev/null | grep 'STATUS:' | head -1)
    log "  quota: ${Q:-unknown}"

    # Stop when everything has ended
    if [ "${S2_DONE}" = "DONE" ] && [ "${S1_DONE}" = "DONE" ] \
       && [ "${MAD_ALIVE}" = "exit" ] && [ "${MARAG_ALIVE}" = "exit" ] \
       && [ -n "${S43}" ] && [ -f "${S43}/edo_stage2_chain/metrics.json" ] \
       && [ -n "${S44}" ] && [ -f "${S44}/edo_stage2_chain/metrics.json" ]; then
      log "ALL 4 BATCHES COMPLETE — watcher exiting"
      break
    fi

    sleep 300
  done
}

nohup bash -c "$(declare -f log watcher_body); WATCH_LOG='${WATCH_LOG}' MONITOR_DIR='${MONITOR_DIR}' WATCH_STATE='${WATCH_STATE}' MAD_PID='${MAD_PID}' MARAG_PID='${MARAG_PID}' watcher_body" > /dev/null 2>&1 &
WATCHER_PID=$!
echo "${WATCHER_PID}" > "${MONITOR_DIR}/r41_watcher.pid"
log "Step D: watcher daemon PID=${WATCHER_PID}  writing snapshots to ${WATCH_LOG}"
log "        state JSON: ${WATCH_STATE}"
log "=============================================================="
log "Launcher exiting. To tail: tail -f ${WATCH_LOG}"
log "=============================================================="

# Exit cleanly; smoke + watcher continue in background
exit 0
