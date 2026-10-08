#!/usr/bin/env python3
"""Probe an independent private scorer boundary without LLM or GPU calls."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile

from peerrolebench_sandbox import SandboxedWorker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "experiments/logs/n02_peerrole_dev_v3_20260926/ledger.json"
SCORER = ROOT / "scripts/peerrolebench_hidden_scorer_probe_worker.py"
RECIPIENT_PROBE = ROOT / "scripts/peerrolebench_pipe3_recipient_probe_worker.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=False, exist_ok=False)
    config = {
        "qualification_version": "scorer-ipc-preflight-v1",
        "fixture": str(FIXTURE.relative_to(ROOT)),
        "fixture_sha256": sha256(FIXTURE),
        "scorer_worker_sha256": sha256(SCORER),
        "candidate_probe_worker_sha256": sha256(RECIPIENT_PROBE),
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "candidate_received_hidden_expected": False,
        "independent_hidden_scorer_ipc": True,
        "scientific_claim_allowed": False,
    }
    (output / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    raw = output / "raw.jsonl"

    def log(event_type: str, payload: object) -> None:
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload},
                                    ensure_ascii=False) + "\n")
            handle.flush()

    log("config", config)
    records = json.loads(FIXTURE.read_text())
    expected_digest = records[2]["payload"]["artifact_sha256"]
    observed: dict[str, object] = {"scorer": {}, "candidate_boundary": {}}
    try:
        with SandboxedWorker({}, output / "scorer_sandbox", log,
                             worker_path=SCORER) as scorer:
            good = scorer.request({"op": "score", "artifact_sha256": expected_digest,
                                   "public_context": {"task_family": "DIST1_queue_race"}})
            bad = scorer.request({"op": "score", "artifact_sha256": "0" * 64,
                                  "public_context": {"task_family": "DIST1_queue_race"}})
            observed["scorer"] = {
                "good": good, "bad": bad,
                "good_response_digest": canonical_digest(good),
                "bad_response_digest": canonical_digest(bad),
                "good_pass": good.get("ok") is True and good.get("status") == "PASS" and good.get("coverage_complete") is True,
                "bad_fail": bad.get("ok") is True and bad.get("status") == "FAIL" and bad.get("coverage_complete") is True,
                "private_trusted_path": str(scorer.trusted),
            }
            # A separate candidate-side probe receives only the public path and
            # attempts to read the scorer's private worker copy.
            payload = {"role": "recipient", "source_files": {}, "required_delivery_paths": []}
            with SandboxedWorker({}, output / "candidate_sandbox", log,
                                 worker_path=RECIPIENT_PROBE) as candidate:
                probe = candidate.request({"payload": payload, "delivery": {},
                                           "operator_path": str(scorer.trusted / "worker.py")})
            observed["candidate_boundary"] = {
                "probe": probe,
                "private_read_denied": probe.get("operator_read", {}).get("ok") is False,
            }
    except Exception as exc:
        observed["error"] = {"type": type(exc).__name__, "message": str(exc)}
        log("preflight_error", observed["error"])

    scorer_result = observed.get("scorer", {})
    candidate_result = observed.get("candidate_boundary", {})
    summary = {
        "qualification_version": config["qualification_version"],
        "scorer_worker_pass_fail_verified": bool(scorer_result.get("good_pass") and scorer_result.get("bad_fail")),
        "candidate_cannot_read_scorer_private_worker": bool(candidate_result.get("private_read_denied")),
        "response_digests_recorded": bool(scorer_result.get("good_response_digest") and scorer_result.get("bad_response_digest")),
        "independent_hidden_scorer_ipc": True,
        "candidate_received_hidden_expected": False,
        "scorer_truth_is_fixture_only": True,
        "scientific_claim_allowed": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "boundary": "Private scorer IPC and candidate read denial only; not a benchmark score or learning result.",
        "remaining_gates": [
            "actual hidden scorer semantics and task-specific coverage",
            "real producer/recipient LLM dispatch through this boundary",
            "operator ledger and scorer retry/timeout protocol in the live runner",
        ],
        "observed": observed,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    passed = (summary["scorer_worker_pass_fail_verified"]
              and summary["candidate_cannot_read_scorer_private_worker"]
              and summary["response_digests_recorded"])
    print(json.dumps({"passed": passed, "independent_hidden_scorer_ipc": True,
                      "scientific_claim_allowed": False}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
