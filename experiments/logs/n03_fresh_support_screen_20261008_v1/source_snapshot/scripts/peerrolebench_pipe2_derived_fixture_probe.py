"""Probe a CSV-writer repair overlay without changing TeamBench or its hashes.

This is decision support for the PIPE2 authority options.  It reconstructs the
same generator semantics from the pinned public schema rows, serializes them
with ``csv.DictWriter``, and reports whether the repaired bytes are shape-valid
and semantically identical to the intended logical rows.  The output is not a
benchmark fixture, does not replace the pinned generator, and never executes a
candidate, LLM, native grader, or GPU job.
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

ROOT = Path(__file__).resolve().parents[1]
TEAMBENCH = ROOT / "references/benchmark_sources/TeamBench"
TEAMBENCH_COMMIT = "d185aef1916fd86a9ba554d581fd256319a973af"
OVERLAY_VERSION = "pipe2-csv-writer-probe-v1"
sys.path.insert(0, str(TEAMBENCH))
sys.path.insert(0, str(ROOT / "scripts"))

from generators.gen_pipe2_data_pipeline import SCHEMAS  # noqa: E402
from peerrolebench_pipe2_material_adapter_v2 import load_pipe2  # noqa: E402


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def csv_text(rows: list[list[str]], columns: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(columns)
    writer.writerows(rows)
    return stream.getvalue()


def parsed_shape(text: str, columns: list[str]) -> dict[str, object]:
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    fieldnames = reader.fieldnames
    if fieldnames != columns:
        return {"status": "INVALID", "reason": "header_mismatch", "fieldnames": fieldnames}
    try:
        rows = list(reader)
    except csv.Error as exc:
        return {"status": "INVALID", "reason": "csv_parse_error", "error": str(exc)}
    if not rows:
        return {"status": "INVALID", "reason": "empty_data", "row_count": 0}
    missing = [
        index for index, row in enumerate(rows, start=1)
        if any(row.get(column) is None for column in columns)
    ]
    return {"status": "VALID" if not missing else "INVALID",
            "row_count": len(rows), "missing_value_rows": missing,
            "rows": rows}


def logical_rows(schema: dict) -> tuple[list[list[str]], list[list[str]]]:
    columns = list(schema["columns"])
    key_columns = list(schema["key_columns"])
    rows = [list(row) for row in schema["rows"]]
    kept = [row for row in rows if all(row[columns.index(key)].strip() for key in key_columns)]
    transformed = []
    for row in kept:
        transformed.append([
            value[: int(schema["truncation_limit"])]
            if schema["col_types"][index] == "str" and len(value) > int(schema["truncation_limit"])
            else value
            for index, value in enumerate(row)
        ])
    return rows, transformed


def probe_seed(seed: int) -> dict[str, object]:
    generated = load_pipe2(seed)
    schema = SCHEMAS[seed % len(SCHEMAS)]
    columns = list(schema["columns"])
    source_rows, expected_rows = logical_rows(schema)
    derived_source = csv_text(source_rows, columns)
    derived_expected = csv_text(expected_rows, columns)
    original_source = generated.workspace_files["data/source.csv"]
    original_expected = generated.workspace_files["data/expected_output.csv"]
    source_shape = parsed_shape(derived_source, columns)
    expected_shape = parsed_shape(derived_expected, columns)
    return {
        "seed": seed,
        "schema_name": schema["name"],
        "schema_index": seed % len(SCHEMAS),
        "columns": columns,
        "key_columns": list(schema["key_columns"]),
        "source_shape": {key: value for key, value in source_shape.items() if key != "rows"},
        "expected_shape": {key: value for key, value in expected_shape.items() if key != "rows"},
        "derived_source_sha256": sha_bytes(derived_source.encode()),
        "derived_expected_sha256": sha_bytes(derived_expected.encode()),
        "original_source_sha256": sha_bytes(original_source.encode()),
        "original_expected_sha256": sha_bytes(original_expected.encode()),
        "source_logical_row_count": len(source_rows),
        "expected_logical_row_count": len(expected_rows),
        "derived_valid": source_shape["status"] == "VALID" and expected_shape["status"] == "VALID",
        "original_bytes_identical": original_source == derived_source and original_expected == derived_expected,
        "semantic_overlay": "same schema rows, key-column filtering, string truncation; serialization only",
    }


def run(out_dir: Path, seeds: list[int]) -> dict[str, object]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    raw = out_dir / "raw.jsonl"
    source_path = TEAMBENCH / "generators/gen_pipe2_data_pipeline.py"
    actual_commit = subprocess.check_output(["git", "-C", str(TEAMBENCH), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(TEAMBENCH), "status", "--porcelain"], text=True)
    derived_root = sha_bytes(json.dumps({
        "base_commit": TEAMBENCH_COMMIT,
        "generator_sha256": sha_bytes(source_path.read_bytes()),
        "overlay_version": OVERLAY_VERSION,
    }, sort_keys=True).encode())
    config = {
        "runner_version": OVERLAY_VERSION,
        "base_commit": TEAMBENCH_COMMIT,
        "actual_commit": actual_commit,
        "base_commit_matches": actual_commit == TEAMBENCH_COMMIT,
        "source_worktree_dirty": bool(dirty),
        "generator_sha256": sha_bytes(source_path.read_bytes()),
        "derived_root_digest": derived_root,
        "seeds": seeds,
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "candidate_code_executed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "benchmark_fixture_written": False,
        "scientific_claim_allowed": False,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    cases = []
    with raw.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                 "event_type": "config", "payload": config}, ensure_ascii=False) + "\n")
        for seed in seeds:
            case = probe_seed(seed)
            cases.append(case)
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": "derived_fixture_probe", "payload": case},
                                    ensure_ascii=False) + "\n")
    summary = {
        **config,
        "status": "PROBE_COMPLETE" if config["base_commit_matches"] and not config["source_worktree_dirty"]
        else "PROBE_PRECONDITION_FAILED",
        "derived_fixture_valid_seeds": [case["seed"] for case in cases if case["derived_valid"]],
        "derived_fixture_invalid_seeds": [case["seed"] for case in cases if not case["derived_valid"]],
        "original_bytes_changed_seeds": [case["seed"] for case in cases if not case["original_bytes_identical"]],
        "original_bytes_preserved_seeds": [case["seed"] for case in cases if case["original_bytes_identical"]],
        "cases": cases,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        "interpretation": "Authority option A probe only; the derived root is not an active benchmark and no label is emitted.",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    with raw.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                 "event_type": "summary", "payload": summary}, ensure_ascii=False) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    args = parser.parse_args()
    result = run(args.output, args.seeds)
    print(json.dumps({key: result[key] for key in (
        "status", "derived_root_digest", "derived_fixture_valid_seeds",
        "derived_fixture_invalid_seeds", "original_bytes_changed_seeds",
        "original_bytes_preserved_seeds")}, indent=2))
