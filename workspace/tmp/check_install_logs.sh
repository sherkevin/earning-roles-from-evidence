#!/bin/bash
cd /media/data3/dengkw/idea04
echo "=== MAD install log ==="
for L in logs/e015_mad_install_v2_*.log; do
  if [ -f "$L" ]; then
    echo "--- $L ---"
    tail -25 "$L"
  fi
done
echo
echo "=== ChatEval install log ==="
for L in logs/e010_chateval_install_v2_*.log; do
  if [ -f "$L" ]; then
    echo "--- $L ---"
    tail -25 "$L"
  fi
done
echo
echo "=== Verify venvs ==="
for V in external_baselines/mad/venv_mad external_baselines/chateval/venv_chateval; do
  if [ -d "$V" ]; then
    echo "$V exists"
    ls "$V/bin/python"* 2>/dev/null | head -3
  else
    echo "$V MISSING"
  fi
done
