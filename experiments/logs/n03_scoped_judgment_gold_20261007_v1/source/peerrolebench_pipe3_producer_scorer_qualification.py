"""Zero-LLM qualification matrix for the PIPE3 producer scorer.

This is intentionally a root-specific preflight.  It does not alter the
TeamBench checkout, invoke its native grader, or wire PIPE3 into the DIST1
runner.  It only verifies that the sealed producer artifact can receive an
independent, digest-bound Qp score on two same-root seeds.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe3_material_adapter import build_materials  # noqa: E402
from peerrolebench_pipe3_producer_scorer import (  # noqa: E402
    CHECK_IDS, SCHEMA_VERSION, SCORER_VERSION, classify, run_producer_scorer,
)
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402


def interfaces(materials):
    models = materials["agent_payloads"]["producer"]["source_files"]["models.py"]
    producer = materials["agent_payloads"]["producer"]["source_files"]["producer.py"]
    import ast
    tree = ast.parse(models)
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    if len(classes) != 1:
        raise ValueError("PIPE3 models must expose exactly one event class")
    event_class = classes[0].name
    names = [node.target.id for node in classes[0].body
             if isinstance(node, ast.AnnAssign) and hasattr(node.target, "id")]
    timestamp = next(name for name in names if "time" in name or "at" in name)
    identifier = next(name for name in names if "id" in name.lower())
    if "serialize_event" not in producer or "produce_events" not in producer:
        raise ValueError("PIPE3 producer public functions missing")
    return {"event_class": event_class, "timestamp_field": timestamp, "id_field": identifier}


def correct_producer(source, info):
    anchor = "    return json.dumps(data, default=str)"
    replacement = (f'    data["{info["timestamp_field"]}"] = '
                   f'event.{info["timestamp_field"]}.isoformat()\n'
                   "    return json.dumps(data)")
    if anchor not in source:
        raise ValueError("producer correction anchor missing")
    return source.replace(anchor, replacement, 1)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=False, exist_ok=False)
    raw = out / "raw.jsonl"

    def log(event_type, payload):
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False) + "\n")
            handle.flush()

    seeds = [0, 1]
    config = {"qualification_version": "pipe3-producer-scorer-qualification-v3",
              "scorer_version": SCORER_VERSION, "response_schema": SCHEMA_VERSION,
              "task_id": "PIPE3_stream_processing", "seeds": seeds,
              "cases": ["authored_correct", "original_delivery", "syntax_failure"],
              "negative_controls": ["trusted_driver_typeerror", "timeout", "digest_mutation",
                                    "decision_incomplete"],
              "llm_calls": 0, "gpu_jobs": 0, "native_grader_invoked": False,
              "candidate_received_hidden_assertions": False,
              "scientific_claim_allowed": False,
              "root_status": "CONDITIONAL_NOT_FROZEN",
              "repeat_count_frozen_before_execution": True}
    (out / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log("config", config)

    results = []
    correct_envelopes = []
    for seed in seeds:
        materials = build_materials(load_pipe3(seed))
        producer = materials["agent_payloads"]["producer"]["source_files"]
        info = interfaces(materials)
        support = {"models.py": producer["models.py"]}
        cases = [
            ("authored_correct", {"producer.py": correct_producer(producer["producer.py"], info), **support}, "PASS"),
            ("original_delivery", {"producer.py": producer["producer.py"], **support}, "FAIL"),
            ("syntax_failure", {"producer.py": "def broken(:\n", **support}, "FAIL"),
        ]
        for name, files, expected in cases:
            case_dir = out / f"seed_{seed}" / name
            case_dir.parent.mkdir(exist_ok=True)
            result = run_producer_scorer(files, info, "PIPE3_stream_processing", seed, case_dir, log)
            observed = {"seed": seed, "case": name, "expected": expected,
                        "status": result.get("status"), "label": result.get("label"),
                        "quality_score": result.get("quality_score"),
                        "decision_complete": result.get("decision_complete"),
                        "coverage_complete": result.get("coverage_complete"),
                        "failure_code": result.get("failure_code"),
                        "source_path": result.get("source_path"),
                        "response_digest": result.get("response_digest"),
                        "transport": result.get("transport")}
            results.append(observed)
            log("case_result", observed)
            if name == "authored_correct":
                correct_envelopes.append(json.loads((case_dir / "response.json").read_text())["response"])

    controls = []
    expected_digest = correct_envelopes[0]["value"]["artifact_sha256"]
    for name, mutated in [
        ("trusted_driver_typeerror", {"ok": False, "error_type": "TypeError"}),
        ("timeout", {"ok": False, "error_type": "TimeoutError"}),
        ("digest_mutation", copy.deepcopy(correct_envelopes[0])),
        ("decision_incomplete", copy.deepcopy(correct_envelopes[0])),
    ]:
        if name == "digest_mutation":
            mutated["value"]["artifact_sha256"] = "f" * 64
        elif name == "decision_incomplete":
            mutated["value"]["decision_complete"] = False
        result = classify(mutated, expected_digest, "PIPE3_stream_processing", 0)
        item = {"case": name, "expected": "UNKNOWN", "status": result.get("status"),
                "label": result.get("label"), "reason": result.get("reason")}
        controls.append(item)
        log("negative_control", item)

    expected = [(seed, case, status) for seed in seeds for case, status in
                (("authored_correct", "PASS"), ("original_delivery", "FAIL"), ("syntax_failure", "FAIL"))]
    passed_cases = all((item["seed"], item["case"], item["status"]) in expected
                       and item["label"] == (1 if item["status"] == "PASS" else 0)
                       for item in results)
    passed_controls = all(item["status"] == "UNKNOWN" and item["label"] is None for item in controls)
    summary = {**config, "passed": passed_cases and passed_controls,
               "results": results, "negative_controls": controls,
               "scorer_is_qualified": False,
               "scientific_claim_allowed": False,
               "remaining_gates": [
                   "recipient-self and sink-adoption scorers remain separate and unimplemented",
                   "PIPE3 runner root adapter and real ledger replay remain open",
                   "candidate/scorer isolation remains non-adversarial Python instrumentation",
                   "seed 0/1 are one structural root, not independent roots",
               ]}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    print(json.dumps({"passed": summary["passed"], "scorer_is_qualified": False,
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
