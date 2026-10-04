"""Terminal-only public projection for the canonical PIPE3 adapter.

This module is deliberately independent from ``FeedbackSidecar`` and from the
responsibility-aware ``AttributionGate``.  A terminal label is admissible only
when the sealed ``TerminalOutcome`` record binds to the selected delivery and
candidate.  The projection passed to a policy contains the derived label and
public timing fields; scorer versions, scorer payload digests, artifact bytes,
and operator fields never cross that boundary.

The module is a protocol seam, not a benchmark result or a learned policy.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Mapping

from peerrolebench_baseline_policies import Feedback
from peerrolebench_policy_sidecar import DecisionSidecar, bind_to_ledger_record


TERMINAL_LABEL_MAPPING_VERSION = "terminal-success-v1"


def _digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


TERMINAL_LABEL_MAPPING_DIGEST = _digest({
    "version": TERMINAL_LABEL_MAPPING_VERSION,
    "success": 1.0,
    "failure": 0.0,
})


def _sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or value != value.lower():
        raise ValueError(f"{name} must be a SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be a SHA-256 digest") from exc
    return value


def _finite(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class TerminalOutcomeSidecar:
    """Typed public binding for one canonical terminal outcome.

    ``success`` is copied from the sealed outcome record during projection;
    callers cannot supply an independent policy label.  ``scorer_version``
    and ``score_payload_sha256`` intentionally do not appear in this type.
    """

    ledger_record_hash: str
    protocol_event_type: str
    protocol_event_id: str
    feedback_id: str
    source_event_id: str
    selection_event_id: str
    delivery_id: str
    delivery_record_hash: str
    producer_id: str
    producer_version: str
    success: bool | None
    label_mapping_version: str = TERMINAL_LABEL_MAPPING_VERSION
    mapping_digest: str = TERMINAL_LABEL_MAPPING_DIGEST
    source_index: int = 0
    arrived_at: float = 0.0
    delay: float = 0.0
    disposition: str = "eligible"
    provenance: str = "public"
    action: str = "use"
    arrival_index: int | None = None
    sidecar_version: str = "terminal-only-sidecar-v1"

    def __post_init__(self) -> None:
        _sha(self.ledger_record_hash, "ledger_record_hash")
        if self.protocol_event_type != "terminal_outcome":
            raise ValueError("terminal sidecar must reference a terminal_outcome event")
        required = (
            self.protocol_event_id, self.feedback_id, self.source_event_id,
            self.selection_event_id, self.delivery_id, self.producer_id,
            self.producer_version, self.label_mapping_version,
        )
        if not all(isinstance(value, str) and value for value in required):
            raise ValueError("terminal sidecar identifiers are required")
        _sha(self.delivery_record_hash, "delivery_record_hash")
        if self.label_mapping_version != TERMINAL_LABEL_MAPPING_VERSION:
            raise ValueError("unsupported terminal label mapping")
        if self.mapping_digest != TERMINAL_LABEL_MAPPING_DIGEST:
            raise ValueError("terminal label mapping digest mismatch")
        if type(self.source_index) is not int or self.source_index < 0:
            raise ValueError("source_index must be a non-negative integer")
        if _finite(self.arrived_at, "arrived_at") < 0 or _finite(self.delay, "delay") < 0:
            raise ValueError("terminal timing must be non-negative")
        if self.disposition not in {"eligible", "unknown"}:
            raise ValueError("unsupported terminal disposition")
        if self.provenance not in {"public", "unknown"}:
            raise ValueError("unsupported terminal provenance")
        if self.arrival_index is not None and (
            type(self.arrival_index) is not int or self.arrival_index < 0
        ):
            raise ValueError("arrival_index must be a non-negative integer")
        if self.disposition == "eligible":
            if self.provenance != "public" or type(self.success) is not bool:
                raise ValueError("eligible terminal sidecar requires public success")
        elif self.success is not None:
            raise ValueError("UNKNOWN terminal sidecar cannot carry success")

    @property
    def label(self) -> float | None:
        if self.success is None:
            return None
        return 1.0 if self.success else 0.0

    def payload(self) -> dict[str, Any]:
        """Stable sidecar payload used for audit and duplicate detection."""
        return {
            "sidecar_version": self.sidecar_version,
            "ledger_record_hash": self.ledger_record_hash,
            "protocol_event_type": self.protocol_event_type,
            "protocol_event_id": self.protocol_event_id,
            "feedback_id": self.feedback_id,
            "source_event_id": self.source_event_id,
            "selection_event_id": self.selection_event_id,
            "delivery_id": self.delivery_id,
            "delivery_record_hash": self.delivery_record_hash,
            "producer_id": self.producer_id,
            "producer_version": self.producer_version,
            "success": self.success,
            "label_mapping_version": self.label_mapping_version,
            "mapping_digest": self.mapping_digest,
            "source_index": self.source_index,
            "arrived_at": self.arrived_at,
            "delay": self.delay,
            "disposition": self.disposition,
            "provenance": self.provenance,
            "action": self.action,
            **({"arrival_index": self.arrival_index}
               if self.arrival_index is not None else {}),
        }

    @property
    def sidecar_digest(self) -> str:
        return _digest(self.payload())


@dataclass(frozen=True)
class TerminalOutcomeProjection:
    """Minimal public feedback row consumed by ``BaselinePolicy``."""

    feedback_id: str
    source_event_id: str
    source: str
    candidate_key: str
    evidence_version: str
    source_index: int
    arrived_at: float
    delay: float
    action: str
    disposition: str
    provenance: str
    label: float | None
    arrival_index: int | None = None

    def __post_init__(self) -> None:
        if self.source != "terminal_outcome":
            raise ValueError("terminal projection must use terminal_outcome source")
        if not self.feedback_id or not self.source_event_id or not self.candidate_key:
            raise ValueError("terminal projection identity is required")
        if self.disposition not in {"eligible", "unknown"}:
            raise ValueError("unsupported terminal projection disposition")
        if self.disposition == "eligible":
            if self.provenance != "public" or self.label not in {0.0, 1.0}:
                raise ValueError("eligible terminal projection requires public binary label")
        elif self.label is not None:
            raise ValueError("UNKNOWN terminal projection cannot carry a label")

    def to_feedback(self) -> Feedback | None:
        if self.disposition != "eligible" or self.provenance != "public":
            return None
        assert self.label is not None
        return Feedback(
            feedback_id=self.feedback_id,
            source_event_id=self.source_event_id,
            source=self.source,
            label=float(self.label),
            arrived_at=float(self.arrived_at),
            delay=float(self.delay),
            action=self.action,
            disposition=self.disposition,
            provenance=self.provenance,
            arrival_index=self.arrival_index,
        )

    def public_payload(self) -> dict[str, Any]:
        """Payload visible to the policy; no scorer/private fields."""
        return {
            "feedback_id": self.feedback_id,
            "source_event_id": self.source_event_id,
            "source": self.source,
            "candidate_key": self.candidate_key,
            "evidence_version": self.evidence_version,
            "source_index": self.source_index,
            "arrived_at": self.arrived_at,
            "delay": self.delay,
            "action": self.action,
            "disposition": self.disposition,
            "provenance": self.provenance,
            **({"arrival_index": self.arrival_index}
               if self.arrival_index is not None else {}),
            **({"label": self.label} if self.label is not None else {}),
        }


def _record_payload(record: Mapping[str, Any], event_type: str) -> Mapping[str, Any]:
    if record.get("event_type") != event_type:
        raise ValueError(f"ledger record is not {event_type}")
    payload = record.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("ledger record payload is required")
    return payload


def project_terminal_outcome(
    sidecar: TerminalOutcomeSidecar,
    *,
    selection: DecisionSidecar,
    outcome_record: Mapping[str, Any],
    delivery_record: Mapping[str, Any],
    read_cut: int | None = None,
) -> TerminalOutcomeProjection:
    """Validate native lineage and derive the only admissible terminal label."""
    bind_to_ledger_record(
        sidecar.payload(), outcome_record,
        expected_event_type="terminal_outcome",
        expected_event_id=sidecar.protocol_event_id,
    )
    outcome = _record_payload(outcome_record, "terminal_outcome")
    delivery = _record_payload(delivery_record, "producer_delivery")
    if sidecar.delivery_id != delivery.get("delivery_id"):
        raise ValueError("terminal outcome delivery mismatch")
    delivery_record_hash = delivery_record.get("record_hash")
    if not isinstance(delivery_record_hash, str) or sidecar.delivery_record_hash != delivery_record_hash:
        raise ValueError("terminal outcome delivery record hash mismatch")
    if outcome.get("delivery_id") != sidecar.delivery_id:
        raise ValueError("terminal outcome payload delivery mismatch")
    if sidecar.selection_event_id != selection.protocol_event_id:
        raise ValueError("terminal outcome selection mismatch")
    if sidecar.source_event_id != selection.event_id:
        raise ValueError("terminal outcome source event does not match selection")
    if delivery.get("selection_id") != selection.protocol_event_id:
        raise ValueError("delivery selection mismatch")
    if delivery.get("producer_id") != sidecar.producer_id:
        raise ValueError("terminal outcome producer mismatch")
    chosen = selection.to_selection().chosen
    if (sidecar.producer_id, sidecar.producer_version) != (
        chosen.candidate_id, chosen.candidate_version,
    ):
        raise ValueError("terminal outcome candidate was not selected")
    if sidecar.disposition != "eligible" or sidecar.provenance != "public":
        raise ValueError("terminal outcome is UNKNOWN/ineligible")
    if type(outcome.get("success")) is not bool or sidecar.success != outcome["success"]:
        raise ValueError("terminal outcome success mismatch")
    if read_cut is not None:
        if type(read_cut) is not int or read_cut < 0:
            raise ValueError("read_cut must be a non-negative integer")
        if sidecar.arrival_index is None or sidecar.arrival_index > read_cut:
            raise ValueError("terminal outcome arrives after the frozen read cut")
    return TerminalOutcomeProjection(
        feedback_id=sidecar.feedback_id,
        source_event_id=sidecar.source_event_id,
        source="terminal_outcome",
        candidate_key=f"{sidecar.producer_id}@{sidecar.producer_version}",
        evidence_version=sidecar.label_mapping_version,
        source_index=sidecar.source_index,
        arrived_at=float(sidecar.arrived_at),
        delay=float(sidecar.delay),
        action=sidecar.action,
        disposition="eligible",
        provenance="public",
        label=sidecar.label,
        arrival_index=sidecar.arrival_index,
    )


__all__ = [
    "TERMINAL_LABEL_MAPPING_VERSION", "TERMINAL_LABEL_MAPPING_DIGEST",
    "TerminalOutcomeSidecar", "TerminalOutcomeProjection",
    "project_terminal_outcome",
]
