#!/bin/bash
# Rescue valid prefix of E-017 seed=42 stage2 + stage1 checkpoints.
# Corrupted portion is F1=0 garbage due to newapi quota exhaustion at ~21:38-21:54 server time.
# Save the full pre-rescue ckpts as forensic backups, then truncate in-place to resumable state.
set -u
cd /media/data3/dengkw/idea04

OUT_ROOT="artifacts/round2_gpt41mini_stage2_fullval"
STAGE2_DIR="${OUT_ROOT}/run_20260419_124129_seed42/edo_stage2_chain"
STAGE1_DIR="${OUT_ROOT}/run_20260419_124130_seed42/fixed_peer_calibrated"

# Forensic backup dir
FORENSIC_DIR="artifacts/forensic/quota_exhaustion_20260419_2338_incident"
mkdir -p "${FORENSIC_DIR}/stage2" "${FORENSIC_DIR}/stage1"

echo "=== Step 1: back up CURRENT full-ckpt state (corrupted) as forensic evidence ==="
cp "${STAGE2_DIR}/_ckpt_preds.jsonl" "${FORENSIC_DIR}/stage2/_ckpt_preds_PRE_RESCUE.jsonl"
cp "${STAGE1_DIR}/_ckpt_preds.jsonl" "${FORENSIC_DIR}/stage1/_ckpt_preds_PRE_RESCUE.jsonl"
cp "${STAGE2_DIR}/metrics.json" "${FORENSIC_DIR}/stage2/metrics_PRE_RESCUE.json" 2>/dev/null
echo "stage2 pre-rescue ckpt: $(wc -l < ${FORENSIC_DIR}/stage2/_ckpt_preds_PRE_RESCUE.jsonl) lines"
echo "stage1 pre-rescue ckpt: $(wc -l < ${FORENSIC_DIR}/stage1/_ckpt_preds_PRE_RESCUE.jsonl) lines"

echo
echo "=== Step 2: find last valid sample in each batch (last sample before F1 collapse) ==="
python3 << 'PYEOF'
import json
from pathlib import Path

OUT_ROOT = Path("artifacts/round2_gpt41mini_stage2_fullval")
STAGE2 = OUT_ROOT / "run_20260419_124129_seed42/edo_stage2_chain"
STAGE1 = OUT_ROOT / "run_20260419_124130_seed42/fixed_peer_calibrated"

def find_last_valid(path: Path, window: int = 50, threshold: float = 0.30) -> int:
    """Return the last sample index whose 50-sample forward-window mean F1 > threshold."""
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    n = len(rows)
    last_valid = -1
    for i in range(n - window):
        f1s = [r.get("answer_f1", 0.0) for r in rows[i:i+window]]
        if sum(f1s) / window >= threshold:
            last_valid = i + window - 1
    return last_valid, n

for name, d in [("stage2", STAGE2), ("stage1", STAGE1)]:
    idx, total = find_last_valid(d / "_ckpt_preds.jsonl")
    print(f"{name}: last valid sample index = {idx} (total ckpt lines = {total}); corrupted from {idx+1} onwards")
PYEOF

echo
echo "=== Step 3: truncate ckpt files to last-valid + truncate sibling jsonl files to same task_id set ==="
python3 << 'PYEOF'
import json
from pathlib import Path

OUT_ROOT = Path("artifacts/round2_gpt41mini_stage2_fullval")
STAGE2 = OUT_ROOT / "run_20260419_124129_seed42/edo_stage2_chain"
STAGE1 = OUT_ROOT / "run_20260419_124130_seed42/fixed_peer_calibrated"

def find_last_valid(path: Path, window: int = 50, threshold: float = 0.30) -> int:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    n = len(rows)
    last_valid = -1
    for i in range(n - window):
        f1s = [r.get("answer_f1", 0.0) for r in rows[i:i+window]]
        if sum(f1s) / window >= threshold:
            last_valid = i + window - 1
    return last_valid, rows

for name, d in [("stage2", STAGE2), ("stage1", STAGE1)]:
    idx, all_rows = find_last_valid(d / "_ckpt_preds.jsonl")
    keep_ids = {r["task_id"] for r in all_rows[:idx+1]}
    print(f"\n=== {name}: keeping samples 0..{idx} = {len(keep_ids)} samples ===")

    # Rewrite _ckpt_preds.jsonl
    ckpt_path = d / "_ckpt_preds.jsonl"
    tmp = ckpt_path.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as fh_out:
        for r in all_rows[:idx+1]:
            fh_out.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(ckpt_path)
    print(f"  rewrote {ckpt_path} to {idx+1} lines")

    # Truncate sibling jsonls that key by task_id
    for side in ["routing_traces.jsonl", "handoff_packets.jsonl",
                 "competence_snapshots.jsonl", "raw_model_outputs.jsonl",
                 "task_tree.jsonl", "audit_events.jsonl",
                 "neighbor_belief_snapshots.jsonl"]:
        sp = d / side
        if not sp.is_file():
            continue
        tmp = sp.with_suffix(".jsonl.tmp")
        kept = 0
        total = 0
        with sp.open(encoding="utf-8") as fh_in, \
             tmp.open("w", encoding="utf-8") as fh_out:
            for line in fh_in:
                line = line.strip()
                if not line:
                    continue
                total += 1
                try:
                    rec = json.loads(line)
                    tid = rec.get("task_id")
                    if tid is None or tid in keep_ids:
                        fh_out.write(line + "\n")
                        kept += 1
                except json.JSONDecodeError:
                    # keep malformed lines to be safe
                    fh_out.write(line + "\n")
                    kept += 1
        tmp.replace(sp)
        print(f"  rewrote {side}: {kept}/{total} lines kept")

    # Delete metrics.json so next resume recomputes (and so is_resume detects incomplete)
    metrics_path = d / "metrics.json"
    if metrics_path.is_file():
        metrics_path.unlink()
        print(f"  deleted {metrics_path} (so runner re-detects as resume, NOT done)")
PYEOF

echo
echo "=== Step 4: verify final ckpt state ==="
for d in "${STAGE2_DIR}" "${STAGE1_DIR}"; do
  echo "--- $d ---"
  echo "  _ckpt_preds.jsonl lines: $(wc -l < ${d}/_ckpt_preds.jsonl)"
  echo "  metrics.json present?: $(test -f ${d}/metrics.json && echo yes || echo no)"
done

echo
echo "=== Step 5: post-rescue F1 sanity ==="
python3 << 'PYEOF'
import json
from pathlib import Path

OUT_ROOT = Path("artifacts/round2_gpt41mini_stage2_fullval")
for name, d in [("stage2", "run_20260419_124129_seed42/edo_stage2_chain"),
                ("stage1", "run_20260419_124130_seed42/fixed_peer_calibrated")]:
    path = OUT_ROOT / d / "_ckpt_preds.jsonl"
    f1s = []
    ems = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                r = json.loads(line)
                f1s.append(r.get("answer_f1", 0.0))
                ems.append(r.get("answer_em", 0.0))
    if f1s:
        print(f"{name}: n={len(f1s)}  mean_F1={sum(f1s)/len(f1s):.4f}  mean_EM={sum(ems)/len(ems):.4f}")
PYEOF
echo
echo "=== Step 6: list forensic backup ==="
ls -la "${FORENSIC_DIR}"/*/
