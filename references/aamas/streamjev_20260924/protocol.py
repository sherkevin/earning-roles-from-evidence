"""Shared event contract for peer/tool Stream-JEV experiments.

The contract is deliberately dependency-free so it can be used by a local
runner, RLinf Channel, ROLL rollout, or an offline replay. Hidden truth and
unselected outputs are rejected from the pre-action state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


# A field name such as ``label`` or ``tool_output`` is not itself leakage: a
# previously selected tool may legitimately return a label or output that is
# visible on the next decision.  The adapter must attach such observations to
# the selected source event.  These names are reserved for hidden correctness
# signals or outputs that were not legally observed.
POST_ACTION_KEYS = {
    "reward", "truth", "ground_truth", "reference_label", "oracle_label",
    "correctness", "correctness_label", "feedback_label", "selected_truth",
    "unselected_output", "future_output", "hidden_output", "future_event",
}


def _reject_hidden(value: Any, path: str = "state") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in POST_ACTION_KEYS:
                raise ValueError(f"post-action field {path}.{key} is not allowed")
            _reject_hidden(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_hidden(child, f"{path}[{index}]")


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    kind: str
    version: str
    description: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionEvent:
    event_id: str
    episode_id: str
    decision_type: str
    context: Mapping[str, Any]
    candidates: Tuple[Candidate, ...]
    chosen_id: str
    propensity: float
    state_version: str
    observed_at: float

    def __post_init__(self) -> None:
        if self.decision_type not in {"select", "verify", "final"}:
            raise ValueError(f"unsupported decision_type={self.decision_type}")
        _reject_hidden(self.context)
        ids = [c.candidate_id for c in self.candidates]
        if len(ids) != len(set(ids)) or self.chosen_id not in ids:
            raise ValueError("chosen candidate must be unique and present in menu")
        if not (0.0 < self.propensity <= 1.0):
            raise ValueError("propensity must be in (0, 1]")


@dataclass(frozen=True)
class FeedbackEvent:
    feedback_id: str
    source_event_id: str
    label: float
    arrived_at: float
    delay: float
    truth_status: str = "arrived"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.truth_status not in {"arrived", "pending", "unavailable"}:
            raise ValueError(f"unsupported truth_status={self.truth_status}")
        if self.delay < 0:
            raise ValueError("delay must be non-negative")


@dataclass(frozen=True)
class StateSnapshot:
    selector_id: str
    version: str
    created_at: float
    payload: Mapping[str, Any]


def candidate_tuple(candidates: Iterable[Candidate]) -> Tuple[Candidate, ...]:
    result = tuple(candidates)
    if not result:
        raise ValueError("candidate menu cannot be empty")
    return result
