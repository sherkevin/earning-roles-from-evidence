# Task report — correcting planning tables into body result tables

Date: 2026-10-08  
Status: v6 layout compiled and reviewed; experimental qualification remains open.

## Purpose

Address the user's concrete finding that the standalone matrix looks like a text
document rather than the result tables in the reference papers. The target is a
compact, numerical table skeleton whose rows, columns, and panels directly serve
the paper's claims. This is a presentation task; it does not change the Goal,
method, active benchmark plan, baseline qualification, or execution budget.

## What went wrong

The old Table 1 routes RQs to tracks, contrasts, estimands, and result tables. It
is an internal experiment index, not a results matrix. Putting it before the
numeric placeholders made the review document carry the wrong visual hierarchy.
The other tables also carried long explanatory columns and captions, repeated
track names, and policy and mutation rows in one grid. A row described an
execution intention rather than exposing a comparison.

Empty cells explain the absence of numbers; they do not excuse excessive prose.
The previous report's 0-overfull result established compilation and legibility,
not conformity to a strong-paper result presentation.

## References inspected

The existing CollabLLM page 6 and MultiAgentBench page 7 renders were viewed
again. The former groups three task datasets with three short metrics; the
latter groups six scenarios with two metrics. Both make the comparison axes and
numeric payload legible, without placing policy-contract sentences in result
cells. They are local comparison samples, not a universal mandatory template or
evidence that every paper in this set received a best-paper award. Original PDF
paths and hashes remain in the 20261008 experiment-matrix audit config.

## Revision and correspondence

The old v3 planning preview is retained. v4/v5 are intermediate result-layout
candidates; v6 is the compact review candidate in
`article/aamas2027/experiment_tables_body.tex`.

| New body table | Paper claim / cards | Execution cells | Result grid |
|---|---|---|---|
| 1: ArtifactRole main results | RQ1/RQ2, H1/H2 | RQ1-I/II, RQ2-I/II/III | Methods × Brier/calibration, future utility, assignment change, cost, streams |
| 2: PeerSelect service and adaptation | RQ3/RQ4, H3 | RQ3-I/II | Selectors × update p95, backlog, state size, payoff, forgetting, recovery, streams |
| 3(a): mechanism ablations | RQ2/RQ4 | RQ4-II | Variants × utility, assignment change, false attribution, cost |
| 3(b): responsibility stress | RQ4, H4 | RQ4-I | Full method / no gate × recipient-owned, mixed, unobserved, resource-failure attribution rates |

- The RQ routing overview leaves this body preview; the existing execution
  manifest preserves it and the nine-cell plan.
- Long component explanations and repeated track cells leave the numeric grid.
- Table captions describe comparisons briefly; gates and execution details stay
  in the manifest and task report.
- Table 2 restores backlog (part of H3) and distinguishes forgetting from drift
  recovery; these were missing or collapsed in earlier layout candidates.
- Table 1 keeps the unqualified Meta-Team L2-public adapter visible, marked with
  a dagger. Its placeholder row is not an executed published baseline.
- PeerSelect uses the track-specific reference/history controls already in the
  active plan; its results are not merged with ArtifactRole's labels.
- Secondary loss, calibration, regret, adoption, rework, p50, backlog distributions,
  UNKNOWN/no-op, replay and cost breakdowns remain required by the active plan.
  Display selection does not remove an endpoint or authorize a new experiment.

The preview uses AAMAS's official local class, font, and full-width table area.
It is a single-column review sheet for full-width table environments, not a
replacement submission layout. The large title, abstract, RQ text, and submission
boilerplate no longer occupy a separate page before the grids.

## Boundary against the Goal

ER-G3/ER-G4 still require qualified independent roots, strong same-information
and published comparisons, real streams, complete costs, uncertainty, and future
assignment outcomes. A grouped task table is useful only when those groups are
real; this candidate cannot manufacture benchmark breadth by duplicating seeds
or presenting ArtifactRole and PeerSelect as interchangeable tasks. The active
root split remains unmodified. The final manuscript must show per-root
confirmation evidence once those populations and cards are qualified.

The main PDF has not been promoted by this task. No API, GPU, or empirical
benchmark run is part of this revision. Every dash means unfilled, not a result.

## Verification

Final output:
`artifacts/aamas2027/experiment_tables_body_20261008_v6/experiment_tables_body.pdf`.

- 2 pages; both rendered at 150 dpi and inspected. Tables 1/2 are on page 1;
  Table 3 is on page 2. No clipped cells or overlapping labels were observed.
- 0 overfull boxes, 0 undefined references, 0 undefined citations.
- Known official-class incomplete-ifx and spacing advisories remain; compilation
  exits with code 0. The built-in compiler failed to load `aamas.cls`; the
  existing official local latexmk toolchain is the verified fallback.
- PDF SHA-256:
  `2b1cd3f5a6a2a71c075dc6058beb440c441c29a2cdccffaad303d0c34ce4e56e`.
- Config, build receipt, compile log, source snapshot, and diagnostics are saved
  under the version directory and
  `experiments/logs/experiment_tables_body_revision_20261008/`.

The canonical main PDF changed during this task: its master record now points
to `balanced_body_20261008_v2`. This task did not promote a master or edit
`main.tex`; the new parent-level master was left intact. Consequently, the v6
receipt honestly records that the observed master hash differs from the
pre-task hash, rather than asserting global byte-level non-change.

The one-page intent in the initial source comment was not achieved: the official
float/layout rules produce two review pages. The document does not claim a
one-page build or submission-format compliance; the full-width table fonts and
headers are the objects of this review.

## Reusable outcome

The three result-table environments are reusable for the paper, while the
external manifest retains all detailed experiment contracts. Layout approval and
scientific readiness remain separate checks.
