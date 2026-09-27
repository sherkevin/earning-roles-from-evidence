"""Build a non-oracular DIST1 actor payload from the pinned TeamBench task.

The adapter keeps the public queue behavior contract while removing the native
spec's bug numbering, hidden test names and Planner solution hints.  It never
executes candidate code or exposes tests/expected metadata.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from typing import Any

from peerrolebench_pipe3_material_adapter import strip_comments_and_docstrings


PRODUCER_OWNED = ("mqueue/queue.py", "mqueue/priority.py")
RECIPIENT_OWNED = ("mqueue/consumer.py",)
SUPPORT_READ_ONLY = ("mqueue/__init__.py", "mqueue/config.py")
HIDDEN_PATHS = (
    "mqueue/producer.py", "tests/__init__.py", "tests/test_capacity.py",
    "tests/test_concurrent.py", "tests/test_crash_recovery.py",
    "tests/test_message_loss.py", "tests/test_ordering.py", "tests/test_single_thread.py",
)
ORACLE_PATTERNS = ("bug 1", "bug 2", "bug 3", "planner", "pytest tests", "supporting documents")


def digest_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def neutral_task_text() -> dict[str, str]:
    spec = """# DIST1: Concurrent Message Queue

## Goal
Make the public message queue safe and interoperable under concurrent producer and
consumer load.

## Responsibilities
- The producer owns `mqueue/queue.py` and `mqueue/priority.py` and must preserve their public names and signatures.
- The recipient owns `mqueue/consumer.py` and must implement its consumer integration.
- `mqueue/__init__.py` and `mqueue/config.py` are read-only support files.

## Acceptance
The queue must keep its capacity bound under concurrent insertion, expose a receipt-based
acknowledgement path that does not lose unacknowledged messages, and order equal-priority
items deterministically without requiring payload values to be comparable. A bounded
concurrent workload must complete without message loss. The parent evaluator keeps tests
private; inspect the public interfaces and data flow before editing.
"""
    brief = """# DIST1 concurrent queue task

Repair the assigned component so the public queue and consumer work correctly under
concurrent load. Preserve public compatibility and return only complete text for files
you are allowed to change.
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
            "schema_version": "peerrolebench-dist1-materials-v1",
            "task_id": generated.task_id, "seed": generated.seed,
            "public_paths": sorted(public_paths), "hidden_paths": list(HIDDEN_PATHS),
            "producer_writable_paths": list(PRODUCER_OWNED),
            "recipient_writable_paths": list(RECIPIENT_OWNED),
            "payload_sha256": digest_json(payloads),
            "task_text_oracle_patterns": text_leaks,
            "source_comment_oracle_patterns": source_leaks,
            "hidden_path_leaks": hidden_leaks,
            "scientific_task_text_qualified": not text_leaks and not source_leaks and not hidden_leaks,
            "native_materials_preserved": True,
            "runtime_dispatch_verified": False,
        },
    }
