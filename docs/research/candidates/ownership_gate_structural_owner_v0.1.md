# Candidate design — structural-owner gate with judged-role calibration (v0.1)

日期：2026-10-06
状态：`CANDIDATE — NOT ACTIVE`
前置决议：等待责任归因门 A/B 确认

## Motivation

C1 v3 exposed that a free-text `target_role` returned by the judge can vary across policy arms
for the same source artifact. If that field is a hard eligibility condition, an arm can be
censored before selection even when the contract, artifact, registered defect, and scorer all
identify the same producer-owned event. The candidate design separates ownership truth from a
noisy judge description.

## Proposed event fields

Every source event retains both fields:

```text
structural_owner_role    ∈ {producer, recipient, sink, mixed, unknown}
judged_target_role       ∈ {producer, recipient, sink, unclear}
judged_target_paths      list[path]
judged_role_agrees       bool | null
```

`structural_owner_role` is computed from the frozen task contract, candidate registry, changed
paths, independent scorer, and registered defect. The model cannot write or override it.
`judged_target_role` and paths remain raw, auditable observations used for judge reliability and
disagreement analysis.

## Eligibility rule (candidate A)

An event is eligible for producer role evidence only when all of the following hold:

1. structural owner is `producer`;
2. source delivery, recipient use/action, producer contract check, and artifact binding are
   complete;
3. the registered producer defect or producer success is directly observed;
4. no recipient-owned, sink-owned, mixed, resource-failed, or unresolved path is included; and
5. the event passes exactly-once and read-cut checks.

The judged role never creates evidence by itself. Disagreement is stored as a calibration flag;
it may be reported as a safety/quality endpoint or used in a separately pre-registered judge
reliability analysis.

## Required qualification cells

Before live comparison, the gate must pass zero-call mutation and replay cells for:

| Cell | Structural owner | Judged role | Expected result |
|---|---|---|---|
| A1 | producer | producer | eligible producer evidence |
| A2 | producer | recipient | eligible evidence + disagreement flag |
| A3 | recipient | producer | `UNKNOWN`, no producer evidence |
| A4 | mixed | producer | `UNKNOWN`, no producer evidence |
| A5 | unknown | producer | `UNKNOWN`, no producer evidence |
| A6 | producer | unclear | eligible evidence + calibration missing flag |
| A7 | producer | producer | duplicate/reordered arrival is idempotent |
| A8 | producer | producer | path/registry/scorer mutation fails closed |

The same cells must be replayed across each policy arm with identical public input digest and
must not change selection, propensity, or cost before the source event becomes legal evidence.

## Falsifiers and boundary

This candidate is rejected if a structural-owner mutation is accepted, a recipient/mixed event
updates producer state, a judged-role disagreement changes eligibility without a structural change,
or two arms receive different public inputs solely because of judge wording. Passing these cells
would qualify the attribution boundary only; it would not show that situated evidence improves
future assignment or that the selector is real-time/stable.

## Status

This document is a design candidate, not an active decision. Do not update the active method or
run confirmation/API/GPU experiments until the A/B gate choice is recorded in a superseding ADR.
