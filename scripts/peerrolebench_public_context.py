"""Recoverable public task/recipient context candidate, without policy updates.

The caller supplies already-vetted public contract text. Natural language alone
cannot establish that text is free of private facts; this module does not make
that claim. Identity, version and read cut are provenance metadata, never
semantic encoder input. The representation is a comparator candidate, not a
reward contract or a new selection protocol.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping

import numpy as np


SCHEMA_VERSION = "peerrole-public-task-recipient-context-v1"
RADIUS = 1.0 - 1e-12
_FIELDS = frozenset({
    "schema_version", "task_contract", "recipient_contract", "recipient_id",
    "declared_recipient_version", "read_cut", "encoder_version", "max_seq_length",
    "token_counts", "vector", "dimension",
})


def _digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                         allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value


def _count_tokens(tokenizer: Any, text: str, max_seq_length: int) -> int:
    ids = tokenizer.encode(text, add_special_tokens=True, truncation=False)
    if not hasattr(ids, "__len__") or isinstance(ids, (str, bytes)):
        raise ValueError("tokenizer must return complete token ids")
    count = len(ids)
    if count <= 0 or count > max_seq_length:
        raise ValueError("public contract exceeds encoder max_seq_length")
    return count


def encode_public_context(*, task_contract: str, recipient_contract: str,
                          recipient_id: str, declared_recipient_version: str,
                          read_cut: int, tokenizer: Any, encoder: Any,
                          encoder_version: str, max_seq_length: int) -> tuple[tuple[float, ...], dict[str, Any]]:
    """Encode both full public contracts and return a sealed JSON receipt."""
    task = _text(task_contract, "task_contract")
    recipient = _text(recipient_contract, "recipient_contract")
    identity = _text(recipient_id, "recipient_id")
    version = _text(declared_recipient_version, "declared_recipient_version")
    encoder_name = _text(encoder_version, "encoder_version")
    if type(read_cut) is not int or read_cut < 0:
        raise ValueError("read_cut must be a non-negative integer")
    if type(max_seq_length) is not int or max_seq_length <= 0:
        raise ValueError("max_seq_length must be positive")
    native_limit = getattr(encoder, "max_seq_length", None)
    if native_limit is not None and int(native_limit) != max_seq_length:
        raise ValueError("max_seq_length differs from injected encoder")
    counts = {
        "task_contract": _count_tokens(tokenizer, task, max_seq_length),
        "recipient_contract": _count_tokens(tokenizer, recipient, max_seq_length),
    }
    values = np.asarray(encoder.encode([task, recipient], normalize_embeddings=True), dtype=np.float64)
    if values.ndim != 2 or values.shape[0] != 2 or values.shape[1] == 0 or not np.all(np.isfinite(values)):
        raise ValueError("encoder must return two finite non-empty vectors")
    norms = np.linalg.norm(values, axis=1)
    if not np.all(np.isfinite(norms)) or np.any(norms <= 0.0):
        raise ValueError("encoder vectors must have finite nonzero norms")
    scaled = values / norms[:, None] * RADIUS
    vector = tuple(float(x) for x in (np.concatenate((scaled[0], scaled[1])) / math.sqrt(2.0)))
    if not all(math.isfinite(x) for x in vector):
        raise ValueError("context vector must be finite")
    body = {
        "schema_version": SCHEMA_VERSION, "task_contract": task,
        "recipient_contract": recipient, "recipient_id": identity,
        "declared_recipient_version": version, "read_cut": read_cut,
        "encoder_version": encoder_name, "max_seq_length": max_seq_length,
        "token_counts": counts, "vector": list(vector), "dimension": len(vector),
    }
    return vector, {**body, "payload_digest": _digest(body)}


def restore_public_context(receipt: Mapping[str, Any], *, expected_payload_digest: str, read_cut: int,
                           recipient_id: str, declared_recipient_version: str,
                           encoder_version: str | None = None) -> tuple[float, ...]:
    """Verify a separately sealed receipt digest; never re-encode saved features."""
    if not isinstance(receipt, Mapping):
        raise ValueError("context receipt must be a mapping")
    if (not isinstance(expected_payload_digest, str) or len(expected_payload_digest) != 64
            or any(char not in "0123456789abcdef" for char in expected_payload_digest)):
        raise ValueError("expected_payload_digest must be an independently sealed SHA-256")
    body = dict(receipt)
    digest = body.pop("payload_digest", None)
    if (set(body) != _FIELDS or body.get("schema_version") != SCHEMA_VERSION
            or digest != expected_payload_digest or digest != _digest(body)):
        raise ValueError("context receipt digest or schema is invalid")
    if (not isinstance(body["task_contract"], str) or not body["task_contract"].strip()
            or not isinstance(body["recipient_contract"], str) or not body["recipient_contract"].strip()
            or not isinstance(body["recipient_id"], str) or not body["recipient_id"].strip()
            or not isinstance(body["declared_recipient_version"], str)
            or not body["declared_recipient_version"].strip()
            or not isinstance(body["encoder_version"], str) or not body["encoder_version"].strip()
            or type(body["read_cut"]) is not int or body["read_cut"] < 0
            or type(body["max_seq_length"]) is not int or body["max_seq_length"] <= 0):
        raise ValueError("context receipt text, encoder, or bounds are invalid")
    counts = body["token_counts"]
    if (not isinstance(counts, dict) or set(counts) != {"task_contract", "recipient_contract"}
            or any(type(value) is not int or not 0 < value <= body["max_seq_length"]
                   for value in counts.values())):
        raise ValueError("context receipt token counts are invalid")
    if (body["read_cut"] != read_cut or body["recipient_id"] != recipient_id
            or body["declared_recipient_version"] != declared_recipient_version
            or (encoder_version is not None and body["encoder_version"] != encoder_version)):
        raise ValueError("context receipt identity or read cut differs")
    dimension = body["dimension"]
    vector = body["vector"]
    if (type(dimension) is not int or dimension <= 0 or dimension % 2
            or not isinstance(vector, list) or len(vector) != dimension
            or any(type(value) not in (int, float) or not math.isfinite(value) for value in vector)):
        raise ValueError("context receipt vector shape is invalid")
    norm = math.hypot(*vector)
    if not math.isfinite(norm) or norm > 1.0 or not math.isclose(norm, RADIUS,
                                                                 rel_tol=0.0, abs_tol=1e-10):
        raise ValueError("context receipt vector norm is invalid")
    return tuple(float(value) for value in vector)


__all__ = ["SCHEMA_VERSION", "encode_public_context", "restore_public_context"]
