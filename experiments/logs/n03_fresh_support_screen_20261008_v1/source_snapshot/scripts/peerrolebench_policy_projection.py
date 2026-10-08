"""Typed operator-to-policy projection for responsibility-aware feedback.

The operator/scorer may retain rich private diagnostics, but a policy receives
only this small projection. This is an information-boundary serialization
contract, not process isolation: the caller must run the operator and policy in
separate trust domains if malicious code is in scope. This module is a seam
contract and mutation-test target; it is not a learned policy or a benchmark
result.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Mapping

from peerrolebench_baseline_policies import Feedback
from peerrolebench_policy_sidecar import (
    DecisionSidecar,
    FeedbackSidecar,
    bind_to_ledger_record,
)


RAW_ACCEPTANCE_MAPPING_VERSION = "raw-acceptance-v1"


def _digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class AttributionGate:
    """Operator-only result used to decide whether a label is attributable."""

    gate_version: str
    ledger_record_hash: str
    sidecar_digest: str
    protocol_event_type: str
    protocol_event_id: str
    source_event_id: str
    delivery_id: str
    producer_id: str
    producer_version: str
    recipient_id: str
    selection_event_id: str
    eligible: bool
    weight: float | None
    label: float | None
    label_mapping_version: str
    evidence_version: str
    source_index: int
    gate_digest: str

    def __post_init__(self) -> None:
        if (not self.gate_version or not self.ledger_record_hash or not self.sidecar_digest
                or not self.protocol_event_type or not self.protocol_event_id
                or not self.source_event_id or not self.delivery_id or not self.producer_id
                or not self.producer_version or not self.recipient_id or not self.selection_event_id):
            raise ValueError("attribution gate identity is required")
        if not self.label_mapping_version or not self.evidence_version:
            raise ValueError("gate versions are required")
        if self.source_index < 0:
            raise ValueError("source_index must be non-negative")
        for name, value in (("ledger_record_hash", self.ledger_record_hash),
                            ("sidecar_digest", self.sidecar_digest),
                            ("gate_digest", self.gate_digest)):
            if len(value) != 64:
                raise ValueError(f"{name} must be a SHA-256 digest")
            try:
                int(value, 16)
            except ValueError as exc:
                raise ValueError(f"{name} must be a SHA-256 digest") from exc
        if self.protocol_event_type not in {"recipient_judgment", "terminal_outcome"}:
            raise ValueError("unsupported attribution event type")
        if self.weight is not None and not 0.0 < float(self.weight) <= 1.0:
            raise ValueError("attribution weight must be positive")
        if self.eligible:
            if self.weight is None or not 0.0 < float(self.weight) <= 1.0:
                raise ValueError("eligible gate requires positive weight")
            if self.label is None or not 0.0 <= float(self.label) <= 1.0:
                raise ValueError("eligible gate requires label in [0,1]")
        elif self.weight is not None or self.label is not None:
            raise ValueError("ineligible gate cannot carry policy label")
        if self.gate_digest != _digest(self.payload()):
            raise ValueError("gate_digest does not match canonical gate payload")

    def payload(self) -> dict[str, Any]:
        """Canonical attestation body; ``gate_digest`` is excluded."""
        return {
            "gate_version": self.gate_version,
            "ledger_record_hash": self.ledger_record_hash,
            "sidecar_digest": self.sidecar_digest,
            "protocol_event_type": self.protocol_event_type,
            "protocol_event_id": self.protocol_event_id,
            "source_event_id": self.source_event_id,
            "delivery_id": self.delivery_id,
            "producer_id": self.producer_id,
            "producer_version": self.producer_version,
            "recipient_id": self.recipient_id,
            "selection_event_id": self.selection_event_id,
            "eligible": self.eligible,
            "weight": self.weight,
            "label": self.label,
            "label_mapping_version": self.label_mapping_version,
            "evidence_version": self.evidence_version,
            "source_index": self.source_index,
        }


@dataclass(frozen=True)
class RawAcceptanceSidecar:
    """Public recipient accept/reject evidence without producer attribution.

    This is deliberately a different type from ``FeedbackSidecar``.  A raw
    acceptance comparator must see a legal recipient decision, but it must not
    read a responsibility gate, producer score, or private scorer label.  The
    canonical judgment ledger record is still required so the projection is
    replayable and cannot invent an acceptance event.
    """

    ledger_record_hash: str
    protocol_event_type: str
    protocol_event_id: str
    feedback_id: str
    source_event_id: str
    selection_event_id: str
    delivery_id: str
    producer_id: str
    producer_version: str
    recipient_id: str
    decision: str
    label_mapping_version: str
    mapping_digest: str
    source_index: int
    arrived_at: float
    delay: float
    arrival_index: int | None = None
    supersedes: str | None = None

    def __post_init__(self) -> None:
        if self.protocol_event_type != "recipient_judgment":
            raise ValueError("raw acceptance must reference a recipient_judgment event")
        required = (
            self.ledger_record_hash, self.protocol_event_id, self.feedback_id,
            self.source_event_id, self.selection_event_id, self.delivery_id,
            self.producer_id, self.producer_version, self.recipient_id,
            self.label_mapping_version, self.mapping_digest,
        )
        if not all(isinstance(value, str) and value for value in required):
            raise ValueError("raw acceptance identity and mapping fields are required")
        for name, value in (("ledger_record_hash", self.ledger_record_hash),
                            ("mapping_digest", self.mapping_digest)):
            if len(value) != 64:
                raise ValueError(f"{name} must be a SHA-256 digest")
            try:
                int(value, 16)
            except ValueError as exc:
                raise ValueError(f"{name} must be a SHA-256 digest") from exc
        if self.label_mapping_version != RAW_ACCEPTANCE_MAPPING_VERSION:
            raise ValueError("unsupported raw acceptance mapping version")
        if self.decision not in {"accept", "reject"}:
            raise ValueError("raw acceptance only accepts accept or reject")
        if self.source_index < 0:
            raise ValueError("source_index must be non-negative")
        if self.arrival_index is not None and (type(self.arrival_index) is not int or self.arrival_index < 0):
            raise ValueError("arrival_index must be a non-negative integer")
        if self.supersedes is not None and (not self.supersedes or self.supersedes == self.feedback_id):
            raise ValueError("supersedes must name a different feedback id")
        for name, value in (("arrived_at", self.arrived_at), ("delay", self.delay)):
            if not math.isfinite(float(value)) or float(value) < 0.0:
                raise ValueError(f"{name} must be non-negative and finite")

    def payload(self) -> dict[str, Any]:
        return {
            "raw_acceptance_version": "raw-acceptance-sidecar-v1",
            "ledger_record_hash": self.ledger_record_hash,
            "protocol_event_type": self.protocol_event_type,
            "protocol_event_id": self.protocol_event_id,
            "feedback_id": self.feedback_id,
            "source_event_id": self.source_event_id,
            "selection_event_id": self.selection_event_id,
            "delivery_id": self.delivery_id,
            "producer_id": self.producer_id,
            "producer_version": self.producer_version,
            "recipient_id": self.recipient_id,
            "decision": self.decision,
            "label_mapping_version": self.label_mapping_version,
            "mapping_digest": self.mapping_digest,
            "source_index": self.source_index,
            "arrived_at": self.arrived_at,
            "delay": self.delay,
            **({"arrival_index": self.arrival_index} if self.arrival_index is not None else {}),
            **({"supersedes": self.supersedes} if self.supersedes is not None else {}),
        }

    @property
    def sidecar_digest(self) -> str:
        return _digest(self.payload())


@dataclass(frozen=True)
class PolicyFeedbackProjection:
    """The complete typed payload visible to an online policy."""

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
    supersedes: str | None = None

    def __post_init__(self) -> None:
        if not self.feedback_id or not self.source_event_id or not self.candidate_key:
            raise ValueError("policy feedback identity is required")
        if self.source not in {"raw_acceptance", "recipient_judgment", "terminal_outcome"}:
            raise ValueError("unsupported policy feedback source")
        if self.source_index < 0 or self.arrived_at < 0 or self.delay < 0:
            raise ValueError("feedback timing must be non-negative")
        if self.arrival_index is not None and (type(self.arrival_index) is not int or self.arrival_index < 0):
            raise ValueError("arrival_index must be a non-negative integer")
        if self.supersedes is not None and (not self.supersedes or self.supersedes == self.feedback_id):
            raise ValueError("supersedes must name a different feedback id")
        if self.disposition not in {"eligible", "unknown"} or self.provenance not in {"public", "unknown"}:
            raise ValueError("unsupported policy feedback disposition")
        if self.disposition == "eligible":
            if self.provenance != "public" or self.label is None:
                raise ValueError("eligible policy feedback requires public label")
            if not 0.0 <= float(self.label) <= 1.0:
                raise ValueError("policy label out of range")
        elif self.label is not None:
            raise ValueError("unknown policy feedback cannot carry label")

    def to_feedback(self) -> Feedback | None:
        if self.disposition != "eligible" or self.provenance != "public":
            return None
        # BaselinePolicy consumes only this typed view; operator gate fields
        # and raw scorer output are intentionally absent.
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
            supersedes=self.supersedes,
        )

    def public_payload(self) -> dict[str, Any]:
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
            **({"arrival_index": self.arrival_index} if self.arrival_index is not None else {}),
            **({"supersedes": self.supersedes} if self.supersedes is not None else {}),
            **({"label": self.label} if self.label is not None else {}),
        }


def project_feedback(
    sidecar: FeedbackSidecar,
    gate: AttributionGate,
    *,
    selection: DecisionSidecar,
) -> PolicyFeedbackProjection:
    """Project rich operator evidence into the minimal policy-visible view."""
    if sidecar.source != sidecar.protocol_event_type:
        raise ValueError("sidecar source and protocol event mismatch")
    if sidecar.disposition != "eligible" or sidecar.provenance != "public":
        if gate.eligible:
            raise ValueError("eligible gate cannot promote non-public sidecar")
    if sidecar.delivery_id != gate.delivery_id:
        raise ValueError("gate and sidecar delivery mismatch")
    if (sidecar.producer_id, sidecar.producer_version) != (gate.producer_id, gate.producer_version):
        raise ValueError("gate and sidecar producer mismatch")
    if gate.eligible and gate.label_mapping_version != sidecar.label_mapping_version:
        raise ValueError("gate and sidecar label mapping mismatch")
    if gate.ledger_record_hash != sidecar.ledger_record_hash:
        raise ValueError("gate and sidecar ledger mismatch")
    if gate.sidecar_digest != sidecar.sidecar_digest:
        raise ValueError("gate and sidecar digest mismatch")
    if (gate.protocol_event_type, gate.protocol_event_id, gate.source_event_id) != (
        sidecar.protocol_event_type, sidecar.protocol_event_id, sidecar.source_event_id
    ):
        raise ValueError("gate and sidecar event mismatch")
    if gate.recipient_id != sidecar.recipient_id:
        raise ValueError("gate and sidecar recipient mismatch")
    if gate.selection_event_id != sidecar.selection_event_id:
        raise ValueError("gate and sidecar selection mismatch")
    if selection.protocol_event_id != sidecar.selection_event_id or selection.event_id != sidecar.source_event_id:
        raise ValueError("feedback is not bound to the supplied selection")
    if selection.to_selection().chosen.key != f"{sidecar.producer_id}@{sidecar.producer_version}":
        raise ValueError("feedback producer was not the selected candidate")
    if gate.eligible and sidecar.label != gate.label:
        raise ValueError("gate and sidecar label mismatch")
    if gate.source_index < 0 or not math.isfinite(float(sidecar.arrived_at)):
        raise ValueError("invalid feedback timing")
    candidate_key = f"{gate.producer_id}@{gate.producer_version}"
    if gate.eligible:
        return PolicyFeedbackProjection(
            feedback_id=sidecar.feedback_id, source_event_id=sidecar.source_event_id,
            source=sidecar.source, candidate_key=candidate_key,
            evidence_version=gate.evidence_version, source_index=gate.source_index,
            arrived_at=float(sidecar.arrived_at), delay=float(sidecar.delay),
            action=sidecar.action, disposition="eligible", provenance="public",
            label=float(gate.label), arrival_index=sidecar.arrival_index,
            supersedes=sidecar.supersedes,
        )
    return PolicyFeedbackProjection(
        feedback_id=sidecar.feedback_id, source_event_id=sidecar.source_event_id,
        source=sidecar.source, candidate_key=candidate_key,
        evidence_version=gate.evidence_version, source_index=gate.source_index,
        arrived_at=float(sidecar.arrived_at), delay=float(sidecar.delay),
        action=sidecar.action, disposition="unknown", provenance="unknown",
        label=None, arrival_index=sidecar.arrival_index,
        supersedes=sidecar.supersedes,
    )


def project_raw_acceptance(
    sidecar: RawAcceptanceSidecar,
    *,
    selection: DecisionSidecar,
    ledger_record: Mapping[str, Any],
) -> PolicyFeedbackProjection:
    """Project only a canonical recipient accept/reject into raw feedback.

    The function intentionally has no attribution gate argument.  It validates
    the public judgment record, selected-candidate identity, and fixed mapping,
    then emits a ``raw_acceptance`` feedback event.  Responsibility-aware
    producer eligibility is therefore neither consumed nor implied.
    """

    bind_to_ledger_record(
        sidecar.payload(), ledger_record,
        expected_event_type="recipient_judgment",
        expected_event_id=sidecar.protocol_event_id,
    )
    payload = ledger_record.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("recipient judgment record payload is required")
    if (payload.get("delivery_id"), payload.get("consumer_id"), payload.get("decision")) != (
        sidecar.delivery_id, sidecar.recipient_id, sidecar.decision
    ):
        raise ValueError("raw acceptance does not match canonical judgment")
    if sidecar.source_event_id != selection.event_id:
        raise ValueError("raw acceptance source event does not match selection")
    if sidecar.selection_event_id != selection.protocol_event_id:
        raise ValueError("raw acceptance selection does not match selection sidecar")
    chosen = selection.to_selection().chosen
    if (sidecar.producer_id, sidecar.producer_version) != (chosen.candidate_id, chosen.candidate_version):
        raise ValueError("raw acceptance producer was not the selected candidate")
    label = 1.0 if sidecar.decision == "accept" else 0.0
    return PolicyFeedbackProjection(
        feedback_id=sidecar.feedback_id,
        source_event_id=sidecar.source_event_id,
        source="raw_acceptance",
        candidate_key=f"{sidecar.producer_id}@{sidecar.producer_version}",
        evidence_version=sidecar.label_mapping_version,
        source_index=sidecar.source_index,
        arrived_at=float(sidecar.arrived_at),
        delay=float(sidecar.delay),
        action=sidecar.decision,
        disposition="eligible",
        provenance="public",
        label=label,
        arrival_index=sidecar.arrival_index,
        supersedes=sidecar.supersedes,
    )


__all__ = [
    "AttributionGate", "PolicyFeedbackProjection", "RAW_ACCEPTANCE_MAPPING_VERSION",
    "RawAcceptanceSidecar", "project_feedback", "project_raw_acceptance",
]
