#!/bin/bash
cd /media/data3/dengkw/idea04/external_baselines/chateval
echo "=== agentverse/agents/ ==="
ls agentverse/agents/ 2>/dev/null
echo
echo "=== agentverse/environments/ ==="
ls agentverse/environments/ 2>/dev/null
echo
echo "=== Search for aggregator / judge / final / decide / verdict in ChatEval (excluding venv) ==="
grep -rn "aggregator\|judge\|final_answer\|final_decision\|verdict\|consensus\|Reviewer" agentverse/ --include='*.py' 2>/dev/null | grep -v __pycache__ | head -25
echo
echo "=== ChatEval available task configs (where the multi-agent debate logic lives) ==="
find agentverse/tasks/ -name '*.yaml' 2>/dev/null | head -10
echo
echo "=== Sample task config: llm_eval/faireval ==="
ls agentverse/tasks/llm_eval/ 2>/dev/null
cat agentverse/tasks/llm_eval/faireval/config.yaml 2>/dev/null | head -80
