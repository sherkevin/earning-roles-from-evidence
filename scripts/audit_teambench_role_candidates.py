#!/usr/bin/env python3
"""Static audit for possible TeamBench cross-role task roots.

This script deliberately does not import or run a TeamBench generator, grader,
candidate agent, test suite, or model.  It records reproducible source facts;
the qualification decision is written separately after human review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


CANDIDATES = [
    "CROSS5_event_schema",
    "PIPE3_stream_processing",
    "MULTI3_polyglot",
    "DIST3_idempotency",
    "NEG3_tech_debt",
    "INFRA2_cicd_repair",
]

KEYWORDS = [
    "producer", "consumer", "processor", "sink", "backend", "frontend",
    "upstream", "downstream", "handoff", "publish", "consume", "integrat",
    "planner", "executor", "schema", "bug", "already", "do not modify",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_repo_commit(teambench: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(teambench), "rev-parse", "HEAD"], text=True
    ).strip()


def extract_files(generator_text: str):
    # Generated workspaces use literal files["path"] assignments.  Dynamic
    # paths remain visible through a separate marker so they are not silently
    # treated as complete evidence.
    literal = set(re.findall(r"files\[\s*['\"]([^'\"]+)['\"]\s*\]", generator_text))
    # Some generators build workspace_files as a dictionary literal instead
    # of assigning files[...].  Restrict this second pattern to path-shaped
    # keys so ordinary configuration dictionaries do not become workspace
    # files.
    literal.update(re.findall(
        r"['\"]((?:\.?[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+)['\"]\s*:",
        generator_text,
    ))
    literal = sorted(literal)
    dynamic = bool(re.search(r"files\[[^'\"]", generator_text))
    return literal, dynamic


def extract_markers(text: str):
    markers = []
    for line_no, line in enumerate(text.splitlines(), 1):
        lower = line.lower()
        if any(word in lower for word in KEYWORDS):
            markers.append({
                "line": line_no,
                "text": line.strip()[:240],
                "keywords": [word for word in KEYWORDS if word in lower],
            })
    return markers


def task_yaml_summary(text: str):
    result = {}
    for key in ("task_id", "category", "domain", "difficulty", "tni_pattern", "parameterized"):
        match = re.search(r"^" + re.escape(key) + r"\s*:\s*(.+)$", text, re.MULTILINE)
        if match:
            result[key] = match.group(1).strip()
    return result


def inspect_candidate(teambench: Path, task_id: str):
    task_dir = teambench / "tasks" / task_id
    generator = teambench / "generators" / ("gen_" + task_id.lower() + ".py")
    # Some generator names omit the task-id case or use a shorter prefix.  Find
    # the unique generator whose source declares this task id when necessary.
    if not generator.exists():
        matches = []
        for path in sorted((teambench / "generators").glob("gen_*.py")):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if 'task_id = "' + task_id + '"' in text or "task_id = '" + task_id + "'" in text:
                matches.append(path)
        if len(matches) == 1:
            generator = matches[0]

    files = []
    for path in sorted(task_dir.glob("*")):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            files.append({
                "path": str(path.relative_to(teambench)),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "lines": len(text.splitlines()),
                "keyword_counts": {word: text.lower().count(word) for word in KEYWORDS if word in text.lower()},
                "markers": extract_markers(text),
            })

    generator_record = None
    if generator.exists():
        generator_text = generator.read_text(encoding="utf-8", errors="replace")
        literal_files, dynamic_files = extract_files(generator_text)
        generator_record = {
            "path": str(generator.relative_to(teambench)),
            "sha256": sha256(generator),
            "bytes": generator.stat().st_size,
            "lines": len(generator_text.splitlines()),
            "literal_workspace_files": literal_files,
            "contains_dynamic_file_keys": dynamic_files,
            "keyword_counts": {word: generator_text.lower().count(word) for word in KEYWORDS if word in generator_text.lower()},
            "markers": extract_markers(generator_text),
        }

    task_yaml = next((item for item in files if item["path"].endswith("/task.yaml")), None)
    task_yaml_text = (task_dir / "task.yaml").read_text(encoding="utf-8") if (task_dir / "task.yaml").exists() else ""
    return {
        "task_id": task_id,
        "task_yaml": task_yaml_summary(task_yaml_text),
        "task_files": files,
        "generator": generator_record,
        "static_only": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--teambench", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    teambench = args.teambench.resolve()
    payload = {
        "experiment_id": "n03_teambench_candidate_scan_20260926",
        "source_commit": source_repo_commit(teambench),
        "scientific_claim_allowed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "candidate_execution": False,
        "candidates": [inspect_candidate(teambench, task_id) for task_id in CANDIDATES],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "source_commit": payload["source_commit"],
        "candidates": [
            {
                "task_id": item["task_id"],
                "generator": item["generator"]["path"] if item["generator"] else None,
                "literal_workspace_files": item["generator"]["literal_workspace_files"] if item["generator"] else [],
            }
            for item in payload["candidates"]
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
