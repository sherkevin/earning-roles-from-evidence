"""Qualify canonical ledger + sidecar stream replay without LLM/GPU."""

from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, PeerRoleLedger, PeerSelection,
    RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_baseline_policies import CandidateRef, TerminalOnlyPolicy  # noqa: E402
from peerrolebench_policy_sidecar import DecisionSidecar, FeedbackSidecar  # noqa: E402
from peerrolebench_policy_sidecar_replay import SidecarRow, replay_policy_sidecars  # noqa: E402


ARTIFACT = "b" * 64
DIGEST = "a" * 64


def canonical_ledger() -> list[dict]:
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection(
        selection_id="selection-0", task_id="task", task_index=0, selector_id="peer-a",
        role="producer", candidate_ids=("peer-b", "peer-c"), chosen_peer_id="peer-b", propensity=0.5,
    ))
    ledger.record_task_start("task", 0)
    ledger.record_delivery(Delivery(
        delivery_id="delivery-0", task_id="task", producer_id="peer-b", recipient_id="peer-a",
        artifact_sha256=ARTIFACT, source_event_id="request-0", task_index=0, selection_id="selection-0",
    ))
    ledger.record_judgment(RecipientJudgment(
        judgment_id="judgment-0", delivery_id="delivery-0", consumer_id="peer-a",
        decision="accept_with_rework", observed_artifact_sha256=ARTIFACT,
    ))
    ledger.record_action(ConsumerAction(
        action_id="action-0", delivery_id="delivery-0", consumer_id="peer-a",
        used_artifact=True, input_artifact_sha256=ARTIFACT, repair_cost=1.0, action="repair",
    ))
    ledger.record_outcome(TerminalOutcome(
        outcome_id="outcome-0", delivery_id="delivery-0", success=True,
        scorer_version="terminal-v1", partial_score=1.0,
    ))
    ledger.record_evidence_update(RoleEvidenceUpdate(
        evidence_id="evidence-0", judgment_id="judgment-0", action_id="action-0",
        outcome_id="outcome-0", update_version="evidence-v1", arrived_at=13.0,
    ))
    return ledger.events


def _record_by_type(events: list[dict], event_type: str) -> dict:
    return next(row for row in events if row["event_type"] == event_type)


def sidecars(events: list[dict]) -> dict[str, SidecarRow]:
    selection_record = _record_by_type(events, "peer_selection")
    judgment_record = _record_by_type(events, "recipient_judgment")
    outcome_record = _record_by_type(events, "terminal_outcome")
    selection = DecisionSidecar(
        ledger_record_hash=selection_record["record_hash"], protocol_event_type="peer_selection",
        protocol_event_id="selection-0", task_id="task", task_index=0, role="producer",
        event_id="policy-selection-0", selector_id="peer-a", context_key="ctx",
        candidates=(CandidateRef("peer-b", "v1"), CandidateRef("peer-c", "v1")),
        base_scores=(0.5, 0.5), chosen_index=0, probabilities=(0.5, 0.5), propensity=0.5,
        state_version="state-0", encoder_version="enc-0", feature_schema="phi-0",
        policy_name="terminal_only", policy_version="v1", base_score_version="base-v1",
        rng_algorithm="numpy-pcg64", rng_draw=0, selected_at=10.0,
    )
    judgment = FeedbackSidecar(
        ledger_record_hash=judgment_record["record_hash"], protocol_event_type="recipient_judgment",
        protocol_event_id="judgment-0", feedback_id="feedback-judgment-0",
        source_event_id="policy-selection-0", selection_event_id="selection-0",
        delivery_id="delivery-0", producer_id="peer-b", producer_version="v1", recipient_id="peer-a",
        source="recipient_judgment", arrived_at=12.0, delay=2.0, action="repair",
        disposition="unknown", provenance="unknown", label_mapping_version="", mapping_digest="",
        responsibility_status="unknown", attribution_basis="", raw_value="accept_with_rework", label=None,
    )
    outcome = FeedbackSidecar(
        ledger_record_hash=outcome_record["record_hash"], protocol_event_type="terminal_outcome",
        protocol_event_id="outcome-0", feedback_id="feedback-outcome-0",
        source_event_id="policy-selection-0", selection_event_id="selection-0",
        delivery_id="delivery-0", producer_id="peer-b", producer_version="v1", recipient_id="peer-a",
        source="terminal_outcome", arrived_at=13.0, delay=3.0, action="use",
        disposition="eligible", provenance="public", label_mapping_version="terminal-v1",
        mapping_digest=DIGEST, responsibility_status="attributed", attribution_basis="terminal-v1",
        raw_value=True, label=1.0,
    )
    return {
        "selection": SidecarRow(selection, selection_record, selection.sidecar_digest),
        "judgment": SidecarRow(judgment, judgment_record, judgment.sidecar_digest),
        "outcome": SidecarRow(outcome, outcome_record, outcome.sidecar_digest),
    }


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    events = canonical_ledger()
    rows = sidecars(events)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"
    config = {
        "experiment_id": "n03_policy_sidecar_stream_qualification_20260928",
        "kind": "engineering_canonical_replay_qualification_not_scientific_benchmark",
        "runtime": {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                    "python": platform.python_version(), "git_commit": commit},
        "protocol_fixture": "in_memory_complete_peer_role_ledger_v1",
        "replay_order": "selections=canonical ledger index; feedback=(arrived_at, protocol_event_id)",
        "cases": ["canonical", "feedback_permuted", "duplicate_sidecar", "truncated_ledger_unknown", "wrong_producer"],
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    raw_path = out_dir / "raw.jsonl"

    def log(kind: str, payload: dict) -> None:
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": kind, "payload": payload}, sort_keys=True) + "\n")
            handle.flush()

    cases: list[dict] = []
    canonical = replay_policy_sidecars(
        events, [rows["selection"], rows["judgment"], rows["outcome"]], TerminalOnlyPolicy,
    )
    cases.append({"case": "canonical", "result": canonical,
                  "expectation_met": canonical["status"] == "PASS" and canonical["update_count"] == 1
                  and canonical["unknown_count"] == 1})
    permuted = replay_policy_sidecars(
        events, [rows["selection"], rows["outcome"], rows["judgment"]], TerminalOnlyPolicy,
    )
    cases.append({"case": "feedback_permuted", "result": permuted,
                  "expectation_met": permuted["status"] == "PASS"
                  and permuted["final_snapshot"] == canonical["final_snapshot"]})
    duplicate = replay_policy_sidecars(
        events, [rows["selection"], rows["judgment"], rows["outcome"], rows["outcome"]], TerminalOnlyPolicy,
    )
    cases.append({"case": "duplicate_sidecar", "result": duplicate,
                  "expectation_met": duplicate["status"] == "INVALID" and duplicate["update_count"] == 0})
    truncated = events[:next(i for i, row in enumerate(events) if row["event_type"] == "terminal_outcome")]
    truncated_rows = [rows["selection"], rows["judgment"]]
    truncated_result = replay_policy_sidecars(truncated, truncated_rows, TerminalOnlyPolicy)
    cases.append({"case": "truncated_ledger_unknown", "result": truncated_result,
                  "expectation_met": truncated_result["status"] == "UNKNOWN"
                  and truncated_result["update_allowed"] is False and truncated_result["update_count"] == 0})
    wrong = replace(rows["outcome"].sidecar, producer_id="peer-c")
    wrong_row = SidecarRow(wrong, rows["outcome"].ledger_record, wrong.sidecar_digest)
    wrong_result = replay_policy_sidecars(
        events, [rows["selection"], rows["judgment"], wrong_row], TerminalOnlyPolicy,
    )
    cases.append({"case": "wrong_producer", "result": wrong_result,
                  "expectation_met": wrong_result["status"] == "INVALID" and wrong_result["update_count"] == 0})
    for case in cases:
        log("case_result", {"case": case["case"], "expectation_met": case["expectation_met"],
                             "status": case["result"]["status"], "update_count": case["result"]["update_count"],
                             "unknown_count": case["result"].get("unknown_count", 0),
                             "duplicate_count": case["result"].get("duplicate_count", 0)})
    summary = {
        "experiment_id": config["experiment_id"], "passed": all(case["expectation_met"] for case in cases),
        "case_count": len(cases), "cases": cases, "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False, "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    log("summary", {"passed": summary["passed"], "case_count": summary["case_count"],
                     "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False})
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({key: result[key] for key in ("passed", "case_count", "real_api_calls",
                                                   "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
