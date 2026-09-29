# Task report — exact same-information four-event counterfactual

- **Date**：2026-09-29
- **Status**：`done / negative candidate qualification`
- **Scope**：zero API, zero GPU; active storyline, method and benchmark versions unchanged

## Question

The minimal debate stream was replayed with an exact same-updater control. The
control shares the candidate's feature vectors, diagonal update rule, window
and pending capacities, correction semantics, probability map, and assignment
schedule. The only changed input is the responsibility gate: the control
accepts the raw label for the recipient-owned event that RARE marks UNKNOWN.

The three events are: a recipient-owned integration error (`e1`), a
producer-owned eligible defect (`e2`), and a delayed correction that supersedes
`e2`. Assignment is evaluated both before and after the correction arrives.

## Result

The test and deterministic probe passed. On the pre-correction assignment,
both policies choose `B` with identical probabilities
`(0.47248103208412756, 0.5275189679158725)`. In the after-assignment schedule,
both choose `A` before the correction is applied. The correction changes both
policy states after the decision, but neither rewrites the sealed assignment.

Therefore `candidate_separates_on_minimal_stream=false`. The earlier apparent
separation was caused by an unfair context-specific control and is not retained
as evidence.

## Interpretation and next gate

This is a useful negative result: the three-event stream does not identify a
responsibility-gate advantage when information and updater mechanics are held
constant. It is not an impossibility result and it does not support efficacy,
novelty, or benchmark claims. The next offline design must add an independently
measured producer-quality consequence and a later unseen-context decision while
keeping all public information and update mechanics equal across arms. No API
or A800 run is justified by this probe.

## Evidence

- Configuration: `experiments/logs/n03_four_event_counterfactual_20260929_v1/config.json`
- Raw output: `experiments/logs/n03_four_event_counterfactual_20260929_v1/raw_output.txt`
- Summary: `experiments/logs/n03_four_event_counterfactual_20260929_v1/summary.json`
- Tests: `tests/test_peerrolebench_four_event_counterfactual.py`
