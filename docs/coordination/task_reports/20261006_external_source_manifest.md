# Task report — parent-owned external source manifest preparation

Date: 2026-10-06
Status: `PARTIAL`
Goal change requested: `false`
Scientific result: `none`

## Purpose

The shared-source v2 contract requires a source digest supplied from outside the
policy-arm projection. The existing C1 runner had only arm-local source records,
so a new live comparison would not yet have a policy-invariant source boundary.
This task adds a preparation utility that extracts one source episode into a
parent-owned receipt and validates it before any arm projection.

## Implementation

- `scripts/peerrolebench_build_external_source_manifest.py` reads one completed
  source episode, its immutable material/registry files and source-only request /
  response files.
- It computes artifact, contract, registry, scorer, prompt and raw-response
  provenance fingerprints; records source API/scorer/action wall costs; sets the
  target state to `NOT_STARTED`; computes the canonical digest outside the arm;
  and calls `freeze_source_receipt` immediately.
- It does not call an LLM, run a scorer, alter a historical result, or perform a
  policy choice. The manifest explicitly records `historical_conversion=true`
  and `scientific_claim_allowed=false`.

## Qualification

The historical PIPE3 v4 `no_update` source was converted and validated:

- source digest:
  `ea8d1d03ed18f8895b7214ea7d84e028472896ea7661330bfce359eef9e2a73a`;
- focused tests: `2 passed`;
- real API calls: `0`;
- GPU jobs: `0`;
- receipt directory:
  `experiments/logs/n03_external_source_manifest_20261006_v1/`.

The receipt is a parent-owned artifact-preparation example, not an independent
source acquisition and not benchmark evidence. Its historical provenance is
kept explicit because the next live card must generate the source manifest in
the same parent phase before policy execution.

## Gate reconciliation

This closes one prerequisite for shared-source accounting. It does not close
second-root authority, live same-information baseline parity, independent live
histories, later assignment/use, complete confirmation cost, or the scientific
submission gate. The next live card must use the utility on a freshly acquired
source, project the receipt into separate arm namespaces, validate each native
selection binding, and report source cost once plus target cost per arm.
