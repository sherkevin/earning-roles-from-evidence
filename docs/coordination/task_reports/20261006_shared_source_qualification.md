# Task report — shared-source projection qualification

Date: 2026-10-06
Status: `PARTIAL`
Goal change requested: `false`
Scientific result: `none`

## Purpose

The previous C1 live card showed that an arm-specific recipient action can stop one
policy before target assignment. The next development design therefore needs to
acquire one source episode once and project the same immutable public evidence into
isolated policy namespaces. This task validates that seam before any further paid
API call. It is an engineering qualification, not an independent-history
benchmark result and not evidence of role-learning efficacy.

## What was implemented

`peerrolebench_shared_source.py` defines `shared-source-projection-v1`:

- a source receipt must carry delivery, judgment, action, producer score, outcome,
  responsibility-gate, episode-status, estimand and acquisition-cost fields;
- every arm receives a unique policy namespace while source fields and the source
  receipt digest remain invariant;
- mutations to delivery, gate, action, outcome or cost are rejected;
- `PENDING_ATTRIBUTION` and `UNKNOWN` remain `ITT_ONLY`, so a determinate gate stop
  cannot silently become an eligible conditional observation.

The implementation is deliberately only a projection seam. It does not claim that
the projected arms are independent histories; the source acquisition cost is shared
and must be accounted for by a future card.

## Qualification evidence

Command:

```text
python3 scripts/peerrolebench_shared_source_qualification.py \
  --output experiments/logs/n03_shared_source_qualification_20261006_v1
```

The six cases in the receipt are:

1. valid source projection;
2. delivery-digest mutation rejected;
3. responsibility-gate mutation rejected;
4. action mutation rejected;
5. acquisition-cost mutation rejected;
6. pending attribution retained as ITT-only.

All six passed. The run made `0` LLM calls, launched `0` GPU jobs, invoked no
native grader, and records `scientific_claim_allowed=false`.

Artifacts:

- [qualification summary](../../experiments/logs/n03_shared_source_qualification_20261006_v1/summary.json)
- [raw case log](../../experiments/logs/n03_shared_source_qualification_20261006_v1/raw.jsonl)
- [focused tests](../../tests/test_peerrolebench_shared_source.py)

The focused suite, together with the structural-owner and C1 contract suites, passed
`19` tests. This result is reproducible offline and does not alter the frozen C1
v4 receipt.

## Goal and gate reconciliation

This closes one small implementation prerequisite for the active method: a future
bounded comparison can separate `episode_status`, `gate_status`, and
`estimand_inclusion` while charging shared acquisition cost. It does **not** close
the Goal requirements for independent roots, independent live histories,
responsibility-safe labels, future assignment, online learning, cost/latency
analysis, or a scientific effect. The scientific readiness flag therefore remains
false and the next live card remains design-only until its zero-call contract adds
policy-selection/native-selection binding and complete cost fields.

No claim, result cell, baseline ranking, or Goal requirement was downgraded.
