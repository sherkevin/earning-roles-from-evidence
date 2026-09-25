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


def test_strict_assignment_requires_producer_and_precedes_task_start():
    ledger = strict_ledger()
    ledger.record_judgment(RecipientJudgment("j1", "d1", "recipient", "accept", DIGEST))
    ledger.record_action(ConsumerAction("a1", "d1", "recipient", True, DIGEST))
    ledger.record_outcome(TerminalOutcome("o1", "d1", True, "tb-v1", 1.0))
    ledger.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "a1", "o1", "v1", 0.0))
    with pytest.raises(ValueError, match="must match"):
        ledger.record_assignment(LaterAssignment("as1", "task-2", 2, "peer-b", "producer", ("e1",)))
    ledger.record_assignment(LaterAssignment("as1", "task-2", 2, "peer-a", "producer", ("e1",)))
    # The assignment is already recorded, so starting that episode is valid.
    ledger.record_task_start("task-2", 2)
    # The strict ledger rejects a retroactive assignment after the episode has
    # started.
    ledger2 = strict_ledger()
    ledger2.record_judgment(RecipientJudgment("j1", "d1", "recipient", "accept", DIGEST))
    ledger2.record_action(ConsumerAction("a1", "d1", "recipient", True, DIGEST))
    ledger2.record_outcome(TerminalOutcome("o1", "d1", True, "tb-v1", 1.0))
    ledger2.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "a1", "o1", "v1", 0.0))
    ledger2.record_task_start("task-2", 2)
    with pytest.raises(ValueError, match="before the assigned task starts"):
        ledger2.record_assignment(LaterAssignment("as1", "task-2", 2, "peer-a", "producer", ("e1",)))


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
