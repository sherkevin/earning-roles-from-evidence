"""Offline qualification for the two-stage evidence/update contract.

This is a protocol/ledger gate, not a benchmark result: it uses no LLM API,
GPU, hidden scorer or model-generated data.  The receipt proves that a
producer-owned source episode can publish evidence without changing a
persistent state, that a later assignment can consume the evidence, and that
only the later outcome can open one idempotent delayed credit.  A
recipient-owned control must stop before publication.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, PeerRoleLedger, PeerSelection,
    ProducerScore, RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_ledger_replay import replay_ledger_events  # noqa: E402
from peerrolebench_isolated_policy_read import read_role_evidence_offer_isolated  # noqa: E402
from peerrolebench_role_evidence_offer import build_role_evidence_from_ledger, make_role_evidence_offer  # noqa: E402
from peerrolebench_two_stage_gate import (  # noqa: E402
    DelayedCreditLedger, derive_later_credit_from_ledger, evaluate_source_gate,
)


RUNNER_VERSION = "two-stage-role-evidence-qualification-v1"
DIGEST = "a" * 64
OUTPUT = "b" * 64


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _materials() -> dict[str, Any]:
    return {"agent_payloads": {
        "producer": {"writable_paths": ["producer.py"]},
        "recipient": {"writable_paths": ["processor.py"]},
    }}


def _score() -> dict[str, Any]:
    return {"status": "PASS", "coverage_complete": True, "decision_complete": True}


def _outcome(outcome_id: str, success: bool = True) -> dict[str, Any]:
    return {
        "status": "PASS" if success else "FAIL", "coverage_complete": True,
        "decision_complete": True, "outcome_id": outcome_id,
        "quality_score": 1.0 if success else 0.0,
    }


def _append_episode(ledger: PeerRoleLedger, *, index: int, selection_id: str,
                    chosen: str, delivery_id: str, producer_paths: list[str],
                    outcome_id: str, prefix: str) -> tuple[dict[str, Any], str]:
    ledger.record_selection(PeerSelection(selection_id, "task", index, "peer-a", "producer",
                                          ("peer-b", "peer-c"), chosen, 0.5))
    ledger.record_task_start("task", index)
    ledger.record_delivery(Delivery(delivery_id, "task", chosen, "peer-a", DIGEST,
                                    f"source-{prefix}", index, selection_id))
    ledger.record_producer_score(ProducerScore(
        f"q-{prefix}", delivery_id, DIGEST, "qualification-score-v1", "PASS", 1,
        1.0, _digest({"q": prefix}), True, True))
    judgment = RecipientJudgment(f"j-{prefix}", delivery_id, "peer-a", "accept_with_rework", DIGEST)
    ledger.record_judgment(judgment)
    action = ConsumerAction(f"a-{prefix}", delivery_id, "peer-a", True, DIGEST, OUTPUT,
                            action="repair")
    ledger.record_action(action)
    outcome = TerminalOutcome(outcome_id, delivery_id, outcome_id != "o-fail",
                              "qualification-outcome-v1", 1.0 if outcome_id != "o-fail" else 0.0,
                              _digest({"outcome": outcome_id}))
    ledger.record_outcome(outcome)
    return {
        "producer_score": _score(),
        "judgment": {"target_role": "producer", "observed_artifact_sha256": DIGEST},
        "action": {"changed_paths": producer_paths},
        "outcome": _outcome(outcome_id, outcome.success),
        "judgment_id": judgment.judgment_id,
        "action_id": action.action_id,
        "outcome_id": outcome.outcome_id,
        "candidate_id": chosen,
    }, delivery_id


def _run_control(control: str) -> dict[str, Any]:
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    persistent = {"updates": 0}
    public_evidence: list[str] = []
    before_publish = _digest(persistent)
    source, delivery_id = _append_episode(
        ledger, index=0, selection_id=f"s-{control}-0", chosen="peer-b",
        delivery_id=f"d-{control}-0",
        producer_paths=["producer.py"] if control == "producer_owned" else ["processor.py"],
        outcome_id="o-source", prefix=f"{control}-source",
    )
    materials = _materials()
    source_gate = evaluate_source_gate(materials, source["producer_score"], source["judgment"],
                                       source["action"], source["outcome"], {"valid": False})
    evidence_id = f"e-{control}-source"
    if not source_gate.evidence_publish_allowed:
        replay = replay_ledger_events(ledger.events, allow_incomplete=True)
        return {
            "control": control, "status": "BLOCKED_BY_ATTRIBUTION_GATE", "passed": True,
            "source_gate": source_gate.payload(), "evidence_published": False,
            "assignment_recorded": False, "later_outcome_recorded": False,
            "policy_updates": 0, "persistent_digest_before": before_publish,
            "persistent_digest_after_publication": _digest(persistent),
            "ledger_event_count": len(ledger.events),
            "replay": {"status": replay.status, "complete": replay.complete},
        }

    # Evidence is a public immutable record, not a policy update.
    ledger.record_evidence_update(RoleEvidenceUpdate(
        evidence_id, source["judgment_id"], source["action_id"], source["outcome_id"],
        "two-stage-public-v1", float(len(ledger.events)),
    ))
    role_offer = make_role_evidence_offer(
        offer_id=f"offer-{control}-role-evidence", task_id="task", task_index=1,
        role="producer", context_key="PIPE3:1",
        candidate_keys=("peer-b@v1", "peer-c@v1"),
        evidence=(build_role_evidence_from_ledger(
            ledger=ledger, evidence_id=evidence_id, candidate_key=f"{source['candidate_id']}@v1",
            role="producer", target_task_index=1, evidence_version="role-evidence-v1", available_index=1,
        ),),
        evidence_version="role-evidence-v1", available_index=1,
    )
    role_read = read_role_evidence_offer_isolated(role_offer, read_cut=1, previous_aux_hash="GENESIS")
    public_evidence.append(evidence_id)
    after_publication = _digest(persistent)
    assert before_publish == after_publication  # publication is not persistent training
    assert persistent["updates"] == 0

    assignment_agent = source["candidate_id"]
    assignment = LaterAssignment(f"as-{control}-1", "task", 1, assignment_agent, "producer",
                                 (evidence_id,), 0.5)
    ledger.record_assignment(assignment)
    ledger.record_selection(PeerSelection(f"s-{control}-1", "task", 1, "peer-a", "producer",
                                          ("peer-b", "peer-c"), assignment_agent, 0.5))
    ledger.record_task_start("task", 1)
    later_delivery = Delivery(f"d-{control}-1", "task", assignment_agent, "peer-a", DIGEST,
                              f"source-{control}-later", 1, f"s-{control}-1")
    ledger.record_delivery(later_delivery)
    ledger.record_producer_score(ProducerScore(
        f"q-{control}-later", later_delivery.delivery_id, DIGEST, "qualification-score-v1",
        "PASS", 1, 1.0, _digest({"q": "later"}), True, True))
    ledger.record_judgment(RecipientJudgment(
        f"j-{control}-later", later_delivery.delivery_id, "peer-a", "accept_with_rework", DIGEST))
    ledger.record_action(ConsumerAction(
        f"a-{control}-later", later_delivery.delivery_id, "peer-a", True, DIGEST, OUTPUT,
        action="repair"))
    ledger.record_outcome(TerminalOutcome(
        f"o-{control}-later", later_delivery.delivery_id, True, "qualification-outcome-v1",
        1.0, _digest({"outcome": "later"})))
    # The strict replay contract requires every completed delivery to end in a
    # terminal evidence record.  This later evidence is recorded after the
    # delayed credit validation and is not fed back into the already sealed
    # task-1 selection.
    ledger.record_evidence_update(RoleEvidenceUpdate(
        f"e-{control}-later", f"j-{control}-later", f"a-{control}-later",
        f"o-{control}-later", "two-stage-public-v1", float(len(ledger.events)),
    ))
    credit = derive_later_credit_from_ledger(
        ledger=ledger, source_gate=source_gate, assignment_id=assignment.assignment_id,
        source_evidence_id=evidence_id, evidence_candidate_id=f"{source['candidate_id']}@v1",
        later_outcome_id=f"o-{control}-later",
    )
    assert credit is not None
    credits = DelayedCreditLedger()
    applied: list[str] = []
    applied_once = credits.apply_once(credit, lambda value: (applied.append(value.credit_digest), persistent.__setitem__("updates", 1)))
    applied_duplicate = credits.apply_once(credit, lambda value: persistent.__setitem__("updates", 2))
    assert applied_once is True and applied_duplicate is False and persistent["updates"] == 1
    replay = replay_ledger_events(ledger.events)
    return {
        "control": control, "status": "QUALIFIED_OFFLINE", "passed": replay.status == "PASS",
        "source_gate": source_gate.payload(), "evidence_published": True,
        "assignment_recorded": True, "later_outcome_recorded": True,
        "policy_updates": persistent["updates"], "duplicate_update_applied": applied_duplicate,
        "persistent_digest_before": before_publish,
        "persistent_digest_after_publication": after_publication,
        "persistent_digest_after_credit": _digest(persistent),
        "ledger_event_count": len(ledger.events), "replay": {"status": replay.status, "complete": replay.complete},
        "credit_digest": credit.credit_digest,
        "role_offer": role_offer.payload(), "role_read": role_read.__dict__,
    }


def run(out_dir: Path) -> dict[str, Any]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    config = {
        "runner_version": RUNNER_VERSION, "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False, "benchmark_status": "qualification_only",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    raw = out_dir / "raw.jsonl"
    rows = []
    for control in ("producer_owned", "recipient_owned"):
        result = _run_control(control)
        rows.append(result)
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True) + "\n")
    summary = {
        **config, "status": "QUALIFIED_OFFLINE",
        "passed": all(row["passed"] for row in rows), "cases": rows,
        "interpretation": "two-stage protocol qualification only; no efficacy, API, GPU, or benchmark claim",
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps({"status": result["status"], "passed": result["passed"]}, indent=2))
