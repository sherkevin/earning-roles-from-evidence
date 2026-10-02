# 2026-10-03 N03 PIPE3 source→target contract qualification

## Scope

This step validates the executable card schema before any live model call. It does not run
candidate code, a real API, a benchmark arm, a baseline, or a GPU job. Historical v1 and the
fixed v2 receipt are both retained; the v2 card digest is the current receipt.

## Receipt

- card: `configs/aamas2027/n03_pipe3_real_smoke_v7.json`
- qualification: `scripts/peerrolebench_pipe3_chain_contract_qualification.py`
- v2 receipt: `experiments/logs/n03_pipe3_chain_contract_qualification_20261003_v2/`
- status: `QUALIFIED_OFFLINE`
- checks: `27/27`
- real API calls: `0`
- GPU jobs: `0`
- `scientific_claim_allowed`: `false`

The checks cover `ArtifactRole`/development qualification scope, explicit source episode 0 and
target episode 1, bounded call/episode budgets, all source→offer→assignment→target-credit
lineage keys, disjoint ownership, producer FAIL/0 and recipient/mixed/out-of-contract label
rules, at least two registered candidate peers, menu/order/propensity/read-cut receipts, and
publish-no-update/credit-once/target-outcome requirements.

## Test failure and correction

The first focused test run found that the validator assumed a card path under the repository
when a negative-control card was placed in pytest's temporary directory. The validator now
records an absolute path for external test cards while keeping repository-relative paths for
normal receipts. The negative controls then passed: missing target-credit keys and treating
source adoption as later use both fail closed. The final focused test result is `7 passed`.

## Boundary

This closes a schema/lineage precondition only. It does not establish that a real recipient
will produce a valid judgment, that any producer defect is observable, that peers have
identifiable persistent differences, or that later assignment changes quality or cost. A live
smoke remains gated on this contract plus the existing scorer/action/source-bound qualification;
no API or GPU call is authorized by this receipt.

`goal_change_requested=false`.
