#!/usr/bin/env python3
"""Bounded, source-linked model feedback for a future AppWorld peer handoff.

This module is deliberately NOT wired into the frozen A0 v4 runner. The caller
must first persist each full, redacted public_api_call event and its source
record. These functions only render a bounded view of those existing records;
they never claim that a truncated response contains evidence it does not show.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Callable


Scrub = Callable[[Any], Any]
_IDENTIFIER = re.compile(r"[A-Za-z0-9_.-]{1,80}\Z")
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_SOURCE_ID = re.compile(r"p([0-9]+)\.c([0-9]+)\Z")
_PUBLIC_KINDS = {"api_observation", "api_doc"}


class SourceReceiptError(ValueError):
    """The source registry is inconsistent or a lookup is not public."""


def canonical(value: Any) -> str:
    # Match A0 v4's exact response digest convention.
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), default=str)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _utf8_prefix(value: str, budget: int) -> str:
    return value.encode("utf-8")[:max(0, budget)].decode("utf-8", "ignore")


def _utf8_suffix(value: str, budget: int) -> str:
    return value.encode("utf-8")[-max(0, budget):].decode("utf-8", "ignore") if budget else ""


def _record(identifier: str, sources: dict[str, dict[str, Any]],
            expected_world: str, scrub: Scrub) -> tuple[dict[str, Any], Any]:
    if not isinstance(identifier, str) or not _IDENTIFIER.fullmatch(identifier):
        raise SourceReceiptError("Malformed public source ID")
    source = sources.get(identifier)
    if not isinstance(source, dict) or source.get("world") != expected_world:
        raise SourceReceiptError("Public source ID absent or from another world")
    kind, app, api = source.get("kind"), source.get("app"), source.get("api")
    if kind not in _PUBLIC_KINDS or not all(
            isinstance(item, str) and _IDENTIFIER.fullmatch(item) for item in (app, api)):
        raise SourceReceiptError("Source is not a typed public API result")
    if (source.get("method") != "get"
            or (kind == "api_observation" and app in {"api_docs", "supervisor", "admin"})
            or (kind == "api_doc" and (app != "api_docs" or api != "show_api_doc"))):
        raise SourceReceiptError("Source is not a permitted public GET")
    recorded_digest = source.get("response_sha256")
    if not isinstance(recorded_digest, str) or not _DIGEST.fullmatch(recorded_digest):
        raise SourceReceiptError("Source response digest is missing")
    safe_value = scrub(source.get("value"))
    if digest(safe_value) != recorded_digest:
        raise SourceReceiptError("Source value and recorded redacted digest disagree")
    metadata = {"source_id": identifier, "kind": kind, "app": app, "api": api,
                "response_sha256": recorded_digest}
    return metadata, safe_value


def _receipted_ids(rows: list[dict[str, Any]], sources: dict[str, dict[str, Any]],
                   expected_world: str, scrub: Scrub) -> list[str]:
    identifiers: list[str] = []
    seen: set[str] = set()
    for row in rows:
        identifier = row.get("source_id")
        if identifier is None:
            continue
        if row.get("ok") is not True or identifier in seen:
            raise SourceReceiptError("Only unique successful public sources can have receipts")
        metadata, _ = _record(identifier, sources, expected_world, scrub)
        if (row.get("app") != metadata["app"] or row.get("api") != metadata["api"]
                or row.get("response_sha256") != metadata["response_sha256"]):
            raise SourceReceiptError("API audit row and source registry disagree")
        identifiers.append(identifier)
        seen.add(identifier)
    return identifiers


def _exact_span(identifiers: list[str]) -> str | None:
    """Show a range only when EVERY intermediate identifier was observed."""
    if not identifiers:
        return None
    matches = [_SOURCE_ID.fullmatch(identifier) for identifier in identifiers]
    if any(match is None for match in matches):
        return None
    numbers = [(int(match.group(1)), int(match.group(2))) for match in matches if match]
    step = numbers[0][0]
    if any(item[0] != step for item in numbers):
        return None
    calls = sorted(item[1] for item in numbers)
    if calls != list(range(calls[0], calls[-1] + 1)):
        return None
    return f"p{step}.c{calls[0]}..p{step}.c{calls[-1]}"


def _bounded_json(payload: dict[str, Any], max_bytes: int) -> str:
    result = canonical(payload)
    if len(result.encode("utf-8")) > max_bytes:
        raise SourceReceiptError("Minimum receipt metadata exceeds configured byte budget")
    return result


def bounded_observation_feedback(
    observation: str, rows: list[dict[str, Any]],
    sources: dict[str, dict[str, Any]], expected_world: str, scrub: Scrub,
    *, max_bytes: int = 4096,
) -> str:
    """Return one model-visible JSON message of at most ``max_bytes`` UTF-8 bytes.

    The index never embeds public response bodies. A controller can expose
    ``source_index_page`` and ``lookup_public_source`` on demand, after logging.
    """
    if max_bytes < 1024:
        raise ValueError("max_bytes must be at least 1024")
    if not isinstance(observation, str):
        raise TypeError("Native observation must be a string")
    safe_observation = scrub(observation)
    if not isinstance(safe_observation, str):
        raise SourceReceiptError("Scrubber did not return a safe observation string")
    identifiers = _receipted_ids(rows, sources, expected_world, scrub)
    sample_ids = identifiers[:2] + identifiers[max(2, len(identifiers) - 2):]
    samples = [_record(identifier, sources, expected_world, scrub)[0]
               for identifier in sample_ids]
    base = {
        "format": "bounded_public_observation_v1",
        "observation_utf8_bytes": len(safe_observation.encode("utf-8")),
        "observation_sha256": hashlib.sha256(safe_observation.encode("utf-8")).hexdigest(),
        "source_count": len(identifiers),
        "source_id_span_exact": _exact_span(identifiers),
        "source_index_sha256": digest(identifiers),
        "sample_receipts": samples,
        "lookup": "Use controller source_index_page(offset,limit) and "
                  "lookup_public_source(source_id,path); omitted data is not evidence.",
    }
    # Leave enough room for metadata, JSON quoting, and multi-byte characters.
    excerpt_budget = min(2048, max_bytes // 2)
    while True:
        safe_bytes = len(safe_observation.encode("utf-8"))
        if safe_bytes <= excerpt_budget:
            view = {"observation": safe_observation, "observation_truncated": False}
        else:
            part = excerpt_budget // 2
            view = {"observation_prefix": _utf8_prefix(safe_observation, part),
                    "observation_suffix": _utf8_suffix(safe_observation, part),
                    "observation_truncated": True}
        payload = {**base, **view}
        result = canonical(payload)
        if len(result.encode("utf-8")) <= max_bytes:
            return result
        if excerpt_budget > 0:
            excerpt_budget //= 2
        elif samples:
            samples.pop()
        else:
            return _bounded_json(payload, max_bytes)


def source_index_page(
    rows: list[dict[str, Any]], sources: dict[str, dict[str, Any]],
    expected_world: str, scrub: Scrub, *, offset: int = 0, limit: int = 8,
    max_bytes: int = 4096,
) -> str:
    """List a bounded page of exact typed IDs/digests; never response bodies."""
    if not isinstance(offset, int) or offset < 0 or not isinstance(limit, int) or not 1 <= limit <= 8:
        raise ValueError("offset must be nonnegative and limit must be 1..8")
    identifiers = _receipted_ids(rows, sources, expected_world, scrub)
    page = identifiers[offset:offset + limit]
    payload = {"format": "public_source_index_page_v1", "offset": offset,
               "total": len(identifiers), "next_offset": offset + len(page) if offset + len(page) < len(identifiers) else None,
               "sources": [_record(identifier, sources, expected_world, scrub)[0]
                           for identifier in page]}
    return _bounded_json(payload, max_bytes)


def _pointer(value: Any, path: str) -> Any:
    if path == "":
        return value
    if not isinstance(path, str) or not path.startswith("/"):
        raise SourceReceiptError("path must be a JSON Pointer")
    current = value
    for encoded in path[1:].split("/"):
        if re.search(r"~(?![01])", encoded):
            raise SourceReceiptError("Invalid JSON Pointer escape")
        part = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and re.fullmatch(r"0|[1-9][0-9]*", part) and int(part) < len(current):
            current = current[int(part)]
        else:
            raise SourceReceiptError("Pointer absent from cited public result")
    return current


def lookup_public_source(
    source_id: str, path: str, sources: dict[str, dict[str, Any]],
    expected_world: str, scrub: Scrub, *, max_bytes: int = 4096,
) -> str:
    """Get an exact typed source_ref only if the referenced value fits.

    Oversize results have no ``source_ref``; the actor must request a narrower
    pointer. This avoids treating a byte-truncated JSON value as evidence.
    """
    if max_bytes < 512:
        raise ValueError("max_bytes must be at least 512")
    metadata, safe_value = _record(source_id, sources, expected_world, scrub)
    value = _pointer(safe_value, path)
    reference = {"kind": metadata["kind"], "source_id": source_id,
                 "path": path, "value": value}
    payload = {"format": "public_source_lookup_v1", "status": "exact",
               **metadata, "source_ref": reference}
    if len(canonical(payload).encode("utf-8")) <= max_bytes:
        return canonical(payload)
    limited = {"format": "public_source_lookup_v1", "status": "requires_narrower_pointer",
               **metadata, "path": path, "value_type": type(value).__name__,
               "value_utf8_bytes": len(canonical(value).encode("utf-8"))}
    return _bounded_json(limited, max_bytes)
