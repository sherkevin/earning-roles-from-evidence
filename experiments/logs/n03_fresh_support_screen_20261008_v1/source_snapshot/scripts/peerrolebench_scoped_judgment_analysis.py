"""Post-hoc audit of the stopped real diagnostic; no provider or artifact execution."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

from peerrolebench_real_closed_loop import log, save

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "experiments/logs/n03_scoped_judgment_real_20261008_v1"
PREPARED = ROOT / "experiments/logs/n03_scoped_judgment_prepare_20261007_v2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(out):
    out.mkdir(parents=True, exist_ok=False)
    inputs = [RUN / "config.json", RUN / "summary.json", RUN / "raw.jsonl",
              PREPARED / "parent_manifest.json", Path(__file__).resolve()]
    for index in (0, 1):
        inputs.extend(sorted((RUN / f"case_{index}").glob("*.json")))
        inputs.append(RUN / f"case_{index}" / "judgment_response.sse")
    config = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "python": sys.version, "platform": platform.platform(), "command": sys.argv,
              "input_sha256": {str(p.relative_to(ROOT)): sha(p) for p in inputs},
              "purpose": "Exact request/response audit plus a standard-library fact reproduction",
              "api_calls": 0, "candidate_executions": 0, "gpu_jobs": 0,
              "probe_datetime_components": [2026, 4, 15, 9, 12, 34]}
    save(out / "config.json", config)
    log(out, "analysis_config", config)
    cases = json.loads((PREPARED / "parent_manifest.json").read_text())["cases"]
    source_summary = json.loads((RUN / "summary.json").read_text())
    assert source_summary["status"] == "STOPPED" and source_summary["request_starts"] == 2
    assert [c["status"] for c in source_summary["cells"]] == ["PASS", "FAILED", "UNSTARTED", "UNSTARTED"]
    rows = []
    for index in (0, 1):
        case = cases[index]
        sent = json.loads((RUN / f"case_{index}" / "judgment_request.json").read_text())
        frozen = json.loads((PREPARED / case["request_path"]).read_text())
        assert sent["messages"] == frozen["messages"]
        answer = json.loads((RUN / f"case_{index}" / "answer.json").read_text())
        cost = json.loads((RUN / f"case_{index}" / "judgment_cost.json").read_text())
        p, r = answer["producer_contract_assessment"], answer["recipient_integration_plan"]
        row = {"case_id": case["case_id"], "producer_expected": case["expected_producer_verdict"],
               "producer_observed": p["verdict"], "recipient_expected": case["expected_recipient_needs_change"],
               "recipient_observed": r["needs_change"], "producer_correct": p["verdict"] == case["expected_producer_verdict"],
               "recipient_correct": r["needs_change"] is case["expected_recipient_needs_change"],
               "public_prompt_unchanged": True, "usage": cost["usage"], "elapsed_seconds": cost["elapsed_seconds"]}
        rows.append(row)
        log(out, "real_response_audit", row)
    instant = datetime(*config["probe_datetime_components"])
    fact = {"str_datetime": str(instant), "isoformat_datetime": instant.isoformat(),
            "json_default_str": json.dumps({"timestamp": instant}, default=str)}
    fact["json_timestamp"] = json.loads(fact["json_default_str"])["timestamp"]
    fact["str_separator"] = fact["str_datetime"][10]
    fact["isoformat_separator"] = fact["isoformat_datetime"][10]
    fact["json_separator"] = fact["json_timestamp"][10]
    log(out, "stdlib_runtime_observation", fact)
    assert fact["str_separator"] == fact["json_separator"] == " " and fact["isoformat_separator"] == "T"
    result = {"status": "FALSE_PRODUCER_ACCEPT_WITH_WRONG_RUNTIME_PREMISE", "rows": rows,
              "runtime_observation": fact, "new_api_calls": 0, "source_api_calls": 2,
              "documented_cumulative_episode_attempts": 33, "documented_cumulative_task_request_starts": 70,
              "unstarted_cells": 2, "missing_usage_requests": 0,
              "source_input_tokens": sum(r["usage"]["input_tokens"] for r in rows),
              "source_output_tokens": sum(r["usage"]["output_tokens"] for r in rows),
              "source_elapsed_seconds": sum(r["elapsed_seconds"] for r in rows),
              "scientific_claim_allowed": False,
              "scope": "Stopped fixed-case prefix, not population accuracy; source results unchanged."}
    save(out / "summary.json", result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
