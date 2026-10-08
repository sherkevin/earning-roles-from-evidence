"""Zero-call qualification for the PIPE3 live-runner precondition contract."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, PeerRoleLedger, PeerSelection,
    ProducerScore, RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_baseline_policies import TerminalOnlyPolicy  # noqa: E402
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_pipe3_live_contract import (  # noqa: E402
    VERSION, classify_ownership, unknown_no_update, validate_ledger_key_binding,
    validate_selection_receipt, validate_source_target_schedule,
)


def _registry():
    return [CandidateRegistryEntry("peer-b", "v1", "b" * 64, "fixture", "c" * 64),
            CandidateRegistryEntry("peer-c", "v1", "c" * 64, "fixture", "c" * 64)]


def _ledger():
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    artifact = "a" * 64
    ledger.record_selection(PeerSelection("s0", "PIPE3_stream_processing", 0, "selector", "producer", ("peer-b", "peer-c"), "peer-b", .5))
    ledger.record_task_start("PIPE3_stream_processing", 0)
    ledger.record_delivery(Delivery("d0", "PIPE3_stream_processing", "peer-b", "recipient", artifact, "src", 0, "s0"))
    ledger.record_producer_score(ProducerScore("q0", "d0", artifact, "qp", "PASS", 1, 1.0, "d" * 64, True, True))
    ledger.record_judgment(RecipientJudgment("j0", "d0", "recipient", "accept", artifact))
    ledger.record_action(ConsumerAction("a0", "d0", "recipient", True, artifact, "e" * 64, 0.0, "use"))
    ledger.record_outcome(TerminalOutcome("y0", "d0", True, "qr", 1.0, "f" * 64))
    ledger.record_evidence_update(RoleEvidenceUpdate("e0", "j0", "a0", "y0", "v1", 1.0))
    ledger.record_assignment(LaterAssignment("as1", "PIPE3_stream_processing", 1, "peer-b", "producer", ("e0",), .5))
    ledger.record_selection(PeerSelection("s1", "PIPE3_stream_processing", 1, "selector", "producer", ("peer-b", "peer-c"), "peer-b", .5))
    ledger.record_task_start("PIPE3_stream_processing", 1)
    ledger.record_delivery(Delivery("d1", "PIPE3_stream_processing", "peer-b", "recipient", "b" * 64, "src1", 1, "s1"))
    ledger.record_producer_score(ProducerScore("q1", "d1", "b" * 64, "qp", "PASS", 1, 1.0, "d" * 64, True, True))
    ledger.record_judgment(RecipientJudgment("j1", "d1", "recipient", "accept", "b" * 64))
    ledger.record_action(ConsumerAction("a1", "d1", "recipient", True, "b" * 64, "e" * 64, 0.0, "use"))
    ledger.record_outcome(TerminalOutcome("y1", "d1", True, "qr", 1.0, "f" * 64))
    ledger.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "a1", "y1", "v1", 2.0))
    return ledger


def _case(name, passed, details):
    return {"case": name, "passed": bool(passed), "details": details}


def run(out_dir: Path) -> dict:
    out_dir = out_dir.resolve(); out_dir.mkdir(parents=False, exist_ok=False)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"
    config = {
        "qualification_version": VERSION,
        "kind": "zero_call_pipe3_live_runner_precondition_contract",
        "task_id": "PIPE3_stream_processing",
        "real_api_calls": 0, "gpu_jobs": 0, "candidate_execution": 0,
        "native_grader_invoked": False, "policy_updates": 0,
        "scientific_claim_allowed": False,
        "runtime": {"python": platform.python_version(), "git_commit": commit,
                     "started_at_utc": datetime.now(timezone.utc).isoformat()},
        "unknown_rule": "UNKNOWN writes no label, assignment, target selection, or policy update",
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    raw_path = out_dir / "raw.jsonl"
    def log(event_type, payload):
        with raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload}, sort_keys=True) + "\n")
            handle.flush()
    log("config", config)
    cases = []
    entries = _registry()
    registry_payload = {"entries": [entry.payload() for entry in entries]}
    (out_dir / "candidate_registry.json").write_text(json.dumps(registry_payload, indent=2) + "\n", encoding="utf-8")

    ledger = _ledger()
    binding = validate_ledger_key_binding(ledger.events)
    schedule = validate_source_target_schedule(events=ledger.events, source_task_index=0,
        target_task_index=1, evidence_id="e0", assignment_id="as1", target_selection_id="s1")
    cases.append(_case("source_to_target_schedule_and_ledger_binding", binding["valid"] and schedule["valid"],
                       {"ledger": binding, "schedule": schedule}))
    bad_schedule = validate_source_target_schedule(events=ledger.events, source_task_index=1,
        target_task_index=0, evidence_id="e0", assignment_id="as1", target_selection_id="s1")
    cases.append(_case("reject_reversed_source_target", not bad_schedule["valid"], bad_schedule))

    policy = TerminalOnlyPolicy()
    selection = policy.choose(event_id="selection-contract", context_key="ctx", selector_id="selector",
        candidates=tuple(__import__("peerrolebench_baseline_policies", fromlist=["CandidateRef"]).CandidateRef(e.candidate_id, e.candidate_version) for e in entries),
        base_scores=(0.0, 0.0), rng=np.random.default_rng(0), state_version="s0",
        encoder_version="e0", feature_schema="f0", selected_at=0.0)
    receipt = validate_selection_receipt(registry=entries, menu_keys=tuple(ref.key for ref in selection.candidates),
        chosen_key=selection.chosen.key, probabilities=selection.probabilities,
        chosen_index=selection.chosen_index, propensity=selection.propensity)
    cases.append(_case("candidate_registry_menu_and_propensity", receipt["valid"], receipt))
    ownership = [
        classify_ownership(changed_paths=("producer.py",), producer_paths=("producer.py",), recipient_paths=("processor.py",), producer_defect_registered=True, producer_score_status="FAIL", producer_label=0),
        classify_ownership(changed_paths=("processor.py",), producer_paths=("producer.py",), recipient_paths=("processor.py",), producer_defect_registered=True, producer_score_status="FAIL", producer_label=0),
        classify_ownership(changed_paths=("producer.py", "processor.py"), producer_paths=("producer.py",), recipient_paths=("processor.py",), producer_defect_registered=True, producer_score_status="FAIL", producer_label=0),
        classify_ownership(changed_paths=("sink.py",), producer_paths=("producer.py",), recipient_paths=("processor.py",), producer_defect_registered=True, producer_score_status="FAIL", producer_label=0),
        classify_ownership(changed_paths=(), producer_paths=("producer.py",), recipient_paths=("processor.py",), producer_defect_registered=False, producer_score_status="PASS", producer_label=1),
    ]
    expected = ["ELIGIBLE", "PENDING_ATTRIBUTION", "UNKNOWN", "UNKNOWN", "PENDING_ATTRIBUTION"]
    cases.append(_case("ownership_classification_table", [row["status"] for row in ownership] == expected,
                       {"rows": ownership, "expected_statuses": expected}))
    unknown = unknown_no_update(state_before="state-0", state_after="state-0", reason="producer scorer UNKNOWN")
    cases.append(_case("unknown_no_update", unknown["valid"], unknown))

    summary = {**config, "status": "QUALIFIED_OFFLINE" if all(row["passed"] for row in cases) else "FAILED_OFFLINE",
               "passed": all(row["passed"] for row in cases), "case_count": len(cases), "cases": cases,
               "remaining_blockers": [
                   "real runner must bind actual API responses to the sealed producer/judgment/action stages",
                   "PIPE3 scorer and independent later-use outcome still require a separate live card",
                   "candidate peers remain exchangeable until persistent per-agent history is specified",
                   "no benchmark, baseline, efficacy, or training claim is supported by this receipt",
               ], "ended_at_utc": datetime.now(timezone.utc).isoformat()}
    (out_dir / "ledger.json").write_text(json.dumps(ledger.events, indent=2) + "\n", encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    log("summary", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in ("status", "passed", "case_count", "real_api_calls", "gpu_jobs", "scientific_claim_allowed")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
