# 0015 — Select before execution and bind later assignment

Status: Accepted. Date: 2026-09-26.

## Context

The first TeamBench vertical slice generated artifacts for every peer before
choosing one, logged a later assignment after feedback, and then selected the
next peer independently. This implemented post-hoc artifact filtering rather
than the intended question: whether past recipient feedback improves a future
pre-execution delegation decision.

The protocol also required a later assignment to name the producer cited by
the evidence. That prevented negative feedback from moving responsibility to a
different peer. Consumer actions were recorded but the grader still evaluated
the original delivery, so `repair` and `independent_redo` did not affect the
terminal artifact.

## Decision

Use pre-execution peer selection as the primary task semantics:

1. At task index `t`, the selector observes only the current task, eligible
   peers, and feedback that has already arrived.
2. It selects one peer and records the actual decision propensity before the
   task starts.
3. Only the selected peer executes and produces the delivered artifact.
4. The recipient seals a judgment, then performs an actual `use`, `repair`, or
   `independent_redo` action.
5. The terminal grader evaluates the artifact produced by that consumer action.
6. Arrived evidence may assign any eligible peer to a later task. The later
   selection must consume that assignment and preserve its decision
   propensity.

Cached artifacts may be used only in a separately named offline artifact
selection study with hidden alternatives and honest generation costs. They are
not evidence for pre-execution peer delegation.

## Rationale

The research claim concerns future responsibility. It is therefore necessary
that feedback change a decision made before later work begins. Binding the
assignment to the next selection makes that causal arrow executable. Allowing
the assignment to choose a different peer lets both positive and negative
evidence affect responsibility. Grading the consumer output makes adoption and
rework observable consequences rather than log labels.

## Consequences

- The protocol fixture can validate ordering, lineage, propensity, and
  exactly-once constraints, but it cannot establish learning efficacy.
- The primary experiment must compare future pre-execution delegation under
  matched information, exploration, task opportunities, and cost.
- Recipient judgment remains distinct from terminal reward; both are logged.
- ADR 0008 is not superseded by this decision. The final benchmark remains
  open and requires a separate benchmark decision.
- The corrected zero-LLM evidence is stored under
  `experiments/logs/peerrolebench_tb_vertical_20260926_causal_v2/` and remains
  marked `scientific_claim_allowed=false`.
