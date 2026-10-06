# ADR 0048 — Parent-owned shared source before arm execution

Status: Accepted for the next C1 runner card  
Date: 2026-10-06  
Supersedes: none

## Context

An arm-local source episode cannot support a fair policy comparison: each arm
could see a different delivery, judgment, scorer state or source cost. The
shared-source v2 contract already validates an immutable receipt, but the old
runner did not acquire that receipt before entering the arm loop.

## Decision

The live runner must execute one parent-owned source phase before any policy arm
is constructed. It must seal the source ledger prefix, native/policy selection
binding, candidate registry, card/commit provenance and an externally supplied
source digest. Each arm then imports that exact immutable prefix into its own
policy namespace and may execute only its own later assignment/target episode.
Source API/scorer calls and source cost are counted once; target calls and target
cost are arm-specific. A preview-only post-update choice is never entered into
the causal ledger.

## Rationale

This is the minimum design that makes “same source, different policy” a testable
statement. It prevents source reacquisition from becoming an uncontrolled
treatment difference, preserves native ledger replay, and makes cost/UNKNOWN
denominators explicit. The decision is an engineering invariant, not evidence
that any policy improves unseen quality or learns a stable role.

## Consequences

- A future live card has a parent source budget plus one target budget per arm;
  the current bounded C1 shape is 2 + 3×2 = 8 API requests.
- Source projections are three namespaces over one source, not three independent
  samples; they cannot supply independent confidence intervals.
- Missing usage/stage timing is recorded as `cost_status=UNKNOWN`, never as a
  measured zero. A source can remain protocol-valid while being excluded from
  complete-cost scientific analysis.
- This does not close the second-root, same-information baseline, independent
  history, or efficacy gates in `GOAL.md`; no Goal downgrade is implied.
