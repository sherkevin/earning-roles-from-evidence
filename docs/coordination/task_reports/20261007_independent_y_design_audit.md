# Task report — independent terminal outcome design audit

Date: 2026-10-07
Status: `CANDIDATE_DESIGN`
Goal change requested: `false`
Scientific result: `none`

## Why this is the next gate

The live C1 smoke exposed a real identification problem: the recipient judgment
was positive while the producer contract and downstream adoption checks failed.
Using that judgment as the update label would therefore teach the selector the
wrong responsibility. Versioned Qp/J/A/D/Y/L receipts now make the disagreement
visible, but the runner still has no independent terminal `Y` measurement.

The distinction required by the active Goal is:

```text
Qp  producer-owned contract quality of the delivered artifact
J   recipient's situated judgment before action
A   recipient action and ownership-safe file diff
D   immediate downstream adoption of that action's output
Y   later target-task terminal quality after an assignment
L   delayed credit binding the source evidence to the later assignment
```

`Y` cannot be a renamed copy of `D`, and the source episode's `D` cannot be
retroactively treated as later-use evidence. Until this is enforced, a
terminal-only baseline and any claim about future role assignment are not
scientifically identifiable.

There is a second contamination to remove before a confirmatory card: the
current adoption scorer's `D` response contains both `A1_producer_boundary`
and `A2_sink_adoption`. Thus the current D receipt is a composite diagnostic,
not a pure downstream label. `A1` belongs in Qp; a clean D scorer must expose
only downstream acceptance checks with its own version and digest. The v3
channel records this provenance but does not silently relabel the historical
scorer output.

## Alternatives examined

### A. Reuse the current adoption scorer as Y

This is the cheapest implementation, but it measures the same public
producer→processor→sink path as `D`. It has no later assignment binding and no
independent terminal measurement. It is rejected as a scientific Y; it may remain
an engineering diagnostic.

### B. Run a private terminal scorer only after the target assignment

The source episode records Qp/J/A/D and can publish evidence only if the
responsibility gate passes. After the target selection, delivery, and action, a
separate private worker runs a frozen terminal contract over the target snapshot.
The worker receives only the sealed public snapshot plus task/seed metadata; it
does not receive J, A, D, policy state, ledger events, or hidden expected text.
It returns a typed `TerminalOutcome` with its own scorer version, check coverage,
response digest, and `PASS`/`FAIL`/`UNKNOWN` status. This is the recommended
candidate because it gives Y a different input scope, execution point, and
failure channel while preserving the existing D receipt.

### C. Treat a recipient's later self-report as Y

This is not independent: it is another judgment and can inherit the same
misattribution or prompt incentives. It may be logged as an auxiliary signal,
but it cannot be the terminal label.

## Candidate contract for B

The worker must satisfy all of the following before a live card can use it:

1. **Temporal binding.** A source episode has `Y=UNKNOWN`; only a target episode
   with a committed `assignment_id`, target `selection_id`, `task_start_id`, and
   target delivery digest may emit `Y`.
2. **Independent input.** The worker input digest is the target post-action
   public snapshot plus the pinned task/seed contract. J, A, D, policy state,
   source outcome, and operator ledger are absent from the worker payload.
3. **Private checks.** Assertions and expected values remain in the trusted
   worker boundary. The actor receives neither their source nor their result.
4. **Coverage discipline.** A malformed response, timeout, resource error, or
   incomplete check set produces `UNKNOWN` with no policy update. A binary label
   is allowed only when every pre-registered terminal check is determinate.
5. **Separate provenance.** `Y` has its own scorer/version/response digest and
   `derived_from=[]`; `D` remains policy-invisible unless a later method contract
   explicitly admits it. The legacy conjunction is retained only for replay.
6. **No double counting.** Target scorer time, API/tool calls, and worker cost are
   separate ledger fields. Source cost is counted once; target cost is counted
   once per arm.
7. **Mutation tests.** Zero-call tests must reject a source Y, a missing
   assignment, a wrong target binding, a D response substituted for Y, a partial
   terminal response, and a duplicate/late Y. No policy state may change in any
   rejected case.
8. **D purity.** The next scorer version must either remove
   `A1_producer_boundary` from D or mark the result as `D_composite` and exclude
   it from any pure-D analysis. A confirmatory card may not call a composite D a
   downstream-only label.

The private worker must compare the target artifact with a pre-generated,
versioned holdout expected-output digest from the frozen task contract. It may
not generate its own oracle from the candidate's producer or processor. The
holdout IDs, reference digest, and worker digest belong in the pre-run manifest;
any mismatch is `UNKNOWN`.

## Zero-call contract qualification

The read-only validator is implemented in
[`peerrolebench_independent_y_contract.py`](../../../scripts/peerrolebench_independent_y_contract.py).
It accepts only target receipts with the complete assignment/selection/task-start
binding, a target artifact digest, a sealed holdout digest, and a complete
terminal response. Four tests cover the positive target row, source/D relabels,
binding and digest mutations, and UNKNOWN/partial/duplicate/late rows. The
qualified rerun is recorded at
[`n03_independent_y_contract_qualification_20261007_v1`](../../../experiments/logs/n03_independent_y_contract_qualification_20261007_v1/summary.json):
4/4 passed, 0 API calls, 0 GPU jobs. This is a provenance gate only; the hidden
terminal worker and its reference holdout are not implemented yet. The first
test invocation happened before config creation and is explicitly recorded as a
process deviation; it is not used as evidence.

## What this would and would not establish

Passing the contract would establish that the runner can observe an independent
later terminal signal and preserve its lineage. It would not establish that J is
predictive, that any updater improves selection, or that the benchmark is
qualified. Those require two structural roots, shared-information baseline
parity, independent histories, and a real API confirmation card.

The active method and benchmark documents remain unchanged. This report is a
candidate implementation specification pending the next protocol qualification;
it does not authorize a new live API run or an A800 job.

## Goal reconciliation

- ER-G1: `PARTIAL` — the causal chain is specified, but independent Y is not yet
  observed in the live runner.
- ER-G2: `OPEN` — no online update or forgetting evidence exists.
- ER-G3: `PARTIAL` — D and Y are now explicitly separated in the contract;
  D purity and same-information baseline parity remain open.
- ER-G4: `PARTIAL` — the required scorer boundary and failure rules are listed;
  no new result is claimed.
- ER-G5: remains closed. No scientific table cell or A800 job is justified.
- ER-G6: no Goal change requested (`false`).
