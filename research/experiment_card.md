# Experiment card — next scientific gate

Status: `BLOCKED_PRE_EXECUTION` until the material handoff descriptor, two-root authority,
same-information contextual arm, and live runner are qualified.

## Design

- Primary track: `ArtifactRole`.
- Development root and confirmation root: structurally independent and frozen before calls.
- Arms: `uniform`, `no_update`, `raw_acceptance`, `terminal_only`,
  `contextual_trust_linear`, `pooled_controller`, `RARE`.
- Four contrasts: no public evidence/no delayed update; public evidence only; delayed update
  only; public evidence plus delayed update.
- Recipient cases: accept/use, accept-with-rework/repair, reject/redo, recipient-only,
  mixed and unresolved attribution.
- Selection: identical menu, read cut, arrival schedule, exploration opportunity, propensity,
  model/API/tool/token budget, state capacity and complete cost fields.

## Primary measurements

H1 information gain; H2 assignment change and unseen-root quality/return/repair/full cost;
H3 publish/read/update p50/p95, service lag, state bytes, drift recovery, forgetting,
`UNKNOWN`, failure and duplicate rates.

## Logging

Before execution: JSON config, code/data/model hashes, seed, hardware, budgets and stopping
rules. During execution: one JSONL event per API/tool/scorer call, raw response, token/cost,
latency, error and lineage. After execution: per-sample raw results, processed metrics,
intervals, statistical tests and failure/UNKNOWN denominators.

## Stop rules

No A800 or scale-up before the live matrix is reproducible and same-information parity passes.
Stop expansion if H1, H2 or H3 fails, if a strong contextual arm matches the candidate, or if
any event-time, attribution, cost or replay invariant fails.
