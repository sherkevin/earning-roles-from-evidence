# Peer-role protocol causality audit

> Date: 2026-09-25
> Scope: `references/aamas/peer_role_protocol_20260925.py`, its tests, and `peerrolebench_tb_gate_manifest_20260925.json`.
> This is a contract audit. Passing the existing protocol tests is not evidence that role learning improves task outcomes.

## Findings

### 0. The initial assignment event is missing

The gate manifest requires `assignment → artifact → judgment → terminal grade → ledger update → next assignment`, but the ledger only models `LaterAssignment`, which is recorded after evidence. There is no initial routing/selection event that links a selector decision to the producer delivery. The adapter must represent both boundaries; otherwise the required order is not executable or auditable.

### 1. Selection and selected-only attribution are not represented

`Delivery` has a producer but no selection event, candidate set, propensity, assignment id, or agent version. A delivery can therefore be inserted without proving that the selector chose that producer. The ledger also has no notion of unselected candidates, so it cannot enforce selected-only feedback.

The adapter must record a selection event first, bind the delivery to it, and verify that `delivery.producer_id` is the chosen eligible candidate. The updater must receive only the chosen peer's feedback; candidate probabilities and versions must be logged for replay and IPS/DR analysis.

### 2. Judgment is separated from terminal truth, but visibility is not auditable

The public call order makes it difficult to record an outcome before judgment because action requires judgment and outcome requires action. However, `terminal_outcome_available=False` is supplied by the caller, not derived from an observation boundary. The protocol does not record which fields were visible to the recipient or selector.

The adapter must seal the judgment before running the terminal grader and log a visibility manifest. Hidden tests, expected score, and terminal output must not be in the judgment or selector observation. The terminal score must be independently retained for calibration/effect analysis and must never be used to rewrite the judgment.

### 3. Judgment/action inconsistency is silently accepted

`record_action` checks identity and artifact digest but does not compare the action with the judgment. For example, `reject_redo` followed by `use` is accepted. This may be a valid human behavior, but it must be explicit: either enforce a documented decision-to-action mapping or log a mismatch as its own observable event and analyze it. `used_artifact=True` is currently a self-report, not proof of workspace adoption; adoption must be backed by artifact/state lineage. A repair action should carry the repaired artifact hash (or an explicit no-output reason).

### 4. Evidence can arrive before terminal outcome

`record_evidence_update` permits `outcome_id=None`, while the gate manifest declares terminal grading before ledger update. The main delayed-feedback condition must reject a role update until the terminal outcome has arrived. If a judgment-only update is desired, it must be a separately named baseline and cannot be called terminal-feedback learning.

### 5. Later assignment can be retroactive or weakly attributed

`record_assignment` checks only that evidence ids exist and that its `task_index` is greater than the cited delivery index. It does not prove that the assignment happened before execution of the next task, that the task id is a new root, or that the assigned agent is the subject of the cited evidence. Add an explicit task-start/assignment boundary and a subject-agent field or enforce producer linkage. An assignment made after the next delivery must be rejected.

### 6. Exactly-once episode semantics are missing

Different ids allow multiple judgments, actions, outcomes, and updates for one delivery. `ConsumerAction` also carries no `judgment_id`, so an action cannot be attributed to one of several judgments. Contradictory labels can therefore enter the role history. Either enforce one sealed judgment, one recipient action, one terminal outcome, and versioned evidence updates per delivery, or make supersession and the judgment/action link explicit and auditable.

### 7. Objective score and cost lineage are underspecified

`TerminalOutcome` stores only a boolean and scorer version. For TeamBench the adapter must retain raw partial score, grader run id, artifact/state diff, test output hash, and measured API/tool cost separately from the recipient label. Otherwise a terminal success cannot support calibration or causal attribution.

## Minimum adapter tests

1. A delivery whose producer was not the chosen candidate is rejected; unselected peers produce no updater event.
2. Judgment is recorded before the terminal grader; selector input excludes terminal fields, and a tampered visibility manifest fails.
3. A judgment/action mismatch follows an explicit policy and is not silently treated as agreement.
4. Main role update before terminal outcome is rejected; a judgment-only baseline is separately named.
5. Duplicate judgment/action/outcome for one delivery is rejected (or supersession is explicit and auditable).
6. Assignment after the next task starts is rejected; assignment before next task start cites evidence for the assigned subject.
7. Claimed adoption/repair is checked against the actual artifact or workspace state hash.
8. Tests are reported as protocol/contract sanity only; no score or learning claim follows from them.
