#!/bin/bash
cd /media/data3/dengkw/idea04/external_baselines/reagent
echo "=== main.py full ==="
cat main.py
echo
echo "=== Agent/agent.py ==="
head -100 Agent/agent.py
echo
echo "=== Agent/moderator2.py (first 80 lines) ==="
head -80 Agent/moderator2.py
echo
echo "=== backend/api.py full ==="
cat backend/api.py
echo
echo "=== DataProcess/Hotpotqa.py ==="
cat DataProcess/Hotpotqa.py
echo
echo "=== DataProcess/Dataset.py ==="
head -100 DataProcess/Dataset.py
echo
echo "=== services.yaml sample (if exists) ==="
find . -maxdepth 3 -name '*.yaml' -o -name 'services.yaml' 2>/dev/null
