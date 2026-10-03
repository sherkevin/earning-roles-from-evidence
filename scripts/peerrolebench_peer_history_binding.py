"""Canonical source-to-target binding for peer-history entries.

``PeerHistoryV2`` stores a deliberately small public projection.  This module
keeps the richer lineage in a separate append-only receipt so history rows
cannot be detached from the source evidence offer or the later assignment.
It consumes an already sealed native ledger and never calls a model or updates
policy state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_ROOT = ROOT / "references/aamas"
if str(PROTOCOL_ROOT) not in sys.path:
    sys.path.insert(0, str(PROTOCOL_ROOT))

from peerrolebench_role_evidence_offer import (  # noqa: E402
    RoleEvidenceOffer,
    build_role_evidence_from_ledger,
)
from peerrolebench_peer_history import HistoryEntryV1  # noqa: E402


SCHEMA = "peer-history-binding-v1"
_SHA256 = set("0123456789abcdef")


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                   ensure_ascii=False, default=str).encode()).hexdigest()


def _sha(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or set(value) - _SHA256:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _opaque(value: str, name: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 256:
        raise ValueError(f"{name} must be a bounded opaque identifier")
    return value


def _event_index(ledger: Any, event_type: str, identity_key: str, identity: str) -> int:
    for index, record in enumerate(getattr(ledger, "events", ())):
        if record.get("event_type") == event_type and record.get("payload", {}).get(identity_key) == identity:
            return index
    raise ValueError(f"ledger is missing {event_type}:{identity}")


@dataclass(frozen=True)
class HistoryBindingReceiptV1:
    history_entry_id: str
    history_status: str
    source_evidence_id: str
    source_offer_id: str
    source_offer_record_hash: str
    source_delivery_id: str
    source_judgment_id: str
    source_action_id: str
    source_outcome_id: str
    target_assignment_id: str
    target_selection_id: str
    target_delivery_id: str
    target_judgment_id: str
    target_action_id: str
    target_outcome_id: str
    source_candidate_key: str
    target_candidate_key: str
    source_task_index: int
    target_task_index: int
    source_available_index: int
    assignment_read_cut: int
    target_decision_index: int
    target_arrival_index: int
    candidate_registry_digest: str
    later_credit_digest: str | None
    binding_digest: str

    def __post_init__(self) -> None:
        for name in (
            "history_entry_id", "source_evidence_id", "source_offer_id",
            "source_delivery_id", "source_judgment_id", "source_action_id",
            "source_outcome_id", "target_assignment_id", "target_selection_id",
            "target_delivery_id", "target_judgment_id", "target_action_id",
            "target_outcome_id", "source_candidate_key", "target_candidate_key",
        ):
            _opaque(getattr(self, name), name)
        if self.history_status not in {"PASS", "FAIL", "UNKNOWN"}:
            raise ValueError("history_status must be PASS, FAIL, or UNKNOWN")
        _sha(self.source_offer_record_hash, "source_offer_record_hash")
        _sha(self.candidate_registry_digest, "candidate_registry_digest")
        if self.history_status in {"PASS", "FAIL"} and self.later_credit_digest is None:
            raise ValueError("determinate history binding requires delayed-credit digest")
        if self.history_status == "UNKNOWN" and self.later_credit_digest is not None:
            raise ValueError("UNKNOWN history binding cannot carry delayed-credit digest")
        if self.later_credit_digest is not None:
            _sha(self.later_credit_digest, "later_credit_digest")
        _sha(self.binding_digest, "binding_digest")
        for name in ("source_task_index", "target_task_index", "source_available_index",
                     "assignment_read_cut", "target_decision_index", "target_arrival_index"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.source_task_index >= self.target_task_index:
            raise ValueError("source task must precede target task")
        if not (self.source_available_index <= self.assignment_read_cut <= self.target_decision_index):
            raise ValueError("source evidence is unavailable at the assignment read cut")
        if self.target_arrival_index <= self.target_decision_index:
            raise ValueError("target outcome must arrive after the target decision")
        if self.source_candidate_key != self.target_candidate_key:
            raise ValueError("source and target candidate keys must identify the same peer")
        if self.binding_digest != _digest(self.payload(include_digest=False)):
            raise ValueError("binding_digest does not match canonical payload")

    def payload(self, *, include_digest: bool = True) -> dict[str, Any]:
        row = {"schema": SCHEMA, **asdict(self)}
        if not include_digest:
            row.pop("binding_digest")
        return row


def build_history_binding_receipt(
    *,
    entry: HistoryEntryV1,
    ledger: Any,
    offer: RoleEvidenceOffer,
    target_assignment: Any,
    target_selection: Any,
    target_outcome_id: str,
    assignment_read_cut: int,
    target_decision_index: int,
    target_arrival_index: int,
    candidate_key: str,
    candidate_registry_digest: str,
    later_credit_digest: str | None = None,
) -> HistoryBindingReceiptV1:
    """Bind one history entry to canonical source and target records."""
    if not isinstance(entry, HistoryEntryV1):
        raise TypeError("entry must be a HistoryEntryV1")
    if not isinstance(offer, RoleEvidenceOffer):
        raise TypeError("offer must be a RoleEvidenceOffer")
    _opaque(candidate_key, "candidate_key")
    _sha(candidate_registry_digest, "candidate_registry_digest")
    if offer.candidate_registry_digest != candidate_registry_digest:
        raise ValueError("offer and binding candidate registry digests differ")
    if target_assignment.task_id != offer.task_id or target_assignment.task_index != offer.task_index:
        raise ValueError("target assignment does not match the source offer task")
    if target_assignment.role != offer.role:
        raise ValueError("target assignment role does not match the source offer")
    if candidate_key not in offer.candidate_keys:
        raise ValueError("candidate is outside the source offer menu")
    if "@" not in candidate_key or candidate_key.split("@", 1)[0] != target_assignment.agent_id:
        raise ValueError("candidate key does not match assigned peer")
    if entry.assignment_id != target_assignment.assignment_id:
        raise ValueError("history entry assignment does not match target assignment")
    if entry.subject_key != target_assignment.agent_id or entry.agent_key != target_assignment.agent_id:
        raise ValueError("history entry subject does not match assigned peer")
    if target_outcome_id != entry.later_outcome_id:
        raise ValueError("history entry outcome does not match target outcome")
    if target_selection.task_id != target_assignment.task_id or target_selection.task_index != target_assignment.task_index:
        raise ValueError("target selection does not match target assignment")
    if target_selection.chosen_peer_id != target_assignment.agent_id:
        raise ValueError("target selection chose a different peer")
    if target_assignment.assignment_id not in getattr(ledger, "assignments", {}):
        raise ValueError("target assignment is not sealed in the canonical ledger")
    if target_selection.selection_id not in getattr(ledger, "selections", {}):
        raise ValueError("target selection is not sealed in the canonical ledger")
    if target_outcome_id not in getattr(ledger, "outcomes", {}):
        raise ValueError("target outcome is not sealed in the canonical ledger")
    source_ids = set(offer.evidence_ids)
    if len(source_ids) != 1:
        raise ValueError("binding requires one source evidence record")
    source_evidence_id = next(iter(source_ids))
    if source_evidence_id not in target_assignment.evidence_ids:
        raise ValueError("target assignment does not cite source evidence")
    source_row = next((row for row in offer.public_evidence if row["evidence_id"] == source_evidence_id), None)
    if source_row is None:
        raise ValueError("source evidence row is missing from the offer")
    source = build_role_evidence_from_ledger(
        ledger=ledger, evidence_id=source_evidence_id, candidate_key=candidate_key,
        role=offer.role, target_task_index=target_assignment.task_index,
        evidence_version=offer.evidence_version, available_index=int(source_row["available_index"]),
    )
    if entry.delivery_digest != source.artifact_sha256 or entry.recipient_judgment_id != source.judgment_id:
        raise ValueError("history entry does not bind to source delivery/judgment")
    target_outcome = ledger.outcomes[target_outcome_id]
    target_delivery = ledger.deliveries[target_outcome.delivery_id]
    target_judgment = next((item for item in ledger.judgments.values() if item.delivery_id == target_delivery.delivery_id), None)
    target_action = next((item for item in ledger.actions.values() if item.delivery_id == target_delivery.delivery_id), None)
    if target_judgment is None or target_action is None:
        raise ValueError("target delivery lacks judgment/action")
    if target_delivery.producer_id != target_assignment.agent_id or target_delivery.task_index != target_assignment.task_index:
        raise ValueError("target delivery is not the assigned peer's target episode")
    if target_selection.selection_id != target_delivery.selection_id:
        raise ValueError("target delivery is not bound to target selection")
    if target_outcome.delivery_id != target_delivery.delivery_id:
        raise ValueError("target outcome delivery mismatch")
    if (int(assignment_read_cut) < int(source.available_index)
            or int(assignment_read_cut) < int(offer.available_index)
            or int(assignment_read_cut) > int(target_decision_index)):
        raise ValueError("assignment read cut is outside source/decision interval")
    if int(target_arrival_index) <= int(target_decision_index) or entry.arrival_index < int(target_arrival_index):
        raise ValueError("history entry arrived before target outcome")
    source_event_index = _event_index(ledger, "role_evidence_update", "evidence_id", source_evidence_id)
    assignment_event_index = _event_index(ledger, "later_assignment", "assignment_id", target_assignment.assignment_id)
    selection_event_index = _event_index(ledger, "peer_selection", "selection_id", target_selection.selection_id)
    outcome_event_index = _event_index(ledger, "terminal_outcome", "outcome_id", target_outcome_id)
    if not source_event_index < assignment_event_index < selection_event_index < outcome_event_index:
        raise ValueError("source, assignment, selection, and target outcome order is invalid")
    body = {
        "history_entry_id": entry.entry_id,
        "history_status": entry.status,
        "source_evidence_id": source_evidence_id,
        "source_offer_id": offer.offer_id,
        "source_offer_record_hash": offer.offer_record_hash,
        "source_delivery_id": source.delivery_id,
        "source_judgment_id": source.judgment_id,
        "source_action_id": source.action_id,
        "source_outcome_id": source.outcome_id,
        "target_assignment_id": target_assignment.assignment_id,
        "target_selection_id": target_selection.selection_id,
        "target_delivery_id": target_delivery.delivery_id,
        "target_judgment_id": target_judgment.judgment_id,
        "target_action_id": target_action.action_id,
        "target_outcome_id": target_outcome_id,
        "source_candidate_key": candidate_key,
        "target_candidate_key": candidate_key,
        "source_task_index": int(source.source_task_index),
        "target_task_index": int(target_assignment.task_index),
        "source_available_index": int(source.available_index),
        "assignment_read_cut": int(assignment_read_cut),
        "target_decision_index": int(target_decision_index),
        "target_arrival_index": int(target_arrival_index),
        "candidate_registry_digest": candidate_registry_digest,
        "later_credit_digest": later_credit_digest,
    }
    return HistoryBindingReceiptV1(**body, binding_digest=_digest({"schema": SCHEMA, **body}))


__all__ = ["HistoryBindingReceiptV1", "SCHEMA", "build_history_binding_receipt"]
