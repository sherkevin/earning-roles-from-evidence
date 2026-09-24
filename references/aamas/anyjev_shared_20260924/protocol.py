"""Dependency-free contract shared by the peer and tool selectors.

AnyJev is the model/runtime layer.  This module only fixes the boundary around
pre-action state and delayed selected-only feedback so the two projects cannot
silently train on different data semantics.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence


SCHEMA_VERSION = "candidate-state-v1"
FEEDBACK_VERSION = "feedback-event-v1"
POST_ACTION_KEYS = frozenset(
    {
        "tool_output",
        "candidate_output",
        "selected_result",
        "artifact_outcome",
        "terminal_reward",
        "label",
        "correctness",
        "accepted",
        "repaired",
    }
)


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _assert_pre_action(value: Any, path: str = "state") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in POST_ACTION_KEYS:
                raise ValueError(f"post-action field {path}.{key} cannot enter pre-action state")
            _assert_pre_action(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for i, child in enumerate(value):
            _assert_pre_action(child, f"{path}[{i}]")


@dataclass(frozen=True)
class Candidate:
    """Versioned tool or peer identity plus information available before acting."""

    kind: str
    provider: str
    name: str
    version: str
    config: Mapping[str, Any] = field(default_factory=dict)
    capability: Mapping[str, Any] = field(default_factory=dict)

    @property
    def uid(self) -> str:
        payload = {"kind": self.kind, "provider": self.provider, "name": self.name,
                   "version": self.version, "config": self.config}
        digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()[:16]
        return f"{self.kind}:{self.provider}:{self.name}:{self.version}:{digest}"

    def to_dict(self) -> dict[str, Any]:
        return {"candidate_kind": self.kind, "provider": self.provider, "name": self.name,
                "version": self.version, "config": dict(self.config),
                "candidate_capability": dict(self.capability), "candidate_uid": self.uid}


@dataclass(frozen=True)
class PreActionState:
    task_type: str
    task_id: str
    task_context: Any
    candidate: Candidate
    history_summary: Any = field(default_factory=dict)
    local_neighbors: tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        value = {
            "schema_version": self.schema_version,
            "task_type": self.task_type,
            "task_id": self.task_id,
            "task_context": self.task_context,
            "candidate": self.candidate.to_dict(),
            "history_summary": self.history_summary,
            "local_neighbors": list(self.local_neighbors),
        }
        _assert_pre_action(value)
        return value

    def context_hash(self) -> str:
        return hashlib.sha256(_canonical(self.to_dict()).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class FeedbackEvent:
    event_id: str
    episode_id: str
    task_type: str
    actor_id: str
    candidate_uid: str
    context_hash: str
    selected: bool
    label: int
    reward_observed_at: str
    feedback_delay_ms: int
    policy_version: str
    propensity: float
    schema_version: str = FEEDBACK_VERSION

    def __post_init__(self) -> None:
        if not self.selected:
            raise ValueError("FeedbackEvent must represent the selected candidate")
        if self.label not in (0, 1):
            raise ValueError("the first protocol version accepts binary labels only")
        if not 0.0 < self.propensity <= 1.0:
            raise ValueError("propensity must be in (0, 1]")
        if self.feedback_delay_ms < 0:
            raise ValueError("feedback_delay_ms must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "episode_id": self.episode_id,
            "task_type": self.task_type,
            "actor_id": self.actor_id,
            "candidate_uid": self.candidate_uid,
            "context_hash": self.context_hash,
            "selected": self.selected,
            "label": self.label,
            "reward_observed_at": self.reward_observed_at,
            "feedback_delay_ms": self.feedback_delay_ms,
            "policy_version": self.policy_version,
            "propensity": self.propensity,
        }


class JevSelector(Protocol):
    def score(self, states: Sequence[PreActionState]) -> Sequence[Mapping[str, Any]]: ...

    def choose(self, states: Sequence[PreActionState]) -> Mapping[str, Any]: ...

    def observe(self, event: FeedbackEvent) -> str: ...

    def snapshot(self) -> Mapping[str, Any]: ...

    def restore(self, snapshot: Mapping[str, Any]) -> None: ...

