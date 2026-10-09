# Execution manifest for the experiment matrix

This file preserves the detailed nine-cell execution skeleton while the main
paper uses a compact four-row overview. It is a planning artifact, not an
observed result. A cell is eligible for confirmation only after its root, split,
policy, seed, budget, scorer, cost contract, stopping rule, and raw event
manifest are frozen.

| Cell | Track/root | Policy or intervention | Primary comparison | Measures |
|---|---|---|---|---|
| RQ1-I | ArtifactRole / development root | raw acceptance vs terminal-only vs RARE | same producer deliveries and recipient observations; legal feedback only | held-out Brier/log loss, calibration, judge reliability |
| RQ1-II | ArtifactRole / confirmation root | contextual-trust-linear vs RARE | same public read cut, delay, propensity, model, and budget | incremental prediction and cross-root transfer |
| RQ2-I | ArtifactRole / confirmation root | no evidence vs public evidence only | preview-to-assignment before target execution | assignment change, future quality, adoption, rework |
| RQ2-II | ArtifactRole / confirmation root | delayed update only vs public evidence plus delayed update | same target tasks and selected-only outcome | future quality–cost utility and complete cost |
| RQ2-III | ArtifactRole / confirmation root | RARE vs pooled controller | same total public capacity and candidate menus | quality–cost utility, concentration, propensity |
| RQ3-I | PeerSelect / development streams | uniform, no-history, history-only, candidate updater | local graph, selected-only payoff, fixed call/token budget | regret/payoff, update p50/p95, state bytes |
| RQ3-II | PeerSelect / drift streams | updater with/without correction and replay | preregistered peer/task drift and delayed feedback | recovery window, forgetting, backlog, replay equality |
| RQ4-I | ArtifactRole / all qualified roots | responsibility mutation matrix | producer-only, recipient-only, mixed, unknown, resource failure | false attribution, UNKNOWN precision, no-op rate |
| RQ4-II | ArtifactRole / all qualified roots | leave-one-mechanism-out | remove gate, public evidence, delay, locality, or updater | main utility, safety, cost, interaction effect |

## Required card fields

Each row must expand to an immutable card containing:

- benchmark/root and development or confirmation split;
- independent stream count, seed list, and reset rule;
- candidate menu, policy version, model/API route, and complete call/token/tool
  budget;
- scorer version, label contract, selected-only denominator, and UNKNOWN rules;
- primary estimand, practical-difference or precision target, interval method,
  multiplicity rule, and stopping rule;
- complete-cost fields, hardware/runtime metadata, and raw JSONL manifest hash.

The main-paper overview does not waive any of these requirements. A missing field
leaves the row planned or UNKNOWN; it never becomes a zero or a predicted value.

