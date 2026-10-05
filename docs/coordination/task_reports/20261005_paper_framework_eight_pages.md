# Task report — AAMAS paper framework and exact body-page build

- **Date:** 2026-10-05
- **Status:** `DONE_FOR_WRITING_SCAFFOLD`
- **Goal change requested:** `false`
- **Scientific readiness:** remains `false`; no empirical result was invented or promoted.

## Purpose

The user requested a complete paper framework in which the remaining work is primarily to
fill verified experiment results. The paper must use the official AAMAS main-track layout and
occupy exactly the maximum allowed body length, excluding references.

## Venue and page evidence

The official AAMAS 2027 submission instructions state that main-track papers may be at most
eight pages, with any number of additional pages for bibliographic references, and require the
official LaTeX style without layout modifications. The local archived copy and the live official
page agree: <https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/instructions/>.

The reviewed artifact is preserved in [`artifacts/aamas2027/paper_framework_20261005/`](../../artifacts/aamas2027/paper_framework_20261005/)
and locally in the isolated build directory. Its receipt is:

```text
article/aamas2027/build/paper_framework_20261005_final/main.pdf
total PDF pages:       9
body pages:            8
references start:      page 9
SHA-256:               431be9e9deb5995a06f55156c3e74d6f2b75bc2d4af0e74fab7450e5a4157486
```

The exact page result is machine-checked by:

```bash
python3 scripts/build_aamas2027.py \
  --build-dir build/paper_framework_20261005_final \
  --main-only --require-content-pages 8
```

The build reports resolved citations, zero overfull boxes, unchanged official template files,
and `body=8; references_start=9`.

## What was added to the paper

1. An executable selector contract with timestamp-separated profile snapshot, post-snapshot
   evidence delta, delayed selected-only residual update, read-cut/state-digest provenance, and
   explicit legal update events.
2. A state-contract table that maps each state field to its source and update boundary.
3. A result-filling contract describing qualification, raw execution, analysis, and paper
   integration checkpoints. Missing, incomplete, or `UNKNOWN` cells remain `TBD`; they are not
   converted into zeros or inferred successes.
4. An explicit Results and Evidence Boundary section with RQ1--RQ4 result placeholders and
   interpretation rules for information-only, safety-only, trade-off, null, and qualified
   positive outcomes.
5. An artifact/replay paragraph tying code, roots, prompts, scorer versions, raw ledgers,
   costs, and read-cut replay to the reproducibility claim.
6. The existing experiment matrix and headline table remain empty and are now accompanied by
   method-state and result-entry contracts.

## Evidence boundary

The manuscript remains an internal pre-results draft. The existing real API traces qualify
engineering and attribution boundaries only; they do not support role specialization, future
quality improvement, or real-time-training claims. The candidate fusion implementation remains
subject to the active method and benchmark gates, including temporal/family-held-out evaluation,
component isolation, responsibility-safe labels, and strong same-information baselines.

## Goal reconciliation

This task advances the paper-writing and experiment-design portion of the Goal: the story,
method interfaces, benchmark/baseline matrix, result placeholders, and exact AAMAS page budget
are now represented in one buildable source. It does **not** complete the Goal's scientific
requirements for benchmark qualification, final backbone/update selection, real efficacy,
real-time service, stability, forgetting, or AAMAS submission readiness. Those remain open
tasks and were not downgraded because the paper was made runnable.
