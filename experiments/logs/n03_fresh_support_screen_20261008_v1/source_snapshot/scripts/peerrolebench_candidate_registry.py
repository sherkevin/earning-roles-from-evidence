"""Immutable candidate identity registry for versioned peer-selection runs.

The native protocol stores candidate IDs only.  Policy sidecars and replay
need a stable versioned identity, however: a changed source or model
configuration must be a new candidate version rather than an in-place edit.
This module validates the small registry written into a runner card and
provides the canonical digest used by configuration and evidence logs.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Iterable, Mapping

from peerrolebench_baseline_policies import CandidateRef


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: Any, name: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


@dataclass(frozen=True)
class CandidateRegistryEntry:
    """The identity that is allowed to appear in a selection menu."""

    candidate_id: str
    candidate_version: str
    source_digest: str
    model_id: str
    model_config_digest: str

    def __post_init__(self) -> None:
        if not self.candidate_id or not self.candidate_version:
            raise ValueError("candidate_id and candidate_version are required")
        if not self.model_id:
            raise ValueError("model_id is required")
        _digest(self.source_digest, "source_digest")
        _digest(self.model_config_digest, "model_config_digest")

    @property
    def key(self) -> str:
        return f"{self.candidate_id}@{self.candidate_version}"

    def payload(self) -> dict[str, str]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_version": self.candidate_version,
            "source_digest": self.source_digest,
            "model_id": self.model_id,
            "model_config_digest": self.model_config_digest,
        }


def _entry(raw: CandidateRegistryEntry | Mapping[str, Any]) -> CandidateRegistryEntry:
    if isinstance(raw, CandidateRegistryEntry):
        return raw
    if not isinstance(raw, Mapping):
        raise ValueError("candidate registry entries must be mappings")
    allowed = {"candidate_id", "candidate_version", "source_digest", "model_id", "model_config_digest"}
    if set(raw) != allowed:
        raise ValueError("candidate registry entry has an unexpected schema")
    return CandidateRegistryEntry(**{key: str(raw[key]) for key in allowed})


def validate_registry(
    entries: Iterable[CandidateRegistryEntry | Mapping[str, Any]],
    *,
    expected_ids: Iterable[str] | None = None,
) -> tuple[CandidateRegistryEntry, ...]:
    """Validate and return entries in canonical candidate-id order."""

    normalized = tuple(_entry(item) for item in entries)
    if not normalized:
        raise ValueError("candidate registry must not be empty")
    ids = [item.candidate_id for item in normalized]
    keys = [item.key for item in normalized]
    if len(set(ids)) != len(ids):
        raise ValueError("candidate IDs must be unique")
    if len(set(keys)) != len(keys):
        raise ValueError("candidate version keys must be unique")
    if expected_ids is not None and set(ids) != {str(value) for value in expected_ids}:
        raise ValueError("candidate registry IDs do not match the pre-registered menu")
    return tuple(sorted(normalized, key=lambda item: item.candidate_id))


def registry_digest(entries: Iterable[CandidateRegistryEntry | Mapping[str, Any]]) -> str:
    """Return the digest of the canonical validated registry payload."""

    canonical = [item.payload() for item in validate_registry(entries)]
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def candidate_refs(
    candidate_ids: Iterable[str],
    entries: Iterable[CandidateRegistryEntry | Mapping[str, Any]],
) -> tuple[CandidateRef, ...]:
    """Resolve native candidate IDs to sidecar refs using only the registry."""

    registry = {item.candidate_id: item for item in validate_registry(entries)}
    ids = tuple(str(value) for value in candidate_ids)
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("candidate IDs must be non-empty and unique")
    try:
        return tuple(CandidateRef(candidate_id, registry[candidate_id].candidate_version) for candidate_id in ids)
    except KeyError as exc:
        raise ValueError(f"candidate ID is not pre-registered: {exc.args[0]}") from exc


__all__ = ["CandidateRegistryEntry", "candidate_refs", "registry_digest", "validate_registry"]
