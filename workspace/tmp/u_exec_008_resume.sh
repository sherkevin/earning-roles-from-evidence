#!/bin/bash
# ============================================================================
# R42 U-EXEC-008 post-recharge resume orchestrator (engineer MCP-3, 2026-04-21)
# ============================================================================
# Purpose:
#   One-shot idempotent recovery script that restarts the E-017 seed=43/44 +
#   MuSiQue matrix pipeline after newapi quota top-up (U-EXEC-008 v2). Runs
#   after user confirms recharge; replaces the per-incident R40
#   `r40_launch_resume_and_schedule.sh` template which was seed=42 specific.
#
# What it does (in order):
#   Step 0:   pre-flight quota probe; abort if not ACTIVE
#   Step 1:   kill any stale schedule_e017 / r41b_n50 / r41d_musique / run_e017
#             daemon processes (belt-and-suspenders; R41f already killed 3)
#   Step 2:   audit what is DONE vs still-partial vs queued
#   Step 3a:  resume seed=43 stage2 + stage1 (from existing --run-dir)
#   Step 3b:  launch seed=44 (fresh run_dir)
#   Step 4:   launch a new scheduler daemon that waits for seed=43+44 DONE
#             then fires paired_bootstrap_ci.py --seeds 42,43,44
#   Step 5:   launch MuSiQue matrix watcher (reuses r41d_musique_matrix_watcher.sh)
#             which itself waits on seed=43 DONE before firing 5 MuSiQue cells
#   Step 6:   print consolidated PID table + log paths
#
# Idempotency:
#   - Re-running is safe: step 1 kills any copies of this orchestrator's
#     own daemons; step 2 re-detects cell completion; step 3-5 skip cells
#     with metrics.json already on disk.
#   - Nohup PIDs written to logs/r42_resume_pids_<TS>.txt for later cleanup.
#
# Dry-run:
#   bash workspace/tmp/u_exec_008_resume.sh --dry-run
# prints the plan + current state without launching anything.
#
# Cross-references:
#   - [quota_exhaustion_incident_20260419_2338] — v1 incident + R40 template
#   - [r41f_quota_exhaustion_v2_20260421_0850]  — v2 incident + recovery playbook
#   - [u_rollback_001_path_a_landed_20260420]    — R40 resume pattern
#   - scripts/run_e017_fullval_seed.py --run-dir — resume interface (E-017 canon)
#   - workspace/tmp/schedule_e017_seeds.sh       — seed=42-specialized scheduler (historical)
#   - workspace/tmp/r41d_musique_matrix_watcher.sh — MuSiQue 5-cell launcher
# ============================================================================

set -uo pipefail
cd /media/data3/dengkw/idea04
mkdir -p logs artifacts/monitor

DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=1
fi

TS="$(date +%Y%m%d_%H%M%S)"
ORCH_LOG="logs/r42_u_exec_008_resume_${TS}.log"
PID_FILE="logs/r42_resume_pids_${TS}.txt"
OUT_ROOT="artifacts/round2_gpt41mini_stage2_fullval"

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${ORCH_LOG}"
}

sub_log(){
  echo "[$(date '+%F %T')]     $*" | tee -a "${ORCH_LOG}"
}

do_or_dryrun(){
  # $1 = description, $2+ = command
  local desc="$1"; shift
  if [ "${DRY_RUN}" -eq 1 ]; then
    sub_log "[DRY-RUN] would: ${desc}"
    sub_log "[DRY-RUN]   cmd: $*"
  else
    sub_log "${desc}"
    "$@"
  fi
}

log "================================================================"
log "R42 U-EXEC-008 post-recharge resume orchestrator"
if [ "${DRY_RUN}" -eq 1 ]; then
  log "**DRY RUN MODE — no processes launched, no state changed**"
fi
log "================================================================"

# ----------------------------------------------------------------------------
# Step 0: pre-flight quota probe
# ----------------------------------------------------------------------------
log ""
log "Step 0: pre-flight newapi quota probe"
if ! bash workspace/tmp/newapi_quota_probe.sh 2>&1 | tee -a "${ORCH_LOG}" | grep -q "newapi ACTIVE"; then
  log "ABORT: newapi quota not ACTIVE. Top up U-EXEC-008 first."
  log "       probe script: workspace/tmp/newapi_quota_probe.sh"
  exit 1
fi
log "Step 0 ✓ newapi ACTIVE"

# ----------------------------------------------------------------------------
# Step 1: kill any stale daemons
# ----------------------------------------------------------------------------
log ""
log "Step 1: killing stale E-017 / n50 / musique daemons (idempotent)"
for pattern in \
    "schedule_e017_seeds" \
    "r41b_n50_smokes_watcher" \
    "r41d_musique_matrix_watcher" \
    "run_e017_fullval_seed" \
    "u_exec_008_resume" ; do
  # Do NOT kill ourselves: `pkill -f u_exec_008_resume` would kill this script.
  if [ "${pattern}" = "u_exec_008_resume" ]; then
    # Kill copies other than this PID.
    others=$(pgrep -f "${pattern}" 2>/dev/null | grep -v "^$$\$" || true)
    if [ -n "${others}" ]; then
      for p in ${others}; do
        do_or_dryrun "killing stale u_exec_008_resume copy PID=${p}" kill "${p}" 2>/dev/null || true
      done
    else
      sub_log "no other u_exec_008_resume copy"
    fi
    continue
  fi
  if pgrep -f "${pattern}" >/dev/null 2>&1; then
    do_or_dryrun "pkill -f ${pattern}" pkill -f "${pattern}" || true
  else
    sub_log "no stale ${pattern}"
  fi
done
[ "${DRY_RUN}" -eq 1 ] || sleep 3

# Verify clean
sub_log "ps -ef | grep e017|r41b|r41d (should be empty):"
ps -ef 2>/dev/null | grep -E "run_e017|schedule_e017|r41b_n50|r41d_musique" | grep -v grep | grep -v "u_exec_008" | tee -a "${ORCH_LOG}" || echo "  (none)" | tee -a "${ORCH_LOG}"
log "Step 1 ✓ stale daemons cleaned"

# ----------------------------------------------------------------------------
# Step 2: audit pipeline state
# ----------------------------------------------------------------------------
log ""
log "Step 2: auditing pipeline cell state"

audit_cell(){
  local label="$1" dir="$2"
  if [ -z "${dir}" ] || [ ! -d "${dir}" ]; then
    echo "  ${label}  MISSING_DIR  (${dir})" | tee -a "${ORCH_LOG}"
    return 1
  fi
  local metrics="${dir}/metrics.json"
  local ckpt="${dir}/_ckpt_preds.jsonl"
  if [ -f "${metrics}" ]; then
    local f1
    f1=$(python3 -c "import json; print(json.load(open('${metrics}')).get('answer_f1','?'))" 2>/dev/null)
    local n
    n=$(python3 -c "import json; print(json.load(open('${metrics}')).get('sample_count','?'))" 2>/dev/null)
    echo "  ${label}  DONE  (n=${n}, F1=${f1})" | tee -a "${ORCH_LOG}"
    return 0
  fi
  if [ -f "${ckpt}" ]; then
    local lines
    lines=$(wc -l < "${ckpt}" 2>/dev/null || echo 0)
    echo "  ${label}  PARTIAL (ckpt_lines=${lines})" | tee -a "${ORCH_LOG}"
    return 2
  fi
  echo "  ${label}  EMPTY" | tee -a "${ORCH_LOG}"
  return 3
}

SEED42_S2="${OUT_ROOT}/run_20260419_124129_seed42/edo_stage2_chain"
SEED42_S1="${OUT_ROOT}/run_20260419_124130_seed42/fixed_peer_calibrated"
SEED43_DIR=$(ls -d ${OUT_ROOT}/run_*_seed43/ 2>/dev/null | sort -r | head -1 || echo "")
SEED43_DIR="${SEED43_DIR%/}"   # strip trailing slash
SEED43_S2=""
SEED43_S1=""
if [ -n "${SEED43_DIR}" ]; then
  SEED43_S2="${SEED43_DIR}/edo_stage2_chain"
  SEED43_S1="${SEED43_DIR}/fixed_peer_calibrated"
fi

log "seed=42:"
audit_cell "  stage2  " "${SEED42_S2}" || true
audit_cell "  stage1  " "${SEED42_S1}" || true
log "seed=43:"
audit_cell "  stage2  " "${SEED43_S2}" || SEED43_S2_STATUS=$?
audit_cell "  stage1  " "${SEED43_S1}" || SEED43_S1_STATUS=$?

# ----------------------------------------------------------------------------
# Step 3a: resume seed=43 (partial, from existing run_dir)
# ----------------------------------------------------------------------------
log ""
log "Step 3a: resume seed=43 partial checkpoints (if not DONE)"

launch_seed43_resume(){
  local method="$1" run_dir="$2" log_name="$3"
  if [ -f "${run_dir}/metrics.json" ]; then
    sub_log "seed=43 ${method} already DONE; skipping."
    return 0
  fi
  if [ ! -d "${run_dir}" ]; then
    log "ABORT: seed=43 ${method} run_dir=${run_dir} missing. Cannot resume."
    return 1
  fi
  local out_log="logs/e017_seed43_${log_name}_resume_${TS}.log"
  if [ "${DRY_RUN}" -eq 1 ]; then
    sub_log "[DRY-RUN] would launch seed=43 ${method} resume:"
    sub_log "[DRY-RUN]   nohup python3 -u scripts/run_e017_fullval_seed.py --seed 43 --method ${method} --workers 8 --run-dir ${run_dir} > ${out_log} 2>&1 &"
    return 0
  fi
  nohup python3 -u scripts/run_e017_fullval_seed.py \
      --seed 43 --method "${method}" --workers 8 \
      --run-dir "${run_dir}" \
    > "${out_log}" 2>&1 &
  local pid=$!
  disown || true
  sub_log "seed=43 ${method}  PID=${pid}  log=${out_log}"
  echo "seed43_${method} pid=${pid} log=${out_log}" >> "${PID_FILE}"
}

if [ -n "${SEED43_S2}" ]; then
  launch_seed43_resume edo_stage2_chain "${SEED43_S2}" stage2
  sleep 1
  launch_seed43_resume fixed_peer_calibrated "${SEED43_S1}" stage1
else
  log "ABORT: no seed=43 run_dir found. Probably a fresh install. Exiting."
  log "Use scripts/run_e017_fullval_seed.py --seed 43 without --run-dir to create."
  exit 2
fi

# ----------------------------------------------------------------------------
# Step 3b: launch seed=44 (fresh)
# ----------------------------------------------------------------------------
log ""
log "Step 3b: launch seed=44 fresh"

SEED44_RUN_ID="run_${TS}_seed44"
SEED44_S2="${OUT_ROOT}/${SEED44_RUN_ID}/edo_stage2_chain"
SEED44_S1="${OUT_ROOT}/${SEED44_RUN_ID}/fixed_peer_calibrated"

# If a seed=44 dir already has DONE metrics, skip (idempotent).
existing_seed44=$(ls -d ${OUT_ROOT}/run_*_seed44/ 2>/dev/null | sort -r | head -1 || echo "")
existing_seed44="${existing_seed44%/}"
SEED44_EXISTING_S2_DONE=0
SEED44_EXISTING_S1_DONE=0
if [ -n "${existing_seed44}" ]; then
  if [ -f "${existing_seed44}/edo_stage2_chain/metrics.json" ]; then
    SEED44_EXISTING_S2_DONE=1
  fi
  if [ -f "${existing_seed44}/fixed_peer_calibrated/metrics.json" ]; then
    SEED44_EXISTING_S1_DONE=1
  fi
fi

if [ "${SEED44_EXISTING_S2_DONE}" -eq 1 ] && [ "${SEED44_EXISTING_S1_DONE}" -eq 1 ]; then
  sub_log "seed=44 already DONE at ${existing_seed44}; skipping fresh launch."
  SEED44_S2="${existing_seed44}/edo_stage2_chain"
  SEED44_S1="${existing_seed44}/fixed_peer_calibrated"
else
  # If seed=44 partial exists, resume it instead of creating new dir.
  if [ -n "${existing_seed44}" ] && [ -f "${existing_seed44}/edo_stage2_chain/_ckpt_preds.jsonl" ]; then
    sub_log "seed=44 partial found at ${existing_seed44}; resuming instead of fresh."
    SEED44_S2="${existing_seed44}/edo_stage2_chain"
    SEED44_S1="${existing_seed44}/fixed_peer_calibrated"
    mkdir -p "${SEED44_S1}"
    launch_seed44_fn(){
      local method="$1" run_dir="$2" log_name="$3"
      if [ -f "${run_dir}/metrics.json" ]; then
        sub_log "seed=44 ${method} already DONE; skipping."
        return 0
      fi
      local out_log="logs/e017_seed44_${log_name}_resume_${TS}.log"
      if [ "${DRY_RUN}" -eq 1 ]; then
        sub_log "[DRY-RUN] would launch seed=44 ${method} (resume/fresh unified):"
        sub_log "[DRY-RUN]   nohup python3 -u scripts/run_e017_fullval_seed.py --seed 44 --method ${method} --workers 8 --run-dir ${run_dir} > ${out_log} 2>&1 &"
        return 0
      fi
      nohup python3 -u scripts/run_e017_fullval_seed.py \
          --seed 44 --method "${method}" --workers 8 \
          --run-dir "${run_dir}" \
        > "${out_log}" 2>&1 &
      local pid=$!
      disown || true
      sub_log "seed=44 ${method}  PID=${pid}  log=${out_log}"
      echo "seed44_${method} pid=${pid} log=${out_log}" >> "${PID_FILE}"
    }
    launch_seed44_fn edo_stage2_chain "${SEED44_S2}" stage2
    sleep 1
    launch_seed44_fn fixed_peer_calibrated "${SEED44_S1}" stage1
  else
    # Fresh launch: create run_dir explicitly (mirrors schedule_e017_seeds.sh launch_seed).
    sub_log "seed=44 fresh launch — creating ${SEED44_S2} + ${SEED44_S1}"
    if [ "${DRY_RUN}" -eq 0 ]; then
      mkdir -p "${SEED44_S2}" "${SEED44_S1}"
    fi
    launch_seed44_fresh_fn(){
      local method="$1" run_dir="$2" log_name="$3"
      local out_log="logs/e017_seed44_${log_name}_fresh_${TS}.log"
      if [ "${DRY_RUN}" -eq 1 ]; then
        sub_log "[DRY-RUN] would launch seed=44 ${method} fresh:"
        sub_log "[DRY-RUN]   nohup python3 -u scripts/run_e017_fullval_seed.py --seed 44 --method ${method} --workers 8 --run-dir ${run_dir} > ${out_log} 2>&1 &"
        return 0
      fi
      nohup python3 -u scripts/run_e017_fullval_seed.py \
          --seed 44 --method "${method}" --workers 8 \
          --run-dir "${run_dir}" \
        > "${out_log}" 2>&1 &
      local pid=$!
      disown || true
      sub_log "seed=44 ${method}  PID=${pid}  log=${out_log}"
      echo "seed44_${method} pid=${pid} log=${out_log}" >> "${PID_FILE}"
    }
    launch_seed44_fresh_fn edo_stage2_chain "${SEED44_S2}" stage2
    sleep 1
    launch_seed44_fresh_fn fixed_peer_calibrated "${SEED44_S1}" stage1
  fi
fi

# ----------------------------------------------------------------------------
# Step 4: launch paired-bootstrap scheduler daemon (runs after seed=43+44 done)
# ----------------------------------------------------------------------------
log ""
log "Step 4: launch paired-bootstrap scheduler (waits seed=43+44 DONE, fires 3-seed CI)"

PAIRED_LOG="logs/r42_paired_bootstrap_scheduler_${TS}.log"
PAIRED_CSV="${OUT_ROOT}/paired_stats_3seed.csv"

# Inline scheduler as a small heredoc nohup bash -c ... to keep things self-contained.
if [ "${DRY_RUN}" -eq 1 ]; then
  sub_log "[DRY-RUN] would launch paired-bootstrap scheduler:"
  sub_log "[DRY-RUN]   waits for: ${SEED43_S2}/metrics.json + ${SEED43_S1}/metrics.json + ${SEED44_S2}/metrics.json + ${SEED44_S1}/metrics.json"
  sub_log "[DRY-RUN]   then runs: python3 scripts/paired_bootstrap_ci.py --seeds 42,43,44 --B 10000 --out ${PAIRED_CSV}"
else
  nohup bash -c "
    set -uo pipefail
    cd /media/data3/dengkw/idea04
    echo '[paired-sched] waiting for seed=43+44 metrics.json'
    while true; do
      ok=1
      for d in '${SEED43_S2}' '${SEED43_S1}' '${SEED44_S2}' '${SEED44_S1}'; do
        if [ ! -f \"\${d}/metrics.json\" ]; then
          ok=0
          break
        fi
      done
      if [ \"\${ok}\" -eq 1 ]; then break; fi
      sleep 120
    done
    echo '[paired-sched] all 4 metrics.json present; validating'
    for d in '${SEED43_S2}' '${SEED43_S1}' '${SEED44_S2}' '${SEED44_S1}'; do
      python3 scripts/validate_logs.py \"\${d}\" | tail -5
    done
    echo '[paired-sched] running paired_bootstrap_ci'
    python3 scripts/paired_bootstrap_ci.py \
        --root '${OUT_ROOT}' \
        --method-a fixed_peer_calibrated \
        --method-b edo_stage2_chain \
        --seeds 42,43,44 \
        --B 10000 \
        --out '${PAIRED_CSV}'
    echo '[paired-sched] DONE. paired_stats_3seed.csv at ${PAIRED_CSV}'
  " > "${PAIRED_LOG}" 2>&1 &
  PAIRED_PID=$!
  disown || true
  sub_log "paired scheduler PID=${PAIRED_PID}  log=${PAIRED_LOG}"
  echo "paired_scheduler pid=${PAIRED_PID} log=${PAIRED_LOG}" >> "${PID_FILE}"
fi

# ----------------------------------------------------------------------------
# Step 5: launch MuSiQue matrix watcher (reuse R41d)
# ----------------------------------------------------------------------------
log ""
log "Step 5: launch MuSiQue matrix watcher (r41d_musique_matrix_watcher.sh)"

# r41d waits for seed=43 DONE + HotpotQA n=50 DONE. HotpotQA n=50 is already
# DONE per R41e state snapshot — watcher will detect & advance.
if [ ! -f "workspace/tmp/r41d_musique_matrix_watcher.sh" ]; then
  log "WARN: r41d_musique_matrix_watcher.sh missing; skipping MuSiQue matrix."
else
  MUSIQUE_LOG="artifacts/monitor/r42_musique_matrix_watch_${TS}.log"
  if [ "${DRY_RUN}" -eq 1 ]; then
    sub_log "[DRY-RUN] would launch: nohup bash workspace/tmp/r41d_musique_matrix_watcher.sh > ${MUSIQUE_LOG} 2>&1 &"
  else
    nohup bash workspace/tmp/r41d_musique_matrix_watcher.sh > "${MUSIQUE_LOG}" 2>&1 &
    MUSIQUE_PID=$!
    disown || true
    sub_log "MuSiQue watcher PID=${MUSIQUE_PID}  log=${MUSIQUE_LOG}"
    echo "musique_watcher pid=${MUSIQUE_PID} log=${MUSIQUE_LOG}" >> "${PID_FILE}"
  fi
fi

# ----------------------------------------------------------------------------
# Step 6: consolidated PID table
# ----------------------------------------------------------------------------
log ""
log "Step 6: consolidated PID table (saved to ${PID_FILE})"
if [ -f "${PID_FILE}" ]; then
  cat "${PID_FILE}" | tee -a "${ORCH_LOG}"
fi

log ""
log "================================================================"
log "R42 U-EXEC-008 resume orchestrator DONE"
log "  orchestrator log: ${ORCH_LOG}"
log "  PIDs file:        ${PID_FILE}"
log "  tail logs:"
log "    tail -f logs/e017_seed43_stage2_resume_${TS}.log"
log "    tail -f logs/e017_seed43_stage1_resume_${TS}.log"
log "    tail -f logs/e017_seed44_stage2_fresh_${TS}.log   (or _resume_ if partial)"
log "    tail -f logs/e017_seed44_stage1_fresh_${TS}.log"
log "    tail -f ${PAIRED_LOG}"
log "    tail -f artifacts/monitor/r42_musique_matrix_watch_${TS}.log"
log "================================================================"
