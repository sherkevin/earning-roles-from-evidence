#!/bin/bash
cd /media/data3/dengkw/idea04
echo "=========================================="
echo "MA-RAG full structure (top 4 levels)"
echo "=========================================="
find external_baselines/marag/ -maxdepth 3 -not -path '*/\.*' | head -40
echo
echo "=========================================="
echo "MA-RAG main.py (first 80 lines)"
echo "=========================================="
head -80 external_baselines/marag/main.py 2>/dev/null
echo
echo "=========================================="
echo "MA-RAG config / requirements"
echo "=========================================="
cat external_baselines/marag/requirements.txt 2>/dev/null
echo
ls external_baselines/marag/configs 2>/dev/null
echo
echo "=========================================="
echo "MA-RAG llm_client / openai usage"
echo "=========================================="
grep -rn "openai\|api_key\|api_base\|chat_url" external_baselines/marag --include="*.py" 2>/dev/null | head -15
echo
echo "=========================================="
echo "ReAgent full structure (top 4 levels)"
echo "=========================================="
find external_baselines/reagent/ -maxdepth 3 -not -path '*/\.*' | head -40
echo
echo "=========================================="
echo "ReAgent main.py (first 80 lines)"
echo "=========================================="
head -80 external_baselines/reagent/main.py 2>/dev/null
echo
echo "=========================================="
echo "ReAgent requirements"
echo "=========================================="
cat external_baselines/reagent/requirements.txt 2>/dev/null
echo
echo "=========================================="
echo "ReAgent llm_client / openai usage"
echo "=========================================="
grep -rn "openai\|api_key\|api_base\|chat_url" external_baselines/reagent --include="*.py" 2>/dev/null | head -15
