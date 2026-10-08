"""Private producer-only scorer for the redacted PIPE3 public contract.

The worker receives only ``producer.py`` and read-only ``models.py``.  It does
not receive tests, expected files, the ledger, or a sink implementation.  The
checks measure the producer artifact only: importability, one-record
serialization, and bounded batch output.
"""
from __future__ import annotations

import ast
from datetime import datetime
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import traceback


SCHEMA_VERSION = "pipe3-producer-score-response-v1"
REQUEST_SCHEMA = "pipe3-producer-score-request-v1"
SCORER_VERSION = "pipe3-producer-objective-v1"
CHECK_IDS = ("P1_import", "P2_iso_serialization", "P3_batch_output")


def digest_files(files):
    h = hashlib.sha256()
    for name, value in sorted(files.items()):
        name_bytes = name.encode()
        value_bytes = value.encode() if isinstance(value, str) else value
        h.update(len(name_bytes).to_bytes(8, "big")); h.update(name_bytes)
        h.update(len(value_bytes).to_bytes(8, "big")); h.update(value_bytes)
    return h.hexdigest()


class Scorer:
    def __init__(self, source, event_class, timestamp_field, id_field):
        self.source = Path(source).resolve()
        self.event_class_name = event_class
        self.timestamp_field = timestamp_field
        self.id_field = id_field
        sys.path.insert(0, str(self.source))
        self.producer = None
        self.models = None
        self.event_class = None

    def _candidate_path(self, filename):
        return str((self.source / filename).resolve())

    def _failure(self, exc):
        paths = {self._candidate_path("producer.py"): "producer.py",
                 self._candidate_path("models.py"): "models.py"}
        frames = traceback.extract_tb(exc.__traceback__) if exc.__traceback__ else []
        source_path = None
        for frame in frames:
            source_path = paths.get(str(Path(frame.filename).resolve()))
            if source_path:
                break
        if source_path is None and isinstance(exc, SyntaxError) and exc.filename:
            source_path = paths.get(str(Path(exc.filename).resolve()))
        if source_path is None:
            return None
        if isinstance(exc, SyntaxError):
            code = "SYNTAX_ERROR_IN_DELIVERY"
        elif isinstance(exc, TypeError):
            code = "TYPE_ERROR_IN_DELIVERY"
        elif isinstance(exc, ImportError):
            code = "IMPORT_ERROR_IN_DELIVERY"
        else:
            return None
        return {"failure_origin": "candidate", "failure_stage": "import",
                "failure_code": code, "exception_class": type(exc).__name__,
                "source_path": source_path, "reason": str(exc)}

    def load(self):
        self.models = importlib.import_module("models")
        self.producer = importlib.import_module("producer")
        self.event_class = getattr(self.models, self.event_class_name)
        if not hasattr(self.producer, "serialize_event") or not hasattr(self.producer, "produce_events"):
            raise AttributeError("producer public API is incomplete")

    def make_event(self, identifier):
        values = {}
        for field_name in self.event_class.__dataclass_fields__:
            if field_name == self.timestamp_field:
                values[field_name] = datetime(2023, 11, 14, 22, 13, 20)
            elif field_name == self.id_field:
                values[field_name] = identifier
            elif any(token in field_name.lower() for token in ("name", "user", "holder", "sensor")):
                values[field_name] = "Müller"
            elif any(token in field_name.lower() for token in ("value", "amount", "price", "description", "url", "location")):
                values[field_name] = "€probe"
            else:
                values[field_name] = "probe"
        return self.event_class(**values)

    def import_gate(self, artifact_digest):
        try:
            ast.parse((self.source / "models.py").read_text(), filename="models.py")
            ast.parse((self.source / "producer.py").read_text(), filename="producer.py")
            self.load()
        except Exception as exc:
            failure = self._failure(exc)
            checks = [{"id": "P1_import", "status": "FAIL" if failure else "UNKNOWN",
                       **(failure or {"reason": type(exc).__name__ + ": " + str(exc)})}]
            checks.extend({"id": check_id, "status": "UNKNOWN", "reason": "blocked_by_import_gate"}
                          for check_id in CHECK_IDS[1:])
            if failure:
                return {"schema_version": SCHEMA_VERSION, "scorer_version": SCORER_VERSION,
                        "task_id": "PIPE3_stream_processing", "seed": None,
                        "artifact_sha256": artifact_digest, "status": "FAIL", "label": 0,
                        "quality_score": 0.0, "decision_complete": True,
                        "coverage_complete": False, "checks": checks,
                        "failed_check_ids": ["P1_import"],
                        "observed_check_count": len(checks), "required_check_ids": list(CHECK_IDS),
                        **failure}
            return {"schema_version": SCHEMA_VERSION, "scorer_version": SCORER_VERSION,
                    "task_id": "PIPE3_stream_processing", "seed": None,
                    "artifact_sha256": artifact_digest, "status": "UNKNOWN", "label": None,
                    "quality_score": None, "decision_complete": False,
                    "coverage_complete": False, "checks": checks,
                    "failed_check_ids": [], "observed_check_count": len(checks),
                    "required_check_ids": list(CHECK_IDS), "reason": "import_gate_unknown"}
        return None

    def run(self, artifact_digest):
        gate = self.import_gate(artifact_digest)
        if gate is not None:
            return gate
        checks = []
        try:
            event = self.make_event("probe-001")
            payload = json.loads(self.producer.serialize_event(event))
            timestamp = payload.get(self.timestamp_field)
            assert isinstance(timestamp, str) and "T" in timestamp and " " not in timestamp
            checks.append({"id": "P1_import", "status": "PASS"})
            checks.append({"id": "P2_iso_serialization", "status": "PASS"})
        except AssertionError as exc:
            checks.append({"id": "P1_import", "status": "PASS"})
            checks.append({"id": "P2_iso_serialization", "status": "FAIL", "reason": str(exc)})
        except Exception as exc:
            checks.append({"id": "P1_import", "status": "PASS"})
            checks.append({"id": "P2_iso_serialization", "status": "UNKNOWN",
                           "reason": type(exc).__name__ + ": " + str(exc)})
        try:
            # SandboxedWorker creates sibling ``public`` and ``scratch``
            # directories.  Derive the scratch path from the trusted source
            # mount instead of depending on environment propagation through
            # the nested sandbox wrapper.
            output = self.source.parent / "scratch" / "producer.jsonl"
            events = [self.make_event("probe-001"), self.make_event("probe-002")]
            self.producer.produce_events(events, str(output))
            encoded = output.read_bytes()
            text = encoded.decode("utf-8")
            lines = text.splitlines()
            payloads = [json.loads(line) for line in lines if line.strip()]
            assert len(payloads) == 2
            assert [item.get(self.id_field) for item in payloads] == ["probe-001", "probe-002"]
            decoded_text = json.dumps(payloads, ensure_ascii=False)
            assert any(marker in decoded_text for marker in ("ü", "é", "€")), \
                "non-ASCII producer value was not preserved after JSON decoding"
            checks.append({"id": "P3_batch_output", "status": "PASS"})
        except AssertionError as exc:
            checks.append({"id": "P3_batch_output", "status": "FAIL", "reason": str(exc)})
        except Exception as exc:
            checks.append({"id": "P3_batch_output", "status": "UNKNOWN",
                           "reason": type(exc).__name__ + ": " + str(exc)})
        complete = len(checks) == len(CHECK_IDS) and all(item["status"] in {"PASS", "FAIL"} for item in checks)
        passed = complete and all(item["status"] == "PASS" for item in checks)
        score = sum(item["status"] == "PASS" for item in checks) / len(CHECK_IDS) if complete else None
        return {"schema_version": SCHEMA_VERSION, "scorer_version": SCORER_VERSION,
                "task_id": "PIPE3_stream_processing", "seed": None,
                "artifact_sha256": artifact_digest,
                "status": "PASS" if passed else "FAIL" if complete else "UNKNOWN",
                "label": 1 if passed else 0 if complete else None,
                "quality_score": score, "decision_complete": complete,
                "coverage_complete": complete, "checks": checks,
                "failed_check_ids": [item["id"] for item in checks if item["status"] == "FAIL"],
                "observed_check_count": len(checks), "required_check_ids": list(CHECK_IDS)}


def main():
    source, _unused, event_class = sys.argv[1:4]
    scorer = Scorer(source, event_class, None, None)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            required = {"op", "schema_version", "task_id", "seed", "artifact_sha256",
                        "scorer_version", "event_class", "timestamp_field", "id_field"}
            if set(request) != required or request["op"] != "score_producer":
                raise ValueError("PIPE3 scorer request fields are invalid")
            if request["schema_version"] != REQUEST_SCHEMA or request["task_id"] != "PIPE3_stream_processing":
                raise ValueError("PIPE3 scorer request schema/task mismatch")
            if request["scorer_version"] != SCORER_VERSION:
                raise ValueError("PIPE3 scorer version mismatch")
            scorer.event_class_name = request["event_class"]
            scorer.timestamp_field = request["timestamp_field"]
            scorer.id_field = request["id_field"]
            result = scorer.run(request["artifact_sha256"])
            result["seed"] = request["seed"]
            if request["artifact_sha256"] != result["artifact_sha256"]:
                result = {"schema_version": SCHEMA_VERSION, "scorer_version": SCORER_VERSION,
                          "task_id": request["task_id"], "seed": request["seed"],
                          "artifact_sha256": result["artifact_sha256"], "status": "UNKNOWN",
                          "label": None, "quality_score": None, "decision_complete": False,
                          "coverage_complete": False, "checks": [], "failed_check_ids": [],
                          "observed_check_count": 0, "required_check_ids": list(CHECK_IDS),
                          "reason": "artifact_digest_mismatch"}
            response = {"ok": True, "value": result}
        except Exception as exc:
            response = {"ok": False, "error_type": type(exc).__name__, "message": str(exc)}
        print(json.dumps(response, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
