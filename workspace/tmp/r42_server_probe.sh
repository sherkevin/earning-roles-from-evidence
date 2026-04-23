#!/bin/bash
# R42 engineer server state probe — runs after engineer takeover
set -u
cd /media/data3/dengkw/idea04

echo "================================================================"
echo "R42 SERVER PROBE  $(date)"
echo "================================================================"

echo ""
echo "=== GPU ==="
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits

echo ""
echo "=== RUNNING engineer procs ==="
ps -ef 2>/dev/null | grep -E '(run_e017|schedule|r41b|r41d|watcher|vllm|python3.*hotpotqa|python3.*reagent|python3.*mad|python3.*marag)' | grep -v grep | head -30 || echo "(none)"

echo ""
echo "=== DISK /media/data3 ==="
df -h /media/data3 | tail -2

echo ""
echo "=== SEED42 FULL ==="
for m in edo_stage2_chain fixed_peer_calibrated; do
  for d in artifacts/round2_gpt41mini_stage2_fullval/run_*_seed42/; do
    if [ -d "${d}${m}" ]; then
      if [ -f "${d}${m}/metrics.json" ]; then
        f1=$(python3 -c "import json; print(json.load(open('${d}${m}/metrics.json'))['answer_f1'])" 2>/dev/null)
        n=$(python3 -c "import json; print(json.load(open('${d}${m}/metrics.json'))['sample_count'])" 2>/dev/null)
        echo "  seed42 ${m}: DONE (n=${n}, F1=${f1}) @ ${d}${m}"
      fi
    fi
  done
done

echo ""
echo "=== SEED43 STATE ==="
for m in edo_stage2_chain fixed_peer_calibrated; do
  d=$(ls -d artifacts/round2_gpt41mini_stage2_fullval/run_*_seed43/ 2>/dev/null | sort -r | head -1)
  if [ -n "${d}" ]; then
    if [ -f "${d}${m}/metrics.json" ]; then
      echo "  seed43 ${m}: DONE"
    elif [ -f "${d}${m}/_ckpt_preds.jsonl" ]; then
      n=$(wc -l < "${d}${m}/_ckpt_preds.jsonl")
      echo "  seed43 ${m}: PARTIAL ckpt=${n}/7405 dir=${d}${m}"
    else
      echo "  seed43 ${m}: EMPTY"
    fi
  else
    echo "  seed43 ${m}: NO_DIR"
  fi
done

echo ""
echo "=== SEED44 STATE ==="
ls -d artifacts/round2_gpt41mini_stage2_fullval/run_*_seed44/ 2>/dev/null || echo "  (none — not yet launched)"

echo ""
echo "=== MuSiQue seed ==="
ls -la artifacts/seed/musique_validation_200.jsonl 2>/dev/null || echo "  (missing)"

echo ""
echo "=== MuSiQue matrix ==="
ls -d artifacts/matrix/musique_n50_*/ 2>/dev/null | head -5 || echo "  (no matrix dirs yet)"

echo ""
echo "=== HotpotQA n=50 external ==="
for sys in mad marag reagent; do
  d=$(ls -d artifacts/external_baselines/${sys}/r41b_n50_*/ 2>/dev/null | sort -r | head -1)
  if [ -n "${d}" ] && [ -f "${d}metrics.json" ]; then
    f1=$(python3 -c "import json,sys; d=json.load(open('${d}metrics.json')); print(d.get('answer_f1', d.get('f1','?')))" 2>/dev/null)
    echo "  ${sys} n=50: DONE F1=${f1}  @ ${d}"
  else
    echo "  ${sys} n=50: ${d} (no metrics.json)"
  fi
done

echo ""
echo "=== vLLM / local models status (E-5 R41h preparation) ==="
which vllm 2>/dev/null || echo "  (no system vllm)"
ls -d /media/data3/dengkw/venvs/ 2>/dev/null || echo "  (no venvs/ directory)"
ls -d /media/data3/dengkw/models/ 2>/dev/null || echo "  (no models/ directory)"

echo ""
echo "=== python3 + virtualenv ==="
python3 --version
~/.local/bin/virtualenv --version 2>/dev/null || echo "  (no virtualenv in ~/.local/bin)"

echo ""
echo "=== Probe complete ==="
