"""Record static provenance for the candidate PeerRoleBench manifest.

This is a zero-LLM, zero-GPU material audit.  It loads the pinned generators,
computes source/payload hashes and records visibility flags; it does not run a
candidate, scorer, native grader or ledger update.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEAM_BENCH = ROOT / "references/benchmark_sources/TeamBench"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(TEAM_BENCH))

from peerrolebench_task_contract import export_task_materials, load_generated_task  # noqa: E402
from peerrolebench_pipe3_material_adapter import build_materials  # noqa: E402


def digest_files(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for name, text in sorted(files.items()):
        name_bytes = name.encode("utf-8")
        value = text.encode("utf-8")
        h.update(len(name_bytes).to_bytes(8, "big"))
        h.update(name_bytes)
        h.update(len(value).to_bytes(8, "big"))
        h.update(value)
    return h.hexdigest()


def digest_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def load_materials(task_id: str, seed: int) -> tuple[dict[str, Any], dict[str, str]]:
    if task_id == "DIST1_queue_race":
        generated = load_generated_task(task_id, seed)
        materials = export_task_materials(generated)
    elif task_id == "PIPE3_stream_processing":
        from generators.gen_pipe3_stream_processing import Generator
        generated = Generator().generate(seed)
        materials = build_materials(generated)
    else:
        raise ValueError(f"unsupported candidate task: {task_id}")
    return materials, dict(generated.workspace_files)


def audit_root(root: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for seed in root["seeds"]:
        materials, workspace = load_materials(root["task_id"], int(seed))
        payloads = materials["agent_payloads"]
        material_manifest = materials["manifest"]
        hidden_paths = set(material_manifest.get("excluded_workspace_paths", []))
        hidden_paths.update(material_manifest.get("hidden_paths", []))
        payload_blob = json.dumps(payloads, ensure_ascii=False, sort_keys=True)
        hidden_leaks = sorted(path for path in hidden_paths if path and path.lower() in payload_blob.lower())
        rows.append({
            "seed": seed,
            "workspace_file_count": len(workspace),
            "workspace_sha256": digest_files(workspace),
            "payload_sha256": digest_json(payloads),
            "role_payload_sha256": {role: digest_json(payload) for role, payload in payloads.items()},
            "role_writable_paths": {role: payload.get("writable_paths", [])
                                    for role, payload in payloads.items()},
            "hidden_paths": sorted(hidden_paths),
            "hidden_path_leaks": hidden_leaks,
            "material_manifest": material_manifest,
            "static_visibility_passed": not hidden_leaks,
        })
    return {"root_id": root["root_id"], "task_id": root["task_id"],
            "structural_signature": root["structural_signature"], "split": root["split"],
            "seeds": rows,
            "all_static_visibility_passed": all(row["static_visibility_passed"] for row in rows)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    try:
        source_commit = subprocess.check_output(
            ["git", "-C", str(TEAM_BENCH), "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(
            ["git", "-C", str(TEAM_BENCH), "status", "--porcelain"], text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        source_commit, dirty = "UNKNOWN", str(exc)
    config = {
        "experiment_id": output.name,
        "purpose": "static provenance audit for candidate benchmark manifest",
        "manifest": str(args.manifest),
        "manifest_version": manifest.get("manifest_version"),
        "command": sys.argv,
        "python": sys.version,
        "platform": platform.platform(),
        "source_commit_expected": manifest.get("source_commit"),
        "source_commit_actual": source_commit,
        "source_dirty": bool(dirty),
        "llm_calls": 0,
        "gpu_jobs": 0,
        "candidate_executed": False,
        "scorer_executed": False,
        "native_grader_invoked": False,
        "scientific_claim_allowed": False,
    }
    (output / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    raw = output / "raw.jsonl"

    def log(event_type: str, payload: Any) -> None:
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False) + "\n")
            handle.flush()

    log("config", config)
    results = []
    errors = []
    for root in manifest.get("roots", []):
        try:
            result = audit_root(root)
            results.append(result)
            log("root_audit", result)
        except Exception as exc:
            error = {"root_id": root.get("root_id"), "type": type(exc).__name__,
                     "message": str(exc)}
            errors.append(error)
            log("root_error", error)
    summary = {
        "manifest_version": manifest.get("manifest_version"),
        "source_pin_match": source_commit == manifest.get("source_commit") and not dirty,
        "root_count": len(results),
        "roots": results,
        "errors": errors,
        "static_provenance_recorded": not errors and len(results) == len(manifest.get("roots", [])),
        "all_root_static_visibility_passed": (
            not errors and len(results) == len(manifest.get("roots", []))
            and all(item["all_static_visibility_passed"] for item in results)
        ),
        "benchmark_frozen": False,
        "scientific_claim_allowed": False,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    print(json.dumps({"static_provenance_recorded": summary["static_provenance_recorded"],
                      "all_root_static_visibility_passed": summary["all_root_static_visibility_passed"],
                      "benchmark_frozen": False}, indent=2))
    return 0 if summary["static_provenance_recorded"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
