# Task report: expected experiment table v2

Date: 2026-10-09
Status: complete as the active planning artifact; scientific closure remains open.

## Why v2 supersedes v1

An independent read-only review found that v1 was algebraically coherent but
could be misread as a universal forecast. It also placed owner-attribution
numbers on PeerSelect rows, conflated coverage with UNKNOWN handling, and did
not make the missing strong same-information baselines explicit.

## Corrections

- v2 labels every numeric cell as an **R1 informative typed-evidence scenario**;
  R2--R8 may tie, lose, or remain unknown and cannot inherit these values.
- PeerSelect false attribution and owner-truth recall are `N/A` in the JSON and
  PDF semantics. UNKNOWN/abstention rate is separate from coverage in JSON.
- The service timing boundary is the full selected-feedback path; the no-update
  row is a no-op update path. Service values are planning targets, not an
  extrapolation from the earlier one-event core timing.
- The archived core rows and columns remain one-to-one with the source PDF. A
  guard paragraph records task-conditioned ridge, matched composition, and the
  closest published adapter as mandatory NO-GO comparisons rather than silently
  treating contextual trust as the strongest baseline.
- The cost sensitivity is explicit: RARE versus contextual trust breaks even at
  approximately `lambda=0.2167`. The displayed `lambda=0.10` is a frozen
  scenario choice, not a universal superiority claim.

## Receipts

- Source: `article/aamas2027/expected_experiment_matrix_v2_20261009/expected_experiment_matrix.tex`
- Values: `docs/paper/aamas2027/expected_experiment_matrix_v2_20261009/expected_results.json`
- README: `docs/paper/aamas2027/expected_experiment_matrix_v2_20261009/README.md`
- Build/validation logs: `experiments/logs/expected_experiment_matrix_v2_20261009/`
- Canonical PDF: `artifacts/aamas2027/expected_experiment_matrix.pdf`

The table remains a guide only. No API call, GPU job, benchmark run, or
scientific result was created by this task.
