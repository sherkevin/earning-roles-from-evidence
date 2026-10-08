"""DIST1 neutral material v2 with an explicit public queue interface contract."""
from __future__ import annotations

import ast
import copy
import json
from typing import Any

from peerrolebench_dist1_material_adapter import (
    HIDDEN_PATHS,
    ORACLE_PATTERNS,
    PRODUCER_OWNED,
    RECIPIENT_OWNED,
    SUPPORT_READ_ONLY,
    digest_json,
)
from peerrolebench_pipe3_material_adapter import strip_comments_and_docstrings


def neutral_task_text() -> dict[str, str]:
    spec = """# DIST1: Concurrent Message Queue

## Goal
Make the public message queue safe and interoperable under concurrent producer and
consumer load.

## Responsibilities
- The producer owns `mqueue/queue.py` and `mqueue/priority.py` and must preserve the public names and method signatures.
- The recipient owns `mqueue/consumer.py` and must implement its consumer integration.
- `mqueue/__init__.py` and `mqueue/config.py` are read-only support files.

## Public interface contract
- `TaskQueue.put(message)` is non-blocking and raises `QueueFull` when the queue and its in-flight messages reach capacity.
- `TaskQueue.get()` is non-blocking: it returns `None` when empty, otherwise exactly `(message, receipt)`.
- `TaskQueue.ack(receipt)` confirms successful processing and releases the in-flight slot.
- `TaskQueue.nack(receipt)` re-enqueues the unacknowledged message for a later `get()`.
- `PriorityTask` orders lower `urgency` first; equal urgency must use a deterministic non-payload tie-breaker.

## Acceptance
The queue must keep its capacity bound under concurrent insertion, preserve every message
until `ack`, recover messages after `nack`, and order equal-priority items without requiring
payload values to be comparable. A bounded concurrent workload must complete without message
loss. The parent evaluator keeps tests private; inspect the public interfaces and data flow
before editing.
"""
    brief = """# DIST1 concurrent queue task

Repair the assigned component so the public queue and consumer work correctly under
concurrent load. Follow the public interface contract, preserve compatibility, and return
only complete text for files you are allowed to change.
"""
    return {"spec_md": spec, "brief_md": brief}


def build_materials(generated: Any) -> dict[str, Any]:
    if generated.task_id != "DIST1_queue_race":
        raise ValueError(f"unexpected task: {generated.task_id}")
    workspace = dict(generated.workspace_files)
    required = set(PRODUCER_OWNED + RECIPIENT_OWNED + SUPPORT_READ_ONLY + HIDDEN_PATHS)
    if set(workspace) != required:
        raise ValueError(f"unexpected workspace paths: {sorted(set(workspace) ^ required)}")
    public_paths = PRODUCER_OWNED + RECIPIENT_OWNED + SUPPORT_READ_ONLY
    public_sources = {path: strip_comments_and_docstrings(workspace[path]) for path in public_paths}
    for path, source in public_sources.items():
        ast.parse(source, filename=path)
    task_text = neutral_task_text()
    text_blob = "\n".join(task_text.values()).lower()
    source_blob = "\n".join(public_sources.values()).lower()
    text_leaks = [pattern for pattern in ORACLE_PATTERNS if pattern in text_blob]
    source_leaks = [pattern for pattern in ORACLE_PATTERNS if pattern in source_blob]
    producer = {
        "task_id": generated.task_id, "seed": generated.seed, "role": "producer",
        "task_text": copy.deepcopy(task_text),
        "source_files": {path: public_sources[path] for path in PRODUCER_OWNED + SUPPORT_READ_ONLY},
        "writable_paths": list(PRODUCER_OWNED), "required_delivery_paths": [],
    }
    recipient = {
        "task_id": generated.task_id, "seed": generated.seed, "role": "recipient",
        "task_text": copy.deepcopy(task_text),
        "source_files": {path: public_sources[path] for path in RECIPIENT_OWNED + SUPPORT_READ_ONLY},
        "writable_paths": list(RECIPIENT_OWNED), "required_delivery_paths": list(PRODUCER_OWNED),
    }
    payloads = {"producer": producer, "recipient": recipient}
    payload_blob = json.dumps(payloads, ensure_ascii=False, sort_keys=True).lower()
    hidden_leaks = [path for path in HIDDEN_PATHS if path.lower() in payload_blob]
    return {
        "agent_payloads": payloads,
        "manifest": {
            "schema_version": "peerrolebench-dist1-materials-v2",
            "task_id": generated.task_id, "seed": generated.seed,
            "public_paths": sorted(public_paths), "hidden_paths": list(HIDDEN_PATHS),
            "producer_writable_paths": list(PRODUCER_OWNED),
            "recipient_writable_paths": list(RECIPIENT_OWNED),
            "payload_sha256": digest_json(payloads),
            "task_text_oracle_patterns": text_leaks,
            "source_comment_oracle_patterns": source_leaks,
            "hidden_path_leaks": hidden_leaks,
            "scientific_task_text_qualified": not text_leaks and not source_leaks and not hidden_leaks,
            "public_interface_contract_version": "dist1-queue-interface-v1",
            "native_materials_preserved": True,
            "runtime_dispatch_verified": False,
        },
    }
