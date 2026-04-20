#!/bin/bash
set -u
cd /media/data3/dengkw/idea04
KEY=$(python3 -c 'import json
d=json.load(open("configs/llm.json"))
nb=d.get("newapi") or d.get("providers",{}).get("newapi")
print(nb["key"])')
echo "key prefix: ${KEY:0:12}..., len=${#KEY}"
external_baselines/reagent/venv_reagent/bin/python workspace/tmp/r41c_diagnose_reagent_bug.py "$KEY" 2>&1
