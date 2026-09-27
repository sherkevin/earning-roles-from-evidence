"""Versioned public sidecars needed to feed BaselinePolicy without defaults.

The causal ledger remains the source of selection/delivery/judgment/action
events.  A sidecar adds only the public, policy-time fields that the ledger
does not currently carry.  Every sidecar is bound to the corresponding ledger
record hash; missing or UNKNOWN fields are rejected instead of being filled
with a convenient default.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Mapping, Sequence

from peerrolebench_baseline_policies import BaselinePolicy, CandidateRef, Feedback, Selection


SIDECAR_VERSION = "peerrole-policy-sidecar-v2"
HASH_LENGTH = 64
SOURCES = frozenset({"recipient_judgment", "terminal_outcome"})
DISPOSITIONS = frozenset({"eligible", "pending", "unknown", "rejected"})
PROVENANCE = frozenset({"public", "unknown"})
ACTIONS = frozenset({"none", "accept", "rework", "reject", "use", "repair", "redo"})


def _digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _require_digest(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) != HASH_LENGTH or value != value.lower():
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
class DecisionSidecar:
    """Public decision snapshot bound to one serialized ledger selection."""

    ledger_record_hash: str
    protocol_event_type: str
    protocol_event_id: str
    task_id: str
    task_index: int
    role: str
    event_id: str
    selector_id: str
    context_key: str
    candidates: tuple[CandidateRef, ...]
    base_scores: tuple[float, ...]
    chosen_index: int
    probabilities: tuple[float, ...]
    propensity: float
    state_version: str
    encoder_version: str
    feature_schema: str
    policy_name: str
    policy_version: str
    base_score_version: str
    rng_algorithm: str
    rng_draw: int
    selected_at: float
    captured_features: tuple[tuple[str, tuple[float, ...]], ...] = ()
    sidecar_version: str = SIDECAR_VERSION

    def __post_init__(self) -> None:
        _require_digest(self.ledger_record_hash, "ledger_record_hash")
        if self.protocol_event_type != "peer_selection":
            raise ValueError("decision sidecar must reference a peer_selection event")
        if not self.protocol_event_id or not self.task_id or not self.role:
            raise ValueError("protocol event, task and role identifiers are required")
        if int(self.task_index) < 0:
            raise ValueError("task_index must be non-negative")
        if not self.event_id or not self.selector_id or not self.context_key:
            raise ValueError("event, selector and context identifiers are required")
        if self.sidecar_version != SIDECAR_VERSION:
            raise ValueError("unsupported sidecar version")
        if not self.candidates or len(self.candidates) != len(self.base_scores):
            raise ValueError("candidates and base_scores must be aligned")
        if len({candidate.key for candidate in self.candidates}) != len(self.candidates):
            raise ValueError("candidate keys must be unique")
        if not (0 <= int(self.chosen_index) < len(self.candidates)):
            raise ValueError("chosen_index is outside the candidate menu")
        if len(self.probabilities) != len(self.candidates):
            raise ValueError("probabilities and candidates must be aligned")
        tuple(_finite(value, "base_score") for value in self.base_scores)
        probabilities = tuple(_finite(value, "probability") for value in self.probabilities)
        if any(value < 0.0 for value in probabilities) or not math.isclose(sum(probabilities), 1.0, abs_tol=1e-9):
            raise ValueError("probabilities must be non-negative and sum to one")
        propensity = _finite(self.propensity, "propensity")
        if not 0.0 < propensity <= 1.0:
            raise ValueError("propensity must be in (0,1]")
        if not math.isclose(propensity, probabilities[self.chosen_index], abs_tol=1e-12):
            raise ValueError("propensity must equal chosen probability")
        if not all((self.state_version, self.encoder_version, self.feature_schema,
                    self.policy_name, self.policy_version, self.base_score_version,
                    self.rng_algorithm)):
            raise ValueError("state/model/schema/policy versions are required")
        if int(self.rng_draw) < 0:
            raise ValueError("rng_draw must be non-negative")
        if _finite(self.selected_at, "selected_at") < 0.0:
            raise ValueError("selected_at must be non-negative")
        candidate_keys = {candidate.key for candidate in self.candidates}
        for key, vector in self.captured_features:
            if key not in candidate_keys or not vector or not all(math.isfinite(float(value)) for value in vector):
                raise ValueError("captured_features must be finite vectors keyed by candidates")

    def to_selection(self) -> Selection:
        return Selection(
            event_id=self.event_id, context_key=self.context_key, selector_id=self.selector_id,
            candidates=self.candidates, base_scores=self.base_scores, chosen_index=self.chosen_index,
            probabilities=self.probabilities, propensity=self.propensity,
            state_version=self.state_version, encoder_version=self.encoder_version,
            feature_schema=self.feature_schema, selected_at=self.selected_at,
            captured_features=self.captured_features,
        )

    def payload(self) -> dict[str, Any]:
        return {
            "sidecar_version": self.sidecar_version,
            "ledger_record_hash": self.ledger_record_hash, "protocol_event_type": self.protocol_event_type,
            "protocol_event_id": self.protocol_event_id, "task_id": self.task_id,
            "task_index": self.task_index, "role": self.role,
            "event_id": self.event_id,
            "selector_id": self.selector_id,
            "context_key": self.context_key,
            "candidates": [{"candidate_id": c.candidate_id, "candidate_version": c.candidate_version} for c in self.candidates],
            "base_scores": list(self.base_scores), "chosen_index": self.chosen_index,
            "probabilities": list(self.probabilities), "propensity": self.propensity,
            "state_version": self.state_version, "encoder_version": self.encoder_version,
            "feature_schema": self.feature_schema, "policy_name": self.policy_name,
            "policy_version": self.policy_version, "base_score_version": self.base_score_version,
            "rng_algorithm": self.rng_algorithm, "rng_draw": self.rng_draw,
            "selected_at": self.selected_at,
            "captured_features": {key: list(values) for key, values in self.captured_features},
        }

    @property
    def sidecar_digest(self) -> str:
        return _digest(self.payload())


@dataclass(frozen=True)
class FeedbackSidecar:
    """Public feedback snapshot bound to one ledger event."""

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
    source: str
    arrived_at: float
    delay: float
    action: str
    disposition: str
    provenance: str
    label_mapping_version: str
    mapping_digest: str
    responsibility_status: str
    attribution_basis: str
    raw_value: Any | None = None
    label: float | None = None
    sidecar_version: str = SIDECAR_VERSION

    def __post_init__(self) -> None:
        _require_digest(self.ledger_record_hash, "ledger_record_hash")
        if self.protocol_event_type not in {"recipient_judgment", "terminal_outcome"}:
            raise ValueError("feedback sidecar must reference judgment or terminal outcome")
        if not self.protocol_event_id or not self.feedback_id or not self.source_event_id:
            raise ValueError("feedback identifiers are required")
        if (not self.selection_event_id or not self.delivery_id or not self.producer_id
                or not self.producer_version or not self.recipient_id):
            raise ValueError("feedback lineage identifiers are required")
        if self.sidecar_version != SIDECAR_VERSION:
            raise ValueError("unsupported sidecar version")
        if self.source not in SOURCES or self.action not in ACTIONS:
            raise ValueError("unsupported feedback source/action")
        if self.disposition not in DISPOSITIONS or self.provenance not in PROVENANCE:
            raise ValueError("unsupported feedback disposition/provenance")
        if _finite(self.arrived_at, "arrived_at") < 0 or _finite(self.delay, "delay") < 0:
            raise ValueError("feedback time values must be non-negative")
        if self.disposition == "eligible" and self.provenance == "public":
            if not self.label_mapping_version or not self.mapping_digest:
                raise ValueError("eligible public feedback requires label mapping version and digest")
            _require_digest(self.mapping_digest, "mapping_digest")
            if self.responsibility_status != "attributed" or not self.attribution_basis:
                raise ValueError("eligible public feedback requires attributed responsibility")
            if self.label is None or not 0.0 <= _finite(self.label, "label") <= 1.0:
                raise ValueError("eligible public feedback requires a label in [0,1]")
        elif self.label is not None:
            raise ValueError("ineligible or non-public feedback cannot carry a label")

    def to_feedback(self) -> Feedback | None:
        if self.disposition != "eligible" or self.provenance != "public":
            return None
        return Feedback(
            feedback_id=self.feedback_id, source_event_id=self.source_event_id,
            source=self.source, label=float(self.label), arrived_at=self.arrived_at,
            delay=self.delay, action=self.action, disposition=self.disposition,
            provenance=self.provenance,
        )

    def payload(self) -> dict[str, Any]:
        return {
            "sidecar_version": self.sidecar_version, "ledger_record_hash": self.ledger_record_hash,
            "protocol_event_type": self.protocol_event_type, "protocol_event_id": self.protocol_event_id,
            "feedback_id": self.feedback_id, "source_event_id": self.source_event_id,
            "selection_event_id": self.selection_event_id, "delivery_id": self.delivery_id,
            "producer_id": self.producer_id, "producer_version": self.producer_version,
            "recipient_id": self.recipient_id,
            "source": self.source, "arrived_at": self.arrived_at, "delay": self.delay,
            "action": self.action, "disposition": self.disposition,
            "provenance": self.provenance, "label_mapping_version": self.label_mapping_version,
            "mapping_digest": self.mapping_digest, "responsibility_status": self.responsibility_status,
            "attribution_basis": self.attribution_basis,
            **({"raw_value": self.raw_value} if self.raw_value is not None else {}),
            **({"label": self.label} if self.label is not None else {}),
        }

    @property
    def sidecar_digest(self) -> str:
        return _digest(self.payload())


def bind_to_ledger_record(
    sidecar: Mapping[str, Any],
    ledger_record: Mapping[str, Any],
    *,
    expected_event_type: str | None = None,
    expected_event_id: str | None = None,
) -> None:
    """Require a sidecar to identify the exact sealed ledger event.

    A record hash alone is insufficient for a useful adapter check: a caller
    could accidentally attach a valid sidecar to a different event while still
    pointing at a valid record.  The protocol type and event id therefore have
    to agree with both the sidecar and the canonical event payload.  The
    optional expected values let a runner check the event it is currently
    processing before it accepts the sidecar.
    """

    record_hash = _require_digest(str(ledger_record.get("record_hash", "")), "ledger_record.record_hash")
    if sidecar.get("ledger_record_hash") != record_hash:
        raise ValueError("sidecar is bound to a different ledger record")
    event_type = sidecar.get("protocol_event_type")
    event_id = sidecar.get("protocol_event_id")
    if not isinstance(event_type, str) or not isinstance(event_id, str) or not event_type or not event_id:
        raise ValueError("sidecar protocol event type and id are required")
    if expected_event_type is not None and event_type != expected_event_type:
        raise ValueError("sidecar event type does not match expected event")
    if expected_event_id is not None and event_id != expected_event_id:
        raise ValueError("sidecar event id does not match expected event")

    payload = ledger_record.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("ledger record payload is required for sidecar binding")
    if ledger_record.get("event_type") != event_type:
        raise ValueError("sidecar event type does not match ledger record")
    id_field = {
        "peer_selection": "selection_id",
        "recipient_judgment": "judgment_id",
        "terminal_outcome": "outcome_id",
    }.get(event_type)
    if id_field is None or payload.get(id_field) != event_id:
        raise ValueError("sidecar event id does not match ledger record")

    # Check the stable task identity whenever the event carries it.  We do not
    # invent missing fields for old ledgers; the absence is handled by the
    # bridge audit and keeps this function a strict equality check.
    for field in ("task_id", "task_index"):
        if field in sidecar and field in payload and sidecar[field] != payload[field]:
            raise ValueError(f"sidecar {field} does not match ledger record")


class PolicySidecarBridge:
    """Consume validated sidecars without re-sampling or fabricating labels."""

    def __init__(self, policy: BaselinePolicy) -> None:
        self.policy = policy
        self._selection_event_by_protocol_id: dict[str, str] = {}

    def ingest_selection(
        self,
        sidecar: DecisionSidecar,
        ledger_record: Mapping[str, Any],
    ) -> Selection:
        bind_to_ledger_record(sidecar.payload(), ledger_record,
                              expected_event_type="peer_selection",
                              expected_event_id=sidecar.protocol_event_id)
        if sidecar.protocol_event_id in self._selection_event_by_protocol_id:
            raise ValueError("duplicate sidecar selection protocol event")
        selection = sidecar.to_selection()
        self.policy.ingest_selection(selection)
        self._selection_event_by_protocol_id[sidecar.protocol_event_id] = selection.event_id
        return selection

    def ingest_feedback(
        self,
        sidecar: FeedbackSidecar,
        ledger_record: Mapping[str, Any],
    ) -> bool:
        bind_to_ledger_record(sidecar.payload(), ledger_record,
                              expected_event_type=sidecar.protocol_event_type,
                              expected_event_id=sidecar.protocol_event_id)
        selection_event_id = self._selection_event_by_protocol_id.get(sidecar.selection_event_id)
        if selection_event_id is None:
            raise ValueError("feedback references an unknown protocol selection")
        if sidecar.source_event_id != selection_event_id:
            raise ValueError("feedback source event does not match protocol selection")
        chosen = self.policy._decisions[selection_event_id].chosen
        if (sidecar.producer_id, sidecar.producer_version) != (chosen.candidate_id, chosen.candidate_version):
            raise ValueError("feedback producer does not match selected candidate")
        feedback = sidecar.to_feedback()
        if feedback is None:
            return False
        return self.policy.observe_feedback(feedback)


__all__ = [
    "DecisionSidecar", "FeedbackSidecar", "PolicySidecarBridge", "SIDECAR_VERSION",
    "bind_to_ledger_record",
]
