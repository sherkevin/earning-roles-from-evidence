"""Auxiliary append-only manifest for pre-decision offers and read traces.

Native ``PeerRoleLedger`` events and the native sidecar manifest have a strict
three-event coverage contract.  Assignment offers and consumption
attestations therefore use this separate chain.  The auxiliary chain binds
the operator record hash and attestation digest, checks offer-before-consume
order, and never changes native replay coverage.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping


GENESIS = "GENESIS"
EVENT_TYPES = frozenset({"assignment_evidence_offer", "decision_consumption_attestation"})
HASH_LENGTH = 64


def _hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _digest(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != HASH_LENGTH or value != value.lower():
        raise ValueError(f"{name} must be a SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be a SHA-256 digest") from exc
    return value


def _row_payload(row: Mapping[str, Any], previous_hash: str) -> dict[str, Any]:
    event_type = str(row.get("event_type", ""))
    event_id = str(row.get("event_id", ""))
    offer_id = str(row.get("offer_id", ""))
    decision_event_id = str(row.get("decision_event_id", ""))
    if event_type not in EVENT_TYPES or not event_id or not offer_id:
        raise ValueError("assignment manifest event, event id and offer id are required")
    if event_type == "assignment_evidence_offer":
        if event_id != offer_id or decision_event_id:
            raise ValueError("offer manifest row has invalid identity")
    else:
        if not decision_event_id or event_id != decision_event_id:
            raise ValueError("consumption manifest row has invalid identity")
    record_hash = _digest(row.get("record_hash"), "record_hash")
    attestation_digest = _digest(row.get("attestation_digest"), "attestation_digest")
    return {
        "event_type": event_type,
        "event_id": event_id,
        "offer_id": offer_id,
        "decision_event_id": decision_event_id,
        "record_hash": record_hash,
        "attestation_digest": attestation_digest,
        "previous_hash": previous_hash,
    }


def build_manifest(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Build a canonical auxiliary chain in caller-provided event order."""

    result: list[dict[str, Any]] = []
    previous = GENESIS
    seen: set[tuple[str, str]] = set()
    offered: set[str] = set()
    consumed: set[str] = set()
    for raw in rows:
        payload = _row_payload(raw, previous)
        key = (payload["event_type"], payload["event_id"])
        if key in seen:
            raise ValueError("duplicate assignment manifest event")
        if payload["event_type"] == "decision_consumption_attestation":
            if payload["offer_id"] not in offered:
                raise ValueError("consumption attestation precedes its offer")
            if payload["offer_id"] in consumed:
                raise ValueError("duplicate consumption for offer")
            consumed.add(payload["offer_id"])
        else:
            if payload["offer_id"] in offered:
                raise ValueError("duplicate assignment offer")
            offered.add(payload["offer_id"])
        record = {**payload, "manifest_record_hash": _hash(payload)}
        result.append(record)
        seen.add(key)
        previous = record["manifest_record_hash"]
    return result


def validate_manifest(manifest: Iterable[Mapping[str, Any]], rows: Iterable[Mapping[str, Any]]) -> str:
    """Validate chain, exact row coverage, and offer/consumption order."""

    expected = {}
    for raw in rows:
        payload = _row_payload(raw, GENESIS)
        key = (payload["event_type"], payload["event_id"])
        if key in expected:
            raise ValueError("duplicate assignment manifest source row")
        expected[key] = tuple(payload[field] for field in ("record_hash", "offer_id", "decision_event_id", "attestation_digest"))

    seen: set[tuple[str, str]] = set()
    offered: set[str] = set()
    consumed: set[str] = set()
    previous = GENESIS
    for index, raw in enumerate(manifest):
        required = {"event_type", "event_id", "offer_id", "decision_event_id", "record_hash",
                    "attestation_digest", "previous_hash", "manifest_record_hash"}
        if set(raw) != required:
            raise ValueError(f"assignment manifest record {index} has an unexpected schema")
        if raw["previous_hash"] != previous:
            raise ValueError(f"assignment manifest hash-chain break at record {index}")
        payload = _row_payload(raw, previous)
        key = (payload["event_type"], payload["event_id"])
        if key in seen:
            raise ValueError("duplicate assignment manifest event")
        if raw["manifest_record_hash"] != _hash(payload):
            raise ValueError(f"assignment manifest hash mismatch at record {index}")
        if expected.get(key) != tuple(payload[field] for field in ("record_hash", "offer_id", "decision_event_id", "attestation_digest")):
            raise ValueError(f"assignment manifest coverage mismatch for {key}")
        if payload["event_type"] == "assignment_evidence_offer":
            if payload["offer_id"] in offered:
                raise ValueError("duplicate assignment offer")
            offered.add(payload["offer_id"])
        else:
            if payload["offer_id"] not in offered:
                raise ValueError("consumption attestation precedes its offer")
            if payload["offer_id"] in consumed:
                raise ValueError("duplicate consumption for offer")
            consumed.add(payload["offer_id"])
        seen.add(key)
        previous = raw["manifest_record_hash"]
    if seen != set(expected):
        raise ValueError("assignment manifest does not cover all rows")
    if offered != consumed:
        raise ValueError("every assignment offer must have one consumption attestation")
    return previous


__all__ = ["GENESIS", "EVENT_TYPES", "build_manifest", "validate_manifest"]
