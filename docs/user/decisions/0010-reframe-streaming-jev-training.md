# 0010 — Reframe the contribution as streaming JEV training

Status: Accepted research direction. Date: 2026-09-24.

## Context

The earlier shared-stack proposal treated AnyJev with a Qwen3-4B backbone as
the implementation mainline. That is useful for reproducing a common selector
interface, but it does not by itself contribute a new training method. AnyJev's
`observe` path accumulates labels and periodically refits a head; Qwen is only
the hidden-state backbone. Neither choice addresses the research question of
how a small decision model can adapt after every new outcome.

The project goal is therefore a trainable JEV-style decision model whose
online state changes at bounded cost under dynamic candidates, selected-only
feedback, delayed labels, drift, and limited replay.

## Decision

1. AnyJev and Qwen3-4B are demoted to baselines, compatibility references, or
   data/serving scaffolds. They are not the paper's claimed contribution.
2. The primary method will be designed as a streaming JEV training framework:
   offline stream/meta-training learns an encoder, candidate scorer, and update
   rule; online execution updates a small trainable fast state after each
   feedback event; asynchronous consolidation handles replay and forgetting.
3. Laya is an open-source candidate initialization and static baseline, not a
   method to adopt unchanged. Its 322M multilingual checkpoint is the default
   small-model candidate, with the 421M English checkpoint as a capacity
   control. This choice remains subject to local reproducibility tests.
4. The method must handle dynamic candidate sets and selected-only delayed
   feedback explicitly. A frozen encoder plus ordinary head retraining or RLS
   is a baseline, not sufficient novelty.

## Rationale

This framing makes the contribution about training for rapid plasticity rather
than about selecting an existing JEV implementation. Laya is useful because it
is a non-autoregressive decision encoder with local weights and typed
probabilities at 322M/421M scale, while its current candidate serialization,
option-order sensitivity, and offline training expose concrete problems for a
new method to solve.

The novelty claim must be narrower than “fast weights” or “test-time learning”
in general. Existing test-time feedback optimizers and continual-learning
methods remain related work and baselines. The differentiating setting is the
combination of JEV candidate decisions, partial selected-action labels,
feedback delay, candidate-set changes, and an objective that trains the model
for post-update prequential performance.

## Consequences

- The old AnyJev/Qwen shared-wrapper tasks remain useful for baseline parity,
  but no result from that wrapper can be reported as the new method.
- Main experiments require local model weights and local training; the
  `内部` idealab API cannot substitute for hidden-state training or parameter
  updates.
- A successful paper must report adaptation sample efficiency, prequential
  regret/reward, update latency, calibration, forgetting, and permutation
  robustness in addition to static accuracy.
- Laya-specific architectural fixes (set scoring, candidate masking, and
  streamable fast state) must be separated from the reusable static baseline
  in ablations.
