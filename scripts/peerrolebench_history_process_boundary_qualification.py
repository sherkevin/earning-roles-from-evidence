"""Zero-call qualification for the peer-history process boundary."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_history_selector import select_from_public_history  # noqa: E402
from peerrolebench_peer_history import PeerHistoryV1  # noqa: E402
from peerrolebench_history_four_cell_qualification import (  # noqa: E402
    CANDIDATES, READ_CUT, RNG_SEED, _fixture,
)


VERSION = "peer-history-process-boundary-qualification-v1"
CELLS = ("restored-history", "restored-empty", "tampered-digest",
         "truncated-snapshot", "wrong-version")


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, default=str,
    ).encode("utf-8")).hexdigest()


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n",
                    encoding="utf-8")


def _bundle(histories: dict[str, PeerHistoryV1]) -> dict[str, Any]:
    return {
        "schema": "peer-history-process-bundle-v1",
        "candidate_keys": list(CANDIDATES),
        "histories": {key: histories[key].snapshot() for key in CANDIDATES},
    }


def _parent_selection(histories: dict[str, PeerHistoryV1], *, target_scope_key: str) -> dict[str, Any]:
    projections = {
        key: histories[key].selector_projection(candidate_key=key)
        for key in CANDIDATES
    }
    return select_from_public_history(
        candidate_keys=CANDIDATES, projections=projections,
        base_scores=(0.0, 0.0), read_cut=READ_CUT, rng_seed=RNG_SEED,
        target_scope_key=target_scope_key,
    )


def _run_child(*, cell_out: Path, bundle: dict[str, Any], target_scope_key: str,
               timeout_s: float = 15.0) -> dict[str, Any]:
    bundle_path = cell_out / "bundle.json"
    receipt_path = cell_out / "child_receipt.json"
    stdout_path = cell_out / "child_stdout.txt"
    stderr_path = cell_out / "child_stderr.txt"
    _json(bundle_path, bundle)
    command = [
        sys.executable, str(SCRIPTS / "peerrolebench_history_process_worker.py"),
        "--bundle", str(bundle_path), "--output", str(receipt_path),
        "--candidate-keys", json.dumps(list(CANDIDATES)),
        "--base-scores", json.dumps([0.0, 0.0]),
        "--read-cut", str(READ_CUT), "--rng-seed", str(RNG_SEED),
        "--target-scope-key", target_scope_key,
    ]
    started = time.perf_counter()
    try:
        completed = subprocess.run(command, cwd=ROOT, text=True,
                                   capture_output=True, timeout=timeout_s)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        completed = subprocess.CompletedProcess(command, 124,
                                                stdout=exc.stdout or "",
                                                stderr=exc.stderr or "timeout")
        timed_out = True
    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 6)
    stdout_path.write_text(completed.stdout or "", encoding="utf-8")
    stderr_path.write_text(completed.stderr or "", encoding="utf-8")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) \
        if receipt_path.exists() else {
            "status": "UNKNOWN", "selection": None,
            "unknown_reason": "child produced no structured receipt",
        }
    return {
        "command": command,
        "returncode": completed.returncode,
        "timed_out": timed_out,
        "wall_ms": elapsed_ms,
        "bundle_sha256": _digest(bundle),
        "bundle_bytes": bundle_path.stat().st_size,
        "receipt": receipt,
    }


def run(out: Path) -> dict[str, Any]:
    out = out.resolve()
    out.mkdir(parents=False, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     text=True).strip()
    components = {
        name: hashlib.sha256((SCRIPTS / name).read_bytes()).hexdigest()
        for name in ("peerrolebench_peer_history.py",
                     "peerrolebench_history_selector.py",
                     "peerrolebench_history_process_worker.py",
                     "peerrolebench_history_process_boundary_qualification.py")
    }
    config = {
        "qualification_version": VERSION,
        "git_commit": commit,
        "python": sys.version,
        "platform": platform.platform(),
        "cells": list(CELLS),
        "candidate_keys": list(CANDIDATES),
        "read_cut": READ_CUT,
        "rng_seed": RNG_SEED,
        "fixture": "canonical-source-target-history-v1",
        "component_sha256": components,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _json(out / "config.json", config)

    _, _, _, valid_history, _, _ = _fixture()
    target_scope_key = valid_history.selector_projection(
        candidate_key="peer-a@v1"
    )["scopes"][0]["scope_key"]
    valid_histories = {
        "peer-a@v1": valid_history,
        "peer-b@v1": PeerHistoryV1.empty("peer-b"),
    }
    empty_histories = {
        key: PeerHistoryV1.empty(key.split("@", 1)[0]) for key in CANDIDATES
    }
    parent_history = _parent_selection(valid_histories, target_scope_key=target_scope_key)
    parent_empty = _parent_selection(empty_histories, target_scope_key=target_scope_key)
    results: dict[str, dict[str, Any]] = {}
    for cell in CELLS:
        cell_out = out / cell
        cell_out.mkdir(parents=False, exist_ok=False)
        if cell == "restored-history":
            bundle = _bundle(valid_histories)
        elif cell == "restored-empty":
            bundle = _bundle(empty_histories)
        elif cell == "tampered-digest":
            bundle = _bundle(valid_histories)
            bundle["histories"]["peer-a@v1"]["state_digest"] = "0" * 64
        elif cell == "truncated-snapshot":
            bundle = _bundle(valid_histories)
            bundle["histories"]["peer-a@v1"].pop("entries", None)
        else:
            bundle = _bundle(valid_histories)
            bundle["histories"]["peer-a@v1"]["version"] = "peer-history-v1"
            payload = {
                key: bundle["histories"]["peer-a@v1"][key]
                for key in ("schema", "version", "agent_key", "seals", "entries", "scopes")
            }
            bundle["histories"]["peer-a@v1"]["state_digest"] = _digest(payload)
        child = _run_child(cell_out=cell_out, bundle=bundle,
                           target_scope_key=target_scope_key)
        receipt = child["receipt"]
        row: dict[str, Any] = {
            "cell": cell,
            "status": "UNKNOWN",
            "child": child,
            "update_count": 0,
            "selection": receipt.get("selection"),
            "child_status": receipt.get("status"),
            "unknown_reason": receipt.get("unknown_reason"),
            "snapshot_sha256": child["bundle_sha256"],
            "snapshot_bytes": child["bundle_bytes"],
            "target_scope_key": target_scope_key,
            "cost": {
                "api_calls": 0, "gpu_jobs": 0, "input_tokens": 0,
                "output_tokens": 0, "tool_calls": 0,
                "snapshot_bytes": child["bundle_bytes"],
                "wall_ms": child["wall_ms"], "updates": 0,
            },
        }
        if cell == "restored-history":
            expected = parent_history
            row["status"] = "PASS" if (
                child["returncode"] == 0 and receipt.get("status") == "PASS"
                and receipt.get("selection") == expected
                and receipt.get("state_digests", {}).get("peer-a@v1") == valid_history.state_digest()
            ) else "UNKNOWN"
            row["equality"] = row["status"] == "PASS"
        elif cell == "restored-empty":
            expected = parent_empty
            row["status"] = "PASS" if (
                child["returncode"] == 0 and receipt.get("status") == "PASS"
                and receipt.get("selection") == expected
                and receipt.get("selection") == parent_empty
                and receipt.get("selection", {}).get("input_digest") == parent_empty.get("input_digest")
            ) else "UNKNOWN"
            row["equality"] = row["status"] == "PASS"
        else:
            row["status"] = "UNKNOWN" if (
                child["returncode"] != 0 and receipt.get("status") == "UNKNOWN"
                and receipt.get("selection") is None and receipt.get("update_count") == 0
            ) else "FAIL"
            row["equality"] = row["status"] == "UNKNOWN"
        _json(cell_out / "summary.json", row)
        (cell_out / "raw.jsonl").write_text(
            json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "event_type": "process_boundary_cell", "payload": row},
                       ensure_ascii=False, default=str) + "\n", encoding="utf-8"
        )
        results[cell] = row

    passed = bool(
        results["restored-history"]["status"] == "PASS"
        and results["restored-empty"]["status"] == "PASS"
        and all(results[cell]["status"] == "UNKNOWN" for cell in CELLS[2:])
    )
    summary = {
        **config,
        "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
        "passed": passed,
        "cells": results,
        "checks": {
            "restored_history_equal": results["restored-history"]["status"] == "PASS",
            "restored_empty_equal": results["restored-empty"]["status"] == "PASS",
            "tampered_digest_rejected": results["tampered-digest"]["status"] == "UNKNOWN",
            "truncated_snapshot_rejected": results["truncated-snapshot"]["status"] == "UNKNOWN",
            "wrong_version_rejected": results["wrong-version"]["status"] == "UNKNOWN",
            "all_updates_zero": all(row["update_count"] == 0 for row in results.values()),
        },
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "interpretation": "Process-boundary replay and fail-closed snapshot checks only; no efficacy or cost claim.",
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _json(out / "summary.json", summary)
    (out / "raw.jsonl").write_text(
        json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "event_type": "process_boundary_summary", "payload": summary},
                   ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps({key: result[key] for key in
                      ("status", "passed", "real_api_calls", "gpu_jobs")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
