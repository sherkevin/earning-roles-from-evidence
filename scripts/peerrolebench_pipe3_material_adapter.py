"""Build a non-oracular PIPE3 actor payload from a pinned TeamBench instance.

This adapter is deliberately small: it keeps executable public source and the
producer/recipient ownership boundary, while replacing TeamBench's solution
revealing prose and removing source comments/docstrings that name the intended
fixes.  It never executes candidate code and never includes tests or expected
metadata in an actor payload.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import io
import json
import tokenize
from typing import Any, Mapping


PRODUCER_OWNED = ("producer.py",)
RECIPIENT_OWNED = ("processor.py",)
SUPPORT_READ_ONLY = ("models.py", "sink.py")
HIDDEN_PATHS = ("tests/__init__.py", "tests/test_pipeline.py", "tests/test_serialization.py")
# These patterns identify explanatory oracle prose.  Implementation literals such as
# ``default=str`` or ``latin-1`` remain visible as ordinary source evidence; hiding
# executable behavior would turn this into a different task rather than a fair repair.
ORACLE_PATTERNS = ("bug 1", "bug 2", "bug 3", "planner", "fix:", "fix the", "serialization mismatch")


def digest_files(files: Mapping[str, str]) -> str:
    h = hashlib.sha256()
    for name, value in sorted(files.items()):
        raw = value.encode("utf-8")
        h.update(len(name.encode()).to_bytes(8, "big"))
        h.update(name.encode())
        h.update(len(raw).to_bytes(8, "big"))
        h.update(raw)
    return h.hexdigest()


def _docstring_starts(tree: ast.AST) -> set[tuple[int, int]]:
    starts: set[tuple[int, int]] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
                if isinstance(body[0].value.value, str):
                    starts.add((body[0].lineno, body[0].col_offset))
    return starts


def strip_comments_and_docstrings(source: str) -> str:
    """Remove explanatory text while preserving executable Python source."""
    tree = ast.parse(source)
    doc_starts = _docstring_starts(tree)
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    cleaned: list[tokenize.TokenInfo] = []
    for token in tokens:
        if token.type == tokenize.COMMENT:
            cleaned.append(token._replace(string=""))
        elif token.type == tokenize.STRING and token.start in doc_starts:
            cleaned.append(token._replace(string=""))
        else:
            cleaned.append(token)
    result = tokenize.untokenize(cleaned)
    ast.parse(result)
    return result


def neutral_task_text(domain: str) -> dict[str, str]:
    spec = f"""# PIPE3: Stream Processing Interoperability

## Goal
Make the public producer -> processor -> sink pipeline interoperate for the `{domain}`
event schema and its sample records.

## Responsibilities
- The producer owns `producer.py` and must preserve its public names and signatures.
- The recipient owns `processor.py` and must preserve its public names and signatures.
- `models.py` and `sink.py` are read-only support files.

## Acceptance
The components must exchange records correctly, preserve the declared event fields,
handle the supplied non-ASCII sample values, and produce output that the public sink
can consume. Keep the patch limited to the contracted files. The parent evaluator keeps
its tests private; inspect the public interfaces and data flow before editing.
"""
    brief = f"""# PIPE3 stream task ({domain})

Repair the assigned component so the public producer, processor, and sink work together.
Read the available source and public interfaces, preserve compatibility, and return only
the complete text of files you are allowed to change.
"""
    return {"spec_md": spec, "brief_md": brief}


def build_materials(generated: Any) -> dict[str, Any]:
    if generated.task_id != "PIPE3_stream_processing":
        raise ValueError(f"unexpected task: {generated.task_id}")
    expected = dict(generated.expected)
    domain = str(expected["domain"])
    workspace = dict(generated.workspace_files)
    required = set(PRODUCER_OWNED + RECIPIENT_OWNED + SUPPORT_READ_ONLY + HIDDEN_PATHS)
    if set(workspace) != required:
        raise ValueError(f"unexpected workspace paths: {sorted(set(workspace) ^ required)}")
    public_paths = PRODUCER_OWNED + RECIPIENT_OWNED + SUPPORT_READ_ONLY
    public_sources = {path: strip_comments_and_docstrings(workspace[path]) for path in public_paths}
    for path, source in public_sources.items():
        ast.parse(source, filename=path)
    task_text = neutral_task_text(domain)
    text_blob = "\n".join(task_text.values()).lower()
    source_blob = "\n".join(public_sources.values()).lower()
    text_leaks = [pattern for pattern in ORACLE_PATTERNS if pattern in text_blob]
    source_leaks = [pattern for pattern in ORACLE_PATTERNS if pattern in source_blob]
    producer = {
        "task_id": generated.task_id,
        "seed": generated.seed,
        "role": "producer",
        "task_text": copy.deepcopy(task_text),
        "source_files": {path: public_sources[path] for path in PRODUCER_OWNED + SUPPORT_READ_ONLY},
        "writable_paths": list(PRODUCER_OWNED),
        "required_delivery_paths": [],
    }
    recipient = {
        "task_id": generated.task_id,
        "seed": generated.seed,
        "role": "recipient",
        "task_text": copy.deepcopy(task_text),
        "source_files": {path: public_sources[path] for path in RECIPIENT_OWNED + SUPPORT_READ_ONLY},
        "writable_paths": list(RECIPIENT_OWNED),
        "required_delivery_paths": list(PRODUCER_OWNED),
    }
    payloads = {"producer": producer, "recipient": recipient}
    payload_blob = json.dumps(payloads, ensure_ascii=False, sort_keys=True)
    hidden_leaks = [path for path in HIDDEN_PATHS if path.lower() in payload_blob.lower()]
    expected_bug_ids = [str(value) for value in expected.get("bugs_fixed", [])]
    expected_metadata_in_payload = any(value in payload_blob for value in expected_bug_ids)
    return {
        "agent_payloads": payloads,
        "manifest": {
            "schema_version": "peerrolebench-pipe3-materials-v1",
            "task_id": generated.task_id,
            "seed": generated.seed,
            "domain": domain,
            "public_paths": sorted(public_paths),
            "hidden_paths": list(HIDDEN_PATHS),
            "producer_writable_paths": list(PRODUCER_OWNED),
            "recipient_writable_paths": list(RECIPIENT_OWNED),
            "payload_sha256": digest_files({role: json.dumps(payload, ensure_ascii=False, sort_keys=True)
                                              for role, payload in payloads.items()}),
            "task_text_oracle_patterns": text_leaks,
            "source_comment_oracle_patterns": source_leaks,
            "hidden_path_leaks": hidden_leaks,
            "scientific_task_text_qualified": not text_leaks and not source_leaks and not hidden_leaks,
            "expected_bug_ids_not_in_payload": not expected_metadata_in_payload,
            "expected_metadata_in_payload": expected_metadata_in_payload,
            "runtime_dispatch_verified": False,
        },
    }
