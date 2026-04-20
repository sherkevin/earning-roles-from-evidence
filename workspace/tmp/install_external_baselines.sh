#!/bin/bash
# Install external_baselines via virtualenv (workaround for missing python3.10-venv apt pkg)
set -u
cd /media/data3/dengkw/idea04
mkdir -p logs
TS=$(date +%Y%m%d_%H%M%S)

VIRTUALENV=/home/dengkw/.local/bin/virtualenv

echo "=== Cleaning failed venv attempts ==="
rm -rf external_baselines/mad/venv_mad external_baselines/chateval/venv_chateval 2>/dev/null

# Task 3 (MAD install via virtualenv)
LOG3="logs/e015_mad_install_v2_${TS}.log"
nohup bash -c "
cd /media/data3/dengkw/idea04/external_baselines/mad &&
${VIRTUALENV} venv_mad --python=python3.10 2>&1 | tail -10 &&
source venv_mad/bin/activate &&
python -m pip install --upgrade pip 2>&1 | tail -3 &&
echo '=== installing MAD reqs ===' &&
python -m pip install -r requirements.txt 2>&1 | tail -15 &&
echo '=== verifying installs ===' &&
python -m pip list | grep -iE 'openai|numpy|pandas|tqdm' &&
echo '=== sanity import ===' &&
python -c 'import openai; print(\"openai\", openai.__version__)' &&
python -c 'import numpy; print(\"numpy\", numpy.__version__)' &&
python -c 'import pandas; print(\"pandas\", pandas.__version__)' &&
echo __MAD_VENV_OK__
" > "${LOG3}" 2>&1 &
echo "T3 (MAD venv via virtualenv) PID=$! LOG=${LOG3}"

# Task 4 (ChatEval install via virtualenv)
LOG4="logs/e010_chateval_install_v2_${TS}.log"
nohup bash -c "
cd /media/data3/dengkw/idea04/external_baselines/chateval &&
${VIRTUALENV} venv_chateval --python=python3.10 2>&1 | tail -10 &&
source venv_chateval/bin/activate &&
python -m pip install --upgrade pip 2>&1 | tail -3 &&
echo '=== installing ChatEval reqs ===' &&
python -m pip install -r requirements.txt 2>&1 | tail -30 &&
echo '=== verifying installs ===' &&
python -m pip list | grep -iE 'openai|langchain|fastapi|gradio|bmtools' &&
echo __CHATEVAL_VENV_OK__
" > "${LOG4}" 2>&1 &
echo "T4 (ChatEval venv via virtualenv) PID=$! LOG=${LOG4}"

echo
echo "=== launched 2 background install tasks at ${TS} ==="
sleep 3
ps -ef | grep -E 'virtualenv|pip install' | grep -v grep
