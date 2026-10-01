from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_two_stage_gate import (  # noqa: E402
    DelayedCreditLedger,
    derive_later_credit_from_ledger,
    evaluate_source_gate,
    validate_later_credit,
)
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, PeerRoleLedger, PeerSelection,
    RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)


def materials():
    return {"agent_payloads": {
        "producer": {"writable_paths": ["producer.py"]},
        "recipient": {"writable_paths": ["processor.py"]},
    }}


def score(status="PASS"):
    return {"status": status, "coverage_complete": True, "decision_complete": True}


def outcome(status="PASS", outcome_id="o0"):
    return {"status": status, "coverage_complete": True, "decision_complete": True,
            "outcome_id": outcome_id, "quality_score": 1.0 if status == "PASS" else 0.0}


def judgment(target="producer"):
    return {"target_role": target, "observed_artifact_sha256": "a" * 64}


def test_publication_is_allowed_without_persistent_update():
    gate = evaluate_source_gate(materials(), score(), judgment(),
                                {"changed_paths": ["producer.py"]}, outcome(),
                                {"valid": False})
    assert gate.attribution_eligible is True
    assert gate.evidence_publish_allowed is True
    assert gate.policy_update_allowed is False
    assert gate.later_use_valid is False


def test_later_outcome_cannot_create_source_attribution_or_evidence():
    gate = evaluate_source_gate(materials(), score(), judgment(),
                                {"changed_paths": []}, outcome(),
                                {"valid": True})
    assert gate.attribution_eligible is False
    assert gate.evidence_publish_allowed is False
    assert gate.policy_update_allowed is False


def test_recipient_only_and_mixed_changes_are_not_producer_evidence():
    recipient = evaluate_source_gate(materials(), score(), judgment(),
                                     {"changed_paths": ["processor.py"]}, outcome())
    mixed = evaluate_source_gate(materials(), score(), judgment(),
                                 {"changed_paths": ["producer.py", "processor.py"]}, outcome())
    assert recipient.status == "PENDING_ATTRIBUTION"
    assert mixed.status == "UNKNOWN"
    assert not recipient.evidence_publish_allowed
    assert not mixed.evidence_publish_allowed


def test_later_credit_requires_assignment_selection_and_complete_outcome():
    gate = evaluate_source_gate(materials(), score(), judgment(),
                                {"changed_paths": ["producer.py"]}, outcome())
    later = outcome("PASS", "o1")
    assert validate_later_credit(source_gate=gate, assignment_id="as1",
                                 source_evidence_id="e0", later_outcome=later,
                                 assignment_consumed=False,
                                 selection_matches_assignment=True,
                                 assignment_agent_id="peer-b", evidence_candidate_id="peer-b") is None
    credit = validate_later_credit(source_gate=gate, assignment_id="as1",
                                   source_evidence_id="e0", later_outcome=later,
                                   assignment_consumed=True,
                                   selection_matches_assignment=True,
                                   assignment_agent_id="peer-b", evidence_candidate_id="peer-b")
    assert credit is not None
    assert validate_later_credit(source_gate=gate, assignment_id="as1",
                                 source_evidence_id="e0", later_outcome=later,
                                 assignment_consumed=True,
                                 selection_matches_assignment=True,
                                 assignment_agent_id="peer-c", evidence_candidate_id="peer-b") is None
    ledger = DelayedCreditLedger()
    applied = []
    assert ledger.apply_once(credit, applied.append) is True
    assert ledger.apply_once(credit, applied.append) is False
    assert len(applied) == 1


def test_delayed_credit_update_rolls_back_before_retry():
    gate = evaluate_source_gate(materials(), score(), judgment(),
                                {"changed_paths": ["producer.py"]}, outcome())
    credit = validate_later_credit(
        source_gate=gate, assignment_id="as-rollback", source_evidence_id="e-rollback",
        later_outcome=outcome("PASS", "o-rollback"), assignment_consumed=True,
        selection_matches_assignment=True, assignment_agent_id="peer-b",
        evidence_candidate_id="peer-b",
    )
    assert credit is not None
    state = {"weight": 0.5, "updates": 0}
    calls = {"count": 0}

    def snapshot():
        return dict(state)

    def restore(before):
        state.clear()
        state.update(before)

    def flaky_update(_credit):
        calls["count"] += 1
        state["weight"] = 0.9
        state["updates"] = 1
        raise RuntimeError("simulated updater failure")

    ledger = DelayedCreditLedger()
    try:
        ledger.apply_once(credit, flaky_update, snapshot=snapshot, restore=restore)
    except RuntimeError:
        pass
    else:
        raise AssertionError("the failed updater must propagate")
    assert state == {"weight": 0.5, "updates": 0}
    assert ledger.credits == {}

    def successful_update(_credit):
        calls["count"] += 1
        state["weight"] = 0.6
        state["updates"] = 1

    assert ledger.apply_once(credit, successful_update, snapshot=snapshot, restore=restore)
    assert state == {"weight": 0.6, "updates": 1}
    assert calls["count"] == 2


def test_native_ledger_task_start_is_selection_bound_not_assignment_bound():
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection("s0", "task", 0, "peer-a", "producer",
                                         ("peer-b", "peer-c"), "peer-b", 0.5))
    # This is legal under the native protocol; it is a separate fact from the
    # method's requirement that a later assignment cite published evidence.
    ledger.record_task_start("task", 0)
    assert ledger.snapshot()["event_count"] == 2
    try:
        ledger.record_assignment(LaterAssignment("as1", "task", 1, "peer-c", "producer", (), 0.5))
    except ValueError as exc:
        assert "role evidence" in str(exc)
    else:
        raise AssertionError("an assignment without evidence must be rejected")


def test_delayed_credit_is_derived_from_canonical_target_lineage():
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection("s0", "task", 0, "peer-a", "producer", ("peer-b", "peer-c"), "peer-b", 0.5))
    ledger.record_task_start("task", 0)
    ledger.record_delivery(Delivery("d0", "task", "peer-b", "peer-a", "a" * 64, "source0", 0, "s0"))
    ledger.record_judgment(RecipientJudgment("j0", "d0", "peer-a", "accept_with_rework", "a" * 64))
    ledger.record_action(ConsumerAction("a0", "d0", "peer-a", True, "a" * 64, "b" * 64, action="repair"))
    ledger.record_outcome(TerminalOutcome("o0", "d0", True, "score-v1", 1.0, "c" * 64))
    ledger.record_evidence_update(RoleEvidenceUpdate("e0", "j0", "a0", "o0", "ev-v1", 1.0))
    ledger.record_assignment(LaterAssignment("as1", "task", 1, "peer-b", "producer", ("e0",), 0.5))
    ledger.record_selection(PeerSelection("s1", "task", 1, "peer-a", "producer", ("peer-b", "peer-c"), "peer-b", 0.5))
    ledger.record_task_start("task", 1)
    ledger.record_delivery(Delivery("d1", "task", "peer-b", "peer-a", "d" * 64, "source1", 1, "s1"))
    ledger.record_judgment(RecipientJudgment("j1", "d1", "peer-a", "accept", "d" * 64))
    ledger.record_action(ConsumerAction("a1", "d1", "peer-a", True, "d" * 64, "e" * 64, action="use"))
    ledger.record_outcome(TerminalOutcome("o1", "d1", True, "score-v1", 1.0, "f" * 64))
    source_gate = evaluate_source_gate(
        materials(), score(), judgment(), {"changed_paths": ["producer.py"]}, outcome(),
    )
    assert derive_later_credit_from_ledger(
        ledger=ledger, source_gate=source_gate, assignment_id="as1", source_evidence_id="e0",
        evidence_candidate_id="peer-b@v1", later_outcome_id="o1",
    ) is not None
    assert derive_later_credit_from_ledger(
        ledger=ledger, source_gate=source_gate, assignment_id="as1", source_evidence_id="e0",
        evidence_candidate_id="peer-c@v1", later_outcome_id="o1",
    ) is None
    assert derive_later_credit_from_ledger(
        ledger=ledger, source_gate=source_gate, assignment_id="as1", source_evidence_id="e0",
        evidence_candidate_id="peer-b@v1", later_outcome_id="o0",
    ) is None
