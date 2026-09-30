# Task report — responsibility/update gate deadlock (2026-09-30)

## Observation

The versioned promotion runner reaches a canonical first episode, a
source-bound public offer, isolated policy read and a later selection for both
ownership controls. It then stops without writing `RoleEvidenceUpdate`,
`LaterAssignment`, `task_start(1)` or a later outcome. The stop is required by
the current contracts:

1. `producer_feedback_eligibility` may report diagnostic `ELIGIBLE`, but its
   `policy_update_allowed` field is hard-coded to `false`.
2. The public offer consequently has `UNKNOWN` disposition and cannot update
   the policy.
3. `LaterAssignment` requires a non-empty `evidence_ids` tuple.
4. `later_use_valid` can only be observed after a later assignment and later
   outcome.

The current dependency is therefore cyclic:

```text
policy update permission ← later-use validation ← later assignment
                         ← role evidence publication ← policy update permission
```

The v1/v2/v3 receipts in
`experiments/logs/n03_pipe3_live_runner_v2_qualification_20260930_v{1,2,3}/`
are the reproducible evidence. This is a method-contract blocker, not an API,
sandbox or GPU failure.

## Candidate resolutions

### A. Two-stage evidence and update (recommended for review)

Separate three states that are currently collapsed:

- `attribution_eligible`: the producer defect, recipient action and contract
  outcome are causally bound;
- `evidence_publish_allowed`: the eligible event may become a public,
  pre-execution role-evidence record and be cited by `LaterAssignment`;
- `policy_update_allowed`: the updater may change persistent policy state.

The first two can be decided from the completed source episode. The third is
decided after the later task outcome validates the use of that evidence. The
event-time rule is:

```text
source episode → attribution/evidence gate → public offer → assignment
→ later task outcome → delayed policy update
```

The update remains selected-only and no-op for UNKNOWN. Recipient-owned repair
never passes the attribution gate. A later outcome is used as delayed
validation/correction, not as information that leaks into the assignment that
preceded it.

This keeps the scientific question identifiable: evidence can affect a future
assignment before execution, while persistent learning is credited only after
the independent later-use result arrives.

### B. Exogenous bootstrap assignment

Permit a pre-registered uniform/bootstrap assignment with a separate
`bootstrap` assignment type, then allow role evidence and updates only after its
later outcome. This breaks the cycle operationally, but it adds a new ledger
primitive and makes the first assignment a baseline phase rather than a result
of peer evidence.

### C. Keep the current gate

Do not create legal later assignments until an external source of role
evidence exists. This is logically consistent but prevents the stated
judgment → evidence → assignment experiment from ever starting on a fresh
root; it can only serve as a closed-gate safety control.

## Constraints for the next implementation

No option may turn diagnostic `ELIGIBLE` into a training label, use recipient
integration as a producer defect, expose a later outcome at the earlier read
cut, or silently alter the Goal. Before changing the active method contract,
the chosen option needs a versioned schema, replay/rollback rules, an explicit
UNKNOWN denominator and a paired recipient-owned control. The benchmark and
baseline gates remain closed, and no external API/A800 run follows from this
report.

## Current status

This report records the blocker and options only. It does not select an option
or modify `method_v1.0_20260928.md`, the active benchmark manifest, or the Goal.
