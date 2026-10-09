# Task report — standalone experiment-matrix LaTeX blueprint

Date: 2026-10-08  
Status: presentation complete; numerical confirmation results remain pending.

## Purpose and acceptance target

Produce a reviewable LaTeX document in the official AAMAS table style, with a
one-to-one mapping from RQ1–RQ4 to the planned paper result tables. The document
must expose the method rows, comparison boundary, metric direction, and future
numeric cells without inventing results. It must compile, be visually checked,
and be opened for the user.

## Delivered table set

Source: `article/aamas2027/experiment_matrices.tex`.

1. Table 1 — four-row experiment map: RQ, track/unit, contrast, result-table
   destination, and estimand.
2. Table 2 — primary ArtifactRole result: seven policy rows and grouped RQ1/RQ2,
   complete-cost, and stream-count columns.
3. Table 3 — online service and stability: PeerSelect controls and responsibility
   mutations, with latency, backlog, state size, attribution, UNKNOWN, and
   forgetting/recovery endpoints.
4. Table 4 — mechanism and responsibility ablations: evidence/update factors and
   ownership, selected-only, correction/replay interventions.

Every empirical cell is a dash. A dash means unfilled, not zero or a prediction.
The existing nine-cell execution manifest remains the source of task roots,
seeds, budgets, scorer versions, stop rules, and raw evidence requirements. This
table layout does not freeze a new method, benchmark, baseline, or result.

## Build and inspection

The built-in standalone compiler could not find the local official `aamas.cls`;
that attempt failed and is not represented as a successful build. The existing
project `latexmk` toolchain then compiled the document with the official local
class. Initial abstract/package and width failures were corrected; prior build
directories and logs are retained.

Final output:
`artifacts/aamas2027/experiment_matrices_20261008_v3/experiment_matrices.pdf`.

- 3 pages; all pages rendered at 160 dpi and inspected.
- 0 overfull boxes, 0 unresolved references, 0 unresolved citations.
- Known official-class incomplete-ifx and balance warnings remain, plus five
  underfull paragraphs; no truncated table content was seen.
- PDF SHA-256:
  `84ec43aa770787aea1d0c8cd5fcc799dc1b1e9584d55397b1f9cf984d289f316`.
- Source, compile log, and verification are retained with the versioned PDF.

No API, GPU job, benchmark execution, or empirical result was produced. The
canonical `artifacts/aamas2027/main.pdf` was not promoted or rewritten by this
task.

## Comparison against Goal

Closed: result-table presentation is now concrete and reviewable; the RQ-to-table
mapping and policy/metric placeholders can be judged before costly experiments.

Still open: qualified independent roots, complete matched-information baseline
execution, live assignment effects, full cost, uncertainty estimates, and
scientific submission gate. Better table layout is not experimental evidence and
does not lower any Goal standard.

## Reusable outcome and next step

The three numeric table environments can be moved into the paper after the user
reviews the layout, then populated only from the matching frozen confirmation
cards. Keep the detailed execution manifest outside the hero result table so
measured comparisons remain readable.
