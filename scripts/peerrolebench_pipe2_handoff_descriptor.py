"""Typed PIPE2 data-handoff identity for the ADR0049 observation path.

The descriptor is intentionally only an identity/lineage contract.  It does
not score a producer, convert adoption into Y, publish a noisy observation,
or update a policy.  It separates the producer source provenance digest from
the opaque ``artifact/extracted_rows.json`` delivery digest and records where
recipient action snapshots will be supplied by a future runner.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any, Iterable, Mapping


SCHEMA = "pipe2-typed-handoff-v1"
DELIVERY_PATH = "artifact/extracted_rows.json"
DELIVERY_SCHEMA = "pipe2-extracted-rows-v1"
_SHA = re.compile(r"^[0-9a-f]{64}$")


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


@dataclass(frozen=True)
class Pipe2HandoffDescriptor:
    schema: str
    task_id: str
    source_task_index: int
    candidate_key: str
    candidate_source_digest: str
    delivery_path: str
    delivery_schema: str
    delivery_artifact_sha256: str
    producer_contract_digest: str
    recipient_before_manifest_digest: str
    recipient_after_manifest_digest: str
    recipient_changed_paths_digest: str
    judgment_id: str
    action_id: str
    outcome_id: str
    target_task_index: int
    source_read_cut: int
    observation_available_index: int
    policy_update_allowed: bool = False
    producer_credit_allowed: bool = False
    descriptor_digest: str = ""

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.task_id != "PIPE2_data_pipeline":
            raise ValueError("unsupported PIPE2 handoff schema/task")
        if not self.candidate_key or "@" not in self.candidate_key:
            raise ValueError("versioned candidate key is required")
        if self.delivery_path != DELIVERY_PATH or self.delivery_schema != DELIVERY_SCHEMA:
            raise ValueError("PIPE2 delivery path/schema mismatch")
        for name in (
            "candidate_source_digest", "delivery_artifact_sha256", "producer_contract_digest",
            "recipient_before_manifest_digest", "recipient_after_manifest_digest",
            "recipient_changed_paths_digest",
        ):
            _sha(getattr(self, name), name)
        for name in ("judgment_id", "action_id", "outcome_id"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError(f"{name} is required")
        for name in ("source_task_index", "target_task_index", "source_read_cut", "observation_available_index"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.source_task_index >= self.target_task_index:
            raise ValueError("target task must follow source task")
        if self.observation_available_index < self.source_read_cut:
            raise ValueError("observation cannot be available before source read cut")
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
        """The only delivery identity safe to expose to a selector."""
        return {
            "schema": "pipe2-public-delivery-v1",
            "task_id": self.task_id,
            "source_task_index": self.source_task_index,
            "target_task_index": self.target_task_index,
            "candidate_key": self.candidate_key,
            "delivery_path": self.delivery_path,
            "delivery_schema": self.delivery_schema,
            "delivery_artifact_sha256": self.delivery_artifact_sha256,
            "observation_available_index": self.observation_available_index,
            "policy_update_allowed": False,
            "producer_credit_allowed": False,
        }


def make_descriptor(**fields: Any) -> Pipe2HandoffDescriptor:
    """Construct a descriptor after calculating its canonical digest."""
    body = {"schema": SCHEMA, **fields,
            "policy_update_allowed": False, "producer_credit_allowed": False}
    body["descriptor_digest"] = canonical_digest(body)
    return Pipe2HandoffDescriptor(**body)


__all__ = ["DELIVERY_PATH", "DELIVERY_SCHEMA", "Pipe2HandoffDescriptor", "SCHEMA",
           "canonical_digest", "digest_changed_paths", "make_descriptor"]
