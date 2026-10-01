"""Typed public role-evidence offer for the two-stage assignment boundary.

`AssignmentEvidenceOffer` is a feedback/updater input whose rows are keyed by
source selection events.  A published role evidence record has a different
identity: it is keyed by the native `RoleEvidenceUpdate` id and may be read by
an assignment policy without invoking a persistent updater.  Keeping the two
schemas separate prevents a lineage id from being mistaken for a feedback
channel or a publication from becoming an implicit training update.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from types import MappingProxyType
from typing import Any, Mapping, Sequence


SCHEMA = "peerrole-role-evidence-offer-v1"
ROLE_EVIDENCE_FIELDS = frozenset({
    "evidence_id", "candidate_key", "role", "source_task_index", "delivery_id",
    "judgment_id", "action_id", "outcome_id", "artifact_sha256", "judgment",
    "action", "outcome_status", "quality_score", "available_index",
})


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _sha(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be a SHA-256 digest") from exc
    return value


@dataclass(frozen=True)
class PublicRoleEvidence:
    evidence_id: str
    candidate_key: str
    role: str
    source_task_index: int
    delivery_id: str
    judgment_id: str
    action_id: str
    outcome_id: str
    artifact_sha256: str
    judgment: str
    action: str
    outcome_status: str
    quality_score: float | None
    available_index: int

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value for value in (
            self.evidence_id, self.candidate_key, self.role, self.judgment,
            self.action, self.outcome_status, self.delivery_id, self.judgment_id,
            self.action_id, self.outcome_id,
        )):
            raise ValueError("public role evidence identity is required")
        if int(self.source_task_index) < 0 or int(self.available_index) < 0:
            raise ValueError("role evidence indices must be non-negative")
        if self.outcome_status not in {"PASS", "FAIL"}:
            raise ValueError("role evidence outcome_status must be PASS or FAIL")
        _sha(self.artifact_sha256, "artifact_sha256")
        if self.quality_score is not None and (
            not math.isfinite(float(self.quality_score)) or not 0.0 <= float(self.quality_score) <= 1.0
        ):
            raise ValueError("role evidence quality_score must be in [0,1]")

    def payload(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "candidate_key": self.candidate_key,
            "role": self.role,
            "source_task_index": int(self.source_task_index),
            "delivery_id": self.delivery_id,
            "judgment_id": self.judgment_id,
            "action_id": self.action_id,
            "outcome_id": self.outcome_id,
            "artifact_sha256": self.artifact_sha256,
            "judgment": self.judgment,
            "action": self.action,
            "outcome_status": self.outcome_status,
            "quality_score": self.quality_score,
            "available_index": int(self.available_index),
        }


@dataclass(frozen=True)
class RoleEvidenceOffer:
    offer_id: str
    offer_record_hash: str
    task_id: str
    task_index: int
    role: str
    context_key: str
    candidate_keys: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    evidence_version: str
    public_evidence: tuple[Mapping[str, Any], ...]
    available_index: int
    bundle_digest: str
    watermark_schema: str = "global-event-index-v1"
    candidate_registry_digest: str | None = None

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value for value in (
            self.offer_id, self.task_id, self.role, self.context_key, self.evidence_version,
        )):
            raise ValueError("role evidence offer identity is required")
        _sha(self.offer_record_hash, "offer_record_hash")
        _sha(self.bundle_digest, "bundle_digest")
        if self.candidate_registry_digest is not None:
            _sha(self.candidate_registry_digest, "candidate_registry_digest")
        if int(self.task_index) < 0 or int(self.available_index) < 0:
            raise ValueError("task_index and available_index must be non-negative")
        if not self.candidate_keys or tuple(sorted(set(self.candidate_keys))) != tuple(self.candidate_keys):
            raise ValueError("candidate_keys must be sorted unique")
        if tuple(sorted(set(self.evidence_ids))) != tuple(self.evidence_ids):
            raise ValueError("evidence_ids must be sorted unique")
        if self.watermark_schema != "global-event-index-v1":
            raise ValueError("unsupported role evidence watermark schema")
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        for row in self.public_evidence:
            if not isinstance(row, Mapping) or set(row) != ROLE_EVIDENCE_FIELDS:
                raise ValueError("role evidence row has private or unknown fields")
            normalized = dict(row)
            if normalized["candidate_key"] not in self.candidate_keys:
                raise ValueError("role evidence candidate is outside the offer menu")
            if normalized["role"] != self.role:
                raise ValueError("role evidence role does not match offer role")
            _sha(str(normalized["artifact_sha256"]), "artifact_sha256")
            if normalized["evidence_id"] in seen or not normalized["evidence_id"]:
                raise ValueError("role evidence ids must be present and unique")
            if int(normalized["source_task_index"]) >= int(self.task_index):
                raise ValueError("role evidence must precede its target task")
            if int(normalized["available_index"]) > int(self.available_index):
                raise ValueError("role evidence availability exceeds offer watermark")
            try:
                json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            except (TypeError, ValueError) as exc:
                raise ValueError("role evidence row must be JSON serializable") from exc
            rows.append(normalized)
            seen.add(str(normalized["evidence_id"]))
        rows.sort(key=lambda item: str(item["evidence_id"]))
        if tuple(sorted(seen)) != tuple(self.evidence_ids):
            raise ValueError("evidence_ids must equal public evidence ids")
        object.__setattr__(self, "public_evidence", tuple(MappingProxyType(row) for row in rows))
        if self.bundle_digest != _digest(self.payload()):
            raise ValueError("bundle_digest does not match canonical role evidence offer")

    def payload(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "offer_id": self.offer_id,
            "task_id": self.task_id,
            "task_index": int(self.task_index),
            "role": self.role,
            "context_key": self.context_key,
            "candidate_keys": list(self.candidate_keys),
            "evidence_ids": list(self.evidence_ids),
            "evidence_version": self.evidence_version,
            "public_evidence": [dict(row) for row in self.public_evidence],
            "available_index": int(self.available_index),
            "watermark_schema": self.watermark_schema,
            "candidate_registry_digest": self.candidate_registry_digest,
        }

    def operator_binding_payload(self) -> dict[str, Any]:
        return {**self.payload(), "offer_record_hash": self.offer_record_hash}


def make_role_evidence_offer(
    *, offer_id: str, task_id: str, task_index: int, role: str, context_key: str,
    candidate_keys: Sequence[str], evidence: Sequence[PublicRoleEvidence],
    evidence_version: str, available_index: int, previous_aux_hash: str = "GENESIS",
    candidate_registry_digest: str | None = None,
) -> RoleEvidenceOffer:
    if not all(isinstance(item, PublicRoleEvidence) for item in evidence):
        raise ValueError("evidence must contain typed PublicRoleEvidence records")
    refs = tuple(candidate_keys)
    rows = tuple(item.payload() for item in evidence)
    ids = tuple(sorted(item.evidence_id for item in evidence))
    payload = {
        "schema": SCHEMA, "offer_id": offer_id, "task_id": task_id,
        "task_index": int(task_index), "role": role, "context_key": context_key,
        "candidate_keys": list(refs), "evidence_ids": list(ids),
        "evidence_version": evidence_version, "public_evidence": list(rows),
        "available_index": int(available_index), "watermark_schema": "global-event-index-v1",
        "candidate_registry_digest": candidate_registry_digest,
    }
    bundle = _digest(payload)
    record = {"record_version": SCHEMA, "previous_aux_hash": previous_aux_hash, **payload}
    return RoleEvidenceOffer(
        offer_id=offer_id,
        offer_record_hash=_digest(record),
        task_id=task_id, task_index=int(task_index), role=role, context_key=context_key,
        candidate_keys=refs, evidence_ids=ids, evidence_version=evidence_version,
        public_evidence=rows, available_index=int(available_index), bundle_digest=bundle,
        candidate_registry_digest=candidate_registry_digest,
    )


def build_role_evidence_from_ledger(
    *, ledger: Any, evidence_id: str, candidate_key: str, role: str,
    target_task_index: int, evidence_version: str, available_index: int,
) -> PublicRoleEvidence:
    """Project one canonical native evidence event into public assignment data.

    The subject and lineage are derived from the ledger, never supplied as
    independent caller claims.  The caller still chooses the versioned
    candidate key, which the runner must bind to the delivery producer id.
    """
    evidence = getattr(ledger, "evidence", {}).get(evidence_id)
    if evidence is None or evidence.outcome_id is None:
        raise ValueError("role evidence must be a known terminal native event")
    judgment = getattr(ledger, "judgments", {}).get(evidence.judgment_id)
    action = getattr(ledger, "actions", {}).get(evidence.action_id)
    if judgment is None or action is None or judgment.delivery_id != action.delivery_id:
        raise ValueError("role evidence lineage is incomplete")
    delivery = getattr(ledger, "deliveries", {}).get(judgment.delivery_id)
    outcome = getattr(ledger, "outcomes", {}).get(evidence.outcome_id)
    if delivery is None or outcome is None or outcome.delivery_id != delivery.delivery_id:
        raise ValueError("role evidence delivery/outcome lineage is invalid")
    if judgment.observed_artifact_sha256 != delivery.artifact_sha256 or action.input_artifact_sha256 != delivery.artifact_sha256:
        raise ValueError("role evidence artifact lineage is invalid")
    if int(delivery.task_index) >= int(target_task_index):
        raise ValueError("role evidence source must precede target task")
    if not candidate_key or not candidate_key.split("@", 1)[0] == delivery.producer_id:
        raise ValueError("role evidence candidate does not match delivery producer")
    return PublicRoleEvidence(
        evidence_id=evidence_id, candidate_key=candidate_key, role=role,
        source_task_index=int(delivery.task_index), delivery_id=delivery.delivery_id,
        judgment_id=judgment.judgment_id, action_id=action.action_id,
        outcome_id=outcome.outcome_id, artifact_sha256=delivery.artifact_sha256,
        judgment=judgment.decision, action=action.action,
        outcome_status="PASS" if outcome.success else "FAIL",
        quality_score=outcome.partial_score, available_index=int(available_index),
    )


__all__ = ["PublicRoleEvidence", "RoleEvidenceOffer", "SCHEMA", "build_role_evidence_from_ledger", "make_role_evidence_offer"]
