#!/bin/bash
# Parallel-launch clone + install work that doesn't compete with E-017's newapi slots.
# This script kicks off 4 background tasks; each writes its own log.
set -u
cd /media/data3/dengkw/idea04
mkdir -p logs external_baselines
TS=$(date +%Y%m%d_%H%M%S)

echo "=== Launching parallel clone + install at ${TS} ==="

# Task 1: Clone MA-RAG (~30 sec, just git)
LOG1="logs/e018_marag_clone_${TS}.log"
nohup bash -c "
cd /media/data3/dengkw/idea04/external_baselines &&
if [ -d marag ]; then
  echo '[skip] marag dir already present'
else
  git clone --depth 1 https://github.com/thangylvp/MA-RAG marag 2>&1
fi &&
ls -la marag/ &&
echo '=== MA-RAG README excerpt ===' &&
head -50 marag/README.md 2>/dev/null &&
echo '=== MA-RAG entry points ===' &&
ls marag/*.py marag/scripts/ 2>/dev/null
" > "${LOG1}" 2>&1 &
echo "T1 (MA-RAG clone) PID=$! LOG=${LOG1}"

# Task 2: Clone ReAgent (~30 sec, just git)
LOG2="logs/e018_reagent_clone_${TS}.log"
nohup bash -c "
cd /media/data3/dengkw/idea04/external_baselines &&
if [ -d reagent ]; then
  echo '[skip] reagent dir already present'
else
  git clone --depth 1 https://github.com/astridesa/ReAgent reagent 2>&1
fi &&
ls -la reagent/ &&
echo '=== ReAgent README excerpt ===' &&
head -50 reagent/README.md 2>/dev/null &&
echo '=== ReAgent entry points ===' &&
ls reagent/*.py reagent/scripts/ 2>/dev/null
" > "${LOG2}" 2>&1 &
echo "T2 (ReAgent clone) PID=$! LOG=${LOG2}"

# Task 3: MAD venv install (light: 4 packages, no LLM call yet)
LOG3="logs/e015_mad_install_${TS}.log"
nohup bash -c "
cd /media/data3/dengkw/idea04/external_baselines/mad &&
if [ -d venv_mad ]; then
  echo '[skip] venv_mad already present, just upgrading pip'
  source venv_mad/bin/activate
  pip install --upgrade pip 2>&1 | tail -3
else
  python3 -m venv venv_mad &&
  source venv_mad/bin/activate &&
  pip install --upgrade pip 2>&1 | tail -3 &&
  pip install -r requirements.txt 2>&1 | tail -10
fi &&
echo '=== installed packages ===' &&
pip list | grep -iE 'openai|numpy|pandas|tqdm' &&
echo '=== MAD math entrypoint ===' &&
ls math/
" > "${LOG3}" 2>&1 &
echo "T3 (MAD install) PID=$! LOG=${LOG3}"

# Task 4: ChatEval venv install (heavy: langchain + BMTools, ~5-10 min)
LOG4="logs/e010_chateval_install_${TS}.log"
nohup bash -c "
cd /media/data3/dengkw/idea04/external_baselines/chateval &&
if [ -d venv_chateval ]; then
  echo '[skip] venv_chateval already present, just upgrading pip'
  source venv_chateval/bin/activate
  pip install --upgrade pip 2>&1 | tail -3
else
  python3 -m venv venv_chateval &&
  source venv_chateval/bin/activate &&
  pip install --upgrade pip 2>&1 | tail -3 &&
  pip install -r requirements.txt 2>&1 | tail -30
fi &&
echo '=== installed packages ===' &&
pip list | grep -iE 'openai|langchain|fastapi|gradio|bmtools' &&
echo '=== ChatEval entrypoint inspection ===' &&
head -30 llm_eval.py 2>/dev/null
" > "${LOG4}" 2>&1 &
echo "T4 (ChatEval install) PID=$! LOG=${LOG4}"

echo
echo "=== launched 4 background tasks at ${TS} ==="
echo "Each writes to its own log; tail any to monitor."
echo
sleep 3
echo "=== process snapshot ==="
ps -ef | grep -E 'git clone|pip install|venv' | grep -v grep
