#!/bin/bash
cd /media/data3/dengkw/idea04
echo "=== logs directory (recent) ==="
ls -lat logs/ | head -12
echo
echo "=== MA-RAG install log full ==="
for L in logs/e018_marag_install_*.log; do
  echo "--- $L ---"
  if [ -f "$L" ]; then
    wc -l "$L"
    echo "... tail 30 ..."
    tail -30 "$L"
  fi
done
echo
echo "=== ReAgent install log full ==="
for L in logs/e018_reagent_install_*.log; do
  echo "--- $L ---"
  if [ -f "$L" ]; then
    wc -l "$L"
    echo "... tail 30 ..."
    tail -30 "$L"
  fi
done
echo
echo "=== venvs exist ==="
ls -ld external_baselines/{marag,reagent}/venv_{marag,reagent} 2>/dev/null
echo
echo "=== procs ==="
ps -ef | grep -E 'pip install|virtualenv|run_e017|schedule_e017' | grep -v grep | grep -v _recbole
