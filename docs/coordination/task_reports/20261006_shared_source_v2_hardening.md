# Task report — shared-source v2 hardening after independent review

Date: 2026-10-06
Status: `PARTIAL`
Goal change requested: `false`
Scientific result: `none`

## Trigger

The v1 six-case qualification was useful but too weak for a live comparison. A
read-only independent Codex review demonstrated that changing the same nested action
or delivery digest in every arm still passed v1 validation. The review also found
that v1 source digests were self-seals, projection digests were not recomputed,
shared costs had no allocation semantics, denominator states were under-specified,
source policy-invariance lacked provenance fingerprints, and policy selection had no
native-ledger binding.

## Repair

Added `shared-source-projection-v2` and a new candidate card. The v2 contract now:

- checks an externally supplied source digest against a canonical source payload;
- requires policy-invariant artifact/contract/registry/scorer/prompt/raw-response
  fingerprints and binds delivery to the artifact fingerprint;
- recomputes each arm digest and rejects coordinated nested, delivery, namespace,
  seal, and projection mutations;
- distinguishes `SOURCE_COMPLETE`, `STOPPED_PRE_TARGET`, and `SOURCE_INCOMPLETE`,
  together with explicit source/target booleans and typed ITT inclusion;
- reports source cost once and target cost as the per-arm sum;
- validates a policy-decision → native-selection binding contract with registry,
  input/state digests, chosen candidate and propensity.

## Evidence

Command:

```text
python3 scripts/peerrolebench_shared_source_v2_qualification.py \
  --output experiments/logs/n03_shared_source_qualification_20261006_v3
```

Ten cases passed. Focused v1/v2 tests pass `6/6`; the run made `0` LLM calls,
launched `0` GPU jobs, invoked no native grader, and records
`scientific_claim_allowed=false`.

Artifacts:

- [v2 summary](../../experiments/logs/n03_shared_source_qualification_20261006_v3/summary.json)
- [v2 raw cases](../../experiments/logs/n03_shared_source_qualification_20261006_v3/raw.jsonl)
- [v2 candidate card](../../research/candidates/c1_shared_source_card_v0.2_20261006.md)

The external seal in this qualification is a fixed synthetic manifest value used to
exercise the contract. It is not proof of a live artifact manifest. The next card
must generate and freeze that manifest before policy execution.

## Gate reconciliation

This hardens one engineering prerequisite and closes none of ER-G1's scientific
effect requirements. Independent roots, independent live histories, actual
policy/native sidecar integration, later assignment, same-information baseline
parity, update latency/forgetting and end-to-end quality/cost remain open. No API,
GPU or paper result cell is authorized by this task, and the Goal is unchanged.
