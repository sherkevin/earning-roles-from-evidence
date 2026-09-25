# ArtifactRole-TB vertical slice: protocol and scorer validation

Date: 2026-09-25  
Status: development evidence only; no method-effect claim.

## What was tested

The adapter ran two parameterized TeamBench task families, `CR2_style_enforce`
and `DIST1_queue_race`, at seeds 0 and 1. Each episode used the same three
persistent fixture peers:

- `peer_01_noop`: the generated buggy workspace;
- `peer_02_repair`: a deterministic repair fixture;
- `peer_03_partial`: a deliberately partial repair.

For each of four conditions (`random`, `static_best`, `terminal_only`, and
`recipient_judgment`), the runner recorded:

```text
selection → delivery → recipient judgment → consumer action
→ fresh evaluator grade → terminal outcome → evidence update
→ next assignment
```

The strict ledger rejected deliveries whose producer was not selected, rejected
judgment/action mismatches, required terminal outcome before an evidence update,
and rejected retroactive or wrongly attributed later assignments. Every run
also stored candidate artifact digests, the selected digest before grading, the
native per-check score payload, and a post-grade digest.

## Results

Raw records: `experiments/logs/peerrolebench_tb_vertical_20260925_secure_v4/raw.jsonl`  
Summary: `experiments/logs/peerrolebench_tb_vertical_20260925_secure_v4/summary.json`

The run completed 16 episodes in 25.14 seconds. Terminal partial scores ranged
from 0.0833 to 0.92, with mean 0.3196. All selected artifacts were unchanged by
the grader, all test trees and `expected.json` files matched their pre-grade
hashes, and all strict ledgers recorded exactly one evidence update per
delivery.

The score spread is a fixture sanity check, not evidence that a selector learns:
the repair fixture is hand-written, the candidate pool is tiny, and the static
arm is only a frozen fixture arm. In particular, the CR2 repair fixture reaches
0.92 on seed 0 but 0.23 on seed 1 because it hard-codes seed-0 symbol names;
this exposes the need for seed-aware candidate generation and held-out
generalization.

The ledger is shared across the two seeds within each task-condition. The first
episode records the later assignment before the second `task_start`; the second
episode therefore exercises the assignment boundary instead of merely writing a
standalone assignment into a discarded ledger.

## Real model interface check

One recipient-judgment request was sent through cc-switch provider `内部` to
`qwen3.8-max`. The prompt exposed task text, candidate id/version, artifact
digest, and a diff summary; it excluded `reports/`, `expected.json`, the
grader, and terminal score. The corrected real response was valid JSON:
`accept`, predicted score `0.90`, confidence `0.62`, with 256 input and 700
output tokens. The first local attempt received a valid response but was
misclassified by a postprocessing variable error; that raw line and a correction
event are retained in
`experiments/logs/peerrolebench_real_judgment_20260925/raw.jsonl`.

This call validates transport, schema parsing, and visibility discipline only.
It is not a performance result and was not fed back into selector state.

## Why the benchmark is not frozen yet

The native TeamBench grader is a task scorer, not a complete peer-selection
isolation boundary. The wrapper now copies only candidate source files into a
fresh evaluator workspace and makes tests/expected labels read-only, but source
executed by the grader can still inspect sibling reports. A containerized
evaluator with a separate grader process is required before adversarial or
LLM-generated candidates are used.

Two task families and two seeds are also insufficient for estimating online
learning, recovery after environment changes, or later-assignment benefit. The
next gate is therefore: build the full sandbox, add at least three development
seeds plus held-out seeds across more task families, and freeze static-best from
the development split. No A800 scaling is justified before that gate passes.
