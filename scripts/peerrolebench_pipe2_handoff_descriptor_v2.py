"""Typed PIPE2 handoff descriptor v2.

This version extends the historical v1 identity contract without mutating it.
It records explicit recipient judgment and observed action values (including a
possible mismatch), plus a sealed event-reference skeleton.  It is still an
identity/lineage adapter: it never scores a producer, publishes an observation,
or updates a selector.  A real runner must replay the native ledger before
calling this builder.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any, Iterable, Mapping

SCHEMA = "pipe2-typed-handoff-v2"
DELIVERY_PATH = "artifact/extracted_rows.json"
DELIVERY_SCHEMA = "pipe2-extracted-rows-v1"
_SHA = re.compile(r"^[0-9a-f]{64}$")
_JUDGMENTS = frozenset({"accept", "accept_with_rework", "reject_redo"})
_ACTIONS = frozenset({"use", "repair", "independent_redo"})
_OUTCOMES = frozenset({"PASS", "FAIL"})
_EVENT_TYPES = {
    "delivery": "producer_delivery",
    "judgment": "recipient_judgment",
    "action": "consumer_action",
    "outcome": "terminal_outcome",
}


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def digest_changed_paths(paths: Iterable[str]) -> str:
    normalized = tuple(sorted(set(str(path) for path in paths)))
    if any(not path or path.startswith("/") or ".." in path.split("/") for path in normalized):
        raise ValueError("changed paths must be relative and traversal-free")
    return canonical_digest({"schema": "pipe2-changed-paths-v1", "paths": list(normalized)})


def _sha(value: str, name: str) -> str:
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _id(value: str, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} is required")
    return value


def _index(value: int, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


@dataclass(frozen=True)
class Pipe2HandoffDescriptor:
    schema: str
    task_id: str
    source_task_index: int
    candidate_key: str
    candidate_source_digest: str
    delivery_id: str
    delivery_path: str
    delivery_schema: str
    delivery_artifact_sha256: str
    producer_contract_digest: str
    recipient_before_manifest_digest: str
    recipient_after_manifest_digest: str
    recipient_changed_paths_digest: str
    judgment: str
    action: str
    used_artifact: bool
    outcome_status: str
    delivery_event_index: int
    judgment_event_index: int
    action_event_index: int
    outcome_event_index: int
    judgment_id: str
    action_id: str
    outcome_id: str
    judgment_record_hash: str
    action_record_hash: str
    outcome_record_hash: str
    target_task_index: int
    source_read_cut: int
    observation_available_index: int
    policy_update_allowed: bool = False
    producer_credit_allowed: bool = False
    descriptor_digest: str = ""

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.task_id != "PIPE2_data_pipeline":
            raise ValueError("unsupported PIPE2 v2 handoff schema/task")
        if not self.candidate_key or "@" not in self.candidate_key:
            raise ValueError("versioned candidate key is required")
        if self.delivery_path != DELIVERY_PATH or self.delivery_schema != DELIVERY_SCHEMA:
            raise ValueError("PIPE2 delivery path/schema mismatch")
        for name in (
            "candidate_source_digest", "delivery_artifact_sha256", "producer_contract_digest",
            "recipient_before_manifest_digest", "recipient_after_manifest_digest",
            "recipient_changed_paths_digest", "judgment_record_hash", "action_record_hash",
            "outcome_record_hash",
        ):
            _sha(getattr(self, name), name)
        _id(self.delivery_id, "delivery_id")
        for name in ("judgment_id", "action_id", "outcome_id"):
            _id(getattr(self, name), name)
        if self.judgment not in _JUDGMENTS or self.action not in _ACTIONS:
            raise ValueError("judgment/action value is invalid")
        if type(self.used_artifact) is not bool:
            raise ValueError("used_artifact must be boolean")
        if self.outcome_status not in _OUTCOMES:
            raise ValueError("outcome_status must be PASS or FAIL")
        for name in ("source_task_index", "target_task_index", "source_read_cut",
                     "observation_available_index", "delivery_event_index",
                     "judgment_event_index", "action_event_index", "outcome_event_index"):
            _index(getattr(self, name), name)
        if self.source_task_index >= self.target_task_index:
            raise ValueError("target task must follow source task")
        if not (self.delivery_event_index < self.judgment_event_index
                <= self.action_event_index <= self.outcome_event_index):
            raise ValueError("delivery, judgment, action and outcome order is invalid")
        if self.source_read_cut < self.outcome_event_index:
            raise ValueError("source read cut does not contain the source outcome")
        if self.observation_available_index < self.outcome_event_index:
            raise ValueError("observation cannot be available before outcome")
        if self.policy_update_allowed or self.producer_credit_allowed:
            raise ValueError("handoff descriptor cannot authorize update or producer credit")
        if self.descriptor_digest != canonical_digest(self.payload(include_digest=False)):
            raise ValueError("handoff descriptor digest mismatch")

    def payload(self, *, include_digest: bool = True) -> dict[str, Any]:
        row = asdict(self)
        if not include_digest:
            row.pop("descriptor_digest")
        return row

    def public_delivery_payload(self) -> dict[str, Any]:
        """Only delivery identity and timing are safe for a selector."""
        return {
            "schema": "pipe2-public-delivery-v2",
            "task_id": self.task_id,
            "source_task_index": self.source_task_index,
            "target_task_index": self.target_task_index,
            "candidate_key": self.candidate_key,
            "delivery_id": self.delivery_id,
            "delivery_path": self.delivery_path,
            "delivery_schema": self.delivery_schema,
            "delivery_artifact_sha256": self.delivery_artifact_sha256,
            "observation_available_index": self.observation_available_index,
            "policy_update_allowed": False,
            "producer_credit_allowed": False,
        }


def validate_event_records(records: Mapping[str, Mapping[str, Any]], *, fields: Mapping[str, Any]) -> None:
    """Check the runner's sealed event references before descriptor construction.

    This is intentionally structural.  The caller must also run the canonical
    ledger replay; this function does not trust arbitrary IDs as lineage.
    """
    if set(records) != set(_EVENT_TYPES):
        raise ValueError("delivery, judgment, action and outcome event records are required")
    expected_ids = {"delivery": fields["delivery_id"], "judgment": fields["judgment_id"],
                    "action": fields["action_id"], "outcome": fields["outcome_id"]}
    expected_indices = {"delivery": fields["delivery_event_index"],
                       "judgment": fields["judgment_event_index"],
                       "action": fields["action_event_index"],
                       "outcome": fields["outcome_event_index"]}
    for name, expected_type in _EVENT_TYPES.items():
        record = records[name]
        if not isinstance(record, Mapping) or record.get("event_type") != expected_type:
            raise ValueError(f"{name} event type is not bound")
        if record.get("event_index") != expected_indices[name]:
            raise ValueError(f"{name} event index is not bound")
        _sha(record.get("record_hash"), f"{name}.record_hash")
        payload = record.get("payload")
        if not isinstance(payload, Mapping):
            raise ValueError(f"{name} event payload is required")
        id_field = {"delivery": "delivery_id", "judgment": "judgment_id",
                    "action": "action_id", "outcome": "outcome_id"}[name]
        if payload.get(id_field) != expected_ids[name] or payload.get("delivery_id") != fields["delivery_id"]:
            raise ValueError(f"{name} event identity is not bound to delivery")
    if records["judgment"]["payload"].get("decision") != fields["judgment"]:
        raise ValueError("judgment value is not bound to event")
    if records["action"]["payload"].get("action") != fields["action"]:
        raise ValueError("action value is not bound to event")
    success = records["outcome"]["payload"].get("success")
    if type(success) is not bool or ("PASS" if success else "FAIL") != fields["outcome_status"]:
        raise ValueError("outcome status is not bound to event")


def make_descriptor(**fields: Any) -> Pipe2HandoffDescriptor:
    body = {"schema": SCHEMA, **fields,
            "policy_update_allowed": False, "producer_credit_allowed": False}
    body["descriptor_digest"] = canonical_digest(body)
    return Pipe2HandoffDescriptor(**body)


def manifest_digest(files: Mapping[str, str], *, allowed_paths: Iterable[str]) -> str:
    expected = tuple(sorted(set(str(path) for path in allowed_paths)))
    if not expected or set(files) != set(expected) or any(not isinstance(text, str) for text in files.values()):
        raise ValueError("recipient manifest is outside the declared source contract")
    if DELIVERY_PATH in expected:
        raise ValueError("opaque delivery artifact cannot be a source-manifest path")
    if any(path.startswith("/") or ".." in path.split("/") for path in expected):
        raise ValueError("manifest paths must be relative and traversal-free")
    return canonical_digest({"schema": "pipe2-recipient-manifest-v2",
                             "paths": list(expected),
                             "files": {path: files[path] for path in expected}})


def make_descriptor_from_snapshots(
    *, recipient_before: Mapping[str, str], recipient_after: Mapping[str, str],
    recipient_allowed_paths: Iterable[str], event_records: Mapping[str, Mapping[str, Any]],
    **fields: Any,
) -> Pipe2HandoffDescriptor:
    """Construct v2 only from sealed source snapshots and bound native events."""
    allowed = tuple(sorted(set(str(path) for path in recipient_allowed_paths)))
    before_digest = manifest_digest(recipient_before, allowed_paths=allowed)
    after_digest = manifest_digest(recipient_after, allowed_paths=allowed)
    changed = tuple(sorted(path for path in allowed if recipient_before[path] != recipient_after[path]))
    body = {
        **fields,
        "recipient_before_manifest_digest": before_digest,
        "recipient_after_manifest_digest": after_digest,
        "recipient_changed_paths_digest": digest_changed_paths(changed),
    }
    validate_event_records(event_records, fields=body)
    return make_descriptor(**body)


__all__ = ["DELIVERY_PATH", "DELIVERY_SCHEMA", "Pipe2HandoffDescriptor", "SCHEMA",
           "canonical_digest", "digest_changed_paths", "make_descriptor",
           "make_descriptor_from_snapshots", "manifest_digest", "validate_event_records"]
