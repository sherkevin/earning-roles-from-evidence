#!/usr/bin/env python3
"""Capture original PIPE1 Planner/Executor information cuts for four seeds.

This is an offline native-material audit: one generator call per seed, static
JSON/AST checks, and no candidate, grader, model, API, or GPU execution. The
Planner's full private spec is preserved. Executor sees the native brief and
four workspace files, with one empty peer-message slot for a later study.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import traceback
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEAMBENCH = ROOT / "references/benchmark_sources/TeamBench"
PIN = "d185aef1916fd86a9ba554d581fd256319a973af"
GENERATOR_REL = "generators/gen_pipe1_etl_fix.py"
TASK_ID = "PIPE1_etl_fix"
SEEDS = (0, 1, 2, 3)
WORKSPACE_PATHS = {"etl.py", "run_etl.py", "source_sample.json", "target_schema.json"}
EXPECTED_KEYS = {"domain", "record_count", "target_fields", "field_map", "null_rules", "records"}
DOMAINS = ("ecommerce", "healthcare", "financial", "logistics")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha_text(value: str) -> str:
    return _sha(value.encode("utf-8"))


def _sha_file(path: Path) -> str:
    return _sha(path.read_bytes())


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _event(path: Path, name: str, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                            "event": name, "payload": payload}, ensure_ascii=False, sort_keys=True) + "\n")


def _git(*args: str, cwd: Path) -> str:
    return subprocess.check_output(["git", "-C", str(cwd), *args], text=True).strip()


def _headings(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.lstrip().startswith("#")]


def _validate(generated: Any, seed: int) -> dict[str, Any]:
    if generated.task_id != TASK_ID or generated.seed != seed:
        raise ValueError("generated identity changed")
    if not isinstance(generated.spec_md, str) or not isinstance(generated.brief_md, str):
        raise ValueError("native task text must be strings")
    workspace = dict(generated.workspace_files)
    if set(workspace) != WORKSPACE_PATHS or any(not isinstance(v, str) for v in workspace.values()):
        raise ValueError(f"unexpected workspace structure at seed {seed}")
    for name in ("etl.py", "run_etl.py"):
        ast.parse(workspace[name], filename=name)
    records = json.loads(workspace["source_sample.json"])
    schema = json.loads(workspace["target_schema.json"])
    expected = dict(generated.expected)
    if set(expected) != EXPECTED_KEYS or expected["domain"] != DOMAINS[seed]:
        raise ValueError(f"unexpected expected shape/domain at seed {seed}")
    if not isinstance(records, list) or len(records) != 10 or not all(isinstance(r, dict) for r in records):
        raise ValueError(f"expected 10 source records at seed {seed}")
    if expected["record_count"] != 10 or not isinstance(expected["records"], list) or len(expected["records"]) != 10:
        raise ValueError(f"unexpected parent expected record count at seed {seed}")
    target_fields = [field["name"] for field in schema["fields"]]
    if target_fields != expected["target_fields"] or len(target_fields) != 10:
        raise ValueError(f"target schema mismatch at seed {seed}")
    if not isinstance(expected["field_map"], dict) or not isinstance(expected["null_rules"], dict):
        raise ValueError(f"expected mapping shape mismatch at seed {seed}")
    if not all(set(record) == set(target_fields) for record in expected["records"]):
        raise ValueError(f"expected target record fields mismatch at seed {seed}")
    return {"workspace": workspace, "records": records, "schema": schema,
            "expected": expected, "target_fields": target_fields}


def capture(out: Path) -> Path:
    """Write a new evidence directory; existing evidence is never overwritten."""
    if out.exists():
        raise FileExistsError(f"capture directory exists: {out}")
    code_paths = {
        "capture": Path(__file__).resolve(),
        "generator": TEAMBENCH / GENERATOR_REL,
        "base": TEAMBENCH / "generators/base.py",
        "primitives": TEAMBENCH / "generators/primitives.py",
    }
    provenance = {
        "project_commit": _git("rev-parse", "HEAD", cwd=ROOT),
        "team_bench_commit": _git("rev-parse", "HEAD", cwd=TEAMBENCH),
        "team_bench_clean": not bool(_git("status", "--porcelain", cwd=TEAMBENCH)),
        "source_sha256": {name: _sha_file(path) for name, path in code_paths.items()},
    }
    out.mkdir(parents=True, exist_ok=False)
    config = {
        "schema_version": "n03-pipe1-native-material-audit-config-v1",
        "status": "FROZEN_BEFORE_GENERATION",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "command": [sys.executable, str(Path(__file__).resolve()), "--out", str(out)],
        "cwd": str(Path.cwd()),
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", "unset")},
        "generator": {"repository": str(TEAMBENCH), "module": "generators.gen_pipe1_etl_fix.Generator",
                      "required_commit": PIN, "task_id": TASK_ID, "seeds": list(SEEDS)},
        "provenance": provenance,
        "activity_budget": {"generator_calls": 4, "candidate_executions": 0, "graders": 0,
                            "llm_api_calls": 0, "gpu_runs": 0},
        "role_projection": {
            "planner": ["task_id", "seed", "spec_md"],
            "executor": ["task_id", "seed", "brief_md", "workspace_files", "peer_message"],
            "parent_only": ["expected", "hashes", "provenance"],
            "peer_message": "single null slot in Executor view; no message generated",
        },
    }
    _json(out / "config.json", config)
    raw = out / "raw.jsonl"
    _event(raw, "config_written", {"config_sha256": _sha_file(out / "config.json")})
    try:
        if provenance["team_bench_commit"] != PIN or not provenance["team_bench_clean"]:
            raise ValueError("TeamBench checkout is not the clean pinned primary source")
        if str(TEAMBENCH) not in sys.path:
            sys.path.insert(0, str(TEAMBENCH))
        module = importlib.import_module("generators.gen_pipe1_etl_fix")
        if Path(module.__file__).resolve() != code_paths["generator"].resolve():
            raise ValueError("unexpected generator module shadowing")
        snapshot = out / "source_snapshot"
        snapshot.mkdir()
        for name, source in code_paths.items():
            shutil.copy2(source, snapshot / f"{name}_{source.name}")
        cases = []
        for seed in SEEDS:
            generated = module.Generator().generate(seed)
            checked = _validate(generated, seed)
            workspace = checked["workspace"]
            expected = checked["expected"]
            # Explicit source projection: no generated.expected is referenced in
            # either actor view. Planner-private rules are intentionally intact.
            planner = {"task_id": generated.task_id, "seed": generated.seed,
                       "spec_md": generated.spec_md}
            executor = {"task_id": generated.task_id, "seed": generated.seed,
                        "brief_md": generated.brief_md,
                        "workspace_files": {name: workspace[name] for name in sorted(WORKSPACE_PATHS)},
                        "peer_message": None}
            if set(planner) != set(config["role_projection"]["planner"]):
                raise ValueError("Planner projection expanded")
            if set(executor) != set(config["role_projection"]["executor"]):
                raise ValueError("Executor projection expanded")
            if executor["peer_message"] is not None:
                raise ValueError("peer message slot not empty")
            parent = {"task_id": generated.task_id, "seed": generated.seed,
                      "expected": expected,
                      "source_projection_note": "Actor views use generated.spec_md, generated.brief_md, and generated.workspace_files only; generated.expected is copied solely here. Content overlap with public schema or Planner-private rules is native and is not treated as leakage.",
                      "hashes": {
                          "spec_md_sha256": _sha_text(generated.spec_md),
                          "brief_md_sha256": _sha_text(generated.brief_md),
                          "workspace_sha256": {name: _sha_text(value) for name, value in workspace.items()},
                          "expected_canonical_sha256": _sha(json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")),
                      }}
            case_dir = out / f"seed_{seed}"
            case_dir.mkdir()
            _json(case_dir / "planner_view.json", planner)
            _json(case_dir / "executor_view.json", executor)
            _json(case_dir / "parent_only.json", parent)
            row = {
                "seed": seed, "domain": expected["domain"], "task_id": generated.task_id,
                "record_count": len(checked["records"]), "target_fields": checked["target_fields"],
                "rule_headings": _headings(generated.spec_md),
                "spec_utf8_bytes": len(generated.spec_md.encode("utf-8")),
                "brief_utf8_bytes": len(generated.brief_md.encode("utf-8")),
                "source_utf8_bytes": {name: len(value.encode("utf-8")) for name, value in workspace.items()},
                "task_text_sha256": {"planner_spec": parent["hashes"]["spec_md_sha256"],
                                      "executor_brief": parent["hashes"]["brief_md_sha256"]},
                "view_file_sha256": {"planner": _sha_file(case_dir / "planner_view.json"),
                                     "executor": _sha_file(case_dir / "executor_view.json"),
                                     "parent_only": _sha_file(case_dir / "parent_only.json")},
                "peer_message_slot": None,
            }
            cases.append(row)
            _event(raw, "seed_captured", row)
        if len(cases) != 4 or {row["domain"] for row in cases} != set(DOMAINS):
            raise ValueError("four-domain coverage failed")
        _json(out / "summary.json", {"status": "NATIVE_MATERIAL_CAPTURED", "case_count": 4,
                                     "generator_calls": 4, "llm_api_calls": 0, "gpu_runs": 0,
                                     "candidate_executions": 0, "graders": 0,
                                     "shared_structural_root": TASK_ID,
                                     "cases": cases,
                                     "qualification_claim": "None; static native material capture only"})
        _event(raw, "capture_completed", {"status": "NATIVE_MATERIAL_CAPTURED", "cases": 4})
        return out
    except Exception as exc:
        _event(raw, "capture_failed", {"error_type": type(exc).__name__, "message": str(exc),
                                        "traceback": traceback.format_exc()})
        _json(out / "summary.json", {"status": "UNKNOWN", "error_type": type(exc).__name__,
                                     "llm_api_calls": 0, "candidate_executions": 0, "graders": 0, "gpu_runs": 0})
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    capture(args.out.resolve())


if __name__ == "__main__":
    main()
