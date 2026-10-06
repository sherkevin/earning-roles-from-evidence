# Task report — C1 selection binding integration

Date: 2026-10-06
Status: `PARTIAL`
Goal change requested: `false`
Scientific result: `none`

## Finding

The C1 runner already created policy selections, native `PeerRoleLedger` events and
sidecar manifests, but it did not expose a v2 binding receipt or validate the roots
at arm completion. The role-evidence overlay also appended a `role_evidence_offer`
without a matching `role_evidence_read`, so the auxiliary chain correctly rejected
the arm as incomplete. The post-update selector is a cloned preview and must remain
outside the native ledger.

## Repair

- `commit_role_evidence_selection` now appends a typed `role_evidence_read` row
  bound to the role offer, assignment and committed decision sidecar;
- the C1 runner builds and validates a v2 selection binding for every committed
  `SelectionSeal`, checking policy/native IDs, sidecar/native record digest, menu,
  chosen candidate, registry digest, state/input digest and propensity;
- each completed arm now validates and stores native and auxiliary manifest roots,
  committed binding receipts, and explicit preview-only flags;
- no preview selection is counted as a native selection or target outcome.

## Qualification evidence

The zero-call C1 contract test uses the actual `Pipe3SelectionBoundary` and fake
actor only to exercise protocol paths. It now passes `10` focused tests across the
C1 runner, role-evidence commit and shared-source v2 contract. It made `0` real
LLM calls, launched `0` GPU jobs, and retains `scientific_claim_allowed=false`.

The test checks all three arms' committed selection bindings and non-`GENESIS` native
and auxiliary roots. The historical C1 v4 live receipt is unchanged; no live rerun
was started. The next live card must be re-frozen at the new runner commit and must
also supply a real external source manifest for shared-source v2.

## Gate reconciliation

This closes a runner/ledger accounting prerequisite. It does not establish a second
root, independent histories, later-use utility, same-information baseline parity,
online-training speed, forgetting, or any efficacy result. No benchmark or Goal
requirement was downgraded.
