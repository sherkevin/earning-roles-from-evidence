"""Zero-call PIPE2 runtime, responsibility, and adoption qualification.

This is an engineering qualification for the derived TeamBench adapter.  It
executes public candidate code in the already qualified sandbox and evaluates
the returned artifacts in the parent.  It is not a benchmark score and never
calls an LLM or a GPU.
"""
from __future__ import annotations

import argparse
import ast
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import traceback

from peerrolebench_pipe2_material_adapter_v2 import (
    build_materials, load_pipe2, validate_extracted_rows,
)
from peerrolebench_sandbox import SandboxedWorker


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_pipe2_runtime_worker.py"
RUNNER_VERSION = "pipe2-runtime-adoption-qualification-v2"
SCHEMA_VERSION = "pipe2-runtime-result-v2"
MATERIAL_ADAPTER = "peerrolebench_pipe2_material_adapter_v2"
MATERIAL_ROOT_DIGEST = None
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


def expected_transform(rows: list[dict[str, str]], columns: list[str], limit: int = 255,
                      col_types: list[str] | None = None) -> list[dict[str, str]]:
    # This is the public PIPELINE_SPEC contract instantiated by the parent;
    # it does not inspect the hidden expected output or native tests.
    types = col_types or ["str"] * len(columns)
    return [{column: (row.get(column, "").strip()[:limit]
                      if types[index] == "str" else row.get(column, ""))
             for index, column in enumerate(columns)} for row in rows]


def expected_extraction(source_csv: str, key_columns: list[str]) -> list[dict[str, str]]:
    """Instantiate only the public extract rule from PIPELINE_SPEC."""
    rows = list(csv.DictReader(io.StringIO(source_csv, newline="")))
    return [row for row in rows if all(row.get(column, "").strip() for column in key_columns)]


def public_col_types(transform_source: str) -> list[str]:
    """Read the transform module's public schema constant without executing it."""
    tree = ast.parse(transform_source, filename="pipeline/transform.py")
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "COL_TYPES" for target in node.targets):
            value = ast.literal_eval(node.value)
            if isinstance(value, list) and all(isinstance(item, str) for item in value):
                return value
    raise ValueError("public transform schema does not declare COL_TYPES")


def public_extract_contract(extract_source: str) -> tuple[list[str], list[str]]:
    """Read COLUMNS and KEY_COLUMNS from the public extractor module."""
    tree = ast.parse(extract_source, filename="pipeline/extract.py")
    values: dict[str, list[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if not names or names[0] not in {"COLUMNS", "KEY_COLUMNS"}:
            continue
        value = ast.literal_eval(node.value)
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            values[names[0]] = value
    if "COLUMNS" not in values or "KEY_COLUMNS" not in values:
        raise ValueError("public extractor schema does not declare COLUMNS and KEY_COLUMNS")
    return values["COLUMNS"], values["KEY_COLUMNS"]


def csv_shape_errors(text: str, columns: list[str]) -> list[dict[str, object]]:
    """Detect malformed fixture rows before turning them into peer labels."""
    errors = []
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fieldnames = reader.fieldnames
    if fieldnames is None:
        return [{"row_index": 0, "reason": "missing_header", "keys": []}]
    if len(fieldnames) != len(set(fieldnames)):
        return [{"row_index": 0, "reason": "duplicate_header", "keys": fieldnames}]
    try:
        rows = list(reader)
    except csv.Error as exc:
        return [{"row_index": 0, "reason": "csv_parse_error",
                 "error_type": type(exc).__name__, "error": str(exc)}]
    for index, row in enumerate(rows, start=1):
        missing_values = [column for column in columns if row.get(column) is None]
        if tuple(row) != tuple(columns) or missing_values:
            errors.append({"row_index": index, "keys": list(row),
                           "unexpected_keys": [key for key in row if key not in columns],
                           "missing_values": missing_values})
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
    load, count = re.subn(r"OUTPUT_COLUMNS\s*=\s*\[[^\n]*\]", "OUTPUT_COLUMNS = COLUMNS", load, count=1)
    if count != 1:
        raise ValueError("PIPE2 loader output-column replacement not found")
    result["pipeline/load.py"] = load
    return result


def negative_recipient_controls(source_files: dict[str, str]) -> dict[str, dict[str, str]]:
    """Construct parent-owned mutations used only to test scorer sensitivity."""
    correct = fix_recipient(source_files)
    drop = dict(correct)
    drop["pipeline/transform.py"] += (
        "\n\n# Parent negative control: deliberately drop the final delivered row.\n"
        "def transform(rows: list[dict]) -> list[dict]:\n"
        "    return rows[:-1]\n")
    ignore = dict(correct)
    ignore["pipeline/transform.py"] += (
        "\n\n# Parent negative control: deliberately ignore the sealed artifact.\n"
        "def transform(rows: list[dict]) -> list[dict]:\n"
        "    return []\n")
    return {"drop_row": drop, "ignore_artifact": ignore}


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
        return "UNKNOWN", {"reason": "candidate_runtime_error" if isinstance(response, dict) else "worker_error",
                            "error_type": response.get("error_type") if isinstance(response, dict) else None,
                            "response": response}
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
              "material_schema_version": "peerrolebench-pipe2-materials-v2",
              "material_adapter": MATERIAL_ADAPTER,
              "material_root_digest": MATERIAL_ROOT_DIGEST,
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
            columns, key_columns = public_extract_contract(
                payloads["producer"]["source_files"]["pipeline/extract.py"])
            source_csv = payloads["producer"]["source_files"]["data/source.csv"]
            fixture_errors = {
                "source_csv": csv_shape_errors(source_csv, columns),
                "expected_output_csv": csv_shape_errors(
                    generated.workspace_files["data/expected_output.csv"], columns),
            }
            col_types = public_col_types(payloads["recipient"]["source_files"]["pipeline/transform.py"])
            expected_rows = (expected_extraction(source_csv, key_columns)
                             if not any(fixture_errors.values()) else [])
            base_sources = {path: payloads["producer"]["source_files"][path]
                            for path in ("pipeline/__init__.py", "pipeline/extract.py")}
            producer_controls = {
                "original_producer": base_sources,
                "correct_producer_control": {**base_sources,
                                              "pipeline/extract.py": fix_producer(base_sources["pipeline/extract.py"])},
            }
            seed_case = {"seed": seed, "task_id": generated.task_id, "columns": columns,
                         "key_columns": key_columns, "col_types": col_types,
                         "expected_row_count": len(expected_rows), "producer": {}, "recipient": {},
                         "fixture_shape_errors": fixture_errors,
                         "source_fixture_status": "INVALID_FIXTURE" if fixture_errors["source_csv"] else "VALID",
                         "oracle_fixture_audit_status": "INVALID_FIXTURE" if fixture_errors["expected_output_csv"] else "VALID",
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

            # Evaluate every producer arm against every recipient arm.  The
            # recipient receives that producer arm's sealed artifact; this
            # keeps handoff provenance explicit and prevents the corrected
            # producer from masking an upstream failure.
            # The qualified sandbox executes Python candidates only.  The
            # public Markdown schema remains recorded in the material
            # manifest, while the deterministic runtime receives only the
            # executable source files it can actually load.
            recipient_public = {path: text for path, text in payloads["recipient"]["source_files"].items()
                                if path.endswith(".py")}
            recipient_controls = {"original_recipient": recipient_public,
                                  "correct_recipient_control": fix_recipient(recipient_public)}
            artifact_by_producer = {}
            for producer_arm, producer_result in seed_case["producer"].items():
                rows = producer_result.get("rows")
                if isinstance(rows, list):
                    try:
                        artifact_by_producer[producer_arm] = validate_extracted_rows(rows, columns=columns)
                    except ValueError:
                        artifact_by_producer[producer_arm] = None
                else:
                    artifact_by_producer[producer_arm] = None

            seed_case["recipient"] = {}
            for producer_arm, artifact in artifact_by_producer.items():
                seed_case["recipient"][producer_arm] = {}
                for recipient_arm, sources in recipient_controls.items():
                    if artifact is None:
                        seed_case["recipient"][producer_arm][recipient_arm] = {
                            "status": "UNKNOWN", "label": None,
                            "reason": "no_valid_producer_artifact",
                            "artifact_source": f"producer:{producer_arm}",
                        }
                        continue
                    actual_rows = artifact["rows"]
                    expected_rows_after_transform = expected_transform(actual_rows, columns,
                                                                       col_types=col_types)
                    expected_output = csv_text(expected_rows_after_transform, columns)
                    request = {"op": "transform_load", "artifact": artifact}
                    response, transport = run_worker(
                        sources, "transform_load", request,
                        out / f"seed_{seed}_{producer_arm}_{recipient_arm}", raw,
                        {"seed": seed, "producer_arm": producer_arm,
                         "recipient_arm": recipient_arm, "role": "recipient",
                         "artifact_sha256": artifact["artifact_sha256"],
                         "artifact_source": f"producer:{producer_arm}"})
                    status, value = score_response(response)
                    if status != "OBSERVED":
                        result = {"status": "UNKNOWN", "label": None, "reason": value["reason"],
                                  "transport": transport,
                                  "artifact_sha256": artifact["artifact_sha256"],
                                  "artifact_source": f"producer:{producer_arm}"}
                    else:
                        observed_output = value.get("output_csv")
                        self_ok = observed_output == expected_output
                        parsed = value.get("parsed_rows")
                        source_keys = [tuple(row.get(column) for column in key_columns)
                                       for row in actual_rows]
                        output_keys = ([tuple(row.get(column) for column in key_columns)
                                       for row in parsed] if isinstance(parsed, list) else None)
                        adoption_ok = output_keys == source_keys
                        result = {"status": "PASS" if self_ok else "FAIL", "label": int(self_ok),
                                  "recipient_self": {"status": "PASS" if self_ok else "FAIL", "label": int(self_ok)},
                                  "artifact_adoption": {"status": "PASS" if adoption_ok else "FAIL", "label": int(adoption_ok),
                                                         "source_row_count": len(source_keys),
                                                         "output_row_count": len(output_keys) if output_keys is not None else None,
                                                         "key_columns": key_columns,
                                                         "source_key_sequence": source_keys,
                                                         "output_key_sequence": output_keys},
                                  "output_csv": observed_output, "expected_output_csv": expected_output,
                                  "source_paths": value.get("source_paths"), "transport": transport,
                                  "artifact_sha256": artifact["artifact_sha256"],
                                  "output_sha256": hashlib.sha256((observed_output or "").encode()).hexdigest()
                                  if isinstance(observed_output, str) else None,
                                  "artifact_source": f"producer:{producer_arm}"}
                    seed_case["recipient"][producer_arm][recipient_arm] = result

            # Canary is a separate sensitivity diagnostic.  It uses a
            # synthetic artifact deliberately and can never satisfy lineage.
            canary_rows = [
                {column: (f" canary-{seed}-0 " if column == columns[1] else
                          ("x" * 300 if column == columns[-1] else f"v-{seed}-0-{column}"))
                 for column in columns},
                {column: (f"canary-{seed}-1" if column == columns[1] else "") for column in columns},
            ]
            canary_artifact = validate_extracted_rows(canary_rows, columns=columns)
            seed_case["canary"] = {}
            for arm, sources in recipient_controls.items():
                canary_request = {"op": "transform_load", "artifact": canary_artifact}
                canary_response, canary_transport = run_worker(
                    sources, "transform_load", canary_request,
                    out / f"seed_{seed}_{arm}_canary", raw,
                    {"seed": seed, "recipient_arm": arm, "role": "recipient_canary",
                     "artifact_sha256": canary_artifact["artifact_sha256"],
                     "artifact_source": "synthetic_canary"})
                canary_status, canary_value = score_response(canary_response)
                if canary_status != "OBSERVED":
                    seed_case["canary"][arm] = {"status": "UNKNOWN", "label": None,
                                                  "reason": canary_value["reason"],
                                                  "transport": canary_transport}
                else:
                    canary_output = canary_value.get("output_csv")
                    canary_expected = csv_text(expected_transform(canary_rows, columns,
                                                                  col_types=col_types), columns)
                    canary_ok = canary_output == canary_expected
                    seed_case["canary"][arm] = {"status": "PASS" if canary_ok else "FAIL",
                                                 "label": int(canary_ok),
                                                 "output_csv": canary_output,
                                                 "expected_output_csv": canary_expected,
                                                 "transport": canary_transport}

            # Independent negative controls demonstrate that the parent scorer
            # detects dropped rows and a recipient that ignores its artifact.
            # They are diagnostics only and never enter the handoff labels.
            seed_case["negative_controls"] = {}
            control_artifact = artifact_by_producer.get("correct_producer_control")
            negative_controls = negative_recipient_controls(recipient_public)
            for control_name, sources in negative_controls.items():
                if control_artifact is None:
                    seed_case["negative_controls"][control_name] = {
                        "status": "UNKNOWN", "label": None,
                        "reason": "no_valid_producer_artifact",
                        "expected_detection": "FAIL",
                    }
                    continue
                control_rows = control_artifact["rows"]
                control_expected = csv_text(expected_transform(control_rows, columns,
                                                              col_types=col_types), columns)
                control_request = {"op": "transform_load", "artifact": control_artifact}
                control_response, control_transport = run_worker(
                    sources, "transform_load", control_request,
                    out / f"seed_{seed}_negative_{control_name}", raw,
                    {"seed": seed, "control": control_name, "role": "recipient_negative_control",
                     "artifact_sha256": control_artifact["artifact_sha256"],
                     "artifact_source": "producer:correct_producer_control"})
                control_status, control_value = score_response(control_response)
                if control_status != "OBSERVED":
                    seed_case["negative_controls"][control_name] = {
                        "status": "UNKNOWN", "label": None, "reason": control_value["reason"],
                        "transport": control_transport, "expected_detection": "FAIL"}
                    continue
                control_output = control_value.get("output_csv")
                control_parsed = control_value.get("parsed_rows")
                control_keys = [tuple(row.get(column) for column in key_columns)
                                for row in control_rows]
                output_keys = ([tuple(row.get(column) for column in key_columns)
                                for row in control_parsed] if isinstance(control_parsed, list) else None)
                self_ok = control_output == control_expected
                adoption_ok = output_keys == control_keys
                seed_case["negative_controls"][control_name] = {
                    "status": "PASS" if (not self_ok and not adoption_ok) else "FAIL",
                    "label": int(not self_ok and not adoption_ok),
                    "expected_detection": "FAIL",
                    "recipient_self": {"status": "PASS" if self_ok else "FAIL",
                                       "label": int(self_ok)},
                    "artifact_adoption": {"status": "PASS" if adoption_ok else "FAIL",
                                           "label": int(adoption_ok),
                                           "source_row_count": len(control_keys),
                                           "output_row_count": len(output_keys) if output_keys is not None else None,
                                           "source_key_sequence": control_keys,
                                           "output_key_sequence": output_keys},
                    "output_csv": control_output, "expected_output_csv": control_expected,
                    "transport": control_transport,
                    "artifact_sha256": control_artifact["artifact_sha256"],
                }
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
    handoff_matrix_passed = bool(valid_cases) and len(valid_cases) == len(cases) and all(
        all(case["recipient"][producer_arm]["original_recipient"].get("recipient_self", {}).get("status") == "FAIL" and
            case["recipient"][producer_arm]["correct_recipient_control"].get("recipient_self", {}).get("status") == "PASS" and
            case["recipient"][producer_arm]["original_recipient"].get("artifact_adoption", {}).get("status") == "PASS" and
            case["recipient"][producer_arm]["correct_recipient_control"].get("artifact_adoption", {}).get("status") == "PASS"
            for producer_arm in case["recipient"])
        for case in valid_cases)
    canary_sensitivity_passed = bool(valid_cases) and len(valid_cases) == len(cases) and all(
        case.get("canary", {}).get("original_recipient", {}).get("status") == "FAIL" and
        case.get("canary", {}).get("correct_recipient_control", {}).get("status") == "PASS"
        for case in valid_cases)
    negative_controls_passed = bool(valid_cases) and len(valid_cases) == len(cases) and all(
        all(case.get("negative_controls", {}).get(control, {}).get("status") == "PASS"
            for control in ("drop_row", "ignore_artifact"))
        for case in valid_cases)
    recipient_discrimination = handoff_matrix_passed and canary_sensitivity_passed and negative_controls_passed
    summary = {**config, "status": "QUALIFIED_OFFLINE" if producer_discrimination and recipient_discrimination else "FAILED_OFFLINE",
               "producer_discrimination_passed": producer_discrimination,
               "handoff_matrix_passed": handoff_matrix_passed,
               "canary_sensitivity_passed": canary_sensitivity_passed,
               "negative_controls_passed": negative_controls_passed,
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
