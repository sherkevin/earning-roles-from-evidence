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


def _hash_payload(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _artifact_hash(value: str) -> str:
    value = str(value)
    if not SHA256_RE.fullmatch(value):
        raise ValueError("artifact_sha256 must be a lowercase SHA-256 digest")
    return value


@dataclass(frozen=True)
class Delivery:
    delivery_id: str
    task_id: str
    producer_id: str
    recipient_id: str
    artifact_sha256: str
    source_event_id: str
    task_index: int

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

    def __post_init__(self) -> None:
        if not self.action_id or not self.delivery_id or not self.consumer_id:
            raise ValueError("action identifiers are required")
        _artifact_hash(self.input_artifact_sha256)
        if self.output_artifact_sha256 is not None:
            _artifact_hash(self.output_artifact_sha256)
        if float(self.repair_cost) < 0:
            raise ValueError("repair_cost must be non-negative")


@dataclass(frozen=True)
class TerminalOutcome:
    outcome_id: str
    delivery_id: str
    success: bool
    scorer_version: str

    def __post_init__(self) -> None:
        if not self.outcome_id or not self.delivery_id or not self.scorer_version:
            raise ValueError("terminal outcome identifiers and scorer_version are required")


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

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.deliveries: dict[str, Delivery] = {}
        self.judgments: dict[str, RecipientJudgment] = {}
        self.actions: dict[str, ConsumerAction] = {}
        self.outcomes: dict[str, TerminalOutcome] = {}
        self.assignments: dict[str, LaterAssignment] = {}

    def _append(self, event_type: str, payload: Mapping[str, Any]) -> None:
        record = {
            "event_type": event_type,
            "payload": dict(payload),
            "previous_hash": self.events[-1]["record_hash"] if self.events else "GENESIS",
        }
        record["record_hash"] = _hash_payload(record)
        self.events.append(record)

    def record_delivery(self, delivery: Delivery) -> None:
        if delivery.delivery_id in self.deliveries:
            raise ValueError("duplicate delivery_id")
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
        self.actions[action.action_id] = action
        self._append("consumer_action", action.__dict__)

    def record_outcome(self, outcome: TerminalOutcome) -> None:
        if outcome.outcome_id in self.outcomes:
            raise ValueError("duplicate outcome_id")
        if outcome.delivery_id not in self.deliveries:
            raise ValueError("outcome must reference a recorded delivery")
        if not any(a.delivery_id == outcome.delivery_id for a in self.actions.values()):
            raise ValueError("terminal outcome requires a consumer action")
        self.outcomes[outcome.outcome_id] = outcome
        self._append("terminal_outcome", outcome.__dict__)

    def record_assignment(self, assignment: LaterAssignment) -> None:
        if assignment.assignment_id in self.assignments:
            raise ValueError("duplicate assignment_id")
        cited = set(assignment.evidence_ids)
        known = {j.judgment_id for j in self.judgments.values()}
        if not cited <= known:
            raise ValueError("assignment cites unknown role evidence")
        cited_deliveries = [self.deliveries[self.judgments[e].delivery_id] for e in cited]
        if not all(assignment.task_index > delivery.task_index for delivery in cited_deliveries):
            raise ValueError("assignment must occur after the cited delivery")
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
            "assignment_count": len(self.assignments),
        }
