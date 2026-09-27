#!/usr/bin/env python3
"""Run a bounded, zero-LLM mutation matrix for the peer-role ledger replay gate.

This is a protocol qualification diagnostic.  It never calls an LLM, scorer, or
GPU.  A valid real ledger is replayed, then copied and mutated in memory.  The
output keeps the raw case-level verdicts separate from the summary so a future
runner can use the same validator before accepting an online update.
"""
from __future__ import annotations

from datetime import datetime, timezone
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_ledger_replay import LedgerReplayError, replay_ledger_events, _hash_payload  # noqa: E402


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


def load_real_fixture() -> list[dict[str, Any]]:
    path = ROOT / "experiments/logs/n02_peerrole_dev_v3_20260926/ledger.json"
    return json.loads(path.read_text())


def mutate(base: list[dict[str, Any]], case: str) -> tuple[list[dict[str, Any]], bool]:
    records = copy.deepcopy(base)
    expects_unknown = False
    if case == "valid_real_v3":
        return records, expects_unknown
    if case == "duplicate_event":
        records.insert(3, copy.deepcopy(records[2]))
        rehash(records)
    elif case == "record_hash_tamper":
        records[2]["record_hash"] = "f" * 64
    elif case == "previous_hash_tamper":
        records[2]["previous_hash"] = "f" * 64
    elif case == "unknown_event":
        records[2]["event_type"] = "mystery_event"
        rehash(records)
    elif case == "retry_event":
        records[2]["event_type"] = "producer_retry"
        rehash(records)
    elif case == "out_of_order":
        start = next(i for i, row in enumerate(records) if row["event_type"] == "task_start")
        delivery = next(i for i, row in enumerate(records) if row["event_type"] == "producer_delivery")
        records[start], records[delivery] = records[delivery], records[start]
        rehash(records)
    elif case == "interrupted_after_judgment":
        cut = next(i for i, row in enumerate(records) if row["event_type"] == "recipient_judgment") + 1
        records = records[:cut]
        rehash(records)
        expects_unknown = True
    else:
        raise ValueError(case)
    return records, expects_unknown


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] != "--output":
        raise SystemExit("usage: peerrolebench_ledger_replay_matrix.py --output DIR")
    output = Path(sys.argv[2]).resolve()
    output.mkdir(parents=False, exist_ok=False)
    config = {
        "experiment_id": output.name,
        "purpose": "parent-side peer-role ledger replay and mutation qualification",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "real_fixture": "experiments/logs/n02_peerrole_dev_v3_20260926/ledger.json",
        "real_fixture_sha256": sha256(ROOT / "experiments/logs/n02_peerrole_dev_v3_20260926/ledger.json"),
        "script_sha256": sha256(Path(__file__)),
        "validator_sha256": sha256(ROOT / "scripts/peerrolebench_ledger_replay.py"),
        "llm_calls": 0,
        "gpu_jobs": 0,
        "native_grader_invoked": False,
        "cases": ["valid_real_v3", "duplicate_event", "record_hash_tamper", "previous_hash_tamper",
                   "unknown_event", "retry_event", "out_of_order", "interrupted_after_judgment"],
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
    base = load_real_fixture()
    rows: list[dict[str, Any]] = []
    for case in config["cases"]:
        records, expects_unknown = mutate(base, case)
        row: dict[str, Any] = {"case": case, "input_event_count": len(records),
                               "expected_unknown": expects_unknown}
        try:
            result = replay_ledger_events(records, allow_incomplete=expects_unknown)
            row.update(status=result.status, complete=result.complete, missing=list(result.missing),
                       observed_code=None, expectation_met=(result.status == "UNKNOWN") == expects_unknown)
        except LedgerReplayError as exc:
            row.update(status="INVALID", complete=False, missing=[], observed_code=exc.code,
                       error=str(exc), expectation_met=not expects_unknown)
        log("case_result", row)
        rows.append(row)
    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config_sha256": sha256(output / "config.json"),
        "raw_sha256": sha256(raw),
        "case_count": len(rows),
        "all_expectations_met": all(row["expectation_met"] for row in rows),
        "valid_real_ledger_passed": rows[0]["status"] == "PASS" and rows[0]["complete"],
        "invalid_or_unknown_cases_rejected_or_marked": all(row["expectation_met"] for row in rows[1:]),
        "llm_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "boundary": "Protocol and replay qualification only; no generated agent output, scorer result, or learning update.",
        "cases": rows,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    log("summary", summary)
    print(json.dumps({k: summary[k] for k in ("all_expectations_met", "valid_real_ledger_passed",
                                               "invalid_or_unknown_cases_rejected_or_marked",
                                               "scientific_claim_allowed")}, ensure_ascii=False, indent=2))
    return 0 if summary["all_expectations_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
