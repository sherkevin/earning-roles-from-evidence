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
        if row.get("event_type") not in _TASK_EVENTS:
            continue
        payload = row.get("payload")
        if not isinstance(payload, Mapping) or not isinstance(payload.get("task_id"), str):
            values.add("<missing>")
        else:
            values.add(payload["task_id"])
    return values


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

    ledger = validate_ledger_key_binding(rows)
    schedule = validate_source_target_schedule(
        events=rows,
        source_task_index=source_task_index,
        target_task_index=target_task_index,
        evidence_id=evidence_id,
        assignment_id=assignment_id,
        target_selection_id=target_selection_id,
    )
    selection = validate_selection_receipt(
        registry=registry,
        menu_keys=menu_keys,
        chosen_key=chosen_key,
        probabilities=probabilities,
        chosen_index=chosen_index,
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
        "ownership": ownership,
        "ownership_status": _ownership_status(ownership),
        "update_boundary": update,
    }


__all__ = ["VERSION", "validate_source_target_fixture"]
