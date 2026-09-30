# Task report — PIPE3 isolated live-trace qualification (2026-09-30)

## Purpose

Check the smallest remaining execution seam without calling an external API:
the pinned PIPE3 scorer/action/outcome path should expose only public summaries,
an isolated policy reader should run before the later selection, and a closed
responsibility gate must leave the policy unchanged.

## Qualification

The accepted receipt is
`experiments/logs/n03_pipe3_isolated_live_trace_qualification_20260930_v3/`.
It runs the pinned v2 CPU scorer workers and action validator, records six
public trace events
`actor_output → scorer_before → action → scorer_after → outcome → policy_read`,
then seals a task-1 selection on the same canonical PIPE3 boundary. The trace
contains digests, paths, scores and worker metadata, never private source or
hidden assertions. The separate-process profile reader passes, the
responsibility gate remains `policy_update_allowed=false`, and the source-bound
selection leaves `policy.updates=0`. Native and auxiliary manifests validate.

The run is `QUALIFIED_OFFLINE`, with 0 external API calls, 0 GPU jobs, and
`scientific_claim_allowed=false`. The earlier v2 directory is retained as an
incomplete attempt; no historical output was rewritten.

## Exact limitation

The isolated reader currently consumes a sealed Meta-Team-style public profile
offer while the source-bound feedback is represented by a separate offer. The
trace proves ordering and public-process handling, but not that the isolated
reader consumed the exact source-bound feedback bundle. The next runner gate
must bind those two objects (or replace them with one typed public offer) and
then execute the same actor/scorer/action/outcome sequence in a versioned live
runner. This qualification therefore does not unlock a benchmark, baseline
comparison, online-learning claim, independent-history result, or A800 run.
