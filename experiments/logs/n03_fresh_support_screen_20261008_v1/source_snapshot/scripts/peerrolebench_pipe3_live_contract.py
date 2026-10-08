"""Small zero-call contract for the future PIPE3 live runner.

This module validates runner preconditions only.  It does not call an LLM,
execute candidate source, score a task, or update a policy.  The contract is
kept separate from the historical runners so a schema mistake cannot alter a
frozen receipt.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from peerrolebench_candidate_registry import (
    CandidateRegistryEntry, candidate_refs, registry_digest, validate_registry,
)
from peerrolebench_event_time_schedule import ArrivalAssignment, validate_schedule
from peerrolebench_ledger_replay import replay_ledger_events


VERSION = "pipe3-live-contract-v1"


@dataclass(frozen=True)
class SourceTargetSchedule:
    source_task_index: int
    target_task_index: int
    evidence_id: str
    assignment_id: str
    target_selection_id: str
    target_start_seen: bool

    def validate(self) -> dict[str, Any]:
        errors: list[str] = []
        if self.source_task_index >= self.target_task_index:
            errors.append("source episode must precede target episode")
        for name, value in (("evidence_id", self.evidence_id), ("assignment_id", self.assignment_id),
                            ("target_selection_id", self.target_selection_id)):
            if not value:
                errors.append(f"{name} is required")
        if not self.target_start_seen:
            errors.append("target task_start is missing")
        return {"valid": not errors, "errors": errors, "source_task_index": self.source_task_index,
                "target_task_index": self.target_task_index, "evidence_id": self.evidence_id,
                "assignment_id": self.assignment_id, "target_selection_id": self.target_selection_id}


def validate_source_target_schedule(
    *, events: Iterable[Mapping[str, Any]], source_task_index: int,
    target_task_index: int, evidence_id: str, assignment_id: str,
    target_selection_id: str,
) -> dict[str, Any]:
    """Check that assignment precedes the target selection/start in one ledger."""
    rows = list(events)
    positions = {(row.get("event_type"), row.get("payload", {}).get("selection_id") or
                 row.get("payload", {}).get("assignment_id")): index for index, row in enumerate(rows)}
    assignment_pos = positions.get(("later_assignment", assignment_id))
    selection_pos = positions.get(("peer_selection", target_selection_id))
    start_pos = next((index for index, row in enumerate(rows)
                      if row.get("event_type") == "task_start"
                      and row.get("payload", {}).get("task_index") == target_task_index), None)
    result = SourceTargetSchedule(source_task_index, target_task_index, evidence_id, assignment_id,
                                  target_selection_id, start_pos is not None).validate()
    result["assignment_before_target_selection"] = assignment_pos is not None and selection_pos is not None and assignment_pos < selection_pos
    result["assignment_before_target_start"] = assignment_pos is not None and start_pos is not None and assignment_pos < start_pos
    result["valid"] = bool(result["valid"] and result["assignment_before_target_selection"] and result["assignment_before_target_start"])
    if not result["assignment_before_target_selection"]:
        result["errors"].append("assignment must precede target selection")
    if not result["assignment_before_target_start"]:
        result["errors"].append("assignment must precede target task_start")
    return result


def validate_ledger_key_binding(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Replay a sealed ledger and check cross-event identity bindings."""
    rows = list(events)
    try:
        replay = replay_ledger_events(rows)
    except Exception as exc:
        return {"valid": False, "status": "INVALID", "error": str(exc), "event_count": len(rows)}
    ledger = replay.ledger
    errors: list[str] = []
    for delivery in ledger.deliveries.values():
        selection = ledger.selections.get(delivery.selection_id)
        if selection is None or selection.chosen_peer_id != delivery.producer_id:
            errors.append(f"delivery {delivery.delivery_id} is not bound to selected peer")
        score = next((item for item in ledger.producer_scores.values() if item.delivery_id == delivery.delivery_id), None)
        if score is None or score.artifact_sha256 != delivery.artifact_sha256:
            errors.append(f"producer score is not bound to delivery {delivery.delivery_id}")
        judgment = next((item for item in ledger.judgments.values() if item.delivery_id == delivery.delivery_id), None)
        action = next((item for item in ledger.actions.values() if item.delivery_id == delivery.delivery_id), None)
        outcome = next((item for item in ledger.outcomes.values() if item.delivery_id == delivery.delivery_id), None)
        if judgment is None or judgment.observed_artifact_sha256 != delivery.artifact_sha256:
            errors.append(f"judgment is not bound to delivery {delivery.delivery_id}")
        if action is None or action.input_artifact_sha256 != delivery.artifact_sha256:
            errors.append(f"action is not bound to delivery {delivery.delivery_id}")
        if outcome is None:
            errors.append(f"outcome is missing for delivery {delivery.delivery_id}")
    return {"valid": not errors, "status": replay.status, "error": None if not errors else "; ".join(errors),
            "event_count": len(rows), "snapshot": replay.snapshot}


def classify_ownership(
    *, changed_paths: Sequence[str], producer_paths: Sequence[str], recipient_paths: Sequence[str],
    producer_defect_registered: bool, producer_score_status: str, producer_label: int | None,
    q_complete: bool = True, source_digest_match: bool = True, counterfactual_complete: bool = True,
) -> dict[str, Any]:
    """Apply the card's conservative responsibility table."""
    changed = set(changed_paths); producers = set(producer_paths); recipients = set(recipient_paths)
    producer_changed = sorted(changed & producers); recipient_changed = sorted(changed & recipients)
    outside = sorted(changed - producers - recipients)
    q_fail = producer_score_status == "FAIL" and producer_label == 0
    if outside or not source_digest_match or not q_complete:
        status, reason = "UNKNOWN", "outside contract, digest mismatch, or incomplete Qp"
    elif producer_changed and recipient_changed:
        status, reason = "UNKNOWN", "mixed ownership requires a registered counterfactual"
    elif recipient_changed and not producer_changed:
        status, reason = "PENDING_ATTRIBUTION", "recipient-only integration cannot label producer"
    elif producer_defect_registered and q_fail and counterfactual_complete and producer_changed:
        status, reason = "ELIGIBLE", "registered producer defect with independent Qp FAIL/0"
    else:
        status, reason = "PENDING_ATTRIBUTION", "no eligible producer responsibility signal"
    return {"status": status, "producer_feedback_eligible": status == "ELIGIBLE",
            "policy_update_allowed": False, "producer_owned_paths_changed": producer_changed,
            "recipient_owned_paths_changed": recipient_changed, "outside_contract_paths": outside,
            "reason": reason}


def validate_selection_receipt(
    *, registry: Sequence[CandidateRegistryEntry | Mapping[str, Any]], menu_keys: Sequence[str],
    chosen_key: str, probabilities: Sequence[float], chosen_index: int, propensity: float,
) -> dict[str, Any]:
    """Validate immutable candidate menu and the recorded sampling propensity."""
    errors: list[str] = []
    try:
        entries = validate_registry(registry)
        candidate_ids = tuple(key.split("@", 1)[0] for key in menu_keys)
        refs = candidate_refs(candidate_ids, entries)
    except (TypeError, ValueError) as exc:
        entries = ()
        refs = ()
        errors.append(f"candidate registry/menu binding is invalid: {exc}")
    if len(menu_keys) < 2 or len(set(menu_keys)) != len(menu_keys):
        errors.append("candidate menu must contain at least two unique keys")
    if tuple(ref.key for ref in refs) != tuple(menu_keys):
        errors.append("menu key is not bound to the registered candidate version")
    if chosen_index < 0 or chosen_index >= len(menu_keys) or menu_keys[chosen_index] != chosen_key:
        errors.append("chosen index/key mismatch")
    if len(probabilities) != len(menu_keys) or any(float(p) < 0 or float(p) > 1 for p in probabilities):
        errors.append("probability vector is invalid")
    if len(probabilities) == len(menu_keys) and abs(sum(float(p) for p in probabilities) - 1.0) > 1e-9:
        errors.append("probabilities must sum to one")
    if (len(probabilities) == len(menu_keys) and 0 <= chosen_index < len(probabilities)
            and abs(float(propensity) - float(probabilities[chosen_index])) > 1e-12):
        errors.append("propensity must equal probability of chosen menu item")
    digest = registry_digest(entries) if entries else None
    return {"valid": not errors, "errors": errors, "registry_digest": digest,
            "menu_keys": list(menu_keys), "chosen_key": chosen_key, "propensity": propensity}


def unknown_no_update(*, state_before: str, state_after: str, reason: str) -> dict[str, Any]:
    """UNKNOWN is an explicit stop: no label, assignment, or policy update."""
    valid = bool(reason and state_before == state_after)
    return {"valid": valid, "status": "UNKNOWN", "unknown_reason": reason,
            "label": None, "assignment_created": False, "target_selection_created": False,
            "policy_update_allowed": False, "state_unchanged": state_before == state_after}


__all__ = ["VERSION", "SourceTargetSchedule", "classify_ownership", "unknown_no_update",
           "validate_ledger_key_binding", "validate_selection_receipt", "validate_source_target_schedule"]
