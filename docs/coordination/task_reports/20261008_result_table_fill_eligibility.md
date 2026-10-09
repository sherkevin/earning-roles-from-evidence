# Task report — eligibility of measured values for body result tables

Date: 2026-10-08  
Status: evidence audit complete; no body result cell qualified.  
Goal change requested: false.

## Purpose and decision

Answer whether the current real runs can fill the three numerical tables in
`article/aamas2027/experiment_tables_body.tex`. The answer is **no** for the
tables as labelled. Their 123 empirical cells are still unfilled: 48 in
ArtifactRole main results, 35 in PeerSelect, and 40 in mechanism/responsibility
ablations. Thirteen of those cells are independent-stream counts, which cannot
be inferred from API request counts, reruns of one root, or fixture cases. This
audit neither changes the Goal nor alters historical results or table cells.

| Table | Closest observed evidence | Missing for the stated estimand |
|---|---|---|
| 1: prediction and future allocation | One PIPE3 parent-source development run completed eight real API requests. All three target arms chose the same peer; two policies each updated once. Another bounded three-arm run made ten real requests, with one arm stopped at the ownership gate. | Independent producer/later-use labels for held-out prediction; a qualified confirmation root; complete same-information baseline parity; a **post-update assignment actually executed** and its independent quality/cost outcome; independent stream intervals. The published adapter remains unqualified. |
| 2: PeerSelect service and adaptation | The upstream graph-IPD CPU smoke used four agents and 200 steps in each of two repeats; its selector mean reward was 14.15. The PIPE3 run measured one update per updating policy. | A shared PeerSelect stream and budget for RARE and all listed controls, plus repeated update timing for p95, backlog, state, payoff, forgetting, and drift recovery. A PIPE3 single-update latency is not a PeerSelect p95. |
| 3: ablations and responsibility stress | Eight zero-call constructed ownership cases and 30/30 PIPE2 authored controls qualified engineering boundaries; the PIPE3 live run exposes judgment/outcome disagreement. | Paired real streams for each ablation, independent attribution truth and denominators in each responsibility category, a no-gate control, future utility and complete cost. Fixture pass counts are not false-attribution rates. |

## Real measurements that can be reported as diagnostics

The parent-source PIPE3 run's eight API calls all completed. It recorded 9,658
input and 4,857 output tokens, one structural root and seed, and three arms. All
target choices were `peer-b@v1`; the producer scorer returned `FAIL` for the same
serialization check in each arm. The `contextual_trust_linear` and RARE updates
took **0.520 ms** and **0.297 ms**, respectively, each from **one update**.
Post-update choices were previews only. The recipient accepted the artifact
while the independent producer/adoption scorer failed under that run's scorer
version. These are reproducible development observations, not estimates of
method advantage, p95 latency, or future assignment benefit. See the
[run report](20261006_parent_source_live_smoke.md) and
[raw summary](../../../experiments/logs/n03_c1_parent_source_live_20261006_v1/summary.json).

The [bounded C1 run](../../../experiments/logs/n03_c1_pipe3_bounded_live_20261006_v4/summary.json)
made ten real requests but did not complete a comparable three-arm target
outcome. The [graph-IPD smoke](../../../experiments/logs/benchmark_selection_20260925/graph_ipd_smoke_ps_metrics.json)
measures the upstream reference alone. Earlier N02 consumer 4/4 checks did not
measure producer correctness or a changed future assignment. Regrading one
artifact or rerunning seed variants does not increase the independent-root or
stream count. Failures and UNKNOWN outcomes remain in their original logs.

## Goal comparison and next data item

This leaves ER-G3's qualified independent task roots and complete baseline
comparison open, and ER-G4's prediction, future-assignment, online stability,
and reproducible method-effect requirements unfulfilled. The nine-cell
[execution manifest](../../paper/aamas2027/EXPERIMENT_MATRIX_EXECUTION_MANIFEST_20261008.md)
is still a plan, not nine completed results. The active benchmark plan and the
newer candidate parity card also disagree on the development/confirmation root
allocation; neither yields a qualified second root. The Goal standards are
unchanged.

The next result worth producing is a frozen, responsibility-qualified
ArtifactRole stream on a structurally independent root, with matched
same-information controls, an actual **future** assignment, independent
producer/later-use outcomes, and complete per-arm cost. Only then can the
first Table 1 utility/assignment contrast be considered for entry. A separate
matched PeerSelect stream is needed for Table 2; neither track substitutes for
the other. This audit used existing artifacts only: **0 new API calls, 0 GPU
jobs, 0 benchmark executions**.
