"""Independent append-only attestation for policy sidecars.

The native peer-role protocol intentionally keeps its event payload schema
strict.  A sidecar digest therefore lives in a parallel manifest rather than
being injected into a dataclass payload and invalidating canonical replay.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping


GENESIS = "GENESIS"
HASH_LENGTH = 64
# Assignment offers and consumption attestations live beside native protocol
# events.  They use the same append-only chain so a runner can seal the
# pre-decision input and the decision read trace without changing the native
# ledger dataclasses.  Existing three-event manifests remain valid.
EVENT_TYPES = frozenset({
    "peer_selection", "recipient_judgment", "terminal_outcome",
    "assignment_evidence_offer", "decision_consumption_attestation",
})


def _hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _digest(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != HASH_LENGTH:
        raise ValueError(f"{name} must be a SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be a SHA-256 digest") from exc
    return value


@dataclass(frozen=True)
class ManifestRecord:
    ledger_record_hash: str
    protocol_event_type: str
    protocol_event_id: str
    sidecar_digest: str
    previous_hash: str
    manifest_record_hash: str

    def payload(self) -> dict[str, str]:
        return {
            "ledger_record_hash": self.ledger_record_hash,
            "protocol_event_type": self.protocol_event_type,
            "protocol_event_id": self.protocol_event_id,
            "sidecar_digest": self.sidecar_digest,
            "previous_hash": self.previous_hash,
        }


def build_manifest(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Build a deterministic manifest in the caller-provided canonical order."""

    result: list[dict[str, str]] = []
    previous = GENESIS
    seen: set[tuple[str, str]] = set()
    for row in rows:
        event_type = str(row.get("protocol_event_type", ""))
        event_id = str(row.get("protocol_event_id", ""))
        if event_type not in EVENT_TYPES or not event_id:
            raise ValueError("manifest event type/id is required")
        key = (event_type, event_id)
        if key in seen:
            raise ValueError("duplicate manifest protocol event")
        seen.add(key)
        ledger_hash = _digest(row.get("ledger_record_hash"), "ledger_record_hash")
        sidecar_hash = _digest(row.get("sidecar_digest"), "sidecar_digest")
        payload = {
            "ledger_record_hash": ledger_hash,
            "protocol_event_type": event_type,
            "protocol_event_id": event_id,
            "sidecar_digest": sidecar_hash,
            "previous_hash": previous,
        }
        record_hash = _hash(payload)
        result.append({**payload, "manifest_record_hash": record_hash})
        previous = record_hash
    return result


def validate_manifest(
    manifest: Iterable[Mapping[str, Any]],
    rows: Iterable[Mapping[str, Any]],
) -> str:
    """Validate chain integrity and exact sidecar/event coverage.

    Returns the final manifest root (or ``GENESIS`` for an empty manifest).
    """

    records = list(manifest)
    expected = {
        (str(row.get("protocol_event_type", "")), str(row.get("protocol_event_id", ""))):
        (_digest(row.get("ledger_record_hash"), "ledger_record_hash"),
         _digest(row.get("sidecar_digest"), "sidecar_digest"))
        for row in rows
    }
    seen: set[tuple[str, str]] = set()
    previous = GENESIS
    for index, raw in enumerate(records):
        if set(raw) != {"ledger_record_hash", "protocol_event_type", "protocol_event_id",
                        "sidecar_digest", "previous_hash", "manifest_record_hash"}:
            raise ValueError(f"manifest record {index} has an unexpected schema")
        event_type = raw["protocol_event_type"]
        event_id = raw["protocol_event_id"]
        if event_type not in EVENT_TYPES or not event_id:
            raise ValueError(f"manifest record {index} has an invalid event identity")
        key = (event_type, event_id)
        if key in seen:
            raise ValueError("duplicate manifest protocol event")
        seen.add(key)
        ledger_hash = _digest(raw["ledger_record_hash"], "ledger_record_hash")
        sidecar_hash = _digest(raw["sidecar_digest"], "sidecar_digest")
        if raw["previous_hash"] != previous:
            raise ValueError(f"manifest hash-chain break at record {index}")
        payload = {
            "ledger_record_hash": ledger_hash,
            "protocol_event_type": event_type,
            "protocol_event_id": event_id,
            "sidecar_digest": sidecar_hash,
            "previous_hash": previous,
        }
        if raw["manifest_record_hash"] != _hash(payload):
            raise ValueError(f"manifest record hash mismatch at record {index}")
        if expected.get(key) != (ledger_hash, sidecar_hash):
            raise ValueError(f"manifest coverage mismatch for {key}")
        previous = raw["manifest_record_hash"]
    if seen != set(expected):
        raise ValueError("manifest does not cover all sidecar rows")
    return previous


__all__ = ["GENESIS", "ManifestRecord", "build_manifest", "validate_manifest"]
