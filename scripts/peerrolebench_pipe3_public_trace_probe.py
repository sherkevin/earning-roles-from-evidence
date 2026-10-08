"""Offline feasibility trace of two frozen public PIPE3 producer artifacts.

No hidden tests, expected labels, scorer worker, provider, or recipient action.
The trace reports observed bytes and timestamp; interpretation belongs to the
parent's later analysis and cannot revise the stopped four-cell API run.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

from peerrolebench_pipe3_material_adapter import digest_files
from peerrolebench_sandbox import SandboxedWorker

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/peerrolebench_pipe3_public_trace_worker.py"
VERSION = "n03-public-trace-feasibility-v1"
FIELDS = {"event_id", "timestamp", "user_name", "action", "page_url"}


def _io():
    from peerrolebench_real_closed_loop import log, save
    return log, save


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _pinned(path: str, base: Path) -> Path:
    resolved = (base / path).resolve()
    if not resolved.is_relative_to(base.resolve()) or not resolved.is_file():
        raise ValueError("public trace input is absent or outside pinned directory")
    return resolved


def _inputs(card_path: Path) -> tuple[dict, Path, list[dict]]:
    card = json.loads(card_path.read_text(encoding="utf-8"))
    if (card.get("schema_version") != VERSION or card.get("max_candidate_rpcs") != 2
            or card.get("scientific_claim_allowed") is not False
            or any(card.get(field) != 0 for field in
                   ("api_calls", "actions", "training_updates", "gpu_jobs"))):
        raise ValueError("public trace card budget or schema differs")
    probe = card.get("probe_input")
    if (not isinstance(probe, dict) or set(probe) != FIELDS
            or any(not isinstance(value, str) or not value for value in probe.values())):
        raise ValueError("public probe input must have five nonempty text fields")
    datetime.fromisoformat(probe["timestamp"])
    prepared = _pinned(card["prepared_dir"] + "/parent_manifest.json", ROOT).parent
    manifest_path = prepared / "parent_manifest.json"
    if _sha(manifest_path) != card["parent_manifest_sha256"]:
        raise ValueError("parent manifest pin changed")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    chosen = card.get("cases")
    if (manifest.get("schema_version") != "n03-scoped-judgment-parent-manifest-v1"
            or not isinstance(chosen, list) or len(chosen) != 2
            or [row.get("order") for row in chosen] != [0, 1]):
        raise ValueError("public trace must use frozen first two cells")
    cells = manifest.get("cases", [])
    if len(cells) != 4 or [row.get("order") for row in cells] != list(range(4)):
        raise ValueError("prepared four-cell manifest invalid")
    if (cells[0].get("producer_origin") != "historical"
            or cells[1].get("producer_origin") != "native"):
        raise ValueError("first two producer sources differ from fixed axes")
    selected = []
    for index, row in enumerate(chosen):
        case = cells[index]
        if row != {"order": index, "case_id": case["case_id"]}:
            raise ValueError("public trace case binding differs")
        request_path = _pinned(case["request_path"], prepared)
        if _sha(request_path) != case["request_sha256"]:
            raise ValueError("prepared public request changed")
        request = json.loads(request_path.read_text(encoding="utf-8"))
        visible = json.loads(request["messages"][0]["content"].split("\n\nPublic task payload:\n", 1)[1])
        files = visible["public_source_files"]
        if (visible["case_id"] != case["case_id"]
                or set(files) != {"producer.py", "processor.py", "models.py", "sink.py"}
                or {name: digest_files({name: source}) for name, source in files.items()}
                != case["public_file_digests"]
                or visible["producer_artifact_sha256"] != case["public_file_digests"]["producer.py"]):
            raise ValueError("public source or producer digest changed")
        selected.append({"case_id": case["case_id"], "request_path": request_path,
                         "request_sha256": case["request_sha256"],
                         "producer_artifact_sha256": case["public_file_digests"]["producer.py"],
                         "sources": {name: files[name] for name in ("models.py", "producer.py")},
                         "source_digest": digest_files({name: files[name] for name in ("models.py", "producer.py")})})
    if selected[0]["sources"]["models.py"] != selected[1]["sources"]["models.py"]:
        raise ValueError("public support model differs across producer sources")
    return card, prepared, selected


def prepare(card_path: Path, out: Path) -> None:
    log, save = _io()
    card_path = card_path.resolve()
    card, prepared, selected = _inputs(card_path)
    out.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__).resolve(), WORKER, ROOT / "scripts/peerrolebench_sandbox.py",
               ROOT / "scripts/peerrolebench_worker_limits.py",
               ROOT / "tools/peerrole-runtime/package-lock.json",
               ROOT / "scripts/peerrolebench_pipe3_material_adapter.py",
               ROOT / "scripts/peerrolebench_real_closed_loop.py", card_path,
               *(row["request_path"] for row in selected)]
    hashes = {str(path): _sha(path) for path in sources}
    seal = {"version": VERSION, "card": card, "card_path": str(card_path),
            "card_sha256": _sha(card_path), "source_sha256": hashes,
            "probe_input_digest": _digest(card["probe_input"]),
            "parent_manifest_sha256": _sha(prepared / "parent_manifest.json"),
            "selected": [{key: row[key] for key in ("case_id", "request_sha256", "source_digest",
                                                  "producer_artifact_sha256")}
                         for row in selected],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
            "platform": platform.platform(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "command": list(sys.argv), "api_calls": 0, "candidate_rpc_budget": 2,
            "actions": 0, "training_updates": 0, "gpu_jobs": 0,
            "scientific_claim_allowed": False}
    save(out / "config.json", seal)
    snap = out / "source_snapshot"
    snap.mkdir()
    for index, path in enumerate(sources):
        shutil.copy2(path, snap / f"{index:02d}_{path.name}")
    save(out / "summary.json", {"status": "READY", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                "candidate_rpc_attempts": 0, "api_calls": 0, "actions": 0,
                                "training_updates": 0, "gpu_jobs": 0, "scientific_claim_allowed": False})
    log(out, "public_trace_prepared", {"config_sha256": _sha(out / "config.json")})


def run_next(card_path: Path, out: Path) -> dict:
    log, save = _io()
    card_path, out = card_path.resolve(), out.resolve()
    card, _prepared, selected = _inputs(card_path)
    seal = json.loads((out / "config.json").read_text(encoding="utf-8"))
    if (seal.get("card") != card or seal.get("card_sha256") != _sha(card_path)
            or any(_sha(Path(path)) != digest for path, digest in seal["source_sha256"].items())):
        raise ValueError("public trace seal or source pin changed")
    previous = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    events = [json.loads(line) for line in (out / "raw.jsonl").read_text().splitlines()]
    attempts = sum(row.get("event_type") == "public_trace_start" for row in events)
    if previous["status"] not in {"READY", "RECORDED"} or attempts != previous["candidate_rpc_attempts"] or attempts >= 2:
        raise ValueError("public trace is stopped or budget exhausted")
    row = selected[attempts]
    stage = out / f"case_{attempts}"
    stage.mkdir(exist_ok=False)
    log(out, "public_trace_start", {"index": attempts, "case_id": row["case_id"],
                                    "source_digest": row["source_digest"]})
    start = time.monotonic()
    try:
        with SandboxedWorker(row["sources"], stage / "sandbox", lambda event, payload: log(out, event, payload),
                             "unused", "unused", worker_path=WORKER, rpc_seconds=20,
                             source_prefixes=("models.py", "producer.py")) as worker:
            response = worker.request({"op": "serialize_event", "probe_input": card["probe_input"]})
        if (not isinstance(response, dict) or response.get("ok") is not True
                or not isinstance(response.get("serialized_output"), str)
                or not isinstance(response.get("timestamp_value"), str)):
            raise ValueError("public serialization response incomplete")
        parsed = json.loads(response["serialized_output"])
        if not isinstance(parsed, dict) or parsed.get("timestamp") != response["timestamp_value"]:
            raise ValueError("public serialization response inconsistent")
        save(stage / "trace.json", {"case_id": row["case_id"], "source_digest": row["source_digest"],
             "producer_artifact_sha256": row["producer_artifact_sha256"],
             "request_sha256": row["request_sha256"], "probe_input": card["probe_input"],
             "probe_input_digest": seal["probe_input_digest"],
             "serialized_output": response["serialized_output"],
             "serialized_output_sha256": hashlib.sha256(response["serialized_output"].encode()).hexdigest(),
             "timestamp_value": response["timestamp_value"], "elapsed_seconds": time.monotonic() - start})
        result = {"status": "COMPLETE" if attempts == 1 else "RECORDED",
                  "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                  "candidate_rpc_attempts": attempts + 1, "api_calls": 0, "actions": 0,
                  "training_updates": 0, "gpu_jobs": 0, "scientific_claim_allowed": False}
        save(out / "summary.json", result)
        log(out, "public_trace_recorded", {"index": attempts, "trace_sha256": _sha(stage / "trace.json")})
        return result
    except Exception as exc:
        result = {"status": "UNKNOWN", "candidate_rpc_attempts": attempts + 1,
                  "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                  "api_calls": 0, "actions": 0, "training_updates": 0, "gpu_jobs": 0,
                  "scientific_claim_allowed": False,
                  "failure_stage": "public_sandbox_or_rpc", "error_type": type(exc).__name__}
        save(out / "summary.json", result)
        log(out, "public_trace_unknown", {"index": attempts, "error_type": type(exc).__name__})
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run-next"))
    parser.add_argument("--card", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare(args.card, args.out)
        print(json.dumps({"status": "READY", "api_calls": 0}))
    else:
        outcome = run_next(args.card, args.out)
        print(json.dumps(outcome))
        sys.exit(0 if outcome["status"] in {"RECORDED", "COMPLETE"} else 1)
