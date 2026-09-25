import pytest

from peer_role_protocol_20260925 import (
    ConsumerAction,
    Delivery,
    LaterAssignment,
    PeerRoleLedger,
    RecipientJudgment,
    RoleEvidenceUpdate,
    TerminalOutcome,
)


DIGEST = "a" * 64
OUT_DIGEST = "b" * 64


def delivery() -> Delivery:
    return Delivery(
        delivery_id="d1",
        task_id="root-1",
        producer_id="agent-a",
        recipient_id="agent-b",
        artifact_sha256=DIGEST,
        source_event_id="produce-1",
        task_index=1,
    )


def judgment() -> RecipientJudgment:
    return RecipientJudgment(
        judgment_id="j1",
        delivery_id="d1",
        consumer_id="agent-b",
        decision="accept",
        observed_artifact_sha256=DIGEST,
    )


def action() -> ConsumerAction:
    return ConsumerAction(
        action_id="a1",
        delivery_id="d1",
        consumer_id="agent-b",
        used_artifact=True,
        input_artifact_sha256=DIGEST,
        output_artifact_sha256=OUT_DIGEST,
    )


def test_vertical_slice_requires_the_declared_order():
    ledger = PeerRoleLedger()
    ledger.record_delivery(delivery())
    with pytest.raises(ValueError, match="prior recipient judgment"):
        ledger.record_action(action())
    ledger.record_judgment(judgment())
    ledger.record_action(action())
    ledger.record_outcome(TerminalOutcome("o1", "d1", True, "native-v1"))
    ledger.record_evidence_update(RoleEvidenceUpdate("ev1", "j1", "a1", "o1", "u1", 3.0))
    ledger.record_assignment(
        LaterAssignment("as1", "root-2", 2, "agent-a", "citation-review", ("ev1",))
    )
    assert ledger.snapshot() == {
        "event_count": 6,
        "last_hash": ledger.events[-1]["record_hash"],
        "delivery_count": 1,
        "judgment_count": 1,
        "action_count": 1,
        "outcome_count": 1,
        "evidence_count": 1,
        "assignment_count": 1,
    }


def test_judgment_cannot_be_terminal_leaked_or_self_authored():
    with pytest.raises(ValueError, match="sealed before terminal"):
        RecipientJudgment(
            "j1", "d1", "agent-b", "accept", DIGEST, terminal_outcome_available=True
        )
    with pytest.raises(ValueError, match="different agents"):
        Delivery("d-self", "root-1", "agent-a", "agent-a", DIGEST, "produce-self", 1)


def test_action_and_assignment_require_attributable_evidence():
    ledger = PeerRoleLedger()
    ledger.record_delivery(delivery())
    with pytest.raises(ValueError, match="delivered artifact digest"):
        ledger.record_judgment(
            RecipientJudgment("j1", "d1", "agent-b", "accept", OUT_DIGEST)
        )
    ledger.record_judgment(judgment())
    with pytest.raises(ValueError, match="delivered artifact digest"):
        ledger.record_action(
            ConsumerAction("a1", "d1", "agent-b", True, OUT_DIGEST)
        )
    with pytest.raises(ValueError, match="unknown role evidence"):
        ledger.record_assignment(
            LaterAssignment("as1", "root-2", 2, "agent-a", "review", ("missing",))
        )


def test_action_mode_cannot_claim_use_without_artifact_use():
    with pytest.raises(ValueError, match="used_artifact=true"):
        ConsumerAction("a1", "d1", "agent-b", False, DIGEST, action="use")


def test_assignment_cannot_precede_the_delivery_it_cites():
    ledger = PeerRoleLedger()
    ledger.record_delivery(delivery())
    ledger.record_judgment(judgment())
    ledger.record_action(action())
    ledger.record_evidence_update(RoleEvidenceUpdate("ev1", "j1", "a1", None, "u1", 2.0))
    with pytest.raises(ValueError, match="after the cited delivery"):
        ledger.record_assignment(
            LaterAssignment("as1", "root-0", 1, "agent-a", "review", ("ev1",))
        )
