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
from peerrolebench_policy_sidecar import DecisionSidecar, FeedbackSidecar


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

    def __post_init__(self) -> None:
        if not self.feedback_id or not self.source_event_id or not self.candidate_key:
            raise ValueError("policy feedback identity is required")
        if self.source not in {"recipient_judgment", "terminal_outcome"}:
            raise ValueError("unsupported policy feedback source")
        if self.source_index < 0 or self.arrived_at < 0 or self.delay < 0:
            raise ValueError("feedback timing must be non-negative")
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
            label=float(gate.label),
        )
    return PolicyFeedbackProjection(
        feedback_id=sidecar.feedback_id, source_event_id=sidecar.source_event_id,
        source=sidecar.source, candidate_key=candidate_key,
        evidence_version=gate.evidence_version, source_index=gate.source_index,
        arrived_at=float(sidecar.arrived_at), delay=float(sidecar.delay),
        action=sidecar.action, disposition="unknown", provenance="unknown",
        label=None,
    )


__all__ = ["AttributionGate", "PolicyFeedbackProjection", "project_feedback"]
