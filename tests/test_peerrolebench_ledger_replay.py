from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_ledger_replay import (  # noqa: E402
    LedgerReplayError,
    replay_ledger_events,
)
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction,
    Delivery,
    LaterAssignment,
    PeerRoleLedger,
    PeerSelection,
    ProducerScore,
    RecipientJudgment,
    RoleEvidenceUpdate,
    TerminalOutcome,
)

DIGEST = "a" * 64
OUT = "b" * 64


def _append_episode(ledger: PeerRoleLedger, task: str, index: int, selection: str, chosen: str, delivery: str, suffix: str) -> RoleEvidenceUpdate:
    ledger.record_selection(PeerSelection(selection, task, index, "selector", "producer", ("peer-a", "peer-b"), chosen, 0.5))
    ledger.record_task_start(task, index)
    ledger.record_delivery(Delivery(delivery, task, chosen, "recipient", DIGEST, f"produce-{suffix}", index, selection))
    judgment = RecipientJudgment(f"j-{suffix}", delivery, "recipient", "accept", DIGEST)
    ledger.record_judgment(judgment)
    action = ConsumerAction(f"a-{suffix}", delivery, "recipient", True, DIGEST, OUT, action="use")
    ledger.record_action(action)
    outcome = TerminalOutcome(f"o-{suffix}", delivery, True, "score-v1", 1.0)
    ledger.record_outcome(outcome)
    evidence = RoleEvidenceUpdate(f"e-{suffix}", judgment.judgment_id, action.action_id, outcome.outcome_id, "update-v1", float(len(ledger.events)))
    ledger.record_evidence_update(evidence)
    return evidence


def valid_events() -> list[dict]:
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    evidence = _append_episode(ledger, "task", 0, "s0", "peer-a", "d0", "0")
    ledger.record_assignment(LaterAssignment("as1", "task", 1, "peer-b", "producer", (evidence.evidence_id,), 0.5))
    _append_episode(ledger, "task", 1, "s1", "peer-b", "d1", "1")
    # JSON round-trip is what the runner persists and catches tuple/list drift.
    return json.loads(json.dumps(ledger.events))


def rehash(records: list[dict]) -> list[dict]:
    previous = "GENESIS"
    for record in records:
        record["previous_hash"] = previous
        import peerrolebench_ledger_replay as module
        record["record_hash"] = module._hash_payload({
            "event_type": record["event_type"],
            "payload": record["payload"],
            "previous_hash": previous,
        })
        previous = record["record_hash"]
    return records


def test_valid_complete_chain_replays_with_hash_and_lineage():
    result = replay_ledger_events(valid_events())
    assert result.status == "PASS"
    assert result.complete is True
    assert result.snapshot == {
        "event_count": 15,
        "last_hash": result.snapshot["last_hash"],
        "delivery_count": 2,
        "producer_score_count": 0,
        "judgment_count": 2,
        "action_count": 2,
        "outcome_count": 2,
        "evidence_count": 2,
        "assignment_count": 1,
    }


def test_missing_terminal_stage_is_unknown_only_when_explicitly_allowed():
    records = valid_events()
    records = records[:-1]  # remove the second evidence update
    with pytest.raises(LedgerReplayError, match="incomplete_ledger"):
        replay_ledger_events(records)
    result = replay_ledger_events(records, allow_incomplete=True)
    assert result.status == "UNKNOWN"
    assert {entry["stage"] for entry in result.missing} == {"role_evidence_update"}


def test_empty_crash_ledger_is_unknown_only_with_explicit_diagnostic_mode():
    with pytest.raises(LedgerReplayError, match="empty_ledger"):
        replay_ledger_events([])
    result = replay_ledger_events([], allow_incomplete=True)
    assert result.status == "UNKNOWN"
    assert result.complete is False
    assert result.missing == ({"stage": "peer_selection"},)


@pytest.mark.parametrize("mutation, code", [
    ("duplicate", "duplicate_event_id"),
    ("hash", "record_hash_mismatch"),
    ("chain", "hash_chain_break"),
    ("unknown", "unknown_event_type"),
    ("retry", "unsupported_retry"),
    ("out_of_order", "out_of_order"),
])
def test_mutation_matrix_rejects_untrusted_ledger(mutation, code):
    records = valid_events()
    if mutation == "duplicate":
        records.insert(3, copy.deepcopy(records[2]))
        rehash(records)
    elif mutation == "hash":
        records[2]["record_hash"] = "f" * 64
    elif mutation == "chain":
        records[2]["previous_hash"] = "f" * 64
    elif mutation == "unknown":
        records[2]["event_type"] = "mystery_event"
        rehash(records)
    elif mutation == "retry":
        records[2]["event_type"] = "producer_retry"
        rehash(records)
    elif mutation == "out_of_order":
        # Move the first delivery before its task_start while preserving the
        # serialized chain.  The outer validator must catch this causal gap.
        delivery_i = next(i for i, e in enumerate(records) if e["event_type"] == "producer_delivery")
        start_i = next(i for i, e in enumerate(records) if e["event_type"] == "task_start")
        records[start_i], records[delivery_i] = records[delivery_i], records[start_i]
        rehash(records)
    with pytest.raises(LedgerReplayError) as caught:
        replay_ledger_events(records)
    assert caught.value.code == code


def test_unknown_payload_and_duplicate_task_start_are_rejected():
    records = valid_events()
    records[0]["payload"]["candidate_ids"] = ["peer-a", "peer-a"]
    rehash(records)
    with pytest.raises(LedgerReplayError, match="malformed_payload|protocol_violation"):
        replay_ledger_events(records)

    records = valid_events()
    start_i = next(i for i, e in enumerate(records) if e["event_type"] == "task_start")
    records.insert(start_i + 1, copy.deepcopy(records[start_i]))
    rehash(records)
    with pytest.raises(LedgerReplayError) as caught:
        replay_ledger_events(records)
    assert caught.value.code == "duplicate_task_start"


@pytest.mark.parametrize("mutation", ["delivery_selection", "judgment_consumer", "evidence_outcome", "assignment_evidence"])
def test_referential_links_cannot_be_rewritten_without_rejection(mutation):
    records = valid_events()
    if mutation == "delivery_selection":
        row = next(e for e in records if e["event_type"] == "producer_delivery")
        row["payload"]["selection_id"] = "missing-selection"
    elif mutation == "judgment_consumer":
        row = next(e for e in records if e["event_type"] == "recipient_judgment")
        row["payload"]["consumer_id"] = "other-recipient"
    elif mutation == "evidence_outcome":
        row = next(e for e in records if e["event_type"] == "role_evidence_update")
        row["payload"]["outcome_id"] = "o-1"
    else:
        row = next(e for e in records if e["event_type"] == "later_assignment")
        row["payload"]["evidence_ids"] = ["missing-evidence"]
    rehash(records)
    with pytest.raises(LedgerReplayError) as caught:
        replay_ledger_events(records)
    assert caught.value.code in {"protocol_violation", "out_of_order"}


def test_producer_score_is_replayed_before_judgment_and_kept_separate():
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection("s0", "task", 0, "selector", "producer",
                                         ("peer-a", "peer-b"), "peer-a", 0.5))
    ledger.record_task_start("task", 0)
    ledger.record_delivery(Delivery("d0", "task", "peer-a", "recipient", DIGEST,
                                   "produce-0", 0, "s0"))
    ledger.record_producer_score(ProducerScore("ps0", "d0", DIGEST, "producer-v1",
                                              "FAIL", 0, 3 / 7, OUT, True))
    judgment = RecipientJudgment("j0", "d0", "recipient", "accept", DIGEST)
    ledger.record_judgment(judgment)
    action = ConsumerAction("a0", "d0", "recipient", True, DIGEST, OUT, action="use")
    ledger.record_action(action)
    ledger.record_outcome(TerminalOutcome("o0", "d0", True, "consumer-v1", 1.0, OUT))
    ledger.record_evidence_update(RoleEvidenceUpdate("e0", "j0", "a0", "o0", "u1", 1.0))
    result = replay_ledger_events(json.loads(json.dumps(ledger.events)))
    assert result.status == "PASS"
    assert result.snapshot["producer_score_count"] == 1


def test_producer_score_after_judgment_is_rejected():
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection("s0", "task", 0, "selector", "producer",
                                         ("peer-a", "peer-b"), "peer-a", 0.5))
    ledger.record_task_start("task", 0)
    ledger.record_delivery(Delivery("d0", "task", "peer-a", "recipient", DIGEST,
                                   "produce-0", 0, "s0"))
    ledger.record_judgment(RecipientJudgment("j0", "d0", "recipient", "accept", DIGEST))
    with pytest.raises(ValueError, match="precede recipient judgment"):
        ledger.record_producer_score(ProducerScore("ps0", "d0", DIGEST, "producer-v1",
                                                   "UNKNOWN"))


@pytest.mark.parametrize("status,label,quality,coverage", [
    ("PASS", 1, 1.0, True),
    ("FAIL", 0, 0.5, True),
    ("UNKNOWN", None, None, False),
])
def test_producer_score_status_contract(status, label, quality, coverage):
    value = ProducerScore("ps", "d", DIGEST, "producer-v1", status, label, quality,
                          OUT if status != "UNKNOWN" else None, coverage)
    assert value.status == status
    if status == "UNKNOWN":
        with pytest.raises(ValueError):
            ProducerScore("bad", "d", DIGEST, "producer-v1", "UNKNOWN", 0, None, None, False)


def test_producer_score_digest_must_match_delivery():
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection("s0", "task", 0, "selector", "producer",
                                         ("peer-a", "peer-b"), "peer-a", 0.5))
    ledger.record_task_start("task", 0)
    ledger.record_delivery(Delivery("d0", "task", "peer-a", "recipient", DIGEST,
                                   "produce-0", 0, "s0"))
    with pytest.raises(ValueError, match="delivered artifact digest"):
        ledger.record_producer_score(ProducerScore("ps0", "d0", OUT, "producer-v1",
                                                   "UNKNOWN"))
