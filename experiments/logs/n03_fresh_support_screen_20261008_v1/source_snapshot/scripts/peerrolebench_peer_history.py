"""Append-only, responsibility-bound peer history for N03 contract checks.

This is a state/projection seam only.  It makes no policy decision, calls no
model, and has no default expert prior.  A live runner must create entries only
after its sealed assignment and independent later outcome are available.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
import math
import re
from typing import Any, Iterable, Mapping


# v2 closes terminal-only masquerading: a determinate history row must carry
# an actual recipient-judgment label as well as its later outcome.  v1
# snapshots/receipts remain historical and are not rewritten.
SCHEMA = "peer-history-v2"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_PUBLIC = frozenset({
    "artifact", "artifact_sha256", "delivery_digest", "task_id", "task", "gold",
    "expected", "private", "private_text", "rationale", "raw_text", "prompt",
})


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                   ensure_ascii=False, default=str).encode()).hexdigest()


def _sha(value: str, name: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _opaque(value: str, name: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 256:
        raise ValueError(f"{name} must be a bounded opaque identifier")
    return value


@dataclass(frozen=True)
class HistoryCostV1:
    input_tokens: int = 0
    output_tokens: int = 0
    tool_calls: int = 0
    wall_ms: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (("input_tokens", self.input_tokens), ("output_tokens", self.output_tokens),
                            ("tool_calls", self.tool_calls)):
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if not math.isfinite(float(self.wall_ms)) or float(self.wall_ms) < 0:
            raise ValueError("wall_ms must be finite and non-negative")


@dataclass(frozen=True)
class AssignmentSealV1:
    assignment_id: str
    subject_key: str
    role_signature_hash: str
    execution_state_fingerprint: str
    sealed_arrival_index: int
    candidate_registry_digest: str

    def __post_init__(self) -> None:
        _opaque(self.assignment_id, "assignment_id")
        _opaque(self.subject_key, "subject_key")
        _sha(self.role_signature_hash, "role_signature_hash")
        _sha(self.execution_state_fingerprint, "execution_state_fingerprint")
        _sha(self.candidate_registry_digest, "candidate_registry_digest")
        if type(self.sealed_arrival_index) is not int or self.sealed_arrival_index < 0:
            raise ValueError("sealed_arrival_index must be a non-negative integer")

    def payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HistoryEntryV1:
    entry_id: str
    agent_key: str
    subject_key: str
    role_signature_hash: str
    execution_state_fingerprint: str
    delivery_digest: str
    recipient_judgment_id: str
    recipient_judgment_label: float | None
    later_outcome_id: str
    later_outcome_label: float | None
    metric_digest: str
    cost: HistoryCostV1
    arrival_index: int
    assignment_id: str
    status: str

    def __post_init__(self) -> None:
        for name, value in (("entry_id", self.entry_id), ("agent_key", self.agent_key),
                            ("subject_key", self.subject_key), ("recipient_judgment_id", self.recipient_judgment_id),
                            ("later_outcome_id", self.later_outcome_id), ("assignment_id", self.assignment_id)):
            _opaque(value, name)
        _sha(self.role_signature_hash, "role_signature_hash")
        _sha(self.execution_state_fingerprint, "execution_state_fingerprint")
        _sha(self.delivery_digest, "delivery_digest")
        _sha(self.metric_digest, "metric_digest")
        if type(self.arrival_index) is not int or self.arrival_index < 0:
            raise ValueError("arrival_index must be a non-negative integer")
        if self.status not in {"PASS", "FAIL", "UNKNOWN"}:
            raise ValueError("history status must be PASS, FAIL, or UNKNOWN")
        for name, value in (("recipient_judgment_label", self.recipient_judgment_label),
                            ("later_outcome_label", self.later_outcome_label)):
            if value is not None and (not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0):
                raise ValueError(f"{name} must be in [0,1]")
        if self.status == "UNKNOWN" and (self.recipient_judgment_label is not None or self.later_outcome_label is not None):
            raise ValueError("UNKNOWN history entries cannot carry positive labels")
        if self.status in {"PASS", "FAIL"}:
            if self.recipient_judgment_label is None:
                raise ValueError("determinate history entries require a recipient judgment label")
            if self.later_outcome_label is None:
                raise ValueError("determinate history entries require a later outcome label")

    def payload(self) -> dict[str, Any]:
        row = asdict(self)
        row["cost"] = asdict(self.cost)
        return row


class PeerHistoryV1:
    """Mutable append-only history with explicit assignment sealing."""

    def __init__(self, agent_key: str):
        self.agent_key = _opaque(agent_key, "agent_key")
        self._seals: dict[str, AssignmentSealV1] = {}
        self._entries: list[HistoryEntryV1] = []

    @classmethod
    def empty(cls, agent_key: str) -> "PeerHistoryV1":
        return cls(agent_key)

    @property
    def entries(self) -> tuple[HistoryEntryV1, ...]:
        return tuple(self._entries)

    @property
    def seals(self) -> tuple[AssignmentSealV1, ...]:
        return tuple(self._seals.values())

    def seal_assignment(self, seal: AssignmentSealV1) -> None:
        if seal.assignment_id in self._seals:
            raise ValueError("duplicate assignment seal")
        if seal.subject_key != self.agent_key:
            raise ValueError("assignment subject does not match history agent")
        if any(existing.sealed_arrival_index == seal.sealed_arrival_index for existing in self._seals.values()):
            raise ValueError("duplicate assignment seal arrival index")
        if self._seals and seal.sealed_arrival_index <= max(item.sealed_arrival_index for item in self._seals.values()):
            raise ValueError("assignment seals must be append-only in arrival order")
        if self._entries and seal.sealed_arrival_index <= self._entries[-1].arrival_index:
            raise ValueError("assignment seal must follow prior history entries")
        self._seals[seal.assignment_id] = seal

    def append(self, entry: HistoryEntryV1) -> None:
        if entry.agent_key != self.agent_key or entry.subject_key != self.agent_key:
            raise ValueError("history entry subject/agent mismatch")
        if entry.entry_id in {item.entry_id for item in self._entries}:
            raise ValueError("duplicate history entry")
        if entry.assignment_id not in self._seals:
            raise ValueError("history entry requires a prior assignment seal")
        seal = self._seals[entry.assignment_id]
        if (entry.subject_key != seal.subject_key
                or entry.role_signature_hash != seal.role_signature_hash
                or entry.execution_state_fingerprint != seal.execution_state_fingerprint):
            raise ValueError("history entry does not match assignment scope")
        if entry.arrival_index <= seal.sealed_arrival_index:
            raise ValueError("history entry must arrive after assignment seal")
        if self._entries and entry.arrival_index <= self._entries[-1].arrival_index:
            raise ValueError("history entries must be append-only in arrival order")
        lineage = (entry.delivery_digest, entry.recipient_judgment_id, entry.later_outcome_id, entry.assignment_id)
        if any((old.delivery_digest, old.recipient_judgment_id, old.later_outcome_id, old.assignment_id) == lineage
               for old in self._entries):
            raise ValueError("duplicate history lineage")
        self._entries.append(entry)

    def _scopes(self) -> dict[str, dict[str, Any]]:
        scopes: dict[str, dict[str, Any]] = {}
        for entry in self._entries:
            scope = f"{entry.role_signature_hash}:{entry.execution_state_fingerprint}"
            row = scopes.setdefault(scope, {"scope_key": scope, "role_signature_hash": entry.role_signature_hash,
                                            "execution_state_fingerprint": entry.execution_state_fingerprint,
                                            "n_pass": 0, "n_fail": 0, "n_unknown": 0, "cost_sum_wall_ms": 0.0,
                                            "cost_count": 0, "last_arrival": None})
            row[f"n_{entry.status.lower()}"] += 1
            row["cost_sum_wall_ms"] += float(entry.cost.wall_ms)
            row["cost_count"] += 1
            row["last_arrival"] = entry.arrival_index
        for row in scopes.values():
            determinate = row["n_pass"] + row["n_fail"]
            row["smoothed_rate"] = ((row["n_pass"] + 1.0) / (determinate + 2.0)) if determinate else None
            row["cost_mean_wall_ms"] = (row["cost_sum_wall_ms"] / row["cost_count"]) if row["cost_count"] else None
            del row["cost_sum_wall_ms"]; del row["cost_count"]
        return scopes

    def selector_projection(self, *, candidate_key: str | None = None) -> dict[str, Any]:
        """Return only opaque scope statistics visible to a future selector."""
        candidate = candidate_key or self.agent_key
        _opaque(candidate, "candidate_key")
        if candidate.split("@", 1)[0] != self.agent_key:
            raise ValueError("history projection candidate does not match history agent")
        scopes = list(self._scopes().values())
        payload = {
            "schema": SCHEMA, "candidate_key": candidate, "entry_count": len(self._entries),
            "scope_count": len(scopes), "scopes": scopes, "history_digest": self.content_digest(),
            "version": VERSION,
        }
        if _FORBIDDEN_PUBLIC.intersection(payload):
            raise AssertionError("forbidden field leaked into public history projection")
        return payload

    def state_payload(self) -> dict[str, Any]:
        return {"schema": SCHEMA, "version": VERSION, "agent_key": self.agent_key,
                "seals": [seal.payload() for seal in self._seals.values()],
                "entries": [entry.payload() for entry in self._entries], "scopes": self._scopes()}

    def state_digest(self) -> str:
        return _digest(self.state_payload())

    def content_digest(self) -> str:
        """Digest evidence content; empty peer histories are homogeneous."""
        payload = {"schema": SCHEMA, "version": VERSION,
                   "seals": [seal.payload() for seal in self._seals.values()],
                   "entries": [entry.payload() for entry in self._entries],
                   "scopes": self._scopes()}
        return _digest(payload)

    def snapshot(self) -> dict[str, Any]:
        payload = self.state_payload()
        return {**payload, "state_digest": _digest(payload)}

    @classmethod
    def replay(cls, snapshot: Mapping[str, Any]) -> "PeerHistoryV1":
        if not isinstance(snapshot, Mapping) or snapshot.get("schema") != SCHEMA:
            raise ValueError("unsupported peer history snapshot")
        if snapshot.get("version") != VERSION:
            raise ValueError("unsupported peer history version")
        expected = snapshot.get("state_digest")
        payload = {key: snapshot[key] for key in ("schema", "version", "agent_key", "seals", "entries", "scopes") if key in snapshot}
        if expected != _digest(payload):
            raise ValueError("peer history snapshot digest mismatch")
        history = cls(str(snapshot["agent_key"]))
        for raw in snapshot.get("seals", ()):
            history.seal_assignment(AssignmentSealV1(**dict(raw)))
        for raw in snapshot.get("entries", ()):
            row = dict(raw); row["cost"] = HistoryCostV1(**dict(row["cost"]))
            history.append(HistoryEntryV1(**row))
        if snapshot.get("scopes") != history._scopes():
            raise ValueError("peer history aggregate mismatch")
        return history


VERSION = "peer-history-v2"

__all__ = ["AssignmentSealV1", "HistoryCostV1", "HistoryEntryV1", "PeerHistoryV1", "SCHEMA", "VERSION"]
