# 0014 — Treat the linear associative recurrence as a validated kernel, not the final method

Status: provisional experimental gate, 2026-09-25.

## Context

We wanted to test whether a linear-attention-style state could provide a
constant-size, immediately updated JEV-like selector state under delayed
selected-only feedback. The recurrence was derived from the usual associative
linear-attention rewrite and implemented as decayed sufficient statistics
`S` and `Z`.

## Evidence

The bounded run used the same synthetic hidden-regime stream for every method,
five paired seeds, 100 decisions per seed, four candidates per menu, and delays
uniformly sampled from 1 to 8. Learners received only the selected candidate's
label when it arrived. The complete configuration, raw JSONL trace, results,
and summary are in
`references/aamas/streamjev_20260924/experiments/logs/linear_associative_smoke_20260925_*`.

The associative method achieved mean expected reward 0.418725 versus 0.418252
for the uniform control, a paired gain of only 0.000474 (SD 0.000718). The
existing OnlineRLSHead reached 0.425695, a paired gain of 0.007444 (SD
0.011270). The associative update was faster in this local Python probe
(update p95 23.964 microseconds versus 78.752 for RLS), but its post-switch
reward was identical to the uniform control (0.526378).

Five out of five seeds matched an explicit exponentially weighted closed-form
sum and passed the same-arrival-batch reverse-order check to floating-point
precision. These checks validate the implementation and its batching rule;
they do not validate predictive quality.

## Decision

Keep the recurrence as a mathematical and systems baseline. Do not present it
as the final backbone, a complete real-time training contribution, or evidence
of improved selection quality.

## Consequences

The next method must address the observed weakness: the non-negative split
feature map and coordinatewise kernel average do not represent the signed,
context-dependent reward structure in this world. Any proposed extension must
beat both the uniform control and OnlineRLSHead on a predeclared real or
benchmark trace while retaining the measured update-cost advantage. The current
smoke is a gate against advancing the bare algebra by analogy alone.
