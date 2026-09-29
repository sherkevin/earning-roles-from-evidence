"""Typed pre-selection evidence offer and consumption attestation.

The F factor must distinguish an evidence offer that exists in the ledger from
evidence actually read before a policy samples a peer.  This module models an
offer that contains no chosen agent or propensity (those are produced by the
subsequent decision), and an attestation that binds the offer to that decision.
The attestation is an audit seam under a non-adversarial runner; a deterministic
digest is not cryptographic proof against a malicious policy process.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from types import MappingProxyType
from typing import Any, Mapping

from peerrolebench_policy_sidecar import DecisionSidecar


PRIVATE_KEYS = frozenset({
    "raw_value", "responsibility_status", "attribution_basis", "mapping_digest",
    "gate_digest", "operator_status", "producer_score_status",
})
PUBLIC_KEYS = frozenset({
    "feedback_id", "source_event_id", "source", "candidate_key", "evidence_version",
    "source_index", "arrival_index", "arrived_at", "delay", "action", "disposition", "provenance", "label",
    "supersedes",
})
REQUIRED_ROW_KEYS = frozenset({
    "feedback_id", "source_event_id", "source", "candidate_key", "evidence_version",
    "source_index", "arrival_index", "arrived_at", "delay", "action", "disposition", "provenance",
})
ROW_SOURCES = frozenset({"recipient_judgment", "terminal_outcome"})
ROW_DISPOSITIONS = frozenset({"eligible", "pending", "unknown", "rejected", "ineligible"})
ROW_PROVENANCE = frozenset({"public", "unknown"})


def _digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _require_digest(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or value != value.lower():
        raise ValueError(f"{name} must be a SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be a SHA-256 digest") from exc
    return value


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be finite and non-negative")
    return result


@dataclass(frozen=True)
class AssignmentEvidenceOffer:
    """Public evidence available before a selection is produced."""

    offer_id: str
    offer_record_hash: str
    task_id: str
    task_index: int
    role: str
    context_key: str
    candidate_keys: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    evidence_version: str
    public_rows: tuple[Mapping[str, Any], ...]
    available_index: int
    bundle_digest: str
    watermark_schema: str = "global-event-index-v1"

    def __post_init__(self) -> None:
        if not self.offer_id or not self.task_id or not self.role or not self.context_key or not self.evidence_version:
            raise ValueError("offer identity is required")
        _require_digest(self.offer_record_hash, "offer_record_hash")
        if int(self.task_index) < 0 or int(self.available_index) < 0:
            raise ValueError("task_index and available_index must be non-negative")
        if not self.candidate_keys or len(set(self.candidate_keys)) != len(self.candidate_keys):
            raise ValueError("candidate keys must be non-empty and unique")
        if tuple(sorted(set(self.evidence_ids))) != tuple(self.evidence_ids):
            raise ValueError("evidence_ids must be sorted and unique")
        if self.watermark_schema != "global-event-index-v1":
            raise ValueError("unsupported watermark schema")
        normalized_rows = []
        seen_feedback_ids = set()
        seen_source_event_ids = set()
        seen_arrival_indices = set()
        for row in self.public_rows:
            if not isinstance(row, Mapping):
                raise ValueError("public evidence rows must be mappings")
            keys = set(row)
            if keys & PRIVATE_KEYS or not keys <= PUBLIC_KEYS:
                raise ValueError("public evidence row contains private or unknown fields")
            if not REQUIRED_ROW_KEYS <= keys:
                raise ValueError("public evidence row is missing required fields")
            if row["source"] not in ROW_SOURCES or row["disposition"] not in ROW_DISPOSITIONS:
                raise ValueError("public evidence row has unsupported source or disposition")
            if row["provenance"] not in ROW_PROVENANCE:
                raise ValueError("public evidence row has unsupported provenance")
            if row["candidate_key"] not in self.candidate_keys:
                raise ValueError("public evidence row references unknown candidate")
            if row["evidence_version"] != self.evidence_version:
                raise ValueError("public evidence row version mismatch")
            try:
                source_index = int(row["source_index"])
                arrival_index = int(row["arrival_index"])
                arrived_at = float(row["arrived_at"])
                delay = float(row["delay"])
            except (TypeError, ValueError) as exc:
                raise ValueError("public evidence row timing/index must be numeric") from exc
            if (source_index < 0 or arrival_index < 0 or arrival_index > int(self.available_index)
                    or arrived_at < 0 or delay < 0):
                raise ValueError("public evidence row timing/index must be non-negative")
            if row["disposition"] == "eligible" and row["provenance"] == "public":
                if "label" not in keys or not 0.0 <= float(row["label"]) <= 1.0:
                    raise ValueError("eligible public evidence row requires label")
            elif "label" in keys:
                raise ValueError("non-public evidence row cannot carry label")
            if not row.get("feedback_id") or row.get("feedback_id") in seen_feedback_ids:
                raise ValueError("public evidence feedback ids must be present and unique")
            if "supersedes" in keys and (
                not isinstance(row["supersedes"], str) or not row["supersedes"]
                or row["supersedes"] == row["feedback_id"]
            ):
                raise ValueError("supersedes must name a different feedback id")
            # Values are intentionally JSON primitives: this makes the bundle
            # digest independent of mutable nested objects.
            try:
                json.dumps(dict(row), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            except (TypeError, ValueError) as exc:
                raise ValueError("public evidence rows must be JSON serializable") from exc
            if any(isinstance(value, (dict, list, tuple, set)) for value in row.values()):
                raise ValueError("public evidence row values must be scalar")
            if any(isinstance(value, float) and not math.isfinite(value) for value in row.values()):
                raise ValueError("public evidence row numeric values must be finite")
            seen_feedback_ids.add(row["feedback_id"])
            if row["source_event_id"] in seen_source_event_ids and "supersedes" not in keys:
                raise ValueError("public evidence source event ids must be unique")
            seen_source_event_ids.add(row["source_event_id"])
            if row["arrival_index"] in seen_arrival_indices:
                raise ValueError("public evidence arrival indices must be unique")
            seen_arrival_indices.add(row["arrival_index"])
            normalized_rows.append(dict(row))
        normalized_rows.sort(key=lambda row: (int(row["arrival_index"]), str(row["feedback_id"])))
        if tuple(sorted(seen_source_event_ids)) != tuple(self.evidence_ids):
            raise ValueError("evidence_ids must equal public source event ids")
        object.__setattr__(self, "public_rows", tuple(MappingProxyType(row) for row in normalized_rows))
        _require_digest(self.bundle_digest, "bundle_digest")
        if self.bundle_digest != _digest(self.payload()):
            raise ValueError("bundle_digest does not match canonical offer payload")

    def payload(self) -> dict[str, Any]:
        """Canonical public bundle; operator ledger binding is excluded."""
        return {
            "offer_id": self.offer_id,
            "task_id": self.task_id,
            "task_index": self.task_index,
            "role": self.role,
            "context_key": self.context_key,
            "candidate_keys": list(self.candidate_keys),
            "evidence_ids": list(self.evidence_ids),
            "evidence_version": self.evidence_version,
            "public_rows": [dict(row) for row in self.public_rows],
            "available_index": self.available_index,
            "watermark_schema": self.watermark_schema,
        }

    def operator_binding_payload(self) -> dict[str, Any]:
        return {**self.payload(), "offer_record_hash": self.offer_record_hash}

    @property
    def public_bundle_digest(self) -> str:
        return self.bundle_digest


@dataclass(frozen=True)
class DecisionConsumptionAttestation:
    """Evidence-read attestation bound to a later decision snapshot."""

    attestation_version: str
    offer_id: str
    offer_record_hash: str
    bundle_digest: str
    decision_protocol_event_id: str
    decision_event_id: str
    decision_sidecar_digest: str
    policy_state_digest_before: str
    state_version: str
    selector_id: str
    context_key: str
    read_cut: int
    decision_index: int
    policy_input_digest: str
    consumed: bool
    attestation_digest: str
    watermark_schema: str = "global-event-index-v1"

    def __post_init__(self) -> None:
        required = (self.attestation_version, self.offer_id, self.decision_protocol_event_id,
                    self.decision_event_id, self.state_version, self.selector_id, self.context_key)
        if not all(required):
            raise ValueError("consumption attestation identity is required")
        for name, value in (("offer_record_hash", self.offer_record_hash),
                            ("bundle_digest", self.bundle_digest),
                            ("decision_sidecar_digest", self.decision_sidecar_digest),
                            ("policy_state_digest_before", self.policy_state_digest_before),
                            ("policy_input_digest", self.policy_input_digest),
                            ("attestation_digest", self.attestation_digest)):
            _require_digest(value, name)
        if int(self.read_cut) < 0 or int(self.decision_index) < 0:
            raise ValueError("read_cut and decision_index must be non-negative")
        if self.watermark_schema != "global-event-index-v1":
            raise ValueError("unsupported watermark schema")
        if self.consumed and self.read_cut > self.decision_index:
            raise ValueError("evidence read_cut is after decision index")
        if self.attestation_digest != _digest(self.payload()):
            raise ValueError("attestation_digest does not match canonical payload")

    def payload(self) -> dict[str, Any]:
        return {
            "attestation_version": self.attestation_version,
            "offer_id": self.offer_id,
            "offer_record_hash": self.offer_record_hash,
            "bundle_digest": self.bundle_digest,
            "decision_protocol_event_id": self.decision_protocol_event_id,
            "decision_event_id": self.decision_event_id,
            "decision_sidecar_digest": self.decision_sidecar_digest,
            "policy_state_digest_before": self.policy_state_digest_before,
            "state_version": self.state_version,
            "selector_id": self.selector_id,
            "context_key": self.context_key,
            "read_cut": self.read_cut,
            "decision_index": self.decision_index,
            "policy_input_digest": self.policy_input_digest,
            "consumed": self.consumed,
            "watermark_schema": self.watermark_schema,
        }

    @staticmethod
    def expected_input_digest(bundle_digest: str, state_digest: str, read_cut: int) -> str:
        return _digest({"bundle_digest": bundle_digest, "state_digest": state_digest, "read_cut": read_cut})


def build_consumption_attestation(
    offer: AssignmentEvidenceOffer,
    decision: DecisionSidecar,
    *,
    consumed: bool,
    read_cut: int,
    decision_index: int,
) -> DecisionConsumptionAttestation:
    decision_keys = tuple(candidate.key for candidate in decision.candidates)
    if offer.candidate_keys != decision_keys:
        raise ValueError("offer candidate menu does not match decision")
    if offer.context_key != decision.context_key:
        raise ValueError("offer context does not match decision")
    if offer.task_id != decision.task_id or offer.task_index != decision.task_index or offer.role != decision.role:
        raise ValueError("offer task/role does not match decision")
    if decision.state_digest is None:
        raise ValueError("decision must carry policy state digest for attestation")
    if int(read_cut) > int(decision_index):
        raise ValueError("read_cut is after decision index")
    if offer.watermark_schema != "global-event-index-v1":
        raise ValueError("unsupported watermark schema")
    if consumed and int(offer.available_index) > int(read_cut):
        raise ValueError("offer is unavailable at read cut")
    state_digest = decision.state_digest
    body = {
        "attestation_version": "decision-consumption-attestation-v1",
        "offer_id": offer.offer_id,
        "offer_record_hash": offer.offer_record_hash,
        "bundle_digest": offer.bundle_digest,
        "decision_protocol_event_id": decision.protocol_event_id,
        "decision_event_id": decision.event_id,
        "decision_sidecar_digest": decision.sidecar_digest,
        "policy_state_digest_before": state_digest,
        "state_version": decision.state_version,
        "selector_id": decision.selector_id,
        "context_key": decision.context_key,
        "read_cut": int(read_cut),
        "decision_index": int(decision_index),
        "policy_input_digest": DecisionConsumptionAttestation.expected_input_digest(
            offer.bundle_digest if consumed else _digest({"empty_offer": True}), state_digest, int(read_cut)
        ),
        "consumed": bool(consumed),
        "watermark_schema": offer.watermark_schema,
    }
    return DecisionConsumptionAttestation(**body, attestation_digest=_digest(body))


def verify_consumption_attestation(
    attestation: DecisionConsumptionAttestation,
    offer: AssignmentEvidenceOffer,
    decision: DecisionSidecar,
) -> bool:
    """Verify that an offer could have been read before this decision."""
    if attestation.offer_id != offer.offer_id or attestation.offer_record_hash != offer.offer_record_hash:
        raise ValueError("attestation offer identity mismatch")
    if offer.bundle_digest != _digest(offer.payload()):
        raise ValueError("offer bundle digest does not match canonical payload")
    decision_keys = tuple(candidate.key for candidate in decision.candidates)
    if offer.candidate_keys != decision_keys:
        raise ValueError("offer candidate menu does not match decision")
    if offer.task_id != decision.task_id or offer.task_index != decision.task_index or offer.role != decision.role:
        raise ValueError("offer task/role does not match decision")
    if offer.context_key != decision.context_key:
        raise ValueError("offer context does not match decision")
    if attestation.bundle_digest != offer.bundle_digest:
        raise ValueError("attestation bundle digest mismatch")
    if attestation.decision_protocol_event_id != decision.protocol_event_id:
        raise ValueError("attestation decision protocol mismatch")
    if attestation.decision_event_id != decision.event_id or attestation.decision_sidecar_digest != decision.sidecar_digest:
        raise ValueError("attestation decision mismatch")
    if decision.state_digest is None or attestation.policy_state_digest_before != decision.state_digest:
        raise ValueError("attestation policy state mismatch")
    if attestation.state_version != decision.state_version or attestation.selector_id != decision.selector_id:
        raise ValueError("attestation policy identity mismatch")
    if attestation.context_key != decision.context_key:
        raise ValueError("attestation context mismatch")
    if attestation.watermark_schema != offer.watermark_schema:
        raise ValueError("attestation watermark schema mismatch")
    if attestation.read_cut > attestation.decision_index:
        raise ValueError("attestation read cut is after decision")
    expected_bundle = offer.bundle_digest if attestation.consumed else _digest({"empty_offer": True})
    expected = DecisionConsumptionAttestation.expected_input_digest(
        expected_bundle, decision.state_digest, attestation.read_cut
    )
    if attestation.policy_input_digest != expected:
        raise ValueError("attestation policy input digest mismatch")
    if attestation.consumed and offer.available_index > attestation.read_cut:
        raise ValueError("offer was unavailable at the read cut")
    return bool(attestation.consumed)


__all__ = ["AssignmentEvidenceOffer", "DecisionConsumptionAttestation",
           "build_consumption_attestation", "verify_consumption_attestation",
           "PUBLIC_KEYS", "PRIVATE_KEYS"]
