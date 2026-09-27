#!/usr/bin/env python3
"""Qualify runner exception/scorer boundary semantics without model calls.

This diagnostic reuses a preserved real ledger and checks that incomplete or
unsupported event streams are never converted into labels.  It also classifies
scorer transport/permission/JSON failures as UNKNOWN.  It does not implement a
hidden scorer and does not claim benchmark or learning validity.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import subprocess
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from peerrolebench_ledger_replay import LedgerReplayError, _hash_payload, replay_ledger_events  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rehash(records: list[dict[str, Any]]) -> None:
    previous = "GENESIS"
    for record in records:
        record["previous_hash"] = previous
        record["record_hash"] = _hash_payload({
            "event_type": record["event_type"],
            "payload": record["payload"],
            "previous_hash": previous,
        })
        previous = record["record_hash"]


def classify_scorer_response(
    response: Any,
    *,
    transport_error: str | None = None,
    timed_out: bool = False,
    permission_denied: bool = False,
) -> dict[str, Any]:
    """Classify only the scorer boundary; unknown responses cannot label work."""
    if timed_out:
        return {"status": "UNKNOWN", "label": None, "reason": "timeout"}
    if permission_denied:
        return {"status": "UNKNOWN", "label": None, "reason": "permission_denied"}
    if transport_error:
        return {"status": "UNKNOWN", "label": None, "reason": transport_error}
    if not isinstance(response, Mapping):
        return {"status": "UNKNOWN", "label": None, "reason": "invalid_json_or_shape"}
    if response.get("scorer_version") == "" or response.get("coverage_complete") is not True:
        return {"status": "UNKNOWN", "label": None, "reason": "missing_or_incomplete_coverage"}
    status = response.get("status")
    if status not in {"PASS", "FAIL"}:
        return {"status": "UNKNOWN", "label": None, "reason": "invalid_status"}
    return {"status": status, "label": int(status == "PASS"), "reason": None}


def update_eligibility(replay_status: str, scorer: Mapping[str, Any]) -> dict[str, Any]:
    allowed = replay_status == "PASS" and scorer.get("status") in {"PASS", "FAIL"}
    return {"update_allowed": allowed,
            "label": scorer.get("label") if allowed else None,
            "reason": None if allowed else "replay_or_scorer_not_qualified"}


def ledger_cases(base: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    cases = {"complete": copy.deepcopy(base)}
    cases["exception_after_selection"] = copy.deepcopy(base[:1])
    cases["exception_after_delivery"] = copy.deepcopy(base[:3])
    cases["exception_after_judgment"] = copy.deepcopy(base[:4])
    retry = copy.deepcopy(base)
    retry.insert(2, {
        "event_type": "producer_retry",
        "payload": {"attempt_id": "retry-1", "source_event_id": "producer-request-0"},
        "previous_hash": "GENESIS",
        "record_hash": "GENESIS",
    })
    rehash(retry)
    cases["transport_retry_record"] = retry
    return cases


def replay_case(records: list[dict[str, Any]], *, strict: bool) -> dict[str, Any]:
    try:
        result = replay_ledger_events(records, allow_incomplete=not strict)
        return {"status": result.status, "complete": result.complete,
                "missing": list(result.missing), "code": None}
    except LedgerReplayError as exc:
        return {"status": "INVALID", "complete": False, "missing": [], "code": exc.code}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    output.mkdir(parents=False, exist_ok=False)
    source = ROOT / "experiments/logs/n02_peerrole_dev_v3_20260926/ledger.json"
    base = json.loads(source.read_text())
    config = {
        "qualification_version": "runner-boundary-v1",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "ledger_source": str(source.relative_to(ROOT)),
        "ledger_sha256": sha256(source),
        "script_sha256": sha256(Path(__file__)),
        "llm_calls": 0, "gpu_jobs": 0, "native_grader_invoked": False,
        "independent_hidden_scorer_ipc": False,
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
    ledger_results = {}
    for name, records in ledger_cases(base).items():
        strict = name == "complete"
        observed = replay_case(records, strict=strict)
        ledger_results[name] = observed
        log("ledger_case", {"case": name, "strict": strict, "event_count": len(records), **observed})

    scorer_inputs = {
        "pass": ({"status": "PASS", "scorer_version": "hidden-v1", "coverage_complete": True}, {}),
        "timeout": (None, {"timed_out": True}),
        "permission": (None, {"permission_denied": True}),
        "transport_error": (None, {"transport_error": "connection_reset"}),
        "invalid_json": ("not-json", {}),
        "missing_coverage": ({"status": "PASS", "scorer_version": "hidden-v1", "coverage_complete": False}, {}),
    }
    scorer_results = {}
    for name, (response, kwargs) in scorer_inputs.items():
        result = classify_scorer_response(response, **kwargs)
        eligibility = update_eligibility("PASS", result)
        scorer_results[name] = {"scorer": result, "eligibility": eligibility}
        log("scorer_case", {"case": name, **scorer_results[name]})

    partials_unknown = all(row["status"] == "UNKNOWN" and not row["complete"]
                           for name, row in ledger_results.items() if name.startswith("exception_"))
    retry_rejected = ledger_results["transport_retry_record"]["status"] == "INVALID" and ledger_results["transport_retry_record"]["code"] == "unsupported_retry"
    scorer_unknown = all(scorer_results[name]["scorer"]["status"] == "UNKNOWN"
                         and not scorer_results[name]["eligibility"]["update_allowed"]
                         for name in ("timeout", "permission", "transport_error", "invalid_json", "missing_coverage"))
    summary = {
        "qualification_version": config["qualification_version"],
        "complete_ledger_passed": ledger_results["complete"]["status"] == "PASS",
        "exception_partials_are_unknown": partials_unknown,
        "retry_record_rejected": retry_rejected,
        "scorer_failures_are_unknown_and_no_update": scorer_unknown,
        "independent_hidden_scorer_ipc": False,
        "scientific_claim_allowed": False,
        "llm_calls": 0, "gpu_jobs": 0,
        "boundary": "Failure/timeout semantics only; no hidden scorer or agent execution.",
        "ledger_results": ledger_results, "scorer_results": scorer_results,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    passed = summary["complete_ledger_passed"] and partials_unknown and retry_rejected and scorer_unknown
    print(json.dumps({"passed": passed, "scientific_claim_allowed": False,
                      "independent_hidden_scorer_ipc": False}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
