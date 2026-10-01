"""Zero-call PIPE2 runtime, responsibility, and adoption qualification.

This is an engineering qualification for the derived TeamBench adapter.  It
executes public candidate code in the already qualified sandbox and evaluates
the returned artifacts in the parent.  It is not a benchmark score and never
calls an LLM or a GPU.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback

from peerrolebench_pipe2_material_adapter import (
    build_materials, load_pipe2, validate_extracted_rows,
)
from peerrolebench_sandbox import SandboxedWorker


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_pipe2_runtime_worker.py"
RUNNER_VERSION = "pipe2-runtime-adoption-qualification-v1"
SCHEMA_VERSION = "pipe2-runtime-result-v1"
UNKNOWN_ERRORS = (TimeoutError, PermissionError, OSError, RuntimeError, ValueError, TypeError, KeyError)


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def parse_csv(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text)))


def csv_text(rows: list[dict[str, str]], columns: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows({column: row.get(column, "") for column in columns} for row in rows)
    return stream.getvalue()


def expected_transform(rows: list[dict[str, str]], columns: list[str], limit: int = 255) -> list[dict[str, str]]:
    # This is the public PIPELINE_SPEC contract instantiated by the parent;
    # it does not inspect the hidden expected output or native tests.
    return [{column: row.get(column, "").strip()[:limit] for column in columns}
            for row in rows]


def csv_shape_errors(text: str, columns: list[str]) -> list[dict[str, object]]:
    """Detect malformed fixture rows before turning them into peer labels."""
    errors = []
    for index, row in enumerate(csv.DictReader(io.StringIO(text)), start=1):
        if tuple(row) != tuple(columns):
            errors.append({"row_index": index, "keys": list(row),
                           "unexpected_keys": [key for key in row if key not in columns]})
    return errors


def fix_producer(source: str) -> str:
    old = "if all(row.get(col, \"\").strip() for col in COLUMNS):"
    new = "if all(row.get(col, \"\").strip() for col in KEY_COLUMNS):"
    if old not in source:
        raise ValueError("PIPE2 producer control replacement not found")
    return source.replace(old, new)


def fix_recipient(source_files: dict[str, str]) -> dict[str, str]:
    result = dict(source_files)
    transform = result["pipeline/transform.py"]
    transform = transform.replace("TRUNCATION_LIMIT = 50", "TRUNCATION_LIMIT = 255")
    result["pipeline/transform.py"] = transform
    load = result["pipeline/load.py"]
    load = load.replace("OUTPUT_COLUMNS = ['emp_id', 'department', 'full_name', 'notes']",
                        "OUTPUT_COLUMNS = COLUMNS")
    load = load.replace("OUTPUT_COLUMNS = ['product_id', 'category', 'product_name', 'description']",
                        "OUTPUT_COLUMNS = COLUMNS")
    load = load.replace("OUTPUT_COLUMNS = ['txn_id', 'amount', 'account_name', 'memo']",
                        "OUTPUT_COLUMNS = COLUMNS")
    result["pipeline/load.py"] = load
    return result


def log_event(raw: Path, event_type: str, payload: object) -> None:
    with raw.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                 "event_type": event_type, "payload": payload},
                                ensure_ascii=False) + "\n")
        handle.flush()


def run_worker(sources: dict[str, str], op: str, request: dict, evidence: Path, raw: Path,
               log_payload: dict) -> tuple[dict | None, dict]:
    evidence.mkdir(parents=False, exist_ok=False)
    config = {"runner_version": RUNNER_VERSION, "schema_version": SCHEMA_VERSION,
              "worker": str(WORKER.relative_to(ROOT)),
              "worker_sha256": hashlib.sha256(WORKER.read_bytes()).hexdigest(),
              "candidate_source_sha256": {path: hashlib.sha256(text.encode()).hexdigest()
                                           for path, text in sorted(sources.items())},
              "operation": op, "request_digest": digest(request),
              "candidate_received_hidden_assertions": False, "scientific_claim_allowed": False,
              **log_payload}
    (evidence / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log_event(raw, "sandbox_config", config)
    response = None
    transport = {"status": "not_started"}
    try:
        with SandboxedWorker(sources, evidence / "sandbox", lambda event, payload: log_event(
                raw, "sandbox." + event, payload), "unused", "unused", worker_path=WORKER,
                rpc_seconds=20, max_input_bytes=64 * 1024,
                source_prefixes=("pipeline/",)) as worker:
            response = worker.request(request)
        transport = {"status": "complete"}
    except UNKNOWN_ERRORS as exc:
        transport = {"status": "error", "error_type": type(exc).__name__, "message": str(exc)}
    result_payload = {"request": request, "response": response, "transport": transport,
                      "response_digest": digest(response) if response is not None else None}
    (evidence / "response.json").write_text(json.dumps(result_payload, indent=2, ensure_ascii=False) + "\n")
    log_event(raw, "sandbox_result", result_payload)
    return response, transport


def score_response(response: dict | None) -> tuple[str, object]:
    if not isinstance(response, dict) or response.get("ok") is not True:
        return "UNKNOWN", {"reason": "worker_error", "response": response}
    value = response.get("value")
    if not isinstance(value, dict):
        return "UNKNOWN", {"reason": "malformed_worker_value"}
    return "OBSERVED", value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    raw = out / "raw.jsonl"
    config = {"runner_version": RUNNER_VERSION, "schema_version": SCHEMA_VERSION,
              "task_id": "PIPE2_data_pipeline", "seeds": args.seeds,
              "python": sys.version, "platform": platform.platform(), "command": sys.argv,
              "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "working_tree_dirty": True, "worker_sha256": hashlib.sha256(WORKER.read_bytes()).hexdigest(),
              "llm_calls": 0, "gpu_jobs": 0, "native_grader_invoked": False,
              "candidate_code_executed": True, "scientific_claim_allowed": False,
              "score_dimensions": ["producer_contract", "recipient_self", "artifact_adoption"],
              "unknown_policy": "transport, malformed response, and runtime/resource errors remain UNKNOWN",
              "started_at_utc": datetime.now(timezone.utc).isoformat()}
    (out / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    log_event(raw, "config", config)
    cases = []
    try:
        for seed in args.seeds:
            generated = load_pipe2(seed)
            materials = build_materials(generated)
            payloads = materials["agent_payloads"]
            columns = list(generated.expected["columns"])
            expected_rows = parse_csv(generated.workspace_files["data/expected_output.csv"])
            source_csv = payloads["producer"]["source_files"]["data/source.csv"]
            fixture_errors = {
                "source_csv": csv_shape_errors(source_csv, columns),
                "expected_output_csv": csv_shape_errors(
                    generated.workspace_files["data/expected_output.csv"], columns),
            }
            base_sources = {path: payloads["producer"]["source_files"][path]
                            for path in ("pipeline/__init__.py", "pipeline/extract.py")}
            producer_controls = {
                "original_producer": base_sources,
                "correct_producer_control": {**base_sources,
                                              "pipeline/extract.py": fix_producer(base_sources["pipeline/extract.py"])},
            }
            seed_case = {"seed": seed, "task_id": generated.task_id, "columns": columns,
                         "expected_row_count": len(expected_rows), "producer": {}, "recipient": {},
                         "fixture_shape_errors": fixture_errors,
                         "fixture_status": "INVALID_FIXTURE" if any(fixture_errors.values()) else "VALID"}
            if seed_case["fixture_status"] == "INVALID_FIXTURE":
                seed_case["reason"] = "CSV rows contain undeclared fields; no peer label is emitted"
                cases.append(seed_case)
                log_event(raw, "invalid_fixture", seed_case)
                continue
            for arm, sources in producer_controls.items():
                request = {"op": "extract", "csv_text": source_csv, "columns": columns}
                response, transport = run_worker(
                    sources, "extract", request, out / f"seed_{seed}_{arm}", raw,
                    {"seed": seed, "arm": arm, "role": "producer"})
                status, value = score_response(response)
                if status != "OBSERVED":
                    result = {"status": "UNKNOWN", "label": None, "reason": value["reason"],
                              "transport": transport}
                else:
                    rows = value.get("rows")
                    producer_ok = rows == expected_rows
                    try:
                        artifact = validate_extracted_rows(rows, columns=columns) if isinstance(rows, list) else None
                        artifact_error = None
                    except ValueError as exc:
                        artifact = None
                        artifact_error = str(exc)
                    producer_ok = producer_ok and artifact is not None
                    result = {"status": "PASS" if producer_ok else "FAIL", "label": int(producer_ok),
                              "rows": rows, "row_count": len(rows) if isinstance(rows, list) else None,
                              "expected_row_count": len(expected_rows),
                              "artifact_sha256": artifact["artifact_sha256"] if artifact else None,
                              "artifact_error": artifact_error,
                              "source_path": value.get("source_path"), "transport": transport}
                seed_case["producer"][arm] = result

            # Recipient evaluation uses a sealed, schema-valid artifact that
            # includes a canary row and an overlong field.  This isolates the
            # recipient's responsibility from upstream extraction quality.
            canary_rows = [
                {column: (f" canary-{seed}-0 " if column == columns[1] else
                          ("x" * 300 if column == columns[-1] else f"v-{seed}-0-{column}"))
                 for column in columns},
                {column: (f"canary-{seed}-1" if column == columns[1] else "") for column in columns},
            ]
            artifact = validate_extracted_rows(canary_rows, columns=columns)
            recipient_public = {path: payloads["recipient"]["source_files"][path]
                                for path in ("pipeline/__init__.py", "pipeline/transform.py",
                                             "pipeline/load.py")}
            recipient_controls = {"original_recipient": recipient_public,
                                  "correct_recipient_control": fix_recipient(recipient_public)}
            expected_rows_after_transform = expected_transform(canary_rows, columns)
            expected_output = csv_text(expected_rows_after_transform, columns)
            for arm, sources in recipient_controls.items():
                request = {"op": "transform_load", "artifact": artifact}
                response, transport = run_worker(
                    sources, "transform_load", request, out / f"seed_{seed}_{arm}", raw,
                    {"seed": seed, "arm": arm, "role": "recipient", "artifact_sha256": artifact["artifact_sha256"]})
                status, value = score_response(response)
                if status != "OBSERVED":
                    result = {"status": "UNKNOWN", "label": None, "reason": value["reason"],
                              "transport": transport, "artifact_sha256": artifact["artifact_sha256"]}
                else:
                    observed_output = value.get("output_csv")
                    self_ok = observed_output == expected_output
                    parsed = value.get("parsed_rows")
                    adoption_ok = isinstance(parsed, list) and any(
                        row.get(columns[1]) == f"canary-{seed}-1" for row in parsed)
                    result = {"status": "PASS" if self_ok else "FAIL", "label": int(self_ok),
                              "recipient_self": {"status": "PASS" if self_ok else "FAIL", "label": int(self_ok)},
                              "artifact_adoption": {"status": "PASS" if adoption_ok else "FAIL", "label": int(adoption_ok)},
                              "output_csv": observed_output, "expected_output_csv": expected_output,
                              "source_paths": value.get("source_paths"), "transport": transport,
                              "artifact_sha256": artifact["artifact_sha256"]}
                seed_case["recipient"][arm] = result
            cases.append(seed_case)
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        log_event(raw, "qualification_failure", error)
        summary = {**config, "status": "FAILED_OFFLINE", "cases": cases, "error": error,
                   "ended_at_utc": datetime.now(timezone.utc).isoformat()}
        (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
        return 1
    valid_cases = [case for case in cases if case.get("fixture_status") == "VALID"]
    producer_discrimination = bool(valid_cases) and len(valid_cases) == len(cases) and all(
        case["producer"]["original_producer"]["status"] == "FAIL" and
        case["producer"]["correct_producer_control"]["status"] == "PASS" for case in valid_cases)
    recipient_discrimination = bool(valid_cases) and len(valid_cases) == len(cases) and all(
        case["recipient"]["original_recipient"].get("recipient_self", {}).get("status") == "FAIL" and
        case["recipient"]["correct_recipient_control"].get("recipient_self", {}).get("status") == "PASS" and
        case["recipient"]["correct_recipient_control"].get("artifact_adoption", {}).get("status") == "PASS"
        for case in valid_cases)
    summary = {**config, "status": "QUALIFIED_OFFLINE" if producer_discrimination and recipient_discrimination else "FAILED_OFFLINE",
               "producer_discrimination_passed": producer_discrimination,
               "recipient_discrimination_passed": recipient_discrimination,
               "valid_case_count": len(valid_cases),
               "invalid_fixture_count": len(cases) - len(valid_cases),
               "runtime_adoption_scorer_qualified": producer_discrimination and recipient_discrimination,
               "benchmark_qualified": False, "scientific_claim_allowed": False,
               "cases": cases, "ended_at_utc": datetime.now(timezone.utc).isoformat(),
               "interpretation": "Actual PIPE2 producer/recipient code execution and parent-side responsibility/adoption checks only; no LLM, GPU, native score, or efficacy claim."}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log_event(raw, "summary", summary)
    print(json.dumps({key: summary[key] for key in
                      ("status", "producer_discrimination_passed", "recipient_discrimination_passed",
                       "runtime_adoption_scorer_qualified", "scientific_claim_allowed")}, indent=2))
    return 0 if summary["runtime_adoption_scorer_qualified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
