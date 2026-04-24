#!/usr/bin/env python3
"""Probe HotpotQA seed sample + run_e017 expected raw_inputs format."""
import json
import sys
from pathlib import Path

seed_path = Path("/media/data3/dengkw/idea04/artifacts/seed/hotpotqa_validation_100.jsonl")
if not seed_path.exists():
    print(f"ABSENT: {seed_path}")
    sys.exit(1)

with seed_path.open() as fh:
    first = json.loads(fh.readline())

print("=== hotpotqa seed first record keys ===")
print(list(first.keys()))
print()
print("=== values (truncated) ===")
for k, v in first.items():
    vs = str(v)
    print(f"  {k}: {vs[:120]}")
print()

# Check if this matches run_e017_fullval_seed.py expected raw_inputs format
raw_inputs_sample_path = Path("/media/data3/dengkw/idea04/artifacts/round2_gpt41mini_stage2_200/run_20260419_114943/edo_stage2_chain/raw_inputs.jsonl")
if raw_inputs_sample_path.exists():
    print(f"=== raw_inputs.jsonl sample keys (from old artifact) ===")
    with raw_inputs_sample_path.open() as fh:
        ri = json.loads(fh.readline())
    print(list(ri.keys()))
    for k in list(ri.keys())[:8]:
        print(f"  {k}: {str(ri[k])[:120]}")
else:
    # Try alternative locations
    alt = list(Path("/media/data3/dengkw/idea04/artifacts").rglob("raw_inputs.jsonl"))
    print(f"=== any raw_inputs.jsonl on server ===")
    print(f"  found {len(alt)}")
    for p in alt[:5]:
        print(f"  {p}")

print()
print("=== run_e017 raw_inputs expected keys (from script lines 190-220) ===")
scripts_path = Path("/media/data3/dengkw/idea04/scripts/run_e017_fullval_seed.py")
if scripts_path.exists():
    lines = scripts_path.read_text().split("\n")
    for i in range(185, 225):
        if i < len(lines):
            print(f"  {i+1}: {lines[i]}")
