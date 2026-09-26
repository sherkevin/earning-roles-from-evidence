import pytest

from peer_role_protocol_20260925 import (
    ConsumerAction,
    Delivery,
    LaterAssignment,
    PeerRoleLedger,
    PeerSelection,
    RecipientJudgment,
    RoleEvidenceUpdate,
    TerminalOutcome,
)


DIGEST = "a" * 64


def strict_ledger() -> PeerRoleLedger:
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(
        PeerSelection("s1", "task-1", 1, "selector", "producer", ("peer-a", "peer-b"), "peer-a", 0.5)
    )
    ledger.record_task_start("task-1", 1)
    ledger.record_delivery(
        Delivery("d1", "task-1", "peer-a", "recipient", DIGEST, "produce-1", 1, "s1")
    )
    return ledger


def test_strict_selection_binds_delivery_to_chosen_peer():
    with pytest.raises(ValueError, match="selected peer"):
        ledger = PeerRoleLedger(require_selection=True)
        ledger.record_selection(
            PeerSelection("s1", "task-1", 1, "selector", "producer", ("peer-a", "peer-b"), "peer-a", 0.5)
        )
        ledger.record_task_start("task-1", 1)
        ledger.record_delivery(
            Delivery("d1", "task-1", "peer-b", "recipient", DIGEST, "produce-1", 1, "s1")
        )


def test_strict_feedback_is_terminal_only_and_action_matches_judgment():
    ledger = strict_ledger()
    ledger.record_judgment(RecipientJudgment("j1", "d1", "recipient", "accept", DIGEST))
    with pytest.raises(ValueError, match="does not match"):
        ledger.record_action(ConsumerAction("a1", "d1", "recipient", True, DIGEST, action="repair"))
    ledger.record_action(ConsumerAction("a1", "d1", "recipient", True, DIGEST, action="use"))
    with pytest.raises(ValueError, match="requires terminal"):
        ledger.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "a1", None, "v1", 0.0))


def test_strict_assignment_can_change_peer_and_is_consumed_by_selection():
    ledger = strict_ledger()
    ledger.record_judgment(RecipientJudgment("j1", "d1", "recipient", "reject_redo", DIGEST))
    ledger.record_action(
        ConsumerAction("a1", "d1", "recipient", False, DIGEST, action="independent_redo")
    )
    ledger.record_outcome(TerminalOutcome("o1", "d1", False, "tb-v1", 0.0))
    ledger.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "a1", "o1", "v1", 0.0))
    ledger.record_assignment(
        LaterAssignment("as1", "task-2", 2, "peer-b", "producer", ("e1",), 0.25)
    )
    with pytest.raises(ValueError, match="consume"):
        ledger.record_selection(
            PeerSelection("s2-bad", "task-2", 2, "selector", "producer", ("peer-a", "peer-b"), "peer-a", 1.0)
        )
    with pytest.raises(ValueError, match="propensity"):
        ledger.record_selection(
            PeerSelection("s2-prop", "task-2", 2, "selector", "producer", ("peer-a", "peer-b"), "peer-b", 1.0)
        )
    ledger.record_selection(
        PeerSelection("s2", "task-2", 2, "selector", "producer", ("peer-a", "peer-b"), "peer-b", 0.25)
    )
    ledger.record_task_start("task-2", 2)


def test_strict_assignment_precedes_selection_and_task_start():
    ledger2 = strict_ledger()
    ledger2.record_judgment(RecipientJudgment("j1", "d1", "recipient", "accept", DIGEST))
    ledger2.record_action(ConsumerAction("a1", "d1", "recipient", True, DIGEST))
    ledger2.record_outcome(TerminalOutcome("o1", "d1", True, "tb-v1", 1.0))
    ledger2.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "a1", "o1", "v1", 0.0))
    ledger2.record_selection(
        PeerSelection("s2", "task-2", 2, "selector", "producer", ("peer-a", "peer-b"), "peer-a", 1.0)
    )
    ledger2.record_task_start("task-2", 2)
    with pytest.raises(ValueError, match="before the assigned task starts"):
        ledger2.record_assignment(LaterAssignment("as1", "task-2", 2, "peer-a", "producer", ("e1",)))


@pytest.mark.parametrize("assigned_peer", ["peer-a", "peer-b"])
def test_assignment_cannot_be_attached_after_selection_before_task_start(assigned_peer):
    ledger = strict_ledger()
    ledger.record_judgment(RecipientJudgment("j1", "d1", "recipient", "accept", DIGEST))
    ledger.record_action(ConsumerAction("a1", "d1", "recipient", True, DIGEST))
    ledger.record_outcome(TerminalOutcome("o1", "d1", True, "tb-v1", 1.0))
    ledger.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "a1", "o1", "v1", 0.0))
    ledger.record_selection(
        PeerSelection("s2", "task-2", 2, "selector", "producer", ("peer-a", "peer-b"), "peer-a", 0.5)
    )
    before = ledger.snapshot()
    with pytest.raises(ValueError, match="before the assigned peer is selected"):
        ledger.record_assignment(
            LaterAssignment("as1", "task-2", 2, assigned_peer, "producer", ("e1",), 0.5)
        )
    assert ledger.snapshot() == before
    assert "as1" not in ledger.assignments


@pytest.mark.parametrize("update_version, arrived_at", [("v1", 0.0), ("v2", 1.0)])
def test_feedback_cannot_update_role_evidence_twice_under_different_ids(update_version, arrived_at):
    ledger = strict_ledger()
    ledger.record_judgment(RecipientJudgment("j1", "d1", "recipient", "accept", DIGEST))
    ledger.record_action(ConsumerAction("a1", "d1", "recipient", True, DIGEST))
    ledger.record_outcome(TerminalOutcome("o1", "d1", True, "tb-v1", 1.0))
    ledger.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "a1", "o1", "v1", 0.0))
    before = ledger.snapshot()
    with pytest.raises(ValueError, match="one role evidence update"):
        ledger.record_evidence_update(
            RoleEvidenceUpdate("e2", "j1", "a1", "o1", update_version, arrived_at)
        )
    assert ledger.snapshot() == before
    assert "e2" not in ledger.evidence


def test_strict_task_start_requires_prior_selection():
    ledger = PeerRoleLedger(require_selection=True)
    with pytest.raises(ValueError, match="selection before task start"):
        ledger.record_task_start("task-1", 1)


def test_strict_duplicate_judgment_action_outcome_is_rejected():
    ledger = strict_ledger()
    ledger.record_judgment(RecipientJudgment("j1", "d1", "recipient", "accept", DIGEST))
    with pytest.raises(ValueError, match="one recipient judgment"):
        ledger.record_judgment(RecipientJudgment("j2", "d1", "recipient", "accept", DIGEST))
    ledger.record_action(ConsumerAction("a1", "d1", "recipient", True, DIGEST))
    with pytest.raises(ValueError, match="one consumer action"):
        ledger.record_action(ConsumerAction("a2", "d1", "recipient", True, DIGEST))
    ledger.record_outcome(TerminalOutcome("o1", "d1", True, "tb-v1"))
    with pytest.raises(ValueError, match="one terminal outcome"):
        ledger.record_outcome(TerminalOutcome("o2", "d1", True, "tb-v1"))
