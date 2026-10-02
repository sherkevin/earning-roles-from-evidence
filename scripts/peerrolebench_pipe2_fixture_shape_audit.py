"""Audit PIPE2 generated CSV shape without executing candidate code."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

from peerrolebench_pipe2_material_adapter_v2 import TEAMBENCH_COMMIT, load_pipe2


ROOT = Path(__file__).resolve().parents[1]
RUNNER_VERSION = "pipe2-fixture-shape-audit-v2"
MATERIAL_ROOT_DIGEST = None


def errors(text: str, columns: list[str]) -> list[dict[str, object]]:
    result = []
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    fieldnames = reader.fieldnames
    if fieldnames is None:
        return [{"row_index": 0, "reason": "missing_header", "keys": []}]
    if len(fieldnames) != len(set(fieldnames)):
        return [{"row_index": 0, "reason": "duplicate_header", "keys": fieldnames}]
    if fieldnames != columns:
        return [{"row_index": 0, "reason": "header_mismatch", "keys": fieldnames,
                 "expected_keys": columns}]
    try:
        rows = list(reader)
    except csv.Error as exc:
        return [{"row_index": 0, "reason": "csv_parse_error",
                 "error_type": type(exc).__name__, "error": str(exc)}]
    if not rows:
        return [{"row_index": 0, "reason": "empty_data", "keys": fieldnames}]
    for row_index, row in enumerate(rows, start=1):
        missing_values = [column for column in columns if row.get(column) is None]
        if tuple(row) != tuple(columns) or missing_values:
            result.append({"row_index": row_index, "keys": list(row),
                           "unexpected_keys": [key for key in row if key not in columns],
                           "missing_values": missing_values})
    return result


def run(out_dir: Path, seeds: list[int]) -> dict:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    raw = out_dir / "raw.jsonl"
    source_repo = ROOT / "references/benchmark_sources/TeamBench"
    source_commit = subprocess.check_output(["git", "-C", str(source_repo), "rev-parse", "HEAD"], text=True).strip()
    source_status = subprocess.check_output(["git", "-C", str(source_repo), "status", "--porcelain"], text=True)
    generator = source_repo / "generators/gen_pipe2_data_pipeline.py"
    registry = source_repo / "generators/registry.py"
    config = {"runner_version": RUNNER_VERSION, "task_id": "PIPE2_data_pipeline",
              "seeds": seeds,
              "source_commit": source_commit, "expected_source_commit": TEAMBENCH_COMMIT,
              "source_commit_matches_expected": source_commit == TEAMBENCH_COMMIT,
              "source_worktree_dirty": bool(source_status),
              "generator_sha256": hashlib.sha256(generator.read_bytes()).hexdigest(),
              "material_root_digest": MATERIAL_ROOT_DIGEST,
              "registry_sha256": hashlib.sha256(registry.read_bytes()).hexdigest(),
              "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "llm_calls": 0, "gpu_jobs": 0, "candidate_code_executed": False,
              "native_grader_invoked": False, "scientific_claim_allowed": False,
              "started_at_utc": datetime.now(timezone.utc).isoformat()}
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    cases = []
    for seed in seeds:
        try:
            generated = load_pipe2(seed)
            columns = list(generated.expected["columns"])
            workspace_digest = hashlib.sha256(json.dumps(
                generated.workspace_files, ensure_ascii=False, sort_keys=True,
                separators=(",", ":")).encode()).hexdigest()
            case = {"seed": seed, "schema_name": generated.expected["schema_name"],
                    "structural_root": f"TeamBench@{TEAMBENCH_COMMIT}/PIPE2_data_pipeline",
                    "schema_index": seed % 5,
                    "columns": columns,
                    "workspace_sha256": workspace_digest,
                    "source_csv_sha256": hashlib.sha256(
                        generated.workspace_files["data/source.csv"].encode()).hexdigest(),
                    "expected_output_sha256": hashlib.sha256(
                        generated.workspace_files["data/expected_output.csv"].encode()).hexdigest(),
                    "source_errors": errors(generated.workspace_files["data/source.csv"], columns),
                    "expected_output_errors": errors(generated.workspace_files["data/expected_output.csv"], columns)}
            case["status"] = "INVALID_FIXTURE" if case["source_errors"] or case["expected_output_errors"] else "VALID"
        except Exception as exc:
            case = {"seed": seed, "status": "UNKNOWN", "error_type": type(exc).__name__,
                    "error": str(exc)}
        cases.append(case)
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": "fixture_shape", "payload": case}) + "\n")
    valid = [case["seed"] for case in cases if case["status"] == "VALID"]
    invalid = [case["seed"] for case in cases if case["status"] == "INVALID_FIXTURE"]
    unknown = [case["seed"] for case in cases if case["status"] == "UNKNOWN"]
    preconditions_passed = source_commit == TEAMBENCH_COMMIT and not source_status
    summary = {**config, "status": "AUDITED" if preconditions_passed else "AUDIT_PRECONDITION_FAILED", "cases": cases,
               "valid_seeds": valid, "invalid_seeds": invalid,
               "public_seed_range": [seed for seed in seeds if seed <= 2],
               "public_invalid_count": sum(case["status"] == "INVALID_FIXTURE" for case in cases if case["seed"] <= 2),
               "hidden_seed_range": [seed for seed in seeds if 3 <= seed <= 9],
               "hidden_invalid_count": sum(case["status"] == "INVALID_FIXTURE" for case in cases if 3 <= case["seed"] <= 9),
               "unknown_seeds": unknown,
               "invalid_fixture_seeds": invalid,
               "out_of_protocol_seeds": [seed for seed in seeds if seed < 0 or seed > 9],
               "preconditions_passed": preconditions_passed,
               "benchmark_qualified": False, "scientific_claim_allowed": False,
               "ended_at_utc": datetime.now(timezone.utc).isoformat(),
               "interpretation": "Generator/data-shape audit only; no candidate code, LLM, GPU, native score, or peer label."}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    with raw.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                 "event_type": "summary", "payload": summary}) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    args = parser.parse_args()
    result = run(args.output, args.seeds)
    print(json.dumps({key: result[key] for key in
                      ("status", "valid_seeds", "invalid_seeds", "public_invalid_count", "hidden_invalid_count")}, indent=2))
