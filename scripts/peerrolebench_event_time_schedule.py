"""Deterministic global arrival schedule for online policy replay.

Feedback sidecars retain wall-clock metadata for audit, but wall-clock order
is not a reproducible online time axis.  A runner card therefore freezes one
integer ``arrival_index`` per feedback event.  This module validates that
schedule independently; it does not sort an observed stream after the fact.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping


EVENT_TYPES = frozenset({"recipient_judgment", "terminal_outcome"})


@dataclass(frozen=True)
class ArrivalAssignment:
    feedback_id: str
    protocol_event_type: str
    protocol_event_id: str
    source_event_id: str
    arrival_index: int

    def __post_init__(self) -> None:
        if not self.feedback_id or self.protocol_event_type not in EVENT_TYPES:
            raise ValueError("feedback identity and supported event type are required")
        if not self.protocol_event_id or not self.source_event_id:
            raise ValueError("protocol and source event IDs are required")
        if int(self.arrival_index) < 0:
            raise ValueError("arrival_index must be non-negative")

    def payload(self) -> dict[str, Any]:
        return {
            "feedback_id": self.feedback_id,
            "protocol_event_type": self.protocol_event_type,
            "protocol_event_id": self.protocol_event_id,
            "source_event_id": self.source_event_id,
            "arrival_index": int(self.arrival_index),
        }


def _assignment(raw: ArrivalAssignment | Mapping[str, Any]) -> ArrivalAssignment:
    if isinstance(raw, ArrivalAssignment):
        return raw
    if not isinstance(raw, Mapping):
        raise ValueError("arrival schedule rows must be mappings")
    fields = {"feedback_id", "protocol_event_type", "protocol_event_id", "source_event_id", "arrival_index"}
    if set(raw) != fields:
        raise ValueError("arrival schedule row has an unexpected schema")
    return ArrivalAssignment(
        feedback_id=str(raw["feedback_id"]),
        protocol_event_type=str(raw["protocol_event_type"]),
        protocol_event_id=str(raw["protocol_event_id"]),
        source_event_id=str(raw["source_event_id"]),
        arrival_index=int(raw["arrival_index"]),
    )


def validate_schedule(
    rows: Iterable[ArrivalAssignment | Mapping[str, Any]],
    *,
    expected_feedback_ids: Iterable[str] | None = None,
) -> tuple[ArrivalAssignment, ...]:
    """Validate a frozen one-to-one schedule and return arrival order."""

    normalized = tuple(_assignment(row) for row in rows)
    feedback_ids = [row.feedback_id for row in normalized]
    event_keys = [(row.protocol_event_type, row.protocol_event_id) for row in normalized]
    indices = [row.arrival_index for row in normalized]
    if len(set(feedback_ids)) != len(feedback_ids):
        raise ValueError("feedback IDs must be unique")
    if len(set(event_keys)) != len(event_keys):
        raise ValueError("protocol event identities must be unique")
    if len(set(indices)) != len(indices):
        raise ValueError("arrival_index must be unique in schedule v1")
    if expected_feedback_ids is not None and set(feedback_ids) != {str(value) for value in expected_feedback_ids}:
        raise ValueError("arrival schedule does not cover the expected feedback set")
    return tuple(sorted(normalized, key=lambda row: row.arrival_index))


def schedule_digest(rows: Iterable[ArrivalAssignment | Mapping[str, Any]]) -> str:
    """Digest the canonical arrival order, including the explicit time axis."""

    payload = [row.payload() for row in validate_schedule(rows)]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


__all__ = ["ArrivalAssignment", "EVENT_TYPES", "schedule_digest", "validate_schedule"]
