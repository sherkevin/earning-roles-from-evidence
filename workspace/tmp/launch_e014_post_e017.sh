#!/bin/bash
# E-014 launcher (gpt-4.1-mini Table 2 ablation) — RUN AFTER E-017 fully done.
# Per ENGINEER_TODO [E-017_migration_landed_ack_20260420] sub-block "Hold/Defer items":
# this script holds until paired_stats_3seed.csv lands, then launches 4 ablation batches
# in 2 parallel pairs (workers=8 each, total 16 concurrent — within newapi safe ceiling).
#
# Engineer copy-paste:
#   ssh -i ~/.ssh/school -o BatchMode=yes -o ControlMaster=no -o ControlPath=none -o IdentityAgent=none \
#     dengkw@10.103.16.12 'bash /media/data3/dengkw/idea04/scripts/launch_e014_post_e017.sh'

set -u
cd /media/data3/dengkw/idea04
mkdir -p logs artifacts/round2_gpt41mini_ablations
unset LLM_BACKEND LLM_BASE_URL LLM_API_KEY LLM_MODEL
export PYTHONPATH=/media/data3/dengkw/idea04/workspace:/media/data3/dengkw/idea04/scripts

OUT_ROOT="artifacts/round2_gpt41mini_ablations"
SAMPLES_JSONL="artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/raw_inputs.jsonl"
SCHED_LOG="logs/e014_scheduler_$(date +%Y%m%d_%H%M%S).log"

log(){
  echo "[$(date '+%F %T')] $*" | tee -a "${SCHED_LOG}"
}

log "=== E-014 launcher start ==="
log "Pre-flight: verify E-017 done (paired_stats_3seed.csv present)"
PAIRED_STATS="artifacts/round2_gpt41mini_stage2_fullval/paired_stats_3seed.csv"
if [ ! -f "${PAIRED_STATS}" ]; then
  log "WARN: ${PAIRED_STATS} not found — E-017 may not be complete yet"
  log "  (E-014 will still run; it doesn't need E-017 data, just needs the newapi slots free)"
  log "  (Check 'ps -ef | grep run_e017' to confirm no E-017 procs alive)"
fi

ALIVE_E017=$(ps -ef | grep -E 'python.*run_e017' | grep -v grep | wc -l)
log "Alive E-017 processes: ${ALIVE_E017}"
if [ "${ALIVE_E017}" -gt 0 ]; then
  log "ABORT: E-017 still running — refuse to launch E-014 (risk of newapi rate-limit collapse)"
  log "  re-run this script after E-017 fully done"
  exit 2
fi

log "=== Launching 4 ablation batches in 2 parallel pairs ==="

run_ablation_pair(){
  local CFG_A="$1"  local TAG_A="$2"
  local CFG_B="$3"  local TAG_B="$4"
  local TS=$(date +%Y%m%d_%H%M%S)

  local DIR_A="${OUT_ROOT}/${TS}_${TAG_A}"
  local DIR_B="${OUT_ROOT}/${TS}_${TAG_B}"
  mkdir -p "${DIR_A}" "${DIR_B}"

  log "  pair A: ${TAG_A} → ${DIR_A}"
  nohup python3 -u scripts/run_round1_v3.py \
      --config "configs/${CFG_A}" \
      --samples-jsonl "${SAMPLES_JSONL}" \
      --methods fixed_peer_calibrated \
      --artifacts-root "${OUT_ROOT}" \
      --resume-run-dir "${DIR_A}" \
      > "logs/e014_${TAG_A}_${TS}.log" 2>&1 &
  local PID_A=$!
  sleep 1

  log "  pair B: ${TAG_B} → ${DIR_B}"
  nohup python3 -u scripts/run_round1_v3.py \
      --config "configs/${CFG_B}" \
      --samples-jsonl "${SAMPLES_JSONL}" \
      --methods fixed_peer_calibrated \
      --artifacts-root "${OUT_ROOT}" \
      --resume-run-dir "${DIR_B}" \
      > "logs/e014_${TAG_B}_${TS}.log" 2>&1 &
  local PID_B=$!

  log "  PIDs: A=${PID_A} B=${PID_B}"
  
  # Wait for both batches to finish (poll metrics.json)
  while true; do
    if [ -f "${DIR_A}/fixed_peer_calibrated/metrics.json" ] && [ -f "${DIR_B}/fixed_peer_calibrated/metrics.json" ]; then
      log "  pair done"
      break
    fi
    if [ -f "${DIR_A}/fixed_peer_calibrated/_ckpt_preds.jsonl" ]; then
      A_DONE=$(wc -l < "${DIR_A}/fixed_peer_calibrated/_ckpt_preds.jsonl")
    else
      A_DONE=0
    fi
    if [ -f "${DIR_B}/fixed_peer_calibrated/_ckpt_preds.jsonl" ]; then
      B_DONE=$(wc -l < "${DIR_B}/fixed_peer_calibrated/_ckpt_preds.jsonl")
    else
      B_DONE=0
    fi
    log "    progress: ${TAG_A}=${A_DONE}/200 | ${TAG_B}=${B_DONE}/200"
    sleep 30
  done
}

# Pair 1: baseline + evidence (both ~30 min wall on workers=8)
run_ablation_pair \
  round2_gpt41mini_ablation_baseline.yaml ablation_baseline \
  round2_gpt41mini_ablation_evidence.yaml ablation_evidence

# Pair 2: no_tcpb + no_gate
run_ablation_pair \
  round2_gpt41mini_ablation_no_tcpb.yaml ablation_no_tcpb \
  round2_gpt41mini_ablation_no_gate.yaml ablation_no_gate

log "=== All 4 ablations done ==="
log "Aggregating into Table 2 CSV..."
python3 - << 'PYEOF' 2>&1 | tee -a "${SCHED_LOG}"
import csv
import json
from pathlib import Path

OUT_ROOT = Path("/media/data3/dengkw/idea04/artifacts/round2_gpt41mini_ablations")
TABLE_FIELDS = ["ablation", "answer_em", "answer_f1", "mean_handoff_count",
                "dead_end_rate", "premature_accept_rate",
                "api_total_tokens_per_sample", "cost_normalized_f1_api",
                "sample_count"]

rows = []
for ablation_dir in sorted(OUT_ROOT.glob("*_ablation_*")):
    metrics_path = ablation_dir / "fixed_peer_calibrated" / "metrics.json"
    if not metrics_path.is_file():
        print(f"[skip] no metrics.json in {ablation_dir}")
        continue
    m = json.loads(metrics_path.read_text(encoding="utf-8"))
    tag = ablation_dir.name.split("_", 1)[1]  # strip TS prefix
    row = {"ablation": tag, **{k: m.get(k, "") for k in TABLE_FIELDS[1:]}}
    rows.append(row)

if rows:
    out_csv = OUT_ROOT / "table2_ablation_main.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=TABLE_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {out_csv}")
    print(f"Rows: {len(rows)}")
    for r in rows:
        print(f"  {r['ablation']:30s}  EM={r['answer_em']}  F1={r['answer_f1']}  tokens={r['api_total_tokens_per_sample']}")
else:
    print("[ERROR] no ablation metrics.json found")
PYEOF

log "=== E-014 launcher complete; deliverable: ${OUT_ROOT}/table2_ablation_main.csv ==="
