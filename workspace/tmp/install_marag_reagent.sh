#!/bin/bash
# Install MA-RAG + ReAgent venvs in background. No LLM calls; safe alongside E-017.
set -u
cd /media/data3/dengkw/idea04
mkdir -p logs
TS=$(date +%Y%m%d_%H%M%S)
VIRTUALENV=/home/dengkw/.local/bin/virtualenv

echo "=== Launching MA-RAG + ReAgent venv installs at ${TS} ==="

LOG_MARAG="logs/e018_marag_install_${TS}.log"
LOG_REAGENT="logs/e018_reagent_install_${TS}.log"

# MA-RAG: slim stack (skip heavy vLLM/pytorch/sentence_transformers; we don't need retriever for HotpotQA gold-context adapter)
{
  cd /media/data3/dengkw/idea04/external_baselines/marag || exit 1
  if [ -d venv_marag ]; then
    echo '[skip] venv_marag already exists'
  else
    ${VIRTUALENV} venv_marag --python=python3.10 2>&1 | tail -5
  fi
  # shellcheck disable=SC1091
  source venv_marag/bin/activate
  python -m pip install --upgrade pip 2>&1 | tail -3
  echo '=== installing MA-RAG slim deps (langchain + openai + tqdm) ==='
  python -m pip install \
    'langchain==0.3.27' \
    'langchain_community==0.3.27' \
    'langchain_core==0.3.74' \
    'langchain_openai==0.3.30' \
    'langgraph==0.6.5' \
    'openai==1.100.2' \
    'python-dotenv' \
    'pydantic==2.11.7' \
    'requests' \
    'tqdm==4.67.1' \
    'numpy' \
    'pandas' \
    'typing_extensions' \
    2>&1 | tail -25
  echo '=== verify install ==='
  python -c 'from langchain_openai import ChatOpenAI; print("langchain_openai ChatOpenAI import OK")'
  python -c 'import langgraph; print("langgraph", langgraph.__version__)'
  python -c 'import openai; print("openai", openai.__version__)'
  echo __MARAG_VENV_OK__
} > "${LOG_MARAG}" 2>&1 &
MARAG_PID=$!
echo "MA-RAG install PID=${MARAG_PID} LOG=${LOG_MARAG}"

# ReAgent: minimal deps
{
  cd /media/data3/dengkw/idea04/external_baselines/reagent || exit 1
  if [ -d venv_reagent ]; then
    echo '[skip] venv_reagent already exists'
  else
    ${VIRTUALENV} venv_reagent --python=python3.10 2>&1 | tail -5
  fi
  # shellcheck disable=SC1091
  source venv_reagent/bin/activate
  python -m pip install --upgrade pip 2>&1 | tail -3
  echo '=== installing ReAgent deps (infer from main.py imports) ==='
  python -m pip install 'openai' 'pandas' 'pyyaml' 'tqdm' 'numpy' 'requests' 2>&1 | tail -15
  echo '=== verify install ==='
  python -c 'from openai import OpenAI; print("openai new API OK")'
  python -c 'import pandas; print("pandas", pandas.__version__)'
  echo __REAGENT_VENV_OK__
} > "${LOG_REAGENT}" 2>&1 &
REAGENT_PID=$!
echo "ReAgent install PID=${REAGENT_PID} LOG=${LOG_REAGENT}"

echo
echo "=== launched at ${TS} ==="
sleep 3
ps -ef | grep -E 'virtualenv|pip install' | grep -v grep
