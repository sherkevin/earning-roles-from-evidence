"""Zero-call matched replay for history/no-history/shuffled/reset consumption."""

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
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, PeerRoleLedger, PeerSelection,
    ProducerScore, RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_peer_history import PeerHistoryV1  # noqa: E402
from peerrolebench_peer_history_adapter import append_history_after_credit  # noqa: E402
from peerrolebench_history_selector import select_from_public_history  # noqa: E402
from peerrolebench_role_evidence_offer import PublicRoleEvidence, make_role_evidence_offer  # noqa: E402
from peerrolebench_two_stage_gate import DelayedCreditLedger, LaterCredit  # noqa: E402


VERSION = "peer-history-four-cell-qualification-v1"
TASK_ID = "PIPE3_stream_processing"
CELLS = ("history", "no-history", "shuffled-history", "reset-history")
CANDIDATES = ("peer-a@v1", "peer-b@v1")
READ_CUT = 20
RNG_SEED = 10


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def _fixture() -> tuple[Any, Any, Any, Any, str, str]:
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection("s0", TASK_ID, 0, "peer-r", "producer",
                                         ("peer-a", "peer-b"), "peer-a", 0.5))
    ledger.record_task_start(TASK_ID, 0)
    ledger.record_delivery(Delivery("d0", TASK_ID, "peer-a", "peer-r", "a" * 64,
                                    "source0", 0, "s0"))
    ledger.record_producer_score(ProducerScore(
        "q0", "d0", "a" * 64, "producer-score-v2", "PASS", 1, 1.0,
        "b" * 64, True, True))
    ledger.record_judgment(RecipientJudgment("j0", "d0", "peer-r", "accept", "a" * 64))
    ledger.record_action(ConsumerAction("c0", "d0", "peer-r", True, "a" * 64,
                                        "c" * 64, action="use"))
    ledger.record_outcome(TerminalOutcome("o0", "d0", True, "source-score-v1", 1.0, "d" * 64))
    ledger.record_evidence_update(RoleEvidenceUpdate("e0", "j0", "c0", "o0", "role-v1", 5.0))
    assignment = LaterAssignment("as1", TASK_ID, 1, "peer-a", "producer", ("e0",), 0.5)
    ledger.record_assignment(assignment)
    ledger.record_selection(PeerSelection("s1", TASK_ID, 1, "peer-r2", "producer",
                                         ("peer-a", "peer-b"), "peer-a", 0.5))
    ledger.record_task_start(TASK_ID, 1)
    ledger.record_delivery(Delivery("d1", TASK_ID, "peer-a", "peer-r2", "e" * 64,
                                    "source1", 1, "s1"))
    ledger.record_judgment(RecipientJudgment("j1", "d1", "peer-r2", "accept", "e" * 64))
    ledger.record_action(ConsumerAction("c1", "d1", "peer-r2", True, "e" * 64,
                                        "f" * 64, action="use"))
    ledger.record_outcome(TerminalOutcome("o1", "d1", True, "target-score-v1", 1.0, "1" * 64))
    registry = _digest("history-four-cell-registry-v1")
    row = PublicRoleEvidence(
        evidence_id="e0", candidate_key="peer-a@v1", role="producer", source_task_index=0,
        delivery_id="d0", judgment_id="j0", action_id="c0", outcome_id="o0",
        artifact_sha256="a" * 64, judgment="accept", action="use",
        outcome_status="PASS", quality_score=1.0, available_index=5,
    )
    offer = make_role_evidence_offer(
        offer_id="offer-four-cell", task_id=TASK_ID, task_index=1, role="producer",
        context_key="PIPE3:1", candidate_keys=CANDIDATES, evidence=(row,),
        evidence_version="role-v1", available_index=5,
        candidate_registry_digest=registry,
    )
    credit = LaterCredit.build(
        assignment_id="as1", source_evidence_id="e0",
        later_outcome_id="o1", later_quality=1.0,
    )
    delayed = DelayedCreditLedger()
    delayed.apply_once(credit, lambda _: None)
    history = PeerHistoryV1.empty("peer-a")
    append_history_after_credit(
        history=history, ledger=ledger, offer=offer,
        target_assignment=assignment, target_selection=ledger.selections["s1"], credit=credit,
        delayed_ledger=delayed, assignment_read_cut=5, target_decision_index=6,
        target_arrival_index=12, candidate_key="peer-a@v1",
        candidate_registry_digest=registry,
    )
    return ledger, offer, assignment, history, registry, _digest(ledger.events)


def _empty_projection(candidate: str) -> dict[str, Any]:
    return PeerHistoryV1.empty(candidate.split("@", 1)[0]).selector_projection(candidate_key=candidate)


def _shuffled_projection(history: PeerHistoryV1) -> dict[str, Any]:
    snapshot = deepcopy(history.snapshot())
    snapshot["entries"][0]["arrival_index"] = snapshot["seals"][0]["sealed_arrival_index"]
    payload = {key: snapshot[key] for key in ("schema", "version", "agent_key", "seals", "entries", "scopes")}
    snapshot["state_digest"] = _digest(payload)
    # Replaying the malformed snapshot is the canonical fail-closed check.
    PeerHistoryV1.replay(snapshot)
    raise AssertionError("shuffled history unexpectedly replayed")


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def run(out: Path) -> dict[str, Any]:
    out = out.resolve()
    out.mkdir(parents=False, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    tracked_components = {
        name: hashlib.sha256((ROOT / "scripts" / name).read_bytes()).hexdigest()
        for name in (
            "peerrolebench_peer_history.py",
            "peerrolebench_peer_history_adapter.py",
            "peerrolebench_history_selector.py",
            "peerrolebench_peer_history_binding.py",
        )
    }
    worktree_status = subprocess.check_output(
        ["git", "status", "--short", "--untracked-files=no"], cwd=ROOT, text=True
    )
    config = {
        "qualification_version": VERSION,
        "git_commit": commit,
        "python": sys.version,
        "platform": platform.platform(),
        "task_id": TASK_ID,
        "cells": list(CELLS),
        "candidate_keys": list(CANDIDATES),
        "read_cut": READ_CUT,
        "rng_seed": RNG_SEED,
        "fixture": "canonical-source-target-history-v1",
        "component_sha256": tracked_components,
        "git_worktree_status_before": worktree_status,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _json(out / "config.json", config)
    ledger, offer, assignment, valid_history, registry, fixture_digest = _fixture()
    results: dict[str, dict[str, Any]] = {}
    for cell in CELLS:
        cell_out = out / cell
        cell_out.mkdir(parents=False, exist_ok=False)
        started = time.perf_counter()
        row: dict[str, Any] = {
            "cell": cell, "fixture_digest": fixture_digest,
            "candidate_registry_digest": registry, "read_cut": READ_CUT,
            "rng_seed": RNG_SEED, "update_count": 0, "scientific_claim_allowed": False,
        }
        try:
            if cell == "history":
                candidate_histories = {
                    "peer-a@v1": valid_history,
                    "peer-b@v1": PeerHistoryV1.empty("peer-b"),
                }
            elif cell in {"no-history", "reset-history"}:
                candidate_histories = {
                    key: PeerHistoryV1.empty(key.split("@", 1)[0]) for key in CANDIDATES
                }
            else:
                candidate_histories = {"peer-a@v1": valid_history, "peer-b@v1": PeerHistoryV1.empty("peer-b")}
            if cell == "shuffled-history":
                _shuffled_projection(valid_history)
            projections = {
                key: history.selector_projection(candidate_key=key)
                for key, history in candidate_histories.items()
            }
            selection = select_from_public_history(
                candidate_keys=CANDIDATES, projections=projections,
                base_scores=(0.0, 0.0), read_cut=READ_CUT, rng_seed=RNG_SEED,
            )
            row.update({
                "status": "PASS", "history_input_digest": selection["input_digest"],
                "projection_digests": selection["projection_digests"],
                "selection": selection, "history_entry_counts": {
                    key: projections[key]["entry_count"] for key in CANDIDATES
                },
            })
        except Exception as exc:
            row.update({
                "status": "UNKNOWN", "unknown_reason": f"{type(exc).__name__}: {exc}",
                "history_input_digest": None, "selection": None,
            })
        elapsed_ms = round((time.perf_counter() - started) * 1000.0, 6)
        row["append_update_latency_ms"] = elapsed_ms
        row["cost"] = {
            "api_calls": 0,
            "gpu_jobs": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "tool_calls": 0,
            "replay_events": len(ledger.events),
            "wall_ms": elapsed_ms,
            "updates": row["update_count"],
        }
        _json(cell_out / "summary.json", row)
        (cell_out / "raw.jsonl").write_text(
            json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "event_type": "cell_result", "payload": row},
                       ensure_ascii=False, default=str) + "\n", encoding="utf-8"
        )
        results[cell] = row
    history_row, no_history_row, shuffled_row, reset_row = (results[cell] for cell in CELLS)
    same_empty = (
        no_history_row["status"] == "PASS" and reset_row["status"] == "PASS"
        and no_history_row["selection"] == reset_row["selection"]
        and no_history_row["history_input_digest"] == reset_row["history_input_digest"]
    )
    history_effect = (
        history_row["status"] == "PASS"
        and history_row["history_input_digest"] != no_history_row["history_input_digest"]
        and history_row["selection"]["propensity"] != no_history_row["selection"]["propensity"]
    )
    rejection = shuffled_row["status"] == "UNKNOWN" and shuffled_row.get("selection") is None
    passed = bool(same_empty and history_effect and rejection and all(
        result["update_count"] == 0 for result in results.values()
    ))
    summary = {
        **config,
        "status": "QUALIFIED_OFFLINE" if passed else "FAILED_OFFLINE",
        "passed": passed,
        "fixture_digest": fixture_digest,
        "cells": results,
        "checks": {"history_effect": history_effect, "empty_reset_equal": same_empty,
                   "shuffled_rejected": rejection, "all_updates_zero": all(
                       result["update_count"] == 0 for result in results.values())},
        "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "interpretation": "Public projection consumption and fail-closed reset/shuffle checks only; no peer suitability or quality/cost claim.",
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _json(out / "summary.json", summary)
    (out / "raw.jsonl").write_text(
        json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "event_type": "four_cell_summary", "payload": summary},
                   ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
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
