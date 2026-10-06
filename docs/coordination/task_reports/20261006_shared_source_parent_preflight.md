# Task report — parent-owned live source and arm projection

Date: 2026-10-06  
Status: `PARTIAL`  
Goal change requested: `false`  
Scientific result: `none`

## Purpose

The previous preflight only converted a historical arm-local episode. That was
insufficient for the benchmark claim: an arm could reacquire or independently
construct its own source. This task changes the C1 runner so the source phase is
parent-owned and happens once before any policy arm is created.

## Implemented contract

- `scripts/peerrolebench_c1_pipe3_bounded_live.py` now builds materials,
  candidate registry and public features once, runs `parent_source` once, and
  writes its ledger, selection binding, source manifest and external digest
  before entering the arm loop.
- Each arm clones the immutable parent ledger prefix and ingests the exact
  parent policy selection into its own policy object. It does not call the
  source judgment/action/scorers again. The arm receives a distinct policy
  namespace and a distinct projection digest while retaining the same
  `selection-parent-0` source selection.
- The source receipt binds selection ID, delivery ID, chosen candidate, registry
  digest, policy/native selection binding digest, card digest, source commit,
  runner version and root. `source_digest.txt` is read as a separate expected
  digest by the parent preflight.
- The runner records an expected eight-request budget for a future live card:
  two parent-source requests plus two target requests per arm. The current
  historical v2 card is not silently reclassified or rerun.
- Cost metadata now distinguishes `COMPLETE` from `UNKNOWN`; missing usage or
  stage timing cannot be presented as measured zero. The scorer total uses the
  recorded outcome-level aggregate when recipient/adoption scorers do not emit
  independent timing fields.
- Selection bindings now require a non-empty unique string candidate menu and a
  chosen candidate that is exactly in that menu.

## Qualification evidence

The zero-call parent fixture was written to
`experiments/logs/n03_c1_zero_call_parent_fixture_20261006_v2/` before the run.
It reports:

- `QUALIFIED_OFFLINE_FIXTURE`, three complete development-only arms;
- `0` real API calls and `0` GPU jobs;
- one source receipt digest
  `b223df06b387f343621055b2502418b1cd8c514daf7fbc07c4036c333009993b`;
- three distinct projection digests and the same source selection
  `selection-parent-0` in all arms;
- source cost status `COMPLETE` only because the fixture explicitly supplied
  complete metadata; this is not a cost result for the real API.

The focused regression command was:

```text
python3 -m pytest -q tests/test_peerrolebench_c1_live_contract.py \
  tests/test_peerrolebench_external_source_manifest.py \
  tests/test_peerrolebench_shared_source_v2.py \
  tests/test_peerrolebench_shared_source.py
```

Result: `11 passed`. The independent v2 zero-call qualification was also
rerun at `experiments/logs/n03_shared_source_qualification_20261006_v3/` with
10 fail-closed cases and no API/GPU calls.

## Cost and failure-path hardening

The first implementation still had two accounting hazards. It could count the
action API elapsed time together with the action result wall time, and an arm
failure after a completed target episode could replace the incurred target cost
with `0.0`. Both paths are now explicit:

- `episode_cost()` chooses one action timing source and records a timing
  disagreement as `UNKNOWN`; scorer timing chooses either the producer plus
  outcome aggregate or the independent recipient/adoption route.
- The runner writes `target_cost_receipt.json` immediately after the target
  episode. The outer failure handler recovers that receipt and marks later
  update/manifest failures as `UNKNOWN` while retaining the measured lower
  bound and any recorded update latency.
- The canonical arm ledger is `cost_ledger_row` plus
  `validate_cost_ledger()`: the shared source cost is counted once and target
  costs are summed once per arm. The legacy diagnostic `result["cost"]` is not
  part of this aggregate.

The focused post-fix checks are 18 passed across the source-cost, external
manifest, C1 runner, shared-source, and baseline-contract suites. The fresh
zero-call receipt is
[`n03_c1_zero_call_parent_fixture_20261006_v3`](../../../experiments/logs/n03_c1_zero_call_parent_fixture_20261006_v3/summary.json).
It reports 0 real API calls and 0 GPU jobs, one source cost of `1.293608125`
wall-second units, and three target cost rows totalling `3.721094624` units.
Those values validate the fixture's declared metadata only; they are not a
model or quality result. The fixture remains `scientific_claim_allowed=false`.

## Goal reconciliation

This advances ER-G3/ER-G4 engineering prerequisites: source reuse, native
selection lineage, arm isolation and explicit cost uncertainty are now
executable. It does not satisfy ER-G1 or ER-G2 efficacy: the fixture has no
real judgments, no unseen stream, no second structural root, no independent
history comparison and no scientific estimate. The parent and arms are still a
single-root development path, and the policy implementation is not locked as
the final method.

The remaining blocker is evidence, not a reason to lower the Goal. Before a
real run, freeze a new card at the committed runner, verify the second-root
authority and same-information baseline matrix, then execute the bounded live
card with real API logs. A800 remains deferred until that live signal and its
cost/UNKNOWN accounting are valid. The parent-source choice is recorded here as
an implementation candidate, not as a user-confirmed decision; no ADR was added
without the required dual confirmation.
