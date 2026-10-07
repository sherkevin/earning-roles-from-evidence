"""Compose existing zero-call contracts for one source-to-target fixture.

This adapter deliberately stops at a replayable, pre-route decision.  It does
not call a model, execute candidate code, score a task, or update a policy.
The PIPE1 runner can use its result as a fail-closed gate before projecting a
validated ledger into the route-receipt schema.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from peerrolebench_pipe3_live_contract import (
    classify_ownership,
    unknown_no_update,
    validate_ledger_key_binding,
    validate_selection_receipt,
    validate_source_target_schedule,
)


VERSION = "pipe1-offline-adapter-v1"
_TASK_EVENTS = {
    "peer_selection", "task_start", "producer_delivery", "later_assignment",
}


def _task_ids(events: Sequence[Mapping[str, Any]]) -> set[str]:
    values: set[str] = set()
    for row in events:
        if not isinstance(row, Mapping):
            values.add("<invalid-row>")
            continue
        if row.get("event_type") not in _TASK_EVENTS:
            continue
        payload = row.get("payload")
        if not isinstance(payload, Mapping) or not isinstance(payload.get("task_id"), str):
            values.add("<missing>")
        else:
            values.add(payload["task_id"])
    return values


def _event_payloads(
    rows: Sequence[Mapping[str, Any]], event_type: str, key: str, value: str,
) -> list[Mapping[str, Any]]:
    """Return payloads for one identity; malformed rows are simply absent."""
    result: list[Mapping[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping) or row.get("event_type") != event_type:
            continue
        payload = row.get("payload")
        if isinstance(payload, Mapping) and payload.get(key) == value:
            result.append(payload)
    return result


def _selection_binding(
    *, rows: Sequence[Mapping[str, Any]], task_id: str, source_task_index: int,
    target_task_index: int,
    target_selection_id: str, assignment_id: str, evidence_id: str,
    menu_keys: Sequence[str], chosen_key: str, propensity: float,
) -> dict[str, Any]:
    """Bind caller-visible selection arguments to the native ledger facts."""
    errors: list[str] = []
    selections = _event_payloads(rows, "peer_selection", "selection_id", target_selection_id)
    if len(selections) != 1:
        errors.append("target selection id must identify exactly one peer_selection")
        selection = None
    else:
        selection = selections[0]
    assignments = _event_payloads(rows, "later_assignment", "assignment_id", assignment_id)
    if len(assignments) != 1:
        errors.append("assignment id must identify exactly one later_assignment")
        assignment = None
    else:
        assignment = assignments[0]

    if not isinstance(target_task_index, int) or isinstance(target_task_index, bool) or target_task_index < 0:
        errors.append("target_task_index must be a non-negative integer")
    if selection is not None:
        if selection.get("task_id") != task_id or selection.get("task_index") != target_task_index:
            errors.append("target selection task identity/index is not bound")
        candidate_ids = selection.get("candidate_ids")
        menu_ids = [str(key).split("@", 1)[0] for key in menu_keys]
        if not isinstance(candidate_ids, (list, tuple)) or tuple(candidate_ids) != tuple(menu_ids):
            errors.append("target selection candidate menu differs from selection receipt")
        selected_id = str(chosen_key).split("@", 1)[0]
        if selection.get("chosen_peer_id") != selected_id:
            errors.append("target selection chosen peer differs from selection receipt")
        native_propensity = selection.get("propensity")
        if not isinstance(native_propensity, (int, float)) or abs(float(native_propensity) - float(propensity)) > 1e-12:
            errors.append("target selection propensity differs from selection receipt")

    evidence_rows = _event_payloads(rows, "role_evidence_update", "evidence_id", evidence_id)
    if len(evidence_rows) != 1:
        errors.append("evidence id must identify exactly one role_evidence_update")
        evidence = None
    else:
        evidence = evidence_rows[0]
    if assignment is not None:
        if assignment.get("task_id") != task_id or assignment.get("task_index") != target_task_index:
            errors.append("assignment task identity/index is not bound")
        evidence_ids = assignment.get("evidence_ids")
        if not isinstance(evidence_ids, (list, tuple)) or evidence_id not in evidence_ids:
            errors.append("assignment does not cite the supplied evidence id")
        if selection is not None and assignment.get("agent_id") != selection.get("chosen_peer_id"):
            errors.append("assignment agent differs from target selected peer")

    evidence_delivery = None
    if evidence is not None:
        delivery_ids: list[str] = []
        for event_type, ref_key in (
            ("recipient_judgment", "judgment_id"),
            ("consumer_action", "action_id"),
            ("terminal_outcome", "outcome_id"),
        ):
            ref = evidence.get(ref_key)
            linked = _event_payloads(rows, event_type, ref_key, ref) if isinstance(ref, str) else []
            if len(linked) != 1 or not isinstance(linked[0].get("delivery_id"), str):
                errors.append(f"evidence {ref_key} is not bound to one {event_type}")
            else:
                delivery_ids.append(linked[0]["delivery_id"])
        if delivery_ids and len(set(delivery_ids)) != 1:
            errors.append("evidence references disagree on delivery")
        if delivery_ids:
            deliveries = _event_payloads(rows, "producer_delivery", "delivery_id", delivery_ids[0])
            if len(deliveries) != 1:
                errors.append("evidence delivery is missing or duplicated")
            else:
                evidence_delivery = deliveries[0]
                if evidence_delivery.get("task_id") != task_id or evidence_delivery.get("task_index") != source_task_index:
                    errors.append("evidence delivery is not bound to the source task index")

    return {
        "valid": not errors,
        "errors": errors,
        "target_selection": dict(selection) if selection is not None else None,
        "assignment": dict(assignment) if assignment is not None else None,
        "evidence_count": len(evidence_rows),
        "evidence_delivery": dict(evidence_delivery) if evidence_delivery is not None else None,
    }


def _ownership_status(rows: Sequence[Mapping[str, Any]]) -> str:
    if not rows:
        return "UNASSESSED"
    statuses = [row["status"] for row in rows]
    if any(status == "UNKNOWN" for status in statuses):
        return "UNKNOWN"
    if all(status == "ELIGIBLE" for status in statuses):
        return "ELIGIBLE"
    return "PENDING_ATTRIBUTION"


def validate_source_target_fixture(
    *,
    events: Iterable[Mapping[str, Any]],
    task_id: str,
    source_task_index: int,
    target_task_index: int,
    evidence_id: str,
    assignment_id: str,
    target_selection_id: str,
    registry: Sequence[Any],
    menu_keys: Sequence[str],
    chosen_key: str,
    probabilities: Sequence[float],
    chosen_index: int,
    propensity: float,
    ownership_cases: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Validate the reusable contracts and return a no-update gate result."""
    rows = list(events)
    errors: list[str] = []
    if not isinstance(task_id, str) or not task_id:
        errors.append("task_id is required")
    task_ids = _task_ids(rows)
    if task_ids != {task_id}:
        errors.append(f"task ids are not uniformly bound to {task_id!r}: {sorted(task_ids)}")

    source_index_valid = isinstance(source_task_index, int) and not isinstance(source_task_index, bool) and source_task_index >= 0
    target_index_valid = isinstance(target_task_index, int) and not isinstance(target_task_index, bool) and target_task_index >= 0
    if not source_index_valid:
        errors.append("source_task_index must be a non-negative integer")
    if not target_index_valid:
        errors.append("target_task_index must be a non-negative integer")
    if source_index_valid and target_index_valid and source_task_index >= target_task_index:
        errors.append("source_task_index must precede target_task_index")
    try:
        ledger = validate_ledger_key_binding(rows)
    except (AttributeError, TypeError, ValueError) as exc:
        ledger = {"valid": False, "status": "INVALID", "error": f"{type(exc).__name__}: {exc}"}
    try:
        schedule = validate_source_target_schedule(
            events=rows,
            source_task_index=source_task_index,
            target_task_index=target_task_index,
            evidence_id=evidence_id,
            assignment_id=assignment_id,
            target_selection_id=target_selection_id,
        )
    except (AttributeError, TypeError, ValueError) as exc:
        schedule = {"valid": False, "status": "INVALID", "errors": [f"{type(exc).__name__}: {exc}"]}
    try:
        selection = validate_selection_receipt(
            registry=registry,
            menu_keys=menu_keys,
            chosen_key=chosen_key,
            probabilities=probabilities,
            chosen_index=chosen_index,
            propensity=propensity,
        )
    except (AttributeError, TypeError, ValueError) as exc:
        selection = {"valid": False, "errors": [f"{type(exc).__name__}: {exc}"]}
    selection_binding = _selection_binding(
        rows=rows, task_id=task_id, source_task_index=source_task_index,
        target_task_index=target_task_index,
        target_selection_id=target_selection_id, assignment_id=assignment_id,
        evidence_id=evidence_id, menu_keys=menu_keys, chosen_key=chosen_key,
        propensity=propensity,
    )
    ownership: list[dict[str, Any]] = []
    for index, case in enumerate(ownership_cases):
        try:
            row = classify_ownership(**dict(case))
        except (TypeError, ValueError) as exc:
            row = {"status": "UNKNOWN", "reason": f"ownership case {index} invalid: {type(exc).__name__}"}
        ownership.append(row)

    if not ledger.get("valid"):
        errors.append("ledger key binding failed")
    if not schedule.get("valid"):
        errors.append("source-to-target schedule failed")
    if not selection.get("valid"):
        errors.append("selection receipt failed")
    if not selection_binding["valid"]:
        errors.append("native selection/assignment/evidence binding failed")

    route_ready = not errors
    if route_ready:
        update = {"status": "READY_FOR_ROUTE", "state_unchanged": True,
                  "label": None, "assignment_created": False,
                  "target_selection_created": False, "policy_update_allowed": False}
    else:
        update = unknown_no_update(
            state_before="offline-adapter-before",
            state_after="offline-adapter-before",
            reason="; ".join(errors),
        )
    return {
        "schema": VERSION,
        "status": update["status"],
        "route_ready": route_ready,
        "policy_update_allowed": False,
        "errors": errors,
        "task_ids": sorted(task_ids),
        "ledger": ledger,
        "schedule": schedule,
        "selection": selection,
        "selection_input": {
            "menu_keys": list(menu_keys),
            "chosen_key": chosen_key,
            "probabilities": [float(value) for value in probabilities],
            "chosen_index": chosen_index,
            "propensity": float(propensity),
        },
        "selection_binding": selection_binding,
        "ownership": ownership,
        "ownership_status": _ownership_status(ownership),
        "update_boundary": update,
    }


__all__ = ["VERSION", "validate_source_target_fixture"]
