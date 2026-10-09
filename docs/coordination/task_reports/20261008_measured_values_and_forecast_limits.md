# Task report — measured values and limits of extrapolation

Date: 2026-10-08  
Status: exact diagnostic data extracted; main result cells remain unmeasured.  
Goal change requested: false.

## Purpose

Assess the request to fill every figure/table from existing observations and
guess unknown values while preserving a favorable result. Extract everything
directly supported by a real run, and establish which quantities can actually
be inferred. This is a data extraction task, with no new experiment or API call.

## Exact observations

Source: `experiments/logs/n03_c1_parent_source_live_20261006_v1/summary.json`.
The following are **single-root development diagnostics**, under the original
v2 scorers. Check fractions are counts of checks, not accuracy across tasks.
The target decisions preceded these updates; no future task was executed after
the updates. Rows share source material and do not constitute independent trials.

| Policy | Producer checks | Recipient checks | Adoption checks | Updates | One-event update time (ms) |
|---|---:|---:|---:|---:|---:|
| No update | 2/3 | 3/3 | 1/2 | 0 | N/A |
| Contextual trust linear | 2/3 | 3/3 | 1/2 | 1 | 0.520 |
| RARE | 2/3 | 3/3 | 1/2 | 1 | 0.297 |

All three target selections were `peer-b@v1`. Even the later previews selected
the same `peer-c@v1` across all three policies. Probability changes alone cannot
establish a change in assignment or its benefit. The source completed eight
real API calls; these are not eight independent task streams.

The exact values are preserved in
`artifacts/analysis/aamas2027/development_observations_20261008_v1/observations.csv`.
Its `provenance.json` contains the raw summary SHA-256, derivation, scope,
scorer versions, and explicit ineligibility for paper method-effect claims.

## Why unknown effects cannot be estimated from these data

There is no executed post-update outcome, held-out prediction population,
multi-event timing distribution, or matched drift stream. Thus future utility,
generalization, Brier/calibration, p95, forgetting, recovery, and ablation
effects are not identified by this run. Choosing favorable values would impose
an unsupported assumption about the very effects the paper must test. A forecast
would need a declared statistical model, supporting observations, validation,
and uncertainty; the current evidence cannot supply those requirements.

No guessed values have been inserted into the paper or scientific result grids.
The measured diagnostics above can support debugging or a clearly scoped
supplement, while the existing
[fill-eligibility audit](20261008_result_table_fill_eligibility.md) remains in
force. Improving actual effect requires qualified, matched future-task
experiments and method revision based on their outcomes.

## Goal reconciliation

ER-G3/ER-G4 remain open for independent roots, complete baselines, future
assignment effect, online stability, and uncertainty. Exact extraction improves
traceability without lowering the Goal. New API calls: 0; GPU jobs: 0; empirical
benchmark executions: 0. Historical source files are preserved.
