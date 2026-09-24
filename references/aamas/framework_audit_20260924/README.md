# Streaming training framework audit (2026-09-24)

This is a source audit for the shared peer/tool JEV runtime. It does not claim
that either upstream framework can train our method unchanged.

## Pinned sources

- RLinf: `RLinf/RLinf`, commit `880477d4d4ef4488faf908a2a5bff6e81f607acd8`
- ROLL: `alibaba/ROLL`, commit `192b1a01ea61c113b2deb543f7b115783038dff8`

The original shallow checkouts were used for inspection and are not part of the
repository payload. Relevant source snapshots are under `snapshots/`.

## Findings

RLinf exposes reusable infrastructure for this problem: Ray workers, async
`Channel` queues with keyed routing and batching, checkpointable workers, and a
disk-backed `TrajectoryReplayBuffer` with asynchronous writes and windowed
sampling. Its replay schema is trajectory-oriented (`[T, B, ...]`) and its
algorithms/environments target embodied/agentic RL, so we should wrap our
event-level `DecisionEvent` into a thin adapter rather than force our labels
into an actor trajectory abstraction.

ROLL provides mature Ray multi-role scheduling, agentic rollout, replay and
asynchronous training primitives. Its default data path is token/rollout
centric and its model strategies assume generative LLM training. It is useful
for a later multi-worker deployment or if the surrounding Agent already runs in
ROLL; it is unnecessarily heavy for the first 322M encoder plus small-state
experiment.

## Framework decision for the first vertical slice

Use ordinary PyTorch for the selector model and a small Ray process boundary for
`Actor -> FeedbackQueue -> Learner -> SnapshotStore`. Reuse RLinf's channel and
replay design ideas through a local adapter first. Do not make RLinf or ROLL a
scientific dependency before the update protocol passes local contract tests.

After the protocol is stable, integrate the same `DecisionEvent` and
`StateSnapshot` contracts with RLinf Channel/replay for A800 throughput tests.
Use ROLL only when the companion Agent runtime needs its existing multi-role
agentic pipeline. This keeps framework code reusable while preventing an RL
LLM stack from dictating the JEV algorithm.
