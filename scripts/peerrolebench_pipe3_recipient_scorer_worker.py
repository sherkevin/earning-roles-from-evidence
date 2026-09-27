"""Private PIPE3 recipient/adoption scorer.

``recipient`` mode sees processor.py plus models.py and scores the recipient's
own transformation on a canonical valid input. ``adoption`` mode additionally
sees the sealed producer.py and public sink.py and runs the actual
producer->processor->sink chain. Tests, expected files and the operator ledger
never enter the worker.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import traceback


SCHEMA_VERSION = "pipe3-recipient-score-response-v1"
REQUEST_SCHEMA = "pipe3-recipient-score-request-v1"
SCORER_VERSION = "pipe3-recipient-objective-v1"
RECIPIENT_CHECK_IDS = ("R1_process", "R2_shape", "R3_utf8_semantics")
ADOPTION_CHECK_IDS = ("A1_producer_boundary", "A2_sink_adoption")


def digest_files(files):
    h = hashlib.sha256()
    for name, value in sorted(files.items()):
        name_bytes = name.encode(); value_bytes = value.encode() if isinstance(value, str) else value
        h.update(len(name_bytes).to_bytes(8, "big")); h.update(name_bytes)
        h.update(len(value_bytes).to_bytes(8, "big")); h.update(value_bytes)
    return h.hexdigest()


class Scorer:
    def __init__(self, source, mode, event_class, timestamp_field, id_field):
        self.source = Path(source).resolve()
        self.mode = mode
        self.event_class_name = event_class
        self.timestamp_field = timestamp_field
        self.id_field = id_field
        sys.path.insert(0, str(self.source))

    def load(self):
        models = importlib.import_module("models")
        processor = importlib.import_module("processor")
        event_class = getattr(models, self.event_class_name)
        if not hasattr(processor, "process_events"):
            raise AttributeError("processor public API is incomplete")
        producer = sink = None
        if self.mode == "adoption":
            producer = importlib.import_module("producer")
            sink = importlib.import_module("sink")
            if not hasattr(producer, "produce_events") or not hasattr(sink, "load_processed_events"):
                raise AttributeError("adoption public API is incomplete")
        return models, processor, event_class, producer, sink

    def candidate_exception(self, exc):
        """Return a stable code only when the traceback points at processor.py."""
        candidate = (self.source / "processor.py").resolve()
        frames = traceback.extract_tb(exc.__traceback__) if exc.__traceback__ else []
        if any(Path(frame.filename).resolve() == candidate for frame in frames):
            return {"failure_origin": "candidate", "failure_stage": "processing",
                    "failure_code": "PROCESSOR_ERROR_IN_DELIVERY",
                    "exception_class": type(exc).__name__, "source_path": "processor.py"}
        return None

    def event(self, identifier):
        _, _, event_class, _, _ = self.load()
        values = {}
        for name in event_class.__dataclass_fields__:
            if name == self.timestamp_field:
                values[name] = datetime(2023, 11, 14, 22, 13, 20).isoformat()
            elif name == self.id_field:
                values[name] = identifier
            elif any(token in name.lower() for token in ("name", "user", "holder", "sensor")):
                values[name] = "Müller"
            elif any(token in name.lower() for token in ("value", "amount", "price", "description", "url", "location")):
                values[name] = "€probe"
            else:
                values[name] = "probe"
        return values

    def run(self, artifact_digest):
        _, processor, event_class, producer, sink = self.load()
        canonical = self.event("probe-001")
        input_path = Path(os.environ.get("PEERROLE_SCRATCH", self.source.parent / "scratch")) / "canonical.jsonl"
        output_path = input_path.with_name("processed.jsonl")
        input_path.write_text(json.dumps(canonical, ensure_ascii=False) + "\n", encoding="utf-8")
        if self.mode == "recipient":
            checks = []
            process_failure = None
            try:
                count = processor.process_events(str(input_path), str(output_path))
                checks.append({"id": "R1_process", "status": "PASS" if count == 1 else "FAIL",
                               "reason": "expected one processed record" if count != 1 else ""})
            except AssertionError as exc:
                checks.append({"id": "R1_process", "status": "FAIL", "reason": str(exc)})
            except Exception as exc:
                process_failure = self.candidate_exception(exc)
                checks.append({"id": "R1_process",
                               "status": "FAIL" if process_failure else "UNKNOWN",
                               "reason": repr(exc), **(process_failure or {})})
            if process_failure:
                # The candidate process reached its own source and failed before
                # producing a consumable record.  This is a determinate negative
                # for both downstream recipient checks; it is not scorer uncertainty.
                checks.extend({"id": check_id, "status": "FAIL",
                               "reason": "blocked_by_candidate_processor_failure"}
                              for check_id in ("R2_shape", "R3_utf8_semantics"))
            elif checks and checks[0]["status"] == "UNKNOWN":
                checks.extend({"id": check_id, "status": "UNKNOWN", "reason": "blocked_by_unknown_process_failure"}
                              for check_id in ("R2_shape", "R3_utf8_semantics"))
            else:
                try:
                    lines = output_path.read_text(encoding="utf-8").splitlines()
                    payload = json.loads(lines[0])
                    checks.append({"id": "R2_shape", "status": "PASS"
                                   if self.id_field in payload and "data" not in payload else "FAIL"})
                    decoded = json.dumps(payload, ensure_ascii=False)
                    checks.append({"id": "R3_utf8_semantics", "status": "PASS"
                                   if any(marker in decoded for marker in ("ü", "é", "€")) else "FAIL"})
                except (UnicodeDecodeError, json.JSONDecodeError, IndexError) as exc:
                    # The processor returned, but its artifact cannot be read as
                    # the public UTF-8/JSON contract.  The output itself is the
                    # evidence, so mark both checks determinate FAILs.
                    checks.extend({"id": check_id, "status": "FAIL", "reason": repr(exc),
                                   "failure_origin": "candidate", "failure_stage": "output",
                                   "failure_code": "PROCESSOR_OUTPUT_INVALID",
                                   "source_path": "processor.py"}
                                  for check_id in ("R2_shape", "R3_utf8_semantics"))
                except OSError as exc:
                    checks.extend({"id": check_id, "status": "UNKNOWN", "reason": repr(exc)}
                                  for check_id in ("R2_shape", "R3_utf8_semantics"))
            required = list(RECIPIENT_CHECK_IDS)
        else:
            checks = []
            produced = input_path.with_name("produced.jsonl")
            try:
                event = event_class(**{name: (datetime(2023, 11, 14, 22, 13, 20)
                                              if name == self.timestamp_field else value)
                                       for name, value in canonical.items()})
                producer.produce_events([event], str(produced))
                serialized = json.loads(produced.read_text(encoding="utf-8").splitlines()[0])
                timestamp = serialized.get(self.timestamp_field)
                checks.append({"id": "A1_producer_boundary", "status": "PASS"
                               if isinstance(timestamp, str) and "T" in timestamp and " " not in timestamp
                               else "FAIL"})
            except Exception as exc:
                checks.append({"id": "A1_producer_boundary", "status": "UNKNOWN", "reason": repr(exc)})
            try:
                processor.process_events(str(produced), str(output_path))
                loaded = sink.load_processed_events(str(output_path))
                checks.append({"id": "A2_sink_adoption", "status": "PASS" if len(loaded) == 1 else "FAIL"})
            except Exception as exc:
                checks.append({"id": "A2_sink_adoption", "status": "FAIL", "reason": repr(exc)})
            required = list(ADOPTION_CHECK_IDS)
        complete = len(checks) == len(required) and all(item["status"] in {"PASS", "FAIL"} for item in checks)
        passed = complete and all(item["status"] == "PASS" for item in checks)
        score = sum(item["status"] == "PASS" for item in checks) / len(required) if complete else None
        return {"schema_version": SCHEMA_VERSION, "scorer_version": SCORER_VERSION,
                "task_id": "PIPE3_stream_processing", "seed": None, "mode": self.mode,
                "artifact_sha256": artifact_digest,
                "status": "PASS" if passed else "FAIL" if complete else "UNKNOWN",
                "label": 1 if passed else 0 if complete else None, "quality_score": score,
                "decision_complete": complete, "coverage_complete": complete,
                "checks": checks, "failed_check_ids": [item["id"] for item in checks if item["status"] == "FAIL"],
                "observed_check_count": len(checks), "required_check_ids": required}


def main():
    source, mode, event_class = sys.argv[1:4]
    if mode not in {"recipient", "adoption"}:
        raise SystemExit("unsupported PIPE3 recipient scorer mode")
    scorer = Scorer(source, mode, event_class, None, None)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            required = {"op", "schema_version", "task_id", "seed", "artifact_sha256",
                        "scorer_version", "mode", "event_class", "timestamp_field", "id_field"}
            if set(request) != required or request["op"] != "score_recipient":
                raise ValueError("recipient scorer request fields are invalid")
            if request["schema_version"] != REQUEST_SCHEMA or request["task_id"] != "PIPE3_stream_processing":
                raise ValueError("recipient scorer request schema/task mismatch")
            if request["scorer_version"] != SCORER_VERSION or request["mode"] != mode:
                raise ValueError("recipient scorer version/mode mismatch")
            scorer.event_class_name = request["event_class"]
            scorer.timestamp_field = request["timestamp_field"]
            scorer.id_field = request["id_field"]
            result = scorer.run(request["artifact_sha256"])
            result["seed"] = request["seed"]
            response = {"ok": True, "value": result}
        except Exception as exc:
            response = {"ok": False, "error_type": type(exc).__name__, "message": str(exc)}
        print(json.dumps(response, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
