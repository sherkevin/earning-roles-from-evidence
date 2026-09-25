"""Minimal peer-judged role-formation protocol.

This module is a benchmark adapter contract, not a learner and not a result.
It makes the causal order explicit:

    delivery -> recipient judgment -> recipient action -> terminal outcome
              -> later assignment

The ledger deliberately keeps the recipient judgment separate from the
terminal scorer.  A terminal result cannot be used to manufacture a judgment
that the recipient never recorded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
from typing import Any, Mapping


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
JUDGMENTS = {"accept", "accept_with_rework", "reject_redo", "reject_reroute"}
ACTIONS = {"use", "repair", "reject", "independent_redo"}
DECISION_ACTION = {
    "accept": "use",
    "accept_with_rework": "repair",
    "reject_redo": "independent_redo",
    "reject_reroute": "reject",
}


def _hash_payload(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _artifact_hash(value: str) -> str:
    value = str(value)
    if not SHA256_RE.fullmatch(value):
        raise ValueError("artifact_sha256 must be a lowercase SHA-256 digest")
    return value


@dataclass(frozen=True)
class PeerSelection:
    """The selector decision that makes a delivery attributable.

    ``candidate_ids`` is the complete eligible local neighborhood observed by
    the selector.  Keeping it in the event is necessary for replay and for
    distinguishing exploration from an oracle that saw all agents.
    """

    selection_id: str
    task_id: str
    task_index: int
    selector_id: str
    role: str
    candidate_ids: tuple[str, ...]
    chosen_peer_id: str
    propensity: float

    def __post_init__(self) -> None:
        if not self.selection_id or not self.task_id or not self.selector_id or not self.role:
            raise ValueError("selection identifiers and role are required")
        if int(self.task_index) < 0:
            raise ValueError("task_index must be non-negative")
        if not self.candidate_ids or len(set(self.candidate_ids)) != len(self.candidate_ids):
            raise ValueError("candidate_ids must be non-empty and unique")
        if self.chosen_peer_id not in self.candidate_ids:
            raise ValueError("chosen_peer_id must be an eligible candidate")
        if self.chosen_peer_id == self.selector_id:
            raise ValueError("selector cannot choose itself")
        if not (0.0 < float(self.propensity) <= 1.0):
            raise ValueError("propensity must be in (0, 1]")


@dataclass(frozen=True)
class Delivery:
    delivery_id: str
    task_id: str
    producer_id: str
    recipient_id: str
    artifact_sha256: str
    source_event_id: str
    task_index: int
    selection_id: str | None = None

    def __post_init__(self) -> None:
        if not self.delivery_id or not self.task_id or not self.source_event_id:
            raise ValueError("delivery identifiers are required")
        if not self.producer_id or not self.recipient_id:
            raise ValueError("producer_id and recipient_id are required")
        if self.producer_id == self.recipient_id:
            raise ValueError("producer and recipient must be different agents")
        if int(self.task_index) < 0:
            raise ValueError("task_index must be non-negative")
        _artifact_hash(self.artifact_sha256)


@dataclass(frozen=True)
class RecipientJudgment:
    judgment_id: str
    delivery_id: str
    consumer_id: str
    decision: str
    observed_artifact_sha256: str
    terminal_outcome_available: bool = False
    repair_note: str = ""

    def __post_init__(self) -> None:
        if not self.judgment_id or not self.delivery_id or not self.consumer_id:
            raise ValueError("judgment identifiers are required")
        if self.decision not in JUDGMENTS:
            raise ValueError(f"decision must be one of {sorted(JUDGMENTS)}")
        _artifact_hash(self.observed_artifact_sha256)
        if self.terminal_outcome_available:
            raise ValueError("recipient judgment must be sealed before terminal outcome")


@dataclass(frozen=True)
class ConsumerAction:
    action_id: str
    delivery_id: str
    consumer_id: str
    used_artifact: bool
    input_artifact_sha256: str
    output_artifact_sha256: str | None = None
    repair_cost: float = 0.0
    action: str = "use"

    def __post_init__(self) -> None:
        if not self.action_id or not self.delivery_id or not self.consumer_id:
            raise ValueError("action identifiers are required")
        if self.action not in ACTIONS:
            raise ValueError(f"action must be one of {sorted(ACTIONS)}")
        _artifact_hash(self.input_artifact_sha256)
        if self.output_artifact_sha256 is not None:
            _artifact_hash(self.output_artifact_sha256)
        if float(self.repair_cost) < 0:
            raise ValueError("repair_cost must be non-negative")
        if self.action in {"use", "repair"} and not self.used_artifact:
            raise ValueError("use/repair actions must mark used_artifact=true")
        if self.action in {"reject", "independent_redo"} and self.used_artifact:
            raise ValueError("reject/independent_redo actions cannot mark artifact as used")


@dataclass(frozen=True)
class TerminalOutcome:
    outcome_id: str
    delivery_id: str
    success: bool
    scorer_version: str
    partial_score: float | None = None
    score_payload_sha256: str | None = None

    def __post_init__(self) -> None:
        if not self.outcome_id or not self.delivery_id or not self.scorer_version:
            raise ValueError("terminal outcome identifiers and scorer_version are required")
        if self.partial_score is not None and not 0.0 <= float(self.partial_score) <= 1.0:
            raise ValueError("partial_score must be in [0, 1]")
        if self.score_payload_sha256 is not None:
            _artifact_hash(self.score_payload_sha256)


@dataclass(frozen=True)
class RoleEvidenceUpdate:
    evidence_id: str
    judgment_id: str
    action_id: str
    outcome_id: str | None
    update_version: str
    arrived_at: float

    def __post_init__(self) -> None:
        if not self.evidence_id or not self.judgment_id or not self.action_id:
            raise ValueError("evidence identifiers are required")
        if not self.update_version or float(self.arrived_at) < 0:
            raise ValueError("update_version and non-negative arrived_at are required")


@dataclass(frozen=True)
class LaterAssignment:
    assignment_id: str
    task_id: str
    task_index: int
    agent_id: str
    role: str
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.assignment_id or not self.task_id or not self.agent_id or not self.role:
            raise ValueError("assignment fields are required")
        if int(self.task_index) < 0:
            raise ValueError("task_index must be non-negative")
        if not self.evidence_ids:
            raise ValueError("assignment must cite role evidence")


class PeerRoleLedger:
    """Append-only state machine for one or more task episodes."""

    def __init__(self, *, require_selection: bool = False, require_terminal_outcome: bool = False) -> None:
        # The default remains compatible with the original contract tests.  A
        # benchmark runner should turn both switches on so an ablation cannot
        # silently bypass attribution or leak a terminal label into learning.
        self.require_selection = require_selection
        self.require_terminal_outcome = require_terminal_outcome
        self.events: list[dict[str, Any]] = []
        self.selections: dict[str, PeerSelection] = {}
        self.deliveries: dict[str, Delivery] = {}
        self.judgments: dict[str, RecipientJudgment] = {}
        self.actions: dict[str, ConsumerAction] = {}
        self.outcomes: dict[str, TerminalOutcome] = {}
        self.evidence: dict[str, RoleEvidenceUpdate] = {}
        self.assignments: dict[str, LaterAssignment] = {}
        self.started_tasks: dict[tuple[str, int], int] = {}

    def _append(self, event_type: str, payload: Mapping[str, Any]) -> None:
        record = {
            "event_type": event_type,
            "payload": dict(payload),
            "previous_hash": self.events[-1]["record_hash"] if self.events else "GENESIS",
        }
        record["record_hash"] = _hash_payload(record)
        self.events.append(record)

    def record_selection(self, selection: PeerSelection) -> None:
        if selection.selection_id in self.selections:
            raise ValueError("duplicate selection_id")
        key = (selection.task_id, selection.task_index)
        if any((s.task_id, s.task_index) == key for s in self.selections.values()):
            raise ValueError("one selection is required per task episode")
        self.selections[selection.selection_id] = selection
        self._append("peer_selection", selection.__dict__)

    def record_task_start(self, task_id: str, task_index: int) -> None:
        key = (task_id, int(task_index))
        if key in self.started_tasks:
            raise ValueError("duplicate task start")
        self.started_tasks[key] = len(self.events)
        self._append("task_start", {"task_id": task_id, "task_index": int(task_index)})

    def record_delivery(self, delivery: Delivery) -> None:
        if delivery.delivery_id in self.deliveries:
            raise ValueError("duplicate delivery_id")
        if self.require_selection:
            if not delivery.selection_id:
                raise ValueError("strict ledger requires a selection_id")
            selection = self.selections.get(delivery.selection_id)
            if selection is None:
                raise ValueError("delivery must reference a recorded selection")
            if (selection.task_id, selection.task_index) != (delivery.task_id, delivery.task_index):
                raise ValueError("selection and delivery task episode must match")
            if selection.chosen_peer_id != delivery.producer_id:
                raise ValueError("delivery producer must be the selected peer")
        self.deliveries[delivery.delivery_id] = delivery
        self._append("producer_delivery", delivery.__dict__)

    def record_judgment(self, judgment: RecipientJudgment) -> None:
        if judgment.judgment_id in self.judgments:
            raise ValueError("duplicate judgment_id")
        delivery = self.deliveries.get(judgment.delivery_id)
        if delivery is None:
            raise ValueError("judgment must reference a recorded delivery")
        if judgment.consumer_id != delivery.recipient_id:
            raise ValueError("only the recorded recipient may judge the delivery")
        if judgment.observed_artifact_sha256 != delivery.artifact_sha256:
            raise ValueError("judgment must cite the delivered artifact digest")
        if any(j.delivery_id == judgment.delivery_id for j in self.judgments.values()):
            raise ValueError("one recipient judgment is allowed per delivery")
        if any(a.delivery_id == judgment.delivery_id for a in self.actions.values()):
            raise ValueError("judgment must precede consumer action")
        self.judgments[judgment.judgment_id] = judgment
        self._append("recipient_judgment", judgment.__dict__)

    def record_action(self, action: ConsumerAction) -> None:
        if action.action_id in self.actions:
            raise ValueError("duplicate action_id")
        delivery = self.deliveries.get(action.delivery_id)
        if delivery is None:
            raise ValueError("action must reference a recorded delivery")
        if action.consumer_id != delivery.recipient_id:
            raise ValueError("only the recorded recipient may act")
        if action.input_artifact_sha256 != delivery.artifact_sha256:
            raise ValueError("action must cite the delivered artifact digest")
        if not any(j.delivery_id == action.delivery_id for j in self.judgments.values()):
            raise ValueError("consumer action requires a prior recipient judgment")
        if any(a.delivery_id == action.delivery_id for a in self.actions.values()):
            raise ValueError("one consumer action is allowed per delivery")
        if self.require_selection:
            judgment = next(j for j in self.judgments.values() if j.delivery_id == action.delivery_id)
            if DECISION_ACTION[judgment.decision] != action.action:
                raise ValueError("consumer action does not match recipient judgment")
        self.actions[action.action_id] = action
        self._append("consumer_action", action.__dict__)

    def record_outcome(self, outcome: TerminalOutcome) -> None:
        if outcome.outcome_id in self.outcomes:
            raise ValueError("duplicate outcome_id")
        if outcome.delivery_id not in self.deliveries:
            raise ValueError("outcome must reference a recorded delivery")
        if not any(a.delivery_id == outcome.delivery_id for a in self.actions.values()):
            raise ValueError("terminal outcome requires a consumer action")
        if any(o.delivery_id == outcome.delivery_id for o in self.outcomes.values()):
            raise ValueError("one terminal outcome is allowed per delivery")
        self.outcomes[outcome.outcome_id] = outcome
        self._append("terminal_outcome", outcome.__dict__)

    def record_evidence_update(self, evidence: RoleEvidenceUpdate) -> None:
        if evidence.evidence_id in self.evidence:
            raise ValueError("duplicate evidence_id")
        judgment = self.judgments.get(evidence.judgment_id)
        action = self.actions.get(evidence.action_id)
        if judgment is None or action is None:
            raise ValueError("evidence must cite a recorded judgment and action")
        if judgment.delivery_id != action.delivery_id:
            raise ValueError("judgment and action must refer to the same delivery")
        if self.require_terminal_outcome and evidence.outcome_id is None:
            raise ValueError("strict ledger requires terminal outcome before evidence update")
        if evidence.outcome_id is not None:
            outcome = self.outcomes.get(evidence.outcome_id)
            if outcome is None or outcome.delivery_id != judgment.delivery_id:
                raise ValueError("evidence outcome must cite the same delivery")
        self.evidence[evidence.evidence_id] = evidence
        self._append("role_evidence_update", evidence.__dict__)

    def record_assignment(self, assignment: LaterAssignment) -> None:
        if assignment.assignment_id in self.assignments:
            raise ValueError("duplicate assignment_id")
        cited = set(assignment.evidence_ids)
        known = set(self.evidence)
        if not cited <= known:
            raise ValueError("assignment cites unknown role evidence")
        cited_deliveries = [
            self.deliveries[self.judgments[self.evidence[e].judgment_id].delivery_id]
            for e in cited
        ]
        if not all(assignment.task_index > delivery.task_index for delivery in cited_deliveries):
            raise ValueError("assignment must occur after the cited delivery")
        if self.require_selection:
            if any((assignment.task_id, assignment.task_index) == key for key in self.started_tasks):
                raise ValueError("assignment must be recorded before the assigned task starts")
            producers = {
                self.deliveries[self.judgments[self.evidence[e].judgment_id].delivery_id].producer_id
                for e in cited
            }
            if producers != {assignment.agent_id}:
                raise ValueError("assignment agent must match the cited producer")
        self.assignments[assignment.assignment_id] = assignment
        self._append("later_assignment", assignment.__dict__)

    def snapshot(self) -> dict[str, Any]:
        return {
            "event_count": len(self.events),
            "last_hash": self.events[-1]["record_hash"] if self.events else "GENESIS",
            "delivery_count": len(self.deliveries),
            "judgment_count": len(self.judgments),
            "action_count": len(self.actions),
            "outcome_count": len(self.outcomes),
            "evidence_count": len(self.evidence),
            "assignment_count": len(self.assignments),
        }
