"""Non-oracular material contract for a PIPE2 ETL handoff.

PIPE2 is a TeamBench-derived candidate root, not a frozen benchmark.  The
adapter exposes a producer-owned extractor and a recipient-owned transform/load
chain.  Expected output, native tests and task bug inventory stay operator-only.
This module does not execute candidate code or call an LLM.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

from peerrolebench_pipe3_material_adapter import digest_files, strip_comments_and_docstrings


ROOT = Path(__file__).resolve().parents[1]
TEAMBENCH = ROOT / "references/benchmark_sources/TeamBench"
TEAMBENCH_COMMIT = "d185aef1916fd86a9ba554d581fd256319a973af"
TASK_ID = "PIPE2_data_pipeline"
MATERIAL_SCHEMA_VERSION = "peerrolebench-pipe2-materials-v2"
PRODUCER_OWNED = ("pipeline/extract.py",)
RECIPIENT_OWNED = ("pipeline/transform.py", "pipeline/load.py")
SUPPORT_READ_ONLY = ("pipeline/__init__.py", "PIPELINE_SPEC.md", "data/source.csv")
RECIPIENT_SUPPORT_READ_ONLY = ("pipeline/__init__.py", "PIPELINE_SPEC.md")
ORCHESTRATOR_READ_ONLY = ("pipeline/run_pipeline.py",)
HIDDEN_PATHS = ("data/expected_output.csv", "tests/__init__.py", "tests/test_pipeline.py", "requirements.txt")
DELIVERY_PATH = "artifact/extracted_rows.json"
ORACLE_PATTERNS = ("bug 1", "bug 2", "bug 3", "planner", "fix:", "fix the", "expected_output")


def load_pipe2(seed: int) -> Any:
    root = str(TEAMBENCH)
    if root not in sys.path:
        sys.path.insert(0, root)
    from generators import registry
    if Path(registry.__file__).resolve() != TEAMBENCH / "generators/registry.py":
        raise RuntimeError("another package shadows the pinned TeamBench generators")
    generated = registry.get_generator(TASK_ID).generate(seed=seed)
    if generated.task_id != TASK_ID:
        raise ValueError(f"unexpected generated task: {generated.task_id}")
    return generated


def neutral_task_text(schema_name: str) -> dict[str, str]:
    return {
        "spec_md": f"""# ETL handoff task ({schema_name})

The parent process supplies a producer extraction artifact and a read-only source schema.
The producer owns `pipeline/extract.py`; the recipient owns only the transform/load chain.
`pipeline/run_pipeline.py` is an operator/orchestrator file and is read-only outside the
recipient role; the recipient must not re-run extraction from source data.
Preserve public interfaces, consume the supplied extraction artifact, and produce the
declared output schema. The parent evaluator keeps expected output and tests private.
""",
        "brief_md": """# Assigned ETL component

Repair the assigned component using only the public schema and any sealed producer
artifact. Return complete text only for files in your writable contract.
""",
    }


def _assert_paths(workspace: Mapping[str, Any]) -> None:
    required = set(PRODUCER_OWNED + RECIPIENT_OWNED + SUPPORT_READ_ONLY +
                   RECIPIENT_SUPPORT_READ_ONLY + ORCHESTRATOR_READ_ONLY + HIDDEN_PATHS)
    if set(workspace) != required:
        raise ValueError(f"unexpected PIPE2 workspace paths: {sorted(set(workspace) ^ required)}")
    if not all(isinstance(workspace[path], str) for path in required):
        raise ValueError("PIPE2 workspace must contain text files")


def build_materials(generated: Any) -> dict[str, Any]:
    if generated.task_id != TASK_ID:
        raise ValueError(f"unexpected task: {generated.task_id}")
    workspace = dict(generated.workspace_files)
    _assert_paths(workspace)
    expected = dict(generated.expected)
    text = neutral_task_text(str(expected["schema_name"]))
    public_paths = tuple(dict.fromkeys(PRODUCER_OWNED + RECIPIENT_OWNED + SUPPORT_READ_ONLY +
                                       RECIPIENT_SUPPORT_READ_ONLY + ORCHESTRATOR_READ_ONLY))
    public_sources = {
        path: strip_comments_and_docstrings(workspace[path]) if path.endswith(".py") else workspace[path]
        for path in public_paths
    }
    for path, source in public_sources.items():
        if path.endswith(".py"):
            compile(source, path, "exec")
    producer = {
        "task_id": TASK_ID, "seed": generated.seed, "role": "producer",
        "task_text": copy.deepcopy(text),
        "source_files": {path: public_sources[path] for path in PRODUCER_OWNED + SUPPORT_READ_ONLY},
        "writable_paths": list(PRODUCER_OWNED), "required_delivery_paths": [],
        "delivery_schema": "pipe2-extracted-rows-v1",
    }
    recipient = {
        "task_id": TASK_ID, "seed": generated.seed, "role": "recipient",
        "task_text": copy.deepcopy(text),
        "source_files": {path: public_sources[path] for path in RECIPIENT_OWNED + RECIPIENT_SUPPORT_READ_ONLY},
        "writable_paths": list(RECIPIENT_OWNED), "required_delivery_paths": [DELIVERY_PATH],
        "delivery_schema": "pipe2-extracted-rows-v1",
    }
    payloads = {"producer": producer, "recipient": recipient}
    blob = json.dumps(payloads, ensure_ascii=False, sort_keys=True)
    text_blob = (text["spec_md"] + text["brief_md"]).lower()
    source_blob = "\n".join(public_sources.values()).lower()
    text_oracle = [pattern for pattern in ORACLE_PATTERNS if pattern in text_blob]
    source_oracle = [pattern for pattern in ORACLE_PATTERNS if pattern in source_blob]
    hidden_leaks = [path for path in HIDDEN_PATHS if path.lower() in blob.lower()]
    return {
        "agent_payloads": payloads,
        "manifest": {
            "schema_version": MATERIAL_SCHEMA_VERSION,
            "task_id": TASK_ID, "seed": generated.seed,
            "source_commit": TEAMBENCH_COMMIT,
            "structural_root": f"TeamBench@{TEAMBENCH_COMMIT}/{TASK_ID}",
            "producer_writable_paths": list(PRODUCER_OWNED),
            "recipient_writable_paths": list(RECIPIENT_OWNED),
            "support_read_only_paths": list(SUPPORT_READ_ONLY),
            "recipient_support_read_only_paths": list(RECIPIENT_SUPPORT_READ_ONLY),
            "orchestrator_read_only_paths": list(ORCHESTRATOR_READ_ONLY),
            "hidden_paths": list(HIDDEN_PATHS), "delivery_path": DELIVERY_PATH,
            "payload_sha256": digest_files({role: json.dumps(value, ensure_ascii=False, sort_keys=True)
                                             for role, value in payloads.items()}),
            "task_text_oracle_patterns": text_oracle,
            "source_oracle_patterns": source_oracle,
            "hidden_path_leaks": hidden_leaks,
            "scientific_task_text_qualified": not text_oracle and not source_oracle and not hidden_leaks,
            "benchmark_qualified": False,
        },
    }


def validate_extracted_rows(rows: Sequence[Mapping[str, Any]], *, columns: Sequence[str]) -> dict[str, Any]:
    """Validate only the public delivery shape; never label correctness."""
    cols = tuple(str(column) for column in columns)
    if not cols or len(set(cols)) != len(cols):
        raise ValueError("columns must be unique and non-empty")
    normalized = []
    for row in rows:
        if not isinstance(row, Mapping) or tuple(row) != cols:
            raise ValueError("extracted row columns do not match the public schema")
        normalized.append({column: row[column] for column in cols})
    artifact = {
        "schema": "pipe2-extracted-rows-v1", "columns": list(cols),
        "row_count": len(normalized), "rows": normalized,
    }
    artifact["artifact_sha256"] = digest_files(
        {DELIVERY_PATH: json.dumps(artifact, sort_keys=True, ensure_ascii=False)})
    return artifact


def attach_extracted_rows(recipient_payload: Mapping[str, Any], artifact: Mapping[str, Any]) -> dict[str, Any]:
    if recipient_payload.get("role") != "recipient":
        raise ValueError("recipient payload required")
    if tuple(recipient_payload.get("required_delivery_paths", ())) != (DELIVERY_PATH,):
        raise ValueError("recipient payload is not awaiting the PIPE2 delivery")
    if artifact.get("schema") != "pipe2-extracted-rows-v1":
        raise ValueError("unexpected PIPE2 delivery schema")
    result = copy.deepcopy(dict(recipient_payload))
    result["source_files"][DELIVERY_PATH] = json.dumps(artifact, sort_keys=True, ensure_ascii=False)
    result["required_delivery_paths"] = []
    result["delivery_sha256"] = str(artifact.get("artifact_sha256"))
    return result


__all__ = [
    "DELIVERY_PATH", "HIDDEN_PATHS", "PRODUCER_OWNED", "RECIPIENT_OWNED", "SUPPORT_READ_ONLY",
    "RECIPIENT_SUPPORT_READ_ONLY", "ORCHESTRATOR_READ_ONLY", "MATERIAL_SCHEMA_VERSION",
    "TEAMBENCH_COMMIT", "attach_extracted_rows", "build_materials", "load_pipe2",
    "neutral_task_text", "validate_extracted_rows",
]
