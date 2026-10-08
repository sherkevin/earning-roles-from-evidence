"""Zero-API qualification for the private PIPE3 terminal holdout scorer."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe3_material_adapter import build_materials  # noqa: E402
from peerrolebench_pipe3_producer_scorer_qualification import interfaces  # noqa: E402
from peerrolebench_pipe3_task_qualification import load_pipe3  # noqa: E402
from peerrolebench_pipe3_terminal_scorer_v1 import classify, run_terminal_scorer  # noqa: E402


def correct_producer(source: str, timestamp: str) -> str:
    anchor = "    return json.dumps(data, default=str)"
    replacement = f'    data["{timestamp}"] = event.{timestamp}.isoformat()\n    return json.dumps(data)'
    if anchor not in source:
        raise ValueError("producer correction anchor missing")
    return source.replace(anchor, replacement, 1)


def correct_processor(source: str) -> str:
    source = source.replace('open(output_path, "w", encoding="latin-1")',
                            'open(output_path, "w", encoding="utf-8")', 1)
    old = '            envelope = {"data": processed}\n            fout.write(json.dumps(envelope, ensure_ascii=False) + "\\n")'
    if old not in source:
        raise ValueError("processor envelope correction anchor missing")
    return source.replace(old, '            fout.write(json.dumps(processed, ensure_ascii=False) + "\\n")', 1)


def run(out_dir: Path) -> dict:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    config = {
        "experiment_id": out_dir.name,
        "qualification_version": "pipe3-terminal-holdout-qualification-v1",
        "task_id": "PIPE3_stream_processing", "seed": 0,
        "cases": ["correct_both", "original", "producer_only_fixed"],
        "real_api_calls": 0, "gpu_jobs": 0, "native_grader_invoked": False,
        "candidate_received_hidden_assertions": False,
        "scientific_claim_allowed": False,
        "platform": platform.platform(), "python": platform.python_version(),
        "git_commit": commit, "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    raw = out_dir / "raw.jsonl"

    def log(event_type, payload):
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()

    materials = build_materials(load_pipe3(0))
    info = interfaces(materials)
    base = dict(materials["agent_payloads"]["recipient"]["source_files"])
    # The recipient payload already contains the producer delivery slot only
    # after attachment; use the complete public snapshot for the worker.
    base = {
        "producer.py": materials["agent_payloads"]["producer"]["source_files"]["producer.py"],
        "processor.py": materials["agent_payloads"]["recipient"]["source_files"]["processor.py"],
        "models.py": materials["agent_payloads"]["recipient"]["source_files"]["models.py"],
        "sink.py": materials["agent_payloads"]["recipient"]["source_files"]["sink.py"],
    }
    cases = {
        "correct_both": {**base,
                         "producer.py": correct_producer(base["producer.py"], info["timestamp_field"]),
                         "processor.py": correct_processor(base["processor.py"])},
        "original": base,
        "producer_only_fixed": {**base,
                                 "producer.py": correct_producer(base["producer.py"], info["timestamp_field"])},
    }
    holdout_info = {
        **info,
        "user_field": next(name for name in ("user_name", "sensor_name", "account_holder") if name in base["models.py"]),
        "action_field": next(name for name in ("action", "metric_type", "txn_type") if name in base["models.py"]),
        "value_field": next(name for name in ("page_url", "location", "description") if name in base["models.py"]),
        "action_value": "page_view" if "page_view" in base["models.py"] else "temperature" if "temperature" in base["models.py"] else "transfer",
        "user_value": "Müller", "value_value": "Price: €99.99",
    }
    results = []
    for name, sources in cases.items():
        result = run_terminal_scorer(sources, holdout_info, "PIPE3_stream_processing", 0,
                                     out_dir / name, log)
        item = {"case": name, "status": result.get("status"), "label": result.get("label"),
                "quality_score": result.get("quality_score"), "coverage_complete": result.get("coverage_complete"),
                "response_digest": result.get("response_digest"), "transport": result.get("transport")}
        results.append(item); log("case_result", item)

    correct = next(item for item in results if item["case"] == "correct_both")
    original = next(item for item in results if item["case"] == "original")
    partial = next(item for item in results if item["case"] == "producer_only_fixed")
    # A response digest mutation must become UNKNOWN before any policy can see it.
    correct_response = json.loads((out_dir / "correct_both" / "response.json").read_text())["response"]
    expected_digest = correct_response["artifact_sha256"]
    holdout_digest = correct_response["holdout_digest"]
    mutated = dict(correct_response); mutated["artifact_sha256"] = "f" * 64
    mutation_result = classify(mutated, expected_digest, holdout_digest, "PIPE3_stream_processing", 0)
    controls = {"artifact_digest_mutation": mutation_result}
    summary = {**config, "passed": (
        correct["status"] == "PASS" and correct["label"] == 1
        and original["status"] == "FAIL" and original["label"] == 0
        and partial["status"] == "FAIL" and partial["label"] == 0
        and mutation_result["status"] == "UNKNOWN" and mutation_result["label"] is None
    ), "results": results, "negative_controls": controls,
               "worker_is_qualified": False,
               "scope": "private worker boundary and holdout projection only; no live API, independent root, policy update, or efficacy claim",
               "ended_at_utc": datetime.now(timezone.utc).isoformat()}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    print(json.dumps({"passed": summary["passed"], "worker_is_qualified": False,
                      "scientific_claim_allowed": False}, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
