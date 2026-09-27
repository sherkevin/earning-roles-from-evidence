#!/usr/bin/env python3
"""Qualify the PIPE3 task contract and ledger fixture without model execution.

This is a bounded N03 prerequisite check.  It does not execute an LLM candidate,
does not call pytest or the native TeamBench grader, and does not create training
data.  The parent keeps hidden tests/expected values and validates only static
contracts that a later real run must implement. This does not prove runtime
payload visibility, scorer isolation, or ledger replay.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEAMBENCH = ROOT / "references/benchmark_sources/TeamBench"
PIN = "d185aef1916fd86a9ba554d581fd256319a973af"
TASK_ID = "PIPE3_stream_processing"
SEEDS = (0, 1, 2)
PRODUCER_OWNED = ("producer.py",)
RECIPIENT_OWNED = ("processor.py",)
SUPPORT_READ_ONLY = ("models.py", "sink.py")
HIDDEN_PATHS = ("tests/__init__.py", "tests/test_pipeline.py", "tests/test_serialization.py")
TASK_TEXT_LEAK_PATTERNS = ("bug 1", "bug 2", "bug 3", "fix", "planner")


def digest_files(files: dict[str, str | bytes]) -> str:
    h = hashlib.sha256()
    for name, value in sorted(files.items()):
        raw = value.encode() if isinstance(value, str) else value
        h.update(len(name.encode()).to_bytes(8, "big"))
        h.update(name.encode())
        h.update(len(raw).to_bytes(8, "big"))
        h.update(raw)
    return h.hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_pin() -> dict[str, Any]:
    actual = subprocess.check_output(["git", "-C", str(TEAMBENCH), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(TEAMBENCH), "status", "--porcelain"], text=True)
    return {"expected": PIN, "actual": actual, "clean": not dirty, "passed": actual == PIN and not dirty}


def load_pipe3(seed: int):
    if str(TEAMBENCH) not in sys.path:
        sys.path.insert(0, str(TEAMBENCH))
    module = importlib.import_module("generators.gen_pipe3_stream_processing")
    if Path(module.__file__).resolve() != TEAMBENCH / "generators/gen_pipe3_stream_processing.py":
        raise RuntimeError("unexpected generator shadowing")
    return module.Generator().generate(seed)


def contract_for(generated: Any) -> dict[str, Any]:
    if generated.task_id != TASK_ID:
        raise ValueError(f"unexpected task id: {generated.task_id!r}")
    files = dict(generated.workspace_files)
    required = set(PRODUCER_OWNED + RECIPIENT_OWNED + SUPPORT_READ_ONLY + HIDDEN_PATHS)
    if set(files) != required:
        raise ValueError(f"PIPE3 generated file set changed: {sorted(set(files) ^ required)}")
    public = set(PRODUCER_OWNED + RECIPIENT_OWNED + SUPPORT_READ_ONLY)
    producer = {
        "role": "producer",
        "public_files": {path: files[path] for path in PRODUCER_OWNED + SUPPORT_READ_ONLY},
        "writable_paths": list(PRODUCER_OWNED),
        "read_only_paths": list(SUPPORT_READ_ONLY),
    }
    recipient = {
        "role": "recipient",
        "public_files": {path: files[path] for path in RECIPIENT_OWNED + SUPPORT_READ_ONLY},
        "writable_paths": list(RECIPIENT_OWNED),
        "required_delivery_paths": list(PRODUCER_OWNED),
        "read_only_paths": list(SUPPORT_READ_ONLY),
    }
    if set(producer["writable_paths"]) & set(recipient["writable_paths"]):
        raise AssertionError("producer and recipient writable paths overlap")
    if set(producer["public_files"]) != set(PRODUCER_OWNED + SUPPORT_READ_ONLY):
        raise AssertionError("producer public payload has unexpected paths")
    if set(recipient["public_files"]) != set(RECIPIENT_OWNED + SUPPORT_READ_ONLY):
        raise AssertionError("recipient pre-delivery payload has unexpected paths")
    if any(path in producer["public_files"] or path in recipient["public_files"] for path in HIDDEN_PATHS):
        raise AssertionError("hidden evaluator file leaked into actor payload")
    task_text = {"spec_md": generated.spec_md, "brief_md": generated.brief_md}
    task_text_blob = "\n".join(task_text.values()).lower()
    task_text_leaks = [pattern for pattern in TASK_TEXT_LEAK_PATTERNS if pattern in task_text_blob]
    hidden_path_mentions = [path for path in HIDDEN_PATHS if path.lower() in task_text_blob]
    expected = dict(generated.expected)
    payloads = {
        "producer": {
            "task_id": generated.task_id,
            "seed": generated.seed,
            "task_text": task_text,
            "public_files": producer["public_files"],
        },
        "recipient": {
            "task_id": generated.task_id,
            "seed": generated.seed,
            "task_text": task_text,
            "public_files": recipient["public_files"],
            "delivery_allowlist": list(PRODUCER_OWNED),
        },
    }
    payload_blob = json.dumps(payloads, ensure_ascii=False, sort_keys=True)
    expected_metadata_leak = any(
        isinstance(value, str) and value and value in payload_blob
        for value in expected.values()
    )
    return {
        "schema_version": "pipe3-task-contract-v2-static",
        "task_id": generated.task_id,
        "seed": generated.seed,
        "domain": expected.get("domain"),
        "expected_bug_ids_recorded_parent_only": list(expected.get("bugs_fixed", [])),
        "producer": producer,
        "recipient": recipient,
        "public_paths": sorted(public),
        "hidden_paths": list(HIDDEN_PATHS),
        "expected_hidden_from_agents": True,
        "instance_digest": digest_files(files),
        "public_payload_digest": digest_files({**producer["public_files"], **recipient["public_files"]}),
        "actor_payload_schema_checked": True,
        "actor_payload_digests": {
            role: digest_text(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            for role, payload in payloads.items()
        },
        "task_text_leak_patterns": task_text_leaks,
        "task_text_hidden_path_mentions": hidden_path_mentions,
        "task_text_scientific_qualified": not task_text_leaks and not hidden_path_mentions and not expected_metadata_leak,
        "expected_metadata_leak": expected_metadata_leak,
        "runtime_payload_dispatch_verified": False,
    }


def validate_ledger() -> dict[str, Any]:
    """Validate the future event order without using any task result."""
    now = datetime.now(timezone.utc).isoformat()
    events = [
        {"event_id": "e0001", "type": "selection", "phase": "pre_execution", "visible_to": ["parent"], "payload": {"peer": "producer-A", "propensity": 0.5}},
        {"event_id": "e0002", "type": "delivery", "phase": "post_execution", "visible_to": ["parent", "recipient"], "payload": {"artifact_digest": "artifact-sha256"}},
        {"event_id": "e0003", "type": "judgment", "phase": "post_delivery", "visible_to": ["parent", "recipient"], "payload": {"label": "unknown", "producer": "producer-A", "recipient": "recipient-B"}},
        {"event_id": "e0004", "type": "consumer_action", "phase": "post_judgment", "visible_to": ["parent"], "payload": {"action": "use"}},
        {"event_id": "e0005", "type": "independent_score", "phase": "post_action", "visible_to": ["parent"], "payload": {"score": "hidden"}},
        {"event_id": "e0006", "type": "role_update", "phase": "feedback_arrival", "visible_to": ["parent", "selector"], "payload": {"source_event": "e0003"}},
    ]
    order = {"selection": 0, "delivery": 1, "judgment": 2, "consumer_action": 3, "independent_score": 4, "role_update": 5}
    ids = [event["event_id"] for event in events]
    checks = {
        "unique_event_ids": len(ids) == len(set(ids)),
        "selection_before_delivery": ids.index("e0001") < ids.index("e0002"),
        "delivery_before_judgment": ids.index("e0002") < ids.index("e0003"),
        "judgment_before_action": ids.index("e0003") < ids.index("e0004"),
        "action_before_score": ids.index("e0004") < ids.index("e0005"),
        "score_before_update": ids.index("e0005") < ids.index("e0006"),
        "hidden_score_not_actor_visible": "parent" in events[4]["visible_to"] and "recipient" not in events[4]["visible_to"],
        "update_references_judgment": events[5]["payload"]["source_event"] == "e0003",
        "all_event_types_known": all(event["type"] in order for event in events),
    }
    return {"schema_version": "pipe3-event-ledger-fixture-v1", "created_at": now, "checks": checks,
            "fixture_passed": all(checks.values()), "event_count": len(events), "events": events,
            "runtime_ledger_replay_verified": False}


def run_isolation_canary(output: Path) -> dict[str, Any]:
    canary_out = output / "isolation_canary"
    command = [sys.executable, str(ROOT / "scripts/peerrolebench_isolation_canary.py"), "--output", str(canary_out)]
    started = time.monotonic()
    process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
    result = {"command": command, "returncode": process.returncode,
              "wall_seconds": round(time.monotonic() - started, 6),
              "stdout": process.stdout, "stderr": process.stderr}
    if (canary_out / "results.json").is_file():
        result["results"] = json.loads((canary_out / "results.json").read_text())
    result["passed"] = process.returncode == 0 and bool(result.get("results", {}).get("canary_contract_passed"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    raw_path = output / "raw.jsonl"

    def log(event_type: str, payload: Any):
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload}, ensure_ascii=False) + "\n")
            handle.flush()

    config = {
        "experiment_id": output.name,
        "purpose": "N03 PIPE3 static task-contract fixture, ledger fixture, and listed-access canary",
        "command": sys.argv,
        "source_commit": PIN,
        "python": sys.version,
        "platform": platform.platform(),
        "seeds": list(SEEDS),
        "llm_calls": 0,
        "gpu_jobs": 0,
        "pytest_invoked": False,
        "native_grader_invoked": False,
        "network": False,
        "scientific_claim_allowed": False,
        "benchmark_qualified": False,
    }
    (output / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("config", config)
    result: dict[str, Any] = {"config": config, "pin": {}, "seeds": {}, "ledger": {}, "isolation": {}}
    try:
        result["pin"] = verify_pin()
        log("pin_check", result["pin"])
        if not result["pin"]["passed"]:
            raise RuntimeError("TeamBench checkout is not the reviewed clean pin")
        for seed in SEEDS:
            generated = load_pipe3(seed)
            contract = contract_for(generated)
            result["seeds"][str(seed)] = {"passed": True, "contract": contract}
            log("task_contract", {"seed": seed, "passed": True, "contract": contract})
        result["ledger"] = validate_ledger()
        log("ledger_check", result["ledger"])
        result["isolation"] = run_isolation_canary(output)
        log("isolation_check", result["isolation"])
    except Exception as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc)}
        log("qualification_error", result["error"])
    seed_pass = len(result["seeds"]) == len(SEEDS) and all(item.get("passed") for item in result["seeds"].values())
    contract_pass = bool(result["pin"].get("passed")) and seed_pass
    ledger_pass = bool(result["ledger"].get("fixture_passed"))
    isolation_pass = bool(result["isolation"].get("passed"))
    task_text_pass = (
        all(item["contract"].get("task_text_scientific_qualified") is True
            for item in result["seeds"].values())
        if seed_pass else False
    )
    result.update({
        "task_contract_passed": contract_pass,
        "ledger_fixture_passed": ledger_pass,
        "listed_isolation_canary_passed": isolation_pass,
        "task_text_scientific_qualified": task_text_pass,
        "contract_fixture_preflight_passed": contract_pass and ledger_pass and isolation_pass,
        "real_agent_preflight_verified": False,
        "qualified_for_pipe3_preflight": False,
        "strict_N01_gate_passed": False,
        "benchmark_qualified": False,
        "scientific_claim_allowed": False,
        "remaining_gates": [
            "real producer/recipient execution with hidden scoring",
            "redacted task text with no intended-fix oracle leak",
            "runtime payload dispatch and scorer isolation proof",
            "real event-ledger replay with exact-once lineage and propensity",
            "multi-event and exception-path coverage",
            "independent task-root confirmation split",
            "complete cost and responsibility evidence",
        ],
    })
    (output / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    log("summary", result)
    print(json.dumps({key: result[key] for key in ("task_contract_passed", "ledger_fixture_passed",
                                                    "listed_isolation_canary_passed", "task_text_scientific_qualified",
                                                    "contract_fixture_preflight_passed", "real_agent_preflight_verified",
                                                    "strict_N01_gate_passed", "benchmark_qualified",
                                                    "scientific_claim_allowed")}, indent=2))
    return 0 if result["contract_fixture_preflight_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
