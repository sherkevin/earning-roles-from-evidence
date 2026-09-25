# 0013 — Freeze the minimal symbol boundary for online selection

Status: Accepted working model. Date: 2026-09-25.

## Context

The earlier formulation represented one event as a tuple containing time, context,
candidate set, action, propensity, history, output, value, delay and label. That tuple
mixed raw observations, derived quantities, audit fields and optional hidden state. It
made the dependency structure unclear and gave no concrete instance for the symbols.

The research task is to design and test a real-time peer/tool selector with delayed,
selected-only feedback. The notation must be small enough to implement and every
primitive must have a real data case.

## Decision

Use the following as the base selector/tool mathematical definition:

$$
(x_t,C_t,a_t,o_t,y_t,\delta_t,s_t).
$$

- `x_t` is the visible task context, including any history already visible at decision
  time.
- `C_t` is the executable candidate set; identity and version live inside each candidate.
- `a_t` is the selected candidate.
- `o_t` is the immediate execution output, when the task exposes one.
- `y_t` is the delayed quality label for the selected candidate.
- `delta_t` is label availability delay.
- `s_t` is writable learner state, not a second environment input.

The dependency chain is:

$$
(x_t,C_t,s_t)\to a_t\to o_t\to y_t\to B_k\to s_{k+1}.
$$

Policy, representation and updater are functions (`pi`, `phi`, `U`), not extra primitive
inputs. Propensity is recorded only when needed for offline evaluation. Candidate versions,
event IDs and arrival sets are embedded or derived logging structures.

For the actual AAMAS claim about learning roles from another agent's judgment, the
minimal research object adds the real judge identity:

$$
(x_t,C_t,a_t,o_t,j_t,y_t,\delta_t,s_t).
$$

Here `j_t` is the consumer/peer who reads and uses the delivery. It cannot be hidden
inside an evaluator function because judge identity and judge bias are part of the
claim. The tool benchmark is a special case with `j_t` fixed to the environment
evaluator. The hidden-state controlled-process extension is added only if an experiment
shows that action changes the future task distribution in a way visible context cannot
explain.

## Rationale

This boundary is sufficient to express selection, immediate output, selected-only delayed
feedback, peer judgment, real-time update cost, and old-task retention. It also lets the
peer and tool projects share the event/update infrastructure without claiming that their
terminal objectives or feedback scopes are identical.

It avoids inventing a `Z_t`, belief, graph state or separate version variable before such
a concept is identifiable from data. The full controlled-process document remains an
extension for the evidence-triggered case.

## Consequences

The canonical notation and worked cases live in
[`minimal_online_selection_model_20260925.md`](../../research/minimal_online_selection_model_20260925.md)
and [`minimal_peer_judged_role_model_20260925.md`](../../research/minimal_peer_judged_role_model_20260925.md).
Any proposed new primitive must include (1) the observable data source, (2) a concrete
instantiation, and (3) an experiment showing that the existing chain cannot represent it.
The prior controlled-process symbols may be used only in the extension section and must
not silently re-enter the base equations.
