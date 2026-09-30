"""Strict bridge between versioned policy selections and native peer events.

The native protocol stores bare candidate IDs, while the policy/assignment
sidecar stores ``candidate_id@candidate_version`` keys and a selection time.
This adapter keeps the two representations explicit.  It never infers a
version, reorders a menu, or turns an unknown key into a known candidate.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Iterable, Mapping, Sequence

from peer_role_protocol_20260925 import PeerSelection
from peerrolebench_baseline_policies import CandidateRef
from peerrolebench_candidate_registry import CandidateRegistryEntry, validate_registry


@dataclass(frozen=True)
class VersionedSelectionView:
    """The minimum selection shape required by assignment binding."""

    candidates: tuple[CandidateRef, ...]
    chosen_index: int
    task_index: int
    selected_at: float
    selector_id: str

    def __post_init__(self) -> None:
        if not all(isinstance(item, CandidateRef) for item in self.candidates):
            raise ValueError("selection view candidates must be CandidateRef values")
        if not self.candidates or len({item.key for item in self.candidates}) != len(self.candidates):
            raise ValueError("selection view candidates must be non-empty and unique")
        if type(self.chosen_index) is not int or not 0 <= self.chosen_index < len(self.candidates):
            raise ValueError("selection view chosen_index is outside the candidate menu")
        if type(self.task_index) is not int or self.task_index < 0:
            raise ValueError("selection view task_index must be non-negative")
        if not isinstance(self.selected_at, (int, float)) or not math.isfinite(float(self.selected_at)):
            raise ValueError("selection view selected_at must be finite")
        if float(self.selected_at) < 0.0:
            raise ValueError("selection view selected_at must be non-negative")
        if not self.selector_id:
            raise ValueError("selection view selector_id is required")
        if self.candidates[self.chosen_index].candidate_id == self.selector_id:
            raise ValueError("selector cannot choose itself")

    @property
    def chosen(self) -> CandidateRef:
        return self.candidates[self.chosen_index]

    @property
    def chosen_key(self) -> str:
        return self.chosen.key


def _registry_map(
    registry: Iterable[CandidateRegistryEntry | Mapping[str, Any]],
) -> dict[str, CandidateRegistryEntry]:
    entries = validate_registry(registry)
    return {entry.key: entry for entry in entries}


def versioned_keys_to_native_ids(
    candidate_keys: Sequence[str],
    registry: Iterable[CandidateRegistryEntry | Mapping[str, Any]],
) -> tuple[str, ...]:
    """Resolve exact versioned keys to bare native IDs without reordering."""

    keys = tuple(candidate_keys)
    if not all(isinstance(key, str) and key for key in keys):
        raise ValueError("versioned candidate keys must be non-empty strings")
    if not keys or len(set(keys)) != len(keys):
        raise ValueError("versioned candidate keys must be non-empty and unique")
    by_key = _registry_map(registry)
    unknown = [key for key in keys if key not in by_key]
    if unknown:
        raise ValueError(f"candidate key is not registered at the requested version: {unknown[0]}")
    return tuple(by_key[key].candidate_id for key in keys)


def view_from_native_selection(
    selection: PeerSelection,
    registry: Iterable[CandidateRegistryEntry | Mapping[str, Any]],
    *,
    selected_at: float,
) -> VersionedSelectionView:
    """Attach registry versions and time to one native selection event."""

    if not isinstance(selection, PeerSelection):
        raise ValueError("selection must be a native PeerSelection")
    entries = validate_registry(registry, expected_ids=selection.candidate_ids)
    refs = tuple(CandidateRef(entry.candidate_id, entry.candidate_version) for entry in (
        next(entry for entry in entries if entry.candidate_id == candidate_id)
        for candidate_id in selection.candidate_ids
    ))
    chosen_index = selection.candidate_ids.index(selection.chosen_peer_id)
    return VersionedSelectionView(
        candidates=refs,
        chosen_index=chosen_index,
        task_index=int(selection.task_index),
        selected_at=selected_at,
        selector_id=selection.selector_id,
    )


def view_from_versioned_selection(
    *,
    candidate_keys: Sequence[str],
    chosen_key: str,
    task_index: int,
    selected_at: float,
    selector_id: str,
    registry: Iterable[CandidateRegistryEntry | Mapping[str, Any]],
) -> VersionedSelectionView:
    """Validate a policy selection before it is bound to a native event."""

    by_key = _registry_map(registry)
    keys = tuple(candidate_keys)
    if not all(isinstance(key, str) and key for key in keys):
        raise ValueError("versioned candidate keys must be non-empty strings")
    versioned_keys_to_native_ids(keys, tuple(by_key.values()))
    if chosen_key not in keys:
        raise ValueError("chosen candidate is outside the versioned candidate menu")
    return VersionedSelectionView(
        candidates=tuple(CandidateRef(by_key[key].candidate_id, by_key[key].candidate_version) for key in keys),
        chosen_index=keys.index(chosen_key), task_index=task_index,
        selected_at=selected_at, selector_id=selector_id,
    )


__all__ = [
    "VersionedSelectionView", "versioned_keys_to_native_ids",
    "view_from_native_selection", "view_from_versioned_selection",
]
