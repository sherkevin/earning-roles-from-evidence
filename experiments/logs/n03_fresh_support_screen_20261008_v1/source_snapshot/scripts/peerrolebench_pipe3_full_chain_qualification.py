"""Zero-call PIPE3 full-chain protocol qualification.

This is an engineering gate for the future live PIPE3 runner.  It builds two
strict episodes and checks selection -> task start -> delivery -> producer
score -> situated judgment -> action -> terminal outcome -> role evidence ->
later assignment -> next selection.  Policy sidecars, a separate assignment
attestation chain, and a frozen global feedback-arrival schedule are replayed
with the responsibility-lineage gate.  No LLM/API/GPU is used and no
scientific efficacy claim is permitted.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, PeerRoleLedger, PeerSelection,
    ProducerScore, RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_baseline_policies import TerminalOnlyPolicy  # noqa: E402
from peerrolebench_assignment_manifest import build_manifest as build_aux_manifest  # noqa: E402
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_event_time_schedule import ArrivalAssignment, validate_schedule, schedule_digest  # noqa: E402
from peerrolebench_pipe3_runner_v1 import Pipe3SelectionBoundary, make_offer, auxiliary_manifest_root  # noqa: E402
from peerrolebench_policy_sidecar import FeedbackSidecar, LINEAGE_SIDECAR_VERSION  # noqa: E402
from peerrolebench_policy_sidecar_manifest import build_manifest as build_native_manifest  # noqa: E402
from peerrolebench_policy_sidecar_replay import SidecarRow, replay_policy_sidecars  # noqa: E402
from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402

ARTIFACTS = {
    "peer-b": "b" * 64,
    "peer-c": "c" * 64,
}

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()

def registry() -> list[CandidateRegistryEntry]:
    model_config = "a" * 64
    return [
        CandidateRegistryEntry("peer-b", "v1", ARTIFACTS["peer-b"], "fixture-model", model_config),
        CandidateRegistryEntry("peer-c", "v1", ARTIFACTS["peer-c"], "fixture-model", model_config),
    ]

def _score(delivery_id: str, artifact: str, suffix: str) -> ProducerScore:
    payload = sha_text(f"producer-score:{delivery_id}:{suffix}")
    return ProducerScore(
        f"producer-score-{suffix}", delivery_id, artifact, "pipe3-producer-objective-v2",
        "PASS", 1, 1.0, payload, True, True,
    )

def _append_episode(boundary: Pipe3SelectionBoundary, *, task_index: int, selection, producer_id: str,
                    artifact: str, suffix: str, selected_at: float, judgment_decision: str = "accept_with_rework") -> dict[str, Any]:
    task_id = "PIPE3_stream_processing"
    boundary.ledger.record_task_start(task_id, task_index)
    delivery = Delivery(
        f"delivery-{suffix}", task_id, producer_id, "peer-a", artifact,
        f"produce-{suffix}", task_index, selection.native_selection.selection_id,
    )
    boundary.ledger.record_delivery(delivery)
    boundary.ledger.record_producer_score(_score(delivery.delivery_id, artifact, suffix))
    judgment = RecipientJudgment(
        f"judgment-{suffix}", delivery.delivery_id, "peer-a", judgment_decision, artifact,
    )
    boundary.ledger.record_judgment(judgment)
    action_name = {"accept": "use", "accept_with_rework": "repair", "reject_redo": "independent_redo", "reject_reroute": "reject"}[judgment_decision]
    action = ConsumerAction(
        f"action-{suffix}", delivery.delivery_id, "peer-a", action_name in {"use", "repair"},
        artifact, None, 0.0 if action_name == "use" else 1.0, action_name,
    )
    boundary.ledger.record_action(action)
    outcome = TerminalOutcome(
        f"outcome-{suffix}", delivery.delivery_id, True, "pipe3-terminal-v2", 1.0,
        sha_text(f"terminal:{suffix}"),
    )
    boundary.ledger.record_outcome(outcome)
    evidence = RoleEvidenceUpdate(
        f"evidence-{suffix}", judgment.judgment_id, action.action_id,
        outcome.outcome_id, "pipe3-lineage-v3", selected_at + 3.0,
    )
    boundary.ledger.record_evidence_update(evidence)
    return {"selection": selection, "delivery": delivery, "judgment": judgment,
            "action": action, "outcome": outcome, "evidence": evidence}

def _make_feedback(ep: dict[str, Any], boundary: Pipe3SelectionBoundary, *, source: str,
                   feedback_id: str, arrived_at: float, label: float) -> SidecarRow:
    event = ep["judgment"] if source == "recipient_judgment" else ep["outcome"]
    event_type = source
    id_field = "judgment_id" if source == "recipient_judgment" else "outcome_id"
    record = next(row for row in boundary.ledger.events if row["event_type"] == event_type and row["payload"][id_field] == getattr(event, id_field))
    delivery = ep["delivery"]
    action = ep["action"]
    sidecar = FeedbackSidecar(
        ledger_record_hash=record["record_hash"], protocol_event_type=event_type,
        protocol_event_id=getattr(event, id_field), feedback_id=feedback_id,
        source_event_id=ep["selection"].policy_selection.event_id,
        selection_event_id=ep["selection"].native_selection.selection_id,
        delivery_id=delivery.delivery_id, producer_id=delivery.producer_id,
        producer_version="v1", recipient_id=delivery.recipient_id, source=source,
        arrived_at=arrived_at, delay=arrived_at - ep["selection"].policy_selection.selected_at,
        action=action.action, disposition="eligible", provenance="public",
        label_mapping_version="pipe3-label-v1", mapping_digest="d" * 64,
        responsibility_status="attributed", attribution_basis="terminal-v2",
        artifact_sha256=delivery.artifact_sha256,
        delivery_record_hash=next(row for row in boundary.ledger.events if row["event_type"] == "producer_delivery" and row["payload"]["delivery_id"] == delivery.delivery_id)["record_hash"],
        action_id=action.action_id,
        action_record_hash=next(row for row in boundary.ledger.events if row["event_type"] == "consumer_action" and row["payload"]["action_id"] == action.action_id)["record_hash"],
        raw_value=label, label=label, sidecar_version=LINEAGE_SIDECAR_VERSION,
    )
    return SidecarRow(sidecar, record, sidecar.sidecar_digest)

def _unknown_control() -> dict[str, Any]:
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    selection = PeerSelection("selection-unknown", "PIPE3_stream_processing", 0, "peer-a", "producer", ("peer-b",), "peer-b", 1.0)
    ledger.record_selection(selection)
    ledger.record_task_start("PIPE3_stream_processing", 0)
    delivery = Delivery("delivery-unknown", "PIPE3_stream_processing", "peer-b", "peer-a", ARTIFACTS["peer-b"], "produce-unknown", 0, selection.selection_id)
    ledger.record_delivery(delivery)
    ledger.record_producer_score(ProducerScore("producer-score-unknown", delivery.delivery_id, delivery.artifact_sha256, "pipe3-producer-objective-v2", "UNKNOWN", None, None, None, False, False))
    replay = replay_ledger_events(ledger.events, allow_incomplete=True)
    return {"status": replay.status, "complete": replay.complete, "missing": list(replay.missing), "update_allowed": False, "policy_updates": 0, "event_count": replay.event_count}

def run(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"
    config = {
        "experiment_id": "n03_pipe3_full_chain_qualification_20260928",
        "qualification_version": "pipe3-full-chain-v1",
        "kind": "zero_api_zero_gpu_protocol_and_lineage_gate",
        "protocol_order": ["peer_selection", "task_start", "producer_delivery", "producer_score", "recipient_judgment", "consumer_action", "terminal_outcome", "role_evidence_update", "later_assignment", "peer_selection"],
        "policy": "terminal_only",
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
        "runtime": {"started_at_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(), "git_commit": commit},
        "fault_cases": ["unknown_scorer_no_update", "wrong_lineage", "late_offer", "missing_schedule"],
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    raw_path = out_dir / "raw.jsonl"
    def log(event_type: str, payload: Any) -> None:
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(), "event_type": event_type, "payload": payload}, sort_keys=True) + "\n")
            handle.flush()
    log("config", config)

    reg = registry()
    boundary = Pipe3SelectionBoundary(TerminalOnlyPolicy(), reg)
    offer0 = make_offer(offer_id="offer-0", task_id="PIPE3_stream_processing", task_index=0, role="producer", context_key="ctx-0", candidate_keys=("peer-b@v1", "peer-c@v1"), public_rows=(), evidence_version="evidence-v3", available_index=0)
    seal0 = boundary.choose_and_seal(offer=offer0, native_selection_id="selection-0", selector_id="peer-a", role="producer", base_scores=(100.0, -100.0), rng=np.random.default_rng(0), state_version="state-0", encoder_version="enc-0", feature_schema="pipe3", policy_version="terminal-v1", base_score_version="base-v1", rng_algorithm="numpy-pcg64", rng_draw=0, selected_at=0.0, read_cut=0, decision_index=0, consume_evidence=False)
    assert seal0.native_selection.chosen_peer_id == "peer-b"
    ep0 = _append_episode(boundary, task_index=0, selection=seal0, producer_id="peer-b", artifact=ARTIFACTS["peer-b"], suffix="0", selected_at=0.0)

    boundary.ledger.record_assignment(LaterAssignment("assignment-1", "PIPE3_stream_processing", 1, "peer-b", "producer", ("evidence-0",), 1.0))
    outcome0 = _make_feedback(ep0, boundary, source="terminal_outcome", feedback_id="feedback-outcome-0", arrived_at=5.0, label=1.0)
    offer1 = make_offer(offer_id="offer-1", task_id="PIPE3_stream_processing", task_index=1, role="producer", context_key="ctx-1", candidate_keys=("peer-b@v1", "peer-c@v1"), public_rows=({
        "feedback_id": outcome0.sidecar.feedback_id, "source_event_id": outcome0.sidecar.source_event_id, "source": "terminal_outcome", "candidate_key": "peer-b@v1", "evidence_version": "evidence-v3", "source_index": 0, "arrival_index": 1, "arrived_at": 5.0, "delay": 5.0, "action": "repair", "disposition": "eligible", "provenance": "public", "label": 1.0,
    },), evidence_version="evidence-v3", available_index=1, previous_aux_hash=auxiliary_manifest_root(boundary.auxiliary_manifest_rows))
    seal1 = boundary.choose_and_seal(offer=offer1, native_selection_id="selection-1", selector_id="peer-a", role="producer", base_scores=(100.0, -100.0), rng=np.random.default_rng(1), state_version="state-1", encoder_version="enc-0", feature_schema="pipe3", policy_version="terminal-v1", base_score_version="base-v1", rng_algorithm="numpy-pcg64", rng_draw=1, selected_at=10.0, read_cut=1, decision_index=2, consume_evidence=True)
    assert seal1.native_selection.chosen_peer_id == "peer-b"
    ep1 = _append_episode(boundary, task_index=1, selection=seal1, producer_id="peer-b", artifact=ARTIFACTS["peer-b"], suffix="1", selected_at=10.0)

    judgment0 = _make_feedback(ep0, boundary, source="recipient_judgment", feedback_id="feedback-judgment-0", arrived_at=4.0, label=0.75)
    judgment1 = _make_feedback(ep1, boundary, source="recipient_judgment", feedback_id="feedback-judgment-1", arrived_at=14.0, label=0.75)
    outcome1 = _make_feedback(ep1, boundary, source="terminal_outcome", feedback_id="feedback-outcome-1", arrived_at=15.0, label=1.0)
    sidecar_rows = [seal0 and SidecarRow(seal0.decision_sidecar, boundary.ledger.events[0], seal0.decision_sidecar.sidecar_digest), judgment0, outcome0, seal1 and SidecarRow(seal1.decision_sidecar, next(row for row in boundary.ledger.events if row["event_type"] == "peer_selection" and row["payload"]["selection_id"] == "selection-1"), seal1.decision_sidecar.sidecar_digest), judgment1, outcome1]
    native_rows = [{"ledger_record_hash": row.sidecar.payload()["ledger_record_hash"], "protocol_event_type": row.sidecar.protocol_event_type, "protocol_event_id": row.sidecar.protocol_event_id, "sidecar_digest": row.sidecar.sidecar_digest} for row in sidecar_rows]
    native_manifest = build_native_manifest(native_rows)
    schedule = [
        ArrivalAssignment(judgment0.sidecar.feedback_id, "recipient_judgment", judgment0.sidecar.protocol_event_id, judgment0.sidecar.source_event_id, 0),
        ArrivalAssignment(outcome0.sidecar.feedback_id, "terminal_outcome", outcome0.sidecar.protocol_event_id, outcome0.sidecar.source_event_id, 1),
        ArrivalAssignment(judgment1.sidecar.feedback_id, "recipient_judgment", judgment1.sidecar.protocol_event_id, judgment1.sidecar.source_event_id, 2),
        ArrivalAssignment(outcome1.sidecar.feedback_id, "terminal_outcome", outcome1.sidecar.protocol_event_id, outcome1.sidecar.source_event_id, 3),
    ]
    schedule_order = validate_schedule(schedule, expected_feedback_ids=[row.sidecar.feedback_id for row in (judgment0, outcome0, judgment1, outcome1)])
    canonical = replay_policy_sidecars(boundary.ledger.events, sidecar_rows, TerminalOnlyPolicy, native_manifest, require_responsibility_lineage=True)
    canonical_ledger = replay_ledger_events(boundary.ledger.events)
    native_root, aux_root = boundary.validate_selection_manifests()
    cases = [{"case": "canonical", "status": canonical["status"], "ledger_status": canonical["ledger_status"], "update_count": canonical["update_count"], "native_manifest_root": canonical.get("manifest_root"), "aux_manifest_root": aux_root, "schedule_digest": schedule_digest(schedule_order), "ledger_event_count": len(boundary.ledger.events), "expectation_met": canonical["status"] == "PASS" and canonical["update_count"] == 2 and canonical_ledger.status == "PASS" and len(boundary.ledger.events) == 17}]
    unknown = _unknown_control()
    cases.append({"case": "unknown_scorer_no_update", **unknown, "expectation_met": unknown["status"] == "UNKNOWN" and not unknown["complete"] and not unknown["update_allowed"] and unknown["policy_updates"] == 0})
    wrong = replace(outcome0.sidecar, producer_id="peer-c")
    wrong_row = SidecarRow(wrong, outcome0.ledger_record, wrong.sidecar_digest)
    wrong_rows = [seal0 and SidecarRow(seal0.decision_sidecar, boundary.ledger.events[0], seal0.decision_sidecar.sidecar_digest), judgment0, wrong_row, seal1 and SidecarRow(seal1.decision_sidecar, next(row for row in boundary.ledger.events if row["event_type"] == "peer_selection" and row["payload"]["selection_id"] == "selection-1"), seal1.decision_sidecar.sidecar_digest), judgment1, outcome1]
    wrong_result = replay_policy_sidecars(boundary.ledger.events, wrong_rows, TerminalOnlyPolicy, build_native_manifest([{"ledger_record_hash": r.sidecar.payload()["ledger_record_hash"], "protocol_event_type": r.sidecar.protocol_event_type, "protocol_event_id": r.sidecar.protocol_event_id, "sidecar_digest": r.sidecar.sidecar_digest} for r in wrong_rows]), require_responsibility_lineage=True)
    cases.append({"case": "wrong_lineage", "status": wrong_result["status"], "update_count": wrong_result["update_count"], "error": wrong_result.get("error"), "expectation_met": wrong_result["status"] == "INVALID" and wrong_result["update_count"] == 0})
    try:
        make_offer(offer_id="late-offer", task_id="PIPE3_stream_processing", task_index=1, role="producer", context_key="ctx-late", candidate_keys=("peer-b@v1", "peer-c@v1"), public_rows=({"feedback_id": outcome0.sidecar.feedback_id, "source_event_id": outcome0.sidecar.source_event_id, "source": "terminal_outcome", "candidate_key": "peer-b@v1", "evidence_version": "evidence-v3", "source_index": 0, "arrival_index": 1, "arrived_at": 5.0, "delay": 5.0, "action": "repair", "disposition": "eligible", "provenance": "public", "label": 1.0},), evidence_version="evidence-v3", available_index=0)
        late = {"status": "PASS", "error": None}
    except ValueError as exc:
        late = {"status": "INVALID", "error": str(exc)}
    cases.append({"case": "late_offer", **late, "expectation_met": late["status"] == "INVALID"})
    try:
        validate_schedule(schedule[:-1], expected_feedback_ids=[row.sidecar.feedback_id for row in (judgment0, outcome0, judgment1, outcome1)])
        missing = {"status": "PASS", "error": None}
    except ValueError as exc:
        missing = {"status": "INVALID", "error": str(exc)}
    cases.append({"case": "missing_schedule", **missing, "expectation_met": missing["status"] == "INVALID"})
    summary = {**config, "passed": all(case["expectation_met"] for case in cases), "case_count": len(cases), "cases": cases, "native_manifest_root": native_root, "auxiliary_manifest_root": aux_root, "ledger_status": canonical_ledger.status, "ledger_event_count": len(boundary.ledger.events), "schedule_digest": schedule_digest(schedule_order), "ended_at_utc": datetime.now(timezone.utc).isoformat()}
    for event in boundary.ledger.events:
        log("ledger_event", event)
    for row in sidecar_rows:
        log("sidecar_row", {"protocol_event_type": row.sidecar.protocol_event_type,
                             "protocol_event_id": row.sidecar.protocol_event_id,
                             "sidecar_digest": row.sidecar.sidecar_digest,
                             "ledger_record_hash": row.ledger_record["record_hash"]})
    log("summary", summary)
    (out_dir / "ledger.json").write_text(json.dumps(boundary.ledger.events, indent=2) + "\n", encoding="utf-8")
    (out_dir / "native_sidecar_manifest.json").write_text(json.dumps(native_manifest, indent=2) + "\n", encoding="utf-8")
    (out_dir / "native_sidecar_rows.jsonl").write_text(
        "".join(json.dumps({"ledger_record_hash": row.ledger_record["record_hash"],
                            "protocol_event_type": row.sidecar.protocol_event_type,
                            "protocol_event_id": row.sidecar.protocol_event_id,
                            "sidecar": row.sidecar.payload(),
                            "sidecar_digest": row.sidecar.sidecar_digest}, sort_keys=True) + "\n"
                for row in sidecar_rows), encoding="utf-8")
    (out_dir / "assignment_aux_rows.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in boundary.auxiliary_manifest_rows), encoding="utf-8")
    (out_dir / "assignment_manifest.json").write_text(
        json.dumps(build_aux_manifest(boundary.auxiliary_manifest_rows), indent=2) + "\n", encoding="utf-8")
    (out_dir / "candidate_registry.json").write_text(
        json.dumps({"entries": [entry.payload() for entry in reg]}, indent=2) + "\n", encoding="utf-8")
    (out_dir / "arrival_schedule.json").write_text(json.dumps([row.payload() for row in schedule_order], indent=2) + "\n", encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({key: result[key] for key in ("passed", "case_count", "real_api_calls", "gpu_jobs", "scientific_claim_allowed", "ledger_status", "ledger_event_count")}, indent=2))
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
