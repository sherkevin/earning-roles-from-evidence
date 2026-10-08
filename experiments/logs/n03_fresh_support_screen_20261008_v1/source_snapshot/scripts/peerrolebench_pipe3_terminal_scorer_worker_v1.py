"""Private PIPE3 terminal holdout worker.

The worker receives only a public target snapshot and a pre-registered holdout
contract.  Its checks are intentionally different from the immediate adoption
receipt: the holdout uses two records and compares a normalized terminal
projection digest.  J/A/D, policy state, and operator ledger data never enter
the worker request.
"""

from __future__ import annotations

from datetime import datetime
import hashlib
import importlib
import json
from pathlib import Path
import sys
import traceback


SCHEMA_VERSION = "pipe3-terminal-holdout-response-v1"
REQUEST_SCHEMA = "pipe3-terminal-holdout-request-v1"
SCORER_VERSION = "pipe3-terminal-holdout-v1"
CHECK_IDS = ("T1_holdout_projection", "T2_batch_cardinality", "T3_utf8_holdout")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _candidate_failure(exc, source_root):
    candidates = {
        (Path(source_root) / name).resolve(): name
        for name in ("producer.py", "processor.py", "sink.py", "models.py")
    }
    frames = traceback.extract_tb(exc.__traceback__) if exc.__traceback__ else []
    for frame in frames:
        path = candidates.get(Path(frame.filename).resolve())
        if path:
            return {"failure_origin": "candidate", "source_path": path,
                    "exception_class": type(exc).__name__, "reason": str(exc)}
    return None


def _event(cls, request, identifier):
    values = {}
    for name in cls.__dataclass_fields__:
        if name == request["timestamp_field"]:
            values[name] = datetime(2023, 11, 14, 22, 13, 20)
        elif name == request["id_field"]:
            values[name] = identifier
        elif name == request["user_field"]:
            values[name] = request["user_value"]
        elif name == request["action_field"]:
            values[name] = request["action_value"]
        elif name == request["value_field"]:
            values[name] = request["value_value"]
        else:
            values[name] = "terminal-probe"
    return cls(**values)


def _projection(records, request):
    normalized = []
    for record in records:
        normalized.append({
            request["id_field"]: record.get(request["id_field"]),
            request["timestamp_field"]: record.get(request["timestamp_field"]),
            request["user_field"]: record.get(request["user_field"]),
            request["action_field"]: record.get(request["action_field"]),
            request["value_field"]: record.get(request["value_field"]),
        })
    return normalized


def score(source_root, request):
    root = Path(source_root).resolve()
    try:
        sys.path.insert(0, str(root))
        models = importlib.import_module("models")
        producer = importlib.import_module("producer")
        processor = importlib.import_module("processor")
        sink = importlib.import_module("sink")
        cls = getattr(models, request["event_class"])
        input_path = root.parent / "scratch" / "terminal_input.jsonl"
        produced_path = root.parent / "scratch" / "terminal_produced.jsonl"
        processed_path = root.parent / "scratch" / "terminal_processed.jsonl"
        events = [_event(cls, request, "terminal-001"), _event(cls, request, "terminal-002")]
        producer.produce_events(events, str(produced_path))
        processor.process_events(str(produced_path), str(processed_path))
        raw = processed_path.read_bytes()
        text = raw.decode("utf-8")
        records = sink.load_processed_events(str(processed_path))
        projection = _projection(records, request)
        checks = [
            {"id": "T1_holdout_projection", "status": "PASS"
             if digest(projection) == request["reference_projection_digest"] else "FAIL",
             "observed_projection_digest": digest(projection)},
            {"id": "T2_batch_cardinality", "status": "PASS"
             if len(records) == 2 and [item.get(request["id_field"]) for item in records]
             == ["terminal-001", "terminal-002"] else "FAIL"},
            {"id": "T3_utf8_holdout", "status": "PASS"
             if any(marker in text for marker in ("ü", "é", "€")) else "FAIL"},
        ]
        complete = all(item["status"] in {"PASS", "FAIL"} for item in checks)
        passed = complete and all(item["status"] == "PASS" for item in checks)
        return {
            "ok": True, "schema_version": SCHEMA_VERSION,
            "scorer_version": SCORER_VERSION,
            "task_id": request["task_id"], "seed": request["seed"],
            "artifact_sha256": request["artifact_sha256"],
            "holdout_digest": request["holdout_digest"],
            "status": "PASS" if passed else "FAIL" if complete else "UNKNOWN",
            "label": 1 if passed else 0 if complete else None,
            "quality_score": sum(item["status"] == "PASS" for item in checks) / len(checks)
            if complete else None,
            "coverage_complete": complete, "checks": checks,
            "required_check_ids": list(CHECK_IDS),
        }
    except (UnicodeDecodeError, json.JSONDecodeError, AssertionError, KeyError, TypeError, ValueError) as exc:
        failure = _candidate_failure(exc, root)
        if failure:
            return {"ok": True, "schema_version": SCHEMA_VERSION,
                    "scorer_version": SCORER_VERSION, "task_id": request["task_id"],
                    "seed": request["seed"], "artifact_sha256": request["artifact_sha256"],
                    "holdout_digest": request["holdout_digest"], "status": "FAIL", "label": 0,
                    "quality_score": 0.0, "coverage_complete": True,
                    "checks": [{"id": check_id, "status": "FAIL", **failure}
                               for check_id in CHECK_IDS],
                    "required_check_ids": list(CHECK_IDS)}
        return {"ok": False, "error_type": type(exc).__name__, "message": str(exc)}
    except Exception as exc:
        failure = _candidate_failure(exc, root)
        if failure:
            return {"ok": True, "schema_version": SCHEMA_VERSION,
                    "scorer_version": SCORER_VERSION, "task_id": request["task_id"],
                    "seed": request["seed"], "artifact_sha256": request["artifact_sha256"],
                    "holdout_digest": request["holdout_digest"], "status": "FAIL", "label": 0,
                    "quality_score": 0.0, "coverage_complete": True,
                    "checks": [{"id": check_id, "status": "FAIL", **failure}
                               for check_id in CHECK_IDS],
                    "required_check_ids": list(CHECK_IDS)}
        return {"ok": False, "error_type": type(exc).__name__, "message": str(exc)}


def main():
    source_root = sys.argv[1]
    for line in sys.stdin:
        try:
            request = json.loads(line)
            required = {"op", "schema_version", "task_id", "seed", "artifact_sha256",
                        "holdout_digest", "reference_projection_digest", "scorer_version",
                        "event_class", "timestamp_field", "id_field", "user_field",
                        "action_field", "value_field", "action_value", "user_value", "value_value"}
            if set(request) != required or request["op"] != "score_terminal":
                raise ValueError("terminal scorer request fields are invalid")
            if request["schema_version"] != REQUEST_SCHEMA or request["scorer_version"] != SCORER_VERSION:
                raise ValueError("terminal scorer request version mismatch")
            response = score(source_root, request)
        except Exception as exc:
            response = {"ok": False, "error_type": type(exc).__name__, "message": str(exc)}
        print(json.dumps(response, separators=(",", ":"), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
