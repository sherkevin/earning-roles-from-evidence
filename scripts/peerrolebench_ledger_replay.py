"""Independent replay validation for the peer-role event ledger.

The protocol object appends events while a runner is executing.  This module is
an *outer* validator: it first checks the serialized hash chain, then replays
the events through the strict protocol state machine, and finally checks that a
complete evidence path exists for every delivery.  It is deliberately usable
without the live runner so a parent process can validate a sealed ledger before
using it for learning or scoring.

The validator distinguishes incomplete execution (``UNKNOWN``) from an invalid
ledger (``INVALID``).  An incomplete ledger can be inspected with
``allow_incomplete=True``; unknown event types, retries inserted into the
append-only ledger, hash changes, and causal/order violations always fail.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "references/aamas"
if str(REFERENCE) not in sys.path:
    sys.path.insert(0, str(REFERENCE))

from peer_role_protocol_20260925 import (  # type: ignore[import-not-found]
    ConsumerAction,
    Delivery,
    LaterAssignment,
    PeerRoleLedger,
    PeerSelection,
    RecipientJudgment,
    RoleEvidenceUpdate,
    TerminalOutcome,
    _hash_payload,
)


EVENT_CONSTRUCTORS = {
    "peer_selection": ("record_selection", PeerSelection, "selection_id"),
    "producer_delivery": ("record_delivery", Delivery, "delivery_id"),
    "recipient_judgment": ("record_judgment", RecipientJudgment, "judgment_id"),
    "consumer_action": ("record_action", ConsumerAction, "action_id"),
    "terminal_outcome": ("record_outcome", TerminalOutcome, "outcome_id"),
    "role_evidence_update": ("record_evidence_update", RoleEvidenceUpdate, "evidence_id"),
    "later_assignment": ("record_assignment", LaterAssignment, "assignment_id"),
}
TASK_START = "task_start"
KNOWN_EVENT_TYPES = frozenset((*EVENT_CONSTRUCTORS, TASK_START))


class LedgerReplayError(ValueError):
    """A sealed event list cannot be trusted as a protocol execution."""

    def __init__(self, code: str, message: str, *, index: int | None = None):
        self.code = code
        self.index = index
        suffix = f" at event {index}" if index is not None else ""
        super().__init__(f"{code}{suffix}: {message}")


@dataclass(frozen=True)
class ReplayResult:
    """Result returned after all event records have been replayed."""

    status: str  # PASS or UNKNOWN; INVALID is represented by LedgerReplayError.
    complete: bool
    event_count: int
    missing: tuple[dict[str, Any], ...]
    snapshot: dict[str, Any]
    ledger: PeerRoleLedger

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "complete": self.complete,
            "event_count": self.event_count,
            "missing": list(self.missing),
            "snapshot": self.snapshot,
        }


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _record_error(index: int, code: str, message: str) -> LedgerReplayError:
    return LedgerReplayError(code, message, index=index)


def _validate_record_shape(record: Any, index: int) -> tuple[str, Mapping[str, Any]]:
    if not isinstance(record, Mapping):
        raise _record_error(index, "malformed_record", "record must be an object")
    expected = {"event_type", "payload", "previous_hash", "record_hash"}
    if set(record) != expected:
        raise _record_error(index, "malformed_record", f"record keys must be {sorted(expected)}")
    event_type = record.get("event_type")
    if not isinstance(event_type, str):
        raise _record_error(index, "malformed_record", "event_type must be a string")
    if event_type not in KNOWN_EVENT_TYPES:
        code = "unsupported_retry" if "retry" in event_type.lower() else "unknown_event_type"
        raise _record_error(index, code, f"event type {event_type!r} is not part of the append-only protocol")
    payload = record.get("payload")
    if not isinstance(payload, Mapping):
        raise _record_error(index, "malformed_record", "payload must be an object")
    for key in ("previous_hash", "record_hash"):
        if not isinstance(record[key], str):
            raise _record_error(index, "malformed_record", f"{key} must be a string")
    return event_type, payload


def _missing_for(ledger: PeerRoleLedger) -> list[dict[str, Any]]:
    """Report absent causal stages without mutating the protocol ledger."""
    missing: list[dict[str, Any]] = []
    for delivery in ledger.deliveries.values():
        delivery_id = delivery.delivery_id
        if not any(j.delivery_id == delivery_id for j in ledger.judgments.values()):
            missing.append({"stage": "recipient_judgment", "delivery_id": delivery_id})
        if not any(a.delivery_id == delivery_id for a in ledger.actions.values()):
            missing.append({"stage": "consumer_action", "delivery_id": delivery_id})
        if not any(o.delivery_id == delivery_id for o in ledger.outcomes.values()):
            missing.append({"stage": "terminal_outcome", "delivery_id": delivery_id})
        if not any(
            ledger.judgments[e.judgment_id].delivery_id == delivery_id
            for e in ledger.evidence.values()
            if e.judgment_id in ledger.judgments
        ):
            missing.append({"stage": "role_evidence_update", "delivery_id": delivery_id})
    for selection in ledger.selections.values():
        key = (selection.task_id, selection.task_index)
        if key not in ledger.started_tasks:
            missing.append({"stage": "task_start", "task_id": selection.task_id, "task_index": selection.task_index})
        if not any((d.task_id, d.task_index) == key for d in ledger.deliveries.values()):
            missing.append({"stage": "producer_delivery", "task_id": selection.task_id, "task_index": selection.task_index})
    return missing


def replay_ledger_events(
    events: Iterable[Mapping[str, Any]],
    *,
    allow_incomplete: bool = False,
    require_nonempty: bool = True,
) -> ReplayResult:
    """Validate and replay serialized protocol events.

    ``allow_incomplete`` is intended for crash/timeout diagnostics.  It returns
    ``UNKNOWN`` with explicit missing stages, while preserving all integrity and
    causal-order checks.  For a learning update or benchmark score callers must
    leave it false, which turns missing terminal evidence into an error.
    """
    records = list(events)
    if require_nonempty and not records:
        if not allow_incomplete:
            raise LedgerReplayError("empty_ledger", "at least one event is required")
        # A process may time out before selection and therefore leave no
        # append-only record at all. Preserve that as an explicit UNKNOWN
        # diagnostic; callers must opt into this path and cannot use it for a
        # learning update or score.
        empty_ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
        return ReplayResult(
            status="UNKNOWN",
            complete=False,
            event_count=0,
            missing=({"stage": "peer_selection"},),
            snapshot=empty_ledger.snapshot(),
            ledger=empty_ledger,
        )
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    previous = "GENESIS"
    seen_ids: set[tuple[str, str, str]] = set()
    started: set[tuple[str, int]] = set()
    delivered_for_episode: set[tuple[str, int]] = set()

    for index, record in enumerate(records):
        event_type, payload = _validate_record_shape(record, index)
        if record["previous_hash"] != previous:
            raise _record_error(index, "hash_chain_break", "previous_hash does not match the preceding record")
        expected_hash = _hash_payload({
            "event_type": event_type,
            "payload": dict(payload),
            "previous_hash": record["previous_hash"],
        })
        if record["record_hash"] != expected_hash:
            raise _record_error(index, "record_hash_mismatch", "record_hash does not cover the serialized record")

        if event_type == TASK_START:
            if set(payload) != {"task_id", "task_index"}:
                raise _record_error(index, "malformed_payload", "task_start payload must contain task_id and task_index")
            task_id, task_index = payload["task_id"], payload["task_index"]
            if not isinstance(task_id, str) or not task_id:
                raise _record_error(index, "malformed_payload", "task_id must be a non-empty string")
            if not isinstance(task_index, int) or isinstance(task_index, bool) or task_index < 0:
                raise _record_error(index, "malformed_payload", "task_index must be a non-negative integer")
            key = (task_id, task_index)
            if key in started:
                raise _record_error(index, "duplicate_task_start", f"task episode {key!r} started twice")
            # A task cannot start before its selection in the strict protocol;
            # PeerRoleLedger enforces this too, but checking here makes the
            # causal reason visible to the parent validator.
            if not any((s.task_id, s.task_index) == key for s in ledger.selections.values()):
                raise _record_error(index, "out_of_order", "task_start requires an earlier peer_selection")
            try:
                ledger.record_task_start(task_id, task_index)
            except Exception as exc:  # normalize protocol errors for callers
                raise _record_error(index, "protocol_violation", str(exc)) from exc
            started.add(key)
        else:
            method, constructor, id_field = EVENT_CONSTRUCTORS[event_type]
            if id_field not in payload:
                raise _record_error(index, "malformed_payload", f"{event_type} payload lacks {id_field}")
            event_id = payload[id_field]
            identity = (event_type, id_field, str(event_id))
            if identity in seen_ids:
                raise _record_error(index, "duplicate_event_id", f"{event_type} {event_id!r} appears twice")
            seen_ids.add(identity)
            try:
                value = constructor(**dict(payload))
            except Exception as exc:
                raise _record_error(index, "malformed_payload", str(exc)) from exc
            if event_type == "producer_delivery":
                key = (value.task_id, value.task_index)
                if key not in started:
                    raise _record_error(index, "out_of_order", "producer_delivery requires an earlier task_start")
                if key in delivered_for_episode:
                    raise _record_error(index, "duplicate_delivery", f"task episode {key!r} has multiple deliveries")
                delivered_for_episode.add(key)
            try:
                getattr(ledger, method)(value)
            except Exception as exc:
                message = str(exc)
                code = "out_of_order" if any(token in message for token in ("prior", "before", "requires", "must reference", "must cite")) else "protocol_violation"
                raise _record_error(index, code, message) from exc

        generated = ledger.events[-1]
        if _canonical(generated) != _canonical(dict(record)):
            raise _record_error(index, "replay_mismatch", "protocol replay produced a different event record")
        previous = record["record_hash"]

    missing = _missing_for(ledger)
    if missing and not allow_incomplete:
        raise LedgerReplayError("incomplete_ledger", f"missing required causal stages: {missing}")
    complete = not missing
    return ReplayResult(
        status="PASS" if complete else "UNKNOWN",
        complete=complete,
        event_count=len(records),
        missing=tuple(missing),
        snapshot=ledger.snapshot(),
        ledger=ledger,
    )


def replay_ledger_file(path: str | Path, **kwargs: Any) -> ReplayResult:
    """Read a JSON ledger array and validate it."""
    source = Path(path)
    try:
        value = json.loads(source.read_text())
    except Exception as exc:
        raise LedgerReplayError("invalid_json", str(exc)) from exc
    if not isinstance(value, list):
        raise LedgerReplayError("invalid_json", "ledger file must contain a JSON array")
    return replay_ledger_events(value, **kwargs)


# Explicit alias for callers that prefer validator terminology.
validate_ledger_events = replay_ledger_events


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--allow-incomplete", action="store_true", help="return UNKNOWN for missing causal stages")
    args = parser.parse_args(argv)
    try:
        result = replay_ledger_file(args.ledger, allow_incomplete=args.allow_incomplete)
    except LedgerReplayError as exc:
        print(json.dumps({"status": "INVALID", "code": exc.code, "index": exc.index, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
