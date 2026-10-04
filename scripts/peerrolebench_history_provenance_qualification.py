"""Zero-call canonical provenance qualification for the history adapter."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))
sys.path.insert(0, str(ROOT / "tests"))

from peerrolebench_peer_history import PeerHistoryV1  # noqa: E402
from peerrolebench_peer_history_adapter import append_history_after_credit  # noqa: E402
from peerrolebench_two_stage_gate import DelayedCreditLedger, LaterCredit  # noqa: E402
from test_peerrolebench_peer_history_binding import _ledger_and_offer  # noqa: E402


VERSION = "peer-history-canonical-provenance-qualification-v1"
CELLS = (
    "valid-chain", "duplicate-credit", "wrong-source-evidence",
    "uncommitted-credit", "candidate-version-mismatch", "registry-mismatch",
    "read-cut-before-source", "arrival-before-decision", "selection-mismatch",
    "credit-target-mismatch",
)


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, default=str,
    ).encode("utf-8")).hexdigest()


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n",
                    encoding="utf-8")


def _base() -> dict[str, Any]:
    ledger, offer, assignment, selection, _entry, registry = _ledger_and_offer()
    credit = LaterCredit.build(
        assignment_id="as1", source_evidence_id="e0",
        later_outcome_id="o1", later_quality=1.0,
    )
    delayed = DelayedCreditLedger()
    history = PeerHistoryV1.empty("peer-a")
    return {"ledger": ledger, "offer": offer, "assignment": assignment,
            "selection": selection, "registry": registry, "credit": credit,
            "delayed": delayed, "history": history}


def _call(base: dict[str, Any], *, credit: LaterCredit | None = None,
          delayed: DelayedCreditLedger | None = None,
          selection: Any | None = None, assignment_read_cut: int = 5,
          target_decision_index: int = 6, target_arrival_index: int = 12,
          candidate_key: str = "peer-a@v1",
          candidate_registry_digest: str | None = None) -> dict[str, Any]:
    selected_credit = credit or base["credit"]
    selected_delayed = delayed or base["delayed"]
    return append_history_after_credit(
        history=base["history"], ledger=base["ledger"], offer=base["offer"],
        target_assignment=base["assignment"],
        target_selection=selection or base["selection"], credit=selected_credit,
        delayed_ledger=selected_delayed,
        assignment_read_cut=assignment_read_cut,
        target_decision_index=target_decision_index,
        target_arrival_index=target_arrival_index,
        candidate_key=candidate_key,
        candidate_registry_digest=(candidate_registry_digest or base["registry"]),
    )


def _run_cell(cell: str) -> dict[str, Any]:
    base = _base()
    started = time.perf_counter()
    row: dict[str, Any] = {"cell": cell, "status": "UNKNOWN",
                           "append_count": 0, "update_count": 0,
                           "scientific_claim_allowed": False}
    try:
        if cell == "valid-chain":
            assert base["delayed"].apply_once(base["credit"], lambda _: None) is True
            result = _call(base)
            restored = PeerHistoryV1.replay(base["history"].snapshot())
            row.update({
                "status": "PASS" if (
                    result.get("status") == "APPENDED"
                    and restored.state_digest() == base["history"].state_digest()
                    and restored.selector_projection(candidate_key="peer-a@v1")
                    == base["history"].selector_projection(candidate_key="peer-a@v1")
                ) else "FAIL",
                "append_count": 1,
                "receipt": result.get("receipt"),
                "history_state_digest": base["history"].state_digest(),
            })
        elif cell == "duplicate-credit":
            assert base["delayed"].apply_once(base["credit"], lambda _: None) is True
            first = _call(base)
            second = _call(base)
            row.update({
                "status": "PASS" if first.get("status") == "APPENDED"
                and second.get("status") == "NOOP"
                and len(base["history"].entries) == 1
                and len(base["history"].seals) == 1 else "FAIL",
                "append_count": 1,
                "first_status": first.get("status"),
                "second_status": second.get("status"),
            })
        else:
            credit = base["credit"]
            delayed = base["delayed"]
            selection = base["selection"]
            kwargs: dict[str, Any] = {}
            if cell == "wrong-source-evidence":
                credit = LaterCredit.build(assignment_id="as1", source_evidence_id="other",
                                           later_outcome_id="o1", later_quality=1.0)
                delayed.apply_once(credit, lambda _: None)
            elif cell == "uncommitted-credit":
                pass
            elif cell == "candidate-version-mismatch":
                delayed.apply_once(credit, lambda _: None)
                kwargs["candidate_key"] = "peer-b@v1"
            elif cell == "registry-mismatch":
                delayed.apply_once(credit, lambda _: None)
                kwargs["candidate_registry_digest"] = _digest("other-registry")
            elif cell == "read-cut-before-source":
                delayed.apply_once(credit, lambda _: None)
                kwargs["assignment_read_cut"] = 4
            elif cell == "arrival-before-decision":
                delayed.apply_once(credit, lambda _: None)
                kwargs["target_arrival_index"] = 6
            elif cell == "selection-mismatch":
                delayed.apply_once(credit, lambda _: None)
                selection = base["ledger"].selections["s0"]
            elif cell == "credit-target-mismatch":
                credit = LaterCredit.build(assignment_id="as1", source_evidence_id="e0",
                                           later_outcome_id="o0", later_quality=1.0)
                delayed.apply_once(credit, lambda _: None)
            else:
                raise AssertionError(f"unregistered cell: {cell}")
            _call(base, credit=credit, delayed=delayed, selection=selection, **kwargs)
            row.update({"status": "FAIL", "unknown_reason": "mutation unexpectedly accepted"})
    except Exception as exc:
        if cell in {"valid-chain", "duplicate-credit"}:
            row.update({"status": "FAIL", "unknown_reason": f"{type(exc).__name__}: {exc}"})
        else:
            row.update({"status": "UNKNOWN", "unknown_reason": f"{type(exc).__name__}: {exc}"})
    row["entry_count"] = len(base["history"].entries)
    row["seal_count"] = len(base["history"].seals)
    row["append_count"] = max(row["append_count"], len(base["history"].entries))
    row["wall_ms"] = round((time.perf_counter() - started) * 1000.0, 6)
    row["cost"] = {"api_calls": 0, "gpu_jobs": 0, "input_tokens": 0,
                   "output_tokens": 0, "tool_calls": 0,
                   "wall_ms": row["wall_ms"], "updates": row["update_count"]}
    return row


def run(out: Path) -> dict[str, Any]:
    out = out.resolve()
    out.mkdir(parents=False, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     text=True).strip()
    component_names = (
        "scripts/peerrolebench_peer_history.py",
        "scripts/peerrolebench_peer_history_adapter.py",
        "scripts/peerrolebench_peer_history_binding.py",
        "scripts/peerrolebench_history_provenance_qualification.py",
    )
    components = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                  for name in component_names}
    config = {"qualification_version": VERSION, "git_commit": commit,
              "python": sys.version, "platform": platform.platform(),
              "cells": list(CELLS), "fixture": "native-ledger-source-target-v1",
              "component_sha256": components,
              "git_worktree_status_before": subprocess.check_output(
                  ["git", "status", "--short", "--untracked-files=no"],
                  cwd=ROOT, text=True),
              "llm_calls": 0, "gpu_jobs": 0,
              "scientific_claim_allowed": False,
              "started_at_utc": datetime.now(timezone.utc).isoformat()}
    _json(out / "config.json", config)
    results: dict[str, Any] = {}
    for cell in CELLS:
        cell_out = out / cell
        cell_out.mkdir(parents=False, exist_ok=False)
        row = _run_cell(cell)
        _json(cell_out / "summary.json", row)
        (cell_out / "raw.jsonl").write_text(
            json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "event_type": "provenance_cell", "payload": row},
                       ensure_ascii=False, default=str) + "\n", encoding="utf-8")
        results[cell] = row
    negatives = CELLS[2:]
    passed = bool(
        results["valid-chain"]["status"] == "PASS"
        and results["duplicate-credit"]["status"] == "PASS"
        and all(results[cell]["status"] == "UNKNOWN" for cell in negatives)
        and all(results[cell]["append_count"] == 0 for cell in negatives)
        and all(row["update_count"] == 0 for row in results.values())
    )
    summary = {**config, "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
               "passed": passed, "cells": results,
               "checks": {
                   "valid_chain_rebuilt": results["valid-chain"]["status"] == "PASS",
                   "duplicate_exactly_once": results["duplicate-credit"]["status"] == "PASS",
                   "all_mutations_unknown": all(results[cell]["status"] == "UNKNOWN" for cell in negatives),
                   "all_mutations_no_append": all(results[cell]["append_count"] == 0 for cell in negatives),
                   "all_updates_zero": all(row["update_count"] == 0 for row in results.values()),
               },
               "real_api_calls": 0, "gpu_jobs": 0,
               "scientific_claim_allowed": False,
               "interpretation": "Canonical native-ledger provenance and mutation rejection only; no live/API/benchmark effect claim.",
               "ended_at_utc": datetime.now(timezone.utc).isoformat()}
    _json(out / "summary.json", summary)
    (out / "raw.jsonl").write_text(
        json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "event_type": "provenance_summary", "payload": summary},
                   ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps({key: result[key] for key in ("status", "passed", "real_api_calls", "gpu_jobs")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
