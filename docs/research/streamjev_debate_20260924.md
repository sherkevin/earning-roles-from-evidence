# Stream-JEV v0: architecture and deployment debate

Date: 2026-09-24  
Status: design proposal under falsification; not a frozen paper method.

This document is the current debate artifact for the peer-selection and
tool-selection projects. The two projects share the event/update/runtime
contract, while their candidate descriptions, labels and evaluators remain
project-specific.

## The decision we need to make

We need a JEV that can select among a changing candidate set, receive feedback
only for the action that was actually executed, handle delayed labels, and
adapt quickly without destroying older competence. A static JEV, a periodic
full-history refit, and a prompt memory do not satisfy this deployment regime.

The three requirements pull in different directions:

- full-model updates can adapt but are too slow and unstable;
- a frozen encoder with a linear posterior is fast and safe but may miss
  context-dependent drift and is weak as the main scientific contribution;
- a learned fast adapter can express drift but needs a safety mechanism and a
  stream-aware training objective.

## Competing proposals

### A. Full end-to-end update after every event

Backpropagate through the complete JEV after every new outcome. This gives the
largest update capacity, but it violates the latency budget, is highly
susceptible to noisy/delayed selected-only labels, and makes rollback and
cross-agent state isolation expensive. It is a stress-test baseline, not the
deployment design.

### B. Frozen encoder plus Bayesian/linear online head

Cache an encoder representation and update a conjugate posterior, RLS head, or
LinUCB/Thompson policy after each label. This is the first correctness and
latency baseline. It is stable and interpretable, but by itself it is a known
online-learning construction and cannot be the full novelty claim.

### C. Stream-JEV with dual fast state and slow consolidation (proposed)

Use a pretrained small encoder for semantic knowledge, a permutation-safe
candidate scorer, and two fast states:

1. a Bayesian/online-Newton state for conservative, low-variance adaptation;
2. a low-rank neural residual state for context-dependent drift.

The output is a gated mixture:

```text
logit(candidate) = base_logit
                  + gate(state, uncertainty, drift) * residual_logit
                  + posterior_logit
```

The gate is small at cold start and grows only with evidence. A bounded update
changes the per-selector state after each observed outcome. A replay learner
periodically trains the residual initialization and, only after a holdout guard,
publishes a new slow checkpoint. The immutable base checkpoint and every
per-selector state are versioned separately.

This is intentionally more conservative than a learned optimizer alone: the
posterior path remains a safe fallback when the neural residual is uncertain.

## Shared model and event contract

Both projects implement the same interfaces:

```text
score(state, typed_decision, candidates)
    -> probabilities, uncertainty, propensity, state_version

record_action(event_id, candidate_id, propensity, output_ref)
submit_feedback(event_id, label, arrived_at, delay, truth_status)
snapshot(selector_id) / restore(snapshot)
```

The event contains no hidden truth and no unselected candidate output. A label
is attached only to the action that was executed. `typed_decision` supports
`select`, `verify`, and `final` so the tool project can reuse the same runtime
for provider selection, evidence verification, and answer/abstain decisions;
the peer project can begin with `select`.

Each selector has isolated state. A shared base encoder may be trained across
projects only after label semantics and calibration are shown compatible; tool
and peer feedback are not silently pooled.

## Training procedure

### Stage 0 — static initialization

Initialize from the 322M Laya multilingual encoder or a same-scale encoder.
Replace its order-sensitive menu head with a candidate-wise encoder and masked
set scorer. Train only the scorer/head on legal offline data. Keep the original
Laya checkpoint as a static baseline.

### Stage 1 — fast-state pretraining

Construct stream episodes from logged events. Each episode specifies candidate
arrival, candidate removal, drift, feedback delay, label noise, and exploration
probabilities. Only selected actions reveal outcomes. Train the posterior prior,
residual initialization and gate using a short unroll.

The objective is post-update performance, not only current classification:

```text
stream_loss = future prequential loss/regret
            + forgetting penalty on replayed old events
            + KL(anchor || adapted prediction)
            + calibration penalty
            + update-cost penalty
```

IPS or doubly robust targets use the logged action propensity. Pending feedback
is kept in a queue and applied when it arrives; it is never converted into a
negative label by timeout.

### Stage 2 — online serving

The serving path performs one cached encoder forward and a small scorer update.
It never backpropagates through the full encoder on the critical path. Recent
events go to a bounded fast buffer; a reservoir buffer protects older regimes.
The learner periodically samples both buffers, updates the residual/head, runs
old-regime and new-regime holdouts, and atomically promotes or rolls back the
checkpoint.

## Why the three requirements can coexist

### Stability

The base encoder is immutable during normal serving. Fast residuals are
low-rank, norm-bounded and anchored to base logits. The reservoir replay and
KL holdout prevent a new regime from overwriting old behavior. A checkpoint is
published only when old-regime loss, calibration and safety constraints pass;
otherwise the system keeps the previous version.

### Timeliness

The posterior state changes on the first valid feedback. A recency-weighted
residual and drift gate respond to repeated evidence from the current regime.
This does not claim to predict an unseen change before any signal exists; the
measurable claim is recovery after the first reliable feedback.

### Speed

Encoder features are cached, and the per-event update touches only a small
posterior/low-rank state. Replay, gradient updates, checkpoint writing and
evaluation run asynchronously. Update latency and forward latency are measured
separately; a fast update cannot hide a slow candidate encoding pass.

## Runtime reuse decision

RLinf supplies the most reusable pieces for the eventual distributed runtime:
keyed asynchronous channels, worker placement, checkpointing and a disk-backed
windowed replay design. Its native replay schema is trajectory-oriented, so we
will wrap `DecisionEvent` rather than change the JEV algorithm to fit it.

ROLL supplies mature Ray multi-role scheduling and asynchronous agentic rollout,
but its default data/model path is generative-LLM-centric. It becomes useful
when the surrounding peer/tool Agent already runs in ROLL; it is not a required
dependency for the first selector experiment.

The first vertical slice uses PyTorch plus a small Ray process boundary. After
the event contract passes, we run the same code through RLinf Channel/replay on
one A800. This limits new code to the scorer, update state, feedback queue and
promotion guard.

## Falsification matrix

The proposed design is rejected or simplified if any of these conditions occur:

1. Stream-JEV does not beat static Laya and ordinary RLS on prequential regret
   after equalizing features, exploration and label access.
2. The residual improves adaptation only by causing a statistically significant
   old-regime regression that replay/anchor cannot control.
3. The online update p95 exceeds the decision interval even with cached
   features, or asynchronous training causes stale-state errors.
4. IPS/DR variance or support violations make the apparent improvement
   disappear on an independently collected exploration slice.
5. The same event contract cannot support both peer and tool typed decisions
   without project-specific leakage or incompatible label semantics.

The first A800 experiment therefore tests the state/update/runtime hypothesis;
it is not allowed to be presented as a paper result until these baselines and
failure checks are complete.
